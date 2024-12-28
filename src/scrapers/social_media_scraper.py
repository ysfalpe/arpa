from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from datetime import datetime
import time
import re

class SocialMediaScraper:
    def __init__(self):
        service = Service(ChromeDriverManager().install())
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')  # Tarayıcıyı arka planda çalıştır
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)

    def scrape_profile(self, url):
        try:
            self.driver.get(url)
            time.sleep(3)

            profile_data = {
                'posts': [],
                'profile_info': {},
                'engagement_metrics': {},
                'content_analysis': {},
                'temporal_patterns': {},
                'platform': ''
            }

            if 'twitter.com' in url:
                profile_data = self._scrape_twitter()
                profile_data['platform'] = 'twitter'
            elif 'instagram.com' in url:
                profile_data = self._scrape_instagram()
                profile_data['platform'] = 'instagram'
            elif 'linkedin.com' in url:
                profile_data = self._scrape_linkedin()
                profile_data['platform'] = 'linkedin'
            else:
                raise ValueError('Desteklenmeyen sosyal medya platformu')

            return profile_data

        finally:
            self.driver.quit()

    def _scrape_twitter(self):
        profile_data = {
            'posts': [],
            'profile_info': {},
            'engagement_metrics': {
                'total_tweets': 0,
                'total_likes': 0,
                'total_retweets': 0,
                'total_replies': 0
            },
            'content_analysis': {
                'hashtags': [],
                'mentions': [],
                'media_count': 0,
                'urls': []
            },
            'temporal_patterns': {
                'posting_hours': {},
                'posting_days': {}
            }
        }

        try:
            # Profil bilgilerini topla
            profile_info = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="UserName"]')))
            profile_data['profile_info']['name'] = profile_info.text
            
            bio = self.driver.find_element(By.CSS_SELECTOR, '[data-testid="UserDescription"]').text
            profile_data['profile_info']['bio'] = bio

            # Tweet'leri topla
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            
            for _ in range(10):  # Daha fazla tweet için scroll sayısını artırdık
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                tweet_elements = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid="tweet"]')
                
                for tweet in tweet_elements:
                    try:
                        tweet_data = {}
                        
                        # Tweet metni
                        text_element = tweet.find_element(By.CSS_SELECTOR, '[data-testid="tweetText"]')
                        tweet_data['content'] = text_element.text
                        
                        # Etkileşim metrikleri
                        metrics = tweet.find_elements(By.CSS_SELECTOR, '[data-testid$="-count"]')
                        for metric in metrics:
                            metric_id = metric.get_attribute('data-testid')
                            if 'like' in metric_id:
                                tweet_data['likes'] = int(metric.text or 0)
                                profile_data['engagement_metrics']['total_likes'] += tweet_data['likes']
                            elif 'retweet' in metric_id:
                                tweet_data['retweets'] = int(metric.text or 0)
                                profile_data['engagement_metrics']['total_retweets'] += tweet_data['retweets']
                            elif 'reply' in metric_id:
                                tweet_data['replies'] = int(metric.text or 0)
                                profile_data['engagement_metrics']['total_replies'] += tweet_data['replies']
                        
                        # Hashtag ve mention analizi
                        hashtags = re.findall(r'#\w+', tweet_data['content'])
                        mentions = re.findall(r'@\w+', tweet_data['content'])
                        urls = re.findall(r'https?://\S+', tweet_data['content'])
                        
                        tweet_data['hashtags'] = hashtags
                        tweet_data['mentions'] = mentions
                        tweet_data['urls'] = urls
                        
                        profile_data['content_analysis']['hashtags'].extend(hashtags)
                        profile_data['content_analysis']['mentions'].extend(mentions)
                        profile_data['content_analysis']['urls'].extend(urls)
                        
                        # Medya içeriği kontrolü
                        media_elements = tweet.find_elements(By.CSS_SELECTOR, '[data-testid="tweetPhoto"], [data-testid="tweetVideo"]')
                        tweet_data['has_media'] = len(media_elements) > 0
                        profile_data['content_analysis']['media_count'] += len(media_elements)
                        
                        # Zaman analizi
                        try:
                            time_element = tweet.find_element(By.CSS_SELECTOR, 'time')
                            tweet_time = time_element.get_attribute('datetime')
                            tweet_datetime = datetime.fromisoformat(tweet_time.replace('Z', '+00:00'))
                            
                            hour = tweet_datetime.hour
                            day = tweet_datetime.strftime('%A')
                            
                            profile_data['temporal_patterns']['posting_hours'][hour] = profile_data['temporal_patterns']['posting_hours'].get(hour, 0) + 1
                            profile_data['temporal_patterns']['posting_days'][day] = profile_data['temporal_patterns']['posting_days'].get(day, 0) + 1
                            
                            tweet_data['timestamp'] = tweet_time
                        except:
                            pass
                        
                        profile_data['posts'].append(tweet_data)
                        profile_data['engagement_metrics']['total_tweets'] += 1
                        
                    except Exception as e:
                        continue
                
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
                
        except Exception as e:
            print(f"Twitter scraping error: {str(e)}")
            
        return profile_data

    def _scrape_instagram(self):
        profile_data = {
            'posts': [],
            'profile_info': {},
            'engagement_metrics': {
                'total_posts': 0,
                'total_likes': 0,
                'total_comments': 0
            },
            'content_analysis': {
                'hashtags': [],
                'mentions': [],
                'media_types': {
                    'image': 0,
                    'video': 0,
                    'carousel': 0
                }
            },
            'temporal_patterns': {
                'posting_hours': {},
                'posting_days': {}
            }
        }

        try:
            # Profil bilgilerini topla
            try:
                profile_info = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '._aa_c')))
                profile_data['profile_info']['name'] = profile_info.find_element(By.CSS_SELECTOR, 'h2').text
                bio_elements = profile_info.find_elements(By.CSS_SELECTOR, '._aacl._aacp')
                if bio_elements:
                    profile_data['profile_info']['bio'] = bio_elements[0].text
            except:
                pass

            # Gönderileri topla
            posts = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '._aagv')))
            
            for post in posts[:30]:  # İlk 30 gönderi
                try:
                    post.click()
                    time.sleep(1)
                    
                    post_data = {}
                    
                    # Gönderi içeriği
                    try:
                        content = self.driver.find_element(By.CSS_SELECTOR, '._a9zs').text
                        post_data['content'] = content
                        
                        # Hashtag ve mention analizi
                        hashtags = re.findall(r'#\w+', content)
                        mentions = re.findall(r'@\w+', content)
                        
                        post_data['hashtags'] = hashtags
                        post_data['mentions'] = mentions
                        
                        profile_data['content_analysis']['hashtags'].extend(hashtags)
                        profile_data['content_analysis']['mentions'].extend(mentions)
                    except:
                        post_data['content'] = ''
                    
                    # Medya türü analizi
                    try:
                        if self.driver.find_elements(By.CSS_SELECTOR, '._aatk._aatl'):
                            post_data['media_type'] = 'carousel'
                            profile_data['content_analysis']['media_types']['carousel'] += 1
                        elif self.driver.find_elements(By.CSS_SELECTOR, '._aagu'):
                            post_data['media_type'] = 'video'
                            profile_data['content_analysis']['media_types']['video'] += 1
                        else:
                            post_data['media_type'] = 'image'
                            profile_data['content_analysis']['media_types']['image'] += 1
                    except:
                        pass
                    
                    # Etkileşim metrikleri
                    try:
                        likes = self.driver.find_element(By.CSS_SELECTOR, '._aacl._aaco._aacw._aacx._aada._aade').text
                        likes = int(re.sub(r'[^\d]', '', likes))
                        post_data['likes'] = likes
                        profile_data['engagement_metrics']['total_likes'] += likes
                    except:
                        post_data['likes'] = 0
                    
                    profile_data['posts'].append(post_data)
                    profile_data['engagement_metrics']['total_posts'] += 1
                    
                except Exception as e:
                    continue
                
                # Modal'ı kapat
                try:
                    close_button = self.driver.find_element(By.CSS_SELECTOR, '._abl-')
                    close_button.click()
                    time.sleep(0.5)
                except:
                    pass
                
        except Exception as e:
            print(f"Instagram scraping error: {str(e)}")
            
        return profile_data

    def _scrape_linkedin(self):
        profile_data = {
            'posts': [],
            'profile_info': {},
            'engagement_metrics': {
                'total_posts': 0,
                'total_reactions': 0,
                'total_comments': 0
            },
            'content_analysis': {
                'hashtags': [],
                'mentions': [],
                'media_count': 0,
                'article_count': 0
            },
            'temporal_patterns': {
                'posting_hours': {},
                'posting_days': {}
            }
        }

        try:
            # Profil bilgilerini topla
            try:
                name = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.text-heading-xlarge'))).text
                profile_data['profile_info']['name'] = name
                
                headline = self.driver.find_element(By.CSS_SELECTOR, '.text-body-medium').text
                profile_data['profile_info']['headline'] = headline
            except:
                pass

            # Gönderileri topla
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            
            for _ in range(5):  # 5 sayfa scroll
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                posts = self.driver.find_elements(By.CSS_SELECTOR, '.feed-shared-update-v2')
                
                for post in posts:
                    try:
                        post_data = {}
                        
                        # Gönderi içeriği
                        try:
                            content = post.find_element(By.CSS_SELECTOR, '.feed-shared-text').text
                            post_data['content'] = content
                            
                            # Hashtag ve mention analizi
                            hashtags = re.findall(r'#\w+', content)
                            mentions = re.findall(r'@\w+', content)
                            
                            post_data['hashtags'] = hashtags
                            post_data['mentions'] = mentions
                            
                            profile_data['content_analysis']['hashtags'].extend(hashtags)
                            profile_data['content_analysis']['mentions'].extend(mentions)
                        except:
                            post_data['content'] = ''
                        
                        # Medya içeriği kontrolü
                        media_elements = post.find_elements(By.CSS_SELECTOR, '.feed-shared-image, .feed-shared-linkedin-video')
                        post_data['has_media'] = len(media_elements) > 0
                        profile_data['content_analysis']['media_count'] += len(media_elements)
                        
                        # Makale kontrolü
                        if post.find_elements(By.CSS_SELECTOR, '.feed-shared-article'):
                            post_data['has_article'] = True
                            profile_data['content_analysis']['article_count'] += 1
                        else:
                            post_data['has_article'] = False
                        
                        # Etkileşim metrikleri
                        try:
                            reactions = post.find_element(By.CSS_SELECTOR, '.social-details-social-counts__reactions-count').text
                            reactions = int(re.sub(r'[^\d]', '', reactions))
                            post_data['reactions'] = reactions
                            profile_data['engagement_metrics']['total_reactions'] += reactions
                        except:
                            post_data['reactions'] = 0
                        
                        profile_data['posts'].append(post_data)
                        profile_data['engagement_metrics']['total_posts'] += 1
                        
                    except Exception as e:
                        continue
                
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
                
        except Exception as e:
            print(f"LinkedIn scraping error: {str(e)}")
            
        return profile_data 