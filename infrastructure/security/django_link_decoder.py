from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from core.interfaces.link_interface import LinkDecoder


class DjangoLinkDecoder(LinkDecoder):
    def decode(self, encoded: str) -> str:
        try:
            return force_str(urlsafe_base64_decode(encoded))
        except (TypeError, ValueError, OverflowError, UnicodeDecodeError):
            raise ValueError("Invalid link format")