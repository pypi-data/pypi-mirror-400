"""Process registry for managing and discovering processes"""

import logging
from typing import Dict, Type, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.process import ProcessProtocol


class ProcessRegistry:
    """
    Central registry for process types.
    
    Allows users to register, discover, and instantiate automation processes.
    Useful for building process catalogs and factories.
    
    Example:
        from athesa.factory import registry
        
        # Register processes
        registry.register('google_login', GoogleLoginProcess)
        registry.register('youtube_upload', YouTubeUploadProcess)
        
        # List available
        print(registry.list())  # ['google_login', 'youtube_upload']
        
        # Get process class
        LoginProcess = registry.get('google_login')
        process_instance = LoginProcess()
        
        # Create instance directly
        process = registry.create('google_login')
    """
    
    def __init__(self):
        self._processes: Dict[str, Type['ProcessProtocol']] = {}
        self._logger = logging.getLogger(__name__)
    
    def register(
        self,
        name: str,
        process_class: Type['ProcessProtocol'],
        force: bool = False
    ) -> None:
        """
        Register a process type.
        
        Args:
            name: Unique identifier for this process
            process_class: Process class (not instance)
            force: If True, overwrite existing registration
            
        Raises:
            ValueError: If process already registered and force=False
            
        Example:
            registry.register('login', GoogleLoginProcess)
        """
        if name in self._processes and not force:
            raise ValueError(
                f"Process '{name}' already registered. "
                f"Use force=True to overwrite."
            )
        
        self._processes[name] = process_class
        self._logger.info(f"Registered process: {name}")
    
    def unregister(self, name: str) -> None:
        """
        Unregister a process.
        
        Args:
            name: Process name to remove
            
        Example:
            registry.unregister('old_process')
        """
        if name in self._processes:
            del self._processes[name]
            self._logger.info(f"Unregistered process: {name}")
    
    def get(self, name: str) -> Optional[Type['ProcessProtocol']]:
        """
        Get process class by name.
        
        Args:
            name: Process name
            
        Returns:
            Process class, or None if not found
            
        Example:
            ProcessClass = registry.get('google_login')
            if ProcessClass:
                process = ProcessClass()
        """
        return self._processes.get(name)
    
    def create(self, name: str, **kwargs) -> Optional['ProcessProtocol']:
        """
        Create process instance by name.
        
        Args:
            name: Process name
            **kwargs: Arguments to pass to process constructor
            
        Returns:
            Process instance, or None if not found
            
        Example:
            process = registry.create('login', config=my_config)
        """
        process_class = self.get(name)
        if process_class:
            return process_class(**kwargs)
        return None
    
    def list(self) -> List[str]:
        """
        List all registered process names.
        
        Returns:
            List of process names
            
        Example:
            for name in registry.list():
                print(f"Available: {name}")
        """
        return sorted(self._processes.keys())
    
    def exists(self, name: str) -> bool:
        """
        Check if process is registered.
        
        Args:
            name: Process name
            
        Returns:
            True if registered
        """
        return name in self._processes
    
    def clear(self) -> None:
        """Clear all registered processes"""
        self._processes.clear()
        self._logger.info("Cleared all process registrations")
    
    def __len__(self) -> int:
        """Get number of registered processes"""
        return len(self._processes)
    
    def __contains__(self, name: str) -> bool:
        """Check if process exists (supports 'in' operator)"""
        return name in self._processes


# Global registry instance
registry = ProcessRegistry()
