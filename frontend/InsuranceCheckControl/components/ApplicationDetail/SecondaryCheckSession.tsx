import { useEffect, useMemo, useRef, useState, type FC } from 'react';
import { useSecondaryCheck } from '../../hooks/useSecondaryCheck';
import { collectRecoveryTargets, extractDecidedFields } from '../../services/mock-llm-client';
import type { ChatTab } from '../../types/domain';
import type { ChatUIMessage, LLMMessage } from '../../types/secondary-check';
import { CheckResultView } from '../CheckResultView/CheckResultView';
import { ImageViewer } from '../ImageViewer/ImageViewer';
import { StatusBadge } from '../common/StatusBadge';
import { SecondaryCheckPanel } from '../SecondaryCheckPanel';

interface SecondaryCheckSessionProps {
  tab: ChatTab;
  fontSize: number;
  hidden: boolean;
}

interface TextMessageProps {
  message: ChatUIMessage & { kind: 'user_text' | 'assistant_text' };
}

const TextMessage: FC<TextMessageProps> = ({ message }) => {
  const isUser = message.kind === 'user_text';
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: isUser ? 'row-reverse' : 'row',
        gap: 8,
        alignItems: 'flex-end',
        animation: 'fadeIn .2s ease',
      }}
    >
      {!isUser && (
        <div
          style={{
            width: 28,
            height: 28,
            borderRadius: '50%',
            background: 'var(--accent)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexShrink: 0,
          }}
        >
          <svg width="13" height="13" fill="none" viewBox="0 0 24 24">
            <circle cx="12" cy="8" r="4" stroke="#fff" strokeWidth="2" />
            <path
              d="M4 20c0-4 3.6-7 8-7s8 3 8 7"
              stroke="#fff"
              strokeWidth="2"
              strokeLinecap="round"
            />
          </svg>
        </div>
      )}
      <div
        style={{
          maxWidth: '78%',
          padding: '9px 13px',
          borderRadius: isUser ? '14px 14px 4px 14px' : '14px 14px 14px 4px',
          background: isUser ? 'var(--accent)' : 'var(--navy-50)',
          color: isUser ? '#fff' : 'var(--navy-900)',
          fontSize: 13,
          lineHeight: 1.6,
          boxShadow: 'var(--shadow-sm)',
          whiteSpace: 'pre-wrap',
        }}
      >
        {message.text}
      </div>
    </div>
  );
};

const ToolCallMessage: FC<{ message: ChatUIMessage & { kind: 'tool_call' } }> = ({ message }) => {
  const label = {
    update_recovery_value: '値更新',
    file_inquiry: '問い合わせ起票',
    finalize_check: '最終判定',
  }[message.call.name];
  const summary =
    message.call.name === 'update_recovery_value'
      ? `${message.call.input.fieldName} ← ${message.call.input.value}`
      : message.call.name === 'file_inquiry'
        ? message.call.input.category
        : message.call.input.checkResult
          ? '承認'
          : '差し戻し';
  return (
    <div
      style={{
        alignSelf: 'flex-start',
        maxWidth: '85%',
        padding: '7px 11px',
        borderRadius: 8,
        border: '1px dashed var(--accent)',
        background: '#fff',
        color: 'var(--navy-800)',
        fontSize: 11,
        lineHeight: 1.5,
        fontFamily: 'monospace',
      }}
    >
      <span style={{ fontWeight: 700, color: 'var(--accent)' }}>▶ {label}</span>　{summary}
    </div>
  );
};

const ToolResultMessage: FC<{ message: ChatUIMessage & { kind: 'tool_result' } }> = ({
  message,
}) => (
  <div
    style={{
      alignSelf: 'flex-start',
      maxWidth: '85%',
      padding: '7px 11px',
      borderRadius: 8,
      background: message.isError ? 'var(--red-lt)' : 'var(--green-lt)',
      color: message.isError ? 'var(--red)' : 'var(--green)',
      fontSize: 11,
      lineHeight: 1.5,
    }}
  >
    <span style={{ fontWeight: 700 }}>{message.isError ? '✗' : '✓'}</span>　{message.message}
  </div>
);

export const SecondaryCheckSession: FC<SecondaryCheckSessionProps> = ({
  tab,
  fontSize,
  hidden,
}) => {
  const {
    detail,
    loading,
    typing,
    chatMessages,
    toolCallLog,
    finalDecision,
    sendUserMessage,
    error,
  } = useSecondaryCheck({ policyNumber: tab.secNo });

  const [input, setInput] = useState('');
  const msgEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!hidden) msgEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages, typing, hidden]);

  const { decidedFields, totalFields } = useMemo(() => {
    if (!detail) return { decidedFields: 0, totalFields: 0 };
    const targets = collectRecoveryTargets(detail.recoveryList);
    const pseudoMessages: LLMMessage[] = toolCallLog.map((entry) => ({
      role: 'assistant',
      content: [
        {
          type: 'tool_use',
          id: entry.id,
          name: entry.call.name,
          input: entry.call.input as Record<string, string | boolean>,
        },
      ],
    }));
    const decided = extractDecidedFields(pseudoMessages);
    return { decidedFields: decided.size, totalFields: targets.length };
  }, [detail, toolCallLog]);

  const send = async (): Promise<void> => {
    if (!input.trim() || typing) return;
    const txt = input.trim();
    setInput('');
    await sendUserMessage(txt);
  };

  return (
    <div
      style={{
        display: hidden ? 'none' : 'flex',
        flex: 1,
        flexDirection: 'column',
        minHeight: 0,
        overflow: 'hidden',
        fontSize,
      }}
    >
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden', minHeight: 0 }}>
        {/* Pane 1: Chat */}
        <div
          style={{
            width: '38%',
            borderRight: '1px solid var(--border)',
            display: 'flex',
            flexDirection: 'column',
            background: '#fff',
            minWidth: 0,
          }}
        >
          <div
            style={{
              padding: '12px 16px',
              borderBottom: '1px solid var(--border)',
              background: 'var(--navy-50)',
            }}
          >
            <div style={{ fontSize: 13, fontWeight: 700, color: 'var(--navy-900)' }}>
              {tab.secNo}
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 4 }}>
              <StatusBadge status={tab.status} />
              <span style={{ fontSize: 11, color: 'var(--gray)' }}>取込日: {tab.importDate}</span>
              {detail && (
                <span
                  style={{
                    fontSize: 11,
                    color: 'var(--accent)',
                    fontWeight: 600,
                    marginLeft: 'auto',
                  }}
                >
                  業務種別: {detail.businessType}
                </span>
              )}
            </div>
          </div>
          <div
            style={{
              flex: 1,
              overflowY: 'auto',
              padding: '16px',
              display: 'flex',
              flexDirection: 'column',
              gap: 10,
            }}
          >
            {loading && (
              <div style={{ color: 'var(--gray)', fontSize: 12, padding: 12 }}>
                詳細データを取得しています...
              </div>
            )}
            {error && (
              <div
                style={{
                  padding: '8px 12px',
                  background: 'var(--red-lt)',
                  color: 'var(--red)',
                  fontSize: 12,
                  borderRadius: 6,
                }}
              >
                {error}
              </div>
            )}
            {chatMessages.map((m, i) => {
              const key = `${i}-${m.timestamp}`;
              if (m.kind === 'user_text' || m.kind === 'assistant_text') {
                return <TextMessage key={key} message={m} />;
              }
              if (m.kind === 'recovery_table') {
                return (
                  <div key={key} style={{ display: 'flex', gap: 8, alignItems: 'flex-end' }}>
                    <div
                      style={{
                        width: 28,
                        height: 28,
                        borderRadius: '50%',
                        background: 'var(--accent)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        flexShrink: 0,
                      }}
                    >
                      <svg width="13" height="13" fill="none" viewBox="0 0 24 24">
                        <circle cx="12" cy="8" r="4" stroke="#fff" strokeWidth="2" />
                        <path
                          d="M4 20c0-4 3.6-7 8-7s8 3 8 7"
                          stroke="#fff"
                          strokeWidth="2"
                          strokeLinecap="round"
                        />
                      </svg>
                    </div>
                    <CheckResultView secNo={m.secNo} />
                  </div>
                );
              }
              if (m.kind === 'tool_call') {
                return <ToolCallMessage key={key} message={m} />;
              }
              return <ToolResultMessage key={key} message={m} />;
            })}
            {typing && (
              <div style={{ display: 'flex', gap: 8, alignItems: 'flex-end' }}>
                <div
                  style={{
                    width: 28,
                    height: 28,
                    borderRadius: '50%',
                    background: 'var(--accent)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  <svg width="13" height="13" fill="none" viewBox="0 0 24 24">
                    <circle cx="12" cy="8" r="4" stroke="#fff" strokeWidth="2" />
                    <path
                      d="M4 20c0-4 3.6-7 8-7s8 3 8 7"
                      stroke="#fff"
                      strokeWidth="2"
                      strokeLinecap="round"
                    />
                  </svg>
                </div>
                <div
                  style={{
                    padding: '10px 14px',
                    borderRadius: '14px 14px 14px 4px',
                    background: 'var(--navy-50)',
                    display: 'flex',
                    gap: 4,
                    alignItems: 'center',
                  }}
                >
                  {[0, 1, 2].map((j) => (
                    <div
                      key={j}
                      style={{
                        width: 6,
                        height: 6,
                        borderRadius: '50%',
                        background: 'var(--navy-500)',
                        animation: 'bounce 1.2s infinite',
                        animationDelay: `${j * 0.2}s`,
                      }}
                    />
                  ))}
                </div>
              </div>
            )}
            <div ref={msgEndRef} />
          </div>
          <div
            style={{
              padding: '10px 14px',
              borderTop: '1px solid var(--border)',
              background: 'var(--navy-50)',
              display: 'flex',
              gap: 8,
              alignItems: 'flex-end',
            }}
          >
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  void send();
                }
              }}
              placeholder="承認 / 値を入力 / 問い合わせ / 最終承認 など (Enter で送信)"
              rows={2}
              style={{
                flex: 1,
                padding: '8px 12px',
                border: '1.5px solid var(--border)',
                borderRadius: 8,
                fontSize: 13,
                resize: 'none',
                outline: 'none',
                lineHeight: 1.5,
              }}
              onFocus={(e) => (e.target.style.borderColor = 'var(--accent)')}
              onBlur={(e) => (e.target.style.borderColor = 'var(--border)')}
              disabled={loading || typing || finalDecision.status !== 'pending'}
            />
            <button
              onClick={() => void send()}
              disabled={!input.trim() || typing || loading || finalDecision.status !== 'pending'}
              style={{
                padding: '9px 14px',
                background:
                  input.trim() && !typing && !loading && finalDecision.status === 'pending'
                    ? 'var(--accent)'
                    : '#d1d5db',
                color: '#fff',
                border: 'none',
                borderRadius: 8,
                fontSize: 13,
                fontWeight: 600,
                cursor:
                  input.trim() && !typing && !loading && finalDecision.status === 'pending'
                    ? 'pointer'
                    : 'default',
                height: 42,
                display: 'flex',
                alignItems: 'center',
                gap: 5,
              }}
            >
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none">
                <path
                  d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
              送信
            </button>
          </div>
        </div>

        {/* Pane 2: Image Viewer */}
        <ImageViewer secNo={tab.secNo} />

        {/* Pane 3: Decision History (right) */}
        <div style={{ width: '22%', display: 'flex', flexDirection: 'column', minWidth: 0 }}>
          <SecondaryCheckPanel
            toolCallLog={toolCallLog}
            finalDecision={finalDecision}
            decidedFields={decidedFields}
            totalFields={totalFields}
          />
        </div>
      </div>
    </div>
  );
};
