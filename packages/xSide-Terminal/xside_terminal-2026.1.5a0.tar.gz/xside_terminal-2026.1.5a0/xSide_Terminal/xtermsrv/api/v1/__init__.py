# -*- coding: utf-8 -*-
# Copyright (C) 2018-2025 Connet Information Technology Company, Shanghai.

from . import terminal
from .ptymgr import PtySession, PtySessionManager

def routes():
    return [
        (r"/api/v1/terminal", terminal.RegisterAPI),
        (r"/api/v1/terminal/(.*)/size", terminal.ResizeAPI),
        (r"/ws/v1/terminal/(.*)", terminal.XtermjsSocket)
    ]