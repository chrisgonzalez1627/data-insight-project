# Quick Start Deployment Guide

This is a simplified guide to get your Data Science project deployed quickly.

## Prerequisites

1. **GitHub Repository**: Push your code to GitHub
2. **Heroku Account**: Sign up at [heroku.com](https://heroku.com)
3. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)

## Step 1: Deploy Backend (Heroku)

### Option A: Using Heroku CLI (Recommended)

```bash
# Install Heroku CLI
# Windows: Download from https://devcenter.heroku.com/articles/heroku-cli
# Mac: brew install heroku/brew/heroku

# Login to Heroku
heroku login

# Navigate to backend directory
cd backend

# Create Heroku app
heroku create your-app-name

# Deploy
git add .
git commit -m "Deploy backend"
git push heroku main

# Check logs
heroku logs --tail
```

### Option B: Using Heroku Dashboard

1. Go to [heroku.com](https://heroku.com)
2. Click "New" → "Create new app"
3. Choose "Deploy from GitHub"
4. Select your repository
5. Set root directory to `backend`
6. Deploy

## Step 2: Deploy Frontend (Vercel)

### Option A: Using Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Navigate to frontend directory
cd frontend

# Deploy
vercel

# Follow prompts and deploy to production
vercel --prod
```

### Option B: Using Vercel Dashboard

1. Go to [vercel.com](https://vercel.com)
2. Click "New Project"
3. Import your GitHub repository
4. Configure:
   - **Framework**: Create React App
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `build`
5. Deploy

## Step 3: Connect Frontend to Backend

### Update Environment Variables

In your Vercel project dashboard:

1. Go to Settings → Environment Variables
2. Add: `REACT_APP_API_URL=https://your-heroku-app-name.herokuapp.com`

### Update CORS Settings

In Heroku:

```bash
heroku config:set CORS_ORIGINS="https://your-vercel-domain.vercel.app"
```

## Step 4: Test Your Deployment

1. **Test Backend**: Visit `https://your-app-name.herokuapp.com/health`
2. **Test Frontend**: Visit your Vercel URL
3. **Check Console**: Look for any API errors in browser console

## Common Issues & Solutions

### CORS Errors
- Make sure CORS_ORIGINS includes your Vercel domain
- Check that the domain is exactly correct (including https://)

### API Connection Errors
- Verify REACT_APP_API_URL is correct
- Check that your Heroku app is running

### Build Failures
- Check Vercel build logs
- Ensure all dependencies are in package.json

## Next Steps

1. **Add Data**: Run your ETL pipeline to populate data
2. **Train Models**: Deploy your ML models
3. **Monitor**: Set up logging and monitoring
4. **Scale**: Consider database and storage solutions

## Support

- **Heroku**: Check logs with `heroku logs --tail`
- **Vercel**: Check deployment logs in dashboard
- **API**: Test endpoints with curl or Postman

## Quick Commands

```bash
# Check Heroku status
heroku ps

# Check Heroku logs
heroku logs --tail

# Restart Heroku app
heroku restart

# Check Vercel deployments
vercel ls

# Redeploy frontend
vercel --prod
``` 