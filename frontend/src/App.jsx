import React, { useState, useEffect } from 'react'
import Dashboard from './components/Dashboard'
import './App.css'

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>CRIS Dashboard</h1>
        <p>Live Data Visualization</p>
      </header>
      <main>
        <Dashboard />
      </main>
    </div>
  )
}

export default App

