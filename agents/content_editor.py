"""
Content Editor Agent  
Fact Checker / Brand Editor
Reviews content for quality, accuracy, and brand alignment
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, List

from agents.base_agent import BaseAgent
from openai import OpenAI

class ContentEditorAgent(BaseAgent):
    """Reviews and validates content for quality and brand alignment"""
    
    def __init__(self):
        super().__init__(
            name="Content Editor Agent",
            role="Fact Checker / Brand Editor",
            tools=["openai_moderation", "fact_checking", "brand_validation", "content_scoring"]
        )
        
        # Initialize OpenAI client
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Content quality criteria
        self.quality_criteria = {
            "grammar_and_clarity": {
                "weight": 0.25,
                "checks": ["grammar", "spelling", "readability", "clarity"]
            },
            "brand_alignment": {
                "weight": 0.25, 
                "checks": ["voice_consistency", "message_alignment", "tone_appropriateness"]
            },
            "factual_accuracy": {
                "weight": 0.25,
                "checks": ["claims_verification", "data_accuracy", "source_credibility"]
            },
            "engagement_potential": {
                "weight": 0.25,
                "checks": ["hook_strength", "cta_effectiveness", "hashtag_relevance", "shareability"]
            }
        }
        
        # Brand guidelines for validation
        self.brand_standards = {
            "voice": "authoritative yet approachable AI expert",
            "tone": ["professional", "insightful", "practical", "forward-thinking"],
            "messaging_pillars": [
                "AI innovation leadership",
                "Practical professional value", 
                "Future-oriented thinking",
                "Accessible expertise"
            ],
            "content_requirements": {
                "min_length": 100,
                "max_length": 1300,
                "required_elements": ["hook", "insight", "cta", "hashtags"],
                "hashtag_count": {"min": 3, "max": 8}
            }
        }
        
        # Common content issues to flag
        self.content_flags = {
            "red_flags": [
                "unrealistic claims",
                "unsubstantiated statistics", 
                "overly promotional language",
                "technical jargon without explanation",
                "clickbait language",
                "outdated information"
            ],
            "yellow_flags": [
                "weak call to action",
                "unclear main message",
                "insufficient professional value",
                "too generic or broad",
                "missing key context"
            ]
        }
    
    def execute_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute content editing task"""
        task_type = task_data.get("task_type", "edit_content")
        
        if task_type == "edit_content":
            content = task_data.get("content")
            return self.review_content(content)
        elif task_type == "fact_check":
            content = task_data.get("content")
            return self.fact_check_content(content)
        elif task_type == "score_content":
            content = task_data.get("content")
            return self.score_content(content)
        else:
            return self.create_response(False, error=f"Unknown task type: {task_type}")
    
    def review_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive content review and validation"""
        if not content:
            return self.create_response(False, error="No content provided for review")
        
        self.log_message("Starting comprehensive content review")
        
        try:
            # Extract content text and components
            content_text = content.get("text", "")
            content_components = {
                "hook": content.get("hook", ""),
                "main_content": content.get("main_content", ""),
                "cta": content.get("call_to_action", ""),
                "hashtags": content.get("hashtags", [])
            }
            
            # Perform multiple validation checks
            review_results = {
                "content_id": content.get("metadata", {}).get("generated_at", "unknown"),
                "reviewed_at": datetime.utcnow().isoformat(),
                "approved": False,
                "overall_score": 0,
                "detailed_scores": {},
                "issues_found": [],
                "suggestions": [],
                "moderation_check": {}
            }
            
            # 1. OpenAI Moderation Check
            moderation_result = self.run_moderation_check(content_text)
            review_results["moderation_check"] = moderation_result
            
            if not moderation_result.get("safe", True):
                review_results["issues_found"].append("Content flagged by moderation system")
                return self.create_response(True, review_results)
            
            # 2. Comprehensive AI-powered review
            ai_review = self.run_ai_content_review(content_text, content_components)
            
            # 3. Technical validation
            technical_validation = self.validate_technical_requirements(content_text, content_components)
            
            # 4. Brand alignment check  
            brand_check = self.validate_brand_alignment(content_text)
            
            # Compile all results
            review_results["detailed_scores"] = {
                "ai_review_score": ai_review.get("overall_score", 0),
                "technical_score": technical_validation.get("score", 0),
                "brand_alignment_score": brand_check.get("score", 0)
            }
            
            # Calculate overall score
            scores = list(review_results["detailed_scores"].values())
            review_results["overall_score"] = sum(scores) / len(scores) if scores else 0
            
            # Combine issues and suggestions
            review_results["issues_found"].extend(ai_review.get("issues", []))
            review_results["issues_found"].extend(technical_validation.get("issues", []))
            review_results["issues_found"].extend(brand_check.get("issues", []))
            
            review_results["suggestions"].extend(ai_review.get("suggestions", []))
            review_results["suggestions"].extend(technical_validation.get("suggestions", []))
            review_results["suggestions"].extend(brand_check.get("suggestions", []))
            
            # Determine approval status
            review_results["approved"] = (
                review_results["overall_score"] >= 3.5 and  # Minimum score threshold
                len([issue for issue in review_results["issues_found"] if "critical" in issue.lower()]) == 0
            )
            
            # Generate feedback summary
            review_results["feedback_summary"] = self.generate_feedback_summary(review_results)
            
            return self.create_response(True, review_results)
            
        except Exception as e:
            self.log_message(f"Content review failed: {e}", level="error")
            return self.create_response(False, error=f"Content review failed: {e}")
    
    def run_moderation_check(self, content_text: str) -> Dict[str, Any]:
        """Run OpenAI moderation check on content"""
        try:
            response = self.openai_client.moderations.create(input=content_text)
            result = response.results[0]
            
            return {
                "safe": not result.flagged,
                "categories": result.categories.model_dump() if hasattr(result, 'categories') else {},
                "category_scores": result.category_scores.model_dump() if hasattr(result, 'category_scores') else {}
            }
            
        except Exception as e:
            self.log_message(f"Moderation check failed: {e}", level="warning")
            return {"safe": True, "error": str(e)}
    
    def run_ai_content_review(self, content_text: str, components: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive AI-powered content review"""
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            review_prompt = f"""
            You are an expert content editor specializing in AI and technology content for LinkedIn.
            
            Review this LinkedIn post for:
            1. Grammar, spelling, and clarity
            2. Professional tone and brand voice consistency  
            3. Factual accuracy and credibility of claims
            4. Engagement potential and call-to-action effectiveness
            5. Overall value for AI professionals and business leaders
            
            Content to review:
            {content_text}
            
            Content components:
            - Hook: {components.get('hook', '')}
            - Main content: {components.get('main_content', '')}
            - CTA: {components.get('cta', '')}
            - Hashtags: {', '.join(components.get('hashtags', []))}
            
            Brand guidelines:
            - Voice: {self.brand_standards['voice']}
            - Tone: {', '.join(self.brand_standards['tone'])}
            - Messaging pillars: {', '.join(self.brand_standards['messaging_pillars'])}
            
            Content flags to watch for:
            - Red flags: {', '.join(self.content_flags['red_flags'])}
            - Yellow flags: {', '.join(self.content_flags['yellow_flags'])}
            
            Provide detailed analysis with specific recommendations.
            
            Respond with JSON:
            {{
                "overall_score": 4.2,
                "category_scores": {{
                    "grammar_clarity": 4.5,
                    "brand_alignment": 4.0,
                    "factual_accuracy": 4.0,
                    "engagement_potential": 4.3
                }},
                "issues": ["specific issue 1", "specific issue 2"],
                "suggestions": ["specific suggestion 1", "specific suggestion 2"],
                "strengths": ["strength 1", "strength 2"],
                "improvement_areas": ["area 1", "area 2"]
            }}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": review_prompt}],
                response_format={"type": "json_object"},
                max_tokens=1500
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            self.log_message(f"AI content review failed: {e}", level="warning")
            return {"overall_score": 3.0, "issues": [f"AI review failed: {e}"], "suggestions": []}
    
    def validate_technical_requirements(self, content_text: str, components: Dict[str, Any]) -> Dict[str, Any]:
        """Validate technical content requirements"""
        issues = []
        suggestions = []
        score = 5.0
        
        try:
            # Length validation
            char_count = len(content_text)
            word_count = len(content_text.split())
            
            if char_count < self.brand_standards["content_requirements"]["min_length"]:
                issues.append(f"Content too short: {char_count} characters (minimum {self.brand_standards['content_requirements']['min_length']})")
                score -= 1.0
            elif char_count > self.brand_standards["content_requirements"]["max_length"]:
                issues.append(f"Content too long: {char_count} characters (maximum {self.brand_standards['content_requirements']['max_length']})")
                score -= 0.5
            
            # Required elements validation
            required_elements = self.brand_standards["content_requirements"]["required_elements"]
            missing_elements = []
            
            if not components.get("hook"):
                missing_elements.append("hook")
            if not components.get("main_content"):
                missing_elements.append("main content")
            if not components.get("cta"):
                missing_elements.append("call to action")
            if not components.get("hashtags"):
                missing_elements.append("hashtags")
            
            if missing_elements:
                issues.append(f"Missing required elements: {', '.join(missing_elements)}")
                score -= len(missing_elements) * 0.5
            
            # Hashtag validation
            hashtag_count = len(components.get("hashtags", []))
            hashtag_requirements = self.brand_standards["content_requirements"]["hashtag_count"]
            
            if hashtag_count < hashtag_requirements["min"]:
                issues.append(f"Too few hashtags: {hashtag_count} (minimum {hashtag_requirements['min']})")
                score -= 0.3
            elif hashtag_count > hashtag_requirements["max"]:
                suggestions.append(f"Consider reducing hashtags: {hashtag_count} (recommended maximum {hashtag_requirements['max']})")
                score -= 0.1
            
            # Structure validation
            if content_text and not any(emoji in content_text[:50] for emoji in ["🔥", "📈", "🚀", "💡", "⚡", "🎯"]):
                suggestions.append("Consider adding an engaging emoji to the hook")
                score -= 0.2
            
            return {
                "score": max(0, min(5, score)),
                "issues": issues,
                "suggestions": suggestions,
                "metrics": {
                    "character_count": char_count,
                    "word_count": word_count,
                    "hashtag_count": hashtag_count
                }
            }
            
        except Exception as e:
            return {
                "score": 3.0,
                "issues": [f"Technical validation error: {e}"],
                "suggestions": []
            }
    
    def validate_brand_alignment(self, content_text: str) -> Dict[str, Any]:
        """Validate content alignment with brand standards"""
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            brand_prompt = f"""
            Evaluate this content's alignment with our brand standards:
            
            Content: {content_text}
            
            Brand Standards:
            - Voice: {self.brand_standards['voice']}
            - Tone: {', '.join(self.brand_standards['tone'])}
            - Messaging Pillars: {', '.join(self.brand_standards['messaging_pillars'])}
            
            Check for:
            1. Voice consistency (authoritative yet approachable)
            2. Appropriate tone (professional, insightful, practical)
            3. Alignment with messaging pillars
            4. Value for target audience (AI professionals, business leaders)
            
            Score 1-5 and provide specific feedback.
            
            Respond with JSON:
            {{
                "score": 4.2,
                "voice_consistency": 4.0,
                "tone_appropriateness": 4.5,
                "message_alignment": 4.0,
                "audience_value": 4.3,
                "issues": ["issue if any"],
                "suggestions": ["suggestion if any"]
            }}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": brand_prompt}],
                response_format={"type": "json_object"},
                max_tokens=800
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            return {
                "score": 3.0,
                "issues": [f"Brand alignment check failed: {e}"],
                "suggestions": []
            }
    
    def generate_feedback_summary(self, review_results: Dict[str, Any]) -> str:
        """Generate human-readable feedback summary"""
        try:
            score = review_results.get("overall_score", 0)
            approved = review_results.get("approved", False)
            issues = review_results.get("issues_found", [])
            suggestions = review_results.get("suggestions", [])
            
            # Status message
            if approved:
                status = f"✅ APPROVED (Score: {score:.1f}/5.0)"
            else:
                status = f"❌ NEEDS REVISION (Score: {score:.1f}/5.0)"
            
            # Issues summary
            issues_text = ""
            if issues:
                issues_text = f"\n🚨 Issues to address:\n" + "\n".join([f"• {issue}" for issue in issues[:5]])
            
            # Suggestions summary  
            suggestions_text = ""
            if suggestions:
                suggestions_text = f"\n💡 Suggestions for improvement:\n" + "\n".join([f"• {suggestion}" for suggestion in suggestions[:5]])
            
            return f"{status}{issues_text}{suggestions_text}"
            
        except Exception as e:
            return f"Feedback summary generation failed: {e}"
    
    def fact_check_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Perform detailed fact-checking on content claims"""
        if not content:
            return self.create_response(False, error="No content provided for fact-checking")
        
        content_text = content.get("text", "")
        
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            fact_check_prompt = f"""
            Perform fact-checking analysis on this AI-related content:
            
            {content_text}
            
            Check for:
            1. Factual accuracy of AI/technology claims
            2. Credibility of any statistics or data mentioned
            3. Currency of information (is it up-to-date?)
            4. Potential exaggerations or unsupported claims
            5. Technical accuracy of AI concepts
            
            Provide specific feedback on any claims that need verification or correction.
            
            Respond with JSON:
            {{
                "fact_check_score": 4.5,
                "verified_claims": ["claim 1", "claim 2"],
                "questionable_claims": ["claim that needs verification"],
                "inaccurate_claims": ["clearly wrong claim"],
                "recommendations": ["specific recommendation"]
            }}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": fact_check_prompt}],
                response_format={"type": "json_object"},
                max_tokens=1000
            )
            
            fact_check_results = json.loads(response.choices[0].message.content)
            fact_check_results["fact_checked_at"] = datetime.utcnow().isoformat()
            
            return self.create_response(True, fact_check_results)
            
        except Exception as e:
            return self.create_response(False, error=f"Fact-checking failed: {e}")
    
    def score_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Generate detailed content scoring"""
        if not content:
            return self.create_response(False, error="No content provided for scoring")
        
        # Run a simplified review focused on scoring
        review_result = self.review_content(content)
        
        if review_result.get("success"):
            scoring_data = {
                "overall_score": review_result.get("data", {}).get("overall_score", 0),
                "detailed_scores": review_result.get("data", {}).get("detailed_scores", {}),
                "scoring_criteria": self.quality_criteria,
                "scored_at": datetime.utcnow().isoformat()
            }
            return self.create_response(True, scoring_data)
        else:
            return review_result
