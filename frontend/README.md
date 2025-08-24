# JobSprint Frontend

Ultra-recent job automation system frontend built with Bootstrap 5 and vanilla JavaScript.

## Features

- 🚀 Ultra-recent job filtering (5-10 minutes)
- 🇨🇦 Canada-specific location optimization
- 👥 Multi-user dashboard
- 📊 Real-time job discovery
- 📱 Mobile-responsive design
- ⚡ Fast static site deployment

## Deployment

This frontend is deployed on Vercel and connects to the Railway backend API.

### Live URLs

- **Frontend**: https://jobsprint.vercel.app
- **Backend API**: https://jobsprint-api.railway.app

## Local Development

1. Open `index.html` in a web browser
2. For API integration, update `CONFIG.API_BASE_URL` in `script.js`
3. Set `CONFIG.DEMO_MODE = false` when API is ready

## Architecture

```
Frontend (Vercel) → API (Railway) → Database (Supabase)
     ↓                    ↓              ↓
Static Files         Business Logic   Data Storage
Global CDN          Background Jobs   Real-time Updates
Auto HTTPS          Email System     User Management
```

## Technologies

- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Framework**: Bootstrap 5
- **Icons**: Font Awesome 6
- **Deployment**: Vercel
- **CDN**: Global edge network

## Configuration

Update `script.js` with your Railway API URL:

```javascript
const CONFIG = {
    API_BASE_URL: 'https://your-railway-app.railway.app/api',
    DEMO_MODE: false
};
```
