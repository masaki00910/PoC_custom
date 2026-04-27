import type { FC } from 'react';
import type { ViewerProps } from './types';

/**
 * 申込書スキャン画像のプレースホルダ。
 * 二次チェック画面の CheckResultView / secondary-check-mock と値を揃えている:
 *  - 契約者: 松本直樹 / ﾏﾂﾓﾄﾅｵｷ、〒 と 住所（カナ）は空欄（=記入漏れ＝一次チェックでエラー）
 *  - 被保険者: 木村さゆり / ｷﾑﾗｻﾕﾘ、〒=060-0001、住所（カナ）=ﾎｯｶｲﾄﾞｳｻｯﾎﾟﾛｼﾁｭｳｵｳｸｷﾀ2ｼﾞｮｳﾆｼ12-12-12
 */
interface FormField {
  x: number;
  y: number;
  w: number;
  label: string;
  value: string;
  blank?: boolean;
}

const sectionHeader = (y: number, title: string): { y: number; title: string } => ({ y, title });

export const ScanPlaceholder: FC<ViewerProps> = ({ scale, offset, secNo }) => {
  const headerFields: FormField[] = [
    { x: 60, y: 78, w: 200, label: '証券番号', value: secNo },
    { x: 280, y: 78, w: 200, label: '申込日', value: '2025年10月15日' },
    { x: 60, y: 108, w: 200, label: '保険種類', value: '定期保険' },
  ];

  const contractorSection = sectionHeader(140, '■ 契約者情報');
  const contractorFields: FormField[] = [
    { x: 60, y: 165, w: 280, label: '契約者氏名（漢字）', value: '松本　直樹' },
    { x: 60, y: 195, w: 280, label: '契約者氏名（カナ）', value: 'ﾏﾂﾓﾄﾅｵｷ' },
    { x: 60, y: 225, w: 120, label: '契約者住所（〒）', value: '', blank: true },
    { x: 60, y: 255, w: 495, label: '契約者住所（カナ）', value: '', blank: true },
  ];

  const insuredSection = sectionHeader(295, '■ 被保険者情報');
  const insuredFields: FormField[] = [
    { x: 60, y: 320, w: 280, label: '被保険者氏名（漢字）', value: '木村　さゆり' },
    { x: 60, y: 350, w: 280, label: '被保険者氏名（カナ）', value: 'ｷﾑﾗｻﾕﾘ' },
    { x: 60, y: 380, w: 200, label: '生年月日', value: '昭和58年4月12日' },
    { x: 280, y: 380, w: 80, label: '性別', value: '女' },
    { x: 60, y: 410, w: 120, label: '被保険者住所（〒）', value: '060-0001' },
    { x: 60, y: 440, w: 495, label: '被保険者住所（カナ）', value: 'ﾎｯｶｲﾄﾞｳｻｯﾎﾟﾛｼﾁｭｳｵｳｸｷﾀ2ｼﾞｮｳﾆｼ12-12-12' },
  ];

  const insuranceSection = sectionHeader(480, '■ 保険情報');
  const insuranceFields: FormField[] = [
    { x: 60, y: 505, w: 140, label: '保険金額', value: '2,000万円' },
    { x: 210, y: 505, w: 100, label: '保険期間', value: '20年' },
    { x: 320, y: 505, w: 140, label: '保険料', value: '¥12,500/月' },
  ];

  const sections = [contractorSection, insuredSection, insuranceSection];
  const allFields = [...headerFields, ...contractorFields, ...insuredFields, ...insuranceFields];

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

      {/* Section headers */}
      {sections.map((s) => (
        <g key={s.y}>
          <rect x="40" y={s.y - 12} width="515" height="16" fill="#e5e7eb" />
          <text
            x="48"
            y={s.y}
            fontFamily="sans-serif"
            fontSize="10"
            fill="#374151"
            fontWeight="bold"
          >
            {s.title}
          </text>
        </g>
      ))}

      {/* Fields */}
      {allFields.map((f) => (
        <g key={`${f.x}-${f.y}`}>
          <text x={f.x} y={f.y - 2} fontSize="8" fill="#6b7280" fontFamily="sans-serif">
            {f.label}
          </text>
          <rect
            x={f.x}
            y={f.y}
            width={f.w}
            height={16}
            fill={f.blank ? '#fdf6f6' : '#fff'}
            stroke={f.blank ? '#dc2626' : '#c0c8d8'}
            strokeWidth={f.blank ? '1' : '0.8'}
            strokeDasharray={f.blank ? '3,2' : undefined}
          />
          {f.blank ? (
            <text
              x={f.x + 6}
              y={f.y + 11}
              fontSize="9"
              fill="#dc2626"
              fontStyle="italic"
              fontFamily="sans-serif"
            >
              （未記入）
            </text>
          ) : (
            <text
              x={f.x + 6}
              y={f.y + 11}
              fontSize="10"
              fill="#1f2937"
              fontFamily="sans-serif"
            >
              {f.value}
            </text>
          )}
        </g>
      ))}

      {/* Signature area */}
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
