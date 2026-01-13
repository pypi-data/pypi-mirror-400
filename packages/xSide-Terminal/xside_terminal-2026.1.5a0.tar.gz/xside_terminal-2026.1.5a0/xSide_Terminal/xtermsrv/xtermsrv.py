# -*- coding: utf-8 -*-
# Copyright (C) 2018-2025 Connet Information Technology Company, Shanghai.

import os
import sys
import tornado
import asyncio
import argparse
import os.path as osp
import tornado.websocket
from api import v1

import logging

logger = logging.getLogger("xterm.server")

debug_mode: bool = False
ptymgr_v1: v1.PtySessionManager|None = None


class Home(tornado.web.RequestHandler):
    """Handles index request."""

    def get(self):
        """Get static index.html page and get javascript running."""
        self.render('index.html')

    def post(self):
        """POST verb: Forbidden."""
        self.set_status(403)


def main(port: int):
    """create and setup a new tornado server"""
    global ptymgr_v1

    # --- create and return a tornado Web Application instance.
    settings = {
        "static_path": osp.join(osp.dirname(__file__), "static"),
        "template_path": osp.join(osp.dirname(__file__), "static")
    }
    application = tornado.web.Application([
        (r"/", Home),
        *v1.routes()
    ],
        debug=debug_mode,
        **settings
    )

    # --- PTY session manager
    application.ptymgr_v1 = ptymgr_v1 = v1.PtySessionManager()
    application.listen(port, address='127.0.0.1')
    logger.info(f"xtermjs server (pid={os.getpid()}) is now at 127.0.0.1:{port}")

    try:
        ioloop = tornado.ioloop.IOLoop.instance()
        ioloop.start()
    except KeyboardInterrupt:
        pass
    finally:
        logger.info('Closing xtermjs server...')
        tornado.ioloop.IOLoop.instance().stop()


if __name__ == '__main__':
    # log to file
    if (sys.version_info[0] == 3 and sys.version_info[1] >= 8 and
            sys.platform.startswith('win')):
        # IMPORTANT (Windows):
        #
        # This project relies on FD readiness semantics (select/poll),
        # e.g. for terminal I/O, subprocess pipes, or socket-based backends.
        #
        # On Windows, Python 3.8+ uses the Proactor event loop by default,
        # which does NOT support select/poll-style FD monitoring and does
        # not implement the add_reader/add_writer APIs.
        #
        # Even if this codebase does not call add_reader/add_writer directly,
        # select/poll usage (directly or via libraries such as Tornado, zmq,
        # or terminal managers) implicitly requires a Selector-based event loop.
        #
        # Removing this policy will cause subtle or hard failures on Windows,
        # including:
        #   - stalled or missing I/O
        #   - subprocess stdout/stderr not updating
        #   - WebSocket or terminal sessions freezing
        #
        # This is a design constraint of asyncio on Windows, not a workaround.
        # See:
        #   - Python asyncio Proactor vs Selector design
        #   - pyzmq / tornado / jupyter Windows compatibility issues
        #
        # DO NOT REMOVE unless the backend is fully rewritten to avoid
        # select/poll and FD-based I/O.
        # Reference:
        #   - https://github.com/zeromq/pyzmq/issues/1423
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    parser = argparse.ArgumentParser(description='xtermjs server packed by xSide')
    parser.add_argument(
        '--port',
        default=8070,
        help="TCP port to be listened on"
    )
    parser.add_argument(
        '--debug',
        action=argparse.BooleanOptionalAction,
        default=False,
        help='enable debug mode'
    )
    args = parser.parse_args()

    debug_mode = args.debug
    if debug_mode:
        logging.basicConfig(level=logging.DEBUG)

    port = int(args.port)
    main(port)
