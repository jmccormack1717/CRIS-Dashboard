import React from 'react'
import './Filters.css'

const Filters = ({ filters, onFilterChange, chartType, onChartTypeChange }) => {
  const handleMeasureChange = (e) => {
    onFilterChange({ measure: e.target.value })
  }

  const handlePeriodChange = (e) => {
    onFilterChange({ period: e.target.value })
  }
  
  const handleChartTypeChange = (e) => {
    if (onChartTypeChange) {
      onChartTypeChange(e.target.value)
    }
  }

  const handleNumberOfPeriodsChange = (e) => {
    const value = e.target.value.trim()
    
    // Allow empty input for easier editing
    if (value === '' || value === null || value === undefined) {
      onFilterChange({ numberOfPeriods: '' })
      return
    }
    
    // Parse the value
    const parsed = parseInt(value, 10)
    
    // If valid number and > 0, use it; otherwise pass the raw value to allow user to continue typing
    if (!isNaN(parsed) && parsed > 0) {
      onFilterChange({ numberOfPeriods: parsed })
    } else if (value === '-') {
      // Allow negative sign for easier editing
      onFilterChange({ numberOfPeriods: value })
    } else {
      // Allow partial input but don't submit invalid values
      onFilterChange({ numberOfPeriods: value })
    }
  }
  
  const handleNumberOfPeriodsBlur = (e) => {
    const value = e.target.value.trim()
    const parsed = parseInt(value, 10)
    
    // On blur, validate and set to 10 if invalid
    if (value === '' || isNaN(parsed) || parsed <= 0) {
      onFilterChange({ numberOfPeriods: 10 })
    } else {
      onFilterChange({ numberOfPeriods: parsed })
    }
  }

  return (
    <div className="filters">
      <div className="filters-header">
        <h2>Filters</h2>
      </div>
      
      <div className="filters-grid">
        <div className="filter-group">
          <label htmlFor="measure">Measure</label>
          <select 
            id="measure" 
            value={filters.measure} 
            onChange={handleMeasureChange}
          >
            <option value="policies">Policies</option>
            <option value="premium">Premium</option>
            <option value="commission">Commission</option>
          </select>
        </div>

        <div className="filter-group">
          <label htmlFor="period">Period</label>
          <select 
            id="period" 
            value={filters.period} 
            onChange={handlePeriodChange}
          >
            <option value="month">Month</option>
            <option value="quarter">Quarter</option>
            <option value="year">Year</option>
          </select>
        </div>

        <div className="filter-group">
          <label htmlFor="numberOfPeriods">Number of Periods</label>
          <input
            id="numberOfPeriods"
            type="text"
            placeholder="10"
            value={filters.numberOfPeriods ?? 10}
            onChange={handleNumberOfPeriodsChange}
            onBlur={handleNumberOfPeriodsBlur}
            inputMode="numeric"
          />
          <small>Show latest N {filters.period}s (default: 10)</small>
        </div>
        
        {chartType !== undefined && (
          <div className="filter-group">
            <label htmlFor="chartType">Chart Type</label>
            <select 
              id="chartType" 
              value={chartType} 
              onChange={handleChartTypeChange}
            >
              <option value="bar">Bar Chart</option>
              <option value="line">Line Chart</option>
              <option value="area">Area Chart</option>
            </select>
            <small>Visualization style</small>
          </div>
        )}
      </div>
    </div>
  )
}

export default Filters

