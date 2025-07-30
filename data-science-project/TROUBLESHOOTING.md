# Frontend-Backend Connection Troubleshooting Guide

## 🔍 Common Issues and Solutions

### 1. **Environment Variables Not Set**

**Problem**: Frontend can't find the backend URL
**Solution**: 
- Check Vercel Environment Variables
- Ensure `REACT_APP_API_URL` is set to: `https://data-science-backend-2024-11b411fad5ba.herokuapp.com`

### 2. **CORS Issues**

**Problem**: Browser blocks requests due to CORS policy
**Solution**:
- Verify CORS_ORIGINS in Heroku: `heroku config:set CORS_ORIGINS="https://your-vercel-domain.vercel.app"`
- Check browser console for CORS errors

### 3. **Network Errors**

**Problem**: Frontend can't reach backend
**Solution**:
- Test backend directly: `curl https://data-science-backend-2024-11b411fad5ba.herokuapp.com/health`
- Check if Heroku app is running: `heroku ps`

### 4. **Build Issues**

**Problem**: Frontend build fails
**Solution**:
- Check Vercel build logs
- Ensure all dependencies are in package.json
- Verify vercel.json configuration

## 🛠️ Debugging Steps

### Step 1: Use the API Test Component

1. Deploy the updated frontend with the API Test component
2. Navigate to `/test` in your frontend
3. Click "Test All API Endpoints"
4. Check the results and console logs

### Step 2: Check Browser Console

1. Open Developer Tools (F12)
2. Go to Console tab
3. Look for:
   - Network errors
   - CORS errors
   - JavaScript errors
   - API request logs

### Step 3: Verify Environment Variables

**In Vercel Dashboard**:
1. Go to Project Settings
2. Environment Variables
3. Check `REACT_APP_API_URL`

**In Heroku**:
```bash
heroku config
```

### Step 4: Test Backend Directly

```bash
# Test health endpoint
curl https://data-science-backend-2024-11b411fad5ba.herokuapp.com/health

# Test analytics endpoint
curl https://data-science-backend-2024-11b411fad5ba.herokuapp.com/analytics

# Test with CORS headers
curl -H "Origin: https://your-vercel-domain.vercel.app" \
     -H "Access-Control-Request-Method: GET" \
     -X OPTIONS \
     https://data-science-backend-2024-11b411fad5ba.herokuapp.com/health
```

## 🔧 Quick Fixes

### Fix 1: Update CORS Settings

```bash
# Set CORS for your Vercel domain
heroku config:set CORS_ORIGINS="https://your-vercel-domain.vercel.app"

# Restart the app
heroku restart
```

### Fix 2: Redeploy Frontend

After updating environment variables in Vercel:
1. Trigger a new deployment
2. Wait for build to complete
3. Test the connection

### Fix 3: Check Heroku Logs

```bash
# View recent logs
heroku logs --tail --num 50

# Check for errors
heroku logs | grep -i error
```

## 📋 Checklist

- [ ] Backend is running on Heroku
- [ ] Environment variable `REACT_APP_API_URL` is set in Vercel
- [ ] CORS_ORIGINS includes your Vercel domain
- [ ] No JavaScript errors in browser console
- [ ] API endpoints return data when tested directly
- [ ] Frontend can make requests to backend

## 🆘 Still Having Issues?

1. **Check the API Test component** at `/test` for detailed error information
2. **Share browser console errors** for specific debugging
3. **Test backend endpoints directly** to isolate the issue
4. **Check Vercel deployment logs** for build issues

## 📞 Support Commands

```bash
# Heroku commands
heroku ps                    # Check app status
heroku logs --tail          # View live logs
heroku config               # View environment variables
heroku restart              # Restart the app

# Test backend endpoints
curl https://data-science-backend-2024-11b411fad5ba.herokuapp.com/health
curl https://data-science-backend-2024-11b411fad5ba.herokuapp.com/analytics
``` 