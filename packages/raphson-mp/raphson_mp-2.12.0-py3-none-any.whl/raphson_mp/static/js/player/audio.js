import { controlChannel, ControlCommand } from "../api.js";
import { createToast, gettext, removeToast } from "../util.js";
import { playerSync } from "./sync.js";
import { eventBus, MusicEvent } from "./event.js";
import { queue } from "./queue.js";
import { Setting } from "./settings.js";
import { getVolume } from "./controls.js";

// Audio element is only to be used directly under very specific circumstances!
export const AUDIO_ELEMENT = /** @type {HTMLAudioElement} */ (document.getElementById("audio"));

AUDIO_ELEMENT.addEventListener('play', () => eventBus.publish(MusicEvent.PLAYER_PLAY));
AUDIO_ELEMENT.addEventListener('pause', () => eventBus.publish(MusicEvent.PLAYER_PAUSE));
AUDIO_ELEMENT.addEventListener('timeupdate', () => eventBus.publish(MusicEvent.PLAYER_POSITION));
AUDIO_ELEMENT.addEventListener('durationchange', () => eventBus.publish(MusicEvent.PLAYER_DURATION));
AUDIO_ELEMENT.addEventListener('seeked', () => eventBus.publish(MusicEvent.PLAYER_SEEK));
AUDIO_ELEMENT.addEventListener('ended', () => {
    if (playerSync.playerId != null) {
        // When following another player, that player is responsible for going to the next track.
        return;
    }
    queue.next();
});

// Audio element should always be playing at max volume
// Volume is set using GainNode
AUDIO_ELEMENT.volume = 1;

// Safari
if (AUDIO_ELEMENT.canPlayType("audio/webm;codecs=opus") != "probably") {
    alert("WEBM/OPUS audio not supported by your browser. Please update your browser or use a different browser.");
}

export const FFT_SIZE = 2 ** 13; // used by visualiser
let analyser = /** @type {AnalyserNode | null} */ (null);
let audioContext = /** @type {AudioContext | null} */ (null);
let gainNode = /** @type {GainNode | null} */ (null);

export function isPaused() {
    return AUDIO_ELEMENT.paused;
}

export async function play(local = false) {
    if (!local && playerSync.playerId != null) {
        // Send action to remote player, but for responsiveness also immediately start playing locally
        controlChannel.sendMessage(ControlCommand.CLIENT_PLAY, {"player_id": playerSync.playerId});
    }

    try {
        await AUDIO_ELEMENT.play();
        removeToast(gettext("Audio playback was blocked by your browser"));
    } catch (err) {
        if (err instanceof Error && err.name == "NotAllowedError") {
            createToast("play", gettext("Audio playback was blocked by your browser"));
        }
    }
}

export function pause(local = false) {
    if (!local && playerSync.playerId != null) {
        // Send action to remote player, but for responsiveness also immediately pause locally
        controlChannel.sendMessage(ControlCommand.CLIENT_PAUSE, {"player_id": playerSync.playerId});
    }

    return AUDIO_ELEMENT.pause();
}

export function getDuration() {
    return isFinite(AUDIO_ELEMENT.duration) && !isNaN(AUDIO_ELEMENT.duration) ? AUDIO_ELEMENT.duration : null;
}

export function getPosition() {
    return isFinite(AUDIO_ELEMENT.currentTime) && !isNaN(AUDIO_ELEMENT.currentTime) ? AUDIO_ELEMENT.currentTime : null;
}

/**
 * @param {number} position
 */
export function seek(position) {
    if (playerSync.playerId != null) {
        controlChannel.sendMessage(ControlCommand.CLIENT_SEEK, {"player_id": playerSync.playerId, position: position});
        return;
    }

    if (!isFinite(position) || isNaN(position)) {
        return;
    }
    AUDIO_ELEMENT.currentTime = position;
}

/**
 * @param {number} delta number of seconds to seek forwards, negative for backwards
 * @returns {void}
 */
export function seekRelative(delta) {
    const position = getPosition();
    const duration = getDuration();
    if (position === null || !duration) return;
    const newTime = position + delta;
    if (newTime < 0) {
        seek(0);
    } else if (newTime > duration) {
        seek(duration);
    } else {
        seek(newTime);
    }
}

export function getAnalyser() {
    return analyser;
}

eventBus.subscribe(MusicEvent.TRACK_REPLACE, async () => {
    if (!queue.currentTrack) throw new Error();
    AUDIO_ELEMENT.src = queue.currentTrack.getAudioURL(Setting.AUDIO_TYPE.value);
    play(true);
});

// Update currently playing track when audio quality is changed
Setting.AUDIO_TYPE.addEventListener('change', () => {
    if (!queue.currentTrack) return;
    const position = getPosition();
    AUDIO_ELEMENT.src = queue.currentTrack.getAudioURL(Setting.AUDIO_TYPE.value);
    // restore position
    if (position) seek(position);
});

// Can only create AudioContext once media is playing
AUDIO_ELEMENT.addEventListener('play', () => {
    if (audioContext) {
        if (audioContext.state == "running") {
            console.debug('audiocontext: running');
            return;
        } else if (audioContext.state == "suspended") {
            console.debug('audiocontext: resume');
            audioContext.resume();
            return;
        }
        // audio context needs to be re-created
    }
    console.debug('audiocontext: create');
    audioContext = new AudioContext();
    const source = audioContext.createMediaElementSource(AUDIO_ELEMENT);
    analyser = audioContext.createAnalyser();
    analyser.fftSize = FFT_SIZE;
    gainNode = audioContext.createGain();
    applyVolume(); // If gain or volume was changed while audio was still paused
    source.connect(analyser);
    source.connect(gainNode);
    gainNode.connect(audioContext.destination);
});

/**
 * Apply gain and volume changes
 */
function applyVolume() {
    // If gain node is available, we can immediately set the gain
    // Otherwise, the 'play' event listener will call this method again
    if (!gainNode || !audioContext) {
        console.debug('audiocontext: gainNode not available yet');
        return;
    }
    const gain = parseInt(Setting.AUDIO_GAIN.value);
    // https://www.dr-lex.be/info-stuff/volumecontrols.html
    const volume = Math.pow(getVolume(), 3);
    console.debug('audiocontext: set gain:', gain, volume, gain * volume);
    // exponential function cannot handle 0 value, so clamp to tiny minimum value instead
    gainNode.gain.exponentialRampToValueAtTime(Math.max(gain * volume, 0.0001), audioContext.currentTime + 0.1);
}

// Respond to volume changes
Setting.AUDIO_GAIN.addEventListener('change', () => applyVolume());
Setting.VOLUME.addEventListener('change', () => applyVolume());
