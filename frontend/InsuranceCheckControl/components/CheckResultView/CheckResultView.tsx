import type { CSSProperties, FC } from 'react';

interface CheckResultViewProps {
  secNo: string;
}

interface InputField {
  label: string;
  value: string;
  error?: boolean;
}

interface RecoveryField {
  label: string;
  value: string;
}

interface SectionRow {
  section: string;
  hasError: boolean;
  fields: InputField[];
  recoveries: RecoveryField[];
}

const cellTh: CSSProperties = {
  padding: '7px 10px',
  textAlign: 'left',
  fontSize: 11,
  fontWeight: 700,
  color: 'var(--navy-700)',
  background: 'var(--navy-50)',
  borderBottom: '1px solid var(--border)',
  whiteSpace: 'nowrap',
};

const cellTd: CSSProperties = {
  padding: '7px 10px',
  fontSize: 12,
  color: 'var(--navy-900)',
  borderBottom: '1px solid var(--border)',
  verticalAlign: 'top',
};

export const CheckResultView: FC<CheckResultViewProps> = ({ secNo }) => {
  const rows: SectionRow[] = [
    {
      section: '契約者',
      hasError: true,
      fields: [
        { label: '契約者名', value: 'ﾏﾂﾓﾄﾅｵｷ' },
        { label: '契〒', value: '*000', error: true },
        { label: '契住所', value: '', error: true },
      ],
      recoveries: [
        { label: '契〒_回復結果', value: '060-0001' },
        { label: '契〒_回復理由', value: `[契約者住所(〒)]既契約より修正：証券番号${secNo}` },
        { label: '契住所_回復結果', value: 'ﾎｯｶｲﾄﾞｳｻｯﾎﾟﾛｼﾁｭｳｵｳｸｷﾀ1ｼﾞｮｳﾆｼ11-11-11' },
        { label: '契住所_回復理由', value: `[契約者住所(〒・カナ)]既契約より修正：証券番号${secNo}` },
      ],
    },
    {
      section: '被保険者',
      hasError: false,
      fields: [
        { label: '第一被名', value: 'ｷﾑﾗｻﾕﾘ' },
        { label: '被〒', value: '060-0001' },
        { label: '被住所', value: 'ﾎｯｶｲﾄﾞｳｻｯﾎﾟﾛｼﾁｭｳｵｳｸｷﾀ2ｼﾞｮｳﾆｼ12-12-12' },
      ],
      recoveries: [
        { label: '被〒_回復結果', value: '—' },
        { label: '被〒_回復理由', value: '—' },
        { label: '被住所_回復結果', value: '—' },
        { label: '被住所_回復理由', value: '—' },
      ],
    },
  ];

  return (
    <div
      style={{
        maxWidth: '94%',
        background: '#fff',
        borderRadius: 10,
        border: '1px solid var(--border)',
        boxShadow: 'var(--shadow-sm)',
        overflow: 'hidden',
        fontSize: 12,
      }}
    >
      <div
        style={{
          padding: '10px 14px',
          background: 'var(--accent-lt)',
          borderBottom: '1px solid var(--border)',
          display: 'flex',
          alignItems: 'center',
          gap: 8,
        }}
      >
        <svg width="15" height="15" fill="none" viewBox="0 0 24 24">
          <path
            d="M9 11l3 3L22 4M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"
            stroke="#2563eb"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
        <div style={{ fontSize: 13, fontWeight: 700, color: 'var(--accent)' }}>
          一次チェック／エラー回復結果
        </div>
        <span
          style={{
            fontSize: 11,
            color: 'var(--gray)',
            marginLeft: 'auto',
            fontFamily: 'monospace',
          }}
        >
          {secNo}
        </span>
      </div>

      {rows.map((r, i) => (
        <div
          key={i}
          style={{
            padding: '12px 14px',
            borderBottom: i < rows.length - 1 ? '1px solid var(--border)' : 'none',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 8 }}>
            <span
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: 5,
                padding: '2px 9px',
                borderRadius: 20,
                fontSize: 11,
                fontWeight: 700,
                background: r.hasError ? 'var(--red-lt)' : 'var(--green-lt)',
                color: r.hasError ? 'var(--red)' : 'var(--green)',
              }}
            >
              {r.hasError ? '⚠ エラーあり（要確認）' : '✓ エラーなし'}
            </span>
            <span style={{ fontSize: 13, fontWeight: 700, color: 'var(--navy-900)' }}>
              ■{r.section}
            </span>
          </div>
          <table
            style={{
              width: '100%',
              borderCollapse: 'collapse',
              marginBottom: 8,
              border: '1px solid var(--border)',
              borderRadius: 6,
              overflow: 'hidden',
            }}
          >
            <thead>
              <tr>
                <th style={{ ...cellTh, width: '35%' }}>項目</th>
                <th style={cellTh}>入力値</th>
              </tr>
            </thead>
            <tbody>
              {r.fields.map((f, j) => (
                <tr key={j} style={{ background: f.error ? 'var(--red-lt)' : '#fff' }}>
                  <td style={{ ...cellTd, color: 'var(--gray)', fontWeight: 600 }}>{f.label}</td>
                  <td
                    style={{
                      ...cellTd,
                      fontFamily: 'monospace',
                      color: f.error ? 'var(--red)' : 'var(--navy-900)',
                    }}
                  >
                    {f.value || '(空欄)'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--navy-700)', marginBottom: 4 }}>
            【一次チェック回復結果】
          </div>
          <table
            style={{
              width: '100%',
              borderCollapse: 'collapse',
              border: '1px solid var(--border)',
              borderRadius: 6,
              overflow: 'hidden',
            }}
          >
            <thead>
              <tr>
                <th style={{ ...cellTh, width: '35%' }}>項目</th>
                <th style={cellTh}>内容</th>
              </tr>
            </thead>
            <tbody>
              {r.recoveries.map((f, j) => {
                const empty = f.value === '—' || f.value === '';
                return (
                  <tr key={j} style={{ background: empty ? '#fff' : 'var(--accent-lt)' }}>
                    <td style={{ ...cellTd, color: 'var(--gray)', fontWeight: 600 }}>{f.label}</td>
                    <td
                      style={{
                        ...cellTd,
                        fontFamily: 'monospace',
                        color: empty ? 'var(--gray)' : 'var(--navy-900)',
                        wordBreak: 'break-all',
                      }}
                    >
                      {f.value}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      ))}
    </div>
  );
};
