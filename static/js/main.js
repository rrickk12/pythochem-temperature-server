// static/js/main.js

document.addEventListener('DOMContentLoaded', function () {
    console.log("main.js loaded.");

    // Retrieve all elements with the "editable" class.
    const editableElements = document.querySelectorAll('.editable');
    editableElements.forEach(el => {
        // Add an event listener for inline editing.
        el.addEventListener('click', function inlineEditHandler(event) {
            const currentText = el.innerText.trim();
            const mac = el.getAttribute('data-mac');
            // Create an input field to replace the current text.
            const input = document.createElement('input');
            input.type = 'text';
            input.value = currentText;
            input.className = 'form-control';
            el.parentNode.replaceChild(input, el);
            input.focus();

            // On blur, restore the text element with updated content.
            input.addEventListener('blur', function () {
                const newText = input.value.trim();
                const span = document.createElement('span');
                span.innerText = newText || "Unnamed Sensor";
                span.className = 'editable';
                span.setAttribute('data-mac', mac);
                input.parentNode.replaceChild(span, input);
                // Reattach the inline editing handler for future edits.
                span.addEventListener('click', inlineEditHandler);
            });
        });
    });
});
