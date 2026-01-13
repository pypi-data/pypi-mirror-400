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
from bstack_utils.constants import *
from browserstack_sdk.sdk_cli.cli import cli
from bstack_utils.bstack1111lll1111_opy_ import bstack1111ll1lll1_opy_
from bstack_utils.bstack1111l1ll_opy_ import bstack11llllll1l_opy_
from bstack_utils.helper import bstack1llll1ll1_opy_
import json
class bstack1ll11lll_opy_:
    _1ll11ll1lll_opy_ = None
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.bstack1111ll11ll1_opy_ = bstack1111ll1lll1_opy_(self.config, logger)
        self.bstack1111l1ll_opy_ = bstack11llllll1l_opy_.bstack11l1l11ll1_opy_(config=self.config)
        self.bstack1111lll111l_opy_ = {}
        self.bstack1llllllll11_opy_ = False
        self.bstack1111ll1ll11_opy_ = (
            self.__1111ll1l111_opy_()
            and self.bstack1111l1ll_opy_ is not None
            and self.bstack1111l1ll_opy_.bstack1llll1l111_opy_()
            and config.get(bstack11l1l_opy_ (u"࠭ࡰࡳࡱ࡭ࡩࡨࡺࡎࡢ࡯ࡨࠫἁ"), None) is not None
            and config.get(bstack11l1l_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡔࡡ࡮ࡧࠪἂ"), os.path.basename(os.getcwd())) is not None
        )
    @classmethod
    def bstack11l1l11ll1_opy_(cls, config, logger):
        if cls._1ll11ll1lll_opy_ is None and config is not None:
            cls._1ll11ll1lll_opy_ = bstack1ll11lll_opy_(config, logger)
        return cls._1ll11ll1lll_opy_
    def bstack1llll1l111_opy_(self):
        bstack11l1l_opy_ (u"ࠣࠤࠥࠎࠥࠦࠠࠡࠢࠣࠤࠥࡊ࡯ࠡࡰࡲࡸࠥࡧࡰࡱ࡮ࡼࠤࡹ࡫ࡳࡵࠢࡲࡶࡩ࡫ࡲࡪࡰࡪࠤࡼ࡮ࡥ࡯࠼ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦ࠭ࠡࡑ࠴࠵ࡾࠦࡩࡴࠢࡱࡳࡹࠦࡥ࡯ࡣࡥࡰࡪࡪࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣ࠱ࠥࡕࡲࡥࡧࡵ࡭ࡳ࡭ࠠࡪࡵࠣࡲࡴࡺࠠࡦࡰࡤࡦࡱ࡫ࡤࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤ࠲ࠦࡰࡳࡱ࡭ࡩࡨࡺࡎࡢ࡯ࡨࠤ࡮ࡹࠠࡏࡱࡱࡩࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡ࠯ࠣࡦࡺ࡯࡬ࡥࡐࡤࡱࡪࠦࡩࡴࠢࡑࡳࡳ࡫ࠊࠡࠢࠣࠤࠥࠦࠠࠡࠤࠥࠦἃ")
        return self.bstack1111ll1ll11_opy_ and self.bstack1111ll11l11_opy_()
    def bstack1111ll11l11_opy_(self):
        bstack1111ll111l1_opy_ = os.getenv(bstack11l1l_opy_ (u"ࠩࡉࡖࡆࡓࡅࡘࡑࡕࡏࡤ࡛ࡓࡆࡆࠪἄ"), self.config.get(bstack11l1l_opy_ (u"ࠪࡪࡷࡧ࡭ࡦࡹࡲࡶࡰ࠭ἅ"), None))
        return bstack1111ll111l1_opy_ in bstack11l11lll1l1_opy_
    def __1111ll1l111_opy_(self):
        bstack11l1l1ll11l_opy_ = False
        for fw in bstack11l1l111l11_opy_:
            if fw in self.config.get(bstack11l1l_opy_ (u"ࠫ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱࠧἆ"), bstack11l1l_opy_ (u"ࠬ࠭ἇ")):
                bstack11l1l1ll11l_opy_ = True
        return bstack1llll1ll1_opy_(self.config.get(bstack11l1l_opy_ (u"࠭ࡴࡦࡵࡷࡓࡧࡹࡥࡳࡸࡤࡦ࡮ࡲࡩࡵࡻࠪἈ"), bstack11l1l1ll11l_opy_))
    def bstack1111ll11lll_opy_(self):
        return (not self.bstack1llll1l111_opy_() and
                self.bstack1111l1ll_opy_ is not None and self.bstack1111l1ll_opy_.bstack1llll1l111_opy_())
    def bstack1111ll1llll_opy_(self):
        if not self.bstack1111ll11lll_opy_():
            return
        if self.config.get(bstack11l1l_opy_ (u"ࠧࡱࡴࡲ࡮ࡪࡩࡴࡏࡣࡰࡩࠬἉ"), None) is None or self.config.get(bstack11l1l_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠫἊ"), os.path.basename(os.getcwd())) is None:
            self.logger.info(bstack11l1l_opy_ (u"ࠤࡗࡩࡸࡺࠠࡓࡧࡲࡶࡩ࡫ࡲࡪࡰࡪࠤࡨࡧ࡮ࠨࡶࠣࡻࡴࡸ࡫ࠡࡣࡶࠤࡧࡻࡩ࡭ࡦࡑࡥࡲ࡫ࠠࡰࡴࠣࡴࡷࡵࡪࡦࡥࡷࡒࡦࡳࡥࠡ࡫ࡶࠤࡳࡻ࡬࡭࠰ࠣࡔࡱ࡫ࡡࡴࡧࠣࡷࡪࡺࠠࡢࠢࡱࡳࡳ࠳࡮ࡶ࡮࡯ࠤࡻࡧ࡬ࡶࡧ࠱ࠦἋ"))
        if not self.__1111ll1l111_opy_():
            self.logger.info(bstack11l1l_opy_ (u"ࠥࡘࡪࡹࡴࠡࡔࡨࡳࡷࡪࡥࡳ࡫ࡱ࡫ࠥࡩࡡ࡯ࠩࡷࠤࡼࡵࡲ࡬ࠢࡤࡷࠥࡺࡥࡴࡶࡕࡩࡵࡵࡲࡵ࡫ࡱ࡫ࠥ࡯ࡳࠡࡦ࡬ࡷࡦࡨ࡬ࡦࡦ࠱ࠤࡕࡲࡥࡢࡵࡨࠤࡪࡴࡡࡣ࡮ࡨࠤ࡮ࡺࠠࡧࡴࡲࡱࠥࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡾࡳ࡬ࠡࡨ࡬ࡰࡪ࠴ࠢἌ"))
    def bstack1111ll1ll1l_opy_(self):
        return self.bstack1llllllll11_opy_
    def bstack1lllllll11l_opy_(self, bstack1111ll1l1ll_opy_):
        self.bstack1llllllll11_opy_ = bstack1111ll1l1ll_opy_
        self.bstack111111l1l1_opy_(bstack11l1l_opy_ (u"ࠦࡦࡶࡰ࡭࡫ࡨࡨࠧἍ"), bstack1111ll1l1ll_opy_)
    def bstack111111111l_opy_(self, test_files):
        try:
            if test_files is None:
                self.logger.debug(bstack11l1l_opy_ (u"ࠧࡡࡲࡦࡱࡵࡨࡪࡸ࡟ࡵࡧࡶࡸࡤ࡬ࡩ࡭ࡧࡶࡡࠥࡔ࡯ࠡࡶࡨࡷࡹࠦࡦࡪ࡮ࡨࡷࠥࡶࡲࡰࡸ࡬ࡨࡪࡪࠠࡧࡱࡵࠤࡴࡸࡤࡦࡴ࡬ࡲ࡬࠴ࠢἎ"))
                return None
            orchestration_strategy = None
            orchestration_metadata = self.bstack1111l1ll_opy_.bstack1111ll1l11l_opy_()
            if self.bstack1111l1ll_opy_ is not None:
                orchestration_strategy = self.bstack1111l1ll_opy_.bstack111l1l1l_opy_()
            if orchestration_strategy is None:
                self.logger.error(bstack11l1l_opy_ (u"ࠨࡏࡳࡥ࡫ࡩࡸࡺࡲࡢࡶ࡬ࡳࡳࠦࡳࡵࡴࡤࡸࡪ࡭ࡹࠡ࡫ࡶࠤࡓࡵ࡮ࡦ࠰ࠣࡇࡦࡴ࡮ࡰࡶࠣࡴࡷࡵࡣࡦࡧࡧࠤࡼ࡯ࡴࡩࠢࡷࡩࡸࡺࠠࡰࡴࡦ࡬ࡪࡹࡴࡳࡣࡷ࡭ࡴࡴࠠࡴࡧࡶࡷ࡮ࡵ࡮࠯ࠤἏ"))
                return None
            self.logger.info(bstack11l1l_opy_ (u"ࠢࡓࡧࡲࡶࡩ࡫ࡲࡪࡰࡪࠤࡹ࡫ࡳࡵࠢࡩ࡭ࡱ࡫ࡳࠡࡹ࡬ࡸ࡭ࠦ࡯ࡳࡥ࡫ࡩࡸࡺࡲࡢࡶ࡬ࡳࡳࠦࡳࡵࡴࡤࡸࡪ࡭ࡹ࠻ࠢࡾࢁࠧἐ").format(orchestration_strategy))
            if cli.is_running():
                self.logger.debug(bstack11l1l_opy_ (u"ࠣࡗࡶ࡭ࡳ࡭ࠠࡄࡎࡌࠤ࡫ࡲ࡯ࡸࠢࡩࡳࡷࠦࡴࡦࡵࡷࠤ࡫࡯࡬ࡦࡵࠣࡳࡷࡩࡨࡦࡵࡷࡶࡦࡺࡩࡰࡰ࠱ࠦἑ"))
                ordered_test_files = cli.test_orchestration_session(test_files, orchestration_strategy, json.dumps(orchestration_metadata))
            else:
                self.logger.debug(bstack11l1l_opy_ (u"ࠤࡘࡷ࡮ࡴࡧࠡࡵࡧ࡯ࠥ࡬࡬ࡰࡹࠣࡪࡴࡸࠠࡵࡧࡶࡸࠥ࡬ࡩ࡭ࡧࡶࠤࡴࡸࡣࡩࡧࡶࡸࡷࡧࡴࡪࡱࡱ࠲ࠧἒ"))
                self.bstack1111ll11ll1_opy_.bstack1111ll11l1l_opy_(test_files, orchestration_strategy, orchestration_metadata)
                ordered_test_files = self.bstack1111ll11ll1_opy_.bstack1111ll111ll_opy_()
            if not ordered_test_files:
                return None
            self.bstack111111l1l1_opy_(bstack11l1l_opy_ (u"ࠥࡹࡵࡲ࡯ࡢࡦࡨࡨ࡙࡫ࡳࡵࡈ࡬ࡰࡪࡹࡃࡰࡷࡱࡸࠧἓ"), len(test_files))
            self.bstack111111l1l1_opy_(bstack11l1l_opy_ (u"ࠦࡳࡵࡤࡦࡋࡱࡨࡪࡾࠢἔ"), int(os.environ.get(bstack11l1l_opy_ (u"ࠧࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡓࡕࡄࡆࡡࡌࡒࡉࡋࡘࠣἕ")) or bstack11l1l_opy_ (u"ࠨ࠰ࠣ἖")))
            self.bstack111111l1l1_opy_(bstack11l1l_opy_ (u"ࠢࡵࡱࡷࡥࡱࡔ࡯ࡥࡧࡶࠦ἗"), int(os.environ.get(bstack11l1l_opy_ (u"ࠣࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡏࡑࡇࡉࡤࡉࡏࡖࡐࡗࠦἘ")) or bstack11l1l_opy_ (u"ࠤ࠴ࠦἙ")))
            self.bstack111111l1l1_opy_(bstack11l1l_opy_ (u"ࠥࡨࡴࡽ࡮࡭ࡱࡤࡨࡪࡪࡔࡦࡵࡷࡊ࡮ࡲࡥࡴࡅࡲࡹࡳࡺࠢἚ"), len(ordered_test_files))
            self.bstack111111l1l1_opy_(bstack11l1l_opy_ (u"ࠦࡸࡶ࡬ࡪࡶࡗࡩࡸࡺࡳࡂࡒࡌࡇࡦࡲ࡬ࡄࡱࡸࡲࡹࠨἛ"), self.bstack1111ll11ll1_opy_.bstack1111ll1l1l1_opy_())
            return ordered_test_files
        except Exception as e:
            self.logger.debug(bstack11l1l_opy_ (u"ࠧࡡࡲࡦࡱࡵࡨࡪࡸ࡟ࡵࡧࡶࡸࡤ࡬ࡩ࡭ࡧࡶࡡࠥࡋࡲࡳࡱࡵࠤ࡮ࡴࠠࡰࡴࡧࡩࡷ࡯࡮ࡨࠢࡷࡩࡸࡺࠠࡤ࡮ࡤࡷࡸ࡫ࡳ࠻ࠢࡾࢁࠧἜ").format(e))
        return None
    def bstack111111l1l1_opy_(self, key, value):
        self.bstack1111lll111l_opy_[key] = value
    def bstack1lllll11l_opy_(self):
        return self.bstack1111lll111l_opy_