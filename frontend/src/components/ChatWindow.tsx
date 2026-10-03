import { useEffect, useState } from "react";
import { api } from "../services/api";
import type { Conversation, Message as MessageType } from "../types/chat";
import { MessageInput } from "./MessageInput";
import { MessageList } from "./MessageList";

export function ChatWindow() {
  const [conversation, setConversation] = useState<Conversation | null>(null);
  const [messages, setMessages] = useState<MessageType[]>([]);
  const [tempAssistantMessage, setTempAssistantMessage] =
    useState<MessageType | null>(null);
  const [tempUserMessage, setTempUserMessage] = useState<MessageType | null>(
    null,
  );
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [compacting, setCompacting] = useState(false);

  useEffect(() => {
    let active = true;
    async function initialize() {
      try {
        const savedId = window.localStorage.getItem("companion.conversationId");
        const current = savedId
          ? await api.loadConversation(savedId)
          : await api.createConversation();
        if (!savedId)
          window.localStorage.setItem("companion.conversationId", current.id);
        if (!active) return;
        setConversation(current);
        const history = await api.loadMessages(current.id);
        if (active) setMessages(history);
      } catch (caught) {
        if (active)
          setError(
            caught instanceof Error ? caught.message : "Something went wrong.",
          );
      } finally {
        if (active) setLoading(false);
      }
    }
    void initialize();
    return () => {
      active = false;
    };
  }, []);

  async function send(content: string) {
    if (!conversation) return;
    setError(null);
    setTempUserMessage({
      id: crypto.randomUUID(),
      role: "user",
      content,
      conversation_id: conversation.id,
      created_at: new Date().toISOString(),
      response_id: null,
      previous_message_id:
        messages.length > 0 ? messages[messages.length - 1].id : null,
      sequence_number:
        messages.length > 0
          ? messages[messages.length - 1].sequence_number + 1
          : 0,
      token_count: 0,
      prompt_token_count: 0,
    });
    setTempAssistantMessage({
      id: crypto.randomUUID(),
      role: "assistant",
      content: "",
      conversation_id: conversation.id,
      created_at: new Date().toISOString(),
      response_id: null,
      previous_message_id: null,
      sequence_number:
        messages.length > 0
          ? messages[messages.length - 1].sequence_number + 2
          : 0,
      token_count: 0,
      prompt_token_count: 0,
    });
    setSending(true);
    try {
      for await (const event of api.streamMessage(conversation.id, content)) {
        if (event.type === "context.compact.initiated") {
          setCompacting(true);
        }
        if (event.type === "context.compact.completed") {
          setCompacting(false);
        }
        if (event.type === "response.output_text.delta") {
          setTempAssistantMessage((current) =>
            current
              ? { ...current, content: current.content + event.delta }
              : current,
          );
        } else if (event.type === "response.completed") {
          setMessages((current) => [
            ...current,
            event.turn.user_message,
            event.turn.assistant_message,
          ]);
          setTempUserMessage(null);
          setTempAssistantMessage(null);
        }
      }
    } catch (caught) {
      setError(
        caught instanceof Error
          ? caught.message
          : "Could not send the message.",
      );
    } finally {
      setSending(false);
    }
  }

  const visibleMessages = [
    ...messages,
    ...(tempUserMessage ? [tempUserMessage] : []),
    ...(tempAssistantMessage ? [tempAssistantMessage] : []),
  ];

  return (
    <main className="app-shell">
      <header className="app-header">
        <div className="avatar" aria-hidden="true">
          C
        </div>
        <div>
          <h1>Companion</h1>
          <p>Here for a conversation</p>
        </div>
      </header>
      {error && (
        <div className="error-banner" role="alert">
          {error}
        </div>
      )}
      <section className="chat-panel" aria-label="Chat">
        <MessageList messages={visibleMessages} loading={loading} />
        {sending &&
          !compacting &&
          tempAssistantMessage &&
          tempAssistantMessage?.content === "" && (
            <div className="typing" role="status">
              Companion is thinking…
            </div>
          )}
        {compacting && (
          <div className="typing" role="status">
            Companion is summarizing the conversation to make room for more
            messages…
          </div>
        )}
        <MessageInput
          disabled={loading || sending || !conversation}
          onSend={send}
        />
      </section>
      <footer>Conversations are stored locally on this device.</footer>
    </main>
  );
}
