import type {
  FinalDecision,
  RecoveryListEntry,
  SecondaryCheckDetail,
  ToolCall,
  ToolCallLogEntry,
} from '../types/secondary-check';

/**
 * S-03-001 応答相当の固定サンプル。business_type="住所" のケース。
 * CheckResultView.tsx のサンプルと揃えている。
 */
const buildRecoveryList = (policyNumber: string): RecoveryListEntry[] => {
  const prevPolicy = 'P' + policyNumber.replace(/^./, '');
  return [
    // 契約者：名前 (表示のみ)
    { attribute: '契約者', section: 'original', title: '契約者名', value: '松本　直樹', errorFlag: false, checkResult: 'OK' },

    // 契約者：契〒 (エラー → 回復対象)
    { attribute: '契約者', section: 'original',        title: '契〒',          value: '*000',    errorFlag: true, checkResult: 'NG' },
    { attribute: '契約者', section: 'first_recovery',  title: '契〒_回復結果',  value: '060-0001', errorFlag: true, checkResult: 'NG' },
    { attribute: '契約者', section: 'first_recovery',  title: '契〒_回復理由',  value: `[契約者住所(〒)] 既契約より修正：証券番号 ${prevPolicy}`, errorFlag: true, checkResult: 'NG' },
    { attribute: '契約者', section: 'second_recovery', title: '契〒_再回復結果', value: '', errorFlag: true, checkResult: '' },
    { attribute: '契約者', section: 'second_recovery', title: '契〒_再回復理由', value: '', errorFlag: true, checkResult: '' },

    // 契約者：契住所 (空 → 回復対象)
    { attribute: '契約者', section: 'original',        title: '契住所',          value: '',        errorFlag: true, checkResult: 'NG' },
    { attribute: '契約者', section: 'first_recovery',  title: '契住所_回復結果',  value: 'ﾎｯｶｲﾄﾞｳｻｯﾎﾟﾛｼﾁｭｳｵｳｸｷﾀ1ｼﾞｮｳﾆｼ11-11-11', errorFlag: true, checkResult: 'NG' },
    { attribute: '契約者', section: 'first_recovery',  title: '契住所_回復理由',  value: `[契約者住所(カナ)] 既契約より修正：証券番号 ${prevPolicy}`, errorFlag: true, checkResult: 'NG' },
    { attribute: '契約者', section: 'second_recovery', title: '契住所_再回復結果', value: '', errorFlag: true, checkResult: '' },
    { attribute: '契約者', section: 'second_recovery', title: '契住所_再回復理由', value: '', errorFlag: true, checkResult: '' },

    // 被保険者：名前 (表示のみ)
    { attribute: '被保険者', section: 'original', title: '第一被名', value: 'ｷﾑﾗｻﾕﾘ', errorFlag: false, checkResult: 'OK' },

    // 被保険者：被〒 (エラーなし、表示のみ)
    { attribute: '被保険者', section: 'original', title: '被〒', value: '060-0001', errorFlag: false, checkResult: 'OK' },

    // 被保険者：被住所 (エラーなし、表示のみ)
    { attribute: '被保険者', section: 'original', title: '被住所', value: 'ﾎｯｶｲﾄﾞｳｻｯﾎﾟﾛｼﾁｭｳｵｳｸｷﾀ2ｼﾞｮｳﾆｼ12-12-12', errorFlag: false, checkResult: 'OK' },
  ];
};

/** S-03-001 詳細データの取得に相当。フロント完全モック。 */
export const fetchSecondaryCheckDetail = (policyNumber: string): Promise<SecondaryCheckDetail> =>
  new Promise((resolve) => {
    setTimeout(
      () =>
        resolve({
          policyNumber,
          businessType: '住所',
          recoveryList: buildRecoveryList(policyNumber),
          sharepointUrl: `https://stellar2026.sharepoint.com/sites/A_test/Shared%20Documents/${policyNumber}`,
          caDocumentImportId: `doc-import-${policyNumber}`,
        }),
      120,
    );
  });

/**
 * tool 呼び出しを in-memory state に記録するだけの疑似 backend。
 * 再起動で消える PoC レベル。将来 S-04-001/002/003 の API に差し替える。
 */
export interface MockBackendState {
  toolCallLog: ToolCallLogEntry[];
  finalDecision: FinalDecision;
}

let currentTimestamp = 0;
const now = (): string => {
  currentTimestamp += 1;
  return new Date(Date.now() + currentTimestamp).toISOString();
};

const newId = (): string => `tc-${Math.random().toString(36).slice(2, 10)}`;

export const applyToolCall = (
  state: MockBackendState,
  call: ToolCall,
): { nextState: MockBackendState; entry: ToolCallLogEntry } => {
  const timestamp = now();
  let message: string;
  let nextFinal = state.finalDecision;

  switch (call.name) {
    case 'update_recovery_value':
      message = `${call.input.fieldName} を「${call.input.value}」に更新（理由: ${call.input.reason}）`;
      break;
    case 'file_inquiry':
      message = `問い合わせ起票: [${call.input.category}] ${call.input.contents}`;
      break;
    case 'finalize_check':
      message = call.input.checkResult ? '承認しました' : '差し戻しました';
      nextFinal = {
        status: call.input.checkResult ? 'approved' : 'rejected',
        completedAt: timestamp,
        note: call.input.status,
      };
      break;
  }

  const entry: ToolCallLogEntry = {
    id: newId(),
    timestamp,
    call,
    result: 'ok',
    message,
  };

  return {
    nextState: {
      toolCallLog: [...state.toolCallLog, entry],
      finalDecision: nextFinal,
    },
    entry,
  };
};

export const initialBackendState = (): MockBackendState => ({
  toolCallLog: [],
  finalDecision: { status: 'pending' },
});
