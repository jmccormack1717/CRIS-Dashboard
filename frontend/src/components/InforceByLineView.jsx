import React from 'react'
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
  const formatValue = (value) => {
    if (metricType === 'premium' || metricType === 'commission' || metricType === 'avg_premium') {
      // Round to nearest dollar (no cents)
      return `$${Math.round(value).toLocaleString()}`
    }
    return value.toLocaleString()
  }

  const formatPercent = (value) => {
    return `${value.toFixed(2)}%`
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

  return (
    <div className="chart-view" style={{ animation: 'fadeInUp 0.6s ease-out' }}>
      <div className="chart-header">
        <h2>{getTitle()}</h2>
        <div className="chart-summary">
          {metricType === 'avg_premium' ? (
            <>
              <span>Total Policies: {totalCount.toLocaleString()}</span>
              <span>Overall Average: {formatValue(data.length > 0 ? totalValue / data.length : 0)}</span>
            </>
          ) : (
            <>
              <span>Total: {formatValue(totalValue)}</span>
              {metricType !== 'policy_count' && (
                <span>Total Policies: {totalCount.toLocaleString()}</span>
              )}
            </>
          )}
        </div>
      </div>

      <div className="chart-container">
        {data.length > 0 ? (
          <>
            {/* Bar Chart */}
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

            {/* Table with Count and Percent (for non-avg_premium metrics) */}
            {metricType !== 'avg_premium' && (
              <div style={{ marginTop: '2rem' }}>
                <h3 style={{ marginBottom: '1rem', color: 'var(--text-primary)' }}>Details</h3>
                <div style={{ overflowX: 'auto' }}>
                  <table style={{ 
                    width: '100%', 
                    borderCollapse: 'collapse',
                    backgroundColor: 'var(--bg-primary)',
                    boxShadow: '0 2px 8px var(--shadow)',
                    borderRadius: '8px',
                    overflow: 'hidden'
                  }}>
                    <thead>
                      <tr style={{ backgroundColor: 'var(--color-primary)', color: '#fff' }}>
                        <th style={{ padding: '12px', textAlign: 'left', border: '1px solid var(--border-color)' }}>Line</th>
                        <th style={{ padding: '12px', textAlign: 'right', border: '1px solid var(--border-color)' }}>
                          {metricType === 'policy_count' ? 'Count' : metricType === 'premium' ? 'Premium' : 'Commission'}
                        </th>
                        <th style={{ padding: '12px', textAlign: 'right', border: '1px solid var(--border-color)' }}>Percent</th>
                        {metricType !== 'policy_count' && (
                          <th style={{ padding: '12px', textAlign: 'right', border: '1px solid var(--border-color)' }}>Policy Count</th>
                        )}
                      </tr>
                    </thead>
                    <tbody>
                      {data.map((item, index) => (
                        <tr key={index} style={{ 
                          backgroundColor: index % 2 === 0 ? 'var(--bg-tertiary)' : 'var(--bg-secondary)',
                          color: 'var(--text-primary)'
                        }}>
                          <td style={{ padding: '12px', border: '1px solid var(--border-color)' }}>{item.line}</td>
                          <td style={{ padding: '12px', textAlign: 'right', border: '1px solid var(--border-color)' }}>
                            {formatValue(item.value)}
                          </td>
                          <td style={{ padding: '12px', textAlign: 'right', border: '1px solid var(--border-color)' }}>
                            {formatPercent(item.percent)}
                          </td>
                          {metricType !== 'policy_count' && (
                            <td style={{ padding: '12px', textAlign: 'right', border: '1px solid var(--border-color)' }}>
                              {item.count.toLocaleString()}
                            </td>
                          )}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* For avg_premium, show table with average premium values */}
            {metricType === 'avg_premium' && (
              <div style={{ marginTop: '2rem' }}>
                <h3 style={{ marginBottom: '1rem', color: 'var(--text-primary)' }}>Average Premium by Line</h3>
                <div style={{ overflowX: 'auto' }}>
                  <table style={{ 
                    width: '100%', 
                    borderCollapse: 'collapse',
                    backgroundColor: 'var(--bg-primary)',
                    boxShadow: '0 2px 8px var(--shadow)',
                    borderRadius: '8px',
                    overflow: 'hidden'
                  }}>
                    <thead>
                      <tr style={{ backgroundColor: 'var(--color-primary)', color: '#fff' }}>
                        <th style={{ padding: '12px', textAlign: 'left', border: '1px solid var(--border-color)' }}>Line</th>
                        <th style={{ padding: '12px', textAlign: 'right', border: '1px solid var(--border-color)' }}>Average Premium</th>
                        <th style={{ padding: '12px', textAlign: 'right', border: '1px solid var(--border-color)' }}>Policy Count</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.map((item, index) => (
                        <tr key={index} style={{ 
                          backgroundColor: index % 2 === 0 ? 'var(--bg-tertiary)' : 'var(--bg-secondary)',
                          color: 'var(--text-primary)'
                        }}>
                          <td style={{ padding: '12px', border: '1px solid var(--border-color)' }}>{item.line}</td>
                          <td style={{ padding: '12px', textAlign: 'right', border: '1px solid var(--border-color)' }}>
                            {formatValue(item.value)}
                          </td>
                          <td style={{ padding: '12px', textAlign: 'right', border: '1px solid var(--border-color)' }}>
                            {item.count.toLocaleString()}
                          </td>
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
  )
}

export default InforceByLineView

