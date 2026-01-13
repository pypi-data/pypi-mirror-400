# Raphson Music Player

Web-based social music player for parties or social spaces.

What makes this different from other music players? It is designed around listening with groups. Instead of playing a single playlist, this music player allows enabling many playlists from different people. Tracks are shuffled from multiple playlists into a single queue. No more arguing about which music to play, everyone's music get played.

An additional benefit of this is music discovery; even when you're listening solo you might like to mix up your own music with someone else's.

![Screenshot of music player](https://downloads.rkslot.nl/music-player-screenshots/player6-small.webp)

## Features

- Player
    - Shuffle music from multiple people's music collections ("playlists").
    - Shuffle algorithm ensures the least recently played songs are picked first.
    - Of course, you can also manually browse or search the music collection and queue specific songs.
    - Sync players so every room in your house plays the same music, or to listen together with a friend somewhere else.
- Music library
    - Create playlists using music files (like MP3, FLAC).
    - Are files too old fashioned for you? Link your Spotify playlist and it will be imported automatically!
    - Built-in web file browser to download, upload, rename and delete files.
    - WebDAV protocol support allows you to connect using a file manager of your choice.
    - Download music using the `yt-dlp`-based downloader.
    - Large, high quality album covers are fetched from MusicBrainz.
    - Time synced lyrics are fetched from various sources.
    - Artist information is downloaded from wikipedia.
    - A metadata editor is available to easily correct metadata while listening.
    - Audio is loudness-normalized ensuring consistent volume for all genres, without losing dynamic range.
- Responsive and mobile compatible
    - Touch-friendly interface.
    - Optionally, stream at a lower quality to save data.
    - Implements the (Open)Subsonic protocol, allowing you to use native apps.
- Statistics
    - See what others are playing now or in the past.
    - Statistics page with graphs based on historical data.
    - Users can connect their last.fm account to also save play history there.
- News
    - Optionally, play hourly news just like real radio.
- Fun
    - Enable 'Album cover meme mode' to replace album covers by (sometimes) funny memes related to the song title.
    - Play games with your music collections, like a music guessing game.
- Simple sofware philosophy
    - The server is simple to run with one command. No other services, like a database, are needed.
    - Python dependencies are kept to a minimum to ensure portability.
    - Queued songs are cached, temporary network connection issues are no problem.
    - Written in pure HTML, CSS and JavaScript with only one third party library (eCharts). The frontend should be fast, even on an old laptop or cheap single board computer.

## Demo

See [docs/demo.md](docs/demo.md).

## Screenshots

See [docs/screenshots.md](docs/screenshots.md) (will load ~20MB of images).

## Usage

See [docs/installation.md](docs/installation.md).

## Related projects

- [Headless client](https://codeberg.org/raphson/music-headless): to run on a headless machine with an audio output. Can be controlled remotely.
- [Headless client HA](https://codeberg.org/raphson/music-headless-ha): Home Assistant integration to control a headless client.

## Development and translation

See [docs/development.md](docs/development.md).
