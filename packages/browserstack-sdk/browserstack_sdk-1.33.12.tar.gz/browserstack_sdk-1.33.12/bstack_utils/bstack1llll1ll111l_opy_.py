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
import logging
logger = logging.getLogger(__name__)
bstack1llll1l1llll_opy_ = 1000
bstack1llll1l1ll1l_opy_ = 2
class bstack1llll1ll1l11_opy_:
    def __init__(self, handler, bstack1llll1ll1111_opy_=bstack1llll1l1llll_opy_, bstack1llll1l1lll1_opy_=bstack1llll1l1ll1l_opy_):
        self.queue = []
        self.handler = handler
        self.bstack1llll1ll1111_opy_ = bstack1llll1ll1111_opy_
        self.bstack1llll1l1lll1_opy_ = bstack1llll1l1lll1_opy_
        self.lock = threading.Lock()
        self.timer = None
        self.bstack1l1llll1ll1_opy_ = None
    def start(self):
        if not (self.timer and self.timer.is_alive()):
            self.bstack1llll1ll1ll1_opy_()
    def bstack1llll1ll1ll1_opy_(self):
        self.bstack1l1llll1ll1_opy_ = threading.Event()
        def bstack1llll1ll1lll_opy_():
            self.bstack1l1llll1ll1_opy_.wait(self.bstack1llll1l1lll1_opy_)
            if not self.bstack1l1llll1ll1_opy_.is_set():
                self.bstack1llll1ll11ll_opy_()
        self.timer = threading.Thread(target=bstack1llll1ll1lll_opy_, daemon=True)
        self.timer.start()
    def bstack1llll1ll11l1_opy_(self):
        try:
            if self.bstack1l1llll1ll1_opy_ and not self.bstack1l1llll1ll1_opy_.is_set():
                self.bstack1l1llll1ll1_opy_.set()
            if self.timer and self.timer.is_alive() and self.timer != threading.current_thread():
                self.timer.join()
        except Exception as e:
            logger.debug(bstack11ll1_opy_ (u"࡛࠭ࡴࡶࡲࡴࡤࡺࡩ࡮ࡧࡵࡡࠥࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮࠻ࠢࠪₗ") + (str(e) or bstack11ll1_opy_ (u"ࠢࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣࡧࡴࡻ࡬ࡥࠢࡱࡳࡹࠦࡢࡦࠢࡦࡳࡳࡼࡥࡳࡶࡨࡨࠥࡺ࡯ࠡࡵࡷࡶ࡮ࡴࡧࠣₘ")))
        finally:
            self.timer = None
    def bstack1llll1ll1l1l_opy_(self):
        if self.timer:
            self.bstack1llll1ll11l1_opy_()
        self.bstack1llll1ll1ll1_opy_()
    def add(self, event):
        with self.lock:
            self.queue.append(event)
            if len(self.queue) >= self.bstack1llll1ll1111_opy_:
                threading.Thread(target=self.bstack1llll1ll11ll_opy_).start()
    def bstack1llll1ll11ll_opy_(self, source = bstack11ll1_opy_ (u"ࠨࠩₙ")):
        with self.lock:
            if not self.queue:
                self.bstack1llll1ll1l1l_opy_()
                return
            data = self.queue[:self.bstack1llll1ll1111_opy_]
            del self.queue[:self.bstack1llll1ll1111_opy_]
        self.handler(data)
        if source != bstack11ll1_opy_ (u"ࠩࡶ࡬ࡺࡺࡤࡰࡹࡱࠫₚ"):
            self.bstack1llll1ll1l1l_opy_()
    def shutdown(self):
        self.bstack1llll1ll11l1_opy_()
        while self.queue:
            self.bstack1llll1ll11ll_opy_(source=bstack11ll1_opy_ (u"ࠪࡷ࡭ࡻࡴࡥࡱࡺࡲࠬₛ"))