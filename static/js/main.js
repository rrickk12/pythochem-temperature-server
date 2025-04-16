"use strict";

document.addEventListener('DOMContentLoaded', () => {
    console.log("main.js loaded.");

    document.querySelectorAll('.editable').forEach(el => {
        const inlineEditHandler = () => {
            const currentText = el.innerText.trim();
            const mac = el.getAttribute('data-mac');
            const input = document.createElement('input');
            input.type = 'text';
            input.value = currentText;
            input.className = 'form-control';
            el.parentNode.replaceChild(input, el);
            input.focus();

            input.addEventListener('blur', () => {
                const newText = input.value.trim();
                const span = document.createElement('span');
                span.innerText = newText || "Unnamed Sensor";
                span.className = 'editable';
                span.setAttribute('data-mac', mac);
                input.parentNode.replaceChild(span, input);
                // Reattach event listener for future editing.
                span.addEventListener('click', inlineEditHandler);
            });
        };

        el.addEventListener('click', inlineEditHandler);
    });
});
