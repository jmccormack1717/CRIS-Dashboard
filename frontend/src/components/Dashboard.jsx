import React, { useState, useEffect, useRef } from 'react'
import Filters from './Filters'
import ChartView from './ChartView'
import { fetchVisualizationData } from '../services/api'
import './Dashboard.css'

const Dashboard = () => {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const debounceTimer = useRef(null)
  
  const [filters, setFilters] = useState({
    measure: 'policies',
    period: 'month',
    numberOfPeriods: 10
  })

  const fetchData = async (currentFilters) => {
    setLoading(true)
    setError(null)
    
    try {
      // Ensure numberOfPeriods defaults to 10
      const filtersToUse = {
        ...currentFilters,
        numberOfPeriods: currentFilters.numberOfPeriods && currentFilters.numberOfPeriods > 0 
          ? currentFilters.numberOfPeriods 
          : 10
      }
      
      const response = await fetchVisualizationData(filtersToUse)
      setData(response.data)
    } catch (err) {
      setError(err.message || 'Failed to fetch data')
      console.error('Error fetching data:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    // Clear any existing timer
    if (debounceTimer.current) {
      clearTimeout(debounceTimer.current)
    }
    
    // Debounce the API call to prevent rapid updates
    debounceTimer.current = setTimeout(() => {
      fetchData(filters)
    }, 300) // 300ms debounce
    
    // Cleanup timer on unmount or filter change
    return () => {
      if (debounceTimer.current) {
        clearTimeout(debounceTimer.current)
      }
    }
  }, [filters])

  const handleFilterChange = (newFilters) => {
    setFilters(prev => {
      const updated = { ...prev, ...newFilters }
      
      // Ensure numberOfPeriods is always valid (default to 10)
      if (!updated.numberOfPeriods || updated.numberOfPeriods <= 0) {
        updated.numberOfPeriods = 10
      }
      
      return updated
    })
  }

  return (
    <div className="dashboard">
      <Filters 
        filters={filters} 
        onFilterChange={handleFilterChange}
      />
      
      {loading && (
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading data...</p>
        </div>
      )}
      
      {error && (
        <div className="error">
          <p>Error: {error}</p>
          <button onClick={() => fetchData(filters)}>Retry</button>
        </div>
      )}
      
      {!loading && !error && (
        <ChartView 
          data={data} 
          measure={filters.measure}
          period={filters.period}
        />
      )}
    </div>
  )
}

export default Dashboard

