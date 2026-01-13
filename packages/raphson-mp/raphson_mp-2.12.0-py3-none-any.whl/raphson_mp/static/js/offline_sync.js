import { ProgressMonitor } from "./progress.js";

const startButton = /** @type {HTMLButtonElement} */ (document.getElementById('start-button'));
const stopButton = /** @type {HTMLButtonElement} */ (document.getElementById('stop-button'));
const statusContainer = /** @type {HTMLTableElement} */ (document.getElementById('status'));
const progress = new ProgressMonitor(startButton, stopButton, statusContainer, "/offline/start", "/offline/stop", "/offline/monitor");
progress.start();
