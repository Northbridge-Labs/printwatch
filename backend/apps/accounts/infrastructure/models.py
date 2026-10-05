"""Accounts ORM models: custom user, developer tokens."""
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """Manager using email as the unique identifier instead of username."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "admin")
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom user using email as the login identifier."""

    class Role(models.TextChoices):
        ADMIN = "admin", "Administrator"
        OPERATOR = "operator", "Operator"
        SERVICE = "service", "Service account"

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    # Inherited `username` is not used for login anymore — relax it so the
    # createsuperuser / management commands don't require a username.
    username = models.CharField(
        max_length=150, unique=False, null=True, blank=True,
        help_text="Optional display name; login is via email.",
    )
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=16, choices=Role.choices, default=Role.OPERATOR
    )
    phone = models.CharField(max_length=32, blank=True)
    department = models.ForeignKey(
        "printers.Department",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="members",
    )

    objects = UserManager()

    def __str__(self) -> str:
        return self.email


class DeveloperToken(models.Model):
    """Long-lived JWT issued to third-party printer app developers.

    Only the JTI is stored; the signed JWT is returned once at mint time.
    Revocation = set ``revoked_at``; the JWT backend checks JTI against DB
    (cached 60s in Valkey).
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="developer_tokens"
    )
    name = models.CharField(max_length=128, help_text="Identify the integration")
    jti = models.UUIDField(unique=True, editable=False)
    scopes = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=["jti"])]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.name} ({self.user.email})"