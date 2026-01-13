# coding: UTF-8
import sys
bstack1111ll_opy_ = sys.version_info [0] == 2
bstack1l11l11_opy_ = 2048
bstack1ll1111_opy_ = 7
def bstack11ll1_opy_ (bstack1l1ll_opy_):
    global bstack1l11ll1_opy_
    bstack1_opy_ = ord (bstack1l1ll_opy_ [-1])
    bstack11ll11l_opy_ = bstack1l1ll_opy_ [:-1]
    bstack111l11l_opy_ = bstack1_opy_ % len (bstack11ll11l_opy_)
    bstack1l1l1l_opy_ = bstack11ll11l_opy_ [:bstack111l11l_opy_] + bstack11ll11l_opy_ [bstack111l11l_opy_:]
    if bstack1111ll_opy_:
        bstack1lllll_opy_ = unicode () .join ([unichr (ord (char) - bstack1l11l11_opy_ - (bstack11111l_opy_ + bstack1_opy_) % bstack1ll1111_opy_) for bstack11111l_opy_, char in enumerate (bstack1l1l1l_opy_)])
    else:
        bstack1lllll_opy_ = str () .join ([chr (ord (char) - bstack1l11l11_opy_ - (bstack11111l_opy_ + bstack1_opy_) % bstack1ll1111_opy_) for bstack11111l_opy_, char in enumerate (bstack1l1l1l_opy_)])
    return eval (bstack1lllll_opy_)
import threading
from collections import deque
from bstack_utils.constants import *
class bstack1lll1l1ll1_opy_:
    def __init__(self):
        self._1lllll1lll11_opy_ = deque()
        self._1lllll1ll11l_opy_ = {}
        self._1lllll1ll1ll_opy_ = False
        self._lock = threading.RLock()
    def bstack1llllll111ll_opy_(self, test_name, bstack1lllll1ll111_opy_):
        with self._lock:
            bstack1llllll111l1_opy_ = self._1lllll1ll11l_opy_.get(test_name, {})
            return bstack1llllll111l1_opy_.get(bstack1lllll1ll111_opy_, 0)
    def bstack1lllll1llll1_opy_(self, test_name, bstack1lllll1ll111_opy_):
        with self._lock:
            bstack1lllll1lll1l_opy_ = self.bstack1llllll111ll_opy_(test_name, bstack1lllll1ll111_opy_)
            self.bstack1lllll1l1lll_opy_(test_name, bstack1lllll1ll111_opy_)
            return bstack1lllll1lll1l_opy_
    def bstack1lllll1l1lll_opy_(self, test_name, bstack1lllll1ll111_opy_):
        with self._lock:
            if test_name not in self._1lllll1ll11l_opy_:
                self._1lllll1ll11l_opy_[test_name] = {}
            bstack1llllll111l1_opy_ = self._1lllll1ll11l_opy_[test_name]
            bstack1lllll1lll1l_opy_ = bstack1llllll111l1_opy_.get(bstack1lllll1ll111_opy_, 0)
            bstack1llllll111l1_opy_[bstack1lllll1ll111_opy_] = bstack1lllll1lll1l_opy_ + 1
    def bstack1111l1ll1_opy_(self, bstack1llllll1111l_opy_, bstack1lllll1ll1l1_opy_):
        bstack1llllll11111_opy_ = self.bstack1lllll1llll1_opy_(bstack1llllll1111l_opy_, bstack1lllll1ll1l1_opy_)
        event_name = bstack11l1l1l1111_opy_[bstack1lllll1ll1l1_opy_]
        bstack11lllll11l1_opy_ = bstack11ll1_opy_ (u"ࠣࡽࢀ࠱ࢀࢃ࠭ࡼࡿࠥ•").format(bstack1llllll1111l_opy_, event_name, bstack1llllll11111_opy_)
        with self._lock:
            self._1lllll1lll11_opy_.append(bstack11lllll11l1_opy_)
    def bstack111l11111_opy_(self):
        with self._lock:
            return len(self._1lllll1lll11_opy_) == 0
    def bstack1ll11l1l11_opy_(self):
        with self._lock:
            if self._1lllll1lll11_opy_:
                bstack1lllll1lllll_opy_ = self._1lllll1lll11_opy_.popleft()
                return bstack1lllll1lllll_opy_
            return None
    def capturing(self):
        with self._lock:
            return self._1lllll1ll1ll_opy_
    def bstack1ll1l11ll_opy_(self):
        with self._lock:
            self._1lllll1ll1ll_opy_ = True
    def bstack1ll1ll1111_opy_(self):
        with self._lock:
            self._1lllll1ll1ll_opy_ = False