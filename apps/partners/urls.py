from apps.partners.views import (
    PartnerList,
    SendPartnerRequest,
    AcceptPartnerRequest,
    RejectPartnerRequest,
    PartnerDetail,

)
from django.urls import path


urlpatterns = [
    path("partners/", PartnerList.as_view()),
    path("partners/partner-requests/send/", SendPartnerRequest.as_view()),
    path("partners/partner-requests/accept/", AcceptPartnerRequest.as_view()),
    path("partners/partner-requests/reject/", RejectPartnerRequest.as_view()),
    path('partners/partner-requests/<uuid:uuid>/', PartnerDetail.as_view()),
]