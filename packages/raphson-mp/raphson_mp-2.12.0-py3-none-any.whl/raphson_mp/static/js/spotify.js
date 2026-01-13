import { createToast, gettext } from "./util.js";

// Compare
const spotifySubmit = /** @type {HTMLInputElement} */ (document.getElementById('spotify-submit'));
const localPlaylist = /** @type {HTMLSelectElement} */ (document.getElementById('spotify-compare-local-playlist'));
const spotifyPlaylistUrl = /** @type {HTMLInputElement} */ (document.getElementById('spotify-compare-remote-playlist'));

spotifySubmit.addEventListener('click', () => {
    const playlist = localPlaylist.value;

    const input = spotifyPlaylistUrl.value;
    let spotifyPlaylistId = null;

    if (input.startsWith('https://open.spotify.com/playlist/')) {
        spotifyPlaylistId = input.substring('https://open.spotify.com/playlist/'.length);

        // Remove query string for e.g. share tracking
        if (input.includes('?')) {
            spotifyPlaylistId = spotifyPlaylistId.substring(0, spotifyPlaylistId.indexOf('?'));
        }
    } else if (/^[A-Za-z0-9]+$/.test(input)) { // base62 value
        spotifyPlaylistId = input;
    } else {
        createToast('icon-close', gettext("Invalid Spotify playlist URL or id"));
        return;
    }

    window.location.assign(`/spotify/compare?playlist=${encodeURIComponent(playlist)}&spotify_playlist=${encodeURIComponent(spotifyPlaylistId)}`);
});
