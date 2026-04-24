import type { CSSProperties, FC } from 'react';
import type { Status } from '../../types/domain';
import { STATUS_STYLE } from '../../utils/constants';

interface StatusBadgeProps {
  status: Status;
}

export const StatusBadge: FC<StatusBadgeProps> = ({ status }) => {
  const s = STATUS_STYLE[status];
  const wrap: CSSProperties = {
    display: 'inline-flex',
    alignItems: 'center',
    gap: 5,
    padding: '3px 10px',
    borderRadius: 20,
    background: s.bg,
    color: s.color,
    fontSize: 12,
    fontWeight: 600,
  };
  const dot: CSSProperties = {
    width: 6,
    height: 6,
    borderRadius: '50%',
    background: s.dot,
    display: 'inline-block',
  };
  return (
    <span style={wrap}>
      <span style={dot} />
      {status}
    </span>
  );
};
