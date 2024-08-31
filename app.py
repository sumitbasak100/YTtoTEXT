from flask import Flask, request, jsonify
from pytube import YouTube
import re
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import JSONFormatter

app = Flask(__name__)

def clean_srt_captions(srt_text):
    # Remove timestamps and blank lines from SRT text
    return re.sub(r'\d+\n[\d:,]+ --> [\d:,]+\n', '', srt_text).strip()

def get_pytube_captions(url):
    try:
        yt = YouTube(url)
        available_captions = yt.captions
        available_languages = yt.captions.keys()

        # Priority for preferred languages
        preferred_languages = ['en', 'en_auto']
        for lang in preferred_languages:
            if lang in available_languages:
                language_code = lang
                break
        else:
            # Fallback to the first available language if preferred languages are not available
            language_code = next(iter(available_languages), None)

        if language_code:
            captions = yt.captions.get_by_language_code(language_code)
            srt_text = captions.generate_srt_captions()
            text = clean_srt_captions(srt_text)
            return {"text": text}
        else:
            available_languages_str = ', '.join(available_languages)
            return {"error": f"No captions available. Available languages: {available_languages_str}."}
    except Exception as e:
        return {"error": str(e)}

def get_youtube_transcript(url):
    try:
        video_id = url.split('v=')[-1]
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'en_auto'])
        formatter = JSONFormatter()
        formatted_transcript = formatter.format_transcript(transcript)
        return {"text": formatted_transcript}
    except Exception as e:
        return {"error": str(e)}

@app.route('/convert', methods=['POST'])
def convert():
    url = request.form.get('url')
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    # First try to get captions using pytube
    response = get_pytube_captions(url)
    
    if "error" in response:
        # If pytube fails, use youtube_transcript_api as fallback
        response = get_youtube_transcript(url)

    return jsonify(response), 200

if __name__ == "__main__":
    app.run(debug=True)
