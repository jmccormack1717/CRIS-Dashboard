import React from 'react'
import { ThemeProvider } from './contexts/ThemeContext'
import Dashboard from './components/Dashboard'
import ThemeToggle from './components/ThemeToggle'
import './App.css'

function App() {
  return (
    <ThemeProvider>
      <div className="App">
      <header className="App-header">
        <div className="header-actions">
          <ThemeToggle />
        </div>
        <div className="header-content">
          <div className="header-title-section">
            <h1>CRIS Dashboard</h1>
            <p>Live Data Visualization</p>
          </div>
        </div>
      </header>
        <main>
          <Dashboard />
        </main>
      </div>
    </ThemeProvider>
  )
}

export default App

