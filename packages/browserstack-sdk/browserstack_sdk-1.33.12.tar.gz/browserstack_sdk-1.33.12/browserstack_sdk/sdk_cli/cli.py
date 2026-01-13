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
import subprocess
import threading
import time
import sys
import grpc
import os
from browserstack_sdk import sdk_pb2_grpc
from browserstack_sdk import sdk_pb2 as structs
from browserstack_sdk.sdk_cli.bstack1lll1l1llll_opy_ import bstack1lll11ll11l_opy_
from browserstack_sdk.sdk_cli.bstack1l1ll111111_opy_ import bstack1l1l1l111ll_opy_
from browserstack_sdk.sdk_cli.bstack1l11lllll11_opy_ import bstack1l1l11111ll_opy_
from browserstack_sdk.sdk_cli.bstack1l1l1lllll1_opy_ import bstack1l1l11ll111_opy_
from browserstack_sdk.sdk_cli.bstack1l1l1111l1l_opy_ import bstack1l1ll11ll1l_opy_
from browserstack_sdk.sdk_cli.bstack1l1l1llll1l_opy_ import bstack1l1l1ll1111_opy_
from browserstack_sdk.sdk_cli.bstack1ll1111ll1l_opy_ import bstack1ll111ll1l1_opy_
from browserstack_sdk.sdk_cli.bstack1l1l1111l11_opy_ import bstack1l1ll11l1l1_opy_
from browserstack_sdk.sdk_cli.bstack1l1ll1111ll_opy_ import bstack1l1l1l1111l_opy_
from browserstack_sdk.sdk_cli.bstack1l1ll1l1lll_opy_ import bstack1l1ll11ll11_opy_
from browserstack_sdk.sdk_cli.bstack1111l11l_opy_ import bstack1111l11l_opy_, bstack1l11111l1_opy_, bstack11llllll1l_opy_
from browserstack_sdk.sdk_cli.pytest_bdd_framework import PytestBDDFramework
from browserstack_sdk.sdk_cli.bstack1ll1ll1111l_opy_ import bstack1ll1l1lllll_opy_
from browserstack_sdk.sdk_cli.bstack1ll11l1lll1_opy_ import bstack1ll11ll1lll_opy_
from browserstack_sdk.sdk_cli.bstack1ll11l1l1l1_opy_ import bstack1ll1l1111l1_opy_
from browserstack_sdk.sdk_cli.bstack1ll11l111ll_opy_ import bstack1ll11l11l1l_opy_
from bstack_utils.helper import Notset, bstack1l11lll11ll_opy_, get_cli_dir, bstack1l1ll1ll11l_opy_, bstack1l1l1l1l_opy_
from browserstack_sdk.sdk_cli.test_framework import TestFramework
from browserstack_sdk.sdk_cli.utils.bstack1lll11l11l1_opy_ import bstack1lll11l1lll_opy_
from browserstack_sdk.sdk_cli.utils.bstack1l11lll1ll_opy_ import bstack11ll1l11l_opy_
from bstack_utils.helper import Notset, bstack1l11lll11ll_opy_, get_cli_dir, bstack1l1ll1ll11l_opy_, bstack1l1l1l1l_opy_, bstack11l1l1l11l_opy_, bstack11l1llll_opy_
from browserstack_sdk.sdk_cli.test_framework import TestFramework, bstack1llll1ll111_opy_, bstack1lll1l11l11_opy_, bstack1lll1111l11_opy_, bstack1lll1ll1lll_opy_
from browserstack_sdk.sdk_cli.bstack1ll11l1l1l1_opy_ import bstack1ll1l1ll1l1_opy_, bstack1ll11lllll1_opy_, bstack1ll11lll1ll_opy_
from bstack_utils.constants import *
from bstack_utils.bstack111ll1l1ll_opy_ import bstack1111l1lll_opy_
from bstack_utils import bstack111lll1l1_opy_
from typing import Any, List, Union, Dict
import traceback
from google.protobuf.json_format import MessageToDict
from datetime import datetime, timedelta
from collections import defaultdict
from pathlib import Path
from functools import wraps
from bstack_utils.measure import measure
from bstack_utils.messages import bstack11lll1llll_opy_, bstack1l1l11lll_opy_
logger = bstack111lll1l1_opy_.get_logger(__name__, bstack111lll1l1_opy_.bstack1l1ll1l1111_opy_())
def bstack1l1ll111ll1_opy_(bs_config):
    bstack1l11llll1l1_opy_ = None
    bstack1l1ll1l1ll1_opy_ = None
    try:
        bstack1l1ll1l1ll1_opy_ = get_cli_dir()
        bstack1l11llll1l1_opy_ = bstack1l1ll1ll11l_opy_(bstack1l1ll1l1ll1_opy_)
        bstack1l11ll1lll1_opy_ = bstack1l11lll11ll_opy_(bstack1l11llll1l1_opy_, bstack1l1ll1l1ll1_opy_, bs_config)
        bstack1l11llll1l1_opy_ = bstack1l11ll1lll1_opy_ if bstack1l11ll1lll1_opy_ else bstack1l11llll1l1_opy_
        if not bstack1l11llll1l1_opy_:
            raise ValueError(bstack11ll1_opy_ (u"ࠨࡕ࡯ࡣࡥࡰࡪࠦࡴࡰࠢࡩ࡭ࡳࡪࠠࡔࡆࡎࡣࡈࡒࡉࡠࡄࡌࡒࡤࡖࡁࡕࡊࠥዹ"))
    except Exception as ex:
        logger.debug(bstack11ll1_opy_ (u"ࠢࡆࡴࡵࡳࡷࠦࡷࡩ࡫࡯ࡩࠥࡪ࡯ࡸࡰ࡯ࡳࡦࡪࡩ࡯ࡩࠣࡸ࡭࡫ࠠ࡭ࡣࡷࡩࡸࡺࠠࡣ࡫ࡱࡥࡷࡿࠠࡼࡿࠥዺ").format(ex))
        bstack1l11llll1l1_opy_ = os.environ.get(bstack11ll1_opy_ (u"ࠣࡕࡇࡏࡤࡉࡌࡊࡡࡅࡍࡓࡥࡐࡂࡖࡋࠦዻ"))
        if bstack1l11llll1l1_opy_:
            logger.debug(bstack11ll1_opy_ (u"ࠤࡉࡥࡱࡲࡩ࡯ࡩࠣࡦࡦࡩ࡫ࠡࡶࡲࠤࡘࡊࡋࡠࡅࡏࡍࡤࡈࡉࡏࡡࡓࡅ࡙ࡎࠠࡧࡴࡲࡱࠥ࡫࡮ࡷ࡫ࡵࡳࡳࡳࡥ࡯ࡶ࠽ࠤࠧዼ") + str(bstack1l11llll1l1_opy_) + bstack11ll1_opy_ (u"ࠥࠦዽ"))
        else:
            logger.debug(bstack11ll1_opy_ (u"ࠦࡓࡵࠠࡷࡣ࡯࡭ࡩࠦࡓࡅࡍࡢࡇࡑࡏ࡟ࡃࡋࡑࡣࡕࡇࡔࡉࠢࡩࡳࡺࡴࡤࠡ࡫ࡱࠤࡪࡴࡶࡪࡴࡲࡲࡲ࡫࡮ࡵ࠽ࠣࡷࡪࡺࡵࡱࠢࡰࡥࡾࠦࡢࡦࠢ࡬ࡲࡨࡵ࡭ࡱ࡮ࡨࡸࡪ࠴ࠢዾ"))
    return bstack1l11llll1l1_opy_, bstack1l1ll1l1ll1_opy_
bstack1l1l1lll11l_opy_ = bstack11ll1_opy_ (u"ࠧ࠿࠹࠺࠻ࠥዿ")
bstack1l1l11l111l_opy_ = bstack11ll1_opy_ (u"ࠨࡲࡦࡣࡧࡽࠧጀ")
bstack1l11ll1ll1l_opy_ = bstack11ll1_opy_ (u"ࠢࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡃࡍࡋࡢࡆࡎࡔ࡟ࡔࡇࡖࡗࡎࡕࡎࡠࡋࡇࠦጁ")
bstack1l1l1lll1ll_opy_ = bstack11ll1_opy_ (u"ࠣࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡄࡎࡌࡣࡇࡏࡎࡠࡎࡌࡗ࡙ࡋࡎࡠࡃࡇࡈࡗࠨጂ")
bstack1llll1l1_opy_ = bstack11ll1_opy_ (u"ࠤࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡃࡘࡘࡔࡓࡁࡕࡋࡒࡒࠧጃ")
bstack1l1l1l1l11l_opy_ = re.compile(bstack11ll1_opy_ (u"ࡵࠦ࠭ࡅࡩࠪ࠰࠭ࠬࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡿࡆࡘ࠯࠮ࠫࠤጄ"))
bstack1l1ll1lll11_opy_ = bstack11ll1_opy_ (u"ࠦࡩ࡫ࡶࡦ࡮ࡲࡴࡲ࡫࡮ࡵࠤጅ")
bstack1l1ll11l111_opy_ = bstack11ll1_opy_ (u"ࠧࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡋࡕࡒࡄࡇࡢࡊࡆࡒࡌࡃࡃࡆࡏࠧጆ")
bstack1l1l1llll11_opy_ = [
    bstack1l11111l1_opy_.bstack1l11ll1l11_opy_,
    bstack1l11111l1_opy_.CONNECT,
    bstack1l11111l1_opy_.bstack11lll1ll_opy_,
]
class SDKCLI:
    _1l1l1ll11l1_opy_ = None
    process: Union[None, Any]
    bstack1l1ll1ll1ll_opy_: bool
    bstack1l1l1l11l1l_opy_: bool
    bstack1l1ll1l11l1_opy_: bool
    bin_session_id: Union[None, str]
    cli_bin_session_id: Union[None, str]
    cli_listen_addr: Union[None, str]
    bstack1l1ll1ll111_opy_: Union[None, grpc.Channel]
    bstack1l1l11ll1ll_opy_: str
    test_framework: TestFramework
    bstack1ll11l1l1l1_opy_: bstack1ll1l1111l1_opy_
    session_framework: str
    config: Union[None, Dict[str, Any]]
    bstack1l11lll1lll_opy_: bstack1l1ll11ll11_opy_
    accessibility: bstack1l1l11111ll_opy_
    bstack1l11lll1ll_opy_: bstack11ll1l11l_opy_
    ai: bstack1l1l11ll111_opy_
    bstack1l1l111l11l_opy_: bstack1l1ll11ll1l_opy_
    bstack1l1ll1l1l11_opy_: List[bstack1l1l1l111ll_opy_]
    config_testhub: Any
    config_observability: Any
    config_accessibility: Any
    bstack1l1l1l11ll1_opy_: Any
    bstack1l1l11l1lll_opy_: Dict[str, timedelta]
    bstack1l1l111l1l1_opy_: str
    bstack1lll1l1llll_opy_: bstack1lll11ll11l_opy_
    def __new__(cls):
        if not cls._1l1l1ll11l1_opy_:
            cls._1l1l1ll11l1_opy_ = super(SDKCLI, cls).__new__(cls)
        return cls._1l1l1ll11l1_opy_
    def __init__(self):
        self.process = None
        self.bstack1l1ll1ll1ll_opy_ = False
        self.bstack1l1ll1ll111_opy_ = None
        self.bstack1lllll11ll1_opy_ = None
        self.cli_bin_session_id = None
        self.cli_listen_addr = os.environ.get(bstack1l1l1lll1ll_opy_, None)
        self.bstack1l1l1l111l1_opy_ = os.environ.get(bstack1l11ll1ll1l_opy_, bstack11ll1_opy_ (u"ࠨࠢጇ")) == bstack11ll1_opy_ (u"ࠢࠣገ")
        self.bstack1l1l1l11l1l_opy_ = False
        self.bstack1l1ll1l11l1_opy_ = False
        self.config = None
        self.config_testhub = None
        self.config_observability = None
        self.config_accessibility = None
        self.bstack1l1l1l11ll1_opy_ = None
        self.test_framework = None
        self.bstack1ll11l1l1l1_opy_ = None
        self.bstack1l1l11ll1ll_opy_=bstack11ll1_opy_ (u"ࠣࠤጉ")
        self.session_framework = None
        self.logger = bstack111lll1l1_opy_.get_logger(self.__class__.__name__, bstack111lll1l1_opy_.bstack1l1ll1l1111_opy_())
        self.bstack1l1l11l1lll_opy_ = defaultdict(lambda: timedelta(microseconds=0))
        self.bstack1lll1l1llll_opy_ = bstack1lll11ll11l_opy_()
        self.bstack1l1l11l11ll_opy_ = None
        self.bstack1l1l1l1l1l1_opy_ = None
        self.bstack1l11lll1lll_opy_ = None
        self.accessibility = None
        self.ai = None
        self.percy = None
        self.bstack1l1ll1l1l11_opy_ = []
    def bstack11lllll11l_opy_(self):
        return os.environ.get(bstack1llll1l1_opy_).lower().__eq__(bstack11ll1_opy_ (u"ࠤࡷࡶࡺ࡫ࠢጊ"))
    def is_enabled(self, config):
        if os.environ.get(bstack1l1ll11l111_opy_, bstack11ll1_opy_ (u"ࠪࠫጋ")).lower() in [bstack11ll1_opy_ (u"ࠫࡹࡸࡵࡦࠩጌ"), bstack11ll1_opy_ (u"ࠬ࠷ࠧግ"), bstack11ll1_opy_ (u"࠭ࡹࡦࡵࠪጎ")]:
            self.logger.debug(bstack11ll1_opy_ (u"ࠢࡇࡱࡵࡧ࡮ࡴࡧࠡࡨࡤࡰࡱࡨࡡࡤ࡭ࠣࡱࡴࡪࡥࠡࡦࡸࡩࠥࡺ࡯ࠡࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡇࡑࡕࡇࡊࡥࡆࡂࡎࡏࡆࡆࡉࡋࠡࡧࡱࡺ࡮ࡸ࡯࡯࡯ࡨࡲࡹࠦࡶࡢࡴ࡬ࡥࡧࡲࡥࠣጏ"))
            os.environ[bstack11ll1_opy_ (u"ࠣࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡃࡋࡑࡅࡗ࡟࡟ࡊࡕࡢࡖ࡚ࡔࡎࡊࡐࡊࠦጐ")] = bstack11ll1_opy_ (u"ࠤࡉࡥࡱࡹࡥࠣ጑")
            return False
        if bstack11ll1_opy_ (u"ࠪࡸࡺࡸࡢࡰࡕࡦࡥࡱ࡫ࠧጒ") in config and str(config[bstack11ll1_opy_ (u"ࠫࡹࡻࡲࡣࡱࡖࡧࡦࡲࡥࠨጓ")]).lower() != bstack11ll1_opy_ (u"ࠬ࡬ࡡ࡭ࡵࡨࠫጔ"):
            return False
        bstack1l11lll1l1l_opy_ = [bstack11ll1_opy_ (u"ࠨࡰࡺࡶࡨࡷࡹࠨጕ"), bstack11ll1_opy_ (u"ࠢࡱࡻࡷࡩࡸࡺ࠭ࡣࡦࡧࠦ጖")]
        bstack1l1l1lll111_opy_ = config.get(bstack11ll1_opy_ (u"ࠣࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࠦ጗")) in bstack1l11lll1l1l_opy_ or os.environ.get(bstack11ll1_opy_ (u"ࠩࡉࡖࡆࡓࡅࡘࡑࡕࡏࡤ࡛ࡓࡆࡆࠪጘ")) in bstack1l11lll1l1l_opy_
        os.environ[bstack11ll1_opy_ (u"ࠥࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡅࡍࡓࡇࡒ࡚ࡡࡌࡗࡤࡘࡕࡏࡐࡌࡒࡌࠨጙ")] = str(bstack1l1l1lll111_opy_) # bstack1l1l1ll11ll_opy_ bstack1l1ll11111l_opy_ VAR to bstack1l1ll1111l1_opy_ is binary running
        return bstack1l1l1lll111_opy_
    def bstack1lll11111_opy_(self):
        for event in bstack1l1l1llll11_opy_:
            bstack1111l11l_opy_.register(
                event, lambda event_name, *args, **kwargs: bstack1111l11l_opy_.logger.debug(bstack11ll1_opy_ (u"ࠦࢀ࡫ࡶࡦࡰࡷࡣࡳࡧ࡭ࡦࡿࠣࡁࡃࠦࡻࡢࡴࡪࡷࢂࠦࠢጚ") + str(kwargs) + bstack11ll1_opy_ (u"ࠧࠨጛ"))
            )
        bstack1111l11l_opy_.register(bstack1l11111l1_opy_.bstack1l11ll1l11_opy_, self.__1l1l1111lll_opy_)
        bstack1111l11l_opy_.register(bstack1l11111l1_opy_.CONNECT, self.__1l1ll11llll_opy_)
        bstack1111l11l_opy_.register(bstack1l11111l1_opy_.bstack11lll1ll_opy_, self.__1l11lllll1l_opy_)
        bstack1111l11l_opy_.register(bstack1l11111l1_opy_.bstack11ll111ll_opy_, self.__1l1l1lll1l1_opy_)
    def bstack111l1l1l1_opy_(self):
        return not self.bstack1l1l1l111l1_opy_ and os.environ.get(bstack1l11ll1ll1l_opy_, bstack11ll1_opy_ (u"ࠨࠢጜ")) != bstack11ll1_opy_ (u"ࠢࠣጝ")
    def is_running(self):
        if self.bstack1l1l1l111l1_opy_:
            return self.bstack1l1ll1ll1ll_opy_
        else:
            return bool(self.bstack1l1ll1ll111_opy_)
    def bstack1l11lll111l_opy_(self, module):
        return any(isinstance(m, module) for m in self.bstack1l1ll1l1l11_opy_) and cli.is_running()
    def __1l11ll1llll_opy_(self, bstack1l1l11l1l1l_opy_=10):
        if self.bstack1lllll11ll1_opy_:
            return
        bstack1ll11l1l1l_opy_ = datetime.now()
        cli_listen_addr = os.environ.get(bstack1l1l1lll1ll_opy_, self.cli_listen_addr)
        self.logger.debug(bstack11ll1_opy_ (u"ࠣ࡝ࠥጞ") + str(id(self)) + bstack11ll1_opy_ (u"ࠤࡠࠤࡨࡵ࡮࡯ࡧࡦࡸ࡮ࡴࡧࠣጟ"))
        channel = grpc.insecure_channel(cli_listen_addr, options=[(bstack11ll1_opy_ (u"ࠥ࡫ࡷࡶࡣ࠯ࡧࡱࡥࡧࡲࡥࡠࡪࡷࡸࡵࡥࡰࡳࡱࡻࡽࠧጠ"), 0), (bstack11ll1_opy_ (u"ࠦ࡬ࡸࡰࡤ࠰ࡨࡲࡦࡨ࡬ࡦࡡ࡫ࡸࡹࡶࡳࡠࡲࡵࡳࡽࡿࠢጡ"), 0)])
        grpc.channel_ready_future(channel).result(timeout=bstack1l1l11l1l1l_opy_)
        self.bstack1l1ll1ll111_opy_ = channel
        self.bstack1lllll11ll1_opy_ = sdk_pb2_grpc.SDKStub(self.bstack1l1ll1ll111_opy_)
        self.bstack1lll1lll1_opy_(bstack11ll1_opy_ (u"ࠧ࡭ࡲࡱࡥ࠽ࡧࡴࡴ࡮ࡦࡥࡷࠦጢ"), datetime.now() - bstack1ll11l1l1l_opy_)
        self.cli_listen_addr = cli_listen_addr
        os.environ[bstack1l1l1lll1ll_opy_] = self.cli_listen_addr
        self.logger.debug(bstack11ll1_opy_ (u"ࠨ࡛ࡼ࡫ࡧࠬࡸ࡫࡬ࡧࠫࢀࡡࠥࡩ࡯࡯ࡰࡨࡧࡹ࡫ࡤ࠻ࠢ࡬ࡷࡤࡩࡨࡪ࡮ࡧࡣࡵࡸ࡯ࡤࡧࡶࡷࡂࠨጣ") + str(self.bstack111l1l1l1_opy_()) + bstack11ll1_opy_ (u"ࠢࠣጤ"))
    def __1l11lllll1l_opy_(self, event_name):
        if self.bstack111l1l1l1_opy_():
            self.logger.debug(bstack11ll1_opy_ (u"ࠣࡥ࡫࡭ࡱࡪ࠭ࡱࡴࡲࡧࡪࡹࡳ࠻ࠢࡶࡸࡴࡶࡰࡪࡰࡪࠤࡈࡒࡉࠣጥ"))
        self.__1l1l111111l_opy_()
    def __1l1l1lll1l1_opy_(self, event_name, bstack1l11lll1111_opy_ = None, exit_code=1):
        if exit_code == 1:
            self.logger.error(bstack11ll1_opy_ (u"ࠤࡖࡳࡲ࡫ࡴࡩ࡫ࡱ࡫ࠥࡽࡥ࡯ࡶࠣࡻࡷࡵ࡮ࡨࠤጦ"))
        bstack1l1l11lll1l_opy_ = Path(bstack1l1ll111l1l_opy_ (u"ࠥࡿࡸ࡫࡬ࡧ࠰ࡦࡰ࡮ࡥࡤࡪࡴࢀ࠳ࡺࡴࡨࡢࡰࡧࡰࡪࡪࡅࡳࡴࡲࡶࡸ࠴ࡪࡴࡱࡱࠦጧ"))
        if self.bstack1l1ll1l1ll1_opy_ and bstack1l1l11lll1l_opy_.exists():
            with open(bstack1l1l11lll1l_opy_, bstack11ll1_opy_ (u"ࠫࡷ࠭ጨ"), encoding=bstack11ll1_opy_ (u"ࠬࡻࡴࡧ࠯࠻ࠫጩ")) as fp:
                data = json.load(fp)
                try:
                    bstack11l1l1l11l_opy_(bstack11ll1_opy_ (u"࠭ࡐࡐࡕࡗࠫጪ"), bstack1111l1lll_opy_(bstack1lllllll1_opy_), data, {
                        bstack11ll1_opy_ (u"ࠧࡢࡷࡷ࡬ࠬጫ"): (self.config[bstack11ll1_opy_ (u"ࠨࡷࡶࡩࡷࡔࡡ࡮ࡧࠪጬ")], self.config[bstack11ll1_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴࡍࡨࡽࠬጭ")])
                    })
                except Exception as e:
                    logger.debug(bstack1l1l11lll_opy_.format(str(e)))
            bstack1l1l11lll1l_opy_.unlink()
        sys.exit(exit_code)
    @measure(event_name=EVENTS.bstack1l1l1l1ll1l_opy_, stage=STAGE.bstack11l1llll1_opy_)
    def __1l1l1111lll_opy_(self, event_name: str, data):
        from bstack_utils.bstack11l11l11ll_opy_ import bstack1lll111111l_opy_
        self.bstack1l1l11ll1ll_opy_, self.bstack1l1ll1l1ll1_opy_ = bstack1l1ll111ll1_opy_(data.bs_config)
        os.environ[bstack11ll1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡ࡚ࡖࡎ࡚ࡁࡃࡎࡈࡣࡉࡏࡒࠨጮ")] = self.bstack1l1ll1l1ll1_opy_
        if not self.bstack1l1l11ll1ll_opy_ or not self.bstack1l1ll1l1ll1_opy_:
            raise ValueError(bstack11ll1_opy_ (u"࡚ࠦࡴࡡࡣ࡮ࡨࠤࡹࡵࠠࡧ࡫ࡱࡨࠥࡺࡨࡦࠢࡖࡈࡐࠦࡃࡍࡋࠣࡦ࡮ࡴࡡࡳࡻࠥጯ"))
        if self.bstack111l1l1l1_opy_():
            self.__1l1ll11llll_opy_(event_name, bstack11llllll1l_opy_())
            return
        try:
            bstack1lll111111l_opy_.end(EVENTS.bstack1ll111111l_opy_.value, EVENTS.bstack1ll111111l_opy_.value + bstack11ll1_opy_ (u"ࠧࡀࡳࡵࡣࡵࡸࠧጰ"), EVENTS.bstack1ll111111l_opy_.value + bstack11ll1_opy_ (u"ࠨ࠺ࡦࡰࡧࠦጱ"), status=True, failure=None, test_name=None)
            logger.debug(bstack11ll1_opy_ (u"ࠢࡄࡱࡰࡴࡱ࡫ࡴࡦࠢࡖࡈࡐࠦࡓࡦࡶࡸࡴ࠳ࠨጲ"))
        except Exception as e:
            logger.debug(bstack11ll1_opy_ (u"ࠣࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤࡼ࡮ࡩ࡭ࡧࠣࡱࡦࡸ࡫ࡪࡰࡪࠤࡰ࡫ࡹࠡ࡯ࡨࡸࡷ࡯ࡣࡴࠢࡾࢁࠧጳ").format(e))
        start = datetime.now()
        is_started = self.__1l1ll1ll1l1_opy_()
        self.bstack1lll1lll1_opy_(bstack11ll1_opy_ (u"ࠤࡶࡴࡦࡽ࡮ࡠࡶ࡬ࡱࡪࠨጴ"), datetime.now() - start)
        if is_started:
            start = datetime.now()
            self.__1l11ll1llll_opy_()
            self.bstack1lll1lll1_opy_(bstack11ll1_opy_ (u"ࠥࡧࡴࡴ࡮ࡦࡥࡷࡣࡹ࡯࡭ࡦࠤጵ"), datetime.now() - start)
            start = datetime.now()
            self.__1l1l11lllll_opy_(data)
            self.bstack1lll1lll1_opy_(bstack11ll1_opy_ (u"ࠦࡸࡺࡡࡳࡶࡢࡷࡪࡹࡳࡪࡱࡱࡣࡹ࡯࡭ࡦࠤጶ"), datetime.now() - start)
    @measure(event_name=EVENTS.bstack1l1l11llll1_opy_, stage=STAGE.bstack11l1llll1_opy_)
    def __1l1ll11llll_opy_(self, event_name: str, data: bstack11llllll1l_opy_):
        if not self.bstack111l1l1l1_opy_():
            self.logger.debug(bstack11ll1_opy_ (u"ࠧ࡬ࡡࡪ࡮ࡨࡨࠥࡺ࡯ࠡࡥࡲࡲࡳ࡫ࡣࡵ࠼ࠣࡲࡴࡺࠠࡢࠢࡦ࡬࡮ࡲࡤ࠮ࡲࡵࡳࡨ࡫ࡳࡴࠤጷ"))
            return
        bin_session_id = os.environ.get(bstack1l11ll1ll1l_opy_)
        start = datetime.now()
        self.__1l11ll1llll_opy_()
        self.bstack1lll1lll1_opy_(bstack11ll1_opy_ (u"ࠨࡣࡰࡰࡱࡩࡨࡺ࡟ࡵ࡫ࡰࡩࠧጸ"), datetime.now() - start)
        self.cli_bin_session_id = bin_session_id
        self.logger.debug(bstack11ll1_opy_ (u"ࠢ࡜ࡽ࡬ࡨ࠭ࡹࡥ࡭ࡨࠬࢁࡢࠦࡣࡩ࡫࡯ࡨ࠲ࡶࡲࡰࡥࡨࡷࡸࡀࠠࡤࡱࡱࡲࡪࡩࡴࡦࡦࠣࡸࡴࠦࡥࡹ࡫ࡶࡸ࡮ࡴࡧࠡࡅࡏࡍࠥࠨጹ") + str(bin_session_id) + bstack11ll1_opy_ (u"ࠣࠤጺ"))
        start = datetime.now()
        self.__1l1l1ll111l_opy_()
        self.bstack1lll1lll1_opy_(bstack11ll1_opy_ (u"ࠤࡶࡸࡦࡸࡴࡠࡵࡨࡷࡸ࡯࡯࡯ࡡࡷ࡭ࡲ࡫ࠢጻ"), datetime.now() - start)
    def __1l1l11ll11l_opy_(self):
        if not self.bstack1lllll11ll1_opy_ or not self.cli_bin_session_id:
            self.logger.debug(bstack11ll1_opy_ (u"ࠥࡧࡦࡴ࡮ࡰࡶࠣࡧࡴࡴࡦࡪࡩࡸࡶࡪࠦ࡭ࡰࡦࡸࡰࡪࡹࠢጼ"))
            return
        bstack1l1l111ll11_opy_ = {
            bstack11ll1_opy_ (u"ࠦࡵࡲࡡࡺࡹࡵ࡭࡬࡮ࡴࠣጽ"): (bstack1l1ll11l1l1_opy_, bstack1l1l1l1111l_opy_, bstack1ll11l11l1l_opy_),
            bstack11ll1_opy_ (u"ࠧࡹࡥ࡭ࡧࡱ࡭ࡺࡳࠢጾ"): (bstack1l1l1ll1111_opy_, bstack1ll111ll1l1_opy_, bstack1ll11ll1lll_opy_),
        }
        if not self.bstack1l1l11l11ll_opy_ and self.session_framework in bstack1l1l111ll11_opy_:
            bstack1l1l1l11l11_opy_, bstack1l1l1l1lll1_opy_, bstack1l1l1ll1lll_opy_ = bstack1l1l111ll11_opy_[self.session_framework]
            bstack1l1ll1l11ll_opy_ = bstack1l1l1l1lll1_opy_()
            self.bstack1l1l1l1l1l1_opy_ = bstack1l1ll1l11ll_opy_
            self.bstack1l1l11l11ll_opy_ = bstack1l1l1ll1lll_opy_
            self.bstack1l1ll1l1l11_opy_.append(bstack1l1ll1l11ll_opy_)
            self.bstack1l1ll1l1l11_opy_.append(bstack1l1l1l11l11_opy_(self.bstack1l1l1l1l1l1_opy_))
        if not self.bstack1l11lll1lll_opy_ and self.config_observability and self.config_observability.success: # bstack1l11llll1ll_opy_
            self.bstack1l11lll1lll_opy_ = bstack1l1ll11ll11_opy_(self.bstack1l1l11l11ll_opy_, self.bstack1l1l1l1l1l1_opy_) # bstack1l1l1l1l111_opy_
            self.bstack1l1ll1l1l11_opy_.append(self.bstack1l11lll1lll_opy_)
        if not self.accessibility and self.config_accessibility and self.config_accessibility.success:
            self.accessibility = bstack1l1l11111ll_opy_(self.bstack1l1l11l11ll_opy_, self.bstack1l1l1l1l1l1_opy_)
            self.bstack1l1ll1l1l11_opy_.append(self.accessibility)
        if not self.ai and isinstance(self.config, dict) and self.config.get(bstack11ll1_opy_ (u"ࠨࡳࡦ࡮ࡩࡌࡪࡧ࡬ࠣጿ"), False) == True:
            self.ai = bstack1l1l11ll111_opy_()
            self.bstack1l1ll1l1l11_opy_.append(self.ai)
        if not self.percy and self.bstack1l1l1l11ll1_opy_ and self.bstack1l1l1l11ll1_opy_.success:
            self.percy = bstack1l1ll11ll1l_opy_(self.bstack1l1l1l11ll1_opy_)
            self.bstack1l1ll1l1l11_opy_.append(self.percy)
        for mod in self.bstack1l1ll1l1l11_opy_:
            if not mod.bstack1l11lll11l1_opy_():
                mod.configure(self.bstack1lllll11ll1_opy_, self.config, self.cli_bin_session_id, self.bstack1lll1l1llll_opy_)
    def __1l1ll11l1ll_opy_(self):
        for mod in self.bstack1l1ll1l1l11_opy_:
            if mod.bstack1l11lll11l1_opy_():
                mod.configure(self.bstack1lllll11ll1_opy_, None, None, None)
    @measure(event_name=EVENTS.bstack1l1ll1l111l_opy_, stage=STAGE.bstack11l1llll1_opy_)
    def __1l1l11lllll_opy_(self, data):
        if not self.cli_bin_session_id or self.bstack1l1l1l11l1l_opy_:
            return
        self.__1l1l1llllll_opy_(data)
        bstack1ll11l1l1l_opy_ = datetime.now()
        req = structs.StartBinSessionRequest()
        req.bin_session_id = self.cli_bin_session_id
        req.path_project = os.getcwd()
        req.language = bstack11ll1_opy_ (u"ࠢࡱࡻࡷ࡬ࡴࡴࠢፀ")
        req.sdk_language = bstack11ll1_opy_ (u"ࠣࡲࡼࡸ࡭ࡵ࡮ࠣፁ")
        req.path_config = data.path_config
        req.sdk_version = data.sdk_version
        req.test_framework = data.test_framework
        req.frameworks.extend(data.frameworks)
        req.framework_versions.update(data.framework_versions)
        req.env_vars.update({key: value for key, value in os.environ.items() if bool(bstack1l1l1l1l11l_opy_.search(key))})
        req.cli_args.extend(sys.argv)
        try:
            self.logger.debug(bstack11ll1_opy_ (u"ࠤ࡞ࠦፂ") + str(id(self)) + bstack11ll1_opy_ (u"ࠥࡡࠥࡳࡡࡪࡰ࠰ࡴࡷࡵࡣࡦࡵࡶ࠾ࠥࡹࡴࡢࡴࡷࡣࡧ࡯࡮ࡠࡵࡨࡷࡸ࡯࡯࡯ࠤፃ"))
            r = self.bstack1lllll11ll1_opy_.StartBinSession(req)
            self.bstack1lll1lll1_opy_(bstack11ll1_opy_ (u"ࠦ࡬ࡸࡰࡤ࠼ࡶࡸࡦࡸࡴࡠࡤ࡬ࡲࡤࡹࡥࡴࡵ࡬ࡳࡳࠨፄ"), datetime.now() - bstack1ll11l1l1l_opy_)
            os.environ[bstack1l11ll1ll1l_opy_] = r.bin_session_id
            self.__1l1ll11lll1_opy_(r)
            self.__1l1l11ll11l_opy_()
            self.bstack1lll1l1llll_opy_.start()
            self.bstack1l1l1l11l1l_opy_ = True
            self.logger.debug(bstack11ll1_opy_ (u"ࠧࡡࠢፅ") + str(id(self)) + bstack11ll1_opy_ (u"ࠨ࡝ࠡ࡯ࡤ࡭ࡳ࠳ࡰࡳࡱࡦࡩࡸࡹ࠺ࠡࡥࡲࡲࡳ࡫ࡣࡵࡧࡧࠦፆ"))
        except grpc.bstack1l1ll11l11l_opy_ as bstack1l1l1l1ll11_opy_:
            self.logger.error(bstack11ll1_opy_ (u"ࠢ࡜ࡽ࡬ࡨ࠭ࡹࡥ࡭ࡨࠬࢁࡢࠦࡴࡪ࡯ࡨࡳࡪࡻࡴ࠮ࡧࡵࡶࡴࡸ࠺ࠡࠤፇ") + str(bstack1l1l1l1ll11_opy_) + bstack11ll1_opy_ (u"ࠣࠤፈ"))
            traceback.print_exc()
            raise bstack1l1l1l1ll11_opy_
        except grpc.RpcError as e:
            self.logger.error(bstack11ll1_opy_ (u"ࠤ࡞ࡿ࡮ࡪࠨࡴࡧ࡯ࡪ࠮ࢃ࡝ࠡࡴࡳࡧ࠲࡫ࡲࡳࡱࡵ࠾ࠥࠨፉ") + str(e) + bstack11ll1_opy_ (u"ࠥࠦፊ"))
            traceback.print_exc()
            raise e
    @measure(event_name=EVENTS.bstack1l1l1l1l1ll_opy_, stage=STAGE.bstack11l1llll1_opy_)
    def __1l1l1ll111l_opy_(self):
        if not self.bstack111l1l1l1_opy_() or not self.cli_bin_session_id or self.bstack1l1ll1l11l1_opy_:
            return
        bstack1ll11l1l1l_opy_ = datetime.now()
        req = structs.ConnectBinSessionRequest()
        req.bin_session_id = self.cli_bin_session_id
        req.platform_index = int(os.environ.get(bstack11ll1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡔࡑࡇࡔࡇࡑࡕࡑࡤࡏࡎࡅࡇ࡛ࠫፋ"), bstack11ll1_opy_ (u"ࠬ࠶ࠧፌ")))
        try:
            self.logger.debug(bstack11ll1_opy_ (u"ࠨ࡛ࠣፍ") + str(id(self)) + bstack11ll1_opy_ (u"ࠢ࡞ࠢࡦ࡬࡮ࡲࡤ࠮ࡲࡵࡳࡨ࡫ࡳࡴ࠼ࠣࡧࡴࡴ࡮ࡦࡥࡷࡣࡧ࡯࡮ࡠࡵࡨࡷࡸ࡯࡯࡯ࠤፎ"))
            r = self.bstack1lllll11ll1_opy_.ConnectBinSession(req)
            self.bstack1lll1lll1_opy_(bstack11ll1_opy_ (u"ࠣࡩࡵࡴࡨࡀࡣࡰࡰࡱࡩࡨࡺ࡟ࡣ࡫ࡱࡣࡸ࡫ࡳࡴ࡫ࡲࡲࠧፏ"), datetime.now() - bstack1ll11l1l1l_opy_)
            self.__1l1ll11lll1_opy_(r)
            self.__1l1l11ll11l_opy_()
            self.bstack1lll1l1llll_opy_.start()
            self.bstack1l1ll1l11l1_opy_ = True
            self.logger.debug(bstack11ll1_opy_ (u"ࠤ࡞ࠦፐ") + str(id(self)) + bstack11ll1_opy_ (u"ࠥࡡࠥࡩࡨࡪ࡮ࡧ࠱ࡵࡸ࡯ࡤࡧࡶࡷ࠿ࠦࡣࡰࡰࡱࡩࡨࡺࡥࡥࠤፑ"))
        except grpc.bstack1l1ll11l11l_opy_ as bstack1l1l1l1ll11_opy_:
            self.logger.error(bstack11ll1_opy_ (u"ࠦࡠࢁࡩࡥࠪࡶࡩࡱ࡬ࠩࡾ࡟ࠣࡸ࡮ࡳࡥࡰࡧࡸࡸ࠲࡫ࡲࡳࡱࡵ࠾ࠥࠨፒ") + str(bstack1l1l1l1ll11_opy_) + bstack11ll1_opy_ (u"ࠧࠨፓ"))
            traceback.print_exc()
            raise bstack1l1l1l1ll11_opy_
        except grpc.RpcError as e:
            self.logger.error(bstack11ll1_opy_ (u"ࠨ࡛ࡼ࡫ࡧࠬࡸ࡫࡬ࡧࠫࢀࡡࠥࡸࡰࡤ࠯ࡨࡶࡷࡵࡲ࠻ࠢࠥፔ") + str(e) + bstack11ll1_opy_ (u"ࠢࠣፕ"))
            traceback.print_exc()
            raise e
    def __1l1ll11lll1_opy_(self, r):
        self.bstack1l1l111ll1l_opy_(r)
        if not r.bin_session_id or not r.config or not isinstance(r.config, str):
            raise ValueError(bstack11ll1_opy_ (u"ࠣࡷࡱࡩࡽࡶࡥࡤࡶࡨࡨࠥࡹࡥࡳࡸࡨࡶࠥࡸࡥࡴࡲࡲࡲࡸ࡫ࠢፖ") + str(r))
        self.config = json.loads(r.config)
        if not self.config:
            raise ValueError(bstack11ll1_opy_ (u"ࠤࡨࡱࡵࡺࡹࠡࡥࡲࡲ࡫࡯ࡧࠡࡨࡲࡹࡳࡪࠢፗ"))
        self.session_framework = r.session_framework
        self.config_testhub = r.testhub
        self.config_observability = r.observability
        self.config_accessibility = r.accessibility
        bstack11ll1_opy_ (u"ࠥࠦࠧࠐࠠࠡࠢࠣࠤࠥࠦࠠࡑࡧࡵࡧࡾࠦࡩࡴࠢࡶࡩࡳࡺࠠࡰࡰ࡯ࡽࠥࡧࡳࠡࡲࡤࡶࡹࠦ࡯ࡧࠢࡷ࡬ࡪࠦࠢࡄࡱࡱࡲࡪࡩࡴࡃ࡫ࡱࡗࡪࡹࡳࡪࡱࡱ࠰ࠧࠦࡡ࡯ࡦࠣࡸ࡭࡯ࡳࠡࡨࡸࡲࡨࡺࡩࡰࡰࠣ࡭ࡸࠦࡡ࡭ࡵࡲࠤࡺࡹࡥࡥࠢࡥࡽ࡙ࠥࡴࡢࡴࡷࡆ࡮ࡴࡓࡦࡵࡶ࡭ࡴࡴ࠮ࠋࠢࠣࠤࠥࠦࠠࠡࠢࡗ࡬ࡪࡸࡥࡧࡱࡵࡩ࠱ࠦࡎࡰࡰࡨࠤ࡭ࡧ࡮ࡥ࡮࡬ࡲ࡬ࠦࡩࡴࠢ࡬ࡱࡵࡲࡥ࡮ࡧࡱࡸࡪࡪ࠮ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠥࠦࠧፘ")
        self.bstack1l1l1l11ll1_opy_ = getattr(r, bstack11ll1_opy_ (u"ࠫࡵ࡫ࡲࡤࡻࠪፙ"), None)
        self.cli_bin_session_id = r.bin_session_id
        os.environ[bstack11ll1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡊࡘࡆࡤࡐࡗࡕࠩፚ")] = self.config_testhub.jwt
        os.environ[bstack11ll1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡕࡖࡋࡇࠫ፛")] = self.config_testhub.build_hashed_id
    def bstack1l1l1ll1l11_opy_(event_name: EVENTS, stage: STAGE):
        def decorator(func):
            @wraps(func)
            def wrapper(self, *args, **kwargs):
                if self.bstack1l1ll1ll1ll_opy_:
                    return func(self, *args, **kwargs)
                @measure(event_name=event_name, stage=stage)
                def bstack1l11llll111_opy_(*a, **kw):
                    return func(self, *a, **kw)
                return bstack1l11llll111_opy_(*args, **kwargs)
            return wrapper
        return decorator
    @bstack1l1l1ll1l11_opy_(event_name=EVENTS.bstack1l1l1ll1l1l_opy_, stage=STAGE.bstack11l1llll1_opy_)
    def __1l1ll1ll1l1_opy_(self, bstack1l1l11l1l1l_opy_=10):
        if self.bstack1l1ll1ll1ll_opy_:
            self.logger.debug(bstack11ll1_opy_ (u"ࠢࡴࡶࡤࡶࡹࡀࠠࡢ࡮ࡵࡩࡦࡪࡹࠡࡴࡸࡲࡳ࡯࡮ࡨࠤ፜"))
            return True
        self.logger.debug(bstack11ll1_opy_ (u"ࠣࡵࡷࡥࡷࡺࠢ፝"))
        if os.getenv(bstack11ll1_opy_ (u"ࠤࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡅࡏࡍࡤࡋࡎࡗࠤ፞")) == bstack1l1ll1lll11_opy_:
            self.cli_bin_session_id = bstack1l1ll1lll11_opy_
            self.cli_listen_addr = bstack11ll1_opy_ (u"ࠥࡹࡳ࡯ࡸ࠻࠱ࡷࡱࡵ࠵ࡳࡥ࡭࠰ࡴࡱࡧࡴࡧࡱࡵࡱ࠲ࠫࡳ࠯ࡵࡲࡧࡰࠨ፟") % (self.cli_bin_session_id)
            self.bstack1l1ll1ll1ll_opy_ = True
            return True
        self.process = subprocess.Popen(
            [self.bstack1l1l11ll1ll_opy_, bstack11ll1_opy_ (u"ࠦࡸࡪ࡫ࠣ፠")],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=dict(os.environ),
            text=True,
            universal_newlines=True, # bstack1l1l1l11lll_opy_ compat for text=True in bstack1l1ll111l11_opy_ python
            encoding=bstack11ll1_opy_ (u"ࠧࡻࡴࡧ࠯࠻ࠦ፡"),
            bufsize=1,
            close_fds=True,
        )
        bstack1l1l111llll_opy_ = threading.Thread(target=self.__1l11lllllll_opy_, args=(bstack1l1l11l1l1l_opy_,))
        bstack1l1l111llll_opy_.start()
        bstack1l1l111llll_opy_.join()
        if self.process.returncode is not None:
            self.logger.debug(bstack11ll1_opy_ (u"ࠨ࡛ࡼ࡫ࡧࠬࡸ࡫࡬ࡧࠫࢀࡡࠥࡹࡰࡢࡹࡱ࠾ࠥࡸࡥࡵࡷࡵࡲࡨࡵࡤࡦ࠿ࡾࡷࡪࡲࡦ࠯ࡲࡵࡳࡨ࡫ࡳࡴ࠰ࡵࡩࡹࡻࡲ࡯ࡥࡲࡨࡪࢃࠠࡰࡷࡷࡁࢀࡹࡥ࡭ࡨ࠱ࡴࡷࡵࡣࡦࡵࡶ࠲ࡸࡺࡤࡰࡷࡷ࠲ࡷ࡫ࡡࡥࠪࠬࢁࠥ࡫ࡲࡳ࠿ࠥ።") + str(self.process.stderr.read()) + bstack11ll1_opy_ (u"ࠢࠣ፣"))
        if not self.bstack1l1ll1ll1ll_opy_:
            self.logger.debug(bstack11ll1_opy_ (u"ࠣ࡝ࠥ፤") + str(id(self)) + bstack11ll1_opy_ (u"ࠤࡠࠤࡨࡲࡥࡢࡰࡸࡴࠧ፥"))
            self.__1l1l111111l_opy_()
        self.logger.debug(bstack11ll1_opy_ (u"ࠥ࡟ࢀ࡯ࡤࠩࡵࡨࡰ࡫࠯ࡽ࡞ࠢࡳࡶࡴࡩࡥࡴࡵࡢࡶࡪࡧࡤࡺ࠼ࠣࠦ፦") + str(self.bstack1l1ll1ll1ll_opy_) + bstack11ll1_opy_ (u"ࠦࠧ፧"))
        return self.bstack1l1ll1ll1ll_opy_
    def __1l11lllllll_opy_(self, bstack1l1l1l1llll_opy_=10):
        bstack1l1l111l111_opy_ = time.time()
        while self.process and time.time() - bstack1l1l111l111_opy_ < bstack1l1l1l1llll_opy_:
            try:
                line = self.process.stdout.readline()
                if bstack11ll1_opy_ (u"ࠧ࡯ࡤ࠾ࠤ፨") in line:
                    self.cli_bin_session_id = line.split(bstack11ll1_opy_ (u"ࠨࡩࡥ࠿ࠥ፩"))[-1:][0].strip()
                    self.logger.debug(bstack11ll1_opy_ (u"ࠢࡤ࡮࡬ࡣࡧ࡯࡮ࡠࡵࡨࡷࡸ࡯࡯࡯ࡡ࡬ࡨ࠿ࠨ፪") + str(self.cli_bin_session_id) + bstack11ll1_opy_ (u"ࠣࠤ፫"))
                    continue
                if bstack11ll1_opy_ (u"ࠤ࡯࡭ࡸࡺࡥ࡯࠿ࠥ፬") in line:
                    self.cli_listen_addr = line.split(bstack11ll1_opy_ (u"ࠥࡰ࡮ࡹࡴࡦࡰࡀࠦ፭"))[-1:][0].strip()
                    self.logger.debug(bstack11ll1_opy_ (u"ࠦࡨࡲࡩࡠ࡮࡬ࡷࡹ࡫࡮ࡠࡣࡧࡨࡷࡀࠢ፮") + str(self.cli_listen_addr) + bstack11ll1_opy_ (u"ࠧࠨ፯"))
                    continue
                if bstack11ll1_opy_ (u"ࠨࡰࡰࡴࡷࡁࠧ፰") in line:
                    port = line.split(bstack11ll1_opy_ (u"ࠢࡱࡱࡵࡸࡂࠨ፱"))[-1:][0].strip()
                    self.logger.debug(bstack11ll1_opy_ (u"ࠣࡲࡲࡶࡹࡀࠢ፲") + str(port) + bstack11ll1_opy_ (u"ࠤࠥ፳"))
                    continue
                if line.strip() == bstack1l1l11l111l_opy_ and self.cli_bin_session_id and self.cli_listen_addr:
                    if os.getenv(bstack11ll1_opy_ (u"ࠥࡗࡉࡑ࡟ࡄࡎࡌࡣࡋࡒࡁࡈࡡࡌࡓࡤ࡙ࡔࡓࡇࡄࡑࠧ፴"), bstack11ll1_opy_ (u"ࠦ࠶ࠨ፵")) == bstack11ll1_opy_ (u"ࠧ࠷ࠢ፶"):
                        if not self.process.stdout.closed:
                            self.process.stdout.close()
                        if not self.process.stderr.closed:
                            self.process.stderr.close()
                    self.bstack1l1ll1ll1ll_opy_ = True
                    return True
            except Exception as e:
                self.logger.debug(bstack11ll1_opy_ (u"ࠨࡥࡳࡴࡲࡶ࠿ࠦࠢ፷") + str(e) + bstack11ll1_opy_ (u"ࠢࠣ፸"))
        return False
    @measure(event_name=EVENTS.bstack1l1l11l1111_opy_, stage=STAGE.bstack11l1llll1_opy_)
    def __1l1l111111l_opy_(self):
        if self.bstack1l1ll1ll111_opy_:
            self.bstack1lll1l1llll_opy_.stop()
            start = datetime.now()
            if self.bstack1l1l111lll1_opy_():
                self.cli_bin_session_id = None
                if self.bstack1l1ll1l11l1_opy_:
                    self.bstack1lll1lll1_opy_(bstack11ll1_opy_ (u"ࠣࡵࡷࡳࡵࡥࡳࡦࡵࡶ࡭ࡴࡴ࡟ࡵ࡫ࡰࡩࠧ፹"), datetime.now() - start)
                else:
                    self.bstack1lll1lll1_opy_(bstack11ll1_opy_ (u"ࠤࡶࡸࡴࡶ࡟ࡴࡧࡶࡷ࡮ࡵ࡮ࡠࡶ࡬ࡱࡪࠨ፺"), datetime.now() - start)
            self.__1l1ll11l1ll_opy_()
            start = datetime.now()
            self.bstack1l1ll1ll111_opy_.close()
            self.bstack1lll1lll1_opy_(bstack11ll1_opy_ (u"ࠥࡨ࡮ࡹࡣࡰࡰࡱࡩࡨࡺ࡟ࡵ࡫ࡰࡩࠧ፻"), datetime.now() - start)
            self.bstack1l1ll1ll111_opy_ = None
        if self.process:
            self.logger.debug(bstack11ll1_opy_ (u"ࠦࡸࡺ࡯ࡱࠤ፼"))
            start = datetime.now()
            self.process.terminate()
            self.bstack1lll1lll1_opy_(bstack11ll1_opy_ (u"ࠧࡱࡩ࡭࡮ࡢࡸ࡮ࡳࡥࠣ፽"), datetime.now() - start)
            self.process = None
            if self.bstack1l1l1l111l1_opy_ and self.config_observability and self.config_testhub and self.config_testhub.testhub_events:
                self.bstack11l1ll1lll_opy_()
                self.logger.info(
                    bstack11ll1_opy_ (u"ࠨࡖࡪࡵ࡬ࡸࠥ࡮ࡴࡵࡲࡶ࠾࠴࠵ࡡࡶࡶࡲࡱࡦࡺࡩࡰࡰ࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡦࡳࡲ࠵ࡢࡶ࡫࡯ࡨࡸ࠵ࡻࡾࠢࡷࡳࠥࡼࡩࡦࡹࠣࡦࡺ࡯࡬ࡥࠢࡵࡩࡵࡵࡲࡵ࠮ࠣ࡭ࡳࡹࡩࡨࡪࡷࡷ࠱ࠦࡡ࡯ࡦࠣࡱࡦࡴࡹࠡ࡯ࡲࡶࡪࠦࡤࡦࡤࡸ࡫࡬࡯࡮ࡨࠢ࡬ࡲ࡫ࡵࡲ࡮ࡣࡷ࡭ࡴࡴࠠࡢ࡮࡯ࠤࡦࡺࠠࡰࡰࡨࠤࡵࡲࡡࡤࡧࠤࡠࡳࠨ፾").format(
                        self.config_testhub.build_hashed_id
                    )
                )
                os.environ[bstack11ll1_opy_ (u"ࠧࡃࡕࡢࡘࡊ࡙ࡔࡐࡒࡖࡣࡇ࡛ࡉࡍࡆࡢࡌࡆ࡙ࡈࡆࡆࡢࡍࡉ࠭፿")] = self.config_testhub.build_hashed_id
        self.bstack1l1ll1ll1ll_opy_ = False
    def __1l1l1llllll_opy_(self, data):
        try:
            import selenium
            data.framework_versions[bstack11ll1_opy_ (u"ࠣࡵࡨࡰࡪࡴࡩࡶ࡯ࠥᎀ")] = selenium.__version__
            data.frameworks.append(bstack11ll1_opy_ (u"ࠤࡶࡩࡱ࡫࡮ࡪࡷࡰࠦᎁ"))
        except:
            pass
        try:
            from playwright._repo_version import __version__
            data.framework_versions[bstack11ll1_opy_ (u"ࠥࡴࡱࡧࡹࡸࡴ࡬࡫࡭ࡺࠢᎂ")] = __version__
            data.frameworks.append(bstack11ll1_opy_ (u"ࠦࡵࡲࡡࡺࡹࡵ࡭࡬࡮ࡴࠣᎃ"))
        except:
            pass
    def bstack1l1l1111111_opy_(self, hub_url: str, platform_index: int, bstack111lll1ll_opy_: Any):
        if self.bstack1ll11l1l1l1_opy_:
            self.logger.debug(bstack11ll1_opy_ (u"ࠧࡹ࡫ࡪࡲࡳࡩࡩࠦࡳࡦࡶࡸࡴࠥࡹࡥ࡭ࡧࡱ࡭ࡺࡳ࠺ࠡࡣ࡯ࡶࡪࡧࡤࡺࠢࡶࡩࡹࠦࡵࡱࠤᎄ"))
            return
        try:
            bstack1ll11l1l1l_opy_ = datetime.now()
            import selenium
            from selenium.webdriver.remote.webdriver import WebDriver
            from selenium.webdriver.common.service import Service
            framework = bstack11ll1_opy_ (u"ࠨࡳࡦ࡮ࡨࡲ࡮ࡻ࡭ࠣᎅ")
            self.bstack1ll11l1l1l1_opy_ = bstack1ll11ll1lll_opy_(
                cli.config.get(bstack11ll1_opy_ (u"ࠢࡩࡷࡥ࡙ࡷࡲࠢᎆ"), hub_url),
                platform_index,
                framework_name=framework,
                framework_version=selenium.__version__,
                classes=[WebDriver],
                bstack1ll1l1l1111_opy_={bstack11ll1_opy_ (u"ࠣࡥࡵࡩࡦࡺࡥࡠࡱࡳࡸ࡮ࡵ࡮ࡴࡡࡩࡶࡴࡳ࡟ࡤࡣࡳࡷࠧᎇ"): bstack111lll1ll_opy_}
            )
            def bstack1l11lll1l11_opy_(self):
                return
            if self.config.get(bstack11ll1_opy_ (u"ࠤࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡂࡷࡷࡳࡲࡧࡴࡪࡱࡱࠦᎈ"), True):
                Service.start = bstack1l11lll1l11_opy_
                Service.stop = bstack1l11lll1l11_opy_
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
            WebDriver.upload_attachment = staticmethod(bstack11ll1l11l_opy_.upload_attachment)
            WebDriver.set_custom_tag = staticmethod(bstack1lll11l1lll_opy_.set_custom_tag)
            WebDriver.performScan = perform_scan
            WebDriver.perform_scan = perform_scan
            self.bstack1lll1lll1_opy_(bstack11ll1_opy_ (u"ࠥࡷࡪࡺࡵࡱࡡࡶࡩࡱ࡫࡮ࡪࡷࡰࠦᎉ"), datetime.now() - bstack1ll11l1l1l_opy_)
        except Exception as e:
            self.logger.error(bstack11ll1_opy_ (u"ࠦ࡫ࡧࡩ࡭ࡧࡧࠤࡹࡵࠠࡴࡧࡷࡹࡵࠦࡳࡦ࡮ࡨࡲ࡮ࡻ࡭࠻ࠢࠥᎊ") + str(e) + bstack11ll1_opy_ (u"ࠧࠨᎋ"))
    def bstack1l1ll1l1l1l_opy_(self, platform_index: int):
        try:
            from playwright.sync_api import BrowserType
            from playwright.sync_api import BrowserContext
            from playwright._impl._connection import Connection
            from playwright._repo_version import __version__
            from bstack_utils.helper import bstack11ll1l1ll_opy_
            self.bstack1ll11l1l1l1_opy_ = bstack1ll11l11l1l_opy_(
                platform_index,
                framework_name=bstack11ll1_opy_ (u"ࠨࡰ࡭ࡣࡼࡻࡷ࡯ࡧࡩࡶࠥᎌ"),
                framework_version=__version__,
                classes=[BrowserType, BrowserContext, Connection],
            )
        except Exception as e:
            self.logger.error(bstack11ll1_opy_ (u"ࠢࡧࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡷࡪࡺࡵࡱࠢࡳࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹࡀࠠࠣᎍ") + str(e) + bstack11ll1_opy_ (u"ࠣࠤᎎ"))
            pass
    def bstack1l1l11lll11_opy_(self):
        if self.test_framework:
            self.logger.debug(bstack11ll1_opy_ (u"ࠤࡶ࡯࡮ࡶࡰࡦࡦࠣࡷࡪࡺࡵࡱࠢࡳࡽࡹ࡫ࡳࡵ࠼ࠣࡥࡱࡸࡥࡢࡦࡼࠤࡸ࡫ࡴࠡࡷࡳࠦᎏ"))
            return
        if bstack1l1l1l1l_opy_():
            import pytest
            self.test_framework = PytestBDDFramework({ bstack11ll1_opy_ (u"ࠥࡴࡾࡺࡥࡴࡶࠥ᎐"): pytest.__version__ }, [bstack11ll1_opy_ (u"ࠦࡵࡿࡴࡦࡵࡷ࠱ࡧࡪࡤࠣ᎑")], self.bstack1lll1l1llll_opy_, self.bstack1lllll11ll1_opy_)
            return
        try:
            import pytest
            self.test_framework = bstack1ll1l1lllll_opy_({ bstack11ll1_opy_ (u"ࠧࡶࡹࡵࡧࡶࡸࠧ᎒"): pytest.__version__ }, [bstack11ll1_opy_ (u"ࠨࡰࡺࡶࡨࡷࡹࠨ᎓")], self.bstack1lll1l1llll_opy_, self.bstack1lllll11ll1_opy_)
        except Exception as e:
            self.logger.error(bstack11ll1_opy_ (u"ࠢࡧࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡷࡪࡺࡵࡱࠢࡳࡽࡹ࡫ࡳࡵ࠼ࠣࠦ᎔") + str(e) + bstack11ll1_opy_ (u"ࠣࠤ᎕"))
        self.bstack1l1ll1lll1l_opy_()
    def bstack1l1ll1lll1l_opy_(self):
        if not self.bstack11lllll11l_opy_():
            return
        bstack1ll111ll_opy_ = None
        def bstack1l111lll11_opy_(config, startdir):
            return bstack11ll1_opy_ (u"ࠤࡧࡶ࡮ࡼࡥࡳ࠼ࠣࡿ࠵ࢃࠢ᎖").format(bstack11ll1_opy_ (u"ࠥࡆࡷࡵࡷࡴࡧࡵࡗࡹࡧࡣ࡬ࠤ᎗"))
        def bstack1ll1l1ll_opy_():
            return
        def bstack1ll1ll1lll_opy_(self, name: str, default=Notset(), skip: bool = False):
            if str(name).lower() == bstack11ll1_opy_ (u"ࠫࡩࡸࡩࡷࡧࡵࠫ᎘"):
                return bstack11ll1_opy_ (u"ࠧࡈࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࠦ᎙")
            else:
                return bstack1ll111ll_opy_(self, name, default, skip)
        try:
            from pytest_selenium import pytest_selenium
            from _pytest.config import Config
            bstack1ll111ll_opy_ = Config.getoption
            pytest_selenium.pytest_report_header = bstack1l111lll11_opy_
            from pytest_selenium.drivers import browserstack
            browserstack.pytest_selenium_runtest_makereport = bstack1ll1l1ll_opy_
            Config.getoption = bstack1ll1ll1lll_opy_
        except Exception as e:
            self.logger.error(bstack11ll1_opy_ (u"ࠨࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡳࡥࡹࡩࡨࠡࡲࡼࡸࡪࡹࡴࠡࡵࡨࡰࡪࡴࡩࡶ࡯ࠣࡪࡴࡸࠠࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡀࠠࠣ᎚") + str(e) + bstack11ll1_opy_ (u"ࠢࠣ᎛"))
    def bstack1l11lll1ll1_opy_(self):
        bstack1lllll1l1_opy_ = MessageToDict(cli.config_testhub, preserving_proto_field_name=True)
        if isinstance(bstack1lllll1l1_opy_, dict):
            if cli.config_observability:
                bstack1lllll1l1_opy_.update(
                    {bstack11ll1_opy_ (u"ࠣࡱࡥࡷࡪࡸࡶࡢࡤ࡬ࡰ࡮ࡺࡹࠣ᎜"): MessageToDict(cli.config_observability, preserving_proto_field_name=True)}
                )
            if cli.config_accessibility:
                accessibility = MessageToDict(cli.config_accessibility, preserving_proto_field_name=True)
                if isinstance(accessibility, dict) and bstack11ll1_opy_ (u"ࠤࡦࡳࡲࡳࡡ࡯ࡦࡶࡣࡹࡵ࡟ࡸࡴࡤࡴࠧ᎝") in accessibility.get(bstack11ll1_opy_ (u"ࠥࡳࡵࡺࡩࡰࡰࡶࠦ᎞"), {}):
                    bstack1l1l1111ll1_opy_ = accessibility.get(bstack11ll1_opy_ (u"ࠦࡴࡶࡴࡪࡱࡱࡷࠧ᎟"))
                    bstack1l1l1111ll1_opy_.update({ bstack11ll1_opy_ (u"ࠧࡩ࡯࡮࡯ࡤࡲࡩࡹࡔࡰ࡙ࡵࡥࡵࠨᎠ"): bstack1l1l1111ll1_opy_.pop(bstack11ll1_opy_ (u"ࠨࡣࡰ࡯ࡰࡥࡳࡪࡳࡠࡶࡲࡣࡼࡸࡡࡱࠤᎡ")) })
                bstack1lllll1l1_opy_.update({bstack11ll1_opy_ (u"ࠢࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠢᎢ"): accessibility })
        return bstack1lllll1l1_opy_
    @measure(event_name=EVENTS.bstack1l1l11ll1l1_opy_, stage=STAGE.bstack11l1llll1_opy_)
    def bstack1l1l111lll1_opy_(self, bstack1l1l11l11l1_opy_: str = None, bstack1l1l11l1l11_opy_: str = None, exit_code: int = None):
        if not self.cli_bin_session_id or not self.bstack1lllll11ll1_opy_:
            return
        bstack1ll11l1l1l_opy_ = datetime.now()
        req = structs.StopBinSessionRequest()
        req.bin_session_id = self.cli_bin_session_id
        if exit_code:
            req.exit_code = exit_code
        if bstack1l1l11l11l1_opy_:
            req.bstack1l1l11l11l1_opy_ = bstack1l1l11l11l1_opy_
        if bstack1l1l11l1l11_opy_:
            req.bstack1l1l11l1l11_opy_ = bstack1l1l11l1l11_opy_
        try:
            r = self.bstack1lllll11ll1_opy_.StopBinSession(req)
            SDKCLI.automate_buildlink = r.automate_buildlink
            SDKCLI.hashed_id = r.hashed_id
            self.bstack1lll1lll1_opy_(bstack11ll1_opy_ (u"ࠣࡩࡵࡴࡨࡀࡳࡵࡱࡳࡣࡧ࡯࡮ࡠࡵࡨࡷࡸ࡯࡯࡯ࠤᎣ"), datetime.now() - bstack1ll11l1l1l_opy_)
            return r.success
        except grpc.RpcError as e:
            traceback.print_exc()
            raise e
    def bstack1lll1lll1_opy_(self, key: str, value: timedelta):
        tag = bstack11ll1_opy_ (u"ࠤࡦ࡬࡮ࡲࡤ࠮ࡲࡵࡳࡨ࡫ࡳࡴࠤᎤ") if self.bstack111l1l1l1_opy_() else bstack11ll1_opy_ (u"ࠥࡱࡦ࡯࡮࠮ࡲࡵࡳࡨ࡫ࡳࡴࠤᎥ")
        self.bstack1l1l11l1lll_opy_[bstack11ll1_opy_ (u"ࠦ࠿ࠨᎦ").join([tag + bstack11ll1_opy_ (u"ࠧ࠳ࠢᎧ") + str(id(self)), key])] += value
    def bstack11l1ll1lll_opy_(self):
        if not os.getenv(bstack11ll1_opy_ (u"ࠨࡄࡆࡄࡘࡋࡤࡖࡅࡓࡈࠥᎨ"), bstack11ll1_opy_ (u"ࠢ࠱ࠤᎩ")) == bstack11ll1_opy_ (u"ࠣ࠳ࠥᎪ"):
            return
        bstack1l11llllll1_opy_ = dict()
        bstack1lll1llllll_opy_ = []
        if self.test_framework:
            bstack1lll1llllll_opy_.extend(list(self.test_framework.bstack1lll1llllll_opy_.values()))
        if self.bstack1ll11l1l1l1_opy_:
            bstack1lll1llllll_opy_.extend(list(self.bstack1ll11l1l1l1_opy_.bstack1lll1llllll_opy_.values()))
        for instance in bstack1lll1llllll_opy_:
            if not instance.platform_index in bstack1l11llllll1_opy_:
                bstack1l11llllll1_opy_[instance.platform_index] = defaultdict(lambda: timedelta(microseconds=0))
            report = bstack1l11llllll1_opy_[instance.platform_index]
            for k, v in instance.bstack1l1l1l11111_opy_().items():
                report[k] += v
                report[k.split(bstack11ll1_opy_ (u"ࠤ࠽ࠦᎫ"))[0]] += v
        bstack1l1l111l1ll_opy_ = sorted([(k, v) for k, v in self.bstack1l1l11l1lll_opy_.items()], key=lambda o: o[1], reverse=True)
        bstack1l1l1ll1ll1_opy_ = 0
        for r in bstack1l1l111l1ll_opy_:
            bstack1l1ll111lll_opy_ = r[1].total_seconds()
            bstack1l1l1ll1ll1_opy_ += bstack1l1ll111lll_opy_
            self.logger.debug(bstack11ll1_opy_ (u"ࠥ࡟ࡵ࡫ࡲࡧ࡟ࠣࡧࡱ࡯࠺ࡼࡴ࡞࠴ࡢࢃ࠽ࠣᎬ") + str(bstack1l1ll111lll_opy_) + bstack11ll1_opy_ (u"ࠦࠧᎭ"))
        self.logger.debug(bstack11ll1_opy_ (u"ࠧ࠳࠭ࠣᎮ"))
        bstack1l1l11l1ll1_opy_ = []
        for platform_index, report in bstack1l11llllll1_opy_.items():
            bstack1l1l11l1ll1_opy_.extend([(platform_index, k, v) for k, v in report.items()])
        bstack1l1l11l1ll1_opy_.sort(key=lambda o: o[2], reverse=True)
        bstack11l11l11l_opy_ = set()
        bstack1l1l11111l1_opy_ = 0
        for r in bstack1l1l11l1ll1_opy_:
            bstack1l1ll111lll_opy_ = r[2].total_seconds()
            bstack1l1l11111l1_opy_ += bstack1l1ll111lll_opy_
            bstack11l11l11l_opy_.add(r[0])
            self.logger.debug(bstack11ll1_opy_ (u"ࠨ࡛ࡱࡧࡵࡪࡢࠦࡴࡦࡵࡷ࠾ࡵࡲࡡࡵࡨࡲࡶࡲ࠳ࡻࡳ࡝࠳ࡡࢂࡀࡻࡳ࡝࠴ࡡࢂࡃࠢᎯ") + str(bstack1l1ll111lll_opy_) + bstack11ll1_opy_ (u"ࠢࠣᎰ"))
        if self.bstack111l1l1l1_opy_():
            self.logger.debug(bstack11ll1_opy_ (u"ࠣ࠯࠰ࠦᎱ"))
            self.logger.debug(bstack11ll1_opy_ (u"ࠤ࡞ࡴࡪࡸࡦ࡞ࠢࡦࡰ࡮ࡀࡣࡩ࡫࡯ࡨ࠲ࡶࡲࡰࡥࡨࡷࡸࡃࡻࡵࡱࡷࡥࡱࡥࡣ࡭࡫ࢀࠤࡹ࡫ࡳࡵ࠼ࡳࡰࡦࡺࡦࡰࡴࡰࡷ࠲ࢁࡳࡵࡴࠫࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠯ࡽ࠾ࠤᎲ") + str(bstack1l1l11111l1_opy_) + bstack11ll1_opy_ (u"ࠥࠦᎳ"))
        else:
            self.logger.debug(bstack11ll1_opy_ (u"ࠦࡠࡶࡥࡳࡨࡠࠤࡨࡲࡩ࠻࡯ࡤ࡭ࡳ࠳ࡰࡳࡱࡦࡩࡸࡹ࠽ࠣᎴ") + str(bstack1l1l1ll1ll1_opy_) + bstack11ll1_opy_ (u"ࠧࠨᎵ"))
        self.logger.debug(bstack11ll1_opy_ (u"ࠨ࠭࠮ࠤᎶ"))
    def test_orchestration_session(self, test_files: list, orchestration_strategy: str, orchestration_metadata: str):
        request = structs.TestOrchestrationRequest(
            bin_session_id=self.cli_bin_session_id,
            orchestration_strategy=orchestration_strategy,
            test_files=test_files,
            orchestration_metadata=orchestration_metadata
        )
        if not self.bstack1lllll11ll1_opy_:
            self.logger.error(bstack11ll1_opy_ (u"ࠢࡤ࡮࡬ࡣࡸ࡫ࡲࡷ࡫ࡦࡩࠥ࡯ࡳࠡࡰࡲࡸࠥ࡯࡮ࡪࡶ࡬ࡥࡱ࡯ࡺࡦࡦ࠱ࠤࡈࡧ࡮࡯ࡱࡷࠤࡵ࡫ࡲࡧࡱࡵࡱࠥࡺࡥࡴࡶࠣࡳࡷࡩࡨࡦࡵࡷࡶࡦࡺࡩࡰࡰ࠱ࠦᎷ"))
            return None
        response = self.bstack1lllll11ll1_opy_.TestOrchestration(request)
        self.logger.debug(bstack11ll1_opy_ (u"ࠣࡶࡨࡷࡹ࠳࡯ࡳࡥ࡫ࡩࡸࡺࡲࡢࡶ࡬ࡳࡳ࠳ࡳࡦࡵࡶ࡭ࡴࡴ࠽ࡼࡿࠥᎸ").format(response))
        if response.success:
            return list(response.ordered_test_files)
        return None
    def bstack1l1l111ll1l_opy_(self, r):
        if r is not None and getattr(r, bstack11ll1_opy_ (u"ࠩࡷࡩࡸࡺࡨࡶࡤࠪᎹ"), None) and getattr(r.testhub, bstack11ll1_opy_ (u"ࠪࡩࡷࡸ࡯ࡳࡵࠪᎺ"), None):
            errors = json.loads(r.testhub.errors.decode(bstack11ll1_opy_ (u"ࠦࡺࡺࡦ࠮࠺ࠥᎻ")))
            for bstack1l11llll11l_opy_, err in errors.items():
                if err[bstack11ll1_opy_ (u"ࠬࡺࡹࡱࡧࠪᎼ")] == bstack11ll1_opy_ (u"࠭ࡩ࡯ࡨࡲࠫᎽ"):
                    self.logger.info(err[bstack11ll1_opy_ (u"ࠧ࡮ࡧࡶࡷࡦ࡭ࡥࠨᎾ")])
                else:
                    self.logger.error(err[bstack11ll1_opy_ (u"ࠨ࡯ࡨࡷࡸࡧࡧࡦࠩᎿ")])
    def bstack1llll111_opy_(self):
        return SDKCLI.automate_buildlink, SDKCLI.hashed_id
cli = SDKCLI()