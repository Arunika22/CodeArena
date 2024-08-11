document.addEventListener('DOMContentLoaded', () => {
    const addTestCaseButton = document.getElementById('add-test-case');
    const testCaseContainer = document.getElementById('test-case-container');

    addTestCaseButton.addEventListener('click', () => {
        const index = document.querySelectorAll('#test-case-container .test-case').length + 1;
        const testCaseHTML = `
            <div class="test-case">
                <label for="input-${index}">Input:</label>
                <textarea id="input-${index}" name="test_case_input[]" required></textarea>
                <label for="output-${index}">Output:</label>
                <textarea id="output-${index}" name="test_case_output[]" required></textarea>
                <button type="button" class="delete-test-case">Delete</button>
            </div>
        `;
        testCaseContainer.insertAdjacentHTML('beforeend', testCaseHTML);
    });

    testCaseContainer.addEventListener('click', (event) => {
        if (event.target.classList.contains('delete-test-case')) {
            event.target.parentElement.remove();
        }
    });
});
