from .execution_log import ExecutionLog
import logging


class ILogger:
    """
    logger interface used within a pipeline and context.
    """

    def write_log(self, message: str = None, level: int = logging.INFO):
        """
        write a log
        :param str message: message to write.
        :param int level: use logging level.
        """
        pass

    def notify(self):
        """
        notify the listeners and watchers on current status.
        """
        pass
