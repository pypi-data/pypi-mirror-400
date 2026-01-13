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
import os
import json
import requests
import logging
import threading
import bstack_utils.constants as bstack11ll11l1ll1_opy_
from urllib.parse import urlparse
from bstack_utils.constants import bstack11ll111ll1l_opy_ as bstack11ll111lll1_opy_, EVENTS
from bstack_utils.bstack111lll1l_opy_ import bstack111lll1l_opy_
from bstack_utils.helper import bstack1lllll111_opy_, bstack1111ll1l1l_opy_, bstack11lll11ll1_opy_, bstack11ll111111l_opy_, \
  bstack11ll11ll1ll_opy_, bstack1l111l11l1_opy_, get_host_info, bstack11ll11l11l1_opy_, bstack1l111l111l_opy_, error_handler, bstack11l1lllll1l_opy_, bstack11ll11l1111_opy_, bstack11lll11l_opy_
from browserstack_sdk._version import __version__
from bstack_utils.bstack1l1lll1l11_opy_ import get_logger
from bstack_utils.bstack11l1l11ll_opy_ import bstack1lll1ll1l11_opy_
from selenium.webdriver.chrome.options import Options as ChromeOptions
from browserstack_sdk.sdk_cli.cli import cli
from bstack_utils.constants import *
from bstack_utils import bstack1l1lll1l11_opy_
logger = get_logger(__name__)
bstack1ll11l1ll_opy_ = bstack1l1lll1l11_opy_.bstack1l111111_opy_(__name__)
bstack11l1l11ll_opy_ = bstack1lll1ll1l11_opy_()
@error_handler(class_method=False)
def _11ll11ll11l_opy_(driver, bstack111111l1ll_opy_):
  response = {}
  try:
    caps = driver.capabilities
    response = {
        bstack11l1l_opy_ (u"ࠩࡲࡷࡤࡴࡡ࡮ࡧࠪᚭ"): caps.get(bstack11l1l_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡓࡧ࡭ࡦࠩᚮ"), None),
        bstack11l1l_opy_ (u"ࠫࡴࡹ࡟ࡷࡧࡵࡷ࡮ࡵ࡮ࠨᚯ"): bstack111111l1ll_opy_.get(bstack11l1l_opy_ (u"ࠬࡵࡳࡗࡧࡵࡷ࡮ࡵ࡮ࠨᚰ"), None),
        bstack11l1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸ࡟࡯ࡣࡰࡩࠬᚱ"): caps.get(bstack11l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡏࡣࡰࡩࠬᚲ"), None),
        bstack11l1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡡࡹࡩࡷࡹࡩࡰࡰࠪᚳ"): caps.get(bstack11l1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴ࡙ࡩࡷࡹࡩࡰࡰࠪᚴ"), None)
    }
  except Exception as error:
    logger.debug(bstack11l1l_opy_ (u"ࠪࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡩ࡯ࠢࡩࡩࡹࡩࡨࡪࡰࡪࠤࡵࡲࡡࡵࡨࡲࡶࡲࠦࡤࡦࡶࡤ࡭ࡱࡹࠠࡸ࡫ࡷ࡬ࠥ࡫ࡲࡳࡱࡵࠤ࠿ࠦࠧᚵ") + str(error))
  return response
def on():
    if os.environ.get(bstack11l1l_opy_ (u"ࠫࡇ࡙࡟ࡂ࠳࠴࡝ࡤࡐࡗࡕࠩᚶ"), None) is None or os.environ[bstack11l1l_opy_ (u"ࠬࡈࡓࡠࡃ࠴࠵࡞ࡥࡊࡘࡖࠪᚷ")] == bstack11l1l_opy_ (u"ࠨ࡮ࡶ࡮࡯ࠦᚸ"):
        return False
    return True
def bstack1111111l1_opy_(config):
  return config.get(bstack11l1l_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠧᚹ"), False) or any([p.get(bstack11l1l_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠨᚺ"), False) == True for p in config.get(bstack11l1l_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬᚻ"), [])])
def bstack11l11ll1_opy_(config, bstack1ll11111l1_opy_):
  try:
    bstack11ll111ll11_opy_ = config.get(bstack11l1l_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠪᚼ"), False)
    if int(bstack1ll11111l1_opy_) < len(config.get(bstack11l1l_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧᚽ"), [])) and config[bstack11l1l_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨᚾ")][bstack1ll11111l1_opy_]:
      bstack11l1lllll11_opy_ = config[bstack11l1l_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩᚿ")][bstack1ll11111l1_opy_].get(bstack11l1l_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠧᛀ"), None)
    else:
      bstack11l1lllll11_opy_ = config.get(bstack11l1l_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠨᛁ"), None)
    if bstack11l1lllll11_opy_ != None:
      bstack11ll111ll11_opy_ = bstack11l1lllll11_opy_
    bstack11ll11lll11_opy_ = os.getenv(bstack11l1l_opy_ (u"ࠩࡅࡗࡤࡇ࠱࠲࡛ࡢࡎ࡜࡚ࠧᛂ")) is not None and len(os.getenv(bstack11l1l_opy_ (u"ࠪࡆࡘࡥࡁ࠲࠳࡜ࡣࡏ࡝ࡔࠨᛃ"))) > 0 and os.getenv(bstack11l1l_opy_ (u"ࠫࡇ࡙࡟ࡂ࠳࠴࡝ࡤࡐࡗࡕࠩᛄ")) != bstack11l1l_opy_ (u"ࠬࡴࡵ࡭࡮ࠪᛅ")
    return bstack11ll111ll11_opy_ and bstack11ll11lll11_opy_
  except Exception as error:
    logger.debug(bstack11l1l_opy_ (u"࠭ࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢ࡬ࡲࠥࡼࡥࡳ࡫ࡩࡽ࡮ࡴࡧࠡࡶ࡫ࡩࠥࡇࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡹࡥࡴࡵ࡬ࡳࡳࠦࡷࡪࡶ࡫ࠤࡪࡸࡲࡰࡴࠣ࠾ࠥ࠭ᛆ") + str(error))
  return False
def bstack1l11l11l_opy_(test_tags):
  bstack1l1lll11ll1_opy_ = os.getenv(bstack11l1l_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡣࡆࡉࡃࡆࡕࡖࡍࡇࡏࡌࡊࡖ࡜ࡣࡈࡕࡎࡇࡋࡊ࡙ࡗࡇࡔࡊࡑࡑࡣ࡞ࡓࡌࠨᛇ"))
  if bstack1l1lll11ll1_opy_ is None:
    return True
  bstack1l1lll11ll1_opy_ = json.loads(bstack1l1lll11ll1_opy_)
  try:
    include_tags = bstack1l1lll11ll1_opy_[bstack11l1l_opy_ (u"ࠨ࡫ࡱࡧࡱࡻࡤࡦࡖࡤ࡫ࡸࡏ࡮ࡕࡧࡶࡸ࡮ࡴࡧࡔࡥࡲࡴࡪ࠭ᛈ")] if bstack11l1l_opy_ (u"ࠩ࡬ࡲࡨࡲࡵࡥࡧࡗࡥ࡬ࡹࡉ࡯ࡖࡨࡷࡹ࡯࡮ࡨࡕࡦࡳࡵ࡫ࠧᛉ") in bstack1l1lll11ll1_opy_ and isinstance(bstack1l1lll11ll1_opy_[bstack11l1l_opy_ (u"ࠪ࡭ࡳࡩ࡬ࡶࡦࡨࡘࡦ࡭ࡳࡊࡰࡗࡩࡸࡺࡩ࡯ࡩࡖࡧࡴࡶࡥࠨᛊ")], list) else []
    exclude_tags = bstack1l1lll11ll1_opy_[bstack11l1l_opy_ (u"ࠫࡪࡾࡣ࡭ࡷࡧࡩ࡙ࡧࡧࡴࡋࡱࡘࡪࡹࡴࡪࡰࡪࡗࡨࡵࡰࡦࠩᛋ")] if bstack11l1l_opy_ (u"ࠬ࡫ࡸࡤ࡮ࡸࡨࡪ࡚ࡡࡨࡵࡌࡲ࡙࡫ࡳࡵ࡫ࡱ࡫ࡘࡩ࡯ࡱࡧࠪᛌ") in bstack1l1lll11ll1_opy_ and isinstance(bstack1l1lll11ll1_opy_[bstack11l1l_opy_ (u"࠭ࡥࡹࡥ࡯ࡹࡩ࡫ࡔࡢࡩࡶࡍࡳ࡚ࡥࡴࡶ࡬ࡲ࡬࡙ࡣࡰࡲࡨࠫᛍ")], list) else []
    excluded = any(tag in exclude_tags for tag in test_tags)
    included = len(include_tags) == 0 or any(tag in include_tags for tag in test_tags)
    return not excluded and included
  except Exception as error:
    logger.debug(bstack11l1l_opy_ (u"ࠢࡆࡴࡵࡳࡷࠦࡷࡩ࡫࡯ࡩࠥࡼࡡ࡭࡫ࡧࡥࡹ࡯࡮ࡨࠢࡷࡩࡸࡺࠠࡤࡣࡶࡩࠥ࡬࡯ࡳࠢࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠢࡥࡩ࡫ࡵࡲࡦࠢࡶࡧࡦࡴ࡮ࡪࡰࡪ࠲ࠥࡋࡲࡳࡱࡵࠤ࠿ࠦࠢᛎ") + str(error))
  return False
def bstack11l1lll11ll_opy_(config, bstack11l1llllll1_opy_, bstack11l1lll1ll1_opy_, bstack11ll1111ll1_opy_):
  bstack11l1lll1l1l_opy_ = bstack11ll111111l_opy_(config)
  bstack11ll111l11l_opy_ = bstack11ll11ll1ll_opy_(config)
  if bstack11l1lll1l1l_opy_ is None or bstack11ll111l11l_opy_ is None:
    logger.error(bstack11l1l_opy_ (u"ࠨࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤࡼ࡮ࡩ࡭ࡧࠣࡧࡷ࡫ࡡࡵ࡫ࡱ࡫ࠥࡺࡥࡴࡶࠣࡶࡺࡴࠠࡧࡱࡵࠤࡇࡸ࡯ࡸࡵࡨࡶࡘࡺࡡࡤ࡭ࠣࡅࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠣࡅࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴ࠺ࠡࡏ࡬ࡷࡸ࡯࡮ࡨࠢࡤࡹࡹ࡮ࡥ࡯ࡶ࡬ࡧࡦࡺࡩࡰࡰࠣࡸࡴࡱࡥ࡯ࠩᛏ"))
    return [None, None]
  try:
    settings = json.loads(os.getenv(bstack11l1l_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡥࡁࡄࡅࡈࡗࡘࡏࡂࡊࡎࡌࡘ࡞ࡥࡃࡐࡐࡉࡍࡌ࡛ࡒࡂࡖࡌࡓࡓࡥ࡙ࡎࡎࠪᛐ"), bstack11l1l_opy_ (u"ࠪࡿࢂ࠭ᛑ")))
    data = {
        bstack11l1l_opy_ (u"ࠫࡵࡸ࡯࡫ࡧࡦࡸࡓࡧ࡭ࡦࠩᛒ"): config[bstack11l1l_opy_ (u"ࠬࡶࡲࡰ࡬ࡨࡧࡹࡔࡡ࡮ࡧࠪᛓ")],
        bstack11l1l_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡓࡧ࡭ࡦࠩᛔ"): config.get(bstack11l1l_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡔࡡ࡮ࡧࠪᛕ"), os.path.basename(os.getcwd())),
        bstack11l1l_opy_ (u"ࠨࡵࡷࡥࡷࡺࡔࡪ࡯ࡨࠫᛖ"): bstack1lllll111_opy_(),
        bstack11l1l_opy_ (u"ࠩࡧࡩࡸࡩࡲࡪࡲࡷ࡭ࡴࡴࠧᛗ"): config.get(bstack11l1l_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡆࡨࡷࡨࡸࡩࡱࡶ࡬ࡳࡳ࠭ᛘ"), bstack11l1l_opy_ (u"ࠫࠬᛙ")),
        bstack11l1l_opy_ (u"ࠬࡹ࡯ࡶࡴࡦࡩࠬᛚ"): {
            bstack11l1l_opy_ (u"࠭ࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡐࡤࡱࡪ࠭ᛛ"): bstack11l1llllll1_opy_,
            bstack11l1l_opy_ (u"ࠧࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭࡙ࡩࡷࡹࡩࡰࡰࠪᛜ"): bstack11l1lll1ll1_opy_,
            bstack11l1l_opy_ (u"ࠨࡵࡧ࡯࡛࡫ࡲࡴ࡫ࡲࡲࠬᛝ"): __version__,
            bstack11l1l_opy_ (u"ࠩ࡯ࡥࡳ࡭ࡵࡢࡩࡨࠫᛞ"): bstack11l1l_opy_ (u"ࠪࡴࡾࡺࡨࡰࡰࠪᛟ"),
            bstack11l1l_opy_ (u"ࠫࡹ࡫ࡳࡵࡈࡵࡥࡲ࡫ࡷࡰࡴ࡮ࠫᛠ"): bstack11l1l_opy_ (u"ࠬࡹࡥ࡭ࡧࡱ࡭ࡺࡳࠧᛡ"),
            bstack11l1l_opy_ (u"࠭ࡴࡦࡵࡷࡊࡷࡧ࡭ࡦࡹࡲࡶࡰ࡜ࡥࡳࡵ࡬ࡳࡳ࠭ᛢ"): bstack11ll1111ll1_opy_
        },
        bstack11l1l_opy_ (u"ࠧࡴࡧࡷࡸ࡮ࡴࡧࡴࠩᛣ"): settings,
        bstack11l1l_opy_ (u"ࠨࡸࡨࡶࡸ࡯࡯࡯ࡅࡲࡲࡹࡸ࡯࡭ࠩᛤ"): bstack11ll11l11l1_opy_(),
        bstack11l1l_opy_ (u"ࠩࡦ࡭ࡎࡴࡦࡰࠩᛥ"): bstack1l111l11l1_opy_(),
        bstack11l1l_opy_ (u"ࠪ࡬ࡴࡹࡴࡊࡰࡩࡳࠬᛦ"): get_host_info(),
        bstack11l1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡄࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳ࠭ᛧ"): bstack11lll11ll1_opy_(config)
    }
    headers = {
        bstack11l1l_opy_ (u"ࠬࡉ࡯࡯ࡶࡨࡲࡹ࠳ࡔࡺࡲࡨࠫᛨ"): bstack11l1l_opy_ (u"࠭ࡡࡱࡲ࡯࡭ࡨࡧࡴࡪࡱࡱ࠳࡯ࡹ࡯࡯ࠩᛩ"),
    }
    config = {
        bstack11l1l_opy_ (u"ࠧࡢࡷࡷ࡬ࠬᛪ"): (bstack11l1lll1l1l_opy_, bstack11ll111l11l_opy_),
        bstack11l1l_opy_ (u"ࠨࡪࡨࡥࡩ࡫ࡲࡴࠩ᛫"): headers
    }
    response = bstack1l111l111l_opy_(bstack11l1l_opy_ (u"ࠩࡓࡓࡘ࡚ࠧ᛬"), bstack11ll111lll1_opy_ + bstack11l1l_opy_ (u"ࠪ࠳ࡻ࠸࠯ࡵࡧࡶࡸࡤࡸࡵ࡯ࡵࠪ᛭"), data, config)
    bstack11ll11ll111_opy_ = response.json()
    if bstack11ll11ll111_opy_[bstack11l1l_opy_ (u"ࠫࡸࡻࡣࡤࡧࡶࡷࠬᛮ")]:
      parsed = json.loads(os.getenv(bstack11l1l_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡡࡄࡇࡈࡋࡓࡔࡋࡅࡍࡑࡏࡔ࡚ࡡࡆࡓࡓࡌࡉࡈࡗࡕࡅ࡙ࡏࡏࡏࡡ࡜ࡑࡑ࠭ᛯ"), bstack11l1l_opy_ (u"࠭ࡻࡾࠩᛰ")))
      parsed[bstack11l1l_opy_ (u"ࠧࡴࡥࡤࡲࡳ࡫ࡲࡗࡧࡵࡷ࡮ࡵ࡮ࠨᛱ")] = bstack11ll11ll111_opy_[bstack11l1l_opy_ (u"ࠨࡦࡤࡸࡦ࠭ᛲ")][bstack11l1l_opy_ (u"ࠩࡶࡧࡦࡴ࡮ࡦࡴ࡙ࡩࡷࡹࡩࡰࡰࠪᛳ")]
      os.environ[bstack11l1l_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡉࡘ࡚࡟ࡂࡅࡆࡉࡘ࡙ࡉࡃࡋࡏࡍ࡙࡟࡟ࡄࡑࡑࡊࡎࡍࡕࡓࡃࡗࡍࡔࡔ࡟࡚ࡏࡏࠫᛴ")] = json.dumps(parsed)
      bstack111lll1l_opy_.bstack1111ll1ll_opy_(bstack11ll11ll111_opy_[bstack11l1l_opy_ (u"ࠫࡩࡧࡴࡢࠩᛵ")][bstack11l1l_opy_ (u"ࠬࡹࡣࡳ࡫ࡳࡸࡸ࠭ᛶ")])
      bstack111lll1l_opy_.bstack11ll11111ll_opy_(bstack11ll11ll111_opy_[bstack11l1l_opy_ (u"࠭ࡤࡢࡶࡤࠫᛷ")][bstack11l1l_opy_ (u"ࠧࡤࡱࡰࡱࡦࡴࡤࡴࠩᛸ")])
      bstack111lll1l_opy_.store()
      return bstack11ll11ll111_opy_[bstack11l1l_opy_ (u"ࠨࡦࡤࡸࡦ࠭᛹")][bstack11l1l_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࡖࡲ࡯ࡪࡴࠧ᛺")], bstack11ll11ll111_opy_[bstack11l1l_opy_ (u"ࠪࡨࡦࡺࡡࠨ᛻")][bstack11l1l_opy_ (u"ࠫ࡮ࡪࠧ᛼")]
    else:
      logger.error(bstack11l1l_opy_ (u"ࠬࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡࡹ࡫࡭ࡱ࡫ࠠࡳࡷࡱࡲ࡮ࡴࡧࠡࡄࡵࡳࡼࡹࡥࡳࡕࡷࡥࡨࡱࠠࡂࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡂࡷࡷࡳࡲࡧࡴࡪࡱࡱ࠾ࠥ࠭᛽") + bstack11ll11ll111_opy_[bstack11l1l_opy_ (u"࠭࡭ࡦࡵࡶࡥ࡬࡫ࠧ᛾")])
      if bstack11ll11ll111_opy_[bstack11l1l_opy_ (u"ࠧ࡮ࡧࡶࡷࡦ࡭ࡥࠨ᛿")] == bstack11l1l_opy_ (u"ࠨࡋࡱࡺࡦࡲࡩࡥࠢࡦࡳࡳ࡬ࡩࡨࡷࡵࡥࡹ࡯࡯࡯ࠢࡳࡥࡸࡹࡥࡥ࠰ࠪᜀ"):
        for bstack11ll111l111_opy_ in bstack11ll11ll111_opy_[bstack11l1l_opy_ (u"ࠩࡨࡶࡷࡵࡲࡴࠩᜁ")]:
          logger.error(bstack11ll111l111_opy_[bstack11l1l_opy_ (u"ࠪࡱࡪࡹࡳࡢࡩࡨࠫᜂ")])
      return None, None
  except Exception as error:
    logger.error(bstack11l1l_opy_ (u"ࠦࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡸࡪ࡬ࡰࡪࠦࡣࡳࡧࡤࡸ࡮ࡴࡧࠡࡶࡨࡷࡹࠦࡲࡶࡰࠣࡪࡴࡸࠠࡃࡴࡲࡻࡸ࡫ࡲࡔࡶࡤࡧࡰࠦࡁࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࠦࡁࡶࡶࡲࡱࡦࡺࡩࡰࡰ࠽ࠤࠧᜃ") +  str(error))
    return None, None
def bstack11l1lll1l11_opy_():
  if os.getenv(bstack11l1l_opy_ (u"ࠬࡈࡓࡠࡃ࠴࠵࡞ࡥࡊࡘࡖࠪᜄ")) is None:
    return {
        bstack11l1l_opy_ (u"࠭ࡳࡵࡣࡷࡹࡸ࠭ᜅ"): bstack11l1l_opy_ (u"ࠧࡦࡴࡵࡳࡷ࠭ᜆ"),
        bstack11l1l_opy_ (u"ࠨ࡯ࡨࡷࡸࡧࡧࡦࠩᜇ"): bstack11l1l_opy_ (u"ࠩࡅࡹ࡮ࡲࡤࠡࡥࡵࡩࡦࡺࡩࡰࡰࠣ࡬ࡦࡪࠠࡧࡣ࡬ࡰࡪࡪ࠮ࠨᜈ")
    }
  data = {bstack11l1l_opy_ (u"ࠪࡩࡳࡪࡔࡪ࡯ࡨࠫᜉ"): bstack1lllll111_opy_()}
  headers = {
      bstack11l1l_opy_ (u"ࠫࡆࡻࡴࡩࡱࡵ࡭ࡿࡧࡴࡪࡱࡱࠫᜊ"): bstack11l1l_opy_ (u"ࠬࡈࡥࡢࡴࡨࡶࠥ࠭ᜋ") + os.getenv(bstack11l1l_opy_ (u"ࠨࡂࡔࡡࡄ࠵࠶࡟࡟ࡋ࡙ࡗࠦᜌ")),
      bstack11l1l_opy_ (u"ࠧࡄࡱࡱࡸࡪࡴࡴ࠮ࡖࡼࡴࡪ࠭ᜍ"): bstack11l1l_opy_ (u"ࠨࡣࡳࡴࡱ࡯ࡣࡢࡶ࡬ࡳࡳ࠵ࡪࡴࡱࡱࠫᜎ")
  }
  response = bstack1l111l111l_opy_(bstack11l1l_opy_ (u"ࠩࡓ࡙࡙࠭ᜏ"), bstack11ll111lll1_opy_ + bstack11l1l_opy_ (u"ࠪ࠳ࡹ࡫ࡳࡵࡡࡵࡹࡳࡹ࠯ࡴࡶࡲࡴࠬᜐ"), data, { bstack11l1l_opy_ (u"ࠫ࡭࡫ࡡࡥࡧࡵࡷࠬᜑ"): headers })
  try:
    if response.status_code == 200:
      logger.info(bstack11l1l_opy_ (u"ࠧࡈࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࠤࡆࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠤࡆࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠡࡖࡨࡷࡹࠦࡒࡶࡰࠣࡱࡦࡸ࡫ࡦࡦࠣࡥࡸࠦࡣࡰ࡯ࡳࡰࡪࡺࡥࡥࠢࡤࡸࠥࠨᜒ") + bstack1111ll1l1l_opy_().isoformat() + bstack11l1l_opy_ (u"࡚࠭ࠨᜓ"))
      return {bstack11l1l_opy_ (u"ࠧࡴࡶࡤࡸࡺࡹ᜔ࠧ"): bstack11l1l_opy_ (u"ࠨࡵࡸࡧࡨ࡫ࡳࡴ᜕ࠩ"), bstack11l1l_opy_ (u"ࠩࡰࡩࡸࡹࡡࡨࡧࠪ᜖"): bstack11l1l_opy_ (u"ࠪࠫ᜗")}
    else:
      response.raise_for_status()
  except requests.RequestException as error:
    logger.error(bstack11l1l_opy_ (u"ࠦࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡸࡪ࡬ࡰࡪࠦ࡭ࡢࡴ࡮࡭ࡳ࡭ࠠࡤࡱࡰࡴࡱ࡫ࡴࡪࡱࡱࠤࡴ࡬ࠠࡃࡴࡲࡻࡸ࡫ࡲࡔࡶࡤࡧࡰࠦࡁࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࠦࡁࡶࡶࡲࡱࡦࡺࡩࡰࡰࠣࡘࡪࡹࡴࠡࡔࡸࡲ࠿ࠦࠢ᜘") + str(error))
    return {
        bstack11l1l_opy_ (u"ࠬࡹࡴࡢࡶࡸࡷࠬ᜙"): bstack11l1l_opy_ (u"࠭ࡥࡳࡴࡲࡶࠬ᜚"),
        bstack11l1l_opy_ (u"ࠧ࡮ࡧࡶࡷࡦ࡭ࡥࠨ᜛"): str(error)
    }
def bstack11ll11ll1l1_opy_(bstack11ll1111lll_opy_):
    return re.match(bstack11l1l_opy_ (u"ࡳࠩࡡࡠࡩ࠱ࠨ࡝࠰࡟ࡨ࠰࠯࠿ࠥࠩ᜜"), bstack11ll1111lll_opy_.strip()) is not None
def bstack11111ll11_opy_(caps, options, desired_capabilities={}, config=None):
    try:
        if options:
          bstack11l1llll1l1_opy_ = options.to_capabilities()
        elif desired_capabilities:
          bstack11l1llll1l1_opy_ = desired_capabilities
        else:
          bstack11l1llll1l1_opy_ = {}
        bstack1ll1111ll11_opy_ = (bstack11l1llll1l1_opy_.get(bstack11l1l_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡒࡦࡳࡥࠨ᜝"), bstack11l1l_opy_ (u"ࠪࠫ᜞")).lower() or caps.get(bstack11l1l_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡔࡡ࡮ࡧࠪᜟ"), bstack11l1l_opy_ (u"ࠬ࠭ᜠ")).lower())
        if bstack1ll1111ll11_opy_ == bstack11l1l_opy_ (u"࠭ࡩࡰࡵࠪᜡ"):
            return True
        if bstack1ll1111ll11_opy_ == bstack11l1l_opy_ (u"ࠧࡢࡰࡧࡶࡴ࡯ࡤࠨᜢ"):
            bstack1ll1111llll_opy_ = str(float(caps.get(bstack11l1l_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯࡙ࡩࡷࡹࡩࡰࡰࠪᜣ")) or bstack11l1llll1l1_opy_.get(bstack11l1l_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬࠼ࡲࡴࡹ࡯࡯࡯ࡵࠪᜤ"), {}).get(bstack11l1l_opy_ (u"ࠪࡳࡸ࡜ࡥࡳࡵ࡬ࡳࡳ࠭ᜥ"),bstack11l1l_opy_ (u"ࠫࠬᜦ"))))
            if bstack1ll1111ll11_opy_ == bstack11l1l_opy_ (u"ࠬࡧ࡮ࡥࡴࡲ࡭ࡩ࠭ᜧ") and int(bstack1ll1111llll_opy_.split(bstack11l1l_opy_ (u"࠭࠮ࠨᜨ"))[0]) < float(bstack11l1llll1ll_opy_):
                logger.warning(str(bstack11ll1111111_opy_))
                return False
            return True
        bstack1l1llll1l1l_opy_ = caps.get(bstack11l1l_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱ࠺ࡰࡲࡷ࡭ࡴࡴࡳࠨᜩ"), {}).get(bstack11l1l_opy_ (u"ࠨࡦࡨࡺ࡮ࡩࡥࡏࡣࡰࡩࠬᜪ"), caps.get(bstack11l1l_opy_ (u"ࠩࡧࡩࡻ࡯ࡣࡦࠩᜫ"), bstack11l1l_opy_ (u"ࠪࠫᜬ")))
        if bstack1l1llll1l1l_opy_:
            logger.warning(bstack11l1l_opy_ (u"ࠦࡆࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠤࡆࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠡࡹ࡬ࡰࡱࠦࡲࡶࡰࠣࡳࡳࡲࡹࠡࡱࡱࠤࡉ࡫ࡳ࡬ࡶࡲࡴࠥࡨࡲࡰࡹࡶࡩࡷࡹ࠮ࠣᜭ"))
            return False
        browser = caps.get(bstack11l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡔࡡ࡮ࡧࠪᜮ"), bstack11l1l_opy_ (u"࠭ࠧᜯ")).lower() or bstack11l1llll1l1_opy_.get(bstack11l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡏࡣࡰࡩࠬᜰ"), bstack11l1l_opy_ (u"ࠨࠩᜱ")).lower()
        if browser != bstack11l1l_opy_ (u"ࠩࡦ࡬ࡷࡵ࡭ࡦࠩᜲ"):
            logger.warning(bstack11l1l_opy_ (u"ࠥࡅࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠣࡅࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࠠࡸ࡫࡯ࡰࠥࡸࡵ࡯ࠢࡲࡲࡱࡿࠠࡰࡰࠣࡇ࡭ࡸ࡯࡮ࡧࠣࡦࡷࡵࡷࡴࡧࡵࡷ࠳ࠨᜳ"))
            return False
        browser_version = caps.get(bstack11l1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶ࡛࡫ࡲࡴ࡫ࡲࡲ᜴ࠬ")) or caps.get(bstack11l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡥࡶࡦࡴࡶ࡭ࡴࡴࠧ᜵")) or bstack11l1llll1l1_opy_.get(bstack11l1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡖࡦࡴࡶ࡭ࡴࡴࠧ᜶")) or bstack11l1llll1l1_opy_.get(bstack11l1l_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱ࠺ࡰࡲࡷ࡭ࡴࡴࡳࠨ᜷"), {}).get(bstack11l1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡘࡨࡶࡸ࡯࡯࡯ࠩ᜸")) or bstack11l1llll1l1_opy_.get(bstack11l1l_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬࠼ࡲࡴࡹ࡯࡯࡯ࡵࠪ᜹"), {}).get(bstack11l1l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡣࡻ࡫ࡲࡴ࡫ࡲࡲࠬ᜺"))
        bstack1l1lll1l111_opy_ = bstack11ll11l1ll1_opy_.bstack1ll11l111l1_opy_
        bstack11ll11lll1l_opy_ = False
        if config is not None:
          bstack11ll11lll1l_opy_ = bstack11l1l_opy_ (u"ࠫࡹࡻࡲࡣࡱࡖࡧࡦࡲࡥࠨ᜻") in config and str(config[bstack11l1l_opy_ (u"ࠬࡺࡵࡳࡤࡲࡗࡨࡧ࡬ࡦࠩ᜼")]).lower() != bstack11l1l_opy_ (u"࠭ࡦࡢ࡮ࡶࡩࠬ᜽")
        if os.environ.get(bstack11l1l_opy_ (u"ࠧࡊࡕࡢࡒࡔࡔ࡟ࡃࡕࡗࡅࡈࡑ࡟ࡊࡐࡉࡖࡆࡥࡁ࠲࠳࡜ࡣࡘࡋࡓࡔࡋࡒࡒࠬ᜾"), bstack11l1l_opy_ (u"ࠨࠩ᜿")).lower() == bstack11l1l_opy_ (u"ࠩࡷࡶࡺ࡫ࠧᝀ") or bstack11ll11lll1l_opy_:
          bstack1l1lll1l111_opy_ = bstack11ll11l1ll1_opy_.bstack1l1lll11l1l_opy_
        if browser_version and browser_version != bstack11l1l_opy_ (u"ࠪࡰࡦࡺࡥࡴࡶࠪᝁ") and int(browser_version.split(bstack11l1l_opy_ (u"ࠫ࠳࠭ᝂ"))[0]) <= bstack1l1lll1l111_opy_:
          logger.warning(bstack1ll1l11l1ll_opy_ (u"ࠬࡇࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡇࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࠢࡺ࡭ࡱࡲࠠࡳࡷࡱࠤࡴࡴ࡬ࡺࠢࡲࡲࠥࡉࡨࡳࡱࡰࡩࠥࡨࡲࡰࡹࡶࡩࡷࠦࡶࡦࡴࡶ࡭ࡴࡴࠠࡨࡴࡨࡥࡹ࡫ࡲࠡࡶ࡫ࡥࡳࠦࡻ࡮࡫ࡱࡣࡦ࠷࠱ࡺࡡࡶࡹࡵࡶ࡯ࡳࡶࡨࡨࡤࡩࡨࡳࡱࡰࡩࡤࡼࡥࡳࡵ࡬ࡳࡳࢃ࠮ࠨᝃ"))
          return False
        if not options:
          bstack1ll111lll11_opy_ = caps.get(bstack11l1l_opy_ (u"࠭ࡧࡰࡱࡪ࠾ࡨ࡮ࡲࡰ࡯ࡨࡓࡵࡺࡩࡰࡰࡶࠫᝄ")) or bstack11l1llll1l1_opy_.get(bstack11l1l_opy_ (u"ࠧࡨࡱࡲ࡫࠿ࡩࡨࡳࡱࡰࡩࡔࡶࡴࡪࡱࡱࡷࠬᝅ"), {})
          if bstack11l1l_opy_ (u"ࠨ࠯࠰࡬ࡪࡧࡤ࡭ࡧࡶࡷࠬᝆ") in bstack1ll111lll11_opy_.get(bstack11l1l_opy_ (u"ࠩࡤࡶ࡬ࡹࠧᝇ"), []):
              logger.warning(bstack11l1l_opy_ (u"ࠥࡅࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠣࡅࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࠠࡸ࡫࡯ࡰࠥࡴ࡯ࡵࠢࡵࡹࡳࠦ࡯࡯ࠢ࡯ࡩ࡬ࡧࡣࡺࠢ࡫ࡩࡦࡪ࡬ࡦࡵࡶࠤࡲࡵࡤࡦ࠰ࠣࡗࡼ࡯ࡴࡤࡪࠣࡸࡴࠦ࡮ࡦࡹࠣ࡬ࡪࡧࡤ࡭ࡧࡶࡷࠥࡳ࡯ࡥࡧࠣࡳࡷࠦࡡࡷࡱ࡬ࡨࠥࡻࡳࡪࡰࡪࠤ࡭࡫ࡡࡥ࡮ࡨࡷࡸࠦ࡭ࡰࡦࡨ࠲ࠧᝈ"))
              return False
        return True
    except Exception as error:
        logger.debug(bstack11l1l_opy_ (u"ࠦࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡪࡰࠣࡺࡦࡲࡩࡥࡣࡷࡩࠥࡧ࠱࠲ࡻࠣࡷࡺࡶࡰࡰࡴࡷࠤ࠿ࠨᝉ") + str(error))
        return False
def set_capabilities(caps, config):
  try:
    bstack1ll1ll1lll1_opy_ = config.get(bstack11l1l_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࡔࡶࡴࡪࡱࡱࡷࠬᝊ"), {})
    bstack1ll1ll1lll1_opy_[bstack11l1l_opy_ (u"࠭ࡡࡶࡶ࡫ࡘࡴࡱࡥ࡯ࠩᝋ")] = os.getenv(bstack11l1l_opy_ (u"ࠧࡃࡕࡢࡅ࠶࠷࡙ࡠࡌ࡚ࡘࠬᝌ"))
    bstack11ll11111l1_opy_ = json.loads(os.getenv(bstack11l1l_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡤࡇࡃࡄࡇࡖࡗࡎࡈࡉࡍࡋࡗ࡝ࡤࡉࡏࡏࡈࡌࡋ࡚ࡘࡁࡕࡋࡒࡒࡤ࡟ࡍࡍࠩᝍ"), bstack11l1l_opy_ (u"ࠩࡾࢁࠬᝎ"))).get(bstack11l1l_opy_ (u"ࠪࡷࡨࡧ࡮࡯ࡧࡵ࡚ࡪࡸࡳࡪࡱࡱࠫᝏ"))
    if not config[bstack11l1l_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡓࡶࡴࡪࡵࡤࡶࡐࡥࡵ࠭ᝐ")].get(bstack11l1l_opy_ (u"ࠧࡧࡰࡱࡡࡤࡹࡹࡵ࡭ࡢࡶࡨࠦᝑ")):
      if bstack11l1l_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡀ࡯ࡱࡶ࡬ࡳࡳࡹࠧᝒ") in caps:
        caps[bstack11l1l_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱ࠺ࡰࡲࡷ࡭ࡴࡴࡳࠨᝓ")][bstack11l1l_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࡐࡲࡷ࡭ࡴࡴࡳࠨ᝔")] = bstack1ll1ll1lll1_opy_
        caps[bstack11l1l_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬࠼ࡲࡴࡹ࡯࡯࡯ࡵࠪ᝕")][bstack11l1l_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࡒࡴࡹ࡯࡯࡯ࡵࠪ᝖")][bstack11l1l_opy_ (u"ࠫࡸࡩࡡ࡯ࡰࡨࡶ࡛࡫ࡲࡴ࡫ࡲࡲࠬ᝗")] = bstack11ll11111l1_opy_
      else:
        caps[bstack11l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࡓࡵࡺࡩࡰࡰࡶࠫ᝘")] = bstack1ll1ll1lll1_opy_
        caps[bstack11l1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࡔࡶࡴࡪࡱࡱࡷࠬ᝙")][bstack11l1l_opy_ (u"ࠧࡴࡥࡤࡲࡳ࡫ࡲࡗࡧࡵࡷ࡮ࡵ࡮ࠨ᝚")] = bstack11ll11111l1_opy_
  except Exception as error:
    logger.debug(bstack11l1l_opy_ (u"ࠣࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤࡼ࡮ࡩ࡭ࡧࠣࡷࡪࡺࡴࡪࡰࡪࠤࡆࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠤࡆࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠡࡥࡤࡴࡦࡨࡩ࡭࡫ࡷ࡭ࡪࡹ࠮ࠡࡇࡵࡶࡴࡸ࠺ࠡࠤ᝛") +  str(error))
def bstack1lll111ll1_opy_(driver, bstack11ll11l1lll_opy_):
  try:
    setattr(driver, bstack11l1l_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬ࡃ࠴࠵ࡾ࡙ࡨࡰࡷ࡯ࡨࡘࡩࡡ࡯ࠩ᝜"), True)
    session = driver.session_id
    if session:
      bstack11l1lll1lll_opy_ = True
      current_url = driver.current_url
      try:
        url = urlparse(current_url)
      except Exception as e:
        bstack11l1lll1lll_opy_ = False
      bstack11l1lll1lll_opy_ = url.scheme in [bstack11l1l_opy_ (u"ࠥ࡬ࡹࡺࡰࠣ᝝"), bstack11l1l_opy_ (u"ࠦ࡭ࡺࡴࡱࡵࠥ᝞")]
      if bstack11l1lll1lll_opy_:
        if bstack11ll11l1lll_opy_:
          logger.info(bstack11l1l_opy_ (u"࡙ࠧࡥࡵࡷࡳࠤ࡫ࡵࡲࠡࡃࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠡࡶࡨࡷࡹ࡯࡮ࡨࠢ࡫ࡥࡸࠦࡳࡵࡣࡵࡸࡪࡪ࠮ࠡࡃࡸࡸࡴࡳࡡࡵࡧࠣࡸࡪࡹࡴࠡࡥࡤࡷࡪࠦࡥࡹࡧࡦࡹࡹ࡯࡯࡯ࠢࡺ࡭ࡱࡲࠠࡣࡧࡪ࡭ࡳࠦ࡭ࡰ࡯ࡨࡲࡹࡧࡲࡪ࡮ࡼ࠲ࠧ᝟"))
      return bstack11ll11l1lll_opy_
  except Exception as e:
    logger.error(bstack11l1l_opy_ (u"ࠨࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢ࡬ࡲࠥࡹࡴࡢࡴࡷ࡭ࡳ࡭ࠠࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡢࡷࡷࡳࡲࡧࡴࡪࡱࡱࠤࡸࡩࡡ࡯ࠢࡩࡳࡷࠦࡴࡩ࡫ࡶࠤࡹ࡫ࡳࡵࠢࡦࡥࡸ࡫࠺ࠡࠤᝠ") + str(e))
    return False
def bstack111ll1l1_opy_(driver, name, path):
  try:
    bstack1l1lllll1ll_opy_ = {
        bstack11l1l_opy_ (u"ࠧࡵࡪࡗࡩࡸࡺࡒࡶࡰࡘࡹ࡮ࡪࠧᝡ"): threading.current_thread().current_test_uuid,
        bstack11l1l_opy_ (u"ࠨࡶ࡫ࡆࡺ࡯࡬ࡥࡗࡸ࡭ࡩ࠭ᝢ"): os.environ.get(bstack11l1l_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡘ࡙ࡎࡊࠧᝣ"), bstack11l1l_opy_ (u"ࠪࠫᝤ")),
        bstack11l1l_opy_ (u"ࠫࡹ࡮ࡊࡸࡶࡗࡳࡰ࡫࡮ࠨᝥ"): os.environ.get(bstack11l1l_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡊࡘࡆࡤࡐࡗࡕࠩᝦ"), bstack11l1l_opy_ (u"࠭ࠧᝧ"))
    }
    bstack1l1llllllll_opy_ = bstack11l1l11ll_opy_.bstack1ll11l1l111_opy_(EVENTS.bstack1l11l1l111_opy_.value)
    logger.debug(bstack11l1l_opy_ (u"ࠧࡑࡧࡵࡪࡴࡸ࡭ࡪࡰࡪࠤࡸࡩࡡ࡯ࠢࡥࡩ࡫ࡵࡲࡦࠢࡶࡥࡻ࡯࡮ࡨࠢࡵࡩࡸࡻ࡬ࡵࡵࠪᝨ"))
    try:
      if (bstack11lll11l_opy_(threading.current_thread(), bstack11l1l_opy_ (u"ࠨ࡫ࡶࡅࡵࡶࡁ࠲࠳ࡼࡘࡪࡹࡴࠨᝩ"), None) and bstack11lll11l_opy_(threading.current_thread(), bstack11l1l_opy_ (u"ࠩࡤࡴࡵࡇ࠱࠲ࡻࡓࡰࡦࡺࡦࡰࡴࡰࠫᝪ"), None)):
        scripts = {bstack11l1l_opy_ (u"ࠪࡷࡨࡧ࡮ࠨᝫ"): bstack111lll1l_opy_.perform_scan}
        bstack11ll111l1l1_opy_ = json.loads(scripts[bstack11l1l_opy_ (u"ࠦࡸࡩࡡ࡯ࠤᝬ")].replace(bstack11l1l_opy_ (u"ࠧࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࠣ᝭"), bstack11l1l_opy_ (u"ࠨࠢᝮ")))
        bstack11ll111l1l1_opy_[bstack11l1l_opy_ (u"ࠧࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠪᝯ")][bstack11l1l_opy_ (u"ࠨ࡯ࡨࡸ࡭ࡵࡤࠨᝰ")] = None
        scripts[bstack11l1l_opy_ (u"ࠤࡶࡧࡦࡴࠢ᝱")] = bstack11l1l_opy_ (u"ࠥࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡨࡼࡪࡩࡵࡵࡱࡵ࠾ࠥࠨᝲ") + json.dumps(bstack11ll111l1l1_opy_)
        bstack111lll1l_opy_.bstack1111ll1ll_opy_(scripts)
        bstack111lll1l_opy_.store()
        logger.debug(driver.execute_script(bstack111lll1l_opy_.perform_scan))
      else:
        logger.debug(driver.execute_async_script(bstack111lll1l_opy_.perform_scan, {bstack11l1l_opy_ (u"ࠦࡲ࡫ࡴࡩࡱࡧࠦᝳ"): name}))
      bstack11l1l11ll_opy_.end(EVENTS.bstack1l11l1l111_opy_.value, bstack1l1llllllll_opy_ + bstack11l1l_opy_ (u"ࠧࡀࡳࡵࡣࡵࡸࠧ᝴"), bstack1l1llllllll_opy_ + bstack11l1l_opy_ (u"ࠨ࠺ࡦࡰࡧࠦ᝵"), True, None)
    except Exception as error:
      bstack11l1l11ll_opy_.end(EVENTS.bstack1l11l1l111_opy_.value, bstack1l1llllllll_opy_ + bstack11l1l_opy_ (u"ࠢ࠻ࡵࡷࡥࡷࡺࠢ᝶"), bstack1l1llllllll_opy_ + bstack11l1l_opy_ (u"ࠣ࠼ࡨࡲࡩࠨ᝷"), False, str(error))
    bstack1l1llllllll_opy_ = bstack11l1l11ll_opy_.bstack11ll11l111l_opy_(EVENTS.bstack1ll11l11lll_opy_.value)
    bstack11l1l11ll_opy_.mark(bstack1l1llllllll_opy_ + bstack11l1l_opy_ (u"ࠤ࠽ࡷࡹࡧࡲࡵࠤ᝸"))
    try:
      if (bstack11lll11l_opy_(threading.current_thread(), bstack11l1l_opy_ (u"ࠪ࡭ࡸࡇࡰࡱࡃ࠴࠵ࡾ࡚ࡥࡴࡶࠪ᝹"), None) and bstack11lll11l_opy_(threading.current_thread(), bstack11l1l_opy_ (u"ࠫࡦࡶࡰࡂ࠳࠴ࡽࡕࡲࡡࡵࡨࡲࡶࡲ࠭᝺"), None)):
        scripts = {bstack11l1l_opy_ (u"ࠬࡹࡣࡢࡰࠪ᝻"): bstack111lll1l_opy_.perform_scan}
        bstack11ll111l1l1_opy_ = json.loads(scripts[bstack11l1l_opy_ (u"ࠨࡳࡤࡣࡱࠦ᝼")].replace(bstack11l1l_opy_ (u"ࠢࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡥࡹࡧࡦࡹࡹࡵࡲ࠻ࠢࠥ᝽"), bstack11l1l_opy_ (u"ࠣࠤ᝾")))
        bstack11ll111l1l1_opy_[bstack11l1l_opy_ (u"ࠩࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠬ᝿")][bstack11l1l_opy_ (u"ࠪࡱࡪࡺࡨࡰࡦࠪក")] = None
        scripts[bstack11l1l_opy_ (u"ࠦࡸࡩࡡ࡯ࠤខ")] = bstack11l1l_opy_ (u"ࠧࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࠣគ") + json.dumps(bstack11ll111l1l1_opy_)
        bstack111lll1l_opy_.bstack1111ll1ll_opy_(scripts)
        bstack111lll1l_opy_.store()
        logger.debug(driver.execute_script(bstack111lll1l_opy_.perform_scan))
      else:
        logger.debug(driver.execute_async_script(bstack111lll1l_opy_.bstack11l1lllllll_opy_, bstack1l1lllll1ll_opy_))
      bstack11l1l11ll_opy_.end(bstack1l1llllllll_opy_, bstack1l1llllllll_opy_ + bstack11l1l_opy_ (u"ࠨ࠺ࡴࡶࡤࡶࡹࠨឃ"), bstack1l1llllllll_opy_ + bstack11l1l_opy_ (u"ࠢ࠻ࡧࡱࡨࠧង"),True, None)
    except Exception as error:
      bstack11l1l11ll_opy_.end(bstack1l1llllllll_opy_, bstack1l1llllllll_opy_ + bstack11l1l_opy_ (u"ࠣ࠼ࡶࡸࡦࡸࡴࠣច"), bstack1l1llllllll_opy_ + bstack11l1l_opy_ (u"ࠤ࠽ࡩࡳࡪࠢឆ"),False, str(error))
    logger.info(bstack11l1l_opy_ (u"ࠥࡅࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠣࡸࡪࡹࡴࡪࡰࡪࠤ࡫ࡵࡲࠡࡶ࡫࡭ࡸࠦࡴࡦࡵࡷࠤࡨࡧࡳࡦࠢ࡫ࡥࡸࠦࡥ࡯ࡦࡨࡨ࠳ࠨជ"))
    try:
      bstack1ll1111l1l1_opy_ = {
        bstack11l1l_opy_ (u"ࠦࡷ࡫ࡱࡶࡧࡶࡸࠧឈ"): {
          bstack11l1l_opy_ (u"ࠧࡩ࡯࡮࡯ࡤࡲࡩࠨញ"): bstack11l1l_opy_ (u"ࠨࡁ࠲࠳࡜ࡣࡘࡇࡖࡆࡡࡕࡉࡘ࡛ࡌࡕࡕࠥដ"),
        },
        bstack11l1l_opy_ (u"ࠢࡳࡧࡶࡴࡴࡴࡳࡦࠤឋ"): {
          bstack11l1l_opy_ (u"ࠣࡤࡲࡨࡾࠨឌ"): {
            bstack11l1l_opy_ (u"ࠤࡰࡷ࡬ࠨឍ"): bstack11l1l_opy_ (u"ࠥࡅࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠣࡸࡪࡹࡴࡪࡰࡪࠤ࡫ࡵࡲࠡࡶ࡫࡭ࡸࠦࡴࡦࡵࡷࠤࡨࡧࡳࡦࠢ࡫ࡥࡸࠦࡥ࡯ࡦࡨࡨ࠳ࠨណ"),
            bstack11l1l_opy_ (u"ࠦࡸࡻࡣࡤࡧࡶࡷࠧត"): True
          }
        }
      }
      bstack1ll11l1ll_opy_.info(json.dumps(bstack1ll1111l1l1_opy_, separators=(bstack11l1l_opy_ (u"ࠬ࠲ࠧថ"), bstack11l1l_opy_ (u"࠭࠺ࠨទ"))))
    except Exception as bstack1l1l1ll1l1_opy_:
      logger.debug(bstack11l1l_opy_ (u"ࠢࡇࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡰࡴ࡭ࠠࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡴࡣࡹࡩࠥࡸࡥࡴࡷ࡯ࡸࡸࠦࡤࡢࡶࡤ࠾ࠥࠨធ") + str(bstack1l1l1ll1l1_opy_) + bstack11l1l_opy_ (u"ࠣࠤន"))
  except Exception as bstack1l1lll1l1l1_opy_:
    logger.error(bstack11l1l_opy_ (u"ࠤࡄࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠢࡵࡩࡸࡻ࡬ࡵࡵࠣࡧࡴࡻ࡬ࡥࠢࡱࡳࡹࠦࡢࡦࠢࡳࡶࡴࡩࡥࡴࡵࡨࡨࠥ࡬࡯ࡳࠢࡷ࡬ࡪࠦࡴࡦࡵࡷࠤࡨࡧࡳࡦ࠼ࠣࠦប") + str(path) + bstack11l1l_opy_ (u"ࠥࠤࡊࡸࡲࡰࡴࠣ࠾ࠧផ") + str(bstack1l1lll1l1l1_opy_))
def bstack11ll11l1l11_opy_(driver):
    caps = driver.capabilities
    if caps.get(bstack11l1l_opy_ (u"ࠦࡵࡲࡡࡵࡨࡲࡶࡲࡔࡡ࡮ࡧࠥព")) and str(caps.get(bstack11l1l_opy_ (u"ࠧࡶ࡬ࡢࡶࡩࡳࡷࡳࡎࡢ࡯ࡨࠦភ"))).lower() == bstack11l1l_opy_ (u"ࠨࡡ࡯ࡦࡵࡳ࡮ࡪࠢម"):
        bstack1ll1111llll_opy_ = caps.get(bstack11l1l_opy_ (u"ࠢࡢࡲࡳ࡭ࡺࡳ࠺ࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡘࡨࡶࡸ࡯࡯࡯ࠤយ")) or caps.get(bstack11l1l_opy_ (u"ࠣࡲ࡯ࡥࡹ࡬࡯ࡳ࡯࡙ࡩࡷࡹࡩࡰࡰࠥរ"))
        if bstack1ll1111llll_opy_ and int(str(bstack1ll1111llll_opy_)) < bstack11l1llll1ll_opy_:
            return False
    return True
def bstack1lllll1lll_opy_(config):
  if bstack11l1l_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠩល") in config:
        return config[bstack11l1l_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠪវ")]
  for platform in config.get(bstack11l1l_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧឝ"), []):
      if bstack11l1l_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠬឞ") in platform:
          return platform[bstack11l1l_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾ࠭ស")]
  return None
def bstack111lllll_opy_(bstack1ll1lllll_opy_):
  try:
    browser_name = bstack1ll1lllll_opy_[bstack11l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡠࡰࡤࡱࡪ࠭ហ")]
    browser_version = bstack1ll1lllll_opy_[bstack11l1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡡࡹࡩࡷࡹࡩࡰࡰࠪឡ")]
    chrome_options = bstack1ll1lllll_opy_[bstack11l1l_opy_ (u"ࠩࡦ࡬ࡷࡵ࡭ࡦࡡࡲࡴࡹ࡯࡯࡯ࡵࠪអ")]
    try:
        bstack11l1llll111_opy_ = int(browser_version.split(bstack11l1l_opy_ (u"ࠪ࠲ࠬឣ"))[0])
    except ValueError as e:
        logger.error(bstack11l1l_opy_ (u"ࠦࡊࡸࡲࡰࡴࠣࡻ࡭࡯࡬ࡦࠢࡦࡳࡳࡼࡥࡳࡶ࡬ࡲ࡬ࠦࡢࡳࡱࡺࡷࡪࡸࠠࡷࡧࡵࡷ࡮ࡵ࡮ࠣឤ") + str(e))
        return False
    if not (browser_name and browser_name.lower() == bstack11l1l_opy_ (u"ࠬࡩࡨࡳࡱࡰࡩࠬឥ")):
        logger.warning(bstack11l1l_opy_ (u"ࠨࡁࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࠦࡁࡶࡶࡲࡱࡦࡺࡩࡰࡰࠣࡻ࡮ࡲ࡬ࠡࡴࡸࡲࠥࡵ࡮࡭ࡻࠣࡳࡳࠦࡃࡩࡴࡲࡱࡪࠦࡢࡳࡱࡺࡷࡪࡸࡳ࠯ࠤឦ"))
        return False
    if bstack11l1llll111_opy_ < bstack11ll11l1ll1_opy_.bstack1l1lll11l1l_opy_:
        logger.warning(bstack1ll1l11l1ll_opy_ (u"ࠧࡂࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡂࡷࡷࡳࡲࡧࡴࡪࡱࡱࠤࡷ࡫ࡱࡶ࡫ࡵࡩࡸࠦࡃࡩࡴࡲࡱࡪࠦࡶࡦࡴࡶ࡭ࡴࡴࠠࡼࡅࡒࡒࡘ࡚ࡁࡏࡖࡖ࠲ࡒࡏࡎࡊࡏࡘࡑࡤࡔࡏࡏࡡࡅࡗ࡙ࡇࡃࡌࡡࡌࡒࡋࡘࡁࡠࡃ࠴࠵࡞ࡥࡓࡖࡒࡓࡓࡗ࡚ࡅࡅࡡࡆࡌࡗࡕࡍࡆࡡ࡙ࡉࡗ࡙ࡉࡐࡐࢀࠤࡴࡸࠠࡩ࡫ࡪ࡬ࡪࡸ࠮ࠨឧ"))
        return False
    if chrome_options and any(bstack11l1l_opy_ (u"ࠨ࠯࠰࡬ࡪࡧࡤ࡭ࡧࡶࡷࠬឨ") in value for value in chrome_options.values() if isinstance(value, str)):
        logger.warning(bstack11l1l_opy_ (u"ࠤࡄࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠢࡄࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳࠦࡷࡪ࡮࡯ࠤࡳࡵࡴࠡࡴࡸࡲࠥࡵ࡮ࠡ࡮ࡨ࡫ࡦࡩࡹࠡࡪࡨࡥࡩࡲࡥࡴࡵࠣࡱࡴࡪࡥ࠯ࠢࡖࡻ࡮ࡺࡣࡩࠢࡷࡳࠥࡴࡥࡸࠢ࡫ࡩࡦࡪ࡬ࡦࡵࡶࠤࡲࡵࡤࡦࠢࡲࡶࠥࡧࡶࡰ࡫ࡧࠤࡺࡹࡩ࡯ࡩࠣ࡬ࡪࡧࡤ࡭ࡧࡶࡷࠥࡳ࡯ࡥࡧ࠱ࠦឩ"))
        return False
    return True
  except Exception as e:
    logger.error(bstack11l1l_opy_ (u"ࠥࡉࡷࡸ࡯ࡳࠢ࡬ࡲࠥࡩࡨࡦࡥ࡮࡭ࡳ࡭ࠠࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࠢࡶࡹࡵࡶ࡯ࡳࡶࠣࡪࡴࡸࠠ࡭ࡱࡦࡥࡱࠦࡃࡩࡴࡲࡱࡪࡀࠠࠣឪ") + str(e))
    return False
def bstack11ll11ll_opy_(bstack11llll1111_opy_, config):
    try:
      bstack1l1lll11l11_opy_ = bstack11l1l_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠫឫ") in config and config[bstack11l1l_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠬឬ")] == True
      bstack11ll11lll1l_opy_ = bstack11l1l_opy_ (u"࠭ࡴࡶࡴࡥࡳࡘࡩࡡ࡭ࡧࠪឭ") in config and str(config[bstack11l1l_opy_ (u"ࠧࡵࡷࡵࡦࡴ࡙ࡣࡢ࡮ࡨࠫឮ")]).lower() != bstack11l1l_opy_ (u"ࠨࡨࡤࡰࡸ࡫ࠧឯ")
      if not (bstack1l1lll11l11_opy_ and (not bstack11lll11ll1_opy_(config) or bstack11ll11lll1l_opy_)):
        return bstack11llll1111_opy_
      bstack11ll111l1ll_opy_ = bstack111lll1l_opy_.bstack11l1llll11l_opy_
      if bstack11ll111l1ll_opy_ is None:
        logger.debug(bstack11l1l_opy_ (u"ࠤࡊࡳࡴ࡭࡬ࡦࠢࡦ࡬ࡷࡵ࡭ࡦࠢࡲࡴࡹ࡯࡯࡯ࡵࠣࡥࡷ࡫ࠠࡏࡱࡱࡩࠧឰ"))
        return bstack11llll1111_opy_
      bstack11ll11l11ll_opy_ = int(str(bstack11ll11l1111_opy_()).split(bstack11l1l_opy_ (u"ࠪ࠲ࠬឱ"))[0])
      logger.debug(bstack11l1l_opy_ (u"ࠦࡘ࡫࡬ࡦࡰ࡬ࡹࡲࠦࡶࡦࡴࡶ࡭ࡴࡴࠠࡥࡧࡷࡩࡨࡺࡥࡥ࠼ࠣࠦឲ") + str(bstack11ll11l11ll_opy_) + bstack11l1l_opy_ (u"ࠧࠨឳ"))
      if bstack11ll11l11ll_opy_ == 3 and isinstance(bstack11llll1111_opy_, dict) and bstack11l1l_opy_ (u"࠭ࡤࡦࡵ࡬ࡶࡪࡪ࡟ࡤࡣࡳࡥࡧ࡯࡬ࡪࡶ࡬ࡩࡸ࠭឴") in bstack11llll1111_opy_ and bstack11ll111l1ll_opy_ is not None:
        if bstack11l1l_opy_ (u"ࠧࡨࡱࡲ࡫࠿ࡩࡨࡳࡱࡰࡩࡔࡶࡴࡪࡱࡱࡷࠬ឵") not in bstack11llll1111_opy_[bstack11l1l_opy_ (u"ࠨࡦࡨࡷ࡮ࡸࡥࡥࡡࡦࡥࡵࡧࡢࡪ࡮࡬ࡸ࡮࡫ࡳࠨា")]:
          bstack11llll1111_opy_[bstack11l1l_opy_ (u"ࠩࡧࡩࡸ࡯ࡲࡦࡦࡢࡧࡦࡶࡡࡣ࡫࡯࡭ࡹ࡯ࡥࡴࠩិ")][bstack11l1l_opy_ (u"ࠪ࡫ࡴࡵࡧ࠻ࡥ࡫ࡶࡴࡳࡥࡐࡲࡷ࡭ࡴࡴࡳࠨី")] = {}
        if bstack11l1l_opy_ (u"ࠫࡦࡸࡧࡴࠩឹ") in bstack11ll111l1ll_opy_:
          if bstack11l1l_opy_ (u"ࠬࡧࡲࡨࡵࠪឺ") not in bstack11llll1111_opy_[bstack11l1l_opy_ (u"࠭ࡤࡦࡵ࡬ࡶࡪࡪ࡟ࡤࡣࡳࡥࡧ࡯࡬ࡪࡶ࡬ࡩࡸ࠭ុ")][bstack11l1l_opy_ (u"ࠧࡨࡱࡲ࡫࠿ࡩࡨࡳࡱࡰࡩࡔࡶࡴࡪࡱࡱࡷࠬូ")]:
            bstack11llll1111_opy_[bstack11l1l_opy_ (u"ࠨࡦࡨࡷ࡮ࡸࡥࡥࡡࡦࡥࡵࡧࡢࡪ࡮࡬ࡸ࡮࡫ࡳࠨួ")][bstack11l1l_opy_ (u"ࠩࡪࡳࡴ࡭࠺ࡤࡪࡵࡳࡲ࡫ࡏࡱࡶ࡬ࡳࡳࡹࠧើ")][bstack11l1l_opy_ (u"ࠪࡥࡷ࡭ࡳࠨឿ")] = []
          for arg in bstack11ll111l1ll_opy_[bstack11l1l_opy_ (u"ࠫࡦࡸࡧࡴࠩៀ")]:
            if arg not in bstack11llll1111_opy_[bstack11l1l_opy_ (u"ࠬࡪࡥࡴ࡫ࡵࡩࡩࡥࡣࡢࡲࡤࡦ࡮ࡲࡩࡵ࡫ࡨࡷࠬេ")][bstack11l1l_opy_ (u"࠭ࡧࡰࡱࡪ࠾ࡨ࡮ࡲࡰ࡯ࡨࡓࡵࡺࡩࡰࡰࡶࠫែ")][bstack11l1l_opy_ (u"ࠧࡢࡴࡪࡷࠬៃ")]:
              bstack11llll1111_opy_[bstack11l1l_opy_ (u"ࠨࡦࡨࡷ࡮ࡸࡥࡥࡡࡦࡥࡵࡧࡢࡪ࡮࡬ࡸ࡮࡫ࡳࠨោ")][bstack11l1l_opy_ (u"ࠩࡪࡳࡴ࡭࠺ࡤࡪࡵࡳࡲ࡫ࡏࡱࡶ࡬ࡳࡳࡹࠧៅ")][bstack11l1l_opy_ (u"ࠪࡥࡷ࡭ࡳࠨំ")].append(arg)
        if bstack11l1l_opy_ (u"ࠫࡪࡾࡴࡦࡰࡶ࡭ࡴࡴࡳࠨះ") in bstack11ll111l1ll_opy_:
          if bstack11l1l_opy_ (u"ࠬ࡫ࡸࡵࡧࡱࡷ࡮ࡵ࡮ࡴࠩៈ") not in bstack11llll1111_opy_[bstack11l1l_opy_ (u"࠭ࡤࡦࡵ࡬ࡶࡪࡪ࡟ࡤࡣࡳࡥࡧ࡯࡬ࡪࡶ࡬ࡩࡸ࠭៉")][bstack11l1l_opy_ (u"ࠧࡨࡱࡲ࡫࠿ࡩࡨࡳࡱࡰࡩࡔࡶࡴࡪࡱࡱࡷࠬ៊")]:
            bstack11llll1111_opy_[bstack11l1l_opy_ (u"ࠨࡦࡨࡷ࡮ࡸࡥࡥࡡࡦࡥࡵࡧࡢࡪ࡮࡬ࡸ࡮࡫ࡳࠨ់")][bstack11l1l_opy_ (u"ࠩࡪࡳࡴ࡭࠺ࡤࡪࡵࡳࡲ࡫ࡏࡱࡶ࡬ࡳࡳࡹࠧ៌")][bstack11l1l_opy_ (u"ࠪࡩࡽࡺࡥ࡯ࡵ࡬ࡳࡳࡹࠧ៍")] = []
          for ext in bstack11ll111l1ll_opy_[bstack11l1l_opy_ (u"ࠫࡪࡾࡴࡦࡰࡶ࡭ࡴࡴࡳࠨ៎")]:
            if ext not in bstack11llll1111_opy_[bstack11l1l_opy_ (u"ࠬࡪࡥࡴ࡫ࡵࡩࡩࡥࡣࡢࡲࡤࡦ࡮ࡲࡩࡵ࡫ࡨࡷࠬ៏")][bstack11l1l_opy_ (u"࠭ࡧࡰࡱࡪ࠾ࡨ࡮ࡲࡰ࡯ࡨࡓࡵࡺࡩࡰࡰࡶࠫ័")][bstack11l1l_opy_ (u"ࠧࡦࡺࡷࡩࡳࡹࡩࡰࡰࡶࠫ៑")]:
              bstack11llll1111_opy_[bstack11l1l_opy_ (u"ࠨࡦࡨࡷ࡮ࡸࡥࡥࡡࡦࡥࡵࡧࡢࡪ࡮࡬ࡸ࡮࡫ࡳࠨ្")][bstack11l1l_opy_ (u"ࠩࡪࡳࡴ࡭࠺ࡤࡪࡵࡳࡲ࡫ࡏࡱࡶ࡬ࡳࡳࡹࠧ៓")][bstack11l1l_opy_ (u"ࠪࡩࡽࡺࡥ࡯ࡵ࡬ࡳࡳࡹࠧ។")].append(ext)
        if bstack11l1l_opy_ (u"ࠫࡵࡸࡥࡧࡵࠪ៕") in bstack11ll111l1ll_opy_:
          if bstack11l1l_opy_ (u"ࠬࡶࡲࡦࡨࡶࠫ៖") not in bstack11llll1111_opy_[bstack11l1l_opy_ (u"࠭ࡤࡦࡵ࡬ࡶࡪࡪ࡟ࡤࡣࡳࡥࡧ࡯࡬ࡪࡶ࡬ࡩࡸ࠭ៗ")][bstack11l1l_opy_ (u"ࠧࡨࡱࡲ࡫࠿ࡩࡨࡳࡱࡰࡩࡔࡶࡴࡪࡱࡱࡷࠬ៘")]:
            bstack11llll1111_opy_[bstack11l1l_opy_ (u"ࠨࡦࡨࡷ࡮ࡸࡥࡥࡡࡦࡥࡵࡧࡢࡪ࡮࡬ࡸ࡮࡫ࡳࠨ៙")][bstack11l1l_opy_ (u"ࠩࡪࡳࡴ࡭࠺ࡤࡪࡵࡳࡲ࡫ࡏࡱࡶ࡬ࡳࡳࡹࠧ៚")][bstack11l1l_opy_ (u"ࠪࡴࡷ࡫ࡦࡴࠩ៛")] = {}
          bstack11l1lllll1l_opy_(bstack11llll1111_opy_[bstack11l1l_opy_ (u"ࠫࡩ࡫ࡳࡪࡴࡨࡨࡤࡩࡡࡱࡣࡥ࡭ࡱ࡯ࡴࡪࡧࡶࠫៜ")][bstack11l1l_opy_ (u"ࠬ࡭࡯ࡰࡩ࠽ࡧ࡭ࡸ࡯࡮ࡧࡒࡴࡹ࡯࡯࡯ࡵࠪ៝")][bstack11l1l_opy_ (u"࠭ࡰࡳࡧࡩࡷࠬ៞")],
                    bstack11ll111l1ll_opy_[bstack11l1l_opy_ (u"ࠧࡱࡴࡨࡪࡸ࠭៟")])
        os.environ[bstack11l1l_opy_ (u"ࠨࡋࡖࡣࡓࡕࡎࡠࡄࡖࡘࡆࡉࡋࡠࡋࡑࡊࡗࡇ࡟ࡂ࠳࠴࡝ࡤ࡙ࡅࡔࡕࡌࡓࡓ࠭០")] = bstack11l1l_opy_ (u"ࠩࡷࡶࡺ࡫ࠧ១")
        return bstack11llll1111_opy_
      else:
        chrome_options = None
        if isinstance(bstack11llll1111_opy_, ChromeOptions):
          chrome_options = bstack11llll1111_opy_
        elif isinstance(bstack11llll1111_opy_, dict):
          for value in bstack11llll1111_opy_.values():
            if isinstance(value, ChromeOptions):
              chrome_options = value
              break
        if chrome_options is None:
          chrome_options = ChromeOptions()
          if isinstance(bstack11llll1111_opy_, dict):
            bstack11llll1111_opy_[bstack11l1l_opy_ (u"ࠪࡳࡵࡺࡩࡰࡰࡶࠫ២")] = chrome_options
          else:
            bstack11llll1111_opy_ = chrome_options
        if bstack11ll111l1ll_opy_ is not None:
          if bstack11l1l_opy_ (u"ࠫࡦࡸࡧࡴࠩ៣") in bstack11ll111l1ll_opy_:
                bstack11ll1111l1l_opy_ = chrome_options.arguments or []
                new_args = bstack11ll111l1ll_opy_[bstack11l1l_opy_ (u"ࠬࡧࡲࡨࡵࠪ៤")]
                for arg in new_args:
                    if arg not in bstack11ll1111l1l_opy_:
                        chrome_options.add_argument(arg)
          if bstack11l1l_opy_ (u"࠭ࡥࡹࡶࡨࡲࡸ࡯࡯࡯ࡵࠪ៥") in bstack11ll111l1ll_opy_:
                existing_extensions = chrome_options.experimental_options.get(bstack11l1l_opy_ (u"ࠧࡦࡺࡷࡩࡳࡹࡩࡰࡰࡶࠫ៦"), [])
                bstack11ll111llll_opy_ = bstack11ll111l1ll_opy_[bstack11l1l_opy_ (u"ࠨࡧࡻࡸࡪࡴࡳࡪࡱࡱࡷࠬ៧")]
                for extension in bstack11ll111llll_opy_:
                    if extension not in existing_extensions:
                        chrome_options.add_encoded_extension(extension)
          if bstack11l1l_opy_ (u"ࠩࡳࡶࡪ࡬ࡳࠨ៨") in bstack11ll111l1ll_opy_:
                bstack11ll1111l11_opy_ = chrome_options.experimental_options.get(bstack11l1l_opy_ (u"ࠪࡴࡷ࡫ࡦࡴࠩ៩"), {})
                bstack11ll11l1l1l_opy_ = bstack11ll111l1ll_opy_[bstack11l1l_opy_ (u"ࠫࡵࡸࡥࡧࡵࠪ៪")]
                bstack11l1lllll1l_opy_(bstack11ll1111l11_opy_, bstack11ll11l1l1l_opy_)
                chrome_options.add_experimental_option(bstack11l1l_opy_ (u"ࠬࡶࡲࡦࡨࡶࠫ៫"), bstack11ll1111l11_opy_)
        os.environ[bstack11l1l_opy_ (u"࠭ࡉࡔࡡࡑࡓࡓࡥࡂࡔࡖࡄࡇࡐࡥࡉࡏࡈࡕࡅࡤࡇ࠱࠲࡛ࡢࡗࡊ࡙ࡓࡊࡑࡑࠫ៬")] = bstack11l1l_opy_ (u"ࠧࡵࡴࡸࡩࠬ៭")
        return bstack11llll1111_opy_
    except Exception as e:
      logger.error(bstack11l1l_opy_ (u"ࠣࡇࡵࡶࡴࡸࠠࡸࡪ࡬ࡰࡪࠦࡡࡥࡦ࡬ࡲ࡬ࠦ࡮ࡰࡰ࠰ࡆࡘࠦࡩ࡯ࡨࡵࡥࠥࡧ࠱࠲ࡻࠣࡧ࡭ࡸ࡯࡮ࡧࠣࡳࡵࡺࡩࡰࡰࡶ࠾ࠥࠨ៮") + str(e))
      return bstack11llll1111_opy_