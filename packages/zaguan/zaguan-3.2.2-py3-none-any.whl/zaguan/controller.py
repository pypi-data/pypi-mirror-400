from json import dumps, loads
from urllib.parse import unquote

from zaguan.container import launch_browser


class WebContainerController(object):
    """
    Clase base para los controladores de contenedores web. Controla la interaccion con el browser en ambas direcciones.


    Attributes:
        processors (list): lista de procesadores.
        inspector (ZaguanInspector): se instancia solo cuando se usa WebKit version 1.

    """
    def __init__(self):
        """
        Constructor de la clase. Inicializa :attr:`WebContainerController.processors` con una lista vacía.
        """
        self.processors = []

    def on_navigation_requested(self, webview, resource, request, *args):
        """
        Este es el método que se ejecuta cada vez que en el browser se pide cargar una URI. Llama
        a :meth:`WebContainerController.process_uri() <WebContainerController.process_uri>` con la URI que obtiene de
        la request que se pasa como parametro.

        Los argumentos cambian segun la version de WebKit:

        * Version 1: no existe documentacion.
        * Version 2: http://lazka.github.io/pgi-docs/WebKit2-4.0/classes/WebView.html#WebKit2.WebView.signals.resource_load_started

        """
        uri = request.get_uri()

        self.process_uri(uri)

    def process_uri(self, uri):
        """Por cada procesador registrado manda a procesar la URI.

        Parameters:
            uri (str): la URI a procesar.
        """
        for processor in self.processors:
            processor(uri)

    def set_screen(self, screen, **kwargs):
        """Envia el comando 'change_screep' al broswer.

        Parameters:
            screen (str): pantalla a la que se quiere cambiar.
            kargs: otros argumentos
        """
        self.send_command("change_screen", [screen, kwargs])

    def send_command(self, command, data=None):
        """ Inyecta la ejecucion de un comando en el browser.

        Parameters:
            command (str): el comando a ejecutar en el browser.
            data (any): los datos que se envian como parametros del comando.
        """
        json_data = dumps(data).replace("\\\"", "\\\'")
        self.send_function("run_op('%s', '%s')" % (command, json_data))

    def get_browser(self, uri, settings=None, debug=False,
                    webkit_version=None, debug_callback=None):
        """
        Obtiene el browser, el metodo para inyectar JS y la implementacion del wrapper de WebKit. Conecta el método
        :meth:`WebContainerController.on_navigation_requested <WebContainerController.on_navigation_requested>` al
        evento ``resource-request-starting`` del browser, esto es para poder atender a nuevas peticiones de URI.

        .. todo::
            Esto debería ser tarea del constructor. ``get_browser`` solo debería devolver el browser.

        Arguments:
            uri (str): the URI of the HTML to open with the web view.
            settings (list): the settings send to webkit.
            debug (boolean):
                to indicate if it should output debug and add context menu and inspector.
            webkit_version (int): the webkit gtk version (1 or 2)

        Returns:
            WebKit2.WebView: el objeto ``WebView``
        """
        if settings is None:
            settings = []

        if debug and webkit_version == 1:
            settings.append(('enable-default-context-menu', True))
            settings.append(('enable-developer-extras', True))

        browser, web_send, implementation = launch_browser(
            uri, debug=debug, user_settings=settings,
            webkit_version=webkit_version, debug_callback=debug_callback)

        self.send_function = web_send
        implementation.connect(browser, self.on_navigation_requested)

        if debug and webkit_version == 1:
            self.inspector = implementation.get_inspector(browser)

        return browser

    def add_processor(self, url_word, instance=None):
        """
        Agrega una instancia de la funcion ``_inner`` a la lista de procesadores para que desde el browser se
        pueda llamar a metodos de Python. Para mas detalles ver la documentacion de
        :meth:`_inner() <add_processor._inner>`.

        Parameters:
            url_word (str):
                Clave que linkea una URI con el procesador ``instance``.
            instance (zaguan.actions.BaseActionController):
                Una instancia de ``BaseActionController`` que debe tener implementados los metodos que se intentaran
                ejecutar desde el browser para la URI.

        .. function:: add_processor._inner(uri)

            Si alguna parte de la URI coincide con ``url_word`` entonces procesa el texto restante
            y lo divide en dos partes: el nombre del método y los datos (parámetros a pasar al metodo).
            Busca el método en la instancia de :class:`BaseActionController <zaguan.actions.BaseActionController>`
            (``instance``) y si existe lo ejecuta.

            :param uri: la URI a parsear.
            :type uri: str
            :raise NotImplementedError:
                excepcion que se lanza cuando el método que está llamando el browser no fué
                implementado en la instancia de :class:`BaseActionController <zaguan.actions.BaseActionController>`.

        """

        def _inner(uri):
            scheme, path = uri.split(':', 1)
            if scheme == "http":
                parts = path.split("/")[2:]
                if parts[0] == url_word:
                    remain = parts[1]
                elif parts[1] == url_word:
                    remain = parts[2]
                else:
                    remain = None
                if remain is not None:
                    try:
                        action, data = remain.split("?")
                    except ValueError:
                        action = remain
                        data = "null"

                    data = loads(unquote(data))
                    # search the action at the 'action controller' instance
                    # argument. if we dont find the action, we try to get it
                    # from the controller itself.
                    method = getattr(instance, action, None)
                    if method is None:
                        method = getattr(self, action, None)

                    if not method:
                        raise NotImplementedError(action)
                    return method(data)

        self.processors.append(_inner)
