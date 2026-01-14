define([], function () {
    const TabManager = {
        loadTab: function () {
            const self = $(this);
            const tab = $(self.data('bs-target'));
            if (!tab.hasClass('loaded')) {
                tab.load(prefix + `/tabs/container`)
                tab.load(self.data('url'), function () {
                    tab.addClass('loaded');
                });
            }
        },

        formSubmit: function (event) {
            event.preventDefault();
            const form = $(this);
            const formData = new FormData(this);

            const submitButton = form.find('button[type="submit"]');
            submitButton.prop('disabled', true);
            const originalButtonText = submitButton.html();
            submitButton.html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>');
            $.ajax({
                url: form.attr('action'),
                type: form.attr("method") || 'POST',
                data: formData,
                processData: false,  // Important for file upload
                contentType: false,  // Important for file upload
                success: function (response) {
                    const next_target_id = form.data('next-target');
                    const reload_subtab_id = form.data('reload-subtab');
                    const target_id = form.data('reload-to-target');
                    if (next_target_id) {
                        $(form.closest('.tab-pane')).html(response);
                        const nextTarget = $(next_target_id);
                        const nextTargetButton = $('[data-bs-target="' + next_target_id + '"]')
                        nextTarget.removeClass('loaded');
                        nextTargetButton.trigger('click');

                    } else if (reload_subtab_id) {
                        const response_html = $(response);
                        const filteredContent = response_html.find(reload_subtab_id);
                        $(reload_subtab_id).html(filteredContent.html());
                    } else if (target_id) {
                        const target = $(target_id);
                        target.html(response);
                    }
                    else {
                        $(form.closest('.tab-pane')).html(response);
                    }
                },
                complete: function () {
                    submitButton.prop('disabled', false);
                    submitButton.html(originalButtonText);
                }
            });
        },

        loadNextTab: function (e) {
            e.preventDefault();
            const self = $(this);
            const nextTargetId = self.data('next-target');
            const additionalButtonId = self.data('additional-button');
            const nextTarget = $(nextTargetId);
            const nextTargetButton = $(`[data-bs-target="${nextTargetId}"]`);

            nextTarget.removeClass('loaded');
            nextTargetButton.trigger('click');
            if (additionalButtonId) {
                const additionalButton = $(additionalButtonId);
                additionalButton.trigger('click');
            }
        },

        init: function () {
            $(document).on('show.bs.tab', 'div[data-bs-toggle="tab"].btn-sm', this.loadTab);
            $(document).on('click', 'button.btn-next', this.loadNextTab);
            $(document).on('submit', '.tab-area form.js-tab-submit', this.formSubmit);
        }
    };

    return TabManager;
});