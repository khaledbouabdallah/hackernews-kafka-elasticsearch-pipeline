#!/bin/bash

# Script to create submission package for school project
# UE Indexation et visualisation de données massives

SUBMISSION_DIR="submission_package"
PROJECT_ROOT="/home/khaledbouabdallah/Projects/pipeline"

echo "Creating submission package structure..."

# Remove old submission package if it exists
rm -rf "$SUBMISSION_DIR"

# Create main directories
mkdir -p "$SUBMISSION_DIR"/{api-collector,kafka/screenshots,logstash/pipeline,elasticsearch/{mappings,queries,results,screenshots},kibana/{exports,screenshots},spark/{screenshots,results},docker}

echo "Copying configuration files..."

# Copy API Collector files
cp "$PROJECT_ROOT/api-collector/collector.py" "$SUBMISSION_DIR/api-collector/"
cp "$PROJECT_ROOT/api-collector/requirements.txt" "$SUBMISSION_DIR/api-collector/"

# Copy sample data if it exists
if [ -f "$PROJECT_ROOT/export/samples/api_collector_sample.json" ]; then
    cp "$PROJECT_ROOT/export/samples/api_collector_sample.json" "$SUBMISSION_DIR/api-collector/sample_data.json"
fi

# Copy Kafka configuration (from docker-compose)
echo "Extracting Kafka configuration..."
cat > "$SUBMISSION_DIR/kafka/README.md" << 'EOF'
# Kafka Configuration

## Topic Information
- **Topic Name**: hackernews-stories
- **Partitions**: 1
- **Replication Factor**: 1

## Configuration
See docker-compose.yml in the docker/ directory for full Kafka and Zookeeper configuration.

## Producer
The API collector (in api-collector/collector.py) acts as the Kafka producer, sending enriched Hacker News stories to the topic.

## Consumer
Logstash (configured in logstash/pipeline/hackernews-stories.conf) acts as the Kafka consumer.

## Screenshots
Add screenshots showing:
1. Kafka topic description: `docker exec -it kafka kafka-topics --describe --topic hackernews-stories --bootstrap-server localhost:9092`
2. Kafka consumer groups
3. Message flow verification
EOF

# Copy Logstash pipeline
cp "$PROJECT_ROOT/logstash/pipeline/hackernews-stories.conf" "$SUBMISSION_DIR/logstash/pipeline/"

# Copy Elasticsearch files
cp "$PROJECT_ROOT/elasticsearch/mappings/hackernews-template.json" "$SUBMISSION_DIR/elasticsearch/mappings/template.json"
cp "$PROJECT_ROOT/elasticsearch/queries/"*.json "$SUBMISSION_DIR/elasticsearch/queries/"

# Copy query results if they exist
if [ -d "$PROJECT_ROOT/elasticsearch/results" ]; then
    cp "$PROJECT_ROOT/elasticsearch/results/"*.json "$SUBMISSION_DIR/elasticsearch/results/" 2>/dev/null || true
fi

# Create Elasticsearch README
cat > "$SUBMISSION_DIR/elasticsearch/README.md" << 'EOF'
# Elasticsearch Configuration

## Index Template
The file `mappings/template.json` contains the index template with custom analyzers:
- **title_analyzer**: Standard tokenization with stemming and stop words
- **ngram_analyzer**: Edge n-gram tokenization (2-10 characters) for partial matching
- **domain_analyzer**: Keyword analyzer for domain aggregations

## Queries
This directory contains the 5 required Elasticsearch queries:

1. **01_text_query.json**: Full-text search on story titles (AI, ML, programming topics)
2. **02_aggregation_query.json**: Aggregation by domain with statistics
3. **03_ngram_query.json**: N-gram partial matching (e.g., "prog" matches "programming")
4. **04_fuzzy_query.json**: Fuzzy matching with typo tolerance
5. **05_time_series_query.json**: Time series analysis with date histograms

## Executing Queries
Use the provided script:
```bash
curl -X POST "http://localhost:9200/hackernews-stories-*/_search?pretty" \
  -H 'Content-Type: application/json' \
  -d @queries/01_text_query.json
```

## Screenshots
Add screenshots showing:
1. Index mapping verification
2. Results for each of the 5 queries
3. Index statistics and document count
EOF

# Copy Spark files
cp "$PROJECT_ROOT/spark/jobs/hackernews_stories_analysis.py" "$SUBMISSION_DIR/spark/"

# Export Spark results if available
if [ -f "$PROJECT_ROOT/export/samples/spark_results.json" ]; then
    cp "$PROJECT_ROOT/export/samples/spark_results.json" "$SUBMISSION_DIR/spark/results/results.json"
fi

# Create Spark README
cat > "$SUBMISSION_DIR/spark/README.md" << 'EOF'
# Spark Processing

## Analytics Functions
The `hackernews_stories_analysis.py` file implements 5 analytics functions:

1. **calculate_story_metrics()**: Basic statistics (avg score, comments, trending score)
2. **analyze_domains()**: Domain popularity and engagement analysis
3. **analyze_authors()**: Author activity patterns and top contributors
4. **categorize_content()**: Content type distribution and characteristics
5. **identify_trending_stories()**: Real-time trending story identification

## Technology Choice
**Spark vs Hadoop**: We chose Apache Spark for this project because:
- Streaming capabilities with Structured Streaming
- Better performance for iterative analytics
- Simpler API with DataFrames
- Built-in windowing and watermark support
- Better integration with Kafka

## Running the Analytics
```bash
docker exec -it spark-master spark-submit \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1 \
  /app/jobs/hackernews_stories_analysis.py
```

## Screenshots
Add screenshots showing:
1. Spark job running in console
2. Output from each analytics function
3. Spark UI (http://localhost:8081)
EOF

# Create Kibana directory structure
cat > "$SUBMISSION_DIR/kibana/README.md" << 'EOF'
# Kibana Visualizations

## Visualizations Required
Based on the 5 Elasticsearch queries, create these visualizations:

1. **Text Query Visualization**:
   - Type: Data Table or Tag Cloud
   - Shows stories matching keywords (AI, ML, Python)

2. **Aggregation Visualization**:
   - Type: Bar Chart or Pie Chart
   - Top domains by story count and average score

3. **N-gram Query Visualization**:
   - Type: Search Results Table
   - Demonstrates partial matching capability

4. **Fuzzy Query Visualization**:
   - Type: Comparison Table
   - Shows typo tolerance in action

5. **Time Series Visualization**:
   - Type: Line Chart or Area Chart
   - Stories posted over time (hourly buckets)

## Dashboard
Combine all 5 visualizations into a single dashboard.

## Exports
- Save each visualization
- Export dashboard as JSON using Kibana's "Export" feature
- Place the JSON file in `exports/dashboard_export.json`

## Screenshots
Add screenshots of:
1. Each individual visualization
2. The complete dashboard
3. Index pattern configuration

Access Kibana at: http://localhost:5601
EOF

# Copy Docker Compose
cp "$PROJECT_ROOT/docker-compose.yml" "$SUBMISSION_DIR/docker/"

# Copy main documentation
cp "$PROJECT_ROOT/RAPPORT_PROJET.md" "$SUBMISSION_DIR/"

# Create main README
cat > "$SUBMISSION_DIR/README.md" << 'EOF'
# Projet Pipeline - Hacker News Data Pipeline
## UE Indexation et visualisation de données massives

This package contains all files required for the school project submission.

## Project Structure

```
submission_package/
├── README.md                          # This file
├── RAPPORT_PROJET.md                  # Main project report (French)
├── api-collector/                     # Part 1: Data Collection (10 points)
│   ├── collector.py                   # Hacker News API collector
│   ├── requirements.txt               # Python dependencies
│   └── sample_data.json              # Sample extracted data
├── kafka/                             # Part 2: Kafka (15 points)
│   ├── README.md                      # Kafka configuration details
│   └── screenshots/                   # Add Kafka screenshots here
├── logstash/                          # Part 3a: Logstash
│   └── pipeline/
│       └── hackernews-stories.conf   # Logstash pipeline configuration
├── elasticsearch/                     # Part 3b: Elasticsearch (25 points)
│   ├── README.md                      # Elasticsearch details
│   ├── mappings/
│   │   └── template.json             # Index template with custom analyzers
│   ├── queries/                       # 5 required queries
│   │   ├── 01_text_query.json
│   │   ├── 02_aggregation_query.json
│   │   ├── 03_ngram_query.json
│   │   ├── 04_fuzzy_query.json
│   │   └── 05_time_series_query.json
│   ├── results/                       # Query execution results
│   └── screenshots/                   # Add Elasticsearch screenshots here
├── kibana/                            # Part 4: Kibana (20 points)
│   ├── README.md                      # Visualization details
│   ├── exports/                       # Dashboard export JSON
│   └── screenshots/                   # Add Kibana screenshots here
├── spark/                             # Part 5: Spark (20 points)
│   ├── README.md                      # Spark details
│   ├── hackernews_stories_analysis.py # 5 analytics functions
│   ├── results/                       # Spark output results
│   └── screenshots/                   # Add Spark screenshots here
└── docker/
    └── docker-compose.yml             # Complete infrastructure setup

```

## How to Run the Project

### Prerequisites
- Docker and Docker Compose installed
- At least 8GB RAM available
- Ports available: 2181, 9092, 9200, 5601, 5000, 8081

### Starting the Pipeline

1. **Start all services**:
   ```bash
   cd docker/
   docker compose up -d
   ```

2. **Wait for services to be ready** (2-3 minutes):
   ```bash
   # Check Elasticsearch
   curl http://localhost:9200/_cluster/health

   # Check Kibana
   curl http://localhost:5601/api/status
   ```

3. **Apply Elasticsearch template**:
   ```bash
   curl -X PUT "http://localhost:9200/_index_template/hackernews-template" \
     -H 'Content-Type: application/json' \
     -d @elasticsearch/mappings/template.json
   ```

4. **Start data collection**:
   The API collector will automatically start collecting Hacker News stories and sending them to Kafka.

5. **Verify data flow**:
   ```bash
   # Check Kafka topic
   docker exec -it kafka kafka-topics --describe --topic hackernews-stories --bootstrap-server localhost:9092

   # Check Elasticsearch indices
   curl http://localhost:9200/_cat/indices/hackernews-*

   # Check document count
   curl http://localhost:9200/hackernews-*/_count
   ```

6. **Execute Elasticsearch queries**:
   ```bash
   # Example: Text query
   curl -X POST "http://localhost:9200/hackernews-stories-*/_search?pretty" \
     -H 'Content-Type: application/json' \
     -d @elasticsearch/queries/01_text_query.json
   ```

7. **Run Spark analytics**:
   ```bash
   docker exec -it spark-master spark-submit \
     --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1 \
     /app/jobs/hackernews_stories_analysis.py
   ```

8. **Access Kibana**:
   - URL: http://localhost:5601
   - Create index pattern: `hackernews-stories-*`
   - Create visualizations based on the 5 queries
   - Build dashboard

## Project Components

### API Collector (Python)
- Fetches new stories from Hacker News API
- Enriches data with domain extraction, content categorization
- Calculates trending scores
- Sends to Kafka topic

### Kafka
- Topic: `hackernews-stories`
- Acts as message broker between collector and Logstash
- Ensures data reliability and scalability

### Logstash
- Consumes from Kafka topic
- Transforms and enriches data
- Tags high-quality content
- Indexes to Elasticsearch

### Elasticsearch
- Stores stories with custom analyzers
- 3 custom analyzers for different query types
- Daily rotating indices pattern
- Full-text search and aggregations

### Kibana
- Visualizes data from Elasticsearch
- 5 visualizations based on required queries
- Interactive dashboard

### Spark
- Stream processing from Kafka
- 5 analytics functions
- Real-time trending detection
- Windowed aggregations

## Technologies

- **Python 3.11**: API collector
- **Apache Kafka 7.6.0**: Message streaming
- **Logstash 8.12.2**: Data transformation
- **Elasticsearch 8.12.2**: Search and analytics
- **Kibana 8.12.2**: Visualization
- **Apache Spark 3.5.1**: Stream processing
- **Docker Compose**: Orchestration

## Grading Breakdown (100 points)

- ✅ Part 1 - Data Collection (10 points)
- ✅ Part 2 - Kafka (15 points)
- ✅ Part 3 - Logstash & Elasticsearch (25 points)
- 🔄 Part 4 - Kibana (20 points) - Visualizations to be created
- ✅ Part 5 - Spark (20 points)
- ✅ Documentation (10 points)

## Next Steps for Completion

1. **Create Kibana Visualizations**:
   - Access Kibana at http://localhost:5601
   - Create 5 visualizations based on queries
   - Build dashboard
   - Export dashboard JSON
   - Take screenshots

2. **Capture Screenshots**:
   - Kafka topic details
   - Logstash processing logs
   - All Elasticsearch query results
   - All 5 Kibana visualizations
   - Kibana dashboard
   - Spark job execution
   - Spark analytics output

3. **Generate PDF Report**:
   - Convert RAPPORT_PROJET.md to PDF
   - Add all screenshots
   - Fill in student name and date

4. **Package for Submission**:
   ```bash
   zip -r projet_pipeline_submission.zip submission_package/
   ```

## Contact & Questions

For questions about this project, refer to the complete report in `RAPPORT_PROJET.md`.

## GitHub Repository

[Add GitHub repository URL here if available]

---

**Course**: UE Indexation et visualisation de données massives
**Due Date**: February 27, 2024
**Technologies**: Kafka, Logstash, Elasticsearch, Kibana, Spark
EOF

# Create a script to collect sample data
cat > "$SUBMISSION_DIR/collect_samples.sh" << 'EOF'
#!/bin/bash

# Script to collect sample data and screenshots information

echo "Sample Data Collection Script"
echo "=============================="
echo ""
echo "This script helps you collect the necessary sample data for submission."
echo ""

# 1. API Collector Sample
echo "1. Collecting API Collector sample data..."
if command -v docker &> /dev/null; then
    docker logs api-collector --tail 100 > api-collector/collector_logs.txt 2>&1
    echo "   ✓ API collector logs saved to api-collector/collector_logs.txt"
else
    echo "   ⚠ Docker not found. Skipping collector logs."
fi

# 2. Kafka Topic Description
echo ""
echo "2. To get Kafka topic description, run:"
echo "   docker exec -it kafka kafka-topics --describe --topic hackernews-stories --bootstrap-server localhost:9092 > kafka/topic_description.txt"

# 3. Elasticsearch Index Info
echo ""
echo "3. To get Elasticsearch index info, run:"
echo "   curl http://localhost:9200/_cat/indices/hackernews-* > elasticsearch/indices_info.txt"
echo "   curl http://localhost:9200/hackernews-*/_count?pretty > elasticsearch/document_count.json"

# 4. Execute all queries
echo ""
echo "4. To execute all Elasticsearch queries, run:"
echo "   cd elasticsearch/queries/"
echo "   for query in *.json; do"
echo "     echo \"Executing \$query...\""
echo "     curl -X POST \"http://localhost:9200/hackernews-stories-*/_search?pretty\" \\"
echo "       -H 'Content-Type: application/json' \\"
echo "       -d @\$query > ../results/\$(basename \$query .json)_results.json"
echo "   done"

# 5. Spark Results
echo ""
echo "5. To capture Spark results, run the job and save output:"
echo "   docker exec -it spark-master spark-submit \\"
echo "     --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1 \\"
echo "     /app/jobs/hackernews_stories_analysis.py > spark/results/analytics_output.txt 2>&1"

echo ""
echo "6. Screenshots to capture:"
echo "   - Kafka topic description (terminal output)"
echo "   - Logstash processing logs (docker logs logstash)"
echo "   - Elasticsearch indices in Kibana Management"
echo "   - Each of the 5 Elasticsearch query results in Kibana Dev Tools"
echo "   - Each of the 5 Kibana visualizations"
echo "   - Complete Kibana dashboard"
echo "   - Spark job execution in terminal"
echo "   - Spark UI at http://localhost:8081"
echo ""
echo "Done! Review the README.md for complete submission instructions."
EOF

chmod +x "$SUBMISSION_DIR/collect_samples.sh"

# Create instructions for screenshot capture
cat > "$SUBMISSION_DIR/SCREENSHOTS_CHECKLIST.md" << 'EOF'
# Screenshots Checklist for Submission

This checklist ensures you capture all required screenshots for the project report.

## Part 1: API Collector (2-3 screenshots)

- [ ] API collector running (docker logs api-collector)
- [ ] Sample API response from Hacker News
- [ ] Enriched data structure (before sending to Kafka)

**Location**: `api-collector/screenshots/`

---

## Part 2: Kafka (3-4 screenshots)

- [ ] Kafka topic description
  ```bash
  docker exec -it kafka kafka-topics --describe --topic hackernews-stories --bootstrap-server localhost:9092
  ```

- [ ] Kafka topic message count
  ```bash
  docker exec -it kafka kafka-run-class kafka.tools.GetOffsetShell \
    --broker-list localhost:9092 --topic hackernews-stories
  ```

- [ ] Sample message from topic (if possible)

- [ ] Kafka in docker-compose services list

**Location**: `kafka/screenshots/`

---

## Part 3: Logstash & Elasticsearch (8-10 screenshots)

### Logstash
- [ ] Logstash configuration file (logstash/pipeline/hackernews-stories.conf)
- [ ] Logstash processing logs showing successful consumption

### Elasticsearch
- [ ] Index template applied successfully
  ```bash
  curl http://localhost:9200/_index_template/hackernews-template?pretty
  ```

- [ ] List of indices
  ```bash
  curl http://localhost:9200/_cat/indices/hackernews-*
  ```

- [ ] Index mapping showing custom analyzers
  ```bash
  curl http://localhost:9200/hackernews-stories-*/_mapping?pretty
  ```

- [ ] Document count
  ```bash
  curl http://localhost:9200/hackernews-*/_count?pretty
  ```

- [ ] Sample indexed document
  ```bash
  curl http://localhost:9200/hackernews-stories-*/_search?size=1&pretty
  ```

- [ ] **Query 1 Result**: Text query (01_text_query.json)
- [ ] **Query 2 Result**: Aggregation query (02_aggregation_query.json)
- [ ] **Query 3 Result**: N-gram query (03_ngram_query.json)
- [ ] **Query 4 Result**: Fuzzy query (04_fuzzy_query.json)
- [ ] **Query 5 Result**: Time series query (05_time_series_query.json)

**Location**: `elasticsearch/screenshots/`

---

## Part 4: Kibana (6-8 screenshots)

### Setup
- [ ] Kibana home page at http://localhost:5601
- [ ] Index pattern creation (hackernews-stories-*)
- [ ] Discover view showing documents

### Visualizations (one screenshot per visualization)
- [ ] **Visualization 1**: Text query results (table or tag cloud)
- [ ] **Visualization 2**: Domain aggregation (bar/pie chart)
- [ ] **Visualization 3**: N-gram search results (table)
- [ ] **Visualization 4**: Fuzzy query results (comparison table)
- [ ] **Visualization 5**: Time series (line/area chart)

### Dashboard
- [ ] Complete dashboard with all 5 visualizations
- [ ] Dashboard in full screen mode (optional)

**Location**: `kibana/screenshots/`

---

## Part 5: Spark (4-5 screenshots)

- [ ] Spark job submission command in terminal
- [ ] Spark job execution output showing all 5 analytics functions
- [ ] Spark UI at http://localhost:8081 (Jobs tab)
- [ ] Spark UI showing completed job details
- [ ] Sample analytics results (e.g., top domains, trending stories)

**Location**: `spark/screenshots/`

---

## Docker Infrastructure (2-3 screenshots)

- [ ] All services running
  ```bash
  docker compose ps
  ```

- [ ] Docker services logs overview
  ```bash
  docker compose logs --tail=50
  ```

- [ ] Resource usage (optional)
  ```bash
  docker stats --no-stream
  ```

**Location**: `docker/screenshots/` (optional)

---

## Summary

**Total Screenshots Needed**: ~25-35 screenshots

### Priority Levels:
- **Critical** (must have):
  - All 5 Elasticsearch query results
  - All 5 Kibana visualizations
  - Kibana dashboard
  - Spark analytics output
  - Kafka topic description

- **Important** (should have):
  - Index mapping with analyzers
  - API collector logs
  - Logstash processing
  - Spark UI

- **Nice to have**:
  - Docker infrastructure
  - Additional technical details

---

## Tips for Taking Screenshots

1. **Use high resolution**: Ensure text is readable
2. **Show context**: Include browser URL bar, terminal prompts
3. **Highlight important parts**: Use arrows or highlights if needed
4. **Name files clearly**:
   - `elasticsearch_query1_text_results.png`
   - `kibana_visualization2_domains.png`
   - `spark_analytics_output.png`
5. **Include timestamps**: Shows when the system was running
6. **Capture errors too**: If you encountered and fixed issues, show them

---

## After Capturing Screenshots

1. Place screenshots in their respective directories
2. Reference them in RAPPORT_PROJET.md
3. Check that each screenshot is clear and relevant
4. Ensure all critical screenshots are captured
5. Review the complete package before submission

EOF

echo ""
echo "✅ Submission package created successfully!"
echo ""
echo "Location: $SUBMISSION_DIR/"
echo ""
echo "Next steps:"
echo "1. Review the structure: ls -R $SUBMISSION_DIR/"
echo "2. Read the main README: cat $SUBMISSION_DIR/README.md"
echo "3. Follow the screenshots checklist: cat $SUBMISSION_DIR/SCREENSHOTS_CHECKLIST.md"
echo "4. Run the sample collection script: cd $SUBMISSION_DIR && ./collect_samples.sh"
echo "5. Create Kibana visualizations (see kibana/README.md)"
echo "6. Capture all required screenshots"
echo "7. Convert RAPPORT_PROJET.md to PDF"
echo "8. Create final zip: zip -r projet_pipeline_submission.zip $SUBMISSION_DIR/"
echo ""
echo "For detailed instructions, see: $SUBMISSION_DIR/README.md"
