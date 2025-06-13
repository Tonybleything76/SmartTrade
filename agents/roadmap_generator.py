"""
AI Implementation Roadmap Generator Agent
Strategic Planning Specialist / AI Transformation Architect
Creates comprehensive AI implementation roadmaps for business transformation
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from openai import OpenAI
from .base_agent import BaseAgent

class RoadmapGeneratorAgent(BaseAgent):
    """Generates strategic AI implementation roadmaps for business transformation"""
    
    def __init__(self):
        super().__init__(
            name="Roadmap Generator Agent",
            role="Strategic Planning Specialist / AI Transformation Architect",
            tools=["openai_api", "strategic_analysis", "roadmap_generation"]
        )
        
        # OpenAI client initialization
        self.openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
        # Roadmap framework components
        self.roadmap_frameworks = {
            "business_optimization": {
                "phases": ["Assessment", "Quick Wins", "Core Implementation", "Advanced Integration", "Continuous Optimization"],
                "focus_areas": ["Process Automation", "Data Analytics", "Decision Support", "Customer Experience", "Operational Efficiency"],
                "timeline": "6-18 months"
            },
            "ai_innovation_strategy": {
                "phases": ["Vision & Strategy", "Proof of Concept", "Pilot Programs", "Scale & Deploy", "Innovation Culture"],
                "focus_areas": ["Strategic Alignment", "Technology Selection", "Talent Development", "Innovation Framework", "Market Positioning"],
                "timeline": "12-24 months"
            },
            "ai_implementation": {
                "phases": ["Planning & Preparation", "Foundation Building", "System Integration", "Testing & Validation", "Deployment & Monitoring"],
                "focus_areas": ["Infrastructure Setup", "Data Preparation", "Model Development", "Integration Testing", "Performance Monitoring"],
                "timeline": "3-12 months"
            }
        }
        
        # Implementation methodologies
        self.methodologies = {
            "agile_ai": "Iterative development with rapid prototyping and continuous feedback",
            "design_thinking": "Human-centered approach focusing on user needs and experience",
            "lean_startup": "Build-measure-learn approach with minimum viable products",
            "waterfall": "Sequential approach with detailed planning and documentation"
        }
        
        # Risk assessment categories
        self.risk_categories = [
            "Technical Complexity",
            "Data Quality & Availability", 
            "Organizational Readiness",
            "Budget & Resource Constraints",
            "Regulatory Compliance",
            "Change Management",
            "Technology Integration",
            "Skills & Training Gaps"
        ]
    
    def execute_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute roadmap generation task"""
        try:
            task_type = task_data.get("task_type", "generate_roadmap")
            
            if task_type == "generate_roadmap":
                return self.generate_implementation_roadmap(task_data)
            elif task_type == "assess_readiness":
                return self.assess_organizational_readiness(task_data)
            elif task_type == "customize_roadmap":
                return self.customize_roadmap_for_industry(task_data)
            else:
                return self.create_response(False, error=f"Unknown task type: {task_type}")
                
        except Exception as e:
            self.log_message(f"Error executing roadmap generation task: {str(e)}", "error")
            return self.create_response(False, error=str(e))
    
    def generate_implementation_roadmap(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive AI implementation roadmap"""
        try:
            # Extract requirements
            business_context = requirements.get("business_context", {})
            ai_objectives = requirements.get("ai_objectives", [])
            timeline_preference = requirements.get("timeline", "12 months")
            budget_range = requirements.get("budget_range", "moderate")
            industry = requirements.get("industry", "general")
            company_size = requirements.get("company_size", "medium")
            
            # Determine primary framework
            primary_framework = self.select_roadmap_framework(ai_objectives, business_context)
            
            # Generate roadmap using AI
            roadmap_data = self.generate_ai_roadmap(
                business_context, ai_objectives, timeline_preference, 
                budget_range, industry, company_size, primary_framework
            )
            
            # Add implementation details
            detailed_roadmap = self.add_implementation_details(roadmap_data, primary_framework)
            
            # Generate risk assessment
            risk_assessment = self.generate_risk_assessment(business_context, ai_objectives)
            
            # Create final roadmap structure
            complete_roadmap = {
                "roadmap_id": f"roadmap_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "generated_at": datetime.now().isoformat(),
                "business_context": business_context,
                "objectives": ai_objectives,
                "framework": primary_framework,
                "timeline": timeline_preference,
                "phases": roadmap_data.get("phases", []),
                "milestones": roadmap_data.get("milestones", []),
                "deliverables": self.extract_deliverables_from_phases(roadmap_data.get("phases", [])),
                "resource_requirements": roadmap_data.get("resources", {}),
                "risk_assessment": risk_assessment,
                "success_metrics": roadmap_data.get("success_metrics", []),
                "recommendations": roadmap_data.get("recommendations", []),
                "workshops": detailed_roadmap.get("workshops", []),
                "design_thinking_integration": detailed_roadmap.get("design_thinking_integration", []),
                "methodology": detailed_roadmap.get("methodology", {})
            }
            
            self.log_message(f"Generated AI implementation roadmap with {len(complete_roadmap['phases'])} phases")
            
            return self.create_response(True, {
                "roadmap": complete_roadmap,
                "summary": self.create_roadmap_summary(complete_roadmap)
            })
            
        except Exception as e:
            self.log_message(f"Error generating implementation roadmap: {str(e)}", "error")
            return self.create_response(False, error=str(e))
    
    def select_roadmap_framework(self, objectives: List[str], context: Dict[str, Any]) -> str:
        """Select the most appropriate roadmap framework"""
        # Simple framework selection logic
        objective_text = " ".join(objectives).lower()
        
        if "optimization" in objective_text or "efficiency" in objective_text:
            return "business_optimization"
        elif "innovation" in objective_text or "strategy" in objective_text:
            return "ai_innovation_strategy"
        else:
            return "ai_implementation"
    
    def generate_ai_roadmap(self, business_context: Dict[str, Any], objectives: List[str], 
                           timeline: str, budget: str, industry: str, 
                           company_size: str, framework: str) -> Dict[str, Any]:
        """Generate roadmap using AI"""
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            prompt = f"""
            You are an expert AI implementation consultant specializing in strategic roadmap development.
            
            Create a comprehensive AI implementation roadmap based on these requirements:
            
            Business Context:
            - Industry: {industry}
            - Company Size: {company_size}
            - Current State: {business_context.get('current_state', 'Beginning AI journey')}
            - Key Challenges: {business_context.get('challenges', 'Standard business challenges')}
            
            AI Objectives:
            {chr(10).join(f"- {obj}" for obj in objectives)}
            
            Framework: {framework}
            Timeline: {timeline}
            Budget Range: {budget}
            
            Framework Details:
            - Phases: {self.roadmap_frameworks[framework]['phases']}
            - Focus Areas: {self.roadmap_frameworks[framework]['focus_areas']}
            - Expected Timeline: {self.roadmap_frameworks[framework]['timeline']}
            
            Generate a detailed roadmap with:
            1. Phase-by-phase breakdown with specific activities
            2. Key milestones and deliverables for each phase
            3. Resource requirements (team, technology, budget)
            4. Success metrics and KPIs
            5. Strategic recommendations
            
            Focus on practical, actionable steps that align with consulting best practices.
            Include specific deliverables that demonstrate value at each phase.
            
            Respond with JSON in this format:
            {{
                "phases": [
                    {{
                        "name": "Phase Name",
                        "duration": "X weeks/months",
                        "objectives": ["objective1", "objective2"],
                        "activities": ["activity1", "activity2"],
                        "deliverables": ["deliverable1", "deliverable2"]
                    }}
                ],
                "milestones": [
                    {{
                        "name": "Milestone Name",
                        "phase": "Phase Name",
                        "deadline": "Week X",
                        "success_criteria": ["criteria1", "criteria2"]
                    }}
                ],
                "resources": {{
                    "team_requirements": ["role1", "role2"],
                    "technology_stack": ["tech1", "tech2"],
                    "estimated_budget": "budget range",
                    "external_support": ["consultant", "vendor"]
                }},
                "success_metrics": [
                    {{
                        "metric": "Metric Name",
                        "target": "Target Value",
                        "measurement": "How to measure"
                    }}
                ],
                "recommendations": [
                    {{
                        "category": "Category",
                        "recommendation": "Specific recommendation",
                        "rationale": "Why this is important"
                    }}
                ]
            }}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.7
            )
            
            roadmap_data = json.loads(response.choices[0].message.content)
            return roadmap_data
            
        except Exception as e:
            self.log_message(f"Error generating AI roadmap: {str(e)}", "error")
            raise e
    
    def extract_deliverables_from_phases(self, phases: List[Dict[str, Any]]) -> List[str]:
        """Extract all deliverables from phases"""
        deliverables = []
        for phase in phases:
            phase_deliverables = phase.get("deliverables", [])
            deliverables.extend(phase_deliverables)
        return deliverables
    
    def add_implementation_details(self, roadmap_data: Dict[str, Any], framework: str) -> Dict[str, Any]:
        """Add detailed implementation specifics to the roadmap"""
        # Add methodology recommendations
        roadmap_data["methodology"] = self.recommend_methodology(roadmap_data)
        
        # Add workshop and training components
        roadmap_data["workshops"] = self.generate_workshop_plan(roadmap_data.get("phases", []))
        
        # Add Design Thinking integration points
        roadmap_data["design_thinking_integration"] = self.integrate_design_thinking(roadmap_data.get("phases", []))
        
        return roadmap_data
    
    def recommend_methodology(self, roadmap_data: Dict[str, Any]) -> Dict[str, Any]:
        """Recommend implementation methodology based on roadmap characteristics"""
        phase_count = len(roadmap_data.get("phases", []))
        
        if phase_count <= 3:
            recommended = "lean_startup"
        elif phase_count <= 5:
            recommended = "agile_ai"
        else:
            recommended = "design_thinking"
        
        return {
            "primary": recommended,
            "description": self.methodologies[recommended],
            "rationale": f"Recommended based on {phase_count} phases and complexity level"
        }
    
    def generate_workshop_plan(self, phases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate workshop plan for each implementation phase"""
        workshops = []
        
        for i, phase in enumerate(phases):
            workshop = {
                "phase": phase["name"],
                "workshop_name": f"AI Implementation Workshop: {phase['name']}",
                "duration": "2-3 days",
                "participants": ["Stakeholders", "Technical Team", "End Users"],
                "objectives": [
                    f"Align on {phase['name'].lower()} objectives",
                    "Identify potential challenges and solutions",
                    "Create detailed implementation plan"
                ],
                "deliverables": [
                    "Phase-specific action plan",
                    "Risk mitigation strategies", 
                    "Resource allocation plan"
                ]
            }
            workshops.append(workshop)
        
        return workshops
    
    def integrate_design_thinking(self, phases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Integrate Design Thinking principles into roadmap phases"""
        design_thinking_steps = ["Empathize", "Define", "Ideate", "Prototype", "Test"]
        integration_points = []
        
        for phase in phases:
            if "planning" in phase["name"].lower() or "assessment" in phase["name"].lower():
                integration_points.append({
                    "phase": phase["name"],
                    "design_thinking_focus": "Empathize & Define",
                    "activities": [
                        "User research and stakeholder interviews",
                        "Problem definition and user journey mapping",
                        "Define success criteria from user perspective"
                    ]
                })
            elif "implementation" in phase["name"].lower() or "development" in phase["name"].lower():
                integration_points.append({
                    "phase": phase["name"],
                    "design_thinking_focus": "Ideate & Prototype",
                    "activities": [
                        "Solution brainstorming sessions",
                        "Rapid prototyping and MVP development",
                        "User feedback integration"
                    ]
                })
            elif "testing" in phase["name"].lower() or "validation" in phase["name"].lower():
                integration_points.append({
                    "phase": phase["name"],
                    "design_thinking_focus": "Test & Iterate",
                    "activities": [
                        "User testing and feedback collection",
                        "Solution refinement based on insights",
                        "Continuous improvement planning"
                    ]
                })
        
        return integration_points
    
    def generate_risk_assessment(self, business_context: Dict[str, Any], objectives: List[str]) -> Dict[str, Any]:
        """Generate comprehensive risk assessment for the implementation"""
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            prompt = f"""
            Analyze the potential risks for this AI implementation project:
            
            Business Context: {json.dumps(business_context)}
            Objectives: {objectives}
            
            Assess risks in these categories:
            {chr(10).join(f"- {category}" for category in self.risk_categories)}
            
            For each identified risk, provide:
            1. Risk description
            2. Probability (Low/Medium/High)
            3. Impact (Low/Medium/High)
            4. Mitigation strategies
            
            Respond with JSON:
            {{
                "risks": [
                    {{
                        "category": "Risk Category",
                        "description": "Risk description",
                        "probability": "Low/Medium/High",
                        "impact": "Low/Medium/High",
                        "mitigation_strategies": ["strategy1", "strategy2"]
                    }}
                ],
                "overall_risk_level": "Low/Medium/High",
                "key_recommendations": ["recommendation1", "recommendation2"]
            }}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            self.log_message(f"Error generating risk assessment: {str(e)}", "error")
            return {
                "risks": [],
                "overall_risk_level": "Medium",
                "key_recommendations": ["Conduct detailed assessment before implementation"]
            }
    
    def assess_organizational_readiness(self, assessment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess organization's readiness for AI implementation"""
        try:
            readiness_factors = {
                "leadership_support": assessment_data.get("leadership_buy_in", 5),
                "data_maturity": assessment_data.get("data_quality", 3),
                "technical_capabilities": assessment_data.get("tech_team_skills", 4),
                "change_management": assessment_data.get("change_readiness", 3),
                "budget_allocation": assessment_data.get("budget_commitment", 4)
            }
            
            # Calculate overall readiness score
            total_score = sum(readiness_factors.values())
            max_score = len(readiness_factors) * 10
            readiness_percentage = (total_score / max_score) * 100
            
            # Determine readiness level
            if readiness_percentage >= 80:
                readiness_level = "High - Ready for Implementation"
            elif readiness_percentage >= 60:
                readiness_level = "Medium - Preparation Needed"
            else:
                readiness_level = "Low - Significant Preparation Required"
            
            recommendations = self.generate_readiness_recommendations(readiness_factors)
            
            return self.create_response(True, {
                "readiness_score": readiness_percentage,
                "readiness_level": readiness_level,
                "factor_scores": readiness_factors,
                "recommendations": recommendations
            })
            
        except Exception as e:
            self.log_message(f"Error assessing organizational readiness: {str(e)}", "error")
            return self.create_response(False, error=str(e))
    
    def generate_readiness_recommendations(self, factors: Dict[str, int]) -> List[Dict[str, Any]]:
        """Generate recommendations based on readiness assessment"""
        recommendations = []
        
        for factor, score in factors.items():
            if score < 7:
                if factor == "leadership_support":
                    recommendations.append({
                        "area": "Leadership Engagement",
                        "recommendation": "Conduct executive AI strategy workshops",
                        "priority": "High"
                    })
                elif factor == "data_maturity":
                    recommendations.append({
                        "area": "Data Foundation",
                        "recommendation": "Implement data governance and quality improvement program",
                        "priority": "High"
                    })
                elif factor == "technical_capabilities":
                    recommendations.append({
                        "area": "Technical Skills",
                        "recommendation": "Develop AI/ML training program for technical team",
                        "priority": "Medium"
                    })
                elif factor == "change_management":
                    recommendations.append({
                        "area": "Change Management",
                        "recommendation": "Establish change management framework and communication plan",
                        "priority": "Medium"
                    })
                elif factor == "budget_allocation":
                    recommendations.append({
                        "area": "Budget Planning",
                        "recommendation": "Develop comprehensive ROI model and budget justification",
                        "priority": "High"
                    })
        
        return recommendations
    
    def create_roadmap_summary(self, roadmap: Dict[str, Any]) -> Dict[str, Any]:
        """Create executive summary of the roadmap"""
        return {
            "total_phases": len(roadmap["phases"]),
            "estimated_timeline": roadmap["timeline"],
            "key_milestones": len(roadmap["milestones"]),
            "primary_framework": roadmap["framework"],
            "risk_level": roadmap["risk_assessment"].get("overall_risk_level", "Medium"),
            "next_steps": [
                "Review and approve roadmap",
                "Secure budget and resources",
                "Begin Phase 1 planning"
            ]
        }
    
    def customize_roadmap_for_industry(self, customization_data: Dict[str, Any]) -> Dict[str, Any]:
        """Customize roadmap for specific industry requirements"""
        try:
            industry = customization_data.get("industry")
            base_roadmap = customization_data.get("roadmap")
            
            # Industry-specific customizations would go here
            # For now, return the base roadmap with industry context
            
            customized_roadmap = base_roadmap.copy()
            customized_roadmap["industry_customizations"] = {
                "industry": industry,
                "specific_considerations": [
                    f"Industry-specific compliance requirements for {industry}",
                    f"Common {industry} use cases and applications",
                    f"Typical {industry} implementation challenges"
                ]
            }
            
            return self.create_response(True, {"customized_roadmap": customized_roadmap})
            
        except Exception as e:
            self.log_message(f"Error customizing roadmap: {str(e)}", "error")
            return self.create_response(False, error=str(e))