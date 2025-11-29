'use client'

import { useState, useRef, useEffect } from 'react'
import { Send, Loader2 } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import axios from 'axios'

interface Message {
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Configure axios defaults
if (typeof window !== 'undefined') {
  axios.defaults.timeout = 60000 // 60 seconds
  axios.defaults.headers.common['Content-Type'] = 'application/json'
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: "Hello! I'm your dental practice assistant. How can I help you today?",
      timestamp: new Date(),
    },
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async () => {
    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    const messageToSend = input.trim()
    setInput('')
    setIsLoading(true)

    try {
      const conversationHistory = messages.map((msg) => ({
        role: msg.role,
        content: msg.content,
      }))

      // Create axios instance with timeout and better error handling
      const axiosInstance = axios.create({
        timeout: 60000, // 60 second timeout for LLM responses
        headers: {
          'Content-Type': 'application/json',
        },
      })

      const response = await axiosInstance.post(`${API_URL}/api/chat`, {
        message: messageToSend,
        conversation_history: conversationHistory,
      })

      if (response.data && response.data.response) {
        const assistantMessage: Message = {
          role: 'assistant',
          content: response.data.response,
          timestamp: new Date(),
        }
        setMessages((prev) => [...prev, assistantMessage])
      } else {
        throw new Error('Invalid response from server')
      }
    } catch (error: any) {
      console.error('Error sending message:', error)
      
      let errorContent = "I'm sorry, I'm having trouble processing your request right now."
      
      if (error.response) {
        // Server responded with error status
        const status = error.response.status
        const detail = error.response.data?.detail || error.response.data?.message || ''
        
        if (status === 402) {
          errorContent = "I'm temporarily unavailable due to API service issues. Please try again in a few moments, or contact us directly at +1-555-0123."
        } else if (status === 401) {
          errorContent = "There's an authentication issue. Please refresh the page and try again."
        } else if (status === 500) {
          errorContent = detail || "The server encountered an error. Please try again in a moment."
        } else if (status === 400) {
          errorContent = detail || "There was an issue with your request. Please try rephrasing your message."
        } else {
          errorContent = detail || `Server error (${status}). Please try again.`
        }
      } else if (error.request) {
        // Request was made but no response received
        if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
          errorContent = "The request took too long. This might be due to high demand. Please try again with a shorter message."
        } else {
          errorContent = "Unable to connect to the server. Please check your internet connection and try again."
        }
      } else {
        // Something else happened
        errorContent = error.message || "An unexpected error occurred. Please try again."
      }
      
      const errorMessage: Message = {
        role: 'assistant',
        content: errorContent,
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
      inputRef.current?.focus()
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="flex flex-col h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-surface/50 backdrop-blur-xl">
        <div className="max-w-4xl mx-auto px-6 py-4">
          <h1 className="text-xl font-semibold text-text">Premium Dental Care</h1>
          <p className="text-sm text-textSecondary mt-1">Intelligent Practice Assistant</p>
        </div>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-8">
        <div className="max-w-4xl mx-auto space-y-6">
          <AnimatePresence>
            {messages.map((message, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.2 }}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-2xl px-6 py-4 ${
                    message.role === 'user'
                      ? 'bg-accent text-white'
                      : 'bg-surfaceElevated text-text border border-border'
                  }`}
                >
                  <p className="text-[15px] leading-relaxed whitespace-pre-wrap">
                    {message.content}
                  </p>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>

          {isLoading && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex justify-start"
            >
              <div className="bg-surfaceElevated rounded-2xl px-6 py-4 border border-border">
                <Loader2 className="w-5 h-5 animate-spin text-textSecondary" />
              </div>
            </motion.div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input */}
      <div className="border-t border-border bg-surface/50 backdrop-blur-xl">
        <div className="max-w-4xl mx-auto px-6 py-4">
          <div className="flex items-end gap-3">
            <div className="flex-1 relative">
              <input
                ref={inputRef}
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Type your message..."
                disabled={isLoading}
                className="w-full bg-surfaceElevated border border-border rounded-2xl px-6 py-4 text-text placeholder-textSecondary focus:outline-none focus:ring-2 focus:ring-accent/50 focus:border-accent/50 disabled:opacity-50 disabled:cursor-not-allowed"
              />
            </div>
            <button
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
              className="bg-accent text-white rounded-2xl p-4 hover:bg-accent/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center min-w-[56px]"
            >
              {isLoading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Send className="w-5 h-5" />
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

