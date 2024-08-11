document.addEventListener('DOMContentLoaded', () => {
    // Initialize CodeMirror editor
    const editor = CodeMirror.fromTextArea(document.getElementById('code-editor'), {
        mode: 'text/x-c++src',
        lineNumbers: true,
        autoCloseBrackets: true,
        matchBrackets: true,
        theme: 'default'
    });

    // Handle the Run button click
    document.getElementById('run-code').addEventListener('click', () => {
        const code = editor.getValue();
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        fetch(window.location.href, {  // Use the current URL for POST request
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ code: code })
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                return response.text().then(text => {
                    throw new Error(`Server responded with status ${response.status}: ${text}`);
                });
            }
        })
        .then(data => {
            document.getElementById('output').textContent = data.results ? data.results.join('\n') : 'No output';
            document.getElementById('error').textContent = data.errors ? data.errors.join('\n') : 'No errors';
        })
        .catch(error => {
            document.getElementById('error').textContent = `Error: ${error.message}`;
            console.error('Error:', error);
        });
    });
});
