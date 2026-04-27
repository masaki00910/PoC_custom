import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import type { LLMClient, LLMRequest, LLMToolDefinition } from '../services/llm-client';
import { MockLLMClient, collectAllFields } from '../services/mock-llm-client';
import {
  applyToolCall,
  fetchSecondaryCheckDetail,
  initialBackendState,
  type MockBackendState,
} from '../services/secondary-check-mock';
import type {
  ChatUIMessage,
  LLMMessage,
  SecondaryCheckDetail,
  ToolCall,
  ToolCallLogEntry,
} from '../types/secondary-check';

const TOOL_DEFINITIONS: LLMToolDefinition[] = [
  {
    name: 'update_recovery_value',
    description:
      '二次チェック担当者の判断として、指定フィールドの再回復値・再回復理由を記録する。一次チェック結果をそのまま承認する場合も、一次回復値をコピーして理由「一次チェック結果を承認」で呼ぶこと。',
    inputSchema: {
      type: 'object',
      properties: {
        fieldName: { type: 'string' },
        value: { type: 'string' },
        reason: { type: 'string' },
      },
      required: ['fieldName', 'value', 'reason'],
    },
  },
  {
    name: 'file_inquiry',
    description: '判断が難しい項目について問い合わせ管理テーブルに起票する。',
    inputSchema: {
      type: 'object',
      properties: {
        category: { type: 'string' },
        contents: { type: 'string' },
      },
      required: ['category', 'contents'],
    },
  },
  {
    name: 'finalize_check',
    description: '二次チェック全体の最終判定を登録する。全フィールドの判断が揃ってから呼ぶ。',
    inputSchema: {
      type: 'object',
      properties: {
        checkResult: { type: 'boolean' },
        status: { type: 'string' },
      },
      required: ['checkResult', 'status'],
    },
  },
];

const SYSTEM_PROMPT_BASE =
  '保険申込書の二次チェック担当者を支援するアシスタントです。' +
  '一次チェック（AI エラー回復）の結果を担当者に提示し、承認 / 値上書き / 問い合わせ のいずれかで判断を進めてください。' +
  '判断が揃ったら最終承認か差し戻しを確定してください。';

const nowIso = (): string => new Date().toISOString();

interface UseSecondaryCheckOptions {
  policyNumber: string;
  client?: LLMClient;
}

export interface UseSecondaryCheckResult {
  detail: SecondaryCheckDetail | null;
  loading: boolean;
  typing: boolean;
  chatMessages: ChatUIMessage[];
  toolCallLog: ToolCallLogEntry[];
  finalDecision: MockBackendState['finalDecision'];
  sendUserMessage: (text: string) => Promise<void>;
  error: string | null;
}

export const useSecondaryCheck = ({
  policyNumber,
  client: injectedClient,
}: UseSecondaryCheckOptions): UseSecondaryCheckResult => {
  const [detail, setDetail] = useState<SecondaryCheckDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [typing, setTyping] = useState(false);
  const [chatMessages, setChatMessages] = useState<ChatUIMessage[]>([]);
  const [backendState, setBackendState] = useState<MockBackendState>(initialBackendState);
  const [error, setError] = useState<string | null>(null);

  const llmMessagesRef = useRef<LLMMessage[]>([]);
  const clientRef = useRef<LLMClient | null>(null);

  const systemPrompt = useMemo(
    () =>
      detail
        ? `${SYSTEM_PROMPT_BASE}\n対象証券番号: ${detail.policyNumber}\n業務種別: ${detail.businessType}`
        : SYSTEM_PROMPT_BASE,
    [detail],
  );

  // 最新 backendState を参照するための ref
  const backendStateRef = useRef(backendState);
  useEffect(() => {
    backendStateRef.current = backendState;
  }, [backendState]);

  const applyToolCallSafely = useCallback(
    (call: ToolCall): ReturnType<typeof applyToolCall> | null => {
      if (
        call.name !== 'update_recovery_value' &&
        call.name !== 'file_inquiry' &&
        call.name !== 'finalize_check'
      ) {
        return null;
      }
      const result = applyToolCall(backendStateRef.current, call);
      backendStateRef.current = result.nextState;
      return result;
    },
    [],
  );

  // invokeLLM は systemPrompt → detail に依存して再生成されるため、useEffect の deps に入れると
   // setDetail 直後に初期化が再実行されて挨拶が 2 回出る。ref 経由で呼び出して deps から外す。
  const invokeLLMRef = useRef<() => Promise<void>>(async () => {});

  const invokeLLM = useCallback(async () => {
    const client = clientRef.current;
    if (!client) return;

    setTyping(true);
    try {
      // tool_use が続く限り繰り返す（agentic ループ）
      let safetyCounter = 0;
      while (safetyCounter < 5) {
        safetyCounter += 1;
        const request: LLMRequest = {
          systemPrompt,
          messages: llmMessagesRef.current,
          tools: TOOL_DEFINITIONS,
        };
        const response = await client.respond(request);

        llmMessagesRef.current = [...llmMessagesRef.current, response.message];

        const timestamp = nowIso();
        const uiAppends: ChatUIMessage[] = [];
        const toolUseResults: Array<{ toolUseId: string; content: string; isError: boolean }> = [];

        for (const block of response.message.content) {
          if (block.type === 'text' && block.text.trim().length > 0) {
            uiAppends.push({ kind: 'assistant_text', text: block.text, timestamp });
          } else if (block.type === 'tool_use') {
            const call = { name: block.name, input: block.input } as ToolCall;
            const applied = applyToolCallSafely(call);
            if (applied) {
              uiAppends.push({ kind: 'tool_call', call: applied.entry.call, timestamp });
              setBackendState(applied.nextState);
              uiAppends.push({
                kind: 'tool_result',
                toolName: applied.entry.call.name,
                message: applied.entry.message ?? '完了',
                isError: applied.entry.result === 'error',
                timestamp,
              });
              toolUseResults.push({
                toolUseId: block.id,
                content: applied.entry.message ?? 'OK',
                isError: false,
              });
            } else {
              uiAppends.push({
                kind: 'tool_result',
                toolName: block.name,
                message: '不正なツール呼び出しが検出されました',
                isError: true,
                timestamp,
              });
              toolUseResults.push({
                toolUseId: block.id,
                content: 'invalid tool call',
                isError: true,
              });
            }
          }
        }

        if (uiAppends.length > 0) {
          setChatMessages((prev) => [...prev, ...uiAppends]);
        }

        if (response.stopReason === 'end_turn' || toolUseResults.length === 0) {
          break;
        }

        // tool_use があった場合、tool_result を user role で追加して再度 LLM に渡す
        const toolResultMessage: LLMMessage = {
          role: 'user',
          content: toolUseResults.map((r) => ({
            type: 'tool_result',
            toolUseId: r.toolUseId,
            content: r.content,
            isError: r.isError,
          })),
        };
        llmMessagesRef.current = [...llmMessagesRef.current, toolResultMessage];
      }
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'LLM 呼び出しに失敗しました');
    } finally {
      setTyping(false);
    }
    // backendState を state 経由で同期的に最新化するため、applyToolCallSafely は closure で参照する
  }, [systemPrompt, applyToolCallSafely]);

  // invokeLLM は毎レンダー再生成されうるため ref を追従させ、useEffect からは ref 経由で呼ぶ
  useEffect(() => {
    invokeLLMRef.current = invokeLLM;
  }, [invokeLLM]);

  // 初期化: detail 取得 → MockLLMClient 構築 → 初回 LLM 応答
  // deps は policyNumber / injectedClient のみ。invokeLLM は deps に入れない（再実行ループ回避）
  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    setChatMessages([]);
    setBackendState(initialBackendState());
    llmMessagesRef.current = [];

    fetchSecondaryCheckDetail(policyNumber)
      .then(async (d) => {
        if (cancelled) return;
        setDetail(d);
        const fields = collectAllFields(d.recoveryList);
        clientRef.current = injectedClient ?? new MockLLMClient(fields);
        // チャット冒頭に一次チェック結果の構造化表（CheckResultView）をピン留めする
        setChatMessages([
          { kind: 'recovery_table', secNo: d.policyNumber, timestamp: nowIso() },
        ]);
        setLoading(false);
        if (cancelled) return;
        await invokeLLMRef.current();
      })
      .catch((e: unknown) => {
        if (cancelled) return;
        setError(e instanceof Error ? e.message : '詳細取得に失敗しました');
        setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [policyNumber, injectedClient]);

  const sendUserMessage = useCallback(
    async (text: string) => {
      const trimmed = text.trim();
      if (!trimmed || typing || !clientRef.current) return;
      const timestamp = nowIso();
      setChatMessages((prev) => [...prev, { kind: 'user_text', text: trimmed, timestamp }]);
      llmMessagesRef.current = [
        ...llmMessagesRef.current,
        { role: 'user', content: [{ type: 'text', text: trimmed }] },
      ];
      await invokeLLM();
    },
    [invokeLLM, typing],
  );

  return {
    detail,
    loading,
    typing,
    chatMessages,
    toolCallLog: backendState.toolCallLog,
    finalDecision: backendState.finalDecision,
    sendUserMessage,
    error,
  };
};
