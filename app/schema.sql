-- Run once against the Cloud SQL instance to initialize the database.

CREATE TABLE IF NOT EXISTS orders (
    id          INT UNSIGNED    NOT NULL AUTO_INCREMENT PRIMARY KEY,
    card_id     VARCHAR(100)    NOT NULL,
    quantity    INT             NOT NULL DEFAULT 1,
    buyer_email VARCHAR(255)    NOT NULL,
    status      VARCHAR(50)     NOT NULL DEFAULT 'pending',
    created_at  TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP
);
