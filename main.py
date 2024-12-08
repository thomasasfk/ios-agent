from flask import Flask, request, jsonify
import os, tempfile, openai
from flask.cli import load_dotenv
from functools import wraps

from agent import run_agent

load_dotenv()
app = Flask(__name__)
openai.api_key = os.getenv('OPENAI_API_KEY')
HEADER_KEY = os.getenv('HEADER_KEY')
HEADER_VALUE = os.getenv('HEADER_VALUE')

def require_auth_header(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.headers.get(HEADER_KEY) == HEADER_VALUE: return f(*args, **kwargs)
        return {}, 500
    return decorated_function

@app.route('/transcribe', methods=['POST'])
@require_auth_header
def transcribe_audio():
    temp_file = None
    try:
        if not request.data: return jsonify({'error': 'No audio data'}), 400
        temp_file = tempfile.NamedTemporaryFile(suffix='.m4a', delete=False)
        temp_file.write(request.data)
        temp_file.close()
        with open(temp_file.name, 'rb') as audio_file:
            transcription = openai.audio.translations.create(
              model="whisper-1",
              file=audio_file,
              response_format="text"
            )
            result = run_agent(transcription)
            return result
    finally:
        if temp_file and os.path.exists(temp_file.name): os.unlink(temp_file.name)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=1337)