from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_spark_session():
    """Create and configure Spark session"""
    return SparkSession.builder \
        .appName("HackerNewsStoriesAnalysis") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1") \
        .config("spark.streaming.stopGracefullyOnShutdown", "true") \
        .getOrCreate()


def read_kafka_stream(spark, kafka_servers, topic):
    """Read streaming data from Kafka"""
    return spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", kafka_servers) \
        .option("subscribe", topic) \
        .option("startingOffsets", "latest") \
        .load()


def get_hn_story_schema():
    """Define schema for Hacker News stories"""
    return StructType([
        StructField("id", StringType()),
        StructField("type", StringType()),
        StructField("author", StringType()),
        StructField("title", StringType()),
        StructField("url", StringType()),
        StructField("domain", StringType()),
        StructField("score", IntegerType()),
        StructField("comments_count", IntegerType()),
        StructField("trending_score", DoubleType()),
        StructField("created_at", StringType()),
        StructField("collected_at", StringType()),
        StructField("pipeline_version", StringType())
    ])


def analyze_story_metrics(df):
    """Analyze story performance metrics"""
    return df \
        .withWatermark("processed_at", "10 minutes") \
        .groupBy(
            window("processed_at", "5 minutes"),
            "type"
        ) \
        .agg(
            count("*").alias("story_count"),
            avg("score").alias("avg_score"),
            max("score").alias("max_score"),
            avg("comments_count").alias("avg_comments"),
            max("comments_count").alias("max_comments"),
            avg("trending_score").alias("avg_trending_score")
        )


def analyze_domains(df):
    """Analyze source domains and distribution"""
    return df \
        .filter(col("domain").isNotNull()) \
        .withWatermark("processed_at", "10 minutes") \
        .groupBy(
            window("processed_at", "5 minutes"),
            "domain"
        ) \
        .agg(
            count("*").alias("story_count"),
            avg("score").alias("avg_domain_score"),
            countDistinct("author").alias("unique_authors")
        ) \
        .orderBy(desc("story_count"))


def analyze_author_activity(df):
    """Analyze author posting patterns"""
    return df \
        .withWatermark("processed_at", "10 minutes") \
        .groupBy(
            window("processed_at", "5 minutes"),
            "author"
        ) \
        .agg(
            count("*").alias("stories_posted"),
            sum("score").alias("total_score"),
            avg("score").alias("avg_score"),
            sum("comments_count").alias("total_comments"),
            countDistinct("type").alias("content_variety")
        ) \
        .filter(col("stories_posted") > 1)


def analyze_content_categories(df):
    """Analyze content type distribution and performance"""
    return df \
        .withWatermark("processed_at", "10 minutes") \
        .groupBy(
            window("processed_at", "5 minutes"),
            "type"
        ) \
        .agg(
            count("*").alias("count"),
            avg("score").alias("avg_score"),
            avg("comments_count").alias("avg_engagement"),
            expr("avg(comments_count / nullif(score, 0))").alias("engagement_rate")
        )


def identify_trending_stories(df):
    """Identify and track trending stories"""
    return df \
        .filter(col("score") >= 100) \
        .withWatermark("processed_at", "10 minutes") \
        .groupBy(
            window("processed_at", "5 minutes")
        ) \
        .agg(
            collect_list(
                struct(
                    col("title"),
                    col("author"),
                    col("score"),
                    col("trending_score"),
                    col("url"),
                    col("type")
                )
            ).alias("trending_stories"),
            count("*").alias("trending_count")
        )


def process_hackernews_stories(df):
    """Process and analyze Hacker News stories"""

    # Define schema for HN stories
    story_schema = get_hn_story_schema()

    # Parse JSON from Kafka value
    stories_df = df.select(
        from_json(col("value").cast("string"), story_schema).alias("story"),
        col("timestamp").alias("kafka_timestamp")
    ).select("story.*", "kafka_timestamp")

    # Add processing timestamp
    stories_df = stories_df.withColumn("processed_at", current_timestamp())

    # Run all analytics
    metrics = analyze_story_metrics(stories_df)
    domains = analyze_domains(stories_df)
    authors = analyze_author_activity(stories_df)
    categories = analyze_content_categories(stories_df)
    trending = identify_trending_stories(stories_df)

    return stories_df, metrics, domains, authors, categories, trending


def write_to_console(df, query_name, output_mode="append"):
    """Write streaming DataFrame to console for debugging"""
    return df.writeStream \
        .outputMode(output_mode) \
        .format("console") \
        .option("truncate", "false") \
        .queryName(query_name) \
        .start()


def main():
    """Main execution function"""
    logger.info("Starting Hacker News Stories Spark Analysis")

    # Configuration
    kafka_servers = "kafka:9092"
    kafka_topic = "hackernews-stories"

    # Create Spark session
    spark = create_spark_session()
    spark.sparkContext.setLogLevel("WARN")

    logger.info(f"Connecting to Kafka at {kafka_servers}, topic: {kafka_topic}")

    # Read from Kafka
    raw_stream = read_kafka_stream(spark, kafka_servers, kafka_topic)

    # Process stories
    stories_df, metrics, domains, authors, categories, trending = \
        process_hackernews_stories(raw_stream)

    # Write streams
    query1 = write_to_console(stories_df, "raw_stories")
    query2 = write_to_console(metrics, "story_metrics", "complete")
    query3 = write_to_console(domains, "domain_analysis", "complete")
    query4 = write_to_console(authors, "author_activity", "complete")
    query5 = write_to_console(categories, "content_categories", "complete")
    query6 = write_to_console(trending, "trending_stories", "complete")

    # Wait for termination
    logger.info("Streaming queries started. Waiting for termination...")
    spark.streams.awaitAnyTermination()


if __name__ == "__main__":
    main()
