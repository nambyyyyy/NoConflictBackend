from django.urls import re_path
from presentation.ws.consumers import ConflictConsumer

websocket_urlpatterns = [
    re_path(r"ws/conflicts/(?P<slug>[\w-]+)/$", ConflictConsumer.as_asgi()), # type: ignore
]