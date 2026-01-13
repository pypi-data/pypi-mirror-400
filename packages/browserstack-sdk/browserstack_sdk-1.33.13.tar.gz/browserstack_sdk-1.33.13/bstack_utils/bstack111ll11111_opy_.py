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
import os
import threading
from bstack_utils.helper import bstack1llll1ll1_opy_
from bstack_utils.constants import bstack11l1l111l11_opy_, EVENTS, STAGE
from bstack_utils.bstack1l1lll1l11_opy_ import get_logger
logger = get_logger(__name__)
class bstack11llll111_opy_:
    bstack1llll1ll1111_opy_ = None
    @classmethod
    def bstack111llll1ll_opy_(cls):
        if cls.on() and os.getenv(bstack11l1l_opy_ (u"ࠨࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡕࡖࡋࡇࠦ⋪")):
            logger.info(
                bstack11l1l_opy_ (u"ࠧࡗ࡫ࡶ࡭ࡹࠦࡨࡵࡶࡳࡷ࠿࠵࠯ࡢࡷࡷࡳࡲࡧࡴࡪࡱࡱ࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡧࡴࡳ࠯ࡣࡷ࡬ࡰࡩࡹ࠯ࡼࡿࠣࡸࡴࠦࡶࡪࡧࡺࠤࡧࡻࡩ࡭ࡦࠣࡶࡪࡶ࡯ࡳࡶ࠯ࠤ࡮ࡴࡳࡪࡩ࡫ࡸࡸ࠲ࠠࡢࡰࡧࠤࡲࡧ࡮ࡺࠢࡰࡳࡷ࡫ࠠࡥࡧࡥࡹ࡬࡭ࡩ࡯ࡩࠣ࡭ࡳ࡬࡯ࡳ࡯ࡤࡸ࡮ࡵ࡮ࠡࡣ࡯ࡰࠥࡧࡴࠡࡱࡱࡩࠥࡶ࡬ࡢࡥࡨࠥࡡࡴࠧ⋫").format(os.getenv(bstack11l1l_opy_ (u"ࠣࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡍ࡛ࡂࡠࡗࡘࡍࡉࠨ⋬"))))
    @classmethod
    def on(cls):
        if os.environ.get(bstack11l1l_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡍ࡛࡙࠭⋭"), None) is None or os.environ[bstack11l1l_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡉࡘ࡚ࡈࡖࡄࡢࡎ࡜࡚ࠧ⋮")] == bstack11l1l_opy_ (u"ࠦࡳࡻ࡬࡭ࠤ⋯"):
            return False
        return True
    @classmethod
    def bstack1lll1l1l1l1l_opy_(cls, bs_config, framework=bstack11l1l_opy_ (u"ࠧࠨ⋰")):
        bstack11l1l1ll11l_opy_ = False
        for fw in bstack11l1l111l11_opy_:
            if fw in framework:
                bstack11l1l1ll11l_opy_ = True
        return bstack1llll1ll1_opy_(bs_config.get(bstack11l1l_opy_ (u"࠭ࡴࡦࡵࡷࡓࡧࡹࡥࡳࡸࡤࡦ࡮ࡲࡩࡵࡻࠪ⋱"), bstack11l1l1ll11l_opy_))
    @classmethod
    def bstack1lll1l11ll11_opy_(cls, framework):
        return framework in bstack11l1l111l11_opy_
    @classmethod
    def bstack1lll1ll1l1ll_opy_(cls, bs_config, framework):
        return cls.bstack1lll1l1l1l1l_opy_(bs_config, framework) is True and cls.bstack1lll1l11ll11_opy_(framework)
    @staticmethod
    def current_hook_uuid():
        return getattr(threading.current_thread(), bstack11l1l_opy_ (u"ࠧࡤࡷࡵࡶࡪࡴࡴࡠࡪࡲࡳࡰࡥࡵࡶ࡫ࡧࠫ⋲"), None)
    @staticmethod
    def bstack111ll111ll_opy_():
        if getattr(threading.current_thread(), bstack11l1l_opy_ (u"ࠨࡥࡸࡶࡷ࡫࡮ࡵࡡࡷࡩࡸࡺ࡟ࡶࡷ࡬ࡨࠬ⋳"), None):
            return {
                bstack11l1l_opy_ (u"ࠩࡷࡽࡵ࡫ࠧ⋴"): bstack11l1l_opy_ (u"ࠪࡸࡪࡹࡴࠨ⋵"),
                bstack11l1l_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡵࡹࡳࡥࡵࡶ࡫ࡧࠫ⋶"): getattr(threading.current_thread(), bstack11l1l_opy_ (u"ࠬࡩࡵࡳࡴࡨࡲࡹࡥࡴࡦࡵࡷࡣࡺࡻࡩࡥࠩ⋷"), None)
            }
        if getattr(threading.current_thread(), bstack11l1l_opy_ (u"࠭ࡣࡶࡴࡵࡩࡳࡺ࡟ࡩࡱࡲ࡯ࡤࡻࡵࡪࡦࠪ⋸"), None):
            return {
                bstack11l1l_opy_ (u"ࠧࡵࡻࡳࡩࠬ⋹"): bstack11l1l_opy_ (u"ࠨࡪࡲࡳࡰ࠭⋺"),
                bstack11l1l_opy_ (u"ࠩ࡫ࡳࡴࡱ࡟ࡳࡷࡱࡣࡺࡻࡩࡥࠩ⋻"): getattr(threading.current_thread(), bstack11l1l_opy_ (u"ࠪࡧࡺࡸࡲࡦࡰࡷࡣ࡭ࡵ࡯࡬ࡡࡸࡹ࡮ࡪࠧ⋼"), None)
            }
        return None
    @staticmethod
    def bstack1lll1l1l1111_opy_(func):
        def wrap(*args, **kwargs):
            if bstack11llll111_opy_.on():
                return func(*args, **kwargs)
            return
        return wrap
    @staticmethod
    def bstack1111l1ll11_opy_(test, hook_name=None):
        bstack1lll1l11lll1_opy_ = test.parent
        if hook_name in [bstack11l1l_opy_ (u"ࠫࡸ࡫ࡴࡶࡲࡢࡧࡱࡧࡳࡴࠩ⋽"), bstack11l1l_opy_ (u"ࠬࡺࡥࡢࡴࡧࡳࡼࡴ࡟ࡤ࡮ࡤࡷࡸ࠭⋾"), bstack11l1l_opy_ (u"࠭ࡳࡦࡶࡸࡴࡤࡳ࡯ࡥࡷ࡯ࡩࠬ⋿"), bstack11l1l_opy_ (u"ࠧࡵࡧࡤࡶࡩࡵࡷ࡯ࡡࡰࡳࡩࡻ࡬ࡦࠩ⌀")]:
            bstack1lll1l11lll1_opy_ = test
        scope = []
        while bstack1lll1l11lll1_opy_ is not None:
            scope.append(bstack1lll1l11lll1_opy_.name)
            bstack1lll1l11lll1_opy_ = bstack1lll1l11lll1_opy_.parent
        scope.reverse()
        return scope[2:]
    @staticmethod
    def bstack1lll1l11ll1l_opy_(hook_type):
        if hook_type == bstack11l1l_opy_ (u"ࠣࡄࡈࡊࡔࡘࡅࡠࡇࡄࡇࡍࠨ⌁"):
            return bstack11l1l_opy_ (u"ࠤࡖࡩࡹࡻࡰࠡࡪࡲࡳࡰࠨ⌂")
        elif hook_type == bstack11l1l_opy_ (u"ࠥࡅࡋ࡚ࡅࡓࡡࡈࡅࡈࡎࠢ⌃"):
            return bstack11l1l_opy_ (u"࡙ࠦ࡫ࡡࡳࡦࡲࡻࡳࠦࡨࡰࡱ࡮ࠦ⌄")
    @staticmethod
    def bstack1lll1l11llll_opy_(bstack1l11l1ll_opy_):
        try:
            if not bstack11llll111_opy_.on():
                return bstack1l11l1ll_opy_
            if os.environ.get(bstack11l1l_opy_ (u"ࠧࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡗࡋࡒࡖࡐࠥ⌅"), None) == bstack11l1l_opy_ (u"ࠨࡴࡳࡷࡨࠦ⌆"):
                tests = os.environ.get(bstack11l1l_opy_ (u"ࠢࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡒࡆࡔࡘࡒࡤ࡚ࡅࡔࡖࡖࠦ⌇"), None)
                if tests is None or tests == bstack11l1l_opy_ (u"ࠣࡰࡸࡰࡱࠨ⌈"):
                    return bstack1l11l1ll_opy_
                bstack1l11l1ll_opy_ = tests.split(bstack11l1l_opy_ (u"ࠩ࠯ࠫ⌉"))
                return bstack1l11l1ll_opy_
        except Exception as exc:
            logger.debug(bstack11l1l_opy_ (u"ࠥࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡩ࡯ࠢࡵࡩࡷࡻ࡮ࠡࡪࡤࡲࡩࡲࡥࡳ࠼ࠣࠦ⌊") + str(str(exc)) + bstack11l1l_opy_ (u"ࠦࠧ⌋"))
        return bstack1l11l1ll_opy_