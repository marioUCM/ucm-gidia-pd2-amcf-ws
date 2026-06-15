function boostmobilityPlotSlot(slotId) {
    var wrap = document.getElementById(slotId);
    if (!wrap) return null;
    return wrap.querySelector('.plotly-graph-div') || wrap;
}

document.getElementById('btn-update').addEventListener('click', function () {
    const nValue = document.getElementById('input-topN').value;
    const btn = this;

    btn.innerText = 'Cargando...';
    btn.disabled = true;

    fetch('/economico/update-graph', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ top_n: nValue }),
    })
        .then(function (response) {
            return response.json();
        })
        .then(function (data) {
            const graph1Data = JSON.parse(data.updt_g1);
            const graph2Data = JSON.parse(data.updt_g2);
            const graph3Data = JSON.parse(data.updt_g3);

            const g1 = boostmobilityPlotSlot('container-g1');
            const g2 = boostmobilityPlotSlot('container-g2');
            const g3 = boostmobilityPlotSlot('container-g3');

            const p1 = g1 ? Plotly.react(g1, graph1Data.data, graph1Data.layout) : Promise.resolve();
            const p2 = g2 ? Plotly.react(g2, graph2Data.data, graph2Data.layout) : Promise.resolve();
            const p3 = g3 ? Plotly.react(g3, graph3Data.data, graph3Data.layout) : Promise.resolve();

            return Promise.all([p1, p2, p3]);
        })
        .then(function () {
            if (window.boostmobilityResizeAllPlots) window.boostmobilityResizeAllPlots();
            btn.innerText = 'Actualizar gráficas';
            btn.disabled = false;
        })
        .catch(function (error) {
            console.error('Error:', error);
            btn.innerText = 'Error';
            btn.disabled = false;
        });
});
