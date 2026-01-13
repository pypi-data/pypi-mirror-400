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
def bstack11111l1111_opy_(package_name):
    bstack11l1l_opy_ (u"ࠨࠢࠣࡅ࡫ࡩࡨࡱࠠࡪࡨࠣࡥࠥࡶࡡࡤ࡭ࡤ࡫ࡪࠦࡩࡴࠢ࡬ࡲࡸࡺࡡ࡭࡮ࡨࡨࠥ࡯࡮ࠡࡶ࡫ࡩࠥ࡫࡮ࡷ࡫ࡵࡳࡳࡳࡥ࡯ࡶࠍࠤࠥࠦࠠࡂࡴࡪࡷ࠿ࠐࠠࠡࠢࠣࠤࠥࠦࠠࡱࡣࡦ࡯ࡦ࡭ࡥࡠࡰࡤࡱࡪࡀࠠࡏࡣࡰࡩࠥࡵࡦࠡࡶ࡫ࡩࠥࡶࡡࡤ࡭ࡤ࡫ࡪࠦࡴࡰࠢࡦ࡬ࡪࡩ࡫ࠡࠪࡨ࠲࡬࠴ࠬࠡࠩࡳࡽࡹ࡫ࡳࡵࡡࡳࡥࡷࡧ࡬࡭ࡧ࡯ࠫ࠮ࠐࠠࠡࠢࠣࡖࡪࡺࡵࡳࡰࡶ࠾ࠏࠦࠠࠡࠢࠣࠤࠥࠦࡢࡰࡱ࡯࠾࡚ࠥࡲࡶࡧࠣ࡭࡫ࠦࡰࡢࡥ࡮ࡥ࡬࡫ࠠࡪࡵࠣ࡭ࡳࡹࡴࡢ࡮࡯ࡩࡩ࠲ࠠࡇࡣ࡯ࡷࡪࠦ࡯ࡵࡪࡨࡶࡼ࡯ࡳࡦࠌࠣࠤࠥࠦࠢࠣࠤᾛ")
    try:
        import importlib
        import importlib.util
        if hasattr(importlib.util, bstack11l1l_opy_ (u"ࠧࡧ࡫ࡱࡨࡤࡹࡰࡦࡥࠪᾜ")):
            bstack11111l1l111_opy_ = importlib.util.find_spec(package_name)
            return bstack11111l1l111_opy_ is not None and bstack11111l1l111_opy_.loader is not None
        elif hasattr(importlib, bstack11l1l_opy_ (u"ࠨࡨ࡬ࡲࡩࡥ࡬ࡰࡣࡧࡩࡷ࠭ᾝ")):
            bstack11111l11lll_opy_ = importlib.find_loader(package_name)
            return bstack11111l11lll_opy_ is not None
    except (ImportError, ModuleNotFoundError, ValueError):
        pass
    return False