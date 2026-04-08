# Stripe Integration Setup Guide

## 🎯 Overview

Your Nurva.AI app now has a complete subscription system that:
- ✅ Tracks free users (3 messages limit)
- ✅ Accepts payments via Stripe
- ✅ Auto-updates subscription status via webhooks
- ✅ Stores payment history
- ✅ User profile with subscription management
- ✅ Automatic renewal on Stripe

---

## 📋 What You Need To Do

### Step 1: Get Stripe API Keys

1. Go to **https://dashboard.stripe.com/**
2. Log in to your account
3. Click **Developers** in the left sidebar
4. Click **API Keys**
5. You'll see:
   - **Publishable Key** (starts with `pk_live_` or `pk_test_`)
   - **Secret Key** (starts with `sk_live_` or `sk_test_`)

### Step 2: Add Keys To .env File

Open `/Users/sami/Desktop/Nurva AI/nurva_project/.env` and update:

```
STRIPE_PUBLISHABLE_KEY=pk_test_XXXXXXXXXXXX
STRIPE_SECRET_KEY=sk_test_XXXXXXXXXXXX
```

### Step 3: Set Up Webhook

This allows Stripe to notify your app when payments are made.

1. In Stripe Dashboard, go to **Developers → Webhooks**
2. Click **Add endpoint**
3. Enter your URL: `https://yoursite.com/webhook/stripe/`
   - For testing: `http://localhost:8000/webhook/stripe/`
   - For live: Your actual domain
4. Select events to listen for:
   - ✅ `customer.subscription.created`
   - ✅ `customer.subscription.updated`
   - ✅ `customer.subscription.deleted`
   - ✅ `invoice.payment_succeeded`
   - ✅ `invoice.payment_failed`
5. Click **Add endpoint**
6. Copy the **Signing Secret** (starts with `whsec_`)

### Step 4: Add Webhook Secret

Update .env file:

```
STRIPE_WEBHOOK_SECRET=whsec_XXXXXXXXXXXX
```

### Step 5: Update Stripe Product Links

The payment links in `chatbot.html` are already set up:

```javascript
const STRIPE_MONTHLY   = 'https://buy.stripe.com/14AcN5eBX9pl9QvdX1bAs02';
const STRIPE_QUARTERLY = 'https://buy.stripe.com/7sY6oHeBXfNJ2o3aKPbAs01';
const STRIPE_ANNUAL    = 'https://buy.stripe.com/dRmfZh1PbeJF8Mr2ejbAs00';
```

Make sure these match your Stripe products.

---

## 🔄 How Payment Flow Works

### User Journey:

```
1. User registers → Free tier (3 messages)
   ↓
2. Tries to send 4th message → Paywall modal
   ↓
3. Clicks "Monthly" / "Quarterly" / "Yearly"
   ↓
4. Redirected to Stripe payment link → Fills card
   ↓
5. Payment successful
   ↓
6. Stripe sends webhook to your server
   ↓
7. UserProfile.is_paid = True
   ↓
8. User gets unlimited messages ✅
```

---

## 📊 Database Models Created

### UserProfile
- `user` - Django User
- `is_paid` - Boolean (Free or Paid)
- `free_messages_used` - Counter (0-3)
- `stripe_customer_id` - From Stripe
- `stripe_subscription_id` - From Stripe
- `subscription_status` - active, past_due, canceled, etc.
- `current_period_start` - When current billing cycle started
- `current_period_end` - When current billing cycle ends

### Subscription
- Stores subscription details
- Tracks plan type (monthly, quarterly, yearly)
- Stores billing cycle dates
- Tracks cancellation status

### Payment
- Records every transaction
- Stores amount, date, status
- Links to Stripe invoice ID

---

## 🔌 API Endpoints Created

### For Frontend (JavaScript):

```javascript
// Check user's message count and subscription status
GET /api/message-status/
Response: {
  is_paid: true,
  messages_used: 0,
  max_free_messages: 3,
  messages_remaining: 3,
  can_send: true
}

// Increment message count after each chat
POST /api/increment-message/
Response: {
  messages_used: 1,
  messages_remaining: 2,
  can_send: true
}
```

### Stripe Webhook:
```
POST /webhook/stripe/
Listens for payment events and auto-updates database
```

---

## 📱 User Profile Page

New page at `/profile/` shows:
- ✅ Current subscription status
- ✅ Remaining free messages (if free tier)
- ✅ Payment history
- ✅ Subscription dates and renewal info
- ✅ Option to cancel subscription

---

## 🧪 Testing Locally

### Test Cards in Stripe:
```
Successful payment:
Card: 4242 4242 4242 4242
Exp: 04/26
CVC: 424

Failed payment:
Card: 4000 0000 0000 0002
Exp: 04/26
CVC: 424
```

### Test Webhook Locally:

Install Stripe CLI:
```bash
brew install stripe/stripe-cli/stripe
```

Login:
```bash
stripe login
```

Forward webhooks:
```bash
stripe listen --forward-to localhost:8000/webhook/stripe/
```

This gives you a signing secret to use in .env

---

## 🚀 Live Setup Checklist

- [ ] Update Stripe keys in .env (live keys, not test)
- [ ] Set webhook endpoint to your live domain
- [ ] Test a real payment
- [ ] Verify user gets unlimited access after payment
- [ ] Check payment history in user profile
- [ ] Enable email notifications in Stripe

---

## ⚙️ Configuration Notes

### Auto-Renewal
✅ Automatically handled by Stripe
- Stripe renews subscription at `current_period_end`
- Webhook confirms renewal → Database updates
- No manual configuration needed

### Subscription Cancellation
User can cancel in profile page (coming soon - redirects to Stripe portal)
- Cancellation queues for end of billing period
- User still has access until period ends
- Status changes to `cancel_at_period_end` = true

### Failed Payments
If payment fails:
- Stripe retries automatically
- If all retries fail, subscription status → `past_due`
- User gets last month of access while Stripe retries

---

## 📚 Response Examples

### User Story: Free → Paid

**Before Payment:**
```json
{
  "is_paid": false,
  "messages_used": 3,
  "messages_remaining": 0,
  "can_send": false
}
```

**After Payment (Webhook received):**
```json
{
  "is_paid": true,
  "subscription_status": "active",
  "current_period_end": "2026-05-04T12:00:00Z",
  "messages_remaining": ∞
}
```

---

## 🆘 Troubleshooting

### Webhook not triggering?
- Check Stripe Dashboard → Webhooks → Event log
- Verify signing secret in .env matches Stripe
- For local testing, use `stripe listen` CLI

### User not marked as paid after payment?
- Check webhook was received (Stripe Dashboard)
- Check database: `UserProfile.stripe_customer_id` populated?
- Check logs for errors

### Payment link not working?
- Verify payment links in chatbot.html are correct
- Check they match your Stripe products
- Test with Stripe test cards

---

## 📞 Need Help?

Check these files for implementation details:
- Models: `/chat/models.py`
- Views/Webhooks: `/chat/views.py`
- URLs: `/chat/urls.py`
- Profile Template: `/chat/templates/chat/profile.html`
- Chatbot Integration: `/chat/templates/chat/chatbot.html`

