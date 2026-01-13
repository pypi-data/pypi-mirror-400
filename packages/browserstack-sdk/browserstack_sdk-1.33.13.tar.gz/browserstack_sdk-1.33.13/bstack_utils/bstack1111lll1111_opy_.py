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
import time
from bstack_utils.bstack11l1ll11lll_opy_ import bstack11l1ll1l1ll_opy_
from bstack_utils.constants import bstack11l1l11111l_opy_
from bstack_utils.helper import get_host_info, bstack111ll11l111_opy_
class bstack1111ll1lll1_opy_:
    bstack11l1l_opy_ (u"ࠣࠤࠥࠎࠥࠦࠠࠡࡊࡤࡲࡩࡲࡥࡴࠢࡷࡩࡸࡺࠠࡰࡴࡧࡩࡷ࡯࡮ࡨࠢࡲࡶࡨ࡮ࡥࡴࡶࡵࡥࡹ࡯࡯࡯ࠢࡺ࡭ࡹ࡮ࠠࡵࡪࡨࠤࡇࡸ࡯ࡸࡵࡨࡶࡘࡺࡡࡤ࡭ࠣࡷࡪࡸࡶࡦࡴ࠱ࠎࠥࠦࠠࠡࠤࠥࠦ⅝")
    def __init__(self, config, logger):
        bstack11l1l_opy_ (u"ࠤࠥࠦࠏࠦࠠࠡࠢࠣࠤࠥࠦ࠺ࡱࡣࡵࡥࡲࠦࡣࡰࡰࡩ࡭࡬ࡀࠠࡥ࡫ࡦࡸ࠱ࠦࡴࡦࡵࡷࠤࡴࡸࡣࡩࡧࡶࡸࡷࡧࡴࡪࡱࡱࠤࡨࡵ࡮ࡧ࡫ࡪࠎࠥࠦࠠࠡࠢࠣࠤࠥࡀࡰࡢࡴࡤࡱࠥࡵࡲࡤࡪࡨࡷࡹࡸࡡࡵ࡫ࡲࡲࡤࡹࡴࡳࡣࡷࡩ࡬ࡿ࠺ࠡࡵࡷࡶ࠱ࠦࡴࡦࡵࡷࠤࡴࡸࡤࡦࡴ࡬ࡲ࡬ࠦࡳࡵࡴࡤࡸࡪ࡭ࡹࠡࡰࡤࡱࡪࠐࠠࠡࠢࠣࠤࠥࠦࠠࠣࠤࠥ⅞")
        self.config = config
        self.logger = logger
        self.bstack1lll1lllllll_opy_ = bstack11l1l_opy_ (u"ࠥࡸࡪࡹࡴࡰࡴࡦ࡬ࡪࡹࡴࡳࡣࡷ࡭ࡴࡴ࠯ࡢࡲ࡬࠳ࡻ࠷࠯ࡴࡲ࡯࡭ࡹ࠳ࡴࡦࡵࡷࡷࠧ⅟")
        self.bstack1llll1111111_opy_ = None
        self.bstack1llll111l111_opy_ = 60
        self.bstack1lll1llll1l1_opy_ = 5
        self.bstack1lll1lllll1l_opy_ = 0
    def bstack1111ll11l1l_opy_(self, test_files, orchestration_strategy, orchestration_metadata={}):
        bstack11l1l_opy_ (u"ࠦࠧࠨࠊࠡࠢࠣࠤࠥࠦࠠࠡࡋࡱ࡭ࡹ࡯ࡡࡵࡧࡶࠤࡹ࡮ࡥࠡࡵࡳࡰ࡮ࡺࠠࡵࡧࡶࡸࡸࠦࡲࡦࡳࡸࡩࡸࡺࠠࡢࡰࡧࠤࡸࡺ࡯ࡳࡧࡶࠤࡹ࡮ࡥࠡࡴࡨࡷࡵࡵ࡮ࡴࡧࠣࡨࡦࡺࡡࠡࡨࡲࡶࠥࡶ࡯࡭࡮࡬ࡲ࡬࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࠤࠥࠦⅠ")
        self.logger.debug(bstack11l1l_opy_ (u"ࠧࡡࡳࡱ࡮࡬ࡸ࡙࡫ࡳࡵࡵࡠࠤࡎࡴࡩࡵ࡫ࡤࡸ࡮ࡴࡧࠡࡵࡳࡰ࡮ࡺࠠࡵࡧࡶࡸࡸࠦࡷࡪࡶ࡫ࠤࡸࡺࡲࡢࡶࡨ࡫ࡾࡀࠠࡼࡿࠥⅡ").format(orchestration_strategy))
        try:
            bstack1lll1llll11l_opy_ = []
            bstack11l1l_opy_ (u"ࠨ࡙ࠢࠣࡨࠤࡼ࡯࡬࡭ࠢࡱࡳࡹࠦࡦࡦࡶࡦ࡬ࠥ࡭ࡩࡵࠢࡰࡩࡹࡧࡤࡢࡶࡤࠤ࡮ࡹࠠࡴࡱࡸࡶࡨ࡫ࠠࡪࡵࠣࡸࡾࡶࡥࠡࡱࡩࠤࡦࡸࡲࡢࡻࠣࡥࡳࡪࠠࡪࡶࠪࡷࠥ࡫࡬ࡦ࡯ࡨࡲࡹࡹࠠࡢࡴࡨࠤࡴ࡬ࠠࡵࡻࡳࡩࠥࡪࡩࡤࡶࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࡤࡨࡧࡦࡻࡳࡦࠢ࡬ࡲࠥࡺࡨࡢࡶࠣࡧࡦࡹࡥ࠭ࠢࡸࡷࡪࡸࠠࡩࡣࡶࠤࡵࡸ࡯ࡷ࡫ࡧࡩࡩࠦ࡭ࡶ࡮ࡷ࡭࠲ࡸࡥࡱࡱࠣࡷࡴࡻࡲࡤࡧࠣࡻ࡮ࡺࡨࠡࡨࡨࡥࡹࡻࡲࡦࡄࡵࡥࡳࡩࡨࠡ࡫ࡱࠤࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࠥࠦࠧⅢ")
            source = orchestration_metadata[bstack11l1l_opy_ (u"ࠧࡳࡷࡱࡣࡸࡳࡡࡳࡶࡢࡷࡪࡲࡥࡤࡶ࡬ࡳࡳ࠭Ⅳ")].get(bstack11l1l_opy_ (u"ࠨࡵࡲࡹࡷࡩࡥࠨⅤ"), [])
            bstack1llll1111lll_opy_ = isinstance(source, list) and all(isinstance(src, dict) and src is not None for src in source) and len(source) > 0
            if orchestration_metadata[bstack11l1l_opy_ (u"ࠩࡵࡹࡳࡥࡳ࡮ࡣࡵࡸࡤࡹࡥ࡭ࡧࡦࡸ࡮ࡵ࡮ࠨⅥ")].get(bstack11l1l_opy_ (u"ࠪࡩࡳࡧࡢ࡭ࡧࡧࠫⅦ"), False) and not bstack1llll1111lll_opy_:
                bstack1lll1llll11l_opy_ = bstack111ll11l111_opy_(source) # bstack1llll1111l1l_opy_-repo is handled bstack1lll1lllll11_opy_
            payload = {
                bstack11l1l_opy_ (u"ࠦࡹ࡫ࡳࡵࡵࠥⅧ"): [{bstack11l1l_opy_ (u"ࠧ࡬ࡩ࡭ࡧࡓࡥࡹ࡮ࠢⅨ"): f} for f in test_files],
                bstack11l1l_opy_ (u"ࠨ࡯ࡳࡥ࡫ࡩࡸࡺࡲࡢࡶ࡬ࡳࡳ࡙ࡴࡳࡣࡷࡩ࡬ࡿࠢⅩ"): orchestration_strategy,
                bstack11l1l_opy_ (u"ࠢࡰࡴࡦ࡬ࡪࡹࡴࡳࡣࡷ࡭ࡴࡴࡍࡦࡶࡤࡨࡦࡺࡡࠣⅪ"): orchestration_metadata,
                bstack11l1l_opy_ (u"ࠣࡰࡲࡨࡪࡏ࡮ࡥࡧࡻࠦⅫ"): int(os.environ.get(bstack11l1l_opy_ (u"ࠤࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡐࡒࡈࡊࡥࡉࡏࡆࡈ࡜ࠧⅬ")) or bstack11l1l_opy_ (u"ࠥ࠴ࠧⅭ")),
                bstack11l1l_opy_ (u"ࠦࡹࡵࡴࡢ࡮ࡑࡳࡩ࡫ࡳࠣⅮ"): int(os.environ.get(bstack11l1l_opy_ (u"ࠧࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡕࡔࡂࡎࡢࡒࡔࡊࡅࡠࡅࡒ࡙ࡓ࡚ࠢⅯ")) or bstack11l1l_opy_ (u"ࠨ࠱ࠣⅰ")),
                bstack11l1l_opy_ (u"ࠢࡱࡴࡲ࡮ࡪࡩࡴࡏࡣࡰࡩࠧⅱ"): self.config.get(bstack11l1l_opy_ (u"ࠨࡲࡵࡳ࡯࡫ࡣࡵࡐࡤࡱࡪ࠭ⅲ"), bstack11l1l_opy_ (u"ࠩࠪⅳ")),
                bstack11l1l_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡐࡤࡱࡪࠨⅴ"): self.config.get(bstack11l1l_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡑࡥࡲ࡫ࠧⅵ"), os.path.basename(os.path.abspath(os.getcwd()))),
                bstack11l1l_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡖࡺࡴࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠥⅶ"): os.environ.get(bstack11l1l_opy_ (u"ࠨࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡈࡕࡊࡎࡇࡣࡗ࡛ࡎࡠࡋࡇࡉࡓ࡚ࡉࡇࡋࡈࡖࠧⅷ"), bstack11l1l_opy_ (u"ࠢࠣⅸ")),
                bstack11l1l_opy_ (u"ࠣࡪࡲࡷࡹࡏ࡮ࡧࡱࠥⅹ"): get_host_info(),
                bstack11l1l_opy_ (u"ࠤࡳࡶࡉ࡫ࡴࡢ࡫࡯ࡷࠧⅺ"): bstack1lll1llll11l_opy_
            }
            self.logger.debug(bstack11l1l_opy_ (u"ࠥ࡟ࡸࡶ࡬ࡪࡶࡗࡩࡸࡺࡳ࡞ࠢࡖࡩࡳࡪࡩ࡯ࡩࠣࡸࡪࡹࡴࠡࡨ࡬ࡰࡪࡹ࠺ࠡࡽࢀࠦⅻ").format(payload))
            response = bstack11l1ll1l1ll_opy_.bstack1llll1l1l111_opy_(self.bstack1lll1lllllll_opy_, payload)
            if response:
                self.bstack1llll1111111_opy_ = self._1lll1llll1ll_opy_(response)
                self.logger.debug(bstack11l1l_opy_ (u"ࠦࡠࡹࡰ࡭࡫ࡷࡘࡪࡹࡴࡴ࡟ࠣࡗࡵࡲࡩࡵࠢࡷࡩࡸࡺࡳࠡࡴࡨࡷࡵࡵ࡮ࡴࡧ࠽ࠤࢀࢃࠢⅼ").format(self.bstack1llll1111111_opy_))
            else:
                self.logger.error(bstack11l1l_opy_ (u"ࠧࡡࡳࡱ࡮࡬ࡸ࡙࡫ࡳࡵࡵࡠࠤࡋࡧࡩ࡭ࡧࡧࠤࡹࡵࠠࡨࡧࡷࠤࡸࡶ࡬ࡪࡶࠣࡸࡪࡹࡴࡴࠢࡵࡩࡸࡶ࡯࡯ࡵࡨ࠲ࠧⅽ"))
        except Exception as e:
            self.logger.error(bstack11l1l_opy_ (u"ࠨ࡛ࡴࡲ࡯࡭ࡹ࡚ࡥࡴࡶࡶࡡࠥࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡ࡫ࡱࠤࡸ࡫࡮ࡥ࡫ࡱ࡫ࠥࡺࡥࡴࡶࠣࡪ࡮ࡲࡥࡴ࠼࠽ࠤࢀࢃࠢⅾ").format(e))
    def _1lll1llll1ll_opy_(self, response):
        bstack11l1l_opy_ (u"ࠢࠣࠤࠍࠤࠥࠦࠠࠡࠢࠣࠤࡕࡸ࡯ࡤࡧࡶࡷࡪࡹࠠࡵࡪࡨࠤࡸࡶ࡬ࡪࡶࠣࡸࡪࡹࡴࡴࠢࡄࡔࡎࠦࡲࡦࡵࡳࡳࡳࡹࡥࠡࡣࡱࡨࠥ࡫ࡸࡵࡴࡤࡧࡹࡹࠠࡳࡧ࡯ࡩࡻࡧ࡮ࡵࠢࡩ࡭ࡪࡲࡤࡴ࠰ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠧࠨࠢⅿ")
        bstack11111ll1_opy_ = {}
        bstack11111ll1_opy_[bstack11l1l_opy_ (u"ࠣࡶ࡬ࡱࡪࡵࡵࡵࠤↀ")] = response.get(bstack11l1l_opy_ (u"ࠤࡷ࡭ࡲ࡫࡯ࡶࡶࠥↁ"), self.bstack1llll111l111_opy_)
        bstack11111ll1_opy_[bstack11l1l_opy_ (u"ࠥࡸ࡮ࡳࡥࡰࡷࡷࡍࡳࡺࡥࡳࡸࡤࡰࠧↂ")] = response.get(bstack11l1l_opy_ (u"ࠦࡹ࡯࡭ࡦࡱࡸࡸࡎࡴࡴࡦࡴࡹࡥࡱࠨↃ"), self.bstack1lll1llll1l1_opy_)
        bstack1llll11111ll_opy_ = response.get(bstack11l1l_opy_ (u"ࠧࡸࡥࡴࡷ࡯ࡸ࡚ࡸ࡬ࠣↄ"))
        bstack1llll111l11l_opy_ = response.get(bstack11l1l_opy_ (u"ࠨࡴࡪ࡯ࡨࡳࡺࡺࡕࡳ࡮ࠥↅ"))
        if bstack1llll11111ll_opy_:
            bstack11111ll1_opy_[bstack11l1l_opy_ (u"ࠢࡳࡧࡶࡹࡱࡺࡕࡳ࡮ࠥↆ")] = bstack1llll11111ll_opy_.split(bstack11l1l11111l_opy_ + bstack11l1l_opy_ (u"ࠣ࠱ࠥↇ"))[1] if bstack11l1l11111l_opy_ + bstack11l1l_opy_ (u"ࠤ࠲ࠦↈ") in bstack1llll11111ll_opy_ else bstack1llll11111ll_opy_
        else:
            bstack11111ll1_opy_[bstack11l1l_opy_ (u"ࠥࡶࡪࡹࡵ࡭ࡶࡘࡶࡱࠨ↉")] = None
        if bstack1llll111l11l_opy_:
            bstack11111ll1_opy_[bstack11l1l_opy_ (u"ࠦࡹ࡯࡭ࡦࡱࡸࡸ࡚ࡸ࡬ࠣ↊")] = bstack1llll111l11l_opy_.split(bstack11l1l11111l_opy_ + bstack11l1l_opy_ (u"ࠧ࠵ࠢ↋"))[1] if bstack11l1l11111l_opy_ + bstack11l1l_opy_ (u"ࠨ࠯ࠣ↌") in bstack1llll111l11l_opy_ else bstack1llll111l11l_opy_
        else:
            bstack11111ll1_opy_[bstack11l1l_opy_ (u"ࠢࡵ࡫ࡰࡩࡴࡻࡴࡖࡴ࡯ࠦ↍")] = None
        if (
            response.get(bstack11l1l_opy_ (u"ࠣࡶ࡬ࡱࡪࡵࡵࡵࠤ↎")) is None or
            response.get(bstack11l1l_opy_ (u"ࠤࡷ࡭ࡲ࡫࡯ࡶࡶࡌࡲࡹ࡫ࡲࡷࡣ࡯ࠦ↏")) is None or
            response.get(bstack11l1l_opy_ (u"ࠥࡸ࡮ࡳࡥࡰࡷࡷ࡙ࡷࡲࠢ←")) is None or
            response.get(bstack11l1l_opy_ (u"ࠦࡷ࡫ࡳࡶ࡮ࡷ࡙ࡷࡲࠢ↑")) is None
        ):
            self.logger.debug(bstack11l1l_opy_ (u"ࠧࡡࡰࡳࡱࡦࡩࡸࡹ࡟ࡴࡲ࡯࡭ࡹࡥࡴࡦࡵࡷࡷࡤࡸࡥࡴࡲࡲࡲࡸ࡫࡝ࠡࡔࡨࡧࡪ࡯ࡶࡦࡦࠣࡲࡺࡲ࡬ࠡࡸࡤࡰࡺ࡫ࠨࡴࠫࠣࡪࡴࡸࠠࡴࡱࡰࡩࠥࡧࡴࡵࡴ࡬ࡦࡺࡺࡥࡴࠢ࡬ࡲࠥࡹࡰ࡭࡫ࡷࠤࡹ࡫ࡳࡵࡵࠣࡅࡕࡏࠠࡳࡧࡶࡴࡴࡴࡳࡦࠤ→"))
        return bstack11111ll1_opy_
    def bstack1111ll111ll_opy_(self):
        if not self.bstack1llll1111111_opy_:
            self.logger.error(bstack11l1l_opy_ (u"ࠨ࡛ࡨࡧࡷࡓࡷࡪࡥࡳࡧࡧࡘࡪࡹࡴࡇ࡫࡯ࡩࡸࡣࠠࡏࡱࠣࡶࡪࡷࡵࡦࡵࡷࠤࡩࡧࡴࡢࠢࡤࡺࡦ࡯࡬ࡢࡤ࡯ࡩࠥࡺ࡯ࠡࡨࡨࡸࡨ࡮ࠠࡰࡴࡧࡩࡷ࡫ࡤࠡࡶࡨࡷࡹࠦࡦࡪ࡮ࡨࡷ࠳ࠨ↓"))
            return None
        bstack1llll11111l1_opy_ = None
        test_files = []
        bstack1llll1111l11_opy_ = int(time.time() * 1000) # bstack1llll1111ll1_opy_ sec
        bstack1lll1llllll1_opy_ = int(self.bstack1llll1111111_opy_.get(bstack11l1l_opy_ (u"ࠢࡵ࡫ࡰࡩࡴࡻࡴࡊࡰࡷࡩࡷࡼࡡ࡭ࠤ↔"), self.bstack1lll1llll1l1_opy_))
        bstack1llll111111l_opy_ = int(self.bstack1llll1111111_opy_.get(bstack11l1l_opy_ (u"ࠣࡶ࡬ࡱࡪࡵࡵࡵࠤ↕"), self.bstack1llll111l111_opy_)) * 1000
        bstack1llll111l11l_opy_ = self.bstack1llll1111111_opy_.get(bstack11l1l_opy_ (u"ࠤࡷ࡭ࡲ࡫࡯ࡶࡶࡘࡶࡱࠨ↖"), None)
        bstack1llll11111ll_opy_ = self.bstack1llll1111111_opy_.get(bstack11l1l_opy_ (u"ࠥࡶࡪࡹࡵ࡭ࡶࡘࡶࡱࠨ↗"), None)
        if bstack1llll11111ll_opy_ is None and bstack1llll111l11l_opy_ is None:
            return None
        try:
            while bstack1llll11111ll_opy_ and (time.time() * 1000 - bstack1llll1111l11_opy_) < bstack1llll111111l_opy_:
                response = bstack11l1ll1l1ll_opy_.bstack1llll1l1l11l_opy_(bstack1llll11111ll_opy_, {})
                if response and response.get(bstack11l1l_opy_ (u"ࠦࡹ࡫ࡳࡵࡵࠥ↘")):
                    bstack1llll11111l1_opy_ = response.get(bstack11l1l_opy_ (u"ࠧࡺࡥࡴࡶࡶࠦ↙"))
                self.bstack1lll1lllll1l_opy_ += 1
                if bstack1llll11111l1_opy_:
                    break
                time.sleep(bstack1lll1llllll1_opy_)
                self.logger.debug(bstack11l1l_opy_ (u"ࠨ࡛ࡨࡧࡷࡓࡷࡪࡥࡳࡧࡧࡘࡪࡹࡴࡇ࡫࡯ࡩࡸࡣࠠࡇࡧࡷࡧ࡭࡯࡮ࡨࠢࡲࡶࡩ࡫ࡲࡦࡦࠣࡸࡪࡹࡴࡴࠢࡩࡶࡴࡳࠠࡳࡧࡶࡹࡱࡺࠠࡖࡔࡏࠤࡦ࡬ࡴࡦࡴࠣࡻࡦ࡯ࡴࡪࡰࡪࠤ࡫ࡵࡲࠡࡽࢀࠤࡸ࡫ࡣࡰࡰࡧࡷ࠳ࠨ↚").format(bstack1lll1llllll1_opy_))
            if bstack1llll111l11l_opy_ and not bstack1llll11111l1_opy_:
                self.logger.debug(bstack11l1l_opy_ (u"ࠢ࡜ࡩࡨࡸࡔࡸࡤࡦࡴࡨࡨ࡙࡫ࡳࡵࡈ࡬ࡰࡪࡹ࡝ࠡࡈࡨࡸࡨ࡮ࡩ࡯ࡩࠣࡳࡷࡪࡥࡳࡧࡧࠤࡹ࡫ࡳࡵࡵࠣࡪࡷࡵ࡭ࠡࡶ࡬ࡱࡪࡵࡵࡵࠢࡘࡖࡑࠨ↛"))
                response = bstack11l1ll1l1ll_opy_.bstack1llll1l1l11l_opy_(bstack1llll111l11l_opy_, {})
                if response and response.get(bstack11l1l_opy_ (u"ࠣࡶࡨࡷࡹࡹࠢ↜")):
                    bstack1llll11111l1_opy_ = response.get(bstack11l1l_opy_ (u"ࠤࡷࡩࡸࡺࡳࠣ↝"))
            if bstack1llll11111l1_opy_ and len(bstack1llll11111l1_opy_) > 0:
                for bstack111l1lllll_opy_ in bstack1llll11111l1_opy_:
                    file_path = bstack111l1lllll_opy_.get(bstack11l1l_opy_ (u"ࠥࡪ࡮ࡲࡥࡑࡣࡷ࡬ࠧ↞"))
                    if file_path:
                        test_files.append(file_path)
            if not bstack1llll11111l1_opy_:
                return None
            self.logger.debug(bstack11l1l_opy_ (u"ࠦࡠ࡭ࡥࡵࡑࡵࡨࡪࡸࡥࡥࡖࡨࡷࡹࡌࡩ࡭ࡧࡶࡡࠥࡕࡲࡥࡧࡵࡩࡩࠦࡴࡦࡵࡷࠤ࡫࡯࡬ࡦࡵࠣࡶࡪࡩࡥࡪࡸࡨࡨ࠿ࠦࡻࡾࠤ↟").format(test_files))
            return test_files
        except Exception as e:
            self.logger.error(bstack11l1l_opy_ (u"ࠧࡡࡧࡦࡶࡒࡶࡩ࡫ࡲࡦࡦࡗࡩࡸࡺࡆࡪ࡮ࡨࡷࡢࠦࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢ࡬ࡲࠥ࡬ࡥࡵࡥ࡫࡭ࡳ࡭ࠠࡰࡴࡧࡩࡷ࡫ࡤࠡࡶࡨࡷࡹࠦࡦࡪ࡮ࡨࡷ࠿ࠦࡻࡾࠤ↠").format(e))
            return None
    def bstack1111ll1l1l1_opy_(self):
        bstack11l1l_opy_ (u"ࠨࠢࠣࠌࠣࠤࠥࠦࠠࠡࠢࠣࡖࡪࡺࡵࡳࡰࡶࠤࡹ࡮ࡥࠡࡥࡲࡹࡳࡺࠠࡰࡨࠣࡷࡵࡲࡩࡵࠢࡷࡩࡸࡺࡳࠡࡃࡓࡍࠥࡩࡡ࡭࡮ࡶࠤࡲࡧࡤࡦ࠰ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠧࠨࠢ↡")
        return self.bstack1lll1lllll1l_opy_