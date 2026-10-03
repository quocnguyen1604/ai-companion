import type { Message as MessageType } from "../types/chat";

export function Message({ message }: { message: MessageType }) {
  if (message.content.trim() === "") {
    return null;
  }
  return (
    <li className={`message message--${message.role}`} key={message.id}>
      <span className="message__role">
        {message.role === "user" ? "You" : "Companion"}
      </span>
      <p>{message.content}</p>
    </li>
  );
}
