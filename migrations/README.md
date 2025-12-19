# Database Migrations

This folder contains SQL migration files to set up the database schema in Supabase.

## How to Apply Migrations

1. Log in to your Supabase dashboard
2. Navigate to the SQL Editor
3. Run each migration file in order (001, 002, 003, etc.)
4. Verify the tables were created successfully

## Migration Files

- **001_create_users_table.sql** - Creates users table with authentication fields
- **002_create_issue_types_table.sql** - Creates issue types table with default categories
- **003_create_issues_table.sql** - Creates issues table for reported problems

## Order is Important

Run the migrations in numerical order as later migrations may depend on earlier ones (e.g., foreign key relationships).

## Verification

After running all migrations, verify with:

```sql
-- Check all tables exist
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public';

-- Check users table is empty (for first-time setup)
SELECT COUNT(*) FROM users;
```
