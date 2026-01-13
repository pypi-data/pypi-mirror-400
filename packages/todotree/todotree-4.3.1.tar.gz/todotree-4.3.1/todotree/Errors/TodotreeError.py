
class TodotreeError(Exception):
    """
    Generic Exception class for application specific exceptions.
    """
    def __init__(self, message=""):
        self.message = message

        super().__init__(message)

    def __str__(self):
        return self.message

    def echo_and_exit(self, config: 'Config'):
        """
        Emit some error messages and exit the application.
        """
        config.console.error(str(self))
        exit(1)

    def warn_and_continue(self, config: 'Config'):
        """
        Emit some warning messages and continue the application.
        """
        config.console.warning(str(self))
