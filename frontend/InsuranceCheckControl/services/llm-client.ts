import type { LLMMessage, ToolName } from '../types/secondary-check';

/**
 * LLM クライアントの抽象。Phase 1 は MockLLMClient、Phase 2 は実 LLM (Anthropic API 等)。
 * I/O は Anthropic Messages API の shape に寄せている。
 */
export interface LLMToolDefinition {
  name: ToolName;
  description: string;
  inputSchema: Record<string, unknown>;
}

export interface LLMRequest {
  systemPrompt: string;
  messages: LLMMessage[];
  tools: LLMToolDefinition[];
}

export interface LLMResponse {
  message: LLMMessage;
  stopReason: 'end_turn' | 'tool_use';
}

export interface LLMClient {
  respond(request: LLMRequest): Promise<LLMResponse>;
}
