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
from typing import Dict, List, Any, Callable, Tuple, Union
from browserstack_sdk import sdk_pb2 as structs
from browserstack_sdk.sdk_cli.bstack1ll1l1ll1ll_opy_ import bstack1ll1ll1l1ll_opy_
from browserstack_sdk.sdk_cli.bstack1llll11l1ll_opy_ import (
    bstack1llll1111l1_opy_,
    bstack1lll1lll1l1_opy_,
    bstack1llll1ll1ll_opy_,
)
from bstack_utils.helper import  bstack11lll11l_opy_
from browserstack_sdk.sdk_cli.bstack1lll1l11l11_opy_ import bstack1lll11l111l_opy_
from browserstack_sdk.sdk_cli.test_framework import TestFramework, bstack1lll111l111_opy_, bstack1ll1ll11lll_opy_, bstack1lll1l1l11l_opy_, bstack1lll111l1l1_opy_
from typing import Tuple, Any
import threading
from bstack_utils.bstack1lll1lll11_opy_ import bstack1ll1lll1_opy_
from browserstack_sdk.sdk_cli.bstack1ll11lllll1_opy_ import bstack1ll11ll1l1l_opy_
from bstack_utils.percy import bstack1l111lll1l_opy_
from bstack_utils.percy_sdk import PercySDK
from bstack_utils.constants import *
import re
class bstack1lll1l11l1l_opy_(bstack1ll1ll1l1ll_opy_):
    def __init__(self, bstack1l11llll11l_opy_: Dict[str, str]):
        super().__init__()
        self.bstack1l11llll11l_opy_ = bstack1l11llll11l_opy_
        self.percy = bstack1l111lll1l_opy_()
        self.bstack1lllll1ll1_opy_ = bstack1ll1lll1_opy_()
        self.bstack1l1l111111l_opy_()
        bstack1lll11l111l_opy_.bstack1ll111ll111_opy_((bstack1llll1111l1_opy_.bstack1lll1ll1ll1_opy_, bstack1lll1lll1l1_opy_.PRE), self.bstack1l11lll1lll_opy_)
        TestFramework.bstack1ll111ll111_opy_((bstack1lll111l111_opy_.TEST, bstack1lll1l1l11l_opy_.POST), self.bstack1l1llll1l11_opy_)
    def is_enabled(self) -> bool:
        return True
    def bstack1l1ll1111l1_opy_(self, instance: bstack1llll1ll1ll_opy_, driver: object):
        bstack1l1l11l11ll_opy_ = TestFramework.bstack1lll1llll1l_opy_(instance.context)
        for t in bstack1l1l11l11ll_opy_:
            bstack1l1l11l11l1_opy_ = TestFramework.bstack1llll1lllll_opy_(t, bstack1ll11ll1l1l_opy_.bstack1l1l1l1lll1_opy_, [])
            if any(instance is d[1] for d in bstack1l1l11l11l1_opy_) or instance == driver:
                return t
    def bstack1l11lll1lll_opy_(
        self,
        f: bstack1lll11l111l_opy_,
        driver: object,
        exec: Tuple[bstack1llll1ll1ll_opy_, str],
        bstack1llll1lll1l_opy_: Tuple[bstack1llll1111l1_opy_, bstack1lll1lll1l1_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        try:
            instance, method_name = exec
            if not bstack1lll11l111l_opy_.bstack1ll1111l11l_opy_(method_name):
                return
            platform_index = f.bstack1llll1lllll_opy_(instance, bstack1lll11l111l_opy_.bstack1ll1111l111_opy_, 0)
            bstack1l1l1111l11_opy_ = self.bstack1l1ll1111l1_opy_(instance, driver)
            bstack1l11llll1l1_opy_ = TestFramework.bstack1llll1lllll_opy_(bstack1l1l1111l11_opy_, TestFramework.bstack1l11lllll1l_opy_, None)
            if not bstack1l11llll1l1_opy_:
                self.logger.debug(bstack11l1l_opy_ (u"ࠦࡴࡴ࡟ࡱࡴࡨࡣࡪࡾࡥࡤࡷࡷࡩ࠿ࠦࡲࡦࡶࡸࡶࡳ࡯࡮ࡨࠢࡤࡷࠥࡹࡥࡴࡵ࡬ࡳࡳࠦࡩࡴࠢࡱࡳࡹࠦࡹࡦࡶࠣࡷࡹࡧࡲࡵࡧࡧࠦ፮"))
                return
            driver_command = f.bstack1ll111111l1_opy_(*args)
            for command in bstack1l1l1llll1_opy_:
                if command == driver_command:
                    self.bstack1ll111llll_opy_(driver, platform_index)
            bstack11l1l1ll1_opy_ = self.percy.bstack111llllll_opy_()
            if driver_command in bstack1111ll1l1_opy_[bstack11l1l1ll1_opy_]:
                self.bstack1lllll1ll1_opy_.bstack1l111lll11_opy_(bstack1l11llll1l1_opy_, driver_command)
        except Exception as e:
            self.logger.error(bstack11l1l_opy_ (u"ࠧࡵ࡮ࡠࡲࡵࡩࡤ࡫ࡸࡦࡥࡸࡸࡪࡀࠠࡦࡴࡵࡳࡷࠨ፯"), e)
    def bstack1l1llll1l11_opy_(
        self,
        f: TestFramework,
        instance: bstack1ll1ll11lll_opy_,
        bstack1llll1lll1l_opy_: Tuple[bstack1lll111l111_opy_, bstack1lll1l1l11l_opy_],
        *args,
        **kwargs,
    ):
        from bstack_utils.bstack11l1l11ll_opy_ import bstack1lll1ll1l11_opy_
        bstack1l1l11l11l1_opy_ = f.bstack1llll1lllll_opy_(instance, bstack1ll11ll1l1l_opy_.bstack1l1l1l1lll1_opy_, [])
        if not bstack1l1l11l11l1_opy_:
            self.logger.debug(bstack11l1l_opy_ (u"ࠨ࡯࡯ࡡࡤࡪࡹ࡫ࡲࡠࡶࡨࡷࡹࡀࠠ࡯ࡱࠣࡨࡷ࡯ࡶࡦࡴࡶࠤ࡫ࡵࡲࠡࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࡁࢀ࡮࡯ࡰ࡭ࡢ࡭ࡳ࡬࡯ࡾࠢࡤࡶ࡬ࡹ࠽ࡼࡣࡵ࡫ࡸࢃࠠ࡬ࡹࡤࡶ࡬ࡹ࠽ࠣ፰") + str(kwargs) + bstack11l1l_opy_ (u"ࠢࠣ፱"))
            return
        if len(bstack1l1l11l11l1_opy_) > 1:
            self.logger.debug(bstack11l1l_opy_ (u"ࠣࡱࡱࡣࡦ࡬ࡴࡦࡴࡢࡸࡪࡹࡴ࠻ࠢࡾࡰࡪࡴࠨࡥࡴ࡬ࡺࡪࡸ࡟ࡪࡰࡶࡸࡦࡴࡣࡦࡵࠬࢁࠥࡪࡲࡪࡸࡨࡶࡸࠦࡦࡰࡴࠣ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࡃࡻࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࢀࠤࡦࡸࡧࡴ࠿ࡾࡥࡷ࡭ࡳࡾࠢ࡮ࡻࡦࡸࡧࡴ࠿ࠥ፲") + str(kwargs) + bstack11l1l_opy_ (u"ࠤࠥ፳"))
        bstack1l11lll1ll1_opy_, bstack1l1l11111l1_opy_ = bstack1l1l11l11l1_opy_[0]
        driver = bstack1l11lll1ll1_opy_()
        if not driver:
            self.logger.debug(bstack11l1l_opy_ (u"ࠥࡳࡳࡥࡡࡧࡶࡨࡶࡤࡺࡥࡴࡶ࠽ࠤࡳࡵࠠࡥࡴ࡬ࡺࡪࡸࠠࡧࡱࡵࠤ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵ࠽ࡼࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࢁࠥࡧࡲࡨࡵࡀࡿࡦࡸࡧࡴࡿࠣ࡯ࡼࡧࡲࡨࡵࡀࠦ፴") + str(kwargs) + bstack11l1l_opy_ (u"ࠦࠧ፵"))
            return
        bstack1l11lllllll_opy_ = {
            TestFramework.bstack1l1llll1ll1_opy_: bstack11l1l_opy_ (u"ࠧࡺࡥࡴࡶࠣࡲࡦࡳࡥࠣ፶"),
            TestFramework.bstack1ll11l11l1l_opy_: bstack11l1l_opy_ (u"ࠨࡴࡦࡵࡷࠤࡺࡻࡩࡥࠤ፷"),
            TestFramework.bstack1l11lllll1l_opy_: bstack11l1l_opy_ (u"ࠢࡵࡧࡶࡸࠥࡸࡥࡳࡷࡱࠤࡳࡧ࡭ࡦࠤ፸")
        }
        bstack1l11lllll11_opy_ = { key: f.bstack1llll1lllll_opy_(instance, key) for key in bstack1l11lllllll_opy_ }
        bstack1l1l1111111_opy_ = [key for key, value in bstack1l11lllll11_opy_.items() if not value]
        if bstack1l1l1111111_opy_:
            for key in bstack1l1l1111111_opy_:
                self.logger.debug(bstack11l1l_opy_ (u"ࠣࡱࡱࡣࡦ࡬ࡴࡦࡴࡢࡸࡪࡹࡴ࠻ࠢࡰ࡭ࡸࡹࡩ࡯ࡩࠣࠦ፹") + str(key) + bstack11l1l_opy_ (u"ࠤࠥ፺"))
            return
        platform_index = f.bstack1llll1lllll_opy_(instance, bstack1lll11l111l_opy_.bstack1ll1111l111_opy_, 0)
        if self.bstack1l11llll11l_opy_.percy_capture_mode == bstack11l1l_opy_ (u"ࠥࡸࡪࡹࡴࡤࡣࡶࡩࠧ፻"):
            bstack11l1ll1lll_opy_ = bstack1l11lllll11_opy_.get(TestFramework.bstack1l11lllll1l_opy_) + bstack11l1l_opy_ (u"ࠦ࠲ࡺࡥࡴࡶࡦࡥࡸ࡫ࠢ፼")
            bstack1l1llllllll_opy_ = bstack1lll1ll1l11_opy_.bstack1ll11l1l111_opy_(EVENTS.bstack1l11llll111_opy_.value)
            PercySDK.screenshot(
                driver,
                bstack11l1ll1lll_opy_,
                bstack11111111l_opy_=bstack1l11lllll11_opy_[TestFramework.bstack1l1llll1ll1_opy_],
                bstack11l1l11l1l_opy_=bstack1l11lllll11_opy_[TestFramework.bstack1ll11l11l1l_opy_],
                bstack1ll11l1lll_opy_=platform_index
            )
            bstack1lll1ll1l11_opy_.end(EVENTS.bstack1l11llll111_opy_.value, bstack1l1llllllll_opy_+bstack11l1l_opy_ (u"ࠧࡀࡳࡵࡣࡵࡸࠧ፽"), bstack1l1llllllll_opy_+bstack11l1l_opy_ (u"ࠨ࠺ࡦࡰࡧࠦ፾"), True, None, None, None, None, test_name=bstack11l1ll1lll_opy_)
    def bstack1ll111llll_opy_(self, driver, platform_index):
        if self.bstack1lllll1ll1_opy_.bstack1l1l11l1l1_opy_() is True or self.bstack1lllll1ll1_opy_.capturing() is True:
            return
        self.bstack1lllll1ll1_opy_.bstack11lll1ll_opy_()
        while not self.bstack1lllll1ll1_opy_.bstack1l1l11l1l1_opy_():
            bstack1l11llll1l1_opy_ = self.bstack1lllll1ll1_opy_.bstack11l1ll11l_opy_()
            self.bstack1l111l1111_opy_(driver, bstack1l11llll1l1_opy_, platform_index)
        self.bstack1lllll1ll1_opy_.bstack1111l1111_opy_()
    def bstack1l111l1111_opy_(self, driver, bstack11l11lll11_opy_, platform_index, test=None):
        from bstack_utils.bstack11l1l11ll_opy_ import bstack1lll1ll1l11_opy_
        bstack1l1llllllll_opy_ = bstack1lll1ll1l11_opy_.bstack1ll11l1l111_opy_(EVENTS.bstack11l1l11lll_opy_.value)
        if test != None:
            bstack11111111l_opy_ = getattr(test, bstack11l1l_opy_ (u"ࠧ࡯ࡣࡰࡩࠬ፿"), None)
            bstack11l1l11l1l_opy_ = getattr(test, bstack11l1l_opy_ (u"ࠨࡷࡸ࡭ࡩ࠭ᎀ"), None)
            PercySDK.screenshot(driver, bstack11l11lll11_opy_, bstack11111111l_opy_=bstack11111111l_opy_, bstack11l1l11l1l_opy_=bstack11l1l11l1l_opy_, bstack1ll11l1lll_opy_=platform_index)
        else:
            PercySDK.screenshot(driver, bstack11l11lll11_opy_)
        bstack1lll1ll1l11_opy_.end(EVENTS.bstack11l1l11lll_opy_.value, bstack1l1llllllll_opy_+bstack11l1l_opy_ (u"ࠤ࠽ࡷࡹࡧࡲࡵࠤᎁ"), bstack1l1llllllll_opy_+bstack11l1l_opy_ (u"ࠥ࠾ࡪࡴࡤࠣᎂ"), True, None, None, None, None, test_name=bstack11l11lll11_opy_)
    def bstack1l1l111111l_opy_(self):
        os.environ[bstack11l1l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡔࡊࡘࡃ࡚ࠩᎃ")] = str(self.bstack1l11llll11l_opy_.success)
        os.environ[bstack11l1l_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡕࡋࡒࡄ࡛ࡢࡇࡆࡖࡔࡖࡔࡈࡣࡒࡕࡄࡆࠩᎄ")] = str(self.bstack1l11llll11l_opy_.percy_capture_mode)
        self.percy.bstack1l11llll1ll_opy_(self.bstack1l11llll11l_opy_.is_percy_auto_enabled)
        self.percy.bstack1l11llllll1_opy_(self.bstack1l11llll11l_opy_.percy_build_id)