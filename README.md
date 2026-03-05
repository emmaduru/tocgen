# TOC Generator — Django SaaS App

A Django-based SaaS application for adding a Table of Contents to any PDF.
Files are processed entirely in-browser and never stored on the server.

## Features

- 🔐 Email/password authentication with email verification
- 🔗 Google OAuth sign-in
- 💳 Stripe subscription management (Pro & Premium tiers)
- 🎚️ Four plan tiers with enforced limits
- 📊 User dashboard with usage tracking
- 🚫 No file storage — only upload metadata is stored for rate limiting
- 📄 PDF editor runs 100% in the browser (pdf.js + pdf-lib)

## Plan Tiers

| Plan      | Max File | Uploads/Day | Watermark | Price    |
|-----------|----------|-------------|-----------|----------|
| Guest     | 5 MB     | 1           | Yes       | Free     |
| Free      | 10 MB    | 5           | Yes       | Free     |
| Pro       | 250 MB   | Unlimited   | No        | $9/month |
| Premium   | 1 GB     | Unlimited   | No        | $24/month|

---

## Quick Start

### 1. Clone & set up environment

```bash
git clone <your-repo>
cd tocgen
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your values (see below)
```

### 3. Run database migrations

```bash
python manage.py migrate
python manage.py loaddata core/fixtures/initial_data.json
python manage.py createsuperuser
```

### 4. Start the development server

```bash
python manage.py runserver
```

Visit http://localhost:8000

---

## Environment Configuration

### Required for all features

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Django secret key (generate with `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`) |
| `DEBUG` | `True` in development, `False` in production |

### Email (verification + password reset)

For **development**, the default `console` backend prints emails to your terminal — no setup needed.

For **production**, use an SMTP service:
- [SendGrid](https://sendgrid.com) — free tier available
- [Mailgun](https://mailgun.com)
- [Postmark](https://postmarkapp.com)

### Google OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create project → Enable Google+ API
3. Create **OAuth 2.0 Client ID** (Web application type)
4. Add Authorised redirect URI:
   - Development: `http://localhost:8000/accounts/google/login/callback/`
   - Production: `https://yourdomain.com/accounts/google/login/callback/`
5. Copy Client ID and Secret to `.env`

> **After running migrations**, also update the Site in Django admin:
> Admin → Sites → Change `localhost:8000` to your actual domain in production.

### Stripe Setup

1. Create account at [stripe.com](https://stripe.com)
2. Get API keys from [Dashboard → Developers → API keys](https://dashboard.stripe.com/apikeys)
3. Create two Products in [Dashboard → Products](https://dashboard.stripe.com/products):
   - **Pro**: $9.00 / month → copy the **Price ID** → `STRIPE_PRICE_PRO`
   - **Premium**: $24.00 / month → copy the **Price ID** → `STRIPE_PRICE_PREMIUM`
4. Set up the **Customer Portal** in [Dashboard → Settings → Billing → Customer portal](https://dashboard.stripe.com/settings/billing/portal)
5. Set up the **webhook** (see below)

#### Stripe Webhook (Development)

Install the [Stripe CLI](https://stripe.com/docs/stripe-cli):
```bash
stripe login
stripe listen --forward-to localhost:8000/stripe/webhook/
# Copy the whsec_... secret → STRIPE_WEBHOOK_SECRET in .env
```

#### Stripe Webhook (Production)

In Dashboard → Developers → Webhooks → Add endpoint:
- URL: `https://yourdomain.com/stripe/webhook/`
- Events to listen to:
  - `customer.subscription.created`
  - `customer.subscription.updated`
  - `customer.subscription.deleted`
  - `invoice.payment_failed`

---

## Project Structure

```
tocgen/
├── manage.py
├── requirements.txt
├── .env.example
├── tocgen/                  # Django project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── core/                    # Main app
│   ├── models.py            # UserProfile, UploadRecord
│   ├── views.py             # All views including Stripe
│   ├── urls.py
│   ├── admin.py
│   ├── signals.py           # Auto-create UserProfile
│   ├── context_processors.py
│   └── fixtures/
│       └── initial_data.json
├── templates/
│   ├── base.html            # Base layout
│   ├── core/
│   │   ├── landing.html     # Landing page with pricing
│   │   ├── dashboard.html   # User dashboard
│   │   └── editor.html      # In-browser PDF editor
│   ├── account/             # django-allauth templates
│   │   ├── login.html
│   │   ├── signup.html
│   │   └── ...
│   └── socialaccount/
│       └── signup.html
└── static/
```

---

## Production Deployment

### Using Gunicorn + Nginx

```bash
# Set in .env
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
# ... SMTP settings

# Collect static files
python manage.py collectstatic

# Run with gunicorn
gunicorn tocgen.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

### Environment variables for production

```
SECRET_KEY=<long-random-string>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
```

### One-click platforms

This app is ready for deployment on:
- **Railway** — add `Procfile`: `web: gunicorn tocgen.wsgi`
- **Render** — Build: `pip install -r requirements.txt && python manage.py migrate`, Start: `gunicorn tocgen.wsgi`
- **Heroku** — standard Django deployment

---

## Extending Limits

Edit `PLAN_LIMITS` in `settings.py`:

```python
PLAN_LIMITS = {
    'anonymous': {'max_mb': 5,    'daily_uploads': 1,    'watermark': True},
    'free':      {'max_mb': 10,   'daily_uploads': 5,    'watermark': True},
    'pro':       {'max_mb': 250,  'daily_uploads': None, 'watermark': False},
    'premium':   {'max_mb': 1024, 'daily_uploads': None, 'watermark': False},
}
```

`daily_uploads: None` = unlimited.
