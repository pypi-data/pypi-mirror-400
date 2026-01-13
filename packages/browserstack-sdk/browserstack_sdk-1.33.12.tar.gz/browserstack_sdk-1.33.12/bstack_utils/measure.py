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
import logging
from functools import wraps
from typing import Optional
from bstack_utils.constants import EVENTS, STAGE
from bstack_utils.bstack111lll1l1_opy_ import get_logger
from bstack_utils.bstack11l11l11ll_opy_ import bstack1lll111111l_opy_
bstack11l11l11ll_opy_ = bstack1lll111111l_opy_()
logger = get_logger(__name__)
def measure(event_name: EVENTS, stage: STAGE, hook_type: Optional[str] = None, bstack1lll1l1l1_opy_: Optional[str] = None):
    bstack11ll1_opy_ (u"ࠨࠢࠣࠌࠣࠤࠥࠦࡄࡦࡥࡲࡶࡦࡺ࡯ࡳࠢࡷࡳࠥࡲ࡯ࡨࠢࡷ࡬ࡪࠦࡳࡵࡣࡵࡸࠥࡺࡩ࡮ࡧࠣࡳ࡫ࠦࡡࠡࡨࡸࡲࡨࡺࡩࡰࡰࠣࡩࡽ࡫ࡣࡶࡶ࡬ࡳࡳࠐࠠࠡࠢࠣࡥࡱࡵ࡮ࡨࠢࡺ࡭ࡹ࡮ࠠࡦࡸࡨࡲࡹࠦ࡮ࡢ࡯ࡨࠤࡦࡴࡤࠡࡵࡷࡥ࡬࡫࠮ࠋࠢࠣࠤࠥࠨࠢࠣẴ")
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            label: str = event_name.value
            bstack1lll1l1ll11_opy_: str = bstack11l11l11ll_opy_.bstack11ll1111l1l_opy_(label)
            start_mark: str = label + bstack11ll1_opy_ (u"ࠢ࠻ࡵࡷࡥࡷࡺࠢẵ")
            end_mark: str = label + bstack11ll1_opy_ (u"ࠣ࠼ࡨࡲࡩࠨẶ")
            result = None
            try:
                if stage.value == STAGE.bstack11l11ll11l_opy_.value:
                    bstack11l11l11ll_opy_.mark(start_mark)
                    result = func(*args, **kwargs)
                elif stage.value == STAGE.END.value:
                    result = func(*args, **kwargs)
                    bstack11l11l11ll_opy_.end(label, start_mark, end_mark, status=True, failure=None,hook_type=hook_type,test_name=bstack1lll1l1l1_opy_)
                elif stage.value == STAGE.bstack11l1llll1_opy_.value:
                    start_mark: str = bstack1lll1l1ll11_opy_ + bstack11ll1_opy_ (u"ࠤ࠽ࡷࡹࡧࡲࡵࠤặ")
                    end_mark: str = bstack1lll1l1ll11_opy_ + bstack11ll1_opy_ (u"ࠥ࠾ࡪࡴࡤࠣẸ")
                    bstack11l11l11ll_opy_.mark(start_mark)
                    result = func(*args, **kwargs)
                    bstack11l11l11ll_opy_.end(label, start_mark, end_mark, status=True, failure=None, hook_type=hook_type,test_name=bstack1lll1l1l1_opy_)
            except Exception as e:
                bstack11l11l11ll_opy_.end(label, start_mark, end_mark, status=False, failure=str(e), hook_type=hook_type,
                                       test_name=bstack1lll1l1l1_opy_)
            return result
        return wrapper
    return decorator