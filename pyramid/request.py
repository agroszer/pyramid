from zope.interface import implements
from zope.interface.interface import InterfaceClass

from webob import Request as WebobRequest

from pyramid.interfaces import IRequest
from pyramid.interfaces import ISessionFactory

from pyramid.exceptions import ConfigurationError
from pyramid.decorator import reify
from pyramid.url import model_url
from pyramid.url import route_url
from pyramid.url import static_url

class TemplateContext(object):
    pass

class Request(WebobRequest):
    """
    A subclass of the :term:`WebOb` Request class.  An instance of
    this class is created by the :term:`router` and is provided to a
    view callable (and to other subsystems) as the ``request``
    argument.

    The documentation below (save for the ``add_response_callback`` and
    ''add_finished_callback`` methods, which are defined in this subclass
    itself, and the attributes ``context``, ``registry``, ``root``,
    ``subpath``, ``traversed``, ``view_name``, ``virtual_root`` , and
    ``virtual_root_path``, each of which is added to the request by the
    :term:`router` at request ingress time) are autogenerated from the WebOb
    source code used when this documentation was generated.

    Due to technical constraints, we can't yet display the WebOb
    version number from which this documentation is autogenerated, but
    it will be the 'prevailing WebOb version' at the time of the
    release of this :app:`Pyramid` version.  See
    http://http://pythonpaste.org/webob/ for further information.
    """
    implements(IRequest)
    response_callbacks = ()
    finished_callbacks = ()
    exception = None
    matchdict = None
    matched_route = None

    @reify
    def tmpl_context(self):
        """ Template context (for Pylons apps) """
        return TemplateContext()

    def add_response_callback(self, callback):
        """
        Add a callback to the set of callbacks to be called by the
        :term:`router` at a point after a :term:`response` object is
        successfully created.  :app:`Pyramid` does not have a
        global response object: this functionality allows an
        application to register an action to be performed against the
        response once one is created.

        A 'callback' is a callable which accepts two positional
        parameters: ``request`` and ``response``.  For example:

        .. code-block:: python
           :linenos:

           def cache_callback(request, response):
               'Set the cache_control max_age for the response'
               response.cache_control.max_age = 360
           request.add_response_callback(cache_callback)

        Response callbacks are called in the order they're added
        (first-to-most-recently-added).  No response callback is
        called if an exception happens in application code, or if the
        response object returned by :term:`view` code is invalid.

        All response callbacks are called *after* the
        :class:`pyramid.events.NewResponse` event is sent.

        Errors raised by callbacks are not handled specially.  They
        will be propagated to the caller of the :app:`Pyramid`
        router application.

        See also: :ref:`using_response_callbacks`.
        """

        callbacks = self.response_callbacks
        if not callbacks:
            callbacks = []
        callbacks.append(callback)
        self.response_callbacks = callbacks

    def _process_response_callbacks(self, response):
        callbacks = self.response_callbacks
        while callbacks:
            callback = callbacks.pop(0)
            callback(self, response)

    def add_finished_callback(self, callback):
        """
        Add a callback to the set of callbacks to be called
        unconditionally by the :term:`router` at the very end of
        request processing.

        ``callback`` is a callable which accepts a single positional
        parameter: ``request``.  For example:

        .. code-block:: python
           :linenos:

           import transaction

           def commit_callback(request):
               '''commit or abort the transaction associated with request'''
               if request.exception is not None:
                   transaction.abort()
               else:
                   transaction.commit()
           request.add_finished_callback(commit_callback)

        Finished callbacks are called in the order they're added (
        first- to most-recently- added).  Finished callbacks (unlike
        response callbacks) are *always* called, even if an exception
        happens in application code that prevents a response from
        being generated.

        The set of finished callbacks associated with a request are
        called *very late* in the processing of that request; they are
        essentially the last thing called by the :term:`router`. They
        are called after response processing has already occurred in a
        top-level ``finally:`` block within the router request
        processing code.  As a result, mutations performed to the
        ``request`` provided to a finished callback will have no
        meaningful effect, because response processing will have
        already occurred, and the request's scope will expire almost
        immediately after all finished callbacks have been processed.

        Errors raised by finished callbacks are not handled specially.
        They will be propagated to the caller of the :app:`Pyramid`
        router application.

        See also: :ref:`using_finished_callbacks`.
        """

        callbacks = self.finished_callbacks
        if not callbacks:
            callbacks = []
        callbacks.append(callback)
        self.finished_callbacks = callbacks

    def _process_finished_callbacks(self):
        callbacks = self.finished_callbacks
        while callbacks:
            callback = callbacks.pop(0)
            callback(self)

    @reify
    def session(self):
        """ Obtain the :term:`session` object associated with this
        request.  If a :term:`session factory` has not been registered
        during application configuration, a
        :class:`pyramid.exceptions.ConfigurationError` will be raised"""
        factory = self.registry.queryUtility(ISessionFactory)
        if factory is None:
            raise ConfigurationError(
                'No session factory registered '
                '(see the Session Objects chapter of the documentation)')
        return factory(self)

    def route_url(self, route_name, *elements, **kw):
        """ Return the URL for the route named ``route_name``, using
        ``*elements`` and ``**kw`` as modifiers.

        This is a convenience method.  The result of calling
        :meth:`pyramid.request.Request.route_url` is the same as calling
        :func:`pyramid.url.route_url` with an explicit ``request``
        parameter.

        The :meth:`pyramid.request.Request.route_url` method calls the
        :func:`pyramid.url.route_url` function using the Request object as
        the ``request`` argument.  The ``route_name``, ``*elements`` and
        ``*kw`` arguments passed to :meth:`pyramid.request.Request.route_url`
        are passed through to :func:`pyramid.url.route_url` unchanged and its
        result is returned.

        This call to :meth:`pyramid.request.Request.route_url`::

          request.route_url('route_name')

        Is completely equivalent to calling :func:`pyramid.url.route_url`
        like this::

          from pyramid.url import route_url
          route_url('route_name', request)
        """
        return route_url(route_name, self, *elements, **kw)

    def model_url(self, model, *elements, **kw):
        """ Return the URL for the model object named ``model``, using
        ``*elements`` and ``**kw`` as modifiers.

        This is a convenience method.  The result of calling
        :meth:`pyramid.request.Request.model_url` is the same as calling
        :func:`pyramid.url.model_url` with an explicit ``request`` parameter.

        The :meth:`pyramid.request.Request.model_url` method calls the
        :func:`pyramid.url.model_url` function using the Request object as
        the ``request`` argument.  The ``model``, ``*elements`` and ``*kw``
        arguments passed to :meth:`pyramid.request.Request.model_url` are
        passed through to :func:`pyramid.url.model_url` unchanged and its
        result is returned.

        This call to :meth:`pyramid.request.Request.model_url`::

          request.route_url(mymodel)

        Is completely equivalent to calling :func:`pyramid.url.model_url`
        like this::

          from pyramid.url import model_url
          route_url(model, request)
        """
        return model_url(model, self, *elements, **kw)

    def static_url(self, path, **kw):
        """ Generates a fully qualified URL for a static :term:`resource`.
        The resource must live within a location defined via the
        :meth:`pyramid.configuration.Configurator.add_static_view`
        :term:`configuration declaration` or the ``<static>`` ZCML
        directive (see :ref:`static_resources_section`).

        This is a convenience method.  The result of calling
        :meth:`pyramid.request.Request.static_url` is the same as calling
        :func:`pyramid.url.static_url` with an explicit ``request`` parameter.

        The :meth:`pyramid.request.Request.static_url` method calls the
        :func:`pyramid.url.static_url` function using the Request object as
        the ``request`` argument.  The ``*kw`` arguments passed to
        :meth:`pyramid.request.Request.static_url` are passed through to
        :func:`pyramid.url.static_url` unchanged and its result is returned.

        This call to :meth:`pyramid.request.Request.static_url`::

          request.static_url('mypackage:static/foo.css')

        Is completely equivalent to calling :func:`pyramid.url.static_url`
        like this::

          from pyramid.url import static_url
          static_url('mypackage:static/foo.css, request)

        See :func:`pyramid.url.static_url` for more information
        
        """
        return static_url(path, self, **kw)

    # override default WebOb "environ['adhoc_attr']" mutation behavior
    __getattr__ = object.__getattribute__
    __setattr__ = object.__setattr__
    __delattr__ = object.__delattr__

    # b/c dict interface for "root factory" code that expects a bare
    # environ.  Explicitly omitted dict methods: clear (unnecessary),
    # copy (implemented by WebOb), fromkeys (unnecessary)

    def __contains__(self, k):
        return self.environ.__contains__(k)

    def __delitem__(self, k):
        return self.environ.__delitem__(k)

    def __getitem__(self, k):
        return self.environ.__getitem__(k)

    def __iter__(self):
        return iter(self.environ)

    def __setitem__(self, k, v):
        self.environ[k] = v

    def get(self, k, default=None):
        return self.environ.get(k, default)

    def has_key(self, k):
        return k in self.environ

    def items(self):
        return self.environ.items()

    def iteritems(self):
        return self.environ.iteritems()

    def iterkeys(self):
        return self.environ.iterkeys()

    def itervalues(self):
        return self.environ.itervalues()

    def keys(self):
        return self.environ.keys()

    def pop(self, k):
        return self.environ.pop(k)

    def popitem(self):
        return self.environ.popitem()

    def setdefault(self, v, default):
        return self.environ.setdefault(v, default)

    def update(self, v, **kw):
        return self.environ.update(v, **kw)

    def values(self):
        return self.environ.values()

def route_request_iface(name, bases=()):
    iface = InterfaceClass('%s_IRequest' % name, bases=bases)
    # for exception view lookups
    iface.combined = InterfaceClass('%s_combined_IRequest' % name,
                                    bases=(iface, IRequest))
    return iface

def add_global_response_headers(request, headerlist):
    def add_headers(request, response):
        for k, v in headerlist:
            response.headerlist.append((k, v))
    request.add_response_callback(add_headers)

