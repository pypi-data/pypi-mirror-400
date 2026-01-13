import { eventBus, MusicEvent } from "./event.js";
import { createIconButton, durationToString, throttle, gettext, withLock } from "../util.js";
import { windows } from "./window.js";
import { Album, Artist, music, Playlist, RAPHSON_SMALL_URL, Track } from "../api.js";
import { trackDisplayHtml } from "./track.js";
import { queue } from "./queue.js";
import { createPlaylistDropdown } from "./playlists.js";

const BROWSE_CONTENT = /** @type {HTMLDivElement} */ (document.getElementById('browse-content'));

/**
 * @param {Track} track
 * @returns {HTMLTableRowElement}
 */
function getTrackRow(track) {
    const colPlaylist = document.createElement('td');
    colPlaylist.textContent = track.playlistName;

    const colDuration = document.createElement('td');
    colDuration.textContent = durationToString(track.duration);

    const colTitle = document.createElement('td');
    colTitle.appendChild(trackDisplayHtml(track));
    colTitle.style.width = '100%'; // make title column as large as possible

    const addButton = createIconButton('playlist-plus', gettext("Add to queue"));
    addButton.addEventListener('click', () => queue.add(track, true));
    const colAdd = document.createElement('td');
    colAdd.appendChild(addButton);

    const row = document.createElement('tr');
    row.append(colPlaylist, colDuration, colTitle, colAdd);
    return row;
}

/**
 * @param {Array<Track>} tracks
 * @returns {HTMLTableElement}
 */
export function getTracksTable(tracks) {
    const table = document.createElement('table');
    table.classList.add('track-list');
    const tbody = document.createElement('tbody');
    table.append(tbody);

    for (const track of tracks) {
        tbody.append(getTrackRow(track));
    }
    return table;
}

const LAZY_LOAD_CHUNK = 300;

class CachedChunk {
    offset;
    tracks;
    /**
     * @param {number} offset
     * @param {Track[]} tracks
     */
    constructor(offset, tracks) {
        this.offset = offset;
        this.tracks = tracks;
    }
}

/**
 * @param {import("../types.js").FilterJson} filters
 * @param {number} length
 */
export async function getLazyLoadedTracksTable(filters, length) {
    const rowHeight = "48px";

    const table = document.createElement('table');
    table.classList.add('track-list');
    const tbody = document.createElement('tbody');
    table.append(tbody);

    // Load the initial chunk of tracks
    filters.limit = LAZY_LOAD_CHUNK;
    let cache = /** @type {CachedChunk | null} */ (null);

    // Placeholder element
    const placeholder = document.createElement('tr');
    placeholder.dataset.placeholder = '1';
    placeholder.style.height = rowHeight;
    const placeholderCell = document.createElement('td');
    placeholderCell.colSpan = 5;
    placeholder.append(placeholderCell);

    /**
     * @param {Array<IntersectionObserverEntry>} entries
     * @param {IntersectionObserver} observer
     */
    async function observerCallback(entries, observer) {
        if (!document.body.contains(table)) {
            // the table no longer exists, unregister ourselves
            console.debug('browse: disconnect observer');
            observer.disconnect();
            return;
        }

        for (const entry of entries) {
            const elem = /** @type {HTMLElement} */ (entry.target);
            let newElem;
            if (entry.isIntersecting && elem.dataset.placeholder == '1') {
                // console.debug('browse: placeholder -> row', elem.dataset.index);

                // Element is a placeholder, but needs to be turned into a real track row
                const trackIndex = parseInt(/** @type {string} */(elem.dataset.index));

                if (cache == null || trackIndex < cache.offset || trackIndex >= cache.offset + LAZY_LOAD_CHUNK) {
                    await withLock("browse_lazy", async () => {
                        // maybe now that the lock is acquired, loading track list is no longer necessary?
                        if (cache != null && trackIndex >= cache.offset && trackIndex < cache.offset + LAZY_LOAD_CHUNK) {
                            return;
                        }

                        // the order of updating chunk and offset matters! there must be no await in between, for atomicity
                        const offset = filters.offset = Math.floor(trackIndex / LAZY_LOAD_CHUNK) * LAZY_LOAD_CHUNK;
                        const tracks = await music.filter(filters);
                        cache = new CachedChunk(offset, tracks);
                    });
                }

                if (!cache) throw new Error();
                const track = cache.tracks[trackIndex % LAZY_LOAD_CHUNK];
                if (!track) throw new Error(`track at index ${trackIndex} does not exist in cache with offset ${cache.offset}`);

                newElem = getTrackRow(track);
                newElem.style.height = rowHeight; // placeholder row height must match actual element height
            } else if (!entry.isIntersecting && elem.dataset.placeholder != '1') {
                // console.debug('browse: row -> placeholder', elem.dataset.index);
                newElem = /** @type {HTMLElement} */ (placeholder.cloneNode(true));
            }

            if (newElem) {
                newElem.dataset.index = elem.dataset.index;
                requestAnimationFrame(() => {
                    elem.replaceWith(newElem);
                    observer.unobserve(elem);
                    observer.observe(newElem);
                });
            }
        }
    };

    // @ts-ignore delay property is only supported by Chrome
    // Without the delay property, Chrome lags when scrolling. Firefox doesn't, so it doesn't need the delay either :)
    const observer = new IntersectionObserver(observerCallback, { root: null, scrollMargin: '1000px', delay: 100 });

    // Add placeholder elements
    for (let i = 0; i < length; i++) {
        const row = /** @type {HTMLElement} */ (placeholder.cloneNode(true));
        row.dataset.index = '' + i;
        observer.observe(row);
        tbody.append(row);
    }

    return table;
}

/**
 * @param {Album | null} album
 * @param {Array<Track>} tracks
 * @returns {HTMLDivElement}
 */
function getAlbumHTML(album, tracks) {
    const image = document.createElement('img');
    image.src = album ? album.getCoverURL('low') : RAPHSON_SMALL_URL;
    image.style.height = image.style.width = '5rem';
    image.style.borderRadius = 'var(--border-radius)';
    image.style.cursor = 'pointer';
    image.addEventListener('click', () => window.open(album?.getCoverURL('high'), '_blank'));

    const text = document.createElement('div');
    const name = document.createElement('h3');
    name.textContent = album ? album.name : gettext("Unknown album");
    name.style.margin = '0';
    text.append(name);

    const header = document.createElement('div');
    header.append(image, text);
    header.classList.add('flex-vcenter', 'flex-gap');
    header.style.marginTop = 'var(--gap)';
    header.style.marginBottom = 'var(--halfgap)';

    for (const track of tracks) {
        if (track.year) {
            const year = document.createElement('p');
            year.textContent = '' + track.year;
            year.classList.add('secondary');
            text.append(year);
            break;
        }
    }

    const albumHtml = document.createElement('div');
    albumHtml.replaceChildren(header, getTracksTable(tracks));
    return albumHtml;
}

/**
 * @param {Artist} artist
 * @param {Array<Track>} tracks
 */
function getArtistHTML(artist, tracks) {
    const children = [];

    const text = document.createElement('div');
    const name = document.createElement('h3');
    name.textContent = artist.name;
    const extract = document.createElement('p');
    extract.classList.add('secondary-large');
    text.append(name, extract);

    artist.getExtract().then(text => extract.textContent = text);

    const image = document.createElement('img');
    image.src = artist.getImageURL("low");
    image.style.height = image.style.width = '10rem';
    image.style.borderRadius = 'var(--border-radius)';
    image.style.cursor = 'pointer';
    image.addEventListener('click', () => window.open(artist.getImageURL("high"), '_blank'));

    const header = document.createElement('div');
    header.append(text, image);
    header.classList.add('flex-space-between', 'flex-vcenter', 'flex-gap');
    children.push(header);

    const albums = /** @type {Array<Album>} */ ([]);
    const looseTracks = /** @type {Array<Track>} */ ([]);

    for (const track of tracks) {
        const album = track.getAlbum();
        if (album) {
            let foundAlbum = false;
            for (const album2 of albums) {
                if (album2.name.toLowerCase() == album.name.toLowerCase()) {
                    foundAlbum = true;
                    break;
                }
            }
            if (!foundAlbum) {
                albums.push(album);
            }
        } else {
            looseTracks.push(track);
        }
    }

    for (const album of albums) {
        const albumTracks = [];
        for (const track of tracks) {
            if (track.album && track.album.toLowerCase() == album.name.toLowerCase()) {
                albumTracks.push(track);
            }
        }
        children.push(getAlbumHTML(album, albumTracks));
    }

    if (looseTracks.length > 0) {
        children.push(getAlbumHTML(null, looseTracks));
    }

    return children;
}

/**
 * @param {string} name
 * @param {string} imageUrl
 * @param {() => void} onClick
 * @returns {HTMLDivElement}
 */
function createImageBox(name, imageUrl, onClick) {
    const text = document.createElement('div');
    text.textContent = name;
    text.classList.add('box-header', 'line');

    const img = document.createElement('div');
    const imgUri = imageUrl;
    img.style.background = `black url("${imgUri}") no-repeat center / cover`;
    img.style.height = '12rem';

    const box = document.createElement('div');
    box.classList.add('box');
    box.style.width = '12rem';
    box.addEventListener('click', onClick);
    box.append(text, img);
    return box;
}

class AbstractBrowse {
    /** @type {string} */
    title;
    /**
     * @param {string} title
     */
    constructor(title) {
        this.title = title;
    }

    async render() {
        throw new Error("abstract method");
    }
}

export class HomeBrowse extends AbstractBrowse {
    #abortController = /** @type {AbortController | null} */ (null);
    #rememberedQuery = /** @type {string | null} */ (null);

    constructor() {
        super(gettext("Browse"));
    }

    /**
     * @param {string} query
     * @returns {Promise<HTMLDivElement>} result
     */
    async #performSearch(query) {
        console.debug('performSearch');
        // abort an existing search query request
        if (this.#abortController) {
            this.#abortController.abort();
        }

        const resultElem = document.createElement('div');

        if (query.length < 3) {
            return resultElem;
        }

        let result;
        try {
            this.#abortController = new AbortController();
            result = await music.search(query, this.#abortController.signal);
            this.#abortController = null;
            console.debug('search: result:', result);
        } catch (err) {
            if (err instanceof DOMException && err.name == "AbortError") {
                console.info("search: aborted");
                return resultElem;
            }
            throw err;
        }

        // Tracks
        if (result.tracks.length > 0) {
            const heading = document.createElement('h3');
            heading.textContent = gettext("Tracks");
            resultElem.append(heading, getTracksTable(result.tracks));
        }

        // Artists
        if (result.artists.length > 0) {
            const heading = document.createElement('h3');
            heading.textContent = gettext("Artists");
            const images = document.createElement('div');
            images.classList.add("search-result-images");
            for (const artist of result.artists) {
                images.append(createImageBox(artist.name, artist.getImageURL("low"), () => browse(new ArtistBrowse(artist))));
                if (images.childNodes.length > 10) {
                    break;
                }
            }
            resultElem.append(heading, images);
        }

        // Albums
        if (result.albums.length > 0) {
            const heading = document.createElement('h3');
            heading.textContent = gettext("Albums");
            const images = document.createElement('div');
            images.classList.add("search-result-images");
            for (const album of result.albums) {
                images.append(createImageBox(album.name, album.getCoverURL('low'), () => browse(new AlbumBrowse(album))));
                if (images.childNodes.length > 10) {
                    break;
                }
            }
            resultElem.append(heading, images);
        }

        return resultElem;
    }

    async render() {
        const playlistSelect = createPlaylistDropdown(false);
        const noPlaylistOption = document.createElement('option');
        noPlaylistOption.textContent = gettext("Playlist");
        playlistSelect.value = "";
        playlistSelect.prepend(noPlaylistOption);
        playlistSelect.addEventListener('input', () => browse(new PlaylistBrowse(music.playlist(playlistSelect.value))));

        const recentlyAddedButton = document.createElement('button');
        recentlyAddedButton.textContent = gettext("Recently added");
        recentlyAddedButton.addEventListener("click", () => browse(new RecentlyAddedBrowse()));

        const recentlyReleasedButton = document.createElement('button');
        recentlyReleasedButton.textContent = gettext("Recently released");
        recentlyReleasedButton.addEventListener("click", () => browse(new RecentlyReleasedBrowse()));

        const randomButton = document.createElement('button');
        randomButton.textContent = gettext("Random");
        randomButton.addEventListener("click", () => browse(new RandomBrowse()));

        const missingMetadataButton = document.createElement('button');
        missingMetadataButton.textContent = gettext("Missing metadata");
        missingMetadataButton.addEventListener("click", () => browse(new MissingMetadataBrowse()));

        const buttonsContainer = document.createElement('div');
        buttonsContainer.append(playlistSelect, recentlyAddedButton, recentlyReleasedButton, randomButton, missingMetadataButton);
        buttonsContainer.classList.add('flex-halfgap');
        buttonsContainer.style.marginBottom = "var(--gap)";

        const searchQuery = document.createElement('input');
        searchQuery.type = 'search';
        searchQuery.placeholder = gettext("Search query");
        searchQuery.style.width = '100%';

        const searchResult = document.createElement('div');

        searchQuery.addEventListener('input', throttle(100, true, async () => {
            this.#rememberedQuery = searchQuery.value;
            searchResult.replaceChildren(await this.#performSearch(searchQuery.value));
        }));

        if (this.#rememberedQuery) {
            searchQuery.value = this.#rememberedQuery;
            searchResult.replaceChildren(await this.#performSearch(searchQuery.value));
        }

        BROWSE_CONTENT.replaceChildren(buttonsContainer, searchQuery, searchResult);

        setTimeout(() => searchQuery.focus(), 0);
    }
}

export class TracksBrowse extends AbstractBrowse {
    filters;
    /**
     * @param {string} title
     * @param {import("../types.js").FilterJson} filters
     */
    constructor(title, filters) {
        super(title);
        this.filters = filters;
    }

    async render() {
        const tracks = await music.filter(this.filters);
        BROWSE_CONTENT.replaceChildren(getTracksTable(tracks));
    }
}

export class LazyTracksBrowse extends AbstractBrowse {
    filters;
    length;
    /**
     * @param {string} title
     * @param {import("../types.js").FilterJson} filters
     * @param {number} length number of items
     */
    constructor(title, filters, length) {
        super(title);
        this.filters = filters;
        this.length = length;
    }

    async render() {
        BROWSE_CONTENT.replaceChildren(await getLazyLoadedTracksTable(this.filters, this.length));
    }
}

export class ArtistBrowse extends AbstractBrowse {
    /** @type {Artist} */
    artist;

    /**
     * @param {Artist} artist
     */
    constructor(artist) {
        super(gettext("Artist: ") + artist.name);
        this.artist = artist;
    }

    async render() {
        const tracks = await music.filter({ artist: this.artist.name, order: 'year_desc,number,title' });
        BROWSE_CONTENT.replaceChildren(...getArtistHTML(this.artist, tracks));
    }
}

export class AlbumBrowse extends AbstractBrowse {
    /** @type {Album} */
    album;

    /**
     * @param {Album} album
     */
    constructor(album) {
        const title = gettext("Album: ") + (album.artist === null ? '' : album.artist + ' - ') + album.name;
        super(title);
        this.album = album;
    }

    async render() {
        /** @type {import("../types.js").FilterJson} */
        const filters = { album: this.album.name, order: 'number,title' };
        if (this.album.artist) {
            filters.album_artist = this.album.artist;
        }
        const tracks = await music.filter(filters);
        BROWSE_CONTENT.replaceChildren(getAlbumHTML(this.album, tracks));
    }
}

export class TagBrowse extends TracksBrowse {
    /**
     * @param {string} tagName
     */
    constructor(tagName) {
        super(gettext("Tag: ") + tagName, { tag: tagName });
    }
}

export class PlaylistBrowse extends LazyTracksBrowse {
    /**
     * @param {Playlist} playlist
     */
    constructor(playlist) {
        super(gettext("Playlist: ") + playlist.name, { playlist: playlist.name, order: 'ctime_desc' }, playlist.trackCount);
    }
}

export class YearBrowse extends TracksBrowse {
    /**
     * @param {number} year
     */
    constructor(year) {
        super(gettext("Year: ") + year, { year: year, order: 'title' });
    }
}

export class TitleBrowse extends TracksBrowse {
    /**
     * @param {string} title
     */
    constructor(title) {
        super(gettext("Title: ") + title, { title: title, order: 'ctime_asc' });
    }
}

export class RecentlyAddedBrowse extends TracksBrowse {
    constructor() {
        super(gettext("Recently added"), { order: "ctime_desc", limit: 100 });
    }
}

export class RecentlyReleasedBrowse extends TracksBrowse {
    constructor() {
        super(gettext("Recently released"), { order: "year_desc", limit: 100 });
    }
}

export class RandomBrowse extends TracksBrowse {
    constructor() {
        super(gettext("Random"), { order: "random", limit: 100 });
    }
}

export class MissingMetadataBrowse extends TracksBrowse {
    constructor() {
        super(gettext("Missing metadata"), { has_metadata: "0", order: "random", limit: 100 });
    }
}

const history = /** @type {Array<AbstractBrowse>} */ ([]);
let current = /** @type {AbstractBrowse | null} */ (null);
const allButton = /** @type {HTMLButtonElement} */ (document.getElementById('browse-all'));
const backButton = /** @type {HTMLButtonElement} */ (document.getElementById('browse-back'));

/**
 * @param {string} textContent
 */
function setHeader(textContent) {
    const browseWindow = /** @type {HTMLDivElement} */ (document.getElementById('window-browse'));
    browseWindow.getElementsByTagName('h2')[0].textContent = textContent;
};

function back() {
    const last = history.pop();
    if (last) {
        current = last;
        updateContent();
    }
};

async function updateContent() {
    if (!current) {
        throw new Error("current is null");
    }
    console.debug('browse:', current);

    setHeader(current.title);
    await current.render();

    backButton.disabled = history.length == 0;
}

/**
 * @param {AbstractBrowse} nextBrowse
 */
export async function browse(nextBrowse) {
    if (current != null) {
        history.push(current);
    }
    current = nextBrowse;
    await updateContent();
    windows.open('window-browse');
};

// Button to open browse window
allButton.addEventListener('click', () => browse(new HomeBrowse()));

// Back button in top left corner of browse window
backButton.addEventListener('click', () => back());

eventBus.subscribe(MusicEvent.METADATA_CHANGE, () => {
    if (!windows.isOpen('window-browse')) {
        console.debug('browse: ignore METADATA_CHANGE, browse window is not open. Is editor open: ', windows.isOpen('window-editor'));
        return;
    }

    console.debug('browse: received METADATA_CHANGE, updating content');
    updateContent();
});
