import { sendErrorReport } from "../util.js";

export const MusicEvent = {
    METADATA_CHANGE: 'metadata_change', // Tracks or playlists have been changed, added, or removed. Any HTML with playlist/track info should be updated. Track with updated metadata may be provided as parameter to the callable.
    TRACK_CHANGE: 'track_change', // Metadata for the currently playing track has changed (also fired on TRACK_REPLACE).
    TRACK_REPLACE: 'track_replace', // A different track is playing
    QUEUE_CHANGE: `queue_change`, // Queue changed
    PLAYER_PLAY: `player_play`,
    PLAYER_PAUSE: `player_pause`,
    PLAYER_POSITION: `player_position`,
    PLAYER_DURATION: `player_duration`,
    PLAYER_SEEK: `player_seek`,
};

class EventBus {
    /** @type{Object.<string, Array<Function>>} */
    listeners;

    constructor() {
        this.listeners = {};

        for (const event of Object.values(MusicEvent)) {
            this.listeners[event] = [];
        }
    }

    /**
     * @param {string} name
     * @param {function} callable
     */
    subscribe(name, callable) {
        console.debug('event: subscribed to:', name, callable);
        this.listeners[name].push(callable);
    }

    /**
     * @param {string} name
     * @param {function} callable
     */
    unsubscribe(name, callable) {
        console.debug('event: unsubscribed from:', name, callable);
        const index = this.listeners[name].indexOf(callable);
        if (index != -1) {
            this.listeners[name].splice(index, 1);
        }
    }

    /**
     * @param {string} name
     * @param {...any} params
     */
    publish(name, ...params) {
        console.debug('event: published:', name, 'to', this.listeners[name].length, 'listeners');
        for (const callable of this.listeners[name]) {
            try {
                callable(...params);
            } catch (error) {
                console.error(error);
                sendErrorReport(error);
            }
        }
    }
}

export const eventBus = new EventBus();

// The track being replaced implies that track metadata has changed
eventBus.subscribe(MusicEvent.TRACK_REPLACE, () => eventBus.publish(MusicEvent.TRACK_CHANGE))
