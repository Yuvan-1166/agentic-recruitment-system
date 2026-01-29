"""
Agent registry for dynamic agent management.

Allows registration and discovery of agents for framework integration.
"""

from typing import Any, Dict, List, Optional, Type

from ..agents.base import BaseAgent


class AgentRegistry:
    """
    Registry for managing available agents.
    
    This enables:
    - Dynamic agent discovery
    - Framework integration (LangGraph, CrewAI)
    - Agent capability querying
    - Dependency injection
    """
    
    _instance: Optional["AgentRegistry"] = None
    
    def __new__(cls) -> "AgentRegistry":
        """Singleton pattern for global registry."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._agents: Dict[str, Type[BaseAgent]] = {}
            cls._instance._instances: Dict[str, BaseAgent] = {}
        return cls._instance
    
    def register(self, agent_class: Type[BaseAgent]) -> None:
        """
        Register an agent class.
        
        Args:
            agent_class: The agent class to register
        """
        name = agent_class.__name__
        self._agents[name] = agent_class
    
    def get_agent_class(self, name: str) -> Optional[Type[BaseAgent]]:
        """Get an agent class by name."""
        return self._agents.get(name)
    
    def get_agent_instance(self, name: str) -> Optional[BaseAgent]:
        """
        Get or create an agent instance.
        
        Uses lazy instantiation and caching.
        """
        if name not in self._instances:
            agent_class = self._agents.get(name)
            if agent_class:
                self._instances[name] = agent_class()
        return self._instances.get(name)
    
    def list_agents(self) -> List[str]:
        """List all registered agent names."""
        return list(self._agents.keys())
    
    def get_agent_capabilities(self) -> Dict[str, str]:
        """Get descriptions of all registered agents."""
        capabilities = {}
        for name, agent_class in self._agents.items():
            instance = agent_class()
            capabilities[name] = instance.description
        return capabilities
    
    def clear(self) -> None:
        """Clear the registry (mainly for testing)."""
        self._agents.clear()
        self._instances.clear()


# Auto-register all agents on import
def _auto_register() -> None:
    """Auto-register all agent classes."""
    from ..agents import (
        ResumeParserAgent,
        JDAnalyzerAgent,
        MatcherAgent,
        ShortlisterAgent,
        TestGeneratorAgent,
        TestEvaluatorAgent,
        RankerAgent,
        BiasAuditorAgent,
    )
    
    registry = AgentRegistry()
    for agent_class in [
        ResumeParserAgent,
        JDAnalyzerAgent,
        MatcherAgent,
        ShortlisterAgent,
        TestGeneratorAgent,
        TestEvaluatorAgent,
        RankerAgent,
        BiasAuditorAgent,
    ]:
        registry.register(agent_class)
