from django.shortcuts import render, redirect
from django.views import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.decorators import method_decorator
import os
import json
from dotenv import load_dotenv
import stripe
from .models import UserProfile, Subscription, Payment
from datetime import datetime, timedelta
from django.utils.timezone import make_aware
import logging

load_dotenv()

# Configure Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

# ===== LOGGING SETUP =====
LOG_FILE = os.path.join(os.path.dirname(__file__), '../payments.log')

def log_payment(message):
    """Log payment verification attempts to a file"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] {message}\n"
    
    with open(LOG_FILE, 'a') as f:
        f.write(log_entry)
    
    print(log_entry.strip())  # Also print to console




class HomeView(View):
    """Renders the home page"""
    def get(self, request):
        context = {
            'app_name': os.getenv('APP_NAME', 'Nurva AI'),
        }
        return render(request, 'chat/home.html', context)


class LoginView(View):
    """Handles user login"""
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('chat:chatbot')
        context = {
            'app_name': os.getenv('APP_NAME', 'Nurva AI'),
        }
        return render(request, 'chat/login.html', context)
    
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Successfully logged in!')
            return redirect('chat:chatbot')
        else:
            messages.error(request, 'Invalid username or password.')
            context = {
                'app_name': os.getenv('APP_NAME', 'Nurva AI'),
            }
            return render(request, 'chat/login.html', context)


class RegisterView(View):
    """Handles user registration"""
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('chat:chatbot')
        context = {
            'app_name': os.getenv('APP_NAME', 'Nurva AI'),
        }
        return render(request, 'chat/register.html', context)
    
    def post(self, request):
        first_name = request.POST.get('first_name', '').strip()
        email = request.POST.get('email', '').strip()
        username = request.POST.get('username', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        
        # Validation
        errors = []
        
        if not first_name:
            errors.append('Full name is required.')
        
        if not email:
            errors.append('Email is required.')
        elif User.objects.filter(email=email).exists():
            errors.append('This email is already registered.')
        
        if not username:
            errors.append('Username is required.')
        elif len(username) < 3:
            errors.append('Username must be at least 3 characters long.')
        elif User.objects.filter(username=username).exists():
            errors.append('This username is already taken.')
        
        if not password1:
            errors.append('Password is required.')
        elif len(password1) < 6:
            errors.append('Password must be at least 6 characters long.')
        
        if password1 != password2:
            errors.append('Passwords do not match.')
        
        if errors:
            context = {
                'app_name': os.getenv('APP_NAME', 'Nurva AI'),
                'errors': errors,
                'first_name': first_name,
                'email': email,
                'username': username,
            }
            return render(request, 'chat/register.html', context)
        
        # Create user
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=first_name
            )
            # Create user profile for tracking free messages
            UserProfile.objects.get_or_create(user=user)
            
            login(request, user)
            messages.success(request, 'Account created successfully! Welcome to Nurva.AI')
            return redirect('chat:chatbot')
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
            context = {
                'app_name': os.getenv('APP_NAME', 'Nurva AI'),
            }
            return render(request, 'chat/register.html', context)


class LogoutView(View):
    """Handles user logout"""
    @method_decorator(login_required(login_url='chat:login'))
    def get(self, request):
        logout(request)
        messages.success(request, 'Successfully logged out!')
        return redirect('chat:home')


class ChatbotView(View):
    """Renders the chatbot interface"""
    @method_decorator(login_required(login_url='chat:login'))
    def get(self, request):
        context = {
            'app_name': os.getenv('APP_NAME', 'Nurva AI'),
        }
        return render(request, 'chat/chatbot.html', context)


@csrf_exempt
@require_http_methods(['GET'])
def get_api_key(request):
    """Get Anthropic API key from backend"""
    api_key = os.getenv('ANTHROPIC_API_KEY', '')
    
    if not api_key:
        return JsonResponse({
            'success': False,
            'error': 'API key not configured'
        }, status=400)
    
    return JsonResponse({
        'success': True,
        'api_key': api_key
    })


@require_http_methods(['GET'])
@login_required(login_url='chat:login')
def get_message_status(request):
    """Get user's message count and paid status"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Auto-verify payment if user isn't marked as paid yet
    if not profile.is_paid:
        try:
            user_email = request.user.email
            log_payment(f"🔍 Checking Stripe for {request.user.username} ({user_email})")
            customers = stripe.Customer.search(query=f"email:'{user_email}'")
            log_payment(f"   Found {len(customers.data)} Stripe customers")
            
            for customer in customers.data:
                subscriptions = stripe.Subscription.list(
                    customer=customer.id,
                    status='active',
                    limit=1
                )
                
                if subscriptions.data and len(subscriptions.data) > 0:
                    subscription = subscriptions.data[0]
                    log_payment(f"✅ FOUND ACTIVE SUBSCRIPTION: {subscription.id} for {request.user.username}")
                    
                    # Update profile
                    profile.stripe_customer_id = customer.id
                    profile.is_paid = True
                    profile.subscription_status = 'active'
                    profile.free_messages_used = 0
                    profile.save()
                    log_payment(f"   Database Updated: is_paid={profile.is_paid}, status={profile.subscription_status}")
                    
                    # Create Subscription record
                    try:
                        period_start = make_aware(datetime.now())
                        period_end = make_aware(datetime.now()) + timedelta(days=30)
                        
                        if hasattr(subscription, 'current_period_start') and subscription.current_period_start:
                            period_start = make_aware(datetime.fromtimestamp(subscription.current_period_start))
                        if hasattr(subscription, 'current_period_end') and subscription.current_period_end:
                            period_end = make_aware(datetime.fromtimestamp(subscription.current_period_end))
                        
                        Subscription.objects.update_or_create(
                            user=request.user,
                            defaults={
                                'stripe_subscription_id': subscription.id,
                                'stripe_customer_id': customer.id,
                                'plan': subscription.items.data[0].plan.interval if subscription.items.data else 'monthly',
                                'status': subscription.status,
                                'current_period_start': period_start,
                                'current_period_end': period_end,
                            }
                        )
                        log_payment(f"   ✅ Created Subscription record")
                    except Exception as sub_error:
                        log_payment(f"   ⚠️ Could not create Subscription: {str(sub_error)}")
                        import traceback
                        traceback.print_exc()
                    
                    # Create Payment record for payment history
                    try:
                        plan_name = subscription.items.data[0].plan.interval if subscription.items.data else 'monthly'
                        amount = subscription.items.data[0].price.unit_amount / 100 if subscription.items.data else 0
                        
                        Payment.objects.get_or_create(
                            stripe_payment_id=subscription.id,
                            defaults={
                                'user': request.user,
                                'stripe_invoice_id': subscription.latest_invoice if hasattr(subscription, 'latest_invoice') else None,
                                'amount': amount,
                                'currency': 'usd',
                                'plan': plan_name,
                                'status': 'succeeded',
                                'paid_at': make_aware(datetime.fromtimestamp(subscription.current_period_start)) if hasattr(subscription, 'current_period_start') and subscription.current_period_start else None,
                            }
                        )
                        log_payment(f"   ✅ Created Payment record: ${amount} {plan_name}")
                    except Exception as pay_error:
                        log_payment(f"   ⚠️ Could not create Payment: {str(pay_error)}")
                    
                    break
                
        except Exception as e:
            log_payment(f"❌ ERROR during verification: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # Determine if user is paid based on subscription status
    is_paid = profile.is_subscription_active()
    
    # Get subscription plan if user is paid
    subscription = Subscription.objects.filter(user=request.user).first()
    subscription_plan = subscription.plan if subscription and subscription.plan else 'free'
    
    # Calculate messages remaining
    if is_paid:
        messages_remaining = 999999  # Use large number instead of infinity for JSON
    else:
        messages_remaining = profile.messages_remaining()
    
    response_data = {
        'success': True,
        'is_paid': is_paid,
        'messages_used': profile.free_messages_used,
        'max_free_messages': profile.max_free_messages,
        'messages_remaining': messages_remaining,
        'can_send': profile.can_send_message(),
        'subscription_status': profile.subscription_status,
        'subscription_plan': subscription_plan,
        'debug': {
            'user': request.user.username,
            'created': created,
            'profile_is_paid': profile.is_paid,
            'profile_status': profile.subscription_status,
        }
    }
    
    log_payment(f"   FINAL STATUS: is_paid={is_paid}, messages_used={profile.free_messages_used}, can_send={profile.can_send_message()}")
    return JsonResponse(response_data)


@require_http_methods(['POST'])
@login_required(login_url='chat:login')
def increment_message_count(request):
    """Increment user's message count"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Check if user can send message
    if not profile.can_send_message():
        print(f"[DEBUG] User {request.user.username} cannot send message: {profile.free_messages_used}/{profile.max_free_messages}")
        return JsonResponse({
            'success': False,
            'error': 'You have reached the free message limit',
            'can_send': False,
            'messages_used': profile.free_messages_used,
            'messages_remaining': 0
        }, status=403)
    
    # Increment count
    profile.free_messages_used += 1
    profile.save()
    
    print(f"[DEBUG] User {request.user.username} message count incremented: {profile.free_messages_used}/{profile.max_free_messages}")
    
    return JsonResponse({
        'success': True,
        'messages_used': profile.free_messages_used,
        'messages_remaining': profile.messages_remaining(),
        'can_send': profile.can_send_message()
    })


class UserProfileView(View):
    """Display user profile with subscription and payment history"""
    @method_decorator(login_required(login_url='chat:login'))
    def get(self, request):
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        subscription = Subscription.objects.filter(user=request.user).first()
        payments = Payment.objects.filter(user=request.user).order_by('-created_at')[:10]
        
        context = {
            'app_name': os.getenv('APP_NAME', 'Nurva AI'),
            'profile': profile,
            'subscription': subscription,
            'payments': payments,
            'is_paid': profile.is_paid,
        }
        return render(request, 'chat/profile.html', context)


@require_http_methods(['POST'])
@login_required(login_url='chat:login')
def verify_payment(request):
    """Verify payment with Stripe and update subscription status"""
    try:
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        # Try to find Stripe customer by email
        user_email = request.user.email
        log_payment(f"🔄 VERIFY: Checking payment for {request.user.username} ({user_email})")
        
        # Search for existing customer by email
        customers = stripe.Customer.search(query=f"email:'{user_email}'")
        log_payment(f"   Found {len(customers.data)} Stripe customers with email {user_email}")
        
        # Try each customer to find one with an active subscription
        for customer in customers.data:
            log_payment(f"   Checking customer {customer.id} ({customer.name})")
            
            # Check for active subscriptions
            subscriptions = stripe.Subscription.list(
                customer=customer.id,
                status='active',
                limit=10
            )
            
            if subscriptions.data and len(subscriptions.data) > 0:
                # Take the first active subscription
                subscription = subscriptions.data[0]
                log_payment(f"   ✅ Found active subscription: {subscription.id}")
                
                # Update profile with Stripe customer ID
                profile.stripe_customer_id = customer.id
                profile.is_paid = True
                profile.subscription_status = 'active'
                profile.free_messages_used = 0
                profile.save()
                
                # Create Subscription record
                try:
                    period_start = make_aware(datetime.now())
                    period_end = make_aware(datetime.now()) + timedelta(days=30)
                    
                    if hasattr(subscription, 'current_period_start') and subscription.current_period_start:
                        period_start = make_aware(datetime.fromtimestamp(subscription.current_period_start))
                    if hasattr(subscription, 'current_period_end') and subscription.current_period_end:
                        period_end = make_aware(datetime.fromtimestamp(subscription.current_period_end))
                    
                    Subscription.objects.update_or_create(
                        user=request.user,
                        defaults={
                            'stripe_subscription_id': subscription.id,
                            'stripe_customer_id': customer.id,
                            'plan': subscription.items.data[0].plan.interval if subscription.items.data else 'monthly',
                            'status': subscription.status,
                            'current_period_start': period_start,
                            'current_period_end': period_end,
                        }
                    )
                    log_payment(f"   ✅ Created Subscription record")
                except Exception as sub_error:
                    log_payment(f"   ⚠️ Could not create Subscription: {str(sub_error)}")
                    import traceback
                    traceback.print_exc()
                
                # Create Payment record for payment history
                try:
                    plan_name = subscription.items.data[0].plan.interval if subscription.items.data else 'monthly'
                    amount = subscription.items.data[0].price.unit_amount / 100 if subscription.items.data else 0
                    
                    Payment.objects.get_or_create(
                        stripe_payment_id=subscription.id,
                        defaults={
                            'user': request.user,
                            'stripe_invoice_id': subscription.latest_invoice if hasattr(subscription, 'latest_invoice') else None,
                            'amount': amount,
                            'currency': 'usd',
                            'plan': plan_name,
                            'status': 'succeeded',
                            'paid_at': make_aware(datetime.fromtimestamp(subscription.current_period_start)) if hasattr(subscription, 'current_period_start') and subscription.current_period_start else None,
                        }
                    )
                    log_payment(f"   ✅ Created Payment record: ${amount} {plan_name}")
                except Exception as pay_error:
                    log_payment(f"   ⚠️ Could not create Payment: {str(pay_error)}")
                
                log_payment(f"✅ VERIFIED: Subscription {subscription.id} is active for {request.user.username}")
                
                return JsonResponse({
                    'success': True,
                    'message': 'Payment verified! Subscription activated.',
                    'is_paid': True,
                    'subscription_status': 'active',
                    'messages_remaining': 999999
                })
        
        log_payment(f"❌ NO SUBSCRIPTION: No active subscriptions found for {user_email}")
        
        # No active subscription found
        return JsonResponse({
            'success': False,
            'message': 'No active subscription found. Please check your email for confirmation.',
            'is_paid': False
        }, status=400)
        
    except Exception as e:
        log_payment(f"❌ ERROR: Payment verification failed for {request.user.username}: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(['POST'])
@login_required(login_url='chat:login')
def cancel_subscription(request):
    """Cancel user's Stripe subscription"""
    try:
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        subscription = Subscription.objects.filter(user=request.user).first()
        
        if not subscription or not subscription.stripe_subscription_id:
            return JsonResponse({
                'success': False,
                'error': 'No active subscription found'
            }, status=404)
        
        # Cancel the Stripe subscription
        log_payment(f"🔄 Canceling subscription {subscription.stripe_subscription_id} for {request.user.username}")
        
        stripe_sub = stripe.Subscription.delete(subscription.stripe_subscription_id)
        
        # Update our records
        profile.is_paid = False
        profile.subscription_status = 'canceled'
        profile.save()
        
        subscription.status = 'canceled'
        subscription.save()
        
        log_payment(f"✅ CANCELED: Subscription {subscription.stripe_subscription_id} for {request.user.username}")
        
        return JsonResponse({
            'success': True,
            'message': 'Subscription canceled successfully. You can resubscribe anytime.',
            'is_paid': False
        })
        
    except Exception as e:
        log_payment(f"❌ ERROR canceling subscription: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(['POST'])
def stripe_webhook(request):
    """Handle Stripe webhook events for subscription updates"""
    stripe_webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, stripe_webhook_secret
        )
    except ValueError:
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError:
        return JsonResponse({'error': 'Invalid signature'}, status=400)
    
    # Handle subscription events
    if event['type'] == 'customer.subscription.updated':
        subscription_data = event['data']['object']
        update_subscription_from_stripe(subscription_data)
    
    elif event['type'] == 'customer.subscription.deleted':
        subscription_data = event['data']['object']
        cancel_subscription_from_stripe(subscription_data)
    
    elif event['type'] == 'customer.subscription.created':
        subscription_data = event['data']['object']
        create_subscription_from_stripe(subscription_data)
    
    elif event['type'] == 'invoice.payment_succeeded':
        invoice_data = event['data']['object']
        handle_payment_succeeded(invoice_data)
    
    elif event['type'] == 'invoice.payment_failed':
        invoice_data = event['data']['object']
        handle_payment_failed(invoice_data)
    
    return JsonResponse({'success': True})


def update_subscription_from_stripe(subscription_data):
    """Update subscription status from Stripe event"""
    stripe_sub_id = subscription_data.get('id')
    
    if not stripe_sub_id:
        return  # Missing required data
    
    try:
        subscription = Subscription.objects.get(stripe_subscription_id=stripe_sub_id)
        subscription.status = subscription_data.get('status', 'incomplete')
        
        # Safely update dates if available
        if subscription_data.get('current_period_start'):
            subscription.current_period_start = make_aware(
                datetime.fromtimestamp(subscription_data['current_period_start'])
            )
        if subscription_data.get('current_period_end'):
            subscription.current_period_end = make_aware(
                datetime.fromtimestamp(subscription_data['current_period_end'])
            )
        
        subscription.cancel_at_period_end = subscription_data.get('cancel_at_period_end', False)
        subscription.save()
        
        # Update UserProfile
        profile = subscription.user.profile
        profile.subscription_status = subscription.status
        profile.is_paid = subscription.status in ['active', 'past_due']
        if subscription.current_period_start:
            profile.current_period_start = subscription.current_period_start
        if subscription.current_period_end:
            profile.current_period_end = subscription.current_period_end
        profile.save()
    except Subscription.DoesNotExist:
        pass
    except Exception as e:
        log_payment(f"❌ Error updating subscription from Stripe: {str(e)}")


def create_subscription_from_stripe(subscription_data):
    """Create subscription record from Stripe event"""
    stripe_cust_id = subscription_data.get('customer')
    stripe_sub_id = subscription_data.get('id')
    
    if not stripe_cust_id or not stripe_sub_id:
        return  # Missing required data
    
    try:
        profile = UserProfile.objects.get(stripe_customer_id=stripe_cust_id)
        
        # Determine plan from items
        plan_name = 'monthly'  # default
        if subscription_data.get('items', {}).get('data'):
            price_data = subscription_data['items']['data'][0].get('price', {})
            recurring = price_data.get('recurring', {})
            if recurring.get('interval') == 'year':
                plan_name = 'yearly'
            elif recurring.get('interval_count') == 3:
                plan_name = 'quarterly'
        
        # Get date fields safely
        period_start = make_aware(datetime.now())
        period_end = make_aware(datetime.now()) + timedelta(days=30)
        
        if subscription_data.get('current_period_start'):
            period_start = make_aware(datetime.fromtimestamp(subscription_data['current_period_start']))
        if subscription_data.get('current_period_end'):
            period_end = make_aware(datetime.fromtimestamp(subscription_data['current_period_end']))
        
        subscription, created = Subscription.objects.get_or_create(
            stripe_subscription_id=stripe_sub_id,
            defaults={
                'user': profile.user,
                'stripe_customer_id': stripe_cust_id,
                'plan': plan_name,
                'status': subscription_data.get('status', 'incomplete'),
                'current_period_start': period_start,
                'current_period_end': period_end,
            }
        )
        
        if created:
            profile.is_paid = True
            profile.stripe_subscription_id = stripe_sub_id
            profile.subscription_status = subscription_data.get('status', 'incomplete')
            if subscription_data.get('created'):
                profile.subscription_start_date = make_aware(
                    datetime.fromtimestamp(subscription_data['created'])
                )
            profile.save()
    except UserProfile.DoesNotExist:
        pass
    except Exception as e:
        log_payment(f"❌ Error creating subscription from Stripe: {str(e)}")


def cancel_subscription_from_stripe(subscription_data):
    """Mark subscription as canceled from Stripe event"""
    stripe_sub_id = subscription_data.get('id')
    
    if not stripe_sub_id:
        return  # Missing required data
    
    try:
        subscription = Subscription.objects.get(stripe_subscription_id=stripe_sub_id)
        subscription.status = 'canceled'
        
        if subscription_data.get('canceled_at'):
            subscription.canceled_at = make_aware(datetime.fromtimestamp(subscription_data['canceled_at']))
        
        subscription.save()
        
        profile = subscription.user.profile
        profile.is_paid = False
        profile.subscription_status = 'canceled'
        profile.save()
    except Subscription.DoesNotExist:
        pass
    except Exception as e:
        log_payment(f"❌ Error canceling subscription from Stripe: {str(e)}")


def handle_payment_succeeded(invoice_data):
    """Record successful payment"""
    stripe_cust_id = invoice_data.get('customer')
    stripe_inv_id = invoice_data.get('id')
    stripe_pay_id = invoice_data.get('payment_intent') or stripe_inv_id  # Use invoice ID as fallback
    
    if not stripe_cust_id or not stripe_inv_id or not stripe_pay_id:
        return  # Missing required data
    
    try:
        profile = UserProfile.objects.get(stripe_customer_id=stripe_cust_id)
        amount = invoice_data.get('amount_paid', invoice_data.get('total', 0)) / 100  # Convert from cents
        
        # Get payment timestamp if available
        paid_at = None
        if invoice_data.get('paid_at'):
            paid_at = make_aware(datetime.fromtimestamp(invoice_data['paid_at']))
        
        payment, created = Payment.objects.get_or_create(
            stripe_payment_id=stripe_pay_id,
            defaults={
                'user': profile.user,
                'stripe_invoice_id': stripe_inv_id,
                'amount': amount,
                'plan': 'subscription',
                'status': 'succeeded',
                'paid_at': paid_at
            }
        )
    except UserProfile.DoesNotExist:
        pass
    except Exception as e:
        log_payment(f"❌ Error handling payment succeeded: {str(e)}")


def handle_payment_failed(invoice_data):
    """Record failed payment"""
    stripe_cust_id = invoice_data.get('customer')
    stripe_inv_id = invoice_data.get('id')
    stripe_pay_id = invoice_data.get('payment_intent') or stripe_inv_id  # Use invoice ID as fallback
    
    if not stripe_cust_id or not stripe_inv_id or not stripe_pay_id:
        return  # Missing required data
    
    try:
        profile = UserProfile.objects.get(stripe_customer_id=stripe_cust_id)
        amount = invoice_data.get('amount_due', invoice_data.get('total', 0)) / 100
        
        payment, created = Payment.objects.get_or_create(
            stripe_payment_id=stripe_pay_id,
            defaults={
                'user': profile.user,
                'stripe_invoice_id': stripe_inv_id,
                'amount': amount,
                'plan': 'subscription',
                'status': 'failed',
            }
        )
    except UserProfile.DoesNotExist:
        pass
    except Exception as e:
        log_payment(f"❌ Error handling payment failed: {str(e)}")



