import React from 'react'
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  AreaChart,
  Area,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts'
import './ChartView.css'

// Sleek Navy Theme Colors
const NAVY_COLORS = {
  primary: '#1e3a8a',
  secondary: '#3b82f6',
  accent: '#60a5fa',
  light: '#93c5fd',
  chart: {
    navy: '#1e40af',
    blue: '#3b82f6',
    sky: '#0ea5e9',
    cyan: '#06b6d4',
    teal: '#14b8a6',
    indigo: '#6366f1',
    lightBlue: '#60a5fa'
  }
}

const CHART_COLORS = [
  '#3b82f6',  // Bright blue
  '#0ea5e9',  // Sky blue
  '#60a5fa',  // Light blue
  '#06b6d4',  // Cyan
  '#14b8a6',  // Teal
  '#6366f1',  // Indigo
  '#1e40af'   // Deep navy
]

const ChartView = ({ data, measure, period, chartType = 'bar' }) => {
  const formatValue = (value) => {
    if (measure === 'premium' || measure === 'commission') {
      return `$${value.toLocaleString()}`
    }
    return value.toLocaleString()
  }

  const chartTitle = `${measure.charAt(0).toUpperCase() + measure.slice(1)} by ${period.charAt(0).toUpperCase() + period.slice(1)}`
  
  const renderChart = () => {
    const yAxisFormatter = (value) => {
      if (measure === 'premium' || measure === 'commission') {
        return `$${(value / 1000).toFixed(0)}k`
      }
      return value.toLocaleString()
    }
    
    const commonProps = {
      data,
      margin: { top: 20, right: 30, left: 20, bottom: 100 }
    }
    
    switch (chartType) {
      case 'line':
        return (
          <ResponsiveContainer width="100%" height={400}>
            <LineChart {...commonProps}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e3a8a" strokeOpacity={0.2} />
              <XAxis 
                dataKey="label" 
                angle={-45}
                textAnchor="end"
                height={100}
                stroke="#94a3b8"
                tick={{ fill: '#cbd5e1' }}
              />
              <YAxis 
                tickFormatter={yAxisFormatter}
                stroke="#94a3b8"
                tick={{ fill: '#cbd5e1' }}
              />
              <Tooltip 
                formatter={(value) => formatValue(value)}
                contentStyle={{ 
                  backgroundColor: '#0f172a', 
                  border: '1px solid #1e3a8a', 
                  borderRadius: '8px',
                  color: '#e2e8f0'
                }}
                labelStyle={{ color: '#60a5fa' }}
              />
              <Legend 
                wrapperStyle={{ color: '#cbd5e1' }}
              />
              <Line 
                type="monotone" 
                dataKey="value" 
                stroke={NAVY_COLORS.accent} 
                strokeWidth={3}
                dot={{ fill: NAVY_COLORS.accent, r: 5 }}
                activeDot={false}
                name={measure.charAt(0).toUpperCase() + measure.slice(1)}
              />
            </LineChart>
          </ResponsiveContainer>
        )
        
      case 'area':
        return (
          <ResponsiveContainer width="100%" height={400}>
            <AreaChart {...commonProps}>
              <defs>
                <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={NAVY_COLORS.secondary} stopOpacity={0.8}/>
                  <stop offset="95%" stopColor={NAVY_COLORS.accent} stopOpacity={0.1}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e3a8a" strokeOpacity={0.2} />
              <XAxis 
                dataKey="label" 
                angle={-45}
                textAnchor="end"
                height={100}
                stroke="#94a3b8"
                tick={{ fill: '#cbd5e1' }}
              />
              <YAxis 
                tickFormatter={yAxisFormatter}
                stroke="#94a3b8"
                tick={{ fill: '#cbd5e1' }}
              />
              <Tooltip 
                formatter={(value) => formatValue(value)}
                contentStyle={{ 
                  backgroundColor: '#0f172a', 
                  border: '1px solid #1e3a8a', 
                  borderRadius: '8px',
                  color: '#e2e8f0'
                }}
                labelStyle={{ color: '#60a5fa' }}
              />
              <Legend 
                wrapperStyle={{ color: '#cbd5e1' }}
              />
              <Area 
                type="monotone" 
                dataKey="value" 
                stroke={NAVY_COLORS.accent} 
                fill="url(#colorValue)"
                name={measure.charAt(0).toUpperCase() + measure.slice(1)}
              />
            </AreaChart>
          </ResponsiveContainer>
        )
        
      case 'pie':
        return (
          <ResponsiveContainer width="100%" height={400}>
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ label, percent }) => `${label}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={120}
                fill="#8884d8"
                dataKey="value"
                nameKey="label"
              >
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                ))}
              </Pie>
              <Tooltip 
                formatter={(value) => formatValue(value)}
                contentStyle={{ 
                  backgroundColor: '#0f172a', 
                  border: '1px solid #1e3a8a', 
                  borderRadius: '8px',
                  color: '#e2e8f0'
                }}
                labelStyle={{ color: '#60a5fa' }}
              />
              <Legend 
                wrapperStyle={{ color: '#cbd5e1' }}
              />
            </PieChart>
          </ResponsiveContainer>
        )
        
      case 'stacked':
        // For stacked, we'll show the same data but with visual stacking effect
        // In a real scenario, you might stack multiple measures
        return (
          <ResponsiveContainer width="100%" height={400}>
            <BarChart {...commonProps}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e3a8a" strokeOpacity={0.2} />
              <XAxis 
                dataKey="label" 
                angle={-45}
                textAnchor="end"
                height={100}
                stroke="#94a3b8"
                tick={{ fill: '#cbd5e1' }}
              />
              <YAxis 
                tickFormatter={yAxisFormatter}
                stroke="#94a3b8"
                tick={{ fill: '#cbd5e1' }}
              />
              <Tooltip 
                formatter={(value) => formatValue(value)}
                contentStyle={{ 
                  backgroundColor: '#0f172a', 
                  border: '1px solid #1e3a8a', 
                  borderRadius: '8px',
                  color: '#e2e8f0'
                }}
                labelStyle={{ color: '#60a5fa' }}
              />
              <Legend 
                wrapperStyle={{ color: '#cbd5e1' }}
              />
              <Bar 
                dataKey="value" 
                stackId="a"
                fill={NAVY_COLORS.secondary}
                name={measure.charAt(0).toUpperCase() + measure.slice(1)}
                radius={[8, 8, 0, 0]}
                cursor="default"
                activeBar={false}
              />
            </BarChart>
          </ResponsiveContainer>
        )
        
      case 'bar':
      default:
        return (
          <ResponsiveContainer width="100%" height={400}>
            <BarChart {...commonProps}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e3a8a" strokeOpacity={0.2} />
              <XAxis 
                dataKey="label" 
                angle={-45}
                textAnchor="end"
                height={100}
                stroke="#94a3b8"
                tick={{ fill: '#cbd5e1' }}
              />
              <YAxis 
                tickFormatter={yAxisFormatter}
                stroke="#94a3b8"
                tick={{ fill: '#cbd5e1' }}
              />
              <Tooltip 
                formatter={(value) => formatValue(value)}
                contentStyle={{ 
                  backgroundColor: '#0f172a', 
                  border: '1px solid #1e3a8a', 
                  borderRadius: '8px',
                  color: '#e2e8f0'
                }}
                labelStyle={{ color: '#60a5fa' }}
              />
              <Legend 
                wrapperStyle={{ color: '#cbd5e1' }}
              />
              <Bar 
                dataKey="value" 
                fill={NAVY_COLORS.secondary}
                name={measure.charAt(0).toUpperCase() + measure.slice(1)}
                radius={[8, 8, 0, 0]}
                cursor="default"
                activeBar={false}
              >
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        )
    }
  }

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
          renderChart()
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

