from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

GUEST_EMAIL = "guest@user.com"
GUEST_PASSWORD = "guest1234"
GUEST_FULLNAME = "Guest User"


class Command(BaseCommand):
    help = "Create or update the Guest user (idempotent)."

    def handle(self, *args, **options):
        User = get_user_model()

        user, created = User.objects.get_or_create(
            email=GUEST_EMAIL,
            defaults={"fullname": GUEST_FULLNAME},
        )

        changed = False
        
        if getattr(user, "fullname", "") != GUEST_FULLNAME:
            user.fullname = GUEST_FULLNAME
            changed = True

        if created or not user.check_password(GUEST_PASSWORD):
            user.set_password(GUEST_PASSWORD)
            changed = True

        if changed:
            user.save()

        self.stdout.write(
            self.style.SUCCESS(
                f"Guest user ready: created={created}, updated={changed}, id={user.id}, email={user.email}"
            )
        )
