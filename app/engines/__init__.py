from .document import ENGINE as DOCUMENT_ENGINE
from .speech import ENGINE as SPEECH_ENGINE

ENGINES = {
    DOCUMENT_ENGINE.engine_id: DOCUMENT_ENGINE,
    SPEECH_ENGINE.engine_id: SPEECH_ENGINE,
}

__all__ = ["ENGINES"]
