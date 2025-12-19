-- Remove status column from issues table

ALTER TABLE issues DROP COLUMN IF EXISTS status;
