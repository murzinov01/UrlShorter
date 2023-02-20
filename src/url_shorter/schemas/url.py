from pydantic import AnyUrl, BaseModel


class UrlShort(BaseModel):
    short_url: AnyUrl

    class Config:
        orm_mode = True


class UrlLong(BaseModel):
    url: AnyUrl

    class Config:
        orm_mode = True


class Url(UrlShort, UrlLong):
    pass

    class Config:
        orm_mode = True
