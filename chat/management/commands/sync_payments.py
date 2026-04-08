from django.core.management.base import BaseCommand
from chat.models import UserProfile, Subscription, Payment
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Sync Payment records from Subscription records'

    def handle(self, *args, **options):
        """Create Payment records for users with active Subscriptions but no Payment records"""
        
        updated = 0
        
        # Get all subscriptions
        subscriptions = Subscription.objects.filter(status='active')
        
        for sub in subscriptions:
            # Check if Payment record exists for this subscription
            payment_exists = Payment.objects.filter(
                stripe_payment_id=sub.stripe_subscription_id
            ).exists()
            
            if not payment_exists:
                # Create Payment record
                try:
                    payment = Payment.objects.create(
                        user=sub.user,
                        stripe_payment_id=sub.stripe_subscription_id,
                        stripe_invoice_id=None,  # Unknown for now
                        amount=39.00 if sub.plan == 'monthly' else 390.00,  # Assume standard pricing
                        currency='usd',
                        plan=sub.plan,
                        status='succeeded',
                        paid_at=sub.created_at if hasattr(sub, 'created_at') else None,
                    )
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✅ Created Payment record for {sub.user.username}: {sub.stripe_subscription_id}'
                        )
                    )
                    updated += 1
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'❌ Error creating Payment for {sub.user.username}: {str(e)}')
                    )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully synced {updated} Payment records')
        )
