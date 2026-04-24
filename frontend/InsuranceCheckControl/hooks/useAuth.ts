import { useCallback, useState } from 'react';
import { login as svcLogin, logout as svcLogout, type Session } from '../services/auth';

export interface UseAuthResult {
  session: Session | null;
  isAdmin: boolean;
  loggingIn: boolean;
  error: string | null;
  login: (userId: string, password: string) => Promise<void>;
  logout: () => void;
}

export const useAuth = (): UseAuthResult => {
  const [session, setSession] = useState<Session | null>(null);
  const [loggingIn, setLoggingIn] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const login = useCallback(async (userId: string, password: string) => {
    setLoggingIn(true);
    setError(null);
    try {
      const next = await svcLogin(userId, password);
      setSession(next);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'ログインに失敗しました。');
      throw e;
    } finally {
      setLoggingIn(false);
    }
  }, []);

  const logout = useCallback(() => {
    svcLogout();
    setSession(null);
  }, []);

  return {
    session,
    isAdmin: session?.role === 'admin',
    loggingIn,
    error,
    login,
    logout,
  };
};
