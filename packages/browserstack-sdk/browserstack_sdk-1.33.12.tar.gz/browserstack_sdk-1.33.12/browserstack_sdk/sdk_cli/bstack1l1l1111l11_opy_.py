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
import copy
import asyncio
import threading
from browserstack_sdk import sdk_pb2 as structs
from packaging import version
import traceback
from browserstack_sdk.sdk_cli.bstack1l1ll111111_opy_ import bstack1l1l1l111ll_opy_
from browserstack_sdk.sdk_cli.bstack1ll11l1l1l1_opy_ import (
    bstack1ll11lllll1_opy_,
    bstack1ll11lll1ll_opy_,
    bstack1ll1l1ll1l1_opy_,
)
from bstack_utils.constants import *
from typing import Any, List, Union, Dict
from pathlib import Path
from browserstack_sdk.sdk_cli.bstack1ll11l111ll_opy_ import bstack1ll11l11l1l_opy_
from datetime import datetime
from typing import Tuple, Any
from bstack_utils.messages import bstack1llll1111_opy_
from bstack_utils.helper import bstack1ll111l11l1_opy_
import threading
import os
import urllib.parse
class bstack1l1ll11l1l1_opy_(bstack1l1l1l111ll_opy_):
    def __init__(self, bstack1l1l1l1l1l1_opy_):
        super().__init__()
        bstack1ll11l11l1l_opy_.bstack1ll1l11111l_opy_((bstack1ll11lllll1_opy_.bstack1ll11l1ll1l_opy_, bstack1ll11lll1ll_opy_.PRE), self.bstack11llll11111_opy_)
        bstack1ll11l11l1l_opy_.bstack1ll1l11111l_opy_((bstack1ll11lllll1_opy_.bstack1ll11l1ll1l_opy_, bstack1ll11lll1ll_opy_.PRE), self.bstack11llll11lll_opy_)
        bstack1ll11l11l1l_opy_.bstack1ll1l11111l_opy_((bstack1ll11lllll1_opy_.bstack1ll11l11l11_opy_, bstack1ll11lll1ll_opy_.PRE), self.bstack11lll1lll11_opy_)
        bstack1ll11l11l1l_opy_.bstack1ll1l11111l_opy_((bstack1ll11lllll1_opy_.bstack1ll11l1l1ll_opy_, bstack1ll11lll1ll_opy_.PRE), self.bstack11llll1l11l_opy_)
        bstack1ll11l11l1l_opy_.bstack1ll1l11111l_opy_((bstack1ll11lllll1_opy_.bstack1ll11l1ll1l_opy_, bstack1ll11lll1ll_opy_.PRE), self.bstack11llll1l1ll_opy_)
        bstack1ll11l11l1l_opy_.bstack1ll1l11111l_opy_((bstack1ll11lllll1_opy_.QUIT, bstack1ll11lll1ll_opy_.PRE), self.on_close)
        self.bstack1l1l1l1l1l1_opy_ = bstack1l1l1l1l1l1_opy_
    def is_enabled(self) -> bool:
        return True
    def bstack11llll11111_opy_(
        self,
        f: bstack1ll11l11l1l_opy_,
        bstack11llll111ll_opy_: object,
        exec: Tuple[bstack1ll1l1ll1l1_opy_, str],
        bstack1lll1lll111_opy_: Tuple[bstack1ll11lllll1_opy_, bstack1ll11lll1ll_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if method_name != bstack11ll1_opy_ (u"ࠥࡰࡦࡻ࡮ࡤࡪࠥᕺ"):
            return
        if not bstack1ll111l11l1_opy_():
            self.logger.debug(bstack11ll1_opy_ (u"ࠦࡗ࡫ࡴࡶࡴࡱ࡭ࡳ࡭ࠠࡪࡰࠣࡰࡦࡻ࡮ࡤࡪࠣࡱࡪࡺࡨࡰࡦ࠯ࠤࡳࡵࡴࠡࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠣᕻ"))
            return
        def wrapped(bstack11llll111ll_opy_, launch, *args, **kwargs):
            response = self.bstack11llll1l1l1_opy_(f.platform_index, instance.ref(), json.dumps({bstack11ll1_opy_ (u"ࠬ࡯ࡳࡑ࡮ࡤࡽࡼࡸࡩࡨࡪࡷࠫᕼ"): True}).encode(bstack11ll1_opy_ (u"ࠨࡵࡵࡨ࠰࠼ࠧᕽ")))
            if response is not None and response.capabilities:
                if not bstack1ll111l11l1_opy_():
                    browser = launch(bstack11llll111ll_opy_)
                    return browser
                bstack11llll111l1_opy_ = json.loads(response.capabilities.decode(bstack11ll1_opy_ (u"ࠢࡶࡶࡩ࠱࠽ࠨᕾ")))
                if not bstack11llll111l1_opy_: # empty caps bstack11llll11ll1_opy_ bstack11lll1lllll_opy_ bstack11llll1l111_opy_ bstack1l11llll1ll_opy_ or error in processing
                    return
                bstack11llll11l11_opy_ = PLAYWRIGHT_HUB_URL + urllib.parse.quote(json.dumps(bstack11llll111l1_opy_))
                f.bstack1lll111ll11_opy_(instance, bstack1ll11l11l1l_opy_.bstack1ll1l1ll111_opy_, bstack11llll11l11_opy_)
                f.bstack1lll111ll11_opy_(instance, bstack1ll11l11l1l_opy_.bstack1ll11ll1l11_opy_, bstack11llll111l1_opy_)
                browser = bstack11llll111ll_opy_.connect(bstack11llll11l11_opy_)
                return browser
        return wrapped
    def bstack11lll1lll11_opy_(
        self,
        f: bstack1ll11l11l1l_opy_,
        Connection: object,
        exec: Tuple[bstack1ll1l1ll1l1_opy_, str],
        bstack1lll1lll111_opy_: Tuple[bstack1ll11lllll1_opy_, bstack1ll11lll1ll_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if method_name != bstack11ll1_opy_ (u"ࠣࡦ࡬ࡷࡵࡧࡴࡤࡪࠥᕿ"):
            self.logger.debug(bstack11ll1_opy_ (u"ࠤࡕࡩࡹࡻࡲ࡯࡫ࡱ࡫ࠥ࡯࡮ࠡࡦ࡬ࡷࡵࡧࡴࡤࡪࠣࡱࡪࡺࡨࡰࡦ࠯ࠤࡳࡵࡴࠡࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠣᖀ"))
            return
        if not bstack1ll111l11l1_opy_():
            return
        def wrapped(Connection, dispatch, *args, **kwargs):
            data = args[0]
            try:
                if args and args[0].get(bstack11ll1_opy_ (u"ࠪࡴࡦࡸࡡ࡮ࡵࠪᖁ"), {}).get(bstack11ll1_opy_ (u"ࠫࡧࡹࡐࡢࡴࡤࡱࡸ࠭ᖂ")):
                    bstack11lll1llll1_opy_ = args[0][bstack11ll1_opy_ (u"ࠧࡶࡡࡳࡣࡰࡷࠧᖃ")][bstack11ll1_opy_ (u"ࠨࡢࡴࡒࡤࡶࡦࡳࡳࠣᖄ")]
                    session_id = bstack11lll1llll1_opy_.get(bstack11ll1_opy_ (u"ࠢࡴࡧࡶࡷ࡮ࡵ࡮ࡊࡦࠥᖅ"))
                    f.bstack1lll111ll11_opy_(instance, bstack1ll11l11l1l_opy_.bstack1ll11ll1111_opy_, session_id)
            except Exception as e:
                self.logger.debug(bstack11ll1_opy_ (u"ࠣࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡥ࡫ࡶࡴࡦࡺࡣࡩࠢࡰࡩࡹ࡮࡯ࡥ࠼ࠣࠦᖆ"), e)
            dispatch(Connection, *args)
        return wrapped
    def bstack11llll1l1ll_opy_(
        self,
        f: bstack1ll11l11l1l_opy_,
        bstack11llll111ll_opy_: object,
        exec: Tuple[bstack1ll1l1ll1l1_opy_, str],
        bstack1lll1lll111_opy_: Tuple[bstack1ll11lllll1_opy_, bstack1ll11lll1ll_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if method_name != bstack11ll1_opy_ (u"ࠤࡦࡳࡳࡴࡥࡤࡶࠥᖇ"):
            return
        if not bstack1ll111l11l1_opy_():
            self.logger.debug(bstack11ll1_opy_ (u"ࠥࡖࡪࡺࡵࡳࡰ࡬ࡲ࡬ࠦࡩ࡯ࠢࡦࡳࡳࡴࡥࡤࡶࠣࡱࡪࡺࡨࡰࡦ࠯ࠤࡳࡵࡴࠡࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠣᖈ"))
            return
        def wrapped(bstack11llll111ll_opy_, connect, *args, **kwargs):
            response = self.bstack11llll1l1l1_opy_(f.platform_index, instance.ref(), json.dumps({bstack11ll1_opy_ (u"ࠫ࡮ࡹࡐ࡭ࡣࡼࡻࡷ࡯ࡧࡩࡶࠪᖉ"): True}).encode(bstack11ll1_opy_ (u"ࠧࡻࡴࡧ࠯࠻ࠦᖊ")))
            if response is not None and response.capabilities:
                bstack11llll111l1_opy_ = json.loads(response.capabilities.decode(bstack11ll1_opy_ (u"ࠨࡵࡵࡨ࠰࠼ࠧᖋ")))
                if not bstack11llll111l1_opy_:
                    return
                bstack11llll11l11_opy_ = PLAYWRIGHT_HUB_URL + urllib.parse.quote(json.dumps(bstack11llll111l1_opy_))
                if bstack11llll111l1_opy_.get(bstack11ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾ࠭ᖌ")):
                    browser = bstack11llll111ll_opy_.bstack11llll11l1l_opy_(bstack11llll11l11_opy_)
                    return browser
                else:
                    args = list(args)
                    args[0] = bstack11llll11l11_opy_
                    return connect(bstack11llll111ll_opy_, *args, **kwargs)
        return wrapped
    def bstack11llll11lll_opy_(
        self,
        f: bstack1ll11l11l1l_opy_,
        bstack1l111l1111l_opy_: object,
        exec: Tuple[bstack1ll1l1ll1l1_opy_, str],
        bstack1lll1lll111_opy_: Tuple[bstack1ll11lllll1_opy_, bstack1ll11lll1ll_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if method_name != bstack11ll1_opy_ (u"ࠣࡰࡨࡻࡤࡶࡡࡨࡧࠥᖍ"):
            return
        if not bstack1ll111l11l1_opy_():
            self.logger.debug(bstack11ll1_opy_ (u"ࠤࡕࡩࡹࡻࡲ࡯࡫ࡱ࡫ࠥ࡯࡮ࠡࡰࡨࡻࡤࡶࡡࡨࡧࠣࡱࡪࡺࡨࡰࡦ࠯ࠤࡳࡵࡴࠡࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠣᖎ"))
            return
        def wrapped(bstack1l111l1111l_opy_, bstack11llll1111l_opy_, *args, **kwargs):
            contexts = bstack1l111l1111l_opy_.browser.contexts
            if contexts:
                for context in contexts:
                    if context.pages:
                        for page in context.pages:
                            if bstack11ll1_opy_ (u"ࠥࡥࡧࡵࡵࡵ࠼ࡥࡰࡦࡴ࡫ࠣᖏ") in page.url:
                                return page
                            else:
                                return bstack11llll1111l_opy_(bstack1l111l1111l_opy_)
                    else:
                        return bstack11llll1111l_opy_(bstack1l111l1111l_opy_)
        return wrapped
    def bstack11llll1l1l1_opy_(self, platform_index: int, ref, user_input_params: bytes):
        req = structs.DriverInitRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.user_input_params = user_input_params
        req.ref = ref
        self.logger.debug(bstack11ll1_opy_ (u"ࠦࡷ࡫ࡧࡪࡵࡷࡩࡷࡥࡷࡦࡤࡧࡶ࡮ࡼࡥࡳࡡ࡬ࡲ࡮ࡺ࠺ࠡࠤᖐ") + str(req) + bstack11ll1_opy_ (u"ࠧࠨᖑ"))
        try:
            r = self.bstack1lllll11ll1_opy_.DriverInit(req)
            if not r.success:
                self.logger.debug(bstack11ll1_opy_ (u"ࠨࡲࡦࡥࡨ࡭ࡻ࡫ࡤࠡࡨࡵࡳࡲࠦࡳࡦࡴࡹࡩࡷࡀࠠࡴࡷࡦࡧࡪࡹࡳ࠾ࠤᖒ") + str(r.success) + bstack11ll1_opy_ (u"ࠢࠣᖓ"))
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack11ll1_opy_ (u"ࠣࡴࡳࡧ࠲࡫ࡲࡳࡱࡵ࠾ࠥࠨᖔ") + str(e) + bstack11ll1_opy_ (u"ࠤࠥᖕ"))
            traceback.print_exc()
            raise e
    def bstack11llll1l11l_opy_(
        self,
        f: bstack1ll11l11l1l_opy_,
        Connection: object,
        exec: Tuple[bstack1ll1l1ll1l1_opy_, str],
        bstack1lll1lll111_opy_: Tuple[bstack1ll11lllll1_opy_, bstack1ll11lll1ll_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if method_name != bstack11ll1_opy_ (u"ࠥࡣࡸ࡫࡮ࡥࡡࡰࡩࡸࡹࡡࡨࡧࡢࡸࡴࡥࡳࡦࡴࡹࡩࡷࠨᖖ"):
            return
        if not bstack1ll111l11l1_opy_():
            return
        def wrapped(Connection, bstack11lll1lll1l_opy_, *args, **kwargs):
            return bstack11lll1lll1l_opy_(Connection, *args, **kwargs)
        return wrapped
    def on_close(
        self,
        f: bstack1ll11l11l1l_opy_,
        bstack11llll111ll_opy_: object,
        exec: Tuple[bstack1ll1l1ll1l1_opy_, str],
        bstack1lll1lll111_opy_: Tuple[bstack1ll11lllll1_opy_, bstack1ll11lll1ll_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if method_name != bstack11ll1_opy_ (u"ࠦࡨࡲ࡯ࡴࡧࠥᖗ"):
            return
        if not bstack1ll111l11l1_opy_():
            self.logger.debug(bstack11ll1_opy_ (u"ࠧࡘࡥࡵࡷࡵࡲ࡮ࡴࡧࠡ࡫ࡱࠤࡨࡲ࡯ࡴࡧࠣࡱࡪࡺࡨࡰࡦ࠯ࠤࡳࡵࡴࠡࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠣᖘ"))
            return
        def wrapped(Connection, close, *args, **kwargs):
            return close(Connection)
        return wrapped