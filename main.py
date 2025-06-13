#!/usr/bin/env python3
"""
Multi-Agent AI Content Workflow System
Main application entry point
"""

import os
import threading
import time
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from flask import Flask

from workflow import ContentWorkflow
from web_interface import create_app
from utils.logger import setup_logger
from utils.config import Config

logger = setup_logger(__name__)

class MultiAgentContentSystem:
    """Main system orchestrator for the multi-agent content pipeline"""
    
    def __init__(self):
        self.config = Config()
        self.workflow = ContentWorkflow()
        self.scheduler = BackgroundScheduler()
        self.flask_app = create_app()
        
    def initialize(self):
        """Initialize the system components"""
        try:
            logger.info("Initializing Multi-Agent Content System...")
            
            # Validate required environment variables
            required_vars = ['OPENAI_API_KEY', 'LINKEDIN_ACCESS_TOKEN']
            missing_vars = [var for var in required_vars if not os.getenv(var)]
            
            if missing_vars:
                logger.error(f"Missing required environment variables: {missing_vars}")
                return False
                
            # Initialize workflow
            if not self.workflow.initialize():
                logger.error("Failed to initialize workflow")
                return False
                
            # Setup scheduled jobs
            self.setup_scheduler()
            
            logger.info("System initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize system: {e}")
            return False
    
    def setup_scheduler(self):
        """Setup scheduled content generation jobs"""
        try:
            # Schedule content generation for 9 AM, 12 PM, and 5 PM daily
            times = ['09:00', '12:00', '17:00']
            
            for time_str in times:
                hour, minute = map(int, time_str.split(':'))
                
                self.scheduler.add_job(
                    self.run_content_pipeline,
                    CronTrigger(hour=hour, minute=minute),
                    id=f'content_generation_{time_str}',
                    name=f'Content Generation {time_str}',
                    replace_existing=True
                )
            
            # Add a manual trigger job that runs every 5 minutes to check for manual requests
            self.scheduler.add_job(
                self.check_manual_requests,
                CronTrigger(minute='*/5'),
                id='manual_check',
                name='Manual Request Check',
                replace_existing=True
            )
            
            self.scheduler.start()
            logger.info("Scheduler setup complete")
            
        except Exception as e:
            logger.error(f"Failed to setup scheduler: {e}")
    
    def run_content_pipeline(self):
        """Execute the full content generation pipeline"""
        try:
            logger.info("Starting scheduled content pipeline...")
            
            # Run the workflow
            results = self.workflow.execute_pipeline()
            
            if results and results.get('success'):
                logger.info(f"Pipeline completed successfully. Generated {len(results.get('posts', []))} posts")
            else:
                logger.error(f"Pipeline failed: {results.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Content pipeline execution failed: {e}")
    
    def check_manual_requests(self):
        """Check for manual content generation requests"""
        try:
            # Check if there are any manual requests in the workflow queue
            if hasattr(self.workflow, 'has_manual_requests') and self.workflow.has_manual_requests():
                logger.info("Processing manual content generation request...")
                self.run_content_pipeline()
        except Exception as e:
            logger.error(f"Error checking manual requests: {e}")
    
    def run_web_interface(self):
        """Start the Flask web interface"""
        try:
            logger.info("Starting web interface on port 5000...")
            self.flask_app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
        except Exception as e:
            logger.error(f"Web interface failed: {e}")
    
    def start(self):
        """Start the complete system"""
        if not self.initialize():
            logger.error("System initialization failed. Exiting.")
            return
        
        try:
            # Start web interface in a separate thread
            web_thread = threading.Thread(target=self.run_web_interface, daemon=True)
            web_thread.start()
            
            logger.info("Multi-Agent Content System is running...")
            logger.info("Web interface available at http://localhost:5000")
            logger.info("Scheduled posts at 9 AM, 12 PM, and 5 PM daily")
            
            # Keep the main thread alive
            while True:
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            logger.info("Shutting down system...")
            self.scheduler.shutdown()
        except Exception as e:
            logger.error(f"System error: {e}")
            self.scheduler.shutdown()

if __name__ == "__main__":
    system = MultiAgentContentSystem()
    system.start()
