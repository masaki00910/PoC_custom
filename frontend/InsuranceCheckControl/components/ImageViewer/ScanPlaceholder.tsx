import type { FC } from 'react';
import type { ViewerProps } from './types';

export const ScanPlaceholder: FC<ViewerProps> = ({ scale, offset, secNo }) => {
  const fields: Array<[number, number, number, string, string]> = [
    [60, 78, 180, '証券番号', secNo],
    [60, 106, 180, '申込日', '2025年10月15日'],
    [60, 134, 180, '保険種類', '定期保険'],
    [60, 162, 280, '被保険者氏名', '山田　太郎'],
    [60, 190, 200, '生年月日', '昭和58年4月12日'],
    [60, 218, 80, '性別', '男'],
    [60, 246, 280, '住所', '東京都新宿区西新宿1-1-1'],
    [60, 290, 120, '保険金額', '2,000万円'],
    [60, 318, 120, '保険期間', '20年'],
    [60, 346, 120, '保険料', '¥12,500/月'],
  ];

  return (
    <svg
      viewBox="0 0 595 842"
      xmlns="http://www.w3.org/2000/svg"
      style={{
        width: 595 * scale,
        height: 842 * scale,
        transform: `translate(${offset.x}px,${offset.y}px)`,
        transformOrigin: 'top left',
        display: 'block',
        flexShrink: 0,
      }}
    >
      <rect width="595" height="842" fill="#f9f8f6" />
      {Array.from({ length: 52 }, (_, i) => (
        <line
          key={i}
          x1="40"
          y1={60 + i * 14}
          x2="555"
          y2={60 + i * 14}
          stroke="#e2e0db"
          strokeWidth="0.8"
        />
      ))}
      <rect x="40" y="30" width="515" height="2" fill="#374151" />
      <rect x="40" y="34" width="515" height="1" fill="#c0c8d8" />
      <text
        x="297"
        y="24"
        textAnchor="middle"
        fontFamily="serif"
        fontSize="14"
        fill="#374151"
        fontWeight="bold"
      >
        生命保険申込書　控
      </text>
      <rect
        x="480"
        y="40"
        width="60"
        height="60"
        rx="4"
        fill="none"
        stroke="#dc2626"
        strokeWidth="1.5"
        strokeDasharray="4,2"
      />
      <text x="510" y="66" textAnchor="middle" fontFamily="serif" fontSize="9" fill="#dc2626">
        受付
      </text>
      <text x="510" y="80" textAnchor="middle" fontFamily="serif" fontSize="9" fill="#dc2626">
        印
      </text>
      {fields.map(([x, y, w, label, val]) => (
        <g key={y}>
          <text x={x} y={y - 2} fontSize="8" fill="#6b7280" fontFamily="sans-serif">
            {label}
          </text>
          <rect x={x} y={y} width={w} height={16} fill="#fff" stroke="#c0c8d8" strokeWidth="0.8" />
          <text x={x + 6} y={y + 11} fontSize="10" fill="#1f2937" fontFamily="sans-serif">
            {val}
          </text>
        </g>
      ))}
      <rect x="40" y="720" width="240" height="60" fill="none" stroke="#c0c8d8" strokeWidth="0.8" />
      <text x="160" y="744" textAnchor="middle" fontSize="9" fill="#9ca3af" fontFamily="sans-serif">
        申込人署名
      </text>
      <rect x="320" y="720" width="235" height="60" fill="none" stroke="#c0c8d8" strokeWidth="0.8" />
      <text x="437" y="744" textAnchor="middle" fontSize="9" fill="#9ca3af" fontFamily="sans-serif">
        代理店印
      </text>
      <rect x="40" y="810" width="515" height="2" fill="#374151" />
    </svg>
  );
};
