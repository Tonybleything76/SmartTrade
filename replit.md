# Multi-Agent AI Content Workflow System

## Overview

This is a sophisticated multi-agent AI system designed to autonomously generate and publish high-quality, brand-aligned LinkedIn posts based on trending topics in AI innovation. The system operates as a coordinated workflow where specialized AI agents collaborate to research trends, generate content, edit for quality, schedule posts, and distribute across social media platforms.

The system targets producing 3 high-quality LinkedIn posts daily at scheduled times (9am, 12pm, 5pm) covering topics including AI Innovation, Generative AI, Technology Roadmaps & Integration, AI for Professionals, and Agentic Systems.

## System Architecture

**Framework**: Python Flask-based web application with background task scheduling
**Agent Architecture**: Multi-agent system using specialized AI agents that communicate through a central hub
**Orchestration**: APScheduler for automated workflow execution and content publishing
**AI Integration**: OpenAI GPT-4 for content generation, editing, and trend analysis
**Web Interface**: Flask-based dashboard for monitoring and manual control

### Core Components:
- **Main Application** (`main.py`): System orchestrator and Flask app launcher
- **Workflow Engine** (`workflow.py`): Central pipeline coordinator managing agent interactions
- **Web Interface** (`web_interface.py`): Dashboard for monitoring and manual controls
- **Agent Framework** (`agents/`): Specialized AI agents for different tasks
- **Utilities** (`utils/`): Configuration management and logging

## Key Components

### Agent System
The system employs 6 specialized AI agents, each with distinct roles:

1. **Orchestration Agent**: Chief Content Officer managing workflow coordination and content validation
2. **Trend Researcher Agent**: AI Trends Analyst identifying trending topics from web sources
3. **Content Developer Agent**: AI-Powered Copywriter generating branded LinkedIn posts
4. **Content Editor Agent**: Fact Checker/Brand Editor ensuring quality and brand alignment
5. **Distribution Agent**: Platform Publisher handling multi-platform content distribution
6. **Scheduler Agent**: Automation Specialist managing content scheduling and publishing

### Web Dashboard
- Real-time system status monitoring
- Manual workflow trigger capabilities
- Content queue management
- Performance metrics and analytics
- Historical workflow tracking

### Configuration Management
- Environment-based configuration using dataclasses
- API key management for OpenAI, LinkedIn, and X (Twitter)
- Content generation parameters and brand guidelines
- Scheduling and publishing preferences

## Data Flow

1. **Initialization**: System validates API keys and initializes all agents
2. **Trend Research**: Researcher agent scrapes AI news sources and identifies trending topics
3. **Content Generation**: Developer agent creates branded LinkedIn posts using GPT-4
4. **Content Review**: Editor agent validates content for quality, accuracy, and brand alignment
5. **Scheduling**: Scheduler agent queues approved content for automated publishing
6. **Distribution**: Distribution agent publishes content to LinkedIn and other platforms
7. **Monitoring**: Web interface provides real-time status and historical analytics

The workflow supports both automated daily execution and manual triggering through the web interface.

## External Dependencies

### Required APIs:
- **OpenAI API**: GPT-4 for content generation, editing, and trend analysis
- **LinkedIn API**: Content publishing and engagement tracking
- **X (Twitter) API**: Optional secondary platform distribution

### Python Packages:
- **Flask**: Web framework for dashboard interface
- **APScheduler**: Background task scheduling and cron jobs
- **OpenAI**: Official OpenAI API client
- **Requests**: HTTP client for web scraping and API calls
- **Trafilatura**: Web content extraction and text processing

### Web Scraping Sources:
- AI news websites (VentureBeat, TechCrunch, AI Magazine)
- Academic sources (ArXiv AI and ML papers)
- Industry blogs (OpenAI, Google AI, Microsoft AI, Anthropic)

## Deployment Strategy

**Platform**: Replit with Python 3.11 runtime
**Process Management**: Single Python process handling both Flask web server and background scheduling
**Port Configuration**: Flask app runs on port 5000
**Environment Variables**: API keys and configuration managed through Replit secrets
**Persistence**: In-memory state management with JSON logging for workflow history

The system is designed to run continuously, with the scheduler managing automated content generation and the Flask interface providing real-time monitoring and manual control capabilities.

## Changelog

```
Changelog:
- June 13, 2025. Initial setup
- June 13, 2025. Updated to use SerpAPI instead of trafilatura for trend research
- June 13, 2025. Made LinkedIn credentials optional for testing
- June 13, 2025. System running with 6 AI agents initialized
- June 13, 2025. Successfully completed full pipeline test with authentic data
- June 13, 2025. Generated 3 professional LinkedIn posts from 271 real trending topics
- June 13, 2025. Added comprehensive content review interface with manual posting controls
- June 13, 2025. Updated content format to Rich Text Format with specific CTA for The AI Ready Professional course
- June 13, 2025. Refined trend research to focus on consulting business areas: business optimization, AI innovation strategy, AI implementation, workshop design, Design Thinking, and AI tool development
```

## User Preferences

```
Preferred communication style: Simple, everyday language.
API priorities: Focus on OpenAI and SerpAPI first, hold on X/Twitter integration for now.
Publishing approach: LinkedIn optional for testing, X/Twitter postponed.
Content format: Rich Text Format (RTF), not markdown.
Call-to-action: All posts must include enrollment CTA for "The AI Ready Professional" course.
Course link: https://adeptly.thinkific.com/products/courses/ai-ready-professional-course
```