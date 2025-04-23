### Step 1: Extract Paragraphs and Title from the HTML File
Your articles are composed of `<p>` tags, and the article title is in the only `<h1>` tag on the page. We’ll use Python with the `BeautifulSoup` library to parse the HTML file and extract this content.

- **Extract Paragraphs**: Read the HTML file and collect the text within all `<p>` tags.
- **Extract Title**: Get the text from the `<h1>` tag to use as the base name for our files.

Here’s a sample implementation:

```python
from bs4 import BeautifulSoup

def extract_paragraphs(html_file):
    with open(html_file, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    paragraphs = [p.get_text().strip() for p in soup.find_all("p")]
    if not paragraphs:
        raise ValueError("No paragraphs found in the HTML file.")
    return paragraphs

def extract_title(html_file):
    with open(html_file, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    h1 = soup.find("h1")
    return h1.get_text().strip() if h1 else "Untitled"
```

---

### Step 2: Group Paragraphs into Pairs
You want to process the paragraphs in groups of two. For an article with 7 paragraphs, this means 3 groups of 2 paragraphs each and 1 group with the remaining paragraph (2+2+2+1), resulting in 4 groups.

- **Grouping Logic**: Use list slicing to create groups of up to 2 paragraphs each.
- **Example**: If `paragraphs = ["p1", "p2", "p3", "p4", "p5", "p6", "p7"]`, the groups would be `[["p1", "p2"], ["p3", "p4"], ["p5", "p6"], ["p7"]]`.

Here’s the function:

```python
def group_paragraphs(paragraphs, group_size=2):
    return [paragraphs[i:i + group_size] for i in range(0, len(paragraphs), group_size)]
```

---

### Step 3: Generate MP3 Files Using Play-AI TTS via Groq Inference
For each group, combine the paragraphs into a single string and send it to the Play-AI TTS service using the Groq API. Name each generated MP3 file as `<article_title>_<number>.mp3`, where the number (1, 2, 3, etc.) corresponds to the group’s order.

- **Sanitize Filename**: Ensure the title is safe for filenames by removing or replacing invalid characters.
- **API Call**: Send the text to the TTS service and save the audio response as an MP3.

Assuming you have a Groq API key stored in an environment variable `GROQ_API_KEY`, here’s the code:

```python
import requests
import re
import os

def sanitize_filename(title):
    return re.sub(r'[^a-zA-Z0-9_]', '_', title)

def generate_mp3(text_group, title, index):
    API_KEY = os.getenv("GROQ_API_KEY")
    if not API_KEY:
        raise ValueError("GROQ_API_KEY environment variable not set.")
    
    url = "https://api.groq.com/tts"  # Replace with actual Groq TTS endpoint
    headers = {"Authorization": f"Bearer {API_KEY}"}
    text = " ".join(text_group)  # Combine paragraphs with a space
    data = {"text": text, "model": "playai-dialog"}  # Adjust model name as per documentation
    
    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        raise Exception(f"TTS API error: {response.text}")
    
    mp3_file = f"{sanitize_filename(title)}_{index}.mp3"
    with open(mp3_file, "wb") as f:
        f.write(response.content)
    print(f"Generated MP3: {mp3_file}")
    return mp3_file
```
---

### Step 4: Combine MP3 Files into a Single MP3 Using FFmpeg
After generating all MP3 files (e.g., `Article_Title_1.mp3`, `Article_Title_2.mp3`, etc.), combine them into one MP3 file named `<article_title>.mp3` using FFmpeg’s `concat` demuxer.

- **Create a List File**: Write a text file listing all MP3 files.
- **Run FFmpeg**: Use the `subprocess` module to execute the FFmpeg command.

Here’s the function:

```python
import subprocess

def combine_mp3s(mp3_list, output_file):
    list_file = "mp3list.txt"
    with open(list_file, "w") as f:
        for mp3 in mp3_list:
            f.write(f"file '{mp3}'\n")
    
    cmd = ["ffmpeg", "-f", "concat", "-i", list_file, "-c", "copy", output_file]
    subprocess.run(cmd, check=True)
    os.remove(list_file)  # Clean up the list file
    print(f"Combined MP3: {output_file}")
```

The `-c copy` option ensures concatenation without re-encoding, assuming all MP3s from the TTS service have compatible formats.

---

### Step 5: Generate a Waveform Video
Pass the combined MP3 file to your existing Python script (`generate_waveform.py`) to create a video named `<article_title>.mp4`.

- **Assumption**: Your script accepts two arguments: the input audio file and the output video file.
- **Execution**: Use `subprocess` to call the script.

Here’s the function:

```python
def generate_waveform_video(audio_file, video_file):
    cmd = ["python", "generate_waveform.py", audio_file, video_file]
    subprocess.run(cmd, check=True)
    print(f"Generated video: {video_file}")
```

---

### Putting It All Together
Combine these steps into a main script that takes the HTML file as a command-line argument:

```python
import sys

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <html_file>")
        sys.exit(1)
    
    html_file = sys.argv[1]
    
    # Extract content
    paragraphs = extract_paragraphs(html_file)
    title = sanitize_filename(extract_title(html_file))
    
    # Group paragraphs
    groups = group_paragraphs(paragraphs, 2)
    
    # Generate MP3s
    mp3_files = []
    for i, group in enumerate(groups, 1):
        mp3_file = generate_mp3(group, title, i)
        mp3_files.append(mp3_file)
    
    # Combine MP3s
    combined_mp3 = f"{title}.mp3"
    combine_mp3s(mp3_files, combined_mp3)
    
    # Generate video
    video_file = f"{title}.mp4"
    generate_waveform_video(combined_mp3, video_file)
```

---

### Requirements
- **Libraries**: Install `beautifulsoup4` and `requests` via pip:
  ```bash
  pip install beautifulsoup4 requests
  ```
- **FFmpeg**: Ensure FFmpeg is installed and accessible from the command line.
- **Groq API Key**: Set the `GROQ_API_KEY` environment variable:
  ```bash
  export GROQ_API_KEY="your_api_key_here"
  ```
- **Waveform Script**: Ensure `generate_waveform.py` is in the same directory and works as expected.

---

### Execution
Run the script with your HTML file:
```bash
python script.py article.html
```

For an article with 7 paragraphs, this will:
- Generate `Article_Title_1.mp3`, `Article_Title_2.mp3`, `Article_Title_3.mp3`, `Article_Title_4.mp3`.
- Combine them into `Article_Title.mp3`.
- Produce `Article_Title.mp4` with the waveform video.
