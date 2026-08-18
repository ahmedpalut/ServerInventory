const dbSettingsButton = document.getElementById("dbSettingsButton");
const databaseSettingsPanel = document.getElementById("databaseSettingsPanel");
const closeDbSettings = document.getElementById("closeDbSettings");
const databaseFile = document.getElementById("database_file");
const selectedFile = document.getElementById("selected_file");
const restoreBtn = document.getElementById("restoreBtn");
const dbPanelOverlay = document.getElementById("databasePanelOverlay");
const connectDatabaseBtn = document.getElementById("connectDatabaseBtn");
const connectDatabaseOverlay = document.getElementById("connectDatabaseOverlay");
const connectDatabasePanel = document.getElementById("connectDatabasePanel");
const closeConnectDatabase = document.getElementById("closeConnectDatabase");
const autoBackupToggle = document.getElementById("autoBackupToggle");
const autoBackupOverlay = document.getElementById("autoBackupOverlay");
const autoBackupPanel = document.getElementById("autoBackupPanel");
const closeAutoBackup = document.getElementById("closeAutoBackup");
const autoBackupForm = document.getElementById("autoBackupForm");

if (connectDatabaseBtn) {
    connectDatabaseBtn.onclick = async function () {

        try {

            const response = await fetch("/mysql_service_status");
            const data = await response.json();

            if (!data.running) {
                window.location.href = "/database_service_warning";
                return;
            }

            connectDatabaseOverlay.style.display = "flex";
            document.body.classList.add("modal-open");

        } catch (error) {

            console.error("MySQL servis durumu kontrol edilemedi:", error);

            window.location.href = "/database_service_warning";
        }
    };
}

if (closeConnectDatabase) {
    closeConnectDatabase.onclick = function () {
        connectDatabaseOverlay.style.display = "none";
        document.body.classList.remove("modal-open");
    };
}

if (connectDatabaseOverlay) {
    connectDatabaseOverlay.onclick = function () {
        connectDatabaseOverlay.style.display = "none";
        document.body.classList.remove("modal-open");
    };
}

async function updateDatabaseConnectionButton() {

    if (!connectDatabaseBtn) return;

    try {

        const response = await fetch("/mysql_service_status");

        if (!response.ok) {
            throw new Error("MySQL servis durumu alınamadı.");
        }

        const data = await response.json();

        if (data.running) {
            connectDatabaseBtn.classList.remove("database-disabled");
        } else {
            connectDatabaseBtn.classList.add("database-disabled");
        }

    } catch (error) {

        console.error("MySQL servis durumu kontrol edilemedi:", error);

        connectDatabaseBtn.disabled = true;
        connectDatabaseBtn.classList.add("database-disabled");
    }
}

updateDatabaseConnectionButton();
setInterval(updateDatabaseConnectionButton, 3000);

if (connectDatabasePanel) {
    connectDatabasePanel.onclick = function (e) {
        e.stopPropagation();
    };
}

function openDatabasePanel() {
    dbPanelOverlay.classList.toggle("active");
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
            selectedFile.title = this.files[0].name;
            restoreBtn.style.display = "flex";
        } else {
            selectedFile.textContent = "";
            restoreBtn.style.display = "none";
        }

    });
}
if (autoBackupToggle) {
    autoBackupToggle.addEventListener("change", function () {

        if (this.checked) {

            document.body.classList.add("modal-open");

            const panel = document.getElementById("autoBackupPanel");
            const overlay = document.getElementById("autoBackupOverlay");

            if (panel) {
                panel.style.right = "0";
            }

            if (overlay) {
                overlay.style.display = "block";
            }

        } else {

            closeAutoBackupPanel();

        }

    });
}


function closeAutoBackupPanel() {

    document.body.classList.remove("modal-open");

    const panel = document.getElementById("autoBackupPanel");
    const overlay = document.getElementById("autoBackupOverlay");

    if (panel) {
        panel.style.right = "-100%";
    }

    if (overlay) {
        overlay.style.display = "none";
    }

    if (autoBackupToggle) {
        autoBackupToggle.checked = false;
    }
}


if (closeAutoBackup) {

    closeAutoBackup.addEventListener("click", function () {

        closeAutoBackupPanel();

    });

}


if (autoBackupOverlay) {

    autoBackupOverlay.addEventListener("click", function (e) {

        if (e.target === autoBackupOverlay) {

            closeAutoBackupPanel();

        }

    });

}


if (autoBackupToggle) {
    autoBackupToggle.addEventListener("change", function () {

        if (this.checked) {

            document.body.classList.add("modal-open");

            const panel = document.getElementById("autoBackupPanel");
            const overlay = document.getElementById("autoBackupOverlay");

            if (panel) {
                panel.style.right = "0";
            }

            if (overlay) {
                overlay.style.display = "block";
            }

        } else {

            closeAutoBackupPanel();

        }

    });
}


function closeAutoBackupPanel() {

    document.body.classList.remove("modal-open");

    const panel = document.getElementById("autoBackupPanel");
    const overlay = document.getElementById("autoBackupOverlay");

    if (panel) {
        panel.style.right = "-100%";
    }

    if (overlay) {
        overlay.style.display = "none";
    }

    if (autoBackupToggle) {
        autoBackupToggle.checked = false;
    }
}


if (closeAutoBackup) {

    closeAutoBackup.addEventListener("click", function () {

        closeAutoBackupPanel();

    });

}


if (autoBackupOverlay) {

    autoBackupOverlay.addEventListener("click", function (e) {

        if (e.target === autoBackupOverlay) {

            closeAutoBackupPanel();

        }

    });

}


if (autoBackupPanel) {

    autoBackupPanel.addEventListener("click", function (e) {

        e.stopPropagation();

    });

}


if (autoBackupForm) {

    autoBackupForm.addEventListener("submit", function (e) {

        e.preventDefault();

        closeAutoBackupPanel();

    });

}