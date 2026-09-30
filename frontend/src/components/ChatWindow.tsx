import { useEffect, useState } from 'react'
import { api } from '../services/api'
import type { Conversation, Message } from '../types/chat'
import { MessageInput } from './MessageInput'
import { MessageList } from './MessageList'

export function ChatWindow() {
  const [conversation, setConversation] = useState<Conversation | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [loading, setLoading] = useState(true)
  const [sending, setSending] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let active = true
    async function initialize() {
      try {
        const savedId = window.localStorage.getItem('companion.conversationId')
        const current = savedId
          ? await api.loadConversation(savedId)
          : await api.createConversation()
        if (!savedId) window.localStorage.setItem('companion.conversationId', current.id)
        if (!active) return
        setConversation(current)
        const history = await api.loadMessages(current.id)
        if (active) setMessages(history)
      } catch (caught) {
        if (active) setError(caught instanceof Error ? caught.message : 'Something went wrong.')
      } finally {
        if (active) setLoading(false)
      }
    }
    void initialize()
    return () => { active = false }
  }, [])

  async function send(content: string) {
    if (!conversation) return
    setError(null)
    setSending(true)
    try {
      const turn = await api.sendMessage(conversation.id, content)
      setMessages((current) => [...current, turn.user_message, turn.assistant_message])
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Could not send the message.')
    } finally {
      setSending(false)
    }
  }

  return (
    <main className="app-shell">
      <header className="app-header">
        <div className="avatar" aria-hidden="true">C</div>
        <div><h1>Companion</h1><p>Here for a conversation</p></div>
      </header>
      {error && <div className="error-banner" role="alert">{error}</div>}
      <section className="chat-panel" aria-label="Chat">
        <MessageList messages={messages} loading={loading} />
        {sending && <div className="typing" role="status">Companion is thinking…</div>}
        <MessageInput disabled={loading || sending || !conversation} onSend={send} />
      </section>
      <footer>Conversations are stored locally on this device.</footer>
    </main>
  )
}
