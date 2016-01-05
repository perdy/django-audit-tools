==========
Middleware
==========

.. automodule:: audit_tools.audit.middleware

.. autoclass:: AuditMiddleware

    .. automethod:: process_view(self, request, view_func, view_args, view_kwargs)
    .. automethod:: process_response(self, request, response)
    .. automethod:: process_exception(self, request, exception)