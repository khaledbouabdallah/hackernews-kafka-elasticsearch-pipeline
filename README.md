# Hacker News Stories Data Pipeline

A real-time data pipeline that collects Hacker News stories, processes them through Kafka, analyzes them with Spark, and visualizes them using the ELK stack.

## Architecture

```
HN API → HN Collector → Kafka → Logstash → Elasticsearch → Kibana
                            ↓
                         Spark (Stream Processing)
```

## Components

- **HN Collector**: Python service that polls Hacker News API and publishes stories to Kafka
- **Kafka + Zookeeper**: Message broker for story streaming
- **Logstash**: Data processing pipeline that consumes from Kafka and indexes to Elasticsearch
- **Elasticsearch**: Search and analytics engine for storing processed stories
- **Kibana**: Visualization and exploration interface
- **Spark**: Stream processing for real-time analytics (story metrics, domain analysis, author patterns, content categorization)

## Project Structure

```
pipeline/
├── api-collector/          # Hacker News API collector service
│   ├── collector.py        # Main collector script
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile         # Container image
├── kafka/                  # Kafka configurations (optional)
├── logstash/              # Logstash configurations
│   └── pipeline/          # Pipeline configurations
│       └── hackernews-stories.conf
├── elasticsearch/         # Elasticsearch configurations (optional)
├── spark/                 # Spark jobs
│   └── jobs/             # Spark job scripts
│       ├── hackernews_stories_analysis.py
│       └── requirements.txt
├── kibana/               # Kibana configurations (optional)
├── docker-compose.yml    # Docker services definition
├── .gitignore           # Git ignore rules
└── README.md            # This file
```

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- At least 8GB RAM available for Docker

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd pipeline
```

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

```bash
# Check Kafka topics
docker exec -it kafka kafka-topics --list --bootstrap-server localhost:9092

# Check Elasticsearch
curl http://localhost:9200/_cat/indices?v

# Check if stories are being collected
docker-compose logs hn-collector | grep "Processed"
```

### 4. Access Web Interfaces

- **Kibana**: http://localhost:5601
- **Elasticsearch**: http://localhost:9200
- **Spark Master UI**: http://localhost:8081

### 5. Create Kibana Index Pattern

1. Open Kibana at http://localhost:5601
2. Go to Management → Stack Management → Index Patterns
3. Click "Create index pattern"
4. Enter pattern: `hackernews-stories-*`
5. Select `@timestamp` as time field
6. Click "Create index pattern"
7. Go to Discover to view your stories

## Running Spark Jobs

### Start a Spark Streaming Job

```bash
docker exec -it spark-master /opt/spark/bin/spark-submit \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1 \
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

## Common Operations

### Stop the Pipeline

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes all data)
docker-compose down -v
```

### Restart a Single Service

```bash
docker-compose restart api-collector
```

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
- `KAFKA_TOPIC`: Kafka topic name (default: `hackernews-stories`)
- `POLL_INTERVAL`: Polling interval in seconds (default: `60`)
- `MAX_STORIES_PER_POLL`: Maximum stories to fetch per poll (default: `30`)

### Adjust Memory Limits

Edit `docker-compose.yml` to adjust memory for services:

```yaml
elasticsearch:
  environment:
    - "ES_JAVA_OPTS=-Xms1g -Xmx1g"  # Increase heap size

spark-worker:
  environment:
    - SPARK_WORKER_MEMORY=2G  # Increase worker memory
```

## Troubleshooting

### Services Won't Start

```bash
# Check Docker resources
docker system df

# Check logs for errors
docker-compose logs
```

### No Stories in Elasticsearch

```bash
# 1. Check HN collector is running
docker-compose logs hn-collector

# 2. Check Kafka has messages
docker exec -it kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic hackernews-stories --from-beginning --max-messages 10

# 3. Check Logstash is processing
docker-compose logs logstash
```

### High Memory Usage

```bash
# Reduce memory in docker-compose.yml
# Stop unnecessary services
docker-compose stop spark-master spark-worker
```

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
