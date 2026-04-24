import type { FC } from 'react';
import type { ViewerProps } from './types';

type HolderField = [label: string, value: string, highlight: boolean];
type SummaryField = [label: string, value: string];
type HistoryRow = [date: string, before: string, after: string];

export const ContractPlaceholder: FC<ViewerProps> = ({ scale, offset, secNo }) => {
  const prevSecNo = 'P' + secNo.replace(/^./, '');

  const holderFields: HolderField[] = [
    ['契約者名（漢字）', '松本　直樹', false],
    ['契約者名（カナ）', 'ﾏﾂﾓﾄﾅｵｷ', true],
    ['生年月日', '昭和58年04月12日', false],
    ['契約者住所（〒）', '060-0001', true],
    ['契約者住所（漢字）', '北海道札幌市中央区北1条西11-11-11', false],
    ['契約者住所（カナ）', 'ﾎｯｶｲﾄﾞｳｻｯﾎﾟﾛｼﾁｭｳｵｳｸｷﾀ1ｼﾞｮｳﾆｼ11-11-11', true],
    ['電話番号', '011-221-xxxx', false],
  ];

  const summary: SummaryField[] = [
    ['既契約証券番号', prevSecNo],
    ['契約日', '2018年07月01日'],
    ['保険種類', '終身保険（低解約返戻金型）'],
    ['保険金額', '3,000万円'],
    ['保険料', '¥18,240 / 月'],
    ['契約状態', '有効'],
    ['最終変更日', '2023年04月15日（住所変更）'],
  ];

  const history: HistoryRow[] = [
    ['2023/04/15', '東京都新宿区西新宿2-8-1', '北海道札幌市中央区北1条西11-11-11'],
    ['2018/07/01', '（新規契約）', '東京都新宿区西新宿2-8-1'],
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
      <rect width="595" height="842" fill="#fff" />
      <rect x="0" y="0" width="595" height="58" fill="#1e3a5f" />
      <text x="30" y="28" fontFamily="sans-serif" fontSize="13" fill="#fff" fontWeight="bold">
        既契約照会システム　- 契約情報詳細
      </text>
      <text x="30" y="46" fontFamily="sans-serif" fontSize="10" fill="#a8c5e8">
        Legacy Contract Reference
      </text>
      <rect x="460" y="16" width="110" height="26" rx="4" fill="#2563eb" />
      <text x="515" y="33" textAnchor="middle" fontFamily="monospace" fontSize="10" fill="#fff">
        照会結果: ヒット
      </text>

      <rect x="20" y="78" width="555" height="46" rx="6" fill="#dbeafe" stroke="#2563eb" strokeWidth="1" />
      <text x="34" y="98" fontFamily="sans-serif" fontSize="10" fill="#1e40af" fontWeight="bold">
        ● マッチング根拠
      </text>
      <text x="34" y="115" fontFamily="sans-serif" fontSize="10" fill="#1e3a5f">
        契約者名（カナ）一致: ﾏﾂﾓﾄﾅｵｷ　／　生年月日一致: S58.04.12　／　既契約証券番号: {prevSecNo}
      </text>

      <rect x="20" y="144" width="555" height="22" fill="#1e3a5f" />
      <text x="30" y="160" fontFamily="sans-serif" fontSize="11" fill="#fff" fontWeight="bold">
        ■ 契約者情報（既契約）
      </text>

      {holderFields.map(([label, val, hl], i) => (
        <g key={i}>
          <rect
            x="20"
            y={172 + i * 26}
            width="555"
            height="26"
            fill={i % 2 === 0 ? '#f8fafc' : '#fff'}
            stroke="#e2e8f0"
            strokeWidth="0.5"
          />
          {hl && <rect x="20" y={172 + i * 26} width="555" height="26" fill="#fef3c7" opacity="0.7" />}
          <text x="32" y={189 + i * 26} fontFamily="sans-serif" fontSize="10" fill="#64748b" fontWeight="bold">
            {label}
          </text>
          <text x="220" y={189 + i * 26} fontFamily="monospace" fontSize="10" fill="#0f172a">
            {val}
          </text>
          {hl && (
            <text
              x="550"
              y={189 + i * 26}
              textAnchor="end"
              fontFamily="sans-serif"
              fontSize="8"
              fill="#b45309"
              fontWeight="bold"
            >
              ● 回復参照
            </text>
          )}
        </g>
      ))}

      <rect x="20" y="366" width="555" height="22" fill="#1e3a5f" />
      <text x="30" y="382" fontFamily="sans-serif" fontSize="11" fill="#fff" fontWeight="bold">
        ■ 既契約サマリ
      </text>
      {summary.map(([label, val], i) => (
        <g key={i}>
          <rect
            x="20"
            y={394 + i * 24}
            width="555"
            height="24"
            fill={i % 2 === 0 ? '#f8fafc' : '#fff'}
            stroke="#e2e8f0"
            strokeWidth="0.5"
          />
          <text x="32" y={410 + i * 24} fontFamily="sans-serif" fontSize="10" fill="#64748b" fontWeight="bold">
            {label}
          </text>
          <text x="220" y={410 + i * 24} fontFamily="monospace" fontSize="10" fill="#0f172a">
            {val}
          </text>
        </g>
      ))}

      <rect x="20" y="576" width="555" height="22" fill="#1e3a5f" />
      <text x="30" y="592" fontFamily="sans-serif" fontSize="11" fill="#fff" fontWeight="bold">
        ■ 住所変更履歴
      </text>
      <rect x="20" y="604" width="555" height="24" fill="#f1f5f9" />
      <text x="32" y="620" fontFamily="sans-serif" fontSize="9" fill="#475569" fontWeight="bold">
        変更日
      </text>
      <text x="130" y="620" fontFamily="sans-serif" fontSize="9" fill="#475569" fontWeight="bold">
        変更前住所
      </text>
      <text x="330" y="620" fontFamily="sans-serif" fontSize="9" fill="#475569" fontWeight="bold">
        変更後住所（現在）
      </text>
      {history.map(([d, b, a], i) => (
        <g key={i}>
          <rect
            x="20"
            y={628 + i * 26}
            width="555"
            height="26"
            fill={i === 0 ? '#fefce8' : '#fff'}
            stroke="#e2e8f0"
            strokeWidth="0.5"
          />
          <text x="32" y={644 + i * 26} fontFamily="monospace" fontSize="9" fill="#0f172a">
            {d}
          </text>
          <text x="130" y={644 + i * 26} fontFamily="sans-serif" fontSize="9" fill="#64748b">
            {b}
          </text>
          <text
            x="330"
            y={644 + i * 26}
            fontFamily="sans-serif"
            fontSize="9"
            fill="#0f172a"
            fontWeight={i === 0 ? 'bold' : 'normal'}
          >
            {a}
          </text>
        </g>
      ))}

      <rect x="20" y="700" width="555" height="60" rx="6" fill="#f0fdf4" stroke="#16a34a" strokeWidth="1" />
      <text x="34" y="720" fontFamily="sans-serif" fontSize="10" fill="#15803d" fontWeight="bold">
        ✓ データ信頼度
      </text>
      <text x="34" y="738" fontFamily="sans-serif" fontSize="9" fill="#166534">
        最終更新: 2023/04/15　／　名寄せ一致度: 98.7%　／　同一契約者と判定
      </text>
      <text x="34" y="752" fontFamily="sans-serif" fontSize="9" fill="#166534">
        本データを一次チェックの回復根拠として自動適用しました。
      </text>

      <text x="297" y="800" textAnchor="middle" fontFamily="sans-serif" fontSize="8" fill="#94a3b8">
        既契約照会システム  |  参照日時: 2025/10/16 09:12:34  |  照会ID: Q{secNo.slice(-4)}-8847
      </text>
    </svg>
  );
};
