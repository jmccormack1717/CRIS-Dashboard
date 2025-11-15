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
    const value = e.target.value
    onFilterChange({ numberOfPeriods: value ? parseInt(value) || null : null })
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
            placeholder={`e.g., 6 for latest 6 ${filters.period}s`}
            value={filters.numberOfPeriods || ''}
            onChange={handleNumberOfPeriodsChange}
          />
          <small>Show latest N {filters.period}s (leave empty for all)</small>
        </div>
      </div>
    </div>
  )
}

export default Filters

