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
import time
from bstack_utils.bstack11l1ll1l1l1_opy_ import bstack11l1ll1l11l_opy_
from bstack_utils.constants import bstack11l11lll1l1_opy_
from bstack_utils.helper import get_host_info, bstack111lll11111_opy_
class bstack1111ll1lll1_opy_:
    bstack11ll1_opy_ (u"ࠤࠥࠦࠏࠦࠠࠡࠢࡋࡥࡳࡪ࡬ࡦࡵࠣࡸࡪࡹࡴࠡࡱࡵࡨࡪࡸࡩ࡯ࡩࠣࡳࡷࡩࡨࡦࡵࡷࡶࡦࡺࡩࡰࡰࠣࡻ࡮ࡺࡨࠡࡶ࡫ࡩࠥࡈࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࠤࡸ࡫ࡲࡷࡧࡵ࠲ࠏࠦࠠࠡࠢࠥࠦࠧ⅞")
    def __init__(self, config, logger):
        bstack11ll1_opy_ (u"ࠥࠦࠧࠐࠠࠡࠢࠣࠤࠥࠦࠠ࠻ࡲࡤࡶࡦࡳࠠࡤࡱࡱࡪ࡮࡭࠺ࠡࡦ࡬ࡧࡹ࠲ࠠࡵࡧࡶࡸࠥࡵࡲࡤࡪࡨࡷࡹࡸࡡࡵ࡫ࡲࡲࠥࡩ࡯࡯ࡨ࡬࡫ࠏࠦࠠࠡࠢࠣࠤࠥࠦ࠺ࡱࡣࡵࡥࡲࠦ࡯ࡳࡥ࡫ࡩࡸࡺࡲࡢࡶ࡬ࡳࡳࡥࡳࡵࡴࡤࡸࡪ࡭ࡹ࠻ࠢࡶࡸࡷ࠲ࠠࡵࡧࡶࡸࠥࡵࡲࡥࡧࡵ࡭ࡳ࡭ࠠࡴࡶࡵࡥࡹ࡫ࡧࡺࠢࡱࡥࡲ࡫ࠊࠡࠢࠣࠤࠥࠦࠠࠡࠤࠥࠦ⅟")
        self.config = config
        self.logger = logger
        self.bstack1llll1111111_opy_ = bstack11ll1_opy_ (u"ࠦࡹ࡫ࡳࡵࡱࡵࡧ࡭࡫ࡳࡵࡴࡤࡸ࡮ࡵ࡮࠰ࡣࡳ࡭࠴ࡼ࠱࠰ࡵࡳࡰ࡮ࡺ࠭ࡵࡧࡶࡸࡸࠨⅠ")
        self.bstack1llll111l11l_opy_ = None
        self.bstack1llll11111l1_opy_ = 60
        self.bstack1llll111111l_opy_ = 5
        self.bstack1lll1lllll1l_opy_ = 0
    def bstack1111ll11lll_opy_(self, test_files, orchestration_strategy, orchestration_metadata={}):
        bstack11ll1_opy_ (u"ࠧࠨࠢࠋࠢࠣࠤࠥࠦࠠࠡࠢࡌࡲ࡮ࡺࡩࡢࡶࡨࡷࠥࡺࡨࡦࠢࡶࡴࡱ࡯ࡴࠡࡶࡨࡷࡹࡹࠠࡳࡧࡴࡹࡪࡹࡴࠡࡣࡱࡨࠥࡹࡴࡰࡴࡨࡷࠥࡺࡨࡦࠢࡵࡩࡸࡶ࡯࡯ࡵࡨࠤࡩࡧࡴࡢࠢࡩࡳࡷࠦࡰࡰ࡮࡯࡭ࡳ࡭࠮ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠥࠦࠧⅡ")
        self.logger.debug(bstack11ll1_opy_ (u"ࠨ࡛ࡴࡲ࡯࡭ࡹ࡚ࡥࡴࡶࡶࡡࠥࡏ࡮ࡪࡶ࡬ࡥࡹ࡯࡮ࡨࠢࡶࡴࡱ࡯ࡴࠡࡶࡨࡷࡹࡹࠠࡸ࡫ࡷ࡬ࠥࡹࡴࡳࡣࡷࡩ࡬ࡿ࠺ࠡࡽࢀࠦⅢ").format(orchestration_strategy))
        try:
            bstack1llll1111ll1_opy_ = []
            bstack11ll1_opy_ (u"ࠢࠣࠤ࡚ࡩࠥࡽࡩ࡭࡮ࠣࡲࡴࡺࠠࡧࡧࡷࡧ࡭ࠦࡧࡪࡶࠣࡱࡪࡺࡡࡥࡣࡷࡥࠥ࡯ࡳࠡࡵࡲࡹࡷࡩࡥࠡ࡫ࡶࠤࡹࡿࡰࡦࠢࡲࡪࠥࡧࡲࡳࡣࡼࠤࡦࡴࡤࠡ࡫ࡷࠫࡸࠦࡥ࡭ࡧࡰࡩࡳࡺࡳࠡࡣࡵࡩࠥࡵࡦࠡࡶࡼࡴࡪࠦࡤࡪࡥࡷࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࡥࡩࡨࡧࡵࡴࡧࠣ࡭ࡳࠦࡴࡩࡣࡷࠤࡨࡧࡳࡦ࠮ࠣࡹࡸ࡫ࡲࠡࡪࡤࡷࠥࡶࡲࡰࡸ࡬ࡨࡪࡪࠠ࡮ࡷ࡯ࡸ࡮࠳ࡲࡦࡲࡲࠤࡸࡵࡵࡳࡥࡨࠤࡼ࡯ࡴࡩࠢࡩࡩࡦࡺࡵࡳࡧࡅࡶࡦࡴࡣࡩࠢ࡬ࡲࠥࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࠦࠧࠨⅣ")
            source = orchestration_metadata[bstack11ll1_opy_ (u"ࠨࡴࡸࡲࡤࡹ࡭ࡢࡴࡷࡣࡸ࡫࡬ࡦࡥࡷ࡭ࡴࡴࠧⅤ")].get(bstack11ll1_opy_ (u"ࠩࡶࡳࡺࡸࡣࡦࠩⅥ"), [])
            bstack1lll1llll1ll_opy_ = isinstance(source, list) and all(isinstance(src, dict) and src is not None for src in source) and len(source) > 0
            if orchestration_metadata[bstack11ll1_opy_ (u"ࠪࡶࡺࡴ࡟ࡴ࡯ࡤࡶࡹࡥࡳࡦ࡮ࡨࡧࡹ࡯࡯࡯ࠩⅦ")].get(bstack11ll1_opy_ (u"ࠫࡪࡴࡡࡣ࡮ࡨࡨࠬⅧ"), False) and not bstack1lll1llll1ll_opy_:
                bstack1llll1111ll1_opy_ = bstack111lll11111_opy_(source) # bstack1llll1111l1l_opy_-repo is handled bstack1lll1lllllll_opy_
            payload = {
                bstack11ll1_opy_ (u"ࠧࡺࡥࡴࡶࡶࠦⅨ"): [{bstack11ll1_opy_ (u"ࠨࡦࡪ࡮ࡨࡔࡦࡺࡨࠣⅩ"): f} for f in test_files],
                bstack11ll1_opy_ (u"ࠢࡰࡴࡦ࡬ࡪࡹࡴࡳࡣࡷ࡭ࡴࡴࡓࡵࡴࡤࡸࡪ࡭ࡹࠣⅪ"): orchestration_strategy,
                bstack11ll1_opy_ (u"ࠣࡱࡵࡧ࡭࡫ࡳࡵࡴࡤࡸ࡮ࡵ࡮ࡎࡧࡷࡥࡩࡧࡴࡢࠤⅫ"): orchestration_metadata,
                bstack11ll1_opy_ (u"ࠤࡱࡳࡩ࡫ࡉ࡯ࡦࡨࡼࠧⅬ"): int(os.environ.get(bstack11ll1_opy_ (u"ࠥࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡑࡓࡉࡋ࡟ࡊࡐࡇࡉ࡝ࠨⅭ")) or bstack11ll1_opy_ (u"ࠦ࠵ࠨⅮ")),
                bstack11ll1_opy_ (u"ࠧࡺ࡯ࡵࡣ࡯ࡒࡴࡪࡥࡴࠤⅯ"): int(os.environ.get(bstack11ll1_opy_ (u"ࠨࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡏࡕࡃࡏࡣࡓࡕࡄࡆࡡࡆࡓ࡚ࡔࡔࠣⅰ")) or bstack11ll1_opy_ (u"ࠢ࠲ࠤⅱ")),
                bstack11ll1_opy_ (u"ࠣࡲࡵࡳ࡯࡫ࡣࡵࡐࡤࡱࡪࠨⅲ"): self.config.get(bstack11ll1_opy_ (u"ࠩࡳࡶࡴࡰࡥࡤࡶࡑࡥࡲ࡫ࠧⅳ"), bstack11ll1_opy_ (u"ࠪࠫⅴ")),
                bstack11ll1_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡑࡥࡲ࡫ࠢⅵ"): self.config.get(bstack11ll1_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡒࡦࡳࡥࠨⅶ"), os.path.basename(os.path.abspath(os.getcwd()))),
                bstack11ll1_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡗࡻ࡮ࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠦⅷ"): os.environ.get(bstack11ll1_opy_ (u"ࠢࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡂࡖࡋࡏࡈࡤࡘࡕࡏࡡࡌࡈࡊࡔࡔࡊࡈࡌࡉࡗࠨⅸ"), bstack11ll1_opy_ (u"ࠣࠤⅹ")),
                bstack11ll1_opy_ (u"ࠤ࡫ࡳࡸࡺࡉ࡯ࡨࡲࠦⅺ"): get_host_info(),
                bstack11ll1_opy_ (u"ࠥࡴࡷࡊࡥࡵࡣ࡬ࡰࡸࠨⅻ"): bstack1llll1111ll1_opy_
            }
            self.logger.debug(bstack11ll1_opy_ (u"ࠦࡠࡹࡰ࡭࡫ࡷࡘࡪࡹࡴࡴ࡟ࠣࡗࡪࡴࡤࡪࡰࡪࠤࡹ࡫ࡳࡵࠢࡩ࡭ࡱ࡫ࡳ࠻ࠢࡾࢁࠧⅼ").format(payload))
            response = bstack11l1ll1l11l_opy_.bstack1llll1l1ll11_opy_(self.bstack1llll1111111_opy_, payload)
            if response:
                self.bstack1llll111l11l_opy_ = self._1llll1111lll_opy_(response)
                self.logger.debug(bstack11ll1_opy_ (u"ࠧࡡࡳࡱ࡮࡬ࡸ࡙࡫ࡳࡵࡵࡠࠤࡘࡶ࡬ࡪࡶࠣࡸࡪࡹࡴࡴࠢࡵࡩࡸࡶ࡯࡯ࡵࡨ࠾ࠥࢁࡽࠣⅽ").format(self.bstack1llll111l11l_opy_))
            else:
                self.logger.error(bstack11ll1_opy_ (u"ࠨ࡛ࡴࡲ࡯࡭ࡹ࡚ࡥࡴࡶࡶࡡࠥࡌࡡࡪ࡮ࡨࡨࠥࡺ࡯ࠡࡩࡨࡸࠥࡹࡰ࡭࡫ࡷࠤࡹ࡫ࡳࡵࡵࠣࡶࡪࡹࡰࡰࡰࡶࡩ࠳ࠨⅾ"))
        except Exception as e:
            self.logger.error(bstack11ll1_opy_ (u"ࠢ࡜ࡵࡳࡰ࡮ࡺࡔࡦࡵࡷࡷࡢࠦࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢ࡬ࡲࠥࡹࡥ࡯ࡦ࡬ࡲ࡬ࠦࡴࡦࡵࡷࠤ࡫࡯࡬ࡦࡵ࠽࠾ࠥࢁࡽࠣⅿ").format(e))
    def _1llll1111lll_opy_(self, response):
        bstack11ll1_opy_ (u"ࠣࠤࠥࠎࠥࠦࠠࠡࠢࠣࠤࠥࡖࡲࡰࡥࡨࡷࡸ࡫ࡳࠡࡶ࡫ࡩࠥࡹࡰ࡭࡫ࡷࠤࡹ࡫ࡳࡵࡵࠣࡅࡕࡏࠠࡳࡧࡶࡴࡴࡴࡳࡦࠢࡤࡲࡩࠦࡥࡹࡶࡵࡥࡨࡺࡳࠡࡴࡨࡰࡪࡼࡡ࡯ࡶࠣࡪ࡮࡫࡬ࡥࡵ࠱ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠨࠢࠣↀ")
        bstack1lllll1l1_opy_ = {}
        bstack1lllll1l1_opy_[bstack11ll1_opy_ (u"ࠤࡷ࡭ࡲ࡫࡯ࡶࡶࠥↁ")] = response.get(bstack11ll1_opy_ (u"ࠥࡸ࡮ࡳࡥࡰࡷࡷࠦↂ"), self.bstack1llll11111l1_opy_)
        bstack1lllll1l1_opy_[bstack11ll1_opy_ (u"ࠦࡹ࡯࡭ࡦࡱࡸࡸࡎࡴࡴࡦࡴࡹࡥࡱࠨↃ")] = response.get(bstack11ll1_opy_ (u"ࠧࡺࡩ࡮ࡧࡲࡹࡹࡏ࡮ࡵࡧࡵࡺࡦࡲࠢↄ"), self.bstack1llll111111l_opy_)
        bstack1llll11111ll_opy_ = response.get(bstack11ll1_opy_ (u"ࠨࡲࡦࡵࡸࡰࡹ࡛ࡲ࡭ࠤↅ"))
        bstack1lll1llll11l_opy_ = response.get(bstack11ll1_opy_ (u"ࠢࡵ࡫ࡰࡩࡴࡻࡴࡖࡴ࡯ࠦↆ"))
        if bstack1llll11111ll_opy_:
            bstack1lllll1l1_opy_[bstack11ll1_opy_ (u"ࠣࡴࡨࡷࡺࡲࡴࡖࡴ࡯ࠦↇ")] = bstack1llll11111ll_opy_.split(bstack11l11lll1l1_opy_ + bstack11ll1_opy_ (u"ࠤ࠲ࠦↈ"))[1] if bstack11l11lll1l1_opy_ + bstack11ll1_opy_ (u"ࠥ࠳ࠧ↉") in bstack1llll11111ll_opy_ else bstack1llll11111ll_opy_
        else:
            bstack1lllll1l1_opy_[bstack11ll1_opy_ (u"ࠦࡷ࡫ࡳࡶ࡮ࡷ࡙ࡷࡲࠢ↊")] = None
        if bstack1lll1llll11l_opy_:
            bstack1lllll1l1_opy_[bstack11ll1_opy_ (u"ࠧࡺࡩ࡮ࡧࡲࡹࡹ࡛ࡲ࡭ࠤ↋")] = bstack1lll1llll11l_opy_.split(bstack11l11lll1l1_opy_ + bstack11ll1_opy_ (u"ࠨ࠯ࠣ↌"))[1] if bstack11l11lll1l1_opy_ + bstack11ll1_opy_ (u"ࠢ࠰ࠤ↍") in bstack1lll1llll11l_opy_ else bstack1lll1llll11l_opy_
        else:
            bstack1lllll1l1_opy_[bstack11ll1_opy_ (u"ࠣࡶ࡬ࡱࡪࡵࡵࡵࡗࡵࡰࠧ↎")] = None
        if (
            response.get(bstack11ll1_opy_ (u"ࠤࡷ࡭ࡲ࡫࡯ࡶࡶࠥ↏")) is None or
            response.get(bstack11ll1_opy_ (u"ࠥࡸ࡮ࡳࡥࡰࡷࡷࡍࡳࡺࡥࡳࡸࡤࡰࠧ←")) is None or
            response.get(bstack11ll1_opy_ (u"ࠦࡹ࡯࡭ࡦࡱࡸࡸ࡚ࡸ࡬ࠣ↑")) is None or
            response.get(bstack11ll1_opy_ (u"ࠧࡸࡥࡴࡷ࡯ࡸ࡚ࡸ࡬ࠣ→")) is None
        ):
            self.logger.debug(bstack11ll1_opy_ (u"ࠨ࡛ࡱࡴࡲࡧࡪࡹࡳࡠࡵࡳࡰ࡮ࡺ࡟ࡵࡧࡶࡸࡸࡥࡲࡦࡵࡳࡳࡳࡹࡥ࡞ࠢࡕࡩࡨ࡫ࡩࡷࡧࡧࠤࡳࡻ࡬࡭ࠢࡹࡥࡱࡻࡥࠩࡵࠬࠤ࡫ࡵࡲࠡࡵࡲࡱࡪࠦࡡࡵࡶࡵ࡭ࡧࡻࡴࡦࡵࠣ࡭ࡳࠦࡳࡱ࡮࡬ࡸࠥࡺࡥࡴࡶࡶࠤࡆࡖࡉࠡࡴࡨࡷࡵࡵ࡮ࡴࡧࠥ↓"))
        return bstack1lllll1l1_opy_
    def bstack1111ll111l1_opy_(self):
        if not self.bstack1llll111l11l_opy_:
            self.logger.error(bstack11ll1_opy_ (u"ࠢ࡜ࡩࡨࡸࡔࡸࡤࡦࡴࡨࡨ࡙࡫ࡳࡵࡈ࡬ࡰࡪࡹ࡝ࠡࡐࡲࠤࡷ࡫ࡱࡶࡧࡶࡸࠥࡪࡡࡵࡣࠣࡥࡻࡧࡩ࡭ࡣࡥࡰࡪࠦࡴࡰࠢࡩࡩࡹࡩࡨࠡࡱࡵࡨࡪࡸࡥࡥࠢࡷࡩࡸࡺࠠࡧ࡫࡯ࡩࡸ࠴ࠢ↔"))
            return None
        bstack1llll111l111_opy_ = None
        test_files = []
        bstack1llll1111l11_opy_ = int(time.time() * 1000) # bstack1lll1llllll1_opy_ sec
        bstack1lll1llll1l1_opy_ = int(self.bstack1llll111l11l_opy_.get(bstack11ll1_opy_ (u"ࠣࡶ࡬ࡱࡪࡵࡵࡵࡋࡱࡸࡪࡸࡶࡢ࡮ࠥ↕"), self.bstack1llll111111l_opy_))
        bstack1lll1lllll11_opy_ = int(self.bstack1llll111l11l_opy_.get(bstack11ll1_opy_ (u"ࠤࡷ࡭ࡲ࡫࡯ࡶࡶࠥ↖"), self.bstack1llll11111l1_opy_)) * 1000
        bstack1lll1llll11l_opy_ = self.bstack1llll111l11l_opy_.get(bstack11ll1_opy_ (u"ࠥࡸ࡮ࡳࡥࡰࡷࡷ࡙ࡷࡲࠢ↗"), None)
        bstack1llll11111ll_opy_ = self.bstack1llll111l11l_opy_.get(bstack11ll1_opy_ (u"ࠦࡷ࡫ࡳࡶ࡮ࡷ࡙ࡷࡲࠢ↘"), None)
        if bstack1llll11111ll_opy_ is None and bstack1lll1llll11l_opy_ is None:
            return None
        try:
            while bstack1llll11111ll_opy_ and (time.time() * 1000 - bstack1llll1111l11_opy_) < bstack1lll1lllll11_opy_:
                response = bstack11l1ll1l11l_opy_.bstack1llll1l11l1l_opy_(bstack1llll11111ll_opy_, {})
                if response and response.get(bstack11ll1_opy_ (u"ࠧࡺࡥࡴࡶࡶࠦ↙")):
                    bstack1llll111l111_opy_ = response.get(bstack11ll1_opy_ (u"ࠨࡴࡦࡵࡷࡷࠧ↚"))
                self.bstack1lll1lllll1l_opy_ += 1
                if bstack1llll111l111_opy_:
                    break
                time.sleep(bstack1lll1llll1l1_opy_)
                self.logger.debug(bstack11ll1_opy_ (u"ࠢ࡜ࡩࡨࡸࡔࡸࡤࡦࡴࡨࡨ࡙࡫ࡳࡵࡈ࡬ࡰࡪࡹ࡝ࠡࡈࡨࡸࡨ࡮ࡩ࡯ࡩࠣࡳࡷࡪࡥࡳࡧࡧࠤࡹ࡫ࡳࡵࡵࠣࡪࡷࡵ࡭ࠡࡴࡨࡷࡺࡲࡴࠡࡗࡕࡐࠥࡧࡦࡵࡧࡵࠤࡼࡧࡩࡵ࡫ࡱ࡫ࠥ࡬࡯ࡳࠢࡾࢁࠥࡹࡥࡤࡱࡱࡨࡸ࠴ࠢ↛").format(bstack1lll1llll1l1_opy_))
            if bstack1lll1llll11l_opy_ and not bstack1llll111l111_opy_:
                self.logger.debug(bstack11ll1_opy_ (u"ࠣ࡝ࡪࡩࡹࡕࡲࡥࡧࡵࡩࡩ࡚ࡥࡴࡶࡉ࡭ࡱ࡫ࡳ࡞ࠢࡉࡩࡹࡩࡨࡪࡰࡪࠤࡴࡸࡤࡦࡴࡨࡨࠥࡺࡥࡴࡶࡶࠤ࡫ࡸ࡯࡮ࠢࡷ࡭ࡲ࡫࡯ࡶࡶ࡙ࠣࡗࡒࠢ↜"))
                response = bstack11l1ll1l11l_opy_.bstack1llll1l11l1l_opy_(bstack1lll1llll11l_opy_, {})
                if response and response.get(bstack11ll1_opy_ (u"ࠤࡷࡩࡸࡺࡳࠣ↝")):
                    bstack1llll111l111_opy_ = response.get(bstack11ll1_opy_ (u"ࠥࡸࡪࡹࡴࡴࠤ↞"))
            if bstack1llll111l111_opy_ and len(bstack1llll111l111_opy_) > 0:
                for bstack111l1ll11l_opy_ in bstack1llll111l111_opy_:
                    file_path = bstack111l1ll11l_opy_.get(bstack11ll1_opy_ (u"ࠦ࡫࡯࡬ࡦࡒࡤࡸ࡭ࠨ↟"))
                    if file_path:
                        test_files.append(file_path)
            if not bstack1llll111l111_opy_:
                return None
            self.logger.debug(bstack11ll1_opy_ (u"ࠧࡡࡧࡦࡶࡒࡶࡩ࡫ࡲࡦࡦࡗࡩࡸࡺࡆࡪ࡮ࡨࡷࡢࠦࡏࡳࡦࡨࡶࡪࡪࠠࡵࡧࡶࡸࠥ࡬ࡩ࡭ࡧࡶࠤࡷ࡫ࡣࡦ࡫ࡹࡩࡩࡀࠠࡼࡿࠥ↠").format(test_files))
            return test_files
        except Exception as e:
            self.logger.error(bstack11ll1_opy_ (u"ࠨ࡛ࡨࡧࡷࡓࡷࡪࡥࡳࡧࡧࡘࡪࡹࡴࡇ࡫࡯ࡩࡸࡣࠠࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣ࡭ࡳࠦࡦࡦࡶࡦ࡬࡮ࡴࡧࠡࡱࡵࡨࡪࡸࡥࡥࠢࡷࡩࡸࡺࠠࡧ࡫࡯ࡩࡸࡀࠠࡼࡿࠥ↡").format(e))
            return None
    def bstack1111ll11ll1_opy_(self):
        bstack11ll1_opy_ (u"ࠢࠣࠤࠍࠤࠥࠦࠠࠡࠢࠣࠤࡗ࡫ࡴࡶࡴࡱࡷࠥࡺࡨࡦࠢࡦࡳࡺࡴࡴࠡࡱࡩࠤࡸࡶ࡬ࡪࡶࠣࡸࡪࡹࡴࡴࠢࡄࡔࡎࠦࡣࡢ࡮࡯ࡷࠥࡳࡡࡥࡧ࠱ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠨࠢࠣ↢")
        return self.bstack1lll1lllll1l_opy_