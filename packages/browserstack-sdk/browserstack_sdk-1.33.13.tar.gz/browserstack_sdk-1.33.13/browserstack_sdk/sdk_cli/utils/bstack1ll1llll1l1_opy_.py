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
import re
from typing import List, Dict, Any
from bstack_utils.bstack1l1lll1l11_opy_ import get_logger
logger = get_logger(__name__)
class bstack1ll1llll1ll_opy_:
    bstack11l1l_opy_ (u"ࠨࠢࠣࠌࠣࠤࠥࠦࡃࡶࡵࡷࡳࡲ࡚ࡡࡨࡏࡤࡲࡦ࡭ࡥࡳࠢࡳࡶࡴࡼࡩࡥࡧࡶࠤࡺࡺࡩ࡭࡫ࡷࡽࠥࡳࡥࡵࡪࡲࡨࡸࠦࡴࡰࠢࡶࡩࡹࠦࡡ࡯ࡦࠣࡶࡪࡺࡲࡪࡧࡹࡩࠥࡩࡵࡴࡶࡲࡱࠥࡺࡡࡨࠢࡰࡩࡹࡧࡤࡢࡶࡤ࠲ࠏࠦࠠࠡࠢࡌࡸࠥࡳࡡࡪࡰࡷࡥ࡮ࡴࡳࠡࡶࡺࡳࠥࡹࡥࡱࡣࡵࡥࡹ࡫ࠠ࡮ࡧࡷࡥࡩࡧࡴࡢࠢࡧ࡭ࡨࡺࡩࡰࡰࡤࡶ࡮࡫ࡳࠡࡨࡲࡶࠥࡺࡥࡴࡶࠣࡰࡪࡼࡥ࡭ࠢࡤࡲࡩࠦࡢࡶ࡫࡯ࡨࠥࡲࡥࡷࡧ࡯ࠤࡨࡻࡳࡵࡱࡰࠤࡹࡧࡧࡴ࠰ࠍࠤࠥࠦࠠࡆࡣࡦ࡬ࠥࡳࡥࡵࡣࡧࡥࡹࡧࠠࡦࡰࡷࡶࡾࠦࡩࡴࠢࡨࡼࡵ࡫ࡣࡵࡧࡧࠤࡹࡵࠠࡣࡧࠣࡷࡹࡸࡵࡤࡶࡸࡶࡪࡪࠠࡢࡵ࠽ࠎࠥࠦࠠࠡࠢࠣࠤࡰ࡫ࡹ࠻ࠢࡾࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠤࡩ࡭ࡪࡲࡤࡠࡶࡼࡴࡪࠨ࠺ࠡࠤࡰࡹࡱࡺࡩࡠࡦࡵࡳࡵࡪ࡯ࡸࡰࠥ࠰ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠥࡺࡦࡲࡵࡦࡵࠥ࠾ࠥࡡ࡬ࡪࡵࡷࠤࡴ࡬ࠠࡵࡣࡪࠤࡻࡧ࡬ࡶࡧࡶࡡࠏࠦࠠࠡࠢࠣࠤࠥࢃࠊࠡࠢࠣࠤࠧࠨࠢᙹ")
    _11ll1ll1l1l_opy_: Dict[str, Dict[str, Any]] = {}
    _11ll1ll1ll1_opy_: Dict[str, Dict[str, Any]] = {}
    @staticmethod
    def set_custom_tag(bstack1ll11ll1_opy_: str, key_value: str, bstack11ll1ll1111_opy_: bool = False) -> None:
        if not bstack1ll11ll1_opy_ or not key_value or bstack1ll11ll1_opy_.strip() == bstack11l1l_opy_ (u"ࠢࠣᙺ") or key_value.strip() == bstack11l1l_opy_ (u"ࠣࠤᙻ"):
            logger.error(bstack11l1l_opy_ (u"ࠤ࡮ࡩࡾࡥ࡮ࡢ࡯ࡨࠤࡦࡴࡤࠡ࡭ࡨࡽࡤࡼࡡ࡭ࡷࡨࠤࡲࡻࡳࡵࠢࡥࡩࠥࡴ࡯࡯࠯ࡱࡹࡱࡲࠠࡢࡰࡧࠤࡳࡵ࡮࠮ࡧࡰࡴࡹࡿࠢᙼ"))
        values: List[str] = bstack1ll1llll1ll_opy_.bstack11ll1ll1l11_opy_(key_value)
        bstack11ll1ll111l_opy_ = {bstack11l1l_opy_ (u"ࠥࡪ࡮࡫࡬ࡥࡡࡷࡽࡵ࡫ࠢᙽ"): bstack11l1l_opy_ (u"ࠦࡲࡻ࡬ࡵ࡫ࡢࡨࡷࡵࡰࡥࡱࡺࡲࠧᙾ"), bstack11l1l_opy_ (u"ࠧࡼࡡ࡭ࡷࡨࡷࠧᙿ"): values}
        bstack11ll1ll1lll_opy_ = bstack1ll1llll1ll_opy_._11ll1ll1ll1_opy_ if bstack11ll1ll1111_opy_ else bstack1ll1llll1ll_opy_._11ll1ll1l1l_opy_
        if bstack1ll11ll1_opy_ in bstack11ll1ll1lll_opy_:
            bstack11ll1lll11l_opy_ = bstack11ll1ll1lll_opy_[bstack1ll11ll1_opy_]
            bstack11ll1lll111_opy_ = bstack11ll1lll11l_opy_.get(bstack11l1l_opy_ (u"ࠨࡶࡢ࡮ࡸࡩࡸࠨ "), [])
            for val in values:
                if val not in bstack11ll1lll111_opy_:
                    bstack11ll1lll111_opy_.append(val)
            bstack11ll1lll11l_opy_[bstack11l1l_opy_ (u"ࠢࡷࡣ࡯ࡹࡪࡹࠢᚁ")] = bstack11ll1lll111_opy_
        else:
            bstack11ll1ll1lll_opy_[bstack1ll11ll1_opy_] = bstack11ll1ll111l_opy_
    @staticmethod
    def bstack11lll11llll_opy_() -> Dict[str, Dict[str, Any]]:
        return bstack1ll1llll1ll_opy_._11ll1ll1l1l_opy_
    @staticmethod
    def bstack11ll1ll11ll_opy_() -> Dict[str, Dict[str, Any]]:
        return bstack1ll1llll1ll_opy_._11ll1ll1ll1_opy_
    @staticmethod
    def bstack11ll1ll1l11_opy_(bstack11ll1ll11l1_opy_: str) -> List[str]:
        bstack11l1l_opy_ (u"ࠣࠤࠥࠎࠥࠦࠠࠡࠢࠣࠤ࡙ࠥࡰ࡭࡫ࡷࡷࠥࡺࡨࡦࠢ࡬ࡲࡵࡻࡴࠡࡵࡷࡶ࡮ࡴࡧࠡࡤࡼࠤࡨࡵ࡭࡮ࡣࡶࠤࡼ࡮ࡩ࡭ࡧࠣࡶࡪࡹࡰࡦࡥࡷ࡭ࡳ࡭ࠠࡥࡱࡸࡦࡱ࡫࠭ࡲࡷࡲࡸࡪࡪࠠࡴࡷࡥࡷࡹࡸࡩ࡯ࡩࡶ࠲ࠏࠦࠠࠡࠢࠣࠤࠥࠦࡆࡰࡴࠣࡩࡽࡧ࡭ࡱ࡮ࡨ࠾ࠥ࠭ࡡ࠭ࠢࠥࡦ࠱ࡩࠢ࠭ࠢࡧࠫࠥ࠳࠾ࠡ࡝ࠪࡥࠬ࠲ࠠࠨࡤ࠯ࡧࠬ࠲ࠠࠨࡦࠪࡡࠏࠦࠠࠡࠢࠣࠤࠥࠦࠢࠣࠤᚂ")
        pattern = re.compile(bstack11l1l_opy_ (u"ࡴࠪࠦ࠭ࡡ࡞ࠣ࡟࠭࠭ࠧࢂࠨ࡜ࡠ࠯ࡡ࠰࠯ࠧᚃ"))
        result = []
        for match in pattern.finditer(bstack11ll1ll11l1_opy_):
            if match.group(1) is not None:
                result.append(match.group(1).strip())
            elif match.group(2) is not None:
                result.append(match.group(2).strip())
        return result
    def __new__(cls, *args, **kwargs):
        raise Exception(bstack11l1l_opy_ (u"࡙ࠥࡹ࡯࡬ࡪࡶࡼࠤࡨࡲࡡࡴࡵࠣࡷ࡭ࡵࡵ࡭ࡦࠣࡲࡴࡺࠠࡣࡧࠣ࡭ࡳࡹࡴࡢࡰࡷ࡭ࡦࡺࡥࡥࠤᚄ"))