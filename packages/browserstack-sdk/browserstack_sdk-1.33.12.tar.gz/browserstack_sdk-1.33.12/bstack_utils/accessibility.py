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
import os
import json
import requests
import logging
import threading
import bstack_utils.constants as bstack11ll11111l1_opy_
from urllib.parse import urlparse
from bstack_utils.constants import bstack11ll11lll1l_opy_ as bstack11ll111ll1l_opy_, EVENTS
from bstack_utils.bstack1l11l111l1_opy_ import bstack1l11l111l1_opy_
from bstack_utils.helper import bstack111lll1lll_opy_, bstack111l11l1ll_opy_, bstack11lllll11l_opy_, bstack11ll11l11l1_opy_, \
  bstack11l1llll111_opy_, bstack1lll11llll_opy_, get_host_info, bstack11ll111l1ll_opy_, bstack11l1l1l11l_opy_, error_handler, bstack11ll1111lll_opy_, bstack11l1lll11ll_opy_, bstack1lll11l1l_opy_
from browserstack_sdk._version import __version__
from bstack_utils.bstack111lll1l1_opy_ import get_logger
from bstack_utils.bstack11l11l11ll_opy_ import bstack1lll111111l_opy_
from selenium.webdriver.chrome.options import Options as ChromeOptions
from browserstack_sdk.sdk_cli.cli import cli
from bstack_utils.constants import *
from bstack_utils import bstack111lll1l1_opy_
logger = get_logger(__name__)
bstack11ll111l1l_opy_ = bstack111lll1l1_opy_.bstack1l1l111l_opy_(__name__)
bstack11l11l11ll_opy_ = bstack1lll111111l_opy_()
@error_handler(class_method=False)
def _11ll11l1l11_opy_(driver, bstack1lllllll1ll_opy_):
  response = {}
  try:
    caps = driver.capabilities
    response = {
        bstack11ll1_opy_ (u"ࠪࡳࡸࡥ࡮ࡢ࡯ࡨࠫᚮ"): caps.get(bstack11ll1_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡔࡡ࡮ࡧࠪᚯ"), None),
        bstack11ll1_opy_ (u"ࠬࡵࡳࡠࡸࡨࡶࡸ࡯࡯࡯ࠩᚰ"): bstack1lllllll1ll_opy_.get(bstack11ll1_opy_ (u"࠭࡯ࡴࡘࡨࡶࡸ࡯࡯࡯ࠩᚱ"), None),
        bstack11ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡠࡰࡤࡱࡪ࠭ᚲ"): caps.get(bstack11ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡐࡤࡱࡪ࠭ᚳ"), None),
        bstack11ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡢࡺࡪࡸࡳࡪࡱࡱࠫᚴ"): caps.get(bstack11ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵ࡚ࡪࡸࡳࡪࡱࡱࠫᚵ"), None)
    }
  except Exception as error:
    logger.debug(bstack11ll1_opy_ (u"ࠫࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡪࡰࠣࡪࡪࡺࡣࡩ࡫ࡱ࡫ࠥࡶ࡬ࡢࡶࡩࡳࡷࡳࠠࡥࡧࡷࡥ࡮ࡲࡳࠡࡹ࡬ࡸ࡭ࠦࡥࡳࡴࡲࡶࠥࡀࠠࠨᚶ") + str(error))
  return response
def on():
    if os.environ.get(bstack11ll1_opy_ (u"ࠬࡈࡓࡠࡃ࠴࠵࡞ࡥࡊࡘࡖࠪᚷ"), None) is None or os.environ[bstack11ll1_opy_ (u"࠭ࡂࡔࡡࡄ࠵࠶࡟࡟ࡋ࡙ࡗࠫᚸ")] == bstack11ll1_opy_ (u"ࠢ࡯ࡷ࡯ࡰࠧᚹ"):
        return False
    return True
def bstack11l1l1ll1_opy_(config):
  return config.get(bstack11ll1_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠨᚺ"), False) or any([p.get(bstack11ll1_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠩᚻ"), False) == True for p in config.get(bstack11ll1_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ᚼ"), [])])
def bstack1ll11l1ll1_opy_(config, bstack1l11ll11ll_opy_):
  try:
    bstack11ll11l1ll1_opy_ = config.get(bstack11ll1_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠫᚽ"), False)
    if int(bstack1l11ll11ll_opy_) < len(config.get(bstack11ll1_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨᚾ"), [])) and config[bstack11ll1_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩᚿ")][bstack1l11ll11ll_opy_]:
      bstack11l1llll1l1_opy_ = config[bstack11ll1_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪᛀ")][bstack1l11ll11ll_opy_].get(bstack11ll1_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠨᛁ"), None)
    else:
      bstack11l1llll1l1_opy_ = config.get(bstack11ll1_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠩᛂ"), None)
    if bstack11l1llll1l1_opy_ != None:
      bstack11ll11l1ll1_opy_ = bstack11l1llll1l1_opy_
    bstack11l1lllllll_opy_ = os.getenv(bstack11ll1_opy_ (u"ࠪࡆࡘࡥࡁ࠲࠳࡜ࡣࡏ࡝ࡔࠨᛃ")) is not None and len(os.getenv(bstack11ll1_opy_ (u"ࠫࡇ࡙࡟ࡂ࠳࠴࡝ࡤࡐࡗࡕࠩᛄ"))) > 0 and os.getenv(bstack11ll1_opy_ (u"ࠬࡈࡓࡠࡃ࠴࠵࡞ࡥࡊࡘࡖࠪᛅ")) != bstack11ll1_opy_ (u"࠭࡮ࡶ࡮࡯ࠫᛆ")
    return bstack11ll11l1ll1_opy_ and bstack11l1lllllll_opy_
  except Exception as error:
    logger.debug(bstack11ll1_opy_ (u"ࠧࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣ࡭ࡳࠦࡶࡦࡴ࡬ࡪࡾ࡯࡮ࡨࠢࡷ࡬ࡪࠦࡁࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࠦࡳࡦࡵࡶ࡭ࡴࡴࠠࡸ࡫ࡷ࡬ࠥ࡫ࡲࡳࡱࡵࠤ࠿ࠦࠧᛇ") + str(error))
  return False
def bstack1llll1111l_opy_(test_tags):
  bstack1l111ll111l_opy_ = os.getenv(bstack11ll1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡤࡇࡃࡄࡇࡖࡗࡎࡈࡉࡍࡋࡗ࡝ࡤࡉࡏࡏࡈࡌࡋ࡚ࡘࡁࡕࡋࡒࡒࡤ࡟ࡍࡍࠩᛈ"))
  if bstack1l111ll111l_opy_ is None:
    return True
  bstack1l111ll111l_opy_ = json.loads(bstack1l111ll111l_opy_)
  try:
    include_tags = bstack1l111ll111l_opy_[bstack11ll1_opy_ (u"ࠩ࡬ࡲࡨࡲࡵࡥࡧࡗࡥ࡬ࡹࡉ࡯ࡖࡨࡷࡹ࡯࡮ࡨࡕࡦࡳࡵ࡫ࠧᛉ")] if bstack11ll1_opy_ (u"ࠪ࡭ࡳࡩ࡬ࡶࡦࡨࡘࡦ࡭ࡳࡊࡰࡗࡩࡸࡺࡩ࡯ࡩࡖࡧࡴࡶࡥࠨᛊ") in bstack1l111ll111l_opy_ and isinstance(bstack1l111ll111l_opy_[bstack11ll1_opy_ (u"ࠫ࡮ࡴࡣ࡭ࡷࡧࡩ࡙ࡧࡧࡴࡋࡱࡘࡪࡹࡴࡪࡰࡪࡗࡨࡵࡰࡦࠩᛋ")], list) else []
    exclude_tags = bstack1l111ll111l_opy_[bstack11ll1_opy_ (u"ࠬ࡫ࡸࡤ࡮ࡸࡨࡪ࡚ࡡࡨࡵࡌࡲ࡙࡫ࡳࡵ࡫ࡱ࡫ࡘࡩ࡯ࡱࡧࠪᛌ")] if bstack11ll1_opy_ (u"࠭ࡥࡹࡥ࡯ࡹࡩ࡫ࡔࡢࡩࡶࡍࡳ࡚ࡥࡴࡶ࡬ࡲ࡬࡙ࡣࡰࡲࡨࠫᛍ") in bstack1l111ll111l_opy_ and isinstance(bstack1l111ll111l_opy_[bstack11ll1_opy_ (u"ࠧࡦࡺࡦࡰࡺࡪࡥࡕࡣࡪࡷࡎࡴࡔࡦࡵࡷ࡭ࡳ࡭ࡓࡤࡱࡳࡩࠬᛎ")], list) else []
    excluded = any(tag in exclude_tags for tag in test_tags)
    included = len(include_tags) == 0 or any(tag in include_tags for tag in test_tags)
    return not excluded and included
  except Exception as error:
    logger.debug(bstack11ll1_opy_ (u"ࠣࡇࡵࡶࡴࡸࠠࡸࡪ࡬ࡰࡪࠦࡶࡢ࡮࡬ࡨࡦࡺࡩ࡯ࡩࠣࡸࡪࡹࡴࠡࡥࡤࡷࡪࠦࡦࡰࡴࠣࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠣࡦࡪ࡬࡯ࡳࡧࠣࡷࡨࡧ࡮࡯࡫ࡱ࡫࠳ࠦࡅࡳࡴࡲࡶࠥࡀࠠࠣᛏ") + str(error))
  return False
def bstack11ll111l111_opy_(config, bstack11ll11l1lll_opy_, bstack11ll111111l_opy_, bstack11ll11ll11l_opy_):
  bstack11ll1111ll1_opy_ = bstack11ll11l11l1_opy_(config)
  bstack11ll1111111_opy_ = bstack11l1llll111_opy_(config)
  if bstack11ll1111ll1_opy_ is None or bstack11ll1111111_opy_ is None:
    logger.error(bstack11ll1_opy_ (u"ࠩࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥࡽࡨࡪ࡮ࡨࠤࡨࡸࡥࡢࡶ࡬ࡲ࡬ࠦࡴࡦࡵࡷࠤࡷࡻ࡮ࠡࡨࡲࡶࠥࡈࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࠤࡆࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠤࡆࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮࠻ࠢࡐ࡭ࡸࡹࡩ࡯ࡩࠣࡥࡺࡺࡨࡦࡰࡷ࡭ࡨࡧࡴࡪࡱࡱࠤࡹࡵ࡫ࡦࡰࠪᛐ"))
    return [None, None]
  try:
    settings = json.loads(os.getenv(bstack11ll1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡉࡘ࡚࡟ࡂࡅࡆࡉࡘ࡙ࡉࡃࡋࡏࡍ࡙࡟࡟ࡄࡑࡑࡊࡎࡍࡕࡓࡃࡗࡍࡔࡔ࡟࡚ࡏࡏࠫᛑ"), bstack11ll1_opy_ (u"ࠫࢀࢃࠧᛒ")))
    data = {
        bstack11ll1_opy_ (u"ࠬࡶࡲࡰ࡬ࡨࡧࡹࡔࡡ࡮ࡧࠪᛓ"): config[bstack11ll1_opy_ (u"࠭ࡰࡳࡱ࡭ࡩࡨࡺࡎࡢ࡯ࡨࠫᛔ")],
        bstack11ll1_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡔࡡ࡮ࡧࠪᛕ"): config.get(bstack11ll1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠫᛖ"), os.path.basename(os.getcwd())),
        bstack11ll1_opy_ (u"ࠩࡶࡸࡦࡸࡴࡕ࡫ࡰࡩࠬᛗ"): bstack111lll1lll_opy_(),
        bstack11ll1_opy_ (u"ࠪࡨࡪࡹࡣࡳ࡫ࡳࡸ࡮ࡵ࡮ࠨᛘ"): config.get(bstack11ll1_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡇࡩࡸࡩࡲࡪࡲࡷ࡭ࡴࡴࠧᛙ"), bstack11ll1_opy_ (u"ࠬ࠭ᛚ")),
        bstack11ll1_opy_ (u"࠭ࡳࡰࡷࡵࡧࡪ࠭ᛛ"): {
            bstack11ll1_opy_ (u"ࠧࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡑࡥࡲ࡫ࠧᛜ"): bstack11ll11l1lll_opy_,
            bstack11ll1_opy_ (u"ࠨࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮࡚ࡪࡸࡳࡪࡱࡱࠫᛝ"): bstack11ll111111l_opy_,
            bstack11ll1_opy_ (u"ࠩࡶࡨࡰ࡜ࡥࡳࡵ࡬ࡳࡳ࠭ᛞ"): __version__,
            bstack11ll1_opy_ (u"ࠪࡰࡦࡴࡧࡶࡣࡪࡩࠬᛟ"): bstack11ll1_opy_ (u"ࠫࡵࡿࡴࡩࡱࡱࠫᛠ"),
            bstack11ll1_opy_ (u"ࠬࡺࡥࡴࡶࡉࡶࡦࡳࡥࡸࡱࡵ࡯ࠬᛡ"): bstack11ll1_opy_ (u"࠭ࡳࡦ࡮ࡨࡲ࡮ࡻ࡭ࠨᛢ"),
            bstack11ll1_opy_ (u"ࠧࡵࡧࡶࡸࡋࡸࡡ࡮ࡧࡺࡳࡷࡱࡖࡦࡴࡶ࡭ࡴࡴࠧᛣ"): bstack11ll11ll11l_opy_
        },
        bstack11ll1_opy_ (u"ࠨࡵࡨࡸࡹ࡯࡮ࡨࡵࠪᛤ"): settings,
        bstack11ll1_opy_ (u"ࠩࡹࡩࡷࡹࡩࡰࡰࡆࡳࡳࡺࡲࡰ࡮ࠪᛥ"): bstack11ll111l1ll_opy_(),
        bstack11ll1_opy_ (u"ࠪࡧ࡮ࡏ࡮ࡧࡱࠪᛦ"): bstack1lll11llll_opy_(),
        bstack11ll1_opy_ (u"ࠫ࡭ࡵࡳࡵࡋࡱࡪࡴ࠭ᛧ"): get_host_info(),
        bstack11ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡅࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࠧᛨ"): bstack11lllll11l_opy_(config)
    }
    headers = {
        bstack11ll1_opy_ (u"࠭ࡃࡰࡰࡷࡩࡳࡺ࠭ࡕࡻࡳࡩࠬᛩ"): bstack11ll1_opy_ (u"ࠧࡢࡲࡳࡰ࡮ࡩࡡࡵ࡫ࡲࡲ࠴ࡰࡳࡰࡰࠪᛪ"),
    }
    config = {
        bstack11ll1_opy_ (u"ࠨࡣࡸࡸ࡭࠭᛫"): (bstack11ll1111ll1_opy_, bstack11ll1111111_opy_),
        bstack11ll1_opy_ (u"ࠩ࡫ࡩࡦࡪࡥࡳࡵࠪ᛬"): headers
    }
    response = bstack11l1l1l11l_opy_(bstack11ll1_opy_ (u"ࠪࡔࡔ࡙ࡔࠨ᛭"), bstack11ll111ll1l_opy_ + bstack11ll1_opy_ (u"ࠫ࠴ࡼ࠲࠰ࡶࡨࡷࡹࡥࡲࡶࡰࡶࠫᛮ"), data, config)
    bstack11l1llll1ll_opy_ = response.json()
    if bstack11l1llll1ll_opy_[bstack11ll1_opy_ (u"ࠬࡹࡵࡤࡥࡨࡷࡸ࠭ᛯ")]:
      parsed = json.loads(os.getenv(bstack11ll1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡢࡅࡈࡉࡅࡔࡕࡌࡆࡎࡒࡉࡕ࡛ࡢࡇࡔࡔࡆࡊࡉࡘࡖࡆ࡚ࡉࡐࡐࡢ࡝ࡒࡒࠧᛰ"), bstack11ll1_opy_ (u"ࠧࡼࡿࠪᛱ")))
      parsed[bstack11ll1_opy_ (u"ࠨࡵࡦࡥࡳࡴࡥࡳࡘࡨࡶࡸ࡯࡯࡯ࠩᛲ")] = bstack11l1llll1ll_opy_[bstack11ll1_opy_ (u"ࠩࡧࡥࡹࡧࠧᛳ")][bstack11ll1_opy_ (u"ࠪࡷࡨࡧ࡮࡯ࡧࡵ࡚ࡪࡸࡳࡪࡱࡱࠫᛴ")]
      os.environ[bstack11ll1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡠࡃࡆࡇࡊ࡙ࡓࡊࡄࡌࡐࡎ࡚࡙ࡠࡅࡒࡒࡋࡏࡇࡖࡔࡄࡘࡎࡕࡎࡠ࡛ࡐࡐࠬᛵ")] = json.dumps(parsed)
      bstack1l11l111l1_opy_.bstack111l1ll1l_opy_(bstack11l1llll1ll_opy_[bstack11ll1_opy_ (u"ࠬࡪࡡࡵࡣࠪᛶ")][bstack11ll1_opy_ (u"࠭ࡳࡤࡴ࡬ࡴࡹࡹࠧᛷ")])
      bstack1l11l111l1_opy_.bstack11ll11l111l_opy_(bstack11l1llll1ll_opy_[bstack11ll1_opy_ (u"ࠧࡥࡣࡷࡥࠬᛸ")][bstack11ll1_opy_ (u"ࠨࡥࡲࡱࡲࡧ࡮ࡥࡵࠪ᛹")])
      bstack1l11l111l1_opy_.store()
      return bstack11l1llll1ll_opy_[bstack11ll1_opy_ (u"ࠩࡧࡥࡹࡧࠧ᛺")][bstack11ll1_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࡗࡳࡰ࡫࡮ࠨ᛻")], bstack11l1llll1ll_opy_[bstack11ll1_opy_ (u"ࠫࡩࡧࡴࡢࠩ᛼")][bstack11ll1_opy_ (u"ࠬ࡯ࡤࠨ᛽")]
    else:
      logger.error(bstack11ll1_opy_ (u"࠭ࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢࡺ࡬࡮ࡲࡥࠡࡴࡸࡲࡳ࡯࡮ࡨࠢࡅࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࠡࡃࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠡࡃࡸࡸࡴࡳࡡࡵ࡫ࡲࡲ࠿ࠦࠧ᛾") + bstack11l1llll1ll_opy_[bstack11ll1_opy_ (u"ࠧ࡮ࡧࡶࡷࡦ࡭ࡥࠨ᛿")])
      if bstack11l1llll1ll_opy_[bstack11ll1_opy_ (u"ࠨ࡯ࡨࡷࡸࡧࡧࡦࠩᜀ")] == bstack11ll1_opy_ (u"ࠩࡌࡲࡻࡧ࡬ࡪࡦࠣࡧࡴࡴࡦࡪࡩࡸࡶࡦࡺࡩࡰࡰࠣࡴࡦࡹࡳࡦࡦ࠱ࠫᜁ"):
        for bstack11l1lll1ll1_opy_ in bstack11l1llll1ll_opy_[bstack11ll1_opy_ (u"ࠪࡩࡷࡸ࡯ࡳࡵࠪᜂ")]:
          logger.error(bstack11l1lll1ll1_opy_[bstack11ll1_opy_ (u"ࠫࡲ࡫ࡳࡴࡣࡪࡩࠬᜃ")])
      return None, None
  except Exception as error:
    logger.error(bstack11ll1_opy_ (u"ࠧࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡࡹ࡫࡭ࡱ࡫ࠠࡤࡴࡨࡥࡹ࡯࡮ࡨࠢࡷࡩࡸࡺࠠࡳࡷࡱࠤ࡫ࡵࡲࠡࡄࡵࡳࡼࡹࡥࡳࡕࡷࡥࡨࡱࠠࡂࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡂࡷࡷࡳࡲࡧࡴࡪࡱࡱ࠾ࠥࠨᜄ") +  str(error))
    return None, None
def bstack11l1llllll1_opy_():
  if os.getenv(bstack11ll1_opy_ (u"࠭ࡂࡔࡡࡄ࠵࠶࡟࡟ࡋ࡙ࡗࠫᜅ")) is None:
    return {
        bstack11ll1_opy_ (u"ࠧࡴࡶࡤࡸࡺࡹࠧᜆ"): bstack11ll1_opy_ (u"ࠨࡧࡵࡶࡴࡸࠧᜇ"),
        bstack11ll1_opy_ (u"ࠩࡰࡩࡸࡹࡡࡨࡧࠪᜈ"): bstack11ll1_opy_ (u"ࠪࡆࡺ࡯࡬ࡥࠢࡦࡶࡪࡧࡴࡪࡱࡱࠤ࡭ࡧࡤࠡࡨࡤ࡭ࡱ࡫ࡤ࠯ࠩᜉ")
    }
  data = {bstack11ll1_opy_ (u"ࠫࡪࡴࡤࡕ࡫ࡰࡩࠬᜊ"): bstack111lll1lll_opy_()}
  headers = {
      bstack11ll1_opy_ (u"ࠬࡇࡵࡵࡪࡲࡶ࡮ࢀࡡࡵ࡫ࡲࡲࠬᜋ"): bstack11ll1_opy_ (u"࠭ࡂࡦࡣࡵࡩࡷࠦࠧᜌ") + os.getenv(bstack11ll1_opy_ (u"ࠢࡃࡕࡢࡅ࠶࠷࡙ࡠࡌ࡚ࡘࠧᜍ")),
      bstack11ll1_opy_ (u"ࠨࡅࡲࡲࡹ࡫࡮ࡵ࠯ࡗࡽࡵ࡫ࠧᜎ"): bstack11ll1_opy_ (u"ࠩࡤࡴࡵࡲࡩࡤࡣࡷ࡭ࡴࡴ࠯࡫ࡵࡲࡲࠬᜏ")
  }
  response = bstack11l1l1l11l_opy_(bstack11ll1_opy_ (u"ࠪࡔ࡚࡚ࠧᜐ"), bstack11ll111ll1l_opy_ + bstack11ll1_opy_ (u"ࠫ࠴ࡺࡥࡴࡶࡢࡶࡺࡴࡳ࠰ࡵࡷࡳࡵ࠭ᜑ"), data, { bstack11ll1_opy_ (u"ࠬ࡮ࡥࡢࡦࡨࡶࡸ࠭ᜒ"): headers })
  try:
    if response.status_code == 200:
      logger.info(bstack11ll1_opy_ (u"ࠨࡂࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࠥࡇࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡇࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࠢࡗࡩࡸࡺࠠࡓࡷࡱࠤࡲࡧࡲ࡬ࡧࡧࠤࡦࡹࠠࡤࡱࡰࡴࡱ࡫ࡴࡦࡦࠣࡥࡹࠦࠢᜓ") + bstack111l11l1ll_opy_().isoformat() + bstack11ll1_opy_ (u"᜔࡛ࠧࠩ"))
      return {bstack11ll1_opy_ (u"ࠨࡵࡷࡥࡹࡻࡳࠨ᜕"): bstack11ll1_opy_ (u"ࠩࡶࡹࡨࡩࡥࡴࡵࠪ᜖"), bstack11ll1_opy_ (u"ࠪࡱࡪࡹࡳࡢࡩࡨࠫ᜗"): bstack11ll1_opy_ (u"ࠫࠬ᜘")}
    else:
      response.raise_for_status()
  except requests.RequestException as error:
    logger.error(bstack11ll1_opy_ (u"ࠧࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡࡹ࡫࡭ࡱ࡫ࠠ࡮ࡣࡵ࡯࡮ࡴࡧࠡࡥࡲࡱࡵࡲࡥࡵ࡫ࡲࡲࠥࡵࡦࠡࡄࡵࡳࡼࡹࡥࡳࡕࡷࡥࡨࡱࠠࡂࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡂࡷࡷࡳࡲࡧࡴࡪࡱࡱࠤ࡙࡫ࡳࡵࠢࡕࡹࡳࡀࠠࠣ᜙") + str(error))
    return {
        bstack11ll1_opy_ (u"࠭ࡳࡵࡣࡷࡹࡸ࠭᜚"): bstack11ll1_opy_ (u"ࠧࡦࡴࡵࡳࡷ࠭᜛"),
        bstack11ll1_opy_ (u"ࠨ࡯ࡨࡷࡸࡧࡧࡦࠩ᜜"): str(error)
    }
def bstack11ll111l1l1_opy_(bstack11ll111ll11_opy_):
    return re.match(bstack11ll1_opy_ (u"ࡴࠪࡢࡡࡪࠫࠩ࡞࠱ࡠࡩ࠱ࠩࡀࠦࠪ᜝"), bstack11ll111ll11_opy_.strip()) is not None
def bstack11l1lll1_opy_(caps, options, desired_capabilities={}, config=None):
    try:
        if options:
          bstack11ll1111l11_opy_ = options.to_capabilities()
        elif desired_capabilities:
          bstack11ll1111l11_opy_ = desired_capabilities
        else:
          bstack11ll1111l11_opy_ = {}
        bstack1l11l1l1lll_opy_ = (bstack11ll1111l11_opy_.get(bstack11ll1_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡓࡧ࡭ࡦࠩ᜞"), bstack11ll1_opy_ (u"ࠫࠬᜟ")).lower() or caps.get(bstack11ll1_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡎࡢ࡯ࡨࠫᜠ"), bstack11ll1_opy_ (u"࠭ࠧᜡ")).lower())
        if bstack1l11l1l1lll_opy_ == bstack11ll1_opy_ (u"ࠧࡪࡱࡶࠫᜢ"):
            return True
        if bstack1l11l1l1lll_opy_ == bstack11ll1_opy_ (u"ࠨࡣࡱࡨࡷࡵࡩࡥࠩᜣ"):
            bstack1l11l11111l_opy_ = str(float(caps.get(bstack11ll1_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰ࡚ࡪࡸࡳࡪࡱࡱࠫᜤ")) or bstack11ll1111l11_opy_.get(bstack11ll1_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭࠽ࡳࡵࡺࡩࡰࡰࡶࠫᜥ"), {}).get(bstack11ll1_opy_ (u"ࠫࡴࡹࡖࡦࡴࡶ࡭ࡴࡴࠧᜦ"),bstack11ll1_opy_ (u"ࠬ࠭ᜧ"))))
            if bstack1l11l1l1lll_opy_ == bstack11ll1_opy_ (u"࠭ࡡ࡯ࡦࡵࡳ࡮ࡪࠧᜨ") and int(bstack1l11l11111l_opy_.split(bstack11ll1_opy_ (u"ࠧ࠯ࠩᜩ"))[0]) < float(bstack11l1lllll1l_opy_):
                logger.warning(str(bstack11ll111l11l_opy_))
                return False
            return True
        bstack1l11l1l11l1_opy_ = caps.get(bstack11ll1_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫࠻ࡱࡳࡸ࡮ࡵ࡮ࡴࠩᜪ"), {}).get(bstack11ll1_opy_ (u"ࠩࡧࡩࡻ࡯ࡣࡦࡐࡤࡱࡪ࠭ᜫ"), caps.get(bstack11ll1_opy_ (u"ࠪࡨࡪࡼࡩࡤࡧࠪᜬ"), bstack11ll1_opy_ (u"ࠫࠬᜭ")))
        if bstack1l11l1l11l1_opy_:
            logger.warning(bstack11ll1_opy_ (u"ࠧࡇࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡇࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࠢࡺ࡭ࡱࡲࠠࡳࡷࡱࠤࡴࡴ࡬ࡺࠢࡲࡲࠥࡊࡥࡴ࡭ࡷࡳࡵࠦࡢࡳࡱࡺࡷࡪࡸࡳ࠯ࠤᜮ"))
            return False
        browser = caps.get(bstack11ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡎࡢ࡯ࡨࠫᜯ"), bstack11ll1_opy_ (u"ࠧࠨᜰ")).lower() or bstack11ll1111l11_opy_.get(bstack11ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡐࡤࡱࡪ࠭ᜱ"), bstack11ll1_opy_ (u"ࠩࠪᜲ")).lower()
        if browser != bstack11ll1_opy_ (u"ࠪࡧ࡭ࡸ࡯࡮ࡧࠪᜳ"):
            logger.warning(bstack11ll1_opy_ (u"ࠦࡆࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠤࡆࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠡࡹ࡬ࡰࡱࠦࡲࡶࡰࠣࡳࡳࡲࡹࠡࡱࡱࠤࡈ࡮ࡲࡰ࡯ࡨࠤࡧࡸ࡯ࡸࡵࡨࡶࡸ࠴᜴ࠢ"))
            return False
        browser_version = caps.get(bstack11ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡜ࡥࡳࡵ࡬ࡳࡳ࠭᜵")) or caps.get(bstack11ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸ࡟ࡷࡧࡵࡷ࡮ࡵ࡮ࠨ᜶")) or bstack11ll1111l11_opy_.get(bstack11ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡗࡧࡵࡷ࡮ࡵ࡮ࠨ᜷")) or bstack11ll1111l11_opy_.get(bstack11ll1_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫࠻ࡱࡳࡸ࡮ࡵ࡮ࡴࠩ᜸"), {}).get(bstack11ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴ࡙ࡩࡷࡹࡩࡰࡰࠪ᜹")) or bstack11ll1111l11_opy_.get(bstack11ll1_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭࠽ࡳࡵࡺࡩࡰࡰࡶࠫ᜺"), {}).get(bstack11ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡤࡼࡥࡳࡵ࡬ࡳࡳ࠭᜻"))
        bstack1l111lll1ll_opy_ = bstack11ll11111l1_opy_.bstack1l111ll1lll_opy_
        bstack11ll111lll1_opy_ = False
        if config is not None:
          bstack11ll111lll1_opy_ = bstack11ll1_opy_ (u"ࠬࡺࡵࡳࡤࡲࡗࡨࡧ࡬ࡦࠩ᜼") in config and str(config[bstack11ll1_opy_ (u"࠭ࡴࡶࡴࡥࡳࡘࡩࡡ࡭ࡧࠪ᜽")]).lower() != bstack11ll1_opy_ (u"ࠧࡧࡣ࡯ࡷࡪ࠭᜾")
        if os.environ.get(bstack11ll1_opy_ (u"ࠨࡋࡖࡣࡓࡕࡎࡠࡄࡖࡘࡆࡉࡋࡠࡋࡑࡊࡗࡇ࡟ࡂ࠳࠴࡝ࡤ࡙ࡅࡔࡕࡌࡓࡓ࠭᜿"), bstack11ll1_opy_ (u"ࠩࠪᝀ")).lower() == bstack11ll1_opy_ (u"ࠪࡸࡷࡻࡥࠨᝁ") or bstack11ll111lll1_opy_:
          bstack1l111lll1ll_opy_ = bstack11ll11111l1_opy_.bstack1l11l11l1ll_opy_
        if browser_version and browser_version != bstack11ll1_opy_ (u"ࠫࡱࡧࡴࡦࡵࡷࠫᝂ") and int(browser_version.split(bstack11ll1_opy_ (u"ࠬ࠴ࠧᝃ"))[0]) <= bstack1l111lll1ll_opy_:
          logger.warning(bstack1l1ll111l1l_opy_ (u"࠭ࡁࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࠦࡁࡶࡶࡲࡱࡦࡺࡩࡰࡰࠣࡻ࡮ࡲ࡬ࠡࡴࡸࡲࠥࡵ࡮࡭ࡻࠣࡳࡳࠦࡃࡩࡴࡲࡱࡪࠦࡢࡳࡱࡺࡷࡪࡸࠠࡷࡧࡵࡷ࡮ࡵ࡮ࠡࡩࡵࡩࡦࡺࡥࡳࠢࡷ࡬ࡦࡴࠠࡼ࡯࡬ࡲࡤࡧ࠱࠲ࡻࡢࡷࡺࡶࡰࡰࡴࡷࡩࡩࡥࡣࡩࡴࡲࡱࡪࡥࡶࡦࡴࡶ࡭ࡴࡴࡽ࠯ࠩᝄ"))
          return False
        if not options:
          bstack1l111llll1l_opy_ = caps.get(bstack11ll1_opy_ (u"ࠧࡨࡱࡲ࡫࠿ࡩࡨࡳࡱࡰࡩࡔࡶࡴࡪࡱࡱࡷࠬᝅ")) or bstack11ll1111l11_opy_.get(bstack11ll1_opy_ (u"ࠨࡩࡲࡳ࡬ࡀࡣࡩࡴࡲࡱࡪࡕࡰࡵ࡫ࡲࡲࡸ࠭ᝆ"), {})
          if bstack11ll1_opy_ (u"ࠩ࠰࠱࡭࡫ࡡࡥ࡮ࡨࡷࡸ࠭ᝇ") in bstack1l111llll1l_opy_.get(bstack11ll1_opy_ (u"ࠪࡥࡷ࡭ࡳࠨᝈ"), []):
              logger.warning(bstack11ll1_opy_ (u"ࠦࡆࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠤࡆࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠡࡹ࡬ࡰࡱࠦ࡮ࡰࡶࠣࡶࡺࡴࠠࡰࡰࠣࡰࡪ࡭ࡡࡤࡻࠣ࡬ࡪࡧࡤ࡭ࡧࡶࡷࠥࡳ࡯ࡥࡧ࠱ࠤࡘࡽࡩࡵࡥ࡫ࠤࡹࡵࠠ࡯ࡧࡺࠤ࡭࡫ࡡࡥ࡮ࡨࡷࡸࠦ࡭ࡰࡦࡨࠤࡴࡸࠠࡢࡸࡲ࡭ࡩࠦࡵࡴ࡫ࡱ࡫ࠥ࡮ࡥࡢࡦ࡯ࡩࡸࡹࠠ࡮ࡱࡧࡩ࠳ࠨᝉ"))
              return False
        return True
    except Exception as error:
        logger.debug(bstack11ll1_opy_ (u"ࠧࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡ࡫ࡱࠤࡻࡧ࡬ࡪࡦࡤࡸࡪࠦࡡ࠲࠳ࡼࠤࡸࡻࡰࡱࡱࡵࡸࠥࡀࠢᝊ") + str(error))
        return False
def set_capabilities(caps, config):
  try:
    bstack1l1l1111ll1_opy_ = config.get(bstack11ll1_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࡕࡰࡵ࡫ࡲࡲࡸ࠭ᝋ"), {})
    bstack1l1l1111ll1_opy_[bstack11ll1_opy_ (u"ࠧࡢࡷࡷ࡬࡙ࡵ࡫ࡦࡰࠪᝌ")] = os.getenv(bstack11ll1_opy_ (u"ࠨࡄࡖࡣࡆ࠷࠱࡚ࡡࡍ࡛࡙࠭ᝍ"))
    bstack11l1lll1l11_opy_ = json.loads(os.getenv(bstack11ll1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡥࡁࡄࡅࡈࡗࡘࡏࡂࡊࡎࡌࡘ࡞ࡥࡃࡐࡐࡉࡍࡌ࡛ࡒࡂࡖࡌࡓࡓࡥ࡙ࡎࡎࠪᝎ"), bstack11ll1_opy_ (u"ࠪࡿࢂ࠭ᝏ"))).get(bstack11ll1_opy_ (u"ࠫࡸࡩࡡ࡯ࡰࡨࡶ࡛࡫ࡲࡴ࡫ࡲࡲࠬᝐ"))
    if not config[bstack11ll1_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡔࡷࡵࡤࡶࡥࡷࡑࡦࡶࠧᝑ")].get(bstack11ll1_opy_ (u"ࠨࡡࡱࡲࡢࡥࡺࡺ࡯࡮ࡣࡷࡩࠧᝒ")):
      if bstack11ll1_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱ࠺ࡰࡲࡷ࡭ࡴࡴࡳࠨᝓ") in caps:
        caps[bstack11ll1_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫࠻ࡱࡳࡸ࡮ࡵ࡮ࡴࠩ᝔")][bstack11ll1_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࡑࡳࡸ࡮ࡵ࡮ࡴࠩ᝕")] = bstack1l1l1111ll1_opy_
        caps[bstack11ll1_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭࠽ࡳࡵࡺࡩࡰࡰࡶࠫ᝖")][bstack11ll1_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࡓࡵࡺࡩࡰࡰࡶࠫ᝗")][bstack11ll1_opy_ (u"ࠬࡹࡣࡢࡰࡱࡩࡷ࡜ࡥࡳࡵ࡬ࡳࡳ࠭᝘")] = bstack11l1lll1l11_opy_
      else:
        caps[bstack11ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࡔࡶࡴࡪࡱࡱࡷࠬ᝙")] = bstack1l1l1111ll1_opy_
        caps[bstack11ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࡕࡰࡵ࡫ࡲࡲࡸ࠭᝚")][bstack11ll1_opy_ (u"ࠨࡵࡦࡥࡳࡴࡥࡳࡘࡨࡶࡸ࡯࡯࡯ࠩ᝛")] = bstack11l1lll1l11_opy_
  except Exception as error:
    logger.debug(bstack11ll1_opy_ (u"ࠤࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥࡽࡨࡪ࡮ࡨࠤࡸ࡫ࡴࡵ࡫ࡱ࡫ࠥࡇࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡇࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࠢࡦࡥࡵࡧࡢࡪ࡮࡬ࡸ࡮࡫ࡳ࠯ࠢࡈࡶࡷࡵࡲ࠻ࠢࠥ᝜") +  str(error))
def bstack11lll1111l_opy_(driver, bstack11l1lll1l1l_opy_):
  try:
    setattr(driver, bstack11ll1_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭ࡄ࠵࠶ࡿࡓࡩࡱࡸࡰࡩ࡙ࡣࡢࡰࠪ᝝"), True)
    session = driver.session_id
    if session:
      bstack11ll11l1111_opy_ = True
      current_url = driver.current_url
      try:
        url = urlparse(current_url)
      except Exception as e:
        bstack11ll11l1111_opy_ = False
      bstack11ll11l1111_opy_ = url.scheme in [bstack11ll1_opy_ (u"ࠦ࡭ࡺࡴࡱࠤ᝞"), bstack11ll1_opy_ (u"ࠧ࡮ࡴࡵࡲࡶࠦ᝟")]
      if bstack11ll11l1111_opy_:
        if bstack11l1lll1l1l_opy_:
          logger.info(bstack11ll1_opy_ (u"ࠨࡓࡦࡶࡸࡴࠥ࡬࡯ࡳࠢࡄࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠢࡷࡩࡸࡺࡩ࡯ࡩࠣ࡬ࡦࡹࠠࡴࡶࡤࡶࡹ࡫ࡤ࠯ࠢࡄࡹࡹࡵ࡭ࡢࡶࡨࠤࡹ࡫ࡳࡵࠢࡦࡥࡸ࡫ࠠࡦࡺࡨࡧࡺࡺࡩࡰࡰࠣࡻ࡮ࡲ࡬ࠡࡤࡨ࡫࡮ࡴࠠ࡮ࡱࡰࡩࡳࡺࡡࡳ࡫࡯ࡽ࠳ࠨᝠ"))
      return bstack11l1lll1l1l_opy_
  except Exception as e:
    logger.error(bstack11ll1_opy_ (u"ࠢࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣ࡭ࡳࠦࡳࡵࡣࡵࡸ࡮ࡴࡧࠡࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠡࡣࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࠥࡹࡣࡢࡰࠣࡪࡴࡸࠠࡵࡪ࡬ࡷࠥࡺࡥࡴࡶࠣࡧࡦࡹࡥ࠻ࠢࠥᝡ") + str(e))
    return False
def bstack1lll1111ll_opy_(driver, name, path):
  try:
    bstack1l111lll111_opy_ = {
        bstack11ll1_opy_ (u"ࠨࡶ࡫ࡘࡪࡹࡴࡓࡷࡱ࡙ࡺ࡯ࡤࠨᝢ"): threading.current_thread().current_test_uuid,
        bstack11ll1_opy_ (u"ࠩࡷ࡬ࡇࡻࡩ࡭ࡦࡘࡹ࡮ࡪࠧᝣ"): os.environ.get(bstack11ll1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡉࡘ࡚ࡈࡖࡄࡢ࡙࡚ࡏࡄࠨᝤ"), bstack11ll1_opy_ (u"ࠫࠬᝥ")),
        bstack11ll1_opy_ (u"ࠬࡺࡨࡋࡹࡷࡘࡴࡱࡥ࡯ࠩᝦ"): os.environ.get(bstack11ll1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡊࡘࡖࠪᝧ"), bstack11ll1_opy_ (u"ࠧࠨᝨ"))
    }
    bstack1lll1l1ll11_opy_ = bstack11l11l11ll_opy_.bstack1lll1111lll_opy_(EVENTS.bstack11lll11l_opy_.value)
    logger.debug(bstack11ll1_opy_ (u"ࠨࡒࡨࡶ࡫ࡵࡲ࡮࡫ࡱ࡫ࠥࡹࡣࡢࡰࠣࡦࡪ࡬࡯ࡳࡧࠣࡷࡦࡼࡩ࡯ࡩࠣࡶࡪࡹࡵ࡭ࡶࡶࠫᝩ"))
    try:
      if (bstack1lll11l1l_opy_(threading.current_thread(), bstack11ll1_opy_ (u"ࠩ࡬ࡷࡆࡶࡰࡂ࠳࠴ࡽ࡙࡫ࡳࡵࠩᝪ"), None) and bstack1lll11l1l_opy_(threading.current_thread(), bstack11ll1_opy_ (u"ࠪࡥࡵࡶࡁ࠲࠳ࡼࡔࡱࡧࡴࡧࡱࡵࡱࠬᝫ"), None)):
        scripts = {bstack11ll1_opy_ (u"ࠫࡸࡩࡡ࡯ࠩᝬ"): bstack1l11l111l1_opy_.perform_scan}
        bstack11ll11ll1ll_opy_ = json.loads(scripts[bstack11ll1_opy_ (u"ࠧࡹࡣࡢࡰࠥ᝭")].replace(bstack11ll1_opy_ (u"ࠨࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤ࡫ࡸࡦࡥࡸࡸࡴࡸ࠺ࠡࠤᝮ"), bstack11ll1_opy_ (u"ࠢࠣᝯ")))
        bstack11ll11ll1ll_opy_[bstack11ll1_opy_ (u"ࠨࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠫᝰ")][bstack11ll1_opy_ (u"ࠩࡰࡩࡹ࡮࡯ࡥࠩ᝱")] = None
        scripts[bstack11ll1_opy_ (u"ࠥࡷࡨࡧ࡮ࠣᝲ")] = bstack11ll1_opy_ (u"ࠦࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡩࡽ࡫ࡣࡶࡶࡲࡶ࠿ࠦࠢᝳ") + json.dumps(bstack11ll11ll1ll_opy_)
        bstack1l11l111l1_opy_.bstack111l1ll1l_opy_(scripts)
        bstack1l11l111l1_opy_.store()
        logger.debug(driver.execute_script(bstack1l11l111l1_opy_.perform_scan))
      else:
        logger.debug(driver.execute_async_script(bstack1l11l111l1_opy_.perform_scan, {bstack11ll1_opy_ (u"ࠧࡳࡥࡵࡪࡲࡨࠧ᝴"): name}))
      bstack11l11l11ll_opy_.end(EVENTS.bstack11lll11l_opy_.value, bstack1lll1l1ll11_opy_ + bstack11ll1_opy_ (u"ࠨ࠺ࡴࡶࡤࡶࡹࠨ᝵"), bstack1lll1l1ll11_opy_ + bstack11ll1_opy_ (u"ࠢ࠻ࡧࡱࡨࠧ᝶"), True, None)
    except Exception as error:
      bstack11l11l11ll_opy_.end(EVENTS.bstack11lll11l_opy_.value, bstack1lll1l1ll11_opy_ + bstack11ll1_opy_ (u"ࠣ࠼ࡶࡸࡦࡸࡴࠣ᝷"), bstack1lll1l1ll11_opy_ + bstack11ll1_opy_ (u"ࠤ࠽ࡩࡳࡪࠢ᝸"), False, str(error))
    bstack1lll1l1ll11_opy_ = bstack11l11l11ll_opy_.bstack11ll1111l1l_opy_(EVENTS.bstack1l11l111111_opy_.value)
    bstack11l11l11ll_opy_.mark(bstack1lll1l1ll11_opy_ + bstack11ll1_opy_ (u"ࠥ࠾ࡸࡺࡡࡳࡶࠥ᝹"))
    try:
      if (bstack1lll11l1l_opy_(threading.current_thread(), bstack11ll1_opy_ (u"ࠫ࡮ࡹࡁࡱࡲࡄ࠵࠶ࡿࡔࡦࡵࡷࠫ᝺"), None) and bstack1lll11l1l_opy_(threading.current_thread(), bstack11ll1_opy_ (u"ࠬࡧࡰࡱࡃ࠴࠵ࡾࡖ࡬ࡢࡶࡩࡳࡷࡳࠧ᝻"), None)):
        scripts = {bstack11ll1_opy_ (u"࠭ࡳࡤࡣࡱࠫ᝼"): bstack1l11l111l1_opy_.perform_scan}
        bstack11ll11ll1ll_opy_ = json.loads(scripts[bstack11ll1_opy_ (u"ࠢࡴࡥࡤࡲࠧ᝽")].replace(bstack11ll1_opy_ (u"ࠣࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࠦ᝾"), bstack11ll1_opy_ (u"ࠤࠥ᝿")))
        bstack11ll11ll1ll_opy_[bstack11ll1_opy_ (u"ࠪࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸ࠭ក")][bstack11ll1_opy_ (u"ࠫࡲ࡫ࡴࡩࡱࡧࠫខ")] = None
        scripts[bstack11ll1_opy_ (u"ࠧࡹࡣࡢࡰࠥគ")] = bstack11ll1_opy_ (u"ࠨࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤ࡫ࡸࡦࡥࡸࡸࡴࡸ࠺ࠡࠤឃ") + json.dumps(bstack11ll11ll1ll_opy_)
        bstack1l11l111l1_opy_.bstack111l1ll1l_opy_(scripts)
        bstack1l11l111l1_opy_.store()
        logger.debug(driver.execute_script(bstack1l11l111l1_opy_.perform_scan))
      else:
        logger.debug(driver.execute_async_script(bstack1l11l111l1_opy_.bstack11ll111llll_opy_, bstack1l111lll111_opy_))
      bstack11l11l11ll_opy_.end(bstack1lll1l1ll11_opy_, bstack1lll1l1ll11_opy_ + bstack11ll1_opy_ (u"ࠢ࠻ࡵࡷࡥࡷࡺࠢង"), bstack1lll1l1ll11_opy_ + bstack11ll1_opy_ (u"ࠣ࠼ࡨࡲࡩࠨច"),True, None)
    except Exception as error:
      bstack11l11l11ll_opy_.end(bstack1lll1l1ll11_opy_, bstack1lll1l1ll11_opy_ + bstack11ll1_opy_ (u"ࠤ࠽ࡷࡹࡧࡲࡵࠤឆ"), bstack1lll1l1ll11_opy_ + bstack11ll1_opy_ (u"ࠥ࠾ࡪࡴࡤࠣជ"),False, str(error))
    logger.info(bstack11ll1_opy_ (u"ࠦࡆࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠤࡹ࡫ࡳࡵ࡫ࡱ࡫ࠥ࡬࡯ࡳࠢࡷ࡬࡮ࡹࠠࡵࡧࡶࡸࠥࡩࡡࡴࡧࠣ࡬ࡦࡹࠠࡦࡰࡧࡩࡩ࠴ࠢឈ"))
    try:
      bstack1l11l11ll1l_opy_ = {
        bstack11ll1_opy_ (u"ࠧࡸࡥࡲࡷࡨࡷࡹࠨញ"): {
          bstack11ll1_opy_ (u"ࠨࡣࡰ࡯ࡰࡥࡳࡪࠢដ"): bstack11ll1_opy_ (u"ࠢࡂ࠳࠴࡝ࡤ࡙ࡁࡗࡇࡢࡖࡊ࡙ࡕࡍࡖࡖࠦឋ"),
        },
        bstack11ll1_opy_ (u"ࠣࡴࡨࡷࡵࡵ࡮ࡴࡧࠥឌ"): {
          bstack11ll1_opy_ (u"ࠤࡥࡳࡩࡿࠢឍ"): {
            bstack11ll1_opy_ (u"ࠥࡱࡸ࡭ࠢណ"): bstack11ll1_opy_ (u"ࠦࡆࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠤࡹ࡫ࡳࡵ࡫ࡱ࡫ࠥ࡬࡯ࡳࠢࡷ࡬࡮ࡹࠠࡵࡧࡶࡸࠥࡩࡡࡴࡧࠣ࡬ࡦࡹࠠࡦࡰࡧࡩࡩ࠴ࠢត"),
            bstack11ll1_opy_ (u"ࠧࡹࡵࡤࡥࡨࡷࡸࠨថ"): True
          }
        }
      }
      bstack11ll111l1l_opy_.info(json.dumps(bstack1l11l11ll1l_opy_, separators=(bstack11ll1_opy_ (u"࠭ࠬࠨទ"), bstack11ll1_opy_ (u"ࠧ࠻ࠩធ"))))
    except Exception as bstack1l11lll1_opy_:
      logger.debug(bstack11ll1_opy_ (u"ࠣࡈࡤ࡭ࡱ࡫ࡤࠡࡶࡲࠤࡱࡵࡧࠡࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠡࡵࡤࡺࡪࠦࡲࡦࡵࡸࡰࡹࡹࠠࡥࡣࡷࡥ࠿ࠦࠢន") + str(bstack1l11lll1_opy_) + bstack11ll1_opy_ (u"ࠤࠥប"))
  except Exception as bstack1l111ll1l1l_opy_:
    logger.error(bstack11ll1_opy_ (u"ࠥࡅࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠣࡶࡪࡹࡵ࡭ࡶࡶࠤࡨࡵࡵ࡭ࡦࠣࡲࡴࡺࠠࡣࡧࠣࡴࡷࡵࡣࡦࡵࡶࡩࡩࠦࡦࡰࡴࠣࡸ࡭࡫ࠠࡵࡧࡶࡸࠥࡩࡡࡴࡧ࠽ࠤࠧផ") + str(path) + bstack11ll1_opy_ (u"ࠦࠥࡋࡲࡳࡱࡵࠤ࠿ࠨព") + str(bstack1l111ll1l1l_opy_))
def bstack11ll11ll1l1_opy_(driver):
    caps = driver.capabilities
    if caps.get(bstack11ll1_opy_ (u"ࠧࡶ࡬ࡢࡶࡩࡳࡷࡳࡎࡢ࡯ࡨࠦភ")) and str(caps.get(bstack11ll1_opy_ (u"ࠨࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡏࡣࡰࡩࠧម"))).lower() == bstack11ll1_opy_ (u"ࠢࡢࡰࡧࡶࡴ࡯ࡤࠣយ"):
        bstack1l11l11111l_opy_ = caps.get(bstack11ll1_opy_ (u"ࠣࡣࡳࡴ࡮ࡻ࡭࠻ࡲ࡯ࡥࡹ࡬࡯ࡳ࡯࡙ࡩࡷࡹࡩࡰࡰࠥរ")) or caps.get(bstack11ll1_opy_ (u"ࠤࡳࡰࡦࡺࡦࡰࡴࡰ࡚ࡪࡸࡳࡪࡱࡱࠦល"))
        if bstack1l11l11111l_opy_ and int(str(bstack1l11l11111l_opy_)) < bstack11l1lllll1l_opy_:
            return False
    return True
def bstack1llll1l11l_opy_(config):
  if bstack11ll1_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠪវ") in config:
        return config[bstack11ll1_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠫឝ")]
  for platform in config.get(bstack11ll1_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨឞ"), []):
      if bstack11ll1_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾ࠭ស") in platform:
          return platform[bstack11ll1_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠧហ")]
  return None
def bstack1ll11l1lll_opy_(bstack111llll1l1_opy_):
  try:
    browser_name = bstack111llll1l1_opy_[bstack11ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡡࡱࡥࡲ࡫ࠧឡ")]
    browser_version = bstack111llll1l1_opy_[bstack11ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡢࡺࡪࡸࡳࡪࡱࡱࠫអ")]
    chrome_options = bstack111llll1l1_opy_[bstack11ll1_opy_ (u"ࠪࡧ࡭ࡸ࡯࡮ࡧࡢࡳࡵࡺࡩࡰࡰࡶࠫឣ")]
    try:
        bstack11l1lll1lll_opy_ = int(browser_version.split(bstack11ll1_opy_ (u"ࠫ࠳࠭ឤ"))[0])
    except ValueError as e:
        logger.error(bstack11ll1_opy_ (u"ࠧࡋࡲࡳࡱࡵࠤࡼ࡮ࡩ࡭ࡧࠣࡧࡴࡴࡶࡦࡴࡷ࡭ࡳ࡭ࠠࡣࡴࡲࡻࡸ࡫ࡲࠡࡸࡨࡶࡸ࡯࡯࡯ࠤឥ") + str(e))
        return False
    if not (browser_name and browser_name.lower() == bstack11ll1_opy_ (u"࠭ࡣࡩࡴࡲࡱࡪ࠭ឦ")):
        logger.warning(bstack11ll1_opy_ (u"ࠢࡂࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡂࡷࡷࡳࡲࡧࡴࡪࡱࡱࠤࡼ࡯࡬࡭ࠢࡵࡹࡳࠦ࡯࡯࡮ࡼࠤࡴࡴࠠࡄࡪࡵࡳࡲ࡫ࠠࡣࡴࡲࡻࡸ࡫ࡲࡴ࠰ࠥឧ"))
        return False
    if bstack11l1lll1lll_opy_ < bstack11ll11111l1_opy_.bstack1l11l11l1ll_opy_:
        logger.warning(bstack1l1ll111l1l_opy_ (u"ࠨࡃࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠡࡃࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࠥࡸࡥࡲࡷ࡬ࡶࡪࡹࠠࡄࡪࡵࡳࡲ࡫ࠠࡷࡧࡵࡷ࡮ࡵ࡮ࠡࡽࡆࡓࡓ࡙ࡔࡂࡐࡗࡗ࠳ࡓࡉࡏࡋࡐ࡙ࡒࡥࡎࡐࡐࡢࡆࡘ࡚ࡁࡄࡍࡢࡍࡓࡌࡒࡂࡡࡄ࠵࠶࡟࡟ࡔࡗࡓࡔࡔࡘࡔࡆࡆࡢࡇࡍࡘࡏࡎࡇࡢ࡚ࡊࡘࡓࡊࡑࡑࢁࠥࡵࡲࠡࡪ࡬࡫࡭࡫ࡲ࠯ࠩឨ"))
        return False
    if chrome_options and any(bstack11ll1_opy_ (u"ࠩ࠰࠱࡭࡫ࡡࡥ࡮ࡨࡷࡸ࠭ឩ") in value for value in chrome_options.values() if isinstance(value, str)):
        logger.warning(bstack11ll1_opy_ (u"ࠥࡅࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠣࡅࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࠠࡸ࡫࡯ࡰࠥࡴ࡯ࡵࠢࡵࡹࡳࠦ࡯࡯ࠢ࡯ࡩ࡬ࡧࡣࡺࠢ࡫ࡩࡦࡪ࡬ࡦࡵࡶࠤࡲࡵࡤࡦ࠰ࠣࡗࡼ࡯ࡴࡤࡪࠣࡸࡴࠦ࡮ࡦࡹࠣ࡬ࡪࡧࡤ࡭ࡧࡶࡷࠥࡳ࡯ࡥࡧࠣࡳࡷࠦࡡࡷࡱ࡬ࡨࠥࡻࡳࡪࡰࡪࠤ࡭࡫ࡡࡥ࡮ࡨࡷࡸࠦ࡭ࡰࡦࡨ࠲ࠧឪ"))
        return False
    return True
  except Exception as e:
    logger.error(bstack11ll1_opy_ (u"ࠦࡊࡸࡲࡰࡴࠣ࡭ࡳࠦࡣࡩࡧࡦ࡯࡮ࡴࡧࠡࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࠣࡷࡺࡶࡰࡰࡴࡷࠤ࡫ࡵࡲࠡ࡮ࡲࡧࡦࡲࠠࡄࡪࡵࡳࡲ࡫࠺ࠡࠤឫ") + str(e))
    return False
def bstack1l1l111l11_opy_(bstack1l1111lll_opy_, config):
    try:
      bstack1l11l1l111l_opy_ = bstack11ll1_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠬឬ") in config and config[bstack11ll1_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾ࠭ឭ")] == True
      bstack11ll111lll1_opy_ = bstack11ll1_opy_ (u"ࠧࡵࡷࡵࡦࡴ࡙ࡣࡢ࡮ࡨࠫឮ") in config and str(config[bstack11ll1_opy_ (u"ࠨࡶࡸࡶࡧࡵࡓࡤࡣ࡯ࡩࠬឯ")]).lower() != bstack11ll1_opy_ (u"ࠩࡩࡥࡱࡹࡥࠨឰ")
      if not (bstack1l11l1l111l_opy_ and (not bstack11lllll11l_opy_(config) or bstack11ll111lll1_opy_)):
        return bstack1l1111lll_opy_
      bstack11ll11ll111_opy_ = bstack1l11l111l1_opy_.bstack11ll11111ll_opy_
      if bstack11ll11ll111_opy_ is None:
        logger.debug(bstack11ll1_opy_ (u"ࠥࡋࡴࡵࡧ࡭ࡧࠣࡧ࡭ࡸ࡯࡮ࡧࠣࡳࡵࡺࡩࡰࡰࡶࠤࡦࡸࡥࠡࡐࡲࡲࡪࠨឱ"))
        return bstack1l1111lll_opy_
      bstack11ll11l11ll_opy_ = int(str(bstack11l1lll11ll_opy_()).split(bstack11ll1_opy_ (u"ࠫ࠳࠭ឲ"))[0])
      logger.debug(bstack11ll1_opy_ (u"࡙ࠧࡥ࡭ࡧࡱ࡭ࡺࡳࠠࡷࡧࡵࡷ࡮ࡵ࡮ࠡࡦࡨࡸࡪࡩࡴࡦࡦ࠽ࠤࠧឳ") + str(bstack11ll11l11ll_opy_) + bstack11ll1_opy_ (u"ࠨࠢ឴"))
      if bstack11ll11l11ll_opy_ == 3 and isinstance(bstack1l1111lll_opy_, dict) and bstack11ll1_opy_ (u"ࠧࡥࡧࡶ࡭ࡷ࡫ࡤࡠࡥࡤࡴࡦࡨࡩ࡭࡫ࡷ࡭ࡪࡹࠧ឵") in bstack1l1111lll_opy_ and bstack11ll11ll111_opy_ is not None:
        if bstack11ll1_opy_ (u"ࠨࡩࡲࡳ࡬ࡀࡣࡩࡴࡲࡱࡪࡕࡰࡵ࡫ࡲࡲࡸ࠭ា") not in bstack1l1111lll_opy_[bstack11ll1_opy_ (u"ࠩࡧࡩࡸ࡯ࡲࡦࡦࡢࡧࡦࡶࡡࡣ࡫࡯࡭ࡹ࡯ࡥࡴࠩិ")]:
          bstack1l1111lll_opy_[bstack11ll1_opy_ (u"ࠪࡨࡪࡹࡩࡳࡧࡧࡣࡨࡧࡰࡢࡤ࡬ࡰ࡮ࡺࡩࡦࡵࠪី")][bstack11ll1_opy_ (u"ࠫ࡬ࡵ࡯ࡨ࠼ࡦ࡬ࡷࡵ࡭ࡦࡑࡳࡸ࡮ࡵ࡮ࡴࠩឹ")] = {}
        if bstack11ll1_opy_ (u"ࠬࡧࡲࡨࡵࠪឺ") in bstack11ll11ll111_opy_:
          if bstack11ll1_opy_ (u"࠭ࡡࡳࡩࡶࠫុ") not in bstack1l1111lll_opy_[bstack11ll1_opy_ (u"ࠧࡥࡧࡶ࡭ࡷ࡫ࡤࡠࡥࡤࡴࡦࡨࡩ࡭࡫ࡷ࡭ࡪࡹࠧូ")][bstack11ll1_opy_ (u"ࠨࡩࡲࡳ࡬ࡀࡣࡩࡴࡲࡱࡪࡕࡰࡵ࡫ࡲࡲࡸ࠭ួ")]:
            bstack1l1111lll_opy_[bstack11ll1_opy_ (u"ࠩࡧࡩࡸ࡯ࡲࡦࡦࡢࡧࡦࡶࡡࡣ࡫࡯࡭ࡹ࡯ࡥࡴࠩើ")][bstack11ll1_opy_ (u"ࠪ࡫ࡴࡵࡧ࠻ࡥ࡫ࡶࡴࡳࡥࡐࡲࡷ࡭ࡴࡴࡳࠨឿ")][bstack11ll1_opy_ (u"ࠫࡦࡸࡧࡴࠩៀ")] = []
          for arg in bstack11ll11ll111_opy_[bstack11ll1_opy_ (u"ࠬࡧࡲࡨࡵࠪេ")]:
            if arg not in bstack1l1111lll_opy_[bstack11ll1_opy_ (u"࠭ࡤࡦࡵ࡬ࡶࡪࡪ࡟ࡤࡣࡳࡥࡧ࡯࡬ࡪࡶ࡬ࡩࡸ࠭ែ")][bstack11ll1_opy_ (u"ࠧࡨࡱࡲ࡫࠿ࡩࡨࡳࡱࡰࡩࡔࡶࡴࡪࡱࡱࡷࠬៃ")][bstack11ll1_opy_ (u"ࠨࡣࡵ࡫ࡸ࠭ោ")]:
              bstack1l1111lll_opy_[bstack11ll1_opy_ (u"ࠩࡧࡩࡸ࡯ࡲࡦࡦࡢࡧࡦࡶࡡࡣ࡫࡯࡭ࡹ࡯ࡥࡴࠩៅ")][bstack11ll1_opy_ (u"ࠪ࡫ࡴࡵࡧ࠻ࡥ࡫ࡶࡴࡳࡥࡐࡲࡷ࡭ࡴࡴࡳࠨំ")][bstack11ll1_opy_ (u"ࠫࡦࡸࡧࡴࠩះ")].append(arg)
        if bstack11ll1_opy_ (u"ࠬ࡫ࡸࡵࡧࡱࡷ࡮ࡵ࡮ࡴࠩៈ") in bstack11ll11ll111_opy_:
          if bstack11ll1_opy_ (u"࠭ࡥࡹࡶࡨࡲࡸ࡯࡯࡯ࡵࠪ៉") not in bstack1l1111lll_opy_[bstack11ll1_opy_ (u"ࠧࡥࡧࡶ࡭ࡷ࡫ࡤࡠࡥࡤࡴࡦࡨࡩ࡭࡫ࡷ࡭ࡪࡹࠧ៊")][bstack11ll1_opy_ (u"ࠨࡩࡲࡳ࡬ࡀࡣࡩࡴࡲࡱࡪࡕࡰࡵ࡫ࡲࡲࡸ࠭់")]:
            bstack1l1111lll_opy_[bstack11ll1_opy_ (u"ࠩࡧࡩࡸ࡯ࡲࡦࡦࡢࡧࡦࡶࡡࡣ࡫࡯࡭ࡹ࡯ࡥࡴࠩ៌")][bstack11ll1_opy_ (u"ࠪ࡫ࡴࡵࡧ࠻ࡥ࡫ࡶࡴࡳࡥࡐࡲࡷ࡭ࡴࡴࡳࠨ៍")][bstack11ll1_opy_ (u"ࠫࡪࡾࡴࡦࡰࡶ࡭ࡴࡴࡳࠨ៎")] = []
          for ext in bstack11ll11ll111_opy_[bstack11ll1_opy_ (u"ࠬ࡫ࡸࡵࡧࡱࡷ࡮ࡵ࡮ࡴࠩ៏")]:
            if ext not in bstack1l1111lll_opy_[bstack11ll1_opy_ (u"࠭ࡤࡦࡵ࡬ࡶࡪࡪ࡟ࡤࡣࡳࡥࡧ࡯࡬ࡪࡶ࡬ࡩࡸ࠭័")][bstack11ll1_opy_ (u"ࠧࡨࡱࡲ࡫࠿ࡩࡨࡳࡱࡰࡩࡔࡶࡴࡪࡱࡱࡷࠬ៑")][bstack11ll1_opy_ (u"ࠨࡧࡻࡸࡪࡴࡳࡪࡱࡱࡷ្ࠬ")]:
              bstack1l1111lll_opy_[bstack11ll1_opy_ (u"ࠩࡧࡩࡸ࡯ࡲࡦࡦࡢࡧࡦࡶࡡࡣ࡫࡯࡭ࡹ࡯ࡥࡴࠩ៓")][bstack11ll1_opy_ (u"ࠪ࡫ࡴࡵࡧ࠻ࡥ࡫ࡶࡴࡳࡥࡐࡲࡷ࡭ࡴࡴࡳࠨ។")][bstack11ll1_opy_ (u"ࠫࡪࡾࡴࡦࡰࡶ࡭ࡴࡴࡳࠨ៕")].append(ext)
        if bstack11ll1_opy_ (u"ࠬࡶࡲࡦࡨࡶࠫ៖") in bstack11ll11ll111_opy_:
          if bstack11ll1_opy_ (u"࠭ࡰࡳࡧࡩࡷࠬៗ") not in bstack1l1111lll_opy_[bstack11ll1_opy_ (u"ࠧࡥࡧࡶ࡭ࡷ࡫ࡤࡠࡥࡤࡴࡦࡨࡩ࡭࡫ࡷ࡭ࡪࡹࠧ៘")][bstack11ll1_opy_ (u"ࠨࡩࡲࡳ࡬ࡀࡣࡩࡴࡲࡱࡪࡕࡰࡵ࡫ࡲࡲࡸ࠭៙")]:
            bstack1l1111lll_opy_[bstack11ll1_opy_ (u"ࠩࡧࡩࡸ࡯ࡲࡦࡦࡢࡧࡦࡶࡡࡣ࡫࡯࡭ࡹ࡯ࡥࡴࠩ៚")][bstack11ll1_opy_ (u"ࠪ࡫ࡴࡵࡧ࠻ࡥ࡫ࡶࡴࡳࡥࡐࡲࡷ࡭ࡴࡴࡳࠨ៛")][bstack11ll1_opy_ (u"ࠫࡵࡸࡥࡧࡵࠪៜ")] = {}
          bstack11ll1111lll_opy_(bstack1l1111lll_opy_[bstack11ll1_opy_ (u"ࠬࡪࡥࡴ࡫ࡵࡩࡩࡥࡣࡢࡲࡤࡦ࡮ࡲࡩࡵ࡫ࡨࡷࠬ៝")][bstack11ll1_opy_ (u"࠭ࡧࡰࡱࡪ࠾ࡨ࡮ࡲࡰ࡯ࡨࡓࡵࡺࡩࡰࡰࡶࠫ៞")][bstack11ll1_opy_ (u"ࠧࡱࡴࡨࡪࡸ࠭៟")],
                    bstack11ll11ll111_opy_[bstack11ll1_opy_ (u"ࠨࡲࡵࡩ࡫ࡹࠧ០")])
        os.environ[bstack11ll1_opy_ (u"ࠩࡌࡗࡤࡔࡏࡏࡡࡅࡗ࡙ࡇࡃࡌࡡࡌࡒࡋࡘࡁࡠࡃ࠴࠵࡞ࡥࡓࡆࡕࡖࡍࡔࡔࠧ១")] = bstack11ll1_opy_ (u"ࠪࡸࡷࡻࡥࠨ២")
        return bstack1l1111lll_opy_
      else:
        chrome_options = None
        if isinstance(bstack1l1111lll_opy_, ChromeOptions):
          chrome_options = bstack1l1111lll_opy_
        elif isinstance(bstack1l1111lll_opy_, dict):
          for value in bstack1l1111lll_opy_.values():
            if isinstance(value, ChromeOptions):
              chrome_options = value
              break
        if chrome_options is None:
          chrome_options = ChromeOptions()
          if isinstance(bstack1l1111lll_opy_, dict):
            bstack1l1111lll_opy_[bstack11ll1_opy_ (u"ࠫࡴࡶࡴࡪࡱࡱࡷࠬ៣")] = chrome_options
          else:
            bstack1l1111lll_opy_ = chrome_options
        if bstack11ll11ll111_opy_ is not None:
          if bstack11ll1_opy_ (u"ࠬࡧࡲࡨࡵࠪ៤") in bstack11ll11ll111_opy_:
                bstack11ll11l1l1l_opy_ = chrome_options.arguments or []
                new_args = bstack11ll11ll111_opy_[bstack11ll1_opy_ (u"࠭ࡡࡳࡩࡶࠫ៥")]
                for arg in new_args:
                    if arg not in bstack11ll11l1l1l_opy_:
                        chrome_options.add_argument(arg)
          if bstack11ll1_opy_ (u"ࠧࡦࡺࡷࡩࡳࡹࡩࡰࡰࡶࠫ៦") in bstack11ll11ll111_opy_:
                existing_extensions = chrome_options.experimental_options.get(bstack11ll1_opy_ (u"ࠨࡧࡻࡸࡪࡴࡳࡪࡱࡱࡷࠬ៧"), [])
                bstack11l1llll11l_opy_ = bstack11ll11ll111_opy_[bstack11ll1_opy_ (u"ࠩࡨࡼࡹ࡫࡮ࡴ࡫ࡲࡲࡸ࠭៨")]
                for extension in bstack11l1llll11l_opy_:
                    if extension not in existing_extensions:
                        chrome_options.add_encoded_extension(extension)
          if bstack11ll1_opy_ (u"ࠪࡴࡷ࡫ࡦࡴࠩ៩") in bstack11ll11ll111_opy_:
                bstack11l1lllll11_opy_ = chrome_options.experimental_options.get(bstack11ll1_opy_ (u"ࠫࡵࡸࡥࡧࡵࠪ៪"), {})
                bstack11ll11lll11_opy_ = bstack11ll11ll111_opy_[bstack11ll1_opy_ (u"ࠬࡶࡲࡦࡨࡶࠫ៫")]
                bstack11ll1111lll_opy_(bstack11l1lllll11_opy_, bstack11ll11lll11_opy_)
                chrome_options.add_experimental_option(bstack11ll1_opy_ (u"࠭ࡰࡳࡧࡩࡷࠬ៬"), bstack11l1lllll11_opy_)
        os.environ[bstack11ll1_opy_ (u"ࠧࡊࡕࡢࡒࡔࡔ࡟ࡃࡕࡗࡅࡈࡑ࡟ࡊࡐࡉࡖࡆࡥࡁ࠲࠳࡜ࡣࡘࡋࡓࡔࡋࡒࡒࠬ៭")] = bstack11ll1_opy_ (u"ࠨࡶࡵࡹࡪ࠭៮")
        return bstack1l1111lll_opy_
    except Exception as e:
      logger.error(bstack11ll1_opy_ (u"ࠤࡈࡶࡷࡵࡲࠡࡹ࡫࡭ࡱ࡫ࠠࡢࡦࡧ࡭ࡳ࡭ࠠ࡯ࡱࡱ࠱ࡇ࡙ࠠࡪࡰࡩࡶࡦࠦࡡ࠲࠳ࡼࠤࡨ࡮ࡲࡰ࡯ࡨࠤࡴࡶࡴࡪࡱࡱࡷ࠿ࠦࠢ៯") + str(e))
      return bstack1l1111lll_opy_