import { eventBus, MusicEvent } from "./event.js";
import { queue } from "./queue.js";
import { music } from "../api.js";
import { isPaused } from "./audio.js";
import { getVolume } from "./controls.js";

const PLAYED_TIMER_INTERVAL_SECONDS = 5;

let hasScrobbled = false;
let playingCounter = 0;
let requiredPlayingCounter = /** @type {number | null} */ (null);

setInterval(async () => {
    if (hasScrobbled || !queue.currentTrack || requiredPlayingCounter == null || isPaused()) {
        return;
    }

    if (getVolume() == 0) {
        console.debug('history: volume is zero');
        return;
    }

    playingCounter += PLAYED_TIMER_INTERVAL_SECONDS;

    console.debug('history: playing, counter:', playingCounter, '/', requiredPlayingCounter);

    if (playingCounter > requiredPlayingCounter) {
        console.info('history: played');
        hasScrobbled = true;
        await music.played(queue.currentTrack);
    }
}, PLAYED_TIMER_INTERVAL_SECONDS * 1000);

eventBus.subscribe(MusicEvent.TRACK_REPLACE, () => {
    hasScrobbled = false;
    playingCounter = 0;
    // last.fm requires track to be played for half its duration or for 4 minutes (whichever is less)
    if (queue.currentTrack) {
        requiredPlayingCounter = Math.min(4 * 60, Math.round(queue.currentTrack.duration / 2));
    } else {
        requiredPlayingCounter = null;
    }
});
