define([], function () {
    const CollectionManager = {
        loadDetailsInSidebar: function () {
            const self = $(this);
            const url = self.data('url');
            const detailsContent = $('#detailsContent');
            detailsContent.load(prefix + "/details/container");
            self.closest('.card-body')
                .find('button.btn-primary')
                .addClass('btn-secondary')
                .removeClass('btn-primary');

            self.addClass('btn-primary').removeClass('btn-secondary');

            $.get(url, function (data) {
                detailsContent.html(data);
            }).fail(function () {
                detailsContent.html('<p class="text-danger">Failed to load details. Please try again.</p>');
            });
        },

        addMultiInputClassifications: function (e) {
            e.preventDefault();
            const self = $(this);
            const thisRow = self.closest('.row');
            thisRow.next().clone()
                .insertAfter(thisRow)
                .find('input').val('');
        },

        removeMultiInputClassifications: function (e) {
            e.preventDefault();
            const self = $(this);
            const thisMultiInput = self.closest('.multi-input');
            thisMultiInput.remove();
        },

        highlightFolder: function (e) {
            const self = $(this);
            const selectedFolder = self.closest('.card');
            selectedFolder.toggleClass('border-primary').toggleClass('border-secondary');
        },

        init: function () {
            // Load details in sidebar
            $(document).on('click', '.edit-collection-button', this.loadDetailsInSidebar);

            // Add a new multi input-field (e.g., 'Basic classification', 'Rights Holder')
            $(document).on('click', '.add-multi-input-classifications', this.addMultiInputClassifications);

            // Remove a multi input-field (e.g., 'Basic classification', 'Rights Holder')
            $(document).on('click', '.remove-multi-field-classification', this.removeMultiInputClassifications);

            // Highlight folder
            $(document).on('change', 'input[name="selected_folder"]', this.highlightFolder);
        }
    };

    return CollectionManager;
});