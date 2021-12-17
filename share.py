#!/bin/python3
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
import io
import stat
import re
import socket


class ShareServer(ThreadingHTTPServer):

    def handle_error(self, request, client_address):
        t, value, traceback = sys.exc_info()
        if issubclass(t, ConnectionError):
            return
        super().handle_error(request, client_address)


class BaseHandler(BaseHTTPRequestHandler):

    protocol_version = 'HTTP/1.1'
    ico = base64.b64decode('AAABAAMAMDAAAAEAIACoJQAANgAAACAgAAABACAAqBAAAN4lAAAQEAAAAQAgAGgEAACGNgAAKAAAADAAAABgAAAAAQAgAAAAAAAAJAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHGzPAFxszwhcbM8U3GzPGZxszxncbM8Z3GzPGdxszxncbM8Z3GzPGdxszxncbM8Z3GzPGdxszxncbM8Z3GzPGdxszxncbM8Z3GzPGdxszxncbM8Z3GzPGdxszxncbM8Z3GzPGdxszxncbM8Z3GzPGdxszxncbM8Z3GzPGdxszxncbM8Z3GzPGdxszxncbM8Z3GzPGdxszxncbM8ZnGzPFNxszwhcbM8AQAAAAAAAAAAAAAAAAAAAAAAAAAAcbM8B3GzPGxxszzccbM8/HGzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPPxxszzccbM8bHGzPAcAAAAAAAAAAAAAAAAAAAAAcbM8bHGzPPZxszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM89nGzPGwAAAAAAAAAAAAAAABxszwhcbM823GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPNtxszwhAAAAAAAAAABxszxTcbM8+3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPPtxszxTAAAAAAAAAABxszxmcbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxmAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8+3GzPOFxszzHcbM8x3GzPOFxszz8cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszzccbM8bHGzPCJxszwMcbM8DXGzPCJxszxscbM83XGzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPNNxszw3AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAcbM8OHGzPNRxszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM88XGzPE0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHGzPE5xszzycbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8s3GzPAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHGzPAlxszy0cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8fQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABxszx+cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8bgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABxszxvcbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz+cbM8cwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABxszyFcbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPOFxszx4cbM8FQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHGzPBBxszzCcbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz0cbM8onGzPC9xszwBAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHGzPGZxszz5cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP5xszzccbM8mXGzPHFxszxxcbM8mHGzPNxxszz+cbM8/XGzPMdxszxScbM8CAAAAAAAAAAAcbM8AXGzPDJxszxDcbM8BAAAAAAAAAAAAAAAAAAAAABxszwDcbM8V3GzPOZxszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8+3GzPKBxszwkcbM8AQAAAAAAAAAAcbM8AXGzPCVxszyTcbM8fHGzPBcAAAAAAAAAAAAAAABxszwXcbM8enGzPORxszzvcbM8lXGzPEJxszwkcbM8JHGzPENxszyVcbM873GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8oHGzPA4AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABxszwEcbM8AgAAAAAAAAAAcbM8B3GzPFFxszzGcbM8/XGzPP9xszz/cbM8/3GzPPVxszzlcbM85XGzPPVxszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszzdcbM8JwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHGzPAFxszwucbM8oXGzPPRxszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszyacbM8AQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHGzPFRxszzicbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxzAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHGzPHRxszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxzAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHGzPHRxszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszyacbM8AQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHGzPFNxszzicbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszzdcbM8JwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHGzPAFxszwucbM8oHGzPPNxszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8n3GzPA4AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABxszwEcbM8AgAAAAAAAAAAcbM8B3GzPFFxszzGcbM8/XGzPP9xszz/cbM8/3GzPPVxszzlcbM85XGzPPVxszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8+3GzPKBxszwkcbM8AQAAAAAAAAAAcbM8AXGzPCVxszyTcbM8fHGzPBcAAAAAAAAAAAAAAABxszwWcbM8enGzPORxszzvcbM8lXGzPEJxszwkcbM8JHGzPENxszyVcbM873GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP5xszzccbM8mXGzPHFxszxxcbM8mHGzPNxxszz+cbM8/XGzPMdxszxScbM8CAAAAAAAAAAAcbM8AXGzPDJxszxCcbM8BAAAAAAAAAAAAAAAAAAAAABxszwDcbM8VnGzPOZxszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz0cbM8onGzPC9xszwBAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHGzPGZxszz5cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPOJxszx4cbM8FQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHGzPBBxszzCcbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz+cbM8cwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABxszyFcbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8bgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABxszxvcbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8fQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABxszx+cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8s3GzPAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHGzPAlxszy0cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM88XGzPE0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHGzPE5xszzycbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPNNxszw3AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAcbM8OHGzPNRxszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszzccbM8bHGzPCJxszwMcbM8DXGzPCJxszxscbM83XGzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8+3GzPOFxszzHcbM8x3GzPOFxszz8cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxncbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxnAAAAAAAAAABxszxmcbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszxmAAAAAAAAAABxszxTcbM8+3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPPtxszxTAAAAAAAAAABxszwhcbM823GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPNtxszwhAAAAAAAAAAAAAAAAcbM8bHGzPPZxszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM89nGzPGwAAAAAAAAAAAAAAAAAAAAAcbM8B3GzPGxxszzccbM8/HGzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPPxxszzccbM8bHGzPAcAAAAAAAAAAAAAAAAAAAAAAAAAAHGzPAFxszwhcbM8U3GzPGZxszxncbM8Z3GzPGdxszxncbM8Z3GzPGdxszxncbM8Z3GzPGdxszxncbM8Z3GzPGdxszxncbM8Z3GzPGdxszxncbM8Z3GzPGdxszxncbM8Z3GzPGdxszxncbM8Z3GzPGdxszxncbM8Z3GzPGdxszxncbM8Z3GzPGdxszxncbM8Z3GzPGdxszxncbM8ZnGzPFNxszwhcbM8AQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP///////wAA////////AADwAAAAAA8AAOAAAAAABwAAwAAAAAADAADAAAAAAAMAAMAAAAAAAwAAwAAAAAADAADAAAAAAAMAAMAAAAfgAwAAwAAAD/ADAADAAAAf+AMAAMAAAB/4AwAAwAAAP/wDAADAAAA//AMAAMAAAD/4AwAAwAAAf/gDAADAAAD/+AMAAMABg//wAwAAwAfv48ADAADAD/+AAAMAAMAf/gAAAwAAwB/8AAADAADAP/wAAAMAAMA//AAAAwAAwB/8AAADAADAH/4AAAMAAMAP/4AAAwAAwAfv48ADAADAAYP/8AMAAMAAAP/4AwAAwAAAf/gDAADAAAA/+AMAAMAAAD/8AwAAwAAAP/wDAADAAAAf+AMAAMAAAB/4AwAAwAAAD/ADAADAAAAH4AMAAMAAAAAAAwAAwAAAAAADAADAAAAAAAMAAMAAAAAAAwAAwAAAAAADAADgAAAAAAcAAPAAAAAADwAA////////AAD///////8AACgAAAAgAAAAQAAAAAEAIAAAAAAAABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHGzPAFxszwOcbM8GXGzPBlxszwZcbM8GXGzPBlxszwZcbM8GXGzPBlxszwZcbM8GXGzPBlxszwZcbM8GXGzPBlxszwZcbM8GXGzPBlxszwZcbM8GXGzPBlxszwZcbM8GXGzPBlxszwZcbM8DnGzPAEAAAAAAAAAAAAAAABxszwHcbM8ZHGzPMFxszzUcbM81HGzPNRxszzUcbM81HGzPNRxszzUcbM81HGzPNRxszzUcbM81HGzPNRxszzUcbM81HGzPNRxszzUcbM81HGzPNRxszzUcbM81HGzPNRxszzUcbM81HGzPNRxszzBcbM8ZHGzPAcAAAAAAAAAAHGzPGRxszz2cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz2cbM8ZAAAAABxszwNcbM8v3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszy/cbM8DXGzPBhxszzUcbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPNRxszwYcbM8GXGzPNRxszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPPlxszzdcbM80HGzPOdxszz+cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM81HGzPBlxszwZcbM81HGzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszzjcbM8Z3GzPBxxszwRcbM8K3GzPJRxszz4cbM8/3GzPP9xszz/cbM8/3GzPP9xszzUcbM8GXGzPBlxszzUcbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM883GzPFcAAAAAAAAAAAAAAAAAAAAAcbM8CXGzPJhxszz/cbM8/3GzPP9xszz/cbM8/3GzPNRxszwZcbM8GXGzPNRxszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3Gz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PP9xszz/cbM8/3GzPP9xszz/cbM8nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHGzPBpxszzbcbM8/3GzPP9xszz/cbM8/3GzPNRxszwZcbM8GXGzPNRxszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszy8cbM8CwAAAAAAAAAAAAAAAAAAAAAAAAAAcbM8NHGzPO1xszz/cbM8/3GzPP9xszz/cbM81HGzPBlxszwZcbM81HGzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPPNxszxXAAAAAAAAAAAAAAAAAAAAAHGzPAlxszyYcbM8/3GzPP9xszz/cbM8/3GzPP9xszzUcbM8GXGzPBlxszzUcbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPONxszxncbM8HHGzPBFxszwrcbM8lHGzPPhxszz/cbM8/3GzPP9xszz/cbM8/3GzPNRxszwZcbM8GXGzPNRxszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPPlxszzdcbM80HGzPOdxszz+cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM81HGzPBlxszwYcbM81HGzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszzUcbM8GHGzPA1xszy/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPL9xszwNAAAAAHGzPGRxszz2cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3GzPP9xszz/cbM8/3Gz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')

    def __init__(self, *args, password=None):
        self.hostname = socket.gethostname()
        self.password = password
        super().__init__(*args)

    def do_GET(self):
        if self.path == '/favicon.ico':
            self.send_response(HTTPStatus.OK)
            self.send_content_length(len(BaseHandler.ico))
            self.send_content_type('image/x-icon')
            self.end_headers()
            self.wfile.write(self.ico)
            return
        if not self.password or self._check_password():
            self.do_get()
            return
        self.respond_ok(self._build_html_for_password())

    def do_POST(self):
        if not self.password or self._check_password():
            self.do_post()
            return
        content_length = self.headers['Content-Length']
        if not content_length or not content_length.isdecimal():
            self.respond_bad_request()
            return
        content_length = int(content_length)
        if content_length > 100:
            self.respond_bad_request()
            return
        data = self.rfile.read(content_length).decode()
        data = parse.unquote_plus(data)
        if data != f'password={self.password}':
            self.respond_redirect(self.path)
            return
        self.respond_redirect_cookie(self.path, f'password={parse.quote_plus(self.password)}; path=/')

    def do_get(self):
        self.respond_method_not_allowed()

    def do_post(self):
        self.respond_method_not_allowed()

    def _check_password(self):
        cookie = cookies.SimpleCookie(self.headers['Cookie'])
        password = cookie.get('password')
        return password and parse.unquote_plus(password.value) == self.password

    def _build_html_for_password(self):
        builder = HtmlBuilder()
        builder.start_head()
        builder.start_title()
        builder.append(self.hostname)
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

    def send_content_length(self, content_length):
        self.send_header('Content-Length', str(content_length))

    def send_content_type(self, content_type):
        self.send_header('Content-Type', content_type)

    def send_location(self, location):
        self.send_header('Location', parse.quote(location))

    def send_accept_ranges(self):
        self.send_header('Accept-Ranges', 'bytes')

    def send_content_range(self, start, end, filesize):
        self.send_header('Content-Range', f'bytes {start}-{end}/{filesize}')

    def send_content_disposition(self, filename):
        filename = parse.quote(filename)
        self.send_header('Content-Disposition', f'attachment;filename="{filename}"')

    def send_cookie(self, cookie):
        self.send_header('Set-Cookie', cookie)

    def respond_ok(self, html):
        self.send_response(HTTPStatus.OK)
        response = html.encode()
        self.send_content_length(len(response))
        self.send_content_type('text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(response)

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
        sys.stderr.write('%s - %s - %s\n' % (t, self.address_string(), format % args))


class FileSendHandler(BaseHandler):

    def __init__(self, *args, dir=None, all=False, files=None, password=None):
        self.dir = None
        self.all = False
        self.files = []
        if dir:
            self.dir = dir
            self.all = all
        elif files:
            for f in files:
                if os.path.isfile(f):
                    self.files.append(os.path.realpath(f))
        self.ua_prefixes = {'curl', 'Wget', 'wget2', 'aria2', 'Axel'}
        super().__init__(*args, password=password)

    def do_get(self):
        path, _ = self.split_path(parse.unquote(self.path))
        if not self.can_respond(path):
            self.respond_not_found()
            return
        if self.is_dir(path):
            if not path.endswith('/'):
                self.respond_redirect(path + '/')
                return
            self.respond_for_dir(path)
        elif self.is_file(path):
            self.respond_for_file(path, self.is_from_commandline())
        else:
            self.respond_not_found()

    def is_from_commandline(self):
        ua = self.headers['User-Agent']
        if not ua:
            return False
        prefix = ua.split('/', 1)[0]
        return prefix in self.ua_prefixes

    def split_path(self, path):
        parts = path.split('?', 1)
        path = parts[0]
        params = {}
        if len(parts) > 1:
            query = parts[1]
            for q in query.split('&'):
                if q:
                    words = q.split('=')
                    if len(words) == 2:
                        params[words[0]] = words[1]
        return (path, params)

    def can_respond(self, path):
        return not self.dir or self.all or path.find('/.') == -1

    def is_dir(self, path):
        if self.dir:
            return os.path.isdir(self.dir + path)
        return path == '/'

    def is_file(self, path):
        if self.dir:
            return os.path.isfile(self.dir + path)
        path = path[1:]
        for f in self.files:
            if path == os.path.basename(f):
                return True
        if path == 'file' and len(self.files) == 1:
            return True

    def get_file(self, path):
        if self.dir:
            return self.dir + path
        path = path[1:]
        for f in self.files:
            if path == os.path.basename(f):
                return f
        if path == 'file' and len(self.files) == 1:
            return self.files[0]
        raise RuntimeError

    def respond_for_dir(self, path):
        try:
            dirs, files = self.list_dir(path)
        except PermissionError:
            self.respond_forbidden()
            return
        except FileNotFoundError:
            self.respond_not_found()
            return
        self.respond_ok(self.build_html(path, dirs, files))

    def respond_for_file(self, path, include_content_disposition):
        file = self.get_file(path)
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
            content_type = self.guess_type(file)
            content_range = self.headers['Range']
            if filesize == 0 or not content_range:
                self.send_response(HTTPStatus.OK)
                self.send_content_length(filesize)
                self.send_content_type(content_type)
                self.send_accept_ranges()
                if include_content_disposition:
                    self.send_content_disposition(filename)
                self.end_headers()
                self.copy_file(f, self.wfile)
                return
            content_range = self.parse_range(content_range, filesize)
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
            self.copy_file_range(f, self.wfile, start, content_length)

    def list_dir(self, path):
        dirs, files = [], []
        if self.dir:
            path = self.dir + path
            for name in os.listdir(path):
                abs_path = path + name
                if self.can_show_file(abs_path):
                    if os.path.isdir(abs_path):
                        dirs.append(name)
                    else:
                        size = self.format_size(os.path.getsize(abs_path))
                        files.append((name, size))
        else:
            for f in self.files:
                files.append((os.path.basename(f), self.format_size(os.path.getsize(f))))
        dirs.sort(key=functools.cmp_to_key(self.cmp_path))
        files.sort(key=functools.cmp_to_key(lambda s1, s2: self.cmp_path(s1[0], s2[0])))
        return (dirs, files)

    def can_show_file(self, file):
        if self.all:
            return True
        if is_windows() and os.stat(file).st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN == 0:
            return True
        return not os.path.basename(file).startswith('.')

    def build_html(self, path, dirs, files):
        path = path.rstrip('/')
        if not path:
            title = self.hostname
        else:
            title = os.path.basename(path)
        builder = HtmlBuilder()
        builder.start_head()
        builder.start_title()
        builder.append(title)
        builder.end_title()
        builder.start_style()
        builder.append('.container{height: 100%; display: flex; flex-direction: column; padding: 0 8px; overflow-wrap: break-word;}')
        builder.append('.header{margin-top: 8px; font-size: larger;}')
        builder.append('hr{margin-bottom: 0; width: 100%;}')
        builder.append('.main{flex: 1; display: flex; flex-direction: column; padding: 16px 8px;}')
        builder.append('.icon{vertical-align: middle; margin-right: 4px;}')
        builder.append('.size{color: #666666; font-size: smaller;}')
        builder.append('iframe{border: 0;}')
        builder.append('a{color: #2440b3; text-decoration: none;}')
        builder.append('a:hover{color:#ff5500;}')
        builder.append('button{cursor: pointer; border: 1px solid #cccccc; color: #333333; background-color: white; border-radius: 4px;}')
        builder.append('button:hover{background-color: #e6e6e6;}')
        builder.end_style()
        builder.start_script()
        builder.append('function view_file(){')
        builder.append('src = this.getAttribute("src");')
        builder.append('var frame = document.createElement("iframe");')
        builder.append('frame.setAttribute("src",src);')
        builder.append('frame.setAttribute("allow","fullscreen");')
        builder.append('frame.setAttribute("width","100%");')
        builder.append('frame.setAttribute("height","100%");')
        builder.append('content = document.getElementById("content");')
        builder.append('content.replaceWith(frame);')
        builder.append('document.title=src;')
        builder.append('}')
        builder.append('window.onload = function() {')
        builder.append('btns = document.getElementsByClassName("btn_view");')
        builder.append('for (var i = 0; i < btns.length; i++) {')
        builder.append('btns[i].onclick = view_file;')
        builder.append('}')
        builder.append('}')
        builder.end_script()
        builder.end_head()
        builder.start_body()
        builder.append('<div class="container">')
        builder.append('<div class="header">')
        builder.append(f'<a href="/">{html.escape(self.hostname)}</a>')
        p = ''
        for name in path.split('/'):
            if name:
                p = f'{p}/{name}'
                builder.append(f'&nbsp;/&nbsp;<a href="{html.escape(parse.quote(p))}/">{html.escape(name)}</a>')
        builder.append('</div>')
        builder.append('<hr>')
        builder.append('<div class="main">')
        builder.append('<div id="content">')
        for d in dirs:
            builder.append('<div>')
            builder.append(f'<a href="{html.escape(parse.quote(d))}/">')
            builder.append(f'<span class="icon"><svg xmlns="http://www.w3.org/2000/svg" height="16px" viewBox="0 0 24 24" width="16px" fill="#5f6368"><path d="M0 0h24v24H0z" fill="none"/><path d="M10 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2h-8l-2-2z"/></svg></span>')
            builder.append(f'{html.escape(d)}</a>')
            builder.append('</div>')
        for f, size in files:
            builder.append('<div>')
            builder.append(f'<a href="{html.escape(parse.quote(f))}" download>')
            builder.append(f'<span class="icon"><svg xmlns="http://www.w3.org/2000/svg" height="16px" viewBox="0 0 24 24" width="16px" fill="#5f6368"><path d="M0 0h24v24H0z" fill="none"/><path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/></svg></span>')
            builder.append(f'{html.escape(f)}</a>')
            builder.append(f'&nbsp;<span class="size">({size})</span>')
            builder.append(f'&nbsp;<button class="btn_view" src="{html.escape(parse.quote(f))}">View</button>')
            builder.append('</div>')
        builder.append('</div>')
        builder.append('</div>')
        builder.append('</div>')
        builder.end_body()
        return builder.build()

    def guess_type(self, path):
        guess, _ = mimetypes.guess_type(path)
        return guess if guess else 'text/plain'

    def parse_range(self, content_range, filesize):
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
        if end:
            end = int(end)
        else:
            end = filesize - 1
        if start > end or end >= filesize:
            return None
        return (start, end)

    def copy_file(self, src, dest):
        while True:
            data = src.read(65536)
            if not data:
                return
            dest.write(data)

    def copy_file_range(self, src, dest, start, length):
        src.seek(start)
        buf_size = 65536
        while length:
            if length <= buf_size:
                dest.write(src.read(length))
                return
            dest.write(src.read(buf_size))
            length -= buf_size

    def cmp_path(self, s1, s2):
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
            if ch1 == ch2:
                i += 1
            elif 48 <= ch1 <= 57 and 48 <= ch2 <= 57:
                num1, idx1 = self.check_number(s1, len1, i)
                num2, idx2 = self.check_number(s2, len2, i)
                if num1 != num2:
                    return num1 - num2
                i = idx1
            else:
                return ch1 - ch2
        return len1 - len2

    def check_number(self, s, n, start):
        num, end = 0, start
        while end < n:
            ch = ord(s[end])
            if ch < 48 or ch > 57:
                break
            num = num * 10 + ch - 48
            end += 1
        return (num, end)

    def format_size(self, size):
        lst = ((1024, 'KB'), (1048576, 'MB'), (1073741824, 'GB'), (1099511627776, 'TB'))
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


class FileReceiveHandler(BaseHandler):

    def __init__(self, dir, *args, password=None):
        self.dir = dir
        super().__init__(*args, password=password)

    def do_get(self):
        if self.path != '/':
            self.respond_redirect('/')
            return
        self.respond_ok(self.build_html())

    def build_html(self):
        builder = HtmlBuilder()
        builder.start_head()
        builder.start_title()
        builder.append(self.hostname)
        builder.end_title()
        builder.start_style()
        builder.append('.container{height: 80%; display: flex; align-items: center; justify-content: center;}')
        builder.end_style()
        builder.end_head()
        builder.start_body()
        builder.append('<div class="container">')
        builder.append('<form action="/" method="post" enctype="multipart/form-data">')
        builder.append('<input name="file" type="file" required multiple>')
        builder.append('<input type="submit">')
        builder.append('</form>')
        builder.append('</div>')
        builder.end_body()
        return builder.build()

    def do_post(self):
        if self.path != '/':
            self.respond_bad_request()
            return
        content_length = self.headers['Content-Length']
        if not content_length or not content_length.isdecimal():
            self.respond_bad_request()
            return
        content_length = int(content_length)
        if not self.check_disk(content_length):
            self.respond_internal_server_error()
            return
        content_type = self.headers['Content-Type']
        if not content_type:
            self.respond_bad_request()
            return
        boundary = self.parse_boundary(content_type)
        if not boundary:
            self.respond_bad_request()
            return
        try:
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
                with open(f'{self.dir}/{filename}', 'wb') as f:
                    parser.write_next_to(f)
            self.respond_redirect('/')
        except MultipartError:
            self.respond_bad_request()
        except PermissionError:
            self.respond_forbidden()

    def check_disk(self, content_length):
        path = self.dir
        if is_windows():
            path, _ = os.path.splitdrive(path)
        total, used, free = shutil.disk_usage(path)
        return free - content_length >= 1073741824

    def parse_boundary(self, content_type):
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


class TextSendHandler(BaseHandler):

    def __init__(self, text, *args, password=None):
        self.text = text
        super().__init__(*args, password=password)

    def do_get(self):
        if self.path != '/':
            self.respond_redirect('/')
            return
        self.respond_ok(self.build_html())

    def build_html(self):
        builder = HtmlBuilder()
        builder.start_head()
        builder.start_title()
        builder.append(self.hostname)
        builder.end_title()
        builder.start_style()
        builder.append('.container{height: 100%; display: flex; flex-direction: column;}')
        builder.append('.content{flex: 1; margin: 10% 8px; word-wrap: break-word; white-space: pre-wrap; overflow-y: auto;}')
        builder.end_style()
        builder.start_body()
        builder.append('<div class="container">')
        builder.append('<pre class="content">')
        builder.append(html.escape(self.text))
        builder.append('</pre>')
        builder.append('</div>')
        builder.end_body()
        return builder.build()


class TextReceiveHandler(BaseHandler):

    def __init__(self, *args, password=None):
        super().__init__(*args, password=password)

    def do_get(self):
        if self.path != '/':
            self.respond_redirect('/')
            return
        self.respond_ok(self.build_html())

    def build_html(self):
        builder = HtmlBuilder()
        builder.start_head()
        builder.start_title()
        builder.append(self.hostname)
        builder.end_title()
        builder.start_style()
        builder.append('.container{height: 100%; display: flex; flex-direction: column;}')
        builder.append('.content{flex: 1; margin: 10% 8px; display: flex; flex-direction: column;}')
        builder.append('.textarea{box-sizing: border-box; flex: 1; width: 100%;}')
        builder.append('.submit{width: 100%;}')
        builder.end_style()
        builder.start_script()
        builder.append('function on_keydown(e){')
        builder.append('if (e.key=="Control"){return;}')
        builder.append('if (e.ctrlKey && e.key=="Enter") {')
        builder.append('form = document.getElementById("form");')
        builder.append('if (form.reportValidity()){')
        builder.append('form.submit();')
        builder.append('e.preventDefault();')
        builder.append('e.stopPropagation();')
        builder.append('}')
        builder.append('}')
        builder.append('}')
        builder.append('window.onload = function() {')
        builder.append('text = document.getElementById("text");')
        builder.append('text.onkeydown = on_keydown;')
        builder.append('}')
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
        content_length = self.headers['Content-Length']
        if not content_length or not content_length.isdecimal():
            self.respond_bad_request()
            return
        content_length = int(content_length)
        if content_length <= 5 or content_length > 1048576:
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
        self.out = io.StringIO()

    def start_head(self):
        self.out.write('<!DOCTYPE html>')
        self.out.write('<html>')
        self.out.write('<head>')
        self.out.write('<meta name="viewport" content="width=device-width,initial-scale=1.0,minimum-scale=1.0"/>')

    def end_head(self):
        self.out.write('</head>')

    def start_title(self):
        self.out.write('<title>')

    def end_title(self):
        self.out.write('</title>')

    def start_style(self):
        self.out.write('<style type="text/css">')
        self.out.write('@media (min-width: 576px) {')
        self.out.write('body{width: 100%;}')
        self.out.write('}')
        self.out.write('@media (min-width: 768px) {')
        self.out.write('body{width: 80%;}')
        self.out.write('}')
        self.out.write('@media (min-width: 992px) {')
        self.out.write('body{width: 70%;}')
        self.out.write('}')
        self.out.write('@media (min-width: 1200px) {')
        self.out.write('body{width: 60%;}')
        self.out.write('}')
        self.out.write('html{height: 100%;}')
        self.out.write('body{height: 100%; margin: 0 auto; padding: 0; font-family: sans-serif;}')

    def end_style(self):
        self.out.write('</style>')

    def start_script(self):
        self.out.write('<script type="text/javascript">')

    def end_script(self):
        self.out.write('</script>')

    def start_body(self):
        self.out.write('<body>')

    def end_body(self):
        self.out.write('</body>')

    def append(self, code):
        self.out.write(code)

    def build(self):
        self.out.write('</html>')
        return self.out.getvalue()

    def __del__(self):
        self.out.close()


class MultipartParser:

    def __init__(self, stream, boundary, content_length):
        self.reader = MultipartReader(stream, content_length)
        self.separator = f'--{boundary}\r\n'.encode()
        self.terminator = f'--{boundary}--\r\n'.encode()
        self.state = MultipartState.INIT
        self.headers = {}
        self.content_disposition = re.compile(r'^form-data; name="(.+)"; filename="(.+)"\r\n$')
        self.name = None
        self.filename = None

    def has_next(self):
        if self.state == MultipartState.INIT:
            if not self.reader.has_next() or self.reader.next_line() != self.separator:
                raise MultipartError
            self.state = MultipartState.HEADER_START
        if self.state == MultipartState.HEADER_START:
            self._parse_headers()
            if self.state != MultipartState.PART_START:
                raise MultipartError
            return True
        if self.state == MultipartState.END:
            return False
        raise MultipartError

    def next_name(self):
        if self.state != MultipartState.PART_START:
            raise MultipartError
        return self.name

    def next_filename(self):
        if self.state != MultipartState.PART_START:
            raise MultipartError
        return self.filename

    def write_next_to(self, out):
        if self.state != MultipartState.PART_START:
            raise MultipartError
        line, next = None, None
        while True:
            if not line:
                if not self.reader.has_next():
                    raise MultipartError
                line = self.reader.next_line()
            if len(line) >= 2 and line[-2:] == b'\r\n':
                if not self.reader.has_next():
                    raise MultipartError
                next = self.reader.next_line()
                if next == self.separator:
                    if len(line) > 2:
                        out.write(line[:-2])
                    self.state = MultipartState.HEADER_START
                    return
                if next == self.terminator:
                    if len(line) > 2:
                        out.write(line[:-2])
                    if self.reader.has_next():
                        raise MultipartError
                    self.state = MultipartState.END
                    return
                out.write(line)
                line = next
            else:
                out.write(line)
                line = None

    def _parse_headers(self):
        if self.state != MultipartState.HEADER_START:
            raise MultipartError
        self.headers = {}
        self.name = None
        self.filename = None
        while True:
            if not self.reader.has_next():
                raise MultipartError
            line = self.reader.next_line().decode()
            if line == '\r\n':
                self.state = MultipartState.PART_START
                break
            parts = line.split(': ')
            if len(parts) != 2:
                raise MultipartError
            key, value = parts
            if key == 'Content-Disposition':
                match = self.content_disposition.match(value)
                if not match:
                    raise MultipartError
                self.name = match.group(1)
                self.filename = match.group(2)
            else:
                self.headers[key] = value
        if not self.name or not self.filename:
            raise MultipartError


class MultipartState:

    INIT = 0
    HEADER_START = 1
    PART_START = 2
    END = 3


class MultipartReader:

    def __init__(self, stream, total_length):
        self.stream = stream
        self.total_length = total_length
        self.read_len = 0

    def has_next(self):
        return self.read_len < self.total_length

    def next_line(self):
        line = self.stream.readline(65536)
        if not line:
            raise MultipartError
        self.read_len += len(line)
        if self.read_len > self.total_length:
            raise MultipartError
        return line


class MultipartError(ValueError):
    pass


def is_windows():
    return os.name == 'nt'


def on_interrupt(a, b):
    if not is_windows():
        sys.stderr.write('\n')
    sys.exit(1)


def parse_address(address):
    parts = address.split(':')
    if len(parts) == 1:
        if parts[0].isdecimal():
            return ('0.0.0.0', int(parts[0]))
        else:
            return (parts[0], 8888)
    host, port = parts
    if not host:
        host = '0.0.0.0'
    if not port:
        port = 8888
    return (host, int(port))


def print_prompt():
    if is_windows():
        sys.stderr.write('Enter your text, then press Ctrl + Z followed by the Enter key:\n')
    else:
        sys.stderr.write('Enter your text, then press Ctrl + D:\n')


def main():
    sys.tracebacklimit = 0
    signal.signal(signal.SIGINT, on_interrupt)
    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument('-b', '--bind', dest='address', metavar='ADDR:PORT', nargs=1, default=['0.0.0.0:8888'], help='bind address [default: 0.0.0.0:8888]')
    parser.add_argument('-a', '--all', action='store_true', help='show all files, including hidden ones')
    parser.add_argument('-t', '--text', action='store_true', help='text mode')
    parser.add_argument('-r', '--receive', action='store_true', help='receive mode')
    parser.add_argument('-p', '--password', nargs='?', const=os.getenv('SHARE_PASSWORD'), help='access password, if no PASSWORD is specified, the environment variable SHARE_PASSWORD will be used')
    parser.add_argument('arguments', nargs='*', help='a directory, files or texts')
    args = parser.parse_args()
    if args.password and len(args.password) < 3:
        raise ValueError('password is too short')
    if args.text:
        if args.receive:
            handler_class = functools.partial(TextReceiveHandler, password=args.password)
        else:
            if args.arguments:
                text = '\n'.join(args.arguments)
            else:
                print_prompt()
                text = ''.join(sys.stdin.readlines())
                if not text:
                    sys.exit(1)
            handler_class = functools.partial(TextSendHandler, text, password=args.password)
    else:
        if args.receive:
            dir = None
            if not args.arguments:
                dir = os.getcwd()
            elif os.path.isdir(args.arguments[0]):
                dir = args.arguments[0]
            else:
                raise FileNotFoundError(f'{args.arguments[0]} is not a directory')
            handler_class = functools.partial(FileReceiveHandler, dir, password=args.password)
        else:
            dir, files = None, None
            if not args.arguments:
                dir = os.getcwd()
            elif os.path.isdir(args.arguments[0]):
                dir = args.arguments[0]
            elif os.path.isfile(args.arguments[0]):
                files = args.arguments
            else:
                raise FileNotFoundError(f'{args.arguments[0]} is not a file or directory')
            if dir:
                handler_class = functools.partial(FileSendHandler, dir=dir, all=args.all, password=args.password)
            else:
                handler_class = functools.partial(FileSendHandler, files=files, password=args.password)
    with ShareServer(parse_address(args.address[0]), handler_class) as server:
        host, port = server.socket.getsockname()[:2]
        sys.stderr.write(f'Serving HTTP on {host} port {port} ...\n')
        server.serve_forever()


main()
