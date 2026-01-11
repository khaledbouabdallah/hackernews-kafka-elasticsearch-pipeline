#!/bin/bash

# Script to export sample data from all pipeline components
# For school project submission

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}Exporting Sample Data for Submission${NC}"
echo -e "${BLUE}============================================${NC}\n"

# Create export directory
mkdir -p ./export/samples

# 1. Export sample data from API collector (from Kafka)
echo -e "${GREEN}[1/5] Exporting sample Hacker News stories from Kafka...${NC}"
docker exec kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic hackernews-stories \
  --from-beginning \
  --max-messages 10 \
  --timeout-ms 5000 > ./export/samples/api_collector_sample_data.json 2>/dev/null

echo -e "  ✓ Saved to: export/samples/api_collector_sample_data.json\n"

# 2. Export sample indexed data from Elasticsearch
echo -e "${GREEN}[2/5] Exporting sample stories from Elasticsearch...${NC}"
curl -s -X GET "http://localhost:9200/hackernews-stories-*/_search?pretty&size=20&sort=collected_at:desc" \
  > ./export/samples/elasticsearch_indexed_data.json

echo -e "  ✓ Saved to: export/samples/elasticsearch_indexed_data.json\n"

# 3. Export index mapping
echo -e "${GREEN}[3/5] Exporting Elasticsearch mapping...${NC}"
curl -s -X GET "http://localhost:9200/hackernews-stories-*/_mapping?pretty" \
  > ./export/samples/elasticsearch_mapping.json

echo -e "  ✓ Saved to: export/samples/elasticsearch_mapping.json\n"

# 4. Export index statistics
echo -e "${GREEN}[4/5] Exporting Elasticsearch statistics...${NC}"
curl -s -X GET "http://localhost:9200/hackernews-stories-*/_stats?pretty" \
  > ./export/samples/elasticsearch_stats.json

echo -e "  ✓ Saved to: export/samples/elasticsearch_stats.json\n"

# 5. Export Kafka topic description
echo -e "${GREEN}[5/5] Exporting Kafka topic information...${NC}"
docker exec kafka kafka-topics \
  --describe \
  --topic hackernews-stories \
  --bootstrap-server localhost:9092 \
  > ./export/samples/kafka_topic_description.txt 2>/dev/null

echo -e "  ✓ Saved to: export/samples/kafka_topic_description.txt\n"

# Summary
echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}Export Summary${NC}"
echo -e "${BLUE}============================================${NC}"
echo -e "${GREEN}✓${NC} API Collector sample (10 stories)"
echo -e "${GREEN}✓${NC} Elasticsearch indexed data (20 stories)"
echo -e "${GREEN}✓${NC} Elasticsearch mapping"
echo -e "${GREEN}✓${NC} Elasticsearch statistics"
echo -e "${GREEN}✓${NC} Kafka topic information"
echo -e "\nAll samples saved to: ${YELLOW}export/samples/${NC}\n"

echo -e "${YELLOW}Note:${NC} For Spark results, run:"
echo -e "  ./export_spark_results.sh\n"
