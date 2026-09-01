CREATE OR REPLACE VIEW sales_ranking AS

SELECT
    s.product_id,

    p.product_category_name,

    SUM(s.quantity) AS units_sold,

    SUM(
        s.quantity * s.unit_price
    ) AS revenue,

    AVG(s.unit_price) AS average_price

FROM sales s

JOIN products p
    ON s.product_id = p.product_id

GROUP BY
    s.product_id,
    p.product_category_name;


CREATE OR REPLACE VIEW inventory_health AS

SELECT
    i.product_id,

    p.product_category_name,

    i.quantity,

    i.reserved_quantity,

    i.minimum_stock,

    i.reorder_point,

    i.reorder_quantity,

    COALESCE(
        SUM(s.quantity),
        0
    ) AS total_units_sold,

    CASE

        WHEN i.quantity <= 0
            THEN 'OUT_OF_STOCK'

        WHEN i.quantity <= i.minimum_stock
            THEN 'CRITICAL'

        WHEN i.quantity <= i.reorder_point
            THEN 'LOW_STOCK'

        ELSE 'HEALTHY'

    END AS stock_status

FROM inventory i

JOIN products p
    ON i.product_id = p.product_id

LEFT JOIN sales s
    ON i.product_id = s.product_id

GROUP BY
    i.product_id,
    p.product_category_name,
    i.quantity,
    i.reserved_quantity,
    i.minimum_stock,
    i.reorder_point,
    i.reorder_quantity;


CREATE OR REPLACE VIEW pending_replenishments AS

SELECT
    t.task_id,

    t.product_id,

    p.product_category_name,

    t.quantity,

    t.priority,

    t.status,

    t.created_at

FROM tasks t

JOIN products p
    ON t.product_id = p.product_id

WHERE
    t.task_type = 'REPLENISHMENT'

    AND t.status IN (
        'PENDING',
        'IN_PROGRESS'
    );


CREATE OR REPLACE VIEW agent_decision_history AS

SELECT
    decision_id,

    agent_name,

    product_id,

    decision_type,

    reasoning,

    decision_data,

    created_at

FROM decisions

ORDER BY created_at DESC;


CREATE OR REPLACE VIEW simulation_activity AS

SELECT
    event_id,

    event_type,

    product_id,

    quantity,

    event_data,

    event_timestamp

FROM events

ORDER BY event_timestamp DESC;


CREATE OR REPLACE VIEW purchase_status AS

SELECT
    pu.purchase_id,

    pu.product_id,

    p.product_category_name,

    pu.supplier_id,

    s.supplier_name,

    pu.quantity,

    pu.unit_cost,

    pu.status,

    pu.expected_delivery,

    pu.delivered_at,

    CASE

        WHEN pu.status = 'DELIVERED'
            THEN 'DELIVERED'

        WHEN pu.expected_delivery <= CURRENT_TIMESTAMP
            THEN 'OVERDUE'

        ELSE 'IN_TRANSIT'

    END AS delivery_status

FROM purchases pu

JOIN products p
    ON pu.product_id = p.product_id

JOIN suppliers s
    ON pu.supplier_id = s.supplier_id;


CREATE OR REPLACE VIEW inventory_movements_history AS

SELECT
    m.movement_id,

    m.product_id,

    p.product_category_name,

    m.movement_type,

    m.quantity,

    m.reference_id,

    m.created_at

FROM inventory_movements m

JOIN products p
    ON m.product_id = p.product_id

ORDER BY m.created_at DESC;