CREATE TABLE IF NOT EXISTS bootstrap_marker (id SERIAL PRIMARY KEY, name VARCHAR(64) UNIQUE NOT NULL);
INSERT INTO bootstrap_marker(name) VALUES ('cycleapi') ON CONFLICT DO NOTHING;

CREATE TABLE IF NOT EXISTS products_product (
    id BIGSERIAL PRIMARY KEY,
    seller_id BIGINT NOT NULL,
    name VARCHAR(120) NOT NULL,
    description TEXT NOT NULL,
    original_price NUMERIC(10, 2) NOT NULL,
    sale_price NUMERIC(10, 2) NOT NULL,
    condition VARCHAR(24) NOT NULL,
    category VARCHAR(32) NOT NULL,
    images JSONB NOT NULL DEFAULT '[]'::jsonb,
    weight_kg DOUBLE PRECISION NOT NULL DEFAULT 1.0,
    is_on_sale BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS products_favorite (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL REFERENCES products_product(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, product_id)
);

CREATE INDEX IF NOT EXISTS idx_products_favorite_user_id ON products_favorite(user_id);
CREATE INDEX IF NOT EXISTS idx_products_favorite_product_id ON products_favorite(product_id);
CREATE INDEX IF NOT EXISTS idx_products_favorite_created_at ON products_favorite(created_at DESC);

CREATE TABLE IF NOT EXISTS orders_cartitem (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1 CHECK (quantity > 0)
);

CREATE TABLE IF NOT EXISTS orders_order (
    id BIGSERIAL PRIMARY KEY,
    buyer_id BIGINT NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'pending_pay',
    total_amount NUMERIC(10, 2) NOT NULL DEFAULT 0,
    items JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS points_pointledger (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    order_id BIGINT NOT NULL,
    points INTEGER NOT NULL,
    reason VARCHAR(120) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS reviews_review (
    id BIGSERIAL PRIMARY KEY,
    order_id BIGINT NOT NULL,
    reviewer_id BIGINT NOT NULL,
    reviewee_id BIGINT NOT NULL,
    rating SMALLINT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS notifications_notification (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    title VARCHAR(120) NOT NULL,
    content TEXT NOT NULL,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);
