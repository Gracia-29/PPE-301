# urls.py
from django.urls import path
from . import views
from .api_views import LoginAPI, RegisterAPI

urlpatterns = [
    path('', views.index, name='index'),
    path('inscription/patient/', views.inscription_patient, name='inscription_patient'),
    path('inscription/hopital/', views.inscription_hopital, name='inscription_hopital'),
    path('inscription/livreur/', views.inscription_livreur, name='inscription_livreur'),
    path('connexion/', views.connexion_view, name='connexion'),
    path('deconnexion/', views.deconnexion_view, name='deconnexion'),
    path('dashboard/patient/<int:patient_id>/', views.dashboard_patient, name='dashboard_patient'),
    path('dashboard/medecin/', views.dashboard_medecin, name='dashboard_medecin'),
    path('dashboard/admin/', views.dashboard_admin, name='dashboard_admin'),
    path('dashboard/admin/utilisateurs/', views.liste_utilisateurs, name='liste_utilisateurs'),
    path('dashboard/admin/utilisateurs/<int:user_id>/statut/', views.basculer_statut_utilisateur, name='basculer_statut_utilisateur'),
    path('dashboard/admin/statistiques/', views.statistiques_admin, name='statistiques_admin'),
    path('dashboard/admin-hopital/', views.dashboard_admin_hopital, name='dashboard_admin_hopital'),
    path('dashboard/livreur/', views.dashboard_livreur, name='dashboard_livreur'),
    path('ajout/hopitaux', views.ajouter_hopital, name='ajouter_hopital'),
    path('hopitaux/', views.liste_hopitaux, name='liste_hopitaux'),
    path('admin/hopitaux/', views.liste_hopitaux_admin, name='liste_hopitaux_admin'),
    path('hopitaux-en-attente/', views.hopitaux_en_attente, name='hopitaux_en_attente'),
    path('confirmer-hopital/<int:hopital_id>/', views.confirmer_hopital, name='confirmer_hopital'),
    path('livreurs-en-attente/', views.livreurs_en_attente, name='livreurs_en_attente'),
    path('activer-livreur/<int:livreur_id>/', views.activer_livreur, name='activer_livreur'),
    path('demande-inscription/<int:hopital_id>/', views.demander_inscription, name='demande_inscription'),
    path('demandes-en-attente/', views.liste_demandes_en_attente, name='liste_demandes_en_attente'),
    path('approuver-demande/<int:demande_id>/', views.approuver_demande, name='approuver_demande'),
    path('refuser-demande/<int:demande_id>/', views.refuser_demande, name='refuser_demande'),
    path('demandes/validees/', views.demandes_validees, name='demandes_validees'),
    path('ajouter-personne/', views.ajouter_personne_a_prevenir, name='ajouter_personne'),
    path('personnes-a-prevenir/', views.personnes_a_prevenir, name='personnes_a_prevenir'),
    path('personne/<int:personne_id>/supprimer/', views.supprimer_personne, name='supprimer_personne'),
    path('personne/<int:personne_id>/modifier/', views.modifier_personne, name='modifier_personne'),
    path('ajouter-medecin/', views.ajouter_medecin, name='ajouter_medecin'),
    path('liste-medecins/', views.liste_medecins, name='liste_medecins'),
    path('medecins/envoyer-identifiants/<int:medecin_id>/', views.envoyer_identifiants, name='envoyer_identifiants'),
    
    path('rendez-vous/ajouter/', views.prendre_rendez_vous, name='ajouter_rendez_vous'),
    path('rendez-vous/liste/', views.mes_rendezvous, name='liste_rendez_vous'),
    
    path('medecin/profil/', views.modifier_profil_medecin, name='modifier_profil_medecin'),
    path('profil/', views.profil_medecin, name='profil_medecin'),
    path('profil-patient/', views.profil_patient, name='profil_patient'),
    path('modifier-profil-patient/', views.modifier_profil_patient, name='modifier_profil_patient'),
    path('hopital/rendez-vous/', views.liste_rendezvous_hopital, name='liste_rendezvous_hopital'),
    path('rendezvous/<int:rdv_id>/valider/', views.valider_rdv, name='valider_rdv'),
    path('hopital/rendez-vous/refuser/<int:rdv_id>/', views.refuser_rdv, name='refuser_rdv'),

    path('assigner-patients/<int:medecin_id>/', views.assign_patients_to_medecin, name='assign_patients'),
    path('mes-patients/', views.mes_patients, name='mes_patients'),
    path('dossier-medical/<int:patient_id>/', views.voir_dossier_medical, name='voir_dossier_medical'),
    path('suivi-medical/ajouter/<int:patient_id>/', views.ajouter_suivi_medical, name='ajouter_suivi_medical'),
    path('dossier-medical/modifier/<int:patient_id>/', views.modifier_dossier_medical, name='modifier_dossier_medical'),
    
    path('ordonnance/creer/<int:patient_id>/', views.creer_ordonnance, name='creer_ordonnance'),
    path('ordonnance/voir/<int:patient_id>/', views.mes_ordonnances, name='mes_ordonnances'),
    path('ordonnance/voir/', views.mes_ordonnances, name='mes_ordonnances'),
    path('ordonnance/telecharger/<int:ordonnance_id>/', views.telecharger_ordonnance, name='telecharger_ordonnance'),
    path('medecin/ordonnances/', views.ordonnances_prescrites, name='ordonnances_prescrites'),
    path('rendezvous/valides/', views.liste_rendezvous_valides, name='liste_rendezvous_valides'),
    path('prendre/rendezvous', views.prendre_rendez_vous, name='prendre_rendez_vous'),
    path('medecin/rendezvous/', views.liste_rendezvous_medecin, name='liste_rendezvous_medecin'),

    path('api/login/', LoginAPI.as_view()),
    path('api/register/', RegisterAPI.as_view()),




]
    




























