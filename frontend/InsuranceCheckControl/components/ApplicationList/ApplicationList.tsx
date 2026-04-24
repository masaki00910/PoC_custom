import { useMemo, useState, type CSSProperties, type FC } from 'react';
import type { ApplicationRow, Status } from '../../types/domain';
import { STATUSES } from '../../types/domain';
import { STATUS_STYLE } from '../../utils/constants';
import { pad } from '../../utils/formatters';
import { SAMPLE_DATA } from '../../services/mock-data';
import { StatusBadge } from '../common/StatusBadge';

interface ApplicationListProps {
  userId: string;
  isAdmin: boolean;
  rowHeight: number;
  fontSize: number;
  onOpenChat: (row: ApplicationRow) => void;
}

type SortKey = keyof Pick<ApplicationRow, 'no' | 'secNo' | 'status' | 'importDate' | 'assignee'>;
interface SortState {
  key: SortKey;
  dir: 'asc' | 'desc';
}

const PER_PAGE = 20;

const pgBtn = (disabled: boolean, active = false): CSSProperties => ({
  width: 30,
  height: 30,
  border: '1.5px solid var(--border)',
  borderRadius: 6,
  background: active ? 'var(--accent)' : '#fff',
  color: active ? '#fff' : disabled ? '#d1d5db' : 'var(--navy-800)',
  fontSize: 13,
  fontWeight: 500,
  cursor: disabled ? 'default' : 'pointer',
});

export const ApplicationList: FC<ApplicationListProps> = ({
  userId,
  isAdmin,
  rowHeight,
  fontSize,
  onOpenChat,
}) => {
  const [search, setSearch] = useState('');
  const [filterStatus, setFilterStatus] = useState<Status | ''>('');
  const [page, setPage] = useState(1);
  const [sort, setSort] = useState<SortState>({ key: 'no', dir: 'asc' });

  const myData = useMemo(
    () => (isAdmin ? SAMPLE_DATA : SAMPLE_DATA.filter((r) => r.assignee === userId)),
    [isAdmin, userId],
  );

  const filtered = useMemo(() => {
    const q = search.toLowerCase();
    return [...myData]
      .filter(
        (r) =>
          (!q ||
            r.secNo.toLowerCase().includes(q) ||
            r.status.includes(q) ||
            r.importDate.includes(q)) &&
          (!filterStatus || r.status === filterStatus),
      )
      .sort((a, b) => {
        const va = a[sort.key];
        const vb = b[sort.key];
        if (typeof va === 'string' && typeof vb === 'string') {
          return sort.dir === 'asc' ? va.localeCompare(vb, 'ja') : vb.localeCompare(va, 'ja');
        }
        if (typeof va === 'number' && typeof vb === 'number') {
          return sort.dir === 'asc' ? va - vb : vb - va;
        }
        return 0;
      });
  }, [myData, search, filterStatus, sort]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / PER_PAGE));
  const paged = filtered.slice((page - 1) * PER_PAGE, page * PER_PAGE);

  const toggleSort = (key: SortKey): void => {
    setSort((s) => (s.key === key ? { ...s, dir: s.dir === 'asc' ? 'desc' : 'asc' } : { key, dir: 'asc' }));
    setPage(1);
  };

  const SortIcon: FC<{ k: SortKey }> = ({ k }) =>
    sort.key !== k ? (
      <span style={{ opacity: 0.3, marginLeft: 4 }}>↕</span>
    ) : (
      <span style={{ marginLeft: 4, color: 'var(--accent)' }}>{sort.dir === 'asc' ? '↑' : '↓'}</span>
    );

  const statusCounts = STATUSES.reduce<Record<Status, number>>(
    (acc, s) => {
      acc[s] = myData.filter((r) => r.status === s).length;
      return acc;
    },
    { 未処理: 0, 処理中: 0, 完了: 0, エラー: 0, 保留: 0 },
  );

  const columns: Array<[SortKey, string]> = [
    ['no', 'No.'],
    ['secNo', '証券番号'],
    ['status', 'ステータス'],
    ['importDate', '取込日'],
    ...(isAdmin ? ([['assignee', '担当者']] as Array<[SortKey, string]>) : []),
  ];

  return (
    <div style={{ flex: 1, overflowY: 'auto', padding: '24px 28px', fontSize }}>
      <div style={{ marginBottom: 20 }}>
        <h1 style={{ fontSize: 20, fontWeight: 700, color: 'var(--navy-900)' }}>担当一覧</h1>
        <p style={{ fontSize: 13, color: 'var(--gray)', marginTop: 3 }}>
          {isAdmin
            ? `全担当者の案件を表示中（${SAMPLE_DATA.length}件）`
            : `${userId} さんに割り当てられた案件を表示中`}
        </p>
      </div>
      <div style={{ display: 'flex', gap: 10, marginBottom: 20, flexWrap: 'wrap' }}>
        {STATUSES.map((s) => {
          const st = STATUS_STYLE[s];
          const selected = filterStatus === s;
          return (
            <button
              key={s}
              onClick={() => {
                setFilterStatus(selected ? '' : s);
                setPage(1);
              }}
              style={{
                padding: '10px 16px',
                borderRadius: 8,
                border: `1.5px solid ${selected ? st.dot : 'var(--border)'}`,
                background: selected ? st.bg : '#fff',
                cursor: 'pointer',
                textAlign: 'left',
                transition: 'all .15s',
                boxShadow: selected ? `0 0 0 2px ${st.dot}30` : 'var(--shadow-sm)',
              }}
            >
              <div style={{ fontSize: 18, fontWeight: 700, color: st.color }}>{statusCounts[s]}</div>
              <div style={{ fontSize: 11, color: 'var(--gray)', marginTop: 2 }}>{s}</div>
            </button>
          );
        })}
      </div>
      <div
        style={{
          background: '#fff',
          borderRadius: 10,
          padding: '12px 16px',
          marginBottom: 16,
          boxShadow: 'var(--shadow-sm)',
          display: 'flex',
          gap: 10,
          alignItems: 'center',
          flexWrap: 'wrap',
        }}
      >
        <div style={{ position: 'relative', flex: '1 1 200px' }}>
          <svg
            style={{ position: 'absolute', left: 10, top: '50%', transform: 'translateY(-50%)', opacity: 0.4 }}
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
          >
            <circle cx="11" cy="11" r="7" stroke="#374151" strokeWidth="2" />
            <path d="M16.5 16.5l4 4" stroke="#374151" strokeWidth="2" strokeLinecap="round" />
          </svg>
          <input
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
            placeholder="証券番号・ステータスで検索..."
            style={{
              width: '100%',
              padding: '8px 12px 8px 32px',
              border: '1.5px solid var(--border)',
              borderRadius: 7,
              fontSize: 13,
              outline: 'none',
            }}
            onFocus={(e) => (e.target.style.borderColor = 'var(--accent)')}
            onBlur={(e) => (e.target.style.borderColor = 'var(--border)')}
          />
        </div>
        <select
          value={filterStatus}
          onChange={(e) => {
            setFilterStatus(e.target.value as Status | '');
            setPage(1);
          }}
          style={{
            padding: '8px 12px',
            border: '1.5px solid var(--border)',
            borderRadius: 7,
            fontSize: 13,
            background: '#fff',
            color: 'var(--navy-800)',
            outline: 'none',
            minWidth: 120,
          }}
        >
          <option value="">全ステータス</option>
          {STATUSES.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
        <span style={{ fontSize: 13, color: 'var(--gray)', whiteSpace: 'nowrap' }}>
          {filtered.length}件
        </span>
      </div>
      <div
        style={{
          background: '#fff',
          borderRadius: 10,
          boxShadow: 'var(--shadow-sm)',
          overflow: 'hidden',
        }}
      >
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize }}>
          <thead>
            <tr style={{ background: 'var(--navy-50)', borderBottom: '2px solid var(--border)' }}>
              {columns.map(([k, label]) => (
                <th
                  key={k}
                  onClick={() => toggleSort(k)}
                  style={{
                    padding: '11px 18px',
                    textAlign: 'left',
                    fontSize: 12,
                    fontWeight: 700,
                    color: 'var(--navy-700)',
                    cursor: 'pointer',
                    userSelect: 'none',
                    whiteSpace: 'nowrap',
                  }}
                >
                  {label}
                  <SortIcon k={k} />
                </th>
              ))}
              <th
                style={{
                  padding: '11px 18px',
                  textAlign: 'center',
                  fontSize: 12,
                  fontWeight: 700,
                  color: 'var(--navy-700)',
                }}
              >
                操作
              </th>
            </tr>
          </thead>
          <tbody>
            {paged.map((row, i) => {
              const padY = rowHeight / 2 - 8;
              return (
                <tr
                  key={row.no}
                  style={{
                    borderBottom: '1px solid var(--border)',
                    background: i % 2 === 0 ? '#fff' : 'var(--navy-50)',
                    transition: 'background .1s',
                  }}
                  onMouseEnter={(e) => (e.currentTarget.style.background = 'var(--accent-lt)')}
                  onMouseLeave={(e) =>
                    (e.currentTarget.style.background = i % 2 === 0 ? '#fff' : 'var(--navy-50)')
                  }
                >
                  <td style={{ padding: `${padY}px 18px`, color: 'var(--gray)', fontSize: 12 }}>
                    {pad(row.no, 3)}
                  </td>
                  <td
                    style={{
                      padding: `${padY}px 18px`,
                      fontWeight: 600,
                      color: 'var(--navy-900)',
                      fontFamily: 'monospace',
                      fontSize: 13,
                    }}
                  >
                    {row.secNo}
                  </td>
                  <td style={{ padding: `${padY}px 18px` }}>
                    <StatusBadge status={row.status} />
                  </td>
                  <td style={{ padding: `${padY}px 18px`, color: 'var(--gray)', fontSize: 12 }}>
                    {row.importDate}
                  </td>
                  {isAdmin && (
                    <td style={{ padding: `${padY}px 18px`, fontSize: 12, color: 'var(--navy-700)' }}>
                      {row.assignee}
                    </td>
                  )}
                  <td style={{ padding: `${padY}px 18px`, textAlign: 'center' }}>
                    <button
                      onClick={() => onOpenChat(row)}
                      style={{
                        padding: '5px 14px',
                        background: 'var(--accent)',
                        color: '#fff',
                        border: 'none',
                        borderRadius: 6,
                        fontSize: 12,
                        fontWeight: 600,
                        cursor: 'pointer',
                        transition: 'opacity .15s',
                      }}
                      onMouseEnter={(e) => (e.currentTarget.style.opacity = '.85')}
                      onMouseLeave={(e) => (e.currentTarget.style.opacity = '1')}
                    >
                      チャットを開く
                    </button>
                  </td>
                </tr>
              );
            })}
            {paged.length === 0 && (
              <tr>
                <td
                  colSpan={columns.length + 1}
                  style={{ padding: 40, textAlign: 'center', color: 'var(--gray)', fontSize: 14 }}
                >
                  該当するデータがありません
                </td>
              </tr>
            )}
          </tbody>
        </table>
        {totalPages > 1 && (
          <div
            style={{
              padding: '12px 18px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              borderTop: '1px solid var(--border)',
              background: 'var(--navy-50)',
            }}
          >
            <span style={{ fontSize: 12, color: 'var(--gray)' }}>
              {(page - 1) * PER_PAGE + 1}〜{Math.min(page * PER_PAGE, filtered.length)} /{' '}
              {filtered.length}件
            </span>
            <div style={{ display: 'flex', gap: 4 }}>
              <button onClick={() => setPage(1)} disabled={page === 1} style={pgBtn(page === 1)}>
                «
              </button>
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                style={pgBtn(page === 1)}
              >
                ‹
              </button>
              {Array.from({ length: totalPages }, (_, i) => i + 1)
                .filter((p) => Math.abs(p - page) <= 2)
                .map((p) => (
                  <button key={p} onClick={() => setPage(p)} style={pgBtn(false, p === page)}>
                    {p}
                  </button>
                ))}
              <button
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                style={pgBtn(page === totalPages)}
              >
                ›
              </button>
              <button
                onClick={() => setPage(totalPages)}
                disabled={page === totalPages}
                style={pgBtn(page === totalPages)}
              >
                »
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
