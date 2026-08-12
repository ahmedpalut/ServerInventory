const dbSettingsButton = document.getElementById("dbSettingsButton");
const databaseSettingsPanel = document.getElementById("databaseSettingsPanel");
const closeDbSettings = document.getElementById("closeDbSettings");
const databaseFile = document.getElementById("database_file");
const selectedFile = document.getElementById("selected_file");
const restoreBtn = document.getElementById("restoreBtn");
const dbPanelOverlay = document.getElementById("databasePanelOverlay");


function openDatabasePanel() {
    dbPanelOverlay.classList.toggle("active");
}


if (databaseSettingsPanel) {
    databaseSettingsPanel.onclick = function(e) {
        e.stopPropagation();
    };
}


if (dbSettingsButton) {
    dbSettingsButton.addEventListener("click", function () {
        openDatabasePanel();
    });
}


if (closeDbSettings) {
    closeDbSettings.addEventListener("click", function () {
        dbPanelOverlay.classList.remove("active");
    });
}


if (dbPanelOverlay) {
    dbPanelOverlay.addEventListener("click", function (e) {
        if (e.target === dbPanelOverlay) {
            dbPanelOverlay.classList.remove("active");
        }
    });
}


if (databaseFile) {
    databaseFile.addEventListener("change", function () {

        if (this.files.length > 0) {
            selectedFile.textContent = this.files[0].name;
            restoreBtn.style.display = "flex";
        } else {
            selectedFile.textContent = "";
            restoreBtn.style.display = "none";
        }

    });
}