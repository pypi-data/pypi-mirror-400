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
import tempfile
import math
from bstack_utils import bstack1l1lll1l11_opy_
from bstack_utils.constants import bstack1lllll1l1l_opy_, bstack11l11lll1l1_opy_
from bstack_utils.helper import bstack111ll11l111_opy_, get_host_info
from bstack_utils.bstack11l1ll11lll_opy_ import bstack11l1ll1l1ll_opy_
import json
import re
import sys
bstack1111l1ll1ll_opy_ = bstack11l1l_opy_ (u"ࠨࡲࡦࡶࡵࡽ࡙࡫ࡳࡵࡵࡒࡲࡋࡧࡩ࡭ࡷࡵࡩࠧἝ")
bstack1111l11l1l1_opy_ = bstack11l1l_opy_ (u"ࠢࡢࡤࡲࡶࡹࡈࡵࡪ࡮ࡧࡓࡳࡌࡡࡪ࡮ࡸࡶࡪࠨ἞")
bstack11111ll1111_opy_ = bstack11l1l_opy_ (u"ࠣࡴࡸࡲࡕࡸࡥࡷ࡫ࡲࡹࡸࡲࡹࡇࡣ࡬ࡰࡪࡪࡆࡪࡴࡶࡸࠧ἟")
bstack1111l1l111l_opy_ = bstack11l1l_opy_ (u"ࠤࡵࡩࡷࡻ࡮ࡑࡴࡨࡺ࡮ࡵࡵࡴ࡮ࡼࡊࡦ࡯࡬ࡦࡦࠥἠ")
bstack1111l111ll1_opy_ = bstack11l1l_opy_ (u"ࠥࡷࡰ࡯ࡰࡇ࡮ࡤ࡯ࡾࡧ࡮ࡥࡈࡤ࡭ࡱ࡫ࡤࠣἡ")
bstack1111l1ll11l_opy_ = bstack11l1l_opy_ (u"ࠦࡷࡻ࡮ࡔ࡯ࡤࡶࡹ࡙ࡥ࡭ࡧࡦࡸ࡮ࡵ࡮ࠣἢ")
bstack1111l1l1l11_opy_ = {
    bstack1111l1ll1ll_opy_,
    bstack1111l11l1l1_opy_,
    bstack11111ll1111_opy_,
    bstack1111l1l111l_opy_,
    bstack1111l111ll1_opy_,
    bstack1111l1ll11l_opy_
}
bstack11111l1llll_opy_ = {bstack11l1l_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸࠬἣ")}
logger = bstack1l1lll1l11_opy_.get_logger(__name__, bstack1lllll1l1l_opy_)
class bstack11111lll1l1_opy_:
    def __init__(self):
        self.enabled = False
        self.name = None
    def enable(self, name):
        self.enabled = True
        self.name = name
    def disable(self):
        self.enabled = False
        self.name = None
    def bstack11111lll1ll_opy_(self):
        return self.enabled
    def get_name(self):
        return self.name
class bstack11llllll1l_opy_:
    _1ll11ll1lll_opy_ = None
    def __init__(self, config):
        self.bstack1111l1l11ll_opy_ = False
        self.bstack1111l11lll1_opy_ = False
        self.bstack1111ll11111_opy_ = False
        self.bstack11111l1ll1l_opy_ = False
        self.bstack1111l11ll11_opy_ = None
        self.bstack11111ll11l1_opy_ = bstack11111lll1l1_opy_()
        self.bstack1111l1ll1l1_opy_ = None
        opts = config.get(bstack11l1l_opy_ (u"࠭ࡴࡦࡵࡷࡓࡷࡩࡨࡦࡵࡷࡶࡦࡺࡩࡰࡰࡒࡴࡹ࡯࡯࡯ࡵࠪἤ"), {})
        self.bstack1111l1l1111_opy_ = config.get(bstack11l1l_opy_ (u"ࠧࡴ࡯ࡤࡶࡹ࡙ࡥ࡭ࡧࡦࡸ࡮ࡵ࡮ࡇࡧࡤࡸࡺࡸࡥࡃࡴࡤࡲࡨ࡮ࡥࡴࡇࡑ࡚ࠬἥ"), bstack11l1l_opy_ (u"ࠣࠤἦ"))
        self.bstack1111l11l111_opy_ = config.get(bstack11l1l_opy_ (u"ࠩࡶࡱࡦࡸࡴࡔࡧ࡯ࡩࡨࡺࡩࡰࡰࡉࡩࡦࡺࡵࡳࡧࡅࡶࡦࡴࡣࡩࡧࡶࡇࡑࡏࠧἧ"), bstack11l1l_opy_ (u"ࠥࠦἨ"))
        bstack1111l1111l1_opy_ = opts.get(bstack1111l1ll11l_opy_, {})
        bstack1111l1l11l1_opy_ = None
        if bstack11l1l_opy_ (u"ࠫࡸࡵࡵࡳࡥࡨࠫἩ") in bstack1111l1111l1_opy_:
            bstack11111lllll1_opy_ = bstack1111l1111l1_opy_[bstack11l1l_opy_ (u"ࠬࡹ࡯ࡶࡴࡦࡩࠬἪ")]
            if bstack11111lllll1_opy_ is None or (isinstance(bstack11111lllll1_opy_, str) and bstack11111lllll1_opy_.strip() == bstack11l1l_opy_ (u"࠭ࠧἫ")) or (isinstance(bstack11111lllll1_opy_, list) and len(bstack11111lllll1_opy_) == 0):
                bstack1111l1l11l1_opy_ = []
            elif isinstance(bstack11111lllll1_opy_, list):
                bstack1111l1l11l1_opy_ = bstack11111lllll1_opy_
            elif isinstance(bstack11111lllll1_opy_, str) and bstack11111lllll1_opy_.strip():
                bstack1111l1l11l1_opy_ = bstack11111lllll1_opy_
            else:
                logger.warning(bstack11l1l_opy_ (u"ࠢࡊࡰࡹࡥࡱ࡯ࡤࠡࡵࡲࡹࡷࡩࡥࠡࡸࡤࡰࡺ࡫ࠠࡪࡰࠣࡧࡴࡴࡦࡪࡩ࠽ࠤࢀࢃ࠮ࠡࡆࡨࡪࡦࡻ࡬ࡵ࡫ࡱ࡫ࠥࡺ࡯ࠡࡧࡰࡴࡹࡿࠠ࡭࡫ࡶࡸ࠳ࠨἬ").format(bstack11111lllll1_opy_))
                bstack1111l1l11l1_opy_ = []
        self.__11111llllll_opy_(
            bstack1111l1111l1_opy_.get(bstack11l1l_opy_ (u"ࠨࡧࡱࡥࡧࡲࡥࡥࠩἭ"), False),
            bstack1111l1111l1_opy_.get(bstack11l1l_opy_ (u"ࠩࡰࡳࡩ࡫ࠧἮ"), bstack11l1l_opy_ (u"ࠪࡶࡪࡲࡥࡷࡣࡱࡸࡋ࡯ࡲࡴࡶࠪἯ")),
            bstack1111l1l11l1_opy_
        )
        self.__1111l11llll_opy_(opts.get(bstack11111ll1111_opy_, False))
        self.__11111lll111_opy_(opts.get(bstack1111l1l111l_opy_, False))
        self.__1111l1l1l1l_opy_(opts.get(bstack1111l111ll1_opy_, False))
    @classmethod
    def bstack11l1l11ll1_opy_(cls, config=None):
        if cls._1ll11ll1lll_opy_ is None and config is not None:
            cls._1ll11ll1lll_opy_ = bstack11llllll1l_opy_(config)
        return cls._1ll11ll1lll_opy_
    @staticmethod
    def bstack1ll111l111_opy_(config: dict) -> bool:
        bstack1111l1lllll_opy_ = config.get(bstack11l1l_opy_ (u"ࠫࡹ࡫ࡳࡵࡑࡵࡧ࡭࡫ࡳࡵࡴࡤࡸ࡮ࡵ࡮ࡐࡲࡷ࡭ࡴࡴࡳࠨἰ"), {}).get(bstack1111l1ll1ll_opy_, {})
        return bstack1111l1lllll_opy_.get(bstack11l1l_opy_ (u"ࠬ࡫࡮ࡢࡤ࡯ࡩࡩ࠭ἱ"), False)
    @staticmethod
    def bstack1111lllll_opy_(config: dict) -> int:
        bstack1111l1lllll_opy_ = config.get(bstack11l1l_opy_ (u"࠭ࡴࡦࡵࡷࡓࡷࡩࡨࡦࡵࡷࡶࡦࡺࡩࡰࡰࡒࡴࡹ࡯࡯࡯ࡵࠪἲ"), {}).get(bstack1111l1ll1ll_opy_, {})
        retries = 0
        if bstack11llllll1l_opy_.bstack1ll111l111_opy_(config):
            retries = bstack1111l1lllll_opy_.get(bstack11l1l_opy_ (u"ࠧ࡮ࡣࡻࡖࡪࡺࡲࡪࡧࡶࠫἳ"), 1)
        return retries
    @staticmethod
    def bstack111lll1l11_opy_(config: dict) -> dict:
        bstack11111l1l11l_opy_ = config.get(bstack11l1l_opy_ (u"ࠨࡶࡨࡷࡹࡕࡲࡤࡪࡨࡷࡹࡸࡡࡵ࡫ࡲࡲࡔࡶࡴࡪࡱࡱࡷࠬἴ"), {})
        return {
            key: value for key, value in bstack11111l1l11l_opy_.items() if key in bstack1111l1l1l11_opy_
        }
    @staticmethod
    def bstack11111lll11l_opy_():
        bstack11l1l_opy_ (u"ࠤࠥࠦࠏࠦࠠࠡࠢࠣࠤࠥࠦࡃࡩࡧࡦ࡯ࠥ࡯ࡦࠡࡶ࡫ࡩࠥࡧࡢࡰࡴࡷࠤࡧࡻࡩ࡭ࡦࠣࡪ࡮ࡲࡥࠡࡧࡻ࡭ࡸࡺࡳ࠯ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠦࠧࠨἵ")
        return os.path.exists(os.path.join(tempfile.gettempdir(), bstack11l1l_opy_ (u"ࠥࡥࡧࡵࡲࡵࡡࡥࡹ࡮ࡲࡤࡠࡽࢀࠦἶ").format(os.getenv(bstack11l1l_opy_ (u"ࠦࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡉࡗࡅࡣ࡚࡛ࡉࡅࠤἷ")))))
    @staticmethod
    def bstack1111l111l11_opy_(test_name: str):
        bstack11l1l_opy_ (u"ࠧࠨࠢࠋࠢࠣࠤࠥࠦࠠࠡࠢࡆ࡬ࡪࡩ࡫ࠡ࡫ࡩࠤࡹ࡮ࡥࠡࡣࡥࡳࡷࡺࠠࡣࡷ࡬ࡰࡩࠦࡦࡪ࡮ࡨࠤࡪࡾࡩࡴࡶࡶ࠲ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠢࠣࠤἸ")
        bstack11111l1l1ll_opy_ = os.path.join(tempfile.gettempdir(), bstack11l1l_opy_ (u"ࠨࡦࡢ࡫࡯ࡩࡩࡥࡴࡦࡵࡷࡷࡤࢁࡽ࠯ࡶࡻࡸࠧἹ").format(os.getenv(bstack11l1l_opy_ (u"ࠢࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡌ࡚ࡈ࡟ࡖࡗࡌࡈࠧἺ"))))
        with open(bstack11111l1l1ll_opy_, bstack11l1l_opy_ (u"ࠨࡣࠪἻ")) as file:
            file.write(bstack11l1l_opy_ (u"ࠤࡾࢁࡡࡴࠢἼ").format(test_name))
    @staticmethod
    def bstack11111l1l1l1_opy_(framework: str) -> bool:
       return framework.lower() in bstack11111l1llll_opy_
    @staticmethod
    def bstack11l11l1l11l_opy_(config: dict) -> bool:
        bstack11111ll11ll_opy_ = config.get(bstack11l1l_opy_ (u"ࠪࡸࡪࡹࡴࡐࡴࡦ࡬ࡪࡹࡴࡳࡣࡷ࡭ࡴࡴࡏࡱࡶ࡬ࡳࡳࡹࠧἽ"), {}).get(bstack1111l11l1l1_opy_, {})
        return bstack11111ll11ll_opy_.get(bstack11l1l_opy_ (u"ࠫࡪࡴࡡࡣ࡮ࡨࡨࠬἾ"), False)
    @staticmethod
    def bstack11l11l11111_opy_(config: dict, bstack11l11l111ll_opy_: int = 0) -> int:
        bstack11l1l_opy_ (u"ࠧࠨࠢࠋࠢࠣࠤࠥࠦࠠࠡࠢࡊࡩࡹࠦࡴࡩࡧࠣࡪࡦ࡯࡬ࡶࡴࡨࠤࡹ࡮ࡲࡦࡵ࡫ࡳࡱࡪࠬࠡࡹ࡫࡭ࡨ࡮ࠠࡤࡣࡱࠤࡧ࡫ࠠࡢࡰࠣࡥࡧࡹ࡯࡭ࡷࡷࡩࠥࡴࡵ࡮ࡤࡨࡶࠥࡵࡲࠡࡣࠣࡴࡪࡸࡣࡦࡰࡷࡥ࡬࡫࠮ࠋࠢࠣࠤࠥࠦࠠࠡࠢࡄࡶ࡬ࡹ࠺ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࡣࡰࡰࡩ࡭࡬ࠦࠨࡥ࡫ࡦࡸ࠮ࡀࠠࡕࡪࡨࠤࡨࡵ࡮ࡧ࡫ࡪࡹࡷࡧࡴࡪࡱࡱࠤࡩ࡯ࡣࡵ࡫ࡲࡲࡦࡸࡹ࠯ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࡵࡱࡷࡥࡱࡥࡴࡦࡵࡷࡷࠥ࠮ࡩ࡯ࡶࠬ࠾࡚ࠥࡨࡦࠢࡷࡳࡹࡧ࡬ࠡࡰࡸࡱࡧ࡫ࡲࠡࡱࡩࠤࡹ࡫ࡳࡵࡵࠣࠬࡷ࡫ࡱࡶ࡫ࡵࡩࡩࠦࡦࡰࡴࠣࡴࡪࡸࡣࡦࡰࡷࡥ࡬࡫࠭ࡣࡣࡶࡩࡩࠦࡴࡩࡴࡨࡷ࡭ࡵ࡬ࡥࡵࠬ࠲ࠏࠦࠠࠡࠢࠣࠤࠥࠦࡒࡦࡶࡸࡶࡳࡹ࠺ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࡩ࡯ࡶ࠽ࠤ࡙࡮ࡥࠡࡨࡤ࡭ࡱࡻࡲࡦࠢࡷ࡬ࡷ࡫ࡳࡩࡱ࡯ࡨ࠳ࠐࠠࠡࠢࠣࠤࠥࠦࠠࠣࠤࠥἿ")
        bstack11111ll11ll_opy_ = config.get(bstack11l1l_opy_ (u"࠭ࡴࡦࡵࡷࡓࡷࡩࡨࡦࡵࡷࡶࡦࡺࡩࡰࡰࡒࡴࡹ࡯࡯࡯ࡵࠪὀ"), {}).get(bstack11l1l_opy_ (u"ࠧࡢࡤࡲࡶࡹࡈࡵࡪ࡮ࡧࡓࡳࡌࡡࡪ࡮ࡸࡶࡪ࠭ὁ"), {})
        bstack1111l11l11l_opy_ = 0
        bstack1111l1llll1_opy_ = 0
        if bstack11llllll1l_opy_.bstack11l11l1l11l_opy_(config):
            bstack1111l1llll1_opy_ = bstack11111ll11ll_opy_.get(bstack11l1l_opy_ (u"ࠨ࡯ࡤࡼࡋࡧࡩ࡭ࡷࡵࡩࡸ࠭ὂ"), 5)
            if isinstance(bstack1111l1llll1_opy_, str) and bstack1111l1llll1_opy_.endswith(bstack11l1l_opy_ (u"ࠩࠨࠫὃ")):
                try:
                    percentage = int(bstack1111l1llll1_opy_.strip(bstack11l1l_opy_ (u"ࠪࠩࠬὄ")))
                    if bstack11l11l111ll_opy_ > 0:
                        bstack1111l11l11l_opy_ = math.ceil((percentage * bstack11l11l111ll_opy_) / 100)
                    else:
                        raise ValueError(bstack11l1l_opy_ (u"࡙ࠦࡵࡴࡢ࡮ࠣࡸࡪࡹࡴࡴࠢࡰࡹࡸࡺࠠࡣࡧࠣࡴࡷࡵࡶࡪࡦࡨࡨࠥ࡬࡯ࡳࠢࡳࡩࡷࡩࡥ࡯ࡶࡤ࡫ࡪ࠳ࡢࡢࡵࡨࡨࠥࡺࡨࡳࡧࡶ࡬ࡴࡲࡤࡴ࠰ࠥὅ"))
                except ValueError as e:
                    raise ValueError(bstack11l1l_opy_ (u"ࠧࡏ࡮ࡷࡣ࡯࡭ࡩࠦࡰࡦࡴࡦࡩࡳࡺࡡࡨࡧࠣࡺࡦࡲࡵࡦࠢࡩࡳࡷࠦ࡭ࡢࡺࡉࡥ࡮ࡲࡵࡳࡧࡶ࠾ࠥࢁࡽࠣ὆").format(bstack1111l1llll1_opy_)) from e
            else:
                bstack1111l11l11l_opy_ = int(bstack1111l1llll1_opy_)
        logger.info(bstack11l1l_opy_ (u"ࠨࡍࡢࡺࠣࡪࡦ࡯࡬ࡶࡴࡨࡷࠥࡺࡨࡳࡧࡶ࡬ࡴࡲࡤࠡࡵࡨࡸࠥࡺ࡯࠻ࠢࡾࢁࠥ࠮ࡦࡳࡱࡰࠤࡨࡵ࡮ࡧ࡫ࡪ࠾ࠥࢁࡽࠪࠤ὇").format(bstack1111l11l11l_opy_, bstack1111l1llll1_opy_))
        return bstack1111l11l11l_opy_
    def bstack11111l1lll1_opy_(self):
        return self.bstack11111l1ll1l_opy_
    def bstack1111l1lll1l_opy_(self):
        return self.bstack1111l11ll11_opy_
    def bstack11111ll1l11_opy_(self):
        return self.bstack1111l1ll1l1_opy_
    def __11111llllll_opy_(self, enabled, mode, source=None):
        try:
            self.bstack11111l1ll1l_opy_ = bool(enabled)
            if mode not in [bstack11l1l_opy_ (u"ࠧࡳࡧ࡯ࡩࡻࡧ࡮ࡵࡈ࡬ࡶࡸࡺࠧὈ"), bstack11l1l_opy_ (u"ࠨࡴࡨࡰࡪࡼࡡ࡯ࡶࡒࡲࡱࡿࠧὉ")]:
                logger.warning(bstack11l1l_opy_ (u"ࠤࡌࡲࡻࡧ࡬ࡪࡦࠣࡷࡲࡧࡲࡵࠢࡶࡩࡱ࡫ࡣࡵ࡫ࡲࡲࠥࡳ࡯ࡥࡧࠣࠫࢀࢃࠧࠡࡲࡵࡳࡻ࡯ࡤࡦࡦ࠱ࠤࡉ࡫ࡦࡢࡷ࡯ࡸ࡮ࡴࡧࠡࡶࡲࠤࠬࡸࡥ࡭ࡧࡹࡥࡳࡺࡆࡪࡴࡶࡸࠬ࠴ࠢὊ").format(mode))
                mode = bstack11l1l_opy_ (u"ࠪࡶࡪࡲࡥࡷࡣࡱࡸࡋ࡯ࡲࡴࡶࠪὋ")
            self.bstack1111l11ll11_opy_ = mode
            self.bstack1111l1ll1l1_opy_ = []
            if source is None:
                self.bstack1111l1ll1l1_opy_ = None
            elif isinstance(source, list):
                self.bstack1111l1ll1l1_opy_ = source
            elif isinstance(source, str) and source.endswith(bstack11l1l_opy_ (u"ࠫ࠳ࡰࡳࡰࡰࠪὌ")):
                self.bstack1111l1ll1l1_opy_ = self._11111llll1l_opy_(source)
            self.__1111l111111_opy_()
        except Exception as e:
            logger.error(bstack11l1l_opy_ (u"ࠧࡌࡡࡪ࡮ࡨࡨࠥࡺ࡯ࠡࡵࡨࡸࠥࡹ࡭ࡢࡴࡷࠤࡸ࡫࡬ࡦࡥࡷ࡭ࡴࡴࠠࡤࡱࡱࡪ࡮࡭ࡵࡳࡣࡷ࡭ࡴࡴࠠ࠮ࠢࡨࡲࡦࡨ࡬ࡦࡦ࠽ࠤࢀࢃࠬࠡ࡯ࡲࡨࡪࡀࠠࡼࡿ࠯ࠤࡸࡵࡵࡳࡥࡨ࠾ࠥࢁࡽ࠯ࠢࡈࡶࡷࡵࡲ࠻ࠢࡾࢁࠧὍ").format(enabled, mode, source, e))
    def bstack11111ll1lll_opy_(self):
        return self.bstack1111l1l11ll_opy_
    def __1111l11llll_opy_(self, value):
        self.bstack1111l1l11ll_opy_ = bool(value)
        self.__1111l111111_opy_()
    def bstack1111l11111l_opy_(self):
        return self.bstack1111l11lll1_opy_
    def __11111lll111_opy_(self, value):
        self.bstack1111l11lll1_opy_ = bool(value)
        self.__1111l111111_opy_()
    def bstack1111l11l1ll_opy_(self):
        return self.bstack1111ll11111_opy_
    def __1111l1l1l1l_opy_(self, value):
        self.bstack1111ll11111_opy_ = bool(value)
        self.__1111l111111_opy_()
    def __1111l111111_opy_(self):
        if self.bstack11111l1ll1l_opy_:
            self.bstack1111l1l11ll_opy_ = False
            self.bstack1111l11lll1_opy_ = False
            self.bstack1111ll11111_opy_ = False
            self.bstack11111ll11l1_opy_.enable(bstack1111l1ll11l_opy_)
        elif self.bstack1111l1l11ll_opy_:
            self.bstack1111l11lll1_opy_ = False
            self.bstack1111ll11111_opy_ = False
            self.bstack11111l1ll1l_opy_ = False
            self.bstack11111ll11l1_opy_.enable(bstack11111ll1111_opy_)
        elif self.bstack1111l11lll1_opy_:
            self.bstack1111l1l11ll_opy_ = False
            self.bstack1111ll11111_opy_ = False
            self.bstack11111l1ll1l_opy_ = False
            self.bstack11111ll11l1_opy_.enable(bstack1111l1l111l_opy_)
        elif self.bstack1111ll11111_opy_:
            self.bstack1111l1l11ll_opy_ = False
            self.bstack1111l11lll1_opy_ = False
            self.bstack11111l1ll1l_opy_ = False
            self.bstack11111ll11l1_opy_.enable(bstack1111l111ll1_opy_)
        else:
            self.bstack11111ll11l1_opy_.disable()
    def bstack1llll1l111_opy_(self):
        return self.bstack11111ll11l1_opy_.bstack11111lll1ll_opy_()
    def bstack111l1l1l_opy_(self):
        if self.bstack11111ll11l1_opy_.bstack11111lll1ll_opy_():
            return self.bstack11111ll11l1_opy_.get_name()
        return None
    def _11111llll1l_opy_(self, bstack1111l1l1lll_opy_):
        bstack11l1l_opy_ (u"ࠨࠢࠣࠌࠣࠤࠥࠦࠠࠡࠢࠣࡔࡦࡸࡳࡦࠢࡍࡗࡔࡔࠠࡴࡱࡸࡶࡨ࡫ࠠࡤࡱࡱࡪ࡮࡭ࡵࡳࡣࡷ࡭ࡴࡴࠠࡧ࡫࡯ࡩࠥࡧ࡮ࡥࠢࡩࡳࡷࡳࡡࡵࠢ࡬ࡸࠥ࡬࡯ࡳࠢࡶࡱࡦࡸࡴࠡࡵࡨࡰࡪࡩࡴࡪࡱࡱ࠲ࠏࠦࠠࠡࠢࠣࠤࠥࠦࡁࡳࡩࡶ࠾ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࡷࡴࡻࡲࡤࡧࡢࡪ࡮ࡲࡥࡠࡲࡤࡸ࡭ࠦࠨࡴࡶࡵ࠭࠿ࠦࡐࡢࡶ࡫ࠤࡹࡵࠠࡵࡪࡨࠤࡏ࡙ࡏࡏࠢࡦࡳࡳ࡬ࡩࡨࡷࡵࡥࡹ࡯࡯࡯ࠢࡩ࡭ࡱ࡫ࠊࠡࠢࠣࠤࠥࠦࠠࠡࡔࡨࡸࡺࡸ࡮ࡴ࠼ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡ࡮࡬ࡷࡹࡀࠠࡇࡱࡵࡱࡦࡺࡴࡦࡦࠣࡰ࡮ࡹࡴࠡࡱࡩࠤࡷ࡫ࡰࡰࡵ࡬ࡸࡴࡸࡹࠡࡥࡲࡲ࡫࡯ࡧࡶࡴࡤࡸ࡮ࡵ࡮ࡴࠌࠣࠤࠥࠦࠠࠡࠢࠣࠦࠧࠨ὎")
        if not os.path.isfile(bstack1111l1l1lll_opy_):
            logger.error(bstack11l1l_opy_ (u"ࠢࡔࡱࡸࡶࡨ࡫ࠠࡧ࡫࡯ࡩࠥ࠭ࡻࡾࠩࠣࡨࡴ࡫ࡳࠡࡰࡲࡸࠥ࡫ࡸࡪࡵࡷ࠲ࠧ὏").format(bstack1111l1l1lll_opy_))
            return []
        data = None
        try:
            with open(bstack1111l1l1lll_opy_, bstack11l1l_opy_ (u"ࠣࡴࠥὐ")) as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            logger.error(bstack11l1l_opy_ (u"ࠤࡈࡶࡷࡵࡲࠡࡲࡤࡶࡸ࡯࡮ࡨࠢࡍࡗࡔࡔࠠࡧࡴࡲࡱࠥࡹ࡯ࡶࡴࡦࡩࠥ࡬ࡩ࡭ࡧࠣࠫࢀࢃࠧ࠻ࠢࡾࢁࠧὑ").format(bstack1111l1l1lll_opy_, e))
            return []
        _1111l111lll_opy_ = None
        _1111l111l1l_opy_ = None
        def _1111ll1111l_opy_():
            bstack1111l11ll1l_opy_ = {}
            bstack1111l1l1ll1_opy_ = {}
            try:
                if self.bstack1111l1l1111_opy_.startswith(bstack11l1l_opy_ (u"ࠪࡿࠬὒ")) and self.bstack1111l1l1111_opy_.endswith(bstack11l1l_opy_ (u"ࠫࢂ࠭ὓ")):
                    bstack1111l11ll1l_opy_ = json.loads(self.bstack1111l1l1111_opy_)
                else:
                    bstack1111l11ll1l_opy_ = dict(item.split(bstack11l1l_opy_ (u"ࠬࡀࠧὔ")) for item in self.bstack1111l1l1111_opy_.split(bstack11l1l_opy_ (u"࠭ࠬࠨὕ")) if bstack11l1l_opy_ (u"ࠧ࠻ࠩὖ") in item) if self.bstack1111l1l1111_opy_ else {}
                if self.bstack1111l11l111_opy_.startswith(bstack11l1l_opy_ (u"ࠨࡽࠪὗ")) and self.bstack1111l11l111_opy_.endswith(bstack11l1l_opy_ (u"ࠩࢀࠫ὘")):
                    bstack1111l1l1ll1_opy_ = json.loads(self.bstack1111l11l111_opy_)
                else:
                    bstack1111l1l1ll1_opy_ = dict(item.split(bstack11l1l_opy_ (u"ࠪ࠾ࠬὙ")) for item in self.bstack1111l11l111_opy_.split(bstack11l1l_opy_ (u"ࠫ࠱࠭὚")) if bstack11l1l_opy_ (u"ࠬࡀࠧὛ") in item) if self.bstack1111l11l111_opy_ else {}
            except json.JSONDecodeError as e:
                logger.error(bstack11l1l_opy_ (u"ࠨࡅࡳࡴࡲࡶࠥࡶࡡࡳࡵ࡬ࡲ࡬ࠦࡦࡦࡣࡷࡹࡷ࡫ࠠࡣࡴࡤࡲࡨ࡮ࠠ࡮ࡣࡳࡴ࡮ࡴࡧࡴ࠼ࠣࡿࢂࠨ὜").format(e))
            logger.debug(bstack11l1l_opy_ (u"ࠢࡇࡧࡤࡸࡺࡸࡥࠡࡤࡵࡥࡳࡩࡨࠡ࡯ࡤࡴࡵ࡯࡮ࡨࡵࠣࡪࡷࡵ࡭ࠡࡧࡱࡺ࠿ࠦࡻࡾ࠮ࠣࡇࡑࡏ࠺ࠡࡽࢀࠦὝ").format(bstack1111l11ll1l_opy_, bstack1111l1l1ll1_opy_))
            return bstack1111l11ll1l_opy_, bstack1111l1l1ll1_opy_
        if _1111l111lll_opy_ is None or _1111l111l1l_opy_ is None:
            _1111l111lll_opy_, _1111l111l1l_opy_ = _1111ll1111l_opy_()
        def bstack1111l1ll111_opy_(name, bstack11111ll1l1l_opy_):
            if name in _1111l111l1l_opy_:
                return _1111l111l1l_opy_[name]
            if name in _1111l111lll_opy_:
                return _1111l111lll_opy_[name]
            if bstack11111ll1l1l_opy_.get(bstack11l1l_opy_ (u"ࠨࡨࡨࡥࡹࡻࡲࡦࡄࡵࡥࡳࡩࡨࠨ὞")):
                return bstack11111ll1l1l_opy_[bstack11l1l_opy_ (u"ࠩࡩࡩࡦࡺࡵࡳࡧࡅࡶࡦࡴࡣࡩࠩὟ")]
            return None
        if isinstance(data, dict):
            bstack11111l1ll11_opy_ = []
            bstack11111ll111l_opy_ = re.compile(bstack11l1l_opy_ (u"ࡵࠫࡣࡡࡁ࠮࡜࠳࠱࠾ࡥ࡝ࠬࠦࠪὠ"))
            for name, bstack11111ll1l1l_opy_ in data.items():
                if not isinstance(bstack11111ll1l1l_opy_, dict):
                    continue
                url = bstack11111ll1l1l_opy_.get(bstack11l1l_opy_ (u"ࠫࡺࡸ࡬ࠨὡ"))
                if url is None or (isinstance(url, str) and url.strip() == bstack11l1l_opy_ (u"ࠬ࠭ὢ")):
                    logger.warning(bstack11l1l_opy_ (u"ࠨࡒࡦࡲࡲࡷ࡮ࡺ࡯ࡳࡻ࡙ࠣࡗࡒࠠࡪࡵࠣࡱ࡮ࡹࡳࡪࡰࡪࠤ࡫ࡵࡲࠡࡵࡲࡹࡷࡩࡥࠡࠩࡾࢁࠬࡀࠠࡼࡿࠥὣ").format(name, bstack11111ll1l1l_opy_))
                    continue
                if not bstack11111ll111l_opy_.match(name):
                    logger.warning(bstack11l1l_opy_ (u"ࠢࡊࡰࡹࡥࡱ࡯ࡤࠡࡵࡲࡹࡷࡩࡥࠡ࡫ࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠥ࡬࡯ࡳ࡯ࡤࡸࠥ࡬࡯ࡳࠢࠪࡿࢂ࠭࠺ࠡࡽࢀࠦὤ").format(name, bstack11111ll1l1l_opy_))
                    continue
                if len(name) > 30 or len(name) < 1:
                    logger.warning(bstack11l1l_opy_ (u"ࠣࡕࡲࡹࡷࡩࡥࠡ࡫ࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠥ࠭ࡻࡾࠩࠣࡱࡺࡹࡴࠡࡪࡤࡺࡪࠦࡡࠡ࡮ࡨࡲ࡬ࡺࡨࠡࡤࡨࡸࡼ࡫ࡥ࡯ࠢ࠴ࠤࡦࡴࡤࠡ࠵࠳ࠤࡨ࡮ࡡࡳࡣࡦࡸࡪࡸࡳ࠯ࠤὥ").format(name))
                    continue
                bstack11111ll1l1l_opy_ = bstack11111ll1l1l_opy_.copy()
                bstack11111ll1l1l_opy_[bstack11l1l_opy_ (u"ࠩࡱࡥࡲ࡫ࠧὦ")] = name
                bstack11111ll1l1l_opy_[bstack11l1l_opy_ (u"ࠪࡪࡪࡧࡴࡶࡴࡨࡆࡷࡧ࡮ࡤࡪࠪὧ")] = bstack1111l1ll111_opy_(name, bstack11111ll1l1l_opy_)
                if not bstack11111ll1l1l_opy_.get(bstack11l1l_opy_ (u"ࠫ࡫࡫ࡡࡵࡷࡵࡩࡇࡸࡡ࡯ࡥ࡫ࠫὨ")) or bstack11111ll1l1l_opy_.get(bstack11l1l_opy_ (u"ࠬ࡬ࡥࡢࡶࡸࡶࡪࡈࡲࡢࡰࡦ࡬ࠬὩ")) == bstack11l1l_opy_ (u"࠭ࠧὪ"):
                    logger.warning(bstack11l1l_opy_ (u"ࠢࡇࡧࡤࡸࡺࡸࡥࠡࡤࡵࡥࡳࡩࡨࠡࡰࡲࡸࠥࡹࡰࡦࡥ࡬ࡪ࡮࡫ࡤࠡࡨࡲࡶࠥࡹ࡯ࡶࡴࡦࡩࠥ࠭ࡻࡾࠩ࠽ࠤࢀࢃࠢὫ").format(name, bstack11111ll1l1l_opy_))
                    continue
                if bstack11111ll1l1l_opy_.get(bstack11l1l_opy_ (u"ࠨࡤࡤࡷࡪࡈࡲࡢࡰࡦ࡬ࠬὬ")) and bstack11111ll1l1l_opy_[bstack11l1l_opy_ (u"ࠩࡥࡥࡸ࡫ࡂࡳࡣࡱࡧ࡭࠭Ὥ")] == bstack11111ll1l1l_opy_[bstack11l1l_opy_ (u"ࠪࡪࡪࡧࡴࡶࡴࡨࡆࡷࡧ࡮ࡤࡪࠪὮ")]:
                    logger.warning(bstack11l1l_opy_ (u"ࠦࡋ࡫ࡡࡵࡷࡵࡩࠥࡨࡲࡢࡰࡦ࡬ࠥࡧ࡮ࡥࠢࡥࡥࡸ࡫ࠠࡣࡴࡤࡲࡨ࡮ࠠࡤࡣࡱࡲࡴࡺࠠࡣࡧࠣࡸ࡭࡫ࠠࡴࡣࡰࡩࠥ࡬࡯ࡳࠢࡶࡳࡺࡸࡣࡦࠢࠪࡿࢂ࠭࠺ࠡࡽࢀࠦὯ").format(name, bstack11111ll1l1l_opy_))
                    continue
                bstack11111l1ll11_opy_.append(bstack11111ll1l1l_opy_)
            return bstack11111l1ll11_opy_
        return data
    def bstack1111ll1l11l_opy_(self):
        data = {
            bstack11l1l_opy_ (u"ࠬࡸࡵ࡯ࡡࡶࡱࡦࡸࡴࡠࡵࡨࡰࡪࡩࡴࡪࡱࡱࠫὰ"): {
                bstack11l1l_opy_ (u"࠭ࡥ࡯ࡣࡥࡰࡪࡪࠧά"): self.bstack11111l1lll1_opy_(),
                bstack11l1l_opy_ (u"ࠧ࡮ࡱࡧࡩࠬὲ"): self.bstack1111l1lll1l_opy_(),
                bstack11l1l_opy_ (u"ࠨࡵࡲࡹࡷࡩࡥࠨέ"): self.bstack11111ll1l11_opy_()
            }
        }
        return data
    def bstack1111l1111ll_opy_(self, config):
        bstack11111ll1ll1_opy_ = {}
        bstack11111ll1ll1_opy_[bstack11l1l_opy_ (u"ࠩࡵࡹࡳࡥࡳ࡮ࡣࡵࡸࡤࡹࡥ࡭ࡧࡦࡸ࡮ࡵ࡮ࠨὴ")] = {
            bstack11l1l_opy_ (u"ࠪࡩࡳࡧࡢ࡭ࡧࡧࠫή"): self.bstack11111l1lll1_opy_(),
            bstack11l1l_opy_ (u"ࠫࡲࡵࡤࡦࠩὶ"): self.bstack1111l1lll1l_opy_()
        }
        bstack11111ll1ll1_opy_[bstack11l1l_opy_ (u"ࠬࡸࡥࡳࡷࡱࡣࡵࡸࡥࡷ࡫ࡲࡹࡸࡲࡹࡠࡨࡤ࡭ࡱ࡫ࡤࠨί")] = {
            bstack11l1l_opy_ (u"࠭ࡥ࡯ࡣࡥࡰࡪࡪࠧὸ"): self.bstack1111l11111l_opy_()
        }
        bstack11111ll1ll1_opy_[bstack11l1l_opy_ (u"ࠧࡳࡷࡱࡣࡵࡸࡥࡷ࡫ࡲࡹࡸࡲࡹࡠࡨࡤ࡭ࡱ࡫ࡤࡠࡨ࡬ࡶࡸࡺࠧό")] = {
            bstack11l1l_opy_ (u"ࠨࡧࡱࡥࡧࡲࡥࡥࠩὺ"): self.bstack11111ll1lll_opy_()
        }
        bstack11111ll1ll1_opy_[bstack11l1l_opy_ (u"ࠩࡶ࡯࡮ࡶ࡟ࡧࡣ࡬ࡰ࡮ࡴࡧࡠࡣࡱࡨࡤ࡬࡬ࡢ࡭ࡼࠫύ")] = {
            bstack11l1l_opy_ (u"ࠪࡩࡳࡧࡢ࡭ࡧࡧࠫὼ"): self.bstack1111l11l1ll_opy_()
        }
        if self.bstack1ll111l111_opy_(config):
            bstack11111ll1ll1_opy_[bstack11l1l_opy_ (u"ࠫࡷ࡫ࡴࡳࡻࡢࡸࡪࡹࡴࡴࡡࡲࡲࡤ࡬ࡡࡪ࡮ࡸࡶࡪ࠭ώ")] = {
                bstack11l1l_opy_ (u"ࠬ࡫࡮ࡢࡤ࡯ࡩࡩ࠭὾"): True,
                bstack11l1l_opy_ (u"࠭࡭ࡢࡺࡢࡶࡪࡺࡲࡪࡧࡶࠫ὿"): self.bstack1111lllll_opy_(config)
            }
        if self.bstack11l11l1l11l_opy_(config):
            bstack11111ll1ll1_opy_[bstack11l1l_opy_ (u"ࠧࡢࡤࡲࡶࡹࡥࡢࡶ࡫࡯ࡨࡤࡵ࡮ࡠࡨࡤ࡭ࡱࡻࡲࡦࠩᾀ")] = {
                bstack11l1l_opy_ (u"ࠨࡧࡱࡥࡧࡲࡥࡥࠩᾁ"): True,
                bstack11l1l_opy_ (u"ࠩࡰࡥࡽࡥࡦࡢ࡫࡯ࡹࡷ࡫ࡳࠨᾂ"): self.bstack11l11l11111_opy_(config)
            }
        return bstack11111ll1ll1_opy_
    def bstack1111l1l1_opy_(self, config):
        bstack11l1l_opy_ (u"ࠥࠦࠧࠐࠠࠡࠢࠣࠤࠥࠦࠠࡄࡱ࡯ࡰࡪࡩࡴࡴࠢࡥࡹ࡮ࡲࡤࠡࡦࡤࡸࡦࠦࡢࡺࠢࡰࡥࡰ࡯࡮ࡨࠢࡤࠤࡨࡧ࡬࡭ࠢࡷࡳࠥࡺࡨࡦࠢࡦࡳࡱࡲࡥࡤࡶ࠰ࡦࡺ࡯࡬ࡥ࠯ࡧࡥࡹࡧࠠࡦࡰࡧࡴࡴ࡯࡮ࡵ࠰ࠍࠤࠥࠦࠠࠡࠢࠣࠤࡆࡸࡧࡴ࠼ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࡤࡸ࡭ࡱࡪ࡟ࡶࡷ࡬ࡨࠥ࠮ࡳࡵࡴࠬ࠾࡚ࠥࡨࡦࠢࡘ࡙ࡎࡊࠠࡰࡨࠣࡸ࡭࡫ࠠࡣࡷ࡬ࡰࡩࠦࡴࡰࠢࡦࡳࡱࡲࡥࡤࡶࠣࡨࡦࡺࡡࠡࡨࡲࡶ࠳ࠐࠠࠡࠢࠣࠤࠥࠦࠠࡓࡧࡷࡹࡷࡴࡳ࠻ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࡥ࡫ࡦࡸ࠿ࠦࡒࡦࡵࡳࡳࡳࡹࡥࠡࡨࡵࡳࡲࠦࡴࡩࡧࠣࡧࡴࡲ࡬ࡦࡥࡷ࠱ࡧࡻࡩ࡭ࡦ࠰ࡨࡦࡺࡡࠡࡧࡱࡨࡵࡵࡩ࡯ࡶ࠯ࠤࡴࡸࠠࡏࡱࡱࡩࠥ࡯ࡦࠡࡨࡤ࡭ࡱ࡫ࡤ࠯ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠦࠧࠨᾃ")
        if not (config.get(bstack11l1l_opy_ (u"ࠫ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱࠧᾄ"), None) in bstack11l11lll1l1_opy_ and self.bstack11111l1lll1_opy_()):
            return None
        bstack1111l1lll11_opy_ = os.environ.get(bstack11l1l_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡊࡘࡆࡤ࡛ࡕࡊࡆࠪᾅ"), None)
        logger.debug(bstack11l1l_opy_ (u"ࠨ࡛ࡤࡱ࡯ࡰࡪࡩࡴࡃࡷ࡬ࡰࡩࡊࡡࡵࡣࡠࠤࡈࡵ࡬࡭ࡧࡦࡸ࡮ࡴࡧࠡࡤࡸ࡭ࡱࡪࠠࡥࡣࡷࡥࠥ࡬࡯ࡳࠢࡥࡹ࡮ࡲࡤࠡࡗࡘࡍࡉࡀࠠࡼࡿࠥᾆ").format(bstack1111l1lll11_opy_))
        try:
            bstack11l1ll1ll11_opy_ = bstack11l1l_opy_ (u"ࠢࡵࡧࡶࡸࡴࡸࡣࡩࡧࡶࡸࡷࡧࡴࡪࡱࡱ࠳ࡦࡶࡩ࠰ࡸ࠴࠳ࡧࡻࡩ࡭ࡦࡶ࠳ࢀࢃ࠯ࡤࡱ࡯ࡰࡪࡩࡴ࠮ࡤࡸ࡭ࡱࡪ࠭ࡥࡣࡷࡥࠧᾇ").format(bstack1111l1lll11_opy_)
            payload = {
                bstack11l1l_opy_ (u"ࠣࡲࡵࡳ࡯࡫ࡣࡵࡐࡤࡱࡪࠨᾈ"): config.get(bstack11l1l_opy_ (u"ࠩࡳࡶࡴࡰࡥࡤࡶࡑࡥࡲ࡫ࠧᾉ"), bstack11l1l_opy_ (u"ࠪࠫᾊ")),
                bstack11l1l_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡑࡥࡲ࡫ࠢᾋ"): config.get(bstack11l1l_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡒࡦࡳࡥࠨᾌ"), os.path.basename(os.path.abspath(os.getcwd()))),
                bstack11l1l_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡗࡻ࡮ࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠦᾍ"): os.environ.get(bstack11l1l_opy_ (u"ࠢࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡂࡖࡋࡏࡈࡤࡘࡕࡏࡡࡌࡈࡊࡔࡔࡊࡈࡌࡉࡗࠨᾎ"), bstack11l1l_opy_ (u"ࠣࠤᾏ")),
                bstack11l1l_opy_ (u"ࠤࡱࡳࡩ࡫ࡉ࡯ࡦࡨࡼࠧᾐ"): int(os.environ.get(bstack11l1l_opy_ (u"ࠥࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡑࡓࡉࡋ࡟ࡊࡐࡇࡉ࡝ࠨᾑ")) or bstack11l1l_opy_ (u"ࠦ࠵ࠨᾒ")),
                bstack11l1l_opy_ (u"ࠧࡺ࡯ࡵࡣ࡯ࡒࡴࡪࡥࡴࠤᾓ"): int(os.environ.get(bstack11l1l_opy_ (u"ࠨࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡏࡕࡃࡏࡣࡓࡕࡄࡆࡡࡆࡓ࡚ࡔࡔࠣᾔ")) or bstack11l1l_opy_ (u"ࠢ࠲ࠤᾕ")),
                bstack11l1l_opy_ (u"ࠣࡪࡲࡷࡹࡏ࡮ࡧࡱࠥᾖ"): get_host_info(),
            }
            logger.debug(bstack11l1l_opy_ (u"ࠤ࡞ࡧࡴࡲ࡬ࡦࡥࡷࡆࡺ࡯࡬ࡥࡆࡤࡸࡦࡣࠠࡔࡧࡱࡨ࡮ࡴࡧࠡࡤࡸ࡭ࡱࡪࠠࡥࡣࡷࡥࠥࡶࡡࡺ࡮ࡲࡥࡩࡀࠠࡼࡿࠥᾗ").format(payload))
            response = bstack11l1ll1l1ll_opy_.bstack11111llll11_opy_(bstack11l1ll1ll11_opy_, payload)
            if response:
                logger.debug(bstack11l1l_opy_ (u"ࠥ࡟ࡨࡵ࡬࡭ࡧࡦࡸࡇࡻࡩ࡭ࡦࡇࡥࡹࡧ࡝ࠡࡄࡸ࡭ࡱࡪࠠࡥࡣࡷࡥࠥࡩ࡯࡭࡮ࡨࡧࡹ࡯࡯࡯ࠢࡵࡩࡸࡶ࡯࡯ࡵࡨ࠾ࠥࢁࡽࠣᾘ").format(response))
                return response
            else:
                logger.error(bstack11l1l_opy_ (u"ࠦࡠࡩ࡯࡭࡮ࡨࡧࡹࡈࡵࡪ࡮ࡧࡈࡦࡺࡡ࡞ࠢࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥࡩ࡯࡭࡮ࡨࡧࡹࠦࡢࡶ࡫࡯ࡨࠥࡪࡡࡵࡣࠣࡪࡴࡸࠠࡣࡷ࡬ࡰࡩࠦࡕࡖࡋࡇ࠾ࠥࢁࡽࠣᾙ").format(bstack1111l1lll11_opy_))
                return None
        except Exception as e:
            logger.error(bstack11l1l_opy_ (u"ࠧࡡࡣࡰ࡮࡯ࡩࡨࡺࡂࡶ࡫࡯ࡨࡉࡧࡴࡢ࡟ࠣࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡩ࡯ࠢࡦࡳࡱࡲࡥࡤࡶ࡬ࡲ࡬ࠦࡢࡶ࡫࡯ࡨࠥࡪࡡࡵࡣࠣࡪࡴࡸࠠࡣࡷ࡬ࡰࡩࠦࡕࡖࡋࡇࠤࢀࢃ࠺ࠡࡽࢀࠦᾚ").format(bstack1111l1lll11_opy_, e))
            return None