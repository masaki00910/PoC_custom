import type { FC } from 'react';
import type { FinalDecision } from '../../types/secondary-check';

interface FinalDecisionBarProps {
  decision: FinalDecision;
  decidedFields: number;
  totalFields: number;
}

const statusStyle = (status: FinalDecision['status']): { bg: string; fg: string; label: string } => {
  switch (status) {
    case 'approved':
      return { bg: 'var(--green-lt)', fg: 'var(--green)', label: '承認済み' };
    case 'rejected':
      return { bg: 'var(--red-lt)', fg: 'var(--red)', label: '差し戻し' };
    case 'pending':
      return { bg: 'var(--gray-lt)', fg: 'var(--gray)', label: '未確定' };
  }
};

export const FinalDecisionBar: FC<FinalDecisionBarProps> = ({
  decision,
  decidedFields,
  totalFields,
}) => {
  const s = statusStyle(decision.status);
  return (
    <div
      style={{
        borderTop: '1px solid var(--border)',
        background: 'var(--navy-50)',
        padding: '12px 14px',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
        <span
          style={{
            fontSize: 11,
            fontWeight: 700,
            padding: '3px 10px',
            borderRadius: 20,
            background: s.bg,
            color: s.fg,
          }}
        >
          {s.label}
        </span>
        <span style={{ fontSize: 12, color: 'var(--navy-700)', fontWeight: 600 }}>最終判定</span>
      </div>
      <div style={{ fontSize: 11, color: 'var(--gray)' }}>
        判断済み: {decidedFields} / {totalFields} 項目
      </div>
      {decision.note && (
        <div style={{ fontSize: 11, color: 'var(--navy-700)', marginTop: 4 }}>
          ステータス: {decision.note}
        </div>
      )}
    </div>
  );
};
