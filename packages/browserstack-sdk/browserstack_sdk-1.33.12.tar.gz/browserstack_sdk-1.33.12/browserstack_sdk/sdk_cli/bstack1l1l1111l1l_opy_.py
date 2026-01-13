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
from typing import Dict, List, Any, Callable, Tuple, Union
from browserstack_sdk import sdk_pb2 as structs
from browserstack_sdk.sdk_cli.bstack1l1ll111111_opy_ import bstack1l1l1l111ll_opy_
from browserstack_sdk.sdk_cli.bstack1ll11l1l1l1_opy_ import (
    bstack1ll11lllll1_opy_,
    bstack1ll11lll1ll_opy_,
    bstack1ll1l1ll1l1_opy_,
)
from bstack_utils.helper import  bstack1lll11l1l_opy_
from browserstack_sdk.sdk_cli.bstack1ll11l1lll1_opy_ import bstack1ll11ll1lll_opy_
from browserstack_sdk.sdk_cli.test_framework import TestFramework, bstack1llll1ll111_opy_, bstack1lll1l11l11_opy_, bstack1lll1111l11_opy_, bstack1lll1ll1lll_opy_
from typing import Tuple, Any
import threading
from bstack_utils.bstack1ll111l1l1_opy_ import bstack1lll1l1ll1_opy_
from browserstack_sdk.sdk_cli.bstack1ll1111ll1l_opy_ import bstack1ll111ll1l1_opy_
from bstack_utils.percy import bstack11l1l11l1_opy_
from bstack_utils.percy_sdk import PercySDK
from bstack_utils.constants import *
import re
class bstack1l1ll11ll1l_opy_(bstack1l1l1l111ll_opy_):
    def __init__(self, bstack11lllll11ll_opy_: Dict[str, str]):
        super().__init__()
        self.bstack11lllll11ll_opy_ = bstack11lllll11ll_opy_
        self.percy = bstack11l1l11l1_opy_()
        self.bstack11111lll_opy_ = bstack1lll1l1ll1_opy_()
        self.bstack11lllll1l11_opy_()
        bstack1ll11ll1lll_opy_.bstack1ll1l11111l_opy_((bstack1ll11lllll1_opy_.bstack1ll11l1l1ll_opy_, bstack1ll11lll1ll_opy_.PRE), self.bstack11lllll111l_opy_)
        TestFramework.bstack1ll1l11111l_opy_((bstack1llll1ll111_opy_.TEST, bstack1lll1111l11_opy_.POST), self.bstack1l1llllll1l_opy_)
    def is_enabled(self) -> bool:
        return True
    def bstack1l1111l1lll_opy_(self, instance: bstack1ll1l1ll1l1_opy_, driver: object):
        bstack11lllllll11_opy_ = TestFramework.bstack1l1lll11l11_opy_(instance.context)
        for t in bstack11lllllll11_opy_:
            bstack1ll111l1111_opy_ = TestFramework.bstack1ll1llll11l_opy_(t, bstack1ll111ll1l1_opy_.bstack1ll111lllll_opy_, [])
            if any(instance is d[1] for d in bstack1ll111l1111_opy_) or instance == driver:
                return t
    def bstack11lllll111l_opy_(
        self,
        f: bstack1ll11ll1lll_opy_,
        driver: object,
        exec: Tuple[bstack1ll1l1ll1l1_opy_, str],
        bstack1lll1lll111_opy_: Tuple[bstack1ll11lllll1_opy_, bstack1ll11lll1ll_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        try:
            instance, method_name = exec
            if not bstack1ll11ll1lll_opy_.bstack1ll1l1ll1ll_opy_(method_name):
                return
            platform_index = f.bstack1ll1llll11l_opy_(instance, bstack1ll11ll1lll_opy_.bstack1lll11l1l1l_opy_, 0)
            bstack1ll1lll11l1_opy_ = self.bstack1l1111l1lll_opy_(instance, driver)
            bstack11lllll11l1_opy_ = TestFramework.bstack1ll1llll11l_opy_(bstack1ll1lll11l1_opy_, TestFramework.bstack1lll11111l1_opy_, None)
            if not bstack11lllll11l1_opy_:
                self.logger.debug(bstack11ll1_opy_ (u"ࠣࡱࡱࡣࡵࡸࡥࡠࡧࡻࡩࡨࡻࡴࡦ࠼ࠣࡶࡪࡺࡵࡳࡰ࡬ࡲ࡬ࠦࡡࡴࠢࡶࡩࡸࡹࡩࡰࡰࠣ࡭ࡸࠦ࡮ࡰࡶࠣࡽࡪࡺࠠࡴࡶࡤࡶࡹ࡫ࡤࠣᕣ"))
                return
            driver_command = f.bstack1ll11l1l111_opy_(*args)
            for command in bstack111l11ll_opy_:
                if command == driver_command:
                    self.bstack1l1ll1ll11_opy_(driver, platform_index)
            bstack1l1lll1lll_opy_ = self.percy.bstack11l11lll1_opy_()
            if driver_command in bstack1ll111lll_opy_[bstack1l1lll1lll_opy_]:
                self.bstack11111lll_opy_.bstack1111l1ll1_opy_(bstack11lllll11l1_opy_, driver_command)
        except Exception as e:
            self.logger.error(bstack11ll1_opy_ (u"ࠤࡲࡲࡤࡶࡲࡦࡡࡨࡼࡪࡩࡵࡵࡧ࠽ࠤࡪࡸࡲࡰࡴࠥᕤ"), e)
    def bstack1l1llllll1l_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll1l11l11_opy_,
        bstack1lll1lll111_opy_: Tuple[bstack1llll1ll111_opy_, bstack1lll1111l11_opy_],
        *args,
        **kwargs,
    ):
        from bstack_utils.bstack11l11l11ll_opy_ import bstack1lll111111l_opy_
        bstack1ll111l1111_opy_ = f.bstack1ll1llll11l_opy_(instance, bstack1ll111ll1l1_opy_.bstack1ll111lllll_opy_, [])
        if not bstack1ll111l1111_opy_:
            self.logger.debug(bstack11ll1_opy_ (u"ࠥࡳࡳࡥࡡࡧࡶࡨࡶࡤࡺࡥࡴࡶ࠽ࠤࡳࡵࠠࡥࡴ࡬ࡺࡪࡸࡳࠡࡨࡲࡶࠥ࡮࡯ࡰ࡭ࡢ࡭ࡳ࡬࡯࠾ࡽ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࢂࠦࡡࡳࡩࡶࡁࢀࡧࡲࡨࡵࢀࠤࡰࡽࡡࡳࡩࡶࡁࠧᕥ") + str(kwargs) + bstack11ll1_opy_ (u"ࠦࠧᕦ"))
            return
        if len(bstack1ll111l1111_opy_) > 1:
            self.logger.debug(bstack11ll1_opy_ (u"ࠧࡵ࡮ࡠࡣࡩࡸࡪࡸ࡟ࡵࡧࡶࡸ࠿ࠦࡻ࡭ࡧࡱࠬࡩࡸࡩࡷࡧࡵࡣ࡮ࡴࡳࡵࡣࡱࡧࡪࡹࠩࡾࠢࡧࡶ࡮ࡼࡥࡳࡵࠣࡪࡴࡸࠠࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࡀࡿ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵࡽࠡࡣࡵ࡫ࡸࡃࡻࡢࡴࡪࡷࢂࠦ࡫ࡸࡣࡵ࡫ࡸࡃࠢᕧ") + str(kwargs) + bstack11ll1_opy_ (u"ࠨࠢᕨ"))
        bstack1ll11111l1l_opy_, bstack1ll111lll1l_opy_ = bstack1ll111l1111_opy_[0]
        driver = bstack1ll11111l1l_opy_()
        if not driver:
            self.logger.debug(bstack11ll1_opy_ (u"ࠢࡰࡰࡢࡥ࡫ࡺࡥࡳࡡࡷࡩࡸࡺ࠺ࠡࡰࡲࠤࡩࡸࡩࡷࡧࡵࠤ࡫ࡵࡲࠡࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࡁࢀ࡮࡯ࡰ࡭ࡢ࡭ࡳ࡬࡯ࡾࠢࡤࡶ࡬ࡹ࠽ࡼࡣࡵ࡫ࡸࢃࠠ࡬ࡹࡤࡶ࡬ࡹ࠽ࠣᕩ") + str(kwargs) + bstack11ll1_opy_ (u"ࠣࠤᕪ"))
            return
        bstack11llll1llll_opy_ = {
            TestFramework.bstack1llll1l11ll_opy_: bstack11ll1_opy_ (u"ࠤࡷࡩࡸࡺࠠ࡯ࡣࡰࡩࠧᕫ"),
            TestFramework.bstack1llll111ll1_opy_: bstack11ll1_opy_ (u"ࠥࡸࡪࡹࡴࠡࡷࡸ࡭ࡩࠨᕬ"),
            TestFramework.bstack1lll11111l1_opy_: bstack11ll1_opy_ (u"ࠦࡹ࡫ࡳࡵࠢࡵࡩࡷࡻ࡮ࠡࡰࡤࡱࡪࠨᕭ")
        }
        bstack11lllll1l1l_opy_ = { key: f.bstack1ll1llll11l_opy_(instance, key) for key in bstack11llll1llll_opy_ }
        bstack11llll1ll11_opy_ = [key for key, value in bstack11lllll1l1l_opy_.items() if not value]
        if bstack11llll1ll11_opy_:
            for key in bstack11llll1ll11_opy_:
                self.logger.debug(bstack11ll1_opy_ (u"ࠧࡵ࡮ࡠࡣࡩࡸࡪࡸ࡟ࡵࡧࡶࡸ࠿ࠦ࡭ࡪࡵࡶ࡭ࡳ࡭ࠠࠣᕮ") + str(key) + bstack11ll1_opy_ (u"ࠨࠢᕯ"))
            return
        platform_index = f.bstack1ll1llll11l_opy_(instance, bstack1ll11ll1lll_opy_.bstack1lll11l1l1l_opy_, 0)
        if self.bstack11lllll11ll_opy_.percy_capture_mode == bstack11ll1_opy_ (u"ࠢࡵࡧࡶࡸࡨࡧࡳࡦࠤᕰ"):
            bstack11lll11ll_opy_ = bstack11lllll1l1l_opy_.get(TestFramework.bstack1lll11111l1_opy_) + bstack11ll1_opy_ (u"ࠣ࠯ࡷࡩࡸࡺࡣࡢࡵࡨࠦᕱ")
            bstack1lll1l1ll11_opy_ = bstack1lll111111l_opy_.bstack1lll1111lll_opy_(EVENTS.bstack11lllll1111_opy_.value)
            PercySDK.screenshot(
                driver,
                bstack11lll11ll_opy_,
                bstack1llll1l1ll_opy_=bstack11lllll1l1l_opy_[TestFramework.bstack1llll1l11ll_opy_],
                bstack11lll1l11l_opy_=bstack11lllll1l1l_opy_[TestFramework.bstack1llll111ll1_opy_],
                bstack1l1lll111_opy_=platform_index
            )
            bstack1lll111111l_opy_.end(EVENTS.bstack11lllll1111_opy_.value, bstack1lll1l1ll11_opy_+bstack11ll1_opy_ (u"ࠤ࠽ࡷࡹࡧࡲࡵࠤᕲ"), bstack1lll1l1ll11_opy_+bstack11ll1_opy_ (u"ࠥ࠾ࡪࡴࡤࠣᕳ"), True, None, None, None, None, test_name=bstack11lll11ll_opy_)
    def bstack1l1ll1ll11_opy_(self, driver, platform_index):
        if self.bstack11111lll_opy_.bstack111l11111_opy_() is True or self.bstack11111lll_opy_.capturing() is True:
            return
        self.bstack11111lll_opy_.bstack1ll1l11ll_opy_()
        while not self.bstack11111lll_opy_.bstack111l11111_opy_():
            bstack11lllll11l1_opy_ = self.bstack11111lll_opy_.bstack1ll11l1l11_opy_()
            self.bstack1l1lllll_opy_(driver, bstack11lllll11l1_opy_, platform_index)
        self.bstack11111lll_opy_.bstack1ll1ll1111_opy_()
    def bstack1l1lllll_opy_(self, driver, bstack1llll11ll1_opy_, platform_index, test=None):
        from bstack_utils.bstack11l11l11ll_opy_ import bstack1lll111111l_opy_
        bstack1lll1l1ll11_opy_ = bstack1lll111111l_opy_.bstack1lll1111lll_opy_(EVENTS.bstack1l1ll1llll_opy_.value)
        if test != None:
            bstack1llll1l1ll_opy_ = getattr(test, bstack11ll1_opy_ (u"ࠫࡳࡧ࡭ࡦࠩᕴ"), None)
            bstack11lll1l11l_opy_ = getattr(test, bstack11ll1_opy_ (u"ࠬࡻࡵࡪࡦࠪᕵ"), None)
            PercySDK.screenshot(driver, bstack1llll11ll1_opy_, bstack1llll1l1ll_opy_=bstack1llll1l1ll_opy_, bstack11lll1l11l_opy_=bstack11lll1l11l_opy_, bstack1l1lll111_opy_=platform_index)
        else:
            PercySDK.screenshot(driver, bstack1llll11ll1_opy_)
        bstack1lll111111l_opy_.end(EVENTS.bstack1l1ll1llll_opy_.value, bstack1lll1l1ll11_opy_+bstack11ll1_opy_ (u"ࠨ࠺ࡴࡶࡤࡶࡹࠨᕶ"), bstack1lll1l1ll11_opy_+bstack11ll1_opy_ (u"ࠢ࠻ࡧࡱࡨࠧᕷ"), True, None, None, None, None, test_name=bstack1llll11ll1_opy_)
    def bstack11lllll1l11_opy_(self):
        os.environ[bstack11ll1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡑࡇࡕࡇ࡞࠭ᕸ")] = str(self.bstack11lllll11ll_opy_.success)
        os.environ[bstack11ll1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡒࡈࡖࡈ࡟࡟ࡄࡃࡓࡘ࡚ࡘࡅࡠࡏࡒࡈࡊ࠭ᕹ")] = str(self.bstack11lllll11ll_opy_.percy_capture_mode)
        self.percy.bstack11llll1ll1l_opy_(self.bstack11lllll11ll_opy_.is_percy_auto_enabled)
        self.percy.bstack11llll1lll1_opy_(self.bstack11lllll11ll_opy_.percy_build_id)