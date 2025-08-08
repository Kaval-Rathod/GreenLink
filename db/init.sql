CREATE EXTENSION IF NOT EXISTS postgis;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    wallet_address TEXT,
    location geometry(Point, 4326),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Submissions table: image uploads with optional GPS and analysis results
CREATE TABLE IF NOT EXISTS submissions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    photo_path TEXT NOT NULL,
    gps_coords geometry(Point, 4326),
    greenery_pct DOUBLE PRECISION,
    carbon_value DOUBLE PRECISION,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Credits table: tokenized carbon credits attribution to users
CREATE TABLE IF NOT EXISTS credits (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    tonnes_co2 DOUBLE PRECISION NOT NULL,
    token_id TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
