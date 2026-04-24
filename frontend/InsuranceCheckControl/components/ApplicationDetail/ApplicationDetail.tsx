import {
  useEffect,
  useRef,
  useState,
  type CSSProperties,
  type Dispatch,
  type FC,
  type MouseEvent,
  type ReactNode,
  type SetStateAction,
  type WheelEvent,
} from 'react';
import type { ChatMessage, ChatMessagesByTab, ChatTab } from '../../types/domain';
import { AI_RESPONSES } from '../../services/mock-data';
import { pickRandom } from '../../utils/formatters';
import { StatusBadge } from '../common/StatusBadge';
import { CheckResultView } from '../CheckResultView/CheckResultView';
import { ScanPlaceholder } from '../ImageViewer/ScanPlaceholder';
import { ContractPlaceholder } from '../ImageViewer/ContractPlaceholder';

type ViewerTabId = 'scan' | 'contract';

interface ApplicationDetailProps {
  tabs: ChatTab[];
  activeTabId: string | null;
  chatSplitPct: number;
  fontSize: number;
  messages: ChatMessagesByTab;
  setMessages: Dispatch<SetStateAction<ChatMessagesByTab>>;
  onTabChange: (id: string) => void;
  onTabClose: (id: string) => void;
}

const zBtn: CSSProperties = {
  background: 'var(--gray-lt)',
  border: '1px solid var(--border)',
  color: 'var(--navy-800)',
  borderRadius: 5,
  padding: '4px 10px',
  fontSize: 13,
  cursor: 'pointer',
};

const viewerTabs: Array<{ id: ViewerTabId; label: string; icon: ReactNode }> = [
  {
    id: 'scan',
    label: '申込書スキャン',
    icon: (
      <path
        d="M4 4h12l4 4v12a2 2 0 01-2 2H4a2 2 0 01-2-2V6a2 2 0 012-2z M14 4v6h6"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    ),
  },
  {
    id: 'contract',
    label: '既契約情報',
    icon: (
      <path
        d="M9 12h6m-6 4h6M7 8h10M5 4h14a1 1 0 011 1v14a1 1 0 01-1 1H5a1 1 0 01-1-1V5a1 1 0 011-1z"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
      />
    ),
  },
];

export const ApplicationDetail: FC<ApplicationDetailProps> = ({
  tabs,
  activeTabId,
  chatSplitPct,
  messages,
  setMessages,
  onTabChange,
  onTabClose,
}) => {
  const [input, setInput] = useState('');
  const [typing, setTyping] = useState(false);
  const [scale, setScale] = useState(1);
  const [offset, setOffset] = useState({ x: 0, y: 0 });
  const [dragging, setDragging] = useState(false);
  const [viewerTab, setViewerTab] = useState<ViewerTabId>('scan');
  const dragStart = useRef<{ x: number; y: number } | null>(null);
  const msgEndRef = useRef<HTMLDivElement | null>(null);
  const activeTab = tabs.find((t) => t.id === activeTabId) ?? null;
  const activeMsgs: ChatMessage[] = activeTabId ? (messages[activeTabId] ?? []) : [];

  useEffect(() => {
    if (!activeTab || !activeTabId) return;
    if (messages[activeTabId]) return;
    setMessages((m) => ({
      ...m,
      [activeTabId]: [
        { role: 'ai', type: 'recovery', secNo: activeTab.secNo },
        {
          role: 'ai',
          text: `証券番号「${activeTab.secNo}」のエラー回復結果を上記の通り表示しました。ご確認の上、必要な対応をお知らせください。`,
        },
      ],
    }));
  }, [activeTab, activeTabId, messages, setMessages]);

  useEffect(() => {
    msgEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [activeMsgs, typing]);

  useEffect(() => {
    setScale(1);
    setOffset({ x: 0, y: 0 });
  }, [activeTabId, viewerTab]);

  const sendMsg = (): void => {
    if (!input.trim() || typing || !activeTabId || !activeTab) return;
    const txt = input.trim();
    setMessages((m) => ({
      ...m,
      [activeTabId]: [...(m[activeTabId] ?? []), { role: 'user', text: txt }],
    }));
    setInput('');
    setTyping(true);
    setTimeout(
      () => {
        const fn = pickRandom(AI_RESPONSES);
        setMessages((m) => ({
          ...m,
          [activeTabId]: [...(m[activeTabId] ?? []), { role: 'ai', text: fn(activeTab.secNo) }],
        }));
        setTyping(false);
      },
      800 + Math.random() * 600,
    );
  };

  const handleWheel = (e: WheelEvent<HTMLDivElement>): void => {
    e.preventDefault();
    setScale((s) => Math.max(0.3, Math.min(4, s - e.deltaY * 0.001)));
  };
  const handleMouseDown = (e: MouseEvent<HTMLDivElement>): void => {
    setDragging(true);
    dragStart.current = { x: e.clientX - offset.x, y: e.clientY - offset.y };
  };
  const handleMouseMove = (e: MouseEvent<HTMLDivElement>): void => {
    if (!dragging || !dragStart.current) return;
    setOffset({ x: e.clientX - dragStart.current.x, y: e.clientY - dragStart.current.y });
  };
  const handleMouseUp = (): void => setDragging(false);

  if (tabs.length === 0) {
    return (
      <div
        style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          gap: 12,
          color: 'var(--gray)',
        }}
      >
        <svg width="48" height="48" fill="none" viewBox="0 0 24 24" opacity=".3">
          <path
            d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
          />
        </svg>
        <div style={{ fontSize: 14 }}>
          「担当一覧」から証券番号を選択してチャットを開いてください
        </div>
      </div>
    );
  }

  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0 }}>
      <div
        style={{
          background: 'var(--gray-lt)',
          borderBottom: '1px solid var(--border)',
          display: 'flex',
          alignItems: 'flex-end',
          overflowX: 'auto',
          flexShrink: 0,
          paddingLeft: 8,
          paddingTop: 6,
        }}
      >
        {tabs.map((tab) => {
          const active = tab.id === activeTabId;
          return (
            <div
              key={tab.id}
              onClick={() => onTabChange(tab.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 8,
                padding: '8px 14px',
                cursor: 'pointer',
                background: active ? '#fff' : 'transparent',
                borderTop: `2px solid ${active ? 'var(--accent)' : 'transparent'}`,
                border: active ? '1px solid var(--border)' : '1px solid transparent',
                borderBottom: active ? '1px solid #fff' : '1px solid transparent',
                borderRadius: '6px 6px 0 0',
                marginRight: 2,
                flexShrink: 0,
                transition: 'background .12s',
              }}
            >
              <StatusBadge status={tab.status} />
              <span
                style={{
                  fontSize: 12,
                  fontWeight: active ? 700 : 400,
                  color: active ? 'var(--navy-900)' : 'var(--gray)',
                  whiteSpace: 'nowrap',
                  maxWidth: 130,
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                }}
              >
                {tab.secNo}
              </span>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onTabClose(tab.id);
                }}
                style={{
                  background: 'none',
                  border: 'none',
                  cursor: 'pointer',
                  color: 'var(--gray)',
                  fontSize: 13,
                  lineHeight: 1,
                  padding: '0 2px',
                  borderRadius: 3,
                }}
                onMouseEnter={(e) => (e.currentTarget.style.color = 'var(--red)')}
                onMouseLeave={(e) => (e.currentTarget.style.color = 'var(--gray)')}
              >
                ✕
              </button>
            </div>
          );
        })}
      </div>
      {activeTab && (
        <div style={{ display: 'flex', flex: 1, overflow: 'hidden', minHeight: 0 }}>
          <div
            style={{
              width: `${chatSplitPct}%`,
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
                {activeTab.secNo}
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 4 }}>
                <StatusBadge status={activeTab.status} />
                <span style={{ fontSize: 11, color: 'var(--gray)' }}>取込日: {activeTab.importDate}</span>
              </div>
            </div>
            <div
              style={{
                flex: 1,
                overflowY: 'auto',
                padding: '16px',
                display: 'flex',
                flexDirection: 'column',
                gap: 12,
              }}
            >
              {activeMsgs.map((m, i) => (
                <div
                  key={i}
                  style={{
                    display: 'flex',
                    flexDirection: m.role === 'user' ? 'row-reverse' : 'row',
                    gap: 8,
                    alignItems: 'flex-end',
                    animation: 'fadeIn .2s ease',
                  }}
                >
                  {m.role === 'ai' && (
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
                  {m.type === 'recovery' ? (
                    <CheckResultView secNo={m.secNo} />
                  ) : (
                    <div
                      style={{
                        maxWidth: '78%',
                        padding: '9px 13px',
                        borderRadius:
                          m.role === 'user' ? '14px 14px 4px 14px' : '14px 14px 14px 4px',
                        background: m.role === 'user' ? 'var(--accent)' : 'var(--navy-50)',
                        color: m.role === 'user' ? '#fff' : 'var(--navy-900)',
                        fontSize: 13,
                        lineHeight: 1.6,
                        boxShadow: 'var(--shadow-sm)',
                      }}
                    >
                      {m.text}
                    </div>
                  )}
                </div>
              ))}
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
                    sendMsg();
                  }
                }}
                placeholder="メッセージを入力... (Enterで送信)"
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
              />
              <button
                onClick={sendMsg}
                disabled={!input.trim() || typing}
                style={{
                  padding: '9px 14px',
                  background: input.trim() && !typing ? 'var(--accent)' : '#d1d5db',
                  color: '#fff',
                  border: 'none',
                  borderRadius: 8,
                  fontSize: 13,
                  fontWeight: 600,
                  cursor: input.trim() && !typing ? 'pointer' : 'default',
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
          <div
            style={{
              flex: 1,
              display: 'flex',
              flexDirection: 'column',
              background: '#f0f1f3',
              minWidth: 0,
            }}
          >
            <div
              style={{
                display: 'flex',
                alignItems: 'flex-end',
                background: '#e5e7eb',
                paddingLeft: 8,
                paddingTop: 6,
                borderBottom: '1px solid var(--border)',
                flexShrink: 0,
                gap: 2,
              }}
            >
              {viewerTabs.map((t) => {
                const active = viewerTab === t.id;
                return (
                  <button
                    key={t.id}
                    onClick={() => setViewerTab(t.id)}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 6,
                      padding: '8px 14px',
                      border: '1px solid var(--border)',
                      borderBottom: active ? '1px solid #fff' : '1px solid var(--border)',
                      borderRadius: '7px 7px 0 0',
                      background: active ? '#fff' : 'transparent',
                      color: active ? 'var(--navy-900)' : 'var(--gray)',
                      fontSize: 12,
                      fontWeight: active ? 700 : 500,
                      cursor: 'pointer',
                      marginBottom: -1,
                      position: 'relative',
                    }}
                  >
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none">
                      {t.icon}
                    </svg>
                    {t.label}
                    {t.id === 'contract' && (
                      <span
                        style={{
                          marginLeft: 4,
                          padding: '1px 7px',
                          borderRadius: 10,
                          fontSize: 9,
                          fontWeight: 700,
                          background: active ? 'var(--accent-lt)' : '#d1d5db',
                          color: active ? 'var(--accent)' : '#6b7280',
                        }}
                      >
                        参考
                      </span>
                    )}
                  </button>
                );
              })}
            </div>
            <div
              style={{
                padding: '8px 14px',
                background: '#fff',
                display: 'flex',
                alignItems: 'center',
                gap: 10,
                flexShrink: 0,
                borderBottom: '1px solid var(--border)',
              }}
            >
              <span style={{ color: 'var(--gray)', fontSize: 12, fontWeight: 600 }}>
                {viewerTab === 'scan' ? '申込書スキャン画像' : 'エラー回復の根拠となった既契約データ'}
              </span>
              <div style={{ flex: 1 }} />
              <button onClick={() => setScale((s) => Math.min(4, s + 0.2))} style={zBtn}>
                ＋
              </button>
              <span style={{ color: 'var(--gray)', fontSize: 12, minWidth: 40, textAlign: 'center' }}>
                {Math.round(scale * 100)}%
              </span>
              <button onClick={() => setScale((s) => Math.max(0.3, s - 0.2))} style={zBtn}>
                －
              </button>
              <button
                onClick={() => {
                  setScale(1);
                  setOffset({ x: 0, y: 0 });
                }}
                style={{ ...zBtn, minWidth: 56 }}
              >
                リセット
              </button>
            </div>
            <div
              style={{
                flex: 1,
                overflow: 'hidden',
                cursor: dragging ? 'grabbing' : 'grab',
                position: 'relative',
                userSelect: 'none',
              }}
              onWheel={handleWheel}
              onMouseDown={handleMouseDown}
              onMouseMove={handleMouseMove}
              onMouseUp={handleMouseUp}
              onMouseLeave={handleMouseUp}
            >
              <div
                style={{
                  position: 'absolute',
                  inset: 0,
                  display: 'flex',
                  alignItems: 'flex-start',
                  justifyContent: 'center',
                  padding: 24,
                  overflow: 'hidden',
                }}
              >
                {viewerTab === 'scan' ? (
                  <ScanPlaceholder scale={scale} offset={offset} secNo={activeTab.secNo} />
                ) : (
                  <ContractPlaceholder scale={scale} offset={offset} secNo={activeTab.secNo} />
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
