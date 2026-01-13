import factory
import hashlib
from .models import Event
from django.db.models.signals import post_save

@factory.django.mute_signals(post_save)
class EventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Event

    # Please refer to Factory boy documentation
    # https://factoryboy.readthedocs.io
