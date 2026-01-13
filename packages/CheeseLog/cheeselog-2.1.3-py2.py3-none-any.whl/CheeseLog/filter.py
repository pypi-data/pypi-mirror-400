from typing import TypedDict, Optional
from collections.abc import Iterable

class Filter(TypedDict):
    weight: Optional[int]
    ''' 权重阈值，低于该权重的日志将被过滤 '''
    message_keys: Optional[Iterable[str]]
    ''' 该类型的日志将被过滤 '''
