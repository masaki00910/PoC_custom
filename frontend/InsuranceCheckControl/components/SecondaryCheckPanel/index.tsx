import type { FC } from 'react';
import type { FinalDecision, ToolCallLogEntry } from '../../types/secondary-check';
import { DecisionHistory } from './DecisionHistory';
import { FinalDecisionBar } from './FinalDecisionBar';

interface SecondaryCheckPanelProps {
  toolCallLog: ToolCallLogEntry[];
  finalDecision: FinalDecision;
  decidedFields: number;
  totalFields: number;
}

export const SecondaryCheckPanel: FC<SecondaryCheckPanelProps> = ({
  toolCallLog,
  finalDecision,
  decidedFields,
  totalFields,
}) => (
  <div
    style={{
      display: 'flex',
      flexDirection: 'column',
      background: '#fff',
      borderLeft: '1px solid var(--border)',
      minWidth: 0,
      height: '100%',
    }}
  >
    <div
      style={{
        padding: '12px 14px',
        borderBottom: '1px solid var(--border)',
        background: 'var(--navy-50)',
        flexShrink: 0,
      }}
    >
      <div style={{ fontSize: 13, fontWeight: 700, color: 'var(--navy-900)' }}>判断履歴</div>
      <div style={{ fontSize: 11, color: 'var(--gray)', marginTop: 2 }}>
        チャット経由で記録された判断が時系列で表示されます
      </div>
    </div>
    <div style={{ flex: 1, overflowY: 'auto' }}>
      <DecisionHistory entries={toolCallLog} />
    </div>
    <FinalDecisionBar
      decision={finalDecision}
      decidedFields={decidedFields}
      totalFields={totalFields}
    />
  </div>
);
