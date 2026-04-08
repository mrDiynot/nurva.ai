from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils.timezone import now
from datetime import timedelta
from chat.models import UserProfile, Subscription


class Command(BaseCommand):
    help = 'Manually activate a paid subscription for a user (for testing webhooks)'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username to activate payment for')
        parser.add_argument(
            '--plan',
            type=str,
            default='monthly',
            choices=['monthly', 'quarterly', 'yearly'],
            help='Subscription plan type'
        )

    def handle(self, *args, **options):
        username = options['username']
        plan = options['plan']

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User "{username}" not found'))
            return

        # Get or create profile
        profile, _ = UserProfile.objects.get_or_create(user=user)

        # Calculate period dates based on plan
        now_time = now()
        if plan == 'monthly':
            period_end = now_time + timedelta(days=30)
        elif plan == 'quarterly':
            period_end = now_time + timedelta(days=90)
        else:  # yearly
            period_end = now_time + timedelta(days=365)

        # Update profile to paid
        profile.is_paid = True
        profile.subscription_status = 'active'
        profile.current_period_start = now_time
        profile.current_period_end = period_end
        profile.free_messages_used = 0  # Reset message count
        profile.save()

        # Create or update subscription
        subscription, created = Subscription.objects.get_or_create(
            user=user,
            defaults={
                'stripe_subscription_id': f'sub_test_{user.id}_{plan}',
                'stripe_customer_id': f'cus_test_{user.id}',
                'plan': plan,
                'status': 'active',
                'current_period_start': now_time,
                'current_period_end': period_end,
                'cancel_at_period_end': False,
            }
        )

        if not created:
            subscription.plan = plan
            subscription.status = 'active'
            subscription.current_period_start = now_time
            subscription.current_period_end = period_end
            subscription.save()

        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Successfully activated {plan} subscription for user "{username}"'
            )
        )
        self.stdout.write(f'   Status: ACTIVE')
        self.stdout.write(f'   Valid until: {period_end.strftime("%Y-%m-%d %H:%M:%S")}')
        self.stdout.write(f'   User can now send unlimited messages')
