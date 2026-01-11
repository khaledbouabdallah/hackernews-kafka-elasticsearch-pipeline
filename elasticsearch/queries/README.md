# Elasticsearch Queries - School Project

This directory contains the 5 required Elasticsearch queries for the project submission.

## Query Files

### 1. Text Query (Requête textuelle) - `01_text_query.json`

**Purpose**: Search for Hacker News stories containing specific keywords related to technology topics.

**Technique Used**:
- `match` query with boolean logic
- Multiple search terms: "AI", "artificial intelligence", "machine learning", "python", "programming"
- Fuzzy matching enabled (`fuzziness: AUTO`)
- Boosting: "python programming" terms are boosted 2x
- Sorted by relevance score and timestamp

**Example Use Case**: Find all stories discussing AI and machine learning technologies.

**Test Command**:
```bash
curl -X POST "http://localhost:9200/hackernews-stories-*/_search?pretty" \
  -H 'Content-Type: application/json' \
  -d @01_text_query.json
```

---

### 2. Aggregation Query (Requête avec agrégation) - `02_aggregation_query.json`

**Purpose**: Aggregate Hacker News stories by source domain and analyze their statistics.

**Technique Used**:
- `terms` aggregation on domain field (top 20 domains)
- Sub-aggregations:
  - Average score per domain
  - Average comments per domain
  - Maximum score per domain
  - Top 3 stories per domain
- Additional aggregation by content type (ask/show/job/story)
- Time range filter: last 7 days

**Example Use Case**: Identify which domains produce the most popular content and their engagement metrics.

**Key Metrics**:
- Story count by domain
- Average engagement (score, comments)
- Content type distribution

---

### 3. N-gram Query (Requête N-gram) - `03_ngram_query.json`

**Purpose**: Enable partial text matching using n-gram analysis.

**Technique Used**:
- Custom `ngram_analyzer` defined in index template
- Edge n-grams (2-10 characters)
- Searches on `title.ngram` field
- Multiple partial terms: "prog", "java", "data"
- Highlighting enabled to show matched fragments

**Example Matches**:
- "prog" matches: "**prog**ramming", "**prog**ress", "**prog**ram"
- "java" matches: "**java**script", "**Java**", "**java** development"
- "data" matches: "**data** science", "**data**base", "**data** analysis"

**Why N-grams**: Allows searching with incomplete words, useful for autocomplete and partial searches.

---

### 4. Fuzzy Query (Requête floue/fuzzy) - `04_fuzzy_query.json`

**Purpose**: Find stories even with typos or spelling variations.

**Technique Used**:
- `fuzzy` query with edit distance
- Multiple fuzzy terms:
  - "pythn" → matches "python" (distance: 1)
  - "machne" → matches "machine" (distance: 1)
  - "lerning" → matches "learning" (distance: 1)
- Fuzziness modes: AUTO and manual (1-2 edits)
- Prefix length optimization
- Highlighting shows corrected matches

**Example Corrections**:
- User types "pythn" → System finds "python"
- User types "machne lerning" → System finds "machine learning"

**Why Fuzzy**: Improves user experience by tolerating common typos.

---

### 5. Time Series Query (Série temporelle) - `05_time_series_query.json`

**Purpose**: Analyze temporal patterns in Hacker News story submissions.

**Technique Used**:
- `date_histogram` aggregation with two intervals:
  - Hourly buckets (last 24 hours)
  - Daily buckets
- Time zone: Europe/Paris
- Minimum document count: 0 (shows empty buckets)
- Extended bounds to show full 24h range

**Sub-aggregations per time bucket**:
- Story type distribution (ask/show/job/story)
- Average score
- Average trending score
- Total comments
- Cumulative sum (running total)
- Unique domains count
- Unique authors count

**Example Insights**:
- Peak posting hours
- Trending score evolution
- Daily activity patterns
- Content diversity over time

**Visualization**: Perfect for line charts showing story volume over time.

---

## Executing All Queries

### Manual Execution

Run each query individually:

```bash
# Query 1: Text Query
curl -X POST "http://localhost:9200/hackernews-stories-*/_search?pretty" \
  -H 'Content-Type: application/json' \
  -d @01_text_query.json

# Query 2: Aggregation
curl -X POST "http://localhost:9200/hackernews-stories-*/_search?pretty" \
  -H 'Content-Type: application/json' \
  -d @02_aggregation_query.json

# Query 3: N-gram
curl -X POST "http://localhost:9200/hackernews-stories-*/_search?pretty" \
  -H 'Content-Type: application/json' \
  -d @03_ngram_query.json

# Query 4: Fuzzy
curl -X POST "http://localhost:9200/hackernews-stories-*/_search?pretty" \
  -H 'Content-Type: application/json' \
  -d @04_fuzzy_query.json

# Query 5: Time Series
curl -X POST "http://localhost:9200/hackernews-stories-*/_search?pretty" \
  -H 'Content-Type: application/json' \
  -d @05_time_series_query.json
```

### Automated Execution

Use the provided script:

```bash
cd /home/khaledbouabdallah/Projects/pipeline
./elasticsearch/execute_all_queries.sh
```

Results will be saved to `elasticsearch/results/` directory.

## Using in Kibana Dev Tools

You can also run these queries in Kibana Dev Tools (http://localhost:5601/app/dev_tools#/console):

```
POST /hackernews-stories-*/_search
{
  // Paste query JSON here
}
```

## Requirements Met

✅ **1 Requête textuelle**: Query 1 (Text search with match)
✅ **1 Requête avec agrégation**: Query 2 (Terms aggregation with sub-aggs)
✅ **1 Requête N-gram**: Query 3 (Edge n-gram partial matching)
✅ **1 Requête floue (fuzzy)**: Query 4 (Fuzzy query with edit distance)
✅ **1 Série temporelle**: Query 5 (Date histogram time series)

## Technical Justifications

### Why These Query Types?

1. **Text Query**: Essential for full-text search in story titles
2. **Aggregation Query**: Provides business intelligence on content sources
3. **N-gram Query**: Enhances search UX with partial matching
4. **Fuzzy Query**: Improves search tolerance to user errors
5. **Time Series**: Reveals temporal patterns and trends

### Elasticsearch Features Demonstrated

- Custom analyzers (title_analyzer, ngram_analyzer)
- Multi-field mappings (keyword + text)
- Boolean queries (must, should, filter)
- Nested aggregations
- Bucket aggregations (terms, date_histogram)
- Metric aggregations (avg, max, sum, cardinality)
- Query boosting
- Highlighting
- Time zone handling
- Sorting strategies

## For Kibana Visualizations

Each query is designed to support Kibana visualizations:

1. **Query 1** → Data Table or Tag Cloud
2. **Query 2** → Bar Chart or Pie Chart (domains)
3. **Query 3** → Search UI or Data Table
4. **Query 4** → Comparison Table
5. **Query 5** → Line Chart or Area Chart (time series)

See Kibana dashboard at: http://localhost:5601
