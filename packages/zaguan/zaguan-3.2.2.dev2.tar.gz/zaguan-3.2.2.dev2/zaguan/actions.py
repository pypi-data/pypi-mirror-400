class BaseActionController(object):
    """Clase base para las acciones que son enlazadas con los controladores que heredan de
    :class:`WebContainerController <zaguan.controller.WebContainerController>`

    Attributes:
        __controler (zaguan.controller.WebContainerController): controlador con el cual interactua la clase.
    """

    def __init__(self, controller):
        """
        Constructor de la clase. Establece el link con un controlador.

        Parameters:
            controller (zaguan.controller.WebContainerController): el controlador a linkear.
        """
        self.__controller = controller

    @property
    def controller(self):
        """Getter para ``__controller``.

        Returns:
           zaguan.controller.WebContainerController: el controlador
        """
        return self.__controller

    def send_command(self, *args, **kwargs):
        """
        Envía un comando al controlador utilizando el método
        :meth:`WebContainerController.send_command() <zaguan.controller.WebContainerController.send_command>` pasando
        ``*args`` y  ``**kwargs``
        """
        self.controller.send_command(*args, **kwargs)
