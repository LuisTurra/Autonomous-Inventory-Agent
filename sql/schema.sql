CREATE TABLE IF NOT EXISTS products (

    product_id VARCHAR(50) PRIMARY KEY,

    product_category_name VARCHAR(100),

    unit_price NUMERIC(12, 2) NOT NULL DEFAULT 0

);


CREATE TABLE IF NOT EXISTS inventory (

    product_id VARCHAR(50) PRIMARY KEY
        REFERENCES products(product_id),

    quantity INTEGER NOT NULL DEFAULT 0,

    reserved_quantity INTEGER NOT NULL DEFAULT 0,

    minimum_stock INTEGER NOT NULL DEFAULT 10,

    reorder_point INTEGER NOT NULL DEFAULT 20,

    reorder_quantity INTEGER NOT NULL DEFAULT 50,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);


CREATE TABLE IF NOT EXISTS suppliers (

    supplier_id SERIAL PRIMARY KEY,

    supplier_name VARCHAR(150) NOT NULL,

    lead_time_days INTEGER NOT NULL,

    reliability NUMERIC(5, 2) NOT NULL

);


CREATE TABLE IF NOT EXISTS sales (

    sale_id BIGSERIAL PRIMARY KEY,

    product_id VARCHAR(50) NOT NULL
        REFERENCES products(product_id),

    quantity INTEGER NOT NULL,

    unit_price NUMERIC(12, 2) NOT NULL,

    sale_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);


CREATE TABLE IF NOT EXISTS purchases (

    purchase_id BIGSERIAL PRIMARY KEY,

    product_id VARCHAR(50) NOT NULL
        REFERENCES products(product_id),

    supplier_id INTEGER NOT NULL
        REFERENCES suppliers(supplier_id),

    quantity INTEGER NOT NULL,

    unit_cost NUMERIC(12, 2) NOT NULL,

    status VARCHAR(30) NOT NULL DEFAULT 'ORDERED',

    expected_delivery TIMESTAMP,

    delivered_at TIMESTAMP

);


CREATE TABLE IF NOT EXISTS inventory_movements (

    movement_id BIGSERIAL PRIMARY KEY,

    product_id VARCHAR(50) NOT NULL
        REFERENCES products(product_id),

    movement_type VARCHAR(30) NOT NULL,

    quantity INTEGER NOT NULL,

    reference_id BIGINT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);


CREATE TABLE IF NOT EXISTS events (

    event_id BIGSERIAL PRIMARY KEY,

    event_type VARCHAR(50) NOT NULL,

    product_id VARCHAR(50),

    quantity INTEGER,

    event_data JSONB,

    event_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);


CREATE TABLE IF NOT EXISTS tasks (

    task_id BIGSERIAL PRIMARY KEY,

    task_type VARCHAR(50) NOT NULL,

    product_id VARCHAR(50)
        REFERENCES products(product_id),

    quantity INTEGER,

    priority VARCHAR(20),

    status VARCHAR(30) NOT NULL DEFAULT 'PENDING',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    completed_at TIMESTAMP

);


CREATE TABLE IF NOT EXISTS decisions (

    decision_id BIGSERIAL PRIMARY KEY,

    agent_name VARCHAR(100) NOT NULL,

    product_id VARCHAR(50),

    decision_type VARCHAR(100) NOT NULL,

    reasoning TEXT,

    decision_data JSONB,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);


CREATE TABLE IF NOT EXISTS agent_memory (

    memory_id BIGSERIAL PRIMARY KEY,

    agent_name VARCHAR(100) NOT NULL,

    memory_type VARCHAR(50),

    context JSONB,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);


CREATE INDEX IF NOT EXISTS idx_sales_product
ON sales(product_id);


CREATE INDEX IF NOT EXISTS idx_sales_timestamp
ON sales(sale_timestamp);


CREATE INDEX IF NOT EXISTS idx_events_timestamp
ON events(event_timestamp);


CREATE INDEX IF NOT EXISTS idx_events_product
ON events(product_id);


CREATE INDEX IF NOT EXISTS idx_tasks_status
ON tasks(status);


CREATE INDEX IF NOT EXISTS idx_tasks_product
ON tasks(product_id);


CREATE INDEX IF NOT EXISTS idx_purchases_status
ON purchases(status);


CREATE INDEX IF NOT EXISTS idx_purchases_product
ON purchases(product_id);


CREATE INDEX IF NOT EXISTS idx_decisions_created
ON decisions(created_at);


CREATE INDEX IF NOT EXISTS idx_decisions_product
ON decisions(product_id);

ALTER TABLE sales
ADD COLUMN IF NOT EXISTS is_simulated BOOLEAN NOT NULL DEFAULT FALSE;

ALTER TABLE purchases
ADD COLUMN IF NOT EXISTS is_simulated BOOLEAN NOT NULL DEFAULT FALSE;

ALTER TABLE inventory_movements
ADD COLUMN IF NOT EXISTS is_simulated BOOLEAN NOT NULL DEFAULT FALSE;

ALTER TABLE events
ADD COLUMN IF NOT EXISTS is_simulated BOOLEAN NOT NULL DEFAULT FALSE;

ALTER TABLE tasks
ADD COLUMN IF NOT EXISTS is_simulated BOOLEAN NOT NULL DEFAULT FALSE;

ALTER TABLE decisions
ADD COLUMN IF NOT EXISTS is_simulated BOOLEAN NOT NULL DEFAULT FALSE;


CREATE TABLE IF NOT EXISTS simulation_inventory_snapshot (

    product_id VARCHAR(50) PRIMARY KEY
        REFERENCES products(product_id),

    quantity INTEGER NOT NULL,

    reserved_quantity INTEGER NOT NULL,

    minimum_stock INTEGER NOT NULL,

    reorder_point INTEGER NOT NULL,

    reorder_quantity INTEGER NOT NULL
);