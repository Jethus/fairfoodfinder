CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    store VARCHAR(100),
    category VARCHAR(100),
    name VARCHAR(255),
    price DECIMAL(10, 2),
    unit_price DECIMAL(10, 2),
    sale_price DECIMAL(10, 2),
    previous_price DECIMAL(10, 2),
    image_url TEXT,
    link TEXT,
    brand VARCHAR(100),
    package_size VARCHAR(50),
    stock VARCHAR(50),
    points VARCHAR(50),
    date_scraped TIMESTAMP,
    product_id VARCHAR(32),
    organic BOOLEAN
);

CREATE INDEX idx_product_id ON products(product_id);
CREATE INDEX idx_date_scraped ON products(date_scraped);