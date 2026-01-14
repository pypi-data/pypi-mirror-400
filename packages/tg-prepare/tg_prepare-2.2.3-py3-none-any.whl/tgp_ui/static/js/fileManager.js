define([], function () {
    const FileManager = {
        // Generic file upload handlers
        triggerFileInput: function () {
            $('#fileInput').trigger('click');
        },
        submitFileUpload: function () {
            $('#fileUploadLocal').trigger('submit');
            this.value = "";    // Reset input to ensure re-uploading
        },

        // Config upload handlers in 'Manage Collections & Metadata' tab
        triggerConfigUpload: function () {
            const self = $(this);
            const form = self.closest('form.config-upload');
            form.find('input.config-upload').trigger('click');
        },
        submitConfigUpload: function () {
            const self = $(this);
            const form = self.closest('form.config-upload');
            form.trigger('submit');
            this.value = "";    // Reset input to ensure re-uploading
        },

        showPreviewOfAvatar: function () {
            const uploadFile = $(this);
            const files = this.files;

            if (files && files.length && window.FileReader) {
                const reader = new FileReader();
                reader.readAsDataURL(files[0]);

                reader.onloadend = function () {
                    uploadFile.closest("div").find('.ratio').html(`
                        <div class="w-100 h-100"
                             style="background-image: url(${this.result});
                                    background-size: cover;
                                    background-position: center;">
                        </div>
                    `);
                };
            }
        },

        cloneFromGit: function (e) {
            e.preventDefault();
            const form = $(e.target);
            const button = form.find('button[type="submit"]');
            const spinner = button.find('.spinner-border');
            const buttonText = button.find('span:not(.spinner-border)');
            const modal = form.closest('.modal');

            button.prop('disabled', true);
            spinner.removeClass('d-none');
            buttonText.text('Cloning...');

            $.ajax({
                url: form.attr('action'),
                method: 'POST',
                data: form.serialize(),
                success: function (response) {
                    $(modal).modal('hide');
                    $(form.closest('.tab-pane')).html(response);
                },
                error: function () {
                    button.removeClass('btn-primary').addClass('btn-danger');
                    buttonText.text('Clone Repository');
                },
                complete: function () {
                    spinner.addClass('d-none');
                    button.prop('disabled', false);
                }
            });
        },

        deleteFolder: function (e) {
            e.preventDefault();
            const button = $(this);
            const itemName = button.data('item-name');
            const itemType = button.data('item-type');

            if (confirm(`Do you want to delete ${itemType === 'folder' ? 'the folder' : 'the file'} "${itemName}"?`)) {
                $.ajax({
                    url: '/api/delete-folder',
                    method: 'DELETE',
                    data: {
                        path: button.data('item-path'),
                        projectname: button.data('projectname')
                    },
                    success: function (response) {
                        $(button.closest('.tab-pane')).html(response);
                    },
                    error: function () {
                        alert('Error deleting item.');
                    }
                });
            }
        },

        deleteXSLT: function (e) {
            e.preventDefault();
            const projectname = $(this).data('projectname');
            const self = this;
            $.ajax({
                url: `/delete-xslt/${projectname}`,
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                },
                success: function (response) {
                    FileManager.hideHint.call(self);
                },
                error: function () {
                    alert('Error deleting XSLT file.');
                }
            });
        },

        hideHint: function () {
            const hint = $('.xslt-upload');
            if (hint) {
                hint.addClass('d-none');
            }
        },

        selectNextcloudFolder: function () {
            const self = $(this);
            const new_state = self.is(':checked') ? 'checked' : '';
            const checkboxes = self.closest('.list-group-item').find('.nextcloud-folder');
            checkboxes
                .prop("checked", new_state)
                .not(':first')
                .prop("disabled", true);
        },

        init: function () {
            // Generic file upload handlers
            $(document).on('change', 'input#fileInput', this.submitFileUpload);
            $(document).on('click', 'button#triggerFileInput', this.triggerFileInput);
            // Config upload handlers in 'Manage Collections & Metadata' tab
            $(document).on('click', 'button.trigger-config-upload', this.triggerConfigUpload);
            $(document).on('change', 'input.config-upload', this.submitConfigUpload);

            $(document).on('click', '.delete-folder', this.deleteFolder);
            $(document).on("change", ".showPreviewOfAvatar", this.showPreviewOfAvatar);
            $(document).on('click', '#deleteXsltButton', this.deleteXSLT);
            $(document).on('change', '.xslt-upload', this.hideHint);
            $(document).on('click', 'input.nextcloud-folder', this.selectNextcloudFolder);
        }
    };

    return FileManager;
});