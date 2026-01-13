import { windows } from "./window.js";
import { queue } from "./queue.js";
import { lyrics } from "./lyrics.js";
import { theater } from "./theater.js";
import { registerHotKeyListener } from "../util.js";
import { browse, HomeBrowse } from "./browse.js";
import { isPaused, pause, play, seekRelative } from "./audio.js";
import { getVolume, setVolume } from "./controls.js";
import { openMenu } from "../contextmenu.js";

const VOLUME_HOTKEY_CHANGE = 0.05;

registerHotKeyListener(key => {
    if (openMenu) {
        openMenu.handleHotkey(key);
        return;
    }

    if (key == 'p' || key == ' ') {
        isPaused() ? play() : pause();
    } else if (key == 'ArrowLeft') {
        queue.previous();
    } else if (key == 'ArrowRight') {
        queue.next();
    } else if (key == 'ArrowUp') {
        setVolume(getVolume() + VOLUME_HOTKEY_CHANGE);
    } else if (key == 'ArrowDown') {
        setVolume(getVolume() - VOLUME_HOTKEY_CHANGE);
    } else if (key == '.' || key == '>') {
        seekRelative(3);
    } else if (key == ',' || key == '<') {
        seekRelative(-3);
    } else if (key == 'Escape') {
        windows.closeTop();
    } else if (key == '/') {
        browse(new HomeBrowse());
    } else if (key == "c") {
        queue.clear();
    } else if (key == "l") {
        lyrics.toggleLyrics();
    } else if (key == "t") {
        theater.toggle();
    } else if (key == "d") {
        windows.open('window-debug');
    }
});
