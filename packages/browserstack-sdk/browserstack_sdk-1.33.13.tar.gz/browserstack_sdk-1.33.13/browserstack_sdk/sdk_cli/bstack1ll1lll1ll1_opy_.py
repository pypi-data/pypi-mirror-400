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
from browserstack_sdk.sdk_cli.test_framework import (
    TestFramework,
    bstack1lll111l111_opy_,
    bstack1ll1ll11lll_opy_,
    bstack1lll1l1l11l_opy_,
    bstack11llll11l1l_opy_,
    bstack1lll111l1l1_opy_,
)
from pathlib import Path
import grpc
from browserstack_sdk import sdk_pb2 as structs
from datetime import datetime, timezone
from typing import List, Dict, Any
import traceback
from bstack_utils.helper import bstack1l1l1ll11l1_opy_
from bstack_utils.bstack11l1l11ll_opy_ import bstack1lll1ll1l11_opy_
from bstack_utils.constants import EVENTS
from browserstack_sdk.sdk_cli.bstack1lllll1l11l_opy_ import bstack1lllll11ll1_opy_
from browserstack_sdk.sdk_cli.utils.bstack1ll1llll1l1_opy_ import bstack1ll1llll1ll_opy_
from bstack_utils.bstack111ll11111_opy_ import bstack11llll111_opy_
bstack1l1l11llll1_opy_ = bstack1l1l1ll11l1_opy_()
bstack1l1111l11ll_opy_ = 1.0
bstack1l1l111ll11_opy_ = bstack11l1l_opy_ (u"࡚ࠦࡶ࡬ࡰࡣࡧࡩࡩࡇࡴࡵࡣࡦ࡬ࡲ࡫࡮ࡵࡵ࠰ࠦᕴ")
bstack11lll111ll1_opy_ = bstack11l1l_opy_ (u"࡚ࠧࡥࡴࡶࡏࡩࡻ࡫࡬ࠣᕵ")
bstack11lll111lll_opy_ = bstack11l1l_opy_ (u"ࠨࡂࡶ࡫࡯ࡨࡑ࡫ࡶࡦ࡮ࠥᕶ")
bstack11lll11l1ll_opy_ = bstack11l1l_opy_ (u"ࠢࡉࡱࡲ࡯ࡑ࡫ࡶࡦ࡮ࠥᕷ")
bstack11lll11l1l1_opy_ = bstack11l1l_opy_ (u"ࠣࡄࡸ࡭ࡱࡪࡌࡦࡸࡨࡰࡍࡵ࡯࡬ࡇࡹࡩࡳࡺࠢᕸ")
_1l1l11l1l1l_opy_ = set()
class bstack1ll1l11llll_opy_(TestFramework):
    bstack1l1111l1111_opy_ = bstack11l1l_opy_ (u"ࠤࡷࡩࡸࡺ࡟ࡧ࡫ࡻࡸࡺࡸࡥࡴࠤᕹ")
    bstack11llll11111_opy_ = bstack11l1l_opy_ (u"ࠥࡸࡪࡹࡴࡠࡪࡲࡳࡰࡹ࡟ࡴࡶࡤࡶࡹ࡫ࡤࠣᕺ")
    bstack11lll1ll1l1_opy_ = bstack11l1l_opy_ (u"ࠦࡹ࡫ࡳࡵࡡ࡫ࡳࡴࡱࡳࡠࡨ࡬ࡲ࡮ࡹࡨࡦࡦࠥᕻ")
    bstack11lll11lll1_opy_ = bstack11l1l_opy_ (u"ࠧࡺࡥࡴࡶࡢ࡬ࡴࡵ࡫ࡠ࡮ࡤࡷࡹࡥࡳࡵࡣࡵࡸࡪࡪࠢᕼ")
    bstack1l11111llll_opy_ = bstack11l1l_opy_ (u"ࠨࡴࡦࡵࡷࡣ࡭ࡵ࡯࡬ࡡ࡯ࡥࡸࡺ࡟ࡧ࡫ࡱ࡭ࡸ࡮ࡥࡥࠤᕽ")
    bstack11llll1l1ll_opy_: bool
    bstack1lllll1l11l_opy_: bstack1lllll11ll1_opy_  = None
    bstack1ll1ll11l11_opy_ = None
    bstack11lllllllll_opy_ = [
        bstack1lll111l111_opy_.BEFORE_ALL,
        bstack1lll111l111_opy_.AFTER_ALL,
        bstack1lll111l111_opy_.BEFORE_EACH,
        bstack1lll111l111_opy_.AFTER_EACH,
    ]
    def __init__(
        self,
        bstack11lll1l1ll1_opy_: Dict[str, str],
        bstack1l1llll1lll_opy_: List[str]=[bstack11l1l_opy_ (u"ࠢࡱࡻࡷࡩࡸࡺࠢᕾ")],
        bstack1lllll1l11l_opy_: bstack1lllll11ll1_opy_=None,
        bstack1ll1ll11l11_opy_=None
    ):
        super().__init__(bstack1l1llll1lll_opy_, bstack11lll1l1ll1_opy_, bstack1lllll1l11l_opy_)
        self.bstack11llll1l1ll_opy_ = any(bstack11l1l_opy_ (u"ࠣࡲࡼࡸࡪࡹࡴࠣᕿ") in item.lower() for item in bstack1l1llll1lll_opy_)
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
        if test_framework_state == bstack1lll111l111_opy_.TEST or test_framework_state in bstack1ll1l11llll_opy_.bstack11lllllllll_opy_:
            bstack11llll1l11l_opy_(test_framework_state, test_hook_state)
        if test_framework_state == bstack1lll111l111_opy_.NONE:
            self.logger.warning(bstack11l1l_opy_ (u"ࠤ࡬࡫ࡳࡵࡲࡦࡦࠣࡧࡦࡲ࡬ࡣࡣࡦ࡯ࠥࡺࡥࡴࡶࡢࡪࡷࡧ࡭ࡦࡹࡲࡶࡰࡥࡳࡵࡣࡷࡩࡂࢁࡴࡦࡵࡷࡣ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟ࡴࡶࡤࡸࡪࢃࠠࡵࡧࡶࡸࡤ࡮࡯ࡰ࡭ࡢࡷࡹࡧࡴࡦ࠿ࠥᖀ") + str(test_hook_state) + bstack11l1l_opy_ (u"ࠥࠦᖁ"))
            return
        if not self.bstack11llll1l1ll_opy_:
            self.logger.warning(bstack11l1l_opy_ (u"ࠦࡹࡸࡡࡤ࡭ࡢࡩࡻ࡫࡮ࡵ࠼ࠣࡹࡳࡹࡵࡱࡲࡲࡶࡹ࡫ࡤࠡࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡁࠧᖂ") + str(str(self.bstack1l1llll1lll_opy_)) + bstack11l1l_opy_ (u"ࠧࠨᖃ"))
            return
        if not isinstance(args, tuple) or len(args) == 0:
            self.logger.warning(bstack11l1l_opy_ (u"ࠨࡴࡳࡣࡦ࡯ࡤ࡫ࡶࡦࡰࡷ࠾ࠥࡻ࡮ࡦࡺࡳࡩࡨࡺࡥࡥࠢࡤࡶ࡬ࡹ࠽ࡼࡣࡵ࡫ࡸࢃࠠ࡬ࡹࡤࡶ࡬ࡹ࠽ࠣᖄ") + str(kwargs) + bstack11l1l_opy_ (u"ࠢࠣᖅ"))
            return
        instance = self.__1l1111l111l_opy_(context, test_framework_state, test_hook_state, *args, **kwargs)
        if not instance:
            self.logger.debug(bstack11l1l_opy_ (u"ࠣࡶࡵࡥࡨࡱ࡟ࡦࡸࡨࡲࡹࡀࠠࡶࡰ࡫ࡥࡳࡪ࡬ࡦࡦࠣࡩࡻ࡫࡮ࡵ࠿ࡾࡸࡪࡹࡴࡠࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡸࡺࡡࡵࡧࢀ࠲ࢀࡺࡥࡴࡶࡢ࡬ࡴࡵ࡫ࡠࡵࡷࡥࡹ࡫ࡽࠡࡣࡵ࡫ࡸࡃࠢᖆ") + str(args) + bstack11l1l_opy_ (u"ࠤࠥᖇ"))
            return
        try:
            if instance!= None and test_framework_state in bstack1ll1l11llll_opy_.bstack11lllllllll_opy_ and test_hook_state == bstack1lll1l1l11l_opy_.PRE:
                bstack1l1llllllll_opy_ = bstack1lll1ll1l11_opy_.bstack1ll11l1l111_opy_(EVENTS.bstack1l1lllll_opy_.value)
                name = str(EVENTS.bstack1l1lllll_opy_.name)+bstack11l1l_opy_ (u"ࠥ࠾ࠧᖈ")+str(test_framework_state.name)
                TestFramework.bstack11lll1l1l11_opy_(instance, name, bstack1l1llllllll_opy_)
        except Exception as e:
            self.logger.debug(bstack11l1l_opy_ (u"ࠦࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡪࡰࠣ࡬ࡴࡵ࡫ࠡࡧࡵࡶࡴࡸࠠࡱࡴࡨ࠾ࠥࢁࡽࠣᖉ").format(e))
        try:
            if not TestFramework.bstack1lll1ll1l1l_opy_(instance, TestFramework.bstack1l11111lll1_opy_) and test_hook_state == bstack1lll1l1l11l_opy_.PRE:
                test = bstack1ll1l11llll_opy_.__11llllll1l1_opy_(args[0])
                if test:
                    instance.data.update(test)
                    self.logger.debug(bstack11l1l_opy_ (u"ࠧࡲ࡯ࡢࡦࡨࡨࠥ࡯࡮ࡴࡶࡤࡲࡨ࡫࠽ࡼ࡫ࡱࡷࡹࡧ࡮ࡤࡧ࠱ࡶࡪ࡬ࠨࠪࡿࠣࡩࡻ࡫࡮ࡵ࠿ࡾࡸࡪࡹࡴࡠࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡸࡺࡡࡵࡧࢀ࠲ࠧᖊ") + str(test_hook_state) + bstack11l1l_opy_ (u"ࠨࠢᖋ"))
            if test_framework_state == bstack1lll111l111_opy_.TEST:
                if test_hook_state == bstack1lll1l1l11l_opy_.PRE and not TestFramework.bstack1lll1ll1l1l_opy_(instance, TestFramework.bstack1l1l1l11l11_opy_):
                    TestFramework.bstack1lllll1111l_opy_(instance, TestFramework.bstack1l1l1l11l11_opy_, datetime.now(tz=timezone.utc))
                    self.logger.debug(bstack11l1l_opy_ (u"ࠢࡴࡧࡷࠤࡹ࡫ࡳࡵ࠯ࡶࡸࡦࡸࡴࠡࡨࡲࡶࠥ࡯࡮ࡴࡶࡤࡲࡨ࡫࠽ࡼ࡫ࡱࡷࡹࡧ࡮ࡤࡧ࠱ࡶࡪ࡬ࠨࠪࡿࠣࡩࡻ࡫࡮ࡵ࠿ࡾࡸࡪࡹࡴࡠࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡸࡺࡡࡵࡧࢀ࠲ࠧᖌ") + str(test_hook_state) + bstack11l1l_opy_ (u"ࠣࠤᖍ"))
                elif test_hook_state == bstack1lll1l1l11l_opy_.POST and not TestFramework.bstack1lll1ll1l1l_opy_(instance, TestFramework.bstack1l1l11ll111_opy_):
                    TestFramework.bstack1lllll1111l_opy_(instance, TestFramework.bstack1l1l11ll111_opy_, datetime.now(tz=timezone.utc))
                    self.logger.debug(bstack11l1l_opy_ (u"ࠤࡶࡩࡹࠦࡴࡦࡵࡷ࠱ࡪࡴࡤࠡࡨࡲࡶࠥ࡯࡮ࡴࡶࡤࡲࡨ࡫࠽ࡼ࡫ࡱࡷࡹࡧ࡮ࡤࡧ࠱ࡶࡪ࡬ࠨࠪࡿࠣࡩࡻ࡫࡮ࡵ࠿ࡾࡸࡪࡹࡴࡠࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡸࡺࡡࡵࡧࢀ࠲ࠧᖎ") + str(test_hook_state) + bstack11l1l_opy_ (u"ࠥࠦᖏ"))
            elif test_framework_state == bstack1lll111l111_opy_.LOG and test_hook_state == bstack1lll1l1l11l_opy_.POST:
                bstack1ll1l11llll_opy_.__11lllll1111_opy_(instance, *args)
            elif test_framework_state == bstack1lll111l111_opy_.LOG_REPORT and test_hook_state == bstack1lll1l1l11l_opy_.POST:
                self.__1l1111l1l11_opy_(instance, *args)
                self.__1l11111ll1l_opy_(instance)
            elif test_framework_state in bstack1ll1l11llll_opy_.bstack11lllllllll_opy_:
                self.__11lll1lll11_opy_(instance, test_framework_state, test_hook_state, *args)
            self.logger.debug(bstack11l1l_opy_ (u"ࠦࡹࡸࡡࡤ࡭ࡢࡩࡻ࡫࡮ࡵ࠼ࠣ࡬ࡦࡴࡤ࡭ࡧࡧࠤࡪࡼࡥ࡯ࡶࡀࡿࡹ࡫ࡳࡵࡡࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࡤࡹࡴࡢࡶࡨࢁ࠳ࢁࡴࡦࡵࡷࡣ࡭ࡵ࡯࡬ࡡࡶࡸࡦࡺࡥࡾࠢ࡬ࡲࡸࡺࡡ࡯ࡥࡨࡁࠧᖐ") + str(instance.ref()) + bstack11l1l_opy_ (u"ࠧࠨᖑ"))
        except Exception as e:
            self.logger.error(e)
            traceback.print_exc()
        self.bstack11llll1l1l1_opy_(instance, (test_framework_state, test_hook_state), *args, **kwargs)
        try:
            if instance!= None and test_framework_state in bstack1ll1l11llll_opy_.bstack11lllllllll_opy_ and test_hook_state == bstack1lll1l1l11l_opy_.POST:
                name = str(EVENTS.bstack1l1lllll_opy_.name)+bstack11l1l_opy_ (u"ࠨ࠺ࠣᖒ")+str(test_framework_state.name)
                bstack1l1llllllll_opy_ = TestFramework.bstack11lll1llll1_opy_(instance, name)
                bstack1lll1ll1l11_opy_.end(EVENTS.bstack1l1lllll_opy_.value, bstack1l1llllllll_opy_+bstack11l1l_opy_ (u"ࠢ࠻ࡵࡷࡥࡷࡺࠢᖓ"), bstack1l1llllllll_opy_+bstack11l1l_opy_ (u"ࠣ࠼ࡨࡲࡩࠨᖔ"), True, None, test_framework_state.name)
        except Exception as e:
            self.logger.debug(bstack11l1l_opy_ (u"ࠤࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥ࡯࡮ࠡࡪࡲࡳࡰࠦࡥࡳࡴࡲࡶ࠿ࠦࡻࡾࠤᖕ").format(e))
    def bstack1l1l1l11l1l_opy_(self):
        return self.bstack11llll1l1ll_opy_
    def __11lllll1l11_opy_(self, *args):
        if len(args) > 2 and callable(getattr(args[2], bstack11l1l_opy_ (u"ࠥ࡫ࡪࡺ࡟ࡳࡧࡶࡹࡱࡺࠢᖖ"), None)):
            rep = args[2].get_result()
            if rep:
                return TestFramework.bstack1l1ll11l11l_opy_(rep, [bstack11l1l_opy_ (u"ࠦࡼ࡮ࡥ࡯ࠤᖗ"), bstack11l1l_opy_ (u"ࠧࡵࡵࡵࡥࡲࡱࡪࠨᖘ"), bstack11l1l_opy_ (u"ࠨࡰࡢࡵࡶࡩࡩࠨᖙ"), bstack11l1l_opy_ (u"ࠢࡧࡣ࡬ࡰࡪࡪࠢᖚ"), bstack11l1l_opy_ (u"ࠣࡵ࡮࡭ࡵࡶࡥࡥࠤᖛ"), bstack11l1l_opy_ (u"ࠤ࡯ࡳࡳ࡭ࡲࡦࡲࡵࡸࡪࡾࡴࠣᖜ")])
        return None
    def __1l1111l1l11_opy_(self, instance: bstack1ll1ll11lll_opy_, *args):
        result = self.__11lllll1l11_opy_(*args)
        if not result:
            return
        failure = None
        bstack1lllll1ll1l_opy_ = None
        if result.get(bstack11l1l_opy_ (u"ࠥࡳࡺࡺࡣࡰ࡯ࡨࠦᖝ"), None) == bstack11l1l_opy_ (u"ࠦ࡫ࡧࡩ࡭ࡧࡧࠦᖞ") and len(args) > 1 and getattr(args[1], bstack11l1l_opy_ (u"ࠧ࡫ࡸࡤ࡫ࡱࡪࡴࠨᖟ"), None) is not None:
            failure = [{bstack11l1l_opy_ (u"࠭ࡢࡢࡥ࡮ࡸࡷࡧࡣࡦࠩᖠ"): [args[1].excinfo.exconly(), result.get(bstack11l1l_opy_ (u"ࠢ࡭ࡱࡱ࡫ࡷ࡫ࡰࡳࡶࡨࡼࡹࠨᖡ"), None)]}]
            bstack1lllll1ll1l_opy_ = bstack11l1l_opy_ (u"ࠣࡃࡶࡷࡪࡸࡴࡪࡱࡱࡉࡷࡸ࡯ࡳࠤᖢ") if bstack11l1l_opy_ (u"ࠤࡄࡷࡸ࡫ࡲࡵ࡫ࡲࡲࠧᖣ") in getattr(args[1].excinfo, bstack11l1l_opy_ (u"ࠥࡸࡾࡶࡥ࡯ࡣࡰࡩࠧᖤ"), bstack11l1l_opy_ (u"ࠦࠧᖥ")) else bstack11l1l_opy_ (u"࡛ࠧ࡮ࡩࡣࡱࡨࡱ࡫ࡤࡆࡴࡵࡳࡷࠨᖦ")
        bstack11lllll1ll1_opy_ = result.get(bstack11l1l_opy_ (u"ࠨ࡯ࡶࡶࡦࡳࡲ࡫ࠢᖧ"), TestFramework.bstack1l11111l1l1_opy_)
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
            target = None # bstack1l111111l1l_opy_ bstack11llllll11l_opy_ this to be bstack11l1l_opy_ (u"ࠢ࡯ࡱࡧࡩ࡮ࡪࠢᖨ")
            if test_framework_state == bstack1lll111l111_opy_.INIT_TEST:
                target = args[0] if isinstance(args[0], str) else None
                if target:
                    self.__11lllll11ll_opy_(context, test_framework_state, target, *args)
            elif test_framework_state == bstack1lll111l111_opy_.LOG:
                nodeid = getattr(getattr(args[0], bstack11l1l_opy_ (u"ࠣࡰࡲࡨࡪࠨᖩ"), None), bstack11l1l_opy_ (u"ࠤࡱࡳࡩ࡫ࡩࡥࠤᖪ"), None) if args else None
                if isinstance(nodeid, str):
                    target = nodeid
            elif getattr(args[0], bstack11l1l_opy_ (u"ࠥࡲࡴࡪࡥࡪࡦࠥᖫ"), None):
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
        bstack1l1111ll11l_opy_ = TestFramework.bstack1llll1lllll_opy_(instance, bstack1ll1l11llll_opy_.bstack11llll11111_opy_, {})
        if not key in bstack1l1111ll11l_opy_:
            bstack1l1111ll11l_opy_[key] = []
        bstack1l11111l1ll_opy_ = TestFramework.bstack1llll1lllll_opy_(instance, bstack1ll1l11llll_opy_.bstack11lll1ll1l1_opy_, {})
        if not key in bstack1l11111l1ll_opy_:
            bstack1l11111l1ll_opy_[key] = []
        bstack11llll1ll1l_opy_ = {
            bstack1ll1l11llll_opy_.bstack11llll11111_opy_: bstack1l1111ll11l_opy_,
            bstack1ll1l11llll_opy_.bstack11lll1ll1l1_opy_: bstack1l11111l1ll_opy_,
        }
        if test_hook_state == bstack1lll1l1l11l_opy_.PRE:
            hook = {
                bstack11l1l_opy_ (u"ࠦࡰ࡫ࡹࠣᖬ"): key,
                TestFramework.bstack11lll1l1l1l_opy_: uuid4().__str__(),
                TestFramework.bstack1l11111l111_opy_: TestFramework.bstack11llll1l111_opy_,
                TestFramework.bstack11lll1l1lll_opy_: datetime.now(tz=timezone.utc),
                TestFramework.bstack1l1111ll1l1_opy_: [],
                TestFramework.bstack11lll1l111l_opy_: args[1] if len(args) > 1 else bstack11l1l_opy_ (u"ࠬ࠭ᖭ"),
                TestFramework.bstack11lllllll1l_opy_: bstack1ll1llll1ll_opy_.bstack11lll11llll_opy_()
            }
            bstack1l1111ll11l_opy_[key].append(hook)
            bstack11llll1ll1l_opy_[bstack1ll1l11llll_opy_.bstack11lll11lll1_opy_] = key
        elif test_hook_state == bstack1lll1l1l11l_opy_.POST:
            bstack1l1111l1ll1_opy_ = bstack1l1111ll11l_opy_.get(key, [])
            hook = bstack1l1111l1ll1_opy_.pop() if bstack1l1111l1ll1_opy_ else None
            if hook:
                result = self.__11lllll1l11_opy_(*args)
                if result:
                    bstack11lllllll11_opy_ = result.get(bstack11l1l_opy_ (u"ࠨ࡯ࡶࡶࡦࡳࡲ࡫ࠢᖮ"), TestFramework.bstack11llll1l111_opy_)
                    if bstack11lllllll11_opy_ != TestFramework.bstack11llll1l111_opy_:
                        hook[TestFramework.bstack1l11111l111_opy_] = bstack11lllllll11_opy_
                hook[TestFramework.bstack1l111111ll1_opy_] = datetime.now(tz=timezone.utc)
                hook[TestFramework.bstack11lllllll1l_opy_]= bstack1ll1llll1ll_opy_.bstack11lll11llll_opy_()
                self.bstack1l11111ll11_opy_(hook)
                logs = hook.get(TestFramework.bstack11lllll111l_opy_, [])
                if logs: self.bstack1l1l1l1l111_opy_(instance, logs)
                bstack1l11111l1ll_opy_[key].append(hook)
                bstack11llll1ll1l_opy_[bstack1ll1l11llll_opy_.bstack1l11111llll_opy_] = key
        TestFramework.bstack11lllll11l1_opy_(instance, bstack11llll1ll1l_opy_)
        self.logger.debug(bstack11l1l_opy_ (u"ࠢࡵࡴࡤࡧࡰࡥࡨࡰࡱ࡮ࡣࡪࡼࡥ࡯ࡶ࠽ࠤࡹ࡫ࡳࡵࡡ࡫ࡳࡴࡱ࡟ࡴࡶࡤࡸࡪࡃࡻ࡬ࡧࡼࢁ࠳ࢁࡴࡦࡵࡷࡣ࡭ࡵ࡯࡬ࡡࡶࡸࡦࡺࡥࡾࠢ࡫ࡳࡴࡱࡳࡠࡵࡷࡥࡷࡺࡥࡥ࠿ࡾ࡬ࡴࡵ࡫ࡴࡡࡶࡸࡦࡸࡴࡦࡦࢀࠤ࡭ࡵ࡯࡬ࡵࡢࡪ࡮ࡴࡩࡴࡪࡨࡨࡂࠨᖯ") + str(bstack1l11111l1ll_opy_) + bstack11l1l_opy_ (u"ࠣࠤᖰ"))
    def __11lllll1l1l_opy_(
        self,
        context: bstack11llll11l1l_opy_,
        test_framework_state: bstack1lll111l111_opy_,
        test_hook_state: bstack1lll1l1l11l_opy_,
        *args,
        **kwargs,
    ):
        fixturedef = TestFramework.bstack1l1ll11l11l_opy_(args[0], [bstack11l1l_opy_ (u"ࠤࡶࡧࡴࡶࡥࠣᖱ"), bstack11l1l_opy_ (u"ࠥࡥࡷ࡭࡮ࡢ࡯ࡨࠦᖲ"), bstack11l1l_opy_ (u"ࠦࡵࡧࡲࡢ࡯ࡶࠦᖳ"), bstack11l1l_opy_ (u"ࠧ࡯ࡤࡴࠤᖴ"), bstack11l1l_opy_ (u"ࠨࡵ࡯࡫ࡷࡸࡪࡹࡴࠣᖵ"), bstack11l1l_opy_ (u"ࠢࡣࡣࡶࡩ࡮ࡪࠢᖶ")]) if len(args) > 0 else {}
        request = args[1] if len(args) > 1 else None
        scope = request.scope if hasattr(request, bstack11l1l_opy_ (u"ࠣࡵࡦࡳࡵ࡫ࠢᖷ")) else fixturedef.get(bstack11l1l_opy_ (u"ࠤࡶࡧࡴࡶࡥࠣᖸ"), None)
        fixturename = request.fixturename if hasattr(request, bstack11l1l_opy_ (u"ࠥࡪ࡮ࡾࡴࡶࡴࡨࡲࡦࡳࡥࠣᖹ")) else None
        node = request.node if hasattr(request, bstack11l1l_opy_ (u"ࠦࡳࡵࡤࡦࠤᖺ")) else None
        target = request.node.nodeid if hasattr(node, bstack11l1l_opy_ (u"ࠧࡴ࡯ࡥࡧ࡬ࡨࠧᖻ")) else None
        baseid = fixturedef.get(bstack11l1l_opy_ (u"ࠨࡢࡢࡵࡨ࡭ࡩࠨᖼ"), None) or bstack11l1l_opy_ (u"ࠢࠣᖽ")
        if (not target or len(baseid) > 0) and hasattr(request, bstack11l1l_opy_ (u"ࠣࡡࡳࡽ࡫ࡻ࡮ࡤ࡫ࡷࡩࡲࠨᖾ")):
            target = bstack1ll1l11llll_opy_.__11lll1lllll_opy_(request._pyfuncitem.location) if hasattr(request._pyfuncitem, bstack11l1l_opy_ (u"ࠤ࡯ࡳࡨࡧࡴࡪࡱࡱࠦᖿ")) else None
            if target and not TestFramework.bstack1lllll111ll_opy_(target):
                self.__11lllll11ll_opy_(context, test_framework_state, target, (target, request._pyfuncitem.location))
                node = request._pyfuncitem
                self.logger.debug(bstack11l1l_opy_ (u"ࠥࡸࡷࡧࡣ࡬ࡡࡩ࡭ࡽࡺࡵࡳࡧࡢࡩࡻ࡫࡮ࡵ࠼ࠣࡪࡦࡲ࡬ࡣࡣࡦ࡯ࠥࡺࡡࡳࡩࡨࡸࡂࢁࡴࡢࡴࡪࡩࡹࢃࠠࡧ࡫ࡻࡸࡺࡸࡥ࡯ࡣࡰࡩࡂࢁࡦࡪࡺࡷࡹࡷ࡫࡮ࡢ࡯ࡨࢁࠥࡴ࡯ࡥࡧࡀࡿࡳࡵࡤࡦࡿࠣࡩࡻ࡫࡮ࡵ࠿ࡾࡸࡪࡹࡴࡠࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡸࡺࡡࡵࡧࢀ࠲ࠧᗀ") + str(test_hook_state) + bstack11l1l_opy_ (u"ࠦࠧᗁ"))
        if not fixturedef or not scope or not target:
            self.logger.warning(bstack11l1l_opy_ (u"ࠧࡺࡲࡢࡥ࡮ࡣ࡫࡯ࡸࡵࡷࡵࡩࡤ࡫ࡶࡦࡰࡷ࠾ࠥࡻ࡮ࡩࡣࡱࡨࡱ࡫ࡤࠡࡧࡹࡩࡳࡺ࠽ࡼࡶࡨࡷࡹࡥࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡶࡸࡦࡺࡥࡾ࠰ࡾࡸࡪࡹࡴࡠࡪࡲࡳࡰࡥࡳࡵࡣࡷࡩࢂࠦࡦࡪࡺࡷࡹࡷ࡫ࡤࡦࡨࡀࡿ࡫࡯ࡸࡵࡷࡵࡩࡩ࡫ࡦࡾࠢࡶࡧࡴࡶࡥ࠾ࡽࡶࡧࡴࡶࡥࡾࠢࡷࡥࡷ࡭ࡥࡵ࠿ࠥᗂ") + str(target) + bstack11l1l_opy_ (u"ࠨࠢᗃ"))
            return None
        instance = TestFramework.bstack1lllll111ll_opy_(target)
        if not instance:
            self.logger.warning(bstack11l1l_opy_ (u"ࠢࡵࡴࡤࡧࡰࡥࡦࡪࡺࡷࡹࡷ࡫࡟ࡦࡸࡨࡲࡹࡀࠠࡶࡰ࡫ࡥࡳࡪ࡬ࡦࡦࠣࡩࡻ࡫࡮ࡵ࠿ࡾࡸࡪࡹࡴࡠࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡸࡺࡡࡵࡧࢀ࠲ࢀࡺࡥࡴࡶࡢ࡬ࡴࡵ࡫ࡠࡵࡷࡥࡹ࡫ࡽࠡࡨ࡬ࡼࡹࡻࡲࡦࡰࡤࡱࡪࡃࡻࡧ࡫ࡻࡸࡺࡸࡥ࡯ࡣࡰࡩࢂࠦࡳࡤࡱࡳࡩࡂࢁࡳࡤࡱࡳࡩࢂࠦࡢࡢࡵࡨ࡭ࡩࡃࡻࡣࡣࡶࡩ࡮ࡪࡽࠡࡶࡤࡶ࡬࡫ࡴ࠾ࠤᗄ") + str(target) + bstack11l1l_opy_ (u"ࠣࠤᗅ"))
            return None
        bstack1l11111l11l_opy_ = TestFramework.bstack1llll1lllll_opy_(instance, bstack1ll1l11llll_opy_.bstack1l1111l1111_opy_, {})
        if os.getenv(bstack11l1l_opy_ (u"ࠤࡖࡈࡐࡥࡃࡍࡋࡢࡊࡑࡇࡇࡠࡈࡌ࡜࡙࡛ࡒࡆࡕࠥᗆ"), bstack11l1l_opy_ (u"ࠥ࠵ࠧᗇ")) == bstack11l1l_opy_ (u"ࠦ࠶ࠨᗈ"):
            bstack1l111111111_opy_ = bstack11l1l_opy_ (u"ࠧࡀࠢᗉ").join((scope, fixturename))
            bstack1l1111ll111_opy_ = datetime.now(tz=timezone.utc)
            bstack1l1111ll1ll_opy_ = {
                bstack11l1l_opy_ (u"ࠨ࡫ࡦࡻࠥᗊ"): bstack1l111111111_opy_,
                bstack11l1l_opy_ (u"ࠢࡵࡣࡪࡷࠧᗋ"): bstack1ll1l11llll_opy_.__11llll1ll11_opy_(request.node),
                bstack11l1l_opy_ (u"ࠣࡨ࡬ࡼࡹࡻࡲࡦࠤᗌ"): fixturedef,
                bstack11l1l_opy_ (u"ࠤࡶࡧࡴࡶࡥࠣᗍ"): scope,
                bstack11l1l_opy_ (u"ࠥࡸࡾࡶࡥࠣᗎ"): None,
            }
            try:
                if test_hook_state == bstack1lll1l1l11l_opy_.POST and callable(getattr(args[-1], bstack11l1l_opy_ (u"ࠦ࡬࡫ࡴࡠࡴࡨࡷࡺࡲࡴࠣᗏ"), None)):
                    bstack1l1111ll1ll_opy_[bstack11l1l_opy_ (u"ࠧࡺࡹࡱࡧࠥᗐ")] = TestFramework.bstack1l1l1ll1lll_opy_(args[-1].get_result())
            except Exception as e:
                pass
            if test_hook_state == bstack1lll1l1l11l_opy_.PRE:
                bstack1l1111ll1ll_opy_[bstack11l1l_opy_ (u"ࠨࡵࡶ࡫ࡧࠦᗑ")] = uuid4().__str__()
                bstack1l1111ll1ll_opy_[bstack1ll1l11llll_opy_.bstack11lll1l1lll_opy_] = bstack1l1111ll111_opy_
            elif test_hook_state == bstack1lll1l1l11l_opy_.POST:
                bstack1l1111ll1ll_opy_[bstack1ll1l11llll_opy_.bstack1l111111ll1_opy_] = bstack1l1111ll111_opy_
            if bstack1l111111111_opy_ in bstack1l11111l11l_opy_:
                bstack1l11111l11l_opy_[bstack1l111111111_opy_].update(bstack1l1111ll1ll_opy_)
                self.logger.debug(bstack11l1l_opy_ (u"ࠢࡶࡲࡧࡥࡹ࡫ࡤࠡࡨ࡬ࡼࡹࡻࡲࡦࡰࡤࡱࡪࡃࡻࡧ࡫ࡻࡸࡺࡸࡥ࡯ࡣࡰࡩࢂࠦࡳࡤࡱࡳࡩࡂࢁࡳࡤࡱࡳࡩࢂࠦࡦࡪࡺࡷࡹࡷ࡫࠽ࠣᗒ") + str(bstack1l11111l11l_opy_[bstack1l111111111_opy_]) + bstack11l1l_opy_ (u"ࠣࠤᗓ"))
            else:
                bstack1l11111l11l_opy_[bstack1l111111111_opy_] = bstack1l1111ll1ll_opy_
                self.logger.debug(bstack11l1l_opy_ (u"ࠤࡶࡥࡻ࡫ࡤࠡࡨ࡬ࡼࡹࡻࡲࡦࡰࡤࡱࡪࡃࡻࡧ࡫ࡻࡸࡺࡸࡥ࡯ࡣࡰࡩࢂࠦࡳࡤࡱࡳࡩࡂࢁࡳࡤࡱࡳࡩࢂࠦࡦࡪࡺࡷࡹࡷ࡫࠽ࡼࡶࡨࡷࡹࡥࡦࡪࡺࡷࡹࡷ࡫ࡽࠡࡶࡵࡥࡨࡱࡥࡥࡡࡩ࡭ࡽࡺࡵࡳࡧࡶࡁࠧᗔ") + str(len(bstack1l11111l11l_opy_)) + bstack11l1l_opy_ (u"ࠥࠦᗕ"))
        TestFramework.bstack1lllll1111l_opy_(instance, bstack1ll1l11llll_opy_.bstack1l1111l1111_opy_, bstack1l11111l11l_opy_)
        self.logger.debug(bstack11l1l_opy_ (u"ࠦࡸࡧࡶࡦࡦࠣࡪ࡮ࡾࡴࡶࡴࡨࡷࡂࢁ࡬ࡦࡰࠫࡸࡷࡧࡣ࡬ࡧࡧࡣ࡫࡯ࡸࡵࡷࡵࡩࡸ࠯ࡽࠡ࡫ࡱࡷࡹࡧ࡮ࡤࡧࡀࠦᗖ") + str(instance.ref()) + bstack11l1l_opy_ (u"ࠧࠨᗗ"))
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
            bstack1ll1l11llll_opy_.bstack1l1111l1111_opy_: {},
            bstack1ll1l11llll_opy_.bstack11lll1ll1l1_opy_: {},
            bstack1ll1l11llll_opy_.bstack11llll11111_opy_: {},
        })
        if len(args) > 1 and isinstance(args[1], tuple):
            TestFramework.bstack1lllll1111l_opy_(ob, TestFramework.bstack11llll1llll_opy_, str(args[1][0]))
        if context.platform_index >= 0:
            TestFramework.bstack1lllll1111l_opy_(ob, TestFramework.bstack1ll1111l111_opy_, context.platform_index)
        TestFramework.bstack1llll11l1l1_opy_[ctx.id] = ob
        self.logger.debug(bstack11l1l_opy_ (u"ࠨࡳࡢࡸࡨࡨࠥ࡯࡮ࡴࡶࡤࡲࡨ࡫ࠠࡤࡶࡻ࠲࡮ࡪ࠽ࡼࡥࡷࡼ࠳࡯ࡤࡾࠢࡷࡥࡷ࡭ࡥࡵ࠿ࡾࡸࡦࡸࡧࡦࡶࢀࠤࡦࡸࡧࡴ࠿ࡾࡥࡷ࡭ࡳࡾࠢ࡬ࡲࡸࡺࡡ࡯ࡥࡨࡷࡂࠨᗘ") + str(TestFramework.bstack1llll11l1l1_opy_.keys()) + bstack11l1l_opy_ (u"ࠢࠣᗙ"))
        return ob
    def bstack1l1l1111lll_opy_(self, instance: bstack1ll1ll11lll_opy_, bstack1llll1lll1l_opy_: Tuple[bstack1lll111l111_opy_, bstack1lll1l1l11l_opy_]):
        bstack11llll11l11_opy_ = (
            bstack1ll1l11llll_opy_.bstack11lll11lll1_opy_
            if bstack1llll1lll1l_opy_[1] == bstack1lll1l1l11l_opy_.PRE
            else bstack1ll1l11llll_opy_.bstack1l11111llll_opy_
        )
        hook = bstack1ll1l11llll_opy_.bstack11llll111l1_opy_(instance, bstack11llll11l11_opy_)
        entries = hook.get(TestFramework.bstack1l1111ll1l1_opy_, []) if isinstance(hook, dict) else []
        entries.extend(TestFramework.bstack1llll1lllll_opy_(instance, TestFramework.bstack1l1111111l1_opy_, []))
        return entries
    def bstack1l1l1l11lll_opy_(self, instance: bstack1ll1ll11lll_opy_, bstack1llll1lll1l_opy_: Tuple[bstack1lll111l111_opy_, bstack1lll1l1l11l_opy_]):
        bstack11llll11l11_opy_ = (
            bstack1ll1l11llll_opy_.bstack11lll11lll1_opy_
            if bstack1llll1lll1l_opy_[1] == bstack1lll1l1l11l_opy_.PRE
            else bstack1ll1l11llll_opy_.bstack1l11111llll_opy_
        )
        bstack1ll1l11llll_opy_.bstack1l111111l11_opy_(instance, bstack11llll11l11_opy_)
        TestFramework.bstack1llll1lllll_opy_(instance, TestFramework.bstack1l1111111l1_opy_, []).clear()
    def bstack1l11111ll11_opy_(self, hook: Dict[str, Any]) -> None:
        bstack11l1l_opy_ (u"ࠣࠤࠥࠎࠥࠦࠠࠡࠢࠣࠤࠥࡖࡲࡰࡥࡨࡷࡸ࡫ࡳࠡࡶ࡫ࡩࠥࡎ࡯ࡰ࡭ࡏࡩࡻ࡫࡬ࠡࡣࡷࡸࡦࡩࡨ࡮ࡧࡱࡸࡸࠦࡳࡪ࡯࡬ࡰࡦࡸࠠࡵࡱࠣࡸ࡭࡫ࠠࡋࡣࡹࡥࠥ࡯࡭ࡱ࡮ࡨࡱࡪࡴࡴࡢࡶ࡬ࡳࡳ࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࡖ࡫࡭ࡸࠦ࡭ࡦࡶ࡫ࡳࡩࡀࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣ࠱ࠥࡉࡨࡦࡥ࡮ࡷࠥࡺࡨࡦࠢࡋࡳࡴࡱࡌࡦࡸࡨࡰࠥࡪࡩࡳࡧࡦࡸࡴࡸࡹࠡ࡫ࡱࡷ࡮ࡪࡥࠡࢀ࠲࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠲࡙ࡵࡲ࡯ࡢࡦࡨࡨࡆࡺࡴࡢࡥ࡫ࡱࡪࡴࡴࡴ࠰ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦ࠭ࠡࡈࡲࡶࠥ࡫ࡡࡤࡪࠣࡪ࡮ࡲࡥࠡ࡫ࡱࠤ࡭ࡵ࡯࡬ࡡ࡯ࡩࡻ࡫࡬ࡠࡨ࡬ࡰࡪࡹࠬࠡࡴࡨࡴࡱࡧࡣࡦࡵ࡙ࠣࠦ࡫ࡳࡵࡎࡨࡺࡪࡲࠢࠡࡹ࡬ࡸ࡭ࠦࠢࡉࡱࡲ࡯ࡑ࡫ࡶࡦ࡮ࠥࠤ࡮ࡴࠠࡪࡶࡶࠤࡵࡧࡴࡩ࠰ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦ࠭ࠡࡋࡩࠤࡦࠦࡦࡪ࡮ࡨࠤ࡮ࡴࠠࡵࡪࡨࠤࡩ࡯ࡲࡦࡥࡷࡳࡷࡿࠠ࡮ࡣࡷࡧ࡭࡫ࡳࠡࡣࠣࡱࡴࡪࡩࡧ࡫ࡨࡨࠥ࡮࡯ࡰ࡭࠰ࡰࡪࡼࡥ࡭ࠢࡩ࡭ࡱ࡫ࠬࠡ࡫ࡷࠤࡨࡸࡥࡢࡶࡨࡷࠥࡧࠠࡍࡱࡪࡉࡳࡺࡲࡺࠢࡲࡦ࡯࡫ࡣࡵࠢࡺ࡭ࡹ࡮ࠠࡢࡶࡷࡥࡨ࡮࡭ࡦࡰࡷࠤࡩ࡫ࡴࡢ࡫࡯ࡷ࠳ࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢ࠰ࠤࡘ࡯࡭ࡪ࡮ࡤࡶࡱࡿࠬࠡ࡫ࡷࠤࡵࡸ࡯ࡤࡧࡶࡷࡪࡹࠠࡃࡷ࡬ࡰࡩࡒࡥࡷࡧ࡯ࠤࡦࡺࡴࡢࡥ࡫ࡱࡪࡴࡴࡴࠢ࡯ࡳࡨࡧࡴࡦࡦࠣ࡭ࡳࠦࡈࡰࡱ࡮ࡐࡪࡼࡥ࡭࠱ࡅࡹ࡮ࡲࡤࡍࡧࡹࡩࡱࡎ࡯ࡰ࡭ࡈࡺࡪࡴࡴࠡࡤࡼࠤࡷ࡫ࡰ࡭ࡣࡦ࡭ࡳ࡭ࠠࠣࡄࡸ࡭ࡱࡪࡌࡦࡸࡨࡰࠧࠦࡷࡪࡶ࡫ࠤࠧࡎ࡯ࡰ࡭ࡏࡩࡻ࡫࡬࠰ࡄࡸ࡭ࡱࡪࡌࡦࡸࡨࡰࡍࡵ࡯࡬ࡇࡹࡩࡳࡺࠢ࠯ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥ࠳ࠠࡕࡪࡨࠤࡨࡸࡥࡢࡶࡨࡨࠥࡒ࡯ࡨࡇࡱࡸࡷࡿࠠࡰࡤ࡭ࡩࡨࡺࡳࠡࡣࡵࡩࠥࡧࡤࡥࡧࡧࠤࡹࡵࠠࡵࡪࡨࠤ࡭ࡵ࡯࡬ࠩࡶࠤࠧࡲ࡯ࡨࡵࠥࠤࡱ࡯ࡳࡵ࠰ࠍࠤࠥࠦࠠࠡࠢࠣࠤࡆࡸࡧࡴ࠼ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࡪࡲࡳࡰࡀࠠࡕࡪࡨࠤࡪࡼࡥ࡯ࡶࠣࡨ࡮ࡩࡴࡪࡱࡱࡥࡷࡿࠠࡤࡱࡱࡸࡦ࡯࡮ࡪࡰࡪࠤࡪࡾࡩࡴࡶ࡬ࡲ࡬ࠦ࡬ࡰࡩࡶࠤࡦࡴࡤࠡࡪࡲࡳࡰࠦࡩ࡯ࡨࡲࡶࡲࡧࡴࡪࡱࡱ࠲ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣ࡬ࡴࡵ࡫ࡠ࡮ࡨࡺࡪࡲ࡟ࡧ࡫࡯ࡩࡸࡀࠠࡍ࡫ࡶࡸࠥࡵࡦࠡࡒࡤࡸ࡭ࠦ࡯ࡣ࡬ࡨࡧࡹࡹࠠࡧࡴࡲࡱࠥࡺࡨࡦࠢࡗࡩࡸࡺࡌࡦࡸࡨࡰࠥࡳ࡯࡯࡫ࡷࡳࡷ࡯࡮ࡨ࠰ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࡤࡸ࡭ࡱࡪ࡟࡭ࡧࡹࡩࡱࡥࡦࡪ࡮ࡨࡷ࠿ࠦࡌࡪࡵࡷࠤࡴ࡬ࠠࡑࡣࡷ࡬ࠥࡵࡢ࡫ࡧࡦࡸࡸࠦࡦࡳࡱࡰࠤࡹ࡮ࡥࠡࡄࡸ࡭ࡱࡪࡌࡦࡸࡨࡰࠥࡳ࡯࡯࡫ࡷࡳࡷ࡯࡮ࡨ࠰ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠧࠨࠢᗚ")
        global _1l1l11l1l1l_opy_
        platform_index = os.environ[bstack11l1l_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡒࡏࡅ࡙ࡌࡏࡓࡏࡢࡍࡓࡊࡅ࡙ࠩᗛ")]
        bstack1l1l111l11l_opy_ = os.path.join(bstack1l1l11llll1_opy_, (bstack1l1l111ll11_opy_ + str(platform_index)), bstack11lll11l1ll_opy_)
        if not os.path.exists(bstack1l1l111l11l_opy_) or not os.path.isdir(bstack1l1l111l11l_opy_):
            self.logger.debug(bstack11l1l_opy_ (u"ࠥࡈ࡮ࡸࡥࡤࡶࡲࡶࡾࠦࡤࡰࡧࡶࠤࡳࡵࡴࠡࡧࡻ࡭ࡸࡺࡳࠡࡶࡲࠤࡵࡸ࡯ࡤࡧࡶࡷࠥࢁࡽࠣᗜ").format(bstack1l1l111l11l_opy_))
            return
        logs = hook.get(bstack11l1l_opy_ (u"ࠦࡱࡵࡧࡴࠤᗝ"), [])
        with os.scandir(bstack1l1l111l11l_opy_) as entries:
            for entry in entries:
                abs_path = os.path.abspath(entry.path)
                if abs_path in _1l1l11l1l1l_opy_:
                    self.logger.info(bstack11l1l_opy_ (u"ࠧࡖࡡࡵࡪࠣࡥࡱࡸࡥࡢࡦࡼࠤࡵࡸ࡯ࡤࡧࡶࡷࡪࡪࠠࡼࡿࠥᗞ").format(abs_path))
                    continue
                if entry.is_file():
                    try:
                        timestamp = datetime.fromtimestamp(entry.stat().st_mtime, tz=timezone.utc).isoformat()
                    except Exception:
                        timestamp = bstack11l1l_opy_ (u"ࠨࠢᗟ")
                    log_entry = bstack1lll111l1l1_opy_(
                        kind=bstack11l1l_opy_ (u"ࠢࡕࡇࡖࡘࡤࡇࡔࡕࡃࡆࡌࡒࡋࡎࡕࠤᗠ"),
                        message=bstack11l1l_opy_ (u"ࠣࠤᗡ"),
                        level=bstack11l1l_opy_ (u"ࠤࠥᗢ"),
                        timestamp=timestamp,
                        fileName=entry.name,
                        bstack1l1ll11111l_opy_=entry.stat().st_size,
                        bstack1l1l1llll11_opy_=bstack11l1l_opy_ (u"ࠥࡑࡆࡔࡕࡂࡎࡢ࡙ࡕࡒࡏࡂࡆࠥᗣ"),
                        bstack1llllll_opy_=os.path.abspath(entry.path),
                        bstack11lll11ll11_opy_=hook.get(TestFramework.bstack11lll1l1l1l_opy_)
                    )
                    logs.append(log_entry)
                    _1l1l11l1l1l_opy_.add(abs_path)
        platform_index = os.environ[bstack11l1l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡔࡑࡇࡔࡇࡑࡕࡑࡤࡏࡎࡅࡇ࡛ࠫᗤ")]
        bstack1l1111lll11_opy_ = os.path.join(bstack1l1l11llll1_opy_, (bstack1l1l111ll11_opy_ + str(platform_index)), bstack11lll11l1ll_opy_, bstack11lll11l1l1_opy_)
        if not os.path.exists(bstack1l1111lll11_opy_) or not os.path.isdir(bstack1l1111lll11_opy_):
            self.logger.info(bstack11l1l_opy_ (u"ࠧࡔ࡯ࠡࡄࡸ࡭ࡱࡪࡌࡦࡸࡨࡰࡍࡵ࡯࡬ࡇࡹࡩࡳࡺࠠࡢࡶࡷࡥࡨ࡮࡭ࡦࡰࡷࡷࠥࡪࡩࡳࡧࡦࡸࡴࡸࡹࠡࡨࡲࡹࡳࡪࠠࡢࡶ࠽ࠤࢀࢃࠢᗥ").format(bstack1l1111lll11_opy_))
        else:
            self.logger.info(bstack11l1l_opy_ (u"ࠨࡐࡳࡱࡦࡩࡸࡹࡩ࡯ࡩࠣࡆࡺ࡯࡬ࡥࡎࡨࡺࡪࡲࡈࡰࡱ࡮ࡉࡻ࡫࡮ࡵࠢࡤࡸࡹࡧࡣࡩ࡯ࡨࡲࡹࡹࠠࡧࡴࡲࡱࠥࡪࡩࡳࡧࡦࡸࡴࡸࡹ࠻ࠢࡾࢁࠧᗦ").format(bstack1l1111lll11_opy_))
            with os.scandir(bstack1l1111lll11_opy_) as entries:
                for entry in entries:
                    abs_path = os.path.abspath(entry.path)
                    if abs_path in _1l1l11l1l1l_opy_:
                        self.logger.info(bstack11l1l_opy_ (u"ࠢࡑࡣࡷ࡬ࠥࡧ࡬ࡳࡧࡤࡨࡾࠦࡰࡳࡱࡦࡩࡸࡹࡥࡥࠢࡾࢁࠧᗧ").format(abs_path))
                        continue
                    if entry.is_file():
                        try:
                            timestamp = datetime.fromtimestamp(entry.stat().st_mtime, tz=timezone.utc).isoformat()
                        except Exception:
                            timestamp = bstack11l1l_opy_ (u"ࠣࠤᗨ")
                        log_entry = bstack1lll111l1l1_opy_(
                            kind=bstack11l1l_opy_ (u"ࠤࡗࡉࡘ࡚࡟ࡂࡖࡗࡅࡈࡎࡍࡆࡐࡗࠦᗩ"),
                            message=bstack11l1l_opy_ (u"ࠥࠦᗪ"),
                            level=bstack11l1l_opy_ (u"ࠦࡇࡻࡩ࡭ࡦࡏࡩࡻ࡫࡬ࠣᗫ"),
                            timestamp=timestamp,
                            fileName=entry.name,
                            bstack1l1ll11111l_opy_=entry.stat().st_size,
                            bstack1l1l1llll11_opy_=bstack11l1l_opy_ (u"ࠧࡓࡁࡏࡗࡄࡐࡤ࡛ࡐࡍࡑࡄࡈࠧᗬ"),
                            bstack1llllll_opy_=os.path.abspath(entry.path),
                            bstack1l1l1l1111l_opy_=hook.get(TestFramework.bstack11lll1l1l1l_opy_)
                        )
                        logs.append(log_entry)
                        _1l1l11l1l1l_opy_.add(abs_path)
        hook[bstack11l1l_opy_ (u"ࠨ࡬ࡰࡩࡶࠦᗭ")] = logs
    def bstack1l1l1l1l111_opy_(
        self,
        bstack1l1l1111l11_opy_: bstack1ll1ll11lll_opy_,
        entries: List[bstack1lll111l1l1_opy_],
    ):
        req = structs.LogCreatedEventRequest()
        req.bin_session_id = os.environ.get(bstack11l1l_opy_ (u"ࠢࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡃࡍࡋࡢࡆࡎࡔ࡟ࡔࡇࡖࡗࡎࡕࡎࡠࡋࡇࠦᗮ"))
        req.platform_index = TestFramework.bstack1llll1lllll_opy_(bstack1l1l1111l11_opy_, TestFramework.bstack1ll1111l111_opy_)
        req.execution_context.hash = str(bstack1l1l1111l11_opy_.context.hash)
        req.execution_context.thread_id = str(bstack1l1l1111l11_opy_.context.thread_id)
        req.execution_context.process_id = str(bstack1l1l1111l11_opy_.context.process_id)
        for entry in entries:
            log_entry = req.logs.add()
            log_entry.test_framework_name = TestFramework.bstack1llll1lllll_opy_(bstack1l1l1111l11_opy_, TestFramework.bstack1l1llll11l1_opy_)
            log_entry.test_framework_version = TestFramework.bstack1llll1lllll_opy_(bstack1l1l1111l11_opy_, TestFramework.bstack1l1l1lll1ll_opy_)
            log_entry.uuid = entry.bstack11lll11ll11_opy_
            log_entry.test_framework_state = bstack1l1l1111l11_opy_.state.name
            log_entry.message = entry.message.encode(bstack11l1l_opy_ (u"ࠣࡷࡷࡪ࠲࠾ࠢᗯ"))
            log_entry.kind = entry.kind
            log_entry.timestamp = (
                entry.timestamp.isoformat()
                if isinstance(entry.timestamp, datetime)
                else datetime.now(tz=timezone.utc).isoformat()
            )
            log_entry.level = bstack11l1l_opy_ (u"ࠤࠥᗰ")
            if entry.kind == bstack11l1l_opy_ (u"ࠥࡘࡊ࡙ࡔࡠࡃࡗࡘࡆࡉࡈࡎࡇࡑࡘࠧᗱ"):
                log_entry.file_name = entry.fileName
                log_entry.file_size = entry.bstack1l1ll11111l_opy_
                log_entry.file_path = entry.bstack1llllll_opy_
        def bstack1l1l1l1l1l1_opy_():
            bstack11ll1l1ll1_opy_ = datetime.now()
            try:
                self.bstack1ll1ll11l11_opy_.LogCreatedEvent(req)
                bstack1l1l1111l11_opy_.bstack11lll111_opy_(bstack11l1l_opy_ (u"ࠦ࡬ࡸࡰࡤ࠼ࡶࡩࡳࡪ࡟࡭ࡱࡪࡣࡨࡸࡥࡢࡶࡨࡨࡤ࡫ࡶࡦࡰࡷࡣࡦࡺࡴࡢࡥ࡫ࡱࡪࡴࡴࠣᗲ"), datetime.now() - bstack11ll1l1ll1_opy_)
            except grpc.RpcError as e:
                self.log_error(bstack11l1l_opy_ (u"ࠧࡸࡰࡤ࠯ࡨࡶࡷࡵࡲ࠻ࠢࡶࡩࡳࡪ࡟࡭ࡱࡪࡣࡨࡸࡥࡢࡶࡨࡨࡤ࡫ࡶࡦࡰࡷࡣࡦࡺࡴࡢࡥ࡫ࡱࡪࡴࡴࠡࡽࢀࠦᗳ").format(str(e)))
                traceback.print_exc()
        self.bstack1lllll1l11l_opy_.enqueue(bstack1l1l1l1l1l1_opy_)
    def __1l11111ll1l_opy_(self, instance) -> None:
        bstack11l1l_opy_ (u"ࠨࠢࠣࠌࠣࠤࠥࠦࠠࠡࠢࠣࡐࡴࡧࡤࡴࠢࡦࡹࡸࡺ࡯࡮ࠢࡷࡥ࡬ࡹࠠࡧࡱࡵࠤࡹ࡮ࡥࠡࡩ࡬ࡺࡪࡴࠠࡵࡧࡶࡸࠥ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࠡ࡫ࡱࡷࡹࡧ࡮ࡤࡧ࠱ࠎࠥࠦࠠࠡࠢࠣࠤࠥࡉࡲࡦࡣࡷࡩࡸࠦࡡࠡࡦ࡬ࡧࡹࠦࡣࡰࡰࡷࡥ࡮ࡴࡩ࡯ࡩࠣࡸࡪࡹࡴࠡ࡮ࡨࡺࡪࡲࠠࡤࡷࡶࡸࡴࡳࠠ࡮ࡧࡷࡥࡩࡧࡴࡢࠢࡵࡩࡹࡸࡩࡦࡸࡨࡨࠥ࡬ࡲࡰ࡯ࠍࠤࠥࠦࠠࠡࠢࠣࠤࡈࡻࡳࡵࡱࡰࡘࡦ࡭ࡍࡢࡰࡤ࡫ࡪࡸࠠࡢࡰࡧࠤࡺࡶࡤࡢࡶࡨࡷࠥࡺࡨࡦࠢ࡬ࡲࡸࡺࡡ࡯ࡥࡨࠤࡸࡺࡡࡵࡧࠣࡹࡸ࡯࡮ࡨࠢࡶࡩࡹࡥࡳࡵࡣࡷࡩࡤ࡫࡮ࡵࡴ࡬ࡩࡸ࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࠤࠥࠦᗴ")
        bstack11llll1ll1l_opy_ = {bstack11l1l_opy_ (u"ࠢࡤࡷࡶࡸࡴࡳ࡟࡮ࡧࡷࡥࡩࡧࡴࡢࠤᗵ"): bstack1ll1llll1ll_opy_.bstack11lll11llll_opy_()}
        from browserstack_sdk.sdk_cli.test_framework import TestFramework
        TestFramework.bstack11lllll11l1_opy_(instance, bstack11llll1ll1l_opy_)
    @staticmethod
    def bstack11llll111l1_opy_(instance: bstack1ll1ll11lll_opy_, bstack11llll11l11_opy_: str):
        bstack11lll1l11l1_opy_ = (
            bstack1ll1l11llll_opy_.bstack11lll1ll1l1_opy_
            if bstack11llll11l11_opy_ == bstack1ll1l11llll_opy_.bstack1l11111llll_opy_
            else bstack1ll1l11llll_opy_.bstack11llll11111_opy_
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
        hook = bstack1ll1l11llll_opy_.bstack11llll111l1_opy_(instance, bstack11llll11l11_opy_)
        if isinstance(hook, dict):
            hook.get(TestFramework.bstack1l1111ll1l1_opy_, []).clear()
    @staticmethod
    def __11lllll1111_opy_(instance: bstack1ll1ll11lll_opy_, *args):
        if len(args) < 2 or not callable(getattr(args[1], bstack11l1l_opy_ (u"ࠣࡩࡨࡸࡤࡸࡥࡤࡱࡵࡨࡸࠨᗶ"), None)):
            return
        if os.getenv(bstack11l1l_opy_ (u"ࠤࡖࡈࡐࡥࡃࡍࡋࡢࡊࡑࡇࡇࡠࡎࡒࡋࡘࠨᗷ"), bstack11l1l_opy_ (u"ࠥ࠵ࠧᗸ")) != bstack11l1l_opy_ (u"ࠦ࠶ࠨᗹ"):
            bstack1ll1l11llll_opy_.logger.warning(bstack11l1l_opy_ (u"ࠧ࡯ࡧ࡯ࡱࡵ࡭ࡳ࡭ࠠࡤࡣࡳࡰࡴ࡭ࠢᗺ"))
            return
        bstack1l1111l11l1_opy_ = {
            bstack11l1l_opy_ (u"ࠨࡳࡦࡶࡸࡴࠧᗻ"): (bstack1ll1l11llll_opy_.bstack11lll11lll1_opy_, bstack1ll1l11llll_opy_.bstack11llll11111_opy_),
            bstack11l1l_opy_ (u"ࠢࡵࡧࡤࡶࡩࡵࡷ࡯ࠤᗼ"): (bstack1ll1l11llll_opy_.bstack1l11111llll_opy_, bstack1ll1l11llll_opy_.bstack11lll1ll1l1_opy_),
        }
        for when in (bstack11l1l_opy_ (u"ࠣࡵࡨࡸࡺࡶࠢᗽ"), bstack11l1l_opy_ (u"ࠤࡦࡥࡱࡲࠢᗾ"), bstack11l1l_opy_ (u"ࠥࡸࡪࡧࡲࡥࡱࡺࡲࠧᗿ")):
            bstack1l111111lll_opy_ = args[1].get_records(when)
            if not bstack1l111111lll_opy_:
                continue
            records = [
                bstack1lll111l1l1_opy_(
                    kind=TestFramework.bstack1l1l1llllll_opy_,
                    message=r.message,
                    level=r.levelname if hasattr(r, bstack11l1l_opy_ (u"ࠦࡱ࡫ࡶࡦ࡮ࡱࡥࡲ࡫ࠢᘀ")) and r.levelname else None,
                    timestamp=(
                        datetime.fromtimestamp(r.created, tz=timezone.utc)
                        if hasattr(r, bstack11l1l_opy_ (u"ࠧࡩࡲࡦࡣࡷࡩࡩࠨᘁ")) and r.created
                        else None
                    ),
                )
                for r in bstack1l111111lll_opy_
                if isinstance(getattr(r, bstack11l1l_opy_ (u"ࠨ࡭ࡦࡵࡶࡥ࡬࡫ࠢᘂ"), None), str) and r.message.strip()
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
    def __11llllll1l1_opy_(test) -> Dict[str, Any]:
        bstack1lll1ll111_opy_ = bstack1ll1l11llll_opy_.__11lll1lllll_opy_(test.location) if hasattr(test, bstack11l1l_opy_ (u"ࠢ࡭ࡱࡦࡥࡹ࡯࡯࡯ࠤᘃ")) else getattr(test, bstack11l1l_opy_ (u"ࠣࡰࡲࡨࡪ࡯ࡤࠣᘄ"), None)
        test_name = test.name if hasattr(test, bstack11l1l_opy_ (u"ࠤࡱࡥࡲ࡫ࠢᘅ")) else None
        bstack11llll111ll_opy_ = test.fspath.strpath if hasattr(test, bstack11l1l_opy_ (u"ࠥࡪࡸࡶࡡࡵࡪࠥᘆ")) and test.fspath else None
        if not bstack1lll1ll111_opy_ or not test_name or not bstack11llll111ll_opy_:
            return None
        code = None
        if hasattr(test, bstack11l1l_opy_ (u"ࠦࡴࡨࡪࠣᘇ")):
            try:
                import inspect
                code = inspect.getsource(test.obj)
            except:
                pass
        bstack11lll11l111_opy_ = []
        try:
            bstack11lll11l111_opy_ = bstack11llll111_opy_.bstack1111l1ll11_opy_(test)
        except:
            bstack1ll1l11llll_opy_.logger.warning(bstack11l1l_opy_ (u"࡛ࠧ࡮ࡢࡤ࡯ࡩࠥࡺ࡯ࠡࡨ࡬ࡲࡩࠦࡴࡦࡵࡷࠤࡸࡩ࡯ࡱࡧࡶ࠰ࠥࡺࡥࡴࡶࠣࡷࡨࡵࡰࡦࡵࠣࡻ࡮ࡲ࡬ࠡࡤࡨࠤࡷ࡫ࡳࡰ࡮ࡹࡩࡩࠦࡩ࡯ࠢࡆࡐࡎࠨᘈ"))
        return {
            TestFramework.bstack1ll11l11l1l_opy_: uuid4().__str__(),
            TestFramework.bstack1l11111lll1_opy_: bstack1lll1ll111_opy_,
            TestFramework.bstack1l1llll1ll1_opy_: test_name,
            TestFramework.bstack1l11lllll1l_opy_: getattr(test, bstack11l1l_opy_ (u"ࠨ࡮ࡰࡦࡨ࡭ࡩࠨᘉ"), None),
            TestFramework.bstack11llllll1ll_opy_: bstack11llll111ll_opy_,
            TestFramework.bstack1l11111111l_opy_: bstack1ll1l11llll_opy_.__11llll1ll11_opy_(test),
            TestFramework.bstack11lllll1lll_opy_: code,
            TestFramework.bstack1l11l1lllll_opy_: TestFramework.bstack1l11111l1l1_opy_,
            TestFramework.bstack1l111ll11ll_opy_: bstack1lll1ll111_opy_,
            TestFramework.bstack11lll11l11l_opy_: bstack11lll11l111_opy_
        }
    @staticmethod
    def __11llll1ll11_opy_(test) -> List[str]:
        markers = []
        current = test
        while current:
            own_markers = getattr(current, bstack11l1l_opy_ (u"ࠢࡰࡹࡱࡣࡲࡧࡲ࡬ࡧࡵࡷࠧᘊ"), [])
            markers.extend([getattr(m, bstack11l1l_opy_ (u"ࠣࡰࡤࡱࡪࠨᘋ"), None) for m in own_markers if getattr(m, bstack11l1l_opy_ (u"ࠤࡱࡥࡲ࡫ࠢᘌ"), None)])
            current = getattr(current, bstack11l1l_opy_ (u"ࠥࡴࡦࡸࡥ࡯ࡶࠥᘍ"), None)
        return markers
    @staticmethod
    def __11lll1lllll_opy_(location):
        return bstack11l1l_opy_ (u"ࠦ࠿ࡀࠢᘎ").join(filter(lambda x: isinstance(x, str), location))