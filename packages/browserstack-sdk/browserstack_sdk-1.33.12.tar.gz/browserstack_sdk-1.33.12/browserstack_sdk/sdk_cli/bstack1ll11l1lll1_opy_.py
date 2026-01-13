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
from bstack_utils.bstack11l11l11ll_opy_ import bstack1lll111111l_opy_
from bstack_utils.constants import EVENTS
class bstack1ll11ll1lll_opy_(bstack1ll1l1111l1_opy_):
    bstack1ll11l1llll_opy_ = bstack11ll1_opy_ (u"ࠤࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡒࡏࡅ࡙ࡌࡏࡓࡏࡢࡍࡓࡊࡅ࡙ࠤሿ")
    NAME = bstack11ll1_opy_ (u"ࠥࡷࡪࡲࡥ࡯࡫ࡸࡱࠧቀ")
    bstack1ll1l1ll111_opy_ = bstack11ll1_opy_ (u"ࠦ࡭ࡻࡢࡠࡷࡵࡰࠧቁ")
    bstack1ll11ll1111_opy_ = bstack11ll1_opy_ (u"ࠧ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡵࡨࡷࡸ࡯࡯࡯ࡡ࡬ࡨࠧቂ")
    bstack1ll11ll11l1_opy_ = bstack11ll1_opy_ (u"ࠨࡩ࡯ࡲࡸࡸࡤࡩࡡࡱࡣࡥ࡭ࡱ࡯ࡴࡪࡧࡶࠦቃ")
    bstack1ll11ll1l11_opy_ = bstack11ll1_opy_ (u"ࠢࡤࡣࡳࡥࡧ࡯࡬ࡪࡶ࡬ࡩࡸࠨቄ")
    bstack1ll11ll11ll_opy_ = bstack11ll1_opy_ (u"ࠣ࡫ࡶࡣࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢ࡬ࡺࡨࠢቅ")
    bstack1ll1l11l11l_opy_ = bstack11ll1_opy_ (u"ࠤࡶࡸࡦࡸࡴࡦࡦࡢࡥࡹࠨቆ")
    bstack1ll1l1l1l1l_opy_ = bstack11ll1_opy_ (u"ࠥࡩࡳࡪࡥࡥࡡࡤࡸࠧቇ")
    bstack1lll11l1l1l_opy_ = bstack11ll1_opy_ (u"ࠦࡵࡲࡡࡵࡨࡲࡶࡲࡥࡩ࡯ࡦࡨࡼࠧቈ")
    bstack1ll1l1l1ll1_opy_ = bstack11ll1_opy_ (u"ࠧࡴࡥࡸࡵࡨࡷࡸ࡯࡯࡯ࠤ቉")
    bstack1ll11lll11l_opy_ = bstack11ll1_opy_ (u"ࠨࡧࡦࡶࠥቊ")
    bstack1ll1l1ll11l_opy_ = bstack11ll1_opy_ (u"ࠢࡴࡥࡵࡩࡪࡴࡳࡩࡱࡷࠦቋ")
    bstack1ll1l1lll1l_opy_ = bstack11ll1_opy_ (u"ࠣࡹ࠶ࡧࡪࡾࡥࡤࡷࡷࡩࡸࡩࡲࡪࡲࡷࠦቌ")
    bstack1ll11lll1l1_opy_ = bstack11ll1_opy_ (u"ࠤࡺ࠷ࡨ࡫ࡸࡦࡥࡸࡸࡪࡹࡣࡳ࡫ࡳࡸࡦࡹࡹ࡯ࡥࠥቍ")
    bstack1ll1l111l11_opy_ = bstack11ll1_opy_ (u"ࠥࡵࡺ࡯ࡴࠣ቎")
    bstack1ll1l1l1l11_opy_: Dict[str, List[Callable]] = dict()
    bstack1ll11llll11_opy_: str
    platform_index: int
    options: Any
    desired_capabilities: Any
    bstack1ll1l1l1111_opy_: Any
    bstack1ll1l11ll1l_opy_: Dict
    def __init__(
        self,
        bstack1ll11llll11_opy_: str,
        platform_index: int,
        framework_name: str,
        framework_version: str,
        classes: List[Type],
        bstack1ll1l1l1111_opy_: Dict[str, Any],
        methods=[bstack11ll1_opy_ (u"ࠦࡤࡥࡩ࡯࡫ࡷࡣࡤࠨ቏"), bstack11ll1_opy_ (u"ࠧࡹࡴࡢࡴࡷࡣࡸ࡫ࡳࡴ࡫ࡲࡲࠧቐ"), bstack11ll1_opy_ (u"ࠨࡥࡹࡧࡦࡹࡹ࡫ࠢቑ"), bstack11ll1_opy_ (u"ࠢࡲࡷ࡬ࡸࠧቒ")],
    ):
        super().__init__(
            framework_name,
            framework_version,
            classes,
        )
        self.bstack1ll11llll11_opy_ = bstack1ll11llll11_opy_
        self.platform_index = platform_index
        self.bstack1ll11ll1l1l_opy_(methods)
        self.bstack1ll1l1l1111_opy_ = bstack1ll1l1l1111_opy_
    @staticmethod
    def session_id(target: object, strict=True):
        return bstack1ll1l1111l1_opy_.get_data(bstack1ll11ll1lll_opy_.bstack1ll11ll1111_opy_, target, strict)
    @staticmethod
    def hub_url(target: object, strict=True):
        return bstack1ll1l1111l1_opy_.get_data(bstack1ll11ll1lll_opy_.bstack1ll1l1ll111_opy_, target, strict)
    @staticmethod
    def bstack1ll1l11l111_opy_(target: object, strict=True):
        return bstack1ll1l1111l1_opy_.get_data(bstack1ll11ll1lll_opy_.bstack1ll11ll11l1_opy_, target, strict)
    @staticmethod
    def capabilities(target: object, strict=True):
        return bstack1ll1l1111l1_opy_.get_data(bstack1ll11ll1lll_opy_.bstack1ll11ll1l11_opy_, target, strict)
    @staticmethod
    def bstack1ll11l11lll_opy_(instance: bstack1ll1l1ll1l1_opy_) -> bool:
        return bstack1ll1l1111l1_opy_.bstack1ll1llll11l_opy_(instance, bstack1ll11ll1lll_opy_.bstack1ll11ll11ll_opy_, False)
    @staticmethod
    def bstack1ll1l1l11l1_opy_(instance: bstack1ll1l1ll1l1_opy_, default_value=None):
        return bstack1ll1l1111l1_opy_.bstack1ll1llll11l_opy_(instance, bstack1ll11ll1lll_opy_.bstack1ll1l1ll111_opy_, default_value)
    @staticmethod
    def bstack1ll11ll1ll1_opy_(instance: bstack1ll1l1ll1l1_opy_, default_value=None):
        return bstack1ll1l1111l1_opy_.bstack1ll1llll11l_opy_(instance, bstack1ll11ll1lll_opy_.bstack1ll11ll1l11_opy_, default_value)
    @staticmethod
    def bstack1ll11l1l11l_opy_(hub_url: str, bstack1ll11l1ll11_opy_=bstack11ll1_opy_ (u"ࠣ࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡥࡲࡱࠧቓ")):
        try:
            bstack1ll1l1l1lll_opy_ = str(urlparse(hub_url).netloc) if hub_url else None
            return bstack1ll1l1l1lll_opy_.endswith(bstack1ll11l1ll11_opy_)
        except:
            pass
        return False
    @staticmethod
    def bstack1ll1l1ll1ll_opy_(method_name: str):
        return method_name == bstack11ll1_opy_ (u"ࠤࡨࡼࡪࡩࡵࡵࡧࠥቔ")
    @staticmethod
    def bstack1ll1l11lll1_opy_(method_name: str, *args):
        return (
            bstack1ll11ll1lll_opy_.bstack1ll1l1ll1ll_opy_(method_name)
            and bstack1ll11ll1lll_opy_.bstack1ll11llll1l_opy_(*args) == bstack1ll11ll1lll_opy_.bstack1ll1l1l1ll1_opy_
        )
    @staticmethod
    def bstack1ll1l111111_opy_(method_name: str, *args):
        if not bstack1ll11ll1lll_opy_.bstack1ll1l1ll1ll_opy_(method_name):
            return False
        if not bstack1ll11ll1lll_opy_.bstack1ll1l1lll1l_opy_ in bstack1ll11ll1lll_opy_.bstack1ll11llll1l_opy_(*args):
            return False
        bstack1ll1l1l11ll_opy_ = bstack1ll11ll1lll_opy_.bstack1ll1l111l1l_opy_(*args)
        return bstack1ll1l1l11ll_opy_ and bstack11ll1_opy_ (u"ࠥࡷࡨࡸࡩࡱࡶࠥቕ") in bstack1ll1l1l11ll_opy_ and bstack11ll1_opy_ (u"ࠦࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡩࡽ࡫ࡣࡶࡶࡲࡶࠧቖ") in bstack1ll1l1l11ll_opy_[bstack11ll1_opy_ (u"ࠧࡹࡣࡳ࡫ࡳࡸࠧ቗")]
    @staticmethod
    def bstack1ll11lll111_opy_(method_name: str, *args):
        if not bstack1ll11ll1lll_opy_.bstack1ll1l1ll1ll_opy_(method_name):
            return False
        if not bstack1ll11ll1lll_opy_.bstack1ll1l1lll1l_opy_ in bstack1ll11ll1lll_opy_.bstack1ll11llll1l_opy_(*args):
            return False
        bstack1ll1l1l11ll_opy_ = bstack1ll11ll1lll_opy_.bstack1ll1l111l1l_opy_(*args)
        return (
            bstack1ll1l1l11ll_opy_
            and bstack11ll1_opy_ (u"ࠨࡳࡤࡴ࡬ࡴࡹࠨቘ") in bstack1ll1l1l11ll_opy_
            and bstack11ll1_opy_ (u"ࠢࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࡥࡡࡶࡶࡲࡱࡦࡺࡩࡰࡰࡢࡷࡨࡸࡩࡱࡶࠥ቙") in bstack1ll1l1l11ll_opy_[bstack11ll1_opy_ (u"ࠣࡵࡦࡶ࡮ࡶࡴࠣቚ")]
        )
    @staticmethod
    def bstack1ll11llll1l_opy_(*args):
        return str(bstack1ll11ll1lll_opy_.bstack1ll11l1l111_opy_(*args)).lower()
    @staticmethod
    def bstack1ll11l1l111_opy_(*args):
        return args[0] if args and type(args) in [list, tuple] and isinstance(args[0], str) else None
    @staticmethod
    def bstack1ll1l111l1l_opy_(*args):
        return args[1] if len(args) > 1 and isinstance(args[1], dict) else None
    @staticmethod
    def bstack1l1l11l11_opy_(driver):
        command_executor = getattr(driver, bstack11ll1_opy_ (u"ࠤࡦࡳࡲࡳࡡ࡯ࡦࡢࡩࡽ࡫ࡣࡶࡶࡲࡶࠧቛ"), None)
        if not command_executor:
            return None
        hub_url = str(command_executor) if isinstance(command_executor, (str, bytes)) else None
        hub_url = str(command_executor._url) if not hub_url and getattr(command_executor, bstack11ll1_opy_ (u"ࠥࡣࡺࡸ࡬ࠣቜ"), None) else None
        if not hub_url:
            client_config = getattr(command_executor, bstack11ll1_opy_ (u"ࠦࡤࡩ࡬ࡪࡧࡱࡸࡤࡩ࡯࡯ࡨ࡬࡫ࠧቝ"), None)
            if not client_config:
                return None
            hub_url = getattr(client_config, bstack11ll1_opy_ (u"ࠧࡸࡥ࡮ࡱࡷࡩࡤࡹࡥࡳࡸࡨࡶࡤࡧࡤࡥࡴࠥ቞"), None)
        return hub_url
    def bstack1ll1l11ll11_opy_(self, instance, driver, hub_url: str):
        result = False
        if not hub_url:
            return result
        command_executor = getattr(driver, bstack11ll1_opy_ (u"ࠨࡣࡰ࡯ࡰࡥࡳࡪ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳࠤ቟"), None)
        if command_executor:
            if isinstance(command_executor, (str, bytes)):
                setattr(driver, bstack11ll1_opy_ (u"ࠢࡤࡱࡰࡱࡦࡴࡤࡠࡧࡻࡩࡨࡻࡴࡰࡴࠥበ"), hub_url)
                result = True
            elif hasattr(command_executor, bstack11ll1_opy_ (u"ࠣࡡࡸࡶࡱࠨቡ")):
                setattr(command_executor, bstack11ll1_opy_ (u"ࠤࡢࡹࡷࡲࠢቢ"), hub_url)
                result = True
        if result:
            self.bstack1ll11llll11_opy_ = hub_url
            bstack1ll11ll1lll_opy_.bstack1lll111ll11_opy_(instance, bstack1ll11ll1lll_opy_.bstack1ll1l1ll111_opy_, hub_url)
            bstack1ll11ll1lll_opy_.bstack1lll111ll11_opy_(
                instance, bstack1ll11ll1lll_opy_.bstack1ll11ll11ll_opy_, bstack1ll11ll1lll_opy_.bstack1ll11l1l11l_opy_(hub_url)
            )
        return result
    @staticmethod
    def bstack1ll1l111lll_opy_(bstack1lll1lll111_opy_: Tuple[bstack1ll11lllll1_opy_, bstack1ll11lll1ll_opy_]):
        return bstack11ll1_opy_ (u"ࠥ࠾ࠧባ").join((bstack1ll11lllll1_opy_(bstack1lll1lll111_opy_[0]).name, bstack1ll11lll1ll_opy_(bstack1lll1lll111_opy_[1]).name))
    @staticmethod
    def bstack1ll1l11111l_opy_(bstack1lll1lll111_opy_: Tuple[bstack1ll11lllll1_opy_, bstack1ll11lll1ll_opy_], callback: Callable):
        bstack1ll1l1l111l_opy_ = bstack1ll11ll1lll_opy_.bstack1ll1l111lll_opy_(bstack1lll1lll111_opy_)
        if not bstack1ll1l1l111l_opy_ in bstack1ll11ll1lll_opy_.bstack1ll1l1l1l11_opy_:
            bstack1ll11ll1lll_opy_.bstack1ll1l1l1l11_opy_[bstack1ll1l1l111l_opy_] = []
        bstack1ll11ll1lll_opy_.bstack1ll1l1l1l11_opy_[bstack1ll1l1l111l_opy_].append(callback)
    def bstack1ll1l11l1ll_opy_(self, instance: bstack1ll1l1ll1l1_opy_, method_name: str, bstack1ll1l11l1l1_opy_: timedelta, *args, **kwargs):
        if not instance or method_name in (bstack11ll1_opy_ (u"ࠦࡸࡺࡡࡳࡶࡢࡷࡪࡹࡳࡪࡱࡱࠦቤ")):
            return
        cmd = args[0] if method_name == bstack11ll1_opy_ (u"ࠧ࡫ࡸࡦࡥࡸࡸࡪࠨብ") and args and type(args) in [list, tuple] and isinstance(args[0], str) else None
        bstack1ll1l111ll1_opy_ = bstack11ll1_opy_ (u"ࠨ࠺ࠣቦ").join(map(str, filter(None, [method_name, cmd])))
        instance.bstack1lll1lll1_opy_(bstack11ll1_opy_ (u"ࠢࡥࡴ࡬ࡺࡪࡸ࠺ࠣቧ") + bstack1ll1l111ll1_opy_, bstack1ll1l11l1l1_opy_)
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
        bstack1ll1l1l111l_opy_ = bstack1ll11ll1lll_opy_.bstack1ll1l111lll_opy_(bstack1lll1lll111_opy_)
        self.logger.debug(bstack11ll1_opy_ (u"ࠣࡱࡱࡣ࡭ࡵ࡯࡬࠼ࠣࡱࡪࡺࡨࡰࡦࡢࡲࡦࡳࡥ࠾ࡽࡰࡩࡹ࡮࡯ࡥࡡࡱࡥࡲ࡫ࡽࠡࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࡁࢀ࡮࡯ࡰ࡭ࡢ࡭ࡳ࡬࡯ࡾࠢࡤࡶ࡬ࡹ࠽ࡼࡣࡵ࡫ࡸࢃࠠ࡬ࡹࡤࡶ࡬ࡹ࠽ࠣቨ") + str(kwargs) + bstack11ll1_opy_ (u"ࠤࠥቩ"))
        if bstack1ll1l1111ll_opy_ == bstack1ll11lllll1_opy_.QUIT:
            if bstack1ll1l1lll11_opy_ == bstack1ll11lll1ll_opy_.PRE:
                bstack1lll1l1ll11_opy_ = bstack1lll111111l_opy_.bstack1lll1111lll_opy_(EVENTS.bstack1lll111l1_opy_.value)
                bstack1ll1l1111l1_opy_.bstack1lll111ll11_opy_(instance, EVENTS.bstack1lll111l1_opy_.value, bstack1lll1l1ll11_opy_)
                self.logger.debug(bstack11ll1_opy_ (u"ࠥ࡭ࡳࡹࡴࡢࡰࡦࡩࡂࢁࡽࠡ࡯ࡨࡸ࡭ࡵࡤࡠࡰࡤࡱࡪࡃࡻࡾࠢࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࡤࡹࡴࡢࡶࡨࡁࢀࢃࠠࡩࡱࡲ࡯ࡤࡹࡴࡢࡶࡨࡁࢀࢃࠢቪ").format(instance, method_name, bstack1ll1l1111ll_opy_, bstack1ll1l1lll11_opy_))
        if bstack1ll1l1111ll_opy_ == bstack1ll11lllll1_opy_.bstack1ll11l1ll1l_opy_:
            if bstack1ll1l1lll11_opy_ == bstack1ll11lll1ll_opy_.POST and not bstack1ll11ll1lll_opy_.bstack1ll11ll1111_opy_ in instance.data:
                session_id = getattr(target, bstack11ll1_opy_ (u"ࠦࡸ࡫ࡳࡴ࡫ࡲࡲࡤ࡯ࡤࠣቫ"), None)
                if session_id:
                    instance.data[bstack1ll11ll1lll_opy_.bstack1ll11ll1111_opy_] = session_id
        elif (
            bstack1ll1l1111ll_opy_ == bstack1ll11lllll1_opy_.bstack1ll11l1l1ll_opy_
            and bstack1ll11ll1lll_opy_.bstack1ll11llll1l_opy_(*args) == bstack1ll11ll1lll_opy_.bstack1ll1l1l1ll1_opy_
        ):
            if bstack1ll1l1lll11_opy_ == bstack1ll11lll1ll_opy_.PRE:
                hub_url = bstack1ll11ll1lll_opy_.bstack1l1l11l11_opy_(target)
                if hub_url:
                    instance.data.update(
                        {
                            bstack1ll11ll1lll_opy_.bstack1ll1l1ll111_opy_: hub_url,
                            bstack1ll11ll1lll_opy_.bstack1ll11ll11ll_opy_: bstack1ll11ll1lll_opy_.bstack1ll11l1l11l_opy_(hub_url),
                            bstack1ll11ll1lll_opy_.bstack1lll11l1l1l_opy_: int(
                                os.environ.get(bstack11ll1_opy_ (u"ࠧࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡕࡒࡁࡕࡈࡒࡖࡒࡥࡉࡏࡆࡈ࡜ࠧቬ"), str(self.platform_index))
                            ),
                        }
                    )
                bstack1ll1l1l11ll_opy_ = bstack1ll11ll1lll_opy_.bstack1ll1l111l1l_opy_(*args)
                bstack1ll1l11l111_opy_ = bstack1ll1l1l11ll_opy_.get(bstack11ll1_opy_ (u"ࠨࡣࡢࡲࡤࡦ࡮ࡲࡩࡵ࡫ࡨࡷࠧቭ"), None) if bstack1ll1l1l11ll_opy_ else None
                if isinstance(bstack1ll1l11l111_opy_, dict):
                    instance.data[bstack1ll11ll1lll_opy_.bstack1ll11ll11l1_opy_] = copy.deepcopy(bstack1ll1l11l111_opy_)
                    instance.data[bstack1ll11ll1lll_opy_.bstack1ll11ll1l11_opy_] = bstack1ll1l11l111_opy_
            elif bstack1ll1l1lll11_opy_ == bstack1ll11lll1ll_opy_.POST:
                if isinstance(result, dict):
                    framework_session_id = result.get(bstack11ll1_opy_ (u"ࠢࡷࡣ࡯ࡹࡪࠨቮ"), dict()).get(bstack11ll1_opy_ (u"ࠣࡵࡨࡷࡸ࡯࡯࡯ࡋࡧࠦቯ"), None)
                    if framework_session_id:
                        instance.data.update(
                            {
                                bstack1ll11ll1lll_opy_.bstack1ll11ll1111_opy_: framework_session_id,
                                bstack1ll11ll1lll_opy_.bstack1ll1l11l11l_opy_: datetime.now(tz=timezone.utc),
                            }
                        )
        elif (
            bstack1ll1l1111ll_opy_ == bstack1ll11lllll1_opy_.bstack1ll11l1l1ll_opy_
            and bstack1ll11ll1lll_opy_.bstack1ll11llll1l_opy_(*args) == bstack1ll11ll1lll_opy_.bstack1ll1l111l11_opy_
            and bstack1ll1l1lll11_opy_ == bstack1ll11lll1ll_opy_.POST
        ):
            instance.data[bstack1ll11ll1lll_opy_.bstack1ll1l1l1l1l_opy_] = datetime.now(tz=timezone.utc)
        if bstack1ll1l1l111l_opy_ in bstack1ll11ll1lll_opy_.bstack1ll1l1l1l11_opy_:
            bstack1ll11ll111l_opy_ = None
            for callback in bstack1ll11ll1lll_opy_.bstack1ll1l1l1l11_opy_[bstack1ll1l1l111l_opy_]:
                try:
                    bstack1ll11llllll_opy_ = callback(self, target, exec, bstack1lll1lll111_opy_, result, *args, **kwargs)
                    if bstack1ll11ll111l_opy_ == None:
                        bstack1ll11ll111l_opy_ = bstack1ll11llllll_opy_
                except Exception as e:
                    self.logger.error(bstack11ll1_opy_ (u"ࠤࡨࡶࡷࡵࡲࠡ࡫ࡱࡺࡴࡱࡩ࡯ࡩࠣࡧࡦࡲ࡬ࡣࡣࡦ࡯࠿ࠦࠢተ") + str(e) + bstack11ll1_opy_ (u"ࠥࠦቱ"))
                    traceback.print_exc()
            if bstack1ll1l1111ll_opy_ == bstack1ll11lllll1_opy_.QUIT:
                if bstack1ll1l1lll11_opy_ == bstack1ll11lll1ll_opy_.POST:
                    bstack1lll1l1ll11_opy_ = bstack1ll1l1111l1_opy_.bstack1ll1llll11l_opy_(instance, EVENTS.bstack1lll111l1_opy_.value)
                    if bstack1lll1l1ll11_opy_!=None:
                        bstack1lll111111l_opy_.end(EVENTS.bstack1lll111l1_opy_.value, bstack1lll1l1ll11_opy_+bstack11ll1_opy_ (u"ࠦ࠿ࡹࡴࡢࡴࡷࠦቲ"), bstack1lll1l1ll11_opy_+bstack11ll1_opy_ (u"ࠧࡀࡥ࡯ࡦࠥታ"), True, None)
            if bstack1ll1l1lll11_opy_ == bstack1ll11lll1ll_opy_.PRE and callable(bstack1ll11ll111l_opy_):
                return bstack1ll11ll111l_opy_
            elif bstack1ll1l1lll11_opy_ == bstack1ll11lll1ll_opy_.POST and bstack1ll11ll111l_opy_:
                return bstack1ll11ll111l_opy_
    def bstack1ll11l11ll1_opy_(
        self, method_name, previous_state: bstack1ll11lllll1_opy_, *args, **kwargs
    ) -> bstack1ll11lllll1_opy_:
        if method_name == bstack11ll1_opy_ (u"ࠨ࡟ࡠ࡫ࡱ࡭ࡹࡥ࡟ࠣቴ") or method_name == bstack11ll1_opy_ (u"ࠢࡴࡶࡤࡶࡹࡥࡳࡦࡵࡶ࡭ࡴࡴࠢት"):
            return bstack1ll11lllll1_opy_.bstack1ll11l1ll1l_opy_
        if method_name == bstack11ll1_opy_ (u"ࠣࡳࡸ࡭ࡹࠨቶ"):
            return bstack1ll11lllll1_opy_.QUIT
        if method_name == bstack11ll1_opy_ (u"ࠤࡨࡼࡪࡩࡵࡵࡧࠥቷ"):
            if previous_state != bstack1ll11lllll1_opy_.NONE:
                command_name = bstack1ll11ll1lll_opy_.bstack1ll11llll1l_opy_(*args)
                if command_name == bstack1ll11ll1lll_opy_.bstack1ll1l1l1ll1_opy_:
                    return bstack1ll11lllll1_opy_.bstack1ll11l1ll1l_opy_
            return bstack1ll11lllll1_opy_.bstack1ll11l1l1ll_opy_
        return bstack1ll11lllll1_opy_.NONE