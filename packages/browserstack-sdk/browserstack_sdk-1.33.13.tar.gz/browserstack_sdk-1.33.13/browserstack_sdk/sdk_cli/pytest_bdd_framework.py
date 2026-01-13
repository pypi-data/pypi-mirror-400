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
from datetime import datetime, timezone
from uuid import uuid4
from typing import Dict, List, Any, Tuple
from browserstack_sdk.sdk_cli.bstack1lll1lll1ll_opy_ import bstack1llll11111l_opy_
from browserstack_sdk.sdk_cli.utils.bstack1ll1l1l1l_opy_ import bstack11llll1l11l_opy_
from pathlib import Path
import grpc
from browserstack_sdk import sdk_pb2 as structs
from browserstack_sdk.sdk_cli.test_framework import (
    TestFramework,
    bstack1lll111l111_opy_,
    bstack1ll1ll11lll_opy_,
    bstack1lll1l1l11l_opy_,
    bstack11llll11l1l_opy_,
    bstack1lll111l1l1_opy_,
)
import traceback
from bstack_utils.helper import bstack1l1l1ll11l1_opy_
from bstack_utils.bstack11l1l11ll_opy_ import bstack1lll1ll1l11_opy_
from bstack_utils.constants import EVENTS
from browserstack_sdk.sdk_cli.utils.bstack1ll1llll1l1_opy_ import bstack1ll1llll1ll_opy_
from browserstack_sdk.sdk_cli.bstack1lllll1l11l_opy_ import bstack1lllll11ll1_opy_
bstack1l1l11llll1_opy_ = bstack1l1l1ll11l1_opy_()
bstack1l1l111ll11_opy_ = bstack11l1l_opy_ (u"ࠢࡖࡲ࡯ࡳࡦࡪࡥࡥࡃࡷࡸࡦࡩࡨ࡮ࡧࡱࡸࡸ࠳ࠢᓁ")
bstack11lll1l1111_opy_ = bstack11l1l_opy_ (u"ࠣࡊࡲࡳࡰࡒࡥࡷࡧ࡯ࠦᓂ")
bstack1l1111l1lll_opy_ = bstack11l1l_opy_ (u"ࠤࡅࡹ࡮ࡲࡤࡍࡧࡹࡩࡱࡎ࡯ࡰ࡭ࡈࡺࡪࡴࡴࠣᓃ")
bstack1l1111l11ll_opy_ = 1.0
_1l1l11l1l1l_opy_ = set()
class PytestBDDFramework(TestFramework):
    bstack1l1111l1111_opy_ = bstack11l1l_opy_ (u"ࠥࡸࡪࡹࡴࡠࡨ࡬ࡼࡹࡻࡲࡦࡵࠥᓄ")
    bstack11llll11111_opy_ = bstack11l1l_opy_ (u"ࠦࡹ࡫ࡳࡵࡡ࡫ࡳࡴࡱࡳࡠࡵࡷࡥࡷࡺࡥࡥࠤᓅ")
    bstack11lll1ll1l1_opy_ = bstack11l1l_opy_ (u"ࠧࡺࡥࡴࡶࡢ࡬ࡴࡵ࡫ࡴࡡࡩ࡭ࡳ࡯ࡳࡩࡧࡧࠦᓆ")
    bstack11lll11lll1_opy_ = bstack11l1l_opy_ (u"ࠨࡴࡦࡵࡷࡣ࡭ࡵ࡯࡬ࡡ࡯ࡥࡸࡺ࡟ࡴࡶࡤࡶࡹ࡫ࡤࠣᓇ")
    bstack1l11111llll_opy_ = bstack11l1l_opy_ (u"ࠢࡵࡧࡶࡸࡤ࡮࡯ࡰ࡭ࡢࡰࡦࡹࡴࡠࡨ࡬ࡲ࡮ࡹࡨࡦࡦࠥᓈ")
    bstack11llll1l1ll_opy_: bool
    bstack1lllll1l11l_opy_: bstack1lllll11ll1_opy_  = None
    bstack11lllllllll_opy_ = [
        bstack1lll111l111_opy_.BEFORE_ALL,
        bstack1lll111l111_opy_.AFTER_ALL,
        bstack1lll111l111_opy_.BEFORE_EACH,
        bstack1lll111l111_opy_.AFTER_EACH,
    ]
    def __init__(
        self,
        bstack11lll1l1ll1_opy_: Dict[str, str],
        bstack1l1llll1lll_opy_: List[str]=[bstack11l1l_opy_ (u"ࠣࡲࡼࡸࡪࡹࡴ࠮ࡤࡧࡨࠧᓉ")],
        bstack1lllll1l11l_opy_: bstack1lllll11ll1_opy_ = None,
        bstack1ll1ll11l11_opy_=None
    ):
        super().__init__(bstack1l1llll1lll_opy_, bstack11lll1l1ll1_opy_, bstack1lllll1l11l_opy_)
        self.bstack11llll1l1ll_opy_ = any(bstack11l1l_opy_ (u"ࠤࡳࡽࡹ࡫ࡳࡵ࠯ࡥࡨࡩࠨᓊ") in item.lower() for item in bstack1l1llll1lll_opy_)
        self.bstack1ll1ll11l11_opy_ = bstack1ll1ll11l11_opy_
    def track_event(
        self,
        context: bstack11llll11l1l_opy_,
        test_framework_state: bstack1lll111l111_opy_,
        test_hook_state: bstack1lll1l1l11l_opy_,
        *args,
        **kwargs,
    ):
        super().track_event(self, context, test_framework_state, test_hook_state, *args, **kwargs)
        if test_framework_state == bstack1lll111l111_opy_.TEST or test_framework_state in PytestBDDFramework.bstack11lllllllll_opy_:
            bstack11llll1l11l_opy_(test_framework_state, test_hook_state)
        if test_framework_state == bstack1lll111l111_opy_.NONE:
            self.logger.warning(bstack11l1l_opy_ (u"ࠥ࡭࡬ࡴ࡯ࡳࡧࡧࠤࡨࡧ࡬࡭ࡤࡤࡧࡰࠦࡴࡦࡵࡷࡣ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟ࡴࡶࡤࡸࡪࡃࡻࡵࡧࡶࡸࡤ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡵࡷࡥࡹ࡫ࡽࠡࡶࡨࡷࡹࡥࡨࡰࡱ࡮ࡣࡸࡺࡡࡵࡧࡀࠦᓋ") + str(test_hook_state) + bstack11l1l_opy_ (u"ࠦࠧᓌ"))
            return
        if not self.bstack11llll1l1ll_opy_:
            self.logger.warning(bstack11l1l_opy_ (u"ࠧࡺࡲࡢࡥ࡮ࡣࡪࡼࡥ࡯ࡶ࠽ࠤࡺࡴࡳࡶࡲࡳࡳࡷࡺࡥࡥࠢࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࡂࠨᓍ") + str(str(self.bstack1l1llll1lll_opy_)) + bstack11l1l_opy_ (u"ࠨࠢᓎ"))
            return
        if not isinstance(args, tuple) or len(args) == 0:
            self.logger.warning(bstack11l1l_opy_ (u"ࠢࡵࡴࡤࡧࡰࡥࡥࡷࡧࡱࡸ࠿ࠦࡵ࡯ࡧࡻࡴࡪࡩࡴࡦࡦࠣࡥࡷ࡭ࡳ࠾ࡽࡤࡶ࡬ࡹࡽࠡ࡭ࡺࡥࡷ࡭ࡳ࠾ࠤᓏ") + str(kwargs) + bstack11l1l_opy_ (u"ࠣࠤᓐ"))
            return
        instance = self.__1l1111l111l_opy_(context, test_framework_state, test_hook_state, *args, **kwargs)
        if not instance:
            self.logger.debug(bstack11l1l_opy_ (u"ࠤࡷࡶࡦࡩ࡫ࡠࡧࡹࡩࡳࡺ࠺ࠡࡷࡱ࡬ࡦࡴࡤ࡭ࡧࡧࠤࡪࡼࡥ࡯ࡶࡀࡿࡹ࡫ࡳࡵࡡࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࡤࡹࡴࡢࡶࡨࢁ࠳ࢁࡴࡦࡵࡷࡣ࡭ࡵ࡯࡬ࡡࡶࡸࡦࡺࡥࡾࠢࡤࡶ࡬ࡹ࠽ࠣᓑ") + str(args) + bstack11l1l_opy_ (u"ࠥࠦᓒ"))
            return
        try:
            if instance!= None and test_framework_state in PytestBDDFramework.bstack11lllllllll_opy_ and test_hook_state == bstack1lll1l1l11l_opy_.PRE:
                bstack1l1llllllll_opy_ = bstack1lll1ll1l11_opy_.bstack1ll11l1l111_opy_(EVENTS.bstack1l1lllll_opy_.value)
                name = str(EVENTS.bstack1l1lllll_opy_.name)+bstack11l1l_opy_ (u"ࠦ࠿ࠨᓓ")+str(test_framework_state.name)
                TestFramework.bstack11lll1l1l11_opy_(instance, name, bstack1l1llllllll_opy_)
        except Exception as e:
            self.logger.debug(bstack11l1l_opy_ (u"ࠧࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡ࡫ࡱࠤ࡭ࡵ࡯࡬ࠢࡨࡶࡷࡵࡲࠡࡲࡵࡩ࠿ࠦࡻࡾࠤᓔ").format(e))
        try:
            if test_framework_state == bstack1lll111l111_opy_.TEST:
                if not TestFramework.bstack1lll1ll1l1l_opy_(instance, TestFramework.bstack1l11111lll1_opy_) and test_hook_state == bstack1lll1l1l11l_opy_.PRE:
                    if not (len(args) >= 3):
                        return
                    test = PytestBDDFramework.__11llllll1l1_opy_(args)
                    if test:
                        instance.data.update(test)
                        self.logger.debug(bstack11l1l_opy_ (u"ࠨ࡬ࡰࡣࡧࡩࡩࠦࡩ࡯ࡵࡷࡥࡳࡩࡥ࠾ࡽ࡬ࡲࡸࡺࡡ࡯ࡥࡨ࠲ࡷ࡫ࡦࠩࠫࢀࠤࡪࡼࡥ࡯ࡶࡀࡿࡹ࡫ࡳࡵࡡࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࡤࡹࡴࡢࡶࡨࢁ࠳ࠨᓕ") + str(test_hook_state) + bstack11l1l_opy_ (u"ࠢࠣᓖ"))
                if test_hook_state == bstack1lll1l1l11l_opy_.PRE and not TestFramework.bstack1lll1ll1l1l_opy_(instance, TestFramework.bstack1l1l1l11l11_opy_):
                    TestFramework.bstack1lllll1111l_opy_(instance, TestFramework.bstack1l1l1l11l11_opy_, datetime.now(tz=timezone.utc))
                    PytestBDDFramework.__11llllllll1_opy_(instance, args)
                    self.logger.debug(bstack11l1l_opy_ (u"ࠣࡵࡨࡸࠥࡺࡥࡴࡶ࠰ࡷࡹࡧࡲࡵࠢࡩࡳࡷࠦࡩ࡯ࡵࡷࡥࡳࡩࡥ࠾ࡽ࡬ࡲࡸࡺࡡ࡯ࡥࡨ࠲ࡷ࡫ࡦࠩࠫࢀࠤࡪࡼࡥ࡯ࡶࡀࡿࡹ࡫ࡳࡵࡡࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࡤࡹࡴࡢࡶࡨࢁ࠳ࠨᓗ") + str(test_hook_state) + bstack11l1l_opy_ (u"ࠤࠥᓘ"))
                elif test_hook_state == bstack1lll1l1l11l_opy_.POST and not TestFramework.bstack1lll1ll1l1l_opy_(instance, TestFramework.bstack1l1l11ll111_opy_):
                    TestFramework.bstack1lllll1111l_opy_(instance, TestFramework.bstack1l1l11ll111_opy_, datetime.now(tz=timezone.utc))
                    self.logger.debug(bstack11l1l_opy_ (u"ࠥࡷࡪࡺࠠࡵࡧࡶࡸ࠲࡫࡮ࡥࠢࡩࡳࡷࠦࡩ࡯ࡵࡷࡥࡳࡩࡥ࠾ࡽ࡬ࡲࡸࡺࡡ࡯ࡥࡨ࠲ࡷ࡫ࡦࠩࠫࢀࠤࡪࡼࡥ࡯ࡶࡀࡿࡹ࡫ࡳࡵࡡࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࡤࡹࡴࡢࡶࡨࢁ࠳ࠨᓙ") + str(test_hook_state) + bstack11l1l_opy_ (u"ࠦࠧᓚ"))
            elif test_framework_state == bstack1lll111l111_opy_.STEP:
                if test_hook_state == bstack1lll1l1l11l_opy_.PRE:
                    PytestBDDFramework.__11llll11lll_opy_(instance, args)
                elif test_hook_state == bstack1lll1l1l11l_opy_.POST:
                    PytestBDDFramework.__11llll11ll1_opy_(instance, args)
            elif test_framework_state == bstack1lll111l111_opy_.LOG and test_hook_state == bstack1lll1l1l11l_opy_.POST:
                PytestBDDFramework.__11lllll1111_opy_(instance, *args)
            elif test_framework_state == bstack1lll111l111_opy_.LOG_REPORT and test_hook_state == bstack1lll1l1l11l_opy_.POST:
                self.__1l1111l1l11_opy_(instance, *args)
                self.__1l11111ll1l_opy_(instance)
            elif test_framework_state in PytestBDDFramework.bstack11lllllllll_opy_:
                self.__11lll1lll11_opy_(instance, test_framework_state, test_hook_state, *args)
            self.logger.debug(bstack11l1l_opy_ (u"ࠧࡺࡲࡢࡥ࡮ࡣࡪࡼࡥ࡯ࡶ࠽ࠤ࡭ࡧ࡮ࡥ࡮ࡨࡨࠥ࡫ࡶࡦࡰࡷࡁࢀࡺࡥࡴࡶࡢࡪࡷࡧ࡭ࡦࡹࡲࡶࡰࡥࡳࡵࡣࡷࡩࢂ࠴ࡻࡵࡧࡶࡸࡤ࡮࡯ࡰ࡭ࡢࡷࡹࡧࡴࡦࡿࠣ࡭ࡳࡹࡴࡢࡰࡦࡩࡂࠨᓛ") + str(instance.ref()) + bstack11l1l_opy_ (u"ࠨࠢᓜ"))
        except Exception as e:
            self.logger.error(e)
            traceback.print_exc()
        self.bstack11llll1l1l1_opy_(instance, (test_framework_state, test_hook_state), *args, **kwargs)
        try:
            if instance!= None and test_framework_state in PytestBDDFramework.bstack11lllllllll_opy_ and test_hook_state == bstack1lll1l1l11l_opy_.POST:
                name = str(EVENTS.bstack1l1lllll_opy_.name)+bstack11l1l_opy_ (u"ࠢ࠻ࠤᓝ")+str(test_framework_state.name)
                bstack1l1llllllll_opy_ = TestFramework.bstack11lll1llll1_opy_(instance, name)
                bstack1lll1ll1l11_opy_.end(EVENTS.bstack1l1lllll_opy_.value, bstack1l1llllllll_opy_+bstack11l1l_opy_ (u"ࠣ࠼ࡶࡸࡦࡸࡴࠣᓞ"), bstack1l1llllllll_opy_+bstack11l1l_opy_ (u"ࠤ࠽ࡩࡳࡪࠢᓟ"), True, None, test_framework_state.name)
        except Exception as e:
            self.logger.debug(bstack11l1l_opy_ (u"ࠥࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡩ࡯ࠢ࡫ࡳࡴࡱࠠࡦࡴࡵࡳࡷࡀࠠࡼࡿࠥᓠ").format(e))
    def bstack1l1l1l11l1l_opy_(self):
        return self.bstack11llll1l1ll_opy_
    def __11lllll1l11_opy_(self, *args):
        if len(args) > 2 and callable(getattr(args[2], bstack11l1l_opy_ (u"ࠦ࡬࡫ࡴࡠࡴࡨࡷࡺࡲࡴࠣᓡ"), None)):
            rep = args[2].get_result()
            if rep:
                return TestFramework.bstack1l1ll11l11l_opy_(rep, [bstack11l1l_opy_ (u"ࠧࡽࡨࡦࡰࠥᓢ"), bstack11l1l_opy_ (u"ࠨ࡯ࡶࡶࡦࡳࡲ࡫ࠢᓣ"), bstack11l1l_opy_ (u"ࠢࡱࡣࡶࡷࡪࡪࠢᓤ"), bstack11l1l_opy_ (u"ࠣࡨࡤ࡭ࡱ࡫ࡤࠣᓥ"), bstack11l1l_opy_ (u"ࠤࡶ࡯࡮ࡶࡰࡦࡦࠥᓦ"), bstack11l1l_opy_ (u"ࠥࡰࡴࡴࡧࡳࡧࡳࡶࡹ࡫ࡸࡵࠤᓧ")])
        return None
    def __1l1111l1l11_opy_(self, instance: bstack1ll1ll11lll_opy_, *args):
        result = self.__11lllll1l11_opy_(*args)
        if not result:
            return
        failure = None
        bstack1lllll1ll1l_opy_ = None
        if result.get(bstack11l1l_opy_ (u"ࠦࡴࡻࡴࡤࡱࡰࡩࠧᓨ"), None) == bstack11l1l_opy_ (u"ࠧ࡬ࡡࡪ࡮ࡨࡨࠧᓩ") and len(args) > 1 and getattr(args[1], bstack11l1l_opy_ (u"ࠨࡥࡹࡥ࡬ࡲ࡫ࡵࠢᓪ"), None) is not None:
            failure = [{bstack11l1l_opy_ (u"ࠧࡣࡣࡦ࡯ࡹࡸࡡࡤࡧࠪᓫ"): [args[1].excinfo.exconly(), result.get(bstack11l1l_opy_ (u"ࠣ࡮ࡲࡲ࡬ࡸࡥࡱࡴࡷࡩࡽࡺࠢᓬ"), None)]}]
            bstack1lllll1ll1l_opy_ = bstack11l1l_opy_ (u"ࠤࡄࡷࡸ࡫ࡲࡵ࡫ࡲࡲࡊࡸࡲࡰࡴࠥᓭ") if bstack11l1l_opy_ (u"ࠥࡅࡸࡹࡥࡳࡶ࡬ࡳࡳࠨᓮ") in getattr(args[1].excinfo, bstack11l1l_opy_ (u"ࠦࡹࡿࡰࡦࡰࡤࡱࡪࠨᓯ"), bstack11l1l_opy_ (u"ࠧࠨᓰ")) else bstack11l1l_opy_ (u"ࠨࡕ࡯ࡪࡤࡲࡩࡲࡥࡥࡇࡵࡶࡴࡸࠢᓱ")
        bstack11lllll1ll1_opy_ = result.get(bstack11l1l_opy_ (u"ࠢࡰࡷࡷࡧࡴࡳࡥࠣᓲ"), TestFramework.bstack1l11111l1l1_opy_)
        if bstack11lllll1ll1_opy_ != TestFramework.bstack1l11111l1l1_opy_:
            TestFramework.bstack1lllll1111l_opy_(instance, TestFramework.bstack1l1l1l1l1ll_opy_, datetime.now(tz=timezone.utc))
        TestFramework.bstack11lllll11l1_opy_(instance, {
            TestFramework.bstack1l11l1ll1l1_opy_: failure,
            TestFramework.bstack1l1111111ll_opy_: bstack1lllll1ll1l_opy_,
            TestFramework.bstack1l11l1lllll_opy_: bstack11lllll1ll1_opy_,
        })
    def __1l1111l111l_opy_(
        self,
        context: bstack11llll11l1l_opy_,
        test_framework_state: bstack1lll111l111_opy_,
        test_hook_state: bstack1lll1l1l11l_opy_,
        *args,
        **kwargs,
    ):
        instance = None
        if test_framework_state == bstack1lll111l111_opy_.SETUP_FIXTURE:
            instance = self.__11lllll1l1l_opy_(context, test_framework_state, test_hook_state, *args, **kwargs)
        else:
            target = None # bstack1l111111l1l_opy_ bstack11llllll11l_opy_ this to be bstack11l1l_opy_ (u"ࠣࡰࡲࡨࡪ࡯ࡤࠣᓳ")
            if test_framework_state == bstack1lll111l111_opy_.INIT_TEST:
                target = args[0] if isinstance(args[0], str) else None
                if target:
                    self.__11lllll11ll_opy_(context, test_framework_state, target, *args)
            elif test_framework_state == bstack1lll111l111_opy_.LOG:
                nodeid = getattr(getattr(args[0], bstack11l1l_opy_ (u"ࠤࡱࡳࡩ࡫ࠢᓴ"), None), bstack11l1l_opy_ (u"ࠥࡲࡴࡪࡥࡪࡦࠥᓵ"), None) if args else None
                if isinstance(nodeid, str):
                    target = nodeid
            elif getattr(args[0], bstack11l1l_opy_ (u"ࠦࡳࡵࡤࡦࠤᓶ"), None):
                target = args[0].node.nodeid
            elif getattr(args[0], bstack11l1l_opy_ (u"ࠧࡴ࡯ࡥࡧ࡬ࡨࠧᓷ"), None):
                target = args[0].nodeid
            instance = TestFramework.bstack1lllll111ll_opy_(target) if target else None
        return instance
    def __11lll1lll11_opy_(
        self,
        instance: bstack1ll1ll11lll_opy_,
        test_framework_state: bstack1lll111l111_opy_,
        test_hook_state: bstack1lll1l1l11l_opy_,
        *args,
    ):
        key = test_framework_state.name
        bstack1l1111ll11l_opy_ = TestFramework.bstack1llll1lllll_opy_(instance, PytestBDDFramework.bstack11llll11111_opy_, {})
        if not key in bstack1l1111ll11l_opy_:
            bstack1l1111ll11l_opy_[key] = []
        bstack1l11111l1ll_opy_ = TestFramework.bstack1llll1lllll_opy_(instance, PytestBDDFramework.bstack11lll1ll1l1_opy_, {})
        if not key in bstack1l11111l1ll_opy_:
            bstack1l11111l1ll_opy_[key] = []
        bstack11llll1ll1l_opy_ = {
            PytestBDDFramework.bstack11llll11111_opy_: bstack1l1111ll11l_opy_,
            PytestBDDFramework.bstack11lll1ll1l1_opy_: bstack1l11111l1ll_opy_,
        }
        if test_hook_state == bstack1lll1l1l11l_opy_.PRE:
            hook_name = args[1] if len(args) > 1 else None
            hook = {
                bstack11l1l_opy_ (u"ࠨ࡫ࡦࡻࠥᓸ"): key,
                TestFramework.bstack11lll1l1l1l_opy_: uuid4().__str__(),
                TestFramework.bstack1l11111l111_opy_: TestFramework.bstack11llll1l111_opy_,
                TestFramework.bstack11lll1l1lll_opy_: datetime.now(tz=timezone.utc),
                TestFramework.bstack1l1111ll1l1_opy_: [],
                TestFramework.bstack11lll1l111l_opy_: hook_name,
                TestFramework.bstack11lllllll1l_opy_: bstack1ll1llll1ll_opy_.bstack11lll11llll_opy_()
            }
            bstack1l1111ll11l_opy_[key].append(hook)
            bstack11llll1ll1l_opy_[PytestBDDFramework.bstack11lll11lll1_opy_] = key
        elif test_hook_state == bstack1lll1l1l11l_opy_.POST:
            bstack1l1111l1ll1_opy_ = bstack1l1111ll11l_opy_.get(key, [])
            hook = bstack1l1111l1ll1_opy_.pop() if bstack1l1111l1ll1_opy_ else None
            if hook:
                result = self.__11lllll1l11_opy_(*args)
                if result:
                    bstack11lllllll11_opy_ = result.get(bstack11l1l_opy_ (u"ࠢࡰࡷࡷࡧࡴࡳࡥࠣᓹ"), TestFramework.bstack11llll1l111_opy_)
                    if bstack11lllllll11_opy_ != TestFramework.bstack11llll1l111_opy_:
                        hook[TestFramework.bstack1l11111l111_opy_] = bstack11lllllll11_opy_
                hook[TestFramework.bstack1l111111ll1_opy_] = datetime.now(tz=timezone.utc)
                hook[TestFramework.bstack11lllllll1l_opy_] = bstack1ll1llll1ll_opy_.bstack11lll11llll_opy_()
                self.bstack1l11111ll11_opy_(hook)
                logs = hook.get(TestFramework.bstack11lllll111l_opy_, [])
                self.bstack1l1l1l1l111_opy_(instance, logs)
                bstack1l11111l1ll_opy_[key].append(hook)
                bstack11llll1ll1l_opy_[PytestBDDFramework.bstack1l11111llll_opy_] = key
        TestFramework.bstack11lllll11l1_opy_(instance, bstack11llll1ll1l_opy_)
        self.logger.debug(bstack11l1l_opy_ (u"ࠣࡶࡵࡥࡨࡱ࡟ࡩࡱࡲ࡯ࡤ࡫ࡶࡦࡰࡷ࠾ࠥࡺࡥࡴࡶࡢ࡬ࡴࡵ࡫ࡠࡵࡷࡥࡹ࡫࠽ࡼ࡭ࡨࡽࢂ࠴ࡻࡵࡧࡶࡸࡤ࡮࡯ࡰ࡭ࡢࡷࡹࡧࡴࡦࡿࠣ࡬ࡴࡵ࡫ࡴࡡࡶࡸࡦࡸࡴࡦࡦࡀࡿ࡭ࡵ࡯࡬ࡵࡢࡷࡹࡧࡲࡵࡧࡧࢁࠥ࡮࡯ࡰ࡭ࡶࡣ࡫࡯࡮ࡪࡵ࡫ࡩࡩࡃࠢᓺ") + str(bstack1l11111l1ll_opy_) + bstack11l1l_opy_ (u"ࠤࠥᓻ"))
    def __11lllll1l1l_opy_(
        self,
        context: bstack11llll11l1l_opy_,
        test_framework_state: bstack1lll111l111_opy_,
        test_hook_state: bstack1lll1l1l11l_opy_,
        *args,
        **kwargs,
    ):
        fixturedef = TestFramework.bstack1l1ll11l11l_opy_(args[0], [bstack11l1l_opy_ (u"ࠥࡷࡨࡵࡰࡦࠤᓼ"), bstack11l1l_opy_ (u"ࠦࡦࡸࡧ࡯ࡣࡰࡩࠧᓽ"), bstack11l1l_opy_ (u"ࠧࡶࡡࡳࡣࡰࡷࠧᓾ"), bstack11l1l_opy_ (u"ࠨࡩࡥࡵࠥᓿ"), bstack11l1l_opy_ (u"ࠢࡶࡰ࡬ࡸࡹ࡫ࡳࡵࠤᔀ"), bstack11l1l_opy_ (u"ࠣࡤࡤࡷࡪ࡯ࡤࠣᔁ")]) if len(args) > 0 else {}
        request = args[1] if len(args) > 1 else None
        scenario = args[2] if len(args) == 3 else None
        scope = request.scope if hasattr(request, bstack11l1l_opy_ (u"ࠤࡶࡧࡴࡶࡥࠣᔂ")) else fixturedef.get(bstack11l1l_opy_ (u"ࠥࡷࡨࡵࡰࡦࠤᔃ"), None)
        fixturename = request.fixturename if hasattr(request, bstack11l1l_opy_ (u"ࠦ࡫࡯ࡸࡵࡷࡵࡩࡳࡧ࡭ࡦࠤᔄ")) else None
        node = request.node if hasattr(request, bstack11l1l_opy_ (u"ࠧࡴ࡯ࡥࡧࠥᔅ")) else None
        target = request.node.nodeid if hasattr(node, bstack11l1l_opy_ (u"ࠨ࡮ࡰࡦࡨ࡭ࡩࠨᔆ")) else None
        baseid = fixturedef.get(bstack11l1l_opy_ (u"ࠢࡣࡣࡶࡩ࡮ࡪࠢᔇ"), None) or bstack11l1l_opy_ (u"ࠣࠤᔈ")
        if (not target or len(baseid) > 0) and hasattr(request, bstack11l1l_opy_ (u"ࠤࡢࡴࡾ࡬ࡵ࡯ࡥ࡬ࡸࡪࡳࠢᔉ")):
            target = PytestBDDFramework.__11lll1lllll_opy_(request._pyfuncitem.location) if hasattr(request._pyfuncitem, bstack11l1l_opy_ (u"ࠥࡰࡴࡩࡡࡵ࡫ࡲࡲࠧᔊ")) else None
            if target and not TestFramework.bstack1lllll111ll_opy_(target):
                self.__11lllll11ll_opy_(context, test_framework_state, target, (target, request._pyfuncitem.location))
                node = request._pyfuncitem
                self.logger.debug(bstack11l1l_opy_ (u"ࠦࡹࡸࡡࡤ࡭ࡢࡪ࡮ࡾࡴࡶࡴࡨࡣࡪࡼࡥ࡯ࡶ࠽ࠤ࡫ࡧ࡬࡭ࡤࡤࡧࡰࠦࡴࡢࡴࡪࡩࡹࡃࡻࡵࡣࡵ࡫ࡪࡺࡽࠡࡨ࡬ࡼࡹࡻࡲࡦࡰࡤࡱࡪࡃࡻࡧ࡫ࡻࡸࡺࡸࡥ࡯ࡣࡰࡩࢂࠦ࡮ࡰࡦࡨࡁࢀࡴ࡯ࡥࡧࢀࠤࡪࡼࡥ࡯ࡶࡀࡿࡹ࡫ࡳࡵࡡࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࡤࡹࡴࡢࡶࡨࢁ࠳ࠨᔋ") + str(test_hook_state) + bstack11l1l_opy_ (u"ࠧࠨᔌ"))
        if not fixturedef or not scope or not target:
            self.logger.warning(bstack11l1l_opy_ (u"ࠨࡴࡳࡣࡦ࡯ࡤ࡬ࡩࡹࡶࡸࡶࡪࡥࡥࡷࡧࡱࡸ࠿ࠦࡵ࡯ࡪࡤࡲࡩࡲࡥࡥࠢࡨࡺࡪࡴࡴ࠾ࡽࡷࡩࡸࡺ࡟ࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡢࡷࡹࡧࡴࡦࡿ࠱ࡿࡹ࡫ࡳࡵࡡ࡫ࡳࡴࡱ࡟ࡴࡶࡤࡸࡪࢃࠠࡧ࡫ࡻࡸࡺࡸࡥࡥࡧࡩࡁࢀ࡬ࡩࡹࡶࡸࡶࡪࡪࡥࡧࡿࠣࡷࡨࡵࡰࡦ࠿ࡾࡷࡨࡵࡰࡦࡿࠣࡸࡦࡸࡧࡦࡶࡀࠦᔍ") + str(target) + bstack11l1l_opy_ (u"ࠢࠣᔎ"))
            return None
        instance = TestFramework.bstack1lllll111ll_opy_(target)
        if not instance:
            self.logger.warning(bstack11l1l_opy_ (u"ࠣࡶࡵࡥࡨࡱ࡟ࡧ࡫ࡻࡸࡺࡸࡥࡠࡧࡹࡩࡳࡺ࠺ࠡࡷࡱ࡬ࡦࡴࡤ࡭ࡧࡧࠤࡪࡼࡥ࡯ࡶࡀࡿࡹ࡫ࡳࡵࡡࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࡤࡹࡴࡢࡶࡨࢁ࠳ࢁࡴࡦࡵࡷࡣ࡭ࡵ࡯࡬ࡡࡶࡸࡦࡺࡥࡾࠢࡩ࡭ࡽࡺࡵࡳࡧࡱࡥࡲ࡫࠽ࡼࡨ࡬ࡼࡹࡻࡲࡦࡰࡤࡱࡪࢃࠠࡴࡥࡲࡴࡪࡃࡻࡴࡥࡲࡴࡪࢃࠠࡣࡣࡶࡩ࡮ࡪ࠽ࡼࡤࡤࡷࡪ࡯ࡤࡾࠢࡷࡥࡷ࡭ࡥࡵ࠿ࠥᔏ") + str(target) + bstack11l1l_opy_ (u"ࠤࠥᔐ"))
            return None
        bstack1l11111l11l_opy_ = TestFramework.bstack1llll1lllll_opy_(instance, PytestBDDFramework.bstack1l1111l1111_opy_, {})
        if os.getenv(bstack11l1l_opy_ (u"ࠥࡗࡉࡑ࡟ࡄࡎࡌࡣࡋࡒࡁࡈࡡࡉࡍ࡝࡚ࡕࡓࡇࡖࠦᔑ"), bstack11l1l_opy_ (u"ࠦ࠶ࠨᔒ")) == bstack11l1l_opy_ (u"ࠧ࠷ࠢᔓ"):
            bstack1l111111111_opy_ = bstack11l1l_opy_ (u"ࠨ࠺ࠣᔔ").join((scope, fixturename))
            bstack1l1111ll111_opy_ = datetime.now(tz=timezone.utc)
            bstack1l1111ll1ll_opy_ = {
                bstack11l1l_opy_ (u"ࠢ࡬ࡧࡼࠦᔕ"): bstack1l111111111_opy_,
                bstack11l1l_opy_ (u"ࠣࡶࡤ࡫ࡸࠨᔖ"): PytestBDDFramework.__11llll1ll11_opy_(request.node, scenario),
                bstack11l1l_opy_ (u"ࠤࡩ࡭ࡽࡺࡵࡳࡧࠥᔗ"): fixturedef,
                bstack11l1l_opy_ (u"ࠥࡷࡨࡵࡰࡦࠤᔘ"): scope,
                bstack11l1l_opy_ (u"ࠦࡹࡿࡰࡦࠤᔙ"): None,
            }
            try:
                if test_hook_state == bstack1lll1l1l11l_opy_.POST and callable(getattr(args[-1], bstack11l1l_opy_ (u"ࠧ࡭ࡥࡵࡡࡵࡩࡸࡻ࡬ࡵࠤᔚ"), None)):
                    bstack1l1111ll1ll_opy_[bstack11l1l_opy_ (u"ࠨࡴࡺࡲࡨࠦᔛ")] = TestFramework.bstack1l1l1ll1lll_opy_(args[-1].get_result())
            except Exception as e:
                pass
            if test_hook_state == bstack1lll1l1l11l_opy_.PRE:
                bstack1l1111ll1ll_opy_[bstack11l1l_opy_ (u"ࠢࡶࡷ࡬ࡨࠧᔜ")] = uuid4().__str__()
                bstack1l1111ll1ll_opy_[PytestBDDFramework.bstack11lll1l1lll_opy_] = bstack1l1111ll111_opy_
            elif test_hook_state == bstack1lll1l1l11l_opy_.POST:
                bstack1l1111ll1ll_opy_[PytestBDDFramework.bstack1l111111ll1_opy_] = bstack1l1111ll111_opy_
            if bstack1l111111111_opy_ in bstack1l11111l11l_opy_:
                bstack1l11111l11l_opy_[bstack1l111111111_opy_].update(bstack1l1111ll1ll_opy_)
                self.logger.debug(bstack11l1l_opy_ (u"ࠣࡷࡳࡨࡦࡺࡥࡥࠢࡩ࡭ࡽࡺࡵࡳࡧࡱࡥࡲ࡫࠽ࡼࡨ࡬ࡼࡹࡻࡲࡦࡰࡤࡱࡪࢃࠠࡴࡥࡲࡴࡪࡃࡻࡴࡥࡲࡴࡪࢃࠠࡧ࡫ࡻࡸࡺࡸࡥ࠾ࠤᔝ") + str(bstack1l11111l11l_opy_[bstack1l111111111_opy_]) + bstack11l1l_opy_ (u"ࠤࠥᔞ"))
            else:
                bstack1l11111l11l_opy_[bstack1l111111111_opy_] = bstack1l1111ll1ll_opy_
                self.logger.debug(bstack11l1l_opy_ (u"ࠥࡷࡦࡼࡥࡥࠢࡩ࡭ࡽࡺࡵࡳࡧࡱࡥࡲ࡫࠽ࡼࡨ࡬ࡼࡹࡻࡲࡦࡰࡤࡱࡪࢃࠠࡴࡥࡲࡴࡪࡃࡻࡴࡥࡲࡴࡪࢃࠠࡧ࡫ࡻࡸࡺࡸࡥ࠾ࡽࡷࡩࡸࡺ࡟ࡧ࡫ࡻࡸࡺࡸࡥࡾࠢࡷࡶࡦࡩ࡫ࡦࡦࡢࡪ࡮ࡾࡴࡶࡴࡨࡷࡂࠨᔟ") + str(len(bstack1l11111l11l_opy_)) + bstack11l1l_opy_ (u"ࠦࠧᔠ"))
        TestFramework.bstack1lllll1111l_opy_(instance, PytestBDDFramework.bstack1l1111l1111_opy_, bstack1l11111l11l_opy_)
        self.logger.debug(bstack11l1l_opy_ (u"ࠧࡹࡡࡷࡧࡧࠤ࡫࡯ࡸࡵࡷࡵࡩࡸࡃࡻ࡭ࡧࡱࠬࡹࡸࡡࡤ࡭ࡨࡨࡤ࡬ࡩࡹࡶࡸࡶࡪࡹࠩࡾࠢ࡬ࡲࡸࡺࡡ࡯ࡥࡨࡁࠧᔡ") + str(instance.ref()) + bstack11l1l_opy_ (u"ࠨࠢᔢ"))
        return instance
    def __11lllll11ll_opy_(
        self,
        context: bstack11llll11l1l_opy_,
        test_framework_state: bstack1lll111l111_opy_,
        target: Any,
        *args,
    ):
        ctx = bstack1llll11111l_opy_.create_context(target)
        ob = bstack1ll1ll11lll_opy_(ctx, self.bstack1l1llll1lll_opy_, self.bstack11lll1l1ll1_opy_, test_framework_state)
        TestFramework.bstack11lllll11l1_opy_(ob, {
            TestFramework.bstack1l1llll11l1_opy_: context.test_framework_name,
            TestFramework.bstack1l1l1lll1ll_opy_: context.test_framework_version,
            TestFramework.bstack1l1111111l1_opy_: [],
            PytestBDDFramework.bstack1l1111l1111_opy_: {},
            PytestBDDFramework.bstack11lll1ll1l1_opy_: {},
            PytestBDDFramework.bstack11llll11111_opy_: {},
        })
        if len(args) > 1 and isinstance(args[1], tuple):
            TestFramework.bstack1lllll1111l_opy_(ob, TestFramework.bstack11llll1llll_opy_, str(args[1][0]))
        if context.platform_index >= 0:
            TestFramework.bstack1lllll1111l_opy_(ob, TestFramework.bstack1ll1111l111_opy_, context.platform_index)
        TestFramework.bstack1llll11l1l1_opy_[ctx.id] = ob
        self.logger.debug(bstack11l1l_opy_ (u"ࠢࡴࡣࡹࡩࡩࠦࡩ࡯ࡵࡷࡥࡳࡩࡥࠡࡥࡷࡼ࠳࡯ࡤ࠾ࡽࡦࡸࡽ࠴ࡩࡥࡿࠣࡸࡦࡸࡧࡦࡶࡀࡿࡹࡧࡲࡨࡧࡷࢁࠥࡧࡲࡨࡵࡀࡿࡦࡸࡧࡴࡿࠣ࡭ࡳࡹࡴࡢࡰࡦࡩࡸࡃࠢᔣ") + str(TestFramework.bstack1llll11l1l1_opy_.keys()) + bstack11l1l_opy_ (u"ࠣࠤᔤ"))
        return ob
    @staticmethod
    def __11llllllll1_opy_(instance, args):
        request, feature, scenario = args
        steps = []
        for step in scenario.steps:
            steps.append({
                bstack11l1l_opy_ (u"ࠩ࡬ࡨࠬᔥ"): id(step),
                bstack11l1l_opy_ (u"ࠪࡸࡪࡾࡴࠨᔦ"): step.name,
                bstack11l1l_opy_ (u"ࠫࡰ࡫ࡹࡸࡱࡵࡨࠬᔧ"): step.keyword,
            })
        meta = {
            bstack11l1l_opy_ (u"ࠬ࡬ࡥࡢࡶࡸࡶࡪ࠭ᔨ"): {
                bstack11l1l_opy_ (u"࠭࡮ࡢ࡯ࡨࠫᔩ"): feature.name,
                bstack11l1l_opy_ (u"ࠧࡱࡣࡷ࡬ࠬᔪ"): feature.filename,
                bstack11l1l_opy_ (u"ࠨࡦࡨࡷࡨࡸࡩࡱࡶ࡬ࡳࡳ࠭ᔫ"): feature.description
            },
            bstack11l1l_opy_ (u"ࠩࡶࡧࡪࡴࡡࡳ࡫ࡲࠫᔬ"): {
                bstack11l1l_opy_ (u"ࠪࡲࡦࡳࡥࠨᔭ"): scenario.name
            },
            bstack11l1l_opy_ (u"ࠫࡸࡺࡥࡱࡵࠪᔮ"): steps,
            bstack11l1l_opy_ (u"ࠬ࡫ࡸࡢ࡯ࡳࡰࡪࡹࠧᔯ"): PytestBDDFramework.__11lll1ll111_opy_(request.node)
        }
        instance.data.update(
            {
                TestFramework.bstack11llll1111l_opy_: meta
            }
        )
    def bstack1l11111ll11_opy_(self, hook: Dict[str, Any]) -> None:
        bstack11l1l_opy_ (u"ࠨࠢࠣࠌࠣࠤࠥࠦࠠࠡࠢࠣࡔࡷࡵࡣࡦࡵࡶࡩࡸࠦࡴࡩࡧࠣࡌࡴࡵ࡫ࡍࡧࡹࡩࡱࠦࡡࡵࡶࡤࡧ࡭ࡳࡥ࡯ࡶࡶࠤࡸ࡯࡭ࡪ࡮ࡤࡶࠥࡺ࡯ࠡࡶ࡫ࡩࠥࡐࡡࡷࡣࠣ࡭ࡲࡶ࡬ࡦ࡯ࡨࡲࡹࡧࡴࡪࡱࡱ࠲ࠏࠦࠠࠡࠢࠣࠤࠥࠦࡔࡩ࡫ࡶࠤࡲ࡫ࡴࡩࡱࡧ࠾ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡ࠯ࠣࡇ࡭࡫ࡣ࡬ࡵࠣࡸ࡭࡫ࠠࡉࡱࡲ࡯ࡑ࡫ࡶࡦ࡮ࠣࡨ࡮ࡸࡥࡤࡶࡲࡶࡾࠦࡩ࡯ࡵ࡬ࡨࡪࠦࡾ࠰࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠰ࡗࡳࡰࡴࡧࡤࡦࡦࡄࡸࡹࡧࡣࡩ࡯ࡨࡲࡹࡹ࠮ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤ࠲ࠦࡆࡰࡴࠣࡩࡦࡩࡨࠡࡨ࡬ࡰࡪࠦࡩ࡯ࠢ࡫ࡳࡴࡱ࡟࡭ࡧࡹࡩࡱࡥࡦࡪ࡮ࡨࡷ࠱ࠦࡲࡦࡲ࡯ࡥࡨ࡫ࡳࠡࠤࡗࡩࡸࡺࡌࡦࡸࡨࡰࠧࠦࡷࡪࡶ࡫ࠤࠧࡎ࡯ࡰ࡭ࡏࡩࡻ࡫࡬ࠣࠢ࡬ࡲࠥ࡯ࡴࡴࠢࡳࡥࡹ࡮࠮ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤ࠲ࠦࡉࡧࠢࡤࠤ࡫࡯࡬ࡦࠢ࡬ࡲࠥࡺࡨࡦࠢࡧ࡭ࡷ࡫ࡣࡵࡱࡵࡽࠥࡳࡡࡵࡥ࡫ࡩࡸࠦࡡࠡ࡯ࡲࡨ࡮࡬ࡩࡦࡦࠣ࡬ࡴࡵ࡫࠮࡮ࡨࡺࡪࡲࠠࡧ࡫࡯ࡩ࠱ࠦࡩࡵࠢࡦࡶࡪࡧࡴࡦࡵࠣࡥࠥࡒ࡯ࡨࡇࡱࡸࡷࡿࠠࡰࡤ࡭ࡩࡨࡺࠠࡸ࡫ࡷ࡬ࠥࡧࡴࡵࡣࡦ࡬ࡲ࡫࡮ࡵࠢࡧࡩࡹࡧࡩ࡭ࡵ࠱ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠ࠮ࠢࡖ࡭ࡲ࡯࡬ࡢࡴ࡯ࡽ࠱ࠦࡩࡵࠢࡳࡶࡴࡩࡥࡴࡵࡨࡷࠥࡈࡵࡪ࡮ࡧࡐࡪࡼࡥ࡭ࠢࡤࡸࡹࡧࡣࡩ࡯ࡨࡲࡹࡹࠠ࡭ࡱࡦࡥࡹ࡫ࡤࠡ࡫ࡱࠤࡍࡵ࡯࡬ࡎࡨࡺࡪࡲ࠯ࡃࡷ࡬ࡰࡩࡒࡥࡷࡧ࡯ࡌࡴࡵ࡫ࡆࡸࡨࡲࡹࠦࡢࡺࠢࡵࡩࡵࡲࡡࡤ࡫ࡱ࡫ࠥࠨࡂࡶ࡫࡯ࡨࡑ࡫ࡶࡦ࡮ࠥࠤࡼ࡯ࡴࡩࠢࠥࡌࡴࡵ࡫ࡍࡧࡹࡩࡱ࠵ࡂࡶ࡫࡯ࡨࡑ࡫ࡶࡦ࡮ࡋࡳࡴࡱࡅࡷࡧࡱࡸࠧ࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣ࠱࡚ࠥࡨࡦࠢࡦࡶࡪࡧࡴࡦࡦࠣࡐࡴ࡭ࡅ࡯ࡶࡵࡽࠥࡵࡢ࡫ࡧࡦࡸࡸࠦࡡࡳࡧࠣࡥࡩࡪࡥࡥࠢࡷࡳࠥࡺࡨࡦࠢ࡫ࡳࡴࡱࠧࡴࠢࠥࡰࡴ࡭ࡳࠣࠢ࡯࡭ࡸࡺ࠮ࠋࠢࠣࠤࠥࠦࠠࠡࠢࡄࡶ࡬ࡹ࠺ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࡨࡰࡱ࡮࠾࡚ࠥࡨࡦࠢࡨࡺࡪࡴࡴࠡࡦ࡬ࡧࡹ࡯࡯࡯ࡣࡵࡽࠥࡩ࡯࡯ࡶࡤ࡭ࡳ࡯࡮ࡨࠢࡨࡼ࡮ࡹࡴࡪࡰࡪࠤࡱࡵࡧࡴࠢࡤࡲࡩࠦࡨࡰࡱ࡮ࠤ࡮ࡴࡦࡰࡴࡰࡥࡹ࡯࡯࡯࠰ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࡪࡲࡳࡰࡥ࡬ࡦࡸࡨࡰࡤ࡬ࡩ࡭ࡧࡶ࠾ࠥࡒࡩࡴࡶࠣࡳ࡫ࠦࡐࡢࡶ࡫ࠤࡴࡨࡪࡦࡥࡷࡷࠥ࡬ࡲࡰ࡯ࠣࡸ࡭࡫ࠠࡕࡧࡶࡸࡑ࡫ࡶࡦ࡮ࠣࡱࡴࡴࡩࡵࡱࡵ࡭ࡳ࡭࠮ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࡢࡶ࡫࡯ࡨࡤࡲࡥࡷࡧ࡯ࡣ࡫࡯࡬ࡦࡵ࠽ࠤࡑ࡯ࡳࡵࠢࡲࡪࠥࡖࡡࡵࡪࠣࡳࡧࡰࡥࡤࡶࡶࠤ࡫ࡸ࡯࡮ࠢࡷ࡬ࡪࠦࡂࡶ࡫࡯ࡨࡑ࡫ࡶࡦ࡮ࠣࡱࡴࡴࡩࡵࡱࡵ࡭ࡳ࡭࠮ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠥࠦࠧᔰ")
        global _1l1l11l1l1l_opy_
        platform_index = os.environ[bstack11l1l_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡐࡍࡃࡗࡊࡔࡘࡍࡠࡋࡑࡈࡊ࡞ࠧᔱ")]
        bstack1l1l111l11l_opy_ = os.path.join(bstack1l1l11llll1_opy_, (bstack1l1l111ll11_opy_ + str(platform_index)), bstack11lll1l1111_opy_)
        if not os.path.exists(bstack1l1l111l11l_opy_) or not os.path.isdir(bstack1l1l111l11l_opy_):
            return
        logs = hook.get(bstack11l1l_opy_ (u"ࠣ࡮ࡲ࡫ࡸࠨᔲ"), [])
        with os.scandir(bstack1l1l111l11l_opy_) as entries:
            for entry in entries:
                abs_path = os.path.abspath(entry.path)
                if abs_path in _1l1l11l1l1l_opy_:
                    self.logger.info(bstack11l1l_opy_ (u"ࠤࡓࡥࡹ࡮ࠠࡢ࡮ࡵࡩࡦࡪࡹࠡࡲࡵࡳࡨ࡫ࡳࡴࡧࡧࠤࢀࢃࠢᔳ").format(abs_path))
                    continue
                if entry.is_file():
                    try:
                        timestamp = datetime.fromtimestamp(entry.stat().st_mtime, tz=timezone.utc).isoformat()
                    except Exception:
                        timestamp = bstack11l1l_opy_ (u"ࠥࠦᔴ")
                    log_entry = bstack1lll111l1l1_opy_(
                        kind=bstack11l1l_opy_ (u"࡙ࠦࡋࡓࡕࡡࡄࡘ࡙ࡇࡃࡉࡏࡈࡒ࡙ࠨᔵ"),
                        message=bstack11l1l_opy_ (u"ࠧࠨᔶ"),
                        level=bstack11l1l_opy_ (u"ࠨࠢᔷ"),
                        timestamp=timestamp,
                        fileName=entry.name,
                        bstack1l1ll11111l_opy_=entry.stat().st_size,
                        bstack1l1l1llll11_opy_=bstack11l1l_opy_ (u"ࠢࡎࡃࡑ࡙ࡆࡒ࡟ࡖࡒࡏࡓࡆࡊࠢᔸ"),
                        bstack1llllll_opy_=os.path.abspath(entry.path),
                        bstack11lll11ll11_opy_=hook.get(TestFramework.bstack11lll1l1l1l_opy_)
                    )
                    logs.append(log_entry)
                    _1l1l11l1l1l_opy_.add(abs_path)
        platform_index = os.environ[bstack11l1l_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡑࡎࡄࡘࡋࡕࡒࡎࡡࡌࡒࡉࡋࡘࠨᔹ")]
        bstack1l1111lll11_opy_ = os.path.join(bstack1l1l11llll1_opy_, (bstack1l1l111ll11_opy_ + str(platform_index)), bstack11lll1l1111_opy_, bstack1l1111l1lll_opy_)
        if not os.path.exists(bstack1l1111lll11_opy_) or not os.path.isdir(bstack1l1111lll11_opy_):
            self.logger.info(bstack11l1l_opy_ (u"ࠤࡑࡳࠥࡈࡵࡪ࡮ࡧࡐࡪࡼࡥ࡭ࡊࡲࡳࡰࡋࡶࡦࡰࡷࠤࡦࡺࡴࡢࡥ࡫ࡱࡪࡴࡴࡴࠢࡧ࡭ࡷ࡫ࡣࡵࡱࡵࡽࠥ࡬࡯ࡶࡰࡧࠤࡦࡺ࠺ࠡࡽࢀࠦᔺ").format(bstack1l1111lll11_opy_))
        else:
            self.logger.info(bstack11l1l_opy_ (u"ࠥࡔࡷࡵࡣࡦࡵࡶ࡭ࡳ࡭ࠠࡃࡷ࡬ࡰࡩࡒࡥࡷࡧ࡯ࡌࡴࡵ࡫ࡆࡸࡨࡲࡹࠦࡡࡵࡶࡤࡧ࡭ࡳࡥ࡯ࡶࡶࠤ࡫ࡸ࡯࡮ࠢࡧ࡭ࡷ࡫ࡣࡵࡱࡵࡽ࠿ࠦࡻࡾࠤᔻ").format(bstack1l1111lll11_opy_))
            with os.scandir(bstack1l1111lll11_opy_) as entries:
                for entry in entries:
                    abs_path = os.path.abspath(entry.path)
                    if abs_path in _1l1l11l1l1l_opy_:
                        self.logger.info(bstack11l1l_opy_ (u"ࠦࡕࡧࡴࡩࠢࡤࡰࡷ࡫ࡡࡥࡻࠣࡴࡷࡵࡣࡦࡵࡶࡩࡩࠦࡻࡾࠤᔼ").format(abs_path))
                        continue
                    if entry.is_file():
                        try:
                            timestamp = datetime.fromtimestamp(entry.stat().st_mtime, tz=timezone.utc).isoformat()
                        except Exception:
                            timestamp = bstack11l1l_opy_ (u"ࠧࠨᔽ")
                        log_entry = bstack1lll111l1l1_opy_(
                            kind=bstack11l1l_opy_ (u"ࠨࡔࡆࡕࡗࡣࡆ࡚ࡔࡂࡅࡋࡑࡊࡔࡔࠣᔾ"),
                            message=bstack11l1l_opy_ (u"ࠢࠣᔿ"),
                            level=bstack11l1l_opy_ (u"ࠣࡄࡸ࡭ࡱࡪࡌࡦࡸࡨࡰࠧᕀ"),
                            timestamp=timestamp,
                            fileName=entry.name,
                            bstack1l1ll11111l_opy_=entry.stat().st_size,
                            bstack1l1l1llll11_opy_=bstack11l1l_opy_ (u"ࠤࡐࡅࡓ࡛ࡁࡍࡡࡘࡔࡑࡕࡁࡅࠤᕁ"),
                            bstack1llllll_opy_=os.path.abspath(entry.path),
                            bstack1l1l1l1111l_opy_=hook.get(TestFramework.bstack11lll1l1l1l_opy_)
                        )
                        logs.append(log_entry)
                        _1l1l11l1l1l_opy_.add(abs_path)
        hook[bstack11l1l_opy_ (u"ࠥࡰࡴ࡭ࡳࠣᕂ")] = logs
    def bstack1l1l1l1l111_opy_(
        self,
        bstack1l1l1111l11_opy_: bstack1ll1ll11lll_opy_,
        entries: List[bstack1lll111l1l1_opy_],
    ):
        req = structs.LogCreatedEventRequest()
        req.bin_session_id = os.environ.get(bstack11l1l_opy_ (u"ࠦࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡇࡑࡏ࡟ࡃࡋࡑࡣࡘࡋࡓࡔࡋࡒࡒࡤࡏࡄࠣᕃ"))
        req.platform_index = TestFramework.bstack1llll1lllll_opy_(bstack1l1l1111l11_opy_, TestFramework.bstack1ll1111l111_opy_)
        req.execution_context.hash = str(bstack1l1l1111l11_opy_.context.hash)
        req.execution_context.thread_id = str(bstack1l1l1111l11_opy_.context.thread_id)
        req.execution_context.process_id = str(bstack1l1l1111l11_opy_.context.process_id)
        for entry in entries:
            log_entry = req.logs.add()
            log_entry.test_framework_name = TestFramework.bstack1llll1lllll_opy_(bstack1l1l1111l11_opy_, TestFramework.bstack1l1llll11l1_opy_)
            log_entry.test_framework_version = TestFramework.bstack1llll1lllll_opy_(bstack1l1l1111l11_opy_, TestFramework.bstack1l1l1lll1ll_opy_)
            log_entry.uuid = entry.bstack11lll11ll11_opy_ if entry.bstack11lll11ll11_opy_ else TestFramework.bstack1llll1lllll_opy_(bstack1l1l1111l11_opy_, TestFramework.bstack1ll11l11l1l_opy_)
            log_entry.test_framework_state = bstack1l1l1111l11_opy_.state.name
            log_entry.message = entry.message.encode(bstack11l1l_opy_ (u"ࠧࡻࡴࡧ࠯࠻ࠦᕄ"))
            log_entry.kind = entry.kind
            log_entry.timestamp = (
                entry.timestamp.isoformat()
                if isinstance(entry.timestamp, datetime)
                else datetime.now(tz=timezone.utc).isoformat()
            )
            if isinstance(entry.level, str) and len(entry.level.strip()) > 0:
                log_entry.level = entry.level.strip()
            if entry.kind == bstack11l1l_opy_ (u"ࠨࡔࡆࡕࡗࡣࡆ࡚ࡔࡂࡅࡋࡑࡊࡔࡔࠣᕅ"):
                log_entry.file_name = entry.fileName
                log_entry.file_size = entry.bstack1l1ll11111l_opy_
                log_entry.file_path = entry.bstack1llllll_opy_
        def bstack1l1l1l1l1l1_opy_():
            bstack11ll1l1ll1_opy_ = datetime.now()
            try:
                self.bstack1ll1ll11l11_opy_.LogCreatedEvent(req)
                bstack1l1l1111l11_opy_.bstack11lll111_opy_(bstack11l1l_opy_ (u"ࠢࡨࡴࡳࡧ࠿ࡹࡥ࡯ࡦࡢࡰࡴ࡭࡟ࡤࡴࡨࡥࡹ࡫ࡤࡠࡧࡹࡩࡳࡺ࡟ࡢࡶࡷࡥࡨ࡮࡭ࡦࡰࡷࠦᕆ"), datetime.now() - bstack11ll1l1ll1_opy_)
            except grpc.RpcError as e:
                self.log_error(bstack11l1l_opy_ (u"ࠣࡴࡳࡧ࠲࡫ࡲࡳࡱࡵ࠾ࠥࡹࡥ࡯ࡦࡢࡰࡴ࡭࡟ࡤࡴࡨࡥࡹ࡫ࡤࡠࡧࡹࡩࡳࡺ࡟ࡢࡶࡷࡥࡨ࡮࡭ࡦࡰࡷࠤࢀࢃࠢᕇ").format(str(e)))
                traceback.print_exc()
        self.bstack1lllll1l11l_opy_.enqueue(bstack1l1l1l1l1l1_opy_)
    def __1l11111ll1l_opy_(self, instance) -> None:
        bstack11l1l_opy_ (u"ࠤࠥࠦࠏࠦࠠࠡࠢࠣࠤࠥࠦࡌࡰࡣࡧࡷࠥࡩࡵࡴࡶࡲࡱࠥࡺࡡࡨࡵࠣࡪࡴࡸࠠࡵࡪࡨࠤ࡬࡯ࡶࡦࡰࠣࡸࡪࡹࡴࠡࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࠤ࡮ࡴࡳࡵࡣࡱࡧࡪ࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࡅࡵࡩࡦࡺࡥࡴࠢࡤࠤࡩ࡯ࡣࡵࠢࡦࡳࡳࡺࡡࡪࡰ࡬ࡲ࡬ࠦࡴࡦࡵࡷࠤࡱ࡫ࡶࡦ࡮ࠣࡧࡺࡹࡴࡰ࡯ࠣࡱࡪࡺࡡࡥࡣࡷࡥࠥࡸࡥࡵࡴ࡬ࡩࡻ࡫ࡤࠡࡨࡵࡳࡲࠐࠠࠡࠢࠣࠤࠥࠦࠠࡄࡷࡶࡸࡴࡳࡔࡢࡩࡐࡥࡳࡧࡧࡦࡴࠣࡥࡳࡪࠠࡶࡲࡧࡥࡹ࡫ࡳࠡࡶ࡫ࡩࠥ࡯࡮ࡴࡶࡤࡲࡨ࡫ࠠࡴࡶࡤࡸࡪࠦࡵࡴ࡫ࡱ࡫ࠥࡹࡥࡵࡡࡶࡸࡦࡺࡥࡠࡧࡱࡸࡷ࡯ࡥࡴ࠰ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠧࠨࠢᕈ")
        bstack11llll1ll1l_opy_ = {bstack11l1l_opy_ (u"ࠥࡧࡺࡹࡴࡰ࡯ࡢࡱࡪࡺࡡࡥࡣࡷࡥࠧᕉ"): bstack1ll1llll1ll_opy_.bstack11lll11llll_opy_()}
        TestFramework.bstack11lllll11l1_opy_(instance, bstack11llll1ll1l_opy_)
    @staticmethod
    def __11llll11lll_opy_(instance, args):
        request, bstack1l1111l1l1l_opy_ = args
        bstack11lll11ll1l_opy_ = id(bstack1l1111l1l1l_opy_)
        bstack11lll1ll11l_opy_ = instance.data[TestFramework.bstack11llll1111l_opy_]
        step = next(filter(lambda st: st[bstack11l1l_opy_ (u"ࠫ࡮ࡪࠧᕊ")] == bstack11lll11ll1l_opy_, bstack11lll1ll11l_opy_[bstack11l1l_opy_ (u"ࠬࡹࡴࡦࡲࡶࠫᕋ")]), None)
        step.update({
            bstack11l1l_opy_ (u"࠭ࡳࡵࡣࡵࡸࡪࡪ࡟ࡢࡶࠪᕌ"): datetime.now(tz=timezone.utc)
        })
        index = next((i for i, st in enumerate(bstack11lll1ll11l_opy_[bstack11l1l_opy_ (u"ࠧࡴࡶࡨࡴࡸ࠭ᕍ")]) if st[bstack11l1l_opy_ (u"ࠨ࡫ࡧࠫᕎ")] == step[bstack11l1l_opy_ (u"ࠩ࡬ࡨࠬᕏ")]), None)
        if index is not None:
            bstack11lll1ll11l_opy_[bstack11l1l_opy_ (u"ࠪࡷࡹ࡫ࡰࡴࠩᕐ")][index] = step
        instance.data[TestFramework.bstack11llll1111l_opy_] = bstack11lll1ll11l_opy_
    @staticmethod
    def __11llll11ll1_opy_(instance, args):
        bstack11l1l_opy_ (u"ࠦࠧࠨࠊࠡࠢࠣࠤࠥࠦࠠࠡࡹ࡫ࡩࡳࠦ࡬ࡦࡰࠣࡥࡷ࡭ࡳࠡ࡫ࡶࠤ࠷࠲ࠠࡪࡶࠣࡷ࡮࡭࡮ࡪࡨ࡬ࡩࡸࠦࡴࡩࡧࡵࡩࠥ࡯ࡳࠡࡰࡲࠤࡪࡾࡣࡦࡲࡷ࡭ࡴࡴࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࡧࡲࡨࡵࠣࡥࡷ࡫ࠠ࠮ࠢ࡞ࡶࡪࡷࡵࡦࡵࡷ࠰ࠥࡹࡴࡦࡲࡠࠎࠥࠦࠠࠡࠢࠣࠤࠥ࡯ࡦࠡࡣࡵ࡫ࡸࠦࡡࡳࡧࠣ࠷ࠥࡺࡨࡦࡰࠣࡸ࡭࡫ࠠ࡭ࡣࡶࡸࠥࡼࡡ࡭ࡷࡨࠤ࡮ࡹࠠࡦࡺࡦࡩࡵࡺࡩࡰࡰࠍࠤࠥࠦࠠࠡࠢࠣࠤࠧࠨࠢᕑ")
        bstack11llllll111_opy_ = datetime.now(tz=timezone.utc)
        request = args[0]
        bstack1l1111l1l1l_opy_ = args[1]
        bstack11lll11ll1l_opy_ = id(bstack1l1111l1l1l_opy_)
        bstack11lll1ll11l_opy_ = instance.data[TestFramework.bstack11llll1111l_opy_]
        step = None
        if bstack11lll11ll1l_opy_ is not None and bstack11lll1ll11l_opy_.get(bstack11l1l_opy_ (u"ࠬࡹࡴࡦࡲࡶࠫᕒ")):
            step = next(filter(lambda st: st[bstack11l1l_opy_ (u"࠭ࡩࡥࠩᕓ")] == bstack11lll11ll1l_opy_, bstack11lll1ll11l_opy_[bstack11l1l_opy_ (u"ࠧࡴࡶࡨࡴࡸ࠭ᕔ")]), None)
            step.update({
                bstack11l1l_opy_ (u"ࠨࡨ࡬ࡲ࡮ࡹࡨࡦࡦࡢࡥࡹ࠭ᕕ"): bstack11llllll111_opy_,
            })
        if len(args) > 2:
            exception = args[2]
            step.update({
                bstack11l1l_opy_ (u"ࠩࡵࡩࡸࡻ࡬ࡵࠩᕖ"): bstack11l1l_opy_ (u"ࠪࡪࡦ࡯࡬ࡦࡦࠪᕗ"),
                bstack11l1l_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡷࡵࡩࠬᕘ"): str(exception)
            })
        else:
            if step is not None:
                step.update({
                    bstack11l1l_opy_ (u"ࠬࡸࡥࡴࡷ࡯ࡸࠬᕙ"): bstack11l1l_opy_ (u"࠭ࡰࡢࡵࡶࡩࡩ࠭ᕚ"),
                })
        index = next((i for i, st in enumerate(bstack11lll1ll11l_opy_[bstack11l1l_opy_ (u"ࠧࡴࡶࡨࡴࡸ࠭ᕛ")]) if st[bstack11l1l_opy_ (u"ࠨ࡫ࡧࠫᕜ")] == step[bstack11l1l_opy_ (u"ࠩ࡬ࡨࠬᕝ")]), None)
        if index is not None:
            bstack11lll1ll11l_opy_[bstack11l1l_opy_ (u"ࠪࡷࡹ࡫ࡰࡴࠩᕞ")][index] = step
        instance.data[TestFramework.bstack11llll1111l_opy_] = bstack11lll1ll11l_opy_
    @staticmethod
    def __11lll1ll111_opy_(node):
        try:
            examples = []
            if hasattr(node, bstack11l1l_opy_ (u"ࠫࡨࡧ࡬࡭ࡵࡳࡩࡨ࠭ᕟ")):
                examples = list(node.callspec.params[bstack11l1l_opy_ (u"ࠬࡥࡰࡺࡶࡨࡷࡹࡥࡢࡥࡦࡢࡩࡽࡧ࡭ࡱ࡮ࡨࠫᕠ")].values())
            return examples
        except:
            return []
    def bstack1l1l1111lll_opy_(self, instance: bstack1ll1ll11lll_opy_, bstack1llll1lll1l_opy_: Tuple[bstack1lll111l111_opy_, bstack1lll1l1l11l_opy_]):
        bstack11llll11l11_opy_ = (
            PytestBDDFramework.bstack11lll11lll1_opy_
            if bstack1llll1lll1l_opy_[1] == bstack1lll1l1l11l_opy_.PRE
            else PytestBDDFramework.bstack1l11111llll_opy_
        )
        hook = PytestBDDFramework.bstack11llll111l1_opy_(instance, bstack11llll11l11_opy_)
        entries = hook.get(TestFramework.bstack1l1111ll1l1_opy_, []) if isinstance(hook, dict) else []
        entries.extend(TestFramework.bstack1llll1lllll_opy_(instance, TestFramework.bstack1l1111111l1_opy_, []))
        return entries
    def bstack1l1l1l11lll_opy_(self, instance: bstack1ll1ll11lll_opy_, bstack1llll1lll1l_opy_: Tuple[bstack1lll111l111_opy_, bstack1lll1l1l11l_opy_]):
        bstack11llll11l11_opy_ = (
            PytestBDDFramework.bstack11lll11lll1_opy_
            if bstack1llll1lll1l_opy_[1] == bstack1lll1l1l11l_opy_.PRE
            else PytestBDDFramework.bstack1l11111llll_opy_
        )
        PytestBDDFramework.bstack1l111111l11_opy_(instance, bstack11llll11l11_opy_)
        TestFramework.bstack1llll1lllll_opy_(instance, TestFramework.bstack1l1111111l1_opy_, []).clear()
    @staticmethod
    def bstack11llll111l1_opy_(instance: bstack1ll1ll11lll_opy_, bstack11llll11l11_opy_: str):
        bstack11lll1l11l1_opy_ = (
            PytestBDDFramework.bstack11lll1ll1l1_opy_
            if bstack11llll11l11_opy_ == PytestBDDFramework.bstack1l11111llll_opy_
            else PytestBDDFramework.bstack11llll11111_opy_
        )
        bstack1l1111lll1l_opy_ = TestFramework.bstack1llll1lllll_opy_(instance, bstack11llll11l11_opy_, None)
        bstack11lll1ll1ll_opy_ = TestFramework.bstack1llll1lllll_opy_(instance, bstack11lll1l11l1_opy_, None) if bstack1l1111lll1l_opy_ else None
        return (
            bstack11lll1ll1ll_opy_[bstack1l1111lll1l_opy_][-1]
            if isinstance(bstack11lll1ll1ll_opy_, dict) and len(bstack11lll1ll1ll_opy_.get(bstack1l1111lll1l_opy_, [])) > 0
            else None
        )
    @staticmethod
    def bstack1l111111l11_opy_(instance: bstack1ll1ll11lll_opy_, bstack11llll11l11_opy_: str):
        hook = PytestBDDFramework.bstack11llll111l1_opy_(instance, bstack11llll11l11_opy_)
        if isinstance(hook, dict):
            hook.get(TestFramework.bstack1l1111ll1l1_opy_, []).clear()
    @staticmethod
    def __11lllll1111_opy_(instance: bstack1ll1ll11lll_opy_, *args):
        if len(args) < 2 or not callable(getattr(args[1], bstack11l1l_opy_ (u"ࠨࡧࡦࡶࡢࡶࡪࡩ࡯ࡳࡦࡶࠦᕡ"), None)):
            return
        if os.getenv(bstack11l1l_opy_ (u"ࠢࡔࡆࡎࡣࡈࡒࡉࡠࡈࡏࡅࡌࡥࡌࡐࡉࡖࠦᕢ"), bstack11l1l_opy_ (u"ࠣ࠳ࠥᕣ")) != bstack11l1l_opy_ (u"ࠤ࠴ࠦᕤ"):
            PytestBDDFramework.logger.warning(bstack11l1l_opy_ (u"ࠥ࡭࡬ࡴ࡯ࡳ࡫ࡱ࡫ࠥࡩࡡࡱ࡮ࡲ࡫ࠧᕥ"))
            return
        bstack1l1111l11l1_opy_ = {
            bstack11l1l_opy_ (u"ࠦࡸ࡫ࡴࡶࡲࠥᕦ"): (PytestBDDFramework.bstack11lll11lll1_opy_, PytestBDDFramework.bstack11llll11111_opy_),
            bstack11l1l_opy_ (u"ࠧࡺࡥࡢࡴࡧࡳࡼࡴࠢᕧ"): (PytestBDDFramework.bstack1l11111llll_opy_, PytestBDDFramework.bstack11lll1ll1l1_opy_),
        }
        for when in (bstack11l1l_opy_ (u"ࠨࡳࡦࡶࡸࡴࠧᕨ"), bstack11l1l_opy_ (u"ࠢࡤࡣ࡯ࡰࠧᕩ"), bstack11l1l_opy_ (u"ࠣࡶࡨࡥࡷࡪ࡯ࡸࡰࠥᕪ")):
            bstack1l111111lll_opy_ = args[1].get_records(when)
            if not bstack1l111111lll_opy_:
                continue
            records = [
                bstack1lll111l1l1_opy_(
                    kind=TestFramework.bstack1l1l1llllll_opy_,
                    message=r.message,
                    level=r.levelname if hasattr(r, bstack11l1l_opy_ (u"ࠤ࡯ࡩࡻ࡫࡬࡯ࡣࡰࡩࠧᕫ")) and r.levelname else None,
                    timestamp=(
                        datetime.fromtimestamp(r.created, tz=timezone.utc)
                        if hasattr(r, bstack11l1l_opy_ (u"ࠥࡧࡷ࡫ࡡࡵࡧࡧࠦᕬ")) and r.created
                        else None
                    ),
                )
                for r in bstack1l111111lll_opy_
                if isinstance(getattr(r, bstack11l1l_opy_ (u"ࠦࡲ࡫ࡳࡴࡣࡪࡩࠧᕭ"), None), str) and r.message.strip()
            ]
            if not records:
                continue
            bstack11lll1lll1l_opy_, bstack11lll1l11l1_opy_ = bstack1l1111l11l1_opy_.get(when, (None, None))
            bstack11llll1lll1_opy_ = TestFramework.bstack1llll1lllll_opy_(instance, bstack11lll1lll1l_opy_, None) if bstack11lll1lll1l_opy_ else None
            bstack11lll1ll1ll_opy_ = TestFramework.bstack1llll1lllll_opy_(instance, bstack11lll1l11l1_opy_, None) if bstack11llll1lll1_opy_ else None
            if isinstance(bstack11lll1ll1ll_opy_, dict) and len(bstack11lll1ll1ll_opy_.get(bstack11llll1lll1_opy_, [])) > 0:
                hook = bstack11lll1ll1ll_opy_[bstack11llll1lll1_opy_][-1]
                if isinstance(hook, dict) and TestFramework.bstack1l1111ll1l1_opy_ in hook:
                    hook[TestFramework.bstack1l1111ll1l1_opy_].extend(records)
                    continue
            logs = TestFramework.bstack1llll1lllll_opy_(instance, TestFramework.bstack1l1111111l1_opy_, [])
            logs.extend(records)
    @staticmethod
    def __11llllll1l1_opy_(args) -> Dict[str, Any]:
        request, feature, scenario = args
        bstack1lll1ll111_opy_ = request.node.nodeid
        test_name = PytestBDDFramework.__11lll1l11ll_opy_(request.node, scenario)
        bstack11llll111ll_opy_ = feature.filename
        if not bstack1lll1ll111_opy_ or not test_name or not bstack11llll111ll_opy_:
            return None
        code = None
        return {
            TestFramework.bstack1ll11l11l1l_opy_: uuid4().__str__(),
            TestFramework.bstack1l11111lll1_opy_: bstack1lll1ll111_opy_,
            TestFramework.bstack1l1llll1ll1_opy_: test_name,
            TestFramework.bstack1l11lllll1l_opy_: bstack1lll1ll111_opy_,
            TestFramework.bstack11llllll1ll_opy_: bstack11llll111ll_opy_,
            TestFramework.bstack1l11111111l_opy_: PytestBDDFramework.__11llll1ll11_opy_(feature, scenario),
            TestFramework.bstack11lllll1lll_opy_: code,
            TestFramework.bstack1l11l1lllll_opy_: TestFramework.bstack1l11111l1l1_opy_,
            TestFramework.bstack1l111ll11ll_opy_: test_name
        }
    @staticmethod
    def __11lll1l11ll_opy_(node, scenario):
        if hasattr(node, bstack11l1l_opy_ (u"ࠬࡩࡡ࡭࡮ࡶࡴࡪࡩࠧᕮ")):
            parts = node.nodeid.rsplit(bstack11l1l_opy_ (u"ࠨ࡛ࠣᕯ"))
            params = parts[-1]
            return bstack11l1l_opy_ (u"ࠢࡼࡿࠣ࡟ࢀࢃࠢᕰ").format(scenario.name, params)
        return scenario.name
    @staticmethod
    def __11llll1ll11_opy_(feature, scenario) -> List[str]:
        return (list(feature.tags) if hasattr(feature, bstack11l1l_opy_ (u"ࠨࡶࡤ࡫ࡸ࠭ᕱ")) else []) + (list(scenario.tags) if hasattr(scenario, bstack11l1l_opy_ (u"ࠩࡷࡥ࡬ࡹࠧᕲ")) else [])
    @staticmethod
    def __11lll1lllll_opy_(location):
        return bstack11l1l_opy_ (u"ࠥ࠾࠿ࠨᕳ").join(filter(lambda x: isinstance(x, str), location))