from datetime import datetime
from typing import Optional

import media_muncher.profile as PG
from media_muncher.analysers.dash import DashAnalyser
from media_muncher.analysers.hls import HlsAnalyser
from media_muncher.exceptions import MediaHandlerError
from media_muncher.handlers import ContentHandler, DASHHandler, HLSHandler


class ProfileMakerException(Exception):
    def __init__(self, messages):
        self.messages = messages

def make_transcoding_profile(
    handler: ContentHandler,
    schema_version: str,
    name: str = "",
    options: Optional[dict] = {},
    force: bool = False,
):
    analyser = None
    if isinstance(handler, HLSHandler):
        analyser = HlsAnalyser(handler)
    elif isinstance(handler, DASHHandler):
        analyser = DashAnalyser(handler)
    else:
        raise Exception("Unsupported handler type")

    # Check that the stream is readable first
    handler.document
    if handler.status > 299:
        raise MediaHandlerError(f"The stream is not readable: HTTP {handler.status}")
    
    renditions = analyser.extract_renditions()
    packaging = analyser.extract_packaging_info()

    generator = PG.ABRProfileGenerator(schema=schema_version, **options)
    profile = generator.generate(renditions, packaging, name)

    # decorate the profile
    profile["_generated_from"] = handler.original_url
    profile["_generated"] = datetime.now().isoformat()

    if not force:
        handle_errors(analyser.messages + generator.messages)

    return (profile, analyser.messages + generator.messages)


def handle_errors(messages):
    errors = [m for m in messages if m.level == "error"]
    if errors:
        raise ProfileMakerException(errors)
