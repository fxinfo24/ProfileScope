"""
API Monetization Platform for ProfileScope
Usage-based pricing and billing system
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import enum

from ..web.database import Base

class PricingTier(enum.Enum):
    FREE = "free"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"

class BillingCycle(enum.Enum):
    MONTHLY = "monthly"
    ANNUAL = "annual"
    PAY_PER_USE = "pay_per_use"

class ApiEndpoint(Base):
    __tablename__ = "api_endpoints"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Endpoint details
    endpoint_name = Column(String(100), nullable=False)
    endpoint_path = Column(String(255), nullable=False)
    method = Column(String(10), default="POST")
    
    # Pricing
    base_cost_per_request = Column(Float, default=0.01)  # Base cost in USD
    tier_multipliers = Column(JSON, nullable=True)  # Different costs per tier
    
    # Rate limiting
    rate_limit_per_minute = Column(Integer, default=60)
    rate_limit_per_hour = Column(Integer, default=1000)
    rate_limit_per_day = Column(Integer, default=10000)
    
    # Features
    requires_authentication = Column(Boolean, default=True)
    complexity_factor = Column(Float, default=1.0)  # Multiplier for complex operations
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Plan details
    name = Column(String(100), nullable=False)
    tier = Column(String(20), nullable=False)  # free, basic, professional, enterprise
    description = Column(Text, nullable=True)
    
    # Pricing
    monthly_price = Column(Float, default=0.0)
    annual_price = Column(Float, default=0.0)
    setup_fee = Column(Float, default=0.0)
    
    # Limits
    requests_per_month = Column(Integer, default=1000)
    analyses_per_month = Column(Integer, default=100)
    team_members = Column(Integer, default=1)
    data_retention_days = Column(Integer, default=30)
    
    # Features (JSON boolean flags)
    features = Column(JSON, nullable=True)
    
    # API cost overrides
    custom_pricing = Column(JSON, nullable=True)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())

class UserSubscription(Base):
    __tablename__ = "user_subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("subscription_plans.id"), nullable=False)
    
    # Subscription details
    status = Column(String(20), default="active")  # active, cancelled, expired, past_due
    billing_cycle = Column(String(20), default="monthly")
    
    # Billing
    current_period_start = Column(DateTime, nullable=False)
    current_period_end = Column(DateTime, nullable=False)
    next_billing_date = Column(DateTime, nullable=True)
    
    # Usage tracking
    requests_used_this_month = Column(Integer, default=0)
    analyses_used_this_month = Column(Integer, default=0)
    last_usage_reset = Column(DateTime, default=func.now())
    
    # Payment
    stripe_subscription_id = Column(String(100), nullable=True)
    last_payment_date = Column(DateTime, nullable=True)
    last_payment_amount = Column(Float, nullable=True)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
    plan = relationship("SubscriptionPlan")

class ApiUsage(Base):
    __tablename__ = "api_usage"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    endpoint_id = Column(Integer, ForeignKey("api_endpoints.id"), nullable=False)
    
    # Request details
    request_timestamp = Column(DateTime, default=func.now())
    response_status = Column(Integer, nullable=False)  # HTTP status code
    processing_time_ms = Column(Integer, nullable=True)
    
    # Billing details
    cost_incurred = Column(Float, default=0.0)
    complexity_multiplier = Column(Float, default=1.0)
    
    # Request metadata
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    request_size_bytes = Column(Integer, nullable=True)
    response_size_bytes = Column(Integer, nullable=True)
    
    # Relationships
    user = relationship("User")
    endpoint = relationship("ApiEndpoint")

class Invoice(Base):
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Invoice details
    invoice_number = Column(String(50), unique=True, nullable=False)
    status = Column(String(20), default="pending")  # pending, paid, overdue, cancelled
    
    # Amounts
    subtotal = Column(Float, nullable=False)
    tax_amount = Column(Float, default=0.0)
    total_amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    
    # Billing period
    billing_period_start = Column(DateTime, nullable=False)
    billing_period_end = Column(DateTime, nullable=False)
    
    # Payment
    due_date = Column(DateTime, nullable=False)
    paid_date = Column(DateTime, nullable=True)
    payment_method = Column(String(50), nullable=True)
    stripe_payment_intent_id = Column(String(100), nullable=True)
    
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    user = relationship("User")

class InvoiceLineItem(Base):
    __tablename__ = "invoice_line_items"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    
    description = Column(String(255), nullable=False)
    quantity = Column(Integer, default=1)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    
    # For API usage items
    endpoint_id = Column(Integer, ForeignKey("api_endpoints.id"), nullable=True)
    usage_count = Column(Integer, nullable=True)
    
    # Relationships
    invoice = relationship("Invoice")
    endpoint = relationship("ApiEndpoint")

class MonetizationService:
    """Service for handling API monetization and billing"""
    
    @staticmethod
    def get_pricing_tiers() -> Dict[str, Dict[str, Any]]:
        """Get available pricing tiers"""
        return {
            "free": {
                "name": "Free",
                "price": 0,
                "requests_per_month": 1000,
                "analyses_per_month": 10,
                "features": ["basic_analysis", "profile_data"],
                "support": "community"
            },
            "basic": {
                "name": "Basic",
                "price": 29,
                "requests_per_month": 10000,
                "analyses_per_month": 100,
                "features": ["basic_analysis", "profile_data", "image_analysis", "basic_api"],
                "support": "email"
            },
            "professional": {
                "name": "Professional", 
                "price": 99,
                "requests_per_month": 50000,
                "analyses_per_month": 500,
                "features": ["all_analysis", "bulk_processing", "advanced_api", "webhooks"],
                "support": "priority"
            },
            "enterprise": {
                "name": "Enterprise",
                "price": 299,
                "requests_per_month": 200000,
                "analyses_per_month": 2000,
                "features": ["unlimited_features", "white_label", "custom_integration", "sla"],
                "support": "dedicated"
            }
        }
    
    @staticmethod
    def calculate_usage_cost(user_id: int, endpoint_name: str, complexity: float = 1.0) -> float:
        """Calculate cost for API usage"""
        from ..web.database import SessionLocal
        
        session = SessionLocal()
        try:
            # Get user's subscription
            subscription = session.query(UserSubscription).join(SubscriptionPlan).filter(
                UserSubscription.user_id == user_id,
                UserSubscription.status == "active"
            ).first()
            
            if not subscription:
                return 0.01  # Default cost for free tier
            
            # Get endpoint pricing
            endpoint = session.query(ApiEndpoint).filter_by(endpoint_name=endpoint_name).first()
            if not endpoint:
                return 0.01
            
            base_cost = endpoint.base_cost_per_request
            
            # Apply tier multiplier
            if subscription.plan.custom_pricing:
                tier_multiplier = subscription.plan.custom_pricing.get(endpoint_name, 1.0)
            else:
                tier_multipliers = {
                    "free": 1.0,
                    "basic": 0.8,
                    "professional": 0.6,
                    "enterprise": 0.4
                }
                tier_multiplier = tier_multipliers.get(subscription.plan.tier, 1.0)
            
            final_cost = base_cost * tier_multiplier * complexity
            return round(final_cost, 4)
            
        finally:
            session.close()
    
    @staticmethod
    def record_api_usage(user_id: int, endpoint_name: str, status_code: int, 
                        processing_time: int = None, complexity: float = 1.0) -> float:
        """Record API usage and calculate cost"""
        from ..web.database import SessionLocal
        
        session = SessionLocal()
        try:
            # Get endpoint
            endpoint = session.query(ApiEndpoint).filter_by(endpoint_name=endpoint_name).first()
            if not endpoint:
                # Create endpoint if it doesn't exist
                endpoint = ApiEndpoint(
                    endpoint_name=endpoint_name,
                    endpoint_path=f"/api/{endpoint_name.lower()}"
                )
                session.add(endpoint)
                session.flush()
            
            # Calculate cost
            cost = MonetizationService.calculate_usage_cost(user_id, endpoint_name, complexity)
            
            # Record usage
            usage = ApiUsage(
                user_id=user_id,
                endpoint_id=endpoint.id,
                response_status=status_code,
                processing_time_ms=processing_time,
                cost_incurred=cost,
                complexity_multiplier=complexity
            )
            session.add(usage)
            
            # Update user's monthly usage
            subscription = session.query(UserSubscription).filter_by(
                user_id=user_id, status="active"
            ).first()
            
            if subscription:
                subscription.requests_used_this_month += 1
                
                # Reset monthly usage if new period
                if subscription.last_usage_reset.month != datetime.utcnow().month:
                    subscription.requests_used_this_month = 1
                    subscription.last_usage_reset = datetime.utcnow()
            
            session.commit()
            return cost
            
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    @staticmethod
    def generate_invoice(user_id: int, billing_period_start: datetime, 
                        billing_period_end: datetime) -> str:
        """Generate invoice for billing period"""
        from ..web.database import SessionLocal
        import uuid
        
        session = SessionLocal()
        try:
            # Get usage for billing period
            usage_records = session.query(ApiUsage).filter(
                ApiUsage.user_id == user_id,
                ApiUsage.request_timestamp >= billing_period_start,
                ApiUsage.request_timestamp <= billing_period_end
            ).all()
            
            if not usage_records:
                return None
            
            # Calculate totals
            subtotal = sum(usage.cost_incurred for usage in usage_records)
            tax_rate = 0.08  # 8% tax (would be configurable)
            tax_amount = subtotal * tax_rate
            total_amount = subtotal + tax_amount
            
            # Generate invoice number
            invoice_number = f"INV-{datetime.utcnow().strftime('%Y%m')}-{str(uuid.uuid4())[:8].upper()}"
            
            # Create invoice
            invoice = Invoice(
                user_id=user_id,
                invoice_number=invoice_number,
                subtotal=subtotal,
                tax_amount=tax_amount,
                total_amount=total_amount,
                billing_period_start=billing_period_start,
                billing_period_end=billing_period_end,
                due_date=datetime.utcnow() + timedelta(days=30)
            )
            session.add(invoice)
            session.flush()
            
            # Create line items grouped by endpoint
            endpoint_usage = {}
            for usage in usage_records:
                endpoint_name = usage.endpoint.endpoint_name
                if endpoint_name not in endpoint_usage:
                    endpoint_usage[endpoint_name] = {
                        "count": 0,
                        "total_cost": 0.0,
                        "endpoint_id": usage.endpoint_id
                    }
                endpoint_usage[endpoint_name]["count"] += 1
                endpoint_usage[endpoint_name]["total_cost"] += usage.cost_incurred
            
            for endpoint_name, data in endpoint_usage.items():
                line_item = InvoiceLineItem(
                    invoice_id=invoice.id,
                    description=f"API Usage - {endpoint_name}",
                    quantity=data["count"],
                    unit_price=data["total_cost"] / data["count"],
                    total_price=data["total_cost"],
                    endpoint_id=data["endpoint_id"],
                    usage_count=data["count"]
                )
                session.add(line_item)
            
            session.commit()
            return invoice_number
            
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    @staticmethod
    def get_usage_analytics(user_id: int, days: int = 30) -> Dict[str, Any]:
        """Get usage analytics for user"""
        from ..web.database import SessionLocal
        from sqlalchemy import func
        
        session = SessionLocal()
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Get usage statistics
            usage_stats = session.query(
                ApiEndpoint.endpoint_name,
                func.count(ApiUsage.id).label('request_count'),
                func.sum(ApiUsage.cost_incurred).label('total_cost'),
                func.avg(ApiUsage.processing_time_ms).label('avg_response_time')
            ).join(
                ApiUsage, ApiEndpoint.id == ApiUsage.endpoint_id
            ).filter(
                ApiUsage.user_id == user_id,
                ApiUsage.request_timestamp >= start_date
            ).group_by(ApiEndpoint.endpoint_name).all()
            
            # Calculate daily usage
            daily_usage = session.query(
                func.date(ApiUsage.request_timestamp).label('date'),
                func.count(ApiUsage.id).label('request_count'),
                func.sum(ApiUsage.cost_incurred).label('daily_cost')
            ).filter(
                ApiUsage.user_id == user_id,
                ApiUsage.request_timestamp >= start_date
            ).group_by(func.date(ApiUsage.request_timestamp)).all()
            
            return {
                "period_days": days,
                "endpoint_stats": [
                    {
                        "endpoint": stat.endpoint_name,
                        "requests": stat.request_count,
                        "total_cost": float(stat.total_cost or 0),
                        "avg_response_time": float(stat.avg_response_time or 0)
                    }
                    for stat in usage_stats
                ],
                "daily_usage": [
                    {
                        "date": daily.date.isoformat(),
                        "requests": daily.request_count,
                        "cost": float(daily.daily_cost or 0)
                    }
                    for daily in daily_usage
                ],
                "total_requests": sum(stat.request_count for stat in usage_stats),
                "total_cost": sum(float(stat.total_cost or 0) for stat in usage_stats)
            }
            
        finally:
            session.close()