from pydantic import BaseModel, EmailStr

from models.baseModel import UserRole


class UserCreate(BaseModel):
    """🆕 Modèle pour l'inscription d'un utilisateur"""
    username: str
    email: EmailStr
    password: str
    role: UserRole  # Utilisation de l'enum UserRole pour garantir les valeurs valides

class TokenResponse(BaseModel):
    """🔐 Réponse contenant le token d'authentification"""
    access_token: str
    token_type: str
