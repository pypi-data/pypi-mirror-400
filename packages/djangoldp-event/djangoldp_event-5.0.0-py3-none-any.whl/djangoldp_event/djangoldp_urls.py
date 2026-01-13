from django.urls import path
from .views import FutureEventsViewset, PastEventsViewset

urlpatterns = [
    path('events/future/', FutureEventsViewset.urls(model_prefix="event-future")),
    path('events/past/', PastEventsViewset.urls(model_prefix="event-past"))
]