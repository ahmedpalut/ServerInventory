const searchSettingsBtn = document.getElementById("searchSettingsBtn");
const searchSettingsOverlay = document.getElementById("searchSettingsOverlay");
const searchSettingsPanel = document.getElementById("searchSettingsPanel");
const closeSearchSettings = document.getElementById("closeSearchSettings");
const selectAllBtn = document.getElementById("selectAllBtn");
const clearAllBtn = document.getElementById("clearAllBtn");
const searchBtn = document.getElementById("searchBtn");

const searchInput = document.getElementById("searchInput");
const searchActive = window.location.pathname === "/logs/search";

if (searchBtn) {
    searchBtn.onclick = function (e) {
        if (searchActive || window.location.pathname === "/logs/search") {
            e.preventDefault();
            window.location.href = "/logs";
            return;
        }

        const query = searchInput ? searchInput.value.trim() : "";
        if (!query) {
            e.preventDefault();
            return;
        }

        const checkedFields = document.querySelectorAll('input[name="fields"]:checked');
        if (checkedFields.length === 0) {
            e.preventDefault();
            alert("Lütfen en az bir arama alanı seçin.");
            return;
        }
    };
}


if (searchSettingsBtn) {

    searchSettingsBtn.onclick = function () {

        searchSettingsOverlay.style.display = "flex";

        document.body.classList.add("modal-open");

    };

}


if (closeSearchSettings) {

    closeSearchSettings.onclick = function () {

        searchSettingsOverlay.style.display = "none";

        document.body.classList.remove("modal-open");

    };

}


if (searchSettingsOverlay) {

    searchSettingsOverlay.onclick = function () {

        searchSettingsOverlay.style.display = "none";

        document.body.classList.remove("modal-open");

    };

}


if (searchSettingsPanel) {

    searchSettingsPanel.onclick = function (e) {

        e.stopPropagation();

    };

}


if (selectAllBtn) {

    selectAllBtn.onclick = function () {

        document
            .querySelectorAll('input[name="fields"]')
            .forEach(box => {
                box.checked = true;
            });

    };

}


if (clearAllBtn) {

    clearAllBtn.onclick = function () {

        document
            .querySelectorAll('input[name="fields"]')
            .forEach(box => {
                box.checked = false;
            });

    };

}