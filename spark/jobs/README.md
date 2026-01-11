# Spark Jobs

## Running the Hacker News Stories Analysis Job

### Using spark-submit

```bash
docker exec -it spark-master /opt/spark/bin/spark-submit \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1 \
  /opt/spark-jobs/hackernews_stories_analysis.py
```

### Using PySpark Shell

```bash
docker exec -it spark-master /opt/spark/bin/pyspark \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1
```

## Job Description

The `hackernews_stories_analysis.py` job performs comprehensive real-time analytics on Hacker News stories:

### Analytics Functions

1. **Story Metrics Analysis**
   - Analyzes story performance with 5-minute windowed aggregations
   - Metrics: count, avg/max score, avg/max comments, avg trending score
   - Grouped by content type (ask, show, job, story)

2. **Domain Analysis**
   - Tracks popular domains and content sources
   - Metrics: story count, average domain score, unique authors per domain
   - Identifies trending sources and domain diversity

3. **Author Activity Patterns**
   - Monitors author posting behavior
   - Metrics: stories posted, total/avg score, total comments, content variety
   - Filters to show only active authors (>1 story in window)

4. **Content Categorization**
   - Analyzes distribution and performance by content type
   - Types: Ask HN, Show HN, Jobs, Regular Stories
   - Calculates engagement rates (comments/score ratio)

5. **Trending Stories Identification**
   - Identifies high-performing stories (score ≥ 100)
   - Tracks title, author, score, trending score, URL
   - Useful for real-time trending story detection

### Technical Details

- **Windowing**: 5-minute tumbling windows with 10-minute watermark for late data
- **Kafka Topic**: `hackernews-stories`
- **Output Mode**: Console (append for raw stories, complete for aggregations)
- **Streaming Queries**: 6 concurrent streams (raw + 5 analytics)

## Customization

### Writing to Elasticsearch

To persist analytics results to Elasticsearch, implement custom `foreachBatch` sinks:

```python
def write_to_es(batch_df, batch_id):
    batch_df.write \
        .format("org.elasticsearch.spark.sql") \
        .option("es.nodes", "elasticsearch") \
        .option("es.port", "9200") \
        .option("es.resource", "hn-analytics/metrics") \
        .mode("append") \
        .save()

analytics_df.writeStream \
    .foreachBatch(write_to_es) \
    .start()
```

### Extending Analytics

Add custom analytics by creating new aggregation functions following the existing pattern:

```python
def analyze_custom_metric(df):
    return df \
        .withWatermark("processed_at", "10 minutes") \
        .groupBy(window("processed_at", "5 minutes"), "your_field") \
        .agg(your_aggregations)
```
