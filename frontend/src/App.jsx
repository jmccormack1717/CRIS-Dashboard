import React from 'react'
import Dashboard from './components/Dashboard'
import './App.css'

function App() {
  // Set navy theme on mount
  React.useEffect(() => {
    document.documentElement.setAttribute('data-theme', 'navy')
  }, [])

  return (
    <div className="App">
      <header className="App-header">
        <div className="header-content">
          <div>
            <h1>CRIS Dashboard</h1>
            <p>Live Data Visualization</p>
          </div>
        </div>
      </header>
      <main>
        <Dashboard />
      </main>
    </div>
  )
}

export default App

