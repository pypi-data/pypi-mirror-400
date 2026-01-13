from django.conf import settings
from django.db import models
from djangoldp.models import Model
from djangoldp_circle.models import Circle
from djangoldp.permissions import AuthenticatedOnly, AnonymousReadOnly, ReadAndCreate, ACLPermissions, InheritPermissions


class Typeevent (Model):
    name = models.CharField(max_length=50, blank=True, null=True, verbose_name="Type d'évènement")

    class Meta(Model.Meta):
        permission_classes = [AuthenticatedOnly]
        rdf_type = 'sib:tag'

    def __str__(self):
        return self.name


class Locationevent (Model):
    name = models.CharField(max_length=50, blank=True, null=True, verbose_name="Lieu, établissement")
    address = models.TextField(max_length=225, blank=True, null=True, verbose_name="Adresse")

    class Meta(Model.Meta):
        permission_classes = [AuthenticatedOnly]
        rdf_type = 'sib:location'

    def __str__(self):
        return self.name

class Regionevent (Model):
    name = models.CharField(max_length=50, blank=True, null=True, verbose_name="Région")

    class Meta(Model.Meta):
        permission_classes = [AuthenticatedOnly]
        rdf_type = 'sib:tag'
    
    def __str__(self):
        return self.name

class Event (Model):
    name = models.CharField(max_length=50, blank=True, null=True, verbose_name="Nom de l'évènement")
    region = models.ForeignKey(Regionevent, blank=True, null=True, verbose_name="Région", on_delete=models.CASCADE)
    type = models.ForeignKey(Typeevent, blank=True, null=True, verbose_name="Type d'évènement", on_delete=models.CASCADE)
    startDate =  models.DateField(blank=True, null=True, verbose_name="Date de début")
    startTime = models.TimeField(blank=True, null=True, verbose_name="Heure de début")
    endDate =  models.DateField(verbose_name="Date de fin", blank=True, null=True )
    endTime =  models.TimeField(verbose_name="Heure de fin", blank=True, null=True )
    img = models.URLField(blank=True, null=True, default=settings.BASE_URL + "/media/defaultevent.png", verbose_name="Illustration de l'évènement")
    location = models.ForeignKey(Locationevent, blank=True, null=True, verbose_name="Lieu de l'évènement", on_delete=models.SET_NULL)
    shortDescription = models.CharField(blank=True, null=True, max_length=250,verbose_name="Short description")
    longDescription = models.TextField(blank=True, null=True, verbose_name="Long description")
    link = models.CharField(max_length=2048, blank=True, null=True, verbose_name="Lien internet")
    facebook = models.CharField(max_length=150, blank=True, null=True, verbose_name="Lien Facebook")
    circle = models.ForeignKey(Circle, null=True, blank=True, related_name="events", on_delete=models.SET_NULL)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='createdEvents', null=True, blank=True, on_delete=models.SET_NULL)
    creationDate = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    visible = models.BooleanField(verbose_name="Visible sur le site", blank=True, null=True,  default=True)

    class Meta(Model.Meta):
        nested_fields = ['type', 'circle', 'author', 'location']
        ordering = ['startDate']
        auto_author = 'author'
        owner_field = 'author'
        permission_classes = [AuthenticatedOnly, ReadAndCreate|ACLPermissions, InheritPermissions]
        inherit_permissions = ['circle']
        rdf_type = 'sib:event'

    def __str__(self):
        return self.name
