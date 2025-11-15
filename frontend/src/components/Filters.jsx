import React from 'react'
import './Filters.css'

const Filters = ({ filters, onFilterChange }) => {
  const handleMeasureChange = (e) => {
    onFilterChange({ measure: e.target.value })
  }

  const handlePeriodChange = (e) => {
    onFilterChange({ period: e.target.value })
  }

  const handleSinceTimeChange = (e) => {
    onFilterChange({ sinceTime: e.target.value || null })
  }

  const handleStartDateChange = (e) => {
    onFilterChange({ startDate: e.target.value || null })
  }

  const handleEndDateChange = (e) => {
    onFilterChange({ endDate: e.target.value || null })
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
          <label htmlFor="sinceTime">Since Time</label>
          <input
            id="sinceTime"
            type="text"
            placeholder="e.g., 30days, 6months, 2024-01-01"
            value={filters.sinceTime || ''}
            onChange={handleSinceTimeChange}
          />
          <small>Examples: 30days, 6months, 1year, 2024-01-01</small>
        </div>

        <div className="filter-group">
          <label htmlFor="startDate">Start Date</label>
          <input
            id="startDate"
            type="date"
            value={filters.startDate || ''}
            onChange={handleStartDateChange}
          />
        </div>

        <div className="filter-group">
          <label htmlFor="endDate">End Date</label>
          <input
            id="endDate"
            type="date"
            value={filters.endDate || ''}
            onChange={handleEndDateChange}
          />
        </div>
      </div>
    </div>
  )
}

export default Filters

