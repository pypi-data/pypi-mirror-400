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
def bstack11111l1111_opy_(package_name):
    bstack11ll1_opy_ (u"ࠢࠣࠤࡆ࡬ࡪࡩ࡫ࠡ࡫ࡩࠤࡦࠦࡰࡢࡥ࡮ࡥ࡬࡫ࠠࡪࡵࠣ࡭ࡳࡹࡴࡢ࡮࡯ࡩࡩࠦࡩ࡯ࠢࡷ࡬ࡪࠦࡥ࡯ࡸ࡬ࡶࡴࡴ࡭ࡦࡰࡷࠎࠥࠦࠠࠡࡃࡵ࡫ࡸࡀࠊࠡࠢࠣࠤࠥࠦࠠࠡࡲࡤࡧࡰࡧࡧࡦࡡࡱࡥࡲ࡫࠺ࠡࡐࡤࡱࡪࠦ࡯ࡧࠢࡷ࡬ࡪࠦࡰࡢࡥ࡮ࡥ࡬࡫ࠠࡵࡱࠣࡧ࡭࡫ࡣ࡬ࠢࠫࡩ࠳࡭࠮࠭ࠢࠪࡴࡾࡺࡥࡴࡶࡢࡴࡦࡸࡡ࡭࡮ࡨࡰࠬ࠯ࠊࠡࠢࠣࠤࡗ࡫ࡴࡶࡴࡱࡷ࠿ࠐࠠࠡࠢࠣࠤࠥࠦࠠࡣࡱࡲࡰ࠿ࠦࡔࡳࡷࡨࠤ࡮࡬ࠠࡱࡣࡦ࡯ࡦ࡭ࡥࠡ࡫ࡶࠤ࡮ࡴࡳࡵࡣ࡯ࡰࡪࡪࠬࠡࡈࡤࡰࡸ࡫ࠠࡰࡶ࡫ࡩࡷࡽࡩࡴࡧࠍࠤࠥࠦࠠࠣࠤࠥᾜ")
    try:
        import importlib
        import importlib.util
        if hasattr(importlib.util, bstack11ll1_opy_ (u"ࠨࡨ࡬ࡲࡩࡥࡳࡱࡧࡦࠫᾝ")):
            bstack11111l11lll_opy_ = importlib.util.find_spec(package_name)
            return bstack11111l11lll_opy_ is not None and bstack11111l11lll_opy_.loader is not None
        elif hasattr(importlib, bstack11ll1_opy_ (u"ࠩࡩ࡭ࡳࡪ࡟࡭ࡱࡤࡨࡪࡸࠧᾞ")):
            bstack11111l1l111_opy_ = importlib.find_loader(package_name)
            return bstack11111l1l111_opy_ is not None
    except (ImportError, ModuleNotFoundError, ValueError):
        pass
    return False