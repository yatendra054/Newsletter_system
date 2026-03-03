# Market Insights - Newsletter System

A robust and high-performance Django-based newsletter system designed for managing subscribers, creating campaigns, and dispatching emails efficiently using multi-threading.

## Features

- **Subscriber Management**: Handled via a clean UI and automated welcome emails.
- **Campaign Archive**: A dedicated section on the home page to view previous newsletters.
- **Admin Integration**: Manage all data and trigger campaign sends directly from the Django Admin.
- **Dynamic Email Rendering**: Professional HTML emails rendered from templates with personalized unsubscribe links.
- **Real-Time Logging**: Comprehensive logging to `django.log` for auditing and debugging.

## Optimization: Parallel Email Dispatch

To ensure high performance as the subscriber list grows, this system implements a **Pub-Sub architecture with Multi-threading**.

### How it Works:
1. **Pub-Sub (Signals)**: When a campaign is triggered (via Admin or UI), the system fires a custom `dispatch_campaign` signal. This decouples the user-facing action from the heavy processing logic.
2. **Multi-threading**: The signal receiver uses Python's `ThreadPoolExecutor` to process the email list.
3. **Concurrency**: Instead of sending emails one-by-one, the system utilizes **10 parallel workers** to dispatch emails simultaneously.

### Optimization Steps Taken:
- **Single-Subscriber Isolation**: Extracted logic into `send_campaign_to_single_subscriber` for thread safety and error containment.
- **Error Robustness**: Each thread is wrapped in a `try/except` block; a failure for one subscriber does not affect others.
- **Rate Limit Compliance Management**: The worker count is set to 10 to balance speed with SMTP provider (e.g., Gmail) rate limits.
- **Efficient Context Handling**: Data is passed to threads in a way that minimizes redundant database calls.

## Setup Instructions

### 1. Environment Setup
```bash
python -m venv env
source env/Scripts/activate  # Windows
pip install django
```

### 2. Configuration
Update `config/settings.py` with your SMTP details:
```python
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
SITE_URL = 'http://127.0.0.1:8000'
```

### 3. Database Initialization
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 4. Running the Project
```bash
python manage.py runserver
```

## Usage

- **Subscribe**: Use the home page form at `/`.
- **Manage Data**: Log in at `/admin/` to add Subscribers or Campaigns.
- **Send Campaigns**: Use the "Send Latest Campaign" button on the home page or use the **Admin Action** "Send selected campaigns" in the Campaign list.
