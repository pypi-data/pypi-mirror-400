from django import forms
from django.conf import settings
from django.contrib import admin
from django.http import HttpRequest
from django.urls import reverse

from .models import IdentityProvider


class IdentityProviderForm(forms.ModelForm):
    class Meta:
        model = IdentityProvider
        fields = "__all__"
        widgets = {
            "metadata": forms.Textarea(attrs={"rows": 10, "cols": 100}),
            "x509_cert": forms.Textarea(attrs={"rows": 10, "cols": 100}),
        }


@admin.register(IdentityProvider)
class IdentityProviderAdmin(admin.ModelAdmin):
    form = IdentityProviderForm
    readonly_fields = (
        "created_at",
        "updated_at",
        "sp_entity_id",
        "sp_acs_url",
        "sp_relay_state",
    )
    list_display = ("label", "provider", "entity_id", "created_at", "is_enabled")
    fieldsets = (
        (None, {"fields": ("label", "provider", "is_enabled")}),
        (
            "Information provided to Identity Provider",
            {"fields": ("sp_entity_id", "sp_acs_url", "sp_relay_state")},
        ),
        (
            "Information provided by Identity Provider (required)",
            {
                "fields": (
                    "entity_id",
                    "sso_url",
                    "x509_cert",
                ),
            },
        ),
        (
            "Field mapping from IdP attributes to User Model",
            {
                "fields": (
                    "user_permanent_id_attr",
                    "first_name_attr",
                    "last_name_attr",
                    "email_attr",
                    "username_attr",
                ),
            },
        ),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    @admin.display(description="Entity ID")
    def sp_entity_id(self, _: IdentityProvider) -> str:
        return getattr(settings, "SOCIAL_AUTH_SAML_SP_ENTITY_ID", "missing")

    @admin.display(description="Assertion Consumer Service (ACS) URL")
    def sp_acs_url(self, _: IdentityProvider) -> str:
        url = reverse("social:complete", args=("saml",))
        return f"https://<insert-external-domain>{url}"

    @admin.display(description="Relay State")
    def sp_relay_state(self, obj: IdentityProvider) -> str:
        return obj.label

    def save_model(
        self,
        request: HttpRequest,
        obj: IdentityProvider,
        form: IdentityProviderForm,
        change: bool,
    ) -> None:
        """Validate that the metadata contains attr_user_permanent_id."""
        # if "attr_user_permanent_id" not in obj.metadata:
        #     raise forms.ValidationError("`attr_user_permanent_id` is a required key.")
        if ":" in obj.label:
            raise forms.ValidationError("`label` must not contain a colon.")
        if " " in obj.label:
            raise forms.ValidationError("`label` must not contain a space.")
        return super().save_model(request, obj, form, change)
