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
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        self.driver = webdriver.Chrome(options=chrome_options)
        self.actions = ActionChains(self.driver)

        self._wait_for_dom_ready()
        self.logger.info("initialized browser")

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
        """Get the current page's HTML source."""
        html = self.driver.page_source
        self.logger.info("Retrieved current page HTML")
        return html

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



