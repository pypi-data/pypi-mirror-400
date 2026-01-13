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
import os
import grpc
from browserstack_sdk import sdk_pb2 as structs
from packaging import version
import traceback
from browserstack_sdk.sdk_cli.bstack1l1ll111111_opy_ import bstack1l1l1l111ll_opy_
from browserstack_sdk.sdk_cli.bstack1ll11l1l1l1_opy_ import (
    bstack1ll11lllll1_opy_,
    bstack1ll11lll1ll_opy_,
    bstack1ll1l1ll1l1_opy_,
)
from browserstack_sdk.sdk_cli.bstack1ll11l1lll1_opy_ import bstack1ll11ll1lll_opy_
from datetime import datetime
from typing import Tuple, Any
from bstack_utils.messages import bstack1llll1111_opy_
from bstack_utils.measure import measure
from bstack_utils.constants import *
import threading
import os
from bstack_utils.bstack11l11l11ll_opy_ import bstack1lll111111l_opy_
class bstack1l1l1ll1111_opy_(bstack1l1l1l111ll_opy_):
    bstack11lll1111ll_opy_ = bstack11ll1_opy_ (u"ࠦࡷ࡫ࡧࡪࡵࡷࡩࡷࡥࡩ࡯࡫ࡷࠦᗲ")
    bstack11lll1l111l_opy_ = bstack11ll1_opy_ (u"ࠧࡸࡥࡨ࡫ࡶࡸࡪࡸ࡟ࡴࡶࡤࡶࡹࠨᗳ")
    bstack11ll1llll1l_opy_ = bstack11ll1_opy_ (u"ࠨࡲࡦࡩ࡬ࡷࡹ࡫ࡲࡠࡵࡷࡳࡵࠨᗴ")
    def __init__(self, bstack1l11lllll11_opy_):
        super().__init__()
        bstack1ll11ll1lll_opy_.bstack1ll1l11111l_opy_((bstack1ll11lllll1_opy_.bstack1ll11l1ll1l_opy_, bstack1ll11lll1ll_opy_.PRE), self.bstack11lll11llll_opy_)
        bstack1ll11ll1lll_opy_.bstack1ll1l11111l_opy_((bstack1ll11lllll1_opy_.bstack1ll11l1l1ll_opy_, bstack1ll11lll1ll_opy_.PRE), self.bstack1l111l1llll_opy_)
        bstack1ll11ll1lll_opy_.bstack1ll1l11111l_opy_((bstack1ll11lllll1_opy_.bstack1ll11l1l1ll_opy_, bstack1ll11lll1ll_opy_.POST), self.bstack11lll111ll1_opy_)
        bstack1ll11ll1lll_opy_.bstack1ll1l11111l_opy_((bstack1ll11lllll1_opy_.bstack1ll11l1l1ll_opy_, bstack1ll11lll1ll_opy_.POST), self.bstack11lll11lll1_opy_)
        bstack1ll11ll1lll_opy_.bstack1ll1l11111l_opy_((bstack1ll11lllll1_opy_.QUIT, bstack1ll11lll1ll_opy_.POST), self.bstack11lll111l11_opy_)
    def is_enabled(self) -> bool:
        return True
    def bstack11lll11llll_opy_(
        self,
        f: bstack1ll11ll1lll_opy_,
        driver: object,
        exec: Tuple[bstack1ll1l1ll1l1_opy_, str],
        bstack1lll1lll111_opy_: Tuple[bstack1ll11lllll1_opy_, bstack1ll11lll1ll_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if method_name != bstack11ll1_opy_ (u"ࠢࡠࡡ࡬ࡲ࡮ࡺ࡟ࡠࠤᗵ"):
            return
        def wrapped(driver, init, *args, **kwargs):
            url = None
            try:
                if isinstance(kwargs.get(bstack11ll1_opy_ (u"ࠣࡥࡲࡱࡲࡧ࡮ࡥࡡࡨࡼࡪࡩࡵࡵࡱࡵࠦᗶ")), str):
                    url = kwargs.get(bstack11ll1_opy_ (u"ࠤࡦࡳࡲࡳࡡ࡯ࡦࡢࡩࡽ࡫ࡣࡶࡶࡲࡶࠧᗷ"))
                elif hasattr(kwargs.get(bstack11ll1_opy_ (u"ࠥࡧࡴࡳ࡭ࡢࡰࡧࡣࡪࡾࡥࡤࡷࡷࡳࡷࠨᗸ")), bstack11ll1_opy_ (u"ࠫࡤࡩ࡬ࡪࡧࡱࡸࡤࡩ࡯࡯ࡨ࡬࡫ࠬᗹ")):
                    url = kwargs.get(bstack11ll1_opy_ (u"ࠧࡩ࡯࡮࡯ࡤࡲࡩࡥࡥࡹࡧࡦࡹࡹࡵࡲࠣᗺ"))._client_config.remote_server_addr
                else:
                    url = kwargs.get(bstack11ll1_opy_ (u"ࠨࡣࡰ࡯ࡰࡥࡳࡪ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳࠤᗻ"))._url
            except Exception as e:
                url = bstack11ll1_opy_ (u"ࠧࠨᗼ")
                self.logger.error(bstack11ll1_opy_ (u"ࠣࡇࡵࡶࡴࡸࠠࡸࡪ࡬ࡰࡪࠦࡧࡦࡶࡷ࡭ࡳ࡭ࠠࡶࡴ࡯ࠤ࡫ࡸ࡯࡮ࠢࡧࡶ࡮ࡼࡥࡳ࠼ࠣࡿࢂࠨᗽ").format(e))
            self.logger.info(bstack11ll1_opy_ (u"ࠤࡕࡩࡲࡵࡴࡦࠢࡖࡩࡷࡼࡥࡳࠢࡄࡨࡩࡸࡥࡴࡵࠣࡦࡪ࡯࡮ࡨࠢࡳࡥࡸࡹࡥࡥࠢࡤࡷࠥࡀࠠࡼࡿࠥᗾ").format(str(url)))
            self.bstack11ll1llll11_opy_(instance, url, f, kwargs)
            self.logger.info(bstack11ll1_opy_ (u"ࠥࡨࡷ࡯ࡶࡦࡴ࠱ࡿࡲ࡫ࡴࡩࡱࡧࡣࡳࡧ࡭ࡦࡿࠣࡴࡱࡧࡴࡧࡱࡵࡱࡤ࡯࡮ࡥࡧࡻࡁࢀࡶ࡬ࡢࡶࡩࡳࡷࡳ࡟ࡪࡰࡧࡩࡽࢃ࠺ࠡࡣࡵ࡫ࡸࡃࡻࡢࡴࡪࡷࢂࠦ࡫ࡸࡣࡵ࡫ࡸࡃࡻ࡬ࡹࡤࡶ࡬ࡹࡽࠣᗿ").format(method_name=method_name, platform_index=f.platform_index, args=args, kwargs=kwargs))
            threading.current_thread().bstackSessionDriver = driver
            return init(driver, *args, **kwargs)
        return wrapped
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
        instance, method_name = exec
        if f.bstack1ll1llll11l_opy_(instance, bstack1l1l1ll1111_opy_.bstack11lll1111ll_opy_, False):
            return
        if not f.bstack1lll1ll1ll1_opy_(instance, bstack1ll11ll1lll_opy_.bstack1lll11l1l1l_opy_):
            return
        platform_index = f.bstack1ll1llll11l_opy_(instance, bstack1ll11ll1lll_opy_.bstack1lll11l1l1l_opy_)
        if f.bstack1ll1l11lll1_opy_(method_name, *args) and len(args) > 1:
            bstack1ll11l1l1l_opy_ = datetime.now()
            hub_url = bstack1ll11ll1lll_opy_.hub_url(driver)
            self.logger.warning(bstack11ll1_opy_ (u"ࠦ࡭ࡻࡢࡠࡷࡵࡰࡂࠨᘀ") + str(hub_url) + bstack11ll1_opy_ (u"ࠧࠨᘁ"))
            bstack11lll11111l_opy_ = args[1][bstack11ll1_opy_ (u"ࠨࡣࡢࡲࡤࡦ࡮ࡲࡩࡵ࡫ࡨࡷࠧᘂ")] if isinstance(args[1], dict) and bstack11ll1_opy_ (u"ࠢࡤࡣࡳࡥࡧ࡯࡬ࡪࡶ࡬ࡩࡸࠨᘃ") in args[1] else None
            bstack11ll1llllll_opy_ = bstack11ll1_opy_ (u"ࠣࡣ࡯ࡻࡦࡿࡳࡎࡣࡷࡧ࡭ࠨᘄ")
            if isinstance(bstack11lll11111l_opy_, dict):
                bstack1ll11l1l1l_opy_ = datetime.now()
                r = self.bstack11lll11ll1l_opy_(
                    instance.ref(),
                    platform_index,
                    f.framework_name,
                    f.framework_version,
                    hub_url
                )
                instance.bstack1lll1lll1_opy_(bstack11ll1_opy_ (u"ࠤࡪࡶࡵࡩ࠺ࡳࡧࡪ࡭ࡸࡺࡥࡳࡡ࡬ࡲ࡮ࡺࠢᘅ"), datetime.now() - bstack1ll11l1l1l_opy_)
                try:
                    if not r.success:
                        self.logger.info(bstack11ll1_opy_ (u"ࠥࡷࡴࡳࡥࡵࡪ࡬ࡲ࡬ࠦࡷࡦࡰࡷࠤࡼࡸ࡯࡯ࡩ࠽ࠤࠧᘆ") + str(r) + bstack11ll1_opy_ (u"ࠦࠧᘇ"))
                        return
                    if r.hub_url:
                        f.bstack1ll1l11ll11_opy_(instance, driver, r.hub_url)
                        f.bstack1lll111ll11_opy_(instance, bstack1l1l1ll1111_opy_.bstack11lll1111ll_opy_, True)
                except Exception as e:
                    self.logger.error(bstack11ll1_opy_ (u"ࠧ࡫ࡲࡳࡱࡵࠦᘈ"), e)
    def bstack11lll111ll1_opy_(
        self,
        f: bstack1ll11ll1lll_opy_,
        driver: object,
        exec: Tuple[bstack1ll1l1ll1l1_opy_, str],
        bstack1lll1lll111_opy_: Tuple[bstack1ll11lllll1_opy_, bstack1ll11lll1ll_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
            session_id = bstack1ll11ll1lll_opy_.session_id(driver)
            if session_id:
                bstack11lll11ll11_opy_ = bstack11ll1_opy_ (u"ࠨࡻࡾ࠼ࡶࡸࡦࡸࡴࠣᘉ").format(session_id)
                bstack1lll111111l_opy_.mark(bstack11lll11ll11_opy_)
    def bstack11lll11lll1_opy_(
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
        if f.bstack1ll1llll11l_opy_(instance, bstack1l1l1ll1111_opy_.bstack11lll1l111l_opy_, False):
            return
        ref = instance.ref()
        hub_url = bstack1ll11ll1lll_opy_.hub_url(driver)
        if not hub_url:
            self.logger.warning(bstack11ll1_opy_ (u"ࠢࡧࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡴࡦࡸࡳࡦࠢ࡫ࡹࡧࡥࡵࡳ࡮ࡀࠦᘊ") + str(hub_url) + bstack11ll1_opy_ (u"ࠣࠤᘋ"))
            return
        framework_session_id = bstack1ll11ll1lll_opy_.session_id(driver)
        if not framework_session_id:
            self.logger.warning(bstack11ll1_opy_ (u"ࠤࡩࡥ࡮ࡲࡥࡥࠢࡷࡳࠥࡶࡡࡳࡵࡨࠤ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟ࡴࡧࡶࡷ࡮ࡵ࡮ࡠ࡫ࡧࡁࠧᘌ") + str(framework_session_id) + bstack11ll1_opy_ (u"ࠥࠦᘍ"))
            return
        if bstack1ll11ll1lll_opy_.bstack1ll11llll1l_opy_(*args) == bstack1ll11ll1lll_opy_.bstack1ll1l1l1ll1_opy_:
            bstack11lll11l111_opy_ = bstack11ll1_opy_ (u"ࠦࢀࢃ࠺ࡦࡰࡧࠦᘎ").format(framework_session_id)
            bstack11lll11ll11_opy_ = bstack11ll1_opy_ (u"ࠧࢁࡽ࠻ࡵࡷࡥࡷࡺࠢᘏ").format(framework_session_id)
            bstack1lll111111l_opy_.end(
                label=bstack11ll1_opy_ (u"ࠨࡳࡥ࡭࠽ࡨࡷ࡯ࡶࡦࡴ࠽ࡴࡴࡹࡴ࠮࡫ࡱ࡭ࡹ࡯ࡡ࡭࡫ࡽࡥࡹ࡯࡯࡯ࠤᘐ"),
                start=bstack11lll11ll11_opy_,
                end=bstack11lll11l111_opy_,
                status=True,
                failure=None
            )
            bstack1ll11l1l1l_opy_ = datetime.now()
            r = self.bstack11lll11l1ll_opy_(
                ref,
                f.bstack1ll1llll11l_opy_(instance, bstack1ll11ll1lll_opy_.bstack1lll11l1l1l_opy_, 0),
                f.framework_name,
                f.framework_version,
                framework_session_id,
                hub_url,
            )
            instance.bstack1lll1lll1_opy_(bstack11ll1_opy_ (u"ࠢࡨࡴࡳࡧ࠿ࡸࡥࡨ࡫ࡶࡸࡪࡸ࡟ࡴࡶࡤࡶࡹࠨᘑ"), datetime.now() - bstack1ll11l1l1l_opy_)
            f.bstack1lll111ll11_opy_(instance, bstack1l1l1ll1111_opy_.bstack11lll1l111l_opy_, r.success)
    def bstack11lll111l11_opy_(
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
        if f.bstack1ll1llll11l_opy_(instance, bstack1l1l1ll1111_opy_.bstack11ll1llll1l_opy_, False):
            return
        ref = instance.ref()
        framework_session_id = bstack1ll11ll1lll_opy_.session_id(driver)
        hub_url = bstack1ll11ll1lll_opy_.hub_url(driver)
        bstack1ll11l1l1l_opy_ = datetime.now()
        r = self.bstack11lll111l1l_opy_(
            ref,
            f.bstack1ll1llll11l_opy_(instance, bstack1ll11ll1lll_opy_.bstack1lll11l1l1l_opy_, 0),
            f.framework_name,
            f.framework_version,
            framework_session_id,
            hub_url,
        )
        instance.bstack1lll1lll1_opy_(bstack11ll1_opy_ (u"ࠣࡩࡵࡴࡨࡀࡲࡦࡩ࡬ࡷࡹ࡫ࡲࡠࡵࡷࡳࡵࠨᘒ"), datetime.now() - bstack1ll11l1l1l_opy_)
        f.bstack1lll111ll11_opy_(instance, bstack1l1l1ll1111_opy_.bstack11ll1llll1l_opy_, r.success)
    @measure(event_name=EVENTS.bstack11llllll11_opy_, stage=STAGE.bstack11l1llll1_opy_)
    def bstack11llll1l1l1_opy_(self, platform_index: int, url: str, ref, user_input_params: bytes):
        req = structs.DriverInitRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.user_input_params = user_input_params
        req.ref = ref
        req.hub_url = url
        self.logger.debug(bstack11ll1_opy_ (u"ࠤࡵࡩ࡬࡯ࡳࡵࡧࡵࡣࡼ࡫ࡢࡥࡴ࡬ࡺࡪࡸ࡟ࡪࡰ࡬ࡸ࠿ࠦࠢᘓ") + str(req) + bstack11ll1_opy_ (u"ࠥࠦᘔ"))
        try:
            r = self.bstack1lllll11ll1_opy_.DriverInit(req)
            if not r.success:
                self.logger.debug(bstack11ll1_opy_ (u"ࠦࡷ࡫ࡣࡦ࡫ࡹࡩࡩࠦࡦࡳࡱࡰࠤࡸ࡫ࡲࡷࡧࡵ࠾ࠥࡹࡵࡤࡥࡨࡷࡸࡃࠢᘕ") + str(r.success) + bstack11ll1_opy_ (u"ࠧࠨᘖ"))
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack11ll1_opy_ (u"ࠨࡲࡱࡥ࠰ࡩࡷࡸ࡯ࡳ࠼ࠣࠦᘗ") + str(e) + bstack11ll1_opy_ (u"ࠢࠣᘘ"))
            traceback.print_exc()
            raise e
    @measure(event_name=EVENTS.bstack11lll1111l1_opy_, stage=STAGE.bstack11l1llll1_opy_)
    def bstack11lll11ll1l_opy_(
        self,
        ref: str,
        platform_index: int,
        framework_name: str,
        framework_version: str,
        hub_url: str
    ):
        self.bstack1ll111111l1_opy_()
        req = structs.AutomationFrameworkInitRequest()
        req.ref = ref
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.framework_name = framework_name
        req.framework_version = framework_version
        req.hub_url = hub_url
        self.logger.debug(bstack11ll1_opy_ (u"ࠣࡴࡨ࡫࡮ࡹࡴࡦࡴࡢ࡭ࡳ࡯ࡴ࠻ࠢࠥᘙ") + str(req) + bstack11ll1_opy_ (u"ࠤࠥᘚ"))
        try:
            r = self.bstack1lllll11ll1_opy_.AutomationFrameworkInit(req)
            if not r.success:
                self.logger.debug(bstack11ll1_opy_ (u"ࠥࡶࡪࡩࡥࡪࡸࡨࡨࠥ࡬ࡲࡰ࡯ࠣࡷࡪࡸࡶࡦࡴ࠽ࠤࡸࡻࡣࡤࡧࡶࡷࡂࠨᘛ") + str(r.success) + bstack11ll1_opy_ (u"ࠦࠧᘜ"))
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack11ll1_opy_ (u"ࠧࡸࡰࡤ࠯ࡨࡶࡷࡵࡲ࠻ࠢࠥᘝ") + str(e) + bstack11ll1_opy_ (u"ࠨࠢᘞ"))
            traceback.print_exc()
            raise e
    @measure(event_name=EVENTS.bstack11ll1lllll1_opy_, stage=STAGE.bstack11l1llll1_opy_)
    def bstack11lll11l1ll_opy_(
        self,
        ref: str,
        platform_index: int,
        framework_name: str,
        framework_version: str,
        framework_session_id: str,
        hub_url: str,
    ):
        self.bstack1ll111111l1_opy_()
        req = structs.AutomationFrameworkStartRequest()
        req.ref = ref
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.framework_name = framework_name
        req.framework_version = framework_version
        req.framework_session_id = framework_session_id
        req.hub_url = hub_url
        self.logger.debug(bstack11ll1_opy_ (u"ࠢࡳࡧࡪ࡭ࡸࡺࡥࡳࡡࡶࡸࡦࡸࡴ࠻ࠢࠥᘟ") + str(req) + bstack11ll1_opy_ (u"ࠣࠤᘠ"))
        try:
            r = self.bstack1lllll11ll1_opy_.AutomationFrameworkStart(req)
            if not r.success:
                self.logger.debug(bstack11ll1_opy_ (u"ࠤࡵࡩࡨ࡫ࡩࡷࡧࡧࠤ࡫ࡸ࡯࡮ࠢࡶࡩࡷࡼࡥࡳ࠼ࠣࠦᘡ") + str(r) + bstack11ll1_opy_ (u"ࠥࠦᘢ"))
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack11ll1_opy_ (u"ࠦࡷࡶࡣ࠮ࡧࡵࡶࡴࡸ࠺ࠡࠤᘣ") + str(e) + bstack11ll1_opy_ (u"ࠧࠨᘤ"))
            traceback.print_exc()
            raise e
    @measure(event_name=EVENTS.bstack11lll111lll_opy_, stage=STAGE.bstack11l1llll1_opy_)
    def bstack11lll111l1l_opy_(
        self,
        ref: str,
        platform_index: int,
        framework_name: str,
        framework_version: str,
        framework_session_id: str,
        hub_url: str,
    ):
        self.bstack1ll111111l1_opy_()
        req = structs.AutomationFrameworkStopRequest()
        req.ref = ref
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.framework_name = framework_name
        req.framework_version = framework_version
        req.framework_session_id = framework_session_id
        req.hub_url = hub_url
        self.logger.debug(bstack11ll1_opy_ (u"ࠨࡲࡦࡩ࡬ࡷࡹ࡫ࡲࡠࡵࡷࡳࡵࡀࠠࠣᘥ") + str(req) + bstack11ll1_opy_ (u"ࠢࠣᘦ"))
        try:
            r = self.bstack1lllll11ll1_opy_.AutomationFrameworkStop(req)
            if not r.success:
                self.logger.debug(bstack11ll1_opy_ (u"ࠣࡴࡨࡧࡪ࡯ࡶࡦࡦࠣࡪࡷࡵ࡭ࠡࡵࡨࡶࡻ࡫ࡲ࠻ࠢࠥᘧ") + str(r) + bstack11ll1_opy_ (u"ࠤࠥᘨ"))
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack11ll1_opy_ (u"ࠥࡶࡵࡩ࠭ࡦࡴࡵࡳࡷࡀࠠࠣᘩ") + str(e) + bstack11ll1_opy_ (u"ࠦࠧᘪ"))
            traceback.print_exc()
            raise e
    @measure(event_name=EVENTS.bstack11llllll_opy_, stage=STAGE.bstack11l1llll1_opy_)
    def bstack11ll1llll11_opy_(self, instance: bstack1ll1l1ll1l1_opy_, url: str, f: bstack1ll11ll1lll_opy_, kwargs):
        bstack11lll1l11ll_opy_ = version.parse(f.framework_version)
        bstack11lll111111_opy_ = kwargs.get(bstack11ll1_opy_ (u"ࠧࡵࡰࡵ࡫ࡲࡲࡸࠨᘫ"))
        bstack11lll1l1111_opy_ = kwargs.get(bstack11ll1_opy_ (u"ࠨࡤࡦࡵ࡬ࡶࡪࡪ࡟ࡤࡣࡳࡥࡧ࡯࡬ࡪࡶ࡬ࡩࡸࠨᘬ"))
        bstack11llll111l1_opy_ = {}
        bstack11lll1l11l1_opy_ = {}
        bstack11lll11l1l1_opy_ = None
        bstack11lll11l11l_opy_ = {}
        if bstack11lll1l1111_opy_ is not None or bstack11lll111111_opy_ is not None: # check top level caps
            if bstack11lll1l1111_opy_ is not None:
                bstack11lll11l11l_opy_[bstack11ll1_opy_ (u"ࠧࡥࡧࡶ࡭ࡷ࡫ࡤࡠࡥࡤࡴࡦࡨࡩ࡭࡫ࡷ࡭ࡪࡹࠧᘭ")] = bstack11lll1l1111_opy_
            if bstack11lll111111_opy_ is not None and callable(getattr(bstack11lll111111_opy_, bstack11ll1_opy_ (u"ࠣࡶࡲࡣࡨࡧࡰࡢࡤ࡬ࡰ࡮ࡺࡩࡦࡵࠥᘮ"))):
                bstack11lll11l11l_opy_[bstack11ll1_opy_ (u"ࠩࡲࡴࡹ࡯࡯࡯ࡵࡢࡥࡸࡥࡣࡢࡲࡤࡦ࡮ࡲࡩࡵ࡫ࡨࡷࠬᘯ")] = bstack11lll111111_opy_.to_capabilities()
        response = self.bstack11llll1l1l1_opy_(f.platform_index, url, instance.ref(), json.dumps(bstack11lll11l11l_opy_).encode(bstack11ll1_opy_ (u"ࠥࡹࡹ࡬࠭࠹ࠤᘰ")))
        if response is not None and response.capabilities:
            bstack11llll111l1_opy_ = json.loads(response.capabilities.decode(bstack11ll1_opy_ (u"ࠦࡺࡺࡦ࠮࠺ࠥᘱ")))
            if not bstack11llll111l1_opy_: # empty caps bstack11llll11ll1_opy_ bstack11lll1lllll_opy_ bstack11llll1l111_opy_ bstack1l11llll1ll_opy_ or error in processing
                return
            bstack11lll11l1l1_opy_ = f.bstack1ll1l1l1111_opy_[bstack11ll1_opy_ (u"ࠧࡩࡲࡦࡣࡷࡩࡤࡵࡰࡵ࡫ࡲࡲࡸࡥࡦࡳࡱࡰࡣࡨࡧࡰࡴࠤᘲ")](bstack11llll111l1_opy_)
        if bstack11lll111111_opy_ is not None and bstack11lll1l11ll_opy_ >= version.parse(bstack11ll1_opy_ (u"࠭࠳࠯࠺࠱࠴ࠬᘳ")):
            bstack11lll1l11l1_opy_ = None
        if (
                not bstack11lll111111_opy_ and not bstack11lll1l1111_opy_
        ) or (
                bstack11lll1l11ll_opy_ < version.parse(bstack11ll1_opy_ (u"ࠧ࠴࠰࠻࠲࠵࠭ᘴ"))
        ):
            bstack11lll1l11l1_opy_ = {}
            bstack11lll1l11l1_opy_.update(bstack11llll111l1_opy_)
        self.logger.info(bstack1llll1111_opy_)
        if os.environ.get(bstack11ll1_opy_ (u"ࠣࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡂࡗࡗࡓࡒࡇࡔࡊࡑࡑࠦᘵ")).lower().__eq__(bstack11ll1_opy_ (u"ࠤࡷࡶࡺ࡫ࠢᘶ")):
            kwargs.update(
                {
                    bstack11ll1_opy_ (u"ࠥࡧࡴࡳ࡭ࡢࡰࡧࡣࡪࡾࡥࡤࡷࡷࡳࡷࠨᘷ"): f.bstack1ll11llll11_opy_,
                }
            )
        if bstack11lll1l11ll_opy_ >= version.parse(bstack11ll1_opy_ (u"ࠫ࠹࠴࠱࠱࠰࠳ࠫᘸ")):
            if bstack11lll1l1111_opy_ is not None:
                del kwargs[bstack11ll1_opy_ (u"ࠧࡪࡥࡴ࡫ࡵࡩࡩࡥࡣࡢࡲࡤࡦ࡮ࡲࡩࡵ࡫ࡨࡷࠧᘹ")]
            kwargs.update(
                {
                    bstack11ll1_opy_ (u"ࠨ࡯ࡱࡶ࡬ࡳࡳࡹࠢᘺ"): bstack11lll11l1l1_opy_,
                    bstack11ll1_opy_ (u"ࠢ࡬ࡧࡨࡴࡤࡧ࡬ࡪࡸࡨࠦᘻ"): True,
                    bstack11ll1_opy_ (u"ࠣࡨ࡬ࡰࡪࡥࡤࡦࡶࡨࡧࡹࡵࡲࠣᘼ"): None,
                }
            )
        elif bstack11lll1l11ll_opy_ >= version.parse(bstack11ll1_opy_ (u"ࠩ࠶࠲࠽࠴࠰ࠨᘽ")):
            kwargs.update(
                {
                    bstack11ll1_opy_ (u"ࠥࡨࡪࡹࡩࡳࡧࡧࡣࡨࡧࡰࡢࡤ࡬ࡰ࡮ࡺࡩࡦࡵࠥᘾ"): bstack11lll1l11l1_opy_,
                    bstack11ll1_opy_ (u"ࠦࡴࡶࡴࡪࡱࡱࡷࠧᘿ"): bstack11lll11l1l1_opy_,
                    bstack11ll1_opy_ (u"ࠧࡱࡥࡦࡲࡢࡥࡱ࡯ࡶࡦࠤᙀ"): True,
                    bstack11ll1_opy_ (u"ࠨࡦࡪ࡮ࡨࡣࡩ࡫ࡴࡦࡥࡷࡳࡷࠨᙁ"): None,
                }
            )
        elif bstack11lll1l11ll_opy_ >= version.parse(bstack11ll1_opy_ (u"ࠧ࠳࠰࠸࠷࠳࠶ࠧᙂ")):
            kwargs.update(
                {
                    bstack11ll1_opy_ (u"ࠣࡦࡨࡷ࡮ࡸࡥࡥࡡࡦࡥࡵࡧࡢࡪ࡮࡬ࡸ࡮࡫ࡳࠣᙃ"): bstack11lll1l11l1_opy_,
                    bstack11ll1_opy_ (u"ࠤ࡮ࡩࡪࡶ࡟ࡢ࡮࡬ࡺࡪࠨᙄ"): True,
                    bstack11ll1_opy_ (u"ࠥࡪ࡮ࡲࡥࡠࡦࡨࡸࡪࡩࡴࡰࡴࠥᙅ"): None,
                }
            )
        else:
            kwargs.update(
                {
                    bstack11ll1_opy_ (u"ࠦࡩ࡫ࡳࡪࡴࡨࡨࡤࡩࡡࡱࡣࡥ࡭ࡱ࡯ࡴࡪࡧࡶࠦᙆ"): bstack11lll1l11l1_opy_,
                    bstack11ll1_opy_ (u"ࠧࡱࡥࡦࡲࡢࡥࡱ࡯ࡶࡦࠤᙇ"): True,
                    bstack11ll1_opy_ (u"ࠨࡦࡪ࡮ࡨࡣࡩ࡫ࡴࡦࡥࡷࡳࡷࠨᙈ"): None,
                }
            )