import type { Status } from '../types/domain';

export interface StatusStyle {
  bg: string;
  color: string;
  dot: string;
}

export const STATUS_STYLE: Record<Status, StatusStyle> = {
  未処理: { bg: 'var(--gray-lt)', color: 'var(--gray)', dot: '#9ca3af' },
  処理中: { bg: 'var(--accent-lt)', color: 'var(--accent)', dot: '#2563eb' },
  完了: { bg: 'var(--green-lt)', color: 'var(--green)', dot: '#16a34a' },
  エラー: { bg: 'var(--red-lt)', color: 'var(--red)', dot: '#dc2626' },
  保留: { bg: 'var(--yellow-lt)', color: 'var(--yellow)', dot: '#d97706' },
};
