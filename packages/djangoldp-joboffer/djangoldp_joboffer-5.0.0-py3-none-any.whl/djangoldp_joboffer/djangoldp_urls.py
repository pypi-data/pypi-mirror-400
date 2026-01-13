from django.urls import path
from .views import JobOffersCurrentViewset, \
                   JobOffersExpiredViewset, JobOfferServerNotificationView
from .models import JobOffer

urlpatterns = [
    path('job-offers/current/', JobOffersCurrentViewset.urls(model_prefix="joboffer-current", model=JobOffer)),
    path('job-offers/expired/', JobOffersExpiredViewset.urls(model_prefix="joboffer-expired", model=JobOffer)),
    path('job-offers/inbox/', JobOfferServerNotificationView.as_view(), name="joboffer-notify-all"),
]
