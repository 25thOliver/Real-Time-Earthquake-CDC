# Real-Time Earthquake CDC Pipeline

Bringing live seismic data to life from API to dashboards, in seconds. This project builds a real-time Change Data Capture(CDC) pipeline that streams live earthquake data from the ![USGS FDSN API](https://earthquake.usgs.gov/fdsnws/event/1/) into **MySQL**, mirrors every change through **Kafka + Debezium**, lands it to **PostgreSQL**, and visualizes global seismic trends **Grafana**.

## Project Overview

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
**- Debezium** - Captures every insert/update via CDC
**- Kafka** - Streams events through topics
**- PostgreSQL** - Sink database for analytics
**- Grafana** - Visualization layer for insights
**- Kafka UI** - Monitors topics and connectors visually
