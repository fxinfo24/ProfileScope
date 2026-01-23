"""
White-label and Customization Features for Vanta
Custom branding and domain management for enterprise clients
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from typing import Dict, Any, Optional
import json

from ..web.database import Base

class WhitelabelConfig(Base):
    __tablename__ = "whitelabel_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    
    # Domain and branding
    custom_domain = Column(String(255), nullable=True)
    domain_verified = Column(Boolean, default=False)
    
    # Visual branding
    company_name = Column(String(100), nullable=False)
    logo_url = Column(String(500), nullable=True)
    favicon_url = Column(String(500), nullable=True)
    primary_color = Column(String(7), default="#3B82F6")  # Hex color
    secondary_color = Column(String(7), default="#1E3A8A")
    
    # Email branding
    email_header_image = Column(String(500), nullable=True)
    email_footer_text = Column(Text, nullable=True)
    support_email = Column(String(255), nullable=True)
    
    # Custom styling
    custom_css = Column(Text, nullable=True)
    custom_javascript = Column(Text, nullable=True)
    
    # Features configuration
    features_config = Column(JSON, nullable=True)  # JSON config for enabled features
    
    # Terms and privacy
    terms_url = Column(String(500), nullable=True)
    privacy_url = Column(String(500), nullable=True)
    
    # API customization
    api_documentation_url = Column(String(500), nullable=True)
    webhook_endpoint = Column(String(500), nullable=True)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    team = relationship("Team")
    
    def __repr__(self):
        return f"<WhitelabelConfig(team_id={self.team_id}, company={self.company_name})>"
    
    def get_branding_config(self) -> Dict[str, Any]:
        """Get complete branding configuration"""
        return {
            "company_name": self.company_name,
            "logo_url": self.logo_url,
            "favicon_url": self.favicon_url,
            "colors": {
                "primary": self.primary_color,
                "secondary": self.secondary_color
            },
            "domain": self.custom_domain,
            "features": self.features_config or {},
            "support_email": self.support_email,
            "legal": {
                "terms_url": self.terms_url,
                "privacy_url": self.privacy_url
            }
        }

class CustomDomain(Base):
    __tablename__ = "custom_domains"
    
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    
    domain = Column(String(255), unique=True, nullable=False)
    subdomain = Column(String(100), nullable=True)  # e.g., 'analytics' for analytics.company.com
    
    # DNS verification
    verification_token = Column(String(64), nullable=False)
    dns_verified = Column(Boolean, default=False)
    ssl_certificate_issued = Column(Boolean, default=False)
    
    # Status
    is_active = Column(Boolean, default=False)
    last_verified = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class BrandingAsset(Base):
    __tablename__ = "branding_assets"
    
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    
    asset_type = Column(String(50), nullable=False)  # logo, favicon, banner, etc.
    file_name = Column(String(255), nullable=False)
    file_url = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=True)  # in bytes
    mime_type = Column(String(100), nullable=True)
    
    # Dimensions for images
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    
    # Usage tracking
    usage_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=func.now())

class WhitelabelService:
    """Service for managing white-label configurations"""
    
    @staticmethod
    def create_whitelabel_config(team_id: int, company_name: str, 
                                primary_color: str = "#3B82F6") -> WhitelabelConfig:
        """Create white-label configuration for a team"""
        from ..web.database import SessionLocal
        
        session = SessionLocal()
        try:
            config = WhitelabelConfig(
                team_id=team_id,
                company_name=company_name,
                primary_color=primary_color,
                features_config={
                    "analytics_dashboard": True,
                    "api_access": True,
                    "custom_reports": True,
                    "team_collaboration": True,
                    "data_export": True,
                    "webhook_integration": True
                }
            )
            session.add(config)
            session.commit()
            return config
            
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    @staticmethod
    def setup_custom_domain(team_id: int, domain: str, subdomain: str = None) -> str:
        """Set up custom domain for white-label installation"""
        import secrets
        from ..web.database import SessionLocal
        
        verification_token = secrets.token_urlsafe(32)
        
        session = SessionLocal()
        try:
            custom_domain = CustomDomain(
                team_id=team_id,
                domain=domain,
                subdomain=subdomain,
                verification_token=verification_token
            )
            session.add(custom_domain)
            session.commit()
            
            return verification_token
            
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    @staticmethod
    def verify_domain(domain: str) -> bool:
        """Verify domain ownership via DNS"""
        import dns.resolver
        from ..web.database import SessionLocal
        
        session = SessionLocal()
        try:
            custom_domain = session.query(CustomDomain).filter_by(domain=domain).first()
            if not custom_domain:
                return False
            
            # Check for TXT record with verification token
            try:
                answers = dns.resolver.resolve(f"_vanta-verify.{domain}", "TXT")
                for answer in answers:
                    if custom_domain.verification_token in str(answer):
                        custom_domain.dns_verified = True
                        custom_domain.last_verified = func.now()
                        session.commit()
                        return True
            except dns.resolver.NXDOMAIN:
                pass
            
            return False
            
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    @staticmethod
    def get_whitelabel_config(team_id: int) -> Optional[Dict[str, Any]]:
        """Get white-label configuration for team"""
        from ..web.database import SessionLocal
        
        session = SessionLocal()
        try:
            config = session.query(WhitelabelConfig).filter_by(team_id=team_id).first()
            return config.get_branding_config() if config else None
        finally:
            session.close()
    
    @staticmethod
    def generate_custom_css(config: WhitelabelConfig) -> str:
        """Generate custom CSS based on branding configuration"""
        css_template = f"""
        /* Custom Vanta Branding */
        :root {{
            --primary-color: {config.primary_color};
            --secondary-color: {config.secondary_color};
        }}
        
        .navbar-brand {{
            background-image: url('{config.logo_url}');
            background-size: contain;
            background-repeat: no-repeat;
        }}
        
        .btn-primary {{
            background-color: var(--primary-color);
            border-color: var(--primary-color);
        }}
        
        .text-primary {{
            color: var(--primary-color) !important;
        }}
        
        .bg-primary {{
            background-color: var(--primary-color) !important;
        }}
        
        {config.custom_css or ''}
        """
        
        return css_template.strip()
    
    @staticmethod
    def generate_email_template(config: WhitelabelConfig, content: str, 
                               subject: str = "") -> str:
        """Generate branded email template"""
        template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>{subject}</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                .header {{ background-color: {config.primary_color}; padding: 20px; text-align: center; }}
                .header img {{ max-height: 60px; }}
                .content {{ padding: 20px; }}
                .footer {{ background-color: #f8f9fa; padding: 15px; text-align: center; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="header">
                {f'<img src="{config.email_header_image}" alt="{config.company_name}">' if config.email_header_image else f'<h2 style="color: white;">{config.company_name}</h2>'}
            </div>
            <div class="content">
                {content}
            </div>
            <div class="footer">
                {config.email_footer_text or f'© {config.company_name}. All rights reserved.'}
                {f'<br>Support: <a href="mailto:{config.support_email}">{config.support_email}</a>' if config.support_email else ''}
            </div>
        </body>
        </html>
        """
        
        return template.strip()