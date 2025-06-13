"""
Scheduler Agent
Automation Specialist / Calendar Coordinator
Manages content scheduling and automated publishing
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from agents.base_agent import BaseAgent

class SchedulerAgent(BaseAgent):
    """Manages content scheduling and automated distribution"""
    
    def __init__(self):
        super().__init__(
            name="Scheduler Agent",
            role="Automation Specialist / Calendar Coordinator",
            tools=["apscheduler", "content_queue", "timezone_handling", "conflict_detection"]
        )
        
        # Initialize scheduler
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        
        # Schedule configuration
        self.schedule_config = {
            "daily_times": ["09:00", "12:00", "17:00"],  # 9 AM, 12 PM, 5 PM
            "timezone": "UTC",
            "max_queue_size": 50,
            "retry_attempts": 3,
            "retry_delay_minutes": 30
        }
        
        # Content queue management
        self.content_queue = []
        self.scheduled_posts = {}
        self.failed_posts = []
        self.publishing_history = []
    
    def execute_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute scheduling task"""
        task_type = task_data.get("task_type", "schedule_content")
        
        if task_type == "schedule_content":
            content = task_data.get("content")
            schedule_time = task_data.get("schedule_time")
            return self.schedule_content(content, schedule_time)
        elif task_type == "get_schedule":
            return self.get_current_schedule()
        elif task_type == "cancel_scheduled":
            job_id = task_data.get("job_id")
            return self.cancel_scheduled_post(job_id)
        elif task_type == "retry_failed":
            return self.retry_failed_posts()
        else:
            return self.create_response(False, error=f"Unknown task type: {task_type}")
    
    def schedule_content(self, content: Dict[str, Any], schedule_time: str = None) -> Dict[str, Any]:
        """Schedule content for publishing"""
        if not content:
            return self.create_response(False, error="No content provided for scheduling")
        
        try:
            # Generate unique job ID
            import uuid
            job_id = str(uuid.uuid4())
            
            # Determine schedule time
            if schedule_time:
                # Use provided time
                try:
                    publish_time = datetime.fromisoformat(schedule_time.replace('Z', '+00:00'))
                except ValueError:
                    return self.create_response(False, error=f"Invalid schedule time format: {schedule_time}")
            else:
                # Find next available slot
                publish_time = self.find_next_available_slot()
            
            # Check for conflicts
            conflict_check = self.check_scheduling_conflicts(publish_time)
            if not conflict_check.get("available"):
                return self.create_response(False, error=f"Scheduling conflict: {conflict_check.get('reason')}")
            
            # Add to content queue
            queued_content = {
                "job_id": job_id,
                "content": content,
                "scheduled_time": publish_time.isoformat(),
                "status": "scheduled",
                "created_at": datetime.utcnow().isoformat(),
                "retry_count": 0,
                "platforms": content.get("platforms", ["linkedin"])
            }
            
            self.content_queue.append(queued_content)
            
            # Schedule the job
            self.scheduler.add_job(
                self.execute_scheduled_publishing,
                trigger=CronTrigger.from_crontab(f"{publish_time.minute} {publish_time.hour} {publish_time.day} {publish_time.month} *"),
                id=job_id,
                name=f"Publish content at {publish_time.strftime('%Y-%m-%d %H:%M')}",
                args=[job_id],
                replace_existing=True
            )
            
            self.scheduled_posts[job_id] = queued_content
            
            self.log_message(f"Content scheduled for {publish_time.isoformat()}", metadata={"job_id": job_id})
            
            return self.create_response(True, {
                "job_id": job_id,
                "scheduled_time": publish_time.isoformat(),
                "status": "scheduled",
                "queue_position": len(self.content_queue),
                "estimated_publish_time": publish_time.strftime("%Y-%m-%d %H:%M UTC")
            })
            
        except Exception as e:
            self.log_message(f"Content scheduling failed: {e}", level="error")
            return self.create_response(False, error=f"Content scheduling failed: {e}")
    
    def find_next_available_slot(self) -> datetime:
        """Find the next available publishing slot"""
        now = datetime.utcnow()
        today = now.date()
        
        # Check today's remaining slots
        for time_str in self.schedule_config["daily_times"]:
            hour, minute = map(int, time_str.split(':'))
            slot_time = datetime.combine(today, datetime.min.time().replace(hour=hour, minute=minute))
            
            # If slot is in the future and not taken
            if slot_time > now and not self.is_slot_occupied(slot_time):
                return slot_time
        
        # Check tomorrow's slots
        tomorrow = today + timedelta(days=1)
        for time_str in self.schedule_config["daily_times"]:
            hour, minute = map(int, time_str.split(':'))
            slot_time = datetime.combine(tomorrow, datetime.min.time().replace(hour=hour, minute=minute))
            
            if not self.is_slot_occupied(slot_time):
                return slot_time
        
        # If all slots are taken, find the earliest free slot after tomorrow
        check_date = tomorrow + timedelta(days=1)
        for _ in range(7):  # Check up to a week ahead
            for time_str in self.schedule_config["daily_times"]:
                hour, minute = map(int, time_str.split(':'))
                slot_time = datetime.combine(check_date, datetime.min.time().replace(hour=hour, minute=minute))
                
                if not self.is_slot_occupied(slot_time):
                    return slot_time
            
            check_date += timedelta(days=1)
        
        # Fallback: schedule for next hour
        return now + timedelta(hours=1)
    
    def is_slot_occupied(self, slot_time: datetime) -> bool:
        """Check if a time slot is already occupied"""
        slot_window = timedelta(minutes=30)  # 30-minute window around each slot
        
        for content in self.content_queue:
            if content.get("status") != "scheduled":
                continue
                
            scheduled_time = datetime.fromisoformat(content["scheduled_time"])
            time_diff = abs(scheduled_time - slot_time)
            
            if time_diff < slot_window:
                return True
        
        return False
    
    def check_scheduling_conflicts(self, publish_time: datetime) -> Dict[str, Any]:
        """Check for scheduling conflicts"""
        try:
            # Check if time is in the past
            if publish_time <= datetime.utcnow():
                return {"available": False, "reason": "Cannot schedule content in the past"}
            
            # Check if slot is occupied
            if self.is_slot_occupied(publish_time):
                return {"available": False, "reason": "Time slot already occupied"}
            
            # Check if too far in the future (more than 30 days)
            if publish_time > datetime.utcnow() + timedelta(days=30):
                return {"available": False, "reason": "Cannot schedule more than 30 days in advance"}
            
            # Check queue capacity
            if len(self.content_queue) >= self.schedule_config["max_queue_size"]:
                return {"available": False, "reason": "Content queue is full"}
            
            return {"available": True, "reason": "Slot available"}
            
        except Exception as e:
            return {"available": False, "reason": f"Conflict check failed: {e}"}
    
    def execute_scheduled_publishing(self, job_id: str):
        """Execute scheduled content publishing"""
        try:
            self.log_message(f"Executing scheduled publishing for job {job_id}")
            
            # Find the content to publish
            content_item = None
            for content in self.content_queue:
                if content.get("job_id") == job_id:
                    content_item = content
                    break
            
            if not content_item:
                self.log_message(f"Content not found for job {job_id}", level="error")
                return
            
            # Update status
            content_item["status"] = "publishing"
            content_item["publishing_started_at"] = datetime.utcnow().isoformat()
            
            # Execute publishing via Distribution Agent
            publishing_result = self.execute_publishing(content_item)
            
            if publishing_result.get("success"):
                # Publishing successful
                content_item["status"] = "published"
                content_item["published_at"] = datetime.utcnow().isoformat()
                content_item["publishing_results"] = publishing_result.get("data", {})
                
                # Move to history
                self.publishing_history.append(content_item)
                self.content_queue = [c for c in self.content_queue if c.get("job_id") != job_id]
                
                if job_id in self.scheduled_posts:
                    del self.scheduled_posts[job_id]
                
                self.log_message(f"Content published successfully: {job_id}")
                
            else:
                # Publishing failed
                self.handle_publishing_failure(content_item, publishing_result.get("error", "Unknown error"))
                
        except Exception as e:
            self.log_message(f"Scheduled publishing execution failed for {job_id}: {e}", level="error")
            # Handle as failed publishing
            if 'content_item' in locals():
                self.handle_publishing_failure(content_item, str(e))
    
    def execute_publishing(self, content_item: Dict[str, Any]) -> Dict[str, Any]:
        """Execute publishing through Distribution Agent"""
        try:
            from agents.distribution import DistributionAgent
            
            distributor = DistributionAgent()
            
            task_data = {
                "task_type": "publish_content",
                "content": content_item.get("content"),
                "platforms": content_item.get("platforms", ["linkedin"])
            }
            
            return distributor.execute_task(task_data)
            
        except Exception as e:
            self.log_message(f"Publishing execution failed: {e}", level="error")
            return self.create_response(False, error=f"Publishing execution failed: {e}")
    
    def handle_publishing_failure(self, content_item: Dict[str, Any], error: str):
        """Handle failed publishing attempts"""
        content_item["status"] = "failed"
        content_item["last_error"] = error
        content_item["failed_at"] = datetime.utcnow().isoformat()
        content_item["retry_count"] = content_item.get("retry_count", 0) + 1
        
        max_retries = self.schedule_config["retry_attempts"]
        
        if content_item["retry_count"] < max_retries:
            # Schedule retry
            retry_time = datetime.utcnow() + timedelta(minutes=self.schedule_config["retry_delay_minutes"])
            
            try:
                retry_job_id = f"{content_item['job_id']}_retry_{content_item['retry_count']}"
                
                self.scheduler.add_job(
                    self.execute_scheduled_publishing,
                    trigger=CronTrigger.from_crontab(f"{retry_time.minute} {retry_time.hour} {retry_time.day} {retry_time.month} *"),
                    id=retry_job_id,
                    name=f"Retry publishing {content_item['job_id']}",
                    args=[content_item['job_id']],
                    replace_existing=True
                )
                
                content_item["status"] = "retry_scheduled"
                content_item["retry_scheduled_for"] = retry_time.isoformat()
                
                self.log_message(f"Retry scheduled for {content_item['job_id']} at {retry_time.isoformat()}")
                
            except Exception as e:
                self.log_message(f"Failed to schedule retry: {e}", level="error")
                self.failed_posts.append(content_item)
        else:
            # Max retries exceeded
            self.failed_posts.append(content_item)
            self.content_queue = [c for c in self.content_queue if c.get("job_id") != content_item.get("job_id")]
            
            job_id = content_item.get("job_id")
            if job_id in self.scheduled_posts:
                del self.scheduled_posts[job_id]
            
            self.log_message(f"Content publishing failed permanently: {job_id}", level="error")
    
    def get_current_schedule(self) -> Dict[str, Any]:
        """Get current scheduling status and queue"""
        try:
            # Get scheduled jobs from APScheduler
            scheduled_jobs = []
            for job in self.scheduler.get_jobs():
                scheduled_jobs.append({
                    "job_id": job.id,
                    "name": job.name,
                    "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                    "trigger": str(job.trigger)
                })
            
            # Calculate queue statistics
            queue_stats = {
                "total_queued": len(self.content_queue),
                "scheduled": len([c for c in self.content_queue if c.get("status") == "scheduled"]),
                "publishing": len([c for c in self.content_queue if c.get("status") == "publishing"]),
                "retry_scheduled": len([c for c in self.content_queue if c.get("status") == "retry_scheduled"]),
                "failed": len(self.failed_posts),
                "published_today": len([
                    h for h in self.publishing_history 
                    if datetime.fromisoformat(h.get("published_at", "1900-01-01")).date() == datetime.utcnow().date()
                ])
            }
            
            # Next scheduled posts
            next_posts = sorted(
                [c for c in self.content_queue if c.get("status") == "scheduled"],
                key=lambda x: x.get("scheduled_time", "")
            )[:5]
            
            return self.create_response(True, {
                "schedule_config": self.schedule_config,
                "queue_statistics": queue_stats,
                "scheduled_jobs": scheduled_jobs,
                "next_posts": next_posts,
                "failed_posts": self.failed_posts[-10:],  # Last 10 failed posts
                "recent_published": self.publishing_history[-10:],  # Last 10 published
                "scheduler_status": "running" if self.scheduler.running else "stopped"
            })
            
        except Exception as e:
            return self.create_response(False, error=f"Failed to get schedule: {e}")
    
    def cancel_scheduled_post(self, job_id: str) -> Dict[str, Any]:
        """Cancel a scheduled post"""
        if not job_id:
            return self.create_response(False, error="No job ID provided")
        
        try:
            # Remove from scheduler
            try:
                self.scheduler.remove_job(job_id)
                scheduler_removed = True
            except:
                scheduler_removed = False
            
            # Remove from queue
            original_queue_size = len(self.content_queue)
            self.content_queue = [c for c in self.content_queue if c.get("job_id") != job_id]
            queue_removed = len(self.content_queue) < original_queue_size
            
            # Remove from scheduled posts
            scheduled_removed = False
            if job_id in self.scheduled_posts:
                del self.scheduled_posts[job_id]
                scheduled_removed = True
            
            if scheduler_removed or queue_removed or scheduled_removed:
                self.log_message(f"Scheduled post cancelled: {job_id}")
                return self.create_response(True, {
                    "job_id": job_id,
                    "cancelled_at": datetime.utcnow().isoformat(),
                    "removed_from_scheduler": scheduler_removed,
                    "removed_from_queue": queue_removed,
                    "removed_from_scheduled": scheduled_removed
                })
            else:
                return self.create_response(False, error=f"Job {job_id} not found in any scheduling system")
                
        except Exception as e:
            return self.create_response(False, error=f"Failed to cancel scheduled post: {e}")
    
    def retry_failed_posts(self) -> Dict[str, Any]:
        """Retry all failed posts"""
        if not self.failed_posts:
            return self.create_response(True, {"message": "No failed posts to retry"})
        
        try:
            retry_count = 0
            retry_results = []
            
            for failed_post in self.failed_posts.copy():
                # Reset retry count and status
                failed_post["retry_count"] = 0
                failed_post["status"] = "scheduled"
                
                # Find next available slot
                next_slot = self.find_next_available_slot()
                failed_post["scheduled_time"] = next_slot.isoformat()
                
                # Add back to queue
                self.content_queue.append(failed_post)
                
                # Reschedule
                job_id = failed_post.get("job_id")
                self.scheduler.add_job(
                    self.execute_scheduled_publishing,
                    trigger=CronTrigger.from_crontab(f"{next_slot.minute} {next_slot.hour} {next_slot.day} {next_slot.month} *"),
                    id=f"{job_id}_manual_retry",
                    name=f"Manual retry: {job_id}",
                    args=[job_id],
                    replace_existing=True
                )
                
                retry_results.append({
                    "job_id": job_id,
                    "rescheduled_for": next_slot.isoformat()
                })
                
                retry_count += 1
            
            # Clear failed posts list
            self.failed_posts.clear()
            
            return self.create_response(True, {
                "retried_count": retry_count,
                "retry_results": retry_results,
                "retried_at": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            return self.create_response(False, error=f"Failed to retry posts: {e}")
