# Radio France Real-Time Broadcasting Monitor

A real-time data pipeline that monitors live broadcasts across Radio France's public radio network, streaming data through Kafka, analyzing with Spark, and visualizing with the ELK stack. Track what's playing right now on France Inter, France Culture, FIP, and other stations with live dashboards and geographic visualizations.

## Architecture

```
Radio France GraphQL API → Python Collector (every 5min) → Kafka → Logstash → Elasticsearch → Kibana
                                                               ↓
                                                    Spark (Real-time Metrics)
```

## Components

- **Radio France Collector**: Python service that polls Radio France GraphQL API for live broadcast data
- **Kafka + Zookeeper**: Message broker for streaming broadcast snapshots
- **Logstash**: Data processing pipeline that enriches broadcast data with geo-locations and themes
- **Elasticsearch**: Search and analytics engine for storing live broadcast data (7-day retention)
- **Kibana**: Real-time visualization dashboards with auto-refresh
- **Spark**: Stream processing for real-time metrics (theme distribution, station activity, music vs talk ratios)

## Project Structure

````
pipeline/
├── api-collector/                  # Radio France API collector service
│   ├── radiofrance_realtime_collector.py  # Real-time broadcast collector
│   ├── requirements.txt            # Python dependencies
│   └── Dockerfile                  # Container image
├── kafka/                          # Kafka configurations
├── logstash/                       # Logstash configurations
│   └── pipeline/                   # Pipeline configurations
│       └── radiofrance-live.conf   # Broadcast processing pipeline
├── elasticsearch/                  # Elasticsearch configurations
│   ├── mappings/
│   │   └── radiofrance-mapping.json  # ES mapping with geo support
│   └── queries/                    # Sample queries for dashboards
│       ├── aggs.json
│       ├── fuzzy.json
│       ├── n-gram.json
│       ├── temporal-serie.json
│       └── textual.json
├── spark/                          # Spark jobs
│   └── jobs/                       # Spark job scripts
│  What This Pipeline Does

Monitors **live broadcasts** across Radio France's network every 5 minutes:

- **7 main stations**: France Inter, France Culture, France Info, France Musique, FIP, Mouv, France Bleu
- **10 FIP webradios**: Rock, Jazz, Groove, World, Nouveautés, Reggae, Electro, Metal, Pop, Hip-Hop
- **10 major France Bleu local stations**: Paris, Lyon, Marseille, Toulouse, Bordeaux, Lille, Nantes, Strasbourg, Nice, Rennes


## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- At least 8GB RAM available for Docker
- **Radio France API Key** - Get yours at https://developers.radiofrance.fr

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd pipeline

# Create .env file with your API key
echo "RADIOFRANCE_API_TOKEN=your-api-key-here" > .envisites

- Docker and Docker Compose installed
- At least 8GB RAM available for Docker

### 1. Clone and Setup

```bash
git clone <broadcasts are being collected
docker-compose logs radiofrance-collector | grep "Collected"

# View latest broadcast data
curl -X GET "localhost:9200/radiofrance-live-*/_search?size=5&sort=snapshot_time:desc&pretty
````

### 2. Start the Pipeline

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f api-collector
```

### 3. Verify Services

Wait 1-2 minutes for all services to start, then verify:

```bashradiofrance-live-*` 5. Select `snapshot_time` as time field 6. Click "Create index pattern" 7. Set time filter to "Last 15 minutes" to see live broadcasts 8. Enable auto-refresh (set to 1 minute) for real-time updates

### 6. Build Live Dashboards

Create visualizations in Kibana:

- **Now Playing Table**: Data table showing station_name, current_show.title, themes, grouped by station
- **France Map**: Coordinate map using geo_location field, filtered by is_local_station:true
- \*\*Theme Distriburadiofrance_realtime_metrics.py

```

This job performs real-time analytics including:
- Station activity tracking (broadcasts per 5-min window)
- Live theme distribution across network
- Music vs talk ratio per station
- Theme co-occurrence analysis
- Geographic broadcast patternsr | grep "Processed"
```

### 4. Access Web Interfaces

- **Kibana**: http://localhost:5601
- **Elasticsearch**: http://localhost:9200
- **Spark Master UI**: http://localhost:8081

### 5. Create Kibana Index Pattern

1. Open KBroadcast Flow

```bash
# Radio France Collector logs
docker-compose logs -f radiofrance-collector

# Kafka consumer lag
docker exec -it kafka kafka-consumer-groups --bootstrap-server localhost:9092 \
  --group logstash-radiofrance-consumer-group --describe

# Logstash processing
docker-compose logs -f logstash

# Elasticsearch document count
curl -X GET "localhost:9200/radiofrance-live-*/_count?pretty"

# View live broadcasts from last 5 minutes
curl -X GET "localhost:9200/radiofrance-live-*/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "range": {
      "snapshot_time": {
        "gte": "now-5m"
      }
    }
  },
  "sort": [{"snapshot_time": "desc"}],
  "size": 10
}'
  /opt/spark-jobs/hackernews_stories_analysis.py
```

This job performs real-time analytics including:

- Story metrics (score, comments, trending)
- Domain analysis (popular sources)
- Author activity patterns
- Content categorization (Ask HN, Show HN, Jobs, Stories)
- Trending story identification

### Interactive Analysis with PySpark

```bash
docker exec -it spark-master /opt/spark/bin/pyspark \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1
```

## Monitoring

### View Story Flow

```bash
# HN Collector logs
docker-compose logs -f hn-collector

# Kafka consumer lag
docker exec -it kafka kafka-consumer-groups --bootstrap-server localhost:9092 \
  --group logstash-hn-consumer-group --describe

# Logstash processing
docker-compose logs -f logstash

# Elasticsearch document count
curl -X GET "localhost:9200/hackernews-stories-*/_count?pretty"
```

### Check Service Health

```bash
# All services status
docker-compose ps

# Resource usage
docker stats
```

radiofrance-live --bootstrap-server localhost:9092
docker exec -it kafka kafka-topics --create --topic radiofrance-live --bootstrap-server localhost:9092 --partitions 5

### Stop the Pipeline

````bash
# StRadio France Collector Environment Variables

- `RADIOFRANCE_API_TOKEN`: Your Radio France API key (required, get from https://developers.radiofrance.fr)
- `RADIOFRANCE_API_URL`: API endpoint (default: `https://openapi.radiofrance.fr/v1/graphql`)
- `KAFKA_BOOTSTRAP_SERVERS`: Kafka broker address (default: `kafka:9092`)
- `KAFKA_TOPIC`: Kafka topic name (default: `radiofrance-live`)
- `POLL_INTERVAL`: Polling interval in seconds (default: `300` = 5 minutes)
- `MONITORED_STATIONS`: Comma-separated station IDs to monitor (default: main stations + FIP webradios + top 10 France Bleu
### Restart a Single Service

```bash
docker-compose restart api-collector
````

### Scale Spark Workers

```bash
docker-compose up -d --scale spark-worker=3
```

### Reset Kafka Topic

```bash
# Delete and recreate topic
docker exec -it kafka kafka-topics --delete --topic hackernews-stories --bootstrap-server localhost:9092
docker exec -it kafka kafka-topics --create --topic hackernews-stories --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
```

## Configuration

### HN Collector Environment Variables

- `KAFKA_BOOTSTRAP_SERVERS`: Kafka broker address (default: `kafka:9092`)
- `HN_API_BASE_URL`: Hacker News API endpoint (default: `https://hacker-news.firebaseio.com/v0`)
- `KAFKBroadcasts in Elasticsearch

```bash
# 1. Check Radio France collector is running and has valid API key
docker-compose logs radiofrance-collector

# 2. Check Kafka has messages
docker exec -it kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic radiofrance-live --from-beginning --max-messages 5

# 3. Check Logstash is processing
docker-compose logs logstash

# 4. Verify API key is valid
docker exec -it radiofrance-collector env | grep RADIOFRANCE_API_TOKEN
spark-worker:
  environment:
    - SPARK_WORKER_MEMORY=2G  # Increase worker memory
```

## Troubleshooting

### Services Won't Start

````bash
# Check Docker resources
docker system df
Radio France Collector** queries GraphQL API every 5 minutes for current broadcasts across 27 stations
2. Broadcast data is enriched with content type, timestamps, and station metadata
3. Enriched snapshots are published to **Kafka** topic `radiofrance-live` (keyed by station for partitioning)
4. **Logstash** consumes from Kafka, adds geo-coordinates for local stations, extracts themes, indexes to **Elasticsearch**
5. **Spark** streams from Kafka for real-time metrics (theme distribution, station activity, content ratios)
6. **Kibana** dashboards auto-refresh every minute showing live broadcasts with 7-day data retention

```bash
# 1. Check HN collector is running
do**Additional visualizations**:
  - Animated time-lapse of theme evolution throughout the day
  - Artist/music tracking specifically for FIP stations
  - Cross-station content comparison (when multiple stations cover same themes)
  - Historical trend charts (theme popularity over days/weeks)
- **Extended monitoring**:
  - Monitor all 44 France Bleu local stations (requires request optimization)
  - Add podcast episode tracking (new episodes published)
  - Track personality appearances across shows
- **Advanced analytics**:
  - Predict next likely content based on scheduling patterns
  - Detect special event coverage across network
  - Music diversity metrics (unique artists per hour on FIP)
  - Theme co-occurrence network graphs
- **Technical improvements**:
  - Add alerting for unusual broadcast patterns
  - Implement request caching to reduce API usage
  - Add Prometheus/Grafana for infrastructure monitoring
  - Scale to monitor European public radio network
# Reduce memory in docker-compose.yml
# Stop unnecessary services
docker-compose stop spark-master spark-worker
````

## Data Flow Example

1. **HN Collector** polls Hacker News API every 60 seconds for new stories
2. Stories are enriched with metadata (domain, trending score, categorization)
3. Enriched stories are published to **Kafka** topic `hackernews-stories`
4. **Logstash** consumes from Kafka, adds tags and processing metadata, indexes to **Elasticsearch**
5. **Spark** streams from Kafka for real-time analytics (story metrics, domain analysis, author patterns)
6. **Kibana** provides visualization and search interface for stories

## Next Steps

- Create custom Kibana dashboards for story visualization:
  - Trending stories over time
  - Domain popularity trends
  - Author activity heatmaps
  - Content type distribution
- Extend Spark jobs for advanced analytics:
  - Sentiment analysis of titles
  - Topic modeling and clustering
  - Predictive scoring for trending potential
- Add alerting based on story patterns
- Scale Kafka partitions for higher throughput
- Add data retention policies in Elasticsearch
- Implement monitoring with Prometheus/Grafana
- Extend to collect and analyze comment threads

## License

MIT

## Contributing

Pull requests are welcome! Please ensure all services start correctly and document any new features.
