from .common import InfoExtractor
from ..utils import url_basename, traverse_obj


class XboxIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?(?P<url>xbox\.com/.*games/store/(?P<id>.+?)(\?|#|$))'

    def _real_extract(self, url):
        webpage = self._download_webpage(url, url_basename(url))
        data = self._search_json(r'__PRELOADED_STATE__\s*=', webpage, 'data', url_basename(url))
        product = traverse_obj(data, ('core2', 'products', 'productSummaries', url_basename(url).upper()))
        return self.playlist_result([{'id': i['purpose'], 'title': i['purpose'], 'channel': i['title'],
            'formats': self._extract_m3u8_formats(i['url'], i['purpose'])} for i in product['cmsVideos']],
            url_basename(url), product['title'])
