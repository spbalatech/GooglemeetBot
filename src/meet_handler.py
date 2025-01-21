from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
import logging
import time
from config import BOT_NAME, CHECK_INTERVAL

logger = logging.getLogger('MeetBot')

class MeetHandler:
    """Handle Google Meet interactions."""
    
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.is_meeting = False
        self.wait = WebDriverWait(driver, 10)
        
    def join_meeting(self, meeting_link: str) -> bool:
        """
        Join a Google Meet meeting.
        
        Args:
            meeting_link: URL of the meeting to join
            
        Returns:
            bool: True if successfully joined, False otherwise
        """
        logger.info(f"Attempting to join meeting: {meeting_link}")
        
        try:
            # Navigate to meeting
            self.driver.get(meeting_link)
            time.sleep(5)  # Wait for initial load
            
            # Handle media permissions
            try:
                dialog_button = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Allow')]"))
                )
                dialog_button.click()
            except TimeoutException:
                logger.info("No permission dialog found")
            
            # Disable media using keyboard shortcuts
            logger.info("Disabling media using keyboard shortcuts...")
            webdriver.ActionChains(self.driver).send_keys('d').perform()  # Disable camera
            time.sleep(0.5)
            webdriver.ActionChains(self.driver).send_keys('e').perform()  # Disable microphone
            time.sleep(0.5)
            
            # Check for meeting errors
            logger.info("Checking meeting status...")
            error_messages = [
                "You can't create a meeting yourself",
                "Meeting hasn't started",
                "Check your meeting code",
                "Meeting not found",
                "You aren't allowed to join this video call"
            ]
            
            try:
                for error in error_messages:
                    try:
                        error_elem = self.driver.find_element(By.XPATH, f"//*[contains(text(), '{error}')]")
                        if error_elem:
                            logger.error(f"Meeting error: {error}")
                            self.driver.save_screenshot('meeting_error.png')
                            return False
                    except NoSuchElementException:
                        continue
            except Exception as e:
                logger.warning(f"Error while checking meeting status: {str(e)}")
                
            # Look for join buttons
            logger.info("Looking for join options...")
            join_buttons = [
                (By.XPATH, "//button[contains(text(), 'Ask to join')]", 'request'),
                (By.XPATH, "//button[contains(text(), 'Join now')]", 'direct'),
                (By.CSS_SELECTOR, "[aria-label='Join meeting']", 'direct')
            ]
            
            join_success = False
            for by, selector, join_type in join_buttons:
                try:
                    button = self.wait.until(EC.element_to_be_clickable((by, selector)))
                    logger.info(f"Found {join_type} join button")
                    button.click()
                    join_success = True
                    
                    if join_type == 'request':
                        logger.info("Waiting for host to admit...")
                        try:
                            self.wait.until(
                                EC.presence_of_element_located(
                                    (By.XPATH, "//*[contains(text(), 'Meeting host will let you in soon')]")
                                )
                            )
                            logger.info("Waiting for host approval...")
                            time.sleep(10)  # Wait for host response
                        except TimeoutException:
                            logger.info("No waiting message found, might be admitted already")
                    
                    break
                except TimeoutException:
                    continue
                
            if not join_success:
                # Check for waiting messages
                waiting_messages = [
                    "Meeting hasn't started",
                    "Waiting for host",
                    "Meeting host will let you in soon"
                ]
                
                for message in waiting_messages:
                    try:
                        wait_elem = self.driver.find_element(By.XPATH, f"//*[contains(text(), '{message}')]")
                        if wait_elem:
                            logger.info(f"Waiting status: {message}")
                            return False
                    except NoSuchElementException:
                        continue
                
                logger.error("Could not find any way to join the meeting")
                self.driver.save_screenshot('join_error.png')
                return False
            
            # Verify we're in the meeting
            logger.info("Verifying meeting join...")
            success_indicators = [
                (By.CSS_SELECTOR, 'div[role="complementary"]'),
                (By.CSS_SELECTOR, '[aria-label="Meeting details"]'),
                (By.CSS_SELECTOR, '[aria-label="Chat with everyone"]'),
                (By.CSS_SELECTOR, '[aria-label="Show everyone"]')
            ]
            
            for by, selector in success_indicators:
                try:
                    self.wait.until(EC.presence_of_element_located((by, selector)))
                    self.is_meeting = True
                    logger.info(f"Successfully joined meeting (found {selector})")
                    return True
                except TimeoutException:
                    continue
            
            if not self.is_meeting:
                logger.error("Could not verify meeting join")
                self.driver.save_screenshot('verify_error.png')
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to join meeting: {str(e)}")
            self.driver.save_screenshot('join_error.png')
            return False
            
    def monitor_participants(self) -> bool:
        """
        Check if there are other participants in the meeting.
        
        Returns:
            bool: True if other participants present, False if only bot remains
        """
        try:
            # Open participants list
            participants_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label*="participant"]'))
            )
            participants_button.click()
            
            # Wait for list to load and get count
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="list"]')))
            participant_elements = self.driver.find_elements(By.CSS_SELECTOR, 'div[role="listitem"]')
            participant_count = len(participant_elements)
            
            logger.info(f"Found {participant_count} participants")
            
            # Check if bot is alone
            other_participants = participant_count > 1
            logger.info(f"Participants in meeting: {participant_count} (including bot)")
            
            return other_participants
            
        except Exception as e:
            logger.error(f"Failed to monitor participants: {str(e)}")
            return True  # Assume others present on error to avoid premature exit
            
    def leave_meeting(self):
        """Leave the current meeting."""
        try:
            if self.is_meeting:
                try:
                    # Look for leave button with multiple possible labels
                    leave_button = self.wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label*="leave" i], button[aria-label*="exit" i]'))
                    )
                    leave_button.click()
                    self.is_meeting = False
                    logger.info("Left meeting successfully")
                except Exception as e:
                    logger.error(f"Failed to find leave button: {str(e)}")
                
        except Exception as e:
            logger.error(f"Failed to leave meeting: {str(e)}")
