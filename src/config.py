import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Google credentials
GOOGLE_EMAIL = os.getenv('GOOGLE_EMAIL')
GOOGLE_PASSWORD = os.getenv('GOOGLE_PASSWORD')

# Meeting configuration
DEFAULT_MEETING_LINK = os.getenv('DEFAULT_MEETING_LINK')
BOT_NAME = os.getenv('BOT_NAME', 'MeetingBot')
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', 30))

# API configuration
API_ENDPOINT = os.getenv('API_ENDPOINT')
API_KEY = os.getenv('API_KEY')

# Browser configuration
BROWSER_ARGS = [
    '--use-fake-ui-for-media-stream',
    '--use-fake-device-for-media-stream',
    '--disable-audio-output',
]
