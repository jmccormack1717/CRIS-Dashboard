import React, { useState, useEffect, useRef } from 'react'
import Filters from './Filters'
import ChartView from './ChartView'
import InforceByLineView from './InforceByLineView'
import { SkeletonChart, SkeletonFilters } from './SkeletonLoader'
import LoadingBar from './LoadingBar'
import LLMChat from './LLMChat'
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
  
  // Track requests to prevent race conditions
  const requestIdRef = useRef(0)
  const isMountedRef = useRef(true)

  const fetchData = async (currentFilters, requestId) => {
    // Only proceed if this is still the latest request
    if (requestId !== requestIdRef.current || !isMountedRef.current) {
      return
    }
    
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
      
      // Only update state if this is still the latest request
      if (requestId === requestIdRef.current && isMountedRef.current) {
        setData(response.data)
        setError(null)
      }
    } catch (err) {
      // Only update error if this is still the latest request and not aborted
      if (requestId === requestIdRef.current && isMountedRef.current && err.name !== 'AbortError' && err.message !== 'canceled') {
        setError(err.message || 'Failed to fetch data')
        console.error('Error fetching data:', err)
      }
    } finally {
      // Only update loading if this is still the latest request
      if (requestId === requestIdRef.current && isMountedRef.current) {
        setLoading(false)
      }
    }
  }

  const fetchInforceData = async (metricType, requestId) => {
    // Only proceed if this is still the latest request
    if (requestId !== requestIdRef.current || !isMountedRef.current) {
      return
    }
    
    console.log('[Dashboard] fetchInforceData called with metricType:', metricType)
    setLoading(true)
    setError(null)
    
    try {
      console.log('[Dashboard] Calling fetchInforceByLine...')
      const response = await fetchInforceByLine(metricType)
      console.log('[Dashboard] Received response:', response)
      
      // Only update state if this is still the latest request
      if (requestId === requestIdRef.current && isMountedRef.current) {
        setData(response.data || response)
        setError(null)
      }
    } catch (err) {
      // Only update error if this is still the latest request and not aborted
      if (requestId === requestIdRef.current && isMountedRef.current && err.name !== 'AbortError' && err.message !== 'canceled') {
        console.error('[Dashboard] Error fetching inforce data:', err)
        setError(err.message || 'Failed to fetch inforce data')
      }
    } finally {
      // Only update loading if this is still the latest request
      if (requestId === requestIdRef.current && isMountedRef.current) {
        setLoading(false)
      }
    }
  }

  useEffect(() => {
    isMountedRef.current = true
    console.log('[Dashboard] useEffect triggered - viewType:', viewType, 'inforceMetric:', inforceMetric, 'filters:', filters)
    
    // Clear any existing timer to ensure fresh fetch
    if (debounceTimer.current) {
      clearTimeout(debounceTimer.current)
      debounceTimer.current = null
    }
    
    // Increment request ID to invalidate any previous requests
    requestIdRef.current += 1
    const currentRequestId = requestIdRef.current
    
    // For inforce view, use shorter debounce to ensure smooth experience
    // For time-based view, use normal debounce
    const debounceDelay = viewType === 'inforce-by-line' ? 50 : 300
    
    // Debounce the API call to prevent rapid updates
    debounceTimer.current = setTimeout(() => {
      // Double-check this is still the latest request before making API call
      if (currentRequestId !== requestIdRef.current || !isMountedRef.current) {
        console.log('[Dashboard] Request outdated, skipping')
        return
      }
      
      console.log('[Dashboard] Debounce timeout - calling API with viewType:', viewType)
      if (viewType === 'time-based') {
        console.log('[Dashboard] Fetching time-based data...')
        fetchData(filters, currentRequestId)
      } else {
        console.log('[Dashboard] Fetching inforce data with metric:', inforceMetric)
        // Ensure loading state is set before fetching
        if (isMountedRef.current && currentRequestId === requestIdRef.current) {
          fetchInforceData(inforceMetric, currentRequestId)
        }
      }
    }, debounceDelay)
    
    // Cleanup timer on unmount or filter change
    return () => {
      // Increment request ID to invalidate any pending requests
      requestIdRef.current += 1
      
      // Clear debounce timer
      if (debounceTimer.current) {
        clearTimeout(debounceTimer.current)
        debounceTimer.current = null
      }
    }
  }, [filters, viewType, inforceMetric])
  
  // Cleanup on unmount
  useEffect(() => {
    return () => {
      isMountedRef.current = false
      requestIdRef.current += 1
      if (debounceTimer.current) {
        clearTimeout(debounceTimer.current)
      }
    }
  }, [])

  const handleFilterChange = (newFilters) => {
    setFilters(prev => {
      const updated = { ...prev, ...newFilters }
      
      // Only validate numberOfPeriods on actual data fetch, not on every change
      // This allows for easier editing in the text input
      
      return updated
    })
  }

  const handleViewTypeChange = (newViewType) => {
    console.log('[Dashboard] handleViewTypeChange called with:', newViewType)
    
    // Invalidate any pending requests when switching views
    requestIdRef.current += 1
    
    // Clear existing timer to ensure fresh fetch
    if (debounceTimer.current) {
      clearTimeout(debounceTimer.current)
      debounceTimer.current = null
    }
    
    // Clear data and error immediately
    setData([]) // Clear data when switching views
    setError(null) // Clear errors when switching views
    
    // If switching to inforce view, immediately set loading to prevent showing "No data available"
    if (newViewType === 'inforce-by-line') {
      setLoading(true)
    }
    
    // Update view type - this will trigger useEffect which will handle the fetch
    setViewType(newViewType)
  }

  const handleInforceMetricChange = (newMetric) => {
    // Invalidate any pending requests when changing metric
    requestIdRef.current += 1
    
    // Clear existing timer to ensure fresh fetch
    if (debounceTimer.current) {
      clearTimeout(debounceTimer.current)
      debounceTimer.current = null
    }
    
    // Set loading immediately when changing metric to prevent showing stale data
    setLoading(true)
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
          disabled={loading && viewType !== 'inforce-by-line'}
          style={{
            backgroundColor: viewType === 'inforce-by-line' ? 'var(--color-primary)' : 'transparent',
            color: viewType === 'inforce-by-line' ? 'white' : 'var(--text-primary)',
            borderColor: 'var(--color-primary)',
            opacity: (loading && viewType !== 'inforce-by-line') ? 0.5 : 1,
            cursor: (loading && viewType !== 'inforce-by-line') ? 'not-allowed' : 'pointer'
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
              <button onClick={() => {
                requestIdRef.current += 1
                fetchData(filters, requestIdRef.current)
              }}>Retry</button>
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
                  disabled={loading}
                  style={{
                    opacity: loading ? 0.6 : 1,
                    cursor: loading ? 'wait' : 'pointer'
                  }}
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
            <div className="loading" style={{ 
              padding: '2rem', 
              textAlign: 'center',
              minHeight: '200px',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <div className="spinner" style={{ 
                width: '40px', 
                height: '40px',
                marginBottom: '1rem'
              }}></div>
              <p style={{ fontSize: '1.1rem', marginTop: '1rem' }}>
                Loading inforce data...
              </p>
              <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
                Processing policies (this may take a few seconds)
              </p>
            </div>
          )}
          
          {error && (
            <div className="error">
              <p>Error: {error}</p>
              <button onClick={() => {
                requestIdRef.current += 1
                fetchInforceData(inforceMetric, requestIdRef.current)
              }}>Retry</button>
            </div>
          )}
          
          {!loading && !error && data && data.length > 0 && (
            <InforceByLineView 
              data={data} 
              metricType={inforceMetric}
              loading={loading}
            />
          )}
          
          {!loading && !error && (!data || data.length === 0) && (
            <div className="inforce-view">
              <div className="no-data">
                <p>No inforce data available</p>
              </div>
            </div>
          )}
        </div>
      )}
      
      {/* LLM Chat Assistant */}
      <LLMChat 
        dashboardState={{
          view_type: viewType,
          measure: filters.measure,
          period: filters.period,
          number_of_periods: filters.numberOfPeriods || 10,
          metric_type: inforceMetric,
          data: data,
          chart_type: chartType
        }}
      />
    </div>
  )
}

export default Dashboard


