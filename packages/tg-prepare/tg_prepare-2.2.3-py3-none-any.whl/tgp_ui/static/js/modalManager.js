define(['bootstrap'], function (bootstrap) {
    const ModalManager = {
        formSubmit: function (event) {
            event.preventDefault();
            const form = $(this);
            const submitButton = form.find('button[type="submit"]');
            const originalButtonText = submitButton.html();

            // show spinner and disable button
            submitButton.html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>')
                .prop('disabled', true);

            $.ajax({
                url: form.attr('action'),
                type: form.attr("method") || 'GET',
                data: form.serialize(),
                success: function (response) {
                    if (form.data('reload-location')) {
                        location.reload();
                    } else {
                        form.closest('.modal-dialog').html(response);
                    }
                },
                error: function () {
                    alert('An error occurred. Please try again.');
                },
                complete: function () {
                    // restore original button text and remove spinner
                    submitButton.html(originalButtonText).prop('disabled', false);
                }
            });
        },

        loadModal: function (e) {
            e.preventDefault();

            const self = $(this);
            const url = self.data('url');
            const modalContainer = $('#genericModalContainer');
            const argsKeys = Object.keys(self.data()).filter(key => key.startsWith('args_'));

            modalContainer.load(prefix + "/modal/container .modal-dialog");
            const modal = new bootstrap.Modal(modalContainer[0]);
            if (!modalContainer.is(':visible')) {
                modal.show();
            };

            let args = {};
            if (argsKeys.length > 0) {
                for (const key of argsKeys) {
                    const value = self.data(key);
                    const paramName = key.replace('args_', '');
                    args[paramName] = value;
                }
            }

            modalContainer.load(url + " .modal-dialog", args);
        },

        loadTEIContent: function (e) {
            e.preventDefault();
            const self = $(this);
            const modal = self.closest('.modal');

            modal.find('.bg-primary, .bg-light')
                .removeClass('bg-primary')
                .removeClass('bg-light')
                .removeClass('text-white');
            self.addClass('bg-primary')
                .addClass('text-white')
                .closest('.list-group-item').addClass('bg-light');

            $.ajax({
                url: self.data('url'),
                method: 'GET',
                dataType: 'json',
                data: self.data(),
                success: function (response) {
                    const teiContentOutput = modal.find('#teiContentOutput');
                    teiContentOutput.empty();
                    const col = $('<div class="col"></div>');
                    col.append('<h3>' + self.data('heading') + '</h3>');
                    col.append('<span></span>');
                    teiContentOutput.append(col);
                    col.find('span').simpleXML({ xmlString: response.content });
                    modal.find('#contentTab').trigger('click');
                }
            });
        },

        focusInputProjectname: function () {
            const projectInput = document.getElementById('projectNameInput');
            projectInput.focus();
        },

        init: function () {
            $(document).on('submit', 'form.js-modal-submit', this.formSubmit);
            $(document).on('click', '.load-modal', this.loadModal);
            $(document).on('click', '.load-tei-content', this.loadTEIContent);
            $(document).on('shown.bs.modal', '#newProject', this.focusInputProjectname);
        }
    };

    return ModalManager;
});