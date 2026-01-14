import requests

from .base import Source
from selectolax.parser import HTMLParser


class ApkPure(Source):
    def __init__(self) -> None:
        self._download_url = "https://d.apkpure.com/b/XAPK/{}?version={}"
        self._search_url = "https://apkpure.com/search?q={}"
        self._headers: dict[str, str] = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            ),
            "Accept": "application/json",
        }

    def get_download_url(
        self,
        package_name: str, version:
        str = 'latest'
    ) -> str:
        return self._download_url.format(package_name, version)

    def search(self, keyword: str, limit: int = 20) -> list[dict]:
        url: str = self._search_url.format(keyword, limit)
        response: requests.Response = requests.get(url, headers=self._headers)
        tree = HTMLParser(response.text)
        apps = []
        for node in tree.css('li > dl[data-dt-recid]'):
            name = node.css_first('p.p1').text().strip()
            developer = node.css_first('p.p2').text().strip()
            rating = node.css_first('span.star').text().strip()
            img = node.css_first('div.l > img').attrs.get('src')
            package_name = (
                node.css_first('a.dd')
                .attrs.get('href', '')
                .split('/')[-1]
            )

            apps.append({
                'name': name,
                'package_name': package_name,
                'icon_url': img,
                'developer': developer,
                'rating': rating or 'N/A',
            })

        return apps
