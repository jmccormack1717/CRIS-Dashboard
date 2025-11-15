# CRIS Dashboard Architecture

## Overview

The CRIS Dashboard is a full-stack web application for visualizing QuickBase data with real-time filtering capabilities.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     React Frontend                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Filters    │  │   Dashboard  │  │  ChartView   │     │
│  │  Component   │→ │  Component   │→ │  Component   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                           ↓                                 │
│                  ┌──────────────┐                           │
│                  │  API Service │                           │
│                  └──────────────┘                           │
└───────────────────────────│─────────────────────────────────┘
                            │ HTTP/REST
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  FastAPI Backend                            │
│  ┌────────────────────────────────────────────────────┐    │
│  │              API Endpoints                         │    │
│  │  POST /api/data                                    │    │
│  │  GET /api/filters/measures                         │    │
│  │  GET /api/filters/periods                          │    │
│  └────────────────────────────────────────────────────┘    │
│                           ↓                                 │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │ QuickBase Client │  │ Data Processor   │                │
│  └──────────────────┘  └──────────────────┘                │
└───────────────────────────│─────────────────────────────────┘
                            │ API Calls
                            ↓
                    ┌───────────────┐
                    │  QuickBase    │
                    │     API       │
                    └───────────────┘
```

## Component Details

### Backend (Python/FastAPI)

#### Main Application (`backend/main.py`)
- FastAPI application with CORS middleware
- API endpoints for data fetching and filter configuration
- Error handling and validation

#### QuickBase Client (`backend/services/quickbase_client.py`)
- Handles API authentication with QuickBase
- Fetches data from QuickBase tables
- Fallback to mock data for development
- Configurable table ID and field mapping

#### Data Processor (`backend/services/data_processor.py`)
- Processes raw QuickBase data
- Implements filtering logic:
  - Date range filtering
  - Period since time filtering (e.g., "30days", "6months")
- Groups data by period (Month, Quarter, Year)
- Aggregates measures (Policies, Premium, Commission)
- Formats data for frontend consumption

### Frontend (React/Vite)

#### Dashboard Component (`frontend/src/components/Dashboard.jsx`)
- Main container component
- Manages state and data fetching
- Coordinates between Filters and ChartView

#### Filters Component (`frontend/src/components/Filters.jsx`)
- User interface for filter selection
- Supports:
  - Measure selection (Policies, Premium, Commission)
  - Period selection (Month, Quarter, Year)
  - Date range filters (Start Date, End Date)
  - Since Time filter (relative or absolute)

#### ChartView Component (`frontend/src/components/ChartView.jsx`)
- Displays data visualizations using Recharts
- Shows both Bar Chart and Line Chart
- Displays summary statistics (Total, Average)
- Responsive design

#### API Service (`frontend/src/services/api.js`)
- Axios-based HTTP client
- API endpoint abstraction
- Error handling

## Data Flow

1. **User Interaction**: User selects filters in the frontend
2. **API Request**: Frontend sends POST request to `/api/data` with filter parameters
3. **Backend Processing**:
   - QuickBase Client fetches raw data from QuickBase API
   - Data Processor applies filters and groups data by period
   - Aggregates values based on selected measure
4. **Response**: Backend returns formatted data array
5. **Visualization**: Frontend renders charts using Recharts library

## Configuration

### Environment Variables (Backend)

- `QUICKBASE_API_TOKEN`: QuickBase API authentication token
- `QUICKBASE_REALM`: QuickBase realm hostname
- `QUICKBASE_TABLE_ID`: Target table ID for queries

### Field Mapping

The following field IDs must be configured based on your QuickBase schema:

- **Date Field**: Field ID 3 (default)
- **Policies Field**: Field ID 6 (default)
- **Premium Field**: Field ID 7 (default)
- **Commission Field**: Field ID 8 (default)

Update these in:
- `backend/services/quickbase_client.py` - Query select fields
- `backend/services/data_processor.py` - Measure field mapping

## Filtering Logic

### Period Grouping
- **Month**: Groups by `YYYY-MM` format
- **Quarter**: Groups by `YYYY-QN` format (e.g., "2024-Q1")
- **Year**: Groups by `YYYY` format

### Measure Aggregation
- Values are summed for each period group
- Supports Policies (count), Premium (currency), Commission (currency)

### Time Filtering
- **Since Time**: Accepts relative formats ("30days", "6months", "1year") or absolute dates ("2024-01-01")
- **Date Range**: Start Date and End Date filters work independently or together

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **Uvicorn**: ASGI server
- **httpx**: Async HTTP client for QuickBase API
- **pydantic**: Data validation
- **python-dotenv**: Environment variable management

### Frontend
- **React 18**: UI library
- **Vite**: Build tool and dev server
- **Recharts**: Charting library
- **Axios**: HTTP client
- **date-fns**: Date utilities (optional)

## Deployment Considerations

1. **Backend**: Deploy to any Python hosting (Heroku, AWS, GCP, Azure)
2. **Frontend**: Static site hosting (Vercel, Netlify, AWS S3)
3. **CORS**: Update CORS origins for production frontend URL
4. **Environment Variables**: Secure storage of QuickBase credentials
5. **API Rate Limiting**: Consider implementing rate limiting for QuickBase API calls

