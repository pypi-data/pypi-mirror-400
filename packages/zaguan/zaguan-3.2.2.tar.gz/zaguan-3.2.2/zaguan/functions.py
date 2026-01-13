from gi.repository.GLib import idle_add


def asynchronous_gtk_message(fun):
    """
    Genera un wrapper de la funcion que se pasa como parametro (``fun``) para ejecutarla de forma asíncrona usando
    :func:`GLib.idle_add <GLib.idle_add>`.

    Parameters:
        fun (function): la funcion a wrappear

    Returns:
        fun2: la funcion wrappeada.

    .. function::  asynchronous_gtk_message.worker(param)

        Ejecuta una funcion con sus ``*args`` y ``**kargs``. Obtiene la funcion y sus parámetros de ``param``

        :param param: tupla que debe contener (funcion_a_ejecutar, \*args, \*\*kargs)
        :type param: tuple

    .. function:: asynchronous_gtk_message.fun2(\*args, \*\*kargs)

        Ejecuta la funcion :func:`GLib.idle_add <GLib.idle_add>` pasándole un
        :meth:`asynchronous_gtk_message.worker <asynchronous_gtk_message.worker>` y como ``*data`` la tupla
        ``(fun,*args,**kargs)``

    """
    def worker(param):
        (function, args, kwargs) = param
        function(*args, **kwargs)

    def fun2(*args, **kwargs):
        idle_add(worker, (fun, args, kwargs))

    return fun2
