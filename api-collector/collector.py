import os
import time
import json
import requests
from kafka import KafkaProducer
from datetime import datetime
from urllib.parse import urlparse
from collections import deque
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HackerNewsCollector:
    def __init__(self):
        self.kafka_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
        self.hn_api_base_url = os.getenv('HN_API_BASE_URL', 'https://hacker-news.firebaseio.com/v0')
        self.kafka_topic = os.getenv('KAFKA_TOPIC', 'hackernews-stories')
        self.poll_interval = int(os.getenv('POLL_INTERVAL', 60))
        self.max_stories_per_poll = int(os.getenv('MAX_STORIES_PER_POLL', 30))

        self.seen_story_ids = deque(maxlen=1000)
        self.producer = None
        self.init_kafka_producer()

    def init_kafka_producer(self):
        """Initialize Kafka producer with retry logic"""
        max_retries = 10
        retry_count = 0

        while retry_count < max_retries:
            try:
                self.producer = KafkaProducer(
                    bootstrap_servers=self.kafka_servers,
                    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                    key_serializer=lambda k: k.encode('utf-8') if k else None
                )
                logger.info(f"Connected to Kafka at {self.kafka_servers}")
                return
            except Exception as e:
                retry_count += 1
                logger.warning(f"Failed to connect to Kafka (attempt {retry_count}/{max_retries}): {e}")
                time.sleep(5)

        raise Exception("Failed to connect to Kafka after maximum retries")

    def fetch_new_story_ids(self):
        """Fetch new story IDs from Hacker News API"""
        try:
            url = f"{self.hn_api_base_url}/newstories.json"
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            story_ids = response.json()
            logger.info(f"Fetched {len(story_ids)} story IDs from HN API")
            return story_ids[:self.max_stories_per_poll]

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching story IDs: {e}")
            return []

    def fetch_story_details(self, story_id):
        """Fetch detailed information for a story"""
        try:
            url = f"{self.hn_api_base_url}/item/{story_id}.json"
            response = requests.get(url, timeout=10)

            if response.status_code == 404:
                logger.debug(f"Story {story_id} not found (deleted or invalid)")
                return None

            if response.status_code == 429:
                logger.warning(f"Rate limited on story {story_id}")
                time.sleep(2)
                return None

            response.raise_for_status()
            story = response.json()

            if not story or story.get('dead') or story.get('deleted'):
                return None

            return story

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching story {story_id}: {e}")
            return None

    def extract_domain(self, url):
        """Extract domain from URL"""
        if not url:
            return None
        try:
            parsed = urlparse(url)
            domain = parsed.netloc or parsed.path
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain if domain else None
        except Exception as e:
            logger.debug(f"Error extracting domain from {url}: {e}")
            return None

    def categorize_story(self, story):
        """Categorize story type based on title and type field"""
        title = story.get('title', '').lower()
        story_type = story.get('type', 'story')

        if story_type == 'job':
            return 'job'
        elif title.startswith('ask hn:'):
            return 'ask'
        elif title.startswith('show hn:'):
            return 'show'
        else:
            return 'story'

    def calculate_trending_score(self, score, timestamp):
        """Calculate trending score using HN-like algorithm"""
        try:
            age_hours = (time.time() - timestamp) / 3600
            if age_hours < 1:
                age_hours = 1

            gravity = 1.8
            trending_score = score / pow(age_hours + 2, gravity)
            return round(trending_score, 2)
        except Exception as e:
            logger.debug(f"Error calculating trending score: {e}")
            return 0.0

    def enrich_story(self, story):
        """Enrich story with additional metadata"""
        story_id = story.get('id')
        timestamp = story.get('time', time.time())
        score = story.get('score', 0)
        url = story.get('url')

        enriched_story = {
            'id': str(story_id),
            'type': self.categorize_story(story),
            'author': story.get('by', 'unknown'),
            'title': story.get('title', ''),
            'url': url,
            'domain': self.extract_domain(url),
            'score': score,
            'comments_count': story.get('descendants', 0),
            'trending_score': self.calculate_trending_score(score, timestamp),
            'created_at': datetime.fromtimestamp(timestamp).isoformat(),
            'collected_at': datetime.utcnow().isoformat(),
            'pipeline_version': '2.0'
        }

        return enriched_story

    def send_to_kafka(self, story):
        """Send story to Kafka topic"""
        try:
            story_id = story.get('id')
            story_type = story.get('type', 'unknown')

            self.producer.send(
                self.kafka_topic,
                key=story_id,
                value=story
            )

            logger.debug(f"Sent story {story_id} (type: {story_type}) to Kafka topic {self.kafka_topic}")
            return True

        except Exception as e:
            logger.error(f"Error sending story to Kafka: {e}")
            return False

    def run(self):
        """Main collection loop"""
        logger.info(f"Starting Hacker News Story Collector")
        logger.info(f"Polling interval: {self.poll_interval} seconds")
        logger.info(f"Max stories per poll: {self.max_stories_per_poll}")
        logger.info(f"Kafka topic: {self.kafka_topic}")

        while True:
            try:
                story_ids = self.fetch_new_story_ids()

                new_stories = 0
                for story_id in story_ids:
                    if story_id in self.seen_story_ids:
                        continue

                    story_data = self.fetch_story_details(story_id)
                    if not story_data:
                        continue

                    enriched_story = self.enrich_story(story_data)

                    if self.send_to_kafka(enriched_story):
                        self.seen_story_ids.append(story_id)
                        new_stories += 1

                    time.sleep(0.1)

                if new_stories > 0:
                    self.producer.flush()
                    logger.info(f"Processed {new_stories} new stories")
                else:
                    logger.info("No new stories found")

                time.sleep(self.poll_interval)

            except KeyboardInterrupt:
                logger.info("Shutting down collector...")
                break
            except Exception as e:
                logger.error(f"Unexpected error in collection loop: {e}")
                time.sleep(self.poll_interval)

        if self.producer:
            self.producer.close()


if __name__ == "__main__":
    collector = HackerNewsCollector()
    collector.run()
