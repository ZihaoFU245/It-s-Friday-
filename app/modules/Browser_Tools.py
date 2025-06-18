from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from app import config
import logging
import time
import re
from pathlib import Path

class BrowserTools:
    def __init__(self, headless = False):
        logging.basicConfig(filename=config.log_path,
                    filemode='a',
                    format='%(asctime)s - %(message)s',
                    level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)

        self.driver = webdriver.Chrome(options=chrome_options)
        self.actions = ActionChains(self.driver)

        self._stealth_patch()

        self._wait_for_dom_ready()
        self.logger.info("initialized browser")

    def _stealth_patch(self):
        # Patch navigator.webdriver, languages, plugins, etc.
        stealth_script = """
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
            Object.defineProperty(navigator, 'platform', { get: () => 'Win32' });
            Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 4 });
            Object.defineProperty(navigator, 'deviceMemory', { get: () => 8 });

            // Mimic Chrome-specific properties
            window.chrome = { runtime: {} };
        """
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": stealth_script
        })

    def _wait_for_dom_ready(self, timeout=10):
        """Wait until the DOM is fully loaded and rendered."""
        WebDriverWait(self.driver, timeout).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )

    def visit(self, url: str):
        self.driver.get(url)
        self._wait_for_dom_ready()
        self.logger.info(f"Visited {url}")
        return self.driver.page_source

    def get_html(self):
        """Get the current page's HTML source with CSS, JS, and href links filtered out."""
        try:
            # Use JavaScript to create a clean HTML structure
            clean_html = self.driver.execute_script("""
                // Clone the document to avoid modifying the original
                var clone = document.cloneNode(true);
                
                // Remove script tags
                var scripts = clone.querySelectorAll('script');
                scripts.forEach(function(script) { script.remove(); });
                
                // Remove style tags
                var styles = clone.querySelectorAll('style');
                styles.forEach(function(style) { style.remove(); });
                
                // Remove link tags (CSS, etc.)
                var links = clone.querySelectorAll('link');
                links.forEach(function(link) { link.remove(); });
                
                // Remove all style attributes and event handlers
                var allElements = clone.querySelectorAll('*');
                allElements.forEach(function(element) {
                    element.removeAttribute('style');
                    element.removeAttribute('onclick');
                    element.removeAttribute('onload');
                    element.removeAttribute('onmouseover');
                    element.removeAttribute('onmouseout');
                    element.removeAttribute('href');
                });
                
                return clone.documentElement.outerHTML;
            """)
            
            self.logger.info("Retrieved filtered HTML (no CSS/JS/href)")
            return clean_html
        except Exception as e:
            # Fallback to original method if JavaScript fails
            self.logger.warning(f"Failed to filter HTML, returning original: {str(e)}")
            html = self.driver.page_source
            self.logger.info("Retrieved current page HTML")
            return html

    def get_page_text(self):
        """Get all text content from the page, filtering out href links and keeping only readable text."""
        try:
            # Use JavaScript to extract clean text content
            page_text = self.driver.execute_script("""
                // Get all text nodes and visible text, excluding links
                var walker = document.createTreeWalker(
                    document.body,
                    NodeFilter.SHOW_TEXT,
                    {
                        acceptNode: function(node) {
                            // Skip text nodes that are inside script, style tags, or hidden elements
                            var parent = node.parentElement;
                            if (!parent) return NodeFilter.FILTER_REJECT;
                            
                            var tagName = parent.tagName.toLowerCase();
                            if (['script', 'style', 'noscript'].includes(tagName)) {
                                return NodeFilter.FILTER_REJECT;
                            }
                            
                            // Skip if parent is a link (a tag)
                            if (tagName === 'a') {
                                return NodeFilter.FILTER_REJECT;
                            }
                            
                            // Skip if text is just whitespace
                            if (node.textContent.trim() === '') {
                                return NodeFilter.FILTER_REJECT;
                            }
                            
                            return NodeFilter.FILTER_ACCEPT;
                        }
                    }
                );
                
                var textNodes = [];
                var node;
                while (node = walker.nextNode()) {
                    var text = node.textContent.trim();
                    if (text && text.length > 0) {
                        textNodes.push(text);
                    }
                }
                
                return textNodes.join(' ');
            """)
            
            # Clean up the text - remove extra whitespace and normalize
            if page_text:
                # Remove multiple spaces and normalize whitespace
                page_text = re.sub(r'\s+', ' ', page_text).strip()
                # Remove common navigation/UI text patterns
                page_text = re.sub(r'\b(Home|Navigation|Menu|Footer|Header|Sidebar|Skip to content)\b', '', page_text, flags=re.IGNORECASE)
                page_text = re.sub(r'\s+', ' ', page_text).strip()
            
            self.logger.info(f"Retrieved page text, {len(page_text)} characters")
            return page_text
            
        except Exception as e:
            self.logger.error(f"Failed to get page text: {str(e)}")
            # Fallback: get text from body element
            try:
                body_text = self.driver.find_element(By.TAG_NAME, "body").text
                self.logger.info("Retrieved page text using fallback method")
                return body_text
            except Exception as fallback_error:
                self.logger.error(f"Fallback method also failed: {str(fallback_error)}")
                return ""

    def find_element(self, selector, by=By.CSS_SELECTOR, timeout=10):
        """Find a single element using the specified selector."""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, selector))
            )
            self.logger.info(f"Found element: {selector}")
            return element
        except TimeoutException:
            self.logger.error(f"Element not found: {selector}")
            return None

    def find_element_by_id(self, element_id, timeout=10):
        """Find an element by its ID attribute."""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.ID, element_id))
            )
            self.logger.info(f"Found element by ID: {element_id}")
            return element
        except TimeoutException:
            self.logger.error(f"Element with ID '{element_id}' not found")
            return None

    def find_elements(self, selector, by=By.CSS_SELECTOR):
        """Find multiple elements using the specified selector."""
        try:
            elements = self.driver.find_elements(by, selector)
            self.logger.info(f"Found {len(elements)} elements: {selector}")
            return elements
        except NoSuchElementException:
            self.logger.error(f"Elements not found: {selector}")
            return []

    def click(self, selector, by=By.CSS_SELECTOR, timeout=10):
        """Click on an element specified by selector."""
        element = self.find_element(selector, by, timeout)
        if element:
            try:
                # Wait until element is clickable
                WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable((by, selector))
                )
                element.click()
                self.logger.info(f"Clicked element: {selector}")
                return True
            except Exception as e:
                self.logger.error(f"Failed to click element {selector}: {str(e)}")
                return False
        return False

    def click_coordinates(self, x, y):
        """Click at specific coordinates."""
        try:
            self.actions.move_by_offset(x, y).click().perform()
            self.actions.reset_actions()  # Reset to avoid offset accumulation
            self.logger.info(f"Clicked at coordinates: ({x}, {y})")
            return True
        except Exception as e:
            self.logger.error(f"Failed to click at coordinates ({x}, {y}): {str(e)}")
            return False

    def double_click(self, selector, by=By.CSS_SELECTOR, timeout=10):
        """Double-click on an element."""
        element = self.find_element(selector, by, timeout)
        if element:
            try:
                self.actions.double_click(element).perform()
                self.logger.info(f"Double-clicked element: {selector}")
                return True
            except Exception as e:
                self.logger.error(f"Failed to double-click element {selector}: {str(e)}")
                return False
        return False

    def right_click(self, selector, by=By.CSS_SELECTOR, timeout=10):
        """Right-click on an element."""
        element = self.find_element(selector, by, timeout)
        if element:
            try:
                self.actions.context_click(element).perform()
                self.logger.info(f"Right-clicked element: {selector}")
                return True
            except Exception as e:
                self.logger.error(f"Failed to right-click element {selector}: {str(e)}")
                return False
        return False

    def drag_and_drop(self, source_selector, target_selector, by=By.CSS_SELECTOR, timeout=10):
        """Drag an element from source to target."""
        source = self.find_element(source_selector, by, timeout)
        target = self.find_element(target_selector, by, timeout)
        
        if source and target:
            try:
                self.actions.drag_and_drop(source, target).perform()
                self.logger.info(f"Dragged from {source_selector} to {target_selector}")
                return True
            except Exception as e:
                self.logger.error(f"Failed to drag and drop: {str(e)}")
                return False
        return False

    def drag_by_offset(self, selector, x_offset, y_offset, by=By.CSS_SELECTOR, timeout=10):
        """Drag an element by a specific offset."""
        element = self.find_element(selector, by, timeout)
        if element:
            try:
                self.actions.drag_and_drop_by_offset(element, x_offset, y_offset).perform()
                self.logger.info(f"Dragged element {selector} by offset ({x_offset}, {y_offset})")
                return True
            except Exception as e:
                self.logger.error(f"Failed to drag by offset: {str(e)}")
                return False
        return False

    def scroll_to_element(self, selector, by=By.CSS_SELECTOR, timeout=10):
        """Scroll to bring an element into view."""
        element = self.find_element(selector, by, timeout)
        if element:
            try:
                self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                self.logger.info(f"Scrolled to element: {selector}")
                return True
            except Exception as e:
                self.logger.error(f"Failed to scroll to element {selector}: {str(e)}")
                return False
        return False

    def scroll_by_pixels(self, x_pixels, y_pixels):
        """Scroll by specific number of pixels."""
        try:
            self.driver.execute_script(f"window.scrollBy({x_pixels}, {y_pixels});")
            self.logger.info(f"Scrolled by pixels: ({x_pixels}, {y_pixels})")
            return True
        except Exception as e:
            self.logger.error(f"Failed to scroll by pixels: {str(e)}")
            return False

    def scroll_to_top(self):
        """Scroll to the top of the page."""
        try:
            self.driver.execute_script("window.scrollTo(0, 0);")
            self.logger.info("Scrolled to top of page")
            return True
        except Exception as e:
            self.logger.error(f"Failed to scroll to top: {str(e)}")
            return False

    def scroll_to_bottom(self):
        """Scroll to the bottom of the page."""
        try:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            self.logger.info("Scrolled to bottom of page")
            return True
        except Exception as e:
            self.logger.error(f"Failed to scroll to bottom: {str(e)}")
            return False

    def type_text(self, selector, text, by=By.CSS_SELECTOR, timeout=10, clear_first=True):
        """Type text into an input field."""
        element = self.find_element(selector, by, timeout)
        if element:
            try:
                if clear_first:
                    element.clear()
                element.send_keys(text)
                self.logger.info(f"Typed text into element {selector}: {text[:50]}...")
                return True
            except Exception as e:
                self.logger.error(f"Failed to type text into {selector}: {str(e)}")
                return False
        return False

    def press_key(self, key):
        """Press a specific key (e.g., Keys.ENTER, Keys.TAB)."""
        try:
            self.actions.send_keys(key).perform()
            self.logger.info(f"Pressed key: {key}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to press key {key}: {str(e)}")
            return False

    def get_element_text(self, selector, by=By.CSS_SELECTOR, timeout=10):
        """Get the text content of an element."""
        element = self.find_element(selector, by, timeout)
        if element:
            try:
                text = element.text
                self.logger.info(f"Retrieved text from element {selector}: {text[:50]}...")
                return text
            except Exception as e:
                self.logger.error(f"Failed to get text from {selector}: {str(e)}")
                return None
        return None

    def get_element_attribute(self, selector, attribute, by=By.CSS_SELECTOR, timeout=10):
        """Get a specific attribute value from an element."""
        element = self.find_element(selector, by, timeout)
        if element:
            try:
                value = element.get_attribute(attribute)
                self.logger.info(f"Retrieved attribute '{attribute}' from element {selector}: {value}")
                return value
            except Exception as e:
                self.logger.error(f"Failed to get attribute '{attribute}' from {selector}: {str(e)}")
                return None
        return None

    def wait_for_element(self, selector, by=By.CSS_SELECTOR, timeout=10):
        """Wait for an element to appear."""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, selector))
            )
            self.logger.info(f"Element appeared: {selector}")
            return element
        except TimeoutException:
            self.logger.error(f"Element did not appear within {timeout} seconds: {selector}")
            return None

    def wait_for_element_clickable(self, selector, by=By.CSS_SELECTOR, timeout=10):
        """Wait for an element to be clickable."""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, selector))
            )
            self.logger.info(f"Element became clickable: {selector}")
            return element
        except TimeoutException:
            self.logger.error(f"Element did not become clickable within {timeout} seconds: {selector}")
            return None

    def take_screenshot(self, filename=None):
        """Take a screenshot of the current page."""
        try:
            if filename is None:
                filename = f"screenshot_{int(time.time())}.png"
            
            # Ensure screenshots directory exists
            screenshots_dir = Path(config.log_path).parent / "screenshots"
            screenshots_dir.mkdir(exist_ok=True)
            
            filepath = screenshots_dir / filename
            self.driver.save_screenshot(str(filepath))
            self.logger.info(f"Screenshot saved: {filepath}")
            return str(filepath)
        except Exception as e:
            self.logger.error(f"Failed to take screenshot: {str(e)}")
            return None

    def get_current_url(self):
        """Get the current page URL."""
        try:
            url = self.driver.current_url
            self.logger.info(f"Current URL: {url}")
            return url
        except Exception as e:
            self.logger.error(f"Failed to get current URL: {str(e)}")
            return None

    def get_page_title(self):
        """Get the current page title."""
        try:
            title = self.driver.title
            self.logger.info(f"Page title: {title}")
            return title
        except Exception as e:
            self.logger.error(f"Failed to get page title: {str(e)}")
            return None

    def execute_javascript(self, script, *args):
        """Execute JavaScript code."""
        try:
            result = self.driver.execute_script(script, *args)
            self.logger.info(f"Executed JavaScript: {script[:100]}...")
            return result
        except Exception as e:
            self.logger.error(f"Failed to execute JavaScript: {str(e)}")
            return None

    def go_back(self):
        """Navigate back in browser history."""
        try:
            self.driver.back()
            self._wait_for_dom_ready()
            self.logger.info("Navigated back")
            return True
        except Exception as e:
            self.logger.error(f"Failed to navigate back: {str(e)}")
            return False

    def go_forward(self):
        """Navigate forward in browser history."""
        try:
            self.driver.forward()
            self._wait_for_dom_ready()
            self.logger.info("Navigated forward")
            return True
        except Exception as e:
            self.logger.error(f"Failed to navigate forward: {str(e)}")
            return False

    def refresh(self):
        """Refresh the current page."""
        try:
            self.driver.refresh()
            self._wait_for_dom_ready()
            self.logger.info("Page refreshed")
            return True
        except Exception as e:
            self.logger.error(f"Failed to refresh page: {str(e)}")
            return False

    def close(self):
        """Close the browser."""
        try:
            self.driver.quit()
            self.logger.info("Browser closed")
            return True
        except Exception as e:
            self.logger.error(f"Failed to close browser: {str(e)}")
            return False

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - automatically close browser."""
        self.close()

    def switch_tabs(self, tab_index=None, tab_handle=None):
        """Switch to a specific tab by index or window handle."""
        try:
            current_handles = self.driver.window_handles
            
            if tab_handle:
                # Switch by window handle
                if tab_handle in current_handles:
                    self.driver.switch_to.window(tab_handle)
                    self._wait_for_dom_ready()
                    self.logger.info(f"Switched to tab with handle: {tab_handle}")
                    return True
                else:
                    self.logger.error(f"Invalid tab handle: {tab_handle}")
                    return False
            
            elif tab_index is not None:
                # Switch by index
                if 0 <= tab_index < len(current_handles):
                    self.driver.switch_to.window(current_handles[tab_index])
                    self._wait_for_dom_ready()
                    self.logger.info(f"Switched to tab at index: {tab_index}")
                    return True
                else:
                    self.logger.error(f"Invalid tab index: {tab_index}. Available tabs: {len(current_handles)}")
                    return False
            
            else:
                # If no parameters provided, switch to the next tab
                current_handle = self.driver.current_window_handle
                current_index = current_handles.index(current_handle)
                next_index = (current_index + 1) % len(current_handles)
                self.driver.switch_to.window(current_handles[next_index])
                self._wait_for_dom_ready()
                self.logger.info(f"Switched to next tab (index {next_index})")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to switch tabs: {str(e)}")
            return False

    def get_all_tab_descriptions(self):
        """Get descriptions (title and URL) of all open tabs."""
        try:
            current_handle = self.driver.current_window_handle
            all_handles = self.driver.window_handles
            tab_descriptions = []
            
            for i, handle in enumerate(all_handles):
                try:
                    # Switch to the tab
                    self.driver.switch_to.window(handle)
                    
                    # Get tab information
                    title = self.driver.title
                    url = self.driver.current_url
                    is_current = (handle == current_handle)
                    
                    tab_descriptions.append({
                        'index': i,
                        'handle': handle,
                        'title': title,
                        'url': url,
                        'is_current': is_current
                    })
                    
                except Exception as e:
                    self.logger.error(f"Failed to get info for tab {i}: {str(e)}")
                    tab_descriptions.append({
                        'index': i,
                        'handle': handle,
                        'title': 'Error retrieving title',
                        'url': 'Error retrieving URL',
                        'is_current': False,
                        'error': str(e)
                    })
            
            # Switch back to the original tab
            self.driver.switch_to.window(current_handle)
            
            self.logger.info(f"Retrieved descriptions for {len(tab_descriptions)} tabs")
            return tab_descriptions
            
        except Exception as e:
            self.logger.error(f"Failed to get tab descriptions: {str(e)}")
            return []

    def open_new_tab(self, url=None):
        """Open a new tab and optionally navigate to a URL."""
        try:
            # Open new tab using JavaScript
            self.driver.execute_script("window.open('');")
            
            # Switch to the new tab (it will be the last one)
            new_handles = self.driver.window_handles
            self.driver.switch_to.window(new_handles[-1])
            
            if url:
                self.driver.get(url)
                self._wait_for_dom_ready()
            
            self.logger.info(f"Opened new tab" + (f" and navigated to {url}" if url else ""))
            return new_handles[-1]  # Return the handle of the new tab
            
        except Exception as e:
            self.logger.error(f"Failed to open new tab: {str(e)}")
            return None

    def close_current_tab(self):
        """Close the current tab and switch to another if available."""
        try:
            current_handles = self.driver.window_handles
            
            if len(current_handles) <= 1:
                self.logger.error("Cannot close the last remaining tab")
                return False
            
            current_handle = self.driver.current_window_handle
            self.driver.close()
            
            # Switch to the first remaining tab
            remaining_handles = [h for h in current_handles if h != current_handle]
            self.driver.switch_to.window(remaining_handles[0])
            self._wait_for_dom_ready()
            
            self.logger.info("Closed current tab and switched to another")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to close current tab: {str(e)}")
            return False
