import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import App from './App'

afterEach(() => { cleanup(); vi.restoreAllMocks(); window.localStorage.clear() })

const conversation = { id: 'conversation-1', created_at: '2026-01-01T00:00:00Z', updated_at: '2026-01-01T00:00:00Z' }

describe('chat interface', () => {
  it('renders the chat and sends a message, displaying both replies', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch')
      .mockResolvedValueOnce(new Response(JSON.stringify(conversation), { status: 201 }))
      .mockResolvedValueOnce(new Response('[]', { status: 200 }))
      .mockResolvedValueOnce(new Response(JSON.stringify({
        user_message: { id: 'm1', conversation_id: conversation.id, role: 'user', content: 'Hello there', created_at: '2026-01-01T00:00:01Z' },
        assistant_message: { id: 'm2', conversation_id: conversation.id, role: 'assistant', content: 'I hear you: Hello there', created_at: '2026-01-01T00:00:02Z' },
      }), { status: 201 }))

    render(<App />)
    expect(screen.getByRole('heading', { name: 'Companion' })).toBeInTheDocument()
    const input = await screen.findByLabelText('Message')
    await userEvent.type(input, 'Hello there')
    await userEvent.click(screen.getByRole('button', { name: 'Send' }))

    expect(await screen.findByText('Hello there')).toBeInTheDocument()
    expect(await screen.findByText('I hear you: Hello there')).toBeInTheDocument()
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(3))
  })

  it('shows a backend connection error', async () => {
    vi.spyOn(globalThis, 'fetch').mockRejectedValue(new TypeError('offline'))
    render(<App />)
    expect(await screen.findByRole('alert')).toHaveTextContent('Could not reach the backend')
  })
})
