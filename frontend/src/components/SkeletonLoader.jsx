import React from 'react'
import './Skeleton.css'

export const SkeletonChart = () => (
  <div className="skeleton-card">
    <div className="skeleton skeleton-title"></div>
    <div className="skeleton skeleton-text"></div>
    <div className="skeleton skeleton-chart" style={{ marginTop: '1rem' }}></div>
  </div>
)

export const SkeletonFilters = () => (
  <div className="skeleton-card">
    <div className="skeleton skeleton-title" style={{ width: '30%' }}></div>
    <div className="skeleton skeleton-filter"></div>
    <div className="skeleton skeleton-filter"></div>
    <div className="skeleton skeleton-filter"></div>
  </div>
)

export default SkeletonChart

