from flask import Flask, request, jsonify
from pytube import YouTube
import re

app = Flask(__name__)

def clean_srt_captions(srt_text):
    # Remove timestamps and blank lines from SRT text
    return re.sub(r'\d+\n[\d:,]+ --> [\d:,]+\n', '', srt_text).strip()

def convert_youtube_to_text(url, language_code='en'):
    try:
        yt = YouTube(url)
        captions = yt.captions.get_by_language_code(language_code)
        if captions:
            srt_text = captions.generate_srt_captions()
            text = clean_srt_captions(srt_text)
            return {"text": text}
        else:
            available_languages = ', '.join(yt.captions.keys())
            return {"error": f"No captions available for '{language_code}'. Available languages: {available_languages}."}
    except Exception as e:
        return {"error": str(e)}

@app.route('/convert', methods=['POST'])
def convert():
    url = request.form.get('url')
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    language_code = request.form.get('language_code', 'en')
    response = convert_youtube_to_text(url, language_code)

    return jsonify(response), 200

if __name__ == "__main__":
    app.run(debug=True)
