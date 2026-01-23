"""
Enterprise Team Management for Vanta
Multi-user collaboration and team features
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
from typing import List, Dict, Any, Optional

from ..web.database import Base
from ..web.models.user import User

class TeamRole(enum.Enum):
    OWNER = "owner"
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"

class TeamPermission(enum.Enum):
    CREATE_ANALYSIS = "create_analysis"
    DELETE_ANALYSIS = "delete_analysis"
    SHARE_ANALYSIS = "share_analysis"
    EXPORT_DATA = "export_data"
    MANAGE_TEAM = "manage_team"
    VIEW_BILLING = "view_billing"
    MANAGE_INTEGRATIONS = "manage_integrations"

class Team(Base):
    __tablename__ = "teams"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # Subscription and billing
    subscription_tier = Column(String(50), default="enterprise")
    max_members = Column(Integer, default=50)
    max_analyses_per_month = Column(Integer, default=1000)
    
    # Customization
    custom_domain = Column(String(255), nullable=True)
    custom_logo_url = Column(String(500), nullable=True)
    custom_branding = Column(Boolean, default=False)
    
    # Settings
    default_permissions = Column(String(500), default="create_analysis,share_analysis,export_data")
    require_approval = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    members = relationship("TeamMember", back_populates="team")
    analyses = relationship("TeamAnalysis", back_populates="team")
    
    def __repr__(self):
        return f"<Team(id={self.id}, name={self.name})>"
    
    def get_member_count(self) -> int:
        return len(self.members)
    
    def can_add_member(self) -> bool:
        return self.get_member_count() < self.max_members
    
    def get_monthly_analysis_count(self) -> int:
        # This would query analyses for current month
        return len(self.analyses)  # Simplified
    
    def can_create_analysis(self) -> bool:
        return self.get_monthly_analysis_count() < self.max_analyses_per_month

class TeamMember(Base):
    __tablename__ = "team_members"
    
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    role = Column(Enum(TeamRole), nullable=False)
    permissions = Column(String(500), nullable=True)  # JSON string of permissions
    
    # Status
    is_active = Column(Boolean, default=True)
    invited_at = Column(DateTime, default=func.now())
    joined_at = Column(DateTime, nullable=True)
    
    # Relationships
    team = relationship("Team", back_populates="members")
    user = relationship("User")
    
    def __repr__(self):
        return f"<TeamMember(team_id={self.team_id}, user_id={self.user_id}, role={self.role})>"
    
    def has_permission(self, permission: TeamPermission) -> bool:
        """Check if member has specific permission"""
        if self.role == TeamRole.OWNER:
            return True
        
        if self.role == TeamRole.ADMIN and permission != TeamPermission.MANAGE_TEAM:
            return True
        
        if self.permissions:
            return permission.value in self.permissions
        
        # Default permissions
        default_perms = self.team.default_permissions.split(",")
        return permission.value in default_perms

class TeamAnalysis(Base):
    __tablename__ = "team_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=False)
    
    # Sharing settings
    shared_with_team = Column(Boolean, default=True)
    shared_externally = Column(Boolean, default=False)
    external_share_token = Column(String(64), nullable=True)
    
    # Collaboration
    tags = Column(String(500), nullable=True)  # Comma-separated tags
    notes = Column(Text, nullable=True)
    
    # Access control
    viewers_only = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    team = relationship("Team", back_populates="analyses")
    analysis = relationship("Analysis")

class TeamInvitation(Base):
    __tablename__ = "team_invitations"
    
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    email = Column(String(255), nullable=False)
    role = Column(Enum(TeamRole), nullable=False)
    
    token = Column(String(64), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    
    invited_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    accepted_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=func.now())

class TeamService:
    """Service class for team management operations"""
    
    @staticmethod
    def create_team(name: str, description: str, owner_id: int) -> Team:
        """Create a new team"""
        from ..web.database import SessionLocal
        
        session = SessionLocal()
        try:
            team = Team(name=name, description=description)
            session.add(team)
            session.flush()  # Get team ID
            
            # Add owner as team member
            owner_member = TeamMember(
                team_id=team.id,
                user_id=owner_id,
                role=TeamRole.OWNER,
                joined_at=datetime.utcnow()
            )
            session.add(owner_member)
            session.commit()
            
            return team
            
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    @staticmethod
    def invite_member(team_id: int, email: str, role: TeamRole, invited_by: int) -> str:
        """Invite a new team member"""
        import secrets
        from datetime import timedelta
        
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(days=7)
        
        from ..web.database import SessionLocal
        session = SessionLocal()
        
        try:
            invitation = TeamInvitation(
                team_id=team_id,
                email=email,
                role=role,
                token=token,
                expires_at=expires_at,
                invited_by=invited_by
            )
            session.add(invitation)
            session.commit()
            
            return token
            
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    @staticmethod
    def accept_invitation(token: str, user_id: int) -> bool:
        """Accept team invitation"""
        from ..web.database import SessionLocal
        session = SessionLocal()
        
        try:
            invitation = session.query(TeamInvitation).filter_by(token=token).first()
            
            if not invitation or invitation.expires_at < datetime.utcnow():
                return False
            
            # Create team member
            member = TeamMember(
                team_id=invitation.team_id,
                user_id=user_id,
                role=invitation.role,
                joined_at=datetime.utcnow()
            )
            session.add(member)
            
            # Mark invitation as accepted
            invitation.accepted_at = datetime.utcnow()
            session.commit()
            
            return True
            
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    @staticmethod
    def get_team_analytics(team_id: int) -> Dict[str, Any]:
        """Get team analytics and usage statistics"""
        from ..web.database import SessionLocal
        session = SessionLocal()
        
        try:
            team = session.query(Team).filter_by(id=team_id).first()
            if not team:
                return {}
            
            # Calculate statistics
            member_count = len(team.members)
            active_members = len([m for m in team.members if m.is_active])
            total_analyses = len(team.analyses)
            
            return {
                "team_name": team.name,
                "member_count": member_count,
                "active_members": active_members,
                "total_analyses": total_analyses,
                "monthly_limit": team.max_analyses_per_month,
                "usage_percentage": (total_analyses / team.max_analyses_per_month) * 100,
                "created_at": team.created_at.isoformat()
            }
            
        finally:
            session.close()