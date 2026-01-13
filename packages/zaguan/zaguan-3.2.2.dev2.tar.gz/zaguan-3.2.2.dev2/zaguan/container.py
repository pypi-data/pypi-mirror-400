from zaguan.engines import get_wk_implementation
from zaguan.functions import asynchronous_gtk_message


def launch_browser(uri, debug=False, user_settings=None, window=None,
                   webkit_version=None, debug_callback=None):
    """Crea e inicializa el objeto browser.

    Parameters:
        debug (boolean): indica si se debe mostrar informacion de debug.
        user_settings (dict): diccionario que contiene las settings que se deben pasar al webkit.
        window (Gtk.Window): objeto al que se le va a injetar el browser.
        webkit_version (int): la version de webit a usar. Puede ser 1 o 2.

    .. todo::
        El contenido de esta funcion podría ir directamente dentro del método
        :meth:`WebContainerController.get_browser() <zaguan.controller.WebContainerController.get_browser>` ya
        que es el unico punto donde se usa.

    Returns
    -----------------

        browser : :class:`WebKit2.WebView`
            la instancia de ``WebView``.

        _web_send : :meth:`launcher_browser._web_send`
            la funcion para ejecutar JS en el browser.

        implementation: :class:`WebKitMethods <zaguan.engines.WebKitMethods>` o :class:`WebKit2Methods <zaguan.engines.WebKit2Methods>`
            instancia del wrapper Zaguan segun la version elegida de WebKit.

    .. function:: launcher_browser._web_send(msg)

        Inyecta javascript de forma asíncrona en la vista. Esta funcion es uno de los valores a devolver
        por :meth:`launch_browser`.

        :param msg: el codigo javascript a correr en el browser
        :type msg: str

    """
    implementation = get_wk_implementation(webkit_version)

    browser = implementation.create_browser(debug)
    implementation.set_settings(browser, user_settings)

    implementation.open_uri(browser, uri)

    def _web_send(msg):
        if debug:
            if debug_callback is None:
                msg_len = 80
                print('>>>', msg[:msg_len],
                      "..." if len(msg) > msg_len else "")
            else:
                debug_callback(msg)

        func = asynchronous_gtk_message(implementation.inject_javascript)
        func(browser, msg)

    return browser, _web_send, implementation
