from P4 import P4, P4Exception, OutputHandler, ReportHandler

from ..utility import *


class PerforceHandler(OutputHandler):
    def __init__(self, _in_logger: logging.Logger):
        OutputHandler.__init__(self)
        self.logger = _in_logger

    def outputInfo(self, i):
        self.logger.debug(i)
        return OutputHandler.HANDLED

    def outputMessage(self, msg):
        self.logger.info(msg)
        return OutputHandler.HANDLED


class Perforce:
    """
    Wrapper around P4 for quick helpers
    """

    _logger = register_logger('perforce')

    @staticmethod
    @lru_cache()
    def get_ci_client_prefix():
        """
        Returns a prefix to be appended to all CI workspaces
        """

        return f'runner{ci_runner_id()}_'

    def __init__(self, port: str, user: str, password: str, charset: str = 'utf8', fingerprint: str = None):
        """
        @param port:
        @param user:
        @param password:
        @param charset:
        @param fingerprint:
        """

        self.p4 = P4()
        self.p4.exception_level = P4.RAISE_ERRORS

        self.p4.port = port
        self.p4.user = user
        self.p4.password = password
        self.p4.charset = charset

        # Logging support
        self.p4.handler = PerforceHandler(self._logger)
        self.p4.logger = self._logger

        self.fingerprint = fingerprint

    def login(self):
        self.p4.connect()

        # Trust the P4 server before doing anything else
        if self.fingerprint is not None:
            self.p4.run('trust', '-i', self.fingerprint)

        self.p4.run_login()

        # Update the environment variables for future P4 CLI calls
        # unfortunately we need this as certain things in Unreal call p4 directly
        os.environ['P4PORT'] = self.p4.port
        os.environ['P4USER'] = self.p4.user
        os.environ['P4CHARSET'] = self.p4.charset

    def update_client(self, name: str, root: str = None, view: list[str] = None):
        """
        Updates the specified client, or creates it with the given details if it doesn't already exist

        @todo handle allowing client options

        Formatted vars in views:s
        $NAME = name
        """

        client = self.p4.fetch_client(name)
        client['Client'] = name
        if root is not None:
            # cleaned_root = root.replace('\\', '/')
            # if not cleaned_root.endswith('/'):
            #     cleaned_root += '/'

            client['Root'] = root

        if view is not None:
            view_list = [x.replace('$NAME', name) for x in view]
            client['View'] = view_list

        client['Options'] = 'allwrite clobber nocompress nomodtime normdir'

        self.p4.save_client(client)

    def sync_workspace(self, name: str, dry_run: bool = False):
        """
        Syncs the workspace to the latest revision

        @todo Handle allowing to sync to specific revision
        @todo Handle clearing the workspace we set

        """

        args = []
        if dry_run:
            args.append('-n')

        # We have to set this here, because we can't manually set global opts
        self.p4.client = name
        self.p4.run_sync(*args)

    def get(self) -> P4:
        """
        Returns the internal P4 object
        """
        return self.p4
