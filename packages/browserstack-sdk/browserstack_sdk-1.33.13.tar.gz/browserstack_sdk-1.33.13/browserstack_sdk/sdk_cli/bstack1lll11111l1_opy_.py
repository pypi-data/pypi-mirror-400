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
from browserstack_sdk.sdk_cli.bstack1ll1l1ll1ll_opy_ import bstack1ll1ll1l1ll_opy_
from browserstack_sdk.sdk_cli.bstack1llll11l1ll_opy_ import (
    bstack1llll1111l1_opy_,
    bstack1lll1lll1l1_opy_,
    bstack1llll1ll1ll_opy_,
)
from browserstack_sdk.sdk_cli.bstack1lll1l11l11_opy_ import bstack1lll11l111l_opy_
from typing import Tuple, Callable, Any
import grpc
from browserstack_sdk import sdk_pb2 as structs
from browserstack_sdk.sdk_cli.bstack1ll1l1ll1ll_opy_ import bstack1ll1ll1l1ll_opy_
from bstack_utils.measure import measure
from bstack_utils.constants import *
import traceback
import os
import time
class bstack1lll11llll1_opy_(bstack1ll1ll1l1ll_opy_):
    bstack1ll111lll1l_opy_ = False
    def __init__(self):
        super().__init__()
        bstack1lll11l111l_opy_.bstack1ll111ll111_opy_((bstack1llll1111l1_opy_.bstack1lll1ll1ll1_opy_, bstack1lll1lll1l1_opy_.PRE), self.bstack1l1ll1llll1_opy_)
    def is_enabled(self) -> bool:
        return True
    def bstack1l1ll1llll1_opy_(
        self,
        f: bstack1lll11l111l_opy_,
        driver: object,
        exec: Tuple[bstack1llll1ll1ll_opy_, str],
        bstack1llll1lll1l_opy_: Tuple[bstack1llll1111l1_opy_, bstack1lll1lll1l1_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        hub_url = f.hub_url(driver)
        if f.bstack1l1ll1ll111_opy_(hub_url):
            if not bstack1lll11llll1_opy_.bstack1ll111lll1l_opy_:
                self.logger.warning(bstack11l1l_opy_ (u"ࠧࡲ࡯ࡤࡣ࡯ࠤࡸ࡫࡬ࡧ࠯࡫ࡩࡦࡲࠠࡧ࡮ࡲࡻࠥࡪࡩࡴࡣࡥࡰࡪࡪࠠࡧࡱࡵࠤࡇࡸ࡯ࡸࡵࡨࡶࡘࡺࡡࡤ࡭ࠣ࡭ࡳ࡬ࡲࡢࠢࡶࡩࡸࡹࡩࡰࡰࡶࠤ࡭ࡻࡢࡠࡷࡵࡰࡂࠨኹ") + str(hub_url) + bstack11l1l_opy_ (u"ࠨࠢኺ"))
                bstack1lll11llll1_opy_.bstack1ll111lll1l_opy_ = True
            return
        command_name = f.bstack1ll111111l1_opy_(*args)
        bstack1l1ll1lll11_opy_ = f.bstack1l1lll1111l_opy_(*args)
        if command_name and command_name.lower() == bstack11l1l_opy_ (u"ࠢࡧ࡫ࡱࡨࡪࡲࡥ࡮ࡧࡱࡸࠧኻ") and bstack1l1ll1lll11_opy_:
            framework_session_id = f.session_id(driver)
            locator_type, locator_value = bstack1l1ll1lll11_opy_.get(bstack11l1l_opy_ (u"ࠣࡷࡶ࡭ࡳ࡭ࠢኼ"), None), bstack1l1ll1lll11_opy_.get(bstack11l1l_opy_ (u"ࠤࡹࡥࡱࡻࡥࠣኽ"), None)
            if not framework_session_id or not locator_type or not locator_value:
                self.logger.warning(bstack11l1l_opy_ (u"ࠥࡿࡨࡵ࡭࡮ࡣࡱࡨࡤࡴࡡ࡮ࡧࢀ࠾ࠥࡳࡩࡴࡵ࡬ࡲ࡬ࠦࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡶࡩࡸࡹࡩࡰࡰࡢ࡭ࡩࠦ࡯ࡳࠢࡤࡶ࡬ࡹ࠮ࡶࡵ࡬ࡲ࡬ࡃࡻ࡭ࡱࡦࡥࡹࡵࡲࡠࡶࡼࡴࡪࢃࠠࡰࡴࠣࡥࡷ࡭ࡳ࠯ࡸࡤࡰࡺ࡫࠽ࠣኾ") + str(locator_value) + bstack11l1l_opy_ (u"ࠦࠧ኿"))
                return
            def bstack1llll1ll111_opy_(driver, bstack1l1lll11111_opy_, *args, **kwargs):
                from selenium.common.exceptions import NoSuchElementException
                try:
                    result = bstack1l1lll11111_opy_(driver, *args, **kwargs)
                    response = self.bstack1l1ll1ll11l_opy_(
                        framework_session_id=framework_session_id,
                        is_success=True,
                        locator_type=locator_type,
                        locator_value=locator_value,
                    )
                    if response and response.execute_script:
                        driver.execute_script(response.execute_script)
                        self.logger.info(bstack11l1l_opy_ (u"ࠧࡹࡵࡤࡥࡨࡷࡸ࠳ࡳࡤࡴ࡬ࡴࡹࡀࠠ࡭ࡱࡦࡥࡹࡵࡲࡠࡶࡼࡴࡪࡃࡻ࡭ࡱࡦࡥࡹࡵࡲࡠࡶࡼࡴࡪࢃࠠ࡭ࡱࡦࡥࡹࡵࡲࡠࡸࡤࡰࡺ࡫࠽ࠣዀ") + str(locator_value) + bstack11l1l_opy_ (u"ࠨࠢ዁"))
                    else:
                        self.logger.warning(bstack11l1l_opy_ (u"ࠢࡴࡷࡦࡧࡪࡹࡳ࠮ࡰࡲ࠱ࡸࡩࡲࡪࡲࡷ࠾ࠥࡲ࡯ࡤࡣࡷࡳࡷࡥࡴࡺࡲࡨࡁࢀࡲ࡯ࡤࡣࡷࡳࡷࡥࡴࡺࡲࡨࢁࠥࡲ࡯ࡤࡣࡷࡳࡷࡥࡶࡢ࡮ࡸࡩࡂࢁ࡬ࡰࡥࡤࡸࡴࡸ࡟ࡷࡣ࡯ࡹࡪࢃࠠࡳࡧࡶࡴࡴࡴࡳࡦ࠿ࠥዂ") + str(response) + bstack11l1l_opy_ (u"ࠣࠤዃ"))
                    return result
                except NoSuchElementException as e:
                    locator = (locator_type, locator_value)
                    return self.__1l1ll1lll1l_opy_(
                        driver, bstack1l1lll11111_opy_, e, framework_session_id, locator, *args, **kwargs
                    )
            bstack1llll1ll111_opy_.__name__ = command_name
            return bstack1llll1ll111_opy_
    def __1l1ll1lll1l_opy_(
        self,
        driver,
        bstack1l1lll11111_opy_: Callable,
        exception,
        framework_session_id: str,
        locator: Tuple[str, str],
        *args,
        **kwargs,
    ):
        try:
            locator_type, locator_value = locator
            response = self.bstack1l1ll1ll11l_opy_(
                framework_session_id=framework_session_id,
                is_success=False,
                locator_type=locator_type,
                locator_value=locator_value,
            )
            if response and response.execute_script:
                driver.execute_script(response.execute_script)
                self.logger.info(bstack11l1l_opy_ (u"ࠤࡩࡥ࡮ࡲࡵࡳࡧ࠰࡬ࡪࡧ࡬ࡪࡰࡪ࠱ࡹࡸࡩࡨࡩࡨࡶࡪࡪ࠺ࠡ࡮ࡲࡧࡦࡺ࡯ࡳࡡࡷࡽࡵ࡫࠽ࡼ࡮ࡲࡧࡦࡺ࡯ࡳࡡࡷࡽࡵ࡫ࡽࠡ࡮ࡲࡧࡦࡺ࡯ࡳࡡࡹࡥࡱࡻࡥ࠾ࠤዄ") + str(locator_value) + bstack11l1l_opy_ (u"ࠥࠦዅ"))
                bstack1l1lll111l1_opy_ = self.bstack1l1ll1ll1ll_opy_(
                    framework_session_id=framework_session_id,
                    locator_type=locator_type,
                )
                self.logger.info(bstack11l1l_opy_ (u"ࠦ࡫ࡧࡩ࡭ࡷࡵࡩ࠲࡮ࡥࡢ࡮࡬ࡲ࡬࠳ࡲࡦࡵࡸࡰࡹࡀࠠ࡭ࡱࡦࡥࡹࡵࡲࡠࡶࡼࡴࡪࡃࡻ࡭ࡱࡦࡥࡹࡵࡲࡠࡶࡼࡴࡪࢃࠠ࡭ࡱࡦࡥࡹࡵࡲࡠࡸࡤࡰࡺ࡫࠽ࡼ࡮ࡲࡧࡦࡺ࡯ࡳࡡࡹࡥࡱࡻࡥࡾࠢ࡫ࡩࡦࡲࡩ࡯ࡩࡢࡶࡪࡹࡵ࡭ࡶࡀࠦ዆") + str(bstack1l1lll111l1_opy_) + bstack11l1l_opy_ (u"ࠧࠨ዇"))
                if bstack1l1lll111l1_opy_.success and args and len(args) > 1:
                    args[1].update(
                        {
                            bstack11l1l_opy_ (u"ࠨࡵࡴ࡫ࡱ࡫ࠧወ"): bstack1l1lll111l1_opy_.locator_type,
                            bstack11l1l_opy_ (u"ࠢࡷࡣ࡯ࡹࡪࠨዉ"): bstack1l1lll111l1_opy_.locator_value,
                        }
                    )
                    return bstack1l1lll11111_opy_(driver, *args, **kwargs)
                elif os.environ.get(bstack11l1l_opy_ (u"ࠣࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡂࡋࡢࡈࡊࡈࡕࡈࠤዊ"), False):
                    self.logger.info(bstack1ll1l11l1ll_opy_ (u"ࠤࡩࡥ࡮ࡲࡵࡳࡧ࠰࡬ࡪࡧ࡬ࡪࡰࡪ࠱ࡷ࡫ࡳࡶ࡮ࡷ࠱ࡲ࡯ࡳࡴ࡫ࡱ࡫࠿ࠦࡳ࡭ࡧࡨࡴ࠭࠹࠰ࠪࠢ࡯ࡩࡹࡺࡩ࡯ࡩࠣࡽࡴࡻࠠࡪࡰࡶࡴࡪࡩࡴࠡࡶ࡫ࡩࠥࡨࡲࡰࡹࡶࡩࡷࠦࡥࡹࡶࡨࡲࡸ࡯࡯࡯ࠢ࡯ࡳ࡬ࡹࠢዋ"))
                    time.sleep(300)
            else:
                self.logger.warning(bstack11l1l_opy_ (u"ࠥࡪࡦ࡯࡬ࡶࡴࡨ࠱ࡳࡵ࠭ࡴࡥࡵ࡭ࡵࡺ࠺ࠡ࡮ࡲࡧࡦࡺ࡯ࡳࡡࡷࡽࡵ࡫࠽ࡼ࡮ࡲࡧࡦࡺ࡯ࡳࡡࡷࡽࡵ࡫ࡽࠡ࡮ࡲࡧࡦࡺ࡯ࡳࡡࡹࡥࡱࡻࡥ࠾ࡽ࡯ࡳࡨࡧࡴࡰࡴࡢࡺࡦࡲࡵࡦࡿࠣࡶࡪࡹࡰࡰࡰࡶࡩࡂࠨዌ") + str(response) + bstack11l1l_opy_ (u"ࠦࠧው"))
        except Exception as err:
            self.logger.warning(bstack11l1l_opy_ (u"ࠧ࡬ࡡࡪ࡮ࡸࡶࡪ࠳ࡨࡦࡣ࡯࡭ࡳ࡭࠭ࡳࡧࡶࡹࡱࡺ࠺ࠡࡧࡵࡶࡴࡸ࠺ࠡࠤዎ") + str(err) + bstack11l1l_opy_ (u"ࠨࠢዏ"))
        raise exception
    @measure(event_name=EVENTS.bstack1l1ll1ll1l1_opy_, stage=STAGE.bstack1lll1l11l_opy_)
    def bstack1l1ll1ll11l_opy_(
        self,
        framework_session_id: str,
        is_success: bool,
        locator_type: str,
        locator_value: str,
        platform_index=bstack11l1l_opy_ (u"ࠢ࠱ࠤዐ"),
    ):
        self.bstack1ll11111lll_opy_()
        req = structs.AISelfHealStepRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.framework_session_id = framework_session_id
        req.is_success = is_success
        req.test_name = bstack11l1l_opy_ (u"ࠣࠤዑ")
        req.locator_type = locator_type
        req.locator_value = locator_value
        try:
            r = self.bstack1ll1ll11l11_opy_.AISelfHealStep(req)
            self.logger.info(bstack11l1l_opy_ (u"ࠤࡵࡩࡨ࡫ࡩࡷࡧࡧࠤ࡫ࡸ࡯࡮ࠢࡶࡩࡷࡼࡥࡳ࠼ࠣࠦዒ") + str(r) + bstack11l1l_opy_ (u"ࠥࠦዓ"))
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack11l1l_opy_ (u"ࠦࡷࡶࡣ࠮ࡧࡵࡶࡴࡸ࠺ࠡࠤዔ") + str(e) + bstack11l1l_opy_ (u"ࠧࠨዕ"))
            traceback.print_exc()
            raise e
    @measure(event_name=EVENTS.bstack1l1ll1lllll_opy_, stage=STAGE.bstack1lll1l11l_opy_)
    def bstack1l1ll1ll1ll_opy_(self, framework_session_id: str, locator_type: str, platform_index=bstack11l1l_opy_ (u"ࠨ࠰ࠣዖ")):
        self.bstack1ll11111lll_opy_()
        req = structs.AISelfHealGetRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.framework_session_id = framework_session_id
        req.locator_type = locator_type
        try:
            r = self.bstack1ll1ll11l11_opy_.AISelfHealGetResult(req)
            self.logger.info(bstack11l1l_opy_ (u"ࠢࡳࡧࡦࡩ࡮ࡼࡥࡥࠢࡩࡶࡴࡳࠠࡴࡧࡵࡺࡪࡸ࠺ࠡࠤ዗") + str(r) + bstack11l1l_opy_ (u"ࠣࠤዘ"))
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack11l1l_opy_ (u"ࠤࡵࡴࡨ࠳ࡥࡳࡴࡲࡶ࠿ࠦࠢዙ") + str(e) + bstack11l1l_opy_ (u"ࠥࠦዚ"))
            traceback.print_exc()
            raise e