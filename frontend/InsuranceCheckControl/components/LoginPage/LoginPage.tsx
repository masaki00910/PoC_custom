import { useState, type FC, type FormEvent } from 'react';

interface LoginPageProps {
  onLogin: (userId: string, password: string) => Promise<void>;
  loggingIn: boolean;
  error: string | null;
}

export const LoginPage: FC<LoginPageProps> = ({ onLogin, loggingIn, error }) => {
  const [id, setId] = useState('');
  const [pw, setPw] = useState('');
  const [localErr, setLocalErr] = useState<string | null>(null);

  const handleSubmit = async (e: FormEvent<HTMLFormElement>): Promise<void> => {
    e.preventDefault();
    if (!id || !pw) {
      setLocalErr('IDとパスワードを入力してください。');
      return;
    }
    setLocalErr(null);
    try {
      await onLogin(id, pw);
    } catch {
      // エラーは親 hook が error として公開するので、ここでは握りつぶす
    }
  };

  const shownError = localErr ?? error;

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg,#e5e7eb 0%,#f3f4f6 50%,#fff 100%)',
      }}
    >
      <div
        style={{
          width: 380,
          background: '#fff',
          borderRadius: 16,
          boxShadow: '0 20px 60px rgba(0,0,0,.12)',
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            background: '#fff',
            borderBottom: '1px solid var(--border)',
            padding: '32px 32px 24px',
            textAlign: 'center',
          }}
        >
          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: 52,
              height: 52,
              background: 'var(--accent)',
              borderRadius: 12,
              marginBottom: 14,
            }}
          >
            <svg width="26" height="26" fill="none" viewBox="0 0 24 24">
              <path
                d="M9 12h6M9 16h6M7 8h10M5 4h14a1 1 0 011 1v14a1 1 0 01-1 1H5a1 1 0 01-1-1V5a1 1 0 011-1z"
                stroke="#fff"
                strokeWidth="1.8"
                strokeLinecap="round"
              />
            </svg>
          </div>
          <div style={{ color: 'var(--navy-900)', fontSize: 17, fontWeight: 700 }}>
            保険申込書エラー回復
          </div>
          <div style={{ color: 'var(--gray)', fontSize: 12, marginTop: 4 }}>
            Error Recovery System
          </div>
        </div>
        <form onSubmit={handleSubmit} style={{ padding: '28px 32px 32px' }}>
          <div style={{ marginBottom: 16 }}>
            <label
              style={{
                display: 'block',
                fontSize: 12,
                fontWeight: 600,
                color: 'var(--navy-700)',
                marginBottom: 6,
              }}
            >
              ユーザーID
            </label>
            <input
              value={id}
              onChange={(e) => setId(e.target.value)}
              style={{
                width: '100%',
                padding: '10px 14px',
                border: '1.5px solid var(--border)',
                borderRadius: 8,
                fontSize: 14,
                outline: 'none',
              }}
              onFocus={(e) => (e.target.style.borderColor = 'var(--accent)')}
              onBlur={(e) => (e.target.style.borderColor = 'var(--border)')}
              placeholder="例: tanaka"
              autoComplete="username"
            />
          </div>
          <div style={{ marginBottom: 20 }}>
            <label
              style={{
                display: 'block',
                fontSize: 12,
                fontWeight: 600,
                color: 'var(--navy-700)',
                marginBottom: 6,
              }}
            >
              パスワード
            </label>
            <input
              type="password"
              value={pw}
              onChange={(e) => setPw(e.target.value)}
              style={{
                width: '100%',
                padding: '10px 14px',
                border: '1.5px solid var(--border)',
                borderRadius: 8,
                fontSize: 14,
                outline: 'none',
              }}
              onFocus={(e) => (e.target.style.borderColor = 'var(--accent)')}
              onBlur={(e) => (e.target.style.borderColor = 'var(--border)')}
              placeholder="••••••••"
              autoComplete="current-password"
            />
          </div>
          {shownError && (
            <div
              style={{
                fontSize: 12,
                color: 'var(--red)',
                marginBottom: 12,
                padding: '8px 12px',
                background: 'var(--red-lt)',
                borderRadius: 6,
              }}
            >
              {shownError}
            </div>
          )}
          <button
            type="submit"
            disabled={loggingIn}
            style={{
              width: '100%',
              padding: '12px',
              background: loggingIn ? '#93c5fd' : 'var(--accent)',
              color: '#fff',
              border: 'none',
              borderRadius: 8,
              fontSize: 14,
              fontWeight: 600,
              cursor: loggingIn ? 'wait' : 'pointer',
            }}
          >
            {loggingIn ? 'ログイン中...' : 'ログイン'}
          </button>
          <div
            style={{
              textAlign: 'center',
              marginTop: 14,
              fontSize: 12,
              color: 'var(--gray)',
            }}
          >
            デモ：
            <code
              style={{
                background: 'var(--gray-lt)',
                padding: '1px 6px',
                borderRadius: 4,
              }}
            >
              admin
            </code>
            でログインすると管理者権限
          </div>
        </form>
      </div>
    </div>
  );
};
