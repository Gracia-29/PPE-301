from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import user_passes_test, login_required   
from django.contrib.auth.decorators import login_required
from .forms import *
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.forms import PasswordChangeForm
from .models import *
from django.http import HttpResponseForbidden, HttpResponse
from django.template.loader import render_to_string
import io
import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from django.db.models import Q
from django.utils.crypto import get_random_string


@login_required
def dashboard_patient(request, patient_id):
    if request.user.role != 'patient':
        messages.error(request, "Accès interdit. Vous devez être un patient pour accéder à ce tableau de bord.")
        return redirect('index')
    patient = get_object_or_404(CustomUser, id=patient_id)
    
    # Récupère la demande d'inscription pour le patient (s'il y en a une)
    
    demande_inscription = DemandeInscription.objects.filter(patient__id=patient_id).first()

    # Si aucune demande, on laisse le patient accéder au dashboard et on affiche un message/CTA
    if not demande_inscription:
        dossier = DossierMedical.objects.filter(patient=patient).first()
        suivi = SuiviMedical.objects.filter(dossier=dossier).last() if dossier else None
        rdv = RendezVous.objects.filter(patient=patient).last() if patient else None
        needs_demande = True
        return render(request, 'patient/patient.html', {
            'patient': patient,
            'dossier': dossier,
            'suivi': suivi,
            'rdv': rdv,
            'demande_inscription': None,
            'needs_demande': needs_demande,
        })

    # Si la demande existe, afficher comme avant
    patient = demande_inscription.patient
    dossier = DossierMedical.objects.filter(patient=patient).first()
    suivi = SuiviMedical.objects.filter(dossier=dossier).last() if dossier else None
    rdv = RendezVous.objects.filter(patient=patient).last() if patient else None

    return render(request, 'patient/patient.html', {
        'patient': patient,
        'dossier': dossier,
        'suivi': suivi,
        'rdv': rdv,
        'demande_inscription': demande_inscription,
        'needs_demande': False,
    })

def dashboard_medecin(request):
    return render(request, 'medecin/medecin.html')

@login_required
@user_passes_test(lambda u: u.is_superuser or u.role == 'admin_system')
def dashboard_admin(request):
    hopitaux_total = Hopital.objects.count()
    validations_en_attente = Hopital.objects.filter(statut='en_attente').count()
    hopitaux_confirmes_total = Hopital.objects.filter(statut='confirme').count()
    patients_total = CustomUser.objects.filter(role='patient').count()
    livreurs_en_attente_total = Livreur.objects.filter(statut='en_attente').count()
    hopitaux_valides = Hopital.objects.filter(statut='confirme').order_by('-created_at')[:5]
    hopitaux_en_attente_liste = Hopital.objects.filter(statut='en_attente').order_by('-created_at')[:5]

    user_roles_labels = {
        'patient': 'Patient',
        'medecin': 'Medecin',
        'admin_hopital': 'Admin hopital',
        'admin_system': 'Administrateur',
        'livreur': 'Livreur',
    }

    recent_users = [
        {
            'type': 'utilisateur',
            'icon_letter': 'U',
            'icon_class': 'blue',
            'title': user.get_full_name() or user.email or user.username,
            'subtitle': user_roles_labels.get(user.role, 'Utilisateur'),
            'created_at': user.created_at,
            'status_text': 'nouveau',
            'status_class': 'blue',
        }
        for user in CustomUser.objects.order_by('-created_at')[:8]
    ]

    recent_hospitals = [
        {
            'type': 'hopital',
            'icon_letter': 'H',
            'icon_class': 'green',
            'title': hopital.nom,
            'subtitle': 'Hopital en attente' if hopital.statut == 'en_attente' else 'Hopital valide',
            'created_at': hopital.created_at,
            'status_text': 'en attente' if hopital.statut == 'en_attente' else 'valide',
            'status_class': 'amber' if hopital.statut == 'en_attente' else 'green',
        }
        for hopital in Hopital.objects.order_by('-created_at')[:8]
    ]

    recent_inscriptions = sorted(
        recent_users + recent_hospitals,
        key=lambda item: item['created_at'],
        reverse=True,
    )[:6]

    return render(request, 'admin/dashboard_admin_principal.html', {
        'hopitaux_total': hopitaux_total,
        'validations_en_attente': validations_en_attente,
        'hopitaux_confirmes_total': hopitaux_confirmes_total,
        'patients_total': patients_total,
        'livreurs_en_attente_total': livreurs_en_attente_total,
        'hopitaux_valides': hopitaux_valides,
        'hopitaux_en_attente_liste': hopitaux_en_attente_liste,
        'recent_inscriptions': recent_inscriptions,
    })

@login_required
@user_passes_test(lambda u: u.is_authenticated and (u.is_superuser or u.role == 'admin_system'))
def liste_utilisateurs(request):
    utilisateurs = CustomUser.objects.order_by('-created_at')
    return render(request, 'admin/liste_utilisateurs.html', {
        'utilisateurs': utilisateurs,
    })

@login_required
@user_passes_test(lambda u: u.is_authenticated and (u.is_superuser or u.role == 'admin_system'))
def basculer_statut_utilisateur(request, user_id):
    utilisateur = get_object_or_404(CustomUser, id=user_id)

    if utilisateur == request.user:
        messages.warning(request, "Vous ne pouvez pas desactiver votre propre compte.")
        return redirect('liste_utilisateurs')

    utilisateur.is_active = not utilisateur.is_active
    utilisateur.save(update_fields=['is_active'])

    if utilisateur.is_active:
        messages.success(request, f"Le compte de {utilisateur.get_full_name() or utilisateur.email} a ete reactive.")
    else:
        messages.success(request, f"Le compte de {utilisateur.get_full_name() or utilisateur.email} a ete desactive.")

    return redirect('liste_utilisateurs')

@login_required
@user_passes_test(lambda u: u.is_authenticated and (u.is_superuser or u.role == 'admin_system'))
def statistiques_admin(request):
    total_utilisateurs = CustomUser.objects.count()
    utilisateurs_actifs = CustomUser.objects.filter(is_active=True).count()
    utilisateurs_inactifs = CustomUser.objects.filter(is_active=False).count()
    total_patients = CustomUser.objects.filter(role='patient').count()
    total_medecins = CustomUser.objects.filter(role='medecin').count()
    total_admins_hopital = CustomUser.objects.filter(role='admin_hopital').count()
    total_livreurs = CustomUser.objects.filter(role='livreur').count()
    total_hopitaux = Hopital.objects.count()
    hopitaux_confirmes = Hopital.objects.filter(statut='confirme').count()
    hopitaux_en_attente = Hopital.objects.filter(statut='en_attente').count()
    demandes_patients_en_attente = DemandeInscription.objects.filter(statut='en_attente').count()
    rendez_vous_total = RendezVous.objects.count()
    rendez_vous_en_attente = RendezVous.objects.filter(statut='en_attente').count()

    return render(request, 'admin/statistiques.html', {
        'total_utilisateurs': total_utilisateurs,
        'utilisateurs_actifs': utilisateurs_actifs,
        'utilisateurs_inactifs': utilisateurs_inactifs,
        'total_patients': total_patients,
        'total_medecins': total_medecins,
        'total_admins_hopital': total_admins_hopital,
        'total_livreurs': total_livreurs,
        'total_hopitaux': total_hopitaux,
        'hopitaux_confirmes': hopitaux_confirmes,
        'hopitaux_en_attente': hopitaux_en_attente,
        'demandes_patients_en_attente': demandes_patients_en_attente,
        'rendez_vous_total': rendez_vous_total,
        'rendez_vous_en_attente': rendez_vous_en_attente,
    })

@login_required
@user_passes_test(lambda u: u.role == 'admin_hopital')
def dashboard_admin_hopital(request):
    hopital = Hopital.objects.filter(admin=request.user).first()
    context = {
        'hopital': hopital,
        'total_medecins': 0,
        'patients_valides': 0,
        'rdv_en_attente': 0,
        'rdv_valides': 0,
        'rdv_stats_labels': [],
        'rdv_stats_values': [],
    }

    if hopital:
        rdv_en_attente = RendezVous.objects.filter(
            hopital=hopital,
            statut='en_attente'
        ).count()

        context.update({
            'total_medecins': Medecin.objects.filter(hopital=hopital).count(),
            'patients_valides': DemandeInscription.objects.filter(
                hopital=hopital,
                statut__in=['approuve', 'valide']
            ).count(),
            'rdv_en_attente': rdv_en_attente,
            'rdv_valides': RendezVous.objects.filter(
                hopital=hopital,
                medecin__isnull=False,
                statut__in=['approuvé', 'validee']
            ).count(),
        })

        today = datetime.date.today()
        current_week_start = today - datetime.timedelta(days=today.weekday())
        week_labels = []
        week_counts = []

        for offset in range(3, -1, -1):
            start_of_week = current_week_start - datetime.timedelta(weeks=offset)
            end_of_week = start_of_week + datetime.timedelta(days=6)
            week_label = f"S{start_of_week.isocalendar()[1]} ({start_of_week.strftime('%d/%m')} - {end_of_week.strftime('%d/%m')})"
            count = RendezVous.objects.filter(
                hopital=hopital,
                date__gte=start_of_week,
                date__lte=end_of_week
            ).count()
            week_labels.append(week_label)
            week_counts.append(count)

        context.update({
            'rdv_stats_labels': week_labels,
            'rdv_stats_values': week_counts,
        })

    return render(request, 'hopital/dashboard_hopital.html', context)

def dashboard_livreur(request):
    return render(request, 'livreur/dashboard_livreur.html')

def index(request): 
    return render(request, 'accueil/index.html')  

def inscription_patient(request):
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Inscription patient réussie ! Bienvenue.")
            return redirect('dashboard_patient', patient_id=user.id)
        else:
            messages.error(request, "Erreur dans le formulaire.")
    else:
        form = PatientRegistrationForm()
    return render(request, 'registration/inscription_patient.html', {'form': form})

def inscription_hopital(request):
    if request.method == 'POST':
        form = HospitalRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            hopital = form.save()
            messages.success(request, "Demande d'inscription d'hôpital soumise. En attente de confirmation.")
            return redirect('index')
        else:
            messages.error(request, "Erreur dans le formulaire.")
    else:
        form = HospitalRegistrationForm()
    return render(request, 'registration/inscription_hopital.html', {'form': form})

def inscription_livreur(request):
    if request.method == 'POST':
        form = LivreurRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Demande d'emploi livreur soumise. En attente de validation.")
            return redirect('index')
        else:
            messages.error(request, "Erreur dans le formulaire.")
    else:
        form = LivreurRegistrationForm()
    return render(request, 'registration/inscription_livreur.html', {'form': form})


def connexion_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            role = user.role

            if user.is_superuser:
                return redirect('dashboard_admin')
            elif role == 'patient':
                return redirect('dashboard_patient', patient_id=user.id)
            elif role == 'medecin':
                return redirect('dashboard_medecin')
            elif role == 'admin_system':
                return redirect('dashboard_admin')
            elif role == 'admin_hopital':
                return redirect('dashboard_admin_hopital')
            elif role == 'livreur':
                return redirect('dashboard_livreur')
            else:
                return redirect('index')
        else:
            messages.error(request, "Identifiants invalides.")
    else:
        form = AuthenticationForm()
    return render(request, 'registration/connexion.html', {'form': form})

def deconnexion_view(request):
    logout(request)
    return redirect('index')

def is_admin_principal(user):
    return user.is_authenticated and (user.is_superuser or user.role == 'admin_system')

def is_admin_hopital(user):
    return user.is_authenticated and user.role == 'admin_hopital'

@login_required
@user_passes_test(is_admin_principal)
def ajouter_hopital(request):
    if request.method == 'POST':
        form = HopitalForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('liste_hopitaux')
    else:
        form = HopitalForm()
    return render(request, 'hopital/ajout_hopitaux.html', {'form': form},)

@login_required
def liste_hopitaux(request):
    hopitaux = Hopital.objects.all()
    return render(request, 'hopital/hopitaux.html', {'hopitaux': hopitaux})

@login_required
@user_passes_test(is_admin_principal)
def liste_hopitaux_admin(request):
    hopitaux_confirmes = Hopital.objects.filter(statut='confirme').order_by('nom')
    hopitaux_non_confirmes = Hopital.objects.exclude(statut='confirme').order_by('nom')
    return render(request, 'hopital/hopitaux_admin.html', {
        'hopitaux_confirmes': hopitaux_confirmes,
        'hopitaux_non_confirmes': hopitaux_non_confirmes,
    })

@login_required
@user_passes_test(lambda u: u.is_superuser)
def hopitaux_en_attente(request):
    hopitaux = Hopital.objects.filter(statut='en_attente')
    return render(request, 'admin/hopitaux_en_attente.html', {'hopitaux': hopitaux})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def confirmer_hopital(request, hopital_id):
    hopital = get_object_or_404(Hopital, id=hopital_id)
    email_hopital = (hopital.email or "").strip().lower()
    admin_user = hopital.admin
    mot_de_passe_temporaire = None

    if not email_hopital:
        messages.error(request, "Impossible de confirmer cet hopital sans email de contact.")
        return redirect('hopitaux_en_attente')

    if admin_user is None:
        utilisateur_existant = CustomUser.objects.filter(email__iexact=email_hopital).first()

        if utilisateur_existant:
            if utilisateur_existant.role != 'admin_hopital':
                messages.error(
                    request,
                    "Un utilisateur existe deja avec cet email, mais il n'est pas administrateur d'hopital."
                )
                return redirect('hopitaux_en_attente')
            admin_user = utilisateur_existant
        else:
            mot_de_passe_temporaire = get_random_string(12)
            admin_user = CustomUser(
                username=email_hopital,
                email=email_hopital,
                role='admin_hopital',
                first_name=hopital.directeur or hopital.nom,
            )
            admin_user.set_password(mot_de_passe_temporaire)
            admin_user.save()

        hopital.admin = admin_user

    hopital.statut = 'confirme'
    hopital.save()

    sujet = "Confirmation de votre inscription hopital"
    if mot_de_passe_temporaire:
        message = f"""Bonjour,

L'inscription de l'hopital {hopital.nom} a ete confirmee.

Voici vos identifiants de connexion :
Identifiant : {admin_user.email}
Mot de passe temporaire : {mot_de_passe_temporaire}

Merci de vous connecter puis de modifier votre mot de passe depuis votre compte.
"""
    else:
        message = f"""Bonjour,

L'inscription de l'hopital {hopital.nom} a ete confirmee.

Votre compte administrateur est associe a cette adresse :
Identifiant : {admin_user.email}

Vous pouvez vous connecter avec vos identifiants habituels et modifier votre mot de passe apres connexion.
"""

    try:
        send_mail(sujet, message, settings.DEFAULT_FROM_EMAIL, [email_hopital])
        messages.success(request, f"Hopital {hopital.nom} confirme et email envoye.")
    except Exception:
        messages.warning(
            request,
            f"Hopital {hopital.nom} confirme, mais l'email n'a pas pu etre envoye."
        )
    return redirect('hopitaux_en_attente')

@login_required
@user_passes_test(lambda u: u.is_superuser)
def livreurs_en_attente(request):
    livreurs = Livreur.objects.filter(statut='en_attente')
    return render(request, 'admin/livreurs_en_attente.html', {'livreurs': livreurs})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def activer_livreur(request, livreur_id):
    livreur = get_object_or_404(Livreur, id=livreur_id)
    livreur.statut = 'actif'
    livreur.save()
    messages.success(request, f"Livreur {livreur.user.get_full_name()} activé.")
    return redirect('livreurs_en_attente')

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
@user_passes_test(is_admin_hopital) 
def liste_demandes_en_attente(request):
    demandes = DemandeInscription.objects.filter(statut='en_attente')
    return render(request, 'admin/attente.html', {'demandes': demandes})

@login_required
@user_passes_test(is_admin_hopital)
def approuver_demande(request, demande_id):
    demande = get_object_or_404(DemandeInscription, id=demande_id)
    demande.statut = 'approuve'
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
@user_passes_test(is_admin_hopital)
def refuser_demande(request, demande_id):
    demande = get_object_or_404(DemandeInscription, id=demande_id)
    demande.statut = 'refuse'
    demande.save()
    messages.warning(request, "Demande refusée.")
    return redirect('liste_demandes_en_attente')

@login_required
def demandes_validees(request):
    user = request.user

    if user.is_superuser:
        # Le superuser voit toutes les demandes validées
        demandes = DemandeInscription.objects.filter(statut__in=['approuve', 'valide'])
    elif user.role == 'admin_hopital':
        try:
            # Récupère l'hôpital de l'admin connecté
            hopital_admin = Hopital.objects.get(admin=user)
            demandes = DemandeInscription.objects.filter(statut__in=['approuve', 'valide'], hopital=hopital_admin)
        except Hopital.DoesNotExist:
            # L'admin n'a pas encore d'hôpital lié
            demandes = []
    else:
        # Patients ou autres rôles ne voient rien ici
        demandes = []

    return render(request, 'admin/demande_valide.html', {'demandes': demandes})


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
    return render(request, 'patient/ajouter_personne.html', {'form': form})

@login_required 
def personnes_a_prevenir(request):
    personnes = request.user.personnes_a_prevenir.all()
    return render(request, 'patient/personne_prevenir.html', {'personnes': personnes}) 

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
    return render(request, 'patient/modifier_personne.html', {'form': form})



@login_required 
def ajouter_medecin(request):
    if not request.user.is_authenticated:
        return redirect('connexion')
    if not is_admin_hopital(request.user):
        messages.error(request, "Acces refuse: vous devez etre admin pour ajouter un medecin.")
        return redirect('index')

    hopital_admin = Hopital.objects.filter(admin=request.user).first()
    if not hopital_admin:
        messages.error(request, "Aucun hopital n'est associe a votre compte admin.")
        return redirect('dashboard_admin_hopital')

    if request.method == 'POST':
        form = MedecinCreationForm(request.POST)
        if form.is_valid():
            user, password, medecin = form.save(hopital=hopital_admin)
            messages.success(request, "Médecin enregistré avec succès.")
            return redirect('liste_medecins')
    else:
        form = MedecinCreationForm()

    return render(request, 'medecin/ajouter_medecin.html', {'form': form})

def envoyer_identifiants(request, medecin_id):
    if not request.user.is_authenticated:
        return redirect('connexion')
    if not is_admin_hopital(request.user):
        messages.error(request, "Acces refuse: vous devez etre admin pour envoyer les identifiants.")
        return redirect('index')

    medecin = get_object_or_404(Medecin, id=medecin_id)
    user = medecin.user
    password = medecin.mot_de_passe_temporaire

    if not password:
        messages.error(request, "Aucun mot de passe disponible pour ce médecin.")
        return redirect('liste_medecins')

    subject = "Vos identifiants de connexion - Médecin"
    message = f"""Bonjour {user.first_name},

Votre compte médecin a été créé.

Voici vos identifiants de connexion :

Identifiant (username) : {user.username}
Mot de passe : {password}

Email du compte : {user.email}

Merci de vous connecter et de changer votre mot de passe dès la première connexion.
"""

    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
    messages.success(request, "Identifiant envoye.")
    return redirect('liste_medecins')




@login_required     
def liste_medecins(request):
    hopital_admin = Hopital.objects.filter(admin=request.user).first()
    search = request.GET.get('q', '').strip()
    specialite = request.GET.get('specialite', '').strip()
    statut = request.GET.get('statut', 'actif').strip()

    if not hopital_admin:
        return render(request, 'medecin/liste_medecins.html', {
            'medecins': [],
            'specialites': [],
            'current_search': search,
            'current_specialite': specialite,
            'current_statut': statut,
            'empty_message': "Aucun médecin associé à cet hôpital pour le moment."
        })

    medecins = Medecin.objects.filter(hopital=hopital_admin)
    specialites = (
        medecins.exclude(specialite='')
        .order_by('specialite')
        .values_list('specialite', flat=True)
        .distinct()
    )

    if search:
        medecins = medecins.filter(
            Q(user__first_name__icontains=search)
            | Q(user__last_name__icontains=search)
            | Q(user__email__icontains=search)
            | Q(user__username__icontains=search)
        )

    if specialite:
        medecins = medecins.filter(specialite=specialite)

    if statut == 'inactif':
        medecins = medecins.filter(user__is_active=False)
    elif statut == 'actif':
        medecins = medecins.filter(user__is_active=True)
    return render(request, 'medecin/liste_medecins.html', {
        'medecins': medecins,
        'specialites': specialites,
        'current_search': search,
        'current_specialite': specialite,
        'current_statut': statut,
        'empty_message': "Aucun médecin associé à cet hôpital pour le moment." if not medecins.exists() else "",
    })

@login_required
def liste_rendezvous_hopital(request):
    try:
        hopital_admin = Hopital.objects.get(admin=request.user)
    except Hopital.DoesNotExist:
        messages.error(request, "Aucun hôpital associé à cet administrateur.")
        return redirect('dashboard_admin_hopital')

    rendez_vous = RendezVous.objects.filter(hopital=hopital_admin, statut='en_attente')
    return render(request, 'rendez-vous/liste_rendezvous.html', {'rendez_vous': rendez_vous})


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

    return render(request, 'admin/modifier-profil.html', {
        'form_user': form_user,
        'form_medecin': form_medecin,
        'form_password': form_password,
    })


def profil_medecin(request):
    medecin = Medecin.objects.get(user=request.user)
    return render(request, 'medecin/profil_medecin.html', {'medecin': medecin})

@login_required
def profil_patient(request):
    return render(request, 'patient/profil_patient.html', {'patient': request.user})

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

    return render(request, 'patient/modifier_profil_patient.html', {'form': form})



@login_required
def prendre_rendez_vous(request):
    hopitaux_valides = Hopital.objects.filter(
        id__in=DemandeInscription.objects.filter(
            patient=request.user,
            statut__in=['approuve', 'valide']
        ).values_list('hopital_id', flat=True)
    )

    if request.method == 'POST':
        form = RendezVousForm(request.POST, user=request.user)
        form.fields['hopital'].queryset = hopitaux_valides
        if form.is_valid():
            rdv = form.save(commit=False)
            rdv.patient = request.user
            rdv.medecin = None  # médecin attribué plus tard par l’hôpital
            rdv.save()
            return redirect('liste_rendez_vous')
    else:
        form = RendezVousForm(user=request.user)
        form.fields['hopital'].queryset = hopitaux_valides
    return render(request, 'rendez-vous/prendre_rendez_vous.html', {'form': form})



@login_required
def mes_rendezvous(request):
    rdvs = RendezVous.objects.filter(patient=request.user)
    return render(request, 'rendez-vous/mes_rendez_vous.html', {'rdvs': rdvs})

@login_required
def liste_rendezvous_hopital(request):
    try:
        hopital_admin = Hopital.objects.get(admin=request.user)
    except Hopital.DoesNotExist:
        messages.error(request, "Aucun hôpital associé à cet administrateur.")
        return redirect('dashboard_admin_hopital')

    rendez_vous = RendezVous.objects.filter(hopital=hopital_admin, statut='en_attente')
    return render(request, 'rendez_vous/liste_rendezvous.html', {'rendez_vous': rendez_vous})


@login_required
@user_passes_test(is_admin_hopital)
def valider_rdv(request, rdv_id):
    rdv = get_object_or_404(RendezVous, id=rdv_id)

    if request.user != rdv.hopital.admin:
        messages.error(request, "Vous ne pouvez pas valider ce rendez-vous.")
        return redirect('liste_rendezvous_hopital')

    if request.method == 'POST':
        form = ValidationRendezVousForm(request.POST, instance=rdv, hopital=rdv.hopital)
        if form.is_valid():
            rdv = form.save(commit=False)
            rdv.statut = 'approuvé' 
            rdv.save()
            messages.success(request, "Rendez-vous validé et médecin attribué.")
            return redirect('liste_rendezvous_hopital')
    else:
        form = ValidationRendezVousForm(instance=rdv, hopital=rdv.hopital)

    return render(request, 'rendez-vous/valider_rdv.html', {
        'form': form,
        'rdv': rdv
    })


@login_required
def refuser_rdv(request, rdv_id):
    rdv = get_object_or_404(RendezVous, id=rdv_id)
    rdv.statut = 'refuse'
    rdv.save()
    return redirect('liste_rendezvous_hopital')


@login_required
@user_passes_test(is_admin_hopital)
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
            statut__in=['approuve', 'valide']
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

    return render(request, 'admin/assign_patients.html', {
        'form': form,
        'medecin': medecin
    })


@login_required
def mes_patients(request):
    user = request.user

    try:
        medecin = Medecin.objects.get(user=user)
    except Medecin.DoesNotExist:
        messages.error(request, "Ce compte n'est pas lié à un médecin.")
        return redirect('index')

    patients = medecin.patients.all()  # Tous les patients assignés

    query = request.GET.get('q', '')
    if query:
        patients = patients.filter(
            Q(first_name__icontains=query) | Q(last_name__icontains=query)
        )

    return render(request, 'patient/patient_medecin.html', {
        'medecin': medecin,
        'patients': patients,
        'query': query,
    })



@login_required
def voir_dossier_medical(request, patient_id):
    dossier = DossierMedical.objects.filter(patient_id=patient_id).first()
    
    # Si le dossier n'existe pas, afficher un message au lieu d'une erreur 404
    if not dossier:
        messages.info(request, "Le dossier médical n'existe pas encore pour ce patient.")
        return redirect('dashboard_patient', patient_id=patient_id)
    
    suivis = dossier.suivis.all().order_by('-date_consultation')  # historique

    base_template = "patient/base_patient.html"
    peut_modifier = False

    if request.user.role == 'medecin':
        base_template = "medecin/base_medecin.html"
        # Exemple : autoriser le médecin s'il est dans une relation à implémenter
        # Ici on ne permet pas la modif par défaut
        peut_modifier = False

    elif request.user.role == 'admin_hopital':
        base_template = "hopital/base_admin_hopital.html"
        peut_modifier = True

    return render(request, 'dossier-medical/voir_dossier.html', {
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

    return render(request, "medecin/ajouter_suivi_medical.html", {"form": form, "dossier": dossier})



@login_required
def modifier_dossier_medical(request, patient_id):
    dossier = get_object_or_404(DossierMedical, patient_id=patient_id)

    # Vérification des droits
    if request.user.role == "medecin":
        if hasattr(dossier, "medecin") and dossier.medecin != request.user:
            messages.error(request, "Vous n'êtes pas autorisé à modifier ce dossier.")
            return redirect("voir_dossier_medical", patient_id=patient_id)
    elif request.user.role != "admin_hopital":
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

    return render(request, "dossier-medeical/modifier_dossier_medical.html", {
        "form": form,
        "dossier": dossier
    })

@login_required
def creer_ordonnance(request, patient_id):
    # Vérifie que l'utilisateur est médecin
    if not hasattr(request.user, 'medecin'):
        return HttpResponseForbidden("Seuls les médecins peuvent créer des ordonnances.")
    
    medecin = request.user.medecin

    # Vérifie que le patient appartient bien à ce médecin
    patient = get_object_or_404(
    CustomUser,
    id=patient_id,
    role='patient',
    medecins_assignés=medecin
)


    if request.method == 'POST':
        form = OrdonnanceForm(request.POST)
        formset = MedicamentFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            ordonnance = form.save(commit=False)
            ordonnance.medecin = medecin
            ordonnance.patient = patient
            ordonnance.save()

            formset.instance = ordonnance
            formset.save()

            return redirect('voir_dossier_medical', patient.id)
    else:
        form = OrdonnanceForm()
        formset = MedicamentFormSet()

    return render(request, 'ordonnance/creer_ordonnance.html', {
        'form': form,
        'formset': formset,
        'patient': patient
    })


# Vue côté patient

@login_required
def mes_ordonnances(request):
    patient = request.user
    ordonnances = Ordonnance.objects.filter(patient=patient)
    return render(request, 'ordonnance/mes_ordonnance.html', {'ordonnances': ordonnances})


@login_required
def ordonnances_prescrites(request):
    # Récupérer le médecin lié à l'utilisateur connecté
    try:
        medecin = Medecin.objects.get(user=request.user)
    except Medecin.DoesNotExist:
        return render(request, 'vous devez etre un médecin')  # ou message d'erreur

    # Récupérer toutes les ordonnances de ce médecin
    ordonnances = Ordonnance.objects.filter(medecin=medecin).order_by('-date_creation')

    return render(request, 'ordonnance/ordonnance_prescrite.html', {'ordonnances': ordonnances})


@login_required
def telecharger_ordonnance(request, ordonnance_id):
    try:
        ordonnance = Ordonnance.objects.get(id=ordonnance_id)
    except Ordonnance.DoesNotExist:
        return HttpResponse("Ordonnance non trouvée.", status=404)

    user = request.user

    # Vérifier que l'utilisateur est soit le patient, soit le médecin prescripteur
    if not (ordonnance.patient == user or ordonnance.medecin.user == user):
        return HttpResponse("Accès refusé.", status=403)

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    x_margin = 2 * cm
    y = height - 2 * cm

    # Titre
    p.setFont("Helvetica-Bold", 18)
    p.drawString(x_margin, y, "Ordonnance médicale")
    y -= 1.5 * cm

    # Infos patient et médecin
    p.setFont("Helvetica", 12)
    p.drawString(x_margin, y, f"Patient : {ordonnance.patient.get_full_name()}")
    y -= 0.7 * cm
    p.drawString(x_margin, y, f"Médecin : Dr. {ordonnance.medecin.user.get_full_name()}")
    y -= 0.7 * cm
    p.drawString(x_margin, y, f"Date : {ordonnance.date_creation.strftime('%d/%m/%Y')}")
    y -= 1 * cm

    # Observations
    p.setFont("Helvetica-Bold", 14)
    p.drawString(x_margin, y, "Observations :")
    y -= 0.8 * cm

    p.setFont("Helvetica", 12)
    text = p.beginText(x_margin, y)
    for line in ordonnance.observations.split('\n'):
        text.textLine(line)
        y -= 0.5 * cm
    p.drawText(text)
    y = text.getY() - 1 * cm

    # Médicaments prescrits
    p.setFont("Helvetica-Bold", 14)
    p.drawString(x_margin, y, "Médicaments prescrits :")
    y -= 1 * cm

    p.setFont("Helvetica", 12)
    medicaments = ordonnance.medicaments.all()
    if medicaments:
        for medicament in medicaments:
            ligne = f"- {medicament.nom} : {medicament.dosage}"
            p.drawString(x_margin + 0.5 * cm, y, ligne)
            y -= 0.7 * cm
            if y < 5 * cm:  # garde un espace en bas pour la signature
                p.showPage()
                y = height - 2 * cm
    else:
        p.drawString(x_margin + 0.5 * cm, y, "Aucun médicament prescrit.")
        y -= 0.7 * cm

    # --- Ajout de la zone signature ---
    if y < 5 * cm:
        p.showPage()
        y = height - 5 * cm

    # Ligne signature
    ligne_x_start = x_margin
    ligne_x_end = x_margin + 8 * cm
    ligne_y = y - 2 * cm
    p.line(ligne_x_start, ligne_y, ligne_x_end, ligne_y)

    # Texte sous la ligne
    p.setFont("Helvetica-Oblique", 10)
    p.drawString(ligne_x_start, ligne_y - 15, "Signature du médecin")

    # Finaliser PDF
    p.showPage()
    p.save()

    buffer.seek(0)
    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="ordonnance_{ordonnance.id}.pdf"'
    return response


@login_required
def liste_rendezvous_valides(request):
    user = request.user
    statuts_valides = ['approuvé', 'approuvÃ©', 'validee']

    if user.role == 'admin_hopital':
        # On récupère l'hôpital de l'admin
        try:
            hopital = Hopital.objects.get(admin=user)
        except Hopital.DoesNotExist:
            messages.error(request, "Aucun hôpital associé à cet administrateur.")
            return redirect('dashboard_admin_hopital')

        # RDV validés pour cet hôpital
        rdvs = RendezVous.objects.filter(
            hopital=hopital,
            medecin__isnull=False,
            statut__in=statuts_valides
        ).order_by('date', 'heure')

    elif user.role == 'medecin':
        # RDV validés attribués au médecin connecté
        try:
            medecin = Medecin.objects.get(user=user)
        except Medecin.DoesNotExist:
            messages.error(request, "Vous n'êtes pas un médecin reconnu.")
            return redirect('dashboard_medecin')

        rdvs = RendezVous.objects.filter(
            medecin=medecin,
            statut__in=statuts_valides
        ).order_by('date', 'heure')

    else:
        messages.error(request, "Accès interdit.")
        return redirect('index')

    return render(request, 'rendez-vous/rendezvous_valides.html', {'rendez_vous': rdvs})

@login_required
def liste_rendezvous_medecin(request):
    user = request.user

    try:
        medecin = Medecin.objects.get(user=user)
    except Medecin.DoesNotExist:
        messages.error(request, "Ce compte n'est pas lié à un médecin.")
        return redirect('index')

    # On récupère les rendez-vous validés attribués à ce médecin
    rdvs = RendezVous.objects.filter(
        medecin=medecin,
        statut__in=['approuvé', 'approuvÃ©', 'validee']
    ).order_by('date', 'heure')

    return render(request, 'medecin/liste_rendezvous_medecin.html', {
        'medecin': medecin,  
        'rendez_vous': rdvs,
    })
