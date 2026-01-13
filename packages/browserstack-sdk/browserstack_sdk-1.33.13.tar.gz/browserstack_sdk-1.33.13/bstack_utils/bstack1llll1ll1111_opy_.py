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
import logging
logger = logging.getLogger(__name__)
bstack1llll1l1llll_opy_ = 1000
bstack1llll1l1lll1_opy_ = 2
class bstack1llll1ll11ll_opy_:
    def __init__(self, handler, bstack1llll1l1ll1l_opy_=bstack1llll1l1llll_opy_, bstack1llll1ll1lll_opy_=bstack1llll1l1lll1_opy_):
        self.queue = []
        self.handler = handler
        self.bstack1llll1l1ll1l_opy_ = bstack1llll1l1ll1l_opy_
        self.bstack1llll1ll1lll_opy_ = bstack1llll1ll1lll_opy_
        self.lock = threading.Lock()
        self.timer = None
        self.bstack1lllll11l11_opy_ = None
    def start(self):
        if not (self.timer and self.timer.is_alive()):
            self.bstack1llll1ll1l1l_opy_()
    def bstack1llll1ll1l1l_opy_(self):
        self.bstack1lllll11l11_opy_ = threading.Event()
        def bstack1llll1ll1l11_opy_():
            self.bstack1lllll11l11_opy_.wait(self.bstack1llll1ll1lll_opy_)
            if not self.bstack1lllll11l11_opy_.is_set():
                self.bstack1llll1ll11l1_opy_()
        self.timer = threading.Thread(target=bstack1llll1ll1l11_opy_, daemon=True)
        self.timer.start()
    def bstack1llll1ll111l_opy_(self):
        try:
            if self.bstack1lllll11l11_opy_ and not self.bstack1lllll11l11_opy_.is_set():
                self.bstack1lllll11l11_opy_.set()
            if self.timer and self.timer.is_alive() and self.timer != threading.current_thread():
                self.timer.join()
        except Exception as e:
            logger.debug(bstack11l1l_opy_ (u"ࠬࡡࡳࡵࡱࡳࡣࡹ࡯࡭ࡦࡴࡠࠤࡊࡾࡣࡦࡲࡷ࡭ࡴࡴ࠺ࠡࠩₖ") + (str(e) or bstack11l1l_opy_ (u"ࠨࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢࡦࡳࡺࡲࡤࠡࡰࡲࡸࠥࡨࡥࠡࡥࡲࡲࡻ࡫ࡲࡵࡧࡧࠤࡹࡵࠠࡴࡶࡵ࡭ࡳ࡭ࠢₗ")))
        finally:
            self.timer = None
    def bstack1llll1ll1ll1_opy_(self):
        if self.timer:
            self.bstack1llll1ll111l_opy_()
        self.bstack1llll1ll1l1l_opy_()
    def add(self, event):
        with self.lock:
            self.queue.append(event)
            if len(self.queue) >= self.bstack1llll1l1ll1l_opy_:
                threading.Thread(target=self.bstack1llll1ll11l1_opy_).start()
    def bstack1llll1ll11l1_opy_(self, source = bstack11l1l_opy_ (u"ࠧࠨₘ")):
        with self.lock:
            if not self.queue:
                self.bstack1llll1ll1ll1_opy_()
                return
            data = self.queue[:self.bstack1llll1l1ll1l_opy_]
            del self.queue[:self.bstack1llll1l1ll1l_opy_]
        self.handler(data)
        if source != bstack11l1l_opy_ (u"ࠨࡵ࡫ࡹࡹࡪ࡯ࡸࡰࠪₙ"):
            self.bstack1llll1ll1ll1_opy_()
    def shutdown(self):
        self.bstack1llll1ll111l_opy_()
        while self.queue:
            self.bstack1llll1ll11l1_opy_(source=bstack11l1l_opy_ (u"ࠩࡶ࡬ࡺࡺࡤࡰࡹࡱࠫₚ"))