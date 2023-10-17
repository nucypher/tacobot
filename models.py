from enum import Enum


class RitualState(Enum):
    NON_INITIATED = 0
    AWAITING_TRANSCRIPTS = 1
    AWAITING_AGGREGATIONS = 2
    TIMEOUT = 3
    INVALID = 4
    FINALIZED = 5
