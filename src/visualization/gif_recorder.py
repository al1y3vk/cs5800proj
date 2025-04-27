"""
GIF recording functionality for algorithm visualizations
"""
import os
import time
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from PIL import Image

class VisualizationRecorder:
    """
    Recorder for creating GIFs from algorithm visualization
    """
    
    def __init__(self, output_dir="output"):
        """
        Initialize the recorder
        
        Args:
            output_dir: Directory to save GIFs
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # List to store frames
        self.frames = []
        self.recording = False
        self.last_capture_time = 0
        self.capture_interval = 0.1  # seconds between frames
        
    def start_recording(self):
        """Start recording frames"""
        self.frames = []
        self.recording = True
        self.last_capture_time = 0
        print("GIF recording started")
        
    def stop_recording(self):
        """Stop recording frames"""
        self.recording = False
        print(f"GIF recording stopped with {len(self.frames)} frames")
        
    def capture_frame(self, fig):
        """
        Capture the current state of the figure as a frame
        
        Args:
            fig: Matplotlib figure to capture
        """
        if not self.recording:
            return
            
        # Only capture frames at regular intervals to keep the GIF a reasonable size
        current_time = time.time()
        if current_time - self.last_capture_time < self.capture_interval:
            return
            
        self.last_capture_time = current_time
        
        # Use the most reliable method - save to temp file and load
        # This works with all backends
        try:
            temp_file = os.path.join(self.output_dir, "_temp_frame.png")
            fig.savefig(temp_file, dpi=fig.dpi, format='png', bbox_inches='tight')
            image = Image.open(temp_file)
            self.frames.append(image.copy())
            # Clean up the temporary file
            if os.path.exists(temp_file):
                os.remove(temp_file)
        except Exception as e:
            print(f"Warning: Unable to capture frame: {e}")
        
    def save_gif(self, filename, fps=10):
        """
        Save recorded frames as an animated GIF
        
        Args:
            filename: Name of the GIF file
            fps: Frames per second
            
        Returns:
            str: Path to the created GIF file or None if no frames
        """
        if not self.frames:
            print("No frames to save")
            return None
            
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Ensure filename has .gif extension
        if not filename.lower().endswith('.gif'):
            filename += '.gif'
            
        filepath = os.path.join(self.output_dir, filename)
        
        # Create the GIF
        duration = 1000 // fps  # Duration of each frame in milliseconds
        
        # Save the frames as a GIF
        self.frames[0].save(
            filepath,
            format='GIF',
            append_images=self.frames[1:],
            save_all=True,
            duration=duration,
            loop=0,  # Loop forever
            optimize=False
        )
        
        print(f"Saved GIF with {len(self.frames)} frames to {filepath}")
        self.frames = []  # Clear frames after saving
        
        return filepath 