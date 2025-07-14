import re

from .common import InfoExtractor
from ..utils import traverse_obj


class XboxIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?(?P<url>xbox\.com/.*games/(?P<id>.+?)(\?|/|#|$))'

    def _real_extract(self, url):
        id = self._match_id(url)
        webpage = self._download_webpage(url, id)
        title = self._html_extract_title(webpage, id).split(':')[0]
        videos = [self._download_json(f'https://video.cascade.microsoft.com/api/og/xbox/videos/{i}/playback-info', i)
            for i in re.findall(r'data-otto-video="([^"]+)"', webpage)]
        video_id = lambda v: v['sources'][0]['url'].split('/')[-1]
        return self.playlist_result([i | {'id': video_id(i), 'title': i['videoTitle'], 'channel': title,
            'formats': self._extract_m3u8_formats(i['sources'][1]['url'], video_id(i))} for i in videos],
            id, title)


class XboxStoreIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?(?P<url>xbox\.com/.*games/store/[^/]*/(?P<id>.+?)(\?|/|#|$))'

    def _real_extract(self, url):
        id = self._match_id(url).upper()
        webpage = self._download_webpage(url, id)
        data = self._search_json(r'__PRELOADED_STATE__\s*=', webpage, 'data', id)
        product = traverse_obj(data, ('core2', 'products', 'productSummaries', id))
        if product.get('videos'):
            videos = product.get('videos', [])
            video_id = lambda v: v['url'].split('/')[-3]
            func = self._extract_ism_formats
        else:
            videos = product.get('cmsVideos', [])
            video_id = lambda v: v['url'].split('/')[-1].split('-AVS')[0]
            func = self._extract_m3u8_formats
        return self.playlist_result([i | {'id': video_id(i), 'channel': product['title'],
            'formats': func(i['url'], video_id(i))} for i in videos],
            id, product['title'])
