<!-- problem_detail.html -->
{% load static %}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ problem.title }}</title>
    <!-- CodeMirror CDN -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.8/codemirror.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.8/theme/dracula.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.8/codemirror.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.8/mode/python/python.min.js"></script>
    <style>
        .editor-container {
            display: flex;
            justify-content: space-between;
        }
        .editor, .problem-details {
            width: 48%;
            padding: 10px;
            box-sizing: border-box;
        }
        .editor {
            border: 1px solid #ccc;
        }
        .problem-details {
            border: 1px solid #ddd;
            background-color: #f9f9f9;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>{{ problem.title }}</h1>
        <div class="editor-container">
            <div class="problem-details">
                <h2>Problem Description</h2>
                <p>{{ problem.description }}</p>
                <h2>Test Cases</h2>
                <h3>Input</h3>
                <pre>{{ problem.testcase_input }}</pre>
                <h3>Output</h3>
                <pre>{{ problem.testcase_output }}</pre>
                <h2>Constraints</h2>
                <p>{{ problem.constraints }}</p>
            </div>
            <div class="editor">
                <textarea id="code-editor" name="code" placeholder="Write your code here..."></textarea>
                <button id="run-code">Run</button>
                <button id="submit-code">Submit</button>
            </div>
        </div>
        <a href="{% url 'solve_problem' %}">Back to Problems List</a>
    </div>
    <script>
        document.addEventListener('DOMContentLoaded', () => {
            // Initialize CodeMirror
            const editor = CodeMirror.fromTextArea(document.getElementById('code-editor'), {
                lineNumbers: true,
                mode: 'python', // Change mode according to your needs
                theme: 'dracula'
            });

            document.getElementById('run-code').addEventListener('click', () => {
                const code = editor.getValue();
                fetch('{% url "execute_code" %}', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': '{{ csrf_token }}'
                    },
                    body: JSON.stringify({ code: code })
                })
                .then(response => response.json())
                .then(data => {
                    alert('Output: ' + data.output);
                })
                .catch(error => {
                    console.error('Error:', error);
                });
            });

            document.getElementById('submit-code').addEventListener('click', () => {
                const code = editor.getValue();
                fetch('{% url "submit_code" %}', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': '{{ csrf_token }}'
                    },
                    body: JSON.stringify({ code: code })
                })
                .then(response => response.json())
                .then(data => {
                    alert('Submission successful: ' + data.message);
                })
                .catch(error => {
                    console.error('Error:', error);
                });
            });
        });
    </script>
</body>
</html>
