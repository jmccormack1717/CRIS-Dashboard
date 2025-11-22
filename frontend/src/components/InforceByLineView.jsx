import React, { useState } from 'react'
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
  LabelList
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

const InforceByLineView = ({ data, metricType }) => {
  const [showTable, setShowTable] = useState(false)

  // Handle empty data
  if (!data || data.length === 0) {
    return (
      <div className="inforce-view">
        <div className="no-data">
          <p>No inforce data available</p>
        </div>
      </div>
    )
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
              {/* Pie Chart for policy_count, premium, commission | Bar Chart for avg_premium */}
              {metricType === 'avg_premium' ? (
                // Bar Chart for Average Premium
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
                        return `$${(value / 1000).toFixed(0)}k`
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
                        backgroundColor: 'var(--bg-secondary)', 
                        border: '1px solid var(--border-color)',
                        borderRadius: '8px',
                        color: 'var(--text-primary)',
                        backdropFilter: 'blur(10px)',
                        WebkitBackdropFilter: 'blur(10px)',
                        boxShadow: '0 4px 12px var(--shadow)'
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
                      name="Average Premium"
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
              ) : (
                // Pie Chart for Policy Count, Premium, Commission
                <ResponsiveContainer width="100%" height={400}>
                  <PieChart>
                    <Pie
                      data={data}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ line, percent }) => `${line}: ${(percent * 100).toFixed(1)}%`}
                      outerRadius={120}
                      fill="#8884d8"
                      dataKey="value"
                      nameKey="line"
                      cursor="default"
                      isAnimationActive={false}
                    >
                      {data.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={NAVY_COLORS[index % NAVY_COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip 
                      formatter={(value, name, props) => {
                        const item = props.payload
                        return [
                          `${formatValue(value)} (${formatPercent(item.percent)})`,
                          item.line
                        ]
                      }}
                      contentStyle={{ 
                        backgroundColor: 'var(--bg-secondary)', 
                        border: '1px solid var(--border-color)',
                        borderRadius: '8px',
                        color: 'var(--text-primary)',
                        backdropFilter: 'blur(10px)',
                        WebkitBackdropFilter: 'blur(10px)',
                        boxShadow: '0 4px 12px var(--shadow)'
                      }}
                      labelStyle={{ color: 'var(--color-accent)' }}
                      cursor={false}
                    />
                    <Legend 
                      formatter={(value, entry) => {
                        const item = data.find(d => d.line === value)
                        return item ? `${value}: ${formatValue(item.value)} (${formatPercent(item.percent)})` : value
                      }}
                      wrapperStyle={{ 
                        color: 'var(--text-secondary)',
                        paddingTop: '20px'
                      }} 
                    />
                  </PieChart>
                </ResponsiveContainer>
              )}

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

