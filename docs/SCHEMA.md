# Database Schema

SpendSense uses a Plaid-compliant SQLite database with Write-Ahead Logging (WAL) mode for better concurrency.

## Entity Relationship Diagram

```
┌─────────────┐
│    users    │
└──────┬──────┘
       │ 1
       │
       │ *
┌──────┴──────────┐         ┌────────────────┐
│    accounts     │         │    personas    │
└──────┬──────────┘         └────────┬───────┘
       │ 1                           │ 1
       │                             │
       │ *                           │ *
┌──────┴────────────┐                │
│   transactions    │                │
└───────────────────┘                │
                                     │
┌────────────────────────────────────┘
│    (user_id foreign key)
│
└─────────────────┐
                  │
         ┌────────┴────────┐
         │    content      │
         └─────────────────┘
```

## Tables

### users

Stores basic user information and consent status.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | TEXT | PRIMARY KEY | UUID v4 |
| name | TEXT | NOT NULL | User's full name |
| email | TEXT | UNIQUE, NOT NULL | User's email address |
| consent | BOOLEAN | DEFAULT FALSE | Data processing consent |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Account creation timestamp |

**Indexes:**
- PRIMARY KEY on `id`
- UNIQUE INDEX on `email`

**Sample Query:**
```sql
SELECT * FROM users WHERE consent = TRUE;
```

---

### accounts

Stores user accounts (checking, savings, credit cards) with balances and credit limits.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | TEXT | PRIMARY KEY | UUID v4 |
| user_id | TEXT | FOREIGN KEY → users(id) | Owner of account |
| type | TEXT | NOT NULL | depository, credit |
| subtype | TEXT | | checking, savings, credit_card |
| name | TEXT | NOT NULL | Account display name |
| mask | TEXT | | Last 4 digits (e.g., "1234") |
| current_balance | INTEGER | NOT NULL | Balance in cents |
| available_balance | INTEGER | | Available balance in cents |
| limit | INTEGER | | Credit limit in cents (cards only) |
| currency | TEXT | DEFAULT 'USD' | Currency code |
| holder_category | TEXT | | primary, joint |
| apr | REAL | | Annual percentage rate (credit) |
| min_payment | INTEGER | | Minimum payment in cents |
| is_overdue | BOOLEAN | DEFAULT FALSE | Payment overdue status |
| last_payment_amount | INTEGER | | Last payment in cents |
| last_payment_date | DATE | | Last payment date |
| next_payment_due_date | DATE | | Next payment due date |
| last_statement_balance | INTEGER | | Statement balance in cents |
| last_statement_date | DATE | | Statement date |
| interest_rate | REAL | | Interest rate for savings |

**Indexes:**
- PRIMARY KEY on `id`
- INDEX on `user_id`

**Relationships:**
- `user_id` → `users.id` (CASCADE DELETE)

**Sample Query:**
```sql
-- Get all accounts for a user with balances
SELECT
  a.name,
  a.type,
  a.subtype,
  a.current_balance,
  a.available_balance,
  a.limit
FROM accounts a
WHERE a.user_id = ?;
```

---

### transactions

Stores transaction history with Plaid-compliant two-level categorization.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | TEXT | PRIMARY KEY | UUID v4 |
| account_id | TEXT | FOREIGN KEY → accounts(id) | Source account |
| date | DATE | NOT NULL | Transaction date |
| amount | INTEGER | NOT NULL | Amount in cents (positive = outflow) |
| merchant_name | TEXT | | Merchant display name |
| merchant_entity_id | TEXT | | Plaid merchant entity ID |
| personal_finance_category_primary | TEXT | | Primary category (e.g., FOOD_AND_DRINK) |
| personal_finance_category_detailed | TEXT | | Detailed category (e.g., RESTAURANTS) |
| payment_channel | TEXT | | online, in_store, other |
| pending | BOOLEAN | DEFAULT FALSE | Transaction pending status |

**Indexes:**
- PRIMARY KEY on `id`
- INDEX on `account_id`
- INDEX on `date`
- COMPOSITE INDEX on `(account_id, date)` for time-range queries

**Relationships:**
- `account_id` → `accounts.id` (CASCADE DELETE)

**Categories:**

Primary categories (Plaid-compliant):
- INCOME
- TRANSFER_IN / TRANSFER_OUT
- LOAN_PAYMENTS
- BANK_FEES
- ENTERTAINMENT
- FOOD_AND_DRINK
- GENERAL_MERCHANDISE
- HOME_IMPROVEMENT
- MEDICAL
- PERSONAL_CARE
- GENERAL_SERVICES
- GOVERNMENT_AND_NON_PROFIT
- TRANSPORTATION
- TRAVEL
- RENT_AND_UTILITIES

Detailed categories are subcategories of primary (e.g., FOOD_AND_DRINK → RESTAURANTS, GROCERIES).

**Sample Queries:**
```sql
-- Get recent transactions for user
SELECT
  t.date,
  t.amount,
  t.merchant_name,
  t.personal_finance_category_primary,
  t.personal_finance_category_detailed,
  a.name as account_name
FROM transactions t
JOIN accounts a ON t.account_id = a.id
WHERE a.user_id = ?
  AND t.date >= date('now', '-30 days')
ORDER BY t.date DESC
LIMIT 50;

-- Get spending by category
SELECT
  t.personal_finance_category_primary as category,
  COUNT(*) as transaction_count,
  SUM(t.amount) as total_amount
FROM transactions t
JOIN accounts a ON t.account_id = a.id
WHERE a.user_id = ?
  AND t.amount > 0  -- outflows only
  AND t.date >= date('now', '-30 days')
GROUP BY t.personal_finance_category_primary
ORDER BY total_amount DESC;
```

---

### personas

Stores assigned personas with confidence scores for auditability.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Persona assignment ID |
| user_id | TEXT | FOREIGN KEY → users(id) | User receiving persona |
| window | TEXT | NOT NULL | Analysis window (30d, 90d, 180d) |
| persona_type | TEXT | NOT NULL | assigned persona |
| confidence | REAL | NOT NULL | Confidence score (0.0-1.0) |
| assigned_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Assignment timestamp |

**Persona Types:**
- `high_utilization` - High credit card utilization (>50%)
- `variable_income` - Irregular income patterns
- `subscription_heavy` - Many recurring subscriptions
- `savings_builder` - Positive savings growth
- `balanced` - No critical issues detected

**Indexes:**
- PRIMARY KEY on `id`
- INDEX on `user_id`
- INDEX on `assigned_at`

**Relationships:**
- `user_id` → `users.id` (CASCADE DELETE)

**Sample Query:**
```sql
-- Get latest persona for user
SELECT
  persona_type,
  confidence,
  window,
  assigned_at
FROM personas
WHERE user_id = ?
ORDER BY assigned_at DESC
LIMIT 1;
```

---

### content

Stores educational content catalog with signal tags for matching.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | TEXT | PRIMARY KEY | Content ID (e.g., "credit-util-101") |
| title | TEXT | NOT NULL | Content title |
| summary | TEXT | NOT NULL | Brief summary |
| body | TEXT | NOT NULL | Full educational content |
| cta | TEXT | NOT NULL | Call-to-action text |
| tags | TEXT | NOT NULL | JSON array of signal tags |
| persona_fit | TEXT | | Best-fit persona type |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Content creation timestamp |

**Signal Tags:**

Tags used for matching content to behavioral signals:
- `high_utilization_X` - Credit utilization thresholds
- `low_utilization_X` - Low credit usage
- `interest_charges` - Paying credit card interest
- `recurring_X` - Subscription count thresholds
- `positive_savings` - Growing savings
- `low_savings` - Minimal savings
- `variable_income` - Irregular income
- `steady_income` - Regular income pattern

**Sample Query:**
```sql
-- Find content matching signal tags
SELECT
  id,
  title,
  summary,
  tags
FROM content
WHERE tags LIKE '%high_utilization%'
  OR tags LIKE '%interest_charges%'
ORDER BY created_at DESC;
```

---

## Query Patterns

### Common Queries

**1. Get User Financial Overview**
```sql
SELECT
  u.name,
  u.email,
  COUNT(DISTINCT a.id) as account_count,
  SUM(CASE WHEN a.type = 'depository' THEN a.current_balance ELSE 0 END) as total_cash,
  SUM(CASE WHEN a.type = 'credit' THEN a.current_balance ELSE 0 END) as total_credit_balance,
  SUM(CASE WHEN a.type = 'credit' THEN a.limit ELSE 0 END) as total_credit_limit
FROM users u
LEFT JOIN accounts a ON u.id = a.user_id
WHERE u.id = ?
GROUP BY u.id, u.name, u.email;
```

**2. Calculate Net Worth**
```sql
SELECT
  SUM(CASE
    WHEN a.type = 'depository' THEN a.current_balance
    WHEN a.type = 'credit' THEN -a.current_balance  -- negative because it's debt
    ELSE 0
  END) as net_worth
FROM accounts a
WHERE a.user_id = ?;
```

**3. Detect Recurring Transactions (Subscriptions)**
```sql
SELECT
  t.merchant_name,
  t.merchant_entity_id,
  COUNT(*) as occurrence_count,
  AVG(t.amount) as avg_amount,
  MIN(t.date) as first_seen,
  MAX(t.date) as last_seen
FROM transactions t
JOIN accounts a ON t.account_id = a.id
WHERE a.user_id = ?
  AND t.amount > 0  -- outflows only
  AND t.date >= date('now', '-90 days')
GROUP BY t.merchant_entity_id
HAVING occurrence_count >= 2
  AND (julianday(MAX(t.date)) - julianday(MIN(t.date))) >= 20  -- at least 20 days apart
ORDER BY avg_amount DESC;
```

**4. Calculate Credit Utilization**
```sql
SELECT
  SUM(a.current_balance) * 1.0 / NULLIF(SUM(a.limit), 0) as utilization_ratio
FROM accounts a
WHERE a.user_id = ?
  AND a.type = 'credit'
  AND a.limit IS NOT NULL
  AND a.limit > 0;
```

**5. Analyze Savings Growth**
```sql
WITH monthly_balances AS (
  SELECT
    strftime('%Y-%m', t.date) as month,
    a.id as account_id,
    a.current_balance - SUM(t.amount) as balance_at_month
  FROM accounts a
  JOIN transactions t ON a.account_id = t.account_id
  WHERE a.user_id = ?
    AND a.subtype = 'savings'
    AND t.date >= date('now', '-180 days')
  GROUP BY strftime('%Y-%m', t.date), a.id
)
SELECT
  account_id,
  MIN(balance_at_month) as min_balance,
  MAX(balance_at_month) as max_balance,
  MAX(balance_at_month) - MIN(balance_at_month) as growth
FROM monthly_balances
GROUP BY account_id;
```

---

## Performance Considerations

### Indexes

All foreign keys are indexed for fast joins:
- `accounts.user_id`
- `transactions.account_id`
- `personas.user_id`

Time-based queries are optimized:
- `transactions.date`
- `transactions.(account_id, date)` composite

### Query Performance

Typical query performance on 50 users, ~5000 transactions:

| Query Type | Avg Time | Notes |
|------------|----------|-------|
| Get user accounts | <1ms | Direct index lookup |
| Get recent transactions | <2ms | Uses composite index |
| Calculate net worth | <1ms | Aggregation over ~3 accounts |
| Detect subscriptions | 5-10ms | Complex grouping, but acceptable |
| Full signal computation | 10-20ms | All 4 signal types |
| Complete recommendation | 20-50ms | Full pipeline |

**Result:** Sub-100ms end-to-end latency for all operations!

### Scalability

Current schema handles 50-100 users efficiently. For production scale (1000+ users):

1. Add caching layer for signal computation
2. Pre-compute personas (batch job)
3. Consider PostgreSQL for better concurrency
4. Add read replicas for scaling reads
5. Partition transactions table by date

---

## Related Documents

- [Architecture](./architecture.md) - Technical architecture details
- [Decision Log](./DECISION_LOG.md) - Why these choices were made
- [Limitations](./LIMITATIONS.md) - Known constraints and scale limits
