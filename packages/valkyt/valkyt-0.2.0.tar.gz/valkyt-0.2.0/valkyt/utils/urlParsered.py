from urllib.parse import urlparse
class UrlPars:

    @staticmethod
    def get_domain(url: str) -> str | None:
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            return domain
        except Exception as e:
            print(f"error : {e}")
            return None