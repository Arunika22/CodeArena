document.addEventListener('DOMContentLoaded', function() {
    var editor = CodeMirror(document.getElementById('cpp-editor'), {
        mode: 'text/x-c++src',
        lineNumbers: true,
        lineWrapping: true,
        theme: 'default',
        autoCloseBrackets: true,
        matchBrackets: true,
        value: ''
    });

    document.getElementById('run-code').addEventListener('click', function() {
        const code = editor.getValue();
        const userInput = document.getElementById('user-input') ? document.getElementById('user-input').value : '';
        document.getElementById('execution-time').textContent = '';
        document.getElementById('memory-usage').textContent = '';
        document.getElementById('performance-metrics').style.display = 'none';
        if (!code.trim()) {
            document.getElementById('output').textContent = 'Error: Code is empty.';
            return;
        }

        fetch('/compile_code/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrf-token')
            },
            body: JSON.stringify({ code: code, input: userInput })
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                return response.json().then(data => { throw data; });
            }
        })
        .then(data => {
            
            // let outputText = data.output || 'Compiled successfully with no output.';
            
            // if (data.errors) {
            //     outputText += `\nErrors:\n${data.errors}`;
            //     document.getElementById('performance-metrics').style.display = 'none';
            // } else {
            //     // Display performance metrics if available
            //     if (data.execution_time) {
            //         document.getElementById('performance-metrics').style.display = 'block';
            //         document.getElementById('execution-time').textContent = `Execution Time: ${data.execution_time} ms`;
            //     } else {
            //         document.getElementById('performance-metrics').style.display = 'none';
            //     }

            //     if (data.memory_usage) {
            //         document.getElementById('memory-usage').textContent = `Memory Usage: ${data.memory_usage} KB`;
            //     }
            // }

            // document.getElementById('output').textContent = outputText;
            let outputText = data.output || 'Compiled successfully with no output.';
            let metricsDisplay = 'none';

            if (data.errors) {
                outputText += `\nErrors:\n${data.errors}`;
            } else {
                if (data.execution_time && data.memory_usage) {
                    metricsDisplay = 'flex';
                    document.getElementById('execution-time').textContent = `Execution Time: ${data.execution_time.toFixed(2)} ms`;
                    document.getElementById('memory-usage').textContent = `Memory Usage: ${data.memory_usage.toFixed(0)} KB`;
                }
            }

            document.getElementById('performance-metrics').style.display = metricsDisplay;
            document.getElementById('output').textContent = outputText;
           
        })
        .catch(error => {
            document.getElementById('output').textContent = error.errors || `Error: ${error.message}`;
        });
    });

    function getCookie(name) {
        let cookieValue = null;
        const cookieElement = document.querySelector(`meta[name="${name}"]`);
        if (cookieElement) {
            cookieValue = cookieElement.getAttribute('content');
        }
        return cookieValue;
    }
});
