function copyToClipboard(elementId) {
    const text = document.getElementById(elementId).getAttribute('data-full-text');
    const button = event.currentTarget;
    const originalContent = button.innerHTML;

    navigator.clipboard.writeText(text).then(() => {
        button.innerHTML = '&#x2705;&#xFE0E;'; 
        
        // setTimeout(() => {
        //     button.innerHTML = originalContent;
        // }, 700);
    }).catch(err => {
        console.error('Ошибка копирования: ', err);
    });
}
