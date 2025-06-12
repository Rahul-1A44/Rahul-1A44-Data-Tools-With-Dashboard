
document.addEventListener('DOMContentLoaded', function() {
    const printButton = document.querySelector('.btn-secondary-custom[onclick="window.print()"]');
    if (printButton) {
        printButton.addEventListener('click', function() {
            window.print();
        });
     
        printButton.removeAttribute('onclick');
    }

    const backButton = document.querySelector('.bottom-back-button-container .btn');
    if (backButton) {
        backButton.addEventListener('click', function() {
            history.back();
        });
       
        backButton.removeAttribute('onclick');
    }
});