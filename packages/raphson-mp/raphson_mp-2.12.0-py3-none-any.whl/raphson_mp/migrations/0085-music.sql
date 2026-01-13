-- Remove track column from blob table
-- Add new ref, reftype columns
PRAGMA foreign_keys=OFF;
BEGIN;

CREATE TABLE blob_new (
    id TEXT NOT NULL UNIQUE,
    blobtype TEXT NOT NULL,
    ref TEXT NOT NULL,
    reftype TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    UNIQUE(blobtype, ref, reftype)
) STRICT;

INSERT INTO blob_new SELECT id, blobtype, track, 'track', timestamp FROM blob;

DROP TABLE blob;

ALTER TABLE blob_new RENAME TO blob;

COMMIT;
