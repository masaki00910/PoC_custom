/**
 * 二次チェック画面の型定義。
 *
 * Power Automate の S-XX-XX フロー (Copilot Studio Skills) と対応:
 * - S-03-001 詳細データの取得 → SecondaryCheckDetail
 * - S-04-001 ステータス更新      → finalize_check tool
 * - S-04-002 詳細データの更新    → update_recovery_value tool
 * - S-04-003 問い合わせ起票      → file_inquiry tool
 *
 * Q4 暫定仕様 (DB 設計見直しあり): 一次チェック結果をそのまま承認する場合も
 * update_recovery_value で一次値をコピーして明示記録する。
 */

export type RecoverySection = 'original' | 'first_recovery' | 'second_recovery';

export interface RecoveryListEntry {
  attribute: string;
  section: RecoverySection;
  title: string;
  value: string;
  errorFlag: boolean;
  checkResult: string;
}

export interface SecondaryCheckDetail {
  policyNumber: string;
  businessType: '漢字' | '住所';
  recoveryList: RecoveryListEntry[];
  sharepointUrl: string;
  caDocumentImportId: string;
}

/** LLM が呼び出す 3 種のツール。Copilot Studio の Skills に相当。 */
export type ToolCall =
  | {
      name: 'update_recovery_value';
      input: {
        fieldName: string;
        value: string;
        reason: string;
      };
    }
  | {
      name: 'file_inquiry';
      input: {
        category: string;
        contents: string;
      };
    }
  | {
      name: 'finalize_check';
      input: {
        checkResult: boolean;
        status: string;
      };
    };

export type ToolName = ToolCall['name'];

export interface ToolCallLogEntry {
  id: string;
  timestamp: string;
  call: ToolCall;
  result: 'ok' | 'error';
  message?: string;
}

export type FinalDecisionStatus = 'pending' | 'approved' | 'rejected';

export interface FinalDecision {
  status: FinalDecisionStatus;
  reviewer?: string;
  completedAt?: string;
  note?: string;
}

/** LLM クライアントに渡す会話メッセージ。Anthropic API の shape に近い。 */
export type LLMMessageRole = 'user' | 'assistant';

export type LLMContentBlock =
  | { type: 'text'; text: string }
  | { type: 'tool_use'; id: string; name: ToolName; input: Record<string, string | boolean> }
  | { type: 'tool_result'; toolUseId: string; content: string; isError?: boolean };

export interface LLMMessage {
  role: LLMMessageRole;
  content: LLMContentBlock[];
}

/** 画面上に表示する UI 用メッセージ（チャット欄の描画対象）。 */
export type ChatUIMessage =
  | { kind: 'user_text'; text: string; timestamp: string }
  | { kind: 'assistant_text'; text: string; timestamp: string }
  | { kind: 'recovery_table'; secNo: string; timestamp: string }
  | { kind: 'tool_call'; call: ToolCall; timestamp: string }
  | { kind: 'tool_result'; toolName: ToolName; message: string; isError: boolean; timestamp: string };
