document.addEventListener('DOMContentLoaded', function() {
    const scrapingTypeSelect = document.getElementById('scrapingType');
    const customSelectorGroup = document.querySelector('.custom-selector-group');
    const customSelectorInput = document.getElementById('customSelector');

    function toggleCustomSelector() {
        if (scrapingTypeSelect.value === 'custom') {
            customSelectorGroup.style.display = 'block';
            customSelectorInput.setAttribute('required', 'required');
        } else {
            customSelectorGroup.style.display = 'none';
            customSelectorInput.removeAttribute('required');
        }
    }

    
    scrapingTypeSelect.addEventListener('change', toggleCustomSelector);

    
    toggleCustomSelector();
});