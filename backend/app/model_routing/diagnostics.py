"""Bounded diagnostic metadata. Never include provider text, inputs, messages or error context."""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

Segment = Literal[
    "claims",
    "evidence_id",
    "quote",
    "abstain",
    "summary",
    "choices",
    "message",
    "content",
    "model",
    "usage",
    "<index>",
    "<unknown>",
]
ValidationType = Literal[
    "missing",
    "extra_forbidden",
    "uuid_parsing",
    "uuid_type",
    "string_type",
    "bool_type",
    "list_type",
    "dict_type",
    "value_error",
    "literal_error",
    "other",
]


class FailureDiagnostic(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, revalidate_instances="always")
    version: Literal["local-failure-v1"] = "local-failure-v1"
    category: Literal[
        "JSON_SYNTAX",
        "OUTPUT_SCHEMA",
        "RESPONSE_SHAPE",
        "MODEL_IDENTITY",
        "TOOL_AUTHORITY",
        "MODEL_REFUSAL",
        "USAGE_INVALID",
        "OUTPUT_LIMIT",
        "TRANSPORT_STATUS",
        "TIMEOUT",
    ]
    parser_class: Literal["JSONDecodeError", "ValidationError", "NONE"] = "NONE"
    validation_paths: list[Annotated[list[Segment], Field(max_length=6)]] = Field(
        default_factory=list, max_length=4
    )
    validation_types: list[ValidationType] = Field(default_factory=list, max_length=4)
    finish_reason: Literal["stop", "length", "refusal", "unknown"] = "unknown"
    input_tokens: Annotated[int, Field(ge=0, le=131072)] | None = None
    output_tokens: Annotated[int, Field(ge=0, le=4096)] | None = None
    http_status: Annotated[int, Field(ge=400, le=599)] | None = None
    output_limit_reached: bool = False
    truncation_indicator: Literal["NOT_ESTABLISHED", "EOF_AND_LENGTH"] = "NOT_ESTABLISHED"


def diagnostic(
    category, choice=None, usage=None, error=None, incomplete_json=False, http_status=None
):
    choice = choice if isinstance(choice, dict) else {}
    finish = choice.get("finish_reason")
    finish = (
        finish if isinstance(finish, str) and finish in {"stop", "length", "refusal"} else "unknown"
    )
    counts = (
        (usage.get("prompt_tokens"), usage.get("completion_tokens"))
        if isinstance(usage, dict)
        else (None, None)
    )
    if not (
        all(type(v) is int for v in counts) and 0 <= counts[0] <= 131072 and 0 <= counts[1] <= 4096
    ):
        counts = (None, None)
    paths, types = [], []
    parser = "NONE"
    if error is not None:
        import json

        from pydantic import ValidationError

        if isinstance(error, ValidationError):
            parser = "ValidationError"
            allowed_segments = {
                "claims",
                "evidence_id",
                "quote",
                "abstain",
                "summary",
                "choices",
                "message",
                "content",
                "model",
                "usage",
            }
            allowed_types = {
                "missing",
                "extra_forbidden",
                "uuid_parsing",
                "uuid_type",
                "string_type",
                "bool_type",
                "list_type",
                "dict_type",
                "value_error",
                "literal_error",
            }
            for item in error.errors(include_input=False, include_context=False, include_url=False)[
                :4
            ]:
                paths.append(
                    [
                        "<index>" if type(v) is int else v if v in allowed_segments else "<unknown>"
                        for v in item["loc"][:6]
                    ]
                )
                types.append(item["type"] if item["type"] in allowed_types else "other")
        elif isinstance(error, json.JSONDecodeError):
            parser = "JSONDecodeError"
    return FailureDiagnostic(
        category=category,
        parser_class=parser,
        validation_paths=paths,
        validation_types=types,
        finish_reason=finish,
        input_tokens=counts[0],
        output_tokens=counts[1],
        http_status=http_status,
        output_limit_reached=finish == "length",
        truncation_indicator="EOF_AND_LENGTH"
        if incomplete_json and finish == "length"
        else "NOT_ESTABLISHED",
    )


def safe_diagnostic(value):
    """Recheck immediately before persistence, including mutable provider exceptions."""
    from pydantic import ValidationError

    try:
        return FailureDiagnostic.model_validate(value).model_dump(mode="json")
    except ValidationError:
        return None
