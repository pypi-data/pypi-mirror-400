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
from browserstack_sdk.sdk_cli.bstack1l1ll111111_opy_ import bstack1l1l1l111ll_opy_
from browserstack_sdk.sdk_cli.bstack1ll11l1l1l1_opy_ import (
    bstack1ll11lllll1_opy_,
    bstack1ll11lll1ll_opy_,
    bstack1ll1l1ll1l1_opy_,
)
from browserstack_sdk.sdk_cli.bstack1ll11l1lll1_opy_ import bstack1ll11ll1lll_opy_
from typing import Tuple, Callable, Any
import grpc
from browserstack_sdk import sdk_pb2 as structs
from browserstack_sdk.sdk_cli.bstack1l1ll111111_opy_ import bstack1l1l1l111ll_opy_
from bstack_utils.measure import measure
from bstack_utils.constants import *
import traceback
import os
import time
class bstack1l1l11ll111_opy_(bstack1l1l1l111ll_opy_):
    bstack1l11ll111l1_opy_ = False
    def __init__(self):
        super().__init__()
        bstack1ll11ll1lll_opy_.bstack1ll1l11111l_opy_((bstack1ll11lllll1_opy_.bstack1ll11l1l1ll_opy_, bstack1ll11lll1ll_opy_.PRE), self.bstack1l111l1llll_opy_)
    def is_enabled(self) -> bool:
        return True
    def bstack1l111l1llll_opy_(
        self,
        f: bstack1ll11ll1lll_opy_,
        driver: object,
        exec: Tuple[bstack1ll1l1ll1l1_opy_, str],
        bstack1lll1lll111_opy_: Tuple[bstack1ll11lllll1_opy_, bstack1ll11lll1ll_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        hub_url = f.hub_url(driver)
        if f.bstack1ll11l1l11l_opy_(hub_url):
            if not bstack1l1l11ll111_opy_.bstack1l11ll111l1_opy_:
                self.logger.warning(bstack11ll1_opy_ (u"ࠤ࡯ࡳࡨࡧ࡬ࠡࡵࡨࡰ࡫࠳ࡨࡦࡣ࡯ࠤ࡫ࡲ࡯ࡸࠢࡧ࡭ࡸࡧࡢ࡭ࡧࡧࠤ࡫ࡵࡲࠡࡄࡵࡳࡼࡹࡥࡳࡕࡷࡥࡨࡱࠠࡪࡰࡩࡶࡦࠦࡳࡦࡵࡶ࡭ࡴࡴࡳࠡࡪࡸࡦࡤࡻࡲ࡭࠿ࠥᒮ") + str(hub_url) + bstack11ll1_opy_ (u"ࠥࠦᒯ"))
                bstack1l1l11ll111_opy_.bstack1l11ll111l1_opy_ = True
            return
        command_name = f.bstack1ll11l1l111_opy_(*args)
        bstack1ll1l1l11ll_opy_ = f.bstack1ll1l111l1l_opy_(*args)
        if command_name and command_name.lower() == bstack11ll1_opy_ (u"ࠦ࡫࡯࡮ࡥࡧ࡯ࡩࡲ࡫࡮ࡵࠤᒰ") and bstack1ll1l1l11ll_opy_:
            framework_session_id = f.session_id(driver)
            locator_type, locator_value = bstack1ll1l1l11ll_opy_.get(bstack11ll1_opy_ (u"ࠧࡻࡳࡪࡰࡪࠦᒱ"), None), bstack1ll1l1l11ll_opy_.get(bstack11ll1_opy_ (u"ࠨࡶࡢ࡮ࡸࡩࠧᒲ"), None)
            if not framework_session_id or not locator_type or not locator_value:
                self.logger.warning(bstack11ll1_opy_ (u"ࠢࡼࡥࡲࡱࡲࡧ࡮ࡥࡡࡱࡥࡲ࡫ࡽ࠻ࠢࡰ࡭ࡸࡹࡩ࡯ࡩࠣࡪࡷࡧ࡭ࡦࡹࡲࡶࡰࡥࡳࡦࡵࡶ࡭ࡴࡴ࡟ࡪࡦࠣࡳࡷࠦࡡࡳࡩࡶ࠲ࡺࡹࡩ࡯ࡩࡀࡿࡱࡵࡣࡢࡶࡲࡶࡤࡺࡹࡱࡧࢀࠤࡴࡸࠠࡢࡴࡪࡷ࠳ࡼࡡ࡭ࡷࡨࡁࠧᒳ") + str(locator_value) + bstack11ll1_opy_ (u"ࠣࠤᒴ"))
                return
            def bstack1l1ll1lllll_opy_(driver, bstack1l111l1ll1l_opy_, *args, **kwargs):
                from selenium.common.exceptions import NoSuchElementException
                try:
                    result = bstack1l111l1ll1l_opy_(driver, *args, **kwargs)
                    response = self.bstack1l111l1l11l_opy_(
                        framework_session_id=framework_session_id,
                        is_success=True,
                        locator_type=locator_type,
                        locator_value=locator_value,
                    )
                    if response and response.execute_script:
                        driver.execute_script(response.execute_script)
                        self.logger.info(bstack11ll1_opy_ (u"ࠤࡶࡹࡨࡩࡥࡴࡵ࠰ࡷࡨࡸࡩࡱࡶ࠽ࠤࡱࡵࡣࡢࡶࡲࡶࡤࡺࡹࡱࡧࡀࡿࡱࡵࡣࡢࡶࡲࡶࡤࡺࡹࡱࡧࢀࠤࡱࡵࡣࡢࡶࡲࡶࡤࡼࡡ࡭ࡷࡨࡁࠧᒵ") + str(locator_value) + bstack11ll1_opy_ (u"ࠥࠦᒶ"))
                    else:
                        self.logger.warning(bstack11ll1_opy_ (u"ࠦࡸࡻࡣࡤࡧࡶࡷ࠲ࡴ࡯࠮ࡵࡦࡶ࡮ࡶࡴ࠻ࠢ࡯ࡳࡨࡧࡴࡰࡴࡢࡸࡾࡶࡥ࠾ࡽ࡯ࡳࡨࡧࡴࡰࡴࡢࡸࡾࡶࡥࡾࠢ࡯ࡳࡨࡧࡴࡰࡴࡢࡺࡦࡲࡵࡦ࠿ࡾࡰࡴࡩࡡࡵࡱࡵࡣࡻࡧ࡬ࡶࡧࢀࠤࡷ࡫ࡳࡱࡱࡱࡷࡪࡃࠢᒷ") + str(response) + bstack11ll1_opy_ (u"ࠧࠨᒸ"))
                    return result
                except NoSuchElementException as e:
                    locator = (locator_type, locator_value)
                    return self.__1l111l1ll11_opy_(
                        driver, bstack1l111l1ll1l_opy_, e, framework_session_id, locator, *args, **kwargs
                    )
            bstack1l1ll1lllll_opy_.__name__ = command_name
            return bstack1l1ll1lllll_opy_
    def __1l111l1ll11_opy_(
        self,
        driver,
        bstack1l111l1ll1l_opy_: Callable,
        exception,
        framework_session_id: str,
        locator: Tuple[str, str],
        *args,
        **kwargs,
    ):
        try:
            locator_type, locator_value = locator
            response = self.bstack1l111l1l11l_opy_(
                framework_session_id=framework_session_id,
                is_success=False,
                locator_type=locator_type,
                locator_value=locator_value,
            )
            if response and response.execute_script:
                driver.execute_script(response.execute_script)
                self.logger.info(bstack11ll1_opy_ (u"ࠨࡦࡢ࡫࡯ࡹࡷ࡫࠭ࡩࡧࡤࡰ࡮ࡴࡧ࠮ࡶࡵ࡭࡬࡭ࡥࡳࡧࡧ࠾ࠥࡲ࡯ࡤࡣࡷࡳࡷࡥࡴࡺࡲࡨࡁࢀࡲ࡯ࡤࡣࡷࡳࡷࡥࡴࡺࡲࡨࢁࠥࡲ࡯ࡤࡣࡷࡳࡷࡥࡶࡢ࡮ࡸࡩࡂࠨᒹ") + str(locator_value) + bstack11ll1_opy_ (u"ࠢࠣᒺ"))
                bstack1l111l1l1ll_opy_ = self.bstack1l111l1l1l1_opy_(
                    framework_session_id=framework_session_id,
                    locator_type=locator_type,
                )
                self.logger.info(bstack11ll1_opy_ (u"ࠣࡨࡤ࡭ࡱࡻࡲࡦ࠯࡫ࡩࡦࡲࡩ࡯ࡩ࠰ࡶࡪࡹࡵ࡭ࡶ࠽ࠤࡱࡵࡣࡢࡶࡲࡶࡤࡺࡹࡱࡧࡀࡿࡱࡵࡣࡢࡶࡲࡶࡤࡺࡹࡱࡧࢀࠤࡱࡵࡣࡢࡶࡲࡶࡤࡼࡡ࡭ࡷࡨࡁࢀࡲ࡯ࡤࡣࡷࡳࡷࡥࡶࡢ࡮ࡸࡩࢂࠦࡨࡦࡣ࡯࡭ࡳ࡭࡟ࡳࡧࡶࡹࡱࡺ࠽ࠣᒻ") + str(bstack1l111l1l1ll_opy_) + bstack11ll1_opy_ (u"ࠤࠥᒼ"))
                if bstack1l111l1l1ll_opy_.success and args and len(args) > 1:
                    args[1].update(
                        {
                            bstack11ll1_opy_ (u"ࠥࡹࡸ࡯࡮ࡨࠤᒽ"): bstack1l111l1l1ll_opy_.locator_type,
                            bstack11ll1_opy_ (u"ࠦࡻࡧ࡬ࡶࡧࠥᒾ"): bstack1l111l1l1ll_opy_.locator_value,
                        }
                    )
                    return bstack1l111l1ll1l_opy_(driver, *args, **kwargs)
                elif os.environ.get(bstack11ll1_opy_ (u"ࠧࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡆࡏ࡟ࡅࡇࡅ࡙ࡌࠨᒿ"), False):
                    self.logger.info(bstack1l1ll111l1l_opy_ (u"ࠨࡦࡢ࡫࡯ࡹࡷ࡫࠭ࡩࡧࡤࡰ࡮ࡴࡧ࠮ࡴࡨࡷࡺࡲࡴ࠮࡯࡬ࡷࡸ࡯࡮ࡨ࠼ࠣࡷࡱ࡫ࡥࡱࠪ࠶࠴࠮ࠦ࡬ࡦࡶࡷ࡭ࡳ࡭ࠠࡺࡱࡸࠤ࡮ࡴࡳࡱࡧࡦࡸࠥࡺࡨࡦࠢࡥࡶࡴࡽࡳࡦࡴࠣࡩࡽࡺࡥ࡯ࡵ࡬ࡳࡳࠦ࡬ࡰࡩࡶࠦᓀ"))
                    time.sleep(300)
            else:
                self.logger.warning(bstack11ll1_opy_ (u"ࠢࡧࡣ࡬ࡰࡺࡸࡥ࠮ࡰࡲ࠱ࡸࡩࡲࡪࡲࡷ࠾ࠥࡲ࡯ࡤࡣࡷࡳࡷࡥࡴࡺࡲࡨࡁࢀࡲ࡯ࡤࡣࡷࡳࡷࡥࡴࡺࡲࡨࢁࠥࡲ࡯ࡤࡣࡷࡳࡷࡥࡶࡢ࡮ࡸࡩࡂࢁ࡬ࡰࡥࡤࡸࡴࡸ࡟ࡷࡣ࡯ࡹࡪࢃࠠࡳࡧࡶࡴࡴࡴࡳࡦ࠿ࠥᓁ") + str(response) + bstack11ll1_opy_ (u"ࠣࠤᓂ"))
        except Exception as err:
            self.logger.warning(bstack11ll1_opy_ (u"ࠤࡩࡥ࡮ࡲࡵࡳࡧ࠰࡬ࡪࡧ࡬ࡪࡰࡪ࠱ࡷ࡫ࡳࡶ࡮ࡷ࠾ࠥ࡫ࡲࡳࡱࡵ࠾ࠥࠨᓃ") + str(err) + bstack11ll1_opy_ (u"ࠥࠦᓄ"))
        raise exception
    @measure(event_name=EVENTS.bstack1l111ll1111_opy_, stage=STAGE.bstack11l1llll1_opy_)
    def bstack1l111l1l11l_opy_(
        self,
        framework_session_id: str,
        is_success: bool,
        locator_type: str,
        locator_value: str,
        platform_index=bstack11ll1_opy_ (u"ࠦ࠵ࠨᓅ"),
    ):
        self.bstack1ll111111l1_opy_()
        req = structs.AISelfHealStepRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.framework_session_id = framework_session_id
        req.is_success = is_success
        req.test_name = bstack11ll1_opy_ (u"ࠧࠨᓆ")
        req.locator_type = locator_type
        req.locator_value = locator_value
        try:
            r = self.bstack1lllll11ll1_opy_.AISelfHealStep(req)
            self.logger.info(bstack11ll1_opy_ (u"ࠨࡲࡦࡥࡨ࡭ࡻ࡫ࡤࠡࡨࡵࡳࡲࠦࡳࡦࡴࡹࡩࡷࡀࠠࠣᓇ") + str(r) + bstack11ll1_opy_ (u"ࠢࠣᓈ"))
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack11ll1_opy_ (u"ࠣࡴࡳࡧ࠲࡫ࡲࡳࡱࡵ࠾ࠥࠨᓉ") + str(e) + bstack11ll1_opy_ (u"ࠤࠥᓊ"))
            traceback.print_exc()
            raise e
    @measure(event_name=EVENTS.bstack1l111l1lll1_opy_, stage=STAGE.bstack11l1llll1_opy_)
    def bstack1l111l1l1l1_opy_(self, framework_session_id: str, locator_type: str, platform_index=bstack11ll1_opy_ (u"ࠥ࠴ࠧᓋ")):
        self.bstack1ll111111l1_opy_()
        req = structs.AISelfHealGetRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.framework_session_id = framework_session_id
        req.locator_type = locator_type
        try:
            r = self.bstack1lllll11ll1_opy_.AISelfHealGetResult(req)
            self.logger.info(bstack11ll1_opy_ (u"ࠦࡷ࡫ࡣࡦ࡫ࡹࡩࡩࠦࡦࡳࡱࡰࠤࡸ࡫ࡲࡷࡧࡵ࠾ࠥࠨᓌ") + str(r) + bstack11ll1_opy_ (u"ࠧࠨᓍ"))
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack11ll1_opy_ (u"ࠨࡲࡱࡥ࠰ࡩࡷࡸ࡯ࡳ࠼ࠣࠦᓎ") + str(e) + bstack11ll1_opy_ (u"ࠢࠣᓏ"))
            traceback.print_exc()
            raise e