export type MessageRole = 'user' | 'assistant'

export interface Conversation {
  id: string
  created_at: string
  updated_at: string
}

export interface Message {
  id: string
  conversation_id: string
  role: MessageRole
  content: string
  created_at: string
}

export interface ChatTurn {
  user_message: Message
  assistant_message: Message
}
