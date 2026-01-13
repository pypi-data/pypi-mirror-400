from vibelab.engine.judge import JudgeExecutor


def test_parse_judgement_response_fenced_json() -> None:
    ex = JudgeExecutor()
    response = """
Here is my judgement:

```json
{"notes": "Looks good overall", "quality": 3}
```
"""
    notes, quality = ex._parse_judgement_response(response)
    assert notes == "Looks good overall"
    assert quality == 3


def test_parse_judgement_response_plain_json_with_extra_braces() -> None:
    ex = JudgeExecutor()
    response = """
Some preface text {not json}
{"notes": "Solid", "quality": "4"}
Some trailing text {also not json}
"""
    notes, quality = ex._parse_judgement_response(response)
    assert notes == "Solid"
    assert quality == 4


def test_parse_judgement_response_fallback_quality_from_text() -> None:
    ex = JudgeExecutor()
    response = "Notes: ok. Quality: 2"
    notes, quality = ex._parse_judgement_response(response)
    assert notes is not None
    assert quality == 2


def test_parse_judgement_response_label_quality() -> None:
    ex = JudgeExecutor()
    response = """```json
{"notes": "meh", "quality": "good"}
```"""
    notes, quality = ex._parse_judgement_response(response)
    assert notes == "meh"
    assert quality == 3


def test_parse_judgement_response_ignores_out_of_range() -> None:
    ex = JudgeExecutor()
    response = """```json
{"notes": "n/a", "quality": 7}
```"""
    notes, quality = ex._parse_judgement_response(response)
    assert notes == "n/a"
    assert quality is None
