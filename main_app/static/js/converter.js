document.addEventListener('DOMContentLoaded', function() {
    const inputFormatSelect = document.getElementById('inputFormat');
    const inputTextAreaGroup = document.getElementById('inputTextAreaGroup');
    const inputFileGroup = document.getElementById('inputFileGroup');
    const inputTextArea = document.getElementById('inputData');
    const inputFile = document.getElementById('inputFile');
    const outputFormatSelect = document.getElementById('outputFormat');

    function toggleInputType() {
        const selectedFormat = inputFormatSelect.value;
        const textBasedFormats = ['json', 'yaml', 'text']; 
        const fileBasedFormats = ['pdf', 'xlsx', 'csv']; 

        if (fileBasedFormats.includes(selectedFormat)) {
            inputTextAreaGroup.style.display = 'none';
            inputFileGroup.style.display = 'block';
            inputTextArea.removeAttribute('required'); 
            inputFile.setAttribute('required', 'required'); 
        
            inputTextArea.value = ''; 
        } else if (textBasedFormats.includes(selectedFormat)) {
            inputTextAreaGroup.style.display = 'block';
            inputFileGroup.style.display = 'none';
            inputFile.removeAttribute('required'); 
            inputTextArea.setAttribute('required', 'required'); 
            
            inputFile.value = ''; // Clear file input when switching to text area
        } else {
            // Default to file input if something unexpected happens
            inputTextAreaGroup.style.display = 'none';
            inputFileGroup.style.display = 'block';
            inputTextArea.removeAttribute('required');
            inputFile.setAttribute('required', 'required');
            inputTextArea.value = '';
        }
    }

    // Trigger the function on page load to set initial state based on default select value
    inputFormatSelect.dispatchEvent(new Event('change'));

    // Add event listener for when the input format changes
    inputFormatSelect.addEventListener('change', toggleInputType);

    // --- Handle Download Text Button ---
    const downloadTextBtn = document.getElementById('downloadTextBtn');
    const convertedOutputPre = document.querySelector('.converted-output');

    if (downloadTextBtn && convertedOutputPre) {
        downloadTextBtn.addEventListener('click', function() {
            const data = convertedOutputPre.innerText;
            const outputFormat = outputFormatSelect.value;
            let filename = `converted_data`;
            let mimeType = 'text/plain';

         
            if (['json', 'yaml', 'csv', 'text'].includes(outputFormat)) {
                filename += `.${outputFormat}`;
                if (outputFormat === 'json') mimeType = 'application/json';
                else if (outputFormat === 'yaml') mimeType = 'application/x-yaml'; 
                else if (outputFormat === 'csv') mimeType = 'text/csv';
                else mimeType = 'text/plain';
            } else {
               
                filename += '.txt'; 
            }
            
            const blob = new Blob([data], { type: mimeType });
            const url = URL.createObjectURL(blob);
            
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        });
    }

    // --- Handle Edit Data Button ---
    const editDataBtn = document.getElementById('editDataBtn');
    
    if (editDataBtn && convertedOutputPre) {
        editDataBtn.addEventListener('click', function() {
            const dataToEdit = convertedOutputPre.innerText;
            const outputFormat = outputFormatSelect.value;

         
            inputTextArea.value = dataToEdit;
            inputFormatSelect.value = outputFormat;

            
            inputTextAreaGroup.style.display = 'block';
            inputFileGroup.style.display = 'none';
            inputFile.removeAttribute('required');
            inputTextArea.setAttribute('required', 'required');
            inputFile.value = ''; 

        
            window.scrollTo({
                top: document.querySelector('.converter-form').offsetTop,
                behavior: 'smooth'
            });

         
            const resultsSection = document.querySelector('.results-section');
            if (resultsSection) {
                resultsSection.remove();
            }

            alert('Converted data loaded into input for editing.');
        });
    }

    
});