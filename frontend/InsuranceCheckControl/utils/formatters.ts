export const pad = (n: number, len = 2): string => String(n).padStart(len, '0');

export const fmtDate = (d: Date): string =>
  `${d.getFullYear()}/${pad(d.getMonth() + 1)}/${pad(d.getDate())}`;

export const pickRandom = <T>(arr: readonly T[]): T => {
  const idx = Math.floor(Math.random() * arr.length);
  const item = arr[idx];
  if (item === undefined) {
    throw new Error('pickRandom called on empty array');
  }
  return item;
};
