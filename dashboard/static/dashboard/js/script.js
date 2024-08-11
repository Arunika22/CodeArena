document.addEventListener("DOMContentLoaded", function() {
    var editor = CodeMirror.fromTextArea(document.getElementById('code-editor'), {
        mode: 'text/x-c++src',
        theme: 'dracula',
        lineNumbers: true,
        matchBrackets: true,
        autoCloseBrackets: true,
    });

    document.getElementById("compile-button").onclick = function() {
        submitCode();
    };
});

function submitCode() {
    const code = document.querySelector('#code-editor').value;
    const input = document.querySelector('textarea[name="input"]').value;

    console.log('Code:', code);
    console.log('Input:', input);

    const formData = new FormData();
    formData.append('code', code);
    formData.append('input', input);

    fetch('/compiler/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken(),
        },
        body: formData,
    })
    .then(response => response.json())
    .then(result => {
        document.getElementById('results').style.display = 'block';
        if (result.error) {
            document.getElementById('errors').textContent = result.error;
        } else {
            document.getElementById('output').textContent = result.output || 'No output';
            document.getElementById('errors').textContent = result.errors || 'No errors';
            document.getElementById('execution-time').textContent = `Execution Time: ${result.execution_time || 'N/A'} ms`;
            document.getElementById('memory-usage').textContent = `Memory Usage: ${result.memory_usage || 'N/A'} KB`;
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}


function getCSRFToken() {
    let cookieValue = null;
    const name = 'csrftoken';
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
