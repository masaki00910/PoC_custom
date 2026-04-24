import type { FC, ReactNode } from 'react';
import type { PageId } from '../../types/domain';

interface NavItem {
  id: PageId;
  label: string;
  icon: ReactNode;
}

interface TopNavProps {
  userId: string;
  isAdmin: boolean;
  currentPage: PageId;
  onNavigate: (page: PageId) => void;
  onLogout: () => void;
}

export const TopNav: FC<TopNavProps> = ({ userId, isAdmin, currentPage, onNavigate, onLogout }) => {
  const navItems: NavItem[] = [
    {
      id: 'list',
      label: '担当一覧',
      icon: (
        <svg width="14" height="14" fill="none" viewBox="0 0 24 24">
          <path
            d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
            stroke="currentColor"
            strokeWidth="1.8"
            strokeLinecap="round"
          />
        </svg>
      ),
    },
    {
      id: 'chat',
      label: 'チャット',
      icon: (
        <svg width="14" height="14" fill="none" viewBox="0 0 24 24">
          <path
            d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
            stroke="currentColor"
            strokeWidth="1.8"
            strokeLinecap="round"
          />
        </svg>
      ),
    },
    ...(isAdmin
      ? [
          {
            id: 'admin' as const,
            label: '管理者',
            icon: (
              <svg width="14" height="14" fill="none" viewBox="0 0 24 24">
                <path
                  d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                  stroke="currentColor"
                  strokeWidth="1.8"
                  strokeLinecap="round"
                />
              </svg>
            ),
          },
        ]
      : []),
  ];

  return (
    <header
      style={{
        background: '#fff',
        borderBottom: '1px solid var(--border)',
        boxShadow: 'var(--shadow-sm)',
        flexShrink: 0,
      }}
    >
      <div
        style={{
          padding: '0 24px',
          height: 52,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          borderBottom: '1px solid var(--border)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div
            style={{
              width: 30,
              height: 30,
              background: 'var(--accent)',
              borderRadius: 7,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0,
            }}
          >
            <svg width="15" height="15" fill="none" viewBox="0 0 24 24">
              <path
                d="M9 12h6M9 16h6M7 8h10M5 4h14a1 1 0 011 1v14a1 1 0 01-1 1H5a1 1 0 01-1-1V5a1 1 0 011-1z"
                stroke="#fff"
                strokeWidth="2"
                strokeLinecap="round"
              />
            </svg>
          </div>
          <span style={{ fontWeight: 700, fontSize: 14, color: 'var(--navy-900)' }}>
            保険申込書エラー回復
          </span>
          {isAdmin && (
            <span
              style={{
                fontSize: 11,
                background: 'var(--accent-lt)',
                color: 'var(--accent)',
                padding: '2px 8px',
                borderRadius: 20,
                fontWeight: 600,
              }}
            >
              管理者
            </span>
          )}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
          <span style={{ fontSize: 13, color: 'var(--gray)' }}>
            <svg
              style={{ verticalAlign: -2, marginRight: 5 }}
              width="13"
              height="13"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle cx="12" cy="8" r="4" stroke="currentColor" strokeWidth="2" />
              <path
                d="M4 20c0-4 3.6-7 8-7s8 3 8 7"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
              />
            </svg>
            {userId}
          </span>
          <button
            onClick={onLogout}
            style={{
              background: 'var(--gray-lt)',
              border: '1px solid var(--border)',
              color: 'var(--navy-800)',
              borderRadius: 6,
              padding: '5px 12px',
              fontSize: 12,
              cursor: 'pointer',
            }}
          >
            ログアウト
          </button>
        </div>
      </div>
      <div
        style={{
          padding: '0 24px',
          display: 'flex',
          gap: 0,
          alignItems: 'flex-end',
          height: 40,
        }}
      >
        {navItems.map((item) => {
          const active = currentPage === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 6,
                padding: '0 18px',
                height: '100%',
                border: 'none',
                borderBottom: `2px solid ${active ? 'var(--accent)' : 'transparent'}`,
                background: 'none',
                color: active ? 'var(--accent)' : 'var(--gray)',
                fontWeight: active ? 600 : 400,
                fontSize: 13,
                cursor: 'pointer',
                transition: 'all .15s',
                whiteSpace: 'nowrap',
              }}
            >
              {item.icon}
              {item.label}
            </button>
          );
        })}
      </div>
    </header>
  );
};
