import type { FC } from 'react';
import type { ToolCallLogEntry } from '../../types/secondary-check';

interface DecisionHistoryProps {
  entries: ToolCallLogEntry[];
}

const formatTime = (iso: string): string => {
  const d = new Date(iso);
  const hh = String(d.getHours()).padStart(2, '0');
  const mm = String(d.getMinutes()).padStart(2, '0');
  const ss = String(d.getSeconds()).padStart(2, '0');
  return `${hh}:${mm}:${ss}`;
};

const badgeStyle = (name: ToolCallLogEntry['call']['name']): { bg: string; fg: string; label: string } => {
  switch (name) {
    case 'update_recovery_value':
      return { bg: 'var(--accent-lt)', fg: 'var(--accent)', label: '値更新' };
    case 'file_inquiry':
      return { bg: 'var(--yellow-lt)', fg: 'var(--yellow)', label: '問い合わせ' };
    case 'finalize_check':
      return { bg: 'var(--green-lt)', fg: 'var(--green)', label: '最終判定' };
  }
};

export const DecisionHistory: FC<DecisionHistoryProps> = ({ entries }) => {
  if (entries.length === 0) {
    return (
      <div
        style={{
          padding: 24,
          textAlign: 'center',
          color: 'var(--gray)',
          fontSize: 12,
          lineHeight: 1.6,
        }}
      >
        まだ判断が記録されていません。
        <br />
        チャットで判断を進めると、ここに履歴が表示されます。
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 10, padding: 12 }}>
      {entries.map((entry) => {
        const badge = badgeStyle(entry.call.name);
        return (
          <div
            key={entry.id}
            style={{
              background: '#fff',
              border: '1px solid var(--border)',
              borderRadius: 8,
              padding: '10px 12px',
              boxShadow: 'var(--shadow-sm)',
            }}
          >
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 8,
                marginBottom: 6,
              }}
            >
              <span
                style={{
                  fontSize: 10,
                  fontWeight: 700,
                  padding: '2px 8px',
                  borderRadius: 10,
                  background: badge.bg,
                  color: badge.fg,
                }}
              >
                {badge.label}
              </span>
              <span style={{ fontSize: 11, color: 'var(--gray)', fontFamily: 'monospace' }}>
                {formatTime(entry.timestamp)}
              </span>
            </div>
            <div style={{ fontSize: 12, color: 'var(--navy-900)', lineHeight: 1.5 }}>
              {entry.call.name === 'update_recovery_value' && (
                <>
                  <div style={{ fontWeight: 600 }}>{entry.call.input.fieldName}</div>
                  <div style={{ fontFamily: 'monospace', color: 'var(--accent)', marginTop: 2 }}>
                    {entry.call.input.value}
                  </div>
                  <div style={{ fontSize: 11, color: 'var(--gray)', marginTop: 4 }}>
                    {entry.call.input.reason}
                  </div>
                </>
              )}
              {entry.call.name === 'file_inquiry' && (
                <>
                  <div style={{ fontWeight: 600 }}>{entry.call.input.category}</div>
                  <div style={{ fontSize: 11, color: 'var(--navy-700)', marginTop: 4 }}>
                    {entry.call.input.contents}
                  </div>
                </>
              )}
              {entry.call.name === 'finalize_check' && (
                <>
                  <div style={{ fontWeight: 600 }}>
                    {entry.call.input.checkResult ? '承認' : '差し戻し'}
                  </div>
                  <div style={{ fontSize: 11, color: 'var(--gray)', marginTop: 4 }}>
                    status: {entry.call.input.status}
                  </div>
                </>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
};
