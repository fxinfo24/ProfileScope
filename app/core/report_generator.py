"""
Report Generator
Generates professional HTML/PDF dossiers from intelligence data.
Uses Jinja2 for templating.
"""

import os
import json
import logging
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from typing import Dict, Any

logger = logging.getLogger(__name__)

class DossierReportGenerator:
    """Generates professional intelligence reports"""
    
    def __init__(self, template_dir: str = "app/web/templates/reports"):
        self.template_dir = template_dir
        # Ensure template dir exists
        os.makedirs(template_dir, exist_ok=True)
        
        self.env = Environment(
            loader=FileSystemLoader(os.path.dirname(os.path.abspath(__file__)) + "/../../web/templates")
        )
        
    def generate_html_report(self, report_data: Dict[str, Any]) -> str:
        """
        Generate a standalone HTML dossier.
        """
        try:
            # We'll use a string template if file doesn't exist to avoid dependency issues
            template = self._get_default_template()
            
            # Enrich data for display
            display_data = self._prepare_data_for_display(report_data)
            
            return template.render(data=display_data, generated_at=datetime.now().strftime("%Y-%m-%d %H:%M"))
            
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            return f"<h1>Error generating report</h1><p>{str(e)}</p>"

    def _prepare_data_for_display(self, data: Dict) -> Dict:
        """Format data for easier rendering"""
        # Ensure all sections exist
        return {
            "meta": data.get("meta", {}),
            "profile": data.get("profile_info", {}),
            "summary": data.get("executive_summary", "No summary available."),
            "psych": data.get("content_analysis", {}).get("psychological_profile", {}),
            "beliefs": data.get("belief_system", {}),
            "consumer": data.get("consumer_profile", {}),
            "auth": data.get("authenticity", {}),
            "raw": data
        }

    def _get_default_template(self):
        """Returns a Jinja2 Template object with default layout"""
        html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>VANTA Intelligence Dossier: {{ data.profile.username if data.profile and data.profile.username else 'Unknown Profile' }}</title>
    <style>
        :root { --primary: #0f172a; --accent: #3b82f6; --danger: #ef4444; --bg: #f8fafc; }
        body { font-family: 'Inter', system-ui, sans-serif; line-height: 1.6; color: #334155; max-width: 900px; margin: 0 auto; padding: 40px; background: var(--bg); }
        .header { border-bottom: 2px solid #e2e8f0; padding-bottom: 20px; margin-bottom: 40px; display: flex; justify-content: space-between; align-items: center; }
        .logo { font-weight: 900; font-size: 24px; color: var(--primary); letter-spacing: -1px; }
        .profile-card { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); display: flex; gap: 20px; margin-bottom: 30px; }
        .avatar { width: 100px; height: 100px; border-radius: 50%; object-fit: cover; background: #e2e8f0; }
        .stats { display: flex; gap: 20px; margin-top: 10px; font-size: 14px; color: #64748b; }
        
        .section { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 20px; }
        h1 { margin: 0; color: var(--primary); font-size: 24px; }
        h2 { color: var(--primary); font-size: 18px; border-left: 4px solid var(--accent); padding-left: 12px; margin-top: 0; }
        h3 { font-size: 16px; color: #475569; margin-bottom: 8px; }
        
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .tag { display: inline-block; padding: 4px 8px; background: #e0f2fe; color: #0369a1; border-radius: 4px; font-size: 12px; margin-right: 6px; margin-bottom: 6px; }
        .risk-high { color: var(--danger); font-weight: bold; }
        
        .bar-container { background: #f1f5f9; height: 8px; border-radius: 4px; overflow: hidden; margin-top: 6px; }
        .bar-fill { height: 100%; background: var(--accent); }
        
        .footer { margin-top: 60px; border-top: 1px solid #e2e8f0; padding-top: 20px; font-size: 12px; color: #94a3b8; text-align: center; }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">VANTA DOSSIER</div>
        <div style="text-align: right">
            <div><strong>Target:</strong> @{{ data.profile.username if data.profile and data.profile.username else 'Unknown' }}</div>
            <div style="font-size: 12px; color: #64748b">Generated: {{ generated_at }}</div>
        </div>
    </div>

    <!-- PROFILE OVERVIEW -->
    <div class="profile-card">
        {% if data.profile.profile_image_url %}
        <img src="{{ data.profile.profile_image_url }}" class="avatar" alt="Profile">
        {% else %}
        <div class="avatar"></div>
        {% endif %}
        <div>
            <h1>{{ data.profile.display_name if data.profile else 'Unknown' }} (@{{ data.profile.username if data.profile else 'unknown' }})</h1>
            <p>{{ data.profile.bio }}</p>
            <div class="stats">
                <span><strong>{{ data.profile.followers }}</strong> Followers</span>
                <span><strong>{{ data.profile.posts }}</strong> Posts</span>
                <span>Platform: {{ data.meta.platform }}</span>
            </div>
            {% if data.profile.is_verified %}
            <div style="margin-top: 8px; color: #059669; font-weight: bold; font-size: 12px;">✓ Verified Account</div>
            {% endif %}
        </div>
    </div>

    <!-- EXECUTIVE SUMMARY -->
    <div class="section" style="border-left: 4px solid #3b82f6;">
        <h2>Executive Summary</h2>
        <p style="font-size: 16px; line-height: 1.8;">{{ data.summary }}</p>
    </div>

    <div class="grid">
        <!-- BELIEF SYSTEM -->
        <div class="section">
            <h2>🌍 Worldview & Beliefs</h2>
            {% if data.beliefs and not data.beliefs.error %}
                <h3>Political Compass</h3>
                <div style="background: #f8fafc; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                    <div><strong>Alignment:</strong> {{ data.beliefs.get('POLITICAL COMPASS', {}).get('label', 'Unknown') }}</div>
                    <div style="font-size: 12px; margin-top: 4px;">
                        Economic: {{ data.beliefs.get('POLITICAL COMPASS', {}).get('economic_axis', 0) }} / 
                        Social: {{ data.beliefs.get('POLITICAL COMPASS', {}).get('social_axis', 0) }}
                    </div>
                </div>
                
                <h3>Core Values</h3>
                {% for key, val in data.beliefs.get('SOCIAL VALUES', {}).items() %}
                <div style="margin-bottom: 8px;">
                    <div style="display:flex; justify-content:space-between; font-size:12px;">
                        <span>{{ key|replace('_', ' ')|title }}</span>
                        <span>{{ val }}/10</span>
                    </div>
                    <div class="bar-container"><div class="bar-fill" style="width: {{ val * 10 }}%"></div></div>
                </div>
                {% endfor %}
            {% else %}
                <p>Insufficient data for belief analysis.</p>
            {% endif %}
        </div>

        <!-- CONSUMER PROFILE -->
        <div class="section">
            <h2>🛍️ Consumer Intelligence</h2>
            {% if data.consumer and not data.consumer.error %}
                <h3>Shopping Persona</h3>
                <div class="tag" style="background: #ecfdf5; color: #047857">{{ data.consumer.get('shopping_psychology', {}).get('buyer_persona', 'Unknown') }}</div>
                
                <h3>Brand Affinity</h3>
                <div style="margin-top: 10px;">
                {% for brand, affinity in data.consumer.get('brand_relationships', {}).get('brand_loyalty', {}).items() %}
                    <span class="tag">{{ brand }} ({{ affinity }})</span>
                {% endfor %}
                </div>

                <h3>Predicted Purchases (90 Days)</h3>
                <ul style="font-size: 13px; padding-left: 20px;">
                {% for item in data.consumer.get('forecast_90_day', {}).get('predicted_purchases', []) %}
                    <li>{{ item }}</li>
                {% endfor %}
                </ul>
            {% else %}
                <p>Insufficient data for consumer analysis.</p>
            {% endif %}
        </div>
    </div>

    <!-- PSYCHOLOGICAL PROFILE -->
    <div class="section">
        <h2>🧠 Psychological Profile</h2>
        {% if data.psych %}
        <div class="grid">
            <div>
                <h3>Big 5 Personality Traits</h3>
                {% for trait, score in data.psych.items() %}
                    {% if score is number %}
                    <div style="margin-bottom: 6px;">
                        <div style="display:flex; justify-content:space-between; font-size:12px;">
                            <span>{{ trait|title }}</span>
                            <span>{{ (score * 100)|round }}%</span>
                        </div>
                        <div class="bar-container"><div class="bar-fill" style="width: {{ score * 100 }}%"></div></div>
                    </div>
                    {% endif %}
                {% endfor %}
            </div>
            <div>
                <h3>Communication Style</h3>
                <p style="font-size: 13px;">{{ data.raw.content_analysis.get('communication_style', 'N/A') }}</p>
            </div>
        </div>
        {% else %}
        <p>Psychological analysis unavailable.</p>
        {% endif %}
    </div>

    <!-- AUTHENTICITY & RISK -->
    <div class="section">
        <h2>🛡️ Authenticity & Risk</h2>
        {% if data.auth %}
            <div style="display: flex; gap: 20px; align-items: center;">
                <div style="flex: 1;">
                    <h3>Risk Level</h3>
                    <div style="font-size: 24px; font-weight: bold; 
                        color: {{ '#ef4444' if data.auth.get('risk_assessment') in ['High', 'Critical', 'critical'] else '#eab308' if data.auth.get('risk_assessment') == 'Medium' else '#22c55e' }}">
                        {{ data.auth.get('risk_assessment', 'Unknown')|upper }}
                    </div>
                </div>
                <div style="flex: 1;">
                    <h3>Bot Likelihood</h3>
                    <div>{{ (data.auth.get('bot_likelihood', 0) * 100)|round }}%</div>
                </div>
                <div style="flex: 1;">
                    <h3>Authenticity Score</h3>
                    <div>{{ (data.auth.get('overall_authenticity', {}).get('score', 0) * 100)|round }}%</div>
                </div>
            </div>
        {% else %}
        <p>Authenticity check unavailable.</p>
        {% endif %}
    </div>

    <div class="footer">
        CONFIDENTIAL - Generated by VANTA Deep Intelligence Platform<br>
        For Official Use Only - {{ generated_at }}
    </div>
</body>
</html>
        """
        return self.env.from_string(html)
