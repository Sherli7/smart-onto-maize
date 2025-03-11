import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import validate_email
from starlette.responses import JSONResponse

from models.baseModel import UserRole
from models.userModel import get_user_by_email, register_user
from utils.security import get_password_hash, verify_password, create_access_token, get_current_user
from schema.userSchema import UserCreate

logger = logging.getLogger(__name__)
router = APIRouter(prefix="", tags=["Authentification"])

# ✅ Définition des rôles autorisés
VALID_ROLES = {"admin", "farmer", "other"}

@router.post("/register")
async def register(request: Request, user: UserCreate):
    """Créer un nouvel utilisateur."""
    ip_address = request.client.host
    logger.info(f"📩 [REQ] Inscription - IP: {ip_address} - Email: {user.email}")

    # ✅ Vérifier le rôle
    if user.role not in UserRole.__members__.values():
        logger.warning(f"❌ Tentative d'inscription avec rôle invalide : {user.role}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rôle invalide. Choisissez parmi: admin, farmer, other."
        )

    # ✅ Valider l'email
    validate_email(str(user.email))

    # ✅ Vérifier si l'utilisateur existe déjà
    existing_user = get_user_by_email(str(user.email))
    if existing_user:
        logger.warning(f"⚠️ Échec inscription : Email déjà utilisé - {user.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nom d'utilisateur ou email déjà utilisé"
        )

    try:
        # ✅ Hacher le mot de passe
        hashed_password = get_password_hash(user.password)
        logger.debug(f"🔑 Mot de passe haché généré : {hashed_password}")

        # ✅ Enregistrer l'utilisateur dans la base de données
        user_id = register_user(user.username, str(user.email), hashed_password, user.role)
        logger.info(f"✅ [RES] Inscription réussie : {user.email}")

        return {
            "id": user_id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        }

    except Exception as e:
        logger.error(f"❌ [ERROR] Erreur lors de l'inscription : {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne du serveur"
        )

@router.post("/login")
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    """🔐 Authentifier un utilisateur et retourner un token JWT."""
    ip_address = request.client.host
    logger.info(f"🔑 Tentative de connexion depuis {ip_address} - Email: {form_data.username}")

    try:
        # ✅ Récupérer l'utilisateur par email
        db_user = get_user_by_email(form_data.username)
        if not db_user:
            logger.warning(f"⚠️ Connexion échouée : Utilisateur non trouvé - Email: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email ou mot de passe incorrect"
            )

        logger.debug(f"🔎 Utilisateur trouvé: {db_user}")

        # ✅ Vérifier le mot de passe
        try:
            if not verify_password(form_data.password, db_user["password_hash"]):
                logger.warning(f"⚠️ Connexion échouée : Mot de passe incorrect - Email: {form_data.username}")
                logger.debug(f"🛠️ Mot de passe en clair: {form_data.password} - Hash attendu: {db_user['password_hash']}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email ou mot de passe incorrect"
                )
        except Exception as bcrypt_error:
            logger.error(f"❌ Erreur bcrypt lors de la vérification du mot de passe : {bcrypt_error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erreur de validation du mot de passe"
            )

        # ✅ Générer un token JWT
        access_token = create_access_token(data={"sub": db_user["username"], "role": db_user["role"]})
        logger.info(f"✅ Connexion réussie pour {db_user['email']} depuis {ip_address}")

        # ✅ Retourner la réponse
        return JSONResponse(content={
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": db_user["id"]
        })

    except HTTPException:
        # Relancer les exceptions HTTP déjà gérées
        raise
    except Exception as e:
        # Journaliser les erreurs inattendues
        logger.error(f"❌ [ERROR] Erreur lors de l'authentification : {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne du serveur"
        )

@router.get("/users/me")
def get_me(current_user: dict = Depends(get_current_user)):
    """Récupérer les informations de l'utilisateur actuellement authentifié."""
    return current_user
