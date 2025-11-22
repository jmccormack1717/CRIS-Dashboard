import React, { useState, useRef, useEffect } from 'react'
import { askLLMQuestion } from '../services/api'
import './LLMChat.css'

const LLMChat = ({ dashboardState }) => {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [isMinimized, setIsMinimized] = useState(true)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Auto-resize textarea
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.style.height = 'auto'
      const scrollHeight = inputRef.current.scrollHeight
      const maxHeight = 200 // Maximum height in pixels (roughly 8-9 lines)
      inputRef.current.style.height = `${Math.min(scrollHeight, maxHeight)}px`
    }
  }, [input])

  const handleSend = async () => {
    if (!input.trim() || loading) return

    const userMessage = input.trim()
    setInput('')
    setLoading(true)

    // Add user message
    const newUserMessage = {
      role: 'user',
      content: userMessage,
      timestamp: new Date()
    }
    setMessages(prev => [...prev, newUserMessage])

    try {
      // Prepare conversation history
      const conversationHistory = messages.map(msg => ({
        role: msg.role,
        content: msg.content
      }))

      // Call LLM API
      const response = await askLLMQuestion(
        userMessage,
        dashboardState,
        conversationHistory
      )

      // Add assistant response
      const assistantMessage = {
        role: 'assistant',
        content: response.response,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      const errorMessage = {
        role: 'assistant',
        content: `Error: ${error.message || 'Failed to get response'}`,
        timestamp: new Date(),
        isError: true
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
      inputRef.current?.focus()
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleClear = () => {
    setMessages([])
  }

  if (isMinimized) {
    return (
      <div className="llm-chat-minimized">
        <button 
          className="llm-chat-toggle"
          onClick={() => setIsMinimized(false)}
          title="Open AI Assistant"
        >
          💬 Ask about your data
        </button>
      </div>
    )
  }

  return (
    <div className="llm-chat">
      <div className="llm-chat-header">
        <div className="llm-chat-title">
          <span>🤖</span>
          <span>AI Assistant</span>
        </div>
        <div className="llm-chat-actions">
          <button 
            className="llm-chat-clear"
            onClick={handleClear}
            title="Clear conversation"
          >
            Clear
          </button>
          <button 
            className="llm-chat-minimize"
            onClick={() => setIsMinimized(true)}
            title="Minimize"
          >
            −
          </button>
        </div>
      </div>

      <div className="llm-chat-messages">
        {messages.length === 0 && (
          <div className="llm-chat-welcome">
            <p>👋 Ask me anything about your dashboard data!</p>
            <p className="llm-chat-suggestions">
              Try: "What's the trend in policies?", "Which line has the highest premium?", 
              or "Summarize the current view"
            </p>
          </div>
        )}
        
        {messages.map((message, index) => (
          <div 
            key={index} 
            className={`llm-chat-message llm-chat-message-${message.role} ${message.isError ? 'llm-chat-error' : ''}`}
          >
            <div className="llm-chat-message-content">
              {message.content.split('\n').map((line, i) => (
                <p key={i}>{line}</p>
              ))}
            </div>
            <div className="llm-chat-message-time">
              {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </div>
          </div>
        ))}
        
        {loading && (
          <div className="llm-chat-message llm-chat-message-assistant">
            <div className="llm-chat-loading">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      <div className="llm-chat-input-container">
        <div className="llm-chat-input-wrapper">
          <textarea
            ref={inputRef}
            className="llm-chat-input"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about your data..."
            rows={1}
            disabled={loading}
          />
          <button
            className={`llm-chat-send ${input.trim() && !loading ? 'llm-chat-send-active' : ''}`}
            onClick={handleSend}
            disabled={!input.trim() || loading}
            title="Send message (Enter)"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M22 2L11 13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M22 2L15 22L11 13L2 9L22 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
  )
}

export default LLMChat

