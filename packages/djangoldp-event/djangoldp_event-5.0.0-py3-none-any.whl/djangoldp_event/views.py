from djangoldp.views.ldp_viewset import LDPViewSet
from datetime import datetime
from .models import Event

class FutureEventsViewset(LDPViewSet):
    model = Event
    def get_queryset(self):
        return super().get_queryset().filter(endDate__gte=datetime.now())

class PastEventsViewset(LDPViewSet):
    model = Event
    def get_queryset(self):
        return super().get_queryset().filter(endDate__lt=datetime.now())
