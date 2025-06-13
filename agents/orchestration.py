"""
Orchestration Agent
Chief Content Officer / Workflow Manager
Coordinates the entire content creation pipeline
"""

import json
from datetime import datetime
from typing import Dict, Any, List

from agents.base_agent import BaseAgent
from utils.logger import setup_logger

class OrchestrationAgent(BaseAgent):
    """Manages the overall content workflow and coordinates between agents"""
    
    def __init__(self):
        super().__init__(
            name="Orchestration Agent",
            role="Chief Content Officer / Workflow Manager",
            tools=["workflow_state", "content_validation", "quality_scoring"]
        )
        
        # Content validation rules
        self.validation_rules = {
            "min_length": 100,
            "max_length": 3000,
            "required_sections": ["hook", "insight", "cta", "hashtags"],
            "topic_pillars": [
                "AI Innovation",
                "Generative AI", 
                "Technology Roadmaps & Integration",
                "AI for Professionals",
                "Agentic Systems"
            ]
        }
        
        # Pipeline status tracking
        self.pipeline_status = {
            "current_run_id": None,
            "stage": "idle",
            "posts_generated": 0,
            "posts_approved": 0,
            "posts_published": 0,
            "errors": []
        }
        
    def execute_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute orchestration task"""
        task_type = task_data.get("task_type", "run_pipeline")
        
        if task_type == "run_pipeline":
            return self.run_content_pipeline()
        elif task_type == "validate_content":
            return self.validate_content(task_data.get("content"))
        elif task_type == "get_status":
            return self.get_pipeline_status()
        else:
            return self.create_response(False, error=f"Unknown task type: {task_type}")
    
    def run_content_pipeline(self) -> Dict[str, Any]:
        """Run the complete content generation pipeline"""
        import uuid
        
        run_id = str(uuid.uuid4())
        self.pipeline_status["current_run_id"] = run_id
        self.pipeline_status["stage"] = "starting"
        self.pipeline_status["errors"] = []
        
        self.log_message(f"Starting content pipeline run: {run_id}")
        
        try:
            # Stage 1: Research trends
            self.pipeline_status["stage"] = "researching_trends"
            trends_result = self.request_trend_research()
            
            if not trends_result.get("success"):
                return self.handle_pipeline_error("Trend research failed", trends_result.get("error"))
            
            trends = trends_result.get("data", {}).get("trends", [])
            if not trends:
                return self.handle_pipeline_error("No trends found", "Trend researcher returned empty results")
            
            self.log_message(f"Found {len(trends)} trending topics")
            
            # Stage 2: Generate content
            self.pipeline_status["stage"] = "generating_content"
            content_results = []
            
            # Generate 3 posts from top trends
            top_trends = trends[:3]
            
            for i, trend in enumerate(top_trends):
                content_result = self.request_content_generation(trend)
                
                if content_result.get("success"):
                    content_results.append(content_result.get("data"))
                    self.pipeline_status["posts_generated"] += 1
                else:
                    self.log_message(f"Content generation failed for trend {i+1}: {content_result.get('error')}", level="warning")
            
            if not content_results:
                return self.handle_pipeline_error("Content generation failed", "No content was generated")
            
            # Stage 3: Edit and validate content
            self.pipeline_status["stage"] = "editing_content"
            approved_content = []
            
            for content in content_results:
                edit_result = self.request_content_editing(content)
                
                if edit_result.get("success") and edit_result.get("data", {}).get("approved"):
                    approved_content.append(edit_result.get("data"))
                    self.pipeline_status["posts_approved"] += 1
                else:
                    self.log_message(f"Content rejected by editor: {edit_result.get('data', {}).get('feedback', 'Unknown reason')}", level="warning")
            
            if not approved_content:
                return self.handle_pipeline_error("Content editing failed", "No content was approved by editor")
            
            # Stage 4: Schedule and distribute
            self.pipeline_status["stage"] = "scheduling_content"
            scheduled_posts = []
            
            for content in approved_content:
                schedule_result = self.request_content_scheduling(content)
                
                if schedule_result.get("success"):
                    scheduled_posts.append(schedule_result.get("data"))
                    self.pipeline_status["posts_published"] += 1
                else:
                    self.log_message(f"Content scheduling failed: {schedule_result.get('error')}", level="warning")
            
            # Complete pipeline
            self.pipeline_status["stage"] = "completed"
            
            return self.create_response(True, {
                "run_id": run_id,
                "posts_generated": self.pipeline_status["posts_generated"],
                "posts_approved": self.pipeline_status["posts_approved"], 
                "posts_scheduled": len(scheduled_posts),
                "scheduled_posts": scheduled_posts
            })
            
        except Exception as e:
            return self.handle_pipeline_error("Pipeline execution error", str(e))
    
    def handle_pipeline_error(self, error_type: str, error_message: str) -> Dict[str, Any]:
        """Handle pipeline errors and update status"""
        self.pipeline_status["stage"] = "error"
        self.pipeline_status["errors"].append({
            "type": error_type,
            "message": error_message,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        self.log_message(f"Pipeline error - {error_type}: {error_message}", level="error")
        
        return self.create_response(False, error=f"{error_type}: {error_message}")
    
    def request_trend_research(self) -> Dict[str, Any]:
        """Request trend research from Trend Researcher Agent"""
        # This would normally use the communication hub to send messages
        # For this implementation, we'll simulate the agent interaction
        
        try:
            from agents.trend_researcher import TrendResearcherAgent
            researcher = TrendResearcherAgent()
            
            task_data = {
                "task_type": "research_trends",
                "topics": self.validation_rules["topic_pillars"],
                "max_trends": 10
            }
            
            return researcher.execute_task(task_data)
            
        except Exception as e:
            self.log_message(f"Failed to request trend research: {e}", level="error")
            return self.create_response(False, error=f"Trend research request failed: {e}")
    
    def request_content_generation(self, trend: Dict[str, Any]) -> Dict[str, Any]:
        """Request content generation from Content Developer Agent"""
        try:
            from agents.content_developer import ContentDeveloperAgent
            developer = ContentDeveloperAgent()
            
            task_data = {
                "task_type": "generate_content",
                "trend": trend,
                "format": "linkedin_post"
            }
            
            return developer.execute_task(task_data)
            
        except Exception as e:
            self.log_message(f"Failed to request content generation: {e}", level="error")
            return self.create_response(False, error=f"Content generation request failed: {e}")
    
    def request_content_editing(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Request content editing from Content Editor Agent"""
        try:
            from agents.content_editor import ContentEditorAgent
            editor = ContentEditorAgent()
            
            task_data = {
                "task_type": "edit_content",
                "content": content
            }
            
            return editor.execute_task(task_data)
            
        except Exception as e:
            self.log_message(f"Failed to request content editing: {e}", level="error")
            return self.create_response(False, error=f"Content editing request failed: {e}")
    
    def request_content_scheduling(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Request content scheduling from Scheduler Agent"""
        try:
            from agents.scheduler import SchedulerAgent
            scheduler = SchedulerAgent()
            
            task_data = {
                "task_type": "schedule_content",
                "content": content
            }
            
            return scheduler.execute_task(task_data)
            
        except Exception as e:
            self.log_message(f"Failed to request content scheduling: {e}", level="error")
            return self.create_response(False, error=f"Content scheduling request failed: {e}")
    
    def validate_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Validate content against brand guidelines and quality standards"""
        if not content:
            return self.create_response(False, error="No content provided for validation")
        
        validation_results = {
            "length_check": False,
            "structure_check": False,
            "topic_alignment": False,
            "score": 0,
            "issues": []
        }
        
        try:
            text = content.get("text", "")
            
            # Length validation
            if self.validation_rules["min_length"] <= len(text) <= self.validation_rules["max_length"]:
                validation_results["length_check"] = True
            else:
                validation_results["issues"].append(f"Content length {len(text)} outside range {self.validation_rules['min_length']}-{self.validation_rules['max_length']}")
            
            # Structure validation
            has_required_sections = all(
                section in text.lower() or content.get(section) 
                for section in self.validation_rules["required_sections"]
            )
            
            if has_required_sections:
                validation_results["structure_check"] = True
            else:
                validation_results["issues"].append("Missing required sections (hook, insight, CTA, hashtags)")
            
            # Topic alignment validation
            topic_match = any(
                topic.lower() in text.lower() 
                for topic in self.validation_rules["topic_pillars"]
            )
            
            if topic_match:
                validation_results["topic_alignment"] = True
            else:
                validation_results["issues"].append("Content does not align with topic pillars")
            
            # Calculate overall score
            checks_passed = sum([
                validation_results["length_check"],
                validation_results["structure_check"], 
                validation_results["topic_alignment"]
            ])
            
            validation_results["score"] = (checks_passed / 3) * 5  # Scale to 1-5
            
            return self.create_response(True, validation_results)
            
        except Exception as e:
            return self.create_response(False, error=f"Content validation failed: {e}")
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get current pipeline status"""
        return self.create_response(True, self.pipeline_status)
