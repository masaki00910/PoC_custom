import {
  useEffect,
  useRef,
  useState,
  type CSSProperties,
  type FC,
  type MouseEvent,
  type ReactNode,
  type WheelEvent,
} from 'react';
import { ContractPlaceholder } from './ContractPlaceholder';
import { ScanPlaceholder } from './ScanPlaceholder';

type ViewerTabId = 'scan' | 'contract';

interface ImageViewerProps {
  secNo: string;
}

const zBtn: CSSProperties = {
  background: 'var(--gray-lt)',
  border: '1px solid var(--border)',
  color: 'var(--navy-800)',
  borderRadius: 5,
  padding: '4px 10px',
  fontSize: 13,
  cursor: 'pointer',
};

const viewerTabs: Array<{ id: ViewerTabId; label: string; icon: ReactNode }> = [
  {
    id: 'scan',
    label: '申込書スキャン',
    icon: (
      <path
        d="M4 4h12l4 4v12a2 2 0 01-2 2H4a2 2 0 01-2-2V6a2 2 0 012-2z M14 4v6h6"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    ),
  },
  {
    id: 'contract',
    label: '既契約情報',
    icon: (
      <path
        d="M9 12h6m-6 4h6M7 8h10M5 4h14a1 1 0 011 1v14a1 1 0 01-1 1H5a1 1 0 01-1-1V5a1 1 0 011-1z"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
      />
    ),
  },
];

export const ImageViewer: FC<ImageViewerProps> = ({ secNo }) => {
  const [viewerTab, setViewerTab] = useState<ViewerTabId>('scan');
  const [scale, setScale] = useState(1);
  const [offset, setOffset] = useState({ x: 0, y: 0 });
  const [dragging, setDragging] = useState(false);
  const dragStart = useRef<{ x: number; y: number } | null>(null);

  useEffect(() => {
    setScale(1);
    setOffset({ x: 0, y: 0 });
  }, [secNo, viewerTab]);

  const handleWheel = (e: WheelEvent<HTMLDivElement>): void => {
    e.preventDefault();
    setScale((s) => Math.max(0.3, Math.min(4, s - e.deltaY * 0.001)));
  };
  const handleMouseDown = (e: MouseEvent<HTMLDivElement>): void => {
    setDragging(true);
    dragStart.current = { x: e.clientX - offset.x, y: e.clientY - offset.y };
  };
  const handleMouseMove = (e: MouseEvent<HTMLDivElement>): void => {
    if (!dragging || !dragStart.current) return;
    setOffset({ x: e.clientX - dragStart.current.x, y: e.clientY - dragStart.current.y });
  };
  const handleMouseUp = (): void => setDragging(false);

  return (
    <div
      style={{
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        background: '#f0f1f3',
        minWidth: 0,
        height: '100%',
      }}
    >
      <div
        style={{
          display: 'flex',
          alignItems: 'flex-end',
          background: '#e5e7eb',
          paddingLeft: 8,
          paddingTop: 6,
          borderBottom: '1px solid var(--border)',
          flexShrink: 0,
          gap: 2,
        }}
      >
        {viewerTabs.map((t) => {
          const active = viewerTab === t.id;
          return (
            <button
              key={t.id}
              onClick={() => setViewerTab(t.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 6,
                padding: '8px 14px',
                border: '1px solid var(--border)',
                borderBottom: active ? '1px solid #fff' : '1px solid var(--border)',
                borderRadius: '7px 7px 0 0',
                background: active ? '#fff' : 'transparent',
                color: active ? 'var(--navy-900)' : 'var(--gray)',
                fontSize: 12,
                fontWeight: active ? 700 : 500,
                cursor: 'pointer',
                marginBottom: -1,
                position: 'relative',
              }}
            >
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none">
                {t.icon}
              </svg>
              {t.label}
              {t.id === 'contract' && (
                <span
                  style={{
                    marginLeft: 4,
                    padding: '1px 7px',
                    borderRadius: 10,
                    fontSize: 9,
                    fontWeight: 700,
                    background: active ? 'var(--accent-lt)' : '#d1d5db',
                    color: active ? 'var(--accent)' : '#6b7280',
                  }}
                >
                  参考
                </span>
              )}
            </button>
          );
        })}
      </div>
      <div
        style={{
          padding: '8px 14px',
          background: '#fff',
          display: 'flex',
          alignItems: 'center',
          gap: 10,
          flexShrink: 0,
          borderBottom: '1px solid var(--border)',
        }}
      >
        <span style={{ color: 'var(--gray)', fontSize: 12, fontWeight: 600 }}>
          {viewerTab === 'scan' ? '申込書スキャン画像' : 'エラー回復の根拠となった既契約データ'}
        </span>
        <div style={{ flex: 1 }} />
        <button onClick={() => setScale((s) => Math.min(4, s + 0.2))} style={zBtn}>
          ＋
        </button>
        <span style={{ color: 'var(--gray)', fontSize: 12, minWidth: 40, textAlign: 'center' }}>
          {Math.round(scale * 100)}%
        </span>
        <button onClick={() => setScale((s) => Math.max(0.3, s - 0.2))} style={zBtn}>
          －
        </button>
        <button
          onClick={() => {
            setScale(1);
            setOffset({ x: 0, y: 0 });
          }}
          style={{ ...zBtn, minWidth: 56 }}
        >
          リセット
        </button>
      </div>
      <div
        style={{
          flex: 1,
          overflow: 'hidden',
          cursor: dragging ? 'grabbing' : 'grab',
          position: 'relative',
          userSelect: 'none',
        }}
        onWheel={handleWheel}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
      >
        <div
          style={{
            position: 'absolute',
            inset: 0,
            display: 'flex',
            alignItems: 'flex-start',
            justifyContent: 'center',
            padding: 24,
            overflow: 'hidden',
          }}
        >
          {viewerTab === 'scan' ? (
            <ScanPlaceholder scale={scale} offset={offset} secNo={secNo} />
          ) : (
            <ContractPlaceholder scale={scale} offset={offset} secNo={secNo} />
          )}
        </div>
      </div>
    </div>
  );
};
