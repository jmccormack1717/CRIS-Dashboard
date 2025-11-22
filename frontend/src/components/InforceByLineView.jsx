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

const COLORS = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#43e97b', '#fa709a', '#fee140', '#30cfd0']

const InforceByLineView = ({ data, metricType }) => {
  const formatValue = (value) => {
    if (metricType === 'premium' || metricType === 'commission' || metricType === 'avg_premium') {
      return `$${value.toLocaleString()}`
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
    <div className="chart-view">
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
              <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 100 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="line" 
                  angle={-45}
                  textAnchor="end"
                  height={100}
                />
                <YAxis tickFormatter={(value) => {
                  if (metricType === 'premium' || metricType === 'commission' || metricType === 'avg_premium') {
                    return `$${(value / 1000).toFixed(0)}k`
                  }
                  return value.toLocaleString()
                }} />
                <Tooltip 
                  formatter={(value, name) => {
                    if (name === 'value') {
                      return formatValue(value)
                    }
                    return value
                  }}
                  labelStyle={{ color: '#333' }}
                  contentStyle={{ backgroundColor: '#fff', border: '1px solid #ccc' }}
                />
                <Legend />
                <Bar 
                  dataKey="value" 
                  name={metricType === 'policy_count' ? 'Policy Count' : 
                        metricType === 'premium' ? 'Premium' :
                        metricType === 'commission' ? 'Commission' :
                        'Average Premium'}
                  radius={[8, 8, 0, 0]}
                >
                  {data.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>

            {/* Table with Count and Percent (for non-avg_premium metrics) */}
            {metricType !== 'avg_premium' && (
              <div style={{ marginTop: '2rem' }}>
                <h3 style={{ marginBottom: '1rem', color: '#333' }}>Details</h3>
                <div style={{ overflowX: 'auto' }}>
                  <table style={{ 
                    width: '100%', 
                    borderCollapse: 'collapse',
                    backgroundColor: '#fff',
                    boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                  }}>
                    <thead>
                      <tr style={{ backgroundColor: '#667eea', color: '#fff' }}>
                        <th style={{ padding: '12px', textAlign: 'left', border: '1px solid #ddd' }}>Line</th>
                        <th style={{ padding: '12px', textAlign: 'right', border: '1px solid #ddd' }}>
                          {metricType === 'policy_count' ? 'Count' : metricType === 'premium' ? 'Premium' : 'Commission'}
                        </th>
                        <th style={{ padding: '12px', textAlign: 'right', border: '1px solid #ddd' }}>Percent</th>
                        {metricType !== 'policy_count' && (
                          <th style={{ padding: '12px', textAlign: 'right', border: '1px solid #ddd' }}>Policy Count</th>
                        )}
                      </tr>
                    </thead>
                    <tbody>
                      {data.map((item, index) => (
                        <tr key={index} style={{ backgroundColor: index % 2 === 0 ? '#f9f9f9' : '#fff' }}>
                          <td style={{ padding: '12px', border: '1px solid #ddd' }}>{item.line}</td>
                          <td style={{ padding: '12px', textAlign: 'right', border: '1px solid #ddd' }}>
                            {formatValue(item.value)}
                          </td>
                          <td style={{ padding: '12px', textAlign: 'right', border: '1px solid #ddd' }}>
                            {formatPercent(item.percent)}
                          </td>
                          {metricType !== 'policy_count' && (
                            <td style={{ padding: '12px', textAlign: 'right', border: '1px solid #ddd' }}>
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
                <h3 style={{ marginBottom: '1rem', color: '#333' }}>Average Premium by Line</h3>
                <div style={{ overflowX: 'auto' }}>
                  <table style={{ 
                    width: '100%', 
                    borderCollapse: 'collapse',
                    backgroundColor: '#fff',
                    boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                  }}>
                    <thead>
                      <tr style={{ backgroundColor: '#667eea', color: '#fff' }}>
                        <th style={{ padding: '12px', textAlign: 'left', border: '1px solid #ddd' }}>Line</th>
                        <th style={{ padding: '12px', textAlign: 'right', border: '1px solid #ddd' }}>Average Premium</th>
                        <th style={{ padding: '12px', textAlign: 'right', border: '1px solid #ddd' }}>Policy Count</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.map((item, index) => (
                        <tr key={index} style={{ backgroundColor: index % 2 === 0 ? '#f9f9f9' : '#fff' }}>
                          <td style={{ padding: '12px', border: '1px solid #ddd' }}>{item.line}</td>
                          <td style={{ padding: '12px', textAlign: 'right', border: '1px solid #ddd' }}>
                            {formatValue(item.value)}
                          </td>
                          <td style={{ padding: '12px', textAlign: 'right', border: '1px solid #ddd' }}>
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

