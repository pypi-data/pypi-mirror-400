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
import os
import threading
from bstack_utils.helper import bstack1111lll1_opy_
from bstack_utils.constants import bstack11l1l111lll_opy_, EVENTS, STAGE
from bstack_utils.bstack111lll1l1_opy_ import get_logger
logger = get_logger(__name__)
class bstack1l11llll1l_opy_:
    bstack1llll1ll111l_opy_ = None
    @classmethod
    def bstack1lll1lll1l_opy_(cls):
        if cls.on() and os.getenv(bstack11ll1_opy_ (u"ࠢࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡌ࡚ࡈ࡟ࡖࡗࡌࡈࠧ⋫")):
            logger.info(
                bstack11ll1_opy_ (u"ࠨࡘ࡬ࡷ࡮ࡺࠠࡩࡶࡷࡴࡸࡀ࠯࠰ࡣࡸࡸࡴࡳࡡࡵ࡫ࡲࡲ࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡨࡵ࡭࠰ࡤࡸ࡭ࡱࡪࡳ࠰ࡽࢀࠤࡹࡵࠠࡷ࡫ࡨࡻࠥࡨࡵࡪ࡮ࡧࠤࡷ࡫ࡰࡰࡴࡷ࠰ࠥ࡯࡮ࡴ࡫ࡪ࡬ࡹࡹࠬࠡࡣࡱࡨࠥࡳࡡ࡯ࡻࠣࡱࡴࡸࡥࠡࡦࡨࡦࡺ࡭ࡧࡪࡰࡪࠤ࡮ࡴࡦࡰࡴࡰࡥࡹ࡯࡯࡯ࠢࡤࡰࡱࠦࡡࡵࠢࡲࡲࡪࠦࡰ࡭ࡣࡦࡩࠦࡢ࡮ࠨ⋬").format(os.getenv(bstack11ll1_opy_ (u"ࠤࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡘ࡙ࡎࡊࠢ⋭"))))
    @classmethod
    def on(cls):
        if os.environ.get(bstack11ll1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡉࡘ࡚ࡈࡖࡄࡢࡎ࡜࡚ࠧ⋮"), None) is None or os.environ[bstack11ll1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡉࡗࡅࡣࡏ࡝ࡔࠨ⋯")] == bstack11ll1_opy_ (u"ࠧࡴࡵ࡭࡮ࠥ⋰"):
            return False
        return True
    @classmethod
    def bstack1lll1l1l1ll1_opy_(cls, bs_config, framework=bstack11ll1_opy_ (u"ࠨࠢ⋱")):
        bstack11l1l1ll1ll_opy_ = False
        for fw in bstack11l1l111lll_opy_:
            if fw in framework:
                bstack11l1l1ll1ll_opy_ = True
        return bstack1111lll1_opy_(bs_config.get(bstack11ll1_opy_ (u"ࠧࡵࡧࡶࡸࡔࡨࡳࡦࡴࡹࡥࡧ࡯࡬ࡪࡶࡼࠫ⋲"), bstack11l1l1ll1ll_opy_))
    @classmethod
    def bstack1lll1l11ll11_opy_(cls, framework):
        return framework in bstack11l1l111lll_opy_
    @classmethod
    def bstack1lll1ll111l1_opy_(cls, bs_config, framework):
        return cls.bstack1lll1l1l1ll1_opy_(bs_config, framework) is True and cls.bstack1lll1l11ll11_opy_(framework)
    @staticmethod
    def current_hook_uuid():
        return getattr(threading.current_thread(), bstack11ll1_opy_ (u"ࠨࡥࡸࡶࡷ࡫࡮ࡵࡡ࡫ࡳࡴࡱ࡟ࡶࡷ࡬ࡨࠬ⋳"), None)
    @staticmethod
    def bstack111ll111l1_opy_():
        if getattr(threading.current_thread(), bstack11ll1_opy_ (u"ࠩࡦࡹࡷࡸࡥ࡯ࡶࡢࡸࡪࡹࡴࡠࡷࡸ࡭ࡩ࠭⋴"), None):
            return {
                bstack11ll1_opy_ (u"ࠪࡸࡾࡶࡥࠨ⋵"): bstack11ll1_opy_ (u"ࠫࡹ࡫ࡳࡵࠩ⋶"),
                bstack11ll1_opy_ (u"ࠬࡺࡥࡴࡶࡢࡶࡺࡴ࡟ࡶࡷ࡬ࡨࠬ⋷"): getattr(threading.current_thread(), bstack11ll1_opy_ (u"࠭ࡣࡶࡴࡵࡩࡳࡺ࡟ࡵࡧࡶࡸࡤࡻࡵࡪࡦࠪ⋸"), None)
            }
        if getattr(threading.current_thread(), bstack11ll1_opy_ (u"ࠧࡤࡷࡵࡶࡪࡴࡴࡠࡪࡲࡳࡰࡥࡵࡶ࡫ࡧࠫ⋹"), None):
            return {
                bstack11ll1_opy_ (u"ࠨࡶࡼࡴࡪ࠭⋺"): bstack11ll1_opy_ (u"ࠩ࡫ࡳࡴࡱࠧ⋻"),
                bstack11ll1_opy_ (u"ࠪ࡬ࡴࡵ࡫ࡠࡴࡸࡲࡤࡻࡵࡪࡦࠪ⋼"): getattr(threading.current_thread(), bstack11ll1_opy_ (u"ࠫࡨࡻࡲࡳࡧࡱࡸࡤ࡮࡯ࡰ࡭ࡢࡹࡺ࡯ࡤࠨ⋽"), None)
            }
        return None
    @staticmethod
    def bstack1lll1l11llll_opy_(func):
        def wrap(*args, **kwargs):
            if bstack1l11llll1l_opy_.on():
                return func(*args, **kwargs)
            return
        return wrap
    @staticmethod
    def bstack111l11l1l1_opy_(test, hook_name=None):
        bstack1lll1l1l1111_opy_ = test.parent
        if hook_name in [bstack11ll1_opy_ (u"ࠬࡹࡥࡵࡷࡳࡣࡨࡲࡡࡴࡵࠪ⋾"), bstack11ll1_opy_ (u"࠭ࡴࡦࡣࡵࡨࡴࡽ࡮ࡠࡥ࡯ࡥࡸࡹࠧ⋿"), bstack11ll1_opy_ (u"ࠧࡴࡧࡷࡹࡵࡥ࡭ࡰࡦࡸࡰࡪ࠭⌀"), bstack11ll1_opy_ (u"ࠨࡶࡨࡥࡷࡪ࡯ࡸࡰࡢࡱࡴࡪࡵ࡭ࡧࠪ⌁")]:
            bstack1lll1l1l1111_opy_ = test
        scope = []
        while bstack1lll1l1l1111_opy_ is not None:
            scope.append(bstack1lll1l1l1111_opy_.name)
            bstack1lll1l1l1111_opy_ = bstack1lll1l1l1111_opy_.parent
        scope.reverse()
        return scope[2:]
    @staticmethod
    def bstack1lll1l11ll1l_opy_(hook_type):
        if hook_type == bstack11ll1_opy_ (u"ࠤࡅࡉࡋࡕࡒࡆࡡࡈࡅࡈࡎࠢ⌂"):
            return bstack11ll1_opy_ (u"ࠥࡗࡪࡺࡵࡱࠢ࡫ࡳࡴࡱࠢ⌃")
        elif hook_type == bstack11ll1_opy_ (u"ࠦࡆࡌࡔࡆࡔࡢࡉࡆࡉࡈࠣ⌄"):
            return bstack11ll1_opy_ (u"࡚ࠧࡥࡢࡴࡧࡳࡼࡴࠠࡩࡱࡲ࡯ࠧ⌅")
    @staticmethod
    def bstack1lll1l11lll1_opy_(bstack111ll111l_opy_):
        try:
            if not bstack1l11llll1l_opy_.on():
                return bstack111ll111l_opy_
            if os.environ.get(bstack11ll1_opy_ (u"ࠨࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡘࡅࡓࡗࡑࠦ⌆"), None) == bstack11ll1_opy_ (u"ࠢࡵࡴࡸࡩࠧ⌇"):
                tests = os.environ.get(bstack11ll1_opy_ (u"ࠣࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡓࡇࡕ࡙ࡓࡥࡔࡆࡕࡗࡗࠧ⌈"), None)
                if tests is None or tests == bstack11ll1_opy_ (u"ࠤࡱࡹࡱࡲࠢ⌉"):
                    return bstack111ll111l_opy_
                bstack111ll111l_opy_ = tests.split(bstack11ll1_opy_ (u"ࠪ࠰ࠬ⌊"))
                return bstack111ll111l_opy_
        except Exception as exc:
            logger.debug(bstack11ll1_opy_ (u"ࠦࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡪࡰࠣࡶࡪࡸࡵ࡯ࠢ࡫ࡥࡳࡪ࡬ࡦࡴ࠽ࠤࠧ⌋") + str(str(exc)) + bstack11ll1_opy_ (u"ࠧࠨ⌌"))
        return bstack111ll111l_opy_