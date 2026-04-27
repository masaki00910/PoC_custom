import { describe, expect, it } from 'vitest';
import {
  MockLLMClient,
  collectAllFields,
  collectRecoveryTargets,
  extractDecidedFields,
  type FieldInfo,
} from '../../../InsuranceCheckControl/services/mock-llm-client';
import type {
  LLMMessage,
  RecoveryListEntry,
} from '../../../InsuranceCheckControl/types/secondary-check';

const buildSampleRecoveryList = (): RecoveryListEntry[] => [
  // 契約者名: 非エラー
  { attribute: '契約者', section: 'original', title: '契約者名', value: '松本　直樹', errorFlag: false, checkResult: 'OK' },
  // 契〒: エラー
  { attribute: '契約者', section: 'original', title: '契〒', value: '*000', errorFlag: true, checkResult: 'NG' },
  { attribute: '契約者', section: 'first_recovery', title: '契〒_回復結果', value: '060-0001', errorFlag: true, checkResult: 'NG' },
  { attribute: '契約者', section: 'first_recovery', title: '契〒_回復理由', value: '既契約より', errorFlag: true, checkResult: 'NG' },
  // 契住所: エラー
  { attribute: '契約者', section: 'original', title: '契住所', value: '', errorFlag: true, checkResult: 'NG' },
  { attribute: '契約者', section: 'first_recovery', title: '契住所_回復結果', value: 'ﾎｯｶｲﾄﾞｳ...', errorFlag: true, checkResult: 'NG' },
  { attribute: '契約者', section: 'first_recovery', title: '契住所_回復理由', value: '既契約より', errorFlag: true, checkResult: 'NG' },
  // 被住所: 非エラー
  { attribute: '被保険者', section: 'original', title: '被住所', value: 'OK住所', errorFlag: false, checkResult: 'OK' },
];

const fields = (): FieldInfo[] => collectAllFields(buildSampleRecoveryList());

const userText = (text: string): LLMMessage => ({
  role: 'user',
  content: [{ type: 'text', text }],
});

const baseRequest = {
  systemPrompt: 'sys',
  tools: [
    { name: 'update_recovery_value' as const, description: '', inputSchema: {} },
    { name: 'file_inquiry' as const, description: '', inputSchema: {} },
    { name: 'finalize_check' as const, description: '', inputSchema: {} },
  ],
};

describe('collectAllFields / collectRecoveryTargets', () => {
  it('collectAllFields は original 行すべてを返す（エラー有無問わず）', () => {
    const all = collectAllFields(buildSampleRecoveryList());
    expect(all).toHaveLength(4);
    expect(all.map((f) => f.fieldName)).toEqual(['契約者名', '契〒', '契住所', '被住所']);
  });

  it('collectRecoveryTargets はエラー項目のみを返す', () => {
    const targets = collectRecoveryTargets(buildSampleRecoveryList());
    expect(targets.map((t) => t.fieldName)).toEqual(['契〒', '契住所']);
  });

  it('isError フラグが正しく伝搬する', () => {
    const all = collectAllFields(buildSampleRecoveryList());
    expect(all.find((f) => f.fieldName === '契〒')?.isError).toBe(true);
    expect(all.find((f) => f.fieldName === '契約者名')?.isError).toBe(false);
  });
});

describe('extractDecidedFields', () => {
  it('update_recovery_value の fieldName だけ拾う', () => {
    const messages: LLMMessage[] = [
      {
        role: 'assistant',
        content: [
          { type: 'tool_use', id: 't1', name: 'update_recovery_value', input: { fieldName: '契〒', value: '060-0001', reason: 'x' } },
          { type: 'tool_use', id: 't2', name: 'file_inquiry', input: { category: 'x', contents: 'y' } },
        ],
      },
    ];
    const result = extractDecidedFields(messages);
    expect(result.has('契〒')).toBe(true);
    expect(result.size).toBe(1);
  });
});

describe('MockLLMClient — 受動的な挙動', () => {
  it('初回はフィールドを歩かず、簡潔なガイドメッセージを返す', async () => {
    const client = new MockLLMClient(fields());
    const res = await client.respond({ ...baseRequest, messages: [] });
    expect(res.stopReason).toBe('end_turn');
    const text = res.message.content.find((c) => c.type === 'text');
    expect(text).toBeDefined();
    if (text && text.type === 'text') {
      expect(text.text).toContain('エラーあり');
      expect(text.text).toContain('契〒');
      expect(text.text).toContain('契住所');
    }
  });

  it('フィールド名 + 承認 で特定項目を一次値で承認', async () => {
    const client = new MockLLMClient(fields());
    const res = await client.respond({
      ...baseRequest,
      messages: [userText('契〒は OK')],
    });
    expect(res.stopReason).toBe('tool_use');
    const toolUses = res.message.content.filter((c) => c.type === 'tool_use');
    expect(toolUses).toHaveLength(1);
    const [tu] = toolUses;
    if (tu && tu.type === 'tool_use') {
      expect(tu.name).toBe('update_recovery_value');
      expect(tu.input).toMatchObject({ fieldName: '契〒', value: '060-0001', reason: '一次チェック結果を承認' });
    }
  });

  it('非エラー項目の承認は原値をコピーして記録', async () => {
    const client = new MockLLMClient(fields());
    const res = await client.respond({
      ...baseRequest,
      messages: [userText('被住所はそのままで')],
    });
    const tu = res.message.content.find((c) => c.type === 'tool_use');
    expect(tu).toBeDefined();
    if (tu && tu.type === 'tool_use') {
      expect(tu.input).toMatchObject({ fieldName: '被住所', value: 'OK住所' });
    }
  });

  it('フィールド名 + 値 で値を上書き', async () => {
    const client = new MockLLMClient(fields());
    const res = await client.respond({
      ...baseRequest,
      messages: [userText('契〒を 060-0002 に修正')],
    });
    const tu = res.message.content.find((c) => c.type === 'tool_use');
    if (tu && tu.type === 'tool_use') {
      expect(tu.name).toBe('update_recovery_value');
      expect(tu.input['fieldName']).toBe('契〒');
      expect(tu.input['value']).toBe('060-0002');
    } else {
      throw new Error('expected tool_use');
    }
  });

  it('一発で複数フィールドを処理する', async () => {
    const client = new MockLLMClient(fields());
    const res = await client.respond({
      ...baseRequest,
      messages: [userText('契〒はOK、契住所を「ﾎｯｶｲﾄﾞｳｻｯﾎﾟﾛ」で')],
    });
    const toolUses = res.message.content.filter((c) => c.type === 'tool_use');
    expect(toolUses).toHaveLength(2);
    const names = toolUses
      .map((tu) => (tu.type === 'tool_use' ? String(tu.input['fieldName']) : ''))
      .sort();
    expect(names).toEqual(['契〒', '契住所']);
  });

  it('「承認」単独はエラー項目を一括承認する', async () => {
    const client = new MockLLMClient(fields());
    const res = await client.respond({
      ...baseRequest,
      messages: [userText('承認')],
    });
    const toolUses = res.message.content.filter((c) => c.type === 'tool_use');
    expect(toolUses).toHaveLength(2);
    const names = toolUses
      .map((tu) => (tu.type === 'tool_use' ? String(tu.input['fieldName']) : ''))
      .sort();
    expect(names).toEqual(['契〒', '契住所']);
  });

  it('フィールド名 + 問い合わせ で file_inquiry を呼ぶ', async () => {
    const client = new MockLLMClient(fields());
    const res = await client.respond({
      ...baseRequest,
      messages: [userText('契住所 問い合わせで')],
    });
    const tu = res.message.content.find((c) => c.type === 'tool_use');
    if (tu && tu.type === 'tool_use') {
      expect(tu.name).toBe('file_inquiry');
      expect(String(tu.input['contents'])).toContain('契住所');
    } else {
      throw new Error('expected tool_use');
    }
  });

  it('エラー項目が未判断なら「最終承認」を拒否', async () => {
    const client = new MockLLMClient(fields());
    const res = await client.respond({ ...baseRequest, messages: [userText('最終承認')] });
    expect(res.stopReason).toBe('end_turn');
    const text = res.message.content.find((c) => c.type === 'text');
    if (text && text.type === 'text') {
      expect(text.text).toContain('未判断');
    }
  });

  it('エラー項目が全て判断済みなら「最終承認」で finalize_check(true)', async () => {
    const client = new MockLLMClient(fields());
    const history: LLMMessage[] = [
      {
        role: 'assistant',
        content: [
          { type: 'tool_use', id: 't1', name: 'update_recovery_value', input: { fieldName: '契〒', value: '060-0001', reason: 'x' } },
          { type: 'tool_use', id: 't2', name: 'update_recovery_value', input: { fieldName: '契住所', value: 'ﾎｯｶｲﾄﾞｳ', reason: 'x' } },
        ],
      },
      userText('最終承認'),
    ];
    const res = await client.respond({ ...baseRequest, messages: history });
    const tu = res.message.content.find((c) => c.type === 'tool_use');
    if (tu && tu.type === 'tool_use') {
      expect(tu.name).toBe('finalize_check');
      expect(tu.input['checkResult']).toBe(true);
    } else {
      throw new Error('expected tool_use');
    }
  });

  it('最終判定後はそれ以上の操作を拒否する', async () => {
    const client = new MockLLMClient(fields());
    const history: LLMMessage[] = [
      {
        role: 'assistant',
        content: [
          { type: 'tool_use', id: 't1', name: 'finalize_check', input: { checkResult: true, status: '次工程待ち' } },
        ],
      },
      userText('追加で修正したい'),
    ];
    const res = await client.respond({ ...baseRequest, messages: history });
    expect(res.stopReason).toBe('end_turn');
    const text = res.message.content.find((c) => c.type === 'text');
    if (text && text.type === 'text') {
      expect(text.text).toContain('最終判定');
    }
  });
});
