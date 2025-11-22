import React, { useState, useEffect, useRef } from 'react'
import Filters from './Filters'
import ChartView from './ChartView'
import InforceByLineView from './InforceByLineView'
import { SkeletonChart, SkeletonFilters } from './SkeletonLoader'
import LoadingBar from './LoadingBar'
import { fetchVisualizationData, fetchInforceByLine } from '../services/api'
import './Dashboard.css'

const Dashboard = () => {
  const [viewType, setViewType] = useState('time-based') // 'time-based' or 'inforce-by-line'
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const debounceTimer = useRef(null)
  
  const [filters, setFilters] = useState({
    measure: 'policies',
    period: 'month',
    numberOfPeriods: 10
  })
  
  const [chartType, setChartType] = useState('bar') // 'bar', 'line', 'area'
  const [inforceMetric, setInforceMetric] = useState('policy_count') // 'policy_count', 'premium', 'commission', 'avg_premium'

  const fetchData = async (currentFilters) => {
    setLoading(true)
    setError(null)
    
    try {
      // Validate and default numberOfPeriods only when fetching
      const numPeriods = parseInt(currentFilters.numberOfPeriods, 10)
      const filtersToUse = {
        ...currentFilters,
        numberOfPeriods: (!isNaN(numPeriods) && numPeriods > 0) ? numPeriods : 10
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

  const fetchInforceData = async (metricType) => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await fetchInforceByLine(metricType)
      setData(response.data)
    } catch (err) {
      setError(err.message || 'Failed to fetch inforce data')
      console.error('Error fetching inforce data:', err)
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
      if (viewType === 'time-based') {
        fetchData(filters)
      } else {
        fetchInforceData(inforceMetric)
      }
    }, 300) // 300ms debounce
    
    // Cleanup timer on unmount or filter change
    return () => {
      if (debounceTimer.current) {
        clearTimeout(debounceTimer.current)
      }
    }
  }, [filters, viewType, inforceMetric])

  const handleFilterChange = (newFilters) => {
    setFilters(prev => {
      const updated = { ...prev, ...newFilters }
      
      // Only validate numberOfPeriods on actual data fetch, not on every change
      // This allows for easier editing in the text input
      
      return updated
    })
  }

  const handleViewTypeChange = (newViewType) => {
    setViewType(newViewType)
    setData([]) // Clear data when switching views
  }

  const handleInforceMetricChange = (newMetric) => {
    setInforceMetric(newMetric)
  }

  return (
    <div className="dashboard">
      <LoadingBar loading={loading} />
      {/* View Type Selector */}
      <div className="view-selector">
        <label>View Type:</label>
        <button
          onClick={() => handleViewTypeChange('time-based')}
          style={{
            backgroundColor: viewType === 'time-based' ? 'var(--color-primary)' : 'transparent',
            color: viewType === 'time-based' ? 'white' : 'var(--text-primary)',
            borderColor: 'var(--color-primary)'
          }}
        >
          Time-Based Metrics
        </button>
        <button
          onClick={() => handleViewTypeChange('inforce-by-line')}
          style={{
            backgroundColor: viewType === 'inforce-by-line' ? 'var(--color-primary)' : 'transparent',
            color: viewType === 'inforce-by-line' ? 'white' : 'var(--text-primary)',
            borderColor: 'var(--color-primary)'
          }}
        >
          Inforce Metrics by Line
        </button>
      </div>

      {viewType === 'time-based' ? (
        <div data-view-transition>
          <Filters 
            filters={filters} 
            onFilterChange={handleFilterChange}
            chartType={chartType}
            onChartTypeChange={setChartType}
          />
          
          {loading && (
            <>
              <SkeletonFilters />
              <SkeletonChart />
            </>
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
              chartType={chartType}
            />
          )}
        </div>
      ) : (
        <div data-view-transition>
          {/* Inforce Metric Selector */}
          <div className="filters" style={{ marginBottom: '1rem' }}>
            <div className="filters-header">
              <h2>Inforce Metrics</h2>
            </div>
            <div className="filters-grid">
              <div className="filter-group">
                <label htmlFor="inforceMetric">Metric Type</label>
                <select 
                  id="inforceMetric" 
                  value={inforceMetric} 
                  onChange={(e) => handleInforceMetricChange(e.target.value)}
                >
                  <option value="policy_count">Policy Count (Inforce) by Line</option>
                  <option value="premium">Premium (Inforce) by Line</option>
                  <option value="commission">Commission (Inforce) by Line</option>
                  <option value="avg_premium">Average Premium (Inforce) by Line</option>
                </select>
              </div>
            </div>
          </div>

          {loading && (
            <div className="loading">
              <div className="spinner"></div>
              <p>Loading inforce data...</p>
            </div>
          )}
          
          {error && (
            <div className="error">
              <p>Error: {error}</p>
              <button onClick={() => fetchInforceData(inforceMetric)}>Retry</button>
            </div>
          )}
          
          {!loading && !error && (
            <InforceByLineView 
              data={data} 
              metricType={inforceMetric}
            />
          )}
        </div>
      )}
    </div>
  )
}

export default Dashboard

