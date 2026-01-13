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
import json
import time
from datetime import datetime, timezone
from browserstack_sdk.sdk_cli.bstack1llll11l1ll_opy_ import (
    bstack1llll1111l1_opy_,
    bstack1lll1lll1l1_opy_,
    bstack1llll111ll1_opy_,
    bstack1llll1ll1ll_opy_,
    bstack1llll1lll11_opy_,
)
from browserstack_sdk.sdk_cli.bstack1lll1l11l11_opy_ import bstack1lll11l111l_opy_
from browserstack_sdk.sdk_cli.test_framework import TestFramework, bstack1lll111l111_opy_, bstack1lll1l1l11l_opy_, bstack1ll1ll11lll_opy_
from browserstack_sdk.sdk_cli.bstack1l1ll11l1l1_opy_ import bstack1l1ll11ll11_opy_
from typing import Tuple, Dict, Any, List, Union
from bstack_utils.helper import bstack1l1l1111l1l_opy_
from browserstack_sdk import sdk_pb2 as structs
from bstack_utils.measure import measure
from bstack_utils.constants import *
from typing import Tuple, List, Any
class bstack1ll11ll1l1l_opy_(bstack1l1ll11ll11_opy_):
    bstack1l11l1l11ll_opy_ = bstack11l1l_opy_ (u"ࠥࡸࡪࡹࡴࡠࡦࡵ࡭ࡻ࡫ࡲࡴࠤᑔ")
    bstack1l1l1l1lll1_opy_ = bstack11l1l_opy_ (u"ࠦࡦࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࡠࡵࡨࡷࡸ࡯࡯࡯ࡵࠥᑕ")
    bstack1l11l1l111l_opy_ = bstack11l1l_opy_ (u"ࠧࡴ࡯࡯ࡡࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡣࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࡤࡹࡥࡴࡵ࡬ࡳࡳࡹࠢᑖ")
    bstack1l11l1llll1_opy_ = bstack11l1l_opy_ (u"ࠨࡴࡦࡵࡷࡣࡸ࡫ࡳࡴ࡫ࡲࡲࡸࠨᑗ")
    bstack1l11l1ll1ll_opy_ = bstack11l1l_opy_ (u"ࠢࡢࡷࡷࡳࡲࡧࡴࡪࡱࡱࡣ࡮ࡴࡳࡵࡣࡱࡧࡪࡥࡲࡦࡨࡶࠦᑘ")
    bstack1l1ll1111ll_opy_ = bstack11l1l_opy_ (u"ࠣࡥࡥࡸࡤࡹࡥࡴࡵ࡬ࡳࡳࡥࡣࡳࡧࡤࡸࡪࡪࠢᑙ")
    bstack1l11l1l11l1_opy_ = bstack11l1l_opy_ (u"ࠤࡦࡦࡹࡥࡳࡦࡵࡶ࡭ࡴࡴ࡟࡯ࡣࡰࡩࠧᑚ")
    bstack1l11ll11111_opy_ = bstack11l1l_opy_ (u"ࠥࡧࡧࡺ࡟ࡴࡧࡶࡷ࡮ࡵ࡮ࡠࡵࡷࡥࡹࡻࡳࠣᑛ")
    def __init__(self):
        super().__init__(bstack1l1ll11l1ll_opy_=self.bstack1l11l1l11ll_opy_, frameworks=[bstack1lll11l111l_opy_.NAME])
        if not self.is_enabled():
            return
        TestFramework.bstack1ll111ll111_opy_((bstack1lll111l111_opy_.BEFORE_EACH, bstack1lll1l1l11l_opy_.POST), self.bstack1l111l1l11l_opy_)
        TestFramework.bstack1ll111ll111_opy_((bstack1lll111l111_opy_.TEST, bstack1lll1l1l11l_opy_.PRE), self.bstack1ll111l1l11_opy_)
        TestFramework.bstack1ll111ll111_opy_((bstack1lll111l111_opy_.TEST, bstack1lll1l1l11l_opy_.POST), self.bstack1l1llll1l11_opy_)
    def is_enabled(self) -> bool:
        return True
    def bstack1l111l1l11l_opy_(
        self,
        f: TestFramework,
        instance: bstack1ll1ll11lll_opy_,
        bstack1llll1lll1l_opy_: Tuple[bstack1lll111l111_opy_, bstack1lll1l1l11l_opy_],
        *args,
        **kwargs,
    ):
        bstack1l1l11l11l1_opy_ = self.bstack1l111l1lll1_opy_(instance.context)
        if not bstack1l1l11l11l1_opy_:
            self.logger.debug(bstack11l1l_opy_ (u"ࠦࡸ࡫ࡴࡠࡣࡦࡸ࡮ࡼࡥࡠࡦࡵ࡭ࡻ࡫ࡲࡴ࠼ࠣࡲࡴࠦࡤࡳ࡫ࡹࡩࡷࠦࡦࡰࡴࠣ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࡃࠢᑜ") + str(bstack1llll1lll1l_opy_) + bstack11l1l_opy_ (u"ࠧࠨᑝ"))
        f.bstack1lllll1111l_opy_(instance, bstack1ll11ll1l1l_opy_.bstack1l1l1l1lll1_opy_, bstack1l1l11l11l1_opy_)
        bstack1l111ll1111_opy_ = self.bstack1l111l1lll1_opy_(instance.context, bstack1l111ll11l1_opy_=False)
        f.bstack1lllll1111l_opy_(instance, bstack1ll11ll1l1l_opy_.bstack1l11l1l111l_opy_, bstack1l111ll1111_opy_)
    def bstack1ll111l1l11_opy_(
        self,
        f: TestFramework,
        instance: bstack1ll1ll11lll_opy_,
        bstack1llll1lll1l_opy_: Tuple[bstack1lll111l111_opy_, bstack1lll1l1l11l_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1l111l1l11l_opy_(f, instance, bstack1llll1lll1l_opy_, *args, **kwargs)
        if not f.bstack1llll1lllll_opy_(instance, bstack1ll11ll1l1l_opy_.bstack1l11l1l11l1_opy_, False):
            self.__1l111l1l1ll_opy_(f,instance,bstack1llll1lll1l_opy_)
    def bstack1l1llll1l11_opy_(
        self,
        f: TestFramework,
        instance: bstack1ll1ll11lll_opy_,
        bstack1llll1lll1l_opy_: Tuple[bstack1lll111l111_opy_, bstack1lll1l1l11l_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1l111l1l11l_opy_(f, instance, bstack1llll1lll1l_opy_, *args, **kwargs)
        if not f.bstack1llll1lllll_opy_(instance, bstack1ll11ll1l1l_opy_.bstack1l11l1l11l1_opy_, False):
            self.__1l111l1l1ll_opy_(f, instance, bstack1llll1lll1l_opy_)
        if not f.bstack1llll1lllll_opy_(instance, bstack1ll11ll1l1l_opy_.bstack1l11ll11111_opy_, False):
            self.__1l111ll1l11_opy_(f, instance, bstack1llll1lll1l_opy_)
    def bstack1l111l1l1l1_opy_(
        self,
        f: bstack1lll11l111l_opy_,
        driver: object,
        exec: Tuple[bstack1llll1ll1ll_opy_, str],
        bstack1llll1lll1l_opy_: Tuple[bstack1llll1111l1_opy_, bstack1lll1lll1l1_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance = exec[0]
        if not f.bstack1l1ll1l1l1l_opy_(instance):
            return
        if f.bstack1llll1lllll_opy_(instance, bstack1ll11ll1l1l_opy_.bstack1l11ll11111_opy_, False):
            return
        driver.execute_script(
            bstack11l1l_opy_ (u"ࠨࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤ࡫ࡸࡦࡥࡸࡸࡴࡸ࠺ࠡࡽࢀࠦᑞ").format(
                json.dumps(
                    {
                        bstack11l1l_opy_ (u"ࠢࡢࡥࡷ࡭ࡴࡴࠢᑟ"): bstack11l1l_opy_ (u"ࠣࡵࡨࡸࡘ࡫ࡳࡴ࡫ࡲࡲࡘࡺࡡࡵࡷࡶࠦᑠ"),
                        bstack11l1l_opy_ (u"ࠤࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠧᑡ"): {bstack11l1l_opy_ (u"ࠥࡷࡹࡧࡴࡶࡵࠥᑢ"): result},
                    }
                )
            )
        )
        f.bstack1lllll1111l_opy_(instance, bstack1ll11ll1l1l_opy_.bstack1l11ll11111_opy_, True)
    def bstack1l111l1lll1_opy_(self, context: bstack1llll1lll11_opy_, bstack1l111ll11l1_opy_= True):
        if bstack1l111ll11l1_opy_:
            bstack1l1l11l11l1_opy_ = self.bstack1l1ll11ll1l_opy_(context, reverse=True)
        else:
            bstack1l1l11l11l1_opy_ = self.bstack1l1ll1l111l_opy_(context, reverse=True)
        return [f for f in bstack1l1l11l11l1_opy_ if f[1].state != bstack1llll1111l1_opy_.QUIT]
    @measure(event_name=EVENTS.bstack11111l111_opy_, stage=STAGE.bstack1lll1l11l_opy_)
    def __1l111ll1l11_opy_(
        self,
        f: TestFramework,
        instance: bstack1ll1ll11lll_opy_,
        bstack1llll1lll1l_opy_: Tuple[bstack1lll111l111_opy_, bstack1lll1l1l11l_opy_],
    ):
        from browserstack_sdk.sdk_cli.cli import cli
        if not cli.config.get(bstack11l1l_opy_ (u"ࠦࡹ࡫ࡳࡵࡅࡲࡲࡹ࡫ࡸࡵࡑࡳࡸ࡮ࡵ࡮ࡴࠤᑣ")).get(bstack11l1l_opy_ (u"ࠧࡹ࡫ࡪࡲࡖࡩࡸࡹࡩࡰࡰࡖࡸࡦࡺࡵࡴࠤᑤ")):
            bstack1l1l11l11l1_opy_ = f.bstack1llll1lllll_opy_(instance, bstack1ll11ll1l1l_opy_.bstack1l1l1l1lll1_opy_, [])
            if not bstack1l1l11l11l1_opy_:
                self.logger.debug(bstack11l1l_opy_ (u"ࠨࡳࡦࡶࡢࡥࡨࡺࡩࡷࡧࡢࡨࡷ࡯ࡶࡦࡴࡶ࠾ࠥࡴ࡯ࠡࡦࡵ࡭ࡻ࡫ࡲࠡࡨࡲࡶࠥ࡮࡯ࡰ࡭ࡢ࡭ࡳ࡬࡯࠾ࠤᑥ") + str(bstack1llll1lll1l_opy_) + bstack11l1l_opy_ (u"ࠢࠣᑦ"))
                return
            driver = bstack1l1l11l11l1_opy_[0][0]()
            status = f.bstack1llll1lllll_opy_(instance, TestFramework.bstack1l11l1lllll_opy_, None)
            if not status:
                self.logger.debug(bstack11l1l_opy_ (u"ࠣࡵࡨࡸࡤࡧࡣࡵ࡫ࡹࡩࡤࡪࡲࡪࡸࡨࡶࡸࡀࠠ࡯ࡱࠣࡷࡹࡧࡴࡶࡵࠣࡪࡴࡸࠠࡵࡧࡶࡸ࠱ࠦࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰ࠿ࠥᑧ") + str(bstack1llll1lll1l_opy_) + bstack11l1l_opy_ (u"ࠤࠥᑨ"))
                return
            bstack1l11l1l1l1l_opy_ = {bstack11l1l_opy_ (u"ࠥࡷࡹࡧࡴࡶࡵࠥᑩ"): status.lower()}
            bstack1l11l1l1l11_opy_ = f.bstack1llll1lllll_opy_(instance, TestFramework.bstack1l11l1ll1l1_opy_, None)
            if status.lower() == bstack11l1l_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡧࡧࠫᑪ") and bstack1l11l1l1l11_opy_ is not None:
                bstack1l11l1l1l1l_opy_[bstack11l1l_opy_ (u"ࠬࡸࡥࡢࡵࡲࡲࠬᑫ")] = bstack1l11l1l1l11_opy_[0][bstack11l1l_opy_ (u"࠭ࡢࡢࡥ࡮ࡸࡷࡧࡣࡦࠩᑬ")][0] if isinstance(bstack1l11l1l1l11_opy_, list) else str(bstack1l11l1l1l11_opy_)
            driver.execute_script(
                bstack11l1l_opy_ (u"ࠢࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡥࡹࡧࡦࡹࡹࡵࡲ࠻ࠢࡾࢁࠧᑭ").format(
                    json.dumps(
                        {
                            bstack11l1l_opy_ (u"ࠣࡣࡦࡸ࡮ࡵ࡮ࠣᑮ"): bstack11l1l_opy_ (u"ࠤࡶࡩࡹ࡙ࡥࡴࡵ࡬ࡳࡳ࡙ࡴࡢࡶࡸࡷࠧᑯ"),
                            bstack11l1l_opy_ (u"ࠥࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸࠨᑰ"): bstack1l11l1l1l1l_opy_,
                        }
                    )
                )
            )
            f.bstack1lllll1111l_opy_(instance, bstack1ll11ll1l1l_opy_.bstack1l11ll11111_opy_, True)
    @measure(event_name=EVENTS.bstack1111ll11l_opy_, stage=STAGE.bstack1lll1l11l_opy_)
    def __1l111l1l1ll_opy_(
        self,
        f: TestFramework,
        instance: bstack1ll1ll11lll_opy_,
        bstack1llll1lll1l_opy_: Tuple[bstack1lll111l111_opy_, bstack1lll1l1l11l_opy_]
    ):
        from browserstack_sdk.sdk_cli.cli import cli
        if not cli.config.get(bstack11l1l_opy_ (u"ࠦࡹ࡫ࡳࡵࡅࡲࡲࡹ࡫ࡸࡵࡑࡳࡸ࡮ࡵ࡮ࡴࠤᑱ")).get(bstack11l1l_opy_ (u"ࠧࡹ࡫ࡪࡲࡖࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠢᑲ")):
            test_name = f.bstack1llll1lllll_opy_(instance, TestFramework.bstack1l111ll11ll_opy_, None)
            if not test_name:
                self.logger.debug(bstack11l1l_opy_ (u"ࠨ࡯࡯ࡡࡥࡩ࡫ࡵࡲࡦࡡࡷࡩࡸࡺ࠺ࠡ࡯࡬ࡷࡸ࡯࡮ࡨࠢࡷࡩࡸࡺࠠ࡯ࡣࡰࡩࠧᑳ"))
                return
            bstack1l1l11l11l1_opy_ = f.bstack1llll1lllll_opy_(instance, bstack1ll11ll1l1l_opy_.bstack1l1l1l1lll1_opy_, [])
            if not bstack1l1l11l11l1_opy_:
                self.logger.debug(bstack11l1l_opy_ (u"ࠢࡴࡧࡷࡣࡦࡩࡴࡪࡸࡨࡣࡩࡸࡩࡷࡧࡵࡷ࠿ࠦ࡮ࡰࠢࡶࡸࡦࡺࡵࡴࠢࡩࡳࡷࠦࡴࡦࡵࡷ࠰ࠥ࡮࡯ࡰ࡭ࡢ࡭ࡳ࡬࡯࠾ࠤᑴ") + str(bstack1llll1lll1l_opy_) + bstack11l1l_opy_ (u"ࠣࠤᑵ"))
                return
            for bstack1l11lll1ll1_opy_, bstack1l111ll111l_opy_ in bstack1l1l11l11l1_opy_:
                if not bstack1lll11l111l_opy_.bstack1l1ll1l1l1l_opy_(bstack1l111ll111l_opy_):
                    continue
                driver = bstack1l11lll1ll1_opy_()
                if not driver:
                    continue
                driver.execute_script(
                    bstack11l1l_opy_ (u"ࠤࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡧࡻࡩࡨࡻࡴࡰࡴ࠽ࠤࢀࢃࠢᑶ").format(
                        json.dumps(
                            {
                                bstack11l1l_opy_ (u"ࠥࡥࡨࡺࡩࡰࡰࠥᑷ"): bstack11l1l_opy_ (u"ࠦࡸ࡫ࡴࡔࡧࡶࡷ࡮ࡵ࡮ࡏࡣࡰࡩࠧᑸ"),
                                bstack11l1l_opy_ (u"ࠧࡧࡲࡨࡷࡰࡩࡳࡺࡳࠣᑹ"): {bstack11l1l_opy_ (u"ࠨ࡮ࡢ࡯ࡨࠦᑺ"): test_name},
                            }
                        )
                    )
                )
            f.bstack1lllll1111l_opy_(instance, bstack1ll11ll1l1l_opy_.bstack1l11l1l11l1_opy_, True)
    def bstack1l1l1llll1l_opy_(
        self,
        instance: bstack1ll1ll11lll_opy_,
        f: TestFramework,
        bstack1llll1lll1l_opy_: Tuple[bstack1lll111l111_opy_, bstack1lll1l1l11l_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1l111l1l11l_opy_(f, instance, bstack1llll1lll1l_opy_, *args, **kwargs)
        bstack1l1l11l11l1_opy_ = [d for d, _ in f.bstack1llll1lllll_opy_(instance, bstack1ll11ll1l1l_opy_.bstack1l1l1l1lll1_opy_, [])]
        if not bstack1l1l11l11l1_opy_:
            self.logger.debug(bstack11l1l_opy_ (u"ࠢࡰࡰࡢࡥ࡫ࡺࡥࡳࡡࡷࡩࡸࡺ࠺ࠡࡰࡲࠤࡸ࡫ࡳࡴ࡫ࡲࡲࡸࠦࡴࡰࠢ࡯࡭ࡳࡱࠢᑻ"))
            return
        if not bstack1l1l1111l1l_opy_():
            self.logger.debug(bstack11l1l_opy_ (u"ࠣࡱࡱࡣࡦ࡬ࡴࡦࡴࡢࡸࡪࡹࡴ࠻ࠢࡱࡳࡹࠦࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࠥࡹࡥࡴࡵ࡬ࡳࡳࠨᑼ"))
            return
        for bstack1l111l1llll_opy_ in bstack1l1l11l11l1_opy_:
            driver = bstack1l111l1llll_opy_()
            if not driver:
                continue
            timestamp = int(time.time() * 1000)
            data = bstack11l1l_opy_ (u"ࠤࡒࡦࡸ࡫ࡲࡷࡣࡥ࡭ࡱ࡯ࡴࡺࡕࡼࡲࡨࡀࠢᑽ") + str(timestamp)
            driver.execute_script(
                bstack11l1l_opy_ (u"ࠥࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡨࡼࡪࡩࡵࡵࡱࡵ࠾ࠥࢁࡽࠣᑾ").format(
                    json.dumps(
                        {
                            bstack11l1l_opy_ (u"ࠦࡦࡩࡴࡪࡱࡱࠦᑿ"): bstack11l1l_opy_ (u"ࠧࡧ࡮࡯ࡱࡷࡥࡹ࡫ࠢᒀ"),
                            bstack11l1l_opy_ (u"ࠨࡡࡳࡩࡸࡱࡪࡴࡴࡴࠤᒁ"): {
                                bstack11l1l_opy_ (u"ࠢࡵࡻࡳࡩࠧᒂ"): bstack11l1l_opy_ (u"ࠣࡃࡱࡲࡴࡺࡡࡵ࡫ࡲࡲࠧᒃ"),
                                bstack11l1l_opy_ (u"ࠤࡧࡥࡹࡧࠢᒄ"): data,
                                bstack11l1l_opy_ (u"ࠥࡰࡪࡼࡥ࡭ࠤᒅ"): bstack11l1l_opy_ (u"ࠦࡩ࡫ࡢࡶࡩࠥᒆ")
                            }
                        }
                    )
                )
            )
    def bstack1l1l1l1llll_opy_(
        self,
        instance: bstack1ll1ll11lll_opy_,
        f: TestFramework,
        bstack1llll1lll1l_opy_: Tuple[bstack1lll111l111_opy_, bstack1lll1l1l11l_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1l111l1l11l_opy_(f, instance, bstack1llll1lll1l_opy_, *args, **kwargs)
        keys = [
            bstack1ll11ll1l1l_opy_.bstack1l1l1l1lll1_opy_,
            bstack1ll11ll1l1l_opy_.bstack1l11l1l111l_opy_,
        ]
        bstack1l1l11l11l1_opy_ = []
        for key in keys:
            bstack1l1l11l11l1_opy_.extend(f.bstack1llll1lllll_opy_(instance, key, []))
        if not bstack1l1l11l11l1_opy_:
            self.logger.debug(bstack11l1l_opy_ (u"ࠧࡵ࡮ࡠࡣࡩࡸࡪࡸ࡟ࡵࡧࡶࡸ࠿ࠦࡵ࡯ࡣࡥࡰࡪࠦࡴࡰࠢࡩ࡭ࡳࡪࠠࡢࡰࡼࠤࡸ࡫ࡳࡴ࡫ࡲࡲࡸࠦࡴࡰࠢ࡯࡭ࡳࡱࠢᒇ"))
            return
        if f.bstack1llll1lllll_opy_(instance, bstack1ll11ll1l1l_opy_.bstack1l1ll1111ll_opy_, False):
            self.logger.debug(bstack11l1l_opy_ (u"ࠨ࡯࡯ࡡࡤࡪࡹ࡫ࡲࡠࡶࡨࡷࡹࡀࠠࡄࡄࡗࠤࡦࡲࡲࡦࡣࡧࡽࠥࡩࡲࡦࡣࡷࡩࡩࠨᒈ"))
            return
        self.bstack1ll11111lll_opy_()
        bstack11ll1l1ll1_opy_ = datetime.now()
        req = structs.TestSessionEventRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = TestFramework.bstack1llll1lllll_opy_(instance, TestFramework.bstack1ll1111l111_opy_)
        req.test_framework_name = TestFramework.bstack1llll1lllll_opy_(instance, TestFramework.bstack1l1llll11l1_opy_)
        req.test_framework_version = TestFramework.bstack1llll1lllll_opy_(instance, TestFramework.bstack1l1l1lll1ll_opy_)
        req.test_framework_state = bstack1llll1lll1l_opy_[0].name
        req.test_hook_state = bstack1llll1lll1l_opy_[1].name
        req.test_uuid = TestFramework.bstack1llll1lllll_opy_(instance, TestFramework.bstack1ll11l11l1l_opy_)
        for bstack1l11lll1ll1_opy_, driver in bstack1l1l11l11l1_opy_:
            try:
                webdriver = bstack1l11lll1ll1_opy_()
                if webdriver is None:
                    self.logger.debug(bstack11l1l_opy_ (u"ࠢࡘࡧࡥࡈࡷ࡯ࡶࡦࡴࠣ࡭ࡳࡹࡴࡢࡰࡦࡩࠥ࡯ࡳࠡࡐࡲࡲࡪࠦࠨࡳࡧࡩࡩࡷ࡫࡮ࡤࡧࠣࡩࡽࡶࡩࡳࡧࡧ࠭ࠧᒉ"))
                    continue
                session = req.automation_sessions.add()
                session.provider = (
                    bstack11l1l_opy_ (u"ࠣࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠢᒊ")
                    if bstack1lll11l111l_opy_.bstack1llll1lllll_opy_(driver, bstack1lll11l111l_opy_.bstack1l111l1l111_opy_, False)
                    else bstack11l1l_opy_ (u"ࠤࡸࡲࡰࡴ࡯ࡸࡰࡢ࡫ࡷ࡯ࡤࠣᒋ")
                )
                session.ref = driver.ref()
                session.hub_url = bstack1lll11l111l_opy_.bstack1llll1lllll_opy_(driver, bstack1lll11l111l_opy_.bstack1l11ll1l1l1_opy_, bstack11l1l_opy_ (u"ࠥࠦᒌ"))
                session.framework_name = driver.framework_name
                session.framework_version = driver.framework_version
                session.framework_session_id = bstack1lll11l111l_opy_.bstack1llll1lllll_opy_(driver, bstack1lll11l111l_opy_.bstack1l11lll1l11_opy_, bstack11l1l_opy_ (u"ࠦࠧᒍ"))
                caps = None
                if hasattr(webdriver, bstack11l1l_opy_ (u"ࠧࡩࡡࡱࡣࡥ࡭ࡱ࡯ࡴࡪࡧࡶࠦᒎ")):
                    try:
                        caps = webdriver.capabilities
                        self.logger.debug(bstack11l1l_opy_ (u"ࠨࡓࡶࡥࡦࡩࡸࡹࡦࡶ࡮࡯ࡽࠥࡸࡥࡵࡴ࡬ࡩࡻ࡫ࡤࠡࡥࡤࡴࡦࡨࡩ࡭࡫ࡷ࡭ࡪࡹࠠࡥ࡫ࡵࡩࡨࡺ࡬ࡺࠢࡩࡶࡴࡳࠠࡥࡴ࡬ࡺࡪࡸ࠮ࡤࡣࡳࡥࡧ࡯࡬ࡪࡶ࡬ࡩࡸࠨᒏ"))
                    except Exception as e:
                        self.logger.debug(bstack11l1l_opy_ (u"ࠢࡇࡣ࡬ࡰࡪࡪࠠࡵࡱࠣ࡫ࡪࡺࠠࡤࡣࡳࡥࡧ࡯࡬ࡪࡶ࡬ࡩࡸࠦࡦࡳࡱࡰࠤࡩࡸࡩࡷࡧࡵ࠲ࡨࡧࡰࡢࡤ࡬ࡰ࡮ࡺࡩࡦࡵ࠽ࠤࠧᒐ") + str(e) + bstack11l1l_opy_ (u"ࠣࠤᒑ"))
                try:
                    bstack1l111l1ll11_opy_ = json.dumps(caps).encode(bstack11l1l_opy_ (u"ࠤࡸࡸ࡫࠳࠸ࠣᒒ")) if caps else bstack1l111l1ll1l_opy_ (u"ࠥࡿࢂࠨᒓ")
                    req.capabilities = bstack1l111l1ll11_opy_
                except Exception as e:
                    self.logger.debug(bstack11l1l_opy_ (u"ࠦ࡬࡫ࡴࡠࡥࡥࡸࡤ࡫ࡶࡦࡰࡷ࠾ࠥ࡬ࡡࡪ࡮ࡨࡨࠥࡺ࡯ࠡࡵࡨࡲࡩࠦࡳࡦࡴ࡬ࡥࡱ࡯ࡺࡦࠢࡦࡥࡵࡹࠠࡧࡱࡵࠤࡷ࡫ࡱࡶࡧࡶࡸ࠿ࠦࠢᒔ") + str(e) + bstack11l1l_opy_ (u"ࠧࠨᒕ"))
            except Exception as e:
                self.logger.error(bstack11l1l_opy_ (u"ࠨࡅࡳࡴࡲࡶࠥࡶࡲࡰࡥࡨࡷࡸ࡯࡮ࡨࠢࡧࡶ࡮ࡼࡥࡳࠢ࡬ࡸࡪࡳ࠺ࠡࠤᒖ") + str(str(e)) + bstack11l1l_opy_ (u"ࠢࠣᒗ"))
        req.execution_context.hash = str(instance.context.hash)
        req.execution_context.thread_id = str(instance.context.thread_id)
        req.execution_context.process_id = str(instance.context.process_id)
        return req
    def bstack1l1lll1l1ll_opy_(
        self,
        f: TestFramework,
        instance: bstack1ll1ll11lll_opy_,
        bstack1llll1lll1l_opy_: Tuple[bstack1lll111l111_opy_, bstack1lll1l1l11l_opy_],
        *args,
        **kwargs
    ):
        bstack1l1l11l11l1_opy_ = f.bstack1llll1lllll_opy_(instance, bstack1ll11ll1l1l_opy_.bstack1l1l1l1lll1_opy_, [])
        if not bstack1l1l1111l1l_opy_() and len(bstack1l1l11l11l1_opy_) == 0:
            bstack1l1l11l11l1_opy_ = f.bstack1llll1lllll_opy_(instance, bstack1ll11ll1l1l_opy_.bstack1l11l1l111l_opy_, [])
        if not bstack1l1l11l11l1_opy_:
            self.logger.debug(bstack11l1l_opy_ (u"ࠣࡱࡱࡣࡧ࡫ࡦࡰࡴࡨࡣࡹ࡫ࡳࡵ࠼ࠣࡲࡴࠦࡤࡳ࡫ࡹࡩࡷࡹࠠࡧࡱࡵࠤ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵ࠽ࡼࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࢁࠥࡧࡲࡨࡵࡀࡿࡦࡸࡧࡴࡿࠣ࡯ࡼࡧࡲࡨࡵࡀࠦᒘ") + str(kwargs) + bstack11l1l_opy_ (u"ࠤࠥᒙ"))
            return {}
        if len(bstack1l1l11l11l1_opy_) > 1:
            self.logger.debug(bstack11l1l_opy_ (u"ࠥࡳࡳࡥࡢࡦࡨࡲࡶࡪࡥࡴࡦࡵࡷ࠾ࠥࢁ࡬ࡦࡰࠫࡨࡷ࡯ࡶࡦࡴࡢ࡭ࡳࡹࡴࡢࡰࡦࡩࡸ࠯ࡽࠡࡦࡵ࡭ࡻ࡫ࡲࡴࠢࡩࡳࡷࠦࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰ࠿ࡾ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࢃࠠࡢࡴࡪࡷࡂࢁࡡࡳࡩࡶࢁࠥࡱࡷࡢࡴࡪࡷࡂࠨᒚ") + str(kwargs) + bstack11l1l_opy_ (u"ࠦࠧᒛ"))
            return {}
        bstack1l11lll1ll1_opy_, bstack1l1l11111l1_opy_ = bstack1l1l11l11l1_opy_[0]
        driver = bstack1l11lll1ll1_opy_()
        if not driver:
            self.logger.debug(bstack11l1l_opy_ (u"ࠧࡵ࡮ࡠࡤࡨࡪࡴࡸࡥࡠࡶࡨࡷࡹࡀࠠ࡯ࡱࠣࡨࡷ࡯ࡶࡦࡴࠣࡪࡴࡸࠠࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࡀࡿ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵࡽࠡࡣࡵ࡫ࡸࡃࡻࡢࡴࡪࡷࢂࠦ࡫ࡸࡣࡵ࡫ࡸࡃࠢᒜ") + str(kwargs) + bstack11l1l_opy_ (u"ࠨࠢᒝ"))
            return {}
        capabilities = f.bstack1llll1lllll_opy_(bstack1l1l11111l1_opy_, bstack1lll11l111l_opy_.bstack1l11ll11l1l_opy_)
        if not capabilities:
            self.logger.debug(bstack11l1l_opy_ (u"ࠢࡰࡰࡢࡦࡪ࡬࡯ࡳࡧࡢࡸࡪࡹࡴ࠻ࠢࡱࡳࠥࡩࡡࡱࡣࡥ࡭ࡱ࡯ࡴࡪࡧࡶࠤ࡫ࡵࡵ࡯ࡦࠣࡪࡴࡸࠠࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࡀࡿ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵࡽࠡࡣࡵ࡫ࡸࡃࡻࡢࡴࡪࡷࢂࠦ࡫ࡸࡣࡵ࡫ࡸࡃࠢᒞ") + str(kwargs) + bstack11l1l_opy_ (u"ࠣࠤᒟ"))
            return {}
        return capabilities.get(bstack11l1l_opy_ (u"ࠤࡤࡰࡼࡧࡹࡴࡏࡤࡸࡨ࡮ࠢᒠ"), {})
    def bstack1l1lllll111_opy_(
        self,
        f: TestFramework,
        instance: bstack1ll1ll11lll_opy_,
        bstack1llll1lll1l_opy_: Tuple[bstack1lll111l111_opy_, bstack1lll1l1l11l_opy_],
        *args,
        **kwargs
    ):
        bstack1l1l11l11l1_opy_ = f.bstack1llll1lllll_opy_(instance, bstack1ll11ll1l1l_opy_.bstack1l1l1l1lll1_opy_, [])
        if not bstack1l1l1111l1l_opy_() and len(bstack1l1l11l11l1_opy_) == 0:
            bstack1l1l11l11l1_opy_ = f.bstack1llll1lllll_opy_(instance, bstack1ll11ll1l1l_opy_.bstack1l11l1l111l_opy_, [])
        if not bstack1l1l11l11l1_opy_:
            self.logger.debug(bstack11l1l_opy_ (u"ࠥ࡫ࡪࡺ࡟ࡢࡷࡷࡳࡲࡧࡴࡪࡱࡱࡣࡩࡸࡩࡷࡧࡵ࠾ࠥࡴ࡯ࠡࡦࡵ࡭ࡻ࡫ࡲࡴࠢࡩࡳࡷࠦࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰ࠿ࡾ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࢃࠠࡢࡴࡪࡷࡂࢁࡡࡳࡩࡶࢁࠥࡱࡷࡢࡴࡪࡷࡂࠨᒡ") + str(kwargs) + bstack11l1l_opy_ (u"ࠦࠧᒢ"))
            return
        if len(bstack1l1l11l11l1_opy_) > 1:
            self.logger.debug(bstack11l1l_opy_ (u"ࠧ࡭ࡥࡵࡡࡤࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳࡥࡤࡳ࡫ࡹࡩࡷࡀࠠࡼ࡮ࡨࡲ࠭ࡪࡲࡪࡸࡨࡶࡤ࡯࡮ࡴࡶࡤࡲࡨ࡫ࡳࠪࡿࠣࡨࡷ࡯ࡶࡦࡴࡶࠤ࡫ࡵࡲࠡࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࡁࢀ࡮࡯ࡰ࡭ࡢ࡭ࡳ࡬࡯ࡾࠢࡤࡶ࡬ࡹ࠽ࡼࡣࡵ࡫ࡸࢃࠠ࡬ࡹࡤࡶ࡬ࡹ࠽ࠣᒣ") + str(kwargs) + bstack11l1l_opy_ (u"ࠨࠢᒤ"))
        bstack1l11lll1ll1_opy_, bstack1l1l11111l1_opy_ = bstack1l1l11l11l1_opy_[0]
        driver = bstack1l11lll1ll1_opy_()
        if not driver:
            self.logger.debug(bstack11l1l_opy_ (u"ࠢࡨࡧࡷࡣࡦࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࡠࡦࡵ࡭ࡻ࡫ࡲ࠻ࠢࡱࡳࠥࡪࡲࡪࡸࡨࡶࠥ࡬࡯ࡳࠢ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࡂࢁࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰࡿࠣࡥࡷ࡭ࡳ࠾ࡽࡤࡶ࡬ࡹࡽࠡ࡭ࡺࡥࡷ࡭ࡳ࠾ࠤᒥ") + str(kwargs) + bstack11l1l_opy_ (u"ࠣࠤᒦ"))
            return
        return driver