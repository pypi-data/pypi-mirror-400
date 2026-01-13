import { eventBus, MusicEvent } from "./event.js";
import { trackDisplayHtml } from "./track.js";
import { queue } from "./queue.js";
import { clamp, durationToString, TRANSITION_DURATION, createToast, gettext, jsonPost, uuidv4, removeToast, vars } from "../util.js";
import { getImageQuality, setSettingChecked, setSettingValue, Setting } from "./settings.js";
import { getDuration, getPosition, isPaused, pause, play, seek, seekRelative } from "./audio.js";
import { AbstractMenuEntry, ContextMenu, MenuEntry, MenuSeparator } from "../contextmenu.js";
import { lyrics } from "./lyrics.js";

const SEEK_BAR = /** @type {HTMLDivElement} */ (document.getElementById('seek-bar'));
const POSITION_TEXT = /** @type {HTMLDivElement} */ (document.getElementById('seek-bar-text-position'));
const DURATION_TEXT = /** @type {HTMLDivElement} */ (document.getElementById('seek-bar-text-duration'));

/**
 * @returns {number} volume 0.0-1.0
 */
export function getVolume() {
    return parseInt(Setting.VOLUME.value) / 100.0;
}

/**
 * @param {number} volume volume 0.0-1.0
 */
export function setVolume(volume) {
    setSettingValue(Setting.VOLUME, clamp(Math.round(volume * 100), 0, 100) + '');
}

// Seek bar
{
    /**
     * @param {MouseEvent} event
     */
    function seekBarSeek(event) {
        const duration = getDuration();
        if (!duration) return;

        const seekbarBounds = SEEK_BAR.getBoundingClientRect();
        const relativePosition = (event.clientX - seekbarBounds.left) / seekbarBounds.width;
        if (relativePosition < 0 || relativePosition > 1) {
            // user has moved outside of seekbar, stop seeking
            document.removeEventListener('mousemove', onMove);
            return;
        }

        const newTime = relativePosition * duration;
        seek(newTime);
    }

    const onMove = (/** @type {MouseEvent} */ event) => {
        seekBarSeek(event);
        event.preventDefault(); // Prevent accidental text selection
    };

    const onUp = () => {
        document.removeEventListener('mousemove', onMove);
        document.removeEventListener('mouseup', onUp);
    };

    SEEK_BAR.addEventListener('mousedown', event => {
        seekBarSeek(event);

        // Keep updating while mouse is moving
        document.addEventListener('mousemove', onMove);

        // Unregister events on mouseup event
        document.addEventListener('mouseup', onUp);

        event.preventDefault(); // Prevent accidental text selection
    });

    // Scroll to seek
    SEEK_BAR.addEventListener('wheel', event => {
        seekRelative(event.deltaY < 0 ? 3 : -3);
    }, { passive: true });


    function updateSeekBar() {
        // Save resources updating seek bar if it's not visible
        if (document.visibilityState != 'visible') {
            return;
        }

        let barCurrent = "";
        let barDuration = "";
        let barWidth = 0;
        if (queue.currentTrack) {
            const position = getPosition();
            const duration = getDuration();

            if (position != null && duration != null) {
                barCurrent = durationToString(Math.round(position));
                barDuration = durationToString(Math.round(duration));
                barWidth = ((position / duration) * 100);
            } else {
                barCurrent = gettext("loading...");
            }
        }

        requestAnimationFrame(() => {
            POSITION_TEXT.textContent = barCurrent;
            DURATION_TEXT.textContent = barDuration;
            // Previously, the seek bar used an inner div with changing width. However, that causes an expensive
            // layout update. Instead, set a background gradient which is nearly free to update.
            SEEK_BAR.style.background = `linear-gradient(90deg, var(--seek-bar-color) ${barWidth}%, var(--background-color) 0%)`;
        });
    }
    eventBus.subscribe(MusicEvent.PLAYER_POSITION, updateSeekBar);
    eventBus.subscribe(MusicEvent.PLAYER_DURATION, updateSeekBar);
    eventBus.subscribe(MusicEvent.TRACK_REPLACE, updateSeekBar);

    // Seek bar is not updated when page is not visible. Immediately update it when the page does become visible.
    document.addEventListener('visibilitychange', updateSeekBar);
}

// Home button
{
    const homeButton = /** @type {HTMLButtonElement} */ (document.getElementById('button-home'));
    homeButton.addEventListener('click', () => window.open('/', '_blank'));
}

// Skip buttons
{
    const prevButton = /** @type {HTMLButtonElement} */ (document.getElementById('button-prev'));
    const nextButton = /** @type {HTMLButtonElement} */ (document.getElementById('button-next'));
    prevButton.addEventListener('click', () => queue.previous());
    nextButton.addEventListener('click', () => queue.next());
}

// Play pause buttons
{
    const pauseButton = /** @type {HTMLButtonElement} */ (document.getElementById('button-pause'));
    const playButton = /** @type {HTMLButtonElement} */ (document.getElementById('button-play'));

    // Play pause click actions
    pauseButton.addEventListener('click', () => pause());
    playButton.addEventListener('click', () => play());

    const updateButtons = () => {
        requestAnimationFrame(() => {
            pauseButton.hidden = isPaused();
            playButton.hidden = !isPaused();
        });
    };

    eventBus.subscribe(MusicEvent.PLAYER_PLAY, updateButtons);
    eventBus.subscribe(MusicEvent.PLAYER_PAUSE, updateButtons);

    // Hide pause button on initial page load, otherwise both play and pause will show
    pauseButton.hidden = true;
}

// Volume slider
{
    function updateVolumeIcon() {
        const volume = parseInt(Setting.VOLUME.value);
        requestAnimationFrame(() => {
            Setting.VOLUME.classList.remove('input-volume-high', 'input-volume-medium', 'input-volume-low');
            if (volume > 60) {
                Setting.VOLUME.classList.add('input-volume-high');
            } else if (volume > 30) {
                Setting.VOLUME.classList.add('input-volume-medium');
            } else {
                Setting.VOLUME.classList.add('input-volume-low');
            }
        });
    }

    // Unfocus after use so arrow hotkeys still work for switching tracks
    Setting.VOLUME.addEventListener('mouseup', () => Setting.VOLUME.blur());

    // Respond to volume button changes
    // Event fired when input value changes, also manually when code changes the value
    Setting.VOLUME.addEventListener('change', () => updateVolumeIcon());
    // Also respond to input event, so volume changes immediately while user is dragging slider
    Setting.VOLUME.addEventListener('input', () => Setting.VOLUME.dispatchEvent(new Event('change')));
    // Set icon on page load
    updateVolumeIcon();

    // Scroll to change volume
    Setting.VOLUME.addEventListener('wheel', event => {
        setVolume(getVolume() + (event.deltaY < 0 ? 0.05 : -0.05));
    }, { passive: true });
}

// Album images
{
    const coverBox = /** @type {HTMLDivElement} */ (document.getElementById("album-cover-box"));
    const bgBottom = /** @type {HTMLDivElement} */ (document.getElementById('bg-image-1'));
    const bgTop = /** @type {HTMLDivElement} */ (document.getElementById('bg-image-2'));
    const fgBottom = /** @type {HTMLDivElement} */ (document.getElementById('album-cover-1'));
    const fgTop = /** @type {HTMLDivElement} */ (document.getElementById('album-cover-2'));

    /**
     * @param {string} imageUrl
     */
    function setAlbumImages(imageUrl) {
        const cssUrl = `url("${imageUrl}")`;

        if (Setting.LITE_MODE.checked) {
            bgTop.style.backgroundImage = cssUrl;
            fgTop.style.backgroundImage = cssUrl;
            bgBottom.style.backgroundImage = "";
            fgBottom.style.backgroundImage = "";
            return;
        }

        // Set bottom to new image
        bgBottom.style.backgroundImage = cssUrl;
        fgBottom.style.backgroundImage = cssUrl;

        // Slowly fade out old top image
        bgTop.style.opacity = '0';
        fgTop.style.opacity = '0';

        setTimeout(() => {
            // To prepare for next replacement, move bottom image to top image
            bgTop.style.backgroundImage = cssUrl;
            fgTop.style.backgroundImage = cssUrl;
            // Make it visible
            bgTop.style.opacity = '1';
            fgTop.style.opacity = '1';
        }, TRANSITION_DURATION);
    }

    function setAlbumImagesCurrent() {
        if (!queue.currentTrack) return;
        const track = queue.currentTrack;
        const imageUrl = track.getCoverURL(getImageQuality(), Setting.MEME_MODE.checked);
        setAlbumImages(imageUrl);
    }

    // Update album cover when track is changed
    eventBus.subscribe(MusicEvent.TRACK_CHANGE, setAlbumImagesCurrent);
    // Update album cover when meme mode is enabled or disabled
    Setting.MEME_MODE.addEventListener('change', setAlbumImagesCurrent);
    // Update album cover when quality is changed
    Setting.AUDIO_TYPE.addEventListener('change', setAlbumImagesCurrent);

    const entries = /** @type {AbstractMenuEntry[]} */ ([]);
    if (!vars.offlineMode) {
        entries.push(new MenuEntry("reload", gettext("Search for new album cover"), null, "n", async () => {
            if (!queue.currentTrack) return;
            createToast("loading", gettext("Looking for new album cover image"));
            await jsonPost(`/track/${encodeURIComponent(queue.currentTrack.path)}/delete_cached_cover`, {meme: Setting.MEME_MODE.checked});
            const imageUrl = queue.currentTrack.getCoverURL(getImageQuality(), Setting.MEME_MODE.checked);
            setAlbumImages(imageUrl + "&cacheBust=" + uuidv4());
            removeToast(gettext("Looking for new album cover image"));
        }));
    }

    entries.push(new MenuEntry("fullscreen", gettext("Open album cover in new tab"), null, "o", () => {
        if (!queue.currentTrack) return;
        window.open(queue.currentTrack.getCoverURL("high", Setting.MEME_MODE.checked), "_blank");
    }));

    entries.push(new MenuEntry("text-box", gettext("Toggle lyrics"), null, "l", () => lyrics.toggleLyrics()))

    entries.push(new MenuEntry("chart-bar", gettext("Toggle visualiser"), null, "v", () => setSettingChecked(Setting.VISUALISER, !Setting.VISUALISER.checked)));

    if (!vars.offlineMode) {
        new MenuEntry("emoticon", gettext("Toggle meme mode"), null, "m", () => setSettingChecked(Setting.MEME_MODE, !Setting.MEME_MODE.checked));
    }

    const menu = new ContextMenu(entries);
    menu.registerListener(coverBox);
}

// Current track info
{
    eventBus.subscribe(MusicEvent.TRACK_CHANGE, () => {
        if (!queue.currentTrack) throw new Error();
        const track = queue.currentTrack;
        const currentTrackElem = /** @type {HTMLSpanElement} */ (document.getElementById('current-track'));
        currentTrackElem.replaceChildren(trackDisplayHtml(track, true));
        document.title = track.displayText();
    });
}
