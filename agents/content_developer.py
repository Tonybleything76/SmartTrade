"""
Content Developer Agent
AI-Powered Copywriter
Generates high-quality LinkedIn posts from trending topics
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, List

from agents.base_agent import BaseAgent
from openai import OpenAI

class ContentDeveloperAgent(BaseAgent):
    """Generates branded content from trending AI topics"""
    
    def __init__(self):
        super().__init__(
            name="Content Developer Agent",
            role="AI-Powered Copywriter", 
            tools=["openai_gpt4", "content_templates", "brand_guidelines"]
        )
        
        # Initialize OpenAI client
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Content templates and guidelines
        self.content_format = {
            "structure": "Hook → Insight → CTA → Hashtags",
            "max_length": 1300,  # LinkedIn post limit
            "tone": "professional, thought-leadership, engaging",
            "cta_types": ["question", "action", "discussion_starter", "resource_share"]
        }
        
        # Brand voice guidelines
        self.brand_guidelines = {
            "voice": "Authoritative yet approachable AI expert",
            "personality": ["innovative", "insightful", "practical", "forward-thinking"],
            "avoid": ["hype", "overpromising", "technical jargon without explanation"],
            "focus": "Value for AI professionals and business leaders"
        }
        
        # Post format templates
        self.post_templates = {
            "insight_sharing": """
🔥 {hook}

{main_insight}

Here's what this means for AI professionals:
{professional_implications}

{call_to_action}

{hashtags}
            """,
            
            "trend_analysis": """
📈 {trend_title}

{trend_explanation}

Why this matters:
• {point_1}
• {point_2} 
• {point_3}

{call_to_action}

{hashtags}
            """,
            
            "future_outlook": """
🚀 The future of {topic_area}:

{future_vision}

What we're seeing now:
{current_developments}

What to watch for:
{future_indicators}

{call_to_action}

{hashtags}
            """
        }
    
    def execute_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute content development task"""
        task_type = task_data.get("task_type", "generate_content")
        
        if task_type == "generate_content":
            trend = task_data.get("trend")
            format_type = task_data.get("format", "linkedin_post")
            return self.generate_content_from_trend(trend, format_type)
        elif task_type == "refine_content":
            content = task_data.get("content")
            feedback = task_data.get("feedback")
            return self.refine_content(content, feedback)
        else:
            return self.create_response(False, error=f"Unknown task type: {task_type}")
    
    def generate_content_from_trend(self, trend: Dict[str, Any], format_type: str = "linkedin_post") -> Dict[str, Any]:
        """Generate LinkedIn post content from a trending topic"""
        if not trend:
            return self.create_response(False, error="No trend data provided")
        
        self.log_message(f"Generating content for trend: {trend.get('title', 'Unknown')}")
        
        try:
            # Select appropriate template based on trend characteristics
            template_type = self.select_template_type(trend)
            
            # Generate content using AI
            generated_content = self.generate_ai_content(trend, template_type)
            
            if not generated_content:
                return self.create_response(False, error="AI content generation failed")
            
            # Format and structure the content
            formatted_content = self.format_content(generated_content, template_type)
            
            # Add metadata
            content_package = {
                "content": formatted_content,
                "metadata": {
                    "source_trend": trend.get("title"),
                    "category": trend.get("category"),
                    "template_used": template_type,
                    "generated_at": datetime.utcnow().isoformat(),
                    "word_count": len(formatted_content.get("text", "").split()),
                    "character_count": len(formatted_content.get("text", "")),
                    "estimated_reading_time": self.calculate_reading_time(formatted_content.get("text", ""))
                }
            }
            
            return self.create_response(True, content_package)
            
        except Exception as e:
            self.log_message(f"Content generation failed: {e}", level="error")
            return self.create_response(False, error=f"Content generation failed: {e}")
    
    def select_template_type(self, trend: Dict[str, Any]) -> str:
        """Select the most appropriate template based on trend characteristics"""
        category = trend.get("category", "").lower()
        content_angles = trend.get("content_angles", [])
        
        # Logic to select template based on trend characteristics
        if "future" in str(content_angles).lower() or "roadmap" in category:
            return "future_outlook"
        elif trend.get("relevance_score", 0) > 8:
            return "trend_analysis"
        else:
            return "insight_sharing"
    
    def generate_ai_content(self, trend: Dict[str, Any], template_type: str) -> Dict[str, Any]:
        """Generate content components using AI"""
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            content_prompt = f"""
            You are an expert AI content creator specializing in LinkedIn posts for AI professionals and business leaders.
            
            Create a high-quality LinkedIn post based on this trending AI topic:
            
            Title: {trend.get('title', '')}
            Summary: {trend.get('summary', '')}
            Category: {trend.get('category', '')}
            Key Insights: {trend.get('key_insights', [])}
            Professional Implications: {trend.get('professional_implications', '')}
            Business Impact: {trend.get('business_impact', '')}
            Content Angles: {trend.get('content_angles', [])}
            
            Brand Guidelines:
            - Voice: {self.brand_guidelines['voice']}
            - Personality: {', '.join(self.brand_guidelines['personality'])}
            - Focus: {self.brand_guidelines['focus']}
            - Avoid: {', '.join(self.brand_guidelines['avoid'])}
            
            Template Type: {template_type}
            
            Generate content with these components:
            1. Hook (attention-grabbing opening line with emoji)
            2. Main insight or analysis (2-3 paragraphs)
            3. Professional implications (bullet points or numbered list)
            4. Call to action (engaging question or action request)
            5. Relevant hashtags (5-8 hashtags)
            
            Requirements:
            - Keep under {self.content_format['max_length']} characters
            - Use {self.content_format['tone']} tone
            - Include practical value for AI professionals
            - Make it engaging and shareable
            - Bold key phrases for emphasis
            
            Respond with JSON:
            {{
                "hook": "Engaging opening with emoji",
                "main_content": "Main insight and analysis paragraphs",
                "implications": ["implication1", "implication2", "implication3"],
                "call_to_action": "Engaging CTA question or request",
                "hashtags": ["#AI", "#Innovation", "#TechLeadership", "#ArtificialIntelligence", "#FutureOfWork"],
                "key_phrases": ["phrase1", "phrase2"]
            }}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": content_prompt}],
                response_format={"type": "json_object"},
                max_tokens=1500
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            self.log_message(f"AI content generation failed: {e}", level="error")
            return {}
    
    def format_content(self, content_components: Dict[str, Any], template_type: str) -> Dict[str, Any]:
        """Format content components into final post structure"""
        try:
            # Get template
            template = self.post_templates.get(template_type, self.post_templates["insight_sharing"])
            
            # Extract components
            hook = content_components.get("hook", "")
            main_content = content_components.get("main_content", "")
            implications = content_components.get("implications", [])
            cta = content_components.get("call_to_action", "")
            hashtags = content_components.get("hashtags", [])
            key_phrases = content_components.get("key_phrases", [])
            
            # Format implications as bullet points
            formatted_implications = "\n".join([f"• {imp}" for imp in implications[:3]])
            
            # Create hashtag string
            hashtag_string = " ".join(hashtags[:8])  # Limit to 8 hashtags
            
            # Format the post based on template type
            if template_type == "trend_analysis":
                formatted_text = template.format(
                    trend_title=hook,
                    trend_explanation=main_content,
                    point_1=implications[0] if len(implications) > 0 else "Key development in AI",
                    point_2=implications[1] if len(implications) > 1 else "Impact on professionals", 
                    point_3=implications[2] if len(implications) > 2 else "Future opportunities",
                    call_to_action=cta,
                    hashtags=hashtag_string
                )
            elif template_type == "future_outlook":
                lines = main_content.split('\n')
                future_vision = lines[0] if lines else main_content[:200]
                current_developments = lines[1] if len(lines) > 1 else formatted_implications
                future_indicators = lines[2] if len(lines) > 2 else "Continued innovation expected"
                
                formatted_text = template.format(
                    topic_area=content_components.get("topic", "AI"),
                    future_vision=future_vision,
                    current_developments=current_developments,
                    future_indicators=future_indicators,
                    call_to_action=cta,
                    hashtags=hashtag_string
                )
            else:  # insight_sharing
                formatted_text = template.format(
                    hook=hook,
                    main_insight=main_content,
                    professional_implications=formatted_implications,
                    call_to_action=cta,
                    hashtags=hashtag_string
                )
            
            # Apply bold formatting to key phrases
            for phrase in key_phrases:
                if phrase in formatted_text:
                    formatted_text = formatted_text.replace(phrase, f"**{phrase}**")
            
            return {
                "text": formatted_text.strip(),
                "hook": hook,
                "main_content": main_content,
                "implications": implications,
                "call_to_action": cta,
                "hashtags": hashtags,
                "key_phrases": key_phrases,
                "template_type": template_type
            }
            
        except Exception as e:
            self.log_message(f"Content formatting failed: {e}", level="error")
            return {"text": "", "error": str(e)}
    
    def refine_content(self, content: Dict[str, Any], feedback: str) -> Dict[str, Any]:
        """Refine content based on editor feedback"""
        if not content or not feedback:
            return self.create_response(False, error="Missing content or feedback for refinement")
        
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            refinement_prompt = f"""
            Refine this LinkedIn post based on the editor feedback:
            
            Original Content:
            {content.get('text', '')}
            
            Editor Feedback:
            {feedback}
            
            Brand Guidelines:
            - Voice: {self.brand_guidelines['voice']}
            - Avoid: {', '.join(self.brand_guidelines['avoid'])}
            - Focus: {self.brand_guidelines['focus']}
            
            Improve the content while maintaining its core message and structure.
            Keep it under {self.content_format['max_length']} characters.
            
            Return the refined content maintaining the same JSON structure as the original.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": refinement_prompt}],
                response_format={"type": "json_object"},
                max_tokens=1500
            )
            
            refined_components = json.loads(response.choices[0].message.content)
            
            # Reformat the refined content
            template_type = content.get("template_type", "insight_sharing")
            refined_content = self.format_content(refined_components, template_type)
            
            # Update metadata
            refined_content["metadata"] = content.get("metadata", {})
            refined_content["metadata"]["refined_at"] = datetime.utcnow().isoformat()
            refined_content["metadata"]["refinement_feedback"] = feedback
            
            return self.create_response(True, {"content": refined_content})
            
        except Exception as e:
            self.log_message(f"Content refinement failed: {e}", level="error")
            return self.create_response(False, error=f"Content refinement failed: {e}")
    
    def calculate_reading_time(self, text: str) -> int:
        """Calculate estimated reading time in seconds"""
        words = len(text.split())
        # Average reading speed: 200 words per minute
        reading_time_minutes = words / 200
        return max(1, int(reading_time_minutes * 60))  # Convert to seconds, minimum 1 second
