import os
import numpy as np
import matplotlib  # Import matplotlib first to set the backend
matplotlib.use('Agg')  # Set non-interactive backend to avoid GUI issues
import matplotlib.pyplot as plt
from moviepy import AudioFileClip, VideoClip

# --- Configuration ---
audio_path = "podcast.mp3"
output_file = "waveform_video_720p.mp4"
video_width = 1280
video_height = 720
video_fps = 24
audio_sample_rate = 44100
waveform_window_duration = 0.1
waveform_color = '#4682B4'
background_color = '#1E1E1E'
line_width = 1.5
encoding_preset = 'medium'
encoding_threads = 4
audio_codec_setting = 'aac'
audio_bitrate_setting = '192k'
# --- End Configuration ---

# 1. Check if audio file exists
if not os.path.exists(audio_path):
    print(f"Error: Audio file '{audio_path}' not found!")
    exit(1)

try:
    # 2. Load audio
    print(f"Loading audio from {audio_path}...")
    audio = AudioFileClip(audio_path)
    print(f"Audio duration: {audio.duration:.2f} seconds")

    # 3. Process audio data
    print(f"Converting audio to numpy array at {audio_sample_rate} Hz...")
    samples = audio.to_soundarray(fps=audio_sample_rate)
    mono_samples = samples.mean(axis=1) if samples.ndim > 1 else samples.flatten()

    max_abs_sample = np.max(np.abs(mono_samples))
    if max_abs_sample > 1.0:
        print(f"Normalizing audio samples...")
        mono_samples /= max_abs_sample

    # 4. Configure Matplotlib figure
    dpi = 100
    fig, ax = plt.subplots(
        figsize=(video_width/dpi, video_height/dpi),
        dpi=dpi,
        facecolor=background_color
    )
    ax.set_facecolor(background_color)
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)  # Remove padding
    ax.set_axis_off()
    ax.set_ylim(-1, 1)
    ax.set_xlim(0, 1)

    window_size_samples = int(waveform_window_duration * audio_sample_rate)

    # 5. Define frame generator
    def make_frame(t):
        current_sample = int(t * audio_sample_rate)
        start = max(0, current_sample - window_size_samples // 2)
        end = min(len(mono_samples), current_sample + window_size_samples // 2)
        window = mono_samples[start:end]

        ax.clear()
        if len(window) > 0:
            x = np.linspace(0, 1, len(window))
            ax.plot(x, window, color=waveform_color, lw=line_width)
        ax.set_ylim(-1, 1)
        ax.set_xlim(0, 1)
        
        fig.canvas.draw()
        frame = np.array(fig.canvas.renderer.buffer_rgba())[..., :3]
        return frame

    # 6. Create and export video
    print("Creating video animation...")
    animation = VideoClip(make_frame, duration=audio.duration)
    
    animation = animation.with_audio(audio)
    
    animation.write_videofile(
        output_file,
        fps=video_fps,
        codec='libx264',
        audio_codec=audio_codec_setting,
        preset=encoding_preset,
        threads=encoding_threads,
        audio_bitrate=audio_bitrate_setting
    )

    print(f"Video saved to {output_file}")

except Exception as e:
    print(f"\nError: {e}")
    traceback.print_exc()

finally:
    plt.close('all')
    if 'audio' in locals():
        audio.close()