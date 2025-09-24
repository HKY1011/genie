# 🗓️ Google Calendar API Setup Guide

This guide will help you set up Google Calendar API integration for Genie, enabling real-time availability checking and automatic mini-task scheduling.

## 📋 Prerequisites

- Google account with access to Google Calendar
- Google Cloud Console access
- Python 3.7+ with pip

## 🚀 Step-by-Step Setup

### Step 1: Create Google Cloud Project

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/
   - Sign in with your Google account

2. **Create a New Project**
   - Click on the project dropdown at the top
   - Click "New Project"
   - Enter a project name (e.g., "Genie Calendar Integration")
   - Click "Create"

3. **Select Your Project**
   - Make sure your new project is selected in the dropdown

### Step 2: Enable Google Calendar API

1. **Navigate to APIs & Services**
   - In the left sidebar, click "APIs & Services" > "Library"

2. **Search for Google Calendar API**
   - In the search bar, type "Google Calendar API"
   - Click on "Google Calendar API" from the results

3. **Enable the API**
   - Click "Enable" button
   - Wait for the API to be enabled

### Step 3: Create OAuth2 Credentials

1. **Go to Credentials**
   - In the left sidebar, click "APIs & Services" > "Credentials"

2. **Create Credentials**
   - Click "Create Credentials" button
   - Select "OAuth client ID"

3. **Configure OAuth Consent Screen**
   - If prompted, click "Configure Consent Screen"
   - Choose "External" user type
   - Fill in required information:
     - App name: "Genie AI Assistant"
     - User support email: Your email
     - Developer contact information: Your email
   - Click "Save and Continue"
   - Skip scopes section, click "Save and Continue"
   - Add test users if needed, click "Save and Continue"
   - Click "Back to Dashboard"

4. **Create OAuth Client ID**
   - Application type: "Desktop application"
   - Name: "Genie Calendar Integration"
   - Click "Create"

5. **Download Credentials**
   - Click "Download" button (JSON format)
   - Save the file as `credentials.json` in your `genie_backend/` directory

### Step 4: Install Python Dependencies

Run the following command in your terminal:

```bash
pip3 install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

### Step 5: Test the Integration

1. **Run the Test Suite**
   ```bash
   cd genie_backend
   python3 test_google_calendar_api.py
   ```

2. **First-Time Authentication**
   - When you run the test for the first time, a browser window will open
   - Sign in with your Google account
   - Grant permission to access your Google Calendar
   - The authentication token will be saved as `token.json`

3. **Verify Setup**
   - The test should show successful authentication
   - You should see your calendar information
   - Free/busy checking should work
   - Event creation/update/deletion should work

## 📁 File Structure

After setup, your `genie_backend/` directory should contain:

```
genie_backend/
├── credentials.json          # OAuth2 credentials (downloaded from Google Cloud)
├── token.json               # Authentication token (created automatically)
├── integrations/
│   └── google_calendar_api.py
├── test_google_calendar_api.py
└── GOOGLE_CALENDAR_SETUP.md
```

## 🔧 Configuration Options

### Custom Calendar ID

By default, the integration uses your primary calendar. To use a different calendar:

```python
from integrations.google_calendar_api import GoogleCalendarAPI

# Use a specific calendar
calendar_api = GoogleCalendarAPI(calendar_id="your_calendar_id@group.calendar.google.com")
```

### Custom Credentials Path

If you want to store credentials in a different location:

```python
calendar_api = GoogleCalendarAPI(
    credentials_path="/path/to/your/credentials.json",
    token_path="/path/to/your/token.json"
)
```

### Multiple Calendars

To check availability across multiple calendars:

```python
# Check multiple calendars
free_busy = calendar_api.get_free_busy(
    start_datetime=datetime.now(),
    end_datetime=datetime.now() + timedelta(days=7),
    calendar_ids=[
        "primary",
        "work@company.com",
        "personal@example.com"
    ]
)
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. "Credentials file not found"
- **Solution**: Make sure `credentials.json` is in the correct directory
- **Check**: File should be in `genie_backend/credentials.json`

#### 2. "API not enabled"
- **Solution**: Enable Google Calendar API in Google Cloud Console
- **Steps**: Go to APIs & Services > Library > Google Calendar API > Enable

#### 3. "OAuth consent screen not configured"
- **Solution**: Configure the OAuth consent screen
- **Steps**: Go to APIs & Services > OAuth consent screen and complete setup

#### 4. "Invalid credentials"
- **Solution**: Download fresh credentials from Google Cloud Console
- **Steps**: Go to APIs & Services > Credentials > Download JSON

#### 5. "Token expired"
- **Solution**: Delete `token.json` and re-authenticate
- **Steps**: Remove `token.json` file and run the test again

### Error Messages and Solutions

| Error | Solution |
|-------|----------|
| `FileNotFoundError: credentials.json` | Download credentials from Google Cloud Console |
| `HttpError 403: API not enabled` | Enable Google Calendar API |
| `HttpError 401: Invalid credentials` | Check OAuth consent screen configuration |
| `HttpError 400: Invalid request` | Verify calendar ID and permissions |

## 🔒 Security Best Practices

### 1. Keep Credentials Secure
- Never commit `credentials.json` or `token.json` to version control
- Add them to `.gitignore`:
  ```
  # Google Calendar API
  credentials.json
  token.json
  ```

### 2. Use Environment Variables (Optional)
For production deployments, consider using environment variables:

```python
import os

calendar_api = GoogleCalendarAPI(
    credentials_path=os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials.json'),
    token_path=os.getenv('GOOGLE_TOKEN_PATH', 'token.json')
)
```

### 3. Regular Token Refresh
- Tokens automatically refresh when expired
- Keep `token.json` secure and backed up

## 🎯 Integration with Genie

Once the Google Calendar API is set up, you can integrate it with Genie:

### Basic Usage

```python
from integrations.google_calendar_api import GoogleCalendarAPI
from datetime import datetime, timedelta

# Initialize API
calendar_api = GoogleCalendarAPI()

# Check availability
free_busy = calendar_api.get_free_busy(
    start_datetime=datetime.now(),
    end_datetime=datetime.now() + timedelta(days=7)
)

# Create a mini-task event
event_id = calendar_api.create_event(
    summary="[Genie] Build React component",
    description="Follow tutorial and implement authentication",
    start_datetime=datetime.now() + timedelta(hours=1),
    end_datetime=datetime.now() + timedelta(hours=1, minutes=30),
    resource_link="https://react.dev/learn/authentication"
)
```

### Advanced Integration

The Google Calendar API is designed to integrate seamlessly with:
- **GenieOrchestrator**: For scheduling mini-tasks
- **PlanningAgent**: For availability-aware task breakdown
- **SupervisorAgent**: For real-time calendar sync

## 📊 Testing Your Setup

Run the comprehensive test suite:

```bash
python3 test_google_calendar_api.py
```

Expected output:
```
🎯 Google Calendar API Comprehensive Test Suite
============================================================

✅ Authentication
✅ Free/Busy Checking  
✅ Event Creation
✅ Event Retrieval
✅ Event Updating
✅ Event Listing
✅ Event Deletion
✅ Error Handling

📊 Results: 8/8 tests passed

🎉 All tests passed! Google Calendar API integration is working correctly.
✅ Ready for integration with Genie orchestrator
```

## 🚀 Next Steps

After successful setup:

1. **Test the Demo**: Run `python3 integrations/google_calendar_api.py` to see a live demo
2. **Integrate with Genie**: Use the API in your Genie orchestrator for automatic scheduling
3. **Customize**: Adjust timezone, calendar preferences, and event formatting
4. **Scale**: Consider multiple calendar support for team environments

## 📞 Support

If you encounter issues:

1. **Check the test output** for specific error messages
2. **Verify Google Cloud Console** settings
3. **Review this setup guide** for common solutions
4. **Check Google Calendar API documentation** for advanced features

---

**🎉 Congratulations!** Your Google Calendar API integration is now ready for Genie's intelligent task scheduling and real-time availability management. 