import { controlChannel, ControlCommand, ControlTopic, music, Track } from "../api.js";
import { MAX_HISTORY_SIZE, queue } from "./queue.js";
import { eventBus, MusicEvent } from "./event.js";
import { clamp, createToast, gettext, throttle, withLock } from "../util.js";
import { Setting } from "./settings.js";
import { playlistCheckboxes } from "./playlists.js";
import { AUDIO_ELEMENT, getDuration, getPosition, isPaused, pause, play } from "./audio.js";
import { getVolume } from "./controls.js";

const SYNC_BANNER = /** @type {HTMLDivElement} */ (document.getElementById('sync-banner'));
const SYNC_BANNER_TEXT = /** @type {HTMLDivElement} */ (document.getElementById('sync-banner-text'));

// Send playing status to server
{
    async function updateNowPlaying() {
        let duration = getDuration();
        if (duration == null && queue.currentTrack != null) {
            // try to use duration from metadata if duration is unknown (e.g. when audio is not loaded yet)
            duration = queue.currentTrack.duration;
        }

        controlChannel.sendMessage(ControlCommand.CLIENT_STATE, {
            paused: isPaused(),
            position: getPosition(),
            duration: duration,
            control: true,
            volume: getVolume(),
            player_name: Setting.NAME.value,
            queue: queue.toJson(),
            playlists: playlistCheckboxes.getActivePlaylists(),
            track: queue.currentTrack == null ? null : queue.currentTrack.toJson(),
        });
    }

    const throttledUpdate = throttle(30, true, updateNowPlaying);

    setInterval(throttledUpdate, 30_000);
    controlChannel.registerConnectHandler(throttledUpdate);
    Setting.NAME.addEventListener('input', throttledUpdate);
    eventBus.subscribe(MusicEvent.PLAYER_PLAY, throttledUpdate);
    eventBus.subscribe(MusicEvent.PLAYER_PAUSE, throttledUpdate);
    eventBus.subscribe(MusicEvent.PLAYER_SEEK, throttledUpdate);
    eventBus.subscribe(MusicEvent.TRACK_CHANGE, throttledUpdate);
    eventBus.subscribe(MusicEvent.QUEUE_CHANGE, throttledUpdate);
    playlistCheckboxes.registerPlaylistToggleListener(throttledUpdate);
    controlChannel.registerMessageHandler(ControlCommand.SERVER_REQUEST_UPDATE, throttledUpdate);
}

// Act on commands from server
{
    controlChannel.registerMessageHandler(ControlCommand.SERVER_PLAY, () => {
        createToast('play', gettext("Started playing by remote control"));
        play();
    });

    controlChannel.registerMessageHandler(ControlCommand.SERVER_PAUSE, () => {
        createToast('pause', gettext("Paused by remote control"));
        pause();
    });

    controlChannel.registerMessageHandler(ControlCommand.SERVER_PREVIOUS, () => {
        createToast('skip-previous', gettext("Skipped to previous track by remote control"));
        queue.previous();
    });

    controlChannel.registerMessageHandler(ControlCommand.SERVER_NEXT, () => {
        createToast('skip-next', gettext("Skipped to next track by remote control"));
        queue.next();
    });

    controlChannel.registerMessageHandler(ControlCommand.SERVER_SEEK, (/** @type {import("../types.js").ControlClientSeek} */ data) => {
        createToast('play', gettext("Seeked by remote control"));
        AUDIO_ELEMENT.currentTime = data.position;
    });

    controlChannel.registerMessageHandler(ControlCommand.SERVER_SET_QUEUE, async (/** @type {import("../types.js").ControlServerSetQueue} */ data) => {
        createToast('playlist-music', gettext("Queue changed by remote control"));
        queue.fromJson(data.tracks);
    });

    controlChannel.registerMessageHandler(ControlCommand.SERVER_SET_PLAYING, async (/** @type {import("../types.js").ControlServerSetPlaying} */ data) => {
        createToast('playlist-music', gettext("Playing track changed by remote control"));
        // Add current track to history
        if (queue.currentTrack !== null) {
            queue.previousTracks.push(queue.currentTrack);
            // If history exceeded maximum length, remove first (oldest) element
            if (queue.previousTracks.length > MAX_HISTORY_SIZE) {
                queue.previousTracks.shift();
            }
            eventBus.publish(MusicEvent.QUEUE_CHANGE);
        }

        // Replace current track with given track
        queue.currentTrack = new Track(data.track);
        eventBus.publish(MusicEvent.TRACK_REPLACE);
    });

    controlChannel.registerMessageHandler(ControlCommand.SERVER_SET_PLAYLISTS, async (/** @type {import("../types.js").ControlServerSetPlaylists} */ data) => {
        createToast('playlist-music', gettext("Playlists changed by remote control"));
        playlistCheckboxes.setActivePlaylists(data.playlists);
    });

    controlChannel.registerMessageHandler(ControlCommand.SERVER_PING, (/** @type {import("../types.js").ControlServerPing} */ data) => {
        controlChannel.sendMessage(ControlCommand.CLIENT_PONG, { player_id: data.player_id });
    });
}

// Send stop signal to server when page is closed
window.addEventListener("pagehide", () => {
    controlChannel.sendStopSignal();
});

class PlayerSync {
    playerId = /** @type {string | null} */ (null);

    /**
     * Measured latency is us -> server -> remote player -> server -> us.
     * We can add half this latency to a received position from the remote player.
     */
    #latencyMeasurements = /** @type {number[]} */ ([]);
    #latencyMeasureStart = /** @type {number | null} */ (null);
    #medianLatency = 0;

    #lastUpdate = 0;
    #hasSynced = false;

    #checkSyncWorkingTimer = 0;
    #measureLatencyTimer = 0;

    constructor() {
        controlChannel.subscribe(ControlTopic.PLAYERS);

        // Sync currently playing
        controlChannel.registerMessageHandler(ControlCommand.SERVER_PLAYER_STATE, (/** @type {import("../types.js").ControlServerPlayerState} */ data) => {
            if (data.player_id == controlChannel.player_id) {
                // It's us
                return;
            }

            if (data.player_id != this.playerId) {
                // We are synced to a different player or not synced at all.
                // If auto sync is enabled, we may want to switch our sync.

                if (Setting.AUTO_SYNC_USERNAME.value == data.username &&
                    (Setting.AUTO_SYNC_DEVICE.value == "" || Setting.AUTO_SYNC_DEVICE.value == data.player_name)
                ) {
                    createToast('sync', gettext("Started sync according to auto sync settings"));
                    console.info('control: auto sync:', data.player_id);

                    // Start sync without requesting update from the remote player, we have the data right here already.
                    this.stop();
                    this.start(data.player_id, false);
                } else {
                    return;
                }
            }

            if (data.queue == null || data.playlists == null) throw new Error("null queue or playlists");

            this.#lastUpdate = Date.now();

            // performSync() cannot function without playlists being loaded
            music.waitForPlaylistsLoaded(() => {
                withLock("control_sync", async () => await this.#performSync(data));
            });
        });

        // Disconnect sync when other player stops
        controlChannel.registerMessageHandler(ControlCommand.SERVER_PLAYER_CLOSED, (/** @type {import("../types.js").ControlServerPlayerClosed} */ data) => {
            if (data.player_id == this.playerId) {
                this.stop();
            }
        });

        // Send playlist changes
        playlistCheckboxes.registerPlaylistToggleListener(() => {
            // Only when we are fully synced, can we to send modifications back to the remote player. We cannot do it
            // before, or we risk sending wrong information to the remote player.
            if (this.playerId != null && this.#hasSynced) {
                controlChannel.sendMessage(ControlCommand.CLIENT_SET_PLAYLISTS, { player_id: this.playerId, playlists: playlistCheckboxes.getActivePlaylists() });
            }
        });

        controlChannel.registerMessageHandler(ControlCommand.SERVER_PONG, () => {
            if (this.#latencyMeasureStart == null) {
                console.warn('sync: received PONG but we have not recorded any PING being sent');
                return;
            }

            const latency = performance.now() - this.#latencyMeasureStart;
            if (latency < 0 || latency > 1000) {
                console.warn('sync: ignoring extreme latency measurement:', latency);
                return;
            }
            this.#latencyMeasureStart = null;

            this.#latencyMeasurements.push(latency);
            if (this.#latencyMeasurements.length > 15) {
                this.#latencyMeasurements.splice(0, 5);
            }
            this.#medianLatency = this.#latencyMeasurements.toSorted()[Math.floor(this.#latencyMeasurements.length / 2)];
            console.debug('sync: measured latency:', latency, 'median:', this.#medianLatency);
        });

        const syncDisconnectButton = document.getElementById('sync-disconnect');
        syncDisconnectButton?.addEventListener('click', () => this.stop());
    }

    /**
     * @param {string} playerId
     */
    start(playerId, requestUpdate = true) {
        clearInterval(this.#measureLatencyTimer);
        clearInterval(this.#checkSyncWorkingTimer);
        this.playerId = playerId;

        this.#hasSynced = false;

        playlistCheckboxes.disableSaving();

        // Measure latency
        this.#measureLatencyTimer = setInterval(() => {
            if (this.playerId == null || !Setting.ACCURATE_SYNC.checked) return;
            this.#latencyMeasureStart = performance.now();
            controlChannel.sendMessage(ControlCommand.CLIENT_PING, { player_id: this.playerId });
        }, 10000);

        this.#checkSyncWorkingTimer = setInterval(() => {
            if (Date.now() - this.#lastUpdate > 90000) {
                this.stop();
            } else if (Date.now() - this.#lastUpdate > 50000) {
                createToast('sync', gettext("Other player went offline. Sync will disconnect automatically if this persists."));
            }
        }, 10000);

        if (requestUpdate) {
            controlChannel.sendMessage(ControlCommand.CLIENT_REQUEST_UPDATE, { player_id: playerId });
        }
    }

    stop() {
        createToast('sync', gettext("Sync disconnected"));
        this.playerId = null;
        clearInterval(this.#measureLatencyTimer);
        clearInterval(this.#checkSyncWorkingTimer);
        SYNC_BANNER.hidden = true;
        queue.fill(); // Our minimum queue size may be larger than the remote player
    }

    /**
     * @param {string} playerId
     */
    cast(playerId) {
        // Send local state to remote player, then connect sync to remote player
        if (queue.currentTrack) {
            controlChannel.sendMessage(ControlCommand.CLIENT_SET_PLAYING, {"player_id": playerId, 'track': queue.currentTrack.toJson()});
        }
        controlChannel.sendMessage(ControlCommand.CLIENT_SET_QUEUE, {
            player_id: playerId,
            tracks: queue.queuedTracks.map(track => { return {manual: track.manual, track: track.track.toJson() }; }),
        });
        const position = getPosition();
        if (position) {
            controlChannel.sendMessage(ControlCommand.CLIENT_SEEK, {"player_id": playerId, "position": position});
        }
        this.start(playerId);
    }

    /**
     * @param {import("../types.js").ControlServerPlayerState} data
     */
    async #performSync(data) {
        const remoteQueue = data.queue;
        const remotePlaylists = data.playlists;

        SYNC_BANNER.hidden = false;
        SYNC_BANNER_TEXT.textContent = data.nickname + (data.player_name ? " - " + data.player_name : "");

        // Current track
        if (data.track && (queue.currentTrack == null || data.track.path != queue.currentTrack.path)) {
            queue.currentTrack = new Track(data.track);
            eventBus.publish(MusicEvent.TRACK_REPLACE);

            // Wait for player to start playing, before the code below can update position
            if (!data.paused) {
                await play(true);
            }
        } else if (data.track == null && queue.currentTrack != null) {
            // Other player has stopped playing any media
            queue.currentTrack = null;
            eventBus.publish(MusicEvent.TRACK_REPLACE);
        }

        // Position
        const position = getPosition();
        if (position != null && data.position != null) {
            AUDIO_ELEMENT.playbackRate = 1;

            if (Setting.ACCURATE_SYNC.checked) {
                const targetPosition = data.position + (this.#medianLatency / 2 / 1000);
                const offset = position - targetPosition;
                console.debug('sync: position offset:', offset);
                AUDIO_ELEMENT.playbackRate = 1;
                if (Math.abs(offset) > 1) {
                    console.debug('sync: seek');
                    AUDIO_ELEMENT.currentTime = data.position;
                } else if (position != 0) { // avoid division by zero
                    const rate = clamp((targetPosition / position) ** 0.5, 0.95, 1.05);
                    console.debug('sync: set rate:', rate);
                    AUDIO_ELEMENT.playbackRate = rate;
                }
            } else {
                AUDIO_ELEMENT.playbackRate = 1;
                if (Math.abs(data.position - position) > 2) {
                    console.debug("sync: seek");
                    AUDIO_ELEMENT.currentTime = data.position;
                }
            }
        }

        // Play/pause, must be after changing current track because TRACK_CHANGE event causes the track to start playing
        // Use local=true, player.pause() and player.play() do not need to send pause/play back to the remote server
        if (data.paused && !isPaused()) {
            console.debug('sync: pause');
            pause(true);
        } else if (!data.paused && isPaused()) {
            console.debug('sync: play');
            play(true);
        }

        // Playlists
        if (remotePlaylists) {
            playlistCheckboxes.setActivePlaylists(remotePlaylists, false); // fireEvents=false to avoid loop
        }

        // Queue
        if (remoteQueue) {
            queue.fromJson(remoteQueue);
        }

        this.#hasSynced = true;
    }
}

export const playerSync = new PlayerSync();

if (window.location.hash != "") {
    const playerId = window.location.hash.substring(1);
    console.debug('sync: start:', playerId);
    playerSync.start(playerId);
}
