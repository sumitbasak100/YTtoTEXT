from flask import Flask, request, jsonify
from pytube import YouTube

app = Flask(__name__)

def convert_youtube_to_text(url, language_code='en'):
    try:
        yt = YouTube(url)
        captions = yt.captions.get_by_language_code(language_code)
        if captions:
            text = captions.generate_srt_captions()
            return text.strip()
        else:
            available_languages = ', '.join(yt.captions.keys())
            return f"No captions available for '{language_code}'. Available languages: {available_languages}."
    except Exception as e:
        return str(e)

@app.route('/convert', methods=['POST'])
def convert():
    url = request.form.get('url')
    if not url:
        return jsonify(error="No URL provided"), 400

    language_code = request.form.get('language_code', 'en')
    text = convert_youtube_to_text(url, language_code)

    return jsonify(text=text), 200

if __name__ == "__main__":
    app.run(debug=True)
