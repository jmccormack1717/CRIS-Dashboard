# Deployment Guide for Render

This guide explains how to deploy both the backend API and frontend to Render as separate services from a single repository.

## Prerequisites

1. A GitHub account with this repository pushed
2. A Render account (sign up at [render.com](https://render.com))
3. QuickBase credentials (API token, realm, and table ID)

## Deployment Steps

### Step 1: Push Repository to GitHub

If you haven't already, push your code to GitHub:

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-github-repo-url>
git push -u origin main
```

### Step 2: Deploy Backend API Service

1. **Go to Render Dashboard**
   - Navigate to [dashboard.render.com](https://dashboard.render.com)
   - Click "New +" → "Web Service"

2. **Connect Repository**
   - Connect your GitHub account if not already connected
   - Select your repository: `CRIS-Dashboard`
   - Click "Connect"

3. **Configure Backend Service**
   - **Name**: `cris-dashboard-api` (or your preferred name)
   - **Region**: Choose closest to your users
   - **Branch**: `main` (or your default branch)
   - **Root Directory**: Leave empty (root of repo)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`

4. **Add Environment Variables**
   Click "Advanced" → "Add Environment Variable" and add:
   - `QUICKBASE_API_TOKEN` = `bykzhu_bmc9_0_ba7azbmc6yyhx8bn868vh6dgm4h`
   - `QUICKBASE_REALM` = Your QuickBase realm (e.g., `company.quickbase.com`)
   - `QUICKBASE_TABLE_ID` = Your QuickBase table ID
   - `FRONTEND_URL` = Will be set automatically after frontend deploys (or set manually)

5. **Create Service**
   - Click "Create Web Service"
   - Wait for deployment to complete
   - **Copy the service URL** (e.g., `https://cris-dashboard-api.onrender.com`)

### Step 3: Deploy Frontend Static Site

1. **Create New Static Site**
   - In Render Dashboard, click "New +" → "Static Site"

2. **Connect Repository**
   - Select the same repository: `CRIS-Dashboard`

3. **Configure Frontend Service**
   - **Name**: `cris-dashboard-frontend` (or your preferred name)
   - **Branch**: `main`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `frontend/dist`

4. **Add Environment Variable**
   - Click "Add Environment Variable"
   - **Key**: `VITE_API_URL`
   - **Value**: Your backend URL from Step 2 (e.g., `https://cris-dashboard-api.onrender.com`)
   - ⚠️ **Important**: Make sure to use `https://` and include the full URL

5. **Create Static Site**
   - Click "Create Static Site"
   - Wait for deployment to complete
   - **Copy the frontend URL** (e.g., `https://cris-dashboard-frontend.onrender.com`)

### Step 4: Update Backend CORS

1. **Go back to Backend Service**
   - Navigate to your backend service in Render Dashboard
   - Go to "Environment" tab

2. **Update FRONTEND_URL**
   - Update `FRONTEND_URL` to your frontend URL (e.g., `https://cris-dashboard-frontend.onrender.com`)
   - Click "Save Changes"
   - The service will automatically redeploy

### Step 5: Verify Deployment

1. **Test Backend API**
   - Visit: `https://your-backend-url.onrender.com/docs`
   - You should see the FastAPI interactive documentation

2. **Test Frontend**
   - Visit: `https://your-frontend-url.onrender.com`
   - The dashboard should load and be able to fetch data from the backend

## Alternative: Using render.yaml (Automated)

If you want to deploy both services automatically using the `render.yaml` configuration:

1. **Push `render.yaml` to your repository** (already included)

2. **In Render Dashboard**
   - Click "New +" → "Blueprint"
   - Select your repository
   - Render will automatically detect `render.yaml` and create both services

3. **Set Environment Variables**
   - For the backend service, add:
     - `QUICKBASE_API_TOKEN`
     - `QUICKBASE_REALM`
     - `QUICKBASE_TABLE_ID`
   - The frontend will automatically get the backend URL

4. **Deploy**
   - Render will deploy both services automatically
   - You can update the `FRONTEND_URL` environment variable in the backend after frontend deploys

## Environment Variables Reference

### Backend Service
- `QUICKBASE_API_TOKEN`: Your QuickBase API token
- `QUICKBASE_REALM`: Your QuickBase realm hostname
- `QUICKBASE_TABLE_ID`: Your QuickBase table ID
- `FRONTEND_URL`: Frontend URL for CORS (e.g., `https://cris-dashboard-frontend.onrender.com`)
- `PORT`: Automatically set by Render (don't set manually)

### Frontend Service
- `VITE_API_URL`: Backend API URL (e.g., `https://cris-dashboard-api.onrender.com`)
- Must start with `https://` for production

## Troubleshooting

### Backend Issues

**Problem**: Backend won't start
- **Solution**: Check that `requirements.txt` is in the root directory
- **Solution**: Verify start command includes `cd backend`

**Problem**: CORS errors
- **Solution**: Make sure `FRONTEND_URL` is set correctly in backend environment variables
- **Solution**: Include both `http://` and `https://` versions if needed

**Problem**: QuickBase API errors
- **Solution**: Verify all QuickBase credentials are correct
- **Solution**: Check that realm hostname doesn't include `https://` prefix

### Frontend Issues

**Problem**: Frontend can't connect to backend
- **Solution**: Verify `VITE_API_URL` is set correctly in frontend environment variables
- **Solution**: Make sure URL includes `https://` protocol
- **Solution**: Check browser console for CORS errors

**Problem**: Build fails
- **Solution**: Make sure `package.json` is in the `frontend` directory
- **Solution**: Check that Node.js version is compatible (Render uses Node 18+ by default)

**Problem**: 404 errors on page refresh
- **Solution**: This is normal for SPAs deployed as static sites. Configure redirect rules:
  - In Render Dashboard → Your Static Site → Settings
  - Under "Redirects/Rewrites", add:
    - Source: `/*`
    - Destination: `/index.html`
    - Status Code: `200`

## Custom Domains

You can add custom domains to both services:

1. **In Render Dashboard** → Your Service → Settings → Custom Domains
2. Add your domain
3. Update DNS records as instructed
4. Update environment variables:
   - Update `FRONTEND_URL` in backend to use custom domain
   - Update `VITE_API_URL` in frontend to use custom backend domain

## Monitoring and Logs

- **View Logs**: Render Dashboard → Your Service → Logs
- **Metrics**: Available in the service dashboard
- **Auto-Deploy**: Enabled by default on git push to main branch

## Cost

- **Free Tier**: Both services can run on free tier (may spin down after inactivity)
- **Starter Plan**: $7/month per service for always-on
- **Professional Plan**: $25/month per service for better performance

## Next Steps

After deployment:
1. Test all functionality with live QuickBase data
2. Set up monitoring/alerting if needed
3. Configure custom domains if desired
4. Set up auto-scaling if needed (requires paid plan)

