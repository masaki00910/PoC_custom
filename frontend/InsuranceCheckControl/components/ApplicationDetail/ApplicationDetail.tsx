import type { FC } from 'react';
import type { ChatTab } from '../../types/domain';
import { StatusBadge } from '../common/StatusBadge';
import { SecondaryCheckSession } from './SecondaryCheckSession';

interface ApplicationDetailProps {
  tabs: ChatTab[];
  activeTabId: string | null;
  fontSize: number;
  onTabChange: (id: string) => void;
  onTabClose: (id: string) => void;
}

export const ApplicationDetail: FC<ApplicationDetailProps> = ({
  tabs,
  activeTabId,
  fontSize,
  onTabChange,
  onTabClose,
}) => {
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
      {/* 各タブの SecondaryCheckSession を並列マウント。切り替えは display で行う。 */}
      {tabs.map((tab) => (
        <SecondaryCheckSession
          key={tab.id}
          tab={tab}
          fontSize={fontSize}
          hidden={tab.id !== activeTabId}
        />
      ))}
    </div>
  );
};
