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
from datetime import datetime, timezone
import os
import builtins
from pathlib import Path
from typing import Any, Tuple, Callable, List
from browserstack_sdk.sdk_cli.bstack1ll11l1l1l1_opy_ import bstack1ll1l1ll1l1_opy_, bstack1ll11lllll1_opy_, bstack1ll11lll1ll_opy_
from browserstack_sdk.sdk_cli.bstack1l1ll111111_opy_ import bstack1l1l1l111ll_opy_
from browserstack_sdk.sdk_cli.bstack1ll1111ll1l_opy_ import bstack1ll111ll1l1_opy_
from browserstack_sdk.sdk_cli.bstack1ll11l1lll1_opy_ import bstack1ll11ll1lll_opy_
from browserstack_sdk.sdk_cli.test_framework import TestFramework, bstack1llll1ll111_opy_, bstack1lll1l11l11_opy_, bstack1lll1111l11_opy_, bstack1lll1ll1lll_opy_
from json import dumps, JSONEncoder
import grpc
from browserstack_sdk import sdk_pb2 as structs
import sys
import traceback
import time
import json
from bstack_utils.helper import bstack1ll111l11l1_opy_, bstack1llll111l1l_opy_
from bstack_utils.measure import measure
from bstack_utils.constants import *
bstack11llllll111_opy_ = [bstack11ll1_opy_ (u"ࠦࡳࡧ࡭ࡦࠤᓡ"), bstack11ll1_opy_ (u"ࠧࡶࡡࡳࡧࡱࡸࠧᓢ"), bstack11ll1_opy_ (u"ࠨࡣࡰࡰࡩ࡭࡬ࠨᓣ"), bstack11ll1_opy_ (u"ࠢࡴࡧࡶࡷ࡮ࡵ࡮ࠣᓤ"), bstack11ll1_opy_ (u"ࠣࡲࡤࡸ࡭ࠨᓥ")]
bstack1lll11lll1l_opy_ = bstack1llll111l1l_opy_()
bstack1ll1ll1l11l_opy_ = bstack11ll1_opy_ (u"ࠤࡘࡴࡱࡵࡡࡥࡧࡧࡅࡹࡺࡡࡤࡪࡰࡩࡳࡺࡳ࠮ࠤᓦ")
bstack1l111111lll_opy_ = {
    bstack11ll1_opy_ (u"ࠥࡴࡾࡺࡥࡴࡶ࠱ࡴࡾࡺࡨࡰࡰ࠱ࡍࡹ࡫࡭ࠣᓧ"): bstack11llllll111_opy_,
    bstack11ll1_opy_ (u"ࠦࡵࡿࡴࡦࡵࡷ࠲ࡵࡿࡴࡩࡱࡱ࠲ࡕࡧࡣ࡬ࡣࡪࡩࠧᓨ"): bstack11llllll111_opy_,
    bstack11ll1_opy_ (u"ࠧࡶࡹࡵࡧࡶࡸ࠳ࡶࡹࡵࡪࡲࡲ࠳ࡓ࡯ࡥࡷ࡯ࡩࠧᓩ"): bstack11llllll111_opy_,
    bstack11ll1_opy_ (u"ࠨࡰࡺࡶࡨࡷࡹ࠴ࡰࡺࡶ࡫ࡳࡳ࠴ࡃ࡭ࡣࡶࡷࠧᓪ"): bstack11llllll111_opy_,
    bstack11ll1_opy_ (u"ࠢࡱࡻࡷࡩࡸࡺ࠮ࡱࡻࡷ࡬ࡴࡴ࠮ࡇࡷࡱࡧࡹ࡯࡯࡯ࠤᓫ"): bstack11llllll111_opy_
    + [
        bstack11ll1_opy_ (u"ࠣࡱࡵ࡭࡬࡯࡮ࡢ࡮ࡱࡥࡲ࡫ࠢᓬ"),
        bstack11ll1_opy_ (u"ࠤ࡮ࡩࡾࡽ࡯ࡳࡦࡶࠦᓭ"),
        bstack11ll1_opy_ (u"ࠥࡪ࡮ࡾࡴࡶࡴࡨ࡭ࡳ࡬࡯ࠣᓮ"),
        bstack11ll1_opy_ (u"ࠦࡰ࡫ࡹࡸࡱࡵࡨࡸࠨᓯ"),
        bstack11ll1_opy_ (u"ࠧࡩࡡ࡭࡮ࡶࡴࡪࡩࠢᓰ"),
        bstack11ll1_opy_ (u"ࠨࡣࡢ࡮࡯ࡳࡧࡰࠢᓱ"),
        bstack11ll1_opy_ (u"ࠢࡴࡶࡤࡶࡹࠨᓲ"),
        bstack11ll1_opy_ (u"ࠣࡵࡷࡳࡵࠨᓳ"),
        bstack11ll1_opy_ (u"ࠤࡧࡹࡷࡧࡴࡪࡱࡱࠦᓴ"),
        bstack11ll1_opy_ (u"ࠥࡻ࡭࡫࡮ࠣᓵ"),
    ],
    bstack11ll1_opy_ (u"ࠦࡵࡿࡴࡦࡵࡷ࠲ࡲࡧࡩ࡯࠰ࡖࡩࡸࡹࡩࡰࡰࠥᓶ"): [bstack11ll1_opy_ (u"ࠧࡹࡴࡢࡴࡷࡴࡦࡺࡨࠣᓷ"), bstack11ll1_opy_ (u"ࠨࡴࡦࡵࡷࡷ࡫ࡧࡩ࡭ࡧࡧࠦᓸ"), bstack11ll1_opy_ (u"ࠢࡵࡧࡶࡸࡸࡩ࡯࡭࡮ࡨࡧࡹ࡫ࡤࠣᓹ"), bstack11ll1_opy_ (u"ࠣ࡫ࡷࡩࡲࡹࠢᓺ")],
    bstack11ll1_opy_ (u"ࠤࡳࡽࡹ࡫ࡳࡵ࠰ࡦࡳࡳ࡬ࡩࡨ࠰ࡆࡳࡳ࡬ࡩࡨࠤᓻ"): [bstack11ll1_opy_ (u"ࠥ࡭ࡳࡼ࡯ࡤࡣࡷ࡭ࡴࡴ࡟ࡱࡣࡵࡥࡲࡹࠢᓼ"), bstack11ll1_opy_ (u"ࠦࡦࡸࡧࡴࠤᓽ")],
    bstack11ll1_opy_ (u"ࠧࡶࡹࡵࡧࡶࡸ࠳࡬ࡩࡹࡶࡸࡶࡪࡹ࠮ࡇ࡫ࡻࡸࡺࡸࡥࡅࡧࡩࠦᓾ"): [bstack11ll1_opy_ (u"ࠨࡳࡤࡱࡳࡩࠧᓿ"), bstack11ll1_opy_ (u"ࠢࡢࡴࡪࡲࡦࡳࡥࠣᔀ"), bstack11ll1_opy_ (u"ࠣࡨࡸࡲࡨࠨᔁ"), bstack11ll1_opy_ (u"ࠤࡳࡥࡷࡧ࡭ࡴࠤᔂ"), bstack11ll1_opy_ (u"ࠥࡹࡳ࡯ࡴࡵࡧࡶࡸࠧᔃ"), bstack11ll1_opy_ (u"ࠦ࡮ࡪࡳࠣᔄ")],
    bstack11ll1_opy_ (u"ࠧࡶࡹࡵࡧࡶࡸ࠳࡬ࡩࡹࡶࡸࡶࡪࡹ࠮ࡔࡷࡥࡖࡪࡷࡵࡦࡵࡷࠦᔅ"): [bstack11ll1_opy_ (u"ࠨࡦࡪࡺࡷࡹࡷ࡫࡮ࡢ࡯ࡨࠦᔆ"), bstack11ll1_opy_ (u"ࠢࡱࡣࡵࡥࡲࠨᔇ"), bstack11ll1_opy_ (u"ࠣࡲࡤࡶࡦࡳ࡟ࡪࡰࡧࡩࡽࠨᔈ")],
    bstack11ll1_opy_ (u"ࠤࡳࡽࡹ࡫ࡳࡵ࠰ࡵࡹࡳࡴࡥࡳ࠰ࡆࡥࡱࡲࡉ࡯ࡨࡲࠦᔉ"): [bstack11ll1_opy_ (u"ࠥࡻ࡭࡫࡮ࠣᔊ"), bstack11ll1_opy_ (u"ࠦࡷ࡫ࡳࡶ࡮ࡷࠦᔋ")],
    bstack11ll1_opy_ (u"ࠧࡶࡹࡵࡧࡶࡸ࠳ࡳࡡࡳ࡭࠱ࡷࡹࡸࡵࡤࡶࡸࡶࡪࡹ࠮ࡏࡱࡧࡩࡐ࡫ࡹࡸࡱࡵࡨࡸࠨᔌ"): [bstack11ll1_opy_ (u"ࠨ࡮ࡰࡦࡨࠦᔍ"), bstack11ll1_opy_ (u"ࠢࡱࡣࡵࡩࡳࡺࠢᔎ")],
    bstack11ll1_opy_ (u"ࠣࡲࡼࡸࡪࡹࡴ࠯࡯ࡤࡶࡰ࠴ࡳࡵࡴࡸࡧࡹࡻࡲࡦࡵ࠱ࡑࡦࡸ࡫ࠣᔏ"): [bstack11ll1_opy_ (u"ࠤࡱࡥࡲ࡫ࠢᔐ"), bstack11ll1_opy_ (u"ࠥࡥࡷ࡭ࡳࠣᔑ"), bstack11ll1_opy_ (u"ࠦࡰࡽࡡࡳࡩࡶࠦᔒ")],
}
_1lll111l1l1_opy_ = set()
class bstack1l1ll11ll11_opy_(bstack1l1l1l111ll_opy_):
    bstack1l1111lll11_opy_ = bstack11ll1_opy_ (u"ࠧࡺࡥࡴࡶࡢࡨࡪ࡬ࡥࡳࡴࡨࡨࠧᔓ")
    bstack1l111111l1l_opy_ = bstack11ll1_opy_ (u"ࠨࡉࡏࡈࡒࠦᔔ")
    bstack1l1111111ll_opy_ = bstack11ll1_opy_ (u"ࠢࡆࡔࡕࡓࡗࠨᔕ")
    bstack1l11111l1ll_opy_: Callable
    bstack1l1111ll1l1_opy_: Callable
    def __init__(self, bstack1l1l11l11ll_opy_, bstack1l1l1l1l1l1_opy_):
        super().__init__()
        self.bstack1l11l111ll1_opy_ = bstack1l1l1l1l1l1_opy_
        if os.getenv(bstack11ll1_opy_ (u"ࠣࡕࡇࡏࡤࡉࡌࡊࡡࡉࡐࡆࡍ࡟ࡐ࠳࠴࡝ࠧᔖ"), bstack11ll1_opy_ (u"ࠤ࠴ࠦᔗ")) != bstack11ll1_opy_ (u"ࠥ࠵ࠧᔘ") or not self.is_enabled():
            self.logger.warning(bstack11ll1_opy_ (u"ࠦࠧᔙ") + str(self.__class__.__name__) + bstack11ll1_opy_ (u"ࠧࠦࡤࡪࡵࡤࡦࡱ࡫ࡤࠣᔚ"))
            return
        TestFramework.bstack1ll1l11111l_opy_((bstack1llll1ll111_opy_.TEST, bstack1lll1111l11_opy_.PRE), self.bstack1ll11l11111_opy_)
        TestFramework.bstack1ll1l11111l_opy_((bstack1llll1ll111_opy_.TEST, bstack1lll1111l11_opy_.POST), self.bstack1l1llllll1l_opy_)
        for event in bstack1llll1ll111_opy_:
            for state in bstack1lll1111l11_opy_:
                TestFramework.bstack1ll1l11111l_opy_((event, state), self.bstack1l111l11111_opy_)
        bstack1l1l11l11ll_opy_.bstack1ll1l11111l_opy_((bstack1ll11lllll1_opy_.bstack1ll11l1l1ll_opy_, bstack1ll11lll1ll_opy_.POST), self.bstack1l111111l11_opy_)
        self.bstack1l11111l1ll_opy_ = sys.stdout.write
        sys.stdout.write = self.bstack1l1111lllll_opy_(bstack1l1ll11ll11_opy_.bstack1l111111l1l_opy_, self.bstack1l11111l1ll_opy_)
        self.bstack1l1111ll1l1_opy_ = sys.stderr.write
        sys.stderr.write = self.bstack1l1111lllll_opy_(bstack1l1ll11ll11_opy_.bstack1l1111111ll_opy_, self.bstack1l1111ll1l1_opy_)
        self.bstack1l111111ll1_opy_ = builtins.print
        builtins.print = self.bstack1l1111l1l1l_opy_()
    def is_enabled(self) -> bool:
        return True
    def bstack1l111l11111_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll1l11l11_opy_,
        bstack1lll1lll111_opy_: Tuple[bstack1llll1ll111_opy_, bstack1lll1111l11_opy_],
        *args,
        **kwargs,
    ):
        if f.bstack1lllll11111_opy_() and instance:
            bstack11lllll1lll_opy_ = datetime.now()
            test_framework_state, test_hook_state = bstack1lll1lll111_opy_
            if test_framework_state == bstack1llll1ll111_opy_.SETUP_FIXTURE:
                return
            elif test_framework_state == bstack1llll1ll111_opy_.LOG:
                bstack1ll11l1l1l_opy_ = datetime.now()
                entries = f.bstack1lll1lll11l_opy_(instance, bstack1lll1lll111_opy_)
                if entries:
                    self.bstack1lll1l11ll1_opy_(instance, entries)
                    instance.bstack1lll1lll1_opy_(bstack11ll1_opy_ (u"ࠨࡧࡳࡲࡦ࠾ࡸ࡫࡮ࡥࡡ࡯ࡳ࡬ࡥࡣࡳࡧࡤࡸࡪࡪ࡟ࡦࡸࡨࡲࡹࠨᔛ"), datetime.now() - bstack1ll11l1l1l_opy_)
                    f.bstack1lll11l1l11_opy_(instance, bstack1lll1lll111_opy_)
                instance.bstack1lll1lll1_opy_(bstack11ll1_opy_ (u"ࠢࡰ࠳࠴ࡽ࠿ࡵ࡮ࡠࡣ࡯ࡰࡤࡺࡥࡴࡶࡢࡩࡻ࡫࡮ࡵࡵࠥᔜ"), datetime.now() - bstack11lllll1lll_opy_)
                return # bstack1l11111l1l1_opy_ not send this event with the bstack1l11111l11l_opy_ bstack1l1111l11l1_opy_
            elif (
                test_framework_state == bstack1llll1ll111_opy_.TEST
                and test_hook_state == bstack1lll1111l11_opy_.POST
                and not f.bstack1lll1ll1ll1_opy_(instance, TestFramework.bstack1llll1llll1_opy_)
            ):
                self.logger.warning(bstack11ll1_opy_ (u"ࠣࡦࡵࡳࡵࡶࡩ࡯ࡩࠣࡨࡺ࡫ࠠࡵࡱࠣࡰࡦࡩ࡫ࠡࡱࡩࠤࡷ࡫ࡳࡶ࡮ࡷࡷࠥࠨᔝ") + str(TestFramework.bstack1lll1ll1ll1_opy_(instance, TestFramework.bstack1llll1llll1_opy_)) + bstack11ll1_opy_ (u"ࠤࠥᔞ"))
                f.bstack1lll111ll11_opy_(instance, bstack1l1ll11ll11_opy_.bstack1l1111lll11_opy_, True)
                return # bstack1l11111l1l1_opy_ not send this event bstack11lllllll1l_opy_ bstack1l11111111l_opy_
            elif (
                f.bstack1ll1llll11l_opy_(instance, bstack1l1ll11ll11_opy_.bstack1l1111lll11_opy_, False)
                and test_framework_state == bstack1llll1ll111_opy_.LOG_REPORT
                and test_hook_state == bstack1lll1111l11_opy_.POST
                and f.bstack1lll1ll1ll1_opy_(instance, TestFramework.bstack1llll1llll1_opy_)
            ):
                self.logger.warning(bstack11ll1_opy_ (u"ࠥ࡭ࡳࡰࡥࡤࡶ࡬ࡲ࡬ࠦࡔࡦࡵࡷࡊࡷࡧ࡭ࡦࡹࡲࡶࡰ࡙ࡴࡢࡶࡨ࠲࡙ࡋࡓࡕ࠮ࠣࡘࡪࡹࡴࡉࡱࡲ࡯ࡘࡺࡡࡵࡧ࠱ࡔࡔ࡙ࡔࠡࠤᔟ") + str(TestFramework.bstack1lll1ll1ll1_opy_(instance, TestFramework.bstack1llll1llll1_opy_)) + bstack11ll1_opy_ (u"ࠦࠧᔠ"))
                self.bstack1l111l11111_opy_(f, instance, (bstack1llll1ll111_opy_.TEST, bstack1lll1111l11_opy_.POST), *args, **kwargs)
            bstack1ll11l1l1l_opy_ = datetime.now()
            data = instance.data.copy()
            bstack11lllll1ll1_opy_ = sorted(
                filter(lambda x: x.get(bstack11ll1_opy_ (u"ࠧ࡫ࡶࡦࡰࡷࡣࡸࡺࡡࡳࡶࡨࡨࡤࡧࡴࠣᔡ"), None), data.pop(bstack11ll1_opy_ (u"ࠨࡴࡦࡵࡷࡣ࡫࡯ࡸࡵࡷࡵࡩࡸࠨᔢ"), {}).values()),
                key=lambda x: x[bstack11ll1_opy_ (u"ࠢࡦࡸࡨࡲࡹࡥࡳࡵࡣࡵࡸࡪࡪ࡟ࡢࡶࠥᔣ")],
            )
            if bstack1ll111ll1l1_opy_.bstack1ll111lllll_opy_ in data:
                data.pop(bstack1ll111ll1l1_opy_.bstack1ll111lllll_opy_)
            data.update({bstack11ll1_opy_ (u"ࠣࡶࡨࡷࡹࡥࡦࡪࡺࡷࡹࡷ࡫ࡳࠣᔤ"): bstack11lllll1ll1_opy_})
            instance.bstack1lll1lll1_opy_(bstack11ll1_opy_ (u"ࠤ࡭ࡷࡴࡴ࠺ࡵࡧࡶࡸࡤ࡬ࡩࡹࡶࡸࡶࡪࡹࠢᔥ"), datetime.now() - bstack1ll11l1l1l_opy_)
            bstack1ll11l1l1l_opy_ = datetime.now()
            event_json = dumps(data, cls=bstack1l1111ll111_opy_)
            instance.bstack1lll1lll1_opy_(bstack11ll1_opy_ (u"ࠥ࡮ࡸࡵ࡮࠻ࡱࡱࡣࡦࡲ࡬ࡠࡶࡨࡷࡹࡥࡥࡷࡧࡱࡸࡸࠨᔦ"), datetime.now() - bstack1ll11l1l1l_opy_)
            self.bstack1l1111l11l1_opy_(instance, bstack1lll1lll111_opy_, event_json=event_json)
            instance.bstack1lll1lll1_opy_(bstack11ll1_opy_ (u"ࠦࡴ࠷࠱ࡺ࠼ࡲࡲࡤࡧ࡬࡭ࡡࡷࡩࡸࡺ࡟ࡦࡸࡨࡲࡹࡹࠢᔧ"), datetime.now() - bstack11lllll1lll_opy_)
    def bstack1ll11l11111_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll1l11l11_opy_,
        bstack1lll1lll111_opy_: Tuple[bstack1llll1ll111_opy_, bstack1lll1111l11_opy_],
        *args,
        **kwargs,
    ):
        from bstack_utils.bstack11l11l11ll_opy_ import bstack1lll111111l_opy_
        bstack1lll1l1ll11_opy_ = bstack1lll111111l_opy_.bstack1lll1111lll_opy_(EVENTS.bstack11llll1l_opy_.value)
        self.bstack1l11l111ll1_opy_.bstack1ll11111l11_opy_(instance, f, bstack1lll1lll111_opy_, *args, **kwargs)
        req = self.bstack1l11l111ll1_opy_.bstack1ll111l11ll_opy_(instance, f, bstack1lll1lll111_opy_, *args, **kwargs)
        self.bstack1l11111ll1l_opy_(f, instance, req)
        bstack1lll111111l_opy_.end(EVENTS.bstack11llll1l_opy_.value, bstack1lll1l1ll11_opy_ + bstack11ll1_opy_ (u"ࠧࡀࡳࡵࡣࡵࡸࠧᔨ"), bstack1lll1l1ll11_opy_ + bstack11ll1_opy_ (u"ࠨ࠺ࡦࡰࡧࠦᔩ"), status=True, failure=None, test_name=None)
    def bstack1l1llllll1l_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll1l11l11_opy_,
        bstack1lll1lll111_opy_: Tuple[bstack1llll1ll111_opy_, bstack1lll1111l11_opy_],
        *args,
        **kwargs,
    ):
        if not f.bstack1ll1llll11l_opy_(instance, self.bstack1l11l111ll1_opy_.bstack1l1llllllll_opy_, False):
            req = self.bstack1l11l111ll1_opy_.bstack1ll111l11ll_opy_(instance, f, bstack1lll1lll111_opy_, *args, **kwargs)
            self.bstack1l11111ll1l_opy_(f, instance, req)
    @measure(event_name=EVENTS.bstack1l11111l111_opy_, stage=STAGE.bstack11l1llll1_opy_)
    def bstack1l11111ll1l_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll1l11l11_opy_,
        req: structs.TestSessionEventRequest
    ):
        if not req:
            self.logger.debug(bstack11ll1_opy_ (u"ࠢࡔ࡭࡬ࡴࡵ࡯࡮ࡨࠢࡗࡩࡸࡺࡓࡦࡵࡶ࡭ࡴࡴࡅࡷࡧࡱࡸࠥ࡭ࡒࡑࡅࠣࡧࡦࡲ࡬࠻ࠢࡑࡳࠥࡼࡡ࡭࡫ࡧࠤࡷ࡫ࡱࡶࡧࡶࡸࠥࡪࡡࡵࡣࠥᔪ"))
            return
        bstack1ll11l1l1l_opy_ = datetime.now()
        try:
            r = self.bstack1lllll11ll1_opy_.TestSessionEvent(req)
            instance.bstack1lll1lll1_opy_(bstack11ll1_opy_ (u"ࠣࡩࡵࡴࡨࡀࡳࡦࡰࡧࡣࡹ࡫ࡳࡵࡡࡶࡩࡸࡹࡩࡰࡰࡢࡩࡻ࡫࡮ࡵࠤᔫ"), datetime.now() - bstack1ll11l1l1l_opy_)
            f.bstack1lll111ll11_opy_(instance, self.bstack1l11l111ll1_opy_.bstack1l1llllllll_opy_, r.success)
            if not r.success:
                self.logger.info(bstack11ll1_opy_ (u"ࠤࡵࡩࡨ࡫ࡩࡷࡧࡧࠤ࡫ࡸ࡯࡮ࠢࡶࡩࡷࡼࡥࡳ࠼ࠣࠦᔬ") + str(r) + bstack11ll1_opy_ (u"ࠥࠦᔭ"))
        except grpc.RpcError as e:
            self.logger.error(bstack11ll1_opy_ (u"ࠦࡷࡶࡣ࠮ࡧࡵࡶࡴࡸ࠺ࠡࠤᔮ") + str(e) + bstack11ll1_opy_ (u"ࠧࠨᔯ"))
            traceback.print_exc()
            raise e
    def bstack1l111111l11_opy_(
        self,
        f: bstack1ll11ll1lll_opy_,
        _driver: object,
        exec: Tuple[bstack1ll1l1ll1l1_opy_, str],
        _1l1111l1ll1_opy_: Tuple[bstack1ll11lllll1_opy_, bstack1ll11lll1ll_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if not bstack1ll11ll1lll_opy_.bstack1ll1l1ll1ll_opy_(method_name):
            return
        if f.bstack1ll11l1l111_opy_(*args) == bstack1ll11ll1lll_opy_.bstack1ll1l1ll11l_opy_:
            bstack11lllll1lll_opy_ = datetime.now()
            screenshot = result.get(bstack11ll1_opy_ (u"ࠨࡶࡢ࡮ࡸࡩࠧᔰ"), None) if isinstance(result, dict) else None
            if not isinstance(screenshot, str) or len(screenshot) <= 0:
                self.logger.warning(bstack11ll1_opy_ (u"ࠢࡪࡰࡹࡥࡱ࡯ࡤࠡࡵࡦࡶࡪ࡫࡮ࡴࡪࡲࡸࠥ࡯࡭ࡢࡩࡨࠤࡧࡧࡳࡦ࠸࠷ࠤࡸࡺࡲࠣᔱ"))
                return
            bstack1ll1lll11l1_opy_ = self.bstack1l1111l1lll_opy_(instance)
            if bstack1ll1lll11l1_opy_:
                entry = bstack1lll1ll1lll_opy_(TestFramework.bstack1l11111llll_opy_, screenshot)
                self.bstack1lll1l11ll1_opy_(bstack1ll1lll11l1_opy_, [entry])
                instance.bstack1lll1lll1_opy_(bstack11ll1_opy_ (u"ࠣࡱ࠴࠵ࡾࡀ࡯࡯ࡡࡤࡪࡹ࡫ࡲࡠࡧࡻࡩࡨࡻࡴࡦࠤᔲ"), datetime.now() - bstack11lllll1lll_opy_)
            else:
                self.logger.warning(bstack11ll1_opy_ (u"ࠤࡸࡲࡦࡨ࡬ࡦࠢࡷࡳࠥࡪࡥࡵࡧࡵࡱ࡮ࡴࡥࠡࡶࡨࡷࡹࠦࡦࡰࡴࠣࡻ࡭࡯ࡣࡩࠢࡷ࡬࡮ࡹࠠࡴࡥࡵࡩࡪࡴࡳࡩࡱࡷࠤࡼࡧࡳࠡࡶࡤ࡯ࡪࡴࠠࡣࡻࠣࡨࡷ࡯ࡶࡦࡴࡀࠤࢀࢃࠢᔳ").format(instance.ref()))
        event = {}
        bstack1ll1lll11l1_opy_ = self.bstack1l1111l1lll_opy_(instance)
        if bstack1ll1lll11l1_opy_:
            self.bstack1l1111l1111_opy_(event, bstack1ll1lll11l1_opy_)
            if event.get(bstack11ll1_opy_ (u"ࠥࡰࡴ࡭ࡳࠣᔴ")):
                self.bstack1lll1l11ll1_opy_(bstack1ll1lll11l1_opy_, event[bstack11ll1_opy_ (u"ࠦࡱࡵࡧࡴࠤᔵ")])
            else:
                self.logger.debug(bstack11ll1_opy_ (u"࡛ࠧ࡮ࡢࡤ࡯ࡩࠥࡺ࡯ࠡࡦࡨࡸࡪࡸ࡭ࡪࡰࡨࠤࡱࡵࡧࡴࠢࡩࡳࡷࠦࡡࡵࡶࡤࡧ࡭ࡳࡥ࡯ࡶࠣࡩࡻ࡫࡮ࡵࠤᔶ"))
    @measure(event_name=EVENTS.bstack1l1111l1l11_opy_, stage=STAGE.bstack11l1llll1_opy_)
    def bstack1lll1l11ll1_opy_(
        self,
        bstack1ll1lll11l1_opy_: bstack1lll1l11l11_opy_,
        entries: List[bstack1lll1ll1lll_opy_],
    ):
        self.bstack1ll111111l1_opy_()
        req = structs.LogCreatedEventRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = TestFramework.bstack1ll1llll11l_opy_(bstack1ll1lll11l1_opy_, TestFramework.bstack1lll11l1l1l_opy_)
        req.execution_context.hash = str(bstack1ll1lll11l1_opy_.context.hash)
        req.execution_context.thread_id = str(bstack1ll1lll11l1_opy_.context.thread_id)
        req.execution_context.process_id = str(bstack1ll1lll11l1_opy_.context.process_id)
        for entry in entries:
            log_entry = req.logs.add()
            log_entry.test_framework_name = TestFramework.bstack1ll1llll11l_opy_(bstack1ll1lll11l1_opy_, TestFramework.bstack1lll1111111_opy_)
            log_entry.test_framework_version = TestFramework.bstack1ll1llll11l_opy_(bstack1ll1lll11l1_opy_, TestFramework.bstack1lll11111ll_opy_)
            log_entry.uuid = TestFramework.bstack1ll1llll11l_opy_(bstack1ll1lll11l1_opy_, TestFramework.bstack1llll111ll1_opy_)
            log_entry.test_framework_state = bstack1ll1lll11l1_opy_.state.name
            log_entry.message = entry.message.encode(bstack11ll1_opy_ (u"ࠨࡵࡵࡨ࠰࠼ࠧᔷ"))
            log_entry.kind = entry.kind
            log_entry.timestamp = (
                entry.timestamp.isoformat()
                if isinstance(entry.timestamp, datetime)
                else datetime.now(tz=timezone.utc).isoformat()
            )
            if isinstance(entry.level, str) and len(entry.level.strip()) > 0:
                log_entry.level = entry.level.strip()
            if entry.kind == bstack11ll1_opy_ (u"ࠢࡕࡇࡖࡘࡤࡇࡔࡕࡃࡆࡌࡒࡋࡎࡕࠤᔸ"):
                log_entry.file_name = entry.fileName
                log_entry.file_size = entry.bstack1llll1lll11_opy_
                log_entry.file_path = entry.bstack1ll11l_opy_
        def bstack1llll1ll1l1_opy_():
            bstack1ll11l1l1l_opy_ = datetime.now()
            try:
                self.bstack1lllll11ll1_opy_.LogCreatedEvent(req)
                if entry.kind == TestFramework.bstack1l11111llll_opy_:
                    bstack1ll1lll11l1_opy_.bstack1lll1lll1_opy_(bstack11ll1_opy_ (u"ࠣࡩࡵࡴࡨࡀࡳࡦࡰࡧࡣࡱࡵࡧࡠࡥࡵࡩࡦࡺࡥࡥࡡࡨࡺࡪࡴࡴࡠࡵࡦࡶࡪ࡫࡮ࡴࡪࡲࡸࠧᔹ"), datetime.now() - bstack1ll11l1l1l_opy_)
                elif entry.kind == TestFramework.bstack1l111111111_opy_:
                    bstack1ll1lll11l1_opy_.bstack1lll1lll1_opy_(bstack11ll1_opy_ (u"ࠤࡪࡶࡵࡩ࠺ࡴࡧࡱࡨࡤࡲ࡯ࡨࡡࡦࡶࡪࡧࡴࡦࡦࡢࡩࡻ࡫࡮ࡵࡡࡤࡸࡹࡧࡣࡩ࡯ࡨࡲࡹࠨᔺ"), datetime.now() - bstack1ll11l1l1l_opy_)
                else:
                    bstack1ll1lll11l1_opy_.bstack1lll1lll1_opy_(bstack11ll1_opy_ (u"ࠥ࡫ࡷࡶࡣ࠻ࡵࡨࡲࡩࡥ࡬ࡰࡩࡢࡧࡷ࡫ࡡࡵࡧࡧࡣࡪࡼࡥ࡯ࡶࡢࡰࡴ࡭ࠢᔻ"), datetime.now() - bstack1ll11l1l1l_opy_)
            except grpc.RpcError as e:
                self.log_error(bstack11ll1_opy_ (u"ࠦࡷࡶࡣ࠮ࡧࡵࡶࡴࡸ࠺ࠡࠤᔼ") + str(e))
                traceback.print_exc()
                raise e
        self.bstack1lll1l1llll_opy_.enqueue(bstack1llll1ll1l1_opy_)
    @measure(event_name=EVENTS.bstack1l1111ll1ll_opy_, stage=STAGE.bstack11l1llll1_opy_)
    def bstack1l1111l11l1_opy_(
        self,
        instance: bstack1lll1l11l11_opy_,
        bstack1lll1lll111_opy_: Tuple[bstack1llll1ll111_opy_, bstack1lll1111l11_opy_],
        event_json=None,
    ):
        self.bstack1ll111111l1_opy_()
        req = structs.TestFrameworkEventRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = TestFramework.bstack1ll1llll11l_opy_(instance, TestFramework.bstack1lll11l1l1l_opy_)
        req.test_framework_name = TestFramework.bstack1ll1llll11l_opy_(instance, TestFramework.bstack1lll1111111_opy_)
        req.test_framework_version = TestFramework.bstack1ll1llll11l_opy_(instance, TestFramework.bstack1lll11111ll_opy_)
        req.test_framework_state = bstack1lll1lll111_opy_[0].name
        req.test_hook_state = bstack1lll1lll111_opy_[1].name
        started_at = TestFramework.bstack1ll1llll11l_opy_(instance, TestFramework.bstack1lllll1111l_opy_, None)
        if started_at:
            req.started_at = started_at.isoformat()
        ended_at = TestFramework.bstack1ll1llll11l_opy_(instance, TestFramework.bstack1lll1ll111l_opy_, None)
        if ended_at:
            req.ended_at = ended_at.isoformat()
        req.uuid = instance.ref()
        req.event_json = (event_json if event_json else dumps(instance.data, cls=bstack1l1111ll111_opy_)).encode(bstack11ll1_opy_ (u"ࠧࡻࡴࡧ࠯࠻ࠦᔽ"))
        req.execution_context.hash = str(instance.context.hash)
        req.execution_context.thread_id = str(instance.context.thread_id)
        req.execution_context.process_id = str(instance.context.process_id)
        def bstack1llll1ll1l1_opy_():
            bstack1ll11l1l1l_opy_ = datetime.now()
            try:
                self.bstack1lllll11ll1_opy_.TestFrameworkEvent(req)
                instance.bstack1lll1lll1_opy_(bstack11ll1_opy_ (u"ࠨࡧࡳࡲࡦ࠾ࡸ࡫࡮ࡥࡡࡷࡩࡸࡺ࡟ࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡢࡩࡻ࡫࡮ࡵࠤᔾ"), datetime.now() - bstack1ll11l1l1l_opy_)
            except grpc.RpcError as e:
                self.log_error(bstack11ll1_opy_ (u"ࠢࡳࡲࡦ࠱ࡪࡸࡲࡰࡴ࠽ࠤࠧᔿ") + str(e))
                traceback.print_exc()
                raise e
        self.bstack1lll1l1llll_opy_.enqueue(bstack1llll1ll1l1_opy_)
    def bstack1l1111l1lll_opy_(self, instance: bstack1ll1l1ll1l1_opy_):
        bstack11lllllll11_opy_ = TestFramework.bstack1l1lll11l11_opy_(instance.context)
        for t in bstack11lllllll11_opy_:
            bstack1ll111l1111_opy_ = TestFramework.bstack1ll1llll11l_opy_(t, bstack1ll111ll1l1_opy_.bstack1ll111lllll_opy_, [])
            if any(instance is d[1] for d in bstack1ll111l1111_opy_):
                return t
    def bstack1l1111ll11l_opy_(self, message):
        self.bstack1l11111l1ll_opy_(message + bstack11ll1_opy_ (u"ࠣ࡞ࡱࠦᕀ"))
    def log_error(self, message):
        self.bstack1l1111ll1l1_opy_(message + bstack11ll1_opy_ (u"ࠤ࡟ࡲࠧᕁ"))
    def bstack1l1111lllll_opy_(self, level, original_func):
        def bstack11lllllllll_opy_(*args):
            try:
                try:
                    return_value = original_func(*args)
                except Exception:
                    return None
                try:
                    if not args or not isinstance(args[0], str) or not args[0].strip():
                        return return_value
                    message = args[0].strip()
                    if bstack11ll1_opy_ (u"ࠥࡉࡻ࡫࡮ࡵࡆ࡬ࡷࡵࡧࡴࡤࡪࡨࡶࡒࡵࡤࡶ࡮ࡨࠦᕂ") in message or bstack11ll1_opy_ (u"ࠦࡠ࡙ࡄࡌࡅࡏࡍࡢࠨᕃ") in message or bstack11ll1_opy_ (u"ࠧࡡࡗࡦࡤࡇࡶ࡮ࡼࡥࡳࡏࡲࡨࡺࡲࡥ࡞ࠤᕄ") in message:
                        return return_value
                    bstack11lllllll11_opy_ = TestFramework.bstack1l1111llll1_opy_()
                    if not bstack11lllllll11_opy_:
                        return return_value
                    bstack1ll1lll11l1_opy_ = next(
                        (
                            instance
                            for instance in bstack11lllllll11_opy_
                            if TestFramework.bstack1lll1ll1ll1_opy_(instance, TestFramework.bstack1llll111ll1_opy_)
                        ),
                        None,
                    )
                    if not bstack1ll1lll11l1_opy_:
                        return return_value
                    entry = bstack1lll1ll1lll_opy_(TestFramework.bstack1lll1l111l1_opy_, message, level)
                    self.bstack1lll1l11ll1_opy_(bstack1ll1lll11l1_opy_, [entry])
                except Exception:
                    pass
                return return_value
            except Exception:
                return None
        return bstack11lllllllll_opy_
    def bstack1l1111l1l1l_opy_(self):
        def bstack1l11111lll1_opy_(*args, **kwargs):
            try:
                self.bstack1l111111ll1_opy_(*args, **kwargs)
                if not args:
                    return
                message = bstack11ll1_opy_ (u"࠭ࠠࠨᕅ").join(str(arg) for arg in args)
                if not message.strip():
                    return
                if bstack11ll1_opy_ (u"ࠢࡆࡸࡨࡲࡹࡊࡩࡴࡲࡤࡸࡨ࡮ࡥࡳࡏࡲࡨࡺࡲࡥࠣᕆ") in message:
                    return
                bstack11lllllll11_opy_ = TestFramework.bstack1l1111llll1_opy_()
                if not bstack11lllllll11_opy_:
                    return
                bstack1ll1lll11l1_opy_ = next(
                    (
                        instance
                        for instance in bstack11lllllll11_opy_
                        if TestFramework.bstack1lll1ll1ll1_opy_(instance, TestFramework.bstack1llll111ll1_opy_)
                    ),
                    None,
                )
                if not bstack1ll1lll11l1_opy_:
                    return
                entry = bstack1lll1ll1lll_opy_(TestFramework.bstack1lll1l111l1_opy_, message, bstack1l1ll11ll11_opy_.bstack1l111111l1l_opy_)
                self.bstack1lll1l11ll1_opy_(bstack1ll1lll11l1_opy_, [entry])
            except Exception as e:
                try:
                    self.bstack1l111111ll1_opy_(bstack1l1ll111l1l_opy_ (u"ࠣ࡝ࡈࡺࡪࡴࡴࡅ࡫ࡶࡴࡦࡺࡣࡩࡧࡵࡑࡴࡪࡵ࡭ࡧࡠࠤࡑࡵࡧࠡࡥࡤࡴࡹࡻࡲࡦࠢࡨࡶࡷࡵࡲ࠻ࠢࡾࡩࢂࠨᕇ"))
                except:
                    pass
        return bstack1l11111lll1_opy_
    def bstack1l1111l1111_opy_(self, event: dict, instance=None) -> None:
        global _1lll111l1l1_opy_
        levels = [bstack11ll1_opy_ (u"ࠤࡗࡩࡸࡺࡌࡦࡸࡨࡰࠧᕈ"), bstack11ll1_opy_ (u"ࠥࡆࡺ࡯࡬ࡥࡎࡨࡺࡪࡲࠢᕉ")]
        bstack1l11111ll11_opy_ = bstack11ll1_opy_ (u"ࠦࠧᕊ")
        if instance is not None:
            try:
                bstack1l11111ll11_opy_ = TestFramework.bstack1ll1llll11l_opy_(instance, TestFramework.bstack1llll111ll1_opy_)
            except Exception as e:
                self.logger.warning(bstack11ll1_opy_ (u"ࠧࡋࡲࡳࡱࡵࠤ࡬࡫ࡴࡵ࡫ࡱ࡫ࠥࡻࡵࡪࡦࠣࡪࡷࡵ࡭ࠡ࡫ࡱࡷࡹࡧ࡮ࡤࡧࠥᕋ").format(e))
        bstack11llllll1l1_opy_ = []
        try:
            for level in levels:
                platform_index = os.environ[bstack11ll1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡖࡌࡂࡖࡉࡓࡗࡓ࡟ࡊࡐࡇࡉ࡝࠭ᕌ")]
                bstack1llll1lll1l_opy_ = os.path.join(bstack1lll11lll1l_opy_, (bstack1ll1ll1l11l_opy_ + str(platform_index)), level)
                if not os.path.isdir(bstack1llll1lll1l_opy_):
                    self.logger.debug(bstack11ll1_opy_ (u"ࠢࡅ࡫ࡵࡩࡨࡺ࡯ࡳࡻࠣࡲࡴࡺࠠࡱࡴࡨࡷࡪࡴࡴࠡࡨࡲࡶࠥࡶࡲࡰࡥࡨࡷࡸ࡯࡮ࡨࠢࡗࡩࡸࡺࠠࡢࡰࡧࠤࡇࡻࡩ࡭ࡦࠣࡰࡪࡼࡥ࡭ࠢࡤࡸࡹࡧࡣࡩ࡯ࡨࡲࡹࡹࠠࡼࡿࠥᕍ").format(bstack1llll1lll1l_opy_))
                    continue
                file_names = os.listdir(bstack1llll1lll1l_opy_)
                for file_name in file_names:
                    file_path = os.path.join(bstack1llll1lll1l_opy_, file_name)
                    abs_path = os.path.abspath(file_path)
                    if abs_path in _1lll111l1l1_opy_:
                        self.logger.info(bstack11ll1_opy_ (u"ࠣࡒࡤࡸ࡭ࠦࡡ࡭ࡴࡨࡥࡩࡿࠠࡱࡴࡲࡧࡪࡹࡳࡦࡦࠣࡿࢂࠨᕎ").format(abs_path))
                        continue
                    if os.path.isfile(file_path):
                        try:
                            bstack1l1111lll1l_opy_ = os.path.getmtime(file_path)
                            timestamp = datetime.fromtimestamp(bstack1l1111lll1l_opy_, tz=timezone.utc).isoformat()
                            file_size = os.path.getsize(file_path)
                            if level == bstack11ll1_opy_ (u"ࠤࡗࡩࡸࡺࡌࡦࡸࡨࡰࠧᕏ"):
                                entry = bstack1lll1ll1lll_opy_(
                                    kind=bstack11ll1_opy_ (u"ࠥࡘࡊ࡙ࡔࡠࡃࡗࡘࡆࡉࡈࡎࡇࡑࡘࠧᕐ"),
                                    message=bstack11ll1_opy_ (u"ࠦࠧᕑ"),
                                    level=level,
                                    timestamp=timestamp,
                                    fileName=file_name,
                                    bstack1llll1lll11_opy_=file_size,
                                    bstack1lll1111l1l_opy_=bstack11ll1_opy_ (u"ࠧࡓࡁࡏࡗࡄࡐࡤ࡛ࡐࡍࡑࡄࡈࠧᕒ"),
                                    bstack1ll11l_opy_=os.path.abspath(file_path),
                                    bstack11lllll1l_opy_=bstack1l11111ll11_opy_
                                )
                            elif level == bstack11ll1_opy_ (u"ࠨࡂࡶ࡫࡯ࡨࡑ࡫ࡶࡦ࡮ࠥᕓ"):
                                entry = bstack1lll1ll1lll_opy_(
                                    kind=bstack11ll1_opy_ (u"ࠢࡕࡇࡖࡘࡤࡇࡔࡕࡃࡆࡌࡒࡋࡎࡕࠤᕔ"),
                                    message=bstack11ll1_opy_ (u"ࠣࠤᕕ"),
                                    level=level,
                                    timestamp=timestamp,
                                    fileName=file_name,
                                    bstack1llll1lll11_opy_=file_size,
                                    bstack1lll1111l1l_opy_=bstack11ll1_opy_ (u"ࠤࡐࡅࡓ࡛ࡁࡍࡡࡘࡔࡑࡕࡁࡅࠤᕖ"),
                                    bstack1ll11l_opy_=os.path.abspath(file_path),
                                    bstack1lllll111ll_opy_=bstack1l11111ll11_opy_
                                )
                            bstack11llllll1l1_opy_.append(entry)
                            _1lll111l1l1_opy_.add(abs_path)
                        except Exception as bstack1l1111111l1_opy_:
                            self.logger.error(bstack11ll1_opy_ (u"ࠥࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡲࡢ࡫ࡶࡩࡩࠦࡷࡩࡧࡱࠤࡵࡸ࡯ࡤࡧࡶࡷ࡮ࡴࡧࠡࡣࡷࡸࡦࡩࡨ࡮ࡧࡱࡸࡸࠦࡻࡾࠤᕗ").format(bstack1l1111111l1_opy_))
        except Exception as e:
            self.logger.error(bstack11ll1_opy_ (u"ࠦࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡳࡣ࡬ࡷࡪࡪࠠࡸࡪࡨࡲࠥࡶࡲࡰࡥࡨࡷࡸ࡯࡮ࡨࠢࡤࡸࡹࡧࡣࡩ࡯ࡨࡲࡹࡹࠠࡼࡿࠥᕘ").format(e))
        event[bstack11ll1_opy_ (u"ࠧࡲ࡯ࡨࡵࠥᕙ")] = bstack11llllll1l1_opy_
class bstack1l1111ll111_opy_(JSONEncoder):
    def __init__(self, **kwargs):
        self.bstack1l1111l111l_opy_ = set()
        kwargs[bstack11ll1_opy_ (u"ࠨࡳ࡬࡫ࡳ࡯ࡪࡿࡳࠣᕚ")] = True
        super().__init__(**kwargs)
    def default(self, obj):
        return bstack11llllllll1_opy_(obj, self.bstack1l1111l111l_opy_)
def bstack11llllll11l_opy_(obj):
    return isinstance(obj, (str, int, float, bool, type(None)))
def bstack11llllllll1_opy_(obj, bstack1l1111l111l_opy_=None, max_depth=3):
    if bstack1l1111l111l_opy_ is None:
        bstack1l1111l111l_opy_ = set()
    if id(obj) in bstack1l1111l111l_opy_ or max_depth <= 0:
        return None
    max_depth -= 1
    bstack1l1111l111l_opy_.add(id(obj))
    if isinstance(obj, datetime):
        return obj.isoformat()
    bstack11llllll1ll_opy_ = TestFramework.bstack1lll1l1l111_opy_(obj)
    bstack1l1111l11ll_opy_ = next((k.lower() in bstack11llllll1ll_opy_.lower() for k in bstack1l111111lll_opy_.keys()), None)
    if bstack1l1111l11ll_opy_:
        obj = TestFramework.bstack1ll1lllll11_opy_(obj, bstack1l111111lll_opy_[bstack1l1111l11ll_opy_])
    if not isinstance(obj, dict):
        keys = []
        if hasattr(obj, bstack11ll1_opy_ (u"ࠢࡠࡡࡶࡰࡴࡺࡳࡠࡡࠥᕛ")):
            keys = getattr(obj, bstack11ll1_opy_ (u"ࠣࡡࡢࡷࡱࡵࡴࡴࡡࡢࠦᕜ"), [])
        elif hasattr(obj, bstack11ll1_opy_ (u"ࠤࡢࡣࡩ࡯ࡣࡵࡡࡢࠦᕝ")):
            keys = getattr(obj, bstack11ll1_opy_ (u"ࠥࡣࡤࡪࡩࡤࡶࡢࡣࠧᕞ"), {}).keys()
        else:
            keys = dir(obj)
        obj = {k: getattr(obj, k, None) for k in keys if not str(k).startswith(bstack11ll1_opy_ (u"ࠦࡤࠨᕟ"))}
        if not obj and bstack11llllll1ll_opy_ == bstack11ll1_opy_ (u"ࠧࡶࡡࡵࡪ࡯࡭ࡧ࠴ࡐࡰࡵ࡬ࡼࡕࡧࡴࡩࠤᕠ"):
            obj = {bstack11ll1_opy_ (u"ࠨࡰࡢࡶ࡫ࠦᕡ"): str(obj)}
    result = {}
    for key, value in obj.items():
        if not bstack11llllll11l_opy_(key) or str(key).startswith(bstack11ll1_opy_ (u"ࠢࡠࠤᕢ")):
            continue
        if value is not None and bstack11llllll11l_opy_(value):
            result[key] = value
        elif isinstance(value, dict):
            r = bstack11llllllll1_opy_(value, bstack1l1111l111l_opy_, max_depth)
            if r is not None:
                result[key] = r
        elif isinstance(value, (list, tuple, set, frozenset)):
            result[key] = list(filter(None, [bstack11llllllll1_opy_(o, bstack1l1111l111l_opy_, max_depth) for o in value]))
    return result or None