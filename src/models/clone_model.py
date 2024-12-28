from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
import torch
import numpy as np
from collections import defaultdict, Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import json
import os

class DigitalClone:
    def __init__(self):
        # Model ve tokenizer'ı yükle
        self.model_name = "dbmdz/bert-base-turkish-uncased"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
        
        # Duygu analizi pipeline'ı
        self.sentiment_pipeline = pipeline("sentiment-analysis", 
                                        model=self.model_name, 
                                        tokenizer=self.tokenizer)
        
        # TF-IDF vektörleştirici
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        self.profile_data = None
        self.personality_vector = None
        self.word_preferences = defaultdict(int)
        self.sentiment_distribution = defaultdict(float)
        self.topic_interests = defaultdict(float)
        self.writing_style = {}
        self.response_cache = {}
        
        # Klon verilerini saklamak için dizin oluştur
        os.makedirs('clones', exist_ok=True)

    def train(self, processed_data):
        self.profile_data = processed_data
        
        # Kelime tercihlerini analiz et
        all_posts_text = []
        for post in processed_data['posts']:
            content = post['cleaned_text']
            all_posts_text.append(content)
            
            # Kelime frekansları
            for word, freq in post['word_frequency'].items():
                self.word_preferences[word] += freq
            
            # Duygu dağılımı
            sentiment = post['sentiment']
            for key, value in sentiment.items():
                self.sentiment_distribution[key] += value
        
        # Duygu dağılımını normalize et
        total_sentiment = sum(self.sentiment_distribution.values())
        if total_sentiment > 0:
            for key in self.sentiment_distribution:
                self.sentiment_distribution[key] /= total_sentiment
        
        # TF-IDF matrisini oluştur
        if all_posts_text:
            self.tfidf_matrix = self.vectorizer.fit_transform(all_posts_text)
            self.feature_names = self.vectorizer.get_feature_names_out()
        
        # Yazım stili analizi
        self._analyze_writing_style(processed_data['posts'])
        
        # Konu ilgi alanlarını analiz et
        self._analyze_topic_interests(processed_data)
        
        # Kişilik vektörü oluştur
        self._create_personality_vector()
        
        # Klon verilerini kaydet
        self._save_clone_data()

    def _analyze_writing_style(self, posts):
        total_posts = len(posts)
        if total_posts == 0:
            return
        
        # Yazım stili metriklerini hesapla
        avg_sentence_length = 0
        avg_word_length = 0
        punctuation_freq = defaultdict(int)
        emoji_freq = defaultdict(int)
        hashtag_freq = 0
        mention_freq = 0
        
        for post in posts:
            # Cümle uzunluğu
            sentences = post['sentences']
            if sentences:
                avg_sentence_length += len(sentences)
            
            # Kelime uzunluğu
            words = post['tokens']
            if words:
                avg_word_length += sum(len(word) for word in words) / len(words)
            
            # Noktalama işaretleri
            text = post['original_text']
            for char in text:
                if char in '.,!?':
                    punctuation_freq[char] += 1
            
            # Emoji kullanımı
            emojis = re.findall(r'[\U0001F300-\U0001F9FF]', text)
            for emoji in emojis:
                emoji_freq[emoji] += 1
            
            # Hashtag ve mention sayısı
            hashtag_freq += len(post['hashtags'])
            mention_freq += len(post['mentions'])
        
        self.writing_style = {
            'avg_sentence_length': avg_sentence_length / total_posts,
            'avg_word_length': avg_word_length / total_posts,
            'punctuation_freq': dict(punctuation_freq),
            'emoji_freq': dict(emoji_freq),
            'hashtag_usage': hashtag_freq / total_posts,
            'mention_usage': mention_freq / total_posts
        }

    def _analyze_topic_interests(self, processed_data):
        # Aggregate analysis'den konu dağılımını al
        if 'aggregate_analysis' in processed_data:
            analysis = processed_data['aggregate_analysis']
            
            # En sık kullanılan kelimelerden konu çıkarımı
            if 'top_words' in analysis:
                for word, freq in analysis['top_words']:
                    self.topic_interests[word] = freq
            
            # Hashtag'lerden konu çıkarımı
            if 'top_hashtags' in analysis:
                for hashtag, freq in analysis['top_hashtags']:
                    topic = hashtag.replace('#', '')
                    self.topic_interests[topic] += freq * 2  # Hashtag'lere daha fazla ağırlık ver

    def _create_personality_vector(self):
        if not self.profile_data:
            return

        features = []
        
        # Temel metin istatistikleri
        content_stats = self.profile_data['aggregate_analysis']['content_stats']
        features.extend([
            content_stats['avg_post_length'],
            content_stats['avg_word_length'],
            content_stats['avg_sentence_length'],
            content_stats['vocabulary_richness']
        ])
        
        # Duygu dağılımı
        sentiment_stats = self.profile_data['aggregate_analysis']['sentiment_stats']
        features.extend([
            sentiment_stats['positive'],
            sentiment_stats['negative'],
            sentiment_stats['neutral'],
            sentiment_stats['compound']
        ])
        
        # Yazım stili özellikleri
        features.extend([
            self.writing_style['avg_sentence_length'],
            self.writing_style['avg_word_length'],
            self.writing_style['hashtag_usage'],
            self.writing_style['mention_usage']
        ])
        
        # En sık kullanılan kelimeler
        top_words = self.profile_data['aggregate_analysis']['top_words']
        word_freqs = [freq for _, freq in top_words[:10]]
        features.extend(word_freqs)
        
        self.personality_vector = np.array(features)

    def generate_response(self, question):
        if not self.profile_data:
            return "Henüz yeterli veri toplanmadı."
            
        # Cache'den yanıt kontrolü
        cache_key = question.lower().strip()
        if cache_key in self.response_cache:
            return self.response_cache[cache_key]

        try:
            # Soruyu vektörleştir
            question_vector = self.vectorizer.transform([question])
            
            # En benzer içeriği bul
            similarities = cosine_similarity(question_vector, self.tfidf_matrix)
            most_similar_idx = similarities.argmax()
            
            # Benzer içeriğin duygusunu al
            similar_post = self.profile_data['posts'][most_similar_idx]
            similar_sentiment = similar_post['sentiment']
            
            # Cevap oluştur
            inputs = self.tokenizer(question, return_tensors="pt")
            
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs.input_ids,
                    max_length=150,
                    num_return_sequences=1,
                    temperature=0.7,
                    top_k=50,
                    top_p=0.95,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Yanıtı kişiselleştir
            response = self._personalize_response(response, similar_sentiment)
            
            # Yanıtı cache'e ekle
            self.response_cache[cache_key] = response
            
            return response
            
        except Exception as e:
            print(f"Response generation error: {str(e)}")
            return "Üzgünüm, şu anda yanıt oluşturamıyorum."

    def _personalize_response(self, response, sentiment):
        try:
            # Duygu tonunu ayarla
            if sentiment['compound'] > 0.05:
                response = self._add_positive_style(response)
            elif sentiment['compound'] < -0.05:
                response = self._add_negative_style(response)
            
            # Sık kullanılan kelimelerden ekle
            common_words = sorted(self.word_preferences.items(), 
                                key=lambda x: x[1], 
                                reverse=True)[:5]
            
            for word, _ in common_words:
                if word not in response.lower() and np.random.random() < 0.3:
                    response += f" {word}"
            
            # Yazım stilini uygula
            response = self._apply_writing_style(response)
            
            return response
            
        except Exception as e:
            print(f"Response personalization error: {str(e)}")
            return response

    def _add_positive_style(self, text):
        positive_emojis = ["😊", "👍", "🙌", "💪", "✨"]
        if np.random.random() < 0.5:
            text += f" {np.random.choice(positive_emojis)}"
        return text

    def _add_negative_style(self, text):
        negative_emojis = ["😔", "😕", "💔", "😢", "😞"]
        if np.random.random() < 0.5:
            text += f" {np.random.choice(negative_emojis)}"
        return text

    def _apply_writing_style(self, text):
        # Noktalama işareti kullanım sıklığına göre ekle
        for punct, freq in self.writing_style['punctuation_freq'].items():
            if freq > 0 and np.random.random() < 0.3:
                text += punct
        
        # Emoji kullanım sıklığına göre ekle
        for emoji, freq in self.writing_style['emoji_freq'].items():
            if freq > 0 and np.random.random() < 0.2:
                text += f" {emoji}"
        
        return text

    def _save_clone_data(self):
        # Klon verilerini JSON formatında kaydet
        clone_data = {
            'word_preferences': dict(self.word_preferences),
            'sentiment_distribution': dict(self.sentiment_distribution),
            'topic_interests': dict(self.topic_interests),
            'writing_style': self.writing_style,
            'personality_vector': self.personality_vector.tolist() if self.personality_vector is not None else None
        }
        
        with open('clones/clone_data.json', 'w', encoding='utf-8') as f:
            json.dump(clone_data, f, ensure_ascii=False, indent=4)

    def load_clone_data(self):
        # Kaydedilmiş klon verilerini yükle
        try:
            with open('clones/clone_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            self.word_preferences = defaultdict(int, data['word_preferences'])
            self.sentiment_distribution = defaultdict(float, data['sentiment_distribution'])
            self.topic_interests = defaultdict(float, data['topic_interests'])
            self.writing_style = data['writing_style']
            
            if data['personality_vector']:
                self.personality_vector = np.array(data['personality_vector'])
                
            return True
            
        except Exception as e:
            print(f"Clone data loading error: {str(e)}")
            return False 