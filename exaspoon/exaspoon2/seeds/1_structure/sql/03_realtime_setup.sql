-- ============================================
-- REALTIME SETUP FOR SUPABASE
-- ============================================
-- This script enables real-time subscriptions for the financial dashboard
-- Run this script in your Supabase SQL editor to enable real-time features

-- Enable Realtime for required tables
-- Note: This requires Supabase project with Realtime enabled

-- 1. Enable Realtime for accounts table
-- This allows real-time updates when accounts are added, modified, or deleted
ALTER PUBLICATION supabase_realtime ADD TABLE accounts;

-- 2. Enable Realtime for transactions table
-- This allows real-time updates when transactions are added, modified, or deleted
ALTER PUBLICATION supabase_realtime ADD TABLE transactions;

-- 3. Enable Realtime for categories table
-- This allows real-time updates when categories are added, modified, or deleted
ALTER PUBLICATION supabase_realtime ADD TABLE categories;

-- ============================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================
-- Uncomment and modify these policies if you have user authentication
-- This ensures users can only see their own data in real-time subscriptions

/*
-- Enable RLS on all tables
ALTER TABLE accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE categories ENABLE ROW LEVEL SECURITY;

-- Accounts policies
CREATE POLICY "Users can view their own accounts in realtime" ON accounts
    FOR SELECT USING (
        auth.uid() IS NOT NULL AND
        (metadata->>'user_id')::text = auth.uid()::text
    );

CREATE POLICY "Users can insert their own accounts in realtime" ON accounts
    FOR INSERT WITH CHECK (
        auth.uid() IS NOT NULL AND
        (metadata->>'user_id')::text = auth.uid()::text
    );

CREATE POLICY "Users can update their own accounts in realtime" ON accounts
    FOR UPDATE USING (
        auth.uid() IS NOT NULL AND
        (metadata->>'user_id')::text = auth.uid()::text
    );

CREATE POLICY "Users can delete their own accounts in realtime" ON accounts
    FOR DELETE USING (
        auth.uid() IS NOT NULL AND
        (metadata->>'user_id')::text = auth.uid()::text
    );

-- Transactions policies
CREATE POLICY "Users can view their own transactions in realtime" ON transactions
    FOR SELECT USING (
        auth.uid() IS NOT NULL AND
        (SELECT metadata->>'user_id' FROM accounts WHERE id = transactions.account_id)::text = auth.uid()::text
    );

CREATE POLICY "Users can insert their own transactions in realtime" ON transactions
    FOR INSERT WITH CHECK (
        auth.uid() IS NOT NULL AND
        (SELECT metadata->>'user_id' FROM accounts WHERE id = transactions.account_id)::text = auth.uid()::text
    );

CREATE POLICY "Users can update their own transactions in realtime" ON transactions
    FOR UPDATE USING (
        auth.uid() IS NOT NULL AND
        (SELECT metadata->>'user_id' FROM accounts WHERE id = transactions.account_id)::text = auth.uid()::text
    );

CREATE POLICY "Users can delete their own transactions in realtime" ON transactions
    FOR DELETE USING (
        auth.uid() IS NOT NULL AND
        (SELECT metadata->>'user_id' FROM accounts WHERE id = transactions.account_id)::text = auth.uid()::text
    );

-- Categories policies (shared across users, but RLS enabled)
CREATE POLICY "Users can view categories in realtime" ON categories
    FOR SELECT USING (true);

CREATE POLICY "Authenticated users can insert categories in realtime" ON categories
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "Authenticated users can update categories in realtime" ON categories
    FOR UPDATE USING (auth.role() = 'authenticated');

CREATE POLICY "Authenticated users can delete categories in realtime" ON categories
    FOR DELETE USING (auth.role() = 'authenticated');
*/

-- ============================================
-- INDEXES FOR OPTIMAL REALTIME PERFORMANCE
-- ============================================
-- Add indexes to improve real-time subscription performance

-- Accounts indexes
CREATE INDEX IF NOT EXISTS idx_accounts_type ON accounts(type);
CREATE INDEX IF NOT EXISTS idx_accounts_currency ON accounts(currency);
CREATE INDEX IF NOT EXISTS idx_accounts_network ON accounts(network);

-- Transactions indexes
CREATE INDEX IF NOT EXISTS idx_transactions_account_id ON transactions(account_id);
CREATE INDEX IF NOT EXISTS idx_transactions_occurred_at ON transactions(occurred_at DESC);
CREATE INDEX IF NOT EXISTS idx_transactions_direction ON transactions(direction);
CREATE INDEX IF NOT EXISTS idx_transactions_category_id ON transactions(category_id);
-- CREATE INDEX IF NOT EXISTS idx_transactions_created_at ON transactions(created_at DESC);

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_transactions_account_date ON transactions(account_id, occurred_at DESC);
CREATE INDEX IF NOT EXISTS idx_transactions_category_date ON transactions(category_id, occurred_at DESC);

-- Categories indexes
CREATE INDEX IF NOT EXISTS idx_categories_kind ON categories(kind);
CREATE INDEX IF NOT EXISTS idx_categories_name ON categories(name);

-- ============================================
-- FUNCTIONS FOR REALTIME TRIGGERS
-- ============================================
-- Create function to handle realtime notifications
-- This can be used for custom real-time event handling

CREATE OR REPLACE FUNCTION notify_realtime_change()
RETURNS TRIGGER AS $$
BEGIN
    -- Log the change for debugging
    RAISE LOG 'Realtime change: % on table %', TG_OP, TG_TABLE_NAME;

    -- The actual realtime publication is handled by Supabase automatically
    -- This function is for custom notification logic if needed

    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- TRIGGERS FOR CUSTOM REALTIME LOGIC
-- ============================================
-- Add triggers if you need custom logic beyond Supabase's built-in realtime

/*
-- Example: Add trigger for accounts
CREATE TRIGGER accounts_realtime_trigger
    AFTER INSERT OR UPDATE OR DELETE ON accounts
    FOR EACH ROW EXECUTE FUNCTION notify_realtime_change();

-- Example: Add trigger for transactions
CREATE TRIGGER transactions_realtime_trigger
    AFTER INSERT OR UPDATE OR DELETE ON transactions
    FOR EACH ROW EXECUTE FUNCTION notify_realtime_change();

-- Example: Add trigger for categories
CREATE TRIGGER categories_realtime_trigger
    AFTER INSERT OR UPDATE OR DELETE ON categories
    FOR EACH ROW EXECUTE FUNCTION notify_realtime_change();
*/

-- ============================================
-- VERIFICATION QUERIES
-- ============================================
-- Run these queries to verify that realtime is enabled

-- Check which tables are in the realtime publication
SELECT
    schemaname,
    tablename
FROM pg_publication_tables
WHERE pubname = 'supabase_realtime'
ORDER BY schemaname, tablename;

-- Check RLS status on tables (if RLS policies are enabled)
SELECT
    schemaname,
    tablename,
    rowsecurity
FROM pg_tables
WHERE schemaname = 'public'
    AND tablename IN ('accounts', 'transactions', 'categories')
ORDER BY tablename;

-- ============================================
-- ENVIRONMENT VARIABLES NEEDED
-- ============================================
-- Make sure these environment variables are set in your application:

-- SUPABASE_URL=your_supabase_project_url
-- SUPABASE_SERVICE_KEY=your_supabase_service_key
-- SUPABASE_ANON_KEY=your_supabase_anon_key (required for realtime subscriptions)

-- ============================================
-- USAGE NOTES
-- ============================================
-- 1. Ensure Realtime is enabled in your Supabase project settings
-- 2. Set the ANON key in your environment variables for frontend realtime connections
-- 3. If using authentication, uncomment and modify the RLS policies above
-- 4. Test the setup by adding/modifying records and checking for realtime updates

SELECT 'Realtime setup completed successfully! 🚀' as status;
