from typing import TypedDict, List, Literal, Dict


MentorLevel = Literal["Beginner", "Intermediate", "Advanced"]


class MentorAdvice(TypedDict):
    level: MentorLevel
    summary: str
    next_challenge: Dict[str, str]
    why: str
    insight: str
    after_that: List[str]
