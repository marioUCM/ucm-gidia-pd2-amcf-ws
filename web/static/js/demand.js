document.addEventListener("DOMContentLoaded", function () {

    const zonesByBorough = window.zonesByBorough;

    console.log("ZONES:", zonesByBorough);

    const boroughSelects = document.querySelectorAll(".borough-select");

    boroughSelects.forEach((boroughSelect) => {

        const container = boroughSelect.closest("form");

        const zoneSelect = container.querySelector(".zone-select");
        const dateInput = container.querySelector(".date-input");
        const hourSelect = container.querySelector(".hour-select");

        boroughSelect.addEventListener("change", function () {

            const selectedBorough = this.value;

            zoneSelect.innerHTML = '<option value="">Selecciona zona</option>';

            if (selectedBorough && zonesByBorough[selectedBorough]) {

                zoneSelect.disabled = false;
                dateInput.disabled = false;
                hourSelect.disabled = false;

                zonesByBorough[selectedBorough].forEach(zone => {
                    const option = document.createElement("option");
                    option.value = zone;
                    option.textContent = zone;
                    zoneSelect.appendChild(option);
                });

            } else {

                zoneSelect.disabled = true;
                dateInput.disabled = true;
                hourSelect.disabled = true;
            }
        });
    });
});