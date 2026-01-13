CREATE TABLE spotify_sync (
    playlist TEXT NOT NULL UNIQUE REFERENCES playlist(name) ON DELETE CASCADE,
    spotify_id TEXT NOT NULL UNIQUE
) STRICT;
