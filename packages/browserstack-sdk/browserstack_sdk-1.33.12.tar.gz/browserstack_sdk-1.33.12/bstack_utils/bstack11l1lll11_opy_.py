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
from browserstack_sdk.bstack1l1l1ll1_opy_ import bstack1lll1l11ll_opy_
from browserstack_sdk.bstack1111ll1ll1_opy_ import RobotHandler
def bstack11ll11l11l_opy_(framework):
    if framework.lower() == bstack11ll1_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࠫᮩ"):
        return bstack1lll1l11ll_opy_.version()
    elif framework.lower() == bstack11ll1_opy_ (u"ࠬࡸ࡯ࡣࡱࡷ᮪ࠫ"):
        return RobotHandler.version()
    elif framework.lower() == bstack11ll1_opy_ (u"࠭ࡢࡦࡪࡤࡺࡪ᮫࠭"):
        import behave
        return behave.__version__
    else:
        return bstack11ll1_opy_ (u"ࠧࡶࡰ࡮ࡲࡴࡽ࡮ࠨᮬ")
def bstack11l11111l1_opy_():
    import importlib.metadata
    framework_name = []
    framework_version = []
    try:
        from selenium import webdriver
        framework_name.append(bstack11ll1_opy_ (u"ࠨࡵࡨࡰࡪࡴࡩࡶ࡯ࠪᮭ"))
        framework_version.append(importlib.metadata.version(bstack11ll1_opy_ (u"ࠤࡶࡩࡱ࡫࡮ࡪࡷࡰࠦᮮ")))
    except:
        pass
    try:
        import playwright
        framework_name.append(bstack11ll1_opy_ (u"ࠪࡴࡱࡧࡹࡸࡴ࡬࡫࡭ࡺࠧᮯ"))
        framework_version.append(importlib.metadata.version(bstack11ll1_opy_ (u"ࠦࡵࡲࡡࡺࡹࡵ࡭࡬࡮ࡴࠣ᮰")))
    except:
        pass
    return {
        bstack11ll1_opy_ (u"ࠬࡴࡡ࡮ࡧࠪ᮱"): bstack11ll1_opy_ (u"࠭࡟ࠨ᮲").join(framework_name),
        bstack11ll1_opy_ (u"ࠧࡷࡧࡵࡷ࡮ࡵ࡮ࠨ᮳"): bstack11ll1_opy_ (u"ࠨࡡࠪ᮴").join(framework_version)
    }