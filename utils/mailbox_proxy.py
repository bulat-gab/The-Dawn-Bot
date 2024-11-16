import ssl
import imaplib
import sys
from imap_tools import MailBox
import socks
import better_proxy

PYTHON_VERSION_MINOR = sys.version_info.minor


class MailBoxProxy(MailBox):
    def __init__(self, proxy: better_proxy.Proxy = None, host='', port=993, timeout=None, keyfile=None, certfile=None, ssl_context=None):
        self.proxy = proxy
        if not proxy:
            raise ValueError('MailBoxProxy requires proxy')

        super().__init__(host, port, timeout, keyfile, certfile, ssl_context)

    def _get_mailbox_client(self) -> imaplib.IMAP4:
        if not self.proxy:
            return super()._get_mailbox_client()

        if PYTHON_VERSION_MINOR < 9:
            return SocksIMAP4SSL(self._host, self._port, self._keyfile, self._certfile, self._ssl_context, proxy=self.proxy)
        elif PYTHON_VERSION_MINOR < 12:
            return SocksIMAP4SSL(
                host=self._host, port=self._port, 
                keyfile=self._keyfile, certfile=self._certfile, ssl_context=self._ssl_context, timeout=self._timeout, proxy=self.proxy)
        else:
            return SocksIMAP4SSL(self._host, self._port, ssl_context=self._ssl_context, timeout=self._timeout, proxy=self.proxy)
        

# https://gist.github.com/sstevan/efccf3d5d3e73039c21aa848353ff52f
class SocksIMAP4(imaplib.IMAP4):
    """
    IMAP service trough SOCKS proxy. PySocks module required.
    """

    PROXY_TYPES = {"socks4": socks.PROXY_TYPE_SOCKS4,
                   "socks5": socks.PROXY_TYPE_SOCKS5,
                   "http": socks.PROXY_TYPE_HTTP}

    def __init__(self, host, port=imaplib.IMAP4_PORT, proxy: better_proxy.Proxy = None, rdns=True, timeout=None):
        self.proxy_addr = proxy.host
        self.proxy_port = proxy.port
        self.rdns = rdns
        self.username = proxy.login
        self.password = proxy.password

        self.proxy_type = SocksIMAP4.PROXY_TYPES[proxy.protocol.lower()]

        imaplib.IMAP4.__init__(self, host, port, timeout)

    def _create_socket(self, timeout=None):
        return socks.create_connection((self.host, self.port), proxy_type=self.proxy_type, proxy_addr=self.proxy_addr,
                                       proxy_port=self.proxy_port, proxy_rdns=self.rdns, proxy_username=self.username,
                                       proxy_password=self.password, timeout=timeout)

class SocksIMAP4SSL(SocksIMAP4):

    def __init__(self, host='', port=imaplib.IMAP4_SSL_PORT, keyfile=None, certfile=None, ssl_context=None, 
                 proxy: better_proxy.Proxy = None, rdns=True, timeout=None):

        if ssl_context is not None and keyfile is not None:
            raise ValueError("ssl_context and keyfile arguments are mutually "
                             "exclusive")
        if ssl_context is not None and certfile is not None:
            raise ValueError("ssl_context and certfile arguments are mutually "
                             "exclusive")

        self.keyfile = keyfile
        self.certfile = certfile
        if ssl_context is None:
            ssl_context = ssl._create_stdlib_context(certfile=certfile,
                                                     keyfile=keyfile)
        self.ssl_context = ssl_context

        SocksIMAP4.__init__(self, host, port, proxy=proxy, rdns=rdns, timeout=timeout)

    def _create_socket(self, timeout=None):
        sock = SocksIMAP4._create_socket(self, timeout=timeout)
        server_hostname = self.host if ssl.HAS_SNI else None
        return self.ssl_context.wrap_socket(sock, server_hostname=server_hostname)

    # Looks like newer versions of Python changed open() method in IMAP4 lib.
    # Adding timeout as additional parameter should resolve issues mentioned in comments.
    # Check https://github.com/python/cpython/blob/main/Lib/imaplib.py#L202 for more details.
    def open(self, host='', port=imaplib.IMAP4_PORT, timeout=None):
        SocksIMAP4.open(self, host, port, timeout)