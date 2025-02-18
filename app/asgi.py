from litestar import Litestar


def create_app() -> Litestar:
    from app.server.core import ApplicationCore

    return Litestar(plugins=[ApplicationCore()])
