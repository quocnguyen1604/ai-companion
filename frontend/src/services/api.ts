import type { ChatTurn, Conversation, Message } from "../types/chat";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api";

export type StreamEvent =
  | { type: "response.output_text.delta"; delta: string }
  | { type: "response.completed"; turn: ChatTurn };

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_URL}${path}`, {
      ...init,
      headers: { "Content-Type": "application/json", ...init?.headers },
    });
  } catch {
    throw new Error(
      "Could not reach the backend. Check that the API is running.",
    );
  }
  if (!response.ok) {
    const payload = (await response.json().catch(() => null)) as {
      detail?: string;
    } | null;
    throw new Error(payload?.detail ?? `Request failed (${response.status})`);
  }
  return response.json() as Promise<T>;
}

async function requestStream<T>(
  path: string,
  init?: RequestInit,
): Promise<ReadableStream<T>> {
  let response: Response;
  try {
    response = await fetch(`${API_URL}${path}`, {
      ...init,
      headers: { "Content-Type": "application/json", ...init?.headers },
    });
  } catch {
    throw new Error(
      "Could not reach the backend. Check that the API is running.",
    );
  }
  if (!response.ok) {
    const payload = (await response.json().catch(() => null)) as {
      detail?: string;
    } | null;
    throw new Error(payload?.detail ?? `Request failed (${response.status})`);
  }
  return response.body as ReadableStream<T>;
}

async function* parseStream(
  stream: ReadableStream<Uint8Array>,
): AsyncGenerator<StreamEvent> {
  const reader = stream.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  try {
    while (true) {
      const { done, value } = await reader.read();
      buffer += decoder.decode(value, { stream: !done });
      buffer = buffer.replace(/\r\n/g, "\n");

      let boundary = buffer.indexOf("\n\n");
      while (boundary !== -1) {
        const chunk = buffer.slice(0, boundary);
        buffer = buffer.slice(boundary + 2);

        console.log("\n--- Chunk ---");
        console.log(chunk);

        const data = chunk
          .split("\n")
          .filter((line) => line.startsWith("data: "))
          .map((line) => line.slice(5).trimStart())
          .join("\n");

        console.log("\n--- Data ---");
        console.log(data);

        if (data) yield JSON.parse(data) as StreamEvent;

        boundary = buffer.indexOf("\n\n");
      }

      if (done) break;
    }
  } finally {
    reader.releaseLock();
  }
}

export const api = {
  createConversation: () =>
    request<Conversation>("/conversations", { method: "POST" }),
  loadConversation: (id: string) =>
    request<Conversation>(`/conversations/${id}`),
  loadMessages: (id: string) =>
    request<Message[]>(`/conversations/${id}/messages`),
  sendMessage: (id: string, content: string) =>
    request<ChatTurn>(`/conversations/${id}/messages`, {
      method: "POST",
      body: JSON.stringify({ content }),
    }),
  async *streamMessage(
    id: string,
    content: string,
  ): AsyncGenerator<StreamEvent> {
    const responseStream = await requestStream<Uint8Array>(
      `/conversations/${id}/messages`,
      {
        method: "POST",
        body: JSON.stringify({ content }),
      },
    );

    yield* parseStream(responseStream);
  },
};
