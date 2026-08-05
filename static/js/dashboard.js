function downloadPDF() {
    const element = document.body;
    const opt = {
        margin: 5,
        filename: 'Sunucu_Envanter_Raporu.pdf',
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2, useCORS: true },
        jsPDF: { unit: 'mm', format: 'a3', orientation: 'landscape' }
    };
    html2pdf().set(opt).from(element).save();
}