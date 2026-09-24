from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash


class AuthenticationService:

    SECRET_KEY = "8vKx3mQ7pL2nZ9rT5wY1sA6dF4hJ0cU8eG3bN7xP9qR2"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

    password_hash = PasswordHash.recommended()

    # --------------------------------------------------
    # Password
    # --------------------------------------------------

    @classmethod
    def hash_password(cls, password: str) -> str:
        """
        Convert plain password into secure password hash.
        """
        return cls.password_hash.hash(password)

    @classmethod
    def verify_password(
            cls,
            plain_password: str,
            hashed_password: str
        ) -> bool:
            """
            Verify plain password against stored hash.
            Returns False (instead of raising) if the stored value
            isn't a valid/recognized hash — e.g. empty, corrupted, or
            accidentally stored as plain text.
            """
            if not plain_password or not hashed_password:
                return False
    
            try:
                return cls.password_hash.verify(
                    plain_password,
                    hashed_password
                )
            except Exception:
                return False

    # --------------------------------------------------
    # JWT
    # --------------------------------------------------

    @classmethod
    def create_access_token(
        cls,
        user_id: int,
        role: str
    ) -> str:

        expire = (
            datetime.now(timezone.utc)
            + timedelta(
                minutes=cls.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        )

        payload = {
            "sub": str(user_id),
            "role": role,
            "exp": expire
        }

        return jwt.encode(
            payload,
            cls.SECRET_KEY,
            algorithm=cls.ALGORITHM
        )

    @classmethod
    def decode_access_token(
        cls,
        token: str
    ) -> Optional[dict]:

        try:

            payload = jwt.decode(
                token,
                cls.SECRET_KEY,
                algorithms=[cls.ALGORITHM]
            )

            user_id = payload.get("sub")
            role = payload.get("role")

            if user_id is None or role is None:
                return None

            return payload

        except InvalidTokenError:
            return None

    # --------------------------------------------------
    # Authentication
    # --------------------------------------------------

    @classmethod
    def authenticate_user(
        cls,
        password: str,
        stored_password: str
    ) -> bool:

        return cls.verify_password(
            password,
            stored_password
        )

    # --------------------------------------------------
    # Create login response
    # --------------------------------------------------

    @classmethod
    def create_login_response(
        cls,
        user_id: int,
        role: str
    ) -> dict:

        access_token = cls.create_access_token(
            user_id=user_id,
            role=role
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user_id,
            "role": role
        }
