import type { Message } from '../types/chat'

interface MessageListProps {
  messages: Message[]
  loading: boolean
}

export function MessageList({ messages, loading }: MessageListProps) {
  if (loading) return <div className="empty-state" role="status">Loading messages…</div>
  if (messages.length === 0) {
    return <div className="empty-state">Say hello to start the conversation.</div>
  }

  return (
    <ol className="message-list" aria-label="Message history">
      {messages.map((message) => (
        <li className={`message message--${message.role}`} key={message.id}>
          <span className="message__role">{message.role === 'user' ? 'You' : 'Companion'}</span>
          <p>{message.content}</p>
        </li>
      ))}
    </ol>
  )
}
