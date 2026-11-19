from django.contrib.auth.base_user import BaseUserManager

class UserManager(BaseUserManager):

    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("User must have an email")

        """
        if "company" not in extra_fields:
            raise ValueError("User must have a company")
        """
        email = self.normalize_email(email)

        user = self.model(
            email=email,
            **extra_fields   # ✅ no username override
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        """
        if extra_fields.get("company") is None:
            raise ValueError("Superuser must have a company")
        """

        return self.create_user(email, password, **extra_fields)
    