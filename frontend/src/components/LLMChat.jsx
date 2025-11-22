import React, { useState, useRef, useEffect } from 'react'
import { askLLMQuestion } from '../services/api'
import './LLMChat.css'

const LLMChat = ({ dashboardState }) => {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [isMinimized, setIsMinimized] = useState(true)
  const [isExpanded, setIsExpanded] = useState(false)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)
  
  // Strip markdown formatting from text
  const stripMarkdown = (text) => {
    if (!text) return text
    
    // Remove markdown headers (##, ###, etc.)
    text = text.replace(/^#{1,6}\s+/gm, '')
    
    // Remove bold/italic markers
    text = text.replace(/\*\*([^*]+)\*\*/g, '$1')
    text = text.replace(/\*([^*]+)\*/g, '$1')
    text = text.replace(/__([^_]+)__/g, '$1')
    text = text.replace(/_([^_]+)_/g, '$1')
    
    // Remove links but keep text
    text = text.replace(/\[([^\]]+)\]\([^\)]+\)/g, '$1')
    
    // Remove code blocks
    text = text.replace(/```[\s\S]*?```/g, '')
    text = text.replace(/`([^`]+)`/g, '$1')
    
    // Remove bullet points and list markers
    text = text.replace(/^[\s]*[-*+]\s+/gm, '')
    text = text.replace(/^\d+\.\s+/gm, '')
    
    // Clean up extra whitespace
    text = text.replace(/\n{3,}/g, '\n\n')
    
    return text.trim()
  }

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

      // Strip markdown and technical jargon from response
      let cleanedResponse = stripMarkdown(response.response)
      
      // Remove any mentions of JSON, data, queries, backend, API
      cleanedResponse = cleanedResponse
        .replace(/\bJSON\b/gi, 'data')
        .replace(/\bfrom the data\b/gi, '')
        .replace(/\blooking at the data\b/gi, '')
        .replace(/\bthe data shows\b/gi, 'the information shows')
        .replace(/\bexamining the data\b/gi, '')
      
      // Add assistant response
      const assistantMessage = {
        role: 'assistant',
        content: cleanedResponse,
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
    <div className={`llm-chat ${isExpanded ? 'llm-chat-expanded' : ''}`}>
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
            className="llm-chat-expand"
            onClick={() => setIsExpanded(!isExpanded)}
            title={isExpanded ? "Shrink" : "Expand to fullscreen"}
          >
            {isExpanded ? (
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M8 3V5M8 21V19M16 3V5M16 21V19M3 8H5M3 16H5M19 8H21M19 16H21M4 8V16C4 17.1046 4.89543 18 6 18H18C19.1046 18 20 17.1046 20 16V8C20 6.89543 19.1046 6 18 6H6C4.89543 6 4 6.89543 4 8Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            ) : (
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M8 3H5C3.89543 3 3 3.89543 3 5V8M21 8V5C21 3.89543 20.1046 3 19 3H16M16 21H19C20.1046 21 21 20.1046 21 19V16M3 16V19C3 20.1046 3.89543 21 5 21H8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            )}
          </button>
          <button 
            className="llm-chat-minimize"
            onClick={() => {
              setIsMinimized(true)
              setIsExpanded(false)
            }}
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
              {message.content.split('\n').map((line, i, arr) => {
                // Skip completely empty lines, but preserve spacing between paragraphs
                if (!line.trim()) {
                  // Only add spacing if there's content before and after
                  const hasContentBefore = arr.slice(0, i).some(l => l.trim())
                  const hasContentAfter = arr.slice(i + 1).some(l => l.trim())
                  if (hasContentBefore && hasContentAfter) {
                    return <br key={i} />
                  }
                  return null
                }
                return <p key={i}>{line}</p>
              })}
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

