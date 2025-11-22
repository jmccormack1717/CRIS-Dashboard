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

// Insurance-themed color palette
const INSURANCE_COLORS = {
  primary: '#1e3a8a',      // Deep insurance blue
  secondary: '#3b82f6',    // Medium blue
  accent: '#60a5fa',       // Light blue
  success: '#059669',      // Green for positive trends
  warning: '#d97706',      // Orange for attention
  danger: '#dc2626',       // Red for alerts
  chart: {
    blue: '#2563eb',
    teal: '#0d9488',
    indigo: '#6366f1',
    slate: '#475569',
    cyan: '#0891b2',
    navy: '#1e40af',
    sky: '#0284c7'
  }
}

const CHART_COLORS = [
  INSURANCE_COLORS.chart.blue,
  INSURANCE_COLORS.chart.teal,
  INSURANCE_COLORS.chart.indigo,
  INSURANCE_COLORS.chart.slate,
  INSURANCE_COLORS.chart.cyan,
  INSURANCE_COLORS.chart.navy,
  INSURANCE_COLORS.chart.sky
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
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis 
                dataKey="label" 
                angle={-45}
                textAnchor="end"
                height={100}
                stroke="#6b7280"
              />
              <YAxis 
                tickFormatter={yAxisFormatter}
                stroke="#6b7280"
              />
              <Tooltip 
                formatter={(value) => formatValue(value)}
                contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb', borderRadius: '4px' }}
                labelStyle={{ color: '#1f2937' }}
              />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="value" 
                stroke={INSURANCE_COLORS.chart.blue} 
                strokeWidth={3}
                dot={{ fill: INSURANCE_COLORS.chart.blue, r: 5 }}
                activeDot={{ r: 7 }}
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
                  <stop offset="5%" stopColor={INSURANCE_COLORS.chart.blue} stopOpacity={0.8}/>
                  <stop offset="95%" stopColor={INSURANCE_COLORS.chart.blue} stopOpacity={0.1}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis 
                dataKey="label" 
                angle={-45}
                textAnchor="end"
                height={100}
                stroke="#6b7280"
              />
              <YAxis 
                tickFormatter={yAxisFormatter}
                stroke="#6b7280"
              />
              <Tooltip 
                formatter={(value) => formatValue(value)}
                contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb', borderRadius: '4px' }}
                labelStyle={{ color: '#1f2937' }}
              />
              <Legend />
              <Area 
                type="monotone" 
                dataKey="value" 
                stroke={INSURANCE_COLORS.chart.blue} 
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
                contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb', borderRadius: '4px' }}
                labelStyle={{ color: '#1f2937' }}
              />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        )
        
      case 'stacked':
        // For stacked, we'll show the same data but with visual stacking effect
        // In a real scenario, you might stack multiple measures
        return (
          <ResponsiveContainer width="100%" height={400}>
            <BarChart {...commonProps}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis 
                dataKey="label" 
                angle={-45}
                textAnchor="end"
                height={100}
                stroke="#6b7280"
              />
              <YAxis 
                tickFormatter={yAxisFormatter}
                stroke="#6b7280"
              />
              <Tooltip 
                formatter={(value) => formatValue(value)}
                contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb', borderRadius: '4px' }}
                labelStyle={{ color: '#1f2937' }}
              />
              <Legend />
              <Bar 
                dataKey="value" 
                stackId="a"
                fill={INSURANCE_COLORS.chart.blue}
                name={measure.charAt(0).toUpperCase() + measure.slice(1)}
                radius={[8, 8, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        )
        
      case 'bar':
      default:
        return (
          <ResponsiveContainer width="100%" height={400}>
            <BarChart {...commonProps}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis 
                dataKey="label" 
                angle={-45}
                textAnchor="end"
                height={100}
                stroke="#6b7280"
              />
              <YAxis 
                tickFormatter={yAxisFormatter}
                stroke="#6b7280"
              />
              <Tooltip 
                formatter={(value) => formatValue(value)}
                contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb', borderRadius: '4px' }}
                labelStyle={{ color: '#1f2937' }}
              />
              <Legend />
              <Bar 
                dataKey="value" 
                fill={INSURANCE_COLORS.chart.blue}
                name={measure.charAt(0).toUpperCase() + measure.slice(1)}
                radius={[8, 8, 0, 0]}
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

