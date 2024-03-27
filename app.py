from flask import Flask, request, jsonify
from pytube import YouTube

app = Flask(__name__)

def convert_youtube_to_text(url):
    try:
        yt = YouTube(url)
        captions = yt.captions.get_by_language_code('en')
        if captions:
            text = captions.generate_srt_captions()
            return text.strip()
        else:
            return "No English captions available for this video."
    except Exception as e:
        return str(e)

@app.route('/convert', methods=['POST'])
def convert():
    if 'url' not in request.form:
        return jsonify(error="No URL provided"), 400

    url = request.form['url']
    text = convert_youtube_to_text(url)

    return jsonify(text=text), 200

if __name__ == "__main__":
    app.run(debug=True)
