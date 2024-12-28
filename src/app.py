from flask import Flask, render_template, request, jsonify
from scrapers.social_media_scraper import SocialMediaScraper
from models.clone_model import DigitalClone
from utils.text_processor import TextProcessor
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_clone', methods=['POST'])
def create_clone():
    social_media_url = request.form.get('url')
    if not social_media_url:
        return jsonify({'error': 'URL gerekli'}), 400

    try:
        # Sosyal medya verilerini çek
        scraper = SocialMediaScraper()
        profile_data = scraper.scrape_profile(social_media_url)

        # Metin işleme
        processor = TextProcessor()
        processed_data = processor.process(profile_data)

        # Dijital klon oluştur
        clone = DigitalClone()
        clone.train(processed_data)

        return jsonify({
            'success': True,
            'message': 'Dijital klon başarıyla oluşturuldu'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/ask_clone', methods=['POST'])
def ask_clone():
    question = request.form.get('question')
    if not question:
        return jsonify({'error': 'Soru gerekli'}), 400

    try:
        clone = DigitalClone()
        response = clone.generate_response(question)
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 