import requests
import json
import os
from typing import Dict, Any

class AgentCommunicator:
    """Klasse für die Kommunikation zwischen Agents"""
    
    def __init__(self):
        self.agents = {
            'webdesign': 'http://localhost:8080',
            'marketing': 'http://localhost:8081',
            'seo': 'http://localhost:8082'
        }
    
    def send_message(self, to_agent: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """Sendet eine Nachricht an einen anderen Agent"""
        if to_agent not in self.agents:
            raise ValueError(f"Agent {to_agent} nicht gefunden")
            
        try:
            response = requests.post(
                f"{self.agents[to_agent]}/api/receive_message",
                json=message,
                headers={'Content-Type': 'application/json'}
            )
            return response.json()
        except Exception as e:
            print(f"Fehler bei der Kommunikation mit {to_agent}: {str(e)}")
            return {"error": str(e)}
    
    def broadcast_message(self, message: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Sendet eine Nachricht an alle Agents"""
        responses = {}
        for agent in self.agents:
            responses[agent] = self.send_message(agent, message)
        return responses

# Singleton-Instanz für die Verwendung in allen Agents
communicator = AgentCommunicator() 