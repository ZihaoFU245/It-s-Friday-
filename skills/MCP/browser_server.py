from fastmcp import FastMCP
from typing import Optional, Dict, Any, List
import sys
import os

# Add the project root directory to sys.path so we can import from app
# Go up two levels: MCP -> skills -> project root
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import config and configure MCP-specific logging
from app.config import Config
config = Config()
config.configure_mcp_logging()

try:    
    from skills.use_browser_skills import (
        navigate_to_url,
        get_current_page_info,
        get_page_html,
        click_element,
        double_click_element,
        right_click_element,
        click_coordinates,
        type_text_into_element,
        press_key,
        get_element_text,
        get_element_attribute,
        scroll_to_element,
        scroll_by_pixels,
        scroll_to_top,
        scroll_to_bottom,
        drag_and_drop_elements,
        drag_element_by_offset,
        go_back,
        go_forward,
        refresh_page,
        take_screenshot,        
        execute_javascript,
        wait_for_element,
        wait_for_element_clickable,
        find_elements,
        close_browser,
        create_new_browser_session,
        get_browser_session_status,
        switch_browser_tabs,
        get_all_browser_tab_descriptions,
        open_new_browser_tab,
        close_current_browser_tab,
        get_page_text,
        find_element_by_id
    )
except ImportError:
    # If running directly, try importing from parent skills directory
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from use_browser_skills import (
        navigate_to_url,
        get_current_page_info,
        get_page_html,
        click_element,
        double_click_element,
        right_click_element,
        click_coordinates,
        type_text_into_element,
        press_key,
        get_element_text,
        get_element_attribute,
        scroll_to_element,
        scroll_by_pixels,
        scroll_to_top,
        scroll_to_bottom,
        drag_and_drop_elements,
        drag_element_by_offset,
        go_back,
        go_forward,
        refresh_page,
        take_screenshot,        
        execute_javascript,
        wait_for_element,
        wait_for_element_clickable,
        find_elements,
        close_browser,
        create_new_browser_session,
        get_browser_session_status,
        switch_browser_tabs,
        get_all_browser_tab_descriptions,
        open_new_browser_tab,
        close_current_browser_tab,
        get_page_text,
        find_element_by_id
    )

mcp = FastMCP("JARVERT-BROWSER")

# ========================================
# BROWSER AUTOMATION TOOLS
# ========================================

@mcp.tool()
async def browser_navigate_to_url(url: str, headless: bool = True) -> Dict[str, Any]:
    """
    Navigate to a specific URL and return page information.
    
    This creates a new browser session if none exists. If you encounter session errors,
    first use browser_close() to clean up, then browser_create_new_session() to start fresh.
    
    Args:
        url: The URL to navigate to
        headless: Whether to run browser in headless mode (default: True)
        
    Returns:
        Dict containing success status, url, title, page_source, and session information
    """
    return await navigate_to_url(url, headless)

@mcp.tool()
async def browser_get_current_page_info() -> Dict[str, Any]:
    """
    Get information about the current page including URL, title, and HTML length.
    
    Requires an active browser session. If session is invalid, the response will include
    recommendations to use browser_create_new_session() and browser_navigate_to_url().
    
    Returns:
        Dict containing current URL, title, page info, and session status
    """
    return await get_current_page_info()

@mcp.tool()
async def browser_get_page_html() -> Dict[str, Any]:
    """
    Get the full HTML source of the current page with CSS, JS, and href links filtered out.
    
    Returns:
        Dict containing the filtered HTML source and length
    """
    return await get_page_html()

@mcp.tool()
async def browser_get_page_text() -> Dict[str, Any]:
    """
    Get all text content from the current page, filtering out href links and keeping only readable text.
    
    This function extracts clean, readable text from the page, excluding:
    - Content inside <script>, <style>, and <noscript> tags
    - Text within <a> (link) tags
    - Navigation and UI elements
    - Extra whitespace and formatting
    
    Returns:
        Dict containing the extracted text content and its length
    """
    return await get_page_text()

@mcp.tool()
async def browser_click_element(selector: str, by_type: str = "css", timeout: int = 10) -> Dict[str, Any]:
    """
    Click on an element specified by selector.
    
    Args:
        selector: The selector string to find the element
        by_type: Type of selector ('css', 'xpath', 'id', 'name', 'class', 'tag')
        timeout: Timeout in seconds
        
    Returns:
        Dict containing success status and details
    """
    return await click_element(selector, by_type, timeout)

@mcp.tool()
async def browser_double_click_element(selector: str, by_type: str = "css", timeout: int = 10) -> Dict[str, Any]:
    """
    Double-click on an element.
    
    Args:
        selector: The selector string to find the element
        by_type: Type of selector ('css', 'xpath', 'id', 'name', 'class', 'tag')
        timeout: Timeout in seconds
        
    Returns:
        Dict containing success status and details
    """
    return await double_click_element(selector, by_type, timeout)

@mcp.tool()
async def browser_right_click_element(selector: str, by_type: str = "css", timeout: int = 10) -> Dict[str, Any]:
    """
    Right-click on an element to open context menu.
    
    Args:
        selector: The selector string to find the element
        by_type: Type of selector ('css', 'xpath', 'id', 'name', 'class', 'tag')
        timeout: Timeout in seconds
        
    Returns:
        Dict containing success status and details
    """
    return await right_click_element(selector, by_type, timeout)

@mcp.tool()
async def browser_click_coordinates(x: int, y: int) -> Dict[str, Any]:
    """
    Click at specific coordinates on the page.
    
    Args:
        x: X coordinate
        y: Y coordinate
        
    Returns:
        Dict containing success status and coordinates
    """
    return await click_coordinates(x, y)

@mcp.tool()
async def browser_type_text(selector: str, text: str, by_type: str = "css", 
                           clear_first: bool = True, timeout: int = 10) -> Dict[str, Any]:
    """
    Type text into an input element.
    
    Args:
        selector: The selector string to find the element
        text: Text to type
        by_type: Type of selector ('css', 'xpath', 'id', 'name', 'class', 'tag')
        clear_first: Whether to clear the field first
        timeout: Timeout in seconds
        
    Returns:
        Dict containing success status and details
    """
    return await type_text_into_element(selector, text, by_type, clear_first, timeout)

@mcp.tool()
async def browser_press_key(key_name: str) -> Dict[str, Any]:
    """
    Press a specific key.
    
    Args:
        key_name: Name of the key ('enter', 'tab', 'escape', 'space', 'backspace', 
                 'delete', 'arrow_up', 'arrow_down', 'arrow_left', 'arrow_right', 
                 'home', 'end', 'page_up', 'page_down', 'f1'-'f5', 'ctrl', 'alt', 'shift')
        
    Returns:
        Dict containing success status
    """
    return await press_key(key_name)

@mcp.tool()
async def browser_get_element_text(selector: str, by_type: str = "css", timeout: int = 10) -> Dict[str, Any]:
    """
    Get text content from an element.
    
    Args:
        selector: The selector string to find the element
        by_type: Type of selector ('css', 'xpath', 'id', 'name', 'class', 'tag')
        timeout: Timeout in seconds
        
    Returns:
        Dict containing text content and success status
    """
    return await get_element_text(selector, by_type, timeout)

@mcp.tool()
async def browser_get_element_attribute(selector: str, attribute: str, by_type: str = "css", 
                                      timeout: int = 10) -> Dict[str, Any]:
    """
    Get an attribute value from an element.
    
    Args:
        selector: The selector string to find the element
        attribute: Name of the attribute to get (e.g., 'href', 'src', 'class', 'id')
        by_type: Type of selector ('css', 'xpath', 'id', 'name', 'class', 'tag')
        timeout: Timeout in seconds
        
    Returns:
        Dict containing attribute value and success status
    """
    return await get_element_attribute(selector, attribute, by_type, timeout)

@mcp.tool()
async def browser_scroll_to_element(selector: str, by_type: str = "css", timeout: int = 10) -> Dict[str, Any]:
    """
    Scroll to bring an element into view.
    
    Args:
        selector: The selector string to find the element
        by_type: Type of selector ('css', 'xpath', 'id', 'name', 'class', 'tag')
        timeout: Timeout in seconds
        
    Returns:
        Dict containing success status
    """
    return await scroll_to_element(selector, by_type, timeout)

@mcp.tool()
async def browser_scroll_by_pixels(x_pixels: int, y_pixels: int) -> Dict[str, Any]:
    """
    Scroll by specific number of pixels.
    
    Args:
        x_pixels: Horizontal scroll amount (positive = right, negative = left)
        y_pixels: Vertical scroll amount (positive = down, negative = up)
        
    Returns:
        Dict containing success status
    """
    return await scroll_by_pixels(x_pixels, y_pixels)

@mcp.tool()
async def browser_scroll_to_top() -> Dict[str, Any]:
    """
    Scroll to the top of the page.
    
    Returns:
        Dict containing success status
    """
    return await scroll_to_top()

@mcp.tool()
async def browser_scroll_to_bottom() -> Dict[str, Any]:
    """
    Scroll to the bottom of the page.
    
    Returns:
        Dict containing success status
    """
    return await scroll_to_bottom()

@mcp.tool()
async def browser_drag_and_drop(source_selector: str, target_selector: str, 
                               by_type: str = "css", timeout: int = 10) -> Dict[str, Any]:
    """
    Drag an element from source to target.
    
    Args:
        source_selector: Selector for the element to drag
        target_selector: Selector for the drop target
        by_type: Type of selector ('css', 'xpath', 'id', 'name', 'class', 'tag')
        timeout: Timeout in seconds
        
    Returns:
        Dict containing success status
    """
    return await drag_and_drop_elements(source_selector, target_selector, by_type, timeout)

@mcp.tool()
async def browser_drag_by_offset(selector: str, x_offset: int, y_offset: int, 
                                by_type: str = "css", timeout: int = 10) -> Dict[str, Any]:
    """
    Drag an element by a specific offset.
    
    Args:
        selector: Selector for the element to drag
        x_offset: Horizontal offset
        y_offset: Vertical offset
        by_type: Type of selector ('css', 'xpath', 'id', 'name', 'class', 'tag')
        timeout: Timeout in seconds
        
    Returns:
        Dict containing success status
    """
    return await drag_element_by_offset(selector, x_offset, y_offset, by_type, timeout)

@mcp.tool()
async def browser_go_back() -> Dict[str, Any]:
    """
    Navigate back in browser history.
    
    Returns:
        Dict containing success status
    """
    return await go_back()

@mcp.tool()
async def browser_go_forward() -> Dict[str, Any]:
    """
    Navigate forward in browser history.
    
    Returns:
        Dict containing success status
    """
    return await go_forward()

@mcp.tool()
async def browser_refresh_page() -> Dict[str, Any]:
    """
    Refresh the current page.
    
    Returns:
        Dict containing success status
    """
    return await refresh_page()

@mcp.tool()
async def browser_take_screenshot(filename: Optional[str] = None) -> Dict[str, Any]:
    """
    Take a screenshot of the current page.
    
    Args:
        filename: Optional filename for the screenshot (will auto-generate if not provided)
        
    Returns:
        Dict containing success status and file path
    """
    return await take_screenshot(filename)

@mcp.tool()
async def browser_execute_javascript(script: str) -> Dict[str, Any]:
    """
    Execute JavaScript code on the current page.
    
    Args:
        script: JavaScript code to execute
        
    Returns:
        Dict containing result and success status
    """
    return await execute_javascript(script)

@mcp.tool()
async def browser_wait_for_element(selector: str, by_type: str = "css", timeout: int = 10) -> Dict[str, Any]:
    """
    Wait for an element to appear in the DOM.
    
    Args:
        selector: The selector string to find the element
        by_type: Type of selector ('css', 'xpath', 'id', 'name', 'class', 'tag')
        timeout: Timeout in seconds
        
    Returns:
        Dict containing success status
    """
    return await wait_for_element(selector, by_type, timeout)

@mcp.tool()
async def browser_wait_for_element_clickable(selector: str, by_type: str = "css", 
                                            timeout: int = 10) -> Dict[str, Any]:
    """
    Wait for an element to be clickable.
    
    Args:
        selector: The selector string to find the element
        by_type: Type of selector ('css', 'xpath', 'id', 'name', 'class', 'tag')
        timeout: Timeout in seconds
        
    Returns:
        Dict containing success status
    """
    return await wait_for_element_clickable(selector, by_type, timeout)

@mcp.tool()
async def browser_find_elements(selector: str, by_type: str = "css") -> Dict[str, Any]:
    """
    Find multiple elements matching the selector and get basic information about them.
    
    Args:
        selector: The selector string to find elements
        by_type: Type of selector ('css', 'xpath', 'id', 'name', 'class', 'tag')
        
    Returns:
        Dict containing element count and basic info about first 5 elements
    """
    return await find_elements(selector, by_type)

@mcp.tool()
async def browser_close() -> Dict[str, Any]:
    """
    Close the browser instance and clean up resources.

    ! If you still need to use browser, then create a new tab and close the old one first.
    Only use this function when the user requests terminate here.
    
    Returns:
        Dict containing success status
    """
    return await close_browser()

@mcp.tool()
async def browser_create_new_session(headless: bool = True) -> Dict[str, Any]:
    """
    Create a new browser session, replacing any existing session.
    
    This tool creates a fresh browser instance, closing any existing session first.
    Use this when you need to start browser automation or when the current session 
    becomes invalid. After creating a session, use browser_navigate_to_url() to visit a page.

    ! You should try create / delete tabs first, rather than shut down the entire page and reopen
    carefully use this function
    
    Args:
        headless: Whether to run browser in headless mode (default: True)
        
    Returns:
        Dict containing success status, session info, and next steps
    """
    return await create_new_browser_session(headless)

@mcp.tool()
async def browser_get_session_status() -> Dict[str, Any]:
    """
    Get the current browser session status and information.
    
    This tool checks if there's an active browser session and provides current page
    information if available. Use this to diagnose session issues or check readiness.
    
    Returns:
        Dict containing session status, current URL, title, and recommendations
    """
    return await get_browser_session_status()

@mcp.tool()
async def browser_switch_tabs(tab_index: Optional[int] = None, tab_handle: Optional[str] = None) -> Dict[str, Any]:
    """
    Switch to a specific browser tab by index or window handle.
    
    Args:
        tab_index: Index of the tab to switch to (0-based). If not provided and no tab_handle, switches to next tab
        tab_handle: Window handle of the specific tab to switch to
        
    Returns:
        Dict containing success status and tab information
    """
    return await switch_browser_tabs(tab_index, tab_handle)

@mcp.tool()
async def browser_get_all_tab_descriptions() -> Dict[str, Any]:
    """
    Get descriptions of all open browser tabs including titles, URLs, and current tab status.
    
    Returns:
        Dict containing all tab information with count, titles, URLs, handles, and which tab is current
    """
    return await get_all_browser_tab_descriptions()

@mcp.tool()
async def browser_open_new_tab(url: Optional[str] = None) -> Dict[str, Any]:
    """
    Open a new browser tab and optionally navigate to a URL.
    
    Args:
        url: Optional URL to navigate to in the new tab
        
    Returns:
        Dict containing success status, new tab handle, and URL if provided
    """
    return await open_new_browser_tab(url)

@mcp.tool()
async def browser_close_current_tab() -> Dict[str, Any]:
    """
    Close the current browser tab and automatically switch to another available tab.
    
    Note: Cannot close the last remaining tab - will return error if only one tab is open.
    
    Returns:
        Dict containing success status
    """
    return await close_current_browser_tab()

@mcp.tool()
async def browser_find_element_by_id(element_id: str, timeout: int = 10) -> Dict[str, Any]:
    """
    Find an element by its ID attribute and return basic information about it.
    
    Args:
        element_id: The ID of the element to find
        timeout: Timeout in seconds to wait for the element
        
    Returns:
        Dict containing success status, element information (tag name, text preview, 
        display status, enabled status), and session status
    """
    return await find_element_by_id(element_id, timeout)

if __name__ == "__main__":
    mcp.run()
