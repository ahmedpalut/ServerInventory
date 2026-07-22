let turkce = true;

document.getElementById("langButton").onclick = function () {

    if (turkce) {

        document.getElementById("title").innerHTML = "🖥️ Server Inventory";

        document.getElementById("card1").innerHTML = "Total Servers";
        document.getElementById("card2").innerHTML = "Windows Servers";
        document.getElementById("card3").innerHTML = "IT Inventory";

        document.getElementById("searchInput").placeholder = "🔍 Search Server...";

        document.getElementById("th1").innerHTML = "Server";
        document.getElementById("th2").innerHTML = "Disk Size (GB)";
        document.getElementById("th3").innerHTML = "Operating System";
        document.getElementById("th4").innerHTML = "RAM";
        document.getElementById("th5").innerHTML = "IP";
        document.getElementById("th6").innerHTML = "Description";
        document.getElementById("th7").innerHTML = "CPU";
        document.getElementById("th8").innerHTML = "Date";
        document.getElementById("th9").innerHTML = "Action";

        document.getElementById("searchSettingsBtn").innerHTML = "⚙️ Search Settings";
        document.getElementById("aramalabel").innerHTML = "Search Settings";
        if(window.location.pathname=="/search"){
            document.getElementById("searchBtn").innerHTML="⬅️ Back";
        }else{
            document.getElementById("searchBtn").innerHTML="🔍 Search";
        }
        document.getElementById("aranacakalan").innerHTML = "Searching Areas";

        document.getElementById("selectAllBtn").innerHTML = "Select All";
        document.getElementById("clearAllBtn").innerHTML = "Clear";

        document.getElementById("editSunucuDuzenle").innerHTML = "Edit Server";
        document.getElementById("esl1").innerHTML = "Server Name";
        document.getElementById("esl2").innerHTML = "Disk Size";
        document.getElementById("esl3").innerHTML = "Disk Size Type (GB/TB)";
        document.getElementById("esl4").innerHTML = "Operating System";
        document.getElementById("esl41").innerHTML = "Select Server";
        document.getElementById("esl42").innerHTML = "New";
        document.getElementById("yeniIsletim").placeholder="New operating system";
        document.getElementById("esl5").innerHTML = "Description";
        document.getElementById("esl6").innerHTML = "Date";

        document.getElementById("sl1").lastChild.textContent = "Server Name";
        document.getElementById("sl2").lastChild.textContent = "Operating System";
        document.getElementById("sl3").lastChild.textContent = "IP Adress";
        document.getElementById("sl4").lastChild.textContent = "Description";
        document.getElementById("sl5").lastChild.textContent = "Disk Size";
        document.getElementById("sl6").lastChild.textContent = "Date";

        document.getElementById("ssr1").lastChild.textContent = "Equals";
        document.getElementById("ssr2").lastChild.textContent = "Min (≥)";
        document.getElementById("ssr3").lastChild.textContent = "Max (≤)";

        document.getElementById("addBtn").innerHTML = "➕ Add Server";

        document.getElementById("tableSettingsBtn").innerHTML="⚙️ Table Settings";
        document.getElementById("ts1").lastChild.textContent="Server Name";
        document.getElementById("ts2").lastChild.textContent="Disk Size";
        document.getElementById("ts3").lastChild.textContent="Operating System";
        document.getElementById("ts6").lastChild.textContent="Description";
        document.getElementById("ts8").lastChild.textContent="Date";
        document.getElementById("tableLabel").innerHTML="Table Settings";

    }

    else {

        document.getElementById("title").innerHTML = "🖥️ Sunucu Envanteri";

        document.getElementById("card1").innerHTML = "Toplam Sunucu";
        document.getElementById("card2").innerHTML = "Windows Sunucu";
        document.getElementById("card3").innerHTML = "IT Envanteri";

        document.getElementById("searchInput").placeholder = "🔍 Sunucu Ara...";

        document.getElementById("th1").innerHTML = "Sunucu";
        document.getElementById("th2").innerHTML = "Disk Boyutu (GB)";
        document.getElementById("th3").innerHTML = "İşletim Sistemi";
        document.getElementById("th4").innerHTML = "RAM";
        document.getElementById("th5").innerHTML = "IP";
        document.getElementById("th6").innerHTML = "Açıklama";
        document.getElementById("th7").innerHTML = "CPU";
        document.getElementById("th8").innerHTML = "Tarih";
        document.getElementById("th9").innerHTML = "İşlem";

        document.getElementById("searchSettingsBtn").innerHTML = "⚙️ Arama Ayarları";
        document.getElementById("aramalabel").innerHTML = "Arama Ayarları";
        if(window.location.pathname=="/search"){
            document.getElementById("searchBtn").innerHTML="⬅️ Geri Dön";
        }else{
            document.getElementById("searchBtn").innerHTML="🔍 Ara";
        }
        document.getElementById("aranacakalan").innerHTML = "Aranacak Alanlar";

        document.getElementById("selectAllBtn").innerHTML = "Tümünü Seç";
        document.getElementById("clearAllBtn").innerHTML = "Temizle";

        document.getElementById("editSunucuDuzenle").innerHTML = "Sunucu Düzenle";
        document.getElementById("esl1").innerHTML = "Sunucu Adı";
        document.getElementById("esl2").innerHTML = "Disk Boyutu";
        document.getElementById("esl3").innerHTML = "Disk Boyut Türü (GB/TB)";
        document.getElementById("esl4").innerHTML = "İşletim Sistemi";
        document.getElementById("esl41").innerHTML = "Sunucu Seçin";
        document.getElementById("esl42").innerHTML = "Yeni";
        document.getElementById("yeniIsletim").placeholder="Yeni İşletim Sistemi";
        document.getElementById("esl5").innerHTML = "Açıklama";
        document.getElementById("esl6").innerHTML = "Tarih";

        document.getElementById("sl1").lastChild.textContent = "Sunucu Adı";
        document.getElementById("sl2").lastChild.textContent = "işletim Sistemi";
        document.getElementById("sl3").lastChild.textContent = "IP Adresi";
        document.getElementById("sl4").lastChild.textContent = "Açıklama";
        document.getElementById("sl5").lastChild.textContent = "Disk Boyutu";
        document.getElementById("sl6").lastChild.textContent = "Tarih";

        document.getElementById("ssr1").lastChild.textContent = "Tam Eşleşme";
        document.getElementById("ssr2").lastChild.textContent = "En az (≥)";
        document.getElementById("ssr3").lastChild.textContent = "En fazla (≤)";

        document.getElementById("addBtn").innerHTML = "➕ Yeni Sunucu";

        document.getElementById("tableSettingsBtn").innerHTML="⚙️ Tablo Ayarları";
        document.getElementById("ts1").lastChild.textContent="Sunucu Adı";
        document.getElementById("ts2").lastChild.textContent="Disk Boyutu";
        document.getElementById("ts3").lastChild.textContent="İşletim Sistemi";
        document.getElementById("ts6").lastChild.textContent="Açıklama";
        document.getElementById("ts8").lastChild.textContent="Tarih";
        document.getElementById("tableLabel").innerHTML="Tablo Ayarları";

    }

    turkce = !turkce;

};