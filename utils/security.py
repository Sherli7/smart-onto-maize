import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from psycopg2.extras import RealDictCursor


from database.database import get_db_connection

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__ident="2b"  # ✅ Force l'utilisation de bcrypt version 2b
)



# ✅ Logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ✅ Clé secrète pour signer le token JWT (⚠️ Changez-la en production et utilisez une variable d'env)
SECRET_KEY = os.getenv("SECRET_KEY", "votre_secret_key_super_securisee")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ✅ OAuth2PasswordBearer définit le chemin de connexion pour récupérer le token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# =========================================
# 🔐 GESTION DES MOTS DE PASSE
# =========================================
def get_password_hash(password: str) -> str:
    """Hache un mot de passe avec bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie si un mot de passe en clair correspond à un mot de passe haché."""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"❌ Erreur bcrypt lors de la vérification du mot de passe: {e}")
        return False

# =========================================
# 🔐 CRÉATION ET VÉRIFICATION DU TOKEN JWT
# =========================================
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Crée un token JWT pour authentifier un utilisateur."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Décode et valide un token JWT."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


# =========================================
# 🔑 RÉCUPÉRATION DE L'UTILISATEUR CONNECTÉ
# =========================================
def get_current_user(token: str = Depends(oauth2_scheme)):
    """🔑 Récupère l'utilisateur actuel à partir du token JWT."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Impossible de valider les informations d'identification",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # ✅ Décodage du token
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception

    # ✅ Connexion à la base de données pour récupérer l'utilisateur
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Erreur de connexion à la base de données")

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT id, username, email, role FROM users WHERE username = %s", (username,))
            user = cur.fetchone()

        if user is None:
            raise credentials_exception

        return user

    except Exception as e:
        logger.error(f"❌ Erreur lors de la récupération de l'utilisateur: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

    finally:
        conn.close()
