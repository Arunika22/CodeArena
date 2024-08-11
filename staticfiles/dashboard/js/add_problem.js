// Function to add a new test case
document.getElementById('add-test-case').addEventListener('click', function() {
    var testCaseContainer = document.getElementById('test-case-container');
    var newTestCase = document.createElement('div');
    newTestCase.classList.add('test-case');
    
    newTestCase.innerHTML = `
        <label>Input:</label>
        <textarea name="test_case_input[]" required></textarea>
        <label>Output:</label>
        <textarea name="test_case_output[]" required></textarea>
        <button type="button" class="delete-test-case">Delete</button>
    `;
    
    testCaseContainer.appendChild(newTestCase);

    // Add event listener for the delete button
    addDeleteEvent(newTestCase.querySelector('.delete-test-case'));
});

// Function to delete a test case
function addDeleteEvent(deleteButton) {
    deleteButton.addEventListener('click', function() {
        deleteButton.parentElement.remove();
    });
}

// Add delete functionality to initial test case
document.querySelectorAll('.delete-test-case').forEach(function(button) {
    addDeleteEvent(button);
});
