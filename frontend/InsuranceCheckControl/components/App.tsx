import { useEffect, useState, type FC } from 'react';
import type { ApplicationRow, ChatTab, PageId } from '../types/domain';
import { useAuth } from '../hooks/useAuth';
import { AdminDashboard } from './AdminDashboard/AdminDashboard';
import { ApplicationDetail } from './ApplicationDetail/ApplicationDetail';
import { ApplicationList } from './ApplicationList/ApplicationList';
import { LoginPage } from './LoginPage/LoginPage';
import { TopNav } from './common/TopNav';

interface TweakMessage {
  type?: string;
}

export const App: FC = () => {
  const { session, isAdmin, loggingIn, error, login, logout } = useAuth();
  const [page, setPage] = useState<PageId>('list');
  const [tabs, setTabs] = useState<ChatTab[]>([]);
  const [activeTabId, setActiveTabId] = useState<string | null>(null);
  const [rowHeight, setRowHeight] = useState(44);
  const [fontSize, setFontSize] = useState(13);

  const handleLogout = (): void => {
    logout();
    setTabs([]);
    setActiveTabId(null);
    setPage('list');
  };

  const navigate = (p: PageId): void => {
    if (p === 'admin' && !isAdmin) return;
    setPage(p);
  };

  const openChat = (row: ApplicationRow): void => {
    setTabs((t) => (t.find((x) => x.id === row.secNo) ? t : [...t, { ...row, id: row.secNo }]));
    setActiveTabId(row.secNo);
    setPage('chat');
  };

  const closeTab = (id: string): void => {
    setTabs((t) => {
      const next = t.filter((x) => x.id !== id);
      if (activeTabId === id) {
        const last = next[next.length - 1];
        setActiveTabId(last ? last.id : null);
      }
      return next;
    });
  };

  useEffect(() => {
    const panel = document.getElementById('tweaks-panel');
    const rowEl = document.getElementById('tw-row-height') as HTMLInputElement | null;
    const fontEl = document.getElementById('tw-font-size') as HTMLInputElement | null;
    if (!panel) return;

    const onRow = (e: Event): void => {
      const target = e.target as HTMLInputElement;
      setRowHeight(Number(target.value));
    };
    const onFont = (e: Event): void => {
      const target = e.target as HTMLInputElement;
      setFontSize(Number(target.value));
    };
    const onMsg = (e: MessageEvent<TweakMessage>): void => {
      if (e.data?.type === '__activate_edit_mode') panel.classList.add('visible');
      if (e.data?.type === '__deactivate_edit_mode') panel.classList.remove('visible');
    };

    rowEl?.addEventListener('input', onRow);
    fontEl?.addEventListener('input', onFont);
    window.addEventListener('message', onMsg);
    window.parent.postMessage({ type: '__edit_mode_available' }, '*');

    return () => {
      rowEl?.removeEventListener('input', onRow);
      fontEl?.removeEventListener('input', onFont);
      window.removeEventListener('message', onMsg);
    };
  }, []);

  if (!session) {
    return <LoginPage onLogin={login} loggingIn={loggingIn} error={error} />;
  }

  return (
    <div
      style={{
        height: '100vh',
        display: 'flex',
        flexDirection: 'column',
        fontSize,
        overflow: 'hidden',
      }}
    >
      <TopNav
        userId={session.userId}
        isAdmin={isAdmin}
        currentPage={page}
        onNavigate={navigate}
        onLogout={handleLogout}
      />
      <div
        style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          minHeight: 0,
          overflow: 'hidden',
        }}
      >
        {page === 'list' && (
          <ApplicationList
            onOpenChat={openChat}
            rowHeight={rowHeight}
            fontSize={fontSize}
            userId={session.userId}
            isAdmin={isAdmin}
          />
        )}
        {page === 'chat' && (
          <ApplicationDetail
            tabs={tabs}
            activeTabId={activeTabId}
            onTabChange={setActiveTabId}
            onTabClose={closeTab}
            fontSize={fontSize}
          />
        )}
        {page === 'admin' && isAdmin && <AdminDashboard fontSize={fontSize} />}
        {page === 'admin' && !isAdmin && (
          <div
            style={{
              flex: 1,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--red)',
              fontSize: 14,
            }}
          >
            管理者権限がありません
          </div>
        )}
      </div>
    </div>
  );
};
