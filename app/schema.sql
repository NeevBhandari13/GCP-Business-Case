-- Run once against the Cloud SQL instance to initialize the database.
-- Connection: psql -h /cloudsql/PROJECT:REGION:INSTANCE -U app -d orders

CREATE TABLE IF NOT EXISTS orders (
    id          SERIAL PRIMARY KEY,
    card_id     VARCHAR(100)  NOT NULL,
    quantity    INTEGER       NOT NULL DEFAULT 1,
    buyer_email VARCHAR(255)  NOT NULL,
    status      VARCHAR(50)   NOT NULL DEFAULT 'pending',
    created_at  TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);
