schemas = {
    "earthquake_minute": """
        CREATE TABLE IF NOT EXISTS earthquake_minute (
            id VARCHAR(64) PRIMARY KEY,
            time_ms BIGINT NOT NULL,
            mag DOUBLE,
            place VARCHAR(512),
            url VARCHAR(512),
            detail VARCHAR(512),
            longitude DOUBLE,
            latitude DOUBLE,
            depth DOUBLE,
            ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        );
    """
}
