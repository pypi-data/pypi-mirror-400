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
import logging
from functools import wraps
from typing import Optional
from bstack_utils.constants import EVENTS, STAGE
from bstack_utils.bstack1l1lll1l11_opy_ import get_logger
from bstack_utils.bstack11l1l11ll_opy_ import bstack1lll1ll1l11_opy_
bstack11l1l11ll_opy_ = bstack1lll1ll1l11_opy_()
logger = get_logger(__name__)
def measure(event_name: EVENTS, stage: STAGE, hook_type: Optional[str] = None, bstack1l1l1llll_opy_: Optional[str] = None):
    bstack11l1l_opy_ (u"ࠧࠨࠢࠋࠢࠣࠤࠥࡊࡥࡤࡱࡵࡥࡹࡵࡲࠡࡶࡲࠤࡱࡵࡧࠡࡶ࡫ࡩࠥࡹࡴࡢࡴࡷࠤࡹ࡯࡭ࡦࠢࡲࡪࠥࡧࠠࡧࡷࡱࡧࡹ࡯࡯࡯ࠢࡨࡼࡪࡩࡵࡵ࡫ࡲࡲࠏࠦࠠࠡࠢࡤࡰࡴࡴࡧࠡࡹ࡬ࡸ࡭ࠦࡥࡷࡧࡱࡸࠥࡴࡡ࡮ࡧࠣࡥࡳࡪࠠࡴࡶࡤ࡫ࡪ࠴ࠊࠡࠢࠣࠤࠧࠨࠢẳ")
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            label: str = event_name.value
            bstack1l1llllllll_opy_: str = bstack11l1l11ll_opy_.bstack11ll11l111l_opy_(label)
            start_mark: str = label + bstack11l1l_opy_ (u"ࠨ࠺ࡴࡶࡤࡶࡹࠨẴ")
            end_mark: str = label + bstack11l1l_opy_ (u"ࠢ࠻ࡧࡱࡨࠧẵ")
            result = None
            try:
                if stage.value == STAGE.bstack1ll1l1lll_opy_.value:
                    bstack11l1l11ll_opy_.mark(start_mark)
                    result = func(*args, **kwargs)
                elif stage.value == STAGE.END.value:
                    result = func(*args, **kwargs)
                    bstack11l1l11ll_opy_.end(label, start_mark, end_mark, status=True, failure=None,hook_type=hook_type,test_name=bstack1l1l1llll_opy_)
                elif stage.value == STAGE.bstack1lll1l11l_opy_.value:
                    start_mark: str = bstack1l1llllllll_opy_ + bstack11l1l_opy_ (u"ࠣ࠼ࡶࡸࡦࡸࡴࠣẶ")
                    end_mark: str = bstack1l1llllllll_opy_ + bstack11l1l_opy_ (u"ࠤ࠽ࡩࡳࡪࠢặ")
                    bstack11l1l11ll_opy_.mark(start_mark)
                    result = func(*args, **kwargs)
                    bstack11l1l11ll_opy_.end(label, start_mark, end_mark, status=True, failure=None, hook_type=hook_type,test_name=bstack1l1l1llll_opy_)
            except Exception as e:
                bstack11l1l11ll_opy_.end(label, start_mark, end_mark, status=False, failure=str(e), hook_type=hook_type,
                                       test_name=bstack1l1l1llll_opy_)
            return result
        return wrapper
    return decorator