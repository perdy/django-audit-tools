(function () {
    /* Make AuditTools.Audit.Filter list */
    var filterList = new AuditTools.Audit.FilterList();
    filterList.add(new AuditTools.Audit.Filter({id: 'filter_url', name: 'URL', template: '#template_filter_url'}));
    filterList.add(new AuditTools.Audit.Filter({id: 'filter_method', name: 'Method', template: '#template_filter_method'}));
    filterList.add(new AuditTools.Audit.Filter({id: 'filter_model', name: 'Model', template: '#template_filter_model'}));
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
                modelActionListView.setResults(data)
            },
            error: function (jqXHR, textStatus, errorThrown) {
                var $panel = $('#result');
                $panel.css('display', 'block');
                AuditTools.Audit.ModelSearch.callback_error($panel, errorThrown);
            },
            complete: AuditTools.Audit.HideLoadScreen
        });
    };

    AuditTools.Audit.ModelAction = Backbone.Model.extend();
    AuditTools.Audit.ModelActionList = Backbone.Collection.extend({
        model: AuditTools.Audit.ModelAction
    });

    AuditTools.Audit.ModelActionView = Backbone.View.extend({
        tagName: "div" ,
        className: "panel panel-default",
        template: '#template_model_action',
        events: {
            'show.bs.tab .access_tab': 'renderAccessPanel',
            'show.bs.tab .process_tab': 'renderProcessPanel',
            'show.bs.tab .changes_tab': 'renderChangesPanel',
            'show.bs.tab .detail_tab': 'renderDetailPanel',
            'show.bs.collapse': 'selectDefaultTab',
            'change [data-changes-check]': 'toggleChangesVisibility'
        },

        initialize: function () {
            _.bindAll(this, 'render', 'unrender', 'renderPanel', 'renderAccessPanel', 'renderProcessPanel', 'renderChangesPanel', 'renderDetailPanel', 'selectDefaultTab', 'toggleChangesVisibility');
        },

        renderPanel: function (panel_template, args) {
            var $panel = $('#detail_' + this.model.id);
            $panel.children().remove();
            var template = _.template($(panel_template).html());
            var template_rendered = template(args);
            $panel.append(template_rendered);
        },

        renderAccessPanel: function (e) {
            this.renderPanel('#template_tab_access', {data: this.model.attributes.access, id: this.model.cid});
        },

        renderProcessPanel: function (e) {
            this.renderPanel('#template_tab_process', {data: this.model.attributes.process, id: this.model.cid});
        },

        renderChangesPanel: function (e) {
            this.renderPanel('#template_tab_changes', {data: this.model.attributes, id: this.model.cid});
        },

        renderDetailPanel: function (e) {
            this.renderPanel('#template_tab_detail', {data: this.model.attributes, id: this.model.cid});
        },

        toggleChangesVisibility: function (e) {
            var $checkbox = $(e.currentTarget);
            var $par = $checkbox.parent().parent().parent();
            if ($checkbox.prop('checked')) {
                $par.find('[data-hideable]').hide();
            } else {
                $par.find('[data-hideable]').show();
            }
        },

        selectDefaultTab: function (e) {
            var $target = $(e.target);
            if ($target.find('li.active').length == 0) {
                $target.find('.changes_tab').tab('show');
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

    AuditTools.Audit.ModelActionListView = Backbone.View.extend({
        el: '#result',
        template: '#template_model_action_list',
        events: {
            'click #pagination li': searchFormView.doSearch
        },

        initialize: function () {
            _.bindAll(this, 'render', 'unrender', 'setResults', 'addAccess', 'removeAccess');

            this.modelActionList = new AuditTools.Audit.ModelActionList();
            this.modelActionList.bind('add', this.addAccess);
            this.modelActionList.bind('remove', this.removeAccess);
            this.page = 1;
            this.num_pages = 1;
        },

        setResults: function (results) {
            // Reset access list
            this.modelActionList.reset();
            this.page = results.page;
            this.num_pages = results.num_pages;
            // Reset html structure
            this.unrender();
            this.render();
            // Add results to access list
            var self = this;
            results.results.forEach(function(modelAction, index) {
                var ma = new AuditTools.Audit.ModelAction(modelAction);
                self.modelActionList.add(ma);
            });
        },

        addAccess: function (modelAction) {
            var modelActionView = new AuditTools.Audit.ModelActionView({
                model: modelAction
            });
            $(this.el).find("#panel_result_list").append(modelActionView.render().el);
        },

        removeAccess: function (modelAction) {
            var modelActionView = new AuditTools.Audit.ModelActionView({
                model: modelAction
            });
            modelActionView.unrender();
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

    var modelActionListView = new AuditTools.Audit.ModelActionListView();
})();
