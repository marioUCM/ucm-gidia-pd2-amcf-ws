document.getElementById('btn-update').addEventListener('click', function() {
    const nValue = document.getElementById('input-topN').value;
    const btn = this;

    btn.innerText = "Cargando...";
    btn.disabled = true;

    fetch('/economico/update-graph', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ top_n: nValue })
    })
    .then(response => response.json())
    .then(data => {
        // 1. Transformamos el texto JSON a un objeto de JavaScript
        const graph1Data = JSON.parse(data.updt_g1);
        const graph2Data = JSON.parse(data.updt_g2);
        const graph3Data = JSON.parse(data.updt_g3);
        
        // 2. Usamos Plotly para repintar las gráficas en los divs correspondientes
        Plotly.react('container-g1', graph1Data.data, graph1Data.layout);
        Plotly.react('container-g2', graph2Data.data, graph2Data.layout);
        Plotly.react('container-g3', graph3Data.data, graph3Data.layout);

        btn.innerText = "Actualizar Gráficas";
        btn.disabled = false;
    })
    .catch(error => {
        console.error('Error:', error);
        btn.innerText = "Error";
        btn.disabled = false; // Importante reactivarlo si hay error
    });
});