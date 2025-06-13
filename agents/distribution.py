"""
Distribution Agent
Platform Publisher / Social Media Manager  
Handles publishing content to LinkedIn and other social platforms
"""

import os
import json
import requests
from datetime import datetime
from typing import Dict, Any, List
import base64

from agents.base_agent import BaseAgent
from openai import OpenAI

class DistributionAgent(BaseAgent):
    """Manages content distribution across social media platforms"""
    
    def __init__(self):
        super().__init__(
            name="Distribution Agent",
            role="Platform Publisher / Social Media Manager",
            tools=["linkedin_api", "x_api", "dalle_image_generation", "platform_optimization"]
        )
        
        # Initialize OpenAI client for image generation
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Platform configurations
        self.platforms = {
            "linkedin": {
                "enabled": True,
                "api_endpoint": "https://api.linkedin.com/v2",
                "access_token": os.getenv("LINKEDIN_ACCESS_TOKEN"),
                "max_length": 3000,
                "supports_images": True
            },
            "x": {
                "enabled": bool(os.getenv("X_API_KEY")),
                "api_endpoint": "https://api.twitter.com/2",
                "access_token": os.getenv("X_ACCESS_TOKEN"),
                "max_length": 280,
                "supports_images": True
            }
        }
        
        # Content optimization settings
        self.optimization_settings = {
            "generate_images": True,
            "image_style": "professional, clean, modern, AI-themed",
            "brand_colors": ["#1e3a8a", "#3b82f6", "#60a5fa", "#93c5fd"],
            "include_branding": True
        }
        
        # Publishing status tracking
        self.publishing_history = []
    
    def execute_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute distribution task"""
        task_type = task_data.get("task_type", "publish_content")
        
        if task_type == "publish_content":
            content = task_data.get("content")
            platforms = task_data.get("platforms", ["linkedin"])
            return self.publish_content(content, platforms)
        elif task_type == "generate_image":
            prompt = task_data.get("prompt")
            return self.generate_content_image(prompt)
        elif task_type == "get_publishing_status":
            return self.get_publishing_status()
        else:
            return self.create_response(False, error=f"Unknown task type: {task_type}")
    
    def publish_content(self, content: Dict[str, Any], platforms: List[str] = None) -> Dict[str, Any]:
        """Publish content to specified social platforms"""
        if not content:
            return self.create_response(False, error="No content provided for publishing")
        
        platforms = platforms or ["linkedin"]
        self.log_message(f"Publishing content to platforms: {', '.join(platforms)}")
        
        try:
            # Generate visual asset if needed
            image_data = None
            if self.optimization_settings["generate_images"]:
                image_result = self.generate_content_image_from_content(content)
                if image_result.get("success"):
                    image_data = image_result.get("data")
            
            # Publish to each platform
            publishing_results = {}
            
            for platform in platforms:
                if platform not in self.platforms:
                    publishing_results[platform] = {
                        "success": False,
                        "error": f"Platform {platform} not supported"
                    }
                    continue
                
                if not self.platforms[platform]["enabled"]:
                    publishing_results[platform] = {
                        "success": False,
                        "error": f"Platform {platform} not configured"
                    }
                    continue
                
                # Optimize content for platform
                optimized_content = self.optimize_content_for_platform(content, platform)
                
                # Publish to platform
                if platform == "linkedin":
                    result = self.publish_to_linkedin(optimized_content, image_data)
                elif platform == "x":
                    result = self.publish_to_x(optimized_content, image_data)
                else:
                    result = {"success": False, "error": f"Publishing method not implemented for {platform}"}
                
                publishing_results[platform] = result
                
                # Log publishing attempt
                self.log_publishing_attempt(content, platform, result)
            
            # Determine overall success
            successful_publishes = [r for r in publishing_results.values() if r.get("success")]
            overall_success = len(successful_publishes) > 0
            
            return self.create_response(overall_success, {
                "publishing_results": publishing_results,
                "successful_platforms": len(successful_publishes),
                "total_platforms": len(platforms),
                "image_generated": image_data is not None,
                "published_at": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            self.log_message(f"Content publishing failed: {e}", level="error")
            return self.create_response(False, error=f"Content publishing failed: {e}")
    
    def optimize_content_for_platform(self, content: Dict[str, Any], platform: str) -> Dict[str, Any]:
        """Optimize content for specific platform requirements"""
        platform_config = self.platforms.get(platform, {})
        max_length = platform_config.get("max_length", 3000)
        
        content_text = content.get("text", "")
        
        # Truncate if necessary
        if len(content_text) > max_length:
            # Try to truncate at sentence boundary
            sentences = content_text.split('. ')
            truncated = ""
            
            for sentence in sentences:
                if len(truncated + sentence + '. ') <= max_length - 20:  # Leave room for "..."
                    truncated += sentence + '. '
                else:
                    break
            
            if not truncated:
                truncated = content_text[:max_length-3] + "..."
            else:
                truncated = truncated.rstrip() + "..."
            
            content_text = truncated
        
        # Platform-specific optimizations
        if platform == "x":
            # For X/Twitter, prioritize hashtags and make content more concise
            hashtags = content.get("hashtags", [])
            if hashtags and len(content_text) + len(" ".join(hashtags)) <= max_length:
                content_text += "\n\n" + " ".join(hashtags[:3])  # Limit hashtags for X
        
        return {
            **content,
            "text": content_text,
            "platform": platform,
            "optimized_at": datetime.utcnow().isoformat()
        }
    
    def publish_to_linkedin(self, content: Dict[str, Any], image_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Publish content to LinkedIn"""
        access_token = self.platforms["linkedin"]["access_token"]
        
        if not access_token:
            return {"success": False, "error": "LinkedIn access token not configured"}
        
        try:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "X-Restli-Protocol-Version": "2.0.0"
            }
            
            # Get user profile info
            profile_response = requests.get(
                f"{self.platforms['linkedin']['api_endpoint']}/me",
                headers=headers
            )
            
            if profile_response.status_code != 200:
                return {"success": False, "error": f"Failed to get LinkedIn profile: {profile_response.text}"}
            
            profile_data = profile_response.json()
            person_urn = f"urn:li:person:{profile_data['id']}"
            
            # Prepare post data
            post_data = {
                "author": person_urn,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": content.get("text", "")
                        },
                        "shareMediaCategory": "ARTICLE" if not image_data else "IMAGE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }
            
            # Add image if available
            if image_data and image_data.get("url"):
                # For simplicity, we'll post as article with image URL
                # In production, you'd upload the image to LinkedIn's media API first
                post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [{
                    "status": "READY",
                    "description": {
                        "text": "AI Innovation Insights"
                    },
                    "media": image_data.get("url"),
                    "title": {
                        "text": content.get("hook", "AI Innovation Update")[:100]
                    }
                }]
            
            # Post to LinkedIn
            response = requests.post(
                f"{self.platforms['linkedin']['api_endpoint']}/ugcPosts",
                headers=headers,
                json=post_data
            )
            
            if response.status_code in [200, 201]:
                post_id = response.json().get("id", "unknown")
                return {
                    "success": True,
                    "platform": "linkedin",
                    "post_id": post_id,
                    "post_url": f"https://www.linkedin.com/feed/update/{post_id}",
                    "published_at": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": f"LinkedIn API error: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            return {"success": False, "error": f"LinkedIn publishing failed: {e}"}
    
    def publish_to_x(self, content: Dict[str, Any], image_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Publish content to X (Twitter)"""
        # Note: This is a simplified implementation. In production, you'd use proper OAuth 2.0
        # and handle image uploads through X's media API
        
        access_token = self.platforms["x"]["access_token"]
        
        if not access_token:
            return {"success": False, "error": "X access token not configured"}
        
        try:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            tweet_data = {
                "text": content.get("text", "")
            }
            
            # For production, you'd handle image upload separately
            if image_data:
                # Placeholder - in production, upload media first and get media_id
                pass
            
            response = requests.post(
                f"{self.platforms['x']['api_endpoint']}/tweets",
                headers=headers,
                json=tweet_data
            )
            
            if response.status_code in [200, 201]:
                tweet_data = response.json()
                tweet_id = tweet_data.get("data", {}).get("id", "unknown")
                
                return {
                    "success": True,
                    "platform": "x",
                    "post_id": tweet_id,
                    "post_url": f"https://x.com/i/status/{tweet_id}",
                    "published_at": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": f"X API error: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            return {"success": False, "error": f"X publishing failed: {e}"}
    
    def generate_content_image_from_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Generate an image based on the content"""
        try:
            # Extract key themes from content
            content_text = content.get("text", "")
            hook = content.get("hook", "")
            hashtags = content.get("hashtags", [])
            
            # Create image prompt based on content
            image_prompt = self.create_image_prompt_from_content(content_text, hook, hashtags)
            
            return self.generate_content_image(image_prompt)
            
        except Exception as e:
            self.log_message(f"Content-based image generation failed: {e}", level="warning")
            return self.create_response(False, error=f"Image generation failed: {e}")
    
    def create_image_prompt_from_content(self, content_text: str, hook: str, hashtags: List[str]) -> str:
        """Create DALL-E prompt based on content"""
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            prompt_creation = f"""
            Create a DALL-E image generation prompt for this LinkedIn AI content:
            
            Hook: {hook}
            Content preview: {content_text[:500]}
            Hashtags: {', '.join(hashtags[:5])}
            
            Style requirements:
            - Professional, clean, modern design
            - AI and technology themed
            - Suitable for LinkedIn business audience
            - Blue color scheme (#1e3a8a, #3b82f6, #60a5fa)
            - Abstract or conceptual (no specific people or companies)
            - High contrast, readable on social media
            
            Create a detailed prompt for generating a relevant visual.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt_creation}],
                max_tokens=300
            )
            
            generated_prompt = response.choices[0].message.content.strip()
            
            # Enhance with style specifications
            final_prompt = f"{generated_prompt}. Professional business illustration style, clean design, modern technology aesthetic, blue color palette, high quality, suitable for LinkedIn."
            
            return final_prompt
            
        except Exception as e:
            # Fallback to generic prompt
            return f"Professional AI technology illustration, modern blue design, abstract concept art, clean business style, suitable for LinkedIn"
    
    def generate_content_image(self, prompt: str) -> Dict[str, Any]:
        """Generate image using DALL-E"""
        if not prompt:
            return self.create_response(False, error="No prompt provided for image generation")
        
        try:
            self.log_message(f"Generating image with prompt: {prompt[:100]}...")
            
            response = self.openai_client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1
            )
            
            image_url = response.data[0].url
            
            return self.create_response(True, {
                "url": image_url,
                "prompt": prompt,
                "generated_at": datetime.utcnow().isoformat(),
                "model": "dall-e-3",
                "size": "1024x1024"
            })
            
        except Exception as e:
            self.log_message(f"Image generation failed: {e}", level="error")
            return self.create_response(False, error=f"Image generation failed: {e}")
    
    def log_publishing_attempt(self, content: Dict[str, Any], platform: str, result: Dict[str, Any]):
        """Log publishing attempt for tracking"""
        log_entry = {
            "content_id": content.get("metadata", {}).get("generated_at", "unknown"),
            "platform": platform,
            "success": result.get("success", False),
            "post_id": result.get("post_id"),
            "error": result.get("error"),
            "attempted_at": datetime.utcnow().isoformat()
        }
        
        self.publishing_history.append(log_entry)
        
        # Keep only last 100 entries
        if len(self.publishing_history) > 100:
            self.publishing_history = self.publishing_history[-100:]
    
    def get_publishing_status(self) -> Dict[str, Any]:
        """Get publishing history and status"""
        try:
            # Calculate success rates
            total_attempts = len(self.publishing_history)
            successful_attempts = len([h for h in self.publishing_history if h.get("success")])
            
            success_rate = (successful_attempts / total_attempts * 100) if total_attempts > 0 else 0
            
            # Platform breakdown
            platform_stats = {}
            for entry in self.publishing_history:
                platform = entry.get("platform", "unknown")
                if platform not in platform_stats:
                    platform_stats[platform] = {"total": 0, "successful": 0}
                
                platform_stats[platform]["total"] += 1
                if entry.get("success"):
                    platform_stats[platform]["successful"] += 1
            
            # Calculate platform success rates
            for platform, stats in platform_stats.items():
                stats["success_rate"] = (stats["successful"] / stats["total"] * 100) if stats["total"] > 0 else 0
            
            return self.create_response(True, {
                "total_attempts": total_attempts,
                "successful_attempts": successful_attempts,
                "success_rate": round(success_rate, 1),
                "platform_stats": platform_stats,
                "recent_attempts": self.publishing_history[-10:],  # Last 10 attempts
                "platforms_configured": [p for p, config in self.platforms.items() if config["enabled"]]
            })
            
        except Exception as e:
            return self.create_response(False, error=f"Failed to get publishing status: {e}")
