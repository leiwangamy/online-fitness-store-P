// Auto-hide and auto-show fields in Django Admin for Product

window.addEventListener("load", function () {
    const isServiceCheckbox = document.querySelector("#id_is_service");
    const isDigitalCheckbox = document.querySelector("#id_is_digital");
    const stockField = document.querySelector("#id_quantity_in_stock").closest(".form-row");
    const serviceAvailabilityRow = document.querySelector("#id_service_availability")?.closest(".form-row");
    const serviceSeatsRow = document.querySelector("#id_service_seats")?.closest(".form-row");

    function updateVisibility() {
        const isService = isServiceCheckbox?.checked;
        const isDigital = isDigitalCheckbox?.checked;

        // --- Logic ---

        // 1. SERVICE PRODUCT → hide quantity, show service fields
        if (isService) {
            if (stockField) stockField.style.display = "none";
            if (serviceAvailabilityRow) serviceAvailabilityRow.style.display = "block";
            
            const availability = document.querySelector("#id_service_availability").value;
            if (availability === "limited") {
                if (serviceSeatsRow) serviceSeatsRow.style.display = "block";
            } else {
                if (serviceSeatsRow) serviceSeatsRow.style.display = "none";
            }
        }

        // 2. DIGITAL PRODUCT → hide quantity, hide service fields
        else if (isDigital) {
            if (stockField) stockField.style.display = "none";
            if (serviceAvailabilityRow) serviceAvailabilityRow.style.display = "none";
            if (serviceSeatsRow) serviceSeatsRow.style.display = "none";
        }

        // 3. PHYSICAL PRODUCT → show stock, hide service
        else {
            if (stockField) stockField.style.display = "block";
            if (serviceAvailabilityRow) serviceAvailabilityRow.style.display = "none";
            if (serviceSeatsRow) serviceSeatsRow.style.display = "none";
        }
    }

    // Event listeners
    isServiceCheckbox?.addEventListener("change", updateVisibility);
    isDigitalCheckbox?.addEventListener("change", updateVisibility);

    const availabilitySelect = document.querySelector("#id_service_availability");
    availabilitySelect?.addEventListener("change", updateVisibility);

    // Initial load
    updateVisibility();
});
