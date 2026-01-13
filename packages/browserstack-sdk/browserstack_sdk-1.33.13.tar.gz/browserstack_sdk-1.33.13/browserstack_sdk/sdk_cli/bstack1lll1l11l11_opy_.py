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
import traceback
from typing import Dict, Tuple, Callable, Type, List, Any
from urllib.parse import urlparse
from browserstack_sdk.sdk_cli.bstack1llll11l1ll_opy_ import (
    bstack1llll111ll1_opy_,
    bstack1llll1ll1ll_opy_,
    bstack1llll1111l1_opy_,
    bstack1lll1lll1l1_opy_,
)
import copy
from datetime import datetime, timezone, timedelta
from bstack_utils.bstack11l1l11ll_opy_ import bstack1lll1ll1l11_opy_
from bstack_utils.constants import EVENTS
class bstack1lll11l111l_opy_(bstack1llll111ll1_opy_):
    bstack1l111l11111_opy_ = bstack11l1l_opy_ (u"ࠧࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡕࡒࡁࡕࡈࡒࡖࡒࡥࡉࡏࡆࡈ࡜ࠧᘏ")
    NAME = bstack11l1l_opy_ (u"ࠨࡳࡦ࡮ࡨࡲ࡮ࡻ࡭ࠣᘐ")
    bstack1l11ll1l1l1_opy_ = bstack11l1l_opy_ (u"ࠢࡩࡷࡥࡣࡺࡸ࡬ࠣᘑ")
    bstack1l11lll1l11_opy_ = bstack11l1l_opy_ (u"ࠣࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡸ࡫ࡳࡴ࡫ࡲࡲࡤ࡯ࡤࠣᘒ")
    bstack11lll111l11_opy_ = bstack11l1l_opy_ (u"ࠤ࡬ࡲࡵࡻࡴࡠࡥࡤࡴࡦࡨࡩ࡭࡫ࡷ࡭ࡪࡹࠢᘓ")
    bstack1l11ll11l1l_opy_ = bstack11l1l_opy_ (u"ࠥࡧࡦࡶࡡࡣ࡫࡯࡭ࡹ࡯ࡥࡴࠤᘔ")
    bstack1l111l1l111_opy_ = bstack11l1l_opy_ (u"ࠦ࡮ࡹ࡟ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡨࡶࡤࠥᘕ")
    bstack11ll1llll1l_opy_ = bstack11l1l_opy_ (u"ࠧࡹࡴࡢࡴࡷࡩࡩࡥࡡࡵࠤᘖ")
    bstack11ll1llllll_opy_ = bstack11l1l_opy_ (u"ࠨࡥ࡯ࡦࡨࡨࡤࡧࡴࠣᘗ")
    bstack1ll1111l111_opy_ = bstack11l1l_opy_ (u"ࠢࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡡ࡬ࡲࡩ࡫ࡸࠣᘘ")
    bstack1l111ll1ll1_opy_ = bstack11l1l_opy_ (u"ࠣࡰࡨࡻࡸ࡫ࡳࡴ࡫ࡲࡲࠧᘙ")
    bstack11ll1llll11_opy_ = bstack11l1l_opy_ (u"ࠤࡪࡩࡹࠨᘚ")
    bstack1l1l11lll1l_opy_ = bstack11l1l_opy_ (u"ࠥࡷࡨࡸࡥࡦࡰࡶ࡬ࡴࡺࠢᘛ")
    bstack1l1111llll1_opy_ = bstack11l1l_opy_ (u"ࠦࡼ࠹ࡣࡦࡺࡨࡧࡺࡺࡥࡴࡥࡵ࡭ࡵࡺࠢᘜ")
    bstack1l111l111l1_opy_ = bstack11l1l_opy_ (u"ࠧࡽ࠳ࡤࡧࡻࡩࡨࡻࡴࡦࡵࡦࡶ࡮ࡶࡴࡢࡵࡼࡲࡨࠨᘝ")
    bstack11lll1111l1_opy_ = bstack11l1l_opy_ (u"ࠨࡱࡶ࡫ࡷࠦᘞ")
    bstack11lll111l1l_opy_: Dict[str, List[Callable]] = dict()
    bstack1l111lll1ll_opy_: str
    platform_index: int
    options: Any
    desired_capabilities: Any
    bstack1lll111llll_opy_: Any
    bstack1l111l1111l_opy_: Dict
    def __init__(
        self,
        bstack1l111lll1ll_opy_: str,
        platform_index: int,
        framework_name: str,
        framework_version: str,
        classes: List[Type],
        bstack1lll111llll_opy_: Dict[str, Any],
        methods=[bstack11l1l_opy_ (u"ࠢࡠࡡ࡬ࡲ࡮ࡺ࡟ࡠࠤᘟ"), bstack11l1l_opy_ (u"ࠣࡵࡷࡥࡷࡺ࡟ࡴࡧࡶࡷ࡮ࡵ࡮ࠣᘠ"), bstack11l1l_opy_ (u"ࠤࡨࡼࡪࡩࡵࡵࡧࠥᘡ"), bstack11l1l_opy_ (u"ࠥࡵࡺ࡯ࡴࠣᘢ")],
    ):
        super().__init__(
            framework_name,
            framework_version,
            classes,
        )
        self.bstack1l111lll1ll_opy_ = bstack1l111lll1ll_opy_
        self.platform_index = platform_index
        self.bstack1lllll111l1_opy_(methods)
        self.bstack1lll111llll_opy_ = bstack1lll111llll_opy_
    @staticmethod
    def session_id(target: object, strict=True):
        return bstack1llll111ll1_opy_.get_data(bstack1lll11l111l_opy_.bstack1l11lll1l11_opy_, target, strict)
    @staticmethod
    def hub_url(target: object, strict=True):
        return bstack1llll111ll1_opy_.get_data(bstack1lll11l111l_opy_.bstack1l11ll1l1l1_opy_, target, strict)
    @staticmethod
    def bstack11lll1111ll_opy_(target: object, strict=True):
        return bstack1llll111ll1_opy_.get_data(bstack1lll11l111l_opy_.bstack11lll111l11_opy_, target, strict)
    @staticmethod
    def capabilities(target: object, strict=True):
        return bstack1llll111ll1_opy_.get_data(bstack1lll11l111l_opy_.bstack1l11ll11l1l_opy_, target, strict)
    @staticmethod
    def bstack1l1ll1l1l1l_opy_(instance: bstack1llll1ll1ll_opy_) -> bool:
        return bstack1llll111ll1_opy_.bstack1llll1lllll_opy_(instance, bstack1lll11l111l_opy_.bstack1l111l1l111_opy_, False)
    @staticmethod
    def bstack1l1llll1111_opy_(instance: bstack1llll1ll1ll_opy_, default_value=None):
        return bstack1llll111ll1_opy_.bstack1llll1lllll_opy_(instance, bstack1lll11l111l_opy_.bstack1l11ll1l1l1_opy_, default_value)
    @staticmethod
    def bstack1ll11l1l11l_opy_(instance: bstack1llll1ll1ll_opy_, default_value=None):
        return bstack1llll111ll1_opy_.bstack1llll1lllll_opy_(instance, bstack1lll11l111l_opy_.bstack1l11ll11l1l_opy_, default_value)
    @staticmethod
    def bstack1l1ll1ll111_opy_(hub_url: str, bstack11lll11111l_opy_=bstack11l1l_opy_ (u"ࠦ࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡨࡵ࡭ࠣᘣ")):
        try:
            bstack11lll111111_opy_ = str(urlparse(hub_url).netloc) if hub_url else None
            return bstack11lll111111_opy_.endswith(bstack11lll11111l_opy_)
        except:
            pass
        return False
    @staticmethod
    def bstack1ll1111l11l_opy_(method_name: str):
        return method_name == bstack11l1l_opy_ (u"ࠧ࡫ࡸࡦࡥࡸࡸࡪࠨᘤ")
    @staticmethod
    def bstack1l1lll1ll1l_opy_(method_name: str, *args):
        return (
            bstack1lll11l111l_opy_.bstack1ll1111l11l_opy_(method_name)
            and bstack1lll11l111l_opy_.bstack1l11l1l1111_opy_(*args) == bstack1lll11l111l_opy_.bstack1l111ll1ll1_opy_
        )
    @staticmethod
    def bstack1ll11111l11_opy_(method_name: str, *args):
        if not bstack1lll11l111l_opy_.bstack1ll1111l11l_opy_(method_name):
            return False
        if not bstack1lll11l111l_opy_.bstack1l1111llll1_opy_ in bstack1lll11l111l_opy_.bstack1l11l1l1111_opy_(*args):
            return False
        bstack1l1ll1lll11_opy_ = bstack1lll11l111l_opy_.bstack1l1lll1111l_opy_(*args)
        return bstack1l1ll1lll11_opy_ and bstack11l1l_opy_ (u"ࠨࡳࡤࡴ࡬ࡴࡹࠨᘥ") in bstack1l1ll1lll11_opy_ and bstack11l1l_opy_ (u"ࠢࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡥࡹࡧࡦࡹࡹࡵࡲࠣᘦ") in bstack1l1ll1lll11_opy_[bstack11l1l_opy_ (u"ࠣࡵࡦࡶ࡮ࡶࡴࠣᘧ")]
    @staticmethod
    def bstack1ll11l1111l_opy_(method_name: str, *args):
        if not bstack1lll11l111l_opy_.bstack1ll1111l11l_opy_(method_name):
            return False
        if not bstack1lll11l111l_opy_.bstack1l1111llll1_opy_ in bstack1lll11l111l_opy_.bstack1l11l1l1111_opy_(*args):
            return False
        bstack1l1ll1lll11_opy_ = bstack1lll11l111l_opy_.bstack1l1lll1111l_opy_(*args)
        return (
            bstack1l1ll1lll11_opy_
            and bstack11l1l_opy_ (u"ࠤࡶࡧࡷ࡯ࡰࡵࠤᘨ") in bstack1l1ll1lll11_opy_
            and bstack11l1l_opy_ (u"ࠥࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࡡࡤࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳࡥࡳࡤࡴ࡬ࡴࡹࠨᘩ") in bstack1l1ll1lll11_opy_[bstack11l1l_opy_ (u"ࠦࡸࡩࡲࡪࡲࡷࠦᘪ")]
        )
    @staticmethod
    def bstack1l11l1l1111_opy_(*args):
        return str(bstack1lll11l111l_opy_.bstack1ll111111l1_opy_(*args)).lower()
    @staticmethod
    def bstack1ll111111l1_opy_(*args):
        return args[0] if args and type(args) in [list, tuple] and isinstance(args[0], str) else None
    @staticmethod
    def bstack1l1lll1111l_opy_(*args):
        return args[1] if len(args) > 1 and isinstance(args[1], dict) else None
    @staticmethod
    def bstack11l111l11_opy_(driver):
        command_executor = getattr(driver, bstack11l1l_opy_ (u"ࠧࡩ࡯࡮࡯ࡤࡲࡩࡥࡥࡹࡧࡦࡹࡹࡵࡲࠣᘫ"), None)
        if not command_executor:
            return None
        hub_url = str(command_executor) if isinstance(command_executor, (str, bytes)) else None
        hub_url = str(command_executor._url) if not hub_url and getattr(command_executor, bstack11l1l_opy_ (u"ࠨ࡟ࡶࡴ࡯ࠦᘬ"), None) else None
        if not hub_url:
            client_config = getattr(command_executor, bstack11l1l_opy_ (u"ࠢࡠࡥ࡯࡭ࡪࡴࡴࡠࡥࡲࡲ࡫࡯ࡧࠣᘭ"), None)
            if not client_config:
                return None
            hub_url = getattr(client_config, bstack11l1l_opy_ (u"ࠣࡴࡨࡱࡴࡺࡥࡠࡵࡨࡶࡻ࡫ࡲࡠࡣࡧࡨࡷࠨᘮ"), None)
        return hub_url
    def bstack1l11l111111_opy_(self, instance, driver, hub_url: str):
        result = False
        if not hub_url:
            return result
        command_executor = getattr(driver, bstack11l1l_opy_ (u"ࠤࡦࡳࡲࡳࡡ࡯ࡦࡢࡩࡽ࡫ࡣࡶࡶࡲࡶࠧᘯ"), None)
        if command_executor:
            if isinstance(command_executor, (str, bytes)):
                setattr(driver, bstack11l1l_opy_ (u"ࠥࡧࡴࡳ࡭ࡢࡰࡧࡣࡪࡾࡥࡤࡷࡷࡳࡷࠨᘰ"), hub_url)
                result = True
            elif hasattr(command_executor, bstack11l1l_opy_ (u"ࠦࡤࡻࡲ࡭ࠤᘱ")):
                setattr(command_executor, bstack11l1l_opy_ (u"ࠧࡥࡵࡳ࡮ࠥᘲ"), hub_url)
                result = True
        if result:
            self.bstack1l111lll1ll_opy_ = hub_url
            bstack1lll11l111l_opy_.bstack1lllll1111l_opy_(instance, bstack1lll11l111l_opy_.bstack1l11ll1l1l1_opy_, hub_url)
            bstack1lll11l111l_opy_.bstack1lllll1111l_opy_(
                instance, bstack1lll11l111l_opy_.bstack1l111l1l111_opy_, bstack1lll11l111l_opy_.bstack1l1ll1ll111_opy_(hub_url)
            )
        return result
    @staticmethod
    def bstack1l111l11l11_opy_(bstack1llll1lll1l_opy_: Tuple[bstack1llll1111l1_opy_, bstack1lll1lll1l1_opy_]):
        return bstack11l1l_opy_ (u"ࠨ࠺ࠣᘳ").join((bstack1llll1111l1_opy_(bstack1llll1lll1l_opy_[0]).name, bstack1lll1lll1l1_opy_(bstack1llll1lll1l_opy_[1]).name))
    @staticmethod
    def bstack1ll111ll111_opy_(bstack1llll1lll1l_opy_: Tuple[bstack1llll1111l1_opy_, bstack1lll1lll1l1_opy_], callback: Callable):
        bstack1l111l11lll_opy_ = bstack1lll11l111l_opy_.bstack1l111l11l11_opy_(bstack1llll1lll1l_opy_)
        if not bstack1l111l11lll_opy_ in bstack1lll11l111l_opy_.bstack11lll111l1l_opy_:
            bstack1lll11l111l_opy_.bstack11lll111l1l_opy_[bstack1l111l11lll_opy_] = []
        bstack1lll11l111l_opy_.bstack11lll111l1l_opy_[bstack1l111l11lll_opy_].append(callback)
    def bstack1llll111lll_opy_(self, instance: bstack1llll1ll1ll_opy_, method_name: str, bstack1llll1l1l11_opy_: timedelta, *args, **kwargs):
        if not instance or method_name in (bstack11l1l_opy_ (u"ࠢࡴࡶࡤࡶࡹࡥࡳࡦࡵࡶ࡭ࡴࡴࠢᘴ")):
            return
        cmd = args[0] if method_name == bstack11l1l_opy_ (u"ࠣࡧࡻࡩࡨࡻࡴࡦࠤᘵ") and args and type(args) in [list, tuple] and isinstance(args[0], str) else None
        bstack11ll1lllll1_opy_ = bstack11l1l_opy_ (u"ࠤ࠽ࠦᘶ").join(map(str, filter(None, [method_name, cmd])))
        instance.bstack11lll111_opy_(bstack11l1l_opy_ (u"ࠥࡨࡷ࡯ࡶࡦࡴ࠽ࠦᘷ") + bstack11ll1lllll1_opy_, bstack1llll1l1l11_opy_)
    def bstack1lll1llll11_opy_(
        self,
        target: object,
        exec: Tuple[bstack1llll1ll1ll_opy_, str],
        bstack1llll1lll1l_opy_: Tuple[bstack1llll1111l1_opy_, bstack1lll1lll1l1_opy_],
        result: Any,
        *args,
        **kwargs,
    ) -> Callable[..., Any]:
        instance, method_name = exec
        bstack1llll1l1111_opy_, bstack1l111l11ll1_opy_ = bstack1llll1lll1l_opy_
        bstack1l111l11lll_opy_ = bstack1lll11l111l_opy_.bstack1l111l11l11_opy_(bstack1llll1lll1l_opy_)
        self.logger.debug(bstack11l1l_opy_ (u"ࠦࡴࡴ࡟ࡩࡱࡲ࡯࠿ࠦ࡭ࡦࡶ࡫ࡳࡩࡥ࡮ࡢ࡯ࡨࡁࢀࡳࡥࡵࡪࡲࡨࡤࡴࡡ࡮ࡧࢀࠤ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵ࠽ࡼࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࢁࠥࡧࡲࡨࡵࡀࡿࡦࡸࡧࡴࡿࠣ࡯ࡼࡧࡲࡨࡵࡀࠦᘸ") + str(kwargs) + bstack11l1l_opy_ (u"ࠧࠨᘹ"))
        if bstack1llll1l1111_opy_ == bstack1llll1111l1_opy_.QUIT:
            if bstack1l111l11ll1_opy_ == bstack1lll1lll1l1_opy_.PRE:
                bstack1l1llllllll_opy_ = bstack1lll1ll1l11_opy_.bstack1ll11l1l111_opy_(EVENTS.bstack111l11l1l_opy_.value)
                bstack1llll111ll1_opy_.bstack1lllll1111l_opy_(instance, EVENTS.bstack111l11l1l_opy_.value, bstack1l1llllllll_opy_)
                self.logger.debug(bstack11l1l_opy_ (u"ࠨࡩ࡯ࡵࡷࡥࡳࡩࡥ࠾ࡽࢀࠤࡲ࡫ࡴࡩࡱࡧࡣࡳࡧ࡭ࡦ࠿ࡾࢁࠥ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡵࡷࡥࡹ࡫࠽ࡼࡿࠣ࡬ࡴࡵ࡫ࡠࡵࡷࡥࡹ࡫࠽ࡼࡿࠥᘺ").format(instance, method_name, bstack1llll1l1111_opy_, bstack1l111l11ll1_opy_))
        if bstack1llll1l1111_opy_ == bstack1llll1111l1_opy_.bstack1llll1ll1l1_opy_:
            if bstack1l111l11ll1_opy_ == bstack1lll1lll1l1_opy_.POST and not bstack1lll11l111l_opy_.bstack1l11lll1l11_opy_ in instance.data:
                session_id = getattr(target, bstack11l1l_opy_ (u"ࠢࡴࡧࡶࡷ࡮ࡵ࡮ࡠ࡫ࡧࠦᘻ"), None)
                if session_id:
                    instance.data[bstack1lll11l111l_opy_.bstack1l11lll1l11_opy_] = session_id
        elif (
            bstack1llll1l1111_opy_ == bstack1llll1111l1_opy_.bstack1lll1ll1ll1_opy_
            and bstack1lll11l111l_opy_.bstack1l11l1l1111_opy_(*args) == bstack1lll11l111l_opy_.bstack1l111ll1ll1_opy_
        ):
            if bstack1l111l11ll1_opy_ == bstack1lll1lll1l1_opy_.PRE:
                hub_url = bstack1lll11l111l_opy_.bstack11l111l11_opy_(target)
                if hub_url:
                    instance.data.update(
                        {
                            bstack1lll11l111l_opy_.bstack1l11ll1l1l1_opy_: hub_url,
                            bstack1lll11l111l_opy_.bstack1l111l1l111_opy_: bstack1lll11l111l_opy_.bstack1l1ll1ll111_opy_(hub_url),
                            bstack1lll11l111l_opy_.bstack1ll1111l111_opy_: int(
                                os.environ.get(bstack11l1l_opy_ (u"ࠣࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡑࡎࡄࡘࡋࡕࡒࡎࡡࡌࡒࡉࡋࡘࠣᘼ"), str(self.platform_index))
                            ),
                        }
                    )
                bstack1l1ll1lll11_opy_ = bstack1lll11l111l_opy_.bstack1l1lll1111l_opy_(*args)
                bstack11lll1111ll_opy_ = bstack1l1ll1lll11_opy_.get(bstack11l1l_opy_ (u"ࠤࡦࡥࡵࡧࡢࡪ࡮࡬ࡸ࡮࡫ࡳࠣᘽ"), None) if bstack1l1ll1lll11_opy_ else None
                if isinstance(bstack11lll1111ll_opy_, dict):
                    instance.data[bstack1lll11l111l_opy_.bstack11lll111l11_opy_] = copy.deepcopy(bstack11lll1111ll_opy_)
                    instance.data[bstack1lll11l111l_opy_.bstack1l11ll11l1l_opy_] = bstack11lll1111ll_opy_
            elif bstack1l111l11ll1_opy_ == bstack1lll1lll1l1_opy_.POST:
                if isinstance(result, dict):
                    framework_session_id = result.get(bstack11l1l_opy_ (u"ࠥࡺࡦࡲࡵࡦࠤᘾ"), dict()).get(bstack11l1l_opy_ (u"ࠦࡸ࡫ࡳࡴ࡫ࡲࡲࡎࡪࠢᘿ"), None)
                    if framework_session_id:
                        instance.data.update(
                            {
                                bstack1lll11l111l_opy_.bstack1l11lll1l11_opy_: framework_session_id,
                                bstack1lll11l111l_opy_.bstack11ll1llll1l_opy_: datetime.now(tz=timezone.utc),
                            }
                        )
        elif (
            bstack1llll1l1111_opy_ == bstack1llll1111l1_opy_.bstack1lll1ll1ll1_opy_
            and bstack1lll11l111l_opy_.bstack1l11l1l1111_opy_(*args) == bstack1lll11l111l_opy_.bstack11lll1111l1_opy_
            and bstack1l111l11ll1_opy_ == bstack1lll1lll1l1_opy_.POST
        ):
            instance.data[bstack1lll11l111l_opy_.bstack11ll1llllll_opy_] = datetime.now(tz=timezone.utc)
        if bstack1l111l11lll_opy_ in bstack1lll11l111l_opy_.bstack11lll111l1l_opy_:
            bstack1l1111lllll_opy_ = None
            for callback in bstack1lll11l111l_opy_.bstack11lll111l1l_opy_[bstack1l111l11lll_opy_]:
                try:
                    bstack1l111l11l1l_opy_ = callback(self, target, exec, bstack1llll1lll1l_opy_, result, *args, **kwargs)
                    if bstack1l1111lllll_opy_ == None:
                        bstack1l1111lllll_opy_ = bstack1l111l11l1l_opy_
                except Exception as e:
                    self.logger.error(bstack11l1l_opy_ (u"ࠧ࡫ࡲࡳࡱࡵࠤ࡮ࡴࡶࡰ࡭࡬ࡲ࡬ࠦࡣࡢ࡮࡯ࡦࡦࡩ࡫࠻ࠢࠥᙀ") + str(e) + bstack11l1l_opy_ (u"ࠨࠢᙁ"))
                    traceback.print_exc()
            if bstack1llll1l1111_opy_ == bstack1llll1111l1_opy_.QUIT:
                if bstack1l111l11ll1_opy_ == bstack1lll1lll1l1_opy_.POST:
                    bstack1l1llllllll_opy_ = bstack1llll111ll1_opy_.bstack1llll1lllll_opy_(instance, EVENTS.bstack111l11l1l_opy_.value)
                    if bstack1l1llllllll_opy_!=None:
                        bstack1lll1ll1l11_opy_.end(EVENTS.bstack111l11l1l_opy_.value, bstack1l1llllllll_opy_+bstack11l1l_opy_ (u"ࠢ࠻ࡵࡷࡥࡷࡺࠢᙂ"), bstack1l1llllllll_opy_+bstack11l1l_opy_ (u"ࠣ࠼ࡨࡲࡩࠨᙃ"), True, None)
            if bstack1l111l11ll1_opy_ == bstack1lll1lll1l1_opy_.PRE and callable(bstack1l1111lllll_opy_):
                return bstack1l1111lllll_opy_
            elif bstack1l111l11ll1_opy_ == bstack1lll1lll1l1_opy_.POST and bstack1l1111lllll_opy_:
                return bstack1l1111lllll_opy_
    def bstack1lllll11111_opy_(
        self, method_name, previous_state: bstack1llll1111l1_opy_, *args, **kwargs
    ) -> bstack1llll1111l1_opy_:
        if method_name == bstack11l1l_opy_ (u"ࠤࡢࡣ࡮ࡴࡩࡵࡡࡢࠦᙄ") or method_name == bstack11l1l_opy_ (u"ࠥࡷࡹࡧࡲࡵࡡࡶࡩࡸࡹࡩࡰࡰࠥᙅ"):
            return bstack1llll1111l1_opy_.bstack1llll1ll1l1_opy_
        if method_name == bstack11l1l_opy_ (u"ࠦࡶࡻࡩࡵࠤᙆ"):
            return bstack1llll1111l1_opy_.QUIT
        if method_name == bstack11l1l_opy_ (u"ࠧ࡫ࡸࡦࡥࡸࡸࡪࠨᙇ"):
            if previous_state != bstack1llll1111l1_opy_.NONE:
                command_name = bstack1lll11l111l_opy_.bstack1l11l1l1111_opy_(*args)
                if command_name == bstack1lll11l111l_opy_.bstack1l111ll1ll1_opy_:
                    return bstack1llll1111l1_opy_.bstack1llll1ll1l1_opy_
            return bstack1llll1111l1_opy_.bstack1lll1ll1ll1_opy_
        return bstack1llll1111l1_opy_.NONE