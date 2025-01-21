from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import os
import pickle
import logging

logger = logging.getLogger('MeetBot')

class GoogleAuth:
    """Handle Google authentication process."""
    
    @staticmethod
    def login():
        """
        Perform Google account login using the Google API client library.
        
        Returns:
            bool: True if login successful, False otherwise
        """
        try:
            logger.info("Starting Google authentication process...")
            
            # Load credentials from file or prompt for new credentials
            creds = None
            if os.path.exists('token.pickle'):
                with open('token.pickle', 'rb') as token:
                    creds = pickle.load(token)
            
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    logger.info("Obtaining new credentials...")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'credentials.json', ['https://www.googleapis.com/auth/meet.readonly'])
                    creds = flow.run_local_server()
                
                # Save the credentials for the next run
                with open('token.pickle', 'wb') as token:
                    pickle.dump(creds, token)
            
            # Create the Meet API client
            meet_service = build('meet', 'v1', credentials=creds)
            
            # Verify access to Google Meet
            logger.info("Verifying Google Meet access...")
            meetings = meet_service.meetings().list().execute()
            if meetings:
                logger.info("Successfully verified Google Meet access")
                return True
            else:
                logger.error("Could not verify Google Meet access")
                return False
            
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            return False
