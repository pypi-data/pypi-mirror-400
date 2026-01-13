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
import atexit
import datetime
import inspect
import logging
import signal
import threading
from uuid import uuid4
from bstack_utils.measure import bstack11l11l11ll_opy_
from bstack_utils.percy_sdk import PercySDK
import pytest
from packaging import version
from browserstack_sdk.__init__ import (bstack11l1llll1l_opy_, bstack1l1ll111l_opy_, update, bstack111lll1ll_opy_,
                                       bstack1l111lll11_opy_, bstack1ll1l1ll_opy_, bstack1l1l1ll111_opy_, bstack1l1lllll1_opy_,
                                       bstack11lll1l1_opy_, bstack1ll1l1l111_opy_, bstack1l111ll1_opy_,
                                       bstack11l1l11ll1_opy_, getAccessibilityResults, getAccessibilityResultsSummary, perform_scan, bstack11l11ll1ll_opy_)
from browserstack_sdk.bstack1l1l1ll1_opy_ import bstack1lll1l11ll_opy_
from browserstack_sdk._version import __version__
from bstack_utils import bstack111lll1l1_opy_
from bstack_utils.capture import bstack111l1l1lll_opy_
from bstack_utils.config import Config
from bstack_utils.percy import *
from bstack_utils.constants import bstack11l1111l1_opy_, bstack1llll1ll11_opy_, bstack1ll11l11l_opy_, \
    bstack1l11l1lll1_opy_
from bstack_utils.helper import bstack1lll11l1l_opy_, bstack111l1ll111l_opy_, bstack111l11l1ll_opy_, bstack1l11lll111_opy_, bstack1ll111l11l1_opy_, bstack111lll1lll_opy_, \
    bstack111lllll1ll_opy_, \
    bstack111lllll111_opy_, bstack1ll1ll1l11_opy_, bstack1l1l11l11_opy_, bstack111ll1ll11l_opy_, bstack1l1l1l1l_opy_, Notset, \
    bstack11lll11lll_opy_, bstack111ll1ll111_opy_, bstack111ll1ll1ll_opy_, Result, bstack111llll1l1l_opy_, bstack11l11111l11_opy_, error_handler, \
    bstack1l1ll111l1_opy_, bstack11l111l1ll_opy_, bstack1111lll1_opy_, bstack11l111ll11l_opy_
from bstack_utils.bstack111l11ll1ll_opy_ import bstack111l11lllll_opy_
from bstack_utils.messages import bstack1lllll11_opy_, bstack1l1111lll1_opy_, bstack1llll1111_opy_, bstack11lll111ll_opy_, bstack11lll1l1l1_opy_, \
    bstack1l1llllll1_opy_, bstack1lll1ll11l_opy_, bstack11l1l1l1ll_opy_, bstack1l1ll11l1_opy_, bstack1l111l11l1_opy_, \
    bstack1llll11l_opy_, bstack1ll1111l11_opy_, bstack11l111l1l_opy_
from bstack_utils.proxy import bstack11l1ll11l_opy_, bstack111lllll1l_opy_
from bstack_utils.bstack1l1l111111_opy_ import bstack1llll1llll1l_opy_, bstack1lllll111l1l_opy_, bstack1llll1llll11_opy_, bstack1llll1lll111_opy_, \
    bstack1lllll1111l1_opy_, bstack1llll1llllll_opy_, bstack1lllll111111_opy_, bstack1l11ll1111_opy_, bstack1llll1lll1ll_opy_
from bstack_utils.bstack1ll11l1l_opy_ import bstack11ll1111ll_opy_
from bstack_utils.bstack11llll1l1_opy_ import bstack1l111l1l_opy_, bstack11ll1ll1ll_opy_, bstack1l111ll1l1_opy_, \
    bstack1ll11ll1ll_opy_, bstack11l11111ll_opy_
from bstack_utils.bstack111l1ll11l_opy_ import bstack111ll111ll_opy_
from bstack_utils.bstack111ll11lll_opy_ import bstack1l11llll1l_opy_
import bstack_utils.accessibility as bstack1l1ll11l1l_opy_
from bstack_utils.bstack111l1l1l1l_opy_ import bstack11lll11l11_opy_
from bstack_utils.bstack1l11l111l1_opy_ import bstack1l11l111l1_opy_
from bstack_utils.bstack11l111l1_opy_ import bstack1lll1lll_opy_
from browserstack_sdk.__init__ import bstack1l11lllll_opy_
from browserstack_sdk.sdk_cli.bstack1l1ll1l1lll_opy_ import bstack1l1ll11ll11_opy_
from browserstack_sdk.sdk_cli.bstack1111l11l_opy_ import bstack1111l11l_opy_, bstack1l11111l1_opy_, bstack11llllll1l_opy_
from browserstack_sdk.sdk_cli.test_framework import bstack1lll1l1ll1l_opy_, bstack1llll1ll111_opy_, bstack1lll1111l11_opy_
from browserstack_sdk.sdk_cli.cli import cli
from browserstack_sdk.sdk_cli.bstack1111l11l_opy_ import bstack1111l11l_opy_, bstack1l11111l1_opy_, bstack11llllll1l_opy_
bstack1lll1l1l_opy_ = None
bstack1llll1lll1_opy_ = None
bstack1l111l1ll_opy_ = None
bstack11l11lllll_opy_ = None
bstack11l1lllll_opy_ = None
bstack1l1l1l1111_opy_ = None
bstack1ll1l11l1_opy_ = None
bstack1ll1l1111_opy_ = None
bstack1llll1llll_opy_ = None
bstack1l1ll11l_opy_ = None
bstack1ll111ll_opy_ = None
bstack1l111l11l_opy_ = None
bstack1l11l11ll1_opy_ = None
bstack11l1l11ll_opy_ = bstack11ll1_opy_ (u"࠭ࠧ⌍")
CONFIG = {}
bstack1l11l1l1ll_opy_ = False
bstack1l1ll11ll1_opy_ = bstack11ll1_opy_ (u"ࠧࠨ⌎")
bstack11ll1l11l1_opy_ = bstack11ll1_opy_ (u"ࠨࠩ⌏")
bstack1ll1lll1l1_opy_ = False
bstack1lll111ll_opy_ = []
bstack1l1l1l11l_opy_ = bstack11l1111l1_opy_
bstack1lll1l1111l1_opy_ = bstack11ll1_opy_ (u"ࠩࡳࡽࡹ࡫ࡳࡵࠩ⌐")
bstack1l11l11ll_opy_ = {}
bstack1ll1l11111_opy_ = None
bstack1lll11lll1_opy_ = False
logger = bstack111lll1l1_opy_.get_logger(__name__, bstack1l1l1l11l_opy_)
store = {
    bstack11ll1_opy_ (u"ࠪࡧࡺࡸࡲࡦࡰࡷࡣ࡭ࡵ࡯࡬ࡡࡸࡹ࡮ࡪࠧ⌑"): []
}
bstack1lll1l11111l_opy_ = False
try:
    from playwright.sync_api import (
        BrowserContext,
        Page
    )
except:
    pass
import json
_1111l1ll1l_opy_ = {}
current_test_uuid = None
cli_context = bstack1lll1l1ll1l_opy_(
    test_framework_name=bstack11l1ll111l_opy_[bstack11ll1_opy_ (u"ࠫࡕ࡟ࡔࡆࡕࡗ࠱ࡇࡊࡄࠨ⌒")] if bstack1l1l1l1l_opy_() else bstack11l1ll111l_opy_[bstack11ll1_opy_ (u"ࠬࡖ࡙ࡕࡇࡖࡘࠬ⌓")],
    test_framework_version=pytest.__version__,
    platform_index=-1,
)
def bstack1ll1l111ll_opy_(page, bstack1111l1ll_opy_):
    try:
        page.evaluate(bstack11ll1_opy_ (u"ࠨ࡟ࠡ࠿ࡁࠤࢀࢃࠢ⌔"),
                      bstack11ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡥࡹࡧࡦࡹࡹࡵࡲ࠻ࠢࡾࠦࡦࡩࡴࡪࡱࡱࠦ࠿ࠦࠢࡴࡧࡷࡗࡪࡹࡳࡪࡱࡱࡒࡦࡳࡥࠣ࠮ࠣࠦࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠢ࠻ࠢࡾࠦࡳࡧ࡭ࡦࠤ࠽ࠫ⌕") + json.dumps(
                          bstack1111l1ll_opy_) + bstack11ll1_opy_ (u"ࠣࡿࢀࠦ⌖"))
    except Exception as e:
        print(bstack11ll1_opy_ (u"ࠤࡨࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥ࡯࡮ࠡࡲ࡯ࡥࡾࡽࡲࡪࡩ࡫ࡸࠥࡹࡥࡴࡵ࡬ࡳࡳࠦ࡮ࡢ࡯ࡨࠤࢀࢃࠢ⌗"), e)
def bstack1l111l111_opy_(page, message, level):
    try:
        page.evaluate(bstack11ll1_opy_ (u"ࠥࡣࠥࡃ࠾ࠡࡽࢀࠦ⌘"), bstack11ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡩࡽ࡫ࡣࡶࡶࡲࡶ࠿ࠦࡻࠣࡣࡦࡸ࡮ࡵ࡮ࠣ࠼ࠣࠦࡦࡴ࡮ࡰࡶࡤࡸࡪࠨࠬࠡࠤࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠧࡀࠠࡼࠤࡧࡥࡹࡧࠢ࠻ࠩ⌙") + json.dumps(
            message) + bstack11ll1_opy_ (u"ࠬ࠲ࠢ࡭ࡧࡹࡩࡱࠨ࠺ࠨ⌚") + json.dumps(level) + bstack11ll1_opy_ (u"࠭ࡽࡾࠩ⌛"))
    except Exception as e:
        print(bstack11ll1_opy_ (u"ࠢࡦࡺࡦࡩࡵࡺࡩࡰࡰࠣ࡭ࡳࠦࡰ࡭ࡣࡼࡻࡷ࡯ࡧࡩࡶࠣࡥࡳࡴ࡯ࡵࡣࡷ࡭ࡴࡴࠠࡼࡿࠥ⌜"), e)
def pytest_configure(config):
    global bstack1l1ll11ll1_opy_
    global CONFIG
    bstack1l1l1ll1l_opy_ = Config.bstack1l1l1111_opy_()
    config.args = bstack1l11llll1l_opy_.bstack1lll1l11lll1_opy_(config.args)
    bstack1l1l1ll1l_opy_.bstack1ll11111l_opy_(bstack1111lll1_opy_(config.getoption(bstack11ll1_opy_ (u"ࠨࡵ࡮࡭ࡵ࡙ࡥࡴࡵ࡬ࡳࡳ࡙ࡴࡢࡶࡸࡷࠬ⌝"))))
    try:
        bstack111lll1l1_opy_.bstack111l111111l_opy_(config.inipath, config.rootpath)
    except:
        pass
    if cli.is_running():
        bstack1111l11l_opy_.invoke(bstack1l11111l1_opy_.CONNECT, bstack11llllll1l_opy_())
        cli_context.platform_index = int(os.environ.get(bstack11ll1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡒࡏࡅ࡙ࡌࡏࡓࡏࡢࡍࡓࡊࡅ࡙ࠩ⌞"), bstack11ll1_opy_ (u"ࠪ࠴ࠬ⌟")))
        config = json.loads(os.environ.get(bstack11ll1_opy_ (u"ࠦࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡇࡔࡔࡆࡊࡉࠥ⌠"), bstack11ll1_opy_ (u"ࠧࢁࡽࠣ⌡")))
        cli.bstack1l1l1111111_opy_(bstack1l1l11l11_opy_(bstack1l1ll11ll1_opy_, CONFIG), cli_context.platform_index, bstack111lll1ll_opy_)
    if cli.bstack1l11lll111l_opy_(bstack1l1ll11ll11_opy_):
        cli.bstack1l1l11lll11_opy_()
        logger.debug(bstack11ll1_opy_ (u"ࠨࡃࡍࡋࠣ࡭ࡸࠦࡡࡤࡶ࡬ࡺࡪࠦࡦࡰࡴࠣࡴࡱࡧࡴࡧࡱࡵࡱࡤ࡯࡮ࡥࡧࡻࡁࠧ⌢") + str(cli_context.platform_index) + bstack11ll1_opy_ (u"ࠢࠣ⌣"))
        cli.test_framework.track_event(cli_context, bstack1llll1ll111_opy_.BEFORE_ALL, bstack1lll1111l11_opy_.PRE, config)
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    when = getattr(call, bstack11ll1_opy_ (u"ࠣࡹ࡫ࡩࡳࠨ⌤"), None)
    if cli.is_running() and when == bstack11ll1_opy_ (u"ࠤࡦࡥࡱࡲࠢ⌥"):
        cli.test_framework.track_event(cli_context, bstack1llll1ll111_opy_.LOG_REPORT, bstack1lll1111l11_opy_.PRE, item, call)
    outcome = yield
    if when == bstack11ll1_opy_ (u"ࠥࡧࡦࡲ࡬ࠣ⌦"):
        report = outcome.get_result()
        passed = report.passed or report.skipped or (report.failed and hasattr(report, bstack11ll1_opy_ (u"ࠦࡼࡧࡳࡹࡨࡤ࡭ࡱࠨ⌧")))
        if not passed:
            config = json.loads(os.environ.get(bstack11ll1_opy_ (u"ࠧࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡈࡕࡎࡇࡋࡊࠦ⌨"), bstack11ll1_opy_ (u"ࠨࡻࡾࠤ〈")))
            if bstack1lll1lll_opy_.bstack1ll11l11ll_opy_(config):
                bstack1llllll1l1ll_opy_ = bstack1lll1lll_opy_.bstack1lllllll1l_opy_(config)
                if item.execution_count > bstack1llllll1l1ll_opy_:
                    print(bstack11ll1_opy_ (u"ࠧࡕࡧࡶࡸࠥ࡬ࡡࡪ࡮ࡨࡨࠥࡧࡦࡵࡧࡵࠤࡷ࡫ࡴࡳ࡫ࡨࡷ࠿ࠦࠧ〉"), report.nodeid, os.environ.get(bstack11ll1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡍ࡛ࡂࡠࡗࡘࡍࡉ࠭⌫")))
                    bstack1lll1lll_opy_.bstack1111l1l1111_opy_(report.nodeid)
            else:
                print(bstack11ll1_opy_ (u"ࠩࡗࡩࡸࡺࠠࡧࡣ࡬ࡰࡪࡪ࠺ࠡࠩ⌬"), report.nodeid, os.environ.get(bstack11ll1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡉࡘ࡚ࡈࡖࡄࡢ࡙࡚ࡏࡄࠨ⌭")))
                bstack1lll1lll_opy_.bstack1111l1l1111_opy_(report.nodeid)
        else:
            print(bstack11ll1_opy_ (u"࡙ࠫ࡫ࡳࡵࠢࡳࡥࡸࡹࡥࡥ࠼ࠣࠫ⌮"), report.nodeid, os.environ.get(bstack11ll1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡊࡘࡆࡤ࡛ࡕࡊࡆࠪ⌯")))
    if cli.is_running():
        if when == bstack11ll1_opy_ (u"ࠨࡳࡦࡶࡸࡴࠧ⌰"):
            cli.test_framework.track_event(cli_context, bstack1llll1ll111_opy_.BEFORE_EACH, bstack1lll1111l11_opy_.POST, item, call, outcome)
        elif when == bstack11ll1_opy_ (u"ࠢࡤࡣ࡯ࡰࠧ⌱"):
            cli.test_framework.track_event(cli_context, bstack1llll1ll111_opy_.LOG_REPORT, bstack1lll1111l11_opy_.POST, item, call, outcome)
        elif when == bstack11ll1_opy_ (u"ࠣࡶࡨࡥࡷࡪ࡯ࡸࡰࠥ⌲"):
            cli.test_framework.track_event(cli_context, bstack1llll1ll111_opy_.AFTER_EACH, bstack1lll1111l11_opy_.POST, item, call, outcome)
        return # skip all existing operations
    skipSessionName = item.config.getoption(bstack11ll1_opy_ (u"ࠩࡶ࡯࡮ࡶࡓࡦࡵࡶ࡭ࡴࡴࡎࡢ࡯ࡨࠫ⌳"))
    plugins = item.config.getoption(bstack11ll1_opy_ (u"ࠥࡴࡱࡻࡧࡪࡰࡶࠦ⌴"))
    report = outcome.get_result()
    os.environ[bstack11ll1_opy_ (u"ࠫࡕ࡟ࡔࡆࡕࡗࡣ࡙ࡋࡓࡕࡡࡑࡅࡒࡋࠧ⌵")] = report.nodeid
    bstack1lll11lll1ll_opy_(item, call, report)
    if bstack11ll1_opy_ (u"ࠧࡶࡹࡵࡧࡶࡸࡤࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡴࡱࡻࡧࡪࡰࠥ⌶") not in plugins or bstack1l1l1l1l_opy_():
        return
    summary = []
    driver = getattr(item, bstack11ll1_opy_ (u"ࠨ࡟ࡥࡴ࡬ࡺࡪࡸࠢ⌷"), None)
    page = getattr(item, bstack11ll1_opy_ (u"ࠢࡠࡲࡤ࡫ࡪࠨ⌸"), None)
    try:
        if (driver == None or driver.session_id == None):
            driver = threading.current_thread().bstackSessionDriver
    except:
        pass
    item._driver = driver
    if (driver is not None or cli.is_running()):
        bstack1lll11lllll1_opy_(item, report, summary, skipSessionName)
    if (page is not None):
        bstack1lll11lll111_opy_(item, report, summary, skipSessionName)
def bstack1lll11lllll1_opy_(item, report, summary, skipSessionName):
    if report.when == bstack11ll1_opy_ (u"ࠨࡵࡨࡸࡺࡶࠧ⌹") and report.skipped:
        bstack1llll1lll1ll_opy_(report)
    if report.when in [bstack11ll1_opy_ (u"ࠤࡶࡩࡹࡻࡰࠣ⌺"), bstack11ll1_opy_ (u"ࠥࡸࡪࡧࡲࡥࡱࡺࡲࠧ⌻")]:
        return
    if not bstack1ll111l11l1_opy_():
        return
    try:
        if ((str(skipSessionName).lower() != bstack11ll1_opy_ (u"ࠫࡹࡸࡵࡦࠩ⌼")) and (not cli.is_running())) and item._driver.session_id:
            item._driver.execute_script(
                bstack11ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࡼࠤࡤࡧࡹ࡯࡯࡯ࠤ࠽ࠤࠧࡹࡥࡵࡕࡨࡷࡸ࡯࡯࡯ࡐࡤࡱࡪࠨࠬࠡࠤࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠧࡀࠠࡼࠤࡱࡥࡲ࡫ࠢ࠻ࠢࠪ⌽") + json.dumps(
                    report.nodeid) + bstack11ll1_opy_ (u"࠭ࡽࡾࠩ⌾"))
        os.environ[bstack11ll1_opy_ (u"ࠧࡑ࡛ࡗࡉࡘ࡚࡟ࡕࡇࡖࡘࡤࡔࡁࡎࡇࠪ⌿")] = report.nodeid
    except Exception as e:
        summary.append(
            bstack11ll1_opy_ (u"࡙ࠣࡄࡖࡓࡏࡎࡈ࠼ࠣࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦ࡭ࡢࡴ࡮ࠤࡸ࡫ࡳࡴ࡫ࡲࡲࠥࡴࡡ࡮ࡧ࠽ࠤࢀ࠶ࡽࠣ⍀").format(e)
        )
    passed = report.passed or report.skipped or (report.failed and hasattr(report, bstack11ll1_opy_ (u"ࠤࡺࡥࡸࡾࡦࡢ࡫࡯ࠦ⍁")))
    bstack1ll111l1l_opy_ = bstack11ll1_opy_ (u"ࠥࠦ⍂")
    bstack1llll1lll1ll_opy_(report)
    if not passed:
        try:
            bstack1ll111l1l_opy_ = report.longrepr.reprcrash
        except Exception as e:
            summary.append(
                bstack11ll1_opy_ (u"ࠦ࡜ࡇࡒࡏࡋࡑࡋ࠿ࠦࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡧࡩࡹ࡫ࡲ࡮࡫ࡱࡩࠥ࡬ࡡࡪ࡮ࡸࡶࡪࠦࡲࡦࡣࡶࡳࡳࡀࠠࡼ࠲ࢀࠦ⍃").format(e)
            )
        try:
            if (threading.current_thread().bstackTestErrorMessages == None):
                threading.current_thread().bstackTestErrorMessages = []
        except Exception as e:
            threading.current_thread().bstackTestErrorMessages = []
        threading.current_thread().bstackTestErrorMessages.append(str(bstack1ll111l1l_opy_))
    if not report.skipped:
        passed = report.passed or (report.failed and hasattr(report, bstack11ll1_opy_ (u"ࠧࡽࡡࡴࡺࡩࡥ࡮ࡲࠢ⍄")))
        bstack1ll111l1l_opy_ = bstack11ll1_opy_ (u"ࠨࠢ⍅")
        if not passed:
            try:
                bstack1ll111l1l_opy_ = report.longrepr.reprcrash
            except Exception as e:
                summary.append(
                    bstack11ll1_opy_ (u"ࠢࡘࡃࡕࡒࡎࡔࡇ࠻ࠢࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥࡪࡥࡵࡧࡵࡱ࡮ࡴࡥࠡࡨࡤ࡭ࡱࡻࡲࡦࠢࡵࡩࡦࡹ࡯࡯࠼ࠣࡿ࠵ࢃࠢ⍆").format(e)
                )
            try:
                if (threading.current_thread().bstackTestErrorMessages == None):
                    threading.current_thread().bstackTestErrorMessages = []
            except Exception as e:
                threading.current_thread().bstackTestErrorMessages = []
            threading.current_thread().bstackTestErrorMessages.append(str(bstack1ll111l1l_opy_))
        try:
            if passed:
                item._driver.execute_script(
                    bstack11ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࡿࡡࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠢࡢࡥࡷ࡭ࡴࡴࠢ࠻ࠢࠥࡥࡳࡴ࡯ࡵࡣࡷࡩࠧ࠲ࠠ࡝ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠥࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸࠨ࠺ࠡࡽ࡟ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠤ࡯ࡩࡻ࡫࡬ࠣ࠼ࠣࠦ࡮ࡴࡦࡰࠤ࠯ࠤࡡࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠦࡩࡧࡴࡢࠤ࠽ࠤࠬ⍇")
                    + json.dumps(bstack11ll1_opy_ (u"ࠤࡳࡥࡸࡹࡥࡥࠣࠥ⍈"))
                    + bstack11ll1_opy_ (u"ࠥࡠࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࢃ࡜ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࢂࠨ⍉")
                )
            else:
                item._driver.execute_script(
                    bstack11ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡩࡽ࡫ࡣࡶࡶࡲࡶ࠿ࠦࡻ࡝ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠥࡥࡨࡺࡩࡰࡰࠥ࠾ࠥࠨࡡ࡯ࡰࡲࡸࡦࡺࡥࠣ࠮ࠣࡠࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠨࡡࡳࡩࡸࡱࡪࡴࡴࡴࠤ࠽ࠤࢀࡢࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠧࡲࡥࡷࡧ࡯ࠦ࠿ࠦࠢࡦࡴࡵࡳࡷࠨࠬࠡ࡞ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠣࡦࡤࡸࡦࠨ࠺ࠡࠩ⍊")
                    + json.dumps(str(bstack1ll111l1l_opy_))
                    + bstack11ll1_opy_ (u"ࠧࡢࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࡾ࡞ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࡽࠣ⍋")
                )
        except Exception as e:
            summary.append(bstack11ll1_opy_ (u"ࠨࡗࡂࡔࡑࡍࡓࡍ࠺ࠡࡈࡤ࡭ࡱ࡫ࡤࠡࡶࡲࠤࡦࡴ࡮ࡰࡶࡤࡸࡪࡀࠠࡼ࠲ࢀࠦ⍌").format(e))
def bstack1lll11ll1ll1_opy_(test_name, error_message):
    try:
        bstack1lll11l1lll1_opy_ = []
        bstack1l11ll11ll_opy_ = os.environ.get(bstack11ll1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡐࡍࡃࡗࡊࡔࡘࡍࡠࡋࡑࡈࡊ࡞ࠧ⍍"), bstack11ll1_opy_ (u"ࠨ࠲ࠪ⍎"))
        bstack1l11111l11_opy_ = {bstack11ll1_opy_ (u"ࠩࡱࡥࡲ࡫ࠧ⍏"): test_name, bstack11ll1_opy_ (u"ࠪࡩࡷࡸ࡯ࡳࠩ⍐"): error_message, bstack11ll1_opy_ (u"ࠫ࡮ࡴࡤࡦࡺࠪ⍑"): bstack1l11ll11ll_opy_}
        bstack1lll1l11l11l_opy_ = os.path.join(tempfile.gettempdir(), bstack11ll1_opy_ (u"ࠬࡶࡷࡠࡲࡼࡸࡪࡹࡴࡠࡧࡵࡶࡴࡸ࡟࡭࡫ࡶࡸ࠳ࡰࡳࡰࡰࠪ⍒"))
        if os.path.exists(bstack1lll1l11l11l_opy_):
            with open(bstack1lll1l11l11l_opy_) as f:
                bstack1lll11l1lll1_opy_ = json.load(f)
        bstack1lll11l1lll1_opy_.append(bstack1l11111l11_opy_)
        with open(bstack1lll1l11l11l_opy_, bstack11ll1_opy_ (u"࠭ࡷࠨ⍓")) as f:
            json.dump(bstack1lll11l1lll1_opy_, f)
    except Exception as e:
        logger.debug(bstack11ll1_opy_ (u"ࠧࡆࡴࡵࡳࡷࠦࡩ࡯ࠢࡳࡩࡷࡹࡩࡴࡶ࡬ࡲ࡬ࠦࡰ࡭ࡣࡼࡻࡷ࡯ࡧࡩࡶࠣࡴࡾࡺࡥࡴࡶࠣࡩࡷࡸ࡯ࡳࡵ࠽ࠤࠬ⍔") + str(e))
def bstack1lll11lll111_opy_(item, report, summary, skipSessionName):
    if report.when in [bstack11ll1_opy_ (u"ࠣࡵࡨࡸࡺࡶࠢ⍕"), bstack11ll1_opy_ (u"ࠤࡷࡩࡦࡸࡤࡰࡹࡱࠦ⍖")]:
        return
    if (str(skipSessionName).lower() != bstack11ll1_opy_ (u"ࠪࡸࡷࡻࡥࠨ⍗")):
        bstack1ll1l111ll_opy_(item._page, report.nodeid)
    passed = report.passed or report.skipped or (report.failed and hasattr(report, bstack11ll1_opy_ (u"ࠦࡼࡧࡳࡹࡨࡤ࡭ࡱࠨ⍘")))
    bstack1ll111l1l_opy_ = bstack11ll1_opy_ (u"ࠧࠨ⍙")
    bstack1llll1lll1ll_opy_(report)
    if not report.skipped:
        if not passed:
            try:
                bstack1ll111l1l_opy_ = report.longrepr.reprcrash
            except Exception as e:
                summary.append(
                    bstack11ll1_opy_ (u"ࠨࡗࡂࡔࡑࡍࡓࡍ࠺ࠡࡈࡤ࡭ࡱ࡫ࡤࠡࡶࡲࠤࡩ࡫ࡴࡦࡴࡰ࡭ࡳ࡫ࠠࡧࡣ࡬ࡰࡺࡸࡥࠡࡴࡨࡥࡸࡵ࡮࠻ࠢࡾ࠴ࢂࠨ⍚").format(e)
                )
        try:
            if passed:
                bstack11l11111ll_opy_(getattr(item, bstack11ll1_opy_ (u"ࠧࡠࡲࡤ࡫ࡪ࠭⍛"), None), bstack11ll1_opy_ (u"ࠣࡲࡤࡷࡸ࡫ࡤࠣ⍜"))
            else:
                error_message = bstack11ll1_opy_ (u"ࠩࠪ⍝")
                if bstack1ll111l1l_opy_:
                    bstack1l111l111_opy_(item._page, str(bstack1ll111l1l_opy_), bstack11ll1_opy_ (u"ࠥࡩࡷࡸ࡯ࡳࠤ⍞"))
                    bstack11l11111ll_opy_(getattr(item, bstack11ll1_opy_ (u"ࠫࡤࡶࡡࡨࡧࠪ⍟"), None), bstack11ll1_opy_ (u"ࠧ࡬ࡡࡪ࡮ࡨࡨࠧ⍠"), str(bstack1ll111l1l_opy_))
                    error_message = str(bstack1ll111l1l_opy_)
                else:
                    bstack11l11111ll_opy_(getattr(item, bstack11ll1_opy_ (u"࠭࡟ࡱࡣࡪࡩࠬ⍡"), None), bstack11ll1_opy_ (u"ࠢࡧࡣ࡬ࡰࡪࡪࠢ⍢"))
                bstack1lll11ll1ll1_opy_(report.nodeid, error_message)
        except Exception as e:
            summary.append(bstack11ll1_opy_ (u"࡙ࠣࡄࡖࡓࡏࡎࡈ࠼ࠣࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦࡵࡱࡦࡤࡸࡪࠦࡳࡦࡵࡶ࡭ࡴࡴࠠࡴࡶࡤࡸࡺࡹ࠺ࠡࡽ࠳ࢁࠧ⍣").format(e))
def pytest_addoption(parser):
    parser.addoption(bstack11ll1_opy_ (u"ࠤ࠰࠱ࡸࡱࡩࡱࡕࡨࡷࡸ࡯࡯࡯ࡐࡤࡱࡪࠨ⍤"), default=bstack11ll1_opy_ (u"ࠥࡊࡦࡲࡳࡦࠤ⍥"), help=bstack11ll1_opy_ (u"ࠦࡆࡻࡴࡰ࡯ࡤࡸ࡮ࡩࠠࡴࡧࡷࠤࡸ࡫ࡳࡴ࡫ࡲࡲࠥࡴࡡ࡮ࡧࠥ⍦"))
    parser.addoption(bstack11ll1_opy_ (u"ࠧ࠳࠭ࡴ࡭࡬ࡴࡘ࡫ࡳࡴ࡫ࡲࡲࡘࡺࡡࡵࡷࡶࠦ⍧"), default=bstack11ll1_opy_ (u"ࠨࡆࡢ࡮ࡶࡩࠧ⍨"), help=bstack11ll1_opy_ (u"ࠢࡂࡷࡷࡳࡲࡧࡴࡪࡥࠣࡷࡪࡺࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠡࡰࡤࡱࡪࠨ⍩"))
    try:
        import pytest_selenium.pytest_selenium
    except:
        parser.addoption(bstack11ll1_opy_ (u"ࠣ࠯࠰ࡨࡷ࡯ࡶࡦࡴࠥ⍪"), action=bstack11ll1_opy_ (u"ࠤࡶࡸࡴࡸࡥࠣ⍫"), default=bstack11ll1_opy_ (u"ࠥࡧ࡭ࡸ࡯࡮ࡧࠥ⍬"),
                         help=bstack11ll1_opy_ (u"ࠦࡉࡸࡩࡷࡧࡵࠤࡹࡵࠠࡳࡷࡱࠤࡹ࡫ࡳࡵࡵࠥ⍭"))
def bstack111l1l1111_opy_(log):
    if not (log[bstack11ll1_opy_ (u"ࠬࡳࡥࡴࡵࡤ࡫ࡪ࠭⍮")] and log[bstack11ll1_opy_ (u"࠭࡭ࡦࡵࡶࡥ࡬࡫ࠧ⍯")].strip()):
        return
    active = bstack111ll111l1_opy_()
    log = {
        bstack11ll1_opy_ (u"ࠧ࡭ࡧࡹࡩࡱ࠭⍰"): log[bstack11ll1_opy_ (u"ࠨ࡮ࡨࡺࡪࡲࠧ⍱")],
        bstack11ll1_opy_ (u"ࠩࡷ࡭ࡲ࡫ࡳࡵࡣࡰࡴࠬ⍲"): bstack111l11l1ll_opy_().isoformat() + bstack11ll1_opy_ (u"ࠪ࡞ࠬ⍳"),
        bstack11ll1_opy_ (u"ࠫࡲ࡫ࡳࡴࡣࡪࡩࠬ⍴"): log[bstack11ll1_opy_ (u"ࠬࡳࡥࡴࡵࡤ࡫ࡪ࠭⍵")],
    }
    if active:
        if active[bstack11ll1_opy_ (u"࠭ࡴࡺࡲࡨࠫ⍶")] == bstack11ll1_opy_ (u"ࠧࡩࡱࡲ࡯ࠬ⍷"):
            log[bstack11ll1_opy_ (u"ࠨࡪࡲࡳࡰࡥࡲࡶࡰࡢࡹࡺ࡯ࡤࠨ⍸")] = active[bstack11ll1_opy_ (u"ࠩ࡫ࡳࡴࡱ࡟ࡳࡷࡱࡣࡺࡻࡩࡥࠩ⍹")]
        elif active[bstack11ll1_opy_ (u"ࠪࡸࡾࡶࡥࠨ⍺")] == bstack11ll1_opy_ (u"ࠫࡹ࡫ࡳࡵࠩ⍻"):
            log[bstack11ll1_opy_ (u"ࠬࡺࡥࡴࡶࡢࡶࡺࡴ࡟ࡶࡷ࡬ࡨࠬ⍼")] = active[bstack11ll1_opy_ (u"࠭ࡴࡦࡵࡷࡣࡷࡻ࡮ࡠࡷࡸ࡭ࡩ࠭⍽")]
    bstack11lll11l11_opy_.bstack1l1l11l11l_opy_([log])
def bstack111ll111l1_opy_():
    if len(store[bstack11ll1_opy_ (u"ࠧࡤࡷࡵࡶࡪࡴࡴࡠࡪࡲࡳࡰࡥࡵࡶ࡫ࡧࠫ⍾")]) > 0 and store[bstack11ll1_opy_ (u"ࠨࡥࡸࡶࡷ࡫࡮ࡵࡡ࡫ࡳࡴࡱ࡟ࡶࡷ࡬ࡨࠬ⍿")][-1]:
        return {
            bstack11ll1_opy_ (u"ࠩࡷࡽࡵ࡫ࠧ⎀"): bstack11ll1_opy_ (u"ࠪ࡬ࡴࡵ࡫ࠨ⎁"),
            bstack11ll1_opy_ (u"ࠫ࡭ࡵ࡯࡬ࡡࡵࡹࡳࡥࡵࡶ࡫ࡧࠫ⎂"): store[bstack11ll1_opy_ (u"ࠬࡩࡵࡳࡴࡨࡲࡹࡥࡨࡰࡱ࡮ࡣࡺࡻࡩࡥࠩ⎃")][-1]
        }
    if store.get(bstack11ll1_opy_ (u"࠭ࡣࡶࡴࡵࡩࡳࡺ࡟ࡵࡧࡶࡸࡤࡻࡵࡪࡦࠪ⎄"), None):
        return {
            bstack11ll1_opy_ (u"ࠧࡵࡻࡳࡩࠬ⎅"): bstack11ll1_opy_ (u"ࠨࡶࡨࡷࡹ࠭⎆"),
            bstack11ll1_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡳࡷࡱࡣࡺࡻࡩࡥࠩ⎇"): store[bstack11ll1_opy_ (u"ࠪࡧࡺࡸࡲࡦࡰࡷࡣࡹ࡫ࡳࡵࡡࡸࡹ࡮ࡪࠧ⎈")]
        }
    return None
def pytest_runtest_logstart(nodeid, location):
    if cli.is_running():
        cli.test_framework.track_event(cli_context, bstack1llll1ll111_opy_.INIT_TEST, bstack1lll1111l11_opy_.PRE, nodeid, location)
def pytest_runtest_logfinish(nodeid, location):
    if cli.is_running():
        cli.test_framework.track_event(cli_context, bstack1llll1ll111_opy_.INIT_TEST, bstack1lll1111l11_opy_.POST, nodeid, location)
def pytest_runtest_call(item):
    if cli.is_running():
        cli.test_framework.track_event(cli_context, bstack1llll1ll111_opy_.TEST, bstack1lll1111l11_opy_.PRE, item)
        return
    try:
        global CONFIG
        item._1lll1l111l11_opy_ = True
        bstack1ll11l111l_opy_ = bstack1l1ll11l1l_opy_.bstack1llll1111l_opy_(bstack111lllll111_opy_(item.own_markers))
        if not cli.bstack1l11lll111l_opy_(bstack1l1ll11ll11_opy_):
            item._a11y_test_case = bstack1ll11l111l_opy_
            if bstack1lll11l1l_opy_(threading.current_thread(), bstack11ll1_opy_ (u"ࠫࡦ࠷࠱ࡺࡒ࡯ࡥࡹ࡬࡯ࡳ࡯ࠪ⎉"), None):
                driver = getattr(item, bstack11ll1_opy_ (u"ࠬࡥࡤࡳ࡫ࡹࡩࡷ࠭⎊"), None)
                item._a11y_started = bstack1l1ll11l1l_opy_.bstack11lll1111l_opy_(driver, bstack1ll11l111l_opy_)
        if not bstack11lll11l11_opy_.on() or bstack1lll1l1111l1_opy_ != bstack11ll1_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹ࠭⎋"):
            return
        global current_test_uuid #, bstack111ll11ll1_opy_
        bstack1111ll1l11_opy_ = {
            bstack11ll1_opy_ (u"ࠧࡶࡷ࡬ࡨࠬ⎌"): uuid4().__str__(),
            bstack11ll1_opy_ (u"ࠨࡵࡷࡥࡷࡺࡥࡥࡡࡤࡸࠬ⎍"): bstack111l11l1ll_opy_().isoformat() + bstack11ll1_opy_ (u"ࠩ࡝ࠫ⎎")
        }
        current_test_uuid = bstack1111ll1l11_opy_[bstack11ll1_opy_ (u"ࠪࡹࡺ࡯ࡤࠨ⎏")]
        store[bstack11ll1_opy_ (u"ࠫࡨࡻࡲࡳࡧࡱࡸࡤࡺࡥࡴࡶࡢࡹࡺ࡯ࡤࠨ⎐")] = bstack1111ll1l11_opy_[bstack11ll1_opy_ (u"ࠬࡻࡵࡪࡦࠪ⎑")]
        threading.current_thread().current_test_uuid = current_test_uuid
        _1111l1ll1l_opy_[item.nodeid] = {**_1111l1ll1l_opy_[item.nodeid], **bstack1111ll1l11_opy_}
        bstack1lll11lll1l1_opy_(item, _1111l1ll1l_opy_[item.nodeid], bstack11ll1_opy_ (u"࠭ࡔࡦࡵࡷࡖࡺࡴࡓࡵࡣࡵࡸࡪࡪࠧ⎒"))
    except Exception as err:
        print(bstack11ll1_opy_ (u"ࠧࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣ࡭ࡳࠦࡰࡺࡶࡨࡷࡹࡥࡲࡶࡰࡷࡩࡸࡺ࡟ࡤࡣ࡯ࡰ࠿ࠦࡻࡾࠩ⎓"), str(err))
def pytest_runtest_setup(item):
    store[bstack11ll1_opy_ (u"ࠨࡥࡸࡶࡷ࡫࡮ࡵࡡࡷࡩࡸࡺ࡟ࡪࡶࡨࡱࠬ⎔")] = item
    if cli.is_running():
        cli.test_framework.track_event(cli_context, bstack1llll1ll111_opy_.BEFORE_EACH, bstack1lll1111l11_opy_.PRE, item, bstack11ll1_opy_ (u"ࠩࡶࡩࡹࡻࡰࠨ⎕"))
    if bstack1lll1lll_opy_.bstack1111l11l111_opy_():
            bstack1lll1l111lll_opy_ = bstack11ll1_opy_ (u"ࠥࡗࡰ࡯ࡰࡱ࡫ࡱ࡫ࠥࡺࡥࡴࡶࠣࡥࡸࠦࡴࡩࡧࠣࡥࡧࡵࡲࡵࠢࡥࡹ࡮ࡲࡤࠡࡨ࡬ࡰࡪࠦࡥࡹ࡫ࡶࡸࡸ࠴ࠢ⎖")
            logger.error(bstack1lll1l111lll_opy_)
            bstack1111ll1l11_opy_ = {
                bstack11ll1_opy_ (u"ࠫࡺࡻࡩࡥࠩ⎗"): uuid4().__str__(),
                bstack11ll1_opy_ (u"ࠬࡹࡴࡢࡴࡷࡩࡩࡥࡡࡵࠩ⎘"): bstack111l11l1ll_opy_().isoformat() + bstack11ll1_opy_ (u"࡚࠭ࠨ⎙"),
                bstack11ll1_opy_ (u"ࠧࡧ࡫ࡱ࡭ࡸ࡮ࡥࡥࡡࡤࡸࠬ⎚"): bstack111l11l1ll_opy_().isoformat() + bstack11ll1_opy_ (u"ࠨ࡜ࠪ⎛"),
                bstack11ll1_opy_ (u"ࠩࡵࡩࡸࡻ࡬ࡵࠩ⎜"): bstack11ll1_opy_ (u"ࠪࡷࡰ࡯ࡰࡱࡧࡧࠫ⎝"),
                bstack11ll1_opy_ (u"ࠫࡷ࡫ࡡࡴࡱࡱࠫ⎞"): bstack1lll1l111lll_opy_,
                bstack11ll1_opy_ (u"ࠬ࡮࡯ࡰ࡭ࡶࠫ⎟"): [],
                bstack11ll1_opy_ (u"࠭ࡦࡪࡺࡷࡹࡷ࡫ࡳࠨ⎠"): []
            }
            bstack1lll11lll1l1_opy_(item, bstack1111ll1l11_opy_, bstack11ll1_opy_ (u"ࠧࡕࡧࡶࡸࡗࡻ࡮ࡔ࡭࡬ࡴࡵ࡫ࡤࠨ⎡"))
            pytest.skip(bstack1lll1l111lll_opy_)
            return # skip all existing operations
    global bstack1lll1l11111l_opy_
    threading.current_thread().percySessionName = item.nodeid
    if bstack111ll1ll11l_opy_():
        atexit.register(bstack1l1l1ll1ll_opy_)
        if not bstack1lll1l11111l_opy_:
            try:
                bstack1lll11ll1l1l_opy_ = [signal.SIGINT, signal.SIGTERM]
                if not bstack11l111ll11l_opy_():
                    bstack1lll11ll1l1l_opy_.extend([signal.SIGHUP, signal.SIGQUIT])
                for s in bstack1lll11ll1l1l_opy_:
                    signal.signal(s, bstack1lll11lll11l_opy_)
                bstack1lll1l11111l_opy_ = True
            except Exception as e:
                logger.debug(
                    bstack11ll1_opy_ (u"ࠣࡇࡵࡶࡴࡸࠠࡪࡰࠣࡶࡪ࡭ࡩࡴࡶࡨࡶࠥࡹࡩࡨࡰࡤࡰࠥ࡮ࡡ࡯ࡦ࡯ࡩࡷࡹ࠺ࠡࠤ⎢") + str(e))
        try:
            item.config.hook.pytest_selenium_runtest_makereport = bstack1llll1llll1l_opy_
        except Exception as err:
            threading.current_thread().testStatus = bstack11ll1_opy_ (u"ࠩࡳࡥࡸࡹࡥࡥࠩ⎣")
    try:
        if not bstack11lll11l11_opy_.on():
            return
        uuid = uuid4().__str__()
        bstack1111ll1l11_opy_ = {
            bstack11ll1_opy_ (u"ࠪࡹࡺ࡯ࡤࠨ⎤"): uuid,
            bstack11ll1_opy_ (u"ࠫࡸࡺࡡࡳࡶࡨࡨࡤࡧࡴࠨ⎥"): bstack111l11l1ll_opy_().isoformat() + bstack11ll1_opy_ (u"ࠬࡠࠧ⎦"),
            bstack11ll1_opy_ (u"࠭ࡴࡺࡲࡨࠫ⎧"): bstack11ll1_opy_ (u"ࠧࡩࡱࡲ࡯ࠬ⎨"),
            bstack11ll1_opy_ (u"ࠨࡪࡲࡳࡰࡥࡴࡺࡲࡨࠫ⎩"): bstack11ll1_opy_ (u"ࠩࡅࡉࡋࡕࡒࡆࡡࡈࡅࡈࡎࠧ⎪"),
            bstack11ll1_opy_ (u"ࠪ࡬ࡴࡵ࡫ࡠࡰࡤࡱࡪ࠭⎫"): bstack11ll1_opy_ (u"ࠫࡸ࡫ࡴࡶࡲࠪ⎬")
        }
        threading.current_thread().current_hook_uuid = uuid
        threading.current_thread().current_test_item = item
        store[bstack11ll1_opy_ (u"ࠬࡩࡵࡳࡴࡨࡲࡹࡥࡴࡦࡵࡷࡣ࡮ࡺࡥ࡮ࠩ⎭")] = item
        store[bstack11ll1_opy_ (u"࠭ࡣࡶࡴࡵࡩࡳࡺ࡟ࡩࡱࡲ࡯ࡤࡻࡵࡪࡦࠪ⎮")] = [uuid]
        if not _1111l1ll1l_opy_.get(item.nodeid, None):
            _1111l1ll1l_opy_[item.nodeid] = {bstack11ll1_opy_ (u"ࠧࡩࡱࡲ࡯ࡸ࠭⎯"): [], bstack11ll1_opy_ (u"ࠨࡨ࡬ࡼࡹࡻࡲࡦࡵࠪ⎰"): []}
        _1111l1ll1l_opy_[item.nodeid][bstack11ll1_opy_ (u"ࠩ࡫ࡳࡴࡱࡳࠨ⎱")].append(bstack1111ll1l11_opy_[bstack11ll1_opy_ (u"ࠪࡹࡺ࡯ࡤࠨ⎲")])
        _1111l1ll1l_opy_[item.nodeid + bstack11ll1_opy_ (u"ࠫ࠲ࡹࡥࡵࡷࡳࠫ⎳")] = bstack1111ll1l11_opy_
        bstack1lll11ll1l11_opy_(item, bstack1111ll1l11_opy_, bstack11ll1_opy_ (u"ࠬࡎ࡯ࡰ࡭ࡕࡹࡳ࡙ࡴࡢࡴࡷࡩࡩ࠭⎴"))
    except Exception as err:
        print(bstack11ll1_opy_ (u"࠭ࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢ࡬ࡲࠥࡶࡹࡵࡧࡶࡸࡤࡸࡵ࡯ࡶࡨࡷࡹࡥࡳࡦࡶࡸࡴ࠿ࠦࡻࡾࠩ⎵"), str(err))
def pytest_runtest_teardown(item):
    if cli.is_running():
        cli.test_framework.track_event(cli_context, bstack1llll1ll111_opy_.TEST, bstack1lll1111l11_opy_.POST, item)
        cli.test_framework.track_event(cli_context, bstack1llll1ll111_opy_.AFTER_EACH, bstack1lll1111l11_opy_.PRE, item, bstack11ll1_opy_ (u"ࠧࡵࡧࡤࡶࡩࡵࡷ࡯ࠩ⎶"))
        return # skip all existing operations
    try:
        global bstack1l11l11ll_opy_
        bstack1l11ll11ll_opy_ = 0
        if bstack1ll1lll1l1_opy_ is True:
            bstack1l11ll11ll_opy_ = int(os.environ.get(bstack11ll1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡑࡎࡄࡘࡋࡕࡒࡎࡡࡌࡒࡉࡋࡘࠨ⎷")))
        if bstack11l1l11l1_opy_.bstack1lll1l11l1_opy_() == bstack11ll1_opy_ (u"ࠤࡷࡶࡺ࡫ࠢ⎸"):
            if bstack11l1l11l1_opy_.bstack11l11lll1_opy_() == bstack11ll1_opy_ (u"ࠥࡸࡪࡹࡴࡤࡣࡶࡩࠧ⎹"):
                bstack1lll1l111111_opy_ = bstack1lll11l1l_opy_(threading.current_thread(), bstack11ll1_opy_ (u"ࠫࡵ࡫ࡲࡤࡻࡖࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠧ⎺"), None)
                bstack11lll11ll_opy_ = bstack1lll1l111111_opy_ + bstack11ll1_opy_ (u"ࠧ࠳ࡴࡦࡵࡷࡧࡦࡹࡥࠣ⎻")
                driver = getattr(item, bstack11ll1_opy_ (u"࠭࡟ࡥࡴ࡬ࡺࡪࡸࠧ⎼"), None)
                bstack1llll1l1ll_opy_ = getattr(item, bstack11ll1_opy_ (u"ࠧ࡯ࡣࡰࡩࠬ⎽"), None)
                bstack11lll1l11l_opy_ = getattr(item, bstack11ll1_opy_ (u"ࠨࡷࡸ࡭ࡩ࠭⎾"), None)
                PercySDK.screenshot(driver, bstack11lll11ll_opy_, bstack1llll1l1ll_opy_=bstack1llll1l1ll_opy_, bstack11lll1l11l_opy_=bstack11lll1l11l_opy_, bstack1l1lll111_opy_=bstack1l11ll11ll_opy_)
        if not cli.bstack1l11lll111l_opy_(bstack1l1ll11ll11_opy_):
            if getattr(item, bstack11ll1_opy_ (u"ࠩࡢࡥ࠶࠷ࡹࡠࡵࡷࡥࡷࡺࡥࡥࠩ⎿"), False):
                bstack1lll1l11ll_opy_.bstack1l1lllll1l_opy_(getattr(item, bstack11ll1_opy_ (u"ࠪࡣࡩࡸࡩࡷࡧࡵࠫ⏀"), None), bstack1l11l11ll_opy_, logger, item)
        if not bstack11lll11l11_opy_.on():
            return
        bstack1111ll1l11_opy_ = {
            bstack11ll1_opy_ (u"ࠫࡺࡻࡩࡥࠩ⏁"): uuid4().__str__(),
            bstack11ll1_opy_ (u"ࠬࡹࡴࡢࡴࡷࡩࡩࡥࡡࡵࠩ⏂"): bstack111l11l1ll_opy_().isoformat() + bstack11ll1_opy_ (u"࡚࠭ࠨ⏃"),
            bstack11ll1_opy_ (u"ࠧࡵࡻࡳࡩࠬ⏄"): bstack11ll1_opy_ (u"ࠨࡪࡲࡳࡰ࠭⏅"),
            bstack11ll1_opy_ (u"ࠩ࡫ࡳࡴࡱ࡟ࡵࡻࡳࡩࠬ⏆"): bstack11ll1_opy_ (u"ࠪࡅࡋ࡚ࡅࡓࡡࡈࡅࡈࡎࠧ⏇"),
            bstack11ll1_opy_ (u"ࠫ࡭ࡵ࡯࡬ࡡࡱࡥࡲ࡫ࠧ⏈"): bstack11ll1_opy_ (u"ࠬࡺࡥࡢࡴࡧࡳࡼࡴࠧ⏉")
        }
        _1111l1ll1l_opy_[item.nodeid + bstack11ll1_opy_ (u"࠭࠭ࡵࡧࡤࡶࡩࡵࡷ࡯ࠩ⏊")] = bstack1111ll1l11_opy_
        bstack1lll11ll1l11_opy_(item, bstack1111ll1l11_opy_, bstack11ll1_opy_ (u"ࠧࡉࡱࡲ࡯ࡗࡻ࡮ࡔࡶࡤࡶࡹ࡫ࡤࠨ⏋"))
    except Exception as err:
        print(bstack11ll1_opy_ (u"ࠨࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡱࡻࡷࡩࡸࡺ࡟ࡳࡷࡱࡸࡪࡹࡴࡠࡶࡨࡥࡷࡪ࡯ࡸࡰ࠽ࠤࢀࢃࠧ⏌"), str(err))
@pytest.hookimpl(hookwrapper=True)
def pytest_fixture_setup(fixturedef, request):
    if bstack1llll1lll111_opy_(fixturedef.argname):
        store[bstack11ll1_opy_ (u"ࠩࡦࡹࡷࡸࡥ࡯ࡶࡢࡱࡴࡪࡵ࡭ࡧࡢ࡭ࡹ࡫࡭ࠨ⏍")] = request.node
    elif bstack1lllll1111l1_opy_(fixturedef.argname):
        store[bstack11ll1_opy_ (u"ࠪࡧࡺࡸࡲࡦࡰࡷࡣࡨࡲࡡࡴࡵࡢ࡭ࡹ࡫࡭ࠨ⏎")] = request.node
    if not bstack11lll11l11_opy_.on():
        if cli.is_running():
            cli.test_framework.track_event(cli_context, bstack1llll1ll111_opy_.SETUP_FIXTURE, bstack1lll1111l11_opy_.PRE, fixturedef, request)
        outcome = yield
        if cli.is_running():
            cli.test_framework.track_event(cli_context, bstack1llll1ll111_opy_.SETUP_FIXTURE, bstack1lll1111l11_opy_.POST, fixturedef, request, outcome)
        return # skip all existing operations
    start_time = datetime.datetime.now()
    if cli.is_running():
        cli.test_framework.track_event(cli_context, bstack1llll1ll111_opy_.SETUP_FIXTURE, bstack1lll1111l11_opy_.PRE, fixturedef, request)
    outcome = yield
    if cli.is_running():
        cli.test_framework.track_event(cli_context, bstack1llll1ll111_opy_.SETUP_FIXTURE, bstack1lll1111l11_opy_.POST, fixturedef, request, outcome)
        return # skip all existing operations
    try:
        fixture = {
            bstack11ll1_opy_ (u"ࠫࡳࡧ࡭ࡦࠩ⏏"): fixturedef.argname,
            bstack11ll1_opy_ (u"ࠬࡸࡥࡴࡷ࡯ࡸࠬ⏐"): bstack111lllll1ll_opy_(outcome),
            bstack11ll1_opy_ (u"࠭ࡤࡶࡴࡤࡸ࡮ࡵ࡮ࠨ⏑"): (datetime.datetime.now() - start_time).total_seconds() * 1000
        }
        current_test_item = store[bstack11ll1_opy_ (u"ࠧࡤࡷࡵࡶࡪࡴࡴࡠࡶࡨࡷࡹࡥࡩࡵࡧࡰࠫ⏒")]
        if not _1111l1ll1l_opy_.get(current_test_item.nodeid, None):
            _1111l1ll1l_opy_[current_test_item.nodeid] = {bstack11ll1_opy_ (u"ࠨࡨ࡬ࡼࡹࡻࡲࡦࡵࠪ⏓"): []}
        _1111l1ll1l_opy_[current_test_item.nodeid][bstack11ll1_opy_ (u"ࠩࡩ࡭ࡽࡺࡵࡳࡧࡶࠫ⏔")].append(fixture)
    except Exception as err:
        logger.debug(bstack11ll1_opy_ (u"ࠪࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡩ࡯ࠢࡳࡽࡹ࡫ࡳࡵࡡࡩ࡭ࡽࡺࡵࡳࡧࡢࡷࡪࡺࡵࡱ࠼ࠣࡿࢂ࠭⏕"), str(err))
if bstack1l1l1l1l_opy_() and bstack11lll11l11_opy_.on():
    def pytest_bdd_before_step(request, step):
        if cli.is_running():
            cli.test_framework.track_event(cli_context, bstack1llll1ll111_opy_.STEP, bstack1lll1111l11_opy_.PRE, request, step)
            return
        try:
            _1111l1ll1l_opy_[request.node.nodeid][bstack11ll1_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡧࡥࡹࡧࠧ⏖")].bstack1lll11ll1l_opy_(id(step))
        except Exception as err:
            print(bstack11ll1_opy_ (u"ࠬࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡ࡫ࡱࠤࡵࡿࡴࡦࡵࡷࡣࡧࡪࡤࡠࡤࡨࡪࡴࡸࡥࡠࡵࡷࡩࡵࡀࠠࡼࡿࠪ⏗"), str(err))
    def pytest_bdd_step_error(request, step, exception):
        if cli.is_running():
            cli.test_framework.track_event(cli_context, bstack1llll1ll111_opy_.STEP, bstack1lll1111l11_opy_.POST, request, step, exception)
            return
        try:
            _1111l1ll1l_opy_[request.node.nodeid][bstack11ll1_opy_ (u"࠭ࡴࡦࡵࡷࡣࡩࡧࡴࡢࠩ⏘")].bstack111l1ll1ll_opy_(id(step), Result.failed(exception=exception))
        except Exception as err:
            print(bstack11ll1_opy_ (u"ࠧࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣ࡭ࡳࠦࡰࡺࡶࡨࡷࡹࡥࡢࡥࡦࡢࡷࡹ࡫ࡰࡠࡧࡵࡶࡴࡸ࠺ࠡࡽࢀࠫ⏙"), str(err))
    def pytest_bdd_after_step(request, step):
        if cli.is_running():
            cli.test_framework.track_event(cli_context, bstack1llll1ll111_opy_.STEP, bstack1lll1111l11_opy_.POST, request, step)
            return
        try:
            bstack111l1ll11l_opy_: bstack111ll111ll_opy_ = _1111l1ll1l_opy_[request.node.nodeid][bstack11ll1_opy_ (u"ࠨࡶࡨࡷࡹࡥࡤࡢࡶࡤࠫ⏚")]
            bstack111l1ll11l_opy_.bstack111l1ll1ll_opy_(id(step), Result.passed())
        except Exception as err:
            print(bstack11ll1_opy_ (u"ࠩࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥ࡯࡮ࠡࡲࡼࡸࡪࡹࡴࡠࡤࡧࡨࡤࡹࡴࡦࡲࡢࡩࡷࡸ࡯ࡳ࠼ࠣࡿࢂ࠭⏛"), str(err))
    def pytest_bdd_before_scenario(request, feature, scenario):
        global bstack1lll1l1111l1_opy_
        try:
            if not bstack11lll11l11_opy_.on() or bstack1lll1l1111l1_opy_ != bstack11ll1_opy_ (u"ࠪࡴࡾࡺࡥࡴࡶ࠰ࡦࡩࡪࠧ⏜"):
                return
            if cli.is_running():
                cli.test_framework.track_event(cli_context, bstack1llll1ll111_opy_.TEST, bstack1lll1111l11_opy_.PRE, request, feature, scenario)
                return
            driver = bstack1lll11l1l_opy_(threading.current_thread(), bstack11ll1_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮ࡗࡪࡹࡳࡪࡱࡱࡈࡷ࡯ࡶࡦࡴࠪ⏝"), None)
            if not _1111l1ll1l_opy_.get(request.node.nodeid, None):
                _1111l1ll1l_opy_[request.node.nodeid] = {}
            bstack111l1ll11l_opy_ = bstack111ll111ll_opy_.bstack1llll11ll111_opy_(
                scenario, feature, request.node,
                name=bstack1llll1llllll_opy_(request.node, scenario),
                started_at=bstack111lll1lll_opy_(),
                file_path=feature.filename,
                scope=[feature.name],
                framework=bstack11ll1_opy_ (u"ࠬࡖࡹࡵࡧࡶࡸ࠲ࡩࡵࡤࡷࡰࡦࡪࡸࠧ⏞"),
                tags=bstack1lllll111111_opy_(feature, scenario),
                bstack111l1l11ll_opy_=bstack11lll11l11_opy_.bstack111l1ll111_opy_(driver) if driver and driver.session_id else {}
            )
            _1111l1ll1l_opy_[request.node.nodeid][bstack11ll1_opy_ (u"࠭ࡴࡦࡵࡷࡣࡩࡧࡴࡢࠩ⏟")] = bstack111l1ll11l_opy_
            bstack1lll11llll11_opy_(bstack111l1ll11l_opy_.uuid)
            bstack11lll11l11_opy_.bstack111ll11l11_opy_(bstack11ll1_opy_ (u"ࠧࡕࡧࡶࡸࡗࡻ࡮ࡔࡶࡤࡶࡹ࡫ࡤࠨ⏠"), bstack111l1ll11l_opy_)
        except Exception as err:
            print(bstack11ll1_opy_ (u"ࠨࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡱࡻࡷࡩࡸࡺ࡟ࡣࡦࡧࡣࡧ࡫ࡦࡰࡴࡨࡣࡸࡩࡥ࡯ࡣࡵ࡭ࡴࡀࠠࡼࡿࠪ⏡"), str(err))
def bstack1lll11ll1lll_opy_(bstack111l11llll_opy_):
    if bstack111l11llll_opy_ in store[bstack11ll1_opy_ (u"ࠩࡦࡹࡷࡸࡥ࡯ࡶࡢ࡬ࡴࡵ࡫ࡠࡷࡸ࡭ࡩ࠭⏢")]:
        store[bstack11ll1_opy_ (u"ࠪࡧࡺࡸࡲࡦࡰࡷࡣ࡭ࡵ࡯࡬ࡡࡸࡹ࡮ࡪࠧ⏣")].remove(bstack111l11llll_opy_)
def bstack1lll11llll11_opy_(test_uuid):
    store[bstack11ll1_opy_ (u"ࠫࡨࡻࡲࡳࡧࡱࡸࡤࡺࡥࡴࡶࡢࡹࡺ࡯ࡤࠨ⏤")] = test_uuid
    threading.current_thread().current_test_uuid = test_uuid
@bstack11lll11l11_opy_.bstack1lll1lll11ll_opy_
def bstack1lll11lll1ll_opy_(item, call, report):
    logger.debug(bstack11ll1_opy_ (u"ࠬ࡮ࡡ࡯ࡦ࡯ࡩࡤࡵ࠱࠲ࡻࡢࡸࡪࡹࡴࡠࡧࡹࡩࡳࡺ࠺ࠡࡵࡷࡥࡷࡺࠧ⏥"))
    global bstack1lll1l1111l1_opy_
    bstack1llll1ll1_opy_ = bstack111lll1lll_opy_()
    if hasattr(report, bstack11ll1_opy_ (u"࠭ࡳࡵࡱࡳࠫ⏦")):
        bstack1llll1ll1_opy_ = bstack111llll1l1l_opy_(report.stop)
    elif hasattr(report, bstack11ll1_opy_ (u"ࠧࡴࡶࡤࡶࡹ࠭⏧")):
        bstack1llll1ll1_opy_ = bstack111llll1l1l_opy_(report.start)
    try:
        if getattr(report, bstack11ll1_opy_ (u"ࠨࡹ࡫ࡩࡳ࠭⏨"), bstack11ll1_opy_ (u"ࠩࠪ⏩")) == bstack11ll1_opy_ (u"ࠪࡧࡦࡲ࡬ࠨ⏪"):
            logger.debug(bstack11ll1_opy_ (u"ࠫ࡭ࡧ࡮ࡥ࡮ࡨࡣࡴ࠷࠱ࡺࡡࡷࡩࡸࡺ࡟ࡦࡸࡨࡲࡹࡀࠠࡴࡶࡤࡸࡪࠦ࠭ࠡࡽࢀ࠰ࠥ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࠡ࠯ࠣࡿࢂ࠭⏫").format(getattr(report, bstack11ll1_opy_ (u"ࠬࡽࡨࡦࡰࠪ⏬"), bstack11ll1_opy_ (u"࠭ࠧ⏭")).__str__(), bstack1lll1l1111l1_opy_))
            if bstack1lll1l1111l1_opy_ == bstack11ll1_opy_ (u"ࠧࡱࡻࡷࡩࡸࡺࠧ⏮"):
                _1111l1ll1l_opy_[item.nodeid][bstack11ll1_opy_ (u"ࠨࡨ࡬ࡲ࡮ࡹࡨࡦࡦࡢࡥࡹ࠭⏯")] = bstack1llll1ll1_opy_
                bstack1lll11lll1l1_opy_(item, _1111l1ll1l_opy_[item.nodeid], bstack11ll1_opy_ (u"ࠩࡗࡩࡸࡺࡒࡶࡰࡉ࡭ࡳ࡯ࡳࡩࡧࡧࠫ⏰"), report, call)
                store[bstack11ll1_opy_ (u"ࠪࡧࡺࡸࡲࡦࡰࡷࡣࡹ࡫ࡳࡵࡡࡸࡹ࡮ࡪࠧ⏱")] = None
            elif bstack1lll1l1111l1_opy_ == bstack11ll1_opy_ (u"ࠦࡵࡿࡴࡦࡵࡷ࠱ࡧࡪࡤࠣ⏲"):
                bstack111l1ll11l_opy_ = _1111l1ll1l_opy_[item.nodeid][bstack11ll1_opy_ (u"ࠬࡺࡥࡴࡶࡢࡨࡦࡺࡡࠨ⏳")]
                bstack111l1ll11l_opy_.set(hooks=_1111l1ll1l_opy_[item.nodeid].get(bstack11ll1_opy_ (u"࠭ࡨࡰࡱ࡮ࡷࠬ⏴"), []))
                exception, bstack111l1l1ll1_opy_ = None, None
                if call.excinfo:
                    exception = call.excinfo.value
                    bstack111l1l1ll1_opy_ = [call.excinfo.exconly(), getattr(report, bstack11ll1_opy_ (u"ࠧ࡭ࡱࡱ࡫ࡷ࡫ࡰࡳࡶࡨࡼࡹ࠭⏵"), bstack11ll1_opy_ (u"ࠨࠩ⏶"))]
                bstack111l1ll11l_opy_.stop(time=bstack1llll1ll1_opy_, result=Result(result=getattr(report, bstack11ll1_opy_ (u"ࠩࡲࡹࡹࡩ࡯࡮ࡧࠪ⏷"), bstack11ll1_opy_ (u"ࠪࡴࡦࡹࡳࡦࡦࠪ⏸")), exception=exception, bstack111l1l1ll1_opy_=bstack111l1l1ll1_opy_))
                bstack11lll11l11_opy_.bstack111ll11l11_opy_(bstack11ll1_opy_ (u"࡙ࠫ࡫ࡳࡵࡔࡸࡲࡋ࡯࡮ࡪࡵ࡫ࡩࡩ࠭⏹"), _1111l1ll1l_opy_[item.nodeid][bstack11ll1_opy_ (u"ࠬࡺࡥࡴࡶࡢࡨࡦࡺࡡࠨ⏺")])
        elif getattr(report, bstack11ll1_opy_ (u"࠭ࡷࡩࡧࡱࠫ⏻"), bstack11ll1_opy_ (u"ࠧࠨ⏼")) in [bstack11ll1_opy_ (u"ࠨࡵࡨࡸࡺࡶࠧ⏽"), bstack11ll1_opy_ (u"ࠩࡷࡩࡦࡸࡤࡰࡹࡱࠫ⏾")]:
            logger.debug(bstack11ll1_opy_ (u"ࠪ࡬ࡦࡴࡤ࡭ࡧࡢࡳ࠶࠷ࡹࡠࡶࡨࡷࡹࡥࡥࡷࡧࡱࡸ࠿ࠦࡳࡵࡣࡷࡩࠥ࠳ࠠࡼࡿ࠯ࠤ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱࠠ࠮ࠢࡾࢁࠬ⏿").format(getattr(report, bstack11ll1_opy_ (u"ࠫࡼ࡮ࡥ࡯ࠩ␀"), bstack11ll1_opy_ (u"ࠬ࠭␁")).__str__(), bstack1lll1l1111l1_opy_))
            bstack111l1lll11_opy_ = item.nodeid + bstack11ll1_opy_ (u"࠭࠭ࠨ␂") + getattr(report, bstack11ll1_opy_ (u"ࠧࡸࡪࡨࡲࠬ␃"), bstack11ll1_opy_ (u"ࠨࠩ␄"))
            if getattr(report, bstack11ll1_opy_ (u"ࠩࡶ࡯࡮ࡶࡰࡦࡦࠪ␅"), False):
                hook_type = bstack11ll1_opy_ (u"ࠪࡆࡊࡌࡏࡓࡇࡢࡉࡆࡉࡈࠨ␆") if getattr(report, bstack11ll1_opy_ (u"ࠫࡼ࡮ࡥ࡯ࠩ␇"), bstack11ll1_opy_ (u"ࠬ࠭␈")) == bstack11ll1_opy_ (u"࠭ࡳࡦࡶࡸࡴࠬ␉") else bstack11ll1_opy_ (u"ࠧࡂࡈࡗࡉࡗࡥࡅࡂࡅࡋࠫ␊")
                _1111l1ll1l_opy_[bstack111l1lll11_opy_] = {
                    bstack11ll1_opy_ (u"ࠨࡷࡸ࡭ࡩ࠭␋"): uuid4().__str__(),
                    bstack11ll1_opy_ (u"ࠩࡶࡸࡦࡸࡴࡦࡦࡢࡥࡹ࠭␌"): bstack1llll1ll1_opy_,
                    bstack11ll1_opy_ (u"ࠪ࡬ࡴࡵ࡫ࡠࡶࡼࡴࡪ࠭␍"): hook_type
                }
            _1111l1ll1l_opy_[bstack111l1lll11_opy_][bstack11ll1_opy_ (u"ࠫ࡫࡯࡮ࡪࡵ࡫ࡩࡩࡥࡡࡵࠩ␎")] = bstack1llll1ll1_opy_
            bstack1lll11ll1lll_opy_(_1111l1ll1l_opy_[bstack111l1lll11_opy_][bstack11ll1_opy_ (u"ࠬࡻࡵࡪࡦࠪ␏")])
            bstack1lll11ll1l11_opy_(item, _1111l1ll1l_opy_[bstack111l1lll11_opy_], bstack11ll1_opy_ (u"࠭ࡈࡰࡱ࡮ࡖࡺࡴࡆࡪࡰ࡬ࡷ࡭࡫ࡤࠨ␐"), report, call)
            if getattr(report, bstack11ll1_opy_ (u"ࠧࡸࡪࡨࡲࠬ␑"), bstack11ll1_opy_ (u"ࠨࠩ␒")) == bstack11ll1_opy_ (u"ࠩࡶࡩࡹࡻࡰࠨ␓"):
                if getattr(report, bstack11ll1_opy_ (u"ࠪࡳࡺࡺࡣࡰ࡯ࡨࠫ␔"), bstack11ll1_opy_ (u"ࠫࡵࡧࡳࡴࡧࡧࠫ␕")) == bstack11ll1_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡨࡨࠬ␖"):
                    bstack1111ll1l11_opy_ = {
                        bstack11ll1_opy_ (u"࠭ࡵࡶ࡫ࡧࠫ␗"): uuid4().__str__(),
                        bstack11ll1_opy_ (u"ࠧࡴࡶࡤࡶࡹ࡫ࡤࡠࡣࡷࠫ␘"): bstack111lll1lll_opy_(),
                        bstack11ll1_opy_ (u"ࠨࡨ࡬ࡲ࡮ࡹࡨࡦࡦࡢࡥࡹ࠭␙"): bstack111lll1lll_opy_()
                    }
                    _1111l1ll1l_opy_[item.nodeid] = {**_1111l1ll1l_opy_[item.nodeid], **bstack1111ll1l11_opy_}
                    bstack1lll11lll1l1_opy_(item, _1111l1ll1l_opy_[item.nodeid], bstack11ll1_opy_ (u"ࠩࡗࡩࡸࡺࡒࡶࡰࡖࡸࡦࡸࡴࡦࡦࠪ␚"))
                    bstack1lll11lll1l1_opy_(item, _1111l1ll1l_opy_[item.nodeid], bstack11ll1_opy_ (u"ࠪࡘࡪࡹࡴࡓࡷࡱࡊ࡮ࡴࡩࡴࡪࡨࡨࠬ␛"), report, call)
    except Exception as err:
        print(bstack11ll1_opy_ (u"ࠫࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡪࡰࠣ࡬ࡦࡴࡤ࡭ࡧࡢࡳ࠶࠷ࡹࡠࡶࡨࡷࡹࡥࡥࡷࡧࡱࡸ࠿ࠦࡻࡾࠩ␜"), str(err))
def bstack1lll11llll1l_opy_(test, bstack1111ll1l11_opy_, result=None, call=None, bstack1l1l11lll1_opy_=None, outcome=None):
    file_path = os.path.relpath(test.fspath.strpath, start=os.getcwd())
    bstack111l1ll11l_opy_ = {
        bstack11ll1_opy_ (u"ࠬࡻࡵࡪࡦࠪ␝"): bstack1111ll1l11_opy_[bstack11ll1_opy_ (u"࠭ࡵࡶ࡫ࡧࠫ␞")],
        bstack11ll1_opy_ (u"ࠧࡵࡻࡳࡩࠬ␟"): bstack11ll1_opy_ (u"ࠨࡶࡨࡷࡹ࠭␠"),
        bstack11ll1_opy_ (u"ࠩࡱࡥࡲ࡫ࠧ␡"): test.name,
        bstack11ll1_opy_ (u"ࠪࡦࡴࡪࡹࠨ␢"): {
            bstack11ll1_opy_ (u"ࠫࡱࡧ࡮ࡨࠩ␣"): bstack11ll1_opy_ (u"ࠬࡶࡹࡵࡪࡲࡲࠬ␤"),
            bstack11ll1_opy_ (u"࠭ࡣࡰࡦࡨࠫ␥"): inspect.getsource(test.obj)
        },
        bstack11ll1_opy_ (u"ࠧࡪࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫ␦"): test.name,
        bstack11ll1_opy_ (u"ࠨࡵࡦࡳࡵ࡫ࠧ␧"): test.name,
        bstack11ll1_opy_ (u"ࠩࡶࡧࡴࡶࡥࡴࠩ␨"): bstack1l11llll1l_opy_.bstack111l11l1l1_opy_(test),
        bstack11ll1_opy_ (u"ࠪࡪ࡮ࡲࡥࡠࡰࡤࡱࡪ࠭␩"): file_path,
        bstack11ll1_opy_ (u"ࠫࡱࡵࡣࡢࡶ࡬ࡳࡳ࠭␪"): file_path,
        bstack11ll1_opy_ (u"ࠬࡸࡥࡴࡷ࡯ࡸࠬ␫"): bstack11ll1_opy_ (u"࠭ࡰࡦࡰࡧ࡭ࡳ࡭ࠧ␬"),
        bstack11ll1_opy_ (u"ࠧࡷࡥࡢࡪ࡮ࡲࡥࡱࡣࡷ࡬ࠬ␭"): file_path,
        bstack11ll1_opy_ (u"ࠨࡵࡷࡥࡷࡺࡥࡥࡡࡤࡸࠬ␮"): bstack1111ll1l11_opy_[bstack11ll1_opy_ (u"ࠩࡶࡸࡦࡸࡴࡦࡦࡢࡥࡹ࠭␯")],
        bstack11ll1_opy_ (u"ࠪࡪࡷࡧ࡭ࡦࡹࡲࡶࡰ࠭␰"): bstack11ll1_opy_ (u"ࠫࡕࡿࡴࡦࡵࡷࠫ␱"),
        bstack11ll1_opy_ (u"ࠬࡩࡵࡴࡶࡲࡱࡗ࡫ࡲࡶࡰࡓࡥࡷࡧ࡭ࠨ␲"): {
            bstack11ll1_opy_ (u"࠭ࡲࡦࡴࡸࡲࡤࡴࡡ࡮ࡧࠪ␳"): test.nodeid
        },
        bstack11ll1_opy_ (u"ࠧࡵࡣࡪࡷࠬ␴"): bstack111lllll111_opy_(test.own_markers)
    }
    if bstack1l1l11lll1_opy_ in [bstack11ll1_opy_ (u"ࠨࡖࡨࡷࡹࡘࡵ࡯ࡕ࡮࡭ࡵࡶࡥࡥࠩ␵"), bstack11ll1_opy_ (u"ࠩࡗࡩࡸࡺࡒࡶࡰࡉ࡭ࡳ࡯ࡳࡩࡧࡧࠫ␶")]:
        bstack111l1ll11l_opy_[bstack11ll1_opy_ (u"ࠪࡱࡪࡺࡡࠨ␷")] = {
            bstack11ll1_opy_ (u"ࠫ࡫࡯ࡸࡵࡷࡵࡩࡸ࠭␸"): bstack1111ll1l11_opy_.get(bstack11ll1_opy_ (u"ࠬ࡬ࡩࡹࡶࡸࡶࡪࡹࠧ␹"), [])
        }
    if bstack1l1l11lll1_opy_ == bstack11ll1_opy_ (u"࠭ࡔࡦࡵࡷࡖࡺࡴࡓ࡬࡫ࡳࡴࡪࡪࠧ␺"):
        bstack111l1ll11l_opy_[bstack11ll1_opy_ (u"ࠧࡳࡧࡶࡹࡱࡺࠧ␻")] = bstack11ll1_opy_ (u"ࠨࡵ࡮࡭ࡵࡶࡥࡥࠩ␼")
        bstack111l1ll11l_opy_[bstack11ll1_opy_ (u"ࠩ࡫ࡳࡴࡱࡳࠨ␽")] = bstack1111ll1l11_opy_[bstack11ll1_opy_ (u"ࠪ࡬ࡴࡵ࡫ࡴࠩ␾")]
        bstack111l1ll11l_opy_[bstack11ll1_opy_ (u"ࠫ࡫࡯࡮ࡪࡵ࡫ࡩࡩࡥࡡࡵࠩ␿")] = bstack1111ll1l11_opy_[bstack11ll1_opy_ (u"ࠬ࡬ࡩ࡯࡫ࡶ࡬ࡪࡪ࡟ࡢࡶࠪ⑀")]
    if result:
        bstack111l1ll11l_opy_[bstack11ll1_opy_ (u"࠭ࡲࡦࡵࡸࡰࡹ࠭⑁")] = result.outcome
        bstack111l1ll11l_opy_[bstack11ll1_opy_ (u"ࠧࡥࡷࡵࡥࡹ࡯࡯࡯ࡡ࡬ࡲࡤࡳࡳࠨ⑂")] = result.duration * 1000
        bstack111l1ll11l_opy_[bstack11ll1_opy_ (u"ࠨࡨ࡬ࡲ࡮ࡹࡨࡦࡦࡢࡥࡹ࠭⑃")] = bstack1111ll1l11_opy_[bstack11ll1_opy_ (u"ࠩࡩ࡭ࡳ࡯ࡳࡩࡧࡧࡣࡦࡺࠧ⑄")]
        if result.failed:
            bstack111l1ll11l_opy_[bstack11ll1_opy_ (u"ࠪࡪࡦ࡯࡬ࡶࡴࡨࡣࡹࡿࡰࡦࠩ⑅")] = bstack11lll11l11_opy_.bstack1lllll1ll11_opy_(call.excinfo.typename)
            bstack111l1ll11l_opy_[bstack11ll1_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡷࡵࡩࠬ⑆")] = bstack11lll11l11_opy_.bstack1lll1lll1ll1_opy_(call.excinfo, result)
        bstack111l1ll11l_opy_[bstack11ll1_opy_ (u"ࠬ࡮࡯ࡰ࡭ࡶࠫ⑇")] = bstack1111ll1l11_opy_[bstack11ll1_opy_ (u"࠭ࡨࡰࡱ࡮ࡷࠬ⑈")]
    if outcome:
        bstack111l1ll11l_opy_[bstack11ll1_opy_ (u"ࠧࡳࡧࡶࡹࡱࡺࠧ⑉")] = bstack111lllll1ll_opy_(outcome)
        bstack111l1ll11l_opy_[bstack11ll1_opy_ (u"ࠨࡦࡸࡶࡦࡺࡩࡰࡰࡢ࡭ࡳࡥ࡭ࡴࠩ⑊")] = 0
        bstack111l1ll11l_opy_[bstack11ll1_opy_ (u"ࠩࡩ࡭ࡳ࡯ࡳࡩࡧࡧࡣࡦࡺࠧ⑋")] = bstack1111ll1l11_opy_[bstack11ll1_opy_ (u"ࠪࡪ࡮ࡴࡩࡴࡪࡨࡨࡤࡧࡴࠨ⑌")]
        if bstack111l1ll11l_opy_[bstack11ll1_opy_ (u"ࠫࡷ࡫ࡳࡶ࡮ࡷࠫ⑍")] == bstack11ll1_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡨࡨࠬ⑎"):
            bstack111l1ll11l_opy_[bstack11ll1_opy_ (u"࠭ࡦࡢ࡫࡯ࡹࡷ࡫࡟ࡵࡻࡳࡩࠬ⑏")] = bstack11ll1_opy_ (u"ࠧࡖࡰ࡫ࡥࡳࡪ࡬ࡦࡦࡈࡶࡷࡵࡲࠨ⑐")  # bstack1lll11ll11l1_opy_
            bstack111l1ll11l_opy_[bstack11ll1_opy_ (u"ࠨࡨࡤ࡭ࡱࡻࡲࡦࠩ⑑")] = [{bstack11ll1_opy_ (u"ࠩࡥࡥࡨࡱࡴࡳࡣࡦࡩࠬ⑒"): [bstack11ll1_opy_ (u"ࠪࡷࡴࡳࡥࠡࡧࡵࡶࡴࡸࠧ⑓")]}]
        bstack111l1ll11l_opy_[bstack11ll1_opy_ (u"ࠫ࡭ࡵ࡯࡬ࡵࠪ⑔")] = bstack1111ll1l11_opy_[bstack11ll1_opy_ (u"ࠬ࡮࡯ࡰ࡭ࡶࠫ⑕")]
    return bstack111l1ll11l_opy_
def bstack1lll11l1llll_opy_(test, bstack1111llll11_opy_, bstack1l1l11lll1_opy_, result, call, outcome, bstack1lll1l111ll1_opy_):
    file_path = os.path.relpath(test.fspath.strpath, start=os.getcwd())
    hook_type = bstack1111llll11_opy_[bstack11ll1_opy_ (u"࠭ࡨࡰࡱ࡮ࡣࡹࡿࡰࡦࠩ⑖")]
    hook_name = bstack1111llll11_opy_[bstack11ll1_opy_ (u"ࠧࡩࡱࡲ࡯ࡤࡴࡡ࡮ࡧࠪ⑗")]
    hook_data = {
        bstack11ll1_opy_ (u"ࠨࡷࡸ࡭ࡩ࠭⑘"): bstack1111llll11_opy_[bstack11ll1_opy_ (u"ࠩࡸࡹ࡮ࡪࠧ⑙")],
        bstack11ll1_opy_ (u"ࠪࡸࡾࡶࡥࠨ⑚"): bstack11ll1_opy_ (u"ࠫ࡭ࡵ࡯࡬ࠩ⑛"),
        bstack11ll1_opy_ (u"ࠬࡴࡡ࡮ࡧࠪ⑜"): bstack11ll1_opy_ (u"࠭ࡻࡾࠩ⑝").format(bstack1lllll111l1l_opy_(hook_name)),
        bstack11ll1_opy_ (u"ࠧࡣࡱࡧࡽࠬ⑞"): {
            bstack11ll1_opy_ (u"ࠨ࡮ࡤࡲ࡬࠭⑟"): bstack11ll1_opy_ (u"ࠩࡳࡽࡹ࡮࡯࡯ࠩ①"),
            bstack11ll1_opy_ (u"ࠪࡧࡴࡪࡥࠨ②"): None
        },
        bstack11ll1_opy_ (u"ࠫࡸࡩ࡯ࡱࡧࠪ③"): test.name,
        bstack11ll1_opy_ (u"ࠬࡹࡣࡰࡲࡨࡷࠬ④"): bstack1l11llll1l_opy_.bstack111l11l1l1_opy_(test, hook_name),
        bstack11ll1_opy_ (u"࠭ࡦࡪ࡮ࡨࡣࡳࡧ࡭ࡦࠩ⑤"): file_path,
        bstack11ll1_opy_ (u"ࠧ࡭ࡱࡦࡥࡹ࡯࡯࡯ࠩ⑥"): file_path,
        bstack11ll1_opy_ (u"ࠨࡴࡨࡷࡺࡲࡴࠨ⑦"): bstack11ll1_opy_ (u"ࠩࡳࡩࡳࡪࡩ࡯ࡩࠪ⑧"),
        bstack11ll1_opy_ (u"ࠪࡺࡨࡥࡦࡪ࡮ࡨࡴࡦࡺࡨࠨ⑨"): file_path,
        bstack11ll1_opy_ (u"ࠫࡸࡺࡡࡳࡶࡨࡨࡤࡧࡴࠨ⑩"): bstack1111llll11_opy_[bstack11ll1_opy_ (u"ࠬࡹࡴࡢࡴࡷࡩࡩࡥࡡࡵࠩ⑪")],
        bstack11ll1_opy_ (u"࠭ࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࠩ⑫"): bstack11ll1_opy_ (u"ࠧࡑࡻࡷࡩࡸࡺ࠭ࡤࡷࡦࡹࡲࡨࡥࡳࠩ⑬") if bstack1lll1l1111l1_opy_ == bstack11ll1_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴ࠮ࡤࡧࡨࠬ⑭") else bstack11ll1_opy_ (u"ࠩࡓࡽࡹ࡫ࡳࡵࠩ⑮"),
        bstack11ll1_opy_ (u"ࠪ࡬ࡴࡵ࡫ࡠࡶࡼࡴࡪ࠭⑯"): hook_type
    }
    bstack1l111lll1l1_opy_ = bstack1111llllll_opy_(_1111l1ll1l_opy_.get(test.nodeid, None))
    if bstack1l111lll1l1_opy_:
        hook_data[bstack11ll1_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡵࡹࡳࡥࡩࡥࠩ⑰")] = bstack1l111lll1l1_opy_
    if result:
        hook_data[bstack11ll1_opy_ (u"ࠬࡸࡥࡴࡷ࡯ࡸࠬ⑱")] = result.outcome
        hook_data[bstack11ll1_opy_ (u"࠭ࡤࡶࡴࡤࡸ࡮ࡵ࡮ࡠ࡫ࡱࡣࡲࡹࠧ⑲")] = result.duration * 1000
        hook_data[bstack11ll1_opy_ (u"ࠧࡧ࡫ࡱ࡭ࡸ࡮ࡥࡥࡡࡤࡸࠬ⑳")] = bstack1111llll11_opy_[bstack11ll1_opy_ (u"ࠨࡨ࡬ࡲ࡮ࡹࡨࡦࡦࡢࡥࡹ࠭⑴")]
        if result.failed:
            hook_data[bstack11ll1_opy_ (u"ࠩࡩࡥ࡮ࡲࡵࡳࡧࡢࡸࡾࡶࡥࠨ⑵")] = bstack11lll11l11_opy_.bstack1lllll1ll11_opy_(call.excinfo.typename)
            hook_data[bstack11ll1_opy_ (u"ࠪࡪࡦ࡯࡬ࡶࡴࡨࠫ⑶")] = bstack11lll11l11_opy_.bstack1lll1lll1ll1_opy_(call.excinfo, result)
    if outcome:
        hook_data[bstack11ll1_opy_ (u"ࠫࡷ࡫ࡳࡶ࡮ࡷࠫ⑷")] = bstack111lllll1ll_opy_(outcome)
        hook_data[bstack11ll1_opy_ (u"ࠬࡪࡵࡳࡣࡷ࡭ࡴࡴ࡟ࡪࡰࡢࡱࡸ࠭⑸")] = 100
        hook_data[bstack11ll1_opy_ (u"࠭ࡦࡪࡰ࡬ࡷ࡭࡫ࡤࡠࡣࡷࠫ⑹")] = bstack1111llll11_opy_[bstack11ll1_opy_ (u"ࠧࡧ࡫ࡱ࡭ࡸ࡮ࡥࡥࡡࡤࡸࠬ⑺")]
        if hook_data[bstack11ll1_opy_ (u"ࠨࡴࡨࡷࡺࡲࡴࠨ⑻")] == bstack11ll1_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࠩ⑼"):
            hook_data[bstack11ll1_opy_ (u"ࠪࡪࡦ࡯࡬ࡶࡴࡨࡣࡹࡿࡰࡦࠩ⑽")] = bstack11ll1_opy_ (u"࡚ࠫࡴࡨࡢࡰࡧࡰࡪࡪࡅࡳࡴࡲࡶࠬ⑾")  # bstack1lll11ll11l1_opy_
            hook_data[bstack11ll1_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡸࡶࡪ࠭⑿")] = [{bstack11ll1_opy_ (u"࠭ࡢࡢࡥ࡮ࡸࡷࡧࡣࡦࠩ⒀"): [bstack11ll1_opy_ (u"ࠧࡴࡱࡰࡩࠥ࡫ࡲࡳࡱࡵࠫ⒁")]}]
    if bstack1lll1l111ll1_opy_:
        hook_data[bstack11ll1_opy_ (u"ࠨࡴࡨࡷࡺࡲࡴࠨ⒂")] = bstack1lll1l111ll1_opy_.result
        hook_data[bstack11ll1_opy_ (u"ࠩࡧࡹࡷࡧࡴࡪࡱࡱࡣ࡮ࡴ࡟࡮ࡵࠪ⒃")] = bstack111ll1ll111_opy_(bstack1111llll11_opy_[bstack11ll1_opy_ (u"ࠪࡷࡹࡧࡲࡵࡧࡧࡣࡦࡺࠧ⒄")], bstack1111llll11_opy_[bstack11ll1_opy_ (u"ࠫ࡫࡯࡮ࡪࡵ࡫ࡩࡩࡥࡡࡵࠩ⒅")])
        hook_data[bstack11ll1_opy_ (u"ࠬ࡬ࡩ࡯࡫ࡶ࡬ࡪࡪ࡟ࡢࡶࠪ⒆")] = bstack1111llll11_opy_[bstack11ll1_opy_ (u"࠭ࡦࡪࡰ࡬ࡷ࡭࡫ࡤࡠࡣࡷࠫ⒇")]
        if hook_data[bstack11ll1_opy_ (u"ࠧࡳࡧࡶࡹࡱࡺࠧ⒈")] == bstack11ll1_opy_ (u"ࠨࡨࡤ࡭ࡱ࡫ࡤࠨ⒉"):
            hook_data[bstack11ll1_opy_ (u"ࠩࡩࡥ࡮ࡲࡵࡳࡧࡢࡸࡾࡶࡥࠨ⒊")] = bstack11lll11l11_opy_.bstack1lllll1ll11_opy_(bstack1lll1l111ll1_opy_.exception_type)
            hook_data[bstack11ll1_opy_ (u"ࠪࡪࡦ࡯࡬ࡶࡴࡨࠫ⒋")] = [{bstack11ll1_opy_ (u"ࠫࡧࡧࡣ࡬ࡶࡵࡥࡨ࡫ࠧ⒌"): bstack111ll1ll1ll_opy_(bstack1lll1l111ll1_opy_.exception)}]
    return hook_data
def bstack1lll11lll1l1_opy_(test, bstack1111ll1l11_opy_, bstack1l1l11lll1_opy_, result=None, call=None, outcome=None):
    logger.debug(bstack11ll1_opy_ (u"ࠬࡹࡥ࡯ࡦࡢࡸࡪࡹࡴࡠࡴࡸࡲࡤ࡫ࡶࡦࡰࡷ࠾ࠥࡇࡴࡵࡧࡰࡴࡹ࡯࡮ࡨࠢࡷࡳࠥ࡭ࡥ࡯ࡧࡵࡥࡹ࡫ࠠࡵࡧࡶࡸࠥࡪࡡࡵࡣࠣࡪࡴࡸࠠࡦࡸࡨࡲࡹࡥࡴࡺࡲࡨࠤ࠲ࠦࡻࡾࠩ⒍").format(bstack1l1l11lll1_opy_))
    bstack111l1ll11l_opy_ = bstack1lll11llll1l_opy_(test, bstack1111ll1l11_opy_, result, call, bstack1l1l11lll1_opy_, outcome)
    driver = getattr(test, bstack11ll1_opy_ (u"࠭࡟ࡥࡴ࡬ࡺࡪࡸࠧ⒎"), None)
    if bstack1l1l11lll1_opy_ == bstack11ll1_opy_ (u"ࠧࡕࡧࡶࡸࡗࡻ࡮ࡔࡶࡤࡶࡹ࡫ࡤࠨ⒏") and driver:
        bstack111l1ll11l_opy_[bstack11ll1_opy_ (u"ࠨ࡫ࡱࡸࡪ࡭ࡲࡢࡶ࡬ࡳࡳࡹࠧ⒐")] = bstack11lll11l11_opy_.bstack111l1ll111_opy_(driver)
    if bstack1l1l11lll1_opy_ == bstack11ll1_opy_ (u"ࠩࡗࡩࡸࡺࡒࡶࡰࡖ࡯࡮ࡶࡰࡦࡦࠪ⒑"):
        bstack1l1l11lll1_opy_ = bstack11ll1_opy_ (u"ࠪࡘࡪࡹࡴࡓࡷࡱࡊ࡮ࡴࡩࡴࡪࡨࡨࠬ⒒")
    bstack1111l1llll_opy_ = {
        bstack11ll1_opy_ (u"ࠫࡪࡼࡥ࡯ࡶࡢࡸࡾࡶࡥࠨ⒓"): bstack1l1l11lll1_opy_,
        bstack11ll1_opy_ (u"ࠬࡺࡥࡴࡶࡢࡶࡺࡴࠧ⒔"): bstack111l1ll11l_opy_
    }
    bstack11lll11l11_opy_.bstack1lll1llll_opy_(bstack1111l1llll_opy_)
    if bstack1l1l11lll1_opy_ == bstack11ll1_opy_ (u"࠭ࡔࡦࡵࡷࡖࡺࡴࡓࡵࡣࡵࡸࡪࡪࠧ⒕"):
        threading.current_thread().bstackTestMeta = {bstack11ll1_opy_ (u"ࠧࡴࡶࡤࡸࡺࡹࠧ⒖"): bstack11ll1_opy_ (u"ࠨࡲࡨࡲࡩ࡯࡮ࡨࠩ⒗")}
    elif bstack1l1l11lll1_opy_ == bstack11ll1_opy_ (u"ࠩࡗࡩࡸࡺࡒࡶࡰࡉ࡭ࡳ࡯ࡳࡩࡧࡧࠫ⒘"):
        threading.current_thread().bstackTestMeta = {bstack11ll1_opy_ (u"ࠪࡷࡹࡧࡴࡶࡵࠪ⒙"): getattr(result, bstack11ll1_opy_ (u"ࠫࡴࡻࡴࡤࡱࡰࡩࠬ⒚"), bstack11ll1_opy_ (u"ࠬ࠭⒛"))}
def bstack1lll11ll1l11_opy_(test, bstack1111ll1l11_opy_, bstack1l1l11lll1_opy_, result=None, call=None, outcome=None, bstack1lll1l111ll1_opy_=None):
    logger.debug(bstack11ll1_opy_ (u"࠭ࡳࡦࡰࡧࡣ࡭ࡵ࡯࡬ࡡࡵࡹࡳࡥࡥࡷࡧࡱࡸ࠿ࠦࡁࡵࡶࡨࡱࡵࡺࡩ࡯ࡩࠣࡸࡴࠦࡧࡦࡰࡨࡶࡦࡺࡥࠡࡪࡲࡳࡰࠦࡤࡢࡶࡤ࠰ࠥ࡫ࡶࡦࡰࡷࡘࡾࡶࡥࠡ࠯ࠣࡿࢂ࠭⒜").format(bstack1l1l11lll1_opy_))
    hook_data = bstack1lll11l1llll_opy_(test, bstack1111ll1l11_opy_, bstack1l1l11lll1_opy_, result, call, outcome, bstack1lll1l111ll1_opy_)
    bstack1111l1llll_opy_ = {
        bstack11ll1_opy_ (u"ࠧࡦࡸࡨࡲࡹࡥࡴࡺࡲࡨࠫ⒝"): bstack1l1l11lll1_opy_,
        bstack11ll1_opy_ (u"ࠨࡪࡲࡳࡰࡥࡲࡶࡰࠪ⒞"): hook_data
    }
    bstack11lll11l11_opy_.bstack1lll1llll_opy_(bstack1111l1llll_opy_)
def bstack1111llllll_opy_(bstack1111ll1l11_opy_):
    if not bstack1111ll1l11_opy_:
        return None
    if bstack1111ll1l11_opy_.get(bstack11ll1_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡥࡣࡷࡥࠬ⒟"), None):
        return getattr(bstack1111ll1l11_opy_[bstack11ll1_opy_ (u"ࠪࡸࡪࡹࡴࡠࡦࡤࡸࡦ࠭⒠")], bstack11ll1_opy_ (u"ࠫࡺࡻࡩࡥࠩ⒡"), None)
    return bstack1111ll1l11_opy_.get(bstack11ll1_opy_ (u"ࠬࡻࡵࡪࡦࠪ⒢"), None)
@pytest.fixture(autouse=True)
def second_fixture(caplog, request):
    if cli.is_running():
        cli.test_framework.track_event(cli_context, bstack1llll1ll111_opy_.LOG, bstack1lll1111l11_opy_.PRE, request, caplog)
    yield
    if cli.is_running():
        cli.test_framework.track_event(cli_context, bstack1llll1ll111_opy_.LOG, bstack1lll1111l11_opy_.POST, request, caplog)
        return # skip all existing operations
    try:
        if not bstack11lll11l11_opy_.on():
            return
        places = [bstack11ll1_opy_ (u"࠭ࡳࡦࡶࡸࡴࠬ⒣"), bstack11ll1_opy_ (u"ࠧࡤࡣ࡯ࡰࠬ⒤"), bstack11ll1_opy_ (u"ࠨࡶࡨࡥࡷࡪ࡯ࡸࡰࠪ⒥")]
        logs = []
        for bstack1lll11llllll_opy_ in places:
            records = caplog.get_records(bstack1lll11llllll_opy_)
            bstack1lll11ll11ll_opy_ = bstack11ll1_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡳࡷࡱࡣࡺࡻࡩࡥࠩ⒦") if bstack1lll11llllll_opy_ == bstack11ll1_opy_ (u"ࠪࡧࡦࡲ࡬ࠨ⒧") else bstack11ll1_opy_ (u"ࠫ࡭ࡵ࡯࡬ࡡࡵࡹࡳࡥࡵࡶ࡫ࡧࠫ⒨")
            bstack1lll1l11l1l1_opy_ = request.node.nodeid + (bstack11ll1_opy_ (u"ࠬ࠭⒩") if bstack1lll11llllll_opy_ == bstack11ll1_opy_ (u"࠭ࡣࡢ࡮࡯ࠫ⒪") else bstack11ll1_opy_ (u"ࠧ࠮ࠩ⒫") + bstack1lll11llllll_opy_)
            test_uuid = bstack1111llllll_opy_(_1111l1ll1l_opy_.get(bstack1lll1l11l1l1_opy_, None))
            if not test_uuid:
                continue
            for record in records:
                if bstack11l11111l11_opy_(record.message):
                    continue
                logs.append({
                    bstack11ll1_opy_ (u"ࠨࡶ࡬ࡱࡪࡹࡴࡢ࡯ࡳࠫ⒬"): bstack111l1ll111l_opy_(record.created).isoformat() + bstack11ll1_opy_ (u"ࠩ࡝ࠫ⒭"),
                    bstack11ll1_opy_ (u"ࠪࡰࡪࡼࡥ࡭ࠩ⒮"): record.levelname,
                    bstack11ll1_opy_ (u"ࠫࡲ࡫ࡳࡴࡣࡪࡩࠬ⒯"): record.message,
                    bstack1lll11ll11ll_opy_: test_uuid
                })
        if len(logs) > 0:
            bstack11lll11l11_opy_.bstack1l1l11l11l_opy_(logs)
    except Exception as err:
        print(bstack11ll1_opy_ (u"ࠬࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡ࡫ࡱࠤࡸ࡫ࡣࡰࡰࡧࡣ࡫࡯ࡸࡵࡷࡵࡩ࠿ࠦࡻࡾࠩ⒰"), str(err))
def bstack1l1ll111_opy_(sequence, driver_command, response=None, driver = None, args = None):
    global bstack1lll11lll1_opy_
    bstack11llll1111_opy_ = bstack1lll11l1l_opy_(threading.current_thread(), bstack11ll1_opy_ (u"࠭ࡩࡴࡃ࠴࠵ࡾ࡚ࡥࡴࡶࠪ⒱"), None) and bstack1lll11l1l_opy_(
            threading.current_thread(), bstack11ll1_opy_ (u"ࠧࡢ࠳࠴ࡽࡕࡲࡡࡵࡨࡲࡶࡲ࠭⒲"), None)
    bstack111lll11_opy_ = getattr(driver, bstack11ll1_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫ࡂ࠳࠴ࡽࡘ࡮࡯ࡶ࡮ࡧࡗࡨࡧ࡮ࠨ⒳"), None) != None and getattr(driver, bstack11ll1_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬ࡃ࠴࠵ࡾ࡙ࡨࡰࡷ࡯ࡨࡘࡩࡡ࡯ࠩ⒴"), None) == True
    if sequence == bstack11ll1_opy_ (u"ࠪࡦࡪ࡬࡯ࡳࡧࠪ⒵") and driver != None:
      if not bstack1lll11lll1_opy_ and bstack1ll111l11l1_opy_() and bstack11ll1_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠫⒶ") in CONFIG and CONFIG[bstack11ll1_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠬⒷ")] == True and bstack1l11l111l1_opy_.bstack1ll1l1111l_opy_(driver_command) and (bstack111lll11_opy_ or bstack11llll1111_opy_) and not bstack11l11ll1ll_opy_(args):
        try:
          bstack1lll11lll1_opy_ = True
          logger.debug(bstack11ll1_opy_ (u"࠭ࡐࡦࡴࡩࡳࡷࡳࡩ࡯ࡩࠣࡷࡨࡧ࡮ࠡࡨࡲࡶࠥࢁࡽࠨⒸ").format(driver_command))
          logger.debug(perform_scan(driver, driver_command=driver_command))
        except Exception as err:
          logger.debug(bstack11ll1_opy_ (u"ࠧࡇࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡴࡪࡸࡦࡰࡴࡰࠤࡸࡩࡡ࡯ࠢࡾࢁࠬⒹ").format(str(err)))
        bstack1lll11lll1_opy_ = False
    if sequence == bstack11ll1_opy_ (u"ࠨࡣࡩࡸࡪࡸࠧⒺ"):
        if driver_command == bstack11ll1_opy_ (u"ࠩࡶࡧࡷ࡫ࡥ࡯ࡵ࡫ࡳࡹ࠭Ⓕ"):
            bstack11lll11l11_opy_.bstack1l1lll1ll_opy_({
                bstack11ll1_opy_ (u"ࠪ࡭ࡲࡧࡧࡦࠩⒼ"): response[bstack11ll1_opy_ (u"ࠫࡻࡧ࡬ࡶࡧࠪⒽ")],
                bstack11ll1_opy_ (u"ࠬࡺࡥࡴࡶࡢࡶࡺࡴ࡟ࡶࡷ࡬ࡨࠬⒾ"): store[bstack11ll1_opy_ (u"࠭ࡣࡶࡴࡵࡩࡳࡺ࡟ࡵࡧࡶࡸࡤࡻࡵࡪࡦࠪⒿ")]
            })
def bstack1l1l1ll1ll_opy_():
    global bstack1lll111ll_opy_
    bstack111lll1l1_opy_.bstack11l111ll11_opy_()
    logging.shutdown()
    bstack11lll11l11_opy_.bstack1111l1l1l1_opy_()
    for driver in bstack1lll111ll_opy_:
        try:
            driver.quit()
        except Exception as e:
            pass
def bstack1lll11lll11l_opy_(*args):
    global bstack1lll111ll_opy_
    bstack11lll11l11_opy_.bstack1111l1l1l1_opy_()
    for driver in bstack1lll111ll_opy_:
        try:
            driver.quit()
        except Exception as e:
            pass
@measure(event_name=EVENTS.bstack111lll111l_opy_, stage=STAGE.bstack11l1llll1_opy_, bstack1lll1l1l1_opy_=bstack1ll1l11111_opy_)
def bstack111111ll1_opy_(self, *args, **kwargs):
    bstack1111ll111_opy_ = bstack1lll1l1l_opy_(self, *args, **kwargs)
    bstack1ll1111ll1_opy_ = getattr(threading.current_thread(), bstack11ll1_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱࡔࡦࡵࡷࡑࡪࡺࡡࠨⓀ"), None)
    if bstack1ll1111ll1_opy_ and bstack1ll1111ll1_opy_.get(bstack11ll1_opy_ (u"ࠨࡵࡷࡥࡹࡻࡳࠨⓁ"), bstack11ll1_opy_ (u"ࠩࠪⓂ")) == bstack11ll1_opy_ (u"ࠪࡴࡪࡴࡤࡪࡰࡪࠫⓃ"):
        bstack11lll11l11_opy_.bstack1ll1lll111_opy_(self)
    return bstack1111ll111_opy_
@measure(event_name=EVENTS.bstack1ll111111l_opy_, stage=STAGE.bstack11l11ll11l_opy_, bstack1lll1l1l1_opy_=bstack1ll1l11111_opy_)
def bstack1111l1111_opy_(framework_name):
    from bstack_utils.config import Config
    bstack1l1l1ll1l_opy_ = Config.bstack1l1l1111_opy_()
    if bstack1l1l1ll1l_opy_.get_property(bstack11ll1_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮ࡣࡲࡵࡤࡠࡥࡤࡰࡱ࡫ࡤࠨⓄ")):
        return
    bstack1l1l1ll1l_opy_.bstack11l1l11l_opy_(bstack11ll1_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯ࡤࡳ࡯ࡥࡡࡦࡥࡱࡲࡥࡥࠩⓅ"), True)
    global bstack11l1l11ll_opy_
    global bstack1lll1ll1_opy_
    bstack11l1l11ll_opy_ = framework_name
    logger.info(bstack1ll1111l11_opy_.format(bstack11l1l11ll_opy_.split(bstack11ll1_opy_ (u"࠭࠭ࠨⓆ"))[0]))
    try:
        from selenium import webdriver
        from selenium.webdriver.common.service import Service
        from selenium.webdriver.remote.webdriver import WebDriver
        if bstack1ll111l11l1_opy_():
            Service.start = bstack1l1l1ll111_opy_
            Service.stop = bstack1l1lllll1_opy_
            webdriver.Remote.get = bstack11lll1111_opy_
            webdriver.Remote.__init__ = bstack1l111111l1_opy_
            if not isinstance(os.getenv(bstack11ll1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡐ࡚ࡖࡈࡗ࡙ࡥࡐࡂࡔࡄࡐࡑࡋࡌࠨⓇ")), str):
                return
            WebDriver.quit = bstack1l1l111l1_opy_
            WebDriver.getAccessibilityResults = getAccessibilityResults
            WebDriver.get_accessibility_results = getAccessibilityResults
            WebDriver.getAccessibilityResultsSummary = getAccessibilityResultsSummary
            WebDriver.get_accessibility_results_summary = getAccessibilityResultsSummary
            WebDriver.performScan = perform_scan
            WebDriver.perform_scan = perform_scan
        elif bstack11lll11l11_opy_.on():
            webdriver.Remote.__init__ = bstack111111ll1_opy_
        bstack1lll1ll1_opy_ = True
    except Exception as e:
        pass
    if os.environ.get(bstack11ll1_opy_ (u"ࠨࡕࡈࡐࡊࡔࡉࡖࡏࡢࡓࡗࡥࡐࡍࡃ࡜࡛ࡗࡏࡇࡉࡖࡢࡍࡓ࡙ࡔࡂࡎࡏࡉࡉ࠭Ⓢ")):
        bstack1lll1ll1_opy_ = eval(os.environ.get(bstack11ll1_opy_ (u"ࠩࡖࡉࡑࡋࡎࡊࡗࡐࡣࡔࡘ࡟ࡑࡎࡄ࡝࡜ࡘࡉࡈࡊࡗࡣࡎࡔࡓࡕࡃࡏࡐࡊࡊࠧⓉ")))
    if not bstack1lll1ll1_opy_:
        bstack1ll1l1l111_opy_(bstack11ll1_opy_ (u"ࠥࡔࡦࡩ࡫ࡢࡩࡨࡷࠥࡴ࡯ࡵࠢ࡬ࡲࡸࡺࡡ࡭࡮ࡨࡨࠧⓊ"), bstack1llll11l_opy_)
    if bstack1111l111_opy_():
        try:
            from selenium.webdriver.remote.remote_connection import RemoteConnection
            if hasattr(RemoteConnection, bstack11ll1_opy_ (u"ࠫࡤ࡭ࡥࡵࡡࡳࡶࡴࡾࡹࡠࡷࡵࡰࠬⓋ")) and callable(getattr(RemoteConnection, bstack11ll1_opy_ (u"ࠬࡥࡧࡦࡶࡢࡴࡷࡵࡸࡺࡡࡸࡶࡱ࠭Ⓦ"))):
                RemoteConnection._get_proxy_url = bstack11l1ll1ll_opy_
            else:
                from selenium.webdriver.remote.client_config import ClientConfig
                ClientConfig.get_proxy_url = bstack11l1ll1ll_opy_
        except Exception as e:
            logger.error(bstack1l1llllll1_opy_.format(str(e)))
    if bstack11ll1_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹ࠭Ⓧ") in str(framework_name).lower():
        if not bstack1ll111l11l1_opy_():
            return
        try:
            from pytest_selenium import pytest_selenium
            from _pytest.config import Config
            pytest_selenium.pytest_report_header = bstack1l111lll11_opy_
            from pytest_selenium.drivers import browserstack
            browserstack.pytest_selenium_runtest_makereport = bstack1ll1l1ll_opy_
            Config.getoption = bstack1ll1ll1lll_opy_
        except Exception as e:
            pass
        try:
            from pytest_bdd import reporting
            reporting.runtest_makereport = bstack111l111l_opy_
        except Exception as e:
            pass
@measure(event_name=EVENTS.bstack1lll111l1_opy_, stage=STAGE.bstack11l1llll1_opy_, bstack1lll1l1l1_opy_=bstack1ll1l11111_opy_)
def bstack1l1l111l1_opy_(self):
    global bstack11l1l11ll_opy_
    global bstack1l111l111l_opy_
    global bstack1llll1lll1_opy_
    try:
        if bstack11ll1_opy_ (u"ࠧࡱࡻࡷࡩࡸࡺࠧⓎ") in bstack11l1l11ll_opy_ and self.session_id != None and bstack1lll11l1l_opy_(threading.current_thread(), bstack11ll1_opy_ (u"ࠨࡶࡨࡷࡹ࡙ࡴࡢࡶࡸࡷࠬⓏ"), bstack11ll1_opy_ (u"ࠩࠪⓐ")) != bstack11ll1_opy_ (u"ࠪࡷࡰ࡯ࡰࡱࡧࡧࠫⓑ"):
            bstack11ll1ll1_opy_ = bstack11ll1_opy_ (u"ࠫࡵࡧࡳࡴࡧࡧࠫⓒ") if len(threading.current_thread().bstackTestErrorMessages) == 0 else bstack11ll1_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡨࡨࠬⓓ")
            bstack11l111l1ll_opy_(logger, True)
            if os.environ.get(bstack11ll1_opy_ (u"࠭ࡐ࡚ࡖࡈࡗ࡙ࡥࡔࡆࡕࡗࡣࡓࡇࡍࡆࠩⓔ"), None):
                self.execute_script(
                    bstack11ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡥࡹࡧࡦࡹࡹࡵࡲ࠻ࠢࡾࠦࡦࡩࡴࡪࡱࡱࠦ࠿ࠦࠢࡴࡧࡷࡗࡪࡹࡳࡪࡱࡱࡒࡦࡳࡥࠣ࠮ࠣࠦࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠢ࠻ࠢࡾࠦࡳࡧ࡭ࡦࠤ࠽ࠤࠬⓕ") + json.dumps(
                        os.environ.get(bstack11ll1_opy_ (u"ࠨࡒ࡜ࡘࡊ࡙ࡔࡠࡖࡈࡗ࡙ࡥࡎࡂࡏࡈࠫⓖ"))) + bstack11ll1_opy_ (u"ࠩࢀࢁࠬⓗ"))
            if self != None:
                bstack1ll11ll1ll_opy_(self, bstack11ll1ll1_opy_, bstack11ll1_opy_ (u"ࠪ࠰ࠥ࠭ⓘ").join(threading.current_thread().bstackTestErrorMessages))
        if not cli.bstack1l11lll111l_opy_(bstack1l1ll11ll11_opy_):
            item = store.get(bstack11ll1_opy_ (u"ࠫࡨࡻࡲࡳࡧࡱࡸࡤࡺࡥࡴࡶࡢ࡭ࡹ࡫࡭ࠨⓙ"), None)
            if item is not None and bstack1lll11l1l_opy_(threading.current_thread(), bstack11ll1_opy_ (u"ࠬࡧ࠱࠲ࡻࡓࡰࡦࡺࡦࡰࡴࡰࠫⓚ"), None):
                bstack1lll1l11ll_opy_.bstack1l1lllll1l_opy_(self, bstack1l11l11ll_opy_, logger, item)
        threading.current_thread().testStatus = bstack11ll1_opy_ (u"࠭ࠧⓛ")
    except Exception as e:
        logger.debug(bstack11ll1_opy_ (u"ࠢࡆࡴࡵࡳࡷࠦࡷࡩ࡫࡯ࡩࠥࡳࡡࡳ࡭࡬ࡲ࡬ࠦࡳࡵࡣࡷࡹࡸࡀࠠࠣⓜ") + str(e))
    bstack1llll1lll1_opy_(self)
    self.session_id = None
@measure(event_name=EVENTS.bstack11llllll_opy_, stage=STAGE.bstack11l1llll1_opy_, bstack1lll1l1l1_opy_=bstack1ll1l11111_opy_)
def bstack1l111111l1_opy_(self, command_executor,
             desired_capabilities=None, browser_profile=None, proxy=None,
             keep_alive=True, file_detector=None, options=None):
    global CONFIG
    global bstack1l111l111l_opy_
    global bstack1ll1l11111_opy_
    global bstack1ll1lll1l1_opy_
    global bstack11l1l11ll_opy_
    global bstack1lll1l1l_opy_
    global bstack1lll111ll_opy_
    global bstack1l1ll11ll1_opy_
    global bstack11ll1l11l1_opy_
    global bstack1l11l11ll_opy_
    CONFIG[bstack11ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡓࡅࡍࠪⓝ")] = str(bstack11l1l11ll_opy_) + str(__version__)
    command_executor = bstack1l1l11l11_opy_(bstack1l1ll11ll1_opy_, CONFIG)
    logger.debug(bstack11lll111ll_opy_.format(command_executor))
    proxy = bstack11l1l11ll1_opy_(CONFIG, proxy)
    bstack1l11ll11ll_opy_ = 0
    try:
        if bstack1ll1lll1l1_opy_ is True:
            bstack1l11ll11ll_opy_ = int(os.environ.get(bstack11ll1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡒࡏࡅ࡙ࡌࡏࡓࡏࡢࡍࡓࡊࡅ࡙ࠩⓞ")))
    except:
        bstack1l11ll11ll_opy_ = 0
    bstack1l111ll11_opy_ = bstack11l1llll1l_opy_(CONFIG, bstack1l11ll11ll_opy_)
    logger.debug(bstack11l1l1l1ll_opy_.format(str(bstack1l111ll11_opy_)))
    bstack1l11l11ll_opy_ = CONFIG.get(bstack11ll1_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ⓟ"))[bstack1l11ll11ll_opy_]
    if bstack11ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡏࡳࡨࡧ࡬ࠨⓠ") in CONFIG and CONFIG[bstack11ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࠩⓡ")]:
        bstack1l111ll1l1_opy_(bstack1l111ll11_opy_, bstack11ll1l11l1_opy_)
    if bstack1l1ll11l1l_opy_.bstack1ll11l1ll1_opy_(CONFIG, bstack1l11ll11ll_opy_) and bstack1l1ll11l1l_opy_.bstack11l1lll1_opy_(bstack1l111ll11_opy_, options, desired_capabilities):
        threading.current_thread().a11yPlatform = True
        if not cli.bstack1l11lll111l_opy_(bstack1l1ll11ll11_opy_):
            bstack1l1ll11l1l_opy_.set_capabilities(bstack1l111ll11_opy_, CONFIG)
    if desired_capabilities:
        bstack1ll1lll1ll_opy_ = bstack1l1ll111l_opy_(desired_capabilities)
        bstack1ll1lll1ll_opy_[bstack11ll1_opy_ (u"࠭ࡵࡴࡧ࡚࠷ࡈ࠭ⓢ")] = bstack11lll11lll_opy_(CONFIG)
        bstack11l1lll1ll_opy_ = bstack11l1llll1l_opy_(bstack1ll1lll1ll_opy_)
        if bstack11l1lll1ll_opy_:
            bstack1l111ll11_opy_ = update(bstack11l1lll1ll_opy_, bstack1l111ll11_opy_)
        desired_capabilities = None
    if options:
        bstack11lll1l1_opy_(options, bstack1l111ll11_opy_)
    if not options:
        options = bstack111lll1ll_opy_(bstack1l111ll11_opy_)
    if proxy and bstack1ll1ll1l11_opy_() >= version.parse(bstack11ll1_opy_ (u"ࠧ࠵࠰࠴࠴࠳࠶ࠧⓣ")):
        options.proxy(proxy)
    if options and bstack1ll1ll1l11_opy_() >= version.parse(bstack11ll1_opy_ (u"ࠨ࠵࠱࠼࠳࠶ࠧⓤ")):
        desired_capabilities = None
    if (
            not options and not desired_capabilities
    ) or (
            bstack1ll1ll1l11_opy_() < version.parse(bstack11ll1_opy_ (u"ࠩ࠶࠲࠽࠴࠰ࠨⓥ")) and not desired_capabilities
    ):
        desired_capabilities = {}
        desired_capabilities.update(bstack1l111ll11_opy_)
    logger.info(bstack1llll1111_opy_)
    bstack11l11l11ll_opy_.end(EVENTS.bstack1ll111111l_opy_.value, EVENTS.bstack1ll111111l_opy_.value + bstack11ll1_opy_ (u"ࠥ࠾ࡸࡺࡡࡳࡶࠥⓦ"),
                               EVENTS.bstack1ll111111l_opy_.value + bstack11ll1_opy_ (u"ࠦ࠿࡫࡮ࡥࠤⓧ"), True, None)
    try:
        if bstack1ll1ll1l11_opy_() >= version.parse(bstack11ll1_opy_ (u"ࠬ࠺࠮࠲࠲࠱࠴ࠬⓨ")):
            bstack1lll1l1l_opy_(self, command_executor=command_executor,
                      options=options, keep_alive=keep_alive, file_detector=file_detector, *args, **kwargs)
        elif bstack1ll1ll1l11_opy_() >= version.parse(bstack11ll1_opy_ (u"࠭࠳࠯࠺࠱࠴ࠬⓩ")):
            bstack1lll1l1l_opy_(self, command_executor=command_executor,
                      desired_capabilities=desired_capabilities, options=options,
                      browser_profile=browser_profile, proxy=proxy,
                      keep_alive=keep_alive, file_detector=file_detector)
        elif bstack1ll1ll1l11_opy_() >= version.parse(bstack11ll1_opy_ (u"ࠧ࠳࠰࠸࠷࠳࠶ࠧ⓪")):
            bstack1lll1l1l_opy_(self, command_executor=command_executor,
                      desired_capabilities=desired_capabilities,
                      browser_profile=browser_profile, proxy=proxy,
                      keep_alive=keep_alive, file_detector=file_detector)
        else:
            bstack1lll1l1l_opy_(self, command_executor=command_executor,
                      desired_capabilities=desired_capabilities,
                      browser_profile=browser_profile, proxy=proxy,
                      keep_alive=keep_alive)
    except Exception as bstack11l111lll1_opy_:
        logger.error(bstack11l111l1l_opy_.format(bstack11ll1_opy_ (u"ࠨࡄࡵࡳࡼࡹࡥࡳࡕࡷࡥࡨࡱࠧ⓫"), str(bstack11l111lll1_opy_)))
        raise bstack11l111lll1_opy_
    try:
        bstack111lll1111_opy_ = bstack11ll1_opy_ (u"ࠩࠪ⓬")
        if bstack1ll1ll1l11_opy_() >= version.parse(bstack11ll1_opy_ (u"ࠪ࠸࠳࠶࠮࠱ࡤ࠴ࠫ⓭")):
            bstack111lll1111_opy_ = self.caps.get(bstack11ll1_opy_ (u"ࠦࡴࡶࡴࡪ࡯ࡤࡰࡍࡻࡢࡖࡴ࡯ࠦ⓮"))
        else:
            bstack111lll1111_opy_ = self.capabilities.get(bstack11ll1_opy_ (u"ࠧࡵࡰࡵ࡫ࡰࡥࡱࡎࡵࡣࡗࡵࡰࠧ⓯"))
        if bstack111lll1111_opy_:
            bstack1l1ll111l1_opy_(bstack111lll1111_opy_)
            if bstack1ll1ll1l11_opy_() <= version.parse(bstack11ll1_opy_ (u"࠭࠳࠯࠳࠶࠲࠵࠭⓰")):
                self.command_executor._url = bstack11ll1_opy_ (u"ࠢࡩࡶࡷࡴ࠿࠵࠯ࠣ⓱") + bstack1l1ll11ll1_opy_ + bstack11ll1_opy_ (u"ࠣ࠼࠻࠴࠴ࡽࡤ࠰ࡪࡸࡦࠧ⓲")
            else:
                self.command_executor._url = bstack11ll1_opy_ (u"ࠤ࡫ࡸࡹࡶࡳ࠻࠱࠲ࠦ⓳") + bstack111lll1111_opy_ + bstack11ll1_opy_ (u"ࠥ࠳ࡼࡪ࠯ࡩࡷࡥࠦ⓴")
            logger.debug(bstack1l1111lll1_opy_.format(bstack111lll1111_opy_))
        else:
            logger.debug(bstack1lllll11_opy_.format(bstack11ll1_opy_ (u"ࠦࡔࡶࡴࡪ࡯ࡤࡰࠥࡎࡵࡣࠢࡱࡳࡹࠦࡦࡰࡷࡱࡨࠧ⓵")))
    except Exception as e:
        logger.debug(bstack1lllll11_opy_.format(e))
    bstack1l111l111l_opy_ = self.session_id
    if bstack11ll1_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸࠬ⓶") in bstack11l1l11ll_opy_:
        threading.current_thread().bstackSessionId = self.session_id
        threading.current_thread().bstackSessionDriver = self
        threading.current_thread().bstackTestErrorMessages = []
        item = store.get(bstack11ll1_opy_ (u"࠭ࡣࡶࡴࡵࡩࡳࡺ࡟ࡵࡧࡶࡸࡤ࡯ࡴࡦ࡯ࠪ⓷"), None)
        if item:
            bstack1lll1l11l1ll_opy_ = getattr(item, bstack11ll1_opy_ (u"ࠧࡠࡶࡨࡷࡹࡥࡣࡢࡵࡨࡣࡸࡺࡡࡳࡶࡨࡨࠬ⓸"), False)
            if not getattr(item, bstack11ll1_opy_ (u"ࠨࡡࡧࡶ࡮ࡼࡥࡳࠩ⓹"), None) and bstack1lll1l11l1ll_opy_:
                setattr(store[bstack11ll1_opy_ (u"ࠩࡦࡹࡷࡸࡥ࡯ࡶࡢࡸࡪࡹࡴࡠ࡫ࡷࡩࡲ࠭⓺")], bstack11ll1_opy_ (u"ࠪࡣࡩࡸࡩࡷࡧࡵࠫ⓻"), self)
        bstack1ll1111ll1_opy_ = getattr(threading.current_thread(), bstack11ll1_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮ࡘࡪࡹࡴࡎࡧࡷࡥࠬ⓼"), None)
        if bstack1ll1111ll1_opy_ and bstack1ll1111ll1_opy_.get(bstack11ll1_opy_ (u"ࠬࡹࡴࡢࡶࡸࡷࠬ⓽"), bstack11ll1_opy_ (u"࠭ࠧ⓾")) == bstack11ll1_opy_ (u"ࠧࡱࡧࡱࡨ࡮ࡴࡧࠨ⓿"):
            bstack11lll11l11_opy_.bstack1ll1lll111_opy_(self)
    bstack1lll111ll_opy_.append(self)
    if bstack11ll1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫ─") in CONFIG and bstack11ll1_opy_ (u"ࠩࡶࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠧ━") in CONFIG[bstack11ll1_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭│")][bstack1l11ll11ll_opy_]:
        bstack1ll1l11111_opy_ = CONFIG[bstack11ll1_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧ┃")][bstack1l11ll11ll_opy_][bstack11ll1_opy_ (u"ࠬࡹࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧࠪ┄")]
    logger.debug(bstack1l111l11l1_opy_.format(bstack1l111l111l_opy_))
@measure(event_name=EVENTS.bstack11llllll11_opy_, stage=STAGE.bstack11l1llll1_opy_, bstack1lll1l1l1_opy_=bstack1ll1l11111_opy_)
def bstack11lll1111_opy_(self, url):
    global bstack1llll1llll_opy_
    global CONFIG
    try:
        bstack11ll1ll1ll_opy_(url, CONFIG, logger)
    except Exception as err:
        logger.debug(bstack1l1ll11l1_opy_.format(str(err)))
    try:
        bstack1llll1llll_opy_(self, url)
    except Exception as e:
        try:
            bstack1ll111l1ll_opy_ = str(e)
            if any(err_msg in bstack1ll111l1ll_opy_ for err_msg in bstack1ll11l11l_opy_):
                bstack11ll1ll1ll_opy_(url, CONFIG, logger, True)
        except Exception as err:
            logger.debug(bstack1l1ll11l1_opy_.format(str(err)))
        raise e
def bstack11ll11l1l_opy_(item, when):
    global bstack1l111l11l_opy_
    try:
        bstack1l111l11l_opy_(item, when)
    except Exception as e:
        pass
def bstack111l111l_opy_(item, call, rep):
    global bstack1l11l11ll1_opy_
    global bstack1lll111ll_opy_
    name = bstack11ll1_opy_ (u"࠭ࠧ┅")
    try:
        if rep.when == bstack11ll1_opy_ (u"ࠧࡤࡣ࡯ࡰࠬ┆"):
            bstack1l111l111l_opy_ = threading.current_thread().bstackSessionId
            skipSessionName = item.config.getoption(bstack11ll1_opy_ (u"ࠨࡵ࡮࡭ࡵ࡙ࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧࠪ┇"))
            try:
                if (str(skipSessionName).lower() != bstack11ll1_opy_ (u"ࠩࡷࡶࡺ࡫ࠧ┈")):
                    name = str(rep.nodeid)
                    bstack1l1l1l11ll_opy_ = bstack1l111l1l_opy_(bstack11ll1_opy_ (u"ࠪࡷࡪࡺࡓࡦࡵࡶ࡭ࡴࡴࡎࡢ࡯ࡨࠫ┉"), name, bstack11ll1_opy_ (u"ࠫࠬ┊"), bstack11ll1_opy_ (u"ࠬ࠭┋"), bstack11ll1_opy_ (u"࠭ࠧ┌"), bstack11ll1_opy_ (u"ࠧࠨ┍"))
                    os.environ[bstack11ll1_opy_ (u"ࠨࡒ࡜ࡘࡊ࡙ࡔࡠࡖࡈࡗ࡙ࡥࡎࡂࡏࡈࠫ┎")] = name
                    for driver in bstack1lll111ll_opy_:
                        if bstack1l111l111l_opy_ == driver.session_id:
                            driver.execute_script(bstack1l1l1l11ll_opy_)
            except Exception as e:
                logger.debug(bstack11ll1_opy_ (u"ࠩࡈࡶࡷࡵࡲࠡ࡫ࡱࠤࡸ࡫ࡴࡵ࡫ࡱ࡫ࠥࡹࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧࠣࡪࡴࡸࠠࡱࡻࡷࡩࡸࡺ࠭ࡣࡦࡧࠤࡸ࡫ࡳࡴ࡫ࡲࡲ࠿ࠦࡻࡾࠩ┏").format(str(e)))
            try:
                bstack1l11ll1111_opy_(rep.outcome.lower())
                if rep.outcome.lower() != bstack11ll1_opy_ (u"ࠪࡷࡰ࡯ࡰࡱࡧࡧࠫ┐"):
                    status = bstack11ll1_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡧࡧࠫ┑") if rep.outcome.lower() == bstack11ll1_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡨࡨࠬ┒") else bstack11ll1_opy_ (u"࠭ࡰࡢࡵࡶࡩࡩ࠭┓")
                    reason = bstack11ll1_opy_ (u"ࠧࠨ└")
                    if status == bstack11ll1_opy_ (u"ࠨࡨࡤ࡭ࡱ࡫ࡤࠨ┕"):
                        reason = rep.longrepr.reprcrash.message
                        if (not threading.current_thread().bstackTestErrorMessages):
                            threading.current_thread().bstackTestErrorMessages = []
                        threading.current_thread().bstackTestErrorMessages.append(reason)
                    level = bstack11ll1_opy_ (u"ࠩ࡬ࡲ࡫ࡵࠧ┖") if status == bstack11ll1_opy_ (u"ࠪࡴࡦࡹࡳࡦࡦࠪ┗") else bstack11ll1_opy_ (u"ࠫࡪࡸࡲࡰࡴࠪ┘")
                    data = name + bstack11ll1_opy_ (u"ࠬࠦࡰࡢࡵࡶࡩࡩࠧࠧ┙") if status == bstack11ll1_opy_ (u"࠭ࡰࡢࡵࡶࡩࡩ࠭┚") else name + bstack11ll1_opy_ (u"ࠧࠡࡨࡤ࡭ࡱ࡫ࡤࠢࠢࠪ┛") + reason
                    bstack1llllll11_opy_ = bstack1l111l1l_opy_(bstack11ll1_opy_ (u"ࠨࡣࡱࡲࡴࡺࡡࡵࡧࠪ├"), bstack11ll1_opy_ (u"ࠩࠪ┝"), bstack11ll1_opy_ (u"ࠪࠫ┞"), bstack11ll1_opy_ (u"ࠫࠬ┟"), level, data)
                    for driver in bstack1lll111ll_opy_:
                        if bstack1l111l111l_opy_ == driver.session_id:
                            driver.execute_script(bstack1llllll11_opy_)
            except Exception as e:
                logger.debug(bstack11ll1_opy_ (u"ࠬࡋࡲࡳࡱࡵࠤ࡮ࡴࠠࡴࡧࡷࡸ࡮ࡴࡧࠡࡵࡨࡷࡸ࡯࡯࡯ࠢࡦࡳࡳࡺࡥࡹࡶࠣࡪࡴࡸࠠࡱࡻࡷࡩࡸࡺ࠭ࡣࡦࡧࠤࡸ࡫ࡳࡴ࡫ࡲࡲ࠿ࠦࡻࡾࠩ┠").format(str(e)))
    except Exception as e:
        logger.debug(bstack11ll1_opy_ (u"࠭ࡅࡳࡴࡲࡶࠥ࡯࡮ࠡࡩࡨࡸࡹ࡯࡮ࡨࠢࡶࡸࡦࡺࡥࠡ࡫ࡱࠤࡵࡿࡴࡦࡵࡷ࠱ࡧࡪࡤࠡࡶࡨࡷࡹࠦࡳࡵࡣࡷࡹࡸࡀࠠࡼࡿࠪ┡").format(str(e)))
    bstack1l11l11ll1_opy_(item, call, rep)
notset = Notset()
def bstack1ll1ll1lll_opy_(self, name: str, default=notset, skip: bool = False):
    global bstack1ll111ll_opy_
    if str(name).lower() == bstack11ll1_opy_ (u"ࠧࡥࡴ࡬ࡺࡪࡸࠧ┢"):
        return bstack11ll1_opy_ (u"ࠣࡄࡵࡳࡼࡹࡥࡳࡕࡷࡥࡨࡱࠢ┣")
    else:
        return bstack1ll111ll_opy_(self, name, default, skip)
def bstack11l1ll1ll_opy_(self):
    global CONFIG
    global bstack1ll1l11l1_opy_
    try:
        proxy = bstack11l1ll11l_opy_(CONFIG)
        if proxy:
            if proxy.endswith(bstack11ll1_opy_ (u"ࠩ࠱ࡴࡦࡩࠧ┤")):
                proxies = bstack111lllll1l_opy_(proxy, bstack1l1l11l11_opy_())
                if len(proxies) > 0:
                    protocol, bstack11l11lll_opy_ = proxies.popitem()
                    if bstack11ll1_opy_ (u"ࠥ࠾࠴࠵ࠢ┥") in bstack11l11lll_opy_:
                        return bstack11l11lll_opy_
                    else:
                        return bstack11ll1_opy_ (u"ࠦ࡭ࡺࡴࡱ࠼࠲࠳ࠧ┦") + bstack11l11lll_opy_
            else:
                return proxy
    except Exception as e:
        logger.error(bstack11ll1_opy_ (u"ࠧࡋࡲࡳࡱࡵࠤ࡮ࡴࠠࡴࡧࡷࡸ࡮ࡴࡧࠡࡲࡵࡳࡽࡿࠠࡶࡴ࡯ࠤ࠿ࠦࡻࡾࠤ┧").format(str(e)))
    return bstack1ll1l11l1_opy_(self)
def bstack1111l111_opy_():
    return (bstack11ll1_opy_ (u"࠭ࡨࡵࡶࡳࡔࡷࡵࡸࡺࠩ┨") in CONFIG or bstack11ll1_opy_ (u"ࠧࡩࡶࡷࡴࡸࡖࡲࡰࡺࡼࠫ┩") in CONFIG) and bstack1l11lll111_opy_() and bstack1ll1ll1l11_opy_() >= version.parse(
        bstack1llll1ll11_opy_)
def bstack1lll11lll_opy_(self,
               executablePath=None,
               channel=None,
               args=None,
               ignoreDefaultArgs=None,
               handleSIGINT=None,
               handleSIGTERM=None,
               handleSIGHUP=None,
               timeout=None,
               env=None,
               headless=None,
               devtools=None,
               proxy=None,
               downloadsPath=None,
               slowMo=None,
               tracesDir=None,
               chromiumSandbox=None,
               firefoxUserPrefs=None
               ):
    global CONFIG
    global bstack1ll1l11111_opy_
    global bstack1ll1lll1l1_opy_
    global bstack11l1l11ll_opy_
    CONFIG[bstack11ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡓࡅࡍࠪ┪")] = str(bstack11l1l11ll_opy_) + str(__version__)
    bstack1l11ll11ll_opy_ = 0
    try:
        if bstack1ll1lll1l1_opy_ is True:
            bstack1l11ll11ll_opy_ = int(os.environ.get(bstack11ll1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡒࡏࡅ࡙ࡌࡏࡓࡏࡢࡍࡓࡊࡅ࡙ࠩ┫")))
    except:
        bstack1l11ll11ll_opy_ = 0
    CONFIG[bstack11ll1_opy_ (u"ࠥ࡭ࡸࡖ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵࠤ┬")] = True
    bstack1l111ll11_opy_ = bstack11l1llll1l_opy_(CONFIG, bstack1l11ll11ll_opy_)
    logger.debug(bstack11l1l1l1ll_opy_.format(str(bstack1l111ll11_opy_)))
    if CONFIG.get(bstack11ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡏࡳࡨࡧ࡬ࠨ┭")):
        bstack1l111ll1l1_opy_(bstack1l111ll11_opy_, bstack11ll1l11l1_opy_)
    if bstack11ll1_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨ┮") in CONFIG and bstack11ll1_opy_ (u"࠭ࡳࡦࡵࡶ࡭ࡴࡴࡎࡢ࡯ࡨࠫ┯") in CONFIG[bstack11ll1_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪ┰")][bstack1l11ll11ll_opy_]:
        bstack1ll1l11111_opy_ = CONFIG[bstack11ll1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫ┱")][bstack1l11ll11ll_opy_][bstack11ll1_opy_ (u"ࠩࡶࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠧ┲")]
    import urllib
    import json
    if bstack11ll1_opy_ (u"ࠪࡸࡺࡸࡢࡰࡕࡦࡥࡱ࡫ࠧ┳") in CONFIG and str(CONFIG[bstack11ll1_opy_ (u"ࠫࡹࡻࡲࡣࡱࡖࡧࡦࡲࡥࠨ┴")]).lower() != bstack11ll1_opy_ (u"ࠬ࡬ࡡ࡭ࡵࡨࠫ┵"):
        bstack1l1l1111ll_opy_ = bstack1l11lllll_opy_()
        bstack1l1ll1l111_opy_ = bstack1l1l1111ll_opy_ + urllib.parse.quote(json.dumps(bstack1l111ll11_opy_))
    else:
        bstack1l1ll1l111_opy_ = bstack11ll1_opy_ (u"࠭ࡷࡴࡵ࠽࠳࠴ࡩࡤࡱ࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡥࡲࡱ࠴ࡶ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵࡁࡦࡥࡵࡹ࠽ࠨ┶") + urllib.parse.quote(json.dumps(bstack1l111ll11_opy_))
    browser = self.connect(bstack1l1ll1l111_opy_)
    return browser
def bstack1l11lllll1_opy_():
    global bstack1lll1ll1_opy_
    global bstack11l1l11ll_opy_
    try:
        from playwright._impl._browser_type import BrowserType
        from bstack_utils.helper import bstack11ll1l1ll_opy_
        if not bstack1ll111l11l1_opy_():
            global bstack11l1llll11_opy_
            if not bstack11l1llll11_opy_:
                from bstack_utils.helper import bstack1l11l1l1_opy_, bstack11ll111ll1_opy_
                bstack11l1llll11_opy_ = bstack1l11l1l1_opy_()
                bstack11ll111ll1_opy_(bstack11l1l11ll_opy_)
            BrowserType.connect = bstack11ll1l1ll_opy_
            return
        BrowserType.launch = bstack1lll11lll_opy_
        bstack1lll1ll1_opy_ = True
    except Exception as e:
        pass
def bstack1lll1l111l1l_opy_():
    global CONFIG
    global bstack1l11l1l1ll_opy_
    global bstack1l1ll11ll1_opy_
    global bstack11ll1l11l1_opy_
    global bstack1ll1lll1l1_opy_
    global bstack1l1l1l11l_opy_
    CONFIG = json.loads(os.environ.get(bstack11ll1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡃࡐࡐࡉࡍࡌ࠭┷")))
    bstack1l11l1l1ll_opy_ = eval(os.environ.get(bstack11ll1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡊࡕࡢࡅࡕࡖ࡟ࡂࡗࡗࡓࡒࡇࡔࡆࠩ┸")))
    bstack1l1ll11ll1_opy_ = os.environ.get(bstack11ll1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡊࡘࡆࡤ࡛ࡒࡍࠩ┹"))
    bstack1l111ll1_opy_(CONFIG, bstack1l11l1l1ll_opy_)
    bstack1l1l1l11l_opy_ = bstack111lll1l1_opy_.configure_logger(CONFIG, bstack1l1l1l11l_opy_)
    if cli.bstack111l1l1l1_opy_():
        bstack1111l11l_opy_.invoke(bstack1l11111l1_opy_.CONNECT, bstack11llllll1l_opy_())
        cli_context.platform_index = int(os.environ.get(bstack11ll1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡓࡐࡆ࡚ࡆࡐࡔࡐࡣࡎࡔࡄࡆ࡚ࠪ┺"), bstack11ll1_opy_ (u"ࠫ࠵࠭┻")))
        cli.bstack1l1ll1l1l1l_opy_(cli_context.platform_index)
        cli.bstack1l1l1111111_opy_(bstack1l1l11l11_opy_(bstack1l1ll11ll1_opy_, CONFIG), cli_context.platform_index, bstack111lll1ll_opy_)
        cli.bstack1l1l11lll11_opy_()
        logger.debug(bstack11ll1_opy_ (u"ࠧࡉࡌࡊࠢ࡬ࡷࠥࡧࡣࡵ࡫ࡹࡩࠥ࡬࡯ࡳࠢࡳࡰࡦࡺࡦࡰࡴࡰࡣ࡮ࡴࡤࡦࡺࡀࠦ┼") + str(cli_context.platform_index) + bstack11ll1_opy_ (u"ࠨࠢ┽"))
        return # skip all existing operations
    global bstack1lll1l1l_opy_
    global bstack1llll1lll1_opy_
    global bstack1l111l1ll_opy_
    global bstack11l11lllll_opy_
    global bstack11l1lllll_opy_
    global bstack1l1l1l1111_opy_
    global bstack1ll1l1111_opy_
    global bstack1llll1llll_opy_
    global bstack1ll1l11l1_opy_
    global bstack1ll111ll_opy_
    global bstack1l111l11l_opy_
    global bstack1l11l11ll1_opy_
    try:
        from selenium import webdriver
        from selenium.webdriver.remote.webdriver import WebDriver
        bstack1lll1l1l_opy_ = webdriver.Remote.__init__
        bstack1llll1lll1_opy_ = WebDriver.quit
        bstack1ll1l1111_opy_ = WebDriver.close
        bstack1llll1llll_opy_ = WebDriver.get
    except Exception as e:
        pass
    if (bstack11ll1_opy_ (u"ࠧࡩࡶࡷࡴࡕࡸ࡯ࡹࡻࠪ┾") in CONFIG or bstack11ll1_opy_ (u"ࠨࡪࡷࡸࡵࡹࡐࡳࡱࡻࡽࠬ┿") in CONFIG) and bstack1l11lll111_opy_():
        if bstack1ll1ll1l11_opy_() < version.parse(bstack1llll1ll11_opy_):
            logger.error(bstack1lll1ll11l_opy_.format(bstack1ll1ll1l11_opy_()))
        else:
            try:
                from selenium.webdriver.remote.remote_connection import RemoteConnection
                if hasattr(RemoteConnection, bstack11ll1_opy_ (u"ࠩࡢ࡫ࡪࡺ࡟ࡱࡴࡲࡼࡾࡥࡵࡳ࡮ࠪ╀")) and callable(getattr(RemoteConnection, bstack11ll1_opy_ (u"ࠪࡣ࡬࡫ࡴࡠࡲࡵࡳࡽࡿ࡟ࡶࡴ࡯ࠫ╁"))):
                    bstack1ll1l11l1_opy_ = RemoteConnection._get_proxy_url
                else:
                    from selenium.webdriver.remote.client_config import ClientConfig
                    bstack1ll1l11l1_opy_ = ClientConfig.get_proxy_url
            except Exception as e:
                logger.error(bstack1l1llllll1_opy_.format(str(e)))
    try:
        from _pytest.config import Config
        bstack1ll111ll_opy_ = Config.getoption
        from _pytest import runner
        bstack1l111l11l_opy_ = runner._update_current_test_var
    except Exception as e:
        logger.warning(bstack11ll1_opy_ (u"ࠦࠪࡹ࠺ࠡࠧࡶࠦ╂"), bstack11lll1l1l1_opy_, str(e))
    try:
        from pytest_bdd import reporting
        bstack1l11l11ll1_opy_ = reporting.runtest_makereport
    except Exception as e:
        logger.debug(bstack11ll1_opy_ (u"ࠬࡖ࡬ࡦࡣࡶࡩࠥ࡯࡮ࡴࡶࡤࡰࡱࠦࡰࡺࡶࡨࡷࡹ࠳ࡢࡥࡦࠣࡸࡴࠦࡲࡶࡰࠣࡴࡾࡺࡥࡴࡶ࠰ࡦࡩࡪࠠࡵࡧࡶࡸࡸ࠭╃"))
    bstack11ll1l11l1_opy_ = CONFIG.get(bstack11ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࡒࡴࡹ࡯࡯࡯ࡵࠪ╄"), {}).get(bstack11ll1_opy_ (u"ࠧ࡭ࡱࡦࡥࡱࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩ╅"))
    bstack1ll1lll1l1_opy_ = True
    bstack1111l1111_opy_(bstack1l11l1lll1_opy_)
if (bstack111ll1ll11l_opy_()):
    bstack1lll1l111l1l_opy_()
@error_handler(class_method=False)
def bstack1lll1l11l111_opy_(hook_name, event, bstack1lll1l111ll_opy_=None):
    if hook_name not in [bstack11ll1_opy_ (u"ࠨࡵࡨࡸࡺࡶ࡟ࡧࡷࡱࡧࡹ࡯࡯࡯ࠩ╆"), bstack11ll1_opy_ (u"ࠩࡷࡩࡦࡸࡤࡰࡹࡱࡣ࡫ࡻ࡮ࡤࡶ࡬ࡳࡳ࠭╇"), bstack11ll1_opy_ (u"ࠪࡷࡪࡺࡵࡱࡡࡰࡳࡩࡻ࡬ࡦࠩ╈"), bstack11ll1_opy_ (u"ࠫࡹ࡫ࡡࡳࡦࡲࡻࡳࡥ࡭ࡰࡦࡸࡰࡪ࠭╉"), bstack11ll1_opy_ (u"ࠬࡹࡥࡵࡷࡳࡣࡨࡲࡡࡴࡵࠪ╊"), bstack11ll1_opy_ (u"࠭ࡴࡦࡣࡵࡨࡴࡽ࡮ࡠࡥ࡯ࡥࡸࡹࠧ╋"), bstack11ll1_opy_ (u"ࠧࡴࡧࡷࡹࡵࡥ࡭ࡦࡶ࡫ࡳࡩ࠭╌"), bstack11ll1_opy_ (u"ࠨࡶࡨࡥࡷࡪ࡯ࡸࡰࡢࡱࡪࡺࡨࡰࡦࠪ╍")]:
        return
    node = store[bstack11ll1_opy_ (u"ࠩࡦࡹࡷࡸࡥ࡯ࡶࡢࡸࡪࡹࡴࡠ࡫ࡷࡩࡲ࠭╎")]
    if hook_name in [bstack11ll1_opy_ (u"ࠪࡷࡪࡺࡵࡱࡡࡰࡳࡩࡻ࡬ࡦࠩ╏"), bstack11ll1_opy_ (u"ࠫࡹ࡫ࡡࡳࡦࡲࡻࡳࡥ࡭ࡰࡦࡸࡰࡪ࠭═")]:
        node = store[bstack11ll1_opy_ (u"ࠬࡩࡵࡳࡴࡨࡲࡹࡥ࡭ࡰࡦࡸࡰࡪࡥࡩࡵࡧࡰࠫ║")]
    elif hook_name in [bstack11ll1_opy_ (u"࠭ࡳࡦࡶࡸࡴࡤࡩ࡬ࡢࡵࡶࠫ╒"), bstack11ll1_opy_ (u"ࠧࡵࡧࡤࡶࡩࡵࡷ࡯ࡡࡦࡰࡦࡹࡳࠨ╓")]:
        node = store[bstack11ll1_opy_ (u"ࠨࡥࡸࡶࡷ࡫࡮ࡵࡡࡦࡰࡦࡹࡳࡠ࡫ࡷࡩࡲ࠭╔")]
    hook_type = bstack1llll1llll11_opy_(hook_name)
    if event == bstack11ll1_opy_ (u"ࠩࡥࡩ࡫ࡵࡲࡦࠩ╕"):
        if cli.is_running():
            cli.test_framework.track_event(cli_context, bstack1llll1ll111_opy_[hook_type], bstack1lll1111l11_opy_.PRE, node, hook_name)
            return
        uuid = uuid4().__str__()
        bstack1111llll11_opy_ = {
            bstack11ll1_opy_ (u"ࠪࡹࡺ࡯ࡤࠨ╖"): uuid,
            bstack11ll1_opy_ (u"ࠫࡸࡺࡡࡳࡶࡨࡨࡤࡧࡴࠨ╗"): bstack111lll1lll_opy_(),
            bstack11ll1_opy_ (u"ࠬࡺࡹࡱࡧࠪ╘"): bstack11ll1_opy_ (u"࠭ࡨࡰࡱ࡮ࠫ╙"),
            bstack11ll1_opy_ (u"ࠧࡩࡱࡲ࡯ࡤࡺࡹࡱࡧࠪ╚"): hook_type,
            bstack11ll1_opy_ (u"ࠨࡪࡲࡳࡰࡥ࡮ࡢ࡯ࡨࠫ╛"): hook_name
        }
        store[bstack11ll1_opy_ (u"ࠩࡦࡹࡷࡸࡥ࡯ࡶࡢ࡬ࡴࡵ࡫ࡠࡷࡸ࡭ࡩ࠭╜")].append(uuid)
        bstack1lll11ll1111_opy_ = node.nodeid
        if hook_type == bstack11ll1_opy_ (u"ࠪࡆࡊࡌࡏࡓࡇࡢࡉࡆࡉࡈࠨ╝"):
            if not _1111l1ll1l_opy_.get(bstack1lll11ll1111_opy_, None):
                _1111l1ll1l_opy_[bstack1lll11ll1111_opy_] = {bstack11ll1_opy_ (u"ࠫ࡭ࡵ࡯࡬ࡵࠪ╞"): []}
            _1111l1ll1l_opy_[bstack1lll11ll1111_opy_][bstack11ll1_opy_ (u"ࠬ࡮࡯ࡰ࡭ࡶࠫ╟")].append(bstack1111llll11_opy_[bstack11ll1_opy_ (u"࠭ࡵࡶ࡫ࡧࠫ╠")])
        _1111l1ll1l_opy_[bstack1lll11ll1111_opy_ + bstack11ll1_opy_ (u"ࠧ࠮ࠩ╡") + hook_name] = bstack1111llll11_opy_
        bstack1lll11ll1l11_opy_(node, bstack1111llll11_opy_, bstack11ll1_opy_ (u"ࠨࡊࡲࡳࡰࡘࡵ࡯ࡕࡷࡥࡷࡺࡥࡥࠩ╢"))
    elif event == bstack11ll1_opy_ (u"ࠩࡤࡪࡹ࡫ࡲࠨ╣"):
        if cli.is_running():
            cli.test_framework.track_event(cli_context, bstack1llll1ll111_opy_[hook_type], bstack1lll1111l11_opy_.POST, node, None, bstack1lll1l111ll_opy_)
            return
        bstack111l1lll11_opy_ = node.nodeid + bstack11ll1_opy_ (u"ࠪ࠱ࠬ╤") + hook_name
        _1111l1ll1l_opy_[bstack111l1lll11_opy_][bstack11ll1_opy_ (u"ࠫ࡫࡯࡮ࡪࡵ࡫ࡩࡩࡥࡡࡵࠩ╥")] = bstack111lll1lll_opy_()
        bstack1lll11ll1lll_opy_(_1111l1ll1l_opy_[bstack111l1lll11_opy_][bstack11ll1_opy_ (u"ࠬࡻࡵࡪࡦࠪ╦")])
        bstack1lll11ll1l11_opy_(node, _1111l1ll1l_opy_[bstack111l1lll11_opy_], bstack11ll1_opy_ (u"࠭ࡈࡰࡱ࡮ࡖࡺࡴࡆࡪࡰ࡬ࡷ࡭࡫ࡤࠨ╧"), bstack1lll1l111ll1_opy_=bstack1lll1l111ll_opy_)
def bstack1lll11ll111l_opy_():
    global bstack1lll1l1111l1_opy_
    if bstack1l1l1l1l_opy_():
        bstack1lll1l1111l1_opy_ = bstack11ll1_opy_ (u"ࠧࡱࡻࡷࡩࡸࡺ࠭ࡣࡦࡧࠫ╨")
    else:
        bstack1lll1l1111l1_opy_ = bstack11ll1_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࠨ╩")
@bstack11lll11l11_opy_.bstack1lll1lll11ll_opy_
def bstack1lll1l1111ll_opy_():
    bstack1lll11ll111l_opy_()
    if cli.is_running():
        try:
            bstack111l11lllll_opy_(bstack1lll1l11l111_opy_)
        except Exception as e:
            logger.debug(bstack11ll1_opy_ (u"ࠤࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥ࡯࡮ࠡࡪࡲࡳࡰࡹࠠࡱࡣࡷࡧ࡭ࡀࠠࡼࡿࠥ╪").format(e))
        return
    if bstack1l11lll111_opy_():
        bstack1l1l1ll1l_opy_ = Config.bstack1l1l1111_opy_()
        bstack11ll1_opy_ (u"ࠪࠫࠬࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࡋࡵࡲࠡࡲࡳࡴࠥࡃࠠ࠲࠮ࠣࡱࡴࡪ࡟ࡦࡺࡨࡧࡺࡺࡥࠡࡩࡨࡸࡸࠦࡵࡴࡧࡧࠤ࡫ࡵࡲࠡࡣ࠴࠵ࡾࠦࡣࡰ࡯ࡰࡥࡳࡪࡳ࠮ࡹࡵࡥࡵࡶࡩ࡯ࡩࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࡈࡲࡶࠥࡶࡰࡱࠢࡁࠤ࠶࠲ࠠ࡮ࡱࡧࡣࡪࡾࡥࡤࡷࡷࡩࠥࡪ࡯ࡦࡵࠣࡲࡴࡺࠠࡳࡷࡱࠤࡧ࡫ࡣࡢࡷࡶࡩࠥ࡯ࡴࠡ࡫ࡶࠤࡵࡧࡴࡤࡪࡨࡨࠥ࡯࡮ࠡࡣࠣࡨ࡮࡬ࡦࡦࡴࡨࡲࡹࠦࡰࡳࡱࡦࡩࡸࡹࠠࡪࡦࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࡖ࡫ࡹࡸࠦࡷࡦࠢࡱࡩࡪࡪࠠࡵࡱࠣࡹࡸ࡫ࠠࡔࡧ࡯ࡩࡳ࡯ࡵ࡮ࡒࡤࡸࡨ࡮ࠨࡴࡧ࡯ࡩࡳ࡯ࡵ࡮ࡡ࡫ࡥࡳࡪ࡬ࡦࡴࠬࠤ࡫ࡵࡲࠡࡲࡳࡴࠥࡄࠠ࠲ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠫࠬ࠭╫")
        if bstack1l1l1ll1l_opy_.get_property(bstack11ll1_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮ࡣࡲࡵࡤࡠࡥࡤࡰࡱ࡫ࡤࠨ╬")):
            if CONFIG.get(bstack11ll1_opy_ (u"ࠬࡶࡡࡳࡣ࡯ࡰࡪࡲࡳࡑࡧࡵࡔࡱࡧࡴࡧࡱࡵࡱࠬ╭")) is not None and int(CONFIG[bstack11ll1_opy_ (u"࠭ࡰࡢࡴࡤࡰࡱ࡫࡬ࡴࡒࡨࡶࡕࡲࡡࡵࡨࡲࡶࡲ࠭╮")]) > 1:
                bstack11ll1111ll_opy_(bstack1l1ll111_opy_)
            return
        bstack11ll1111ll_opy_(bstack1l1ll111_opy_)
    try:
        bstack111l11lllll_opy_(bstack1lll1l11l111_opy_)
    except Exception as e:
        logger.debug(bstack11ll1_opy_ (u"ࠢࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣ࡭ࡳࠦࡨࡰࡱ࡮ࡷࠥࡶࡡࡵࡥ࡫࠾ࠥࢁࡽࠣ╯").format(e))
bstack1lll1l1111ll_opy_()