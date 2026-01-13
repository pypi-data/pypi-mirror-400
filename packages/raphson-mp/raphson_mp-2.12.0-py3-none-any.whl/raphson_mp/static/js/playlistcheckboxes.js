import { music, Playlist } from "./api.js";
import { registerHotKeyListener, uuidv4 } from "./util.js";

class PlaylistToggleEvent {
    playlist;
    state;
    /**
     * @param {string} playlist
     * @param {boolean} state
     */
    constructor(playlist, state) {
        this.playlist = playlist;
        this.state = state;
    }
}

export class PlaylistCheckboxes {
    #parentElement;
    #save = true;
    #onChange = /** @type {((event: PlaylistToggleEvent) => void)[]} */ ([]);

    /**
     * @param {HTMLDivElement} parentElement
     */
    constructor(parentElement) {
        this.#parentElement = parentElement;

        registerHotKeyListener(key => {
            const keyInt = parseInt(key);
            if (isNaN(keyInt) || keyInt == 0) {
                return;
            }

            console.debug('playlistcheckboxes: toggle playlist', keyInt);

            const checkboxes = parentElement.getElementsByTagName('div')[0].getElementsByTagName('input');
            if (keyInt <= checkboxes.length) {
                // Toggle checkbox
                const checkbox = checkboxes[keyInt - 1];
                checkbox.checked = !checkbox.checked;
                this.#fireChangeEvent(checkbox);
                this.#savePlaylistState();
            }
        });
    }

    disableSaving() {
        this.#save = false;
    }

    /**
     * @returns {Array<string>} list of playlist names
     */
    getActivePlaylists() {
        const active = [];
        for (const checkbox of this.#parentElement.getElementsByTagName('input')) {
            if (!checkbox.checked) {
                continue;
            }

            const playlist = checkbox.dataset.playlist;
            if (!playlist) throw new Error();

            active.push(playlist);
        }

        return active;
    }

    /**
     * @param {Array<string>} playlists
     */
    setActivePlaylists(playlists, fireEvents = true) {
        for (const checkbox of this.#parentElement.getElementsByTagName('input')) {
            const playlist = checkbox.dataset.playlist;
            if (!playlist) throw new Error();

            const isChecked = checkbox.checked;
            const shouldBeChecked = playlists.includes(playlist);
            if (isChecked != shouldBeChecked) {
                checkbox.checked = shouldBeChecked;
                if (fireEvents) {
                    this.#fireChangeEvent(checkbox);
                }
            }
        }
    }

    /**
     * @param {(event: PlaylistToggleEvent) => void} callback
     */
    registerPlaylistToggleListener(callback) {
        this.#onChange.push(callback);
    }

    /**
     * @param {HTMLInputElement} checkbox
     */
    #fireChangeEvent(checkbox) {
        const event = new PlaylistToggleEvent(/** @type {string} */ (checkbox.dataset.playlist), checkbox.checked);
        for (const callback of this.#onChange) {
            callback(event);
        }
    }

    /**
     * Update checked state of playlist checkboxes from local storage
     * @returns {void}
     */
    #loadPlaylistState() {
        if (!this.#save) {
            console.debug('playlist: not loading checkbox state');
            return;
        }
        const playlistsString = localStorage.getItem('playlists');
        if (!playlistsString) {
            console.info('playlist: no state saved');
            return;
        }
        /** @type {Array<string>} */
        const playlists = JSON.parse(playlistsString);
        console.debug('playlist: restoring state', playlists);
        this.setActivePlaylists(playlists, false);
    }

    /**
     * Save state of playlist checkboxes to local storage
     * @returns {void}
     */
    #savePlaylistState() {
        if (!this.#save) {
            console.debug('playlist: not saving checkbox state');
            return;
        }
        const playlists = this.getActivePlaylists();
        console.debug('playlist: saving checkbox state', playlists);
        localStorage.setItem('playlists', JSON.stringify(playlists));
    }

    /**
     * @param {Playlist} playlist Playlist
     * @param {number} index Hotkey number, set to >=10 to not assign a hotkey
     * @param {boolean} defaultChecked Whether checkbox should be checked
     * @returns {HTMLSpanElement}
     */
    #createPlaylistCheckbox(playlist, index, defaultChecked) {
        const id = uuidv4();;
        const label = document.createElement("label");
        label.htmlFor = id;

        const input = document.createElement("input");
        input.type = 'checkbox';
        input.dataset.playlist = playlist.name;
        input.id = id;
        input.checked = defaultChecked;
        label.append(input);

        const text = document.createElement('div');
        text.textContent = playlist.name;
        label.append(text);

        if (index < 10) { // Assume number keys higher than 9 don't exist
            const sup = document.createElement('sup');
            sup.textContent = index + '';
            text.append(sup);
        }

        const trackCount = document.createElement('span');
        trackCount.classList.add('secondary');
        trackCount.textContent = ' ' + playlist.trackCount;
        label.append(trackCount);

        return label;
    }

    createPlaylistCheckboxes() {
        const mainDiv = document.createElement('div');
        const otherDiv = document.createElement('div');
        mainDiv.classList.add('playlist-checkbox-row');
        otherDiv.classList.add('playlist-checkbox-row');

        let index = 1;
        for (const playlist of music.playlists()) {
            if (playlist.trackCount == 0) {
                continue;
            }

            if (playlist.favorite) {
                mainDiv.appendChild(this.#createPlaylistCheckbox(playlist, index++, true));
            } else {
                otherDiv.appendChild(this.#createPlaylistCheckbox(playlist, 10, false));
            }
        }

        this.#parentElement.replaceChildren(mainDiv, otherDiv);

        for (const input of this.#parentElement.getElementsByTagName('input')) {
            input.addEventListener('input', () => {
                this.#fireChangeEvent(input);
                this.#savePlaylistState();
            });
        }

        // load checked/unchecked state from local storage
        this.#loadPlaylistState();
    }
}
