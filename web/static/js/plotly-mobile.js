/**
 * Plotly en móvil: recalcula tamaño y márgenes al cargar, al rotar y al cambiar el viewport.
 * Los gráficos viven en un div interno (.plotly-graph-div), no en #container-g1.
 * Expone window.boostmobilityResizeAllPlots para llamarlo tras Plotly.react.
 */
(function () {
    function debounce(fn, ms) {
        var t;
        return function () {
            clearTimeout(t);
            t = setTimeout(fn, ms);
        };
    }

    function plotRoots() {
        var nodes = document.querySelectorAll('.site-main .plotly-graph-div.js-plotly-plot');
        if (nodes.length) return nodes;
        return document.querySelectorAll('.site-main .plotly-graph-div');
    }

    function hasPlot(el) {
        return !!(el && el._fullLayout);
    }

    function patchMargins(el) {
        if (typeof Plotly === 'undefined' || !hasPlot(el)) return;
        var w = window.innerWidth || document.documentElement.clientWidth;
        if (w > 560) return;
        try {
            Plotly.relayout(el, {
                autosize: true,
                margin: { l: 36, r: 6, t: 32, b: 36, pad: 0 },
            });
        } catch (e) {}
    }

    function resizeOne(el) {
        if (typeof Plotly === 'undefined' || !hasPlot(el)) return;
        try {
            Plotly.relayout(el, { autosize: true });
        } catch (e) {}
        patchMargins(el);
        try {
            Plotly.Plots.resize(el);
        } catch (e) {}
    }

    function resizeAll() {
        plotRoots().forEach(resizeOne);
    }

    var debounced = debounce(resizeAll, 100);

    document.addEventListener('DOMContentLoaded', function () {
        [0, 120, 350, 700].forEach(function (ms) {
            setTimeout(resizeAll, ms);
        });
    });

    window.addEventListener('orientationchange', function () {
        setTimeout(resizeAll, 280);
    });

    window.addEventListener('resize', debounced);

    if (window.visualViewport) {
        window.visualViewport.addEventListener('resize', debounced);
    }

    window.boostmobilityResizeAllPlots = resizeAll;
})();
