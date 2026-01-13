import { music } from "../api.js";
import { browse, HomeBrowse } from "./browse.js";
import { news } from "./news.js";
import { queue } from "./queue.js";

class Windows {
    baseIndex;
    /** @type {Array<string>} */
    #openWindows;

    constructor() {
        this.baseIndex = 100;
        this.#openWindows = [];

        // Window open buttons
        for (const elem of document.getElementsByClassName('window-overlay')) {
            const openButton = document.getElementById('open-' + elem.id);
            if (openButton === null) {
                continue;
            }
            const id = elem.id;
            openButton.addEventListener('click', () => windows.open(id));
        }

        // Window close buttons
        for (const elem of document.getElementsByClassName('window-close-button')) {
            if (!(elem instanceof HTMLElement)) continue;
            const id = elem.dataset.for;
            if (id === undefined) {
                console.warn('Window close button has no data-for attribute');
                continue;
            }
            elem.addEventListener('click', () => history.back());
        }

        // Click outside window to close
        for (const elem of document.getElementsByClassName('window-overlay')) {
            elem.addEventListener('mousedown', event => {
                if (!event.currentTarget || event.target != event.currentTarget || !(event.currentTarget instanceof HTMLElement)) {
                    return; // clicked inside window
                }
                console.debug('window: clicked outside, closing window');
                this.closeTop();
            });
        }
    }

    /**
     * Open a window, above other windows. If the window is already opens, it is just moved to the top.
     * @param {string} idToOpen HTML id of window element
     */
    open(idToOpen, manageHistory = true) {
        console.debug('window: open:', idToOpen);

        const windowToOpen = /** @type {HTMLElement} */ (document.getElementById(idToOpen));
        if (!windowToOpen.classList.contains('window-overlay')) {
            throw new Error('Window is missing window-overlay class');
        }

        if (this.#openWindows.includes(idToOpen)) {
            console.debug('window: already open');
            // Already open, elevate existing window to top
            this.#openWindows.splice(this.#openWindows.indexOf(idToOpen), 1)
            this.#openWindows.push(idToOpen);

            // Change z-index of all open windows
            let i = 1;
            for (const openWindow of this.#openWindows) {
                console.debug('window: is open:', openWindow);
                const windowElem = /** @type {HTMLElement} */ (document.getElementById(openWindow));
                windowElem.style.zIndex = (this.baseIndex + i++) + '';
            }
        } else {
            // Add window to top (end of array), set z-index and make visible
            this.#openWindows.push(idToOpen);
            windowToOpen.style.zIndex = this.baseIndex + this.#openWindows.indexOf(idToOpen) + '';
            windowToOpen.classList.remove('overlay-hidden');

            // Add entry to history, so back button can close the window
            if (manageHistory) {
                console.debug('window: pushState:', this.#openWindows);
                history.pushState(this.#openWindows, '');
            }
        }

        // Prevent scrolling body, double scrolling is annoying, especially on touch screen devices
        document.body.classList.add("no-scroll");
    }

    /**
     * Close top window
     */
    closeTop() {
        if (this.#openWindows.length > 0) {
            history.back();
        }
    }

    /**
     * @param {string} id
     * @returns
     */
    isOpen(id) {
        return !document.getElementById(id)?.classList.contains('overlay-hidden');
    }

    /**
     * @param {Array<string>} newOpenWindows
     */
    setOpenWindows(newOpenWindows) {
        console.debug('window: set open windows:', newOpenWindows);
        const windowsToClose = new Set(this.#openWindows);

        for (const window of newOpenWindows) {
            if (windowsToClose.has(window)) {
                windowsToClose.delete(window);
            } else {
                this.open(window, false);
            }
        }

        for (const window of windowsToClose) {
            // Hide closed window
            const windowElem = /** @type {HTMLElement} */ (document.getElementById(window));

            windowElem.classList.add('overlay-hidden');
            windowElem.style.zIndex = '';
            this.#openWindows.splice(this.#openWindows.indexOf(window), 1);
        }

        // If there are no more open windows, allow scrolling body again
        if (this.#openWindows.length == 0) {
            document.body.classList.remove("no-scroll");
        }
    }
}

export const windows = new Windows();


// debug window
document.getElementById('debug-error')?.addEventListener('click', () => { throw new Error("debug"); });
document.getElementById('debug-news')?.addEventListener('click', () => news.queue());
document.getElementById('debug-queue')?.addEventListener('click', () => console.debug(queue.queuedTracks));

window.addEventListener('popstate', event => {
    console.debug('window: received popstate event');
    const newOpenWindows = event.state ? event.state : [];
    windows.setOpenWindows(newOpenWindows);
});

// When page loads, there are no open windows. The history state should reflect that.
if (history.state) {
    history.replaceState([], "");
}
