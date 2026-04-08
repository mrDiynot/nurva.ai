from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import UserProfile, Subscription, Payment


# ============================================================================
# USER PROFILE ADMIN
# ============================================================================
class UserProfileInline(admin.StackedInline):
    """Inline admin for UserProfile linked to User"""
    model = UserProfile
    extra = 0
    fields = (
        'stripe_customer_id', 'stripe_subscription_id', 'subscription_status',
        'current_period_start', 'current_period_end', 'is_paid',
        'free_messages_used', 'max_free_messages'
    )
    readonly_fields = (
        'stripe_customer_id', 'stripe_subscription_id',
        'current_period_start', 'current_period_end', 'is_paid',
        'free_messages_used', 'max_free_messages'
    )


class PaymentInline(admin.TabularInline):
    """Inline admin for Payments linked to User"""
    model = Payment
    extra = 0
    fields = (
        'amount', 'currency', 'status', 'plan',
        'stripe_payment_id', 'created_at'
    )
    readonly_fields = ('created_at', 'stripe_payment_id')


class SubscriptionInline(admin.TabularInline):
    """Inline admin for Subscriptions linked to User"""
    model = Subscription
    extra = 0
    fields = (
        'plan', 'status', 'current_period_start', 'current_period_end',
        'cancel_at_period_end', 'canceled_at', 'stripe_subscription_id'
    )
    readonly_fields = ('current_period_start', 'current_period_end', 'canceled_at')


# ============================================================================
# ENHANCED USER ADMIN
# ============================================================================
class EnhancedUserAdmin(BaseUserAdmin):
    """Enhanced user admin with subscription and payment views"""
    inlines = (UserProfileInline, SubscriptionInline, PaymentInline)
    list_display = (
        'username', 'email', 'first_name', 'is_active', 'get_subscription_status',
        'get_free_messages', 'date_joined'
    )
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    def get_subscription_status(self, obj):
        """Display subscription status"""
        try:
            profile = obj.profile
            return profile.subscription_status.upper()
        except:
            return "N/A"
    get_subscription_status.short_description = "Subscription Status"
    
    def get_free_messages(self, obj):
        """Display free messages used"""
        try:
            profile = obj.profile
            return f"{profile.free_messages_used}/{profile.max_free_messages}"
        except:
            return "N/A"
    get_free_messages.short_description = "Messages (Used/Limit)"


# ============================================================================
# USER PROFILE ADMIN
# ============================================================================
class UserProfileAdmin(admin.ModelAdmin):
    """Admin interface for UserProfile"""
    list_display = (
        'user', 'subscription_status', 'is_paid', 'free_messages_used',
        'current_period_end', 'stripe_customer_id_short'
    )
    list_filter = ('subscription_status', 'is_paid')
    search_fields = ('user__username', 'user__email', 'stripe_customer_id')
    readonly_fields = (
        'user', 'stripe_customer_id', 'stripe_subscription_id',
        'current_period_start', 'current_period_end', 'is_paid',
        'free_messages_used', 'max_free_messages'
    )
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Subscription Status', {
            'fields': (
                'subscription_status', 'is_paid',
                'current_period_start', 'current_period_end'
            )
        }),
        ('Stripe Integration', {
            'fields': ('stripe_customer_id', 'stripe_subscription_id'),
            'classes': ('collapse',)
        }),
        ('Free Messages Tracking', {
            'fields': ('free_messages_used', 'max_free_messages'),
            'description': 'Free tier message usage'
        }),
    )
    ordering = ('-user__date_joined',)
    
    def stripe_customer_id_short(self, obj):
        """Display shortened Stripe customer ID"""
        if obj.stripe_customer_id:
            return f"{obj.stripe_customer_id[:20]}..."
        return "Not Set"
    stripe_customer_id_short.short_description = "Stripe Customer"


# ============================================================================
# SUBSCRIPTION ADMIN
# ============================================================================
class SubscriptionAdmin(admin.ModelAdmin):
    """Admin interface for Subscription management"""
    list_display = (
        'get_user', 'plan', 'status', 'current_period_start', 'current_period_end',
        'cancel_at_period_end', 'stripe_subscription_id_short'
    )
    list_filter = ('plan', 'status', 'cancel_at_period_end', 'created_at')
    search_fields = (
        'user__username', 'user__email',
        'stripe_subscription_id'
    )
    readonly_fields = (
        'user', 'created_at', 'updated_at',
        'stripe_subscription_id', 'stripe_customer_id'
    )
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Plan Details', {
            'fields': ('plan', 'status', 'current_period_start', 'current_period_end')
        }),
        ('Renewal Settings', {
            'fields': ('cancel_at_period_end', 'canceled_at')
        }),
        ('Stripe Integration', {
            'fields': ('stripe_subscription_id', 'stripe_customer_id'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    
    def get_user(self, obj):
        """Display username linked to subscription"""
        return obj.user.username
    get_user.short_description = "User"
    get_user.admin_order_field = 'user__username'
    
    def stripe_subscription_id_short(self, obj):
        """Display shortened Stripe subscription ID"""
        if obj.stripe_subscription_id:
            return f"{obj.stripe_subscription_id[:25]}..."
        return "Not Set"
    stripe_subscription_id_short.short_description = "Stripe ID"


# ============================================================================
# PAYMENT ADMIN
# ============================================================================
class PaymentAdmin(admin.ModelAdmin):
    """Admin interface for Payment tracking"""
    list_display = (
        'get_user', 'amount_display', 'plan', 'status',
        'created_at', 'stripe_payment_id_short'
    )
    list_filter = ('status', 'plan', 'currency', 'created_at')
    search_fields = (
        'user__username',
        'user__email',
        'stripe_payment_id', 'stripe_invoice_id'
    )
    readonly_fields = (
        'user', 'stripe_payment_id', 'stripe_invoice_id',
        'created_at', 'amount_display'
    )
    fieldsets = (
        ('Payment Information', {
            'fields': ('user', 'amount_display', 'currency')
        }),
        ('Plan & Status', {
            'fields': ('plan', 'status', 'paid_at')
        }),
        ('Stripe Integration', {
            'fields': ('stripe_payment_id', 'stripe_invoice_id'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    
    def get_user(self, obj):
        """Display username linked to payment"""
        return obj.user.username
    get_user.short_description = "User"
    get_user.admin_order_field = 'user__username'
    
    def amount_display(self, obj):
        """Display formatted amount with currency"""
        return f"${obj.amount} {obj.currency.upper()}"
    amount_display.short_description = "Amount"
    
    def stripe_payment_id_short(self, obj):
        """Display shortened Stripe payment ID"""
        if obj.stripe_payment_id:
            return f"{obj.stripe_payment_id[:20]}..."
        return "Not Set"
    stripe_payment_id_short.short_description = "Payment ID"


# ============================================================================
# REGISTER ALL MODELS
# ============================================================================
# Unregister the default User admin and register our enhanced version
admin.site.unregister(User)
admin.site.register(User, EnhancedUserAdmin)

# Register all models
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(Payment, PaymentAdmin)

# Customize admin site
admin.site.site_header = "Nurva.AI Admin Control Panel"
admin.site.site_title = "Nurva.AI Admin"
admin.site.index_title = "Welcome to Nurva.AI Administration"
