"""
Base classes for ANSE plugins.

Plugins extend ANSE with custom sensors, devices, and integrations by
inheriting from these base classes and implementing required methods.
"""

import inspect
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class Plugin(ABC):
    """Base class for all ANSE plugins."""
    
    # Required: Plugin name (lowercase, alphanumeric + underscore)
    name: str
    
    # Required: Plugin description
    description: str
    
    # Optional: Sensitivity level (low, medium, high)
    sensitivity: str = "low"
    
    # Optional: Rate limit in calls per minute
    rate_limit: int = 60
    
    # Optional: Plugin author
    author: Optional[str] = None
    
    # Optional: Plugin version
    version: Optional[str] = "1.0.0"
    
    def __init__(self):
        """Initialize the plugin.
        
        Subclasses should override this to set up connections,
        hardware initialization, etc.
        """
        self._validate_plugin()
    
    def _validate_plugin(self) -> None:
        """Validate required plugin attributes."""
        if not hasattr(self, 'name') or not self.name:
            raise ValueError("Plugin must define 'name' attribute")
        
        if not hasattr(self, 'description') or not self.description:
            raise ValueError("Plugin must define 'description' attribute")
        
        if not self.name.replace('_', '').replace('-', '').isalnum():
            raise ValueError(
                f"Plugin name must be alphanumeric + underscore/dash: {self.name}"
            )
    
    async def on_load(self) -> None:
        """Called when plugin is loaded by ANSE.
        
        Override this to perform async initialization like connecting
        to external services, discovering devices, etc.
        """
        pass
    
    async def on_unload(self) -> None:
        """Called when plugin is unloaded.
        
        Override this to clean up connections, stop threads, etc.
        """
        pass
    
    def get_tools(self) -> Dict[str, Dict[str, Any]]:
        """Auto-discover tools from public async methods.
        
        Returns:
            Dictionary of {tool_name: tool_metadata}
        """
        tools = {}
        
        for name, method in inspect.getmembers(self):
            if name.startswith('_'):
                continue
            
            if inspect.iscoroutinefunction(method):
                sig = inspect.signature(method)
                
                # Build parameter info
                parameters = {}
                for param_name, param in sig.parameters.items():
                    if param_name == 'self':
                        continue
                    
                    param_info = {'required': param.default == inspect.Parameter.empty}
                    
                    # Try to get type from annotation
                    if param.annotation != inspect.Parameter.empty:
                        param_info['type'] = param.annotation.__name__
                    
                    parameters[param_name] = param_info
                
                tools[name] = {
                    'description': inspect.getdoc(method) or f"Call {name}",
                    'parameters': parameters,
                    'method': method
                }
        
        return tools


class SensorPlugin(Plugin):
    """Base class for sensor/data-capture plugins.
    
    Sensors provide read-only access to hardware or external data sources.
    Examples: temperature sensors, cameras, microphones, APIs
    """
    
    sensitivity: str = "low"  # Sensors typically have low sensitivity
    
    @abstractmethod
    async def validate_connection(self) -> bool:
        """Validate that the sensor is connected and working.
        
        Returns:
            True if connected and ready, False otherwise
        """
        pass


class ControlPlugin(Plugin):
    """Base class for control/action plugins.
    
    Controllers allow ANSE to perform actions in the real world.
    Examples: smart lights, door locks, robot arms, motors
    """
    
    sensitivity: str = "high"  # Controllers are high sensitivity (can affect world)
    
    @abstractmethod
    async def get_status(self) -> Dict[str, Any]:
        """Get current status of controlled device.
        
        Returns:
            Status dictionary with current state
        """
        pass
    
    @abstractmethod
    async def validate_action(self, action: str, **kwargs) -> bool:
        """Validate that an action is safe to execute.
        
        Args:
            action: Name of action to validate
            **kwargs: Action parameters
            
        Returns:
            True if action is safe, False otherwise
        """
        pass


class NetworkPlugin(Plugin):
    """Base class for network/API plugins.
    
    Network plugins connect to external services and APIs.
    Examples: databases, cloud services, APIs, message queues
    """
    
    sensitivity: str = "medium"  # Depends on what the API can do
    
    @abstractmethod
    async def test_connection(self) -> bool:
        """Test connectivity to the external service.
        
        Returns:
            True if connected, False otherwise
        """
        pass


class AnalysisPlugin(Plugin):
    """Base class for analysis/processing plugins.
    
    Analysis plugins process data and provide insights.
    Examples: image analysis, data aggregation, anomaly detection
    """
    
    sensitivity: str = "low"  # Analysis plugins are read-only
    
    @abstractmethod
    async def validate_input(self, data: Any) -> bool:
        """Validate that input data is in expected format.
        
        Args:
            data: Data to analyze
            
        Returns:
            True if valid, False otherwise
        """
        pass
