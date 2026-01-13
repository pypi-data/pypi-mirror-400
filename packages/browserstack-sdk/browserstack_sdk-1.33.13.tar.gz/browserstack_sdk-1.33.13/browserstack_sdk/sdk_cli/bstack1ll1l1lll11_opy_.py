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
from datetime import datetime
import os
import threading
from browserstack_sdk.sdk_cli.bstack1llll11l1ll_opy_ import (
    bstack1llll1111l1_opy_,
    bstack1lll1lll1l1_opy_,
    bstack1llll111ll1_opy_,
    bstack1llll1ll1ll_opy_,
)
from browserstack_sdk.sdk_cli.bstack1lll1l11l11_opy_ import bstack1lll11l111l_opy_
from browserstack_sdk.sdk_cli.test_framework import TestFramework, bstack1lll111l111_opy_, bstack1lll1l1l11l_opy_, bstack1ll1ll11lll_opy_
from typing import Tuple, Dict, Any, List, Union
from browserstack_sdk import sdk_pb2 as structs
from browserstack_sdk.sdk_cli.bstack1ll1l1ll1ll_opy_ import bstack1ll1ll1l1ll_opy_
from browserstack_sdk.sdk_cli.bstack1ll11lllll1_opy_ import bstack1ll11ll1l1l_opy_
from browserstack_sdk.sdk_cli.bstack1lll11l1ll1_opy_ import bstack1lll11l11l1_opy_
from browserstack_sdk.sdk_cli.bstack1ll1l111ll1_opy_ import bstack1ll1l1111l1_opy_
from bstack_utils.helper import bstack1l1llll111l_opy_
from bstack_utils.measure import measure
from bstack_utils.constants import *
from bstack_utils.bstack11l1l11ll_opy_ import bstack1lll1ll1l11_opy_
from bstack_utils import bstack1l1lll1l11_opy_
import grpc
import traceback
import json
class bstack1ll1l11l11l_opy_(bstack1ll1ll1l1ll_opy_):
    bstack1ll111lll1l_opy_ = False
    bstack1ll11111ll1_opy_ = bstack11l1l_opy_ (u"ࠣࡵࡨࡰࡪࡴࡩࡶ࡯࠱ࡻࡪࡨࡤࡳ࡫ࡹࡩࡷࠨᇣ")
    bstack1l1lll1llll_opy_ = bstack11l1l_opy_ (u"ࠤࡵࡩࡲࡵࡴࡦ࠰ࡺࡩࡧࡪࡲࡪࡸࡨࡶࠧᇤ")
    bstack1l1lll1l11l_opy_ = bstack11l1l_opy_ (u"ࠥࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࡢ࡭ࡳ࡯ࡴࠣᇥ")
    bstack1ll111ll1ll_opy_ = bstack11l1l_opy_ (u"ࠦࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࡣ࡮ࡹ࡟ࡴࡥࡤࡲࡳ࡯࡮ࡨࠤᇦ")
    bstack1ll111l1lll_opy_ = bstack11l1l_opy_ (u"ࠧࡪࡲࡪࡸࡨࡶࡤ࡮ࡡࡴࡡࡸࡶࡱࠨᇧ")
    scripts: Dict[str, Dict[str, str]]
    commands: Dict[str, Dict[str, Dict[str, List[str]]]]
    def __init__(self, bstack1lll1l1l1ll_opy_, bstack1ll1l111lll_opy_):
        super().__init__()
        self.scripts = dict()
        self.commands = dict()
        self.accessibility = False
        self.bstack1ll11l1l1l1_opy_ = False
        self.bstack1ll111111ll_opy_ = dict()
        self.bstack1ll11l1ll_opy_ = bstack1l1lll1l11_opy_.bstack1l111111_opy_(__name__)
        self.bstack1ll1111111l_opy_ = False
        self.bstack1ll111ll11l_opy_ = dict()
        if not self.is_enabled():
            return
        self.bstack1l1llllll1l_opy_ = bstack1ll1l111lll_opy_
        bstack1lll1l1l1ll_opy_.bstack1ll111ll111_opy_((bstack1llll1111l1_opy_.bstack1lll1ll1ll1_opy_, bstack1lll1lll1l1_opy_.PRE), self.bstack1ll111l111l_opy_)
        TestFramework.bstack1ll111ll111_opy_((bstack1lll111l111_opy_.TEST, bstack1lll1l1l11l_opy_.PRE), self.bstack1ll111l1l11_opy_)
        TestFramework.bstack1ll111ll111_opy_((bstack1lll111l111_opy_.TEST, bstack1lll1l1l11l_opy_.POST), self.bstack1l1llll1l11_opy_)
    def is_enabled(self) -> bool:
        return True
    def bstack1ll111l1l11_opy_(
        self,
        f: TestFramework,
        instance: bstack1ll1ll11lll_opy_,
        bstack1llll1lll1l_opy_: Tuple[bstack1lll111l111_opy_, bstack1lll1l1l11l_opy_],
        *args,
        **kwargs,
    ):
        tags = self._1l1lll1lll1_opy_(instance, args)
        test_framework = f.bstack1llll1lllll_opy_(instance, TestFramework.bstack1l1llll11l1_opy_)
        if self.bstack1ll11l1l1l1_opy_:
            self.bstack1ll111111ll_opy_[bstack11l1l_opy_ (u"ࠨࡴࡦࡵࡷࡣࡷࡻ࡮ࡠࡷࡸ࡭ࡩࠨᇨ")] = f.bstack1llll1lllll_opy_(instance, TestFramework.bstack1ll11l11l1l_opy_)
        if bstack11l1l_opy_ (u"ࠧࡱࡻࡷࡩࡸࡺ࠭ࡣࡦࡧࠫᇩ") in instance.bstack1l1llll1lll_opy_:
            platform_index = f.bstack1llll1lllll_opy_(instance, TestFramework.bstack1ll1111l111_opy_)
            self.accessibility = self.bstack1l1lll11l11_opy_(tags, self.config[bstack11l1l_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫᇪ")][platform_index])
        else:
            capabilities = self.bstack1l1llllll1l_opy_.bstack1l1lll1l1ll_opy_(f, instance, bstack1llll1lll1l_opy_, *args, **kwargs)
            if not capabilities:
                self.logger.debug(bstack11l1l_opy_ (u"ࠤࡲࡲࡤࡨࡥࡧࡱࡵࡩࡤࡺࡥࡴࡶ࠽ࠤࡳࡵࠠࡤࡣࡳࡥࡧ࡯࡬ࡪࡶ࡬ࡩࡸࠦࡦࡰࡷࡱࡨࠥ࡬࡯ࡳࠢ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࡂࢁࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰࡿࠣࡥࡷ࡭ࡳ࠾ࡽࡤࡶ࡬ࡹࡽࠡ࡭ࡺࡥࡷ࡭ࡳ࠾ࠤᇫ") + str(kwargs) + bstack11l1l_opy_ (u"ࠥࠦᇬ"))
                return
            self.accessibility = self.bstack1l1lll11l11_opy_(tags, capabilities)
        if self.bstack1l1llllll1l_opy_.pages and self.bstack1l1llllll1l_opy_.pages.values():
            bstack1ll111l1l1l_opy_ = list(self.bstack1l1llllll1l_opy_.pages.values())
            if bstack1ll111l1l1l_opy_ and isinstance(bstack1ll111l1l1l_opy_[0], (list, tuple)) and bstack1ll111l1l1l_opy_[0]:
                bstack1ll111ll1l1_opy_ = bstack1ll111l1l1l_opy_[0][0]
                if callable(bstack1ll111ll1l1_opy_):
                    page = bstack1ll111ll1l1_opy_()
                    def bstack111ll1llll_opy_():
                        self.get_accessibility_results(page, bstack11l1l_opy_ (u"ࠦࡵࡲࡡࡺࡹࡵ࡭࡬࡮ࡴࠣᇭ"))
                    def bstack1ll111l11l1_opy_():
                        self.get_accessibility_results_summary(page, bstack11l1l_opy_ (u"ࠧࡶ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵࠤᇮ"))
                    setattr(page, bstack11l1l_opy_ (u"ࠨࡧࡦࡶࡄࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࡔࡨࡷࡺࡲࡴࡴࠤᇯ"), bstack111ll1llll_opy_)
                    setattr(page, bstack11l1l_opy_ (u"ࠢࡨࡧࡷࡅࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࡕࡩࡸࡻ࡬ࡵࡕࡸࡱࡲࡧࡲࡺࠤᇰ"), bstack1ll111l11l1_opy_)
        self.logger.debug(bstack11l1l_opy_ (u"ࠣࡵ࡫ࡳࡺࡲࡤࠡࡴࡸࡲࠥࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡼࡡ࡭ࡷࡨࡁࠧᇱ") + str(self.accessibility) + bstack11l1l_opy_ (u"ࠤࠥᇲ"))
    def bstack1ll111l111l_opy_(
        self,
        f: bstack1lll11l111l_opy_,
        driver: object,
        exec: Tuple[bstack1llll1ll1ll_opy_, str],
        bstack1llll1lll1l_opy_: Tuple[bstack1llll1111l1_opy_, bstack1lll1lll1l1_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        try:
            bstack11ll1l1ll1_opy_ = datetime.now()
            self.bstack1ll11111l1l_opy_(f, exec, *args, **kwargs)
            instance, method_name = exec
            instance.bstack11lll111_opy_(bstack11l1l_opy_ (u"ࠥࡥ࠶࠷ࡹ࠻࡫ࡱ࡭ࡹࡥࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࡥࡣࡰࡰࡩ࡭࡬ࠨᇳ"), datetime.now() - bstack11ll1l1ll1_opy_)
            if (
                not f.bstack1ll1111l11l_opy_(method_name)
                or f.bstack1ll11111l11_opy_(method_name, *args)
                or f.bstack1ll11l1111l_opy_(method_name, *args)
            ):
                return
            if not f.bstack1llll1lllll_opy_(instance, bstack1ll1l11l11l_opy_.bstack1l1lll1l11l_opy_, False):
                if not bstack1ll1l11l11l_opy_.bstack1ll111lll1l_opy_:
                    self.logger.warning(bstack11l1l_opy_ (u"ࠦࡠࡶ࡬ࡢࡶࡩࡳࡷࡳ࡟ࡪࡰࡧࡩࡽࡃࠢᇴ") + str(f.platform_index) + bstack11l1l_opy_ (u"ࠧࡣࠠࡢ࠳࠴ࡽࠥࡩࡡࡱࡣࡥ࡭ࡱ࡯ࡴࡪࡧࡶࠤ࡭ࡧࡶࡦࠢࡱࡳࡹࠦࡢࡦࡧࡱࠤࡸ࡫ࡴࠡࡨࡲࡶࠥࡺࡨࡪࡵࠣࡷࡪࡹࡳࡪࡱࡱࠦᇵ"))
                    bstack1ll1l11l11l_opy_.bstack1ll111lll1l_opy_ = True
                return
            bstack1l1lllll1l1_opy_ = self.scripts.get(f.framework_name, {})
            if not bstack1l1lllll1l1_opy_:
                platform_index = f.bstack1llll1lllll_opy_(instance, bstack1lll11l111l_opy_.bstack1ll1111l111_opy_, 0)
                self.logger.debug(bstack11l1l_opy_ (u"ࠨ࡮ࡰࠢࡤ࠵࠶ࡿࠠࡴࡥࡵ࡭ࡵࡺࡳࠡࡨࡲࡶࠥࡶ࡬ࡢࡶࡩࡳࡷࡳ࡟ࡪࡰࡧࡩࡽࡃࡻࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡡ࡬ࡲࡩ࡫ࡸࡾࠢࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࡤࡴࡡ࡮ࡧࡀࠦᇶ") + str(f.framework_name) + bstack11l1l_opy_ (u"ࠢࠣᇷ"))
                return
            command_name = f.bstack1ll111111l1_opy_(*args)
            if not command_name:
                self.logger.debug(bstack11l1l_opy_ (u"ࠣ࡯࡬ࡷࡸ࡯࡮ࡨࠢࡦࡳࡲࡳࡡ࡯ࡦࡢࡲࡦࡳࡥࠡࡨࡲࡶࠥ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡰࡤࡱࡪࡃࡻࡧ࠰ࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࡤࡴࡡ࡮ࡧࢀࠤࡲ࡫ࡴࡩࡱࡧࡣࡳࡧ࡭ࡦ࠿ࠥᇸ") + str(method_name) + bstack11l1l_opy_ (u"ࠤࠥᇹ"))
                return
            bstack1l1lllllll1_opy_ = f.bstack1llll1lllll_opy_(instance, bstack1ll1l11l11l_opy_.bstack1ll111l1lll_opy_, False)
            if command_name == bstack11l1l_opy_ (u"ࠥ࡫ࡪࡺࠢᇺ") and not bstack1l1lllllll1_opy_:
                f.bstack1lllll1111l_opy_(instance, bstack1ll1l11l11l_opy_.bstack1ll111l1lll_opy_, True)
                bstack1l1lllllll1_opy_ = True
            if not bstack1l1lllllll1_opy_ and not self.bstack1ll11l1l1l1_opy_:
                self.logger.debug(bstack11l1l_opy_ (u"ࠦࡳࡵࠠࡖࡔࡏࠤࡱࡵࡡࡥࡧࡧࠤ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟࡯ࡣࡰࡩࡂࢁࡦ࠯ࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡳࡧ࡭ࡦࡿࠣࡧࡴࡳ࡭ࡢࡰࡧࡣࡳࡧ࡭ࡦ࠿ࠥᇻ") + str(command_name) + bstack11l1l_opy_ (u"ࠧࠨᇼ"))
                return
            scripts_to_run = self.commands.get(f.framework_name, {}).get(method_name, {}).get(command_name, [])
            if not scripts_to_run:
                self.logger.debug(bstack11l1l_opy_ (u"ࠨ࡮ࡰࠢࡤ࠵࠶ࡿࠠࡴࡥࡵ࡭ࡵࡺࡳࠡࡨࡲࡶࠥ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡰࡤࡱࡪࡃࡻࡧ࠰ࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࡤࡴࡡ࡮ࡧࢀࠤࡨࡵ࡭࡮ࡣࡱࡨࡤࡴࡡ࡮ࡧࡀࠦᇽ") + str(command_name) + bstack11l1l_opy_ (u"ࠢࠣᇾ"))
                return
            self.logger.info(bstack11l1l_opy_ (u"ࠣࡴࡸࡲࡳ࡯࡮ࡨࠢࡾࡰࡪࡴࠨࡴࡥࡵ࡭ࡵࡺࡳࡠࡶࡲࡣࡷࡻ࡮ࠪࡿࠣࡷࡨࡸࡩࡱࡶࡶࠤ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟࡯ࡣࡰࡩࡂࢁࡦ࠯ࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡳࡧ࡭ࡦࡿࠣࡧࡴࡳ࡭ࡢࡰࡧࡣࡳࡧ࡭ࡦ࠿ࠥᇿ") + str(command_name) + bstack11l1l_opy_ (u"ࠤࠥሀ"))
            scripts = [(s, bstack1l1lllll1l1_opy_[s]) for s in scripts_to_run if s in bstack1l1lllll1l1_opy_]
            for script_name, bstack1ll11l11111_opy_ in scripts:
                try:
                    bstack11ll1l1ll1_opy_ = datetime.now()
                    if script_name == bstack11l1l_opy_ (u"ࠥࡷࡨࡧ࡮ࠣሁ"):
                        result = self.perform_scan(driver, method=command_name, framework_name=f.framework_name)
                        try:
                            bstack1ll111l1l_opy_ = {
                                bstack11l1l_opy_ (u"ࠦࡷ࡫ࡱࡶࡧࡶࡸࠧሂ"): {
                                    bstack11l1l_opy_ (u"ࠧࡩ࡯࡮࡯ࡤࡲࡩࠨሃ"): bstack11l1l_opy_ (u"ࠨࡁ࠲࠳࡜ࡣࡘࡉࡁࡏࠤሄ"),
                                    bstack11l1l_opy_ (u"ࠢࡱࡣࡵࡥࡲ࡫ࡴࡦࡴࡶࠦህ"): [
                                        {
                                            bstack11l1l_opy_ (u"ࠣ࡯ࡨࡸ࡭ࡵࡤࠣሆ"): command_name
                                        }
                                    ]
                                },
                                bstack11l1l_opy_ (u"ࠤࡵࡩࡸࡶ࡯࡯ࡵࡨࠦሇ"): {
                                    bstack11l1l_opy_ (u"ࠥࡦࡴࡪࡹࠣለ"): {
                                        bstack11l1l_opy_ (u"ࠦࡲࡹࡧࠣሉ"): result.get(bstack11l1l_opy_ (u"ࠧࡳࡳࡨࠤሊ"), bstack11l1l_opy_ (u"ࠨࠢላ")) if isinstance(result, dict) else bstack11l1l_opy_ (u"ࠢࠣሌ"),
                                        bstack11l1l_opy_ (u"ࠣࡵࡸࡧࡨ࡫ࡳࡴࠤል"): result.get(bstack11l1l_opy_ (u"ࠤࡶࡹࡨࡩࡥࡴࡵࠥሎ"), True) if isinstance(result, dict) else True
                                    }
                                }
                            }
                            self.bstack1ll11l1ll_opy_.info(json.dumps(bstack1ll111l1l_opy_, separators=(bstack11l1l_opy_ (u"ࠥ࠰ࠧሏ"), bstack11l1l_opy_ (u"ࠦ࠿ࠨሐ"))))
                        except Exception as bstack1l1l1ll1l1_opy_:
                            self.logger.debug(bstack11l1l_opy_ (u"ࠧࡌࡡࡪ࡮ࡨࡨࠥࡺ࡯ࠡ࡮ࡲ࡫ࠥࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡹࡣࡢࡰࠣࡨࡦࡺࡡ࠻ࠢࠥሑ") + str(bstack1l1l1ll1l1_opy_) + bstack11l1l_opy_ (u"ࠨࠢሒ"))
                    instance.bstack11lll111_opy_(bstack11l1l_opy_ (u"ࠢࡢ࠳࠴ࡽ࠿ࠨሓ") + script_name, datetime.now() - bstack11ll1l1ll1_opy_)
                    if isinstance(result, dict) and not result.get(bstack11l1l_opy_ (u"ࠣࡵࡸࡧࡨ࡫ࡳࡴࠤሔ"), True):
                        self.logger.warning(bstack11l1l_opy_ (u"ࠤࡶ࡯࡮ࡶࠠࡦࡺࡨࡧࡺࡺࡩ࡯ࡩࠣࡶࡪࡳࡡࡪࡰ࡬ࡲ࡬ࠦࡳࡤࡴ࡬ࡴࡹࡹ࠺ࠡࠤሕ") + str(result) + bstack11l1l_opy_ (u"ࠥࠦሖ"))
                        break
                except Exception as e:
                    self.logger.error(bstack11l1l_opy_ (u"ࠦࡪࡸࡲࡰࡴࠣࡩࡽ࡫ࡣࡶࡶ࡬ࡲ࡬ࠦࡳࡤࡴ࡬ࡴࡹࡃࡻࡴࡥࡵ࡭ࡵࡺ࡟࡯ࡣࡰࡩࢂࠦࡥࡳࡴࡲࡶࡂࠨሗ") + str(e) + bstack11l1l_opy_ (u"ࠧࠨመ"))
        except Exception as e:
            self.logger.error(bstack11l1l_opy_ (u"ࠨ࡯࡯ࡡࡥࡩ࡫ࡵࡲࡦࡡࡨࡼࡪࡩࡵࡵࡧࠣࡩࡷࡸ࡯ࡳ࠿ࠥሙ") + str(e) + bstack11l1l_opy_ (u"ࠢࠣሚ"))
    def bstack1l1llll1l11_opy_(
        self,
        f: TestFramework,
        instance: bstack1ll1ll11lll_opy_,
        bstack1llll1lll1l_opy_: Tuple[bstack1lll111l111_opy_, bstack1lll1l1l11l_opy_],
        *args,
        **kwargs,
    ):
        tags = self._1l1lll1lll1_opy_(instance, args)
        capabilities = self.bstack1l1llllll1l_opy_.bstack1l1lll1l1ll_opy_(f, instance, bstack1llll1lll1l_opy_, *args, **kwargs)
        self.accessibility = self.bstack1l1lll11l11_opy_(tags, capabilities)
        if not self.accessibility:
            self.logger.debug(bstack11l1l_opy_ (u"ࠣࡱࡱࡣࡦ࡬ࡴࡦࡴࡢࡸࡪࡹࡴ࠻ࠢࡤ࠵࠶ࡿࠠ࡯ࡱࡷࠤࡪࡴࡡࡣ࡮ࡨࡨࠧማ"))
            return
        driver = self.bstack1l1llllll1l_opy_.bstack1l1lllll111_opy_(f, instance, bstack1llll1lll1l_opy_, *args, **kwargs)
        test_name = f.bstack1llll1lllll_opy_(instance, TestFramework.bstack1l1llll1ll1_opy_)
        if not test_name:
            self.logger.debug(bstack11l1l_opy_ (u"ࠤࡲࡲࡤࡧࡦࡵࡧࡵࡣࡹ࡫ࡳࡵ࠼ࠣࡱ࡮ࡹࡳࡪࡰࡪࠤࡹ࡫ࡳࡵࠢࡱࡥࡲ࡫ࠢሜ"))
            return
        test_uuid = f.bstack1llll1lllll_opy_(instance, TestFramework.bstack1ll11l11l1l_opy_)
        if not test_uuid:
            self.logger.debug(bstack11l1l_opy_ (u"ࠥࡳࡳࡥࡡࡧࡶࡨࡶࡤࡺࡥࡴࡶ࠽ࠤࡲ࡯ࡳࡴ࡫ࡱ࡫ࠥࡺࡥࡴࡶࠣࡹࡺ࡯ࡤࠣም"))
            return
        if isinstance(self.bstack1l1llllll1l_opy_, bstack1lll11l11l1_opy_):
            framework_name = bstack11l1l_opy_ (u"ࠫࡵࡲࡡࡺࡹࡵ࡭࡬࡮ࡴࠨሞ")
        else:
            framework_name = bstack11l1l_opy_ (u"ࠬࡹࡥ࡭ࡧࡱ࡭ࡺࡳࠧሟ")
        self.bstack111ll1l1_opy_(driver, test_name, framework_name, test_uuid)
    def perform_scan(self, driver: object, method: Union[None, str], framework_name: str):
        bstack1l1llllllll_opy_ = bstack1lll1ll1l11_opy_.bstack1ll11l1l111_opy_(EVENTS.bstack1l11l1l111_opy_.value)
        if not self.accessibility:
            self.logger.debug(bstack11l1l_opy_ (u"ࠨࡰࡦࡴࡩࡳࡷࡳ࡟ࡴࡥࡤࡲ࠿ࠦࡡ࠲࠳ࡼࠤࡳࡵࡴࠡࡧࡱࡥࡧࡲࡥࡥࠢࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࡤࡴࡡ࡮ࡧࡀࡿ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟࡯ࡣࡰࡩࢂࠦࠢሠ"))
            return
        bstack11ll1l1ll1_opy_ = datetime.now()
        bstack1ll11l11111_opy_ = self.scripts.get(framework_name, {}).get(bstack11l1l_opy_ (u"ࠢࡴࡥࡤࡲࠧሡ"), None)
        if not bstack1ll11l11111_opy_:
            self.logger.debug(bstack11l1l_opy_ (u"ࠣࡲࡨࡶ࡫ࡵࡲ࡮ࡡࡶࡧࡦࡴ࠺ࠡ࡯࡬ࡷࡸ࡯࡮ࡨࠢࠪࡷࡨࡧ࡮ࠨࠢࡶࡧࡷ࡯ࡰࡵࠢࡩࡳࡷࠦࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡱࡥࡲ࡫࠽ࠣሢ") + str(framework_name) + bstack11l1l_opy_ (u"ࠤࠣࠦሣ"))
            return
        if self.bstack1ll11l1l1l1_opy_:
            arg = dict()
            arg[bstack11l1l_opy_ (u"ࠥࡱࡪࡺࡨࡰࡦࠥሤ")] = method if method else bstack11l1l_opy_ (u"ࠦࠧሥ")
            arg[bstack11l1l_opy_ (u"ࠧࡺࡨࡕࡧࡶࡸࡗࡻ࡮ࡖࡷ࡬ࡨࠧሦ")] = self.bstack1ll111111ll_opy_[bstack11l1l_opy_ (u"ࠨࡴࡦࡵࡷࡣࡷࡻ࡮ࡠࡷࡸ࡭ࡩࠨሧ")]
            arg[bstack11l1l_opy_ (u"ࠢࡵࡪࡅࡹ࡮ࡲࡤࡖࡷ࡬ࡨࠧረ")] = self.bstack1ll111111ll_opy_[bstack11l1l_opy_ (u"ࠣࡶࡨࡷࡹ࡮ࡵࡣࡡࡥࡹ࡮ࡲࡤࡠࡷࡸ࡭ࡩࠨሩ")]
            arg[bstack11l1l_opy_ (u"ࠤࡤࡹࡹ࡮ࡈࡦࡣࡧࡩࡷࠨሪ")] = self.bstack1ll111111ll_opy_[bstack11l1l_opy_ (u"ࠥࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࡗࡳࡰ࡫࡮ࠣራ")]
            arg[bstack11l1l_opy_ (u"ࠦࡹ࡮ࡊࡸࡶࡗࡳࡰ࡫࡮ࠣሬ")] = self.bstack1ll111111ll_opy_[bstack11l1l_opy_ (u"ࠧࡺࡨࡠ࡬ࡺࡸࡤࡺ࡯࡬ࡧࡱࠦር")]
            arg[bstack11l1l_opy_ (u"ࠨࡳࡤࡣࡱࡘ࡮ࡳࡥࡴࡶࡤࡱࡵࠨሮ")] = str(int(datetime.now().timestamp() * 1000))
            bstack1l1lll1ll11_opy_ = self.bstack1ll111l11ll_opy_(bstack11l1l_opy_ (u"ࠢࡴࡥࡤࡲࠧሯ"), self.bstack1ll111111ll_opy_[bstack11l1l_opy_ (u"ࠣࡶࡨࡷࡹࡥࡲࡶࡰࡢࡹࡺ࡯ࡤࠣሰ")])
            if bstack11l1l_opy_ (u"ࠤࡦࡩࡳࡺࡲࡢ࡮ࡄࡹࡹ࡮ࡔࡰ࡭ࡨࡲࠧሱ") in bstack1l1lll1ll11_opy_:
                bstack1l1lll1ll11_opy_ = bstack1l1lll1ll11_opy_.copy()
                bstack1l1lll1ll11_opy_[bstack11l1l_opy_ (u"ࠥࡧࡪࡴࡴࡳࡣ࡯ࡅࡺࡺࡨࡉࡧࡤࡨࡪࡸࠢሲ")] = bstack1l1lll1ll11_opy_.pop(bstack11l1l_opy_ (u"ࠦࡨ࡫࡮ࡵࡴࡤࡰࡆࡻࡴࡩࡖࡲ࡯ࡪࡴࠢሳ"))
            arg = bstack1l1llll111l_opy_(arg, bstack1l1lll1ll11_opy_)
            bstack1l1lll111ll_opy_ = bstack1ll11l11111_opy_ % json.dumps(arg)
            driver.execute_script(bstack1l1lll111ll_opy_)
            return
        instance = bstack1llll111ll1_opy_.bstack1lllll111ll_opy_(driver)
        if instance:
            if not bstack1llll111ll1_opy_.bstack1llll1lllll_opy_(instance, bstack1ll1l11l11l_opy_.bstack1ll111ll1ll_opy_, False):
                bstack1llll111ll1_opy_.bstack1lllll1111l_opy_(instance, bstack1ll1l11l11l_opy_.bstack1ll111ll1ll_opy_, True)
            else:
                self.logger.info(bstack11l1l_opy_ (u"ࠧࡶࡥࡳࡨࡲࡶࡲࡥࡳࡤࡣࡱ࠾ࠥࡧ࡬ࡳࡧࡤࡨࡾࠦࡩ࡯ࠢࡳࡶࡴ࡭ࡲࡦࡵࡶࠤ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟࡯ࡣࡰࡩࡂࢁࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡱࡥࡲ࡫ࡽࠡ࡯ࡨࡸ࡭ࡵࡤ࠾ࠤሴ") + str(method) + bstack11l1l_opy_ (u"ࠨࠢስ"))
                return
        self.logger.info(bstack11l1l_opy_ (u"ࠢࡱࡧࡵࡪࡴࡸ࡭ࡠࡵࡦࡥࡳࡀࠠࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡢࡲࡦࡳࡥ࠾ࡽࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࡤࡴࡡ࡮ࡧࢀࠤࡲ࡫ࡴࡩࡱࡧࡁࠧሶ") + str(method) + bstack11l1l_opy_ (u"ࠣࠤሷ"))
        if framework_name == bstack11l1l_opy_ (u"ࠩࡳࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹ࠭ሸ"):
            result = self.bstack1l1llllll1l_opy_.bstack1l1lll11lll_opy_(driver, bstack1ll11l11111_opy_)
        else:
            result = driver.execute_async_script(bstack1ll11l11111_opy_, {bstack11l1l_opy_ (u"ࠥࡱࡪࡺࡨࡰࡦࠥሹ"): method if method else bstack11l1l_opy_ (u"ࠦࠧሺ")})
        bstack1lll1ll1l11_opy_.end(EVENTS.bstack1l11l1l111_opy_.value, bstack1l1llllllll_opy_+bstack11l1l_opy_ (u"ࠧࡀࡳࡵࡣࡵࡸࠧሻ"), bstack1l1llllllll_opy_+bstack11l1l_opy_ (u"ࠨ࠺ࡦࡰࡧࠦሼ"), True, None, command=method)
        if instance:
            bstack1llll111ll1_opy_.bstack1lllll1111l_opy_(instance, bstack1ll1l11l11l_opy_.bstack1ll111ll1ll_opy_, False)
            instance.bstack11lll111_opy_(bstack11l1l_opy_ (u"ࠢࡢ࠳࠴ࡽ࠿ࡶࡥࡳࡨࡲࡶࡲࡥࡳࡤࡣࡱࠦሽ"), datetime.now() - bstack11ll1l1ll1_opy_)
        return result
        def bstack1ll111l1111_opy_(self, driver: object, framework_name, result_type: str):
            self.bstack1ll11111lll_opy_()
            req = structs.AccessibilityResultRequest()
            req.bin_session_id = self.bin_session_id
            req.bstack1ll11l111ll_opy_ = self.bstack1ll111111ll_opy_[bstack11l1l_opy_ (u"ࠣࡶࡨࡷࡹࡥࡲࡶࡰࡢࡹࡺ࡯ࡤࠣሾ")]
            req.result_type = result_type
            req.session_id = self.bin_session_id
            try:
                r = self.bstack1ll1ll11l11_opy_.AccessibilityResult(req)
                if not r.success:
                    self.logger.debug(bstack11l1l_opy_ (u"ࠤࡵࡩࡨ࡫ࡩࡷࡧࡧࠤ࡫ࡸ࡯࡮ࠢࡶࡩࡷࡼࡥࡳ࠼ࠣࠦሿ") + str(r) + bstack11l1l_opy_ (u"ࠥࠦቀ"))
                else:
                    bstack1ll1111ll1l_opy_ = json.loads(r.bstack1ll11l11l11_opy_.decode(bstack11l1l_opy_ (u"ࠫࡺࡺࡦ࠮࠺ࠪቁ")))
                    if result_type == bstack11l1l_opy_ (u"ࠬ࡭ࡥࡵࡔࡨࡷࡺࡲࡴࡴࠩቂ"):
                        return bstack1ll1111ll1l_opy_.get(bstack11l1l_opy_ (u"ࠨࡤࡢࡶࡤࠦቃ"), [])
                    else:
                        return bstack1ll1111ll1l_opy_.get(bstack11l1l_opy_ (u"ࠢࡥࡣࡷࡥࠧቄ"), {})
            except grpc.RpcError as e:
                self.logger.error(bstack11l1l_opy_ (u"ࠣࡴࡳࡧ࠲࡫ࡲࡳࡱࡵࠤࡼ࡮ࡩ࡭ࡧࠣࡪࡪࡺࡣࡩ࡫ࡱ࡫ࠥ࡭ࡥࡵࡡࡤࡴࡵࡥࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࡥࡲࡦࡵࡸࡰࡹࠦࡦࡳࡱࡰࠤࡨࡲࡩ࠻ࠢࠥቅ") + str(e) + bstack11l1l_opy_ (u"ࠤࠥቆ"))
    @measure(event_name=EVENTS.bstack1ll1l1l111_opy_, stage=STAGE.bstack1lll1l11l_opy_)
    def get_accessibility_results(self, driver: object, framework_name):
        if not self.accessibility:
            self.logger.debug(bstack11l1l_opy_ (u"ࠥ࡫ࡪࡺ࡟ࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿ࡟ࡳࡧࡶࡹࡱࡺࡳ࠻ࠢࡤ࠵࠶ࡿࠠ࡯ࡱࡷࠤࡪࡴࡡࡣ࡮ࡨࡨࠧቇ"))
            return
        if self.bstack1ll11l1l1l1_opy_:
            self.logger.debug(bstack11l1l_opy_ (u"ࠫࡕ࡫ࡲࡧࡱࡵࡱ࡮ࡴࡧࠡࡵࡦࡥࡳࠦࡦࡰࡴࠣࡥࡵࡶࠠࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠧቈ"))
            self.perform_scan(driver, method=None, framework_name=framework_name)
            return self.bstack1ll111l1111_opy_(driver, framework_name, bstack11l1l_opy_ (u"ࠧ࡭ࡥࡵࡔࡨࡷࡺࡲࡴࡴࠤ቉"))
        bstack1ll11l11111_opy_ = self.scripts.get(framework_name, {}).get(bstack11l1l_opy_ (u"ࠨࡧࡦࡶࡕࡩࡸࡻ࡬ࡵࡵࠥቊ"), None)
        if not bstack1ll11l11111_opy_:
            self.logger.debug(bstack11l1l_opy_ (u"ࠢ࡮࡫ࡶࡷ࡮ࡴࡧࠡࠩࡪࡩࡹࡘࡥࡴࡷ࡯ࡸࡸ࠭ࠠࡴࡥࡵ࡭ࡵࡺࠠࡧࡱࡵࠤ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟࡯ࡣࡰࡩࡂࠨቋ") + str(framework_name) + bstack11l1l_opy_ (u"ࠣࠤቌ"))
            return
        self.perform_scan(driver, method=None, framework_name=framework_name)
        bstack11ll1l1ll1_opy_ = datetime.now()
        if framework_name == bstack11l1l_opy_ (u"ࠩࡳࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹ࠭ቍ"):
            result = self.bstack1l1llllll1l_opy_.bstack1l1lll11lll_opy_(driver, bstack1ll11l11111_opy_)
        else:
            result = driver.execute_async_script(bstack1ll11l11111_opy_)
        instance = bstack1llll111ll1_opy_.bstack1lllll111ll_opy_(driver)
        if instance:
            instance.bstack11lll111_opy_(bstack11l1l_opy_ (u"ࠥࡥ࠶࠷ࡹ࠻ࡩࡨࡸࡤࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࡤࡸࡥࡴࡷ࡯ࡸࡸࠨ቎"), datetime.now() - bstack11ll1l1ll1_opy_)
        return result
    @measure(event_name=EVENTS.bstack1l1llll11_opy_, stage=STAGE.bstack1lll1l11l_opy_)
    def get_accessibility_results_summary(self, driver: object, framework_name):
        if not self.accessibility:
            self.logger.debug(bstack11l1l_opy_ (u"ࠦ࡬࡫ࡴࡠࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࡠࡴࡨࡷࡺࡲࡴࡴࡡࡶࡹࡲࡳࡡࡳࡻ࠽ࠤࡦ࠷࠱ࡺࠢࡱࡳࡹࠦࡥ࡯ࡣࡥࡰࡪࡪࠢ቏"))
            return
        if self.bstack1ll11l1l1l1_opy_:
            self.perform_scan(driver, method=None, framework_name=framework_name)
            return self.bstack1ll111l1111_opy_(driver, framework_name, bstack11l1l_opy_ (u"ࠬ࡭ࡥࡵࡔࡨࡷࡺࡲࡴࡴࡕࡸࡱࡲࡧࡲࡺࠩቐ"))
        bstack1ll11l11111_opy_ = self.scripts.get(framework_name, {}).get(bstack11l1l_opy_ (u"ࠨࡧࡦࡶࡕࡩࡸࡻ࡬ࡵࡵࡖࡹࡲࡳࡡࡳࡻࠥቑ"), None)
        if not bstack1ll11l11111_opy_:
            self.logger.debug(bstack11l1l_opy_ (u"ࠢ࡮࡫ࡶࡷ࡮ࡴࡧࠡࠩࡪࡩࡹࡘࡥࡴࡷ࡯ࡸࡸ࡙ࡵ࡮࡯ࡤࡶࡾ࠭ࠠࡴࡥࡵ࡭ࡵࡺࠠࡧࡱࡵࠤ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟࡯ࡣࡰࡩࡂࠨቒ") + str(framework_name) + bstack11l1l_opy_ (u"ࠣࠤቓ"))
            return
        self.perform_scan(driver, method=None, framework_name=framework_name)
        bstack11ll1l1ll1_opy_ = datetime.now()
        if framework_name == bstack11l1l_opy_ (u"ࠩࡳࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹ࠭ቔ"):
            result = self.bstack1l1llllll1l_opy_.bstack1l1lll11lll_opy_(driver, bstack1ll11l11111_opy_)
        else:
            result = driver.execute_async_script(bstack1ll11l11111_opy_)
        instance = bstack1llll111ll1_opy_.bstack1lllll111ll_opy_(driver)
        if instance:
            instance.bstack11lll111_opy_(bstack11l1l_opy_ (u"ࠥࡥ࠶࠷ࡹ࠻ࡩࡨࡸࡤࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࡤࡸࡥࡴࡷ࡯ࡸࡸࡥࡳࡶ࡯ࡰࡥࡷࡿࠢቕ"), datetime.now() - bstack11ll1l1ll1_opy_)
        return result
    @measure(event_name=EVENTS.bstack1ll1111l1ll_opy_, stage=STAGE.bstack1lll1l11l_opy_)
    def bstack1l1lll11ll1_opy_(
        self,
        platform_index: int,
        framework_name: str,
        framework_version: str,
        hub_url: str,
    ):
        self.bstack1ll11111lll_opy_()
        req = structs.AccessibilityConfigRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.framework_name = framework_name
        req.framework_version = framework_version
        req.hub_url = hub_url
        try:
            r = self.bstack1ll1ll11l11_opy_.AccessibilityConfig(req)
            if not r.success:
                self.logger.debug(bstack11l1l_opy_ (u"ࠦࡷ࡫ࡣࡦ࡫ࡹࡩࡩࠦࡦࡳࡱࡰࠤࡸ࡫ࡲࡷࡧࡵ࠾ࠥࠨቖ") + str(r) + bstack11l1l_opy_ (u"ࠧࠨ቗"))
            else:
                self.bstack1l1llll11ll_opy_(framework_name, r)
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack11l1l_opy_ (u"ࠨࡲࡱࡥ࠰ࡩࡷࡸ࡯ࡳ࠼ࠣࠦቘ") + str(e) + bstack11l1l_opy_ (u"ࠢࠣ቙"))
            traceback.print_exc()
            raise e
    def bstack1l1llll11ll_opy_(self, framework_name: str, result: structs.AccessibilityConfigResponse) -> bool:
        if not result.success or not result.accessibility.success:
            self.logger.debug(bstack11l1l_opy_ (u"ࠣ࡮ࡲࡥࡩࡥࡣࡰࡰࡩ࡭࡬ࡀࠠࡢ࠳࠴ࡽࠥࡴ࡯ࡵࠢࡩࡳࡺࡴࡤࠣቚ"))
            return False
        if result.accessibility.is_app_accessibility:
            self.bstack1ll11l1l1l1_opy_ = result.accessibility.is_app_accessibility
        if result.testhub.build_hashed_id:
            self.bstack1ll111111ll_opy_[bstack11l1l_opy_ (u"ࠤࡷࡩࡸࡺࡨࡶࡤࡢࡦࡺ࡯࡬ࡥࡡࡸࡹ࡮ࡪࠢቛ")] = result.testhub.build_hashed_id
        if result.testhub.jwt:
            self.bstack1ll111111ll_opy_[bstack11l1l_opy_ (u"ࠥࡸ࡭ࡥࡪࡸࡶࡢࡸࡴࡱࡥ࡯ࠤቜ")] = result.testhub.jwt
        if result.accessibility.options:
            options = result.accessibility.options
            if options.capabilities:
                for caps in options.capabilities:
                    self.bstack1ll111111ll_opy_[caps.name] = caps.value
            if options.scripts:
                self.scripts[framework_name] = {row.name: row.command for row in options.scripts}
            if options.commands_to_wrap and options.commands_to_wrap.commands:
                scripts_to_run = [s for s in options.commands_to_wrap.scripts_to_run]
                if not scripts_to_run:
                    return False
                bstack1ll111llll1_opy_ = dict()
                for command in options.commands_to_wrap.commands:
                    if command.library == self.bstack1ll11111ll1_opy_ and command.module == self.bstack1l1lll1llll_opy_:
                        if command.method and not command.method in bstack1ll111llll1_opy_:
                            bstack1ll111llll1_opy_[command.method] = dict()
                        if command.name and not command.name in bstack1ll111llll1_opy_[command.method]:
                            bstack1ll111llll1_opy_[command.method][command.name] = list()
                        bstack1ll111llll1_opy_[command.method][command.name].extend(scripts_to_run)
                self.commands[framework_name] = bstack1ll111llll1_opy_
        return bool(self.commands.get(framework_name, None))
    def bstack1ll11111l1l_opy_(
        self,
        f: bstack1lll11l111l_opy_,
        exec: Tuple[bstack1llll1ll1ll_opy_, str],
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if isinstance(self.bstack1l1llllll1l_opy_, bstack1lll11l11l1_opy_) and method_name != bstack11l1l_opy_ (u"ࠫࡨࡵ࡮࡯ࡧࡦࡸࠬቝ"):
            return
        if bstack1llll111ll1_opy_.bstack1lll1ll1l1l_opy_(instance, bstack1ll1l11l11l_opy_.bstack1l1lll1l11l_opy_):
            return
        if f.bstack1l1lll1ll1l_opy_(method_name, *args):
            bstack1l1llllll11_opy_ = False
            desired_capabilities = f.bstack1ll11l1l11l_opy_(instance)
            if isinstance(desired_capabilities, dict):
                hub_url = f.bstack1l1llll1111_opy_(instance)
                platform_index = f.bstack1llll1lllll_opy_(instance, bstack1lll11l111l_opy_.bstack1ll1111l111_opy_, 0)
                bstack1ll11111111_opy_ = datetime.now()
                r = self.bstack1l1lll11ll1_opy_(platform_index, f.framework_name, f.framework_version, hub_url)
                instance.bstack11lll111_opy_(bstack11l1l_opy_ (u"ࠧ࡭ࡲࡱࡥ࠽ࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࡢࡧࡴࡴࡦࡪࡩࠥ቞"), datetime.now() - bstack1ll11111111_opy_)
                bstack1l1llllll11_opy_ = r.success
            else:
                self.logger.error(bstack11l1l_opy_ (u"ࠨ࡭ࡪࡵࡶ࡭ࡳ࡭ࠠࡥࡧࡶ࡭ࡷ࡫ࡤࠡࡥࡤࡴࡦࡨࡩ࡭࡫ࡷ࡭ࡪࡹ࠽ࠣ቟") + str(desired_capabilities) + bstack11l1l_opy_ (u"ࠢࠣበ"))
            f.bstack1lllll1111l_opy_(instance, bstack1ll1l11l11l_opy_.bstack1l1lll1l11l_opy_, bstack1l1llllll11_opy_)
    def bstack1l11l11l_opy_(self, test_tags):
        bstack1l1lll11ll1_opy_ = self.config.get(bstack11l1l_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࡐࡲࡷ࡭ࡴࡴࡳࠨቡ"))
        if not bstack1l1lll11ll1_opy_:
            return True
        try:
            include_tags = bstack1l1lll11ll1_opy_[bstack11l1l_opy_ (u"ࠩ࡬ࡲࡨࡲࡵࡥࡧࡗࡥ࡬ࡹࡉ࡯ࡖࡨࡷࡹ࡯࡮ࡨࡕࡦࡳࡵ࡫ࠧቢ")] if bstack11l1l_opy_ (u"ࠪ࡭ࡳࡩ࡬ࡶࡦࡨࡘࡦ࡭ࡳࡊࡰࡗࡩࡸࡺࡩ࡯ࡩࡖࡧࡴࡶࡥࠨባ") in bstack1l1lll11ll1_opy_ and isinstance(bstack1l1lll11ll1_opy_[bstack11l1l_opy_ (u"ࠫ࡮ࡴࡣ࡭ࡷࡧࡩ࡙ࡧࡧࡴࡋࡱࡘࡪࡹࡴࡪࡰࡪࡗࡨࡵࡰࡦࠩቤ")], list) else []
            exclude_tags = bstack1l1lll11ll1_opy_[bstack11l1l_opy_ (u"ࠬ࡫ࡸࡤ࡮ࡸࡨࡪ࡚ࡡࡨࡵࡌࡲ࡙࡫ࡳࡵ࡫ࡱ࡫ࡘࡩ࡯ࡱࡧࠪብ")] if bstack11l1l_opy_ (u"࠭ࡥࡹࡥ࡯ࡹࡩ࡫ࡔࡢࡩࡶࡍࡳ࡚ࡥࡴࡶ࡬ࡲ࡬࡙ࡣࡰࡲࡨࠫቦ") in bstack1l1lll11ll1_opy_ and isinstance(bstack1l1lll11ll1_opy_[bstack11l1l_opy_ (u"ࠧࡦࡺࡦࡰࡺࡪࡥࡕࡣࡪࡷࡎࡴࡔࡦࡵࡷ࡭ࡳ࡭ࡓࡤࡱࡳࡩࠬቧ")], list) else []
            excluded = any(tag in exclude_tags for tag in test_tags)
            included = len(include_tags) == 0 or any(tag in include_tags for tag in test_tags)
            return not excluded and included
        except Exception as error:
            self.logger.debug(bstack11l1l_opy_ (u"ࠣࡇࡵࡶࡴࡸࠠࡸࡪ࡬ࡰࡪࠦࡶࡢ࡮࡬ࡨࡦࡺࡩ࡯ࡩࠣࡸࡪࡹࡴࠡࡥࡤࡷࡪࠦࡦࡰࡴࠣࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠣࡦࡪ࡬࡯ࡳࡧࠣࡷࡨࡧ࡮࡯࡫ࡱ࡫࠳ࠦࡅࡳࡴࡲࡶࠥࡀࠠࠣቨ") + str(error))
        return False
    def bstack11111ll11_opy_(self, caps):
        try:
            if self.bstack1ll11l1l1l1_opy_:
                bstack1ll1111ll11_opy_ = caps.get(bstack11l1l_opy_ (u"ࠤࡳࡰࡦࡺࡦࡰࡴࡰࡒࡦࡳࡥࠣቩ"))
                if bstack1ll1111ll11_opy_ is not None and str(bstack1ll1111ll11_opy_).lower() == bstack11l1l_opy_ (u"ࠥࡥࡳࡪࡲࡰ࡫ࡧࠦቪ"):
                    bstack1ll1111llll_opy_ = caps.get(bstack11l1l_opy_ (u"ࠦࡦࡶࡰࡪࡷࡰ࠾ࡵࡲࡡࡵࡨࡲࡶࡲ࡜ࡥࡳࡵ࡬ࡳࡳࠨቫ")) or caps.get(bstack11l1l_opy_ (u"ࠧࡶ࡬ࡢࡶࡩࡳࡷࡳࡖࡦࡴࡶ࡭ࡴࡴࠢቬ"))
                    if bstack1ll1111llll_opy_ is not None and int(bstack1ll1111llll_opy_) < 11:
                        self.logger.warning(bstack11l1l_opy_ (u"ࠨࡁࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࠦࡁࡶࡶࡲࡱࡦࡺࡩࡰࡰࠣࡻ࡮ࡲ࡬ࠡࡴࡸࡲࠥࡵ࡮࡭ࡻࠣࡳࡳࠦࡁ࡯ࡦࡵࡳ࡮ࡪࠠ࠲࠳ࠣࡥࡳࡪࠠࡢࡤࡲࡺࡪ࠴ࠠࡄࡷࡵࡶࡪࡴࡴࠡࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࠣࡺࡪࡸࡳࡪࡱࡱࠤࡂࠨቭ") + str(bstack1ll1111llll_opy_) + bstack11l1l_opy_ (u"ࠢࠣቮ"))
                        return False
                return True
            bstack1l1llll1l1l_opy_ = caps.get(bstack11l1l_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫࠻ࡱࡳࡸ࡮ࡵ࡮ࡴࠩቯ"), {}).get(bstack11l1l_opy_ (u"ࠩࡧࡩࡻ࡯ࡣࡦࡐࡤࡱࡪ࠭ተ"), caps.get(bstack11l1l_opy_ (u"ࠪࡨࡪࡼࡩࡤࡧࠪቱ"), bstack11l1l_opy_ (u"ࠫࠬቲ")))
            if bstack1l1llll1l1l_opy_:
                self.logger.warning(bstack11l1l_opy_ (u"ࠧࡇࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡇࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࠢࡺ࡭ࡱࡲࠠࡳࡷࡱࠤࡴࡴ࡬ࡺࠢࡲࡲࠥࡊࡥࡴ࡭ࡷࡳࡵࠦࡢࡳࡱࡺࡷࡪࡸࡳ࠯ࠤታ"))
                return False
            browser = caps.get(bstack11l1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡎࡢ࡯ࡨࠫቴ"), bstack11l1l_opy_ (u"ࠧࠨት")).lower()
            if browser != bstack11l1l_opy_ (u"ࠨࡥ࡫ࡶࡴࡳࡥࠨቶ"):
                self.logger.warning(bstack11l1l_opy_ (u"ࠤࡄࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠢࡄࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳࠦࡷࡪ࡮࡯ࠤࡷࡻ࡮ࠡࡱࡱࡰࡾࠦ࡯࡯ࠢࡆ࡬ࡷࡵ࡭ࡦࠢࡥࡶࡴࡽࡳࡦࡴࡶ࠲ࠧቷ"))
                return False
            bstack1l1lll1l111_opy_ = bstack1ll11l111l1_opy_
            if not self.config.get(bstack11l1l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡃࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࠬቸ")) or self.config.get(bstack11l1l_opy_ (u"ࠫࡹࡻࡲࡣࡱࡶࡧࡦࡲࡥࠨቹ")):
                bstack1l1lll1l111_opy_ = bstack1l1lll11l1l_opy_
            browser_version = caps.get(bstack11l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡜ࡥࡳࡵ࡬ࡳࡳ࠭ቺ"))
            if not browser_version:
                browser_version = caps.get(bstack11l1l_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡀ࡯ࡱࡶ࡬ࡳࡳࡹࠧቻ"), {}).get(bstack11l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡗࡧࡵࡷ࡮ࡵ࡮ࠨቼ"), bstack11l1l_opy_ (u"ࠨࠩች"))
            bstack1ll111l1ll1_opy_ = str(browser_version).lower() if browser_version is not None else bstack11l1l_opy_ (u"ࠩࠪቾ")
            if bstack1ll111l1ll1_opy_:
                if bstack1ll111l1ll1_opy_.startswith(bstack11l1l_opy_ (u"ࠪࡰࡦࡺࡥࡴࡶࠪቿ")):
                    if bstack1ll111l1ll1_opy_.startswith(bstack11l1l_opy_ (u"ࠫࡱࡧࡴࡦࡵࡷ࠱ࠬኀ")):
                        bstack1ll11l11ll1_opy_ = bstack1ll111l1ll1_opy_[len(bstack11l1l_opy_ (u"ࠬࡲࡡࡵࡧࡶࡸ࠲࠭ኁ")):]
                        if bstack1ll11l11ll1_opy_ and not bstack1ll11l11ll1_opy_.isdigit():
                            self.logger.warning(bstack11l1l_opy_ (u"ࠨࡉ࡯ࡸࡤࡰ࡮ࡪࠠࡣࡴࡲࡻࡸ࡫ࡲࠡࡸࡨࡶࡸ࡯࡯࡯ࠢࡩࡳࡷࡳࡡࡵࠢࠪࠦኂ") + str(browser_version) + bstack11l1l_opy_ (u"ࠢࠨ࠽ࠣࡩࡽࡶࡥࡤࡶࡨࡨࠥ࠭࡬ࡢࡶࡨࡷࡹ࠭ࠠࡰࡴࠣࠫࡱࡧࡴࡦࡵࡷ࠱ࡁࡴࡵ࡮ࡤࡨࡶࡃ࠭࠮ࠣኃ"))
                            return False
                else:
                    try:
                        if int(bstack1ll111l1ll1_opy_.split(bstack11l1l_opy_ (u"ࠨ࠰ࠪኄ"))[0]) <= bstack1l1lll1l111_opy_:
                            self.logger.warning(bstack11l1l_opy_ (u"ࠤࡄࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠢࡄࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳࠦࡷࡪ࡮࡯ࠤࡷࡻ࡮ࠡࡱࡱࡰࡾࠦ࡯࡯ࠢࡆ࡬ࡷࡵ࡭ࡦࠢࡥࡶࡴࡽࡳࡦࡴࠣࡺࡪࡸࡳࡪࡱࡱࠤ࡬ࡸࡥࡢࡶࡨࡶࠥࡺࡨࡢࡰࠣࠦኅ") + str(bstack1l1lll1l111_opy_) + bstack11l1l_opy_ (u"ࠥ࠲ࠧኆ"))
                            return False
                    except (ValueError, IndexError) as e:
                        self.logger.debug(bstack11l1l_opy_ (u"࡚ࠦࡴࡡࡣ࡮ࡨࠤࡹࡵࠠࡱࡣࡵࡷࡪࠦࡢࡳࡱࡺࡷࡪࡸࠠࡷࡧࡵࡷ࡮ࡵ࡮ࠡࠩࡾࡦࡷࡵࡷࡴࡧࡵࡣࡻ࡫ࡲࡴ࡫ࡲࡲࢂ࠭࠺ࠡࠤኇ") + str(e) + bstack11l1l_opy_ (u"ࠧࠨኈ"))
            bstack1ll111lll11_opy_ = caps.get(bstack11l1l_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡀ࡯ࡱࡶ࡬ࡳࡳࡹࠧ኉"), {}).get(bstack11l1l_opy_ (u"ࠧࡤࡪࡵࡳࡲ࡫ࡏࡱࡶ࡬ࡳࡳࡹࠧኊ"))
            if not bstack1ll111lll11_opy_:
                bstack1ll111lll11_opy_ = caps.get(bstack11l1l_opy_ (u"ࠨࡩࡲࡳ࡬ࡀࡣࡩࡴࡲࡱࡪࡕࡰࡵ࡫ࡲࡲࡸ࠭ኋ"), {})
            if bstack1ll111lll11_opy_ and bstack11l1l_opy_ (u"ࠩ࠰࠱࡭࡫ࡡࡥ࡮ࡨࡷࡸ࠭ኌ") in bstack1ll111lll11_opy_.get(bstack11l1l_opy_ (u"ࠪࡥࡷ࡭ࡳࠨኍ"), []):
                self.logger.warning(bstack11l1l_opy_ (u"ࠦࡆࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠤࡆࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠡࡹ࡬ࡰࡱࠦ࡮ࡰࡶࠣࡶࡺࡴࠠࡰࡰࠣࡰࡪ࡭ࡡࡤࡻࠣ࡬ࡪࡧࡤ࡭ࡧࡶࡷࠥࡳ࡯ࡥࡧ࠱ࠤࡘࡽࡩࡵࡥ࡫ࠤࡹࡵࠠ࡯ࡧࡺࠤ࡭࡫ࡡࡥ࡮ࡨࡷࡸࠦ࡭ࡰࡦࡨࠤࡴࡸࠠࡢࡸࡲ࡭ࡩࠦࡵࡴ࡫ࡱ࡫ࠥ࡮ࡥࡢࡦ࡯ࡩࡸࡹࠠ࡮ࡱࡧࡩ࠳ࠨ኎"))
                return False
            return True
        except Exception as error:
            self.logger.debug(bstack11l1l_opy_ (u"ࠧࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡ࡫ࡱࠤࡻࡧ࡬ࡪࡦࡤࡸࡪࠦࡡ࠲࠳ࡼࠤࡸࡻࡰࡱࡱࡵࡸࠥࡀࠢ኏") + str(error))
            return False
    def bstack1l1lllll11l_opy_(self, test_uuid: str, result: structs.FetchDriverExecuteParamsEventResponse):
        bstack1l1lllll1ll_opy_ = {
            bstack11l1l_opy_ (u"࠭ࡴࡩࡖࡨࡷࡹࡘࡵ࡯ࡗࡸ࡭ࡩ࠭ነ"): test_uuid,
        }
        bstack1ll111lllll_opy_ = {}
        if result.success:
            bstack1ll111lllll_opy_ = json.loads(result.accessibility_execute_params)
        return bstack1l1llll111l_opy_(bstack1l1lllll1ll_opy_, bstack1ll111lllll_opy_)
    def bstack1ll111l11ll_opy_(self, script_name: str, test_uuid: str) -> dict:
        bstack11l1l_opy_ (u"ࠢࠣࠤࠍࠤࠥࠦࠠࠡࠢࠣࠤࡋ࡫ࡴࡤࡪࠣࡧࡪࡴࡴࡳࡣ࡯ࠤࡦࡻࡴࡩࠢࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠢࡦࡳࡳ࡬ࡩࡨࡷࡵࡥࡹ࡯࡯࡯ࠢࡩࡳࡷࠦࡴࡩࡧࠣ࡫࡮ࡼࡥ࡯ࠢࡶࡧࡷ࡯ࡰࡵࠢࡱࡥࡲ࡫࠮ࠋࠢࠣࠤࠥࠦࠠࠡࠢࡕࡩࡹࡻࡲ࡯ࡵࠣࡧࡦࡩࡨࡦࡦࠣࡧࡴࡴࡦࡪࡩࠣ࡭࡫ࠦࡡ࡭ࡴࡨࡥࡩࡿࠠࡧࡧࡷࡧ࡭࡫ࡤ࠭ࠢࡲࡸ࡭࡫ࡲࡸ࡫ࡶࡩࠥࡲ࡯ࡢࡦࡶࠤࡦࡴࡤࠡࡥࡤࡧ࡭࡫ࡳࠡ࡫ࡷ࠲ࠏࠦࠠࠡࠢࠣࠤࠥࠦࡁࡳࡩࡶ࠾ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࡷࡨࡸࡩࡱࡶࡢࡲࡦࡳࡥ࠻ࠢࡑࡥࡲ࡫ࠠࡰࡨࠣࡸ࡭࡫ࠠࡴࡥࡵ࡭ࡵࡺࠠࡵࡱࠣࡪࡪࡺࡣࡩࠢࡦࡳࡳ࡬ࡩࡨࠢࡩࡳࡷࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࡹ࡫ࡳࡵࡡࡸࡹ࡮ࡪ࠺ࠡࡗࡘࡍࡉࠦ࡯ࡧࠢࡷ࡬ࡪࠦࡴࡦࡵࡷࠤࡷࡻ࡮ࠡࡨࡲࡶࠥࡽࡨࡪࡥ࡫ࠤࡹࡵࠠࡧࡧࡷࡧ࡭ࠦࡣࡰࡰࡩ࡭࡬ࠐࠠࠡࠢࠣࠤࠥࠦࠠࡓࡧࡷࡹࡷࡴࡳ࠻ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࡥ࡫ࡦࡸ࠿ࠦࡃࡰࡰࡩ࡭࡬ࡻࡲࡢࡶ࡬ࡳࡳࠦࡤࡪࡥࡷ࡭ࡴࡴࡡࡳࡻ࠯ࠤࡪࡳࡰࡵࡻࠣࡨ࡮ࡩࡴࠡ࡫ࡩࠤࡪࡸࡲࡰࡴࠣࡳࡨࡩࡵࡳࡵࠍࠤࠥࠦࠠࠡࠢࠣࠤࠧࠨࠢኑ")
        try:
            if self.bstack1ll1111111l_opy_:
                return self.bstack1ll111ll11l_opy_
            self.bstack1ll11111lll_opy_()
            req = structs.FetchDriverExecuteParamsEventRequest()
            req.bin_session_id = self.bin_session_id
            req.product = bstack11l1l_opy_ (u"ࠣࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠣኒ")
            req.script_name = script_name
            r = self.bstack1ll1ll11l11_opy_.FetchDriverExecuteParamsEvent(req)
            if r.success:
                self.bstack1ll111ll11l_opy_ = self.bstack1l1lllll11l_opy_(test_uuid, r)
                self.bstack1ll1111111l_opy_ = True
            else:
                self.logger.error(bstack11l1l_opy_ (u"ࠤࡩࡩࡹࡩࡨࡄࡧࡱࡸࡷࡧ࡬ࡂࡷࡷ࡬ࡆ࠷࠱ࡺࡅࡲࡲ࡫࡯ࡧ࠻ࠢࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥ࡬ࡥࡵࡥ࡫ࠤࡩࡸࡩࡷࡧࡵࠤࡪࡾࡥࡤࡷࡷࡩࠥࡶࡡࡳࡣࡰࡷࠥ࡬࡯ࡳࠢࡾࡷࡨࡸࡩࡱࡶࡢࡲࡦࡳࡥࡾ࠼ࠣࠦና") + str(r.error) + bstack11l1l_opy_ (u"ࠥࠦኔ"))
                self.bstack1ll111ll11l_opy_ = dict()
            return self.bstack1ll111ll11l_opy_
        except Exception as e:
            self.logger.error(bstack11l1l_opy_ (u"ࠦ࡫࡫ࡴࡤࡪࡆࡩࡳࡺࡲࡢ࡮ࡄࡹࡹ࡮ࡁ࠲࠳ࡼࡇࡴࡴࡦࡪࡩ࠽ࠤࡋࡧࡩ࡭ࡧࡧࠤࡹࡵࠠࡧࡧࡷࡧ࡭ࠦࡤࡳ࡫ࡹࡩࡷࠦࡥࡹࡧࡦࡹࡹ࡫ࠠࡱࡣࡵࡥࡲࡹࠠࡧࡱࡵࠤࢀࡹࡣࡳ࡫ࡳࡸࡤࡴࡡ࡮ࡧࢀ࠾ࠥࠨን") + str(traceback.format_exc()) + bstack11l1l_opy_ (u"ࠧࠨኖ"))
            return dict()
    def bstack111ll1l1_opy_(self, driver: object, name: str, framework_name: str, test_uuid: str):
        bstack1l1llllllll_opy_ = None
        try:
            self.bstack1ll11111lll_opy_()
            req = structs.FetchDriverExecuteParamsEventRequest()
            req.bin_session_id = self.bin_session_id
            req.product = bstack11l1l_opy_ (u"ࠨࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࠨኗ")
            req.script_name = bstack11l1l_opy_ (u"ࠢࡴࡣࡹࡩࡗ࡫ࡳࡶ࡮ࡷࡷࠧኘ")
            r = self.bstack1ll1ll11l11_opy_.FetchDriverExecuteParamsEvent(req)
            if not r.success:
                self.logger.debug(bstack11l1l_opy_ (u"ࠣࡴࡨࡧࡪ࡯ࡶࡦࡦࠣࡨࡷ࡯ࡶࡦࡴࠣࡩࡽ࡫ࡣࡶࡶࡨࠤࡵࡧࡲࡢ࡯ࡶࠤ࡫ࡸ࡯࡮ࠢࡶࡩࡷࡼࡥࡳ࠼ࠣࠦኙ") + str(r.error) + bstack11l1l_opy_ (u"ࠤࠥኚ"))
            else:
                bstack1l1lllll1ll_opy_ = self.bstack1l1lllll11l_opy_(test_uuid, r)
                bstack1ll11l11111_opy_ = r.script
            self.logger.debug(bstack11l1l_opy_ (u"ࠪࡔࡪࡸࡦࡰࡴࡰ࡭ࡳ࡭ࠠࡴࡥࡤࡲࠥࡨࡥࡧࡱࡵࡩࠥࡹࡡࡷ࡫ࡱ࡫ࠥࡸࡥࡴࡷ࡯ࡸࡸ࠭ኛ") + str(bstack1l1lllll1ll_opy_))
            self.perform_scan(driver, name, framework_name=framework_name)
            if not bstack1ll11l11111_opy_:
                self.logger.debug(bstack11l1l_opy_ (u"ࠦࡵ࡫ࡲࡧࡱࡵࡱࡤࡹࡣࡢࡰ࠽ࠤࡲ࡯ࡳࡴ࡫ࡱ࡫ࠥ࠭ࡳࡢࡸࡨࡖࡪࡹࡵ࡭ࡶࡶࠫࠥࡹࡣࡳ࡫ࡳࡸࠥ࡬࡯ࡳࠢࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࡤࡴࡡ࡮ࡧࡀࠦኜ") + str(framework_name) + bstack11l1l_opy_ (u"ࠧࠦࠢኝ"))
                return
            bstack1l1llllllll_opy_ = bstack1lll1ll1l11_opy_.bstack1ll11l1l111_opy_(EVENTS.bstack1ll11l11lll_opy_.value)
            self.bstack1ll1111lll1_opy_(driver, bstack1ll11l11111_opy_, bstack1l1lllll1ll_opy_, framework_name)
            try:
                bstack1ll1111l1l1_opy_ = {
                    bstack11l1l_opy_ (u"ࠨࡲࡦࡳࡸࡩࡸࡺࠢኞ"): {
                        bstack11l1l_opy_ (u"ࠢࡤࡱࡰࡱࡦࡴࡤࠣኟ"): bstack11l1l_opy_ (u"ࠣࡃ࠴࠵࡞ࡥࡓࡂࡘࡈࡣࡗࡋࡓࡖࡎࡗࡗࠧአ"),
                    },
                    bstack11l1l_opy_ (u"ࠤࡵࡩࡸࡶ࡯࡯ࡵࡨࠦኡ"): {
                        bstack11l1l_opy_ (u"ࠥࡦࡴࡪࡹࠣኢ"): {
                            bstack11l1l_opy_ (u"ࠦࡲࡹࡧࠣኣ"): bstack11l1l_opy_ (u"ࠧࡇࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡺࡥࡴࡶ࡬ࡲ࡬ࠦࡦࡰࡴࠣࡸ࡭࡯ࡳࠡࡶࡨࡷࡹࠦࡣࡢࡵࡨࠤ࡭ࡧࡳࠡࡧࡱࡨࡪࡪ࠮ࠣኤ"),
                            bstack11l1l_opy_ (u"ࠨࡳࡶࡥࡦࡩࡸࡹࠢእ"): True
                        }
                    }
                }
                self.bstack1ll11l1ll_opy_.info(json.dumps(bstack1ll1111l1l1_opy_, separators=(bstack11l1l_opy_ (u"ࠧ࠭ࠩኦ"), bstack11l1l_opy_ (u"ࠨ࠼ࠪኧ"))))
            except Exception as bstack1l1l1ll1l1_opy_:
                self.logger.debug(bstack11l1l_opy_ (u"ࠤࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥࡲ࡯ࡨࠢࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠢࡶࡥࡻ࡫ࠠࡳࡧࡶࡹࡱࡺࡳࠡࡦࡤࡸࡦࡀࠠࠣከ") + str(bstack1l1l1ll1l1_opy_) + bstack11l1l_opy_ (u"ࠥࠦኩ"))
            self.logger.info(bstack11l1l_opy_ (u"ࠦࡆࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠤࡹ࡫ࡳࡵ࡫ࡱ࡫ࠥ࡬࡯ࡳࠢࡷ࡬࡮ࡹࠠࡵࡧࡶࡸࠥࡩࡡࡴࡧࠣ࡬ࡦࡹࠠࡦࡰࡧࡩࡩ࠴ࠢኪ"))
            bstack1lll1ll1l11_opy_.end(EVENTS.bstack1ll11l11lll_opy_.value, bstack1l1llllllll_opy_+bstack11l1l_opy_ (u"ࠧࡀࡳࡵࡣࡵࡸࠧካ"), bstack1l1llllllll_opy_+bstack11l1l_opy_ (u"ࠨ࠺ࡦࡰࡧࠦኬ"), True, None, command=bstack11l1l_opy_ (u"ࠧࡴࡣࡹࡩࡗ࡫ࡳࡶ࡮ࡷࡷࠬክ"),test_name=name)
        except Exception as bstack1l1lll1l1l1_opy_:
            self.logger.error(bstack11l1l_opy_ (u"ࠣࡃࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠡࡴࡨࡷࡺࡲࡴࡴࠢࡦࡳࡺࡲࡤࠡࡰࡲࡸࠥࡨࡥࠡࡲࡵࡳࡨ࡫ࡳࡴࡧࡧࠤ࡫ࡵࡲࠡࡶ࡫ࡩࠥࡺࡥࡴࡶࠣࡧࡦࡹࡥ࠻ࠢࠥኮ") + bstack11l1l_opy_ (u"ࠤࡶࡸࡷ࠮ࡰࡢࡶ࡫࠭ࠧኯ") + bstack11l1l_opy_ (u"ࠥࠤࡊࡸࡲࡰࡴࠣ࠾ࠧኰ") + str(bstack1l1lll1l1l1_opy_))
            bstack1lll1ll1l11_opy_.end(EVENTS.bstack1ll11l11lll_opy_.value, bstack1l1llllllll_opy_+bstack11l1l_opy_ (u"ࠦ࠿ࡹࡴࡢࡴࡷࠦ኱"), bstack1l1llllllll_opy_+bstack11l1l_opy_ (u"ࠧࡀࡥ࡯ࡦࠥኲ"), False, bstack1l1lll1l1l1_opy_, command=bstack11l1l_opy_ (u"࠭ࡳࡢࡸࡨࡖࡪࡹࡵ࡭ࡶࡶࠫኳ"),test_name=name)
    def bstack1ll1111lll1_opy_(self, driver, bstack1ll11l11111_opy_, bstack1l1lllll1ll_opy_, framework_name):
        if framework_name == bstack11l1l_opy_ (u"ࠧࡱ࡮ࡤࡽࡼࡸࡩࡨࡪࡷࠫኴ"):
            self.bstack1l1llllll1l_opy_.bstack1l1lll11lll_opy_(driver, bstack1ll11l11111_opy_, bstack1l1lllll1ll_opy_)
        else:
            self.logger.debug(driver.execute_async_script(bstack1ll11l11111_opy_, bstack1l1lllll1ll_opy_))
    def _1l1lll1lll1_opy_(self, instance: bstack1ll1ll11lll_opy_, args: Tuple) -> list:
        bstack11l1l_opy_ (u"ࠣࠤࠥࡉࡽࡺࡲࡢࡥࡷࠤࡹࡧࡧࡴࠢࡥࡥࡸ࡫ࡤࠡࡱࡱࠤࡹ࡮ࡥࠡࡶࡨࡷࡹࠦࡦࡳࡣࡰࡩࡼࡵࡲ࡬࠰ࠥࠦࠧኵ")
        if bstack11l1l_opy_ (u"ࠩࡳࡽࡹ࡫ࡳࡵ࠯ࡥࡨࡩ࠭኶") in instance.bstack1l1llll1lll_opy_:
            return args[2].tags if hasattr(args[2], bstack11l1l_opy_ (u"ࠪࡸࡦ࡭ࡳࠨ኷")) else []
        if hasattr(args[0], bstack11l1l_opy_ (u"ࠫࡴࡽ࡮ࡠ࡯ࡤࡶࡰ࡫ࡲࡴࠩኸ")):
            return [marker.name for marker in args[0].own_markers]
        return []
    def bstack1l1lll11l11_opy_(self, tags, capabilities):
        return self.bstack1l11l11l_opy_(tags) and self.bstack11111ll11_opy_(capabilities)