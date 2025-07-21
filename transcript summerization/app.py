from flask import Flask, render_template, request
from youtube_transcript_api import YouTubeTranscriptApi
from transformers import pipeline
import re

app = Flask(__name__)
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def extract_video_id(url):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    return match.group(1) if match else None

def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([entry['text'] for entry in transcript])
    except:
        return None

def summarize_text(text):
    max_chunk = 1000
    chunks = [text[i:i + max_chunk] for i in range(0, len(text), max_chunk)]
    summary = ""
    for chunk in chunks:
        result = summarizer(chunk, max_length=200, min_length=50, do_sample=False)
        summary += result[0]['summary_text'] + " "
    return summary.strip()

@app.route("/", methods=["GET", "POST"])
def index():
    summary = ""
    error = ""
    if request.method == "POST":
        url = request.form["url"]
        video_id = extract_video_id(url)
        if not video_id:
            error = "Invalid YouTube URL."
        else:
            transcript = get_transcript(video_id)
            if transcript:
                summary = summarize_text(transcript)
            else:
                error = "Transcript not available for this video."
    return render_template("index.html", summary=summary, error=error)

if __name__ == "__main__":
    app.run(debug=True)
