"""
Base Agent Class
Provides common functionality for all specialized agents
"""

import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod

from utils.logger import setup_logger

class BaseAgent(ABC):
    """Abstract base class for all agents in the system"""
    
    def __init__(self, name: str, role: str, tools: List[str] = None):
        self.name = name
        self.role = role
        self.tools = tools or []
        self.agent_id = str(uuid.uuid4())
        self.logger = setup_logger(f"agent.{name.lower().replace(' ', '_')}")
        self.state = {}
        self.message_history = []
        
    def log_message(self, message: str, level: str = "info", metadata: Dict[str, Any] = None):
        """Log a message with agent context"""
        log_data = {
            "agent_id": self.agent_id,
            "agent_name": self.name,
            "timestamp": datetime.utcnow().isoformat(),
            "message": message
        }
        
        if metadata:
            log_data.update(metadata)
            
        if level == "error":
            self.logger.error(json.dumps(log_data))
        elif level == "warning":
            self.logger.warning(json.dumps(log_data))
        else:
            self.logger.info(json.dumps(log_data))
    
    def update_state(self, key: str, value: Any):
        """Update agent state"""
        self.state[key] = value
        self.log_message(f"State updated: {key}", metadata={"state_key": key})
    
    def get_state(self, key: str, default: Any = None) -> Any:
        """Get value from agent state"""
        return self.state.get(key, default)
    
    def send_message(self, recipient_agent: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """Send message to another agent"""
        message_data = {
            "id": str(uuid.uuid4()),
            "from": self.name,
            "to": recipient_agent,
            "timestamp": datetime.utcnow().isoformat(),
            "payload": message
        }
        
        self.message_history.append(message_data)
        self.log_message(f"Message sent to {recipient_agent}", metadata={"message_id": message_data["id"]})
        
        return message_data
    
    def receive_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Receive and process message from another agent"""
        self.message_history.append(message)
        self.log_message(f"Message received from {message.get('from')}", metadata={"message_id": message.get("id")})
        
        return self.process_message(message)
    
    def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process received message - override in subclasses"""
        return {"status": "received", "message": "Message processed by base agent"}
    
    def validate_input(self, data: Dict[str, Any], required_fields: List[str]) -> tuple[bool, str]:
        """Validate input data has required fields"""
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            error_msg = f"Missing required fields: {', '.join(missing_fields)}"
            self.log_message(error_msg, level="error")
            return False, error_msg
            
        return True, "Valid"
    
    def create_response(self, success: bool, data: Dict[str, Any] = None, error: str = None) -> Dict[str, Any]:
        """Create standardized response format"""
        response = {
            "agent": self.name,
            "agent_id": self.agent_id,
            "timestamp": datetime.utcnow().isoformat(),
            "success": success
        }
        
        if success and data:
            response["data"] = data
        elif not success and error:
            response["error"] = error
            
        return response
    
    @abstractmethod
    def execute_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute primary task - must be implemented by subclasses"""
        pass
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return agent capabilities and status"""
        return {
            "name": self.name,
            "role": self.role,
            "tools": self.tools,
            "agent_id": self.agent_id,
            "state_keys": list(self.state.keys()),
            "message_count": len(self.message_history)
        }
    
    def reset_state(self):
        """Reset agent state and history"""
        self.state.clear()
        self.message_history.clear()
        self.log_message("Agent state reset")

class AgentCommunicationHub:
    """Central hub for inter-agent communication"""
    
    def __init__(self):
        self.agents = {}
        self.message_queue = []
        self.logger = setup_logger("communication_hub")
    
    def register_agent(self, agent: BaseAgent):
        """Register an agent with the communication hub"""
        self.agents[agent.name] = agent
        self.logger.info(f"Agent registered: {agent.name} ({agent.role})")
    
    def route_message(self, from_agent: str, to_agent: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """Route message between agents"""
        if to_agent not in self.agents:
            error_msg = f"Target agent not found: {to_agent}"
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}
        
        try:
            target_agent = self.agents[to_agent]
            response = target_agent.receive_message(message)
            
            self.logger.info(f"Message routed from {from_agent} to {to_agent}")
            return {"success": True, "response": response}
            
        except Exception as e:
            error_msg = f"Message routing failed: {e}"
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def broadcast_message(self, from_agent: str, message: Dict[str, Any], exclude: List[str] = None) -> Dict[str, Any]:
        """Broadcast message to all agents except excluded ones"""
        exclude = exclude or [from_agent]
        responses = {}
        
        for agent_name, agent in self.agents.items():
            if agent_name not in exclude:
                try:
                    response = agent.receive_message(message)
                    responses[agent_name] = response
                except Exception as e:
                    responses[agent_name] = {"success": False, "error": str(e)}
        
        return {"success": True, "responses": responses}
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all registered agents"""
        status = {}
        
        for agent_name, agent in self.agents.items():
            try:
                status[agent_name] = agent.get_capabilities()
            except Exception as e:
                status[agent_name] = {"error": str(e)}
                
        return status
