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
import shutil
import base64
import time
import stat
import re
import socket
import ssl
import zipfile


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
        sys.stderr.write(f'\033[33m{msg}\033[0m\n')


class BaseHandler(BaseHTTPRequestHandler):

    protocol_version = 'HTTP/1.1'
    ico = base64.b64decode('AAABAAMAMDAAAAEAIACoJQAANgAAACAgAAABACAAqBAAAN4lAAAQEAAAAQAgAGgEAACGNgAAKAAAADAAAABgAAAAAQAgAAAAAAAAJAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHGzPAFxszwhcbM8U3GzPGZxszxncbM8Z3GzPGdxszxncbM8Z3GzPGdxszxncbM8Z3GzPGdxszxncbM8Z3GzPGdxszxncbM8Z3GzPGdxszxncbM8Z3GzPGdxszxncbM8Z3GzPGdxszxncbM8Z3GzPGdxszxncbM8Z3GzPGdxszxncbM8Z3GzPGdxszxncbM8Z3GzPGdxszxncbM8ZnGzPFNxszwhcbM8AQAAAAAAAAAAAAAAAAAAAAAAAAAAcbM8B3GzPGxxszzccbM8/HGzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPPxxszzccbM8bHGzPAcAAAAAAAAAAAAAAAAAAAAAcbM8bHGzPPZxszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM89nGzPGwAAAAAAAAAAAAAAABxszwhcbM823GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPNtxszwhAAAAAAAAAABxszxTcbM8+3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPPtxszxTAAAAAAAAAABxszxmcbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxmAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8+3GzPOFxszzHcbM8x3GzPOFxszz8cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszzccbM8bHGzPCJxszwMcbM8DXGzPCJxszxscbM83XGzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPNNxszw3AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAcbM8OHGzPNRxszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM88XGzPE0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHGzPE5xszzycbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8s3GzPAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHGzPAlxszy0cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8fQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABxszx+cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8bgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABxszxvcbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz+cbM8cwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABxszyFcbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPOFxszx4cbM8FQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHGzPBBxszzCcbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz0cbM8onGzPC9xszwBAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHGzPGZxszz5cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP5xszzccbM8mXGzPHFxszxxcbM8mHGzPNxxszz+cbM8/XGzPMdxszxScbM8CAAAAAAAAAAAcbM8AXGzPDJxszxDcbM8BAAAAAAAAAAAAAAAAAAAAABxszwDcbM8V3GzPOZxszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8+3GzPKBxszwkcbM8AQAAAAAAAAAAcbM8AXGzPCVxszyTcbM8fHGzPBcAAAAAAAAAAAAAAABxszwXcbM8enGzPORxszzvcbM8lXGzPEJxszwkcbM8JHGzPENxszyVcbM873GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8oHGzPA4AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABxszwEcbM8AgAAAAAAAAAAcbM8B3GzPFFxszzGcbM8/XGzPP9xszz/cbM8/3GzPPVxszzlcbM85XGzPPVxszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszzdcbM8JwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHGzPAFxszwucbM8oXGzPPRxszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszyacbM8AQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHGzPFRxszzicbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxzAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHGzPHRxszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxzAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHGzPHRxszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszyacbM8AQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHGzPFNxszzicbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszzdcbM8JwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHGzPAFxszwucbM8oHGzPPNxszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8n3GzPA4AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABxszwEcbM8AgAAAAAAAAAAcbM8B3GzPFFxszzGcbM8/XGzPP9xszz/cbM8/3GzPPVxszzlcbM85XGzPPVxszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8+3GzPKBxszwkcbM8AQAAAAAAAAAAcbM8AXGzPCVxszyTcbM8fHGzPBcAAAAAAAAAAAAAAABxszwWcbM8enGzPORxszzvcbM8lXGzPEJxszwkcbM8JHGzPENxszyVcbM873GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP5xszzccbM8mXGzPHFxszxxcbM8mHGzPNxxszz+cbM8/XGzPMdxszxScbM8CAAAAAAAAAAAcbM8AXGzPDJxszxCcbM8BAAAAAAAAAAAAAAAAAAAAABxszwDcbM8VnGzPOZxszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz0cbM8onGzPC9xszwBAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHGzPGZxszz5cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPOJxszx4cbM8FQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHGzPBBxszzCcbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz+cbM8cwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABxszyFcbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8bgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABxszxvcbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8fQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABxszx+cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8s3GzPAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHGzPAlxszy0cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM88XGzPE0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHGzPE5xszzycbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPNNxszw3AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAcbM8OHGzPNRxszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszzccbM8bHGzPCJxszwMcbM8DXGzPCJxszxscbM83XGzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8+3GzPOFxszzHcbM8x3GzPOFxszz8cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxmcbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxmAAAAAAAAAABxszxTcbM8+3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPPtxszxTAAAAAAAAAABxszwhcbM823GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPNtxszwhAAAAAAAAAAAAAAAAcbM8bHGzPPZxszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM89nGzPGwAAAAAAAAAAAAAAAAAAAAAcbM8B3GzPGxxszzccbM8/HGzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPPxxszzccbM8bHGzPAcAAAAAAAAAAAAAAAAAAAAAAAAAAHGzPAFxszwhcbM8U3GzPGZxszxncbM8Z3GzPGdxszxncbM8Z3GzPGdxszxncbM8Z3GzPGdxszxncbM8Z3GzPGdxszxncbM8Z3GzPGdxszxncbM8Z3GzPGdxszxncbM8Z3GzPGdxszxncbM8Z3GzPGdxszxncbM8Z3GzPGdxszxncbM8Z3GzPGdxszxncbM8Z3GzPGdxszxncbM8ZnGzPFNxszwhcbM8AQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP///////wAA////////AADwAAAAAA8AAOAAAAAABwAAwAAAAAADAADAAAAAAAMAAMAAAAAAAwAAwAAAAAADAADAAAAAAAMAAMAAAAfgAwAAwAAAD/ADAADAAAAf+AMAAMAAAB/4AwAAwAAAP/wDAADAAAA//AMAAMAAAD/4AwAAwAAAf/gDAADAAAD/+AMAAMABg//wAwAAwAfv48ADAADAD/+AAAMAAMAf/gAAAwAAwB/8AAADAADAP/wAAAMAAMA//AAAAwAAwB/8AAADAADAH/4AAAMAAMAP/4AAAwAAwAfv48ADAADAAYP/8AMAAMAAAP/4AwAAwAAAf/gDAADAAAA/+AMAAMAAAD/8AwAAwAAAP/wDAADAAAAf+AMAAMAAAB/4AwAAwAAAD/ADAADAAAAH4AMAAMAAAAAAAwAAwAAAAAADAADAAAAAAAMAAMAAAAAAAwAAwAAAAAADAADgAAAAAAcAAPAAAAAADwAA////////AAD///////8AACgAAAAgAAAAQAAAAAEAIAAAAAAAABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHGzPAFxszwOcbM8GXGzPBlxszwZcbM8GXGzPBlxszwZcbM8GXGzPBlxszwZcbM8GXGzPBlxszwZcbM8GXGzPBlxszwZcbM8GXGzPBlxszwZcbM8GXGzPBlxszwZcbM8GXGzPBlxszwZcbM8DnGzPAEAAAAAAAAAAAAAAABxszwHcbM8ZHGzPMFxszzUcbM81HGzPNRxszzUcbM81HGzPNRxszzUcbM81HGzPNRxszzUcbM81HGzPNRxszzUcbM81HGzPNRxszzUcbM81HGzPNRxszzUcbM81HGzPNRxszzUcbM81HGzPNRxszzBcbM8ZHGzPAcAAAAAAAAAAHGzPGRxszz2cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz2cbM8ZAAAAABxszwNcbM8v3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszy/cbM8DXGzPBhxszzUcbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPNRxszwYcbM8GXGzPNRxszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPPlxszzdcbM80HGzPOdxszz+cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM81HGzPBlxszwZcbM81HGzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszzjcbM8Z3GzPBxxszwRcbM8K3GzPJRxszz4cbM8/3GzPP9xszz/cbM8/3GzPP9xszzUcbM8GXGzPBlxszzUcbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM883GzPFcAAAAAAAAAAAAAAAAAAAAAcbM8CXGzPJhxszz/cbM8/3GzPP9xszz/cbM8/3GzPNRxszwZcbM8GXGzPNRxszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3Gz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PP9xszz/cbM8/3GzPP9xszz/cbM8nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHGzPBpxszzbcbM8/3GzPP9xszz/cbM8/3GzPNRxszwZcbM8GXGzPNRxszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszy8cbM8CwAAAAAAAAAAAAAAAAAAAAAAAAAAcbM8NHGzPO1xszz/cbM8/3GzPP9xszz/cbM81HGzPBlxszwZcbM81HGzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPPNxszxXAAAAAAAAAAAAAAAAAAAAAHGzPAlxszyYcbM8/3GzPP9xszz/cbM8/3GzPP9xszzUcbM8GXGzPBlxszzUcbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPONxszxncbM8HHGzPBFxszwrcbM8lHGzPPhxszz/cbM8/3GzPP9xszz/cbM8/3GzPNRxszwZcbM8GXGzPNRxszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPPlxszzdcbM80HGzPOdxszz+cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM81HGzPBlxszwYcbM81HGzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszzUcbM8GHGzPA1xszy/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPL9xszwNAAAAAHGzPGRxszz2cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3Gz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')

    def __init__(self, *args, password=None):
        self._hostname = socket.gethostname()
        self._password = password
        super().__init__(*args)

    def do_GET(self):
        if self.path == '/favicon.ico':
            self.send_response(HTTPStatus.OK)
            self.send_content_length(len(BaseHandler.ico))
            self.send_content_type('image/x-icon')
            self.end_headers()
            self.wfile.write(self.ico)
            return
        if not self._password or self._validate_password():
            self.do_get()
            return
        self.respond_ok(self._build_html_for_password())

    def do_POST(self):
        if not self._password or self._validate_password():
            self.do_post()
            return
        content_length = self.get_content_length()
        if not content_length or content_length > 100:
            self.respond_bad_request()
            return
        data = self.rfile.read(content_length).decode()
        data = parse.unquote_plus(data)
        if data != f'password={self._password}':
            self.respond_redirect(self.path)
            return
        self.respond_redirect_cookie(self.path, f'password={parse.quote_plus(self._password)}; path=/')

    def do_PUT(self):
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

    def handle_multipart(self, save_dir, redirect_location):
        content_length = self.get_content_length()
        if not content_length:
            self.respond_bad_request()
            return
        if not self._has_freespace(content_length):
            self.respond_internal_server_error()
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
        if not self._has_freespace(content_length):
            self.respond_internal_server_error()
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
            self.respond_ok()

    def send_response(self, code, message=None):
        self.log_request(code)
        self.send_response_only(code, message)

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
        builder.end_style()
        builder.end_head()
        builder.start_body()
        builder.append('<div class="container">')
        builder.append(f'<form action="{self.path}" method="post">')
        builder.append('<input name="password" type="password" placeholder="Enter your password" minlength="3" required autofocus>')
        builder.append('&nbsp<input type="submit">')
        builder.append('</form>')
        builder.append('</div>')
        builder.end_body()
        return builder.build()

    def _has_freespace(self, need_size):
        path = self._dir
        if is_windows():
            path, _ = os.path.splitdrive(path)
        total, used, free = shutil.disk_usage(path)
        return free - need_size >= 1073741824

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

    def _split_path(self, path):
        path, _, query = path.partition('?')
        path = parse.unquote(path)
        parts = []
        for p in path.split('/'):
            if p == '..':
                parts.pop()
            elif p and p != '.':
                parts.append(p)
        collapsed_path = '/' + '/'.join(parts)
        if path != '/' and path.endswith('/'):
            collapsed_path += '/'
        return (collapsed_path, query)

    def send_content_length(self, content_length):
        self.send_header('Content-Length', str(content_length))

    def send_content_type(self, content_type):
        self.send_header('Content-Type', content_type)

    def send_transfer_encoding(self, encoding):
        self.send_header('Transfer-Encoding', encoding)

    def send_location(self, location):
        self.send_header('Location', location)

    def send_accept_ranges(self):
        self.send_header('Accept-Ranges', 'bytes')

    def send_content_range(self, start, end, filesize):
        self.send_header('Content-Range', f'bytes {start}-{end}/{filesize}')

    def send_content_disposition(self, filename):
        filename = parse.quote(filename)
        self.send_header('Content-Disposition', f'attachment;filename="{filename}"')

    def send_cookie(self, cookie):
        self.send_header('Set-Cookie', cookie)

    def respond_ok(self, html=None):
        self.send_response(HTTPStatus.OK)
        if html:
            response = html.encode()
            self.send_content_length(len(response))
            self.send_content_type('text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(response)
        else:
            self.send_content_length(0)
            self.end_headers()

    def respond_redirect(self, location):
        self.send_response(HTTPStatus.SEE_OTHER)
        self.send_content_length(0)
        self.send_location(location)
        self.end_headers()

    def respond_redirect_cookie(self, location, cookie):
        self.send_response(HTTPStatus.SEE_OTHER)
        self.send_content_length(0)
        self.send_location(location)
        self.send_cookie(cookie)
        self.end_headers()

    def respond_range_not_satisfiable(self):
        self.close_connection = True
        self.send_response(HTTPStatus.REQUESTED_RANGE_NOT_SATISFIABLE)
        self.send_content_length(0)
        self.end_headers()

    def respond_bad_request(self):
        self.close_connection = True
        self.send_response(HTTPStatus.BAD_REQUEST)
        self.send_content_length(0)
        self.end_headers()

    def respond_unauthorized(self):
        self.close_connection = True
        self.send_response(HTTPStatus.UNAUTHORIZED)
        self.send_content_length(0)
        self.end_headers()

    def respond_forbidden(self):
        self.close_connection = True
        self.send_response(HTTPStatus.FORBIDDEN)
        self.send_content_length(0)
        self.end_headers()

    def respond_not_found(self):
        self.close_connection = True
        self.send_response(HTTPStatus.NOT_FOUND)
        self.send_content_length(0)
        self.end_headers()

    def respond_method_not_allowed(self):
        self.close_connection = True
        self.send_response(HTTPStatus.METHOD_NOT_ALLOWED)
        self.send_content_length(0)
        self.end_headers()

    def respond_internal_server_error(self):
        self.close_connection = True
        self.send_response(HTTPStatus.INTERNAL_SERVER_ERROR)
        self.send_content_length(0)
        self.end_headers()

    def log_request(self, code, size=None):
        if isinstance(code, HTTPStatus):
            code = code.value
        self.log_message('%s %s %s', self.command, str(code), parse.unquote(self.path))

    def log_message(self, format, *args):
        year, month, day, hh, mm, ss, x, y, z = time.localtime()
        t = f'{year:04}/{month:02}/{day:02} {hh:02}:{mm:02}:{ss:02}'
        sys.stderr.write('%s - %s:%s - %s\n' % (t, self.client_address[0], self.client_address[1], format % args))


class BaseFileShareHandler(BaseHandler):

    def __init__(self, *args, upload=False, **kwargs):
        self._upload = upload
        self._ua_prefixes = {'curl', 'Wget', 'wget2', 'aria2', 'Axel'}
        if is_windows():
            self.is_hidden = self._is_hidden_windows
        else:
            self.is_hidden = self._is_hidden_unix
        super().__init__(*args, **kwargs)

    def respond_for_file(self, file):
        include_content_disposition = self._is_from_commandline()
        try:
            f = open(file, 'rb')
        except PermissionError:
            self.respond_forbidden()
            return
        except FileNotFoundError:
            self.respond_not_found()
            return
        with f:
            filename = os.path.basename(file)
            filesize = os.path.getsize(file)
            content_type = self._guess_type(file)
            content_range = self.headers['Range']
            if filesize == 0 or not content_range:
                self.send_response(HTTPStatus.OK)
                self.send_content_length(filesize)
                self.send_content_type(content_type)
                self.send_accept_ranges()
                if include_content_disposition:
                    self.send_content_disposition(filename)
                self.end_headers()
                self._copy_file(f, self.wfile)
                return
            content_range = self._parse_range(content_range, filesize)
            if not content_range:
                self.respond_range_not_satisfiable()
                return
            start, end = content_range
            content_length = end - start + 1
            self.send_response(HTTPStatus.PARTIAL_CONTENT)
            self.send_content_length(content_length)
            self.send_content_type(content_type)
            self.send_accept_ranges()
            self.send_content_range(start, end, filesize)
            if include_content_disposition:
                self.send_content_disposition(filename)
            self.end_headers()
            self._copy_file_range(f, self.wfile, start, content_length)

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
        builder.append('.list-item:nth-child(even){background-color: #f8f8f8;}')
        builder.append('.item-left{display: flex;}')
        builder.append('.item-right{min-width: 140px; max-width: 140px; display: flex; justify-content: flex-end;}')
        builder.append('.item-icon{flex: none; margin-right: 4px;}')
        builder.append('.size{color: #666666;}')
        builder.append('iframe{border: 0;}')
        builder.append('a{color: #2965c7; text-decoration: none;}')
        builder.append('a.hidden{color: #42a5f5;}')
        builder.append('a:hover{color: #ff5500;}')
        builder.append('.btn-download{display: block; height: 20px; margin-left: 4px;}')
        builder.append('.btn-download:hover{background-color: #e6e6e6; border-radius: 50%;}')
        if self._upload:
            builder.append('.upload{cursor: pointer; background-color: #76797b; border: 1px solid #76797b; color: white; border-radius: 16px;}')
            builder.append('.upload:hover{background-color: #565e64; border-color: #565e64;}')
            builder.append('.upload:disabled{opacity: .65; pointer-events: none; user-select: none;}')
            builder.append('.dragging{border: 4px dashed #cccccc; border-radius: 4px;}')
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
                builder.append(f'&nbsp;/&nbsp;<a href="{html.escape(parse.quote(p))}/">{html.escape(name)}</a>')
        builder.append('</div>')
        if self._upload:
            builder.append('<button id="upload" class="upload">Upload</button>')
            builder.append(f'<form id="form" action="{html.escape(parse.quote(path))}" method="post" enctype="multipart/form-data" style="display: none;">')
            builder.append('<input id="file" name="file" type="file" required multiple>')
            builder.append('</form>')
        builder.append('</div>')
        builder.append('<hr>')
        builder.append('<div class="main">')
        builder.append('<div id="content" class="content">')
        builder.append('<ul>')
        for d, hidden, items in dirs:
            builder.append('<li class="list-item">')
            builder.append(f'<a class="item-left{" hidden" if hidden else ""}" href="{html.escape(parse.quote(d))}/">')
            builder.append('<svg class="item-icon" xmlns="http://www.w3.org/2000/svg" height="20px" viewBox="0 0 24 24" width="20px" fill="#76797b"><path d="M10 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2h-8l-2-2z"/></svg>')
            builder.append(f'{html.escape(d)}')
            builder.append('</a>')
            builder.append('<span class="item-right">')
            builder.append(f'<span class="size">{items} {"item" if items == 1 else "items"}</span>')
            builder.append(f'<a class="btn-download" href="{html.escape(parse.quote(d + ".zip"))}" download>')
            builder.append('<svg xmlns="http://www.w3.org/2000/svg" height="20" width="20" fill="#2965c7"><path d="M4.208 17.5q-.687 0-1.198-.5-.51-.5-.51-1.188V5.438q0-.334.115-.573.114-.24.281-.469L4.062 3q.167-.229.417-.365.25-.135.542-.135h9.958q.292 0 .542.135.25.136.437.365l1.167 1.396q.167.229.271.469.104.239.104.573v10.374q0 .688-.5 1.188t-1.188.5Zm.375-12.438h10.855l-.709-.812H5.292ZM4.25 15.75h11.5V6.812H4.25v8.938ZM10 14.396q.167 0 .333-.073.167-.073.292-.198l2.104-2.104q.25-.25.25-.604 0-.355-.25-.605t-.604-.25q-.354 0-.604.25l-.646.646v-2.5q0-.354-.26-.614-.261-.261-.615-.261t-.615.261q-.26.26-.26.614v2.5l-.646-.646q-.25-.25-.604-.25t-.604.25q-.25.25-.25.605 0 .354.25.604l2.104 2.104q.125.125.292.198.166.073.333.073ZM4.25 15.75V6.812v8.938Z"/></svg>')
            builder.append('</a>')
            builder.append('</span>')
            builder.append('</li>')
        for f, hidden, size in files:
            builder.append('<li class="list-item">')
            builder.append(f'<a class="btn-view item-left{" hidden" if hidden else ""}" href="{html.escape(parse.quote(f))}">')
            builder.append('<svg class="item-icon" xmlns="http://www.w3.org/2000/svg" height="20" viewBox="0 -960 960 960" width="20" fill="#76797b"><path d="M320-240h320v-80H320v80Zm0-160h320v-80H320v80ZM240-80q-33 0-56.5-23.5T160-160v-640q0-33 23.5-56.5T240-880h320l240 240v480q0 33-23.5 56.5T720-80H240Zm280-520v-200H240v640h480v-440H520ZM240-800v200-200 640-640Z"/></svg>')
            builder.append(f'{html.escape(f)}')
            builder.append('</a>')
            builder.append('<span class="item-right">')
            builder.append(f'<span class="size">{self._format_size(size)}</span>')
            builder.append(f'<a class="btn-download" href="{html.escape(parse.quote(f))}" download>')
            builder.append('<svg xmlns="http://www.w3.org/2000/svg" enable-background="new 0 0 24 24" height="20px" viewBox="0 0 24 24" width="20px" fill="#2965c7"><g><path d="M18,15v3H6v-3H4v3c0,1.1,0.9,2,2,2h12c1.1,0,2-0.9,2-2v-3H18z M17,11l-1.41-1.41L13,12.17V4h-2v8.17L8.41,9.59L7,11l5,5 L17,11z"/></g></svg>')
            builder.append('</a>')
            builder.append('</span>')
            builder.append('</li>')
        builder.append('</ul>')
        builder.append('</div>')
        builder.append('</div>')
        builder.append('</div>')
        builder.end_body()
        return builder.build()

    def cmp_file(self, e1, e2):
        s1, hidden1, _ = e1
        s2, hidden2, _ = e2
        if hidden1 != hidden2:
            return hidden2 - hidden1
        if s1[0] == '.' and s2[0] != '.':
            return -1
        if s1[0] != '.' and s2[0] == '.':
            return 1
        len1, len2 = len(s1), len(s2)
        i, min_len = 0, min(len1, len2)
        while i < min_len:
            ch1, ch2 = ord(s1[i]), ord(s2[i])
            if 65 <= ch1 <= 90:
                ch1 += 32
            if 65 <= ch2 <= 90:
                ch2 += 32
            if 49 <= ch1 <= 57 and 49 <= ch2 <= 57:
                num1, idx1 = self._check_number(s1, len1, i)
                num2, idx2 = self._check_number(s2, len2, i)
                if num1 != num2:
                    return num1 - num2
                i = idx1
            elif ch1 == ch2:
                i += 1
            else:
                return ch1 - ch2
        return len1 - len2

    def _is_from_commandline(self):
        ua = self.headers['User-Agent']
        if not ua:
            return False
        prefix = ua.split('/', 1)[0]
        return prefix in self._ua_prefixes

    def _guess_type(self, path):
        guess, _ = mimetypes.guess_type(path)
        return guess if guess else 'text/plain'

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

    def _copy_file(self, src, dest):
        while True:
            data = src.read(65536)
            if not data:
                return
            dest.write(data)

    def _copy_file_range(self, src, dest, start, length):
        src.seek(start)
        while length:
            l = min(length, 65536)
            dest.write(src.read(l))
            length -= l

    def _is_hidden_windows(self, file_path):
        try:
            return self._is_hidden_unix(file_path) or os.stat(file_path).st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN != 0
        except FileNotFoundError:
            return False

    def _is_hidden_unix(self, file_path):
        return os.path.basename(file_path).startswith('.')

    def _check_number(self, s, n, start):
        num, end = 0, start
        while end < n:
            ch = ord(s[end])
            if ch < 48 or ch > 57:
                break
            num = num * 10 + ch - 48
            end += 1
        return (num, end)

    def _format_size(self, size):
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


class FileShareHandler(BaseFileShareHandler):

    def __init__(self, files, *args, **kwargs):
        self._files = files
        super().__init__(*args, **kwargs)

    def do_get(self):
        try:
            path, _ = self._split_path(self.path)
        except IndexError:
            self.respond_bad_request()
            return
        if path == '/':
            files = []
            for f in self._files:
                size = 0
                try:
                    size = os.path.getsize(f)
                except PermissionError:
                    pass
                except FileNotFoundError:
                    continue
                files.append((os.path.basename(f), self.is_hidden(f), size))
            files.sort(key=functools.cmp_to_key(self.cmp_file))
            self.respond_ok(self.build_html(path, [], files))
            return
        path = path[1:]
        for f in self._files:
            if path == os.path.basename(f):
                self.respond_for_file(f)
                return
        if path == 'file' and len(self._files) == 1:
            self.respond_for_file(self._files[0])
        else:
            self.respond_not_found()


class DirectoryShareHandler(BaseFileShareHandler):

    def __init__(self, dir, all, *args, **kwargs):
        self._dir = dir.rstrip('/\\') + '/'
        self._all = all
        if is_windows():
            self._contains_hidden_segment = self._contains_hidden_segment_windows
        else:
            self._contains_hidden_segment = self._contains_hidden_segment_unix
        super().__init__(*args, **kwargs)

    def do_get(self):
        try:
            path, _ = self._split_path(self.path)
        except IndexError:
            self.respond_bad_request()
            return
        if not self._all and self._contains_hidden_segment(path):
            self.respond_not_found()
            return
        file_path = self._dir.rstrip('/') + path
        if os.path.isdir(file_path):
            if not path.endswith('/'):
                self.respond_redirect(path + '/')
                return
            try:
                dirs, files = self.list_dir(file_path)
                dirs.sort(key=functools.cmp_to_key(self.cmp_file))
                files.sort(key=functools.cmp_to_key(self.cmp_file))
            except PermissionError:
                self.respond_forbidden()
            except FileNotFoundError:
                self.respond_not_found()
            else:
                self.respond_ok(self.build_html(path, dirs, files))
        elif os.path.isfile(file_path):
            self.respond_for_file(file_path)
        elif file_path.endswith('.zip'):
            file_path = file_path[:-4]
            if os.path.isdir(file_path):
                self.respond_for_archive(file_path)
            else:
                self.respond_not_found()
        else:
            self.respond_not_found()

    def do_post(self):
        if self._upload:
            try:
                path, _ = self._split_path(self.path)
            except IndexError:
                self.respond_bad_request()
                return
            self.handle_multipart(self._dir.rstrip('/') + path, parse.quote(path))
        else:
            super().do_post()

    def do_put(self):
        if self._upload:
            try:
                path, _ = self._split_path(self.path)
            except IndexError:
                self.respond_bad_request()
                return
            self.handle_putfile(self._dir.rstrip('/') + path)
        else:
            super().do_put()

    def respond_for_archive(self, dir):
        self.send_response(HTTPStatus.OK)
        self.send_content_type('application/zip')
        self.send_transfer_encoding('chunked')
        self.end_headers()
        with ChunkWriter(self.wfile) as writer:
            with zipfile.ZipFile(writer, 'w', zipfile.ZIP_STORED, strict_timestamps=False) as zip:
                try:
                    self._archive(os.path.dirname(dir.rstrip('/')), dir, zip)
                except (PermissionError, FileNotFoundError):
                    pass

    def list_dir(self, dir):
        if not dir.endswith('/'):
            dir = dir + '/'
        dirs, files = [], []
        for name in os.listdir(dir):
            path = dir + name
            hidden = self.is_hidden(path)
            if self._all or not hidden:
                if os.path.isdir(path):
                    items = []
                    try:
                        items = [f for f in os.listdir(path) if self._all or not self.is_hidden(f'{path}/{f}')]
                    except Exception:
                        pass
                    dirs.append((name, hidden, len(items)))
                else:
                    size = 0
                    try:
                        size = os.path.getsize(path)
                    except Exception:
                        pass
                    files.append((name, hidden, size))
        return (dirs, files)

    def _archive(self, base_dir, dir, zip):
        if not base_dir.endswith('/'):
            base_dir = base_dir + '/'
        if not dir.endswith('/'):
            dir = dir + '/'
        for name in os.listdir(dir):
            path = dir + name
            if self._all or not self.is_hidden(path):
                if os.path.isdir(path):
                    self._archive(base_dir, path, zip)
                else:
                    arcname = path[len(base_dir):]
                    try:
                        zip.write(path, arcname)
                    except (PermissionError, FileNotFoundError):
                        pass

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

    def __init__(self, dir, *args, **kwargs):
        self._dir = dir
        super().__init__(*args, **kwargs)

    def do_get(self):
        if self.path != '/':
            self.respond_redirect('/')
            return
        self.respond_ok(self.build_html())

    def build_html(self):
        builder = HtmlBuilder()
        builder.start_head()
        builder.start_title()
        builder.append(self._hostname)
        builder.end_title()
        builder.start_style()
        builder.append('.container{height: 80%; padding: 0 8px; display: flex; align-items: center; justify-content: center;}')
        builder.append('.upload{width: 100%; height: 60%; border: 1px solid #cccccc; border-radius: 16px; cursor: pointer; background-color: white; color: #333333; font-size: xx-large;}')
        builder.append('.upload:hover{background-color: #e6e6e6;}')
        builder.append('.upload:disabled{opacity: .65; pointer-events: none; user-select: none;}')
        builder.append('.dragging{border: 4px dashed #cccccc;}')
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
        builder.append('<form id="form" action="/" method="post" enctype="multipart/form-data" style="display: none;">')
        builder.append('<input id="file" name="file" type="file" required multiple>')
        builder.append('</form>')
        builder.append('</button>')
        builder.append('</div>')
        builder.end_body()
        return builder.build()

    def do_post(self):
        if self.path != '/':
            self.respond_bad_request()
            return
        self.handle_multipart(self._dir, '/')

    def do_put(self):
        try:
            path, _ = self._split_path(self.path)
        except IndexError:
            self.respond_bad_request()
            return
        self.handle_putfile(self._dir.rstrip('/') + path)


class TextShareHandler(BaseHandler):

    def __init__(self, text, *args, **kwargs):
        self._text = text
        super().__init__(*args, **kwargs)

    def do_get(self):
        if self.path != '/':
            self.respond_redirect('/')
            return
        self.respond_ok(self.build_html())

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
        if self.path != '/':
            self.respond_redirect('/')
            return
        self.respond_ok(self.build_html())

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
        if self.path != '/':
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
        print(text)


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
        self._list.append('html{height: 100%;}')
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
        return ''.join(self._list)


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

    def write(self, data):
        if not data:
            return 0
        self._stream.write(f'{hex(len(data))[2:]}\r\n'.encode())
        n = self._stream.write(data)
        self._stream.write(b'\r\n')
        return n

    def flush(self):
        self._stream.flush()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self._stream.write(b'0\r\n\r\n')


def get_best_family(host, port):
    info = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM, flags=socket.AI_PASSIVE)
    family, type, proto, canonname, addr = info[0]
    return family, addr


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
    ctx.maximum_version = ssl.TLSVersion.TLSv1_3
    ctx.load_cert_chain(certfile=certfile, keyfile=keyfile, password=password)
    return ctx


def start_server(address, port, certfile, keyfile, keypass, handler_class):
    ShareServer.address_family, addr = get_best_family(address, port)
    with ShareServer(addr, handler_class) as server:
        if certfile:
            ctx = create_ssl_context(certfile, keyfile, keypass)
            server.socket = ctx.wrap_socket(server.socket, server_side=True)
        host, port = server.socket.getsockname()[:2]
        sys.stderr.write(f'Serving HTTP on {host} port {port} ...\n')
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
    general.add_argument('-t', '--text', action='store_true', help='for text')
    general.add_argument('-P', '--password', nargs='?', const=os.getenv('SHARE_PASSWORD'), help='access password, if no PASSWORD is specified, the environment variable SHARE_PASSWORD will be used')
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
        dir = None
        if not args.arguments:
            dir = os.getcwd()
        elif os.path.isdir(args.arguments[0]):
            dir = args.arguments[0]
        else:
            raise FileNotFoundError(f'{args.arguments[0]} is not a directory')
        handler_class = functools.partial(DirectoryShareHandler, dir, args.all, upload=True, password=args.password)
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
            dir, files = None, None
            if not args.arguments:
                dir = os.getcwd()
            elif os.path.isdir(args.arguments[0]):
                dir = args.arguments[0]
            else:
                for f in args.arguments:
                    if not os.path.isfile(f):
                        raise FileNotFoundError(f'{f} is not a file')
                files = [os.path.realpath(f) for f in args.arguments]
            if dir:
                handler_class = functools.partial(DirectoryShareHandler, dir, args.all, password=args.password)
            else:
                handler_class = functools.partial(FileShareHandler, files, password=args.password)
    else:
        if args.text:
            handler_class = functools.partial(TextReceiveHandler, password=args.password)
        else:
            dir = None
            if not args.arguments:
                dir = os.getcwd()
            elif os.path.isdir(args.arguments[0]):
                dir = args.arguments[0]
            else:
                raise FileNotFoundError(f'{args.arguments[0]} is not a directory')
            handler_class = functools.partial(FileReceiveHandler, dir, password=args.password)
    start_server(args.address, args.port, args.certfile, args.keyfile, args.keypass, handler_class)


main()
