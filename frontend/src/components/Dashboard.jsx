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
  const loadingTimeoutRef = useRef(null)
  
  // Safety check: ensure loading never gets stuck for more than 35 seconds
  useEffect(() => {
    if (loading) {
      // Clear any existing timeout
      if (loadingTimeoutRef.current) {
        clearTimeout(loadingTimeoutRef.current)
      }
      
      // Set a failsafe timeout to force loading to false
      loadingTimeoutRef.current = setTimeout(() => {
        if (loading && isMountedRef.current) {
          console.warn('[Dashboard] Failsafe triggered - loading state stuck, forcing to false')
          setLoading(false)
          setError('Loading timeout. Please refresh the page or try again.')
        }
      }, 35000)
    } else {
      // Clear timeout when loading becomes false
      if (loadingTimeoutRef.current) {
        clearTimeout(loadingTimeoutRef.current)
        loadingTimeoutRef.current = null
      }
    }
    
    // Cleanup on unmount
    return () => {
      if (loadingTimeoutRef.current) {
        clearTimeout(loadingTimeoutRef.current)
        loadingTimeoutRef.current = null
      }
    }
  }, [loading])

  const fetchData = async (currentFilters, requestId) => {
    // Check if this request is still valid before starting
    if (requestId !== requestIdRef.current || !isMountedRef.current) {
      return
    }
    
    // Loading is already set by the debounce timeout, just clear error
    setError(null)
    
    // Safety timeout: force loading to false after 30 seconds
    const timeoutId = setTimeout(() => {
      if (requestId === requestIdRef.current && isMountedRef.current) {
        console.warn('[Dashboard] Request timeout - forcing loading to false')
        setLoading(false)
        setError('Request timed out. Please try again.')
      }
    }, 30000)
    
    try {
      // Double-check request is still valid
      if (requestId !== requestIdRef.current || !isMountedRef.current) {
        clearTimeout(timeoutId)
        setLoading(false)
        return
      }
      
      // Validate numberOfPeriods - should already be validated before fetchData is called
      // But double-check here to be safe
      const numPeriods = parseInt(currentFilters.numberOfPeriods, 10)
      if (!currentFilters.numberOfPeriods || currentFilters.numberOfPeriods === '' || isNaN(numPeriods) || numPeriods <= 0) {
        console.log('[Dashboard] Invalid numberOfPeriods in fetchData, aborting')
        setLoading(false)
        return
      }
      const filtersToUse = {
        ...currentFilters,
        numberOfPeriods: numPeriods
      }
      
      const response = await fetchVisualizationData(filtersToUse)
      
      // Only update state if this is still the latest request
      if (requestId === requestIdRef.current && isMountedRef.current) {
        setData(response.data)
        setError(null)
        setLoading(false)
      } else {
        // Request was invalidated - ensure loading is cleared
        setLoading(false)
      }
    } catch (err) {
      // Only update error if this is still the latest request and not aborted
      if (requestId === requestIdRef.current && isMountedRef.current && err.name !== 'AbortError' && err.message !== 'canceled') {
        setError(err.message || 'Failed to fetch data')
        console.error('Error fetching data:', err)
      }
      // Always clear loading on error (unless request was invalidated and new one started)
      setLoading(false)
    } finally {
      clearTimeout(timeoutId)
      // Always ensure loading is false if this request is no longer valid
      if (requestId !== requestIdRef.current) {
        setLoading(false)
      }
    }
  }

  const fetchInforceData = async (metricType, requestId) => {
    // Check if this request is still valid before starting
    if (requestId !== requestIdRef.current || !isMountedRef.current) {
      setLoading(false)
      return
    }
    
    console.log('[Dashboard] fetchInforceData called with metricType:', metricType)
    // Loading is already set by the debounce timeout, just clear error
    setError(null)
    
    // Safety timeout: force loading to false after 30 seconds (inforce processing can take time)
    const timeoutId = setTimeout(() => {
      if (requestId === requestIdRef.current && isMountedRef.current) {
        console.warn('[Dashboard] Inforce request timeout - forcing loading to false')
        setLoading(false)
        setError('Request timed out. Please try again.')
      }
    }, 30000)
    
    try {
      // Double-check request is still valid
      if (requestId !== requestIdRef.current || !isMountedRef.current) {
        clearTimeout(timeoutId)
        setLoading(false)
        return
      }
      
      console.log('[Dashboard] Calling fetchInforceByLine...')
      const response = await fetchInforceByLine(metricType)
      console.log('[Dashboard] Received response:', response)
      
      // Only update state if this is still the latest request
      if (requestId === requestIdRef.current && isMountedRef.current) {
        setData(response.data || response)
        setError(null)
        setLoading(false)
      } else {
        // Request was invalidated - ensure loading is cleared
        setLoading(false)
      }
    } catch (err) {
      // Only update error if this is still the latest request and not aborted
      if (requestId === requestIdRef.current && isMountedRef.current && err.name !== 'AbortError' && err.message !== 'canceled') {
        console.error('[Dashboard] Error fetching inforce data:', err)
        setError(err.message || 'Failed to fetch inforce data')
      }
      // Always clear loading on error (unless request was invalidated and new one started)
      setLoading(false)
    } finally {
      clearTimeout(timeoutId)
      // Always ensure loading is false if this request is no longer valid
      if (requestId !== requestIdRef.current) {
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
    // For time-based view, use longer debounce to prevent loading flicker when typing/changing dropdowns
    const debounceDelay = viewType === 'inforce-by-line' ? 50 : 700
    
    // Debounce the API call to prevent rapid updates
    // Set loading only when the debounce timer actually fires, not immediately
    debounceTimer.current = setTimeout(() => {
      // Double-check this is still the latest request before making API call
      if (currentRequestId !== requestIdRef.current || !isMountedRef.current) {
        console.log('[Dashboard] Request outdated, skipping - clearing loading state')
        // Clear loading if this debounced request was cancelled
        if (isMountedRef.current) {
          setLoading(false)
        }
        return
      }
      
      // Only now set loading - right before making the API call
      // This prevents loading flicker when user is still typing or changing dropdowns
      setLoading(true)
      
      console.log('[Dashboard] Debounce timeout - calling API with viewType:', viewType)
      if (viewType === 'time-based') {
        // Validate numberOfPeriods before fetching - don't fetch if empty or invalid
        const numPeriods = parseInt(filters.numberOfPeriods, 10)
        if (!filters.numberOfPeriods || filters.numberOfPeriods === '' || isNaN(numPeriods) || numPeriods <= 0) {
          console.log('[Dashboard] numberOfPeriods is empty or invalid, skipping fetch')
          setLoading(false)
          return
        }
        console.log('[Dashboard] Fetching time-based data...')
        fetchData(filters, currentRequestId)
      } else {
        console.log('[Dashboard] Fetching inforce data with metric:', inforceMetric)
        // Ensure loading state is set before fetching
        if (isMountedRef.current && currentRequestId === requestIdRef.current) {
          fetchInforceData(inforceMetric, currentRequestId)
        } else {
          // Request was invalidated, clear loading
          setLoading(false)
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
      
      // Clear all timers
      if (debounceTimer.current) {
        clearTimeout(debounceTimer.current)
        debounceTimer.current = null
      }
      if (loadingTimeoutRef.current) {
        clearTimeout(loadingTimeoutRef.current)
        loadingTimeoutRef.current = null
      }
      
      // Ensure loading is cleared on unmount
      setLoading(false)
    }
  }, [])

  const handleFilterChange = (newFilters) => {
    // Invalidate any pending requests when changing filters
    requestIdRef.current += 1
    
    // Clear existing timer to ensure fresh fetch
    if (debounceTimer.current) {
      clearTimeout(debounceTimer.current)
      debounceTimer.current = null
    }
    
    // Don't set loading immediately - let the debounce timer handle it
    // This prevents loading flicker when typing in inputs
    
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
    
    // Ensure loading is cleared first, then set it immediately for smooth transition
    setLoading(false)
    // Use setTimeout to ensure state update happens after clearing
    setTimeout(() => {
      if (isMountedRef.current) {
        setLoading(true)
      }
    }, 0)
    
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
    
    // Ensure loading is cleared first, then set it immediately
    setLoading(false)
    // Use setTimeout to ensure state update happens after clearing
    setTimeout(() => {
      if (isMountedRef.current) {
        setLoading(true)
      }
    }, 0)
    
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
            onChartTypeChange={(newChartType) => {
              // Chart type change doesn't require data reload - just visualization change
              setChartType(newChartType)
            }}
            loading={loading}
          />
          
          {loading && (
            <div style={{ 
              padding: '2rem', 
              textAlign: 'center',
              minHeight: '400px',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              animation: 'fadeIn 0.3s ease-in'
            }}>
              <div className="spinner" style={{ 
                width: '40px', 
                height: '40px',
                marginBottom: '1rem'
              }}></div>
              <p style={{ fontSize: '1.1rem', marginTop: '1rem', color: 'var(--text-primary)' }}>
                Loading time-based metrics...
              </p>
              <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
                Processing {filters.measure} data for {filters.numberOfPeriods || 10} {filters.period}s
              </p>
            </div>
          )}
          
          {error && (
            <div className="error">
              <p>Error: {error}</p>
              <button onClick={() => {
                requestIdRef.current += 1
                setLoading(true)
                fetchData(filters, requestIdRef.current)
              }}>Retry</button>
            </div>
          )}
          
          {!loading && !error && data && data.length > 0 && (
            <ChartView 
              data={data} 
              measure={filters.measure}
              period={filters.period}
              chartType={chartType}
            />
          )}
          
          {!loading && !error && (!data || data.length === 0) && (
            <div className="no-data" style={{ 
              padding: '2rem', 
              textAlign: 'center',
              minHeight: '200px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <p>No data available for the selected filters</p>
            </div>
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
              justifyContent: 'center',
              animation: 'fadeIn 0.3s ease-in'
            }}>
              <div className="spinner" style={{ 
                width: '40px', 
                height: '40px',
                marginBottom: '1rem'
              }}></div>
              <p style={{ fontSize: '1.1rem', marginTop: '1rem', color: 'var(--text-primary)' }}>
                Loading inforce data...
              </p>
              <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
                Processing ~3960 policies (this may take a few seconds)
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


