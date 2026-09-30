import { useState, type FormEvent } from 'react'

interface MessageInputProps {
  disabled: boolean
  onSend: (content: string) => Promise<void>
}

export function MessageInput({ disabled, onSend }: MessageInputProps) {
  const [content, setContent] = useState('')

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const message = content.trim()
    if (!message || disabled) return
    setContent('')
    await onSend(message)
  }

  return (
    <form className="message-input" onSubmit={handleSubmit}>
      <label className="visually-hidden" htmlFor="message">Message</label>
      <textarea
        id="message"
        value={content}
        onChange={(event) => setContent(event.target.value)}
        onKeyDown={(event) => {
          if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault()
            event.currentTarget.form?.requestSubmit()
          }
        }}
        placeholder="Write a message…"
        rows={2}
        maxLength={20000}
        disabled={disabled}
      />
      <button type="submit" disabled={disabled || !content.trim()}>
        {disabled ? 'Sending…' : 'Send'}
      </button>
    </form>
  )
}
