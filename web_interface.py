"""
Web Interface for Multi-Agent Content System
Flask-based dashboard for monitoring and controlling the content pipeline
"""

import json
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from typing import Dict, Any

from workflow import ContentWorkflow
from utils.config import get_config
from utils.logger import setup_logger, system_logger

def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    config = get_config()
    
    # Configure Flask app
    app.config['SECRET_KEY'] = config.web.secret_key
    app.config['DEBUG'] = config.web.debug
    
    # Initialize logger
    logger = setup_logger("web_interface")
    
    # Initialize workflow (will be created by main app)
    workflow = None
    
    def get_workflow():
        """Get workflow instance - will be set by main app"""
        nonlocal workflow
        if workflow is None:
            workflow = ContentWorkflow()
            workflow.initialize()
        return workflow
    
    @app.route('/')
    def dashboard():
        """Main dashboard page"""
        try:
            wf = get_workflow()
            
            # Get current system status
            status = wf.get_workflow_status()
            
            # Get recent workflow runs
            recent_runs = wf.get_workflow_history(limit=10)
            
            # Get today's metrics
            today = datetime.utcnow().date()
            today_runs = [
                run for run in recent_runs
                if datetime.fromisoformat(run.get("started_at", "1900-01-01")).date() == today
            ]
            
            # Calculate dashboard metrics
            dashboard_data = {
                "system_status": status.get("current_status", "unknown"),
                "current_run_id": status.get("current_run_id"),
                "system_health": status.get("system_health", {}),
                "agents_status": status.get("agents_status", {}),
                "metrics": status.get("metrics", {}),
                "recent_runs": recent_runs,
                "today_runs": today_runs,
                "today_stats": {
                    "total_runs": len(today_runs),
                    "successful_runs": len([r for r in today_runs if r.get("success")]),
                    "failed_runs": len([r for r in today_runs if not r.get("success")]),
                    "content_generated": sum(len(r.get("content_generated", [])) for r in today_runs),
                    "average_duration": sum(r.get("duration_seconds", 0) for r in today_runs) / len(today_runs) if today_runs else 0
                }
            }
            
            return render_template('dashboard.html', data=dashboard_data, config=config.to_dict())
            
        except Exception as e:
            logger.error(f"Dashboard error: {e}")
            return render_template('dashboard.html', 
                                 data={"error": f"Dashboard error: {e}"}, 
                                 config=config.to_dict())
    
    @app.route('/api/status')
    def api_status():
        """API endpoint for system status"""
        try:
            wf = get_workflow()
            status = wf.get_workflow_status()
            return jsonify({
                "success": True,
                "data": status,
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }), 500
    
    @app.route('/api/trigger-pipeline', methods=['POST'])
    def api_trigger_pipeline():
        """API endpoint to manually trigger content pipeline"""
        try:
            wf = get_workflow()
            
            # Check if workflow is already running
            status = wf.get_workflow_status()
            if status.get("current_status") not in ["idle", "completed", "failed"]:
                return jsonify({
                    "success": False,
                    "error": f"Workflow already running with status: {status.get('current_status')}",
                    "current_run_id": status.get("current_run_id")
                }), 400
            
            # Trigger pipeline
            result = wf.execute_pipeline(manual_trigger=True)
            
            if result.get("success"):
                system_logger.log_system_event(
                    "manual_pipeline_trigger",
                    "Pipeline manually triggered via web interface",
                    {"run_id": result.get("run_id"), "user_triggered": True}
                )
                
                return jsonify({
                    "success": True,
                    "data": result,
                    "message": "Content pipeline started successfully"
                })
            else:
                return jsonify({
                    "success": False,
                    "error": result.get("error", "Pipeline execution failed"),
                    "data": result
                }), 500
                
        except Exception as e:
            logger.error(f"Pipeline trigger error: {e}")
            return jsonify({
                "success": False,
                "error": f"Pipeline trigger error: {e}"
            }), 500
    
    @app.route('/api/workflow-history')
    def api_workflow_history():
        """API endpoint for workflow history"""
        try:
            wf = get_workflow()
            limit = request.args.get('limit', 50, type=int)
            history = wf.get_workflow_history(limit=limit)
            
            return jsonify({
                "success": True,
                "data": {
                    "history": history,
                    "count": len(history)
                },
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/agents-status')
    def api_agents_status():
        """API endpoint for individual agent status"""
        try:
            wf = get_workflow()
            
            agents_data = {}
            for agent_name, agent in wf.agents.items():
                try:
                    capabilities = agent.get_capabilities() if hasattr(agent, 'get_capabilities') else {}
                    agents_data[agent_name] = {
                        "name": agent.name if hasattr(agent, 'name') else agent_name,
                        "role": agent.role if hasattr(agent, 'role') else "Unknown",
                        "status": "active",
                        "capabilities": capabilities
                    }
                except Exception as e:
                    agents_data[agent_name] = {
                        "name": agent_name,
                        "status": "error",
                        "error": str(e)
                    }
            
            return jsonify({
                "success": True,
                "data": agents_data,
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/scheduler-status')
    def api_scheduler_status():
        """API endpoint for scheduler status"""
        try:
            wf = get_workflow()
            scheduler = wf.agents.get("scheduler")
            
            if not scheduler:
                return jsonify({
                    "success": False,
                    "error": "Scheduler agent not available"
                }), 404
            
            # Get scheduler status
            result = scheduler.execute_task({"task_type": "get_schedule"})
            
            return jsonify({
                "success": result.get("success", False),
                "data": result.get("data", {}),
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/cancel-scheduled/<job_id>', methods=['POST'])
    def api_cancel_scheduled(job_id):
        """API endpoint to cancel a scheduled post"""
        try:
            wf = get_workflow()
            scheduler = wf.agents.get("scheduler")
            
            if not scheduler:
                return jsonify({
                    "success": False,
                    "error": "Scheduler agent not available"
                }), 404
            
            result = scheduler.execute_task({
                "task_type": "cancel_scheduled",
                "job_id": job_id
            })
            
            if result.get("success"):
                system_logger.log_system_event(
                    "scheduled_post_cancelled",
                    f"Scheduled post cancelled via web interface",
                    {"job_id": job_id, "user_action": True}
                )
            
            return jsonify(result)
            
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/retry-failed', methods=['POST'])
    def api_retry_failed():
        """API endpoint to retry failed posts"""
        try:
            wf = get_workflow()
            scheduler = wf.agents.get("scheduler")
            
            if not scheduler:
                return jsonify({
                    "success": False,
                    "error": "Scheduler agent not available"
                }), 404
            
            result = scheduler.execute_task({"task_type": "retry_failed"})
            
            if result.get("success"):
                system_logger.log_system_event(
                    "failed_posts_retry",
                    "Failed posts retry triggered via web interface",
                    {"retry_count": result.get("data", {}).get("retried_count", 0)}
                )
            
            return jsonify(result)
            
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/system-config')
    def api_system_config():
        """API endpoint for system configuration"""
        try:
            return jsonify({
                "success": True,
                "data": config.to_dict(),
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/content-review')
    def content_review():
        """Content review page"""
        return render_template('content_review.html')
    
    @app.route('/roadmap-generator')
    def roadmap_generator():
        """AI Implementation Roadmap Generator page"""
        return render_template('roadmap_generator.html')

    @app.route('/api/publish-now', methods=['POST'])
    def api_publish_now():
        """API endpoint to publish content immediately"""
        try:
            data = request.get_json()
            job_id = data.get('job_id')
            
            if not job_id:
                return jsonify({
                    "success": False,
                    "error": "Job ID is required"
                }), 400
            
            wf = get_workflow()
            scheduler_agent = wf.agents.get('scheduler')
            
            if not scheduler_agent:
                return jsonify({
                    "success": False,
                    "error": "Scheduler agent not available"
                }), 500
            
            # Execute immediate publishing
            result = scheduler_agent.execute_scheduled_publishing(job_id)
            
            return jsonify({
                "success": True,
                "data": result
            })
            
        except Exception as e:
            logger.error(f"Publish now API error: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500

    @app.route('/api/update-content', methods=['POST'])
    def api_update_content():
        """API endpoint to update scheduled content"""
        try:
            data = request.get_json()
            job_id = data.get('job_id')
            updated_content = data.get('content')
            
            if not job_id or not updated_content:
                return jsonify({
                    "success": False,
                    "error": "Job ID and content are required"
                }), 400
            
            wf = get_workflow()
            scheduler_agent = wf.agents.get('scheduler')
            
            if not scheduler_agent:
                return jsonify({
                    "success": False,
                    "error": "Scheduler agent not available"
                }), 500
            
            # Update content in scheduler
            if hasattr(scheduler_agent, 'scheduled_posts') and job_id in scheduler_agent.scheduled_posts:
                post = scheduler_agent.scheduled_posts[job_id]
                post['content'].update(updated_content)
                
                # Recalculate reading time and word count
                text = updated_content.get('text', '')
                post['content']['word_count'] = len(text.split())
                post['content']['reading_time_seconds'] = max(30, len(text.split()) * 0.4)
                
                logger.info(f"Updated content for job {job_id}")
                
                return jsonify({
                    "success": True,
                    "data": {"message": "Content updated successfully"}
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "Scheduled post not found"
                }), 404
            
        except Exception as e:
            logger.error(f"Update content API error: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500

    @app.route('/api/metrics')
    def api_metrics():
        """API endpoint for system metrics"""
        try:
            wf = get_workflow()
            status = wf.get_workflow_status()
            
            # Calculate additional metrics
            recent_runs = wf.get_workflow_history(limit=100)
            
            # Performance metrics
            success_rate = 0
            if recent_runs:
                successful = len([r for r in recent_runs if r.get("success")])
                success_rate = (successful / len(recent_runs)) * 100
            
            # Time-based metrics
            now = datetime.utcnow()
            last_24h = now - timedelta(hours=24)
            last_week = now - timedelta(days=7)
            
            runs_24h = [
                r for r in recent_runs
                if datetime.fromisoformat(r.get("started_at", "1900-01-01")) > last_24h
            ]
            
            runs_week = [
                r for r in recent_runs
                if datetime.fromisoformat(r.get("started_at", "1900-01-01")) > last_week
            ]
            
            metrics = {
                "basic": status.get("metrics", {}),
                "performance": {
                    "success_rate": round(success_rate, 1),
                    "total_runs": len(recent_runs),
                    "runs_24h": len(runs_24h),
                    "runs_week": len(runs_week),
                    "successful_runs_24h": len([r for r in runs_24h if r.get("success")]),
                    "failed_runs_24h": len([r for r in runs_24h if not r.get("success")])
                },
                "system_health": status.get("system_health", {}),
                "last_updated": datetime.utcnow().isoformat()
            }
            
            return jsonify({
                "success": True,
                "data": metrics
            })
            
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/generate-roadmap', methods=['POST'])
    def api_generate_roadmap():
        """API endpoint to generate AI implementation roadmap"""
        try:
            workflow = get_workflow()
            if not workflow:
                return jsonify({"success": False, "error": "Workflow not initialized"}), 500
            
            roadmap_agent = workflow.agents.get('roadmap_generator')
            if not roadmap_agent:
                return jsonify({"success": False, "error": "Roadmap generator not available"}), 500
            
            # Get request data
            request_data = request.get_json()
            
            # Generate roadmap
            result = roadmap_agent.execute_task({
                "task_type": "generate_roadmap",
                "business_context": request_data.get("business_context", {}),
                "ai_objectives": request_data.get("ai_objectives", []),
                "timeline": request_data.get("timeline", "12 months"),
                "budget_range": request_data.get("budget_range", "moderate"),
                "industry": request_data.get("industry", "general"),
                "company_size": request_data.get("company_size", "medium")
            })
            
            return jsonify(result)
            
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/assess-readiness', methods=['POST'])
    def api_assess_readiness():
        """API endpoint to assess organizational readiness for AI"""
        try:
            workflow = get_workflow()
            if not workflow:
                return jsonify({"success": False, "error": "Workflow not initialized"}), 500
            
            roadmap_agent = workflow.agents.get('roadmap_generator')
            if not roadmap_agent:
                return jsonify({"success": False, "error": "Roadmap generator not available"}), 500
            
            # Get assessment data
            request_data = request.get_json()
            
            # Assess readiness
            result = roadmap_agent.execute_task({
                "task_type": "assess_readiness",
                **request_data
            })
            
            return jsonify(result)
            
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors"""
        return render_template('dashboard.html', 
                             data={"error": "Page not found"}, 
                             config=config.to_dict()), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors"""
        logger.error(f"Internal server error: {error}")
        return render_template('dashboard.html', 
                             data={"error": "Internal server error"}, 
                             config=config.to_dict()), 500
    
    # Set workflow instance (will be called by main app)
    def set_workflow(wf_instance):
        nonlocal workflow
        workflow = wf_instance
    
    app.set_workflow = set_workflow
    
    return app
