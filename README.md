# CRIS Dashboard

A live data visualization tool with Python (FastAPI) backend and React frontend, integrated with QuickBase API.

## Features

- **Real-time Data Visualization**: Connect to QuickBase API to fetch and display live data
- **Multiple Measures**: Visualize Policies, Premium, and Commission data
- **Flexible Periods**: View data by Month, Quarter, or Year
- **Advanced Filtering**: 
  - Date range filtering (Start Date / End Date)
  - Period since time filtering (e.g., "30days", "6months", "2024-01-01")
- **Multiple Chart Types**: Bar charts and Line charts for data visualization

## Architecture

```
CRIS-Dashboard/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── services/
│   │   ├── quickbase_client.py # QuickBase API integration
│   │   └── data_processor.py   # Data processing and filtering logic
│   └── .env.example            # Environment variables template
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.jsx   # Main dashboard component
│   │   │   ├── Filters.jsx     # Filter controls
│   │   │   └── ChartView.jsx   # Chart visualization
│   │   ├── services/
│   │   │   └── api.js          # API service layer
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
├── requirements.txt            # Python dependencies
└── README.md
```

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

3. Install Python dependencies:
```bash
pip install -r ../requirements.txt
```

4. Create a `.env` file in the `backend` directory:
```bash
cp .env.example .env
```

5. Update the `.env` file with your QuickBase credentials:
```
QUICKBASE_API_TOKEN=bykzhu_bmc9_0_ba7azbmc6yyhx8bn868vh6dgm4h
QUICKBASE_REALM=your-realm.quickbase.com
QUICKBASE_TABLE_ID=your-table-id
```

6. Run the backend server:
```bash
python main.py
```

The backend will run on `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env` file (optional, if API URL differs):
```bash
VITE_API_URL=http://localhost:8000
```

4. Start the development server:
```bash
npm run dev
```

The frontend will run on `http://localhost:3000`

## Configuration

### QuickBase API Setup

You need to configure the following in `backend/.env`:

- **QUICKBASE_API_TOKEN**: Your QuickBase API token (already provided)
- **QUICKBASE_REALM**: Your QuickBase realm hostname (e.g., `yourcompany.quickbase.com`)
- **QUICKBASE_TABLE_ID**: The table ID you want to query from QuickBase

### Field ID Configuration

Update the field IDs in the following files to match your QuickBase table schema:

1. `backend/services/quickbase_client.py`:
   - Adjust the `select` array in the query payload to match your field IDs

2. `backend/services/data_processor.py`:
   - Update `measure_fields` dictionary with correct field IDs:
     ```python
     self.measure_fields = {
         "policies": 6,  # Your policies field ID
         "premium": 7,   # Your premium field ID
         "commission": 8 # Your commission field ID
     }
     ```
   - Update `date_field_id` in `_get_date_from_record` method

## API Endpoints

### POST /api/data
Get filtered visualization data.

**Request Body:**
```json
{
  "measure": "policies|premium|commission",
  "period": "month|quarter|year",
  "start_date": "2024-01-01" (optional),
  "end_date": "2024-12-31" (optional),
  "since_time": "30days|6months|2024-01-01" (optional)
}
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "period": "2024-01",
      "value": 1234.56,
      "label": "Jan 2024"
    }
  ],
  "measure": "policies",
  "period": "month"
}
```

### GET /api/filters/measures
Get available measures.

### GET /api/filters/periods
Get available periods.

## Usage

1. Select a **Measure**: Policies, Premium, or Commission
2. Select a **Period**: Month, Quarter, or Year
3. Optionally set filters:
   - **Since Time**: Enter relative time (e.g., "30days", "6months") or absolute date
   - **Start Date / End Date**: Set a specific date range
4. View the visualizations in both Bar Chart and Line Chart formats

## Development Notes

- The backend uses mock data if QuickBase API is unavailable (for development/testing)
- Frontend automatically refreshes when filters change
- All date parsing handles multiple formats
- Charts are responsive and mobile-friendly

## Troubleshooting

1. **CORS Errors**: Ensure the backend CORS settings include your frontend URL
2. **API Connection Issues**: Check QuickBase credentials in `.env` file
3. **No Data Displayed**: Verify field IDs match your QuickBase table schema
4. **Date Parsing Errors**: Check date format in QuickBase records

