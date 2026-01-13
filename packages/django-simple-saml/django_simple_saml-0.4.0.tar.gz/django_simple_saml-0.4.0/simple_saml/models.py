from __future__ import annotations

from typing import Any

from django.db import models
from django.utils.translation import gettext_lazy as _lazy


class IdentityProviderManager(models.Manager):
    """Custom manager for the IdentityProvider model."""

    def active(self) -> models.QuerySet[IdentityProvider]:
        """Return only the active IdentityProviders."""
        return self.get_queryset().filter(is_enabled=True)


class IdentityProvider(models.Model):
    """Class to store the Identity Provider metadata."""

    label = models.CharField(
        max_length=255,
        unique=True,
        help_text=_lazy(
            "A unique label / key used to identify the IdP to use. "
            "(Recommended value is the name or URL of the IdP.)"
        ),
    )
    provider = models.CharField(
        max_length=255,
        help_text=_lazy("The name of the provider (e.g. Google Workspace, Okta)."),
        blank=True,
    )
    entity_id = models.CharField(
        max_length=255,
        help_text=_lazy("The entity ID provided by the IdP."),
        verbose_name="Entity ID",
    )
    sso_url = models.CharField(
        max_length=255,
        help_text=_lazy("The SSO URL provided by the IdP."),
        verbose_name="SSO URL",
    )
    x509_cert = models.TextField(
        help_text=_lazy("The X.509 certificate provided by the IdP."),
        verbose_name="X509 Certificate",
    )
    # these user attributes are used to map user details required to
    # complete account creation, the model values determine the
    # attribute names used to map the user details.
    user_permanent_id_attr = models.CharField(
        max_length=255,
        help_text=_lazy(
            "The attribute provided by the IdP for the user's unique "
            "ID property (required)."
        ),
    )
    first_name_attr = models.CharField(
        blank=True,
        max_length=255,
        help_text=_lazy(
            "The name of the attribute provided by the IdP for the "
            "'user.first_name' property."
        ),
    )
    last_name_attr = models.CharField(
        blank=True,
        max_length=255,
        help_text=_lazy(
            "The name of the attribute provided by the IdP for "
            "'user.last_name' property"
        ),
    )
    email_attr = models.CharField(
        blank=True,
        max_length=255,
        help_text=_lazy(
            "The name of the attribute provided by the IdP for the "
            "'user.email' property."
        ),
    )
    username_attr = models.CharField(
        blank=True,
        max_length=255,
        help_text=_lazy(
            "The username attribute provided by the IdP for the "
            "'user.username' property."
        ),
    )
    is_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = IdentityProviderManager()

    def __str__(self) -> str:
        if self.provider:
            return f"{self.label} ({self.provider})"
        return self.label

    def save(self, *args: Any, **kwargs: Any) -> IdentityProvider:
        if "update_fields" in kwargs:
            kwargs["update_fields"] += ["updated_at"]
        return super().save(*args, **kwargs)

    @property
    def user_attribute_map(self) -> dict[str, str]:
        # only return non-empty values, as social_auth does not handle
        # empty values well.
        if not self.user_permanent_id_attr:
            raise ValueError("IdentityProvider.user_permanent_id_attr is required")
        return {
            k: v
            for k, v in {
                "attr_user_permanent_id": self.user_permanent_id_attr,
                "attr_first_name": self.first_name_attr,
                "attr_last_name": self.last_name_attr,
                "attr_username": self.username_attr,
                "attr_email": self.email_attr,
            }.items()
            if v
        }

    @property
    def config(self) -> dict[str, str]:
        # returns the config for the get_idp method
        return {
            "entity_id": self.entity_id,
            "url": self.sso_url,
            "x509cert": self.x509_cert,
        } | self.user_attribute_map

    def x509_cert_short(self) -> str:
        """Return truncated version of X.509 certificate."""
        if not self.x509_cert:
            return ""
        return self.x509_cert[:20] + "..." + self.x509_cert[-20:]
