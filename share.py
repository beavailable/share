#!/bin/env python3
import sys
import signal
import os
import argparse
import functools
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler, HTTPStatus
from http import cookies
from urllib import parse
import html
import mimetypes
import base64
import io
import time
import stat
import re
import socket
import ssl
import tarfile


class ShareServer(ThreadingHTTPServer):

    def __init__(self, *args, **kwargs):
        if is_windows():
            self._print_error = self._print_error_windows
        else:
            self._print_error = self._print_error_unix
        super().__init__(*args, **kwargs)

    def handle_error(self, request, client_address):
        year, month, day, hh, mm, ss, x, y, z = time.localtime()
        t, value, traceback = sys.exc_info()
        self._print_error(f'{year:04}/{month:02}/{day:02} {hh:02}:{mm:02}:{ss:02} - {client_address[0]}:{client_address[1]} - {t.__name__}: {value}')

    def _print_error_windows(self, msg):
        sys.stderr.write(f'{msg}\n')

    def _print_error_unix(self, msg):
        if sys.stderr.isatty():
            sys.stderr.write(f'\033[33m{msg}\033[0m\n')
        else:
            sys.stderr.write(f'{msg}\n')


class BaseHandler(BaseHTTPRequestHandler):

    protocol_version = 'HTTP/1.1'
    ico = base64.b64decode('AAABAAMAMDAAAAEAIACoJQAANgAAACAgAAABACAAqBAAAN4lAAAQEAAAAQAgAGgEAACGNgAAKAAAADAAAABgAAAAAQAgAAAAAAAAJAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHGzPAFxszwhcbM8U3GzPGZxszxncbM8Z3GzPGdxszxncbM8Z3GzPGdxszxncbM8Z3GzPGdxszxncbM8Z3GzPGdxszxncbM8Z3GzPGdxszxncbM8Z3GzPGdxszxncbM8Z3GzPGdxszxncbM8Z3GzPGdxszxncbM8Z3GzPGdxszxncbM8Z3GzPGdxszxncbM8Z3GzPGdxszxncbM8ZnGzPFNxszwhcbM8AQAAAAAAAAAAAAAAAAAAAAAAAAAAcbM8B3GzPGxxszzccbM8/HGzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPPxxszzccbM8bHGzPAcAAAAAAAAAAAAAAAAAAAAAcbM8bHGzPPZxszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM89nGzPGwAAAAAAAAAAAAAAABxszwhcbM823GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPNtxszwhAAAAAAAAAABxszxTcbM8+3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPPtxszxTAAAAAAAAAABxszxmcbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxmAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8+3GzPOFxszzHcbM8x3GzPOFxszz8cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszzccbM8bHGzPCJxszwMcbM8DXGzPCJxszxscbM83XGzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPNNxszw3AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAcbM8OHGzPNRxszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM88XGzPE0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHGzPE5xszzycbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8s3GzPAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHGzPAlxszy0cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8fQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABxszx+cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8bgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABxszxvcbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz+cbM8cwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABxszyFcbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPOFxszx4cbM8FQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHGzPBBxszzCcbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz0cbM8onGzPC9xszwBAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHGzPGZxszz5cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP5xszzccbM8mXGzPHFxszxxcbM8mHGzPNxxszz+cbM8/XGzPMdxszxScbM8CAAAAAAAAAAAcbM8AXGzPDJxszxDcbM8BAAAAAAAAAAAAAAAAAAAAABxszwDcbM8V3GzPOZxszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8+3GzPKBxszwkcbM8AQAAAAAAAAAAcbM8AXGzPCVxszyTcbM8fHGzPBcAAAAAAAAAAAAAAABxszwXcbM8enGzPORxszzvcbM8lXGzPEJxszwkcbM8JHGzPENxszyVcbM873GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8oHGzPA4AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABxszwEcbM8AgAAAAAAAAAAcbM8B3GzPFFxszzGcbM8/XGzPP9xszz/cbM8/3GzPPVxszzlcbM85XGzPPVxszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszzdcbM8JwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHGzPAFxszwucbM8oXGzPPRxszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszyacbM8AQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHGzPFRxszzicbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxzAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHGzPHRxszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxzAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHGzPHRxszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszyacbM8AQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHGzPFNxszzicbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszzdcbM8JwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHGzPAFxszwucbM8oHGzPPNxszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8n3GzPA4AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABxszwEcbM8AgAAAAAAAAAAcbM8B3GzPFFxszzGcbM8/XGzPP9xszz/cbM8/3GzPPVxszzlcbM85XGzPPVxszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8+3GzPKBxszwkcbM8AQAAAAAAAAAAcbM8AXGzPCVxszyTcbM8fHGzPBcAAAAAAAAAAAAAAABxszwWcbM8enGzPORxszzvcbM8lXGzPEJxszwkcbM8JHGzPENxszyVcbM873GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP5xszzccbM8mXGzPHFxszxxcbM8mHGzPNxxszz+cbM8/XGzPMdxszxScbM8CAAAAAAAAAAAcbM8AXGzPDJxszxCcbM8BAAAAAAAAAAAAAAAAAAAAABxszwDcbM8VnGzPOZxszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz0cbM8onGzPC9xszwBAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHGzPGZxszz5cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPOJxszx4cbM8FQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHGzPBBxszzCcbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz+cbM8cwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABxszyFcbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8bgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABxszxvcbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8fQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABxszx+cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8s3GzPAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHGzPAlxszy0cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM88XGzPE0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHGzPE5xszzycbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPNNxszw3AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAcbM8OHGzPNRxszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszzccbM8bHGzPCJxszwMcbM8DXGzPCJxszxscbM83XGzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8+3GzPOFxszzHcbM8x3GzPOFxszz8cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxmcbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxmAAAAAAAAAABxszxTcbM8+3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPPtxszxTAAAAAAAAAABxszwhcbM823GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPNtxszwhAAAAAAAAAAAAAAAAcbM8bHGzPPZxszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM89nGzPGwAAAAAAAAAAAAAAAAAAAAAcbM8B3GzPGxxszzccbM8/HGzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPPxxszzccbM8bHGzPAcAAAAAAAAAAAAAAAAAAAAAAAAAAHGzPAFxszwhcbM8U3GzPGZxszxncbM8Z3GzPGdxszxncbM8Z3GzPGdxszxncbM8Z3GzPGdxszxncbM8Z3GzPGdxszxncbM8Z3GzPGdxszxncbM8Z3GzPGdxszxncbM8Z3GzPGdxszxncbM8Z3GzPGdxszxncbM8Z3GzPGdxszxncbM8Z3GzPGdxszxncbM8Z3GzPGdxszxncbM8ZnGzPFNxszwhcbM8AQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP///////wAA////////AADwAAAAAA8AAOAAAAAABwAAwAAAAAADAADAAAAAAAMAAMAAAAAAAwAAwAAAAAADAADAAAAAAAMAAMAAAAfgAwAAwAAAD/ADAADAAAAf+AMAAMAAAB/4AwAAwAAAP/wDAADAAAA//AMAAMAAAD/4AwAAwAAAf/gDAADAAAD/+AMAAMABg//wAwAAwAfv48ADAADAD/+AAAMAAMAf/gAAAwAAwB/8AAADAADAP/wAAAMAAMA//AAAAwAAwB/8AAADAADAH/4AAAMAAMAP/4AAAwAAwAfv48ADAADAAYP/8AMAAMAAAP/4AwAAwAAAf/gDAADAAAA/+AMAAMAAAD/8AwAAwAAAP/wDAADAAAAf+AMAAMAAAB/4AwAAwAAAD/ADAADAAAAH4AMAAMAAAAAAAwAAwAAAAAADAADAAAAAAAMAAMAAAAAAAwAAwAAAAAADAADgAAAAAAcAAPAAAAAADwAA////////AAD///////8AACgAAAAgAAAAQAAAAAEAIAAAAAAAABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHGzPAFxszwOcbM8GXGzPBlxszwZcbM8GXGzPBlxszwZcbM8GXGzPBlxszwZcbM8GXGzPBlxszwZcbM8GXGzPBlxszwZcbM8GXGzPBlxszwZcbM8GXGzPBlxszwZcbM8GXGzPBlxszwZcbM8DnGzPAEAAAAAAAAAAAAAAABxszwHcbM8ZHGzPMFxszzUcbM81HGzPNRxszzUcbM81HGzPNRxszzUcbM81HGzPNRxszzUcbM81HGzPNRxszzUcbM81HGzPNRxszzUcbM81HGzPNRxszzUcbM81HGzPNRxszzUcbM81HGzPNRxszzBcbM8ZHGzPAcAAAAAAAAAAHGzPGRxszz2cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz2cbM8ZAAAAABxszwNcbM8v3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszy/cbM8DXGzPBhxszzUcbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPNRxszwYcbM8GXGzPNRxszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPPlxszzdcbM80HGzPOdxszz+cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM81HGzPBlxszwZcbM81HGzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszzjcbM8Z3GzPBxxszwRcbM8K3GzPJRxszz4cbM8/3GzPP9xszz/cbM8/3GzPP9xszzUcbM8GXGzPBlxszzUcbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM883GzPFcAAAAAAAAAAAAAAAAAAAAAcbM8CXGzPJhxszz/cbM8/3GzPP9xszz/cbM8/3GzPNRxszwZcbM8GXGzPNRxszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszy8cbM8CwAAAAAAAAAAAAAAAAAAAAAAAAAAcbM8NHGzPO1xszz/cbM8/3GzPP9xszz/cbM81HGzPBlxszwZcbM81HGzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPJwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABxszwacbM823GzPP9xszz/cbM8/3GzPP9xszzUcbM8GXGzPBlxszzUcbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz2cbM8ewAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHGzPCpxszzncbM8/3GzPP9xszz/cbM8/3GzPNRxszwZcbM8GXGzPNRxszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPPxxszz+cbM8/3GzPP9xszz9cbM8yHGzPFJxszwIAAAAAAAAAAAAAAAAAAAAAAAAAABxszwBcbM8fXGzPP9xszz/cbM8/3GzPP9xszz/cbM81HGzPBlxszwZcbM81HGzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPNZxszx6cbM8UXGzPGRxszy3cbM84HGzPHxxszwXAAAAAHGzPBlxszxtcbM8QnGzPAhxszwCcbM8EXGzPG1xszztcbM8/3GzPP9xszz/cbM8/3GzPP9xszzUcbM8GXGzPBlxszzUcbM8/3GzPP9xszz/cbM8/3GzPP9xszzKcbM8KwAAAAAAAAAAAAAAAHGzPBBxszwkcbM8AnGzPAhxszxTcbM8yHGzPP1xszztcbM8unGzPKlxszzLcbM8+HGzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPNRxszwZcbM8GXGzPNRxszz/cbM8/3GzPP9xszz/cbM893GzPFIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABxszwscbM8o3GzPPRxszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM81HGzPBlxszwZcbM81HGzPP9xszz/cbM8/3GzPP9xszzfcbM8HgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHGzPJlxszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszzUcbM8GXGzPBlxszzUcbM8/3GzPP9xszz/cbM8/3GzPN9xszweAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAcbM8mXGzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPNRxszwZcbM8GXGzPNRxszz/cbM8/3GzPP9xszz/cbM893GzPFIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABxszwscbM8o3GzPPRxszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM81HGzPBlxszwZcbM81HGzPP9xszz/cbM8/3GzPP9xszz/cbM8ynGzPCsAAAAAAAAAAAAAAABxszwQcbM8JHGzPAJxszwIcbM8U3GzPMhxszz9cbM87XGzPLpxszypcbM8y3GzPPhxszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszzUcbM8GXGzPBlxszzUcbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM81nGzPHlxszxRcbM8ZHGzPLdxszzgcbM8fHGzPBcAAAAAcbM8GXGzPG1xszxCcbM8CHGzPAJxszwRcbM8bXGzPO1xszz/cbM8/3GzPP9xszz/cbM8/3GzPNRxszwZcbM8GXGzPNRxszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPPxxszz+cbM8/3GzPP9xszz9cbM8yHGzPFNxszwIAAAAAAAAAAAAAAAAAAAAAAAAAABxszwBcbM8fXGzPP9xszz/cbM8/3GzPP9xszz/cbM81HGzPBlxszwZcbM81HGzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM89nGzPHsAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABxszwqcbM853GzPP9xszz/cbM8/3GzPP9xszzUcbM8GXGzPBlxszzUcbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHGzPBpxszzbcbM8/3GzPP9xszz/cbM8/3GzPNRxszwZcbM8GXGzPNRxszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszy8cbM8CwAAAAAAAAAAAAAAAAAAAAAAAAAAcbM8NHGzPO1xszz/cbM8/3GzPP9xszz/cbM81HGzPBlxszwZcbM81HGzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPPNxszxXAAAAAAAAAAAAAAAAAAAAAHGzPAlxszyYcbM8/3GzPP9xszz/cbM8/3GzPP9xszzUcbM8GXGzPBlxszzUcbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPONxszxncbM8HHGzPBFxszwrcbM8lHGzPPhxszz/cbM8/3GzPP9xszz/cbM8/3GzPNRxszwZcbM8GXGzPNRxszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPPlxszzdcbM80HGzPOdxszz+cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM81HGzPBlxszwYcbM81HGzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszzUcbM8GHGzPA1xszy/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPL9xszwNAAAAAHGzPGRxszz2cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3Gz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')
    start_time = time.time()
    _control_char_table = str.maketrans({c: fr'\x{c:02x}' for c in (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 92, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159)})

    def __init__(self, *args, password=None):
        self._hostname = socket.gethostname()
        self._password = password
        self._compressor = None
        self._ua_prefixes = {'curl', 'Wget', 'wget2', 'aria2', 'Axel'}
        super().__init__(*args)

    def init_compressor(self):
        if self._compressor:
            return True
        try:
            import zstandard as zstd
            self._compressor = zstd.ZstdCompressor(write_checksum=True)
            return True
        except ModuleNotFoundError:
            return False

    def do_GET(self):
        self._split_path()
        if self._path_only == '/favicon.ico':
            self.respond_for_file('favicon.ico')
            return
        if not self._password or self._validate_password():
            self.do_get()
            return
        if self._path_only != '/':
            self.respond_redirect(f'/?returnUrl={self.path}')
            return
        last_modified = str(self.start_time)
        if self.get_if_modified_since() == last_modified:
            self.respond_not_modified(last_modified)
        else:
            self.respond_for_html(self._build_html_for_password(), last_modified)

    def do_POST(self):
        self._split_path()
        if not self._password or self._validate_password():
            self.do_post()
            return
        content_length = self.get_content_length()
        if not content_length or content_length > 100:
            self.respond_bad_request()
            return
        data = self.rfile.read(content_length).decode()
        data = parse.unquote_plus(data)
        password, _, remember_device = data.partition('&')
        if password == f'password={self._password}':
            cookie = f'password={parse.quote_plus(self._password)}; path=/'
            if remember_device == 'remember_device=on':
                cookie += '; max-age=31536000'
            cookie += '; HttpOnly'
            redirect_url = parse.quote(self._queries.get('returnUrl', self._path_only))
        else:
            cookie = None
            redirect_url = self.path
        self.respond_redirect(redirect_url, cookie)

    def do_PUT(self):
        self._split_path()
        if not self._password or self._validate_password():
            self.do_put()
            return
        self.respond_unauthorized()

    def do_get(self):
        self.respond_method_not_allowed()

    def do_post(self):
        self.respond_method_not_allowed()

    def do_put(self):
        self.respond_method_not_allowed()

    def get_content_length(self):
        content_length = self.headers['Content-Length']
        if not content_length or not content_length.isdecimal():
            return None
        return int(content_length)

    def get_accept_encoding(self):
        accept_encoding = self.headers['Accept-Encoding']
        if not accept_encoding:
            return set()
        return set(accept_encoding.split(', '))

    def get_if_modified_since(self):
        return self.headers['If-Modified-Since']

    def handle_multipart(self, save_dir, redirect_location):
        content_length = self.get_content_length()
        if not content_length:
            self.respond_bad_request()
            return
        content_type = self.headers['Content-Type']
        if not content_type:
            self.respond_bad_request()
            return
        boundary = self._parse_boundary(content_type)
        if not boundary:
            self.respond_bad_request()
            return
        try:
            os.makedirs(save_dir, exist_ok=True)
            save_dir = save_dir.rstrip('/\\')
            parser = MultipartParser(self.rfile, boundary, content_length)
            while parser.has_next():
                name = parser.next_name()
                if name != 'file':
                    self.respond_bad_request()
                    return
                filename = parser.next_filename()
                if not filename:
                    self.respond_bad_request()
                    return
                with open(f'{save_dir}/{os.path.basename(filename)}', 'wb') as f:
                    parser.write_next_to(f)
        except MultipartError:
            self.respond_bad_request()
        except PermissionError:
            self.respond_forbidden()
        except FileExistsError:
            self.respond_internal_server_error()
        else:
            self.respond_redirect(redirect_location)

    def handle_putfile(self, file_path):
        content_length = self.get_content_length()
        if not content_length:
            self.respond_bad_request()
            return
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'wb') as f:
                while content_length:
                    l = min(content_length, 65536)
                    f.write(self.rfile.read(l))
                    content_length -= l
        except PermissionError:
            self.respond_forbidden()
        except FileExistsError:
            self.respond_internal_server_error()
        else:
            self.respond(HTTPStatus.OK, content_length='0')

    def send_response(self, code, message=None):
        self.log_request(code)
        self.send_response_only(code, message)

    def send_error(self, code, message=None, explain=None):
        if message is None:
            if code in self.responses:
                message = self.responses[code][0]
            else:
                message = ''
        try:
            detail = parse.unquote(self.path)
        except AttributeError:
            detail = message
        self.log_error('%s %d %s', self.command if self.command else '???', code, detail)
        self.send_response_only(code, message)
        self.send_header('Connection', 'close')
        self.end_headers()

    def _validate_password(self):
        cookie = cookies.SimpleCookie(self.headers['Cookie'])
        password = cookie.get('password')
        return password and parse.unquote_plus(password.value) == self._password

    def _build_html_for_password(self):
        builder = HtmlBuilder()
        builder.start_head()
        builder.start_title()
        builder.append(self._hostname)
        builder.end_title()
        builder.start_style()
        builder.append('.container{height: 80%; display: flex; align-items: center; justify-content: center;}')
        builder.append('.password{margin-top: 4px; margin-bottom: 12px; line-height: 24px;}')
        builder.append('.submit{width: 100%; height: 32px; margin-top: 24px;}')
        builder.end_style()
        builder.end_head()
        builder.start_body()
        builder.append('<div class="container">')
        builder.append(f'<form action="{self.path}" method="post">')
        builder.append('<label style="display: block;" for="password">Password:</label>')
        builder.append('<input class="password" id="password" name="password" type="password" minlength="3" required autofocus>')
        builder.append('<div>')
        builder.append('<input id="remember_device" name="remember_device" type="checkbox">')
        builder.append('<label for="remember_device">&nbsp;Remember device</label>')
        builder.append('</div>')
        builder.append('<input class="submit" type="submit" value="Continue">')
        builder.append('</form>')
        builder.append('</div>')
        builder.end_body()
        return builder.build()

    def _parse_boundary(self, content_type):
        parts = content_type.split('; ')
        if len(parts) != 2:
            return None
        form_data, boundary = parts
        if form_data != 'multipart/form-data':
            return None
        parts = boundary.split('=')
        if len(parts) != 2:
            return None
        key, value = parts
        if key != 'boundary':
            return None
        return value

    def _parse_range(self, content_range, filesize):
        if len(content_range) < 8 or content_range[:6] != 'bytes=':
            return None
        parts = content_range[6:].split('-')
        if len(parts) != 2:
            return None
        start, end = parts
        if not start.isdecimal():
            return None
        if end and not end.isdecimal():
            return None
        start = int(start)
        end = int(end) if end else filesize - 1
        if start > end or end >= filesize:
            return None
        return (start, end)

    def _split_path(self):
        path, _, query = parse.unquote(self.path).partition('?')
        parts = []
        for p in path.split('/'):
            if p == '..':
                if parts:
                    parts.pop()
            elif p and p != '.':
                parts.append(p)
        collapsed_path = '/' + '/'.join(parts)
        if path != '/' and path.endswith('/'):
            collapsed_path += '/'
        queries = {}
        for item in query.split('&'):
            key, _, value = item.partition('=')
            queries[key] = value
        self._path_only, self._queries = collapsed_path, queries

    def _is_from_commandline(self):
        ua = self.headers['User-Agent']
        if not ua:
            return False
        prefix = ua.split('/', 1)[0]
        return prefix in self._ua_prefixes

    def _guess_type(self, path):
        guess, _ = mimetypes.guess_type(path)
        if not guess:
            guess = 'application/octet-stream'
        if guess.startswith('text'):
            guess = f'{guess}; charset=utf-8'
        return guess

    def respond(self, status, *, content_type=None, content_length=None, last_modified=None, transfer_encoding=None, content_encoding=None, accept_ranges=None, content_range=None, content_disposition=None, location=None, cookie=None):
        self.send_response(status)
        if content_type is not None:
            self.send_header('Content-Type', content_type)
        if content_length is not None:
            self.send_header('Content-Length', content_length)
        if last_modified is not None:
            self.send_header('Cache-Control', 'public, no-cache')
            self.send_header('Last-Modified', last_modified)
        if transfer_encoding is not None:
            self.send_header('Transfer-Encoding', transfer_encoding)
        if content_encoding is not None:
            self.send_header('Content-Encoding', content_encoding)
        if accept_ranges is not None:
            self.send_header('Accept-Ranges', accept_ranges)
        if content_range is not None:
            self.send_header('Content-Range', content_range)
        if content_disposition is not None:
            self.send_header('Content-Disposition', content_disposition)
        if location is not None:
            self.send_header('Location', location)
        if cookie is not None:
            self.send_header('Set-Cookie', cookie)
        self.end_headers()

    def respond_redirect(self, location, cookie=None):
        self.respond(HTTPStatus.SEE_OTHER, content_length='0', location=location, cookie=cookie)

    def respond_not_modified(self, last_modified, content_type='text/html; charset=utf-8', accept_ranges=None):
        self.respond(HTTPStatus.NOT_MODIFIED, content_type=content_type, last_modified=last_modified, accept_ranges=accept_ranges)

    def respond_range_not_satisfiable(self):
        self.send_error(HTTPStatus.REQUESTED_RANGE_NOT_SATISFIABLE)

    def respond_bad_request(self):
        self.send_error(HTTPStatus.BAD_REQUEST)

    def respond_unauthorized(self):
        self.send_error(HTTPStatus.UNAUTHORIZED)

    def respond_forbidden(self):
        self.send_error(HTTPStatus.FORBIDDEN)

    def respond_not_found(self):
        self.send_error(HTTPStatus.NOT_FOUND)

    def respond_method_not_allowed(self):
        self.send_error(HTTPStatus.METHOD_NOT_ALLOWED)

    def respond_internal_server_error(self):
        self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR)

    def respond_for_html(self, html, last_modified=None):
        if len(html) >= 1024 and 'zstd' in self.get_accept_encoding() and self.init_compressor():
            html = self._compressor.compress(html)
            content_length = len(html)
            content_encoding = 'zstd'
        else:
            content_length = len(html)
            content_encoding = None
        self.respond(HTTPStatus.OK, content_type='text/html; charset=utf-8', content_length=content_length, last_modified=last_modified, content_encoding=content_encoding)
        self.wfile.write(html)

    def respond_for_file(self, file):
        if file == 'favicon.ico':
            filename = 'favicon.ico'
            filesize = len(self.ico)
            content_type = 'image/x-icon'
        else:
            filename = os.path.basename(file)
            filesize = os.path.getsize(file)
            content_type = self._guess_type(file)
        request_range = self.headers['Range']
        if request_range:
            request_range = self._parse_range(request_range, filesize)
            if not request_range:
                self.respond_range_not_satisfiable()
                return
            start, end = request_range
            content_length = end - start + 1
            status = HTTPStatus.PARTIAL_CONTENT
            content_range = f'bytes {start}-{end}/{filesize}'
        else:
            start = 0
            content_length = filesize
            status = HTTPStatus.OK
            content_range = None
        if file == 'favicon.ico':
            f = io.BytesIO(self.ico)
            last_modified = str(self.start_time)
        else:
            try:
                f = open(file, 'rb')
                last_modified = str(os.fstat(f.fileno()).st_mtime)
            except PermissionError:
                self.respond_forbidden()
                return
            except FileNotFoundError:
                self.respond_not_found()
                return
        accept_ranges = 'bytes'
        with f:
            if status == HTTPStatus.OK and self.get_if_modified_since() == last_modified:
                self.respond_not_modified(last_modified, content_type=content_type, accept_ranges=accept_ranges)
                return
            if status == HTTPStatus.OK and content_length >= 1024 and 'zstd' in self.get_accept_encoding() and self.init_compressor():
                compress = True
                content_length = None
                transfer_encoding = 'chunked'
                content_encoding = 'zstd'
                accept_ranges = None
            else:
                compress = False
                transfer_encoding = None
                content_encoding = None
            if self._is_from_commandline():
                content_disposition = f'attachment; filename="{parse.quote(filename)}"'
            else:
                content_disposition = None
            self.respond(status, content_type=content_type, content_length=content_length, last_modified=last_modified, transfer_encoding=transfer_encoding, content_encoding=content_encoding, accept_ranges=accept_ranges, content_range=content_range, content_disposition=content_disposition)
            if start:
                f.seek(start)
            if compress:
                with ChunkWriter(self.wfile) as writer:
                    self._compressor.copy_stream(f, writer, filesize, read_size=65536, write_size=65544)
            else:
                while content_length:
                    l = min(content_length, 65536)
                    self.wfile.write(f.read(l))
                    content_length -= l

    def log_request(self, code, size=None):
        self.log_message('%s %d %s', self.command, code, parse.unquote(self.path))

    def log_message(self, format, *args):
        year, month, day, hh, mm, ss, x, y, z = time.localtime()
        t = f'{year:04}/{month:02}/{day:02} {hh:02}:{mm:02}:{ss:02}'
        message = format % args
        sys.stderr.write('%s - %s:%s - %s\n' % (t, self.client_address[0], self.client_address[1], message.translate(self._control_char_table)))


class BaseFileShareHandler(BaseHandler):

    def __init__(self, *args, upload=False, **kwargs):
        self._upload = upload
        if is_windows():
            self.is_hidden = self._is_hidden_windows
        else:
            self.is_hidden = self._is_hidden_unix
        super().__init__(*args, **kwargs)

    def respond_for_archive(self, dir_path):
        if not self.init_compressor():
            self.respond_not_found()
            return
        if self._is_from_commandline():
            if dir_path == '/':
                filename = 'root.tar.zst'
            else:
                filename = f'{os.path.basename(dir_path.rstrip("/"))}.tar.zst'
            content_disposition = f'attachment; filename="{parse.quote(filename)}"'
        else:
            content_disposition = None
        self.respond(HTTPStatus.OK, content_type='application/zstd', transfer_encoding='chunked', content_disposition=content_disposition)
        with self._compressor.stream_writer(ChunkWriter(self.wfile), write_size=65544) as writer:
            with tarfile.open(None, 'w|', writer, 65536) as tar:
                self.archive_folder(dir_path, '', tar)

    def archive_folder(self, dir_path, arcname, tar):
        for name in sorted(os.listdir(dir_path)):
            full_path = dir_path.rstrip('/') + '/' + name
            if not self.archive_filter(full_path):
                continue
            tarinfo = tar.gettarinfo(full_path, arcname + '/' + name)
            if not tarinfo:
                continue
            try:
                if tarinfo.isdir():
                    tar.addfile(tarinfo)
                    self.archive_folder(full_path, arcname + '/' + name, tar)
                elif tarinfo.isfile():
                    with open(full_path, 'rb') as f:
                        tar.addfile(tarinfo, f)
                else:
                    tar.addfile(tarinfo)
            except (PermissionError, FileNotFoundError):
                continue

    def archive_filter(self, path):
        raise NotImplementedError

    def build_html(self, path, dirs, files):
        if path == '/':
            title = self._hostname
        else:
            title = os.path.basename(path.rstrip('/'))
        builder = HtmlBuilder()
        builder.start_head()
        builder.start_title()
        builder.append(title)
        builder.end_title()
        builder.start_style()
        builder.append('.container{height: 100%; display: flex; flex-direction: column; padding: 0 8px; overflow-wrap: break-word;}')
        builder.append('.header{display: flex; justify-content: space-between; padding: 14px 0; font-size: xx-large;}')
        builder.append('hr{width: 100%;}')
        builder.append('.main{flex: auto; padding: 16px 0;}')
        builder.append('.content{width: 100%; height: 100%;}')
        builder.append('.list-item{display: flex; justify-content: space-between; padding: 2px 0; word-break: break-all;}')
        builder.append('@media (prefers-color-scheme: light) {')
        builder.append('.list-item:nth-child(even){background-color: #f8f8f8;}')
        builder.append('}')
        builder.append('@media (prefers-color-scheme: dark) {')
        builder.append('.list-item:nth-child(even){background-color: #151515;}')
        builder.append('}')
        builder.append('.item-left{display: flex;}')
        builder.append('.item-right{min-width: 140px; max-width: 140px; display: flex; justify-content: flex-end;}')
        builder.append('.item-icon{flex: none; margin-right: 4px;}')
        builder.append('.size{font-size: smaller; color: #666666;}')
        builder.append('iframe{border: 0;}')
        builder.append('a{color: #0b57d0; text-decoration: none;}')
        builder.append('a.hidden{color: #128bff;}')
        builder.append('a:hover{text-decoration: underline;}')
        builder.append('.btn-download{display: block; height: 20px; margin-left: 4px;}')
        builder.append('.btn-download:hover{background-color: #e6e6e6; border-radius: 50%;}')
        if self._upload:
            builder.append('.upload{cursor: pointer; background-color: #76797b; border: 1px solid #76797b; color: white; border-radius: 16px;}')
            builder.append('.upload:hover{background-color: #565e64; border-color: #565e64;}')
            builder.append('.upload:disabled{opacity: .65; pointer-events: none; user-select: none;}')
            builder.append('@media (prefers-color-scheme: light) {')
            builder.append('.dragging{border: 4px dashed #cccccc; border-radius: 4px;}')
            builder.append('}')
            builder.append('@media (prefers-color-scheme: dark) {')
            builder.append('.dragging{border: 4px dashed #333333; border-radius: 4px;}')
            builder.append('}')
        builder.end_style()
        if self._upload:
            builder.start_script()
            builder.append('''
function on_upload_click() {
    document.getElementById("file").click();
}
function on_upload() {
    document.getElementById("upload").setAttribute("disabled", "");
    document.getElementById("form").submit();
}

let drag_counter = 0;

function on_dragenter(e) {
    e.preventDefault();
    drag_counter++;
    if (drag_counter === 1) {
        let types = e.dataTransfer.types;
        if (types[types.length - 1] === "Files") {
            e.currentTarget.classList.add("dragging");
        }
    }
}
function on_dragover(e) {
    e.preventDefault();
}
function on_dragleave(e) {
    e.preventDefault();
    drag_counter--;
    if (drag_counter === 0) {
        e.currentTarget.classList.remove("dragging");
    }
}
function on_drop(e) {
    e.preventDefault();
    drag_counter = 0;
    e.currentTarget.classList.remove("dragging");
    if (e.dataTransfer.files.length > 0) {
        document.getElementById("file").files = e.dataTransfer.files;
        on_upload();
    }
}
function on_load() {
    let upload = document.getElementById("upload");
    upload.onclick = on_upload_click;
    let content = document.getElementById("content");
    content.ondragenter = on_dragenter;
    content.ondragover = on_dragover;
    content.ondragleave = on_dragleave;
    content.ondrop = on_drop;
    let file = document.getElementById("file");
    file.onchange = on_upload;
}

window.onload = on_load;
''')
            builder.end_script()
        builder.end_head()
        builder.start_body()
        builder.append('<div class="container">')
        builder.append('<div class="header">')
        builder.append('<div>')
        builder.append(f'<a href="/">{html.escape(self._hostname)}</a>')
        p = ''
        for name in path.split('/'):
            if name:
                p = f'{p}/{name}'
                builder.append(f'&nbsp;/&nbsp;<a href="{parse.quote(p)}/">{html.escape(name)}</a>')
        builder.append('</div>')
        if self._upload:
            builder.append('<button id="upload" class="upload">Upload</button>')
            builder.append(f'<form id="form" action="{parse.quote(path)}" method="post" enctype="multipart/form-data" style="display: none;">')
            builder.append('<input id="file" name="file" type="file" required multiple>')
            builder.append('</form>')
        builder.append('</div>')
        builder.append('<hr>')
        builder.append('<div class="main">')
        builder.append('<div id="content" class="content">')
        builder.append('<ul>')
        for d in dirs:
            quoted_name = parse.quote(d.name)
            builder.append('<li class="list-item">')
            builder.append(f'<a class="item-left{" hidden" if d.hidden else ""}" href="{quoted_name}/" title="{quoted_name}">')
            builder.append('<svg class="item-icon" xmlns="http://www.w3.org/2000/svg" height="20px" viewBox="0 0 24 24" width="20px" fill="#76797b"><path d="M10 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2h-8l-2-2z"/></svg>')
            builder.append(f'{html.escape(d.name)}')
            builder.append('</a>')
            builder.append('<span class="item-right">')
            builder.append(f'<a class="btn-download" href="{quoted_name}.tar.zst" title="Archive" download>')
            builder.append('<svg xmlns="http://www.w3.org/2000/svg" height="20" width="20" fill="#0b57d0"><path d="M4.208 17.5q-.687 0-1.198-.5-.51-.5-.51-1.188V5.438q0-.334.115-.573.114-.24.281-.469L4.062 3q.167-.229.417-.365.25-.135.542-.135h9.958q.292 0 .542.135.25.136.437.365l1.167 1.396q.167.229.271.469.104.239.104.573v10.374q0 .688-.5 1.188t-1.188.5Zm.375-12.438h10.855l-.709-.812H5.292ZM4.25 15.75h11.5V6.812H4.25v8.938ZM10 14.396q.167 0 .333-.073.167-.073.292-.198l2.104-2.104q.25-.25.25-.604 0-.355-.25-.605t-.604-.25q-.354 0-.604.25l-.646.646v-2.5q0-.354-.26-.614-.261-.261-.615-.261t-.615.261q-.26.26-.26.614v2.5l-.646-.646q-.25-.25-.604-.25t-.604.25q-.25.25-.25.605 0 .354.25.604l2.104 2.104q.125.125.292.198.166.073.333.073ZM4.25 15.75V6.812v8.938Z"/></svg>')
            builder.append('</a>')
            builder.append('</span>')
            builder.append('</li>')
        for f in files:
            quoted_name = parse.quote(f.name)
            builder.append('<li class="list-item">')
            builder.append(f'<a class="item-left{" hidden" if f.hidden else ""}" href="{quoted_name}" title="{quoted_name}">')
            builder.append('<svg class="item-icon" xmlns="http://www.w3.org/2000/svg" height="20" viewBox="0 -960 960 960" width="20" fill="#76797b"><path d="M320-240h320v-80H320v80Zm0-160h320v-80H320v80ZM240-80q-33 0-56.5-23.5T160-160v-640q0-33 23.5-56.5T240-880h320l240 240v480q0 33-23.5 56.5T720-80H240Zm280-520v-200H240v640h480v-440H520ZM240-800v200-200 640-640Z"/></svg>')
            builder.append(f'{html.escape(f.name)}')
            builder.append('</a>')
            builder.append('<span class="item-right">')
            builder.append(f'<span class="size">{self._format_size(f.size)}</span>')
            builder.append(f'<a class="btn-download" href="{quoted_name}" title="Download" download>')
            builder.append('<svg xmlns="http://www.w3.org/2000/svg" enable-background="new 0 0 24 24" height="20px" viewBox="0 0 24 24" width="20px" fill="#0b57d0"><g><path d="M18,15v3H6v-3H4v3c0,1.1,0.9,2,2,2h12c1.1,0,2-0.9,2-2v-3H18z M17,11l-1.41-1.41L13,12.17V4h-2v8.17L8.41,9.59L7,11l5,5 L17,11z"/></g></svg>')
            builder.append('</a>')
            builder.append('</span>')
            builder.append('</li>')
        builder.append('</ul>')
        builder.append('</div>')
        builder.append('</div>')
        builder.append('</div>')
        builder.end_body()
        return builder.build()

    def _is_hidden_windows(self, file_path):
        try:
            return self._is_hidden_unix(file_path) or os.stat(file_path).st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN != 0
        except FileNotFoundError:
            return False

    def _is_hidden_unix(self, file_path):
        return os.path.basename(file_path).startswith('.')

    def _format_size(self, size):
        if size < 0:
            return 'unknown'
        lst = ((1024, 'KiB'), (1048576, 'MiB'), (1073741824, 'GiB'), (1099511627776, 'TiB'))
        idx = 0
        if size < 1048576:
            idx = 0
        elif size < 1073741824:
            idx = 1
        elif size < 1099511627776:
            idx = 2
        else:
            idx = 3
        return f'{size/lst[idx][0]:.2f} {lst[idx][1]}'


class VirtualTarShareHandler(BaseFileShareHandler):

    def __init__(self, dir_path, all_files, *args, **kwargs):
        self._dir = dir_path.rstrip('/\\') + '/'
        if dir_path == '/':
            self._filename = 'root.tar.zst'
        else:
            self._filename = f'{os.path.basename(self._dir.rstrip("/"))}.tar.zst'
        self._all = all_files
        super().__init__(*args, **kwargs)

    def do_get(self):
        if self._path_only == '/':
            last_modified = str(self.start_time)
            if self.get_if_modified_since() == last_modified:
                self.respond_not_modified(last_modified)
            else:
                dirs, files = [], [FileItem(self._filename, False, -1)]
                self.respond_for_html(self.build_html(self._path_only, dirs, files), last_modified)
            return
        name = self._path_only[1:]
        if name == self._filename or name == 'file':
            self.respond_for_archive(self._dir)
            return
        self.respond_not_found()

    def archive_filter(self, path):
        return self._all or not self.is_hidden(path)


class FileShareHandler(BaseFileShareHandler):

    def __init__(self, files, *args, **kwargs):
        self._files = files
        super().__init__(*args, **kwargs)

    def do_get(self):
        if self._path_only == '/':
            dirs, files = self.list_files()
            self.respond_for_html(self.build_html(self._path_only, dirs, files))
            return
        name = self._path_only[1:]
        file_path = self.get_file(name)
        if file_path:
            self.respond_for_file(file_path)
            return
        self.respond_not_found()

    def list_files(self):
        dirs, files = [], []
        for f in self._files:
            try:
                files.append(FileItem(os.path.basename(f), self.is_hidden(f), os.path.getsize(f)))
            except Exception:
                pass
        return (dirs, files)

    def get_file(self, name):
        f = self._find_file(name)
        if f:
            return f
        if len(self._files) == 1 and name == 'file':
            return self._files[0]
        return None

    def _find_file(self, name):
        for f in self._files:
            if os.path.basename(f) == name:
                return f
        return None


class DirectoryShareHandler(BaseFileShareHandler):

    def __init__(self, dir_path, all_files, *args, **kwargs):
        self._dir = dir_path.rstrip('/\\') + '/'
        self._all = all_files
        if is_windows():
            self._contains_hidden_segment = self._contains_hidden_segment_windows
        else:
            self._contains_hidden_segment = self._contains_hidden_segment_unix
        super().__init__(*args, **kwargs)

    def do_get(self):
        if not self.is_url_valid(self._path_only):
            self.respond_not_found()
            return
        full_path = self._dir.rstrip('/') + self._path_only
        if os.path.isdir(full_path):
            if not self._path_only.endswith('/'):
                self.respond_redirect(self._path_only + '/')
                return
            try:
                last_modified = str(max(os.stat(full_path).st_mtime, self.start_time))
            except PermissionError:
                self.respond_forbidden()
                return
            except FileNotFoundError:
                self.respond_not_found()
                return
            if self.get_if_modified_since() == last_modified:
                self.respond_not_modified(last_modified)
            else:
                try:
                    dirs, files = self.list_dir(full_path)
                except PermissionError:
                    self.respond_forbidden()
                    return
                except FileNotFoundError:
                    self.respond_not_found()
                    return
                self.respond_for_html(self.build_html(self._path_only, dirs, files), last_modified)
            return
        if os.path.isfile(full_path):
            self.respond_for_file(full_path)
            return
        if full_path.endswith('.tar.zst'):
            full_path = full_path[:-8]
            if os.path.isdir(full_path):
                self.respond_for_archive(full_path)
                return
        self.respond_not_found()

    def is_url_valid(self, path):
        return self._all or not self._contains_hidden_segment(path)

    def list_dir(self, dir_path):
        if not dir_path.endswith('/'):
            dir_path = dir_path + '/'
        dirs, files = [], []
        for name in os.listdir(dir_path):
            full_path = dir_path + name
            hidden = self.is_hidden(full_path)
            if self._all or not hidden:
                if os.path.isdir(full_path):
                    dirs.append(FileItem(name, hidden, None))
                else:
                    size = 0
                    try:
                        size = os.path.getsize(full_path)
                    except Exception:
                        pass
                    files.append(FileItem(name, hidden, size))
        return (sorted(dirs), sorted(files))

    def do_post(self):
        if self._upload:
            self.handle_multipart(self._dir.rstrip('/') + self._path_only, parse.quote(self._path_only))
        else:
            super().do_post()

    def do_put(self):
        if self._upload:
            self.handle_putfile(self._dir.rstrip('/') + self._path_only)
        else:
            super().do_put()

    def archive_filter(self, path):
        return self._all or not self.is_hidden(path)

    def _contains_hidden_segment_windows(self, path):
        if path == '/':
            return False
        prefix = self._dir
        for segment in path.strip('/').split('/'):
            if self.is_hidden(prefix + segment):
                return True
            prefix = prefix + segment + '/'
        return False

    def _contains_hidden_segment_unix(self, path):
        return path.find('/.') != -1


class FileReceiveHandler(BaseHandler):

    def __init__(self, dir_path, *args, **kwargs):
        self._dir = dir_path
        super().__init__(*args, **kwargs)

    def do_get(self):
        last_modified = str(self.start_time)
        if self.get_if_modified_since() == last_modified:
            self.respond_not_modified(last_modified)
        else:
            self.respond_for_html(self.build_html(), last_modified)

    def build_html(self):
        builder = HtmlBuilder()
        builder.start_head()
        builder.start_title()
        builder.append(self._hostname)
        builder.end_title()
        builder.start_style()
        builder.append('.container{height: 80%; padding: 0 8px; display: flex; align-items: center; justify-content: center;}')
        builder.append('@media (prefers-color-scheme: light) {')
        builder.append('.upload{width: 100%; height: 60%; border: 1px solid #cccccc; border-radius: 16px; cursor: pointer; background-color: white; color: #333333; font-size: xx-large;}')
        builder.append('.upload:hover{background-color: #e6e6e6;}')
        builder.append('.dragging{border: 4px dashed #cccccc;}')
        builder.append('}')
        builder.append('@media (prefers-color-scheme: dark) {')
        builder.append('.upload{width: 100%; height: 60%; border: 1px solid #333333; border-radius: 16px; cursor: pointer; background-color: black; color: #cccccc; font-size: xx-large;}')
        builder.append('.upload:hover{background-color: #1a1a1a;}')
        builder.append('.dragging{border: 4px dashed #333333;}')
        builder.append('}')
        builder.append('.upload:disabled{opacity: .65; pointer-events: none; user-select: none;}')
        builder.end_style()
        builder.start_script()
        builder.append('''
function on_upload_click() {
    document.getElementById("file").click();
}
function on_upload() {
    document.getElementById("upload").setAttribute("disabled", "");
    document.getElementById("form").submit();
}

let drag_counter = 0;

function on_dragenter(e) {
    e.preventDefault();
    drag_counter++;
    if (drag_counter === 1) {
        let types = e.dataTransfer.types;
        if (types[types.length - 1] === "Files") {
            e.currentTarget.classList.add("dragging");
        }
    }
}
function on_dragover(e) {
    e.preventDefault();
}
function on_dragleave(e) {
    e.preventDefault();
    drag_counter--;
    if (drag_counter === 0) {
        e.currentTarget.classList.remove("dragging");
    }
}
function on_drop(e) {
    e.preventDefault();
    drag_counter = 0;
    e.currentTarget.classList.remove("dragging");
    if (e.dataTransfer.files.length > 0) {
        document.getElementById("file").files = e.dataTransfer.files;
        on_upload();
    }
}
function on_load() {
    let upload = document.getElementById("upload");
    upload.onclick = on_upload_click;
    upload.ondragenter = on_dragenter;
    upload.ondragover = on_dragover;
    upload.ondragleave = on_dragleave;
    upload.ondrop = on_drop;
    let file = document.getElementById("file");
    file.onchange = on_upload;
}

window.onload = on_load;
''')
        builder.end_script()
        builder.end_head()
        builder.start_body()
        builder.append('<div class="container">')
        builder.append('<button id="upload" class="upload">')
        builder.append('Upload')
        builder.append(f'<form id="form" action="{self.path}" method="post" enctype="multipart/form-data" style="display: none;">')
        builder.append('<input id="file" name="file" type="file" required multiple>')
        builder.append('</form>')
        builder.append('</button>')
        builder.append('</div>')
        builder.end_body()
        return builder.build()

    def do_post(self):
        self.handle_multipart(self._dir.rstrip('/') + self._path_only, parse.quote(self._path_only))

    def do_put(self):
        self.handle_putfile(self._dir.rstrip('/') + self._path_only)


class TextShareHandler(BaseHandler):

    def __init__(self, text, *args, **kwargs):
        self._text = text
        super().__init__(*args, **kwargs)

    def do_get(self):
        if self._path_only != '/':
            self.respond_redirect('/')
            return
        last_modified = str(self.start_time)
        if self.get_if_modified_since() == last_modified:
            self.respond_not_modified(last_modified)
        else:
            self.respond_for_html(self.build_html(), last_modified)

    def build_html(self):
        builder = HtmlBuilder()
        builder.start_head()
        builder.start_title()
        builder.append(self._hostname)
        builder.end_title()
        builder.start_style()
        builder.append('.container{height: 100%; display: flex; flex-direction: column;}')
        builder.append('.content{flex: auto; margin: 10% 8px; word-wrap: break-word; white-space: pre-wrap; overflow-y: auto;}')
        builder.end_style()
        builder.start_body()
        builder.append('<div class="container">')
        builder.append('<pre class="content">')
        builder.append(html.escape(self._text))
        builder.append('</pre>')
        builder.append('</div>')
        builder.end_body()
        return builder.build()


class TextReceiveHandler(BaseHandler):

    def do_get(self):
        if self._path_only != '/':
            self.respond_redirect('/')
            return
        last_modified = str(self.start_time)
        if self.get_if_modified_since() == last_modified:
            self.respond_not_modified(last_modified)
        else:
            self.respond_for_html(self.build_html(), last_modified)

    def build_html(self):
        builder = HtmlBuilder()
        builder.start_head()
        builder.start_title()
        builder.append(self._hostname)
        builder.end_title()
        builder.start_style()
        builder.append('.container{height: 100%; display: flex; flex-direction: column;}')
        builder.append('.content{flex: auto; margin: 10% 8px; display: flex; flex-direction: column;}')
        builder.append('.textarea{flex: auto; width: 100%;}')
        builder.append('.submit{width: 100%;}')
        builder.end_style()
        builder.start_script()
        builder.append('''
function on_keydown(e) {
    if (e.key === "Control") {
        return;
    }
    if (e.ctrlKey && e.key === "Enter") {
        form = document.getElementById("form");
        if (form.reportValidity()) {
            form.submit();
            e.preventDefault();
            e.stopPropagation();
        }
    }
}
function on_load() {
    text = document.getElementById("text");
    text.onkeydown = on_keydown;
}

window.onload = on_load;
''')
        builder.end_script()
        builder.end_head()
        builder.start_body()
        builder.append('<div class="container">')
        builder.append('<form id="form" class="content" action="/" method="post">')
        builder.append('<textarea id="text" class="textarea" name="text" placeholder="Enter text" required autofocus></textarea>')
        builder.append('<br>')
        builder.append('<input class="submit" type="submit">')
        builder.append('</form>')
        builder.append('</div>')
        builder.end_body()
        return builder.build()

    def do_post(self):
        if self._path_only != '/':
            self.respond_bad_request()
            return
        content_type = self.headers['Content-Type']
        if content_type != 'application/x-www-form-urlencoded':
            self.respond_bad_request()
            return
        content_length = self.get_content_length()
        if not content_length or content_length <= 5 or content_length > 1048576:
            self.respond_bad_request()
            return
        text = self.rfile.read(5).decode()
        if text != 'text=':
            self.respond_bad_request()
            return
        text = self.rfile.read(content_length - 5).decode()
        text = parse.unquote_plus(text)
        self.respond_redirect('/')
        print(f'From {self.client_address[0]}:{self.client_address[1]}:\n{text}')


class HtmlBuilder:

    def __init__(self):
        self._list = []

    def start_head(self):
        self._list.append('<!DOCTYPE html>')
        self._list.append('<html>')
        self._list.append('<head>')
        self._list.append('<meta name="viewport" content="width=device-width,initial-scale=1.0,minimum-scale=1.0"/>')

    def end_head(self):
        self._list.append('</head>')

    def start_title(self):
        self._list.append('<title>')

    def end_title(self):
        self._list.append('</title>')

    def start_style(self):
        self._list.append('<style type="text/css">')
        self._list.append('*{margin: 0; padding: 0; box-sizing: border-box;}')
        self._list.append('@media (min-width: 576px) {')
        self._list.append('html{padding-left: calc(100vw - 100%);}')
        self._list.append('body{width: 80vw;}')
        self._list.append('}')
        self._list.append('@media (min-width: 768px) {')
        self._list.append('body{width: 70vw;}')
        self._list.append('}')
        self._list.append('@media (min-width: 992px) {')
        self._list.append('body{width: 60vw;}')
        self._list.append('}')
        self._list.append('@media (min-width: 1200px) {')
        self._list.append('body{width: 50vw;}')
        self._list.append('}')
        self._list.append('html{color-scheme: light dark; height: 100%;}')
        self._list.append('body{height: 100%; margin: 0 auto; font-family: sans-serif;}')
        self._list.append('input{padding: 1px 2px;}')
        self._list.append('button, input[type="submit"]{padding: 1px 6px;}')
        self._list.append('textarea{padding: 2px;}')

    def end_style(self):
        self._list.append('</style>')

    def start_script(self):
        self._list.append('<script type="text/javascript">')

    def end_script(self):
        self._list.append('</script>')

    def start_body(self):
        self._list.append('<body>')

    def end_body(self):
        self._list.append('</body>')

    def append(self, code):
        self._list.append(code)

    def build(self):
        self._list.append('</html>')
        return ''.join(self._list).encode()


class FileItem:

    def __init__(self, name, hidden, size):
        self.name = name
        self.hidden = hidden
        self.size = size

    def __lt__(self, other):
        if self.hidden != other.hidden:
            return self.hidden
        name1, name2 = self.name, other.name
        if name1[0] == '.' and name2[0] != '.':
            return True
        if name1[0] != '.' and name2[0] == '.':
            return False
        len1, len2 = len(name1), len(name2)
        i, min_len = 0, min(len1, len2)
        while i < min_len:
            ch1, ch2 = ord(name1[i]), ord(name2[i])
            if 65 <= ch1 <= 90:
                ch1 += 32
            if 65 <= ch2 <= 90:
                ch2 += 32
            if 49 <= ch1 <= 57 and 49 <= ch2 <= 57:
                num1, idx1 = self._check_number(name1, len1, i)
                num2, idx2 = self._check_number(name2, len2, i)
                if num1 != num2:
                    return num1 < num2
                i = idx1
            elif ch1 == ch2:
                i += 1
            else:
                return ch1 < ch2
        return len1 < len2

    def _check_number(self, s, n, start):
        num, end = 0, start
        while end < n:
            ch = ord(s[end])
            if ch < 48 or ch > 57:
                break
            num = num * 10 + ch - 48
            end += 1
        return (num, end)


class MultipartParser:

    def __init__(self, stream, boundary, content_length):
        self._stream = stream
        self._total_length = content_length
        self._read_length = 0
        self._separator = f'--{boundary}\r\n'.encode()
        self._terminator = f'--{boundary}--\r\n'.encode()
        self._state = MultipartState.INIT
        self._content_dispositon_pattern = re.compile(r'^form-data; name="(.+)"; filename="(.+)"\r\n$')
        self._name = None
        self._filename = None

    def has_next(self):
        if self._state == MultipartState.INIT:
            if self._next_line() != self._separator:
                raise MultipartError
            self._state = MultipartState.HEADER_START
        if self._state == MultipartState.HEADER_START:
            self._parse_headers()
            self._state = MultipartState.PART_START
            return True
        if self._state == MultipartState.END and self._read_length == self._total_length:
            return False
        raise MultipartError

    def next_name(self):
        if self._state != MultipartState.PART_START:
            raise MultipartError
        return self._name

    def next_filename(self):
        if self._state != MultipartState.PART_START:
            raise MultipartError
        return self._filename

    def write_next_to(self, out):
        if self._state != MultipartState.PART_START:
            raise MultipartError
        line, next = None, None
        while True:
            if not line:
                line = self._next_line()
            if len(line) >= 2 and line[-2:] == b'\r\n':
                next = self._next_line()
                if next == self._separator:
                    if len(line) > 2:
                        out.write(line[:-2])
                    self._state = MultipartState.HEADER_START
                    return
                if next == self._terminator:
                    if len(line) > 2:
                        out.write(line[:-2])
                    self._state = MultipartState.END
                    return
                out.write(line)
                line = next
            else:
                out.write(line)
                line = None

    def _parse_headers(self):
        self._name = None
        self._filename = None
        while True:
            line = self._next_line().decode()
            if line == '\r\n':
                break
            parts = line.split(': ')
            if len(parts) != 2:
                raise MultipartError
            key, value = parts
            if key == 'Content-Disposition':
                match = self._content_dispositon_pattern.match(value)
                if not match:
                    raise MultipartError
                self._name = match.group(1)
                self._filename = match.group(2)
        if not self._name or not self._filename:
            raise MultipartError

    def _next_line(self):
        if self._read_length >= self._total_length:
            raise MultipartError
        l = min(65536, self._total_length - self._read_length)
        line = self._stream.readline(l)
        if not line:
            raise MultipartError
        self._read_length += len(line)
        return line


class MultipartState:

    INIT = 0
    HEADER_START = 1
    PART_START = 2
    END = 3


class MultipartError(ValueError):
    pass


class ChunkWriter:

    def __init__(self, stream):
        self._stream = stream
        self._closed = False

    def write(self, data):
        if not data:
            return 0
        self._stream.write(f'{hex(len(data))[2:]}\r\n'.encode())
        n = self._stream.write(data)
        self._stream.write(b'\r\n')
        return n

    def flush(self):
        self._stream.flush()

    def close(self):
        if self._closed:
            return
        self._closed = True
        self._stream.write(b'0\r\n\r\n')

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


def get_best_family(host, port):
    info = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM, flags=socket.AI_PASSIVE)
    family, type, proto, canonname, addr = info[0]
    return family, addr


def get_ip(family):
    address = ('10.254.254.254', 0) if family == socket.AF_INET else ('ff05::', 0, 0, 0)
    default_ip = '127.0.0.1' if family == socket.AF_INET else '::1'
    try:
        with socket.socket(family, socket.SOCK_DGRAM) as s:
            s.connect(address)
            return s.getsockname()[0]
    except OSError:
        return default_ip


def is_windows():
    return os.name == 'nt'


def on_interrupt(a, b):
    if not is_windows():
        sys.stderr.write('\n')
    sys.exit(1)


def print_prompt():
    if is_windows():
        sys.stderr.write('Enter your text, then press Ctrl + Z followed by the Enter key:\n')
    else:
        sys.stderr.write('Enter your text, then press Ctrl + D:\n')


def create_ssl_context(certfile, keyfile=None, password=None):
    ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ctx.minimum_version = ssl.TLSVersion.TLSv1_3
    ctx.load_cert_chain(certfile=certfile, keyfile=keyfile, password=password)
    return ctx


def print_qrcode(text):
    if sys.stderr.isatty():
        try:
            import qrcode
            qr = qrcode.QRCode()
            qr.add_data(text)
            if is_windows():
                qr.print_ascii(sys.stderr, False, True)
            else:
                qr.print_tty(sys.stderr)
        except ModuleNotFoundError:
            pass


def start_server(address, port, certfile, keyfile, keypass, handler_class, show_qrcode):
    family, addr = get_best_family(address, port)
    ShareServer.address_family = family
    with ShareServer(addr, handler_class) as server:
        if certfile:
            ctx = create_ssl_context(certfile, keyfile, keypass)
            server.socket = ctx.wrap_socket(server.socket, server_side=True)
            https = True
        else:
            https = False
        host, port = server.socket.getsockname()[:2]
        ip = addr[0]
        if ip == '0.0.0.0' or ip == '::':
            ip = get_ip(family)
        if family == socket.AF_INET6:
            ip = f'[{ip}]'
        url = f'{"https" if https else "http"}://{ip}:{port}/'
        sys.stderr.write(f'Serving {"HTTPS" if https else "HTTP"} on {host} port {port} ({url}) ...\n')
        if show_qrcode:
            print_qrcode(url)
        server.serve_forever()


def main():
    sys.tracebacklimit = 0
    signal.signal(signal.SIGINT, on_interrupt)
    parser = argparse.ArgumentParser(allow_abbrev=False, add_help=False)
    parser.add_argument('arguments', nargs='*', help='a directory, files or texts')

    general = parser.add_argument_group('general options')
    general.add_argument('-b', '--bind', dest='address', help='bind address [default: all interfaces]')
    general.add_argument('-p', '--port', type=int, default=8888, help='port [default: 8888]')
    general.add_argument('-s', '--share', action='store_true', help='share mode (default mode)')
    general.add_argument('-r', '--receive', action='store_true', help='receive mode, can be used with -s option (only for directory)')
    general.add_argument('-a', '--all', action='store_true', help='show all files, including hidden ones, only for directory')
    general.add_argument('-z', '--archive', action='store_true', help='share the directory itself as an archive, only for directory')
    general.add_argument('-t', '--text', action='store_true', help='for text')
    general.add_argument('-P', '--password', nargs='?', const=os.getenv('SHARE_PASSWORD'), help='access password, if no PASSWORD is specified, the environment variable SHARE_PASSWORD will be used')
    general.add_argument('-q', '--qrcode', action='store_true', help='show the qrcode')
    general.add_argument('-h', '--help', action='help', help='show this help message and exit')

    tls = parser.add_argument_group('tls options')
    tls.add_argument('--certfile', help='cert file')
    tls.add_argument('--keyfile', help='key file')
    tls.add_argument('--keypass', help='key password')

    args = parser.parse_args()
    if args.password and len(args.password) < 3:
        raise ValueError('password is too short')
    if not args.receive:
        args.share = True
    if args.share and args.receive:
        dir_path = None
        if not args.arguments:
            dir_path = os.getcwd()
        elif os.path.isdir(args.arguments[0]):
            dir_path = args.arguments[0]
        else:
            raise FileNotFoundError(f'{args.arguments[0]} is not a directory')
        handler_class = functools.partial(DirectoryShareHandler, dir_path, args.all, upload=True, password=args.password)
    elif args.share:
        if args.text:
            if args.arguments:
                text = '\n'.join(args.arguments)
            else:
                print_prompt()
                text = ''.join(sys.stdin.readlines())
                if not text:
                    sys.exit(1)
            handler_class = functools.partial(TextShareHandler, text, password=args.password)
        else:
            dir_path, files = None, None
            if not args.arguments:
                dir_path = os.getcwd()
            elif os.path.isdir(args.arguments[0]):
                dir_path = args.arguments[0]
            else:
                for f in args.arguments:
                    if not os.path.isfile(f):
                        raise FileNotFoundError(f'{f} is not a file')
                files = [os.path.realpath(f) for f in args.arguments]
            if dir_path:
                if args.archive:
                    handler_class = functools.partial(VirtualTarShareHandler, dir_path, args.all, password=args.password)
                else:
                    handler_class = functools.partial(DirectoryShareHandler, dir_path, args.all, password=args.password)
            else:
                handler_class = functools.partial(FileShareHandler, files, password=args.password)
    else:
        if args.text:
            handler_class = functools.partial(TextReceiveHandler, password=args.password)
        else:
            dir_path = None
            if not args.arguments:
                dir_path = os.getcwd()
            elif os.path.isdir(args.arguments[0]):
                dir_path = args.arguments[0]
            else:
                raise FileNotFoundError(f'{args.arguments[0]} is not a directory')
            handler_class = functools.partial(FileReceiveHandler, dir_path, password=args.password)
    start_server(args.address, args.port, args.certfile, args.keyfile, args.keypass, handler_class, args.qrcode)


main()
