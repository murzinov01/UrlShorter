from fastapi import APIRouter, Depends, Response, Request, Body, Path, status
from fastapi.exceptions import HTTPException
from pydantic import AnyUrl

from ..db.dals.url_dal import UrlDAL
from ..dependencies import get_url_dal
from ..enums import Tags
from ..schemas.url import Url, UrlLong, UrlShort
from ..utils import generate_short_url

router = APIRouter(prefix="/urls", tags=[Tags.urls])

additional_router = APIRouter(tags=[Tags.additional])


@router.post("/", response_model=UrlShort, status_code=status.HTTP_200_OK, description="Generate short url based on full url")
async def create_short_url(
        response: Response,
        url_long: UrlLong = Body(
            example={
                "url": "https://habr.com/ru/all/"
            }
        ),
        url_dal: UrlDAL = Depends(get_url_dal)
):
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


@router.get("/{short_url:path}", response_model=UrlLong, description="Get full url by short link previously generated")
async def get_full_url(
        short_url: AnyUrl = Path(example="http://const.com/68d0"),
        url_dal: UrlDAL = Depends(get_url_dal)
):
    if url_entry := await url_dal.get_url(short_url):
        return url_entry
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short url does not exist")


@router.delete("/{short_url:path}", status_code=status.HTTP_204_NO_CONTENT, description="Delete short url")
async def delete_short_url(
        short_url: AnyUrl = Path(example="http://const.com/68d0"),
        url_dal: UrlDAL = Depends(get_url_dal)
):
    if await url_dal.get_url(short_url):
        await url_dal.delete_url(short_url)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short url does not exist")


# Additional Endpoint
@additional_router.get("/urls/", response_model=list[Url], description="Get all urls (short and full) stored in the system")
async def get_urls(skip: int = 0, limit: int = 100, url_dal: UrlDAL = Depends(get_url_dal)):
    result = await url_dal.get_all_urls(skip, limit)
    return result


# With Redirect
@additional_router.get("/{token}", status_code=status.HTTP_302_FOUND)
async def redirect(
        request: Request,
        response: Response,
        token: str = Path(example="68d0"),
        url_dal: UrlDAL = Depends(get_url_dal)
):
    """
    Redirect to long url based on short one.
    This endpoint will replace the current domain (**localhost**) with **const.com**, so you can test the redirect in the developer tools
    """
    short_url = str(request.url)
    # Replace localhost with the domain from the short link generator
    # Just for test
    short_url = short_url.replace("localhost:8000", "const.com")
    if url_entry := await url_dal.get_url(short_url):
        response.status_code = status.HTTP_302_FOUND
        response.headers["Location"] = url_entry.url
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short url does not exist"
        )
