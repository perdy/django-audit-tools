(function () {
    /**
     * Object for manage ModelSearch page.
     * @type {Object}
     */
    AuditTools.Audit.ModelSearch = {};

    /** Variables **/
    AuditTools.Audit.ModelSearch.active_filters = 0;
    AuditTools.Audit.ModelSearch.filters_id = '#filters';
    AuditTools.Audit.ModelSearch.filter_name = 'filter';
    AuditTools.Audit.ModelSearch.filters = ['Model', 'User', 'URL', 'Method', 'Interlink'];
    AuditTools.Audit.ModelSearch.search_result = {};
    AuditTools.Audit.ModelSearch.process_url = '/audit/api/process/';
    AuditTools.Audit.ModelSearch.access_url = '/audit/api/access/';

    /**
     * Gets all values remaining for selects.
     * @returns {*|jQuery}
     */
    AuditTools.Audit.ModelSearch.get_values = function () {
        var values = AuditTools.Audit.ModelSearch.filters;

        var used_values = [];
        $(AuditTools.Audit.ModelSearch.filters_id + ' select').each(function () {
            used_values.push($(this).val());
        });

        return $(values).not(used_values).get();
    };

    AuditTools.Audit.ModelSearch.RemoveDate = function ($button) {
        var target_date = $button.attr('data-target') + ' .bfh-datepicker-toggle input[type="text"]';

        var today = new Date();
        var day = today.getDate();
        var dd = day > 9 ? day : '0' + day;
        var month = today.getMonth() + 1;
        var mm = month > 9 ? month : '0' + month;
        var yyyy = today.getFullYear();

        $(target_date).val(dd + '/' + mm + '/' + yyyy);

        var target_time = $button.attr('data-target') + ' .bfh-timepicker-toggle input[type="text"]';
        var time_str = '00:00';
        if ($button.attr('data-target') == '.input_to') {
            time_str = '23:59';
        }
        $(target_time).val(time_str);
    };

    /**
     * Add a new filter in search form.
     * @constructor
     */
    AuditTools.Audit.ModelSearch.AddNewFilter = function () {
        AuditTools.Audit.ModelSearch.active_filters += 1;
        var values = AuditTools.Audit.ModelSearch.get_values();

        if (values.length > 0) {
            // Disable current selects
            $(AuditTools.Audit.ModelSearch.filters_id + ' select').each(function () {
                $(this).prop('disabled', true);
            });

            var options = [];

            // Default value
            var default_opt = $('<option/>', {
                value: '',
                text: 'Select a filter',
                style: 'display: none;',
                disabled: true,
                selected: true
            });
            options.push(default_opt);

            for (var i = 0; i < values.length; i++) {
                var opt = $('<option/>', {
                    value: values[i],
                    text: values[i]
                });
                options.push(opt);
            }

            var sel = $('<select/>', {
                class: 'form-control',
                html: options
            });

            var div_select = $('<div/>', {
                class: 'col-xs-2',
                html: sel
            });

            var but_icon = $('<span/>', {
                class: 'glyphicon glyphicon-minus'
            });

            var but = $('<button/>', {
                type: 'button',
                class: 'btn btn-danger remove-filter-button',
                id: 'removeFilterButton' + AuditTools.Audit.ModelSearch.active_filters,
                html: but_icon
            });

            var label = $('<label/>', {
                id: 'filter_label_' + AuditTools.Audit.ModelSearch.active_filters,
                class: 'col-xs-1 control-label filter-label',
                text: 'Filter'
            });

            var div_button = $('<div/>', {
                class: 'col-xs-1',
                html: but
            });

            var div1 = $('<div/>', {
                id: AuditTools.Audit.ModelSearch.filter_name + '_' + AuditTools.Audit.ModelSearch.active_filters,
                class: 'form-group',
                html: [div_button, label, div_select]
            });
            $(AuditTools.Audit.ModelSearch.filters_id).append(div1);
            $('#add_filter_button').hide();
        }

    };

    /**
     * Remove a filter from search form.
     * @param button
     * @constructor
     */
    AuditTools.Audit.ModelSearch.RemoveFilter = function (button) {
        $('#add_filter_button').show();

        var filter_id = button.parent().parent().attr('id');
        var val = $('#' + filter_id + ' select').first().val();

        $('#filters').find('select').each(function () {
            var found = false;
            $(this).find('option').each(function () {
                if ($(this).val() == val) {
                    found = true;
                }
            });

            if (found == false) {
                var opt = $('<option/>', {
                    value: val,
                    text: val
                });

                $(this).append(opt);
            }
        });

        var par = button.parent().parent();
        par.remove();

        $(AuditTools.Audit.ModelSearch.filters_id + ' select').last().prop('disabled', false);
    };

    /**
     * Add input fields for selected option.
     * @param $select
     * @constructor
     */
    AuditTools.Audit.ModelSearch.AddSelectFieldsFilter = function ($select) {
        var values = AuditTools.Audit.ModelSearch.get_values();
        if (values.length > 0) {
            $('#add_filter_button').show();
        }

        var val = $select.val();
        var par = $select.parent().parent();

        // Remove old fields
        par.children().each(function (i) {
            if (i > 2) {
                $(this).remove()
            }
        });

        // Add new fields
        var template = null;
        if (val == 'User') {
            template = _.template($('#filter_user_template').html());
        } else if (val == 'URL') {
            template = _.template($('#filter_url_template').html());
        } else if (val == 'Method') {
            template = _.template($('#filter_method_template').html());
        } else if (val == 'Model') {
            template = _.template($('#filter_model_template').html());
        } else if (val == 'Interlink') {
            template = _.template($('#filter_interlink_template').html());
        }
        var template_rendered = template({});
        par.append(template_rendered);
    };

    AuditTools.Audit.ModelSearch.FillModelList = function (data) {
        $('#result').css('display', 'block');

        var $result_list = $('#result_list');
        $result_list.children().remove();

        var template = _.template($('#result_list_template').html());
        var template_rendered = template({'data': data.query, 'paginator': data.paginator});

        $result_list.append(template_rendered);
    };

    /**
     * Show details of a model.
     * @param $tab tab that fires the event.
     * @constructor
     */
    AuditTools.Audit.ModelSearch.FillModelChanges = function ($tab) {
        var s = $tab.data('target');
        var splitted = s.split('_');
        var index = splitted[splitted.length - 1];

        var $panel = $(s);
        $panel.children().remove();

        var template = _.template($('#tab_changes_template').html());
        var template_rendered = template({'data': AuditTools.Audit.ModelSearch.search_result.query[index].content, 'index': index});

        $panel.append(template_rendered);
    };

    /**
     * Show details of a model.
     * @param $tab tab that fires the event.
     * @constructor
     */
    AuditTools.Audit.ModelSearch.FillModelDetail = function ($tab) {
        var s = $tab.data('target');
        var splitted = s.split('_');
        var index = splitted[splitted.length - 1];

        var $panel = $(s);
        $panel.children().remove();

        var template = _.template($('#tab_detail_template').html());
        var template_rendered = template({'data': AuditTools.Audit.ModelSearch.search_result.query[index]});

        $panel.append(template_rendered);
    };

    /**
     * Show access of a model.
     * @param $tab tab that fires the event.
     * @constructor
     */
    AuditTools.Audit.ModelSearch.FillModelAccess = function ($tab) {
        try {
            var s = $tab.data('target');
            var splitted = s.split('_');
            var index = splitted[splitted.length - 1];

            var $panel = $(s);
            $panel.children().remove();

            try {
                var access_id = AuditTools.Audit.ModelSearch.search_result.query[index].access.$oid;
                var $template = $('#tab_access_template');

                AuditTools.Audit.LoadScreen.ShowLoadScreen();

                $.ajax({
                    url: AuditTools.Audit.ModelSearch.access_url + access_id + '/',
                    type: 'GET',
                    dataType: 'JSON',
                    success: function (data) {
                        AuditTools.Audit.ModelSearch.callback_success_model_detail(data, $panel, $template);
                    },
                    error: function (jqXHR, textStatus, errorThrown) {
                        AuditTools.Audit.ModelSearch.callback_error($panel, errorThrown);
                    },
                    complete: AuditTools.Audit.LoadScreen.HideLoadScreen
                });
            } catch (e) {
                var result_h = $('<h5>', {
                    text: 'Access not found'
                });

                var result_div = $('<div>', {
                    html: result_h
                });

                $panel.append(result_div);
            }
        } catch (e) {}
    };

    /**
     * Show process of a model.
     * @param $tab tab that fires the event.
     * @constructor
     */
    AuditTools.Audit.ModelSearch.FillModelProcess = function ($tab) {
        try {
            var s = $tab.data('target');
            var splitted = s.split('_');
            var index = splitted[splitted.length - 1];

            var $panel = $(s);
            $panel.children().remove();

            try {
                var process_id = AuditTools.Audit.ModelSearch.search_result.query[index].process.$oid;
                var $template = $('#tab_process_template');

                AuditTools.Audit.LoadScreen.ShowLoadScreen();

                $.ajax({
                    url: AuditTools.Audit.ModelSearch.process_url + process_id + '/',
                    type: 'GET',
                    dataType: 'JSON',
                    success: function (data) {
                        AuditTools.Audit.ModelSearch.callback_success_model_detail(data, $panel, $template);
                    },
                    error: function (jqXHR, textStatus, errorThrown) {
                        AuditTools.Audit.ModelSearch.callback_error($panel, errorThrown);
                    },
                    complete: AuditTools.Audit.LoadScreen.HideLoadScreen
                });
            } catch (e) {
                var result_h = $('<h5>', {
                    text: 'Process not found'
                });

                var result_div = $('<div>', {
                    html: result_h
                });

                $panel.append(result_div);
            }
        } catch (e) {
        }
    };

    /**
     * Callback function for success ajax call filling #model_detail
     * @param data Ajax response
     * @param $panel panel where template will be rendered
     * @param $template template that will be rendered
     */
    AuditTools.Audit.ModelSearch.callback_success_model_detail = function (data, $panel, $template) {
        var template = _.template($template.html());
        var template_rendered = template({'data': data.query});

        $panel.append(template_rendered);

        AuditTools.Audit.LoadScreen.HideLoadScreen();
    };

    /**
     * Callback function for error ajax calls. Shows error returned.
     * @param $panel
     * @param errorThrown
     */
    AuditTools.Audit.ModelSearch.callback_error = function ($panel, errorThrown) {
        $panel.children().remove();

        var h4_div = $('<h4>', {
            text: 'Search error: ' + errorThrown
        });

        var error_div = $('<div>', {
            id: 'result_error',
            html: h4_div
        });

        $panel.append(error_div);
    };

    /**
     * Validate form.
     * @constructor
     */
    AuditTools.Audit.ModelSearch.ValidateForm = function (pag) {
        pag = pag || 1;
        AuditTools.Audit.LoadScreen.ShowLoadScreen();

        var $form = $('#search_form');
        var serializedForm = $form.serialize() + '&page=' + pag;

        $.ajax({
            url: $form.attr('action'),
            type: $form.attr('method'),
            dataType: $form.attr('data-type'),
            data: serializedForm,
            success: function (data) {
                AuditTools.Audit.ModelSearch.search_result = data;
                AuditTools.Audit.ModelSearch.FillModelList(data);
            },
            error: function (jqXHR, textStatus, errorThrown) {
                var $panel = $('#result');
                $panel.css('display', 'block');
                AuditTools.Audit.ModelSearch.callback_error($panel, errorThrown);
            },
            complete: AuditTools.Audit.LoadScreen.HideLoadScreen
        });
    };

    AuditTools.Audit.ModelSearch.ChangeTabItemsVisibilityToggle = function ($checkbox) {
        $par = $checkbox.parent().parent().parent();
        if ($checkbox.prop('checked')) {
            $par.find('[data-hideable]').hide();
        } else {
            $par.find('[data-hideable]').show();
        }
    };

    /**
     * Activate all events.
     * @constructor
     */
    AuditTools.Audit.ModelSearch.EnableEvents = function () {
        var body = $('body');
        // Event for remove date
        body.on('click', '.remove-date-button', function (e) {
            e.preventDefault();
            AuditTools.Audit.ModelSearch.RemoveDate($(this));
        });
        // Add filter event
        body.on('click', '.add-filter-button', function (e) {
            e.preventDefault();
            AuditTools.Audit.ModelSearch.AddNewFilter();
        });
        // Remove filter event
        body.on('click', '.remove-filter-button', function (e) {
            e.preventDefault();
            AuditTools.Audit.ModelSearch.RemoveFilter($(this));
        });
        // Add custom filter event
        body.on('change', AuditTools.Audit.ModelSearch.filters_id + ' select', function (e) {
            e.preventDefault();
            AuditTools.Audit.ModelSearch.AddSelectFieldsFilter($(this));
        });
        // Search button
        $('#send_button').click(function (e) {
            e.preventDefault();
            AuditTools.Audit.ModelSearch.ValidateForm();
        });
        // Changes tab expand
        body.on('show.bs.tab', '#result_list .changes_tab', function () {
            AuditTools.Audit.ModelSearch.FillModelChanges($(this));
        });
        // Detail tab expand
        body.on('show.bs.tab', '#result_list .detail_tab', function () {
            AuditTools.Audit.ModelSearch.FillModelDetail($(this));
        });
        // Access tab expand
        body.on('show.bs.tab', '#result_list .access_tab', function () {
            AuditTools.Audit.ModelSearch.FillModelAccess($(this));
        });
        // Process tab expand
        body.on('show.bs.tab', '#result_list .process_tab', function () {
            AuditTools.Audit.ModelSearch.FillModelProcess($(this));
        });
        // Auto show changes on expand panel
        body.on('show.bs.collapse', 'div.panel', function () {
            var $tab = $(this).find('.changes_tab');
            AuditTools.Audit.ModelSearch.FillModelChanges($tab);
        });
        // Change page in paginator
        body.on('click', '#result_list .pagination li a', function () {
            AuditTools.Audit.ModelSearch.ValidateForm($(this).attr('data-page'))
        });
        // Checkbox for hiding unchanged items in changes tab
        body.on('change', '[data-changes-check]', function () {
            AuditTools.Audit.ModelSearch.ChangeTabItemsVisibilityToggle($(this));
        });
    };

    /**
     * Disable all events.
     * @constructor
     */
    AuditTools.Audit.ModelSearch.DisableEvents = function () {
        var body = $('body');
        body.off('click', '.remove-date-button');
        body.off('click', '.add-filter-button');
        body.off('click', '.remove-filter-button');
        body.off('change', AuditTools.Audit.ModelSearch.filters_id + ' select');
        $('#send_button').unbind('click');
        body.off('show.bs.tab', '#result_list .changes_tab');
        body.off('show.bs.tab', '#result_list .detail_tab');
        body.off('show.bs.tab', '#result_list .access_tab');
        body.off('show.bs.tab', '#result_list .process_tab');
        body.off('show.bs.collapse', 'div.panel');
        body.off('show.bs.collapse', 'div.panel');
        body.off('change', '[data-changes-check]');
    };

    $(document).ready(function () {
        AuditTools.Audit.ModelSearch.EnableEvents();
    });
})();
