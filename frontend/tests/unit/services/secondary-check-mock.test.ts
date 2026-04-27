import { describe, expect, it } from 'vitest';
import {
  applyToolCall,
  fetchSecondaryCheckDetail,
  initialBackendState,
} from '../../../InsuranceCheckControl/services/secondary-check-mock';
import type { ToolCall } from '../../../InsuranceCheckControl/types/secondary-check';

describe('fetchSecondaryCheckDetail', () => {
  it('住所の recoveryList に errorFlag 項目と OK 項目の両方を含む', async () => {
    const detail = await fetchSecondaryCheckDetail('SK-2024000017');
    expect(detail.policyNumber).toBe('SK-2024000017');
    expect(detail.businessType).toBe('住所');
    const errors = detail.recoveryList.filter((e) => e.section === 'original' && e.errorFlag);
    const oks = detail.recoveryList.filter((e) => e.section === 'original' && !e.errorFlag);
    expect(errors.length).toBeGreaterThan(0);
    expect(oks.length).toBeGreaterThan(0);
  });
});

describe('applyToolCall', () => {
  it('update_recovery_value でログに残り finalDecision は変わらない', () => {
    const call: ToolCall = {
      name: 'update_recovery_value',
      input: { fieldName: '契〒', value: '060-0001', reason: 'test' },
    };
    const { nextState, entry } = applyToolCall(initialBackendState(), call);
    expect(nextState.toolCallLog).toHaveLength(1);
    expect(nextState.finalDecision.status).toBe('pending');
    expect(entry.result).toBe('ok');
    expect(entry.message).toContain('契〒');
  });

  it('finalize_check(true) で finalDecision が approved に遷移', () => {
    const call: ToolCall = {
      name: 'finalize_check',
      input: { checkResult: true, status: '次工程待ち' },
    };
    const { nextState } = applyToolCall(initialBackendState(), call);
    expect(nextState.finalDecision.status).toBe('approved');
    expect(nextState.finalDecision.completedAt).toBeDefined();
  });

  it('finalize_check(false) で rejected に遷移', () => {
    const call: ToolCall = {
      name: 'finalize_check',
      input: { checkResult: false, status: '差し戻し' },
    };
    const { nextState } = applyToolCall(initialBackendState(), call);
    expect(nextState.finalDecision.status).toBe('rejected');
  });

  it('複数回呼ぶとログが追記される', () => {
    let state = initialBackendState();
    state = applyToolCall(state, {
      name: 'update_recovery_value',
      input: { fieldName: 'A', value: 'a', reason: 'r' },
    }).nextState;
    state = applyToolCall(state, {
      name: 'file_inquiry',
      input: { category: 'c', contents: 'x' },
    }).nextState;
    expect(state.toolCallLog).toHaveLength(2);
    expect(state.toolCallLog[0]?.call.name).toBe('update_recovery_value');
    expect(state.toolCallLog[1]?.call.name).toBe('file_inquiry');
  });
});
