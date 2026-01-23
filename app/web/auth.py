"""
Vanta Authentication System
JWT-based authentication with role-based access control
"""

import os
import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from .database import get_database_session
from .models.user import User, UserRole

# Load environment variables
load_dotenv()

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "Vanta2024SecureTokenKey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

class AuthenticationError(Exception):
    """Authentication related errors"""
    pass

class AuthorizationError(Exception):
    """Authorization related errors"""
    pass

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Dict[str, Any]:
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Token has expired")
    except jwt.JWTError:
        raise AuthenticationError("Invalid token")

def authenticate_user(email: str, password: str, db: Session) -> Optional[User]:
    """Authenticate a user with email and password"""
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        return None
        
    if not verify_password(password, user.hashed_password):
        return None
        
    if not user.is_active:
        return None
        
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    return user

def create_user(email: str, password: str, username: str = None, 
                first_name: str = None, last_name: str = None,
                db: Session = None) -> User:
    """Create a new user"""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise AuthenticationError("User with this email already exists")
    
    if username:
        existing_username = db.query(User).filter(User.username == username).first()
        if existing_username:
            raise AuthenticationError("Username already taken")
    
    # Create new user
    hashed_pw = hash_password(password)
    
    user = User(
        email=email,
        username=username,
        hashed_password=hashed_pw,
        first_name=first_name,
        last_name=last_name,
        role=UserRole.USER  # Default role
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user

def get_current_user(token: str, db: Session) -> User:
    """Get current user from JWT token"""
    try:
        payload = verify_token(token)
        user_id: int = payload.get("sub")
        
        if user_id is None:
            raise AuthenticationError("Invalid token payload")
            
    except AuthenticationError:
        raise
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise AuthenticationError("User not found")
        
    return user

def require_role(required_role: UserRole):
    """Decorator to require specific user role"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Extract user from kwargs (assumes user is passed)
            user = kwargs.get('current_user')
            if not user:
                raise AuthorizationError("Authentication required")
            
            # Check role hierarchy
            role_hierarchy = {
                UserRole.USER: 0,
                UserRole.PREMIUM: 1,
                UserRole.ENTERPRISE: 2,
                UserRole.ADMIN: 3
            }
            
            user_level = role_hierarchy.get(user.role, 0)
            required_level = role_hierarchy.get(required_role, 0)
            
            if user_level < required_level:
                raise AuthorizationError(f"Role {required_role.value} required")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def generate_api_key() -> str:
    """Generate a new API key"""
    import secrets
    return f"psk_{secrets.token_urlsafe(32)}"

def create_user_with_api_key(email: str, password: str, db: Session) -> tuple[User, str]:
    """Create user and generate API key"""
    user = create_user(email, password, db=db)
    api_key = generate_api_key()
    
    user.api_key = api_key
    db.commit()
    
    return user, api_key

def authenticate_api_key(api_key: str, db: Session) -> Optional[User]:
    """Authenticate using API key"""
    user = db.query(User).filter(User.api_key == api_key).first()
    
    if not user or not user.is_active:
        return None
        
    return user