# coding: utf-8
from __future__ import unicode_literals

from base64 import b64encode
import re
import math

from ..compat import (
    compat_str,
    compat_HTTPError
)
from ..utils import (
    float_or_none,
    mimetype2ext,
    parse_duration,
    parse_codecs,
    int_or_none,
    unified_timestamp,
    try_get,
    ExtractorError
)
from .common import InfoExtractor

ROOT_BASE_URL = "https://www.picta.cu/"
API_BASE_URL = "https://api.picta.cu/api/v2/"


# noinspection PyAbstractClass
class PictaBaseIE(InfoExtractor):

    @staticmethod
    def _extract_video(video, video_id=None, require_title=True):
        if len(video["results"]) == 0:
            raise ExtractorError("Cannot find video!")

        title = (
            video["results"][0]["nombre"]
            if require_title
            else video.get("results")[0].get("nombre")
        )
        description = try_get(
            video, lambda x: x["results"][0]["descripcion"], compat_str
        )
        slug_url = try_get(
            video, lambda x: x["results"][0]["slug_url"], compat_str
        )
        uploader = try_get(
            video, lambda x: x["results"][0]["usuario"]["username"], compat_str
        )
        add_date = try_get(video, lambda x: x["results"][0]["fecha_creacion"])
        timestamp = int_or_none(unified_timestamp(add_date))
        thumbnail = try_get(video, lambda x: x["results"][0]["url_imagen"])
        manifest_url = try_get(video, lambda x: x["results"][0]["url_manifiesto"])
        category = try_get(
            video, lambda x: x["results"][0]["categoria"]["tipologia"]["nombre"], compat_str
        )
        playlist_channel = (
            video["results"][0]["lista_reproduccion_canal"][0]
            if len(video["results"][0]["lista_reproduccion_canal"]) > 0
            else None
        )
        subtitle_url = try_get(video, lambda x: x["results"][0]["url_subtitulo"])

        return {
            "id": try_get(video, lambda x: x["results"][0]["id"], compat_str) or video_id,
            "title": title,
            "slug_url": slug_url,
            "description": description,
            "thumbnail": thumbnail,
            "uploader": uploader,
            "timestamp": timestamp,
            "category": [category] if category else None,
            "manifest_url": manifest_url,
            "playlist_channel": playlist_channel,
            "subtitle_url": subtitle_url,
        }


# noinspection PyAbstractClass
class PictaIE(PictaBaseIE):
    IE_NAME = "picta"
    IE_DESC = "Picta videos"
    _VALID_URL = r"https?://(?:www\.)?picta\.cu/(?:medias|movie|embed)/(?:\?v=)?(?P<id>[\da-z-]+)" \
                 r"(?:\?playlist=(?P<playlist_id>[\da-z-]+))?"

    _TESTS = [
        {
            "url": "https://www.picta.cu/medias/orishas-everyday-2019-01-16-16-36-42-443003",
            "file": "Orishas - Everyday-orishas-everyday-2019-01-16-16-36-42-443003.webm",
            "md5": "7ffdeb0043500c4bb660c04e74e90f7a",
            "info_dict": {
                "id": "818",
                "slug_url": "orishas-everyday-2019-01-16-16-36-42-443003",
                "ext": "webm",
                "title": "Orishas - Everyday",
                "thumbnail": r"re:^https?://.*imagen/img.*\.png$",
                "upload_date": "20190116",
                "description": "Orishas - Everyday (Video Oficial)",
                "uploader": "admin",
                "timestamp": 1547656602,
            },
            "params": {"format": "4"},
        },
        {
            "url": ("https://www.picta.cu/embed/"
                    "palmiche-galeno-tercer-lugar-torneo-virtual-robotica-2020-05-21-16-15-31-431895"),
            "file": ("Palmiche Galeno tercer lugar en torneo virtual de "
                     "robótica-palmiche-galeno-tercer-lugar-torneo-virtual-robotica-2020-05-21-16-15-31-431895.mp4"),
            "md5": "6031b7a3add2eade9c5bef7ecf5d4b02",
            "info_dict": {
                "id": "3500",
                "slug_url": "palmiche-galeno-tercer-lugar-torneo-virtual-robotica-2020-05-21-16-15-31-431895",
                "ext": "mp4",
                "title": "Palmiche Galeno tercer lugar en torneo virtual de robótica",
                "thumbnail": r"re:^https?://.*imagen/img.*\.jpeg$",
                "upload_date": "20200521",
                "description": ("En esta emisión:\r\n"
                                "Iniciará en La Habana nuevo método para medir el consumo "
                                "eléctrico |  https://bit.ly/jtlecturacee\r\n"
                                "GICAcovid: nueva aplicación web para los centros de "
                                "aislamiento |  https://bit.ly/jtgicacovid\r\n"
                                "Obtuvo Palmiche tercer lugar en la primera competencia "
                                "virtual de robótica |  https://bit.ly/jtpalmichegaleno\r\n"
                                "\r\n"
                                "Síguenos en:\r\n"
                                "Facebook: http://www.facebook.com/JuventudTecnicaCuba\r\n"
                                "Twitter e Instagram: @juventudtecnica\r\n"
                                "Telegram: http://t.me/juventudtecnica"),
                "uploader": "ernestoguerra21",
                "timestamp": 1590077731,
            },
        },
        {
            "url": "https://www.picta.cu/movie/phineas-ferb-pelicula-candace-universo-2020-08-28-21-00-32-857026",
            "only_matching": True,
        },
        {"url": "https://www.picta.cu/embed/?v=818", "only_matching": True},
        {
            "url": ("https://www.picta.cu/embed/"
                    "palmiche-galeno-tercer-lugar-torneo-virtual-robotica-2020-05-21-16-15-31-431895"),
            "only_matching": True,
        },
    ]

    _LANGUAGES_CODES = ['es']
    _LANG_ES = _LANGUAGES_CODES[0]

    _SUBTITLE_FORMATS = ('srt', )

    def _real_initialize(self):
        self.playlist_id = None

    @classmethod
    def _match_playlist_id(cls, url):
        if '_VALID_URL_RE' not in cls.__dict__:
            cls._VALID_URL_RE = re.compile(cls._VALID_URL)
        m = cls._VALID_URL_RE.match(url)
        assert m
        return m.group('playlist_id')

    def _get_subtitles(self, video):
        sub_lang_list = {}
        lang = self._LANG_ES

        sub_url = video.get('subtitle_url', '')

        if sub_url:
            sub_formats = []
            for ext in self._SUBTITLE_FORMATS:
                sub_formats.append({
                    'url': sub_url,
                    'ext': ext,
                })
            sub_lang_list[lang] = sub_formats
        if not sub_lang_list:
            self._downloader.report_warning('video doesn\'t have subtitles')
            return {}
        return sub_lang_list

    def _parse_mpd_formats(self, mpd_doc, mpd_id=None, mpd_base_url='', mpd_url=None):
        """
        Parse formats from MPD manifest.
        References:
         1. MPEG-DASH Standard, ISO/IEC 23009-1:2014(E),
            http://standards.iso.org/ittf/PubliclyAvailableStandards/c065274_ISO_IEC_23009-1_2014.zip
         2. https://en.wikipedia.org/wiki/Dynamic_Adaptive_Streaming_over_HTTP
        Note: Fix MPD manifest for Picta
         3. https://developer.mozilla.org/en-US/docs/Web/Guide/Audio_and_video_delivery/Setting_up_adaptive_streaming_media_sources
        """
        if mpd_doc.get('type') == 'dynamic':
            return []

        namespace = self._search_regex(r'(?i)^{([^}]+)?}MPD$', mpd_doc.tag, 'namespace', default=None)

        def _add_ns(path):
            return self._xpath_ns(path, namespace)

        def is_drm_protected(element):
            return element.find(_add_ns('ContentProtection')) is not None

        def extract_multisegment_info(element, ms_parent_info):
            ms_info = ms_parent_info.copy()

            # As per [1, 5.3.9.2.2] SegmentList and SegmentTemplate share some
            # common attributes and elements.  We will only extract relevant
            # for us.
            def extract_common(source):
                segment_timeline = source.find(_add_ns('SegmentTimeline'))
                if segment_timeline is not None:
                    s_e = segment_timeline.findall(_add_ns('S'))
                    if s_e:
                        ms_info['total_number'] = 0
                        ms_info['s'] = []
                        for s in s_e:
                            r = int(s.get('r', 0))
                            ms_info['total_number'] += 1 + r
                            ms_info['s'].append({
                                't': int(s.get('t', 0)),
                                # @d is mandatory (see [1, 5.3.9.6.2, Table 17, page 60])
                                'd': int(s.attrib['d']),
                                'r': r,
                            })
                start_number = source.get('startNumber')
                if start_number:
                    ms_info['start_number'] = int(start_number)
                timescale = source.get('timescale')
                if timescale:
                    ms_info['timescale'] = int(timescale)
                segment_duration = source.get('duration')
                if segment_duration:
                    ms_info['segment_duration'] = float(segment_duration)

            def extract_Initialization(source):
                initialization = source.find(_add_ns('Initialization'))
                # TODO: Fix Initialization sourceURL
                if initialization is not None:
                    ms_info['initialization_url'] = initialization.get('sourceURL')

            segment_list = element.find(_add_ns('SegmentList'))
            if segment_list is not None:
                extract_common(segment_list)
                extract_Initialization(segment_list)
                segment_urls_e = segment_list.findall(_add_ns('SegmentURL'))
                if segment_urls_e:
                    # TODO: Fix SegmentURL media
                    segment_urls = [segment.get('media') for segment in segment_urls_e if segment.get('media') is not None]
                    if segment_urls:
                        ms_info['segment_urls'] = segment_urls
            else:
                segment_template = element.find(_add_ns('SegmentTemplate'))
                if segment_template is not None:
                    extract_common(segment_template)
                    media = segment_template.get('media')
                    if media:
                        ms_info['media'] = media
                    initialization = segment_template.get('initialization')
                    if initialization:
                        ms_info['initialization'] = initialization
                    else:
                        extract_Initialization(segment_template)
            return ms_info

        mpd_duration = parse_duration(mpd_doc.get('mediaPresentationDuration'))
        formats = []
        for period in mpd_doc.findall(_add_ns('Period')):
            period_duration = parse_duration(period.get('duration')) or mpd_duration
            period_ms_info = extract_multisegment_info(period, {
                'start_number': 1,
                'timescale': 1,
            })
            for adaptation_set in period.findall(_add_ns('AdaptationSet')):
                if is_drm_protected(adaptation_set):
                    continue
                adaption_set_ms_info = extract_multisegment_info(adaptation_set, period_ms_info)
                for representation in adaptation_set.findall(_add_ns('Representation')):
                    if is_drm_protected(representation):
                        continue
                    representation_attrib = adaptation_set.attrib.copy()
                    representation_attrib.update(representation.attrib)
                    # According to [1, 5.3.7.2, Table 9, page 41], @mimeType is mandatory
                    mime_type = representation_attrib['mimeType']
                    content_type = mime_type.split('/')[0]
                    if content_type == 'text':
                        # TODO implement WebVTT downloading
                        pass
                    elif content_type in ('video', 'audio'):
                        base_url = ''
                        for element in (representation, adaptation_set, period, mpd_doc):
                            base_url_e = element.find(_add_ns('BaseURL'))
                            if base_url_e is not None:
                                base_url = base_url_e.text + base_url
                                if re.match(r'^https?://', base_url):
                                    break
                        if mpd_base_url and not re.match(r'^https?://', base_url):
                            if not mpd_base_url.endswith('/') and not base_url.startswith('/'):
                                mpd_base_url += '/'
                            base_url = mpd_base_url + base_url
                        representation_id = representation_attrib.get('id')
                        lang = representation_attrib.get('lang')
                        url_el = representation.find(_add_ns('BaseURL'))
                        filesize = int_or_none(url_el.attrib.get('{http://youtube.com/yt/2012/10/10}contentLength') if url_el is not None else None)
                        bandwidth = int_or_none(representation_attrib.get('bandwidth'))
                        f = {
                            'format_id': '%s-%s' % (mpd_id, representation_id) if mpd_id else representation_id,
                            'manifest_url': mpd_url,
                            'ext': mimetype2ext(mime_type),
                            'width': int_or_none(representation_attrib.get('width')),
                            'height': int_or_none(representation_attrib.get('height')),
                            'tbr': float_or_none(bandwidth, 1000),
                            'asr': int_or_none(representation_attrib.get('audioSamplingRate')),
                            'fps': int_or_none(representation_attrib.get('frameRate')),
                            'language': lang if lang not in ('mul', 'und', 'zxx', 'mis') else None,
                            'format_note': 'DASH %s' % content_type,
                            'filesize': filesize,
                            'container': mimetype2ext(mime_type) + '_dash',
                        }
                        f.update(parse_codecs(representation_attrib.get('codecs')))
                        representation_ms_info = extract_multisegment_info(representation, adaption_set_ms_info)

                        def prepare_template(template_name, identifiers):
                            tmpl = representation_ms_info[template_name]
                            # First of, % characters outside $...$ templates
                            # must be escaped by doubling for proper processing
                            # by % operator string formatting used further (see
                            # https://github.com/ytdl-org/youtube-dl/issues/16867).
                            t = ''
                            in_template = False
                            for c in tmpl:
                                t += c
                                if c == '$':
                                    in_template = not in_template
                                elif c == '%' and not in_template:
                                    t += c
                            # Next, $...$ templates are translated to their
                            # %(...) counterparts to be used with % operator
                            t = t.replace('$RepresentationID$', representation_id)
                            t = re.sub(r'\$(%s)\$' % '|'.join(identifiers), r'%(\1)d', t)
                            t = re.sub(r'\$(%s)%%([^$]+)\$' % '|'.join(identifiers), r'%(\1)\2', t)
                            t.replace('$$', '$')
                            return t

                        # @initialization is a regular template like @media one
                        # so it should be handled just the same way (see
                        # https://github.com/ytdl-org/youtube-dl/issues/11605)
                        if 'initialization' in representation_ms_info:
                            initialization_template = prepare_template(
                                'initialization',
                                # As per [1, 5.3.9.4.2, Table 15, page 54] $Number$ and
                                # $Time$ shall not be included for @initialization thus
                                # only $Bandwidth$ remains
                                ('Bandwidth', ))
                            representation_ms_info['initialization_url'] = initialization_template % {
                                'Bandwidth': bandwidth,
                            }

                        def location_key(location):
                            return 'url' if re.match(r'^https?://', location) else 'path'

                        if 'segment_urls' not in representation_ms_info and 'media' in representation_ms_info:

                            media_template = prepare_template('media', ('Number', 'Bandwidth', 'Time'))
                            media_location_key = location_key(media_template)

                            # As per [1, 5.3.9.4.4, Table 16, page 55] $Number$ and $Time$
                            # can't be used at the same time
                            if '%(Number' in media_template and 's' not in representation_ms_info:
                                segment_duration = None
                                if 'total_number' not in representation_ms_info and 'segment_duration' in representation_ms_info:
                                    segment_duration = float_or_none(representation_ms_info['segment_duration'], representation_ms_info['timescale'])
                                    representation_ms_info['total_number'] = int(math.ceil(float(period_duration) / segment_duration))
                                representation_ms_info['fragments'] = [{
                                    media_location_key: media_template % {
                                        'Number': segment_number,
                                        'Bandwidth': bandwidth,
                                    },
                                    'duration': segment_duration,
                                } for segment_number in range(
                                    representation_ms_info['start_number'],
                                    representation_ms_info['total_number'] + representation_ms_info['start_number'])]
                            else:
                                # $Number*$ or $Time$ in media template with S list available
                                # Example $Number*$: http://www.svtplay.se/klipp/9023742/stopptid-om-bjorn-borg
                                # Example $Time$: https://play.arkena.com/embed/avp/v2/player/media/b41dda37-d8e7-4d3f-b1b5-9a9db578bdfe/1/129411
                                representation_ms_info['fragments'] = []
                                segment_time = 0
                                segment_d = None
                                segment_number = representation_ms_info['start_number']

                                def add_segment_url():
                                    segment_url = media_template % {
                                        'Time': segment_time,
                                        'Bandwidth': bandwidth,
                                        'Number': segment_number,
                                    }
                                    representation_ms_info['fragments'].append({
                                        media_location_key: segment_url,
                                        'duration': float_or_none(segment_d, representation_ms_info['timescale']),
                                    })

                                for num, s in enumerate(representation_ms_info['s']):
                                    segment_time = s.get('t') or segment_time
                                    segment_d = s['d']
                                    add_segment_url()
                                    segment_number += 1
                                    for r in range(s.get('r', 0)):
                                        segment_time += segment_d
                                        add_segment_url()
                                        segment_number += 1
                                    segment_time += segment_d
                        elif 'segment_urls' in representation_ms_info and 's' in representation_ms_info:
                            # No media template
                            # Example: https://www.youtube.com/watch?v=iXZV5uAYMJI
                            # or any YouTube dashsegments video
                            fragments = []
                            segment_index = 0
                            timescale = representation_ms_info['timescale']
                            for s in representation_ms_info['s']:
                                duration = float_or_none(s['d'], timescale)
                                for r in range(s.get('r', 0) + 1):
                                    segment_uri = representation_ms_info['segment_urls'][segment_index]
                                    fragments.append({
                                        location_key(segment_uri): segment_uri,
                                        'duration': duration,
                                    })
                                    segment_index += 1
                            representation_ms_info['fragments'] = fragments
                        elif 'segment_urls' in representation_ms_info:
                            # Segment URLs with no SegmentTimeline
                            # Example: https://www.seznam.cz/zpravy/clanek/cesko-zasahne-vitr-o-sile-vichrice-muze-byt-i-zivotu-nebezpecny-39091
                            # https://github.com/ytdl-org/youtube-dl/pull/14844
                            fragments = []
                            segment_duration = float_or_none(
                                representation_ms_info['segment_duration'],
                                representation_ms_info['timescale']) if 'segment_duration' in representation_ms_info else None
                            for segment_url in representation_ms_info['segment_urls']:
                                fragment = {
                                    location_key(segment_url): segment_url,
                                }
                                if segment_duration:
                                    fragment['duration'] = segment_duration
                                fragments.append(fragment)
                            representation_ms_info['fragments'] = fragments
                        # If there is a fragments key available then we correctly recognized fragmented media.
                        # Otherwise we will assume unfragmented media with direct access. Technically, such
                        # assumption is not necessarily correct since we may simply have no support for
                        # some forms of fragmented media renditions yet, but for now we'll use this fallback.
                        if 'fragments' in representation_ms_info:
                            f.update({
                                # NB: mpd_url may be empty when MPD manifest is parsed from a string
                                'url': mpd_url or base_url,
                                'fragment_base_url': base_url,
                                'fragments': [],
                                'protocol': 'http_dash_segments',
                            })
                            if 'initialization_url' in representation_ms_info:
                                initialization_url = representation_ms_info['initialization_url']
                                if not f.get('url'):
                                    f['url'] = initialization_url
                                f['fragments'].append({location_key(initialization_url): initialization_url})
                            f['fragments'].extend(representation_ms_info['fragments'])
                        else:
                            # Assuming direct URL to unfragmented media.
                            f['url'] = base_url
                        formats.append(f)
                    else:
                        self.report_warning('Unknown MIME type %s in DASH manifest' % mime_type)
        return formats

    def _real_extract(self, url):
        playlist_id = None
        video_id = self._match_id(url)
        json_url = API_BASE_URL + "publicacion/?format=json&slug_url_raw=%s" % video_id
        video = self._download_json(json_url, video_id, "Downloading video JSON")
        info = self._extract_video(video, video_id)
        if (
                info["playlist_channel"]
                and self.playlist_id is None
                and self._match_playlist_id(url) is None
        ):
            playlist_id = info["playlist_channel"].get("id")
            self.playlist_id = playlist_id
        # Download Playlist (--yes-playlist) in first place
        if (
                self.playlist_id is None
                and self._match_playlist_id(url)
                and not self._downloader.params.get('noplaylist')
        ):
            playlist_id = compat_str(self._match_playlist_id(url))
            self.playlist_id = playlist_id
            self.to_screen('Downloading playlist %s - add --no-playlist to just download video' % playlist_id)
            return self.url_result(
                ROOT_BASE_URL + "medias/" + video_id + "?" + "playlist=" + playlist_id,
                PictaUserPlaylistIE.ie_key(),
                playlist_id
            )
        elif playlist_id and not self._downloader.params.get('noplaylist'):
            playlist_id = compat_str(playlist_id)
            self.to_screen('Downloading playlist %s - add --no-playlist to just download video' % playlist_id)
            return self.url_result(
                ROOT_BASE_URL + "medias/" + video_id + "?" + "playlist=" + playlist_id,
                PictaChannelPlaylistIE.ie_key(),
                playlist_id
            )
        elif self._downloader.params.get('noplaylist'):
            self.to_screen('Downloading just video %s because of --no-playlist' % video_id)

        formats = []
        # MPD manifest
        if info.get("manifest_url"):
            formats.extend(
                self._extract_mpd_formats(info.get("manifest_url"), video_id)
            )

        if not formats:
            raise ExtractorError("Cannot find video formats")

        self._sort_formats(formats)
        info["formats"] = formats

        # subtitles
        video_subtitles = self.extract_subtitles(info)
        info["subtitles"] = video_subtitles
        return info


# noinspection PyAbstractClass
class PictaEmbedIE(InfoExtractor):
    IE_NAME = "picta:embed"
    IE_DESC = "Picta embedded videos"
    _VALID_URL = r"https?://www\.picta\.cu/embed/(?:\?v=)?(?P<id>[\d]+)"

    _TESTS = [
        {
            "url": "https://www.picta.cu/embed/?v=818",
            "file": "Orishas - Everyday-orishas-everyday-2019-01-16-16-36-42-443003.webm",
            "md5": "7ffdeb0043500c4bb660c04e74e90f7a",
            "info_dict": {
                "id": "818",
                "slug_url": "orishas-everyday-2019-01-16-16-36-42-443003",
                "ext": "webm",
                "title": "Orishas - Everyday",
                "thumbnail": r"re:^https?://.*imagen/img.*\.png$",
                "upload_date": "20190116",
                "description": "Orishas - Everyday (Video Oficial)",
                "uploader": "admin",
                "timestamp": 1547656602,
            },
            "params": {"format": "4"},
        },
        {
            "url": ("https://www.picta.cu/embed/"
                    "palmiche-galeno-tercer-lugar-torneo-virtual-robotica-2020-05-21-16-15-31-431895"),
            "file": ("Palmiche Galeno tercer lugar en torneo virtual de "
                     "robótica-palmiche-galeno-tercer-lugar-torneo-virtual-robotica-2020-05-21-16-15-31-431895.mp4"),
            "md5": "6031b7a3add2eade9c5bef7ecf5d4b02",
            "info_dict": {
                "id": "3500",
                "slug_url": "palmiche-galeno-tercer-lugar-torneo-virtual-robotica-2020-05-21-16-15-31-431895",
                "ext": "mp4",
                "title": "Palmiche Galeno tercer lugar en torneo virtual de robótica",
                "thumbnail": r"re:^https?://.*imagen/img.*\.jpeg$",
                "upload_date": "20200521",
                "description": ("En esta emisión:\r\n"
                                "Iniciará en La Habana nuevo método para medir el consumo "
                                "eléctrico |  https://bit.ly/jtlecturacee\r\n"
                                "GICAcovid: nueva aplicación web para los centros de "
                                "aislamiento |  https://bit.ly/jtgicacovid\r\n"
                                "Obtuvo Palmiche tercer lugar en la primera competencia "
                                "virtual de robótica |  https://bit.ly/jtpalmichegaleno\r\n"
                                "\r\n"
                                "Síguenos en:\r\n"
                                "Facebook: http://www.facebook.com/JuventudTecnicaCuba\r\n"
                                "Twitter e Instagram: @juventudtecnica\r\n"
                                "Telegram: http://t.me/juventudtecnica"),
                "uploader": "ernestoguerra21",
                "timestamp": 1590077731,
            },
        },
    ]

    def _real_extract(self, url):
        return self.url_result(url, PictaIE.ie_key())


# noinspection PyAbstractClass
class PictaPlaylistIE(InfoExtractor):
    API_PLAYLIST_ENDPOINT = API_BASE_URL + "lista_reproduccion_canal/"
    IE_NAME = "picta:playlist"
    IE_DESC = "Picta playlist"
    _VALID_URL = r"https?://(?:www\.)?picta\.cu/(?:medias|movie|embed)/(?P<id>[\da-z-]+)" \
                 r"\?playlist=(?P<playlist_id>[\da-z-]+)$"

    _NETRC_MACHINE = "picta"

    @classmethod
    def _match_playlist_id(cls, url):
        if '_VALID_URL_RE' not in cls.__dict__:
            cls._VALID_URL_RE = re.compile(cls._VALID_URL)
        m = cls._VALID_URL_RE.match(url)
        assert m
        return m.group('playlist_id')

    def _set_auth_basic(self):
        header = {}
        username, password = self._get_login_info()
        if username is None:
            return header

        if isinstance(username, str):
            username = username.encode('latin1')

        if isinstance(password, str):
            password = password.encode('latin1')

        authstr = "Basic " + compat_str(b64encode(b":".join((username, password))).decode("utf-8"))

        header["Authorization"] = authstr
        return header

    def _extract_playlist(self, playlist, playlist_id=None, require_title=True):
        if len(playlist.get("results", [])) == 0:
            raise ExtractorError("Cannot find playlist!")

        title = (
            playlist["results"][0]["nombre"]
            if require_title
            else playlist["results"][0].get("nombre")
        )
        thumbnail = try_get(playlist, lambda x: x["results"][0].get("url_imagen"))
        entries = try_get(playlist, lambda x: x["results"][0]["publicaciones"])

        return {
            "id": try_get(playlist, lambda x: x["results"][0]["id"], compat_str) or playlist_id,
            "title": title,
            "thumbnail": thumbnail,
            "entries": entries,
        }

    def _entries(self, playlist_id):
        json_url = self.API_PLAYLIST_ENDPOINT + "?format=json&id=%s" % playlist_id
        headers = self._set_auth_basic()
        playlist = {}
        try:
            playlist = self._download_json(json_url, playlist_id, "Downloading playlist JSON", headers=headers)
            assert playlist.get("count", 0) >= 1
        except ExtractorError as e:
            if isinstance(e.cause, compat_HTTPError) and e.cause.code in (403,):
                raise self.raise_login_required(
                    msg='This playlist is only available for registered users. Check your username and password'
                )
        except AssertionError:
            raise ExtractorError("Playlist no exists!")

        info_playlist = self._extract_playlist(playlist, playlist_id)
        playlist_entries = info_playlist.get("entries")

        for video in playlist_entries:
            video_id = video.get("id")
            video_url = ROOT_BASE_URL + "medias/" + video.get("slug_url") + "?" + "playlist=" + playlist_id
            yield self.url_result(video_url, PictaIE.ie_key(), video_id)

    def _real_extract(self, url):
        playlist_id = self._match_playlist_id(url)
        entries = self._entries(playlist_id)
        return self.playlist_result(entries, playlist_id)


# noinspection PyAbstractClass
class PictaChannelPlaylistIE(PictaPlaylistIE):
    IE_NAME = "picta:channel:playlist"
    IE_DESC = "Picta channel playlist"

    _TEST_CHANNEL = {
        "url": ("https://www.picta.cu/medias/"
                "201-paradigma-devops-implementacion-tecnomatica-2020-07-05-22-44-41-299736"),
        "info_dict": {
            "id": 4441,
            "title": "D\u00eda 2: Telecomunicaciones, Redes y Ciberseguridad",
            "thumbnail": r"re:^https?://.*imagen/img.*\.jpeg$",
        },
    }


# noinspection PyAbstractClass
class PictaUserPlaylistIE(PictaPlaylistIE, PictaBaseIE):
    API_PLAYLIST_ENDPOINT = API_BASE_URL + "lista_reproduccion/"
    IE_NAME = "picta:user:playlist"
    IE_DESC = "Picta user playlist"

    _TEST_USER = {
        "url": "https://www.picta.cu/medias/fundamento-big-data-2020-08-09-19-47-15-230297?playlist=129",
        "info_dict": {
            "id": 129,
            "title": "picta-dl",
            "thumbnail": None,
        },
    }

    def _extract_playlist(self, playlist, playlist_id=None, require_title=True):
        if len(playlist["results"]) == 0:
            raise ExtractorError("Cannot find playlist!")

        title = (
            playlist["results"][0]["nombre"]
            if require_title
            else playlist.get("results")[0].get("nombre")
        )
        thumbnail = None
        entries = try_get(playlist, lambda x: x["results"][0]["publicacion"])

        # Playlist User need update slug_url video
        for entry in entries:
            video_id = entry.get("id")
            json_url = API_BASE_URL + "publicacion/?format=json&id=%s" % video_id
            video = self._download_json(json_url, video_id, "Downloading video JSON")
            info = self._extract_video(video, video_id)
            entry["slug_url"] = info.get("slug_url")

        return {
            "id": try_get(playlist, lambda x: x["results"][0]["id"], compat_str) or playlist_id,
            "title": title,
            "thumbnail": thumbnail,
            "entries": entries,
        }
