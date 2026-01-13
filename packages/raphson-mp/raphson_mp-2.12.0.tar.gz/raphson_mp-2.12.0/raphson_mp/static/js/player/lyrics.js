import { eventBus, MusicEvent } from "./event.js";
import { queue } from "./queue.js";
import { TimeSyncedLyrics, PlainLyrics, Lyrics } from "../api.js";
import { createToast, gettext, vars } from "../util.js";
import { setSettingChecked, Setting } from "./settings.js";
import { getPosition, seek } from "./audio.js";
import { ContextMenu, MenuEntry } from "../contextmenu.js";
import { editor } from "./editor.js";

class PlayerLyrics {
    #lyricsBox = /** @type {HTMLDivElement} */ (document.getElementById('lyrics-box'));
    #lyrics = /** @type {Lyrics | null} */ (null);
    #lastLine = /** @type {number | null} */ (null);
    #syncScroll = true;
    #syncScrollEnableTimer = 0;

    constructor() {
        // Updating synced lyrics is skipped when the page is not visible. Update immediately when it
        // does become visible, without smooth scrolling so the scroll is not noticeable.
        document.addEventListener('visibilitychange', () => this.#updateSyncedLyrics(false));

        // Handle lyrics setting being changed
        Setting.LYRICS.addEventListener('change', () => {
            this.#updateLyrics();
        });

        eventBus.subscribe(MusicEvent.TRACK_REPLACE, () => {
            this.#lyricsBox.scrollTo({ "top": 0 });
        });

        // Update lyrics when track changes
        eventBus.subscribe(MusicEvent.TRACK_CHANGE, () => {
            const track = queue.currentTrack;
            this.#setLyrics(track ? track.parsedLyrics : null);
        });

        // Continuously update synced lyrics
        eventBus.subscribe(MusicEvent.PLAYER_POSITION, () => requestAnimationFrame(() => this.#updateSyncedLyrics(true)));

        // Re-enable synced lyrics scrolling on seek
        eventBus.subscribe(MusicEvent.PLAYER_SEEK, () => {
            this.#syncScroll = true;
            requestAnimationFrame(() => this.#updateSyncedLyrics(true));
        });

        // Disable scrolling to current lyrics when the user scrolls manually
        this.#lyricsBox.addEventListener('wheel', () => this.#allowScrolling());
        this.#lyricsBox.addEventListener('touchmove', () => this.#allowScrolling());

        if (!vars.offlineMode) {
            const menu = new ContextMenu([
                new MenuEntry("reload", gettext("Search for new lyrics"), null, "n", () => this.#searchNewLyrics()),
                new MenuEntry("pencil", gettext("Edit lyrics"), null, "e", () => {
                    if (!queue.currentTrack) return;
                    editor.open(queue.currentTrack);
                    const lyricsField = /** @type {HTMLElement} */ (document.getElementById('editor-lyrics'));
                    lyricsField.focus();
                }),
            ]);
            menu.registerListener(this.#lyricsBox);
        }
    }

    toggleLyrics() {
        const checked = !Setting.LYRICS.checked;
        setSettingChecked(Setting.LYRICS, checked);
        if (checked) {
            createToast('text-box', gettext("Lyrics shown"), gettext("Lyrics hidden"));
        } else {
            createToast('text-box', gettext("Lyrics hidden"), gettext("Lyrics shown"));
        }
    }

    /**
     * @param {Lyrics | null} lyrics
     */
    #setLyrics(lyrics) {
        this.#lyrics = lyrics;
        this.#lastLine = null; // When lyrics change, current state is no longer accurate
        this.#updateLyrics();
    }

    #allowScrolling() {
        if (!this.#lyrics || !(this.#lyrics instanceof TimeSyncedLyrics)) {
            return;
        }

        console.debug('lyrics: disable sync scroll');
        this.#syncScroll = false;

        // re-enable sync in 10 seconds, as long as the user does not scroll again
        clearTimeout(this.#syncScrollEnableTimer);
        this.#syncScrollEnableTimer = setTimeout(() => {
            this.#syncScroll = true;
            console.debug('lyrics: re-enable sync scroll');
            this.#updateSyncedLyrics(true);
        }, 10_000);
    }

    /**
     * @param {boolean} smooth
     */
    #updateSyncedLyrics(smooth) {
        if (!this.#lyrics || !(this.#lyrics instanceof TimeSyncedLyrics)) return;

        if (document.visibilityState != 'visible') return;

        const position = getPosition();
        if (position == null) return;

        const currentLine = this.#lyrics.currentLine(position);

        // No need to cause an expensive DOM update if we're still at the same line
        if (currentLine == this.#lastLine) return;

        // Set color and scroll the right element into view
        let i = 0;
        for (const lineElem of this.#lyricsBox.children) {
            if (!(lineElem instanceof HTMLElement)) continue;
            if (i == currentLine) {
                lineElem.classList.remove('secondary-large');

                // Scroll parent so current line is centered
                if (this.#syncScroll) {
                    const totalHeight = this.#lyricsBox.getBoundingClientRect().height;
                    const lineHeight = lineElem.getBoundingClientRect().height;
                    const scrollTarget = Math.max(0, lineElem.offsetTop - totalHeight / 2 + lineHeight / 2);
                    this.#lyricsBox.scrollTo({ "top": scrollTarget, "behavior": smooth ? "smooth" : "instant" });
                }
            } else {
                lineElem.classList.add('secondary-large');
            }

            i++;
        }
    }

    async #searchNewLyrics() {
        if (!queue.currentTrack) throw new Error();

        createToast("loading", gettext("Searching for new lyrics"));

        if (await queue.currentTrack.searchLyrics()) {
            createToast("reload", gettext("Found new lyrics"), gettext("Searching for new lyrics"));
        } else {
            createToast("alert-circle", gettext("Could not find any new lyrics"), gettext("Searching for new lyrics"));
        }

        this.#lyrics = queue.currentTrack.parsedLyrics;
        this.#updateLyrics();
    }

    #updateLyrics() {
        clearTimeout(this.#syncScrollEnableTimer);

        if (!this.#lyrics || !Setting.LYRICS.checked) {
            this.#lyricsBox.hidden = true;
            return;
        }

        this.#lyricsBox.hidden = false;

        const newContent = [];

        if (this.#lyrics instanceof TimeSyncedLyrics) {
            for (const line of this.#lyrics.text) {
                const lineElem = document.createElement('span');
                lineElem.textContent = line.text;
                lineElem.append(document.createElement('br'));
                lineElem.addEventListener('click', () => seek(line.startTime));
                lineElem.style.cursor = 'pointer';
                newContent.push(lineElem);
            }

            this.#syncScroll = true;
        } else if (this.#lyrics instanceof PlainLyrics) {
            if (this.#lyrics.text == "[Instrumental]") {
                this.#lyricsBox.hidden = true;
            } else {
                const notTimeSyncedElem = document.createElement('span');
                notTimeSyncedElem.classList.add("secondary");
                notTimeSyncedElem.style.fontStyle = "oblique";
                notTimeSyncedElem.append(gettext("not time-synced"), document.createElement('br'));
                newContent.push(notTimeSyncedElem);

                const lyricsElem = document.createElement('span');
                lyricsElem.textContent = this.#lyrics.text;
                lyricsElem.style.whiteSpace = 'pre-line'; // render newlines
                newContent.push(lyricsElem);
            }
        }

        this.#lyricsBox.replaceChildren(...newContent);

        this.#updateSyncedLyrics(false);
    }
}

export const lyrics = new PlayerLyrics();
