from typing import Literal

from pydantic import BaseModel

MessageAnalysis = Literal["positive", "negative", "unknown"]


class AnalyzeMessageResponse(BaseModel):
    message_analysis: MessageAnalysis
