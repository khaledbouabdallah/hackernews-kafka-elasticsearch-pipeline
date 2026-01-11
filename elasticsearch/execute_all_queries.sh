#!/bin/bash

# Script to execute all 5 required Elasticsearch queries
# Results are saved to the results/ directory for school project submission

# Colors for output
GREEN='\033[0.32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Create results directory
mkdir -p ./elasticsearch/results

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Executing Elasticsearch Queries${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Query 1: Text Query
echo -e "${GREEN}[1/5] Executing Text Query (Recherche textuelle)...${NC}"
curl -s -X POST "http://localhost:9200/hackernews-stories-*/_search?pretty" \
  -H 'Content-Type: application/json' \
  -d @./elasticsearch/queries/01_text_query.json \
  > ./elasticsearch/results/01_text_query_results.json

echo -e "  ✓ Results saved to: elasticsearch/results/01_text_query_results.json\n"

# Query 2: Aggregation Query
echo -e "${GREEN}[2/5] Executing Aggregation Query (Agrégation par domaine)...${NC}"
curl -s -X POST "http://localhost:9200/hackernews-stories-*/_search?pretty" \
  -H 'Content-Type: application/json' \
  -d @./elasticsearch/queries/02_aggregation_query.json \
  > ./elasticsearch/results/02_aggregation_query_results.json

echo -e "  ✓ Results saved to: elasticsearch/results/02_aggregation_query_results.json\n"

# Query 3: N-gram Query
echo -e "${GREEN}[3/5] Executing N-gram Query (Recherche partielle)...${NC}"
curl -s -X POST "http://localhost:9200/hackernews-stories-*/_search?pretty" \
  -H 'Content-Type: application/json' \
  -d @./elasticsearch/queries/03_ngram_query.json \
  > ./elasticsearch/results/03_ngram_query_results.json

echo -e "  ✓ Results saved to: elasticsearch/results/03_ngram_query_results.json\n"

# Query 4: Fuzzy Query
echo -e "${GREEN}[4/5] Executing Fuzzy Query (Recherche floue)...${NC}"
curl -s -X POST "http://localhost:9200/hackernews-stories-*/_search?pretty" \
  -H 'Content-Type: application/json' \
  -d @./elasticsearch/queries/04_fuzzy_query.json \
  > ./elasticsearch/results/04_fuzzy_query_results.json

echo -e "  ✓ Results saved to: elasticsearch/results/04_fuzzy_query_results.json\n"

# Query 5: Time Series Query
echo -e "${GREEN}[5/5] Executing Time Series Query (Série temporelle)...${NC}"
curl -s -X POST "http://localhost:9200/hackernews-stories-*/_search?pretty" \
  -H 'Content-Type: application/json' \
  -d @./elasticsearch/queries/05_time_series_query.json \
  > ./elasticsearch/results/05_time_series_query_results.json

echo -e "  ✓ Results saved to: elasticsearch/results/05_time_series_query_results.json\n"

# Summary
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "All 5 queries executed successfully!"
echo -e "\nResults location: ${YELLOW}elasticsearch/results/${NC}"
echo -e "\nQuery descriptions:"
echo -e "  1. ${YELLOW}Text Query${NC}: Searches for AI, ML, Python related stories"
echo -e "  2. ${YELLOW}Aggregation Query${NC}: Aggregates stories by domain with statistics"
echo -e "  3. ${YELLOW}N-gram Query${NC}: Partial matching (e.g., 'prog' matches 'programming')"
echo -e "  4. ${YELLOW}Fuzzy Query${NC}: Tolerant to typos (e.g., 'pythn' matches 'python')"
echo -e "  5. ${YELLOW}Time Series Query${NC}: Analyzes story trends over last 24 hours"
echo -e "\n${GREEN}✓ All queries ready for submission!${NC}\n"
