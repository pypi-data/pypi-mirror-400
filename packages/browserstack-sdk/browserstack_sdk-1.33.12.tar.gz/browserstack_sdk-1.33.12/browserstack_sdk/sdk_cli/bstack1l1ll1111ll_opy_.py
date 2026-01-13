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
import os
import threading
import asyncio
from browserstack_sdk.sdk_cli.bstack1ll11l1l1l1_opy_ import (
    bstack1ll11lllll1_opy_,
    bstack1ll11lll1ll_opy_,
    bstack1ll1l1ll1l1_opy_,
    bstack1ll1111lll1_opy_,
)
from typing import Tuple, Dict, Any, List, Union
from bstack_utils.helper import bstack1ll111l11l1_opy_, bstack1l1l1l1l_opy_
from browserstack_sdk.sdk_cli.bstack1ll11l1lll1_opy_ import bstack1ll11ll1lll_opy_
from browserstack_sdk.sdk_cli.test_framework import TestFramework, bstack1llll1ll111_opy_, bstack1lll1111l11_opy_, bstack1lll1l11l11_opy_
from browserstack_sdk.sdk_cli.bstack1ll11l111ll_opy_ import bstack1ll11l11l1l_opy_
from browserstack_sdk.sdk_cli.bstack1ll111l1ll1_opy_ import bstack1ll111l1l11_opy_
from typing import Tuple, List, Any
from bstack_utils.bstack11llll1l1_opy_ import bstack1l111l1l_opy_, bstack1ll11ll1ll_opy_, bstack11l11111ll_opy_
from browserstack_sdk import sdk_pb2 as structs
class bstack1l1l1l1111l_opy_(bstack1ll111l1l11_opy_):
    bstack1ll111ll1ll_opy_ = bstack11ll1_opy_ (u"ࠨࡴࡦࡵࡷࡣࡩࡸࡩࡷࡧࡵࡷࠧᖙ")
    bstack1ll111lllll_opy_ = bstack11ll1_opy_ (u"ࠢࡢࡷࡷࡳࡲࡧࡴࡪࡱࡱࡣࡸ࡫ࡳࡴ࡫ࡲࡲࡸࠨᖚ")
    bstack1ll1111llll_opy_ = bstack11ll1_opy_ (u"ࠣࡰࡲࡲࡤࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡦࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࡠࡵࡨࡷࡸ࡯࡯࡯ࡵࠥᖛ")
    bstack1ll1111l11l_opy_ = bstack11ll1_opy_ (u"ࠤࡷࡩࡸࡺ࡟ࡴࡧࡶࡷ࡮ࡵ࡮ࡴࠤᖜ")
    bstack1ll11l1111l_opy_ = bstack11ll1_opy_ (u"ࠥࡥࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴ࡟ࡪࡰࡶࡸࡦࡴࡣࡦࡡࡵࡩ࡫ࡹࠢᖝ")
    bstack1l1llllllll_opy_ = bstack11ll1_opy_ (u"ࠦࡨࡨࡴࡠࡵࡨࡷࡸ࡯࡯࡯ࡡࡦࡶࡪࡧࡴࡦࡦࠥᖞ")
    bstack1l1llllll11_opy_ = bstack11ll1_opy_ (u"ࠧࡩࡢࡵࡡࡶࡩࡸࡹࡩࡰࡰࡢࡲࡦࡳࡥࠣᖟ")
    bstack1ll1111l1l1_opy_ = bstack11ll1_opy_ (u"ࠨࡣࡣࡶࡢࡷࡪࡹࡳࡪࡱࡱࡣࡸࡺࡡࡵࡷࡶࠦᖠ")
    def __init__(self):
        super().__init__(bstack1ll111ll111_opy_=self.bstack1ll111ll1ll_opy_, frameworks=[bstack1ll11ll1lll_opy_.NAME])
        if not self.is_enabled():
            return
        TestFramework.bstack1ll1l11111l_opy_((bstack1llll1ll111_opy_.BEFORE_EACH, bstack1lll1111l11_opy_.POST), self.bstack11lll1l1l1l_opy_)
        if bstack1l1l1l1l_opy_():
            TestFramework.bstack1ll1l11111l_opy_((bstack1llll1ll111_opy_.TEST, bstack1lll1111l11_opy_.POST), self.bstack1ll11l11111_opy_)
        else:
            TestFramework.bstack1ll1l11111l_opy_((bstack1llll1ll111_opy_.TEST, bstack1lll1111l11_opy_.PRE), self.bstack1ll11l11111_opy_)
        TestFramework.bstack1ll1l11111l_opy_((bstack1llll1ll111_opy_.TEST, bstack1lll1111l11_opy_.POST), self.bstack1l1llllll1l_opy_)
    def is_enabled(self) -> bool:
        return True
    def bstack11lll1l1l1l_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll1l11l11_opy_,
        bstack1lll1lll111_opy_: Tuple[bstack1llll1ll111_opy_, bstack1lll1111l11_opy_],
        *args,
        **kwargs,
    ):
        bstack11lll1ll1l1_opy_ = self.bstack11lll1ll1ll_opy_(instance.context)
        if not bstack11lll1ll1l1_opy_:
            self.logger.debug(bstack11ll1_opy_ (u"ࠢࡴࡧࡷࡣࡦࡩࡴࡪࡸࡨࡣࡵࡧࡧࡦ࠼ࠣࡲࡴࠦࡰࡢࡩࡨࠤ࡫ࡵࡲࠡࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࡁࠧᖡ") + str(bstack1lll1lll111_opy_) + bstack11ll1_opy_ (u"ࠣࠤᖢ"))
            return
        f.bstack1lll111ll11_opy_(instance, bstack1l1l1l1111l_opy_.bstack1ll111lllll_opy_, bstack11lll1ll1l1_opy_)
    def bstack11lll1ll1ll_opy_(self, context: bstack1ll1111lll1_opy_, bstack11lll1l1ll1_opy_= True):
        if bstack11lll1l1ll1_opy_:
            bstack11lll1ll1l1_opy_ = self.bstack1l1lllllll1_opy_(context, reverse=True)
        else:
            bstack11lll1ll1l1_opy_ = self.bstack1ll1111111l_opy_(context, reverse=True)
        return [f for f in bstack11lll1ll1l1_opy_ if f[1].state != bstack1ll11lllll1_opy_.QUIT]
    def bstack1ll11l11111_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll1l11l11_opy_,
        bstack1lll1lll111_opy_: Tuple[bstack1llll1ll111_opy_, bstack1lll1111l11_opy_],
        *args,
        **kwargs,
    ):
        self.bstack11lll1l1l1l_opy_(f, instance, bstack1lll1lll111_opy_, *args, **kwargs)
        if not bstack1ll111l11l1_opy_:
            self.logger.debug(bstack11ll1_opy_ (u"ࠤࡲࡲࡤࡨࡥࡧࡱࡵࡩࡤࡺࡥࡴࡶ࠽ࠤࡳࡵࡴࠡࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠡࡨࡲࡶࠥ࡮࡯ࡰ࡭ࡢ࡭ࡳ࡬࡯࠾ࡽ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࢂࠦࡡࡳࡩࡶࡁࢀࡧࡲࡨࡵࢀࠤࡰࡽࡡࡳࡩࡶࡁࠧᖣ") + str(kwargs) + bstack11ll1_opy_ (u"ࠥࠦᖤ"))
            return
        bstack11lll1ll1l1_opy_ = f.bstack1ll1llll11l_opy_(instance, bstack1l1l1l1111l_opy_.bstack1ll111lllll_opy_, [])
        if not bstack11lll1ll1l1_opy_:
            self.logger.debug(bstack11ll1_opy_ (u"ࠦࡴࡴ࡟ࡣࡧࡩࡳࡷ࡫࡟ࡵࡧࡶࡸ࠿ࠦ࡮ࡰࠢࡧࡶ࡮ࡼࡥࡳࡵࠣࡪࡴࡸࠠࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࡀࡿ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵࡽࠡࡣࡵ࡫ࡸࡃࡻࡢࡴࡪࡷࢂࠦ࡫ࡸࡣࡵ࡫ࡸࡃࠢᖥ") + str(kwargs) + bstack11ll1_opy_ (u"ࠧࠨᖦ"))
            return
        if len(bstack11lll1ll1l1_opy_) > 1:
            self.logger.debug(
                bstack1l1ll111l1l_opy_ (u"ࠨ࡯࡯ࡡࡥࡩ࡫ࡵࡲࡦࡡࡷࡩࡸࡺ࠺ࠡࡽ࡯ࡩࡳ࠮ࡰࡢࡩࡨࡣ࡮ࡴࡳࡵࡣࡱࡧࡪࡹࠩࡾࠢࡧࡶ࡮ࡼࡥࡳࡵࠣࡪࡴࡸࠠࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࡀࡿ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵࡽࠡࡣࡵ࡫ࡸࡃࡻࡢࡴࡪࡷࢂࠦ࡫ࡸࡣࡵ࡫ࡸࡃࡻ࡬ࡹࡤࡶ࡬ࡹࡽࠣᖧ"))
        bstack11lll1l1lll_opy_, bstack1ll111lll1l_opy_ = bstack11lll1ll1l1_opy_[0]
        page = bstack11lll1l1lll_opy_()
        if not page:
            self.logger.debug(bstack11ll1_opy_ (u"ࠢࡰࡰࡢࡦࡪ࡬࡯ࡳࡧࡢࡸࡪࡹࡴ࠻ࠢࡱࡳࠥࡶࡡࡨࡧࠣࡪࡴࡸࠠࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࡀࡿ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵࡽࠡࡣࡵ࡫ࡸࡃࡻࡢࡴࡪࡷࢂࠦ࡫ࡸࡣࡵ࡫ࡸࡃࠢᖨ") + str(kwargs) + bstack11ll1_opy_ (u"ࠣࠤᖩ"))
            return
        bstack1lll1l1l1_opy_ = getattr(args[0], bstack11ll1_opy_ (u"ࠤࡱࡳࡩ࡫ࡩࡥࠤᖪ"), None)
        from browserstack_sdk.sdk_cli.cli import cli
        if not cli.config.get(bstack11ll1_opy_ (u"ࠥࡸࡪࡹࡴࡄࡱࡱࡸࡪࡾࡴࡐࡲࡷ࡭ࡴࡴࡳࠣᖫ")).get(bstack11ll1_opy_ (u"ࠦࡸࡱࡩࡱࡕࡨࡷࡸ࡯࡯࡯ࡐࡤࡱࡪࠨᖬ")):
            try:
                page.evaluate(bstack11ll1_opy_ (u"ࠧࡥࠠ࠾ࡀࠣࡿࢂࠨᖭ"),
                            bstack11ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤ࡫ࡸࡦࡥࡸࡸࡴࡸ࠺ࠡࡽࠥࡥࡨࡺࡩࡰࡰࠥ࠾ࠥࠨࡳࡦࡶࡖࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠢ࠭ࠢࠥࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸࠨ࠺ࠡࡽࠥࡲࡦࡳࡥࠣ࠼ࠪᖮ") + json.dumps(
                                bstack1lll1l1l1_opy_) + bstack11ll1_opy_ (u"ࠢࡾࡿࠥᖯ"))
            except Exception as e:
                self.logger.debug(bstack11ll1_opy_ (u"ࠣࡧࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡱ࡮ࡤࡽࡼࡸࡩࡨࡪࡷࠤࡸ࡫ࡳࡴ࡫ࡲࡲࠥࡴࡡ࡮ࡧࠣࡿࢂࠨᖰ"), e)
    def bstack1l1llllll1l_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll1l11l11_opy_,
        bstack1lll1lll111_opy_: Tuple[bstack1llll1ll111_opy_, bstack1lll1111l11_opy_],
        *args,
        **kwargs,
    ):
        self.bstack11lll1l1l1l_opy_(f, instance, bstack1lll1lll111_opy_, *args, **kwargs)
        if not bstack1ll111l11l1_opy_:
            self.logger.debug(bstack11ll1_opy_ (u"ࠤࡲࡲࡤࡨࡥࡧࡱࡵࡩࡤࡺࡥࡴࡶ࠽ࠤࡳࡵࡴࠡࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠡࡨࡲࡶࠥ࡮࡯ࡰ࡭ࡢ࡭ࡳ࡬࡯࠾ࡽ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࢂࠦࡡࡳࡩࡶࡁࢀࡧࡲࡨࡵࢀࠤࡰࡽࡡࡳࡩࡶࡁࠧᖱ") + str(kwargs) + bstack11ll1_opy_ (u"ࠥࠦᖲ"))
            return
        bstack11lll1ll1l1_opy_ = f.bstack1ll1llll11l_opy_(instance, bstack1l1l1l1111l_opy_.bstack1ll111lllll_opy_, [])
        if not bstack11lll1ll1l1_opy_:
            self.logger.debug(bstack11ll1_opy_ (u"ࠦࡴࡴ࡟ࡣࡧࡩࡳࡷ࡫࡟ࡵࡧࡶࡸ࠿ࠦ࡮ࡰࠢࡧࡶ࡮ࡼࡥࡳࡵࠣࡪࡴࡸࠠࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࡀࡿ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵࡽࠡࡣࡵ࡫ࡸࡃࡻࡢࡴࡪࡷࢂࠦ࡫ࡸࡣࡵ࡫ࡸࡃࠢᖳ") + str(kwargs) + bstack11ll1_opy_ (u"ࠧࠨᖴ"))
            return
        if len(bstack11lll1ll1l1_opy_) > 1:
            self.logger.debug(
                bstack1l1ll111l1l_opy_ (u"ࠨ࡯࡯ࡡࡥࡩ࡫ࡵࡲࡦࡡࡷࡩࡸࡺ࠺ࠡࡽ࡯ࡩࡳ࠮ࡰࡢࡩࡨࡣ࡮ࡴࡳࡵࡣࡱࡧࡪࡹࠩࡾࠢࡧࡶ࡮ࡼࡥࡳࡵࠣࡪࡴࡸࠠࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࡀࡿ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵࡽࠡࡣࡵ࡫ࡸࡃࡻࡢࡴࡪࡷࢂࠦ࡫ࡸࡣࡵ࡫ࡸࡃࡻ࡬ࡹࡤࡶ࡬ࡹࡽࠣᖵ"))
        bstack11lll1l1lll_opy_, bstack1ll111lll1l_opy_ = bstack11lll1ll1l1_opy_[0]
        page = bstack11lll1l1lll_opy_()
        if not page:
            self.logger.debug(bstack11ll1_opy_ (u"ࠢࡰࡰࡢࡦࡪ࡬࡯ࡳࡧࡢࡸࡪࡹࡴ࠻ࠢࡱࡳࠥࡶࡡࡨࡧࠣࡪࡴࡸࠠࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࡀࡿ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵࡽࠡࡣࡵ࡫ࡸࡃࡻࡢࡴࡪࡷࢂࠦ࡫ࡸࡣࡵ࡫ࡸࡃࠢᖶ") + str(kwargs) + bstack11ll1_opy_ (u"ࠣࠤᖷ"))
            return
        status = f.bstack1ll1llll11l_opy_(instance, TestFramework.bstack1ll1ll1ll1l_opy_, None)
        if not status:
            self.logger.debug(bstack11ll1_opy_ (u"ࠤࡱࡳࠥࡹࡴࡢࡶࡸࡷࠥ࡬࡯ࡳࠢࡷࡩࡸࡺࠬࠡࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࡁࠧᖸ") + str(bstack1lll1lll111_opy_) + bstack11ll1_opy_ (u"ࠥࠦᖹ"))
            return
        bstack1ll111l1lll_opy_ = {bstack11ll1_opy_ (u"ࠦࡸࡺࡡࡵࡷࡶࠦᖺ"): status.lower()}
        bstack1ll1111ll11_opy_ = f.bstack1ll1llll11l_opy_(instance, TestFramework.bstack1lll11ll1l1_opy_, None)
        if status.lower() == bstack11ll1_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡨࡨࠬᖻ") and bstack1ll1111ll11_opy_ is not None:
            bstack1ll111l1lll_opy_[bstack11ll1_opy_ (u"࠭ࡲࡦࡣࡶࡳࡳ࠭ᖼ")] = bstack1ll1111ll11_opy_[0][bstack11ll1_opy_ (u"ࠧࡣࡣࡦ࡯ࡹࡸࡡࡤࡧࠪᖽ")][0] if isinstance(bstack1ll1111ll11_opy_, list) else str(bstack1ll1111ll11_opy_)
        from browserstack_sdk.sdk_cli.cli import cli
        if not cli.config.get(bstack11ll1_opy_ (u"ࠣࡶࡨࡷࡹࡉ࡯࡯ࡶࡨࡼࡹࡕࡰࡵ࡫ࡲࡲࡸࠨᖾ")).get(bstack11ll1_opy_ (u"ࠤࡶ࡯࡮ࡶࡓࡦࡵࡶ࡭ࡴࡴࡓࡵࡣࡷࡹࡸࠨᖿ")):
            try:
                page.evaluate(
                        bstack11ll1_opy_ (u"ࠥࡣࠥࡃ࠾ࠡࡽࢀࠦᗀ"),
                        bstack11ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡩࡽ࡫ࡣࡶࡶࡲࡶ࠿ࠦࡻࠣࡣࡦࡸ࡮ࡵ࡮ࠣ࠼ࠣࠦࡸ࡫ࡴࡔࡧࡶࡷ࡮ࡵ࡮ࡔࡶࡤࡸࡺࡹࠢ࠭ࠢࠥࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸࠨ࠺ࠡࠩᗁ")
                        + json.dumps(bstack1ll111l1lll_opy_)
                        + bstack11ll1_opy_ (u"ࠧࢃࠢᗂ")
                    )
            except Exception as e:
                self.logger.debug(bstack11ll1_opy_ (u"ࠨࡥࡹࡥࡨࡴࡹ࡯࡯࡯ࠢ࡬ࡲࠥࡶ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵࠢࡶࡩࡸࡹࡩࡰࡰࠣࡷࡹࡧࡴࡶࡵࠣࡿࢂࠨᗃ"), e)
    def bstack1ll11111l11_opy_(
        self,
        instance: bstack1lll1l11l11_opy_,
        f: TestFramework,
        bstack1lll1lll111_opy_: Tuple[bstack1llll1ll111_opy_, bstack1lll1111l11_opy_],
        *args,
        **kwargs,
    ):
        self.bstack11lll1l1l1l_opy_(f, instance, bstack1lll1lll111_opy_, *args, **kwargs)
        if not bstack1ll111l11l1_opy_:
            self.logger.debug(
                bstack1l1ll111l1l_opy_ (u"ࠢ࡮ࡣࡵ࡯ࡤࡵ࠱࠲ࡻࡢࡷࡾࡴࡣ࠻ࠢࡱࡳࡹࠦࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࠥࡹࡥࡴࡵ࡬ࡳࡳ࠲ࠠࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࡀࡿ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵࡽࠡࡣࡵ࡫ࡸࡃࡻࡢࡴࡪࡷࢂࠦ࡫ࡸࡣࡵ࡫ࡸࡃࡻ࡬ࡹࡤࡶ࡬ࡹࡽࠣᗄ"))
            return
        bstack11lll1ll1l1_opy_ = f.bstack1ll1llll11l_opy_(instance, bstack1l1l1l1111l_opy_.bstack1ll111lllll_opy_, [])
        if not bstack11lll1ll1l1_opy_:
            self.logger.debug(bstack11ll1_opy_ (u"ࠣࡱࡱࡣࡧ࡫ࡦࡰࡴࡨࡣࡹ࡫ࡳࡵ࠼ࠣࡲࡴࠦࡤࡳ࡫ࡹࡩࡷࡹࠠࡧࡱࡵࠤ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵ࠽ࡼࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࢁࠥࡧࡲࡨࡵࡀࡿࡦࡸࡧࡴࡿࠣ࡯ࡼࡧࡲࡨࡵࡀࠦᗅ") + str(kwargs) + bstack11ll1_opy_ (u"ࠤࠥᗆ"))
            return
        if len(bstack11lll1ll1l1_opy_) > 1:
            self.logger.debug(
                bstack1l1ll111l1l_opy_ (u"ࠥࡳࡳࡥࡢࡦࡨࡲࡶࡪࡥࡴࡦࡵࡷ࠾ࠥࢁ࡬ࡦࡰࠫࡴࡦ࡭ࡥࡠ࡫ࡱࡷࡹࡧ࡮ࡤࡧࡶ࠭ࢂࠦࡤࡳ࡫ࡹࡩࡷࡹࠠࡧࡱࡵࠤ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵ࠽ࡼࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࢁࠥࡧࡲࡨࡵࡀࡿࡦࡸࡧࡴࡿࠣ࡯ࡼࡧࡲࡨࡵࡀࡿࡰࡽࡡࡳࡩࡶࢁࠧᗇ"))
        bstack11lll1l1lll_opy_, bstack1ll111lll1l_opy_ = bstack11lll1ll1l1_opy_[0]
        page = bstack11lll1l1lll_opy_()
        if not page:
            self.logger.debug(bstack11ll1_opy_ (u"ࠦࡲࡧࡲ࡬ࡡࡲ࠵࠶ࡿ࡟ࡴࡻࡱࡧ࠿ࠦ࡮ࡰࠢࡳࡥ࡬࡫ࠠࡧࡱࡵࠤ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵ࠽ࡼࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࢁࠥࡧࡲࡨࡵࡀࡿࡦࡸࡧࡴࡿࠣ࡯ࡼࡧࡲࡨࡵࡀࠦᗈ") + str(kwargs) + bstack11ll1_opy_ (u"ࠧࠨᗉ"))
            return
        timestamp = int(time.time() * 1000)
        data = bstack11ll1_opy_ (u"ࠨࡏࡣࡵࡨࡶࡻࡧࡢࡪ࡮࡬ࡸࡾ࡙ࡹ࡯ࡥ࠽ࠦᗊ") + str(timestamp)
        try:
            page.evaluate(
                bstack11ll1_opy_ (u"ࠢࡠࠢࡀࡂࠥࢁࡽࠣᗋ"),
                bstack11ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࡿࢂ࠭ᗌ").format(
                    json.dumps(
                        {
                            bstack11ll1_opy_ (u"ࠤࡤࡧࡹ࡯࡯࡯ࠤᗍ"): bstack11ll1_opy_ (u"ࠥࡥࡳࡴ࡯ࡵࡣࡷࡩࠧᗎ"),
                            bstack11ll1_opy_ (u"ࠦࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠢᗏ"): {
                                bstack11ll1_opy_ (u"ࠧࡺࡹࡱࡧࠥᗐ"): bstack11ll1_opy_ (u"ࠨࡁ࡯ࡰࡲࡸࡦࡺࡩࡰࡰࠥᗑ"),
                                bstack11ll1_opy_ (u"ࠢࡥࡣࡷࡥࠧᗒ"): data,
                                bstack11ll1_opy_ (u"ࠣ࡮ࡨࡺࡪࡲࠢᗓ"): bstack11ll1_opy_ (u"ࠤࡧࡩࡧࡻࡧࠣᗔ")
                            }
                        }
                    )
                )
            )
        except Exception as e:
            self.logger.debug(bstack11ll1_opy_ (u"ࠥࡩࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡩ࡯ࠢࡳࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹࠦ࡯࠲࠳ࡼࠤࡦࡴ࡮ࡰࡶࡤࡸ࡮ࡵ࡮ࠡ࡯ࡤࡶࡰ࡯࡮ࡨࠢࡾࢁࠧᗕ"), e)
    def bstack1ll111l11ll_opy_(
        self,
        instance: bstack1lll1l11l11_opy_,
        f: TestFramework,
        bstack1lll1lll111_opy_: Tuple[bstack1llll1ll111_opy_, bstack1lll1111l11_opy_],
        *args,
        **kwargs,
    ):
        self.bstack11lll1l1l1l_opy_(f, instance, bstack1lll1lll111_opy_, *args, **kwargs)
        if f.bstack1ll1llll11l_opy_(instance, bstack1l1l1l1111l_opy_.bstack1l1llllllll_opy_, False):
            return
        self.bstack1ll111111l1_opy_()
        req = structs.TestSessionEventRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = TestFramework.bstack1ll1llll11l_opy_(instance, TestFramework.bstack1lll11l1l1l_opy_)
        req.test_framework_name = TestFramework.bstack1ll1llll11l_opy_(instance, TestFramework.bstack1lll1111111_opy_)
        req.test_framework_version = TestFramework.bstack1ll1llll11l_opy_(instance, TestFramework.bstack1lll11111ll_opy_)
        req.test_framework_state = bstack1lll1lll111_opy_[0].name
        req.test_hook_state = bstack1lll1lll111_opy_[1].name
        req.test_uuid = TestFramework.bstack1ll1llll11l_opy_(instance, TestFramework.bstack1llll111ll1_opy_)
        for bstack11lll1ll111_opy_ in bstack1ll11l11l1l_opy_.bstack1lll1llllll_opy_.values():
            session = req.automation_sessions.add()
            session.provider = (
                bstack11ll1_opy_ (u"ࠦࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࠥᗖ")
                if bstack1ll111l11l1_opy_
                else bstack11ll1_opy_ (u"ࠧࡻ࡮࡬ࡰࡲࡻࡳࡥࡧࡳ࡫ࡧࠦᗗ")
            )
            session.ref = bstack11lll1ll111_opy_.ref()
            session.hub_url = bstack1ll11l11l1l_opy_.bstack1ll1llll11l_opy_(bstack11lll1ll111_opy_, bstack1ll11l11l1l_opy_.bstack1ll1l1ll111_opy_, bstack11ll1_opy_ (u"ࠨࠢᗘ"))
            session.framework_name = bstack11lll1ll111_opy_.framework_name
            session.framework_version = bstack11lll1ll111_opy_.framework_version
            session.framework_session_id = bstack1ll11l11l1l_opy_.bstack1ll1llll11l_opy_(bstack11lll1ll111_opy_, bstack1ll11l11l1l_opy_.bstack1ll11ll1111_opy_, bstack11ll1_opy_ (u"ࠢࠣᗙ"))
        req.execution_context.hash = str(instance.context.hash)
        req.execution_context.thread_id = str(instance.context.thread_id)
        req.execution_context.process_id = str(instance.context.process_id)
        return req
    def bstack1l1lllll1l1_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll1l11l11_opy_,
        bstack1lll1lll111_opy_: Tuple[bstack1llll1ll111_opy_, bstack1lll1111l11_opy_],
        *args,
        **kwargs
    ):
        bstack11lll1ll1l1_opy_ = f.bstack1ll1llll11l_opy_(instance, bstack1l1l1l1111l_opy_.bstack1ll111lllll_opy_, [])
        if not bstack11lll1ll1l1_opy_:
            self.logger.debug(bstack11ll1_opy_ (u"ࠣࡩࡨࡸࡤࡧࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࡡࡧࡶ࡮ࡼࡥࡳ࠼ࠣࡲࡴࠦࡰࡢࡩࡨࡷࠥ࡬࡯ࡳࠢ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࡂࢁࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰࡿࠣࡥࡷ࡭ࡳ࠾ࡽࡤࡶ࡬ࡹࡽࠡ࡭ࡺࡥࡷ࡭ࡳ࠾ࠤᗚ") + str(kwargs) + bstack11ll1_opy_ (u"ࠤࠥᗛ"))
            return
        if len(bstack11lll1ll1l1_opy_) > 1:
            self.logger.debug(bstack11ll1_opy_ (u"ࠥ࡫ࡪࡺ࡟ࡢࡷࡷࡳࡲࡧࡴࡪࡱࡱࡣࡩࡸࡩࡷࡧࡵ࠾ࠥࢁ࡬ࡦࡰࠫࡴࡦ࡭ࡥࡠ࡫ࡱࡷࡹࡧ࡮ࡤࡧࡶ࠭ࢂࠦࡤࡳ࡫ࡹࡩࡷࡹࠠࡧࡱࡵࠤ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵ࠽ࡼࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࢁࠥࡧࡲࡨࡵࡀࡿࡦࡸࡧࡴࡿࠣ࡯ࡼࡧࡲࡨࡵࡀࠦᗜ") + str(kwargs) + bstack11ll1_opy_ (u"ࠦࠧᗝ"))
        bstack11lll1l1lll_opy_, bstack1ll111lll1l_opy_ = bstack11lll1ll1l1_opy_[0]
        page = bstack11lll1l1lll_opy_()
        if not page:
            self.logger.debug(bstack11ll1_opy_ (u"ࠧ࡭ࡥࡵࡡࡤࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳࡥࡤࡳ࡫ࡹࡩࡷࡀࠠ࡯ࡱࠣࡴࡦ࡭ࡥࠡࡨࡲࡶࠥ࡮࡯ࡰ࡭ࡢ࡭ࡳ࡬࡯࠾ࡽ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࢂࠦࡡࡳࡩࡶࡁࢀࡧࡲࡨࡵࢀࠤࡰࡽࡡࡳࡩࡶࡁࠧᗞ") + str(kwargs) + bstack11ll1_opy_ (u"ࠨࠢᗟ"))
            return
        return page
    def bstack1ll111lll11_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll1l11l11_opy_,
        bstack1lll1lll111_opy_: Tuple[bstack1llll1ll111_opy_, bstack1lll1111l11_opy_],
        *args,
        **kwargs
    ):
        caps = {}
        bstack11lll1ll11l_opy_ = {}
        for bstack11lll1ll111_opy_ in bstack1ll11l11l1l_opy_.bstack1lll1llllll_opy_.values():
            caps = bstack1ll11l11l1l_opy_.bstack1ll1llll11l_opy_(bstack11lll1ll111_opy_, bstack1ll11l11l1l_opy_.bstack1ll11ll1l11_opy_, bstack11ll1_opy_ (u"ࠢࠣᗠ"))
        bstack11lll1ll11l_opy_[bstack11ll1_opy_ (u"ࠣࡤࡵࡳࡼࡹࡥࡳࡐࡤࡱࡪࠨᗡ")] = caps.get(bstack11ll1_opy_ (u"ࠤࡥࡶࡴࡽࡳࡦࡴࠥᗢ"), bstack11ll1_opy_ (u"ࠥࠦᗣ"))
        bstack11lll1ll11l_opy_[bstack11ll1_opy_ (u"ࠦࡵࡲࡡࡵࡨࡲࡶࡲࡔࡡ࡮ࡧࠥᗤ")] = caps.get(bstack11ll1_opy_ (u"ࠧࡵࡳࠣᗥ"), bstack11ll1_opy_ (u"ࠨࠢᗦ"))
        bstack11lll1ll11l_opy_[bstack11ll1_opy_ (u"ࠢࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡘࡨࡶࡸ࡯࡯࡯ࠤᗧ")] = caps.get(bstack11ll1_opy_ (u"ࠣࡱࡶࡣࡻ࡫ࡲࡴ࡫ࡲࡲࠧᗨ"), bstack11ll1_opy_ (u"ࠤࠥᗩ"))
        bstack11lll1ll11l_opy_[bstack11ll1_opy_ (u"ࠥࡦࡷࡵࡷࡴࡧࡵ࡚ࡪࡸࡳࡪࡱࡱࠦᗪ")] = caps.get(bstack11ll1_opy_ (u"ࠦࡧࡸ࡯ࡸࡵࡨࡶࡤࡼࡥࡳࡵ࡬ࡳࡳࠨᗫ"), bstack11ll1_opy_ (u"ࠧࠨᗬ"))
        return bstack11lll1ll11l_opy_
    def bstack1l11ll11l11_opy_(self, page: object, bstack1l111ll1ll1_opy_, args={}):
        try:
            bstack11lll1l1l11_opy_ = bstack11ll1_opy_ (u"ࠨࠢࠣࠪࡩࡹࡳࡩࡴࡪࡱࡱࠤ࠭࠴࠮࠯ࡤࡶࡸࡦࡩ࡫ࡔࡦ࡮ࡅࡷ࡭ࡳࠪࠢࡾࡿࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࡳࡧࡷࡹࡷࡴࠠ࡯ࡧࡺࠤࡕࡸ࡯࡮࡫ࡶࡩ࠭࠮ࡲࡦࡵࡲࡰࡻ࡫ࠬࠡࡴࡨ࡮ࡪࡩࡴࠪࠢࡀࡂࠥࢁࡻࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࡣࡵࡷࡥࡨࡱࡓࡥ࡭ࡄࡶ࡬ࡹ࠮ࡱࡷࡶ࡬࠭ࡸࡥࡴࡱ࡯ࡺࡪ࠯࠻ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࡼࡨࡱࡣࡧࡵࡤࡺࡿࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࢃࡽࠪ࠽ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࡿࢀ࠭࠭ࢁࡡࡳࡩࡢ࡮ࡸࡵ࡮ࡾࠫࠥࠦࠧᗭ")
            bstack1l111ll1ll1_opy_ = bstack1l111ll1ll1_opy_.replace(bstack11ll1_opy_ (u"ࠢࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠥᗮ"), bstack11ll1_opy_ (u"ࠣࡤࡶࡸࡦࡩ࡫ࡔࡦ࡮ࡅࡷ࡭ࡳࠣᗯ"))
            script = bstack11lll1l1l11_opy_.format(fn_body=bstack1l111ll1ll1_opy_, arg_json=json.dumps(args))
            return page.evaluate(script)
        except Exception as e:
            self.logger.error(bstack11ll1_opy_ (u"ࠤࡤ࠵࠶ࡿ࡟ࡴࡥࡵ࡭ࡵࡺ࡟ࡦࡺࡨࡧࡺࡺࡥ࠻ࠢࡈࡶࡷࡵࡲࠡࡧࡻࡩࡨࡻࡴࡪࡰࡪࠤࡹ࡮ࡥࠡࡣ࠴࠵ࡾࠦࡳࡤࡴ࡬ࡴࡹ࠲ࠠࠣᗰ") + str(e) + bstack11ll1_opy_ (u"ࠥࠦᗱ"))