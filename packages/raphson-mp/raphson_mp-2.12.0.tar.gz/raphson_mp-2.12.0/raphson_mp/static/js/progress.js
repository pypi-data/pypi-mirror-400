import { checkResponseCode, jsonPost } from "./util.js";

export class ProgressMonitor {
    #decoder = new TextDecoder();
    #startButton;
    #stopButton;
    #statusContainer;
    #monitorEndpoint;
    #logTable = /** @type {HTMLTableSectionElement | null} */ (null);

    /**
     * @param {HTMLButtonElement} startButton
     * @param {HTMLButtonElement} stopButton
     * @param {HTMLDivElement} statusContainer
     * @param {string} startEndpoint
     * @param {string} stopEndpoint
     * @param {string} monitorEndpoint
     */
    constructor(startButton, stopButton, statusContainer, startEndpoint, stopEndpoint, monitorEndpoint) {
        this.#startButton = startButton;
        this.#stopButton = stopButton;
        this.#statusContainer = statusContainer;
        this.#monitorEndpoint = monitorEndpoint;

        startButton.addEventListener("click", () => jsonPost(startEndpoint, {}));
        stopButton.addEventListener("click", () => jsonPost(stopEndpoint, {}));
    }

    /**
     * @param {import("./types.js").ProgressEntry} entry
     * @returns {HTMLTableRowElement}
     */
    #createRow(entry) {
        if (!entry.task) throw new Error("this method does not handle all_done")
        const tdTask = document.createElement('td');
        tdTask.textContent = entry.task;
        const tdIcon = document.createElement('td');
        if (entry.state == "done") {
            tdIcon.classList.add('icon', 'icon-check', 'icon-col');
        } else if (entry.state == "start") {
            tdIcon.classList.add('icon', 'icon-loading', 'spinning', 'icon-col');
        } else if (entry.state == "error") {
            tdIcon.classList.add('icon', 'icon-close', 'icon-col');
        }
        const row = document.createElement('tr');
        row.dataset.task = entry.task;
        row.append(tdTask, tdIcon);
        return row;
    }

    /**
     * @param {import("./types.js").ProgressEntry} entry
     */
    #handleEntry(entry) {
        console.debug('progress: received value', entry);

        if (entry.state == "stopped") {
            if (this.#logTable) {
                // All done, any loading icons should be replaced by stop icon
                for (const elem of this.#logTable.querySelectorAll('.icon-loading')) {
                    elem.classList.remove('icon-loading', 'spinning');
                    elem.classList.add('icon-close');
                }
            } else {
                // Remove loading text
                this.#statusContainer.replaceChildren();
            }
            // Show start button
            this.#startButton.hidden = false;
            this.#stopButton.hidden = true;
        } else if (entry.state == "running") {
            if (this.#logTable == null) {
                const thTask = document.createElement('th');
                thTask.textContent = 'Task';
                thTask.classList.add('wrap');
                const thIcon = document.createElement('th');
                thIcon.classList.add('icon-col');
                const tr = document.createElement('tr');
                tr.append(thTask, thIcon);
                const thead = document.createElement('thead');
                thead.append(tr)
                const tbody = document.createElement('tbody');
                const table = document.createElement('table');
                table.classList.add('table');
                table.append(thead, tbody);
                this.#statusContainer.replaceChildren(table);
                this.#logTable = tbody;
            }
            // Show stop button
            this.#startButton.hidden = true;
            this.#stopButton.hidden = false;
        } else if (entry.state == "error") {
            if (!this.#logTable) throw new Error();
            console.info('progress: error:', entry.task);
            for (const row of this.#logTable.children) {
                if ((!(row instanceof HTMLElement))) throw new Error();
                if (row.dataset.task == entry.task) {
                    row.replaceWith(this.#createRow(entry));
                }
            }
        } else if (entry.state == "done") {
            if (!this.#logTable) throw new Error();
            console.info('progress: done:', entry.task);
            // Task done
            // Remove loading row
            for (const row of this.#logTable.children) {
                if ((!(row instanceof HTMLElement))) throw new Error();
                if (row.dataset.task == entry.task) {
                    row.remove();
                    break;
                }
            }

            // Insert done row after last loading row
            let lastLoadingRow = null;
            for (const row of this.#logTable.children) {
                const icon = /** @type {HTMLTableCellElement} */ (row.querySelector("td:nth-child(2)"));
                if (icon.classList.contains('icon-loading')) {
                    lastLoadingRow = row;
                } else {
                    break;
                }
            }
            const doneRow = this.#createRow(entry);
            if (lastLoadingRow) {
                lastLoadingRow.after(doneRow);
            } else {
                this.#logTable.prepend(doneRow);
            }
        } else if (entry.state == "start") {
            if (!this.#logTable) throw new Error();
            console.info('progress: start:', entry.task);
            // Task start
            this.#logTable.prepend(this.#createRow(entry));

            if (this.#logTable.children.length > 100) {
                this.#logTable.children[this.#logTable.children.length - 1].remove();
            }
        } else {
            console.warn('progress: unknown state:', entry.state);
        }
    }

    /**
     * @param {ReadableStreamReadResult<Uint8Array<ArrayBufferLike>>} result
     */
    async #handleResponse(result) {
        const values = this.#decoder.decode(result.value);
        for (const value of values.split('\n')) {
            if (value) {
                this.#handleEntry(JSON.parse(value));
            }
        }
        return result;
    }

    async start() {
        try {
            const response = await fetch(this.#monitorEndpoint, { method: 'GET' });
            checkResponseCode(response);
            if (response.body == null) throw new Error();
            const reader = response.body.getReader();

            let result;
            while (!(result = await reader.read()).done) {
                await this.#handleResponse(result);
            }
        } finally {
            this.#statusContainer.replaceChildren("Waiting for status...");
            this.#logTable = null;
            setTimeout(() => this.start(), 1000);
        }
    }
}
