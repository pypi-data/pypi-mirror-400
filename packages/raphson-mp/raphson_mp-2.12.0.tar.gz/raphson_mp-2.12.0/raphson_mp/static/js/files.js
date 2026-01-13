import { gettext, vars } from "./util.js";
import { ContextMenu, MenuEntry } from "./contextmenu.js";

const UPLOAD_FILES_BUTTON = document.getElementById('upload-files-button');
const UPLOAD_FILES_FORM = document.getElementById('upload-files-form');
const CREATE_DIRECTORY_BUTTON = document.getElementById('create-directory-button');
const CREATE_DIRECTORY_FORM = document.getElementById('create-directory-form');
const CREATE_DIRECTORY_DIRNAME = document.getElementById('dirname');
const FILES_TBODY = /** @type {HTMLTableSectionElement} */ (document.getElementById("tbody"));

if (UPLOAD_FILES_BUTTON && UPLOAD_FILES_FORM) {
    UPLOAD_FILES_BUTTON.addEventListener('click', () => {
        UPLOAD_FILES_BUTTON.setAttribute("disabled", "");
        UPLOAD_FILES_FORM.hidden = false;
    });
}

if (CREATE_DIRECTORY_BUTTON && CREATE_DIRECTORY_FORM && CREATE_DIRECTORY_DIRNAME) {
    CREATE_DIRECTORY_BUTTON.addEventListener('click', () => {
        CREATE_DIRECTORY_BUTTON.setAttribute("disabled", "");
        CREATE_DIRECTORY_FORM.hidden = false;
        CREATE_DIRECTORY_DIRNAME.focus();
    });
}

/**
 * @param {string} path
 * @param {string} newName
 */
async function renameFile(path, newName) {
    const formData = new FormData();
    formData.append("csrf", vars.csrfToken);
    formData.append("path", path);
    formData.append("new-name", newName);
    await fetch('/files/rename', {method: 'POST', body: formData});
    location.reload();
}

for (const tr of FILES_TBODY.children) {
    if (!(tr instanceof HTMLTableRowElement)) continue;

    const path = tr.dataset.path;
    if (!path) throw new Error("path missing from dataset");

    tr.addEventListener("contextmenu", event => {
        event.preventDefault();

        const entries = [
            new MenuEntry("download", gettext("Download"), null, null, () => {
                window.open('/files/download?path=' + encodeURIComponent(path), "_blank");
            }),
        ];

        // presence of upload button means user has write permissions
        if (UPLOAD_FILES_BUTTON) {
            entries.push(new MenuEntry("rename-box", gettext("Rename"), null, null, () => {
                window.location.assign('/files/rename?path=' + encodeURIComponent(path));
            }));

            const name = path.split("/").slice(-1)[0];
            const isTrash = window.location.href.endsWith("&trash"); // TODO properly examine query string
            if (isTrash) {
                entries.push(new MenuEntry("delete-restore", gettext("Restore from trash"), null, null, () => {
                    renameFile(path, name.substring(".trash.".length));
                }))
            } else {
                entries.push(new MenuEntry("delete", gettext("Move to trash"), null, null, () => {
                    renameFile(path, `.trash.${name}`);
                }));
            }
        }

        const menu = new ContextMenu(entries);
        menu.open(event);
    });
}
