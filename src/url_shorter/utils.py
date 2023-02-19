from hashlib import md5


def generate_short_url(url: str, protocol="http://", domain: str = "const.com", hash_length=4) -> str:
    url_hash = md5(url.encode("utf-8")).hexdigest()
    if hash_length > len(url_hash):
        hash_length = len(url_hash)
    if hash_length < 1:
        raise ValueError
    short_url = f"{protocol}{domain}/{url_hash[:hash_length]}"
    return short_url
