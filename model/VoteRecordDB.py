from typing import List, Tuple, OrderedDict
from threading import Lock
 
class VoteRecordDB:
    """
    MemoryDB is a model that represents an in-memory database for storing scores and locks.
    Attributes:
        score_win (OrderedDict[int, float]): An ordered dictionary mapping integer operator_id to float values representing winning scores.
        score_lose (OrderedDict[int, float]): An ordered dictionary mapping integer operator_id to float values representing losing scores.
        lock_score_win (List[Lock]): A list of Lock objects associated with winning operator_id.
        lock_score_lose (List[Lock]): A list of Lock objects associated with losing operator_id.
    """
    score_win: OrderedDict[int, float]
    score_lose: OrderedDict[int, float]
    lock_score_win: List[Lock]
    lock_score_lose: List[Lock]
    def __init__(self, score_win=None, score_lose=None, lock_score_win=None, lock_score_lose=None):
        self.score_win = score_win if score_win is not None else OrderedDict()
        self.score_lose = score_lose if score_lose is not None else OrderedDict()
        self.lock_score_win = lock_score_win if lock_score_win is not None else [Lock() for i in range(len(self.score_win))]
        self.lock_score_lose = lock_score_lose if lock_score_lose is not None else [Lock() for i in range(len(self.score_lose))]