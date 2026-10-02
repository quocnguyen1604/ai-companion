import type { Message as MessageType } from "../types/chat";
import { Message } from "./Message";

interface MessageListProps {
  messages: MessageType[];
  loading: boolean;
}

export function MessageList({ messages, loading }: MessageListProps) {
  if (loading)
    return (
      <div className="empty-state" role="status">
        Loading messages…
      </div>
    );
  if (messages.length === 0) {
    return (
      <div className="empty-state">Say hello to start the conversation.</div>
    );
  }

  return (
    <ol className="message-list" aria-label="Message history">
      {messages.map((message) => (
        <Message key={message.id} message={message} />
      ))}
    </ol>
  );
}
