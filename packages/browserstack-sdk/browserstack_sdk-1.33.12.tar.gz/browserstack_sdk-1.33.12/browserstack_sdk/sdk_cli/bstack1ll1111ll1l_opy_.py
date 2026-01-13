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
import json
import time
from datetime import datetime, timezone
from browserstack_sdk.sdk_cli.bstack1ll11l1l1l1_opy_ import (
    bstack1ll11lllll1_opy_,
    bstack1ll11lll1ll_opy_,
    bstack1ll1l1111l1_opy_,
    bstack1ll1l1ll1l1_opy_,
    bstack1ll1111lll1_opy_,
)
from browserstack_sdk.sdk_cli.bstack1ll11l1lll1_opy_ import bstack1ll11ll1lll_opy_
from browserstack_sdk.sdk_cli.test_framework import TestFramework, bstack1llll1ll111_opy_, bstack1lll1111l11_opy_, bstack1lll1l11l11_opy_
from browserstack_sdk.sdk_cli.bstack1ll111l1ll1_opy_ import bstack1ll111l1l11_opy_
from typing import Tuple, Dict, Any, List, Union
from bstack_utils.helper import bstack1ll111l11l1_opy_
from browserstack_sdk import sdk_pb2 as structs
from bstack_utils.measure import measure
from bstack_utils.constants import *
from typing import Tuple, List, Any
class bstack1ll111ll1l1_opy_(bstack1ll111l1l11_opy_):
    bstack1ll111ll1ll_opy_ = bstack11ll1_opy_ (u"ࠣࡶࡨࡷࡹࡥࡤࡳ࡫ࡹࡩࡷࡹࠢኒ")
    bstack1ll111lllll_opy_ = bstack11ll1_opy_ (u"ࠤࡤࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳࡥࡳࡦࡵࡶ࡭ࡴࡴࡳࠣና")
    bstack1ll1111llll_opy_ = bstack11ll1_opy_ (u"ࠥࡲࡴࡴ࡟ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡡࡶࡶࡲࡱࡦࡺࡩࡰࡰࡢࡷࡪࡹࡳࡪࡱࡱࡷࠧኔ")
    bstack1ll1111l11l_opy_ = bstack11ll1_opy_ (u"ࠦࡹ࡫ࡳࡵࡡࡶࡩࡸࡹࡩࡰࡰࡶࠦን")
    bstack1ll11l1111l_opy_ = bstack11ll1_opy_ (u"ࠧࡧࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࡡ࡬ࡲࡸࡺࡡ࡯ࡥࡨࡣࡷ࡫ࡦࡴࠤኖ")
    bstack1l1llllllll_opy_ = bstack11ll1_opy_ (u"ࠨࡣࡣࡶࡢࡷࡪࡹࡳࡪࡱࡱࡣࡨࡸࡥࡢࡶࡨࡨࠧኗ")
    bstack1l1llllll11_opy_ = bstack11ll1_opy_ (u"ࠢࡤࡤࡷࡣࡸ࡫ࡳࡴ࡫ࡲࡲࡤࡴࡡ࡮ࡧࠥኘ")
    bstack1ll1111l1l1_opy_ = bstack11ll1_opy_ (u"ࠣࡥࡥࡸࡤࡹࡥࡴࡵ࡬ࡳࡳࡥࡳࡵࡣࡷࡹࡸࠨኙ")
    def __init__(self):
        super().__init__(bstack1ll111ll111_opy_=self.bstack1ll111ll1ll_opy_, frameworks=[bstack1ll11ll1lll_opy_.NAME])
        if not self.is_enabled():
            return
        TestFramework.bstack1ll1l11111l_opy_((bstack1llll1ll111_opy_.BEFORE_EACH, bstack1lll1111l11_opy_.POST), self.bstack1ll1111l1ll_opy_)
        TestFramework.bstack1ll1l11111l_opy_((bstack1llll1ll111_opy_.TEST, bstack1lll1111l11_opy_.PRE), self.bstack1ll11l11111_opy_)
        TestFramework.bstack1ll1l11111l_opy_((bstack1llll1ll111_opy_.TEST, bstack1lll1111l11_opy_.POST), self.bstack1l1llllll1l_opy_)
    def is_enabled(self) -> bool:
        return True
    def bstack1ll1111l1ll_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll1l11l11_opy_,
        bstack1lll1lll111_opy_: Tuple[bstack1llll1ll111_opy_, bstack1lll1111l11_opy_],
        *args,
        **kwargs,
    ):
        bstack1ll111l1111_opy_ = self.bstack1ll11111lll_opy_(instance.context)
        if not bstack1ll111l1111_opy_:
            self.logger.debug(bstack11ll1_opy_ (u"ࠤࡶࡩࡹࡥࡡࡤࡶ࡬ࡺࡪࡥࡤࡳ࡫ࡹࡩࡷࡹ࠺ࠡࡰࡲࠤࡩࡸࡩࡷࡧࡵࠤ࡫ࡵࡲࠡࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࡁࠧኚ") + str(bstack1lll1lll111_opy_) + bstack11ll1_opy_ (u"ࠥࠦኛ"))
        f.bstack1lll111ll11_opy_(instance, bstack1ll111ll1l1_opy_.bstack1ll111lllll_opy_, bstack1ll111l1111_opy_)
        bstack1ll11111111_opy_ = self.bstack1ll11111lll_opy_(instance.context, bstack1ll111ll11l_opy_=False)
        f.bstack1lll111ll11_opy_(instance, bstack1ll111ll1l1_opy_.bstack1ll1111llll_opy_, bstack1ll11111111_opy_)
    def bstack1ll11l11111_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll1l11l11_opy_,
        bstack1lll1lll111_opy_: Tuple[bstack1llll1ll111_opy_, bstack1lll1111l11_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1ll1111l1ll_opy_(f, instance, bstack1lll1lll111_opy_, *args, **kwargs)
        if not f.bstack1ll1llll11l_opy_(instance, bstack1ll111ll1l1_opy_.bstack1l1llllll11_opy_, False):
            self.__1ll111111ll_opy_(f,instance,bstack1lll1lll111_opy_)
    def bstack1l1llllll1l_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll1l11l11_opy_,
        bstack1lll1lll111_opy_: Tuple[bstack1llll1ll111_opy_, bstack1lll1111l11_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1ll1111l1ll_opy_(f, instance, bstack1lll1lll111_opy_, *args, **kwargs)
        if not f.bstack1ll1llll11l_opy_(instance, bstack1ll111ll1l1_opy_.bstack1l1llllll11_opy_, False):
            self.__1ll111111ll_opy_(f, instance, bstack1lll1lll111_opy_)
        if not f.bstack1ll1llll11l_opy_(instance, bstack1ll111ll1l1_opy_.bstack1ll1111l1l1_opy_, False):
            self.__1ll11111ll1_opy_(f, instance, bstack1lll1lll111_opy_)
    def bstack1ll111llll1_opy_(
        self,
        f: bstack1ll11ll1lll_opy_,
        driver: object,
        exec: Tuple[bstack1ll1l1ll1l1_opy_, str],
        bstack1lll1lll111_opy_: Tuple[bstack1ll11lllll1_opy_, bstack1ll11lll1ll_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance = exec[0]
        if not f.bstack1ll11l11lll_opy_(instance):
            return
        if f.bstack1ll1llll11l_opy_(instance, bstack1ll111ll1l1_opy_.bstack1ll1111l1l1_opy_, False):
            return
        driver.execute_script(
            bstack11ll1_opy_ (u"ࠦࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡩࡽ࡫ࡣࡶࡶࡲࡶ࠿ࠦࡻࡾࠤኜ").format(
                json.dumps(
                    {
                        bstack11ll1_opy_ (u"ࠧࡧࡣࡵ࡫ࡲࡲࠧኝ"): bstack11ll1_opy_ (u"ࠨࡳࡦࡶࡖࡩࡸࡹࡩࡰࡰࡖࡸࡦࡺࡵࡴࠤኞ"),
                        bstack11ll1_opy_ (u"ࠢࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠥኟ"): {bstack11ll1_opy_ (u"ࠣࡵࡷࡥࡹࡻࡳࠣአ"): result},
                    }
                )
            )
        )
        f.bstack1lll111ll11_opy_(instance, bstack1ll111ll1l1_opy_.bstack1ll1111l1l1_opy_, True)
    def bstack1ll11111lll_opy_(self, context: bstack1ll1111lll1_opy_, bstack1ll111ll11l_opy_= True):
        if bstack1ll111ll11l_opy_:
            bstack1ll111l1111_opy_ = self.bstack1l1lllllll1_opy_(context, reverse=True)
        else:
            bstack1ll111l1111_opy_ = self.bstack1ll1111111l_opy_(context, reverse=True)
        return [f for f in bstack1ll111l1111_opy_ if f[1].state != bstack1ll11lllll1_opy_.QUIT]
    @measure(event_name=EVENTS.bstack11llll111_opy_, stage=STAGE.bstack11l1llll1_opy_)
    def __1ll11111ll1_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll1l11l11_opy_,
        bstack1lll1lll111_opy_: Tuple[bstack1llll1ll111_opy_, bstack1lll1111l11_opy_],
    ):
        from browserstack_sdk.sdk_cli.cli import cli
        if not cli.config.get(bstack11ll1_opy_ (u"ࠤࡷࡩࡸࡺࡃࡰࡰࡷࡩࡽࡺࡏࡱࡶ࡬ࡳࡳࡹࠢኡ")).get(bstack11ll1_opy_ (u"ࠥࡷࡰ࡯ࡰࡔࡧࡶࡷ࡮ࡵ࡮ࡔࡶࡤࡸࡺࡹࠢኢ")):
            bstack1ll111l1111_opy_ = f.bstack1ll1llll11l_opy_(instance, bstack1ll111ll1l1_opy_.bstack1ll111lllll_opy_, [])
            if not bstack1ll111l1111_opy_:
                self.logger.debug(bstack11ll1_opy_ (u"ࠦࡸ࡫ࡴࡠࡣࡦࡸ࡮ࡼࡥࡠࡦࡵ࡭ࡻ࡫ࡲࡴ࠼ࠣࡲࡴࠦࡤࡳ࡫ࡹࡩࡷࠦࡦࡰࡴࠣ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࡃࠢኣ") + str(bstack1lll1lll111_opy_) + bstack11ll1_opy_ (u"ࠧࠨኤ"))
                return
            driver = bstack1ll111l1111_opy_[0][0]()
            status = f.bstack1ll1llll11l_opy_(instance, TestFramework.bstack1ll1ll1ll1l_opy_, None)
            if not status:
                self.logger.debug(bstack11ll1_opy_ (u"ࠨࡳࡦࡶࡢࡥࡨࡺࡩࡷࡧࡢࡨࡷ࡯ࡶࡦࡴࡶ࠾ࠥࡴ࡯ࠡࡵࡷࡥࡹࡻࡳࠡࡨࡲࡶࠥࡺࡥࡴࡶ࠯ࠤ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵ࠽ࠣእ") + str(bstack1lll1lll111_opy_) + bstack11ll1_opy_ (u"ࠢࠣኦ"))
                return
            bstack1ll111l1lll_opy_ = {bstack11ll1_opy_ (u"ࠣࡵࡷࡥࡹࡻࡳࠣኧ"): status.lower()}
            bstack1ll1111ll11_opy_ = f.bstack1ll1llll11l_opy_(instance, TestFramework.bstack1lll11ll1l1_opy_, None)
            if status.lower() == bstack11ll1_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࠩከ") and bstack1ll1111ll11_opy_ is not None:
                bstack1ll111l1lll_opy_[bstack11ll1_opy_ (u"ࠪࡶࡪࡧࡳࡰࡰࠪኩ")] = bstack1ll1111ll11_opy_[0][bstack11ll1_opy_ (u"ࠫࡧࡧࡣ࡬ࡶࡵࡥࡨ࡫ࠧኪ")][0] if isinstance(bstack1ll1111ll11_opy_, list) else str(bstack1ll1111ll11_opy_)
            driver.execute_script(
                bstack11ll1_opy_ (u"ࠧࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࡼࡿࠥካ").format(
                    json.dumps(
                        {
                            bstack11ll1_opy_ (u"ࠨࡡࡤࡶ࡬ࡳࡳࠨኬ"): bstack11ll1_opy_ (u"ࠢࡴࡧࡷࡗࡪࡹࡳࡪࡱࡱࡗࡹࡧࡴࡶࡵࠥክ"),
                            bstack11ll1_opy_ (u"ࠣࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠦኮ"): bstack1ll111l1lll_opy_,
                        }
                    )
                )
            )
            f.bstack1lll111ll11_opy_(instance, bstack1ll111ll1l1_opy_.bstack1ll1111l1l1_opy_, True)
    @measure(event_name=EVENTS.bstack1l1lllllll_opy_, stage=STAGE.bstack11l1llll1_opy_)
    def __1ll111111ll_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll1l11l11_opy_,
        bstack1lll1lll111_opy_: Tuple[bstack1llll1ll111_opy_, bstack1lll1111l11_opy_]
    ):
        from browserstack_sdk.sdk_cli.cli import cli
        if not cli.config.get(bstack11ll1_opy_ (u"ࠤࡷࡩࡸࡺࡃࡰࡰࡷࡩࡽࡺࡏࡱࡶ࡬ࡳࡳࡹࠢኯ")).get(bstack11ll1_opy_ (u"ࠥࡷࡰ࡯ࡰࡔࡧࡶࡷ࡮ࡵ࡮ࡏࡣࡰࡩࠧኰ")):
            test_name = f.bstack1ll1llll11l_opy_(instance, TestFramework.bstack1llll1l111l_opy_, None)
            if not test_name:
                self.logger.debug(bstack11ll1_opy_ (u"ࠦࡴࡴ࡟ࡣࡧࡩࡳࡷ࡫࡟ࡵࡧࡶࡸ࠿ࠦ࡭ࡪࡵࡶ࡭ࡳ࡭ࠠࡵࡧࡶࡸࠥࡴࡡ࡮ࡧࠥ኱"))
                return
            bstack1ll111l1111_opy_ = f.bstack1ll1llll11l_opy_(instance, bstack1ll111ll1l1_opy_.bstack1ll111lllll_opy_, [])
            if not bstack1ll111l1111_opy_:
                self.logger.debug(bstack11ll1_opy_ (u"ࠧࡹࡥࡵࡡࡤࡧࡹ࡯ࡶࡦࡡࡧࡶ࡮ࡼࡥࡳࡵ࠽ࠤࡳࡵࠠࡴࡶࡤࡸࡺࡹࠠࡧࡱࡵࠤࡹ࡫ࡳࡵ࠮ࠣ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࡃࠢኲ") + str(bstack1lll1lll111_opy_) + bstack11ll1_opy_ (u"ࠨࠢኳ"))
                return
            for bstack1ll11111l1l_opy_, bstack1l1lllll1ll_opy_ in bstack1ll111l1111_opy_:
                if not bstack1ll11ll1lll_opy_.bstack1ll11l11lll_opy_(bstack1l1lllll1ll_opy_):
                    continue
                driver = bstack1ll11111l1l_opy_()
                if not driver:
                    continue
                driver.execute_script(
                    bstack11ll1_opy_ (u"ࠢࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡥࡹࡧࡦࡹࡹࡵࡲ࠻ࠢࡾࢁࠧኴ").format(
                        json.dumps(
                            {
                                bstack11ll1_opy_ (u"ࠣࡣࡦࡸ࡮ࡵ࡮ࠣኵ"): bstack11ll1_opy_ (u"ࠤࡶࡩࡹ࡙ࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧࠥ኶"),
                                bstack11ll1_opy_ (u"ࠥࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸࠨ኷"): {bstack11ll1_opy_ (u"ࠦࡳࡧ࡭ࡦࠤኸ"): test_name},
                            }
                        )
                    )
                )
            f.bstack1lll111ll11_opy_(instance, bstack1ll111ll1l1_opy_.bstack1l1llllll11_opy_, True)
    def bstack1ll11111l11_opy_(
        self,
        instance: bstack1lll1l11l11_opy_,
        f: TestFramework,
        bstack1lll1lll111_opy_: Tuple[bstack1llll1ll111_opy_, bstack1lll1111l11_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1ll1111l1ll_opy_(f, instance, bstack1lll1lll111_opy_, *args, **kwargs)
        bstack1ll111l1111_opy_ = [d for d, _ in f.bstack1ll1llll11l_opy_(instance, bstack1ll111ll1l1_opy_.bstack1ll111lllll_opy_, [])]
        if not bstack1ll111l1111_opy_:
            self.logger.debug(bstack11ll1_opy_ (u"ࠧࡵ࡮ࡠࡣࡩࡸࡪࡸ࡟ࡵࡧࡶࡸ࠿ࠦ࡮ࡰࠢࡶࡩࡸࡹࡩࡰࡰࡶࠤࡹࡵࠠ࡭࡫ࡱ࡯ࠧኹ"))
            return
        if not bstack1ll111l11l1_opy_():
            self.logger.debug(bstack11ll1_opy_ (u"ࠨ࡯࡯ࡡࡤࡪࡹ࡫ࡲࡠࡶࡨࡷࡹࡀࠠ࡯ࡱࡷࠤࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࠣࡷࡪࡹࡳࡪࡱࡱࠦኺ"))
            return
        for bstack1ll111l111l_opy_ in bstack1ll111l1111_opy_:
            driver = bstack1ll111l111l_opy_()
            if not driver:
                continue
            timestamp = int(time.time() * 1000)
            data = bstack11ll1_opy_ (u"ࠢࡐࡤࡶࡩࡷࡼࡡࡣ࡫࡯࡭ࡹࡿࡓࡺࡰࡦ࠾ࠧኻ") + str(timestamp)
            driver.execute_script(
                bstack11ll1_opy_ (u"ࠣࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࡿࢂࠨኼ").format(
                    json.dumps(
                        {
                            bstack11ll1_opy_ (u"ࠤࡤࡧࡹ࡯࡯࡯ࠤኽ"): bstack11ll1_opy_ (u"ࠥࡥࡳࡴ࡯ࡵࡣࡷࡩࠧኾ"),
                            bstack11ll1_opy_ (u"ࠦࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠢ኿"): {
                                bstack11ll1_opy_ (u"ࠧࡺࡹࡱࡧࠥዀ"): bstack11ll1_opy_ (u"ࠨࡁ࡯ࡰࡲࡸࡦࡺࡩࡰࡰࠥ዁"),
                                bstack11ll1_opy_ (u"ࠢࡥࡣࡷࡥࠧዂ"): data,
                                bstack11ll1_opy_ (u"ࠣ࡮ࡨࡺࡪࡲࠢዃ"): bstack11ll1_opy_ (u"ࠤࡧࡩࡧࡻࡧࠣዄ")
                            }
                        }
                    )
                )
            )
    def bstack1ll111l11ll_opy_(
        self,
        instance: bstack1lll1l11l11_opy_,
        f: TestFramework,
        bstack1lll1lll111_opy_: Tuple[bstack1llll1ll111_opy_, bstack1lll1111l11_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1ll1111l1ll_opy_(f, instance, bstack1lll1lll111_opy_, *args, **kwargs)
        keys = [
            bstack1ll111ll1l1_opy_.bstack1ll111lllll_opy_,
            bstack1ll111ll1l1_opy_.bstack1ll1111llll_opy_,
        ]
        bstack1ll111l1111_opy_ = []
        for key in keys:
            bstack1ll111l1111_opy_.extend(f.bstack1ll1llll11l_opy_(instance, key, []))
        if not bstack1ll111l1111_opy_:
            self.logger.debug(bstack11ll1_opy_ (u"ࠥࡳࡳࡥࡡࡧࡶࡨࡶࡤࡺࡥࡴࡶ࠽ࠤࡺࡴࡡࡣ࡮ࡨࠤࡹࡵࠠࡧ࡫ࡱࡨࠥࡧ࡮ࡺࠢࡶࡩࡸࡹࡩࡰࡰࡶࠤࡹࡵࠠ࡭࡫ࡱ࡯ࠧዅ"))
            return
        if f.bstack1ll1llll11l_opy_(instance, bstack1ll111ll1l1_opy_.bstack1l1llllllll_opy_, False):
            self.logger.debug(bstack11ll1_opy_ (u"ࠦࡴࡴ࡟ࡢࡨࡷࡩࡷࡥࡴࡦࡵࡷ࠾ࠥࡉࡂࡕࠢࡤࡰࡷ࡫ࡡࡥࡻࠣࡧࡷ࡫ࡡࡵࡧࡧࠦ዆"))
            return
        self.bstack1ll111111l1_opy_()
        bstack1ll11l1l1l_opy_ = datetime.now()
        req = structs.TestSessionEventRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = TestFramework.bstack1ll1llll11l_opy_(instance, TestFramework.bstack1lll11l1l1l_opy_)
        req.test_framework_name = TestFramework.bstack1ll1llll11l_opy_(instance, TestFramework.bstack1lll1111111_opy_)
        req.test_framework_version = TestFramework.bstack1ll1llll11l_opy_(instance, TestFramework.bstack1lll11111ll_opy_)
        req.test_framework_state = bstack1lll1lll111_opy_[0].name
        req.test_hook_state = bstack1lll1lll111_opy_[1].name
        req.test_uuid = TestFramework.bstack1ll1llll11l_opy_(instance, TestFramework.bstack1llll111ll1_opy_)
        for bstack1ll11111l1l_opy_, driver in bstack1ll111l1111_opy_:
            try:
                webdriver = bstack1ll11111l1l_opy_()
                if webdriver is None:
                    self.logger.debug(bstack11ll1_opy_ (u"ࠧ࡝ࡥࡣࡆࡵ࡭ࡻ࡫ࡲࠡ࡫ࡱࡷࡹࡧ࡮ࡤࡧࠣ࡭ࡸࠦࡎࡰࡰࡨࠤ࠭ࡸࡥࡧࡧࡵࡩࡳࡩࡥࠡࡧࡻࡴ࡮ࡸࡥࡥࠫࠥ዇"))
                    continue
                session = req.automation_sessions.add()
                session.provider = (
                    bstack11ll1_opy_ (u"ࠨࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࠧወ")
                    if bstack1ll11ll1lll_opy_.bstack1ll1llll11l_opy_(driver, bstack1ll11ll1lll_opy_.bstack1ll11ll11ll_opy_, False)
                    else bstack11ll1_opy_ (u"ࠢࡶࡰ࡮ࡲࡴࡽ࡮ࡠࡩࡵ࡭ࡩࠨዉ")
                )
                session.ref = driver.ref()
                session.hub_url = bstack1ll11ll1lll_opy_.bstack1ll1llll11l_opy_(driver, bstack1ll11ll1lll_opy_.bstack1ll1l1ll111_opy_, bstack11ll1_opy_ (u"ࠣࠤዊ"))
                session.framework_name = driver.framework_name
                session.framework_version = driver.framework_version
                session.framework_session_id = bstack1ll11ll1lll_opy_.bstack1ll1llll11l_opy_(driver, bstack1ll11ll1lll_opy_.bstack1ll11ll1111_opy_, bstack11ll1_opy_ (u"ࠤࠥዋ"))
                caps = None
                if hasattr(webdriver, bstack11ll1_opy_ (u"ࠥࡧࡦࡶࡡࡣ࡫࡯࡭ࡹ࡯ࡥࡴࠤዌ")):
                    try:
                        caps = webdriver.capabilities
                        self.logger.debug(bstack11ll1_opy_ (u"ࠦࡘࡻࡣࡤࡧࡶࡷ࡫ࡻ࡬࡭ࡻࠣࡶࡪࡺࡲࡪࡧࡹࡩࡩࠦࡣࡢࡲࡤࡦ࡮ࡲࡩࡵ࡫ࡨࡷࠥࡪࡩࡳࡧࡦࡸࡱࡿࠠࡧࡴࡲࡱࠥࡪࡲࡪࡸࡨࡶ࠳ࡩࡡࡱࡣࡥ࡭ࡱ࡯ࡴࡪࡧࡶࠦው"))
                    except Exception as e:
                        self.logger.debug(bstack11ll1_opy_ (u"ࠧࡌࡡࡪ࡮ࡨࡨࠥࡺ࡯ࠡࡩࡨࡸࠥࡩࡡࡱࡣࡥ࡭ࡱ࡯ࡴࡪࡧࡶࠤ࡫ࡸ࡯࡮ࠢࡧࡶ࡮ࡼࡥࡳ࠰ࡦࡥࡵࡧࡢࡪ࡮࡬ࡸ࡮࡫ࡳ࠻ࠢࠥዎ") + str(e) + bstack11ll1_opy_ (u"ࠨࠢዏ"))
                try:
                    bstack1ll1111l111_opy_ = json.dumps(caps).encode(bstack11ll1_opy_ (u"ࠢࡶࡶࡩ࠱࠽ࠨዐ")) if caps else bstack1ll111l1l1l_opy_ (u"ࠣࡽࢀࠦዑ")
                    req.capabilities = bstack1ll1111l111_opy_
                except Exception as e:
                    self.logger.debug(bstack11ll1_opy_ (u"ࠤࡪࡩࡹࡥࡣࡣࡶࡢࡩࡻ࡫࡮ࡵ࠼ࠣࡪࡦ࡯࡬ࡦࡦࠣࡸࡴࠦࡳࡦࡰࡧࠤࡸ࡫ࡲࡪࡣ࡯࡭ࡿ࡫ࠠࡤࡣࡳࡷࠥ࡬࡯ࡳࠢࡵࡩࡶࡻࡥࡴࡶ࠽ࠤࠧዒ") + str(e) + bstack11ll1_opy_ (u"ࠥࠦዓ"))
            except Exception as e:
                self.logger.error(bstack11ll1_opy_ (u"ࠦࡊࡸࡲࡰࡴࠣࡴࡷࡵࡣࡦࡵࡶ࡭ࡳ࡭ࠠࡥࡴ࡬ࡺࡪࡸࠠࡪࡶࡨࡱ࠿ࠦࠢዔ") + str(str(e)) + bstack11ll1_opy_ (u"ࠧࠨዕ"))
        req.execution_context.hash = str(instance.context.hash)
        req.execution_context.thread_id = str(instance.context.thread_id)
        req.execution_context.process_id = str(instance.context.process_id)
        return req
    def bstack1ll111lll11_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll1l11l11_opy_,
        bstack1lll1lll111_opy_: Tuple[bstack1llll1ll111_opy_, bstack1lll1111l11_opy_],
        *args,
        **kwargs
    ):
        bstack1ll111l1111_opy_ = f.bstack1ll1llll11l_opy_(instance, bstack1ll111ll1l1_opy_.bstack1ll111lllll_opy_, [])
        if not bstack1ll111l11l1_opy_() and len(bstack1ll111l1111_opy_) == 0:
            bstack1ll111l1111_opy_ = f.bstack1ll1llll11l_opy_(instance, bstack1ll111ll1l1_opy_.bstack1ll1111llll_opy_, [])
        if not bstack1ll111l1111_opy_:
            self.logger.debug(bstack11ll1_opy_ (u"ࠨ࡯࡯ࡡࡥࡩ࡫ࡵࡲࡦࡡࡷࡩࡸࡺ࠺ࠡࡰࡲࠤࡩࡸࡩࡷࡧࡵࡷࠥ࡬࡯ࡳࠢ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࡂࢁࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰࡿࠣࡥࡷ࡭ࡳ࠾ࡽࡤࡶ࡬ࡹࡽࠡ࡭ࡺࡥࡷ࡭ࡳ࠾ࠤዖ") + str(kwargs) + bstack11ll1_opy_ (u"ࠢࠣ዗"))
            return {}
        if len(bstack1ll111l1111_opy_) > 1:
            self.logger.debug(bstack11ll1_opy_ (u"ࠣࡱࡱࡣࡧ࡫ࡦࡰࡴࡨࡣࡹ࡫ࡳࡵ࠼ࠣࡿࡱ࡫࡮ࠩࡦࡵ࡭ࡻ࡫ࡲࡠ࡫ࡱࡷࡹࡧ࡮ࡤࡧࡶ࠭ࢂࠦࡤࡳ࡫ࡹࡩࡷࡹࠠࡧࡱࡵࠤ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵ࠽ࡼࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࢁࠥࡧࡲࡨࡵࡀࡿࡦࡸࡧࡴࡿࠣ࡯ࡼࡧࡲࡨࡵࡀࠦዘ") + str(kwargs) + bstack11ll1_opy_ (u"ࠤࠥዙ"))
            return {}
        bstack1ll11111l1l_opy_, bstack1ll111lll1l_opy_ = bstack1ll111l1111_opy_[0]
        driver = bstack1ll11111l1l_opy_()
        if not driver:
            self.logger.debug(bstack11ll1_opy_ (u"ࠥࡳࡳࡥࡢࡦࡨࡲࡶࡪࡥࡴࡦࡵࡷ࠾ࠥࡴ࡯ࠡࡦࡵ࡭ࡻ࡫ࡲࠡࡨࡲࡶࠥ࡮࡯ࡰ࡭ࡢ࡭ࡳ࡬࡯࠾ࡽ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࢂࠦࡡࡳࡩࡶࡁࢀࡧࡲࡨࡵࢀࠤࡰࡽࡡࡳࡩࡶࡁࠧዚ") + str(kwargs) + bstack11ll1_opy_ (u"ࠦࠧዛ"))
            return {}
        capabilities = f.bstack1ll1llll11l_opy_(bstack1ll111lll1l_opy_, bstack1ll11ll1lll_opy_.bstack1ll11ll1l11_opy_)
        if not capabilities:
            self.logger.debug(bstack11ll1_opy_ (u"ࠧࡵ࡮ࡠࡤࡨࡪࡴࡸࡥࡠࡶࡨࡷࡹࡀࠠ࡯ࡱࠣࡧࡦࡶࡡࡣ࡫࡯࡭ࡹ࡯ࡥࡴࠢࡩࡳࡺࡴࡤࠡࡨࡲࡶࠥ࡮࡯ࡰ࡭ࡢ࡭ࡳ࡬࡯࠾ࡽ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࢂࠦࡡࡳࡩࡶࡁࢀࡧࡲࡨࡵࢀࠤࡰࡽࡡࡳࡩࡶࡁࠧዜ") + str(kwargs) + bstack11ll1_opy_ (u"ࠨࠢዝ"))
            return {}
        return capabilities.get(bstack11ll1_opy_ (u"ࠢࡢ࡮ࡺࡥࡾࡹࡍࡢࡶࡦ࡬ࠧዞ"), {})
    def bstack1l1lllll1l1_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll1l11l11_opy_,
        bstack1lll1lll111_opy_: Tuple[bstack1llll1ll111_opy_, bstack1lll1111l11_opy_],
        *args,
        **kwargs
    ):
        bstack1ll111l1111_opy_ = f.bstack1ll1llll11l_opy_(instance, bstack1ll111ll1l1_opy_.bstack1ll111lllll_opy_, [])
        if not bstack1ll111l11l1_opy_() and len(bstack1ll111l1111_opy_) == 0:
            bstack1ll111l1111_opy_ = f.bstack1ll1llll11l_opy_(instance, bstack1ll111ll1l1_opy_.bstack1ll1111llll_opy_, [])
        if not bstack1ll111l1111_opy_:
            self.logger.debug(bstack11ll1_opy_ (u"ࠣࡩࡨࡸࡤࡧࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࡡࡧࡶ࡮ࡼࡥࡳ࠼ࠣࡲࡴࠦࡤࡳ࡫ࡹࡩࡷࡹࠠࡧࡱࡵࠤ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵ࠽ࡼࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࢁࠥࡧࡲࡨࡵࡀࡿࡦࡸࡧࡴࡿࠣ࡯ࡼࡧࡲࡨࡵࡀࠦዟ") + str(kwargs) + bstack11ll1_opy_ (u"ࠤࠥዠ"))
            return
        if len(bstack1ll111l1111_opy_) > 1:
            self.logger.debug(bstack11ll1_opy_ (u"ࠥ࡫ࡪࡺ࡟ࡢࡷࡷࡳࡲࡧࡴࡪࡱࡱࡣࡩࡸࡩࡷࡧࡵ࠾ࠥࢁ࡬ࡦࡰࠫࡨࡷ࡯ࡶࡦࡴࡢ࡭ࡳࡹࡴࡢࡰࡦࡩࡸ࠯ࡽࠡࡦࡵ࡭ࡻ࡫ࡲࡴࠢࡩࡳࡷࠦࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰ࠿ࡾ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࢃࠠࡢࡴࡪࡷࡂࢁࡡࡳࡩࡶࢁࠥࡱࡷࡢࡴࡪࡷࡂࠨዡ") + str(kwargs) + bstack11ll1_opy_ (u"ࠦࠧዢ"))
        bstack1ll11111l1l_opy_, bstack1ll111lll1l_opy_ = bstack1ll111l1111_opy_[0]
        driver = bstack1ll11111l1l_opy_()
        if not driver:
            self.logger.debug(bstack11ll1_opy_ (u"ࠧ࡭ࡥࡵࡡࡤࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳࡥࡤࡳ࡫ࡹࡩࡷࡀࠠ࡯ࡱࠣࡨࡷ࡯ࡶࡦࡴࠣࡪࡴࡸࠠࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࡀࡿ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵࡽࠡࡣࡵ࡫ࡸࡃࡻࡢࡴࡪࡷࢂࠦ࡫ࡸࡣࡵ࡫ࡸࡃࠢዣ") + str(kwargs) + bstack11ll1_opy_ (u"ࠨࠢዤ"))
            return
        return driver