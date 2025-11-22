import React, { useState } from 'react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell
} from 'recharts'
import './ChartView.css'
import './ChartHoverFix.css'
import './InforceByLineView.css'

// Sleek Navy Theme Colors
const NAVY_COLORS = [
  '#3b82f6',  // Bright blue
  '#0ea5e9',  // Sky blue
  '#60a5fa',  // Light blue
  '#06b6d4',  // Cyan
  '#14b8a6',  // Teal
  '#6366f1',  // Indigo
  '#1e40af'   // Deep navy
]

const InforceByLineView = ({ data, metricType, loading }) => {
  const [showTable, setShowTable] = useState(false)

  // Handle empty data - but only if not loading (to prevent showing "No data" during fetch)
  // Pass loading prop from parent to know if we're still fetching
  if (!loading && (!data || data.length === 0)) {
    return (
      <div className="inforce-view">
        <div className="no-data">
          <p>No inforce data available</p>
        </div>
      </div>
    )
  }
  
  // If loading, don't render the main content yet
  if (loading && (!data || data.length === 0)) {
    return null // Loading state is handled by parent component
  }

  const formatValue = (value) => {
    if (value === null || value === undefined || isNaN(value)) {
      return '0'
    }
    if (metricType === 'premium' || metricType === 'commission' || metricType === 'avg_premium') {
      // Round to nearest dollar (no cents)
      return `$${Math.round(value).toLocaleString()}`
    }
    return value.toLocaleString()
  }

  const formatPercent = (value) => {
    if (value === null || value === undefined || isNaN(value)) {
      return '0.00%'
    }
    return `${Number(value).toFixed(2)}%`
  }

  const getTitle = () => {
    switch (metricType) {
      case 'policy_count':
        return 'Policy Count (Inforce) by Line'
      case 'premium':
        return 'Premium (Inforce) by Line'
      case 'commission':
        return 'Commission (Inforce) by Line'
      case 'avg_premium':
        return 'Average Premium (Inforce) by Line'
      default:
        return 'Inforce Metrics by Line'
    }
  }

  // Calculate totals for summary
  const totalValue = data.reduce((sum, item) => sum + item.value, 0)
  const totalCount = data.reduce((sum, item) => sum + (item.count || 0), 0)
  
  // Get top line (highest value)
  const topLine = data.length > 0 ? data.reduce((max, item) => 
    item.value > max.value ? item : max
  , data[0]) : null
  
  // Get number of lines
  const numberOfLines = data.length

  return (
    <div className="inforce-view" style={{ animation: 'fadeInUp 0.6s ease-out' }}>
      {/* Summary Cards */}
      <div className="inforce-summary-cards">
        <div className="summary-card">
          <div className="summary-card-label">Total {metricType === 'policy_count' ? 'Policies' : metricType === 'premium' ? 'Premium' : metricType === 'commission' ? 'Commission' : 'Average Premium'}</div>
          <div className="summary-card-value">
            {metricType === 'avg_premium' 
              ? formatValue(data.length > 0 ? totalValue / data.length : 0)
              : formatValue(totalValue)
            }
          </div>
        </div>

        {metricType !== 'policy_count' && metricType !== 'avg_premium' && (
          <div className="summary-card">
            <div className="summary-card-label">Total Policies</div>
            <div className="summary-card-value">{totalCount.toLocaleString()}</div>
          </div>
        )}

        {metricType === 'avg_premium' && (
          <div className="summary-card">
            <div className="summary-card-label">Total Policies</div>
            <div className="summary-card-value">{totalCount.toLocaleString()}</div>
          </div>
        )}

        {topLine && (
          <div className="summary-card">
            <div className="summary-card-label">Top Line</div>
            <div className="summary-card-value-name">{topLine.line}</div>
            <div className="summary-card-value-sub">
              {formatValue(topLine.value)}
              {metricType !== 'avg_premium' && (
                <span className="summary-card-percent"> ({formatPercent(topLine.percent)})</span>
              )}
            </div>
          </div>
        )}

        <div className="summary-card">
          <div className="summary-card-label">Number of Lines</div>
          <div className="summary-card-value">{numberOfLines}</div>
        </div>
      </div>

      {/* Chart Section */}
      <div className="chart-view">
        <div className="chart-header">
          <h2>{getTitle()}</h2>
        </div>

        <div className="chart-container">
          {data.length > 0 ? (
            <>
              {/* Bar Chart for all metric types */}
              <ResponsiveContainer width="100%" height={400}>
                <BarChart 
                  data={data} 
                  margin={{ top: 20, right: 30, left: 20, bottom: 100 }}
                  onMouseEnter={() => {}}
                  onMouseLeave={() => {}}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="line" 
                    angle={-45}
                    textAnchor="end"
                    height={100}
                    stroke="var(--text-tertiary)"
                    tick={{ fill: 'var(--text-secondary)' }}
                  />
                  <YAxis 
                    tickFormatter={(value) => {
                      if (metricType === 'premium' || metricType === 'commission' || metricType === 'avg_premium') {
                        return `$${(value / 1000).toFixed(0)}k`
                      }
                      return value.toLocaleString()
                    }}
                    stroke="var(--text-tertiary)"
                    tick={{ fill: 'var(--text-secondary)' }}
                  />
                  <CartesianGrid 
                    strokeDasharray="3 3" 
                    stroke="var(--color-primary)" 
                    strokeOpacity={0.2} 
                  />
                  <Tooltip 
                    formatter={(value, name) => {
                      if (name === 'value') {
                        return formatValue(value)
                      }
                      return value
                    }}
                    labelStyle={{ color: 'var(--color-accent)' }}
                    contentStyle={{ 
                      backgroundColor: document.documentElement.getAttribute('data-theme') === 'light' 
                        ? 'rgba(255, 255, 255, 0.98)' 
                        : 'rgba(51, 65, 85, 0.98)', 
                      border: '1px solid rgba(59, 130, 246, 0.3)',
                      borderRadius: '8px',
                      color: 'var(--text-primary)',
                      backdropFilter: 'blur(10px)',
                      WebkitBackdropFilter: 'blur(10px)',
                      boxShadow: document.documentElement.getAttribute('data-theme') === 'light'
                        ? '0 4px 12px rgba(0, 0, 0, 0.1)'
                        : '0 4px 12px rgba(0, 0, 0, 0.3)'
                    }}
                    cursor={false}
                  />
                  <Legend 
                    wrapperStyle={{ 
                      color: 'var(--text-secondary)'
                    }} 
                  />
                  <Bar 
                    dataKey="value" 
                    name={metricType === 'policy_count' ? 'Policy Count' : 
                          metricType === 'premium' ? 'Premium' :
                          metricType === 'commission' ? 'Commission' :
                          'Average Premium'}
                    radius={[8, 8, 0, 0]}
                    cursor="default"
                    activeBar={null}
                    isAnimationActive={false}
                  >
                    {data.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={NAVY_COLORS[index % NAVY_COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>

              {/* Optional Details Table */}
              <div className="inforce-table-toggle">
                <button 
                  className="toggle-table-btn"
                  onClick={() => setShowTable(!showTable)}
                >
                  {showTable ? '▼ Hide Details' : '▶ Show Details Table'}
                </button>
              </div>

              {showTable && (
                <div className="inforce-table-container">
                  <div className="table-wrapper">
                    <table className="inforce-table">
                      <thead>
                        <tr>
                          <th>Line</th>
                          <th className="text-right">
                            {metricType === 'policy_count' ? 'Count' : metricType === 'premium' ? 'Premium' : metricType === 'commission' ? 'Commission' : 'Average Premium'}
                          </th>
                          {metricType !== 'avg_premium' && (
                            <th className="text-right">Percent</th>
                          )}
                          {metricType !== 'policy_count' && (
                            <th className="text-right">Policy Count</th>
                          )}
                        </tr>
                      </thead>
                      <tbody>
                        {data.map((item, index) => (
                          <tr key={index}>
                            <td>{item.line}</td>
                            <td className="text-right">{formatValue(item.value)}</td>
                            {metricType !== 'avg_premium' && (
                              <td className="text-right">{formatPercent(item.percent)}</td>
                            )}
                            {metricType !== 'policy_count' && (
                              <td className="text-right">{item.count.toLocaleString()}</td>
                            )}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="no-data">
              <p>No inforce data available</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default InforceByLineView

