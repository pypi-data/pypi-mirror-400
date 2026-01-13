import factory
import hashlib
from .models import Resource
from django.db.models.signals import post_save

@factory.django.mute_signals(post_save)
class ResourceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Resource

    # Please refer to Factory boy documentation
    # https://factoryboy.readthedocs.io
