from .common import InfoExtractor
from ..utils import traverse_obj, url_or_none


class SymphonyliveIE(InfoExtractor):
    _VALID_URL = r'https?://(?:.*\.)?symphony\.live/m/(?P<id>[^/]+)'
    _TESTS = [{
        'url': 'https://watch.symphony.live/m/iSLexFsu/made-in-america-trailer?r=79jFxaiM',
        'info_dict': {
            'id': 'iSLexFsu',
            'title': 'Made In America - Trailer',
            'duration': 174,
            'timestamp': 1751404805,
        },
    }]

    def _real_extract(self, url):
        video_id = self._match_id(url)
        data = ('{"provider":"cleeng","credentials":{"token":""},"asset":{"id":"'
            + video_id + '","drmPolicyId":"","params":{},"accessType":"public"}}')
        token = self._download_json('https://ent-api.symphony.live/entitlement',
            data=data.encode(), video_id=video_id).get('token')
        video = traverse_obj(self._download_json('https://cdn.jwplayer.com/v2/media/' + video_id,
            query={'token': token}, video_id=video_id, fatal=False), ('playlist', 0))
        link = traverse_obj(video, ('sources', 0, 'file'), expected_type=url_or_none)
        return video | {'id': video_id, 'timestamp': video.get('pubdate'),
            'formats': self._extract_m3u8_formats(link, video_id)}
