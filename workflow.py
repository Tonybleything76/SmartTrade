"""
Content Workflow Management
Orchestrates the multi-agent content creation pipeline
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from enum import Enum

from agents.orchestration import OrchestrationAgent
from agents.trend_researcher import TrendResearcherAgent
from agents.content_developer import ContentDeveloperAgent
from agents.content_editor import ContentEditorAgent
from agents.distribution import DistributionAgent
from agents.scheduler import SchedulerAgent
from agents.base_agent import AgentCommunicationHub
from utils.logger import setup_logger, system_logger
from utils.config import get_config

class WorkflowStatus(Enum):
    """Workflow execution status"""
    IDLE = "idle"
    INITIALIZING = "initializing"
    RESEARCHING = "researching"
    GENERATING = "generating"
    EDITING = "editing"
    SCHEDULING = "scheduling"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

class ContentWorkflow:
    """Main workflow orchestrator for the content creation pipeline"""
    
    def __init__(self):
        self.config = get_config()
        self.logger = setup_logger("content_workflow")
        
        # Initialize agents
        self.agents = {}
        self.communication_hub = AgentCommunicationHub()
        
        # Workflow state
        self.current_status = WorkflowStatus.IDLE
        self.current_run_id = None
        self.workflow_history = []
        self.active_jobs = {}
        self.manual_request_queue = []
        
        # Performance metrics
        self.metrics = {
            "total_workflows": 0,
            "successful_workflows": 0,
            "failed_workflows": 0,
            "average_duration_seconds": 0,
            "content_generated_today": 0,
            "content_published_today": 0
        }
        
        # Workflow configuration
        self.workflow_config = {
            "max_concurrent_jobs": 3,
            "job_timeout_minutes": 30,
            "retry_failed_jobs": True,
            "auto_cleanup_old_jobs": True,
            "cleanup_age_hours": 24
        }
    
    def initialize(self) -> bool:
        """Initialize the workflow system and all agents"""
        try:
            self.logger.info("Initializing Content Workflow System...")
            self.current_status = WorkflowStatus.INITIALIZING
            
            # Initialize all agents
            agent_classes = [
                ("orchestration", OrchestrationAgent),
                ("trend_researcher", TrendResearcherAgent),
                ("content_developer", ContentDeveloperAgent),
                ("content_editor", ContentEditorAgent),
                ("distribution", DistributionAgent),
                ("scheduler", SchedulerAgent)
            ]
            
            for agent_name, agent_class in agent_classes:
                try:
                    agent = agent_class()
                    self.agents[agent_name] = agent
                    self.communication_hub.register_agent(agent)
                    self.logger.info(f"Initialized agent: {agent_name}")
                except Exception as e:
                    self.logger.error(f"Failed to initialize agent {agent_name}: {e}")
                    return False
            
            # Validate system configuration
            validation_result = self.validate_system_configuration()
            if not validation_result["valid"]:
                self.logger.error(f"System validation failed: {validation_result['errors']}")
                return False
            
            self.current_status = WorkflowStatus.IDLE
            self.logger.info("Content Workflow System initialized successfully")
            
            # Log system startup
            system_logger.log_system_event(
                "workflow_initialization",
                "Content workflow system initialized",
                {
                    "agents_count": len(self.agents),
                    "config_valid": True,
                    "status": self.current_status.value
                }
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Workflow initialization failed: {e}")
            self.current_status = WorkflowStatus.FAILED
            return False
    
    def validate_system_configuration(self) -> Dict[str, Any]:
        """Validate system configuration and agent readiness"""
        errors = []
        warnings = []
        
        try:
            # Check API keys
            if not self.config.api.openai_api_key:
                errors.append("OpenAI API key not configured")
            
            if not self.config.api.linkedin_access_token:
                warnings.append("LinkedIn access token not configured - LinkedIn publishing disabled")
            
            # Check agent initialization
            required_agents = ["orchestration", "trend_researcher", "content_developer", "content_editor", "distribution", "scheduler"]
            for agent_name in required_agents:
                if agent_name not in self.agents:
                    errors.append(f"Required agent not initialized: {agent_name}")
            
            # Check content configuration
            if not self.config.content.topic_pillars:
                errors.append("No topic pillars configured for content generation")
            
            if not self.config.content.posting_times:
                errors.append("No posting times configured")
            
            # Check research sources
            sources = self.config.get_research_sources()
            total_sources = sum(len(source_list) for source_list in sources.values())
            if total_sources == 0:
                warnings.append("No research sources configured")
            
            return {
                "valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings,
                "checks_performed": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "valid": False,
                "errors": [f"Configuration validation error: {e}"],
                "warnings": warnings
            }
    
    def execute_pipeline(self, manual_trigger: bool = False) -> Dict[str, Any]:
        """Execute the complete content generation pipeline"""
        if self.current_status not in [WorkflowStatus.IDLE, WorkflowStatus.COMPLETED, WorkflowStatus.FAILED]:
            return {
                "success": False,
                "error": f"Workflow already running with status: {self.current_status.value}",
                "current_run_id": self.current_run_id
            }
        
        # Generate new run ID
        run_id = str(uuid.uuid4())
        self.current_run_id = run_id
        self.current_status = WorkflowStatus.RESEARCHING
        
        start_time = datetime.utcnow()
        
        # Initialize workflow run
        workflow_run = {
            "run_id": run_id,
            "started_at": start_time.isoformat(),
            "manual_trigger": manual_trigger,
            "status": self.current_status.value,
            "stages": {},
            "content_generated": [],
            "errors": [],
            "metrics": {}
        }
        
        self.active_jobs[run_id] = workflow_run
        
        try:
            self.logger.info(f"Starting content pipeline execution: {run_id}")
            system_logger.log_content_pipeline(run_id, "started", "initiated", {"manual_trigger": manual_trigger})
            
            # Stage 1: Research trending topics
            research_result = self.execute_research_stage(run_id)
            workflow_run["stages"]["research"] = research_result
            
            if not research_result.get("success"):
                return self.handle_workflow_failure(run_id, "research", research_result.get("error", "Research stage failed"))
            
            trends = research_result.get("data", {}).get("trends", [])
            if not trends:
                return self.handle_workflow_failure(run_id, "research", "No trends found")
            
            # Stage 2: Generate content from trends
            self.current_status = WorkflowStatus.GENERATING
            workflow_run["status"] = self.current_status.value
            
            generation_result = self.execute_generation_stage(run_id, trends[:3])  # Generate from top 3 trends
            workflow_run["stages"]["generation"] = generation_result
            
            if not generation_result.get("success"):
                return self.handle_workflow_failure(run_id, "generation", generation_result.get("error", "Content generation failed"))
            
            generated_content = generation_result.get("data", {}).get("content", [])
            if not generated_content:
                return self.handle_workflow_failure(run_id, "generation", "No content generated")
            
            # Stage 3: Edit and validate content
            self.current_status = WorkflowStatus.EDITING
            workflow_run["status"] = self.current_status.value
            
            editing_result = self.execute_editing_stage(run_id, generated_content)
            workflow_run["stages"]["editing"] = editing_result
            
            if not editing_result.get("success"):
                return self.handle_workflow_failure(run_id, "editing", editing_result.get("error", "Content editing failed"))
            
            approved_content = editing_result.get("data", {}).get("approved_content", [])
            if not approved_content:
                return self.handle_workflow_failure(run_id, "editing", "No content approved")
            
            # Stage 4: Schedule and distribute content
            self.current_status = WorkflowStatus.SCHEDULING
            workflow_run["status"] = self.current_status.value
            
            scheduling_result = self.execute_scheduling_stage(run_id, approved_content)
            workflow_run["stages"]["scheduling"] = scheduling_result
            
            if not scheduling_result.get("success"):
                return self.handle_workflow_failure(run_id, "scheduling", scheduling_result.get("error", "Content scheduling failed"))
            
            # Complete workflow
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            workflow_run.update({
                "completed_at": end_time.isoformat(),
                "duration_seconds": duration,
                "status": "completed",
                "content_generated": approved_content,
                "scheduled_posts": scheduling_result.get("data", {}).get("scheduled_posts", [])
            })
            
            self.current_status = WorkflowStatus.COMPLETED
            self.complete_workflow_run(run_id, True)
            
            # Update metrics
            self.update_workflow_metrics(run_id, True, duration)
            
            self.logger.info(f"Content pipeline completed successfully: {run_id}")
            system_logger.log_content_pipeline(run_id, "completed", "success", {
                "duration_seconds": duration,
                "content_count": len(approved_content),
                "scheduled_count": len(scheduling_result.get("data", {}).get("scheduled_posts", []))
            })
            
            return {
                "success": True,
                "run_id": run_id,
                "duration_seconds": duration,
                "content_generated": len(approved_content),
                "posts_scheduled": len(scheduling_result.get("data", {}).get("scheduled_posts", [])),
                "workflow_data": workflow_run
            }
            
        except Exception as e:
            return self.handle_workflow_failure(run_id, "execution", str(e))
    
    def execute_research_stage(self, run_id: str) -> Dict[str, Any]:
        """Execute the trend research stage"""
        try:
            stage_start = datetime.utcnow()
            
            researcher = self.agents.get("trend_researcher")
            if not researcher:
                return {"success": False, "error": "Trend researcher agent not available"}
            
            # Request trend research
            task_data = {
                "task_type": "research_trends",
                "topics": self.config.content.topic_pillars,
                "max_trends": 10
            }
            
            result = researcher.execute_task(task_data)
            
            stage_duration = (datetime.utcnow() - stage_start).total_seconds()
            
            if result.get("success"):
                trends = result.get("data", {}).get("trends", [])
                
                return {
                    "success": True,
                    "stage": "research",
                    "duration_seconds": stage_duration,
                    "data": {
                        "trends": trends,
                        "trends_count": len(trends),
                        "sources_checked": result.get("data", {}).get("sources_checked", 0)
                    }
                }
            else:
                return {
                    "success": False,
                    "stage": "research",
                    "duration_seconds": stage_duration,
                    "error": result.get("error", "Unknown research error")
                }
                
        except Exception as e:
            return {"success": False, "stage": "research", "error": f"Research stage exception: {e}"}
    
    def execute_generation_stage(self, run_id: str, trends: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute the content generation stage"""
        try:
            stage_start = datetime.utcnow()
            
            developer = self.agents.get("content_developer")
            if not developer:
                return {"success": False, "error": "Content developer agent not available"}
            
            generated_content = []
            generation_errors = []
            
            for i, trend in enumerate(trends):
                try:
                    task_data = {
                        "task_type": "generate_content",
                        "trend": trend,
                        "format": "linkedin_post"
                    }
                    
                    result = developer.execute_task(task_data)
                    
                    if result.get("success"):
                        content_data = result.get("data", {})
                        content_data["trend_source"] = trend.get("title", f"Trend {i+1}")
                        content_data["generation_order"] = i + 1
                        generated_content.append(content_data)
                    else:
                        generation_errors.append(f"Trend {i+1}: {result.get('error', 'Unknown error')}")
                        
                except Exception as e:
                    generation_errors.append(f"Trend {i+1}: {str(e)}")
            
            stage_duration = (datetime.utcnow() - stage_start).total_seconds()
            
            if generated_content:
                return {
                    "success": True,
                    "stage": "generation",
                    "duration_seconds": stage_duration,
                    "data": {
                        "content": generated_content,
                        "content_count": len(generated_content),
                        "trends_processed": len(trends),
                        "errors": generation_errors
                    }
                }
            else:
                return {
                    "success": False,
                    "stage": "generation",
                    "duration_seconds": stage_duration,
                    "error": f"No content generated. Errors: {'; '.join(generation_errors)}"
                }
                
        except Exception as e:
            return {"success": False, "stage": "generation", "error": f"Generation stage exception: {e}"}
    
    def execute_editing_stage(self, run_id: str, content_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute the content editing and validation stage"""
        try:
            stage_start = datetime.utcnow()
            
            editor = self.agents.get("content_editor")
            if not editor:
                return {"success": False, "error": "Content editor agent not available"}
            
            approved_content = []
            rejected_content = []
            editing_errors = []
            
            for i, content_item in enumerate(content_list):
                try:
                    task_data = {
                        "task_type": "edit_content",
                        "content": content_item.get("content", {})
                    }
                    
                    result = editor.execute_task(task_data)
                    
                    if result.get("success"):
                        review_data = result.get("data", {})
                        
                        if review_data.get("approved", False):
                            # Content approved
                            approved_item = {
                                **content_item,
                                "review_data": review_data,
                                "approval_score": review_data.get("overall_score", 0),
                                "reviewed_at": datetime.utcnow().isoformat()
                            }
                            approved_content.append(approved_item)
                        else:
                            # Content rejected
                            rejected_item = {
                                **content_item,
                                "review_data": review_data,
                                "rejection_reason": review_data.get("feedback_summary", "Quality standards not met"),
                                "reviewed_at": datetime.utcnow().isoformat()
                            }
                            rejected_content.append(rejected_item)
                    else:
                        editing_errors.append(f"Content {i+1}: {result.get('error', 'Unknown error')}")
                        
                except Exception as e:
                    editing_errors.append(f"Content {i+1}: {str(e)}")
            
            stage_duration = (datetime.utcnow() - stage_start).total_seconds()
            
            return {
                "success": True,
                "stage": "editing",
                "duration_seconds": stage_duration,
                "data": {
                    "approved_content": approved_content,
                    "rejected_content": rejected_content,
                    "approved_count": len(approved_content),
                    "rejected_count": len(rejected_content),
                    "total_reviewed": len(content_list),
                    "approval_rate": len(approved_content) / len(content_list) * 100 if content_list else 0,
                    "errors": editing_errors
                }
            }
                
        except Exception as e:
            return {"success": False, "stage": "editing", "error": f"Editing stage exception: {e}"}
    
    def execute_scheduling_stage(self, run_id: str, approved_content: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute the content scheduling stage"""
        try:
            stage_start = datetime.utcnow()
            
            scheduler = self.agents.get("scheduler")
            if not scheduler:
                return {"success": False, "error": "Scheduler agent not available"}
            
            scheduled_posts = []
            scheduling_errors = []
            
            for i, content_item in enumerate(approved_content):
                try:
                    task_data = {
                        "task_type": "schedule_content",
                        "content": content_item.get("content", {}),
                        # Let scheduler find next available slot
                    }
                    
                    result = scheduler.execute_task(task_data)
                    
                    if result.get("success"):
                        scheduled_data = result.get("data", {})
                        scheduled_post = {
                            **content_item,
                            "scheduling_data": scheduled_data,
                            "job_id": scheduled_data.get("job_id"),
                            "scheduled_time": scheduled_data.get("scheduled_time"),
                            "scheduled_at": datetime.utcnow().isoformat()
                        }
                        scheduled_posts.append(scheduled_post)
                    else:
                        scheduling_errors.append(f"Content {i+1}: {result.get('error', 'Unknown error')}")
                        
                except Exception as e:
                    scheduling_errors.append(f"Content {i+1}: {str(e)}")
            
            stage_duration = (datetime.utcnow() - stage_start).total_seconds()
            
            if scheduled_posts:
                return {
                    "success": True,
                    "stage": "scheduling",
                    "duration_seconds": stage_duration,
                    "data": {
                        "scheduled_posts": scheduled_posts,
                        "scheduled_count": len(scheduled_posts),
                        "total_content": len(approved_content),
                        "scheduling_success_rate": len(scheduled_posts) / len(approved_content) * 100 if approved_content else 0,
                        "errors": scheduling_errors
                    }
                }
            else:
                return {
                    "success": False,
                    "stage": "scheduling",
                    "duration_seconds": stage_duration,
                    "error": f"No content scheduled. Errors: {'; '.join(scheduling_errors)}"
                }
                
        except Exception as e:
            return {"success": False, "stage": "scheduling", "error": f"Scheduling stage exception: {e}"}
    
    def handle_workflow_failure(self, run_id: str, failed_stage: str, error: str) -> Dict[str, Any]:
        """Handle workflow failure"""
        self.current_status = WorkflowStatus.FAILED
        
        if run_id in self.active_jobs:
            self.active_jobs[run_id].update({
                "status": "failed",
                "failed_stage": failed_stage,
                "error": error,
                "failed_at": datetime.utcnow().isoformat()
            })
        
        self.complete_workflow_run(run_id, False)
        self.update_workflow_metrics(run_id, False, 0)
        
        self.logger.error(f"Workflow {run_id} failed at {failed_stage}: {error}")
        system_logger.log_content_pipeline(run_id, failed_stage, "failed", {"error": error})
        
        return {
            "success": False,
            "run_id": run_id,
            "failed_stage": failed_stage,
            "error": error,
            "status": self.current_status.value
        }
    
    def complete_workflow_run(self, run_id: str, success: bool):
        """Complete a workflow run and move to history"""
        if run_id in self.active_jobs:
            workflow_data = self.active_jobs[run_id]
            workflow_data["success"] = success
            
            # Move to history
            self.workflow_history.append(workflow_data)
            del self.active_jobs[run_id]
            
            # Cleanup old history
            if len(self.workflow_history) > 100:  # Keep last 100 runs
                self.workflow_history = self.workflow_history[-100:]
        
        # Reset current run
        if self.current_run_id == run_id:
            self.current_run_id = None
            self.current_status = WorkflowStatus.IDLE
    
    def update_workflow_metrics(self, run_id: str, success: bool, duration: float):
        """Update workflow performance metrics"""
        self.metrics["total_workflows"] += 1
        
        if success:
            self.metrics["successful_workflows"] += 1
        else:
            self.metrics["failed_workflows"] += 1
        
        # Update average duration
        if duration > 0:
            total_duration = self.metrics["average_duration_seconds"] * (self.metrics["total_workflows"] - 1)
            self.metrics["average_duration_seconds"] = (total_duration + duration) / self.metrics["total_workflows"]
        
        # Update daily counts
        today = datetime.utcnow().date()
        
        # Count content generated today
        today_content = sum(
            len(run.get("content_generated", []))
            for run in self.workflow_history
            if datetime.fromisoformat(run.get("started_at", "1900-01-01")).date() == today
        )
        self.metrics["content_generated_today"] = today_content
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """Get current workflow status and metrics"""
        return {
            "current_status": self.current_status.value,
            "current_run_id": self.current_run_id,
            "active_jobs": len(self.active_jobs),
            "metrics": self.metrics,
            "agents_status": {
                name: agent.get_capabilities() if hasattr(agent, 'get_capabilities') else {"status": "unknown"}
                for name, agent in self.agents.items()
            },
            "system_health": self.check_system_health(),
            "last_successful_run": self.get_last_successful_run(),
            "recent_runs": self.workflow_history[-5:] if self.workflow_history else []
        }
    
    def check_system_health(self) -> Dict[str, Any]:
        """Check overall system health"""
        health_status = {
            "overall": "healthy",
            "agents": {},
            "configuration": "valid",
            "issues": []
        }
        
        # Check agent health
        for agent_name, agent in self.agents.items():
            try:
                # Basic agent health check
                health_status["agents"][agent_name] = "healthy"
            except Exception as e:
                health_status["agents"][agent_name] = f"unhealthy: {e}"
                health_status["issues"].append(f"Agent {agent_name}: {e}")
        
        # Check configuration
        config_validation = self.validate_system_configuration()
        if not config_validation.get("valid"):
            health_status["configuration"] = "invalid"
            health_status["issues"].extend(config_validation.get("errors", []))
        
        # Determine overall health
        if health_status["issues"]:
            health_status["overall"] = "degraded" if len(health_status["issues"]) < 3 else "unhealthy"
        
        return health_status
    
    def get_last_successful_run(self) -> Optional[Dict[str, Any]]:
        """Get information about the last successful workflow run"""
        successful_runs = [run for run in self.workflow_history if run.get("success")]
        return successful_runs[-1] if successful_runs else None
    
    def has_manual_requests(self) -> bool:
        """Check if there are manual content generation requests"""
        return len(self.manual_request_queue) > 0
    
    def queue_manual_request(self, request_data: Dict[str, Any]) -> str:
        """Queue a manual content generation request"""
        request_id = str(uuid.uuid4())
        request = {
            "request_id": request_id,
            "requested_at": datetime.utcnow().isoformat(),
            "request_data": request_data,
            "status": "queued"
        }
        
        self.manual_request_queue.append(request)
        return request_id
    
    def process_manual_requests(self) -> Dict[str, Any]:
        """Process queued manual requests"""
        if not self.manual_request_queue:
            return {"success": True, "message": "No manual requests to process"}
        
        # Process the oldest request
        request = self.manual_request_queue.pop(0)
        request["status"] = "processing"
        
        # Execute pipeline for manual request
        result = self.execute_pipeline(manual_trigger=True)
        
        return {
            "success": result.get("success", False),
            "request_id": request["request_id"],
            "pipeline_result": result
        }
    
    def get_workflow_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get workflow execution history"""
        return self.workflow_history[-limit:] if self.workflow_history else []
    
    def cleanup_old_workflows(self):
        """Cleanup old workflow data"""
        if not self.workflow_config.get("auto_cleanup_old_jobs"):
            return
        
        cleanup_age = timedelta(hours=self.workflow_config.get("cleanup_age_hours", 24))
        cutoff_time = datetime.utcnow() - cleanup_age
        
        # Clean up old workflow history
        self.workflow_history = [
            run for run in self.workflow_history
            if datetime.fromisoformat(run.get("started_at", "1900-01-01")) > cutoff_time
        ]
        
        # Clean up old active jobs (shouldn't happen, but safety check)
        old_jobs = [
            run_id for run_id, job in self.active_jobs.items()
            if datetime.fromisoformat(job.get("started_at", "1900-01-01")) < cutoff_time
        ]
        
        for job_id in old_jobs:
            del self.active_jobs[job_id]
            self.logger.warning(f"Cleaned up stale job: {job_id}")
