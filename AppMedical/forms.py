# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import *
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = [
            'username', 'first_name', 'last_name',
            'email', 'password1', 'password2',
            'role', 'genre', 'telephone', 'adresse',
            'date_naissance', 'photo',
        ]
        widgets = {
            'date_naissance': forms.DateInput(attrs={'type': 'date'}),
            'adresse': forms.Textarea(attrs={'rows': 1}),
            'telephone': forms.TextInput(attrs={'type': 'tel', 'pattern': '(^[0-9]{8}$)|(^\\+228[0-9]{8}$)'}),    
            'photo': forms.ClearableFileInput(attrs={'accept': 'image/*'}), 
            'role': forms.Select(attrs={'class': 'form-select'}),
            'genre': forms.Select(attrs={'class': 'form-select'}),
            'username': forms.TextInput(attrs={'placeholder': 'Nom d’utilisateur'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'Prénom'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Nom'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),  
            'password1': forms.PasswordInput(attrs={'placeholder': 'Mot de passe'}),
            'password2': forms.PasswordInput(attrs={'placeholder': 'Confirmer le mot de passe'}), 
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.telephone = self.cleaned_data.get('telephone')
        user.adresse = self.cleaned_data.get('adresse')
        user.date_naissance = self.cleaned_data.get('date_naissance')
        user.genre = self.cleaned_data.get('genre')
        user.role = self.cleaned_data.get('role')
        user.photo = self.cleaned_data.get('photo')

        if commit:
            user.save()
        return user



class CustomLoginForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            user = authenticate(self.request, username=username, password=password)
            if user is None:
                raise forms.ValidationError("Nom d'utilisateur ou mot de passe invalide.")
            self.user = user
        return cleaned_data

    def get_user(self):
        return self.user
    
class HopitalForm(forms.ModelForm):
    class Meta:
        model = Hopital
        fields = ['nom', 'adresse', 'admin']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse': forms.TextInput(attrs={'class': 'form-control'}),
            'admin': forms.Select(attrs={'class': 'form-select'}),
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
            raise ValidationError("Cet email est déjà utilisé pour un autre utilisateur.")
        return email

    def save(self, commit=True, hopital=None):
        import random
        import string

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

        if hopital:
            medecin = Medecin.objects.create(
                user=user,
                specialite=self.cleaned_data['specialite'],
                telephone=self.cleaned_data['telephone'],
                hopital=hopital,
                mot_de_passe_temporaire=password 
            )
        else:
            raise ValueError("Hopital requis pour l'enregistrement du médecin.")

        return user, password
    

class RendezVousForm(forms.ModelForm):
    hopital = forms.ModelChoiceField(
        queryset=Hopital.objects.none(),
        required=True,
        label="Hôpital",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = RendezVous
        fields = ['hopital', 'date', 'heure', 'motif'] 
        widgets ={
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'heure':forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),

        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(RendezVousForm, self).__init__(*args, **kwargs)

        if user:
            demandes = DemandeInscription.objects.filter(patient=user, approuvee=True)
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
            'adresse': forms.TextInput(attrs={'class': 'form-control', 'rows': 0 }),
        }

class PatientUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'telephone', 'adresse', 'genre', 'date_naissance', 'photo']


class AssignPatientsForm(forms.ModelForm):
    class Meta:
        model = Medecin
        fields = ['patients']  # patients doit être un ManyToManyField dans Medecin

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
        exclude = ["dossier"]
        widgets = {
            "poids": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Poids (kg)"}),
            "taille": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Taille (cm)"}),
            "tension_arterielle": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex: 12/8"}),
            "temperature": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Température (°C)"}),
            "observations": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "examens": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "traitements": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "prescriptions": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }




class DossierMedicalForm(forms.ModelForm):
    class Meta:
        model = DossierMedical
        fields = [
            "groupe_sanguin",
            "antecedents",
            "allergies",
            "infos_complementaires",
        ]
        widgets = {
            "groupe_sanguin": forms.TextInput(attrs={"class": "form-control"}),
            "antecedents": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "allergies": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "infos_complementaires": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

