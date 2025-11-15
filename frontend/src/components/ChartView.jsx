import React from 'react'
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts'
import './ChartView.css'

const ChartView = ({ data, measure, period }) => {
  const formatValue = (value) => {
    if (measure === 'premium' || measure === 'commission') {
      return `$${value.toLocaleString()}`
    }
    return value.toLocaleString()
  }

  const chartTitle = `${measure.charAt(0).toUpperCase() + measure.slice(1)} by ${period.charAt(0).toUpperCase() + period.slice(1)}`

  return (
    <div className="chart-view">
      <div className="chart-header">
        <h2>{chartTitle}</h2>
        <div className="chart-summary">
          <span>
            Total: {formatValue(data.reduce((sum, item) => sum + item.value, 0))}
          </span>
          <span>
            Average: {formatValue(data.length > 0 ? data.reduce((sum, item) => sum + item.value, 0) / data.length : 0)}
          </span>
        </div>
      </div>

      <div className="chart-container">
        {data.length > 0 ? (
          <>
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="label" 
                  angle={-45}
                  textAnchor="end"
                  height={100}
                />
                <YAxis tickFormatter={(value) => {
                  if (measure === 'premium' || measure === 'commission') {
                    return `$${(value / 1000).toFixed(0)}k`
                  }
                  return value.toLocaleString()
                }} />
                <Tooltip 
                  formatter={(value) => formatValue(value)}
                  labelStyle={{ color: '#333' }}
                />
                <Legend />
                <Bar 
                  dataKey="value" 
                  fill="#667eea" 
                  name={measure.charAt(0).toUpperCase() + measure.slice(1)}
                />
              </BarChart>
            </ResponsiveContainer>

            <ResponsiveContainer width="100%" height={400} style={{ marginTop: '2rem' }}>
              <LineChart data={data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="label" 
                  angle={-45}
                  textAnchor="end"
                  height={100}
                />
                <YAxis tickFormatter={(value) => {
                  if (measure === 'premium' || measure === 'commission') {
                    return `$${(value / 1000).toFixed(0)}k`
                  }
                  return value.toLocaleString()
                }} />
                <Tooltip 
                  formatter={(value) => formatValue(value)}
                  labelStyle={{ color: '#333' }}
                />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="value" 
                  stroke="#764ba2" 
                  strokeWidth={3}
                  dot={{ fill: '#764ba2', r: 4 }}
                  name={measure.charAt(0).toUpperCase() + measure.slice(1)}
                />
              </LineChart>
            </ResponsiveContainer>
          </>
        ) : (
          <div className="no-data">
            <p>No data available for the selected filters</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default ChartView

