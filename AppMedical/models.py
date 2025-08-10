from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# Create your models here.


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('patient', 'Patient'),
        ('medecin', 'Médecin'),
        ('admin', 'Admin Hôpital'),
    ]
    GENRE_CHOICES = [
        ('H', 'Homme'),
        ('F', 'Femme'),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    genre = models.CharField(max_length=1, choices=GENRE_CHOICES, null=True, blank=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    adresse = models.TextField(blank=True, null=True)
    date_naissance = models.DateField(blank=True, null=True)
    photo = models.ImageField(upload_to='profils/', blank=True, null=True)

class Hopital(models.Model):
    nom = models.CharField(max_length=100)
    adresse = models.TextField()
    admin = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'admin'})

    def __str__(self):
        return self.nom


class DemandeInscription(models.Model):
    CHOIX_GROUPES_SANGUINS = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]

    patient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'patient'})
    hopital = models.ForeignKey(Hopital, on_delete=models.CASCADE)
    date_demande = models.DateTimeField(auto_now_add=True)
    approuvee = models.BooleanField(null=True)  # True, False, None
    groupe_sanguin = models.CharField(max_length=3, choices=CHOIX_GROUPES_SANGUINS, null=True, blank=True)
    antecedents = models.TextField(blank=True)
    allergies = models.TextField(blank=True)
    informations_complementaires = models.TextField(blank=True)
    


    def __str__(self):
        return f"{self.patient.username} -> {self.hopital.nom} ({'✔️' if self.approuvee else '❌' if self.approuvee is False else '🕒'})"
    
class PersonneAPrevenir(models.Model):
    patient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='personnes_a_prevenir')
    nom = models.CharField(max_length=100)
    relation = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return f"{self.nom} ({self.relation})"
    
class Medecin(models.Model):
    photo = models.ImageField(upload_to='photos/', null=True, blank=True)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    specialite = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20)
    hopital = models.ForeignKey("Hopital", on_delete=models.CASCADE)
    mot_de_passe_temporaire = models.CharField(max_length=100, blank=True)
    patients = models.ManyToManyField(CustomUser, related_name='medecins_assignés', limit_choices_to={'role': 'patient'}, blank=True)


    def __str__(self):
        return f"{self.user.get_full_name()} - {self.specialite}"
    


class RendezVous(models.Model):
    patient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'patient'})
    medecin = models.ForeignKey(Medecin, on_delete=models.CASCADE, null=True, blank=True)
    hopital = models.ForeignKey(Hopital, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField()
    heure = models.TimeField()
    motif = models.TextField(blank=True)
    statut = models.CharField(max_length=20, choices=[
        ('en_attente', 'En attente'),
        ('approuvé', 'Approuvé'),
        ('refusé', 'Refusé')
    ], default='en_attente')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rendez-vous {self.patient} avec {self.medecin} le {self.date} à {self.heure}"
    

class DossierMedical(models.Model):
    patient = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="dossier")
    groupe_sanguin = models.CharField(max_length=3, default="Inconnu")
    antecedents = models.TextField(blank=True, null=True)
    allergies = models.TextField(blank=True, null=True)
    infos_complementaires = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Dossier médical de {self.patient.get_full_name()}"

class SuiviMedical(models.Model):
    dossier = models.ForeignKey(DossierMedical, on_delete=models.CASCADE, related_name="suivis")
    date_consultation = models.DateTimeField(auto_now_add=True)
    poids = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    taille = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    tension_arterielle = models.CharField(max_length=20, blank=True, null=True)
    temperature = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    observations = models.TextField(blank=True, null=True)
    examens = models.TextField(blank=True, null=True)
    traitements = models.TextField(blank=True, null=True)
    prescriptions = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Suivi du {self.date_consultation.strftime('%d/%m/%Y')} - {self.dossier.patient.username}"
    

class FichierSuivi(models.Model):
    suivi = models.ForeignKey(SuiviMedical, on_delete=models.CASCADE, related_name="fichiers")
    fichiers = models.FileField(upload_to='suivis/')
    description = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Fichier pour {self.suivi} - {self.fichier.name}"
