-- Multi-User Job Automation System Database Schema
-- Run this in Supabase SQL Editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    is_admin BOOLEAN DEFAULT false,
    subscription_tier VARCHAR(50) DEFAULT 'free',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create User Preferences table
CREATE TABLE IF NOT EXISTS user_preferences (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    keywords JSONB DEFAULT '[]'::jsonb,
    exclude_keywords JSONB DEFAULT '[]'::jsonb,
    locations JSONB DEFAULT '[]'::jsonb,
    min_salary INTEGER DEFAULT 0,
    max_salary INTEGER DEFAULT 999999,
    job_types JSONB DEFAULT '["full-time", "remote"]'::jsonb,
    sites_enabled JSONB DEFAULT '["linkedin", "indeed", "glassdoor"]'::jsonb,
    search_frequency_minutes INTEGER DEFAULT 15,
    linkedin_quality_threshold INTEGER DEFAULT 65,
    max_hours_old INTEGER DEFAULT 24,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create Jobs table
CREATE TABLE IF NOT EXISTS jobs (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    external_id VARCHAR(255),
    title VARCHAR(500) NOT NULL,
    company VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    salary_min INTEGER,
    salary_max INTEGER,
    job_url TEXT NOT NULL,
    description TEXT,
    site_source VARCHAR(50) NOT NULL,
    quality_score DECIMAL(5,2) DEFAULT 0,
    posted_date TIMESTAMP WITH TIME ZONE,
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(external_id, site_source)
);

-- Create User Jobs table (many-to-many relationship)
CREATE TABLE IF NOT EXISTS user_jobs (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,
    is_notified BOOLEAN DEFAULT false,
    is_applied BOOLEAN DEFAULT false,
    is_saved BOOLEAN DEFAULT false,
    is_hidden BOOLEAN DEFAULT false,
    match_score DECIMAL(5,2) DEFAULT 0,
    notified_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, job_id)
);

-- Create Admin Settings table
CREATE TABLE IF NOT EXISTS admin_settings (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value JSONB NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active);
CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id ON user_preferences(user_id);
CREATE INDEX IF NOT EXISTS idx_jobs_site_source ON jobs(site_source);
CREATE INDEX IF NOT EXISTS idx_jobs_posted_date ON jobs(posted_date);
CREATE INDEX IF NOT EXISTS idx_jobs_quality_score ON jobs(quality_score);
CREATE INDEX IF NOT EXISTS idx_jobs_scraped_at ON jobs(scraped_at);
CREATE INDEX IF NOT EXISTS idx_user_jobs_user_id ON user_jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_user_jobs_job_id ON user_jobs(job_id);
CREATE INDEX IF NOT EXISTS idx_user_jobs_notified ON user_jobs(is_notified);
CREATE INDEX IF NOT EXISTS idx_admin_settings_key ON admin_settings(setting_key);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_user_preferences_updated_at ON user_preferences;
CREATE TRIGGER update_user_preferences_updated_at 
    BEFORE UPDATE ON user_preferences 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_admin_settings_updated_at ON admin_settings;
CREATE TRIGGER update_admin_settings_updated_at 
    BEFORE UPDATE ON admin_settings 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default admin settings
INSERT INTO admin_settings (setting_key, setting_value, description) VALUES
('system_name', '"LinkedIn Job Automation System"', 'System display name'),
('max_users', '100', 'Maximum number of users allowed'),
('default_search_frequency', '15', 'Default search frequency in minutes'),
('linkedin_rate_limit', '10', 'LinkedIn requests per minute limit'),
('email_rate_limit', '50', 'Emails per hour limit')
ON CONFLICT (setting_key) DO NOTHING;

-- Create Row Level Security (RLS) policies
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_jobs ENABLE ROW LEVEL SECURITY;

-- Users can only see their own data
CREATE POLICY "Users can view own profile" ON users
    FOR SELECT USING (auth.uid()::text = id::text);

CREATE POLICY "Users can update own profile" ON users
    FOR UPDATE USING (auth.uid()::text = id::text);

-- User preferences policies
CREATE POLICY "Users can view own preferences" ON user_preferences
    FOR SELECT USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can update own preferences" ON user_preferences
    FOR UPDATE USING (auth.uid()::text = user_id::text);

-- User jobs policies
CREATE POLICY "Users can view own job interactions" ON user_jobs
    FOR SELECT USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can update own job interactions" ON user_jobs
    FOR ALL USING (auth.uid()::text = user_id::text);

-- Admin policies (users with is_admin = true can access everything)
CREATE POLICY "Admins can view all users" ON users
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE id::text = auth.uid()::text 
            AND is_admin = true
        )
    );

-- Jobs table is readable by all authenticated users
CREATE POLICY "Authenticated users can view jobs" ON jobs
    FOR SELECT USING (auth.role() = 'authenticated');

-- Create a function to get user preferences as JSON (for API)
CREATE OR REPLACE FUNCTION get_user_preferences_json(user_uuid UUID)
RETURNS JSON AS $$
DECLARE
    prefs JSON;
BEGIN
    SELECT row_to_json(user_preferences) INTO prefs
    FROM user_preferences
    WHERE user_id = user_uuid;
    
    RETURN prefs;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create a function to get user job stats
CREATE OR REPLACE FUNCTION get_user_job_stats(user_uuid UUID)
RETURNS JSON AS $$
DECLARE
    stats JSON;
BEGIN
    SELECT json_build_object(
        'total_jobs_seen', COUNT(*),
        'jobs_applied', COUNT(*) FILTER (WHERE is_applied = true),
        'jobs_saved', COUNT(*) FILTER (WHERE is_saved = true),
        'notifications_sent', COUNT(*) FILTER (WHERE is_notified = true)
    ) INTO stats
    FROM user_jobs
    WHERE user_id = user_uuid;
    
    RETURN stats;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create a view for admin dashboard
CREATE OR REPLACE VIEW admin_dashboard_stats AS
SELECT 
    (SELECT COUNT(*) FROM users) as total_users,
    (SELECT COUNT(*) FROM users WHERE is_active = true) as active_users,
    (SELECT COUNT(*) FROM jobs) as total_jobs,
    (SELECT COUNT(*) FROM user_jobs WHERE is_notified = true) as total_notifications,
    (SELECT COUNT(*) FROM jobs WHERE scraped_at > NOW() - INTERVAL '24 hours') as jobs_today,
    (SELECT COUNT(DISTINCT user_id) FROM user_jobs WHERE created_at > NOW() - INTERVAL '24 hours') as active_users_today;

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO authenticated;

-- Insert a default admin user (password: admin123 - CHANGE THIS!)
INSERT INTO users (email, name, password_hash, is_admin, subscription_tier) VALUES
('admin@jobsprint.com', 'System Administrator', 
 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', -- SHA256 of 'admin123'
 true, 'admin')
ON CONFLICT (email) DO NOTHING;

-- Create default preferences for admin user
INSERT INTO user_preferences (user_id, keywords, locations, sites_enabled)
SELECT id, 
       '["software engineer", "python developer", "java developer", "full stack developer"]'::jsonb,
       '["Remote", "San Francisco", "New York", "Seattle", "Austin"]'::jsonb,
       '["linkedin", "indeed", "glassdoor"]'::jsonb
FROM users WHERE email = 'admin@jobsprint.com'
ON CONFLICT DO NOTHING;
