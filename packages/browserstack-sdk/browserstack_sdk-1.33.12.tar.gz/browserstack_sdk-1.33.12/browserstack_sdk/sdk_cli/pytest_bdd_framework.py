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
from datetime import datetime, timezone
from uuid import uuid4
from typing import Dict, List, Any, Tuple
from browserstack_sdk.sdk_cli.bstack1lll11ll111_opy_ import bstack1lll1lllll1_opy_
from browserstack_sdk.sdk_cli.utils.bstack1l11lll1ll_opy_ import bstack1ll1lllllll_opy_
from pathlib import Path
import grpc
from browserstack_sdk import sdk_pb2 as structs
from browserstack_sdk.sdk_cli.test_framework import (
    TestFramework,
    bstack1llll1ll111_opy_,
    bstack1lll1l11l11_opy_,
    bstack1lll1111l11_opy_,
    bstack1lll1l1ll1l_opy_,
    bstack1lll1ll1lll_opy_,
)
import traceback
from bstack_utils.helper import bstack1llll111l1l_opy_
from bstack_utils.bstack11l11l11ll_opy_ import bstack1lll111111l_opy_
from bstack_utils.constants import EVENTS
from browserstack_sdk.sdk_cli.utils.bstack1lll11l11l1_opy_ import bstack1lll11l1lll_opy_
from browserstack_sdk.sdk_cli.bstack1lll1l1llll_opy_ import bstack1lll11ll11l_opy_
bstack1lll11lll1l_opy_ = bstack1llll111l1l_opy_()
bstack1ll1ll1l11l_opy_ = bstack11ll1_opy_ (u"࡚ࠦࡶ࡬ࡰࡣࡧࡩࡩࡇࡴࡵࡣࡦ࡬ࡲ࡫࡮ࡵࡵ࠰ࠦჱ")
bstack1llll1l1lll_opy_ = bstack11ll1_opy_ (u"ࠧࡎ࡯ࡰ࡭ࡏࡩࡻ࡫࡬ࠣჲ")
bstack1lll1l1l11l_opy_ = bstack11ll1_opy_ (u"ࠨࡂࡶ࡫࡯ࡨࡑ࡫ࡶࡦ࡮ࡋࡳࡴࡱࡅࡷࡧࡱࡸࠧჳ")
bstack1lll1l1l1l1_opy_ = 1.0
_1lll111l1l1_opy_ = set()
class PytestBDDFramework(TestFramework):
    bstack1lllll11l11_opy_ = bstack11ll1_opy_ (u"ࠢࡵࡧࡶࡸࡤ࡬ࡩࡹࡶࡸࡶࡪࡹࠢჴ")
    bstack1ll1llll1ll_opy_ = bstack11ll1_opy_ (u"ࠣࡶࡨࡷࡹࡥࡨࡰࡱ࡮ࡷࡤࡹࡴࡢࡴࡷࡩࡩࠨჵ")
    bstack1lll11lll11_opy_ = bstack11ll1_opy_ (u"ࠤࡷࡩࡸࡺ࡟ࡩࡱࡲ࡯ࡸࡥࡦࡪࡰ࡬ࡷ࡭࡫ࡤࠣჶ")
    bstack1lll111lll1_opy_ = bstack11ll1_opy_ (u"ࠥࡸࡪࡹࡴࡠࡪࡲࡳࡰࡥ࡬ࡢࡵࡷࡣࡸࡺࡡࡳࡶࡨࡨࠧჷ")
    bstack1llll1lllll_opy_ = bstack11ll1_opy_ (u"ࠦࡹ࡫ࡳࡵࡡ࡫ࡳࡴࡱ࡟࡭ࡣࡶࡸࡤ࡬ࡩ࡯࡫ࡶ࡬ࡪࡪࠢჸ")
    bstack1llll11ll1l_opy_: bool
    bstack1lll1l1llll_opy_: bstack1lll11ll11l_opy_  = None
    bstack1ll1ll11ll1_opy_ = [
        bstack1llll1ll111_opy_.BEFORE_ALL,
        bstack1llll1ll111_opy_.AFTER_ALL,
        bstack1llll1ll111_opy_.BEFORE_EACH,
        bstack1llll1ll111_opy_.AFTER_EACH,
    ]
    def __init__(
        self,
        bstack1lll1l11111_opy_: Dict[str, str],
        bstack1ll1ll1llll_opy_: List[str]=[bstack11ll1_opy_ (u"ࠧࡶࡹࡵࡧࡶࡸ࠲ࡨࡤࡥࠤჹ")],
        bstack1lll1l1llll_opy_: bstack1lll11ll11l_opy_ = None,
        bstack1lllll11ll1_opy_=None
    ):
        super().__init__(bstack1ll1ll1llll_opy_, bstack1lll1l11111_opy_, bstack1lll1l1llll_opy_)
        self.bstack1llll11ll1l_opy_ = any(bstack11ll1_opy_ (u"ࠨࡰࡺࡶࡨࡷࡹ࠳ࡢࡥࡦࠥჺ") in item.lower() for item in bstack1ll1ll1llll_opy_)
        self.bstack1lllll11ll1_opy_ = bstack1lllll11ll1_opy_
    def track_event(
        self,
        context: bstack1lll1l1ll1l_opy_,
        test_framework_state: bstack1llll1ll111_opy_,
        test_hook_state: bstack1lll1111l11_opy_,
        *args,
        **kwargs,
    ):
        super().track_event(self, context, test_framework_state, test_hook_state, *args, **kwargs)
        if test_framework_state == bstack1llll1ll111_opy_.TEST or test_framework_state in PytestBDDFramework.bstack1ll1ll11ll1_opy_:
            bstack1ll1lllllll_opy_(test_framework_state, test_hook_state)
        if test_framework_state == bstack1llll1ll111_opy_.NONE:
            self.logger.warning(bstack11ll1_opy_ (u"ࠢࡪࡩࡱࡳࡷ࡫ࡤࠡࡥࡤࡰࡱࡨࡡࡤ࡭ࠣࡸࡪࡹࡴࡠࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡸࡺࡡࡵࡧࡀࡿࡹ࡫ࡳࡵࡡࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࡤࡹࡴࡢࡶࡨࢁࠥࡺࡥࡴࡶࡢ࡬ࡴࡵ࡫ࡠࡵࡷࡥࡹ࡫࠽ࠣ჻") + str(test_hook_state) + bstack11ll1_opy_ (u"ࠣࠤჼ"))
            return
        if not self.bstack1llll11ll1l_opy_:
            self.logger.warning(bstack11ll1_opy_ (u"ࠤࡷࡶࡦࡩ࡫ࡠࡧࡹࡩࡳࡺ࠺ࠡࡷࡱࡷࡺࡶࡰࡰࡴࡷࡩࡩࠦࡦࡳࡣࡰࡩࡼࡵࡲ࡬࠿ࠥჽ") + str(str(self.bstack1ll1ll1llll_opy_)) + bstack11ll1_opy_ (u"ࠥࠦჾ"))
            return
        if not isinstance(args, tuple) or len(args) == 0:
            self.logger.warning(bstack11ll1_opy_ (u"ࠦࡹࡸࡡࡤ࡭ࡢࡩࡻ࡫࡮ࡵ࠼ࠣࡹࡳ࡫ࡸࡱࡧࡦࡸࡪࡪࠠࡢࡴࡪࡷࡂࢁࡡࡳࡩࡶࢁࠥࡱࡷࡢࡴࡪࡷࡂࠨჿ") + str(kwargs) + bstack11ll1_opy_ (u"ࠧࠨᄀ"))
            return
        instance = self.__1llll11ll11_opy_(context, test_framework_state, test_hook_state, *args, **kwargs)
        if not instance:
            self.logger.debug(bstack11ll1_opy_ (u"ࠨࡴࡳࡣࡦ࡯ࡤ࡫ࡶࡦࡰࡷ࠾ࠥࡻ࡮ࡩࡣࡱࡨࡱ࡫ࡤࠡࡧࡹࡩࡳࡺ࠽ࡼࡶࡨࡷࡹࡥࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡶࡸࡦࡺࡥࡾ࠰ࡾࡸࡪࡹࡴࡠࡪࡲࡳࡰࡥࡳࡵࡣࡷࡩࢂࠦࡡࡳࡩࡶࡁࠧᄁ") + str(args) + bstack11ll1_opy_ (u"ࠢࠣᄂ"))
            return
        try:
            if instance!= None and test_framework_state in PytestBDDFramework.bstack1ll1ll11ll1_opy_ and test_hook_state == bstack1lll1111l11_opy_.PRE:
                bstack1lll1l1ll11_opy_ = bstack1lll111111l_opy_.bstack1lll1111lll_opy_(EVENTS.bstack11l1llllll_opy_.value)
                name = str(EVENTS.bstack11l1llllll_opy_.name)+bstack11ll1_opy_ (u"ࠣ࠼ࠥᄃ")+str(test_framework_state.name)
                TestFramework.bstack1ll1lll1l11_opy_(instance, name, bstack1lll1l1ll11_opy_)
        except Exception as e:
            self.logger.debug(bstack11ll1_opy_ (u"ࠤࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥ࡯࡮ࠡࡪࡲࡳࡰࠦࡥࡳࡴࡲࡶࠥࡶࡲࡦ࠼ࠣࡿࢂࠨᄄ").format(e))
        try:
            if test_framework_state == bstack1llll1ll111_opy_.TEST:
                if not TestFramework.bstack1lll1ll1ll1_opy_(instance, TestFramework.bstack1llll1l1111_opy_) and test_hook_state == bstack1lll1111l11_opy_.PRE:
                    if not (len(args) >= 3):
                        return
                    test = PytestBDDFramework.__1ll1ll1ll11_opy_(args)
                    if test:
                        instance.data.update(test)
                        self.logger.debug(bstack11ll1_opy_ (u"ࠥࡰࡴࡧࡤࡦࡦࠣ࡭ࡳࡹࡴࡢࡰࡦࡩࡂࢁࡩ࡯ࡵࡷࡥࡳࡩࡥ࠯ࡴࡨࡪ࠭࠯ࡽࠡࡧࡹࡩࡳࡺ࠽ࡼࡶࡨࡷࡹࡥࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡶࡸࡦࡺࡥࡾ࠰ࠥᄅ") + str(test_hook_state) + bstack11ll1_opy_ (u"ࠦࠧᄆ"))
                if test_hook_state == bstack1lll1111l11_opy_.PRE and not TestFramework.bstack1lll1ll1ll1_opy_(instance, TestFramework.bstack1lllll1111l_opy_):
                    TestFramework.bstack1lll111ll11_opy_(instance, TestFramework.bstack1lllll1111l_opy_, datetime.now(tz=timezone.utc))
                    PytestBDDFramework.__1lllll11lll_opy_(instance, args)
                    self.logger.debug(bstack11ll1_opy_ (u"ࠧࡹࡥࡵࠢࡷࡩࡸࡺ࠭ࡴࡶࡤࡶࡹࠦࡦࡰࡴࠣ࡭ࡳࡹࡴࡢࡰࡦࡩࡂࢁࡩ࡯ࡵࡷࡥࡳࡩࡥ࠯ࡴࡨࡪ࠭࠯ࡽࠡࡧࡹࡩࡳࡺ࠽ࡼࡶࡨࡷࡹࡥࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡶࡸࡦࡺࡥࡾ࠰ࠥᄇ") + str(test_hook_state) + bstack11ll1_opy_ (u"ࠨࠢᄈ"))
                elif test_hook_state == bstack1lll1111l11_opy_.POST and not TestFramework.bstack1lll1ll1ll1_opy_(instance, TestFramework.bstack1lll1ll111l_opy_):
                    TestFramework.bstack1lll111ll11_opy_(instance, TestFramework.bstack1lll1ll111l_opy_, datetime.now(tz=timezone.utc))
                    self.logger.debug(bstack11ll1_opy_ (u"ࠢࡴࡧࡷࠤࡹ࡫ࡳࡵ࠯ࡨࡲࡩࠦࡦࡰࡴࠣ࡭ࡳࡹࡴࡢࡰࡦࡩࡂࢁࡩ࡯ࡵࡷࡥࡳࡩࡥ࠯ࡴࡨࡪ࠭࠯ࡽࠡࡧࡹࡩࡳࡺ࠽ࡼࡶࡨࡷࡹࡥࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡶࡸࡦࡺࡥࡾ࠰ࠥᄉ") + str(test_hook_state) + bstack11ll1_opy_ (u"ࠣࠤᄊ"))
            elif test_framework_state == bstack1llll1ll111_opy_.STEP:
                if test_hook_state == bstack1lll1111l11_opy_.PRE:
                    PytestBDDFramework.__1llll11lll1_opy_(instance, args)
                elif test_hook_state == bstack1lll1111l11_opy_.POST:
                    PytestBDDFramework.__1lll1l1111l_opy_(instance, args)
            elif test_framework_state == bstack1llll1ll111_opy_.LOG and test_hook_state == bstack1lll1111l11_opy_.POST:
                PytestBDDFramework.__1llll1ll1ll_opy_(instance, *args)
            elif test_framework_state == bstack1llll1ll111_opy_.LOG_REPORT and test_hook_state == bstack1lll1111l11_opy_.POST:
                self.__1llll1ll11l_opy_(instance, *args)
                self.__1ll1lll11ll_opy_(instance)
            elif test_framework_state in PytestBDDFramework.bstack1ll1ll11ll1_opy_:
                self.__1llll1l1l11_opy_(instance, test_framework_state, test_hook_state, *args)
            self.logger.debug(bstack11ll1_opy_ (u"ࠤࡷࡶࡦࡩ࡫ࡠࡧࡹࡩࡳࡺ࠺ࠡࡪࡤࡲࡩࡲࡥࡥࠢࡨࡺࡪࡴࡴ࠾ࡽࡷࡩࡸࡺ࡟ࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡢࡷࡹࡧࡴࡦࡿ࠱ࡿࡹ࡫ࡳࡵࡡ࡫ࡳࡴࡱ࡟ࡴࡶࡤࡸࡪࢃࠠࡪࡰࡶࡸࡦࡴࡣࡦ࠿ࠥᄋ") + str(instance.ref()) + bstack11ll1_opy_ (u"ࠥࠦᄌ"))
        except Exception as e:
            self.logger.error(e)
            traceback.print_exc()
        self.bstack1ll1ll11lll_opy_(instance, (test_framework_state, test_hook_state), *args, **kwargs)
        try:
            if instance!= None and test_framework_state in PytestBDDFramework.bstack1ll1ll11ll1_opy_ and test_hook_state == bstack1lll1111l11_opy_.POST:
                name = str(EVENTS.bstack11l1llllll_opy_.name)+bstack11ll1_opy_ (u"ࠦ࠿ࠨᄍ")+str(test_framework_state.name)
                bstack1lll1l1ll11_opy_ = TestFramework.bstack1ll1ll1l1ll_opy_(instance, name)
                bstack1lll111111l_opy_.end(EVENTS.bstack11l1llllll_opy_.value, bstack1lll1l1ll11_opy_+bstack11ll1_opy_ (u"ࠧࡀࡳࡵࡣࡵࡸࠧᄎ"), bstack1lll1l1ll11_opy_+bstack11ll1_opy_ (u"ࠨ࠺ࡦࡰࡧࠦᄏ"), True, None, test_framework_state.name)
        except Exception as e:
            self.logger.debug(bstack11ll1_opy_ (u"ࠢࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣ࡭ࡳࠦࡨࡰࡱ࡮ࠤࡪࡸࡲࡰࡴ࠽ࠤࢀࢃࠢᄐ").format(e))
    def bstack1lllll11111_opy_(self):
        return self.bstack1llll11ll1l_opy_
    def __1llll111111_opy_(self, *args):
        if len(args) > 2 and callable(getattr(args[2], bstack11ll1_opy_ (u"ࠣࡩࡨࡸࡤࡸࡥࡴࡷ࡯ࡸࠧᄑ"), None)):
            rep = args[2].get_result()
            if rep:
                return TestFramework.bstack1ll1lllll11_opy_(rep, [bstack11ll1_opy_ (u"ࠤࡺ࡬ࡪࡴࠢᄒ"), bstack11ll1_opy_ (u"ࠥࡳࡺࡺࡣࡰ࡯ࡨࠦᄓ"), bstack11ll1_opy_ (u"ࠦࡵࡧࡳࡴࡧࡧࠦᄔ"), bstack11ll1_opy_ (u"ࠧ࡬ࡡࡪ࡮ࡨࡨࠧᄕ"), bstack11ll1_opy_ (u"ࠨࡳ࡬࡫ࡳࡴࡪࡪࠢᄖ"), bstack11ll1_opy_ (u"ࠢ࡭ࡱࡱ࡫ࡷ࡫ࡰࡳࡶࡨࡼࡹࠨᄗ")])
        return None
    def __1llll1ll11l_opy_(self, instance: bstack1lll1l11l11_opy_, *args):
        result = self.__1llll111111_opy_(*args)
        if not result:
            return
        failure = None
        bstack1lllll1ll11_opy_ = None
        if result.get(bstack11ll1_opy_ (u"ࠣࡱࡸࡸࡨࡵ࡭ࡦࠤᄘ"), None) == bstack11ll1_opy_ (u"ࠤࡩࡥ࡮ࡲࡥࡥࠤᄙ") and len(args) > 1 and getattr(args[1], bstack11ll1_opy_ (u"ࠥࡩࡽࡩࡩ࡯ࡨࡲࠦᄚ"), None) is not None:
            failure = [{bstack11ll1_opy_ (u"ࠫࡧࡧࡣ࡬ࡶࡵࡥࡨ࡫ࠧᄛ"): [args[1].excinfo.exconly(), result.get(bstack11ll1_opy_ (u"ࠧࡲ࡯࡯ࡩࡵࡩࡵࡸࡴࡦࡺࡷࠦᄜ"), None)]}]
            bstack1lllll1ll11_opy_ = bstack11ll1_opy_ (u"ࠨࡁࡴࡵࡨࡶࡹ࡯࡯࡯ࡇࡵࡶࡴࡸࠢᄝ") if bstack11ll1_opy_ (u"ࠢࡂࡵࡶࡩࡷࡺࡩࡰࡰࠥᄞ") in getattr(args[1].excinfo, bstack11ll1_opy_ (u"ࠣࡶࡼࡴࡪࡴࡡ࡮ࡧࠥᄟ"), bstack11ll1_opy_ (u"ࠤࠥᄠ")) else bstack11ll1_opy_ (u"࡙ࠥࡳ࡮ࡡ࡯ࡦ࡯ࡩࡩࡋࡲࡳࡱࡵࠦᄡ")
        bstack1llll1l1ll1_opy_ = result.get(bstack11ll1_opy_ (u"ࠦࡴࡻࡴࡤࡱࡰࡩࠧᄢ"), TestFramework.bstack1lll1l11l1l_opy_)
        if bstack1llll1l1ll1_opy_ != TestFramework.bstack1lll1l11l1l_opy_:
            TestFramework.bstack1lll111ll11_opy_(instance, TestFramework.bstack1llll1llll1_opy_, datetime.now(tz=timezone.utc))
        TestFramework.bstack1lll11llll1_opy_(instance, {
            TestFramework.bstack1lll11ll1l1_opy_: failure,
            TestFramework.bstack1lll1111ll1_opy_: bstack1lllll1ll11_opy_,
            TestFramework.bstack1ll1ll1ll1l_opy_: bstack1llll1l1ll1_opy_,
        })
    def __1llll11ll11_opy_(
        self,
        context: bstack1lll1l1ll1l_opy_,
        test_framework_state: bstack1llll1ll111_opy_,
        test_hook_state: bstack1lll1111l11_opy_,
        *args,
        **kwargs,
    ):
        instance = None
        if test_framework_state == bstack1llll1ll111_opy_.SETUP_FIXTURE:
            instance = self.__1lll111l1ll_opy_(context, test_framework_state, test_hook_state, *args, **kwargs)
        else:
            target = None # bstack1lll1l1lll1_opy_ bstack1lllll11l1l_opy_ this to be bstack11ll1_opy_ (u"ࠧࡴ࡯ࡥࡧ࡬ࡨࠧᄣ")
            if test_framework_state == bstack1llll1ll111_opy_.INIT_TEST:
                target = args[0] if isinstance(args[0], str) else None
                if target:
                    self.__1lllll111l1_opy_(context, test_framework_state, target, *args)
            elif test_framework_state == bstack1llll1ll111_opy_.LOG:
                nodeid = getattr(getattr(args[0], bstack11ll1_opy_ (u"ࠨ࡮ࡰࡦࡨࠦᄤ"), None), bstack11ll1_opy_ (u"ࠢ࡯ࡱࡧࡩ࡮ࡪࠢᄥ"), None) if args else None
                if isinstance(nodeid, str):
                    target = nodeid
            elif getattr(args[0], bstack11ll1_opy_ (u"ࠣࡰࡲࡨࡪࠨᄦ"), None):
                target = args[0].node.nodeid
            elif getattr(args[0], bstack11ll1_opy_ (u"ࠤࡱࡳࡩ࡫ࡩࡥࠤᄧ"), None):
                target = args[0].nodeid
            instance = TestFramework.bstack1ll1lllll1l_opy_(target) if target else None
        return instance
    def __1llll1l1l11_opy_(
        self,
        instance: bstack1lll1l11l11_opy_,
        test_framework_state: bstack1llll1ll111_opy_,
        test_hook_state: bstack1lll1111l11_opy_,
        *args,
    ):
        key = test_framework_state.name
        bstack1ll1lll1ll1_opy_ = TestFramework.bstack1ll1llll11l_opy_(instance, PytestBDDFramework.bstack1ll1llll1ll_opy_, {})
        if not key in bstack1ll1lll1ll1_opy_:
            bstack1ll1lll1ll1_opy_[key] = []
        bstack1ll1lll1lll_opy_ = TestFramework.bstack1ll1llll11l_opy_(instance, PytestBDDFramework.bstack1lll11lll11_opy_, {})
        if not key in bstack1ll1lll1lll_opy_:
            bstack1ll1lll1lll_opy_[key] = []
        bstack1ll1ll1l111_opy_ = {
            PytestBDDFramework.bstack1ll1llll1ll_opy_: bstack1ll1lll1ll1_opy_,
            PytestBDDFramework.bstack1lll11lll11_opy_: bstack1ll1lll1lll_opy_,
        }
        if test_hook_state == bstack1lll1111l11_opy_.PRE:
            hook_name = args[1] if len(args) > 1 else None
            hook = {
                bstack11ll1_opy_ (u"ࠥ࡯ࡪࡿࠢᄨ"): key,
                TestFramework.bstack1llll1l1l1l_opy_: uuid4().__str__(),
                TestFramework.bstack1llll1111ll_opy_: TestFramework.bstack1ll1ll1l1l1_opy_,
                TestFramework.bstack1lll1ll1l1l_opy_: datetime.now(tz=timezone.utc),
                TestFramework.bstack1ll1llll111_opy_: [],
                TestFramework.bstack1ll1lll1l1l_opy_: hook_name,
                TestFramework.bstack1lll1llll11_opy_: bstack1lll11l1lll_opy_.bstack1ll1llll1l1_opy_()
            }
            bstack1ll1lll1ll1_opy_[key].append(hook)
            bstack1ll1ll1l111_opy_[PytestBDDFramework.bstack1lll111lll1_opy_] = key
        elif test_hook_state == bstack1lll1111l11_opy_.POST:
            bstack1lll11l11ll_opy_ = bstack1ll1lll1ll1_opy_.get(key, [])
            hook = bstack1lll11l11ll_opy_.pop() if bstack1lll11l11ll_opy_ else None
            if hook:
                result = self.__1llll111111_opy_(*args)
                if result:
                    bstack1lll1l111ll_opy_ = result.get(bstack11ll1_opy_ (u"ࠦࡴࡻࡴࡤࡱࡰࡩࠧᄩ"), TestFramework.bstack1ll1ll1l1l1_opy_)
                    if bstack1lll1l111ll_opy_ != TestFramework.bstack1ll1ll1l1l1_opy_:
                        hook[TestFramework.bstack1llll1111ll_opy_] = bstack1lll1l111ll_opy_
                hook[TestFramework.bstack1lll11l1ll1_opy_] = datetime.now(tz=timezone.utc)
                hook[TestFramework.bstack1lll1llll11_opy_] = bstack1lll11l1lll_opy_.bstack1ll1llll1l1_opy_()
                self.bstack1lll1ll11ll_opy_(hook)
                logs = hook.get(TestFramework.bstack1lll11l111l_opy_, [])
                self.bstack1lll1l11ll1_opy_(instance, logs)
                bstack1ll1lll1lll_opy_[key].append(hook)
                bstack1ll1ll1l111_opy_[PytestBDDFramework.bstack1llll1lllll_opy_] = key
        TestFramework.bstack1lll11llll1_opy_(instance, bstack1ll1ll1l111_opy_)
        self.logger.debug(bstack11ll1_opy_ (u"ࠧࡺࡲࡢࡥ࡮ࡣ࡭ࡵ࡯࡬ࡡࡨࡺࡪࡴࡴ࠻ࠢࡷࡩࡸࡺ࡟ࡩࡱࡲ࡯ࡤࡹࡴࡢࡶࡨࡁࢀࡱࡥࡺࡿ࠱ࡿࡹ࡫ࡳࡵࡡ࡫ࡳࡴࡱ࡟ࡴࡶࡤࡸࡪࢃࠠࡩࡱࡲ࡯ࡸࡥࡳࡵࡣࡵࡸࡪࡪ࠽ࡼࡪࡲࡳࡰࡹ࡟ࡴࡶࡤࡶࡹ࡫ࡤࡾࠢ࡫ࡳࡴࡱࡳࡠࡨ࡬ࡲ࡮ࡹࡨࡦࡦࡀࠦᄪ") + str(bstack1ll1lll1lll_opy_) + bstack11ll1_opy_ (u"ࠨࠢᄫ"))
    def __1lll111l1ll_opy_(
        self,
        context: bstack1lll1l1ll1l_opy_,
        test_framework_state: bstack1llll1ll111_opy_,
        test_hook_state: bstack1lll1111l11_opy_,
        *args,
        **kwargs,
    ):
        fixturedef = TestFramework.bstack1ll1lllll11_opy_(args[0], [bstack11ll1_opy_ (u"ࠢࡴࡥࡲࡴࡪࠨᄬ"), bstack11ll1_opy_ (u"ࠣࡣࡵ࡫ࡳࡧ࡭ࡦࠤᄭ"), bstack11ll1_opy_ (u"ࠤࡳࡥࡷࡧ࡭ࡴࠤᄮ"), bstack11ll1_opy_ (u"ࠥ࡭ࡩࡹࠢᄯ"), bstack11ll1_opy_ (u"ࠦࡺࡴࡩࡵࡶࡨࡷࡹࠨᄰ"), bstack11ll1_opy_ (u"ࠧࡨࡡࡴࡧ࡬ࡨࠧᄱ")]) if len(args) > 0 else {}
        request = args[1] if len(args) > 1 else None
        scenario = args[2] if len(args) == 3 else None
        scope = request.scope if hasattr(request, bstack11ll1_opy_ (u"ࠨࡳࡤࡱࡳࡩࠧᄲ")) else fixturedef.get(bstack11ll1_opy_ (u"ࠢࡴࡥࡲࡴࡪࠨᄳ"), None)
        fixturename = request.fixturename if hasattr(request, bstack11ll1_opy_ (u"ࠣࡨ࡬ࡼࡹࡻࡲࡦࡰࡤࡱࡪࠨᄴ")) else None
        node = request.node if hasattr(request, bstack11ll1_opy_ (u"ࠤࡱࡳࡩ࡫ࠢᄵ")) else None
        target = request.node.nodeid if hasattr(node, bstack11ll1_opy_ (u"ࠥࡲࡴࡪࡥࡪࡦࠥᄶ")) else None
        baseid = fixturedef.get(bstack11ll1_opy_ (u"ࠦࡧࡧࡳࡦ࡫ࡧࠦᄷ"), None) or bstack11ll1_opy_ (u"ࠧࠨᄸ")
        if (not target or len(baseid) > 0) and hasattr(request, bstack11ll1_opy_ (u"ࠨ࡟ࡱࡻࡩࡹࡳࡩࡩࡵࡧࡰࠦᄹ")):
            target = PytestBDDFramework.__1lll1llll1l_opy_(request._pyfuncitem.location) if hasattr(request._pyfuncitem, bstack11ll1_opy_ (u"ࠢ࡭ࡱࡦࡥࡹ࡯࡯࡯ࠤᄺ")) else None
            if target and not TestFramework.bstack1ll1lllll1l_opy_(target):
                self.__1lllll111l1_opy_(context, test_framework_state, target, (target, request._pyfuncitem.location))
                node = request._pyfuncitem
                self.logger.debug(bstack11ll1_opy_ (u"ࠣࡶࡵࡥࡨࡱ࡟ࡧ࡫ࡻࡸࡺࡸࡥࡠࡧࡹࡩࡳࡺ࠺ࠡࡨࡤࡰࡱࡨࡡࡤ࡭ࠣࡸࡦࡸࡧࡦࡶࡀࡿࡹࡧࡲࡨࡧࡷࢁࠥ࡬ࡩࡹࡶࡸࡶࡪࡴࡡ࡮ࡧࡀࡿ࡫࡯ࡸࡵࡷࡵࡩࡳࡧ࡭ࡦࡿࠣࡲࡴࡪࡥ࠾ࡽࡱࡳࡩ࡫ࡽࠡࡧࡹࡩࡳࡺ࠽ࡼࡶࡨࡷࡹࡥࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡶࡸࡦࡺࡥࡾ࠰ࠥᄻ") + str(test_hook_state) + bstack11ll1_opy_ (u"ࠤࠥᄼ"))
        if not fixturedef or not scope or not target:
            self.logger.warning(bstack11ll1_opy_ (u"ࠥࡸࡷࡧࡣ࡬ࡡࡩ࡭ࡽࡺࡵࡳࡧࡢࡩࡻ࡫࡮ࡵ࠼ࠣࡹࡳ࡮ࡡ࡯ࡦ࡯ࡩࡩࠦࡥࡷࡧࡱࡸࡂࢁࡴࡦࡵࡷࡣ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟ࡴࡶࡤࡸࡪࢃ࠮ࡼࡶࡨࡷࡹࡥࡨࡰࡱ࡮ࡣࡸࡺࡡࡵࡧࢀࠤ࡫࡯ࡸࡵࡷࡵࡩࡩ࡫ࡦ࠾ࡽࡩ࡭ࡽࡺࡵࡳࡧࡧࡩ࡫ࢃࠠࡴࡥࡲࡴࡪࡃࡻࡴࡥࡲࡴࡪࢃࠠࡵࡣࡵ࡫ࡪࡺ࠽ࠣᄽ") + str(target) + bstack11ll1_opy_ (u"ࠦࠧᄾ"))
            return None
        instance = TestFramework.bstack1ll1lllll1l_opy_(target)
        if not instance:
            self.logger.warning(bstack11ll1_opy_ (u"ࠧࡺࡲࡢࡥ࡮ࡣ࡫࡯ࡸࡵࡷࡵࡩࡤ࡫ࡶࡦࡰࡷ࠾ࠥࡻ࡮ࡩࡣࡱࡨࡱ࡫ࡤࠡࡧࡹࡩࡳࡺ࠽ࡼࡶࡨࡷࡹࡥࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡶࡸࡦࡺࡥࡾ࠰ࡾࡸࡪࡹࡴࡠࡪࡲࡳࡰࡥࡳࡵࡣࡷࡩࢂࠦࡦࡪࡺࡷࡹࡷ࡫࡮ࡢ࡯ࡨࡁࢀ࡬ࡩࡹࡶࡸࡶࡪࡴࡡ࡮ࡧࢀࠤࡸࡩ࡯ࡱࡧࡀࡿࡸࡩ࡯ࡱࡧࢀࠤࡧࡧࡳࡦ࡫ࡧࡁࢀࡨࡡࡴࡧ࡬ࡨࢂࠦࡴࡢࡴࡪࡩࡹࡃࠢᄿ") + str(target) + bstack11ll1_opy_ (u"ࠨࠢᅀ"))
            return None
        bstack1lll111llll_opy_ = TestFramework.bstack1ll1llll11l_opy_(instance, PytestBDDFramework.bstack1lllll11l11_opy_, {})
        if os.getenv(bstack11ll1_opy_ (u"ࠢࡔࡆࡎࡣࡈࡒࡉࡠࡈࡏࡅࡌࡥࡆࡊ࡚ࡗ࡙ࡗࡋࡓࠣᅁ"), bstack11ll1_opy_ (u"ࠣ࠳ࠥᅂ")) == bstack11ll1_opy_ (u"ࠤ࠴ࠦᅃ"):
            bstack1lllll1l111_opy_ = bstack11ll1_opy_ (u"ࠥ࠾ࠧᅄ").join((scope, fixturename))
            bstack1ll1llllll1_opy_ = datetime.now(tz=timezone.utc)
            bstack1lllll1l11l_opy_ = {
                bstack11ll1_opy_ (u"ࠦࡰ࡫ࡹࠣᅅ"): bstack1lllll1l111_opy_,
                bstack11ll1_opy_ (u"ࠧࡺࡡࡨࡵࠥᅆ"): PytestBDDFramework.__1lll111l11l_opy_(request.node, scenario),
                bstack11ll1_opy_ (u"ࠨࡦࡪࡺࡷࡹࡷ࡫ࠢᅇ"): fixturedef,
                bstack11ll1_opy_ (u"ࠢࡴࡥࡲࡴࡪࠨᅈ"): scope,
                bstack11ll1_opy_ (u"ࠣࡶࡼࡴࡪࠨᅉ"): None,
            }
            try:
                if test_hook_state == bstack1lll1111l11_opy_.POST and callable(getattr(args[-1], bstack11ll1_opy_ (u"ࠤࡪࡩࡹࡥࡲࡦࡵࡸࡰࡹࠨᅊ"), None)):
                    bstack1lllll1l11l_opy_[bstack11ll1_opy_ (u"ࠥࡸࡾࡶࡥࠣᅋ")] = TestFramework.bstack1lll1l1l111_opy_(args[-1].get_result())
            except Exception as e:
                pass
            if test_hook_state == bstack1lll1111l11_opy_.PRE:
                bstack1lllll1l11l_opy_[bstack11ll1_opy_ (u"ࠦࡺࡻࡩࡥࠤᅌ")] = uuid4().__str__()
                bstack1lllll1l11l_opy_[PytestBDDFramework.bstack1lll1ll1l1l_opy_] = bstack1ll1llllll1_opy_
            elif test_hook_state == bstack1lll1111l11_opy_.POST:
                bstack1lllll1l11l_opy_[PytestBDDFramework.bstack1lll11l1ll1_opy_] = bstack1ll1llllll1_opy_
            if bstack1lllll1l111_opy_ in bstack1lll111llll_opy_:
                bstack1lll111llll_opy_[bstack1lllll1l111_opy_].update(bstack1lllll1l11l_opy_)
                self.logger.debug(bstack11ll1_opy_ (u"ࠧࡻࡰࡥࡣࡷࡩࡩࠦࡦࡪࡺࡷࡹࡷ࡫࡮ࡢ࡯ࡨࡁࢀ࡬ࡩࡹࡶࡸࡶࡪࡴࡡ࡮ࡧࢀࠤࡸࡩ࡯ࡱࡧࡀࡿࡸࡩ࡯ࡱࡧࢀࠤ࡫࡯ࡸࡵࡷࡵࡩࡂࠨᅍ") + str(bstack1lll111llll_opy_[bstack1lllll1l111_opy_]) + bstack11ll1_opy_ (u"ࠨࠢᅎ"))
            else:
                bstack1lll111llll_opy_[bstack1lllll1l111_opy_] = bstack1lllll1l11l_opy_
                self.logger.debug(bstack11ll1_opy_ (u"ࠢࡴࡣࡹࡩࡩࠦࡦࡪࡺࡷࡹࡷ࡫࡮ࡢ࡯ࡨࡁࢀ࡬ࡩࡹࡶࡸࡶࡪࡴࡡ࡮ࡧࢀࠤࡸࡩ࡯ࡱࡧࡀࡿࡸࡩ࡯ࡱࡧࢀࠤ࡫࡯ࡸࡵࡷࡵࡩࡂࢁࡴࡦࡵࡷࡣ࡫࡯ࡸࡵࡷࡵࡩࢂࠦࡴࡳࡣࡦ࡯ࡪࡪ࡟ࡧ࡫ࡻࡸࡺࡸࡥࡴ࠿ࠥᅏ") + str(len(bstack1lll111llll_opy_)) + bstack11ll1_opy_ (u"ࠣࠤᅐ"))
        TestFramework.bstack1lll111ll11_opy_(instance, PytestBDDFramework.bstack1lllll11l11_opy_, bstack1lll111llll_opy_)
        self.logger.debug(bstack11ll1_opy_ (u"ࠤࡶࡥࡻ࡫ࡤࠡࡨ࡬ࡼࡹࡻࡲࡦࡵࡀࡿࡱ࡫࡮ࠩࡶࡵࡥࡨࡱࡥࡥࡡࡩ࡭ࡽࡺࡵࡳࡧࡶ࠭ࢂࠦࡩ࡯ࡵࡷࡥࡳࡩࡥ࠾ࠤᅑ") + str(instance.ref()) + bstack11ll1_opy_ (u"ࠥࠦᅒ"))
        return instance
    def __1lllll111l1_opy_(
        self,
        context: bstack1lll1l1ll1l_opy_,
        test_framework_state: bstack1llll1ll111_opy_,
        target: Any,
        *args,
    ):
        ctx = bstack1lll1lllll1_opy_.create_context(target)
        ob = bstack1lll1l11l11_opy_(ctx, self.bstack1ll1ll1llll_opy_, self.bstack1lll1l11111_opy_, test_framework_state)
        TestFramework.bstack1lll11llll1_opy_(ob, {
            TestFramework.bstack1lll1111111_opy_: context.test_framework_name,
            TestFramework.bstack1lll11111ll_opy_: context.test_framework_version,
            TestFramework.bstack1llll11l111_opy_: [],
            PytestBDDFramework.bstack1lllll11l11_opy_: {},
            PytestBDDFramework.bstack1lll11lll11_opy_: {},
            PytestBDDFramework.bstack1ll1llll1ll_opy_: {},
        })
        if len(args) > 1 and isinstance(args[1], tuple):
            TestFramework.bstack1lll111ll11_opy_(ob, TestFramework.bstack1lll11lllll_opy_, str(args[1][0]))
        if context.platform_index >= 0:
            TestFramework.bstack1lll111ll11_opy_(ob, TestFramework.bstack1lll11l1l1l_opy_, context.platform_index)
        TestFramework.bstack1lll1llllll_opy_[ctx.id] = ob
        self.logger.debug(bstack11ll1_opy_ (u"ࠦࡸࡧࡶࡦࡦࠣ࡭ࡳࡹࡴࡢࡰࡦࡩࠥࡩࡴࡹ࠰࡬ࡨࡂࢁࡣࡵࡺ࠱࡭ࡩࢃࠠࡵࡣࡵ࡫ࡪࡺ࠽ࡼࡶࡤࡶ࡬࡫ࡴࡾࠢࡤࡶ࡬ࡹ࠽ࡼࡣࡵ࡫ࡸࢃࠠࡪࡰࡶࡸࡦࡴࡣࡦࡵࡀࠦᅓ") + str(TestFramework.bstack1lll1llllll_opy_.keys()) + bstack11ll1_opy_ (u"ࠧࠨᅔ"))
        return ob
    @staticmethod
    def __1lllll11lll_opy_(instance, args):
        request, feature, scenario = args
        steps = []
        for step in scenario.steps:
            steps.append({
                bstack11ll1_opy_ (u"࠭ࡩࡥࠩᅕ"): id(step),
                bstack11ll1_opy_ (u"ࠧࡵࡧࡻࡸࠬᅖ"): step.name,
                bstack11ll1_opy_ (u"ࠨ࡭ࡨࡽࡼࡵࡲࡥࠩᅗ"): step.keyword,
            })
        meta = {
            bstack11ll1_opy_ (u"ࠩࡩࡩࡦࡺࡵࡳࡧࠪᅘ"): {
                bstack11ll1_opy_ (u"ࠪࡲࡦࡳࡥࠨᅙ"): feature.name,
                bstack11ll1_opy_ (u"ࠫࡵࡧࡴࡩࠩᅚ"): feature.filename,
                bstack11ll1_opy_ (u"ࠬࡪࡥࡴࡥࡵ࡭ࡵࡺࡩࡰࡰࠪᅛ"): feature.description
            },
            bstack11ll1_opy_ (u"࠭ࡳࡤࡧࡱࡥࡷ࡯࡯ࠨᅜ"): {
                bstack11ll1_opy_ (u"ࠧ࡯ࡣࡰࡩࠬᅝ"): scenario.name
            },
            bstack11ll1_opy_ (u"ࠨࡵࡷࡩࡵࡹࠧᅞ"): steps,
            bstack11ll1_opy_ (u"ࠩࡨࡼࡦࡳࡰ࡭ࡧࡶࠫᅟ"): PytestBDDFramework.__1lll1ll1111_opy_(request.node)
        }
        instance.data.update(
            {
                TestFramework.bstack1llll1l11l1_opy_: meta
            }
        )
    def bstack1lll1ll11ll_opy_(self, hook: Dict[str, Any]) -> None:
        bstack11ll1_opy_ (u"ࠥࠦࠧࠐࠠࠡࠢࠣࠤࠥࠦࠠࡑࡴࡲࡧࡪࡹࡳࡦࡵࠣࡸ࡭࡫ࠠࡉࡱࡲ࡯ࡑ࡫ࡶࡦ࡮ࠣࡥࡹࡺࡡࡤࡪࡰࡩࡳࡺࡳࠡࡵ࡬ࡱ࡮ࡲࡡࡳࠢࡷࡳࠥࡺࡨࡦࠢࡍࡥࡻࡧࠠࡪ࡯ࡳࡰࡪࡳࡥ࡯ࡶࡤࡸ࡮ࡵ࡮࠯ࠌࠣࠤࠥࠦࠠࠡࠢࠣࡘ࡭࡯ࡳࠡ࡯ࡨࡸ࡭ࡵࡤ࠻ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥ࠳ࠠࡄࡪࡨࡧࡰࡹࠠࡵࡪࡨࠤࡍࡵ࡯࡬ࡎࡨࡺࡪࡲࠠࡥ࡫ࡵࡩࡨࡺ࡯ࡳࡻࠣ࡭ࡳࡹࡩࡥࡧࠣࢂ࠴࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠴࡛ࡰ࡭ࡱࡤࡨࡪࡪࡁࡵࡶࡤࡧ࡭ࡳࡥ࡯ࡶࡶ࠲ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡ࠯ࠣࡊࡴࡸࠠࡦࡣࡦ࡬ࠥ࡬ࡩ࡭ࡧࠣ࡭ࡳࠦࡨࡰࡱ࡮ࡣࡱ࡫ࡶࡦ࡮ࡢࡪ࡮ࡲࡥࡴ࠮ࠣࡶࡪࡶ࡬ࡢࡥࡨࡷࠥࠨࡔࡦࡵࡷࡐࡪࡼࡥ࡭ࠤࠣࡻ࡮ࡺࡨࠡࠤࡋࡳࡴࡱࡌࡦࡸࡨࡰࠧࠦࡩ࡯ࠢ࡬ࡸࡸࠦࡰࡢࡶ࡫࠲ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡ࠯ࠣࡍ࡫ࠦࡡࠡࡨ࡬ࡰࡪࠦࡩ࡯ࠢࡷ࡬ࡪࠦࡤࡪࡴࡨࡧࡹࡵࡲࡺࠢࡰࡥࡹࡩࡨࡦࡵࠣࡥࠥࡳ࡯ࡥ࡫ࡩ࡭ࡪࡪࠠࡩࡱࡲ࡯࠲ࡲࡥࡷࡧ࡯ࠤ࡫࡯࡬ࡦ࠮ࠣ࡭ࡹࠦࡣࡳࡧࡤࡸࡪࡹࠠࡢࠢࡏࡳ࡬ࡋ࡮ࡵࡴࡼࠤࡴࡨࡪࡦࡥࡷࠤࡼ࡯ࡴࡩࠢࡤࡸࡹࡧࡣࡩ࡯ࡨࡲࡹࠦࡤࡦࡶࡤ࡭ࡱࡹ࠮ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤ࠲ࠦࡓࡪ࡯࡬ࡰࡦࡸ࡬ࡺ࠮ࠣ࡭ࡹࠦࡰࡳࡱࡦࡩࡸࡹࡥࡴࠢࡅࡹ࡮ࡲࡤࡍࡧࡹࡩࡱࠦࡡࡵࡶࡤࡧ࡭ࡳࡥ࡯ࡶࡶࠤࡱࡵࡣࡢࡶࡨࡨࠥ࡯࡮ࠡࡊࡲࡳࡰࡒࡥࡷࡧ࡯࠳ࡇࡻࡩ࡭ࡦࡏࡩࡻ࡫࡬ࡉࡱࡲ࡯ࡊࡼࡥ࡯ࡶࠣࡦࡾࠦࡲࡦࡲ࡯ࡥࡨ࡯࡮ࡨࠢࠥࡆࡺ࡯࡬ࡥࡎࡨࡺࡪࡲࠢࠡࡹ࡬ࡸ࡭ࠦࠢࡉࡱࡲ࡯ࡑ࡫ࡶࡦ࡮࠲ࡆࡺ࡯࡬ࡥࡎࡨࡺࡪࡲࡈࡰࡱ࡮ࡉࡻ࡫࡮ࡵࠤ࠱ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠ࠮ࠢࡗ࡬ࡪࠦࡣࡳࡧࡤࡸࡪࡪࠠࡍࡱࡪࡉࡳࡺࡲࡺࠢࡲࡦ࡯࡫ࡣࡵࡵࠣࡥࡷ࡫ࠠࡢࡦࡧࡩࡩࠦࡴࡰࠢࡷ࡬ࡪࠦࡨࡰࡱ࡮ࠫࡸࠦࠢ࡭ࡱࡪࡷࠧࠦ࡬ࡪࡵࡷ࠲ࠏࠦࠠࠡࠢࠣࠤࠥࠦࡁࡳࡩࡶ࠾ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣ࡬ࡴࡵ࡫࠻ࠢࡗ࡬ࡪࠦࡥࡷࡧࡱࡸࠥࡪࡩࡤࡶ࡬ࡳࡳࡧࡲࡺࠢࡦࡳࡳࡺࡡࡪࡰ࡬ࡲ࡬ࠦࡥࡹ࡫ࡶࡸ࡮ࡴࡧࠡ࡮ࡲ࡫ࡸࠦࡡ࡯ࡦࠣ࡬ࡴࡵ࡫ࠡ࡫ࡱࡪࡴࡸ࡭ࡢࡶ࡬ࡳࡳ࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥ࡮࡯ࡰ࡭ࡢࡰࡪࡼࡥ࡭ࡡࡩ࡭ࡱ࡫ࡳ࠻ࠢࡏ࡭ࡸࡺࠠࡰࡨࠣࡔࡦࡺࡨࠡࡱࡥ࡮ࡪࡩࡴࡴࠢࡩࡶࡴࡳࠠࡵࡪࡨࠤ࡙࡫ࡳࡵࡎࡨࡺࡪࡲࠠ࡮ࡱࡱ࡭ࡹࡵࡲࡪࡰࡪ࠲ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࡦࡺ࡯࡬ࡥࡡ࡯ࡩࡻ࡫࡬ࡠࡨ࡬ࡰࡪࡹ࠺ࠡࡎ࡬ࡷࡹࠦ࡯ࡧࠢࡓࡥࡹ࡮ࠠࡰࡤ࡭ࡩࡨࡺࡳࠡࡨࡵࡳࡲࠦࡴࡩࡧࠣࡆࡺ࡯࡬ࡥࡎࡨࡺࡪࡲࠠ࡮ࡱࡱ࡭ࡹࡵࡲࡪࡰࡪ࠲ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠢࠣࠤᅠ")
        global _1lll111l1l1_opy_
        platform_index = os.environ[bstack11ll1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡔࡑࡇࡔࡇࡑࡕࡑࡤࡏࡎࡅࡇ࡛ࠫᅡ")]
        bstack1llll1lll1l_opy_ = os.path.join(bstack1lll11lll1l_opy_, (bstack1ll1ll1l11l_opy_ + str(platform_index)), bstack1llll1l1lll_opy_)
        if not os.path.exists(bstack1llll1lll1l_opy_) or not os.path.isdir(bstack1llll1lll1l_opy_):
            return
        logs = hook.get(bstack11ll1_opy_ (u"ࠧࡲ࡯ࡨࡵࠥᅢ"), [])
        with os.scandir(bstack1llll1lll1l_opy_) as entries:
            for entry in entries:
                abs_path = os.path.abspath(entry.path)
                if abs_path in _1lll111l1l1_opy_:
                    self.logger.info(bstack11ll1_opy_ (u"ࠨࡐࡢࡶ࡫ࠤࡦࡲࡲࡦࡣࡧࡽࠥࡶࡲࡰࡥࡨࡷࡸ࡫ࡤࠡࡽࢀࠦᅣ").format(abs_path))
                    continue
                if entry.is_file():
                    try:
                        timestamp = datetime.fromtimestamp(entry.stat().st_mtime, tz=timezone.utc).isoformat()
                    except Exception:
                        timestamp = bstack11ll1_opy_ (u"ࠢࠣᅤ")
                    log_entry = bstack1lll1ll1lll_opy_(
                        kind=bstack11ll1_opy_ (u"ࠣࡖࡈࡗ࡙ࡥࡁࡕࡖࡄࡇࡍࡓࡅࡏࡖࠥᅥ"),
                        message=bstack11ll1_opy_ (u"ࠤࠥᅦ"),
                        level=bstack11ll1_opy_ (u"ࠥࠦᅧ"),
                        timestamp=timestamp,
                        fileName=entry.name,
                        bstack1llll1lll11_opy_=entry.stat().st_size,
                        bstack1lll1111l1l_opy_=bstack11ll1_opy_ (u"ࠦࡒࡇࡎࡖࡃࡏࡣ࡚ࡖࡌࡐࡃࡇࠦᅨ"),
                        bstack1ll11l_opy_=os.path.abspath(entry.path),
                        bstack1lll111l111_opy_=hook.get(TestFramework.bstack1llll1l1l1l_opy_)
                    )
                    logs.append(log_entry)
                    _1lll111l1l1_opy_.add(abs_path)
        platform_index = os.environ[bstack11ll1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡕࡒࡁࡕࡈࡒࡖࡒࡥࡉࡏࡆࡈ࡜ࠬᅩ")]
        bstack1lll1ll1l11_opy_ = os.path.join(bstack1lll11lll1l_opy_, (bstack1ll1ll1l11l_opy_ + str(platform_index)), bstack1llll1l1lll_opy_, bstack1lll1l1l11l_opy_)
        if not os.path.exists(bstack1lll1ll1l11_opy_) or not os.path.isdir(bstack1lll1ll1l11_opy_):
            self.logger.info(bstack11ll1_opy_ (u"ࠨࡎࡰࠢࡅࡹ࡮ࡲࡤࡍࡧࡹࡩࡱࡎ࡯ࡰ࡭ࡈࡺࡪࡴࡴࠡࡣࡷࡸࡦࡩࡨ࡮ࡧࡱࡸࡸࠦࡤࡪࡴࡨࡧࡹࡵࡲࡺࠢࡩࡳࡺࡴࡤࠡࡣࡷ࠾ࠥࢁࡽࠣᅪ").format(bstack1lll1ll1l11_opy_))
        else:
            self.logger.info(bstack11ll1_opy_ (u"ࠢࡑࡴࡲࡧࡪࡹࡳࡪࡰࡪࠤࡇࡻࡩ࡭ࡦࡏࡩࡻ࡫࡬ࡉࡱࡲ࡯ࡊࡼࡥ࡯ࡶࠣࡥࡹࡺࡡࡤࡪࡰࡩࡳࡺࡳࠡࡨࡵࡳࡲࠦࡤࡪࡴࡨࡧࡹࡵࡲࡺ࠼ࠣࡿࢂࠨᅫ").format(bstack1lll1ll1l11_opy_))
            with os.scandir(bstack1lll1ll1l11_opy_) as entries:
                for entry in entries:
                    abs_path = os.path.abspath(entry.path)
                    if abs_path in _1lll111l1l1_opy_:
                        self.logger.info(bstack11ll1_opy_ (u"ࠣࡒࡤࡸ࡭ࠦࡡ࡭ࡴࡨࡥࡩࡿࠠࡱࡴࡲࡧࡪࡹࡳࡦࡦࠣࡿࢂࠨᅬ").format(abs_path))
                        continue
                    if entry.is_file():
                        try:
                            timestamp = datetime.fromtimestamp(entry.stat().st_mtime, tz=timezone.utc).isoformat()
                        except Exception:
                            timestamp = bstack11ll1_opy_ (u"ࠤࠥᅭ")
                        log_entry = bstack1lll1ll1lll_opy_(
                            kind=bstack11ll1_opy_ (u"ࠥࡘࡊ࡙ࡔࡠࡃࡗࡘࡆࡉࡈࡎࡇࡑࡘࠧᅮ"),
                            message=bstack11ll1_opy_ (u"ࠦࠧᅯ"),
                            level=bstack11ll1_opy_ (u"ࠧࡈࡵࡪ࡮ࡧࡐࡪࡼࡥ࡭ࠤᅰ"),
                            timestamp=timestamp,
                            fileName=entry.name,
                            bstack1llll1lll11_opy_=entry.stat().st_size,
                            bstack1lll1111l1l_opy_=bstack11ll1_opy_ (u"ࠨࡍࡂࡐࡘࡅࡑࡥࡕࡑࡎࡒࡅࡉࠨᅱ"),
                            bstack1ll11l_opy_=os.path.abspath(entry.path),
                            bstack1lllll111ll_opy_=hook.get(TestFramework.bstack1llll1l1l1l_opy_)
                        )
                        logs.append(log_entry)
                        _1lll111l1l1_opy_.add(abs_path)
        hook[bstack11ll1_opy_ (u"ࠢ࡭ࡱࡪࡷࠧᅲ")] = logs
    def bstack1lll1l11ll1_opy_(
        self,
        bstack1ll1lll11l1_opy_: bstack1lll1l11l11_opy_,
        entries: List[bstack1lll1ll1lll_opy_],
    ):
        req = structs.LogCreatedEventRequest()
        req.bin_session_id = os.environ.get(bstack11ll1_opy_ (u"ࠣࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡄࡎࡌࡣࡇࡏࡎࡠࡕࡈࡗࡘࡏࡏࡏࡡࡌࡈࠧᅳ"))
        req.platform_index = TestFramework.bstack1ll1llll11l_opy_(bstack1ll1lll11l1_opy_, TestFramework.bstack1lll11l1l1l_opy_)
        req.execution_context.hash = str(bstack1ll1lll11l1_opy_.context.hash)
        req.execution_context.thread_id = str(bstack1ll1lll11l1_opy_.context.thread_id)
        req.execution_context.process_id = str(bstack1ll1lll11l1_opy_.context.process_id)
        for entry in entries:
            log_entry = req.logs.add()
            log_entry.test_framework_name = TestFramework.bstack1ll1llll11l_opy_(bstack1ll1lll11l1_opy_, TestFramework.bstack1lll1111111_opy_)
            log_entry.test_framework_version = TestFramework.bstack1ll1llll11l_opy_(bstack1ll1lll11l1_opy_, TestFramework.bstack1lll11111ll_opy_)
            log_entry.uuid = entry.bstack1lll111l111_opy_ if entry.bstack1lll111l111_opy_ else TestFramework.bstack1ll1llll11l_opy_(bstack1ll1lll11l1_opy_, TestFramework.bstack1llll111ll1_opy_)
            log_entry.test_framework_state = bstack1ll1lll11l1_opy_.state.name
            log_entry.message = entry.message.encode(bstack11ll1_opy_ (u"ࠤࡸࡸ࡫࠳࠸ࠣᅴ"))
            log_entry.kind = entry.kind
            log_entry.timestamp = (
                entry.timestamp.isoformat()
                if isinstance(entry.timestamp, datetime)
                else datetime.now(tz=timezone.utc).isoformat()
            )
            if isinstance(entry.level, str) and len(entry.level.strip()) > 0:
                log_entry.level = entry.level.strip()
            if entry.kind == bstack11ll1_opy_ (u"ࠥࡘࡊ࡙ࡔࡠࡃࡗࡘࡆࡉࡈࡎࡇࡑࡘࠧᅵ"):
                log_entry.file_name = entry.fileName
                log_entry.file_size = entry.bstack1llll1lll11_opy_
                log_entry.file_path = entry.bstack1ll11l_opy_
        def bstack1llll1ll1l1_opy_():
            bstack1ll11l1l1l_opy_ = datetime.now()
            try:
                self.bstack1lllll11ll1_opy_.LogCreatedEvent(req)
                bstack1ll1lll11l1_opy_.bstack1lll1lll1_opy_(bstack11ll1_opy_ (u"ࠦ࡬ࡸࡰࡤ࠼ࡶࡩࡳࡪ࡟࡭ࡱࡪࡣࡨࡸࡥࡢࡶࡨࡨࡤ࡫ࡶࡦࡰࡷࡣࡦࡺࡴࡢࡥ࡫ࡱࡪࡴࡴࠣᅶ"), datetime.now() - bstack1ll11l1l1l_opy_)
            except grpc.RpcError as e:
                self.log_error(bstack11ll1_opy_ (u"ࠧࡸࡰࡤ࠯ࡨࡶࡷࡵࡲ࠻ࠢࡶࡩࡳࡪ࡟࡭ࡱࡪࡣࡨࡸࡥࡢࡶࡨࡨࡤ࡫ࡶࡦࡰࡷࡣࡦࡺࡴࡢࡥ࡫ࡱࡪࡴࡴࠡࡽࢀࠦᅷ").format(str(e)))
                traceback.print_exc()
        self.bstack1lll1l1llll_opy_.enqueue(bstack1llll1ll1l1_opy_)
    def __1ll1lll11ll_opy_(self, instance) -> None:
        bstack11ll1_opy_ (u"ࠨࠢࠣࠌࠣࠤࠥࠦࠠࠡࠢࠣࡐࡴࡧࡤࡴࠢࡦࡹࡸࡺ࡯࡮ࠢࡷࡥ࡬ࡹࠠࡧࡱࡵࠤࡹ࡮ࡥࠡࡩ࡬ࡺࡪࡴࠠࡵࡧࡶࡸࠥ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࠡ࡫ࡱࡷࡹࡧ࡮ࡤࡧ࠱ࠎࠥࠦࠠࠡࠢࠣࠤࠥࡉࡲࡦࡣࡷࡩࡸࠦࡡࠡࡦ࡬ࡧࡹࠦࡣࡰࡰࡷࡥ࡮ࡴࡩ࡯ࡩࠣࡸࡪࡹࡴࠡ࡮ࡨࡺࡪࡲࠠࡤࡷࡶࡸࡴࡳࠠ࡮ࡧࡷࡥࡩࡧࡴࡢࠢࡵࡩࡹࡸࡩࡦࡸࡨࡨࠥ࡬ࡲࡰ࡯ࠍࠤࠥࠦࠠࠡࠢࠣࠤࡈࡻࡳࡵࡱࡰࡘࡦ࡭ࡍࡢࡰࡤ࡫ࡪࡸࠠࡢࡰࡧࠤࡺࡶࡤࡢࡶࡨࡷࠥࡺࡨࡦࠢ࡬ࡲࡸࡺࡡ࡯ࡥࡨࠤࡸࡺࡡࡵࡧࠣࡹࡸ࡯࡮ࡨࠢࡶࡩࡹࡥࡳࡵࡣࡷࡩࡤ࡫࡮ࡵࡴ࡬ࡩࡸ࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࠤࠥࠦᅸ")
        bstack1ll1ll1l111_opy_ = {bstack11ll1_opy_ (u"ࠢࡤࡷࡶࡸࡴࡳ࡟࡮ࡧࡷࡥࡩࡧࡴࡢࠤᅹ"): bstack1lll11l1lll_opy_.bstack1ll1llll1l1_opy_()}
        TestFramework.bstack1lll11llll1_opy_(instance, bstack1ll1ll1l111_opy_)
    @staticmethod
    def __1llll11lll1_opy_(instance, args):
        request, bstack1lll1ll11l1_opy_ = args
        bstack1ll1ll1lll1_opy_ = id(bstack1lll1ll11l1_opy_)
        bstack1lll111ll1l_opy_ = instance.data[TestFramework.bstack1llll1l11l1_opy_]
        step = next(filter(lambda st: st[bstack11ll1_opy_ (u"ࠨ࡫ࡧࠫᅺ")] == bstack1ll1ll1lll1_opy_, bstack1lll111ll1l_opy_[bstack11ll1_opy_ (u"ࠩࡶࡸࡪࡶࡳࠨᅻ")]), None)
        step.update({
            bstack11ll1_opy_ (u"ࠪࡷࡹࡧࡲࡵࡧࡧࡣࡦࡺࠧᅼ"): datetime.now(tz=timezone.utc)
        })
        index = next((i for i, st in enumerate(bstack1lll111ll1l_opy_[bstack11ll1_opy_ (u"ࠫࡸࡺࡥࡱࡵࠪᅽ")]) if st[bstack11ll1_opy_ (u"ࠬ࡯ࡤࠨᅾ")] == step[bstack11ll1_opy_ (u"࠭ࡩࡥࠩᅿ")]), None)
        if index is not None:
            bstack1lll111ll1l_opy_[bstack11ll1_opy_ (u"ࠧࡴࡶࡨࡴࡸ࠭ᆀ")][index] = step
        instance.data[TestFramework.bstack1llll1l11l1_opy_] = bstack1lll111ll1l_opy_
    @staticmethod
    def __1lll1l1111l_opy_(instance, args):
        bstack11ll1_opy_ (u"ࠣࠤࠥࠎࠥࠦࠠࠡࠢࠣࠤࠥࡽࡨࡦࡰࠣࡰࡪࡴࠠࡢࡴࡪࡷࠥ࡯ࡳࠡ࠴࠯ࠤ࡮ࡺࠠࡴ࡫ࡪࡲ࡮࡬ࡩࡦࡵࠣࡸ࡭࡫ࡲࡦࠢ࡬ࡷࠥࡴ࡯ࠡࡧࡻࡧࡪࡶࡴࡪࡱࡱࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࡤࡶ࡬ࡹࠠࡢࡴࡨࠤ࠲࡛ࠦࡳࡧࡴࡹࡪࡹࡴ࠭ࠢࡶࡸࡪࡶ࡝ࠋࠢࠣࠤࠥࠦࠠࠡࠢ࡬ࡪࠥࡧࡲࡨࡵࠣࡥࡷ࡫ࠠ࠴ࠢࡷ࡬ࡪࡴࠠࡵࡪࡨࠤࡱࡧࡳࡵࠢࡹࡥࡱࡻࡥࠡ࡫ࡶࠤࡪࡾࡣࡦࡲࡷ࡭ࡴࡴࠊࠡࠢࠣࠤࠥࠦࠠࠡࠤࠥࠦᆁ")
        bstack1llll1111l1_opy_ = datetime.now(tz=timezone.utc)
        request = args[0]
        bstack1lll1ll11l1_opy_ = args[1]
        bstack1ll1ll1lll1_opy_ = id(bstack1lll1ll11l1_opy_)
        bstack1lll111ll1l_opy_ = instance.data[TestFramework.bstack1llll1l11l1_opy_]
        step = None
        if bstack1ll1ll1lll1_opy_ is not None and bstack1lll111ll1l_opy_.get(bstack11ll1_opy_ (u"ࠩࡶࡸࡪࡶࡳࠨᆂ")):
            step = next(filter(lambda st: st[bstack11ll1_opy_ (u"ࠪ࡭ࡩ࠭ᆃ")] == bstack1ll1ll1lll1_opy_, bstack1lll111ll1l_opy_[bstack11ll1_opy_ (u"ࠫࡸࡺࡥࡱࡵࠪᆄ")]), None)
            step.update({
                bstack11ll1_opy_ (u"ࠬ࡬ࡩ࡯࡫ࡶ࡬ࡪࡪ࡟ࡢࡶࠪᆅ"): bstack1llll1111l1_opy_,
            })
        if len(args) > 2:
            exception = args[2]
            step.update({
                bstack11ll1_opy_ (u"࠭ࡲࡦࡵࡸࡰࡹ࠭ᆆ"): bstack11ll1_opy_ (u"ࠧࡧࡣ࡬ࡰࡪࡪࠧᆇ"),
                bstack11ll1_opy_ (u"ࠨࡨࡤ࡭ࡱࡻࡲࡦࠩᆈ"): str(exception)
            })
        else:
            if step is not None:
                step.update({
                    bstack11ll1_opy_ (u"ࠩࡵࡩࡸࡻ࡬ࡵࠩᆉ"): bstack11ll1_opy_ (u"ࠪࡴࡦࡹࡳࡦࡦࠪᆊ"),
                })
        index = next((i for i, st in enumerate(bstack1lll111ll1l_opy_[bstack11ll1_opy_ (u"ࠫࡸࡺࡥࡱࡵࠪᆋ")]) if st[bstack11ll1_opy_ (u"ࠬ࡯ࡤࠨᆌ")] == step[bstack11ll1_opy_ (u"࠭ࡩࡥࠩᆍ")]), None)
        if index is not None:
            bstack1lll111ll1l_opy_[bstack11ll1_opy_ (u"ࠧࡴࡶࡨࡴࡸ࠭ᆎ")][index] = step
        instance.data[TestFramework.bstack1llll1l11l1_opy_] = bstack1lll111ll1l_opy_
    @staticmethod
    def __1lll1ll1111_opy_(node):
        try:
            examples = []
            if hasattr(node, bstack11ll1_opy_ (u"ࠨࡥࡤࡰࡱࡹࡰࡦࡥࠪᆏ")):
                examples = list(node.callspec.params[bstack11ll1_opy_ (u"ࠩࡢࡴࡾࡺࡥࡴࡶࡢࡦࡩࡪ࡟ࡦࡺࡤࡱࡵࡲࡥࠨᆐ")].values())
            return examples
        except:
            return []
    def bstack1lll1lll11l_opy_(self, instance: bstack1lll1l11l11_opy_, bstack1lll1lll111_opy_: Tuple[bstack1llll1ll111_opy_, bstack1lll1111l11_opy_]):
        bstack1llll11llll_opy_ = (
            PytestBDDFramework.bstack1lll111lll1_opy_
            if bstack1lll1lll111_opy_[1] == bstack1lll1111l11_opy_.PRE
            else PytestBDDFramework.bstack1llll1lllll_opy_
        )
        hook = PytestBDDFramework.bstack1lll1l11lll_opy_(instance, bstack1llll11llll_opy_)
        entries = hook.get(TestFramework.bstack1ll1llll111_opy_, []) if isinstance(hook, dict) else []
        entries.extend(TestFramework.bstack1ll1llll11l_opy_(instance, TestFramework.bstack1llll11l111_opy_, []))
        return entries
    def bstack1lll11l1l11_opy_(self, instance: bstack1lll1l11l11_opy_, bstack1lll1lll111_opy_: Tuple[bstack1llll1ll111_opy_, bstack1lll1111l11_opy_]):
        bstack1llll11llll_opy_ = (
            PytestBDDFramework.bstack1lll111lll1_opy_
            if bstack1lll1lll111_opy_[1] == bstack1lll1111l11_opy_.PRE
            else PytestBDDFramework.bstack1llll1lllll_opy_
        )
        PytestBDDFramework.bstack1ll1lll111l_opy_(instance, bstack1llll11llll_opy_)
        TestFramework.bstack1ll1llll11l_opy_(instance, TestFramework.bstack1llll11l111_opy_, []).clear()
    @staticmethod
    def bstack1lll1l11lll_opy_(instance: bstack1lll1l11l11_opy_, bstack1llll11llll_opy_: str):
        bstack1ll1lll1111_opy_ = (
            PytestBDDFramework.bstack1lll11lll11_opy_
            if bstack1llll11llll_opy_ == PytestBDDFramework.bstack1llll1lllll_opy_
            else PytestBDDFramework.bstack1ll1llll1ll_opy_
        )
        bstack1lll1lll1ll_opy_ = TestFramework.bstack1ll1llll11l_opy_(instance, bstack1llll11llll_opy_, None)
        bstack1llll11l1l1_opy_ = TestFramework.bstack1ll1llll11l_opy_(instance, bstack1ll1lll1111_opy_, None) if bstack1lll1lll1ll_opy_ else None
        return (
            bstack1llll11l1l1_opy_[bstack1lll1lll1ll_opy_][-1]
            if isinstance(bstack1llll11l1l1_opy_, dict) and len(bstack1llll11l1l1_opy_.get(bstack1lll1lll1ll_opy_, [])) > 0
            else None
        )
    @staticmethod
    def bstack1ll1lll111l_opy_(instance: bstack1lll1l11l11_opy_, bstack1llll11llll_opy_: str):
        hook = PytestBDDFramework.bstack1lll1l11lll_opy_(instance, bstack1llll11llll_opy_)
        if isinstance(hook, dict):
            hook.get(TestFramework.bstack1ll1llll111_opy_, []).clear()
    @staticmethod
    def __1llll1ll1ll_opy_(instance: bstack1lll1l11l11_opy_, *args):
        if len(args) < 2 or not callable(getattr(args[1], bstack11ll1_opy_ (u"ࠥ࡫ࡪࡺ࡟ࡳࡧࡦࡳࡷࡪࡳࠣᆑ"), None)):
            return
        if os.getenv(bstack11ll1_opy_ (u"ࠦࡘࡊࡋࡠࡅࡏࡍࡤࡌࡌࡂࡉࡢࡐࡔࡍࡓࠣᆒ"), bstack11ll1_opy_ (u"ࠧ࠷ࠢᆓ")) != bstack11ll1_opy_ (u"ࠨ࠱ࠣᆔ"):
            PytestBDDFramework.logger.warning(bstack11ll1_opy_ (u"ࠢࡪࡩࡱࡳࡷ࡯࡮ࡨࠢࡦࡥࡵࡲ࡯ࡨࠤᆕ"))
            return
        bstack1llll11l1ll_opy_ = {
            bstack11ll1_opy_ (u"ࠣࡵࡨࡸࡺࡶࠢᆖ"): (PytestBDDFramework.bstack1lll111lll1_opy_, PytestBDDFramework.bstack1ll1llll1ll_opy_),
            bstack11ll1_opy_ (u"ࠤࡷࡩࡦࡸࡤࡰࡹࡱࠦᆗ"): (PytestBDDFramework.bstack1llll1lllll_opy_, PytestBDDFramework.bstack1lll11lll11_opy_),
        }
        for when in (bstack11ll1_opy_ (u"ࠥࡷࡪࡺࡵࡱࠤᆘ"), bstack11ll1_opy_ (u"ࠦࡨࡧ࡬࡭ࠤᆙ"), bstack11ll1_opy_ (u"ࠧࡺࡥࡢࡴࡧࡳࡼࡴࠢᆚ")):
            bstack1lll1lll1l1_opy_ = args[1].get_records(when)
            if not bstack1lll1lll1l1_opy_:
                continue
            records = [
                bstack1lll1ll1lll_opy_(
                    kind=TestFramework.bstack1lll1l111l1_opy_,
                    message=r.message,
                    level=r.levelname if hasattr(r, bstack11ll1_opy_ (u"ࠨ࡬ࡦࡸࡨࡰࡳࡧ࡭ࡦࠤᆛ")) and r.levelname else None,
                    timestamp=(
                        datetime.fromtimestamp(r.created, tz=timezone.utc)
                        if hasattr(r, bstack11ll1_opy_ (u"ࠢࡤࡴࡨࡥࡹ࡫ࡤࠣᆜ")) and r.created
                        else None
                    ),
                )
                for r in bstack1lll1lll1l1_opy_
                if isinstance(getattr(r, bstack11ll1_opy_ (u"ࠣ࡯ࡨࡷࡸࡧࡧࡦࠤᆝ"), None), str) and r.message.strip()
            ]
            if not records:
                continue
            bstack1llll11l11l_opy_, bstack1ll1lll1111_opy_ = bstack1llll11l1ll_opy_.get(when, (None, None))
            bstack1lll1l1l1ll_opy_ = TestFramework.bstack1ll1llll11l_opy_(instance, bstack1llll11l11l_opy_, None) if bstack1llll11l11l_opy_ else None
            bstack1llll11l1l1_opy_ = TestFramework.bstack1ll1llll11l_opy_(instance, bstack1ll1lll1111_opy_, None) if bstack1lll1l1l1ll_opy_ else None
            if isinstance(bstack1llll11l1l1_opy_, dict) and len(bstack1llll11l1l1_opy_.get(bstack1lll1l1l1ll_opy_, [])) > 0:
                hook = bstack1llll11l1l1_opy_[bstack1lll1l1l1ll_opy_][-1]
                if isinstance(hook, dict) and TestFramework.bstack1ll1llll111_opy_ in hook:
                    hook[TestFramework.bstack1ll1llll111_opy_].extend(records)
                    continue
            logs = TestFramework.bstack1ll1llll11l_opy_(instance, TestFramework.bstack1llll11l111_opy_, [])
            logs.extend(records)
    @staticmethod
    def __1ll1ll1ll11_opy_(args) -> Dict[str, Any]:
        request, feature, scenario = args
        bstack1l1l11l111_opy_ = request.node.nodeid
        test_name = PytestBDDFramework.__1llll111l11_opy_(request.node, scenario)
        bstack1lll11ll1ll_opy_ = feature.filename
        if not bstack1l1l11l111_opy_ or not test_name or not bstack1lll11ll1ll_opy_:
            return None
        code = None
        return {
            TestFramework.bstack1llll111ll1_opy_: uuid4().__str__(),
            TestFramework.bstack1llll1l1111_opy_: bstack1l1l11l111_opy_,
            TestFramework.bstack1llll1l11ll_opy_: test_name,
            TestFramework.bstack1lll11111l1_opy_: bstack1l1l11l111_opy_,
            TestFramework.bstack1llll111lll_opy_: bstack1lll11ll1ll_opy_,
            TestFramework.bstack1lll11l1111_opy_: PytestBDDFramework.__1lll111l11l_opy_(feature, scenario),
            TestFramework.bstack1llll11111l_opy_: code,
            TestFramework.bstack1ll1ll1ll1l_opy_: TestFramework.bstack1lll1l11l1l_opy_,
            TestFramework.bstack1llll1l111l_opy_: test_name
        }
    @staticmethod
    def __1llll111l11_opy_(node, scenario):
        if hasattr(node, bstack11ll1_opy_ (u"ࠩࡦࡥࡱࡲࡳࡱࡧࡦࠫᆞ")):
            parts = node.nodeid.rsplit(bstack11ll1_opy_ (u"ࠥ࡟ࠧᆟ"))
            params = parts[-1]
            return bstack11ll1_opy_ (u"ࠦࢀࢃࠠ࡜ࡽࢀࠦᆠ").format(scenario.name, params)
        return scenario.name
    @staticmethod
    def __1lll111l11l_opy_(feature, scenario) -> List[str]:
        return (list(feature.tags) if hasattr(feature, bstack11ll1_opy_ (u"ࠬࡺࡡࡨࡵࠪᆡ")) else []) + (list(scenario.tags) if hasattr(scenario, bstack11ll1_opy_ (u"࠭ࡴࡢࡩࡶࠫᆢ")) else [])
    @staticmethod
    def __1lll1llll1l_opy_(location):
        return bstack11ll1_opy_ (u"ࠢ࠻࠼ࠥᆣ").join(filter(lambda x: isinstance(x, str), location))