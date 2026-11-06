# Coding challenge: Top 2 orders per customer (SQL)

## Problem
You have two tables:

`customers(customer_id, name, country)`
`orders(order_id, customer_id, order_date, amount, status)`  -- status is 'paid', 'refunded' or 'pending'

For each customer, return their **two largest paid orders**. Output: `name`, `order_id`, `amount`, `rank_in_customer` (1 = largest).

Sort by `name`, then `rank_in_customer`. Customers with no paid orders must not appear. If a customer has only one paid order, return just that one.

Follow-up: if two orders tie on amount, both should get the same rank and both should be returned. What changes?

## Example
customers: (1, Asha, UK), (2, Ben, UK), (3, Cara, FR)
orders:
(10, 1, 2026-01-05, 120, paid)
(11, 1, 2026-02-10, 100, paid)
(12, 1, 2026-03-01, 150, paid)
(13, 2, 2026-01-20, 400, paid)
(14, 2, 2026-02-02, 50, refunded)

Output:
| name | order_id | amount | rank_in_customer |
|------|----------|--------|------------------|
| Asha | 12       | 150    | 1                |
| Asha | 10       | 120    | 2                |
| Ben  | 13       | 400    | 1                |

## Constraints
- Standard SQL (Postgres flavour is fine).
- Orders table could have 100M rows, so filter before ranking.
- `amount` can be NULL for some pending orders.

## Hints
<details>
<summary>Hints</summary>

1. This is a top-N per group problem. Think `ROW_NUMBER() OVER (PARTITION BY ... ORDER BY ...)`.
2. You can't filter on a window function in the same SELECT's WHERE. Use a CTE or subquery.
3. Filter `status = 'paid'` inside the CTE, before ranking, so refunds don't take a rank slot.
4. For the tie follow-up, look at how RANK and DENSE_RANK differ from ROW_NUMBER.
</details>

## How I'll review it
Open this in Claude Code and paste your query. I'll check: PARTITION BY and ORDER BY choice, where the paid filter sits, the CTE structure, NULL handling and the tie follow-up. Then I'll ask you to explain why you can't filter the window function directly, the way an interviewer would.
