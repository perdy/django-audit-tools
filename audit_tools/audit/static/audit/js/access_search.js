(function () {
    /* Make AuditTools.Audit.Filter list */
    var filterList = new AuditTools.Audit.FilterList();
    filterList.add(new AuditTools.Audit.Filter({id: 'filter_url', name: 'URL', template: '#template_filter_url'}));
    filterList.add(new AuditTools.Audit.Filter({id: 'filter_method', name: 'Method', template: '#template_filter_method'}));
    filterList.add(new AuditTools.Audit.Filter({id: 'filter_user', name: 'User', template: '#template_filter_user'}));
    filterList.add(new AuditTools.Audit.Filter({
        id: 'filter_interlink',
        name: 'Interlink',
        template: '#template_filter_interlink'
    }));

    var searchFormView = new AuditTools.Audit.SearchFormView();
    searchFormView.setFilters(filterList);
    searchFormView.render();

    /**
     * Callback function for search.
     * @param page
     */
    AuditTools.Audit._search_callback = function (page) {
        page = page || 1;
        var $form = $('#search');
        var serializedForm = $form.serialize() + '&page=' + page;

        AuditTools.Audit.ShowLoadScreen();

        $.ajax({
            url: $form.attr('action'),
            type: $form.attr('method'),
            dataType: $form.attr('data-type'),
            data: serializedForm,
            success: function (data) {
                accessListView.setResults(data)
            },
            error: function (jqXHR, textStatus, errorThrown) {
                var $panel = $('#result');
                $panel.css('display', 'block');
                AuditTools.Audit.ModelSearch.callback_error($panel, errorThrown);
            },
            complete: AuditTools.Audit.HideLoadScreen
        });
    };

    AuditTools.Audit.Access = Backbone.Model.extend();
    AuditTools.Audit.AccessList = Backbone.Collection.extend({
        model: AuditTools.Audit.Access
    });

    AuditTools.Audit.AccessView = Backbone.View.extend({
        tagName: "div" ,
        className: "panel panel-default",
        template: '#template_access',
        events: {
            'show.bs.tab .access_tab': 'renderAccessPanel',
            'show.bs.tab .process_tab': 'renderProcessPanel',
            'show.bs.collapse': 'selectDefaultTab'
        },

        initialize: function () {
            _.bindAll(this, 'render', 'unrender', 'renderPanel', 'renderAccessPanel', 'renderProcessPanel', 'selectDefaultTab');
        },

        renderPanel: function (panel_template, args) {
            var $panel = $('#detail_' + this.model.id);
            $panel.children().remove();
            var template = _.template($(panel_template).html());
            var template_rendered = template(args);
            $panel.append(template_rendered);
        },

        renderAccessPanel: function (e) {
            this.renderPanel('#template_tab_access', {data: this.model.attributes});
        },

        renderProcessPanel: function (e) {
            this.renderPanel('#template_tab_process', {data: this.model.attributes.process});
        },

        selectDefaultTab: function (e) {
            var $target = $(e.target);
            if ($target.find('li.active').length == 0) {
                $target.find('.access_tab').tab('show');
            }
        },

        render: function () {
            var template = _.template($(this.template).html());
            var template_rendered = template({data: this.model.attributes, id: this.model.id});
            $(this.el).html(template_rendered);
            return this;
        },

        unrender: function () {
            $('#' + this.model.id).remove();
            return this;
        }
    });

    AuditTools.Audit.AccessListView = Backbone.View.extend({
        el: '#result',
        template: '#template_access_list',
        events: {
            'click #pagination li': searchFormView.doSearch
        },

        initialize: function () {
            _.bindAll(this, 'render', 'unrender', 'setResults', 'addAccess', 'removeAccess');

            this.accessList = new AuditTools.Audit.AccessList();
            this.accessList.bind('add', this.addAccess);
            this.accessList.bind('remove', this.removeAccess);
            this.page = 1;
            this.num_pages = 1;
        },

        setResults: function (results) {
            // Reset access list
            this.accessList.reset();
            this.page = results.page;
            this.num_pages = results.num_pages;
            // Reset html structure
            this.unrender();
            this.render();
            // Add results to access list
            var self = this;
            results.results.forEach(function(access, index) {
                var a = new AuditTools.Audit.Access(access);
                self.accessList.add(a);
            });
        },

        addAccess: function (access) {
            var accessView = new AuditTools.Audit.AccessView({
                model: access
            });
            $(this.el).find("#panel_result_list").append(accessView.render().el);
        },

        removeAccess: function (access) {
            var accessView = new AuditTools.Audit.AccessView({
                model: access
            });
            accessView.unrender();
        },

        render: function () {
            var template = _.template($(this.template).html());
            var template_rendered = template({data: this.model, current_page: this.page, num_pages: this.num_pages});
            $(this.el).append(template_rendered);
            return this;
        },

        unrender: function () {
            $(this.el).children().remove();
            return this;
        }
    });

    var accessListView = new AuditTools.Audit.AccessListView();
})();
