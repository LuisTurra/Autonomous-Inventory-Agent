
CREATE TABLE IF NOT EXISTS products (
    product_id VARCHAR(100) PRIMARY KEY,

    product_category_name VARCHAR(100),

    unit_price NUMERIC(12,2),

    reorder_point INTEGER DEFAULT 10,
    reorder_quantity INTEGER DEFAULT 50,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS inventory (
    product_id VARCHAR(100) PRIMARY KEY,

    quantity INTEGER NOT NULL DEFAULT 0,
    reserved_quantity INTEGER NOT NULL DEFAULT 0,

    minimum_stock INTEGER NOT NULL DEFAULT 5,
    reorder_point INTEGER NOT NULL DEFAULT 10,
    reorder_quantity INTEGER NOT NULL DEFAULT 50,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (product_id)
        REFERENCES products(product_id),

    CHECK (quantity >= 0),
    CHECK (reserved_quantity >= 0)
);


CREATE TABLE IF NOT EXISTS suppliers (
    supplier_id SERIAL PRIMARY KEY,

    supplier_name VARCHAR(150) NOT NULL,

    lead_time_days INTEGER DEFAULT 7,

    reliability NUMERIC(5,4) DEFAULT 0.95,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS sales (
    sale_id BIGSERIAL PRIMARY KEY,

    product_id VARCHAR(100) NOT NULL,

    quantity INTEGER NOT NULL,

    unit_price NUMERIC(12,2) NOT NULL,

    sale_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (product_id)
        REFERENCES products(product_id),

    CHECK (quantity > 0)
);


CREATE TABLE IF NOT EXISTS purchases (
    purchase_id BIGSERIAL PRIMARY KEY,

    product_id VARCHAR(100) NOT NULL,

    supplier_id INTEGER,

    quantity INTEGER NOT NULL,

    unit_cost NUMERIC(12,2),

    status VARCHAR(30) DEFAULT 'ORDERED',

    ordered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    expected_delivery TIMESTAMP,

    delivered_at TIMESTAMP,

    FOREIGN KEY (product_id)
        REFERENCES products(product_id),

    FOREIGN KEY (supplier_id)
        REFERENCES suppliers(supplier_id),

    CHECK (quantity > 0)
);


CREATE TABLE IF NOT EXISTS inventory_movements (
    movement_id BIGSERIAL PRIMARY KEY,

    product_id VARCHAR(100) NOT NULL,

    movement_type VARCHAR(30) NOT NULL,

    quantity INTEGER NOT NULL,

    reference_id BIGINT,

    movement_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (product_id)
        REFERENCES products(product_id)
);


CREATE TABLE IF NOT EXISTS events (
    event_id BIGSERIAL PRIMARY KEY,

    event_type VARCHAR(50) NOT NULL,

    product_id VARCHAR(100),

    quantity INTEGER,

    event_data JSONB,

    event_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    processed BOOLEAN DEFAULT FALSE,

    FOREIGN KEY (product_id)
        REFERENCES products(product_id)
);


CREATE TABLE IF NOT EXISTS tasks (
    task_id BIGSERIAL PRIMARY KEY,

    task_type VARCHAR(50) NOT NULL,

    product_id VARCHAR(100),

    quantity INTEGER,

    priority VARCHAR(20) DEFAULT 'NORMAL',

    status VARCHAR(30) DEFAULT 'PENDING',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    completed_at TIMESTAMP,

    FOREIGN KEY (product_id)
        REFERENCES products(product_id)
);


CREATE TABLE IF NOT EXISTS decisions (
    decision_id BIGSERIAL PRIMARY KEY,

    agent_name VARCHAR(100) NOT NULL,

    product_id VARCHAR(100),

    decision_type VARCHAR(50) NOT NULL,

    reasoning TEXT,

    decision_data JSONB,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (product_id)
        REFERENCES products(product_id)
);


CREATE TABLE IF NOT EXISTS agent_memory (
    memory_id BIGSERIAL PRIMARY KEY,

    agent_name VARCHAR(100) NOT NULL,

    memory_type VARCHAR(50),

    context JSONB,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================
-- INDEXES
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_sales_product
    ON sales(product_id);

CREATE INDEX IF NOT EXISTS idx_sales_timestamp
    ON sales(sale_timestamp);

CREATE INDEX IF NOT EXISTS idx_inventory_movements_product
    ON inventory_movements(product_id);

CREATE INDEX IF NOT EXISTS idx_events_processed
    ON events(processed);

CREATE INDEX IF NOT EXISTS idx_events_timestamp
    ON events(event_timestamp);

CREATE INDEX IF NOT EXISTS idx_tasks_status
    ON tasks(status);

CREATE INDEX IF NOT EXISTS idx_decisions_product
    ON decisions(product_id);