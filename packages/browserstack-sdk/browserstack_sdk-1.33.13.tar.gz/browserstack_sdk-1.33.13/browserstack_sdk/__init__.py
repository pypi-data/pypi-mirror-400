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
import atexit
import shlex
import signal
import yaml
import socket
import datetime
import string
import random
import collections.abc
import traceback
import copy
import threading
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import json
from packaging import version
from browserstack.local import Local
from urllib.parse import urlparse
from dotenv import load_dotenv
from browserstack_sdk.bstack111llll11l_opy_ import bstack1l1ll11l1l_opy_
from browserstack_sdk.bstack11llll11l_opy_ import *
import time
import requests
from bstack_utils.constants import EVENTS, STAGE, bstack1l11ll1l_opy_
from bstack_utils.messages import bstack11ll11111l_opy_, bstack1l11111ll_opy_, bstack11l111lll_opy_, bstack1ll11ll1ll_opy_, bstack11l11ll1ll_opy_, bstack11lll1ll11_opy_
from bstack_utils.measure import measure
from bstack_utils.bstack1l1lll1l11_opy_ import get_logger
from bstack_utils.helper import bstack1lllll111l_opy_
from browserstack_sdk.bstack11l11lllll_opy_ import bstack11l11l1l1l_opy_
logger = get_logger(__name__)
def bstack11llll11_opy_():
  global CONFIG
  headers = {
        bstack11l1l_opy_ (u"ࠪࡇࡴࡴࡴࡦࡰࡷ࠱ࡹࡿࡰࡦࠩࡶ"): bstack11l1l_opy_ (u"ࠫࡦࡶࡰ࡭࡫ࡦࡥࡹ࡯࡯࡯࠱࡭ࡷࡴࡴࠧࡷ"),
      }
  proxies = bstack1lllll111l_opy_(CONFIG, bstack1l11ll1l_opy_)
  try:
    response = requests.get(bstack1l11ll1l_opy_, headers=headers, proxies=proxies, timeout=5)
    if response.json():
      bstack11lll1ll1_opy_ = response.json()[bstack11l1l_opy_ (u"ࠬ࡮ࡵࡣࡵࠪࡸ")]
      logger.debug(bstack11ll11111l_opy_.format(response.json()))
      return bstack11lll1ll1_opy_
    else:
      logger.debug(bstack1l11111ll_opy_.format(bstack11l1l_opy_ (u"ࠨࡒࡦࡵࡳࡳࡳࡹࡥࠡࡌࡖࡓࡓࠦࡰࡢࡴࡶࡩࠥ࡫ࡲࡳࡱࡵࠤࠧࡹ")))
  except Exception as e:
    logger.debug(bstack1l11111ll_opy_.format(e))
def bstack11lllll11_opy_(hub_url):
  global CONFIG
  url = bstack11l1l_opy_ (u"ࠢࡩࡶࡷࡴࡸࡀ࠯࠰ࠤࡺ")+  hub_url + bstack11l1l_opy_ (u"ࠣ࠱ࡦ࡬ࡪࡩ࡫ࠣࡻ")
  headers = {
        bstack11l1l_opy_ (u"ࠩࡆࡳࡳࡺࡥ࡯ࡶ࠰ࡸࡾࡶࡥࠨࡼ"): bstack11l1l_opy_ (u"ࠪࡥࡵࡶ࡬ࡪࡥࡤࡸ࡮ࡵ࡮࠰࡬ࡶࡳࡳ࠭ࡽ"),
      }
  proxies = bstack1lllll111l_opy_(CONFIG, url)
  try:
    start_time = time.perf_counter()
    requests.get(url, headers=headers, proxies=proxies, timeout=5)
    latency = time.perf_counter() - start_time
    logger.debug(bstack11l111lll_opy_.format(hub_url, latency))
    return dict(hub_url=hub_url, latency=latency)
  except Exception as e:
    logger.debug(bstack1ll11ll1ll_opy_.format(hub_url, e))
@measure(event_name=EVENTS.bstack11llll1ll_opy_, stage=STAGE.bstack1lll1l11l_opy_)
def bstack1lll11ll11_opy_():
  try:
    global bstack1l1l1ll1_opy_
    global CONFIG
    if bstack11l1l_opy_ (u"ࠫ࡭ࡻࡢࡓࡧࡪ࡭ࡴࡴࠧࡾ") in CONFIG and CONFIG[bstack11l1l_opy_ (u"ࠬ࡮ࡵࡣࡔࡨ࡫࡮ࡵ࡮ࠨࡿ")]:
      from bstack_utils.constants import bstack11l1lll1l_opy_
      bstack1ll1l1lll1_opy_ = CONFIG[bstack11l1l_opy_ (u"࠭ࡨࡶࡤࡕࡩ࡬࡯࡯࡯ࠩࢀ")]
      if bstack1ll1l1lll1_opy_ in bstack11l1lll1l_opy_:
        bstack1l1l1ll1_opy_ = bstack11l1lll1l_opy_[bstack1ll1l1lll1_opy_]
        logger.debug(bstack11l11ll1ll_opy_.format(bstack1l1l1ll1_opy_))
        return
      else:
        logger.debug(bstack11l1l_opy_ (u"ࠢࡉࡷࡥࠤࡰ࡫ࡹࠡࠩࡾࢁࠬࠦ࡮ࡰࡶࠣࡪࡴࡻ࡮ࡥࠢ࡬ࡲࠥࡎࡕࡃࡡࡘࡖࡑࡥࡍࡂࡒ࠯ࠤ࡫ࡧ࡬࡭࡫ࡱ࡫ࠥࡨࡡࡤ࡭ࠣࡸࡴࠦ࡯ࡱࡶ࡬ࡱࡦࡲࠠࡩࡷࡥࠤࡩ࡫ࡴࡦࡥࡷ࡭ࡴࡴࠢࢁ").format(bstack1ll1l1lll1_opy_))
    bstack11lll1ll1_opy_ = bstack11llll11_opy_()
    bstack1l11111l11_opy_ = []
    results = []
    for bstack1l1111l11_opy_ in bstack11lll1ll1_opy_:
      bstack1l11111l11_opy_.append(bstack11l11l1l1l_opy_(target=bstack11lllll11_opy_,args=(bstack1l1111l11_opy_,)))
    for t in bstack1l11111l11_opy_:
      t.start()
    for t in bstack1l11111l11_opy_:
      results.append(t.join())
    bstack1l11l11l11_opy_ = {}
    for item in results:
      hub_url = item[bstack11l1l_opy_ (u"ࠨࡪࡸࡦࡤࡻࡲ࡭ࠩࢂ")]
      latency = item[bstack11l1l_opy_ (u"ࠩ࡯ࡥࡹ࡫࡮ࡤࡻࠪࢃ")]
      bstack1l11l11l11_opy_[hub_url] = latency
    bstack1lll111l1_opy_ = min(bstack1l11l11l11_opy_, key= lambda x: bstack1l11l11l11_opy_[x])
    bstack1l1l1ll1_opy_ = bstack1lll111l1_opy_
    logger.debug(bstack11l11ll1ll_opy_.format(bstack1lll111l1_opy_))
  except Exception as e:
    logger.debug(bstack11lll1ll11_opy_.format(e))
from browserstack_sdk.bstack1lllll11l1_opy_ import *
from browserstack_sdk.bstack11l11lllll_opy_ import *
from browserstack_sdk.bstack111l1111l_opy_ import *
import logging
import requests
from bstack_utils.constants import *
from bstack_utils.bstack1l1lll1l11_opy_ import get_logger
from bstack_utils.measure import measure
logger = get_logger(__name__)
@measure(event_name=EVENTS.bstack1l11lll1l1_opy_, stage=STAGE.bstack1lll1l11l_opy_)
def bstack11lll1l1ll_opy_():
    global bstack1l1l1ll1_opy_
    try:
        bstack11l111111l_opy_ = bstack1ll1l111_opy_()
        bstack111l11111_opy_(bstack11l111111l_opy_)
        hub_url = bstack11l111111l_opy_.get(bstack11l1l_opy_ (u"ࠥࡹࡷࡲࠢࢄ"), bstack11l1l_opy_ (u"ࠦࠧࢅ"))
        if hub_url.endswith(bstack11l1l_opy_ (u"ࠬ࠵ࡷࡥ࠱࡫ࡹࡧ࠭ࢆ")):
            hub_url = hub_url.rsplit(bstack11l1l_opy_ (u"࠭࠯ࡸࡦ࠲࡬ࡺࡨࠧࢇ"), 1)[0]
        if hub_url.startswith(bstack11l1l_opy_ (u"ࠧࡩࡶࡷࡴ࠿࠵࠯ࠨ࢈")):
            hub_url = hub_url[7:]
        elif hub_url.startswith(bstack11l1l_opy_ (u"ࠨࡪࡷࡸࡵࡹ࠺࠰࠱ࠪࢉ")):
            hub_url = hub_url[8:]
        bstack1l1l1ll1_opy_ = hub_url
    except Exception as e:
        raise RuntimeError(e)
def bstack1ll1l111_opy_():
    global CONFIG
    bstack11l1l1ll_opy_ = CONFIG.get(bstack11l1l_opy_ (u"ࠩࡷࡹࡷࡨ࡯ࡔࡥࡤࡰࡪࡕࡰࡵ࡫ࡲࡲࡸ࠭ࢊ"), {}).get(bstack11l1l_opy_ (u"ࠪ࡫ࡷ࡯ࡤࡏࡣࡰࡩࠬࢋ"), bstack11l1l_opy_ (u"ࠫࡓࡕ࡟ࡈࡔࡌࡈࡤࡔࡁࡎࡇࡢࡔࡆ࡙ࡓࡆࡆࠪࢌ"))
    if not isinstance(bstack11l1l1ll_opy_, str):
        raise ValueError(bstack11l1l_opy_ (u"ࠧࡇࡔࡔࠢ࠽ࠤࡌࡸࡩࡥࠢࡱࡥࡲ࡫ࠠ࡮ࡷࡶࡸࠥࡨࡥࠡࡣࠣࡺࡦࡲࡩࡥࠢࡶࡸࡷ࡯࡮ࡨࠤࢍ"))
    try:
        bstack11l111111l_opy_ = bstack111lll111_opy_(bstack11l1l1ll_opy_)
        return bstack11l111111l_opy_
    except Exception as e:
        logger.error(bstack11l1l_opy_ (u"ࠨࡁࡕࡕࠣ࠾ࠥࡋࡲࡳࡱࡵࠤ࡮ࡴࠠࡨࡧࡷࡸ࡮ࡴࡧࠡࡩࡵ࡭ࡩࠦࡤࡦࡶࡤ࡭ࡱࡹࠠ࠻ࠢࡾࢁࠧࢎ").format(str(e)))
        return {}
def bstack111lll111_opy_(bstack11l1l1ll_opy_):
    global CONFIG
    try:
        if not CONFIG[bstack11l1l_opy_ (u"ࠧࡶࡵࡨࡶࡓࡧ࡭ࡦࠩ࢏")] or not CONFIG[bstack11l1l_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡌࡧࡼࠫ࢐")]:
            raise ValueError(bstack11l1l_opy_ (u"ࠤࡐ࡭ࡸࡹࡩ࡯ࡩࠣࡆࡷࡵࡷࡴࡧࡵࡗࡹࡧࡣ࡬ࠢࡸࡷࡪࡸ࡮ࡢ࡯ࡨࠤࡴࡸࠠࡢࡥࡦࡩࡸࡹࠠ࡬ࡧࡼࠦ࢑"))
        url = bstack1l1l1lll_opy_ + bstack11l1l1ll_opy_
        auth = (CONFIG[bstack11l1l_opy_ (u"ࠪࡹࡸ࡫ࡲࡏࡣࡰࡩࠬ࢒")], CONFIG[bstack11l1l_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶࡏࡪࡿࠧ࢓")])
        response = requests.get(url, auth=auth)
        if response.status_code == 200 and response.text:
            bstack1l11llll1_opy_ = json.loads(response.text)
            return bstack1l11llll1_opy_
    except ValueError as ve:
        logger.error(bstack11l1l_opy_ (u"ࠧࡇࡔࡔࠢ࠽ࠤࡊࡸࡲࡰࡴࠣ࡭ࡳࠦࡦࡦࡶࡦ࡬࡮ࡴࡧࠡࡩࡵ࡭ࡩࠦࡤࡦࡶࡤ࡭ࡱࡹࠠ࠻ࠢࡾࢁࠧ࢔").format(str(ve)))
        raise ValueError(ve)
    except Exception as e:
        logger.error(bstack11l1l_opy_ (u"ࠨࡁࡕࡕࠣ࠾ࠥࡋࡲࡳࡱࡵࠤ࡮ࡴࠠࡧࡧࡷࡧ࡭࡯࡮ࡨࠢࡪࡶ࡮ࡪࠠࡥࡧࡷࡥ࡮ࡲࡳࠡ࠼ࠣࡿࢂࠨ࢕").format(str(e)))
        raise RuntimeError(e)
    return {}
def bstack111l11111_opy_(bstack1lll111111_opy_):
    global CONFIG
    if bstack11l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࠫ࢖") not in CONFIG or str(CONFIG[bstack11l1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡌࡰࡥࡤࡰࠬࢗ")]).lower() == bstack11l1l_opy_ (u"ࠩࡩࡥࡱࡹࡥࠨ࢘"):
        CONFIG[bstack11l1l_opy_ (u"ࠪࡰࡴࡩࡡ࡭࢙ࠩ")] = False
    elif bstack11l1l_opy_ (u"ࠫ࡮ࡹࡔࡳ࡫ࡤࡰࡌࡸࡩࡥ࢚ࠩ") in bstack1lll111111_opy_:
        bstack111lll11_opy_ = CONFIG.get(bstack11l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࡑࡳࡸ࡮ࡵ࡮ࡴ࢛ࠩ"), {})
        logger.debug(bstack11l1l_opy_ (u"ࠨࡁࡕࡕࠣ࠾ࠥࡋࡸࡪࡵࡷ࡭ࡳ࡭ࠠ࡭ࡱࡦࡥࡱࠦ࡯ࡱࡶ࡬ࡳࡳࡹ࠺ࠡࠧࡶࠦ࢜"), bstack111lll11_opy_)
        bstack11ll1lll1l_opy_ = bstack1lll111111_opy_.get(bstack11l1l_opy_ (u"ࠢࡤࡷࡶࡸࡴࡳࡒࡦࡲࡨࡥࡹ࡫ࡲࡴࠤ࢝"), [])
        bstack1lllll1l1_opy_ = bstack11l1l_opy_ (u"ࠣ࠮ࠥ࢞").join(bstack11ll1lll1l_opy_)
        logger.debug(bstack11l1l_opy_ (u"ࠤࡄࡘࡘࠦ࠺ࠡࡅࡸࡷࡹࡵ࡭ࠡࡴࡨࡴࡪࡧࡴࡦࡴࠣࡷࡹࡸࡩ࡯ࡩ࠽ࠤࠪࡹࠢ࢟"), bstack1lllll1l1_opy_)
        bstack11l1111l_opy_ = {
            bstack11l1l_opy_ (u"ࠥࡰࡴࡩࡡ࡭ࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠧࢠ"): bstack11l1l_opy_ (u"ࠦࡦࡺࡳ࠮ࡴࡨࡴࡪࡧࡴࡦࡴࠥࢡ"),
            bstack11l1l_opy_ (u"ࠧ࡬࡯ࡳࡥࡨࡐࡴࡩࡡ࡭ࠤࢢ"): bstack11l1l_opy_ (u"ࠨࡴࡳࡷࡨࠦࢣ"),
            bstack11l1l_opy_ (u"ࠢࡤࡷࡶࡸࡴࡳ࠭ࡳࡧࡳࡩࡦࡺࡥࡳࠤࢤ"): bstack1lllll1l1_opy_
        }
        bstack111lll11_opy_.update(bstack11l1111l_opy_)
        logger.debug(bstack11l1l_opy_ (u"ࠣࡃࡗࡗࠥࡀࠠࡖࡲࡧࡥࡹ࡫ࡤࠡ࡮ࡲࡧࡦࡲࠠࡰࡲࡷ࡭ࡴࡴࡳ࠻ࠢࠨࡷࠧࢥ"), bstack111lll11_opy_)
        CONFIG[bstack11l1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࡍࡱࡦࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭ࢦ")] = bstack111lll11_opy_
        logger.debug(bstack11l1l_opy_ (u"ࠥࡅ࡙࡙ࠠ࠻ࠢࡉ࡭ࡳࡧ࡬ࠡࡅࡒࡒࡋࡏࡇ࠻ࠢࠨࡷࠧࢧ"), CONFIG)
def bstack1l1l111l1_opy_():
    bstack11l111111l_opy_ = bstack1ll1l111_opy_()
    if not bstack11l111111l_opy_[bstack11l1l_opy_ (u"ࠫࡵࡲࡡࡺࡹࡵ࡭࡬࡮ࡴࡖࡴ࡯ࠫࢨ")]:
      raise ValueError(bstack11l1l_opy_ (u"ࠧࡶ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵࡗࡵࡰࠥ࡯ࡳࠡ࡯࡬ࡷࡸ࡯࡮ࡨࠢࡩࡶࡴࡳࠠࡨࡴ࡬ࡨࠥࡪࡥࡵࡣ࡬ࡰࡸ࠴ࠢࢩ"))
    return bstack11l111111l_opy_[bstack11l1l_opy_ (u"࠭ࡰ࡭ࡣࡼࡻࡷ࡯ࡧࡩࡶࡘࡶࡱ࠭ࢪ")] + bstack11l1l_opy_ (u"ࠧࡀࡥࡤࡴࡸࡃࠧࢫ")
@measure(event_name=EVENTS.bstack1l1ll1l1l1_opy_, stage=STAGE.bstack1lll1l11l_opy_)
def bstack1lllllllll_opy_() -> list:
    global CONFIG
    result = []
    if CONFIG:
        auth = (CONFIG[bstack11l1l_opy_ (u"ࠨࡷࡶࡩࡷࡔࡡ࡮ࡧࠪࢬ")], CONFIG[bstack11l1l_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴࡍࡨࡽࠬࢭ")])
        url = bstack11l1ll1l1_opy_
        logger.debug(bstack11l1l_opy_ (u"ࠥࡅࡹࡺࡥ࡮ࡲࡷ࡭ࡳ࡭ࠠࡵࡱࠣࡪࡪࡺࡣࡩࠢࡥࡹ࡮ࡲࡤࡴࠢࡩࡶࡴࡳࠠࡃࡴࡲࡻࡸ࡫ࡲࡔࡶࡤࡧࡰࠦࡔࡶࡴࡥࡳࡘࡩࡡ࡭ࡧࠣࡅࡕࡏࠢࢮ"))
        try:
            response = requests.get(url, auth=auth, headers={bstack11l1l_opy_ (u"ࠦࡈࡵ࡮ࡵࡧࡱࡸ࠲࡚ࡹࡱࡧࠥࢯ"): bstack11l1l_opy_ (u"ࠧࡧࡰࡱ࡮࡬ࡧࡦࡺࡩࡰࡰ࠲࡮ࡸࡵ࡮ࠣࢰ")})
            if response.status_code == 200:
                bstack11l1111lll_opy_ = json.loads(response.text)
                bstack1l11ll1ll1_opy_ = bstack11l1111lll_opy_.get(bstack11l1l_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡸ࠭ࢱ"), [])
                if bstack1l11ll1ll1_opy_:
                    bstack1l1lll11l1_opy_ = bstack1l11ll1ll1_opy_[0]
                    build_hashed_id = bstack1l1lll11l1_opy_.get(bstack11l1l_opy_ (u"ࠧࡩࡣࡶ࡬ࡪࡪ࡟ࡪࡦࠪࢲ"))
                    bstack11l11llll_opy_ = bstack11l11l1l_opy_ + build_hashed_id
                    result.extend([build_hashed_id, bstack11l11llll_opy_])
                    logger.info(bstack11l11l11l1_opy_.format(bstack11l11llll_opy_))
                    bstack1111l111l_opy_ = CONFIG[bstack11l1l_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠫࢳ")]
                    if bstack11l1l_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫࢴ") in CONFIG:
                      bstack1111l111l_opy_ += bstack11l1l_opy_ (u"ࠪࠤࠬࢵ") + CONFIG[bstack11l1l_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭ࢶ")]
                    if bstack1111l111l_opy_ != bstack1l1lll11l1_opy_.get(bstack11l1l_opy_ (u"ࠬࡴࡡ࡮ࡧࠪࢷ")):
                      logger.debug(bstack11l11l1l11_opy_.format(bstack1l1lll11l1_opy_.get(bstack11l1l_opy_ (u"࠭࡮ࡢ࡯ࡨࠫࢸ")), bstack1111l111l_opy_))
                    return result
                else:
                    logger.debug(bstack11l1l_opy_ (u"ࠢࡂࡖࡖࠤ࠿ࠦࡎࡰࠢࡥࡹ࡮ࡲࡤࡴࠢࡩࡳࡺࡴࡤࠡ࡫ࡱࠤࡹ࡮ࡥࠡࡴࡨࡷࡵࡵ࡮ࡴࡧ࠱ࠦࢹ"))
            else:
                logger.debug(bstack11l1l_opy_ (u"ࠣࡃࡗࡗࠥࡀࠠࡇࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡪࡪࡺࡣࡩࠢࡥࡹ࡮ࡲࡤࡴ࠰ࠥࢺ"))
        except Exception as e:
            logger.error(bstack11l1l_opy_ (u"ࠤࡄࡘࡘࠦ࠺ࠡࡇࡵࡶࡴࡸࠠࡪࡰࠣ࡫ࡪࡺࡴࡪࡰࡪࠤࡧࡻࡩ࡭ࡦࡶࠤ࠿ࠦࡻࡾࠤࢻ").format(str(e)))
    else:
        logger.debug(bstack11l1l_opy_ (u"ࠥࡅ࡙࡙ࠠ࠻ࠢࡆࡓࡓࡌࡉࡈࠢ࡬ࡷࠥࡴ࡯ࡵࠢࡶࡩࡹ࠴ࠠࡖࡰࡤࡦࡱ࡫ࠠࡵࡱࠣࡪࡪࡺࡣࡩࠢࡥࡹ࡮ࡲࡤࡴ࠰ࠥࢼ"))
    return [None, None]
from browserstack_sdk.sdk_cli.cli import cli
from browserstack_sdk.sdk_cli.bstack1l1l1lllll_opy_ import bstack1l1l1lllll_opy_, bstack111111lll_opy_, bstack1l1lll1l1l_opy_, bstack1llll1111l_opy_
from bstack_utils.measure import bstack11l1l11ll_opy_
from bstack_utils.measure import measure
from bstack_utils.percy import *
from bstack_utils.percy_sdk import PercySDK
from bstack_utils.bstack1lll1lll11_opy_ import bstack1ll1lll1_opy_
from bstack_utils.messages import *
from bstack_utils import bstack1l1lll1l11_opy_
from bstack_utils.constants import *
from bstack_utils.helper import bstack1ll1l1ll1_opy_, bstack1l111l111l_opy_, bstack1l1l1ll1l_opy_, bstack11lll11l_opy_, \
  bstack11lll11ll1_opy_, \
  Notset, bstack1l11llll_opy_, \
  bstack11l11ll11l_opy_, bstack111l11l1_opy_, bstack11l1lll111_opy_, bstack1l111l11l1_opy_, bstack11ll1l1l_opy_, bstack1l11ll11l_opy_, \
  bstack1l11ll111_opy_, \
  bstack111llllll1_opy_, bstack1lll11llll_opy_, bstack11l1l1ll11_opy_, bstack1l1111l1ll_opy_, \
  bstack11111111_opy_, bstack1l1ll1ll_opy_, bstack1llll1ll1_opy_, bstack111l1ll11_opy_, bstack1lllll11ll_opy_
from bstack_utils.bstack11llll11ll_opy_ import bstack1ll1l1l11_opy_
from bstack_utils.bstack1lll1ll1l1_opy_ import bstack111ll111l_opy_, bstack11ll1l111l_opy_
from bstack_utils.bstack11l1lll11_opy_ import bstack1lll111l11_opy_
from bstack_utils.bstack111l11ll1_opy_ import bstack111lllll1l_opy_, bstack11lll1lll1_opy_
from bstack_utils.bstack111lll1l_opy_ import bstack111lll1l_opy_
from bstack_utils.bstack11111l11_opy_ import bstack11lllll1_opy_
from bstack_utils.proxy import bstack11l1l1l111_opy_, bstack1lllll111l_opy_, bstack1l1ll1l1ll_opy_, bstack11ll11ll1_opy_
from bstack_utils.bstack11l1ll1ll_opy_ import bstack11ll1ll1_opy_, bstack1l1ll1l11_opy_
import bstack_utils.bstack1l1llll1l_opy_ as bstack1ll11l1l1_opy_
import bstack_utils.bstack1l11lll11l_opy_ as bstack111lllll11_opy_
from browserstack_sdk.sdk_cli.cli import cli
from browserstack_sdk.sdk_cli.utils.bstack1ll1l1l1l_opy_ import bstack1ll111ll1_opy_
from bstack_utils.bstack1111l1ll_opy_ import bstack11llllll1l_opy_
from bstack_utils.bstack11ll111l1_opy_ import bstack1lll1l1l1_opy_
if os.getenv(bstack11l1l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡇࡑࡏ࡟ࡉࡑࡒࡏࡘ࠭ࢽ")):
  cli.bstack1lll1l1l1l_opy_()
else:
  os.environ[bstack11l1l_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡈࡒࡉࡠࡊࡒࡓࡐ࡙ࠧࢾ")] = bstack11l1l_opy_ (u"࠭ࡴࡳࡷࡨࠫࢿ")
bstack1lllllll1l_opy_ = bstack11l1l_opy_ (u"ࠧࠡࠢ࠲࠮ࠥࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾ࠢ࠭࠳ࡡࡴࠠࠡ࡫ࡩࠬࡵࡧࡧࡦࠢࡀࡁࡂࠦࡶࡰ࡫ࡧࠤ࠵࠯ࠠࡼ࡞ࡱࠤࠥࠦࡴࡳࡻࡾࡠࡳࠦࡣࡰࡰࡶࡸࠥ࡬ࡳࠡ࠿ࠣࡶࡪࡷࡵࡪࡴࡨࠬࡡ࠭ࡦࡴ࡞ࠪ࠭ࡀࡢ࡮ࠡࠢࠣࠤࠥ࡬ࡳ࠯ࡣࡳࡴࡪࡴࡤࡇ࡫࡯ࡩࡘࡿ࡮ࡤࠪࡥࡷࡹࡧࡣ࡬ࡡࡳࡥࡹ࡮ࠬࠡࡌࡖࡓࡓ࠴ࡳࡵࡴ࡬ࡲ࡬࡯ࡦࡺࠪࡳࡣ࡮ࡴࡤࡦࡺࠬࠤ࠰ࠦࠢ࠻ࠤࠣ࠯ࠥࡐࡓࡐࡐ࠱ࡷࡹࡸࡩ࡯ࡩ࡬ࡪࡾ࠮ࡊࡔࡑࡑ࠲ࡵࡧࡲࡴࡧࠫࠬࡦࡽࡡࡪࡶࠣࡲࡪࡽࡐࡢࡩࡨ࠶࠳࡫ࡶࡢ࡮ࡸࡥࡹ࡫ࠨࠣࠪࠬࠤࡂࡄࠠࡼࡿࠥ࠰ࠥࡢࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡥࡹࡧࡦࡹࡹࡵࡲ࠻ࠢࡾࠦࡦࡩࡴࡪࡱࡱࠦ࠿ࠦࠢࡨࡧࡷࡗࡪࡹࡳࡪࡱࡱࡈࡪࡺࡡࡪ࡮ࡶࠦࢂࡢࠧࠪࠫࠬ࡟ࠧ࡮ࡡࡴࡪࡨࡨࡤ࡯ࡤࠣ࡟ࠬࠤ࠰ࠦࠢ࠭࡞࡟ࡲࠧ࠯࡜࡯ࠢࠣࠤࠥࢃࡣࡢࡶࡦ࡬࠭࡫ࡸࠪࡽ࡟ࡲࠥࠦࠠࠡࡿ࡟ࡲࠥࠦࡽ࡝ࡰࠣࠤ࠴࠰ࠠ࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࠤ࠯࠵ࠧࣀ")
bstack1l11l1l1l1_opy_ = bstack11l1l_opy_ (u"ࠨ࡞ࡱ࠳࠯ࠦ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࠣ࠮࠴ࡢ࡮ࡤࡱࡱࡷࡹࠦࡢࡴࡶࡤࡧࡰࡥࡰࡢࡶ࡫ࠤࡂࠦࡰࡳࡱࡦࡩࡸࡹ࠮ࡢࡴࡪࡺࡠࡶࡲࡰࡥࡨࡷࡸ࠴ࡡࡳࡩࡹ࠲ࡱ࡫࡮ࡨࡶ࡫ࠤ࠲ࠦ࠳࡞࡞ࡱࡧࡴࡴࡳࡵࠢࡥࡷࡹࡧࡣ࡬ࡡࡦࡥࡵࡹࠠ࠾ࠢࡳࡶࡴࡩࡥࡴࡵ࠱ࡥࡷ࡭ࡶ࡜ࡲࡵࡳࡨ࡫ࡳࡴ࠰ࡤࡶ࡬ࡼ࠮࡭ࡧࡱ࡫ࡹ࡮ࠠ࠮ࠢ࠴ࡡࡡࡴࡣࡰࡰࡶࡸࠥࡶ࡟ࡪࡰࡧࡩࡽࠦ࠽ࠡࡲࡵࡳࡨ࡫ࡳࡴ࠰ࡤࡶ࡬ࡼ࡛ࡱࡴࡲࡧࡪࡹࡳ࠯ࡣࡵ࡫ࡻ࠴࡬ࡦࡰࡪࡸ࡭ࠦ࠭ࠡ࠴ࡠࡠࡳࡶࡲࡰࡥࡨࡷࡸ࠴ࡡࡳࡩࡹࠤࡂࠦࡰࡳࡱࡦࡩࡸࡹ࠮ࡢࡴࡪࡺ࠳ࡹ࡬ࡪࡥࡨࠬ࠵࠲ࠠࡱࡴࡲࡧࡪࡹࡳ࠯ࡣࡵ࡫ࡻ࠴࡬ࡦࡰࡪࡸ࡭ࠦ࠭ࠡ࠵ࠬࡠࡳࡩ࡯࡯ࡵࡷࠤ࡮ࡳࡰࡰࡴࡷࡣࡵࡲࡡࡺࡹࡵ࡭࡬࡮ࡴ࠵ࡡࡥࡷࡹࡧࡣ࡬ࠢࡀࠤࡷ࡫ࡱࡶ࡫ࡵࡩ࠭ࠨࡰ࡭ࡣࡼࡻࡷ࡯ࡧࡩࡶࠥ࠭ࡀࡢ࡮ࡪ࡯ࡳࡳࡷࡺ࡟ࡱ࡮ࡤࡽࡼࡸࡩࡨࡪࡷ࠸ࡤࡨࡳࡵࡣࡦ࡯࠳ࡩࡨࡳࡱࡰ࡭ࡺࡳ࠮࡭ࡣࡸࡲࡨ࡮ࠠ࠾ࠢࡤࡷࡾࡴࡣࠡࠪ࡯ࡥࡺࡴࡣࡩࡑࡳࡸ࡮ࡵ࡮ࡴࠫࠣࡁࡃࠦࡻ࡝ࡰ࡯ࡩࡹࠦࡣࡢࡲࡶ࠿ࡡࡴࡴࡳࡻࠣࡿࡡࡴࡣࡢࡲࡶࠤࡂࠦࡊࡔࡑࡑ࠲ࡵࡧࡲࡴࡧࠫࡦࡸࡺࡡࡤ࡭ࡢࡧࡦࡶࡳࠪ࡞ࡱࠤࠥࢃࠠࡤࡣࡷࡧ࡭࠮ࡥࡹࠫࠣࡿࡡࡴࠠࠡࠢࠣࢁࡡࡴࠠࠡࡴࡨࡸࡺࡸ࡮ࠡࡣࡺࡥ࡮ࡺࠠࡪ࡯ࡳࡳࡷࡺ࡟ࡱ࡮ࡤࡽࡼࡸࡩࡨࡪࡷ࠸ࡤࡨࡳࡵࡣࡦ࡯࠳ࡩࡨࡳࡱࡰ࡭ࡺࡳ࠮ࡤࡱࡱࡲࡪࡩࡴࠩࡽ࡟ࡲࠥࠦࠠࠡࡹࡶࡉࡳࡪࡰࡰ࡫ࡱࡸ࠿ࠦࡠࡸࡵࡶ࠾࠴࠵ࡣࡥࡲ࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡦࡳࡲ࠵ࡰ࡭ࡣࡼࡻࡷ࡯ࡧࡩࡶࡂࡧࡦࡶࡳ࠾ࠦࡾࡩࡳࡩ࡯ࡥࡧࡘࡖࡎࡉ࡯࡮ࡲࡲࡲࡪࡴࡴࠩࡌࡖࡓࡓ࠴ࡳࡵࡴ࡬ࡲ࡬࡯ࡦࡺࠪࡦࡥࡵࡹࠩࠪࡿࡣ࠰ࡡࡴࠠࠡࠢࠣ࠲࠳࠴࡬ࡢࡷࡱࡧ࡭ࡕࡰࡵ࡫ࡲࡲࡸࡢ࡮ࠡࠢࢀ࠭ࡡࡴࡽ࡝ࡰ࠲࠮ࠥࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾ࠢ࠭࠳ࡡࡴࠧࣁ")
from ._version import __version__
bstack111l1l1l1_opy_ = None
CONFIG = {}
bstack1111l1ll1_opy_ = {}
bstack11l1llll1l_opy_ = {}
bstack1ll1llll1l_opy_ = None
bstack111111l1l_opy_ = None
bstack11l1ll1l_opy_ = None
bstack11ll1111ll_opy_ = -1
bstack1ll1ll1lll_opy_ = 0
bstack1l111l111_opy_ = bstack1lllll1l1l_opy_
bstack1l1l11ll1_opy_ = 1
bstack111ll1l11_opy_ = False
bstack1l1llll1ll_opy_ = False
bstack11l1ll111l_opy_ = bstack11l1l_opy_ (u"ࠩࠪࣂ")
bstack11l11l1ll1_opy_ = bstack11l1l_opy_ (u"ࠪࠫࣃ")
bstack1ll1ll111l_opy_ = False
bstack11ll1l1lll_opy_ = True
bstack1l1l11ll1l_opy_ = bstack11l1l_opy_ (u"ࠫࠬࣄ")
bstack1ll111111l_opy_ = []
bstack1l1111ll_opy_ = threading.Lock()
bstack1l1111llll_opy_ = threading.Lock()
bstack1l1l1ll1_opy_ = bstack11l1l_opy_ (u"ࠬ࠭ࣅ")
bstack1ll1ll11l1_opy_ = False
bstack11l1111l1l_opy_ = None
bstack1l11l11111_opy_ = None
bstack1lll111l_opy_ = None
bstack11ll1111_opy_ = -1
bstack11111lll_opy_ = os.path.join(os.path.expanduser(bstack11l1l_opy_ (u"࠭ࡾࠨࣆ")), bstack11l1l_opy_ (u"ࠧ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠧࣇ"), bstack11l1l_opy_ (u"ࠨ࠰ࡵࡳࡧࡵࡴ࠮ࡴࡨࡴࡴࡸࡴ࠮ࡪࡨࡰࡵ࡫ࡲ࠯࡬ࡶࡳࡳ࠭ࣈ"))
bstack1llll1lll1_opy_ = 0
bstack111l11ll_opy_ = 0
bstack11lllll11l_opy_ = []
bstack1l11lll111_opy_ = []
bstack1ll1ll1l11_opy_ = []
bstack11111l1l1_opy_ = []
bstack1ll1111l_opy_ = bstack11l1l_opy_ (u"ࠩࠪࣉ")
bstack1llll1lll_opy_ = bstack11l1l_opy_ (u"ࠪࠫ࣊")
bstack1lllllll1_opy_ = False
bstack1ll1l1ll_opy_ = False
bstack11ll11l111_opy_ = {}
bstack11l11lll1_opy_ = {}
bstack1l1l11111_opy_ = None
bstack11llllllll_opy_ = None
bstack1l1l1lll11_opy_ = None
bstack1ll11ll1l1_opy_ = None
bstack11l1l111ll_opy_ = None
bstack1111l11l_opy_ = None
bstack1111l111_opy_ = None
bstack1l1l1l1lll_opy_ = None
bstack11ll1l11_opy_ = None
bstack1l111ll1_opy_ = None
bstack11l1l111l1_opy_ = None
bstack1ll1l11l_opy_ = None
bstack11l11l11_opy_ = None
bstack1l11l1ll11_opy_ = None
bstack1l1111ll1l_opy_ = None
bstack1lll1l1ll_opy_ = None
bstack11l1ll11l1_opy_ = None
bstack1l1l1ll11l_opy_ = None
bstack1ll1l11l11_opy_ = None
bstack111ll11l_opy_ = None
bstack1l1l11l1ll_opy_ = None
bstack11l111ll1_opy_ = None
bstack1lllll1l11_opy_ = None
thread_local = threading.local()
bstack1l1lll1ll1_opy_ = False
bstack1ll1l1l1l1_opy_ = bstack11l1l_opy_ (u"ࠦࠧ࣋")
logger = bstack1l1lll1l11_opy_.get_logger(__name__, bstack1l111l111_opy_)
bstack1ll11l1ll_opy_ = bstack1l1lll1l11_opy_.bstack1l111111_opy_(__name__)
bstack1l1ll11111_opy_ = Config.bstack11l1l11ll1_opy_()
percy = bstack1l111lll1l_opy_()
bstack1lllll1ll1_opy_ = bstack1ll1lll1_opy_()
bstack11ll11l11l_opy_ = bstack111l1111l_opy_()
def bstack11l1lllll1_opy_():
  global CONFIG
  global bstack1lllllll1_opy_
  global bstack1l1ll11111_opy_
  testContextOptions = bstack1l1ll1ll11_opy_(CONFIG)
  if bstack11lll11ll1_opy_(CONFIG):
    if (bstack11l1l_opy_ (u"ࠬࡹ࡫ࡪࡲࡖࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠧ࣌") in testContextOptions and str(testContextOptions[bstack11l1l_opy_ (u"࠭ࡳ࡬࡫ࡳࡗࡪࡹࡳࡪࡱࡱࡒࡦࡳࡥࠨ࣍")]).lower() == bstack11l1l_opy_ (u"ࠧࡵࡴࡸࡩࠬ࣎")):
      bstack1lllllll1_opy_ = True
    bstack1l1ll11111_opy_.bstack1l11ll1l1_opy_(testContextOptions.get(bstack11l1l_opy_ (u"ࠨࡵ࡮࡭ࡵ࡙ࡥࡴࡵ࡬ࡳࡳ࡙ࡴࡢࡶࡸࡷ࣏ࠬ"), False))
  else:
    bstack1lllllll1_opy_ = True
    bstack1l1ll11111_opy_.bstack1l11ll1l1_opy_(True)
def bstack11l11l1lll_opy_():
  from appium.version import version as appium_version
  return version.parse(appium_version)
def bstack1l1l1l1ll1_opy_():
  from selenium import webdriver
  return version.parse(webdriver.__version__)
def bstack11l1ll1l1l_opy_():
  global bstack11l11lll1_opy_
  args = sys.argv
  for i in range(len(args)):
    if bstack11l1l_opy_ (u"ࠤ࠰࠱ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡦࡳࡳ࡬ࡩࡨࡨ࡬ࡰࡪࠨ࣐") == args[i].lower() or bstack11l1l_opy_ (u"ࠥ࠱࠲ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡨࡵ࡮ࡧ࡫ࡪ࣑ࠦ") == args[i].lower():
      path = args[i + 1]
      sys.argv.remove(args[i])
      sys.argv.remove(path)
      bstack11l11lll1_opy_[bstack11l1l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡇࡔࡔࡆࡊࡉࡢࡊࡎࡒࡅࠨ࣒")] = path
      return path
  return None
bstack1l11lll1l_opy_ = re.compile(bstack11l1l_opy_ (u"ࡷࠨ࠮ࠫࡁ࡟ࠨࢀ࠮࠮ࠫࡁࠬࢁ࠳࠰࠿࣓ࠣ"))
def bstack11l1ll1111_opy_(loader, node):
  value = loader.construct_scalar(node)
  for group in bstack1l11lll1l_opy_.findall(value):
    if group is not None and os.environ.get(group) is not None:
      value = value.replace(bstack11l1l_opy_ (u"ࠨࠤࡼࠤࣔ") + group + bstack11l1l_opy_ (u"ࠢࡾࠤࣕ"), os.environ.get(group))
  return value
def bstack11l11l11ll_opy_():
  global bstack1lllll1l11_opy_
  if bstack1lllll1l11_opy_ is None:
        bstack1lllll1l11_opy_ = bstack11l1ll1l1l_opy_()
  bstack1l1llll1_opy_ = bstack1lllll1l11_opy_
  if bstack1l1llll1_opy_ and os.path.exists(os.path.abspath(bstack1l1llll1_opy_)):
    fileName = bstack1l1llll1_opy_
  if bstack11l1l_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡄࡑࡑࡊࡎࡍ࡟ࡇࡋࡏࡉࠬࣖ") in os.environ and os.path.exists(
          os.path.abspath(os.environ[bstack11l1l_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡅࡒࡒࡋࡏࡇࡠࡈࡌࡐࡊ࠭ࣗ")])) and not bstack11l1l_opy_ (u"ࠪࡪ࡮ࡲࡥࡏࡣࡰࡩࠬࣘ") in locals():
    fileName = os.environ[bstack11l1l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡇࡔࡔࡆࡊࡉࡢࡊࡎࡒࡅࠨࣙ")]
  if bstack11l1l_opy_ (u"ࠬ࡬ࡩ࡭ࡧࡑࡥࡲ࡫ࠧࣚ") in locals():
    bstack1llllll_opy_ = os.path.abspath(fileName)
  else:
    bstack1llllll_opy_ = bstack11l1l_opy_ (u"࠭ࠧࣛ")
  bstack1l1ll1lll_opy_ = os.getcwd()
  bstack1ll1ll111_opy_ = bstack11l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡹ࡮࡮ࠪࣜ")
  bstack1ll1lll111_opy_ = bstack11l1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡺࡣࡰࡰࠬࣝ")
  while (not os.path.exists(bstack1llllll_opy_)) and bstack1l1ll1lll_opy_ != bstack11l1l_opy_ (u"ࠤࠥࣞ"):
    bstack1llllll_opy_ = os.path.join(bstack1l1ll1lll_opy_, bstack1ll1ll111_opy_)
    if not os.path.exists(bstack1llllll_opy_):
      bstack1llllll_opy_ = os.path.join(bstack1l1ll1lll_opy_, bstack1ll1lll111_opy_)
    if bstack1l1ll1lll_opy_ != os.path.dirname(bstack1l1ll1lll_opy_):
      bstack1l1ll1lll_opy_ = os.path.dirname(bstack1l1ll1lll_opy_)
    else:
      bstack1l1ll1lll_opy_ = bstack11l1l_opy_ (u"ࠥࠦࣟ")
  bstack1lllll1l11_opy_ = bstack1llllll_opy_ if os.path.exists(bstack1llllll_opy_) else None
  return bstack1lllll1l11_opy_
def bstack1ll11l11ll_opy_(config):
    if bstack11l1l_opy_ (u"ࠫࡹ࡫ࡳࡵࡔࡨࡴࡴࡸࡴࡪࡰࡪࠫ࣠") in config:
      config[bstack11l1l_opy_ (u"ࠬࡺࡥࡴࡶࡒࡦࡸ࡫ࡲࡷࡣࡥ࡭ࡱ࡯ࡴࡺࠩ࣡")] = config[bstack11l1l_opy_ (u"࠭ࡴࡦࡵࡷࡖࡪࡶ࡯ࡳࡶ࡬ࡲ࡬࠭࣢")]
    if bstack11l1l_opy_ (u"ࠧࡵࡧࡶࡸࡗ࡫ࡰࡰࡴࡷ࡭ࡳ࡭ࡏࡱࡶ࡬ࡳࡳࡹࣣࠧ") in config:
      config[bstack11l1l_opy_ (u"ࠨࡶࡨࡷࡹࡕࡢࡴࡧࡵࡺࡦࡨࡩ࡭࡫ࡷࡽࡔࡶࡴࡪࡱࡱࡷࠬࣤ")] = config[bstack11l1l_opy_ (u"ࠩࡷࡩࡸࡺࡒࡦࡲࡲࡶࡹ࡯࡮ࡨࡑࡳࡸ࡮ࡵ࡮ࡴࠩࣥ")]
def bstack11l1l1l1l_opy_():
  bstack1llllll_opy_ = bstack11l11l11ll_opy_()
  if not os.path.exists(bstack1llllll_opy_):
    bstack1ll11l111l_opy_(
      bstack111111ll_opy_.format(os.getcwd()))
  try:
    with open(bstack1llllll_opy_, bstack11l1l_opy_ (u"ࠪࡶࣦࠬ")) as stream:
      yaml.add_implicit_resolver(bstack11l1l_opy_ (u"ࠦࠦࡶࡡࡵࡪࡨࡼࠧࣧ"), bstack1l11lll1l_opy_)
      yaml.add_constructor(bstack11l1l_opy_ (u"ࠧࠧࡰࡢࡶ࡫ࡩࡽࠨࣨ"), bstack11l1ll1111_opy_)
      config = yaml.load(stream, yaml.FullLoader)
      bstack1ll11l11ll_opy_(config)
      return config
  except:
    with open(bstack1llllll_opy_, bstack11l1l_opy_ (u"࠭ࡲࠨࣩ")) as stream:
      try:
        config = yaml.safe_load(stream)
        bstack1ll11l11ll_opy_(config)
        return config
      except yaml.YAMLError as exc:
        bstack1ll11l111l_opy_(bstack1l1l11l11l_opy_.format(str(exc)))
def bstack1ll111l11_opy_(config):
  bstack1l1ll11ll1_opy_ = bstack1l11l111ll_opy_(config)
  for option in list(bstack1l1ll11ll1_opy_):
    if option.lower() in bstack11lllllll_opy_ and option != bstack11lllllll_opy_[option.lower()]:
      bstack1l1ll11ll1_opy_[bstack11lllllll_opy_[option.lower()]] = bstack1l1ll11ll1_opy_[option]
      del bstack1l1ll11ll1_opy_[option]
  return config
def bstack11llll1l11_opy_():
  global bstack11l1llll1l_opy_
  for key, bstack1ll1ll1111_opy_ in bstack11llll1l1_opy_.items():
    if isinstance(bstack1ll1ll1111_opy_, list):
      for var in bstack1ll1ll1111_opy_:
        if var in os.environ and os.environ[var] and str(os.environ[var]).strip():
          bstack11l1llll1l_opy_[key] = os.environ[var]
          break
    elif bstack1ll1ll1111_opy_ in os.environ and os.environ[bstack1ll1ll1111_opy_] and str(os.environ[bstack1ll1ll1111_opy_]).strip():
      bstack11l1llll1l_opy_[key] = os.environ[bstack1ll1ll1111_opy_]
  if bstack11l1l_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡌࡐࡅࡄࡐࡤࡏࡄࡆࡐࡗࡍࡋࡏࡅࡓࠩ࣪") in os.environ:
    bstack11l1llll1l_opy_[bstack11l1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡕࡷࡥࡨࡱࡌࡰࡥࡤࡰࡔࡶࡴࡪࡱࡱࡷࠬ࣫")] = {}
    bstack11l1llll1l_opy_[bstack11l1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࡍࡱࡦࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭࣬")][bstack11l1l_opy_ (u"ࠪࡰࡴࡩࡡ࡭ࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶ࣭ࠬ")] = os.environ[bstack11l1l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡐࡔࡉࡁࡍࡡࡌࡈࡊࡔࡔࡊࡈࡌࡉࡗ࣮࠭")]
def bstack111lll11ll_opy_():
  global bstack1111l1ll1_opy_
  global bstack1l1l11ll1l_opy_
  global bstack11l11lll1_opy_
  bstack1l1ll1l1l_opy_ = []
  for idx, val in enumerate(sys.argv):
    if idx < len(sys.argv) - 1 and bstack11l1l_opy_ (u"ࠬ࠳࠭ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴࡬ࡰࡥࡤࡰࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨ࣯").lower() == val.lower():
      bstack1111l1ll1_opy_[bstack11l1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࡒࡴࡹ࡯࡯࡯ࡵࣰࠪ")] = {}
      bstack1111l1ll1_opy_[bstack11l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡔࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࡓࡵࡺࡩࡰࡰࡶࣱࠫ")][bstack11l1l_opy_ (u"ࠨ࡮ࡲࡧࡦࡲࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࣲࠪ")] = sys.argv[idx + 1]
      bstack1l1ll1l1l_opy_.extend([idx, idx + 1])
      break
  for key, bstack11l1l1l1l1_opy_ in bstack11l11l1111_opy_.items():
    if isinstance(bstack11l1l1l1l1_opy_, list):
      for idx, val in enumerate(sys.argv):
        if idx >= len(sys.argv) - 1:
          continue
        for var in bstack11l1l1l1l1_opy_:
          if bstack11l1l_opy_ (u"ࠩ࠰࠱ࠬࣳ") + var.lower() == val.lower() and key not in bstack1111l1ll1_opy_:
            bstack1111l1ll1_opy_[key] = sys.argv[idx + 1]
            bstack1l1l11ll1l_opy_ += bstack11l1l_opy_ (u"ࠪࠤ࠲࠳ࠧࣴ") + var + bstack11l1l_opy_ (u"ࠫࠥ࠭ࣵ") + shlex.quote(sys.argv[idx + 1])
            bstack1lllll11ll_opy_(bstack11l11lll1_opy_, key, sys.argv[idx + 1])
            bstack1l1ll1l1l_opy_.extend([idx, idx + 1])
            break
    else:
      for idx, val in enumerate(sys.argv):
        if idx >= len(sys.argv) - 1:
          continue
        if bstack11l1l_opy_ (u"ࠬ࠳࠭ࠨࣶ") + bstack11l1l1l1l1_opy_.lower() == val.lower() and key not in bstack1111l1ll1_opy_:
          bstack1111l1ll1_opy_[key] = sys.argv[idx + 1]
          bstack1l1l11ll1l_opy_ += bstack11l1l_opy_ (u"࠭ࠠ࠮࠯ࠪࣷ") + bstack11l1l1l1l1_opy_ + bstack11l1l_opy_ (u"ࠧࠡࠩࣸ") + shlex.quote(sys.argv[idx + 1])
          bstack1lllll11ll_opy_(bstack11l11lll1_opy_, key, sys.argv[idx + 1])
          bstack1l1ll1l1l_opy_.extend([idx, idx + 1])
  for idx in sorted(set(bstack1l1ll1l1l_opy_), reverse=True):
    if idx < len(sys.argv):
      del sys.argv[idx]
def bstack1l11llll11_opy_(config):
  bstack1l1l1l1l11_opy_ = config.keys()
  for bstack1l1l1l11_opy_, bstack1l1111ll1_opy_ in bstack1l1lll1ll_opy_.items():
    if bstack1l1111ll1_opy_ in bstack1l1l1l1l11_opy_:
      config[bstack1l1l1l11_opy_] = config[bstack1l1111ll1_opy_]
      del config[bstack1l1111ll1_opy_]
  for bstack1l1l1l11_opy_, bstack1l1111ll1_opy_ in bstack111lll1ll_opy_.items():
    if isinstance(bstack1l1111ll1_opy_, list):
      for bstack1lll1ll1l_opy_ in bstack1l1111ll1_opy_:
        if bstack1lll1ll1l_opy_ in bstack1l1l1l1l11_opy_:
          config[bstack1l1l1l11_opy_] = config[bstack1lll1ll1l_opy_]
          del config[bstack1lll1ll1l_opy_]
          break
    elif bstack1l1111ll1_opy_ in bstack1l1l1l1l11_opy_:
      config[bstack1l1l1l11_opy_] = config[bstack1l1111ll1_opy_]
      del config[bstack1l1111ll1_opy_]
  for bstack1lll1ll1l_opy_ in list(config):
    for bstack11ll1l1111_opy_ in bstack11ll1l1l11_opy_:
      if bstack1lll1ll1l_opy_.lower() == bstack11ll1l1111_opy_.lower() and bstack1lll1ll1l_opy_ != bstack11ll1l1111_opy_:
        config[bstack11ll1l1111_opy_] = config[bstack1lll1ll1l_opy_]
        del config[bstack1lll1ll1l_opy_]
  bstack11lll1lll_opy_ = [{}]
  if not config.get(bstack11l1l_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࣹࠫ")):
    config[bstack11l1l_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࣺࠬ")] = [{}]
  bstack11lll1lll_opy_ = config[bstack11l1l_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ࣻ")]
  for platform in bstack11lll1lll_opy_:
    for bstack1lll1ll1l_opy_ in list(platform):
      for bstack11ll1l1111_opy_ in bstack11ll1l1l11_opy_:
        if bstack1lll1ll1l_opy_.lower() == bstack11ll1l1111_opy_.lower() and bstack1lll1ll1l_opy_ != bstack11ll1l1111_opy_:
          platform[bstack11ll1l1111_opy_] = platform[bstack1lll1ll1l_opy_]
          del platform[bstack1lll1ll1l_opy_]
  for bstack1l1l1l11_opy_, bstack1l1111ll1_opy_ in bstack111lll1ll_opy_.items():
    for platform in bstack11lll1lll_opy_:
      if isinstance(bstack1l1111ll1_opy_, list):
        for bstack1lll1ll1l_opy_ in bstack1l1111ll1_opy_:
          if bstack1lll1ll1l_opy_ in platform:
            platform[bstack1l1l1l11_opy_] = platform[bstack1lll1ll1l_opy_]
            del platform[bstack1lll1ll1l_opy_]
            break
      elif bstack1l1111ll1_opy_ in platform:
        platform[bstack1l1l1l11_opy_] = platform[bstack1l1111ll1_opy_]
        del platform[bstack1l1111ll1_opy_]
  for bstack1ll1l111l1_opy_ in bstack1l11111111_opy_:
    if bstack1ll1l111l1_opy_ in config:
      if not bstack1l11111111_opy_[bstack1ll1l111l1_opy_] in config:
        config[bstack1l11111111_opy_[bstack1ll1l111l1_opy_]] = {}
      config[bstack1l11111111_opy_[bstack1ll1l111l1_opy_]].update(config[bstack1ll1l111l1_opy_])
      del config[bstack1ll1l111l1_opy_]
  for platform in bstack11lll1lll_opy_:
    for bstack1ll1l111l1_opy_ in bstack1l11111111_opy_:
      if bstack1ll1l111l1_opy_ in list(platform):
        if not bstack1l11111111_opy_[bstack1ll1l111l1_opy_] in platform:
          platform[bstack1l11111111_opy_[bstack1ll1l111l1_opy_]] = {}
        platform[bstack1l11111111_opy_[bstack1ll1l111l1_opy_]].update(platform[bstack1ll1l111l1_opy_])
        del platform[bstack1ll1l111l1_opy_]
  config = bstack1ll111l11_opy_(config)
  return config
def bstack111ll1ll11_opy_(config):
  global bstack11l11l1ll1_opy_
  bstack1ll1l1llll_opy_ = False
  if bstack11l1l_opy_ (u"ࠫࡹࡻࡲࡣࡱࡖࡧࡦࡲࡥࠨࣼ") in config and str(config[bstack11l1l_opy_ (u"ࠬࡺࡵࡳࡤࡲࡗࡨࡧ࡬ࡦࠩࣽ")]).lower() != bstack11l1l_opy_ (u"࠭ࡦࡢ࡮ࡶࡩࠬࣾ"):
    if bstack11l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࠫࣿ") not in config or str(config[bstack11l1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡌࡰࡥࡤࡰࠬऀ")]).lower() == bstack11l1l_opy_ (u"ࠩࡩࡥࡱࡹࡥࠨँ"):
      config[bstack11l1l_opy_ (u"ࠪࡰࡴࡩࡡ࡭ࠩं")] = False
    else:
      bstack11l111111l_opy_ = bstack1ll1l111_opy_()
      if bstack11l1l_opy_ (u"ࠫ࡮ࡹࡔࡳ࡫ࡤࡰࡌࡸࡩࡥࠩः") in bstack11l111111l_opy_:
        if not bstack11l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࡑࡳࡸ࡮ࡵ࡮ࡴࠩऄ") in config:
          config[bstack11l1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࡒࡴࡹ࡯࡯࡯ࡵࠪअ")] = {}
        config[bstack11l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡔࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࡓࡵࡺࡩࡰࡰࡶࠫआ")][bstack11l1l_opy_ (u"ࠨ࡮ࡲࡧࡦࡲࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪइ")] = bstack11l1l_opy_ (u"ࠩࡤࡸࡸ࠳ࡲࡦࡲࡨࡥࡹ࡫ࡲࠨई")
        bstack1ll1l1llll_opy_ = True
        bstack11l11l1ll1_opy_ = config[bstack11l1l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡗࡹࡧࡣ࡬ࡎࡲࡧࡦࡲࡏࡱࡶ࡬ࡳࡳࡹࠧउ")].get(bstack11l1l_opy_ (u"ࠫࡱࡵࡣࡢ࡮ࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭ऊ"))
  if bstack11lll11ll1_opy_(config) and bstack11l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࠩऋ") in config and str(config[bstack11l1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࠪऌ")]).lower() != bstack11l1l_opy_ (u"ࠧࡧࡣ࡯ࡷࡪ࠭ऍ") and not bstack1ll1l1llll_opy_:
    if not bstack11l1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡕࡷࡥࡨࡱࡌࡰࡥࡤࡰࡔࡶࡴࡪࡱࡱࡷࠬऎ") in config:
      config[bstack11l1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࡍࡱࡦࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭ए")] = {}
    if not config[bstack11l1l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡗࡹࡧࡣ࡬ࡎࡲࡧࡦࡲࡏࡱࡶ࡬ࡳࡳࡹࠧऐ")].get(bstack11l1l_opy_ (u"ࠫࡸࡱࡩࡱࡄ࡬ࡲࡦࡸࡹࡊࡰ࡬ࡸ࡮ࡧ࡬ࡪࡵࡤࡸ࡮ࡵ࡮ࠨऑ")) and not bstack11l1l_opy_ (u"ࠬࡲ࡯ࡤࡣ࡯ࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧऒ") in config[bstack11l1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࡒࡴࡹ࡯࡯࡯ࡵࠪओ")]:
      bstack1lllll111_opy_ = datetime.datetime.now()
      bstack1l111lll1_opy_ = bstack1lllll111_opy_.strftime(bstack11l1l_opy_ (u"ࠧࠦࡦࡢࠩࡧࡥࠥࡉࠧࡐࠫऔ"))
      hostname = socket.gethostname()
      bstack11ll111111_opy_ = bstack11l1l_opy_ (u"ࠨࠩक").join(random.choices(string.ascii_lowercase + string.digits, k=4))
      identifier = bstack11l1l_opy_ (u"ࠩࡾࢁࡤࢁࡽࡠࡽࢀࠫख").format(bstack1l111lll1_opy_, hostname, bstack11ll111111_opy_)
      config[bstack11l1l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡗࡹࡧࡣ࡬ࡎࡲࡧࡦࡲࡏࡱࡶ࡬ࡳࡳࡹࠧग")][bstack11l1l_opy_ (u"ࠫࡱࡵࡣࡢ࡮ࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭घ")] = identifier
    bstack11l11l1ll1_opy_ = config[bstack11l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࡑࡳࡸ࡮ࡵ࡮ࡴࠩङ")].get(bstack11l1l_opy_ (u"࠭࡬ࡰࡥࡤࡰࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨच"))
  return config
def bstack1lll11l11_opy_():
  bstack1l1ll1ll1_opy_ =  bstack1l111l11l1_opy_()[bstack11l1l_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡥ࡮ࡶ࡯ࡥࡩࡷ࠭छ")]
  return bstack1l1ll1ll1_opy_ if bstack1l1ll1ll1_opy_ else -1
def bstack1l11l1111l_opy_(bstack1l1ll1ll1_opy_):
  global CONFIG
  if not bstack11l1l_opy_ (u"ࠨࠦࡾࡆ࡚ࡏࡌࡅࡡࡑ࡙ࡒࡈࡅࡓࡿࠪज") in CONFIG[bstack11l1l_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫझ")]:
    return
  CONFIG[bstack11l1l_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬञ")] = CONFIG[bstack11l1l_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭ट")].replace(
    bstack11l1l_opy_ (u"ࠬࠪࡻࡃࡗࡌࡐࡉࡥࡎࡖࡏࡅࡉࡗࢃࠧठ"),
    str(bstack1l1ll1ll1_opy_)
  )
def bstack1l1l1111_opy_():
  global CONFIG
  if not bstack11l1l_opy_ (u"࠭ࠤࡼࡆࡄࡘࡊࡥࡔࡊࡏࡈࢁࠬड") in CONFIG[bstack11l1l_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩढ")]:
    return
  bstack1lllll111_opy_ = datetime.datetime.now()
  bstack1l111lll1_opy_ = bstack1lllll111_opy_.strftime(bstack11l1l_opy_ (u"ࠨࠧࡧ࠱ࠪࡨ࠭ࠦࡊ࠽ࠩࡒ࠭ण"))
  CONFIG[bstack11l1l_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫत")] = CONFIG[bstack11l1l_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬथ")].replace(
    bstack11l1l_opy_ (u"ࠫࠩࢁࡄࡂࡖࡈࡣ࡙ࡏࡍࡆࡿࠪद"),
    bstack1l111lll1_opy_
  )
def bstack11lll1l1l1_opy_():
  global CONFIG
  if bstack11l1l_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧध") in CONFIG and not bool(CONFIG[bstack11l1l_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨन")]):
    del CONFIG[bstack11l1l_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩऩ")]
    return
  if not bstack11l1l_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪप") in CONFIG:
    CONFIG[bstack11l1l_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫफ")] = bstack11l1l_opy_ (u"ࠪࠧࠩࢁࡂࡖࡋࡏࡈࡤࡔࡕࡎࡄࡈࡖࢂ࠭ब")
  if bstack11l1l_opy_ (u"ࠫࠩࢁࡄࡂࡖࡈࡣ࡙ࡏࡍࡆࡿࠪभ") in CONFIG[bstack11l1l_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧम")]:
    bstack1l1l1111_opy_()
    os.environ[bstack11l1l_opy_ (u"࠭ࡂࡔࡖࡄࡇࡐࡥࡃࡐࡏࡅࡍࡓࡋࡄࡠࡄࡘࡍࡑࡊ࡟ࡊࡆࠪय")] = CONFIG[bstack11l1l_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩर")]
  if not bstack11l1l_opy_ (u"ࠨࠦࡾࡆ࡚ࡏࡌࡅࡡࡑ࡙ࡒࡈࡅࡓࡿࠪऱ") in CONFIG[bstack11l1l_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫल")]:
    return
  bstack1l1ll1ll1_opy_ = bstack11l1l_opy_ (u"ࠪࠫळ")
  bstack11l1lll1l1_opy_ = bstack1lll11l11_opy_()
  if bstack11l1lll1l1_opy_ != -1:
    bstack1l1ll1ll1_opy_ = bstack11l1l_opy_ (u"ࠫࡈࡏࠠࠨऴ") + str(bstack11l1lll1l1_opy_)
  if bstack1l1ll1ll1_opy_ == bstack11l1l_opy_ (u"ࠬ࠭व"):
    bstack111l1ll1l_opy_ = bstack1l11ll1111_opy_(CONFIG[bstack11l1l_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡓࡧ࡭ࡦࠩश")])
    if bstack111l1ll1l_opy_ != -1:
      bstack1l1ll1ll1_opy_ = str(bstack111l1ll1l_opy_)
  if bstack1l1ll1ll1_opy_:
    bstack1l11l1111l_opy_(bstack1l1ll1ll1_opy_)
    os.environ[bstack11l1l_opy_ (u"ࠧࡃࡕࡗࡅࡈࡑ࡟ࡄࡑࡐࡆࡎࡔࡅࡅࡡࡅ࡙ࡎࡒࡄࡠࡋࡇࠫष")] = CONFIG[bstack11l1l_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪस")]
def bstack1ll1l11lll_opy_(bstack11l1l111_opy_, bstack111llll11_opy_, path):
  bstack1llllll1ll_opy_ = {
    bstack11l1l_opy_ (u"ࠩ࡬ࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭ह"): bstack111llll11_opy_
  }
  if os.path.exists(path):
    bstack1l1l111ll1_opy_ = json.load(open(path, bstack11l1l_opy_ (u"ࠪࡶࡧ࠭ऺ")))
  else:
    bstack1l1l111ll1_opy_ = {}
  bstack1l1l111ll1_opy_[bstack11l1l111_opy_] = bstack1llllll1ll_opy_
  with open(path, bstack11l1l_opy_ (u"ࠦࡼ࠱ࠢऻ")) as outfile:
    json.dump(bstack1l1l111ll1_opy_, outfile)
def bstack1l11ll1111_opy_(bstack11l1l111_opy_):
  bstack11l1l111_opy_ = str(bstack11l1l111_opy_)
  bstack1lll11111_opy_ = os.path.join(os.path.expanduser(bstack11l1l_opy_ (u"ࠬࢄ़ࠧ")), bstack11l1l_opy_ (u"࠭࠮ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠭ऽ"))
  try:
    if not os.path.exists(bstack1lll11111_opy_):
      os.makedirs(bstack1lll11111_opy_)
    file_path = os.path.join(os.path.expanduser(bstack11l1l_opy_ (u"ࠧࡿࠩा")), bstack11l1l_opy_ (u"ࠨ࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࠨि"), bstack11l1l_opy_ (u"ࠩ࠱ࡦࡺ࡯࡬ࡥ࠯ࡱࡥࡲ࡫࠭ࡤࡣࡦ࡬ࡪ࠴ࡪࡴࡱࡱࠫी"))
    if not os.path.isfile(file_path):
      with open(file_path, bstack11l1l_opy_ (u"ࠪࡻࠬु")):
        pass
      with open(file_path, bstack11l1l_opy_ (u"ࠦࡼ࠱ࠢू")) as outfile:
        json.dump({}, outfile)
    with open(file_path, bstack11l1l_opy_ (u"ࠬࡸࠧृ")) as bstack11l1llll11_opy_:
      bstack1llllllll_opy_ = json.load(bstack11l1llll11_opy_)
    if bstack11l1l111_opy_ in bstack1llllllll_opy_:
      bstack11l11111_opy_ = bstack1llllllll_opy_[bstack11l1l111_opy_][bstack11l1l_opy_ (u"࠭ࡩࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪॄ")]
      bstack11lll111l_opy_ = int(bstack11l11111_opy_) + 1
      bstack1ll1l11lll_opy_(bstack11l1l111_opy_, bstack11lll111l_opy_, file_path)
      return bstack11lll111l_opy_
    else:
      bstack1ll1l11lll_opy_(bstack11l1l111_opy_, 1, file_path)
      return 1
  except Exception as e:
    logger.warning(bstack11l111ll1l_opy_.format(str(e)))
    return -1
def bstack111ll1ll1l_opy_(config):
  if not config[bstack11l1l_opy_ (u"ࠧࡶࡵࡨࡶࡓࡧ࡭ࡦࠩॅ")] or not config[bstack11l1l_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡌࡧࡼࠫॆ")]:
    return True
  else:
    return False
def bstack1l1l111111_opy_(config, index=0):
  global bstack1ll1ll111l_opy_
  bstack1l11111l1_opy_ = {}
  caps = bstack1ll111ll11_opy_ + bstack11ll1111l_opy_
  if config.get(bstack11l1l_opy_ (u"ࠩࡷࡹࡷࡨ࡯ࡔࡥࡤࡰࡪ࠭े"), False):
    bstack1l11111l1_opy_[bstack11l1l_opy_ (u"ࠪࡸࡺࡸࡢࡰࡵࡦࡥࡱ࡫ࠧै")] = True
    bstack1l11111l1_opy_[bstack11l1l_opy_ (u"ࠫࡹࡻࡲࡣࡱࡖࡧࡦࡲࡥࡐࡲࡷ࡭ࡴࡴࡳࠨॉ")] = config.get(bstack11l1l_opy_ (u"ࠬࡺࡵࡳࡤࡲࡗࡨࡧ࡬ࡦࡑࡳࡸ࡮ࡵ࡮ࡴࠩॊ"), {})
  if bstack1ll1ll111l_opy_:
    caps += bstack1ll11llll1_opy_
  for key in config:
    if key in caps + [bstack11l1l_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩो")]:
      continue
    bstack1l11111l1_opy_[key] = config[key]
  if bstack11l1l_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪौ") in config:
    for bstack11ll11l1ll_opy_ in config[bstack11l1l_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶ्ࠫ")][index]:
      if bstack11ll11l1ll_opy_ in caps:
        continue
      bstack1l11111l1_opy_[bstack11ll11l1ll_opy_] = config[bstack11l1l_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬॎ")][index][bstack11ll11l1ll_opy_]
  bstack1l11111l1_opy_[bstack11l1l_opy_ (u"ࠪ࡬ࡴࡹࡴࡏࡣࡰࡩࠬॏ")] = socket.gethostname()
  if bstack11l1l_opy_ (u"ࠫࡻ࡫ࡲࡴ࡫ࡲࡲࠬॐ") in bstack1l11111l1_opy_:
    del (bstack1l11111l1_opy_[bstack11l1l_opy_ (u"ࠬࡼࡥࡳࡵ࡬ࡳࡳ࠭॑")])
  return bstack1l11111l1_opy_
def bstack11l11111l_opy_(config):
  global bstack1ll1ll111l_opy_
  bstack1ll1111l1_opy_ = {}
  caps = bstack11ll1111l_opy_
  if bstack1ll1ll111l_opy_:
    caps += bstack1ll11llll1_opy_
  for key in caps:
    if key in config:
      bstack1ll1111l1_opy_[key] = config[key]
  return bstack1ll1111l1_opy_
def bstack11l11111ll_opy_(bstack1l11111l1_opy_, bstack1ll1111l1_opy_):
  bstack1llll1ll_opy_ = {}
  for key in bstack1l11111l1_opy_.keys():
    if key in bstack1l1lll1ll_opy_:
      bstack1llll1ll_opy_[bstack1l1lll1ll_opy_[key]] = bstack1l11111l1_opy_[key]
    else:
      bstack1llll1ll_opy_[key] = bstack1l11111l1_opy_[key]
  for key in bstack1ll1111l1_opy_:
    if key in bstack1l1lll1ll_opy_:
      bstack1llll1ll_opy_[bstack1l1lll1ll_opy_[key]] = bstack1ll1111l1_opy_[key]
    else:
      bstack1llll1ll_opy_[key] = bstack1ll1111l1_opy_[key]
  return bstack1llll1ll_opy_
def bstack111lll11l1_opy_(config, index=0):
  global bstack1ll1ll111l_opy_
  caps = {}
  config = copy.deepcopy(config)
  bstack111111ll1_opy_ = bstack1ll1l1ll1_opy_(bstack11ll1111l1_opy_, config, logger)
  bstack1ll1111l1_opy_ = bstack11l11111l_opy_(config)
  bstack111llll1_opy_ = bstack11ll1111l_opy_
  bstack111llll1_opy_ += bstack1l11llll1l_opy_
  bstack1ll1111l1_opy_ = update(bstack1ll1111l1_opy_, bstack111111ll1_opy_)
  if bstack1ll1ll111l_opy_:
    bstack111llll1_opy_ += bstack1ll11llll1_opy_
  if bstack11l1l_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴ॒ࠩ") in config:
    if bstack11l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡏࡣࡰࡩࠬ॓") in config[bstack11l1l_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫ॔")][index]:
      caps[bstack11l1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡑࡥࡲ࡫ࠧॕ")] = config[bstack11l1l_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ॖ")][index][bstack11l1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡓࡧ࡭ࡦࠩॗ")]
    if bstack11l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡜ࡥࡳࡵ࡬ࡳࡳ࠭क़") in config[bstack11l1l_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩख़")][index]:
      caps[bstack11l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡗࡧࡵࡷ࡮ࡵ࡮ࠨग़")] = str(config[bstack11l1l_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫज़")][index][bstack11l1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴ࡙ࡩࡷࡹࡩࡰࡰࠪड़")])
    bstack1ll1lllll1_opy_ = bstack1ll1l1ll1_opy_(bstack11ll1111l1_opy_, config[bstack11l1l_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ढ़")][index], logger)
    bstack111llll1_opy_ += list(bstack1ll1lllll1_opy_.keys())
    for bstack1l1111lll_opy_ in bstack111llll1_opy_:
      if bstack1l1111lll_opy_ in config[bstack11l1l_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧफ़")][index]:
        if bstack1l1111lll_opy_ == bstack11l1l_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡖࡦࡴࡶ࡭ࡴࡴࠧय़"):
          try:
            bstack1ll1lllll1_opy_[bstack1l1111lll_opy_] = str(config[bstack11l1l_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩॠ")][index][bstack1l1111lll_opy_] * 1.0)
          except:
            bstack1ll1lllll1_opy_[bstack1l1111lll_opy_] = str(config[bstack11l1l_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪॡ")][index][bstack1l1111lll_opy_])
        else:
          bstack1ll1lllll1_opy_[bstack1l1111lll_opy_] = config[bstack11l1l_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫॢ")][index][bstack1l1111lll_opy_]
        del (config[bstack11l1l_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬॣ")][index][bstack1l1111lll_opy_])
    bstack1ll1111l1_opy_ = update(bstack1ll1111l1_opy_, bstack1ll1lllll1_opy_)
  bstack1l11111l1_opy_ = bstack1l1l111111_opy_(config, index)
  for bstack1lll1ll1l_opy_ in bstack11ll1111l_opy_ + list(bstack111111ll1_opy_.keys()):
    if bstack1lll1ll1l_opy_ in bstack1l11111l1_opy_:
      bstack1ll1111l1_opy_[bstack1lll1ll1l_opy_] = bstack1l11111l1_opy_[bstack1lll1ll1l_opy_]
      del (bstack1l11111l1_opy_[bstack1lll1ll1l_opy_])
  if bstack1l11llll_opy_(config):
    bstack1l11111l1_opy_[bstack11l1l_opy_ (u"ࠪࡹࡸ࡫ࡗ࠴ࡅࠪ।")] = True
    caps.update(bstack1ll1111l1_opy_)
    caps[bstack11l1l_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮࠾ࡴࡶࡴࡪࡱࡱࡷࠬ॥")] = bstack1l11111l1_opy_
  else:
    bstack1l11111l1_opy_[bstack11l1l_opy_ (u"ࠬࡻࡳࡦ࡙࠶ࡇࠬ०")] = False
    caps.update(bstack11l11111ll_opy_(bstack1l11111l1_opy_, bstack1ll1111l1_opy_))
    if bstack11l1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡎࡢ࡯ࡨࠫ१") in caps:
      caps[bstack11l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࠨ२")] = caps[bstack11l1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡐࡤࡱࡪ࠭३")]
      del (caps[bstack11l1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡑࡥࡲ࡫ࠧ४")])
    if bstack11l1l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵ࡚ࡪࡸࡳࡪࡱࡱࠫ५") in caps:
      caps[bstack11l1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡤࡼࡥࡳࡵ࡬ࡳࡳ࠭६")] = caps[bstack11l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡜ࡥࡳࡵ࡬ࡳࡳ࠭७")]
      del (caps[bstack11l1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡖࡦࡴࡶ࡭ࡴࡴࠧ८")])
  return caps
def bstack11l111l11_opy_():
  global bstack1l1l1ll1_opy_
  global CONFIG
  if bstack1l1l1l1ll1_opy_() <= version.parse(bstack11l1l_opy_ (u"ࠧ࠴࠰࠴࠷࠳࠶ࠧ९")):
    if bstack1l1l1ll1_opy_ != bstack11l1l_opy_ (u"ࠨࠩ॰"):
      return bstack11l1l_opy_ (u"ࠤ࡫ࡸࡹࡶ࠺࠰࠱ࠥॱ") + bstack1l1l1ll1_opy_ + bstack11l1l_opy_ (u"ࠥ࠾࠽࠶࠯ࡸࡦ࠲࡬ࡺࡨࠢॲ")
    return bstack1lll11lll_opy_
  if bstack1l1l1ll1_opy_ != bstack11l1l_opy_ (u"ࠫࠬॳ"):
    return bstack11l1l_opy_ (u"ࠧ࡮ࡴࡵࡲࡶ࠾࠴࠵ࠢॴ") + bstack1l1l1ll1_opy_ + bstack11l1l_opy_ (u"ࠨ࠯ࡸࡦ࠲࡬ࡺࡨࠢॵ")
  return bstack1ll111ll1l_opy_
def bstack11l111l11l_opy_(options):
  return hasattr(options, bstack11l1l_opy_ (u"ࠧࡴࡧࡷࡣࡨࡧࡰࡢࡤ࡬ࡰ࡮ࡺࡹࠨॶ"))
def update(d, u):
  for k, v in u.items():
    if isinstance(v, collections.abc.Mapping):
      d[k] = update(d.get(k, {}), v)
    else:
      if isinstance(v, list):
        d[k] = d.get(k, []) + v
      else:
        d[k] = v
  return d
def bstack1l1l1l111l_opy_(options, bstack1ll111l1l1_opy_):
  for bstack1l1lll11l_opy_ in bstack1ll111l1l1_opy_:
    if bstack1l1lll11l_opy_ in [bstack11l1l_opy_ (u"ࠨࡣࡵ࡫ࡸ࠭ॷ"), bstack11l1l_opy_ (u"ࠩࡨࡼࡹ࡫࡮ࡴ࡫ࡲࡲࡸ࠭ॸ")]:
      continue
    if bstack1l1lll11l_opy_ in options._experimental_options:
      options._experimental_options[bstack1l1lll11l_opy_] = update(options._experimental_options[bstack1l1lll11l_opy_],
                                                         bstack1ll111l1l1_opy_[bstack1l1lll11l_opy_])
    else:
      options.add_experimental_option(bstack1l1lll11l_opy_, bstack1ll111l1l1_opy_[bstack1l1lll11l_opy_])
  if bstack11l1l_opy_ (u"ࠪࡥࡷ࡭ࡳࠨॹ") in bstack1ll111l1l1_opy_:
    for arg in bstack1ll111l1l1_opy_[bstack11l1l_opy_ (u"ࠫࡦࡸࡧࡴࠩॺ")]:
      options.add_argument(arg)
    del (bstack1ll111l1l1_opy_[bstack11l1l_opy_ (u"ࠬࡧࡲࡨࡵࠪॻ")])
  if bstack11l1l_opy_ (u"࠭ࡥࡹࡶࡨࡲࡸ࡯࡯࡯ࡵࠪॼ") in bstack1ll111l1l1_opy_:
    for ext in bstack1ll111l1l1_opy_[bstack11l1l_opy_ (u"ࠧࡦࡺࡷࡩࡳࡹࡩࡰࡰࡶࠫॽ")]:
      try:
        options.add_extension(ext)
      except OSError:
        options.add_encoded_extension(ext)
    del (bstack1ll111l1l1_opy_[bstack11l1l_opy_ (u"ࠨࡧࡻࡸࡪࡴࡳࡪࡱࡱࡷࠬॾ")])
def bstack11ll1ll11_opy_(options, bstack1llll11lll_opy_):
  if bstack11l1l_opy_ (u"ࠩࡳࡶࡪ࡬ࡳࠨॿ") in bstack1llll11lll_opy_:
    for bstack1l1lll1l1_opy_ in bstack1llll11lll_opy_[bstack11l1l_opy_ (u"ࠪࡴࡷ࡫ࡦࡴࠩঀ")]:
      if bstack1l1lll1l1_opy_ in options._preferences:
        options._preferences[bstack1l1lll1l1_opy_] = update(options._preferences[bstack1l1lll1l1_opy_], bstack1llll11lll_opy_[bstack11l1l_opy_ (u"ࠫࡵࡸࡥࡧࡵࠪঁ")][bstack1l1lll1l1_opy_])
      else:
        options.set_preference(bstack1l1lll1l1_opy_, bstack1llll11lll_opy_[bstack11l1l_opy_ (u"ࠬࡶࡲࡦࡨࡶࠫং")][bstack1l1lll1l1_opy_])
  if bstack11l1l_opy_ (u"࠭ࡡࡳࡩࡶࠫঃ") in bstack1llll11lll_opy_:
    for arg in bstack1llll11lll_opy_[bstack11l1l_opy_ (u"ࠧࡢࡴࡪࡷࠬ঄")]:
      options.add_argument(arg)
def bstack11lll11ll_opy_(options, bstack1l1ll111l1_opy_):
  if bstack11l1l_opy_ (u"ࠨࡹࡨࡦࡻ࡯ࡥࡸࠩঅ") in bstack1l1ll111l1_opy_:
    options.use_webview(bool(bstack1l1ll111l1_opy_[bstack11l1l_opy_ (u"ࠩࡺࡩࡧࡼࡩࡦࡹࠪআ")]))
  bstack1l1l1l111l_opy_(options, bstack1l1ll111l1_opy_)
def bstack1ll1ll11_opy_(options, bstack11l11ll111_opy_):
  for bstack11ll1l11l_opy_ in bstack11l11ll111_opy_:
    if bstack11ll1l11l_opy_ in [bstack11l1l_opy_ (u"ࠪࡸࡪࡩࡨ࡯ࡱ࡯ࡳ࡬ࡿࡐࡳࡧࡹ࡭ࡪࡽࠧই"), bstack11l1l_opy_ (u"ࠫࡦࡸࡧࡴࠩঈ")]:
      continue
    options.set_capability(bstack11ll1l11l_opy_, bstack11l11ll111_opy_[bstack11ll1l11l_opy_])
  if bstack11l1l_opy_ (u"ࠬࡧࡲࡨࡵࠪউ") in bstack11l11ll111_opy_:
    for arg in bstack11l11ll111_opy_[bstack11l1l_opy_ (u"࠭ࡡࡳࡩࡶࠫঊ")]:
      options.add_argument(arg)
  if bstack11l1l_opy_ (u"ࠧࡵࡧࡦ࡬ࡳࡵ࡬ࡰࡩࡼࡔࡷ࡫ࡶࡪࡧࡺࠫঋ") in bstack11l11ll111_opy_:
    options.bstack1111llll1_opy_(bool(bstack11l11ll111_opy_[bstack11l1l_opy_ (u"ࠨࡶࡨࡧ࡭ࡴ࡯࡭ࡱࡪࡽࡕࡸࡥࡷ࡫ࡨࡻࠬঌ")]))
def bstack1l1l1l1111_opy_(options, bstack1l11l1l1_opy_):
  for bstack1l1l11llll_opy_ in bstack1l11l1l1_opy_:
    if bstack1l1l11llll_opy_ in [bstack11l1l_opy_ (u"ࠩࡤࡨࡩ࡯ࡴࡪࡱࡱࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭঍"), bstack11l1l_opy_ (u"ࠪࡥࡷ࡭ࡳࠨ঎")]:
      continue
    options._options[bstack1l1l11llll_opy_] = bstack1l11l1l1_opy_[bstack1l1l11llll_opy_]
  if bstack11l1l_opy_ (u"ࠫࡦࡪࡤࡪࡶ࡬ࡳࡳࡧ࡬ࡐࡲࡷ࡭ࡴࡴࡳࠨএ") in bstack1l11l1l1_opy_:
    for bstack11l1lllll_opy_ in bstack1l11l1l1_opy_[bstack11l1l_opy_ (u"ࠬࡧࡤࡥ࡫ࡷ࡭ࡴࡴࡡ࡭ࡑࡳࡸ࡮ࡵ࡮ࡴࠩঐ")]:
      options.bstack1ll1l1ll1l_opy_(
        bstack11l1lllll_opy_, bstack1l11l1l1_opy_[bstack11l1l_opy_ (u"࠭ࡡࡥࡦ࡬ࡸ࡮ࡵ࡮ࡢ࡮ࡒࡴࡹ࡯࡯࡯ࡵࠪ঑")][bstack11l1lllll_opy_])
  if bstack11l1l_opy_ (u"ࠧࡢࡴࡪࡷࠬ঒") in bstack1l11l1l1_opy_:
    for arg in bstack1l11l1l1_opy_[bstack11l1l_opy_ (u"ࠨࡣࡵ࡫ࡸ࠭ও")]:
      options.add_argument(arg)
def bstack11lllllll1_opy_(options, caps):
  if not hasattr(options, bstack11l1l_opy_ (u"ࠩࡎࡉ࡞࠭ঔ")):
    return
  if options.KEY == bstack11l1l_opy_ (u"ࠪ࡫ࡴࡵࡧ࠻ࡥ࡫ࡶࡴࡳࡥࡐࡲࡷ࡭ࡴࡴࡳࠨক"):
    options = bstack11llll11l1_opy_.bstack11ll11ll_opy_(bstack11llll1111_opy_=options, config=CONFIG)
  if options.KEY == bstack11l1l_opy_ (u"ࠫ࡬ࡵ࡯ࡨ࠼ࡦ࡬ࡷࡵ࡭ࡦࡑࡳࡸ࡮ࡵ࡮ࡴࠩখ") and options.KEY in caps:
    bstack1l1l1l111l_opy_(options, caps[bstack11l1l_opy_ (u"ࠬ࡭࡯ࡰࡩ࠽ࡧ࡭ࡸ࡯࡮ࡧࡒࡴࡹ࡯࡯࡯ࡵࠪগ")])
  elif options.KEY == bstack11l1l_opy_ (u"࠭࡭ࡰࡼ࠽ࡪ࡮ࡸࡥࡧࡱࡻࡓࡵࡺࡩࡰࡰࡶࠫঘ") and options.KEY in caps:
    bstack11ll1ll11_opy_(options, caps[bstack11l1l_opy_ (u"ࠧ࡮ࡱࡽ࠾࡫࡯ࡲࡦࡨࡲࡼࡔࡶࡴࡪࡱࡱࡷࠬঙ")])
  elif options.KEY == bstack11l1l_opy_ (u"ࠨࡵࡤࡪࡦࡸࡩ࠯ࡱࡳࡸ࡮ࡵ࡮ࡴࠩচ") and options.KEY in caps:
    bstack1ll1ll11_opy_(options, caps[bstack11l1l_opy_ (u"ࠩࡶࡥ࡫ࡧࡲࡪ࠰ࡲࡴࡹ࡯࡯࡯ࡵࠪছ")])
  elif options.KEY == bstack11l1l_opy_ (u"ࠪࡱࡸࡀࡥࡥࡩࡨࡓࡵࡺࡩࡰࡰࡶࠫজ") and options.KEY in caps:
    bstack11lll11ll_opy_(options, caps[bstack11l1l_opy_ (u"ࠫࡲࡹ࠺ࡦࡦࡪࡩࡔࡶࡴࡪࡱࡱࡷࠬঝ")])
  elif options.KEY == bstack11l1l_opy_ (u"ࠬࡹࡥ࠻࡫ࡨࡓࡵࡺࡩࡰࡰࡶࠫঞ") and options.KEY in caps:
    bstack1l1l1l1111_opy_(options, caps[bstack11l1l_opy_ (u"࠭ࡳࡦ࠼࡬ࡩࡔࡶࡴࡪࡱࡱࡷࠬট")])
def bstack1ll1l11111_opy_(caps):
  global bstack1ll1ll111l_opy_
  if isinstance(os.environ.get(bstack11l1l_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡉࡔࡡࡄࡔࡕࡥࡁࡖࡖࡒࡑࡆ࡚ࡅࠨঠ")), str):
    bstack1ll1ll111l_opy_ = eval(os.getenv(bstack11l1l_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡊࡕࡢࡅࡕࡖ࡟ࡂࡗࡗࡓࡒࡇࡔࡆࠩড")))
  if bstack1ll1ll111l_opy_:
    if bstack11l11l1lll_opy_() < version.parse(bstack11l1l_opy_ (u"ࠩ࠵࠲࠸࠴࠰ࠨঢ")):
      return None
    else:
      from appium.options.common.base import AppiumOptions
      options = AppiumOptions().load_capabilities(caps)
      return options
  else:
    browser = bstack11l1l_opy_ (u"ࠪࡧ࡭ࡸ࡯࡮ࡧࠪণ")
    if bstack11l1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡓࡧ࡭ࡦࠩত") in caps:
      browser = caps[bstack11l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡔࡡ࡮ࡧࠪথ")]
    elif bstack11l1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࠧদ") in caps:
      browser = caps[bstack11l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࠨধ")]
    browser = str(browser).lower()
    if browser == bstack11l1l_opy_ (u"ࠨ࡫ࡳ࡬ࡴࡴࡥࠨন") or browser == bstack11l1l_opy_ (u"ࠩ࡬ࡴࡦࡪࠧ঩"):
      browser = bstack11l1l_opy_ (u"ࠪࡷࡦ࡬ࡡࡳ࡫ࠪপ")
    if browser == bstack11l1l_opy_ (u"ࠫࡸࡧ࡭ࡴࡷࡱ࡫ࠬফ"):
      browser = bstack11l1l_opy_ (u"ࠬࡩࡨࡳࡱࡰࡩࠬব")
    if browser not in [bstack11l1l_opy_ (u"࠭ࡣࡩࡴࡲࡱࡪ࠭ভ"), bstack11l1l_opy_ (u"ࠧࡦࡦࡪࡩࠬম"), bstack11l1l_opy_ (u"ࠨ࡫ࡨࠫয"), bstack11l1l_opy_ (u"ࠩࡶࡥ࡫ࡧࡲࡪࠩর"), bstack11l1l_opy_ (u"ࠪࡪ࡮ࡸࡥࡧࡱࡻࠫ঱")]:
      return None
    try:
      package = bstack11l1l_opy_ (u"ࠫࡸ࡫࡬ࡦࡰ࡬ࡹࡲ࠴ࡷࡦࡤࡧࡶ࡮ࡼࡥࡳ࠰ࡾࢁ࠳ࡵࡰࡵ࡫ࡲࡲࡸ࠭ল").format(browser)
      name = bstack11l1l_opy_ (u"ࠬࡕࡰࡵ࡫ࡲࡲࡸ࠭঳")
      browser_options = getattr(__import__(package, fromlist=[name]), name)
      options = browser_options()
      if not bstack11l111l11l_opy_(options):
        return None
      for bstack1lll1ll1l_opy_ in caps.keys():
        options.set_capability(bstack1lll1ll1l_opy_, caps[bstack1lll1ll1l_opy_])
      bstack11lllllll1_opy_(options, caps)
      return options
    except Exception as e:
      logger.debug(str(e))
      return None
def bstack1111l1l1l_opy_(options, bstack1l1l11l1l_opy_):
  if not bstack11l111l11l_opy_(options):
    return
  for bstack1lll1ll1l_opy_ in bstack1l1l11l1l_opy_.keys():
    if bstack1lll1ll1l_opy_ in bstack1l11llll1l_opy_:
      continue
    if bstack1lll1ll1l_opy_ in options._caps and type(options._caps[bstack1lll1ll1l_opy_]) in [dict, list]:
      options._caps[bstack1lll1ll1l_opy_] = update(options._caps[bstack1lll1ll1l_opy_], bstack1l1l11l1l_opy_[bstack1lll1ll1l_opy_])
    else:
      options.set_capability(bstack1lll1ll1l_opy_, bstack1l1l11l1l_opy_[bstack1lll1ll1l_opy_])
  bstack11lllllll1_opy_(options, bstack1l1l11l1l_opy_)
  if bstack11l1l_opy_ (u"࠭࡭ࡰࡼ࠽ࡨࡪࡨࡵࡨࡩࡨࡶࡆࡪࡤࡳࡧࡶࡷࠬ঴") in options._caps:
    if options._caps[bstack11l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡏࡣࡰࡩࠬ঵")] and options._caps[bstack11l1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡐࡤࡱࡪ࠭শ")].lower() != bstack11l1l_opy_ (u"ࠩࡩ࡭ࡷ࡫ࡦࡰࡺࠪষ"):
      del options._caps[bstack11l1l_opy_ (u"ࠪࡱࡴࢀ࠺ࡥࡧࡥࡹ࡬࡭ࡥࡳࡃࡧࡨࡷ࡫ࡳࡴࠩস")]
def bstack11lll1l1l_opy_(proxy_config):
  if bstack11l1l_opy_ (u"ࠫ࡭ࡺࡴࡱࡵࡓࡶࡴࡾࡹࠨহ") in proxy_config:
    proxy_config[bstack11l1l_opy_ (u"ࠬࡹࡳ࡭ࡒࡵࡳࡽࡿࠧ঺")] = proxy_config[bstack11l1l_opy_ (u"࠭ࡨࡵࡶࡳࡷࡕࡸ࡯ࡹࡻࠪ঻")]
    del (proxy_config[bstack11l1l_opy_ (u"ࠧࡩࡶࡷࡴࡸࡖࡲࡰࡺࡼ়ࠫ")])
  if bstack11l1l_opy_ (u"ࠨࡲࡵࡳࡽࡿࡔࡺࡲࡨࠫঽ") in proxy_config and proxy_config[bstack11l1l_opy_ (u"ࠩࡳࡶࡴࡾࡹࡕࡻࡳࡩࠬা")].lower() != bstack11l1l_opy_ (u"ࠪࡨ࡮ࡸࡥࡤࡶࠪি"):
    proxy_config[bstack11l1l_opy_ (u"ࠫࡵࡸ࡯ࡹࡻࡗࡽࡵ࡫ࠧী")] = bstack11l1l_opy_ (u"ࠬࡳࡡ࡯ࡷࡤࡰࠬু")
  if bstack11l1l_opy_ (u"࠭ࡰࡳࡱࡻࡽࡆࡻࡴࡰࡥࡲࡲ࡫࡯ࡧࡖࡴ࡯ࠫূ") in proxy_config:
    proxy_config[bstack11l1l_opy_ (u"ࠧࡱࡴࡲࡼࡾ࡚ࡹࡱࡧࠪৃ")] = bstack11l1l_opy_ (u"ࠨࡲࡤࡧࠬৄ")
  return proxy_config
def bstack1l111l1ll_opy_(config, proxy):
  from selenium.webdriver.common.proxy import Proxy
  if not bstack11l1l_opy_ (u"ࠩࡳࡶࡴࡾࡹࠨ৅") in config:
    return proxy
  config[bstack11l1l_opy_ (u"ࠪࡴࡷࡵࡸࡺࠩ৆")] = bstack11lll1l1l_opy_(config[bstack11l1l_opy_ (u"ࠫࡵࡸ࡯ࡹࡻࠪে")])
  if proxy == None:
    proxy = Proxy(config[bstack11l1l_opy_ (u"ࠬࡶࡲࡰࡺࡼࠫৈ")])
  return proxy
def bstack1l1l111l1l_opy_(self):
  global CONFIG
  global bstack1ll1l11l_opy_
  try:
    proxy = bstack1l1ll1l1ll_opy_(CONFIG)
    if proxy:
      if proxy.endswith(bstack11l1l_opy_ (u"࠭࠮ࡱࡣࡦࠫ৉")):
        proxies = bstack11l1l1l111_opy_(proxy, bstack11l111l11_opy_())
        if len(proxies) > 0:
          protocol, bstack1l11ll1ll_opy_ = proxies.popitem()
          if bstack11l1l_opy_ (u"ࠢ࠻࠱࠲ࠦ৊") in bstack1l11ll1ll_opy_:
            return bstack1l11ll1ll_opy_
          else:
            return bstack11l1l_opy_ (u"ࠣࡪࡷࡸࡵࡀ࠯࠰ࠤো") + bstack1l11ll1ll_opy_
      else:
        return proxy
  except Exception as e:
    logger.error(bstack11l1l_opy_ (u"ࠤࡈࡶࡷࡵࡲࠡ࡫ࡱࠤࡸ࡫ࡴࡵ࡫ࡱ࡫ࠥࡶࡲࡰࡺࡼࠤࡺࡸ࡬ࠡ࠼ࠣࡿࢂࠨৌ").format(str(e)))
  return bstack1ll1l11l_opy_(self)
def bstack1llll11ll_opy_():
  global CONFIG
  return bstack11ll11ll1_opy_(CONFIG) and bstack1l11ll11l_opy_() and bstack1l1l1l1ll1_opy_() >= version.parse(bstack11l1ll111_opy_)
def bstack1ll11111_opy_():
  global CONFIG
  return (bstack11l1l_opy_ (u"ࠪ࡬ࡹࡺࡰࡑࡴࡲࡼࡾ্࠭") in CONFIG or bstack11l1l_opy_ (u"ࠫ࡭ࡺࡴࡱࡵࡓࡶࡴࡾࡹࠨৎ") in CONFIG) and bstack1l11ll111_opy_()
def bstack1l11l111ll_opy_(config):
  bstack1l1ll11ll1_opy_ = {}
  if bstack11l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࡑࡳࡸ࡮ࡵ࡮ࡴࠩ৏") in config:
    bstack1l1ll11ll1_opy_ = config[bstack11l1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࡒࡴࡹ࡯࡯࡯ࡵࠪ৐")]
  if bstack11l1l_opy_ (u"ࠧ࡭ࡱࡦࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭৑") in config:
    bstack1l1ll11ll1_opy_ = config[bstack11l1l_opy_ (u"ࠨ࡮ࡲࡧࡦࡲࡏࡱࡶ࡬ࡳࡳࡹࠧ৒")]
  proxy = bstack1l1ll1l1ll_opy_(config)
  if proxy:
    if proxy.endswith(bstack11l1l_opy_ (u"ࠩ࠱ࡴࡦࡩࠧ৓")) and os.path.isfile(proxy):
      bstack1l1ll11ll1_opy_[bstack11l1l_opy_ (u"ࠪ࠱ࡵࡧࡣ࠮ࡨ࡬ࡰࡪ࠭৔")] = proxy
    else:
      parsed_url = None
      if proxy.endswith(bstack11l1l_opy_ (u"ࠫ࠳ࡶࡡࡤࠩ৕")):
        proxies = bstack1lllll111l_opy_(config, bstack11l111l11_opy_())
        if len(proxies) > 0:
          protocol, bstack1l11ll1ll_opy_ = proxies.popitem()
          if bstack11l1l_opy_ (u"ࠧࡀ࠯࠰ࠤ৖") in bstack1l11ll1ll_opy_:
            parsed_url = urlparse(bstack1l11ll1ll_opy_)
          else:
            parsed_url = urlparse(protocol + bstack11l1l_opy_ (u"ࠨ࠺࠰࠱ࠥৗ") + bstack1l11ll1ll_opy_)
      else:
        parsed_url = urlparse(proxy)
      if parsed_url and parsed_url.hostname: bstack1l1ll11ll1_opy_[bstack11l1l_opy_ (u"ࠧࡱࡴࡲࡼࡾࡎ࡯ࡴࡶࠪ৘")] = str(parsed_url.hostname)
      if parsed_url and parsed_url.port: bstack1l1ll11ll1_opy_[bstack11l1l_opy_ (u"ࠨࡲࡵࡳࡽࡿࡐࡰࡴࡷࠫ৙")] = str(parsed_url.port)
      if parsed_url and parsed_url.username: bstack1l1ll11ll1_opy_[bstack11l1l_opy_ (u"ࠩࡳࡶࡴࡾࡹࡖࡵࡨࡶࠬ৚")] = str(parsed_url.username)
      if parsed_url and parsed_url.password: bstack1l1ll11ll1_opy_[bstack11l1l_opy_ (u"ࠪࡴࡷࡵࡸࡺࡒࡤࡷࡸ࠭৛")] = str(parsed_url.password)
  return bstack1l1ll11ll1_opy_
def bstack1l1ll1ll11_opy_(config):
  if bstack11l1l_opy_ (u"ࠫࡹ࡫ࡳࡵࡅࡲࡲࡹ࡫ࡸࡵࡑࡳࡸ࡮ࡵ࡮ࡴࠩড়") in config:
    return config[bstack11l1l_opy_ (u"ࠬࡺࡥࡴࡶࡆࡳࡳࡺࡥࡹࡶࡒࡴࡹ࡯࡯࡯ࡵࠪঢ়")]
  return {}
def bstack1ll1l11l1l_opy_(caps):
  global bstack11l11l1ll1_opy_
  if bstack11l1l_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡀ࡯ࡱࡶ࡬ࡳࡳࡹࠧ৞") in caps:
    caps[bstack11l1l_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱ࠺ࡰࡲࡷ࡭ࡴࡴࡳࠨয়")][bstack11l1l_opy_ (u"ࠨ࡮ࡲࡧࡦࡲࠧৠ")] = True
    if bstack11l11l1ll1_opy_:
      caps[bstack11l1l_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬࠼ࡲࡴࡹ࡯࡯࡯ࡵࠪৡ")][bstack11l1l_opy_ (u"ࠪࡰࡴࡩࡡ࡭ࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬৢ")] = bstack11l11l1ll1_opy_
  else:
    caps[bstack11l1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡰࡴࡩࡡ࡭ࠩৣ")] = True
    if bstack11l11l1ll1_opy_:
      caps[bstack11l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡱࡵࡣࡢ࡮ࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭৤")] = bstack11l11l1ll1_opy_
@measure(event_name=EVENTS.bstack111ll1111_opy_, stage=STAGE.bstack1lll1l11l_opy_, bstack1l1l1llll_opy_=bstack11l1ll1l_opy_)
def bstack11ll1l1l1_opy_():
  global CONFIG
  if not bstack11lll11ll1_opy_(CONFIG) or cli.is_enabled(CONFIG):
    return
  if bstack11l1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࠪ৥") in CONFIG and bstack1llll1ll1_opy_(CONFIG[bstack11l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࠫ০")]):
    if (
      bstack11l1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡕࡷࡥࡨࡱࡌࡰࡥࡤࡰࡔࡶࡴࡪࡱࡱࡷࠬ১") in CONFIG
      and bstack1llll1ll1_opy_(CONFIG[bstack11l1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࡍࡱࡦࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭২")].get(bstack11l1l_opy_ (u"ࠪࡷࡰ࡯ࡰࡃ࡫ࡱࡥࡷࡿࡉ࡯࡫ࡷ࡭ࡦࡲࡩࡴࡣࡷ࡭ࡴࡴࠧ৩")))
    ):
      logger.debug(bstack11l1l_opy_ (u"ࠦࡑࡵࡣࡢ࡮ࠣࡦ࡮ࡴࡡࡳࡻࠣࡲࡴࡺࠠࡴࡶࡤࡶࡹ࡫ࡤࠡࡣࡶࠤࡸࡱࡩࡱࡄ࡬ࡲࡦࡸࡹࡊࡰ࡬ࡸ࡮ࡧ࡬ࡪࡵࡤࡸ࡮ࡵ࡮ࠡ࡫ࡶࠤࡪࡴࡡࡣ࡮ࡨࡨࠧ৪"))
      return
    bstack1l1ll11ll1_opy_ = bstack1l11l111ll_opy_(CONFIG)
    bstack11ll1ll1l_opy_(CONFIG[bstack11l1l_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷࡐ࡫ࡹࠨ৫")], bstack1l1ll11ll1_opy_)
def bstack11ll1ll1l_opy_(key, bstack1l1ll11ll1_opy_):
  global bstack111l1l1l1_opy_
  logger.info(bstack1l11l11lll_opy_)
  try:
    bstack111l1l1l1_opy_ = Local()
    bstack111l1l1ll_opy_ = {bstack11l1l_opy_ (u"࠭࡫ࡦࡻࠪ৬"): key}
    bstack111l1l1ll_opy_.update(bstack1l1ll11ll1_opy_)
    logger.debug(bstack1lll1l1l11_opy_.format(str(bstack111l1l1ll_opy_)).replace(key, bstack11l1l_opy_ (u"ࠧ࡜ࡔࡈࡈࡆࡉࡔࡆࡆࡠࠫ৭")))
    bstack111l1l1l1_opy_.start(**bstack111l1l1ll_opy_)
    if bstack111l1l1l1_opy_.isRunning():
      logger.info(bstack1ll11111ll_opy_)
  except Exception as e:
    bstack1ll11l111l_opy_(bstack1llll1l1l1_opy_.format(str(e)))
def bstack11l111l1ll_opy_():
  global bstack111l1l1l1_opy_
  if bstack111l1l1l1_opy_.isRunning():
    logger.info(bstack1ll1ll1ll_opy_)
    bstack111l1l1l1_opy_.stop()
  bstack111l1l1l1_opy_ = None
def bstack11l11ll1l1_opy_(bstack1lll1ll1_opy_=[]):
  global CONFIG
  bstack111l1l111_opy_ = []
  bstack1l11l1ll1l_opy_ = [bstack11l1l_opy_ (u"ࠨࡱࡶࠫ৮"), bstack11l1l_opy_ (u"ࠩࡲࡷ࡛࡫ࡲࡴ࡫ࡲࡲࠬ৯"), bstack11l1l_opy_ (u"ࠪࡨࡪࡼࡩࡤࡧࡑࡥࡲ࡫ࠧৰ"), bstack11l1l_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲ࡜ࡥࡳࡵ࡬ࡳࡳ࠭ৱ"), bstack11l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡔࡡ࡮ࡧࠪ৲"), bstack11l1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡖࡦࡴࡶ࡭ࡴࡴࠧ৳")]
  try:
    for err in bstack1lll1ll1_opy_:
      bstack1llll11l_opy_ = {}
      for k in bstack1l11l1ll1l_opy_:
        val = CONFIG[bstack11l1l_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪ৴")][int(err[bstack11l1l_opy_ (u"ࠨ࡫ࡱࡨࡪࡾࠧ৵")])].get(k)
        if val:
          bstack1llll11l_opy_[k] = val
      if(err[bstack11l1l_opy_ (u"ࠩࡨࡶࡷࡵࡲࠨ৶")] != bstack11l1l_opy_ (u"ࠪࠫ৷")):
        bstack1llll11l_opy_[bstack11l1l_opy_ (u"ࠫࡹ࡫ࡳࡵࡵࠪ৸")] = {
          err[bstack11l1l_opy_ (u"ࠬࡴࡡ࡮ࡧࠪ৹")]: err[bstack11l1l_opy_ (u"࠭ࡥࡳࡴࡲࡶࠬ৺")]
        }
        bstack111l1l111_opy_.append(bstack1llll11l_opy_)
  except Exception as e:
    logger.debug(bstack11l1l_opy_ (u"ࠧࡆࡴࡵࡳࡷࠦࡩ࡯ࠢࡩࡳࡷࡳࡡࡵࡶ࡬ࡲ࡬ࠦࡤࡢࡶࡤࠤ࡫ࡵࡲࠡࡧࡹࡩࡳࡺ࠺ࠡࠩ৻") + str(e))
  finally:
    return bstack111l1l111_opy_
def bstack11l1ll1l11_opy_(file_name):
  bstack11ll111lll_opy_ = []
  try:
    bstack1l11lll1ll_opy_ = os.path.join(tempfile.gettempdir(), file_name)
    if os.path.exists(bstack1l11lll1ll_opy_):
      with open(bstack1l11lll1ll_opy_) as f:
        bstack1lll11l1_opy_ = json.load(f)
        bstack11ll111lll_opy_ = bstack1lll11l1_opy_
      os.remove(bstack1l11lll1ll_opy_)
    return bstack11ll111lll_opy_
  except Exception as e:
    logger.debug(bstack11l1l_opy_ (u"ࠨࡇࡵࡶࡴࡸࠠࡪࡰࠣࡪ࡮ࡴࡤࡪࡰࡪࠤࡪࡸࡲࡰࡴࠣࡰ࡮ࡹࡴ࠻ࠢࠪৼ") + str(e))
    return bstack11ll111lll_opy_
def bstack1l1lll111_opy_():
  try:
      from bstack_utils.constants import bstack11ll1l111_opy_, EVENTS
      from bstack_utils.helper import bstack1l111l111l_opy_, get_host_info, bstack1l1ll11111_opy_
      from datetime import datetime
      from filelock import FileLock
      bstack1l1l1l11l_opy_ = os.path.join(os.getcwd(), bstack11l1l_opy_ (u"ࠩ࡯ࡳ࡬࠭৽"), bstack11l1l_opy_ (u"ࠪ࡯ࡪࡿ࠭࡮ࡧࡷࡶ࡮ࡩࡳ࠯࡬ࡶࡳࡳ࠭৾"))
      lock = FileLock(bstack1l1l1l11l_opy_+bstack11l1l_opy_ (u"ࠦ࠳ࡲ࡯ࡤ࡭ࠥ৿"))
      def bstack1ll1l1111l_opy_():
          try:
              with lock:
                  with open(bstack1l1l1l11l_opy_, bstack11l1l_opy_ (u"ࠧࡸࠢ਀"), encoding=bstack11l1l_opy_ (u"ࠨࡵࡵࡨ࠰࠼ࠧਁ")) as file:
                      data = json.load(file)
                      config = {
                          bstack11l1l_opy_ (u"ࠢࡩࡧࡤࡨࡪࡸࡳࠣਂ"): {
                              bstack11l1l_opy_ (u"ࠣࡅࡲࡲࡹ࡫࡮ࡵ࠯ࡗࡽࡵ࡫ࠢਃ"): bstack11l1l_opy_ (u"ࠤࡤࡴࡵࡲࡩࡤࡣࡷ࡭ࡴࡴ࠯࡫ࡵࡲࡲࠧ਄"),
                          }
                      }
                      bstack1ll1l1111_opy_ = datetime.utcnow()
                      bstack1lllll111_opy_ = bstack1ll1l1111_opy_.strftime(bstack11l1l_opy_ (u"ࠥࠩ࡞࠳ࠥ࡮࠯ࠨࡨ࡙ࠫࡈ࠻ࠧࡐ࠾࡙ࠪ࠮ࠦࡨ࡙࡙ࠣࡉࠢਅ"))
                      bstack1lll1ll111_opy_ = os.environ.get(bstack11l1l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡉࡗࡅࡣ࡚࡛ࡉࡅࠩਆ")) if os.environ.get(bstack11l1l_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡊࡘࡆࡤ࡛ࡕࡊࡆࠪਇ")) else bstack1l1ll11111_opy_.get_property(bstack11l1l_opy_ (u"ࠨࡳࡥ࡭ࡕࡹࡳࡏࡤࠣਈ"))
                      payload = {
                          bstack11l1l_opy_ (u"ࠢࡦࡸࡨࡲࡹࡥࡴࡺࡲࡨࠦਉ"): bstack11l1l_opy_ (u"ࠣࡵࡧ࡯ࡤ࡫ࡶࡦࡰࡷࡷࠧਊ"),
                          bstack11l1l_opy_ (u"ࠤࡧࡥࡹࡧࠢ਋"): {
                              bstack11l1l_opy_ (u"ࠥࡸࡪࡹࡴࡩࡷࡥࡣࡺࡻࡩࡥࠤ਌"): bstack1lll1ll111_opy_,
                              bstack11l1l_opy_ (u"ࠦࡨࡸࡥࡢࡶࡨࡨࡤࡪࡡࡺࠤ਍"): bstack1lllll111_opy_,
                              bstack11l1l_opy_ (u"ࠧ࡫ࡶࡦࡰࡷࡣࡳࡧ࡭ࡦࠤ਎"): bstack11l1l_opy_ (u"ࠨࡓࡅࡍࡉࡩࡦࡺࡵࡳࡧࡓࡩࡷ࡬࡯ࡳ࡯ࡤࡲࡨ࡫ࠢਏ"),
                              bstack11l1l_opy_ (u"ࠢࡦࡸࡨࡲࡹࡥࡪࡴࡱࡱࠦਐ"): {
                                  bstack11l1l_opy_ (u"ࠣ࡯ࡨࡥࡸࡻࡲࡦࡵࠥ਑"): data,
                                  bstack11l1l_opy_ (u"ࠤࡶࡨࡰࡘࡵ࡯ࡋࡧࠦ਒"): bstack1l1ll11111_opy_.get_property(bstack11l1l_opy_ (u"ࠥࡷࡩࡱࡒࡶࡰࡌࡨࠧਓ"))
                              },
                              bstack11l1l_opy_ (u"ࠦࡺࡹࡥࡳࡡࡧࡥࡹࡧࠢਔ"): bstack1l1ll11111_opy_.get_property(bstack11l1l_opy_ (u"ࠧࡻࡳࡦࡴࡑࡥࡲ࡫ࠢਕ")),
                              bstack11l1l_opy_ (u"ࠨࡨࡰࡵࡷࡣ࡮ࡴࡦࡰࠤਖ"): get_host_info()
                          }
                      }
                      bstack1l1llll11l_opy_ = bstack1l1l1ll1l_opy_(cli.config, [bstack11l1l_opy_ (u"ࠢࡢࡲ࡬ࡷࠧਗ"), bstack11l1l_opy_ (u"ࠣࡧࡧࡷࡎࡴࡳࡵࡴࡸࡱࡪࡴࡴࡢࡶ࡬ࡳࡳࠨਘ"), bstack11l1l_opy_ (u"ࠤࡤࡴ࡮ࠨਙ")], bstack11ll1l111_opy_)
                      response = bstack1l111l111l_opy_(bstack11l1l_opy_ (u"ࠥࡔࡔ࡙ࡔࠣਚ"), bstack1l1llll11l_opy_, payload, config)
                      if(response.status_code >= 200 and response.status_code < 300):
                          logger.debug(bstack11l1l_opy_ (u"ࠦࡉࡧࡴࡢࠢࡶࡩࡳࡺࠠࡴࡷࡦࡧࡪࡹࡳࡧࡷ࡯ࡰࡾࠦࡴࡰࠢࡾࢁࠥࡽࡩࡵࡪࠣࡨࡦࡺࡡࠡࡽࢀࠦਛ").format(bstack11ll1l111_opy_, payload))
                      else:
                          logger.debug(bstack11l1l_opy_ (u"ࠧࡘࡥࡲࡷࡨࡷࡹࠦࡦࡢ࡫࡯ࡩࡩࠦࡦࡰࡴࠣࡿࢂࠦࡷࡪࡶ࡫ࠤࡩࡧࡴࡢࠢࡾࢁࠧਜ").format(bstack11ll1l111_opy_, payload))
          except Exception as e:
              logger.debug(bstack11l1l_opy_ (u"ࠨࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡶࡩࡳࡪࠠ࡬ࡧࡼࠤࡲ࡫ࡴࡳ࡫ࡦࡷࠥࡪࡡࡵࡣࠣࡻ࡮ࡺࡨࠡࡧࡵࡶࡴࡸࠠࡼࡿࠥਝ").format(e))
      bstack1ll1l1111l_opy_()
      bstack111l11l1_opy_(bstack1l1l1l11l_opy_, logger)
  except:
    pass
def bstack11l11l11l_opy_():
  global bstack1ll1l1l1l1_opy_
  global bstack1ll111111l_opy_
  global bstack11lllll11l_opy_
  global bstack1l11lll111_opy_
  global bstack1ll1ll1l11_opy_
  global bstack1llll1lll_opy_
  global CONFIG
  bstack1l1lllll1l_opy_ = os.environ.get(bstack11l1l_opy_ (u"ࠧࡇࡔࡄࡑࡊ࡝ࡏࡓࡍࡢ࡙ࡘࡋࡄࠨਞ"))
  if bstack1l1lllll1l_opy_ in [bstack11l1l_opy_ (u"ࠨࡴࡲࡦࡴࡺࠧਟ"), bstack11l1l_opy_ (u"ࠩࡳࡥࡧࡵࡴࠨਠ")]:
    bstack1lll1lll1l_opy_()
  percy.shutdown()
  if bstack1ll1l1l1l1_opy_:
    logger.warning(bstack1lll111ll_opy_.format(str(bstack1ll1l1l1l1_opy_)))
  else:
    try:
      bstack1l1l111ll1_opy_ = bstack11l11ll11l_opy_(bstack11l1l_opy_ (u"ࠪ࠲ࡧࡹࡴࡢࡥ࡮࠱ࡨࡵ࡮ࡧ࡫ࡪ࠲࡯ࡹ࡯࡯ࠩਡ"), logger)
      if bstack1l1l111ll1_opy_.get(bstack11l1l_opy_ (u"ࠫࡳࡻࡤࡨࡧࡢࡰࡴࡩࡡ࡭ࠩਢ")) and bstack1l1l111ll1_opy_.get(bstack11l1l_opy_ (u"ࠬࡴࡵࡥࡩࡨࡣࡱࡵࡣࡢ࡮ࠪਣ")).get(bstack11l1l_opy_ (u"࠭ࡨࡰࡵࡷࡲࡦࡳࡥࠨਤ")):
        logger.warning(bstack1lll111ll_opy_.format(str(bstack1l1l111ll1_opy_[bstack11l1l_opy_ (u"ࠧ࡯ࡷࡧ࡫ࡪࡥ࡬ࡰࡥࡤࡰࠬਥ")][bstack11l1l_opy_ (u"ࠨࡪࡲࡷࡹࡴࡡ࡮ࡧࠪਦ")])))
    except Exception as e:
      logger.error(e)
  if cli.is_running():
    bstack1l1l1lllll_opy_.invoke(bstack111111lll_opy_.bstack1l1111lll1_opy_)
  logger.info(bstack1l11l11l1l_opy_)
  global bstack111l1l1l1_opy_
  if bstack111l1l1l1_opy_:
    bstack11l111l1ll_opy_()
  try:
    with bstack1l1111ll_opy_:
      bstack11l1l11111_opy_ = bstack1ll111111l_opy_.copy()
    for driver in bstack11l1l11111_opy_:
      driver.quit()
  except Exception as e:
    pass
  logger.info(bstack1llll111l1_opy_)
  if bstack1llll1lll_opy_ == bstack11l1l_opy_ (u"ࠩࡵࡳࡧࡵࡴࠨਧ"):
    bstack1ll1ll1l11_opy_ = bstack11l1ll1l11_opy_(bstack11l1l_opy_ (u"ࠪࡶࡴࡨ࡯ࡵࡡࡨࡶࡷࡵࡲࡠ࡮࡬ࡷࡹ࠴ࡪࡴࡱࡱࠫਨ"))
  if bstack1llll1lll_opy_ == bstack11l1l_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࠫ਩") and len(bstack1l11lll111_opy_) == 0:
    bstack1l11lll111_opy_ = bstack11l1ll1l11_opy_(bstack11l1l_opy_ (u"ࠬࡶࡷࡠࡲࡼࡸࡪࡹࡴࡠࡧࡵࡶࡴࡸ࡟࡭࡫ࡶࡸ࠳ࡰࡳࡰࡰࠪਪ"))
    if len(bstack1l11lll111_opy_) == 0:
      bstack1l11lll111_opy_ = bstack11l1ll1l11_opy_(bstack11l1l_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹࡥࡰࡱࡲࡢࡩࡷࡸ࡯ࡳࡡ࡯࡭ࡸࡺ࠮࡫ࡵࡲࡲࠬਫ"))
  bstack1l111l1ll1_opy_ = bstack11l1l_opy_ (u"ࠧࠨਬ")
  if len(bstack11lllll11l_opy_) > 0:
    bstack1l111l1ll1_opy_ = bstack11l11ll1l1_opy_(bstack11lllll11l_opy_)
  elif len(bstack1l11lll111_opy_) > 0:
    bstack1l111l1ll1_opy_ = bstack11l11ll1l1_opy_(bstack1l11lll111_opy_)
  elif len(bstack1ll1ll1l11_opy_) > 0:
    bstack1l111l1ll1_opy_ = bstack11l11ll1l1_opy_(bstack1ll1ll1l11_opy_)
  elif len(bstack11111l1l1_opy_) > 0:
    bstack1l111l1ll1_opy_ = bstack11l11ll1l1_opy_(bstack11111l1l1_opy_)
  if bool(bstack1l111l1ll1_opy_):
    bstack11l11llll1_opy_(bstack1l111l1ll1_opy_)
  else:
    bstack11l11llll1_opy_()
  bstack111l11l1_opy_(bstack1l1llllll1_opy_, logger)
  if bstack1l1lllll1l_opy_ not in [bstack11l1l_opy_ (u"ࠨࡴࡲࡦࡴࡺ࠭ࡪࡰࡷࡩࡷࡴࡡ࡭ࠩਭ")]:
    bstack1l1lll111_opy_()
  bstack1l1lll1l11_opy_.bstack11lllll1l_opy_(CONFIG)
  if len(bstack1ll1ll1l11_opy_) > 0:
    sys.exit(len(bstack1ll1ll1l11_opy_))
def bstack1lll11ll1l_opy_(bstack1l11lllll1_opy_, frame):
  global bstack1l1ll11111_opy_
  logger.error(bstack11l1l1lll1_opy_)
  bstack1l1ll11111_opy_.bstack1ll1111ll1_opy_(bstack11l1l_opy_ (u"ࠩࡶࡨࡰࡑࡩ࡭࡮ࡑࡳࠬਮ"), bstack1l11lllll1_opy_)
  if hasattr(signal, bstack11l1l_opy_ (u"ࠪࡗ࡮࡭࡮ࡢ࡮ࡶࠫਯ")):
    bstack1l1ll11111_opy_.bstack1ll1111ll1_opy_(bstack11l1l_opy_ (u"ࠫࡸࡪ࡫ࡌ࡫࡯ࡰࡘ࡯ࡧ࡯ࡣ࡯ࠫਰ"), signal.Signals(bstack1l11lllll1_opy_).name)
  else:
    bstack1l1ll11111_opy_.bstack1ll1111ll1_opy_(bstack11l1l_opy_ (u"ࠬࡹࡤ࡬ࡍ࡬ࡰࡱ࡙ࡩࡨࡰࡤࡰࠬ਱"), bstack11l1l_opy_ (u"࠭ࡓࡊࡉࡘࡒࡐࡔࡏࡘࡐࠪਲ"))
  if cli.is_running():
    bstack1l1l1lllll_opy_.invoke(bstack111111lll_opy_.bstack1l1111lll1_opy_)
  bstack1l1lllll1l_opy_ = os.environ.get(bstack11l1l_opy_ (u"ࠧࡇࡔࡄࡑࡊ࡝ࡏࡓࡍࡢ࡙ࡘࡋࡄࠨਲ਼"))
  if bstack1l1lllll1l_opy_ == bstack11l1l_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࠨ਴") and not cli.is_enabled(CONFIG):
    bstack1ll1llll11_opy_.stop(bstack1l1ll11111_opy_.get_property(bstack11l1l_opy_ (u"ࠩࡶࡨࡰࡑࡩ࡭࡮ࡖ࡭࡬ࡴࡡ࡭ࠩਵ")))
  bstack11l11l11l_opy_()
  sys.exit(1)
def bstack1ll11l111l_opy_(err):
  logger.critical(bstack11l1ll1ll1_opy_.format(str(err)))
  bstack11l11llll1_opy_(bstack11l1ll1ll1_opy_.format(str(err)), True)
  atexit.unregister(bstack11l11l11l_opy_)
  bstack1lll1lll1l_opy_()
  sys.exit(1)
def bstack1ll1111l11_opy_(error, message):
  logger.critical(str(error))
  logger.critical(message)
  bstack11l11llll1_opy_(message, True)
  atexit.unregister(bstack11l11l11l_opy_)
  bstack1lll1lll1l_opy_()
  sys.exit(1)
def bstack111111l1_opy_():
  global CONFIG
  global bstack1111l1ll1_opy_
  global bstack11l1llll1l_opy_
  global bstack11ll1l1lll_opy_
  CONFIG = bstack11l1l1l1l_opy_()
  load_dotenv(CONFIG.get(bstack11l1l_opy_ (u"ࠪࡩࡳࡼࡆࡪ࡮ࡨࠫਸ਼")))
  bstack11llll1l11_opy_()
  bstack111lll11ll_opy_()
  CONFIG = bstack1l11llll11_opy_(CONFIG)
  update(CONFIG, bstack11l1llll1l_opy_)
  update(CONFIG, bstack1111l1ll1_opy_)
  if not cli.is_enabled(CONFIG):
    CONFIG = bstack111ll1ll11_opy_(CONFIG)
  bstack11ll1l1lll_opy_ = bstack11lll11ll1_opy_(CONFIG)
  os.environ[bstack11l1l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡅ࡚࡚ࡏࡎࡃࡗࡍࡔࡔࠧ਷")] = bstack11ll1l1lll_opy_.__str__().lower()
  bstack1l1ll11111_opy_.bstack1ll1111ll1_opy_(bstack11l1l_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯ࡤࡹࡥࡴࡵ࡬ࡳࡳ࠭ਸ"), bstack11ll1l1lll_opy_)
  if (bstack11l1l_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡓࡧ࡭ࡦࠩਹ") in CONFIG and bstack11l1l_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡔࡡ࡮ࡧࠪ਺") in bstack1111l1ll1_opy_) or (
          bstack11l1l_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠫ਻") in CONFIG and bstack11l1l_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡏࡣࡰࡩ਼ࠬ") not in bstack11l1llll1l_opy_):
    if os.getenv(bstack11l1l_opy_ (u"ࠪࡆࡘ࡚ࡁࡄࡍࡢࡇࡔࡓࡂࡊࡐࡈࡈࡤࡈࡕࡊࡎࡇࡣࡎࡊࠧ਽")):
      CONFIG[bstack11l1l_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭ਾ")] = os.getenv(bstack11l1l_opy_ (u"ࠬࡈࡓࡕࡃࡆࡏࡤࡉࡏࡎࡄࡌࡒࡊࡊ࡟ࡃࡗࡌࡐࡉࡥࡉࡅࠩਿ"))
    else:
      if not CONFIG.get(bstack11l1l_opy_ (u"ࠨࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࠤੀ"), bstack11l1l_opy_ (u"ࠢࠣੁ")) in bstack1lllll1111_opy_:
        bstack11lll1l1l1_opy_()
  elif (bstack11l1l_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠫੂ") not in CONFIG and bstack11l1l_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫ੃") in CONFIG) or (
          bstack11l1l_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡐࡤࡱࡪ࠭੄") in bstack11l1llll1l_opy_ and bstack11l1l_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡑࡥࡲ࡫ࠧ੅") not in bstack1111l1ll1_opy_):
    del (CONFIG[bstack11l1l_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧ੆")])
  if bstack111ll1ll1l_opy_(CONFIG):
    bstack1ll11l111l_opy_(bstack1llllll1l1_opy_)
  Config.bstack11l1l11ll1_opy_().bstack1ll1111ll1_opy_(bstack11l1l_opy_ (u"ࠨࡵࡴࡧࡵࡒࡦࡳࡥࠣੇ"), CONFIG[bstack11l1l_opy_ (u"ࠧࡶࡵࡨࡶࡓࡧ࡭ࡦࠩੈ")])
  bstack1lll1l1lll_opy_()
  bstack1l1ll111ll_opy_()
  if bstack1ll1ll111l_opy_ and not CONFIG.get(bstack11l1l_opy_ (u"ࠣࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࠦ੉"), bstack11l1l_opy_ (u"ࠤࠥ੊")) in bstack1lllll1111_opy_:
    CONFIG[bstack11l1l_opy_ (u"ࠪࡥࡵࡶࠧੋ")] = bstack11l111lll1_opy_(CONFIG)
    logger.info(bstack1111111l_opy_.format(CONFIG[bstack11l1l_opy_ (u"ࠫࡦࡶࡰࠨੌ")]))
  if not bstack11ll1l1lll_opy_:
    CONFIG[bstack11l1l_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨ੍")] = [{}]
def bstack11l1lll1ll_opy_(config, bstack1111ll1l_opy_):
  global CONFIG
  global bstack1ll1ll111l_opy_
  CONFIG = config
  bstack1ll1ll111l_opy_ = bstack1111ll1l_opy_
def bstack1l1ll111ll_opy_():
  global CONFIG
  global bstack1ll1ll111l_opy_
  if bstack11l1l_opy_ (u"࠭ࡡࡱࡲࠪ੎") in CONFIG:
    try:
      from appium import version
    except Exception as e:
      bstack1ll1111l11_opy_(e, bstack1l1111l1_opy_)
    bstack1ll1ll111l_opy_ = True
    bstack1l1ll11111_opy_.bstack1ll1111ll1_opy_(bstack11l1l_opy_ (u"ࠧࡢࡲࡳࡣࡦࡻࡴࡰ࡯ࡤࡸࡪ࠭੏"), True)
def bstack11l111lll1_opy_(config):
  bstack1llll1ll1l_opy_ = bstack11l1l_opy_ (u"ࠨࠩ੐")
  app = config[bstack11l1l_opy_ (u"ࠩࡤࡴࡵ࠭ੑ")]
  if isinstance(app, str):
    if os.path.splitext(app)[1] in bstack11l11l1l1_opy_:
      if os.path.exists(app):
        bstack1llll1ll1l_opy_ = bstack11llllll1_opy_(config, app)
      elif bstack11l111llll_opy_(app):
        bstack1llll1ll1l_opy_ = app
      else:
        bstack1ll11l111l_opy_(bstack1ll11111l_opy_.format(app))
    else:
      if bstack11l111llll_opy_(app):
        bstack1llll1ll1l_opy_ = app
      elif os.path.exists(app):
        bstack1llll1ll1l_opy_ = bstack11llllll1_opy_(app)
      else:
        bstack1ll11l111l_opy_(bstack11lllll111_opy_)
  else:
    if len(app) > 2:
      bstack1ll11l111l_opy_(bstack1llll11l11_opy_)
    elif len(app) == 2:
      if bstack11l1l_opy_ (u"ࠪࡴࡦࡺࡨࠨ੒") in app and bstack11l1l_opy_ (u"ࠫࡨࡻࡳࡵࡱࡰࡣ࡮ࡪࠧ੓") in app:
        if os.path.exists(app[bstack11l1l_opy_ (u"ࠬࡶࡡࡵࡪࠪ੔")]):
          bstack1llll1ll1l_opy_ = bstack11llllll1_opy_(config, app[bstack11l1l_opy_ (u"࠭ࡰࡢࡶ࡫ࠫ੕")], app[bstack11l1l_opy_ (u"ࠧࡤࡷࡶࡸࡴࡳ࡟ࡪࡦࠪ੖")])
        else:
          bstack1ll11l111l_opy_(bstack1ll11111l_opy_.format(app))
      else:
        bstack1ll11l111l_opy_(bstack1llll11l11_opy_)
    else:
      for key in app:
        if key in bstack111lll1ll1_opy_:
          if key == bstack11l1l_opy_ (u"ࠨࡲࡤࡸ࡭࠭੗"):
            if os.path.exists(app[key]):
              bstack1llll1ll1l_opy_ = bstack11llllll1_opy_(config, app[key])
            else:
              bstack1ll11l111l_opy_(bstack1ll11111l_opy_.format(app))
          else:
            bstack1llll1ll1l_opy_ = app[key]
        else:
          bstack1ll11l111l_opy_(bstack1l1lllll11_opy_)
  return bstack1llll1ll1l_opy_
def bstack11l111llll_opy_(bstack1llll1ll1l_opy_):
  import re
  bstack1l1ll1lll1_opy_ = re.compile(bstack11l1l_opy_ (u"ࡴࠥࡢࡠࡧ࠭ࡻࡃ࠰࡞࠵࠳࠹࡝ࡡ࠱ࡠ࠲ࡣࠪࠥࠤ੘"))
  bstack1l111lll_opy_ = re.compile(bstack11l1l_opy_ (u"ࡵࠦࡣࡡࡡ࠮ࡼࡄ࠱࡟࠶࠭࠺࡞ࡢ࠲ࡡ࠳࡝ࠫ࠱࡞ࡥ࠲ࢀࡁ࠮࡜࠳࠱࠾ࡢ࡟࠯࡞࠰ࡡ࠯ࠪࠢਖ਼"))
  if bstack11l1l_opy_ (u"ࠫࡧࡹ࠺࠰࠱ࠪਗ਼") in bstack1llll1ll1l_opy_ or re.fullmatch(bstack1l1ll1lll1_opy_, bstack1llll1ll1l_opy_) or re.fullmatch(bstack1l111lll_opy_, bstack1llll1ll1l_opy_):
    return True
  else:
    return False
@measure(event_name=EVENTS.bstack111ll1lll1_opy_, stage=STAGE.bstack1lll1l11l_opy_, bstack1l1l1llll_opy_=bstack11l1ll1l_opy_)
def bstack11llllll1_opy_(config, path, bstack1ll11ll11l_opy_=None):
  import requests
  from requests_toolbelt.multipart.encoder import MultipartEncoder
  import hashlib
  md5_hash = hashlib.md5(open(os.path.abspath(path), bstack11l1l_opy_ (u"ࠬࡸࡢࠨਜ਼")).read()).hexdigest()
  bstack111l1l11_opy_ = bstack1lll1ll11l_opy_(md5_hash)
  bstack1llll1ll1l_opy_ = None
  if bstack111l1l11_opy_:
    logger.info(bstack11l11l111l_opy_.format(bstack111l1l11_opy_, md5_hash))
    return bstack111l1l11_opy_
  bstack11ll1l1ll1_opy_ = datetime.datetime.now()
  bstack11l111l111_opy_ = MultipartEncoder(
    fields={
      bstack11l1l_opy_ (u"࠭ࡦࡪ࡮ࡨࠫੜ"): (os.path.basename(path), open(os.path.abspath(path), bstack11l1l_opy_ (u"ࠧࡳࡤࠪ੝")), bstack11l1l_opy_ (u"ࠨࡶࡨࡼࡹ࠵ࡰ࡭ࡣ࡬ࡲࠬਫ਼")),
      bstack11l1l_opy_ (u"ࠩࡦࡹࡸࡺ࡯࡮ࡡ࡬ࡨࠬ੟"): bstack1ll11ll11l_opy_
    }
  )
  response = requests.post(bstack11l1l1l1ll_opy_, data=bstack11l111l111_opy_,
                           headers={bstack11l1l_opy_ (u"ࠪࡇࡴࡴࡴࡦࡰࡷ࠱࡙ࡿࡰࡦࠩ੠"): bstack11l111l111_opy_.content_type},
                           auth=(config[bstack11l1l_opy_ (u"ࠫࡺࡹࡥࡳࡐࡤࡱࡪ࠭੡")], config[bstack11l1l_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷࡐ࡫ࡹࠨ੢")]))
  try:
    res = json.loads(response.text)
    bstack1llll1ll1l_opy_ = res[bstack11l1l_opy_ (u"࠭ࡡࡱࡲࡢࡹࡷࡲࠧ੣")]
    logger.info(bstack1111lll1l_opy_.format(bstack1llll1ll1l_opy_))
    bstack1ll11ll11_opy_(md5_hash, bstack1llll1ll1l_opy_)
    cli.bstack11lll111_opy_(bstack11l1l_opy_ (u"ࠢࡩࡶࡷࡴ࠿ࡻࡰ࡭ࡱࡤࡨࡤࡧࡰࡱࠤ੤"), datetime.datetime.now() - bstack11ll1l1ll1_opy_)
  except ValueError as err:
    bstack1ll11l111l_opy_(bstack1l11l1lll_opy_.format(str(err)))
  return bstack1llll1ll1l_opy_
def bstack1lll1l1lll_opy_(framework_name=None, args=None):
  global CONFIG
  global bstack1l1l11ll1_opy_
  bstack11ll111l1l_opy_ = 1
  bstack111ll1l1ll_opy_ = 1
  if bstack11l1l_opy_ (u"ࠨࡲࡤࡶࡦࡲ࡬ࡦ࡮ࡶࡔࡪࡸࡐ࡭ࡣࡷࡪࡴࡸ࡭ࠨ੥") in CONFIG:
    bstack111ll1l1ll_opy_ = CONFIG[bstack11l1l_opy_ (u"ࠩࡳࡥࡷࡧ࡬࡭ࡧ࡯ࡷࡕ࡫ࡲࡑ࡮ࡤࡸ࡫ࡵࡲ࡮ࠩ੦")]
  else:
    bstack111ll1l1ll_opy_ = bstack1l1l111l11_opy_(framework_name, args) or 1
  if bstack11l1l_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭੧") in CONFIG:
    bstack11ll111l1l_opy_ = len(CONFIG[bstack11l1l_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧ੨")])
  bstack1l1l11ll1_opy_ = int(bstack111ll1l1ll_opy_) * int(bstack11ll111l1l_opy_)
def bstack1l1l111l11_opy_(framework_name, args):
  if framework_name == bstack1l11l111l1_opy_ and args and bstack11l1l_opy_ (u"ࠬ࠳࠭ࡱࡴࡲࡧࡪࡹࡳࡦࡵࠪ੩") in args:
      bstack1ll1lll1ll_opy_ = args.index(bstack11l1l_opy_ (u"࠭࠭࠮ࡲࡵࡳࡨ࡫ࡳࡴࡧࡶࠫ੪"))
      return int(args[bstack1ll1lll1ll_opy_ + 1]) or 1
  return 1
def bstack1lll1ll11l_opy_(md5_hash):
  try:
    from filelock import FileLock
  except ImportError:
    logger.debug(bstack11l1l_opy_ (u"ࠧࡧ࡫࡯ࡩࡱࡵࡣ࡬ࠢࡱࡳࡹࠦࡡࡷࡣ࡬ࡰࡦࡨ࡬ࡦ࠮ࠣࡹࡸ࡯࡮ࡨࠢࡥࡥࡸ࡯ࡣࠡࡨ࡬ࡰࡪࠦ࡯ࡱࡧࡵࡥࡹ࡯࡯࡯ࡵࠪ੫"))
    bstack11llllll_opy_ = os.path.join(os.path.expanduser(bstack11l1l_opy_ (u"ࠨࢀࠪ੬")), bstack11l1l_opy_ (u"ࠩ࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࠩ੭"), bstack11l1l_opy_ (u"ࠪࡥࡵࡶࡕࡱ࡮ࡲࡥࡩࡓࡄ࠶ࡊࡤࡷ࡭࠴ࡪࡴࡱࡱࠫ੮"))
    if os.path.exists(bstack11llllll_opy_):
      try:
        bstack11l1l1l11_opy_ = json.load(open(bstack11llllll_opy_, bstack11l1l_opy_ (u"ࠫࡷࡨࠧ੯")))
        if md5_hash in bstack11l1l1l11_opy_:
          bstack1l1ll1l1_opy_ = bstack11l1l1l11_opy_[md5_hash]
          bstack1l1l11l11_opy_ = datetime.datetime.now()
          bstack111lllllll_opy_ = datetime.datetime.strptime(bstack1l1ll1l1_opy_[bstack11l1l_opy_ (u"ࠬࡺࡩ࡮ࡧࡶࡸࡦࡳࡰࠨੰ")], bstack11l1l_opy_ (u"࠭ࠥࡥ࠱ࠨࡱ࠴࡙ࠫࠡࠧࡋ࠾ࠪࡓ࠺ࠦࡕࠪੱ"))
          if (bstack1l1l11l11_opy_ - bstack111lllllll_opy_).days > 30:
            return None
          elif version.parse(str(__version__)) > version.parse(bstack1l1ll1l1_opy_[bstack11l1l_opy_ (u"ࠧࡴࡦ࡮ࡣࡻ࡫ࡲࡴ࡫ࡲࡲࠬੲ")]):
            return None
          return bstack1l1ll1l1_opy_[bstack11l1l_opy_ (u"ࠨ࡫ࡧࠫੳ")]
      except Exception as e:
        logger.debug(bstack11l1l_opy_ (u"ࠩࡈࡶࡷࡵࡲࠡࡴࡨࡥࡩ࡯࡮ࡨࠢࡐࡈ࠺ࠦࡨࡢࡵ࡫ࠤ࡫࡯࡬ࡦ࠼ࠣࡿࢂ࠭ੴ").format(str(e)))
    return None
  bstack11llllll_opy_ = os.path.join(os.path.expanduser(bstack11l1l_opy_ (u"ࠪࢂࠬੵ")), bstack11l1l_opy_ (u"ࠫ࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࠫ੶"), bstack11l1l_opy_ (u"ࠬࡧࡰࡱࡗࡳࡰࡴࡧࡤࡎࡆ࠸ࡌࡦࡹࡨ࠯࡬ࡶࡳࡳ࠭੷"))
  lock_file = bstack11llllll_opy_ + bstack11l1l_opy_ (u"࠭࠮࡭ࡱࡦ࡯ࠬ੸")
  try:
    with FileLock(lock_file, timeout=10):
      if os.path.exists(bstack11llllll_opy_):
        with open(bstack11llllll_opy_, bstack11l1l_opy_ (u"ࠧࡳࠩ੹")) as f:
          content = f.read().strip()
          if content:
            bstack11l1l1l11_opy_ = json.loads(content)
            if md5_hash in bstack11l1l1l11_opy_:
              bstack1l1ll1l1_opy_ = bstack11l1l1l11_opy_[md5_hash]
              bstack1l1l11l11_opy_ = datetime.datetime.now()
              bstack111lllllll_opy_ = datetime.datetime.strptime(bstack1l1ll1l1_opy_[bstack11l1l_opy_ (u"ࠨࡶ࡬ࡱࡪࡹࡴࡢ࡯ࡳࠫ੺")], bstack11l1l_opy_ (u"ࠩࠨࡨ࠴ࠫ࡭࠰ࠧ࡜ࠤࠪࡎ࠺ࠦࡏ࠽ࠩࡘ࠭੻"))
              if (bstack1l1l11l11_opy_ - bstack111lllllll_opy_).days > 30:
                return None
              elif version.parse(str(__version__)) > version.parse(bstack1l1ll1l1_opy_[bstack11l1l_opy_ (u"ࠪࡷࡩࡱ࡟ࡷࡧࡵࡷ࡮ࡵ࡮ࠨ੼")]):
                return None
              return bstack1l1ll1l1_opy_[bstack11l1l_opy_ (u"ࠫ࡮ࡪࠧ੽")]
      return None
  except Exception as e:
    logger.debug(bstack11l1l_opy_ (u"ࠬࡋࡲࡳࡱࡵࠤࡼ࡯ࡴࡩࠢࡩ࡭ࡱ࡫ࠠ࡭ࡱࡦ࡯࡮ࡴࡧࠡࡨࡲࡶࠥࡓࡄ࠶ࠢ࡫ࡥࡸ࡮࠺ࠡࡽࢀࠫ੾").format(str(e)))
    return None
def bstack1ll11ll11_opy_(md5_hash, bstack1llll1ll1l_opy_):
  try:
    from filelock import FileLock
  except ImportError:
    logger.debug(bstack11l1l_opy_ (u"࠭ࡦࡪ࡮ࡨࡰࡴࡩ࡫ࠡࡰࡲࡸࠥࡧࡶࡢ࡫࡯ࡥࡧࡲࡥ࠭ࠢࡸࡷ࡮ࡴࡧࠡࡤࡤࡷ࡮ࡩࠠࡧ࡫࡯ࡩࠥࡵࡰࡦࡴࡤࡸ࡮ࡵ࡮ࡴࠩ੿"))
    bstack1lll11111_opy_ = os.path.join(os.path.expanduser(bstack11l1l_opy_ (u"ࠧࡿࠩ઀")), bstack11l1l_opy_ (u"ࠨ࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࠨઁ"))
    if not os.path.exists(bstack1lll11111_opy_):
      os.makedirs(bstack1lll11111_opy_)
    bstack11llllll_opy_ = os.path.join(os.path.expanduser(bstack11l1l_opy_ (u"ࠩࢁࠫં")), bstack11l1l_opy_ (u"ࠪ࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࠪઃ"), bstack11l1l_opy_ (u"ࠫࡦࡶࡰࡖࡲ࡯ࡳࡦࡪࡍࡅ࠷ࡋࡥࡸ࡮࠮࡫ࡵࡲࡲࠬ઄"))
    bstack11ll1l1l1l_opy_ = {
      bstack11l1l_opy_ (u"ࠬ࡯ࡤࠨઅ"): bstack1llll1ll1l_opy_,
      bstack11l1l_opy_ (u"࠭ࡴࡪ࡯ࡨࡷࡹࡧ࡭ࡱࠩઆ"): datetime.datetime.strftime(datetime.datetime.now(), bstack11l1l_opy_ (u"ࠧࠦࡦ࠲ࠩࡲ࠵࡚ࠥࠢࠨࡌ࠿ࠫࡍ࠻ࠧࡖࠫઇ")),
      bstack11l1l_opy_ (u"ࠨࡵࡧ࡯ࡤࡼࡥࡳࡵ࡬ࡳࡳ࠭ઈ"): str(__version__)
    }
    try:
      bstack11l1l1l11_opy_ = {}
      if os.path.exists(bstack11llllll_opy_):
        bstack11l1l1l11_opy_ = json.load(open(bstack11llllll_opy_, bstack11l1l_opy_ (u"ࠩࡵࡦࠬઉ")))
      bstack11l1l1l11_opy_[md5_hash] = bstack11ll1l1l1l_opy_
      with open(bstack11llllll_opy_, bstack11l1l_opy_ (u"ࠥࡻ࠰ࠨઊ")) as outfile:
        json.dump(bstack11l1l1l11_opy_, outfile)
    except Exception as e:
      logger.debug(bstack11l1l_opy_ (u"ࠫࡊࡸࡲࡰࡴࠣࡹࡵࡪࡡࡵ࡫ࡱ࡫ࠥࡓࡄ࠶ࠢ࡫ࡥࡸ࡮ࠠࡧ࡫࡯ࡩ࠿ࠦࡻࡾࠩઋ").format(str(e)))
    return
  bstack1lll11111_opy_ = os.path.join(os.path.expanduser(bstack11l1l_opy_ (u"ࠬࢄࠧઌ")), bstack11l1l_opy_ (u"࠭࠮ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠭ઍ"))
  if not os.path.exists(bstack1lll11111_opy_):
    os.makedirs(bstack1lll11111_opy_)
  bstack11llllll_opy_ = os.path.join(os.path.expanduser(bstack11l1l_opy_ (u"ࠧࡿࠩ઎")), bstack11l1l_opy_ (u"ࠨ࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࠨએ"), bstack11l1l_opy_ (u"ࠩࡤࡴࡵ࡛ࡰ࡭ࡱࡤࡨࡒࡊ࠵ࡉࡣࡶ࡬࠳ࡰࡳࡰࡰࠪઐ"))
  lock_file = bstack11llllll_opy_ + bstack11l1l_opy_ (u"ࠪ࠲ࡱࡵࡣ࡬ࠩઑ")
  bstack11ll1l1l1l_opy_ = {
    bstack11l1l_opy_ (u"ࠫ࡮ࡪࠧ઒"): bstack1llll1ll1l_opy_,
    bstack11l1l_opy_ (u"ࠬࡺࡩ࡮ࡧࡶࡸࡦࡳࡰࠨઓ"): datetime.datetime.strftime(datetime.datetime.now(), bstack11l1l_opy_ (u"࠭ࠥࡥ࠱ࠨࡱ࠴࡙ࠫࠡࠧࡋ࠾ࠪࡓ࠺ࠦࡕࠪઔ")),
    bstack11l1l_opy_ (u"ࠧࡴࡦ࡮ࡣࡻ࡫ࡲࡴ࡫ࡲࡲࠬક"): str(__version__)
  }
  try:
    with FileLock(lock_file, timeout=10):
      bstack11l1l1l11_opy_ = {}
      if os.path.exists(bstack11llllll_opy_):
        with open(bstack11llllll_opy_, bstack11l1l_opy_ (u"ࠨࡴࠪખ")) as f:
          content = f.read().strip()
          if content:
            bstack11l1l1l11_opy_ = json.loads(content)
      bstack11l1l1l11_opy_[md5_hash] = bstack11ll1l1l1l_opy_
      with open(bstack11llllll_opy_, bstack11l1l_opy_ (u"ࠤࡺࠦગ")) as outfile:
        json.dump(bstack11l1l1l11_opy_, outfile)
  except Exception as e:
    logger.debug(bstack11l1l_opy_ (u"ࠪࡉࡷࡸ࡯ࡳࠢࡺ࡭ࡹ࡮ࠠࡧ࡫࡯ࡩࠥࡲ࡯ࡤ࡭࡬ࡲ࡬ࠦࡦࡰࡴࠣࡑࡉ࠻ࠠࡩࡣࡶ࡬ࠥࡻࡰࡥࡣࡷࡩ࠿ࠦࡻࡾࠩઘ").format(str(e)))
def bstack1lll1l1111_opy_(self):
  return
def bstack11ll11lll1_opy_(self):
  return
def bstack1l1lll11ll_opy_():
  global bstack1lll111l_opy_
  bstack1lll111l_opy_ = True
@measure(event_name=EVENTS.bstack111l11l1l_opy_, stage=STAGE.bstack1lll1l11l_opy_, bstack1l1l1llll_opy_=bstack11l1ll1l_opy_)
def bstack1lll11l111_opy_(self):
  global bstack11l1ll111l_opy_
  global bstack1ll1llll1l_opy_
  global bstack11llllllll_opy_
  try:
    if bstack11l1l_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࠫઙ") in bstack11l1ll111l_opy_ and self.session_id != None and bstack11lll11l_opy_(threading.current_thread(), bstack11l1l_opy_ (u"ࠬࡺࡥࡴࡶࡖࡸࡦࡺࡵࡴࠩચ"), bstack11l1l_opy_ (u"࠭ࠧછ")) != bstack11l1l_opy_ (u"ࠧࡴ࡭࡬ࡴࡵ࡫ࡤࠨજ"):
      bstack1ll11l1l1l_opy_ = bstack11l1l_opy_ (u"ࠨࡲࡤࡷࡸ࡫ࡤࠨઝ") if len(threading.current_thread().bstackTestErrorMessages) == 0 else bstack11l1l_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࠩઞ")
      if bstack1ll11l1l1l_opy_ == bstack11l1l_opy_ (u"ࠪࡪࡦ࡯࡬ࡦࡦࠪટ"):
        bstack11111111_opy_(logger)
      if self != None:
        bstack111lllll1l_opy_(self, bstack1ll11l1l1l_opy_, bstack11l1l_opy_ (u"ࠫ࠱ࠦࠧઠ").join(threading.current_thread().bstackTestErrorMessages))
    threading.current_thread().testStatus = bstack11l1l_opy_ (u"ࠬ࠭ડ")
    if bstack11l1l_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹ࠭ઢ") in bstack11l1ll111l_opy_ and getattr(threading.current_thread(), bstack11l1l_opy_ (u"ࠧࡢ࠳࠴ࡽࡕࡲࡡࡵࡨࡲࡶࡲ࠭ણ"), None):
      bstack11ll1l11l1_opy_.bstack1ll1ll1ll1_opy_(self, bstack11ll11l111_opy_, logger, wait=True)
    if bstack11l1l_opy_ (u"ࠨࡤࡨ࡬ࡦࡼࡥࠨત") in bstack11l1ll111l_opy_:
      if not threading.currentThread().behave_test_status:
        bstack111lllll1l_opy_(self, bstack11l1l_opy_ (u"ࠤࡳࡥࡸࡹࡥࡥࠤથ"))
      bstack111lllll11_opy_.bstack1l11llllll_opy_(self)
  except Exception as e:
    logger.debug(bstack11l1l_opy_ (u"ࠥࡉࡷࡸ࡯ࡳࠢࡺ࡬࡮ࡲࡥࠡ࡯ࡤࡶࡰ࡯࡮ࡨࠢࡶࡸࡦࡺࡵࡴ࠼ࠣࠦદ") + str(e))
  bstack11llllllll_opy_(self)
  self.session_id = None
def bstack1l11l1l1l_opy_(self, *args, **kwargs):
  try:
    from selenium.webdriver.remote.remote_connection import RemoteConnection
    from bstack_utils.helper import bstack1l111llll_opy_
    global bstack11l1ll111l_opy_
    command_executor = kwargs.get(bstack11l1l_opy_ (u"ࠫࡨࡵ࡭࡮ࡣࡱࡨࡤ࡫ࡸࡦࡥࡸࡸࡴࡸࠧધ"), bstack11l1l_opy_ (u"ࠬ࠭ન"))
    bstack1l1lll1l_opy_ = False
    if type(command_executor) == str and bstack11l1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡩ࡯࡮ࠩ઩") in command_executor:
      bstack1l1lll1l_opy_ = True
    elif isinstance(command_executor, RemoteConnection) and bstack11l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡣࡰ࡯ࠪપ") in str(getattr(command_executor, bstack11l1l_opy_ (u"ࠨࡡࡸࡶࡱ࠭ફ"), bstack11l1l_opy_ (u"ࠩࠪબ"))):
      bstack1l1lll1l_opy_ = True
    else:
      kwargs = bstack11llll11l1_opy_.bstack11ll11ll_opy_(bstack11llll1111_opy_=kwargs, config=CONFIG)
      return bstack1l1l11111_opy_(self, *args, **kwargs)
    if bstack1l1lll1l_opy_:
      bstack11l1111ll1_opy_ = bstack1ll11l1l1_opy_.bstack1llll1l1_opy_(CONFIG, bstack11l1ll111l_opy_)
      if kwargs.get(bstack11l1l_opy_ (u"ࠪࡳࡵࡺࡩࡰࡰࡶࠫભ")):
        kwargs[bstack11l1l_opy_ (u"ࠫࡴࡶࡴࡪࡱࡱࡷࠬમ")] = bstack1l111llll_opy_(kwargs[bstack11l1l_opy_ (u"ࠬࡵࡰࡵ࡫ࡲࡲࡸ࠭ય")], bstack11l1ll111l_opy_, CONFIG, bstack11l1111ll1_opy_)
      elif kwargs.get(bstack11l1l_opy_ (u"࠭ࡤࡦࡵ࡬ࡶࡪࡪ࡟ࡤࡣࡳࡥࡧ࡯࡬ࡪࡶ࡬ࡩࡸ࠭ર")):
        kwargs[bstack11l1l_opy_ (u"ࠧࡥࡧࡶ࡭ࡷ࡫ࡤࡠࡥࡤࡴࡦࡨࡩ࡭࡫ࡷ࡭ࡪࡹࠧ઱")] = bstack1l111llll_opy_(kwargs[bstack11l1l_opy_ (u"ࠨࡦࡨࡷ࡮ࡸࡥࡥࡡࡦࡥࡵࡧࡢࡪ࡮࡬ࡸ࡮࡫ࡳࠨલ")], bstack11l1ll111l_opy_, CONFIG, bstack11l1111ll1_opy_)
  except Exception as e:
    logger.error(bstack11l1l_opy_ (u"ࠤࡈࡶࡷࡵࡲࠡࡹ࡫ࡩࡳࠦࡰࡳࡱࡦࡩࡸࡹࡩ࡯ࡩࠣࡗࡉࡑࠠࡤࡣࡳࡷ࠿ࠦࡻࡾࠤળ").format(str(e)))
  return bstack1l1l11111_opy_(self, *args, **kwargs)
@measure(event_name=EVENTS.bstack1llllll111_opy_, stage=STAGE.bstack1lll1l11l_opy_, bstack1l1l1llll_opy_=bstack11l1ll1l_opy_)
def bstack11l111l1l_opy_(self, command_executor=bstack11l1l_opy_ (u"ࠥ࡬ࡹࡺࡰ࠻࠱࠲࠵࠷࠽࠮࠱࠰࠳࠲࠶ࡀ࠴࠵࠶࠷ࠦ઴"), *args, **kwargs):
  global bstack1ll1llll1l_opy_
  global bstack1ll111111l_opy_
  bstack11l1l1l11l_opy_ = bstack1l11l1l1l_opy_(self, command_executor=command_executor, *args, **kwargs)
  if not bstack11llll111_opy_.on():
    return bstack11l1l1l11l_opy_
  try:
    logger.debug(bstack11l1l_opy_ (u"ࠫࡈࡵ࡭࡮ࡣࡱࡨࠥࡋࡸࡦࡥࡸࡸࡴࡸࠠࡸࡪࡨࡲࠥࡈࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࠤࡆࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠡ࡫ࡶࠤ࡫ࡧ࡬ࡴࡧࠣ࠱ࠥࢁࡽࠨવ").format(str(command_executor)))
    logger.debug(bstack11l1l_opy_ (u"ࠬࡎࡵࡣࠢࡘࡖࡑࠦࡩࡴࠢ࠰ࠤࢀࢃࠧશ").format(str(command_executor._url)))
    from selenium.webdriver.remote.remote_connection import RemoteConnection
    if isinstance(command_executor, RemoteConnection) and bstack11l1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡩ࡯࡮ࠩષ") in command_executor._url:
      bstack1l1ll11111_opy_.bstack1ll1111ll1_opy_(bstack11l1l_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱ࡟ࡴࡧࡶࡷ࡮ࡵ࡮ࠨસ"), True)
  except:
    pass
  if (isinstance(command_executor, str) and bstack11l1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡤࡱࡰࠫહ") in command_executor):
    bstack1l1ll11111_opy_.bstack1ll1111ll1_opy_(bstack11l1l_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬ࡡࡶࡩࡸࡹࡩࡰࡰࠪ઺"), True)
  threading.current_thread().bstackSessionDriver = self
  bstack1l1ll1111l_opy_ = getattr(threading.current_thread(), bstack11l1l_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭ࡗࡩࡸࡺࡍࡦࡶࡤࠫ઻"), None)
  bstack1ll1lllll_opy_ = {}
  if self.capabilities is not None:
    bstack1ll1lllll_opy_[bstack11l1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡤࡴࡡ࡮ࡧ઼ࠪ")] = self.capabilities.get(bstack11l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡔࡡ࡮ࡧࠪઽ"))
    bstack1ll1lllll_opy_[bstack11l1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸ࡟ࡷࡧࡵࡷ࡮ࡵ࡮ࠨા")] = self.capabilities.get(bstack11l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡗࡧࡵࡷ࡮ࡵ࡮ࠨિ"))
    bstack1ll1lllll_opy_[bstack11l1l_opy_ (u"ࠨࡥ࡫ࡶࡴࡳࡥࡠࡱࡳࡸ࡮ࡵ࡮ࡴࠩી")] = self.capabilities.get(bstack11l1l_opy_ (u"ࠩࡪࡳࡴ࡭࠺ࡤࡪࡵࡳࡲ࡫ࡏࡱࡶ࡬ࡳࡳࡹࠧુ"))
  if CONFIG.get(bstack11l1l_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠪૂ"), False) and bstack11llll11l1_opy_.bstack111lllll_opy_(bstack1ll1lllll_opy_):
    threading.current_thread().a11yPlatform = True
  if bstack11l1l_opy_ (u"ࠫࡧ࡫ࡨࡢࡸࡨࠫૃ") in bstack11l1ll111l_opy_ or bstack11l1l_opy_ (u"ࠬࡸ࡯ࡣࡱࡷࠫૄ") in bstack11l1ll111l_opy_:
    bstack1ll1llll11_opy_.bstack1llll1llll_opy_(self)
  if bstack11l1l_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹ࠭ૅ") in bstack11l1ll111l_opy_ and bstack1l1ll1111l_opy_ and bstack1l1ll1111l_opy_.get(bstack11l1l_opy_ (u"ࠧࡴࡶࡤࡸࡺࡹࠧ૆"), bstack11l1l_opy_ (u"ࠨࠩે")) == bstack11l1l_opy_ (u"ࠩࡳࡩࡳࡪࡩ࡯ࡩࠪૈ"):
    bstack1ll1llll11_opy_.bstack1llll1llll_opy_(self)
  bstack1ll1llll1l_opy_ = self.session_id
  with bstack1l1111ll_opy_:
    bstack1ll111111l_opy_.append(self)
  return bstack11l1l1l11l_opy_
def bstack11lll111l1_opy_(args):
  return bstack11l1l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡨࡼࡪࡩࡵࡵࡱࡵࠫૉ") in str(args)
def bstack111lll1l1l_opy_(self, driver_command, *args, **kwargs):
  global bstack111ll11l_opy_
  global bstack1l1lll1ll1_opy_
  bstack111111111_opy_ = bstack11lll11l_opy_(threading.current_thread(), bstack11l1l_opy_ (u"ࠫ࡮ࡹࡁ࠲࠳ࡼࡘࡪࡹࡴࠨ૊"), None) and bstack11lll11l_opy_(
          threading.current_thread(), bstack11l1l_opy_ (u"ࠬࡧ࠱࠲ࡻࡓࡰࡦࡺࡦࡰࡴࡰࠫો"), None)
  bstack111ll111_opy_ = bstack11lll11l_opy_(threading.current_thread(), bstack11l1l_opy_ (u"࠭ࡩࡴࡃࡳࡴࡆ࠷࠱ࡺࡖࡨࡷࡹ࠭ૌ"), None) and bstack11lll11l_opy_(
          threading.current_thread(), bstack11l1l_opy_ (u"ࠧࡢࡲࡳࡅ࠶࠷ࡹࡑ࡮ࡤࡸ࡫ࡵࡲ࡮્ࠩ"), None)
  bstack11lll11lll_opy_ = getattr(self, bstack11l1l_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫ࡂ࠳࠴ࡽࡘ࡮࡯ࡶ࡮ࡧࡗࡨࡧ࡮ࠨ૎"), None) != None and getattr(self, bstack11l1l_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬ࡃ࠴࠵ࡾ࡙ࡨࡰࡷ࡯ࡨࡘࡩࡡ࡯ࠩ૏"), None) == True
  if not bstack1l1lll1ll1_opy_ and bstack11l1l_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠪૐ") in CONFIG and CONFIG[bstack11l1l_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠫ૑")] == True and bstack111lll1l_opy_.bstack1l11ll11_opy_(driver_command) and (bstack11lll11lll_opy_ or bstack111111111_opy_ or bstack111ll111_opy_) and not bstack11lll111l1_opy_(args):
    try:
      bstack1l1lll1ll1_opy_ = True
      logger.debug(bstack11l1l_opy_ (u"ࠬࡖࡥࡳࡨࡲࡶࡲ࡯࡮ࡨࠢࡶࡧࡦࡴࠠࡧࡱࡵࠤࢀࢃࠧ૒").format(driver_command))
      bstack11llll1lll_opy_ = perform_scan(self, driver_command=driver_command)
      logger.debug(bstack11llll1lll_opy_)
      try:
        bstack1ll111l1l_opy_ = {
          bstack11l1l_opy_ (u"ࠨࡲࡦࡳࡸࡩࡸࡺࠢ૓"): {
            bstack11l1l_opy_ (u"ࠢࡤࡱࡰࡱࡦࡴࡤࠣ૔"): bstack11l1l_opy_ (u"ࠣࡃ࠴࠵࡞ࡥࡓࡄࡃࡑࠦ૕"),
            bstack11l1l_opy_ (u"ࠤࡳࡥࡷࡧ࡭ࡦࡶࡨࡶࡸࠨ૖"): [
              {
                bstack11l1l_opy_ (u"ࠥࡱࡪࡺࡨࡰࡦࠥ૗"): driver_command
              }
            ]
          },
          bstack11l1l_opy_ (u"ࠦࡷ࡫ࡳࡱࡱࡱࡷࡪࠨ૘"): {
            bstack11l1l_opy_ (u"ࠧࡨ࡯ࡥࡻࠥ૙"): {
              bstack11l1l_opy_ (u"ࠨ࡭ࡴࡩࠥ૚"): bstack11llll1lll_opy_.get(bstack11l1l_opy_ (u"ࠢ࡮ࡵࡪࠦ૛"), bstack11l1l_opy_ (u"ࠣࠤ૜")) if isinstance(bstack11llll1lll_opy_, dict) else bstack11l1l_opy_ (u"ࠤࠥ૝"),
              bstack11l1l_opy_ (u"ࠥࡷࡺࡩࡣࡦࡵࡶࠦ૞"): bstack11llll1lll_opy_.get(bstack11l1l_opy_ (u"ࠦࡸࡻࡣࡤࡧࡶࡷࠧ૟"), True) if isinstance(bstack11llll1lll_opy_, dict) else True
            }
          }
        }
        logger.debug(bstack11l1l_opy_ (u"ࠬࡇࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡹࡣࡢࡰࠣࡥࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࠠ࡭ࡱࡪࠤࡩࡧࡴࡢ࠼ࠣࡿࢂ࠭ૠ").format(bstack1ll111l1l_opy_))
        bstack1ll11l1ll_opy_.info(json.dumps(bstack1ll111l1l_opy_, separators=(bstack11l1l_opy_ (u"࠭ࠬࠨૡ"), bstack11l1l_opy_ (u"ࠧ࠻ࠩૢ"))))
      except Exception as bstack1l1l1ll1l1_opy_:
        logger.debug(bstack11l1l_opy_ (u"ࠨࡈࡤ࡭ࡱ࡫ࡤࠡࡶࡲࠤࡱࡵࡧࠡࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠡࡵࡦࡥࡳࠦࡤࡢࡶࡤ࠾ࠥࢁࡽࠨૣ").format(str(bstack1l1l1ll1l1_opy_)))
    except Exception as err:
      logger.debug(bstack11l1l_opy_ (u"ࠩࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥࡶࡥࡳࡨࡲࡶࡲࠦࡳࡤࡣࡱࠤࢀࢃࠧ૤").format(str(err)))
    bstack1l1lll1ll1_opy_ = False
  response = bstack111ll11l_opy_(self, driver_command, *args, **kwargs)
  if (bstack11l1l_opy_ (u"ࠪࡶࡴࡨ࡯ࡵࠩ૥") in str(bstack11l1ll111l_opy_).lower() or bstack11l1l_opy_ (u"ࠫࡧ࡫ࡨࡢࡸࡨࠫ૦") in str(bstack11l1ll111l_opy_).lower()) and bstack11llll111_opy_.on():
    try:
      if driver_command == bstack11l1l_opy_ (u"ࠬࡹࡣࡳࡧࡨࡲࡸ࡮࡯ࡵࠩ૧"):
        bstack1ll1llll11_opy_.bstack1l1lll111l_opy_({
            bstack11l1l_opy_ (u"࠭ࡩ࡮ࡣࡪࡩࠬ૨"): response[bstack11l1l_opy_ (u"ࠧࡷࡣ࡯ࡹࡪ࠭૩")],
            bstack11l1l_opy_ (u"ࠨࡶࡨࡷࡹࡥࡲࡶࡰࡢࡹࡺ࡯ࡤࠨ૪"): bstack1ll1llll11_opy_.current_test_uuid() if bstack1ll1llll11_opy_.current_test_uuid() else bstack11llll111_opy_.current_hook_uuid()
        })
    except:
      pass
  return response
@measure(event_name=EVENTS.bstack11l1111l11_opy_, stage=STAGE.bstack1lll1l11l_opy_, bstack1l1l1llll_opy_=bstack11l1ll1l_opy_)
def bstack111l111ll_opy_(self, command_executor,
             desired_capabilities=None, browser_profile=None, proxy=None,
             keep_alive=True, file_detector=None, options=None, *args, **kwargs):
  global CONFIG
  global bstack1ll1llll1l_opy_
  global bstack11ll1111ll_opy_
  global bstack11l1ll1l_opy_
  global bstack111ll1l11_opy_
  global bstack1l1llll1ll_opy_
  global bstack11l1ll111l_opy_
  global bstack1l1l11111_opy_
  global bstack1ll111111l_opy_
  global bstack11ll1111_opy_
  global bstack11ll11l111_opy_
  if os.getenv(bstack11l1l_opy_ (u"ࠩࡅࡗࡤࡇ࠱࠲࡛ࡢࡎ࡜࡚ࠧ૫")) is not None and bstack11llll11l1_opy_.bstack1lllll1lll_opy_(CONFIG) is None:
    CONFIG[bstack11l1l_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠪ૬")] = True
  CONFIG[bstack11l1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡖࡈࡐ࠭૭")] = str(bstack11l1ll111l_opy_) + str(__version__)
  bstack1ll1lll11l_opy_ = os.environ[bstack11l1l_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡊࡘࡆࡤ࡛ࡕࡊࡆࠪ૮")]
  bstack11l1111ll1_opy_ = bstack1ll11l1l1_opy_.bstack1llll1l1_opy_(CONFIG, bstack11l1ll111l_opy_)
  CONFIG[bstack11l1l_opy_ (u"࠭ࡴࡦࡵࡷ࡬ࡺࡨࡂࡶ࡫࡯ࡨ࡚ࡻࡩࡥࠩ૯")] = bstack1ll1lll11l_opy_
  CONFIG[bstack11l1l_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡖࡲࡰࡦࡸࡧࡹࡓࡡࡱࠩ૰")] = bstack11l1111ll1_opy_
  if CONFIG.get(bstack11l1l_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࡐࡲࡷ࡭ࡴࡴࡳࠨ૱"),bstack11l1l_opy_ (u"ࠩࠪ૲")) and bstack11l1l_opy_ (u"ࠪࡶࡴࡨ࡯ࡵࠩ૳") in bstack11l1ll111l_opy_:
    CONFIG[bstack11l1l_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࡓࡵࡺࡩࡰࡰࡶࠫ૴")].pop(bstack11l1l_opy_ (u"ࠬ࡯࡮ࡤ࡮ࡸࡨࡪ࡚ࡡࡨࡵࡌࡲ࡙࡫ࡳࡵ࡫ࡱ࡫ࡘࡩ࡯ࡱࡧࠪ૵"), None)
    CONFIG[bstack11l1l_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࡕࡰࡵ࡫ࡲࡲࡸ࠭૶")].pop(bstack11l1l_opy_ (u"ࠧࡦࡺࡦࡰࡺࡪࡥࡕࡣࡪࡷࡎࡴࡔࡦࡵࡷ࡭ࡳ࡭ࡓࡤࡱࡳࡩࠬ૷"), None)
  command_executor = bstack11l111l11_opy_()
  logger.debug(bstack1llll11l1_opy_.format(command_executor))
  proxy = bstack1l111l1ll_opy_(CONFIG, proxy)
  bstack1ll11111l1_opy_ = 0 if bstack11ll1111ll_opy_ < 0 else bstack11ll1111ll_opy_
  try:
    if bstack111ll1l11_opy_ is True:
      bstack1ll11111l1_opy_ = int(multiprocessing.current_process().name)
    elif bstack1l1llll1ll_opy_ is True:
      bstack1ll11111l1_opy_ = int(threading.current_thread().name)
  except:
    bstack1ll11111l1_opy_ = 0
  bstack1l1l11l1l_opy_ = bstack111lll11l1_opy_(CONFIG, bstack1ll11111l1_opy_)
  logger.debug(bstack11lll1111_opy_.format(str(bstack1l1l11l1l_opy_)))
  if bstack11l1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡌࡰࡥࡤࡰࠬ૸") in CONFIG and bstack1llll1ll1_opy_(CONFIG[bstack11l1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡍࡱࡦࡥࡱ࠭ૹ")]):
    bstack1ll1l11l1l_opy_(bstack1l1l11l1l_opy_)
  if bstack11llll11l1_opy_.bstack11l11ll1_opy_(CONFIG, bstack1ll11111l1_opy_) and bstack11llll11l1_opy_.bstack11111ll11_opy_(bstack1l1l11l1l_opy_, options, desired_capabilities, CONFIG):
    threading.current_thread().a11yPlatform = True
    if (cli.accessibility is None or not cli.accessibility.is_enabled()):
      bstack11llll11l1_opy_.set_capabilities(bstack1l1l11l1l_opy_, CONFIG)
  if desired_capabilities:
    bstack11ll1llll1_opy_ = bstack1l11llll11_opy_(desired_capabilities)
    bstack11ll1llll1_opy_[bstack11l1l_opy_ (u"ࠪࡹࡸ࡫ࡗ࠴ࡅࠪૺ")] = bstack1l11llll_opy_(CONFIG)
    bstack11l1l1llll_opy_ = bstack111lll11l1_opy_(bstack11ll1llll1_opy_)
    if bstack11l1l1llll_opy_:
      bstack1l1l11l1l_opy_ = update(bstack11l1l1llll_opy_, bstack1l1l11l1l_opy_)
    desired_capabilities = None
  if options:
    bstack1111l1l1l_opy_(options, bstack1l1l11l1l_opy_)
  if not options:
    options = bstack1ll1l11111_opy_(bstack1l1l11l1l_opy_)
  bstack11ll11l111_opy_ = CONFIG.get(bstack11l1l_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧૻ"))[bstack1ll11111l1_opy_]
  if proxy and bstack1l1l1l1ll1_opy_() >= version.parse(bstack11l1l_opy_ (u"ࠬ࠺࠮࠲࠲࠱࠴ࠬૼ")):
    options.proxy(proxy)
  if options and bstack1l1l1l1ll1_opy_() >= version.parse(bstack11l1l_opy_ (u"࠭࠳࠯࠺࠱࠴ࠬ૽")):
    desired_capabilities = None
  if (
          not options and not desired_capabilities
  ) or (
          bstack1l1l1l1ll1_opy_() < version.parse(bstack11l1l_opy_ (u"ࠧ࠴࠰࠻࠲࠵࠭૾")) and not desired_capabilities
  ):
    desired_capabilities = {}
    desired_capabilities.update(bstack1l1l11l1l_opy_)
  logger.info(bstack11l1l11l1_opy_)
  bstack11l1l11ll_opy_.end(EVENTS.bstack11l1l111l_opy_.value, EVENTS.bstack11l1l111l_opy_.value + bstack11l1l_opy_ (u"ࠣ࠼ࡶࡸࡦࡸࡴࠣ૿"), EVENTS.bstack11l1l111l_opy_.value + bstack11l1l_opy_ (u"ࠤ࠽ࡩࡳࡪࠢ଀"), status=True, failure=None, test_name=bstack11l1ll1l_opy_)
  if bstack11l1l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡣࡵࡸ࡯ࡧ࡫࡯ࡩࠬଁ") in kwargs:
    del kwargs[bstack11l1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡤࡶࡲࡰࡨ࡬ࡰࡪ࠭ଂ")]
  try:
    if bstack1l1l1l1ll1_opy_() >= version.parse(bstack11l1l_opy_ (u"ࠬ࠺࠮࠲࠲࠱࠴ࠬଃ")):
      bstack1l1l11111_opy_(self, command_executor=command_executor,
                options=options, keep_alive=keep_alive, file_detector=file_detector, *args, **kwargs)
    elif bstack1l1l1l1ll1_opy_() >= version.parse(bstack11l1l_opy_ (u"࠭࠳࠯࠺࠱࠴ࠬ଄")):
      bstack1l1l11111_opy_(self, command_executor=command_executor,
                desired_capabilities=desired_capabilities, options=options,
                browser_profile=browser_profile, proxy=proxy,
                keep_alive=keep_alive, file_detector=file_detector)
    elif bstack1l1l1l1ll1_opy_() >= version.parse(bstack11l1l_opy_ (u"ࠧ࠳࠰࠸࠷࠳࠶ࠧଅ")):
      bstack1l1l11111_opy_(self, command_executor=command_executor,
                desired_capabilities=desired_capabilities,
                browser_profile=browser_profile, proxy=proxy,
                keep_alive=keep_alive, file_detector=file_detector)
    else:
      bstack1l1l11111_opy_(self, command_executor=command_executor,
                desired_capabilities=desired_capabilities,
                browser_profile=browser_profile, proxy=proxy,
                keep_alive=keep_alive)
  except Exception as bstack111ll1l1l1_opy_:
    logger.error(bstack1l111l1l1l_opy_.format(bstack11l1l_opy_ (u"ࠨࡄࡵࡳࡼࡹࡥࡳࡕࡷࡥࡨࡱࠧଆ"), str(bstack111ll1l1l1_opy_)))
    raise bstack111ll1l1l1_opy_
  if bstack11llll11l1_opy_.bstack11l11ll1_opy_(CONFIG, bstack1ll11111l1_opy_) and bstack11llll11l1_opy_.bstack11111ll11_opy_(self.caps, options, desired_capabilities):
    if CONFIG[bstack11l1l_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡑࡴࡲࡨࡺࡩࡴࡎࡣࡳࠫଇ")][bstack11l1l_opy_ (u"ࠪࡥࡵࡶ࡟ࡢࡷࡷࡳࡲࡧࡴࡦࠩଈ")] == True:
      threading.current_thread().appA11yPlatform = True
      if cli.accessibility is None or not cli.accessibility.is_enabled():
        bstack11llll11l1_opy_.set_capabilities(bstack1l1l11l1l_opy_, CONFIG)
  try:
    bstack11ll111l11_opy_ = bstack11l1l_opy_ (u"ࠫࠬଉ")
    if bstack1l1l1l1ll1_opy_() >= version.parse(bstack11l1l_opy_ (u"ࠬ࠺࠮࠱࠰࠳ࡦ࠶࠭ଊ")):
      if self.caps is not None:
        bstack11ll111l11_opy_ = self.caps.get(bstack11l1l_opy_ (u"ࠨ࡯ࡱࡶ࡬ࡱࡦࡲࡈࡶࡤࡘࡶࡱࠨଋ"))
    else:
      if self.capabilities is not None:
        bstack11ll111l11_opy_ = self.capabilities.get(bstack11l1l_opy_ (u"ࠢࡰࡲࡷ࡭ࡲࡧ࡬ࡉࡷࡥ࡙ࡷࡲࠢଌ"))
    if bstack11ll111l11_opy_:
      bstack11l1l1ll11_opy_(bstack11ll111l11_opy_)
      if bstack1l1l1l1ll1_opy_() <= version.parse(bstack11l1l_opy_ (u"ࠨ࠵࠱࠵࠸࠴࠰ࠨ଍")):
        self.command_executor._url = bstack11l1l_opy_ (u"ࠤ࡫ࡸࡹࡶ࠺࠰࠱ࠥ଎") + bstack1l1l1ll1_opy_ + bstack11l1l_opy_ (u"ࠥ࠾࠽࠶࠯ࡸࡦ࠲࡬ࡺࡨࠢଏ")
      else:
        self.command_executor._url = bstack11l1l_opy_ (u"ࠦ࡭ࡺࡴࡱࡵ࠽࠳࠴ࠨଐ") + bstack11ll111l11_opy_ + bstack11l1l_opy_ (u"ࠧ࠵ࡷࡥ࠱࡫ࡹࡧࠨ଑")
      logger.debug(bstack1lll11l1l_opy_.format(bstack11ll111l11_opy_))
    else:
      logger.debug(bstack11l1l11l_opy_.format(bstack11l1l_opy_ (u"ࠨࡏࡱࡶ࡬ࡱࡦࡲࠠࡉࡷࡥࠤࡳࡵࡴࠡࡨࡲࡹࡳࡪࠢ଒")))
  except Exception as e:
    logger.debug(bstack11l1l11l_opy_.format(e))
  if bstack11l1l_opy_ (u"ࠧࡳࡱࡥࡳࡹ࠭ଓ") in bstack11l1ll111l_opy_:
    bstack1l1l1lll1_opy_(bstack11ll1111ll_opy_, bstack11ll1111_opy_)
  bstack1ll1llll1l_opy_ = self.session_id
  if bstack11l1l_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࠨଔ") in bstack11l1ll111l_opy_ or bstack11l1l_opy_ (u"ࠩࡥࡩ࡭ࡧࡶࡦࠩକ") in bstack11l1ll111l_opy_ or bstack11l1l_opy_ (u"ࠪࡶࡴࡨ࡯ࡵࠩଖ") in bstack11l1ll111l_opy_:
    threading.current_thread().bstackSessionId = self.session_id
    threading.current_thread().bstackSessionDriver = self
    threading.current_thread().bstackTestErrorMessages = []
  bstack1l1ll1111l_opy_ = getattr(threading.current_thread(), bstack11l1l_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮ࡘࡪࡹࡴࡎࡧࡷࡥࠬଗ"), None)
  if bstack11l1l_opy_ (u"ࠬࡨࡥࡩࡣࡹࡩࠬଘ") in bstack11l1ll111l_opy_ or bstack11l1l_opy_ (u"࠭ࡲࡰࡤࡲࡸࠬଙ") in bstack11l1ll111l_opy_:
    bstack1ll1llll11_opy_.bstack1llll1llll_opy_(self)
  if bstack11l1l_opy_ (u"ࠧࡱࡻࡷࡩࡸࡺࠧଚ") in bstack11l1ll111l_opy_ and bstack1l1ll1111l_opy_ and bstack1l1ll1111l_opy_.get(bstack11l1l_opy_ (u"ࠨࡵࡷࡥࡹࡻࡳࠨଛ"), bstack11l1l_opy_ (u"ࠩࠪଜ")) == bstack11l1l_opy_ (u"ࠪࡴࡪࡴࡤࡪࡰࡪࠫଝ"):
    bstack1ll1llll11_opy_.bstack1llll1llll_opy_(self)
  with bstack1l1111ll_opy_:
    bstack1ll111111l_opy_.append(self)
  if bstack11l1l_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧଞ") in CONFIG and bstack11l1l_opy_ (u"ࠬࡹࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧࠪଟ") in CONFIG[bstack11l1l_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩଠ")][bstack1ll11111l1_opy_]:
    bstack11l1ll1l_opy_ = CONFIG[bstack11l1l_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪଡ")][bstack1ll11111l1_opy_][bstack11l1l_opy_ (u"ࠨࡵࡨࡷࡸ࡯࡯࡯ࡐࡤࡱࡪ࠭ଢ")]
  logger.debug(bstack1llllll11l_opy_.format(bstack1ll1llll1l_opy_))
try:
  try:
    import Browser
    from subprocess import Popen
    from browserstack_sdk.__init__ import bstack1l1l111l1_opy_
    def bstack1ll1l1ll11_opy_(self, args, bufsize=-1, executable=None,
              stdin=None, stdout=None, stderr=None,
              preexec_fn=None, close_fds=True,
              shell=False, cwd=None, env=None, universal_newlines=None,
              startupinfo=None, creationflags=0,
              restore_signals=True, start_new_session=False,
              pass_fds=(), *, user=None, group=None, extra_groups=None,
              encoding=None, errors=None, text=None, umask=-1, pipesize=-1):
      global CONFIG
      global bstack1ll1ll11l1_opy_
      if(bstack11l1l_opy_ (u"ࠤ࡬ࡲࡩ࡫ࡸ࠯࡬ࡶࠦଣ") in args[1]):
        with open(os.path.join(os.path.expanduser(bstack11l1l_opy_ (u"ࠪࢂࠬତ")), bstack11l1l_opy_ (u"ࠫ࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࠫଥ"), bstack11l1l_opy_ (u"ࠬ࠴ࡳࡦࡵࡶ࡭ࡴࡴࡩࡥࡵ࠱ࡸࡽࡺࠧଦ")), bstack11l1l_opy_ (u"࠭ࡷࠨଧ")) as fp:
          fp.write(bstack11l1l_opy_ (u"ࠢࠣନ"))
        if(not os.path.exists(os.path.join(os.path.dirname(args[1]), bstack11l1l_opy_ (u"ࠣ࡫ࡱࡨࡪࡾ࡟ࡣࡵࡷࡥࡨࡱ࠮࡫ࡵࠥ଩")))):
          with open(args[1], bstack11l1l_opy_ (u"ࠩࡵࠫପ")) as f:
            lines = f.readlines()
            index = next((i for i, line in enumerate(lines) if bstack11l1l_opy_ (u"ࠪࡥࡸࡿ࡮ࡤࠢࡩࡹࡳࡩࡴࡪࡱࡱࠤࡤࡴࡥࡸࡒࡤ࡫ࡪ࠮ࡣࡰࡰࡷࡩࡽࡺࠬࠡࡲࡤ࡫ࡪࠦ࠽ࠡࡸࡲ࡭ࡩࠦ࠰ࠪࠩଫ") in line), None)
            if index is not None:
                lines.insert(index+2, bstack1lllllll1l_opy_)
            if bstack11l1l_opy_ (u"ࠫࡹࡻࡲࡣࡱࡖࡧࡦࡲࡥࠨବ") in CONFIG and str(CONFIG[bstack11l1l_opy_ (u"ࠬࡺࡵࡳࡤࡲࡗࡨࡧ࡬ࡦࠩଭ")]).lower() != bstack11l1l_opy_ (u"࠭ࡦࡢ࡮ࡶࡩࠬମ"):
                bstack11ll1ll111_opy_ = bstack1l1l111l1_opy_()
                bstack1l11l1l1l1_opy_ = bstack11l1l_opy_ (u"ࠧࠨࠩࠍ࠳࠯ࠦ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࠣ࠮࠴ࠐࡣࡰࡰࡶࡸࠥࡨࡳࡵࡣࡦ࡯ࡤࡶࡡࡵࡪࠣࡁࠥࡶࡲࡰࡥࡨࡷࡸ࠴ࡡࡳࡩࡹ࡟ࡵࡸ࡯ࡤࡧࡶࡷ࠳ࡧࡲࡨࡸ࠱ࡰࡪࡴࡧࡵࡪࠣ࠱ࠥ࠹࡝࠼ࠌࡦࡳࡳࡹࡴࠡࡤࡶࡸࡦࡩ࡫ࡠࡥࡤࡴࡸࠦ࠽ࠡࡲࡵࡳࡨ࡫ࡳࡴ࠰ࡤࡶ࡬ࡼ࡛ࡱࡴࡲࡧࡪࡹࡳ࠯ࡣࡵ࡫ࡻ࠴࡬ࡦࡰࡪࡸ࡭ࠦ࠭ࠡ࠳ࡠ࠿ࠏࡩ࡯࡯ࡵࡷࠤࡵࡥࡩ࡯ࡦࡨࡼࠥࡃࠠࡱࡴࡲࡧࡪࡹࡳ࠯ࡣࡵ࡫ࡻࡡࡰࡳࡱࡦࡩࡸࡹ࠮ࡢࡴࡪࡺ࠳ࡲࡥ࡯ࡩࡷ࡬ࠥ࠳ࠠ࠳࡟࠾ࠎࡵࡸ࡯ࡤࡧࡶࡷ࠳ࡧࡲࡨࡸࠣࡁࠥࡶࡲࡰࡥࡨࡷࡸ࠴ࡡࡳࡩࡹ࠲ࡸࡲࡩࡤࡧࠫ࠴࠱ࠦࡰࡳࡱࡦࡩࡸࡹ࠮ࡢࡴࡪࡺ࠳ࡲࡥ࡯ࡩࡷ࡬ࠥ࠳ࠠ࠴ࠫ࠾ࠎࡨࡵ࡮ࡴࡶࠣ࡭ࡲࡶ࡯ࡳࡶࡢࡴࡱࡧࡹࡸࡴ࡬࡫࡭ࡺ࠴ࡠࡤࡶࡸࡦࡩ࡫ࠡ࠿ࠣࡶࡪࡷࡵࡪࡴࡨࠬࠧࡶ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵࠤࠬ࠿ࠏ࡯࡭ࡱࡱࡵࡸࡤࡶ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵ࠶ࡢࡦࡸࡺࡡࡤ࡭࠱ࡧ࡭ࡸ࡯࡮࡫ࡸࡱ࠳ࡲࡡࡶࡰࡦ࡬ࠥࡃࠠࡢࡵࡼࡲࡨࠦࠨ࡭ࡣࡸࡲࡨ࡮ࡏࡱࡶ࡬ࡳࡳࡹࠩࠡ࠿ࡁࠤࢀࢁࠊࠡࠢ࡯ࡩࡹࠦࡣࡢࡲࡶ࠿ࠏࠦࠠࡵࡴࡼࠤࢀࢁࠊࠡࠢࠣࠤࡨࡧࡰࡴࠢࡀࠤࡏ࡙ࡏࡏ࠰ࡳࡥࡷࡹࡥࠩࡤࡶࡸࡦࡩ࡫ࡠࡥࡤࡴࡸ࠯࠻ࠋࠢࠣࢁࢂࠦࡣࡢࡶࡦ࡬ࠥ࠮ࡥࡹࠫࠣࡿࢀࠐࠠࠡࠢࠣࡧࡴࡴࡳࡰ࡮ࡨ࠲ࡪࡸࡲࡰࡴࠫࠦࡋࡧࡩ࡭ࡧࡧࠤࡹࡵࠠࡱࡣࡵࡷࡪࠦࡣࡢࡲࡤࡦ࡮ࡲࡩࡵ࡫ࡨࡷ࠿ࠨࠬࠡࡧࡻ࠭ࡀࠐࠠࠡࡿࢀࠎࠥࠦࡲࡦࡶࡸࡶࡳࠦࡡࡸࡣ࡬ࡸࠥ࡯࡭ࡱࡱࡵࡸࡤࡶ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵ࠶ࡢࡦࡸࡺࡡࡤ࡭࠱ࡧ࡭ࡸ࡯࡮࡫ࡸࡱ࠳ࡩ࡯࡯ࡰࡨࡧࡹ࠮ࡻࡼࠌࠣࠤࠥࠦࡷࡴࡇࡱࡨࡵࡵࡩ࡯ࡶ࠽ࠤࠬࢁࡣࡥࡲࡘࡶࡱࢃࠧࠡ࠭ࠣࡩࡳࡩ࡯ࡥࡧࡘࡖࡎࡉ࡯࡮ࡲࡲࡲࡪࡴࡴࠩࡌࡖࡓࡓ࠴ࡳࡵࡴ࡬ࡲ࡬࡯ࡦࡺࠪࡦࡥࡵࡹࠩࠪ࠮ࠍࠤࠥࠦࠠ࠯࠰࠱ࡰࡦࡻ࡮ࡤࡪࡒࡴࡹ࡯࡯࡯ࡵࠍࠤࠥࢃࡽࠪ࠽ࠍࢁࢂࡁࠊ࠰ࠬࠣࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃࠠࠫ࠱ࠍࠫࠬ࠭ଯ").format(bstack11ll1ll111_opy_=bstack11ll1ll111_opy_)
            lines.insert(1, bstack1l11l1l1l1_opy_)
            f.seek(0)
            with open(os.path.join(os.path.dirname(args[1]), bstack11l1l_opy_ (u"ࠣ࡫ࡱࡨࡪࡾ࡟ࡣࡵࡷࡥࡨࡱ࠮࡫ࡵࠥର")), bstack11l1l_opy_ (u"ࠩࡺࠫ଱")) as bstack1lll1llll_opy_:
              bstack1lll1llll_opy_.writelines(lines)
        CONFIG[bstack11l1l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡕࡇࡏࠬଲ")] = str(bstack11l1ll111l_opy_) + str(__version__)
        bstack1ll1lll11l_opy_ = os.environ[bstack11l1l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡉࡗࡅࡣ࡚࡛ࡉࡅࠩଳ")]
        bstack11l1111ll1_opy_ = bstack1ll11l1l1_opy_.bstack1llll1l1_opy_(CONFIG, bstack11l1ll111l_opy_)
        CONFIG[bstack11l1l_opy_ (u"ࠬࡺࡥࡴࡶ࡫ࡹࡧࡈࡵࡪ࡮ࡧ࡙ࡺ࡯ࡤࠨ଴")] = bstack1ll1lll11l_opy_
        CONFIG[bstack11l1l_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡕࡸ࡯ࡥࡷࡦࡸࡒࡧࡰࠨଵ")] = bstack11l1111ll1_opy_
        bstack1ll11111l1_opy_ = 0 if bstack11ll1111ll_opy_ < 0 else bstack11ll1111ll_opy_
        try:
          if bstack111ll1l11_opy_ is True:
            bstack1ll11111l1_opy_ = int(multiprocessing.current_process().name)
          elif bstack1l1llll1ll_opy_ is True:
            bstack1ll11111l1_opy_ = int(threading.current_thread().name)
        except:
          bstack1ll11111l1_opy_ = 0
        CONFIG[bstack11l1l_opy_ (u"ࠢࡶࡵࡨ࡛࠸ࡉࠢଶ")] = False
        CONFIG[bstack11l1l_opy_ (u"ࠣ࡫ࡶࡔࡱࡧࡹࡸࡴ࡬࡫࡭ࡺࠢଷ")] = True
        bstack1l1l11l1l_opy_ = bstack111lll11l1_opy_(CONFIG, bstack1ll11111l1_opy_)
        logger.debug(bstack11lll1111_opy_.format(str(bstack1l1l11l1l_opy_)))
        if CONFIG.get(bstack11l1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡍࡱࡦࡥࡱ࠭ସ")):
          bstack1ll1l11l1l_opy_(bstack1l1l11l1l_opy_)
        if bstack11l1l_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ହ") in CONFIG and bstack11l1l_opy_ (u"ࠫࡸ࡫ࡳࡴ࡫ࡲࡲࡓࡧ࡭ࡦࠩ଺") in CONFIG[bstack11l1l_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨ଻")][bstack1ll11111l1_opy_]:
          bstack11l1ll1l_opy_ = CONFIG[bstack11l1l_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴ଼ࠩ")][bstack1ll11111l1_opy_][bstack11l1l_opy_ (u"ࠧࡴࡧࡶࡷ࡮ࡵ࡮ࡏࡣࡰࡩࠬଽ")]
        args.append(os.path.join(os.path.expanduser(bstack11l1l_opy_ (u"ࠨࢀࠪା")), bstack11l1l_opy_ (u"ࠩ࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࠩି"), bstack11l1l_opy_ (u"ࠪ࠲ࡸ࡫ࡳࡴ࡫ࡲࡲ࡮ࡪࡳ࠯ࡶࡻࡸࠬୀ")))
        args.append(str(threading.get_ident()))
        args.append(json.dumps(bstack1l1l11l1l_opy_))
        args[1] = os.path.join(os.path.dirname(args[1]), bstack11l1l_opy_ (u"ࠦ࡮ࡴࡤࡦࡺࡢࡦࡸࡺࡡࡤ࡭࠱࡮ࡸࠨୁ"))
      bstack1ll1ll11l1_opy_ = True
      return bstack1l1111ll1l_opy_(self, args, bufsize=bufsize, executable=executable,
                    stdin=stdin, stdout=stdout, stderr=stderr,
                    preexec_fn=preexec_fn, close_fds=close_fds,
                    shell=shell, cwd=cwd, env=env, universal_newlines=universal_newlines,
                    startupinfo=startupinfo, creationflags=creationflags,
                    restore_signals=restore_signals, start_new_session=start_new_session,
                    pass_fds=pass_fds, user=user, group=group, extra_groups=extra_groups,
                    encoding=encoding, errors=errors, text=text, umask=umask, pipesize=pipesize)
  except Exception as e:
    pass
  import playwright._impl._api_structures
  import playwright._impl._helper
  def bstack1lll111l1l_opy_(self,
        executablePath = None,
        channel = None,
        args = None,
        ignoreDefaultArgs = None,
        handleSIGINT = None,
        handleSIGTERM = None,
        handleSIGHUP = None,
        timeout = None,
        env = None,
        headless = None,
        devtools = None,
        proxy = None,
        downloadsPath = None,
        slowMo = None,
        tracesDir = None,
        chromiumSandbox = None,
        firefoxUserPrefs = None
        ):
    global CONFIG
    global bstack11ll1111ll_opy_
    global bstack11l1ll1l_opy_
    global bstack111ll1l11_opy_
    global bstack1l1llll1ll_opy_
    global bstack11l1ll111l_opy_
    CONFIG[bstack11l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡗࡉࡑࠧୂ")] = str(bstack11l1ll111l_opy_) + str(__version__)
    bstack1ll1lll11l_opy_ = os.environ[bstack11l1l_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡕࡖࡋࡇࠫୃ")]
    bstack11l1111ll1_opy_ = bstack1ll11l1l1_opy_.bstack1llll1l1_opy_(CONFIG, bstack11l1ll111l_opy_)
    CONFIG[bstack11l1l_opy_ (u"ࠧࡵࡧࡶࡸ࡭ࡻࡢࡃࡷ࡬ࡰࡩ࡛ࡵࡪࡦࠪୄ")] = bstack1ll1lll11l_opy_
    CONFIG[bstack11l1l_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡐࡳࡱࡧࡹࡨࡺࡍࡢࡲࠪ୅")] = bstack11l1111ll1_opy_
    bstack1ll11111l1_opy_ = 0 if bstack11ll1111ll_opy_ < 0 else bstack11ll1111ll_opy_
    try:
      if bstack111ll1l11_opy_ is True:
        bstack1ll11111l1_opy_ = int(multiprocessing.current_process().name)
      elif bstack1l1llll1ll_opy_ is True:
        bstack1ll11111l1_opy_ = int(threading.current_thread().name)
    except:
      bstack1ll11111l1_opy_ = 0
    CONFIG[bstack11l1l_opy_ (u"ࠤ࡬ࡷࡕࡲࡡࡺࡹࡵ࡭࡬࡮ࡴࠣ୆")] = True
    bstack1l1l11l1l_opy_ = bstack111lll11l1_opy_(CONFIG, bstack1ll11111l1_opy_)
    logger.debug(bstack11lll1111_opy_.format(str(bstack1l1l11l1l_opy_)))
    if CONFIG.get(bstack11l1l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡎࡲࡧࡦࡲࠧେ")):
      bstack1ll1l11l1l_opy_(bstack1l1l11l1l_opy_)
    if bstack11l1l_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧୈ") in CONFIG and bstack11l1l_opy_ (u"ࠬࡹࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧࠪ୉") in CONFIG[bstack11l1l_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩ୊")][bstack1ll11111l1_opy_]:
      bstack11l1ll1l_opy_ = CONFIG[bstack11l1l_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪୋ")][bstack1ll11111l1_opy_][bstack11l1l_opy_ (u"ࠨࡵࡨࡷࡸ࡯࡯࡯ࡐࡤࡱࡪ࠭ୌ")]
    import urllib
    import json
    if bstack11l1l_opy_ (u"ࠩࡷࡹࡷࡨ࡯ࡔࡥࡤࡰࡪ୍࠭") in CONFIG and str(CONFIG[bstack11l1l_opy_ (u"ࠪࡸࡺࡸࡢࡰࡕࡦࡥࡱ࡫ࠧ୎")]).lower() != bstack11l1l_opy_ (u"ࠫ࡫ࡧ࡬ࡴࡧࠪ୏"):
        bstack1lll11ll_opy_ = bstack1l1l111l1_opy_()
        bstack11ll1ll111_opy_ = bstack1lll11ll_opy_ + urllib.parse.quote(json.dumps(bstack1l1l11l1l_opy_))
    else:
        bstack11ll1ll111_opy_ = bstack11l1l_opy_ (u"ࠬࡽࡳࡴ࠼࠲࠳ࡨࡪࡰ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡤࡱࡰ࠳ࡵࡲࡡࡺࡹࡵ࡭࡬࡮ࡴࡀࡥࡤࡴࡸࡃࠧ୐") + urllib.parse.quote(json.dumps(bstack1l1l11l1l_opy_))
    browser = self.connect(bstack11ll1ll111_opy_)
    return browser
except Exception as e:
    pass
def bstack11l11lll1l_opy_():
    global bstack1ll1ll11l1_opy_
    global bstack11l1ll111l_opy_
    global CONFIG
    try:
        from playwright._impl._browser_type import BrowserType
        from bstack_utils.helper import bstack1l1l1l1l_opy_
        global bstack1l1ll11111_opy_
        if not bstack11ll1l1lll_opy_:
          global bstack11l111ll1_opy_
          if not bstack11l111ll1_opy_:
            from bstack_utils.helper import bstack1lll1111_opy_, bstack1l111ll1l_opy_, bstack11ll11l1l1_opy_
            bstack11l111ll1_opy_ = bstack1lll1111_opy_()
            bstack1l111ll1l_opy_(bstack11l1ll111l_opy_)
            bstack11l1111ll1_opy_ = bstack1ll11l1l1_opy_.bstack1llll1l1_opy_(CONFIG, bstack11l1ll111l_opy_)
            bstack1l1ll11111_opy_.bstack1ll1111ll1_opy_(bstack11l1l_opy_ (u"ࠨࡐࡍࡃ࡜࡛ࡗࡏࡇࡉࡖࡢࡔࡗࡕࡄࡖࡅࡗࡣࡒࡇࡐࠣ୑"), bstack11l1111ll1_opy_)
          BrowserType.connect = bstack1l1l1l1l_opy_
          return
        BrowserType.launch = bstack1lll111l1l_opy_
        bstack1ll1ll11l1_opy_ = True
    except Exception as e:
        pass
    try:
      import Browser
      from subprocess import Popen
      Popen.__init__ = bstack1ll1l1ll11_opy_
      bstack1ll1ll11l1_opy_ = True
    except Exception as e:
      pass
def bstack1ll1lll11_opy_(context, bstack11l1111111_opy_):
  try:
    context.page.evaluate(bstack11l1l_opy_ (u"ࠢࡠࠢࡀࡂࠥࢁࡽࠣ୒"), bstack11l1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࡿࠧࡧࡣࡵ࡫ࡲࡲࠧࡀࠠࠣࡵࡨࡸࡘ࡫ࡳࡴ࡫ࡲࡲࡓࡧ࡭ࡦࠤ࠯ࠤࠧࡧࡲࡨࡷࡰࡩࡳࡺࡳࠣ࠼ࠣࡿࠧࡴࡡ࡮ࡧࠥ࠾ࠬ୓")+ json.dumps(bstack11l1111111_opy_) + bstack11l1l_opy_ (u"ࠤࢀࢁࠧ୔"))
  except Exception as e:
    logger.debug(bstack11l1l_opy_ (u"ࠥࡩࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡩ࡯ࠢࡳࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹࠦࡳࡦࡵࡶ࡭ࡴࡴࠠ࡯ࡣࡰࡩࠥࢁࡽ࠻ࠢࡾࢁࠧ୕").format(str(e), traceback.format_exc()))
def bstack111llll1l1_opy_(context, message, level):
  try:
    context.page.evaluate(bstack11l1l_opy_ (u"ࠦࡤࠦ࠽࠿ࠢࡾࢁࠧୖ"), bstack11l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࡼࠤࡤࡧࡹ࡯࡯࡯ࠤ࠽ࠤࠧࡧ࡮࡯ࡱࡷࡥࡹ࡫ࠢ࠭ࠢࠥࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸࠨ࠺ࠡࡽࠥࡨࡦࡺࡡࠣ࠼ࠪୗ") + json.dumps(message) + bstack11l1l_opy_ (u"࠭ࠬࠣ࡮ࡨࡺࡪࡲࠢ࠻ࠩ୘") + json.dumps(level) + bstack11l1l_opy_ (u"ࠧࡾࡿࠪ୙"))
  except Exception as e:
    logger.debug(bstack11l1l_opy_ (u"ࠣࡧࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡱ࡮ࡤࡽࡼࡸࡩࡨࡪࡷࠤࡦࡴ࡮ࡰࡶࡤࡸ࡮ࡵ࡮ࠡࡽࢀ࠾ࠥࢁࡽࠣ୚").format(str(e), traceback.format_exc()))
@measure(event_name=EVENTS.bstack1llllll11_opy_, stage=STAGE.bstack1lll1l11l_opy_, bstack1l1l1llll_opy_=bstack11l1ll1l_opy_)
def bstack1ll11l1ll1_opy_(self, url):
  global bstack1l11l1ll11_opy_
  try:
    bstack11ll1lll_opy_(url)
  except Exception as err:
    logger.debug(bstack11llll111l_opy_.format(str(err)))
  try:
    bstack1l11l1ll11_opy_(self, url)
  except Exception as e:
    try:
      bstack111ll1l1l_opy_ = str(e)
      if any(err_msg in bstack111ll1l1l_opy_ for err_msg in bstack11lll1ll1l_opy_):
        bstack11ll1lll_opy_(url, True)
    except Exception as err:
      logger.debug(bstack11llll111l_opy_.format(str(err)))
    raise e
def bstack1llll1111_opy_(self):
  global bstack1l11l11111_opy_
  bstack1l11l11111_opy_ = self
  return
def bstack1lll1llll1_opy_(self):
  global bstack11l1111l1l_opy_
  bstack11l1111l1l_opy_ = self
  return
def bstack111ll1ll_opy_(test_name, bstack1ll11l1111_opy_):
  global CONFIG
  if percy.bstack1llll111l_opy_() == bstack11l1l_opy_ (u"ࠤࡷࡶࡺ࡫ࠢ୛"):
    bstack1ll1l1l1ll_opy_ = os.path.relpath(bstack1ll11l1111_opy_, start=os.getcwd())
    suite_name, _ = os.path.splitext(bstack1ll1l1l1ll_opy_)
    bstack1l1l1llll_opy_ = suite_name + bstack11l1l_opy_ (u"ࠥ࠱ࠧଡ଼") + test_name
    threading.current_thread().percySessionName = bstack1l1l1llll_opy_
def bstack1l11l1l11_opy_(self, test, *args, **kwargs):
  global bstack1l1l1lll11_opy_
  test_name = None
  bstack1ll11l1111_opy_ = None
  if test:
    test_name = str(test.name)
    bstack1ll11l1111_opy_ = str(test.source)
  bstack111ll1ll_opy_(test_name, bstack1ll11l1111_opy_)
  bstack1l1l1lll11_opy_(self, test, *args, **kwargs)
@measure(event_name=EVENTS.bstack1l1ll11ll_opy_, stage=STAGE.bstack1lll1l11l_opy_, bstack1l1l1llll_opy_=bstack11l1ll1l_opy_)
def bstack111lll111l_opy_(driver, bstack1l1l1llll_opy_):
  if not bstack1lllllll1_opy_ and bstack1l1l1llll_opy_:
      bstack1ll111lll1_opy_ = {
          bstack11l1l_opy_ (u"ࠫࡦࡩࡴࡪࡱࡱࠫଢ଼"): bstack11l1l_opy_ (u"ࠬࡹࡥࡵࡕࡨࡷࡸ࡯࡯࡯ࡐࡤࡱࡪ࠭୞"),
          bstack11l1l_opy_ (u"࠭ࡡࡳࡩࡸࡱࡪࡴࡴࡴࠩୟ"): {
              bstack11l1l_opy_ (u"ࠧ࡯ࡣࡰࡩࠬୠ"): bstack1l1l1llll_opy_
          }
      }
      bstack11lllll1ll_opy_ = bstack11l1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࡿࢂ࠭ୡ").format(json.dumps(bstack1ll111lll1_opy_))
      driver.execute_script(bstack11lllll1ll_opy_)
  if bstack111111l1l_opy_:
      bstack1ll1111ll_opy_ = {
          bstack11l1l_opy_ (u"ࠩࡤࡧࡹ࡯࡯࡯ࠩୢ"): bstack11l1l_opy_ (u"ࠪࡥࡳࡴ࡯ࡵࡣࡷࡩࠬୣ"),
          bstack11l1l_opy_ (u"ࠫࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠧ୤"): {
              bstack11l1l_opy_ (u"ࠬࡪࡡࡵࡣࠪ୥"): bstack1l1l1llll_opy_ + bstack11l1l_opy_ (u"࠭ࠠࡱࡣࡶࡷࡪࡪࠡࠨ୦"),
              bstack11l1l_opy_ (u"ࠧ࡭ࡧࡹࡩࡱ࠭୧"): bstack11l1l_opy_ (u"ࠨ࡫ࡱࡪࡴ࠭୨")
          }
      }
      if bstack111111l1l_opy_.status == bstack11l1l_opy_ (u"ࠩࡓࡅࡘ࡙ࠧ୩"):
          bstack1ll11lll1_opy_ = bstack11l1l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡨࡼࡪࡩࡵࡵࡱࡵ࠾ࠥࢁࡽࠨ୪").format(json.dumps(bstack1ll1111ll_opy_))
          driver.execute_script(bstack1ll11lll1_opy_)
          bstack111lllll1l_opy_(driver, bstack11l1l_opy_ (u"ࠫࡵࡧࡳࡴࡧࡧࠫ୫"))
      elif bstack111111l1l_opy_.status == bstack11l1l_opy_ (u"ࠬࡌࡁࡊࡎࠪ୬"):
          reason = bstack11l1l_opy_ (u"ࠨࠢ୭")
          bstack1ll111ll_opy_ = bstack1l1l1llll_opy_ + bstack11l1l_opy_ (u"ࠧࠡࡨࡤ࡭ࡱ࡫ࡤࠨ୮")
          if bstack111111l1l_opy_.message:
              reason = str(bstack111111l1l_opy_.message)
              bstack1ll111ll_opy_ = bstack1ll111ll_opy_ + bstack11l1l_opy_ (u"ࠨࠢࡺ࡭ࡹ࡮ࠠࡦࡴࡵࡳࡷࡀࠠࠨ୯") + reason
          bstack1ll1111ll_opy_[bstack11l1l_opy_ (u"ࠩࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠬ୰")] = {
              bstack11l1l_opy_ (u"ࠪࡰࡪࡼࡥ࡭ࠩୱ"): bstack11l1l_opy_ (u"ࠫࡪࡸࡲࡰࡴࠪ୲"),
              bstack11l1l_opy_ (u"ࠬࡪࡡࡵࡣࠪ୳"): bstack1ll111ll_opy_
          }
          bstack1ll11lll1_opy_ = bstack11l1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤ࡫ࡸࡦࡥࡸࡸࡴࡸ࠺ࠡࡽࢀࠫ୴").format(json.dumps(bstack1ll1111ll_opy_))
          driver.execute_script(bstack1ll11lll1_opy_)
          bstack111lllll1l_opy_(driver, bstack11l1l_opy_ (u"ࠧࡧࡣ࡬ࡰࡪࡪࠧ୵"), reason)
          bstack1l1ll1ll_opy_(reason, str(bstack111111l1l_opy_), str(bstack11ll1111ll_opy_), logger)
@measure(event_name=EVENTS.bstack1llllllll1_opy_, stage=STAGE.bstack1lll1l11l_opy_, bstack1l1l1llll_opy_=bstack11l1ll1l_opy_)
def bstack1lllll11_opy_(driver, test):
  if percy.bstack1llll111l_opy_() == bstack11l1l_opy_ (u"ࠣࡶࡵࡹࡪࠨ୶") and percy.bstack111llllll_opy_() == bstack11l1l_opy_ (u"ࠤࡷࡩࡸࡺࡣࡢࡵࡨࠦ୷"):
      bstack11l1ll1lll_opy_ = bstack11lll11l_opy_(threading.current_thread(), bstack11l1l_opy_ (u"ࠪࡴࡪࡸࡣࡺࡕࡨࡷࡸ࡯࡯࡯ࡐࡤࡱࡪ࠭୸"), None)
      bstack1l111l1111_opy_(driver, bstack11l1ll1lll_opy_, test)
  if (bstack11lll11l_opy_(threading.current_thread(), bstack11l1l_opy_ (u"ࠫ࡮ࡹࡁ࠲࠳ࡼࡘࡪࡹࡴࠨ୹"), None) and
      bstack11lll11l_opy_(threading.current_thread(), bstack11l1l_opy_ (u"ࠬࡧ࠱࠲ࡻࡓࡰࡦࡺࡦࡰࡴࡰࠫ୺"), None)) or (
      bstack11lll11l_opy_(threading.current_thread(), bstack11l1l_opy_ (u"࠭ࡩࡴࡃࡳࡴࡆ࠷࠱ࡺࡖࡨࡷࡹ࠭୻"), None) and
      bstack11lll11l_opy_(threading.current_thread(), bstack11l1l_opy_ (u"ࠧࡢࡲࡳࡅ࠶࠷ࡹࡑ࡮ࡤࡸ࡫ࡵࡲ࡮ࠩ୼"), None)):
      logger.info(bstack11l1l_opy_ (u"ࠣࡃࡸࡸࡴࡳࡡࡵࡧࠣࡸࡪࡹࡴࠡࡥࡤࡷࡪࠦࡥࡹࡧࡦࡹࡹ࡯࡯࡯ࠢ࡫ࡥࡸࠦࡥ࡯ࡦࡨࡨ࠳ࠦࡐࡳࡱࡦࡩࡸࡹࡩ࡯ࡩࠣࡪࡴࡸࠠࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡵࡧࡶࡸ࡮ࡴࡧࠡ࡫ࡶࠤࡺࡴࡤࡦࡴࡺࡥࡾ࠴ࠠࠣ୽"))
      bstack11llll11l1_opy_.bstack111ll1l1_opy_(driver, name=test.name, path=test.source)
def bstack1l11l1l11l_opy_(test, bstack1l1l1llll_opy_):
    try:
      bstack11ll1l1ll1_opy_ = datetime.datetime.now()
      data = {}
      if test:
        data[bstack11l1l_opy_ (u"ࠩࡱࡥࡲ࡫ࠧ୾")] = bstack1l1l1llll_opy_
      if bstack111111l1l_opy_:
        if bstack111111l1l_opy_.status == bstack11l1l_opy_ (u"ࠪࡔࡆ࡙ࡓࠨ୿"):
          data[bstack11l1l_opy_ (u"ࠫࡸࡺࡡࡵࡷࡶࠫ஀")] = bstack11l1l_opy_ (u"ࠬࡶࡡࡴࡵࡨࡨࠬ஁")
        elif bstack111111l1l_opy_.status == bstack11l1l_opy_ (u"࠭ࡆࡂࡋࡏࠫஂ"):
          data[bstack11l1l_opy_ (u"ࠧࡴࡶࡤࡸࡺࡹࠧஃ")] = bstack11l1l_opy_ (u"ࠨࡨࡤ࡭ࡱ࡫ࡤࠨ஄")
          if bstack111111l1l_opy_.message:
            data[bstack11l1l_opy_ (u"ࠩࡵࡩࡦࡹ࡯࡯ࠩஅ")] = str(bstack111111l1l_opy_.message)
      user = CONFIG[bstack11l1l_opy_ (u"ࠪࡹࡸ࡫ࡲࡏࡣࡰࡩࠬஆ")]
      key = CONFIG[bstack11l1l_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶࡏࡪࡿࠧஇ")]
      host = bstack1l1l1ll1l_opy_(cli.config, [bstack11l1l_opy_ (u"ࠧࡧࡰࡪࡵࠥஈ"), bstack11l1l_opy_ (u"ࠨࡡࡶࡶࡲࡱࡦࡺࡥࠣஉ"), bstack11l1l_opy_ (u"ࠢࡢࡲ࡬ࠦஊ")], bstack11l1l_opy_ (u"ࠣࡪࡷࡸࡵࡹ࠺࠰࠱ࡤࡴ࡮࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡩ࡯࡮ࠤ஋"))
      url = bstack11l1l_opy_ (u"ࠩࡾࢁ࠴ࡧࡵࡵࡱࡰࡥࡹ࡫࠯ࡴࡧࡶࡷ࡮ࡵ࡮ࡴ࠱ࡾࢁ࠳ࡰࡳࡰࡰࠪ஌").format(host, bstack1ll1llll1l_opy_)
      headers = {
        bstack11l1l_opy_ (u"ࠪࡇࡴࡴࡴࡦࡰࡷ࠱ࡹࡿࡰࡦࠩ஍"): bstack11l1l_opy_ (u"ࠫࡦࡶࡰ࡭࡫ࡦࡥࡹ࡯࡯࡯࠱࡭ࡷࡴࡴࠧஎ"),
      }
      if bool(data):
        requests.put(url, json=data, headers=headers, auth=(user, key))
        cli.bstack11lll111_opy_(bstack11l1l_opy_ (u"ࠧ࡮ࡴࡵࡲ࠽ࡹࡵࡪࡡࡵࡧࡢࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡶࡸࡦࡺࡵࡴࠤஏ"), datetime.datetime.now() - bstack11ll1l1ll1_opy_)
    except Exception as e:
      logger.error(bstack11l11l111_opy_.format(str(e)))
def bstack11l111111_opy_(test, bstack1l1l1llll_opy_):
  global CONFIG
  global bstack11l1111l1l_opy_
  global bstack1l11l11111_opy_
  global bstack1ll1llll1l_opy_
  global bstack111111l1l_opy_
  global bstack11l1ll1l_opy_
  global bstack1ll11ll1l1_opy_
  global bstack11l1l111ll_opy_
  global bstack1111l11l_opy_
  global bstack1l1l11l1ll_opy_
  global bstack1ll111111l_opy_
  global bstack11ll11l111_opy_
  global bstack1l1111llll_opy_
  try:
    if not bstack1ll1llll1l_opy_:
      with bstack1l1111llll_opy_:
        bstack1lll1lllll_opy_ = os.path.join(os.path.expanduser(bstack11l1l_opy_ (u"࠭ࡾࠨஐ")), bstack11l1l_opy_ (u"ࠧ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠧ஑"), bstack11l1l_opy_ (u"ࠨ࠰ࡶࡩࡸࡹࡩࡰࡰ࡬ࡨࡸ࠴ࡴࡹࡶࠪஒ"))
        if os.path.exists(bstack1lll1lllll_opy_):
          with open(bstack1lll1lllll_opy_, bstack11l1l_opy_ (u"ࠩࡵࠫஓ")) as f:
            content = f.read().strip()
            if content:
              bstack1l11lllll_opy_ = json.loads(bstack11l1l_opy_ (u"ࠥࡿࠧஔ") + content + bstack11l1l_opy_ (u"ࠫࠧࡾࠢ࠻ࠢࠥࡽࠧ࠭க") + bstack11l1l_opy_ (u"ࠧࢃࠢ஖"))
              bstack1ll1llll1l_opy_ = bstack1l11lllll_opy_.get(str(threading.get_ident()))
  except Exception as e:
    logger.debug(bstack11l1l_opy_ (u"࠭ࡅࡳࡴࡲࡶࠥࡸࡥࡢࡦ࡬ࡲ࡬ࠦࡳࡦࡵࡶ࡭ࡴࡴࠠࡊࡆࡶࠤ࡫࡯࡬ࡦ࠼ࠣࠫ஗") + str(e))
  if bstack1ll111111l_opy_:
    with bstack1l1111ll_opy_:
      bstack1lll1ll1ll_opy_ = bstack1ll111111l_opy_.copy()
    for driver in bstack1lll1ll1ll_opy_:
      if bstack1ll1llll1l_opy_ == driver.session_id:
        if test:
          bstack1lllll11_opy_(driver, test)
        bstack111lll111l_opy_(driver, bstack1l1l1llll_opy_)
  elif bstack1ll1llll1l_opy_:
    bstack1l11l1l11l_opy_(test, bstack1l1l1llll_opy_)
  if bstack11l1111l1l_opy_:
    bstack11l1l111ll_opy_(bstack11l1111l1l_opy_)
  if bstack1l11l11111_opy_:
    bstack1111l11l_opy_(bstack1l11l11111_opy_)
  if bstack1lll111l_opy_:
    bstack1l1l11l1ll_opy_()
def bstack11ll1llll_opy_(self, test, *args, **kwargs):
  bstack1l1l1llll_opy_ = None
  if test:
    bstack1l1l1llll_opy_ = str(test.name)
  bstack11l111111_opy_(test, bstack1l1l1llll_opy_)
  bstack1ll11ll1l1_opy_(self, test, *args, **kwargs)
def bstack1lll1l11_opy_(self, parent, test, skip_on_failure=None, rpa=False):
  global bstack1111l111_opy_
  global CONFIG
  global bstack1ll111111l_opy_
  global bstack1ll1llll1l_opy_
  global bstack1l1111llll_opy_
  bstack1l1l1l11l1_opy_ = None
  try:
    if bstack11lll11l_opy_(threading.current_thread(), bstack11l1l_opy_ (u"ࠧࡢ࠳࠴ࡽࡕࡲࡡࡵࡨࡲࡶࡲ࠭஘"), None) or bstack11lll11l_opy_(threading.current_thread(), bstack11l1l_opy_ (u"ࠨࡣࡳࡴࡆ࠷࠱ࡺࡒ࡯ࡥࡹ࡬࡯ࡳ࡯ࠪங"), None):
      try:
        if not bstack1ll1llll1l_opy_:
          bstack1lll1lllll_opy_ = os.path.join(os.path.expanduser(bstack11l1l_opy_ (u"ࠩࢁࠫச")), bstack11l1l_opy_ (u"ࠪ࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࠪ஛"), bstack11l1l_opy_ (u"ࠫ࠳ࡹࡥࡴࡵ࡬ࡳࡳ࡯ࡤࡴ࠰ࡷࡼࡹ࠭ஜ"))
          with bstack1l1111llll_opy_:
            if os.path.exists(bstack1lll1lllll_opy_):
              with open(bstack1lll1lllll_opy_, bstack11l1l_opy_ (u"ࠬࡸࠧ஝")) as f:
                content = f.read().strip()
                if content:
                  bstack1l11lllll_opy_ = json.loads(bstack11l1l_opy_ (u"ࠨࡻࠣஞ") + content + bstack11l1l_opy_ (u"ࠧࠣࡺࠥ࠾ࠥࠨࡹࠣࠩட") + bstack11l1l_opy_ (u"ࠣࡿࠥ஠"))
                  bstack1ll1llll1l_opy_ = bstack1l11lllll_opy_.get(str(threading.get_ident()))
      except Exception as e:
        logger.debug(bstack11l1l_opy_ (u"ࠩࡈࡶࡷࡵࡲࠡࡴࡨࡥࡩ࡯࡮ࡨࠢࡶࡩࡸࡹࡩࡰࡰࠣࡍࡉࡹࠠࡧ࡫࡯ࡩࠥ࡯࡮ࠡࡶࡨࡷࡹࠦࡳࡵࡣࡷࡹࡸࡀࠠࠨ஡") + str(e))
      if bstack1ll111111l_opy_:
        with bstack1l1111ll_opy_:
          bstack1lll1ll1ll_opy_ = bstack1ll111111l_opy_.copy()
        for driver in bstack1lll1ll1ll_opy_:
          if bstack1ll1llll1l_opy_ == driver.session_id:
            bstack1l1l1l11l1_opy_ = driver
    bstack11l11ll1l_opy_ = bstack11llll11l1_opy_.bstack1l11l11l_opy_(test.tags)
    if bstack1l1l1l11l1_opy_:
      threading.current_thread().isA11yTest = bstack11llll11l1_opy_.bstack1lll111ll1_opy_(bstack1l1l1l11l1_opy_, bstack11l11ll1l_opy_)
      threading.current_thread().isAppA11yTest = bstack11llll11l1_opy_.bstack1lll111ll1_opy_(bstack1l1l1l11l1_opy_, bstack11l11ll1l_opy_)
    else:
      threading.current_thread().isA11yTest = bstack11l11ll1l_opy_
      threading.current_thread().isAppA11yTest = bstack11l11ll1l_opy_
  except:
    pass
  bstack1111l111_opy_(self, parent, test, skip_on_failure=skip_on_failure, rpa=rpa)
  global bstack111111l1l_opy_
  try:
    bstack111111l1l_opy_ = self._test
  except:
    bstack111111l1l_opy_ = self.test
def bstack1lll1ll11_opy_():
  global bstack11111lll_opy_
  try:
    if os.path.exists(bstack11111lll_opy_):
      os.remove(bstack11111lll_opy_)
  except Exception as e:
    logger.debug(bstack11l1l_opy_ (u"ࠪࡉࡷࡸ࡯ࡳࠢ࡬ࡲࠥࡪࡥ࡭ࡧࡷ࡭ࡳ࡭ࠠࡳࡱࡥࡳࡹࠦࡲࡦࡲࡲࡶࡹࠦࡦࡪ࡮ࡨ࠾ࠥ࠭஢") + str(e))
def bstack1l11l11l1_opy_():
  global bstack11111lll_opy_
  bstack1l1l111ll1_opy_ = {}
  lock_file = bstack11111lll_opy_ + bstack11l1l_opy_ (u"ࠫ࠳ࡲ࡯ࡤ࡭ࠪண")
  try:
    from filelock import FileLock
  except ImportError:
    logger.debug(bstack11l1l_opy_ (u"ࠬ࡬ࡩ࡭ࡧ࡯ࡳࡨࡱࠠ࡯ࡱࡷࠤࡦࡼࡡࡪ࡮ࡤࡦࡱ࡫ࠬࠡࡷࡶ࡭ࡳ࡭ࠠࡣࡣࡶ࡭ࡨࠦࡦࡪ࡮ࡨࠤࡴࡶࡥࡳࡣࡷ࡭ࡴࡴࡳࠨத"))
    try:
      if not os.path.isfile(bstack11111lll_opy_):
        with open(bstack11111lll_opy_, bstack11l1l_opy_ (u"࠭ࡷࠨ஥")) as f:
          json.dump({}, f)
      if os.path.exists(bstack11111lll_opy_):
        with open(bstack11111lll_opy_, bstack11l1l_opy_ (u"ࠧࡳࠩ஦")) as f:
          content = f.read().strip()
          if content:
            bstack1l1l111ll1_opy_ = json.loads(content)
    except Exception as e:
      logger.debug(bstack11l1l_opy_ (u"ࠨࡇࡵࡶࡴࡸࠠࡪࡰࠣࡶࡪࡧࡤࡪࡰࡪࠤࡷࡵࡢࡰࡶࠣࡶࡪࡶ࡯ࡳࡶࠣࡪ࡮ࡲࡥ࠻ࠢࠪ஧") + str(e))
    return bstack1l1l111ll1_opy_
  try:
    os.makedirs(os.path.dirname(bstack11111lll_opy_), exist_ok=True)
    with FileLock(lock_file, timeout=10):
      if not os.path.isfile(bstack11111lll_opy_):
        with open(bstack11111lll_opy_, bstack11l1l_opy_ (u"ࠩࡺࠫந")) as f:
          json.dump({}, f)
      if os.path.exists(bstack11111lll_opy_):
        with open(bstack11111lll_opy_, bstack11l1l_opy_ (u"ࠪࡶࠬன")) as f:
          content = f.read().strip()
          if content:
            bstack1l1l111ll1_opy_ = json.loads(content)
  except Exception as e:
    logger.debug(bstack11l1l_opy_ (u"ࠫࡊࡸࡲࡰࡴࠣ࡭ࡳࠦࡲࡦࡣࡧ࡭ࡳ࡭ࠠࡳࡱࡥࡳࡹࠦࡲࡦࡲࡲࡶࡹࠦࡦࡪ࡮ࡨ࠾ࠥ࠭ப") + str(e))
  finally:
    return bstack1l1l111ll1_opy_
def bstack1l1l1lll1_opy_(platform_index, item_index):
  global bstack11111lll_opy_
  lock_file = bstack11111lll_opy_ + bstack11l1l_opy_ (u"ࠬ࠴࡬ࡰࡥ࡮ࠫ஫")
  try:
    from filelock import FileLock
  except ImportError:
    logger.debug(bstack11l1l_opy_ (u"࠭ࡦࡪ࡮ࡨࡰࡴࡩ࡫ࠡࡰࡲࡸࠥࡧࡶࡢ࡫࡯ࡥࡧࡲࡥ࠭ࠢࡸࡷ࡮ࡴࡧࠡࡤࡤࡷ࡮ࡩࠠࡧ࡫࡯ࡩࠥࡵࡰࡦࡴࡤࡸ࡮ࡵ࡮ࡴࠩ஬"))
    try:
      bstack1l1l111ll1_opy_ = {}
      if os.path.exists(bstack11111lll_opy_):
        with open(bstack11111lll_opy_, bstack11l1l_opy_ (u"ࠧࡳࠩ஭")) as f:
          content = f.read().strip()
          if content:
            bstack1l1l111ll1_opy_ = json.loads(content)
      bstack1l1l111ll1_opy_[item_index] = platform_index
      with open(bstack11111lll_opy_, bstack11l1l_opy_ (u"ࠣࡹࠥம")) as outfile:
        json.dump(bstack1l1l111ll1_opy_, outfile)
    except Exception as e:
      logger.debug(bstack11l1l_opy_ (u"ࠩࡈࡶࡷࡵࡲࠡ࡫ࡱࠤࡼࡸࡩࡵ࡫ࡱ࡫ࠥࡺ࡯ࠡࡴࡲࡦࡴࡺࠠࡳࡧࡳࡳࡷࡺࠠࡧ࡫࡯ࡩ࠿ࠦࠧய") + str(e))
    return
  try:
    os.makedirs(os.path.dirname(bstack11111lll_opy_), exist_ok=True)
    with FileLock(lock_file, timeout=10):
      bstack1l1l111ll1_opy_ = {}
      if os.path.exists(bstack11111lll_opy_):
        with open(bstack11111lll_opy_, bstack11l1l_opy_ (u"ࠪࡶࠬர")) as f:
          content = f.read().strip()
          if content:
            bstack1l1l111ll1_opy_ = json.loads(content)
      bstack1l1l111ll1_opy_[item_index] = platform_index
      with open(bstack11111lll_opy_, bstack11l1l_opy_ (u"ࠦࡼࠨற")) as outfile:
        json.dump(bstack1l1l111ll1_opy_, outfile)
  except Exception as e:
    logger.debug(bstack11l1l_opy_ (u"ࠬࡋࡲࡳࡱࡵࠤ࡮ࡴࠠࡸࡴ࡬ࡸ࡮ࡴࡧࠡࡶࡲࠤࡷࡵࡢࡰࡶࠣࡶࡪࡶ࡯ࡳࡶࠣࡪ࡮ࡲࡥ࠻ࠢࠪல") + str(e))
def bstack11lll11111_opy_(bstack11l111ll11_opy_):
  global CONFIG
  bstack1l1l1l111_opy_ = bstack11l1l_opy_ (u"࠭ࠧள")
  if not bstack11l1l_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪழ") in CONFIG:
    logger.info(bstack11l1l_opy_ (u"ࠨࡐࡲࠤࡵࡲࡡࡵࡨࡲࡶࡲࡹࠠࡱࡣࡶࡷࡪࡪࠠࡶࡰࡤࡦࡱ࡫ࠠࡵࡱࠣ࡫ࡪࡴࡥࡳࡣࡷࡩࠥࡸࡥࡱࡱࡵࡸࠥ࡬࡯ࡳࠢࡕࡳࡧࡵࡴࠡࡴࡸࡲࠬவ"))
  try:
    platform = CONFIG[bstack11l1l_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬஶ")][bstack11l111ll11_opy_]
    if bstack11l1l_opy_ (u"ࠪࡳࡸ࠭ஷ") in platform:
      bstack1l1l1l111_opy_ += str(platform[bstack11l1l_opy_ (u"ࠫࡴࡹࠧஸ")]) + bstack11l1l_opy_ (u"ࠬ࠲ࠠࠨஹ")
    if bstack11l1l_opy_ (u"࠭࡯ࡴࡘࡨࡶࡸ࡯࡯࡯ࠩ஺") in platform:
      bstack1l1l1l111_opy_ += str(platform[bstack11l1l_opy_ (u"ࠧࡰࡵ࡙ࡩࡷࡹࡩࡰࡰࠪ஻")]) + bstack11l1l_opy_ (u"ࠨ࠮ࠣࠫ஼")
    if bstack11l1l_opy_ (u"ࠩࡧࡩࡻ࡯ࡣࡦࡐࡤࡱࡪ࠭஽") in platform:
      bstack1l1l1l111_opy_ += str(platform[bstack11l1l_opy_ (u"ࠪࡨࡪࡼࡩࡤࡧࡑࡥࡲ࡫ࠧா")]) + bstack11l1l_opy_ (u"ࠫ࠱ࠦࠧி")
    if bstack11l1l_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡖࡦࡴࡶ࡭ࡴࡴࠧீ") in platform:
      bstack1l1l1l111_opy_ += str(platform[bstack11l1l_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡗࡧࡵࡷ࡮ࡵ࡮ࠨு")]) + bstack11l1l_opy_ (u"ࠧ࠭ࠢࠪூ")
    if bstack11l1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡐࡤࡱࡪ࠭௃") in platform:
      bstack1l1l1l111_opy_ += str(platform[bstack11l1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡑࡥࡲ࡫ࠧ௄")]) + bstack11l1l_opy_ (u"ࠪ࠰ࠥ࠭௅")
    if bstack11l1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶ࡛࡫ࡲࡴ࡫ࡲࡲࠬெ") in platform:
      bstack1l1l1l111_opy_ += str(platform[bstack11l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡜ࡥࡳࡵ࡬ࡳࡳ࠭ே")]) + bstack11l1l_opy_ (u"࠭ࠬࠡࠩை")
  except Exception as e:
    logger.debug(bstack11l1l_opy_ (u"ࠧࡔࡱࡰࡩࠥ࡫ࡲࡳࡱࡵࠤ࡮ࡴࠠࡨࡧࡱࡩࡷࡧࡴࡪࡰࡪࠤࡵࡲࡡࡵࡨࡲࡶࡲࠦࡳࡵࡴ࡬ࡲ࡬ࠦࡦࡰࡴࠣࡶࡪࡶ࡯ࡳࡶࠣ࡫ࡪࡴࡥࡳࡣࡷ࡭ࡴࡴࠧ௉") + str(e))
  finally:
    if bstack1l1l1l111_opy_[len(bstack1l1l1l111_opy_) - 2:] == bstack11l1l_opy_ (u"ࠨ࠮ࠣࠫொ"):
      bstack1l1l1l111_opy_ = bstack1l1l1l111_opy_[:-2]
    return bstack1l1l1l111_opy_
def bstack1l111ll11_opy_(path, bstack1l1l1l111_opy_):
  try:
    import xml.etree.ElementTree as ET
    bstack1l1lllll1_opy_ = ET.parse(path)
    bstack1ll11ll111_opy_ = bstack1l1lllll1_opy_.getroot()
    bstack11l11ll11_opy_ = None
    for suite in bstack1ll11ll111_opy_.iter(bstack11l1l_opy_ (u"ࠩࡶࡹ࡮ࡺࡥࠨோ")):
      if bstack11l1l_opy_ (u"ࠪࡷࡴࡻࡲࡤࡧࠪௌ") in suite.attrib:
        suite.attrib[bstack11l1l_opy_ (u"ࠫࡳࡧ࡭ࡦ்ࠩ")] += bstack11l1l_opy_ (u"ࠬࠦࠧ௎") + bstack1l1l1l111_opy_
        bstack11l11ll11_opy_ = suite
    bstack11l1l1ll1l_opy_ = None
    for robot in bstack1ll11ll111_opy_.iter(bstack11l1l_opy_ (u"࠭ࡲࡰࡤࡲࡸࠬ௏")):
      bstack11l1l1ll1l_opy_ = robot
    bstack111lllll1_opy_ = len(bstack11l1l1ll1l_opy_.findall(bstack11l1l_opy_ (u"ࠧࡴࡷ࡬ࡸࡪ࠭ௐ")))
    if bstack111lllll1_opy_ == 1:
      bstack11l1l1ll1l_opy_.remove(bstack11l1l1ll1l_opy_.findall(bstack11l1l_opy_ (u"ࠨࡵࡸ࡭ࡹ࡫ࠧ௑"))[0])
      bstack1l1l111lll_opy_ = ET.Element(bstack11l1l_opy_ (u"ࠩࡶࡹ࡮ࡺࡥࠨ௒"), attrib={bstack11l1l_opy_ (u"ࠪࡲࡦࡳࡥࠨ௓"): bstack11l1l_opy_ (u"ࠫࡘࡻࡩࡵࡧࡶࠫ௔"), bstack11l1l_opy_ (u"ࠬ࡯ࡤࠨ௕"): bstack11l1l_opy_ (u"࠭ࡳ࠱ࠩ௖")})
      bstack11l1l1ll1l_opy_.insert(1, bstack1l1l111lll_opy_)
      bstack111ll1lll_opy_ = None
      for suite in bstack11l1l1ll1l_opy_.iter(bstack11l1l_opy_ (u"ࠧࡴࡷ࡬ࡸࡪ࠭ௗ")):
        bstack111ll1lll_opy_ = suite
      bstack111ll1lll_opy_.append(bstack11l11ll11_opy_)
      bstack1l1l11ll_opy_ = None
      for status in bstack11l11ll11_opy_.iter(bstack11l1l_opy_ (u"ࠨࡵࡷࡥࡹࡻࡳࠨ௘")):
        bstack1l1l11ll_opy_ = status
      bstack111ll1lll_opy_.append(bstack1l1l11ll_opy_)
    bstack1l1lllll1_opy_.write(path)
  except Exception as e:
    logger.debug(bstack11l1l_opy_ (u"ࠩࡈࡶࡷࡵࡲࠡ࡫ࡱࠤࡵࡧࡲࡴ࡫ࡱ࡫ࠥࡽࡨࡪ࡮ࡨࠤ࡬࡫࡮ࡦࡴࡤࡸ࡮ࡴࡧࠡࡴࡲࡦࡴࡺࠠࡳࡧࡳࡳࡷࡺࠧ௙") + str(e))
def bstack1l1ll1l111_opy_(outs_dir, pabot_args, options, start_time_string, tests_root_name):
  global bstack1l1l1ll11l_opy_
  global CONFIG
  if bstack11l1l_opy_ (u"ࠥࡴࡾࡺࡨࡰࡰࡳࡥࡹ࡮ࠢ௚") in options:
    del options[bstack11l1l_opy_ (u"ࠦࡵࡿࡴࡩࡱࡱࡴࡦࡺࡨࠣ௛")]
  bstack1llllll1ll_opy_ = bstack1l11l11l1_opy_()
  for item_id in bstack1llllll1ll_opy_.keys():
    path = os.path.join(outs_dir, str(item_id), bstack11l1l_opy_ (u"ࠬࡵࡵࡵࡲࡸࡸ࠳ࡾ࡭࡭ࠩ௜"))
    bstack1l111ll11_opy_(path, bstack11lll11111_opy_(bstack1llllll1ll_opy_[item_id]))
  bstack1lll1ll11_opy_()
  return bstack1l1l1ll11l_opy_(outs_dir, pabot_args, options, start_time_string, tests_root_name)
def bstack1l11111l1l_opy_(self, ff_profile_dir):
  global bstack1l1l1l1lll_opy_
  if not ff_profile_dir:
    return None
  return bstack1l1l1l1lll_opy_(self, ff_profile_dir)
def bstack1l1l1lll1l_opy_(datasources, opts_for_run, outs_dir, pabot_args, suite_group):
  from pabot.pabot import QueueItem
  global CONFIG
  global bstack11l11l1ll1_opy_
  bstack1lll11l11l_opy_ = []
  if bstack11l1l_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩ௝") in CONFIG:
    bstack1lll11l11l_opy_ = CONFIG[bstack11l1l_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪ௞")]
  return [
    QueueItem(
      datasources,
      outs_dir,
      opts_for_run,
      suite,
      pabot_args[bstack11l1l_opy_ (u"ࠣࡥࡲࡱࡲࡧ࡮ࡥࠤ௟")],
      pabot_args[bstack11l1l_opy_ (u"ࠤࡹࡩࡷࡨ࡯ࡴࡧࠥ௠")],
      argfile,
      pabot_args.get(bstack11l1l_opy_ (u"ࠥ࡬࡮ࡼࡥࠣ௡")),
      pabot_args[bstack11l1l_opy_ (u"ࠦࡵࡸ࡯ࡤࡧࡶࡷࡪࡹࠢ௢")],
      platform[0],
      bstack11l11l1ll1_opy_
    )
    for suite in suite_group
    for argfile in pabot_args[bstack11l1l_opy_ (u"ࠧࡧࡲࡨࡷࡰࡩࡳࡺࡦࡪ࡮ࡨࡷࠧ௣")] or [(bstack11l1l_opy_ (u"ࠨࠢ௤"), None)]
    for platform in enumerate(bstack1lll11l11l_opy_)
  ]
def bstack11llllll11_opy_(self, datasources, outs_dir, options,
                        execution_item, command, verbose, argfile,
                        hive=None, processes=0, platform_index=0, bstack11ll111ll_opy_=bstack11l1l_opy_ (u"ࠧࠨ௥")):
  global bstack1l111ll1_opy_
  self.platform_index = platform_index
  self.bstack1lll1111ll_opy_ = bstack11ll111ll_opy_
  bstack1l111ll1_opy_(self, datasources, outs_dir, options,
                      execution_item, command, verbose, argfile, hive, processes)
def bstack1llllll1l_opy_(caller_id, datasources, is_last, item, outs_dir):
  global bstack11l1l111l1_opy_
  global bstack1l1l11ll1l_opy_
  bstack11l1llllll_opy_ = copy.deepcopy(item)
  if not bstack11l1l_opy_ (u"ࠨࡸࡤࡶ࡮ࡧࡢ࡭ࡧࠪ௦") in item.options:
    bstack11l1llllll_opy_.options[bstack11l1l_opy_ (u"ࠩࡹࡥࡷ࡯ࡡࡣ࡮ࡨࠫ௧")] = []
  bstack1l1111l11l_opy_ = bstack11l1llllll_opy_.options[bstack11l1l_opy_ (u"ࠪࡺࡦࡸࡩࡢࡤ࡯ࡩࠬ௨")].copy()
  for v in bstack11l1llllll_opy_.options[bstack11l1l_opy_ (u"ࠫࡻࡧࡲࡪࡣࡥࡰࡪ࠭௩")]:
    if bstack11l1l_opy_ (u"ࠬࡈࡓࡕࡃࡆࡏࡕࡒࡁࡕࡈࡒࡖࡒࡏࡎࡅࡇ࡛ࠫ௪") in v:
      bstack1l1111l11l_opy_.remove(v)
    if bstack11l1l_opy_ (u"࠭ࡂࡔࡖࡄࡇࡐࡉࡌࡊࡃࡕࡋࡘ࠭௫") in v:
      bstack1l1111l11l_opy_.remove(v)
    if bstack11l1l_opy_ (u"ࠧࡃࡕࡗࡅࡈࡑࡄࡆࡈࡏࡓࡈࡇࡌࡊࡆࡈࡒ࡙ࡏࡆࡊࡇࡕࠫ௬") in v:
      bstack1l1111l11l_opy_.remove(v)
  bstack1l1111l11l_opy_.insert(0, bstack11l1l_opy_ (u"ࠨࡄࡖࡘࡆࡉࡋࡑࡎࡄࡘࡋࡕࡒࡎࡋࡑࡈࡊ࡞࠺ࡼࡿࠪ௭").format(bstack11l1llllll_opy_.platform_index))
  bstack1l1111l11l_opy_.insert(0, bstack11l1l_opy_ (u"ࠩࡅࡗ࡙ࡇࡃࡌࡆࡈࡊࡑࡕࡃࡂࡎࡌࡈࡊࡔࡔࡊࡈࡌࡉࡗࡀࡻࡾࠩ௮").format(bstack11l1llllll_opy_.bstack1lll1111ll_opy_))
  bstack11l1llllll_opy_.options[bstack11l1l_opy_ (u"ࠪࡺࡦࡸࡩࡢࡤ࡯ࡩࠬ௯")] = bstack1l1111l11l_opy_
  if bstack1l1l11ll1l_opy_:
    bstack11l1llllll_opy_.options[bstack11l1l_opy_ (u"ࠫࡻࡧࡲࡪࡣࡥࡰࡪ࠭௰")].insert(0, bstack11l1l_opy_ (u"ࠬࡈࡓࡕࡃࡆࡏࡈࡒࡉࡂࡔࡊࡗ࠿ࢁࡽࠨ௱").format(bstack1l1l11ll1l_opy_))
  return bstack11l1l111l1_opy_(caller_id, datasources, is_last, bstack11l1llllll_opy_, outs_dir)
def bstack1ll1ll1l1l_opy_(command, item_index):
  try:
    if bstack1l1ll11111_opy_.get_property(bstack11l1l_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡥࡳࡦࡵࡶ࡭ࡴࡴࠧ௲")):
      os.environ[bstack11l1l_opy_ (u"ࠧࡄࡗࡕࡖࡊࡔࡔࡠࡒࡏࡅ࡙ࡌࡏࡓࡏࡢࡈࡆ࡚ࡁࠨ௳")] = json.dumps(CONFIG[bstack11l1l_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫ௴")][item_index % bstack1ll1ll1lll_opy_])
    global bstack1l1l11ll1l_opy_
    if bstack1l1l11ll1l_opy_:
      command[0] = command[0].replace(bstack11l1l_opy_ (u"ࠩࡵࡳࡧࡵࡴࠨ௵"), bstack11l1l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠯ࡶࡨࡰࠦࡲࡰࡤࡲࡸ࠲࡯࡮ࡵࡧࡵࡲࡦࡲࠠ࠮࠯ࡥࡷࡹࡧࡣ࡬ࡡࡳࡰࡦࡺࡦࡰࡴࡰࡣ࡮ࡴࡤࡦࡺࠣࠫ௶") + str(item_index % bstack1ll1ll1lll_opy_) + bstack11l1l_opy_ (u"ࠫࠥ࠳࠭ࡣࡵࡷࡥࡨࡱ࡟ࡪࡶࡨࡱࡤ࡯࡮ࡥࡧࡻࠤࠬ௷") + str(
        item_index) + bstack11l1l_opy_ (u"ࠬࠦࠧ௸") + bstack1l1l11ll1l_opy_, 1)
    else:
      command[0] = command[0].replace(bstack11l1l_opy_ (u"࠭ࡲࡰࡤࡲࡸࠬ௹"),
                                      bstack11l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠳ࡳࡥ࡭ࠣࡶࡴࡨ࡯ࡵ࠯࡬ࡲࡹ࡫ࡲ࡯ࡣ࡯ࠤ࠲࠳ࡢࡴࡶࡤࡧࡰࡥࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡠ࡫ࡱࡨࡪࡾࠠࠨ௺") +  str(item_index % bstack1ll1ll1lll_opy_) + bstack11l1l_opy_ (u"ࠨࠢ࠰࠱ࡧࡹࡴࡢࡥ࡮ࡣ࡮ࡺࡥ࡮ࡡ࡬ࡲࡩ࡫ࡸࠡࠩ௻") + str(item_index), 1)
  except Exception as e:
    logger.error(bstack11l1l_opy_ (u"ࠩࡈࡶࡷࡵࡲࠡ࡯ࡲࡨ࡮࡬ࡹࡪࡰࡪࠤࡨࡵ࡭࡮ࡣࡱࡨࠥ࡬࡯ࡳࠢࡳࡥࡧࡵࡴࠡࡴࡸࡲ࠿ࠦࡻࡾࠩ௼").format(str(e)))
def bstack11ll11lll_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index):
  global bstack11ll1l11_opy_
  try:
    bstack1ll1ll1l1l_opy_(command, item_index)
    return bstack11ll1l11_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index)
  except Exception as e:
    logger.error(bstack11l1l_opy_ (u"ࠪࡉࡷࡸ࡯ࡳࠢ࡬ࡲࠥࡶࡡࡣࡱࡷࠤࡷࡻ࡮࠻ࠢࡾࢁࠬ௽").format(str(e)))
    raise e
def bstack1l111l11ll_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir):
  global bstack11ll1l11_opy_
  try:
    bstack1ll1ll1l1l_opy_(command, item_index)
    return bstack11ll1l11_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir)
  except Exception as e:
    logger.error(bstack11l1l_opy_ (u"ࠫࡊࡸࡲࡰࡴࠣ࡭ࡳࠦࡰࡢࡤࡲࡸࠥࡸࡵ࡯ࠢ࠵࠲࠶࠹࠺ࠡࡽࢀࠫ௾").format(str(e)))
    try:
      return bstack11ll1l11_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index)
    except Exception as e2:
      logger.error(bstack11l1l_opy_ (u"ࠬࡋࡲࡳࡱࡵࠤ࡮ࡴࠠࡱࡣࡥࡳࡹࠦ࠲࠯࠳࠶ࠤ࡫ࡧ࡬࡭ࡤࡤࡧࡰࡀࠠࡼࡿࠪ௿").format(str(e2)))
      raise e
def bstack1l111111ll_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir, process_timeout):
  global bstack11ll1l11_opy_
  try:
    bstack1ll1ll1l1l_opy_(command, item_index)
    if process_timeout is None:
      process_timeout = 3600
    return bstack11ll1l11_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir, process_timeout)
  except Exception as e:
    logger.error(bstack11l1l_opy_ (u"࠭ࡅࡳࡴࡲࡶࠥ࡯࡮ࠡࡲࡤࡦࡴࡺࠠࡳࡷࡱࠤ࠷࠴࠱࠶࠼ࠣࡿࢂ࠭ఀ").format(str(e)))
    try:
      return bstack11ll1l11_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir)
    except Exception as e2:
      logger.error(bstack11l1l_opy_ (u"ࠧࡆࡴࡵࡳࡷࠦࡩ࡯ࠢࡳࡥࡧࡵࡴࠡ࠴࠱࠵࠺ࠦࡦࡢ࡮࡯ࡦࡦࡩ࡫࠻ࠢࡾࢁࠬఁ").format(str(e2)))
      raise e
def _11lll11l1_opy_(bstack1l1l1ll11_opy_, item_index, process_timeout, sleep_before_start, bstack1l111l11_opy_):
  bstack1ll1ll1l1l_opy_(bstack1l1l1ll11_opy_, item_index)
  if process_timeout is None:
    process_timeout = 3600
  if sleep_before_start and sleep_before_start > 0:
    time.sleep(min(sleep_before_start, 5))
  return process_timeout
def bstack111lll1l1_opy_(command, bstack111lll1lll_opy_, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir, process_timeout, sleep_before_start):
  global bstack11ll1l11_opy_
  global bstack11l11lll1_opy_
  global bstack1l1l11ll1l_opy_
  try:
    for env_name, bstack1lll1111l_opy_ in bstack11l11lll1_opy_.items():
      os.environ[env_name] = bstack1lll1111l_opy_
    bstack1l1l11ll1l_opy_ = bstack11l1l_opy_ (u"ࠣࠤం")
    bstack1ll1ll1l1l_opy_(command, item_index)
    if process_timeout is None:
      process_timeout = 3600
    if sleep_before_start and sleep_before_start > 0:
      time.sleep(min(sleep_before_start, 5))
    return bstack11ll1l11_opy_(command, bstack111lll1lll_opy_, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir, process_timeout, sleep_before_start)
  except Exception as e:
    logger.error(bstack11l1l_opy_ (u"ࠩࡈࡶࡷࡵࡲࠡ࡫ࡱࠤࡵࡧࡢࡰࡶࠣࡶࡺࡴࠠ࠶࠰࠳࠾ࠥࢁࡽࠨః").format(str(e)))
    try:
      return bstack11ll1l11_opy_(command, bstack111lll1lll_opy_, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir, process_timeout)
    except Exception as e2:
      logger.error(bstack11l1l_opy_ (u"ࠪࡉࡷࡸ࡯ࡳࠢ࡬ࡲࠥࡶࡡࡣࡱࡷࠤ࡫ࡧ࡬࡭ࡤࡤࡧࡰࡀࠠࡼࡿࠪఄ").format(str(e2)))
      raise e
def bstack1ll11l11l_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir, process_timeout, sleep_before_start):
  global bstack11ll1l11_opy_
  try:
    process_timeout = _11lll11l1_opy_(command, item_index, process_timeout, sleep_before_start, bstack11l1l_opy_ (u"ࠫ࠹࠴࠲ࠨఅ"))
    return bstack11ll1l11_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir, process_timeout, sleep_before_start)
  except Exception as e:
    logger.error(bstack11l1l_opy_ (u"ࠬࡋࡲࡳࡱࡵࠤ࡮ࡴࠠࡱࡣࡥࡳࡹࠦࡲࡶࡰࠣ࠸࠳࠸࠺ࠡࡽࢀࠫఆ").format(str(e)))
    try:
      return bstack11ll1l11_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir, process_timeout)
    except Exception as e2:
      logger.error(bstack11l1l_opy_ (u"࠭ࡅࡳࡴࡲࡶࠥ࡯࡮ࠡࡲࡤࡦࡴࡺࠠࡧࡣ࡯ࡰࡧࡧࡣ࡬࠼ࠣࡿࢂ࠭ఇ").format(str(e2)))
      raise e
def is_driver_active(driver):
  return True if driver and driver.session_id else False
def bstack11ll11l11_opy_(self, runner, quiet=False, capture=True):
  global bstack111ll11ll_opy_
  bstack1ll1l1l1_opy_ = bstack111ll11ll_opy_(self, runner, quiet=quiet, capture=capture)
  if self.exception:
    if not hasattr(runner, bstack11l1l_opy_ (u"ࠧࡦࡺࡦࡩࡵࡺࡩࡰࡰࡢࡥࡷࡸࠧఈ")):
      runner.exception_arr = []
    if not hasattr(runner, bstack11l1l_opy_ (u"ࠨࡧࡻࡧࡤࡺࡲࡢࡥࡨࡦࡦࡩ࡫ࡠࡣࡵࡶࠬఉ")):
      runner.exc_traceback_arr = []
    runner.exception = self.exception
    runner.exc_traceback = self.exc_traceback
    runner.exception_arr.append(self.exception)
    runner.exc_traceback_arr.append(self.exc_traceback)
  return bstack1ll1l1l1_opy_
def bstack1ll1l111ll_opy_(runner, hook_name, context, element, bstack1ll1llll1_opy_, *args):
  try:
    if runner.hooks.get(hook_name):
      bstack11ll11l11l_opy_.bstack11111llll_opy_(hook_name, element)
    bstack1ll1llll1_opy_(runner, hook_name, context, *args)
    if runner.hooks.get(hook_name):
      bstack11ll11l11l_opy_.bstack1l1l1111l_opy_(element)
      if hook_name not in [bstack11l1l_opy_ (u"ࠩࡥࡩ࡫ࡵࡲࡦࡡࡤࡰࡱ࠭ఊ"), bstack11l1l_opy_ (u"ࠪࡥ࡫ࡺࡥࡳࡡࡤࡰࡱ࠭ఋ")] and args and hasattr(args[0], bstack11l1l_opy_ (u"ࠫࡪࡸࡲࡰࡴࡢࡱࡪࡹࡳࡢࡩࡨࠫఌ")):
        args[0].error_message = bstack11l1l_opy_ (u"ࠬ࠭఍")
  except Exception as e:
    logger.debug(bstack11l1l_opy_ (u"࠭ࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢ࡫ࡥࡳࡪ࡬ࡦࠢ࡫ࡳࡴࡱࡳࠡ࡫ࡱࠤࡧ࡫ࡨࡢࡸࡨ࠾ࠥࢁࡽࠨఎ").format(str(e)))
@measure(event_name=EVENTS.bstack1l1lllll_opy_, stage=STAGE.bstack1lll1l11l_opy_, hook_type=bstack11l1l_opy_ (u"ࠢࡣࡧࡩࡳࡷ࡫ࡁ࡭࡮ࠥఏ"), bstack1l1l1llll_opy_=bstack11l1ll1l_opy_)
def bstack1l111l11l_opy_(runner, name, context, bstack1ll1llll1_opy_, *args):
    if runner.hooks.get(bstack11l1l_opy_ (u"ࠣࡤࡨࡪࡴࡸࡥࡠࡣ࡯ࡰࠧఐ")).__name__ != bstack11l1l_opy_ (u"ࠤࡥࡩ࡫ࡵࡲࡦࡡࡤࡰࡱࡥࡤࡦࡨࡤࡹࡱࡺ࡟ࡩࡱࡲ࡯ࠧ఑"):
      bstack1ll1l111ll_opy_(runner, name, context, runner, bstack1ll1llll1_opy_, *args)
    try:
      threading.current_thread().bstackSessionDriver if bstack111llll111_opy_(bstack11l1l_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭ࡖࡩࡸࡹࡩࡰࡰࡇࡶ࡮ࡼࡥࡳࠩఒ")) else context.browser
      runner.driver_initialised = bstack11l1l_opy_ (u"ࠦࡧ࡫ࡦࡰࡴࡨࡣࡦࡲ࡬ࠣఓ")
    except Exception as e:
      logger.debug(bstack11l1l_opy_ (u"ࠬࡌࡡࡪ࡮ࡨࡨࠥࡺ࡯ࠡࡵࡨࡸࠥࡪࡲࡪࡸࡨࡶࠥ࡯࡮ࡪࡶ࡬ࡥࡱ࡯ࡳࡦࠢࡤࡸࡹࡸࡩࡣࡷࡷࡩ࠿ࠦࡻࡾࠩఔ").format(str(e)))
def bstack1l1l111l_opy_(runner, name, context, bstack1ll1llll1_opy_, *args):
    bstack1ll1l111ll_opy_(runner, name, context, context.feature, bstack1ll1llll1_opy_, *args)
    try:
      if not bstack1lllllll1_opy_:
        bstack1l1l1l11l1_opy_ = threading.current_thread().bstackSessionDriver if bstack111llll111_opy_(bstack11l1l_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰ࡙ࡥࡴࡵ࡬ࡳࡳࡊࡲࡪࡸࡨࡶࠬక")) else context.browser
        if is_driver_active(bstack1l1l1l11l1_opy_):
          if runner.driver_initialised is None: runner.driver_initialised = bstack11l1l_opy_ (u"ࠢࡣࡧࡩࡳࡷ࡫࡟ࡧࡧࡤࡸࡺࡸࡥࠣఖ")
          bstack11l1111111_opy_ = str(runner.feature.name)
          bstack1ll1lll11_opy_(context, bstack11l1111111_opy_)
          bstack1l1l1l11l1_opy_.execute_script(bstack11l1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࡿࠧࡧࡣࡵ࡫ࡲࡲࠧࡀࠠࠣࡵࡨࡸࡘ࡫ࡳࡴ࡫ࡲࡲࡓࡧ࡭ࡦࠤ࠯ࠤࠧࡧࡲࡨࡷࡰࡩࡳࡺࡳࠣ࠼ࠣࡿࠧࡴࡡ࡮ࡧࠥ࠾ࠥ࠭గ") + json.dumps(bstack11l1111111_opy_) + bstack11l1l_opy_ (u"ࠩࢀࢁࠬఘ"))
    except Exception as e:
      logger.debug(bstack11l1l_opy_ (u"ࠪࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦࡳࡦࡶࠣࡷࡪࡹࡳࡪࡱࡱࠤࡳࡧ࡭ࡦࠢ࡬ࡲࠥࡨࡥࡧࡱࡵࡩࠥ࡬ࡥࡢࡶࡸࡶࡪࡀࠠࡼࡿࠪఙ").format(str(e)))
def bstack1l1l1111ll_opy_(runner, name, context, bstack1ll1llll1_opy_, *args):
    target = context.scenario if hasattr(context, bstack11l1l_opy_ (u"ࠫࡸࡩࡥ࡯ࡣࡵ࡭ࡴ࠭చ")) else context.feature
    bstack1ll1l111ll_opy_(runner, name, context, target, bstack1ll1llll1_opy_, *args)
@measure(event_name=EVENTS.bstack1l1l11lll_opy_, stage=STAGE.bstack1lll1l11l_opy_, bstack1l1l1llll_opy_=bstack11l1ll1l_opy_)
def bstack1ll111l11l_opy_(runner, name, context, bstack1ll1llll1_opy_, *args):
    bstack11ll11l11l_opy_.start_test(context)
    bstack1ll1l111ll_opy_(runner, name, context, context.scenario, bstack1ll1llll1_opy_, *args)
    threading.current_thread().a11y_stop = False
    bstack111lllll11_opy_.bstack111l1l11l_opy_(context, *args)
    try:
      bstack1l1l1l11l1_opy_ = bstack11lll11l_opy_(threading.current_thread(), bstack11l1l_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯ࡘ࡫ࡳࡴ࡫ࡲࡲࡉࡸࡩࡷࡧࡵࠫఛ"), context.browser)
      if is_driver_active(bstack1l1l1l11l1_opy_):
        bstack1ll1llll11_opy_.bstack1llll1llll_opy_(bstack11lll11l_opy_(threading.current_thread(), bstack11l1l_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰ࡙ࡥࡴࡵ࡬ࡳࡳࡊࡲࡪࡸࡨࡶࠬజ"), {}))
        if runner.driver_initialised is None: runner.driver_initialised = bstack11l1l_opy_ (u"ࠢࡣࡧࡩࡳࡷ࡫࡟ࡴࡥࡨࡲࡦࡸࡩࡰࠤఝ")
        if (not bstack1lllllll1_opy_):
          scenario_name = args[0].name
          feature_name = bstack11l1111111_opy_ = str(runner.feature.name)
          bstack11l1111111_opy_ = feature_name + bstack11l1l_opy_ (u"ࠨࠢ࠰ࠤࠬఞ") + scenario_name
          if runner.driver_initialised == bstack11l1l_opy_ (u"ࠤࡥࡩ࡫ࡵࡲࡦࡡࡶࡧࡪࡴࡡࡳ࡫ࡲࠦట"):
            bstack1ll1lll11_opy_(context, bstack11l1111111_opy_)
            bstack1l1l1l11l1_opy_.execute_script(bstack11l1l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡨࡼࡪࡩࡵࡵࡱࡵ࠾ࠥࢁࠢࡢࡥࡷ࡭ࡴࡴࠢ࠻ࠢࠥࡷࡪࡺࡓࡦࡵࡶ࡭ࡴࡴࡎࡢ࡯ࡨࠦ࠱ࠦࠢࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠥ࠾ࠥࢁࠢ࡯ࡣࡰࡩࠧࡀࠠࠨఠ") + json.dumps(bstack11l1111111_opy_) + bstack11l1l_opy_ (u"ࠫࢂࢃࠧడ"))
    except Exception as e:
      logger.debug(bstack11l1l_opy_ (u"ࠬࡌࡡࡪ࡮ࡨࡨࠥࡺ࡯ࠡࡵࡨࡸࠥࡹࡥࡴࡵ࡬ࡳࡳࠦ࡮ࡢ࡯ࡨࠤ࡮ࡴࠠࡣࡧࡩࡳࡷ࡫ࠠࡴࡥࡨࡲࡦࡸࡩࡰ࠼ࠣࡿࢂ࠭ఢ").format(str(e)))
@measure(event_name=EVENTS.bstack1l1lllll_opy_, stage=STAGE.bstack1lll1l11l_opy_, hook_type=bstack11l1l_opy_ (u"ࠨࡢࡦࡨࡲࡶࡪ࡙ࡴࡦࡲࠥణ"), bstack1l1l1llll_opy_=bstack11l1ll1l_opy_)
def bstack1ll1l11l1_opy_(runner, name, context, bstack1ll1llll1_opy_, *args):
    bstack1ll1l111ll_opy_(runner, name, context, args[0], bstack1ll1llll1_opy_, *args)
    try:
      bstack1l1l1l11l1_opy_ = threading.current_thread().bstackSessionDriver if bstack111llll111_opy_(bstack11l1l_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱࡓࡦࡵࡶ࡭ࡴࡴࡄࡳ࡫ࡹࡩࡷ࠭త")) else context.browser
      if is_driver_active(bstack1l1l1l11l1_opy_):
        if runner.driver_initialised is None: runner.driver_initialised = bstack11l1l_opy_ (u"ࠣࡤࡨࡪࡴࡸࡥࡠࡵࡷࡩࡵࠨథ")
        bstack11ll11l11l_opy_.bstack1l1111ll11_opy_(args[0])
        if runner.driver_initialised == bstack11l1l_opy_ (u"ࠤࡥࡩ࡫ࡵࡲࡦࡡࡶࡸࡪࡶࠢద"):
          feature_name = bstack11l1111111_opy_ = str(runner.feature.name)
          bstack11l1111111_opy_ = feature_name + bstack11l1l_opy_ (u"ࠪࠤ࠲ࠦࠧధ") + context.scenario.name
          bstack1l1l1l11l1_opy_.execute_script(bstack11l1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡩࡽ࡫ࡣࡶࡶࡲࡶ࠿ࠦࡻࠣࡣࡦࡸ࡮ࡵ࡮ࠣ࠼ࠣࠦࡸ࡫ࡴࡔࡧࡶࡷ࡮ࡵ࡮ࡏࡣࡰࡩࠧ࠲ࠠࠣࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠦ࠿ࠦࡻࠣࡰࡤࡱࡪࠨ࠺ࠡࠩన") + json.dumps(bstack11l1111111_opy_) + bstack11l1l_opy_ (u"ࠬࢃࡽࠨ఩"))
    except Exception as e:
      logger.debug(bstack11l1l_opy_ (u"࠭ࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡶࡩࡹࠦࡳࡦࡵࡶ࡭ࡴࡴࠠ࡯ࡣࡰࡩࠥ࡯࡮ࠡࡤࡨࡪࡴࡸࡥࠡࡵࡷࡩࡵࡀࠠࡼࡿࠪప").format(str(e)))
@measure(event_name=EVENTS.bstack1l1lllll_opy_, stage=STAGE.bstack1lll1l11l_opy_, hook_type=bstack11l1l_opy_ (u"ࠢࡢࡨࡷࡩࡷ࡙ࡴࡦࡲࠥఫ"), bstack1l1l1llll_opy_=bstack11l1ll1l_opy_)
def bstack1ll1l11ll_opy_(runner, name, context, bstack1ll1llll1_opy_, *args):
  bstack11ll11l11l_opy_.bstack1l111111l1_opy_(args[0])
  try:
    step_status = args[0].status.name
    bstack1l1l1l11l1_opy_ = threading.current_thread().bstackSessionDriver if bstack11l1l_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫ࡔࡧࡶࡷ࡮ࡵ࡮ࡅࡴ࡬ࡺࡪࡸࠧబ") in threading.current_thread().__dict__.keys() else context.browser
    if is_driver_active(bstack1l1l1l11l1_opy_):
      if runner.driver_initialised is None:
        runner.driver_initialised  = bstack11l1l_opy_ (u"ࠩ࡬ࡲࡸࡺࡥࡱࠩభ")
        feature_name = bstack11l1111111_opy_ = str(runner.feature.name)
        bstack11l1111111_opy_ = feature_name + bstack11l1l_opy_ (u"ࠪࠤ࠲ࠦࠧమ") + context.scenario.name
        bstack1l1l1l11l1_opy_.execute_script(bstack11l1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡩࡽ࡫ࡣࡶࡶࡲࡶ࠿ࠦࡻࠣࡣࡦࡸ࡮ࡵ࡮ࠣ࠼ࠣࠦࡸ࡫ࡴࡔࡧࡶࡷ࡮ࡵ࡮ࡏࡣࡰࡩࠧ࠲ࠠࠣࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠦ࠿ࠦࡻࠣࡰࡤࡱࡪࠨ࠺ࠡࠩయ") + json.dumps(bstack11l1111111_opy_) + bstack11l1l_opy_ (u"ࠬࢃࡽࠨర"))
    if str(step_status).lower() == bstack11l1l_opy_ (u"࠭ࡦࡢ࡫࡯ࡩࡩ࠭ఱ"):
      bstack1l11l1llll_opy_ = bstack11l1l_opy_ (u"ࠧࠨల")
      bstack11l111l1_opy_ = bstack11l1l_opy_ (u"ࠨࠩళ")
      bstack1ll1ll11ll_opy_ = bstack11l1l_opy_ (u"ࠩࠪఴ")
      try:
        import traceback
        bstack1l11l1llll_opy_ = runner.exception.__class__.__name__
        bstack1l1llll111_opy_ = traceback.format_tb(runner.exc_traceback)
        bstack11l111l1_opy_ = bstack11l1l_opy_ (u"ࠪࠤࠬవ").join(bstack1l1llll111_opy_)
        bstack1ll1ll11ll_opy_ = bstack1l1llll111_opy_[-1]
      except Exception as e:
        logger.debug(bstack1l1ll1111_opy_.format(str(e)))
      bstack1l11l1llll_opy_ += bstack1ll1ll11ll_opy_
      bstack111llll1l1_opy_(context, json.dumps(str(args[0].name) + bstack11l1l_opy_ (u"ࠦࠥ࠳ࠠࡇࡣ࡬ࡰࡪࡪࠡ࡝ࡰࠥశ") + str(bstack11l111l1_opy_)),
                          bstack11l1l_opy_ (u"ࠧ࡫ࡲࡳࡱࡵࠦష"))
      if runner.driver_initialised == bstack11l1l_opy_ (u"ࠨࡢࡦࡨࡲࡶࡪࡥࡳࡵࡧࡳࠦస"):
        bstack11lll1lll1_opy_(getattr(context, bstack11l1l_opy_ (u"ࠧࡱࡣࡪࡩࠬహ"), None), bstack11l1l_opy_ (u"ࠣࡨࡤ࡭ࡱ࡫ࡤࠣ఺"), bstack1l11l1llll_opy_)
        bstack1l1l1l11l1_opy_.execute_script(bstack11l1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡧࡻࡩࡨࡻࡴࡰࡴ࠽ࠤࢀࠨࡡࡤࡶ࡬ࡳࡳࠨ࠺ࠡࠤࡤࡲࡳࡵࡴࡢࡶࡨࠦ࠱ࠦࠢࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠥ࠾ࠥࢁࠢࡥࡣࡷࡥࠧࡀࠧ఻") + json.dumps(str(args[0].name) + bstack11l1l_opy_ (u"ࠥࠤ࠲ࠦࡆࡢ࡫࡯ࡩࡩࠧ࡜࡯ࠤ఼") + str(bstack11l111l1_opy_)) + bstack11l1l_opy_ (u"ࠫ࠱ࠦࠢ࡭ࡧࡹࡩࡱࠨ࠺ࠡࠤࡨࡶࡷࡵࡲࠣࡿࢀࠫఽ"))
      if runner.driver_initialised == bstack11l1l_opy_ (u"ࠧࡨࡥࡧࡱࡵࡩࡤࡹࡴࡦࡲࠥా"):
        bstack111lllll1l_opy_(bstack1l1l1l11l1_opy_, bstack11l1l_opy_ (u"࠭ࡦࡢ࡫࡯ࡩࡩ࠭ి"), bstack11l1l_opy_ (u"ࠢࡔࡥࡨࡲࡦࡸࡩࡰࠢࡩࡥ࡮ࡲࡥࡥࠢࡺ࡭ࡹ࡮࠺ࠡ࡞ࡱࠦీ") + str(bstack1l11l1llll_opy_))
    else:
      bstack111llll1l1_opy_(context, bstack11l1l_opy_ (u"ࠣࡒࡤࡷࡸ࡫ࡤࠢࠤు"), bstack11l1l_opy_ (u"ࠤ࡬ࡲ࡫ࡵࠢూ"))
      if runner.driver_initialised == bstack11l1l_opy_ (u"ࠥࡦࡪ࡬࡯ࡳࡧࡢࡷࡹ࡫ࡰࠣృ"):
        bstack11lll1lll1_opy_(getattr(context, bstack11l1l_opy_ (u"ࠫࡵࡧࡧࡦࠩౄ"), None), bstack11l1l_opy_ (u"ࠧࡶࡡࡴࡵࡨࡨࠧ౅"))
      bstack1l1l1l11l1_opy_.execute_script(bstack11l1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤ࡫ࡸࡦࡥࡸࡸࡴࡸ࠺ࠡࡽࠥࡥࡨࡺࡩࡰࡰࠥ࠾ࠥࠨࡡ࡯ࡰࡲࡸࡦࡺࡥࠣ࠮ࠣࠦࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠢ࠻ࠢࡾࠦࡩࡧࡴࡢࠤ࠽ࠫె") + json.dumps(str(args[0].name) + bstack11l1l_opy_ (u"ࠢࠡ࠯ࠣࡔࡦࡹࡳࡦࡦࠤࠦే")) + bstack11l1l_opy_ (u"ࠨ࠮ࠣࠦࡱ࡫ࡶࡦ࡮ࠥ࠾ࠥࠨࡩ࡯ࡨࡲࠦࢂࢃࠧై"))
      if runner.driver_initialised == bstack11l1l_opy_ (u"ࠤࡥࡩ࡫ࡵࡲࡦࡡࡶࡸࡪࡶࠢ౉"):
        bstack111lllll1l_opy_(bstack1l1l1l11l1_opy_, bstack11l1l_opy_ (u"ࠥࡴࡦࡹࡳࡦࡦࠥొ"))
  except Exception as e:
    logger.debug(bstack11l1l_opy_ (u"ࠫࡋࡧࡩ࡭ࡧࡧࠤࡹࡵࠠ࡮ࡣࡵ࡯ࠥࡹࡥࡴࡵ࡬ࡳࡳࠦࡳࡵࡣࡷࡹࡸࠦࡩ࡯ࠢࡤࡪࡹ࡫ࡲࠡࡵࡷࡩࡵࡀࠠࡼࡿࠪో").format(str(e)))
  bstack1ll1l111ll_opy_(runner, name, context, args[0], bstack1ll1llll1_opy_, *args)
@measure(event_name=EVENTS.bstack1lll11lll1_opy_, stage=STAGE.bstack1lll1l11l_opy_, bstack1l1l1llll_opy_=bstack11l1ll1l_opy_)
def bstack111ll11l1_opy_(runner, name, context, bstack1ll1llll1_opy_, *args):
  bstack11ll11l11l_opy_.end_test(args[0])
  try:
    bstack1l11lll11_opy_ = args[0].status.name
    bstack1l1l1l11l1_opy_ = bstack11lll11l_opy_(threading.current_thread(), bstack11l1l_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯ࡘ࡫ࡳࡴ࡫ࡲࡲࡉࡸࡩࡷࡧࡵࠫౌ"), context.browser)
    bstack111lllll11_opy_.bstack1l11llllll_opy_(bstack1l1l1l11l1_opy_)
    if str(bstack1l11lll11_opy_).lower() == bstack11l1l_opy_ (u"࠭ࡦࡢ࡫࡯ࡩࡩ్࠭"):
      bstack1l11l1llll_opy_ = bstack11l1l_opy_ (u"ࠧࠨ౎")
      bstack11l111l1_opy_ = bstack11l1l_opy_ (u"ࠨࠩ౏")
      bstack1ll1ll11ll_opy_ = bstack11l1l_opy_ (u"ࠩࠪ౐")
      try:
        import traceback
        bstack1l11l1llll_opy_ = runner.exception.__class__.__name__
        bstack1l1llll111_opy_ = traceback.format_tb(runner.exc_traceback)
        bstack11l111l1_opy_ = bstack11l1l_opy_ (u"ࠪࠤࠬ౑").join(bstack1l1llll111_opy_)
        bstack1ll1ll11ll_opy_ = bstack1l1llll111_opy_[-1]
      except Exception as e:
        logger.debug(bstack1l1ll1111_opy_.format(str(e)))
      bstack1l11l1llll_opy_ += bstack1ll1ll11ll_opy_
      bstack111llll1l1_opy_(context, json.dumps(str(args[0].name) + bstack11l1l_opy_ (u"ࠦࠥ࠳ࠠࡇࡣ࡬ࡰࡪࡪࠡ࡝ࡰࠥ౒") + str(bstack11l111l1_opy_)),
                          bstack11l1l_opy_ (u"ࠧ࡫ࡲࡳࡱࡵࠦ౓"))
      if runner.driver_initialised == bstack11l1l_opy_ (u"ࠨࡢࡦࡨࡲࡶࡪࡥࡳࡤࡧࡱࡥࡷ࡯࡯ࠣ౔") or runner.driver_initialised == bstack11l1l_opy_ (u"ࠧࡪࡰࡶࡸࡪࡶౕࠧ"):
        bstack11lll1lll1_opy_(getattr(context, bstack11l1l_opy_ (u"ࠨࡲࡤ࡫ࡪౖ࠭"), None), bstack11l1l_opy_ (u"ࠤࡩࡥ࡮ࡲࡥࡥࠤ౗"), bstack1l11l1llll_opy_)
        bstack1l1l1l11l1_opy_.execute_script(bstack11l1l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡨࡼࡪࡩࡵࡵࡱࡵ࠾ࠥࢁࠢࡢࡥࡷ࡭ࡴࡴࠢ࠻ࠢࠥࡥࡳࡴ࡯ࡵࡣࡷࡩࠧ࠲ࠠࠣࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠦ࠿ࠦࡻࠣࡦࡤࡸࡦࠨ࠺ࠨౘ") + json.dumps(str(args[0].name) + bstack11l1l_opy_ (u"ࠦࠥ࠳ࠠࡇࡣ࡬ࡰࡪࡪࠡ࡝ࡰࠥౙ") + str(bstack11l111l1_opy_)) + bstack11l1l_opy_ (u"ࠬ࠲ࠠࠣ࡮ࡨࡺࡪࡲࠢ࠻ࠢࠥࡩࡷࡸ࡯ࡳࠤࢀࢁࠬౚ"))
      if runner.driver_initialised == bstack11l1l_opy_ (u"ࠨࡢࡦࡨࡲࡶࡪࡥࡳࡤࡧࡱࡥࡷ࡯࡯ࠣ౛") or runner.driver_initialised == bstack11l1l_opy_ (u"ࠧࡪࡰࡶࡸࡪࡶࠧ౜"):
        bstack111lllll1l_opy_(bstack1l1l1l11l1_opy_, bstack11l1l_opy_ (u"ࠨࡨࡤ࡭ࡱ࡫ࡤࠨౝ"), bstack11l1l_opy_ (u"ࠤࡖࡧࡪࡴࡡࡳ࡫ࡲࠤ࡫ࡧࡩ࡭ࡧࡧࠤࡼ࡯ࡴࡩ࠼ࠣࡠࡳࠨ౞") + str(bstack1l11l1llll_opy_))
    else:
      bstack111llll1l1_opy_(context, bstack11l1l_opy_ (u"ࠥࡔࡦࡹࡳࡦࡦࠤࠦ౟"), bstack11l1l_opy_ (u"ࠦ࡮ࡴࡦࡰࠤౠ"))
      if runner.driver_initialised == bstack11l1l_opy_ (u"ࠧࡨࡥࡧࡱࡵࡩࡤࡹࡣࡦࡰࡤࡶ࡮ࡵࠢౡ") or runner.driver_initialised == bstack11l1l_opy_ (u"࠭ࡩ࡯ࡵࡷࡩࡵ࠭ౢ"):
        bstack11lll1lll1_opy_(getattr(context, bstack11l1l_opy_ (u"ࠧࡱࡣࡪࡩࠬౣ"), None), bstack11l1l_opy_ (u"ࠣࡲࡤࡷࡸ࡫ࡤࠣ౤"))
      bstack1l1l1l11l1_opy_.execute_script(bstack11l1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡧࡻࡩࡨࡻࡴࡰࡴ࠽ࠤࢀࠨࡡࡤࡶ࡬ࡳࡳࠨ࠺ࠡࠤࡤࡲࡳࡵࡴࡢࡶࡨࠦ࠱ࠦࠢࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠥ࠾ࠥࢁࠢࡥࡣࡷࡥࠧࡀࠧ౥") + json.dumps(str(args[0].name) + bstack11l1l_opy_ (u"ࠥࠤ࠲ࠦࡐࡢࡵࡶࡩࡩࠧࠢ౦")) + bstack11l1l_opy_ (u"ࠫ࠱ࠦࠢ࡭ࡧࡹࡩࡱࠨ࠺ࠡࠤ࡬ࡲ࡫ࡵࠢࡾࡿࠪ౧"))
      if runner.driver_initialised == bstack11l1l_opy_ (u"ࠧࡨࡥࡧࡱࡵࡩࡤࡹࡣࡦࡰࡤࡶ࡮ࡵࠢ౨") or runner.driver_initialised == bstack11l1l_opy_ (u"࠭ࡩ࡯ࡵࡷࡩࡵ࠭౩"):
        bstack111lllll1l_opy_(bstack1l1l1l11l1_opy_, bstack11l1l_opy_ (u"ࠢࡱࡣࡶࡷࡪࡪࠢ౪"))
  except Exception as e:
    logger.debug(bstack11l1l_opy_ (u"ࠨࡈࡤ࡭ࡱ࡫ࡤࠡࡶࡲࠤࡲࡧࡲ࡬ࠢࡶࡩࡸࡹࡩࡰࡰࠣࡷࡹࡧࡴࡶࡵࠣ࡭ࡳࠦࡡࡧࡶࡨࡶࠥ࡬ࡥࡢࡶࡸࡶࡪࡀࠠࡼࡿࠪ౫").format(str(e)))
  bstack1ll1l111ll_opy_(runner, name, context, context.scenario, bstack1ll1llll1_opy_, *args)
  if len(context.scenario.tags) == 0: threading.current_thread().current_test_uuid = None
def bstack111ll1ll1_opy_(runner, name, context, bstack1ll1llll1_opy_, *args):
    target = context.scenario if hasattr(context, bstack11l1l_opy_ (u"ࠩࡶࡧࡪࡴࡡࡳ࡫ࡲࠫ౬")) else context.feature
    bstack1ll1l111ll_opy_(runner, name, context, target, bstack1ll1llll1_opy_, *args)
    threading.current_thread().current_test_uuid = None
def bstack1l1ll11lll_opy_(runner, name, context, bstack1ll1llll1_opy_, *args):
    try:
      bstack1l1l1l11l1_opy_ = bstack11lll11l_opy_(threading.current_thread(), bstack11l1l_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭ࡖࡩࡸࡹࡩࡰࡰࡇࡶ࡮ࡼࡥࡳࠩ౭"), context.browser)
      bstack1l1ll11l11_opy_ = bstack11l1l_opy_ (u"ࠫࠬ౮")
      if context.failed is True:
        bstack1ll1ll11l_opy_ = []
        bstack11ll111ll1_opy_ = []
        bstack1l11ll11l1_opy_ = []
        try:
          import traceback
          for exc in runner.exception_arr:
            bstack1ll1ll11l_opy_.append(exc.__class__.__name__)
          for exc_tb in runner.exc_traceback_arr:
            bstack1l1llll111_opy_ = traceback.format_tb(exc_tb)
            bstack1l1l1l1ll_opy_ = bstack11l1l_opy_ (u"ࠬࠦࠧ౯").join(bstack1l1llll111_opy_)
            bstack11ll111ll1_opy_.append(bstack1l1l1l1ll_opy_)
            bstack1l11ll11l1_opy_.append(bstack1l1llll111_opy_[-1])
        except Exception as e:
          logger.debug(bstack1l1ll1111_opy_.format(str(e)))
        bstack1l11l1llll_opy_ = bstack11l1l_opy_ (u"࠭ࠧ౰")
        for i in range(len(bstack1ll1ll11l_opy_)):
          bstack1l11l1llll_opy_ += bstack1ll1ll11l_opy_[i] + bstack1l11ll11l1_opy_[i] + bstack11l1l_opy_ (u"ࠧ࡝ࡰࠪ౱")
        bstack1l1ll11l11_opy_ = bstack11l1l_opy_ (u"ࠨࠢࠪ౲").join(bstack11ll111ll1_opy_)
        if runner.driver_initialised in [bstack11l1l_opy_ (u"ࠤࡥࡩ࡫ࡵࡲࡦࡡࡩࡩࡦࡺࡵࡳࡧࠥ౳"), bstack11l1l_opy_ (u"ࠥࡦࡪ࡬࡯ࡳࡧࡢࡥࡱࡲࠢ౴")]:
          bstack111llll1l1_opy_(context, bstack1l1ll11l11_opy_, bstack11l1l_opy_ (u"ࠦࡪࡸࡲࡰࡴࠥ౵"))
          bstack11lll1lll1_opy_(getattr(context, bstack11l1l_opy_ (u"ࠬࡶࡡࡨࡧࠪ౶"), None), bstack11l1l_opy_ (u"ࠨࡦࡢ࡫࡯ࡩࡩࠨ౷"), bstack1l11l1llll_opy_)
          bstack1l1l1l11l1_opy_.execute_script(bstack11l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡥࡹࡧࡦࡹࡹࡵࡲ࠻ࠢࡾࠦࡦࡩࡴࡪࡱࡱࠦ࠿ࠦࠢࡢࡰࡱࡳࡹࡧࡴࡦࠤ࠯ࠤࠧࡧࡲࡨࡷࡰࡩࡳࡺࡳࠣ࠼ࠣࡿࠧࡪࡡࡵࡣࠥ࠾ࠬ౸") + json.dumps(bstack1l1ll11l11_opy_) + bstack11l1l_opy_ (u"ࠨ࠮ࠣࠦࡱ࡫ࡶࡦ࡮ࠥ࠾ࠥࠨࡥࡳࡴࡲࡶࠧࢃࡽࠨ౹"))
          bstack111lllll1l_opy_(bstack1l1l1l11l1_opy_, bstack11l1l_opy_ (u"ࠤࡩࡥ࡮ࡲࡥࡥࠤ౺"), bstack11l1l_opy_ (u"ࠥࡗࡴࡳࡥࠡࡵࡦࡩࡳࡧࡲࡪࡱࡶࠤ࡫ࡧࡩ࡭ࡧࡧ࠾ࠥࡢ࡮ࠣ౻") + str(bstack1l11l1llll_opy_))
          bstack11ll1ll1l1_opy_ = bstack1l1111l1ll_opy_(bstack1l1ll11l11_opy_, runner.feature.name, logger)
          if (bstack11ll1ll1l1_opy_ != None):
            bstack11111l1l1_opy_.append(bstack11ll1ll1l1_opy_)
      else:
        if runner.driver_initialised in [bstack11l1l_opy_ (u"ࠦࡧ࡫ࡦࡰࡴࡨࡣ࡫࡫ࡡࡵࡷࡵࡩࠧ౼"), bstack11l1l_opy_ (u"ࠧࡨࡥࡧࡱࡵࡩࡤࡧ࡬࡭ࠤ౽")]:
          bstack111llll1l1_opy_(context, bstack11l1l_opy_ (u"ࠨࡆࡦࡣࡷࡹࡷ࡫࠺ࠡࠤ౾") + str(runner.feature.name) + bstack11l1l_opy_ (u"ࠢࠡࡲࡤࡷࡸ࡫ࡤࠢࠤ౿"), bstack11l1l_opy_ (u"ࠣ࡫ࡱࡪࡴࠨಀ"))
          bstack11lll1lll1_opy_(getattr(context, bstack11l1l_opy_ (u"ࠩࡳࡥ࡬࡫ࠧಁ"), None), bstack11l1l_opy_ (u"ࠥࡴࡦࡹࡳࡦࡦࠥಂ"))
          bstack1l1l1l11l1_opy_.execute_script(bstack11l1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡩࡽ࡫ࡣࡶࡶࡲࡶ࠿ࠦࡻࠣࡣࡦࡸ࡮ࡵ࡮ࠣ࠼ࠣࠦࡦࡴ࡮ࡰࡶࡤࡸࡪࠨࠬࠡࠤࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠧࡀࠠࡼࠤࡧࡥࡹࡧࠢ࠻ࠩಃ") + json.dumps(bstack11l1l_opy_ (u"ࠧࡌࡥࡢࡶࡸࡶࡪࡀࠠࠣ಄") + str(runner.feature.name) + bstack11l1l_opy_ (u"ࠨࠠࡱࡣࡶࡷࡪࡪࠡࠣಅ")) + bstack11l1l_opy_ (u"ࠧ࠭ࠢࠥࡰࡪࡼࡥ࡭ࠤ࠽ࠤࠧ࡯࡮ࡧࡱࠥࢁࢂ࠭ಆ"))
          bstack111lllll1l_opy_(bstack1l1l1l11l1_opy_, bstack11l1l_opy_ (u"ࠨࡲࡤࡷࡸ࡫ࡤࠨಇ"))
          bstack11ll1ll1l1_opy_ = bstack1l1111l1ll_opy_(bstack1l1ll11l11_opy_, runner.feature.name, logger)
          if (bstack11ll1ll1l1_opy_ != None):
            bstack11111l1l1_opy_.append(bstack11ll1ll1l1_opy_)
    except Exception as e:
      logger.debug(bstack11l1l_opy_ (u"ࠩࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥࡳࡡࡳ࡭ࠣࡷࡪࡹࡳࡪࡱࡱࠤࡸࡺࡡࡵࡷࡶࠤ࡮ࡴࠠࡢࡨࡷࡩࡷࠦࡦࡦࡣࡷࡹࡷ࡫࠺ࠡࡽࢀࠫಈ").format(str(e)))
    bstack1ll1l111ll_opy_(runner, name, context, context.feature, bstack1ll1llll1_opy_, *args)
@measure(event_name=EVENTS.bstack1l1lllll_opy_, stage=STAGE.bstack1lll1l11l_opy_, hook_type=bstack11l1l_opy_ (u"ࠥࡥ࡫ࡺࡥࡳࡃ࡯ࡰࠧಉ"), bstack1l1l1llll_opy_=bstack11l1ll1l_opy_)
def bstack1111lll1_opy_(runner, name, context, bstack1ll1llll1_opy_, *args):
    bstack1ll1l111ll_opy_(runner, name, context, runner, bstack1ll1llll1_opy_, *args)
def bstack11l11lll_opy_(self, name, context, *args):
  try:
    if bstack11ll1l1lll_opy_:
      platform_index = int(threading.current_thread()._name) % bstack1ll1ll1lll_opy_
      bstack1l11111l_opy_ = CONFIG[bstack11l1l_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧಊ")][platform_index]
      os.environ[bstack11l1l_opy_ (u"ࠬࡉࡕࡓࡔࡈࡒ࡙ࡥࡐࡍࡃࡗࡊࡔࡘࡍࡠࡆࡄࡘࡆ࠭ಋ")] = json.dumps(bstack1l11111l_opy_)
    global bstack1ll1llll1_opy_
    if not hasattr(self, bstack11l1l_opy_ (u"࠭ࡤࡳ࡫ࡹࡩࡷࡥࡩ࡯࡫ࡷ࡭ࡦࡲࡩࡴࡧࡧࠫಌ")):
      self.driver_initialised = None
    bstack1111llll_opy_ = {
        bstack11l1l_opy_ (u"ࠧࡣࡧࡩࡳࡷ࡫࡟ࡢ࡮࡯ࠫ಍"): bstack1l111l11l_opy_,
        bstack11l1l_opy_ (u"ࠨࡤࡨࡪࡴࡸࡥࡠࡨࡨࡥࡹࡻࡲࡦࠩಎ"): bstack1l1l111l_opy_,
        bstack11l1l_opy_ (u"ࠩࡥࡩ࡫ࡵࡲࡦࡡࡷࡥ࡬࠭ಏ"): bstack1l1l1111ll_opy_,
        bstack11l1l_opy_ (u"ࠪࡦࡪ࡬࡯ࡳࡧࡢࡷࡨ࡫࡮ࡢࡴ࡬ࡳࠬಐ"): bstack1ll111l11l_opy_,
        bstack11l1l_opy_ (u"ࠫࡧ࡫ࡦࡰࡴࡨࡣࡸࡺࡥࡱࠩ಑"): bstack1ll1l11l1_opy_,
        bstack11l1l_opy_ (u"ࠬࡧࡦࡵࡧࡵࡣࡸࡺࡥࡱࠩಒ"): bstack1ll1l11ll_opy_,
        bstack11l1l_opy_ (u"࠭ࡡࡧࡶࡨࡶࡤࡹࡣࡦࡰࡤࡶ࡮ࡵࠧಓ"): bstack111ll11l1_opy_,
        bstack11l1l_opy_ (u"ࠧࡢࡨࡷࡩࡷࡥࡴࡢࡩࠪಔ"): bstack111ll1ll1_opy_,
        bstack11l1l_opy_ (u"ࠨࡣࡩࡸࡪࡸ࡟ࡧࡧࡤࡸࡺࡸࡥࠨಕ"): bstack1l1ll11lll_opy_,
        bstack11l1l_opy_ (u"ࠩࡤࡪࡹ࡫ࡲࡠࡣ࡯ࡰࠬಖ"): bstack1111lll1_opy_
    }
    handler = bstack1111llll_opy_.get(name, bstack1ll1llll1_opy_)
    try:
      handler(self, name, context, bstack1ll1llll1_opy_, *args)
    except Exception as e:
      logger.debug(bstack11l1l_opy_ (u"ࠪࡉࡷࡸ࡯ࡳࠢ࡬ࡲࠥࡨࡥࡩࡣࡹࡩࠥ࡮࡯ࡰ࡭ࠣ࡬ࡦࡴࡤ࡭ࡧࡵࠤࢀࢃ࠺ࠡࡽࢀࠫಗ").format(name, str(e)))
    if name in [bstack11l1l_opy_ (u"ࠫࡦ࡬ࡴࡦࡴࡢࡪࡪࡧࡴࡶࡴࡨࠫಘ"), bstack11l1l_opy_ (u"ࠬࡧࡦࡵࡧࡵࡣࡸࡩࡥ࡯ࡣࡵ࡭ࡴ࠭ಙ"), bstack11l1l_opy_ (u"࠭ࡡࡧࡶࡨࡶࡤࡧ࡬࡭ࠩಚ")]:
      try:
        bstack1l1l1l11l1_opy_ = threading.current_thread().bstackSessionDriver if bstack111llll111_opy_(bstack11l1l_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱࡓࡦࡵࡶ࡭ࡴࡴࡄࡳ࡫ࡹࡩࡷ࠭ಛ")) else context.browser
        bstack1l1111111_opy_ = (
          (name == bstack11l1l_opy_ (u"ࠨࡣࡩࡸࡪࡸ࡟ࡢ࡮࡯ࠫಜ") and self.driver_initialised == bstack11l1l_opy_ (u"ࠤࡥࡩ࡫ࡵࡲࡦࡡࡤࡰࡱࠨಝ")) or
          (name == bstack11l1l_opy_ (u"ࠪࡥ࡫ࡺࡥࡳࡡࡩࡩࡦࡺࡵࡳࡧࠪಞ") and self.driver_initialised == bstack11l1l_opy_ (u"ࠦࡧ࡫ࡦࡰࡴࡨࡣ࡫࡫ࡡࡵࡷࡵࡩࠧಟ")) or
          (name == bstack11l1l_opy_ (u"ࠬࡧࡦࡵࡧࡵࡣࡸࡩࡥ࡯ࡣࡵ࡭ࡴ࠭ಠ") and self.driver_initialised in [bstack11l1l_opy_ (u"ࠨࡢࡦࡨࡲࡶࡪࡥࡳࡤࡧࡱࡥࡷ࡯࡯ࠣಡ"), bstack11l1l_opy_ (u"ࠢࡪࡰࡶࡸࡪࡶࠢಢ")]) or
          (name == bstack11l1l_opy_ (u"ࠨࡣࡩࡸࡪࡸ࡟ࡴࡶࡨࡴࠬಣ") and self.driver_initialised == bstack11l1l_opy_ (u"ࠤࡥࡩ࡫ࡵࡲࡦࡡࡶࡸࡪࡶࠢತ"))
        )
        if bstack1l1111111_opy_:
          self.driver_initialised = None
          if bstack1l1l1l11l1_opy_ and hasattr(bstack1l1l1l11l1_opy_, bstack11l1l_opy_ (u"ࠪࡷࡪࡹࡳࡪࡱࡱࡣ࡮ࡪࠧಥ")):
            try:
              bstack1l1l1l11l1_opy_.quit()
            except Exception as e:
              logger.debug(bstack11l1l_opy_ (u"ࠫࡊࡸࡲࡰࡴࠣࡵࡺ࡯ࡴࡵ࡫ࡱ࡫ࠥࡪࡲࡪࡸࡨࡶࠥ࡯࡮ࠡࡤࡨ࡬ࡦࡼࡥࠡࡪࡲࡳࡰࡀࠠࡼࡿࠪದ").format(str(e)))
      except Exception as e:
        logger.debug(bstack11l1l_opy_ (u"ࠬࡋࡲࡳࡱࡵࠤ࡮ࡴࠠࡢࡨࡷࡩࡷࠦࡨࡰࡱ࡮ࠤࡨࡲࡥࡢࡰࡸࡴࠥ࡬࡯ࡳࠢࡾࢁ࠿ࠦࡻࡾࠩಧ").format(name, str(e)))
  except Exception as e:
    logger.debug(bstack11l1l_opy_ (u"࠭ࡃࡳ࡫ࡷ࡭ࡨࡧ࡬ࠡࡧࡵࡶࡴࡸࠠࡪࡰࠣࡦࡪ࡮ࡡࡷࡧࠣࡶࡺࡴࠠࡩࡱࡲ࡯ࠥࢁࡽ࠻ࠢࡾࢁࠬನ").format(name, str(e)))
    try:
      bstack1ll1llll1_opy_(self, name, context, *args)
    except Exception as e2:
      logger.debug(bstack11l1l_opy_ (u"ࠧࡆࡴࡵࡳࡷࠦࡩ࡯ࠢࡩࡥࡱࡲࡢࡢࡥ࡮ࠤࡴࡸࡩࡨ࡫ࡱࡥࡱࠦࡢࡦࡪࡤࡺࡪࠦࡨࡰࡱ࡮ࠤࢀࢃ࠺ࠡࡽࢀࠫ಩").format(name, str(e2)))
def bstack11lll11l1l_opy_(config, startdir):
  return bstack11l1l_opy_ (u"ࠣࡦࡵ࡭ࡻ࡫ࡲ࠻ࠢࡾ࠴ࢂࠨಪ").format(bstack11l1l_opy_ (u"ࠤࡅࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࠣಫ"))
notset = Notset()
def bstack11ll1l11ll_opy_(self, name: str, default=notset, skip: bool = False):
  global bstack1lll1l1ll_opy_
  if str(name).lower() == bstack11l1l_opy_ (u"ࠪࡨࡷ࡯ࡶࡦࡴࠪಬ"):
    return bstack11l1l_opy_ (u"ࠦࡇࡸ࡯ࡸࡵࡨࡶࡘࡺࡡࡤ࡭ࠥಭ")
  else:
    return bstack1lll1l1ll_opy_(self, name, default, skip)
def bstack1ll11l1l_opy_(item, when):
  global bstack11l1ll11l1_opy_
  try:
    bstack11l1ll11l1_opy_(item, when)
  except Exception as e:
    pass
def bstack1l111lllll_opy_():
  return
def bstack1lll11ll1_opy_(type, name, status, reason, bstack11ll1ll11l_opy_, bstack1l1l1ll111_opy_):
  bstack1ll111lll1_opy_ = {
    bstack11l1l_opy_ (u"ࠬࡧࡣࡵ࡫ࡲࡲࠬಮ"): type,
    bstack11l1l_opy_ (u"࠭ࡡࡳࡩࡸࡱࡪࡴࡴࡴࠩಯ"): {}
  }
  if type == bstack11l1l_opy_ (u"ࠧࡢࡰࡱࡳࡹࡧࡴࡦࠩರ"):
    bstack1ll111lll1_opy_[bstack11l1l_opy_ (u"ࠨࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠫಱ")][bstack11l1l_opy_ (u"ࠩ࡯ࡩࡻ࡫࡬ࠨಲ")] = bstack11ll1ll11l_opy_
    bstack1ll111lll1_opy_[bstack11l1l_opy_ (u"ࠪࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸ࠭ಳ")][bstack11l1l_opy_ (u"ࠫࡩࡧࡴࡢࠩ಴")] = json.dumps(str(bstack1l1l1ll111_opy_))
  if type == bstack11l1l_opy_ (u"ࠬࡹࡥࡵࡕࡨࡷࡸ࡯࡯࡯ࡐࡤࡱࡪ࠭ವ"):
    bstack1ll111lll1_opy_[bstack11l1l_opy_ (u"࠭ࡡࡳࡩࡸࡱࡪࡴࡴࡴࠩಶ")][bstack11l1l_opy_ (u"ࠧ࡯ࡣࡰࡩࠬಷ")] = name
  if type == bstack11l1l_opy_ (u"ࠨࡵࡨࡸࡘ࡫ࡳࡴ࡫ࡲࡲࡘࡺࡡࡵࡷࡶࠫಸ"):
    bstack1ll111lll1_opy_[bstack11l1l_opy_ (u"ࠩࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠬಹ")][bstack11l1l_opy_ (u"ࠪࡷࡹࡧࡴࡶࡵࠪ಺")] = status
    if status == bstack11l1l_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡧࡧࠫ಻"):
      bstack1ll111lll1_opy_[bstack11l1l_opy_ (u"ࠬࡧࡲࡨࡷࡰࡩࡳࡺࡳࠨ಼")][bstack11l1l_opy_ (u"࠭ࡲࡦࡣࡶࡳࡳ࠭ಽ")] = json.dumps(str(reason))
  bstack11lllll1ll_opy_ = bstack11l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡥࡹࡧࡦࡹࡹࡵࡲ࠻ࠢࡾࢁࠬಾ").format(json.dumps(bstack1ll111lll1_opy_))
  return bstack11lllll1ll_opy_
def bstack1l1ll1ll1l_opy_(driver_command, response):
    if driver_command == bstack11l1l_opy_ (u"ࠨࡵࡦࡶࡪ࡫࡮ࡴࡪࡲࡸࠬಿ"):
        bstack1ll1llll11_opy_.bstack1l1lll111l_opy_({
            bstack11l1l_opy_ (u"ࠩ࡬ࡱࡦ࡭ࡥࠨೀ"): response[bstack11l1l_opy_ (u"ࠪࡺࡦࡲࡵࡦࠩು")],
            bstack11l1l_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡵࡹࡳࡥࡵࡶ࡫ࡧࠫೂ"): bstack1ll1llll11_opy_.current_test_uuid()
        })
def bstack1111ll11_opy_(item, call, rep):
  global bstack1ll1l11l11_opy_
  global bstack1ll111111l_opy_
  global bstack1lllllll1_opy_
  name = bstack11l1l_opy_ (u"ࠬ࠭ೃ")
  try:
    if rep.when == bstack11l1l_opy_ (u"࠭ࡣࡢ࡮࡯ࠫೄ"):
      bstack1ll1llll1l_opy_ = threading.current_thread().bstackSessionId
      try:
        if not bstack1lllllll1_opy_:
          name = str(rep.nodeid)
          bstack1lll1l111_opy_ = bstack1lll11ll1_opy_(bstack11l1l_opy_ (u"ࠧࡴࡧࡷࡗࡪࡹࡳࡪࡱࡱࡒࡦࡳࡥࠨ೅"), name, bstack11l1l_opy_ (u"ࠨࠩೆ"), bstack11l1l_opy_ (u"ࠩࠪೇ"), bstack11l1l_opy_ (u"ࠪࠫೈ"), bstack11l1l_opy_ (u"ࠫࠬ೉"))
          threading.current_thread().bstack11ll11l1_opy_ = name
          for driver in bstack1ll111111l_opy_:
            if bstack1ll1llll1l_opy_ == driver.session_id:
              driver.execute_script(bstack1lll1l111_opy_)
      except Exception as e:
        logger.debug(bstack11l1l_opy_ (u"ࠬࡋࡲࡳࡱࡵࠤ࡮ࡴࠠࡴࡧࡷࡸ࡮ࡴࡧࠡࡵࡨࡷࡸ࡯࡯࡯ࡐࡤࡱࡪࠦࡦࡰࡴࠣࡴࡾࡺࡥࡴࡶ࠰ࡦࡩࡪࠠࡴࡧࡶࡷ࡮ࡵ࡮࠻ࠢࡾࢁࠬೊ").format(str(e)))
      try:
        bstack11ll1ll1_opy_(rep.outcome.lower())
        if rep.outcome.lower() != bstack11l1l_opy_ (u"࠭ࡳ࡬࡫ࡳࡴࡪࡪࠧೋ"):
          status = bstack11l1l_opy_ (u"ࠧࡧࡣ࡬ࡰࡪࡪࠧೌ") if rep.outcome.lower() == bstack11l1l_opy_ (u"ࠨࡨࡤ࡭ࡱ࡫ࡤࠨ್") else bstack11l1l_opy_ (u"ࠩࡳࡥࡸࡹࡥࡥࠩ೎")
          reason = bstack11l1l_opy_ (u"ࠪࠫ೏")
          if status == bstack11l1l_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡧࡧࠫ೐"):
            reason = rep.longrepr.reprcrash.message
            if (not threading.current_thread().bstackTestErrorMessages):
              threading.current_thread().bstackTestErrorMessages = []
            threading.current_thread().bstackTestErrorMessages.append(reason)
          level = bstack11l1l_opy_ (u"ࠬ࡯࡮ࡧࡱࠪ೑") if status == bstack11l1l_opy_ (u"࠭ࡰࡢࡵࡶࡩࡩ࠭೒") else bstack11l1l_opy_ (u"ࠧࡦࡴࡵࡳࡷ࠭೓")
          data = name + bstack11l1l_opy_ (u"ࠨࠢࡳࡥࡸࡹࡥࡥࠣࠪ೔") if status == bstack11l1l_opy_ (u"ࠩࡳࡥࡸࡹࡥࡥࠩೕ") else name + bstack11l1l_opy_ (u"ࠪࠤ࡫ࡧࡩ࡭ࡧࡧࠥࠥ࠭ೖ") + reason
          bstack11l1111l1_opy_ = bstack1lll11ll1_opy_(bstack11l1l_opy_ (u"ࠫࡦࡴ࡮ࡰࡶࡤࡸࡪ࠭೗"), bstack11l1l_opy_ (u"ࠬ࠭೘"), bstack11l1l_opy_ (u"࠭ࠧ೙"), bstack11l1l_opy_ (u"ࠧࠨ೚"), level, data)
          for driver in bstack1ll111111l_opy_:
            if bstack1ll1llll1l_opy_ == driver.session_id:
              driver.execute_script(bstack11l1111l1_opy_)
      except Exception as e:
        logger.debug(bstack11l1l_opy_ (u"ࠨࡇࡵࡶࡴࡸࠠࡪࡰࠣࡷࡪࡺࡴࡪࡰࡪࠤࡸ࡫ࡳࡴ࡫ࡲࡲࠥࡩ࡯࡯ࡶࡨࡼࡹࠦࡦࡰࡴࠣࡴࡾࡺࡥࡴࡶ࠰ࡦࡩࡪࠠࡴࡧࡶࡷ࡮ࡵ࡮࠻ࠢࡾࢁࠬ೛").format(str(e)))
  except Exception as e:
    logger.debug(bstack11l1l_opy_ (u"ࠩࡈࡶࡷࡵࡲࠡ࡫ࡱࠤ࡬࡫ࡴࡵ࡫ࡱ࡫ࠥࡹࡴࡢࡶࡨࠤ࡮ࡴࠠࡱࡻࡷࡩࡸࡺ࠭ࡣࡦࡧࠤࡹ࡫ࡳࡵࠢࡶࡸࡦࡺࡵࡴ࠼ࠣࡿࢂ࠭೜").format(str(e)))
  bstack1ll1l11l11_opy_(item, call, rep)
def bstack1l111l1111_opy_(driver, bstack11l11lll11_opy_, test=None):
  global bstack11ll1111ll_opy_
  if test != None:
    bstack11111111l_opy_ = getattr(test, bstack11l1l_opy_ (u"ࠪࡲࡦࡳࡥࠨೝ"), None)
    bstack11l1l11l1l_opy_ = getattr(test, bstack11l1l_opy_ (u"ࠫࡺࡻࡩࡥࠩೞ"), None)
    PercySDK.screenshot(driver, bstack11l11lll11_opy_, bstack11111111l_opy_=bstack11111111l_opy_, bstack11l1l11l1l_opy_=bstack11l1l11l1l_opy_, bstack1ll11l1lll_opy_=bstack11ll1111ll_opy_)
  else:
    PercySDK.screenshot(driver, bstack11l11lll11_opy_)
@measure(event_name=EVENTS.bstack11l1l11lll_opy_, stage=STAGE.bstack1lll1l11l_opy_, bstack1l1l1llll_opy_=bstack11l1ll1l_opy_)
def bstack1ll111llll_opy_(driver):
  if bstack1lllll1ll1_opy_.bstack1l1l11l1l1_opy_() is True or bstack1lllll1ll1_opy_.capturing() is True:
    return
  bstack1lllll1ll1_opy_.bstack11lll1ll_opy_()
  while not bstack1lllll1ll1_opy_.bstack1l1l11l1l1_opy_():
    bstack1ll1111111_opy_ = bstack1lllll1ll1_opy_.bstack11l1ll11l_opy_()
    bstack1l111l1111_opy_(driver, bstack1ll1111111_opy_)
  bstack1lllll1ll1_opy_.bstack1111l1111_opy_()
def bstack1llll1l1ll_opy_(sequence, driver_command, response = None, bstack11ll11ll11_opy_ = None, args = None):
    try:
      if sequence != bstack11l1l_opy_ (u"ࠬࡨࡥࡧࡱࡵࡩࠬ೟"):
        return
      if percy.bstack1llll111l_opy_() == bstack11l1l_opy_ (u"ࠨࡦࡢ࡮ࡶࡩࠧೠ"):
        return
      bstack1ll1111111_opy_ = bstack11lll11l_opy_(threading.current_thread(), bstack11l1l_opy_ (u"ࠧࡱࡧࡵࡧࡾ࡙ࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧࠪೡ"), None)
      for command in bstack1l1l1llll1_opy_:
        if command == driver_command:
          with bstack1l1111ll_opy_:
            bstack1lll1ll1ll_opy_ = bstack1ll111111l_opy_.copy()
          for driver in bstack1lll1ll1ll_opy_:
            bstack1ll111llll_opy_(driver)
      bstack11l1l1ll1_opy_ = percy.bstack111llllll_opy_()
      if driver_command in bstack1111ll1l1_opy_[bstack11l1l1ll1_opy_]:
        bstack1lllll1ll1_opy_.bstack1l111lll11_opy_(bstack1ll1111111_opy_, driver_command)
    except Exception as e:
      pass
def bstack11l1lll1_opy_(framework_name):
  if bstack1l1ll11111_opy_.get_property(bstack11l1l_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫ࡠ࡯ࡲࡨࡤࡩࡡ࡭࡮ࡨࡨࠬೢ")):
      return
  bstack1l1ll11111_opy_.bstack1ll1111ll1_opy_(bstack11l1l_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬ࡡࡰࡳࡩࡥࡣࡢ࡮࡯ࡩࡩ࠭ೣ"), True)
  global bstack11l1ll111l_opy_
  global bstack1ll1ll11l1_opy_
  global bstack1ll1l1ll_opy_
  bstack11l1ll111l_opy_ = framework_name
  logger.info(bstack11lll1l111_opy_.format(bstack11l1ll111l_opy_.split(bstack11l1l_opy_ (u"ࠪ࠱ࠬ೤"))[0]))
  bstack11l1lllll1_opy_()
  try:
    from selenium import webdriver
    from selenium.webdriver.common.service import Service
    from selenium.webdriver.remote.webdriver import WebDriver
    if bstack11ll1l1lll_opy_:
      Service.start = bstack1lll1l1111_opy_
      Service.stop = bstack11ll11lll1_opy_
      webdriver.Remote.get = bstack1ll11l1ll1_opy_
      WebDriver.quit = bstack1lll11l111_opy_
      webdriver.Remote.__init__ = bstack111l111ll_opy_
    if not bstack11ll1l1lll_opy_:
        webdriver.Remote.__init__ = bstack11l111l1l_opy_
    WebDriver.getAccessibilityResults = getAccessibilityResults
    WebDriver.get_accessibility_results = getAccessibilityResults
    WebDriver.getAccessibilityResultsSummary = getAccessibilityResultsSummary
    WebDriver.get_accessibility_results_summary = getAccessibilityResultsSummary
    WebDriver.performScan = perform_scan
    WebDriver.perform_scan = perform_scan
    WebDriver.execute = bstack111lll1l1l_opy_
    bstack1ll1ll11l1_opy_ = True
  except Exception as e:
    pass
  try:
    if bstack11ll1l1lll_opy_:
      from QWeb.keywords import browser
      browser.close_browser = bstack1l1lll11ll_opy_
  except Exception as e:
    pass
  bstack11l11lll1l_opy_()
  if not bstack1ll1ll11l1_opy_:
    bstack1ll1111l11_opy_(bstack11l1l_opy_ (u"ࠦࡕࡧࡣ࡬ࡣࡪࡩࡸࠦ࡮ࡰࡶࠣ࡭ࡳࡹࡴࡢ࡮࡯ࡩࡩࠨ೥"), bstack1lll1l1l_opy_)
  if bstack1llll11ll_opy_():
    try:
      from selenium.webdriver.remote.remote_connection import RemoteConnection
      if hasattr(RemoteConnection, bstack11l1l_opy_ (u"ࠬࡥࡧࡦࡶࡢࡴࡷࡵࡸࡺࡡࡸࡶࡱ࠭೦")) and callable(getattr(RemoteConnection, bstack11l1l_opy_ (u"࠭࡟ࡨࡧࡷࡣࡵࡸ࡯ࡹࡻࡢࡹࡷࡲࠧ೧"))):
        RemoteConnection._get_proxy_url = bstack1l1l111l1l_opy_
      else:
        from selenium.webdriver.remote.client_config import ClientConfig
        ClientConfig.get_proxy_url = bstack1l1l111l1l_opy_
    except Exception as e:
      logger.error(bstack1l1l11ll11_opy_.format(str(e)))
  if bstack1ll11111_opy_():
    bstack111llllll1_opy_(CONFIG, logger)
  if (bstack11l1l_opy_ (u"ࠧࡳࡱࡥࡳࡹ࠭೨") in str(framework_name).lower()):
    try:
      from robot import run_cli
      from robot.output import Output
      from robot.running.status import TestStatus
      from pabot.pabot import QueueItem
      from pabot import pabot
      try:
        if percy.bstack1llll111l_opy_() == bstack11l1l_opy_ (u"ࠣࡶࡵࡹࡪࠨ೩"):
          bstack1lll111l11_opy_(bstack1llll1l1ll_opy_)
        from SeleniumLibrary.keywords.webdrivertools.webdrivertools import WebDriverCreator
        WebDriverCreator._get_ff_profile = bstack1l11111l1l_opy_
        from SeleniumLibrary.keywords.webdrivertools.webdrivertools import WebDriverCache
        WebDriverCache.close = bstack1lll1llll1_opy_
      except Exception as e:
        logger.warning(bstack1l111l1l11_opy_ + str(e))
      try:
        from AppiumLibrary.utils.applicationcache import ApplicationCache
        ApplicationCache.close = bstack1llll1111_opy_
      except Exception as e:
        logger.debug(bstack11llll1l_opy_ + str(e))
    except Exception as e:
      bstack1ll1111l11_opy_(e, bstack1l111l1l11_opy_)
    Output.start_test = bstack1l11l1l11_opy_
    Output.end_test = bstack11ll1llll_opy_
    TestStatus.__init__ = bstack1lll1l11_opy_
    QueueItem.__init__ = bstack11llllll11_opy_
    pabot._create_items = bstack1l1l1lll1l_opy_
    try:
      from pabot import __version__ as bstack11ll11llll_opy_
      if version.parse(bstack11ll11llll_opy_) >= version.parse(bstack11l1l_opy_ (u"ࠩ࠸࠲࠵࠴࠰ࠨ೪")):
        pabot._run = bstack111lll1l1_opy_
      elif version.parse(bstack11ll11llll_opy_) >= version.parse(bstack11l1l_opy_ (u"ࠪ࠸࠳࠸࠮࠱ࠩ೫")):
        pabot._run = bstack1ll11l11l_opy_
      elif version.parse(bstack11ll11llll_opy_) >= version.parse(bstack11l1l_opy_ (u"ࠫ࠷࠴࠱࠶࠰࠳ࠫ೬")):
        pabot._run = bstack1l111111ll_opy_
      elif version.parse(bstack11ll11llll_opy_) >= version.parse(bstack11l1l_opy_ (u"ࠬ࠸࠮࠲࠵࠱࠴ࠬ೭")):
        pabot._run = bstack1l111l11ll_opy_
      else:
        pabot._run = bstack11ll11lll_opy_
    except Exception as e:
      pabot._run = bstack11ll11lll_opy_
    pabot._create_command_for_execution = bstack1llllll1l_opy_
    pabot._report_results = bstack1l1ll1l111_opy_
  if bstack11l1l_opy_ (u"࠭ࡢࡦࡪࡤࡺࡪ࠭೮") in str(framework_name).lower():
    try:
      from behave.runner import Runner
      from behave.model import Step
    except Exception as e:
      bstack1ll1111l11_opy_(e, bstack1l1ll11l1_opy_)
    Runner.run_hook = bstack11l11lll_opy_
    Step.run = bstack11ll11l11_opy_
  if bstack11l1l_opy_ (u"ࠧࡱࡻࡷࡩࡸࡺࠧ೯") in str(framework_name).lower():
    if not bstack11ll1l1lll_opy_:
      return
    try:
      from pytest_selenium import pytest_selenium
      from _pytest.config import Config
      pytest_selenium.pytest_report_header = bstack11lll11l1l_opy_
      from pytest_selenium.drivers import browserstack
      browserstack.pytest_selenium_runtest_makereport = bstack1l111lllll_opy_
      Config.getoption = bstack11ll1l11ll_opy_
    except Exception as e:
      pass
    try:
      from pytest_bdd import reporting
      reporting.runtest_makereport = bstack1111ll11_opy_
    except Exception as e:
      pass
def bstack1llll1l11l_opy_():
  global CONFIG
  if bstack11l1l_opy_ (u"ࠨࡲࡤࡶࡦࡲ࡬ࡦ࡮ࡶࡔࡪࡸࡐ࡭ࡣࡷࡪࡴࡸ࡭ࠨ೰") in CONFIG and int(CONFIG[bstack11l1l_opy_ (u"ࠩࡳࡥࡷࡧ࡬࡭ࡧ࡯ࡷࡕ࡫ࡲࡑ࡮ࡤࡸ࡫ࡵࡲ࡮ࠩೱ")]) > 1:
    logger.warning(bstack11111l1ll_opy_)
def bstack1l11l111l_opy_(arg, bstack1lll1l1ll1_opy_, bstack11ll111lll_opy_=None):
  global CONFIG
  global bstack1l1l1ll1_opy_
  global bstack1ll1ll111l_opy_
  global bstack11ll1l1lll_opy_
  global bstack1l1ll11111_opy_
  bstack1l1lllll1l_opy_ = bstack11l1l_opy_ (u"ࠪࡴࡾࡺࡥࡴࡶࠪೲ")
  if bstack1lll1l1ll1_opy_ and isinstance(bstack1lll1l1ll1_opy_, str):
    bstack1lll1l1ll1_opy_ = eval(bstack1lll1l1ll1_opy_)
  CONFIG = bstack1lll1l1ll1_opy_[bstack11l1l_opy_ (u"ࠫࡈࡕࡎࡇࡋࡊࠫೳ")]
  bstack1l1l1ll1_opy_ = bstack1lll1l1ll1_opy_[bstack11l1l_opy_ (u"ࠬࡎࡕࡃࡡࡘࡖࡑ࠭೴")]
  bstack1ll1ll111l_opy_ = bstack1lll1l1ll1_opy_[bstack11l1l_opy_ (u"࠭ࡉࡔࡡࡄࡔࡕࡥࡁࡖࡖࡒࡑࡆ࡚ࡅࠨ೵")]
  bstack11ll1l1lll_opy_ = bstack1lll1l1ll1_opy_[bstack11l1l_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡁࡖࡖࡒࡑࡆ࡚ࡉࡐࡐࠪ೶")]
  bstack1l1ll11111_opy_.bstack1ll1111ll1_opy_(bstack11l1l_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫ࡠࡵࡨࡷࡸ࡯࡯࡯ࠩ೷"), bstack11ll1l1lll_opy_)
  os.environ[bstack11l1l_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡈࡕࡅࡒࡋࡗࡐࡔࡎࠫ೸")] = bstack1l1lllll1l_opy_
  os.environ[bstack11l1l_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡆࡓࡓࡌࡉࡈࠩ೹")] = json.dumps(CONFIG)
  os.environ[bstack11l1l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡌ࡚ࡈ࡟ࡖࡔࡏࠫ೺")] = bstack1l1l1ll1_opy_
  os.environ[bstack11l1l_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡎ࡙࡟ࡂࡒࡓࡣࡆ࡛ࡔࡐࡏࡄࡘࡊ࠭೻")] = str(bstack1ll1ll111l_opy_)
  os.environ[bstack11l1l_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡖ࡙ࡕࡇࡖࡘࡤࡖࡌࡖࡉࡌࡒࠬ೼")] = str(True)
  if bstack11l1lll111_opy_(arg, [bstack11l1l_opy_ (u"ࠧ࠮ࡰࠪ೽"), bstack11l1l_opy_ (u"ࠨ࠯࠰ࡲࡺࡳࡰࡳࡱࡦࡩࡸࡹࡥࡴࠩ೾")]) != -1:
    os.environ[bstack11l1l_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡒ࡜ࡘࡊ࡙ࡔࡠࡒࡄࡖࡆࡒࡌࡆࡎࠪ೿")] = str(True)
  if len(sys.argv) <= 1:
    logger.critical(bstack1l1111l111_opy_)
    return
  bstack1l1111l1l1_opy_()
  global bstack1l1l11ll1_opy_
  global bstack11ll1111ll_opy_
  global bstack11l11l1ll1_opy_
  global bstack1l1l11ll1l_opy_
  global bstack1l11lll111_opy_
  global bstack1ll1l1ll_opy_
  global bstack111ll1l11_opy_
  arg.append(bstack11l1l_opy_ (u"ࠥ࠱࡜ࠨഀ"))
  arg.append(bstack11l1l_opy_ (u"ࠦ࡮࡭࡮ࡰࡴࡨ࠾ࡒࡵࡤࡶ࡮ࡨࠤࡦࡲࡲࡦࡣࡧࡽࠥ࡯࡭ࡱࡱࡵࡸࡪࡪ࠺ࡱࡻࡷࡩࡸࡺ࠮ࡑࡻࡷࡩࡸࡺࡗࡢࡴࡱ࡭ࡳ࡭ࠢഁ"))
  arg.append(bstack11l1l_opy_ (u"ࠧ࠳ࡗࠣം"))
  arg.append(bstack11l1l_opy_ (u"ࠨࡩࡨࡰࡲࡶࡪࡀࡔࡩࡧࠣ࡬ࡴࡵ࡫ࡪ࡯ࡳࡰࠧഃ"))
  global bstack1l1l11111_opy_
  global bstack11llllllll_opy_
  global bstack111ll11l_opy_
  global bstack1111l111_opy_
  global bstack1l1l1l1lll_opy_
  global bstack1l111ll1_opy_
  global bstack11l1l111l1_opy_
  global bstack11l11l11_opy_
  global bstack1l11l1ll11_opy_
  global bstack1ll1l11l_opy_
  global bstack1lll1l1ll_opy_
  global bstack11l1ll11l1_opy_
  global bstack1ll1l11l11_opy_
  try:
    from selenium import webdriver
    from selenium.webdriver.remote.webdriver import WebDriver
    bstack1l1l11111_opy_ = webdriver.Remote.__init__
    bstack11llllllll_opy_ = WebDriver.quit
    bstack11l11l11_opy_ = WebDriver.close
    bstack1l11l1ll11_opy_ = WebDriver.get
    bstack111ll11l_opy_ = WebDriver.execute
  except Exception as e:
    pass
  if bstack11ll11ll1_opy_(CONFIG) and bstack1l11ll11l_opy_():
    if bstack1l1l1l1ll1_opy_() < version.parse(bstack11l1ll111_opy_):
      logger.error(bstack111l11lll_opy_.format(bstack1l1l1l1ll1_opy_()))
    else:
      try:
        from selenium.webdriver.remote.remote_connection import RemoteConnection
        if hasattr(RemoteConnection, bstack11l1l_opy_ (u"ࠧࡠࡩࡨࡸࡤࡶࡲࡰࡺࡼࡣࡺࡸ࡬ࠨഄ")) and callable(getattr(RemoteConnection, bstack11l1l_opy_ (u"ࠨࡡࡪࡩࡹࡥࡰࡳࡱࡻࡽࡤࡻࡲ࡭ࠩഅ"))):
          bstack1ll1l11l_opy_ = RemoteConnection._get_proxy_url
        else:
          from selenium.webdriver.remote.client_config import ClientConfig
          bstack1ll1l11l_opy_ = ClientConfig.get_proxy_url
      except Exception as e:
        logger.error(bstack1l1l11ll11_opy_.format(str(e)))
  try:
    from _pytest.config import Config
    bstack1lll1l1ll_opy_ = Config.getoption
    from _pytest import runner
    bstack11l1ll11l1_opy_ = runner._update_current_test_var
  except Exception as e:
    logger.warning(bstack11l1l_opy_ (u"ࠤࠨࡷ࠿ࠦࠥࡴࠤആ"), bstack1l1lll1111_opy_, str(e))
  try:
    from pytest_bdd import reporting
    bstack1ll1l11l11_opy_ = reporting.runtest_makereport
  except Exception as e:
    logger.debug(bstack11l1l_opy_ (u"ࠪࡔࡱ࡫ࡡࡴࡧࠣ࡭ࡳࡹࡴࡢ࡮࡯ࠤࡵࡿࡴࡦࡵࡷ࠱ࡧࡪࡤࠡࡶࡲࠤࡷࡻ࡮ࠡࡲࡼࡸࡪࡹࡴ࠮ࡤࡧࡨࠥࡺࡥࡴࡶࡶࠫഇ"))
  bstack11l11l1ll1_opy_ = CONFIG.get(bstack11l1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡘࡺࡡࡤ࡭ࡏࡳࡨࡧ࡬ࡐࡲࡷ࡭ࡴࡴࡳࠨഈ"), {}).get(bstack11l1l_opy_ (u"ࠬࡲ࡯ࡤࡣ࡯ࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧഉ"))
  bstack111ll1l11_opy_ = True
  if cli.is_enabled(CONFIG):
    if cli.bstack1l1l111ll_opy_():
      bstack1l1l1lllll_opy_.invoke(bstack111111lll_opy_.CONNECT, bstack1llll1111l_opy_())
    platform_index = int(os.environ.get(bstack11l1l_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡖࡌࡂࡖࡉࡓࡗࡓ࡟ࡊࡐࡇࡉ࡝࠭ഊ"), bstack11l1l_opy_ (u"ࠧ࠱ࠩഋ")))
  else:
    bstack11l1lll1_opy_(bstack1l11lll1_opy_)
  os.environ[bstack11l1l_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡖࡕࡈࡖࡓࡇࡍࡆࠩഌ")] = CONFIG[bstack11l1l_opy_ (u"ࠩࡸࡷࡪࡸࡎࡢ࡯ࡨࠫ഍")]
  os.environ[bstack11l1l_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡄࡇࡈࡋࡓࡔࡡࡎࡉ࡞࠭എ")] = CONFIG[bstack11l1l_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶࡏࡪࡿࠧഏ")]
  os.environ[bstack11l1l_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡆ࡛ࡔࡐࡏࡄࡘࡎࡕࡎࠨഐ")] = bstack11ll1l1lll_opy_.__str__()
  from _pytest.config import main as bstack1lll1l11ll_opy_
  bstack11l1l11l11_opy_ = []
  try:
    exit_code = bstack1lll1l11ll_opy_(arg)
    if cli.is_enabled(CONFIG):
      cli.bstack1l11l1111_opy_()
    if bstack11l1l_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡥࡥࡳࡴࡲࡶࡤࡲࡩࡴࡶࠪ഑") in multiprocessing.current_process().__dict__.keys():
      for bstack11llll1l1l_opy_ in multiprocessing.current_process().bstack_error_list:
        bstack11l1l11l11_opy_.append(bstack11llll1l1l_opy_)
    try:
      bstack1ll1ll1l_opy_ = (bstack11l1l11l11_opy_, int(exit_code))
      bstack11ll111lll_opy_.append(bstack1ll1ll1l_opy_)
    except:
      bstack11ll111lll_opy_.append((bstack11l1l11l11_opy_, exit_code))
  except Exception as e:
    logger.error(traceback.format_exc())
    bstack11l1l11l11_opy_.append({bstack11l1l_opy_ (u"ࠧ࡯ࡣࡰࡩࠬഒ"): bstack11l1l_opy_ (u"ࠨࡒࡵࡳࡨ࡫ࡳࡴࠢࠪഓ") + os.environ.get(bstack11l1l_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡒࡏࡅ࡙ࡌࡏࡓࡏࡢࡍࡓࡊࡅ࡙ࠩഔ")), bstack11l1l_opy_ (u"ࠪࡩࡷࡸ࡯ࡳࠩക"): traceback.format_exc(), bstack11l1l_opy_ (u"ࠫ࡮ࡴࡤࡦࡺࠪഖ"): int(os.environ.get(bstack11l1l_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡕࡒࡁࡕࡈࡒࡖࡒࡥࡉࡏࡆࡈ࡜ࠬഗ")))})
    bstack11ll111lll_opy_.append((bstack11l1l11l11_opy_, 1))
def mod_behave_main(args, retries):
  try:
    from behave.configuration import Configuration
    from behave.__main__ import run_behave
    from browserstack_sdk.bstack_behave_runner import BehaveRunner
    config = Configuration(args)
    config.update_userdata({bstack11l1l_opy_ (u"ࠨࡲࡦࡶࡵ࡭ࡪࡹࠢഘ"): str(retries)})
    return run_behave(config, runner_class=BehaveRunner)
  except Exception as e:
    bstack1lll1lll1_opy_ = e.__class__.__name__
    print(bstack11l1l_opy_ (u"ࠢࠦࡵ࠽ࠤࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡪࡰࠣࡶࡺࡴ࡮ࡪࡰࡪࠤࡧ࡫ࡨࡢࡸࡨࠤࡹ࡫ࡳࡵࠢࠨࡷࠧങ") % (bstack1lll1lll1_opy_, e))
    return 1
def bstack1ll1111lll_opy_(arg):
  global bstack111l11ll_opy_
  bstack11l1lll1_opy_(bstack11ll1ll1ll_opy_)
  os.environ[bstack11l1l_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡊࡕࡢࡅࡕࡖ࡟ࡂࡗࡗࡓࡒࡇࡔࡆࠩച")] = str(bstack1ll1ll111l_opy_)
  retries = bstack11llllll1l_opy_.bstack1111lllll_opy_(CONFIG)
  status_code = 0
  if bstack11llllll1l_opy_.bstack1ll111l111_opy_(CONFIG):
    status_code = mod_behave_main(arg, retries)
  else:
    from behave.__main__ import main as bstack1ll11l11l1_opy_
    status_code = bstack1ll11l11l1_opy_(arg)
  if status_code != 0:
    bstack111l11ll_opy_ = status_code
def bstack1lll11l1ll_opy_():
  logger.info(bstack1lll1l111l_opy_)
  import argparse
  parser = argparse.ArgumentParser()
  parser.add_argument(bstack11l1l_opy_ (u"ࠩࡶࡩࡹࡻࡰࠨഛ"), help=bstack11l1l_opy_ (u"ࠪࡋࡪࡴࡥࡳࡣࡷࡩࠥࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࠤࡨࡵ࡮ࡧ࡫ࡪࠫജ"))
  parser.add_argument(bstack11l1l_opy_ (u"ࠫ࠲ࡻࠧഝ"), bstack11l1l_opy_ (u"ࠬ࠳࠭ࡶࡵࡨࡶࡳࡧ࡭ࡦࠩഞ"), help=bstack11l1l_opy_ (u"࡙࠭ࡰࡷࡵࠤࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࠣࡹࡸ࡫ࡲ࡯ࡣࡰࡩࠬട"))
  parser.add_argument(bstack11l1l_opy_ (u"ࠧ࠮࡭ࠪഠ"), bstack11l1l_opy_ (u"ࠨ࠯࠰࡯ࡪࡿࠧഡ"), help=bstack11l1l_opy_ (u"ࠩ࡜ࡳࡺࡸࠠࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࠦࡡࡤࡥࡨࡷࡸࠦ࡫ࡦࡻࠪഢ"))
  parser.add_argument(bstack11l1l_opy_ (u"ࠪ࠱࡫࠭ണ"), bstack11l1l_opy_ (u"ࠫ࠲࠳ࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࠩത"), help=bstack11l1l_opy_ (u"ࠬ࡟࡯ࡶࡴࠣࡸࡪࡹࡴࠡࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࠫഥ"))
  bstack1ll11l111_opy_ = parser.parse_args()
  try:
    bstack1l111ll111_opy_ = bstack11l1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳࡭ࡥ࡯ࡧࡵ࡭ࡨ࠴ࡹ࡮࡮࠱ࡷࡦࡳࡰ࡭ࡧࠪദ")
    if bstack1ll11l111_opy_.framework and bstack1ll11l111_opy_.framework not in (bstack11l1l_opy_ (u"ࠧࡱࡻࡷ࡬ࡴࡴࠧധ"), bstack11l1l_opy_ (u"ࠨࡲࡼࡸ࡭ࡵ࡮࠴ࠩന")):
      bstack1l111ll111_opy_ = bstack11l1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮࠲ࡾࡳ࡬࠯ࡵࡤࡱࡵࡲࡥࠨഩ")
    bstack1l1l1l1l1_opy_ = os.path.join(os.path.dirname(os.path.realpath(__file__)), bstack1l111ll111_opy_)
    bstack1111l1l11_opy_ = open(bstack1l1l1l1l1_opy_, bstack11l1l_opy_ (u"ࠪࡶࠬപ"))
    bstack1l1ll1llll_opy_ = bstack1111l1l11_opy_.read()
    bstack1111l1l11_opy_.close()
    if bstack1ll11l111_opy_.username:
      bstack1l1ll1llll_opy_ = bstack1l1ll1llll_opy_.replace(bstack11l1l_opy_ (u"ࠫ࡞ࡕࡕࡓࡡࡘࡗࡊࡘࡎࡂࡏࡈࠫഫ"), bstack1ll11l111_opy_.username)
    if bstack1ll11l111_opy_.key:
      bstack1l1ll1llll_opy_ = bstack1l1ll1llll_opy_.replace(bstack11l1l_opy_ (u"ࠬ࡟ࡏࡖࡔࡢࡅࡈࡉࡅࡔࡕࡢࡏࡊ࡟ࠧബ"), bstack1ll11l111_opy_.key)
    if bstack1ll11l111_opy_.framework:
      bstack1l1ll1llll_opy_ = bstack1l1ll1llll_opy_.replace(bstack11l1l_opy_ (u"࡙࠭ࡐࡗࡕࡣࡋࡘࡁࡎࡇ࡚ࡓࡗࡑࠧഭ"), bstack1ll11l111_opy_.framework)
    file_name = bstack11l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡹ࡮࡮ࠪമ")
    file_path = os.path.abspath(file_name)
    bstack1l1ll111_opy_ = open(file_path, bstack11l1l_opy_ (u"ࠨࡹࠪയ"))
    bstack1l1ll111_opy_.write(bstack1l1ll1llll_opy_)
    bstack1l1ll111_opy_.close()
    logger.info(bstack1l1l11lll1_opy_)
    try:
      os.environ[bstack11l1l_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡈࡕࡅࡒࡋࡗࡐࡔࡎࠫര")] = bstack1ll11l111_opy_.framework if bstack1ll11l111_opy_.framework != None else bstack11l1l_opy_ (u"ࠥࠦറ")
      config = yaml.safe_load(bstack1l1ll1llll_opy_)
      config[bstack11l1l_opy_ (u"ࠫࡸࡵࡵࡳࡥࡨࠫല")] = bstack11l1l_opy_ (u"ࠬࡶࡹࡵࡪࡲࡲ࠲ࡹࡥࡵࡷࡳࠫള")
      bstack111111l11_opy_(bstack1l11ll11ll_opy_, config)
    except Exception as e:
      logger.debug(bstack1l1lllllll_opy_.format(str(e)))
  except Exception as e:
    logger.error(bstack1l11l1l1ll_opy_.format(str(e)))
def bstack111111l11_opy_(bstack1lll1lll_opy_, config, bstack1l1111l1l_opy_={}):
  global bstack11ll1l1lll_opy_
  global bstack1llll1lll_opy_
  global bstack1l1ll11111_opy_
  if not config:
    return
  bstack11ll11l1l_opy_ = bstack1ll1lll1l_opy_ if not bstack11ll1l1lll_opy_ else (
    bstack11l1ll11ll_opy_ if bstack11l1l_opy_ (u"࠭ࡡࡱࡲࠪഴ") in config else (
        bstack111l1llll_opy_ if config.get(bstack11l1l_opy_ (u"ࠧࡵࡷࡵࡦࡴ࡙ࡣࡢ࡮ࡨࠫവ")) else bstack1ll1111l1l_opy_
    )
)
  bstack111lll11l_opy_ = False
  bstack1ll11l1l11_opy_ = False
  if bstack11ll1l1lll_opy_ is True:
      if bstack11l1l_opy_ (u"ࠨࡣࡳࡴࠬശ") in config:
          bstack111lll11l_opy_ = True
      else:
          bstack1ll11l1l11_opy_ = True
  bstack11l1111ll1_opy_ = bstack1ll11l1l1_opy_.bstack1llll1l1_opy_(config, bstack1llll1lll_opy_)
  bstack1l11111lll_opy_ = bstack11ll1l111l_opy_()
  data = {
    bstack11l1l_opy_ (u"ࠩࡸࡷࡪࡸࡎࡢ࡯ࡨࠫഷ"): config[bstack11l1l_opy_ (u"ࠪࡹࡸ࡫ࡲࡏࡣࡰࡩࠬസ")],
    bstack11l1l_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶࡏࡪࡿࠧഹ"): config[bstack11l1l_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷࡐ࡫ࡹࠨഺ")],
    bstack11l1l_opy_ (u"࠭ࡥࡷࡧࡱࡸࡤࡺࡹࡱࡧ഻ࠪ"): bstack1lll1lll_opy_,
    bstack11l1l_opy_ (u"ࠧࡥࡧࡷࡩࡨࡺࡥࡥࡈࡵࡥࡲ࡫ࡷࡰࡴ࡮഼ࠫ"): os.environ.get(bstack11l1l_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡇࡔࡄࡑࡊ࡝ࡏࡓࡍࠪഽ"), bstack1llll1lll_opy_),
    bstack11l1l_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡠࡪࡤࡷ࡭࡫ࡤࡠ࡫ࡧࠫാ"): bstack1ll1111l_opy_,
    bstack11l1l_opy_ (u"ࠪࡳࡵࡺࡩ࡮ࡣ࡯ࡣ࡭ࡻࡢࡠࡷࡵࡰࠬി"): bstack1lll11llll_opy_(),
    bstack11l1l_opy_ (u"ࠫࡪࡼࡥ࡯ࡶࡢࡴࡷࡵࡰࡦࡴࡷ࡭ࡪࡹࠧീ"): {
      bstack11l1l_opy_ (u"ࠬࡲࡡ࡯ࡩࡸࡥ࡬࡫࡟ࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࠪു"): str(config[bstack11l1l_opy_ (u"࠭ࡳࡰࡷࡵࡧࡪ࠭ൂ")]) if bstack11l1l_opy_ (u"ࠧࡴࡱࡸࡶࡨ࡫ࠧൃ") in config else bstack11l1l_opy_ (u"ࠣࡷࡱ࡯ࡳࡵࡷ࡯ࠤൄ"),
      bstack11l1l_opy_ (u"ࠩ࡯ࡥࡳ࡭ࡵࡢࡩࡨ࡚ࡪࡸࡳࡪࡱࡱࠫ൅"): sys.version,
      bstack11l1l_opy_ (u"ࠪࡶࡪ࡬ࡥࡳࡴࡨࡶࠬെ"): bstack11lll1l1_opy_(os.environ.get(bstack11l1l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡊࡗࡇࡍࡆ࡙ࡒࡖࡐ࠭േ"), bstack1llll1lll_opy_)),
      bstack11l1l_opy_ (u"ࠬࡲࡡ࡯ࡩࡸࡥ࡬࡫ࠧൈ"): bstack11l1l_opy_ (u"࠭ࡰࡺࡶ࡫ࡳࡳ࠭൉"),
      bstack11l1l_opy_ (u"ࠧࡱࡴࡲࡨࡺࡩࡴࠨൊ"): bstack11ll11l1l_opy_,
      bstack11l1l_opy_ (u"ࠨࡲࡵࡳࡩࡻࡣࡵࡡࡰࡥࡵ࠭ോ"): bstack11l1111ll1_opy_,
      bstack11l1l_opy_ (u"ࠩࡷࡩࡸࡺࡨࡶࡤࡢࡹࡺ࡯ࡤࠨൌ"): os.environ[bstack11l1l_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡉࡘ࡚ࡈࡖࡄࡢ࡙࡚ࡏࡄࠨ്")],
      bstack11l1l_opy_ (u"ࠫ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱࠧൎ"): os.environ.get(bstack11l1l_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡋࡘࡁࡎࡇ࡚ࡓࡗࡑࠧ൏"), bstack1llll1lll_opy_),
      bstack11l1l_opy_ (u"࠭ࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡘࡨࡶࡸ࡯࡯࡯ࠩ൐"): bstack111ll111l_opy_(os.environ.get(bstack11l1l_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡆࡓࡃࡐࡉ࡜ࡕࡒࡌࠩ൑"), bstack1llll1lll_opy_)),
      bstack11l1l_opy_ (u"ࠨࡣࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࡋࡸࡡ࡮ࡧࡺࡳࡷࡱࠧ൒"): bstack1l11111lll_opy_.get(bstack11l1l_opy_ (u"ࠩࡱࡥࡲ࡫ࠧ൓")),
      bstack11l1l_opy_ (u"ࠪࡥࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࡆࡳࡣࡰࡩࡼࡵࡲ࡬ࡘࡨࡶࡸ࡯࡯࡯ࠩൔ"): bstack1l11111lll_opy_.get(bstack11l1l_opy_ (u"ࠫࡻ࡫ࡲࡴ࡫ࡲࡲࠬൕ")),
      bstack11l1l_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡒࡦࡳࡥࠨൖ"): config[bstack11l1l_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡓࡧ࡭ࡦࠩൗ")] if config[bstack11l1l_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡔࡡ࡮ࡧࠪ൘")] else bstack11l1l_opy_ (u"ࠣࡷࡱ࡯ࡳࡵࡷ࡯ࠤ൙"),
      bstack11l1l_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫ൚"): str(config[bstack11l1l_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬ൛")]) if bstack11l1l_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭൜") in config else bstack11l1l_opy_ (u"ࠧࡻ࡮࡬ࡰࡲࡻࡳࠨ൝"),
      bstack11l1l_opy_ (u"࠭࡯ࡴࠩ൞"): sys.platform,
      bstack11l1l_opy_ (u"ࠧࡩࡱࡶࡸࡳࡧ࡭ࡦࠩൟ"): socket.gethostname(),
      bstack11l1l_opy_ (u"ࠨࡵࡧ࡯ࡗࡻ࡮ࡊࡦࠪൠ"): bstack1l1ll11111_opy_.get_property(bstack11l1l_opy_ (u"ࠩࡶࡨࡰࡘࡵ࡯ࡋࡧࠫൡ"))
    }
  }
  if not bstack1l1ll11111_opy_.get_property(bstack11l1l_opy_ (u"ࠪࡷࡩࡱࡋࡪ࡮࡯ࡗ࡮࡭࡮ࡢ࡮ࠪൢ")) is None:
    data[bstack11l1l_opy_ (u"ࠫࡪࡼࡥ࡯ࡶࡢࡴࡷࡵࡰࡦࡴࡷ࡭ࡪࡹࠧൣ")][bstack11l1l_opy_ (u"ࠬ࡬ࡩ࡯࡫ࡶ࡬ࡪࡪࡍࡦࡶࡤࡨࡦࡺࡡࠨ൤")] = {
      bstack11l1l_opy_ (u"࠭ࡲࡦࡣࡶࡳࡳ࠭൥"): bstack11l1l_opy_ (u"ࠧࡶࡵࡨࡶࡤࡱࡩ࡭࡮ࡨࡨࠬ൦"),
      bstack11l1l_opy_ (u"ࠨࡵ࡬࡫ࡳࡧ࡬ࠨ൧"): bstack1l1ll11111_opy_.get_property(bstack11l1l_opy_ (u"ࠩࡶࡨࡰࡑࡩ࡭࡮ࡖ࡭࡬ࡴࡡ࡭ࠩ൨")),
      bstack11l1l_opy_ (u"ࠪࡷ࡮࡭࡮ࡢ࡮ࡑࡹࡲࡨࡥࡳࠩ൩"): bstack1l1ll11111_opy_.get_property(bstack11l1l_opy_ (u"ࠫࡸࡪ࡫ࡌ࡫࡯ࡰࡓࡵࠧ൪"))
    }
  if bstack1lll1lll_opy_ == bstack1l1lll1lll_opy_:
    data[bstack11l1l_opy_ (u"ࠬ࡫ࡶࡦࡰࡷࡣࡵࡸ࡯ࡱࡧࡵࡸ࡮࡫ࡳࠨ൫")][bstack11l1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࡈࡵ࡮ࡧ࡫ࡪࠫ൬")] = bstack111l1ll11_opy_(config)
    data[bstack11l1l_opy_ (u"ࠧࡦࡸࡨࡲࡹࡥࡰࡳࡱࡳࡩࡷࡺࡩࡦࡵࠪ൭")][bstack11l1l_opy_ (u"ࠨ࡫ࡶࡔࡪࡸࡣࡺࡃࡸࡸࡴࡋ࡮ࡢࡤ࡯ࡩࡩ࠭൮")] = percy.bstack1l1l1111l1_opy_
    data[bstack11l1l_opy_ (u"ࠩࡨࡺࡪࡴࡴࡠࡲࡵࡳࡵ࡫ࡲࡵ࡫ࡨࡷࠬ൯")][bstack11l1l_opy_ (u"ࠪࡴࡪࡸࡣࡺࡄࡸ࡭ࡱࡪࡉࡥࠩ൰")] = percy.percy_build_id
  if not bstack11llllll1l_opy_.bstack111lll1l11_opy_(CONFIG):
    data[bstack11l1l_opy_ (u"ࠫࡪࡼࡥ࡯ࡶࡢࡴࡷࡵࡰࡦࡴࡷ࡭ࡪࡹࠧ൱")][bstack11l1l_opy_ (u"ࠬࡺࡥࡴࡶࡒࡶࡨ࡮ࡥࡴࡶࡵࡥࡹ࡯࡯࡯ࠩ൲")] = bstack11llllll1l_opy_.bstack111lll1l11_opy_(CONFIG)
  bstack1111111ll_opy_ = bstack1ll11lll_opy_.bstack11l1l11ll1_opy_(CONFIG, logger)
  bstack1111l1ll_opy_ = bstack11llllll1l_opy_.bstack11l1l11ll1_opy_(config=CONFIG)
  if bstack1111111ll_opy_ is not None and bstack1111l1ll_opy_ is not None and bstack1111l1ll_opy_.bstack1llll1l111_opy_():
    data[bstack11l1l_opy_ (u"࠭ࡥࡷࡧࡱࡸࡤࡶࡲࡰࡲࡨࡶࡹ࡯ࡥࡴࠩ൳")][bstack1111l1ll_opy_.bstack111l1l1l_opy_()] = bstack1111111ll_opy_.bstack1lllll11l_opy_()
  update(data[bstack11l1l_opy_ (u"ࠧࡦࡸࡨࡲࡹࡥࡰࡳࡱࡳࡩࡷࡺࡩࡦࡵࠪ൴")], bstack1l1111l1l_opy_)
  try:
    response = bstack1l111l111l_opy_(bstack11l1l_opy_ (u"ࠨࡒࡒࡗ࡙࠭൵"), bstack1ll1l1l11_opy_(bstack1111l11ll_opy_), data, {
      bstack11l1l_opy_ (u"ࠩࡤࡹࡹ࡮ࠧ൶"): (config[bstack11l1l_opy_ (u"ࠪࡹࡸ࡫ࡲࡏࡣࡰࡩࠬ൷")], config[bstack11l1l_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶࡏࡪࡿࠧ൸")])
    })
    if response:
      logger.debug(bstack1ll1lll1l1_opy_.format(bstack1lll1lll_opy_, str(response.json())))
  except Exception as e:
    logger.debug(bstack111l1lll_opy_.format(str(e)))
def bstack11lll1l1_opy_(framework):
  return bstack11l1l_opy_ (u"ࠧࢁࡽ࠮ࡲࡼࡸ࡭ࡵ࡮ࡢࡩࡨࡲࡹ࠵ࡻࡾࠤ൹").format(str(framework), __version__) if framework else bstack11l1l_opy_ (u"ࠨࡰࡺࡶ࡫ࡳࡳࡧࡧࡦࡰࡷ࠳ࢀࢃࠢൺ").format(
    __version__)
def bstack1l1111l1l1_opy_():
  global CONFIG
  global bstack1l111l111_opy_
  if bool(CONFIG):
    return
  try:
    bstack111111l1_opy_()
    logger.debug(bstack1ll11l11_opy_.format(str(CONFIG)))
    bstack1l111l111_opy_ = bstack1l1lll1l11_opy_.configure_logger(CONFIG, bstack1l111l111_opy_)
    bstack11l1lllll1_opy_()
  except Exception as e:
    logger.error(bstack11l1l_opy_ (u"ࠢࡇࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡷࡪࡺࡵࡱ࠮ࠣࡩࡷࡸ࡯ࡳ࠼ࠣࠦൻ") + str(e))
    sys.exit(1)
  sys.excepthook = bstack111l11l11_opy_
  atexit.register(bstack11l11l11l_opy_)
  signal.signal(signal.SIGINT, bstack1lll11ll1l_opy_)
  signal.signal(signal.SIGTERM, bstack1lll11ll1l_opy_)
def bstack111l11l11_opy_(exctype, value, traceback):
  global bstack1ll111111l_opy_
  try:
    for driver in bstack1ll111111l_opy_:
      bstack111lllll1l_opy_(driver, bstack11l1l_opy_ (u"ࠨࡨࡤ࡭ࡱ࡫ࡤࠨർ"), bstack11l1l_opy_ (u"ࠤࡖࡩࡸࡹࡩࡰࡰࠣࡪࡦ࡯࡬ࡦࡦࠣࡻ࡮ࡺࡨ࠻ࠢ࡟ࡲࠧൽ") + str(value))
  except Exception:
    pass
  logger.info(bstack11l1l1111l_opy_)
  bstack11l11llll1_opy_(value, True)
  sys.__excepthook__(exctype, value, traceback)
  sys.exit(1)
def bstack11l11llll1_opy_(message=bstack11l1l_opy_ (u"ࠪࠫൾ"), bstack1ll111111_opy_ = False):
  global CONFIG
  bstack11l1l1111_opy_ = bstack11l1l_opy_ (u"ࠫ࡬ࡲ࡯ࡣࡣ࡯ࡉࡽࡩࡥࡱࡶ࡬ࡳࡳ࠭ൿ") if bstack1ll111111_opy_ else bstack11l1l_opy_ (u"ࠬ࡫ࡲࡳࡱࡵࠫ඀")
  try:
    if message:
      bstack1l1111l1l_opy_ = {
        bstack11l1l1111_opy_ : str(message)
      }
      bstack111111l11_opy_(bstack1l1lll1lll_opy_, CONFIG, bstack1l1111l1l_opy_)
    else:
      bstack111111l11_opy_(bstack1l1lll1lll_opy_, CONFIG)
  except Exception as e:
    logger.debug(bstack11l1lll11l_opy_.format(str(e)))
def bstack11ll111l_opy_(bstack1l11ll1lll_opy_, size):
  bstack1lllll1ll_opy_ = []
  while len(bstack1l11ll1lll_opy_) > size:
    bstack1l111ll11l_opy_ = bstack1l11ll1lll_opy_[:size]
    bstack1lllll1ll_opy_.append(bstack1l111ll11l_opy_)
    bstack1l11ll1lll_opy_ = bstack1l11ll1lll_opy_[size:]
  bstack1lllll1ll_opy_.append(bstack1l11ll1lll_opy_)
  return bstack1lllll1ll_opy_
def bstack1ll1llll_opy_(args):
  if bstack11l1l_opy_ (u"࠭࠭࡮ࠩඁ") in args and bstack11l1l_opy_ (u"ࠧࡱࡦࡥࠫං") in args:
    return True
  return False
@measure(event_name=EVENTS.bstack11l1l111l_opy_, stage=STAGE.bstack1ll1l1lll_opy_)
def run_on_browserstack(bstack1l111l1lll_opy_=None, bstack11ll111lll_opy_=None, bstack11ll1lll1_opy_=False):
  global CONFIG
  global bstack1l1l1ll1_opy_
  global bstack1ll1ll111l_opy_
  global bstack1llll1lll_opy_
  global bstack1l1ll11111_opy_
  bstack1l1lllll1l_opy_ = bstack11l1l_opy_ (u"ࠨࠩඃ")
  bstack111l11l1_opy_(bstack1l1llllll1_opy_, logger)
  if bstack1l111l1lll_opy_ and isinstance(bstack1l111l1lll_opy_, str):
    bstack1l111l1lll_opy_ = eval(bstack1l111l1lll_opy_)
  if bstack1l111l1lll_opy_:
    CONFIG = bstack1l111l1lll_opy_[bstack11l1l_opy_ (u"ࠩࡆࡓࡓࡌࡉࡈࠩ඄")]
    bstack1l1l1ll1_opy_ = bstack1l111l1lll_opy_[bstack11l1l_opy_ (u"ࠪࡌ࡚ࡈ࡟ࡖࡔࡏࠫඅ")]
    bstack1ll1ll111l_opy_ = bstack1l111l1lll_opy_[bstack11l1l_opy_ (u"ࠫࡎ࡙࡟ࡂࡒࡓࡣࡆ࡛ࡔࡐࡏࡄࡘࡊ࠭ආ")]
    bstack1l1ll11111_opy_.bstack1ll1111ll1_opy_(bstack11l1l_opy_ (u"ࠬࡏࡓࡠࡃࡓࡔࡤࡇࡕࡕࡑࡐࡅ࡙ࡋࠧඇ"), bstack1ll1ll111l_opy_)
    bstack1l1lllll1l_opy_ = bstack11l1l_opy_ (u"࠭ࡰࡺࡶ࡫ࡳࡳ࠭ඈ")
  bstack1l1ll11111_opy_.bstack1ll1111ll1_opy_(bstack11l1l_opy_ (u"ࠧࡴࡦ࡮ࡖࡺࡴࡉࡥࠩඉ"), uuid4().__str__())
  logger.info(bstack11l1l_opy_ (u"ࠨࡕࡇࡏࠥࡸࡵ࡯ࠢࡶࡸࡦࡸࡴࡦࡦࠣࡻ࡮ࡺࡨࠡ࡫ࡧ࠾ࠥ࠭ඊ") + bstack1l1ll11111_opy_.get_property(bstack11l1l_opy_ (u"ࠩࡶࡨࡰࡘࡵ࡯ࡋࡧࠫඋ")));
  logger.debug(bstack11l1l_opy_ (u"ࠪࡷࡩࡱࡒࡶࡰࡌࡨࡂ࠭ඌ") + bstack1l1ll11111_opy_.get_property(bstack11l1l_opy_ (u"ࠫࡸࡪ࡫ࡓࡷࡱࡍࡩ࠭ඍ")))
  if not bstack11ll1lll1_opy_:
    if len(sys.argv) <= 1:
      logger.critical(bstack1l1111l111_opy_)
      return
    if sys.argv[1] == bstack11l1l_opy_ (u"ࠬ࠳࠭ࡷࡧࡵࡷ࡮ࡵ࡮ࠨඎ") or sys.argv[1] == bstack11l1l_opy_ (u"࠭࠭ࡷࠩඏ"):
      logger.info(bstack11l1l_opy_ (u"ࠧࡃࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࠦࡐࡺࡶ࡫ࡳࡳࠦࡓࡅࡍࠣࡺࢀࢃࠧඐ").format(__version__))
      return
    if sys.argv[1] == bstack11l1l_opy_ (u"ࠨࡵࡨࡸࡺࡶࠧඑ"):
      bstack1lll11l1ll_opy_()
      return
  args = sys.argv
  bstack1l1111l1l1_opy_()
  global bstack1l1l11ll1_opy_
  global bstack1ll1ll1lll_opy_
  global bstack111ll1l11_opy_
  global bstack1l1llll1ll_opy_
  global bstack11ll1111ll_opy_
  global bstack11l11l1ll1_opy_
  global bstack1l1l11ll1l_opy_
  global bstack11lllll11l_opy_
  global bstack1l11lll111_opy_
  global bstack1ll1l1ll_opy_
  global bstack1llll1lll1_opy_
  bstack1ll1ll1lll_opy_ = len(CONFIG.get(bstack11l1l_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬඒ"), []))
  if not bstack1l1lllll1l_opy_:
    if args[1] == bstack11l1l_opy_ (u"ࠪࡴࡾࡺࡨࡰࡰࠪඓ") or args[1] == bstack11l1l_opy_ (u"ࠫࡵࡿࡴࡩࡱࡱ࠷ࠬඔ"):
      bstack1l1lllll1l_opy_ = bstack11l1l_opy_ (u"ࠬࡶࡹࡵࡪࡲࡲࠬඕ")
      args = args[2:]
    elif args[1] == bstack11l1l_opy_ (u"࠭ࡲࡰࡤࡲࡸࠬඖ"):
      bstack1l1lllll1l_opy_ = bstack11l1l_opy_ (u"ࠧࡳࡱࡥࡳࡹ࠭඗")
      args = args[2:]
    elif args[1] == bstack11l1l_opy_ (u"ࠨࡲࡤࡦࡴࡺࠧ඘"):
      bstack1l1lllll1l_opy_ = bstack11l1l_opy_ (u"ࠩࡳࡥࡧࡵࡴࠨ඙")
      args = args[2:]
    elif args[1] == bstack11l1l_opy_ (u"ࠪࡶࡴࡨ࡯ࡵ࠯࡬ࡲࡹ࡫ࡲ࡯ࡣ࡯ࠫක"):
      bstack1l1lllll1l_opy_ = bstack11l1l_opy_ (u"ࠫࡷࡵࡢࡰࡶ࠰࡭ࡳࡺࡥࡳࡰࡤࡰࠬඛ")
      args = args[2:]
    elif args[1] == bstack11l1l_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸࠬග"):
      bstack1l1lllll1l_opy_ = bstack11l1l_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹ࠭ඝ")
      args = args[2:]
    elif args[1] == bstack11l1l_opy_ (u"ࠧࡣࡧ࡫ࡥࡻ࡫ࠧඞ"):
      bstack1l1lllll1l_opy_ = bstack11l1l_opy_ (u"ࠨࡤࡨ࡬ࡦࡼࡥࠨඟ")
      args = args[2:]
    else:
      if not bstack11l1l_opy_ (u"ࠩࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࠬච") in CONFIG or str(CONFIG[bstack11l1l_opy_ (u"ࠪࡪࡷࡧ࡭ࡦࡹࡲࡶࡰ࠭ඡ")]).lower() in [bstack11l1l_opy_ (u"ࠫࡵࡿࡴࡩࡱࡱࠫජ"), bstack11l1l_opy_ (u"ࠬࡶࡹࡵࡪࡲࡲ࠸࠭ඣ")]:
        bstack1l1lllll1l_opy_ = bstack11l1l_opy_ (u"࠭ࡰࡺࡶ࡫ࡳࡳ࠭ඤ")
        args = args[1:]
      elif str(CONFIG[bstack11l1l_opy_ (u"ࠧࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࠪඥ")]).lower() == bstack11l1l_opy_ (u"ࠨࡴࡲࡦࡴࡺࠧඦ"):
        bstack1l1lllll1l_opy_ = bstack11l1l_opy_ (u"ࠩࡵࡳࡧࡵࡴࠨට")
        args = args[1:]
      elif str(CONFIG[bstack11l1l_opy_ (u"ࠪࡪࡷࡧ࡭ࡦࡹࡲࡶࡰ࠭ඨ")]).lower() == bstack11l1l_opy_ (u"ࠫࡵࡧࡢࡰࡶࠪඩ"):
        bstack1l1lllll1l_opy_ = bstack11l1l_opy_ (u"ࠬࡶࡡࡣࡱࡷࠫඪ")
        args = args[1:]
      elif str(CONFIG[bstack11l1l_opy_ (u"࠭ࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࠩණ")]).lower() == bstack11l1l_opy_ (u"ࠧࡱࡻࡷࡩࡸࡺࠧඬ"):
        bstack1l1lllll1l_opy_ = bstack11l1l_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࠨත")
        args = args[1:]
      elif str(CONFIG[bstack11l1l_opy_ (u"ࠩࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࠬථ")]).lower() == bstack11l1l_opy_ (u"ࠪࡦࡪ࡮ࡡࡷࡧࠪද"):
        bstack1l1lllll1l_opy_ = bstack11l1l_opy_ (u"ࠫࡧ࡫ࡨࡢࡸࡨࠫධ")
        args = args[1:]
      else:
        os.environ[bstack11l1l_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡋࡘࡁࡎࡇ࡚ࡓࡗࡑࠧන")] = bstack1l1lllll1l_opy_
        bstack1ll11l111l_opy_(bstack1l111l1l1_opy_)
  os.environ[bstack11l1l_opy_ (u"࠭ࡆࡓࡃࡐࡉ࡜ࡕࡒࡌࡡࡘࡗࡊࡊࠧ඲")] = bstack1l1lllll1l_opy_
  bstack1llll1lll_opy_ = bstack1l1lllll1l_opy_
  if cli.is_enabled(CONFIG):
    try:
      bstack1l1l1l1l1l_opy_ = bstack1l1llll1l1_opy_[bstack11l1l_opy_ (u"ࠧࡑ࡛ࡗࡉࡘ࡚࠭ࡃࡆࡇࠫඳ")] if bstack1l1lllll1l_opy_ == bstack11l1l_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࠨප") and bstack11ll1l1l_opy_() else bstack1l1lllll1l_opy_
      bstack1l1l1lllll_opy_.invoke(bstack111111lll_opy_.bstack1l11ll1l1l_opy_, bstack1l1lll1l1l_opy_(
        sdk_version=__version__,
        path_config=bstack11l11l11ll_opy_(),
        path_project=os.getcwd(),
        test_framework=bstack1l1l1l1l1l_opy_,
        frameworks=[bstack1l1l1l1l1l_opy_],
        framework_versions={
          bstack1l1l1l1l1l_opy_: bstack111ll111l_opy_(bstack11l1l_opy_ (u"ࠩࡕࡳࡧࡵࡴࠨඵ") if bstack1l1lllll1l_opy_ in [bstack11l1l_opy_ (u"ࠪࡴࡦࡨ࡯ࡵࠩබ"), bstack11l1l_opy_ (u"ࠫࡷࡵࡢࡰࡶࠪභ"), bstack11l1l_opy_ (u"ࠬࡸ࡯ࡣࡱࡷ࠱࡮ࡴࡴࡦࡴࡱࡥࡱ࠭ම")] else bstack1l1lllll1l_opy_)
        },
        bs_config=CONFIG
      ))
      if cli.config.get(bstack11l1l_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠣඹ"), None):
        CONFIG[bstack11l1l_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠤය")] = cli.config.get(bstack11l1l_opy_ (u"ࠣࡤࡸ࡭ࡱࡪࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠥර"), None)
    except Exception as e:
      bstack1l1l1lllll_opy_.invoke(bstack111111lll_opy_.bstack1lll1111l1_opy_, e.__traceback__, 1)
    if bstack1ll1ll111l_opy_:
      CONFIG[bstack11l1l_opy_ (u"ࠤࡤࡴࡵࠨ඼")] = cli.config[bstack11l1l_opy_ (u"ࠥࡥࡵࡶࠢල")]
      logger.info(bstack1111111l_opy_.format(CONFIG[bstack11l1l_opy_ (u"ࠫࡦࡶࡰࠨ඾")]))
  else:
    bstack1l1l1lllll_opy_.clear()
  global bstack1l1111ll1l_opy_
  global bstack11l111ll1_opy_
  if bstack1l111l1lll_opy_:
    try:
      bstack11ll1l1ll1_opy_ = datetime.datetime.now()
      os.environ[bstack11l1l_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡋࡘࡁࡎࡇ࡚ࡓࡗࡑࠧ඿")] = bstack1l1lllll1l_opy_
      bstack111111l11_opy_(bstack11ll11ll1l_opy_, CONFIG)
      cli.bstack11lll111_opy_(bstack11l1l_opy_ (u"ࠨࡨࡵࡶࡳ࠾ࡸࡪ࡫ࡠࡶࡨࡷࡹࡥࡡࡵࡶࡨࡱࡵࡺࡥࡥࠤව"), datetime.datetime.now() - bstack11ll1l1ll1_opy_)
    except Exception as e:
      logger.debug(bstack1l1lll11_opy_.format(str(e)))
  global bstack1l1l11111_opy_
  global bstack11llllllll_opy_
  global bstack1l1l1lll11_opy_
  global bstack1ll11ll1l1_opy_
  global bstack1111l11l_opy_
  global bstack11l1l111ll_opy_
  global bstack1111l111_opy_
  global bstack1l1l1l1lll_opy_
  global bstack11ll1l11_opy_
  global bstack1l111ll1_opy_
  global bstack11l1l111l1_opy_
  global bstack11l11l11_opy_
  global bstack1ll1llll1_opy_
  global bstack111ll11ll_opy_
  global bstack1l11l1ll11_opy_
  global bstack1ll1l11l_opy_
  global bstack1lll1l1ll_opy_
  global bstack11l1ll11l1_opy_
  global bstack1l1l1ll11l_opy_
  global bstack1ll1l11l11_opy_
  global bstack111ll11l_opy_
  try:
    from selenium import webdriver
    from selenium.webdriver.remote.webdriver import WebDriver
    bstack1l1l11111_opy_ = webdriver.Remote.__init__
    bstack11llllllll_opy_ = WebDriver.quit
    bstack11l11l11_opy_ = WebDriver.close
    bstack1l11l1ll11_opy_ = WebDriver.get
    bstack111ll11l_opy_ = WebDriver.execute
  except Exception as e:
    pass
  try:
    import Browser
    from subprocess import Popen
    bstack1l1111ll1l_opy_ = Popen.__init__
  except Exception as e:
    pass
  try:
    from bstack_utils.helper import bstack1lll1111_opy_
    bstack11l111ll1_opy_ = bstack1lll1111_opy_()
  except Exception as e:
    pass
  try:
    global bstack1l1l11l1ll_opy_
    from QWeb.keywords import browser
    bstack1l1l11l1ll_opy_ = browser.close_browser
  except Exception as e:
    pass
  if bstack11ll11ll1_opy_(CONFIG) and bstack1l11ll11l_opy_():
    if bstack1l1l1l1ll1_opy_() < version.parse(bstack11l1ll111_opy_):
      logger.error(bstack111l11lll_opy_.format(bstack1l1l1l1ll1_opy_()))
    else:
      try:
        from selenium.webdriver.remote.remote_connection import RemoteConnection
        if hasattr(RemoteConnection, bstack11l1l_opy_ (u"ࠧࡠࡩࡨࡸࡤࡶࡲࡰࡺࡼࡣࡺࡸ࡬ࠨශ")) and callable(getattr(RemoteConnection, bstack11l1l_opy_ (u"ࠨࡡࡪࡩࡹࡥࡰࡳࡱࡻࡽࡤࡻࡲ࡭ࠩෂ"))):
          RemoteConnection._get_proxy_url = bstack1l1l111l1l_opy_
        else:
          from selenium.webdriver.remote.client_config import ClientConfig
          ClientConfig.get_proxy_url = bstack1l1l111l1l_opy_
      except Exception as e:
        logger.error(bstack1l1l11ll11_opy_.format(str(e)))
  if not CONFIG.get(bstack11l1l_opy_ (u"ࠩࡧ࡭ࡸࡧࡢ࡭ࡧࡄࡹࡹࡵࡃࡢࡲࡷࡹࡷ࡫ࡌࡰࡩࡶࠫස"), False) and not bstack1l111l1lll_opy_:
    logger.info(bstack1l111ll1l1_opy_)
  if not cli.is_enabled(CONFIG):
    if bstack11l1l_opy_ (u"ࠪࡸࡺࡸࡢࡰࡕࡦࡥࡱ࡫ࠧහ") in CONFIG and str(CONFIG[bstack11l1l_opy_ (u"ࠫࡹࡻࡲࡣࡱࡖࡧࡦࡲࡥࠨළ")]).lower() != bstack11l1l_opy_ (u"ࠬ࡬ࡡ࡭ࡵࡨࠫෆ"):
      bstack11lll1l1ll_opy_()
    elif bstack1l1lllll1l_opy_ != bstack11l1l_opy_ (u"࠭ࡰࡺࡶ࡫ࡳࡳ࠭෇") or (bstack1l1lllll1l_opy_ == bstack11l1l_opy_ (u"ࠧࡱࡻࡷ࡬ࡴࡴࠧ෈") and not bstack1l111l1lll_opy_):
      bstack1lll11ll11_opy_()
  if (bstack1l1lllll1l_opy_ in [bstack11l1l_opy_ (u"ࠨࡲࡤࡦࡴࡺࠧ෉"), bstack11l1l_opy_ (u"ࠩࡵࡳࡧࡵࡴࠨ්"), bstack11l1l_opy_ (u"ࠪࡶࡴࡨ࡯ࡵ࠯࡬ࡲࡹ࡫ࡲ࡯ࡣ࡯ࠫ෋")]):
    try:
      from robot import run_cli
      from robot.output import Output
      from robot.running.status import TestStatus
      from pabot.pabot import QueueItem
      from pabot import pabot
      try:
        from SeleniumLibrary.keywords.webdrivertools.webdrivertools import WebDriverCreator
        from SeleniumLibrary.keywords.webdrivertools.webdrivertools import WebDriverCache
        WebDriverCreator._get_ff_profile = bstack1l11111l1l_opy_
        bstack11l1l111ll_opy_ = WebDriverCache.close
      except Exception as e:
        logger.warning(bstack1l111l1l11_opy_ + str(e))
      try:
        from AppiumLibrary.utils.applicationcache import ApplicationCache
        bstack1111l11l_opy_ = ApplicationCache.close
      except Exception as e:
        logger.debug(bstack11llll1l_opy_ + str(e))
    except Exception as e:
      bstack1ll1111l11_opy_(e, bstack1l111l1l11_opy_)
    if bstack1l1lllll1l_opy_ != bstack11l1l_opy_ (u"ࠫࡷࡵࡢࡰࡶ࠰࡭ࡳࡺࡥࡳࡰࡤࡰࠬ෌"):
      bstack1lll1ll11_opy_()
    bstack1l1l1lll11_opy_ = Output.start_test
    bstack1ll11ll1l1_opy_ = Output.end_test
    bstack1111l111_opy_ = TestStatus.__init__
    bstack11ll1l11_opy_ = pabot._run
    bstack1l111ll1_opy_ = QueueItem.__init__
    bstack11l1l111l1_opy_ = pabot._create_command_for_execution
    bstack1l1l1ll11l_opy_ = pabot._report_results
  if bstack1l1lllll1l_opy_ == bstack11l1l_opy_ (u"ࠬࡨࡥࡩࡣࡹࡩࠬ෍"):
    try:
      from behave.runner import Runner
      from behave.model import Step
    except Exception as e:
      bstack1ll1111l11_opy_(e, bstack1l1ll11l1_opy_)
    bstack1ll1llll1_opy_ = Runner.run_hook
    bstack111ll11ll_opy_ = Step.run
  if bstack1l1lllll1l_opy_ == bstack11l1l_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹ࠭෎"):
    try:
      from _pytest.config import Config
      bstack1lll1l1ll_opy_ = Config.getoption
      from _pytest import runner
      bstack11l1ll11l1_opy_ = runner._update_current_test_var
    except Exception as e:
      logger.warning(bstack11l1l_opy_ (u"ࠢࠦࡵ࠽ࠤࠪࡹࠢා"), bstack1l1lll1111_opy_, str(e))
    try:
      from pytest_bdd import reporting
      bstack1ll1l11l11_opy_ = reporting.runtest_makereport
    except Exception as e:
      logger.debug(bstack11l1l_opy_ (u"ࠨࡒ࡯ࡩࡦࡹࡥࠡ࡫ࡱࡷࡹࡧ࡬࡭ࠢࡳࡽࡹ࡫ࡳࡵ࠯ࡥࡨࡩࠦࡴࡰࠢࡵࡹࡳࠦࡰࡺࡶࡨࡷࡹ࠳ࡢࡥࡦࠣࡸࡪࡹࡴࡴࠩැ"))
    if bstack1l1ll1l11_opy_():
      logger.warning(bstack1ll111l1_opy_[bstack11l1l_opy_ (u"ࠩࡖࡈࡐ࠳ࡇࡆࡐ࠰࠴࠵࠻ࠧෑ")])
  try:
    framework_name = bstack11l1l_opy_ (u"ࠪࡶࡴࡨ࡯ࡵࠩි") if bstack1l1lllll1l_opy_ in [bstack11l1l_opy_ (u"ࠫࡵࡧࡢࡰࡶࠪී"), bstack11l1l_opy_ (u"ࠬࡸ࡯ࡣࡱࡷࠫු"), bstack11l1l_opy_ (u"࠭ࡲࡰࡤࡲࡸ࠲࡯࡮ࡵࡧࡵࡲࡦࡲࠧ෕")] else bstack1l11l11ll_opy_(bstack1l1lllll1l_opy_)
    bstack1llll111_opy_ = {
      bstack11l1l_opy_ (u"ࠧࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡢࡲࡦࡳࡥࠨූ"): bstack11l1l_opy_ (u"ࠨࡒࡼࡸࡪࡹࡴ࠮ࡥࡸࡧࡺࡳࡢࡦࡴࠪ෗") if bstack1l1lllll1l_opy_ == bstack11l1l_opy_ (u"ࠩࡳࡽࡹ࡫ࡳࡵࠩෘ") and bstack11ll1l1l_opy_() else framework_name,
      bstack11l1l_opy_ (u"ࠪࡪࡷࡧ࡭ࡦࡹࡲࡶࡰࡥࡶࡦࡴࡶ࡭ࡴࡴࠧෙ"): bstack111ll111l_opy_(framework_name),
      bstack11l1l_opy_ (u"ࠫࡸࡪ࡫ࡠࡸࡨࡶࡸ࡯࡯࡯ࠩේ"): __version__,
      bstack11l1l_opy_ (u"ࠬ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡷࡶࡩࡩ࠭ෛ"): bstack1l1lllll1l_opy_
    }
    if bstack1l1lllll1l_opy_ in bstack11lll1111l_opy_ + bstack1llll1ll11_opy_:
      if bstack11llll11l1_opy_.bstack1111111l1_opy_(CONFIG):
        if bstack11l1l_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࡕࡰࡵ࡫ࡲࡲࡸ࠭ො") in CONFIG:
          os.environ[bstack11l1l_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡣࡆࡉࡃࡆࡕࡖࡍࡇࡏࡌࡊࡖ࡜ࡣࡈࡕࡎࡇࡋࡊ࡙ࡗࡇࡔࡊࡑࡑࡣ࡞ࡓࡌࠨෝ")] = os.getenv(bstack11l1l_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡤࡇࡃࡄࡇࡖࡗࡎࡈࡉࡍࡋࡗ࡝ࡤࡉࡏࡏࡈࡌࡋ࡚ࡘࡁࡕࡋࡒࡒࡤ࡟ࡍࡍࠩෞ"), json.dumps(CONFIG[bstack11l1l_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࡑࡳࡸ࡮ࡵ࡮ࡴࠩෟ")]))
          CONFIG[bstack11l1l_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࡒࡴࡹ࡯࡯࡯ࡵࠪ෠")].pop(bstack11l1l_opy_ (u"ࠫ࡮ࡴࡣ࡭ࡷࡧࡩ࡙ࡧࡧࡴࡋࡱࡘࡪࡹࡴࡪࡰࡪࡗࡨࡵࡰࡦࠩ෡"), None)
          CONFIG[bstack11l1l_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࡔࡶࡴࡪࡱࡱࡷࠬ෢")].pop(bstack11l1l_opy_ (u"࠭ࡥࡹࡥ࡯ࡹࡩ࡫ࡔࡢࡩࡶࡍࡳ࡚ࡥࡴࡶ࡬ࡲ࡬࡙ࡣࡰࡲࡨࠫ෣"), None)
        bstack1llll111_opy_[bstack11l1l_opy_ (u"ࠧࡵࡧࡶࡸࡋࡸࡡ࡮ࡧࡺࡳࡷࡱࠧ෤")] = {
          bstack11l1l_opy_ (u"ࠨࡰࡤࡱࡪ࠭෥"): bstack11l1l_opy_ (u"ࠩࡶࡩࡱ࡫࡮ࡪࡷࡰࠫ෦"),
          bstack11l1l_opy_ (u"ࠪࡺࡪࡸࡳࡪࡱࡱࠫ෧"): str(bstack1l1l1l1ll1_opy_())
        }
    if bstack1l1lllll1l_opy_ not in [bstack11l1l_opy_ (u"ࠫࡷࡵࡢࡰࡶ࠰࡭ࡳࡺࡥࡳࡰࡤࡰࠬ෨")] and not cli.is_running():
      bstack11lllll1l1_opy_, bstack11111ll1_opy_ = bstack1ll1llll11_opy_.launch(CONFIG, bstack1llll111_opy_)
      if bstack11111ll1_opy_.get(bstack11l1l_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠬ෩")) is not None and bstack11llll11l1_opy_.bstack1lllll1lll_opy_(CONFIG) is None:
        value = bstack11111ll1_opy_[bstack11l1l_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾ࠭෪")].get(bstack11l1l_opy_ (u"ࠧࡴࡷࡦࡧࡪࡹࡳࠨ෫"))
        if value is not None:
            CONFIG[bstack11l1l_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠨ෬")] = value
        else:
          logger.debug(bstack11l1l_opy_ (u"ࠤࡑࡳࠥࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡪࡡࡵࡣࠣࡪࡴࡻ࡮ࡥࠢ࡬ࡲࠥࡸࡥࡴࡲࡲࡲࡸ࡫ࠢ෭"))
  except Exception as e:
    logger.debug(bstack1l111l1l1l_opy_.format(bstack11l1l_opy_ (u"ࠪࡘࡪࡹࡴࡉࡷࡥࠫ෮"), str(e)))
  if bstack1l1lllll1l_opy_ == bstack11l1l_opy_ (u"ࠫࡵࡿࡴࡩࡱࡱࠫ෯"):
    bstack111ll1l11_opy_ = True
    if bstack1l111l1lll_opy_ and bstack11ll1lll1_opy_:
      bstack11l11l1ll1_opy_ = CONFIG.get(bstack11l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࡑࡳࡸ࡮ࡵ࡮ࡴࠩ෰"), {}).get(bstack11l1l_opy_ (u"࠭࡬ࡰࡥࡤࡰࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨ෱"))
      bstack11l1lll1_opy_(bstack1llll1l11_opy_)
    elif bstack1l111l1lll_opy_:
      bstack11l11l1ll1_opy_ = CONFIG.get(bstack11l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡔࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࡓࡵࡺࡩࡰࡰࡶࠫෲ"), {}).get(bstack11l1l_opy_ (u"ࠨ࡮ࡲࡧࡦࡲࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪෳ"))
      global bstack1ll111111l_opy_
      try:
        if bstack1ll1llll_opy_(bstack1l111l1lll_opy_[bstack11l1l_opy_ (u"ࠩࡩ࡭ࡱ࡫࡟࡯ࡣࡰࡩࠬ෴")]) and multiprocessing.current_process().name == bstack11l1l_opy_ (u"ࠪ࠴ࠬ෵"):
          bstack1l111l1lll_opy_[bstack11l1l_opy_ (u"ࠫ࡫࡯࡬ࡦࡡࡱࡥࡲ࡫ࠧ෶")].remove(bstack11l1l_opy_ (u"ࠬ࠳࡭ࠨ෷"))
          bstack1l111l1lll_opy_[bstack11l1l_opy_ (u"࠭ࡦࡪ࡮ࡨࡣࡳࡧ࡭ࡦࠩ෸")].remove(bstack11l1l_opy_ (u"ࠧࡱࡦࡥࠫ෹"))
          bstack1l111l1lll_opy_[bstack11l1l_opy_ (u"ࠨࡨ࡬ࡰࡪࡥ࡮ࡢ࡯ࡨࠫ෺")] = bstack1l111l1lll_opy_[bstack11l1l_opy_ (u"ࠩࡩ࡭ࡱ࡫࡟࡯ࡣࡰࡩࠬ෻")][0]
          with open(bstack1l111l1lll_opy_[bstack11l1l_opy_ (u"ࠪࡪ࡮ࡲࡥࡠࡰࡤࡱࡪ࠭෼")], bstack11l1l_opy_ (u"ࠫࡷ࠭෽")) as f:
            bstack111l1ll1_opy_ = f.read()
          bstack1ll11llll_opy_ = bstack11l1l_opy_ (u"ࠧࠨࠢࡧࡴࡲࡱࠥࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡸࡪ࡫ࠡ࡫ࡰࡴࡴࡸࡴࠡࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡪࡰ࡬ࡸ࡮ࡧ࡬ࡪࡼࡨ࠿ࠥࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣ࡮ࡴࡩࡵ࡫ࡤࡰ࡮ࢀࡥࠩࡽࢀ࠭ࡀࠦࡦࡳࡱࡰࠤࡵࡪࡢࠡ࡫ࡰࡴࡴࡸࡴࠡࡒࡧࡦࡀࠦ࡯ࡨࡡࡧࡦࠥࡃࠠࡑࡦࡥ࠲ࡩࡵ࡟ࡣࡴࡨࡥࡰࡁࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࡨࡪ࡬ࠠ࡮ࡱࡧࡣࡧࡸࡥࡢ࡭ࠫࡷࡪࡲࡦ࠭ࠢࡤࡶ࡬࠲ࠠࡵࡧࡰࡴࡴࡸࡡࡳࡻࠣࡁࠥ࠶ࠩ࠻ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࡵࡴࡼ࠾ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࡧࡲࡨࠢࡀࠤࡸࡺࡲࠩ࡫ࡱࡸ࠭ࡧࡲࡨࠫ࠮࠵࠵࠯ࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥ࡫ࡸࡤࡧࡳࡸࠥࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡࡣࡶࠤࡪࡀࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࡱࡣࡶࡷࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࡳ࡬ࡥࡤࡣࠪࡶࡩࡱ࡬ࠬࡢࡴࡪ࠰ࡹ࡫࡭ࡱࡱࡵࡥࡷࡿࠩࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࡕࡪࡢ࠯ࡦࡲࡣࡧࠦ࠽ࠡ࡯ࡲࡨࡤࡨࡲࡦࡣ࡮ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࡑࡦࡥ࠲ࡩࡵ࡟ࡣࡴࡨࡥࡰࠦ࠽ࠡ࡯ࡲࡨࡤࡨࡲࡦࡣ࡮ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࡑࡦࡥࠬ࠮࠴ࡳࡦࡶࡢࡸࡷࡧࡣࡦࠪࠬࡠࡳࠨࠢࠣ෾").format(str(bstack1l111l1lll_opy_))
          bstack11llll1ll1_opy_ = bstack1ll11llll_opy_ + bstack111l1ll1_opy_
          bstack11ll11111_opy_ = bstack1l111l1lll_opy_[bstack11l1l_opy_ (u"࠭ࡦࡪ࡮ࡨࡣࡳࡧ࡭ࡦࠩ෿")] + bstack11l1l_opy_ (u"ࠧࡠࡤࡶࡸࡦࡩ࡫ࡠࡶࡨࡱࡵ࠴ࡰࡺࠩ฀")
          with open(bstack11ll11111_opy_, bstack11l1l_opy_ (u"ࠨࡹࠪก")):
            pass
          with open(bstack11ll11111_opy_, bstack11l1l_opy_ (u"ࠤࡺ࠯ࠧข")) as f:
            f.write(bstack11llll1ll1_opy_)
          import subprocess
          bstack1l11l1lll1_opy_ = subprocess.run([bstack11l1l_opy_ (u"ࠥࡴࡾࡺࡨࡰࡰࠥฃ"), bstack11ll11111_opy_])
          if os.path.exists(bstack11ll11111_opy_):
            os.unlink(bstack11ll11111_opy_)
          os._exit(bstack1l11l1lll1_opy_.returncode)
        else:
          if bstack1ll1llll_opy_(bstack1l111l1lll_opy_[bstack11l1l_opy_ (u"ࠫ࡫࡯࡬ࡦࡡࡱࡥࡲ࡫ࠧค")]):
            bstack1l111l1lll_opy_[bstack11l1l_opy_ (u"ࠬ࡬ࡩ࡭ࡧࡢࡲࡦࡳࡥࠨฅ")].remove(bstack11l1l_opy_ (u"࠭࠭࡮ࠩฆ"))
            bstack1l111l1lll_opy_[bstack11l1l_opy_ (u"ࠧࡧ࡫࡯ࡩࡤࡴࡡ࡮ࡧࠪง")].remove(bstack11l1l_opy_ (u"ࠨࡲࡧࡦࠬจ"))
            bstack1l111l1lll_opy_[bstack11l1l_opy_ (u"ࠩࡩ࡭ࡱ࡫࡟࡯ࡣࡰࡩࠬฉ")] = bstack1l111l1lll_opy_[bstack11l1l_opy_ (u"ࠪࡪ࡮ࡲࡥࡠࡰࡤࡱࡪ࠭ช")][0]
          bstack11l1lll1_opy_(bstack1llll1l11_opy_)
          sys.path.append(os.path.dirname(os.path.abspath(bstack1l111l1lll_opy_[bstack11l1l_opy_ (u"ࠫ࡫࡯࡬ࡦࡡࡱࡥࡲ࡫ࠧซ")])))
          sys.argv = sys.argv[2:]
          mod_globals = globals()
          mod_globals[bstack11l1l_opy_ (u"ࠬࡥ࡟࡯ࡣࡰࡩࡤࡥࠧฌ")] = bstack11l1l_opy_ (u"࠭࡟ࡠ࡯ࡤ࡭ࡳࡥ࡟ࠨญ")
          mod_globals[bstack11l1l_opy_ (u"ࠧࡠࡡࡩ࡭ࡱ࡫࡟ࡠࠩฎ")] = os.path.abspath(bstack1l111l1lll_opy_[bstack11l1l_opy_ (u"ࠨࡨ࡬ࡰࡪࡥ࡮ࡢ࡯ࡨࠫฏ")])
          exec(open(bstack1l111l1lll_opy_[bstack11l1l_opy_ (u"ࠩࡩ࡭ࡱ࡫࡟࡯ࡣࡰࡩࠬฐ")]).read(), mod_globals)
      except BaseException as e:
        try:
          traceback.print_exc()
          logger.error(bstack11l1l_opy_ (u"ࠪࡇࡦࡻࡧࡩࡶࠣࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࡀࠠࡼࡿࠪฑ").format(str(e)))
          for driver in bstack1ll111111l_opy_:
            bstack11ll111lll_opy_.append({
              bstack11l1l_opy_ (u"ࠫࡳࡧ࡭ࡦࠩฒ"): bstack1l111l1lll_opy_[bstack11l1l_opy_ (u"ࠬ࡬ࡩ࡭ࡧࡢࡲࡦࡳࡥࠨณ")],
              bstack11l1l_opy_ (u"࠭ࡥࡳࡴࡲࡶࠬด"): str(e),
              bstack11l1l_opy_ (u"ࠧࡪࡰࡧࡩࡽ࠭ต"): multiprocessing.current_process().name
            })
            bstack111lllll1l_opy_(driver, bstack11l1l_opy_ (u"ࠨࡨࡤ࡭ࡱ࡫ࡤࠨถ"), bstack11l1l_opy_ (u"ࠤࡖࡩࡸࡹࡩࡰࡰࠣࡪࡦ࡯࡬ࡦࡦࠣࡻ࡮ࡺࡨ࠻ࠢ࡟ࡲࠧท") + str(e))
        except Exception:
          pass
      finally:
        try:
          for driver in bstack1ll111111l_opy_:
            driver.quit()
        except Exception as e:
          pass
    else:
      percy.init(bstack1ll1ll111l_opy_, CONFIG, logger)
      bstack11ll1l1l1_opy_()
      bstack1llll1l11l_opy_()
      percy.bstack11111lll1_opy_()
      bstack1lll1l1ll1_opy_ = {
        bstack11l1l_opy_ (u"ࠪࡪ࡮ࡲࡥࡠࡰࡤࡱࡪ࠭ธ"): args[0],
        bstack11l1l_opy_ (u"ࠫࡈࡕࡎࡇࡋࡊࠫน"): CONFIG,
        bstack11l1l_opy_ (u"ࠬࡎࡕࡃࡡࡘࡖࡑ࠭บ"): bstack1l1l1ll1_opy_,
        bstack11l1l_opy_ (u"࠭ࡉࡔࡡࡄࡔࡕࡥࡁࡖࡖࡒࡑࡆ࡚ࡅࠨป"): bstack1ll1ll111l_opy_
      }
      if bstack11l1l_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪผ") in CONFIG:
        bstack1ll111l1ll_opy_ = bstack1l1ll11l1l_opy_(args, logger, CONFIG, bstack11ll1l1lll_opy_, bstack1ll1ll1lll_opy_)
        bstack11lllll11l_opy_ = bstack1ll111l1ll_opy_.bstack1llll1l1l_opy_(run_on_browserstack, bstack1lll1l1ll1_opy_, bstack1ll1llll_opy_(args))
      else:
        if bstack1ll1llll_opy_(args):
          bstack1lll1l1ll1_opy_[bstack11l1l_opy_ (u"ࠨࡨ࡬ࡰࡪࡥ࡮ࡢ࡯ࡨࠫฝ")] = args
          test = multiprocessing.Process(name=str(0),
                                         target=run_on_browserstack, args=(bstack1lll1l1ll1_opy_,))
          test.start()
          test.join()
        else:
          bstack11l1lll1_opy_(bstack1llll1l11_opy_)
          sys.path.append(os.path.dirname(os.path.abspath(args[0])))
          mod_globals = globals()
          mod_globals[bstack11l1l_opy_ (u"ࠩࡢࡣࡳࡧ࡭ࡦࡡࡢࠫพ")] = bstack11l1l_opy_ (u"ࠪࡣࡤࡳࡡࡪࡰࡢࡣࠬฟ")
          mod_globals[bstack11l1l_opy_ (u"ࠫࡤࡥࡦࡪ࡮ࡨࡣࡤ࠭ภ")] = os.path.abspath(args[0])
          sys.argv = sys.argv[2:]
          exec(open(args[0]).read(), mod_globals)
  elif bstack1l1lllll1l_opy_ == bstack11l1l_opy_ (u"ࠬࡶࡡࡣࡱࡷࠫม") or bstack1l1lllll1l_opy_ == bstack11l1l_opy_ (u"࠭ࡲࡰࡤࡲࡸࠬย"):
    percy.init(bstack1ll1ll111l_opy_, CONFIG, logger)
    percy.bstack11111lll1_opy_()
    try:
      from pabot import pabot
    except Exception as e:
      bstack1ll1111l11_opy_(e, bstack1l111l1l11_opy_)
    bstack11ll1l1l1_opy_()
    bstack11l1lll1_opy_(bstack1l11l111l1_opy_)
    if bstack11ll1l1lll_opy_:
      bstack1lll1l1lll_opy_(bstack1l11l111l1_opy_, args)
      if bstack11l1l_opy_ (u"ࠧ࠮࠯ࡳࡶࡴࡩࡥࡴࡵࡨࡷࠬร") in args:
        i = args.index(bstack11l1l_opy_ (u"ࠨ࠯࠰ࡴࡷࡵࡣࡦࡵࡶࡩࡸ࠭ฤ"))
        args.pop(i)
        args.pop(i)
      if bstack11l1l_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬล") not in CONFIG:
        CONFIG[bstack11l1l_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ฦ")] = [{}]
        bstack1ll1ll1lll_opy_ = 1
      if bstack1l1l11ll1_opy_ == 0:
        bstack1l1l11ll1_opy_ = 1
      args.insert(0, str(bstack1l1l11ll1_opy_))
      args.insert(0, str(bstack11l1l_opy_ (u"ࠫ࠲࠳ࡰࡳࡱࡦࡩࡸࡹࡥࡴࠩว")))
    if bstack1ll1llll11_opy_.on():
      try:
        from robot.run import USAGE
        from robot.utils import ArgumentParser
        from pabot.arguments import _parse_pabot_args
        bstack1l111l1l_opy_, pabot_args = _parse_pabot_args(args)
        opts, bstack11ll1lll11_opy_ = ArgumentParser(
            USAGE,
            auto_pythonpath=False,
            auto_argumentfile=True,
            env_options=bstack11l1l_opy_ (u"ࠧࡘࡏࡃࡑࡗࡣࡔࡖࡔࡊࡑࡑࡗࠧศ"),
        ).parse_args(bstack1l111l1l_opy_)
        bstack1l1ll1l11l_opy_ = args.index(bstack1l111l1l_opy_[0]) if len(bstack1l111l1l_opy_) > 0 else len(args)
        args.insert(bstack1l1ll1l11l_opy_, str(bstack11l1l_opy_ (u"࠭࠭࠮࡮࡬ࡷࡹ࡫࡮ࡦࡴࠪษ")))
        args.insert(bstack1l1ll1l11l_opy_ + 1, str(os.path.join(os.path.dirname(os.path.realpath(__file__)), bstack11l1l_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱ࡟ࡳࡱࡥࡳࡹࡥ࡬ࡪࡵࡷࡩࡳ࡫ࡲ࠯ࡲࡼࠫส"))))
        if bstack11llllll1l_opy_.bstack1ll111l111_opy_(CONFIG):
          args.insert(bstack1l1ll1l11l_opy_, str(bstack11l1l_opy_ (u"ࠨ࠯࠰ࡰ࡮ࡹࡴࡦࡰࡨࡶࠬห")))
          args.insert(bstack1l1ll1l11l_opy_ + 1, str(bstack11l1l_opy_ (u"ࠩࡕࡩࡹࡸࡹࡇࡣ࡬ࡰࡪࡪ࠺ࡼࡿࠪฬ").format(bstack11llllll1l_opy_.bstack1111lllll_opy_(CONFIG))))
        if bstack1llll1ll1_opy_(os.environ.get(bstack11l1l_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡕࡉࡗ࡛ࡎࠨอ"))) and str(os.environ.get(bstack11l1l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡖࡊࡘࡕࡏࡡࡗࡉࡘ࡚ࡓࠨฮ"), bstack11l1l_opy_ (u"ࠬࡴࡵ࡭࡮ࠪฯ"))) != bstack11l1l_opy_ (u"࠭࡮ࡶ࡮࡯ࠫะ"):
          for bstack1ll111lll_opy_ in bstack11ll1lll11_opy_:
            args.remove(bstack1ll111lll_opy_)
          test_files = os.environ.get(bstack11l1l_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡒࡆࡔࡘࡒࡤ࡚ࡅࡔࡖࡖࠫั")).split(bstack11l1l_opy_ (u"ࠨ࠮ࠪา"))
          for bstack1l111llll1_opy_ in test_files:
            args.append(bstack1l111llll1_opy_)
      except Exception as e:
        logger.error(bstack11l1l_opy_ (u"ࠤࡈࡶࡷࡵࡲࠡࡹ࡫࡭ࡱ࡫ࠠࡢࡶࡷࡥࡨ࡮ࡩ࡯ࡩࠣࡰ࡮ࡹࡴࡦࡰࡨࡶࠥ࡬࡯ࡳࠢࡾࢁ࠳ࠦࡅࡳࡴࡲࡶࠥ࠳ࠠࡼࡿࠥำ").format(bstack1l111ll1ll_opy_, e))
    pabot.main(args)
  elif bstack1l1lllll1l_opy_ == bstack11l1l_opy_ (u"ࠪࡶࡴࡨ࡯ࡵ࠯࡬ࡲࡹ࡫ࡲ࡯ࡣ࡯ࠫิ"):
    try:
      from robot import run_cli
    except Exception as e:
      bstack1ll1111l11_opy_(e, bstack1l111l1l11_opy_)
    for a in args:
      if bstack11l1l_opy_ (u"ࠫࡇ࡙ࡔࡂࡅࡎࡔࡑࡇࡔࡇࡑࡕࡑࡎࡔࡄࡆ࡚ࠪี") in a:
        bstack11ll1111ll_opy_ = int(a.split(bstack11l1l_opy_ (u"ࠬࡀࠧึ"))[1])
      if bstack11l1l_opy_ (u"࠭ࡂࡔࡖࡄࡇࡐࡊࡅࡇࡎࡒࡇࡆࡒࡉࡅࡇࡑࡘࡎࡌࡉࡆࡔࠪื") in a:
        bstack11l11l1ll1_opy_ = str(a.split(bstack11l1l_opy_ (u"ࠧ࠻ุࠩ"))[1])
      if bstack11l1l_opy_ (u"ࠨࡄࡖࡘࡆࡉࡋࡄࡎࡌࡅࡗࡍࡓࠨู") in a:
        bstack1l1l11ll1l_opy_ = str(a.split(bstack11l1l_opy_ (u"ࠩ࠽ฺࠫ"))[1])
    bstack11l1ll11_opy_ = None
    bstack1l1ll11l_opy_ = None
    if bstack11l1l_opy_ (u"ࠪ࠱࠲ࡨࡳࡵࡣࡦ࡯ࡤ࡯ࡴࡦ࡯ࡢ࡭ࡳࡪࡥࡹࠩ฻") in args:
      i = args.index(bstack11l1l_opy_ (u"ࠫ࠲࠳ࡢࡴࡶࡤࡧࡰࡥࡩࡵࡧࡰࡣ࡮ࡴࡤࡦࡺࠪ฼"))
      args.pop(i)
      bstack11l1ll11_opy_ = args.pop(i)
    if bstack11l1l_opy_ (u"ࠬ࠳࠭ࡣࡵࡷࡥࡨࡱ࡟ࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡡ࡬ࡲࡩ࡫ࡸࠨ฽") in args:
      i = args.index(bstack11l1l_opy_ (u"࠭࠭࠮ࡤࡶࡸࡦࡩ࡫ࡠࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡢ࡭ࡳࡪࡥࡹࠩ฾"))
      args.pop(i)
      bstack1l1ll11l_opy_ = args.pop(i)
    if bstack11l1ll11_opy_ is not None:
      global bstack11ll1111_opy_
      bstack11ll1111_opy_ = bstack11l1ll11_opy_
    if bstack1l1ll11l_opy_ is not None and int(bstack11ll1111ll_opy_) < 0:
      bstack11ll1111ll_opy_ = int(bstack1l1ll11l_opy_)
    bstack11l1lll1_opy_(bstack1l11l111l1_opy_)
    run_cli(args)
    if bstack11l1l_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱ࡟ࡦࡴࡵࡳࡷࡥ࡬ࡪࡵࡷࠫ฿") in multiprocessing.current_process().__dict__.keys():
      for bstack11llll1l1l_opy_ in multiprocessing.current_process().bstack_error_list:
        bstack11ll111lll_opy_.append(bstack11llll1l1l_opy_)
  elif bstack1l1lllll1l_opy_ == bstack11l1l_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࠨเ"):
    bstack1l1l1l11ll_opy_ = bstack11ll1l11l1_opy_(args, logger, CONFIG, bstack11ll1l1lll_opy_)
    bstack1l1l1l11ll_opy_.bstack1llll11111_opy_()
    bstack11ll1l1l1_opy_()
    bstack1l1llll1ll_opy_ = True
    bstack1ll1l1ll_opy_ = bstack1l1l1l11ll_opy_.bstack111l111l_opy_()
    bstack1l1l1l11ll_opy_.bstack1lll1l1ll1_opy_(bstack1lllllll1_opy_)
    bstack1l1l1l11ll_opy_.bstack11ll1l1ll_opy_()
    bstack1lll1l1l1_opy_(bstack1l1lllll1l_opy_, CONFIG, bstack1l1l1l11ll_opy_.bstack1ll1l11ll1_opy_())
    bstack1l1llllll_opy_ = bstack1l1l1l11ll_opy_.bstack1llll1l1l_opy_(bstack1l11l111l_opy_, {
      bstack11l1l_opy_ (u"ࠩࡋ࡙ࡇࡥࡕࡓࡎࠪแ"): bstack1l1l1ll1_opy_,
      bstack11l1l_opy_ (u"ࠪࡍࡘࡥࡁࡑࡒࡢࡅ࡚࡚ࡏࡎࡃࡗࡉࠬโ"): bstack1ll1ll111l_opy_,
      bstack11l1l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡅ࡚࡚ࡏࡎࡃࡗࡍࡔࡔࠧใ"): bstack11ll1l1lll_opy_
    })
    try:
      bstack11l1l11l11_opy_, bstack1ll11ll1l_opy_ = map(list, zip(*bstack1l1llllll_opy_))
      bstack1l11lll111_opy_ = bstack11l1l11l11_opy_[0]
      for status_code in bstack1ll11ll1l_opy_:
        if status_code != 0:
          bstack1llll1lll1_opy_ = status_code
          break
    except Exception as e:
      logger.debug(bstack11l1l_opy_ (u"࡛ࠧ࡮ࡢࡤ࡯ࡩࠥࡺ࡯ࠡࡵࡤࡺࡪࠦࡥࡳࡴࡲࡶࡸࠦࡡ࡯ࡦࠣࡷࡹࡧࡴࡶࡵࠣࡧࡴࡪࡥ࠯ࠢࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥࡀࠠࡼࡿࠥไ").format(str(e)))
  elif bstack1l1lllll1l_opy_ == bstack11l1l_opy_ (u"࠭ࡢࡦࡪࡤࡺࡪ࠭ๅ"):
    try:
      from behave.__main__ import main as bstack1ll11l11l1_opy_
      from behave.configuration import Configuration
    except Exception as e:
      bstack1ll1111l11_opy_(e, bstack1l1ll11l1_opy_)
    bstack11ll1l1l1_opy_()
    bstack1l1llll1ll_opy_ = True
    bstack1llll11l1l_opy_ = 1
    if bstack11l1l_opy_ (u"ࠧࡱࡣࡵࡥࡱࡲࡥ࡭ࡵࡓࡩࡷࡖ࡬ࡢࡶࡩࡳࡷࡳࠧๆ") in CONFIG:
      bstack1llll11l1l_opy_ = CONFIG[bstack11l1l_opy_ (u"ࠨࡲࡤࡶࡦࡲ࡬ࡦ࡮ࡶࡔࡪࡸࡐ࡭ࡣࡷࡪࡴࡸ࡭ࠨ็")]
    if bstack11l1l_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷ่ࠬ") in CONFIG:
      bstack1llll111ll_opy_ = int(bstack1llll11l1l_opy_) * int(len(CONFIG[bstack11l1l_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ้࠭")]))
    else:
      bstack1llll111ll_opy_ = int(bstack1llll11l1l_opy_)
    config = Configuration(args)
    bstack1ll1l1l11l_opy_ = config.paths
    if len(bstack1ll1l1l11l_opy_) == 0:
      import glob
      pattern = bstack11l1l_opy_ (u"ࠫ࠯࠰࠯ࠫ࠰ࡩࡩࡦࡺࡵࡳࡧ๊ࠪ")
      bstack11l111l1l1_opy_ = glob.glob(pattern, recursive=True)
      args.extend(bstack11l111l1l1_opy_)
      config = Configuration(args)
      bstack1ll1l1l11l_opy_ = config.paths
    bstack1l11l1ll_opy_ = [os.path.normpath(item) for item in bstack1ll1l1l11l_opy_]
    bstack11l1l1lll_opy_ = [os.path.normpath(item) for item in args]
    bstack1l1l11111l_opy_ = [item for item in bstack11l1l1lll_opy_ if item not in bstack1l11l1ll_opy_]
    import platform as pf
    if pf.system().lower() == bstack11l1l_opy_ (u"ࠬࡽࡩ࡯ࡦࡲࡻࡸ๋࠭"):
      from pathlib import PureWindowsPath, PurePosixPath
      bstack1l11l1ll_opy_ = [str(PurePosixPath(PureWindowsPath(bstack1ll11lll1l_opy_)))
                    for bstack1ll11lll1l_opy_ in bstack1l11l1ll_opy_]
    bstack11l1llll1_opy_ = []
    for spec in bstack1l11l1ll_opy_:
      bstack11l1l1l1_opy_ = []
      bstack11l1l1l1_opy_ += bstack1l1l11111l_opy_
      bstack11l1l1l1_opy_.append(spec)
      bstack11l1llll1_opy_.append(bstack11l1l1l1_opy_)
    execution_items = []
    for bstack11l1l1l1_opy_ in bstack11l1llll1_opy_:
      if bstack11l1l_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩ์") in CONFIG:
        for index, _ in enumerate(CONFIG[bstack11l1l_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪํ")]):
          item = {}
          item[bstack11l1l_opy_ (u"ࠨࡣࡵ࡫ࠬ๎")] = bstack11l1l_opy_ (u"ࠩࠣࠫ๏").join(bstack11l1l1l1_opy_)
          item[bstack11l1l_opy_ (u"ࠪ࡭ࡳࡪࡥࡹࠩ๐")] = index
          execution_items.append(item)
      else:
        item = {}
        item[bstack11l1l_opy_ (u"ࠫࡦࡸࡧࠨ๑")] = bstack11l1l_opy_ (u"ࠬࠦࠧ๒").join(bstack11l1l1l1_opy_)
        item[bstack11l1l_opy_ (u"࠭ࡩ࡯ࡦࡨࡼࠬ๓")] = 0
        execution_items.append(item)
    bstack1l1111111l_opy_ = bstack11ll111l_opy_(execution_items, bstack1llll111ll_opy_)
    for execution_item in bstack1l1111111l_opy_:
      bstack1l111111l_opy_ = []
      for item in execution_item:
        bstack1l111111l_opy_.append(bstack11l11l1l1l_opy_(name=str(item[bstack11l1l_opy_ (u"ࠧࡪࡰࡧࡩࡽ࠭๔")]),
                                             target=bstack1ll1111lll_opy_,
                                             args=(item[bstack11l1l_opy_ (u"ࠨࡣࡵ࡫ࠬ๕")],)))
      for t in bstack1l111111l_opy_:
        t.start()
      for t in bstack1l111111l_opy_:
        t.join()
  else:
    bstack1ll11l111l_opy_(bstack1l111l1l1_opy_)
  if not bstack1l111l1lll_opy_:
    bstack1lll1lll1l_opy_()
    if(bstack1l1lllll1l_opy_ in [bstack11l1l_opy_ (u"ࠩࡥࡩ࡭ࡧࡶࡦࠩ๖"), bstack11l1l_opy_ (u"ࠪࡴࡾࡺࡥࡴࡶࠪ๗")]):
      bstack1l1lll111_opy_()
  bstack1l1lll1l11_opy_.bstack1l11l11ll1_opy_()
def browserstack_initialize(bstack1111l11l1_opy_=None):
  logger.info(bstack11l1l_opy_ (u"ࠫࡗࡻ࡮࡯࡫ࡱ࡫࡙ࠥࡄࡌࠢࡺ࡭ࡹ࡮ࠠࡢࡴࡪࡷ࠿ࠦࠧ๘") + str(bstack1111l11l1_opy_))
  run_on_browserstack(bstack1111l11l1_opy_, None, True)
@measure(event_name=EVENTS.bstack1l11l111_opy_, stage=STAGE.bstack1lll1l11l_opy_, bstack1l1l1llll_opy_=bstack11l1ll1l_opy_)
def bstack1lll1lll1l_opy_():
  global CONFIG
  global bstack1llll1lll_opy_
  global bstack1llll1lll1_opy_
  global bstack111l11ll_opy_
  global bstack1l1ll11111_opy_
  bstack1ll111ll1_opy_.bstack1ll1ll1l1_opy_()
  if cli.is_running():
    bstack1l1l1lllll_opy_.invoke(bstack111111lll_opy_.bstack1l1111lll1_opy_)
  else:
    bstack1111l1ll_opy_ = bstack11llllll1l_opy_.bstack11l1l11ll1_opy_(config=CONFIG)
    bstack1111l1ll_opy_.bstack1111l1l1_opy_(CONFIG)
  if bstack1llll1lll_opy_ == bstack11l1l_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸࠬ๙"):
    if not cli.is_enabled(CONFIG):
      bstack1ll1llll11_opy_.stop()
  else:
    bstack1ll1llll11_opy_.stop()
  if not cli.is_enabled(CONFIG):
    bstack11llll111_opy_.bstack111llll1ll_opy_()
  if bstack11l1l_opy_ (u"࠭ࡴࡶࡴࡥࡳࡘࡩࡡ࡭ࡧࠪ๚") in CONFIG and str(CONFIG[bstack11l1l_opy_ (u"ࠧࡵࡷࡵࡦࡴ࡙ࡣࡢ࡮ࡨࠫ๛")]).lower() != bstack11l1l_opy_ (u"ࠨࡨࡤࡰࡸ࡫ࠧ๜"):
    hashed_id, bstack11l11llll_opy_ = bstack1lllllllll_opy_()
  else:
    hashed_id, bstack11l11llll_opy_ = get_build_link()
  bstack11l11111l1_opy_(hashed_id)
  logger.info(bstack11l1l_opy_ (u"ࠩࡖࡈࡐࠦࡲࡶࡰࠣࡩࡳࡪࡥࡥࠢࡩࡳࡷࠦࡩࡥ࠼ࠪ๝") + bstack1l1ll11111_opy_.get_property(bstack11l1l_opy_ (u"ࠪࡷࡩࡱࡒࡶࡰࡌࡨࠬ๞"), bstack11l1l_opy_ (u"ࠫࠬ๟")) + bstack11l1l_opy_ (u"ࠬ࠲ࠠࡵࡧࡶࡸ࡭ࡻࡢࠡ࡫ࡧ࠾ࠥ࠭๠") + os.getenv(bstack11l1l_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡕࡖࡋࡇࠫ๡"), bstack11l1l_opy_ (u"ࠧࠨ๢")))
  if hashed_id is not None and bstack1lll11l11_opy_() != -1:
    sessions = bstack1ll1l111l_opy_(hashed_id)
    bstack11l111ll_opy_(sessions, bstack11l11llll_opy_)
  if bstack1llll1lll_opy_ == bstack11l1l_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࠨ๣") and bstack1llll1lll1_opy_ != 0:
    sys.exit(bstack1llll1lll1_opy_)
  if bstack1llll1lll_opy_ == bstack11l1l_opy_ (u"ࠩࡥࡩ࡭ࡧࡶࡦࠩ๤") and bstack111l11ll_opy_ != 0:
    sys.exit(bstack111l11ll_opy_)
def bstack11l11111l1_opy_(new_id):
    global bstack1ll1111l_opy_
    bstack1ll1111l_opy_ = new_id
def bstack1l11l11ll_opy_(bstack1111ll111_opy_):
  if bstack1111ll111_opy_:
    return bstack1111ll111_opy_.capitalize()
  else:
    return bstack11l1l_opy_ (u"ࠪࠫ๥")
@measure(event_name=EVENTS.bstack1111ll11l_opy_, stage=STAGE.bstack1lll1l11l_opy_, bstack1l1l1llll_opy_=bstack11l1ll1l_opy_)
def bstack11111ll1l_opy_(bstack1l11111ll1_opy_):
  if bstack11l1l_opy_ (u"ࠫࡳࡧ࡭ࡦࠩ๦") in bstack1l11111ll1_opy_ and bstack1l11111ll1_opy_[bstack11l1l_opy_ (u"ࠬࡴࡡ࡮ࡧࠪ๧")] != bstack11l1l_opy_ (u"࠭ࠧ๨"):
    return bstack1l11111ll1_opy_[bstack11l1l_opy_ (u"ࠧ࡯ࡣࡰࡩࠬ๩")]
  else:
    bstack1l1l1llll_opy_ = bstack11l1l_opy_ (u"ࠣࠤ๪")
    if bstack11l1l_opy_ (u"ࠩࡧࡩࡻ࡯ࡣࡦࠩ๫") in bstack1l11111ll1_opy_ and bstack1l11111ll1_opy_[bstack11l1l_opy_ (u"ࠪࡨࡪࡼࡩࡤࡧࠪ๬")] != None:
      bstack1l1l1llll_opy_ += bstack1l11111ll1_opy_[bstack11l1l_opy_ (u"ࠫࡩ࡫ࡶࡪࡥࡨࠫ๭")] + bstack11l1l_opy_ (u"ࠧ࠲ࠠࠣ๮")
      if bstack1l11111ll1_opy_[bstack11l1l_opy_ (u"࠭࡯ࡴࠩ๯")] == bstack11l1l_opy_ (u"ࠢࡪࡱࡶࠦ๰"):
        bstack1l1l1llll_opy_ += bstack11l1l_opy_ (u"ࠣ࡫ࡒࡗࠥࠨ๱")
      bstack1l1l1llll_opy_ += (bstack1l11111ll1_opy_[bstack11l1l_opy_ (u"ࠩࡲࡷࡤࡼࡥࡳࡵ࡬ࡳࡳ࠭๲")] or bstack11l1l_opy_ (u"ࠪࠫ๳"))
      return bstack1l1l1llll_opy_
    else:
      bstack1l1l1llll_opy_ += bstack1l11l11ll_opy_(bstack1l11111ll1_opy_[bstack11l1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࠬ๴")]) + bstack11l1l_opy_ (u"ࠧࠦࠢ๵") + (
              bstack1l11111ll1_opy_[bstack11l1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸ࡟ࡷࡧࡵࡷ࡮ࡵ࡮ࠨ๶")] or bstack11l1l_opy_ (u"ࠧࠨ๷")) + bstack11l1l_opy_ (u"ࠣ࠮ࠣࠦ๸")
      if bstack1l11111ll1_opy_[bstack11l1l_opy_ (u"ࠩࡲࡷࠬ๹")] == bstack11l1l_opy_ (u"࡛ࠥ࡮ࡴࡤࡰࡹࡶࠦ๺"):
        bstack1l1l1llll_opy_ += bstack11l1l_opy_ (u"ࠦ࡜࡯࡮ࠡࠤ๻")
      bstack1l1l1llll_opy_ += bstack1l11111ll1_opy_[bstack11l1l_opy_ (u"ࠬࡵࡳࡠࡸࡨࡶࡸ࡯࡯࡯ࠩ๼")] or bstack11l1l_opy_ (u"࠭ࠧ๽")
      return bstack1l1l1llll_opy_
@measure(event_name=EVENTS.bstack11111l111_opy_, stage=STAGE.bstack1lll1l11l_opy_, bstack1l1l1llll_opy_=bstack11l1ll1l_opy_)
def bstack1lllllll11_opy_(bstack1111l1lll_opy_):
  if bstack1111l1lll_opy_ == bstack11l1l_opy_ (u"ࠢࡥࡱࡱࡩࠧ๾"):
    return bstack11l1l_opy_ (u"ࠨ࠾ࡷࡨࠥࡩ࡬ࡢࡵࡶࡁࠧࡨࡳࡵࡣࡦ࡯࠲ࡪࡡࡵࡣࠥࠤࡸࡺࡹ࡭ࡧࡀࠦࡨࡵ࡬ࡰࡴ࠽࡫ࡷ࡫ࡥ࡯࠽ࠥࡂࡁ࡬࡯࡯ࡶࠣࡧࡴࡲ࡯ࡳ࠿ࠥ࡫ࡷ࡫ࡥ࡯ࠤࡁࡇࡴࡳࡰ࡭ࡧࡷࡩࡩࡂ࠯ࡧࡱࡱࡸࡃࡂ࠯ࡵࡦࡁࠫ๿")
  elif bstack1111l1lll_opy_ == bstack11l1l_opy_ (u"ࠤࡩࡥ࡮ࡲࡥࡥࠤ຀"):
    return bstack11l1l_opy_ (u"ࠪࡀࡹࡪࠠࡤ࡮ࡤࡷࡸࡃࠢࡣࡵࡷࡥࡨࡱ࠭ࡥࡣࡷࡥࠧࠦࡳࡵࡻ࡯ࡩࡂࠨࡣࡰ࡮ࡲࡶ࠿ࡸࡥࡥ࠽ࠥࡂࡁ࡬࡯࡯ࡶࠣࡧࡴࡲ࡯ࡳ࠿ࠥࡶࡪࡪࠢ࠿ࡈࡤ࡭ࡱ࡫ࡤ࠽࠱ࡩࡳࡳࡺ࠾࠽࠱ࡷࡨࡃ࠭ກ")
  elif bstack1111l1lll_opy_ == bstack11l1l_opy_ (u"ࠦࡵࡧࡳࡴࡧࡧࠦຂ"):
    return bstack11l1l_opy_ (u"ࠬࡂࡴࡥࠢࡦࡰࡦࡹࡳ࠾ࠤࡥࡷࡹࡧࡣ࡬࠯ࡧࡥࡹࡧࠢࠡࡵࡷࡽࡱ࡫࠽ࠣࡥࡲࡰࡴࡸ࠺ࡨࡴࡨࡩࡳࡁࠢ࠿࠾ࡩࡳࡳࡺࠠࡤࡱ࡯ࡳࡷࡃࠢࡨࡴࡨࡩࡳࠨ࠾ࡑࡣࡶࡷࡪࡪ࠼࠰ࡨࡲࡲࡹࡄ࠼࠰ࡶࡧࡂࠬ຃")
  elif bstack1111l1lll_opy_ == bstack11l1l_opy_ (u"ࠨࡥࡳࡴࡲࡶࠧຄ"):
    return bstack11l1l_opy_ (u"ࠧ࠽ࡶࡧࠤࡨࡲࡡࡴࡵࡀࠦࡧࡹࡴࡢࡥ࡮࠱ࡩࡧࡴࡢࠤࠣࡷࡹࡿ࡬ࡦ࠿ࠥࡧࡴࡲ࡯ࡳ࠼ࡵࡩࡩࡁࠢ࠿࠾ࡩࡳࡳࡺࠠࡤࡱ࡯ࡳࡷࡃࠢࡳࡧࡧࠦࡃࡋࡲࡳࡱࡵࡀ࠴࡬࡯࡯ࡶࡁࡀ࠴ࡺࡤ࠿ࠩ຅")
  elif bstack1111l1lll_opy_ == bstack11l1l_opy_ (u"ࠣࡶ࡬ࡱࡪࡵࡵࡵࠤຆ"):
    return bstack11l1l_opy_ (u"ࠩ࠿ࡸࡩࠦࡣ࡭ࡣࡶࡷࡂࠨࡢࡴࡶࡤࡧࡰ࠳ࡤࡢࡶࡤࠦࠥࡹࡴࡺ࡮ࡨࡁࠧࡩ࡯࡭ࡱࡵ࠾ࠨ࡫ࡥࡢ࠵࠵࠺ࡀࠨ࠾࠽ࡨࡲࡲࡹࠦࡣࡰ࡮ࡲࡶࡂࠨࠣࡦࡧࡤ࠷࠷࠼ࠢ࠿ࡖ࡬ࡱࡪࡵࡵࡵ࠾࠲ࡪࡴࡴࡴ࠿࠾࠲ࡸࡩࡄࠧງ")
  elif bstack1111l1lll_opy_ == bstack11l1l_opy_ (u"ࠥࡶࡺࡴ࡮ࡪࡰࡪࠦຈ"):
    return bstack11l1l_opy_ (u"ࠫࡁࡺࡤࠡࡥ࡯ࡥࡸࡹ࠽ࠣࡤࡶࡸࡦࡩ࡫࠮ࡦࡤࡸࡦࠨࠠࡴࡶࡼࡰࡪࡃࠢࡤࡱ࡯ࡳࡷࡀࡢ࡭ࡣࡦ࡯ࡀࠨ࠾࠽ࡨࡲࡲࡹࠦࡣࡰ࡮ࡲࡶࡂࠨࡢ࡭ࡣࡦ࡯ࠧࡄࡒࡶࡰࡱ࡭ࡳ࡭࠼࠰ࡨࡲࡲࡹࡄ࠼࠰ࡶࡧࡂࠬຉ")
  else:
    return bstack11l1l_opy_ (u"ࠬࡂࡴࡥࠢࡤࡰ࡮࡭࡮࠾ࠤࡦࡩࡳࡺࡥࡳࠤࠣࡧࡱࡧࡳࡴ࠿ࠥࡦࡸࡺࡡࡤ࡭࠰ࡨࡦࡺࡡࠣࠢࡶࡸࡾࡲࡥ࠾ࠤࡦࡳࡱࡵࡲ࠻ࡤ࡯ࡥࡨࡱ࠻ࠣࡀ࠿ࡪࡴࡴࡴࠡࡥࡲࡰࡴࡸ࠽ࠣࡤ࡯ࡥࡨࡱࠢ࠿ࠩຊ") + bstack1l11l11ll_opy_(
      bstack1111l1lll_opy_) + bstack11l1l_opy_ (u"࠭࠼࠰ࡨࡲࡲࡹࡄ࠼࠰ࡶࡧࡂࠬ຋")
def bstack1l1ll111l_opy_(session):
  return bstack11l1l_opy_ (u"ࠧ࠽ࡶࡵࠤࡨࡲࡡࡴࡵࡀࠦࡧࡹࡴࡢࡥ࡮࠱ࡷࡵࡷࠣࡀ࠿ࡸࡩࠦࡣ࡭ࡣࡶࡷࡂࠨࡢࡴࡶࡤࡧࡰ࠳ࡤࡢࡶࡤࠤࡸ࡫ࡳࡴ࡫ࡲࡲ࠲ࡴࡡ࡮ࡧࠥࡂࡁࡧࠠࡩࡴࡨࡪࡂࠨࡻࡾࠤࠣࡸࡦࡸࡧࡦࡶࡀࠦࡤࡨ࡬ࡢࡰ࡮ࠦࡃࢁࡽ࠽࠱ࡤࡂࡁ࠵ࡴࡥࡀࡾࢁࢀࢃ࠼ࡵࡦࠣࡥࡱ࡯ࡧ࡯࠿ࠥࡧࡪࡴࡴࡦࡴࠥࠤࡨࡲࡡࡴࡵࡀࠦࡧࡹࡴࡢࡥ࡮࠱ࡩࡧࡴࡢࠤࡁࡿࢂࡂ࠯ࡵࡦࡁࡀࡹࡪࠠࡢ࡮࡬࡫ࡳࡃࠢࡤࡧࡱࡸࡪࡸࠢࠡࡥ࡯ࡥࡸࡹ࠽ࠣࡤࡶࡸࡦࡩ࡫࠮ࡦࡤࡸࡦࠨ࠾ࡼࡿ࠿࠳ࡹࡪ࠾࠽ࡶࡧࠤࡦࡲࡩࡨࡰࡀࠦࡨ࡫࡮ࡵࡧࡵࠦࠥࡩ࡬ࡢࡵࡶࡁࠧࡨࡳࡵࡣࡦ࡯࠲ࡪࡡࡵࡣࠥࡂࢀࢃ࠼࠰ࡶࡧࡂࡁࡺࡤࠡࡣ࡯࡭࡬ࡴ࠽ࠣࡥࡨࡲࡹ࡫ࡲࠣࠢࡦࡰࡦࡹࡳ࠾ࠤࡥࡷࡹࡧࡣ࡬࠯ࡧࡥࡹࡧࠢ࠿ࡽࢀࡀ࠴ࡺࡤ࠿࠾࠲ࡸࡷࡄࠧຌ").format(
    session[bstack11l1l_opy_ (u"ࠨࡲࡸࡦࡱ࡯ࡣࡠࡷࡵࡰࠬຍ")], bstack11111ll1l_opy_(session), bstack1lllllll11_opy_(session[bstack11l1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡵࡷࡥࡹࡻࡳࠨຎ")]),
    bstack1lllllll11_opy_(session[bstack11l1l_opy_ (u"ࠪࡷࡹࡧࡴࡶࡵࠪຏ")]),
    bstack1l11l11ll_opy_(session[bstack11l1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࠬຐ")] or session[bstack11l1l_opy_ (u"ࠬࡪࡥࡷ࡫ࡦࡩࠬຑ")] or bstack11l1l_opy_ (u"࠭ࠧຒ")) + bstack11l1l_opy_ (u"ࠢࠡࠤຓ") + (session[bstack11l1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡡࡹࡩࡷࡹࡩࡰࡰࠪດ")] or bstack11l1l_opy_ (u"ࠩࠪຕ")),
    session[bstack11l1l_opy_ (u"ࠪࡳࡸ࠭ຖ")] + bstack11l1l_opy_ (u"ࠦࠥࠨທ") + session[bstack11l1l_opy_ (u"ࠬࡵࡳࡠࡸࡨࡶࡸ࡯࡯࡯ࠩຘ")], session[bstack11l1l_opy_ (u"࠭ࡤࡶࡴࡤࡸ࡮ࡵ࡮ࠨນ")] or bstack11l1l_opy_ (u"ࠧࠨບ"),
    session[bstack11l1l_opy_ (u"ࠨࡥࡵࡩࡦࡺࡥࡥࡡࡤࡸࠬປ")] if session[bstack11l1l_opy_ (u"ࠩࡦࡶࡪࡧࡴࡦࡦࡢࡥࡹ࠭ຜ")] else bstack11l1l_opy_ (u"ࠪࠫຝ"))
@measure(event_name=EVENTS.bstack11111l11l_opy_, stage=STAGE.bstack1lll1l11l_opy_, bstack1l1l1llll_opy_=bstack11l1ll1l_opy_)
def bstack11l111ll_opy_(sessions, bstack11l11llll_opy_):
  try:
    bstack1lll11l1l1_opy_ = bstack11l1l_opy_ (u"ࠦࠧພ")
    if not os.path.exists(bstack11l1llll_opy_):
      os.mkdir(bstack11l1llll_opy_)
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), bstack11l1l_opy_ (u"ࠬࡧࡳࡴࡧࡷࡷ࠴ࡸࡥࡱࡱࡵࡸ࠳࡮ࡴ࡮࡮ࠪຟ")), bstack11l1l_opy_ (u"࠭ࡲࠨຠ")) as f:
      bstack1lll11l1l1_opy_ = f.read()
    bstack1lll11l1l1_opy_ = bstack1lll11l1l1_opy_.replace(bstack11l1l_opy_ (u"ࠧࡼࠧࡕࡉࡘ࡛ࡌࡕࡕࡢࡇࡔ࡛ࡎࡕࠧࢀࠫມ"), str(len(sessions)))
    bstack1lll11l1l1_opy_ = bstack1lll11l1l1_opy_.replace(bstack11l1l_opy_ (u"ࠨࡽࠨࡆ࡚ࡏࡌࡅࡡࡘࡖࡑࠫࡽࠨຢ"), bstack11l11llll_opy_)
    bstack1lll11l1l1_opy_ = bstack1lll11l1l1_opy_.replace(bstack11l1l_opy_ (u"ࠩࡾࠩࡇ࡛ࡉࡍࡆࡢࡒࡆࡓࡅࠦࡿࠪຣ"),
                                              sessions[0].get(bstack11l1l_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡡࡱࡥࡲ࡫ࠧ຤")) if sessions[0] else bstack11l1l_opy_ (u"ࠫࠬລ"))
    with open(os.path.join(bstack11l1llll_opy_, bstack11l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠱ࡷ࡫ࡰࡰࡴࡷ࠲࡭ࡺ࡭࡭ࠩ຦")), bstack11l1l_opy_ (u"࠭ࡷࠨວ")) as stream:
      stream.write(bstack1lll11l1l1_opy_.split(bstack11l1l_opy_ (u"ࠧࡼࠧࡖࡉࡘ࡙ࡉࡐࡐࡖࡣࡉࡇࡔࡂࠧࢀࠫຨ"))[0])
      for session in sessions:
        stream.write(bstack1l1ll111l_opy_(session))
      stream.write(bstack1lll11l1l1_opy_.split(bstack11l1l_opy_ (u"ࠨࡽࠨࡗࡊ࡙ࡓࡊࡑࡑࡗࡤࡊࡁࡕࡃࠨࢁࠬຩ"))[1])
    logger.info(bstack11l1l_opy_ (u"ࠩࡊࡩࡳ࡫ࡲࡢࡶࡨࡨࠥࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࠤࡧࡻࡩ࡭ࡦࠣࡥࡷࡺࡩࡧࡣࡦࡸࡸࠦࡡࡵࠢࡾࢁࠬສ").format(bstack11l1llll_opy_));
  except Exception as e:
    logger.debug(bstack1l11l1ll1_opy_.format(str(e)))
def bstack1ll1l111l_opy_(hashed_id):
  global CONFIG
  try:
    bstack11ll1l1ll1_opy_ = datetime.datetime.now()
    host = bstack11l1l_opy_ (u"ࠪ࡬ࡹࡺࡰࡴ࠼࠲࠳ࡦࡶࡩ࠮ࡥ࡯ࡳࡺࡪ࠮ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡣࡰ࡯ࠪຫ") if bstack11l1l_opy_ (u"ࠫࡦࡶࡰࠨຬ") in CONFIG else bstack11l1l_opy_ (u"ࠬ࡮ࡴࡵࡲࡶ࠾࠴࠵ࡡࡱ࡫࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡦࡳࡲ࠭ອ")
    user = CONFIG[bstack11l1l_opy_ (u"࠭ࡵࡴࡧࡵࡒࡦࡳࡥࠨຮ")]
    key = CONFIG[bstack11l1l_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡋࡦࡻࠪຯ")]
    bstack11lll1llll_opy_ = bstack11l1l_opy_ (u"ࠨࡣࡳࡴ࠲ࡧࡵࡵࡱࡰࡥࡹ࡫ࠧະ") if bstack11l1l_opy_ (u"ࠩࡤࡴࡵ࠭ັ") in CONFIG else (bstack11l1l_opy_ (u"ࠪࡸࡺࡸࡢࡰࡵࡦࡥࡱ࡫ࠧາ") if CONFIG.get(bstack11l1l_opy_ (u"ࠫࡹࡻࡲࡣࡱࡶࡧࡦࡲࡥࠨຳ")) else bstack11l1l_opy_ (u"ࠬࡧࡵࡵࡱࡰࡥࡹ࡫ࠧິ"))
    host = bstack1l1l1ll1l_opy_(cli.config, [bstack11l1l_opy_ (u"ࠨࡡࡱ࡫ࡶࠦີ"), bstack11l1l_opy_ (u"ࠢࡢࡲࡳࡅࡺࡺ࡯࡮ࡣࡷࡩࠧຶ"), bstack11l1l_opy_ (u"ࠣࡣࡳ࡭ࠧື")], host) if bstack11l1l_opy_ (u"ࠩࡤࡴࡵຸ࠭") in CONFIG else bstack1l1l1ll1l_opy_(cli.config, [bstack11l1l_opy_ (u"ࠥࡥࡵ࡯ࡳູࠣ"), bstack11l1l_opy_ (u"ࠦࡦࡻࡴࡰ࡯ࡤࡸࡪࠨ຺"), bstack11l1l_opy_ (u"ࠧࡧࡰࡪࠤົ")], host)
    url = bstack11l1l_opy_ (u"࠭ࡻࡾ࠱ࡾࢁ࠴ࡨࡵࡪ࡮ࡧࡷ࠴ࢁࡽ࠰ࡵࡨࡷࡸ࡯࡯࡯ࡵ࠱࡮ࡸࡵ࡮ࠨຼ").format(host, bstack11lll1llll_opy_, hashed_id)
    headers = {
      bstack11l1l_opy_ (u"ࠧࡄࡱࡱࡸࡪࡴࡴ࠮ࡶࡼࡴࡪ࠭ຽ"): bstack11l1l_opy_ (u"ࠨࡣࡳࡴࡱ࡯ࡣࡢࡶ࡬ࡳࡳ࠵ࡪࡴࡱࡱࠫ຾"),
    }
    proxies = bstack1lllll111l_opy_(CONFIG, url)
    response = requests.get(url, headers=headers, proxies=proxies, auth=(user, key))
    if response.json():
      cli.bstack11lll111_opy_(bstack11l1l_opy_ (u"ࠤ࡫ࡸࡹࡶ࠺ࡨࡧࡷࡣࡸ࡫ࡳࡴ࡫ࡲࡲࡸࡥ࡬ࡪࡵࡷࠦ຿"), datetime.datetime.now() - bstack11ll1l1ll1_opy_)
      return list(map(lambda session: session[bstack11l1l_opy_ (u"ࠪࡥࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴ࡟ࡴࡧࡶࡷ࡮ࡵ࡮ࠨເ")], response.json()))
  except Exception as e:
    logger.debug(bstack1lll11111l_opy_.format(str(e)))
@measure(event_name=EVENTS.bstack11lll1l11_opy_, stage=STAGE.bstack1lll1l11l_opy_, bstack1l1l1llll_opy_=bstack11l1ll1l_opy_)
def get_build_link():
  global CONFIG
  global bstack1ll1111l_opy_
  try:
    if bstack11l1l_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡑࡥࡲ࡫ࠧແ") in CONFIG:
      bstack11ll1l1ll1_opy_ = datetime.datetime.now()
      host = bstack11l1l_opy_ (u"ࠬࡧࡰࡪ࠯ࡦࡰࡴࡻࡤࠨໂ") if bstack11l1l_opy_ (u"࠭ࡡࡱࡲࠪໃ") in CONFIG else bstack11l1l_opy_ (u"ࠧࡢࡲ࡬ࠫໄ")
      user = CONFIG[bstack11l1l_opy_ (u"ࠨࡷࡶࡩࡷࡔࡡ࡮ࡧࠪ໅")]
      key = CONFIG[bstack11l1l_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴࡍࡨࡽࠬໆ")]
      bstack11lll1llll_opy_ = bstack11l1l_opy_ (u"ࠪࡥࡵࡶ࠭ࡢࡷࡷࡳࡲࡧࡴࡦࠩ໇") if bstack11l1l_opy_ (u"ࠫࡦࡶࡰࠨ່") in CONFIG else bstack11l1l_opy_ (u"ࠬࡧࡵࡵࡱࡰࡥࡹ࡫້ࠧ")
      url = bstack11l1l_opy_ (u"࠭ࡨࡵࡶࡳࡷ࠿࠵࠯ࡼࡿ࠽ࡿࢂࡆࡻࡾ࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡥࡲࡱ࠴ࢁࡽ࠰ࡤࡸ࡭ࡱࡪࡳ࠯࡬ࡶࡳࡳ໊࠭").format(user, key, host, bstack11lll1llll_opy_)
      if cli.is_enabled(CONFIG):
        bstack11l11llll_opy_, hashed_id = cli.bstack1l1l1ll1ll_opy_()
        logger.info(bstack11l11l11l1_opy_.format(bstack11l11llll_opy_))
        return [hashed_id, bstack11l11llll_opy_]
      else:
        headers = {
          bstack11l1l_opy_ (u"ࠧࡄࡱࡱࡸࡪࡴࡴ࠮ࡶࡼࡴࡪ໋࠭"): bstack11l1l_opy_ (u"ࠨࡣࡳࡴࡱ࡯ࡣࡢࡶ࡬ࡳࡳ࠵ࡪࡴࡱࡱࠫ໌"),
        }
        if bstack11l1l_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫໍ") in CONFIG:
          params = {bstack11l1l_opy_ (u"ࠪࡲࡦࡳࡥࠨ໎"): CONFIG[bstack11l1l_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡑࡥࡲ࡫ࠧ໏")], bstack11l1l_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡣ࡮ࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨ໐"): CONFIG[bstack11l1l_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨ໑")]}
        else:
          params = {bstack11l1l_opy_ (u"ࠧ࡯ࡣࡰࡩࠬ໒"): CONFIG[bstack11l1l_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠫ໓")]}
        proxies = bstack1lllll111l_opy_(CONFIG, url)
        response = requests.get(url, params=params, headers=headers, proxies=proxies)
        if response.json():
          bstack1ll1llllll_opy_ = response.json()[0][bstack11l1l_opy_ (u"ࠩࡤࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳࡥࡢࡶ࡫࡯ࡨࠬ໔")]
          if bstack1ll1llllll_opy_:
            bstack11l11llll_opy_ = bstack1ll1llllll_opy_[bstack11l1l_opy_ (u"ࠪࡴࡺࡨ࡬ࡪࡥࡢࡹࡷࡲࠧ໕")].split(bstack11l1l_opy_ (u"ࠫࡵࡻࡢ࡭࡫ࡦ࠱ࡧࡻࡩ࡭ࡦࠪ໖"))[0] + bstack11l1l_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡷ࠴࠭໗") + bstack1ll1llllll_opy_[
              bstack11l1l_opy_ (u"࠭ࡨࡢࡵ࡫ࡩࡩࡥࡩࡥࠩ໘")]
            logger.info(bstack11l11l11l1_opy_.format(bstack11l11llll_opy_))
            bstack1ll1111l_opy_ = bstack1ll1llllll_opy_[bstack11l1l_opy_ (u"ࠧࡩࡣࡶ࡬ࡪࡪ࡟ࡪࡦࠪ໙")]
            bstack1111l111l_opy_ = CONFIG[bstack11l1l_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠫ໚")]
            if bstack11l1l_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫ໛") in CONFIG:
              bstack1111l111l_opy_ += bstack11l1l_opy_ (u"ࠪࠤࠬໜ") + CONFIG[bstack11l1l_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭ໝ")]
            if bstack1111l111l_opy_ != bstack1ll1llllll_opy_[bstack11l1l_opy_ (u"ࠬࡴࡡ࡮ࡧࠪໞ")]:
              logger.debug(bstack11l11l1l11_opy_.format(bstack1ll1llllll_opy_[bstack11l1l_opy_ (u"࠭࡮ࡢ࡯ࡨࠫໟ")], bstack1111l111l_opy_))
            cli.bstack11lll111_opy_(bstack11l1l_opy_ (u"ࠢࡩࡶࡷࡴ࠿࡭ࡥࡵࡡࡥࡹ࡮ࡲࡤࡠ࡮࡬ࡲࡰࠨ໠"), datetime.datetime.now() - bstack11ll1l1ll1_opy_)
            return [bstack1ll1llllll_opy_[bstack11l1l_opy_ (u"ࠨࡪࡤࡷ࡭࡫ࡤࡠ࡫ࡧࠫ໡")], bstack11l11llll_opy_]
    else:
      logger.warning(bstack111l1111_opy_)
  except Exception as e:
    logger.debug(bstack1llll11ll1_opy_.format(str(e)))
  return [None, None]
def bstack11ll1lll_opy_(url, bstack11lll1l11l_opy_=False):
  global CONFIG
  global bstack1ll1l1l1l1_opy_
  if not bstack1ll1l1l1l1_opy_:
    hostname = bstack1111lll11_opy_(url)
    is_private = bstack11l11l1ll_opy_(hostname)
    if (bstack11l1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡍࡱࡦࡥࡱ࠭໢") in CONFIG and not bstack1llll1ll1_opy_(CONFIG[bstack11l1l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡎࡲࡧࡦࡲࠧ໣")])) and (is_private or bstack11lll1l11l_opy_):
      bstack1ll1l1l1l1_opy_ = hostname
def bstack1111lll11_opy_(url):
  return urlparse(url).hostname
def bstack11l11l1ll_opy_(hostname):
  for bstack1l1l11l111_opy_ in bstack11lll111ll_opy_:
    regex = re.compile(bstack1l1l11l111_opy_)
    if regex.match(hostname):
      return True
  return False
def bstack111llll111_opy_(bstack1ll11ll1_opy_):
  return True if bstack1ll11ll1_opy_ in threading.current_thread().__dict__.keys() else False
@measure(event_name=EVENTS.bstack1ll1l1l111_opy_, stage=STAGE.bstack1lll1l11l_opy_, bstack1l1l1llll_opy_=bstack11l1ll1l_opy_)
def getAccessibilityResults(driver):
  global CONFIG
  global bstack11ll1111ll_opy_
  bstack11ll1lllll_opy_ = not (bstack11lll11l_opy_(threading.current_thread(), bstack11l1l_opy_ (u"ࠫ࡮ࡹࡁ࠲࠳ࡼࡘࡪࡹࡴࠨ໤"), None) and bstack11lll11l_opy_(
          threading.current_thread(), bstack11l1l_opy_ (u"ࠬࡧ࠱࠲ࡻࡓࡰࡦࡺࡦࡰࡴࡰࠫ໥"), None))
  bstack11l1111ll_opy_ = getattr(driver, bstack11l1l_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡇ࠱࠲ࡻࡖ࡬ࡴࡻ࡬ࡥࡕࡦࡥࡳ࠭໦"), None) != True
  bstack111ll111_opy_ = bstack11lll11l_opy_(threading.current_thread(), bstack11l1l_opy_ (u"ࠧࡪࡵࡄࡴࡵࡇ࠱࠲ࡻࡗࡩࡸࡺࠧ໧"), None) and bstack11lll11l_opy_(
          threading.current_thread(), bstack11l1l_opy_ (u"ࠨࡣࡳࡴࡆ࠷࠱ࡺࡒ࡯ࡥࡹ࡬࡯ࡳ࡯ࠪ໨"), None)
  if bstack111ll111_opy_:
    if not bstack111lll1111_opy_():
      logger.warning(bstack11l1l_opy_ (u"ࠤࡑࡳࡹࠦࡡ࡯ࠢࡄࡴࡵࠦࡁࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࠦࡁࡶࡶࡲࡱࡦࡺࡩࡰࡰࠣࡷࡪࡹࡳࡪࡱࡱ࠰ࠥࡩࡡ࡯ࡰࡲࡸࠥࡸࡥࡵࡴ࡬ࡩࡻ࡫ࠠࡂࡲࡳࠤࡆࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠤࡷ࡫ࡳࡶ࡮ࡷࡷ࠳ࠨ໩"))
      return {}
    logger.debug(bstack11l1l_opy_ (u"ࠪࡔࡪࡸࡦࡰࡴࡰ࡭ࡳ࡭ࠠࡴࡥࡤࡲࠥࡨࡥࡧࡱࡵࡩࠥ࡭ࡥࡵࡶ࡬ࡲ࡬ࠦࡲࡦࡵࡸࡰࡹࡹࠧ໪"))
    logger.debug(perform_scan(driver, driver_command=bstack11l1l_opy_ (u"ࠫࡪࡾࡥࡤࡷࡷࡩࡘࡩࡲࡪࡲࡷࠫ໫")))
    results = bstack11111l1l_opy_(bstack11l1l_opy_ (u"ࠧࡸࡥࡴࡷ࡯ࡸࡸࠨ໬"))
    if results is not None and results.get(bstack11l1l_opy_ (u"ࠨࡩࡴࡵࡸࡩࡸࠨ໭")) is not None:
        return results[bstack11l1l_opy_ (u"ࠢࡪࡵࡶࡹࡪࡹࠢ໮")]
    logger.error(bstack11l1l_opy_ (u"ࠣࡐࡲࠤࡆࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠤࡗ࡫ࡳࡶ࡮ࡷࡷࠥࡽࡥࡳࡧࠣࡪࡴࡻ࡮ࡥ࠰ࠥ໯"))
    return []
  if not bstack11llll11l1_opy_.bstack11l11ll1_opy_(CONFIG, bstack11ll1111ll_opy_) or (bstack11l1111ll_opy_ and bstack11ll1lllll_opy_):
    logger.warning(bstack11l1l_opy_ (u"ࠤࡑࡳࡹࠦࡡ࡯ࠢࡄࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠢࡄࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳࠦࡳࡦࡵࡶ࡭ࡴࡴࠬࠡࡥࡤࡲࡳࡵࡴࠡࡴࡨࡸࡷ࡯ࡥࡷࡧࠣࡅࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠣࡶࡪࡹࡵ࡭ࡶࡶ࠲ࠧ໰"))
    return {}
  try:
    logger.debug(bstack11l1l_opy_ (u"ࠪࡔࡪࡸࡦࡰࡴࡰ࡭ࡳ࡭ࠠࡴࡥࡤࡲࠥࡨࡥࡧࡱࡵࡩࠥ࡭ࡥࡵࡶ࡬ࡲ࡬ࠦࡲࡦࡵࡸࡰࡹࡹࠧ໱"))
    logger.debug(perform_scan(driver))
    results = driver.execute_async_script(bstack111lll1l_opy_.bstack111ll1llll_opy_)
    return results
  except Exception:
    logger.error(bstack11l1l_opy_ (u"ࠦࡓࡵࠠࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡳࡧࡶࡹࡱࡺࡳࠡࡹࡨࡶࡪࠦࡦࡰࡷࡱࡨ࠳ࠨ໲"))
    return {}
@measure(event_name=EVENTS.bstack1l1llll11_opy_, stage=STAGE.bstack1lll1l11l_opy_, bstack1l1l1llll_opy_=bstack11l1ll1l_opy_)
def getAccessibilityResultsSummary(driver):
  global CONFIG
  global bstack11ll1111ll_opy_
  bstack11ll1lllll_opy_ = not (bstack11lll11l_opy_(threading.current_thread(), bstack11l1l_opy_ (u"ࠬ࡯ࡳࡂ࠳࠴ࡽ࡙࡫ࡳࡵࠩ໳"), None) and bstack11lll11l_opy_(
          threading.current_thread(), bstack11l1l_opy_ (u"࠭ࡡ࠲࠳ࡼࡔࡱࡧࡴࡧࡱࡵࡱࠬ໴"), None))
  bstack11l1111ll_opy_ = getattr(driver, bstack11l1l_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱࡁ࠲࠳ࡼࡗ࡭ࡵࡵ࡭ࡦࡖࡧࡦࡴࠧ໵"), None) != True
  bstack111ll111_opy_ = bstack11lll11l_opy_(threading.current_thread(), bstack11l1l_opy_ (u"ࠨ࡫ࡶࡅࡵࡶࡁ࠲࠳ࡼࡘࡪࡹࡴࠨ໶"), None) and bstack11lll11l_opy_(
          threading.current_thread(), bstack11l1l_opy_ (u"ࠩࡤࡴࡵࡇ࠱࠲ࡻࡓࡰࡦࡺࡦࡰࡴࡰࠫ໷"), None)
  if bstack111ll111_opy_:
    if not bstack111lll1111_opy_():
      logger.warning(bstack11l1l_opy_ (u"ࠥࡒࡴࡺࠠࡢࡰࠣࡅࡵࡶࠠࡂࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡂࡷࡷࡳࡲࡧࡴࡪࡱࡱࠤࡸ࡫ࡳࡴ࡫ࡲࡲ࠱ࠦࡣࡢࡰࡱࡳࡹࠦࡲࡦࡶࡵ࡭ࡪࡼࡥࠡࡃࡳࡴࠥࡇࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡸࡥࡴࡷ࡯ࡸࡸࠦࡳࡶ࡯ࡰࡥࡷࡿ࠮ࠣ໸"))
      return {}
    logger.debug(bstack11l1l_opy_ (u"ࠫࡕ࡫ࡲࡧࡱࡵࡱ࡮ࡴࡧࠡࡵࡦࡥࡳࠦࡢࡦࡨࡲࡶࡪࠦࡧࡦࡶࡷ࡭ࡳ࡭ࠠࡳࡧࡶࡹࡱࡺࡳࠡࡵࡸࡱࡲࡧࡲࡺࠩ໹"))
    logger.debug(perform_scan(driver, driver_command=bstack11l1l_opy_ (u"ࠬ࡫ࡸࡦࡥࡸࡸࡪ࡙ࡣࡳ࡫ࡳࡸࠬ໺")))
    results = bstack11111l1l_opy_(bstack11l1l_opy_ (u"ࠨࡲࡦࡵࡸࡰࡹ࡙ࡵ࡮࡯ࡤࡶࡾࠨ໻"))
    if results is not None and results.get(bstack11l1l_opy_ (u"ࠢࡴࡷࡰࡱࡦࡸࡹࠣ໼")) is not None:
        return results[bstack11l1l_opy_ (u"ࠣࡵࡸࡱࡲࡧࡲࡺࠤ໽")]
    logger.error(bstack11l1l_opy_ (u"ࠤࡑࡳࠥࡇࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡘࡥࡴࡷ࡯ࡸࡸࠦࡓࡶ࡯ࡰࡥࡷࡿࠠࡸࡣࡶࠤ࡫ࡵࡵ࡯ࡦ࠱ࠦ໾"))
    return {}
  if not bstack11llll11l1_opy_.bstack11l11ll1_opy_(CONFIG, bstack11ll1111ll_opy_) or (bstack11l1111ll_opy_ and bstack11ll1lllll_opy_):
    logger.warning(bstack11l1l_opy_ (u"ࠥࡒࡴࡺࠠࡢࡰࠣࡅࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠣࡅࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࠠࡴࡧࡶࡷ࡮ࡵ࡮࠭ࠢࡦࡥࡳࡴ࡯ࡵࠢࡵࡩࡹࡸࡩࡦࡸࡨࠤࡆࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠤࡷ࡫ࡳࡶ࡮ࡷࡷࠥࡹࡵ࡮࡯ࡤࡶࡾ࠴ࠢ໿"))
    return {}
  try:
    logger.debug(bstack11l1l_opy_ (u"ࠫࡕ࡫ࡲࡧࡱࡵࡱ࡮ࡴࡧࠡࡵࡦࡥࡳࠦࡢࡦࡨࡲࡶࡪࠦࡧࡦࡶࡷ࡭ࡳ࡭ࠠࡳࡧࡶࡹࡱࡺࡳࠡࡵࡸࡱࡲࡧࡲࡺࠩༀ"))
    logger.debug(perform_scan(driver))
    bstack1lll1l11l1_opy_ = driver.execute_async_script(bstack111lll1l_opy_.bstack1l1l11l1_opy_)
    return bstack1lll1l11l1_opy_
  except Exception:
    logger.error(bstack11l1l_opy_ (u"ࠧࡔ࡯ࠡࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠡࡵࡸࡱࡲࡧࡲࡺࠢࡺࡥࡸࠦࡦࡰࡷࡱࡨ࠳ࠨ༁"))
    return {}
def bstack111lll1111_opy_():
  global CONFIG
  global bstack11ll1111ll_opy_
  bstack111l1lll1_opy_ = bstack11lll11l_opy_(threading.current_thread(), bstack11l1l_opy_ (u"࠭ࡩࡴࡃࡳࡴࡆ࠷࠱ࡺࡖࡨࡷࡹ࠭༂"), None) and bstack11lll11l_opy_(threading.current_thread(), bstack11l1l_opy_ (u"ࠧࡢࡲࡳࡅ࠶࠷ࡹࡑ࡮ࡤࡸ࡫ࡵࡲ࡮ࠩ༃"), None)
  if not bstack11llll11l1_opy_.bstack11l11ll1_opy_(CONFIG, bstack11ll1111ll_opy_) or not bstack111l1lll1_opy_:
        logger.warning(bstack11l1l_opy_ (u"ࠣࡐࡲࡸࠥࡧ࡮ࠡࡃࡳࡴࠥࡇࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡇࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࠢࡶࡩࡸࡹࡩࡰࡰ࠯ࠤࡨࡧ࡮࡯ࡱࡷࠤࡷ࡫ࡴࡳ࡫ࡨࡺࡪࠦࡲࡦࡵࡸࡰࡹࡹ࠮ࠣ༄"))
        return False
  return True
def bstack11111l1l_opy_(result_type):
    bstack1lll111lll_opy_ = bstack1ll1llll11_opy_.current_test_uuid() if bstack1ll1llll11_opy_.current_test_uuid() else bstack11llll111_opy_.current_hook_uuid()
    with ThreadPoolExecutor() as executor:
        future = executor.submit(bstack11lllll1_opy_(bstack1lll111lll_opy_, result_type))
        try:
            return future.result(timeout=bstack1ll11lll11_opy_)
        except TimeoutError:
            logger.error(bstack11l1l_opy_ (u"ࠤࡗ࡭ࡲ࡫࡯ࡶࡶࠣࡥ࡫ࡺࡥࡳࠢࡾࢁࡸࠦࡷࡩ࡫࡯ࡩࠥ࡬ࡥࡵࡥ࡫࡭ࡳ࡭ࠠࡂࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡓࡧࡶࡹࡱࡺࡳࠣ༅").format(bstack1ll11lll11_opy_))
        except Exception as ex:
            logger.debug(bstack11l1l_opy_ (u"ࠥࡉࡷࡸ࡯ࡳࠢࡵࡩࡹࡸࡩࡦࡸ࡬ࡲ࡬ࠦࡁࡱࡲࠣࡅࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠣࡅࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࠠࡼࡿ࠱ࠤࡊࡸࡲࡰࡴࠣ࠱ࠥࢁࡽࠣ༆").format(result_type, str(ex)))
    return {}
@measure(event_name=EVENTS.bstack1l11l1l111_opy_, stage=STAGE.bstack1lll1l11l_opy_, bstack1l1l1llll_opy_=bstack11l1ll1l_opy_)
def perform_scan(driver, *args, **kwargs):
  global CONFIG
  global bstack11ll1111ll_opy_
  bstack11ll1lllll_opy_ = not (bstack11lll11l_opy_(threading.current_thread(), bstack11l1l_opy_ (u"ࠫ࡮ࡹࡁ࠲࠳ࡼࡘࡪࡹࡴࠨ༇"), None) and bstack11lll11l_opy_(
          threading.current_thread(), bstack11l1l_opy_ (u"ࠬࡧ࠱࠲ࡻࡓࡰࡦࡺࡦࡰࡴࡰࠫ༈"), None))
  bstack111llll1l_opy_ = not (bstack11lll11l_opy_(threading.current_thread(), bstack11l1l_opy_ (u"࠭ࡩࡴࡃࡳࡴࡆ࠷࠱ࡺࡖࡨࡷࡹ࠭༉"), None) and bstack11lll11l_opy_(
          threading.current_thread(), bstack11l1l_opy_ (u"ࠧࡢࡲࡳࡅ࠶࠷ࡹࡑ࡮ࡤࡸ࡫ࡵࡲ࡮ࠩ༊"), None))
  bstack11l1111ll_opy_ = getattr(driver, bstack11l1l_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫ࡂ࠳࠴ࡽࡘ࡮࡯ࡶ࡮ࡧࡗࡨࡧ࡮ࠨ་"), None) != True
  if not bstack11llll11l1_opy_.bstack11l11ll1_opy_(CONFIG, bstack11ll1111ll_opy_) or (bstack11l1111ll_opy_ and bstack11ll1lllll_opy_ and bstack111llll1l_opy_):
    logger.warning(bstack11l1l_opy_ (u"ࠤࡑࡳࡹࠦࡡ࡯ࠢࡄࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠢࡄࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳࠦࡳࡦࡵࡶ࡭ࡴࡴࠬࠡࡥࡤࡲࡳࡵࡴࠡࡴࡸࡲࠥࡇࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡹࡣࡢࡰ࠱ࠦ༌"))
    return {}
  try:
    bstack1ll11lllll_opy_ = bstack11l1l_opy_ (u"ࠪࡥࡵࡶࠧ།") in CONFIG and CONFIG.get(bstack11l1l_opy_ (u"ࠫࡦࡶࡰࠨ༎"), bstack11l1l_opy_ (u"ࠬ࠭༏"))
    session_id = getattr(driver, bstack11l1l_opy_ (u"࠭ࡳࡦࡵࡶ࡭ࡴࡴ࡟ࡪࡦࠪ༐"), None)
    if not session_id:
      logger.warning(bstack11l1l_opy_ (u"ࠢࡏࡱࠣࡷࡪࡹࡳࡪࡱࡱࠤࡎࡊࠠࡧࡱࡸࡲࡩࠦࡦࡰࡴࠣࡨࡷ࡯ࡶࡦࡴࠥ༑"))
      return {bstack11l1l_opy_ (u"ࠣࡧࡵࡶࡴࡸࠢ༒"): bstack11l1l_opy_ (u"ࠤࡑࡳࠥࡹࡥࡴࡵ࡬ࡳࡳࠦࡉࡅࠢࡩࡳࡺࡴࡤࠣ༓")}
    if bstack1ll11lllll_opy_:
      try:
        bstack1l11ll111l_opy_ = {
              bstack11l1l_opy_ (u"ࠪࡸ࡭ࡐࡷࡵࡖࡲ࡯ࡪࡴࠧ༔"): os.environ.get(bstack11l1l_opy_ (u"ࠫࡇ࡙࡟ࡂ࠳࠴࡝ࡤࡐࡗࡕࠩ༕"), os.environ.get(bstack11l1l_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡊࡘࡆࡤࡐࡗࡕࠩ༖"), bstack11l1l_opy_ (u"࠭ࠧ༗"))),
              bstack11l1l_opy_ (u"ࠧࡵࡪࡗࡩࡸࡺࡒࡶࡰࡘࡹ࡮ࡪ༘ࠧ"): bstack1ll1llll11_opy_.current_test_uuid() if bstack1ll1llll11_opy_.current_test_uuid() else bstack11llll111_opy_.current_hook_uuid(),
              bstack11l1l_opy_ (u"ࠨࡣࡸࡸ࡭ࡎࡥࡢࡦࡨࡶ༙ࠬ"): os.environ.get(bstack11l1l_opy_ (u"ࠩࡅࡗࡤࡇ࠱࠲࡛ࡢࡎ࡜࡚ࠧ༚")),
              bstack11l1l_opy_ (u"ࠪࡷࡨࡧ࡮ࡕ࡫ࡰࡩࡸࡺࡡ࡮ࡲࠪ༛"): str(int(datetime.datetime.now().timestamp() * 1000)),
              bstack11l1l_opy_ (u"ࠫࡹ࡮ࡂࡶ࡫࡯ࡨ࡚ࡻࡩࡥࠩ༜"): os.environ.get(bstack11l1l_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡊࡘࡆࡤ࡛ࡕࡊࡆࠪ༝"), bstack11l1l_opy_ (u"࠭ࠧ༞")),
              bstack11l1l_opy_ (u"ࠧ࡮ࡧࡷ࡬ࡴࡪࠧ༟"): kwargs.get(bstack11l1l_opy_ (u"ࠨࡦࡵ࡭ࡻ࡫ࡲࡠࡥࡲࡱࡲࡧ࡮ࡥࠩ༠"), None) or bstack11l1l_opy_ (u"ࠩࠪ༡")
          }
        if not hasattr(thread_local, bstack11l1l_opy_ (u"ࠪࡦࡦࡹࡥࡠࡣࡳࡴࡤࡧ࠱࠲ࡻࡢࡷࡨࡸࡩࡱࡶࠪ༢")):
            scripts = {bstack11l1l_opy_ (u"ࠫࡸࡩࡡ࡯ࠩ༣"): bstack111lll1l_opy_.perform_scan}
            thread_local.base_app_a11y_script = scripts
        bstack11lll11l11_opy_ = copy.deepcopy(thread_local.base_app_a11y_script)
        bstack11lll11l11_opy_[bstack11l1l_opy_ (u"ࠬࡹࡣࡢࡰࠪ༤")] = bstack11lll11l11_opy_[bstack11l1l_opy_ (u"࠭ࡳࡤࡣࡱࠫ༥")] % json.dumps(bstack1l11ll111l_opy_)
        bstack111lll1l_opy_.bstack1111ll1ll_opy_(bstack11lll11l11_opy_)
        bstack111lll1l_opy_.store()
        bstack111l111l1_opy_ = driver.execute_script(bstack111lll1l_opy_.perform_scan)
      except Exception as bstack1l11ll1l11_opy_:
        logger.info(bstack11l1l_opy_ (u"ࠢࡂࡲࡳ࡭ࡺࡳࠠࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡴࡥࡤࡲࠥ࡬ࡡࡪ࡮ࡨࡨ࠿ࠦࠢ༦") + str(bstack1l11ll1l11_opy_))
        bstack111l111l1_opy_ = {bstack11l1l_opy_ (u"ࠣࡧࡵࡶࡴࡸࠢ༧"): str(bstack1l11ll1l11_opy_)}
    else:
      bstack111l111l1_opy_ = driver.execute_async_script(bstack111lll1l_opy_.perform_scan, {bstack11l1l_opy_ (u"ࠩࡰࡩࡹ࡮࡯ࡥࠩ༨"): kwargs.get(bstack11l1l_opy_ (u"ࠪࡨࡷ࡯ࡶࡦࡴࡢࡧࡴࡳ࡭ࡢࡰࡧࠫ༩"), None) or bstack11l1l_opy_ (u"ࠫࠬ༪")})
    return bstack111l111l1_opy_
  except Exception as err:
    logger.error(bstack11l1l_opy_ (u"࡛ࠧ࡮ࡢࡤ࡯ࡩࠥࡺ࡯ࠡࡴࡸࡲࠥࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡹࡣࡢࡰ࠱ࠤࢀࢃࠢ༫").format(str(err)))
    return {}