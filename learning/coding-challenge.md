# Coding challenge: Repeat high-value customers (SQL)

## Problem
You have two tables:

`customers(customer_id, name, country)`
`orders(order_id, customer_id, order_date, amount, status)`  -- status is 'paid', 'refunded' or 'pending'

Write a query that returns, for each customer who has **at least 3 paid orders in 2026** and a **total paid spend above £300**:
`name`, `paid_orders` (count), `total_spend`, `avg_order_value` (rounded to 2 dp).

Sort by `total_spend` descending. Customers with no orders must not appear.

## Example
customers: (1, Asha, UK), (2, Ben, UK), (3, Cara, FR)
orders:
(10, 1, 2026-01-05, 120, paid)
(11, 1, 2026-02-10, 100, paid)
(12, 1, 2026-03-01, 150, paid)
(13, 2, 2026-01-20, 400, paid)
(14, 2, 2026-02-02, 50, refunded)
(15, 3, 2025-12-30, 90, paid)

Output:
| name | paid_orders | total_spend | avg_order_value |
|------|-------------|-------------|-----------------|
| Asha | 3           | 370         | 123.33          |

(Ben has only 1 paid order; Cara's order is in 2025.)

## Constraints
- Standard SQL (Postgres flavour is fine).
- Orders table could have 100M rows, so filter early.
- `amount` can be NULL for some pending orders.

## Hints
<details>
<summary>Hints</summary>

1. Which conditions are about single rows (status, year)? Which are about groups (count, sum)?
2. Row conditions go in WHERE, group conditions in HAVING.
3. Join to customers to get the name, and remember to include it in GROUP BY (or group by customer_id and name).
4. For the date filter, prefer `order_date >= '2026-01-01' AND order_date < '2027-01-01'` over wrapping the column in a function, so an index can be used.
</details>

## How I'll review it
Open this in Claude Code and paste your query. I'll check: correct WHERE vs HAVING placement, the date filter, NULL handling, GROUP BY validity, and whether it would scale. Then I'll ask you to explain why each condition sits where it does, the way an interviewer would.
