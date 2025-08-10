# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('inscription/', views.inscription_view, name='inscription'),
    path('connexion/', views.connexion_view, name='connexion'),
    path('deconnexion/', views.deconnexion_view, name='deconnexion'),
    path('dashboard/patient/', views.dashboard_patient, name='dashboard_patient'),
    path('dashboard/medecin/', views.dashboard_medecin, name='dashboard_medecin'),
    path('dashboard/admin/', views.dashboard_admin, name='dashboard_admin'),
    path('ajout/hopitaux', views.ajouter_hopital, name='ajouter_hopital'),
    path('hopitaux/', views.liste_hopitaux, name='liste_hopitaux'),
    path('hopitaux-admin/', views.liste_hopitaux_admin, name='liste_hopitaux_admin'),
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
    path('hopital/rendez-vous/valider/<int:rdv_id>/', views.valider_rdv, name='valider_rdv'),
    path('hopital/rendez-vous/refuser/<int:rdv_id>/', views.refuser_rdv, name='refuser_rdv'),

    path('assigner-patients/<int:medecin_id>/', views.assign_patients_to_medecin, name='assign_patients'),
    path('mes-patients/', views.mes_patients, name='mes_patients'),
    path('dossier-medical/<int:patient_id>/', views.voir_dossier_medical, name='voir_dossier_medical'),
    path('suivi-medical/ajouter/<int:patient_id>/', views.ajouter_suivi_medical, name='ajouter_suivi_medical'),
    path('dossier-medical/modifier/<int:patient_id>/', views.modifier_dossier_medical, name='modifier_dossier_medical'),



]
    




























