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
import copy
import asyncio
import threading
from browserstack_sdk import sdk_pb2 as structs
from packaging import version
import traceback
from browserstack_sdk.sdk_cli.bstack1ll1l1ll1ll_opy_ import bstack1ll1ll1l1ll_opy_
from browserstack_sdk.sdk_cli.bstack1llll11l1ll_opy_ import (
    bstack1llll1111l1_opy_,
    bstack1lll1lll1l1_opy_,
    bstack1llll1ll1ll_opy_,
)
from bstack_utils.constants import *
from typing import Any, List, Union, Dict
from pathlib import Path
from browserstack_sdk.sdk_cli.bstack1ll1l111ll1_opy_ import bstack1ll1l1111l1_opy_
from datetime import datetime
from typing import Tuple, Any
from bstack_utils.messages import bstack11l1l11l1_opy_
from bstack_utils.helper import bstack1l1l1111l1l_opy_
import threading
import os
import urllib.parse
class bstack1lll11l1111_opy_(bstack1ll1ll1l1ll_opy_):
    def __init__(self, bstack1ll1l111lll_opy_):
        super().__init__()
        bstack1ll1l1111l1_opy_.bstack1ll111ll111_opy_((bstack1llll1111l1_opy_.bstack1llll1ll1l1_opy_, bstack1lll1lll1l1_opy_.PRE), self.bstack1l11ll1llll_opy_)
        bstack1ll1l1111l1_opy_.bstack1ll111ll111_opy_((bstack1llll1111l1_opy_.bstack1llll1ll1l1_opy_, bstack1lll1lll1l1_opy_.PRE), self.bstack1l11lll11ll_opy_)
        bstack1ll1l1111l1_opy_.bstack1ll111ll111_opy_((bstack1llll1111l1_opy_.bstack1lll1lllll1_opy_, bstack1lll1lll1l1_opy_.PRE), self.bstack1l11ll111ll_opy_)
        bstack1ll1l1111l1_opy_.bstack1ll111ll111_opy_((bstack1llll1111l1_opy_.bstack1lll1ll1ll1_opy_, bstack1lll1lll1l1_opy_.PRE), self.bstack1l11lll11l1_opy_)
        bstack1ll1l1111l1_opy_.bstack1ll111ll111_opy_((bstack1llll1111l1_opy_.bstack1llll1ll1l1_opy_, bstack1lll1lll1l1_opy_.PRE), self.bstack1l11lll1111_opy_)
        bstack1ll1l1111l1_opy_.bstack1ll111ll111_opy_((bstack1llll1111l1_opy_.QUIT, bstack1lll1lll1l1_opy_.PRE), self.on_close)
        self.bstack1ll1l111lll_opy_ = bstack1ll1l111lll_opy_
    def is_enabled(self) -> bool:
        return True
    def bstack1l11ll1llll_opy_(
        self,
        f: bstack1ll1l1111l1_opy_,
        bstack1l11lll111l_opy_: object,
        exec: Tuple[bstack1llll1ll1ll_opy_, str],
        bstack1llll1lll1l_opy_: Tuple[bstack1llll1111l1_opy_, bstack1lll1lll1l1_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if method_name != bstack11l1l_opy_ (u"ࠨ࡬ࡢࡷࡱࡧ࡭ࠨᎅ"):
            return
        if not bstack1l1l1111l1l_opy_():
            self.logger.debug(bstack11l1l_opy_ (u"ࠢࡓࡧࡷࡹࡷࡴࡩ࡯ࡩࠣ࡭ࡳࠦ࡬ࡢࡷࡱࡧ࡭ࠦ࡭ࡦࡶ࡫ࡳࡩ࠲ࠠ࡯ࡱࡷࠤࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࠣࡷࡪࡹࡳࡪࡱࡱࠦᎆ"))
            return
        def wrapped(bstack1l11lll111l_opy_, launch, *args, **kwargs):
            response = self.bstack1l11lll1l1l_opy_(f.platform_index, instance.ref(), json.dumps({bstack11l1l_opy_ (u"ࠨ࡫ࡶࡔࡱࡧࡹࡸࡴ࡬࡫࡭ࡺࠧᎇ"): True}).encode(bstack11l1l_opy_ (u"ࠤࡸࡸ࡫࠳࠸ࠣᎈ")))
            if response is not None and response.capabilities:
                if not bstack1l1l1111l1l_opy_():
                    browser = launch(bstack1l11lll111l_opy_)
                    return browser
                bstack1l11ll1ll11_opy_ = json.loads(response.capabilities.decode(bstack11l1l_opy_ (u"ࠥࡹࡹ࡬࠭࠹ࠤᎉ")))
                if not bstack1l11ll1ll11_opy_: # empty caps bstack1l11ll11lll_opy_ bstack1l11ll1lll1_opy_ bstack1l11ll1ll1l_opy_ bstack1ll1ll1ll11_opy_ or error in processing
                    return
                bstack1l11ll1l11l_opy_ = PLAYWRIGHT_HUB_URL + urllib.parse.quote(json.dumps(bstack1l11ll1ll11_opy_))
                f.bstack1lllll1111l_opy_(instance, bstack1ll1l1111l1_opy_.bstack1l11ll1l1l1_opy_, bstack1l11ll1l11l_opy_)
                f.bstack1lllll1111l_opy_(instance, bstack1ll1l1111l1_opy_.bstack1l11ll11l1l_opy_, bstack1l11ll1ll11_opy_)
                browser = bstack1l11lll111l_opy_.connect(bstack1l11ll1l11l_opy_)
                return browser
        return wrapped
    def bstack1l11ll111ll_opy_(
        self,
        f: bstack1ll1l1111l1_opy_,
        Connection: object,
        exec: Tuple[bstack1llll1ll1ll_opy_, str],
        bstack1llll1lll1l_opy_: Tuple[bstack1llll1111l1_opy_, bstack1lll1lll1l1_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if method_name != bstack11l1l_opy_ (u"ࠦࡩ࡯ࡳࡱࡣࡷࡧ࡭ࠨᎊ"):
            self.logger.debug(bstack11l1l_opy_ (u"ࠧࡘࡥࡵࡷࡵࡲ࡮ࡴࡧࠡ࡫ࡱࠤࡩ࡯ࡳࡱࡣࡷࡧ࡭ࠦ࡭ࡦࡶ࡫ࡳࡩ࠲ࠠ࡯ࡱࡷࠤࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࠣࡷࡪࡹࡳࡪࡱࡱࠦᎋ"))
            return
        if not bstack1l1l1111l1l_opy_():
            return
        def wrapped(Connection, dispatch, *args, **kwargs):
            data = args[0]
            try:
                if args and args[0].get(bstack11l1l_opy_ (u"࠭ࡰࡢࡴࡤࡱࡸ࠭ᎌ"), {}).get(bstack11l1l_opy_ (u"ࠧࡣࡵࡓࡥࡷࡧ࡭ࡴࠩᎍ")):
                    bstack1l11ll1l1ll_opy_ = args[0][bstack11l1l_opy_ (u"ࠣࡲࡤࡶࡦࡳࡳࠣᎎ")][bstack11l1l_opy_ (u"ࠤࡥࡷࡕࡧࡲࡢ࡯ࡶࠦᎏ")]
                    session_id = bstack1l11ll1l1ll_opy_.get(bstack11l1l_opy_ (u"ࠥࡷࡪࡹࡳࡪࡱࡱࡍࡩࠨ᎐"))
                    f.bstack1lllll1111l_opy_(instance, bstack1ll1l1111l1_opy_.bstack1l11lll1l11_opy_, session_id)
            except Exception as e:
                self.logger.debug(bstack11l1l_opy_ (u"ࠦࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡪࡰࠣࡨ࡮ࡹࡰࡢࡶࡦ࡬ࠥࡳࡥࡵࡪࡲࡨ࠿ࠦࠢ᎑"), e)
            dispatch(Connection, *args)
        return wrapped
    def bstack1l11lll1111_opy_(
        self,
        f: bstack1ll1l1111l1_opy_,
        bstack1l11lll111l_opy_: object,
        exec: Tuple[bstack1llll1ll1ll_opy_, str],
        bstack1llll1lll1l_opy_: Tuple[bstack1llll1111l1_opy_, bstack1lll1lll1l1_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if method_name != bstack11l1l_opy_ (u"ࠧࡩ࡯࡯ࡰࡨࡧࡹࠨ᎒"):
            return
        if not bstack1l1l1111l1l_opy_():
            self.logger.debug(bstack11l1l_opy_ (u"ࠨࡒࡦࡶࡸࡶࡳ࡯࡮ࡨࠢ࡬ࡲࠥࡩ࡯࡯ࡰࡨࡧࡹࠦ࡭ࡦࡶ࡫ࡳࡩ࠲ࠠ࡯ࡱࡷࠤࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࠣࡷࡪࡹࡳࡪࡱࡱࠦ᎓"))
            return
        def wrapped(bstack1l11lll111l_opy_, connect, *args, **kwargs):
            response = self.bstack1l11lll1l1l_opy_(f.platform_index, instance.ref(), json.dumps({bstack11l1l_opy_ (u"ࠧࡪࡵࡓࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹ࠭᎔"): True}).encode(bstack11l1l_opy_ (u"ࠣࡷࡷࡪ࠲࠾ࠢ᎕")))
            if response is not None and response.capabilities:
                bstack1l11ll1ll11_opy_ = json.loads(response.capabilities.decode(bstack11l1l_opy_ (u"ࠤࡸࡸ࡫࠳࠸ࠣ᎖")))
                if not bstack1l11ll1ll11_opy_:
                    return
                bstack1l11ll1l11l_opy_ = PLAYWRIGHT_HUB_URL + urllib.parse.quote(json.dumps(bstack1l11ll1ll11_opy_))
                if bstack1l11ll1ll11_opy_.get(bstack11l1l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠩ᎗")):
                    browser = bstack1l11lll111l_opy_.bstack1l11ll11l11_opy_(bstack1l11ll1l11l_opy_)
                    return browser
                else:
                    args = list(args)
                    args[0] = bstack1l11ll1l11l_opy_
                    return connect(bstack1l11lll111l_opy_, *args, **kwargs)
        return wrapped
    def bstack1l11lll11ll_opy_(
        self,
        f: bstack1ll1l1111l1_opy_,
        bstack1l1ll1l1ll1_opy_: object,
        exec: Tuple[bstack1llll1ll1ll_opy_, str],
        bstack1llll1lll1l_opy_: Tuple[bstack1llll1111l1_opy_, bstack1lll1lll1l1_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if method_name != bstack11l1l_opy_ (u"ࠦࡳ࡫ࡷࡠࡲࡤ࡫ࡪࠨ᎘"):
            return
        if not bstack1l1l1111l1l_opy_():
            self.logger.debug(bstack11l1l_opy_ (u"ࠧࡘࡥࡵࡷࡵࡲ࡮ࡴࡧࠡ࡫ࡱࠤࡳ࡫ࡷࡠࡲࡤ࡫ࡪࠦ࡭ࡦࡶ࡫ࡳࡩ࠲ࠠ࡯ࡱࡷࠤࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࠣࡷࡪࡹࡳࡪࡱࡱࠦ᎙"))
            return
        def wrapped(bstack1l1ll1l1ll1_opy_, bstack1l11ll11ll1_opy_, *args, **kwargs):
            contexts = bstack1l1ll1l1ll1_opy_.browser.contexts
            if contexts:
                for context in contexts:
                    if context.pages:
                        for page in context.pages:
                            if bstack11l1l_opy_ (u"ࠨࡡࡣࡱࡸࡸ࠿ࡨ࡬ࡢࡰ࡮ࠦ᎚") in page.url:
                                return page
                            else:
                                return bstack1l11ll11ll1_opy_(bstack1l1ll1l1ll1_opy_)
                    else:
                        return bstack1l11ll11ll1_opy_(bstack1l1ll1l1ll1_opy_)
        return wrapped
    def bstack1l11lll1l1l_opy_(self, platform_index: int, ref, user_input_params: bytes):
        req = structs.DriverInitRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.user_input_params = user_input_params
        req.ref = ref
        self.logger.debug(bstack11l1l_opy_ (u"ࠢࡳࡧࡪ࡭ࡸࡺࡥࡳࡡࡺࡩࡧࡪࡲࡪࡸࡨࡶࡤ࡯࡮ࡪࡶ࠽ࠤࠧ᎛") + str(req) + bstack11l1l_opy_ (u"ࠣࠤ᎜"))
        try:
            r = self.bstack1ll1ll11l11_opy_.DriverInit(req)
            if not r.success:
                self.logger.debug(bstack11l1l_opy_ (u"ࠤࡵࡩࡨ࡫ࡩࡷࡧࡧࠤ࡫ࡸ࡯࡮ࠢࡶࡩࡷࡼࡥࡳ࠼ࠣࡷࡺࡩࡣࡦࡵࡶࡁࠧ᎝") + str(r.success) + bstack11l1l_opy_ (u"ࠥࠦ᎞"))
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack11l1l_opy_ (u"ࠦࡷࡶࡣ࠮ࡧࡵࡶࡴࡸ࠺ࠡࠤ᎟") + str(e) + bstack11l1l_opy_ (u"ࠧࠨᎠ"))
            traceback.print_exc()
            raise e
    def bstack1l11lll11l1_opy_(
        self,
        f: bstack1ll1l1111l1_opy_,
        Connection: object,
        exec: Tuple[bstack1llll1ll1ll_opy_, str],
        bstack1llll1lll1l_opy_: Tuple[bstack1llll1111l1_opy_, bstack1lll1lll1l1_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if method_name != bstack11l1l_opy_ (u"ࠨ࡟ࡴࡧࡱࡨࡤࡳࡥࡴࡵࡤ࡫ࡪࡥࡴࡰࡡࡶࡩࡷࡼࡥࡳࠤᎡ"):
            return
        if not bstack1l1l1111l1l_opy_():
            return
        def wrapped(Connection, bstack1l11ll1l111_opy_, *args, **kwargs):
            return bstack1l11ll1l111_opy_(Connection, *args, **kwargs)
        return wrapped
    def on_close(
        self,
        f: bstack1ll1l1111l1_opy_,
        bstack1l11lll111l_opy_: object,
        exec: Tuple[bstack1llll1ll1ll_opy_, str],
        bstack1llll1lll1l_opy_: Tuple[bstack1llll1111l1_opy_, bstack1lll1lll1l1_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if method_name != bstack11l1l_opy_ (u"ࠢࡤ࡮ࡲࡷࡪࠨᎢ"):
            return
        if not bstack1l1l1111l1l_opy_():
            self.logger.debug(bstack11l1l_opy_ (u"ࠣࡔࡨࡸࡺࡸ࡮ࡪࡰࡪࠤ࡮ࡴࠠࡤ࡮ࡲࡷࡪࠦ࡭ࡦࡶ࡫ࡳࡩ࠲ࠠ࡯ࡱࡷࠤࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࠣࡷࡪࡹࡳࡪࡱࡱࠦᎣ"))
            return
        def wrapped(Connection, close, *args, **kwargs):
            return close(Connection)
        return wrapped