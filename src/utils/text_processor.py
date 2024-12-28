import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.probability import FreqDist
from nltk.collocations import BigramCollocationFinder
from nltk.metrics import BigramAssocMeasures
from collections import Counter
import re
import numpy as np

class TextProcessor:
    def __init__(self):
        # NLTK gerekli dosyaları indir
        nltk.download('punkt')
        nltk.download('stopwords')
        nltk.download('vader_lexicon')
        nltk.download('averaged_perceptron_tagger')
        
        self.stop_words = set(stopwords.words('turkish'))
        self.sia = SentimentIntensityAnalyzer()

    def process(self, profile_data):
        if not profile_data or not profile_data.get('posts'):
            return None

        processed_data = {
            'posts': [],
            'aggregate_analysis': {
                'sentiment_stats': {
                    'positive': 0,
                    'negative': 0,
                    'neutral': 0,
                    'compound': 0
                },
                'content_stats': {
                    'avg_post_length': 0,
                    'avg_word_length': 0,
                    'avg_sentence_length': 0,
                    'vocabulary_richness': 0
                },
                'top_words': [],
                'top_bigrams': [],
                'top_hashtags': [],
                'top_mentions': [],
                'topic_distribution': {},
                'temporal_patterns': profile_data.get('temporal_patterns', {})
            },
            'profile_info': profile_data.get('profile_info', {}),
            'engagement_metrics': profile_data.get('engagement_metrics', {})
        }

        all_words = []
        all_sentences = []
        all_hashtags = []
        all_mentions = []
        
        # Her gönderiyi işle
        for post in profile_data['posts']:
            content = post.get('content', '')
            
            # Metin temizleme
            cleaned_text = self._clean_text(content)
            
            # Tokenization
            tokens = word_tokenize(cleaned_text)
            sentences = sent_tokenize(cleaned_text)
            
            # Stop words'leri kaldır
            filtered_tokens = [token for token in tokens if token not in self.stop_words]
            
            # Duygu analizi
            sentiment = self.sia.polarity_scores(cleaned_text)
            
            # Kelime frekansı
            word_freq = self._get_word_frequency(filtered_tokens)
            
            # Hashtag ve mention analizi
            hashtags = re.findall(r'#\w+', content)
            mentions = re.findall(r'@\w+', content)
            
            # Bigram analizi
            bigrams = list(nltk.bigrams(filtered_tokens))
            
            processed_post = {
                'original_text': content,
                'cleaned_text': cleaned_text,
                'tokens': tokens,
                'filtered_tokens': filtered_tokens,
                'sentences': sentences,
                'sentiment': sentiment,
                'word_frequency': word_freq,
                'hashtags': hashtags,
                'mentions': mentions,
                'bigrams': bigrams
            }
            
            # Orijinal post verilerini koru
            processed_post.update({k:v for k,v in post.items() if k not in processed_post})
            
            processed_data['posts'].append(processed_post)
            
            # Toplu analiz için veri toplama
            all_words.extend(filtered_tokens)
            all_sentences.extend(sentences)
            all_hashtags.extend(hashtags)
            all_mentions.extend(mentions)
            
            # Duygu istatistiklerini güncelle
            if sentiment['compound'] > 0.05:
                processed_data['aggregate_analysis']['sentiment_stats']['positive'] += 1
            elif sentiment['compound'] < -0.05:
                processed_data['aggregate_analysis']['sentiment_stats']['negative'] += 1
            else:
                processed_data['aggregate_analysis']['sentiment_stats']['neutral'] += 1
            
            processed_data['aggregate_analysis']['sentiment_stats']['compound'] += sentiment['compound']

        # Toplu analiz hesaplamaları
        if len(profile_data['posts']) > 0:
            # Ortalama değerleri hesapla
            processed_data['aggregate_analysis']['content_stats']['avg_post_length'] = len(all_words) / len(profile_data['posts'])
            processed_data['aggregate_analysis']['content_stats']['avg_word_length'] = sum(len(word) for word in all_words) / len(all_words) if all_words else 0
            processed_data['aggregate_analysis']['content_stats']['avg_sentence_length'] = len(all_words) / len(all_sentences) if all_sentences else 0
            
            # Kelime çeşitliliği (vocabulary richness)
            unique_words = set(all_words)
            processed_data['aggregate_analysis']['content_stats']['vocabulary_richness'] = len(unique_words) / len(all_words) if all_words else 0
            
            # En sık kullanılan kelimeler
            word_freq = FreqDist(all_words)
            processed_data['aggregate_analysis']['top_words'] = word_freq.most_common(20)
            
            # En sık kullanılan bigramlar
            bigram_finder = BigramCollocationFinder.from_words(all_words)
            processed_data['aggregate_analysis']['top_bigrams'] = bigram_finder.nbest(BigramAssocMeasures.likelihood_ratio, 10)
            
            # En sık kullanılan hashtag ve mentionlar
            hashtag_freq = Counter(all_hashtags)
            mention_freq = Counter(all_mentions)
            processed_data['aggregate_analysis']['top_hashtags'] = hashtag_freq.most_common(10)
            processed_data['aggregate_analysis']['top_mentions'] = mention_freq.most_common(10)
            
            # Normalize sentiment compound score
            processed_data['aggregate_analysis']['sentiment_stats']['compound'] /= len(profile_data['posts'])

        return processed_data

    def _clean_text(self, text):
        # URL'leri kaldır
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Emojileri kaldır
        text = re.sub(r'[\U00010000-\U0010ffff]', '', text)
        
        # Özel karakterleri kaldır ama noktalama işaretlerini koru
        text = re.sub(r'[^\w\s.,!?]', '', text)
        
        # Fazla boşlukları kaldır
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text.lower()

    def _get_word_frequency(self, tokens):
        # Stop words'leri kaldır
        tokens = [token for token in tokens if token not in self.stop_words]
        
        # Kelime frekansı hesapla
        freq_dist = FreqDist(tokens)
        return dict(freq_dist)

    def _extract_topics(self, texts, num_topics=5):
        # Basit konu çıkarımı - en sık geçen kelime gruplarına dayalı
        all_words = []
        for text in texts:
            tokens = word_tokenize(text.lower())
            tokens = [t for t in tokens if t not in self.stop_words and len(t) > 3]
            all_words.extend(tokens)
            
        word_freq = Counter(all_words)
        return dict(word_freq.most_common(num_topics)) 