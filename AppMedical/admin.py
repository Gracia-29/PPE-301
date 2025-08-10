from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Hopital)
admin.site.register(DemandeInscription)
admin.site.register(PersonneAPrevenir)
admin.site.register(Medecin)
admin.site.register(RendezVous)
