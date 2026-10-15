from abc import ABC, abstractmethod
from uuid import uuid4

from app.evaluation.contracts import JudgeRequest, JudgeResponse


class Judge(ABC):
    @abstractmethod
    def review(self, request: JudgeRequest) -> JudgeResponse: ...


class FixtureJudge(Judge):
    def review(self, request):
        # Content is inert data; no tools, policy authority, rubric override or model client.
        return JudgeResponse(
            score=1 if request.content.strip() else 0,
            reason="Fixture nonempty-content rubric only; not coherence quality.",
            trace_id=uuid4(),
        )


REAL_JUDGE_STATUS = "REAL LLM JUDGE NOT CONFIGURED"
