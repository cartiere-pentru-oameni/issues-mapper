-- Create issue_types table
CREATE TABLE IF NOT EXISTS issue_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on name
CREATE INDEX IF NOT EXISTS idx_issue_types_name ON issue_types(name);

-- Create trigger for updated_at
CREATE TRIGGER update_issue_types_updated_at
    BEFORE UPDATE ON issue_types
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Insert default issue types
INSERT INTO issue_types (name, active) VALUES
    ('Illegal Dumping', TRUE),
    ('Broken Street Lights', TRUE),
    ('Potholes', TRUE),
    ('Graffiti', TRUE)
ON CONFLICT (name) DO NOTHING;
