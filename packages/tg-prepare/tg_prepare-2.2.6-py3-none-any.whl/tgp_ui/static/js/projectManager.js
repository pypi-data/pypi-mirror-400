define([], function () {
    const ProjectManager = {
        addMultiInputAttributes: function (event) {
            event.preventDefault();

            // Clone the current input group element
            const currentInputGroup = event.target.closest('.input-group');
            const newInputGroup = currentInputGroup.cloneNode(true);

            // Clear the input field in the cloned element
            const input = newInputGroup.querySelector('input');
            if (input) {
                input.value = '';
            }

            // Replace the plus symbol with a minus symbol and add the 'remove-multi-input' class
            const button = newInputGroup.querySelector('.add-multi-input');
            if (button) {
                button.classList.remove('add-multi-input');
                button.classList.add('remove-multi-input');
                const logo = button.querySelector('i');
                logo.classList.remove('bi-plus-circle-dotted');
                logo.classList.add('bi-dash-circle-dotted');
            }

            // Append the cloned element at the end of the parent container
            currentInputGroup.parentNode.appendChild(newInputGroup);
        },

        removeMultiInputAttributes: function (event) {
            event.preventDefault();

            // Remove the parent div of the minus button
            const inputGroup = event.target.closest('.input-group');
            if (inputGroup) {
                inputGroup.remove();
            }
        },

        focusInputProjectname: function () {
            const projectInput = document.getElementById('projectNameInput');
            if (projectInput) {
                projectInput.focus();
            }
        },

        init: function () {
            // Event binding for adding a new multi-input field
            $(document).on('click', '.add-multi-input', this.addMultiInputAttributes);

            // Event binding for removing a multi-input field
            $(document).on('click', '.remove-multi-input', this.removeMultiInputAttributes);

            // Event binding for focusing on the project name input in the modal
            $(document).on('shown.bs.modal', '#newProject', this.focusInputProjectname);
        }
    };

    return ProjectManager;
});