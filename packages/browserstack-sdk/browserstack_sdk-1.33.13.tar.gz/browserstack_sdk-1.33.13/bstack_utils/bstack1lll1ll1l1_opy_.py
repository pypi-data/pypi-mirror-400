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
from browserstack_sdk.bstack1lllll11l1_opy_ import bstack11ll1l11l1_opy_
from browserstack_sdk.bstack111l111111_opy_ import RobotHandler
def bstack111ll111l_opy_(framework):
    if framework.lower() == bstack11l1l_opy_ (u"ࠪࡴࡾࡺࡥࡴࡶࠪᮨ"):
        return bstack11ll1l11l1_opy_.version()
    elif framework.lower() == bstack11l1l_opy_ (u"ࠫࡷࡵࡢࡰࡶࠪᮩ"):
        return RobotHandler.version()
    elif framework.lower() == bstack11l1l_opy_ (u"ࠬࡨࡥࡩࡣࡹࡩ᮪ࠬ"):
        import behave
        return behave.__version__
    else:
        return bstack11l1l_opy_ (u"࠭ࡵ࡯࡭ࡱࡳࡼࡴ᮫ࠧ")
def bstack11ll1l111l_opy_():
    import importlib.metadata
    framework_name = []
    framework_version = []
    try:
        from selenium import webdriver
        framework_name.append(bstack11l1l_opy_ (u"ࠧࡴࡧ࡯ࡩࡳ࡯ࡵ࡮ࠩᮬ"))
        framework_version.append(importlib.metadata.version(bstack11l1l_opy_ (u"ࠣࡵࡨࡰࡪࡴࡩࡶ࡯ࠥᮭ")))
    except:
        pass
    try:
        import playwright
        framework_name.append(bstack11l1l_opy_ (u"ࠩࡳࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹ࠭ᮮ"))
        framework_version.append(importlib.metadata.version(bstack11l1l_opy_ (u"ࠥࡴࡱࡧࡹࡸࡴ࡬࡫࡭ࡺࠢᮯ")))
    except:
        pass
    return {
        bstack11l1l_opy_ (u"ࠫࡳࡧ࡭ࡦࠩ᮰"): bstack11l1l_opy_ (u"ࠬࡥࠧ᮱").join(framework_name),
        bstack11l1l_opy_ (u"࠭ࡶࡦࡴࡶ࡭ࡴࡴࠧ᮲"): bstack11l1l_opy_ (u"ࠧࡠࠩ᮳").join(framework_version)
    }