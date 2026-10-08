import type { Message as MessageType } from "../types/chat";
import { Message } from "./Message";
import { useRef, useEffect } from "react";

interface MessageListProps {
  messages: MessageType[];
  loading: boolean;
}

export function MessageList({ messages, loading }: MessageListProps) {
  const listRef = useRef<HTMLOListElement>(null);

  useEffect(() => {
    if (listRef.current) {
      listRef.current.scrollTop = listRef.current.scrollHeight;
    }
  }, [messages]);

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
    <ol ref={listRef} className="message-list" aria-label="Message history">
      {messages.map((message) => {
        return <Message key={message.id} message={message} />;
      })}
    </ol>
  );
}
