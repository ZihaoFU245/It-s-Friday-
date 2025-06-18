"""
Use selenium to achieve chrome automation
Wrapper function for MCP server such that LLM can then have control of web browsing
"""
from app.modules.Browser_Tools import BrowserTools
from typing import Optional, Dict, Any, List, Union
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import asyncio
import logging

# Global browser instance to maintain session across multiple calls (lazy loading)
_browser_instance = None
_browser_session_active = False

def get_browser_instance(headless: bool = True) -> BrowserTools:
    """
    Get or create a browser instance with lazy loading.
    Browser is only created when first needed, not at module import.
    """
    global _browser_instance, _browser_session_active
    if _browser_instance is None or not _browser_session_active:
        _browser_instance = BrowserTools(headless=headless)
        _browser_session_active = True
    return _browser_instance

def is_browser_session_active() -> bool:
    """Check if browser session is currently active."""
    global _browser_session_active
    return _browser_session_active and _browser_instance is not None

def close_browser_instance():
    """Close the global browser instance."""
    global _browser_instance, _browser_session_active
    if _browser_instance:
        try:
            _browser_instance.close()
        except Exception:
            pass  # Ignore errors during cleanup
        _browser_instance = None
        _browser_session_active = False

def force_new_browser_session(headless: bool = True) -> BrowserTools:
    """
    Force create a new browser session, closing the existing one if it exists.
    """
    close_browser_instance()
    return get_browser_instance(headless)

# Navigation Skills
async def navigate_to_url(url: str, headless: bool = True) -> Dict[str, Any]:
    """
    Navigate to a specific URL and return the page source.
    
    This creates a new browser session if none exists. If the current session is invalid,
    you should first call browser_close() and then use browser_create_new_session() before 
    calling this function again.
    
    Args:
        url: The URL to navigate to
        headless: Whether to run browser in headless mode
        
    Returns:
        Dict containing success status, url, title, page_source, and session_info
    """
    try:
        browser = get_browser_instance(headless)
        page_source = browser.visit(url)
        title = browser.get_page_title()
        current_url = browser.get_current_url()
        
        return {
            'success': True,
            'url': current_url,
            'title': title,
            'page_source': page_source[:1000] + "..." if len(page_source) > 1000 else page_source,
            'full_html_length': len(page_source),
            'session_active': is_browser_session_active(),
            'session_info': 'New session created' if not _browser_session_active else 'Using existing session'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'url': url,
            'session_active': is_browser_session_active(),
            'recommendation': 'If session is invalid, use browser_close() then browser_create_new_session()'
        }

async def get_current_page_info() -> Dict[str, Any]:
    """
    Get information about the current page.
    
    If session is invalid or no browser is active, you need to:
    1. Use browser_close() to clean up invalid session
    2. Use browser_create_new_session() to create a new session
    3. Use browser_navigate_to_url() to navigate to a page
    
    Returns:
        Dict containing current URL, title, page info, and session status
    """
    try:
        if not is_browser_session_active():
            return {
                'success': False,
                'error': 'No active browser session',
                'session_active': False,
                'recommendation': 'Use browser_create_new_session() then browser_navigate_to_url()'
            }
        
        browser = get_browser_instance()
        url = browser.get_current_url()
        title = browser.get_page_title()
        html = browser.get_html()
        
        return {
            'success': True,
            'url': url,
            'title': title,
            'html_length': len(html) if html else 0,
            'session_active': True
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'session_active': is_browser_session_active(),
            'recommendation': 'If session is invalid, use browser_close() then browser_create_new_session()'
        }

async def get_page_html() -> Dict[str, Any]:
    """
    Get the full HTML source of the current page.
    
    Returns:
        Dict containing the HTML source
    """
    try:
        browser = get_browser_instance()
        html = browser.get_html()
        
        return {
            'success': True,
            'html': html,
            'length': len(html) if html else 0
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

async def get_page_text() -> Dict[str, Any]:
    """
    Get all text content from the current page, filtering out href links and keeping only readable text.
    
    Returns:
        Dict containing the extracted text content
    """
    try:
        if not is_browser_session_active():
            return {
                'success': False,
                'error': 'No active browser session',
                'session_active': False,
                'recommendation': 'Use browser_create_new_session() then browser_navigate_to_url()'
            }
        
        browser = get_browser_instance()
        text = browser.get_page_text()
        
        return {
            'success': True,
            'text': text,
            'length': len(text) if text else 0,
            'session_active': True
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'session_active': is_browser_session_active()
        }

async def find_element_by_id(element_id: str, timeout: int = 10) -> Dict[str, Any]:
    """
    Find an element by its ID attribute.
    
    Args:
        element_id: The ID of the element to find
        timeout: Timeout in seconds
        
    Returns:
        Dict containing success status and element information
    """
    try:
        if not is_browser_session_active():
            return {
                'success': False,
                'error': 'No active browser session',
                'element_id': element_id,
                'session_active': False,
                'recommendation': 'Use browser_create_new_session() then browser_navigate_to_url()'
            }
        
        browser = get_browser_instance()
        element = browser.find_element_by_id(element_id, timeout)
        
        if element:
            # Get basic element information
            tag_name = element.tag_name
            text = element.text[:100] if element.text else ""
            is_displayed = element.is_displayed()
            is_enabled = element.is_enabled()
            
            return {
                'success': True,
                'element_id': element_id,
                'found': True,
                'tag_name': tag_name,
                'text_preview': text,
                'is_displayed': is_displayed,
                'is_enabled': is_enabled,
                'session_active': True
            }
        else:
            return {
                'success': False,
                'element_id': element_id,
                'found': False,
                'error': f'Element with ID "{element_id}" not found',
                'session_active': True
            }
            
    except Exception as e:
        return {
            'success': False,
            'element_id': element_id,
            'error': str(e),
            'session_active': is_browser_session_active()
        }

# Element Interaction Skills
async def click_element(selector: str, by_type: str = "css", timeout: int = 10) -> Dict[str, Any]:
    """
    Click on an element specified by selector.
    
    Requires an active browser session. If session is invalid:
    1. Use browser_close() to clean up
    2. Use browser_create_new_session() to create new session
    3. Use browser_navigate_to_url() to load a page
    
    Args:
        selector: The selector string to find the element
        by_type: Type of selector ('css', 'xpath', 'id', 'name', 'class', 'tag')
        timeout: Timeout in seconds
        
    Returns:
        Dict containing success status, details, and session info
    """
    try:
        if not is_browser_session_active():
            return {
                'success': False,
                'error': 'No active browser session',
                'selector': selector,
                'action': 'click',
                'session_active': False,
                'recommendation': 'Use browser_create_new_session() then browser_navigate_to_url()'
            }
        
        browser = get_browser_instance()
        by_mapping = {
            'css': By.CSS_SELECTOR,
            'xpath': By.XPATH,
            'id': By.ID,
            'name': By.NAME,
            'class': By.CLASS_NAME,
            'tag': By.TAG_NAME
        }
        
        by = by_mapping.get(by_type.lower(), By.CSS_SELECTOR)
        success = browser.click(selector, by, timeout)
        
        return {
            'success': success,
            'selector': selector,
            'by_type': by_type,
            'action': 'click',
            'session_active': True
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'selector': selector,
            'action': 'click',
            'session_active': is_browser_session_active(),
            'recommendation': 'If session is invalid, use browser_close() then browser_create_new_session()'
        }

async def double_click_element(selector: str, by_type: str = "css", timeout: int = 10) -> Dict[str, Any]:
    """
    Double-click on an element.
    
    Args:
        selector: The selector string to find the element
        by_type: Type of selector
        timeout: Timeout in seconds
        
    Returns:
        Dict containing success status and details
    """
    try:
        browser = get_browser_instance()
        by_mapping = {
            'css': By.CSS_SELECTOR,
            'xpath': By.XPATH,
            'id': By.ID,
            'name': By.NAME,
            'class': By.CLASS_NAME,
            'tag': By.TAG_NAME
        }
        
        by = by_mapping.get(by_type.lower(), By.CSS_SELECTOR)
        success = browser.double_click(selector, by, timeout)
        
        return {
            'success': success,
            'selector': selector,
            'by_type': by_type,
            'action': 'double_click'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'selector': selector,
            'action': 'double_click'
        }

async def right_click_element(selector: str, by_type: str = "css", timeout: int = 10) -> Dict[str, Any]:
    """
    Right-click on an element.
    
    Args:
        selector: The selector string to find the element
        by_type: Type of selector
        timeout: Timeout in seconds
        
    Returns:
        Dict containing success status and details
    """
    try:
        browser = get_browser_instance()
        by_mapping = {
            'css': By.CSS_SELECTOR,
            'xpath': By.XPATH,
            'id': By.ID,
            'name': By.NAME,
            'class': By.CLASS_NAME,
            'tag': By.TAG_NAME
        }
        
        by = by_mapping.get(by_type.lower(), By.CSS_SELECTOR)
        success = browser.right_click(selector, by, timeout)
        
        return {
            'success': success,
            'selector': selector,
            'by_type': by_type,
            'action': 'right_click'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'selector': selector,
            'action': 'right_click'
        }

async def click_coordinates(x: int, y: int) -> Dict[str, Any]:
    """
    Click at specific coordinates on the page.
    
    Args:
        x: X coordinate
        y: Y coordinate
        
    Returns:
        Dict containing success status and coordinates
    """
    try:
        browser = get_browser_instance()
        success = browser.click_coordinates(x, y)
        
        return {
            'success': success,
            'coordinates': {'x': x, 'y': y},
            'action': 'click_coordinates'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'coordinates': {'x': x, 'y': y},
            'action': 'click_coordinates'
        }

# Text Input Skills
async def type_text_into_element(selector: str, text: str, by_type: str = "css", 
                                clear_first: bool = True, timeout: int = 10) -> Dict[str, Any]:
    """
    Type text into an input element.
    
    Args:
        selector: The selector string to find the element
        text: Text to type
        by_type: Type of selector
        clear_first: Whether to clear the field first
        timeout: Timeout in seconds
        
    Returns:
        Dict containing success status and details
    """
    try:
        browser = get_browser_instance()
        by_mapping = {
            'css': By.CSS_SELECTOR,
            'xpath': By.XPATH,
            'id': By.ID,
            'name': By.NAME,
            'class': By.CLASS_NAME,
            'tag': By.TAG_NAME
        }
        
        by = by_mapping.get(by_type.lower(), By.CSS_SELECTOR)
        success = browser.type_text(selector, text, by, timeout, clear_first)
        
        return {
            'success': success,
            'selector': selector,
            'text_length': len(text),
            'clear_first': clear_first,
            'action': 'type_text'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'selector': selector,
            'action': 'type_text'
        }

async def press_key(key_name: str) -> Dict[str, Any]:
    """
    Press a specific key.
    
    Args:
        key_name: Name of the key ('enter', 'tab', 'escape', 'space', etc.)
        
    Returns:
        Dict containing success status
    """
    try:
        browser = get_browser_instance()
        
        # Map key names to Selenium keys
        key_mapping = {
            'enter': Keys.ENTER,
            'return': Keys.RETURN,
            'tab': Keys.TAB,
            'escape': Keys.ESCAPE,
            'space': Keys.SPACE,
            'backspace': Keys.BACKSPACE,
            'delete': Keys.DELETE,
            'arrow_up': Keys.ARROW_UP,
            'arrow_down': Keys.ARROW_DOWN,
            'arrow_left': Keys.ARROW_LEFT,
            'arrow_right': Keys.ARROW_RIGHT,
            'home': Keys.HOME,
            'end': Keys.END,
            'page_up': Keys.PAGE_UP,
            'page_down': Keys.PAGE_DOWN,
            'f1': Keys.F1,
            'f2': Keys.F2,
            'f3': Keys.F3,
            'f4': Keys.F4,
            'f5': Keys.F5,
            'ctrl': Keys.CONTROL,
            'alt': Keys.ALT,
            'shift': Keys.SHIFT
        }
        
        key = key_mapping.get(key_name.lower(), getattr(Keys, key_name.upper(), None))
        if key is None:
            return {
                'success': False,
                'error': f"Unknown key: {key_name}",
                'available_keys': list(key_mapping.keys())
            }
        
        success = browser.press_key(key)
        
        return {
            'success': success,
            'key': key_name,
            'action': 'press_key'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'key': key_name,
            'action': 'press_key'
        }

# Element Information Skills
async def get_element_text(selector: str, by_type: str = "css", timeout: int = 10) -> Dict[str, Any]:
    """
    Get text content from an element.
    
    Args:
        selector: The selector string to find the element
        by_type: Type of selector
        timeout: Timeout in seconds
        
    Returns:
        Dict containing text content and success status
    """
    try:
        browser = get_browser_instance()
        by_mapping = {
            'css': By.CSS_SELECTOR,
            'xpath': By.XPATH,
            'id': By.ID,
            'name': By.NAME,
            'class': By.CLASS_NAME,
            'tag': By.TAG_NAME
        }
        
        by = by_mapping.get(by_type.lower(), By.CSS_SELECTOR)
        text = browser.get_element_text(selector, by, timeout)
        
        return {
            'success': text is not None,
            'text': text,
            'selector': selector,
            'action': 'get_text'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'selector': selector,
            'action': 'get_text'
        }

async def get_element_attribute(selector: str, attribute: str, by_type: str = "css", timeout: int = 10) -> Dict[str, Any]:
    """
    Get an attribute value from an element.
    
    Args:
        selector: The selector string to find the element
        attribute: Name of the attribute to get
        by_type: Type of selector
        timeout: Timeout in seconds
        
    Returns:
        Dict containing attribute value and success status
    """
    try:
        browser = get_browser_instance()
        by_mapping = {
            'css': By.CSS_SELECTOR,
            'xpath': By.XPATH,
            'id': By.ID,
            'name': By.NAME,
            'class': By.CLASS_NAME,
            'tag': By.TAG_NAME
        }
        
        by = by_mapping.get(by_type.lower(), By.CSS_SELECTOR)
        value = browser.get_element_attribute(selector, attribute, by, timeout)
        
        return {
            'success': value is not None,
            'attribute': attribute,
            'value': value,
            'selector': selector,
            'action': 'get_attribute'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'selector': selector,
            'attribute': attribute,
            'action': 'get_attribute'
        }

# Scrolling Skills
async def scroll_to_element(selector: str, by_type: str = "css", timeout: int = 10) -> Dict[str, Any]:
    """
    Scroll to bring an element into view.
    
    Args:
        selector: The selector string to find the element
        by_type: Type of selector
        timeout: Timeout in seconds
        
    Returns:
        Dict containing success status
    """
    try:
        browser = get_browser_instance()
        by_mapping = {
            'css': By.CSS_SELECTOR,
            'xpath': By.XPATH,
            'id': By.ID,
            'name': By.NAME,
            'class': By.CLASS_NAME,
            'tag': By.TAG_NAME
        }
        
        by = by_mapping.get(by_type.lower(), By.CSS_SELECTOR)
        success = browser.scroll_to_element(selector, by, timeout)
        
        return {
            'success': success,
            'selector': selector,
            'action': 'scroll_to_element'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'selector': selector,
            'action': 'scroll_to_element'
        }

async def scroll_by_pixels(x_pixels: int, y_pixels: int) -> Dict[str, Any]:
    """
    Scroll by specific number of pixels.
    
    Args:
        x_pixels: Horizontal scroll amount (positive = right, negative = left)
        y_pixels: Vertical scroll amount (positive = down, negative = up)
        
    Returns:
        Dict containing success status
    """
    try:
        browser = get_browser_instance()
        success = browser.scroll_by_pixels(x_pixels, y_pixels)
        
        return {
            'success': success,
            'x_pixels': x_pixels,
            'y_pixels': y_pixels,
            'action': 'scroll_by_pixels'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'x_pixels': x_pixels,
            'y_pixels': y_pixels,
            'action': 'scroll_by_pixels'
        }

async def scroll_to_top() -> Dict[str, Any]:
    """
    Scroll to the top of the page.
    
    Returns:
        Dict containing success status
    """
    try:
        browser = get_browser_instance()
        success = browser.scroll_to_top()
        
        return {
            'success': success,
            'action': 'scroll_to_top'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'action': 'scroll_to_top'
        }

async def scroll_to_bottom() -> Dict[str, Any]:
    """
    Scroll to the bottom of the page.
    
    Returns:
        Dict containing success status
    """
    try:
        browser = get_browser_instance()
        success = browser.scroll_to_bottom()
        
        return {
            'success': success,
            'action': 'scroll_to_bottom'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'action': 'scroll_to_bottom'
        }

# Drag and Drop Skills
async def drag_and_drop_elements(source_selector: str, target_selector: str, 
                                by_type: str = "css", timeout: int = 10) -> Dict[str, Any]:
    """
    Drag an element from source to target.
    
    Args:
        source_selector: Selector for the element to drag
        target_selector: Selector for the drop target
        by_type: Type of selector
        timeout: Timeout in seconds
        
    Returns:
        Dict containing success status
    """
    try:
        browser = get_browser_instance()
        by_mapping = {
            'css': By.CSS_SELECTOR,
            'xpath': By.XPATH,
            'id': By.ID,
            'name': By.NAME,
            'class': By.CLASS_NAME,
            'tag': By.TAG_NAME
        }
        
        by = by_mapping.get(by_type.lower(), By.CSS_SELECTOR)
        success = browser.drag_and_drop(source_selector, target_selector, by, timeout)
        
        return {
            'success': success,
            'source_selector': source_selector,
            'target_selector': target_selector,
            'action': 'drag_and_drop'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'source_selector': source_selector,
            'target_selector': target_selector,
            'action': 'drag_and_drop'
        }

async def drag_element_by_offset(selector: str, x_offset: int, y_offset: int, 
                               by_type: str = "css", timeout: int = 10) -> Dict[str, Any]:
    """
    Drag an element by a specific offset.
    
    Args:
        selector: Selector for the element to drag
        x_offset: Horizontal offset
        y_offset: Vertical offset
        by_type: Type of selector
        timeout: Timeout in seconds
        
    Returns:
        Dict containing success status
    """
    try:
        browser = get_browser_instance()
        by_mapping = {
            'css': By.CSS_SELECTOR,
            'xpath': By.XPATH,
            'id': By.ID,
            'name': By.NAME,
            'class': By.CLASS_NAME,
            'tag': By.TAG_NAME
        }
        
        by = by_mapping.get(by_type.lower(), By.CSS_SELECTOR)
        success = browser.drag_by_offset(selector, x_offset, y_offset, by, timeout)
        
        return {
            'success': success,
            'selector': selector,
            'x_offset': x_offset,
            'y_offset': y_offset,
            'action': 'drag_by_offset'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'selector': selector,
            'x_offset': x_offset,
            'y_offset': y_offset,
            'action': 'drag_by_offset'
        }

# Browser Navigation Skills
async def go_back() -> Dict[str, Any]:
    """
    Navigate back in browser history.
    
    Returns:
        Dict containing success status
    """
    try:
        browser = get_browser_instance()
        success = browser.go_back()
        
        return {
            'success': success,
            'action': 'go_back'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'action': 'go_back'
        }

async def go_forward() -> Dict[str, Any]:
    """
    Navigate forward in browser history.
    
    Returns:
        Dict containing success status
    """
    try:
        browser = get_browser_instance()
        success = browser.go_forward()
        
        return {
            'success': success,
            'action': 'go_forward'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'action': 'go_forward'
        }

async def refresh_page() -> Dict[str, Any]:
    """
    Refresh the current page.
    
    Returns:
        Dict containing success status
    """
    try:
        browser = get_browser_instance()
        success = browser.refresh()
        
        return {
            'success': success,
            'action': 'refresh'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'action': 'refresh'
        }

# Utility Skills
async def take_screenshot(filename: Optional[str] = None) -> Dict[str, Any]:
    """
    Take a screenshot of the current page.
    
    Args:
        filename: Optional filename for the screenshot
        
    Returns:
        Dict containing success status and file path
    """
    try:
        browser = get_browser_instance()
        filepath = browser.take_screenshot(filename)
        
        return {
            'success': filepath is not None,
            'filepath': filepath,
            'action': 'take_screenshot'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'action': 'take_screenshot'
        }

async def execute_javascript(script: str, *args) -> Dict[str, Any]:
    """
    Execute JavaScript code on the current page.
    
    Args:
        script: JavaScript code to execute
        *args: Arguments to pass to the script
        
    Returns:
        Dict containing result and success status
    """
    try:
        browser = get_browser_instance()
        result = browser.execute_javascript(script, *args)
        
        return {
            'success': True,
            'result': result,
            'script_length': len(script),
            'action': 'execute_javascript'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'script_length': len(script),
            'action': 'execute_javascript'
        }

async def wait_for_element(selector: str, by_type: str = "css", timeout: int = 10) -> Dict[str, Any]:
    """
    Wait for an element to appear in the DOM.
    
    Args:
        selector: The selector string to find the element
        by_type: Type of selector
        timeout: Timeout in seconds
        
    Returns:
        Dict containing success status
    """
    try:
        browser = get_browser_instance()
        by_mapping = {
            'css': By.CSS_SELECTOR,
            'xpath': By.XPATH,
            'id': By.ID,
            'name': By.NAME,
            'class': By.CLASS_NAME,
            'tag': By.TAG_NAME
        }
        
        by = by_mapping.get(by_type.lower(), By.CSS_SELECTOR)
        element = browser.wait_for_element(selector, by, timeout)
        
        return {
            'success': element is not None,
            'selector': selector,
            'timeout': timeout,
            'action': 'wait_for_element'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'selector': selector,
            'timeout': timeout,
            'action': 'wait_for_element'
        }

async def wait_for_element_clickable(selector: str, by_type: str = "css", timeout: int = 10) -> Dict[str, Any]:
    """
    Wait for an element to be clickable.
    
    Args:
        selector: The selector string to find the element
        by_type: Type of selector
        timeout: Timeout in seconds
        
    Returns:
        Dict containing success status
    """
    try:
        browser = get_browser_instance()
        by_mapping = {
            'css': By.CSS_SELECTOR,
            'xpath': By.XPATH,
            'id': By.ID,
            'name': By.NAME,
            'class': By.CLASS_NAME,
            'tag': By.TAG_NAME
        }
        
        by = by_mapping.get(by_type.lower(), By.CSS_SELECTOR)
        element = browser.wait_for_element_clickable(selector, by, timeout)
        
        return {
            'success': element is not None,
            'selector': selector,
            'timeout': timeout,
            'action': 'wait_for_element_clickable'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'selector': selector,
            'timeout': timeout,
            'action': 'wait_for_element_clickable'
        }

async def find_elements(selector: str, by_type: str = "css") -> Dict[str, Any]:
    """
    Find multiple elements matching the selector.
    
    Args:
        selector: The selector string to find elements
        by_type: Type of selector
        
    Returns:
        Dict containing element count and basic info
    """
    try:
        browser = get_browser_instance()
        by_mapping = {
            'css': By.CSS_SELECTOR,
            'xpath': By.XPATH,
            'id': By.ID,
            'name': By.NAME,
            'class': By.CLASS_NAME,
            'tag': By.TAG_NAME
        }
        
        by = by_mapping.get(by_type.lower(), By.CSS_SELECTOR)
        elements = browser.find_elements(selector, by)
        
        # Get basic info about found elements
        elements_info = []
        for i, element in enumerate(elements[:5]):  # Limit to first 5 for performance
            try:
                info = {
                    'index': i,
                    'tag_name': element.tag_name,
                    'text': element.text[:50] + "..." if len(element.text) > 50 else element.text,
                    'visible': element.is_displayed()
                }
                elements_info.append(info)
            except:
                elements_info.append({'index': i, 'error': 'Could not get element info'})
        
        return {
            'success': True,
            'count': len(elements),
            'selector': selector,
            'elements_info': elements_info,
            'action': 'find_elements'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'selector': selector,
            'action': 'find_elements'
        }

# Session Management
async def close_browser() -> Dict[str, Any]:
    """
    Close the browser instance and clean up resources.
    
    Returns:
        Dict containing success status
    """
    try:
        close_browser_instance()
        return {
            'success': True,
            'action': 'close_browser',
            'session_active': False,
            'message': 'Browser session closed successfully'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'action': 'close_browser'
        }

async def create_new_browser_session(headless: bool = True) -> Dict[str, Any]:
    """
    Create a new browser session, replacing any existing session.
    
    This function will close any existing session and create a fresh browser instance.
    Use this when the current session becomes invalid or you need a clean start.
    
    Args:
        headless: Whether to run browser in headless mode (default: True)
        
    Returns:
        Dict containing success status and session info
    """
    try:
        browser = force_new_browser_session(headless)
        return {
            'success': True,
            'action': 'create_new_session',
            'session_active': True,
            'headless': headless,
            'message': 'New browser session created successfully',
            'next_step': 'Use browser_navigate_to_url() to visit a webpage'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'action': 'create_new_session'
        }

async def get_browser_session_status() -> Dict[str, Any]:
    """
    Get the current browser session status.
    
    Returns:
        Dict containing session information
    """
    try:
        session_active = is_browser_session_active()
        current_url = None
        current_title = None
        
        if session_active:
            try:
                browser = get_browser_instance()
                current_url = browser.get_current_url()
                current_title = browser.get_page_title()
            except Exception:
                # Session might be broken
                session_active = False
        
        return {
            'success': True,
            'session_active': session_active,
            'current_url': current_url,
            'current_title': current_title,
            'message': 'Session is active' if session_active else 'No active session',
            'recommendation': 'Ready to use' if session_active else 'Use browser_create_new_session() to start'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'session_active': False
        }

# Tab Management Skills
async def switch_browser_tabs(tab_index: Optional[int] = None, tab_handle: Optional[str] = None) -> Dict[str, Any]:
    """
    Switch to a specific browser tab.
    
    Args:
        tab_index: Index of the tab to switch to (0-based)
        tab_handle: Window handle of the tab to switch to
        
    Returns:
        Dict containing success status and tab information
    """
    try:
        browser = get_browser_instance()
        success = browser.switch_tabs(tab_index, tab_handle)
        
        return {
            'success': success,
            'tab_index': tab_index,
            'tab_handle': tab_handle,
            'action': 'switch_tabs'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'tab_index': tab_index,
            'tab_handle': tab_handle,
            'action': 'switch_tabs'
        }

async def get_all_browser_tab_descriptions() -> Dict[str, Any]:
    """
    Get descriptions of all open browser tabs.
    
    Returns:
        Dict containing all tab information including titles, URLs, and current tab
    """
    try:
        browser = get_browser_instance()
        tab_descriptions = browser.get_all_tab_descriptions()
        
        return {
            'success': True,
            'tab_count': len(tab_descriptions),
            'tabs': tab_descriptions,
            'action': 'get_all_tab_descriptions'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'action': 'get_all_tab_descriptions'
        }

async def open_new_browser_tab(url: Optional[str] = None) -> Dict[str, Any]:
    """
    Open a new browser tab and optionally navigate to a URL.
    
    Args:
        url: Optional URL to navigate to in the new tab
        
    Returns:
        Dict containing success status and new tab handle
    """
    try:
        browser = get_browser_instance()
        tab_handle = browser.open_new_tab(url)
        
        return {
            'success': tab_handle is not None,
            'tab_handle': tab_handle,
            'url': url,
            'action': 'open_new_tab'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'url': url,
            'action': 'open_new_tab'
        }

async def close_current_browser_tab() -> Dict[str, Any]:
    """
    Close the current browser tab and switch to another if available.
    
    Returns:
        Dict containing success status
    """
    try:
        browser = get_browser_instance()
        success = browser.close_current_tab()
        
        return {
            'success': success,
            'action': 'close_current_tab'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'action': 'close_current_tab'
        }