from django.contrib.auth.decorators import user_passes_test
from django.http import HttpRequest, HttpResponse

from .metadata import MetadataException, get_saml_metadata


@user_passes_test(lambda u: u.is_superuser)
def saml_metadata_view(request: HttpRequest) -> HttpResponse:
    """View to generate the SAML metadata XML (superuser only)."""
    try:
        metadata = get_saml_metadata(request)
        return HttpResponse(content=metadata, content_type="text/xml")
    except MetadataException as ex:
        raise Exception("Error generating metadata XML.") from ex
