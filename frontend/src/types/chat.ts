export type MessageRole = "user" | "assistant";

export interface Conversation {
  id: string;
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: string;
  conversation_id: string;
  role: MessageRole;
  content: string;
  created_at: string;
  response_id: string | null;
  previous_message_id: string | null;
  sequence_number: number;
  token_count: number;
  prompt_token_count: number;
}

export interface ChatTurn {
  user_message: Message;
  assistant_message: Message;
}
