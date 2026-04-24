import type { ApplicationRow, Status, User } from '../types/domain';
import { STATUSES } from '../types/domain';
import { fmtDate, pickRandom, pad } from '../utils/formatters';

export const SAMPLE_USERS: readonly User[] = [
  { id: 'admin', name: 'システム管理者', role: 'admin', dept: '管理部', lastLogin: '2026/04/22 09:01' },
  { id: 'tanaka', name: '田中 花子', role: 'user', dept: '第一営業部', lastLogin: '2026/04/22 08:45' },
  { id: 'sato', name: '佐藤 一郎', role: 'user', dept: '第二営業部', lastLogin: '2026/04/21 17:30' },
  { id: 'yamada', name: '山田 太郎', role: 'user', dept: '審査部', lastLogin: '2026/04/21 16:12' },
  { id: 'suzuki', name: '鈴木 美咲', role: 'admin', dept: '管理部', lastLogin: '2026/04/20 11:00' },
  { id: 'ito', name: '伊藤 健二', role: 'user', dept: '第一営業部', lastLogin: '2026/04/19 14:22' },
];

const USER_IDS: readonly string[] = ['tanaka', 'sato', 'yamada', 'suzuki', 'ito'];

const buildSampleData = (): ApplicationRow[] =>
  Array.from({ length: 28 }, (_, i) => {
    const d = new Date(2025, Math.floor(Math.random() * 12), Math.floor(Math.random() * 28) + 1);
    const serial = pad(2024000 + (i + 1) * 17 + Math.floor(Math.random() * 100), 10).slice(0, 10);
    return {
      no: i + 1,
      secNo: `SK-${serial}`,
      status: pickRandom<Status>(STATUSES),
      importDate: fmtDate(d),
      assignee: pickRandom(USER_IDS),
    };
  });

export const SAMPLE_DATA: readonly ApplicationRow[] = buildSampleData();

export const AI_RESPONSES: ReadonlyArray<(secNo: string) => string> = [
  (s) => `申込書「${s}」を確認しました。被保険者氏名の記載に問題はありません。`,
  (s) => `証券番号「${s}」の申込日を確認中です。記載内容は正常です。`,
  () => `保険金額の記載を確認しました。補正の必要はありません。`,
  () => `住所欄に番地の記載が不完全な可能性があります。ご確認をお願いします。`,
  () => `署名欄に記入漏れが検出されました。申込人署名の確認が必要です。`,
  () => `記載内容を全項目チェックしました。問題は検出されませんでした。`,
];
