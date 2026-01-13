import { eventBus, MusicEvent } from "./event.js";
import { choice, durationToString, createToast, createIconButton, gettext, jsonPost, sendErrorReport, vars, withLock } from "../util.js";
import { music, Track, controlChannel, ControlCommand } from "../api.js";
import { getTagFilter } from "./tag.js";
import { getImageQuality, Setting } from "./settings.js";
import { trackDisplayHtml } from "./track.js";
import { playerSync } from "./sync.js";
import { getIntersectPlaylists, playlistCheckboxes } from "./playlists.js";
import { getPosition, seek } from "./audio.js";

export const MAX_HISTORY_SIZE = 25;

/**
 * @param {string | null} currentPlaylist current playlist name
 * @returns {string | null} next playlist name
 */
function getNextPlaylist(currentPlaylist) {
    const playlists = playlistCheckboxes.getActivePlaylists();

    let playlist;

    if (playlists.length === 0) {
        // No one is selected
        console.warn('playlist: no playlists active');
        return null;
    } else if (currentPlaylist === null) {
        // No playlist chosen yet, choose random playlist
        playlist = choice(playlists);
    } else {
        const currentIndex = playlists.indexOf(currentPlaylist);
        if (currentIndex === -1) {
            // Current playlist is no longer active, we don't know the logical next playlist
            // Choose random playlist
            playlist = choice(playlists);
        } else {
            // Choose next playlist in list, wrapping around if at the end
            playlist = playlists[(currentIndex + 1) % playlists.length];
        }
    }

    return playlist;
}

export class QueuedTrack {
    track;
    manual;
    audioElem = /** @type {HTMLAudioElement | null} */ (null);

    /**
     * @param {Track} track
     * @param {boolean} manual
     */
    constructor(track, manual) {
        this.track = track;
        this.manual = manual;

        if (vars.offlineMode) {
            // No need to cache in case of network disruptions when we function offline
            this.audioElem = null;
        } else {
            // Use dummy audio element to keep audio cached
            // Load a bit later, to give priority to the loading of other assets
            setTimeout(() => {
                this.audioElem = document.createElement('audio');
                this.audioElem.src = track.getAudioURL(Setting.AUDIO_TYPE.value);
                this.audioElem.preload = 'auto';
            }, 5000);
        }
    }
}

class Queue {
    #htmlCurrentQueueSize = /** @type {HTMLSpanElement} */ (document.getElementById("current-queue-size"));
    #htmlQueue = /** @type {HTMLTableElement} */ (document.getElementById("queue"));
    #htmlQueueBox = /** @type {HTMLTableElement} */ (document.getElementById("box-queue"));
    #previousPlaylist = /** @type {string|null} */ (null);
    previousTracks = /** @type {Array<Track>} */ ([]);
    queuedTracks = /** @type {Array<QueuedTrack>} */ ([]);
    currentTrack = /** @type {Track|null} */ (null);
    #fillDelay = 0;

    constructor() {
        eventBus.subscribe(MusicEvent.METADATA_CHANGE, (/** @type {Track} */ updatedTrack) => {
            // Current track
            if (this.currentTrack != null && this.currentTrack.path == updatedTrack.path) {
                this.currentTrack = updatedTrack;
                console.debug('queue: updating current track following a METADATA_CHANGE event', updatedTrack.path);
                eventBus.publish(MusicEvent.TRACK_CHANGE);
            }

            // Queue
            let queueChanged = false;
            for (const queuedTrack of this.queuedTracks) {
                if (queuedTrack.track.path == updatedTrack.path) {
                    console.debug('queue: updating track in queue following a METADATA_CHANGE event', updatedTrack.path);
                    queuedTrack.track = updatedTrack;
                    queueChanged = true;
                }
            }
            if (queueChanged) {
                eventBus.publish(MusicEvent.QUEUE_CHANGE);
            }

            // Previous tracks
            for (let i = 0; i < this.previousTracks.length; i++) {
                if (this.previousTracks[i].path == updatedTrack.path) {
                    this.previousTracks[i] = updatedTrack;
                }
            }
        });

        // When playlist checkboxes are loaded, fill queue
        playlistCheckboxes.registerPlaylistToggleListener(() => this.fill());

        // Clear queue button
        const clearButton = /** @type {HTMLButtonElement} */ (document.getElementById('queue-clear'));
        clearButton.addEventListener('click', () => this.clear());

        eventBus.subscribe(MusicEvent.QUEUE_CHANGE, () => {
            this.#updateHtml();
            this.fill();
        });

        // Fill queue when size is changed
        Setting.QUEUE_SIZE.addEventListener('change', () => this.fill());

        // Update album covers when meme mode is changed (setTimeout to let currently playing cover update first)
        Setting.MEME_MODE.addEventListener('change', () => setTimeout(() => this.#updateHtml(), 100));
        // Remove icon changes based on this setting
        Setting.QUEUE_REMOVE_REPLACE.addEventListener('change', () => this.#updateHtml());
        // Update quality of tracks preloaded in queue
        Setting.AUDIO_TYPE.addEventListener('change', () => {
            for (const track of this.queuedTracks) {
                if (!track.audioElem) continue;
                track.audioElem.src = track.track.getAudioURL(Setting.AUDIO_TYPE.value);
            }
            // Also update quality of images in queue
            this.#updateHtml();
        });

        // Save player state periodically and when closed
        setInterval(() => this.#saveState(), 60000);
        window.addEventListener("pagehide", () => this.#saveState());
    };

    /**
     * Play given track immediately
     * @param {Track} track
     */
    playNow(track) {
        if (playerSync.playerId != null) {
            // delegate to other player
            controlChannel.sendMessage(ControlCommand.CLIENT_SET_PLAYING, {"player_id": playerSync.playerId, 'track': track.toJson()});
        }

        // Add current track to history
        if (this.currentTrack !== null) {
            this.previousTracks.push(this.currentTrack);
            // If history exceeded maximum length, remove first (oldest) element
            if (this.previousTracks.length > MAX_HISTORY_SIZE) {
                this.previousTracks.shift();
            }
            eventBus.publish(MusicEvent.QUEUE_CHANGE);
        }

        // Replace current track with given track
        this.currentTrack = track;
        eventBus.publish(MusicEvent.TRACK_REPLACE);
    }

    /**
     * the supplied modifyFunction must make a clone of the queue!
     * @param {(tracks: Array<QueuedTrack>) => Array<QueuedTrack> | null} modifyFunction
     */
    modifyQueue(modifyFunction) {
        const newQueue = modifyFunction(this.queuedTracks);
        if (newQueue == null) {
            // not modified
            return;
        }

        if (playerSync.playerId != null) {
            // delegate to other player
            controlChannel.sendMessage(ControlCommand.CLIENT_SET_QUEUE, {
                player_id: playerSync.playerId,
                tracks: newQueue.map(queuedTrack => { return {manual: queuedTrack.manual, track: queuedTrack.track.toJson() }; }),
            });
        } else {
            // modify our queue directly
            this.queuedTracks = newQueue;
            eventBus.publish(MusicEvent.QUEUE_CHANGE);
        }
    }

    /**
     * Add track to queue
     * @param {Track} track
     * @param {boolean} manual True if this track is added manually by the user
     * @param {boolean} top True to add track to top of queue, e.g. for news
     */
    add(track, manual, top = false) {
        this.modifyQueue(tracks => {
            const newTrack = new QueuedTrack(track, manual);
            if (top) {
                // add to top
                return [newTrack, ...tracks];
            }

            if (manual) {
                // are there already manually added tracks?
                if (tracks.some(track => track.manual)) {
                    // add after last manually added track
                    const i = tracks.map(track => track.manual).lastIndexOf(true);
                    return tracks.toSpliced(i + 1, 0, newTrack);
                } else {
                    // add to top
                    return [newTrack, ...tracks];
                }
            }

            // add to end of queue
            return [...tracks, newTrack];
        });
    };

    /**
     * @param {number} index
     */
    async remove(index) {
        const track = this.queuedTracks[index];

        const replacements = /** @type {QueuedTrack[]} */ ([]);

        if (!track.manual && Setting.QUEUE_REMOVE_REPLACE.checked) {
            // Replace the track with a new track from the same playlist
            const playlist = track.track.playlist;
            const replacementTrack = await playlist.chooseRandomTrack(false, getTagFilter(), getIntersectPlaylists(playlist.name));
            if (replacementTrack) {
                replacements.push(new QueuedTrack(replacementTrack, false));
            }
        }

        this.modifyQueue(tracks => {
            return tracks.toSpliced(index, 1, ...replacements);
        });
    };

    /**
     * Remove all items from queue
     */
    clear() {
        this.modifyQueue(tracks => {
            // keep only manually added tracks
            return tracks.filter(track => track.manual);
        });
        createToast('playlist-remove', gettext("Queue cleared"));
    }

    #getMinimumSize() {
        let minQueueSize = parseInt(Setting.QUEUE_SIZE.value);
        return isFinite(minQueueSize) ? minQueueSize : 1;
    }

    fill() {
        if (playerSync.playerId != null) {
            // filling the queue is handled by other player
            return;
        }

        withLock("queue_fill", async () => {
            if (this.queuedTracks.length >= this.#getMinimumSize()) {
                console.debug('queue: full');
                return;
            }

            console.debug('queue: fill');

            try {
                const playlistName = getNextPlaylist(this.#previousPlaylist);
                console.debug(`queue: round robin: ${this.#previousPlaylist} -> ${playlistName}`);
                this.#previousPlaylist = playlistName;

                if (playlistName == null) {
                    // No playlists are active. fill() will be called again when a playlist is enabled.
                    return;
                }

                const playlist = music.playlist(playlistName);
                const track = await playlist.chooseRandomTrack(false, getTagFilter(), getIntersectPlaylists(playlistName));
                if (track != null) {
                    this.add(track, false);

                    // start next track if there is no current track playing (most likely when the page has just loaded)
                    if (this.currentTrack == null) {
                        console.info('queue: no current track, call next()');
                        this.next();
                    }

                    // track added successfully -- reset fill delay
                    this.#fillDelay = 0;
                }
            } catch (error) {
                console.warn('queue:', error);
                console.warn('queue: retry fill in', Math.round(this.#fillDelay / 1000), 'seconds');
            }

            if (this.#fillDelay < 30000) {
                this.#fillDelay += 1000;
            }
            setTimeout(() => this.fill(), this.#fillDelay);
        });
    };

    /**
     * Update queue HTML, if #queueChanged is true
     */
    #updateHtml() {
        const rows = /** @type {Array<HTMLElement>} */ ([]);
        let i = 0;
        let totalQueueDuration = 0;
        for (const queuedTrack of this.queuedTracks) {
            const rememberI = i++;

            const track = queuedTrack.track;

            if (track instanceof Track) {
                totalQueueDuration += track.duration;
            }

            const imageUrl = queuedTrack.track.getCoverURL(getImageQuality(), Setting.MEME_MODE.checked);

            const coverDiv = document.createElement("div");
            coverDiv.classList.add("box", "queue-cover");
            coverDiv.style.backgroundImage = `url("${imageUrl}")`;

            // Track title HTML
            const trackDiv = trackDisplayHtml(track, true);

            const deleteIcon = !queuedTrack.manual && Setting.QUEUE_REMOVE_REPLACE.checked ? "reload" : "close";
            const deleteElem = createIconButton(deleteIcon, gettext("Remove from queue"));
            deleteElem.classList.add('queue-remove-item');
            deleteElem.onclick = () => queue.remove(rememberI);

            // Add columns to <tr> row and add the row to the table
            const row = document.createElement('div');
            row.classList.add('queue-item', 'flex-vcenter');
            row.dataset.queuePos = rememberI + '';
            row.append(coverDiv, trackDiv, deleteElem);

            rows.push(row);
        }

        this.#htmlCurrentQueueSize.textContent = durationToString(totalQueueDuration);

        // Add events to <tr> elements
        queue.#dragDropTable(rows);

        this.#htmlQueue.replaceChildren(...rows);
    };

    // Based on https://code-boxx.com/drag-drop-sortable-list-javascript/
    /**
     * @param {Array<HTMLElement>} rows
     */
    #dragDropTable(rows) {
        function createLine() {
            const line = document.createElement('div');
            line.style.background = 'var(--background-color-active)';
            line.style.height = '2px';
            line.style.width = '100%';
            return line;
        }

        let current = /** @type {HTMLElement | null} */ (null); // Element that is being dragged
        let line = /** @type {HTMLElement | null} */ (null);

        const determinePosition = (/** @type {number} */ currentPos, /** @type {MouseEvent} */ event) => {
            let targetPos = rows.length - 1;

            for (let i = 0; i < rows.length; i++) {
                const row = rows[i];
                const rect = row.getBoundingClientRect();
                if (currentPos >= i && event.clientY < rect.y + rect.height / 2) {
                    targetPos = i;
                    break;
                } else if (currentPos < i && event.clientY < rect.y + rect.height / 2 + rect.height) {
                    targetPos = i;
                    break;
                }
            }
            console.debug('queue: drop: move from', currentPos, 'to', targetPos);
            return targetPos;
        };

        this.#htmlQueueBox.addEventListener('dragover', event => {
            event.preventDefault();

            if (current == null) {
                return;
            }

            if (line != null) {
                line.remove();
            }

            const currentPos = parseInt(/** @type {string} */(current.dataset.queuePos));
            const targetPos = determinePosition(currentPos, event);

            if (targetPos < currentPos) {
                rows[targetPos].before(line = createLine());
            } else if (targetPos > currentPos) {
                rows[targetPos].after(line = createLine());
            }
        });

        this.#htmlQueueBox.addEventListener('drop', event => {
            event.preventDefault();

            if (current == null) {
                return;
            }

            const currentPos = parseInt(/** @type {string} */(current.dataset.queuePos));
            const targetPos = determinePosition(currentPos, event);

            this.modifyQueue(tracks => {
                const tracksCopy = [...tracks];
                // Remove current (being dragged) track from queue
                const track = tracksCopy.splice(currentPos, 1)[0];
                // Add it to the place it was dropped
                tracksCopy.splice(targetPos, 0, track);
                return tracksCopy;
            });

            current = null;
        });

        for (let row of rows) {
            row.draggable = true; // Make draggable

            row.ondragstart = () => {
                current = row;
            };
        };
    };

    previous() {
        if (playerSync.playerId != null) {
            // Delegate action to remote player
            controlChannel.sendMessage(ControlCommand.CLIENT_PREVIOUS, { "player_id": playerSync.playerId });
            return;
        }

        if (!this.currentTrack) {
            return;
        }

        const previousTrack = this.previousTracks.pop();

        // Try to skip to beginning of current track first
        const position = getPosition();
        if ((position && position > 15) || previousTrack == undefined) {
            seek(0);
            return;
        }

        // Add current track to beginning of queue
        this.add(this.currentTrack, false, true);

        // Replace current track with last track in history
        this.currentTrack = previousTrack;

        eventBus.publish(MusicEvent.TRACK_REPLACE);
    };

    next() {
        if (playerSync.playerId != null) {
            // Delegate action to remote player
            controlChannel.sendMessage(ControlCommand.CLIENT_NEXT, { "player_id": playerSync.playerId });
            return;
        }

        // Remove first item from queue
        const track = this.queuedTracks.shift();
        if (track == undefined) {
            console.warn('queue: no next track available');
            return;
        }

        // Add current track to history
        if (this.currentTrack !== null) {
            this.previousTracks.push(this.currentTrack);
            // If history exceeded maximum length, remove first (oldest) element
            if (this.previousTracks.length > MAX_HISTORY_SIZE) {
                this.previousTracks.shift();
            }
        }

        // Replace current track with first item from queue
        this.currentTrack = track.track;
        eventBus.publish(MusicEvent.QUEUE_CHANGE);
        eventBus.publish(MusicEvent.TRACK_REPLACE);
    };



    /**
     * @returns {import("../types.js").QueuedTrackJson[]}
     */
    toJson() {
        return this.queuedTracks.map(queuedTrack => {
            return { manual: queuedTrack.manual, track: queuedTrack.track.toJson() };
        });
    }

    /**
     * @param {import("../types.js").QueuedTrackJson[]} jsonQueue
     */
    fromJson(jsonQueue) {
        const newQueue = [];
        for (const jsonTrack of jsonQueue) {
            let queuedTrack = null;

            // Reuse existing queued track object whenever possible
            // It is relatively expensive to create these objects
            for (const existingTrack of queue.queuedTracks) {
                if (existingTrack.track.path == jsonTrack.track.path && existingTrack.manual == jsonTrack.manual) {
                    queuedTrack = existingTrack;
                }
            }

            if (!queuedTrack) {
                queuedTrack = new QueuedTrack(new Track(jsonTrack.track), jsonTrack.manual);
            }

            newQueue.push(queuedTrack);
        }
        queue.queuedTracks = newQueue;
        eventBus.publish(MusicEvent.QUEUE_CHANGE);
    }

    /**
     * @returns {import("../types.js").SavedStateJson}
     */
    #getState() {
        return {
            "position": getPosition(),
            "current": queue.currentTrack ? queue.currentTrack.toJson() : null,
            "queue": this.toJson(),
        }
    }

    /**
     * @param {import("../types.js").SavedStateJson} state
     */
    #setState(state) {
        this.fromJson(state.queue);
        if (state.current) {
            queue.currentTrack = new Track(state.current);
            eventBus.publish(MusicEvent.TRACK_REPLACE);
        }
        if (state.position) {
            seek(state.position);
        }
    }

    #loadState() {
        const state = localStorage.getItem("state")
        if (state) {
            this.#setState(JSON.parse(state));
        }
    }

    #saveState() {
        localStorage.setItem("state", JSON.stringify(this.#getState()));
    }

    /**
     * Called when playlist checkboxes are loaded
     */
    init() {
        if (playerSync.playerId != null) {
            return;
        }

        if (Setting.RESTORE_QUEUE.checked) {
            try {
                this.#loadState();
            } catch (err) {
                // Catch error so queue.fill() is still called when something is wrong
                // Otherwise entire player would fail to load
                sendErrorReport(err);
            }
        }

        queue.fill();
    }
};

export const queue = new Queue();

// Clear the queue when playlists are changed.
playlistCheckboxes.registerPlaylistToggleListener(event => {
    if (playerSync.playerId != null || !Setting.AUTO_CLEAR_QUEUE.checked) {
        return;
    }

    if (event.state) {
        // Clear queue (except for manually added items)
        queue.clear();
    } else {
        // Modify queue to remove tracks from the disabled playlist
        queue.modifyQueue(tracks => {
            return tracks.filter(track => track.track.playlistName != event.playlist);
        });
    }
});

controlChannel.registerMessageHandler(ControlCommand.SERVER_FILE_CHANGE, async (/** @type {import("../types.js").ControlServerFileChange} */ data) => {
    // If track has been deleted on the server
    if (playerSync.playerId == null && data.action == "delete") {
        // Remove from queue
        queue.modifyQueue(queue => {
            const newQueue = queue.filter(track => track.track.path != data.track);
            return newQueue.length < queue.length ? newQueue : null;
        });
        // Remove from previousTracks
        queue.previousTracks = queue.previousTracks.filter(track => track.path != data.track);
    }
});
