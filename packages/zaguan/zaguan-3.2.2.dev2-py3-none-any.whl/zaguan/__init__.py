from gi.repository.Gtk import Window, WindowType, WindowPosition, main
from gi.repository.Gdk import threads_init


from time import sleep

from zaguan.controller import WebContainerController


class Zaguan(object):
    """
    Esta clase administra una ventana y le injecta un browser obtenido desde
    :meth:`WebContainerController.get_browser() <zaguan.controller.WebContainerController.get_browser>`. El browser muestra la :attr:`~Zaguan.uri`.

    Attributes:
        controller (zaguan.controller.WebContainerController): se usa para crear el browser.
        uri (str): indica los recursos que se requieren mostrar en el browser.
        on_close: funcion que se ejecuta al cerrar.
    """
    def __init__(self, uri, controller=None):
        """
        Constructor de Zaguan

        Parameters:
            uri (str): la URI del HTML a visualizar en el browser.
            controller (zaguan.controller.WebContainerController): el controlador.
        """
        if controller is None:
            controller = WebContainerController()
        self.controller = controller
        self.uri = uri
        self.on_close = None

    def run(self, settings=None, window=None, debug=False, on_close=None):
        """
        Si no se pasa una ventana, la crea y la muestra.
        Obtiene un browser desde :attr:`~Zaguan.controller` y lo injecta en la ventana.

        Parameters:
            settings (list): lista de settings a enviar al webkit.
            window (Gtk.Window): la ventana que contiene el browser donde se visualizará el HTML.
            debug (bool): indica si se debe abrir las herramientas para desarrollador del browser.
            on_close (function): funcion que se ejecutará al cerrar.
        """
        self.on_close = on_close
        threads_init()

        if window is None:
            self.window = Window(WindowType.TOPLEVEL)
            self.window.set_position(WindowPosition.CENTER_ALWAYS)
        else:
            self.window = window

        browser = self.controller.get_browser(self.uri, debug=debug,
                                              settings=settings)
        self.window.connect("delete-event", self.quit)
        self.window.set_border_width(0)
        self.window.add(browser)

        sleep(1)
        self.window.show_all()
        self.window.show()
        main()

    def quit(self, widget, event):
        """
        Funcion que se ejecuta al cerrar la ventana. Ejecuta :attr:`~on_close` con los parametros.

        Parameters:
            widget: parametro que toma cuando `Window` llama al callback al salir
            event: parametro que toma cuando `Window` llama al callback al salir

        """
        if self.on_close is not None:
            self.on_close(widget, event)
