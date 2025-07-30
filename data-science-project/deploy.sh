#!/bin/bash

# Data Science Project Deployment Script
# This script helps deploy the backend to Heroku and frontend to Vercel

set -e  # Exit on any error

echo "🚀 Starting deployment process..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required tools are installed
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    if ! command -v heroku &> /dev/null; then
        print_error "Heroku CLI is not installed. Please install it first."
        print_status "Visit: https://devcenter.heroku.com/articles/heroku-cli"
        exit 1
    fi
    
    if ! command -v vercel &> /dev/null; then
        print_warning "Vercel CLI is not installed. Installing now..."
        npm install -g vercel
    fi
    
    if ! command -v git &> /dev/null; then
        print_error "Git is not installed. Please install it first."
        exit 1
    fi
    
    print_success "Prerequisites check completed!"
}

# Deploy backend to Heroku
deploy_backend() {
    print_status "Deploying backend to Heroku..."
    
    cd backend
    
    # Check if we're in a git repository
    if [ ! -d ".git" ]; then
        print_status "Initializing git repository for backend..."
        git init
        git add .
        git commit -m "Initial commit for Heroku deployment"
    fi
    
    # Check if Heroku app exists
    if ! heroku apps:info &> /dev/null; then
        print_status "Creating new Heroku app..."
        read -p "Enter your Heroku app name: " app_name
        heroku create $app_name
    fi
    
    # Get the app name
    app_name=$(heroku apps:info --json | grep -o '"name":"[^"]*"' | cut -d'"' -f4)
    print_status "Using Heroku app: $app_name"
    
    # Set environment variables
    print_status "Setting environment variables..."
    heroku config:set CORS_ORIGINS="https://your-frontend-domain.vercel.app"
    
    # Deploy
    print_status "Deploying to Heroku..."
    git add .
    git commit -m "Deploy backend to Heroku" || true
    git push heroku main
    
    print_success "Backend deployed successfully!"
    print_status "Backend URL: https://$app_name.herokuapp.com"
    
    cd ..
}

# Deploy frontend to Vercel
deploy_frontend() {
    print_status "Deploying frontend to Vercel..."
    
    cd frontend
    
    # Update vercel.json with backend URL
    print_status "Updating Vercel configuration..."
    read -p "Enter your Heroku app name: " heroku_app_name
    
    # Update vercel.json
    sed -i "s/your-heroku-app-name/$heroku_app_name/g" vercel.json
    
    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        print_status "Creating .env file..."
        cp .env.example .env
        sed -i "s/your-heroku-app-name/$heroku_app_name/g" .env
    fi
    
    # Deploy to Vercel
    print_status "Deploying to Vercel..."
    vercel --prod --yes
    
    print_success "Frontend deployed successfully!"
    
    cd ..
}

# Main deployment function
main() {
    echo "🎯 Data Science Project Deployment"
    echo "=================================="
    
    check_prerequisites
    
    # Ask user which part to deploy
    echo ""
    echo "What would you like to deploy?"
    echo "1. Backend only (Heroku)"
    echo "2. Frontend only (Vercel)"
    echo "3. Both backend and frontend"
    echo "4. Exit"
    
    read -p "Enter your choice (1-4): " choice
    
    case $choice in
        1)
            deploy_backend
            ;;
        2)
            deploy_frontend
            ;;
        3)
            deploy_backend
            echo ""
            deploy_frontend
            ;;
        4)
            print_status "Exiting..."
            exit 0
            ;;
        *)
            print_error "Invalid choice. Please enter 1-4."
            exit 1
            ;;
    esac
    
    echo ""
    print_success "Deployment completed!"
    print_status "Don't forget to:"
    print_status "1. Update CORS settings in Heroku with your Vercel domain"
    print_status "2. Test both applications"
    print_status "3. Set up monitoring and logging"
}

# Run main function
main "$@" 