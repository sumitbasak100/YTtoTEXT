from flask import Flask, request, jsonify
from pytube import YouTube
import re

app = Flask(__name__)

def clean_srt_captions(srt_text):
    # Remove timestamps and blank lines from SRT text
    return re.sub(r'\d+\n[\d:,]+ --> [\d:,]+\n', '', srt_text).strip()

def convert_youtube_to_text(url, language_code):
    try:
        yt = YouTube(url)
        available_languages = yt.captions.keys()
        
        if not language_code:
            # Use the first available language code if none is provided
            language_code = next(iter(available_languages), None)

        if language_code and language_code in available_languages:
            captions = yt.captions.get_by_language_code(language_code)
            srt_text = captions.generate_srt_captions()
            text = clean_srt_captions(srt_text)
            return {"text": text}
        else:
            available_languages_str = ', '.join(available_languages)
            return {"error": f"No captions available for '{language_code}'. Available languages: {available_languages_str}."}
    except Exception as e:
        return {"error": str(e)}

@app.route('/convert', methods=['POST'])
def convert():
    url = request.form.get('url')
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    language_code = request.form.get('language_code')
    response = convert_youtube_to_text(url, language_code)

    return jsonify(response), 200

if __name__ == "__main__":
    app.run(debug=True)
