from fastapi import APIRouter, Depends, Response, status
from fastapi.exceptions import HTTPException
from pydantic import AnyUrl

from ..db.dals.url_dal import UrlDAL
from ..dependencies import get_url_dal
from ..enums import Tags
from ..schemas.url import Url, UrlLong, UrlShort
from ..utils import generate_short_url

router = APIRouter(prefix="/urls", tags=[Tags.urls])

additional_router = APIRouter(prefix="/urls", tags=[Tags.additional])


@router.post("/", response_model=UrlShort, status_code=status.HTTP_200_OK)
async def create_short_url(url_long: UrlLong, response: Response, url_dal: UrlDAL = Depends(get_url_dal)):
    # check if short utl already exists
    if url_entry := await url_dal.get_short_utl(url_long.url):
        return UrlShort(short_url=url_entry.short_url)
    else:
        url_short = UrlShort(short_url=generate_short_url(url_long.url))
        if await url_dal.get_url(url_short.short_url):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="A collision occurred while generating a short link",
            )
        await url_dal.create_url(url=url_long.url, short_url=url_short.short_url)
        response.status_code = status.HTTP_201_CREATED
        return url_short


@router.get("/{short_url:path}", response_model=UrlLong)
async def get_full_url(short_url: AnyUrl, url_dal: UrlDAL = Depends(get_url_dal)):
    if url_entry := await url_dal.get_url(short_url):
        return url_entry
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short url does not exist")


# With Redirect
# @router.get("/{short_url:path}")
# async def get_full_url(short_url: AnyUrl, response: Response, url_dal: UrlDAL = Depends(get_url_dal)):
#     if url_entry := await url_dal.get_url(short_url):
#         print(url_entry, type(url_entry))
#         response.status_code = status.HTTP_302_FOUND
#         response.headers["Location"] = url_entry.url
#     else:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Short url does not exist"
#         )


@router.delete("/{short_url:path}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_short_url(short_url: AnyUrl, url_dal: UrlDAL = Depends(get_url_dal)):
    if await url_dal.get_url(short_url):
        await url_dal.delete_url(short_url)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short url does not exist")


# Additional Endpoint
@additional_router.get("/", response_model=list[Url])
async def get_urls(skip: int = 0, limit: int = 100, url_dal: UrlDAL = Depends(get_url_dal)):
    result = await url_dal.get_all_urls(skip, limit)
    print(result)
    return result
