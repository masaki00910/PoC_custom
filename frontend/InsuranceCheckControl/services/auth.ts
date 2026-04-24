import type { UserRole } from '../types/domain';

/**
 * PoC 用の擬似認証サービス。
 * CLAUDE.md §4 に従い、将来的に MSAL.js + Entra ID に差し替える前提で
 * 副作用（現状はインメモリ、将来は MSAL）を本モジュールに閉じ込める。
 *
 * NOTE: トークン／個人情報を localStorage / sessionStorage に保存しない。
 *       ブラウザリロード時は再ログインを要求する（MSAL 切替後の挙動と同じ）。
 */

export interface Session {
  userId: string;
  role: UserRole;
}

let currentSession: Session | null = null;

const resolveRole = (userId: string): UserRole => {
  const lower = userId.toLowerCase();
  return lower === 'admin' || lower.includes('admin') ? 'admin' : 'user';
};

export const login = async (userId: string, password: string): Promise<Session> => {
  if (!userId || !password) {
    throw new Error('IDとパスワードを入力してください。');
  }
  await new Promise((resolve) => setTimeout(resolve, 700));
  const session: Session = { userId, role: resolveRole(userId) };
  currentSession = session;
  return session;
};

export const logout = (): void => {
  currentSession = null;
};

export const getSession = (): Session | null => currentSession;
