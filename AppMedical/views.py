from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import user_passes_test, login_required   
from django.contrib.auth.decorators import login_required
from .forms import *
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.core.mail import send_mail
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import PasswordChangeForm
from .models import *

def dashboard_patient(request):
    return render(request, 'dashboard/patient.html')        

def dashboard_medecin(request):
    return render(request, 'dashboard/medecin.html')

def dashboard_admin(request):
    return render(request, 'dashboard/admin.html')

def index(request): 
    return render(request, 'dashboard/index.html')  

def inscription_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Inscription réussie ! Connectez-vous maintenant.")
            return redirect('connexion') 
        else:
            messages.error(request, "Erreur dans le formulaire.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/inscription.html', {'form': form})



def connexion_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            role = user.role
            if role == 'patient':
                return redirect('dashboard_patient')
            elif role == 'medecin':
                return redirect('dashboard_medecin')
            else:
                return redirect('dashboard_admin')
        else:
            messages.error(request, "Identifiants invalides.")
    else:
        form = AuthenticationForm()
    return render(request, 'registration/connexion.html', {'form': form})


def deconnexion_view(request):
    logout(request)
    return redirect('index')

def is_admin(user):
    return user.is_superuser or user.role == 'admin'

@login_required
@user_passes_test(is_admin)
def ajouter_hopital(request):
    if request.method == 'POST':
        form = HopitalForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('liste_hopitaux')
    else:
        form = HopitalForm()
    return render(request, 'liste/ajout_hopitaux.html', {'form': form},)

@login_required
def liste_hopitaux(request):
    hopitaux = Hopital.objects.all()
    return render(request, 'liste/hopitaux.html', {'hopitaux': hopitaux})

@login_required
def liste_hopitaux_admin(request):
    hopitaux = Hopital.objects.all()
    return render(request, 'liste/hopitaux_admin.html', {'hopitaux': hopitaux})

@login_required
def demander_inscription(request, hopital_id):
    hopital = get_object_or_404(Hopital, id=hopital_id)

    if request.method == 'POST':
        form = DemandeInscriptionForm(request.POST)
        if form.is_valid():
            demande = form.save(commit=False)
            demande.patient = request.user  
            demande.hopital = hopital 
            demande.save()
            return redirect('index')
    else:
        form = DemandeInscriptionForm(initial={'hopital': hopital})

    return render(request, 'registration/demande_inscription.html', {'form': form})


@login_required
@user_passes_test(lambda u: u.is_superuser or u.role == 'admin') 
def liste_demandes_en_attente(request):
    demandes = DemandeInscription.objects.filter(approuvee__isnull=True)
    return render(request, 'liste/attente.html', {'demandes': demandes})

@login_required
@user_passes_test(lambda u: u.is_superuser or u.role == 'admin')
def approuver_demande(request, demande_id):
    demande = get_object_or_404(DemandeInscription, id=demande_id)
    demande.approuvee = True
    demande.save()

    # Création automatique du dossier médical si pas déjà existant
    DossierMedical.objects.get_or_create(
        patient=demande.patient,
        defaults={
            'groupe_sanguin': demande.groupe_sanguin,
            'antecedents': demande.antecedents,
            'allergies': demande.allergies,
            'infos_complementaires': demande.informations_complementaires
        }
    )

    messages.success(request, "Demande approuvée avec succès et dossier médical créé.")
    return redirect('liste_demandes_en_attente')


@login_required
@user_passes_test(lambda u: u.is_superuser or u.role == 'admin')
def refuser_demande(request, demande_id):
    demande = get_object_or_404(DemandeInscription, id=demande_id)
    demande.approuvee = False
    demande.save()
    messages.warning(request, "Demande refusée.")
    return redirect('liste_demandes_en_attente')

@login_required
def demandes_validees(request):
    user = request.user

    if user.is_superuser:
        # Le superuser voit toutes les demandes validées
        demandes = DemandeInscription.objects.filter(approuvee=True)
    elif user.role == 'admin':
        try:
            # Récupère l'hôpital de l'admin connecté
            hopital_admin = Hopital.objects.get(admin=user)
            demandes = DemandeInscription.objects.filter(approuvee=True, hopital=hopital_admin)
        except Hopital.DoesNotExist:
            # L'admin n'a pas encore d'hôpital lié
            demandes = []
    else:
        # Patients ou autres rôles ne voient rien ici
        demandes = []

    return render(request, 'liste/demande_valide.html', {'demandes': demandes})


@login_required
def ajouter_personne_a_prevenir(request):
    if request.method == 'POST':
        form = PersonneAPrevenirForm(request.POST)
        if form.is_valid():
            personne = form.save(commit=False)
            personne.patient = request.user
            personne.save()
            return redirect('personnes_a_prevenir')
    else:
        form = PersonneAPrevenirForm()
    return render(request, 'liste/ajouter_personne.html', {'form': form})

@login_required 
def personnes_a_prevenir(request):
    personnes = request.user.personnes_a_prevenir.all()
    return render(request, 'liste/personne_prevenir.html', {'personnes': personnes}) 

def supprimer_personne(request, personne_id):
    personne = get_object_or_404(PersonneAPrevenir, id=personne_id, patient=request.user)
    personne.delete()
    return redirect('personnes_a_prevenir')

def modifier_personne(request, personne_id):
    personne = get_object_or_404(PersonneAPrevenir, id=personne_id, patient=request.user)
    if request.method == 'POST':
        form = PersonneAPrevenirForm(request.POST, instance=personne)
        if form.is_valid():
            form.save()
            return redirect('personnes_a_prevenir')
    else:
        form = PersonneAPrevenirForm(instance=personne)
    return render(request, 'liste/modifier_personne.html', {'form': form})



@login_required 
def ajouter_medecin(request):
    if not request.user.is_authenticated or request.user.role != 'admin':
        return redirect('connexion')

    hopital_admin = Hopital.objects.get(admin=request.user)

    if request.method == 'POST':
        form = MedecinCreationForm(request.POST)
        if form.is_valid():
            user, password = form.save(hopital=hopital_admin)   
            messages.success(request, "Médecin enregistré avec succès.")
            return redirect('liste_medecins')
    else:
        form = MedecinCreationForm()

    return render(request, 'liste/ajouter_medecin.html', {'form': form})

def envoyer_identifiants(request, medecin_id):
    if not request.user.is_authenticated or request.user.role != 'admin':
        return redirect('connexion')

    medecin = get_object_or_404(Medecin, id=medecin_id)
    user = medecin.user
    password = medecin.mot_de_passe_temporaire

    if not password:
        messages.error(request, "Aucun mot de passe disponible pour ce médecin.")
        return redirect('liste_medecins')

    subject = "Vos identifiants de connexion - Médecin"
    message = f"""Bonjour {user.first_name},

            Votre compte médecin a été créé.

            Voici vos identifiants :

            Email : {user.email}
            Mot de passe : {password}

            Merci de vous connecter et de changer votre mot de passe dès la première connexion.
            """

    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
    messages.success(request, f"Identifiants envoyés à {user.email}.")
    return redirect('liste_medecins')




@login_required     
def liste_medecins(request):
    try:
        hopital_admin = Hopital.objects.get(admin=request.user)
    except Hopital.DoesNotExist:
        messages.error(request, "Aucun médecin associé à cet hopital.")
        return redirect('liste_medecins')
    
    medecins = Medecin.objects.filter(hopital=hopital_admin)
    return render(request, 'liste/liste_medecins.html', {'medecins': medecins})

@login_required
def liste_rendezvous_hopital(request):
    try:
        hopital_admin = Hopital.objects.get(admin=request.user)
    except Hopital.DoesNotExist:
        messages.error(request, "Aucun hôpital associé à cet administrateur.")
        return redirect('dashboard_admin')

    rendez_vous = RendezVous.objects.filter(hopital=hopital_admin, statut='en_attente')
    return render(request, 'liste/liste_rendezvous.html', {'rendez_vous': rendez_vous})


@login_required
def modifier_profil_medecin(request):
    user = request.user
    try:
        medecin = user.medecin
    except:
        messages.error(request, "Ce compte n'est pas lié à un médecin.")
        return redirect('dashboard_medecin')

    if request.method == 'POST':
        form_user = MedecinProfilForm(request.POST, request.FILES, instance=user)
        form_medecin = MedecinInfosProForm(request.POST, instance=medecin)
        form_password = PasswordChangeForm(user, request.POST)

        if form_user.is_valid() and form_medecin.is_valid():
            form_user.save()
            form_medecin.save()
            if form_password.is_valid():
                user = form_password.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Mot de passe modifié avec succès.")
            messages.success(request, "Profil mis à jour avec succès.")
            return redirect('dashboard_medecin')
        else:
            messages.error(request, "Veuillez corriger les erreurs.")
    else:
        form_user = MedecinProfilForm(instance=user)
        form_medecin = MedecinInfosProForm(instance=user.medecin)
        form_password = PasswordChangeForm(user)

    return render(request, 'dashboard/modifier-profil.html', {
        'form_user': form_user,
        'form_medecin': form_medecin,
        'form_password': form_password,
    })


def profil_medecin(request):
    medecin = Medecin.objects.get(user=request.user)
    return render(request, 'dashboard/profil_medecin.html', {'medecin': medecin})

@login_required
def profil_patient(request):
    return render(request, 'dashboard/profil_patient.html', {'patient': request.user})

@login_required
def modifier_profil_patient(request):
    patient = request.user
    if request.method == 'POST':
        form = PatientUpdateForm(request.POST, request.FILES, instance=patient)
        if form.is_valid():
            form.save()
            return redirect('profil_patient')
    else:
        form = PatientUpdateForm(instance=patient)

    return render(request, 'dashboard/modifier_profil_patient.html', {'form': form})



@login_required
def prendre_rendez_vous(request):
    if request.method == 'POST':
        form = RendezVousForm(request.POST, user=request.user)
        if form.is_valid():
            rdv = form.save(commit=False)
            rdv.patient = request.user
            rdv.medecin = None  # médecin attribué plus tard par l’hôpital
            rdv.save()
            return redirect('liste_rendez_vous')
    else:
        form = RendezVousForm(user=request.user)
    return render(request, 'liste/prendre_rendez_vous.html', {'form': form})



@login_required
def mes_rendezvous(request):
    rdvs = RendezVous.objects.filter(patient=request.user)
    return render(request, 'liste/mes_rendez_vous.html', {'rdvs': rdvs})

@login_required
def liste_rendezvous_hopital(request):
    try:
        hopital_admin = Hopital.objects.get(admin=request.user)
    except Hopital.DoesNotExist:
        messages.error(request, "Aucun hôpital associé à cet administrateur.")
        return redirect('dashboard_admin')

    rendez_vous = RendezVous.objects.filter(hopital=hopital_admin, statut='en_attente')
    return render(request, 'liste/liste_rendezvous.html', {'rendez_vous': rendez_vous})


@login_required
def valider_rdv(request, rdv_id):
    rdv = get_object_or_404(RendezVous, id=rdv_id)
    rdv.statut = 'valide'
    rdv.save()
    return redirect('liste_rendezvous_hopital')

@login_required
def refuser_rdv(request, rdv_id):
    rdv = get_object_or_404(RendezVous, id=rdv_id)
    rdv.statut = 'refuse'
    rdv.save()
    return redirect('liste_rendezvous_hopital')


def is_admin(user):
    return user.is_authenticated and user.role == 'admin'

@login_required
@user_passes_test(is_admin)
def assign_patients_to_medecin(request, medecin_id):
    medecin = get_object_or_404(Medecin, id=medecin_id)

    # Vérification que l'admin est bien celui de l'hôpital du médecin
    if request.user != medecin.hopital.admin:
        return redirect('index')

    # On récupère tous les patients approuvés pour l'hôpital de l'admin
    patients_du_meme_hopital = CustomUser.objects.filter(
        role='patient',
        id__in=DemandeInscription.objects.filter(
            hopital=medecin.hopital,
            approuvee=True
        ).values_list('patient_id', flat=True)
    )

    if request.method == 'POST':
        form = AssignPatientsForm(request.POST, instance=medecin)
        form.fields['patients'].queryset = patients_du_meme_hopital
        if form.is_valid():
            form.save()
            return redirect('liste_medecins')
    else:
        form = AssignPatientsForm(instance=medecin)
        form.fields['patients'].queryset = patients_du_meme_hopital

    return render(request, 'liste/assign_patients.html', {
        'form': form,
        'medecin': medecin
    })

@login_required
def mes_patients(request):
    if not hasattr(request.user, 'medecin'):
        return redirect('index') 

    medecin = request.user.medecin
    patients = medecin.patients.all() 

    return render(request, 'liste/patient_medecin.html', {
        'patients': patients
    })


@login_required
def voir_dossier_medical(request, patient_id):
    dossier = get_object_or_404(DossierMedical, patient_id=patient_id)
    suivis = dossier.suivis.all().order_by('-date_consultation')  # historique

    base_template = "dashboard/base_patient.html"
    peut_modifier = False

    if request.user.role == 'medecin':
        base_template = "dashboard/base_medecin.html"
        # Exemple : autoriser le médecin s'il est dans une relation à implémenter
        # Ici on ne permet pas la modif par défaut
        peut_modifier = False

    elif request.user.role == 'admin':
        base_template = "dashboard/base_admin.html"
        peut_modifier = True

    return render(request, 'liste/voir_dossier.html', {
        'dossier': dossier,
        'suivis': suivis,
        'base_template': base_template,
        'peut_modifier': peut_modifier
    })


@login_required
def ajouter_suivi_medical(request, patient_id):
    dossier = get_object_or_404(DossierMedical, patient_id=patient_id)
    
    if request.method == "POST":
        form = SuiviMedicalForm(request.POST, request.FILES)
        if form.is_valid():
            suivi = form.save(commit=False)
            suivi.dossier = dossier
            suivi.save()

            # Sauvegarde des fichiers
            for fichier in request.FILES.getlist('fichiers'):
                FichierSuivi.objects.create(suivi=suivi, fichiers=fichier)

            messages.success(request, "Suivi médical ajouté avec succès.")
            return redirect("voir_dossier_medical", patient_id=patient_id)
    else:
        form = SuiviMedicalForm()

    return render(request, "liste/ajouter_suivi_medical.html", {"form": form, "dossier": dossier})



@login_required
def modifier_dossier_medical(request, patient_id):
    dossier = get_object_or_404(DossierMedical, patient_id=patient_id)

    # Vérification des droits
    if request.user.role == "medecin":
        if hasattr(dossier, "medecin") and dossier.medecin != request.user:
            messages.error(request, "Vous n'êtes pas autorisé à modifier ce dossier.")
            return redirect("voir_dossier_medical", patient_id=patient_id)
    elif request.user.role != "admin":
        messages.error(request, "Vous n'êtes pas autorisé à modifier ce dossier.")
        return redirect("voir_dossier_medical", patient_id=patient_id)

    if request.method == "POST":
        form = DossierMedicalForm(request.POST, request.FILES, instance=dossier)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Dossier médical mis à jour avec succès.")
            return redirect("voir_dossier_medical", patient_id=patient_id)
        else:
            messages.error(request, "❌ Erreur dans le formulaire.")
    else:
        form = DossierMedicalForm(instance=dossier)

    return render(request, "liste/modifier_dossier_medical.html", {
        "form": form,
        "dossier": dossier
    })
