"""Browser automation bridge protocol"""

from typing import Protocol, Tuple, Callable, Any, List, runtime_checkable


@runtime_checkable
class BridgeProtocol(Protocol):
    """
    Protocol for browser automation tools.
    
    Athesa uses this protocol to abstract Selenium, Playwright, or custom tools.
    Any class implementing these methods can be used as a bridge.
    
    Example implementations:
    - SeleniumBridge (athesa.adapters.selenium)
    - PlaywrightBridge (athesa.adapters.playwright)
    - CustomBridge (your own)
    """
    
    def click(self, selector: Tuple[str, str]) -> None:
        """
        Click an element.
        
        Args:
            selector: Tuple of (by, value) e.g., (By.CSS, '#button')
        
        Example:
            bridge.click((By.ID, 'submit-btn'))
        """
        ...
    
    def type_text(self, selector: Tuple[str, str], text: str) -> None:
        """
        Type text into an input element.
        
        Args:
            selector: Tuple of (by, value)
            text: Text to type
            
        Example:
            bridge.type_text((By.CSS, 'input[name="email"]'), 'user@example.com')
        """
        ...
    
    def navigate(self, url: str) -> None:
        """
        Navigate to a URL.
        
        Args:
            url: Full URL to navigate to
            
        Example:
            bridge.navigate('https://example.com/login')
        """
        ...
    
    def is_visible(self, selector: Tuple[str, str]) -> bool:
        """
        Check if element is visible (displayed).
        
        Args:
            selector: Tuple of (by, value)
            
        Returns:
            True if element exists and is visible
            
        Example:
            if bridge.is_visible((By.ID, 'error-message')):
                print("Error displayed")
        """
        ...
    
    def is_existing(self, selector: Tuple[str, str]) -> bool:
        """
        Check if element exists in DOM (may not be visible).
        
        Args:
            selector: Tuple of (by, value)
            
        Returns:
            True if element exists in DOM
        """
        ...
    
    def get_text(self, selector: Tuple[str, str]) -> str:
        """
        Get text content of an element.
        
        Args:
            selector: Tuple of (by, value)
            
        Returns:
            Element's text content
        """
        ...
    
    def get_attribute(self, selector: Tuple[str, str], attribute: str) -> str:
        """
        Get attribute value of an element.
        
        Args:
            selector: Tuple of (by, value)
            attribute: Attribute name (e.g., 'href', 'value')
            
        Returns:
            Attribute value
        """
        ...
    
    def upload_file(self, selector: Tuple[str, str], file_path: str) -> None:
        """
        Upload a file to an input[type=file] element.
        
        Args:
            selector: Tuple of (by, value)
            file_path: Absolute path to file
        """
        ...
    
    def wait_for_condition(self, condition: Callable, timeout: int = 10) -> None:
        """
        Wait for a custom condition to be true.
        
        Args:
            condition: Callable that returns bool
            timeout: Maximum seconds to wait
            
        Example:
            bridge.wait_for_condition(
                lambda: bridge.is_visible((By.ID, 'loading')) == False,
                timeout=30
            )
        """
        ...
    
    def execute_script(self, script: str, *args) -> Any:
        """
        Execute JavaScript in the browser.
        
        Args:
            script: JavaScript code to execute
            *args: Arguments to pass to script
            
        Returns:
            Script return value
            
        Example:
            bridge.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        """
        ...
    
    def refresh_page(self) -> None:
        """Refresh the current page."""
        ...
    
    def get_current_url(self) -> str:
        """Get current page URL."""
        ...
    
    def switch_to_frame(self, frame_reference: Any) -> None:
        """
        Switch to an iframe.
        
        Args:
            frame_reference: Frame index, name, or element
        """
        ...
    
    def switch_to_default_content(self) -> None:
        """Switch back to main document from iframe."""
        ...
    
    def get_window_handles(self) -> List[str]:
        """Get all window/tab handles."""
        ...
    
    def switch_to_window(self, handle: str) -> None:
        """
        Switch to a specific window/tab.
        
        Args:
            handle: Window handle from get_window_handles()
        """
        ...
    
    def close_current_window(self) -> None:
        """Close the current window/tab."""
        ...
