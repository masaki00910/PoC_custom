import { useState, type FC } from 'react';
import type { User, UserRole, Status } from '../../types/domain';
import { STATUSES } from '../../types/domain';
import { STATUS_STYLE } from '../../utils/constants';
import { SAMPLE_DATA, SAMPLE_USERS } from '../../services/mock-data';
import { StatCard } from '../common/StatCard';

interface AdminDashboardProps {
  fontSize: number;
}

export const AdminDashboard: FC<AdminDashboardProps> = ({ fontSize }) => {
  const [users, setUsers] = useState<User[]>([...SAMPLE_USERS]);
  const [editId, setEditId] = useState<string | null>(null);
  const [editRole, setEditRole] = useState<UserRole>('user');

  const statCounts = STATUSES.reduce<Record<Status, number>>(
    (a, s) => {
      a[s] = SAMPLE_DATA.filter((r) => r.status === s).length;
      return a;
    },
    { 未処理: 0, 処理中: 0, 完了: 0, エラー: 0, 保留: 0 },
  );

  const headers = ['ユーザーID', '氏名', '部署', '権限', '最終ログイン', '操作'] as const;

  return (
    <div style={{ flex: 1, overflowY: 'auto', padding: '24px 28px', fontSize }}>
      <div style={{ marginBottom: 20 }}>
        <h1 style={{ fontSize: 20, fontWeight: 700, color: 'var(--navy-900)' }}>
          管理者ダッシュボード
        </h1>
        <p style={{ fontSize: 13, color: 'var(--gray)', marginTop: 3 }}>
          システム全体の状況とユーザー管理
        </p>
      </div>

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit,minmax(130px,1fr))',
          gap: 12,
          marginBottom: 28,
        }}
      >
        <StatCard label="総件数" value={SAMPLE_DATA.length} color="var(--accent)" />
        {STATUSES.map((s) => (
          <StatCard key={s} label={s} value={statCounts[s]} color={STATUS_STYLE[s].dot} />
        ))}
      </div>

      <div
        style={{
          background: '#fff',
          borderRadius: 10,
          boxShadow: 'var(--shadow-sm)',
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            padding: '14px 18px',
            borderBottom: '1px solid var(--border)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <div style={{ fontWeight: 700, fontSize: 14, color: 'var(--navy-900)' }}>ユーザー管理</div>
          <span style={{ fontSize: 12, color: 'var(--gray)' }}>{users.length}名</span>
        </div>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize }}>
          <thead>
            <tr style={{ background: 'var(--navy-50)', borderBottom: '1px solid var(--border)' }}>
              {headers.map((h) => (
                <th
                  key={h}
                  style={{
                    padding: '10px 16px',
                    textAlign: 'left',
                    fontSize: 12,
                    fontWeight: 700,
                    color: 'var(--navy-700)',
                    whiteSpace: 'nowrap',
                  }}
                >
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {users.map((u, i) => (
              <tr
                key={u.id}
                style={{
                  borderBottom: '1px solid var(--border)',
                  background: i % 2 === 0 ? '#fff' : 'var(--navy-50)',
                }}
              >
                <td
                  style={{
                    padding: '10px 16px',
                    fontFamily: 'monospace',
                    fontSize: 12,
                    color: 'var(--gray)',
                  }}
                >
                  {u.id}
                </td>
                <td style={{ padding: '10px 16px', fontWeight: 600, color: 'var(--navy-900)' }}>
                  {u.name}
                </td>
                <td style={{ padding: '10px 16px', fontSize: 12, color: 'var(--gray)' }}>
                  {u.dept}
                </td>
                <td style={{ padding: '10px 16px' }}>
                  {editId === u.id ? (
                    <select
                      value={editRole}
                      onChange={(e) => setEditRole(e.target.value as UserRole)}
                      style={{
                        padding: '4px 8px',
                        border: '1px solid var(--border)',
                        borderRadius: 5,
                        fontSize: 12,
                        background: '#fff',
                      }}
                    >
                      <option value="user">一般</option>
                      <option value="admin">管理者</option>
                    </select>
                  ) : (
                    <span
                      style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: 5,
                        padding: '2px 8px',
                        borderRadius: 20,
                        fontSize: 12,
                        fontWeight: 600,
                        background: u.role === 'admin' ? 'var(--accent-lt)' : 'var(--gray-lt)',
                        color: u.role === 'admin' ? 'var(--accent)' : 'var(--gray)',
                      }}
                    >
                      {u.role === 'admin' ? '管理者' : '一般'}
                    </span>
                  )}
                </td>
                <td style={{ padding: '10px 16px', fontSize: 12, color: 'var(--gray)' }}>
                  {u.lastLogin}
                </td>
                <td style={{ padding: '10px 16px' }}>
                  {editId === u.id ? (
                    <div style={{ display: 'flex', gap: 6 }}>
                      <button
                        onClick={() => {
                          setUsers((us) => us.map((x) => (x.id === u.id ? { ...x, role: editRole } : x)));
                          setEditId(null);
                        }}
                        style={{
                          padding: '4px 10px',
                          background: 'var(--accent)',
                          color: '#fff',
                          border: 'none',
                          borderRadius: 5,
                          fontSize: 12,
                          cursor: 'pointer',
                        }}
                      >
                        保存
                      </button>
                      <button
                        onClick={() => setEditId(null)}
                        style={{
                          padding: '4px 10px',
                          background: 'var(--gray-lt)',
                          border: '1px solid var(--border)',
                          color: 'var(--gray)',
                          borderRadius: 5,
                          fontSize: 12,
                          cursor: 'pointer',
                        }}
                      >
                        キャンセル
                      </button>
                    </div>
                  ) : (
                    <button
                      onClick={() => {
                        setEditId(u.id);
                        setEditRole(u.role);
                      }}
                      style={{
                        padding: '4px 10px',
                        background: 'var(--gray-lt)',
                        border: '1px solid var(--border)',
                        color: 'var(--navy-800)',
                        borderRadius: 5,
                        fontSize: 12,
                        cursor: 'pointer',
                      }}
                    >
                      編集
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
