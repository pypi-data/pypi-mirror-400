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
import threading
from collections import deque
from bstack_utils.constants import *
class bstack1ll1lll1_opy_:
    def __init__(self):
        self._1lllll1lll1l_opy_ = deque()
        self._1lllll1ll111_opy_ = {}
        self._1lllll1ll11l_opy_ = False
        self._lock = threading.RLock()
    def bstack1lllll1lllll_opy_(self, test_name, bstack1lllll1ll1l1_opy_):
        with self._lock:
            bstack1lllll1ll1ll_opy_ = self._1lllll1ll111_opy_.get(test_name, {})
            return bstack1lllll1ll1ll_opy_.get(bstack1lllll1ll1l1_opy_, 0)
    def bstack1llllll111ll_opy_(self, test_name, bstack1lllll1ll1l1_opy_):
        with self._lock:
            bstack1lllll1lll11_opy_ = self.bstack1lllll1lllll_opy_(test_name, bstack1lllll1ll1l1_opy_)
            self.bstack1llllll11111_opy_(test_name, bstack1lllll1ll1l1_opy_)
            return bstack1lllll1lll11_opy_
    def bstack1llllll11111_opy_(self, test_name, bstack1lllll1ll1l1_opy_):
        with self._lock:
            if test_name not in self._1lllll1ll111_opy_:
                self._1lllll1ll111_opy_[test_name] = {}
            bstack1lllll1ll1ll_opy_ = self._1lllll1ll111_opy_[test_name]
            bstack1lllll1lll11_opy_ = bstack1lllll1ll1ll_opy_.get(bstack1lllll1ll1l1_opy_, 0)
            bstack1lllll1ll1ll_opy_[bstack1lllll1ll1l1_opy_] = bstack1lllll1lll11_opy_ + 1
    def bstack1l111lll11_opy_(self, bstack1llllll1111l_opy_, bstack1llllll111l1_opy_):
        bstack1lllll1llll1_opy_ = self.bstack1llllll111ll_opy_(bstack1llllll1111l_opy_, bstack1llllll111l1_opy_)
        event_name = bstack11l11ll1ll1_opy_[bstack1llllll111l1_opy_]
        bstack1l11llll1l1_opy_ = bstack11l1l_opy_ (u"ࠢࡼࡿ࠰ࡿࢂ࠳ࡻࡾࠤ‡").format(bstack1llllll1111l_opy_, event_name, bstack1lllll1llll1_opy_)
        with self._lock:
            self._1lllll1lll1l_opy_.append(bstack1l11llll1l1_opy_)
    def bstack1l1l11l1l1_opy_(self):
        with self._lock:
            return len(self._1lllll1lll1l_opy_) == 0
    def bstack11l1ll11l_opy_(self):
        with self._lock:
            if self._1lllll1lll1l_opy_:
                bstack1lllll1l1lll_opy_ = self._1lllll1lll1l_opy_.popleft()
                return bstack1lllll1l1lll_opy_
            return None
    def capturing(self):
        with self._lock:
            return self._1lllll1ll11l_opy_
    def bstack11lll1ll_opy_(self):
        with self._lock:
            self._1lllll1ll11l_opy_ = True
    def bstack1111l1111_opy_(self):
        with self._lock:
            self._1lllll1ll11l_opy_ = False