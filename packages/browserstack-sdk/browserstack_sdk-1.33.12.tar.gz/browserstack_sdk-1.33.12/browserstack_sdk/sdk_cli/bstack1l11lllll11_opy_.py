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
from datetime import datetime
import os
import threading
from browserstack_sdk.sdk_cli.bstack1ll11l1l1l1_opy_ import (
    bstack1ll11lllll1_opy_,
    bstack1ll11lll1ll_opy_,
    bstack1ll1l1111l1_opy_,
    bstack1ll1l1ll1l1_opy_,
)
from browserstack_sdk.sdk_cli.bstack1ll11l1lll1_opy_ import bstack1ll11ll1lll_opy_
from browserstack_sdk.sdk_cli.test_framework import TestFramework, bstack1llll1ll111_opy_, bstack1lll1111l11_opy_, bstack1lll1l11l11_opy_
from typing import Tuple, Dict, Any, List, Union
from browserstack_sdk import sdk_pb2 as structs
from browserstack_sdk.sdk_cli.bstack1l1ll111111_opy_ import bstack1l1l1l111ll_opy_
from browserstack_sdk.sdk_cli.bstack1ll1111ll1l_opy_ import bstack1ll111ll1l1_opy_
from browserstack_sdk.sdk_cli.bstack1l1ll1111ll_opy_ import bstack1l1l1l1111l_opy_
from browserstack_sdk.sdk_cli.bstack1ll11l111ll_opy_ import bstack1ll11l11l1l_opy_
from bstack_utils.helper import bstack1l11l11l1l1_opy_
from bstack_utils.measure import measure
from bstack_utils.constants import *
from bstack_utils.bstack11l11l11ll_opy_ import bstack1lll111111l_opy_
from bstack_utils import bstack111lll1l1_opy_
import grpc
import traceback
import json
class bstack1l1l11111ll_opy_(bstack1l1l1l111ll_opy_):
    bstack1l11ll111l1_opy_ = False
    bstack1l11l11ll11_opy_ = bstack11ll1_opy_ (u"ࠧࡹࡥ࡭ࡧࡱ࡭ࡺࡳ࠮ࡸࡧࡥࡨࡷ࡯ࡶࡦࡴࠥᏘ")
    bstack1l111ll1l11_opy_ = bstack11ll1_opy_ (u"ࠨࡲࡦ࡯ࡲࡸࡪ࠴ࡷࡦࡤࡧࡶ࡮ࡼࡥࡳࠤᏙ")
    bstack1l11l11llll_opy_ = bstack11ll1_opy_ (u"ࠢࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿ࡟ࡪࡰ࡬ࡸࠧᏚ")
    bstack1l11l1111ll_opy_ = bstack11ll1_opy_ (u"ࠣࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࡠ࡫ࡶࡣࡸࡩࡡ࡯ࡰ࡬ࡲ࡬ࠨᏛ")
    bstack1l11l1llll1_opy_ = bstack11ll1_opy_ (u"ࠤࡧࡶ࡮ࡼࡥࡳࡡ࡫ࡥࡸࡥࡵࡳ࡮ࠥᏜ")
    scripts: Dict[str, Dict[str, str]]
    commands: Dict[str, Dict[str, Dict[str, List[str]]]]
    def __init__(self, bstack1l1l11l11ll_opy_, bstack1l1l1l1l1l1_opy_):
        super().__init__()
        self.scripts = dict()
        self.commands = dict()
        self.accessibility = False
        self.bstack1l11ll111ll_opy_ = False
        self.bstack1l11l1ll111_opy_ = dict()
        self.bstack11ll111l1l_opy_ = bstack111lll1l1_opy_.bstack1l1l111l_opy_(__name__)
        self.bstack1l111llll11_opy_ = False
        self.bstack1l11ll1111l_opy_ = dict()
        if not self.is_enabled():
            return
        self.bstack1l11l111ll1_opy_ = bstack1l1l1l1l1l1_opy_
        bstack1l1l11l11ll_opy_.bstack1ll1l11111l_opy_((bstack1ll11lllll1_opy_.bstack1ll11l1l1ll_opy_, bstack1ll11lll1ll_opy_.PRE), self.bstack1l111llllll_opy_)
        TestFramework.bstack1ll1l11111l_opy_((bstack1llll1ll111_opy_.TEST, bstack1lll1111l11_opy_.PRE), self.bstack1ll11l11111_opy_)
        TestFramework.bstack1ll1l11111l_opy_((bstack1llll1ll111_opy_.TEST, bstack1lll1111l11_opy_.POST), self.bstack1l1llllll1l_opy_)
    def is_enabled(self) -> bool:
        return True
    def bstack1ll11l11111_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll1l11l11_opy_,
        bstack1lll1lll111_opy_: Tuple[bstack1llll1ll111_opy_, bstack1lll1111l11_opy_],
        *args,
        **kwargs,
    ):
        tags = self._1l11l11lll1_opy_(instance, args)
        test_framework = f.bstack1ll1llll11l_opy_(instance, TestFramework.bstack1lll1111111_opy_)
        if self.bstack1l11ll111ll_opy_:
            self.bstack1l11l1ll111_opy_[bstack11ll1_opy_ (u"ࠥࡸࡪࡹࡴࡠࡴࡸࡲࡤࡻࡵࡪࡦࠥᏝ")] = f.bstack1ll1llll11l_opy_(instance, TestFramework.bstack1llll111ll1_opy_)
        if bstack11ll1_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷ࠱ࡧࡪࡤࠨᏞ") in instance.bstack1ll1ll1llll_opy_:
            platform_index = f.bstack1ll1llll11l_opy_(instance, TestFramework.bstack1lll11l1l1l_opy_)
            self.accessibility = self.bstack1l11l1l111l_opy_(tags, self.config[bstack11ll1_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨᏟ")][platform_index])
        else:
            capabilities = self.bstack1l11l111ll1_opy_.bstack1ll111lll11_opy_(f, instance, bstack1lll1lll111_opy_, *args, **kwargs)
            if not capabilities:
                self.logger.debug(bstack11ll1_opy_ (u"ࠨ࡯࡯ࡡࡥࡩ࡫ࡵࡲࡦࡡࡷࡩࡸࡺ࠺ࠡࡰࡲࠤࡨࡧࡰࡢࡤ࡬ࡰ࡮ࡺࡩࡦࡵࠣࡪࡴࡻ࡮ࡥࠢࡩࡳࡷࠦࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰ࠿ࡾ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࢃࠠࡢࡴࡪࡷࡂࢁࡡࡳࡩࡶࢁࠥࡱࡷࡢࡴࡪࡷࡂࠨᏠ") + str(kwargs) + bstack11ll1_opy_ (u"ࠢࠣᏡ"))
                return
            self.accessibility = self.bstack1l11l1l111l_opy_(tags, capabilities)
        if self.bstack1l11l111ll1_opy_.pages and self.bstack1l11l111ll1_opy_.pages.values():
            bstack1l11l1l1l1l_opy_ = list(self.bstack1l11l111ll1_opy_.pages.values())
            if bstack1l11l1l1l1l_opy_ and isinstance(bstack1l11l1l1l1l_opy_[0], (list, tuple)) and bstack1l11l1l1l1l_opy_[0]:
                bstack1l111ll11ll_opy_ = bstack1l11l1l1l1l_opy_[0][0]
                if callable(bstack1l111ll11ll_opy_):
                    page = bstack1l111ll11ll_opy_()
                    def bstack1l11lll1l_opy_():
                        self.get_accessibility_results(page, bstack11ll1_opy_ (u"ࠣࡲ࡯ࡥࡾࡽࡲࡪࡩ࡫ࡸࠧᏢ"))
                    def bstack1l11l1l1ll1_opy_():
                        self.get_accessibility_results_summary(page, bstack11ll1_opy_ (u"ࠤࡳࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹࠨᏣ"))
                    setattr(page, bstack11ll1_opy_ (u"ࠥ࡫ࡪࡺࡁࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࡘࡥࡴࡷ࡯ࡸࡸࠨᏤ"), bstack1l11lll1l_opy_)
                    setattr(page, bstack11ll1_opy_ (u"ࠦ࡬࡫ࡴࡂࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࡒࡦࡵࡸࡰࡹ࡙ࡵ࡮࡯ࡤࡶࡾࠨᏥ"), bstack1l11l1l1ll1_opy_)
        self.logger.debug(bstack11ll1_opy_ (u"ࠧࡹࡨࡰࡷ࡯ࡨࠥࡸࡵ࡯ࠢࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠢࡹࡥࡱࡻࡥ࠾ࠤᏦ") + str(self.accessibility) + bstack11ll1_opy_ (u"ࠨࠢᏧ"))
    def bstack1l111llllll_opy_(
        self,
        f: bstack1ll11ll1lll_opy_,
        driver: object,
        exec: Tuple[bstack1ll1l1ll1l1_opy_, str],
        bstack1lll1lll111_opy_: Tuple[bstack1ll11lllll1_opy_, bstack1ll11lll1ll_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        try:
            bstack1ll11l1l1l_opy_ = datetime.now()
            self.bstack1l11l11l111_opy_(f, exec, *args, **kwargs)
            instance, method_name = exec
            instance.bstack1lll1lll1_opy_(bstack11ll1_opy_ (u"ࠢࡢ࠳࠴ࡽ࠿࡯࡮ࡪࡶࡢࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࡢࡧࡴࡴࡦࡪࡩࠥᏨ"), datetime.now() - bstack1ll11l1l1l_opy_)
            if (
                not f.bstack1ll1l1ll1ll_opy_(method_name)
                or f.bstack1ll1l111111_opy_(method_name, *args)
                or f.bstack1ll11lll111_opy_(method_name, *args)
            ):
                return
            if not f.bstack1ll1llll11l_opy_(instance, bstack1l1l11111ll_opy_.bstack1l11l11llll_opy_, False):
                if not bstack1l1l11111ll_opy_.bstack1l11ll111l1_opy_:
                    self.logger.warning(bstack11ll1_opy_ (u"ࠣ࡝ࡳࡰࡦࡺࡦࡰࡴࡰࡣ࡮ࡴࡤࡦࡺࡀࠦᏩ") + str(f.platform_index) + bstack11ll1_opy_ (u"ࠤࡠࠤࡦ࠷࠱ࡺࠢࡦࡥࡵࡧࡢࡪ࡮࡬ࡸ࡮࡫ࡳࠡࡪࡤࡺࡪࠦ࡮ࡰࡶࠣࡦࡪ࡫࡮ࠡࡵࡨࡸࠥ࡬࡯ࡳࠢࡷ࡬࡮ࡹࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠣᏪ"))
                    bstack1l1l11111ll_opy_.bstack1l11ll111l1_opy_ = True
                return
            bstack1l11l111l1l_opy_ = self.scripts.get(f.framework_name, {})
            if not bstack1l11l111l1l_opy_:
                platform_index = f.bstack1ll1llll11l_opy_(instance, bstack1ll11ll1lll_opy_.bstack1lll11l1l1l_opy_, 0)
                self.logger.debug(bstack11ll1_opy_ (u"ࠥࡲࡴࠦࡡ࠲࠳ࡼࠤࡸࡩࡲࡪࡲࡷࡷࠥ࡬࡯ࡳࠢࡳࡰࡦࡺࡦࡰࡴࡰࡣ࡮ࡴࡤࡦࡺࡀࡿࡵࡲࡡࡵࡨࡲࡶࡲࡥࡩ࡯ࡦࡨࡼࢂࠦࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡱࡥࡲ࡫࠽ࠣᏫ") + str(f.framework_name) + bstack11ll1_opy_ (u"ࠦࠧᏬ"))
                return
            command_name = f.bstack1ll11l1l111_opy_(*args)
            if not command_name:
                self.logger.debug(bstack11ll1_opy_ (u"ࠧࡳࡩࡴࡵ࡬ࡲ࡬ࠦࡣࡰ࡯ࡰࡥࡳࡪ࡟࡯ࡣࡰࡩࠥ࡬࡯ࡳࠢࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࡤࡴࡡ࡮ࡧࡀࡿ࡫࠴ࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡱࡥࡲ࡫ࡽࠡ࡯ࡨࡸ࡭ࡵࡤࡠࡰࡤࡱࡪࡃࠢᏭ") + str(method_name) + bstack11ll1_opy_ (u"ࠨࠢᏮ"))
                return
            bstack1l11l111l11_opy_ = f.bstack1ll1llll11l_opy_(instance, bstack1l1l11111ll_opy_.bstack1l11l1llll1_opy_, False)
            if command_name == bstack11ll1_opy_ (u"ࠢࡨࡧࡷࠦᏯ") and not bstack1l11l111l11_opy_:
                f.bstack1lll111ll11_opy_(instance, bstack1l1l11111ll_opy_.bstack1l11l1llll1_opy_, True)
                bstack1l11l111l11_opy_ = True
            if not bstack1l11l111l11_opy_ and not self.bstack1l11ll111ll_opy_:
                self.logger.debug(bstack11ll1_opy_ (u"ࠣࡰࡲࠤ࡚ࡘࡌࠡ࡮ࡲࡥࡩ࡫ࡤࠡࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡳࡧ࡭ࡦ࠿ࡾࡪ࠳࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡰࡤࡱࡪࢃࠠࡤࡱࡰࡱࡦࡴࡤࡠࡰࡤࡱࡪࡃࠢᏰ") + str(command_name) + bstack11ll1_opy_ (u"ࠤࠥᏱ"))
                return
            scripts_to_run = self.commands.get(f.framework_name, {}).get(method_name, {}).get(command_name, [])
            if not scripts_to_run:
                self.logger.debug(bstack11ll1_opy_ (u"ࠥࡲࡴࠦࡡ࠲࠳ࡼࠤࡸࡩࡲࡪࡲࡷࡷࠥ࡬࡯ࡳࠢࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࡤࡴࡡ࡮ࡧࡀࡿ࡫࠴ࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡱࡥࡲ࡫ࡽࠡࡥࡲࡱࡲࡧ࡮ࡥࡡࡱࡥࡲ࡫࠽ࠣᏲ") + str(command_name) + bstack11ll1_opy_ (u"ࠦࠧᏳ"))
                return
            self.logger.info(bstack11ll1_opy_ (u"ࠧࡸࡵ࡯ࡰ࡬ࡲ࡬ࠦࡻ࡭ࡧࡱࠬࡸࡩࡲࡪࡲࡷࡷࡤࡺ࡯ࡠࡴࡸࡲ࠮ࢃࠠࡴࡥࡵ࡭ࡵࡺࡳࠡࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡳࡧ࡭ࡦ࠿ࡾࡪ࠳࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡰࡤࡱࡪࢃࠠࡤࡱࡰࡱࡦࡴࡤࡠࡰࡤࡱࡪࡃࠢᏴ") + str(command_name) + bstack11ll1_opy_ (u"ࠨࠢᏵ"))
            scripts = [(s, bstack1l11l111l1l_opy_[s]) for s in scripts_to_run if s in bstack1l11l111l1l_opy_]
            for script_name, bstack1l111ll1ll1_opy_ in scripts:
                try:
                    bstack1ll11l1l1l_opy_ = datetime.now()
                    if script_name == bstack11ll1_opy_ (u"ࠢࡴࡥࡤࡲࠧ᏶"):
                        result = self.perform_scan(driver, method=command_name, framework_name=f.framework_name)
                        try:
                            bstack1ll1ll11ll_opy_ = {
                                bstack11ll1_opy_ (u"ࠣࡴࡨࡵࡺ࡫ࡳࡵࠤ᏷"): {
                                    bstack11ll1_opy_ (u"ࠤࡦࡳࡲࡳࡡ࡯ࡦࠥᏸ"): bstack11ll1_opy_ (u"ࠥࡅ࠶࠷࡙ࡠࡕࡆࡅࡓࠨᏹ"),
                                    bstack11ll1_opy_ (u"ࠦࡵࡧࡲࡢ࡯ࡨࡸࡪࡸࡳࠣᏺ"): [
                                        {
                                            bstack11ll1_opy_ (u"ࠧࡳࡥࡵࡪࡲࡨࠧᏻ"): command_name
                                        }
                                    ]
                                },
                                bstack11ll1_opy_ (u"ࠨࡲࡦࡵࡳࡳࡳࡹࡥࠣᏼ"): {
                                    bstack11ll1_opy_ (u"ࠢࡣࡱࡧࡽࠧᏽ"): {
                                        bstack11ll1_opy_ (u"ࠣ࡯ࡶ࡫ࠧ᏾"): result.get(bstack11ll1_opy_ (u"ࠤࡰࡷ࡬ࠨ᏿"), bstack11ll1_opy_ (u"ࠥࠦ᐀")) if isinstance(result, dict) else bstack11ll1_opy_ (u"ࠦࠧᐁ"),
                                        bstack11ll1_opy_ (u"ࠧࡹࡵࡤࡥࡨࡷࡸࠨᐂ"): result.get(bstack11ll1_opy_ (u"ࠨࡳࡶࡥࡦࡩࡸࡹࠢᐃ"), True) if isinstance(result, dict) else True
                                    }
                                }
                            }
                            self.bstack11ll111l1l_opy_.info(json.dumps(bstack1ll1ll11ll_opy_, separators=(bstack11ll1_opy_ (u"ࠢ࠭ࠤᐄ"), bstack11ll1_opy_ (u"ࠣ࠼ࠥᐅ"))))
                        except Exception as bstack1l11lll1_opy_:
                            self.logger.debug(bstack11ll1_opy_ (u"ࠤࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥࡲ࡯ࡨࠢࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠢࡶࡧࡦࡴࠠࡥࡣࡷࡥ࠿ࠦࠢᐆ") + str(bstack1l11lll1_opy_) + bstack11ll1_opy_ (u"ࠥࠦᐇ"))
                    instance.bstack1lll1lll1_opy_(bstack11ll1_opy_ (u"ࠦࡦ࠷࠱ࡺ࠼ࠥᐈ") + script_name, datetime.now() - bstack1ll11l1l1l_opy_)
                    if isinstance(result, dict) and not result.get(bstack11ll1_opy_ (u"ࠧࡹࡵࡤࡥࡨࡷࡸࠨᐉ"), True):
                        self.logger.warning(bstack11ll1_opy_ (u"ࠨࡳ࡬࡫ࡳࠤࡪࡾࡥࡤࡷࡷ࡭ࡳ࡭ࠠࡳࡧࡰࡥ࡮ࡴࡩ࡯ࡩࠣࡷࡨࡸࡩࡱࡶࡶ࠾ࠥࠨᐊ") + str(result) + bstack11ll1_opy_ (u"ࠢࠣᐋ"))
                        break
                except Exception as e:
                    self.logger.error(bstack11ll1_opy_ (u"ࠣࡧࡵࡶࡴࡸࠠࡦࡺࡨࡧࡺࡺࡩ࡯ࡩࠣࡷࡨࡸࡩࡱࡶࡀࡿࡸࡩࡲࡪࡲࡷࡣࡳࡧ࡭ࡦࡿࠣࡩࡷࡸ࡯ࡳ࠿ࠥᐌ") + str(e) + bstack11ll1_opy_ (u"ࠤࠥᐍ"))
        except Exception as e:
            self.logger.error(bstack11ll1_opy_ (u"ࠥࡳࡳࡥࡢࡦࡨࡲࡶࡪࡥࡥࡹࡧࡦࡹࡹ࡫ࠠࡦࡴࡵࡳࡷࡃࠢᐎ") + str(e) + bstack11ll1_opy_ (u"ࠦࠧᐏ"))
    def bstack1l1llllll1l_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll1l11l11_opy_,
        bstack1lll1lll111_opy_: Tuple[bstack1llll1ll111_opy_, bstack1lll1111l11_opy_],
        *args,
        **kwargs,
    ):
        tags = self._1l11l11lll1_opy_(instance, args)
        capabilities = self.bstack1l11l111ll1_opy_.bstack1ll111lll11_opy_(f, instance, bstack1lll1lll111_opy_, *args, **kwargs)
        self.accessibility = self.bstack1l11l1l111l_opy_(tags, capabilities)
        if not self.accessibility:
            self.logger.debug(bstack11ll1_opy_ (u"ࠧࡵ࡮ࡠࡣࡩࡸࡪࡸ࡟ࡵࡧࡶࡸ࠿ࠦࡡ࠲࠳ࡼࠤࡳࡵࡴࠡࡧࡱࡥࡧࡲࡥࡥࠤᐐ"))
            return
        driver = self.bstack1l11l111ll1_opy_.bstack1l1lllll1l1_opy_(f, instance, bstack1lll1lll111_opy_, *args, **kwargs)
        test_name = f.bstack1ll1llll11l_opy_(instance, TestFramework.bstack1llll1l11ll_opy_)
        if not test_name:
            self.logger.debug(bstack11ll1_opy_ (u"ࠨ࡯࡯ࡡࡤࡪࡹ࡫ࡲࡠࡶࡨࡷࡹࡀࠠ࡮࡫ࡶࡷ࡮ࡴࡧࠡࡶࡨࡷࡹࠦ࡮ࡢ࡯ࡨࠦᐑ"))
            return
        test_uuid = f.bstack1ll1llll11l_opy_(instance, TestFramework.bstack1llll111ll1_opy_)
        if not test_uuid:
            self.logger.debug(bstack11ll1_opy_ (u"ࠢࡰࡰࡢࡥ࡫ࡺࡥࡳࡡࡷࡩࡸࡺ࠺ࠡ࡯࡬ࡷࡸ࡯࡮ࡨࠢࡷࡩࡸࡺࠠࡶࡷ࡬ࡨࠧᐒ"))
            return
        if isinstance(self.bstack1l11l111ll1_opy_, bstack1l1l1l1111l_opy_):
            framework_name = bstack11ll1_opy_ (u"ࠨࡲ࡯ࡥࡾࡽࡲࡪࡩ࡫ࡸࠬᐓ")
        else:
            framework_name = bstack11ll1_opy_ (u"ࠩࡶࡩࡱ࡫࡮ࡪࡷࡰࠫᐔ")
        self.bstack1lll1111ll_opy_(driver, test_name, framework_name, test_uuid)
    def perform_scan(self, driver: object, method: Union[None, str], framework_name: str):
        bstack1lll1l1ll11_opy_ = bstack1lll111111l_opy_.bstack1lll1111lll_opy_(EVENTS.bstack11lll11l_opy_.value)
        if not self.accessibility:
            self.logger.debug(bstack11ll1_opy_ (u"ࠥࡴࡪࡸࡦࡰࡴࡰࡣࡸࡩࡡ࡯࠼ࠣࡥ࠶࠷ࡹࠡࡰࡲࡸࠥ࡫࡮ࡢࡤ࡯ࡩࡩࠦࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡱࡥࡲ࡫࠽ࡼࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡳࡧ࡭ࡦࡿࠣࠦᐕ"))
            return
        bstack1ll11l1l1l_opy_ = datetime.now()
        bstack1l111ll1ll1_opy_ = self.scripts.get(framework_name, {}).get(bstack11ll1_opy_ (u"ࠦࡸࡩࡡ࡯ࠤᐖ"), None)
        if not bstack1l111ll1ll1_opy_:
            self.logger.debug(bstack11ll1_opy_ (u"ࠧࡶࡥࡳࡨࡲࡶࡲࡥࡳࡤࡣࡱ࠾ࠥࡳࡩࡴࡵ࡬ࡲ࡬ࠦࠧࡴࡥࡤࡲࠬࠦࡳࡤࡴ࡬ࡴࡹࠦࡦࡰࡴࠣࡪࡷࡧ࡭ࡦࡹࡲࡶࡰࡥ࡮ࡢ࡯ࡨࡁࠧᐗ") + str(framework_name) + bstack11ll1_opy_ (u"ࠨࠠࠣᐘ"))
            return
        if self.bstack1l11ll111ll_opy_:
            arg = dict()
            arg[bstack11ll1_opy_ (u"ࠢ࡮ࡧࡷ࡬ࡴࡪࠢᐙ")] = method if method else bstack11ll1_opy_ (u"ࠣࠤᐚ")
            arg[bstack11ll1_opy_ (u"ࠤࡷ࡬࡙࡫ࡳࡵࡔࡸࡲ࡚ࡻࡩࡥࠤᐛ")] = self.bstack1l11l1ll111_opy_[bstack11ll1_opy_ (u"ࠥࡸࡪࡹࡴࡠࡴࡸࡲࡤࡻࡵࡪࡦࠥᐜ")]
            arg[bstack11ll1_opy_ (u"ࠦࡹ࡮ࡂࡶ࡫࡯ࡨ࡚ࡻࡩࡥࠤᐝ")] = self.bstack1l11l1ll111_opy_[bstack11ll1_opy_ (u"ࠧࡺࡥࡴࡶ࡫ࡹࡧࡥࡢࡶ࡫࡯ࡨࡤࡻࡵࡪࡦࠥᐞ")]
            arg[bstack11ll1_opy_ (u"ࠨࡡࡶࡶ࡫ࡌࡪࡧࡤࡦࡴࠥᐟ")] = self.bstack1l11l1ll111_opy_[bstack11ll1_opy_ (u"ࠢࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࡔࡰ࡭ࡨࡲࠧᐠ")]
            arg[bstack11ll1_opy_ (u"ࠣࡶ࡫ࡎࡼࡺࡔࡰ࡭ࡨࡲࠧᐡ")] = self.bstack1l11l1ll111_opy_[bstack11ll1_opy_ (u"ࠤࡷ࡬ࡤࡰࡷࡵࡡࡷࡳࡰ࡫࡮ࠣᐢ")]
            arg[bstack11ll1_opy_ (u"ࠥࡷࡨࡧ࡮ࡕ࡫ࡰࡩࡸࡺࡡ࡮ࡲࠥᐣ")] = str(int(datetime.now().timestamp() * 1000))
            bstack1l11l111lll_opy_ = self.bstack1l11l11l11l_opy_(bstack11ll1_opy_ (u"ࠦࡸࡩࡡ࡯ࠤᐤ"), self.bstack1l11l1ll111_opy_[bstack11ll1_opy_ (u"ࠧࡺࡥࡴࡶࡢࡶࡺࡴ࡟ࡶࡷ࡬ࡨࠧᐥ")])
            if bstack11ll1_opy_ (u"ࠨࡣࡦࡰࡷࡶࡦࡲࡁࡶࡶ࡫ࡘࡴࡱࡥ࡯ࠤᐦ") in bstack1l11l111lll_opy_:
                bstack1l11l111lll_opy_ = bstack1l11l111lll_opy_.copy()
                bstack1l11l111lll_opy_[bstack11ll1_opy_ (u"ࠢࡤࡧࡱࡸࡷࡧ࡬ࡂࡷࡷ࡬ࡍ࡫ࡡࡥࡧࡵࠦᐧ")] = bstack1l11l111lll_opy_.pop(bstack11ll1_opy_ (u"ࠣࡥࡨࡲࡹࡸࡡ࡭ࡃࡸࡸ࡭࡚࡯࡬ࡧࡱࠦᐨ"))
            arg = bstack1l11l11l1l1_opy_(arg, bstack1l11l111lll_opy_)
            bstack1l11l1lll1l_opy_ = bstack1l111ll1ll1_opy_ % json.dumps(arg)
            driver.execute_script(bstack1l11l1lll1l_opy_)
            return
        instance = bstack1ll1l1111l1_opy_.bstack1ll1lllll1l_opy_(driver)
        if instance:
            if not bstack1ll1l1111l1_opy_.bstack1ll1llll11l_opy_(instance, bstack1l1l11111ll_opy_.bstack1l11l1111ll_opy_, False):
                bstack1ll1l1111l1_opy_.bstack1lll111ll11_opy_(instance, bstack1l1l11111ll_opy_.bstack1l11l1111ll_opy_, True)
            else:
                self.logger.info(bstack11ll1_opy_ (u"ࠤࡳࡩࡷ࡬࡯ࡳ࡯ࡢࡷࡨࡧ࡮࠻ࠢࡤࡰࡷ࡫ࡡࡥࡻࠣ࡭ࡳࠦࡰࡳࡱࡪࡶࡪࡹࡳࠡࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡳࡧ࡭ࡦ࠿ࡾࡪࡷࡧ࡭ࡦࡹࡲࡶࡰࡥ࡮ࡢ࡯ࡨࢁࠥࡳࡥࡵࡪࡲࡨࡂࠨᐩ") + str(method) + bstack11ll1_opy_ (u"ࠥࠦᐪ"))
                return
        self.logger.info(bstack11ll1_opy_ (u"ࠦࡵ࡫ࡲࡧࡱࡵࡱࡤࡹࡣࡢࡰ࠽ࠤ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟࡯ࡣࡰࡩࡂࢁࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡱࡥࡲ࡫ࡽࠡ࡯ࡨࡸ࡭ࡵࡤ࠾ࠤᐫ") + str(method) + bstack11ll1_opy_ (u"ࠧࠨᐬ"))
        if framework_name == bstack11ll1_opy_ (u"࠭ࡰ࡭ࡣࡼࡻࡷ࡯ࡧࡩࡶࠪᐭ"):
            result = self.bstack1l11l111ll1_opy_.bstack1l11ll11l11_opy_(driver, bstack1l111ll1ll1_opy_)
        else:
            result = driver.execute_async_script(bstack1l111ll1ll1_opy_, {bstack11ll1_opy_ (u"ࠢ࡮ࡧࡷ࡬ࡴࡪࠢᐮ"): method if method else bstack11ll1_opy_ (u"ࠣࠤᐯ")})
        bstack1lll111111l_opy_.end(EVENTS.bstack11lll11l_opy_.value, bstack1lll1l1ll11_opy_+bstack11ll1_opy_ (u"ࠤ࠽ࡷࡹࡧࡲࡵࠤᐰ"), bstack1lll1l1ll11_opy_+bstack11ll1_opy_ (u"ࠥ࠾ࡪࡴࡤࠣᐱ"), True, None, command=method)
        if instance:
            bstack1ll1l1111l1_opy_.bstack1lll111ll11_opy_(instance, bstack1l1l11111ll_opy_.bstack1l11l1111ll_opy_, False)
            instance.bstack1lll1lll1_opy_(bstack11ll1_opy_ (u"ࠦࡦ࠷࠱ࡺ࠼ࡳࡩࡷ࡬࡯ࡳ࡯ࡢࡷࡨࡧ࡮ࠣᐲ"), datetime.now() - bstack1ll11l1l1l_opy_)
        return result
        def bstack1l11l1lllll_opy_(self, driver: object, framework_name, result_type: str):
            self.bstack1ll111111l1_opy_()
            req = structs.AccessibilityResultRequest()
            req.bin_session_id = self.bin_session_id
            req.bstack1l111lll1l1_opy_ = self.bstack1l11l1ll111_opy_[bstack11ll1_opy_ (u"ࠧࡺࡥࡴࡶࡢࡶࡺࡴ࡟ࡶࡷ࡬ࡨࠧᐳ")]
            req.result_type = result_type
            req.session_id = self.bin_session_id
            try:
                r = self.bstack1lllll11ll1_opy_.AccessibilityResult(req)
                if not r.success:
                    self.logger.debug(bstack11ll1_opy_ (u"ࠨࡲࡦࡥࡨ࡭ࡻ࡫ࡤࠡࡨࡵࡳࡲࠦࡳࡦࡴࡹࡩࡷࡀࠠࠣᐴ") + str(r) + bstack11ll1_opy_ (u"ࠢࠣᐵ"))
                else:
                    bstack1l111lllll1_opy_ = json.loads(r.bstack1l11ll11111_opy_.decode(bstack11ll1_opy_ (u"ࠨࡷࡷࡪ࠲࠾ࠧᐶ")))
                    if result_type == bstack11ll1_opy_ (u"ࠩࡪࡩࡹࡘࡥࡴࡷ࡯ࡸࡸ࠭ᐷ"):
                        return bstack1l111lllll1_opy_.get(bstack11ll1_opy_ (u"ࠥࡨࡦࡺࡡࠣᐸ"), [])
                    else:
                        return bstack1l111lllll1_opy_.get(bstack11ll1_opy_ (u"ࠦࡩࡧࡴࡢࠤᐹ"), {})
            except grpc.RpcError as e:
                self.logger.error(bstack11ll1_opy_ (u"ࠧࡸࡰࡤ࠯ࡨࡶࡷࡵࡲࠡࡹ࡫࡭ࡱ࡫ࠠࡧࡧࡷࡧ࡭࡯࡮ࡨࠢࡪࡩࡹࡥࡡࡱࡲࡢࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࡢࡶࡪࡹࡵ࡭ࡶࠣࡪࡷࡵ࡭ࠡࡥ࡯࡭࠿ࠦࠢᐺ") + str(e) + bstack11ll1_opy_ (u"ࠨࠢᐻ"))
    @measure(event_name=EVENTS.bstack1lll1l111l_opy_, stage=STAGE.bstack11l1llll1_opy_)
    def get_accessibility_results(self, driver: object, framework_name):
        if not self.accessibility:
            self.logger.debug(bstack11ll1_opy_ (u"ࠢࡨࡧࡷࡣࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࡣࡷ࡫ࡳࡶ࡮ࡷࡷ࠿ࠦࡡ࠲࠳ࡼࠤࡳࡵࡴࠡࡧࡱࡥࡧࡲࡥࡥࠤᐼ"))
            return
        if self.bstack1l11ll111ll_opy_:
            self.logger.debug(bstack11ll1_opy_ (u"ࠨࡒࡨࡶ࡫ࡵࡲ࡮࡫ࡱ࡫ࠥࡹࡣࡢࡰࠣࡪࡴࡸࠠࡢࡲࡳࠤࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠫᐽ"))
            self.perform_scan(driver, method=None, framework_name=framework_name)
            return self.bstack1l11l1lllll_opy_(driver, framework_name, bstack11ll1_opy_ (u"ࠤࡪࡩࡹࡘࡥࡴࡷ࡯ࡸࡸࠨᐾ"))
        bstack1l111ll1ll1_opy_ = self.scripts.get(framework_name, {}).get(bstack11ll1_opy_ (u"ࠥ࡫ࡪࡺࡒࡦࡵࡸࡰࡹࡹࠢᐿ"), None)
        if not bstack1l111ll1ll1_opy_:
            self.logger.debug(bstack11ll1_opy_ (u"ࠦࡲ࡯ࡳࡴ࡫ࡱ࡫ࠥ࠭ࡧࡦࡶࡕࡩࡸࡻ࡬ࡵࡵࠪࠤࡸࡩࡲࡪࡲࡷࠤ࡫ࡵࡲࠡࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡳࡧ࡭ࡦ࠿ࠥᑀ") + str(framework_name) + bstack11ll1_opy_ (u"ࠧࠨᑁ"))
            return
        self.perform_scan(driver, method=None, framework_name=framework_name)
        bstack1ll11l1l1l_opy_ = datetime.now()
        if framework_name == bstack11ll1_opy_ (u"࠭ࡰ࡭ࡣࡼࡻࡷ࡯ࡧࡩࡶࠪᑂ"):
            result = self.bstack1l11l111ll1_opy_.bstack1l11ll11l11_opy_(driver, bstack1l111ll1ll1_opy_)
        else:
            result = driver.execute_async_script(bstack1l111ll1ll1_opy_)
        instance = bstack1ll1l1111l1_opy_.bstack1ll1lllll1l_opy_(driver)
        if instance:
            instance.bstack1lll1lll1_opy_(bstack11ll1_opy_ (u"ࠢࡢ࠳࠴ࡽ࠿࡭ࡥࡵࡡࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࡡࡵࡩࡸࡻ࡬ࡵࡵࠥᑃ"), datetime.now() - bstack1ll11l1l1l_opy_)
        return result
    @measure(event_name=EVENTS.bstack1ll1ll1ll1_opy_, stage=STAGE.bstack11l1llll1_opy_)
    def get_accessibility_results_summary(self, driver: object, framework_name):
        if not self.accessibility:
            self.logger.debug(bstack11ll1_opy_ (u"ࠣࡩࡨࡸࡤࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࡤࡸࡥࡴࡷ࡯ࡸࡸࡥࡳࡶ࡯ࡰࡥࡷࡿ࠺ࠡࡣ࠴࠵ࡾࠦ࡮ࡰࡶࠣࡩࡳࡧࡢ࡭ࡧࡧࠦᑄ"))
            return
        if self.bstack1l11ll111ll_opy_:
            self.perform_scan(driver, method=None, framework_name=framework_name)
            return self.bstack1l11l1lllll_opy_(driver, framework_name, bstack11ll1_opy_ (u"ࠩࡪࡩࡹࡘࡥࡴࡷ࡯ࡸࡸ࡙ࡵ࡮࡯ࡤࡶࡾ࠭ᑅ"))
        bstack1l111ll1ll1_opy_ = self.scripts.get(framework_name, {}).get(bstack11ll1_opy_ (u"ࠥ࡫ࡪࡺࡒࡦࡵࡸࡰࡹࡹࡓࡶ࡯ࡰࡥࡷࡿࠢᑆ"), None)
        if not bstack1l111ll1ll1_opy_:
            self.logger.debug(bstack11ll1_opy_ (u"ࠦࡲ࡯ࡳࡴ࡫ࡱ࡫ࠥ࠭ࡧࡦࡶࡕࡩࡸࡻ࡬ࡵࡵࡖࡹࡲࡳࡡࡳࡻࠪࠤࡸࡩࡲࡪࡲࡷࠤ࡫ࡵࡲࠡࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡳࡧ࡭ࡦ࠿ࠥᑇ") + str(framework_name) + bstack11ll1_opy_ (u"ࠧࠨᑈ"))
            return
        self.perform_scan(driver, method=None, framework_name=framework_name)
        bstack1ll11l1l1l_opy_ = datetime.now()
        if framework_name == bstack11ll1_opy_ (u"࠭ࡰ࡭ࡣࡼࡻࡷ࡯ࡧࡩࡶࠪᑉ"):
            result = self.bstack1l11l111ll1_opy_.bstack1l11ll11l11_opy_(driver, bstack1l111ll1ll1_opy_)
        else:
            result = driver.execute_async_script(bstack1l111ll1ll1_opy_)
        instance = bstack1ll1l1111l1_opy_.bstack1ll1lllll1l_opy_(driver)
        if instance:
            instance.bstack1lll1lll1_opy_(bstack11ll1_opy_ (u"ࠢࡢ࠳࠴ࡽ࠿࡭ࡥࡵࡡࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࡡࡵࡩࡸࡻ࡬ࡵࡵࡢࡷࡺࡳ࡭ࡢࡴࡼࠦᑊ"), datetime.now() - bstack1ll11l1l1l_opy_)
        return result
    @measure(event_name=EVENTS.bstack1l111ll11l1_opy_, stage=STAGE.bstack11l1llll1_opy_)
    def bstack1l111ll111l_opy_(
        self,
        platform_index: int,
        framework_name: str,
        framework_version: str,
        hub_url: str,
    ):
        self.bstack1ll111111l1_opy_()
        req = structs.AccessibilityConfigRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.framework_name = framework_name
        req.framework_version = framework_version
        req.hub_url = hub_url
        try:
            r = self.bstack1lllll11ll1_opy_.AccessibilityConfig(req)
            if not r.success:
                self.logger.debug(bstack11ll1_opy_ (u"ࠣࡴࡨࡧࡪ࡯ࡶࡦࡦࠣࡪࡷࡵ࡭ࠡࡵࡨࡶࡻ࡫ࡲ࠻ࠢࠥᑋ") + str(r) + bstack11ll1_opy_ (u"ࠤࠥᑌ"))
            else:
                self.bstack1l11l1l11ll_opy_(framework_name, r)
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack11ll1_opy_ (u"ࠥࡶࡵࡩ࠭ࡦࡴࡵࡳࡷࡀࠠࠣᑍ") + str(e) + bstack11ll1_opy_ (u"ࠦࠧᑎ"))
            traceback.print_exc()
            raise e
    def bstack1l11l1l11ll_opy_(self, framework_name: str, result: structs.AccessibilityConfigResponse) -> bool:
        if not result.success or not result.accessibility.success:
            self.logger.debug(bstack11ll1_opy_ (u"ࠧࡲ࡯ࡢࡦࡢࡧࡴࡴࡦࡪࡩ࠽ࠤࡦ࠷࠱ࡺࠢࡱࡳࡹࠦࡦࡰࡷࡱࡨࠧᑏ"))
            return False
        if result.accessibility.is_app_accessibility:
            self.bstack1l11ll111ll_opy_ = result.accessibility.is_app_accessibility
        if result.testhub.build_hashed_id:
            self.bstack1l11l1ll111_opy_[bstack11ll1_opy_ (u"ࠨࡴࡦࡵࡷ࡬ࡺࡨ࡟ࡣࡷ࡬ࡰࡩࡥࡵࡶ࡫ࡧࠦᑐ")] = result.testhub.build_hashed_id
        if result.testhub.jwt:
            self.bstack1l11l1ll111_opy_[bstack11ll1_opy_ (u"ࠢࡵࡪࡢ࡮ࡼࡺ࡟ࡵࡱ࡮ࡩࡳࠨᑑ")] = result.testhub.jwt
        if result.accessibility.options:
            options = result.accessibility.options
            if options.capabilities:
                for caps in options.capabilities:
                    self.bstack1l11l1ll111_opy_[caps.name] = caps.value
            if options.scripts:
                self.scripts[framework_name] = {row.name: row.command for row in options.scripts}
            if options.commands_to_wrap and options.commands_to_wrap.commands:
                scripts_to_run = [s for s in options.commands_to_wrap.scripts_to_run]
                if not scripts_to_run:
                    return False
                bstack1l11l1111l1_opy_ = dict()
                for command in options.commands_to_wrap.commands:
                    if command.library == self.bstack1l11l11ll11_opy_ and command.module == self.bstack1l111ll1l11_opy_:
                        if command.method and not command.method in bstack1l11l1111l1_opy_:
                            bstack1l11l1111l1_opy_[command.method] = dict()
                        if command.name and not command.name in bstack1l11l1111l1_opy_[command.method]:
                            bstack1l11l1111l1_opy_[command.method][command.name] = list()
                        bstack1l11l1111l1_opy_[command.method][command.name].extend(scripts_to_run)
                self.commands[framework_name] = bstack1l11l1111l1_opy_
        return bool(self.commands.get(framework_name, None))
    def bstack1l11l11l111_opy_(
        self,
        f: bstack1ll11ll1lll_opy_,
        exec: Tuple[bstack1ll1l1ll1l1_opy_, str],
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if isinstance(self.bstack1l11l111ll1_opy_, bstack1l1l1l1111l_opy_) and method_name != bstack11ll1_opy_ (u"ࠨࡥࡲࡲࡳ࡫ࡣࡵࠩᑒ"):
            return
        if bstack1ll1l1111l1_opy_.bstack1lll1ll1ll1_opy_(instance, bstack1l1l11111ll_opy_.bstack1l11l11llll_opy_):
            return
        if f.bstack1ll1l11lll1_opy_(method_name, *args):
            bstack1l111lll11l_opy_ = False
            desired_capabilities = f.bstack1ll11ll1ll1_opy_(instance)
            if isinstance(desired_capabilities, dict):
                hub_url = f.bstack1ll1l1l11l1_opy_(instance)
                platform_index = f.bstack1ll1llll11l_opy_(instance, bstack1ll11ll1lll_opy_.bstack1lll11l1l1l_opy_, 0)
                bstack1l11l1l1l11_opy_ = datetime.now()
                r = self.bstack1l111ll111l_opy_(platform_index, f.framework_name, f.framework_version, hub_url)
                instance.bstack1lll1lll1_opy_(bstack11ll1_opy_ (u"ࠤࡪࡶࡵࡩ࠺ࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿ࡟ࡤࡱࡱࡪ࡮࡭ࠢᑓ"), datetime.now() - bstack1l11l1l1l11_opy_)
                bstack1l111lll11l_opy_ = r.success
            else:
                self.logger.error(bstack11ll1_opy_ (u"ࠥࡱ࡮ࡹࡳࡪࡰࡪࠤࡩ࡫ࡳࡪࡴࡨࡨࠥࡩࡡࡱࡣࡥ࡭ࡱ࡯ࡴࡪࡧࡶࡁࠧᑔ") + str(desired_capabilities) + bstack11ll1_opy_ (u"ࠦࠧᑕ"))
            f.bstack1lll111ll11_opy_(instance, bstack1l1l11111ll_opy_.bstack1l11l11llll_opy_, bstack1l111lll11l_opy_)
    def bstack1llll1111l_opy_(self, test_tags):
        bstack1l111ll111l_opy_ = self.config.get(bstack11ll1_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࡔࡶࡴࡪࡱࡱࡷࠬᑖ"))
        if not bstack1l111ll111l_opy_:
            return True
        try:
            include_tags = bstack1l111ll111l_opy_[bstack11ll1_opy_ (u"࠭ࡩ࡯ࡥ࡯ࡹࡩ࡫ࡔࡢࡩࡶࡍࡳ࡚ࡥࡴࡶ࡬ࡲ࡬࡙ࡣࡰࡲࡨࠫᑗ")] if bstack11ll1_opy_ (u"ࠧࡪࡰࡦࡰࡺࡪࡥࡕࡣࡪࡷࡎࡴࡔࡦࡵࡷ࡭ࡳ࡭ࡓࡤࡱࡳࡩࠬᑘ") in bstack1l111ll111l_opy_ and isinstance(bstack1l111ll111l_opy_[bstack11ll1_opy_ (u"ࠨ࡫ࡱࡧࡱࡻࡤࡦࡖࡤ࡫ࡸࡏ࡮ࡕࡧࡶࡸ࡮ࡴࡧࡔࡥࡲࡴࡪ࠭ᑙ")], list) else []
            exclude_tags = bstack1l111ll111l_opy_[bstack11ll1_opy_ (u"ࠩࡨࡼࡨࡲࡵࡥࡧࡗࡥ࡬ࡹࡉ࡯ࡖࡨࡷࡹ࡯࡮ࡨࡕࡦࡳࡵ࡫ࠧᑚ")] if bstack11ll1_opy_ (u"ࠪࡩࡽࡩ࡬ࡶࡦࡨࡘࡦ࡭ࡳࡊࡰࡗࡩࡸࡺࡩ࡯ࡩࡖࡧࡴࡶࡥࠨᑛ") in bstack1l111ll111l_opy_ and isinstance(bstack1l111ll111l_opy_[bstack11ll1_opy_ (u"ࠫࡪࡾࡣ࡭ࡷࡧࡩ࡙ࡧࡧࡴࡋࡱࡘࡪࡹࡴࡪࡰࡪࡗࡨࡵࡰࡦࠩᑜ")], list) else []
            excluded = any(tag in exclude_tags for tag in test_tags)
            included = len(include_tags) == 0 or any(tag in include_tags for tag in test_tags)
            return not excluded and included
        except Exception as error:
            self.logger.debug(bstack11ll1_opy_ (u"ࠧࡋࡲࡳࡱࡵࠤࡼ࡮ࡩ࡭ࡧࠣࡺࡦࡲࡩࡥࡣࡷ࡭ࡳ࡭ࠠࡵࡧࡶࡸࠥࡩࡡࡴࡧࠣࡪࡴࡸࠠࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡣࡧࡩࡳࡷ࡫ࠠࡴࡥࡤࡲࡳ࡯࡮ࡨ࠰ࠣࡉࡷࡸ࡯ࡳࠢ࠽ࠤࠧᑝ") + str(error))
        return False
    def bstack11l1lll1_opy_(self, caps):
        try:
            if self.bstack1l11ll111ll_opy_:
                bstack1l11l1l1lll_opy_ = caps.get(bstack11ll1_opy_ (u"ࠨࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡏࡣࡰࡩࠧᑞ"))
                if bstack1l11l1l1lll_opy_ is not None and str(bstack1l11l1l1lll_opy_).lower() == bstack11ll1_opy_ (u"ࠢࡢࡰࡧࡶࡴ࡯ࡤࠣᑟ"):
                    bstack1l11l11111l_opy_ = caps.get(bstack11ll1_opy_ (u"ࠣࡣࡳࡴ࡮ࡻ࡭࠻ࡲ࡯ࡥࡹ࡬࡯ࡳ࡯࡙ࡩࡷࡹࡩࡰࡰࠥᑠ")) or caps.get(bstack11ll1_opy_ (u"ࠤࡳࡰࡦࡺࡦࡰࡴࡰ࡚ࡪࡸࡳࡪࡱࡱࠦᑡ"))
                    if bstack1l11l11111l_opy_ is not None and int(bstack1l11l11111l_opy_) < 11:
                        self.logger.warning(bstack11ll1_opy_ (u"ࠥࡅࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠣࡅࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࠠࡸ࡫࡯ࡰࠥࡸࡵ࡯ࠢࡲࡲࡱࡿࠠࡰࡰࠣࡅࡳࡪࡲࡰ࡫ࡧࠤ࠶࠷ࠠࡢࡰࡧࠤࡦࡨ࡯ࡷࡧ࠱ࠤࡈࡻࡲࡳࡧࡱࡸࠥࡶ࡬ࡢࡶࡩࡳࡷࡳࠠࡷࡧࡵࡷ࡮ࡵ࡮ࠡ࠿ࠥᑢ") + str(bstack1l11l11111l_opy_) + bstack11ll1_opy_ (u"ࠦࠧᑣ"))
                        return False
                return True
            bstack1l11l1l11l1_opy_ = caps.get(bstack11ll1_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯࠿ࡵࡰࡵ࡫ࡲࡲࡸ࠭ᑤ"), {}).get(bstack11ll1_opy_ (u"࠭ࡤࡦࡸ࡬ࡧࡪࡔࡡ࡮ࡧࠪᑥ"), caps.get(bstack11ll1_opy_ (u"ࠧࡥࡧࡹ࡭ࡨ࡫ࠧᑦ"), bstack11ll1_opy_ (u"ࠨࠩᑧ")))
            if bstack1l11l1l11l1_opy_:
                self.logger.warning(bstack11ll1_opy_ (u"ࠤࡄࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠢࡄࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳࠦࡷࡪ࡮࡯ࠤࡷࡻ࡮ࠡࡱࡱࡰࡾࠦ࡯࡯ࠢࡇࡩࡸࡱࡴࡰࡲࠣࡦࡷࡵࡷࡴࡧࡵࡷ࠳ࠨᑨ"))
                return False
            browser = caps.get(bstack11ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡒࡦࡳࡥࠨᑩ"), bstack11ll1_opy_ (u"ࠫࠬᑪ")).lower()
            if browser != bstack11ll1_opy_ (u"ࠬࡩࡨࡳࡱࡰࡩࠬᑫ"):
                self.logger.warning(bstack11ll1_opy_ (u"ࠨࡁࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࠦࡁࡶࡶࡲࡱࡦࡺࡩࡰࡰࠣࡻ࡮ࡲ࡬ࠡࡴࡸࡲࠥࡵ࡮࡭ࡻࠣࡳࡳࠦࡃࡩࡴࡲࡱࡪࠦࡢࡳࡱࡺࡷࡪࡸࡳ࠯ࠤᑬ"))
                return False
            bstack1l111lll1ll_opy_ = bstack1l111ll1lll_opy_
            if not self.config.get(bstack11ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡇࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࠩᑭ")) or self.config.get(bstack11ll1_opy_ (u"ࠨࡶࡸࡶࡧࡵࡳࡤࡣ࡯ࡩࠬᑮ")):
                bstack1l111lll1ll_opy_ = bstack1l11l11l1ll_opy_
            browser_version = caps.get(bstack11ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴ࡙ࡩࡷࡹࡩࡰࡰࠪᑯ"))
            if not browser_version:
                browser_version = caps.get(bstack11ll1_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭࠽ࡳࡵࡺࡩࡰࡰࡶࠫᑰ"), {}).get(bstack11ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶ࡛࡫ࡲࡴ࡫ࡲࡲࠬᑱ"), bstack11ll1_opy_ (u"ࠬ࠭ᑲ"))
            bstack1l11l1l1111_opy_ = str(browser_version).lower() if browser_version is not None else bstack11ll1_opy_ (u"࠭ࠧᑳ")
            if bstack1l11l1l1111_opy_:
                if bstack1l11l1l1111_opy_.startswith(bstack11ll1_opy_ (u"ࠧ࡭ࡣࡷࡩࡸࡺࠧᑴ")):
                    if bstack1l11l1l1111_opy_.startswith(bstack11ll1_opy_ (u"ࠨ࡮ࡤࡸࡪࡹࡴ࠮ࠩᑵ")):
                        bstack1l11l1ll1ll_opy_ = bstack1l11l1l1111_opy_[len(bstack11ll1_opy_ (u"ࠩ࡯ࡥࡹ࡫ࡳࡵ࠯ࠪᑶ")):]
                        if bstack1l11l1ll1ll_opy_ and not bstack1l11l1ll1ll_opy_.isdigit():
                            self.logger.warning(bstack11ll1_opy_ (u"ࠥࡍࡳࡼࡡ࡭࡫ࡧࠤࡧࡸ࡯ࡸࡵࡨࡶࠥࡼࡥࡳࡵ࡬ࡳࡳࠦࡦࡰࡴࡰࡥࡹࠦࠧࠣᑷ") + str(browser_version) + bstack11ll1_opy_ (u"ࠦࠬࡁࠠࡦࡺࡳࡩࡨࡺࡥࡥࠢࠪࡰࡦࡺࡥࡴࡶࠪࠤࡴࡸࠠࠨ࡮ࡤࡸࡪࡹࡴ࠮࠾ࡱࡹࡲࡨࡥࡳࡀࠪ࠲ࠧᑸ"))
                            return False
                else:
                    try:
                        if int(bstack1l11l1l1111_opy_.split(bstack11ll1_opy_ (u"ࠬ࠴ࠧᑹ"))[0]) <= bstack1l111lll1ll_opy_:
                            self.logger.warning(bstack11ll1_opy_ (u"ࠨࡁࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࠦࡁࡶࡶࡲࡱࡦࡺࡩࡰࡰࠣࡻ࡮ࡲ࡬ࠡࡴࡸࡲࠥࡵ࡮࡭ࡻࠣࡳࡳࠦࡃࡩࡴࡲࡱࡪࠦࡢࡳࡱࡺࡷࡪࡸࠠࡷࡧࡵࡷ࡮ࡵ࡮ࠡࡩࡵࡩࡦࡺࡥࡳࠢࡷ࡬ࡦࡴࠠࠣᑺ") + str(bstack1l111lll1ll_opy_) + bstack11ll1_opy_ (u"ࠢ࠯ࠤᑻ"))
                            return False
                    except (ValueError, IndexError) as e:
                        self.logger.debug(bstack11ll1_opy_ (u"ࠣࡗࡱࡥࡧࡲࡥࠡࡶࡲࠤࡵࡧࡲࡴࡧࠣࡦࡷࡵࡷࡴࡧࡵࠤࡻ࡫ࡲࡴ࡫ࡲࡲࠥ࠭ࡻࡣࡴࡲࡻࡸ࡫ࡲࡠࡸࡨࡶࡸ࡯࡯࡯ࡿࠪ࠾ࠥࠨᑼ") + str(e) + bstack11ll1_opy_ (u"ࠤࠥᑽ"))
            bstack1l111llll1l_opy_ = caps.get(bstack11ll1_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭࠽ࡳࡵࡺࡩࡰࡰࡶࠫᑾ"), {}).get(bstack11ll1_opy_ (u"ࠫࡨ࡮ࡲࡰ࡯ࡨࡓࡵࡺࡩࡰࡰࡶࠫᑿ"))
            if not bstack1l111llll1l_opy_:
                bstack1l111llll1l_opy_ = caps.get(bstack11ll1_opy_ (u"ࠬ࡭࡯ࡰࡩ࠽ࡧ࡭ࡸ࡯࡮ࡧࡒࡴࡹ࡯࡯࡯ࡵࠪᒀ"), {})
            if bstack1l111llll1l_opy_ and bstack11ll1_opy_ (u"࠭࠭࠮ࡪࡨࡥࡩࡲࡥࡴࡵࠪᒁ") in bstack1l111llll1l_opy_.get(bstack11ll1_opy_ (u"ࠧࡢࡴࡪࡷࠬᒂ"), []):
                self.logger.warning(bstack11ll1_opy_ (u"ࠣࡃࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠡࡃࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࠥࡽࡩ࡭࡮ࠣࡲࡴࡺࠠࡳࡷࡱࠤࡴࡴࠠ࡭ࡧࡪࡥࡨࡿࠠࡩࡧࡤࡨࡱ࡫ࡳࡴࠢࡰࡳࡩ࡫࠮ࠡࡕࡺ࡭ࡹࡩࡨࠡࡶࡲࠤࡳ࡫ࡷࠡࡪࡨࡥࡩࡲࡥࡴࡵࠣࡱࡴࡪࡥࠡࡱࡵࠤࡦࡼ࡯ࡪࡦࠣࡹࡸ࡯࡮ࡨࠢ࡫ࡩࡦࡪ࡬ࡦࡵࡶࠤࡲࡵࡤࡦ࠰ࠥᒃ"))
                return False
            return True
        except Exception as error:
            self.logger.debug(bstack11ll1_opy_ (u"ࠤࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥ࡯࡮ࠡࡸࡤࡰ࡮ࡪࡡࡵࡧࠣࡥ࠶࠷ࡹࠡࡵࡸࡴࡵࡵࡲࡵࠢ࠽ࠦᒄ") + str(error))
            return False
    def bstack1l11l1lll11_opy_(self, test_uuid: str, result: structs.FetchDriverExecuteParamsEventResponse):
        bstack1l111lll111_opy_ = {
            bstack11ll1_opy_ (u"ࠪࡸ࡭࡚ࡥࡴࡶࡕࡹࡳ࡛ࡵࡪࡦࠪᒅ"): test_uuid,
        }
        bstack1l11l1ll1l1_opy_ = {}
        if result.success:
            bstack1l11l1ll1l1_opy_ = json.loads(result.accessibility_execute_params)
        return bstack1l11l11l1l1_opy_(bstack1l111lll111_opy_, bstack1l11l1ll1l1_opy_)
    def bstack1l11l11l11l_opy_(self, script_name: str, test_uuid: str) -> dict:
        bstack11ll1_opy_ (u"ࠦࠧࠨࠊࠡࠢࠣࠤࠥࠦࠠࠡࡈࡨࡸࡨ࡮ࠠࡤࡧࡱࡸࡷࡧ࡬ࠡࡣࡸࡸ࡭ࠦࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࠦࡣࡰࡰࡩ࡭࡬ࡻࡲࡢࡶ࡬ࡳࡳࠦࡦࡰࡴࠣࡸ࡭࡫ࠠࡨ࡫ࡹࡩࡳࠦࡳࡤࡴ࡬ࡴࡹࠦ࡮ࡢ࡯ࡨ࠲ࠏࠦࠠࠡࠢࠣࠤࠥࠦࡒࡦࡶࡸࡶࡳࡹࠠࡤࡣࡦ࡬ࡪࡪࠠࡤࡱࡱࡪ࡮࡭ࠠࡪࡨࠣࡥࡱࡸࡥࡢࡦࡼࠤ࡫࡫ࡴࡤࡪࡨࡨ࠱ࠦ࡯ࡵࡪࡨࡶࡼ࡯ࡳࡦࠢ࡯ࡳࡦࡪࡳࠡࡣࡱࡨࠥࡩࡡࡤࡪࡨࡷࠥ࡯ࡴ࠯ࠌࠣࠤࠥࠦࠠࠡࠢࠣࡅࡷ࡭ࡳ࠻ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࡴࡥࡵ࡭ࡵࡺ࡟࡯ࡣࡰࡩ࠿ࠦࡎࡢ࡯ࡨࠤࡴ࡬ࠠࡵࡪࡨࠤࡸࡩࡲࡪࡲࡷࠤࡹࡵࠠࡧࡧࡷࡧ࡭ࠦࡣࡰࡰࡩ࡭࡬ࠦࡦࡰࡴࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࡶࡨࡷࡹࡥࡵࡶ࡫ࡧ࠾࡛ࠥࡕࡊࡆࠣࡳ࡫ࠦࡴࡩࡧࠣࡸࡪࡹࡴࠡࡴࡸࡲࠥ࡬࡯ࡳࠢࡺ࡬࡮ࡩࡨࠡࡶࡲࠤ࡫࡫ࡴࡤࡪࠣࡧࡴࡴࡦࡪࡩࠍࠤࠥࠦࠠࠡࠢࠣࠤࡗ࡫ࡴࡶࡴࡱࡷ࠿ࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࡩ࡯ࡣࡵ࠼ࠣࡇࡴࡴࡦࡪࡩࡸࡶࡦࡺࡩࡰࡰࠣࡨ࡮ࡩࡴࡪࡱࡱࡥࡷࡿࠬࠡࡧࡰࡴࡹࡿࠠࡥ࡫ࡦࡸࠥ࡯ࡦࠡࡧࡵࡶࡴࡸࠠࡰࡥࡦࡹࡷࡹࠊࠡࠢࠣࠤࠥࠦࠠࠡࠤࠥࠦᒆ")
        try:
            if self.bstack1l111llll11_opy_:
                return self.bstack1l11ll1111l_opy_
            self.bstack1ll111111l1_opy_()
            req = structs.FetchDriverExecuteParamsEventRequest()
            req.bin_session_id = self.bin_session_id
            req.product = bstack11ll1_opy_ (u"ࠧࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠧᒇ")
            req.script_name = script_name
            r = self.bstack1lllll11ll1_opy_.FetchDriverExecuteParamsEvent(req)
            if r.success:
                self.bstack1l11ll1111l_opy_ = self.bstack1l11l1lll11_opy_(test_uuid, r)
                self.bstack1l111llll11_opy_ = True
            else:
                self.logger.error(bstack11ll1_opy_ (u"ࠨࡦࡦࡶࡦ࡬ࡈ࡫࡮ࡵࡴࡤࡰࡆࡻࡴࡩࡃ࠴࠵ࡾࡉ࡯࡯ࡨ࡬࡫࠿ࠦࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡩࡩࡹࡩࡨࠡࡦࡵ࡭ࡻ࡫ࡲࠡࡧࡻࡩࡨࡻࡴࡦࠢࡳࡥࡷࡧ࡭ࡴࠢࡩࡳࡷࠦࡻࡴࡥࡵ࡭ࡵࡺ࡟࡯ࡣࡰࡩࢂࡀࠠࠣᒈ") + str(r.error) + bstack11ll1_opy_ (u"ࠢࠣᒉ"))
                self.bstack1l11ll1111l_opy_ = dict()
            return self.bstack1l11ll1111l_opy_
        except Exception as e:
            self.logger.error(bstack11ll1_opy_ (u"ࠣࡨࡨࡸࡨ࡮ࡃࡦࡰࡷࡶࡦࡲࡁࡶࡶ࡫ࡅ࠶࠷ࡹࡄࡱࡱࡪ࡮࡭࠺ࠡࡈࡤ࡭ࡱ࡫ࡤࠡࡶࡲࠤ࡫࡫ࡴࡤࡪࠣࡨࡷ࡯ࡶࡦࡴࠣࡩࡽ࡫ࡣࡶࡶࡨࠤࡵࡧࡲࡢ࡯ࡶࠤ࡫ࡵࡲࠡࡽࡶࡧࡷ࡯ࡰࡵࡡࡱࡥࡲ࡫ࡽ࠻ࠢࠥᒊ") + str(traceback.format_exc()) + bstack11ll1_opy_ (u"ࠤࠥᒋ"))
            return dict()
    def bstack1lll1111ll_opy_(self, driver: object, name: str, framework_name: str, test_uuid: str):
        bstack1lll1l1ll11_opy_ = None
        try:
            self.bstack1ll111111l1_opy_()
            req = structs.FetchDriverExecuteParamsEventRequest()
            req.bin_session_id = self.bin_session_id
            req.product = bstack11ll1_opy_ (u"ࠥࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠥᒌ")
            req.script_name = bstack11ll1_opy_ (u"ࠦࡸࡧࡶࡦࡔࡨࡷࡺࡲࡴࡴࠤᒍ")
            r = self.bstack1lllll11ll1_opy_.FetchDriverExecuteParamsEvent(req)
            if not r.success:
                self.logger.debug(bstack11ll1_opy_ (u"ࠧࡸࡥࡤࡧ࡬ࡺࡪࡪࠠࡥࡴ࡬ࡺࡪࡸࠠࡦࡺࡨࡧࡺࡺࡥࠡࡲࡤࡶࡦࡳࡳࠡࡨࡵࡳࡲࠦࡳࡦࡴࡹࡩࡷࡀࠠࠣᒎ") + str(r.error) + bstack11ll1_opy_ (u"ࠨࠢᒏ"))
            else:
                bstack1l111lll111_opy_ = self.bstack1l11l1lll11_opy_(test_uuid, r)
                bstack1l111ll1ll1_opy_ = r.script
            self.logger.debug(bstack11ll1_opy_ (u"ࠧࡑࡧࡵࡪࡴࡸ࡭ࡪࡰࡪࠤࡸࡩࡡ࡯ࠢࡥࡩ࡫ࡵࡲࡦࠢࡶࡥࡻ࡯࡮ࡨࠢࡵࡩࡸࡻ࡬ࡵࡵࠪᒐ") + str(bstack1l111lll111_opy_))
            self.perform_scan(driver, name, framework_name=framework_name)
            if not bstack1l111ll1ll1_opy_:
                self.logger.debug(bstack11ll1_opy_ (u"ࠣࡲࡨࡶ࡫ࡵࡲ࡮ࡡࡶࡧࡦࡴ࠺ࠡ࡯࡬ࡷࡸ࡯࡮ࡨࠢࠪࡷࡦࡼࡥࡓࡧࡶࡹࡱࡺࡳࠨࠢࡶࡧࡷ࡯ࡰࡵࠢࡩࡳࡷࠦࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡱࡥࡲ࡫࠽ࠣᒑ") + str(framework_name) + bstack11ll1_opy_ (u"ࠤࠣࠦᒒ"))
                return
            bstack1lll1l1ll11_opy_ = bstack1lll111111l_opy_.bstack1lll1111lll_opy_(EVENTS.bstack1l11l111111_opy_.value)
            self.bstack1l11l1ll11l_opy_(driver, bstack1l111ll1ll1_opy_, bstack1l111lll111_opy_, framework_name)
            try:
                bstack1l11l11ll1l_opy_ = {
                    bstack11ll1_opy_ (u"ࠥࡶࡪࡷࡵࡦࡵࡷࠦᒓ"): {
                        bstack11ll1_opy_ (u"ࠦࡨࡵ࡭࡮ࡣࡱࡨࠧᒔ"): bstack11ll1_opy_ (u"ࠧࡇ࠱࠲࡛ࡢࡗࡆ࡜ࡅࡠࡔࡈࡗ࡚ࡒࡔࡔࠤᒕ"),
                    },
                    bstack11ll1_opy_ (u"ࠨࡲࡦࡵࡳࡳࡳࡹࡥࠣᒖ"): {
                        bstack11ll1_opy_ (u"ࠢࡣࡱࡧࡽࠧᒗ"): {
                            bstack11ll1_opy_ (u"ࠣ࡯ࡶ࡫ࠧᒘ"): bstack11ll1_opy_ (u"ࠤࡄࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠢࡷࡩࡸࡺࡩ࡯ࡩࠣࡪࡴࡸࠠࡵࡪ࡬ࡷࠥࡺࡥࡴࡶࠣࡧࡦࡹࡥࠡࡪࡤࡷࠥ࡫࡮ࡥࡧࡧ࠲ࠧᒙ"),
                            bstack11ll1_opy_ (u"ࠥࡷࡺࡩࡣࡦࡵࡶࠦᒚ"): True
                        }
                    }
                }
                self.bstack11ll111l1l_opy_.info(json.dumps(bstack1l11l11ll1l_opy_, separators=(bstack11ll1_opy_ (u"ࠫ࠱࠭ᒛ"), bstack11ll1_opy_ (u"ࠬࡀࠧᒜ"))))
            except Exception as bstack1l11lll1_opy_:
                self.logger.debug(bstack11ll1_opy_ (u"ࠨࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢ࡯ࡳ࡬ࠦࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࠦࡳࡢࡸࡨࠤࡷ࡫ࡳࡶ࡮ࡷࡷࠥࡪࡡࡵࡣ࠽ࠤࠧᒝ") + str(bstack1l11lll1_opy_) + bstack11ll1_opy_ (u"ࠢࠣᒞ"))
            self.logger.info(bstack11ll1_opy_ (u"ࠣࡃࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠡࡶࡨࡷࡹ࡯࡮ࡨࠢࡩࡳࡷࠦࡴࡩ࡫ࡶࠤࡹ࡫ࡳࡵࠢࡦࡥࡸ࡫ࠠࡩࡣࡶࠤࡪࡴࡤࡦࡦ࠱ࠦᒟ"))
            bstack1lll111111l_opy_.end(EVENTS.bstack1l11l111111_opy_.value, bstack1lll1l1ll11_opy_+bstack11ll1_opy_ (u"ࠤ࠽ࡷࡹࡧࡲࡵࠤᒠ"), bstack1lll1l1ll11_opy_+bstack11ll1_opy_ (u"ࠥ࠾ࡪࡴࡤࠣᒡ"), True, None, command=bstack11ll1_opy_ (u"ࠫࡸࡧࡶࡦࡔࡨࡷࡺࡲࡴࡴࠩᒢ"),test_name=name)
        except Exception as bstack1l111ll1l1l_opy_:
            self.logger.error(bstack11ll1_opy_ (u"ࠧࡇࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡸࡥࡴࡷ࡯ࡸࡸࠦࡣࡰࡷ࡯ࡨࠥࡴ࡯ࡵࠢࡥࡩࠥࡶࡲࡰࡥࡨࡷࡸ࡫ࡤࠡࡨࡲࡶࠥࡺࡨࡦࠢࡷࡩࡸࡺࠠࡤࡣࡶࡩ࠿ࠦࠢᒣ") + bstack11ll1_opy_ (u"ࠨࡳࡵࡴࠫࡴࡦࡺࡨࠪࠤᒤ") + bstack11ll1_opy_ (u"ࠢࠡࡇࡵࡶࡴࡸࠠ࠻ࠤᒥ") + str(bstack1l111ll1l1l_opy_))
            bstack1lll111111l_opy_.end(EVENTS.bstack1l11l111111_opy_.value, bstack1lll1l1ll11_opy_+bstack11ll1_opy_ (u"ࠣ࠼ࡶࡸࡦࡸࡴࠣᒦ"), bstack1lll1l1ll11_opy_+bstack11ll1_opy_ (u"ࠤ࠽ࡩࡳࡪࠢᒧ"), False, bstack1l111ll1l1l_opy_, command=bstack11ll1_opy_ (u"ࠪࡷࡦࡼࡥࡓࡧࡶࡹࡱࡺࡳࠨᒨ"),test_name=name)
    def bstack1l11l1ll11l_opy_(self, driver, bstack1l111ll1ll1_opy_, bstack1l111lll111_opy_, framework_name):
        if framework_name == bstack11ll1_opy_ (u"ࠫࡵࡲࡡࡺࡹࡵ࡭࡬࡮ࡴࠨᒩ"):
            self.bstack1l11l111ll1_opy_.bstack1l11ll11l11_opy_(driver, bstack1l111ll1ll1_opy_, bstack1l111lll111_opy_)
        else:
            self.logger.debug(driver.execute_async_script(bstack1l111ll1ll1_opy_, bstack1l111lll111_opy_))
    def _1l11l11lll1_opy_(self, instance: bstack1lll1l11l11_opy_, args: Tuple) -> list:
        bstack11ll1_opy_ (u"ࠧࠨࠢࡆࡺࡷࡶࡦࡩࡴࠡࡶࡤ࡫ࡸࠦࡢࡢࡵࡨࡨࠥࡵ࡮ࠡࡶ࡫ࡩࠥࡺࡥࡴࡶࠣࡪࡷࡧ࡭ࡦࡹࡲࡶࡰ࠴ࠢࠣࠤᒪ")
        if bstack11ll1_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹ࠳ࡢࡥࡦࠪᒫ") in instance.bstack1ll1ll1llll_opy_:
            return args[2].tags if hasattr(args[2], bstack11ll1_opy_ (u"ࠧࡵࡣࡪࡷࠬᒬ")) else []
        if hasattr(args[0], bstack11ll1_opy_ (u"ࠨࡱࡺࡲࡤࡳࡡࡳ࡭ࡨࡶࡸ࠭ᒭ")):
            return [marker.name for marker in args[0].own_markers]
        return []
    def bstack1l11l1l111l_opy_(self, tags, capabilities):
        return self.bstack1llll1111l_opy_(tags) and self.bstack11l1lll1_opy_(capabilities)