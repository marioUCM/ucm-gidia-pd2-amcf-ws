document.addEventListener('DOMContentLoaded', () => {
    // Función para cargar zonas basado en el distrito seleccionado
    function loadZones(boroughSelect, zoneSelect) {
        const selectedBorough = boroughSelect.value;
        const currentZoneValue = zoneSelect.value; // Guardamos el valor actual (si viene del POST)
        
        zoneSelect.innerHTML = '<option value="">Selecciona zona</option>';
        
        if (selectedBorough && window.zonesByBorough[selectedBorough]) {
            window.zonesByBorough[selectedBorough].sort().forEach(zone => {
                const option = document.createElement('option');
                option.value = zone;
                option.textContent = zone;
                // Si la zona coincide con la que el usuario seleccionó antes del POST, la marcamos
                if (zone === currentZoneValue) {
                    option.selected = true;
                }
                zoneSelect.appendChild(option);
            });
            zoneSelect.disabled = false;
        } else {
            zoneSelect.disabled = true;
        }
    }
    
    // Configurar todos los selects de distrito
    document.querySelectorAll('.borough-select').forEach(boroughSelect => {
        const container = boroughSelect.closest('.location-box');
        // Usamos la clase para no liarnos con los names (soluciona el bug del Taxi)
        const zoneSelect = container.querySelector('.zone-select');
        
        // Cargar zonas iniciales si hay un valor seleccionado
        if (boroughSelect.value) {
            loadZones(boroughSelect, zoneSelect);
        } else {
            zoneSelect.disabled = true;
        }
        
        // Evento change
        boroughSelect.addEventListener('change', function() {
            loadZones(boroughSelect, zoneSelect);
        });
    });
    
    // Scroll a resultados si existen
    const resultVtc = document.getElementById('result-vtc');
    const resultMax = document.getElementById('result-max');
    if (resultVtc) resultVtc.scrollIntoView({ behavior: 'smooth', block: 'center' });
    if (resultMax) resultMax.scrollIntoView({ behavior: 'smooth', block: 'center' });
    
    // Preservar valores seleccionados después del submit
    // Para VTC
    const vtcForm = document.getElementById('form-vtc');
    if (vtcForm) {
        const vtcBoroughOrigen = vtcForm.querySelector('[name="PUborough"]');
        const vtcZoneOrigen = vtcForm.querySelector('[name="PUzone"]');
        const vtcBoroughDestino = vtcForm.querySelector('[name="DOborough"]');
        const vtcZoneDestino = vtcForm.querySelector('[name="DOzone"]');
        
        if (vtcBoroughOrigen && vtcBoroughOrigen.value && vtcZoneOrigen) {
            loadZones(vtcBoroughOrigen, vtcZoneOrigen);
        }
        if (vtcBoroughDestino && vtcBoroughDestino.value && vtcZoneDestino) {
            loadZones(vtcBoroughDestino, vtcZoneDestino);
        }
    }
    
    // Para Taxi
    const taxiForm = document.getElementById('form-taxi');
    if (taxiForm) {
        const taxiBoroughOrigen = taxiForm.querySelector('[name="PUborough"]');
        const taxiZoneOrigen = taxiForm.querySelector('[name="PUzone"]');
        
        if (taxiBoroughOrigen && taxiBoroughOrigen.value && taxiZoneOrigen) {
            loadZones(taxiBoroughOrigen, taxiZoneOrigen);
        }
    }
});