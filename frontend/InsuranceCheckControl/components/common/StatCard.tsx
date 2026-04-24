import type { FC } from 'react';

interface StatCardProps {
  label: string;
  value: number;
  color: string;
}

export const StatCard: FC<StatCardProps> = ({ label, value, color }) => (
  <div
    style={{
      background: '#fff',
      borderRadius: 10,
      padding: '16px 18px',
      boxShadow: 'var(--shadow-sm)',
      borderLeft: `3px solid ${color}`,
    }}
  >
    <div style={{ fontSize: 22, fontWeight: 700, color }}>{value}</div>
    <div style={{ fontSize: 12, color: 'var(--gray)', marginTop: 4 }}>{label}</div>
  </div>
);
