import cv2
import numpy as np
import ffmpeg
import logging
from datetime import datetime
from pathlib import Path
import requests
from config import API_ENDPOINT, API_KEY

logger = logging.getLogger('MeetBot')

class VideoHandler:
    """Handle video stream generation and processing."""
    
    def __init__(self):
        self.recording = False
        self.output_file = None
        self.writer = None
        # Create recordings directory if it doesn't exist
        Path("recordings").mkdir(exist_ok=True)
        
    def start_recording(self):
        """Start recording the video stream."""
        try:
            # Generate output filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.output_file = f"recordings/meet_recording_{timestamp}.mp4"
            
            # Initialize video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            self.writer = cv2.VideoWriter(
                self.output_file,
                fourcc,
                30.0,  # fps
                (1280, 720)  # resolution
            )
            
            self.recording = True
            logger.info(f"Started recording to {self.output_file}")
            
        except Exception as e:
            logger.error(f"Failed to start recording: {str(e)}")
            
    def stop_recording(self):
        """Stop recording and upload the video."""
        try:
            if self.recording and self.writer:
                self.writer.release()
                self.recording = False
                logger.info("Stopped recording")
                
                # Upload the video
                self._upload_video()
                
        except Exception as e:
            logger.error(f"Failed to stop recording: {str(e)}")
            
    def _upload_video(self):
        """Upload the recorded video to the specified API endpoint."""
        # Skip upload for now as API endpoint is not configured
        logger.info(f"Video saved to: {self.output_file}")
        logger.info("Video upload skipped - API endpoint not configured")
