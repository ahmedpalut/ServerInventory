
const dbSettingsButton = document.getElementById("dbSettingsButton");
const databaseSettingsPanel = document.getElementById("databaseSettingsPanel");
const closeDbSettings = document.getElementById("closeDbSettings");
const databaseFile = document.getElementById("database_file");
const selectedFile = document.getElementById("selected_file");
const restoreBtn = document.getElementById("restoreBtn");

function openDatabasePanel(){
    databaseSettingsPanel.classList.toggle("active");
}

closeDbSettings.addEventListener("click", function () {
    databaseSettingsPanel.classList.remove("active");
});



databaseFile.addEventListener("change", function () {
    if (this.files.length > 0) {
        selectedFile.textContent = this.files[0].name;
        restoreBtn.style.display = "flex";
    } else {
        selectedFile.textContent = "";
        restoreBtn.style.display = "none";
    }
});