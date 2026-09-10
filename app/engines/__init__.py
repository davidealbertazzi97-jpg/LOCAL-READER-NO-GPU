from .document import ENGINE as DOCUMENT_ENGINE
from .reflow import ENGINE as REFLOW_ENGINE
from .speech import ENGINE as SPEECH_ENGINE
from .text import ENGINE as TEXT_ENGINE

ENGINES = {
    DOCUMENT_ENGINE.engine_id: DOCUMENT_ENGINE,
    TEXT_ENGINE.engine_id: TEXT_ENGINE,
    SPEECH_ENGINE.engine_id: SPEECH_ENGINE,
    REFLOW_ENGINE.engine_id: REFLOW_ENGINE,
}

__all__ = ["ENGINES"]
