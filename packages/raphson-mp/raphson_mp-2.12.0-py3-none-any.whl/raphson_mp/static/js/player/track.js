import { AlbumBrowse, ArtistBrowse, browse, PlaylistBrowse, TitleBrowse, YearBrowse } from "./browse.js";
import { Artist, Track } from "../api.js";
import { createIcon, createToast, gettext, jsonPost, vars } from "../util.js";
import { editor } from "./editor.js";
import { queue } from "./queue.js";
import { windows } from "./window.js";
import { AbstractMenuEntry, ContextMenu, MenuEntry, MenuSeparator } from "../contextmenu.js";
import { Setting } from "./settings.js";


let copyTrack = /** @type {Track | null} */ (null);
if (!vars.offlineMode) {
    const copyPlaylist = /** @type {HTMLSelectElement} */ (document.getElementById('copy-playlist'));
    const copyDoButton = /** @type {HTMLButtonElement} */ (document.getElementById('copy-do-button'));
    copyDoButton.addEventListener('click', async () => {
        if (!copyTrack) throw new Error();
        if (copyPlaylist.value == '') return;
        copyDoButton.disabled = true;
        await copyTrack.copyTo(copyPlaylist.value);
        windows.closeTop();
        copyDoButton.disabled = false;
    });
}

/**
 * @param {MouseEvent} mouse
 * @param {Track} track
 */
function openTrackMenu(mouse, track) {
    const entries = /** @type {AbstractMenuEntry[]} */ ([]);

    // Play now
    entries.push(new MenuEntry("play", gettext("Play now"), null, "p", () => queue.playNow(track)));

    // Add to queue
    entries.push(new MenuEntry("playlist-plus", gettext("Play next"), null, "n", () => queue.add(track, true, true)));
    entries.push(new MenuEntry("playlist-plus", gettext("Add to queue"), null, "q", () => queue.add(track, true)));

    // Edit
    if (track.isWritable()) {
        entries.push(new MenuSeparator());
        entries.push(new MenuEntry("pencil", gettext("Edit metadata"), gettext("Open metadata editor"), "e", () => {
            editor.open(track);
        }));
    }

    // Copy
    if (!vars.offlineMode && !track.isVirtual()) {
        entries.push(new MenuEntry("content-duplicate", gettext("Copy"), gettext("Copy this track to another playlist"), "c", () => {
            copyTrack = track;
            windows.open('window-copy');
        }));
    }

    // Share
    if (!vars.offlineMode) {
        entries.push(new MenuEntry("share", gettext("Share"), gettext("Create public share link"), "s", async () => {
            const response = await jsonPost('/share/create', { track: track.path });
            const json = await response.json();
            const absoluteShareUrl = new URL('/share/' + json.code, document.location.href).href;

            if (navigator.canShare) {
                const shareData = { url: absoluteShareUrl };
                if (navigator.canShare(shareData)) {
                    navigator.share(shareData);
                    return;
                } else {
                    console.warn('share: canShare == false');
                }
            } else {
                console.warn('share: Share API is not available');
            }

            window.open(absoluteShareUrl, '_blank');
        }));
    }

    // Report
    if (!vars.offlineMode) {
        entries.push(new MenuEntry("alert-circle", gettext("Report"), gettext("Report a problem with this track"), "r", async () => {
            await track.reportProblem();
            createToast('alert-circle', gettext("Problem reported"));
        }));
    }

    // Dislike
    if (!vars.offlineMode && !track.isVirtual()) {
        entries.push(new MenuSeparator());
        entries.push(new MenuEntry("thumb-down", gettext("Dislike"), gettext("Never play this track again"), "d", async () => {
            await track.dislike();
            if (queue.currentTrack && queue.currentTrack.path == track.path) {
                queue.next();
            }
        }));
    }

    // Delete
    if (track.isWritable()) {
        entries.push(new MenuEntry("delete", gettext("Delete"), gettext("Delete this track"), null, async () => {
            await track.delete();
            if (queue.currentTrack && queue.currentTrack.path == track.path) {
                queue.next();
            }
        }));
    }

    // Download
    entries.push(new MenuSeparator());
    if (!vars.offlineMode) {
        entries.push(new MenuEntry("download", gettext("Download as MP3"), null, null, () => {
            window.open(track.getAudioURL("mp3_with_metadata") + "&download=1", "_blank");
        }))
        entries.push(new MenuEntry("download", gettext("Download original file"), null, null, () => {
            window.open("/files/download?path=" + encodeURIComponent(track.path), "_blank");
        }))
    } else {
        // Offline mode only has one audio format
        entries.push(new MenuEntry("download", gettext("Download"), null, null, () => {
            window.open(track.getAudioURL(Setting.AUDIO_TYPE.value) + "&download=1", "_blank");
        }))
    }

    new ContextMenu(entries).open(mouse);
}

/**
 * @param {Track} track
 */
function getPrimaryLine(track) {
    const primary = document.createElement('div');

    if (track.title) {
        let first = true;
        for (const artist of track.artists) {
            if (first) {
                first = false;
            } else {
                primary.append(', ');
            }

            const artistHtml = document.createElement('a');
            artistHtml.textContent = artist;
            artistHtml.addEventListener("click", () => browse(new ArtistBrowse(new Artist({ "name": artist }))));
            primary.append(artistHtml);
        }

        if (track.artists.length > 0) {
            primary.append(' - ');
        }

        const titleHtml = document.createElement(track.isVirtual() ? 'span' : 'a');
        titleHtml.textContent = track.title;
        titleHtml.style.color = 'var(--text-color)';
        const title = track.title;
        if (!track.isVirtual()) {
            titleHtml.addEventListener("click", () => browse(new TitleBrowse(title)));
        }
        primary.append(titleHtml);
    } else {
        const span = document.createElement('span');
        span.style.color = "var(--text-color-warning)";
        span.textContent = track.path.substring(track.path.indexOf('/') + 1);
        primary.append(span);
    }

    const menuIcon = createIcon("dots-horizontal");
    menuIcon.classList.add("track-menu-icon");
    menuIcon.addEventListener("click", event => openTrackMenu(event, track));
    primary.append(menuIcon);

    return primary;
}

/**
 * @param {Track} track
 * @param {boolean} showPlaylist
 */
function getSecondaryLine(track, showPlaylist) {
    const secondary = document.createElement('div');
    secondary.classList.add('secondary');
    secondary.style.marginTop = 'var(--smallgap)';

    if (showPlaylist && !track.isVirtual()) {
        const playlistHtml = document.createElement('a');
        playlistHtml.addEventListener("click", () => browse(new PlaylistBrowse(track.playlist)));
        playlistHtml.textContent = track.playlistName;
        secondary.append(playlistHtml);
    }

    const year = track.year;
    const album = track.getAlbum();

    if (year || track.album) {
        if (showPlaylist && !track.isVirtual()) {
            secondary.append(', ');
        }

        if (album) {
            const albumHtml = document.createElement('a');
            albumHtml.addEventListener("click", () => browse(new AlbumBrowse(album)));
            if (album.artist) {
                albumHtml.textContent = album.artist + ' - ' + album.name;
            } else {
                albumHtml.textContent = album.name;
            }
            secondary.append(albumHtml);
            if (track.year) {
                secondary.append(', ');
            }
        }

        if (year) {
            const yearHtml = document.createElement('a');
            yearHtml.textContent = year + '';
            yearHtml.addEventListener('click', () => browse(new YearBrowse(year)));
            secondary.append(yearHtml);
        }
    }
    return secondary;
}

/**
 * Get display HTML for a track
 * @param {Track} track
 * @param {boolean} showPlaylist
 * @returns {HTMLSpanElement}
 */
export function trackDisplayHtml(track, showPlaylist = false) {
    const html = document.createElement('div');
    html.classList.add('track-display-text');

    html.addEventListener("contextmenu", event => {
        event.preventDefault();
        openTrackMenu(event, track);
    });

    const content = document.createElement("div");
    content.append(getPrimaryLine(track), getSecondaryLine(track, showPlaylist));
    html.append(content);

    return html;
}
