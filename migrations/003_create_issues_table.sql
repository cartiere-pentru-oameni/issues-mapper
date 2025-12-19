-- Create issues table
CREATE TABLE IF NOT EXISTS issues (
    id SERIAL PRIMARY KEY,
    issue_type_id INTEGER NOT NULL REFERENCES issue_types(id) ON DELETE RESTRICT,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    image_url TEXT NOT NULL,
    image_filename VARCHAR(255) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'resolved')),
    notes TEXT,
    uploaded_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    extraction_error BOOLEAN DEFAULT FALSE,
    error_message TEXT
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_issues_type ON issues(issue_type_id);
CREATE INDEX IF NOT EXISTS idx_issues_status ON issues(status);
CREATE INDEX IF NOT EXISTS idx_issues_timestamp ON issues(timestamp);
CREATE INDEX IF NOT EXISTS idx_issues_uploaded_by ON issues(uploaded_by);
CREATE INDEX IF NOT EXISTS idx_issues_extraction_error ON issues(extraction_error);

-- Create spatial index for location queries (if PostGIS is available)
-- CREATE INDEX IF NOT EXISTS idx_issues_location ON issues USING GIST(point(longitude, latitude));

-- Create trigger for updated_at
CREATE TRIGGER update_issues_updated_at
    BEFORE UPDATE ON issues
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
