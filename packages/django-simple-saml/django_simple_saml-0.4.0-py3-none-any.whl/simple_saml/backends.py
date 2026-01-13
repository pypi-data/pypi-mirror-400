import logging

from social_core.backends.saml import SAMLAuth as BaseSAMLAuth, SAMLIdentityProvider

from .models import IdentityProvider

logger = logging.getLogger(__name__)


class SimpleSAMLAuth(BaseSAMLAuth):
    """Subclass of SAMLAuth that stores the IdP info in a model."""

    def get_idp(self, idp_name: str | None) -> SAMLIdentityProvider:
        if idp_name is None:
            raise ValueError("Identity provider name cannot be None.")
        try:
            idp = IdentityProvider.objects.get(label=idp_name)
        except IdentityProvider.DoesNotExist:
            raise ValueError(f"Identity provider {idp_name} does not exist.")
        if not idp.is_enabled:
            # TODO: is this a security issue? Should we return a 404 instead?
            raise ValueError(f"Identity provider {idp_name} is not enabled.")
        return SAMLIdentityProvider(backend=self, name=idp_name, **idp.config)

    def get_user_id(self, details: dict, response: dict) -> str:
        """Return the permanent user id from the response."""
        try:
            return super().get_user_id(details, response)
        except KeyError:
            logger.exception(
                "Error getting user_permanent_id from response. "
                "Check response for more details: %s",
                response,
            )
            raise
