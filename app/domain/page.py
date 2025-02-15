from litestar import get
from litestar.response import Template


@get("/")
async def page() -> Template:
    return Template("page.html")
