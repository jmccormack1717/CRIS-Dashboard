import React from 'react'
import './Filters.css'

const Filters = ({ filters, onFilterChange }) => {
  const handleMeasureChange = (e) => {
    onFilterChange({ measure: e.target.value })
  }

  const handlePeriodChange = (e) => {
    onFilterChange({ period: e.target.value })
  }

  const handleNumberOfPeriodsChange = (e) => {
    const value = e.target.value.trim()
    
    // If empty, default to 10
    if (value === '' || value === null || value === undefined) {
      onFilterChange({ numberOfPeriods: 10 })
      return
    }
    
    // Parse the value
    const parsed = parseInt(value, 10)
    
    // If valid number and > 0, use it; otherwise default to 10
    if (!isNaN(parsed) && parsed > 0) {
      onFilterChange({ numberOfPeriods: parsed })
    } else {
      // Invalid input, reset to 10
      onFilterChange({ numberOfPeriods: 10 })
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
            type="number"
            min="1"
            placeholder={`Default: 10 (latest 10 ${filters.period}s)`}
            value={filters.numberOfPeriods ?? 10}
            onChange={handleNumberOfPeriodsChange}
            onBlur={(e) => {
              // On blur, ensure value is valid or reset to 10
              const value = e.target.value.trim()
              if (value === '' || isNaN(parseInt(value, 10)) || parseInt(value, 10) <= 0) {
                onFilterChange({ numberOfPeriods: 10 })
              }
            }}
          />
          <small>Show latest N {filters.period}s (default: 10)</small>
        </div>
      </div>
    </div>
  )
}

export default Filters

