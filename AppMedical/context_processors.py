from .models import DemandeInscription


def demande_inscription_approuvee(request):
    """Expose dans le contexte si le patient a une demande d'inscription approuvée.

    Retourne `{'demande_inscription_validee': True/False}`.
    """
    validated = False
    try:
        user = getattr(request, 'user', None)
        if user and user.is_authenticated and getattr(user, 'role', None) == 'patient':
            validated = DemandeInscription.objects.filter(patient=user, approuvee=True).exists()
    except Exception:
        validated = False
    return {'demande_inscription_validee': validated}
