import { controlChannel, ControlCommand, ControlTopic, music } from "../api.js";
import { PlaylistCheckboxes } from "../playlistcheckboxes.js";
import { jsonPost, vars } from "../util.js";
import { queue } from "./queue.js";
import { Setting } from "./settings.js";

const PRIMARY_PLAYLIST = /** @type {HTMLDivElement} */ (document.getElementById('primary-playlist')).textContent;

/**
 * @param {boolean} onlyWritable
 */
export function createPlaylistDropdown(onlyWritable) {
    const select = document.createElement('select');

    for (const playlist of music.playlists()) {
        if (onlyWritable && (!playlist.write || playlist.synced)) continue;
        const option = document.createElement('option');
        option.value = playlist.name;
        option.textContent = playlist.name;
        select.appendChild(option);
    }

    select.value = PRIMARY_PLAYLIST;
    return select;
}

function updatePlaylistDropdowns() {
    console.debug('playlist: updating dropdowns');

    const selects = /** @type {HTMLCollectionOf<HTMLSelectElement>} */ (document.getElementsByClassName('playlist-select'));
    for (const select of selects) {
        const previousValue = select.value;
        const newSelect = createPlaylistDropdown(select.classList.contains('playlist-select-writable'));
        select.replaceChildren(...newSelect.children);
        select.value = previousValue ? previousValue : PRIMARY_PLAYLIST;
    }
}

const checkboxesParent = /** @type {HTMLDivElement} */ (document.getElementById('playlist-checkboxes'));
export const playlistCheckboxes = new PlaylistCheckboxes(checkboxesParent);

music.loadPlaylists();
music.waitForPlaylistsLoaded(async () => {
    updatePlaylistDropdowns();
    playlistCheckboxes.createPlaylistCheckboxes();
    queue.init();
});

// Refresh playlist checkboxes when files are changed on the server
if (!vars.offlineMode) {
    controlChannel.subscribe(ControlTopic.FILES);
    controlChannel.registerMessageHandler(ControlCommand.SERVER_FILE_CHANGE, async (/** @type {import("../types.js").ControlServerFileChange} */ data) => {
        if (data.action == "delete" || data.action == "insert") {
            await music.loadPlaylists();
            playlistCheckboxes.createPlaylistCheckboxes();
        }
    });
}

/**
 * @param {string} playlist
 * @returns {string[] | null}
 */
export function getIntersectPlaylists(playlist) {
    if (Setting.COMMON_ARTISTS.checked) {
        const playlists = playlistCheckboxes.getActivePlaylists();
        if (playlists.length < 2) {
            return null;
        }
        playlists.splice(playlists.indexOf(playlist), 1);
        return playlists
    } else {
        return null;
    }
}
