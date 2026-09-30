import type { ChatTurn, Conversation, Message } from '../types/chat'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response
  try {
    response = await fetch(`${API_URL}${path}`, {
      ...init,
      headers: { 'Content-Type': 'application/json', ...init?.headers },
    })
  } catch {
    throw new Error('Could not reach the backend. Check that the API is running.')
  }
  if (!response.ok) {
    const payload = await response.json().catch(() => null) as { detail?: string } | null
    throw new Error(payload?.detail ?? `Request failed (${response.status})`)
  }
  return response.json() as Promise<T>
}

export const api = {
  createConversation: () => request<Conversation>('/conversations', { method: 'POST' }),
  loadConversation: (id: string) => request<Conversation>(`/conversations/${id}`),
  loadMessages: (id: string) => request<Message[]>(`/conversations/${id}/messages`),
  sendMessage: (id: string, content: string) => request<ChatTurn>(`/conversations/${id}/messages`, {
    method: 'POST',
    body: JSON.stringify({ content }),
  }),
}
