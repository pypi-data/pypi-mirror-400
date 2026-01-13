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
import traceback
from typing import Dict, Tuple, Callable, Type, List, Any
from urllib.parse import urlparse
from browserstack_sdk.sdk_cli.bstack1ll11l1l1l1_opy_ import (
    bstack1ll1l1111l1_opy_,
    bstack1ll1l1ll1l1_opy_,
    bstack1ll11lllll1_opy_,
    bstack1ll11lll1ll_opy_,
)
import copy
from datetime import datetime, timezone, timedelta
class bstack1ll11l11l1l_opy_(bstack1ll1l1111l1_opy_):
    bstack1ll11l1llll_opy_ = bstack11ll1_opy_ (u"ࠥࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡓࡐࡆ࡚ࡆࡐࡔࡐࡣࡎࡔࡄࡆ࡚ࠥቸ")
    bstack1ll11ll1111_opy_ = bstack11ll1_opy_ (u"ࠦ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟ࡴࡧࡶࡷ࡮ࡵ࡮ࡠ࡫ࡧࠦቹ")
    bstack1ll1l1ll111_opy_ = bstack11ll1_opy_ (u"ࠧ࡮ࡵࡣࡡࡸࡶࡱࠨቺ")
    bstack1ll11ll1l11_opy_ = bstack11ll1_opy_ (u"ࠨࡣࡢࡲࡤࡦ࡮ࡲࡩࡵ࡫ࡨࡷࠧቻ")
    bstack1ll1l1lll1l_opy_ = bstack11ll1_opy_ (u"ࠢࡸ࠵ࡦࡩࡽ࡫ࡣࡶࡶࡨࡷࡨࡸࡩࡱࡶࠥቼ")
    bstack1ll11lll1l1_opy_ = bstack11ll1_opy_ (u"ࠣࡹ࠶ࡧࡪࡾࡥࡤࡷࡷࡩࡸࡩࡲࡪࡲࡷࡥࡸࡿ࡮ࡤࠤች")
    NAME = bstack11ll1_opy_ (u"ࠤࡳࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹࠨቾ")
    bstack1ll11l111l1_opy_: Dict[str, List[Callable]] = dict()
    platform_index: int
    options: Any
    desired_capabilities: Any
    bstack1ll1l1l1111_opy_: Any
    bstack1ll1l11ll1l_opy_: Dict
    def __init__(
        self,
        platform_index: int,
        framework_name: str,
        framework_version: str,
        classes: List[Type],
        methods=[bstack11ll1_opy_ (u"ࠥࡰࡦࡻ࡮ࡤࡪࠥቿ"), bstack11ll1_opy_ (u"ࠦࡨࡵ࡮࡯ࡧࡦࡸࠧኀ"), bstack11ll1_opy_ (u"ࠧࡴࡥࡸࡡࡳࡥ࡬࡫ࠢኁ"), bstack11ll1_opy_ (u"ࠨࡣ࡭ࡱࡶࡩࠧኂ"), bstack11ll1_opy_ (u"ࠢࡥ࡫ࡶࡴࡦࡺࡣࡩࠤኃ")],
    ):
        super().__init__(
            framework_name,
            framework_version,
            classes,
        )
        self.platform_index = platform_index
        self.bstack1ll11ll1l1l_opy_(methods)
    def bstack1ll1l11l1ll_opy_(self, instance: bstack1ll1l1ll1l1_opy_, method_name: str, bstack1ll1l11l1l1_opy_: timedelta, *args, **kwargs):
        pass
    def bstack1ll1l11llll_opy_(
        self,
        target: object,
        exec: Tuple[bstack1ll1l1ll1l1_opy_, str],
        bstack1lll1lll111_opy_: Tuple[bstack1ll11lllll1_opy_, bstack1ll11lll1ll_opy_],
        result: Any,
        *args,
        **kwargs,
    ) -> Callable[..., Any]:
        instance, method_name = exec
        bstack1ll1l1111ll_opy_, bstack1ll1l1lll11_opy_ = bstack1lll1lll111_opy_
        bstack1ll1l1l111l_opy_ = bstack1ll11l11l1l_opy_.bstack1ll1l111lll_opy_(bstack1lll1lll111_opy_)
        if bstack1ll1l1l111l_opy_ in bstack1ll11l11l1l_opy_.bstack1ll11l111l1_opy_:
            bstack1ll11ll111l_opy_ = None
            for callback in bstack1ll11l11l1l_opy_.bstack1ll11l111l1_opy_[bstack1ll1l1l111l_opy_]:
                try:
                    bstack1ll11llllll_opy_ = callback(self, target, exec, bstack1lll1lll111_opy_, result, *args, **kwargs)
                    if bstack1ll11ll111l_opy_ == None:
                        bstack1ll11ll111l_opy_ = bstack1ll11llllll_opy_
                except Exception as e:
                    self.logger.error(bstack11ll1_opy_ (u"ࠣࡧࡵࡶࡴࡸࠠࡪࡰࡹࡳࡰ࡯࡮ࡨࠢࡦࡥࡱࡲࡢࡢࡥ࡮࠾ࠥࠨኄ") + str(e) + bstack11ll1_opy_ (u"ࠤࠥኅ"))
                    traceback.print_exc()
            if bstack1ll1l1lll11_opy_ == bstack1ll11lll1ll_opy_.PRE and callable(bstack1ll11ll111l_opy_):
                return bstack1ll11ll111l_opy_
            elif bstack1ll1l1lll11_opy_ == bstack1ll11lll1ll_opy_.POST and bstack1ll11ll111l_opy_:
                return bstack1ll11ll111l_opy_
    def bstack1ll11l11ll1_opy_(
        self, method_name, previous_state: bstack1ll11lllll1_opy_, *args, **kwargs
    ) -> bstack1ll11lllll1_opy_:
        if method_name == bstack11ll1_opy_ (u"ࠪࡰࡦࡻ࡮ࡤࡪࠪኆ") or method_name == bstack11ll1_opy_ (u"ࠫࡨࡵ࡮࡯ࡧࡦࡸࠬኇ") or method_name == bstack11ll1_opy_ (u"ࠬࡴࡥࡸࡡࡳࡥ࡬࡫ࠧኈ"):
            return bstack1ll11lllll1_opy_.bstack1ll11l1ll1l_opy_
        if method_name == bstack11ll1_opy_ (u"࠭ࡤࡪࡵࡳࡥࡹࡩࡨࠨ኉"):
            return bstack1ll11lllll1_opy_.bstack1ll11l11l11_opy_
        if method_name == bstack11ll1_opy_ (u"ࠧࡤ࡮ࡲࡷࡪ࠭ኊ"):
            return bstack1ll11lllll1_opy_.QUIT
        return bstack1ll11lllll1_opy_.NONE
    @staticmethod
    def bstack1ll1l111lll_opy_(bstack1lll1lll111_opy_: Tuple[bstack1ll11lllll1_opy_, bstack1ll11lll1ll_opy_]):
        return bstack11ll1_opy_ (u"ࠣ࠼ࠥኋ").join((bstack1ll11lllll1_opy_(bstack1lll1lll111_opy_[0]).name, bstack1ll11lll1ll_opy_(bstack1lll1lll111_opy_[1]).name))
    @staticmethod
    def bstack1ll1l11111l_opy_(bstack1lll1lll111_opy_: Tuple[bstack1ll11lllll1_opy_, bstack1ll11lll1ll_opy_], callback: Callable):
        bstack1ll1l1l111l_opy_ = bstack1ll11l11l1l_opy_.bstack1ll1l111lll_opy_(bstack1lll1lll111_opy_)
        if not bstack1ll1l1l111l_opy_ in bstack1ll11l11l1l_opy_.bstack1ll11l111l1_opy_:
            bstack1ll11l11l1l_opy_.bstack1ll11l111l1_opy_[bstack1ll1l1l111l_opy_] = []
        bstack1ll11l11l1l_opy_.bstack1ll11l111l1_opy_[bstack1ll1l1l111l_opy_].append(callback)
    @staticmethod
    def bstack1ll1l1ll1ll_opy_(method_name: str):
        return True
    @staticmethod
    def bstack1ll1l11lll1_opy_(method_name: str, *args) -> bool:
        return True
    @staticmethod
    def bstack1ll11ll1ll1_opy_(instance: bstack1ll1l1ll1l1_opy_, default_value=None):
        return bstack1ll1l1111l1_opy_.bstack1ll1llll11l_opy_(instance, bstack1ll11l11l1l_opy_.bstack1ll11ll1l11_opy_, default_value)
    @staticmethod
    def bstack1ll11l11lll_opy_(instance: bstack1ll1l1ll1l1_opy_) -> bool:
        return True
    @staticmethod
    def bstack1ll1l1l11l1_opy_(instance: bstack1ll1l1ll1l1_opy_, default_value=None):
        return bstack1ll1l1111l1_opy_.bstack1ll1llll11l_opy_(instance, bstack1ll11l11l1l_opy_.bstack1ll1l1ll111_opy_, default_value)
    @staticmethod
    def bstack1ll11l1l111_opy_(*args):
        return args[0] if args and type(args) in [list, tuple] and isinstance(args[0], str) else None
    @staticmethod
    def bstack1ll1l111111_opy_(method_name: str, *args):
        if not bstack1ll11l11l1l_opy_.bstack1ll1l1ll1ll_opy_(method_name):
            return False
        if not bstack1ll11l11l1l_opy_.bstack1ll1l1lll1l_opy_ in bstack1ll11l11l1l_opy_.bstack1ll11llll1l_opy_(*args):
            return False
        bstack1ll1l1l11ll_opy_ = bstack1ll11l11l1l_opy_.bstack1ll1l111l1l_opy_(*args)
        return bstack1ll1l1l11ll_opy_ and bstack11ll1_opy_ (u"ࠤࡶࡧࡷ࡯ࡰࡵࠤኌ") in bstack1ll1l1l11ll_opy_ and bstack11ll1_opy_ (u"ࠥࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡨࡼࡪࡩࡵࡵࡱࡵࠦኍ") in bstack1ll1l1l11ll_opy_[bstack11ll1_opy_ (u"ࠦࡸࡩࡲࡪࡲࡷࠦ኎")]
    @staticmethod
    def bstack1ll11lll111_opy_(method_name: str, *args):
        if not bstack1ll11l11l1l_opy_.bstack1ll1l1ll1ll_opy_(method_name):
            return False
        if not bstack1ll11l11l1l_opy_.bstack1ll1l1lll1l_opy_ in bstack1ll11l11l1l_opy_.bstack1ll11llll1l_opy_(*args):
            return False
        bstack1ll1l1l11ll_opy_ = bstack1ll11l11l1l_opy_.bstack1ll1l111l1l_opy_(*args)
        return (
            bstack1ll1l1l11ll_opy_
            and bstack11ll1_opy_ (u"ࠧࡹࡣࡳ࡫ࡳࡸࠧ኏") in bstack1ll1l1l11ll_opy_
            and bstack11ll1_opy_ (u"ࠨࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࡤࡧࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࡡࡶࡧࡷ࡯ࡰࡵࠤነ") in bstack1ll1l1l11ll_opy_[bstack11ll1_opy_ (u"ࠢࡴࡥࡵ࡭ࡵࡺࠢኑ")]
        )
    @staticmethod
    def bstack1ll11llll1l_opy_(*args):
        return str(bstack1ll11l11l1l_opy_.bstack1ll11l1l111_opy_(*args)).lower()