export const STATUSES = ['未処理', '処理中', '完了', 'エラー', '保留'] as const;
export type Status = (typeof STATUSES)[number];

export type UserRole = 'admin' | 'user';

export interface User {
  id: string;
  name: string;
  role: UserRole;
  dept: string;
  lastLogin: string;
}

export interface ApplicationRow {
  no: number;
  secNo: string;
  status: Status;
  importDate: string;
  assignee: string;
}

export interface ChatTab extends ApplicationRow {
  id: string;
}

export type ChatMessageRole = 'ai' | 'user';

export interface ChatTextMessage {
  role: ChatMessageRole;
  text: string;
  type?: undefined;
}

export interface ChatRecoveryMessage {
  role: 'ai';
  type: 'recovery';
  secNo: string;
}

export type ChatMessage = ChatTextMessage | ChatRecoveryMessage;

export type ChatMessagesByTab = Record<string, ChatMessage[]>;

export type PageId = 'list' | 'chat' | 'admin';
