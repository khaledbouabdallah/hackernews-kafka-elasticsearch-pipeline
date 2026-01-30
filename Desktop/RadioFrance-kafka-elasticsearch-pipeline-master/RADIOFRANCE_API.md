# Radio France Open API Documentation

This document explains how to use the Radio France Open API for collecting live broadcast data.

## API Overview

- **Type**: GraphQL API
- **Base URL**: `https://openapi.radiofrance.fr/v1/graphql`
- **Authentication**: API token (x-token)
- **Rate Limit**: 1000 requests per day
- **Documentation**: https://developers.radiofrance.fr

## Getting an API Key

1. Visit https://developers.radiofrance.fr
2. Create an account
3. Go to "Mon compte" → "Demander une clé d'API"
4. Describe your project name and purpose
5. Wait for approval (usually same day)
6. Receive API key via email

## Authentication

Pass your API token in one of two ways:

### Option 1: HTTP Header (Recommended)
```bash
curl -X POST https://openapi.radiofrance.fr/v1/graphql \
  -H "x-token: your-api-token-here" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ brands { id title } }"}'
```

### Option 2: URL Parameter
```bash
curl -X POST "https://openapi.radiofrance.fr/v1/graphql?x-token=your-api-token-here" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ brands { id title } }"}'
```

## Available Stations

Radio France operates 7 main brands:

| Station ID | Name | Description |
|------------|------|-------------|
| `FRANCEINTER` | France Inter | Generalist talk radio, biggest audience |
| `FRANCECULTURE` | France Culture | Cultural programming, philosophy, history |
| `FRANCEINFO` | France Info | 24/7 news and information |
| `FRANCEMUSIQUE` | France Musique | Classical music and jazz |
| `FIP` | FIP | Eclectic music (no ads, minimal talking) |
| `MOUV` | Mouv' | Youth-oriented hip-hop and urban music |
| `FRANCEBLEU` | France Bleu | Network of 44 local/regional stations |

### FIP Webradios (10 genre-specific streams)

| Station ID | Genre |
|------------|-------|
| `FIP_ROCK` | Rock music |
| `FIP_JAZZ` | Jazz |
| `FIP_GROOVE` | Funk, soul, R&B |
| `FIP_WORLD` | World music |
| `FIP_NOUVEAUTES` | New releases |
| `FIP_REGGAE` | Reggae |
| `FIP_ELECTRO` | Electronic music |
| `FIP_METAL` | Metal |
| `FIP_POP` | Indie/pop |
| `FIP_HIP_HOP` | Hip-hop |

### Major France Bleu Local Stations

| Station ID | City/Region |
|------------|-------------|
| `FRANCEBLEU_PARIS` | Paris |
| `FRANCEBLEU_RHONE` | Lyon |
| `FRANCEBLEU_PROVENCE` | Marseille |
| `FRANCEBLEU_OCCITANIE` | Toulouse |
| `FRANCEBLEU_GIRONDE` | Bordeaux |
| `FRANCEBLEU_NORD` | Lille |
| `FRANCEBLEU_LOIREOCEAN` | Nantes |
| `FRANCEBLEU_ALSACE` | Strasbourg |
| `FRANCEBLEU_AZUR` | Nice |
| `FRANCEBLEU_ARMORIQUE` | Rennes |

## Key GraphQL Queries

### 1. List All Brands

Get information about all Radio France brands:

```graphql
{
  brands {
    id
    title
    baseline
    description
    websiteUrl
    playerUrl
    liveStream
  }
}
```

**Response includes**: Brand metadata, streaming URLs, website links.

### 2. Get Station Details (with local radios and webradios)

```graphql
{
  brand(id: FIP) {
    id
    title
    baseline
    description
    liveStream
    localRadios {
      id
      title
      liveStream
    }
    webRadios {
      id
      title
      description
      liveStream
    }
  }
}
```

### 3. Get Current Broadcast Grid (Last Hour)

**IMPORTANT**: Grid queries are limited to **less than 24 hours** between start and end timestamps.

```graphql
{
  grid(
    start: 1737284400
    end: 1737288000
    station: FRANCEINTER
  ) {
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
```

**Timestamp format**: POSIX timestamp (seconds since 1970-01-01 00:00:00 UTC)
- Use https://www.epochconverter.com/ to convert dates
- Example: `1737284400` = 2026-01-19 09:00:00 UTC

### 4. Get Paginated Grid (for full 24h period)

For time ranges that return more than 100 results, use `paginatedGrid`:

```graphql
{
  paginatedGrid(
    start: 1737244800
    end: 1737331200
    station: FRANCECULTURE
    after: null
  ) {
    cursor
    node {
      steps {
        ... on DiffusionStep {
          id
          start
          end
          diffusion {
            title
            taxonomiesConnection {
              edges {
                node {
                  path
                  title
                }
              }
            }
          }
        }
        ... on TrackStep {
          id
          track {
            title
            mainArtists
          }
        }
      }
    }
  }
}
```

Use the returned `cursor` value in the `after` parameter to get the next page.

### 5. Get Show Information

Retrieve show details by URL:

```graphql
{
  showByUrl(
    url: "https://www.radiofrance.fr/franceculture/podcasts/fictions-theatre-et-cie"
  ) {
    id
    title
    url
    standFirst
    podcast {
      rss
      itunes
    }
    taxonomiesConnection {
      edges {
        node {
          path
          type
          title
        }
      }
    }
  }
}
```

### 6. Get Recent Diffusions of a Show

```graphql
{
  diffusionsOfShowByUrl(
    url: "https://www.radiofrance.fr/franceculture/podcasts/fictions-theatre-et-cie"
    first: 10
  ) {
    edges {
      node {
        id
        title
        url
        published_date
        podcastEpisode {
          url
          playerUrl
          duration
          created
        }
      }
    }
  }
}
```

### 7. Get Taxonomies (Themes and Tags)

```graphql
{
  taxonomies(source: UNIFIED, first: 20) {
    edges {
      node {
        id
        path
        type
        title
        standFirst
      }
    }
  }
}
```

**Taxonomy types**:
- `theme`: Hierarchical themes (can have 3 levels: theme/subtheme/subsubtheme)
- `tag`: Flat keyword tags
- `dossier`: Special content dossiers

**Examples**:
- Theme path: `"sciences-savoirs/sciences/biologie"` (3 levels)
- Tag: `"climat"`, `"elections"`, `"musique"`

## Data Model

### Content Types in Grid

The `grid` query returns different step types:

1. **DiffusionStep**: A show broadcast with full metadata
2. **TrackStep**: A music track (artist, title, album)
3. **BlankStep**: Filler content (jingles, news flashes, ads)

### Important Fields

**Diffusion (Show Broadcast)**:
- `id`: Unique identifier
- `title`: Show episode title
- `standFirst`: Description/summary
- `url`: Web page URL
- `published_date`: POSIX timestamp
- `show`: Parent show information
- `podcastEpisode`: Audio file and metadata (if available)
- `taxonomiesConnection`: Themes and tags

**PodcastEpisode**:
- `url`: Direct MP3 audio file URL
- `playerUrl`: Embeddable player URL
- `duration`: Length in seconds
- `created`: Publication timestamp

**Track (Music)**:
- `title`: Song title
- `albumTitle`: Album name
- `mainArtists`: Artist name(s)

**Taxonomy**:
- `path`: Hierarchical path (e.g., `"culture/cinema"`)
- `type`: `"theme"` or `"tag"`
- `title`: Display name

## Best Practices

### Rate Limit Management

With 1000 requests/day, optimize your collection strategy:

**Good Strategy (5-min polling, 27 stations)**:
- 12 requests/hour × 24 hours = 288 requests/day
- Leaves 712 requests for retries and ad-hoc queries

**Request Budget Examples**:
- Querying 1 station every 5 minutes: ~288 req/day
- Full 24h grid for 3 stations daily: ~30 req/day
- Monitoring 50 shows for new episodes (hourly): ~1200 req/day ⚠️ (too much!)

### Efficient Querying

1. **Query current hour only** (not full day) for live monitoring
2. **Batch multiple fields** in one query (use GraphQL fragments)
3. **Cache station metadata** (brand info rarely changes)
4. **Use pagination cursor** for large result sets

### Time Range Limitations

- Grid queries: **Maximum 24 hours** between start and end
- To get data for longer periods: Make multiple queries for consecutive 24h windows
- You cannot query historical data older than what's currently available (typically last few days)

### Error Handling

Common errors:

- **401 Unauthorized**: Invalid or missing API token
- **429 Too Many Requests**: Rate limit exceeded (1000/day)
- **400 Bad Request**: Invalid GraphQL query syntax
- **Time range error**: Queries exceeding 24h return empty or error

## Example: Real-Time Collection Script

```python
import requests
import time
from datetime import datetime

API_URL = "https://openapi.radiofrance.fr/v1/graphql"
API_TOKEN = "your-token-here"

def get_current_broadcasts(station_id):
    # Query last hour
    now = int(time.time())
    one_hour_ago = now - 3600

    query = """
    {
      grid(start: %d, end: %d, station: %s) {
        ... on DiffusionStep {
          id
          start
          end
          diffusion {
            title
            taxonomiesConnection {
              edges {
                node {
                  path
                  title
                }
              }
            }
          }
        }
        ... on TrackStep {
          id
          track {
            title
            mainArtists
          }
        }
      }
    }
    """ % (one_hour_ago, now, station_id)

    response = requests.post(
        API_URL,
        headers={"x-token": API_TOKEN, "Content-Type": "application/json"},
        json={"query": query}
    )

    return response.json()

# Collect from multiple stations
stations = ["FRANCEINTER", "FRANCECULTURE", "FIP"]

while True:
    for station in stations:
        data = get_current_broadcasts(station)
        print(f"{datetime.now()} - {station}: {len(data['data']['grid'])} broadcasts")

    # Poll every 5 minutes (300 seconds)
    time.sleep(300)
```

## Resources

- **Official Portal**: https://developers.radiofrance.fr
- **GraphQL Playground**: https://openapi.radiofrance.fr/v1/graphql?x-token=YOUR_TOKEN
- **Support Email**: support.openapi@radiofrance.com
- **GraphQL Guide**: https://graphql.org/learn/

## Frequently Asked Questions

**Q: Can I get historical data from 6 months ago?**
A: No, the API only allows querying recent broadcasts (typically last few days, with 24h max range per query).

**Q: How do I know what's playing RIGHT NOW?**
A: Query the grid for the last hour: `start: now-3600, end: now`

**Q: Why are some podcasts missing?**
A: Not all broadcasts have podcast episodes. Check if `podcastEpisode` field is null.

**Q: What's the difference between FIP and FIP_ROCK?**
A: FIP is the main eclectic station. FIP_ROCK is a genre-specific webradio playing only rock music.

**Q: Can I stream the audio directly?**
A: Yes, use the `liveStream` URL for live audio, or `podcastEpisode.url` for on-demand MP3 files.

**Q: How are themes organized?**
A: Hierarchically with up to 3 levels, separated by slashes: `sciences-savoirs/sciences/biologie`

**Q: What timezone are timestamps in?**
A: All timestamps are UTC (Unix epoch seconds). Convert to local time in your application.
