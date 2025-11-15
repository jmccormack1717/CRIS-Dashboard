# Quick Deployment Guide to Render

## Quick Overview

You have two ways to deploy:

### Method 1: Manual Deployment (Recommended for first time)
Deploy backend and frontend separately for better control.

### Method 2: Blueprint Deployment (Using render.yaml)
Deploy both services automatically from one configuration file.

---

## Method 1: Manual Deployment (Step-by-Step)

### Part A: Deploy Backend API

1. **Go to [dashboard.render.com](https://dashboard.render.com)**
2. **Click "New +" → "Web Service"**
3. **Connect your GitHub repository**
4. **Configure Backend:**
   - **Name**: `cris-dashboard-api`
   - **Region**: Choose closest region
   - **Branch**: `main`
   - **Root Directory**: *(leave empty)*
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`

5. **Add Environment Variables:**
   - `QUICKBASE_API_TOKEN` = `bykzhu_bmc9_0_ba7azbmc6yyhx8bn868vh6dgm4h`
   - `QUICKBASE_REALM` = Your realm (e.g., `company.quickbase.com`)
   - `QUICKBASE_TABLE_ID` = Your table ID
   - `FRONTEND_URL` = *(leave empty for now, will update later)*

6. **Click "Create Web Service"**
7. **Wait for deployment** - Copy the URL (e.g., `https://cris-dashboard-api.onrender.com`)

### Part B: Deploy Frontend

1. **In Render Dashboard, click "New +" → "Static Site"**
2. **Connect the same GitHub repository**
3. **Configure Frontend:**
   - **Name**: `cris-dashboard-frontend`
   - **Branch**: `main`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`

4. **Add Environment Variable:**
   - **Key**: `VITE_API_URL`
   - **Value**: Your backend URL from Part A (e.g., `https://cris-dashboard-api.onrender.com`)
   - ⚠️ **Must include `https://`**

5. **Click "Create Static Site"**
6. **Wait for deployment** - Copy the URL (e.g., `https://cris-dashboard-frontend.onrender.com`)

### Part C: Update Backend CORS

1. **Go back to your Backend service** in Render Dashboard
2. **Go to "Environment" tab**
3. **Update `FRONTEND_URL`** to your frontend URL (e.g., `https://cris-dashboard-frontend.onrender.com`)
4. **Click "Save Changes"** - Service will auto-redeploy

### ✅ Done!

- **Backend API**: `https://cris-dashboard-api.onrender.com/docs`
- **Frontend**: `https://cris-dashboard-frontend.onrender.com`

---

## Method 2: Blueprint Deployment (Automatic)

### Using render.yaml

1. **Push `render.yaml` to GitHub** (already done)

2. **In Render Dashboard:**
   - Click "New +" → "Blueprint"
   - Select your repository
   - Render will detect `render.yaml` automatically

3. **Configure Environment Variables:**
   - **For Backend:**
     - `QUICKBASE_API_TOKEN`
     - `QUICKBASE_REALM`
     - `QUICKBASE_TABLE_ID`
     - `FRONTEND_URL` *(update after frontend deploys)*
   - **For Frontend:**
     - `VITE_API_URL` = Your backend URL (e.g., `https://cris-dashboard-api.onrender.com`)

4. **Click "Apply"** - Render will deploy both services

5. **After deployment, update `FRONTEND_URL` in backend** with the frontend URL

---

## Important Notes

### Environment Variables

**Backend needs:**
- ✅ `QUICKBASE_API_TOKEN` - Your QuickBase token
- ✅ `QUICKBASE_REALM` - Your QuickBase realm (no https://)
- ✅ `QUICKBASE_TABLE_ID` - Your table ID
- ✅ `FRONTEND_URL` - Frontend URL for CORS

**Frontend needs:**
- ✅ `VITE_API_URL` - Backend URL (must include `https://`)

### Common Issues

**CORS Errors?**
- Make sure `FRONTEND_URL` in backend matches your frontend URL exactly
- Include `https://` in the URL

**Frontend can't connect to backend?**
- Verify `VITE_API_URL` is set correctly in frontend
- Must start with `https://`
- Check backend is running and accessible

**Build fails?**
- Check that `requirements.txt` is in root directory
- Check that `package.json` is in `frontend` directory
- Verify Node.js version (Render uses 18+ by default)

### Testing

- **Backend**: Visit `https://your-backend-url.onrender.com/docs` for API docs
- **Frontend**: Visit `https://your-frontend-url.onrender.com` for the dashboard

---

## What Happens Next?

After successful deployment:
1. ✅ Both services are live
2. ✅ Frontend can communicate with backend
3. ✅ Backend connects to QuickBase
4. ✅ Dashboard displays live data

**Free Tier Note**: Services may spin down after 15 minutes of inactivity. First request after spin-down may be slow (~30 seconds) to wake up.

