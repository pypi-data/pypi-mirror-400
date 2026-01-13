CREATE TABLE saved_player_state (
    user INTEGER NOT NULL REFERENCES user(id),
    player_id TEXT NOT NULL,
    tracks TEXT NOT NULL,
    UNIQUE(user, player_id)
) STRICT;
