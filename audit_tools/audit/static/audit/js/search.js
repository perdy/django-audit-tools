(function () {
    /**
     * Search filter.
     */
    AuditTools.Audit.Filter = Backbone.Model.extend({
        defaults: {
            id: 'filter_id',
            name: 'filter_name',
            template: 'template'
        }
    });

    /**
     * View for search filter.
     */
    AuditTools.Audit.FilterView = Backbone.View.extend({
        el: '#filters',

        initialize: function () {
            _.bindAll(this, 'render', 'unrender');
        },

        render: function () {
            var template = _.template($(this.model.get('template')).html());
            var template_rendered = template({name: this.model.get('id')});
            $(this.el).append(template_rendered);
            return this;
        },

        unrender: function () {
            $('#' + this.model.get('id')).remove();
            return this;
        }
    });

    /**
     * List of search filters
     */
    AuditTools.Audit.FilterList = Backbone.Collection.extend({
        model: AuditTools.Audit.Filter
    });

    /**
     * View for search form.
     */
    AuditTools.Audit.SearchFormView = Backbone.View.extend({
        el: '#search_form',
        events: {
            'click button#send_button': 'doSearch',
            'click button#add_filter_button': 'selectFilter',
            'click button.remove-filter-button': 'deselectFilter',
            'click button.remove-date-button': 'setDefaultDate'
        },

        initialize: function () {
            _.bindAll(this, 'render', 'unrender', 'addFilter', 'removeFilter', 'selectFilter', 'deselectFilter',
                'doSearch', 'addFilterOption', 'removeFilterOption', 'setDefaultDate', 'setDefaultDateFrom', 'setDefaultDateTo');

            this.filterList = new AuditTools.Audit.FilterList();
            this.activeList = new AuditTools.Audit.FilterList();
            this.activeList.bind('add', this.addFilter);
            this.activeList.bind('remove', this.removeFilter);
        },

        setFilters: function(filterList) {
            this.filterList = filterList;
        },

        selectFilter: function (e) {
            var filter_id = $('#select_filter option:selected').val();
            // Add filter to active list
            var filter = this.filterList.get(filter_id);
            this.activeList.add(filter);
            // Remove filter from options in select_filter
            this.removeFilterOption(filter);

            // If list is empty, hide select
            if (this.activeList.length === this.filterList.length) {
                $('#add_filters').hide();
            }
        },

        deselectFilter: function (e) {
            // If select was hidden, show it
            if (this.activeList.length === this.filterList.length) {
                $('#add_filters').show();
            }
            var filter_id = $(e.currentTarget).data('filter');
            // Remove filter from active list
            this.activeList.remove(filter_id);
            // Add filter to options in select_filter
            var filter = this.filterList.get(filter_id);
            this.addFilterOption(filter);
        },

        addFilter: function (filter) {
            var filterView = new AuditTools.Audit.FilterView({
                model: filter
            });
            filterView.render();
        },

        removeFilter: function (filter) {
            var filterView = new AuditTools.Audit.FilterView({
                model: filter
            });
            filterView.unrender();
        },

        doSearch: function (e) {
            e.preventDefault();
            try {
                var page = parseInt($(e.currentTarget).data('page'));
                AuditTools.Audit._search_callback(page)
            } catch(exc) {
                AuditTools.Audit._search_callback()
            }
        },

        addFilterOption: function (filter) {
            var $select = $('#select_filter');
            var $option = $('<option/>', {
                text: filter.get('name'),
                value: filter.get('id'),
                id: 'option_' + filter.get('id')
            });
            $select.append($option);
        },

        removeFilterOption: function (filter) {
            $('#option_' + filter.get('id')).remove()
        },

        setDefaultDateTo: function () {
            var today = new Date();
            var day = today.getDate();
            var dd = day > 9 ? day : '0' + day;
            var month = today.getMonth() + 1;
            var mm = month > 9 ? month : '0' + month;
            var yyyy = today.getFullYear();
            $('#input_date_to input[name="date_to_0"]').val(dd + '/' + mm + '/' + yyyy);
            $('#input_time_to input[name="date_to_1"]').val('23:59');
            $('#input_time_to .bfh-timepicker-popover input[type="text"]').val('00');
        },

        setDefaultDateFrom: function () {
            var today = new Date();
            var day = today.getDate();
            var dd = day > 9 ? day : '0' + day;
            var month = today.getMonth() + 1;
            var mm = month > 9 ? month : '0' + month;
            var yyyy = today.getFullYear();
            $('#input_date_from input[name="date_from_0"]').val(dd + '/' + mm + '/' + yyyy);
            $('#input_time_from input[name="date_from_1"]').val('00:00');
            $('#input_time_from .bfh-timepicker-popover input[type="text"]').val('00');
        },

        setDefaultDate: function (e) {
            var type = $(e.currentTarget).data('target');
            if (type == 'from') {
                this.setDefaultDateFrom();
            } else if (type == 'to') {
                this.setDefaultDateTo();
            }
        },

        render: function () {
            var template = _.template($('#template_search_form').html());
            var template_rendered = template();
            $(this.el).append(template_rendered);
            var self = this;
            this.filterList.each(function (model, index) {
                self.addFilterOption(model);
            });
        },

        unrender: function () {
            $(this.el).children().remove();
        }
    });
})(jQuery);
