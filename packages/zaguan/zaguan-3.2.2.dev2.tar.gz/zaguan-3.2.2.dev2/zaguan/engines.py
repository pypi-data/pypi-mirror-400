import sys
import gi


def get_wk_implementation(webkit_version):
    """Retorna el webkit wrapper de Zaguan segun la version.

    Arguments:
        webkit_version (int): la version de webkit a usar. Puede ser 1 o 2.
    """
    implementation = WebKit2Methods
    if webkit_version == 1:
        implementation = WebKitMethods

    return implementation


class WebKitMethods(object):
    """Clase que implementa métodos estaticos para la version 1 de WebKit."""
    @staticmethod
    def create_browser(debug=False, cache_model=None, process_model=None):
        """Crea la instancia de :class:`WebView <WebKit2.WebView>` y la configura correctamente.

        Parameters:
            debug (bool): indica si se debe abrir herramientas para desarrollador.
            cache_model (CacheModel): indica el comportamiento de la cache del browser.
            process_model: sin uso.

        Returns:
            WebView: la instancia de ``WebView`` configurada.
        """
        gi.require_version('WebKit', '3.0')
        from gi.repository.WebKit import WebView, WebSettings, set_cache_model

        if debug:
            WebKitMethods.print_version()

        if cache_model is not None:
            # http://lazka.github.io/pgi-docs/WebKit-3.0/functions.html#WebKit.set_cache_model
            set_cache_model(cache_model)

        # Setting for WebKit via git http://lazka.github.io/pgi-docs/#WebKit-3.0/classes/WebSettings.html
        settings = WebSettings()
        settings.set_property('enable-accelerated-compositing', True)
        settings.set_property('enable-file-access-from-file-uris', True)

        settings.set_property('enable-default-context-menu', not debug)

        webview = WebView()
        webview.set_settings(settings)
        return webview

    @staticmethod
    def inject_javascript(browser, script):
        """Injecta JavaScript en un objeto ``WebView``.

        Parameters:
            browser (WebView): el objeto ``WebView`` destino.
            script (str): el script JS a correr.
        """
        browser.execute_script(script)

    @staticmethod
    def open_uri(browser, uri):
        """Abre una URI en el browser.

        Parameters:
            browser (WebView): el objeto ``WebView`` destino.
            uri (str): la URI del contenido a abrir en el browser.
        """
        browser.open(uri)

    @staticmethod
    def set_settings(browser, user_settings):
        """Agrega las settings al browser.

        Parameters:
            browser (WebView): el objeto ``WebView`` destino.
            user_settings: las settings a agregar al browser.
        """
        browser_settings = browser.get_settings()
        if user_settings is not None:
            for setting, value in user_settings:
                browser_settings.set_property(setting, value)

    @staticmethod
    def get_inspector(browser):
        """Obtiene el Inspector de la instancia de ``WebKit``.

        Parameters:
            browser (WebView): el objeto ``WebView`` destino.

        Returns:
            Inspector: el inspector de zaguan.
        """
        ret = None
        try:
            from zaguan_inspector import Inspector

            inspector = browser.get_inspector()
            ret = Inspector(inspector)
        except ImportError:
            pass

        return ret

    @staticmethod
    def connect(browser, callback):
        """Conecta el evento de navegación al browser.

        Parameters:
            browser (WebView): el objeto ``WebView`` destino.
            callback (function): la función callback.
        """
        browser.connect("resource-request-starting", callback)

    @staticmethod
    def print_version():
        """Hace un print con la version de WebKit."""
        from gi.repository.WebKit import (major_version, minor_version,
                                          micro_version)
        version = "{}.{}.{}".format(major_version(), minor_version(),
                                    micro_version())
        print("Cargando WebKit: {}".format(version))


class WebKit2Methods(object):
    """Clase que implementa métodos estaticos para la version 2 de WebKit."""
    @staticmethod
    def create_browser(debug=False, cache_model=None, process_model=None):
        """Crea la instancia de :class:`WebView <WebKit2.WebView>` y la configura correctamente.

        Parameters:
            debug (bool): indica si se debe abrir herramientas para desarrollador.
            cache_model (WebKit2.CacheModel): indica el comportamiento de la cache del browser.
            process_model: sin uso.

        Returns:
            WebKit2.WebView: la instancia de ``WebKit2.WebView`` configurada.
        """
        py_version = sys.version_info
        try:
            webkit2_version = "4.1" if py_version >= (3, 12) else "4.0"
            gi.require_version("WebKit2", webkit2_version)
        except ImportError:
            gi.require_version("WebKit2", "4.0")
        from gi.repository.WebKit2 import WebView, Settings

        if debug:
            WebKit2Methods.print_version()

        settings = Settings()
        settings.set_allow_file_access_from_file_urls(True)
        if debug:
            settings.set_enable_developer_extras(True)
            settings.set_enable_write_console_messages_to_stdout(True)
        webview = WebView()

        if cache_model is not None:
            # http://lazka.github.io/pgi-docs/WebKit2-4.0/classes/WebContext.html#WebKit2.WebContext.set_cache_model
            context = webview.get_context()
            context.set_cache_model(cache_model)

        if process_model is not None:
            # http://lazka.github.io/pgi-docs/WebKit2-4.0/classes/WebContext.html#WebKit2.WebContext.set_process_model
            context = webview.get_context()
            context.set_process_model(process_model)

        if not debug:
            # https://people.gnome.org/~gcampagna/docs/WebKit2-3.0/WebKit2.WebView-context-menu.html
            def menu_contextual(webview, context_menu, event, hit_test_result):
                context_menu.remove_all()

            webview.connect('context-menu', menu_contextual)

        webview.set_settings(settings)
        return webview

    @staticmethod
    def inject_javascript(browser, script):
        """Injecta JavaScript en un objeto :class:`WebKit2.WebView`.

        Parameters:
            browser (WebKit2.WebView): el objeto ``WebView`` destino.
            script (str): el script JS a correr.
        """
        browser.run_javascript(script)

    @staticmethod
    def open_uri(browser, uri):
        """Abre una URI en el browser.

        Parameters:
            browser (WebKit2.WebView): el objeto ``WebView`` destino.
            uri (str): la URI del contenido a abrir en el browser.
        """
        browser.load_uri(uri)

    @staticmethod
    def set_settings(browser, user_settings):
        """Agrega las settings al browser.

        Parameters:
            browser (WebKit2.WebView): el objeto ``WebView`` destino.
            user_settings: las settings a agregar al browser.
        """
        browser_settings = browser.get_settings()
        if user_settings is not None:
            for setting, value in user_settings:
                browser_settings.set_property(setting, value)

    @staticmethod
    def connect(browser, callback):
        """Conecta el evento de navegación al browser.

        Parameters:
            browser (WebKit2.WebView): el objeto ``WebView`` destino.
            callback (function): la función callback.
        """
        browser.connect("resource-load-started", callback)

    @staticmethod
    def print_version():
        """Hace un print con la version de WebKit."""
        from gi.repository.WebKit2 import (get_major_version,
                                           get_minor_version,
                                           get_micro_version)

        version = "{}.{}.{}".format(get_major_version(), get_minor_version(),
                                    get_micro_version())
        print("Cargando WebKit: {}".format(version))
