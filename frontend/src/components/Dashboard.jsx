import React, { useState, useEffect } from 'react'
import Filters from './Filters'
import ChartView from './ChartView'
import { fetchVisualizationData } from '../services/api'
import './Dashboard.css'

const Dashboard = () => {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  
  const [filters, setFilters] = useState({
    measure: 'policies',
    period: 'month',
    numberOfPeriods: null
  })

  const fetchData = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await fetchVisualizationData(filters)
      setData(response.data)
    } catch (err) {
      setError(err.message || 'Failed to fetch data')
      console.error('Error fetching data:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [filters])

  const handleFilterChange = (newFilters) => {
    setFilters(prev => ({ ...prev, ...newFilters }))
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
          <button onClick={fetchData}>Retry</button>
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

