-- Move sync settings to playlist table
BEGIN;

ALTER TABLE playlist ADD COLUMN sync_type TEXT NULL;
ALTER TABLE playlist ADD COLUMN sync_ref TEXT NULL;

UPDATE playlist SET sync_type = 'spotify' WHERE EXISTS(SELECT 1 FROM spotify_sync WHERE playlist = name);
UPDATE playlist SET sync_ref = (SELECT spotify_id FROM spotify_sync WHERE playlist = name) WHERE EXISTS(SELECT 1 FROM spotify_sync WHERE playlist = name);

DROP TABLE spotify_sync;

COMMIT;
