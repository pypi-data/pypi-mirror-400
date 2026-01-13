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
import json
import logging
logger = logging.getLogger(__name__)
class BrowserStackSdk:
    def get_current_platform():
        bstack11l11l11l_opy_ = {}
        bstack111ll1l11l_opy_ = os.environ.get(bstack11ll1_opy_ (u"ࠧࡄࡗࡕࡖࡊࡔࡔࡠࡒࡏࡅ࡙ࡌࡏࡓࡏࡢࡈࡆ࡚ࡁࠨ༭"), bstack11ll1_opy_ (u"ࠨࠩ༮"))
        if not bstack111ll1l11l_opy_:
            return bstack11l11l11l_opy_
        try:
            bstack111ll1l111_opy_ = json.loads(bstack111ll1l11l_opy_)
            if bstack11ll1_opy_ (u"ࠤࡲࡷࠧ༯") in bstack111ll1l111_opy_:
                bstack11l11l11l_opy_[bstack11ll1_opy_ (u"ࠥࡳࡸࠨ༰")] = bstack111ll1l111_opy_[bstack11ll1_opy_ (u"ࠦࡴࡹࠢ༱")]
            if bstack11ll1_opy_ (u"ࠧࡵࡳࡠࡸࡨࡶࡸ࡯࡯࡯ࠤ༲") in bstack111ll1l111_opy_ or bstack11ll1_opy_ (u"ࠨ࡯ࡴࡘࡨࡶࡸ࡯࡯࡯ࠤ༳") in bstack111ll1l111_opy_:
                bstack11l11l11l_opy_[bstack11ll1_opy_ (u"ࠢࡰࡵ࡙ࡩࡷࡹࡩࡰࡰࠥ༴")] = bstack111ll1l111_opy_.get(bstack11ll1_opy_ (u"ࠣࡱࡶࡣࡻ࡫ࡲࡴ࡫ࡲࡲ༵ࠧ"), bstack111ll1l111_opy_.get(bstack11ll1_opy_ (u"ࠤࡲࡷ࡛࡫ࡲࡴ࡫ࡲࡲࠧ༶")))
            if bstack11ll1_opy_ (u"ࠥࡦࡷࡵࡷࡴࡧࡵ༷ࠦ") in bstack111ll1l111_opy_ or bstack11ll1_opy_ (u"ࠦࡧࡸ࡯ࡸࡵࡨࡶࡓࡧ࡭ࡦࠤ༸") in bstack111ll1l111_opy_:
                bstack11l11l11l_opy_[bstack11ll1_opy_ (u"ࠧࡨࡲࡰࡹࡶࡩࡷࡔࡡ࡮ࡧ༹ࠥ")] = bstack111ll1l111_opy_.get(bstack11ll1_opy_ (u"ࠨࡢࡳࡱࡺࡷࡪࡸࠢ༺"), bstack111ll1l111_opy_.get(bstack11ll1_opy_ (u"ࠢࡣࡴࡲࡻࡸ࡫ࡲࡏࡣࡰࡩࠧ༻")))
            if bstack11ll1_opy_ (u"ࠣࡤࡵࡳࡼࡹࡥࡳࡡࡹࡩࡷࡹࡩࡰࡰࠥ༼") in bstack111ll1l111_opy_ or bstack11ll1_opy_ (u"ࠤࡥࡶࡴࡽࡳࡦࡴ࡙ࡩࡷࡹࡩࡰࡰࠥ༽") in bstack111ll1l111_opy_:
                bstack11l11l11l_opy_[bstack11ll1_opy_ (u"ࠥࡦࡷࡵࡷࡴࡧࡵ࡚ࡪࡸࡳࡪࡱࡱࠦ༾")] = bstack111ll1l111_opy_.get(bstack11ll1_opy_ (u"ࠦࡧࡸ࡯ࡸࡵࡨࡶࡤࡼࡥࡳࡵ࡬ࡳࡳࠨ༿"), bstack111ll1l111_opy_.get(bstack11ll1_opy_ (u"ࠧࡨࡲࡰࡹࡶࡩࡷ࡜ࡥࡳࡵ࡬ࡳࡳࠨཀ")))
            if bstack11ll1_opy_ (u"ࠨࡤࡦࡸ࡬ࡧࡪࠨཁ") in bstack111ll1l111_opy_ or bstack11ll1_opy_ (u"ࠢࡥࡧࡹ࡭ࡨ࡫ࡎࡢ࡯ࡨࠦག") in bstack111ll1l111_opy_:
                bstack11l11l11l_opy_[bstack11ll1_opy_ (u"ࠣࡦࡨࡺ࡮ࡩࡥࡏࡣࡰࡩࠧགྷ")] = bstack111ll1l111_opy_.get(bstack11ll1_opy_ (u"ࠤࡧࡩࡻ࡯ࡣࡦࠤང"), bstack111ll1l111_opy_.get(bstack11ll1_opy_ (u"ࠥࡨࡪࡼࡩࡤࡧࡑࡥࡲ࡫ࠢཅ")))
            if bstack11ll1_opy_ (u"ࠦࡵࡲࡡࡵࡨࡲࡶࡲࠨཆ") in bstack111ll1l111_opy_ or bstack11ll1_opy_ (u"ࠧࡶ࡬ࡢࡶࡩࡳࡷࡳࡎࡢ࡯ࡨࠦཇ") in bstack111ll1l111_opy_:
                bstack11l11l11l_opy_[bstack11ll1_opy_ (u"ࠨࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡏࡣࡰࡩࠧ཈")] = bstack111ll1l111_opy_.get(bstack11ll1_opy_ (u"ࠢࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࠤཉ"), bstack111ll1l111_opy_.get(bstack11ll1_opy_ (u"ࠣࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡑࡥࡲ࡫ࠢཊ")))
            if bstack11ll1_opy_ (u"ࠤࡳࡰࡦࡺࡦࡰࡴࡰࡣࡻ࡫ࡲࡴ࡫ࡲࡲࠧཋ") in bstack111ll1l111_opy_ or bstack11ll1_opy_ (u"ࠥࡴࡱࡧࡴࡧࡱࡵࡱ࡛࡫ࡲࡴ࡫ࡲࡲࠧཌ") in bstack111ll1l111_opy_:
                bstack11l11l11l_opy_[bstack11ll1_opy_ (u"ࠦࡵࡲࡡࡵࡨࡲࡶࡲ࡜ࡥࡳࡵ࡬ࡳࡳࠨཌྷ")] = bstack111ll1l111_opy_.get(bstack11ll1_opy_ (u"ࠧࡶ࡬ࡢࡶࡩࡳࡷࡳ࡟ࡷࡧࡵࡷ࡮ࡵ࡮ࠣཎ"), bstack111ll1l111_opy_.get(bstack11ll1_opy_ (u"ࠨࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡗࡧࡵࡷ࡮ࡵ࡮ࠣཏ")))
            if bstack11ll1_opy_ (u"ࠢࡤࡷࡶࡸࡴࡳࡖࡢࡴ࡬ࡥࡧࡲࡥࡴࠤཐ") in bstack111ll1l111_opy_:
                bstack11l11l11l_opy_[bstack11ll1_opy_ (u"ࠣࡥࡸࡷࡹࡵ࡭ࡗࡣࡵ࡭ࡦࡨ࡬ࡦࡵࠥད")] = bstack111ll1l111_opy_[bstack11ll1_opy_ (u"ࠤࡦࡹࡸࡺ࡯࡮ࡘࡤࡶ࡮ࡧࡢ࡭ࡧࡶࠦདྷ")]
        except Exception as error:
            logger.error(bstack11ll1_opy_ (u"ࠥࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡷࡩ࡫࡯ࡩࠥ࡭ࡥࡵࡶ࡬ࡲ࡬ࠦࡣࡶࡴࡵࡩࡳࡺࠠࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࠢࡧࡥࡹࡧ࠺ࠡࠤན") +  str(error))
        return bstack11l11l11l_opy_