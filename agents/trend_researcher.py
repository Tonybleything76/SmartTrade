"""
Trend Researcher Agent
AI Trends Analyst
Identifies and analyzes trending AI topics from multiple sources
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, List
import trafilatura

from agents.base_agent import BaseAgent
from openai import OpenAI

class TrendResearcherAgent(BaseAgent):
    """Researches trending AI topics from various online sources"""
    
    def __init__(self):
        super().__init__(
            name="Trend Researcher Agent", 
            role="AI Trends Analyst",
            tools=["web_scraping", "rss_feeds", "openai_analysis", "trend_ranking"]
        )
        
        # Initialize OpenAI client
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Research sources configuration
        self.research_sources = {
            "ai_news_sites": [
                "https://venturebeat.com/ai/",
                "https://techcrunch.com/category/artificial-intelligence/",
                "https://www.artificialintelligence-news.com/",
                "https://aimagazine.com/",
                "https://www.theverge.com/ai-artificial-intelligence"
            ],
            "academic_sources": [
                "https://arxiv.org/list/cs.AI/recent",
                "https://arxiv.org/list/cs.LG/recent"
            ],
            "industry_blogs": [
                "https://openai.com/blog/",
                "https://blog.google/technology/ai/",
                "https://blogs.microsoft.com/ai/",
                "https://www.anthropic.com/news"
            ]
        }
        
        # Topic categories for filtering
        self.topic_categories = [
            "AI Innovation",
            "Generative AI",
            "Technology Roadmaps & Integration", 
            "AI for Professionals",
            "Agentic Systems",
            "Machine Learning",
            "Neural Networks",
            "AI Ethics"
        ]
    
    def execute_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute trend research task"""
        task_type = task_data.get("task_type", "research_trends")
        
        if task_type == "research_trends":
            topics = task_data.get("topics", self.topic_categories)
            max_trends = task_data.get("max_trends", 10)
            return self.research_trending_topics(topics, max_trends)
        elif task_type == "analyze_topic":
            topic = task_data.get("topic")
            return self.analyze_single_topic(topic)
        else:
            return self.create_response(False, error=f"Unknown task type: {task_type}")
    
    def research_trending_topics(self, topics: List[str], max_trends: int = 10) -> Dict[str, Any]:
        """Research trending topics across multiple sources"""
        self.log_message(f"Starting trend research for {len(topics)} topic categories")
        
        try:
            all_trends = []
            
            # Scrape content from different source categories
            for source_type, urls in self.research_sources.items():
                self.log_message(f"Researching {source_type} sources...")
                
                trends_from_source = self.scrape_source_category(urls, topics, source_type)
                all_trends.extend(trends_from_source)
            
            if not all_trends:
                return self.create_response(False, error="No trends found from any sources")
            
            # Rank and filter trends
            ranked_trends = self.rank_trends(all_trends, max_trends)
            
            # Enhance trends with AI analysis
            enhanced_trends = self.enhance_trends_with_ai(ranked_trends)
            
            return self.create_response(True, {
                "trends": enhanced_trends,
                "total_found": len(all_trends),
                "sources_checked": sum(len(urls) for urls in self.research_sources.values()),
                "research_timestamp": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            self.log_message(f"Trend research failed: {e}", level="error")
            return self.create_response(False, error=f"Trend research failed: {e}")
    
    def scrape_source_category(self, urls: List[str], topics: List[str], source_type: str) -> List[Dict[str, Any]]:
        """Scrape content from a category of sources"""
        trends = []
        
        for url in urls:
            try:
                self.log_message(f"Scraping {url}")
                
                # Get website content using trafilatura
                downloaded = trafilatura.fetch_url(url)
                if not downloaded:
                    continue
                    
                text_content = trafilatura.extract(downloaded)
                if not text_content:
                    continue
                
                # Extract trends from content using AI
                extracted_trends = self.extract_trends_from_content(text_content, topics, url, source_type)
                trends.extend(extracted_trends)
                
            except Exception as e:
                self.log_message(f"Failed to scrape {url}: {e}", level="warning")
                continue
        
        return trends
    
    def extract_trends_from_content(self, content: str, topics: List[str], source_url: str, source_type: str) -> List[Dict[str, Any]]:
        """Extract trending topics from scraped content using AI"""
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            prompt = f"""
            Analyze the following content and identify trending AI topics that match these categories: {', '.join(topics)}.
            
            For each trend found, provide:
            1. Title (concise, engaging)
            2. Summary (2-3 sentences)
            3. Category (from the provided list)
            4. Relevance score (1-10)
            5. Key insights or developments
            
            Content to analyze:
            {content[:4000]}  # Limit content length
            
            Respond with JSON in this format:
            {{"trends": [
                {{
                    "title": "Trend title",
                    "summary": "Brief summary",
                    "category": "Category name",
                    "relevance_score": 8,
                    "key_insights": ["insight1", "insight2"],
                    "keywords": ["keyword1", "keyword2"]
                }}
            ]}}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                max_tokens=1500
            )
            
            result = json.loads(response.choices[0].message.content)
            trends = result.get("trends", [])
            
            # Add source metadata to trends
            for trend in trends:
                trend.update({
                    "source_url": source_url,
                    "source_type": source_type,
                    "discovered_at": datetime.utcnow().isoformat()
                })
            
            return trends
            
        except Exception as e:
            self.log_message(f"AI trend extraction failed: {e}", level="warning")
            return []
    
    def rank_trends(self, trends: List[Dict[str, Any]], max_trends: int) -> List[Dict[str, Any]]:
        """Rank trends by relevance, novelty, and engagement potential"""
        try:
            # Calculate composite score for each trend
            for trend in trends:
                relevance_score = trend.get("relevance_score", 5)
                
                # Bonus for recent discoveries
                discovered_time = datetime.fromisoformat(trend.get("discovered_at", datetime.utcnow().isoformat()))
                hours_since_discovery = (datetime.utcnow() - discovered_time).total_seconds() / 3600
                recency_bonus = max(0, 5 - (hours_since_discovery / 24))  # Decay over days
                
                # Bonus for high-authority sources
                source_bonus = 2 if trend.get("source_type") == "academic_sources" else 1
                
                # Calculate final score
                trend["composite_score"] = relevance_score + recency_bonus + source_bonus
            
            # Sort by composite score and return top trends
            sorted_trends = sorted(trends, key=lambda x: x.get("composite_score", 0), reverse=True)
            
            return sorted_trends[:max_trends]
            
        except Exception as e:
            self.log_message(f"Trend ranking failed: {e}", level="warning")
            return trends[:max_trends]
    
    def enhance_trends_with_ai(self, trends: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enhance trends with additional AI analysis"""
        enhanced_trends = []
        
        for trend in trends:
            try:
                # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
                # do not change this unless explicitly requested by the user
                enhancement_prompt = f"""
                Enhance this AI trend analysis with additional insights:
                
                Title: {trend.get('title', '')}
                Summary: {trend.get('summary', '')}
                Category: {trend.get('category', '')}
                
                Provide:
                1. Professional implications (how this affects AI professionals)
                2. Business impact (potential business applications)
                3. Future outlook (what this might lead to)
                4. Content angles (3 interesting angles for LinkedIn posts)
                
                Respond with JSON:
                {{
                    "professional_implications": "text",
                    "business_impact": "text", 
                    "future_outlook": "text",
                    "content_angles": ["angle1", "angle2", "angle3"]
                }}
                """
                
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": enhancement_prompt}],
                    response_format={"type": "json_object"},
                    max_tokens=800
                )
                
                enhancement = json.loads(response.choices[0].message.content)
                
                # Merge enhancement with original trend
                enhanced_trend = {**trend, **enhancement}
                enhanced_trends.append(enhanced_trend)
                
            except Exception as e:
                self.log_message(f"Trend enhancement failed for {trend.get('title', 'Unknown')}: {e}", level="warning")
                enhanced_trends.append(trend)  # Use original if enhancement fails
        
        return enhanced_trends
    
    def analyze_single_topic(self, topic: str) -> Dict[str, Any]:
        """Perform deep analysis on a single topic"""
        if not topic:
            return self.create_response(False, error="No topic provided for analysis")
        
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            analysis_prompt = f"""
            Perform a comprehensive analysis of this AI topic: {topic}
            
            Provide:
            1. Current state and recent developments
            2. Key players and technologies involved
            3. Market implications and opportunities
            4. Technical challenges and solutions
            5. Timeline and future predictions
            6. Related topics and connections
            
            Respond with detailed JSON analysis.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": analysis_prompt}],
                response_format={"type": "json_object"},
                max_tokens=2000
            )
            
            analysis = json.loads(response.choices[0].message.content)
            
            return self.create_response(True, {
                "topic": topic,
                "analysis": analysis,
                "analyzed_at": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            return self.create_response(False, error=f"Topic analysis failed: {e}")
