#!/usr/bin/env python3
"""
Radio France Real-Time Broadcast Collector

Polls Radio France GraphQL API every 5 minutes to collect current broadcasts
across all monitored stations and publishes to Kafka.
"""

import os
import sys
import time
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional
import requests
from kafka import KafkaProducer
from kafka.errors import KafkaError

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Configuration from environment variables
RADIOFRANCE_API_URL = os.getenv(
    "RADIOFRANCE_API_URL", "https://openapi.radiofrance.fr/v1/graphql"
)
RADIOFRANCE_API_TOKEN = os.getenv("RADIOFRANCE_API_TOKEN")
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "radiofrance-live")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "300"))  # 5 minutes default

# Stations to monitor
MAIN_STATIONS = [
    "FRANCEINTER",
    "FRANCECULTURE",
    "FRANCEINFO",
    "FRANCEMUSIQUE",
    "FIP",
    "MOUV",
]

FIP_WEBRADIOS = [
    "FIP_ROCK",
    "FIP_JAZZ",
    "FIP_GROOVE",
    "FIP_WORLD",
    "FIP_NOUVEAUTES",
    "FIP_REGGAE",
    "FIP_ELECTRO",
    "FIP_METAL",
    "FIP_POP",
    "FIP_HIP_HOP",
]

# Top 10 France Bleu local stations (major cities)
FRANCE_BLEU_STATIONS = [
    "FRANCEBLEU_PARIS",
    "FRANCEBLEU_RHONE",  # Lyon
    "FRANCEBLEU_PROVENCE",  # Marseille
    "FRANCEBLEU_OCCITANIE",  # Toulouse
    "FRANCEBLEU_GIRONDE",  # Bordeaux
    "FRANCEBLEU_NORD",  # Lille
    "FRANCEBLEU_LOIREOCEAN",  # Nantes
    "FRANCEBLEU_ALSACE",  # Strasbourg
    "FRANCEBLEU_AZUR",  # Nice
    "FRANCEBLEU_ARMORIQUE",  # Rennes
]

# Geographic coordinates for France Bleu stations (for map visualization)
STATION_COORDINATES = {
    "FRANCEBLEU_PARIS": {"lat": 48.8566, "lon": 2.3522},
    "FRANCEBLEU_RHONE": {"lat": 45.7640, "lon": 4.8357},
    "FRANCEBLEU_PROVENCE": {"lat": 43.2965, "lon": 5.3698},
    "FRANCEBLEU_OCCITANIE": {"lat": 43.6047, "lon": 1.4442},
    "FRANCEBLEU_GIRONDE": {"lat": 44.8378, "lon": -0.5792},
    "FRANCEBLEU_NORD": {"lat": 50.6292, "lon": 3.0573},
    "FRANCEBLEU_LOIREOCEAN": {"lat": 47.2184, "lon": -1.5536},
    "FRANCEBLEU_ALSACE": {"lat": 48.5734, "lon": 7.7521},
    "FRANCEBLEU_AZUR": {"lat": 43.7102, "lon": 7.2620},
    "FRANCEBLEU_ARMORIQUE": {"lat": 48.1173, "lon": -1.6778},
}

ALL_STATIONS = MAIN_STATIONS + FIP_WEBRADIOS + FRANCE_BLEU_STATIONS


class RadioFranceCollector:
    """Collects live broadcast data from Radio France API."""

    def __init__(self):
        if not RADIOFRANCE_API_TOKEN:
            logger.error("RADIOFRANCE_API_TOKEN environment variable not set!")
            sys.exit(1)

        self.api_url = RADIOFRANCE_API_URL
        self.api_token = RADIOFRANCE_API_TOKEN
        self.session = requests.Session()
        self.session.headers.update(
            {"x-token": self.api_token, "Content-Type": "application/json"}
        )

        self.producer = None
        self.request_count = 0

    def init_kafka_producer(self):
        """Initialize Kafka producer with retry logic."""
        max_retries = 10
        retry_count = 0

        while retry_count < max_retries:
            try:
                self.producer = KafkaProducer(
                    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                    key_serializer=lambda k: k.encode("utf-8") if k else None,
                    max_request_size=5242880,  # 5MB
                    acks="all",
                    retries=3,
                )
                logger.info(f"Kafka producer initialized: {KAFKA_BOOTSTRAP_SERVERS}")
                return
            except KafkaError as e:
                retry_count += 1
                wait_time = min(2**retry_count, 60)
                logger.warning(
                    f"Failed to connect to Kafka (attempt {retry_count}/{max_retries}): {e}"
                )
                if retry_count < max_retries:
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error("Max retries reached. Exiting.")
                    sys.exit(1)

    def get_current_broadcast_grid(self, station_id: str) -> Optional[Dict]:
        """
        Query Radio France API for current hour's broadcast grid.

        Args:
            station_id: Station identifier (e.g., 'FRANCEINTER')

        Returns:
            API response data or None if request fails
        """
        # Get timestamps for last hour
        now = int(time.time())
        one_hour_ago = now - 3600

        # GraphQL query for broadcast grid
        query = """
        {
          grid(start: %d, end: %d, station: %s) {
            ... on DiffusionStep {
              id
              start
              end
              diffusion {
                id
                title
                standFirst
                url
                published_date
                show {
                  id
                  title
                }
                taxonomiesConnection {
                  edges {
                    node {
                      id
                      path
                      type
                      title
                    }
                  }
                }
                podcastEpisode {
                  id
                  title
                  url
                  playerUrl
                  duration
                  created
                }
              }
            }
            ... on TrackStep {
              id
              start
              end
              track {
                id
                title
                albumTitle
                mainArtists
              }
            }
            ... on BlankStep {
              id
              title
              start
              end
            }
          }
        }
        """ % (
            one_hour_ago,
            now,
            station_id,
        )

        try:
            response = self.session.post(
                self.api_url, json={"query": query}, timeout=30
            )
            response.raise_for_status()
            self.request_count += 1

            data = response.json()

            if "errors" in data:
                logger.error(f"GraphQL errors for {station_id}: {data['errors']}")
                return None

            return data.get("data", {}).get("grid", [])

        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed for {station_id}: {e}")
            return None

    def extract_content_type(self, step: Dict) -> str:
        """Determine content type from step data."""
        if "diffusion" in step:
            return "show"
        elif "track" in step:
            return "music"
        else:
            return "blank"

    def extract_themes(self, diffusion: Dict) -> List[str]:
        """Extract theme paths from diffusion taxonomies."""
        themes = []
        taxonomies = diffusion.get("taxonomiesConnection", {}).get("edges", [])
        for edge in taxonomies:
            node = edge.get("node", {})
            if node.get("type") == "theme":
                themes.append(node.get("path", ""))
        return [t for t in themes if t]

    def process_broadcast_data(
        self, station_id: str, grid_data: List[Dict]
    ) -> List[Dict]:
        """
        Process raw grid data into structured broadcast snapshots.

        Args:
            station_id: Station identifier
            grid_data: Raw grid data from API

        Returns:
            List of processed broadcast documents
        """
        processed = []
        snapshot_time = datetime.now(timezone.utc)

        # Determine if this is a local station
        is_local = station_id in FRANCE_BLEU_STATIONS

        # Get geographic coordinates if available
        geo_location = None
        if is_local and station_id in STATION_COORDINATES:
            coords = STATION_COORDINATES[station_id]
            geo_location = {"lat": coords["lat"], "lon": coords["lon"]}

        for step in grid_data:
            step_id = step.get("id", "")
            start_ts = step.get("start", 0)
            end_ts = step.get("end", 0)
            content_type = self.extract_content_type(step)

            # Build base document
            doc = {
                "step_id": step_id,
                "station_id": station_id,
                "station_name": station_id.replace("_", " ").title(),
                "snapshot_time": snapshot_time.isoformat(),
                "broadcast_start": (
                    datetime.fromtimestamp(start_ts, timezone.utc).isoformat()
                    if start_ts
                    else None
                ),
                "broadcast_end": (
                    datetime.fromtimestamp(end_ts, timezone.utc).isoformat()
                    if end_ts
                    else None
                ),
                "content_type": content_type,
                "is_local_station": is_local,
                "geo_location": geo_location,
            }

            # Add content-specific fields
            if content_type == "show":
                diffusion = step.get("diffusion")
                if not diffusion:
                    # Skip if diffusion data is missing
                    continue

                doc["current_show"] = {
                    "id": diffusion.get("id"),
                    "title": diffusion.get("title"),
                    "description": diffusion.get("standFirst"),
                    "url": diffusion.get("url"),
                    "published_date": diffusion.get("published_date"),
                }

                # Extract show info
                show = diffusion.get("show", {})
                if show:
                    doc["current_show"]["show_id"] = show.get("id")
                    doc["current_show"]["show_title"] = show.get("title")

                # Extract themes
                doc["themes"] = self.extract_themes(diffusion)

                # Check for podcast
                podcast = diffusion.get("podcastEpisode")
                if podcast:
                    doc["podcast_episode"] = {
                        "id": podcast.get("id"),
                        "title": podcast.get("title"),
                        "audio_url": podcast.get("url"),
                        "player_url": podcast.get("playerUrl"),
                        "duration": podcast.get("duration"),
                        "created": podcast.get("created"),
                    }
                    doc["has_podcast"] = True
                else:
                    doc["has_podcast"] = False

            elif content_type == "music":
                track = step.get("track", {})
                doc["current_track"] = {
                    "id": track.get("id"),
                    "title": track.get("title"),
                    "album": track.get("albumTitle"),
                    "artists": track.get("mainArtists"),
                }
                doc["themes"] = []
                doc["has_podcast"] = False

            else:  # blank
                doc["blank_title"] = step.get("title", "Unknown")
                doc["themes"] = []
                doc["has_podcast"] = False

            # Calculate if currently broadcasting
            now_ts = time.time()
            doc["is_current"] = (
                (start_ts <= now_ts <= end_ts) if (start_ts and end_ts) else False
            )

            processed.append(doc)

        return processed

    def publish_to_kafka(self, documents: List[Dict]):
        """Publish broadcast documents to Kafka topic."""
        for doc in documents:
            try:
                # Use station_id as key for partitioning
                key = doc["station_id"]

                future = self.producer.send(KAFKA_TOPIC, key=key, value=doc)

                # Wait for send to complete (with timeout)
                future.get(timeout=10)

            except KafkaError as e:
                logger.error(f"Failed to publish to Kafka: {e}")
            except Exception as e:
                logger.error(f"Unexpected error publishing to Kafka: {e}")

    def collect_and_publish(self):
        """Main collection cycle: query API and publish to Kafka."""
        logger.info(f"Starting collection cycle for {len(ALL_STATIONS)} stations")

        total_broadcasts = 0
        successful_stations = 0

        for station_id in ALL_STATIONS:
            logger.info(f"Querying {station_id}...")

            grid_data = self.get_current_broadcast_grid(station_id)

            if grid_data is None:
                logger.warning(f"No data returned for {station_id}")
                continue

            if not grid_data:
                logger.info(f"Empty grid for {station_id}")
                continue

            # Process the data
            documents = self.process_broadcast_data(station_id, grid_data)

            if documents:
                # Publish to Kafka
                self.publish_to_kafka(documents)

                total_broadcasts += len(documents)
                successful_stations += 1
                logger.info(f"✓ {station_id}: {len(documents)} broadcasts collected")

            # Small delay between stations to avoid rate limiting
            time.sleep(0.5)

        logger.info(
            f"Collection cycle complete: {successful_stations}/{len(ALL_STATIONS)} stations, "
            f"{total_broadcasts} total broadcasts, {self.request_count} API requests"
        )

    def run(self):
        """Main loop: collect data at regular intervals."""
        logger.info("=== Radio France Real-Time Collector Starting ===")
        logger.info(f"API URL: {self.api_url}")
        logger.info(f"Kafka: {KAFKA_BOOTSTRAP_SERVERS} → {KAFKA_TOPIC}")
        logger.info(
            f"Poll interval: {POLL_INTERVAL} seconds ({POLL_INTERVAL/60:.1f} minutes)"
        )
        logger.info(f"Monitoring {len(ALL_STATIONS)} stations")

        # Initialize Kafka
        self.init_kafka_producer()

        # Main loop
        while True:
            try:
                cycle_start = time.time()

                self.collect_and_publish()

                cycle_duration = time.time() - cycle_start
                logger.info(f"Cycle took {cycle_duration:.1f} seconds")

                # Sleep until next poll interval
                sleep_time = max(0, POLL_INTERVAL - cycle_duration)
                if sleep_time > 0:
                    logger.info(
                        f"Sleeping for {sleep_time:.1f} seconds until next cycle..."
                    )
                    time.sleep(sleep_time)

            except KeyboardInterrupt:
                logger.info("Shutdown requested by user")
                break
            except Exception as e:
                logger.error(f"Unexpected error in main loop: {e}", exc_info=True)
                logger.info("Sleeping 60 seconds before retry...")
                time.sleep(60)

        # Cleanup
        if self.producer:
            self.producer.close()
        logger.info("Collector stopped")


if __name__ == "__main__":
    collector = RadioFranceCollector()
    collector.run()
