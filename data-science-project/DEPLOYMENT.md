# Deployment Guide: Vercel (Frontend) + Heroku (Backend)

This guide will help you deploy your Data Science project to Vercel (frontend) and Heroku (backend).

## Prerequisites

1. **GitHub Account**: Your code should be in a GitHub repository
2. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
3. **Heroku Account**: Sign up at [heroku.com](https://heroku.com)
4. **Heroku CLI**: Install from [devcenter.heroku.com](https://devcenter.heroku.com/articles/heroku-cli)

## Step 1: Deploy Backend to Heroku

### 1.1 Prepare Your Repository

Make sure your backend code is in the `backend/` directory and includes:
- `main.py` (FastAPI application)
- `requirements.txt` (Python dependencies)
- `Procfile` (Heroku process definition)
- `runtime.txt` (Python version)

### 1.2 Deploy to Heroku

```bash
# Navigate to backend directory
cd backend

# Login to Heroku
heroku login

# Create a new Heroku app
heroku create your-app-name

# Add buildpacks (if needed)
heroku buildpacks:set heroku/python

# Set environment variables
heroku config:set CORS_ORIGINS="https://your-frontend-domain.vercel.app"

# Deploy the application
git add .
git commit -m "Deploy backend to Heroku"
git push heroku main

# Check the logs
heroku logs --tail
```

### 1.3 Verify Backend Deployment

1. Visit your Heroku app URL: `https://your-app-name.herokuapp.com`
2. You should see the API documentation or a JSON response
3. Test the health endpoint: `https://your-app-name.herokuapp.com/health`

### 1.4 Important Notes for Backend

- **Data Storage**: Heroku's filesystem is ephemeral. For production, consider using:
  - Heroku Postgres for database
  - AWS S3 for file storage
  - Redis for caching

- **Environment Variables**: Set these in Heroku dashboard:
  ```bash
  heroku config:set CORS_ORIGINS="https://your-frontend-domain.vercel.app"
  heroku config:set DATABASE_URL="your_database_url"
  ```

## Step 2: Deploy Frontend to Vercel

### 2.1 Prepare Your Repository

Make sure your frontend code is in the `frontend/` directory and includes:
- `package.json` (Node.js dependencies)
- `vercel.json` (Vercel configuration)
- `.env.example` (Environment variables template)

### 2.2 Deploy to Vercel

#### Option A: Using Vercel CLI

```bash
# Navigate to frontend directory
cd frontend

# Install Vercel CLI
npm i -g vercel

# Deploy to Vercel
vercel

# Follow the prompts:
# - Link to existing project or create new
# - Set project name
# - Confirm deployment settings
```

#### Option B: Using Vercel Dashboard

1. Go to [vercel.com](https://vercel.com)
2. Click "New Project"
3. Import your GitHub repository
4. Configure the project:
   - **Framework Preset**: Create React App
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `build`

### 2.3 Configure Environment Variables

In your Vercel project dashboard:

1. Go to Settings → Environment Variables
2. Add the following variables:
   ```
   REACT_APP_API_URL=https://your-heroku-app-name.herokuapp.com
   ```

### 2.4 Update Vercel Configuration

Update `frontend/vercel.json` with your actual Heroku app URL:

```json
{
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "https://your-heroku-app-name.herokuapp.com/$1"
    }
  ],
  "routes": [
    {
      "src": "/[^.]+",
      "dest": "/",
      "status": 200
    }
  ],
  "buildCommand": "npm run build",
  "outputDirectory": "build",
  "framework": "create-react-app"
}
```

### 2.5 Redeploy Frontend

After updating the configuration:

```bash
# If using Vercel CLI
vercel --prod

# Or trigger a new deployment from Vercel dashboard
```

## Step 3: Update CORS Settings

After both deployments are complete:

1. **Update Backend CORS**: Add your Vercel domain to Heroku environment variables:
   ```bash
   heroku config:set CORS_ORIGINS="https://your-frontend-domain.vercel.app"
   ```

2. **Redeploy Backend** (if needed):
   ```bash
   git push heroku main
   ```

## Step 4: Test the Deployment

### 4.1 Test Backend API

```bash
# Test health endpoint
curl https://your-heroku-app-name.herokuapp.com/health

# Test data sources
curl https://your-heroku-app-name.herokuapp.com/data/sources
```

### 4.2 Test Frontend

1. Visit your Vercel app URL
2. Check browser console for any API errors
3. Test all features: Dashboard, Data Explorer, Analytics, etc.

## Step 5: Production Considerations

### 5.1 Backend (Heroku)

- **Database**: Use Heroku Postgres for persistent data
- **File Storage**: Use AWS S3 or similar for data files
- **Caching**: Use Redis for improved performance
- **Monitoring**: Set up Heroku add-ons for monitoring

### 5.2 Frontend (Vercel)

- **Environment Variables**: Keep sensitive data in Vercel environment variables
- **Custom Domain**: Configure custom domain if needed
- **Analytics**: Add Google Analytics or similar

### 5.3 Security

- **API Keys**: Store all API keys in environment variables
- **CORS**: Restrict CORS origins to your actual domains
- **HTTPS**: Both Vercel and Heroku provide HTTPS by default

## Troubleshooting

### Common Issues

1. **CORS Errors**: Make sure CORS_ORIGINS includes your Vercel domain
2. **API Connection**: Verify REACT_APP_API_URL is correct
3. **Build Failures**: Check build logs in Vercel dashboard
4. **Runtime Errors**: Check Heroku logs with `heroku logs --tail`

### Debugging Commands

```bash
# Check Heroku logs
heroku logs --tail

# Check Heroku config
heroku config

# Restart Heroku app
heroku restart

# Check Vercel deployment status
vercel ls
```

## Maintenance

### Regular Tasks

1. **Monitor Logs**: Check both Vercel and Heroku logs regularly
2. **Update Dependencies**: Keep packages updated
3. **Backup Data**: If using external databases, ensure regular backups
4. **Performance**: Monitor app performance and optimize as needed

### Scaling

- **Heroku**: Upgrade dyno type for better performance
- **Vercel**: Automatically scales with traffic
- **Database**: Consider read replicas for high traffic

## Support

- **Vercel Documentation**: [vercel.com/docs](https://vercel.com/docs)
- **Heroku Documentation**: [devcenter.heroku.com](https://devcenter.heroku.com)
- **FastAPI Documentation**: [fastapi.tiangolo.com](https://fastapi.tiangolo.com)
- **React Documentation**: [reactjs.org](https://reactjs.org) 