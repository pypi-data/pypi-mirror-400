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
from datetime import datetime, timezone
import os
import builtins
from pathlib import Path
from typing import Any, Tuple, Callable, List
from browserstack_sdk.sdk_cli.bstack1llll11l1ll_opy_ import bstack1llll1ll1ll_opy_, bstack1llll1111l1_opy_, bstack1lll1lll1l1_opy_
from browserstack_sdk.sdk_cli.bstack1ll1l1ll1ll_opy_ import bstack1ll1ll1l1ll_opy_
from browserstack_sdk.sdk_cli.bstack1ll11lllll1_opy_ import bstack1ll11ll1l1l_opy_
from browserstack_sdk.sdk_cli.bstack1lll1l11l11_opy_ import bstack1lll11l111l_opy_
from browserstack_sdk.sdk_cli.test_framework import TestFramework, bstack1lll111l111_opy_, bstack1ll1ll11lll_opy_, bstack1lll1l1l11l_opy_, bstack1lll111l1l1_opy_
from json import dumps, JSONEncoder
import grpc
from browserstack_sdk import sdk_pb2 as structs
import sys
import traceback
import time
import json
from bstack_utils.helper import bstack1l1l1111l1l_opy_, bstack1l1l1ll11l1_opy_
from bstack_utils.measure import measure
from bstack_utils.constants import *
bstack1l1l1l1l11l_opy_ = [bstack11l1l_opy_ (u"ࠢ࡯ࡣࡰࡩࠧዬ"), bstack11l1l_opy_ (u"ࠣࡲࡤࡶࡪࡴࡴࠣይ"), bstack11l1l_opy_ (u"ࠤࡦࡳࡳ࡬ࡩࡨࠤዮ"), bstack11l1l_opy_ (u"ࠥࡷࡪࡹࡳࡪࡱࡱࠦዯ"), bstack11l1l_opy_ (u"ࠦࡵࡧࡴࡩࠤደ")]
bstack1l1l11llll1_opy_ = bstack1l1l1ll11l1_opy_()
bstack1l1l111ll11_opy_ = bstack11l1l_opy_ (u"࡛ࠧࡰ࡭ࡱࡤࡨࡪࡪࡁࡵࡶࡤࡧ࡭ࡳࡥ࡯ࡶࡶ࠱ࠧዱ")
bstack1l1l1l11111_opy_ = {
    bstack11l1l_opy_ (u"ࠨࡰࡺࡶࡨࡷࡹ࠴ࡰࡺࡶ࡫ࡳࡳ࠴ࡉࡵࡧࡰࠦዲ"): bstack1l1l1l1l11l_opy_,
    bstack11l1l_opy_ (u"ࠢࡱࡻࡷࡩࡸࡺ࠮ࡱࡻࡷ࡬ࡴࡴ࠮ࡑࡣࡦ࡯ࡦ࡭ࡥࠣዳ"): bstack1l1l1l1l11l_opy_,
    bstack11l1l_opy_ (u"ࠣࡲࡼࡸࡪࡹࡴ࠯ࡲࡼࡸ࡭ࡵ࡮࠯ࡏࡲࡨࡺࡲࡥࠣዴ"): bstack1l1l1l1l11l_opy_,
    bstack11l1l_opy_ (u"ࠤࡳࡽࡹ࡫ࡳࡵ࠰ࡳࡽࡹ࡮࡯࡯࠰ࡆࡰࡦࡹࡳࠣድ"): bstack1l1l1l1l11l_opy_,
    bstack11l1l_opy_ (u"ࠥࡴࡾࡺࡥࡴࡶ࠱ࡴࡾࡺࡨࡰࡰ࠱ࡊࡺࡴࡣࡵ࡫ࡲࡲࠧዶ"): bstack1l1l1l1l11l_opy_
    + [
        bstack11l1l_opy_ (u"ࠦࡴࡸࡩࡨ࡫ࡱࡥࡱࡴࡡ࡮ࡧࠥዷ"),
        bstack11l1l_opy_ (u"ࠧࡱࡥࡺࡹࡲࡶࡩࡹࠢዸ"),
        bstack11l1l_opy_ (u"ࠨࡦࡪࡺࡷࡹࡷ࡫ࡩ࡯ࡨࡲࠦዹ"),
        bstack11l1l_opy_ (u"ࠢ࡬ࡧࡼࡻࡴࡸࡤࡴࠤዺ"),
        bstack11l1l_opy_ (u"ࠣࡥࡤࡰࡱࡹࡰࡦࡥࠥዻ"),
        bstack11l1l_opy_ (u"ࠤࡦࡥࡱࡲ࡯ࡣ࡬ࠥዼ"),
        bstack11l1l_opy_ (u"ࠥࡷࡹࡧࡲࡵࠤዽ"),
        bstack11l1l_opy_ (u"ࠦࡸࡺ࡯ࡱࠤዾ"),
        bstack11l1l_opy_ (u"ࠧࡪࡵࡳࡣࡷ࡭ࡴࡴࠢዿ"),
        bstack11l1l_opy_ (u"ࠨࡷࡩࡧࡱࠦጀ"),
    ],
    bstack11l1l_opy_ (u"ࠢࡱࡻࡷࡩࡸࡺ࠮࡮ࡣ࡬ࡲ࠳࡙ࡥࡴࡵ࡬ࡳࡳࠨጁ"): [bstack11l1l_opy_ (u"ࠣࡵࡷࡥࡷࡺࡰࡢࡶ࡫ࠦጂ"), bstack11l1l_opy_ (u"ࠤࡷࡩࡸࡺࡳࡧࡣ࡬ࡰࡪࡪࠢጃ"), bstack11l1l_opy_ (u"ࠥࡸࡪࡹࡴࡴࡥࡲࡰࡱ࡫ࡣࡵࡧࡧࠦጄ"), bstack11l1l_opy_ (u"ࠦ࡮ࡺࡥ࡮ࡵࠥጅ")],
    bstack11l1l_opy_ (u"ࠧࡶࡹࡵࡧࡶࡸ࠳ࡩ࡯࡯ࡨ࡬࡫࠳ࡉ࡯࡯ࡨ࡬࡫ࠧጆ"): [bstack11l1l_opy_ (u"ࠨࡩ࡯ࡸࡲࡧࡦࡺࡩࡰࡰࡢࡴࡦࡸࡡ࡮ࡵࠥጇ"), bstack11l1l_opy_ (u"ࠢࡢࡴࡪࡷࠧገ")],
    bstack11l1l_opy_ (u"ࠣࡲࡼࡸࡪࡹࡴ࠯ࡨ࡬ࡼࡹࡻࡲࡦࡵ࠱ࡊ࡮ࡾࡴࡶࡴࡨࡈࡪ࡬ࠢጉ"): [bstack11l1l_opy_ (u"ࠤࡶࡧࡴࡶࡥࠣጊ"), bstack11l1l_opy_ (u"ࠥࡥࡷ࡭࡮ࡢ࡯ࡨࠦጋ"), bstack11l1l_opy_ (u"ࠦ࡫ࡻ࡮ࡤࠤጌ"), bstack11l1l_opy_ (u"ࠧࡶࡡࡳࡣࡰࡷࠧግ"), bstack11l1l_opy_ (u"ࠨࡵ࡯࡫ࡷࡸࡪࡹࡴࠣጎ"), bstack11l1l_opy_ (u"ࠢࡪࡦࡶࠦጏ")],
    bstack11l1l_opy_ (u"ࠣࡲࡼࡸࡪࡹࡴ࠯ࡨ࡬ࡼࡹࡻࡲࡦࡵ࠱ࡗࡺࡨࡒࡦࡳࡸࡩࡸࡺࠢጐ"): [bstack11l1l_opy_ (u"ࠤࡩ࡭ࡽࡺࡵࡳࡧࡱࡥࡲ࡫ࠢ጑"), bstack11l1l_opy_ (u"ࠥࡴࡦࡸࡡ࡮ࠤጒ"), bstack11l1l_opy_ (u"ࠦࡵࡧࡲࡢ࡯ࡢ࡭ࡳࡪࡥࡹࠤጓ")],
    bstack11l1l_opy_ (u"ࠧࡶࡹࡵࡧࡶࡸ࠳ࡸࡵ࡯ࡰࡨࡶ࠳ࡉࡡ࡭࡮ࡌࡲ࡫ࡵࠢጔ"): [bstack11l1l_opy_ (u"ࠨࡷࡩࡧࡱࠦጕ"), bstack11l1l_opy_ (u"ࠢࡳࡧࡶࡹࡱࡺࠢ጖")],
    bstack11l1l_opy_ (u"ࠣࡲࡼࡸࡪࡹࡴ࠯࡯ࡤࡶࡰ࠴ࡳࡵࡴࡸࡧࡹࡻࡲࡦࡵ࠱ࡒࡴࡪࡥࡌࡧࡼࡻࡴࡸࡤࡴࠤ጗"): [bstack11l1l_opy_ (u"ࠤࡱࡳࡩ࡫ࠢጘ"), bstack11l1l_opy_ (u"ࠥࡴࡦࡸࡥ࡯ࡶࠥጙ")],
    bstack11l1l_opy_ (u"ࠦࡵࡿࡴࡦࡵࡷ࠲ࡲࡧࡲ࡬࠰ࡶࡸࡷࡻࡣࡵࡷࡵࡩࡸ࠴ࡍࡢࡴ࡮ࠦጚ"): [bstack11l1l_opy_ (u"ࠧࡴࡡ࡮ࡧࠥጛ"), bstack11l1l_opy_ (u"ࠨࡡࡳࡩࡶࠦጜ"), bstack11l1l_opy_ (u"ࠢ࡬ࡹࡤࡶ࡬ࡹࠢጝ")],
}
_1l1l11l1l1l_opy_ = set()
class bstack1lll111ll1l_opy_(bstack1ll1ll1l1ll_opy_):
    bstack1l1l1lll11l_opy_ = bstack11l1l_opy_ (u"ࠣࡶࡨࡷࡹࡥࡤࡦࡨࡨࡶࡷ࡫ࡤࠣጞ")
    bstack1l1l111llll_opy_ = bstack11l1l_opy_ (u"ࠤࡌࡒࡋࡕࠢጟ")
    bstack1l1l11ll11l_opy_ = bstack11l1l_opy_ (u"ࠥࡉࡗࡘࡏࡓࠤጠ")
    bstack1l1ll111l11_opy_: Callable
    bstack1l1l11l1l11_opy_: Callable
    def __init__(self, bstack1lll1l1l1ll_opy_, bstack1ll1l111lll_opy_):
        super().__init__()
        self.bstack1l1llllll1l_opy_ = bstack1ll1l111lll_opy_
        if os.getenv(bstack11l1l_opy_ (u"ࠦࡘࡊࡋࡠࡅࡏࡍࡤࡌࡌࡂࡉࡢࡓ࠶࠷࡙ࠣጡ"), bstack11l1l_opy_ (u"ࠧ࠷ࠢጢ")) != bstack11l1l_opy_ (u"ࠨ࠱ࠣጣ") or not self.is_enabled():
            self.logger.warning(bstack11l1l_opy_ (u"ࠢࠣጤ") + str(self.__class__.__name__) + bstack11l1l_opy_ (u"ࠣࠢࡧ࡭ࡸࡧࡢ࡭ࡧࡧࠦጥ"))
            return
        TestFramework.bstack1ll111ll111_opy_((bstack1lll111l111_opy_.TEST, bstack1lll1l1l11l_opy_.PRE), self.bstack1ll111l1l11_opy_)
        TestFramework.bstack1ll111ll111_opy_((bstack1lll111l111_opy_.TEST, bstack1lll1l1l11l_opy_.POST), self.bstack1l1llll1l11_opy_)
        for event in bstack1lll111l111_opy_:
            for state in bstack1lll1l1l11l_opy_:
                TestFramework.bstack1ll111ll111_opy_((event, state), self.bstack1l1l1ll111l_opy_)
        bstack1lll1l1l1ll_opy_.bstack1ll111ll111_opy_((bstack1llll1111l1_opy_.bstack1lll1ll1ll1_opy_, bstack1lll1lll1l1_opy_.POST), self.bstack1l1ll111ll1_opy_)
        self.bstack1l1ll111l11_opy_ = sys.stdout.write
        sys.stdout.write = self.bstack1l1l11lllll_opy_(bstack1lll111ll1l_opy_.bstack1l1l111llll_opy_, self.bstack1l1ll111l11_opy_)
        self.bstack1l1l11l1l11_opy_ = sys.stderr.write
        sys.stderr.write = self.bstack1l1l11lllll_opy_(bstack1lll111ll1l_opy_.bstack1l1l11ll11l_opy_, self.bstack1l1l11l1l11_opy_)
        self.bstack1l1ll111111_opy_ = builtins.print
        builtins.print = self.bstack1l1l111l111_opy_()
    def is_enabled(self) -> bool:
        return True
    def bstack1l1l1ll111l_opy_(
        self,
        f: TestFramework,
        instance: bstack1ll1ll11lll_opy_,
        bstack1llll1lll1l_opy_: Tuple[bstack1lll111l111_opy_, bstack1lll1l1l11l_opy_],
        *args,
        **kwargs,
    ):
        if f.bstack1l1l1l11l1l_opy_() and instance:
            bstack1l1ll111l1l_opy_ = datetime.now()
            test_framework_state, test_hook_state = bstack1llll1lll1l_opy_
            if test_framework_state == bstack1lll111l111_opy_.SETUP_FIXTURE:
                return
            elif test_framework_state == bstack1lll111l111_opy_.LOG:
                bstack11ll1l1ll1_opy_ = datetime.now()
                entries = f.bstack1l1l1111lll_opy_(instance, bstack1llll1lll1l_opy_)
                if entries:
                    self.bstack1l1l1l1l111_opy_(instance, entries)
                    instance.bstack11lll111_opy_(bstack11l1l_opy_ (u"ࠤࡪࡶࡵࡩ࠺ࡴࡧࡱࡨࡤࡲ࡯ࡨࡡࡦࡶࡪࡧࡴࡦࡦࡢࡩࡻ࡫࡮ࡵࠤጦ"), datetime.now() - bstack11ll1l1ll1_opy_)
                    f.bstack1l1l1l11lll_opy_(instance, bstack1llll1lll1l_opy_)
                instance.bstack11lll111_opy_(bstack11l1l_opy_ (u"ࠥࡳ࠶࠷ࡹ࠻ࡱࡱࡣࡦࡲ࡬ࡠࡶࡨࡷࡹࡥࡥࡷࡧࡱࡸࡸࠨጧ"), datetime.now() - bstack1l1ll111l1l_opy_)
                return # bstack1l1l1l1ll11_opy_ not send this event with the bstack1l1l1ll1ll1_opy_ bstack1l1l1ll1111_opy_
            elif (
                test_framework_state == bstack1lll111l111_opy_.TEST
                and test_hook_state == bstack1lll1l1l11l_opy_.POST
                and not f.bstack1lll1ll1l1l_opy_(instance, TestFramework.bstack1l1l1l1l1ll_opy_)
            ):
                self.logger.warning(bstack11l1l_opy_ (u"ࠦࡩࡸ࡯ࡱࡲ࡬ࡲ࡬ࠦࡤࡶࡧࠣࡸࡴࠦ࡬ࡢࡥ࡮ࠤࡴ࡬ࠠࡳࡧࡶࡹࡱࡺࡳࠡࠤጨ") + str(TestFramework.bstack1lll1ll1l1l_opy_(instance, TestFramework.bstack1l1l1l1l1ll_opy_)) + bstack11l1l_opy_ (u"ࠧࠨጩ"))
                f.bstack1lllll1111l_opy_(instance, bstack1lll111ll1l_opy_.bstack1l1l1lll11l_opy_, True)
                return # bstack1l1l1l1ll11_opy_ not send this event bstack1l1l1lllll1_opy_ bstack1l1l111ll1l_opy_
            elif (
                f.bstack1llll1lllll_opy_(instance, bstack1lll111ll1l_opy_.bstack1l1l1lll11l_opy_, False)
                and test_framework_state == bstack1lll111l111_opy_.LOG_REPORT
                and test_hook_state == bstack1lll1l1l11l_opy_.POST
                and f.bstack1lll1ll1l1l_opy_(instance, TestFramework.bstack1l1l1l1l1ll_opy_)
            ):
                self.logger.warning(bstack11l1l_opy_ (u"ࠨࡩ࡯࡬ࡨࡧࡹ࡯࡮ࡨࠢࡗࡩࡸࡺࡆࡳࡣࡰࡩࡼࡵࡲ࡬ࡕࡷࡥࡹ࡫࠮ࡕࡇࡖࡘ࠱ࠦࡔࡦࡵࡷࡌࡴࡵ࡫ࡔࡶࡤࡸࡪ࠴ࡐࡐࡕࡗࠤࠧጪ") + str(TestFramework.bstack1lll1ll1l1l_opy_(instance, TestFramework.bstack1l1l1l1l1ll_opy_)) + bstack11l1l_opy_ (u"ࠢࠣጫ"))
                self.bstack1l1l1ll111l_opy_(f, instance, (bstack1lll111l111_opy_.TEST, bstack1lll1l1l11l_opy_.POST), *args, **kwargs)
            bstack11ll1l1ll1_opy_ = datetime.now()
            data = instance.data.copy()
            bstack1l1l1111ll1_opy_ = sorted(
                filter(lambda x: x.get(bstack11l1l_opy_ (u"ࠣࡧࡹࡩࡳࡺ࡟ࡴࡶࡤࡶࡹ࡫ࡤࡠࡣࡷࠦጬ"), None), data.pop(bstack11l1l_opy_ (u"ࠤࡷࡩࡸࡺ࡟ࡧ࡫ࡻࡸࡺࡸࡥࡴࠤጭ"), {}).values()),
                key=lambda x: x[bstack11l1l_opy_ (u"ࠥࡩࡻ࡫࡮ࡵࡡࡶࡸࡦࡸࡴࡦࡦࡢࡥࡹࠨጮ")],
            )
            if bstack1ll11ll1l1l_opy_.bstack1l1l1l1lll1_opy_ in data:
                data.pop(bstack1ll11ll1l1l_opy_.bstack1l1l1l1lll1_opy_)
            data.update({bstack11l1l_opy_ (u"ࠦࡹ࡫ࡳࡵࡡࡩ࡭ࡽࡺࡵࡳࡧࡶࠦጯ"): bstack1l1l1111ll1_opy_})
            instance.bstack11lll111_opy_(bstack11l1l_opy_ (u"ࠧࡰࡳࡰࡰ࠽ࡸࡪࡹࡴࡠࡨ࡬ࡼࡹࡻࡲࡦࡵࠥጰ"), datetime.now() - bstack11ll1l1ll1_opy_)
            bstack11ll1l1ll1_opy_ = datetime.now()
            event_json = dumps(data, cls=bstack1l1l11ll1ll_opy_)
            instance.bstack11lll111_opy_(bstack11l1l_opy_ (u"ࠨࡪࡴࡱࡱ࠾ࡴࡴ࡟ࡢ࡮࡯ࡣࡹ࡫ࡳࡵࡡࡨࡺࡪࡴࡴࡴࠤጱ"), datetime.now() - bstack11ll1l1ll1_opy_)
            self.bstack1l1l1ll1111_opy_(instance, bstack1llll1lll1l_opy_, event_json=event_json)
            instance.bstack11lll111_opy_(bstack11l1l_opy_ (u"ࠢࡰ࠳࠴ࡽ࠿ࡵ࡮ࡠࡣ࡯ࡰࡤࡺࡥࡴࡶࡢࡩࡻ࡫࡮ࡵࡵࠥጲ"), datetime.now() - bstack1l1ll111l1l_opy_)
    def bstack1ll111l1l11_opy_(
        self,
        f: TestFramework,
        instance: bstack1ll1ll11lll_opy_,
        bstack1llll1lll1l_opy_: Tuple[bstack1lll111l111_opy_, bstack1lll1l1l11l_opy_],
        *args,
        **kwargs,
    ):
        from bstack_utils.bstack11l1l11ll_opy_ import bstack1lll1ll1l11_opy_
        bstack1l1llllllll_opy_ = bstack1lll1ll1l11_opy_.bstack1ll11l1l111_opy_(EVENTS.bstack1l1ll11ll_opy_.value)
        self.bstack1l1llllll1l_opy_.bstack1l1l1llll1l_opy_(instance, f, bstack1llll1lll1l_opy_, *args, **kwargs)
        req = self.bstack1l1llllll1l_opy_.bstack1l1l1l1llll_opy_(instance, f, bstack1llll1lll1l_opy_, *args, **kwargs)
        self.bstack1l1l11l111l_opy_(f, instance, req)
        bstack1lll1ll1l11_opy_.end(EVENTS.bstack1l1ll11ll_opy_.value, bstack1l1llllllll_opy_ + bstack11l1l_opy_ (u"ࠣ࠼ࡶࡸࡦࡸࡴࠣጳ"), bstack1l1llllllll_opy_ + bstack11l1l_opy_ (u"ࠤ࠽ࡩࡳࡪࠢጴ"), status=True, failure=None, test_name=None)
    def bstack1l1llll1l11_opy_(
        self,
        f: TestFramework,
        instance: bstack1ll1ll11lll_opy_,
        bstack1llll1lll1l_opy_: Tuple[bstack1lll111l111_opy_, bstack1lll1l1l11l_opy_],
        *args,
        **kwargs,
    ):
        if not f.bstack1llll1lllll_opy_(instance, self.bstack1l1llllll1l_opy_.bstack1l1ll1111ll_opy_, False):
            req = self.bstack1l1llllll1l_opy_.bstack1l1l1l1llll_opy_(instance, f, bstack1llll1lll1l_opy_, *args, **kwargs)
            self.bstack1l1l11l111l_opy_(f, instance, req)
    @measure(event_name=EVENTS.bstack1l1l1l11ll1_opy_, stage=STAGE.bstack1lll1l11l_opy_)
    def bstack1l1l11l111l_opy_(
        self,
        f: TestFramework,
        instance: bstack1ll1ll11lll_opy_,
        req: structs.TestSessionEventRequest
    ):
        if not req:
            self.logger.debug(bstack11l1l_opy_ (u"ࠥࡗࡰ࡯ࡰࡱ࡫ࡱ࡫࡚ࠥࡥࡴࡶࡖࡩࡸࡹࡩࡰࡰࡈࡺࡪࡴࡴࠡࡩࡕࡔࡈࠦࡣࡢ࡮࡯࠾ࠥࡔ࡯ࠡࡸࡤࡰ࡮ࡪࠠࡳࡧࡴࡹࡪࡹࡴࠡࡦࡤࡸࡦࠨጵ"))
            return
        bstack11ll1l1ll1_opy_ = datetime.now()
        try:
            r = self.bstack1ll1ll11l11_opy_.TestSessionEvent(req)
            instance.bstack11lll111_opy_(bstack11l1l_opy_ (u"ࠦ࡬ࡸࡰࡤ࠼ࡶࡩࡳࡪ࡟ࡵࡧࡶࡸࡤࡹࡥࡴࡵ࡬ࡳࡳࡥࡥࡷࡧࡱࡸࠧጶ"), datetime.now() - bstack11ll1l1ll1_opy_)
            f.bstack1lllll1111l_opy_(instance, self.bstack1l1llllll1l_opy_.bstack1l1ll1111ll_opy_, r.success)
            if not r.success:
                self.logger.info(bstack11l1l_opy_ (u"ࠧࡸࡥࡤࡧ࡬ࡺࡪࡪࠠࡧࡴࡲࡱࠥࡹࡥࡳࡸࡨࡶ࠿ࠦࠢጷ") + str(r) + bstack11l1l_opy_ (u"ࠨࠢጸ"))
        except grpc.RpcError as e:
            self.logger.error(bstack11l1l_opy_ (u"ࠢࡳࡲࡦ࠱ࡪࡸࡲࡰࡴ࠽ࠤࠧጹ") + str(e) + bstack11l1l_opy_ (u"ࠣࠤጺ"))
            traceback.print_exc()
            raise e
    def bstack1l1ll111ll1_opy_(
        self,
        f: bstack1lll11l111l_opy_,
        _driver: object,
        exec: Tuple[bstack1llll1ll1ll_opy_, str],
        _1l1l111lll1_opy_: Tuple[bstack1llll1111l1_opy_, bstack1lll1lll1l1_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if not bstack1lll11l111l_opy_.bstack1ll1111l11l_opy_(method_name):
            return
        if f.bstack1ll111111l1_opy_(*args) == bstack1lll11l111l_opy_.bstack1l1l11lll1l_opy_:
            bstack1l1ll111l1l_opy_ = datetime.now()
            screenshot = result.get(bstack11l1l_opy_ (u"ࠤࡹࡥࡱࡻࡥࠣጻ"), None) if isinstance(result, dict) else None
            if not isinstance(screenshot, str) or len(screenshot) <= 0:
                self.logger.warning(bstack11l1l_opy_ (u"ࠥ࡭ࡳࡼࡡ࡭࡫ࡧࠤࡸࡩࡲࡦࡧࡱࡷ࡭ࡵࡴࠡ࡫ࡰࡥ࡬࡫ࠠࡣࡣࡶࡩ࠻࠺ࠠࡴࡶࡵࠦጼ"))
                return
            bstack1l1l1111l11_opy_ = self.bstack1l1ll1111l1_opy_(instance)
            if bstack1l1l1111l11_opy_:
                entry = bstack1lll111l1l1_opy_(TestFramework.bstack1l1l11l1ll1_opy_, screenshot)
                self.bstack1l1l1l1l111_opy_(bstack1l1l1111l11_opy_, [entry])
                instance.bstack11lll111_opy_(bstack11l1l_opy_ (u"ࠦࡴ࠷࠱ࡺ࠼ࡲࡲࡤࡧࡦࡵࡧࡵࡣࡪࡾࡥࡤࡷࡷࡩࠧጽ"), datetime.now() - bstack1l1ll111l1l_opy_)
            else:
                self.logger.warning(bstack11l1l_opy_ (u"ࠧࡻ࡮ࡢࡤ࡯ࡩࠥࡺ࡯ࠡࡦࡨࡸࡪࡸ࡭ࡪࡰࡨࠤࡹ࡫ࡳࡵࠢࡩࡳࡷࠦࡷࡩ࡫ࡦ࡬ࠥࡺࡨࡪࡵࠣࡷࡨࡸࡥࡦࡰࡶ࡬ࡴࡺࠠࡸࡣࡶࠤࡹࡧ࡫ࡦࡰࠣࡦࡾࠦࡤࡳ࡫ࡹࡩࡷࡃࠠࡼࡿࠥጾ").format(instance.ref()))
        event = {}
        bstack1l1l1111l11_opy_ = self.bstack1l1ll1111l1_opy_(instance)
        if bstack1l1l1111l11_opy_:
            self.bstack1l1l1l111l1_opy_(event, bstack1l1l1111l11_opy_)
            if event.get(bstack11l1l_opy_ (u"ࠨ࡬ࡰࡩࡶࠦጿ")):
                self.bstack1l1l1l1l111_opy_(bstack1l1l1111l11_opy_, event[bstack11l1l_opy_ (u"ࠢ࡭ࡱࡪࡷࠧፀ")])
            else:
                self.logger.debug(bstack11l1l_opy_ (u"ࠣࡗࡱࡥࡧࡲࡥࠡࡶࡲࠤࡩ࡫ࡴࡦࡴࡰ࡭ࡳ࡫ࠠ࡭ࡱࡪࡷࠥ࡬࡯ࡳࠢࡤࡸࡹࡧࡣࡩ࡯ࡨࡲࡹࠦࡥࡷࡧࡱࡸࠧፁ"))
    @measure(event_name=EVENTS.bstack1l1l11111ll_opy_, stage=STAGE.bstack1lll1l11l_opy_)
    def bstack1l1l1l1l111_opy_(
        self,
        bstack1l1l1111l11_opy_: bstack1ll1ll11lll_opy_,
        entries: List[bstack1lll111l1l1_opy_],
    ):
        self.bstack1ll11111lll_opy_()
        req = structs.LogCreatedEventRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = TestFramework.bstack1llll1lllll_opy_(bstack1l1l1111l11_opy_, TestFramework.bstack1ll1111l111_opy_)
        req.execution_context.hash = str(bstack1l1l1111l11_opy_.context.hash)
        req.execution_context.thread_id = str(bstack1l1l1111l11_opy_.context.thread_id)
        req.execution_context.process_id = str(bstack1l1l1111l11_opy_.context.process_id)
        for entry in entries:
            log_entry = req.logs.add()
            log_entry.test_framework_name = TestFramework.bstack1llll1lllll_opy_(bstack1l1l1111l11_opy_, TestFramework.bstack1l1llll11l1_opy_)
            log_entry.test_framework_version = TestFramework.bstack1llll1lllll_opy_(bstack1l1l1111l11_opy_, TestFramework.bstack1l1l1lll1ll_opy_)
            log_entry.uuid = TestFramework.bstack1llll1lllll_opy_(bstack1l1l1111l11_opy_, TestFramework.bstack1ll11l11l1l_opy_)
            log_entry.test_framework_state = bstack1l1l1111l11_opy_.state.name
            log_entry.message = entry.message.encode(bstack11l1l_opy_ (u"ࠤࡸࡸ࡫࠳࠸ࠣፂ"))
            log_entry.kind = entry.kind
            log_entry.timestamp = (
                entry.timestamp.isoformat()
                if isinstance(entry.timestamp, datetime)
                else datetime.now(tz=timezone.utc).isoformat()
            )
            if isinstance(entry.level, str) and len(entry.level.strip()) > 0:
                log_entry.level = entry.level.strip()
            if entry.kind == bstack11l1l_opy_ (u"ࠥࡘࡊ࡙ࡔࡠࡃࡗࡘࡆࡉࡈࡎࡇࡑࡘࠧፃ"):
                log_entry.file_name = entry.fileName
                log_entry.file_size = entry.bstack1l1ll11111l_opy_
                log_entry.file_path = entry.bstack1llllll_opy_
        def bstack1l1l1l1l1l1_opy_():
            bstack11ll1l1ll1_opy_ = datetime.now()
            try:
                self.bstack1ll1ll11l11_opy_.LogCreatedEvent(req)
                if entry.kind == TestFramework.bstack1l1l11l1ll1_opy_:
                    bstack1l1l1111l11_opy_.bstack11lll111_opy_(bstack11l1l_opy_ (u"ࠦ࡬ࡸࡰࡤ࠼ࡶࡩࡳࡪ࡟࡭ࡱࡪࡣࡨࡸࡥࡢࡶࡨࡨࡤ࡫ࡶࡦࡰࡷࡣࡸࡩࡲࡦࡧࡱࡷ࡭ࡵࡴࠣፄ"), datetime.now() - bstack11ll1l1ll1_opy_)
                elif entry.kind == TestFramework.bstack1l1l11l1lll_opy_:
                    bstack1l1l1111l11_opy_.bstack11lll111_opy_(bstack11l1l_opy_ (u"ࠧ࡭ࡲࡱࡥ࠽ࡷࡪࡴࡤࡠ࡮ࡲ࡫ࡤࡩࡲࡦࡣࡷࡩࡩࡥࡥࡷࡧࡱࡸࡤࡧࡴࡵࡣࡦ࡬ࡲ࡫࡮ࡵࠤፅ"), datetime.now() - bstack11ll1l1ll1_opy_)
                else:
                    bstack1l1l1111l11_opy_.bstack11lll111_opy_(bstack11l1l_opy_ (u"ࠨࡧࡳࡲࡦ࠾ࡸ࡫࡮ࡥࡡ࡯ࡳ࡬ࡥࡣࡳࡧࡤࡸࡪࡪ࡟ࡦࡸࡨࡲࡹࡥ࡬ࡰࡩࠥፆ"), datetime.now() - bstack11ll1l1ll1_opy_)
            except grpc.RpcError as e:
                self.log_error(bstack11l1l_opy_ (u"ࠢࡳࡲࡦ࠱ࡪࡸࡲࡰࡴ࠽ࠤࠧፇ") + str(e))
                traceback.print_exc()
                raise e
        self.bstack1lllll1l11l_opy_.enqueue(bstack1l1l1l1l1l1_opy_)
    @measure(event_name=EVENTS.bstack1l1l1ll1l1l_opy_, stage=STAGE.bstack1lll1l11l_opy_)
    def bstack1l1l1ll1111_opy_(
        self,
        instance: bstack1ll1ll11lll_opy_,
        bstack1llll1lll1l_opy_: Tuple[bstack1lll111l111_opy_, bstack1lll1l1l11l_opy_],
        event_json=None,
    ):
        self.bstack1ll11111lll_opy_()
        req = structs.TestFrameworkEventRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = TestFramework.bstack1llll1lllll_opy_(instance, TestFramework.bstack1ll1111l111_opy_)
        req.test_framework_name = TestFramework.bstack1llll1lllll_opy_(instance, TestFramework.bstack1l1llll11l1_opy_)
        req.test_framework_version = TestFramework.bstack1llll1lllll_opy_(instance, TestFramework.bstack1l1l1lll1ll_opy_)
        req.test_framework_state = bstack1llll1lll1l_opy_[0].name
        req.test_hook_state = bstack1llll1lll1l_opy_[1].name
        started_at = TestFramework.bstack1llll1lllll_opy_(instance, TestFramework.bstack1l1l1l11l11_opy_, None)
        if started_at:
            req.started_at = started_at.isoformat()
        ended_at = TestFramework.bstack1llll1lllll_opy_(instance, TestFramework.bstack1l1l11ll111_opy_, None)
        if ended_at:
            req.ended_at = ended_at.isoformat()
        req.uuid = instance.ref()
        req.event_json = (event_json if event_json else dumps(instance.data, cls=bstack1l1l11ll1ll_opy_)).encode(bstack11l1l_opy_ (u"ࠣࡷࡷࡪ࠲࠾ࠢፈ"))
        req.execution_context.hash = str(instance.context.hash)
        req.execution_context.thread_id = str(instance.context.thread_id)
        req.execution_context.process_id = str(instance.context.process_id)
        def bstack1l1l1l1l1l1_opy_():
            bstack11ll1l1ll1_opy_ = datetime.now()
            try:
                self.bstack1ll1ll11l11_opy_.TestFrameworkEvent(req)
                instance.bstack11lll111_opy_(bstack11l1l_opy_ (u"ࠤࡪࡶࡵࡩ࠺ࡴࡧࡱࡨࡤࡺࡥࡴࡶࡢࡪࡷࡧ࡭ࡦࡹࡲࡶࡰࡥࡥࡷࡧࡱࡸࠧፉ"), datetime.now() - bstack11ll1l1ll1_opy_)
            except grpc.RpcError as e:
                self.log_error(bstack11l1l_opy_ (u"ࠥࡶࡵࡩ࠭ࡦࡴࡵࡳࡷࡀࠠࠣፊ") + str(e))
                traceback.print_exc()
                raise e
        self.bstack1lllll1l11l_opy_.enqueue(bstack1l1l1l1l1l1_opy_)
    def bstack1l1ll1111l1_opy_(self, instance: bstack1llll1ll1ll_opy_):
        bstack1l1l11l11ll_opy_ = TestFramework.bstack1lll1llll1l_opy_(instance.context)
        for t in bstack1l1l11l11ll_opy_:
            bstack1l1l11l11l1_opy_ = TestFramework.bstack1llll1lllll_opy_(t, bstack1ll11ll1l1l_opy_.bstack1l1l1l1lll1_opy_, [])
            if any(instance is d[1] for d in bstack1l1l11l11l1_opy_):
                return t
    def bstack1l1ll11l111_opy_(self, message):
        self.bstack1l1ll111l11_opy_(message + bstack11l1l_opy_ (u"ࠦࡡࡴࠢፋ"))
    def log_error(self, message):
        self.bstack1l1l11l1l11_opy_(message + bstack11l1l_opy_ (u"ࠧࡢ࡮ࠣፌ"))
    def bstack1l1l11lllll_opy_(self, level, original_func):
        def bstack1l1l1ll11ll_opy_(*args):
            try:
                try:
                    return_value = original_func(*args)
                except Exception:
                    return None
                try:
                    if not args or not isinstance(args[0], str) or not args[0].strip():
                        return return_value
                    message = args[0].strip()
                    if bstack11l1l_opy_ (u"ࠨࡅࡷࡧࡱࡸࡉ࡯ࡳࡱࡣࡷࡧ࡭࡫ࡲࡎࡱࡧࡹࡱ࡫ࠢፍ") in message or bstack11l1l_opy_ (u"ࠢ࡜ࡕࡇࡏࡈࡒࡉ࡞ࠤፎ") in message or bstack11l1l_opy_ (u"ࠣ࡝࡚ࡩࡧࡊࡲࡪࡸࡨࡶࡒࡵࡤࡶ࡮ࡨࡡࠧፏ") in message:
                        return return_value
                    bstack1l1l11l11ll_opy_ = TestFramework.bstack1l1ll111lll_opy_()
                    if not bstack1l1l11l11ll_opy_:
                        return return_value
                    bstack1l1l1111l11_opy_ = next(
                        (
                            instance
                            for instance in bstack1l1l11l11ll_opy_
                            if TestFramework.bstack1lll1ll1l1l_opy_(instance, TestFramework.bstack1ll11l11l1l_opy_)
                        ),
                        None,
                    )
                    if not bstack1l1l1111l11_opy_:
                        return return_value
                    entry = bstack1lll111l1l1_opy_(TestFramework.bstack1l1l1llllll_opy_, message, level)
                    self.bstack1l1l1l1l111_opy_(bstack1l1l1111l11_opy_, [entry])
                except Exception:
                    pass
                return return_value
            except Exception:
                return None
        return bstack1l1l1ll11ll_opy_
    def bstack1l1l111l111_opy_(self):
        def bstack1l1l1lll1l1_opy_(*args, **kwargs):
            try:
                self.bstack1l1ll111111_opy_(*args, **kwargs)
                if not args:
                    return
                message = bstack11l1l_opy_ (u"ࠩࠣࠫፐ").join(str(arg) for arg in args)
                if not message.strip():
                    return
                if bstack11l1l_opy_ (u"ࠥࡉࡻ࡫࡮ࡵࡆ࡬ࡷࡵࡧࡴࡤࡪࡨࡶࡒࡵࡤࡶ࡮ࡨࠦፑ") in message:
                    return
                bstack1l1l11l11ll_opy_ = TestFramework.bstack1l1ll111lll_opy_()
                if not bstack1l1l11l11ll_opy_:
                    return
                bstack1l1l1111l11_opy_ = next(
                    (
                        instance
                        for instance in bstack1l1l11l11ll_opy_
                        if TestFramework.bstack1lll1ll1l1l_opy_(instance, TestFramework.bstack1ll11l11l1l_opy_)
                    ),
                    None,
                )
                if not bstack1l1l1111l11_opy_:
                    return
                entry = bstack1lll111l1l1_opy_(TestFramework.bstack1l1l1llllll_opy_, message, bstack1lll111ll1l_opy_.bstack1l1l111llll_opy_)
                self.bstack1l1l1l1l111_opy_(bstack1l1l1111l11_opy_, [entry])
            except Exception as e:
                try:
                    self.bstack1l1ll111111_opy_(bstack1ll1l11l1ll_opy_ (u"ࠦࡠࡋࡶࡦࡰࡷࡈ࡮ࡹࡰࡢࡶࡦ࡬ࡪࡸࡍࡰࡦࡸࡰࡪࡣࠠࡍࡱࡪࠤࡨࡧࡰࡵࡷࡵࡩࠥ࡫ࡲࡳࡱࡵ࠾ࠥࢁࡥࡾࠤፒ"))
                except:
                    pass
        return bstack1l1l1lll1l1_opy_
    def bstack1l1l1l111l1_opy_(self, event: dict, instance=None) -> None:
        global _1l1l11l1l1l_opy_
        levels = [bstack11l1l_opy_ (u"࡚ࠧࡥࡴࡶࡏࡩࡻ࡫࡬ࠣፓ"), bstack11l1l_opy_ (u"ࠨࡂࡶ࡫࡯ࡨࡑ࡫ࡶࡦ࡮ࠥፔ")]
        bstack1l1l1lll111_opy_ = bstack11l1l_opy_ (u"ࠢࠣፕ")
        if instance is not None:
            try:
                bstack1l1l1lll111_opy_ = TestFramework.bstack1llll1lllll_opy_(instance, TestFramework.bstack1ll11l11l1l_opy_)
            except Exception as e:
                self.logger.warning(bstack11l1l_opy_ (u"ࠣࡇࡵࡶࡴࡸࠠࡨࡧࡷࡸ࡮ࡴࡧࠡࡷࡸ࡭ࡩࠦࡦࡳࡱࡰࠤ࡮ࡴࡳࡵࡣࡱࡧࡪࠨፖ").format(e))
        bstack1l1l1l111ll_opy_ = []
        try:
            for level in levels:
                platform_index = os.environ[bstack11l1l_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡒࡏࡅ࡙ࡌࡏࡓࡏࡢࡍࡓࡊࡅ࡙ࠩፗ")]
                bstack1l1l111l11l_opy_ = os.path.join(bstack1l1l11llll1_opy_, (bstack1l1l111ll11_opy_ + str(platform_index)), level)
                if not os.path.isdir(bstack1l1l111l11l_opy_):
                    self.logger.debug(bstack11l1l_opy_ (u"ࠥࡈ࡮ࡸࡥࡤࡶࡲࡶࡾࠦ࡮ࡰࡶࠣࡴࡷ࡫ࡳࡦࡰࡷࠤ࡫ࡵࡲࠡࡲࡵࡳࡨ࡫ࡳࡴ࡫ࡱ࡫࡚ࠥࡥࡴࡶࠣࡥࡳࡪࠠࡃࡷ࡬ࡰࡩࠦ࡬ࡦࡸࡨࡰࠥࡧࡴࡵࡣࡦ࡬ࡲ࡫࡮ࡵࡵࠣࡿࢂࠨፘ").format(bstack1l1l111l11l_opy_))
                    continue
                file_names = os.listdir(bstack1l1l111l11l_opy_)
                for file_name in file_names:
                    file_path = os.path.join(bstack1l1l111l11l_opy_, file_name)
                    abs_path = os.path.abspath(file_path)
                    if abs_path in _1l1l11l1l1l_opy_:
                        self.logger.info(bstack11l1l_opy_ (u"ࠦࡕࡧࡴࡩࠢࡤࡰࡷ࡫ࡡࡥࡻࠣࡴࡷࡵࡣࡦࡵࡶࡩࡩࠦࡻࡾࠤፙ").format(abs_path))
                        continue
                    if os.path.isfile(file_path):
                        try:
                            bstack1l1l1l1ll1l_opy_ = os.path.getmtime(file_path)
                            timestamp = datetime.fromtimestamp(bstack1l1l1l1ll1l_opy_, tz=timezone.utc).isoformat()
                            file_size = os.path.getsize(file_path)
                            if level == bstack11l1l_opy_ (u"࡚ࠧࡥࡴࡶࡏࡩࡻ࡫࡬ࠣፚ"):
                                entry = bstack1lll111l1l1_opy_(
                                    kind=bstack11l1l_opy_ (u"ࠨࡔࡆࡕࡗࡣࡆ࡚ࡔࡂࡅࡋࡑࡊࡔࡔࠣ፛"),
                                    message=bstack11l1l_opy_ (u"ࠢࠣ፜"),
                                    level=level,
                                    timestamp=timestamp,
                                    fileName=file_name,
                                    bstack1l1ll11111l_opy_=file_size,
                                    bstack1l1l1llll11_opy_=bstack11l1l_opy_ (u"ࠣࡏࡄࡒ࡚ࡇࡌࡠࡗࡓࡐࡔࡇࡄࠣ፝"),
                                    bstack1llllll_opy_=os.path.abspath(file_path),
                                    bstack1lll111lll_opy_=bstack1l1l1lll111_opy_
                                )
                            elif level == bstack11l1l_opy_ (u"ࠤࡅࡹ࡮ࡲࡤࡍࡧࡹࡩࡱࠨ፞"):
                                entry = bstack1lll111l1l1_opy_(
                                    kind=bstack11l1l_opy_ (u"ࠥࡘࡊ࡙ࡔࡠࡃࡗࡘࡆࡉࡈࡎࡇࡑࡘࠧ፟"),
                                    message=bstack11l1l_opy_ (u"ࠦࠧ፠"),
                                    level=level,
                                    timestamp=timestamp,
                                    fileName=file_name,
                                    bstack1l1ll11111l_opy_=file_size,
                                    bstack1l1l1llll11_opy_=bstack11l1l_opy_ (u"ࠧࡓࡁࡏࡗࡄࡐࡤ࡛ࡐࡍࡑࡄࡈࠧ፡"),
                                    bstack1llllll_opy_=os.path.abspath(file_path),
                                    bstack1l1l1l1111l_opy_=bstack1l1l1lll111_opy_
                                )
                            bstack1l1l1l111ll_opy_.append(entry)
                            _1l1l11l1l1l_opy_.add(abs_path)
                        except Exception as bstack1l1l1ll1l11_opy_:
                            self.logger.error(bstack11l1l_opy_ (u"ࠨࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢࡵࡥ࡮ࡹࡥࡥࠢࡺ࡬ࡪࡴࠠࡱࡴࡲࡧࡪࡹࡳࡪࡰࡪࠤࡦࡺࡴࡢࡥ࡫ࡱࡪࡴࡴࡴࠢࡾࢁࠧ።").format(bstack1l1l1ll1l11_opy_))
        except Exception as e:
            self.logger.error(bstack11l1l_opy_ (u"ࠢࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣࡶࡦ࡯ࡳࡦࡦࠣࡻ࡭࡫࡮ࠡࡲࡵࡳࡨ࡫ࡳࡴ࡫ࡱ࡫ࠥࡧࡴࡵࡣࡦ࡬ࡲ࡫࡮ࡵࡵࠣࡿࢂࠨ፣").format(e))
        event[bstack11l1l_opy_ (u"ࠣ࡮ࡲ࡫ࡸࠨ፤")] = bstack1l1l1l111ll_opy_
class bstack1l1l11ll1ll_opy_(JSONEncoder):
    def __init__(self, **kwargs):
        self.bstack1l1l11ll1l1_opy_ = set()
        kwargs[bstack11l1l_opy_ (u"ࠤࡶ࡯࡮ࡶ࡫ࡦࡻࡶࠦ፥")] = True
        super().__init__(**kwargs)
    def default(self, obj):
        return bstack1l1l11l1111_opy_(obj, self.bstack1l1l11ll1l1_opy_)
def bstack1l1l111l1ll_opy_(obj):
    return isinstance(obj, (str, int, float, bool, type(None)))
def bstack1l1l11l1111_opy_(obj, bstack1l1l11ll1l1_opy_=None, max_depth=3):
    if bstack1l1l11ll1l1_opy_ is None:
        bstack1l1l11ll1l1_opy_ = set()
    if id(obj) in bstack1l1l11ll1l1_opy_ or max_depth <= 0:
        return None
    max_depth -= 1
    bstack1l1l11ll1l1_opy_.add(id(obj))
    if isinstance(obj, datetime):
        return obj.isoformat()
    bstack1l1l11lll11_opy_ = TestFramework.bstack1l1l1ll1lll_opy_(obj)
    bstack1l1l111l1l1_opy_ = next((k.lower() in bstack1l1l11lll11_opy_.lower() for k in bstack1l1l1l11111_opy_.keys()), None)
    if bstack1l1l111l1l1_opy_:
        obj = TestFramework.bstack1l1ll11l11l_opy_(obj, bstack1l1l1l11111_opy_[bstack1l1l111l1l1_opy_])
    if not isinstance(obj, dict):
        keys = []
        if hasattr(obj, bstack11l1l_opy_ (u"ࠥࡣࡤࡹ࡬ࡰࡶࡶࡣࡤࠨ፦")):
            keys = getattr(obj, bstack11l1l_opy_ (u"ࠦࡤࡥࡳ࡭ࡱࡷࡷࡤࡥࠢ፧"), [])
        elif hasattr(obj, bstack11l1l_opy_ (u"ࠧࡥ࡟ࡥ࡫ࡦࡸࡤࡥࠢ፨")):
            keys = getattr(obj, bstack11l1l_opy_ (u"ࠨ࡟ࡠࡦ࡬ࡧࡹࡥ࡟ࠣ፩"), {}).keys()
        else:
            keys = dir(obj)
        obj = {k: getattr(obj, k, None) for k in keys if not str(k).startswith(bstack11l1l_opy_ (u"ࠢࡠࠤ፪"))}
        if not obj and bstack1l1l11lll11_opy_ == bstack11l1l_opy_ (u"ࠣࡲࡤࡸ࡭ࡲࡩࡣ࠰ࡓࡳࡸ࡯ࡸࡑࡣࡷ࡬ࠧ፫"):
            obj = {bstack11l1l_opy_ (u"ࠤࡳࡥࡹ࡮ࠢ፬"): str(obj)}
    result = {}
    for key, value in obj.items():
        if not bstack1l1l111l1ll_opy_(key) or str(key).startswith(bstack11l1l_opy_ (u"ࠥࡣࠧ፭")):
            continue
        if value is not None and bstack1l1l111l1ll_opy_(value):
            result[key] = value
        elif isinstance(value, dict):
            r = bstack1l1l11l1111_opy_(value, bstack1l1l11ll1l1_opy_, max_depth)
            if r is not None:
                result[key] = r
        elif isinstance(value, (list, tuple, set, frozenset)):
            result[key] = list(filter(None, [bstack1l1l11l1111_opy_(o, bstack1l1l11ll1l1_opy_, max_depth) for o in value]))
    return result or None