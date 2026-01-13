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
import os
import grpc
from browserstack_sdk import sdk_pb2 as structs
from packaging import version
import traceback
from browserstack_sdk.sdk_cli.bstack1ll1l1ll1ll_opy_ import bstack1ll1ll1l1ll_opy_
from browserstack_sdk.sdk_cli.bstack1llll11l1ll_opy_ import (
    bstack1llll1111l1_opy_,
    bstack1lll1lll1l1_opy_,
    bstack1llll1ll1ll_opy_,
)
from browserstack_sdk.sdk_cli.bstack1lll1l11l11_opy_ import bstack1lll11l111l_opy_
from datetime import datetime
from typing import Tuple, Any
from bstack_utils.messages import bstack11l1l11l1_opy_
from bstack_utils.measure import measure
from bstack_utils.constants import *
import threading
import os
from bstack_utils.bstack11l1l11ll_opy_ import bstack1lll1ll1l11_opy_
class bstack1ll1ll1llll_opy_(bstack1ll1ll1l1ll_opy_):
    bstack1l11l11l1ll_opy_ = bstack11l1l_opy_ (u"ࠢࡳࡧࡪ࡭ࡸࡺࡥࡳࡡ࡬ࡲ࡮ࡺࠢᏽ")
    bstack1l11l11l11l_opy_ = bstack11l1l_opy_ (u"ࠣࡴࡨ࡫࡮ࡹࡴࡦࡴࡢࡷࡹࡧࡲࡵࠤ᏾")
    bstack1l11l111l11_opy_ = bstack11l1l_opy_ (u"ࠤࡵࡩ࡬࡯ࡳࡵࡧࡵࡣࡸࡺ࡯ࡱࠤ᏿")
    def __init__(self, bstack1ll1l1lll11_opy_):
        super().__init__()
        bstack1lll11l111l_opy_.bstack1ll111ll111_opy_((bstack1llll1111l1_opy_.bstack1llll1ll1l1_opy_, bstack1lll1lll1l1_opy_.PRE), self.bstack1l11l111ll1_opy_)
        bstack1lll11l111l_opy_.bstack1ll111ll111_opy_((bstack1llll1111l1_opy_.bstack1lll1ll1ll1_opy_, bstack1lll1lll1l1_opy_.PRE), self.bstack1l1ll1llll1_opy_)
        bstack1lll11l111l_opy_.bstack1ll111ll111_opy_((bstack1llll1111l1_opy_.bstack1lll1ll1ll1_opy_, bstack1lll1lll1l1_opy_.POST), self.bstack1l111llllll_opy_)
        bstack1lll11l111l_opy_.bstack1ll111ll111_opy_((bstack1llll1111l1_opy_.bstack1lll1ll1ll1_opy_, bstack1lll1lll1l1_opy_.POST), self.bstack1l111lll11l_opy_)
        bstack1lll11l111l_opy_.bstack1ll111ll111_opy_((bstack1llll1111l1_opy_.QUIT, bstack1lll1lll1l1_opy_.POST), self.bstack1l11l111lll_opy_)
    def is_enabled(self) -> bool:
        return True
    def bstack1l11l111ll1_opy_(
        self,
        f: bstack1lll11l111l_opy_,
        driver: object,
        exec: Tuple[bstack1llll1ll1ll_opy_, str],
        bstack1llll1lll1l_opy_: Tuple[bstack1llll1111l1_opy_, bstack1lll1lll1l1_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if method_name != bstack11l1l_opy_ (u"ࠥࡣࡤ࡯࡮ࡪࡶࡢࡣࠧ᐀"):
            return
        def wrapped(driver, init, *args, **kwargs):
            url = None
            try:
                if isinstance(kwargs.get(bstack11l1l_opy_ (u"ࠦࡨࡵ࡭࡮ࡣࡱࡨࡤ࡫ࡸࡦࡥࡸࡸࡴࡸࠢᐁ")), str):
                    url = kwargs.get(bstack11l1l_opy_ (u"ࠧࡩ࡯࡮࡯ࡤࡲࡩࡥࡥࡹࡧࡦࡹࡹࡵࡲࠣᐂ"))
                elif hasattr(kwargs.get(bstack11l1l_opy_ (u"ࠨࡣࡰ࡯ࡰࡥࡳࡪ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳࠤᐃ")), bstack11l1l_opy_ (u"ࠧࡠࡥ࡯࡭ࡪࡴࡴࡠࡥࡲࡲ࡫࡯ࡧࠨᐄ")):
                    url = kwargs.get(bstack11l1l_opy_ (u"ࠣࡥࡲࡱࡲࡧ࡮ࡥࡡࡨࡼࡪࡩࡵࡵࡱࡵࠦᐅ"))._client_config.remote_server_addr
                else:
                    url = kwargs.get(bstack11l1l_opy_ (u"ࠤࡦࡳࡲࡳࡡ࡯ࡦࡢࡩࡽ࡫ࡣࡶࡶࡲࡶࠧᐆ"))._url
            except Exception as e:
                url = bstack11l1l_opy_ (u"ࠪࠫᐇ")
                self.logger.error(bstack11l1l_opy_ (u"ࠦࡊࡸࡲࡰࡴࠣࡻ࡭࡯࡬ࡦࠢࡪࡩࡹࡺࡩ࡯ࡩࠣࡹࡷࡲࠠࡧࡴࡲࡱࠥࡪࡲࡪࡸࡨࡶ࠿ࠦࡻࡾࠤᐈ").format(e))
            self.logger.info(bstack11l1l_opy_ (u"ࠧࡘࡥ࡮ࡱࡷࡩ࡙ࠥࡥࡳࡸࡨࡶࠥࡇࡤࡥࡴࡨࡷࡸࠦࡢࡦ࡫ࡱ࡫ࠥࡶࡡࡴࡵࡨࡨࠥࡧࡳࠡ࠼ࠣࡿࢂࠨᐉ").format(str(url)))
            self.bstack1l111ll1l1l_opy_(instance, url, f, kwargs)
            self.logger.info(bstack11l1l_opy_ (u"ࠨࡤࡳ࡫ࡹࡩࡷ࠴ࡻ࡮ࡧࡷ࡬ࡴࡪ࡟࡯ࡣࡰࡩࢂࠦࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡠ࡫ࡱࡨࡪࡾ࠽ࡼࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡢ࡭ࡳࡪࡥࡹࡿ࠽ࠤࡦࡸࡧࡴ࠿ࡾࡥࡷ࡭ࡳࡾࠢ࡮ࡻࡦࡸࡧࡴ࠿ࡾ࡯ࡼࡧࡲࡨࡵࢀࠦᐊ").format(method_name=method_name, platform_index=f.platform_index, args=args, kwargs=kwargs))
            threading.current_thread().bstackSessionDriver = driver
            return init(driver, *args, **kwargs)
        return wrapped
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
        instance, method_name = exec
        if f.bstack1llll1lllll_opy_(instance, bstack1ll1ll1llll_opy_.bstack1l11l11l1ll_opy_, False):
            return
        if not f.bstack1lll1ll1l1l_opy_(instance, bstack1lll11l111l_opy_.bstack1ll1111l111_opy_):
            return
        platform_index = f.bstack1llll1lllll_opy_(instance, bstack1lll11l111l_opy_.bstack1ll1111l111_opy_)
        if f.bstack1l1lll1ll1l_opy_(method_name, *args) and len(args) > 1:
            bstack11ll1l1ll1_opy_ = datetime.now()
            hub_url = bstack1lll11l111l_opy_.hub_url(driver)
            self.logger.warning(bstack11l1l_opy_ (u"ࠢࡩࡷࡥࡣࡺࡸ࡬࠾ࠤᐋ") + str(hub_url) + bstack11l1l_opy_ (u"ࠣࠤᐌ"))
            bstack1l111lllll1_opy_ = args[1][bstack11l1l_opy_ (u"ࠤࡦࡥࡵࡧࡢࡪ࡮࡬ࡸ࡮࡫ࡳࠣᐍ")] if isinstance(args[1], dict) and bstack11l1l_opy_ (u"ࠥࡧࡦࡶࡡࡣ࡫࡯࡭ࡹ࡯ࡥࡴࠤᐎ") in args[1] else None
            bstack1l11l11l111_opy_ = bstack11l1l_opy_ (u"ࠦࡦࡲࡷࡢࡻࡶࡑࡦࡺࡣࡩࠤᐏ")
            if isinstance(bstack1l111lllll1_opy_, dict):
                bstack11ll1l1ll1_opy_ = datetime.now()
                r = self.bstack1l111lll111_opy_(
                    instance.ref(),
                    platform_index,
                    f.framework_name,
                    f.framework_version,
                    hub_url
                )
                instance.bstack11lll111_opy_(bstack11l1l_opy_ (u"ࠧ࡭ࡲࡱࡥ࠽ࡶࡪ࡭ࡩࡴࡶࡨࡶࡤ࡯࡮ࡪࡶࠥᐐ"), datetime.now() - bstack11ll1l1ll1_opy_)
                try:
                    if not r.success:
                        self.logger.info(bstack11l1l_opy_ (u"ࠨࡳࡰ࡯ࡨࡸ࡭࡯࡮ࡨࠢࡺࡩࡳࡺࠠࡸࡴࡲࡲ࡬ࡀࠠࠣᐑ") + str(r) + bstack11l1l_opy_ (u"ࠢࠣᐒ"))
                        return
                    if r.hub_url:
                        f.bstack1l11l111111_opy_(instance, driver, r.hub_url)
                        f.bstack1lllll1111l_opy_(instance, bstack1ll1ll1llll_opy_.bstack1l11l11l1ll_opy_, True)
                except Exception as e:
                    self.logger.error(bstack11l1l_opy_ (u"ࠣࡧࡵࡶࡴࡸࠢᐓ"), e)
    def bstack1l111llllll_opy_(
        self,
        f: bstack1lll11l111l_opy_,
        driver: object,
        exec: Tuple[bstack1llll1ll1ll_opy_, str],
        bstack1llll1lll1l_opy_: Tuple[bstack1llll1111l1_opy_, bstack1lll1lll1l1_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
            session_id = bstack1lll11l111l_opy_.session_id(driver)
            if session_id:
                bstack1l11l1111l1_opy_ = bstack11l1l_opy_ (u"ࠤࡾࢁ࠿ࡹࡴࡢࡴࡷࠦᐔ").format(session_id)
                bstack1lll1ll1l11_opy_.mark(bstack1l11l1111l1_opy_)
    def bstack1l111lll11l_opy_(
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
        if f.bstack1llll1lllll_opy_(instance, bstack1ll1ll1llll_opy_.bstack1l11l11l11l_opy_, False):
            return
        ref = instance.ref()
        hub_url = bstack1lll11l111l_opy_.hub_url(driver)
        if not hub_url:
            self.logger.warning(bstack11l1l_opy_ (u"ࠥࡪࡦ࡯࡬ࡦࡦࠣࡸࡴࠦࡰࡢࡴࡶࡩࠥ࡮ࡵࡣࡡࡸࡶࡱࡃࠢᐕ") + str(hub_url) + bstack11l1l_opy_ (u"ࠦࠧᐖ"))
            return
        framework_session_id = bstack1lll11l111l_opy_.session_id(driver)
        if not framework_session_id:
            self.logger.warning(bstack11l1l_opy_ (u"ࠧ࡬ࡡࡪ࡮ࡨࡨࠥࡺ࡯ࠡࡲࡤࡶࡸ࡫ࠠࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡢࡷࡪࡹࡳࡪࡱࡱࡣ࡮ࡪ࠽ࠣᐗ") + str(framework_session_id) + bstack11l1l_opy_ (u"ࠨࠢᐘ"))
            return
        if bstack1lll11l111l_opy_.bstack1l11l1l1111_opy_(*args) == bstack1lll11l111l_opy_.bstack1l111ll1ll1_opy_:
            bstack1l11l111l1l_opy_ = bstack11l1l_opy_ (u"ࠢࡼࡿ࠽ࡩࡳࡪࠢᐙ").format(framework_session_id)
            bstack1l11l1111l1_opy_ = bstack11l1l_opy_ (u"ࠣࡽࢀ࠾ࡸࡺࡡࡳࡶࠥᐚ").format(framework_session_id)
            bstack1lll1ll1l11_opy_.end(
                label=bstack11l1l_opy_ (u"ࠤࡶࡨࡰࡀࡤࡳ࡫ࡹࡩࡷࡀࡰࡰࡵࡷ࠱࡮ࡴࡩࡵ࡫ࡤࡰ࡮ࢀࡡࡵ࡫ࡲࡲࠧᐛ"),
                start=bstack1l11l1111l1_opy_,
                end=bstack1l11l111l1l_opy_,
                status=True,
                failure=None
            )
            bstack11ll1l1ll1_opy_ = datetime.now()
            r = self.bstack1l11l11111l_opy_(
                ref,
                f.bstack1llll1lllll_opy_(instance, bstack1lll11l111l_opy_.bstack1ll1111l111_opy_, 0),
                f.framework_name,
                f.framework_version,
                framework_session_id,
                hub_url,
            )
            instance.bstack11lll111_opy_(bstack11l1l_opy_ (u"ࠥ࡫ࡷࡶࡣ࠻ࡴࡨ࡫࡮ࡹࡴࡦࡴࡢࡷࡹࡧࡲࡵࠤᐜ"), datetime.now() - bstack11ll1l1ll1_opy_)
            f.bstack1lllll1111l_opy_(instance, bstack1ll1ll1llll_opy_.bstack1l11l11l11l_opy_, r.success)
    def bstack1l11l111lll_opy_(
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
        if f.bstack1llll1lllll_opy_(instance, bstack1ll1ll1llll_opy_.bstack1l11l111l11_opy_, False):
            return
        ref = instance.ref()
        framework_session_id = bstack1lll11l111l_opy_.session_id(driver)
        hub_url = bstack1lll11l111l_opy_.hub_url(driver)
        bstack11ll1l1ll1_opy_ = datetime.now()
        r = self.bstack1l111lll1l1_opy_(
            ref,
            f.bstack1llll1lllll_opy_(instance, bstack1lll11l111l_opy_.bstack1ll1111l111_opy_, 0),
            f.framework_name,
            f.framework_version,
            framework_session_id,
            hub_url,
        )
        instance.bstack11lll111_opy_(bstack11l1l_opy_ (u"ࠦ࡬ࡸࡰࡤ࠼ࡵࡩ࡬࡯ࡳࡵࡧࡵࡣࡸࡺ࡯ࡱࠤᐝ"), datetime.now() - bstack11ll1l1ll1_opy_)
        f.bstack1lllll1111l_opy_(instance, bstack1ll1ll1llll_opy_.bstack1l11l111l11_opy_, r.success)
    @measure(event_name=EVENTS.bstack1llllll11_opy_, stage=STAGE.bstack1lll1l11l_opy_)
    def bstack1l11lll1l1l_opy_(self, platform_index: int, url: str, ref, user_input_params: bytes):
        req = structs.DriverInitRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.user_input_params = user_input_params
        req.ref = ref
        req.hub_url = url
        self.logger.debug(bstack11l1l_opy_ (u"ࠧࡸࡥࡨ࡫ࡶࡸࡪࡸ࡟ࡸࡧࡥࡨࡷ࡯ࡶࡦࡴࡢ࡭ࡳ࡯ࡴ࠻ࠢࠥᐞ") + str(req) + bstack11l1l_opy_ (u"ࠨࠢᐟ"))
        try:
            r = self.bstack1ll1ll11l11_opy_.DriverInit(req)
            if not r.success:
                self.logger.debug(bstack11l1l_opy_ (u"ࠢࡳࡧࡦࡩ࡮ࡼࡥࡥࠢࡩࡶࡴࡳࠠࡴࡧࡵࡺࡪࡸ࠺ࠡࡵࡸࡧࡨ࡫ࡳࡴ࠿ࠥᐠ") + str(r.success) + bstack11l1l_opy_ (u"ࠣࠤᐡ"))
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack11l1l_opy_ (u"ࠤࡵࡴࡨ࠳ࡥࡳࡴࡲࡶ࠿ࠦࠢᐢ") + str(e) + bstack11l1l_opy_ (u"ࠥࠦᐣ"))
            traceback.print_exc()
            raise e
    @measure(event_name=EVENTS.bstack1l111llll1l_opy_, stage=STAGE.bstack1lll1l11l_opy_)
    def bstack1l111lll111_opy_(
        self,
        ref: str,
        platform_index: int,
        framework_name: str,
        framework_version: str,
        hub_url: str
    ):
        self.bstack1ll11111lll_opy_()
        req = structs.AutomationFrameworkInitRequest()
        req.ref = ref
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.framework_name = framework_name
        req.framework_version = framework_version
        req.hub_url = hub_url
        self.logger.debug(bstack11l1l_opy_ (u"ࠦࡷ࡫ࡧࡪࡵࡷࡩࡷࡥࡩ࡯࡫ࡷ࠾ࠥࠨᐤ") + str(req) + bstack11l1l_opy_ (u"ࠧࠨᐥ"))
        try:
            r = self.bstack1ll1ll11l11_opy_.AutomationFrameworkInit(req)
            if not r.success:
                self.logger.debug(bstack11l1l_opy_ (u"ࠨࡲࡦࡥࡨ࡭ࡻ࡫ࡤࠡࡨࡵࡳࡲࠦࡳࡦࡴࡹࡩࡷࡀࠠࡴࡷࡦࡧࡪࡹࡳ࠾ࠤᐦ") + str(r.success) + bstack11l1l_opy_ (u"ࠢࠣᐧ"))
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack11l1l_opy_ (u"ࠣࡴࡳࡧ࠲࡫ࡲࡳࡱࡵ࠾ࠥࠨᐨ") + str(e) + bstack11l1l_opy_ (u"ࠤࠥᐩ"))
            traceback.print_exc()
            raise e
    @measure(event_name=EVENTS.bstack1l11l11lll1_opy_, stage=STAGE.bstack1lll1l11l_opy_)
    def bstack1l11l11111l_opy_(
        self,
        ref: str,
        platform_index: int,
        framework_name: str,
        framework_version: str,
        framework_session_id: str,
        hub_url: str,
    ):
        self.bstack1ll11111lll_opy_()
        req = structs.AutomationFrameworkStartRequest()
        req.ref = ref
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.framework_name = framework_name
        req.framework_version = framework_version
        req.framework_session_id = framework_session_id
        req.hub_url = hub_url
        self.logger.debug(bstack11l1l_opy_ (u"ࠥࡶࡪ࡭ࡩࡴࡶࡨࡶࡤࡹࡴࡢࡴࡷ࠾ࠥࠨᐪ") + str(req) + bstack11l1l_opy_ (u"ࠦࠧᐫ"))
        try:
            r = self.bstack1ll1ll11l11_opy_.AutomationFrameworkStart(req)
            if not r.success:
                self.logger.debug(bstack11l1l_opy_ (u"ࠧࡸࡥࡤࡧ࡬ࡺࡪࡪࠠࡧࡴࡲࡱࠥࡹࡥࡳࡸࡨࡶ࠿ࠦࠢᐬ") + str(r) + bstack11l1l_opy_ (u"ࠨࠢᐭ"))
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack11l1l_opy_ (u"ࠢࡳࡲࡦ࠱ࡪࡸࡲࡰࡴ࠽ࠤࠧᐮ") + str(e) + bstack11l1l_opy_ (u"ࠣࠤᐯ"))
            traceback.print_exc()
            raise e
    @measure(event_name=EVENTS.bstack1l11l1111ll_opy_, stage=STAGE.bstack1lll1l11l_opy_)
    def bstack1l111lll1l1_opy_(
        self,
        ref: str,
        platform_index: int,
        framework_name: str,
        framework_version: str,
        framework_session_id: str,
        hub_url: str,
    ):
        self.bstack1ll11111lll_opy_()
        req = structs.AutomationFrameworkStopRequest()
        req.ref = ref
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.framework_name = framework_name
        req.framework_version = framework_version
        req.framework_session_id = framework_session_id
        req.hub_url = hub_url
        self.logger.debug(bstack11l1l_opy_ (u"ࠤࡵࡩ࡬࡯ࡳࡵࡧࡵࡣࡸࡺ࡯ࡱ࠼ࠣࠦᐰ") + str(req) + bstack11l1l_opy_ (u"ࠥࠦᐱ"))
        try:
            r = self.bstack1ll1ll11l11_opy_.AutomationFrameworkStop(req)
            if not r.success:
                self.logger.debug(bstack11l1l_opy_ (u"ࠦࡷ࡫ࡣࡦ࡫ࡹࡩࡩࠦࡦࡳࡱࡰࠤࡸ࡫ࡲࡷࡧࡵ࠾ࠥࠨᐲ") + str(r) + bstack11l1l_opy_ (u"ࠧࠨᐳ"))
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack11l1l_opy_ (u"ࠨࡲࡱࡥ࠰ࡩࡷࡸ࡯ࡳ࠼ࠣࠦᐴ") + str(e) + bstack11l1l_opy_ (u"ࠢࠣᐵ"))
            traceback.print_exc()
            raise e
    @measure(event_name=EVENTS.bstack11l1111l11_opy_, stage=STAGE.bstack1lll1l11l_opy_)
    def bstack1l111ll1l1l_opy_(self, instance: bstack1llll1ll1ll_opy_, url: str, f: bstack1lll11l111l_opy_, kwargs):
        bstack1l11l11ll11_opy_ = version.parse(f.framework_version)
        bstack1l11l11l1l1_opy_ = kwargs.get(bstack11l1l_opy_ (u"ࠣࡱࡳࡸ࡮ࡵ࡮ࡴࠤᐶ"))
        bstack1l111llll11_opy_ = kwargs.get(bstack11l1l_opy_ (u"ࠤࡧࡩࡸ࡯ࡲࡦࡦࡢࡧࡦࡶࡡࡣ࡫࡯࡭ࡹ࡯ࡥࡴࠤᐷ"))
        bstack1l11ll1ll11_opy_ = {}
        bstack1l111ll1lll_opy_ = {}
        bstack1l11l11ll1l_opy_ = None
        bstack1l11l11llll_opy_ = {}
        if bstack1l111llll11_opy_ is not None or bstack1l11l11l1l1_opy_ is not None: # check top level caps
            if bstack1l111llll11_opy_ is not None:
                bstack1l11l11llll_opy_[bstack11l1l_opy_ (u"ࠪࡨࡪࡹࡩࡳࡧࡧࡣࡨࡧࡰࡢࡤ࡬ࡰ࡮ࡺࡩࡦࡵࠪᐸ")] = bstack1l111llll11_opy_
            if bstack1l11l11l1l1_opy_ is not None and callable(getattr(bstack1l11l11l1l1_opy_, bstack11l1l_opy_ (u"ࠦࡹࡵ࡟ࡤࡣࡳࡥࡧ࡯࡬ࡪࡶ࡬ࡩࡸࠨᐹ"))):
                bstack1l11l11llll_opy_[bstack11l1l_opy_ (u"ࠬࡵࡰࡵ࡫ࡲࡲࡸࡥࡡࡴࡡࡦࡥࡵࡧࡢࡪ࡮࡬ࡸ࡮࡫ࡳࠨᐺ")] = bstack1l11l11l1l1_opy_.to_capabilities()
        response = self.bstack1l11lll1l1l_opy_(f.platform_index, url, instance.ref(), json.dumps(bstack1l11l11llll_opy_).encode(bstack11l1l_opy_ (u"ࠨࡵࡵࡨ࠰࠼ࠧᐻ")))
        if response is not None and response.capabilities:
            bstack1l11ll1ll11_opy_ = json.loads(response.capabilities.decode(bstack11l1l_opy_ (u"ࠢࡶࡶࡩ࠱࠽ࠨᐼ")))
            if not bstack1l11ll1ll11_opy_: # empty caps bstack1l11ll11lll_opy_ bstack1l11ll1lll1_opy_ bstack1l11ll1ll1l_opy_ bstack1ll1ll1ll11_opy_ or error in processing
                return
            bstack1l11l11ll1l_opy_ = f.bstack1lll111llll_opy_[bstack11l1l_opy_ (u"ࠣࡥࡵࡩࡦࡺࡥࡠࡱࡳࡸ࡮ࡵ࡮ࡴࡡࡩࡶࡴࡳ࡟ࡤࡣࡳࡷࠧᐽ")](bstack1l11ll1ll11_opy_)
        if bstack1l11l11l1l1_opy_ is not None and bstack1l11l11ll11_opy_ >= version.parse(bstack11l1l_opy_ (u"ࠩ࠶࠲࠽࠴࠰ࠨᐾ")):
            bstack1l111ll1lll_opy_ = None
        if (
                not bstack1l11l11l1l1_opy_ and not bstack1l111llll11_opy_
        ) or (
                bstack1l11l11ll11_opy_ < version.parse(bstack11l1l_opy_ (u"ࠪ࠷࠳࠾࠮࠱ࠩᐿ"))
        ):
            bstack1l111ll1lll_opy_ = {}
            bstack1l111ll1lll_opy_.update(bstack1l11ll1ll11_opy_)
        self.logger.info(bstack11l1l11l1_opy_)
        if os.environ.get(bstack11l1l_opy_ (u"ࠦࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡅ࡚࡚ࡏࡎࡃࡗࡍࡔࡔࠢᑀ")).lower().__eq__(bstack11l1l_opy_ (u"ࠧࡺࡲࡶࡧࠥᑁ")):
            kwargs.update(
                {
                    bstack11l1l_opy_ (u"ࠨࡣࡰ࡯ࡰࡥࡳࡪ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳࠤᑂ"): f.bstack1l111lll1ll_opy_,
                }
            )
        if bstack1l11l11ll11_opy_ >= version.parse(bstack11l1l_opy_ (u"ࠧ࠵࠰࠴࠴࠳࠶ࠧᑃ")):
            if bstack1l111llll11_opy_ is not None:
                del kwargs[bstack11l1l_opy_ (u"ࠣࡦࡨࡷ࡮ࡸࡥࡥࡡࡦࡥࡵࡧࡢࡪ࡮࡬ࡸ࡮࡫ࡳࠣᑄ")]
            kwargs.update(
                {
                    bstack11l1l_opy_ (u"ࠤࡲࡴࡹ࡯࡯࡯ࡵࠥᑅ"): bstack1l11l11ll1l_opy_,
                    bstack11l1l_opy_ (u"ࠥ࡯ࡪ࡫ࡰࡠࡣ࡯࡭ࡻ࡫ࠢᑆ"): True,
                    bstack11l1l_opy_ (u"ࠦ࡫࡯࡬ࡦࡡࡧࡩࡹ࡫ࡣࡵࡱࡵࠦᑇ"): None,
                }
            )
        elif bstack1l11l11ll11_opy_ >= version.parse(bstack11l1l_opy_ (u"ࠬ࠹࠮࠹࠰࠳ࠫᑈ")):
            kwargs.update(
                {
                    bstack11l1l_opy_ (u"ࠨࡤࡦࡵ࡬ࡶࡪࡪ࡟ࡤࡣࡳࡥࡧ࡯࡬ࡪࡶ࡬ࡩࡸࠨᑉ"): bstack1l111ll1lll_opy_,
                    bstack11l1l_opy_ (u"ࠢࡰࡲࡷ࡭ࡴࡴࡳࠣᑊ"): bstack1l11l11ll1l_opy_,
                    bstack11l1l_opy_ (u"ࠣ࡭ࡨࡩࡵࡥࡡ࡭࡫ࡹࡩࠧᑋ"): True,
                    bstack11l1l_opy_ (u"ࠤࡩ࡭ࡱ࡫࡟ࡥࡧࡷࡩࡨࡺ࡯ࡳࠤᑌ"): None,
                }
            )
        elif bstack1l11l11ll11_opy_ >= version.parse(bstack11l1l_opy_ (u"ࠪ࠶࠳࠻࠳࠯࠲ࠪᑍ")):
            kwargs.update(
                {
                    bstack11l1l_opy_ (u"ࠦࡩ࡫ࡳࡪࡴࡨࡨࡤࡩࡡࡱࡣࡥ࡭ࡱ࡯ࡴࡪࡧࡶࠦᑎ"): bstack1l111ll1lll_opy_,
                    bstack11l1l_opy_ (u"ࠧࡱࡥࡦࡲࡢࡥࡱ࡯ࡶࡦࠤᑏ"): True,
                    bstack11l1l_opy_ (u"ࠨࡦࡪ࡮ࡨࡣࡩ࡫ࡴࡦࡥࡷࡳࡷࠨᑐ"): None,
                }
            )
        else:
            kwargs.update(
                {
                    bstack11l1l_opy_ (u"ࠢࡥࡧࡶ࡭ࡷ࡫ࡤࡠࡥࡤࡴࡦࡨࡩ࡭࡫ࡷ࡭ࡪࡹࠢᑑ"): bstack1l111ll1lll_opy_,
                    bstack11l1l_opy_ (u"ࠣ࡭ࡨࡩࡵࡥࡡ࡭࡫ࡹࡩࠧᑒ"): True,
                    bstack11l1l_opy_ (u"ࠤࡩ࡭ࡱ࡫࡟ࡥࡧࡷࡩࡨࡺ࡯ࡳࠤᑓ"): None,
                }
            )