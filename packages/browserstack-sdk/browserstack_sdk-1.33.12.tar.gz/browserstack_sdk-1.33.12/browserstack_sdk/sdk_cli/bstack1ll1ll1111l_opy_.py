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
from browserstack_sdk.sdk_cli.test_framework import (
    TestFramework,
    bstack1llll1ll111_opy_,
    bstack1lll1l11l11_opy_,
    bstack1lll1111l11_opy_,
    bstack1lll1l1ll1l_opy_,
    bstack1lll1ll1lll_opy_,
)
from pathlib import Path
import grpc
from browserstack_sdk import sdk_pb2 as structs
from datetime import datetime, timezone
from typing import List, Dict, Any
import traceback
from bstack_utils.helper import bstack1llll111l1l_opy_
from bstack_utils.bstack11l11l11ll_opy_ import bstack1lll111111l_opy_
from bstack_utils.constants import EVENTS
from browserstack_sdk.sdk_cli.bstack1lll1l1llll_opy_ import bstack1lll11ll11l_opy_
from browserstack_sdk.sdk_cli.utils.bstack1lll11l11l1_opy_ import bstack1lll11l1lll_opy_
from bstack_utils.bstack111ll11lll_opy_ import bstack1l11llll1l_opy_
bstack1lll11lll1l_opy_ = bstack1llll111l1l_opy_()
bstack1lll1l1l1l1_opy_ = 1.0
bstack1ll1ll1l11l_opy_ = bstack11ll1_opy_ (u"ࠣࡗࡳࡰࡴࡧࡤࡦࡦࡄࡸࡹࡧࡣࡩ࡯ࡨࡲࡹࡹ࠭ࠣᆤ")
bstack1ll1ll11111_opy_ = bstack11ll1_opy_ (u"ࠤࡗࡩࡸࡺࡌࡦࡸࡨࡰࠧᆥ")
bstack1ll1ll111l1_opy_ = bstack11ll1_opy_ (u"ࠥࡆࡺ࡯࡬ࡥࡎࡨࡺࡪࡲࠢᆦ")
bstack1ll1l1llll1_opy_ = bstack11ll1_opy_ (u"ࠦࡍࡵ࡯࡬ࡎࡨࡺࡪࡲࠢᆧ")
bstack1ll1ll11l11_opy_ = bstack11ll1_opy_ (u"ࠧࡈࡵࡪ࡮ࡧࡐࡪࡼࡥ࡭ࡊࡲࡳࡰࡋࡶࡦࡰࡷࠦᆨ")
_1lll111l1l1_opy_ = set()
class bstack1ll1l1lllll_opy_(TestFramework):
    bstack1lllll11l11_opy_ = bstack11ll1_opy_ (u"ࠨࡴࡦࡵࡷࡣ࡫࡯ࡸࡵࡷࡵࡩࡸࠨᆩ")
    bstack1ll1llll1ll_opy_ = bstack11ll1_opy_ (u"ࠢࡵࡧࡶࡸࡤ࡮࡯ࡰ࡭ࡶࡣࡸࡺࡡࡳࡶࡨࡨࠧᆪ")
    bstack1lll11lll11_opy_ = bstack11ll1_opy_ (u"ࠣࡶࡨࡷࡹࡥࡨࡰࡱ࡮ࡷࡤ࡬ࡩ࡯࡫ࡶ࡬ࡪࡪࠢᆫ")
    bstack1lll111lll1_opy_ = bstack11ll1_opy_ (u"ࠤࡷࡩࡸࡺ࡟ࡩࡱࡲ࡯ࡤࡲࡡࡴࡶࡢࡷࡹࡧࡲࡵࡧࡧࠦᆬ")
    bstack1llll1lllll_opy_ = bstack11ll1_opy_ (u"ࠥࡸࡪࡹࡴࡠࡪࡲࡳࡰࡥ࡬ࡢࡵࡷࡣ࡫࡯࡮ࡪࡵ࡫ࡩࡩࠨᆭ")
    bstack1llll11ll1l_opy_: bool
    bstack1lll1l1llll_opy_: bstack1lll11ll11l_opy_  = None
    bstack1lllll11ll1_opy_ = None
    bstack1ll1ll11ll1_opy_ = [
        bstack1llll1ll111_opy_.BEFORE_ALL,
        bstack1llll1ll111_opy_.AFTER_ALL,
        bstack1llll1ll111_opy_.BEFORE_EACH,
        bstack1llll1ll111_opy_.AFTER_EACH,
    ]
    def __init__(
        self,
        bstack1lll1l11111_opy_: Dict[str, str],
        bstack1ll1ll1llll_opy_: List[str]=[bstack11ll1_opy_ (u"ࠦࡵࡿࡴࡦࡵࡷࠦᆮ")],
        bstack1lll1l1llll_opy_: bstack1lll11ll11l_opy_=None,
        bstack1lllll11ll1_opy_=None
    ):
        super().__init__(bstack1ll1ll1llll_opy_, bstack1lll1l11111_opy_, bstack1lll1l1llll_opy_)
        self.bstack1llll11ll1l_opy_ = any(bstack11ll1_opy_ (u"ࠧࡶࡹࡵࡧࡶࡸࠧᆯ") in item.lower() for item in bstack1ll1ll1llll_opy_)
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
        if test_framework_state == bstack1llll1ll111_opy_.TEST or test_framework_state in bstack1ll1l1lllll_opy_.bstack1ll1ll11ll1_opy_:
            bstack1ll1lllllll_opy_(test_framework_state, test_hook_state)
        if test_framework_state == bstack1llll1ll111_opy_.NONE:
            self.logger.warning(bstack11ll1_opy_ (u"ࠨࡩࡨࡰࡲࡶࡪࡪࠠࡤࡣ࡯ࡰࡧࡧࡣ࡬ࠢࡷࡩࡸࡺ࡟ࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡢࡷࡹࡧࡴࡦ࠿ࡾࡸࡪࡹࡴࡠࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡸࡺࡡࡵࡧࢀࠤࡹ࡫ࡳࡵࡡ࡫ࡳࡴࡱ࡟ࡴࡶࡤࡸࡪࡃࠢᆰ") + str(test_hook_state) + bstack11ll1_opy_ (u"ࠢࠣᆱ"))
            return
        if not self.bstack1llll11ll1l_opy_:
            self.logger.warning(bstack11ll1_opy_ (u"ࠣࡶࡵࡥࡨࡱ࡟ࡦࡸࡨࡲࡹࡀࠠࡶࡰࡶࡹࡵࡶ࡯ࡳࡶࡨࡨࠥ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫࠾ࠤᆲ") + str(str(self.bstack1ll1ll1llll_opy_)) + bstack11ll1_opy_ (u"ࠤࠥᆳ"))
            return
        if not isinstance(args, tuple) or len(args) == 0:
            self.logger.warning(bstack11ll1_opy_ (u"ࠥࡸࡷࡧࡣ࡬ࡡࡨࡺࡪࡴࡴ࠻ࠢࡸࡲࡪࡾࡰࡦࡥࡷࡩࡩࠦࡡࡳࡩࡶࡁࢀࡧࡲࡨࡵࢀࠤࡰࡽࡡࡳࡩࡶࡁࠧᆴ") + str(kwargs) + bstack11ll1_opy_ (u"ࠦࠧᆵ"))
            return
        instance = self.__1llll11ll11_opy_(context, test_framework_state, test_hook_state, *args, **kwargs)
        if not instance:
            self.logger.debug(bstack11ll1_opy_ (u"ࠧࡺࡲࡢࡥ࡮ࡣࡪࡼࡥ࡯ࡶ࠽ࠤࡺࡴࡨࡢࡰࡧࡰࡪࡪࠠࡦࡸࡨࡲࡹࡃࡻࡵࡧࡶࡸࡤ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡵࡷࡥࡹ࡫ࡽ࠯ࡽࡷࡩࡸࡺ࡟ࡩࡱࡲ࡯ࡤࡹࡴࡢࡶࡨࢁࠥࡧࡲࡨࡵࡀࠦᆶ") + str(args) + bstack11ll1_opy_ (u"ࠨࠢᆷ"))
            return
        try:
            if instance!= None and test_framework_state in bstack1ll1l1lllll_opy_.bstack1ll1ll11ll1_opy_ and test_hook_state == bstack1lll1111l11_opy_.PRE:
                bstack1lll1l1ll11_opy_ = bstack1lll111111l_opy_.bstack1lll1111lll_opy_(EVENTS.bstack11l1llllll_opy_.value)
                name = str(EVENTS.bstack11l1llllll_opy_.name)+bstack11ll1_opy_ (u"ࠢ࠻ࠤᆸ")+str(test_framework_state.name)
                TestFramework.bstack1ll1lll1l11_opy_(instance, name, bstack1lll1l1ll11_opy_)
        except Exception as e:
            self.logger.debug(bstack11ll1_opy_ (u"ࠣࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡩࡱࡲ࡯ࠥ࡫ࡲࡳࡱࡵࠤࡵࡸࡥ࠻ࠢࡾࢁࠧᆹ").format(e))
        try:
            if not TestFramework.bstack1lll1ll1ll1_opy_(instance, TestFramework.bstack1llll1l1111_opy_) and test_hook_state == bstack1lll1111l11_opy_.PRE:
                test = bstack1ll1l1lllll_opy_.__1ll1ll1ll11_opy_(args[0])
                if test:
                    instance.data.update(test)
                    self.logger.debug(bstack11ll1_opy_ (u"ࠤ࡯ࡳࡦࡪࡥࡥࠢ࡬ࡲࡸࡺࡡ࡯ࡥࡨࡁࢀ࡯࡮ࡴࡶࡤࡲࡨ࡫࠮ࡳࡧࡩࠬ࠮ࢃࠠࡦࡸࡨࡲࡹࡃࡻࡵࡧࡶࡸࡤ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡵࡷࡥࡹ࡫ࡽ࠯ࠤᆺ") + str(test_hook_state) + bstack11ll1_opy_ (u"ࠥࠦᆻ"))
            if test_framework_state == bstack1llll1ll111_opy_.TEST:
                if test_hook_state == bstack1lll1111l11_opy_.PRE and not TestFramework.bstack1lll1ll1ll1_opy_(instance, TestFramework.bstack1lllll1111l_opy_):
                    TestFramework.bstack1lll111ll11_opy_(instance, TestFramework.bstack1lllll1111l_opy_, datetime.now(tz=timezone.utc))
                    self.logger.debug(bstack11ll1_opy_ (u"ࠦࡸ࡫ࡴࠡࡶࡨࡷࡹ࠳ࡳࡵࡣࡵࡸࠥ࡬࡯ࡳࠢ࡬ࡲࡸࡺࡡ࡯ࡥࡨࡁࢀ࡯࡮ࡴࡶࡤࡲࡨ࡫࠮ࡳࡧࡩࠬ࠮ࢃࠠࡦࡸࡨࡲࡹࡃࡻࡵࡧࡶࡸࡤ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡵࡷࡥࡹ࡫ࡽ࠯ࠤᆼ") + str(test_hook_state) + bstack11ll1_opy_ (u"ࠧࠨᆽ"))
                elif test_hook_state == bstack1lll1111l11_opy_.POST and not TestFramework.bstack1lll1ll1ll1_opy_(instance, TestFramework.bstack1lll1ll111l_opy_):
                    TestFramework.bstack1lll111ll11_opy_(instance, TestFramework.bstack1lll1ll111l_opy_, datetime.now(tz=timezone.utc))
                    self.logger.debug(bstack11ll1_opy_ (u"ࠨࡳࡦࡶࠣࡸࡪࡹࡴ࠮ࡧࡱࡨࠥ࡬࡯ࡳࠢ࡬ࡲࡸࡺࡡ࡯ࡥࡨࡁࢀ࡯࡮ࡴࡶࡤࡲࡨ࡫࠮ࡳࡧࡩࠬ࠮ࢃࠠࡦࡸࡨࡲࡹࡃࡻࡵࡧࡶࡸࡤ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡵࡷࡥࡹ࡫ࡽ࠯ࠤᆾ") + str(test_hook_state) + bstack11ll1_opy_ (u"ࠢࠣᆿ"))
            elif test_framework_state == bstack1llll1ll111_opy_.LOG and test_hook_state == bstack1lll1111l11_opy_.POST:
                bstack1ll1l1lllll_opy_.__1llll1ll1ll_opy_(instance, *args)
            elif test_framework_state == bstack1llll1ll111_opy_.LOG_REPORT and test_hook_state == bstack1lll1111l11_opy_.POST:
                self.__1llll1ll11l_opy_(instance, *args)
                self.__1ll1lll11ll_opy_(instance)
            elif test_framework_state in bstack1ll1l1lllll_opy_.bstack1ll1ll11ll1_opy_:
                self.__1llll1l1l11_opy_(instance, test_framework_state, test_hook_state, *args)
            self.logger.debug(bstack11ll1_opy_ (u"ࠣࡶࡵࡥࡨࡱ࡟ࡦࡸࡨࡲࡹࡀࠠࡩࡣࡱࡨࡱ࡫ࡤࠡࡧࡹࡩࡳࡺ࠽ࡼࡶࡨࡷࡹࡥࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡶࡸࡦࡺࡥࡾ࠰ࡾࡸࡪࡹࡴࡠࡪࡲࡳࡰࡥࡳࡵࡣࡷࡩࢂࠦࡩ࡯ࡵࡷࡥࡳࡩࡥ࠾ࠤᇀ") + str(instance.ref()) + bstack11ll1_opy_ (u"ࠤࠥᇁ"))
        except Exception as e:
            self.logger.error(e)
            traceback.print_exc()
        self.bstack1ll1ll11lll_opy_(instance, (test_framework_state, test_hook_state), *args, **kwargs)
        try:
            if instance!= None and test_framework_state in bstack1ll1l1lllll_opy_.bstack1ll1ll11ll1_opy_ and test_hook_state == bstack1lll1111l11_opy_.POST:
                name = str(EVENTS.bstack11l1llllll_opy_.name)+bstack11ll1_opy_ (u"ࠥ࠾ࠧᇂ")+str(test_framework_state.name)
                bstack1lll1l1ll11_opy_ = TestFramework.bstack1ll1ll1l1ll_opy_(instance, name)
                bstack1lll111111l_opy_.end(EVENTS.bstack11l1llllll_opy_.value, bstack1lll1l1ll11_opy_+bstack11ll1_opy_ (u"ࠦ࠿ࡹࡴࡢࡴࡷࠦᇃ"), bstack1lll1l1ll11_opy_+bstack11ll1_opy_ (u"ࠧࡀࡥ࡯ࡦࠥᇄ"), True, None, test_framework_state.name)
        except Exception as e:
            self.logger.debug(bstack11ll1_opy_ (u"ࠨࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢ࡬ࡲࠥ࡮࡯ࡰ࡭ࠣࡩࡷࡸ࡯ࡳ࠼ࠣࡿࢂࠨᇅ").format(e))
    def bstack1lllll11111_opy_(self):
        return self.bstack1llll11ll1l_opy_
    def __1llll111111_opy_(self, *args):
        if len(args) > 2 and callable(getattr(args[2], bstack11ll1_opy_ (u"ࠢࡨࡧࡷࡣࡷ࡫ࡳࡶ࡮ࡷࠦᇆ"), None)):
            rep = args[2].get_result()
            if rep:
                return TestFramework.bstack1ll1lllll11_opy_(rep, [bstack11ll1_opy_ (u"ࠣࡹ࡫ࡩࡳࠨᇇ"), bstack11ll1_opy_ (u"ࠤࡲࡹࡹࡩ࡯࡮ࡧࠥᇈ"), bstack11ll1_opy_ (u"ࠥࡴࡦࡹࡳࡦࡦࠥᇉ"), bstack11ll1_opy_ (u"ࠦ࡫ࡧࡩ࡭ࡧࡧࠦᇊ"), bstack11ll1_opy_ (u"ࠧࡹ࡫ࡪࡲࡳࡩࡩࠨᇋ"), bstack11ll1_opy_ (u"ࠨ࡬ࡰࡰࡪࡶࡪࡶࡲࡵࡧࡻࡸࠧᇌ")])
        return None
    def __1llll1ll11l_opy_(self, instance: bstack1lll1l11l11_opy_, *args):
        result = self.__1llll111111_opy_(*args)
        if not result:
            return
        failure = None
        bstack1lllll1ll11_opy_ = None
        if result.get(bstack11ll1_opy_ (u"ࠢࡰࡷࡷࡧࡴࡳࡥࠣᇍ"), None) == bstack11ll1_opy_ (u"ࠣࡨࡤ࡭ࡱ࡫ࡤࠣᇎ") and len(args) > 1 and getattr(args[1], bstack11ll1_opy_ (u"ࠤࡨࡼࡨ࡯࡮ࡧࡱࠥᇏ"), None) is not None:
            failure = [{bstack11ll1_opy_ (u"ࠪࡦࡦࡩ࡫ࡵࡴࡤࡧࡪ࠭ᇐ"): [args[1].excinfo.exconly(), result.get(bstack11ll1_opy_ (u"ࠦࡱࡵ࡮ࡨࡴࡨࡴࡷࡺࡥࡹࡶࠥᇑ"), None)]}]
            bstack1lllll1ll11_opy_ = bstack11ll1_opy_ (u"ࠧࡇࡳࡴࡧࡵࡸ࡮ࡵ࡮ࡆࡴࡵࡳࡷࠨᇒ") if bstack11ll1_opy_ (u"ࠨࡁࡴࡵࡨࡶࡹ࡯࡯࡯ࠤᇓ") in getattr(args[1].excinfo, bstack11ll1_opy_ (u"ࠢࡵࡻࡳࡩࡳࡧ࡭ࡦࠤᇔ"), bstack11ll1_opy_ (u"ࠣࠤᇕ")) else bstack11ll1_opy_ (u"ࠤࡘࡲ࡭ࡧ࡮ࡥ࡮ࡨࡨࡊࡸࡲࡰࡴࠥᇖ")
        bstack1llll1l1ll1_opy_ = result.get(bstack11ll1_opy_ (u"ࠥࡳࡺࡺࡣࡰ࡯ࡨࠦᇗ"), TestFramework.bstack1lll1l11l1l_opy_)
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
            target = None # bstack1lll1l1lll1_opy_ bstack1lllll11l1l_opy_ this to be bstack11ll1_opy_ (u"ࠦࡳࡵࡤࡦ࡫ࡧࠦᇘ")
            if test_framework_state == bstack1llll1ll111_opy_.INIT_TEST:
                target = args[0] if isinstance(args[0], str) else None
                if target:
                    self.__1lllll111l1_opy_(context, test_framework_state, target, *args)
            elif test_framework_state == bstack1llll1ll111_opy_.LOG:
                nodeid = getattr(getattr(args[0], bstack11ll1_opy_ (u"ࠧࡴ࡯ࡥࡧࠥᇙ"), None), bstack11ll1_opy_ (u"ࠨ࡮ࡰࡦࡨ࡭ࡩࠨᇚ"), None) if args else None
                if isinstance(nodeid, str):
                    target = nodeid
            elif getattr(args[0], bstack11ll1_opy_ (u"ࠢ࡯ࡱࡧࡩ࡮ࡪࠢᇛ"), None):
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
        bstack1ll1lll1ll1_opy_ = TestFramework.bstack1ll1llll11l_opy_(instance, bstack1ll1l1lllll_opy_.bstack1ll1llll1ll_opy_, {})
        if not key in bstack1ll1lll1ll1_opy_:
            bstack1ll1lll1ll1_opy_[key] = []
        bstack1ll1lll1lll_opy_ = TestFramework.bstack1ll1llll11l_opy_(instance, bstack1ll1l1lllll_opy_.bstack1lll11lll11_opy_, {})
        if not key in bstack1ll1lll1lll_opy_:
            bstack1ll1lll1lll_opy_[key] = []
        bstack1ll1ll1l111_opy_ = {
            bstack1ll1l1lllll_opy_.bstack1ll1llll1ll_opy_: bstack1ll1lll1ll1_opy_,
            bstack1ll1l1lllll_opy_.bstack1lll11lll11_opy_: bstack1ll1lll1lll_opy_,
        }
        if test_hook_state == bstack1lll1111l11_opy_.PRE:
            hook = {
                bstack11ll1_opy_ (u"ࠣ࡭ࡨࡽࠧᇜ"): key,
                TestFramework.bstack1llll1l1l1l_opy_: uuid4().__str__(),
                TestFramework.bstack1llll1111ll_opy_: TestFramework.bstack1ll1ll1l1l1_opy_,
                TestFramework.bstack1lll1ll1l1l_opy_: datetime.now(tz=timezone.utc),
                TestFramework.bstack1ll1llll111_opy_: [],
                TestFramework.bstack1ll1lll1l1l_opy_: args[1] if len(args) > 1 else bstack11ll1_opy_ (u"ࠩࠪᇝ"),
                TestFramework.bstack1lll1llll11_opy_: bstack1lll11l1lll_opy_.bstack1ll1llll1l1_opy_()
            }
            bstack1ll1lll1ll1_opy_[key].append(hook)
            bstack1ll1ll1l111_opy_[bstack1ll1l1lllll_opy_.bstack1lll111lll1_opy_] = key
        elif test_hook_state == bstack1lll1111l11_opy_.POST:
            bstack1lll11l11ll_opy_ = bstack1ll1lll1ll1_opy_.get(key, [])
            hook = bstack1lll11l11ll_opy_.pop() if bstack1lll11l11ll_opy_ else None
            if hook:
                result = self.__1llll111111_opy_(*args)
                if result:
                    bstack1lll1l111ll_opy_ = result.get(bstack11ll1_opy_ (u"ࠥࡳࡺࡺࡣࡰ࡯ࡨࠦᇞ"), TestFramework.bstack1ll1ll1l1l1_opy_)
                    if bstack1lll1l111ll_opy_ != TestFramework.bstack1ll1ll1l1l1_opy_:
                        hook[TestFramework.bstack1llll1111ll_opy_] = bstack1lll1l111ll_opy_
                hook[TestFramework.bstack1lll11l1ll1_opy_] = datetime.now(tz=timezone.utc)
                hook[TestFramework.bstack1lll1llll11_opy_]= bstack1lll11l1lll_opy_.bstack1ll1llll1l1_opy_()
                self.bstack1lll1ll11ll_opy_(hook)
                logs = hook.get(TestFramework.bstack1lll11l111l_opy_, [])
                if logs: self.bstack1lll1l11ll1_opy_(instance, logs)
                bstack1ll1lll1lll_opy_[key].append(hook)
                bstack1ll1ll1l111_opy_[bstack1ll1l1lllll_opy_.bstack1llll1lllll_opy_] = key
        TestFramework.bstack1lll11llll1_opy_(instance, bstack1ll1ll1l111_opy_)
        self.logger.debug(bstack11ll1_opy_ (u"ࠦࡹࡸࡡࡤ࡭ࡢ࡬ࡴࡵ࡫ࡠࡧࡹࡩࡳࡺ࠺ࠡࡶࡨࡷࡹࡥࡨࡰࡱ࡮ࡣࡸࡺࡡࡵࡧࡀࡿࡰ࡫ࡹࡾ࠰ࡾࡸࡪࡹࡴࡠࡪࡲࡳࡰࡥࡳࡵࡣࡷࡩࢂࠦࡨࡰࡱ࡮ࡷࡤࡹࡴࡢࡴࡷࡩࡩࡃࡻࡩࡱࡲ࡯ࡸࡥࡳࡵࡣࡵࡸࡪࡪࡽࠡࡪࡲࡳࡰࡹ࡟ࡧ࡫ࡱ࡭ࡸ࡮ࡥࡥ࠿ࠥᇟ") + str(bstack1ll1lll1lll_opy_) + bstack11ll1_opy_ (u"ࠧࠨᇠ"))
    def __1lll111l1ll_opy_(
        self,
        context: bstack1lll1l1ll1l_opy_,
        test_framework_state: bstack1llll1ll111_opy_,
        test_hook_state: bstack1lll1111l11_opy_,
        *args,
        **kwargs,
    ):
        fixturedef = TestFramework.bstack1ll1lllll11_opy_(args[0], [bstack11ll1_opy_ (u"ࠨࡳࡤࡱࡳࡩࠧᇡ"), bstack11ll1_opy_ (u"ࠢࡢࡴࡪࡲࡦࡳࡥࠣᇢ"), bstack11ll1_opy_ (u"ࠣࡲࡤࡶࡦࡳࡳࠣᇣ"), bstack11ll1_opy_ (u"ࠤ࡬ࡨࡸࠨᇤ"), bstack11ll1_opy_ (u"ࠥࡹࡳ࡯ࡴࡵࡧࡶࡸࠧᇥ"), bstack11ll1_opy_ (u"ࠦࡧࡧࡳࡦ࡫ࡧࠦᇦ")]) if len(args) > 0 else {}
        request = args[1] if len(args) > 1 else None
        scope = request.scope if hasattr(request, bstack11ll1_opy_ (u"ࠧࡹࡣࡰࡲࡨࠦᇧ")) else fixturedef.get(bstack11ll1_opy_ (u"ࠨࡳࡤࡱࡳࡩࠧᇨ"), None)
        fixturename = request.fixturename if hasattr(request, bstack11ll1_opy_ (u"ࠢࡧ࡫ࡻࡸࡺࡸࡥ࡯ࡣࡰࡩࠧᇩ")) else None
        node = request.node if hasattr(request, bstack11ll1_opy_ (u"ࠣࡰࡲࡨࡪࠨᇪ")) else None
        target = request.node.nodeid if hasattr(node, bstack11ll1_opy_ (u"ࠤࡱࡳࡩ࡫ࡩࡥࠤᇫ")) else None
        baseid = fixturedef.get(bstack11ll1_opy_ (u"ࠥࡦࡦࡹࡥࡪࡦࠥᇬ"), None) or bstack11ll1_opy_ (u"ࠦࠧᇭ")
        if (not target or len(baseid) > 0) and hasattr(request, bstack11ll1_opy_ (u"ࠧࡥࡰࡺࡨࡸࡲࡨ࡯ࡴࡦ࡯ࠥᇮ")):
            target = bstack1ll1l1lllll_opy_.__1lll1llll1l_opy_(request._pyfuncitem.location) if hasattr(request._pyfuncitem, bstack11ll1_opy_ (u"ࠨ࡬ࡰࡥࡤࡸ࡮ࡵ࡮ࠣᇯ")) else None
            if target and not TestFramework.bstack1ll1lllll1l_opy_(target):
                self.__1lllll111l1_opy_(context, test_framework_state, target, (target, request._pyfuncitem.location))
                node = request._pyfuncitem
                self.logger.debug(bstack11ll1_opy_ (u"ࠢࡵࡴࡤࡧࡰࡥࡦࡪࡺࡷࡹࡷ࡫࡟ࡦࡸࡨࡲࡹࡀࠠࡧࡣ࡯ࡰࡧࡧࡣ࡬ࠢࡷࡥࡷ࡭ࡥࡵ࠿ࡾࡸࡦࡸࡧࡦࡶࢀࠤ࡫࡯ࡸࡵࡷࡵࡩࡳࡧ࡭ࡦ࠿ࡾࡪ࡮ࡾࡴࡶࡴࡨࡲࡦࡳࡥࡾࠢࡱࡳࡩ࡫࠽ࡼࡰࡲࡨࡪࢃࠠࡦࡸࡨࡲࡹࡃࡻࡵࡧࡶࡸࡤ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡵࡷࡥࡹ࡫ࡽ࠯ࠤᇰ") + str(test_hook_state) + bstack11ll1_opy_ (u"ࠣࠤᇱ"))
        if not fixturedef or not scope or not target:
            self.logger.warning(bstack11ll1_opy_ (u"ࠤࡷࡶࡦࡩ࡫ࡠࡨ࡬ࡼࡹࡻࡲࡦࡡࡨࡺࡪࡴࡴ࠻ࠢࡸࡲ࡭ࡧ࡮ࡥ࡮ࡨࡨࠥ࡫ࡶࡦࡰࡷࡁࢀࡺࡥࡴࡶࡢࡪࡷࡧ࡭ࡦࡹࡲࡶࡰࡥࡳࡵࡣࡷࡩࢂ࠴ࡻࡵࡧࡶࡸࡤ࡮࡯ࡰ࡭ࡢࡷࡹࡧࡴࡦࡿࠣࡪ࡮ࡾࡴࡶࡴࡨࡨࡪ࡬࠽ࡼࡨ࡬ࡼࡹࡻࡲࡦࡦࡨࡪࢂࠦࡳࡤࡱࡳࡩࡂࢁࡳࡤࡱࡳࡩࢂࠦࡴࡢࡴࡪࡩࡹࡃࠢᇲ") + str(target) + bstack11ll1_opy_ (u"ࠥࠦᇳ"))
            return None
        instance = TestFramework.bstack1ll1lllll1l_opy_(target)
        if not instance:
            self.logger.warning(bstack11ll1_opy_ (u"ࠦࡹࡸࡡࡤ࡭ࡢࡪ࡮ࡾࡴࡶࡴࡨࡣࡪࡼࡥ࡯ࡶ࠽ࠤࡺࡴࡨࡢࡰࡧࡰࡪࡪࠠࡦࡸࡨࡲࡹࡃࡻࡵࡧࡶࡸࡤ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡵࡷࡥࡹ࡫ࡽ࠯ࡽࡷࡩࡸࡺ࡟ࡩࡱࡲ࡯ࡤࡹࡴࡢࡶࡨࢁࠥ࡬ࡩࡹࡶࡸࡶࡪࡴࡡ࡮ࡧࡀࡿ࡫࡯ࡸࡵࡷࡵࡩࡳࡧ࡭ࡦࡿࠣࡷࡨࡵࡰࡦ࠿ࡾࡷࡨࡵࡰࡦࡿࠣࡦࡦࡹࡥࡪࡦࡀࡿࡧࡧࡳࡦ࡫ࡧࢁࠥࡺࡡࡳࡩࡨࡸࡂࠨᇴ") + str(target) + bstack11ll1_opy_ (u"ࠧࠨᇵ"))
            return None
        bstack1lll111llll_opy_ = TestFramework.bstack1ll1llll11l_opy_(instance, bstack1ll1l1lllll_opy_.bstack1lllll11l11_opy_, {})
        if os.getenv(bstack11ll1_opy_ (u"ࠨࡓࡅࡍࡢࡇࡑࡏ࡟ࡇࡎࡄࡋࡤࡌࡉ࡙ࡖࡘࡖࡊ࡙ࠢᇶ"), bstack11ll1_opy_ (u"ࠢ࠲ࠤᇷ")) == bstack11ll1_opy_ (u"ࠣ࠳ࠥᇸ"):
            bstack1lllll1l111_opy_ = bstack11ll1_opy_ (u"ࠤ࠽ࠦᇹ").join((scope, fixturename))
            bstack1ll1llllll1_opy_ = datetime.now(tz=timezone.utc)
            bstack1lllll1l11l_opy_ = {
                bstack11ll1_opy_ (u"ࠥ࡯ࡪࡿࠢᇺ"): bstack1lllll1l111_opy_,
                bstack11ll1_opy_ (u"ࠦࡹࡧࡧࡴࠤᇻ"): bstack1ll1l1lllll_opy_.__1lll111l11l_opy_(request.node),
                bstack11ll1_opy_ (u"ࠧ࡬ࡩࡹࡶࡸࡶࡪࠨᇼ"): fixturedef,
                bstack11ll1_opy_ (u"ࠨࡳࡤࡱࡳࡩࠧᇽ"): scope,
                bstack11ll1_opy_ (u"ࠢࡵࡻࡳࡩࠧᇾ"): None,
            }
            try:
                if test_hook_state == bstack1lll1111l11_opy_.POST and callable(getattr(args[-1], bstack11ll1_opy_ (u"ࠣࡩࡨࡸࡤࡸࡥࡴࡷ࡯ࡸࠧᇿ"), None)):
                    bstack1lllll1l11l_opy_[bstack11ll1_opy_ (u"ࠤࡷࡽࡵ࡫ࠢሀ")] = TestFramework.bstack1lll1l1l111_opy_(args[-1].get_result())
            except Exception as e:
                pass
            if test_hook_state == bstack1lll1111l11_opy_.PRE:
                bstack1lllll1l11l_opy_[bstack11ll1_opy_ (u"ࠥࡹࡺ࡯ࡤࠣሁ")] = uuid4().__str__()
                bstack1lllll1l11l_opy_[bstack1ll1l1lllll_opy_.bstack1lll1ll1l1l_opy_] = bstack1ll1llllll1_opy_
            elif test_hook_state == bstack1lll1111l11_opy_.POST:
                bstack1lllll1l11l_opy_[bstack1ll1l1lllll_opy_.bstack1lll11l1ll1_opy_] = bstack1ll1llllll1_opy_
            if bstack1lllll1l111_opy_ in bstack1lll111llll_opy_:
                bstack1lll111llll_opy_[bstack1lllll1l111_opy_].update(bstack1lllll1l11l_opy_)
                self.logger.debug(bstack11ll1_opy_ (u"ࠦࡺࡶࡤࡢࡶࡨࡨࠥ࡬ࡩࡹࡶࡸࡶࡪࡴࡡ࡮ࡧࡀࡿ࡫࡯ࡸࡵࡷࡵࡩࡳࡧ࡭ࡦࡿࠣࡷࡨࡵࡰࡦ࠿ࡾࡷࡨࡵࡰࡦࡿࠣࡪ࡮ࡾࡴࡶࡴࡨࡁࠧሂ") + str(bstack1lll111llll_opy_[bstack1lllll1l111_opy_]) + bstack11ll1_opy_ (u"ࠧࠨሃ"))
            else:
                bstack1lll111llll_opy_[bstack1lllll1l111_opy_] = bstack1lllll1l11l_opy_
                self.logger.debug(bstack11ll1_opy_ (u"ࠨࡳࡢࡸࡨࡨࠥ࡬ࡩࡹࡶࡸࡶࡪࡴࡡ࡮ࡧࡀࡿ࡫࡯ࡸࡵࡷࡵࡩࡳࡧ࡭ࡦࡿࠣࡷࡨࡵࡰࡦ࠿ࡾࡷࡨࡵࡰࡦࡿࠣࡪ࡮ࡾࡴࡶࡴࡨࡁࢀࡺࡥࡴࡶࡢࡪ࡮ࡾࡴࡶࡴࡨࢁࠥࡺࡲࡢࡥ࡮ࡩࡩࡥࡦࡪࡺࡷࡹࡷ࡫ࡳ࠾ࠤሄ") + str(len(bstack1lll111llll_opy_)) + bstack11ll1_opy_ (u"ࠢࠣህ"))
        TestFramework.bstack1lll111ll11_opy_(instance, bstack1ll1l1lllll_opy_.bstack1lllll11l11_opy_, bstack1lll111llll_opy_)
        self.logger.debug(bstack11ll1_opy_ (u"ࠣࡵࡤࡺࡪࡪࠠࡧ࡫ࡻࡸࡺࡸࡥࡴ࠿ࡾࡰࡪࡴࠨࡵࡴࡤࡧࡰ࡫ࡤࡠࡨ࡬ࡼࡹࡻࡲࡦࡵࠬࢁࠥ࡯࡮ࡴࡶࡤࡲࡨ࡫࠽ࠣሆ") + str(instance.ref()) + bstack11ll1_opy_ (u"ࠤࠥሇ"))
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
            bstack1ll1l1lllll_opy_.bstack1lllll11l11_opy_: {},
            bstack1ll1l1lllll_opy_.bstack1lll11lll11_opy_: {},
            bstack1ll1l1lllll_opy_.bstack1ll1llll1ll_opy_: {},
        })
        if len(args) > 1 and isinstance(args[1], tuple):
            TestFramework.bstack1lll111ll11_opy_(ob, TestFramework.bstack1lll11lllll_opy_, str(args[1][0]))
        if context.platform_index >= 0:
            TestFramework.bstack1lll111ll11_opy_(ob, TestFramework.bstack1lll11l1l1l_opy_, context.platform_index)
        TestFramework.bstack1lll1llllll_opy_[ctx.id] = ob
        self.logger.debug(bstack11ll1_opy_ (u"ࠥࡷࡦࡼࡥࡥࠢ࡬ࡲࡸࡺࡡ࡯ࡥࡨࠤࡨࡺࡸ࠯࡫ࡧࡁࢀࡩࡴࡹ࠰࡬ࡨࢂࠦࡴࡢࡴࡪࡩࡹࡃࡻࡵࡣࡵ࡫ࡪࡺࡽࠡࡣࡵ࡫ࡸࡃࡻࡢࡴࡪࡷࢂࠦࡩ࡯ࡵࡷࡥࡳࡩࡥࡴ࠿ࠥለ") + str(TestFramework.bstack1lll1llllll_opy_.keys()) + bstack11ll1_opy_ (u"ࠦࠧሉ"))
        return ob
    def bstack1lll1lll11l_opy_(self, instance: bstack1lll1l11l11_opy_, bstack1lll1lll111_opy_: Tuple[bstack1llll1ll111_opy_, bstack1lll1111l11_opy_]):
        bstack1llll11llll_opy_ = (
            bstack1ll1l1lllll_opy_.bstack1lll111lll1_opy_
            if bstack1lll1lll111_opy_[1] == bstack1lll1111l11_opy_.PRE
            else bstack1ll1l1lllll_opy_.bstack1llll1lllll_opy_
        )
        hook = bstack1ll1l1lllll_opy_.bstack1lll1l11lll_opy_(instance, bstack1llll11llll_opy_)
        entries = hook.get(TestFramework.bstack1ll1llll111_opy_, []) if isinstance(hook, dict) else []
        entries.extend(TestFramework.bstack1ll1llll11l_opy_(instance, TestFramework.bstack1llll11l111_opy_, []))
        return entries
    def bstack1lll11l1l11_opy_(self, instance: bstack1lll1l11l11_opy_, bstack1lll1lll111_opy_: Tuple[bstack1llll1ll111_opy_, bstack1lll1111l11_opy_]):
        bstack1llll11llll_opy_ = (
            bstack1ll1l1lllll_opy_.bstack1lll111lll1_opy_
            if bstack1lll1lll111_opy_[1] == bstack1lll1111l11_opy_.PRE
            else bstack1ll1l1lllll_opy_.bstack1llll1lllll_opy_
        )
        bstack1ll1l1lllll_opy_.bstack1ll1lll111l_opy_(instance, bstack1llll11llll_opy_)
        TestFramework.bstack1ll1llll11l_opy_(instance, TestFramework.bstack1llll11l111_opy_, []).clear()
    def bstack1lll1ll11ll_opy_(self, hook: Dict[str, Any]) -> None:
        bstack11ll1_opy_ (u"ࠧࠨࠢࠋࠢࠣࠤࠥࠦࠠࠡࠢࡓࡶࡴࡩࡥࡴࡵࡨࡷࠥࡺࡨࡦࠢࡋࡳࡴࡱࡌࡦࡸࡨࡰࠥࡧࡴࡵࡣࡦ࡬ࡲ࡫࡮ࡵࡵࠣࡷ࡮ࡳࡩ࡭ࡣࡵࠤࡹࡵࠠࡵࡪࡨࠤࡏࡧࡶࡢࠢ࡬ࡱࡵࡲࡥ࡮ࡧࡱࡸࡦࡺࡩࡰࡰ࠱ࠎࠥࠦࠠࠡࠢࠣࠤ࡚ࠥࡨࡪࡵࠣࡱࡪࡺࡨࡰࡦ࠽ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠ࠮ࠢࡆ࡬ࡪࡩ࡫ࡴࠢࡷ࡬ࡪࠦࡈࡰࡱ࡮ࡐࡪࡼࡥ࡭ࠢࡧ࡭ࡷ࡫ࡣࡵࡱࡵࡽࠥ࡯࡮ࡴ࡫ࡧࡩࠥࢄ࠯࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠯ࡖࡲ࡯ࡳࡦࡪࡥࡥࡃࡷࡸࡦࡩࡨ࡮ࡧࡱࡸࡸ࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣ࠱ࠥࡌ࡯ࡳࠢࡨࡥࡨ࡮ࠠࡧ࡫࡯ࡩࠥ࡯࡮ࠡࡪࡲࡳࡰࡥ࡬ࡦࡸࡨࡰࡤ࡬ࡩ࡭ࡧࡶ࠰ࠥࡸࡥࡱ࡮ࡤࡧࡪࡹࠠࠣࡖࡨࡷࡹࡒࡥࡷࡧ࡯ࠦࠥࡽࡩࡵࡪࠣࠦࡍࡵ࡯࡬ࡎࡨࡺࡪࡲࠢࠡ࡫ࡱࠤ࡮ࡺࡳࠡࡲࡤࡸ࡭࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣ࠱ࠥࡏࡦࠡࡣࠣࡪ࡮ࡲࡥࠡ࡫ࡱࠤࡹ࡮ࡥࠡࡦ࡬ࡶࡪࡩࡴࡰࡴࡼࠤࡲࡧࡴࡤࡪࡨࡷࠥࡧࠠ࡮ࡱࡧ࡭࡫࡯ࡥࡥࠢ࡫ࡳࡴࡱ࠭࡭ࡧࡹࡩࡱࠦࡦࡪ࡮ࡨ࠰ࠥ࡯ࡴࠡࡥࡵࡩࡦࡺࡥࡴࠢࡤࠤࡑࡵࡧࡆࡰࡷࡶࡾࠦ࡯ࡣ࡬ࡨࡧࡹࠦࡷࡪࡶ࡫ࠤࡦࡺࡴࡢࡥ࡫ࡱࡪࡴࡴࠡࡦࡨࡸࡦ࡯࡬ࡴ࠰ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦ࠭ࠡࡕ࡬ࡱ࡮ࡲࡡࡳ࡮ࡼ࠰ࠥ࡯ࡴࠡࡲࡵࡳࡨ࡫ࡳࡴࡧࡶࠤࡇࡻࡩ࡭ࡦࡏࡩࡻ࡫࡬ࠡࡣࡷࡸࡦࡩࡨ࡮ࡧࡱࡸࡸࠦ࡬ࡰࡥࡤࡸࡪࡪࠠࡪࡰࠣࡌࡴࡵ࡫ࡍࡧࡹࡩࡱ࠵ࡂࡶ࡫࡯ࡨࡑ࡫ࡶࡦ࡮ࡋࡳࡴࡱࡅࡷࡧࡱࡸࠥࡨࡹࠡࡴࡨࡴࡱࡧࡣࡪࡰࡪࠤࠧࡈࡵࡪ࡮ࡧࡐࡪࡼࡥ࡭ࠤࠣࡻ࡮ࡺࡨࠡࠤࡋࡳࡴࡱࡌࡦࡸࡨࡰ࠴ࡈࡵࡪ࡮ࡧࡐࡪࡼࡥ࡭ࡊࡲࡳࡰࡋࡶࡦࡰࡷࠦ࠳ࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢ࠰ࠤ࡙࡮ࡥࠡࡥࡵࡩࡦࡺࡥࡥࠢࡏࡳ࡬ࡋ࡮ࡵࡴࡼࠤࡴࡨࡪࡦࡥࡷࡷࠥࡧࡲࡦࠢࡤࡨࡩ࡫ࡤࠡࡶࡲࠤࡹ࡮ࡥࠡࡪࡲࡳࡰ࠭ࡳࠡࠤ࡯ࡳ࡬ࡹࠢࠡ࡮࡬ࡷࡹ࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࡃࡵ࡫ࡸࡀࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥ࡮࡯ࡰ࡭࠽ࠤ࡙࡮ࡥࠡࡧࡹࡩࡳࡺࠠࡥ࡫ࡦࡸ࡮ࡵ࡮ࡢࡴࡼࠤࡨࡵ࡮ࡵࡣ࡬ࡲ࡮ࡴࡧࠡࡧࡻ࡭ࡸࡺࡩ࡯ࡩࠣࡰࡴ࡭ࡳࠡࡣࡱࡨࠥ࡮࡯ࡰ࡭ࠣ࡭ࡳ࡬࡯ࡳ࡯ࡤࡸ࡮ࡵ࡮࠯ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࡩࡱࡲ࡯ࡤࡲࡥࡷࡧ࡯ࡣ࡫࡯࡬ࡦࡵ࠽ࠤࡑ࡯ࡳࡵࠢࡲࡪࠥࡖࡡࡵࡪࠣࡳࡧࡰࡥࡤࡶࡶࠤ࡫ࡸ࡯࡮ࠢࡷ࡬ࡪࠦࡔࡦࡵࡷࡐࡪࡼࡥ࡭ࠢࡰࡳࡳ࡯ࡴࡰࡴ࡬ࡲ࡬࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࡨࡵࡪ࡮ࡧࡣࡱ࡫ࡶࡦ࡮ࡢࡪ࡮ࡲࡥࡴ࠼ࠣࡐ࡮ࡹࡴࠡࡱࡩࠤࡕࡧࡴࡩࠢࡲࡦ࡯࡫ࡣࡵࡵࠣࡪࡷࡵ࡭ࠡࡶ࡫ࡩࠥࡈࡵࡪ࡮ࡧࡐࡪࡼࡥ࡭ࠢࡰࡳࡳ࡯ࡴࡰࡴ࡬ࡲ࡬࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࠤࠥࠦሊ")
        global _1lll111l1l1_opy_
        platform_index = os.environ[bstack11ll1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡖࡌࡂࡖࡉࡓࡗࡓ࡟ࡊࡐࡇࡉ࡝࠭ላ")]
        bstack1llll1lll1l_opy_ = os.path.join(bstack1lll11lll1l_opy_, (bstack1ll1ll1l11l_opy_ + str(platform_index)), bstack1ll1l1llll1_opy_)
        if not os.path.exists(bstack1llll1lll1l_opy_) or not os.path.isdir(bstack1llll1lll1l_opy_):
            self.logger.debug(bstack11ll1_opy_ (u"ࠢࡅ࡫ࡵࡩࡨࡺ࡯ࡳࡻࠣࡨࡴ࡫ࡳࠡࡰࡲࡸࠥ࡫ࡸࡪࡵࡷࡷࠥࡺ࡯ࠡࡲࡵࡳࡨ࡫ࡳࡴࠢࡾࢁࠧሌ").format(bstack1llll1lll1l_opy_))
            return
        logs = hook.get(bstack11ll1_opy_ (u"ࠣ࡮ࡲ࡫ࡸࠨል"), [])
        with os.scandir(bstack1llll1lll1l_opy_) as entries:
            for entry in entries:
                abs_path = os.path.abspath(entry.path)
                if abs_path in _1lll111l1l1_opy_:
                    self.logger.info(bstack11ll1_opy_ (u"ࠤࡓࡥࡹ࡮ࠠࡢ࡮ࡵࡩࡦࡪࡹࠡࡲࡵࡳࡨ࡫ࡳࡴࡧࡧࠤࢀࢃࠢሎ").format(abs_path))
                    continue
                if entry.is_file():
                    try:
                        timestamp = datetime.fromtimestamp(entry.stat().st_mtime, tz=timezone.utc).isoformat()
                    except Exception:
                        timestamp = bstack11ll1_opy_ (u"ࠥࠦሏ")
                    log_entry = bstack1lll1ll1lll_opy_(
                        kind=bstack11ll1_opy_ (u"࡙ࠦࡋࡓࡕࡡࡄࡘ࡙ࡇࡃࡉࡏࡈࡒ࡙ࠨሐ"),
                        message=bstack11ll1_opy_ (u"ࠧࠨሑ"),
                        level=bstack11ll1_opy_ (u"ࠨࠢሒ"),
                        timestamp=timestamp,
                        fileName=entry.name,
                        bstack1llll1lll11_opy_=entry.stat().st_size,
                        bstack1lll1111l1l_opy_=bstack11ll1_opy_ (u"ࠢࡎࡃࡑ࡙ࡆࡒ࡟ࡖࡒࡏࡓࡆࡊࠢሓ"),
                        bstack1ll11l_opy_=os.path.abspath(entry.path),
                        bstack1lll111l111_opy_=hook.get(TestFramework.bstack1llll1l1l1l_opy_)
                    )
                    logs.append(log_entry)
                    _1lll111l1l1_opy_.add(abs_path)
        platform_index = os.environ[bstack11ll1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡑࡎࡄࡘࡋࡕࡒࡎࡡࡌࡒࡉࡋࡘࠨሔ")]
        bstack1lll1ll1l11_opy_ = os.path.join(bstack1lll11lll1l_opy_, (bstack1ll1ll1l11l_opy_ + str(platform_index)), bstack1ll1l1llll1_opy_, bstack1ll1ll11l11_opy_)
        if not os.path.exists(bstack1lll1ll1l11_opy_) or not os.path.isdir(bstack1lll1ll1l11_opy_):
            self.logger.info(bstack11ll1_opy_ (u"ࠤࡑࡳࠥࡈࡵࡪ࡮ࡧࡐࡪࡼࡥ࡭ࡊࡲࡳࡰࡋࡶࡦࡰࡷࠤࡦࡺࡴࡢࡥ࡫ࡱࡪࡴࡴࡴࠢࡧ࡭ࡷ࡫ࡣࡵࡱࡵࡽࠥ࡬࡯ࡶࡰࡧࠤࡦࡺ࠺ࠡࡽࢀࠦሕ").format(bstack1lll1ll1l11_opy_))
        else:
            self.logger.info(bstack11ll1_opy_ (u"ࠥࡔࡷࡵࡣࡦࡵࡶ࡭ࡳ࡭ࠠࡃࡷ࡬ࡰࡩࡒࡥࡷࡧ࡯ࡌࡴࡵ࡫ࡆࡸࡨࡲࡹࠦࡡࡵࡶࡤࡧ࡭ࡳࡥ࡯ࡶࡶࠤ࡫ࡸ࡯࡮ࠢࡧ࡭ࡷ࡫ࡣࡵࡱࡵࡽ࠿ࠦࡻࡾࠤሖ").format(bstack1lll1ll1l11_opy_))
            with os.scandir(bstack1lll1ll1l11_opy_) as entries:
                for entry in entries:
                    abs_path = os.path.abspath(entry.path)
                    if abs_path in _1lll111l1l1_opy_:
                        self.logger.info(bstack11ll1_opy_ (u"ࠦࡕࡧࡴࡩࠢࡤࡰࡷ࡫ࡡࡥࡻࠣࡴࡷࡵࡣࡦࡵࡶࡩࡩࠦࡻࡾࠤሗ").format(abs_path))
                        continue
                    if entry.is_file():
                        try:
                            timestamp = datetime.fromtimestamp(entry.stat().st_mtime, tz=timezone.utc).isoformat()
                        except Exception:
                            timestamp = bstack11ll1_opy_ (u"ࠧࠨመ")
                        log_entry = bstack1lll1ll1lll_opy_(
                            kind=bstack11ll1_opy_ (u"ࠨࡔࡆࡕࡗࡣࡆ࡚ࡔࡂࡅࡋࡑࡊࡔࡔࠣሙ"),
                            message=bstack11ll1_opy_ (u"ࠢࠣሚ"),
                            level=bstack11ll1_opy_ (u"ࠣࡄࡸ࡭ࡱࡪࡌࡦࡸࡨࡰࠧማ"),
                            timestamp=timestamp,
                            fileName=entry.name,
                            bstack1llll1lll11_opy_=entry.stat().st_size,
                            bstack1lll1111l1l_opy_=bstack11ll1_opy_ (u"ࠤࡐࡅࡓ࡛ࡁࡍࡡࡘࡔࡑࡕࡁࡅࠤሜ"),
                            bstack1ll11l_opy_=os.path.abspath(entry.path),
                            bstack1lllll111ll_opy_=hook.get(TestFramework.bstack1llll1l1l1l_opy_)
                        )
                        logs.append(log_entry)
                        _1lll111l1l1_opy_.add(abs_path)
        hook[bstack11ll1_opy_ (u"ࠥࡰࡴ࡭ࡳࠣም")] = logs
    def bstack1lll1l11ll1_opy_(
        self,
        bstack1ll1lll11l1_opy_: bstack1lll1l11l11_opy_,
        entries: List[bstack1lll1ll1lll_opy_],
    ):
        req = structs.LogCreatedEventRequest()
        req.bin_session_id = os.environ.get(bstack11ll1_opy_ (u"ࠦࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡇࡑࡏ࡟ࡃࡋࡑࡣࡘࡋࡓࡔࡋࡒࡒࡤࡏࡄࠣሞ"))
        req.platform_index = TestFramework.bstack1ll1llll11l_opy_(bstack1ll1lll11l1_opy_, TestFramework.bstack1lll11l1l1l_opy_)
        req.execution_context.hash = str(bstack1ll1lll11l1_opy_.context.hash)
        req.execution_context.thread_id = str(bstack1ll1lll11l1_opy_.context.thread_id)
        req.execution_context.process_id = str(bstack1ll1lll11l1_opy_.context.process_id)
        for entry in entries:
            log_entry = req.logs.add()
            log_entry.test_framework_name = TestFramework.bstack1ll1llll11l_opy_(bstack1ll1lll11l1_opy_, TestFramework.bstack1lll1111111_opy_)
            log_entry.test_framework_version = TestFramework.bstack1ll1llll11l_opy_(bstack1ll1lll11l1_opy_, TestFramework.bstack1lll11111ll_opy_)
            log_entry.uuid = entry.bstack1lll111l111_opy_
            log_entry.test_framework_state = bstack1ll1lll11l1_opy_.state.name
            log_entry.message = entry.message.encode(bstack11ll1_opy_ (u"ࠧࡻࡴࡧ࠯࠻ࠦሟ"))
            log_entry.kind = entry.kind
            log_entry.timestamp = (
                entry.timestamp.isoformat()
                if isinstance(entry.timestamp, datetime)
                else datetime.now(tz=timezone.utc).isoformat()
            )
            log_entry.level = bstack11ll1_opy_ (u"ࠨࠢሠ")
            if entry.kind == bstack11ll1_opy_ (u"ࠢࡕࡇࡖࡘࡤࡇࡔࡕࡃࡆࡌࡒࡋࡎࡕࠤሡ"):
                log_entry.file_name = entry.fileName
                log_entry.file_size = entry.bstack1llll1lll11_opy_
                log_entry.file_path = entry.bstack1ll11l_opy_
        def bstack1llll1ll1l1_opy_():
            bstack1ll11l1l1l_opy_ = datetime.now()
            try:
                self.bstack1lllll11ll1_opy_.LogCreatedEvent(req)
                bstack1ll1lll11l1_opy_.bstack1lll1lll1_opy_(bstack11ll1_opy_ (u"ࠣࡩࡵࡴࡨࡀࡳࡦࡰࡧࡣࡱࡵࡧࡠࡥࡵࡩࡦࡺࡥࡥࡡࡨࡺࡪࡴࡴࡠࡣࡷࡸࡦࡩࡨ࡮ࡧࡱࡸࠧሢ"), datetime.now() - bstack1ll11l1l1l_opy_)
            except grpc.RpcError as e:
                self.log_error(bstack11ll1_opy_ (u"ࠤࡵࡴࡨ࠳ࡥࡳࡴࡲࡶ࠿ࠦࡳࡦࡰࡧࡣࡱࡵࡧࡠࡥࡵࡩࡦࡺࡥࡥࡡࡨࡺࡪࡴࡴࡠࡣࡷࡸࡦࡩࡨ࡮ࡧࡱࡸࠥࢁࡽࠣሣ").format(str(e)))
                traceback.print_exc()
        self.bstack1lll1l1llll_opy_.enqueue(bstack1llll1ll1l1_opy_)
    def __1ll1lll11ll_opy_(self, instance) -> None:
        bstack11ll1_opy_ (u"ࠥࠦࠧࠐࠠࠡࠢࠣࠤࠥࠦࠠࡍࡱࡤࡨࡸࠦࡣࡶࡵࡷࡳࡲࠦࡴࡢࡩࡶࠤ࡫ࡵࡲࠡࡶ࡫ࡩࠥ࡭ࡩࡷࡧࡱࠤࡹ࡫ࡳࡵࠢࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࠥ࡯࡮ࡴࡶࡤࡲࡨ࡫࠮ࠋࠢࠣࠤࠥࠦࠠࠡࠢࡆࡶࡪࡧࡴࡦࡵࠣࡥࠥࡪࡩࡤࡶࠣࡧࡴࡴࡴࡢ࡫ࡱ࡭ࡳ࡭ࠠࡵࡧࡶࡸࠥࡲࡥࡷࡧ࡯ࠤࡨࡻࡳࡵࡱࡰࠤࡲ࡫ࡴࡢࡦࡤࡸࡦࠦࡲࡦࡶࡵ࡭ࡪࡼࡥࡥࠢࡩࡶࡴࡳࠊࠡࠢࠣࠤࠥࠦࠠࠡࡅࡸࡷࡹࡵ࡭ࡕࡣࡪࡑࡦࡴࡡࡨࡧࡵࠤࡦࡴࡤࠡࡷࡳࡨࡦࡺࡥࡴࠢࡷ࡬ࡪࠦࡩ࡯ࡵࡷࡥࡳࡩࡥࠡࡵࡷࡥࡹ࡫ࠠࡶࡵ࡬ࡲ࡬ࠦࡳࡦࡶࡢࡷࡹࡧࡴࡦࡡࡨࡲࡹࡸࡩࡦࡵ࠱ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠨࠢࠣሤ")
        bstack1ll1ll1l111_opy_ = {bstack11ll1_opy_ (u"ࠦࡨࡻࡳࡵࡱࡰࡣࡲ࡫ࡴࡢࡦࡤࡸࡦࠨሥ"): bstack1lll11l1lll_opy_.bstack1ll1llll1l1_opy_()}
        from browserstack_sdk.sdk_cli.test_framework import TestFramework
        TestFramework.bstack1lll11llll1_opy_(instance, bstack1ll1ll1l111_opy_)
    @staticmethod
    def bstack1lll1l11lll_opy_(instance: bstack1lll1l11l11_opy_, bstack1llll11llll_opy_: str):
        bstack1ll1lll1111_opy_ = (
            bstack1ll1l1lllll_opy_.bstack1lll11lll11_opy_
            if bstack1llll11llll_opy_ == bstack1ll1l1lllll_opy_.bstack1llll1lllll_opy_
            else bstack1ll1l1lllll_opy_.bstack1ll1llll1ll_opy_
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
        hook = bstack1ll1l1lllll_opy_.bstack1lll1l11lll_opy_(instance, bstack1llll11llll_opy_)
        if isinstance(hook, dict):
            hook.get(TestFramework.bstack1ll1llll111_opy_, []).clear()
    @staticmethod
    def __1llll1ll1ll_opy_(instance: bstack1lll1l11l11_opy_, *args):
        if len(args) < 2 or not callable(getattr(args[1], bstack11ll1_opy_ (u"ࠧ࡭ࡥࡵࡡࡵࡩࡨࡵࡲࡥࡵࠥሦ"), None)):
            return
        if os.getenv(bstack11ll1_opy_ (u"ࠨࡓࡅࡍࡢࡇࡑࡏ࡟ࡇࡎࡄࡋࡤࡒࡏࡈࡕࠥሧ"), bstack11ll1_opy_ (u"ࠢ࠲ࠤረ")) != bstack11ll1_opy_ (u"ࠣ࠳ࠥሩ"):
            bstack1ll1l1lllll_opy_.logger.warning(bstack11ll1_opy_ (u"ࠤ࡬࡫ࡳࡵࡲࡪࡰࡪࠤࡨࡧࡰ࡭ࡱࡪࠦሪ"))
            return
        bstack1llll11l1ll_opy_ = {
            bstack11ll1_opy_ (u"ࠥࡷࡪࡺࡵࡱࠤራ"): (bstack1ll1l1lllll_opy_.bstack1lll111lll1_opy_, bstack1ll1l1lllll_opy_.bstack1ll1llll1ll_opy_),
            bstack11ll1_opy_ (u"ࠦࡹ࡫ࡡࡳࡦࡲࡻࡳࠨሬ"): (bstack1ll1l1lllll_opy_.bstack1llll1lllll_opy_, bstack1ll1l1lllll_opy_.bstack1lll11lll11_opy_),
        }
        for when in (bstack11ll1_opy_ (u"ࠧࡹࡥࡵࡷࡳࠦር"), bstack11ll1_opy_ (u"ࠨࡣࡢ࡮࡯ࠦሮ"), bstack11ll1_opy_ (u"ࠢࡵࡧࡤࡶࡩࡵࡷ࡯ࠤሯ")):
            bstack1lll1lll1l1_opy_ = args[1].get_records(when)
            if not bstack1lll1lll1l1_opy_:
                continue
            records = [
                bstack1lll1ll1lll_opy_(
                    kind=TestFramework.bstack1lll1l111l1_opy_,
                    message=r.message,
                    level=r.levelname if hasattr(r, bstack11ll1_opy_ (u"ࠣ࡮ࡨࡺࡪࡲ࡮ࡢ࡯ࡨࠦሰ")) and r.levelname else None,
                    timestamp=(
                        datetime.fromtimestamp(r.created, tz=timezone.utc)
                        if hasattr(r, bstack11ll1_opy_ (u"ࠤࡦࡶࡪࡧࡴࡦࡦࠥሱ")) and r.created
                        else None
                    ),
                )
                for r in bstack1lll1lll1l1_opy_
                if isinstance(getattr(r, bstack11ll1_opy_ (u"ࠥࡱࡪࡹࡳࡢࡩࡨࠦሲ"), None), str) and r.message.strip()
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
    def __1ll1ll1ll11_opy_(test) -> Dict[str, Any]:
        bstack1l1l11l111_opy_ = bstack1ll1l1lllll_opy_.__1lll1llll1l_opy_(test.location) if hasattr(test, bstack11ll1_opy_ (u"ࠦࡱࡵࡣࡢࡶ࡬ࡳࡳࠨሳ")) else getattr(test, bstack11ll1_opy_ (u"ࠧࡴ࡯ࡥࡧ࡬ࡨࠧሴ"), None)
        test_name = test.name if hasattr(test, bstack11ll1_opy_ (u"ࠨ࡮ࡢ࡯ࡨࠦስ")) else None
        bstack1lll11ll1ll_opy_ = test.fspath.strpath if hasattr(test, bstack11ll1_opy_ (u"ࠢࡧࡵࡳࡥࡹ࡮ࠢሶ")) and test.fspath else None
        if not bstack1l1l11l111_opy_ or not test_name or not bstack1lll11ll1ll_opy_:
            return None
        code = None
        if hasattr(test, bstack11ll1_opy_ (u"ࠣࡱࡥ࡮ࠧሷ")):
            try:
                import inspect
                code = inspect.getsource(test.obj)
            except:
                pass
        bstack1ll1ll11l1l_opy_ = []
        try:
            bstack1ll1ll11l1l_opy_ = bstack1l11llll1l_opy_.bstack111l11l1l1_opy_(test)
        except:
            bstack1ll1l1lllll_opy_.logger.warning(bstack11ll1_opy_ (u"ࠤࡘࡲࡦࡨ࡬ࡦࠢࡷࡳࠥ࡬ࡩ࡯ࡦࠣࡸࡪࡹࡴࠡࡵࡦࡳࡵ࡫ࡳ࠭ࠢࡷࡩࡸࡺࠠࡴࡥࡲࡴࡪࡹࠠࡸ࡫࡯ࡰࠥࡨࡥࠡࡴࡨࡷࡴࡲࡶࡦࡦࠣ࡭ࡳࠦࡃࡍࡋࠥሸ"))
        return {
            TestFramework.bstack1llll111ll1_opy_: uuid4().__str__(),
            TestFramework.bstack1llll1l1111_opy_: bstack1l1l11l111_opy_,
            TestFramework.bstack1llll1l11ll_opy_: test_name,
            TestFramework.bstack1lll11111l1_opy_: getattr(test, bstack11ll1_opy_ (u"ࠥࡲࡴࡪࡥࡪࡦࠥሹ"), None),
            TestFramework.bstack1llll111lll_opy_: bstack1lll11ll1ll_opy_,
            TestFramework.bstack1lll11l1111_opy_: bstack1ll1l1lllll_opy_.__1lll111l11l_opy_(test),
            TestFramework.bstack1llll11111l_opy_: code,
            TestFramework.bstack1ll1ll1ll1l_opy_: TestFramework.bstack1lll1l11l1l_opy_,
            TestFramework.bstack1llll1l111l_opy_: bstack1l1l11l111_opy_,
            TestFramework.bstack1ll1ll111ll_opy_: bstack1ll1ll11l1l_opy_
        }
    @staticmethod
    def __1lll111l11l_opy_(test) -> List[str]:
        markers = []
        current = test
        while current:
            own_markers = getattr(current, bstack11ll1_opy_ (u"ࠦࡴࡽ࡮ࡠ࡯ࡤࡶࡰ࡫ࡲࡴࠤሺ"), [])
            markers.extend([getattr(m, bstack11ll1_opy_ (u"ࠧࡴࡡ࡮ࡧࠥሻ"), None) for m in own_markers if getattr(m, bstack11ll1_opy_ (u"ࠨ࡮ࡢ࡯ࡨࠦሼ"), None)])
            current = getattr(current, bstack11ll1_opy_ (u"ࠢࡱࡣࡵࡩࡳࡺࠢሽ"), None)
        return markers
    @staticmethod
    def __1lll1llll1l_opy_(location):
        return bstack11ll1_opy_ (u"ࠣ࠼࠽ࠦሾ").join(filter(lambda x: isinstance(x, str), location))