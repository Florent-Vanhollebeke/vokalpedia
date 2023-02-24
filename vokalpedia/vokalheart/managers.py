
from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Créer et enregistrer un utilisateur avec l'adresse email et le mot de passe fournis.
        """
        if not email:
            raise ValueError('L\'adresse email doit être fournie.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Créer et enregistrer un superutilisateur avec l'adresse email et le mot de passe fournis.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

