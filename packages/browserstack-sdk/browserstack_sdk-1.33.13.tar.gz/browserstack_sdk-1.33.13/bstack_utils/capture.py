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
import builtins
import logging
class bstack111l1l11ll_opy_:
    def __init__(self, handler):
        self._11l1ll11111_opy_ = builtins.print
        self.handler = handler
        self._started = False
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self._11l1l1lllll_opy_ = {
            level: getattr(self.logger, level)
            for level in [bstack11l1l_opy_ (u"ࠬ࡯࡮ࡧࡱࠪᠣ"), bstack11l1l_opy_ (u"࠭ࡤࡦࡤࡸ࡫ࠬᠤ"), bstack11l1l_opy_ (u"ࠧࡸࡣࡵࡲ࡮ࡴࡧࠨᠥ"), bstack11l1l_opy_ (u"ࠨࡧࡵࡶࡴࡸࠧᠦ")]
        }
    def start(self):
        if self._started:
            return
        self._started = True
        builtins.print = self._11l1ll111l1_opy_
        self._11l1ll1111l_opy_()
    def _11l1ll111l1_opy_(self, *args, **kwargs):
        self._11l1ll11111_opy_(*args, **kwargs)
        message = bstack11l1l_opy_ (u"ࠩࠣࠫᠧ").join(map(str, args)) + bstack11l1l_opy_ (u"ࠪࡠࡳ࠭ᠨ")
        self._11l1l1llll1_opy_(bstack11l1l_opy_ (u"ࠫࡎࡔࡆࡐࠩᠩ"), message)
    def _11l1l1llll1_opy_(self, level, msg, *args, **kwargs):
        if self.handler:
            self.handler({bstack11l1l_opy_ (u"ࠬࡲࡥࡷࡧ࡯ࠫᠪ"): level, bstack11l1l_opy_ (u"࠭࡭ࡦࡵࡶࡥ࡬࡫ࠧᠫ"): msg})
    def _11l1ll1111l_opy_(self):
        for level, bstack11l1l1lll11_opy_ in self._11l1l1lllll_opy_.items():
            setattr(logging, level, self._11l1l1lll1l_opy_(level, bstack11l1l1lll11_opy_))
    def _11l1l1lll1l_opy_(self, level, bstack11l1l1lll11_opy_):
        def wrapper(msg, *args, **kwargs):
            bstack11l1l1lll11_opy_(msg, *args, **kwargs)
            self._11l1l1llll1_opy_(level.upper(), msg)
        return wrapper
    def reset(self):
        if not self._started:
            return
        self._started = False
        builtins.print = self._11l1ll11111_opy_
        for level, bstack11l1l1lll11_opy_ in self._11l1l1lllll_opy_.items():
            setattr(logging, level, bstack11l1l1lll11_opy_)