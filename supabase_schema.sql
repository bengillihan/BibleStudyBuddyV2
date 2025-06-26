-- Bible Study Buddy Database Schema for Supabase
-- Run this SQL in your Supabase SQL Editor to create the required tables

-- Create the users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(64) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create the study_sessions table
CREATE TABLE IF NOT EXISTS study_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    passage VARCHAR(200) NOT NULL,
    date DATE NOT NULL,
    
    -- 10 reflection questions
    question_1 TEXT,
    question_2 TEXT,
    question_3 TEXT,
    question_4 TEXT,
    question_5 TEXT,
    question_6 TEXT,
    question_7 TEXT,
    question_8 TEXT,
    question_9 TEXT,
    question_10 TEXT,
    
    -- Passage text and analysis
    passage_text TEXT NOT NULL,
    word_freq_json TEXT,  -- JSON string for word frequency
    bigram_freq_json TEXT,  -- JSON string for bigram frequency
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_study_sessions_user_id ON study_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_study_sessions_updated_at ON study_sessions(updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_study_sessions_created_at ON study_sessions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Create a function to automatically update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers to automatically update updated_at timestamps
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_study_sessions_updated_at 
    BEFORE UPDATE ON study_sessions 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (RLS)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE study_sessions ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for users table
CREATE POLICY "Users can view their own profile" ON users
    FOR SELECT USING (auth.uid()::text = id::text);

CREATE POLICY "Users can update their own profile" ON users
    FOR UPDATE USING (auth.uid()::text = id::text);

-- Create RLS policies for study_sessions table
CREATE POLICY "Users can view their own study sessions" ON study_sessions
    FOR SELECT USING (user_id = (SELECT id FROM users WHERE auth.uid()::text = id::text));

CREATE POLICY "Users can insert their own study sessions" ON study_sessions
    FOR INSERT WITH CHECK (user_id = (SELECT id FROM users WHERE auth.uid()::text = id::text));

CREATE POLICY "Users can update their own study sessions" ON study_sessions
    FOR UPDATE USING (user_id = (SELECT id FROM users WHERE auth.uid()::text = id::text));

CREATE POLICY "Users can delete their own study sessions" ON study_sessions
    FOR DELETE USING (user_id = (SELECT id FROM users WHERE auth.uid()::text = id::text));

-- Grant necessary permissions (if needed)
GRANT USAGE ON SCHEMA public TO postgres, anon, authenticated, service_role;
GRANT ALL ON ALL TABLES IN SCHEMA public TO postgres, anon, authenticated, service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO postgres, anon, authenticated, service_role;