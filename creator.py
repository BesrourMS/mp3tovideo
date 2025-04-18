import os
import numpy as np
import matplotlib.pyplot as plt
from moviepy import AudioFileClip, VideoClip, CompositeAudioClip

# Check if file exists
audio_path = "podcast.mp3"  # Note I changed this to match your actual file name
if not os.path.exists(audio_path):
    print(f"Error: Audio file '{audio_path}' not found!")
    exit(1)

try:
    # Load audio with verbose output
    print(f"Loading audio from {audio_path}...")
    audio = AudioFileClip(audio_path)
    
    # Extract raw audio data
    fps = 44100
    print("Converting to numpy array...")
    samples = audio.to_soundarray(fps=fps)
    mono = samples.mean(axis=1)  # convert stereo→mono
    
    # Create a reusable figure for better performance
    print("Setting up figure...")
    fig, ax = plt.subplots(figsize=(6, 2))
    
    # Define a function to draw a waveform frame at time t
    def make_frame(t):
        # Clear previous frame content
        ax.clear()
        
        # Which samples to plot
        i = int(t * fps)
        window_size = int(0.05 * fps)  # 50ms window
        
        # Make sure we don't go beyond array bounds
        if i + window_size >= len(mono):
            window = mono[i:]
        else:
            window = mono[i:i + window_size]
        
        # Draw waveform
        ax.fill_between(np.linspace(0, 1, len(window)), window, color="black")
        ax.set_axis_off()
        ax.set_ylim(-1, 1)  # Normalize the y-axis range
        
        # Convert matplotlib figure to numpy array
        fig.canvas.draw()
        frame = np.array(fig.canvas.renderer.buffer_rgba())[:,:,:3]
        return frame
    
    # Create the video clip from the frame generator
    print("Creating video animation...")
    animation = VideoClip(make_frame, duration=audio.duration)
    
    # Update the audio - using new approach
    animation.audio = audio  # Direct assignment
    
    # Export with appropriate codec settings
    print("Rendering video...")
    output_file = "waveform_video.mp4"
    animation.write_videofile(output_file, fps=24, codec='libx264', audio_codec='aac')
    print(f"Video saved to {output_file}")
    
    # Clean up
    plt.close(fig)
    audio.close()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()