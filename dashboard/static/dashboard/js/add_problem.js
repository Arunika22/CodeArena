// document.addEventListener('DOMContentLoaded', () => {
//     const problemForm = document.getElementById('ProblemForm');  // Ensure this ID matches your form's ID
//     const addTestCaseButton = document.getElementById('add-testcase-btn');
//     const addAdditionalTestCaseButton = document.getElementById('add-additional-testcase-btn');
//     const testCaseContainer = document.getElementById('testcase-section');
//     const additionalTestCaseContainer = document.getElementById('additional-testcase-section');
//     console.log('problemForm:', problemForm);
//     console.log('addTestCaseButton:', addTestCaseButton);
//     console.log('addAdditionalTestCaseButton:', addAdditionalTestCaseButton);
//     console.log('testCaseContainer:', testCaseContainer);
//     console.log('additionalTestCaseContainer:', additionalTestCaseContainer);
//     if (!problemForm || !addTestCaseButton || !addAdditionalTestCaseButton) {
//         console.error('One or more elements not found in the DOM.');
//         return;
//     }

//     // Function to add new regular test case
//     addTestCaseButton.addEventListener('click', () => {
//         const index = testCaseContainer.querySelectorAll('.testcase-group').length;
//         const testCaseHTML = `
//             <div class="testcase-group">
//                 <label for="testcase-input-${index}">Test Case Input</label>
//                 <input type="text" name="testcase_input_${index}" class="testcase-input" required>
//                 <label for="testcase-output-${index}">Test Case Output</label>
//                 <input type="text" name="testcase_output_${index}" class="testcase-output" required>
//                 <button type="button" class="btn-remove-testcase">Remove</button>
//             </div>
//         `;
//         testCaseContainer.insertAdjacentHTML('beforeend', testCaseHTML);
//     });

//     // Function to add new additional test case
//     addAdditionalTestCaseButton.addEventListener('click', () => {
//         const index = additionalTestCaseContainer.querySelectorAll('.additional-testcase-group').length;
//         const additionalTestCaseHTML = `
//             <div class="additional-testcase-group">
//                 <label for="additional-testcase-input-${index}">Additional Test Case Input</label>
//                 <input type="text" name="additional_testcase_input_${index}" class="additional-testcase-input" required>
//                 <label for="additional-testcase-output-${index}">Additional Test Case Output</label>
//                 <input type="text" name="additional_testcase_output_${index}" class="additional-testcase-output" required>
//                 <button type="button" class="btn-remove-additional-testcase">Remove</button>
//             </div>
//         `;
//         additionalTestCaseContainer.insertAdjacentHTML('beforeend', additionalTestCaseHTML);
//     });

//     // Delegated event listener for removing test cases
//     problemForm.addEventListener('click', (event) => {
//         if (event.target.classList.contains('btn-remove-testcase') || event.target.classList.contains('btn-remove-additional-testcase')) {
//             event.target.closest('.testcase-group, .additional-testcase-group').remove();
//         }
//     });
//     function removeTestcase(button) {
//         const testcaseGroup = button.closest('.testcase-group, .additional-testcase-group');
//         if (testcaseGroup) {
//             testcaseGroup.remove();
//         }
//     }
//     // Form submission logic
//     problemForm.addEventListener('submit', (event) => {
//         event.preventDefault();
//         const formData = new FormData(problemForm);

//         fetch(problemForm.action, {
//             method: 'POST',
//             body: formData,
//             headers: {
//                 'X-CSRFToken': getCookie('csrftoken'),  // Django CSRF token
//                 'X-Requested-With': 'XMLHttpRequest'  // Indicate AJAX request
//             }
//         })
//         .then(response => response.json())
//         .then(data => {
//             if (data.success) {
              
//                 window.location.href = data.redirect_url;  // Use redirect URL from response
//             } else {
//                 alert('Submission failed. Please check the form for errors.');
//                 console.error(data.errors);  // Log form validation errors
//             }
//         })
//         .catch(error => {
//             console.error('Error:', error);
//         });
//     });

//     // Function to get CSRF token from cookies (for Django)
//     function getCookie(name) {
//         let cookieValue = null;
//         if (document.cookie && document.cookie !== '') {
//             const cookies = document.cookie.split(';');
//             for (let i = 0; i < cookies.length; i++) {
//                 const cookie = cookies[i].trim();
//                 if (cookie.substring(0, name.length + 1) === (name + '=')) {
//                     cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
//                     break;
//                 }
//             }
//         }
//         return cookieValue;
//     }
// });
document.addEventListener('DOMContentLoaded', () => {
    const problemForm = document.getElementById('ProblemForm');  // Ensure this ID matches your form's ID
    const addTestCaseButton = document.getElementById('add-testcase-btn');
    const addAdditionalTestCaseButton = document.getElementById('add-additional-testcase-btn');
    const testCaseContainer = document.getElementById('testcase-section');
    const additionalTestCaseContainer = document.getElementById('additional-testcase-section');
    console.log('problemForm:', problemForm);
    console.log('addTestCaseButton:', addTestCaseButton);
    console.log('addAdditionalTestCaseButton:', addAdditionalTestCaseButton);
    console.log('testCaseContainer:', testCaseContainer);
    console.log('additionalTestCaseContainer:', additionalTestCaseContainer);
    
    if (!problemForm || !addTestCaseButton || !addAdditionalTestCaseButton) {
        console.error('One or more elements not found in the DOM.');
        return;
    }

    // Function to add new regular test case
    addTestCaseButton.addEventListener('click', () => {
        const index = testCaseContainer.querySelectorAll('.testcase-group').length;
        const testCaseHTML = `
            <div class="testcase-group">
                <label for="testcase-input-${index}">Test Case Input</label>
                <textarea name="testcase_input_${index}" class="testcase-input" rows="4" required></textarea>
                <label for="testcase-output-${index}">Test Case Output</label>
                <textarea name="testcase_output_${index}" class="testcase-output" rows="4" required></textarea>
                <button type="button" class="btn-remove-testcase" onclick="removeTestcase(this)">Remove</button>
            </div>
        `;
        testCaseContainer.insertAdjacentHTML('beforeend', testCaseHTML);
    });

    // Function to add new additional test case
    addAdditionalTestCaseButton.addEventListener('click', () => {
        const index = additionalTestCaseContainer.querySelectorAll('.additional-testcase-group').length;
        const additionalTestCaseHTML = `
            <div class="additional-testcase-group">
                <label for="additional-testcase-input-${index}">Additional Test Case Input</label>
                <textarea name="additional_testcase_input_${index}" class="additional-testcase-input" rows="4" required></textarea>
                <label for="additional-testcase-output-${index}">Additional Test Case Output</label>
                <textarea name="additional_testcase_output_${index}" class="additional-testcase-output" rows="4" required></textarea>
                <button type="button" class="btn-remove-additional-testcase" onclick="removeTestcase(this)">Remove</button>
            </div>
        `;
        additionalTestCaseContainer.insertAdjacentHTML('beforeend', additionalTestCaseHTML);
    });

    // Delegated event listener for removing test cases
    problemForm.addEventListener('click', (event) => {
        if (event.target.classList.contains('btn-remove-testcase') || event.target.classList.contains('btn-remove-additional-testcase')) {
            event.target.closest('.testcase-group, .additional-testcase-group').remove();
        }
    });

    function removeTestcase(button) {
        const testcaseGroup = button.closest('.testcase-group, .additional-testcase-group');
        if (testcaseGroup) {
            testcaseGroup.remove();
        }
    }

    // Form submission logic
    problemForm.addEventListener('submit', (event) => {
        event.preventDefault();
        const formData = new FormData(problemForm);

        fetch(problemForm.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),  // Django CSRF token
                'X-Requested-With': 'XMLHttpRequest'  // Indicate AJAX request
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                window.location.href = data.redirect_url;  // Use redirect URL from response
            } else {
                alert('Submission failed. Please check the form for errors.');
                console.error(data.errors);  // Log form validation errors
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });

    // Function to get CSRF token from cookies (for Django)
    function getCookie(name) {
        let cookieValue = null;
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
});

