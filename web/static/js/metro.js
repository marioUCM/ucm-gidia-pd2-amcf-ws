document.addEventListener('DOMContentLoaded', function () {
    const toggleButton = document.querySelector('[data-view-toggle]');
    const gridView = document.querySelector('[data-group-view="grid"]');
    const focusView = document.querySelector('[data-group-view="focus"]');
    const cards = Array.from(document.querySelectorAll('[data-focus-card]'));
    const prevButton = document.querySelector('[data-carousel-prev]');
    const nextButton = document.querySelector('[data-carousel-next]');
    const currentCounter = document.querySelector('[data-carousel-current]');
    const mapFrame = document.querySelector('.metro-map-frame');
    const mapSection = document.querySelector('#metro-prediction-map');
    const mapRows = Array.from(document.querySelectorAll('[data-map-line]'));
    const clearMapButton = document.querySelector('[data-map-clear]');
    const mapSelectionLabel = document.querySelector('[data-map-selection-label]');

    if (!toggleButton || !gridView || !focusView || cards.length === 0) {
        return;
    }

    let activeIndex = 0;
    let activeView = 'grid';
    let activeMapLine = null;
    let pendingMapLine = null;

    function renderCarousel() {
        cards.forEach(function (card, index) {
            const isActive = index === activeIndex;
            card.hidden = !isActive;
            card.classList.toggle('is-active', isActive);
        });

        if (currentCounter) {
            currentCounter.textContent = String(activeIndex + 1);
        }
    }

    function setView(nextView) {
        activeView = nextView;
        const showingFocus = nextView === 'focus';
        gridView.hidden = showingFocus;
        focusView.hidden = !showingFocus;
        toggleButton.textContent = showingFocus ? 'Volver a mosaico' : 'Ver vista guiada';
        toggleButton.setAttribute('aria-pressed', showingFocus ? 'true' : 'false');
    }

    function moveCarousel(step) {
        activeIndex = (activeIndex + step + cards.length) % cards.length;
        renderCarousel();
    }

    function setRowSelection(lineId) {
        mapRows.forEach(function (row) {
            row.classList.toggle('is-map-selected', !!lineId && row.dataset.mapLine === lineId);
        });
    }

    function syncMapSelectionUi(lineId) {
        activeMapLine = lineId || null;
        setRowSelection(activeMapLine);

        if (clearMapButton) {
            clearMapButton.hidden = !activeMapLine;
        }

        if (mapSelectionLabel) {
            mapSelectionLabel.textContent = activeMapLine ? 'Línea ' + activeMapLine : 'Línea seleccionada';
        }
    }

    function postMapSelection(lineId) {
        if (!mapFrame || !mapFrame.contentWindow) {
            return;
        }

        mapFrame.contentWindow.postMessage(
            {
                type: 'metro-map-focus-line',
                lineId: lineId || null
            },
            window.location.origin
        );
    }

    function setMapSelection(lineId) {
        pendingMapLine = lineId || null;
        syncMapSelectionUi(pendingMapLine);
        postMapSelection(activeMapLine);
    }

    function focusMapLine(lineId) {
        if (mapSection) {
            mapSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }

        window.setTimeout(function () {
            setMapSelection(lineId);
        }, 240);
    }

    toggleButton.addEventListener('click', function () {
        setView(activeView === 'grid' ? 'focus' : 'grid');
    });

    if (prevButton) {
        prevButton.addEventListener('click', function () {
            moveCarousel(-1);
        });
    }

    if (nextButton) {
        nextButton.addEventListener('click', function () {
            moveCarousel(1);
        });
    }

    mapRows.forEach(function (row) {
        row.addEventListener('click', function () {
            focusMapLine(row.dataset.mapLine);
        });

        row.addEventListener('keydown', function (event) {
            if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                focusMapLine(row.dataset.mapLine);
            }
        });
    });

    if (clearMapButton) {
        clearMapButton.addEventListener('click', function () {
            setMapSelection(null);
        });
    }

    if (mapFrame) {
        mapFrame.addEventListener('load', function () {
            if (pendingMapLine !== null) {
                window.setTimeout(function () {
                    postMapSelection(pendingMapLine);
                }, 180);
            }
        });
    }

    window.addEventListener('message', function (event) {
        const data = event && event.data ? event.data : null;
        if (!data || data.type !== 'metro-map-selection-changed') {
            return;
        }

        syncMapSelectionUi(data.lineId || null);
    });

    renderCarousel();
    setView('grid');
})
