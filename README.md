# 🚀 **JobSprint - LinkedIn Job Automation System**

## **✅ CLEAN LOCAL SETUP - ALL COMPONENTS WORKING**

A complete LinkedIn job automation system with ultra-recent filtering, multi-user support, and professional UI.

---

## **🎯 FEATURES**

### **🔍 LinkedIn Job Scraping:**
- ✅ **Ultra-Recent Filtering**: 5min to 24hr job discovery
- ✅ **Canadian Optimization**: 108+ Canadian locations
- ✅ **Multiple Methods**: Guest API + Selenium fallback
- ✅ **Real-Time Results**: Live LinkedIn job postings

### **🔐 Authentication System:**
- ✅ **Admin Panel**: Full administrative access
- ✅ **User Registration**: Instant account creation
- ✅ **Session Management**: Secure login state
- ✅ **Local Fallback**: Works without external database

### **🌐 Professional UI:**
- ✅ **Bootstrap Design**: Modern, responsive interface
- ✅ **Interactive Modals**: Sign up, login, admin panels
- ✅ **Mobile Friendly**: Works on all devices
- ✅ **Real-time Feedback**: User-friendly alerts

---

## **🚀 QUICK START**

### **1. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **2. Start the Application**
```bash
python app.py
```

### **3. Access the System**
- **Frontend**: http://127.0.0.1:5000
- **Dashboard**: http://127.0.0.1:5000/dashboard.html
- **Admin Dashboard**: http://127.0.0.1:5000/dashboard.html?admin=true
- **API**: http://127.0.0.1:5000/api/*
- **Health Check**: http://127.0.0.1:5000/health

---

## **🔐 DEFAULT ACCOUNTS**

### **Admin Account:**
- **Email**: admin@jobsprint.com
- **Password**: admin123
- **Features**: Full admin access, user management

### **Test User:**
- **Email**: test@jobsprint.com
- **Password**: test123
- **Features**: Regular user access

### **Create New Account:**
- Click "Sign Up" in the navigation
- Fill in your details
- Account created instantly

---

## **📁 PROJECT STRUCTURE**

```
JobSprint/
├── app.py                    # 🚀 Main Flask application
├── requirements.txt          # 📦 Python dependencies
├── README.md                 # 📚 This documentation
├── frontend/                 # 🌐 Frontend files
│   ├── index.html           # 📄 Main page
│   ├── dashboard.html       # 📊 Dashboard page
│   ├── script.js            # 💻 JavaScript logic
│   └── styles.css           # 🎨 Custom styles
└── src/                     # 🔧 Backend modules
    ├── linkedin_scraper_free.py  # 🔍 LinkedIn scraper
    ├── supabase_manager.py       # 🗄️ Database manager
    ├── location_manager.py       # 📍 Location handling
    ├── email_system.py           # 📧 Email notifications
    └── [other modules]
```

---

## **🔍 API ENDPOINTS**

### **Authentication:**
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `POST /api/auth/logout` - User logout

### **Job Search:**
- `POST /api/jobs/search` - Search LinkedIn jobs

### **System:**
- `GET /health` - Health check

---

## **🧪 TESTING**

### **Health Check:**
```bash
curl http://127.0.0.1:5000/health
```

### **Admin Login:**
```bash
curl -X POST http://127.0.0.1:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@jobsprint.com","password":"admin123"}'
```

### **Job Search:**
```bash
# Login first
curl -c cookies.txt -X POST http://127.0.0.1:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@jobsprint.com","password":"admin123"}'

# Search jobs
curl -b cookies.txt -X POST http://127.0.0.1:5000/api/jobs/search \
  -H "Content-Type: application/json" \
  -d '{"keywords":"software engineer","location":"Toronto, ON","max_results":3}'
```

---

## **⚙️ CONFIGURATION**

### **Time Filters:**
- `r300` = Last 5 minutes
- `r600` = Last 10 minutes
- `r1800` = Last 30 minutes
- `r3600` = Last 1 hour
- `r86400` = Last 24 hours

### **Work Types:**
- `1` = On-site
- `2` = Remote (default)
- `3` = Hybrid

### **Canadian Locations:**
- Toronto, ON
- Vancouver, BC
- Montreal, QC
- Calgary, AB
- Ottawa, ON
- And 100+ more cities

---

## **🔧 TROUBLESHOOTING**

### **App Won't Start:**
- Check Python version (3.8+ required)
- Install dependencies: `pip install -r requirements.txt`
- Check port 5000 is available

### **Login Issues:**
- Use exact credentials: admin@jobsprint.com / admin123
- Clear browser cookies if needed
- Check browser console for errors

### **Job Search Issues:**
- Login first before searching
- Try different keywords or locations
- LinkedIn may rate limit requests

---

## **📊 SYSTEM STATUS**

### **✅ VERIFIED WORKING:**
- [x] Health check endpoint
- [x] Frontend loading
- [x] Admin authentication
- [x] User registration
- [x] Job search API
- [x] LinkedIn scraper
- [x] Session management
- [x] Professional UI

### **🎯 READY FOR:**
- [x] Local development
- [x] Feature testing
- [x] User interface testing
- [x] Job search testing
- [x] Admin panel testing

---

## **🎉 SUCCESS!**

**Your JobSprint system is now:**
- ✅ **Completely cleaned up** and organized
- ✅ **All components working** perfectly
- ✅ **Ready for development** and testing
- ✅ **Professional quality** user experience
- ✅ **Zero external dependencies** for basic operation

**Start the app with `python app.py` and visit http://127.0.0.1:5000 to begin!** 🚀
