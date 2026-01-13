# coding: UTF-8
import sys
bstack1lll1l_opy_ = sys.version_info [0] == 2
bstack1ll1lll_opy_ = 2048
bstack11111_opy_ = 7
def bstack11l1l_opy_ (bstack1lllll1_opy_):
    global bstackl_opy_
    bstack11l1_opy_ = ord (bstack1lllll1_opy_ [-1])
    bstack11lllll_opy_ = bstack1lllll1_opy_ [:-1]
    bstack1ll11l_opy_ = bstack11l1_opy_ % len (bstack11lllll_opy_)
    bstack1111ll1_opy_ = bstack11lllll_opy_ [:bstack1ll11l_opy_] + bstack11lllll_opy_ [bstack1ll11l_opy_:]
    if bstack1lll1l_opy_:
        bstack111_opy_ = unicode () .join ([unichr (ord (char) - bstack1ll1lll_opy_ - (bstack11l11l1_opy_ + bstack11l1_opy_) % bstack11111_opy_) for bstack11l11l1_opy_, char in enumerate (bstack1111ll1_opy_)])
    else:
        bstack111_opy_ = str () .join ([chr (ord (char) - bstack1ll1lll_opy_ - (bstack11l11l1_opy_ + bstack11l1_opy_) % bstack11111_opy_) for bstack11l11l1_opy_, char in enumerate (bstack1111ll1_opy_)])
    return eval (bstack111_opy_)
import os
import threading
import os
from typing import Dict, Any
from dataclasses import dataclass
from collections import defaultdict
from datetime import timedelta
@dataclass
class bstack1llll1lll11_opy_:
    id: str
    hash: str
    thread_id: int
    process_id: int
    type: str
class bstack1llll11111l_opy_:
    bstack11ll1lll1l1_opy_ = bstack11l1l_opy_ (u"ࠥࡦࡪࡴࡣࡩ࡯ࡤࡶࡰࠨᙶ")
    context: bstack1llll1lll11_opy_
    data: Dict[str, Any]
    platform_index: int
    def __init__(self, context: bstack1llll1lll11_opy_):
        self.context = context
        self.data = dict({bstack1llll11111l_opy_.bstack11ll1lll1l1_opy_: defaultdict(lambda: timedelta(microseconds=0))})
        self.platform_index = int(os.environ.get(bstack11l1l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡔࡑࡇࡔࡇࡑࡕࡑࡤࡏࡎࡅࡇ࡛ࠫᙷ"), bstack11l1l_opy_ (u"ࠬ࠶ࠧᙸ")))
    def ref(self) -> str:
        return str(self.context.id)
    def bstack1llll1l1l1l_opy_(self, target: object):
        return bstack1llll11111l_opy_.create_context(target) == self.context
    def bstack1l1ll11lll1_opy_(self, context: bstack1llll1lll11_opy_):
        return context and context.thread_id == self.context.thread_id and context.process_id == self.context.process_id
    def bstack11lll111_opy_(self, key: str, value: timedelta):
        self.data[bstack1llll11111l_opy_.bstack11ll1lll1l1_opy_][key] += value
    def bstack1ll1lll111l_opy_(self) -> dict:
        return self.data[bstack1llll11111l_opy_.bstack11ll1lll1l1_opy_]
    @staticmethod
    def create_context(
        target: object,
        thread_id=threading.get_ident(),
        process_id=os.getpid(),
    ):
        return bstack1llll1lll11_opy_(
            id=hash(target),
            hash=hash(target),
            thread_id=thread_id,
            process_id=process_id,
            type=target,
        )