const deviceTypeSelect = document.getElementById("net_device_type");
const otherDeviceTypeContainer = document.getElementById("otherDeviceTypeContainer");
const otherDeviceTypeInput = document.getElementById("otherDeviceType");

deviceTypeSelect.addEventListener("change", function () {

    if (this.value === "Diğer") {
        otherDeviceTypeContainer.style.display = "block";
        otherDeviceTypeInput.required = true;
        otherDeviceTypeInput.focus();
    } else {
        otherDeviceTypeContainer.style.display = "none";
        otherDeviceTypeInput.required = false;
        otherDeviceTypeInput.value = "";
    }

});