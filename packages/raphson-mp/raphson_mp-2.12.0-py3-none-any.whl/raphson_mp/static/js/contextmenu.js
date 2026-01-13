import { clamp, createIcon } from "./util.js";

export let openMenu = /** @type {ContextMenu | null} */ (null);

window.addEventListener('mousedown', event => {
    if (!openMenu || !openMenu.elem) return;

    if (event.target && event.target instanceof HTMLElement) {
        if (openMenu.elem.contains(event.target)) {
            return;
        }
    }

    openMenu.close();
});

export class AbstractMenuEntry {

}

export class MenuEntry extends AbstractMenuEntry {
    icon;
    name;
    description;
    hotkey;
    callback;

    /**
     * @param {string} icon
     * @param {string} name
     * @param {string | null} description
     * @param {string | null} hotkey
     * @param {() => void} callback
     */
    constructor(icon, name, description, hotkey, callback) {
        super();
        this.icon = icon;
        this.name = name;
        this.description = description;
        this.hotkey = hotkey;
        this.callback = callback;
    }

}

export class MenuSeparator extends AbstractMenuEntry {

}

export class ContextMenu {
    entries
    elem = /** @type {HTMLElement | null} */ (null);

    /**
     * @param {AbstractMenuEntry[]} entries
     */
    constructor(entries) {
        this.entries = entries
    }

    /**
     * @param {MouseEvent} mouse
     */
    open(mouse) {
        if (openMenu) openMenu.close();
        openMenu = this;

        this.elem = document.createElement("div");
        this.elem.classList.add("context-menu");

        for (const entry of this.entries) {
            if (entry instanceof MenuSeparator) {
                this.elem.append(document.createElement("hr"));
            } else if (entry instanceof MenuEntry) {
                const icon = createIcon(entry.icon, true);

                const name = document.createElement("span");
                name.textContent = entry.name;

                const hotkey = document.createElement("span");
                hotkey.classList.add("secondary");
                hotkey.textContent = entry.hotkey;

                const entryDiv = document.createElement("div");
                entryDiv.append(icon, name, hotkey);
                entryDiv.addEventListener("click", () => {
                    entry.callback();
                    this.close();
                });
                if (entry.description) {
                    entryDiv.title = entry.description;
                }
                this.elem.append(entryDiv);
            }

        }

        document.body.append(this.elem);
        const rect = this.elem.getBoundingClientRect();
        this.elem.style.left = clamp(mouse.pageX, 0, document.body.scrollWidth - rect.width) + "px";
        this.elem.style.top = clamp(mouse.pageY, 0, document.body.scrollHeight - rect.height) + "px";
    }

    /**
     * @param {string} hotkey
     */
    handleHotkey(hotkey) {
        if (hotkey == 'Escape') {
            this.close();
            return;
        }

        for (const entry of this.entries) {
            if (entry instanceof MenuEntry && entry.hotkey != null && entry.hotkey == hotkey) {
                entry.callback();
                this.close();
                return;
            }
        }
    }

    close() {
        if (this.elem) this.elem.remove();
        openMenu = null;
    }

    /**
     *
     * @param {HTMLElement} element
     */
    registerListener(element) {
        element.addEventListener("contextmenu", event => {
            event.preventDefault();
            this.open(event);
        });
    }
}
