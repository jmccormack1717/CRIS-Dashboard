import React, { createContext, useContext, useState, useEffect } from 'react'

const AuthContext = createContext(null)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [loading, setLoading] = useState(true)

  // Check for existing session on mount
  useEffect(() => {
    const stored = localStorage.getItem('cris_authenticated')
    if (stored === 'true') {
      setIsAuthenticated(true)
    }
    setLoading(false)
  }, [])

  const login = (username, password) => {
    // Validate credentials
    const validUsername = 'robs@crgholdings.com'
    const validPassword = 'vjdj8tq4!CRIS'
    
    // Normalize username/email (case-insensitive)
    const normalizedUsername = username.toLowerCase().trim()
    const normalizedValidUsername = validUsername.toLowerCase().trim()
    
    if (normalizedUsername === normalizedValidUsername && password === validPassword) {
      setIsAuthenticated(true)
      localStorage.setItem('cris_authenticated', 'true')
      return { success: true }
    } else {
      return { 
        success: false, 
        error: 'Invalid username or password' 
      }
    }
  }

  const logout = () => {
    setIsAuthenticated(false)
    localStorage.removeItem('cris_authenticated')
  }

  const value = {
    isAuthenticated,
    loading,
    login,
    logout
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

