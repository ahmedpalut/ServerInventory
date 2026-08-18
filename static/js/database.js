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

function loadBackupSettings(updateToggle = false) {
    fetch("/api/backup/settings")
        .then(res => res.json())
        .then(data => {
            if (data.success && data.settings) {
                const s = data.settings;
                const isEnabled = Boolean(s.is_enabled);

                if (updateToggle) {
                    if (autoBackupToggle) autoBackupToggle.checked = isEnabled;
                    const settingsBtn = document.getElementById("autoBackupSettingsBtn");
                    if (settingsBtn) settingsBtn.style.display = isEnabled ? "flex" : "none";
                }

                const freqEl = document.getElementById("backupFrequency");
                if (freqEl) freqEl.value = s.frequency || "daily";
                const dayEl = document.getElementById("backupDay");
                if (dayEl) dayEl.value = s.backup_day || "mon";
                const dayGroup = document.getElementById("backupDayGroup");
                if (dayGroup) dayGroup.style.display = (freqEl && freqEl.value === "weekly") ? "block" : "none";

                const timeEl = document.getElementById("backupTime");
                if (timeEl) timeEl.value = s.backup_time || "03:00";
                const folderEl = document.getElementById("backupFolder");
                if (folderEl) folderEl.value = s.backup_folder || "";
                const maxEl = document.getElementById("maxBackupCount");
                if (maxEl) maxEl.value = s.max_backup_count || 10;
                const delEl = document.getElementById("deleteOldBackups");
                if (delEl) delEl.checked = Boolean(s.delete_old_backups);

                const lastBackupEl = document.getElementById("lastBackupDisplay");
                const statusEl = document.getElementById("lastBackupStatusDisplay");
                if (lastBackupEl) {
                    if (s.last_backup_date) {
                        lastBackupEl.textContent = "📅 Son Yedekleme: " + s.last_backup_date;
                    } else {
                        lastBackupEl.textContent = "📅 Son Yedekleme: Henüz yapılmadı";
                    }
                }
                if (statusEl) {
                    if (s.last_backup_status) {
                        statusEl.textContent = "📌 Durum: " + s.last_backup_status;
                        statusEl.style.color = s.last_backup_status.startsWith("Error") ? "#ef4444" : "#22c55e";
                    } else {
                        statusEl.textContent = "";
                    }
                }
            }
        })
        .catch(err => console.error("Yedekleme ayarları yüklenemedi:", err));
}

function openAutoBackupPanel() {
    document.body.classList.add("modal-open");
    loadBackupSettings(false);
    const panel = document.getElementById("autoBackupPanel");
    const overlay = document.getElementById("autoBackupOverlay");

    if (panel) {
        panel.style.right = "0";
    }
    if (overlay) {
        overlay.style.display = "block";
    }
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
}

if (autoBackupToggle) {
    autoBackupToggle.addEventListener("change", function () {
        const settingsBtn = document.getElementById("autoBackupSettingsBtn");
        const isChecked = this.checked;

        if (settingsBtn) {
            settingsBtn.style.display = isChecked ? "flex" : "none";
        }

        const payload = {
            is_enabled: isChecked,
            frequency: document.getElementById("backupFrequency") ? document.getElementById("backupFrequency").value : "daily",
            backup_day: document.getElementById("backupDay") ? document.getElementById("backupDay").value : "mon",
            backup_time: document.getElementById("backupTime") ? document.getElementById("backupTime").value : "03:00",
            backup_folder: document.getElementById("backupFolder") ? document.getElementById("backupFolder").value : "",
            max_backup_count: document.getElementById("maxBackupCount") ? document.getElementById("maxBackupCount").value : 10,
            delete_old_backups: document.getElementById("deleteOldBackups") ? document.getElementById("deleteOldBackups").checked : true
        };

        fetch("/api/backup/settings", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        })
        .then(res => res.json())
        .then(data => {
            if (!isChecked) {
                closeAutoBackupPanel();
            }
        })
        .catch(err => console.error("Yedekleme durumu güncellenemedi:", err));
    });
}

if (closeAutoBackup) {
    closeAutoBackup.addEventListener("click", function () {
        closeAutoBackupPanel();
    });
}

if (autoBackupOverlay) {
    autoBackupOverlay.addEventListener("click", function () {
        closeAutoBackupPanel();
    });
}

const selectBackupFolderBtn = document.getElementById("selectBackupFolder");
if (selectBackupFolderBtn) {
    selectBackupFolderBtn.addEventListener("click", function () {
        const folderInput = document.getElementById("backupFolder");
        fetch("/api/backup/select-folder", {
            method: "POST"
        })
        .then(res => res.json())
        .then(data => {
            if (data.success && data.folder && folderInput) {
                folderInput.value = data.folder;
            }
        })
        .catch(err => {
            console.error("Klasör seçici hatası:", err);
            const currentPath = folderInput ? folderInput.value : "";
            const choice = prompt("Yedeklerin kaydedileceği klasör yolunu girin:", currentPath || "C:\\ServerInventoryBackups");
            if (choice !== null && folderInput) {
                folderInput.value = choice.trim();
            }
        });
    });
}

const backupFrequencyEl = document.getElementById("backupFrequency");
if (backupFrequencyEl) {
    backupFrequencyEl.addEventListener("change", function () {
        const dayGroup = document.getElementById("backupDayGroup");
        if (dayGroup) {
            dayGroup.style.display = this.value === "weekly" ? "block" : "none";
        }
    });
}

function performSaveBackupSettings() {
    if (autoBackupToggle) {
        autoBackupToggle.checked = true;
    }
    const settingsBtn = document.getElementById("autoBackupSettingsBtn");
    if (settingsBtn) {
        settingsBtn.style.display = "flex";
    }

    const payload = {
        is_enabled: true,
        frequency: document.getElementById("backupFrequency") ? document.getElementById("backupFrequency").value : "daily",
        backup_day: document.getElementById("backupDay") ? document.getElementById("backupDay").value : "mon",
        backup_time: document.getElementById("backupTime") ? document.getElementById("backupTime").value : "03:00",
        backup_folder: document.getElementById("backupFolder") ? document.getElementById("backupFolder").value : "",
        max_backup_count: document.getElementById("maxBackupCount") ? document.getElementById("maxBackupCount").value : 10,
        delete_old_backups: document.getElementById("deleteOldBackups") ? document.getElementById("deleteOldBackups").checked : true
    };

    fetch("/api/backup/settings", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            alert(data.message || "Yedekleme ayarları kaydedildi.");
            closeAutoBackupPanel();
            loadBackupSettings(true);
        } else {
            alert("Hata: " + (data.error || "Ayarlar kaydedilemedi."));
        }
    })
    .catch(err => {
        alert("İstek gönderilemedi: " + err);
    });
}

const saveAutoBackupBtn = document.getElementById("saveAutoBackupBtn");
if (saveAutoBackupBtn) {
    saveAutoBackupBtn.addEventListener("click", function () {
        performSaveBackupSettings();
    });
}

if (autoBackupForm) {
    autoBackupForm.addEventListener("submit", function (e) {
        e.preventDefault();
        performSaveBackupSettings();
    });
}

document.addEventListener("DOMContentLoaded", function () {
    loadBackupSettings(true);
});