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
import subprocess
import threading
import time
import sys
import grpc
import os
from browserstack_sdk import sdk_pb2_grpc
from browserstack_sdk import sdk_pb2 as structs
from browserstack_sdk.sdk_cli.bstack1lllll1l11l_opy_ import bstack1lllll11ll1_opy_
from browserstack_sdk.sdk_cli.bstack1ll1l1ll1ll_opy_ import bstack1ll1ll1l1ll_opy_
from browserstack_sdk.sdk_cli.bstack1ll1l1lll11_opy_ import bstack1ll1l11l11l_opy_
from browserstack_sdk.sdk_cli.bstack1lll11111l1_opy_ import bstack1lll11llll1_opy_
from browserstack_sdk.sdk_cli.bstack1ll1lll1l11_opy_ import bstack1lll1l11l1l_opy_
from browserstack_sdk.sdk_cli.bstack1ll1ll1l1l1_opy_ import bstack1ll1ll1llll_opy_
from browserstack_sdk.sdk_cli.bstack1ll11lllll1_opy_ import bstack1ll11ll1l1l_opy_
from browserstack_sdk.sdk_cli.bstack1ll11ll1ll1_opy_ import bstack1lll11l1111_opy_
from browserstack_sdk.sdk_cli.bstack1lll11l1ll1_opy_ import bstack1lll11l11l1_opy_
from browserstack_sdk.sdk_cli.bstack1ll11lll11l_opy_ import bstack1lll111ll1l_opy_
from browserstack_sdk.sdk_cli.bstack1l1l1lllll_opy_ import bstack1l1l1lllll_opy_, bstack111111lll_opy_, bstack1llll1111l_opy_
from browserstack_sdk.sdk_cli.pytest_bdd_framework import PytestBDDFramework
from browserstack_sdk.sdk_cli.bstack1ll1lll1ll1_opy_ import bstack1ll1l11llll_opy_
from browserstack_sdk.sdk_cli.bstack1lll1l11l11_opy_ import bstack1lll11l111l_opy_
from browserstack_sdk.sdk_cli.bstack1llll11l1ll_opy_ import bstack1llll111ll1_opy_
from browserstack_sdk.sdk_cli.bstack1ll1l111ll1_opy_ import bstack1ll1l1111l1_opy_
from bstack_utils.helper import Notset, bstack1ll1l1ll111_opy_, get_cli_dir, bstack1lll1l1lll1_opy_, bstack11ll1l1l_opy_
from browserstack_sdk.sdk_cli.test_framework import TestFramework
from browserstack_sdk.sdk_cli.utils.bstack1ll1llll1l1_opy_ import bstack1ll1llll1ll_opy_
from browserstack_sdk.sdk_cli.utils.bstack1ll1l1l1l_opy_ import bstack1ll111ll1_opy_
from bstack_utils.helper import Notset, bstack1ll1l1ll111_opy_, get_cli_dir, bstack1lll1l1lll1_opy_, bstack11ll1l1l_opy_, bstack1l111l111l_opy_, bstack1l11ll111_opy_
from browserstack_sdk.sdk_cli.test_framework import TestFramework, bstack1lll111l111_opy_, bstack1ll1ll11lll_opy_, bstack1lll1l1l11l_opy_, bstack1lll111l1l1_opy_
from browserstack_sdk.sdk_cli.bstack1llll11l1ll_opy_ import bstack1llll1ll1ll_opy_, bstack1llll1111l1_opy_, bstack1lll1lll1l1_opy_
from bstack_utils.constants import *
from bstack_utils.bstack11llll11ll_opy_ import bstack1ll1l1l11_opy_
from bstack_utils import bstack1l1lll1l11_opy_
from typing import Any, List, Union, Dict
import traceback
from google.protobuf.json_format import MessageToDict
from datetime import datetime, timedelta
from collections import defaultdict
from pathlib import Path
from functools import wraps
from bstack_utils.measure import measure
from bstack_utils.messages import bstack1ll1lll1l1_opy_, bstack111l1lll_opy_
logger = bstack1l1lll1l11_opy_.get_logger(__name__, bstack1l1lll1l11_opy_.bstack1ll1lll1lll_opy_())
def bstack1lll1ll111l_opy_(bs_config):
    bstack1ll1llllll1_opy_ = None
    bstack1ll11llll1l_opy_ = None
    try:
        bstack1ll11llll1l_opy_ = get_cli_dir()
        bstack1ll1llllll1_opy_ = bstack1lll1l1lll1_opy_(bstack1ll11llll1l_opy_)
        bstack1ll1lll1111_opy_ = bstack1ll1l1ll111_opy_(bstack1ll1llllll1_opy_, bstack1ll11llll1l_opy_, bs_config)
        bstack1ll1llllll1_opy_ = bstack1ll1lll1111_opy_ if bstack1ll1lll1111_opy_ else bstack1ll1llllll1_opy_
        if not bstack1ll1llllll1_opy_:
            raise ValueError(bstack11l1l_opy_ (u"ࠤࡘࡲࡦࡨ࡬ࡦࠢࡷࡳࠥ࡬ࡩ࡯ࡦࠣࡗࡉࡑ࡟ࡄࡎࡌࡣࡇࡏࡎࡠࡒࡄࡘࡍࠨᄄ"))
    except Exception as ex:
        logger.debug(bstack11l1l_opy_ (u"ࠥࡉࡷࡸ࡯ࡳࠢࡺ࡬࡮ࡲࡥࠡࡦࡲࡻࡳࡲ࡯ࡢࡦ࡬ࡲ࡬ࠦࡴࡩࡧࠣࡰࡦࡺࡥࡴࡶࠣࡦ࡮ࡴࡡࡳࡻࠣࡿࢂࠨᄅ").format(ex))
        bstack1ll1llllll1_opy_ = os.environ.get(bstack11l1l_opy_ (u"ࠦࡘࡊࡋࡠࡅࡏࡍࡤࡈࡉࡏࡡࡓࡅ࡙ࡎࠢᄆ"))
        if bstack1ll1llllll1_opy_:
            logger.debug(bstack11l1l_opy_ (u"ࠧࡌࡡ࡭࡮࡬ࡲ࡬ࠦࡢࡢࡥ࡮ࠤࡹࡵࠠࡔࡆࡎࡣࡈࡒࡉࡠࡄࡌࡒࡤࡖࡁࡕࡊࠣࡪࡷࡵ࡭ࠡࡧࡱࡺ࡮ࡸ࡯࡯࡯ࡨࡲࡹࡀࠠࠣᄇ") + str(bstack1ll1llllll1_opy_) + bstack11l1l_opy_ (u"ࠨࠢᄈ"))
        else:
            logger.debug(bstack11l1l_opy_ (u"ࠢࡏࡱࠣࡺࡦࡲࡩࡥࠢࡖࡈࡐࡥࡃࡍࡋࡢࡆࡎࡔ࡟ࡑࡃࡗࡌࠥ࡬࡯ࡶࡰࡧࠤ࡮ࡴࠠࡦࡰࡹ࡭ࡷࡵ࡮࡮ࡧࡱࡸࡀࠦࡳࡦࡶࡸࡴࠥࡳࡡࡺࠢࡥࡩࠥ࡯࡮ࡤࡱࡰࡴࡱ࡫ࡴࡦ࠰ࠥᄉ"))
    return bstack1ll1llllll1_opy_, bstack1ll11llll1l_opy_
bstack1lll111ll11_opy_ = bstack11l1l_opy_ (u"ࠣ࠻࠼࠽࠾ࠨᄊ")
bstack1ll1l111111_opy_ = bstack11l1l_opy_ (u"ࠤࡵࡩࡦࡪࡹࠣᄋ")
bstack1ll1l1lllll_opy_ = bstack11l1l_opy_ (u"ࠥࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡆࡐࡎࡥࡂࡊࡐࡢࡗࡊ࡙ࡓࡊࡑࡑࡣࡎࡊࠢᄌ")
bstack1ll1l1l1l11_opy_ = bstack11l1l_opy_ (u"ࠦࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡇࡑࡏ࡟ࡃࡋࡑࡣࡑࡏࡓࡕࡇࡑࡣࡆࡊࡄࡓࠤᄍ")
bstack11ll1l1lll_opy_ = bstack11l1l_opy_ (u"ࠧࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡆ࡛ࡔࡐࡏࡄࡘࡎࡕࡎࠣᄎ")
bstack1ll1lllll1l_opy_ = re.compile(bstack11l1l_opy_ (u"ࡸࠢࠩࡁ࡬࠭࠳࠰ࠨࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࢂࡂࡔࠫ࠱࠮ࠧᄏ"))
bstack1lll11111ll_opy_ = bstack11l1l_opy_ (u"ࠢࡥࡧࡹࡩࡱࡵࡰ࡮ࡧࡱࡸࠧᄐ")
bstack1lll11ll1ll_opy_ = bstack11l1l_opy_ (u"ࠣࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡇࡑࡕࡇࡊࡥࡆࡂࡎࡏࡆࡆࡉࡋࠣᄑ")
bstack1ll1lll11l1_opy_ = [
    bstack111111lll_opy_.bstack1l11ll1l1l_opy_,
    bstack111111lll_opy_.CONNECT,
    bstack111111lll_opy_.bstack1l1111lll1_opy_,
]
class SDKCLI:
    _1ll11ll1lll_opy_ = None
    process: Union[None, Any]
    bstack1ll1ll11ll1_opy_: bool
    bstack1lll1111111_opy_: bool
    bstack1ll1l1l1lll_opy_: bool
    bin_session_id: Union[None, str]
    cli_bin_session_id: Union[None, str]
    cli_listen_addr: Union[None, str]
    bstack1lll11l11ll_opy_: Union[None, grpc.Channel]
    bstack1ll1l11l1l1_opy_: str
    test_framework: TestFramework
    bstack1llll11l1ll_opy_: bstack1llll111ll1_opy_
    session_framework: str
    config: Union[None, Dict[str, Any]]
    bstack1lll1111l11_opy_: bstack1lll111ll1l_opy_
    accessibility: bstack1ll1l11l11l_opy_
    bstack1ll1l1l1l_opy_: bstack1ll111ll1_opy_
    ai: bstack1lll11llll1_opy_
    bstack1lll11ll111_opy_: bstack1lll1l11l1l_opy_
    bstack1ll1l1l11l1_opy_: List[bstack1ll1ll1l1ll_opy_]
    config_testhub: Any
    config_observability: Any
    config_accessibility: Any
    bstack1ll1ll1l111_opy_: Any
    bstack1ll1lllllll_opy_: Dict[str, timedelta]
    bstack1lll1ll1111_opy_: str
    bstack1lllll1l11l_opy_: bstack1lllll11ll1_opy_
    def __new__(cls):
        if not cls._1ll11ll1lll_opy_:
            cls._1ll11ll1lll_opy_ = super(SDKCLI, cls).__new__(cls)
        return cls._1ll11ll1lll_opy_
    def __init__(self):
        self.process = None
        self.bstack1ll1ll11ll1_opy_ = False
        self.bstack1lll11l11ll_opy_ = None
        self.bstack1ll1ll11l11_opy_ = None
        self.cli_bin_session_id = None
        self.cli_listen_addr = os.environ.get(bstack1ll1l1l1l11_opy_, None)
        self.bstack1ll1llll11l_opy_ = os.environ.get(bstack1ll1l1lllll_opy_, bstack11l1l_opy_ (u"ࠤࠥᄒ")) == bstack11l1l_opy_ (u"ࠥࠦᄓ")
        self.bstack1lll1111111_opy_ = False
        self.bstack1ll1l1l1lll_opy_ = False
        self.config = None
        self.config_testhub = None
        self.config_observability = None
        self.config_accessibility = None
        self.bstack1ll1ll1l111_opy_ = None
        self.test_framework = None
        self.bstack1llll11l1ll_opy_ = None
        self.bstack1ll1l11l1l1_opy_=bstack11l1l_opy_ (u"ࠦࠧᄔ")
        self.session_framework = None
        self.logger = bstack1l1lll1l11_opy_.get_logger(self.__class__.__name__, bstack1l1lll1l11_opy_.bstack1ll1lll1lll_opy_())
        self.bstack1ll1lllllll_opy_ = defaultdict(lambda: timedelta(microseconds=0))
        self.bstack1lllll1l11l_opy_ = bstack1lllll11ll1_opy_()
        self.bstack1lll1l1l1ll_opy_ = None
        self.bstack1ll1l111lll_opy_ = None
        self.bstack1lll1111l11_opy_ = None
        self.accessibility = None
        self.ai = None
        self.percy = None
        self.bstack1ll1l1l11l1_opy_ = []
    def bstack11lll11ll1_opy_(self):
        return os.environ.get(bstack11ll1l1lll_opy_).lower().__eq__(bstack11l1l_opy_ (u"ࠧࡺࡲࡶࡧࠥᄕ"))
    def is_enabled(self, config):
        if os.environ.get(bstack1lll11ll1ll_opy_, bstack11l1l_opy_ (u"࠭ࠧᄖ")).lower() in [bstack11l1l_opy_ (u"ࠧࡵࡴࡸࡩࠬᄗ"), bstack11l1l_opy_ (u"ࠨ࠳ࠪᄘ"), bstack11l1l_opy_ (u"ࠩࡼࡩࡸ࠭ᄙ")]:
            self.logger.debug(bstack11l1l_opy_ (u"ࠥࡊࡴࡸࡣࡪࡰࡪࠤ࡫ࡧ࡬࡭ࡤࡤࡧࡰࠦ࡭ࡰࡦࡨࠤࡩࡻࡥࠡࡶࡲࠤࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡊࡔࡘࡃࡆࡡࡉࡅࡑࡒࡂࡂࡅࡎࠤࡪࡴࡶࡪࡴࡲࡲࡲ࡫࡮ࡵࠢࡹࡥࡷ࡯ࡡࡣ࡮ࡨࠦᄚ"))
            os.environ[bstack11l1l_opy_ (u"ࠦࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡆࡎࡔࡁࡓ࡛ࡢࡍࡘࡥࡒࡖࡐࡑࡍࡓࡍࠢᄛ")] = bstack11l1l_opy_ (u"ࠧࡌࡡ࡭ࡵࡨࠦᄜ")
            return False
        if bstack11l1l_opy_ (u"࠭ࡴࡶࡴࡥࡳࡘࡩࡡ࡭ࡧࠪᄝ") in config and str(config[bstack11l1l_opy_ (u"ࠧࡵࡷࡵࡦࡴ࡙ࡣࡢ࡮ࡨࠫᄞ")]).lower() != bstack11l1l_opy_ (u"ࠨࡨࡤࡰࡸ࡫ࠧᄟ"):
            return False
        bstack1ll1l1lll1l_opy_ = [bstack11l1l_opy_ (u"ࠤࡳࡽࡹ࡫ࡳࡵࠤᄠ"), bstack11l1l_opy_ (u"ࠥࡴࡾࡺࡥࡴࡶ࠰ࡦࡩࡪࠢᄡ")]
        bstack1lll1l1l1l1_opy_ = config.get(bstack11l1l_opy_ (u"ࠦ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱࠢᄢ")) in bstack1ll1l1lll1l_opy_ or os.environ.get(bstack11l1l_opy_ (u"ࠬࡌࡒࡂࡏࡈ࡛ࡔࡘࡋࡠࡗࡖࡉࡉ࠭ᄣ")) in bstack1ll1l1lll1l_opy_
        os.environ[bstack11l1l_opy_ (u"ࠨࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡈࡉࡏࡃࡕ࡝ࡤࡏࡓࡠࡔࡘࡒࡓࡏࡎࡈࠤᄤ")] = str(bstack1lll1l1l1l1_opy_) # bstack1ll1l1llll1_opy_ bstack1ll11lll1ll_opy_ VAR to bstack1ll1l11l111_opy_ is binary running
        return bstack1lll1l1l1l1_opy_
    def bstack1lll1l1l1l_opy_(self):
        for event in bstack1ll1lll11l1_opy_:
            bstack1l1l1lllll_opy_.register(
                event, lambda event_name, *args, **kwargs: bstack1l1l1lllll_opy_.logger.debug(bstack11l1l_opy_ (u"ࠢࡼࡧࡹࡩࡳࡺ࡟࡯ࡣࡰࡩࢂࠦ࠽࠿ࠢࡾࡥࡷ࡭ࡳࡾࠢࠥᄥ") + str(kwargs) + bstack11l1l_opy_ (u"ࠣࠤᄦ"))
            )
        bstack1l1l1lllll_opy_.register(bstack111111lll_opy_.bstack1l11ll1l1l_opy_, self.__1ll1ll111ll_opy_)
        bstack1l1l1lllll_opy_.register(bstack111111lll_opy_.CONNECT, self.__1ll1l1ll11l_opy_)
        bstack1l1l1lllll_opy_.register(bstack111111lll_opy_.bstack1l1111lll1_opy_, self.__1lll1l1111l_opy_)
        bstack1l1l1lllll_opy_.register(bstack111111lll_opy_.bstack1lll1111l1_opy_, self.__1lll11ll1l1_opy_)
    def bstack1l1l111ll_opy_(self):
        return not self.bstack1ll1llll11l_opy_ and os.environ.get(bstack1ll1l1lllll_opy_, bstack11l1l_opy_ (u"ࠤࠥᄧ")) != bstack11l1l_opy_ (u"ࠥࠦᄨ")
    def is_running(self):
        if self.bstack1ll1llll11l_opy_:
            return self.bstack1ll1ll11ll1_opy_
        else:
            return bool(self.bstack1lll11l11ll_opy_)
    def bstack1lll1l111ll_opy_(self, module):
        return any(isinstance(m, module) for m in self.bstack1ll1l1l11l1_opy_) and cli.is_running()
    def __1ll1l1l1l1l_opy_(self, bstack1ll1ll1ll1l_opy_=10):
        if self.bstack1ll1ll11l11_opy_:
            return
        bstack11ll1l1ll1_opy_ = datetime.now()
        cli_listen_addr = os.environ.get(bstack1ll1l1l1l11_opy_, self.cli_listen_addr)
        self.logger.debug(bstack11l1l_opy_ (u"ࠦࡠࠨᄩ") + str(id(self)) + bstack11l1l_opy_ (u"ࠧࡣࠠࡤࡱࡱࡲࡪࡩࡴࡪࡰࡪࠦᄪ"))
        channel = grpc.insecure_channel(cli_listen_addr, options=[(bstack11l1l_opy_ (u"ࠨࡧࡳࡲࡦ࠲ࡪࡴࡡࡣ࡮ࡨࡣ࡭ࡺࡴࡱࡡࡳࡶࡴࡾࡹࠣᄫ"), 0), (bstack11l1l_opy_ (u"ࠢࡨࡴࡳࡧ࠳࡫࡮ࡢࡤ࡯ࡩࡤ࡮ࡴࡵࡲࡶࡣࡵࡸ࡯ࡹࡻࠥᄬ"), 0)])
        grpc.channel_ready_future(channel).result(timeout=bstack1ll1ll1ll1l_opy_)
        self.bstack1lll11l11ll_opy_ = channel
        self.bstack1ll1ll11l11_opy_ = sdk_pb2_grpc.SDKStub(self.bstack1lll11l11ll_opy_)
        self.bstack11lll111_opy_(bstack11l1l_opy_ (u"ࠣࡩࡵࡴࡨࡀࡣࡰࡰࡱࡩࡨࡺࠢᄭ"), datetime.now() - bstack11ll1l1ll1_opy_)
        self.cli_listen_addr = cli_listen_addr
        os.environ[bstack1ll1l1l1l11_opy_] = self.cli_listen_addr
        self.logger.debug(bstack11l1l_opy_ (u"ࠤ࡞ࡿ࡮ࡪࠨࡴࡧ࡯ࡪ࠮ࢃ࡝ࠡࡥࡲࡲࡳ࡫ࡣࡵࡧࡧ࠾ࠥ࡯ࡳࡠࡥ࡫࡭ࡱࡪ࡟ࡱࡴࡲࡧࡪࡹࡳ࠾ࠤᄮ") + str(self.bstack1l1l111ll_opy_()) + bstack11l1l_opy_ (u"ࠥࠦᄯ"))
    def __1lll1l1111l_opy_(self, event_name):
        if self.bstack1l1l111ll_opy_():
            self.logger.debug(bstack11l1l_opy_ (u"ࠦࡨ࡮ࡩ࡭ࡦ࠰ࡴࡷࡵࡣࡦࡵࡶ࠾ࠥࡹࡴࡰࡲࡳ࡭ࡳ࡭ࠠࡄࡎࡌࠦᄰ"))
        self.__1ll1l11111l_opy_()
    def __1lll11ll1l1_opy_(self, event_name, bstack1lll11lllll_opy_ = None, exit_code=1):
        if exit_code == 1:
            self.logger.error(bstack11l1l_opy_ (u"࡙ࠧ࡯࡮ࡧࡷ࡬࡮ࡴࡧࠡࡹࡨࡲࡹࠦࡷࡳࡱࡱ࡫ࠧᄱ"))
        bstack1lll11l1lll_opy_ = Path(bstack1ll1l11l1ll_opy_ (u"ࠨࡻࡴࡧ࡯ࡪ࠳ࡩ࡬ࡪࡡࡧ࡭ࡷࢃ࠯ࡶࡰ࡫ࡥࡳࡪ࡬ࡦࡦࡈࡶࡷࡵࡲࡴ࠰࡭ࡷࡴࡴࠢᄲ"))
        if self.bstack1ll11llll1l_opy_ and bstack1lll11l1lll_opy_.exists():
            with open(bstack1lll11l1lll_opy_, bstack11l1l_opy_ (u"ࠧࡳࠩᄳ"), encoding=bstack11l1l_opy_ (u"ࠨࡷࡷࡪ࠲࠾ࠧᄴ")) as fp:
                data = json.load(fp)
                try:
                    bstack1l111l111l_opy_(bstack11l1l_opy_ (u"ࠩࡓࡓࡘ࡚ࠧᄵ"), bstack1ll1l1l11_opy_(bstack1111l11ll_opy_), data, {
                        bstack11l1l_opy_ (u"ࠪࡥࡺࡺࡨࠨᄶ"): (self.config[bstack11l1l_opy_ (u"ࠫࡺࡹࡥࡳࡐࡤࡱࡪ࠭ᄷ")], self.config[bstack11l1l_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷࡐ࡫ࡹࠨᄸ")])
                    })
                except Exception as e:
                    logger.debug(bstack111l1lll_opy_.format(str(e)))
            bstack1lll11l1lll_opy_.unlink()
        sys.exit(exit_code)
    @measure(event_name=EVENTS.bstack1ll1ll11111_opy_, stage=STAGE.bstack1lll1l11l_opy_)
    def __1ll1ll111ll_opy_(self, event_name: str, data):
        from bstack_utils.bstack11l1l11ll_opy_ import bstack1lll1ll1l11_opy_
        self.bstack1ll1l11l1l1_opy_, self.bstack1ll11llll1l_opy_ = bstack1lll1ll111l_opy_(data.bs_config)
        os.environ[bstack11l1l_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡝ࡒࡊࡖࡄࡆࡑࡋ࡟ࡅࡋࡕࠫᄹ")] = self.bstack1ll11llll1l_opy_
        if not self.bstack1ll1l11l1l1_opy_ or not self.bstack1ll11llll1l_opy_:
            raise ValueError(bstack11l1l_opy_ (u"ࠢࡖࡰࡤࡦࡱ࡫ࠠࡵࡱࠣࡪ࡮ࡴࡤࠡࡶ࡫ࡩ࡙ࠥࡄࡌࠢࡆࡐࡎࠦࡢࡪࡰࡤࡶࡾࠨᄺ"))
        if self.bstack1l1l111ll_opy_():
            self.__1ll1l1ll11l_opy_(event_name, bstack1llll1111l_opy_())
            return
        try:
            bstack1lll1ll1l11_opy_.end(EVENTS.bstack11l1l111l_opy_.value, EVENTS.bstack11l1l111l_opy_.value + bstack11l1l_opy_ (u"ࠣ࠼ࡶࡸࡦࡸࡴࠣᄻ"), EVENTS.bstack11l1l111l_opy_.value + bstack11l1l_opy_ (u"ࠤ࠽ࡩࡳࡪࠢᄼ"), status=True, failure=None, test_name=None)
            logger.debug(bstack11l1l_opy_ (u"ࠥࡇࡴࡳࡰ࡭ࡧࡷࡩ࡙ࠥࡄࡌࠢࡖࡩࡹࡻࡰ࠯ࠤᄽ"))
        except Exception as e:
            logger.debug(bstack11l1l_opy_ (u"ࠦࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡸࡪ࡬ࡰࡪࠦ࡭ࡢࡴ࡮࡭ࡳ࡭ࠠ࡬ࡧࡼࠤࡲ࡫ࡴࡳ࡫ࡦࡷࠥࢁࡽࠣᄾ").format(e))
        start = datetime.now()
        is_started = self.__1lll1l1ll1l_opy_()
        self.bstack11lll111_opy_(bstack11l1l_opy_ (u"ࠧࡹࡰࡢࡹࡱࡣࡹ࡯࡭ࡦࠤᄿ"), datetime.now() - start)
        if is_started:
            start = datetime.now()
            self.__1ll1l1l1l1l_opy_()
            self.bstack11lll111_opy_(bstack11l1l_opy_ (u"ࠨࡣࡰࡰࡱࡩࡨࡺ࡟ࡵ࡫ࡰࡩࠧᅀ"), datetime.now() - start)
            start = datetime.now()
            self.__1ll1lll1l1l_opy_(data)
            self.bstack11lll111_opy_(bstack11l1l_opy_ (u"ࠢࡴࡶࡤࡶࡹࡥࡳࡦࡵࡶ࡭ࡴࡴ࡟ࡵ࡫ࡰࡩࠧᅁ"), datetime.now() - start)
    @measure(event_name=EVENTS.bstack1ll1lllll11_opy_, stage=STAGE.bstack1lll1l11l_opy_)
    def __1ll1l1ll11l_opy_(self, event_name: str, data: bstack1llll1111l_opy_):
        if not self.bstack1l1l111ll_opy_():
            self.logger.debug(bstack11l1l_opy_ (u"ࠣࡨࡤ࡭ࡱ࡫ࡤࠡࡶࡲࠤࡨࡵ࡮࡯ࡧࡦࡸ࠿ࠦ࡮ࡰࡶࠣࡥࠥࡩࡨࡪ࡮ࡧ࠱ࡵࡸ࡯ࡤࡧࡶࡷࠧᅂ"))
            return
        bin_session_id = os.environ.get(bstack1ll1l1lllll_opy_)
        start = datetime.now()
        self.__1ll1l1l1l1l_opy_()
        self.bstack11lll111_opy_(bstack11l1l_opy_ (u"ࠤࡦࡳࡳࡴࡥࡤࡶࡢࡸ࡮ࡳࡥࠣᅃ"), datetime.now() - start)
        self.cli_bin_session_id = bin_session_id
        self.logger.debug(bstack11l1l_opy_ (u"ࠥ࡟ࢀ࡯ࡤࠩࡵࡨࡰ࡫࠯ࡽ࡞ࠢࡦ࡬࡮ࡲࡤ࠮ࡲࡵࡳࡨ࡫ࡳࡴ࠼ࠣࡧࡴࡴ࡮ࡦࡥࡷࡩࡩࠦࡴࡰࠢࡨࡼ࡮ࡹࡴࡪࡰࡪࠤࡈࡒࡉࠡࠤᅄ") + str(bin_session_id) + bstack11l1l_opy_ (u"ࠦࠧᅅ"))
        start = datetime.now()
        self.__1ll1ll111l1_opy_()
        self.bstack11lll111_opy_(bstack11l1l_opy_ (u"ࠧࡹࡴࡢࡴࡷࡣࡸ࡫ࡳࡴ࡫ࡲࡲࡤࡺࡩ࡮ࡧࠥᅆ"), datetime.now() - start)
    def __1lll1111l1l_opy_(self):
        if not self.bstack1ll1ll11l11_opy_ or not self.cli_bin_session_id:
            self.logger.debug(bstack11l1l_opy_ (u"ࠨࡣࡢࡰࡱࡳࡹࠦࡣࡰࡰࡩ࡭࡬ࡻࡲࡦࠢࡰࡳࡩࡻ࡬ࡦࡵࠥᅇ"))
            return
        bstack1lll1ll11l1_opy_ = {
            bstack11l1l_opy_ (u"ࠢࡱ࡮ࡤࡽࡼࡸࡩࡨࡪࡷࠦᅈ"): (bstack1lll11l1111_opy_, bstack1lll11l11l1_opy_, bstack1ll1l1111l1_opy_),
            bstack11l1l_opy_ (u"ࠣࡵࡨࡰࡪࡴࡩࡶ࡯ࠥᅉ"): (bstack1ll1ll1llll_opy_, bstack1ll11ll1l1l_opy_, bstack1lll11l111l_opy_),
        }
        if not self.bstack1lll1l1l1ll_opy_ and self.session_framework in bstack1lll1ll11l1_opy_:
            bstack1ll11lll111_opy_, bstack1ll11ll1l11_opy_, bstack1ll1l11ll1l_opy_ = bstack1lll1ll11l1_opy_[self.session_framework]
            bstack1ll1l1l1111_opy_ = bstack1ll11ll1l11_opy_()
            self.bstack1ll1l111lll_opy_ = bstack1ll1l1l1111_opy_
            self.bstack1lll1l1l1ll_opy_ = bstack1ll1l11ll1l_opy_
            self.bstack1ll1l1l11l1_opy_.append(bstack1ll1l1l1111_opy_)
            self.bstack1ll1l1l11l1_opy_.append(bstack1ll11lll111_opy_(self.bstack1ll1l111lll_opy_))
        if not self.bstack1lll1111l11_opy_ and self.config_observability and self.config_observability.success: # bstack1ll1ll1ll11_opy_
            self.bstack1lll1111l11_opy_ = bstack1lll111ll1l_opy_(self.bstack1lll1l1l1ll_opy_, self.bstack1ll1l111lll_opy_) # bstack1ll1l111l11_opy_
            self.bstack1ll1l1l11l1_opy_.append(self.bstack1lll1111l11_opy_)
        if not self.accessibility and self.config_accessibility and self.config_accessibility.success:
            self.accessibility = bstack1ll1l11l11l_opy_(self.bstack1lll1l1l1ll_opy_, self.bstack1ll1l111lll_opy_)
            self.bstack1ll1l1l11l1_opy_.append(self.accessibility)
        if not self.ai and isinstance(self.config, dict) and self.config.get(bstack11l1l_opy_ (u"ࠤࡶࡩࡱ࡬ࡈࡦࡣ࡯ࠦᅊ"), False) == True:
            self.ai = bstack1lll11llll1_opy_()
            self.bstack1ll1l1l11l1_opy_.append(self.ai)
        if not self.percy and self.bstack1ll1ll1l111_opy_ and self.bstack1ll1ll1l111_opy_.success:
            self.percy = bstack1lll1l11l1l_opy_(self.bstack1ll1ll1l111_opy_)
            self.bstack1ll1l1l11l1_opy_.append(self.percy)
        for mod in self.bstack1ll1l1l11l1_opy_:
            if not mod.bstack1lll1l11lll_opy_():
                mod.configure(self.bstack1ll1ll11l11_opy_, self.config, self.cli_bin_session_id, self.bstack1lllll1l11l_opy_)
    def __1lll1111lll_opy_(self):
        for mod in self.bstack1ll1l1l11l1_opy_:
            if mod.bstack1lll1l11lll_opy_():
                mod.configure(self.bstack1ll1ll11l11_opy_, None, None, None)
    @measure(event_name=EVENTS.bstack1lll1ll11ll_opy_, stage=STAGE.bstack1lll1l11l_opy_)
    def __1ll1lll1l1l_opy_(self, data):
        if not self.cli_bin_session_id or self.bstack1lll1111111_opy_:
            return
        self.__1ll1llll111_opy_(data)
        bstack11ll1l1ll1_opy_ = datetime.now()
        req = structs.StartBinSessionRequest()
        req.bin_session_id = self.cli_bin_session_id
        req.path_project = os.getcwd()
        req.language = bstack11l1l_opy_ (u"ࠥࡴࡾࡺࡨࡰࡰࠥᅋ")
        req.sdk_language = bstack11l1l_opy_ (u"ࠦࡵࡿࡴࡩࡱࡱࠦᅌ")
        req.path_config = data.path_config
        req.sdk_version = data.sdk_version
        req.test_framework = data.test_framework
        req.frameworks.extend(data.frameworks)
        req.framework_versions.update(data.framework_versions)
        req.env_vars.update({key: value for key, value in os.environ.items() if bool(bstack1ll1lllll1l_opy_.search(key))})
        req.cli_args.extend(sys.argv)
        try:
            self.logger.debug(bstack11l1l_opy_ (u"ࠧࡡࠢᅍ") + str(id(self)) + bstack11l1l_opy_ (u"ࠨ࡝ࠡ࡯ࡤ࡭ࡳ࠳ࡰࡳࡱࡦࡩࡸࡹ࠺ࠡࡵࡷࡥࡷࡺ࡟ࡣ࡫ࡱࡣࡸ࡫ࡳࡴ࡫ࡲࡲࠧᅎ"))
            r = self.bstack1ll1ll11l11_opy_.StartBinSession(req)
            self.bstack11lll111_opy_(bstack11l1l_opy_ (u"ࠢࡨࡴࡳࡧ࠿ࡹࡴࡢࡴࡷࡣࡧ࡯࡮ࡠࡵࡨࡷࡸ࡯࡯࡯ࠤᅏ"), datetime.now() - bstack11ll1l1ll1_opy_)
            os.environ[bstack1ll1l1lllll_opy_] = r.bin_session_id
            self.__1ll1l11ll11_opy_(r)
            self.__1lll1111l1l_opy_()
            self.bstack1lllll1l11l_opy_.start()
            self.bstack1lll1111111_opy_ = True
            self.logger.debug(bstack11l1l_opy_ (u"ࠣ࡝ࠥᅐ") + str(id(self)) + bstack11l1l_opy_ (u"ࠤࡠࠤࡲࡧࡩ࡯࠯ࡳࡶࡴࡩࡥࡴࡵ࠽ࠤࡨࡵ࡮࡯ࡧࡦࡸࡪࡪࠢᅑ"))
        except grpc.bstack1lll11lll1l_opy_ as bstack1lll111l1ll_opy_:
            self.logger.error(bstack11l1l_opy_ (u"ࠥ࡟ࢀ࡯ࡤࠩࡵࡨࡰ࡫࠯ࡽ࡞ࠢࡷ࡭ࡲ࡫࡯ࡦࡷࡷ࠱ࡪࡸࡲࡰࡴ࠽ࠤࠧᅒ") + str(bstack1lll111l1ll_opy_) + bstack11l1l_opy_ (u"ࠦࠧᅓ"))
            traceback.print_exc()
            raise bstack1lll111l1ll_opy_
        except grpc.RpcError as e:
            self.logger.error(bstack11l1l_opy_ (u"ࠧࡡࡻࡪࡦࠫࡷࡪࡲࡦࠪࡿࡠࠤࡷࡶࡣ࠮ࡧࡵࡶࡴࡸ࠺ࠡࠤᅔ") + str(e) + bstack11l1l_opy_ (u"ࠨࠢᅕ"))
            traceback.print_exc()
            raise e
    @measure(event_name=EVENTS.bstack1lll11lll11_opy_, stage=STAGE.bstack1lll1l11l_opy_)
    def __1ll1ll111l1_opy_(self):
        if not self.bstack1l1l111ll_opy_() or not self.cli_bin_session_id or self.bstack1ll1l1l1lll_opy_:
            return
        bstack11ll1l1ll1_opy_ = datetime.now()
        req = structs.ConnectBinSessionRequest()
        req.bin_session_id = self.cli_bin_session_id
        req.platform_index = int(os.environ.get(bstack11l1l_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡐࡍࡃࡗࡊࡔࡘࡍࡠࡋࡑࡈࡊ࡞ࠧᅖ"), bstack11l1l_opy_ (u"ࠨ࠲ࠪᅗ")))
        try:
            self.logger.debug(bstack11l1l_opy_ (u"ࠤ࡞ࠦᅘ") + str(id(self)) + bstack11l1l_opy_ (u"ࠥࡡࠥࡩࡨࡪ࡮ࡧ࠱ࡵࡸ࡯ࡤࡧࡶࡷ࠿ࠦࡣࡰࡰࡱࡩࡨࡺ࡟ࡣ࡫ࡱࡣࡸ࡫ࡳࡴ࡫ࡲࡲࠧᅙ"))
            r = self.bstack1ll1ll11l11_opy_.ConnectBinSession(req)
            self.bstack11lll111_opy_(bstack11l1l_opy_ (u"ࠦ࡬ࡸࡰࡤ࠼ࡦࡳࡳࡴࡥࡤࡶࡢࡦ࡮ࡴ࡟ࡴࡧࡶࡷ࡮ࡵ࡮ࠣᅚ"), datetime.now() - bstack11ll1l1ll1_opy_)
            self.__1ll1l11ll11_opy_(r)
            self.__1lll1111l1l_opy_()
            self.bstack1lllll1l11l_opy_.start()
            self.bstack1ll1l1l1lll_opy_ = True
            self.logger.debug(bstack11l1l_opy_ (u"ࠧࡡࠢᅛ") + str(id(self)) + bstack11l1l_opy_ (u"ࠨ࡝ࠡࡥ࡫࡭ࡱࡪ࠭ࡱࡴࡲࡧࡪࡹࡳ࠻ࠢࡦࡳࡳࡴࡥࡤࡶࡨࡨࠧᅜ"))
        except grpc.bstack1lll11lll1l_opy_ as bstack1lll111l1ll_opy_:
            self.logger.error(bstack11l1l_opy_ (u"ࠢ࡜ࡽ࡬ࡨ࠭ࡹࡥ࡭ࡨࠬࢁࡢࠦࡴࡪ࡯ࡨࡳࡪࡻࡴ࠮ࡧࡵࡶࡴࡸ࠺ࠡࠤᅝ") + str(bstack1lll111l1ll_opy_) + bstack11l1l_opy_ (u"ࠣࠤᅞ"))
            traceback.print_exc()
            raise bstack1lll111l1ll_opy_
        except grpc.RpcError as e:
            self.logger.error(bstack11l1l_opy_ (u"ࠤ࡞ࡿ࡮ࡪࠨࡴࡧ࡯ࡪ࠮ࢃ࡝ࠡࡴࡳࡧ࠲࡫ࡲࡳࡱࡵ࠾ࠥࠨᅟ") + str(e) + bstack11l1l_opy_ (u"ࠥࠦᅠ"))
            traceback.print_exc()
            raise e
    def __1ll1l11ll11_opy_(self, r):
        self.bstack1ll1l1l111l_opy_(r)
        if not r.bin_session_id or not r.config or not isinstance(r.config, str):
            raise ValueError(bstack11l1l_opy_ (u"ࠦࡺࡴࡥࡹࡲࡨࡧࡹ࡫ࡤࠡࡵࡨࡶࡻ࡫ࡲࠡࡴࡨࡷࡵࡵ࡮ࡴࡧࠥᅡ") + str(r))
        self.config = json.loads(r.config)
        if not self.config:
            raise ValueError(bstack11l1l_opy_ (u"ࠧ࡫࡭ࡱࡶࡼࠤࡨࡵ࡮ࡧ࡫ࡪࠤ࡫ࡵࡵ࡯ࡦࠥᅢ"))
        self.session_framework = r.session_framework
        self.config_testhub = r.testhub
        self.config_observability = r.observability
        self.config_accessibility = r.accessibility
        bstack11l1l_opy_ (u"ࠨࠢࠣࠌࠣࠤࠥࠦࠠࠡࠢࠣࡔࡪࡸࡣࡺࠢ࡬ࡷࠥࡹࡥ࡯ࡶࠣࡳࡳࡲࡹࠡࡣࡶࠤࡵࡧࡲࡵࠢࡲࡪࠥࡺࡨࡦࠢࠥࡇࡴࡴ࡮ࡦࡥࡷࡆ࡮ࡴࡓࡦࡵࡶ࡭ࡴࡴࠬࠣࠢࡤࡲࡩࠦࡴࡩ࡫ࡶࠤ࡫ࡻ࡮ࡤࡶ࡬ࡳࡳࠦࡩࡴࠢࡤࡰࡸࡵࠠࡶࡵࡨࡨࠥࡨࡹࠡࡕࡷࡥࡷࡺࡂࡪࡰࡖࡩࡸࡹࡩࡰࡰ࠱ࠎࠥࠦࠠࠡࠢࠣࠤ࡚ࠥࡨࡦࡴࡨࡪࡴࡸࡥ࠭ࠢࡑࡳࡳ࡫ࠠࡩࡣࡱࡨࡱ࡯࡮ࡨࠢ࡬ࡷࠥ࡯࡭ࡱ࡮ࡨࡱࡪࡴࡴࡦࡦ࠱ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠨࠢࠣᅣ")
        self.bstack1ll1ll1l111_opy_ = getattr(r, bstack11l1l_opy_ (u"ࠧࡱࡧࡵࡧࡾ࠭ᅤ"), None)
        self.cli_bin_session_id = r.bin_session_id
        os.environ[bstack11l1l_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡍ࡛ࡂࡠࡌ࡚ࡘࠬᅥ")] = self.config_testhub.jwt
        os.environ[bstack11l1l_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡘ࡙ࡎࡊࠧᅦ")] = self.config_testhub.build_hashed_id
    def bstack1lll1l1l111_opy_(event_name: EVENTS, stage: STAGE):
        def decorator(func):
            @wraps(func)
            def wrapper(self, *args, **kwargs):
                if self.bstack1ll1ll11ll1_opy_:
                    return func(self, *args, **kwargs)
                @measure(event_name=event_name, stage=stage)
                def bstack1lll11ll11l_opy_(*a, **kw):
                    return func(self, *a, **kw)
                return bstack1lll11ll11l_opy_(*args, **kwargs)
            return wrapper
        return decorator
    @bstack1lll1l1l111_opy_(event_name=EVENTS.bstack1lll11l1l11_opy_, stage=STAGE.bstack1lll1l11l_opy_)
    def __1lll1l1ll1l_opy_(self, bstack1ll1ll1ll1l_opy_=10):
        if self.bstack1ll1ll11ll1_opy_:
            self.logger.debug(bstack11l1l_opy_ (u"ࠥࡷࡹࡧࡲࡵ࠼ࠣࡥࡱࡸࡥࡢࡦࡼࠤࡷࡻ࡮࡯࡫ࡱ࡫ࠧᅧ"))
            return True
        self.logger.debug(bstack11l1l_opy_ (u"ࠦࡸࡺࡡࡳࡶࠥᅨ"))
        if os.getenv(bstack11l1l_opy_ (u"ࠧࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡈࡒࡉࡠࡇࡑ࡚ࠧᅩ")) == bstack1lll11111ll_opy_:
            self.cli_bin_session_id = bstack1lll11111ll_opy_
            self.cli_listen_addr = bstack11l1l_opy_ (u"ࠨࡵ࡯࡫ࡻ࠾࠴ࡺ࡭ࡱ࠱ࡶࡨࡰ࠳ࡰ࡭ࡣࡷࡪࡴࡸ࡭࠮ࠧࡶ࠲ࡸࡵࡣ࡬ࠤᅪ") % (self.cli_bin_session_id)
            self.bstack1ll1ll11ll1_opy_ = True
            return True
        self.process = subprocess.Popen(
            [self.bstack1ll1l11l1l1_opy_, bstack11l1l_opy_ (u"ࠢࡴࡦ࡮ࠦᅫ")],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=dict(os.environ),
            text=True,
            universal_newlines=True, # bstack1lll1l111l1_opy_ compat for text=True in bstack1lll1l11ll1_opy_ python
            encoding=bstack11l1l_opy_ (u"ࠣࡷࡷࡪ࠲࠾ࠢᅬ"),
            bufsize=1,
            close_fds=True,
        )
        bstack1lll1l1llll_opy_ = threading.Thread(target=self.__1lll1l11111_opy_, args=(bstack1ll1ll1ll1l_opy_,))
        bstack1lll1l1llll_opy_.start()
        bstack1lll1l1llll_opy_.join()
        if self.process.returncode is not None:
            self.logger.debug(bstack11l1l_opy_ (u"ࠤ࡞ࡿ࡮ࡪࠨࡴࡧ࡯ࡪ࠮ࢃ࡝ࠡࡵࡳࡥࡼࡴ࠺ࠡࡴࡨࡸࡺࡸ࡮ࡤࡱࡧࡩࡂࢁࡳࡦ࡮ࡩ࠲ࡵࡸ࡯ࡤࡧࡶࡷ࠳ࡸࡥࡵࡷࡵࡲࡨࡵࡤࡦࡿࠣࡳࡺࡺ࠽ࡼࡵࡨࡰ࡫࠴ࡰࡳࡱࡦࡩࡸࡹ࠮ࡴࡶࡧࡳࡺࡺ࠮ࡳࡧࡤࡨ࠭࠯ࡽࠡࡧࡵࡶࡂࠨᅭ") + str(self.process.stderr.read()) + bstack11l1l_opy_ (u"ࠥࠦᅮ"))
        if not self.bstack1ll1ll11ll1_opy_:
            self.logger.debug(bstack11l1l_opy_ (u"ࠦࡠࠨᅯ") + str(id(self)) + bstack11l1l_opy_ (u"ࠧࡣࠠࡤ࡮ࡨࡥࡳࡻࡰࠣᅰ"))
            self.__1ll1l11111l_opy_()
        self.logger.debug(bstack11l1l_opy_ (u"ࠨ࡛ࡼ࡫ࡧࠬࡸ࡫࡬ࡧࠫࢀࡡࠥࡶࡲࡰࡥࡨࡷࡸࡥࡲࡦࡣࡧࡽ࠿ࠦࠢᅱ") + str(self.bstack1ll1ll11ll1_opy_) + bstack11l1l_opy_ (u"ࠢࠣᅲ"))
        return self.bstack1ll1ll11ll1_opy_
    def __1lll1l11111_opy_(self, bstack1ll1l111l1l_opy_=10):
        bstack1ll1l11lll1_opy_ = time.time()
        while self.process and time.time() - bstack1ll1l11lll1_opy_ < bstack1ll1l111l1l_opy_:
            try:
                line = self.process.stdout.readline()
                if bstack11l1l_opy_ (u"ࠣ࡫ࡧࡁࠧᅳ") in line:
                    self.cli_bin_session_id = line.split(bstack11l1l_opy_ (u"ࠤ࡬ࡨࡂࠨᅴ"))[-1:][0].strip()
                    self.logger.debug(bstack11l1l_opy_ (u"ࠥࡧࡱ࡯࡟ࡣ࡫ࡱࡣࡸ࡫ࡳࡴ࡫ࡲࡲࡤ࡯ࡤ࠻ࠤᅵ") + str(self.cli_bin_session_id) + bstack11l1l_opy_ (u"ࠦࠧᅶ"))
                    continue
                if bstack11l1l_opy_ (u"ࠧࡲࡩࡴࡶࡨࡲࡂࠨᅷ") in line:
                    self.cli_listen_addr = line.split(bstack11l1l_opy_ (u"ࠨ࡬ࡪࡵࡷࡩࡳࡃࠢᅸ"))[-1:][0].strip()
                    self.logger.debug(bstack11l1l_opy_ (u"ࠢࡤ࡮࡬ࡣࡱ࡯ࡳࡵࡧࡱࡣࡦࡪࡤࡳ࠼ࠥᅹ") + str(self.cli_listen_addr) + bstack11l1l_opy_ (u"ࠣࠤᅺ"))
                    continue
                if bstack11l1l_opy_ (u"ࠤࡳࡳࡷࡺ࠽ࠣᅻ") in line:
                    port = line.split(bstack11l1l_opy_ (u"ࠥࡴࡴࡸࡴ࠾ࠤᅼ"))[-1:][0].strip()
                    self.logger.debug(bstack11l1l_opy_ (u"ࠦࡵࡵࡲࡵ࠼ࠥᅽ") + str(port) + bstack11l1l_opy_ (u"ࠧࠨᅾ"))
                    continue
                if line.strip() == bstack1ll1l111111_opy_ and self.cli_bin_session_id and self.cli_listen_addr:
                    if os.getenv(bstack11l1l_opy_ (u"ࠨࡓࡅࡍࡢࡇࡑࡏ࡟ࡇࡎࡄࡋࡤࡏࡏࡠࡕࡗࡖࡊࡇࡍࠣᅿ"), bstack11l1l_opy_ (u"ࠢ࠲ࠤᆀ")) == bstack11l1l_opy_ (u"ࠣ࠳ࠥᆁ"):
                        if not self.process.stdout.closed:
                            self.process.stdout.close()
                        if not self.process.stderr.closed:
                            self.process.stderr.close()
                    self.bstack1ll1ll11ll1_opy_ = True
                    return True
            except Exception as e:
                self.logger.debug(bstack11l1l_opy_ (u"ࠤࡨࡶࡷࡵࡲ࠻ࠢࠥᆂ") + str(e) + bstack11l1l_opy_ (u"ࠥࠦᆃ"))
        return False
    @measure(event_name=EVENTS.bstack1lll111111l_opy_, stage=STAGE.bstack1lll1l11l_opy_)
    def __1ll1l11111l_opy_(self):
        if self.bstack1lll11l11ll_opy_:
            self.bstack1lllll1l11l_opy_.stop()
            start = datetime.now()
            if self.bstack1ll11llll11_opy_():
                self.cli_bin_session_id = None
                if self.bstack1ll1l1l1lll_opy_:
                    self.bstack11lll111_opy_(bstack11l1l_opy_ (u"ࠦࡸࡺ࡯ࡱࡡࡶࡩࡸࡹࡩࡰࡰࡢࡸ࡮ࡳࡥࠣᆄ"), datetime.now() - start)
                else:
                    self.bstack11lll111_opy_(bstack11l1l_opy_ (u"ࠧࡹࡴࡰࡲࡢࡷࡪࡹࡳࡪࡱࡱࡣࡹ࡯࡭ࡦࠤᆅ"), datetime.now() - start)
            self.__1lll1111lll_opy_()
            start = datetime.now()
            self.bstack1lll11l11ll_opy_.close()
            self.bstack11lll111_opy_(bstack11l1l_opy_ (u"ࠨࡤࡪࡵࡦࡳࡳࡴࡥࡤࡶࡢࡸ࡮ࡳࡥࠣᆆ"), datetime.now() - start)
            self.bstack1lll11l11ll_opy_ = None
        if self.process:
            self.logger.debug(bstack11l1l_opy_ (u"ࠢࡴࡶࡲࡴࠧᆇ"))
            start = datetime.now()
            self.process.terminate()
            self.bstack11lll111_opy_(bstack11l1l_opy_ (u"ࠣ࡭࡬ࡰࡱࡥࡴࡪ࡯ࡨࠦᆈ"), datetime.now() - start)
            self.process = None
            if self.bstack1ll1llll11l_opy_ and self.config_observability and self.config_testhub and self.config_testhub.testhub_events:
                self.bstack1l11l1111_opy_()
                self.logger.info(
                    bstack11l1l_opy_ (u"ࠤ࡙࡭ࡸ࡯ࡴࠡࡪࡷࡸࡵࡹ࠺࠰࠱ࡤࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡩ࡯࡮࠱ࡥࡹ࡮ࡲࡤࡴ࠱ࡾࢁࠥࡺ࡯ࠡࡸ࡬ࡩࡼࠦࡢࡶ࡫࡯ࡨࠥࡸࡥࡱࡱࡵࡸ࠱ࠦࡩ࡯ࡵ࡬࡫࡭ࡺࡳ࠭ࠢࡤࡲࡩࠦ࡭ࡢࡰࡼࠤࡲࡵࡲࡦࠢࡧࡩࡧࡻࡧࡨ࡫ࡱ࡫ࠥ࡯࡮ࡧࡱࡵࡱࡦࡺࡩࡰࡰࠣࡥࡱࡲࠠࡢࡶࠣࡳࡳ࡫ࠠࡱ࡮ࡤࡧࡪࠧ࡜࡯ࠤᆉ").format(
                        self.config_testhub.build_hashed_id
                    )
                )
                os.environ[bstack11l1l_opy_ (u"ࠪࡆࡘࡥࡔࡆࡕࡗࡓࡕ࡙࡟ࡃࡗࡌࡐࡉࡥࡈࡂࡕࡋࡉࡉࡥࡉࡅࠩᆊ")] = self.config_testhub.build_hashed_id
        self.bstack1ll1ll11ll1_opy_ = False
    def __1ll1llll111_opy_(self, data):
        try:
            import selenium
            data.framework_versions[bstack11l1l_opy_ (u"ࠦࡸ࡫࡬ࡦࡰ࡬ࡹࡲࠨᆋ")] = selenium.__version__
            data.frameworks.append(bstack11l1l_opy_ (u"ࠧࡹࡥ࡭ࡧࡱ࡭ࡺࡳࠢᆌ"))
        except:
            pass
        try:
            from playwright._repo_version import __version__
            data.framework_versions[bstack11l1l_opy_ (u"ࠨࡰ࡭ࡣࡼࡻࡷ࡯ࡧࡩࡶࠥᆍ")] = __version__
            data.frameworks.append(bstack11l1l_opy_ (u"ࠢࡱ࡮ࡤࡽࡼࡸࡩࡨࡪࡷࠦᆎ"))
        except:
            pass
    def bstack1ll11lll1l1_opy_(self, hub_url: str, platform_index: int, bstack1ll1l11111_opy_: Any):
        if self.bstack1llll11l1ll_opy_:
            self.logger.debug(bstack11l1l_opy_ (u"ࠣࡵ࡮࡭ࡵࡶࡥࡥࠢࡶࡩࡹࡻࡰࠡࡵࡨࡰࡪࡴࡩࡶ࡯࠽ࠤࡦࡲࡲࡦࡣࡧࡽࠥࡹࡥࡵࠢࡸࡴࠧᆏ"))
            return
        try:
            bstack11ll1l1ll1_opy_ = datetime.now()
            import selenium
            from selenium.webdriver.remote.webdriver import WebDriver
            from selenium.webdriver.common.service import Service
            framework = bstack11l1l_opy_ (u"ࠤࡶࡩࡱ࡫࡮ࡪࡷࡰࠦᆐ")
            self.bstack1llll11l1ll_opy_ = bstack1lll11l111l_opy_(
                cli.config.get(bstack11l1l_opy_ (u"ࠥ࡬ࡺࡨࡕࡳ࡮ࠥᆑ"), hub_url),
                platform_index,
                framework_name=framework,
                framework_version=selenium.__version__,
                classes=[WebDriver],
                bstack1lll111llll_opy_={bstack11l1l_opy_ (u"ࠦࡨࡸࡥࡢࡶࡨࡣࡴࡶࡴࡪࡱࡱࡷࡤ࡬ࡲࡰ࡯ࡢࡧࡦࡶࡳࠣᆒ"): bstack1ll1l11111_opy_}
            )
            def bstack1lll111lll1_opy_(self):
                return
            if self.config.get(bstack11l1l_opy_ (u"ࠧࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡅࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࠢᆓ"), True):
                Service.start = bstack1lll111lll1_opy_
                Service.stop = bstack1lll111lll1_opy_
            def get_accessibility_results(driver):
                if self.accessibility and self.accessibility.is_enabled():
                    return self.accessibility.get_accessibility_results(driver, framework_name=framework)
            def get_accessibility_results_summary(driver):
                if self.accessibility and self.accessibility.is_enabled():
                    return self.accessibility.get_accessibility_results_summary(driver, framework_name=framework)
            def perform_scan(driver):
                if self.accessibility and self.accessibility.is_enabled():
                    return self.accessibility.perform_scan(driver, method=None, framework_name=framework)
            WebDriver.getAccessibilityResults = get_accessibility_results
            WebDriver.get_accessibility_results = get_accessibility_results
            WebDriver.getAccessibilityResultsSummary = get_accessibility_results_summary
            WebDriver.get_accessibility_results_summary = get_accessibility_results_summary
            WebDriver.upload_attachment = staticmethod(bstack1ll111ll1_opy_.upload_attachment)
            WebDriver.set_custom_tag = staticmethod(bstack1ll1llll1ll_opy_.set_custom_tag)
            WebDriver.performScan = perform_scan
            WebDriver.perform_scan = perform_scan
            self.bstack11lll111_opy_(bstack11l1l_opy_ (u"ࠨࡳࡦࡶࡸࡴࡤࡹࡥ࡭ࡧࡱ࡭ࡺࡳࠢᆔ"), datetime.now() - bstack11ll1l1ll1_opy_)
        except Exception as e:
            self.logger.error(bstack11l1l_opy_ (u"ࠢࡧࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡷࡪࡺࡵࡱࠢࡶࡩࡱ࡫࡮ࡪࡷࡰ࠾ࠥࠨᆕ") + str(e) + bstack11l1l_opy_ (u"ࠣࠤᆖ"))
    def bstack1ll1l1l1ll1_opy_(self, platform_index: int):
        try:
            from playwright.sync_api import BrowserType
            from playwright.sync_api import BrowserContext
            from playwright._impl._connection import Connection
            from playwright._repo_version import __version__
            from bstack_utils.helper import bstack1l1l1l1l_opy_
            self.bstack1llll11l1ll_opy_ = bstack1ll1l1111l1_opy_(
                platform_index,
                framework_name=bstack11l1l_opy_ (u"ࠤࡳࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹࠨᆗ"),
                framework_version=__version__,
                classes=[BrowserType, BrowserContext, Connection],
            )
        except Exception as e:
            self.logger.error(bstack11l1l_opy_ (u"ࠥࡪࡦ࡯࡬ࡦࡦࠣࡸࡴࠦࡳࡦࡶࡸࡴࠥࡶ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵ࠼ࠣࠦᆘ") + str(e) + bstack11l1l_opy_ (u"ࠦࠧᆙ"))
            pass
    def bstack1ll11llllll_opy_(self):
        if self.test_framework:
            self.logger.debug(bstack11l1l_opy_ (u"ࠧࡹ࡫ࡪࡲࡳࡩࡩࠦࡳࡦࡶࡸࡴࠥࡶࡹࡵࡧࡶࡸ࠿ࠦࡡ࡭ࡴࡨࡥࡩࡿࠠࡴࡧࡷࠤࡺࡶࠢᆚ"))
            return
        if bstack11ll1l1l_opy_():
            import pytest
            self.test_framework = PytestBDDFramework({ bstack11l1l_opy_ (u"ࠨࡰࡺࡶࡨࡷࡹࠨᆛ"): pytest.__version__ }, [bstack11l1l_opy_ (u"ࠢࡱࡻࡷࡩࡸࡺ࠭ࡣࡦࡧࠦᆜ")], self.bstack1lllll1l11l_opy_, self.bstack1ll1ll11l11_opy_)
            return
        try:
            import pytest
            self.test_framework = bstack1ll1l11llll_opy_({ bstack11l1l_opy_ (u"ࠣࡲࡼࡸࡪࡹࡴࠣᆝ"): pytest.__version__ }, [bstack11l1l_opy_ (u"ࠤࡳࡽࡹ࡫ࡳࡵࠤᆞ")], self.bstack1lllll1l11l_opy_, self.bstack1ll1ll11l11_opy_)
        except Exception as e:
            self.logger.error(bstack11l1l_opy_ (u"ࠥࡪࡦ࡯࡬ࡦࡦࠣࡸࡴࠦࡳࡦࡶࡸࡴࠥࡶࡹࡵࡧࡶࡸ࠿ࠦࠢᆟ") + str(e) + bstack11l1l_opy_ (u"ࠦࠧᆠ"))
        self.bstack1ll1l1ll1l1_opy_()
    def bstack1ll1l1ll1l1_opy_(self):
        if not self.bstack11lll11ll1_opy_():
            return
        bstack1lll1l1ll_opy_ = None
        def bstack11lll11l1l_opy_(config, startdir):
            return bstack11l1l_opy_ (u"ࠧࡪࡲࡪࡸࡨࡶ࠿ࠦࡻ࠱ࡿࠥᆡ").format(bstack11l1l_opy_ (u"ࠨࡂࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࠧᆢ"))
        def bstack1l111lllll_opy_():
            return
        def bstack11ll1l11ll_opy_(self, name: str, default=Notset(), skip: bool = False):
            if str(name).lower() == bstack11l1l_opy_ (u"ࠧࡥࡴ࡬ࡺࡪࡸࠧᆣ"):
                return bstack11l1l_opy_ (u"ࠣࡄࡵࡳࡼࡹࡥࡳࡕࡷࡥࡨࡱࠢᆤ")
            else:
                return bstack1lll1l1ll_opy_(self, name, default, skip)
        try:
            from pytest_selenium import pytest_selenium
            from _pytest.config import Config
            bstack1lll1l1ll_opy_ = Config.getoption
            pytest_selenium.pytest_report_header = bstack11lll11l1l_opy_
            from pytest_selenium.drivers import browserstack
            browserstack.pytest_selenium_runtest_makereport = bstack1l111lllll_opy_
            Config.getoption = bstack11ll1l11ll_opy_
        except Exception as e:
            self.logger.error(bstack11l1l_opy_ (u"ࠤࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥࡶࡡࡵࡥ࡫ࠤࡵࡿࡴࡦࡵࡷࠤࡸ࡫࡬ࡦࡰ࡬ࡹࡲࠦࡦࡰࡴࠣࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠼ࠣࠦᆥ") + str(e) + bstack11l1l_opy_ (u"ࠥࠦᆦ"))
    def bstack1ll11ll11ll_opy_(self):
        bstack11111ll1_opy_ = MessageToDict(cli.config_testhub, preserving_proto_field_name=True)
        if isinstance(bstack11111ll1_opy_, dict):
            if cli.config_observability:
                bstack11111ll1_opy_.update(
                    {bstack11l1l_opy_ (u"ࠦࡴࡨࡳࡦࡴࡹࡥࡧ࡯࡬ࡪࡶࡼࠦᆧ"): MessageToDict(cli.config_observability, preserving_proto_field_name=True)}
                )
            if cli.config_accessibility:
                accessibility = MessageToDict(cli.config_accessibility, preserving_proto_field_name=True)
                if isinstance(accessibility, dict) and bstack11l1l_opy_ (u"ࠧࡩ࡯࡮࡯ࡤࡲࡩࡹ࡟ࡵࡱࡢࡻࡷࡧࡰࠣᆨ") in accessibility.get(bstack11l1l_opy_ (u"ࠨ࡯ࡱࡶ࡬ࡳࡳࡹࠢᆩ"), {}):
                    bstack1ll1ll1lll1_opy_ = accessibility.get(bstack11l1l_opy_ (u"ࠢࡰࡲࡷ࡭ࡴࡴࡳࠣᆪ"))
                    bstack1ll1ll1lll1_opy_.update({ bstack11l1l_opy_ (u"ࠣࡥࡲࡱࡲࡧ࡮ࡥࡵࡗࡳ࡜ࡸࡡࡱࠤᆫ"): bstack1ll1ll1lll1_opy_.pop(bstack11l1l_opy_ (u"ࠤࡦࡳࡲࡳࡡ࡯ࡦࡶࡣࡹࡵ࡟ࡸࡴࡤࡴࠧᆬ")) })
                bstack11111ll1_opy_.update({bstack11l1l_opy_ (u"ࠥࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠥᆭ"): accessibility })
        return bstack11111ll1_opy_
    @measure(event_name=EVENTS.bstack1ll1ll1111l_opy_, stage=STAGE.bstack1lll1l11l_opy_)
    def bstack1ll11llll11_opy_(self, bstack1ll1ll1l11l_opy_: str = None, bstack1ll1ll11l1l_opy_: str = None, exit_code: int = None):
        if not self.cli_bin_session_id or not self.bstack1ll1ll11l11_opy_:
            return
        bstack11ll1l1ll1_opy_ = datetime.now()
        req = structs.StopBinSessionRequest()
        req.bin_session_id = self.cli_bin_session_id
        if exit_code:
            req.exit_code = exit_code
        if bstack1ll1ll1l11l_opy_:
            req.bstack1ll1ll1l11l_opy_ = bstack1ll1ll1l11l_opy_
        if bstack1ll1ll11l1l_opy_:
            req.bstack1ll1ll11l1l_opy_ = bstack1ll1ll11l1l_opy_
        try:
            r = self.bstack1ll1ll11l11_opy_.StopBinSession(req)
            SDKCLI.automate_buildlink = r.automate_buildlink
            SDKCLI.hashed_id = r.hashed_id
            self.bstack11lll111_opy_(bstack11l1l_opy_ (u"ࠦ࡬ࡸࡰࡤ࠼ࡶࡸࡴࡶ࡟ࡣ࡫ࡱࡣࡸ࡫ࡳࡴ࡫ࡲࡲࠧᆮ"), datetime.now() - bstack11ll1l1ll1_opy_)
            return r.success
        except grpc.RpcError as e:
            traceback.print_exc()
            raise e
    def bstack11lll111_opy_(self, key: str, value: timedelta):
        tag = bstack11l1l_opy_ (u"ࠧࡩࡨࡪ࡮ࡧ࠱ࡵࡸ࡯ࡤࡧࡶࡷࠧᆯ") if self.bstack1l1l111ll_opy_() else bstack11l1l_opy_ (u"ࠨ࡭ࡢ࡫ࡱ࠱ࡵࡸ࡯ࡤࡧࡶࡷࠧᆰ")
        self.bstack1ll1lllllll_opy_[bstack11l1l_opy_ (u"ࠢ࠻ࠤᆱ").join([tag + bstack11l1l_opy_ (u"ࠣ࠯ࠥᆲ") + str(id(self)), key])] += value
    def bstack1l11l1111_opy_(self):
        if not os.getenv(bstack11l1l_opy_ (u"ࠤࡇࡉࡇ࡛ࡇࡠࡒࡈࡖࡋࠨᆳ"), bstack11l1l_opy_ (u"ࠥ࠴ࠧᆴ")) == bstack11l1l_opy_ (u"ࠦ࠶ࠨᆵ"):
            return
        bstack1lll1111ll1_opy_ = dict()
        bstack1llll11l1l1_opy_ = []
        if self.test_framework:
            bstack1llll11l1l1_opy_.extend(list(self.test_framework.bstack1llll11l1l1_opy_.values()))
        if self.bstack1llll11l1ll_opy_:
            bstack1llll11l1l1_opy_.extend(list(self.bstack1llll11l1ll_opy_.bstack1llll11l1l1_opy_.values()))
        for instance in bstack1llll11l1l1_opy_:
            if not instance.platform_index in bstack1lll1111ll1_opy_:
                bstack1lll1111ll1_opy_[instance.platform_index] = defaultdict(lambda: timedelta(microseconds=0))
            report = bstack1lll1111ll1_opy_[instance.platform_index]
            for k, v in instance.bstack1ll1lll111l_opy_().items():
                report[k] += v
                report[k.split(bstack11l1l_opy_ (u"ࠧࡀࠢᆶ"))[0]] += v
        bstack1ll1lll11ll_opy_ = sorted([(k, v) for k, v in self.bstack1ll1lllllll_opy_.items()], key=lambda o: o[1], reverse=True)
        bstack1lll111l11l_opy_ = 0
        for r in bstack1ll1lll11ll_opy_:
            bstack1lll1l1ll11_opy_ = r[1].total_seconds()
            bstack1lll111l11l_opy_ += bstack1lll1l1ll11_opy_
            self.logger.debug(bstack11l1l_opy_ (u"ࠨ࡛ࡱࡧࡵࡪࡢࠦࡣ࡭࡫࠽ࡿࡷࡡ࠰࡞ࡿࡀࠦᆷ") + str(bstack1lll1l1ll11_opy_) + bstack11l1l_opy_ (u"ࠢࠣᆸ"))
        self.logger.debug(bstack11l1l_opy_ (u"ࠣ࠯࠰ࠦᆹ"))
        bstack1lll11l1l1l_opy_ = []
        for platform_index, report in bstack1lll1111ll1_opy_.items():
            bstack1lll11l1l1l_opy_.extend([(platform_index, k, v) for k, v in report.items()])
        bstack1lll11l1l1l_opy_.sort(key=lambda o: o[2], reverse=True)
        bstack11ll111l1l_opy_ = set()
        bstack1ll1l1l11ll_opy_ = 0
        for r in bstack1lll11l1l1l_opy_:
            bstack1lll1l1ll11_opy_ = r[2].total_seconds()
            bstack1ll1l1l11ll_opy_ += bstack1lll1l1ll11_opy_
            bstack11ll111l1l_opy_.add(r[0])
            self.logger.debug(bstack11l1l_opy_ (u"ࠤ࡞ࡴࡪࡸࡦ࡞ࠢࡷࡩࡸࡺ࠺ࡱ࡮ࡤࡸ࡫ࡵࡲ࡮࠯ࡾࡶࡠ࠶࡝ࡾ࠼ࡾࡶࡠ࠷࡝ࡾ࠿ࠥᆺ") + str(bstack1lll1l1ll11_opy_) + bstack11l1l_opy_ (u"ࠥࠦᆻ"))
        if self.bstack1l1l111ll_opy_():
            self.logger.debug(bstack11l1l_opy_ (u"ࠦ࠲࠳ࠢᆼ"))
            self.logger.debug(bstack11l1l_opy_ (u"ࠧࡡࡰࡦࡴࡩࡡࠥࡩ࡬ࡪ࠼ࡦ࡬࡮ࡲࡤ࠮ࡲࡵࡳࡨ࡫ࡳࡴ࠿ࡾࡸࡴࡺࡡ࡭ࡡࡦࡰ࡮ࢃࠠࡵࡧࡶࡸ࠿ࡶ࡬ࡢࡶࡩࡳࡷࡳࡳ࠮ࡽࡶࡸࡷ࠮ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠫࢀࡁࠧᆽ") + str(bstack1ll1l1l11ll_opy_) + bstack11l1l_opy_ (u"ࠨࠢᆾ"))
        else:
            self.logger.debug(bstack11l1l_opy_ (u"ࠢ࡜ࡲࡨࡶ࡫ࡣࠠࡤ࡮࡬࠾ࡲࡧࡩ࡯࠯ࡳࡶࡴࡩࡥࡴࡵࡀࠦᆿ") + str(bstack1lll111l11l_opy_) + bstack11l1l_opy_ (u"ࠣࠤᇀ"))
        self.logger.debug(bstack11l1l_opy_ (u"ࠤ࠰࠱ࠧᇁ"))
    def test_orchestration_session(self, test_files: list, orchestration_strategy: str, orchestration_metadata: str):
        request = structs.TestOrchestrationRequest(
            bin_session_id=self.cli_bin_session_id,
            orchestration_strategy=orchestration_strategy,
            test_files=test_files,
            orchestration_metadata=orchestration_metadata
        )
        if not self.bstack1ll1ll11l11_opy_:
            self.logger.error(bstack11l1l_opy_ (u"ࠥࡧࡱ࡯࡟ࡴࡧࡵࡺ࡮ࡩࡥࠡ࡫ࡶࠤࡳࡵࡴࠡ࡫ࡱ࡭ࡹ࡯ࡡ࡭࡫ࡽࡩࡩ࠴ࠠࡄࡣࡱࡲࡴࡺࠠࡱࡧࡵࡪࡴࡸ࡭ࠡࡶࡨࡷࡹࠦ࡯ࡳࡥ࡫ࡩࡸࡺࡲࡢࡶ࡬ࡳࡳ࠴ࠢᇂ"))
            return None
        response = self.bstack1ll1ll11l11_opy_.TestOrchestration(request)
        self.logger.debug(bstack11l1l_opy_ (u"ࠦࡹ࡫ࡳࡵ࠯ࡲࡶࡨ࡮ࡥࡴࡶࡵࡥࡹ࡯࡯࡯࠯ࡶࡩࡸࡹࡩࡰࡰࡀࡿࢂࠨᇃ").format(response))
        if response.success:
            return list(response.ordered_test_files)
        return None
    def bstack1ll1l1l111l_opy_(self, r):
        if r is not None and getattr(r, bstack11l1l_opy_ (u"ࠬࡺࡥࡴࡶ࡫ࡹࡧ࠭ᇄ"), None) and getattr(r.testhub, bstack11l1l_opy_ (u"࠭ࡥࡳࡴࡲࡶࡸ࠭ᇅ"), None):
            errors = json.loads(r.testhub.errors.decode(bstack11l1l_opy_ (u"ࠢࡶࡶࡩ࠱࠽ࠨᇆ")))
            for bstack1ll1l1111ll_opy_, err in errors.items():
                if err[bstack11l1l_opy_ (u"ࠨࡶࡼࡴࡪ࠭ᇇ")] == bstack11l1l_opy_ (u"ࠩ࡬ࡲ࡫ࡵࠧᇈ"):
                    self.logger.info(err[bstack11l1l_opy_ (u"ࠪࡱࡪࡹࡳࡢࡩࡨࠫᇉ")])
                else:
                    self.logger.error(err[bstack11l1l_opy_ (u"ࠫࡲ࡫ࡳࡴࡣࡪࡩࠬᇊ")])
    def bstack1l1l1ll1ll_opy_(self):
        return SDKCLI.automate_buildlink, SDKCLI.hashed_id
cli = SDKCLI()