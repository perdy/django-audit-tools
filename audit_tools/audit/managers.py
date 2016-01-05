from __future__ import unicode_literals

import re

from mongoengine import QuerySet


def _check_args(required_arg, incompatible_args, kwargs, cmp_func=lambda x, y: x.startswith(y)):
    """Check for correct arguments.

    :param required_arg: required keyword argument.
    :type required_arg: unicode
    :param incompatible_args: tuple of incompatible args.
    :type incompatible_args: tuple(unicode)
    :param kwargs: kwargs
    :type kwargs: dict
    :param cmp_func: function that returns true if a key is valid.
    :type cmp_func: function
    :return: key, value
    """
    # Required arguments
    try:
        key, value = [(k, v) for k, v in kwargs.iteritems() if cmp_func(k, required_arg)][0]
    except IndexError:
        raise AttributeError('Argument {} without modifiers required.'.format(required_arg))

    # Incompatible arguments
    if len([x for x in kwargs.keys() if x in incompatible_args]) > 0:
        raise AttributeError('You cannot call this function with {}. Use only fview argument for that.'.format(
            ', '.join(incompatible_args)))

    return key, value


class ModelActionQuerySet(QuerySet):
    """Custom manager for ModelAction.
    """

    def _prepare_kwargs_by_model(self, kwargs):
        required_arg = 'klass'
        incompatible_args = ('model__full_name', 'model__name', 'model__app')
        key, klass = _check_args(required_arg, incompatible_args, kwargs, cmp_func=lambda x, y: x == y)

        # Clean kwargs
        del kwargs[key]

        klass_name = klass.__name__
        klass_module = klass.__module__.split('.', 1)[0]

        kwargs['model__name'] = klass_name
        kwargs['model__app'] = klass_module

        return kwargs

    def filter_by_model(self, *args, **kwargs):
        """Filtered queryset by model.

        :param kwargs: klass kwarg required.
        :return: QuerySet
        """
        kwargs = self._prepare_kwargs_by_model(kwargs)

        return self.filter(*args, **kwargs)

    def get_by_model(self, *args, **kwargs):
        """Get object by model.

        :param kwargs: klass kwarg required.
        :return: ModelAction
        """
        kwargs = self._prepare_kwargs_by_model(kwargs)

        return self.get(*args, **kwargs)

    def _prepare_kwargs_by_model_list(self, kwargs):
        required_arg = 'klass'
        incompatible_args = ('model__full_name', 'model__name', 'model__app')
        key, klass = _check_args(required_arg, incompatible_args, kwargs, cmp_func=lambda x, y: x == y)

        # Clean kwargs
        del kwargs[key]

        r = r''
        for k in klass:
            klass_name = k.__name__
            klass_module = k.__module__
            klass_full_name = klass_module + '.' + klass_name
            r += klass_full_name + '|'

        r = r[:-1]
        kwargs['model__full_name'] = re.compile(r)

        return kwargs

    def filter_by_model_list(self, *args, **kwargs):
        """Filtered queryset by model list.

        :param kwargs: klass kwarg required.
        :return: QuerySet
        """
        kwargs = self._prepare_kwargs_by_model_list(kwargs)

        return self.filter(*args, **kwargs)

    def get_by_model_list(self, *args, **kwargs):
        """Get object by model list.

        :param kwargs: klass kwarg required.
        :return: ModelAction
        """
        kwargs = self._prepare_kwargs_by_model_list(kwargs)

        return self.get(*args, **kwargs)

    def _prepare_kwargs_by_instance(self, kwargs):
        required_arg = 'obj'
        incompatible_args = ('instance__id', 'model__name', 'model__app', 'model__full_name')
        key, obj = _check_args(required_arg, incompatible_args, kwargs, cmp_func=lambda x, y: x == y)

        # Clean kwargs
        del kwargs[key]

        obj_id = str(obj.pk)

        kwargs['instance__id'] = obj_id
        kwargs['model__name'] = obj.__class__.__name__
        kwargs['model__app'] = obj.__module__.split('.')[0]

        return kwargs

    def filter_by_instance(self, *args, **kwargs):
        """Filtered queryset by object instance.

        :param kwargs: obj kwarg required.
        :return: QuerySet
        """
        kwargs = self._prepare_kwargs_by_instance(kwargs)

        return self.filter(*args, **kwargs)

    def get_by_instance(self, *args, **kwargs):
        """Get object by instance.

        :param kwargs: obj kwarg required.
        :return: ModelAction
        """
        kwargs = self._prepare_kwargs_by_instance(kwargs)

        return self.get(*args, **kwargs)


class AccessQuerySet(QuerySet):
    """Custom manager for Access.
    """

    def _prepare_kwargs_by_view(self, kwargs):
        required_arg = 'fview'
        incompatible_args = ('view__name', 'view__full_name', 'view__app')
        key, fview = _check_args(required_arg, incompatible_args, kwargs, cmp_func=lambda x, y: x == y)

        # Clean kwargs
        del kwargs[key]

        view_name = fview.__name__
        view_module = fview.__module__
        view_full_name = view_module + '.' + view_name

        kwargs['view__full_name'] = view_full_name

        return kwargs

    def filter_by_view(self, *args, **kwargs):
        """Filtered queryset by view object or function.

        :param kwargs: fview kwarg required.
        :return: QuerySet
        """
        kwargs = self._prepare_kwargs_by_view(kwargs)

        return self.filter(*args, **kwargs)

    def get_by_view(self, *args, **kwargs):
        """Get object by view.

        :param kwargs: fview kwarg required.
        :return: Access
        """
        kwargs = self._prepare_kwargs_by_view(kwargs)

        return self.get(*args, **kwargs)

    def _prepare_kwargs_by_url(self, kwargs):
        required_arg = 'url'
        incompatible_args = ('request__path', )
        key, url = _check_args(required_arg, incompatible_args, kwargs)

        # Clean kwargs
        del kwargs[key]

        # Get modifier
        splitted_key = key.rsplit('__', 1)
        if len(splitted_key) > 1:
            modifier = splitted_key[1]
        else:
            modifier = ''

        if modifier == 'regex':
            url = re.compile(url)
            key = 'request__path'
        elif modifier:
            key = 'request__path__' + modifier
        else:
            key = 'request__path'

        kwargs[key] = url

        return kwargs

    def filter_by_url(self, *args, **kwargs):
        """Filtered queryset by url. Url accept all modifiers, including __regex.

        :param kwargs: url kwarg required.
        :return: QuerySet
        """
        kwargs = self._prepare_kwargs_by_url(kwargs)

        return self.filter(*args, **kwargs)

    def get_by_url(self, *args, **kwargs):
        """Get object by url. Url accept all modifiers, including __regex.

        :param kwargs: url kwarg required.
        :return: Access
        """
        kwargs = self._prepare_kwargs_by_url(kwargs)

        return self.get(*args, **kwargs)

    def _prepare_kwargs_by_exception(self, kwargs):
        required_arg = 'exc'
        incompatible_args = ('exception__type', )
        key, exc = _check_args(required_arg, incompatible_args, kwargs, cmp_func=lambda x, y: x == y)

        # Clean kwargs
        del kwargs[key]

        exc_name = exc.__name__

        kwargs['exception__type'] = exc_name

        return kwargs

    def filter_by_exception(self, *args, **kwargs):
        """Filter object by exception.

        :param kwargs: exc kwarg required.
        :return: QuerySet
        """
        kwargs = self._prepare_kwargs_by_exception(kwargs)

        return self.filter(*args, **kwargs)

    def get_by_exception(self, *args, **kwargs):
        """Get object by exception.

        :param kwargs: exc kwarg required.
        :return: Access
        """
        kwargs = self._prepare_kwargs_by_exception(kwargs)

        return self.get(*args, **kwargs)
