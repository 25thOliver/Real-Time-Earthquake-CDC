# Real-Time Earthquake CDC Pipeline

Bringing live seismic data to life from API to dashboards, in seconds. This project builds a real-time Change Data Capture(CDC) pipeline that streams live earthquake data from the [USGS FDSN API](https://earthquake.usgs.gov/fdsnws/event/1/) into **MySQL**, mirrors every change through **Kafka + Debezium**, lands it to **PostgreSQL**, and visualizes global seismic trends **Grafana**.

## Project Overview

Earthquakes happen without warning, and understanding their pattern. Traditional earthquake monitoring systems often have delays between when an earthquake occurs and when the data becomes available for analysis. This project eliminates that gap.

**Real-world impact:**
- Emergency responders can see global seismic activity as it happens
- Researchers can analyze earthquake patterns in real-time
- The public can track seismic events in their region instantly

Think of it like the difference between reading yesterday's newspaper vs. watching live news-except for earthquakes happening anywhere on Earth.

Every minute, the U.S. Geological Survey(USGS) publishes new earthquake events around the world.
In this project, we built a pipeline that:

**1. Fetches** new quakes every minute from the USGS API

**2. Upserts** events into MySQL

**3. Capture Changes** in real-time via Debezium & Kafka

**4. Streams** them into PostgreSQL

**5. Visualizes** live quakes and metrics in Grafana dashboards

![System Architecture](images/architecture.png)
*Overall system architecture diagram*

## Architecture
```
USGS API → MySQL → Debezium → Kafka → JDBC Sink → PostgreSQL → Grafana

```
Each component plays a critical role:

**- MySQL** - Primary database storing fresh quake data

**- Adminer UI** - Visualizes our data in primary MySQL database after API ingestion

**- Debezium** - Captures every insert/update via CDC

**- Kafka** - Streams events through topics

**- PostgreSQL** - Sink database for analytics

**- Grafana** - Visualization layer for insights

**- Kafka UI** - Monitors topics and connectors visually

![Kafka Topics](images/kafka_topics.png)
*Kafka UI showing topics*

![Sink and Source Connectors](images/connectors.png)
*Sink and Source Connectors*

## Phases of the Build
### Phase 1: USGS API Integration

**What's happening here:** The United States Geological Survey(USGS) maintains a public API that reports every earthquake detected globally. We poll (ask) this API every 60s: "What earthquake happened in the last minute?"

**Why every minute?** Earthquakes don't wait, and neither should our data. By checking every minute, we ensure our dashboard shows the most current picture of global seismic activity.

A Python script polls the API:
```bash
https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime={NOW-1min}&endtime={NOW}

```
New events are upserted into `earthquake_minute` table in MySQL.

![Sample MySQL table rows after API ingestion](images/mysql_data.png)
*Earthquake MySQL table rows after API ingestion in Adminer UI*

### Phase 2: Change-Data-Capture(CDC)
Imagine MySQL is a busy restaurant kitchen, and the binlog is a camera recording everything the chefs do. Debezium is like a food critic watching that recording in real-time, narrating every dish that gets plated, modified, or sent back.

Without CDC, we'd have to repeatedly ask MySQL "What's new?" every few seconds-inefficient and slow. With CDC, MySQL tells us the moment something changes. It's the difference between spam-refreshing your email vs. getting instant push notifications.

- MySQL binary logging enabled (`binlog_format=ROW`)
    *Understanding the Binlog*
    At the core of this project lies **MySQL's Binary log(binlog), a special journal that records every change made to the database: inserts, updates, and deletes.

    By enabling it in **ROW format**, MySQL doesn't just log that "something changed". It records **exactly what changed** in each row. This is what allows tools like **Debezium** to reconstruct the full story for every database mutation in real-time.
    ![Binlog Settings](images/binlog.png)

    **Why it Matters**
    - `log_bin = ON` - Enables binary logging
    - `binlog_format = ROW` - Captures row-level detail for CDC
    - `server_id` - Provides a unique identifier for the MySQL instance(required by Debezium)

    Once the binlog is active, Debezium can tap into it via Kafka Connect, continuously streaming every change into Kafka topics—turning your database into a real-time data source.

- Debezium MySQL connector listens for changes
- Kafka topics carry those changes
- JDBC Sink connector writes them to PostgrSQL

![Debezium connector configuration (Kafka Connect UI)](images/sink_connector.png)
*Debezium connector configuration (Kafka Connect UI)*

![Kafka UI → Topics → Messages view](images/kafka_messages.png)
*Kafka UI → Topics → Messages view*

### Phase 3: Grafana Visualization
Grafana connects to PostgreSQL and brings seismic data to life through four panels:

**1. Real-Time World Map** — Global quake visualization
   - *Why it's useful:* Instantly see WHERE earthquakes are clustering. Notice the "Ring of Fire" pattern around the Pacific?

**2. Quakes Per Hour** — Time-series trend of activity
   - *Why it's useful:* Spot unusual spikes that might indicate aftershock sequences or increased regional activity

**3. Top 5 Hotspot Regions** — Aggregated regional summary
   - *Why it's useful:* Quantify which areas are most seismically active over time

**4. Quakes in Last Hour (Gauge)** — Real-time activity level
   - *Why it's useful:* A quick "pulse check" showing if Earth is currently rumbling more than usual

![Grafana dashboard](images/grafana_dashboard.png)
*Grafana dashboard (full view)*

![Close-up of world map panel](images/world_map.png)
*Close-up of world map panel*

## Conclusion
This project demonstrates the power of streaming data from a global earthquake API to actionable visualizations in real time.
By Combining open-source tools like **Debezium**, **Kafka**, and **Grafana**, we built a pipeline that's not just functional but alive constantly evolving with Earth's tremors.

**What we proved:**
- Real-time data pipelines can be built with free, open-source tools
- Complex infrastructure can be orchestrated with Docker Compose
- CDC is the key to keeping distributed systems in sync without manual intervention

**Real-world applications of this architecture:**
- IoT sensor networks (replace earthquakes with temperature/pressure readings)
- E-commerce inventory systems (track stock changes across warehouses)
- Financial fraud detection (monitor transactions in real-time)
- Healthcare patient monitoring (stream vital signs to alert systems)

The principles here scale from earthquake monitoring to any domain where **seeing changes as they happen** creates value.

![Grafana + Kafka UI side-by-side for the closing shot](images/final_shot.png)

### Quick Start
```bash
# Start all services
docker compose up -d

# Access components
MySQL        → localhost:3306
Kafka UI     → http://localhost:8082
Grafana      → http://localhost:3000
PostgreSQL   → localhost:5435
Adminer UI   → http://localhost:8080
```