import logging
from pathlib import Path
import time

from config import DEFAULT_MEETING_LINK, BROWSER_ARGS, CHECK_INTERVAL
from logger import setup_logger
from auth import GoogleAuth
from meet_handler import MeetHandler
from video_handler import VideoHandler

def main():
    try:
        # Setup logging
        logger = setup_logger()
        logger.info("Application started")
        
        # Create necessary directories
        Path("logs").mkdir(exist_ok=True)
        Path("recordings").mkdir(exist_ok=True)
        
        # Initialize video handler
        video_handler = VideoHandler()
        
        # Set up Chrome WebDriver
        # No longer needed since we're using the Google API client library
            
        try:
            # Authenticate with Google
            logger.info("Authenticating with Google")
            if not GoogleAuth.login():
                logger.error("Authentication failed. Exiting...")
                return
            
            # Initialize meet handler
            meet_handler = MeetHandler(None)
                
            # Initialize meet handler
            meet_handler = MeetHandler(driver)
            
            # Validate and join meeting
            logger.info("Validating meeting link")
            if not DEFAULT_MEETING_LINK:
                logger.error("No meeting link provided. Please set DEFAULT_MEETING_LINK in .env file")
                return
                
            if not DEFAULT_MEETING_LINK.startswith('https://meet.google.com/'):
                logger.error("Invalid meeting link format. Must be a Google Meet link")
                return
                
            # Attempt to join meeting with retries
            join_attempts = 3
            for attempt in range(join_attempts):
                logger.info(f"Attempting to join meeting (attempt {attempt + 1}/{join_attempts})")
                if meet_handler.join_meeting(DEFAULT_MEETING_LINK):
                    break
                if attempt < join_attempts - 1:
                    logger.info(f"Join attempt {attempt + 1} failed, retrying in 5 seconds...")
                    time.sleep(5)
                else:
                    logger.error("Failed to join meeting after all attempts. Exiting...")
                    return
                
            # Start recording
            logger.info("Starting recording")
            video_handler.start_recording()
            
            # Monitor participants
            logger.info("Monitoring participants")
            while True:
                if not meet_handler.monitor_participants():
                    logger.info("No other participants in meeting. Stopping recording...")
                    break
                    
                time.sleep(CHECK_INTERVAL)
                
            # Stop recording and leave meeting
            logger.info("Stopping recording and leaving meeting")
            video_handler.stop_recording()
            meet_handler.leave_meeting()
            
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            
        finally:
            # Close browser
            logger.info("Closing browser")
            driver.quit()
            
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    main()
