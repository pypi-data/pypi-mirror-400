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
import os
import threading
import asyncio
from browserstack_sdk.sdk_cli.bstack1llll11l1ll_opy_ import (
    bstack1llll1111l1_opy_,
    bstack1lll1lll1l1_opy_,
    bstack1llll1ll1ll_opy_,
    bstack1llll1lll11_opy_,
)
from typing import Tuple, Dict, Any, List, Union
from bstack_utils.helper import bstack1l1l1111l1l_opy_, bstack11ll1l1l_opy_
from browserstack_sdk.sdk_cli.bstack1lll1l11l11_opy_ import bstack1lll11l111l_opy_
from browserstack_sdk.sdk_cli.test_framework import TestFramework, bstack1lll111l111_opy_, bstack1lll1l1l11l_opy_, bstack1ll1ll11lll_opy_
from browserstack_sdk.sdk_cli.bstack1ll1l111ll1_opy_ import bstack1ll1l1111l1_opy_
from browserstack_sdk.sdk_cli.bstack1l1ll11l1l1_opy_ import bstack1l1ll11ll11_opy_
from typing import Tuple, List, Any
from bstack_utils.bstack111l11ll1_opy_ import bstack1lll11ll1_opy_, bstack111lllll1l_opy_, bstack11lll1lll1_opy_
from browserstack_sdk import sdk_pb2 as structs
class bstack1lll11l11l1_opy_(bstack1l1ll11ll11_opy_):
    bstack1l11l1l11ll_opy_ = bstack11l1l_opy_ (u"ࠤࡷࡩࡸࡺ࡟ࡥࡴ࡬ࡺࡪࡸࡳࠣᎤ")
    bstack1l1l1l1lll1_opy_ = bstack11l1l_opy_ (u"ࠥࡥࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴ࡟ࡴࡧࡶࡷ࡮ࡵ࡮ࡴࠤᎥ")
    bstack1l11l1l111l_opy_ = bstack11l1l_opy_ (u"ࠦࡳࡵ࡮ࡠࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡢࡷࡷࡳࡲࡧࡴࡪࡱࡱࡣࡸ࡫ࡳࡴ࡫ࡲࡲࡸࠨᎦ")
    bstack1l11l1llll1_opy_ = bstack11l1l_opy_ (u"ࠧࡺࡥࡴࡶࡢࡷࡪࡹࡳࡪࡱࡱࡷࠧᎧ")
    bstack1l11l1ll1ll_opy_ = bstack11l1l_opy_ (u"ࠨࡡࡶࡶࡲࡱࡦࡺࡩࡰࡰࡢ࡭ࡳࡹࡴࡢࡰࡦࡩࡤࡸࡥࡧࡵࠥᎨ")
    bstack1l1ll1111ll_opy_ = bstack11l1l_opy_ (u"ࠢࡤࡤࡷࡣࡸ࡫ࡳࡴ࡫ࡲࡲࡤࡩࡲࡦࡣࡷࡩࡩࠨᎩ")
    bstack1l11l1l11l1_opy_ = bstack11l1l_opy_ (u"ࠣࡥࡥࡸࡤࡹࡥࡴࡵ࡬ࡳࡳࡥ࡮ࡢ࡯ࡨࠦᎪ")
    bstack1l11ll11111_opy_ = bstack11l1l_opy_ (u"ࠤࡦࡦࡹࡥࡳࡦࡵࡶ࡭ࡴࡴ࡟ࡴࡶࡤࡸࡺࡹࠢᎫ")
    def __init__(self):
        super().__init__(bstack1l1ll11l1ll_opy_=self.bstack1l11l1l11ll_opy_, frameworks=[bstack1lll11l111l_opy_.NAME])
        if not self.is_enabled():
            return
        TestFramework.bstack1ll111ll111_opy_((bstack1lll111l111_opy_.BEFORE_EACH, bstack1lll1l1l11l_opy_.POST), self.bstack1l11ll1111l_opy_)
        if bstack11ll1l1l_opy_():
            TestFramework.bstack1ll111ll111_opy_((bstack1lll111l111_opy_.TEST, bstack1lll1l1l11l_opy_.POST), self.bstack1ll111l1l11_opy_)
        else:
            TestFramework.bstack1ll111ll111_opy_((bstack1lll111l111_opy_.TEST, bstack1lll1l1l11l_opy_.PRE), self.bstack1ll111l1l11_opy_)
        TestFramework.bstack1ll111ll111_opy_((bstack1lll111l111_opy_.TEST, bstack1lll1l1l11l_opy_.POST), self.bstack1l1llll1l11_opy_)
    def is_enabled(self) -> bool:
        return True
    def bstack1l11ll1111l_opy_(
        self,
        f: TestFramework,
        instance: bstack1ll1ll11lll_opy_,
        bstack1llll1lll1l_opy_: Tuple[bstack1lll111l111_opy_, bstack1lll1l1l11l_opy_],
        *args,
        **kwargs,
    ):
        bstack1l11l1ll11l_opy_ = self.bstack1l11l1l1lll_opy_(instance.context)
        if not bstack1l11l1ll11l_opy_:
            self.logger.debug(bstack11l1l_opy_ (u"ࠥࡷࡪࡺ࡟ࡢࡥࡷ࡭ࡻ࡫࡟ࡱࡣࡪࡩ࠿ࠦ࡮ࡰࠢࡳࡥ࡬࡫ࠠࡧࡱࡵࠤ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵ࠽ࠣᎬ") + str(bstack1llll1lll1l_opy_) + bstack11l1l_opy_ (u"ࠦࠧᎭ"))
            return
        f.bstack1lllll1111l_opy_(instance, bstack1lll11l11l1_opy_.bstack1l1l1l1lll1_opy_, bstack1l11l1ll11l_opy_)
    def bstack1l11l1l1lll_opy_(self, context: bstack1llll1lll11_opy_, bstack1l11l1lll1l_opy_= True):
        if bstack1l11l1lll1l_opy_:
            bstack1l11l1ll11l_opy_ = self.bstack1l1ll11ll1l_opy_(context, reverse=True)
        else:
            bstack1l11l1ll11l_opy_ = self.bstack1l1ll1l111l_opy_(context, reverse=True)
        return [f for f in bstack1l11l1ll11l_opy_ if f[1].state != bstack1llll1111l1_opy_.QUIT]
    def bstack1ll111l1l11_opy_(
        self,
        f: TestFramework,
        instance: bstack1ll1ll11lll_opy_,
        bstack1llll1lll1l_opy_: Tuple[bstack1lll111l111_opy_, bstack1lll1l1l11l_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1l11ll1111l_opy_(f, instance, bstack1llll1lll1l_opy_, *args, **kwargs)
        if not bstack1l1l1111l1l_opy_:
            self.logger.debug(bstack11l1l_opy_ (u"ࠧࡵ࡮ࡠࡤࡨࡪࡴࡸࡥࡠࡶࡨࡷࡹࡀࠠ࡯ࡱࡷࠤࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࠣࡷࡪࡹࡳࡪࡱࡱࠤ࡫ࡵࡲࠡࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࡁࢀ࡮࡯ࡰ࡭ࡢ࡭ࡳ࡬࡯ࡾࠢࡤࡶ࡬ࡹ࠽ࡼࡣࡵ࡫ࡸࢃࠠ࡬ࡹࡤࡶ࡬ࡹ࠽ࠣᎮ") + str(kwargs) + bstack11l1l_opy_ (u"ࠨࠢᎯ"))
            return
        bstack1l11l1ll11l_opy_ = f.bstack1llll1lllll_opy_(instance, bstack1lll11l11l1_opy_.bstack1l1l1l1lll1_opy_, [])
        if not bstack1l11l1ll11l_opy_:
            self.logger.debug(bstack11l1l_opy_ (u"ࠢࡰࡰࡢࡦࡪ࡬࡯ࡳࡧࡢࡸࡪࡹࡴ࠻ࠢࡱࡳࠥࡪࡲࡪࡸࡨࡶࡸࠦࡦࡰࡴࠣ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࡃࡻࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࢀࠤࡦࡸࡧࡴ࠿ࡾࡥࡷ࡭ࡳࡾࠢ࡮ࡻࡦࡸࡧࡴ࠿ࠥᎰ") + str(kwargs) + bstack11l1l_opy_ (u"ࠣࠤᎱ"))
            return
        if len(bstack1l11l1ll11l_opy_) > 1:
            self.logger.debug(
                bstack1ll1l11l1ll_opy_ (u"ࠤࡲࡲࡤࡨࡥࡧࡱࡵࡩࡤࡺࡥࡴࡶ࠽ࠤࢀࡲࡥ࡯ࠪࡳࡥ࡬࡫࡟ࡪࡰࡶࡸࡦࡴࡣࡦࡵࠬࢁࠥࡪࡲࡪࡸࡨࡶࡸࠦࡦࡰࡴࠣ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࡃࡻࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࢀࠤࡦࡸࡧࡴ࠿ࡾࡥࡷ࡭ࡳࡾࠢ࡮ࡻࡦࡸࡧࡴ࠿ࡾ࡯ࡼࡧࡲࡨࡵࢀࠦᎲ"))
        bstack1l11l1lll11_opy_, bstack1l1l11111l1_opy_ = bstack1l11l1ll11l_opy_[0]
        page = bstack1l11l1lll11_opy_()
        if not page:
            self.logger.debug(bstack11l1l_opy_ (u"ࠥࡳࡳࡥࡢࡦࡨࡲࡶࡪࡥࡴࡦࡵࡷ࠾ࠥࡴ࡯ࠡࡲࡤ࡫ࡪࠦࡦࡰࡴࠣ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࡃࡻࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࢀࠤࡦࡸࡧࡴ࠿ࡾࡥࡷ࡭ࡳࡾࠢ࡮ࡻࡦࡸࡧࡴ࠿ࠥᎳ") + str(kwargs) + bstack11l1l_opy_ (u"ࠦࠧᎴ"))
            return
        bstack1l1l1llll_opy_ = getattr(args[0], bstack11l1l_opy_ (u"ࠧࡴ࡯ࡥࡧ࡬ࡨࠧᎵ"), None)
        from browserstack_sdk.sdk_cli.cli import cli
        if not cli.config.get(bstack11l1l_opy_ (u"ࠨࡴࡦࡵࡷࡇࡴࡴࡴࡦࡺࡷࡓࡵࡺࡩࡰࡰࡶࠦᎶ")).get(bstack11l1l_opy_ (u"ࠢࡴ࡭࡬ࡴࡘ࡫ࡳࡴ࡫ࡲࡲࡓࡧ࡭ࡦࠤᎷ")):
            try:
                page.evaluate(bstack11l1l_opy_ (u"ࠣࡡࠣࡁࡃࠦࡻࡾࠤᎸ"),
                            bstack11l1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡧࡻࡩࡨࡻࡴࡰࡴ࠽ࠤࢀࠨࡡࡤࡶ࡬ࡳࡳࠨ࠺ࠡࠤࡶࡩࡹ࡙ࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧࠥ࠰ࠥࠨࡡࡳࡩࡸࡱࡪࡴࡴࡴࠤ࠽ࠤࢀࠨ࡮ࡢ࡯ࡨࠦ࠿࠭Ꮉ") + json.dumps(
                                bstack1l1l1llll_opy_) + bstack11l1l_opy_ (u"ࠥࢁࢂࠨᎺ"))
            except Exception as e:
                self.logger.debug(bstack11l1l_opy_ (u"ࠦࡪࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡪࡰࠣࡴࡱࡧࡹࡸࡴ࡬࡫࡭ࡺࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠡࡰࡤࡱࡪࠦࡻࡾࠤᎻ"), e)
    def bstack1l1llll1l11_opy_(
        self,
        f: TestFramework,
        instance: bstack1ll1ll11lll_opy_,
        bstack1llll1lll1l_opy_: Tuple[bstack1lll111l111_opy_, bstack1lll1l1l11l_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1l11ll1111l_opy_(f, instance, bstack1llll1lll1l_opy_, *args, **kwargs)
        if not bstack1l1l1111l1l_opy_:
            self.logger.debug(bstack11l1l_opy_ (u"ࠧࡵ࡮ࡠࡤࡨࡪࡴࡸࡥࡠࡶࡨࡷࡹࡀࠠ࡯ࡱࡷࠤࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࠣࡷࡪࡹࡳࡪࡱࡱࠤ࡫ࡵࡲࠡࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࡁࢀ࡮࡯ࡰ࡭ࡢ࡭ࡳ࡬࡯ࡾࠢࡤࡶ࡬ࡹ࠽ࡼࡣࡵ࡫ࡸࢃࠠ࡬ࡹࡤࡶ࡬ࡹ࠽ࠣᎼ") + str(kwargs) + bstack11l1l_opy_ (u"ࠨࠢᎽ"))
            return
        bstack1l11l1ll11l_opy_ = f.bstack1llll1lllll_opy_(instance, bstack1lll11l11l1_opy_.bstack1l1l1l1lll1_opy_, [])
        if not bstack1l11l1ll11l_opy_:
            self.logger.debug(bstack11l1l_opy_ (u"ࠢࡰࡰࡢࡦࡪ࡬࡯ࡳࡧࡢࡸࡪࡹࡴ࠻ࠢࡱࡳࠥࡪࡲࡪࡸࡨࡶࡸࠦࡦࡰࡴࠣ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࡃࡻࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࢀࠤࡦࡸࡧࡴ࠿ࡾࡥࡷ࡭ࡳࡾࠢ࡮ࡻࡦࡸࡧࡴ࠿ࠥᎾ") + str(kwargs) + bstack11l1l_opy_ (u"ࠣࠤᎿ"))
            return
        if len(bstack1l11l1ll11l_opy_) > 1:
            self.logger.debug(
                bstack1ll1l11l1ll_opy_ (u"ࠤࡲࡲࡤࡨࡥࡧࡱࡵࡩࡤࡺࡥࡴࡶ࠽ࠤࢀࡲࡥ࡯ࠪࡳࡥ࡬࡫࡟ࡪࡰࡶࡸࡦࡴࡣࡦࡵࠬࢁࠥࡪࡲࡪࡸࡨࡶࡸࠦࡦࡰࡴࠣ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࡃࡻࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࢀࠤࡦࡸࡧࡴ࠿ࡾࡥࡷ࡭ࡳࡾࠢ࡮ࡻࡦࡸࡧࡴ࠿ࡾ࡯ࡼࡧࡲࡨࡵࢀࠦᏀ"))
        bstack1l11l1lll11_opy_, bstack1l1l11111l1_opy_ = bstack1l11l1ll11l_opy_[0]
        page = bstack1l11l1lll11_opy_()
        if not page:
            self.logger.debug(bstack11l1l_opy_ (u"ࠥࡳࡳࡥࡢࡦࡨࡲࡶࡪࡥࡴࡦࡵࡷ࠾ࠥࡴ࡯ࠡࡲࡤ࡫ࡪࠦࡦࡰࡴࠣ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࡃࡻࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࢀࠤࡦࡸࡧࡴ࠿ࡾࡥࡷ࡭ࡳࡾࠢ࡮ࡻࡦࡸࡧࡴ࠿ࠥᏁ") + str(kwargs) + bstack11l1l_opy_ (u"ࠦࠧᏂ"))
            return
        status = f.bstack1llll1lllll_opy_(instance, TestFramework.bstack1l11l1lllll_opy_, None)
        if not status:
            self.logger.debug(bstack11l1l_opy_ (u"ࠧࡴ࡯ࠡࡵࡷࡥࡹࡻࡳࠡࡨࡲࡶࠥࡺࡥࡴࡶ࠯ࠤ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵ࠽ࠣᏃ") + str(bstack1llll1lll1l_opy_) + bstack11l1l_opy_ (u"ࠨࠢᏄ"))
            return
        bstack1l11l1l1l1l_opy_ = {bstack11l1l_opy_ (u"ࠢࡴࡶࡤࡸࡺࡹࠢᏅ"): status.lower()}
        bstack1l11l1l1l11_opy_ = f.bstack1llll1lllll_opy_(instance, TestFramework.bstack1l11l1ll1l1_opy_, None)
        if status.lower() == bstack11l1l_opy_ (u"ࠨࡨࡤ࡭ࡱ࡫ࡤࠨᏆ") and bstack1l11l1l1l11_opy_ is not None:
            bstack1l11l1l1l1l_opy_[bstack11l1l_opy_ (u"ࠩࡵࡩࡦࡹ࡯࡯ࠩᏇ")] = bstack1l11l1l1l11_opy_[0][bstack11l1l_opy_ (u"ࠪࡦࡦࡩ࡫ࡵࡴࡤࡧࡪ࠭Ꮘ")][0] if isinstance(bstack1l11l1l1l11_opy_, list) else str(bstack1l11l1l1l11_opy_)
        from browserstack_sdk.sdk_cli.cli import cli
        if not cli.config.get(bstack11l1l_opy_ (u"ࠦࡹ࡫ࡳࡵࡅࡲࡲࡹ࡫ࡸࡵࡑࡳࡸ࡮ࡵ࡮ࡴࠤᏉ")).get(bstack11l1l_opy_ (u"ࠧࡹ࡫ࡪࡲࡖࡩࡸࡹࡩࡰࡰࡖࡸࡦࡺࡵࡴࠤᏊ")):
            try:
                page.evaluate(
                        bstack11l1l_opy_ (u"ࠨ࡟ࠡ࠿ࡁࠤࢀࢃࠢᏋ"),
                        bstack11l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡥࡹࡧࡦࡹࡹࡵࡲ࠻ࠢࡾࠦࡦࡩࡴࡪࡱࡱࠦ࠿ࠦࠢࡴࡧࡷࡗࡪࡹࡳࡪࡱࡱࡗࡹࡧࡴࡶࡵࠥ࠰ࠥࠨࡡࡳࡩࡸࡱࡪࡴࡴࡴࠤ࠽ࠤࠬᏌ")
                        + json.dumps(bstack1l11l1l1l1l_opy_)
                        + bstack11l1l_opy_ (u"ࠣࡿࠥᏍ")
                    )
            except Exception as e:
                self.logger.debug(bstack11l1l_opy_ (u"ࠤࡨࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥ࡯࡮ࠡࡲ࡯ࡥࡾࡽࡲࡪࡩ࡫ࡸࠥࡹࡥࡴࡵ࡬ࡳࡳࠦࡳࡵࡣࡷࡹࡸࠦࡻࡾࠤᏎ"), e)
    def bstack1l1l1llll1l_opy_(
        self,
        instance: bstack1ll1ll11lll_opy_,
        f: TestFramework,
        bstack1llll1lll1l_opy_: Tuple[bstack1lll111l111_opy_, bstack1lll1l1l11l_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1l11ll1111l_opy_(f, instance, bstack1llll1lll1l_opy_, *args, **kwargs)
        if not bstack1l1l1111l1l_opy_:
            self.logger.debug(
                bstack1ll1l11l1ll_opy_ (u"ࠥࡱࡦࡸ࡫ࡠࡱ࠴࠵ࡾࡥࡳࡺࡰࡦ࠾ࠥࡴ࡯ࡵࠢࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࠡࡵࡨࡷࡸ࡯࡯࡯࠮ࠣ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࡃࡻࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࢀࠤࡦࡸࡧࡴ࠿ࡾࡥࡷ࡭ࡳࡾࠢ࡮ࡻࡦࡸࡧࡴ࠿ࡾ࡯ࡼࡧࡲࡨࡵࢀࠦᏏ"))
            return
        bstack1l11l1ll11l_opy_ = f.bstack1llll1lllll_opy_(instance, bstack1lll11l11l1_opy_.bstack1l1l1l1lll1_opy_, [])
        if not bstack1l11l1ll11l_opy_:
            self.logger.debug(bstack11l1l_opy_ (u"ࠦࡴࡴ࡟ࡣࡧࡩࡳࡷ࡫࡟ࡵࡧࡶࡸ࠿ࠦ࡮ࡰࠢࡧࡶ࡮ࡼࡥࡳࡵࠣࡪࡴࡸࠠࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࡀࡿ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵࡽࠡࡣࡵ࡫ࡸࡃࡻࡢࡴࡪࡷࢂࠦ࡫ࡸࡣࡵ࡫ࡸࡃࠢᏐ") + str(kwargs) + bstack11l1l_opy_ (u"ࠧࠨᏑ"))
            return
        if len(bstack1l11l1ll11l_opy_) > 1:
            self.logger.debug(
                bstack1ll1l11l1ll_opy_ (u"ࠨ࡯࡯ࡡࡥࡩ࡫ࡵࡲࡦࡡࡷࡩࡸࡺ࠺ࠡࡽ࡯ࡩࡳ࠮ࡰࡢࡩࡨࡣ࡮ࡴࡳࡵࡣࡱࡧࡪࡹࠩࡾࠢࡧࡶ࡮ࡼࡥࡳࡵࠣࡪࡴࡸࠠࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࡀࡿ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵࡽࠡࡣࡵ࡫ࡸࡃࡻࡢࡴࡪࡷࢂࠦ࡫ࡸࡣࡵ࡫ࡸࡃࡻ࡬ࡹࡤࡶ࡬ࡹࡽࠣᏒ"))
        bstack1l11l1lll11_opy_, bstack1l1l11111l1_opy_ = bstack1l11l1ll11l_opy_[0]
        page = bstack1l11l1lll11_opy_()
        if not page:
            self.logger.debug(bstack11l1l_opy_ (u"ࠢ࡮ࡣࡵ࡯ࡤࡵ࠱࠲ࡻࡢࡷࡾࡴࡣ࠻ࠢࡱࡳࠥࡶࡡࡨࡧࠣࡪࡴࡸࠠࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࡀࡿ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵࡽࠡࡣࡵ࡫ࡸࡃࡻࡢࡴࡪࡷࢂࠦ࡫ࡸࡣࡵ࡫ࡸࡃࠢᏓ") + str(kwargs) + bstack11l1l_opy_ (u"ࠣࠤᏔ"))
            return
        timestamp = int(time.time() * 1000)
        data = bstack11l1l_opy_ (u"ࠤࡒࡦࡸ࡫ࡲࡷࡣࡥ࡭ࡱ࡯ࡴࡺࡕࡼࡲࡨࡀࠢᏕ") + str(timestamp)
        try:
            page.evaluate(
                bstack11l1l_opy_ (u"ࠥࡣࠥࡃ࠾ࠡࡽࢀࠦᏖ"),
                bstack11l1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡩࡽ࡫ࡣࡶࡶࡲࡶ࠿ࠦࡻࡾࠩᏗ").format(
                    json.dumps(
                        {
                            bstack11l1l_opy_ (u"ࠧࡧࡣࡵ࡫ࡲࡲࠧᏘ"): bstack11l1l_opy_ (u"ࠨࡡ࡯ࡰࡲࡸࡦࡺࡥࠣᏙ"),
                            bstack11l1l_opy_ (u"ࠢࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠥᏚ"): {
                                bstack11l1l_opy_ (u"ࠣࡶࡼࡴࡪࠨᏛ"): bstack11l1l_opy_ (u"ࠤࡄࡲࡳࡵࡴࡢࡶ࡬ࡳࡳࠨᏜ"),
                                bstack11l1l_opy_ (u"ࠥࡨࡦࡺࡡࠣᏝ"): data,
                                bstack11l1l_opy_ (u"ࠦࡱ࡫ࡶࡦ࡮ࠥᏞ"): bstack11l1l_opy_ (u"ࠧࡪࡥࡣࡷࡪࠦᏟ")
                            }
                        }
                    )
                )
            )
        except Exception as e:
            self.logger.debug(bstack11l1l_opy_ (u"ࠨࡥࡹࡥࡨࡴࡹ࡯࡯࡯ࠢ࡬ࡲࠥࡶ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵࠢࡲ࠵࠶ࡿࠠࡢࡰࡱࡳࡹࡧࡴࡪࡱࡱࠤࡲࡧࡲ࡬࡫ࡱ࡫ࠥࢁࡽࠣᏠ"), e)
    def bstack1l1l1l1llll_opy_(
        self,
        instance: bstack1ll1ll11lll_opy_,
        f: TestFramework,
        bstack1llll1lll1l_opy_: Tuple[bstack1lll111l111_opy_, bstack1lll1l1l11l_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1l11ll1111l_opy_(f, instance, bstack1llll1lll1l_opy_, *args, **kwargs)
        if f.bstack1llll1lllll_opy_(instance, bstack1lll11l11l1_opy_.bstack1l1ll1111ll_opy_, False):
            return
        self.bstack1ll11111lll_opy_()
        req = structs.TestSessionEventRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = TestFramework.bstack1llll1lllll_opy_(instance, TestFramework.bstack1ll1111l111_opy_)
        req.test_framework_name = TestFramework.bstack1llll1lllll_opy_(instance, TestFramework.bstack1l1llll11l1_opy_)
        req.test_framework_version = TestFramework.bstack1llll1lllll_opy_(instance, TestFramework.bstack1l1l1lll1ll_opy_)
        req.test_framework_state = bstack1llll1lll1l_opy_[0].name
        req.test_hook_state = bstack1llll1lll1l_opy_[1].name
        req.test_uuid = TestFramework.bstack1llll1lllll_opy_(instance, TestFramework.bstack1ll11l11l1l_opy_)
        for bstack1l11l1ll111_opy_ in bstack1ll1l1111l1_opy_.bstack1llll11l1l1_opy_.values():
            session = req.automation_sessions.add()
            session.provider = (
                bstack11l1l_opy_ (u"ࠢࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࠨᏡ")
                if bstack1l1l1111l1l_opy_
                else bstack11l1l_opy_ (u"ࠣࡷࡱ࡯ࡳࡵࡷ࡯ࡡࡪࡶ࡮ࡪࠢᏢ")
            )
            session.ref = bstack1l11l1ll111_opy_.ref()
            session.hub_url = bstack1ll1l1111l1_opy_.bstack1llll1lllll_opy_(bstack1l11l1ll111_opy_, bstack1ll1l1111l1_opy_.bstack1l11ll1l1l1_opy_, bstack11l1l_opy_ (u"ࠤࠥᏣ"))
            session.framework_name = bstack1l11l1ll111_opy_.framework_name
            session.framework_version = bstack1l11l1ll111_opy_.framework_version
            session.framework_session_id = bstack1ll1l1111l1_opy_.bstack1llll1lllll_opy_(bstack1l11l1ll111_opy_, bstack1ll1l1111l1_opy_.bstack1l11lll1l11_opy_, bstack11l1l_opy_ (u"ࠥࠦᏤ"))
        req.execution_context.hash = str(instance.context.hash)
        req.execution_context.thread_id = str(instance.context.thread_id)
        req.execution_context.process_id = str(instance.context.process_id)
        return req
    def bstack1l1lllll111_opy_(
        self,
        f: TestFramework,
        instance: bstack1ll1ll11lll_opy_,
        bstack1llll1lll1l_opy_: Tuple[bstack1lll111l111_opy_, bstack1lll1l1l11l_opy_],
        *args,
        **kwargs
    ):
        bstack1l11l1ll11l_opy_ = f.bstack1llll1lllll_opy_(instance, bstack1lll11l11l1_opy_.bstack1l1l1l1lll1_opy_, [])
        if not bstack1l11l1ll11l_opy_:
            self.logger.debug(bstack11l1l_opy_ (u"ࠦ࡬࡫ࡴࡠࡣࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࡤࡪࡲࡪࡸࡨࡶ࠿ࠦ࡮ࡰࠢࡳࡥ࡬࡫ࡳࠡࡨࡲࡶࠥ࡮࡯ࡰ࡭ࡢ࡭ࡳ࡬࡯࠾ࡽ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࢂࠦࡡࡳࡩࡶࡁࢀࡧࡲࡨࡵࢀࠤࡰࡽࡡࡳࡩࡶࡁࠧᏥ") + str(kwargs) + bstack11l1l_opy_ (u"ࠧࠨᏦ"))
            return
        if len(bstack1l11l1ll11l_opy_) > 1:
            self.logger.debug(bstack11l1l_opy_ (u"ࠨࡧࡦࡶࡢࡥࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴ࡟ࡥࡴ࡬ࡺࡪࡸ࠺ࠡࡽ࡯ࡩࡳ࠮ࡰࡢࡩࡨࡣ࡮ࡴࡳࡵࡣࡱࡧࡪࡹࠩࡾࠢࡧࡶ࡮ࡼࡥࡳࡵࠣࡪࡴࡸࠠࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࡀࡿ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵࡽࠡࡣࡵ࡫ࡸࡃࡻࡢࡴࡪࡷࢂࠦ࡫ࡸࡣࡵ࡫ࡸࡃࠢᏧ") + str(kwargs) + bstack11l1l_opy_ (u"ࠢࠣᏨ"))
        bstack1l11l1lll11_opy_, bstack1l1l11111l1_opy_ = bstack1l11l1ll11l_opy_[0]
        page = bstack1l11l1lll11_opy_()
        if not page:
            self.logger.debug(bstack11l1l_opy_ (u"ࠣࡩࡨࡸࡤࡧࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࡡࡧࡶ࡮ࡼࡥࡳ࠼ࠣࡲࡴࠦࡰࡢࡩࡨࠤ࡫ࡵࡲࠡࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࡁࢀ࡮࡯ࡰ࡭ࡢ࡭ࡳ࡬࡯ࡾࠢࡤࡶ࡬ࡹ࠽ࡼࡣࡵ࡫ࡸࢃࠠ࡬ࡹࡤࡶ࡬ࡹ࠽ࠣᏩ") + str(kwargs) + bstack11l1l_opy_ (u"ࠤࠥᏪ"))
            return
        return page
    def bstack1l1lll1l1ll_opy_(
        self,
        f: TestFramework,
        instance: bstack1ll1ll11lll_opy_,
        bstack1llll1lll1l_opy_: Tuple[bstack1lll111l111_opy_, bstack1lll1l1l11l_opy_],
        *args,
        **kwargs
    ):
        caps = {}
        bstack1l11l1l1ll1_opy_ = {}
        for bstack1l11l1ll111_opy_ in bstack1ll1l1111l1_opy_.bstack1llll11l1l1_opy_.values():
            caps = bstack1ll1l1111l1_opy_.bstack1llll1lllll_opy_(bstack1l11l1ll111_opy_, bstack1ll1l1111l1_opy_.bstack1l11ll11l1l_opy_, bstack11l1l_opy_ (u"ࠥࠦᏫ"))
        bstack1l11l1l1ll1_opy_[bstack11l1l_opy_ (u"ࠦࡧࡸ࡯ࡸࡵࡨࡶࡓࡧ࡭ࡦࠤᏬ")] = caps.get(bstack11l1l_opy_ (u"ࠧࡨࡲࡰࡹࡶࡩࡷࠨᏭ"), bstack11l1l_opy_ (u"ࠨࠢᏮ"))
        bstack1l11l1l1ll1_opy_[bstack11l1l_opy_ (u"ࠢࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡐࡤࡱࡪࠨᏯ")] = caps.get(bstack11l1l_opy_ (u"ࠣࡱࡶࠦᏰ"), bstack11l1l_opy_ (u"ࠤࠥᏱ"))
        bstack1l11l1l1ll1_opy_[bstack11l1l_opy_ (u"ࠥࡴࡱࡧࡴࡧࡱࡵࡱ࡛࡫ࡲࡴ࡫ࡲࡲࠧᏲ")] = caps.get(bstack11l1l_opy_ (u"ࠦࡴࡹ࡟ࡷࡧࡵࡷ࡮ࡵ࡮ࠣᏳ"), bstack11l1l_opy_ (u"ࠧࠨᏴ"))
        bstack1l11l1l1ll1_opy_[bstack11l1l_opy_ (u"ࠨࡢࡳࡱࡺࡷࡪࡸࡖࡦࡴࡶ࡭ࡴࡴࠢᏵ")] = caps.get(bstack11l1l_opy_ (u"ࠢࡣࡴࡲࡻࡸ࡫ࡲࡠࡸࡨࡶࡸ࡯࡯࡯ࠤ᏶"), bstack11l1l_opy_ (u"ࠣࠤ᏷"))
        return bstack1l11l1l1ll1_opy_
    def bstack1l1lll11lll_opy_(self, page: object, bstack1ll11l11111_opy_, args={}):
        try:
            bstack1l11ll111l1_opy_ = bstack11l1l_opy_ (u"ࠤࠥࠦ࠭࡬ࡵ࡯ࡥࡷ࡭ࡴࡴࠠࠩ࠰࠱࠲ࡧࡹࡴࡢࡥ࡮ࡗࡩࡱࡁࡳࡩࡶ࠭ࠥࢁࡻࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࡶࡪࡺࡵࡳࡰࠣࡲࡪࡽࠠࡑࡴࡲࡱ࡮ࡹࡥࠩࠪࡵࡩࡸࡵ࡬ࡷࡧ࠯ࠤࡷ࡫ࡪࡦࡥࡷ࠭ࠥࡃ࠾ࠡࡽࡾࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࡦࡸࡺࡡࡤ࡭ࡖࡨࡰࡇࡲࡨࡵ࠱ࡴࡺࡹࡨࠩࡴࡨࡷࡴࡲࡶࡦࠫ࠾ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࡿ࡫ࡴ࡟ࡣࡱࡧࡽࢂࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࡿࢀ࠭ࡀࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࢂࢃࠩࠩࡽࡤࡶ࡬ࡥࡪࡴࡱࡱࢁ࠮ࠨࠢࠣᏸ")
            bstack1ll11l11111_opy_ = bstack1ll11l11111_opy_.replace(bstack11l1l_opy_ (u"ࠥࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸࠨᏹ"), bstack11l1l_opy_ (u"ࠦࡧࡹࡴࡢࡥ࡮ࡗࡩࡱࡁࡳࡩࡶࠦᏺ"))
            script = bstack1l11ll111l1_opy_.format(fn_body=bstack1ll11l11111_opy_, arg_json=json.dumps(args))
            return page.evaluate(script)
        except Exception as e:
            self.logger.error(bstack11l1l_opy_ (u"ࠧࡧ࠱࠲ࡻࡢࡷࡨࡸࡩࡱࡶࡢࡩࡽ࡫ࡣࡶࡶࡨ࠾ࠥࡋࡲࡳࡱࡵࠤࡪࡾࡥࡤࡷࡷ࡭ࡳ࡭ࠠࡵࡪࡨࠤࡦ࠷࠱ࡺࠢࡶࡧࡷ࡯ࡰࡵ࠮ࠣࠦᏻ") + str(e) + bstack11l1l_opy_ (u"ࠨࠢᏼ"))