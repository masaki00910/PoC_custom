import type {
  LLMContentBlock,
  LLMMessage,
  RecoveryListEntry,
  ToolCall,
} from '../types/secondary-check';
import type { LLMClient, LLMRequest, LLMResponse } from './llm-client';

/**
 * エラーあり項目のみを抽出した回復対象。従来通り「最終判定の前に判断が必要なもの」。
 */
export interface RecoveryTarget {
  fieldName: string;
  attribute: string;
  originalValue: string;
  firstRecoveryValue: string;
  firstRecoveryReason: string;
}

/**
 * 申込の全フィールド（エラーなしも含む）。二次チェック担当者は非エラー項目に対しても
 * 承認・上書きの操作を記録することがあるため、受付対象は全フィールド。
 */
export interface FieldInfo {
  fieldName: string;
  attribute: string;
  originalValue: string;
  firstRecoveryValue: string;
  firstRecoveryReason: string;
  isError: boolean;
}

export const collectAllFields = (list: RecoveryListEntry[]): FieldInfo[] => {
  const byTitle = new Map<string, RecoveryListEntry>();
  for (const e of list) byTitle.set(e.title, e);
  return list
    .filter((e) => e.section === 'original')
    .map((o) => ({
      fieldName: o.title,
      attribute: o.attribute,
      originalValue: o.value,
      firstRecoveryValue: byTitle.get(`${o.title}_回復結果`)?.value ?? '',
      firstRecoveryReason: byTitle.get(`${o.title}_回復理由`)?.value ?? '',
      isError: o.errorFlag,
    }));
};

export const collectRecoveryTargets = (list: RecoveryListEntry[]): RecoveryTarget[] =>
  collectAllFields(list)
    .filter((f) => f.isError)
    .map(({ fieldName, attribute, originalValue, firstRecoveryValue, firstRecoveryReason }) => ({
      fieldName,
      attribute,
      originalValue,
      firstRecoveryValue,
      firstRecoveryReason,
    }));

export const extractDecidedFields = (messages: LLMMessage[]): Set<string> => {
  const decided = new Set<string>();
  for (const m of messages) {
    for (const block of m.content) {
      if (block.type === 'tool_use' && block.name === 'update_recovery_value') {
        const fieldName = block.input['fieldName'];
        if (typeof fieldName === 'string') decided.add(fieldName);
      }
    }
  }
  return decided;
};

const wasFinalized = (messages: LLMMessage[]): boolean =>
  messages.some((m) =>
    m.content.some((b) => b.type === 'tool_use' && b.name === 'finalize_check'),
  );

const latestUserText = (messages: LLMMessage[]): string | null => {
  for (let i = messages.length - 1; i >= 0; i--) {
    const m = messages[i];
    if (!m || m.role !== 'user') continue;
    for (const block of m.content) {
      if (block.type === 'text') return block.text;
    }
    return null;
  }
  return null;
};

const latestUserMessageIsToolResult = (messages: LLMMessage[]): boolean => {
  const last = messages[messages.length - 1];
  return Boolean(last && last.role === 'user' && last.content.some((b) => b.type === 'tool_result'));
};

// ── Intent classification ──────────────────────────────────────
type SegmentAction =
  | { kind: 'approve'; field: FieldInfo }
  | { kind: 'override'; field: FieldInfo; value: string; reason: string }
  | { kind: 'inquiry'; field: FieldInfo; contents: string };

const APPROVE_PATTERNS = [
  /(?:OK|ok|オッケー|okay|承認|採用|そのまま|問題ない|問題無い|いいです|大丈夫)/i,
];
const INQUIRY_PATTERNS = [/(?:問い合わせ|わからない|わかんない|判断できない|保留)/];
const FINALIZE_APPROVE_PATTERNS = [/(?:最終承認|最終(?:OK|ok)|最終確定|全件承認|全(?:部|て)承認)/i];
const FINALIZE_REJECT_PATTERNS = [/(?:最終差(?:し|)戻|最終(?:NG|ng)|全件差戻|全(?:部|て)差戻)/i];
const BATCH_APPROVE_PATTERNS = [
  /^(?:全(?:部|て)|一括|まとめて)?(?:OK|ok|承認|問題ない)[。．!！]?$/i,
];

/** 郵便番号 "060-0001" / "060 0001" / "0600001" / 住所カナなど。 */
const extractValue = (seg: string, fieldName: string): string | undefined => {
  // まず field 名の後続部分を見る ("契〒は 060-0001" → "060-0001")
  const idx = seg.indexOf(fieldName);
  const after = idx >= 0 ? seg.slice(idx + fieldName.length) : seg;

  const postal = after.match(/(\d{3})[-\s]?(\d{4})/);
  if (postal && postal[1] && postal[2]) return `${postal[1]}-${postal[2]}`;

  const quoted = after.match(/[「『"]([^」』"]+)[」』"]/);
  if (quoted && quoted[1]) return quoted[1];

  // "<field>は<VALUE>で" / "<field>を<VALUE>に" 等の助詞区切り
  const particle = after.match(/[はをにで]\s*([^\s、。,]+?)(?:[で]?[で]?[。.!！?？]?$|$)/);
  if (particle && particle[1] && particle[1].length > 0) {
    const v = particle[1].replace(/[はをにでとの]$/, '');
    if (v && !APPROVE_PATTERNS.some((r) => r.test(v))) return v;
  }

  return undefined;
};

const detectFieldInSegment = (seg: string, fields: FieldInfo[]): FieldInfo | null => {
  // 長いフィールド名優先（"契約者名" が "契" の前に来るように）
  const sorted = [...fields].sort((a, b) => b.fieldName.length - a.fieldName.length);
  for (const f of sorted) {
    if (seg.includes(f.fieldName)) return f;
  }
  return null;
};

const classifySegment = (seg: string, fields: FieldInfo[]): SegmentAction | null => {
  const field = detectFieldInSegment(seg, fields);
  if (!field) return null;

  if (INQUIRY_PATTERNS.some((r) => r.test(seg))) {
    return { kind: 'inquiry', field, contents: seg };
  }

  const value = extractValue(seg, field.fieldName);
  if (value) {
    return {
      kind: 'override',
      field,
      value,
      reason: `担当者判断: ${seg}`,
    };
  }

  if (APPROVE_PATTERNS.some((r) => r.test(seg))) {
    return { kind: 'approve', field };
  }

  return null;
};

const parseUserSegments = (text: string, fields: FieldInfo[]): SegmentAction[] => {
  const segments = text
    .split(/[、，。,\n]+/)
    .map((s) => s.trim())
    .filter(Boolean);

  const actions: SegmentAction[] = [];
  for (const seg of segments) {
    const a = classifySegment(seg, fields);
    if (a) actions.push(a);
  }
  return actions;
};

// ── Tool call builders ─────────────────────────────────────────
const makeId = (): string => `tc-${Math.random().toString(36).slice(2, 10)}`;

const approveToolCall = (field: FieldInfo): ToolCall => {
  const value = field.isError ? field.firstRecoveryValue : field.originalValue;
  const reason = field.isError
    ? '一次チェック結果を承認'
    : '原値のまま承認（エラーなし項目）';
  return {
    name: 'update_recovery_value',
    input: { fieldName: field.fieldName, value, reason },
  };
};

const overrideToolCall = (field: FieldInfo, value: string, reason: string): ToolCall => ({
  name: 'update_recovery_value',
  input: { fieldName: field.fieldName, value, reason },
});

const inquiryToolCall = (field: FieldInfo, contents: string): ToolCall => ({
  name: 'file_inquiry',
  input: {
    category: '二次チェック判断保留',
    contents: `フィールド: ${field.fieldName} / 内容: ${contents}`,
  },
});

// ── Response helpers ───────────────────────────────────────────
const textResponse = (text: string): LLMResponse => ({
  message: { role: 'assistant', content: [{ type: 'text', text }] },
  stopReason: 'end_turn',
});

const toolCallsResponse = (text: string, calls: ToolCall[]): LLMResponse => {
  const content: LLMContentBlock[] = [];
  if (text) content.push({ type: 'text', text });
  for (const call of calls) {
    content.push({
      type: 'tool_use',
      id: makeId(),
      name: call.name,
      input: call.input as Record<string, string | boolean>,
    });
  }
  return {
    message: { role: 'assistant', content },
    stopReason: 'tool_use',
  };
};

// ── MockLLMClient ──────────────────────────────────────────────
/**
 * ルールベースの agentic mock LLM。
 *
 * 基本姿勢は **受動的**: LLM 側から「次はどの項目？」のような個別のアクション要求はしない。
 * 担当者の発話に含まれる指示（フィールド名 + 動作）をできる範囲で読み取り、
 * 対応する tool を呼ぶ。エラー有無に関わらず任意項目が対象。
 *
 * 一括操作:
 * - 「OK」「承認」単独 → エラー項目のみ一次値で一括承認
 * - 「最終承認」      → エラー項目がすべて判断済みなら finalize_check(true)
 * - 「最終差し戻し」  → finalize_check(false)
 */
export class MockLLMClient implements LLMClient {
  constructor(private readonly fields: FieldInfo[]) {}

  async respond(request: LLMRequest): Promise<LLMResponse> {
    await new Promise((resolve) => setTimeout(resolve, 400));

    const { messages } = request;
    const isInitialGreeting = messages.length === 0;
    const finalized = wasFinalized(messages);

    if (finalized) {
      return textResponse('既に最終判定が登録されています。追加の操作はできません。');
    }
    if (isInitialGreeting) {
      return textResponse(this.buildInitialMessage());
    }
    if (latestUserMessageIsToolResult(messages)) {
      return textResponse('記録しました。他にご指示があればお知らせください。');
    }

    const userText = latestUserText(messages);
    if (!userText) {
      return textResponse('すみません、もう一度入力してください。');
    }

    // 最終判定
    if (FINALIZE_APPROVE_PATTERNS.some((r) => r.test(userText))) {
      const decided = extractDecidedFields(messages);
      const errorTargets = this.fields.filter((f) => f.isError);
      const unresolved = errorTargets.filter((t) => !decided.has(t.fieldName));
      if (unresolved.length > 0) {
        return textResponse(
          `未判断のエラー項目が残っています:\n` +
            unresolved.map((t) => `・${t.fieldName}`).join('\n') +
            '\n承認・修正・問い合わせのいずれかで対応してから最終承認してください。',
        );
      }
      return toolCallsResponse('最終承認として登録します。', [
        { name: 'finalize_check', input: { checkResult: true, status: '次工程待ち' } },
      ]);
    }
    if (FINALIZE_REJECT_PATTERNS.some((r) => r.test(userText))) {
      return toolCallsResponse('最終差し戻しとして登録します。', [
        { name: 'finalize_check', input: { checkResult: false, status: '差し戻し' } },
      ]);
    }

    // フィールド単位の指示（複数対応）
    const actions = parseUserSegments(userText, this.fields);
    if (actions.length > 0) {
      const calls: ToolCall[] = [];
      const summaryLines: string[] = [];
      for (const a of actions) {
        if (a.kind === 'approve') {
          calls.push(approveToolCall(a.field));
          summaryLines.push(
            `・${a.field.fieldName}: 承認（${a.field.isError ? a.field.firstRecoveryValue : a.field.originalValue}）`,
          );
        } else if (a.kind === 'override') {
          calls.push(overrideToolCall(a.field, a.value, a.reason));
          summaryLines.push(`・${a.field.fieldName}: 「${a.value}」で更新`);
        } else {
          calls.push(inquiryToolCall(a.field, a.contents));
          summaryLines.push(`・${a.field.fieldName}: 問い合わせ起票`);
        }
      }
      return toolCallsResponse(
        `以下の指示として記録します:\n${summaryLines.join('\n')}`,
        calls,
      );
    }

    // 一括承認（エラー項目に対してのみ）
    if (BATCH_APPROVE_PATTERNS.some((r) => r.test(userText.trim()))) {
      const decided = extractDecidedFields(messages);
      const pending = this.fields.filter((f) => f.isError && !decided.has(f.fieldName));
      if (pending.length === 0) {
        return textResponse(
          'エラー項目は既にすべて判断済みです。最終承認する場合は「最終承認」と入力してください。',
        );
      }
      const calls = pending.map(approveToolCall);
      return toolCallsResponse(
        `未判断のエラー項目 ${pending.length} 件を一次回復値で承認します:\n` +
          pending.map((t) => `・${t.fieldName} → ${t.firstRecoveryValue}`).join('\n'),
        calls,
      );
    }

    // 個別インクワイアリ（フィールド名なし）— 全文を内容として保留起票するか
    if (INQUIRY_PATTERNS.some((r) => r.test(userText))) {
      return textResponse(
        '問い合わせ対象のフィールド名を含めて指示してください。（例: 「契住所 問い合わせ」）',
      );
    }

    return textResponse(
      '指示を読み取れませんでした。フィールド名を添えて指示をお願いします。\n' +
        '例: 「契〒 は OK」「契住所 を ﾎｯｶｲﾄﾞｳ... で」「被住所 問い合わせ」「最終承認」',
    );
  }

  private buildInitialMessage(): string {
    const errors = this.fields.filter((f) => f.isError);
    if (errors.length === 0) {
      return (
        '二次チェックを開始します。上の表が一次チェック結果です。\n' +
        'エラー項目はありません。内容を確認のうえ、必要に応じて個別の承認や修正を指示してください。\n' +
        '問題なければ「最終承認」と入力してください。'
      );
    }
    return (
      '二次チェックを開始します。上の表が一次チェック結果です。\n' +
      `エラーあり: ${errors.length} 項目（${errors.map((e) => e.fieldName).join(' / ')}）。\n` +
      'フィールド名を添えて指示をお願いします。例:\n' +
      '・「契〒 は OK」（一次回復値を承認）\n' +
      '・「契住所 を 060-0002 で」（値を上書き）\n' +
      '・「被住所 問い合わせ」（判断保留）\n' +
      '・「承認」単独（エラー項目を一括承認）\n' +
      '・「最終承認」（全体を確定）'
    );
  }
}
