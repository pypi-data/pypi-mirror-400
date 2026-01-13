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
from bstack_utils.constants import *
from browserstack_sdk.sdk_cli.cli import cli
from bstack_utils.bstack1111lll111l_opy_ import bstack1111ll1lll1_opy_
from bstack_utils.bstack11l111l1_opy_ import bstack1lll1lll_opy_
from bstack_utils.helper import bstack1111lll1_opy_
import json
class bstack1l1111111l_opy_:
    _1l1l1ll11l1_opy_ = None
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.bstack1111ll1l1ll_opy_ = bstack1111ll1lll1_opy_(self.config, logger)
        self.bstack11l111l1_opy_ = bstack1lll1lll_opy_.bstack1l1l1111_opy_(config=self.config)
        self.bstack1111ll1ll11_opy_ = {}
        self.bstack1llllll1l11_opy_ = False
        self.bstack1111ll111ll_opy_ = (
            self.__1111ll1l1l1_opy_()
            and self.bstack11l111l1_opy_ is not None
            and self.bstack11l111l1_opy_.bstack1l1l1ll11_opy_()
            and config.get(bstack11ll1_opy_ (u"ࠧࡱࡴࡲ࡮ࡪࡩࡴࡏࡣࡰࡩࠬἂ"), None) is not None
            and config.get(bstack11ll1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠫἃ"), os.path.basename(os.getcwd())) is not None
        )
    @classmethod
    def bstack1l1l1111_opy_(cls, config, logger):
        if cls._1l1l1ll11l1_opy_ is None and config is not None:
            cls._1l1l1ll11l1_opy_ = bstack1l1111111l_opy_(config, logger)
        return cls._1l1l1ll11l1_opy_
    def bstack1l1l1ll11_opy_(self):
        bstack11ll1_opy_ (u"ࠤࠥࠦࠏࠦࠠࠡࠢࠣࠤࠥࠦࡄࡰࠢࡱࡳࡹࠦࡡࡱࡲ࡯ࡽࠥࡺࡥࡴࡶࠣࡳࡷࡪࡥࡳ࡫ࡱ࡫ࠥࡽࡨࡦࡰ࠽ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠ࠮ࠢࡒ࠵࠶ࡿࠠࡪࡵࠣࡲࡴࡺࠠࡦࡰࡤࡦࡱ࡫ࡤࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤ࠲ࠦࡏࡳࡦࡨࡶ࡮ࡴࡧࠡ࡫ࡶࠤࡳࡵࡴࠡࡧࡱࡥࡧࡲࡥࡥࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥ࠳ࠠࡱࡴࡲ࡮ࡪࡩࡴࡏࡣࡰࡩࠥ࡯ࡳࠡࡐࡲࡲࡪࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢ࠰ࠤࡧࡻࡩ࡭ࡦࡑࡥࡲ࡫ࠠࡪࡵࠣࡒࡴࡴࡥࠋࠢࠣࠤࠥࠦࠠࠡࠢࠥࠦࠧἄ")
        return self.bstack1111ll111ll_opy_ and self.bstack1111ll1llll_opy_()
    def bstack1111ll1llll_opy_(self):
        bstack1111ll11l11_opy_ = os.getenv(bstack11ll1_opy_ (u"ࠪࡊࡗࡇࡍࡆ࡙ࡒࡖࡐࡥࡕࡔࡇࡇࠫἅ"), self.config.get(bstack11ll1_opy_ (u"ࠫ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱࠧἆ"), None))
        return bstack1111ll11l11_opy_ in bstack11l1l1111l1_opy_
    def __1111ll1l1l1_opy_(self):
        bstack11l1l1ll1ll_opy_ = False
        for fw in bstack11l1l111lll_opy_:
            if fw in self.config.get(bstack11ll1_opy_ (u"ࠬ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࠨἇ"), bstack11ll1_opy_ (u"࠭ࠧἈ")):
                bstack11l1l1ll1ll_opy_ = True
        return bstack1111lll1_opy_(self.config.get(bstack11ll1_opy_ (u"ࠧࡵࡧࡶࡸࡔࡨࡳࡦࡴࡹࡥࡧ࡯࡬ࡪࡶࡼࠫἉ"), bstack11l1l1ll1ll_opy_))
    def bstack1111ll1l111_opy_(self):
        return (not self.bstack1l1l1ll11_opy_() and
                self.bstack11l111l1_opy_ is not None and self.bstack11l111l1_opy_.bstack1l1l1ll11_opy_())
    def bstack1111lll1111_opy_(self):
        if not self.bstack1111ll1l111_opy_():
            return
        if self.config.get(bstack11ll1_opy_ (u"ࠨࡲࡵࡳ࡯࡫ࡣࡵࡐࡤࡱࡪ࠭Ἂ"), None) is None or self.config.get(bstack11ll1_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡏࡣࡰࡩࠬἋ"), os.path.basename(os.getcwd())) is None:
            self.logger.info(bstack11ll1_opy_ (u"ࠥࡘࡪࡹࡴࠡࡔࡨࡳࡷࡪࡥࡳ࡫ࡱ࡫ࠥࡩࡡ࡯ࠩࡷࠤࡼࡵࡲ࡬ࠢࡤࡷࠥࡨࡵࡪ࡮ࡧࡒࡦࡳࡥࠡࡱࡵࠤࡵࡸ࡯࡫ࡧࡦࡸࡓࡧ࡭ࡦࠢ࡬ࡷࠥࡴࡵ࡭࡮࠱ࠤࡕࡲࡥࡢࡵࡨࠤࡸ࡫ࡴࠡࡣࠣࡲࡴࡴ࠭࡯ࡷ࡯ࡰࠥࡼࡡ࡭ࡷࡨ࠲ࠧἌ"))
        if not self.__1111ll1l1l1_opy_():
            self.logger.info(bstack11ll1_opy_ (u"࡙ࠦ࡫ࡳࡵࠢࡕࡩࡴࡸࡤࡦࡴ࡬ࡲ࡬ࠦࡣࡢࡰࠪࡸࠥࡽ࡯ࡳ࡭ࠣࡥࡸࠦࡴࡦࡵࡷࡖࡪࡶ࡯ࡳࡶ࡬ࡲ࡬ࠦࡩࡴࠢࡧ࡭ࡸࡧࡢ࡭ࡧࡧ࠲ࠥࡖ࡬ࡦࡣࡶࡩࠥ࡫࡮ࡢࡤ࡯ࡩࠥ࡯ࡴࠡࡨࡵࡳࡲࠦࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡿ࡭࡭ࠢࡩ࡭ࡱ࡫࠮ࠣἍ"))
    def bstack1111ll11l1l_opy_(self):
        return self.bstack1llllll1l11_opy_
    def bstack1lllllll1l1_opy_(self, bstack1111ll1l11l_opy_):
        self.bstack1llllll1l11_opy_ = bstack1111ll1l11l_opy_
        self.bstack1lllllll111_opy_(bstack11ll1_opy_ (u"ࠧࡧࡰࡱ࡮࡬ࡩࡩࠨἎ"), bstack1111ll1l11l_opy_)
    def bstack111111l1l1_opy_(self, test_files):
        try:
            if test_files is None:
                self.logger.debug(bstack11ll1_opy_ (u"ࠨ࡛ࡳࡧࡲࡶࡩ࡫ࡲࡠࡶࡨࡷࡹࡥࡦࡪ࡮ࡨࡷࡢࠦࡎࡰࠢࡷࡩࡸࡺࠠࡧ࡫࡯ࡩࡸࠦࡰࡳࡱࡹ࡭ࡩ࡫ࡤࠡࡨࡲࡶࠥࡵࡲࡥࡧࡵ࡭ࡳ࡭࠮ࠣἏ"))
                return None
            orchestration_strategy = None
            orchestration_metadata = self.bstack11l111l1_opy_.bstack1111ll1ll1l_opy_()
            if self.bstack11l111l1_opy_ is not None:
                orchestration_strategy = self.bstack11l111l1_opy_.bstack111llll11_opy_()
            if orchestration_strategy is None:
                self.logger.error(bstack11ll1_opy_ (u"ࠢࡐࡴࡦ࡬ࡪࡹࡴࡳࡣࡷ࡭ࡴࡴࠠࡴࡶࡵࡥࡹ࡫ࡧࡺࠢ࡬ࡷࠥࡔ࡯࡯ࡧ࠱ࠤࡈࡧ࡮࡯ࡱࡷࠤࡵࡸ࡯ࡤࡧࡨࡨࠥࡽࡩࡵࡪࠣࡸࡪࡹࡴࠡࡱࡵࡧ࡭࡫ࡳࡵࡴࡤࡸ࡮ࡵ࡮ࠡࡵࡨࡷࡸ࡯࡯࡯࠰ࠥἐ"))
                return None
            self.logger.info(bstack11ll1_opy_ (u"ࠣࡔࡨࡳࡷࡪࡥࡳ࡫ࡱ࡫ࠥࡺࡥࡴࡶࠣࡪ࡮ࡲࡥࡴࠢࡺ࡭ࡹ࡮ࠠࡰࡴࡦ࡬ࡪࡹࡴࡳࡣࡷ࡭ࡴࡴࠠࡴࡶࡵࡥࡹ࡫ࡧࡺ࠼ࠣࡿࢂࠨἑ").format(orchestration_strategy))
            if cli.is_running():
                self.logger.debug(bstack11ll1_opy_ (u"ࠤࡘࡷ࡮ࡴࡧࠡࡅࡏࡍࠥ࡬࡬ࡰࡹࠣࡪࡴࡸࠠࡵࡧࡶࡸࠥ࡬ࡩ࡭ࡧࡶࠤࡴࡸࡣࡩࡧࡶࡸࡷࡧࡴࡪࡱࡱ࠲ࠧἒ"))
                ordered_test_files = cli.test_orchestration_session(test_files, orchestration_strategy, json.dumps(orchestration_metadata))
            else:
                self.logger.debug(bstack11ll1_opy_ (u"࡙ࠥࡸ࡯࡮ࡨࠢࡶࡨࡰࠦࡦ࡭ࡱࡺࠤ࡫ࡵࡲࠡࡶࡨࡷࡹࠦࡦࡪ࡮ࡨࡷࠥࡵࡲࡤࡪࡨࡷࡹࡸࡡࡵ࡫ࡲࡲ࠳ࠨἓ"))
                self.bstack1111ll1l1ll_opy_.bstack1111ll11lll_opy_(test_files, orchestration_strategy, orchestration_metadata)
                ordered_test_files = self.bstack1111ll1l1ll_opy_.bstack1111ll111l1_opy_()
            if not ordered_test_files:
                return None
            self.bstack1lllllll111_opy_(bstack11ll1_opy_ (u"ࠦࡺࡶ࡬ࡰࡣࡧࡩࡩ࡚ࡥࡴࡶࡉ࡭ࡱ࡫ࡳࡄࡱࡸࡲࡹࠨἔ"), len(test_files))
            self.bstack1lllllll111_opy_(bstack11ll1_opy_ (u"ࠧࡴ࡯ࡥࡧࡌࡲࡩ࡫ࡸࠣἕ"), int(os.environ.get(bstack11ll1_opy_ (u"ࠨࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡔࡏࡅࡇࡢࡍࡓࡊࡅ࡙ࠤ἖")) or bstack11ll1_opy_ (u"ࠢ࠱ࠤ἗")))
            self.bstack1lllllll111_opy_(bstack11ll1_opy_ (u"ࠣࡶࡲࡸࡦࡲࡎࡰࡦࡨࡷࠧἘ"), int(os.environ.get(bstack11ll1_opy_ (u"ࠤࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡐࡒࡈࡊࡥࡃࡐࡗࡑࡘࠧἙ")) or bstack11ll1_opy_ (u"ࠥ࠵ࠧἚ")))
            self.bstack1lllllll111_opy_(bstack11ll1_opy_ (u"ࠦࡩࡵࡷ࡯࡮ࡲࡥࡩ࡫ࡤࡕࡧࡶࡸࡋ࡯࡬ࡦࡵࡆࡳࡺࡴࡴࠣἛ"), len(ordered_test_files))
            self.bstack1lllllll111_opy_(bstack11ll1_opy_ (u"ࠧࡹࡰ࡭࡫ࡷࡘࡪࡹࡴࡴࡃࡓࡍࡈࡧ࡬࡭ࡅࡲࡹࡳࡺࠢἜ"), self.bstack1111ll1l1ll_opy_.bstack1111ll11ll1_opy_())
            return ordered_test_files
        except Exception as e:
            self.logger.debug(bstack11ll1_opy_ (u"ࠨ࡛ࡳࡧࡲࡶࡩ࡫ࡲࡠࡶࡨࡷࡹࡥࡦࡪ࡮ࡨࡷࡢࠦࡅࡳࡴࡲࡶࠥ࡯࡮ࠡࡱࡵࡨࡪࡸࡩ࡯ࡩࠣࡸࡪࡹࡴࠡࡥ࡯ࡥࡸࡹࡥࡴ࠼ࠣࡿࢂࠨἝ").format(e))
        return None
    def bstack1lllllll111_opy_(self, key, value):
        self.bstack1111ll1ll11_opy_[key] = value
    def bstack1l1llll1l_opy_(self):
        return self.bstack1111ll1ll11_opy_