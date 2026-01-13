import { createIcon, createToast, gettext, jsonPost, vars } from "./util.js";

const playlistElem = /** @type {HTMLDivElement} */ (document.getElementById('playlist'));
const playlist = playlistElem.textContent;

for (const elem of document.getElementsByClassName("add-button")) {
    if (!(elem instanceof HTMLButtonElement)) throw new Error();

    elem.addEventListener("click", async () => {
        const spinner = createIcon("loading");
        elem.replaceWith(spinner);
        try {
            await jsonPost("/spotify/download", {"id": elem.dataset.id, "dir": playlist});
            createToast("download", gettext("Download complete"));
        } finally {
            spinner.remove();
        }
    })
}
