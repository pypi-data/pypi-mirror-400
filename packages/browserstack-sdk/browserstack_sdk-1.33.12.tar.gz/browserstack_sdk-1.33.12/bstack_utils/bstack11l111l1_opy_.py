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
import tempfile
import math
from bstack_utils import bstack111lll1l1_opy_
from bstack_utils.constants import bstack11l1111l1_opy_, bstack11l1l1111l1_opy_
from bstack_utils.helper import bstack111lll11111_opy_, get_host_info
from bstack_utils.bstack11l1ll1l1l1_opy_ import bstack11l1ll1l11l_opy_
import json
import re
import sys
bstack11111ll11l1_opy_ = bstack11ll1_opy_ (u"ࠢࡳࡧࡷࡶࡾ࡚ࡥࡴࡶࡶࡓࡳࡌࡡࡪ࡮ࡸࡶࡪࠨ἞")
bstack1111l111lll_opy_ = bstack11ll1_opy_ (u"ࠣࡣࡥࡳࡷࡺࡂࡶ࡫࡯ࡨࡔࡴࡆࡢ࡫࡯ࡹࡷ࡫ࠢ἟")
bstack1111ll11111_opy_ = bstack11ll1_opy_ (u"ࠤࡵࡹࡳࡖࡲࡦࡸ࡬ࡳࡺࡹ࡬ࡺࡈࡤ࡭ࡱ࡫ࡤࡇ࡫ࡵࡷࡹࠨἠ")
bstack1111l1llll1_opy_ = bstack11ll1_opy_ (u"ࠥࡶࡪࡸࡵ࡯ࡒࡵࡩࡻ࡯࡯ࡶࡵ࡯ࡽࡋࡧࡩ࡭ࡧࡧࠦἡ")
bstack1111l11l1ll_opy_ = bstack11ll1_opy_ (u"ࠦࡸࡱࡩࡱࡈ࡯ࡥࡰࡿࡡ࡯ࡦࡉࡥ࡮ࡲࡥࡥࠤἢ")
bstack1111l1lllll_opy_ = bstack11ll1_opy_ (u"ࠧࡸࡵ࡯ࡕࡰࡥࡷࡺࡓࡦ࡮ࡨࡧࡹ࡯࡯࡯ࠤἣ")
bstack11111l1ll11_opy_ = {
    bstack11111ll11l1_opy_,
    bstack1111l111lll_opy_,
    bstack1111ll11111_opy_,
    bstack1111l1llll1_opy_,
    bstack1111l11l1ll_opy_,
    bstack1111l1lllll_opy_
}
bstack11111llll1l_opy_ = {bstack11ll1_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹ࠭ἤ")}
logger = bstack111lll1l1_opy_.get_logger(__name__, bstack11l1111l1_opy_)
class bstack1111l1l1ll1_opy_:
    def __init__(self):
        self.enabled = False
        self.name = None
    def enable(self, name):
        self.enabled = True
        self.name = name
    def disable(self):
        self.enabled = False
        self.name = None
    def bstack11111ll11ll_opy_(self):
        return self.enabled
    def get_name(self):
        return self.name
class bstack1lll1lll_opy_:
    _1l1l1ll11l1_opy_ = None
    def __init__(self, config):
        self.bstack1111l1lll11_opy_ = False
        self.bstack11111l1l1ll_opy_ = False
        self.bstack1111l111l11_opy_ = False
        self.bstack11111lll111_opy_ = False
        self.bstack11111ll1l1l_opy_ = None
        self.bstack1111l1l11l1_opy_ = bstack1111l1l1ll1_opy_()
        self.bstack1111l11l11l_opy_ = None
        opts = config.get(bstack11ll1_opy_ (u"ࠧࡵࡧࡶࡸࡔࡸࡣࡩࡧࡶࡸࡷࡧࡴࡪࡱࡱࡓࡵࡺࡩࡰࡰࡶࠫἥ"), {})
        self.bstack1111ll1111l_opy_ = config.get(bstack11ll1_opy_ (u"ࠨࡵࡰࡥࡷࡺࡓࡦ࡮ࡨࡧࡹ࡯࡯࡯ࡈࡨࡥࡹࡻࡲࡦࡄࡵࡥࡳࡩࡨࡦࡵࡈࡒ࡛࠭ἦ"), bstack11ll1_opy_ (u"ࠤࠥἧ"))
        self.bstack11111ll1111_opy_ = config.get(bstack11ll1_opy_ (u"ࠪࡷࡲࡧࡲࡵࡕࡨࡰࡪࡩࡴࡪࡱࡱࡊࡪࡧࡴࡶࡴࡨࡆࡷࡧ࡮ࡤࡪࡨࡷࡈࡒࡉࠨἨ"), bstack11ll1_opy_ (u"ࠦࠧἩ"))
        bstack11111llll11_opy_ = opts.get(bstack1111l1lllll_opy_, {})
        bstack11111lllll1_opy_ = None
        if bstack11ll1_opy_ (u"ࠬࡹ࡯ࡶࡴࡦࡩࠬἪ") in bstack11111llll11_opy_:
            bstack11111ll111l_opy_ = bstack11111llll11_opy_[bstack11ll1_opy_ (u"࠭ࡳࡰࡷࡵࡧࡪ࠭Ἣ")]
            if bstack11111ll111l_opy_ is None or (isinstance(bstack11111ll111l_opy_, str) and bstack11111ll111l_opy_.strip() == bstack11ll1_opy_ (u"ࠧࠨἬ")) or (isinstance(bstack11111ll111l_opy_, list) and len(bstack11111ll111l_opy_) == 0):
                bstack11111lllll1_opy_ = []
            elif isinstance(bstack11111ll111l_opy_, list):
                bstack11111lllll1_opy_ = bstack11111ll111l_opy_
            elif isinstance(bstack11111ll111l_opy_, str) and bstack11111ll111l_opy_.strip():
                bstack11111lllll1_opy_ = bstack11111ll111l_opy_
            else:
                logger.warning(bstack11ll1_opy_ (u"ࠣࡋࡱࡺࡦࡲࡩࡥࠢࡶࡳࡺࡸࡣࡦࠢࡹࡥࡱࡻࡥࠡ࡫ࡱࠤࡨࡵ࡮ࡧ࡫ࡪ࠾ࠥࢁࡽ࠯ࠢࡇࡩ࡫ࡧࡵ࡭ࡶ࡬ࡲ࡬ࠦࡴࡰࠢࡨࡱࡵࡺࡹࠡ࡮࡬ࡷࡹ࠴ࠢἭ").format(bstack11111ll111l_opy_))
                bstack11111lllll1_opy_ = []
        self.__1111l11l1l1_opy_(
            bstack11111llll11_opy_.get(bstack11ll1_opy_ (u"ࠩࡨࡲࡦࡨ࡬ࡦࡦࠪἮ"), False),
            bstack11111llll11_opy_.get(bstack11ll1_opy_ (u"ࠪࡱࡴࡪࡥࠨἯ"), bstack11ll1_opy_ (u"ࠫࡷ࡫࡬ࡦࡸࡤࡲࡹࡌࡩࡳࡵࡷࠫἰ")),
            bstack11111lllll1_opy_
        )
        self.__1111l1l1l1l_opy_(opts.get(bstack1111ll11111_opy_, False))
        self.__11111l1l11l_opy_(opts.get(bstack1111l1llll1_opy_, False))
        self.__11111lll11l_opy_(opts.get(bstack1111l11l1ll_opy_, False))
    @classmethod
    def bstack1l1l1111_opy_(cls, config=None):
        if cls._1l1l1ll11l1_opy_ is None and config is not None:
            cls._1l1l1ll11l1_opy_ = bstack1lll1lll_opy_(config)
        return cls._1l1l1ll11l1_opy_
    @staticmethod
    def bstack1ll11l11ll_opy_(config: dict) -> bool:
        bstack11111ll1l11_opy_ = config.get(bstack11ll1_opy_ (u"ࠬࡺࡥࡴࡶࡒࡶࡨ࡮ࡥࡴࡶࡵࡥࡹ࡯࡯࡯ࡑࡳࡸ࡮ࡵ࡮ࡴࠩἱ"), {}).get(bstack11111ll11l1_opy_, {})
        return bstack11111ll1l11_opy_.get(bstack11ll1_opy_ (u"࠭ࡥ࡯ࡣࡥࡰࡪࡪࠧἲ"), False)
    @staticmethod
    def bstack1lllllll1l_opy_(config: dict) -> int:
        bstack11111ll1l11_opy_ = config.get(bstack11ll1_opy_ (u"ࠧࡵࡧࡶࡸࡔࡸࡣࡩࡧࡶࡸࡷࡧࡴࡪࡱࡱࡓࡵࡺࡩࡰࡰࡶࠫἳ"), {}).get(bstack11111ll11l1_opy_, {})
        retries = 0
        if bstack1lll1lll_opy_.bstack1ll11l11ll_opy_(config):
            retries = bstack11111ll1l11_opy_.get(bstack11ll1_opy_ (u"ࠨ࡯ࡤࡼࡗ࡫ࡴࡳ࡫ࡨࡷࠬἴ"), 1)
        return retries
    @staticmethod
    def bstack1l1l1111l_opy_(config: dict) -> dict:
        bstack1111l11lll1_opy_ = config.get(bstack11ll1_opy_ (u"ࠩࡷࡩࡸࡺࡏࡳࡥ࡫ࡩࡸࡺࡲࡢࡶ࡬ࡳࡳࡕࡰࡵ࡫ࡲࡲࡸ࠭ἵ"), {})
        return {
            key: value for key, value in bstack1111l11lll1_opy_.items() if key in bstack11111l1ll11_opy_
        }
    @staticmethod
    def bstack1111l11l111_opy_():
        bstack11ll1_opy_ (u"ࠥࠦࠧࠐࠠࠡࠢࠣࠤࠥࠦࠠࡄࡪࡨࡧࡰࠦࡩࡧࠢࡷ࡬ࡪࠦࡡࡣࡱࡵࡸࠥࡨࡵࡪ࡮ࡧࠤ࡫࡯࡬ࡦࠢࡨࡼ࡮ࡹࡴࡴ࠰ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠧࠨࠢἶ")
        return os.path.exists(os.path.join(tempfile.gettempdir(), bstack11ll1_opy_ (u"ࠦࡦࡨ࡯ࡳࡶࡢࡦࡺ࡯࡬ࡥࡡࡾࢁࠧἷ").format(os.getenv(bstack11ll1_opy_ (u"ࠧࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡊࡘࡆࡤ࡛ࡕࡊࡆࠥἸ")))))
    @staticmethod
    def bstack1111l1l1111_opy_(test_name: str):
        bstack11ll1_opy_ (u"ࠨࠢࠣࠌࠣࠤࠥࠦࠠࠡࠢࠣࡇ࡭࡫ࡣ࡬ࠢ࡬ࡪࠥࡺࡨࡦࠢࡤࡦࡴࡸࡴࠡࡤࡸ࡭ࡱࡪࠠࡧ࡫࡯ࡩࠥ࡫ࡸࡪࡵࡷࡷ࠳ࠐࠠࠡࠢࠣࠤࠥࠦࠠࠣࠤࠥἹ")
        bstack1111l1ll1l1_opy_ = os.path.join(tempfile.gettempdir(), bstack11ll1_opy_ (u"ࠢࡧࡣ࡬ࡰࡪࡪ࡟ࡵࡧࡶࡸࡸࡥࡻࡾ࠰ࡷࡼࡹࠨἺ").format(os.getenv(bstack11ll1_opy_ (u"ࠣࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡍ࡛ࡂࡠࡗࡘࡍࡉࠨἻ"))))
        with open(bstack1111l1ll1l1_opy_, bstack11ll1_opy_ (u"ࠩࡤࠫἼ")) as file:
            file.write(bstack11ll1_opy_ (u"ࠥࡿࢂࡢ࡮ࠣἽ").format(test_name))
    @staticmethod
    def bstack1111l1l1lll_opy_(framework: str) -> bool:
       return framework.lower() in bstack11111llll1l_opy_
    @staticmethod
    def bstack11l11l11111_opy_(config: dict) -> bool:
        bstack1111l111ll1_opy_ = config.get(bstack11ll1_opy_ (u"ࠫࡹ࡫ࡳࡵࡑࡵࡧ࡭࡫ࡳࡵࡴࡤࡸ࡮ࡵ࡮ࡐࡲࡷ࡭ࡴࡴࡳࠨἾ"), {}).get(bstack1111l111lll_opy_, {})
        return bstack1111l111ll1_opy_.get(bstack11ll1_opy_ (u"ࠬ࡫࡮ࡢࡤ࡯ࡩࡩ࠭Ἷ"), False)
    @staticmethod
    def bstack11l11l1l1l1_opy_(config: dict, bstack11l11l1ll1l_opy_: int = 0) -> int:
        bstack11ll1_opy_ (u"ࠨࠢࠣࠌࠣࠤࠥࠦࠠࠡࠢࠣࡋࡪࡺࠠࡵࡪࡨࠤ࡫ࡧࡩ࡭ࡷࡵࡩࠥࡺࡨࡳࡧࡶ࡬ࡴࡲࡤ࠭ࠢࡺ࡬࡮ࡩࡨࠡࡥࡤࡲࠥࡨࡥࠡࡣࡱࠤࡦࡨࡳࡰ࡮ࡸࡸࡪࠦ࡮ࡶ࡯ࡥࡩࡷࠦ࡯ࡳࠢࡤࠤࡵ࡫ࡲࡤࡧࡱࡸࡦ࡭ࡥ࠯ࠌࠣࠤࠥࠦࠠࠡࠢࠣࡅࡷ࡭ࡳ࠻ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࡤࡱࡱࡪ࡮࡭ࠠࠩࡦ࡬ࡧࡹ࠯࠺ࠡࡖ࡫ࡩࠥࡩ࡯࡯ࡨ࡬࡫ࡺࡸࡡࡵ࡫ࡲࡲࠥࡪࡩࡤࡶ࡬ࡳࡳࡧࡲࡺ࠰ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࡶࡲࡸࡦࡲ࡟ࡵࡧࡶࡸࡸࠦࠨࡪࡰࡷ࠭࠿ࠦࡔࡩࡧࠣࡸࡴࡺࡡ࡭ࠢࡱࡹࡲࡨࡥࡳࠢࡲࡪࠥࡺࡥࡴࡶࡶࠤ࠭ࡸࡥࡲࡷ࡬ࡶࡪࡪࠠࡧࡱࡵࠤࡵ࡫ࡲࡤࡧࡱࡸࡦ࡭ࡥ࠮ࡤࡤࡷࡪࡪࠠࡵࡪࡵࡩࡸ࡮࡯࡭ࡦࡶ࠭࠳ࠐࠠࠡࠢࠣࠤࠥࠦࠠࡓࡧࡷࡹࡷࡴࡳ࠻ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࡪࡰࡷ࠾࡚ࠥࡨࡦࠢࡩࡥ࡮ࡲࡵࡳࡧࠣࡸ࡭ࡸࡥࡴࡪࡲࡰࡩ࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࠤࠥࠦὀ")
        bstack1111l111ll1_opy_ = config.get(bstack11ll1_opy_ (u"ࠧࡵࡧࡶࡸࡔࡸࡣࡩࡧࡶࡸࡷࡧࡴࡪࡱࡱࡓࡵࡺࡩࡰࡰࡶࠫὁ"), {}).get(bstack11ll1_opy_ (u"ࠨࡣࡥࡳࡷࡺࡂࡶ࡫࡯ࡨࡔࡴࡆࡢ࡫࡯ࡹࡷ࡫ࠧὂ"), {})
        bstack11111llllll_opy_ = 0
        bstack1111l1ll111_opy_ = 0
        if bstack1lll1lll_opy_.bstack11l11l11111_opy_(config):
            bstack1111l1ll111_opy_ = bstack1111l111ll1_opy_.get(bstack11ll1_opy_ (u"ࠩࡰࡥࡽࡌࡡࡪ࡮ࡸࡶࡪࡹࠧὃ"), 5)
            if isinstance(bstack1111l1ll111_opy_, str) and bstack1111l1ll111_opy_.endswith(bstack11ll1_opy_ (u"ࠪࠩࠬὄ")):
                try:
                    percentage = int(bstack1111l1ll111_opy_.strip(bstack11ll1_opy_ (u"ࠫࠪ࠭ὅ")))
                    if bstack11l11l1ll1l_opy_ > 0:
                        bstack11111llllll_opy_ = math.ceil((percentage * bstack11l11l1ll1l_opy_) / 100)
                    else:
                        raise ValueError(bstack11ll1_opy_ (u"࡚ࠧ࡯ࡵࡣ࡯ࠤࡹ࡫ࡳࡵࡵࠣࡱࡺࡹࡴࠡࡤࡨࠤࡵࡸ࡯ࡷ࡫ࡧࡩࡩࠦࡦࡰࡴࠣࡴࡪࡸࡣࡦࡰࡷࡥ࡬࡫࠭ࡣࡣࡶࡩࡩࠦࡴࡩࡴࡨࡷ࡭ࡵ࡬ࡥࡵ࠱ࠦ὆"))
                except ValueError as e:
                    raise ValueError(bstack11ll1_opy_ (u"ࠨࡉ࡯ࡸࡤࡰ࡮ࡪࠠࡱࡧࡵࡧࡪࡴࡴࡢࡩࡨࠤࡻࡧ࡬ࡶࡧࠣࡪࡴࡸࠠ࡮ࡣࡻࡊࡦ࡯࡬ࡶࡴࡨࡷ࠿ࠦࡻࡾࠤ὇").format(bstack1111l1ll111_opy_)) from e
            else:
                bstack11111llllll_opy_ = int(bstack1111l1ll111_opy_)
        logger.info(bstack11ll1_opy_ (u"ࠢࡎࡣࡻࠤ࡫ࡧࡩ࡭ࡷࡵࡩࡸࠦࡴࡩࡴࡨࡷ࡭ࡵ࡬ࡥࠢࡶࡩࡹࠦࡴࡰ࠼ࠣࡿࢂࠦࠨࡧࡴࡲࡱࠥࡩ࡯࡯ࡨ࡬࡫࠿ࠦࡻࡾࠫࠥὈ").format(bstack11111llllll_opy_, bstack1111l1ll111_opy_))
        return bstack11111llllll_opy_
    def bstack1111l11llll_opy_(self):
        return self.bstack11111lll111_opy_
    def bstack1111l1l111l_opy_(self):
        return self.bstack11111ll1l1l_opy_
    def bstack11111ll1lll_opy_(self):
        return self.bstack1111l11l11l_opy_
    def __1111l11l1l1_opy_(self, enabled, mode, source=None):
        try:
            self.bstack11111lll111_opy_ = bool(enabled)
            if mode not in [bstack11ll1_opy_ (u"ࠨࡴࡨࡰࡪࡼࡡ࡯ࡶࡉ࡭ࡷࡹࡴࠨὉ"), bstack11ll1_opy_ (u"ࠩࡵࡩࡱ࡫ࡶࡢࡰࡷࡓࡳࡲࡹࠨὊ")]:
                logger.warning(bstack11ll1_opy_ (u"ࠥࡍࡳࡼࡡ࡭࡫ࡧࠤࡸࡳࡡࡳࡶࠣࡷࡪࡲࡥࡤࡶ࡬ࡳࡳࠦ࡭ࡰࡦࡨࠤࠬࢁࡽࠨࠢࡳࡶࡴࡼࡩࡥࡧࡧ࠲ࠥࡊࡥࡧࡣࡸࡰࡹ࡯࡮ࡨࠢࡷࡳࠥ࠭ࡲࡦ࡮ࡨࡺࡦࡴࡴࡇ࡫ࡵࡷࡹ࠭࠮ࠣὋ").format(mode))
                mode = bstack11ll1_opy_ (u"ࠫࡷ࡫࡬ࡦࡸࡤࡲࡹࡌࡩࡳࡵࡷࠫὌ")
            self.bstack11111ll1l1l_opy_ = mode
            self.bstack1111l11l11l_opy_ = []
            if source is None:
                self.bstack1111l11l11l_opy_ = None
            elif isinstance(source, list):
                self.bstack1111l11l11l_opy_ = source
            elif isinstance(source, str) and source.endswith(bstack11ll1_opy_ (u"ࠬ࠴ࡪࡴࡱࡱࠫὍ")):
                self.bstack1111l11l11l_opy_ = self._1111l1l11ll_opy_(source)
            self.__11111lll1l1_opy_()
        except Exception as e:
            logger.error(bstack11ll1_opy_ (u"ࠨࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡶࡩࡹࠦࡳ࡮ࡣࡵࡸࠥࡹࡥ࡭ࡧࡦࡸ࡮ࡵ࡮ࠡࡥࡲࡲ࡫࡯ࡧࡶࡴࡤࡸ࡮ࡵ࡮ࠡ࠯ࠣࡩࡳࡧࡢ࡭ࡧࡧ࠾ࠥࢁࡽ࠭ࠢࡰࡳࡩ࡫࠺ࠡࡽࢀ࠰ࠥࡹ࡯ࡶࡴࡦࡩ࠿ࠦࡻࡾ࠰ࠣࡉࡷࡸ࡯ࡳ࠼ࠣࡿࢂࠨ὎").format(enabled, mode, source, e))
    def bstack11111l1ll1l_opy_(self):
        return self.bstack1111l1lll11_opy_
    def __1111l1l1l1l_opy_(self, value):
        self.bstack1111l1lll11_opy_ = bool(value)
        self.__11111lll1l1_opy_()
    def bstack1111l111111_opy_(self):
        return self.bstack11111l1l1ll_opy_
    def __11111l1l11l_opy_(self, value):
        self.bstack11111l1l1ll_opy_ = bool(value)
        self.__11111lll1l1_opy_()
    def bstack1111l1ll1ll_opy_(self):
        return self.bstack1111l111l11_opy_
    def __11111lll11l_opy_(self, value):
        self.bstack1111l111l11_opy_ = bool(value)
        self.__11111lll1l1_opy_()
    def __11111lll1l1_opy_(self):
        if self.bstack11111lll111_opy_:
            self.bstack1111l1lll11_opy_ = False
            self.bstack11111l1l1ll_opy_ = False
            self.bstack1111l111l11_opy_ = False
            self.bstack1111l1l11l1_opy_.enable(bstack1111l1lllll_opy_)
        elif self.bstack1111l1lll11_opy_:
            self.bstack11111l1l1ll_opy_ = False
            self.bstack1111l111l11_opy_ = False
            self.bstack11111lll111_opy_ = False
            self.bstack1111l1l11l1_opy_.enable(bstack1111ll11111_opy_)
        elif self.bstack11111l1l1ll_opy_:
            self.bstack1111l1lll11_opy_ = False
            self.bstack1111l111l11_opy_ = False
            self.bstack11111lll111_opy_ = False
            self.bstack1111l1l11l1_opy_.enable(bstack1111l1llll1_opy_)
        elif self.bstack1111l111l11_opy_:
            self.bstack1111l1lll11_opy_ = False
            self.bstack11111l1l1ll_opy_ = False
            self.bstack11111lll111_opy_ = False
            self.bstack1111l1l11l1_opy_.enable(bstack1111l11l1ll_opy_)
        else:
            self.bstack1111l1l11l1_opy_.disable()
    def bstack1l1l1ll11_opy_(self):
        return self.bstack1111l1l11l1_opy_.bstack11111ll11ll_opy_()
    def bstack111llll11_opy_(self):
        if self.bstack1111l1l11l1_opy_.bstack11111ll11ll_opy_():
            return self.bstack1111l1l11l1_opy_.get_name()
        return None
    def _1111l1l11ll_opy_(self, bstack1111l1ll11l_opy_):
        bstack11ll1_opy_ (u"ࠢࠣࠤࠍࠤࠥࠦࠠࠡࠢࠣࠤࡕࡧࡲࡴࡧࠣࡎࡘࡕࡎࠡࡵࡲࡹࡷࡩࡥࠡࡥࡲࡲ࡫࡯ࡧࡶࡴࡤࡸ࡮ࡵ࡮ࠡࡨ࡬ࡰࡪࠦࡡ࡯ࡦࠣࡪࡴࡸ࡭ࡢࡶࠣ࡭ࡹࠦࡦࡰࡴࠣࡷࡲࡧࡲࡵࠢࡶࡩࡱ࡫ࡣࡵ࡫ࡲࡲ࠳ࠐࠠࠡࠢࠣࠤࠥࠦࠠࡂࡴࡪࡷ࠿ࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࡸࡵࡵࡳࡥࡨࡣ࡫࡯࡬ࡦࡡࡳࡥࡹ࡮ࠠࠩࡵࡷࡶ࠮ࡀࠠࡑࡣࡷ࡬ࠥࡺ࡯ࠡࡶ࡫ࡩࠥࡐࡓࡐࡐࠣࡧࡴࡴࡦࡪࡩࡸࡶࡦࡺࡩࡰࡰࠣࡪ࡮ࡲࡥࠋࠢࠣࠤࠥࠦࠠࠡࠢࡕࡩࡹࡻࡲ࡯ࡵ࠽ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢ࡯࡭ࡸࡺ࠺ࠡࡈࡲࡶࡲࡧࡴࡵࡧࡧࠤࡱ࡯ࡳࡵࠢࡲࡪࠥࡸࡥࡱࡱࡶ࡭ࡹࡵࡲࡺࠢࡦࡳࡳ࡬ࡩࡨࡷࡵࡥࡹ࡯࡯࡯ࡵࠍࠤࠥࠦࠠࠡࠢࠣࠤࠧࠨࠢ὏")
        if not os.path.isfile(bstack1111l1ll11l_opy_):
            logger.error(bstack11ll1_opy_ (u"ࠣࡕࡲࡹࡷࡩࡥࠡࡨ࡬ࡰࡪࠦࠧࡼࡿࠪࠤࡩࡵࡥࡴࠢࡱࡳࡹࠦࡥࡹ࡫ࡶࡸ࠳ࠨὐ").format(bstack1111l1ll11l_opy_))
            return []
        data = None
        try:
            with open(bstack1111l1ll11l_opy_, bstack11ll1_opy_ (u"ࠤࡵࠦὑ")) as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            logger.error(bstack11ll1_opy_ (u"ࠥࡉࡷࡸ࡯ࡳࠢࡳࡥࡷࡹࡩ࡯ࡩࠣࡎࡘࡕࡎࠡࡨࡵࡳࡲࠦࡳࡰࡷࡵࡧࡪࠦࡦࡪ࡮ࡨࠤࠬࢁࡽࠨ࠼ࠣࡿࢂࠨὒ").format(bstack1111l1ll11l_opy_, e))
            return []
        _1111l1lll1l_opy_ = None
        _1111l1111l1_opy_ = None
        def _1111l1111ll_opy_():
            bstack11111l1llll_opy_ = {}
            bstack1111l111l1l_opy_ = {}
            try:
                if self.bstack1111ll1111l_opy_.startswith(bstack11ll1_opy_ (u"ࠫࢀ࠭ὓ")) and self.bstack1111ll1111l_opy_.endswith(bstack11ll1_opy_ (u"ࠬࢃࠧὔ")):
                    bstack11111l1llll_opy_ = json.loads(self.bstack1111ll1111l_opy_)
                else:
                    bstack11111l1llll_opy_ = dict(item.split(bstack11ll1_opy_ (u"࠭࠺ࠨὕ")) for item in self.bstack1111ll1111l_opy_.split(bstack11ll1_opy_ (u"ࠧ࠭ࠩὖ")) if bstack11ll1_opy_ (u"ࠨ࠼ࠪὗ") in item) if self.bstack1111ll1111l_opy_ else {}
                if self.bstack11111ll1111_opy_.startswith(bstack11ll1_opy_ (u"ࠩࡾࠫ὘")) and self.bstack11111ll1111_opy_.endswith(bstack11ll1_opy_ (u"ࠪࢁࠬὙ")):
                    bstack1111l111l1l_opy_ = json.loads(self.bstack11111ll1111_opy_)
                else:
                    bstack1111l111l1l_opy_ = dict(item.split(bstack11ll1_opy_ (u"ࠫ࠿࠭὚")) for item in self.bstack11111ll1111_opy_.split(bstack11ll1_opy_ (u"ࠬ࠲ࠧὛ")) if bstack11ll1_opy_ (u"࠭࠺ࠨ὜") in item) if self.bstack11111ll1111_opy_ else {}
            except json.JSONDecodeError as e:
                logger.error(bstack11ll1_opy_ (u"ࠢࡆࡴࡵࡳࡷࠦࡰࡢࡴࡶ࡭ࡳ࡭ࠠࡧࡧࡤࡸࡺࡸࡥࠡࡤࡵࡥࡳࡩࡨࠡ࡯ࡤࡴࡵ࡯࡮ࡨࡵ࠽ࠤࢀࢃࠢὝ").format(e))
            logger.debug(bstack11ll1_opy_ (u"ࠣࡈࡨࡥࡹࡻࡲࡦࠢࡥࡶࡦࡴࡣࡩࠢࡰࡥࡵࡶࡩ࡯ࡩࡶࠤ࡫ࡸ࡯࡮ࠢࡨࡲࡻࡀࠠࡼࡿ࠯ࠤࡈࡒࡉ࠻ࠢࡾࢁࠧ὞").format(bstack11111l1llll_opy_, bstack1111l111l1l_opy_))
            return bstack11111l1llll_opy_, bstack1111l111l1l_opy_
        if _1111l1lll1l_opy_ is None or _1111l1111l1_opy_ is None:
            _1111l1lll1l_opy_, _1111l1111l1_opy_ = _1111l1111ll_opy_()
        def bstack1111l11ll1l_opy_(name, bstack1111l11ll11_opy_):
            if name in _1111l1111l1_opy_:
                return _1111l1111l1_opy_[name]
            if name in _1111l1lll1l_opy_:
                return _1111l1lll1l_opy_[name]
            if bstack1111l11ll11_opy_.get(bstack11ll1_opy_ (u"ࠩࡩࡩࡦࡺࡵࡳࡧࡅࡶࡦࡴࡣࡩࠩὟ")):
                return bstack1111l11ll11_opy_[bstack11ll1_opy_ (u"ࠪࡪࡪࡧࡴࡶࡴࡨࡆࡷࡧ࡮ࡤࡪࠪὠ")]
            return None
        if isinstance(data, dict):
            bstack11111ll1ll1_opy_ = []
            bstack1111l11111l_opy_ = re.compile(bstack11ll1_opy_ (u"ࡶࠬࡤ࡛ࡂ࠯࡝࠴࠲࠿࡟࡞࠭ࠧࠫὡ"))
            for name, bstack1111l11ll11_opy_ in data.items():
                if not isinstance(bstack1111l11ll11_opy_, dict):
                    continue
                url = bstack1111l11ll11_opy_.get(bstack11ll1_opy_ (u"ࠬࡻࡲ࡭ࠩὢ"))
                if url is None or (isinstance(url, str) and url.strip() == bstack11ll1_opy_ (u"࠭ࠧὣ")):
                    logger.warning(bstack11ll1_opy_ (u"ࠢࡓࡧࡳࡳࡸ࡯ࡴࡰࡴࡼࠤ࡚ࡘࡌࠡ࡫ࡶࠤࡲ࡯ࡳࡴ࡫ࡱ࡫ࠥ࡬࡯ࡳࠢࡶࡳࡺࡸࡣࡦࠢࠪࡿࢂ࠭࠺ࠡࡽࢀࠦὤ").format(name, bstack1111l11ll11_opy_))
                    continue
                if not bstack1111l11111l_opy_.match(name):
                    logger.warning(bstack11ll1_opy_ (u"ࠣࡋࡱࡺࡦࡲࡩࡥࠢࡶࡳࡺࡸࡣࡦࠢ࡬ࡨࡪࡴࡴࡪࡨ࡬ࡩࡷࠦࡦࡰࡴࡰࡥࡹࠦࡦࡰࡴࠣࠫࢀࢃࠧ࠻ࠢࡾࢁࠧὥ").format(name, bstack1111l11ll11_opy_))
                    continue
                if len(name) > 30 or len(name) < 1:
                    logger.warning(bstack11ll1_opy_ (u"ࠤࡖࡳࡺࡸࡣࡦࠢ࡬ࡨࡪࡴࡴࡪࡨ࡬ࡩࡷࠦࠧࡼࡿࠪࠤࡲࡻࡳࡵࠢ࡫ࡥࡻ࡫ࠠࡢࠢ࡯ࡩࡳ࡭ࡴࡩࠢࡥࡩࡹࡽࡥࡦࡰࠣ࠵ࠥࡧ࡮ࡥࠢ࠶࠴ࠥࡩࡨࡢࡴࡤࡧࡹ࡫ࡲࡴ࠰ࠥὦ").format(name))
                    continue
                bstack1111l11ll11_opy_ = bstack1111l11ll11_opy_.copy()
                bstack1111l11ll11_opy_[bstack11ll1_opy_ (u"ࠪࡲࡦࡳࡥࠨὧ")] = name
                bstack1111l11ll11_opy_[bstack11ll1_opy_ (u"ࠫ࡫࡫ࡡࡵࡷࡵࡩࡇࡸࡡ࡯ࡥ࡫ࠫὨ")] = bstack1111l11ll1l_opy_(name, bstack1111l11ll11_opy_)
                if not bstack1111l11ll11_opy_.get(bstack11ll1_opy_ (u"ࠬ࡬ࡥࡢࡶࡸࡶࡪࡈࡲࡢࡰࡦ࡬ࠬὩ")) or bstack1111l11ll11_opy_.get(bstack11ll1_opy_ (u"࠭ࡦࡦࡣࡷࡹࡷ࡫ࡂࡳࡣࡱࡧ࡭࠭Ὢ")) == bstack11ll1_opy_ (u"ࠧࠨὫ"):
                    logger.warning(bstack11ll1_opy_ (u"ࠣࡈࡨࡥࡹࡻࡲࡦࠢࡥࡶࡦࡴࡣࡩࠢࡱࡳࡹࠦࡳࡱࡧࡦ࡭࡫࡯ࡥࡥࠢࡩࡳࡷࠦࡳࡰࡷࡵࡧࡪࠦࠧࡼࡿࠪ࠾ࠥࢁࡽࠣὬ").format(name, bstack1111l11ll11_opy_))
                    continue
                if bstack1111l11ll11_opy_.get(bstack11ll1_opy_ (u"ࠩࡥࡥࡸ࡫ࡂࡳࡣࡱࡧ࡭࠭Ὥ")) and bstack1111l11ll11_opy_[bstack11ll1_opy_ (u"ࠪࡦࡦࡹࡥࡃࡴࡤࡲࡨ࡮ࠧὮ")] == bstack1111l11ll11_opy_[bstack11ll1_opy_ (u"ࠫ࡫࡫ࡡࡵࡷࡵࡩࡇࡸࡡ࡯ࡥ࡫ࠫὯ")]:
                    logger.warning(bstack11ll1_opy_ (u"ࠧࡌࡥࡢࡶࡸࡶࡪࠦࡢࡳࡣࡱࡧ࡭ࠦࡡ࡯ࡦࠣࡦࡦࡹࡥࠡࡤࡵࡥࡳࡩࡨࠡࡥࡤࡲࡳࡵࡴࠡࡤࡨࠤࡹ࡮ࡥࠡࡵࡤࡱࡪࠦࡦࡰࡴࠣࡷࡴࡻࡲࡤࡧࠣࠫࢀࢃࠧ࠻ࠢࡾࢁࠧὰ").format(name, bstack1111l11ll11_opy_))
                    continue
                bstack11111ll1ll1_opy_.append(bstack1111l11ll11_opy_)
            return bstack11111ll1ll1_opy_
        return data
    def bstack1111ll1ll1l_opy_(self):
        data = {
            bstack11ll1_opy_ (u"࠭ࡲࡶࡰࡢࡷࡲࡧࡲࡵࡡࡶࡩࡱ࡫ࡣࡵ࡫ࡲࡲࠬά"): {
                bstack11ll1_opy_ (u"ࠧࡦࡰࡤࡦࡱ࡫ࡤࠨὲ"): self.bstack1111l11llll_opy_(),
                bstack11ll1_opy_ (u"ࠨ࡯ࡲࡨࡪ࠭έ"): self.bstack1111l1l111l_opy_(),
                bstack11ll1_opy_ (u"ࠩࡶࡳࡺࡸࡣࡦࠩὴ"): self.bstack11111ll1lll_opy_()
            }
        }
        return data
    def bstack11111l1lll1_opy_(self, config):
        bstack11111lll1ll_opy_ = {}
        bstack11111lll1ll_opy_[bstack11ll1_opy_ (u"ࠪࡶࡺࡴ࡟ࡴ࡯ࡤࡶࡹࡥࡳࡦ࡮ࡨࡧࡹ࡯࡯࡯ࠩή")] = {
            bstack11ll1_opy_ (u"ࠫࡪࡴࡡࡣ࡮ࡨࡨࠬὶ"): self.bstack1111l11llll_opy_(),
            bstack11ll1_opy_ (u"ࠬࡳ࡯ࡥࡧࠪί"): self.bstack1111l1l111l_opy_()
        }
        bstack11111lll1ll_opy_[bstack11ll1_opy_ (u"࠭ࡲࡦࡴࡸࡲࡤࡶࡲࡦࡸ࡬ࡳࡺࡹ࡬ࡺࡡࡩࡥ࡮ࡲࡥࡥࠩὸ")] = {
            bstack11ll1_opy_ (u"ࠧࡦࡰࡤࡦࡱ࡫ࡤࠨό"): self.bstack1111l111111_opy_()
        }
        bstack11111lll1ll_opy_[bstack11ll1_opy_ (u"ࠨࡴࡸࡲࡤࡶࡲࡦࡸ࡬ࡳࡺࡹ࡬ࡺࡡࡩࡥ࡮ࡲࡥࡥࡡࡩ࡭ࡷࡹࡴࠨὺ")] = {
            bstack11ll1_opy_ (u"ࠩࡨࡲࡦࡨ࡬ࡦࡦࠪύ"): self.bstack11111l1ll1l_opy_()
        }
        bstack11111lll1ll_opy_[bstack11ll1_opy_ (u"ࠪࡷࡰ࡯ࡰࡠࡨࡤ࡭ࡱ࡯࡮ࡨࡡࡤࡲࡩࡥࡦ࡭ࡣ࡮ࡽࠬὼ")] = {
            bstack11ll1_opy_ (u"ࠫࡪࡴࡡࡣ࡮ࡨࡨࠬώ"): self.bstack1111l1ll1ll_opy_()
        }
        if self.bstack1ll11l11ll_opy_(config):
            bstack11111lll1ll_opy_[bstack11ll1_opy_ (u"ࠬࡸࡥࡵࡴࡼࡣࡹ࡫ࡳࡵࡵࡢࡳࡳࡥࡦࡢ࡫࡯ࡹࡷ࡫ࠧ὾")] = {
                bstack11ll1_opy_ (u"࠭ࡥ࡯ࡣࡥࡰࡪࡪࠧ὿"): True,
                bstack11ll1_opy_ (u"ࠧ࡮ࡣࡻࡣࡷ࡫ࡴࡳ࡫ࡨࡷࠬᾀ"): self.bstack1lllllll1l_opy_(config)
            }
        if self.bstack11l11l11111_opy_(config):
            bstack11111lll1ll_opy_[bstack11ll1_opy_ (u"ࠨࡣࡥࡳࡷࡺ࡟ࡣࡷ࡬ࡰࡩࡥ࡯࡯ࡡࡩࡥ࡮ࡲࡵࡳࡧࠪᾁ")] = {
                bstack11ll1_opy_ (u"ࠩࡨࡲࡦࡨ࡬ࡦࡦࠪᾂ"): True,
                bstack11ll1_opy_ (u"ࠪࡱࡦࡾ࡟ࡧࡣ࡬ࡰࡺࡸࡥࡴࠩᾃ"): self.bstack11l11l1l1l1_opy_(config)
            }
        return bstack11111lll1ll_opy_
    def bstack111llll111_opy_(self, config):
        bstack11ll1_opy_ (u"ࠦࠧࠨࠊࠡࠢࠣࠤࠥࠦࠠࠡࡅࡲࡰࡱ࡫ࡣࡵࡵࠣࡦࡺ࡯࡬ࡥࠢࡧࡥࡹࡧࠠࡣࡻࠣࡱࡦࡱࡩ࡯ࡩࠣࡥࠥࡩࡡ࡭࡮ࠣࡸࡴࠦࡴࡩࡧࠣࡧࡴࡲ࡬ࡦࡥࡷ࠱ࡧࡻࡩ࡭ࡦ࠰ࡨࡦࡺࡡࠡࡧࡱࡨࡵࡵࡩ࡯ࡶ࠱ࠎࠥࠦࠠࠡࠢࠣࠤࠥࡇࡲࡨࡵ࠽ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࡥࡹ࡮ࡲࡤࡠࡷࡸ࡭ࡩࠦࠨࡴࡶࡵ࠭࠿ࠦࡔࡩࡧ࡙࡚ࠣࡏࡄࠡࡱࡩࠤࡹ࡮ࡥࠡࡤࡸ࡭ࡱࡪࠠࡵࡱࠣࡧࡴࡲ࡬ࡦࡥࡷࠤࡩࡧࡴࡢࠢࡩࡳࡷ࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࡔࡨࡸࡺࡸ࡮ࡴ࠼ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࡦ࡬ࡧࡹࡀࠠࡓࡧࡶࡴࡴࡴࡳࡦࠢࡩࡶࡴࡳࠠࡵࡪࡨࠤࡨࡵ࡬࡭ࡧࡦࡸ࠲ࡨࡵࡪ࡮ࡧ࠱ࡩࡧࡴࡢࠢࡨࡲࡩࡶ࡯ࡪࡰࡷ࠰ࠥࡵࡲࠡࡐࡲࡲࡪࠦࡩࡧࠢࡩࡥ࡮ࡲࡥࡥ࠰ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠧࠨࠢᾄ")
        if not (config.get(bstack11ll1_opy_ (u"ࠬ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࠨᾅ"), None) in bstack11l1l1111l1_opy_ and self.bstack1111l11llll_opy_()):
            return None
        bstack1111l1l1l11_opy_ = os.environ.get(bstack11ll1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡕࡖࡋࡇࠫᾆ"), None)
        logger.debug(bstack11ll1_opy_ (u"ࠢ࡜ࡥࡲࡰࡱ࡫ࡣࡵࡄࡸ࡭ࡱࡪࡄࡢࡶࡤࡡࠥࡉ࡯࡭࡮ࡨࡧࡹ࡯࡮ࡨࠢࡥࡹ࡮ࡲࡤࠡࡦࡤࡸࡦࠦࡦࡰࡴࠣࡦࡺ࡯࡬ࡥࠢࡘ࡙ࡎࡊ࠺ࠡࡽࢀࠦᾇ").format(bstack1111l1l1l11_opy_))
        try:
            bstack11l1ll1ll1l_opy_ = bstack11ll1_opy_ (u"ࠣࡶࡨࡷࡹࡵࡲࡤࡪࡨࡷࡹࡸࡡࡵ࡫ࡲࡲ࠴ࡧࡰࡪ࠱ࡹ࠵࠴ࡨࡵࡪ࡮ࡧࡷ࠴ࢁࡽ࠰ࡥࡲࡰࡱ࡫ࡣࡵ࠯ࡥࡹ࡮ࡲࡤ࠮ࡦࡤࡸࡦࠨᾈ").format(bstack1111l1l1l11_opy_)
            payload = {
                bstack11ll1_opy_ (u"ࠤࡳࡶࡴࡰࡥࡤࡶࡑࡥࡲ࡫ࠢᾉ"): config.get(bstack11ll1_opy_ (u"ࠪࡴࡷࡵࡪࡦࡥࡷࡒࡦࡳࡥࠨᾊ"), bstack11ll1_opy_ (u"ࠫࠬᾋ")),
                bstack11ll1_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡒࡦࡳࡥࠣᾌ"): config.get(bstack11ll1_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡓࡧ࡭ࡦࠩᾍ"), os.path.basename(os.path.abspath(os.getcwd()))),
                bstack11ll1_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡘࡵ࡯ࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠧᾎ"): os.environ.get(bstack11ll1_opy_ (u"ࠣࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡃࡗࡌࡐࡉࡥࡒࡖࡐࡢࡍࡉࡋࡎࡕࡋࡉࡍࡊࡘࠢᾏ"), bstack11ll1_opy_ (u"ࠤࠥᾐ")),
                bstack11ll1_opy_ (u"ࠥࡲࡴࡪࡥࡊࡰࡧࡩࡽࠨᾑ"): int(os.environ.get(bstack11ll1_opy_ (u"ࠦࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡒࡔࡊࡅࡠࡋࡑࡈࡊ࡞ࠢᾒ")) or bstack11ll1_opy_ (u"ࠧ࠶ࠢᾓ")),
                bstack11ll1_opy_ (u"ࠨࡴࡰࡶࡤࡰࡓࡵࡤࡦࡵࠥᾔ"): int(os.environ.get(bstack11ll1_opy_ (u"ࠢࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡐࡖࡄࡐࡤࡔࡏࡅࡇࡢࡇࡔ࡛ࡎࡕࠤᾕ")) or bstack11ll1_opy_ (u"ࠣ࠳ࠥᾖ")),
                bstack11ll1_opy_ (u"ࠤ࡫ࡳࡸࡺࡉ࡯ࡨࡲࠦᾗ"): get_host_info(),
            }
            logger.debug(bstack11ll1_opy_ (u"ࠥ࡟ࡨࡵ࡬࡭ࡧࡦࡸࡇࡻࡩ࡭ࡦࡇࡥࡹࡧ࡝ࠡࡕࡨࡲࡩ࡯࡮ࡨࠢࡥࡹ࡮ࡲࡤࠡࡦࡤࡸࡦࠦࡰࡢࡻ࡯ࡳࡦࡪ࠺ࠡࡽࢀࠦᾘ").format(payload))
            response = bstack11l1ll1l11l_opy_.bstack11111l1l1l1_opy_(bstack11l1ll1ll1l_opy_, payload)
            if response:
                logger.debug(bstack11ll1_opy_ (u"ࠦࡠࡩ࡯࡭࡮ࡨࡧࡹࡈࡵࡪ࡮ࡧࡈࡦࡺࡡ࡞ࠢࡅࡹ࡮ࡲࡤࠡࡦࡤࡸࡦࠦࡣࡰ࡮࡯ࡩࡨࡺࡩࡰࡰࠣࡶࡪࡹࡰࡰࡰࡶࡩ࠿ࠦࡻࡾࠤᾙ").format(response))
                return response
            else:
                logger.error(bstack11ll1_opy_ (u"ࠧࡡࡣࡰ࡮࡯ࡩࡨࡺࡂࡶ࡫࡯ࡨࡉࡧࡴࡢ࡟ࠣࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦࡣࡰ࡮࡯ࡩࡨࡺࠠࡣࡷ࡬ࡰࡩࠦࡤࡢࡶࡤࠤ࡫ࡵࡲࠡࡤࡸ࡭ࡱࡪࠠࡖࡗࡌࡈ࠿ࠦࡻࡾࠤᾚ").format(bstack1111l1l1l11_opy_))
                return None
        except Exception as e:
            logger.error(bstack11ll1_opy_ (u"ࠨ࡛ࡤࡱ࡯ࡰࡪࡩࡴࡃࡷ࡬ࡰࡩࡊࡡࡵࡣࡠࠤࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡪࡰࠣࡧࡴࡲ࡬ࡦࡥࡷ࡭ࡳ࡭ࠠࡣࡷ࡬ࡰࡩࠦࡤࡢࡶࡤࠤ࡫ࡵࡲࠡࡤࡸ࡭ࡱࡪࠠࡖࡗࡌࡈࠥࢁࡽ࠻ࠢࡾࢁࠧᾛ").format(bstack1111l1l1l11_opy_, e))
            return None