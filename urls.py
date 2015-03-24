#!/usr/bin/env python
# coding=utf8
try:
    import psyco

    psyco.full()
except:
    pass

from handlers import account, admin, blog
from handlers import ErrorHandler

routes = []
routes.extend(blog.routes)
routes.extend(account.routes)
routes.extend(admin.routes)
routes.append((r"/(.*)", ErrorHandler))
