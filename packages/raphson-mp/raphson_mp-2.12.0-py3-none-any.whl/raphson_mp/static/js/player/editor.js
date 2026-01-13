import { windows } from "./window.js";
import { eventBus, MusicEvent } from "./event.js";
import { Track } from "../api.js";
import { createToast, gettext } from "../util.js";
import { ContextMenu, MenuEntry } from "../contextmenu.js";

const SAVE_BUTTON = /** @type {HTMLButtonElement} */ (document.getElementById("editor-save"));
const LOOKUP_BUTTON = /** @type {HTMLButtonElement} */ (document.getElementById("editor-lookup"));
const LOOKUP_NO_RESULT = /** @type {HTMLTableElement} */ (document.getElementById("editor-lookup-no-result"));
const LOOKUP_RESULT_CONTAINER = /** @type {HTMLTableElement} */ (document.getElementById("editor-lookup-result"));
const LOOKUP_RESULT_ACOUSTID = /** @type {HTMLAnchorElement} */ (document.getElementById("editor-lookup-acoustid"));
const LOOKUP_RESULT_TABLE = /** @type {HTMLTableSectionElement} */ (document.getElementById("editor-lookup-tbody"));
const WRITING = /** @type {HTMLParagraphElement} */ (document.getElementById('editor-writing'));

const PATH = /** @type {HTMLInputElement} */ (document.getElementById('editor-path'));
const TITLE = /** @type {HTMLInputElement} */ (document.getElementById('editor-title'));
const ALBUM = /** @type {HTMLInputElement} */ (document.getElementById('editor-album'));
const ARTISTS = /** @type {HTMLInputElement} */ (document.getElementById('editor-artists'));
const ALBUM_ARTIST = /** @type {HTMLInputElement} */ (document.getElementById('editor-album-artist'));
const TAGS = /** @type {HTMLInputElement} */ (document.getElementById('editor-tags'));
const YEAR = /** @type {HTMLInputElement} */ (document.getElementById('editor-year'));
const NUMBER = /** @type {HTMLInputElement} */ (document.getElementById('editor-number'));
const LYRICS = /** @type {HTMLTextAreaElement} */ (document.getElementById('editor-lyrics'));

class Editor {
    #track = /** @type {Track | null} */ (null);

    constructor() {
        SAVE_BUTTON.addEventListener('click', () => this.#save());
        LOOKUP_BUTTON.addEventListener('click', () => this.#auto());

        document.addEventListener('keydown', event => {
            if (event.ctrlKey && event.key == "Enter" && windows.isOpen('window-editor')) {
                this.#save();
            }
        });

        // Artist menu
        new ContextMenu([
            new MenuEntry("auto-fix", gettext("Auto split artist"), null, null, () => {
                ARTISTS.value = ARTISTS.value.split(",").join(";").split("&").join(";");
            })
        ]).registerListener(ARTISTS);

        // Album artist menu
        new ContextMenu([
            new MenuEntry("auto-fix", gettext("Copy first artist"), null, null, () => {
                ALBUM_ARTIST.value = ARTISTS.value.split(";")[0];
            }),
            new MenuEntry("auto-fix", gettext("Copy second artist"), null, null, () => {
                ALBUM_ARTIST.value = ARTISTS.value.split(";")[1];
            }),
        ]).registerListener(ALBUM_ARTIST);
    };

    /**
     * Populate input fields and show metadata editor window
     * @param {Track} track
     */
    open(track) {
        if (track == null) {
            throw new Error('Track is null');
        }
        this.#track = track;
        this.#trackToHtml();

        LOOKUP_NO_RESULT.hidden = true;
        LOOKUP_RESULT_CONTAINER.hidden = true;
        LOOKUP_BUTTON.hidden = false;

        // Make editor window window visible, and bring it to the top
        windows.open('window-editor');
    };

    /**
     * @param {HTMLInputElement | HTMLTextAreaElement} elem
     * @returns {string | null} Value of HTML input with the given id.
     */
    #getValue(elem) {
        const value = elem.value.trim();
        return value === '' ? null : value;
    };

    /**
     * @param {HTMLInputElement | HTMLTextAreaElement} elem
     * @returns {Array<string>}
     */
    #getValues(elem) {
        return elem.value.split(";").map(s => s.trim()).filter(s => s.length > 0);
    }

    /**
     * @param {HTMLInputElement | HTMLTextAreaElement} elem
     * @param {string | null} value
     */
    #setValue(elem, value) {
        elem.value = value ? value : "";
    }

    /**
     *
     * @param {HTMLInputElement | HTMLTextAreaElement} elem
     * @param {Array<string>} values
     */
    #setValues(elem, values) {
        elem.value = values.join("; ");
    }

    /**
     * Copy content from track object variables to HTML input fields
     */
    #trackToHtml() {
        if (!this.#track) {
            throw new Error();
        }
        this.#setValue(PATH, this.#track.path);
        this.#setValue(TITLE, this.#track.title);
        this.#setValue(ALBUM, this.#track.album);
        this.#setValues(ARTISTS, this.#track.artists);
        this.#setValue(ALBUM_ARTIST, this.#track.albumArtist);
        this.#setValues(TAGS, this.#track.tags);
        this.#setValue(YEAR, this.#track.year ? this.#track.year + '' : null);
        this.#setValue(NUMBER, this.#track.trackNumber ? this.#track.trackNumber + '' : null);
        this.#setValue(LYRICS, this.#track.lyrics);
    }

    /**
     * Copy content from input fields to track object
     */
    #htmlToTrack() {
        if (!this.#track) {
            throw new Error();
        }
        this.#track.title = this.#getValue(TITLE);
        this.#track.album = this.#getValue(ALBUM);
        this.#track.artists = this.#getValues(ARTISTS);
        this.#track.albumArtist = this.#getValue(ALBUM_ARTIST);
        this.#track.tags = this.#getValues(TAGS);
        const yearStr = this.#getValue(YEAR);
        this.#track.year = yearStr ? parseInt(yearStr) : null;
        const numberStr = this.#getValue(NUMBER);
        this.#track.trackNumber = numberStr ? parseInt(numberStr) : null;
        this.#track.lyrics = this.#getValue(LYRICS);
    }

    /**
     * Save metadata and close metadata editor window
     */
    async #save() {
        if (this.#track == null) {
            throw new Error();
        }
        this.#htmlToTrack();

        // Loading text
        SAVE_BUTTON.hidden = true;
        WRITING.hidden = false;

        // Make request to update metadata
        try {
            await this.#track.saveMetadata();
        } catch (e) {
            alert('An error occurred while updating metadata.');
            return;
        } finally {
            WRITING.hidden = true;
            SAVE_BUTTON.hidden = false;
        }

        // Close window, and restore save button
        windows.closeTop();

        // Music player should update all track-related HTML with new metadata. This event must be
        // fired after the editor window is closed, so other windows can check whether they are open.
        eventBus.publish(MusicEvent.METADATA_CHANGE, this.#track);

        this.#track = null;
    };

    async #auto() {
        if (!this.#track) {
            throw new Error();
        }

        LOOKUP_BUTTON.hidden = true;
        LOOKUP_RESULT_CONTAINER.hidden = true;
        LOOKUP_NO_RESULT.hidden = true;

        try {
            const result = await this.#track.acoustid();

            if (!result) {
                LOOKUP_NO_RESULT.hidden = false;
                return;
            }

            const rows = [];
            for (const release of result.releases) {
                const tdTitle = document.createElement('td');
                tdTitle.textContent = release.title;
                const tdArtist = document.createElement('td');
                tdArtist.textContent = release.artists.join(', ');
                const tdAlbum = document.createElement('td');
                tdAlbum.textContent = release.album;
                const tdYear = document.createElement('td');
                tdYear.textContent = release.year + '';
                const tdType = document.createElement('td');
                tdType.textContent = release.release_type;
                const tdPackaging = document.createElement('td');
                tdPackaging.textContent = release.packaging;
                const row = document.createElement('tr');
                row.append(tdTitle, tdArtist, tdAlbum, tdYear, tdType, tdPackaging);

                // Click a row to auto fill metadata
                row.style.cursor = 'pointer';
                row.addEventListener('click', () => {
                    this.#setValue(TITLE, release.title);
                    this.#setValues(ARTISTS, release.artists);
                    this.#setValue(ALBUM, release.album);
                    this.#setValue(ALBUM_ARTIST, release.album_artist);
                    this.#setValue(YEAR, release.year + '');
                });

                rows.push(row);
            }

            LOOKUP_RESULT_TABLE.replaceChildren(...rows);
            LOOKUP_RESULT_ACOUSTID.href = 'https://acoustid.org/track/' + result.acoustid;
            LOOKUP_RESULT_CONTAINER.hidden = false;
        } catch (ex) {
            createToast('close', gettext("Could not fingerprint audio file, maybe it is corrupt?"));
            console.warn(ex);
        } finally {
            LOOKUP_BUTTON.hidden = false;
        }
    }

};

export const editor = new Editor();
