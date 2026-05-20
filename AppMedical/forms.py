# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.db import transaction
from django.forms import inlineformset_factory

from .models import *


class PatientRegistrationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'email', 'password1', 'password2',
            'genre', 'telephone', 'date_naissance'
        ]
        widgets = {
            'date_naissance': forms.DateInput(attrs={'type': 'date'}),
            'telephone': forms.TextInput(attrs={'type': 'tel'}),
            'genre': forms.Select(attrs={'class': 'form-select'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'Prenom'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Nom'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
            'password1': forms.PasswordInput(attrs={'placeholder': 'Mot de passe'}),
            'password2': forms.PasswordInput(attrs={'placeholder': 'Confirmer le mot de passe'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.role = 'patient'
        user.telephone = self.cleaned_data.get('telephone')
        user.date_naissance = self.cleaned_data.get('date_naissance')
        user.genre = self.cleaned_data.get('genre')

        if commit:
            user.save()
        return user


class LivreurRegistrationForm(UserCreationForm):
    permis_conduire = forms.CharField(max_length=50, required=False, label='Type de permis de conduire')
    vehicule = forms.CharField(max_length=100, required=False, label='Type de vehicule')
    zone_livraison = forms.CharField(max_length=100, required=False, label='Zone de livraison preferee')

    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'email', 'password1', 'password2',
            'telephone', 'adresse'
        ]
        widgets = {
            'telephone': forms.TextInput(attrs={'type': 'tel'}),
            'adresse': forms.Textarea(attrs={'rows': 2}),
            'first_name': forms.TextInput(attrs={'placeholder': 'Prenom'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Nom'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
            'password1': forms.PasswordInput(attrs={'placeholder': 'Mot de passe'}),
            'password2': forms.PasswordInput(attrs={'placeholder': 'Confirmer le mot de passe'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.role = 'livreur'

        if commit:
            user.save()
            Livreur.objects.create(
                user=user,
                permis_conduire=self.cleaned_data.get('permis_conduire'),
                vehicule=self.cleaned_data.get('vehicule'),
                zone_livraison=self.cleaned_data.get('zone_livraison'),
                statut='en_attente'
            )
        return user


class HospitalRegistrationForm(forms.ModelForm):
    class Meta:
        model = Hopital
        fields = [
            'nom',
            'type',
            'numero_enregistrement',
            'nif',
            'licence',
            'date_expiration',
            'adresse',
            'ville',
            'telephone',
            'email',
            'directeur',
        ]
        labels = {
            'numero_enregistrement': "Numero d'enregistrement",
            'date_expiration': "Date d'expiration",
        }
        widgets = {
            'nom': forms.TextInput(attrs={'placeholder': "Nom de l'hopital"}),
            'type': forms.Select(),
            'numero_enregistrement': forms.TextInput(attrs={'placeholder': "Numero d'enregistrement"}),
            'nif': forms.TextInput(attrs={'placeholder': 'NIF'}),
            'licence': forms.ClearableFileInput(attrs={'accept': '.pdf,application/pdf'}),
            'date_expiration': forms.DateInput(attrs={'type': 'date'}),
            'adresse': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Adresse'}),
            'ville': forms.TextInput(attrs={'placeholder': 'Ville'}),
            'telephone': forms.TextInput(attrs={'type': 'tel', 'placeholder': 'Telephone'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
            'directeur': forms.TextInput(attrs={'placeholder': 'Directeur'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name in [
            'nom',
            'type',
            'numero_enregistrement',
            'nif',
            'licence',
            'date_expiration',
            'adresse',
            'ville',
            'telephone',
            'email',
            'directeur',
        ]:
            self.fields[field_name].required = True

    def clean_licence(self):
        licence = self.cleaned_data.get('licence')
        if licence and not licence.name.lower().endswith('.pdf'):
            raise ValidationError("La licence doit etre un fichier PDF.")
        return licence

    def save(self, commit=True):
        hopital = super().save(commit=False)
        hopital.statut = 'en_attente'

        if commit:
            hopital.save()
        return hopital


class HospitalRegistrationStepOneForm(forms.ModelForm):
    class Meta:
        model = Hopital
        fields = [
            'nom',
            'type',
            'numero_enregistrement',
            'nif',
            'licence',
            'date_expiration',
        ]
        labels = {
            'numero_enregistrement': "Numero d'enregistrement",
            'date_expiration': "Date d'expiration",
        }
        widgets = {
            'nom': forms.TextInput(attrs={'placeholder': "Nom de l'hopital"}),
            'type': forms.Select(),
            'numero_enregistrement': forms.TextInput(attrs={'placeholder': "Numero d'enregistrement"}),
            'nif': forms.TextInput(attrs={'placeholder': 'NIF'}),
            'licence': forms.ClearableFileInput(attrs={'accept': '.pdf,application/pdf'}),
            'date_expiration': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_licence(self):
        licence = self.cleaned_data.get('licence')
        if licence and not licence.name.lower().endswith('.pdf'):
            raise ValidationError("La licence doit etre un fichier PDF.")
        return licence


class HospitalRegistrationStepTwoForm(forms.ModelForm):
    class Meta:
        model = Hopital
        fields = [
            'adresse',
            'ville',
            'telephone',
            'email',
            'directeur',
        ]
        widgets = {
            'adresse': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Adresse'}),
            'ville': forms.TextInput(attrs={'placeholder': 'Ville'}),
            'telephone': forms.TextInput(attrs={'type': 'tel', 'placeholder': 'Telephone'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
            'directeur': forms.TextInput(attrs={'placeholder': 'Directeur'}),
        }


class DemandeInscriptionForm(forms.ModelForm):
    class Meta:
        model = DemandeInscription
        fields = ['hopital', 'groupe_sanguin', 'antecedents', 'allergies', 'informations_complementaires']
        widgets = {
            'hopital': forms.HiddenInput(),
            'groupe_sanguin': forms.Select(attrs={'class': 'form-control'}),
            'antecedents': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'allergies': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'informations_complementaires': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class PersonneAPrevenirForm(forms.ModelForm):
    class Meta:
        model = PersonneAPrevenir
        fields = ['nom', 'relation', 'telephone', 'email']
        widget = {
            'nom': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'relation': forms.CharField(max_length=150),
            'email': forms.EmailField(),
            'telephone': forms.CharField(max_length=150),
        }


class MedecinCreationForm(forms.ModelForm):
    nom = forms.CharField(max_length=150)
    prenom = forms.CharField(max_length=150)
    email = forms.EmailField()
    telephone = forms.CharField(max_length=20)
    specialite = forms.CharField(max_length=100)

    class Meta:
        model = Medecin
        fields = ['specialite', 'telephone']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(username=email).exists():
            raise ValidationError("Cet email est deja utilise pour un autre utilisateur.")
        return email

    @transaction.atomic
    def save(self, commit=True, hopital=None):
        import random
        import string

        if not hopital:
            raise ValueError("Hopital requis pour l'enregistrement du medecin.")

        password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        email = self.cleaned_data['email']
        nom = self.cleaned_data['nom']
        prenom = self.cleaned_data['prenom']

        user = CustomUser.objects.create_user(
            username=email,
            email=email,
            first_name=prenom,
            last_name=nom,
            password=password,
            role='medecin'
        )
        user.is_active = True
        user.save()

        medecin = Medecin.objects.create(
            user=user,
            specialite=self.cleaned_data['specialite'],
            telephone=self.cleaned_data['telephone'],
            hopital=hopital,
            mot_de_passe_temporaire=password
        )

        return user, password, medecin


class RendezVousForm(forms.ModelForm):
    hopital = forms.ModelChoiceField(
        queryset=Hopital.objects.none(),
        required=True,
        label='Hopital',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = RendezVous
        fields = ['hopital', 'date', 'heure', 'motif']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'heure': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(RendezVousForm, self).__init__(*args, **kwargs)

        if user:
            demandes = DemandeInscription.objects.filter(patient=user, statut__in=['approuve', 'valide'])
            hopitaux_autorises = Hopital.objects.filter(id__in=demandes.values_list('hopital_id', flat=True))
            self.fields['hopital'].queryset = hopitaux_autorises


class MedecinProfilForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'telephone', 'adresse', 'date_naissance', 'genre', 'photo']


class MedecinInfosProForm(forms.ModelForm):
    class Meta:
        model = Medecin
        fields = ['specialite']
        widgets = {
            'adresse': forms.TextInput(attrs={'class': 'form-control', 'rows': 0}),
        }


class PatientUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'telephone', 'adresse', 'genre', 'date_naissance', 'photo']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prenom'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'type': 'tel', 'placeholder': 'Numero de telephone'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Adresse'}),
            'genre': forms.Select(attrs={'class': 'form-select'}),
            'date_naissance': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'photo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }


class AssignPatientsForm(forms.ModelForm):
    class Meta:
        model = Medecin
        fields = ['patients']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            self.fields['patients'].queryset = CustomUser.objects.filter(
                role='patient',
                hopital=user.hopital
            )


class SuiviMedicalForm(forms.ModelForm):
    class Meta:
        model = SuiviMedical
        exclude = ['dossier']
        widgets = {
            'poids': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Poids (kg)'}),
            'taille': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Taille (cm)'}),
            'tension_arterielle': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 12/8'}),
            'temperature': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Temperature (C)'}),
            'observations': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'examens': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'traitements': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'prescriptions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class DossierMedicalForm(forms.ModelForm):
    class Meta:
        model = DossierMedical
        fields = [
            'groupe_sanguin',
            'antecedents',
            'allergies',
            'infos_complementaires',
        ]
        widgets = {
            'groupe_sanguin': forms.TextInput(attrs={'class': 'form-control'}),
            'antecedents': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'allergies': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'infos_complementaires': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class OrdonnanceForm(forms.ModelForm):
    class Meta:
        model = Ordonnance
        fields = ['observations']
        widgets = {
            'observations': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }


class MedicamentPrescritForm(forms.ModelForm):
    class Meta:
        model = MedicamentPrescrit
        fields = ['nom', 'dosage', 'frequence', 'duree']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'dosage': forms.TextInput(attrs={'class': 'form-control'}),
            'frequence': forms.TextInput(attrs={'class': 'form-control'}),
            'duree': forms.TextInput(attrs={'class': 'form-control'}),
        }


MedicamentFormSet = inlineformset_factory(
    Ordonnance,
    MedicamentPrescrit,
    form=MedicamentPrescritForm,
    extra=1,
    can_delete=True
)


class ValidationRendezVousForm(forms.ModelForm):
    medecin = forms.ModelChoiceField(queryset=Medecin.objects.none(), required=True, label='Attribuer un medecin')

    class Meta:
        model = RendezVous
        fields = ['medecin']

    def __init__(self, *args, **kwargs):
        hopital = kwargs.pop('hopital', None)
        super().__init__(*args, **kwargs)
        if hopital:
            self.fields['medecin'].queryset = Medecin.objects.filter(hopital=hopital)
