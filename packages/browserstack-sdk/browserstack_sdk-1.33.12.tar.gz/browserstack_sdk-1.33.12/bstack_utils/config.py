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
conf = {
    bstack11ll1_opy_ (u"ࠨࡣࡳࡴࡤࡧࡵࡵࡱࡰࡥࡹ࡫ࠧᠭ"): False,
    bstack11ll1_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬ࡡࡶࡩࡸࡹࡩࡰࡰࠪᠮ"): True,
    bstack11ll1_opy_ (u"ࠪࡷࡰ࡯ࡰࡠࡵࡨࡷࡸ࡯࡯࡯ࡡࡶࡸࡦࡺࡵࡴࠩᠯ"): False
}
class Config(object):
    instance = None
    def __init__(self):
        self._11l1l1ll1l1_opy_ = conf
    @classmethod
    def bstack1l1l1111_opy_(cls):
        if cls.instance:
            return cls.instance
        return Config()
    def get_property(self, property_name, bstack11l1l1ll1ll_opy_=None):
        return self._11l1l1ll1l1_opy_.get(property_name, bstack11l1l1ll1ll_opy_)
    def bstack11l1l11l_opy_(self, property_name, bstack11l1l1ll11l_opy_):
        self._11l1l1ll1l1_opy_[property_name] = bstack11l1l1ll11l_opy_
    def bstack1ll11111l_opy_(self, val):
        self._11l1l1ll1l1_opy_[bstack11ll1_opy_ (u"ࠫࡸࡱࡩࡱࡡࡶࡩࡸࡹࡩࡰࡰࡢࡷࡹࡧࡴࡶࡵࠪᠰ")] = bool(val)
    def bstack1llllllll1l_opy_(self):
        return self._11l1l1ll1l1_opy_.get(bstack11ll1_opy_ (u"ࠬࡹ࡫ࡪࡲࡢࡷࡪࡹࡳࡪࡱࡱࡣࡸࡺࡡࡵࡷࡶࠫᠱ"), False)