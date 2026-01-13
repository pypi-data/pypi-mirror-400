CREATE TABLE playlist_sync_errors (
    playlist TEXT NOT NULL REFERENCES playlist(name),
    type TEXT NOT NULL,
    display TEXT NOT NULL
) STRICT;
