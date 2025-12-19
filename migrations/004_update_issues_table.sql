-- Update issues table to match upload functionality

-- Drop old constraints on latitude, longitude, and timestamp to allow NULL for failed extractions
ALTER TABLE issues ALTER COLUMN latitude DROP NOT NULL;
ALTER TABLE issues ALTER COLUMN longitude DROP NOT NULL;
ALTER TABLE issues ALTER COLUMN timestamp DROP NOT NULL;

-- Rename image_filename to image_path
ALTER TABLE issues RENAME COLUMN image_filename TO image_path;

-- Add raw_extraction_text column for debugging
ALTER TABLE issues ADD COLUMN IF NOT EXISTS raw_extraction_text TEXT;

-- Update image_url to allow NULL (in case storage upload fails)
ALTER TABLE issues ALTER COLUMN image_url DROP NOT NULL;
