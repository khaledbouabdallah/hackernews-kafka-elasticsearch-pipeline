#!/bin/bash

# Script to apply Elasticsearch index template for Hacker News stories
# This template defines custom analyzers for text search, n-grams, and domain analysis

echo "Applying Elasticsearch index template..."

curl -X PUT "http://localhost:9200/_index_template/hackernews-stories-template" \
  -H 'Content-Type: application/json' \
  -d @./elasticsearch/mappings/hackernews-template.json

echo -e "\n\nTemplate applied successfully!"
echo "Verifying template..."

curl -X GET "http://localhost:9200/_index_template/hackernews-stories-template?pretty"

echo -e "\n\nTo recreate indices with new template, run:"
echo "  docker compose restart logstash"
echo "  curl -X DELETE 'http://localhost:9200/hackernews-stories-*'"
echo "  # Wait for new data to be indexed"
