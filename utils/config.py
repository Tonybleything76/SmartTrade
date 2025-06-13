"""
Configuration management for the Multi-Agent Content System
Handles environment variables, settings, and system configuration
"""

import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class APIConfig:
    """API configuration settings"""
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    linkedin_access_token: str = field(default_factory=lambda: os.getenv("LINKEDIN_ACCESS_TOKEN", ""))
    x_api_key: str = field(default_factory=lambda: os.getenv("X_API_KEY", ""))
    x_access_token: str = field(default_factory=lambda: os.getenv("X_ACCESS_TOKEN", ""))
    x_api_secret: str = field(default_factory=lambda: os.getenv("X_API_SECRET", ""))
    x_access_token_secret: str = field(default_factory=lambda: os.getenv("X_ACCESS_TOKEN_SECRET", ""))

@dataclass
class ContentConfig:
    """Content generation configuration"""
    daily_post_count: int = 3
    posting_times: List[str] = field(default_factory=lambda: ["09:00", "12:00", "17:00"])
    max_content_length: int = 1300
    min_content_length: int = 100
    hashtag_count_range: tuple = (3, 8)
    
    # Topic categories for content generation
    topic_pillars: List[str] = field(default_factory=lambda: [
        "AI Innovation",
        "Generative AI",
        "Technology Roadmaps & Integration",
        "AI for Professionals",
        "Agentic Systems"
    ])
    
    # Content quality thresholds
    min_approval_score: float = 3.5
    max_retry_attempts: int = 3
    
    # Brand voice settings
    brand_voice: str = "authoritative yet approachable AI expert"
    brand_tone: List[str] = field(default_factory=lambda: [
        "professional", "insightful", "practical", "forward-thinking"
    ])

@dataclass
class ScrapingConfig:
    """Web scraping configuration"""
    request_timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    user_agent: str = "MultiAgentContentBot/1.0 (AI Content Research)"
    
    # Research sources
    ai_news_sources: List[str] = field(default_factory=lambda: [
        "https://venturebeat.com/ai/",
        "https://techcrunch.com/category/artificial-intelligence/",
        "https://www.artificialintelligence-news.com/",
        "https://aimagazine.com/",
        "https://www.theverge.com/ai-artificial-intelligence"
    ])
    
    academic_sources: List[str] = field(default_factory=lambda: [
        "https://arxiv.org/list/cs.AI/recent",
        "https://arxiv.org/list/cs.LG/recent"
    ])
    
    industry_blogs: List[str] = field(default_factory=lambda: [
        "https://openai.com/blog/",
        "https://blog.google/technology/ai/",
        "https://blogs.microsoft.com/ai/",
        "https://www.anthropic.com/news"
    ])

@dataclass
class SchedulingConfig:
    """Scheduling and automation configuration"""
    timezone: str = "UTC"
    max_queue_size: int = 50
    retry_delay_minutes: int = 30
    max_scheduling_days_ahead: int = 30
    
    # Scheduling conflict detection
    minimum_post_interval_minutes: int = 30
    
    # Automation settings
    auto_publish: bool = True
    auto_retry_failed: bool = True
    cleanup_old_posts_days: int = 30

@dataclass
class LoggingConfig:
    """Logging configuration"""
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    json_logging: bool = field(default_factory=lambda: os.getenv("JSON_LOGGING", "true").lower() == "true")
    log_file: Optional[str] = field(default_factory=lambda: os.getenv("LOG_FILE"))
    
    # Log retention
    max_log_entries: int = 10000
    log_rotation_days: int = 7

@dataclass
class WebInterfaceConfig:
    """Web interface configuration"""
    host: str = "0.0.0.0"
    port: int = 5000
    debug: bool = field(default_factory=lambda: os.getenv("FLASK_DEBUG", "false").lower() == "true")
    secret_key: str = field(default_factory=lambda: os.getenv("FLASK_SECRET_KEY", "dev-secret-key-change-in-production"))
    
    # Session settings
    session_timeout_minutes: int = 60
    
    # Dashboard refresh intervals
    dashboard_refresh_seconds: int = 30
    status_refresh_seconds: int = 10

class Config:
    """Main configuration class that aggregates all settings"""
    
    def __init__(self):
        self.api = APIConfig()
        self.content = ContentConfig()
        self.scraping = ScrapingConfig()
        self.scheduling = SchedulingConfig()
        self.logging = LoggingConfig()
        self.web = WebInterfaceConfig()
        
        # System metadata
        self.system_name = "MultiAgentContentSystem"
        self.version = "1.0.0"
        self.startup_time = datetime.utcnow()
        
        # Validate configuration
        self._validate_config()
    
    def _validate_config(self):
        """Validate configuration settings"""
        validation_errors = []
        
        # Validate API keys
        if not self.api.openai_api_key:
            validation_errors.append("OPENAI_API_KEY is required")
        
        # LinkedIn token is optional - system can run without publishing capability
        if not self.api.linkedin_access_token:
            print("Warning: LINKEDIN_ACCESS_TOKEN not provided - publishing will be disabled")
        
        # Validate content settings
        if self.content.min_content_length >= self.content.max_content_length:
            validation_errors.append("min_content_length must be less than max_content_length")
        
        if self.content.min_approval_score < 1.0 or self.content.min_approval_score > 5.0:
            validation_errors.append("min_approval_score must be between 1.0 and 5.0")
        
        # Validate posting times
        for time_str in self.content.posting_times:
            try:
                hour, minute = map(int, time_str.split(':'))
                if not (0 <= hour <= 23 and 0 <= minute <= 59):
                    validation_errors.append(f"Invalid posting time format: {time_str}")
            except ValueError:
                validation_errors.append(f"Invalid posting time format: {time_str}")
        
        # Validate hashtag count range
        if len(self.content.hashtag_count_range) != 2 or self.content.hashtag_count_range[0] > self.content.hashtag_count_range[1]:
            validation_errors.append("hashtag_count_range must be a tuple of (min, max) where min <= max")
        
        # Validate scheduling settings
        if self.scheduling.max_queue_size < 1:
            validation_errors.append("max_queue_size must be at least 1")
        
        if self.scheduling.minimum_post_interval_minutes < 1:
            validation_errors.append("minimum_post_interval_minutes must be at least 1")
        
        # Validate web interface settings
        if not (1 <= self.web.port <= 65535):
            validation_errors.append("Web interface port must be between 1 and 65535")
        
        if validation_errors:
            raise ValueError(f"Configuration validation failed:\n" + "\n".join(f"- {error}" for error in validation_errors))
    
    def get_research_sources(self) -> Dict[str, List[str]]:
        """Get all research sources organized by type"""
        return {
            "ai_news_sites": self.scraping.ai_news_sources,
            "academic_sources": self.scraping.academic_sources,
            "industry_blogs": self.scraping.industry_blogs
        }
    
    def get_platform_configs(self) -> Dict[str, Dict[str, Any]]:
        """Get social media platform configurations"""
        return {
            "linkedin": {
                "enabled": bool(self.api.linkedin_access_token),
                "access_token": self.api.linkedin_access_token,
                "max_length": 3000,
                "supports_images": True,
                "api_endpoint": "https://api.linkedin.com/v2"
            },
            "x": {
                "enabled": bool(self.api.x_api_key and self.api.x_access_token),
                "api_key": self.api.x_api_key,
                "access_token": self.api.x_access_token,
                "api_secret": self.api.x_api_secret,
                "access_token_secret": self.api.x_access_token_secret,
                "max_length": 280,
                "supports_images": True,
                "api_endpoint": "https://api.twitter.com/2"
            }
        }
    
    def get_content_validation_rules(self) -> Dict[str, Any]:
        """Get content validation rules"""
        return {
            "min_length": self.content.min_content_length,
            "max_length": self.content.max_content_length,
            "required_sections": ["hook", "insight", "cta", "hashtags"],
            "topic_pillars": self.content.topic_pillars,
            "min_approval_score": self.content.min_approval_score,
            "hashtag_count": {
                "min": self.content.hashtag_count_range[0],
                "max": self.content.hashtag_count_range[1]
            },
            "brand_voice": self.content.brand_voice,
            "brand_tone": self.content.brand_tone
        }
    
    def get_agent_configs(self) -> Dict[str, Dict[str, Any]]:
        """Get agent-specific configurations"""
        return {
            "orchestration": {
                "validation_rules": self.get_content_validation_rules(),
                "retry_attempts": self.content.max_retry_attempts
            },
            "trend_researcher": {
                "sources": self.get_research_sources(),
                "max_trends": 10,
                "scraping_timeout": self.scraping.request_timeout,
                "max_retries": self.scraping.max_retries
            },
            "content_developer": {
                "max_length": self.content.max_content_length,
                "brand_voice": self.content.brand_voice,
                "brand_tone": self.content.brand_tone,
                "topic_pillars": self.content.topic_pillars
            },
            "content_editor": {
                "validation_rules": self.get_content_validation_rules(),
                "min_approval_score": self.content.min_approval_score
            },
            "distribution": {
                "platforms": self.get_platform_configs(),
                "generate_images": True,
                "image_style": "professional, clean, modern, AI-themed"
            },
            "scheduler": {
                "daily_times": self.content.posting_times,
                "timezone": self.scheduling.timezone,
                "max_queue_size": self.scheduling.max_queue_size,
                "retry_attempts": self.content.max_retry_attempts,
                "retry_delay_minutes": self.scheduling.retry_delay_minutes
            }
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "system": {
                "name": self.system_name,
                "version": self.version,
                "startup_time": self.startup_time.isoformat()
            },
            "api": {
                "openai_configured": bool(self.api.openai_api_key),
                "linkedin_configured": bool(self.api.linkedin_access_token),
                "x_configured": bool(self.api.x_api_key and self.api.x_access_token)
            },
            "content": {
                "daily_post_count": self.content.daily_post_count,
                "posting_times": self.content.posting_times,
                "content_length_range": [self.content.min_content_length, self.content.max_content_length],
                "hashtag_count_range": self.content.hashtag_count_range,
                "topic_pillars": self.content.topic_pillars,
                "min_approval_score": self.content.min_approval_score
            },
            "scheduling": {
                "timezone": self.scheduling.timezone,
                "max_queue_size": self.scheduling.max_queue_size,
                "auto_publish": self.scheduling.auto_publish,
                "auto_retry_failed": self.scheduling.auto_retry_failed
            },
            "web_interface": {
                "host": self.web.host,
                "port": self.web.port,
                "debug": self.web.debug
            }
        }
    
    def update_from_env(self):
        """Update configuration from environment variables"""
        # API configurations
        if os.getenv("OPENAI_API_KEY"):
            self.api.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        if os.getenv("LINKEDIN_ACCESS_TOKEN"):
            self.api.linkedin_access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")
        
        # Content configurations
        if os.getenv("DAILY_POST_COUNT"):
            try:
                self.content.daily_post_count = int(os.getenv("DAILY_POST_COUNT"))
            except ValueError:
                pass
        
        if os.getenv("POSTING_TIMES"):
            try:
                times = os.getenv("POSTING_TIMES").split(",")
                self.content.posting_times = [time.strip() for time in times]
            except:
                pass
        
        if os.getenv("MIN_APPROVAL_SCORE"):
            try:
                self.content.min_approval_score = float(os.getenv("MIN_APPROVAL_SCORE"))
            except ValueError:
                pass
        
        # Web interface configurations
        if os.getenv("WEB_PORT"):
            try:
                self.web.port = int(os.getenv("WEB_PORT"))
            except ValueError:
                pass
        
        # Re-validate after updates
        self._validate_config()

# Global configuration instance
_config_instance = None

def get_config() -> Config:
    """Get the global configuration instance"""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance

def reload_config():
    """Reload configuration from environment"""
    global _config_instance
    _config_instance = Config()
    return _config_instance
