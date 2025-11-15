# Backend Setup

## Environment Variables

Create a `.env` file in this directory with the following variables:

```
QUICKBASE_API_TOKEN=bykzhu_bmc9_0_ba7azbmc6yyhx8bn868vh6dgm4h
QUICKBASE_REALM=your-realm.quickbase.com
QUICKBASE_TABLE_ID=your-table-id
```

## Running the Server

```bash
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

