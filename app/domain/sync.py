from app.lzpy import LZString
from app.model import Archive

from litestar import Response, get
from sqlalchemy.ext.asyncio import AsyncSession


@get("/sync")
async def sync(key: str, db_session: AsyncSession) -> Response:
    if not key:
        return Response(status_code=400, content={"error": "未填写秘钥"})
    if len(key) != 40:
        return Response(status_code=400, content={"error": "秘钥长度不合法"})

    archive = await db_session.get(Archive, key)
    if archive is None:
        return Response(status_code=400, content={"error": "秘钥不存在"})

    result = LZString.compressToUTF16(archive.data)
    return Response(
        status_code=200,
        content={
            "data": result,
            "vote_times": archive.vote_times,
            "updated_at": archive.updated_at,
        },
    )
