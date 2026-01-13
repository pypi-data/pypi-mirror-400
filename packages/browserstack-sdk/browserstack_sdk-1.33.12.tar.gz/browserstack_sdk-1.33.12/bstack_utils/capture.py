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
import builtins
import logging
class bstack111l1l1lll_opy_:
    def __init__(self, handler):
        self._11l1l1lllll_opy_ = builtins.print
        self.handler = handler
        self._started = False
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self._11l1ll11111_opy_ = {
            level: getattr(self.logger, level)
            for level in [bstack11ll1_opy_ (u"࠭ࡩ࡯ࡨࡲࠫᠤ"), bstack11ll1_opy_ (u"ࠧࡥࡧࡥࡹ࡬࠭ᠥ"), bstack11ll1_opy_ (u"ࠨࡹࡤࡶࡳ࡯࡮ࡨࠩᠦ"), bstack11ll1_opy_ (u"ࠩࡨࡶࡷࡵࡲࠨᠧ")]
        }
    def start(self):
        if self._started:
            return
        self._started = True
        builtins.print = self._11l1l1llll1_opy_
        self._11l1ll1111l_opy_()
    def _11l1l1llll1_opy_(self, *args, **kwargs):
        self._11l1l1lllll_opy_(*args, **kwargs)
        message = bstack11ll1_opy_ (u"ࠪࠤࠬᠨ").join(map(str, args)) + bstack11ll1_opy_ (u"ࠫࡡࡴࠧᠩ")
        self._11l1ll111l1_opy_(bstack11ll1_opy_ (u"ࠬࡏࡎࡇࡑࠪᠪ"), message)
    def _11l1ll111l1_opy_(self, level, msg, *args, **kwargs):
        if self.handler:
            self.handler({bstack11ll1_opy_ (u"࠭࡬ࡦࡸࡨࡰࠬᠫ"): level, bstack11ll1_opy_ (u"ࠧ࡮ࡧࡶࡷࡦ࡭ࡥࠨᠬ"): msg})
    def _11l1ll1111l_opy_(self):
        for level, bstack11l1l1lll1l_opy_ in self._11l1ll11111_opy_.items():
            setattr(logging, level, self._11l1l1lll11_opy_(level, bstack11l1l1lll1l_opy_))
    def _11l1l1lll11_opy_(self, level, bstack11l1l1lll1l_opy_):
        def wrapper(msg, *args, **kwargs):
            bstack11l1l1lll1l_opy_(msg, *args, **kwargs)
            self._11l1ll111l1_opy_(level.upper(), msg)
        return wrapper
    def reset(self):
        if not self._started:
            return
        self._started = False
        builtins.print = self._11l1l1lllll_opy_
        for level, bstack11l1l1lll1l_opy_ in self._11l1ll11111_opy_.items():
            setattr(logging, level, bstack11l1l1lll1l_opy_)