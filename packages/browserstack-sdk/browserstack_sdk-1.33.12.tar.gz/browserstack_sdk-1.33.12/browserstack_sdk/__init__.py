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
from browserstack_sdk.bstack1l1111ll11_opy_ import bstack1lll11ll1_opy_
from browserstack_sdk.bstack11ll11ll1_opy_ import *
import time
import requests
from bstack_utils.constants import EVENTS, STAGE, bstack1lll1l11l_opy_
from bstack_utils.messages import bstack1l11l111l_opy_, bstack1l1ll11111_opy_, bstack11111111l_opy_, bstack111lll11ll_opy_, bstack11lll1ll1l_opy_, bstack1l1l11ll_opy_
from bstack_utils.measure import measure
from bstack_utils.bstack111lll1l1_opy_ import get_logger
from bstack_utils.helper import bstack1lllll1111_opy_
from browserstack_sdk.bstack1ll1lll1_opy_ import bstack1lll1l1ll_opy_
logger = get_logger(__name__)
def bstack11l1l1lll_opy_():
  global CONFIG
  headers = {
        bstack11ll1_opy_ (u"ࠪࡇࡴࡴࡴࡦࡰࡷ࠱ࡹࡿࡰࡦࠩࡶ"): bstack11ll1_opy_ (u"ࠫࡦࡶࡰ࡭࡫ࡦࡥࡹ࡯࡯࡯࠱࡭ࡷࡴࡴࠧࡷ"),
      }
  proxies = bstack1lllll1111_opy_(CONFIG, bstack1lll1l11l_opy_)
  try:
    response = requests.get(bstack1lll1l11l_opy_, headers=headers, proxies=proxies, timeout=5)
    if response.json():
      bstack11111l111_opy_ = response.json()[bstack11ll1_opy_ (u"ࠬ࡮ࡵࡣࡵࠪࡸ")]
      logger.debug(bstack1l11l111l_opy_.format(response.json()))
      return bstack11111l111_opy_
    else:
      logger.debug(bstack1l1ll11111_opy_.format(bstack11ll1_opy_ (u"ࠨࡒࡦࡵࡳࡳࡳࡹࡥࠡࡌࡖࡓࡓࠦࡰࡢࡴࡶࡩࠥ࡫ࡲࡳࡱࡵࠤࠧࡹ")))
  except Exception as e:
    logger.debug(bstack1l1ll11111_opy_.format(e))
def bstack1l1llllll_opy_(hub_url):
  global CONFIG
  url = bstack11ll1_opy_ (u"ࠢࡩࡶࡷࡴࡸࡀ࠯࠰ࠤࡺ")+  hub_url + bstack11ll1_opy_ (u"ࠣ࠱ࡦ࡬ࡪࡩ࡫ࠣࡻ")
  headers = {
        bstack11ll1_opy_ (u"ࠩࡆࡳࡳࡺࡥ࡯ࡶ࠰ࡸࡾࡶࡥࠨࡼ"): bstack11ll1_opy_ (u"ࠪࡥࡵࡶ࡬ࡪࡥࡤࡸ࡮ࡵ࡮࠰࡬ࡶࡳࡳ࠭ࡽ"),
      }
  proxies = bstack1lllll1111_opy_(CONFIG, url)
  try:
    start_time = time.perf_counter()
    requests.get(url, headers=headers, proxies=proxies, timeout=5)
    latency = time.perf_counter() - start_time
    logger.debug(bstack11111111l_opy_.format(hub_url, latency))
    return dict(hub_url=hub_url, latency=latency)
  except Exception as e:
    logger.debug(bstack111lll11ll_opy_.format(hub_url, e))
@measure(event_name=EVENTS.bstack1ll11111_opy_, stage=STAGE.bstack11l1llll1_opy_)
def bstack11l111l111_opy_():
  try:
    global bstack1l1ll11ll1_opy_
    global CONFIG
    if bstack11ll1_opy_ (u"ࠫ࡭ࡻࡢࡓࡧࡪ࡭ࡴࡴࠧࡾ") in CONFIG and CONFIG[bstack11ll1_opy_ (u"ࠬ࡮ࡵࡣࡔࡨ࡫࡮ࡵ࡮ࠨࡿ")]:
      from bstack_utils.constants import bstack11111l1ll_opy_
      bstack1llll111l_opy_ = CONFIG[bstack11ll1_opy_ (u"࠭ࡨࡶࡤࡕࡩ࡬࡯࡯࡯ࠩࢀ")]
      if bstack1llll111l_opy_ in bstack11111l1ll_opy_:
        bstack1l1ll11ll1_opy_ = bstack11111l1ll_opy_[bstack1llll111l_opy_]
        logger.debug(bstack11lll1ll1l_opy_.format(bstack1l1ll11ll1_opy_))
        return
      else:
        logger.debug(bstack11ll1_opy_ (u"ࠢࡉࡷࡥࠤࡰ࡫ࡹࠡࠩࡾࢁࠬࠦ࡮ࡰࡶࠣࡪࡴࡻ࡮ࡥࠢ࡬ࡲࠥࡎࡕࡃࡡࡘࡖࡑࡥࡍࡂࡒ࠯ࠤ࡫ࡧ࡬࡭࡫ࡱ࡫ࠥࡨࡡࡤ࡭ࠣࡸࡴࠦ࡯ࡱࡶ࡬ࡱࡦࡲࠠࡩࡷࡥࠤࡩ࡫ࡴࡦࡥࡷ࡭ࡴࡴࠢࢁ").format(bstack1llll111l_opy_))
    bstack11111l111_opy_ = bstack11l1l1lll_opy_()
    bstack1lllll1ll_opy_ = []
    results = []
    for bstack1111llll1_opy_ in bstack11111l111_opy_:
      bstack1lllll1ll_opy_.append(bstack1lll1l1ll_opy_(target=bstack1l1llllll_opy_,args=(bstack1111llll1_opy_,)))
    for t in bstack1lllll1ll_opy_:
      t.start()
    for t in bstack1lllll1ll_opy_:
      results.append(t.join())
    bstack1lll1lll11_opy_ = {}
    for item in results:
      hub_url = item[bstack11ll1_opy_ (u"ࠨࡪࡸࡦࡤࡻࡲ࡭ࠩࢂ")]
      latency = item[bstack11ll1_opy_ (u"ࠩ࡯ࡥࡹ࡫࡮ࡤࡻࠪࢃ")]
      bstack1lll1lll11_opy_[hub_url] = latency
    bstack1l1l11111l_opy_ = min(bstack1lll1lll11_opy_, key= lambda x: bstack1lll1lll11_opy_[x])
    bstack1l1ll11ll1_opy_ = bstack1l1l11111l_opy_
    logger.debug(bstack11lll1ll1l_opy_.format(bstack1l1l11111l_opy_))
  except Exception as e:
    logger.debug(bstack1l1l11ll_opy_.format(e))
from browserstack_sdk.bstack1l1l1ll1_opy_ import *
from browserstack_sdk.bstack1ll1lll1_opy_ import *
from browserstack_sdk.bstack111ll1111_opy_ import *
import logging
import requests
from bstack_utils.constants import *
from bstack_utils.bstack111lll1l1_opy_ import get_logger
from bstack_utils.measure import measure
logger = get_logger(__name__)
@measure(event_name=EVENTS.bstack1111ll11_opy_, stage=STAGE.bstack11l1llll1_opy_)
def bstack1111lll1l_opy_():
    global bstack1l1ll11ll1_opy_
    try:
        bstack11lll111l1_opy_ = bstack11lll111l_opy_()
        bstack111l1111l_opy_(bstack11lll111l1_opy_)
        hub_url = bstack11lll111l1_opy_.get(bstack11ll1_opy_ (u"ࠥࡹࡷࡲࠢࢄ"), bstack11ll1_opy_ (u"ࠦࠧࢅ"))
        if hub_url.endswith(bstack11ll1_opy_ (u"ࠬ࠵ࡷࡥ࠱࡫ࡹࡧ࠭ࢆ")):
            hub_url = hub_url.rsplit(bstack11ll1_opy_ (u"࠭࠯ࡸࡦ࠲࡬ࡺࡨࠧࢇ"), 1)[0]
        if hub_url.startswith(bstack11ll1_opy_ (u"ࠧࡩࡶࡷࡴ࠿࠵࠯ࠨ࢈")):
            hub_url = hub_url[7:]
        elif hub_url.startswith(bstack11ll1_opy_ (u"ࠨࡪࡷࡸࡵࡹ࠺࠰࠱ࠪࢉ")):
            hub_url = hub_url[8:]
        bstack1l1ll11ll1_opy_ = hub_url
    except Exception as e:
        raise RuntimeError(e)
def bstack11lll111l_opy_():
    global CONFIG
    bstack1111l1l11_opy_ = CONFIG.get(bstack11ll1_opy_ (u"ࠩࡷࡹࡷࡨ࡯ࡔࡥࡤࡰࡪࡕࡰࡵ࡫ࡲࡲࡸ࠭ࢊ"), {}).get(bstack11ll1_opy_ (u"ࠪ࡫ࡷ࡯ࡤࡏࡣࡰࡩࠬࢋ"), bstack11ll1_opy_ (u"ࠫࡓࡕ࡟ࡈࡔࡌࡈࡤࡔࡁࡎࡇࡢࡔࡆ࡙ࡓࡆࡆࠪࢌ"))
    if not isinstance(bstack1111l1l11_opy_, str):
        raise ValueError(bstack11ll1_opy_ (u"ࠧࡇࡔࡔࠢ࠽ࠤࡌࡸࡩࡥࠢࡱࡥࡲ࡫ࠠ࡮ࡷࡶࡸࠥࡨࡥࠡࡣࠣࡺࡦࡲࡩࡥࠢࡶࡸࡷ࡯࡮ࡨࠤࢍ"))
    try:
        bstack11lll111l1_opy_ = bstack1ll11lll1_opy_(bstack1111l1l11_opy_)
        return bstack11lll111l1_opy_
    except Exception as e:
        logger.error(bstack11ll1_opy_ (u"ࠨࡁࡕࡕࠣ࠾ࠥࡋࡲࡳࡱࡵࠤ࡮ࡴࠠࡨࡧࡷࡸ࡮ࡴࡧࠡࡩࡵ࡭ࡩࠦࡤࡦࡶࡤ࡭ࡱࡹࠠ࠻ࠢࡾࢁࠧࢎ").format(str(e)))
        return {}
def bstack1ll11lll1_opy_(bstack1111l1l11_opy_):
    global CONFIG
    try:
        if not CONFIG[bstack11ll1_opy_ (u"ࠧࡶࡵࡨࡶࡓࡧ࡭ࡦࠩ࢏")] or not CONFIG[bstack11ll1_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡌࡧࡼࠫ࢐")]:
            raise ValueError(bstack11ll1_opy_ (u"ࠤࡐ࡭ࡸࡹࡩ࡯ࡩࠣࡆࡷࡵࡷࡴࡧࡵࡗࡹࡧࡣ࡬ࠢࡸࡷࡪࡸ࡮ࡢ࡯ࡨࠤࡴࡸࠠࡢࡥࡦࡩࡸࡹࠠ࡬ࡧࡼࠦ࢑"))
        url = bstack1l1l11l1l_opy_ + bstack1111l1l11_opy_
        auth = (CONFIG[bstack11ll1_opy_ (u"ࠪࡹࡸ࡫ࡲࡏࡣࡰࡩࠬ࢒")], CONFIG[bstack11ll1_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶࡏࡪࡿࠧ࢓")])
        response = requests.get(url, auth=auth)
        if response.status_code == 200 and response.text:
            bstack1l1l11l1ll_opy_ = json.loads(response.text)
            return bstack1l1l11l1ll_opy_
    except ValueError as ve:
        logger.error(bstack11ll1_opy_ (u"ࠧࡇࡔࡔࠢ࠽ࠤࡊࡸࡲࡰࡴࠣ࡭ࡳࠦࡦࡦࡶࡦ࡬࡮ࡴࡧࠡࡩࡵ࡭ࡩࠦࡤࡦࡶࡤ࡭ࡱࡹࠠ࠻ࠢࡾࢁࠧ࢔").format(str(ve)))
        raise ValueError(ve)
    except Exception as e:
        logger.error(bstack11ll1_opy_ (u"ࠨࡁࡕࡕࠣ࠾ࠥࡋࡲࡳࡱࡵࠤ࡮ࡴࠠࡧࡧࡷࡧ࡭࡯࡮ࡨࠢࡪࡶ࡮ࡪࠠࡥࡧࡷࡥ࡮ࡲࡳࠡ࠼ࠣࡿࢂࠨ࢕").format(str(e)))
        raise RuntimeError(e)
    return {}
def bstack111l1111l_opy_(bstack1ll11ll1l1_opy_):
    global CONFIG
    if bstack11ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࠫ࢖") not in CONFIG or str(CONFIG[bstack11ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡌࡰࡥࡤࡰࠬࢗ")]).lower() == bstack11ll1_opy_ (u"ࠩࡩࡥࡱࡹࡥࠨ࢘"):
        CONFIG[bstack11ll1_opy_ (u"ࠪࡰࡴࡩࡡ࡭࢙ࠩ")] = False
    elif bstack11ll1_opy_ (u"ࠫ࡮ࡹࡔࡳ࡫ࡤࡰࡌࡸࡩࡥ࢚ࠩ") in bstack1ll11ll1l1_opy_:
        bstack111llll1l_opy_ = CONFIG.get(bstack11ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࡑࡳࡸ࡮ࡵ࡮ࡴ࢛ࠩ"), {})
        logger.debug(bstack11ll1_opy_ (u"ࠨࡁࡕࡕࠣ࠾ࠥࡋࡸࡪࡵࡷ࡭ࡳ࡭ࠠ࡭ࡱࡦࡥࡱࠦ࡯ࡱࡶ࡬ࡳࡳࡹ࠺ࠡࠧࡶࠦ࢜"), bstack111llll1l_opy_)
        bstack11l11ll111_opy_ = bstack1ll11ll1l1_opy_.get(bstack11ll1_opy_ (u"ࠢࡤࡷࡶࡸࡴࡳࡒࡦࡲࡨࡥࡹ࡫ࡲࡴࠤ࢝"), [])
        bstack11l1ll1l1l_opy_ = bstack11ll1_opy_ (u"ࠣ࠮ࠥ࢞").join(bstack11l11ll111_opy_)
        logger.debug(bstack11ll1_opy_ (u"ࠤࡄࡘࡘࠦ࠺ࠡࡅࡸࡷࡹࡵ࡭ࠡࡴࡨࡴࡪࡧࡴࡦࡴࠣࡷࡹࡸࡩ࡯ࡩ࠽ࠤࠪࡹࠢ࢟"), bstack11l1ll1l1l_opy_)
        bstack111llllll_opy_ = {
            bstack11ll1_opy_ (u"ࠥࡰࡴࡩࡡ࡭ࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠧࢠ"): bstack11ll1_opy_ (u"ࠦࡦࡺࡳ࠮ࡴࡨࡴࡪࡧࡴࡦࡴࠥࢡ"),
            bstack11ll1_opy_ (u"ࠧ࡬࡯ࡳࡥࡨࡐࡴࡩࡡ࡭ࠤࢢ"): bstack11ll1_opy_ (u"ࠨࡴࡳࡷࡨࠦࢣ"),
            bstack11ll1_opy_ (u"ࠢࡤࡷࡶࡸࡴࡳ࠭ࡳࡧࡳࡩࡦࡺࡥࡳࠤࢤ"): bstack11l1ll1l1l_opy_
        }
        bstack111llll1l_opy_.update(bstack111llllll_opy_)
        logger.debug(bstack11ll1_opy_ (u"ࠣࡃࡗࡗࠥࡀࠠࡖࡲࡧࡥࡹ࡫ࡤࠡ࡮ࡲࡧࡦࡲࠠࡰࡲࡷ࡭ࡴࡴࡳ࠻ࠢࠨࡷࠧࢥ"), bstack111llll1l_opy_)
        CONFIG[bstack11ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࡍࡱࡦࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭ࢦ")] = bstack111llll1l_opy_
        logger.debug(bstack11ll1_opy_ (u"ࠥࡅ࡙࡙ࠠ࠻ࠢࡉ࡭ࡳࡧ࡬ࠡࡅࡒࡒࡋࡏࡇ࠻ࠢࠨࡷࠧࢧ"), CONFIG)
def bstack1l11lllll_opy_():
    bstack11lll111l1_opy_ = bstack11lll111l_opy_()
    if not bstack11lll111l1_opy_[bstack11ll1_opy_ (u"ࠫࡵࡲࡡࡺࡹࡵ࡭࡬࡮ࡴࡖࡴ࡯ࠫࢨ")]:
      raise ValueError(bstack11ll1_opy_ (u"ࠧࡶ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵࡗࡵࡰࠥ࡯ࡳࠡ࡯࡬ࡷࡸ࡯࡮ࡨࠢࡩࡶࡴࡳࠠࡨࡴ࡬ࡨࠥࡪࡥࡵࡣ࡬ࡰࡸ࠴ࠢࢩ"))
    return bstack11lll111l1_opy_[bstack11ll1_opy_ (u"࠭ࡰ࡭ࡣࡼࡻࡷ࡯ࡧࡩࡶࡘࡶࡱ࠭ࢪ")] + bstack11ll1_opy_ (u"ࠧࡀࡥࡤࡴࡸࡃࠧࢫ")
@measure(event_name=EVENTS.bstack1ll11ll11_opy_, stage=STAGE.bstack11l1llll1_opy_)
def bstack1llll1l1l1_opy_() -> list:
    global CONFIG
    result = []
    if CONFIG:
        auth = (CONFIG[bstack11ll1_opy_ (u"ࠨࡷࡶࡩࡷࡔࡡ࡮ࡧࠪࢬ")], CONFIG[bstack11ll1_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴࡍࡨࡽࠬࢭ")])
        url = bstack1l1l1lllll_opy_
        logger.debug(bstack11ll1_opy_ (u"ࠥࡅࡹࡺࡥ࡮ࡲࡷ࡭ࡳ࡭ࠠࡵࡱࠣࡪࡪࡺࡣࡩࠢࡥࡹ࡮ࡲࡤࡴࠢࡩࡶࡴࡳࠠࡃࡴࡲࡻࡸ࡫ࡲࡔࡶࡤࡧࡰࠦࡔࡶࡴࡥࡳࡘࡩࡡ࡭ࡧࠣࡅࡕࡏࠢࢮ"))
        try:
            response = requests.get(url, auth=auth, headers={bstack11ll1_opy_ (u"ࠦࡈࡵ࡮ࡵࡧࡱࡸ࠲࡚ࡹࡱࡧࠥࢯ"): bstack11ll1_opy_ (u"ࠧࡧࡰࡱ࡮࡬ࡧࡦࡺࡩࡰࡰ࠲࡮ࡸࡵ࡮ࠣࢰ")})
            if response.status_code == 200:
                bstack1l1ll1111l_opy_ = json.loads(response.text)
                bstack1ll11lll_opy_ = bstack1l1ll1111l_opy_.get(bstack11ll1_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡸ࠭ࢱ"), [])
                if bstack1ll11lll_opy_:
                    bstack111l1l11l_opy_ = bstack1ll11lll_opy_[0]
                    build_hashed_id = bstack111l1l11l_opy_.get(bstack11ll1_opy_ (u"ࠧࡩࡣࡶ࡬ࡪࡪ࡟ࡪࡦࠪࢲ"))
                    bstack1l111l1l11_opy_ = bstack1ll1111111_opy_ + build_hashed_id
                    result.extend([build_hashed_id, bstack1l111l1l11_opy_])
                    logger.info(bstack1lll1l1lll_opy_.format(bstack1l111l1l11_opy_))
                    bstack11ll1l1l11_opy_ = CONFIG[bstack11ll1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠫࢳ")]
                    if bstack11ll1_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫࢴ") in CONFIG:
                      bstack11ll1l1l11_opy_ += bstack11ll1_opy_ (u"ࠪࠤࠬࢵ") + CONFIG[bstack11ll1_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭ࢶ")]
                    if bstack11ll1l1l11_opy_ != bstack111l1l11l_opy_.get(bstack11ll1_opy_ (u"ࠬࡴࡡ࡮ࡧࠪࢷ")):
                      logger.debug(bstack1llll11lll_opy_.format(bstack111l1l11l_opy_.get(bstack11ll1_opy_ (u"࠭࡮ࡢ࡯ࡨࠫࢸ")), bstack11ll1l1l11_opy_))
                    return result
                else:
                    logger.debug(bstack11ll1_opy_ (u"ࠢࡂࡖࡖࠤ࠿ࠦࡎࡰࠢࡥࡹ࡮ࡲࡤࡴࠢࡩࡳࡺࡴࡤࠡ࡫ࡱࠤࡹ࡮ࡥࠡࡴࡨࡷࡵࡵ࡮ࡴࡧ࠱ࠦࢹ"))
            else:
                logger.debug(bstack11ll1_opy_ (u"ࠣࡃࡗࡗࠥࡀࠠࡇࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡪࡪࡺࡣࡩࠢࡥࡹ࡮ࡲࡤࡴ࠰ࠥࢺ"))
        except Exception as e:
            logger.error(bstack11ll1_opy_ (u"ࠤࡄࡘࡘࠦ࠺ࠡࡇࡵࡶࡴࡸࠠࡪࡰࠣ࡫ࡪࡺࡴࡪࡰࡪࠤࡧࡻࡩ࡭ࡦࡶࠤ࠿ࠦࡻࡾࠤࢻ").format(str(e)))
    else:
        logger.debug(bstack11ll1_opy_ (u"ࠥࡅ࡙࡙ࠠ࠻ࠢࡆࡓࡓࡌࡉࡈࠢ࡬ࡷࠥࡴ࡯ࡵࠢࡶࡩࡹ࠴ࠠࡖࡰࡤࡦࡱ࡫ࠠࡵࡱࠣࡪࡪࡺࡣࡩࠢࡥࡹ࡮ࡲࡤࡴ࠰ࠥࢼ"))
    return [None, None]
from browserstack_sdk.sdk_cli.cli import cli
from browserstack_sdk.sdk_cli.bstack1111l11l_opy_ import bstack1111l11l_opy_, bstack1l11111l1_opy_, bstack1ll1ll11_opy_, bstack11llllll1l_opy_
from bstack_utils.measure import bstack11l11l11ll_opy_
from bstack_utils.measure import measure
from bstack_utils.percy import *
from bstack_utils.percy_sdk import PercySDK
from bstack_utils.bstack1ll111l1l1_opy_ import bstack1lll1l1ll1_opy_
from bstack_utils.messages import *
from bstack_utils import bstack111lll1l1_opy_
from bstack_utils.constants import *
from bstack_utils.helper import bstack1ll1lllll1_opy_, bstack11l1l1l11l_opy_, bstack1ll1l111_opy_, bstack1lll11l1l_opy_, \
  bstack11lllll11l_opy_, \
  Notset, bstack11lll11lll_opy_, \
  bstack11llllllll_opy_, bstack1lllll11l1_opy_, bstack1l1llll11l_opy_, bstack1lll11llll_opy_, bstack1l1l1l1l_opy_, bstack1l11lll111_opy_, \
  bstack11l1llll_opy_, \
  bstack1l11ll11l1_opy_, bstack1l1ll11ll_opy_, bstack1l1ll111l1_opy_, bstack11lllllll_opy_, \
  bstack11l111l1ll_opy_, bstack11l1l11l11_opy_, bstack1111lll1_opy_, bstack11l111lll_opy_, bstack1l11llllll_opy_
from bstack_utils.bstack111ll1l1ll_opy_ import bstack1111l1lll_opy_
from bstack_utils.bstack11l1lll11_opy_ import bstack11ll11l11l_opy_, bstack11l11111l1_opy_
from bstack_utils.bstack1ll11l1l_opy_ import bstack11ll1111ll_opy_
from bstack_utils.bstack11llll1l1_opy_ import bstack1ll11ll1ll_opy_, bstack11l11111ll_opy_
from bstack_utils.bstack1l11l111l1_opy_ import bstack1l11l111l1_opy_
from bstack_utils.bstack11l11ll1_opy_ import bstack1lll111l11_opy_
from bstack_utils.proxy import bstack111lllll1l_opy_, bstack1lllll1111_opy_, bstack11l1ll11l_opy_, bstack1l1ll11lll_opy_
from bstack_utils.bstack1l1l111111_opy_ import bstack1l11ll1111_opy_, bstack11l1l111l_opy_
import bstack_utils.bstack1l111l11ll_opy_ as bstack1l11111ll1_opy_
import bstack_utils.bstack1llll1l11_opy_ as bstack11l1111l1l_opy_
from browserstack_sdk.sdk_cli.cli import cli
from browserstack_sdk.sdk_cli.utils.bstack1l11lll1ll_opy_ import bstack11ll1l11l_opy_
from bstack_utils.bstack11l111l1_opy_ import bstack1lll1lll_opy_
from bstack_utils.bstack1llll1l111_opy_ import bstack111l1llll_opy_
if os.getenv(bstack11ll1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡇࡑࡏ࡟ࡉࡑࡒࡏࡘ࠭ࢽ")):
  cli.bstack1lll11111_opy_()
else:
  os.environ[bstack11ll1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡈࡒࡉࡠࡊࡒࡓࡐ࡙ࠧࢾ")] = bstack11ll1_opy_ (u"࠭ࡴࡳࡷࡨࠫࢿ")
bstack1ll111l1_opy_ = bstack11ll1_opy_ (u"ࠧࠡࠢ࠲࠮ࠥࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾ࠢ࠭࠳ࡡࡴࠠࠡ࡫ࡩࠬࡵࡧࡧࡦࠢࡀࡁࡂࠦࡶࡰ࡫ࡧࠤ࠵࠯ࠠࡼ࡞ࡱࠤࠥࠦࡴࡳࡻࡾࡠࡳࠦࡣࡰࡰࡶࡸࠥ࡬ࡳࠡ࠿ࠣࡶࡪࡷࡵࡪࡴࡨࠬࡡ࠭ࡦࡴ࡞ࠪ࠭ࡀࡢ࡮ࠡࠢࠣࠤࠥ࡬ࡳ࠯ࡣࡳࡴࡪࡴࡤࡇ࡫࡯ࡩࡘࡿ࡮ࡤࠪࡥࡷࡹࡧࡣ࡬ࡡࡳࡥࡹ࡮ࠬࠡࡌࡖࡓࡓ࠴ࡳࡵࡴ࡬ࡲ࡬࡯ࡦࡺࠪࡳࡣ࡮ࡴࡤࡦࡺࠬࠤ࠰ࠦࠢ࠻ࠤࠣ࠯ࠥࡐࡓࡐࡐ࠱ࡷࡹࡸࡩ࡯ࡩ࡬ࡪࡾ࠮ࡊࡔࡑࡑ࠲ࡵࡧࡲࡴࡧࠫࠬࡦࡽࡡࡪࡶࠣࡲࡪࡽࡐࡢࡩࡨ࠶࠳࡫ࡶࡢ࡮ࡸࡥࡹ࡫ࠨࠣࠪࠬࠤࡂࡄࠠࡼࡿࠥ࠰ࠥࡢࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡥࡹࡧࡦࡹࡹࡵࡲ࠻ࠢࡾࠦࡦࡩࡴࡪࡱࡱࠦ࠿ࠦࠢࡨࡧࡷࡗࡪࡹࡳࡪࡱࡱࡈࡪࡺࡡࡪ࡮ࡶࠦࢂࡢࠧࠪࠫࠬ࡟ࠧ࡮ࡡࡴࡪࡨࡨࡤ࡯ࡤࠣ࡟ࠬࠤ࠰ࠦࠢ࠭࡞࡟ࡲࠧ࠯࡜࡯ࠢࠣࠤࠥࢃࡣࡢࡶࡦ࡬࠭࡫ࡸࠪࡽ࡟ࡲࠥࠦࠠࠡࡿ࡟ࡲࠥࠦࡽ࡝ࡰࠣࠤ࠴࠰ࠠ࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࠤ࠯࠵ࠧࣀ")
bstack1l1l111ll1_opy_ = bstack11ll1_opy_ (u"ࠨ࡞ࡱ࠳࠯ࠦ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࠣ࠮࠴ࡢ࡮ࡤࡱࡱࡷࡹࠦࡢࡴࡶࡤࡧࡰࡥࡰࡢࡶ࡫ࠤࡂࠦࡰࡳࡱࡦࡩࡸࡹ࠮ࡢࡴࡪࡺࡠࡶࡲࡰࡥࡨࡷࡸ࠴ࡡࡳࡩࡹ࠲ࡱ࡫࡮ࡨࡶ࡫ࠤ࠲ࠦ࠳࡞࡞ࡱࡧࡴࡴࡳࡵࠢࡥࡷࡹࡧࡣ࡬ࡡࡦࡥࡵࡹࠠ࠾ࠢࡳࡶࡴࡩࡥࡴࡵ࠱ࡥࡷ࡭ࡶ࡜ࡲࡵࡳࡨ࡫ࡳࡴ࠰ࡤࡶ࡬ࡼ࠮࡭ࡧࡱ࡫ࡹ࡮ࠠ࠮ࠢ࠴ࡡࡡࡴࡣࡰࡰࡶࡸࠥࡶ࡟ࡪࡰࡧࡩࡽࠦ࠽ࠡࡲࡵࡳࡨ࡫ࡳࡴ࠰ࡤࡶ࡬ࡼ࡛ࡱࡴࡲࡧࡪࡹࡳ࠯ࡣࡵ࡫ࡻ࠴࡬ࡦࡰࡪࡸ࡭ࠦ࠭ࠡ࠴ࡠࡠࡳࡶࡲࡰࡥࡨࡷࡸ࠴ࡡࡳࡩࡹࠤࡂࠦࡰࡳࡱࡦࡩࡸࡹ࠮ࡢࡴࡪࡺ࠳ࡹ࡬ࡪࡥࡨࠬ࠵࠲ࠠࡱࡴࡲࡧࡪࡹࡳ࠯ࡣࡵ࡫ࡻ࠴࡬ࡦࡰࡪࡸ࡭ࠦ࠭ࠡ࠵ࠬࡠࡳࡩ࡯࡯ࡵࡷࠤ࡮ࡳࡰࡰࡴࡷࡣࡵࡲࡡࡺࡹࡵ࡭࡬࡮ࡴ࠵ࡡࡥࡷࡹࡧࡣ࡬ࠢࡀࠤࡷ࡫ࡱࡶ࡫ࡵࡩ࠭ࠨࡰ࡭ࡣࡼࡻࡷ࡯ࡧࡩࡶࠥ࠭ࡀࡢ࡮ࡪ࡯ࡳࡳࡷࡺ࡟ࡱ࡮ࡤࡽࡼࡸࡩࡨࡪࡷ࠸ࡤࡨࡳࡵࡣࡦ࡯࠳ࡩࡨࡳࡱࡰ࡭ࡺࡳ࠮࡭ࡣࡸࡲࡨ࡮ࠠ࠾ࠢࡤࡷࡾࡴࡣࠡࠪ࡯ࡥࡺࡴࡣࡩࡑࡳࡸ࡮ࡵ࡮ࡴࠫࠣࡁࡃࠦࡻ࡝ࡰ࡯ࡩࡹࠦࡣࡢࡲࡶ࠿ࡡࡴࡴࡳࡻࠣࡿࡡࡴࡣࡢࡲࡶࠤࡂࠦࡊࡔࡑࡑ࠲ࡵࡧࡲࡴࡧࠫࡦࡸࡺࡡࡤ࡭ࡢࡧࡦࡶࡳࠪ࡞ࡱࠤࠥࢃࠠࡤࡣࡷࡧ࡭࠮ࡥࡹࠫࠣࡿࡡࡴࠠࠡࠢࠣࢁࡡࡴࠠࠡࡴࡨࡸࡺࡸ࡮ࠡࡣࡺࡥ࡮ࡺࠠࡪ࡯ࡳࡳࡷࡺ࡟ࡱ࡮ࡤࡽࡼࡸࡩࡨࡪࡷ࠸ࡤࡨࡳࡵࡣࡦ࡯࠳ࡩࡨࡳࡱࡰ࡭ࡺࡳ࠮ࡤࡱࡱࡲࡪࡩࡴࠩࡽ࡟ࡲࠥࠦࠠࠡࡹࡶࡉࡳࡪࡰࡰ࡫ࡱࡸ࠿ࠦࡠࡸࡵࡶ࠾࠴࠵ࡣࡥࡲ࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡦࡳࡲ࠵ࡰ࡭ࡣࡼࡻࡷ࡯ࡧࡩࡶࡂࡧࡦࡶࡳ࠾ࠦࡾࡩࡳࡩ࡯ࡥࡧࡘࡖࡎࡉ࡯࡮ࡲࡲࡲࡪࡴࡴࠩࡌࡖࡓࡓ࠴ࡳࡵࡴ࡬ࡲ࡬࡯ࡦࡺࠪࡦࡥࡵࡹࠩࠪࡿࡣ࠰ࡡࡴࠠࠡࠢࠣ࠲࠳࠴࡬ࡢࡷࡱࡧ࡭ࡕࡰࡵ࡫ࡲࡲࡸࡢ࡮ࠡࠢࢀ࠭ࡡࡴࡽ࡝ࡰ࠲࠮ࠥࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾ࠢ࠭࠳ࡡࡴࠧࣁ")
from ._version import __version__
bstack1l1ll1111_opy_ = None
CONFIG = {}
bstack1l11111ll_opy_ = {}
bstack1llllll11l_opy_ = {}
bstack1l111l111l_opy_ = None
bstack1l11l11l11_opy_ = None
bstack1ll1l11111_opy_ = None
bstack111l11l1l_opy_ = -1
bstack1llll11l1l_opy_ = 0
bstack1l1l1l11l_opy_ = bstack11l1111l1_opy_
bstack11l1l1l11_opy_ = 1
bstack1ll1lll1l1_opy_ = False
bstack1ll111111_opy_ = False
bstack11l1l11ll_opy_ = bstack11ll1_opy_ (u"ࠩࠪࣂ")
bstack11ll1l11l1_opy_ = bstack11ll1_opy_ (u"ࠪࠫࣃ")
bstack1l11l1l1ll_opy_ = False
bstack1llll1l1_opy_ = True
bstack111llll1ll_opy_ = bstack11ll1_opy_ (u"ࠫࠬࣄ")
bstack1lll111ll_opy_ = []
bstack1l1lll11_opy_ = threading.Lock()
bstack11l111ll_opy_ = threading.Lock()
bstack1l1ll11ll1_opy_ = bstack11ll1_opy_ (u"ࠬ࠭ࣅ")
bstack1lll1ll1_opy_ = False
bstack1lll1111_opy_ = None
bstack1l1lll1l11_opy_ = None
bstack11l1l1111_opy_ = None
bstack11111ll1l_opy_ = -1
bstack1lll1ll1ll_opy_ = os.path.join(os.path.expanduser(bstack11ll1_opy_ (u"࠭ࡾࠨࣆ")), bstack11ll1_opy_ (u"ࠧ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠧࣇ"), bstack11ll1_opy_ (u"ࠨ࠰ࡵࡳࡧࡵࡴ࠮ࡴࡨࡴࡴࡸࡴ࠮ࡪࡨࡰࡵ࡫ࡲ࠯࡬ࡶࡳࡳ࠭ࣈ"))
bstack11ll1ll11l_opy_ = 0
bstack1lll1l1l11_opy_ = 0
bstack111l1l111_opy_ = []
bstack1l111lll_opy_ = []
bstack1l1111l1ll_opy_ = []
bstack1ll1l1l1l1_opy_ = []
bstack1ll11ll111_opy_ = bstack11ll1_opy_ (u"ࠩࠪࣉ")
bstack11l1l1ll1l_opy_ = bstack11ll1_opy_ (u"ࠪࠫ࣊")
bstack1111ll1l1_opy_ = False
bstack1111l1l1l_opy_ = False
bstack1l11l11ll_opy_ = {}
bstack11ll1llll_opy_ = {}
bstack1lll1l1l_opy_ = None
bstack1llll1lll1_opy_ = None
bstack11ll1111_opy_ = None
bstack1ll1ll111l_opy_ = None
bstack11l1111l_opy_ = None
bstack1l11l1ll_opy_ = None
bstack1l111l1ll_opy_ = None
bstack11l11lllll_opy_ = None
bstack1ll1llll11_opy_ = None
bstack11l1lllll_opy_ = None
bstack1l1l1l1111_opy_ = None
bstack1ll1l11l1_opy_ = None
bstack1ll1l1111_opy_ = None
bstack1llll1llll_opy_ = None
bstack1l1ll11l_opy_ = None
bstack1ll111ll_opy_ = None
bstack1l111l11l_opy_ = None
bstack1lllll11ll_opy_ = None
bstack1l11l11ll1_opy_ = None
bstack11ll11l1ll_opy_ = None
bstack1llllll1l_opy_ = None
bstack11l1llll11_opy_ = None
bstack1lll1111l1_opy_ = None
thread_local = threading.local()
bstack1lll11lll1_opy_ = False
bstack1l1ll1l11l_opy_ = bstack11ll1_opy_ (u"ࠦࠧ࣋")
logger = bstack111lll1l1_opy_.get_logger(__name__, bstack1l1l1l11l_opy_)
bstack11ll111l1l_opy_ = bstack111lll1l1_opy_.bstack1l1l111l_opy_(__name__)
bstack1l1l1ll1l_opy_ = Config.bstack1l1l1111_opy_()
percy = bstack11l1l11l1_opy_()
bstack11111lll_opy_ = bstack1lll1l1ll1_opy_()
bstack11l1ll111_opy_ = bstack111ll1111_opy_()
def bstack1l1l1l111l_opy_():
  global CONFIG
  global bstack1111ll1l1_opy_
  global bstack1l1l1ll1l_opy_
  testContextOptions = bstack111ll1ll11_opy_(CONFIG)
  if bstack11lllll11l_opy_(CONFIG):
    if (bstack11ll1_opy_ (u"ࠬࡹ࡫ࡪࡲࡖࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠧ࣌") in testContextOptions and str(testContextOptions[bstack11ll1_opy_ (u"࠭ࡳ࡬࡫ࡳࡗࡪࡹࡳࡪࡱࡱࡒࡦࡳࡥࠨ࣍")]).lower() == bstack11ll1_opy_ (u"ࠧࡵࡴࡸࡩࠬ࣎")):
      bstack1111ll1l1_opy_ = True
    bstack1l1l1ll1l_opy_.bstack1ll11111l_opy_(testContextOptions.get(bstack11ll1_opy_ (u"ࠨࡵ࡮࡭ࡵ࡙ࡥࡴࡵ࡬ࡳࡳ࡙ࡴࡢࡶࡸࡷ࣏ࠬ"), False))
  else:
    bstack1111ll1l1_opy_ = True
    bstack1l1l1ll1l_opy_.bstack1ll11111l_opy_(True)
def bstack1l11l11l1l_opy_():
  from appium.version import version as appium_version
  return version.parse(appium_version)
def bstack1ll1ll1l11_opy_():
  from selenium import webdriver
  return version.parse(webdriver.__version__)
def bstack1ll111l111_opy_():
  global bstack11ll1llll_opy_
  args = sys.argv
  for i in range(len(args)):
    if bstack11ll1_opy_ (u"ࠤ࠰࠱ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡦࡳࡳ࡬ࡩࡨࡨ࡬ࡰࡪࠨ࣐") == args[i].lower() or bstack11ll1_opy_ (u"ࠥ࠱࠲ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡨࡵ࡮ࡧ࡫ࡪ࣑ࠦ") == args[i].lower():
      path = args[i + 1]
      sys.argv.remove(args[i])
      sys.argv.remove(path)
      bstack11ll1llll_opy_[bstack11ll1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡇࡔࡔࡆࡊࡉࡢࡊࡎࡒࡅࠨ࣒")] = path
      return path
  return None
bstack11llll111l_opy_ = re.compile(bstack11ll1_opy_ (u"ࡷࠨ࠮ࠫࡁ࡟ࠨࢀ࠮࠮ࠫࡁࠬࢁ࠳࠰࠿࣓ࠣ"))
def bstack11l111111l_opy_(loader, node):
  value = loader.construct_scalar(node)
  for group in bstack11llll111l_opy_.findall(value):
    if group is not None and os.environ.get(group) is not None:
      value = value.replace(bstack11ll1_opy_ (u"ࠨࠤࡼࠤࣔ") + group + bstack11ll1_opy_ (u"ࠢࡾࠤࣕ"), os.environ.get(group))
  return value
def bstack1lll111ll1_opy_():
  global bstack1lll1111l1_opy_
  if bstack1lll1111l1_opy_ is None:
        bstack1lll1111l1_opy_ = bstack1ll111l111_opy_()
  bstack1ll111ll11_opy_ = bstack1lll1111l1_opy_
  if bstack1ll111ll11_opy_ and os.path.exists(os.path.abspath(bstack1ll111ll11_opy_)):
    fileName = bstack1ll111ll11_opy_
  if bstack11ll1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡄࡑࡑࡊࡎࡍ࡟ࡇࡋࡏࡉࠬࣖ") in os.environ and os.path.exists(
          os.path.abspath(os.environ[bstack11ll1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡅࡒࡒࡋࡏࡇࡠࡈࡌࡐࡊ࠭ࣗ")])) and not bstack11ll1_opy_ (u"ࠪࡪ࡮ࡲࡥࡏࡣࡰࡩࠬࣘ") in locals():
    fileName = os.environ[bstack11ll1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡇࡔࡔࡆࡊࡉࡢࡊࡎࡒࡅࠨࣙ")]
  if bstack11ll1_opy_ (u"ࠬ࡬ࡩ࡭ࡧࡑࡥࡲ࡫ࠧࣚ") in locals():
    bstack1ll11l_opy_ = os.path.abspath(fileName)
  else:
    bstack1ll11l_opy_ = bstack11ll1_opy_ (u"࠭ࠧࣛ")
  bstack11lll11l1l_opy_ = os.getcwd()
  bstack111lll111_opy_ = bstack11ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡹ࡮࡮ࠪࣜ")
  bstack1ll11ll11l_opy_ = bstack11ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡺࡣࡰࡰࠬࣝ")
  while (not os.path.exists(bstack1ll11l_opy_)) and bstack11lll11l1l_opy_ != bstack11ll1_opy_ (u"ࠤࠥࣞ"):
    bstack1ll11l_opy_ = os.path.join(bstack11lll11l1l_opy_, bstack111lll111_opy_)
    if not os.path.exists(bstack1ll11l_opy_):
      bstack1ll11l_opy_ = os.path.join(bstack11lll11l1l_opy_, bstack1ll11ll11l_opy_)
    if bstack11lll11l1l_opy_ != os.path.dirname(bstack11lll11l1l_opy_):
      bstack11lll11l1l_opy_ = os.path.dirname(bstack11lll11l1l_opy_)
    else:
      bstack11lll11l1l_opy_ = bstack11ll1_opy_ (u"ࠥࠦࣟ")
  bstack1lll1111l1_opy_ = bstack1ll11l_opy_ if os.path.exists(bstack1ll11l_opy_) else None
  return bstack1lll1111l1_opy_
def bstack11lll1l111_opy_(config):
    if bstack11ll1_opy_ (u"ࠫࡹ࡫ࡳࡵࡔࡨࡴࡴࡸࡴࡪࡰࡪࠫ࣠") in config:
      config[bstack11ll1_opy_ (u"ࠬࡺࡥࡴࡶࡒࡦࡸ࡫ࡲࡷࡣࡥ࡭ࡱ࡯ࡴࡺࠩ࣡")] = config[bstack11ll1_opy_ (u"࠭ࡴࡦࡵࡷࡖࡪࡶ࡯ࡳࡶ࡬ࡲ࡬࠭࣢")]
    if bstack11ll1_opy_ (u"ࠧࡵࡧࡶࡸࡗ࡫ࡰࡰࡴࡷ࡭ࡳ࡭ࡏࡱࡶ࡬ࡳࡳࡹࣣࠧ") in config:
      config[bstack11ll1_opy_ (u"ࠨࡶࡨࡷࡹࡕࡢࡴࡧࡵࡺࡦࡨࡩ࡭࡫ࡷࡽࡔࡶࡴࡪࡱࡱࡷࠬࣤ")] = config[bstack11ll1_opy_ (u"ࠩࡷࡩࡸࡺࡒࡦࡲࡲࡶࡹ࡯࡮ࡨࡑࡳࡸ࡮ࡵ࡮ࡴࠩࣥ")]
def bstack11l111l1l1_opy_():
  bstack1ll11l_opy_ = bstack1lll111ll1_opy_()
  if not os.path.exists(bstack1ll11l_opy_):
    bstack11ll11l11_opy_(
      bstack1llll11l1_opy_.format(os.getcwd()))
  try:
    with open(bstack1ll11l_opy_, bstack11ll1_opy_ (u"ࠪࡶࣦࠬ")) as stream:
      yaml.add_implicit_resolver(bstack11ll1_opy_ (u"ࠦࠦࡶࡡࡵࡪࡨࡼࠧࣧ"), bstack11llll111l_opy_)
      yaml.add_constructor(bstack11ll1_opy_ (u"ࠧࠧࡰࡢࡶ࡫ࡩࡽࠨࣨ"), bstack11l111111l_opy_)
      config = yaml.load(stream, yaml.FullLoader)
      bstack11lll1l111_opy_(config)
      return config
  except:
    with open(bstack1ll11l_opy_, bstack11ll1_opy_ (u"࠭ࡲࠨࣩ")) as stream:
      try:
        config = yaml.safe_load(stream)
        bstack11lll1l111_opy_(config)
        return config
      except yaml.YAMLError as exc:
        bstack11ll11l11_opy_(bstack1llll1lll_opy_.format(str(exc)))
def bstack1ll11111l1_opy_(config):
  bstack1l111ll1ll_opy_ = bstack1l1l1l111_opy_(config)
  for option in list(bstack1l111ll1ll_opy_):
    if option.lower() in bstack1lll111lll_opy_ and option != bstack1lll111lll_opy_[option.lower()]:
      bstack1l111ll1ll_opy_[bstack1lll111lll_opy_[option.lower()]] = bstack1l111ll1ll_opy_[option]
      del bstack1l111ll1ll_opy_[option]
  return config
def bstack1l1l1lll_opy_():
  global bstack1llllll11l_opy_
  for key, bstack1llll1l1l_opy_ in bstack1l1ll11l11_opy_.items():
    if isinstance(bstack1llll1l1l_opy_, list):
      for var in bstack1llll1l1l_opy_:
        if var in os.environ and os.environ[var] and str(os.environ[var]).strip():
          bstack1llllll11l_opy_[key] = os.environ[var]
          break
    elif bstack1llll1l1l_opy_ in os.environ and os.environ[bstack1llll1l1l_opy_] and str(os.environ[bstack1llll1l1l_opy_]).strip():
      bstack1llllll11l_opy_[key] = os.environ[bstack1llll1l1l_opy_]
  if bstack11ll1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡌࡐࡅࡄࡐࡤࡏࡄࡆࡐࡗࡍࡋࡏࡅࡓࠩ࣪") in os.environ:
    bstack1llllll11l_opy_[bstack11ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡕࡷࡥࡨࡱࡌࡰࡥࡤࡰࡔࡶࡴࡪࡱࡱࡷࠬ࣫")] = {}
    bstack1llllll11l_opy_[bstack11ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࡍࡱࡦࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭࣬")][bstack11ll1_opy_ (u"ࠪࡰࡴࡩࡡ࡭ࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶ࣭ࠬ")] = os.environ[bstack11ll1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡐࡔࡉࡁࡍࡡࡌࡈࡊࡔࡔࡊࡈࡌࡉࡗ࣮࠭")]
def bstack1l11llll_opy_():
  global bstack1l11111ll_opy_
  global bstack111llll1ll_opy_
  global bstack11ll1llll_opy_
  bstack1llll1ll1l_opy_ = []
  for idx, val in enumerate(sys.argv):
    if idx < len(sys.argv) - 1 and bstack11ll1_opy_ (u"ࠬ࠳࠭ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴࡬ࡰࡥࡤࡰࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨ࣯").lower() == val.lower():
      bstack1l11111ll_opy_[bstack11ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࡒࡴࡹ࡯࡯࡯ࡵࣰࠪ")] = {}
      bstack1l11111ll_opy_[bstack11ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡔࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࡓࡵࡺࡩࡰࡰࡶࣱࠫ")][bstack11ll1_opy_ (u"ࠨ࡮ࡲࡧࡦࡲࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࣲࠪ")] = sys.argv[idx + 1]
      bstack1llll1ll1l_opy_.extend([idx, idx + 1])
      break
  for key, bstack1l1ll1l1l_opy_ in bstack11l1l111l1_opy_.items():
    if isinstance(bstack1l1ll1l1l_opy_, list):
      for idx, val in enumerate(sys.argv):
        if idx >= len(sys.argv) - 1:
          continue
        for var in bstack1l1ll1l1l_opy_:
          if bstack11ll1_opy_ (u"ࠩ࠰࠱ࠬࣳ") + var.lower() == val.lower() and key not in bstack1l11111ll_opy_:
            bstack1l11111ll_opy_[key] = sys.argv[idx + 1]
            bstack111llll1ll_opy_ += bstack11ll1_opy_ (u"ࠪࠤ࠲࠳ࠧࣴ") + var + bstack11ll1_opy_ (u"ࠫࠥ࠭ࣵ") + shlex.quote(sys.argv[idx + 1])
            bstack1l11llllll_opy_(bstack11ll1llll_opy_, key, sys.argv[idx + 1])
            bstack1llll1ll1l_opy_.extend([idx, idx + 1])
            break
    else:
      for idx, val in enumerate(sys.argv):
        if idx >= len(sys.argv) - 1:
          continue
        if bstack11ll1_opy_ (u"ࠬ࠳࠭ࠨࣶ") + bstack1l1ll1l1l_opy_.lower() == val.lower() and key not in bstack1l11111ll_opy_:
          bstack1l11111ll_opy_[key] = sys.argv[idx + 1]
          bstack111llll1ll_opy_ += bstack11ll1_opy_ (u"࠭ࠠ࠮࠯ࠪࣷ") + bstack1l1ll1l1l_opy_ + bstack11ll1_opy_ (u"ࠧࠡࠩࣸ") + shlex.quote(sys.argv[idx + 1])
          bstack1l11llllll_opy_(bstack11ll1llll_opy_, key, sys.argv[idx + 1])
          bstack1llll1ll1l_opy_.extend([idx, idx + 1])
  for idx in sorted(set(bstack1llll1ll1l_opy_), reverse=True):
    if idx < len(sys.argv):
      del sys.argv[idx]
def bstack1l1ll111l_opy_(config):
  bstack1ll1l11lll_opy_ = config.keys()
  for bstack1lll111l_opy_, bstack11l11l1ll_opy_ in bstack11l111ll1l_opy_.items():
    if bstack11l11l1ll_opy_ in bstack1ll1l11lll_opy_:
      config[bstack1lll111l_opy_] = config[bstack11l11l1ll_opy_]
      del config[bstack11l11l1ll_opy_]
  for bstack1lll111l_opy_, bstack11l11l1ll_opy_ in bstack11ll1lll1l_opy_.items():
    if isinstance(bstack11l11l1ll_opy_, list):
      for bstack1l11l11l1_opy_ in bstack11l11l1ll_opy_:
        if bstack1l11l11l1_opy_ in bstack1ll1l11lll_opy_:
          config[bstack1lll111l_opy_] = config[bstack1l11l11l1_opy_]
          del config[bstack1l11l11l1_opy_]
          break
    elif bstack11l11l1ll_opy_ in bstack1ll1l11lll_opy_:
      config[bstack1lll111l_opy_] = config[bstack11l11l1ll_opy_]
      del config[bstack11l11l1ll_opy_]
  for bstack1l11l11l1_opy_ in list(config):
    for bstack1l111ll11l_opy_ in bstack1l111111l_opy_:
      if bstack1l11l11l1_opy_.lower() == bstack1l111ll11l_opy_.lower() and bstack1l11l11l1_opy_ != bstack1l111ll11l_opy_:
        config[bstack1l111ll11l_opy_] = config[bstack1l11l11l1_opy_]
        del config[bstack1l11l11l1_opy_]
  bstack11l11lll11_opy_ = [{}]
  if not config.get(bstack11ll1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࣹࠫ")):
    config[bstack11ll1_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࣺࠬ")] = [{}]
  bstack11l11lll11_opy_ = config[bstack11ll1_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ࣻ")]
  for platform in bstack11l11lll11_opy_:
    for bstack1l11l11l1_opy_ in list(platform):
      for bstack1l111ll11l_opy_ in bstack1l111111l_opy_:
        if bstack1l11l11l1_opy_.lower() == bstack1l111ll11l_opy_.lower() and bstack1l11l11l1_opy_ != bstack1l111ll11l_opy_:
          platform[bstack1l111ll11l_opy_] = platform[bstack1l11l11l1_opy_]
          del platform[bstack1l11l11l1_opy_]
  for bstack1lll111l_opy_, bstack11l11l1ll_opy_ in bstack11ll1lll1l_opy_.items():
    for platform in bstack11l11lll11_opy_:
      if isinstance(bstack11l11l1ll_opy_, list):
        for bstack1l11l11l1_opy_ in bstack11l11l1ll_opy_:
          if bstack1l11l11l1_opy_ in platform:
            platform[bstack1lll111l_opy_] = platform[bstack1l11l11l1_opy_]
            del platform[bstack1l11l11l1_opy_]
            break
      elif bstack11l11l1ll_opy_ in platform:
        platform[bstack1lll111l_opy_] = platform[bstack11l11l1ll_opy_]
        del platform[bstack11l11l1ll_opy_]
  for bstack11ll1ll111_opy_ in bstack1l1lll11l1_opy_:
    if bstack11ll1ll111_opy_ in config:
      if not bstack1l1lll11l1_opy_[bstack11ll1ll111_opy_] in config:
        config[bstack1l1lll11l1_opy_[bstack11ll1ll111_opy_]] = {}
      config[bstack1l1lll11l1_opy_[bstack11ll1ll111_opy_]].update(config[bstack11ll1ll111_opy_])
      del config[bstack11ll1ll111_opy_]
  for platform in bstack11l11lll11_opy_:
    for bstack11ll1ll111_opy_ in bstack1l1lll11l1_opy_:
      if bstack11ll1ll111_opy_ in list(platform):
        if not bstack1l1lll11l1_opy_[bstack11ll1ll111_opy_] in platform:
          platform[bstack1l1lll11l1_opy_[bstack11ll1ll111_opy_]] = {}
        platform[bstack1l1lll11l1_opy_[bstack11ll1ll111_opy_]].update(platform[bstack11ll1ll111_opy_])
        del platform[bstack11ll1ll111_opy_]
  config = bstack1ll11111l1_opy_(config)
  return config
def bstack1ll1lll11_opy_(config):
  global bstack11ll1l11l1_opy_
  bstack1l11ll1l1_opy_ = False
  if bstack11ll1_opy_ (u"ࠫࡹࡻࡲࡣࡱࡖࡧࡦࡲࡥࠨࣼ") in config and str(config[bstack11ll1_opy_ (u"ࠬࡺࡵࡳࡤࡲࡗࡨࡧ࡬ࡦࠩࣽ")]).lower() != bstack11ll1_opy_ (u"࠭ࡦࡢ࡮ࡶࡩࠬࣾ"):
    if bstack11ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࠫࣿ") not in config or str(config[bstack11ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡌࡰࡥࡤࡰࠬऀ")]).lower() == bstack11ll1_opy_ (u"ࠩࡩࡥࡱࡹࡥࠨँ"):
      config[bstack11ll1_opy_ (u"ࠪࡰࡴࡩࡡ࡭ࠩं")] = False
    else:
      bstack11lll111l1_opy_ = bstack11lll111l_opy_()
      if bstack11ll1_opy_ (u"ࠫ࡮ࡹࡔࡳ࡫ࡤࡰࡌࡸࡩࡥࠩः") in bstack11lll111l1_opy_:
        if not bstack11ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࡑࡳࡸ࡮ࡵ࡮ࡴࠩऄ") in config:
          config[bstack11ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࡒࡴࡹ࡯࡯࡯ࡵࠪअ")] = {}
        config[bstack11ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡔࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࡓࡵࡺࡩࡰࡰࡶࠫआ")][bstack11ll1_opy_ (u"ࠨ࡮ࡲࡧࡦࡲࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪइ")] = bstack11ll1_opy_ (u"ࠩࡤࡸࡸ࠳ࡲࡦࡲࡨࡥࡹ࡫ࡲࠨई")
        bstack1l11ll1l1_opy_ = True
        bstack11ll1l11l1_opy_ = config[bstack11ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡗࡹࡧࡣ࡬ࡎࡲࡧࡦࡲࡏࡱࡶ࡬ࡳࡳࡹࠧउ")].get(bstack11ll1_opy_ (u"ࠫࡱࡵࡣࡢ࡮ࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭ऊ"))
  if bstack11lllll11l_opy_(config) and bstack11ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࠩऋ") in config and str(config[bstack11ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࠪऌ")]).lower() != bstack11ll1_opy_ (u"ࠧࡧࡣ࡯ࡷࡪ࠭ऍ") and not bstack1l11ll1l1_opy_:
    if not bstack11ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡕࡷࡥࡨࡱࡌࡰࡥࡤࡰࡔࡶࡴࡪࡱࡱࡷࠬऎ") in config:
      config[bstack11ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࡍࡱࡦࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭ए")] = {}
    if not config[bstack11ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡗࡹࡧࡣ࡬ࡎࡲࡧࡦࡲࡏࡱࡶ࡬ࡳࡳࡹࠧऐ")].get(bstack11ll1_opy_ (u"ࠫࡸࡱࡩࡱࡄ࡬ࡲࡦࡸࡹࡊࡰ࡬ࡸ࡮ࡧ࡬ࡪࡵࡤࡸ࡮ࡵ࡮ࠨऑ")) and not bstack11ll1_opy_ (u"ࠬࡲ࡯ࡤࡣ࡯ࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧऒ") in config[bstack11ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࡒࡴࡹ࡯࡯࡯ࡵࠪओ")]:
      bstack111lll1lll_opy_ = datetime.datetime.now()
      bstack1ll1llll1l_opy_ = bstack111lll1lll_opy_.strftime(bstack11ll1_opy_ (u"ࠧࠦࡦࡢࠩࡧࡥࠥࡉࠧࡐࠫऔ"))
      hostname = socket.gethostname()
      bstack1l1l11111_opy_ = bstack11ll1_opy_ (u"ࠨࠩक").join(random.choices(string.ascii_lowercase + string.digits, k=4))
      identifier = bstack11ll1_opy_ (u"ࠩࡾࢁࡤࢁࡽࡠࡽࢀࠫख").format(bstack1ll1llll1l_opy_, hostname, bstack1l1l11111_opy_)
      config[bstack11ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡗࡹࡧࡣ࡬ࡎࡲࡧࡦࡲࡏࡱࡶ࡬ࡳࡳࡹࠧग")][bstack11ll1_opy_ (u"ࠫࡱࡵࡣࡢ࡮ࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭घ")] = identifier
    bstack11ll1l11l1_opy_ = config[bstack11ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࡑࡳࡸ࡮ࡵ࡮ࡴࠩङ")].get(bstack11ll1_opy_ (u"࠭࡬ࡰࡥࡤࡰࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨच"))
  return config
def bstack1ll1ll11l_opy_():
  bstack1l1111l11l_opy_ =  bstack1lll11llll_opy_()[bstack11ll1_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡥ࡮ࡶ࡯ࡥࡩࡷ࠭छ")]
  return bstack1l1111l11l_opy_ if bstack1l1111l11l_opy_ else -1
def bstack1l1ll111ll_opy_(bstack1l1111l11l_opy_):
  global CONFIG
  if not bstack11ll1_opy_ (u"ࠨࠦࡾࡆ࡚ࡏࡌࡅࡡࡑ࡙ࡒࡈࡅࡓࡿࠪज") in CONFIG[bstack11ll1_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫझ")]:
    return
  CONFIG[bstack11ll1_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬञ")] = CONFIG[bstack11ll1_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭ट")].replace(
    bstack11ll1_opy_ (u"ࠬࠪࡻࡃࡗࡌࡐࡉࡥࡎࡖࡏࡅࡉࡗࢃࠧठ"),
    str(bstack1l1111l11l_opy_)
  )
def bstack11l1l1llll_opy_():
  global CONFIG
  if not bstack11ll1_opy_ (u"࠭ࠤࡼࡆࡄࡘࡊࡥࡔࡊࡏࡈࢁࠬड") in CONFIG[bstack11ll1_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩढ")]:
    return
  bstack111lll1lll_opy_ = datetime.datetime.now()
  bstack1ll1llll1l_opy_ = bstack111lll1lll_opy_.strftime(bstack11ll1_opy_ (u"ࠨࠧࡧ࠱ࠪࡨ࠭ࠦࡊ࠽ࠩࡒ࠭ण"))
  CONFIG[bstack11ll1_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫत")] = CONFIG[bstack11ll1_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬथ")].replace(
    bstack11ll1_opy_ (u"ࠫࠩࢁࡄࡂࡖࡈࡣ࡙ࡏࡍࡆࡿࠪद"),
    bstack1ll1llll1l_opy_
  )
def bstack11ll1ll11_opy_():
  global CONFIG
  if bstack11ll1_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧध") in CONFIG and not bool(CONFIG[bstack11ll1_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨन")]):
    del CONFIG[bstack11ll1_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩऩ")]
    return
  if not bstack11ll1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪप") in CONFIG:
    CONFIG[bstack11ll1_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫफ")] = bstack11ll1_opy_ (u"ࠪࠧࠩࢁࡂࡖࡋࡏࡈࡤࡔࡕࡎࡄࡈࡖࢂ࠭ब")
  if bstack11ll1_opy_ (u"ࠫࠩࢁࡄࡂࡖࡈࡣ࡙ࡏࡍࡆࡿࠪभ") in CONFIG[bstack11ll1_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧम")]:
    bstack11l1l1llll_opy_()
    os.environ[bstack11ll1_opy_ (u"࠭ࡂࡔࡖࡄࡇࡐࡥࡃࡐࡏࡅࡍࡓࡋࡄࡠࡄࡘࡍࡑࡊ࡟ࡊࡆࠪय")] = CONFIG[bstack11ll1_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩर")]
  if not bstack11ll1_opy_ (u"ࠨࠦࡾࡆ࡚ࡏࡌࡅࡡࡑ࡙ࡒࡈࡅࡓࡿࠪऱ") in CONFIG[bstack11ll1_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫल")]:
    return
  bstack1l1111l11l_opy_ = bstack11ll1_opy_ (u"ࠪࠫळ")
  bstack11l1l11111_opy_ = bstack1ll1ll11l_opy_()
  if bstack11l1l11111_opy_ != -1:
    bstack1l1111l11l_opy_ = bstack11ll1_opy_ (u"ࠫࡈࡏࠠࠨऴ") + str(bstack11l1l11111_opy_)
  if bstack1l1111l11l_opy_ == bstack11ll1_opy_ (u"ࠬ࠭व"):
    bstack111l111ll_opy_ = bstack1lllll1ll1_opy_(CONFIG[bstack11ll1_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡓࡧ࡭ࡦࠩश")])
    if bstack111l111ll_opy_ != -1:
      bstack1l1111l11l_opy_ = str(bstack111l111ll_opy_)
  if bstack1l1111l11l_opy_:
    bstack1l1ll111ll_opy_(bstack1l1111l11l_opy_)
    os.environ[bstack11ll1_opy_ (u"ࠧࡃࡕࡗࡅࡈࡑ࡟ࡄࡑࡐࡆࡎࡔࡅࡅࡡࡅ࡙ࡎࡒࡄࡠࡋࡇࠫष")] = CONFIG[bstack11ll1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪस")]
def bstack1l1l111lll_opy_(bstack1l11l1111l_opy_, bstack1l111l1ll1_opy_, path):
  bstack11ll1111l_opy_ = {
    bstack11ll1_opy_ (u"ࠩ࡬ࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭ह"): bstack1l111l1ll1_opy_
  }
  if os.path.exists(path):
    bstack1lll11111l_opy_ = json.load(open(path, bstack11ll1_opy_ (u"ࠪࡶࡧ࠭ऺ")))
  else:
    bstack1lll11111l_opy_ = {}
  bstack1lll11111l_opy_[bstack1l11l1111l_opy_] = bstack11ll1111l_opy_
  with open(path, bstack11ll1_opy_ (u"ࠦࡼ࠱ࠢऻ")) as outfile:
    json.dump(bstack1lll11111l_opy_, outfile)
def bstack1lllll1ll1_opy_(bstack1l11l1111l_opy_):
  bstack1l11l1111l_opy_ = str(bstack1l11l1111l_opy_)
  bstack11lll1lll_opy_ = os.path.join(os.path.expanduser(bstack11ll1_opy_ (u"ࠬࢄ़ࠧ")), bstack11ll1_opy_ (u"࠭࠮ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠭ऽ"))
  try:
    if not os.path.exists(bstack11lll1lll_opy_):
      os.makedirs(bstack11lll1lll_opy_)
    file_path = os.path.join(os.path.expanduser(bstack11ll1_opy_ (u"ࠧࡿࠩा")), bstack11ll1_opy_ (u"ࠨ࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࠨि"), bstack11ll1_opy_ (u"ࠩ࠱ࡦࡺ࡯࡬ࡥ࠯ࡱࡥࡲ࡫࠭ࡤࡣࡦ࡬ࡪ࠴ࡪࡴࡱࡱࠫी"))
    if not os.path.isfile(file_path):
      with open(file_path, bstack11ll1_opy_ (u"ࠪࡻࠬु")):
        pass
      with open(file_path, bstack11ll1_opy_ (u"ࠦࡼ࠱ࠢू")) as outfile:
        json.dump({}, outfile)
    with open(file_path, bstack11ll1_opy_ (u"ࠬࡸࠧृ")) as bstack1l1l11l1_opy_:
      bstack11l111l11l_opy_ = json.load(bstack1l1l11l1_opy_)
    if bstack1l11l1111l_opy_ in bstack11l111l11l_opy_:
      bstack1111ll1ll_opy_ = bstack11l111l11l_opy_[bstack1l11l1111l_opy_][bstack11ll1_opy_ (u"࠭ࡩࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪॄ")]
      bstack1ll1l1l1l_opy_ = int(bstack1111ll1ll_opy_) + 1
      bstack1l1l111lll_opy_(bstack1l11l1111l_opy_, bstack1ll1l1l1l_opy_, file_path)
      return bstack1ll1l1l1l_opy_
    else:
      bstack1l1l111lll_opy_(bstack1l11l1111l_opy_, 1, file_path)
      return 1
  except Exception as e:
    logger.warning(bstack1ll111l11_opy_.format(str(e)))
    return -1
def bstack1lll111111_opy_(config):
  if not config[bstack11ll1_opy_ (u"ࠧࡶࡵࡨࡶࡓࡧ࡭ࡦࠩॅ")] or not config[bstack11ll1_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡌࡧࡼࠫॆ")]:
    return True
  else:
    return False
def bstack111l11l1_opy_(config, index=0):
  global bstack1l11l1l1ll_opy_
  bstack1ll11lllll_opy_ = {}
  caps = bstack1llll11111_opy_ + bstack1l1111l1l_opy_
  if config.get(bstack11ll1_opy_ (u"ࠩࡷࡹࡷࡨ࡯ࡔࡥࡤࡰࡪ࠭े"), False):
    bstack1ll11lllll_opy_[bstack11ll1_opy_ (u"ࠪࡸࡺࡸࡢࡰࡵࡦࡥࡱ࡫ࠧै")] = True
    bstack1ll11lllll_opy_[bstack11ll1_opy_ (u"ࠫࡹࡻࡲࡣࡱࡖࡧࡦࡲࡥࡐࡲࡷ࡭ࡴࡴࡳࠨॉ")] = config.get(bstack11ll1_opy_ (u"ࠬࡺࡵࡳࡤࡲࡗࡨࡧ࡬ࡦࡑࡳࡸ࡮ࡵ࡮ࡴࠩॊ"), {})
  if bstack1l11l1l1ll_opy_:
    caps += bstack1lllllll11_opy_
  for key in config:
    if key in caps + [bstack11ll1_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩो")]:
      continue
    bstack1ll11lllll_opy_[key] = config[key]
  if bstack11ll1_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪौ") in config:
    for bstack111ll1l1_opy_ in config[bstack11ll1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶ्ࠫ")][index]:
      if bstack111ll1l1_opy_ in caps:
        continue
      bstack1ll11lllll_opy_[bstack111ll1l1_opy_] = config[bstack11ll1_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬॎ")][index][bstack111ll1l1_opy_]
  bstack1ll11lllll_opy_[bstack11ll1_opy_ (u"ࠪ࡬ࡴࡹࡴࡏࡣࡰࡩࠬॏ")] = socket.gethostname()
  if bstack11ll1_opy_ (u"ࠫࡻ࡫ࡲࡴ࡫ࡲࡲࠬॐ") in bstack1ll11lllll_opy_:
    del (bstack1ll11lllll_opy_[bstack11ll1_opy_ (u"ࠬࡼࡥࡳࡵ࡬ࡳࡳ࠭॑")])
  return bstack1ll11lllll_opy_
def bstack1l1l1llll1_opy_(config):
  global bstack1l11l1l1ll_opy_
  bstack11lll1l1l_opy_ = {}
  caps = bstack1l1111l1l_opy_
  if bstack1l11l1l1ll_opy_:
    caps += bstack1lllllll11_opy_
  for key in caps:
    if key in config:
      bstack11lll1l1l_opy_[key] = config[key]
  return bstack11lll1l1l_opy_
def bstack111ll1llll_opy_(bstack1ll11lllll_opy_, bstack11lll1l1l_opy_):
  bstack1llll111ll_opy_ = {}
  for key in bstack1ll11lllll_opy_.keys():
    if key in bstack11l111ll1l_opy_:
      bstack1llll111ll_opy_[bstack11l111ll1l_opy_[key]] = bstack1ll11lllll_opy_[key]
    else:
      bstack1llll111ll_opy_[key] = bstack1ll11lllll_opy_[key]
  for key in bstack11lll1l1l_opy_:
    if key in bstack11l111ll1l_opy_:
      bstack1llll111ll_opy_[bstack11l111ll1l_opy_[key]] = bstack11lll1l1l_opy_[key]
    else:
      bstack1llll111ll_opy_[key] = bstack11lll1l1l_opy_[key]
  return bstack1llll111ll_opy_
def bstack11l1llll1l_opy_(config, index=0):
  global bstack1l11l1l1ll_opy_
  caps = {}
  config = copy.deepcopy(config)
  bstack1ll1ll111_opy_ = bstack1ll1lllll1_opy_(bstack11111111_opy_, config, logger)
  bstack11lll1l1l_opy_ = bstack1l1l1llll1_opy_(config)
  bstack11ll11llll_opy_ = bstack1l1111l1l_opy_
  bstack11ll11llll_opy_ += bstack1l11l1111_opy_
  bstack11lll1l1l_opy_ = update(bstack11lll1l1l_opy_, bstack1ll1ll111_opy_)
  if bstack1l11l1l1ll_opy_:
    bstack11ll11llll_opy_ += bstack1lllllll11_opy_
  if bstack11ll1_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴ॒ࠩ") in config:
    if bstack11ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡏࡣࡰࡩࠬ॓") in config[bstack11ll1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫ॔")][index]:
      caps[bstack11ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡑࡥࡲ࡫ࠧॕ")] = config[bstack11ll1_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ॖ")][index][bstack11ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡓࡧ࡭ࡦࠩॗ")]
    if bstack11ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡜ࡥࡳࡵ࡬ࡳࡳ࠭क़") in config[bstack11ll1_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩख़")][index]:
      caps[bstack11ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡗࡧࡵࡷ࡮ࡵ࡮ࠨग़")] = str(config[bstack11ll1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫज़")][index][bstack11ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴ࡙ࡩࡷࡹࡩࡰࡰࠪड़")])
    bstack111ll1ll_opy_ = bstack1ll1lllll1_opy_(bstack11111111_opy_, config[bstack11ll1_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ढ़")][index], logger)
    bstack11ll11llll_opy_ += list(bstack111ll1ll_opy_.keys())
    for bstack1l11llll11_opy_ in bstack11ll11llll_opy_:
      if bstack1l11llll11_opy_ in config[bstack11ll1_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧफ़")][index]:
        if bstack1l11llll11_opy_ == bstack11ll1_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡖࡦࡴࡶ࡭ࡴࡴࠧय़"):
          try:
            bstack111ll1ll_opy_[bstack1l11llll11_opy_] = str(config[bstack11ll1_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩॠ")][index][bstack1l11llll11_opy_] * 1.0)
          except:
            bstack111ll1ll_opy_[bstack1l11llll11_opy_] = str(config[bstack11ll1_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪॡ")][index][bstack1l11llll11_opy_])
        else:
          bstack111ll1ll_opy_[bstack1l11llll11_opy_] = config[bstack11ll1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫॢ")][index][bstack1l11llll11_opy_]
        del (config[bstack11ll1_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬॣ")][index][bstack1l11llll11_opy_])
    bstack11lll1l1l_opy_ = update(bstack11lll1l1l_opy_, bstack111ll1ll_opy_)
  bstack1ll11lllll_opy_ = bstack111l11l1_opy_(config, index)
  for bstack1l11l11l1_opy_ in bstack1l1111l1l_opy_ + list(bstack1ll1ll111_opy_.keys()):
    if bstack1l11l11l1_opy_ in bstack1ll11lllll_opy_:
      bstack11lll1l1l_opy_[bstack1l11l11l1_opy_] = bstack1ll11lllll_opy_[bstack1l11l11l1_opy_]
      del (bstack1ll11lllll_opy_[bstack1l11l11l1_opy_])
  if bstack11lll11lll_opy_(config):
    bstack1ll11lllll_opy_[bstack11ll1_opy_ (u"ࠪࡹࡸ࡫ࡗ࠴ࡅࠪ।")] = True
    caps.update(bstack11lll1l1l_opy_)
    caps[bstack11ll1_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮࠾ࡴࡶࡴࡪࡱࡱࡷࠬ॥")] = bstack1ll11lllll_opy_
  else:
    bstack1ll11lllll_opy_[bstack11ll1_opy_ (u"ࠬࡻࡳࡦ࡙࠶ࡇࠬ०")] = False
    caps.update(bstack111ll1llll_opy_(bstack1ll11lllll_opy_, bstack11lll1l1l_opy_))
    if bstack11ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡎࡢ࡯ࡨࠫ१") in caps:
      caps[bstack11ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࠨ२")] = caps[bstack11ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡐࡤࡱࡪ࠭३")]
      del (caps[bstack11ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡑࡥࡲ࡫ࠧ४")])
    if bstack11ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵ࡚ࡪࡸࡳࡪࡱࡱࠫ५") in caps:
      caps[bstack11ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡤࡼࡥࡳࡵ࡬ࡳࡳ࠭६")] = caps[bstack11ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡜ࡥࡳࡵ࡬ࡳࡳ࠭७")]
      del (caps[bstack11ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡖࡦࡴࡶ࡭ࡴࡴࠧ८")])
  return caps
def bstack1l1l11l11_opy_():
  global bstack1l1ll11ll1_opy_
  global CONFIG
  if bstack1ll1ll1l11_opy_() <= version.parse(bstack11ll1_opy_ (u"ࠧ࠴࠰࠴࠷࠳࠶ࠧ९")):
    if bstack1l1ll11ll1_opy_ != bstack11ll1_opy_ (u"ࠨࠩ॰"):
      return bstack11ll1_opy_ (u"ࠤ࡫ࡸࡹࡶ࠺࠰࠱ࠥॱ") + bstack1l1ll11ll1_opy_ + bstack11ll1_opy_ (u"ࠥ࠾࠽࠶࠯ࡸࡦ࠲࡬ࡺࡨࠢॲ")
    return bstack111l1ll11_opy_
  if bstack1l1ll11ll1_opy_ != bstack11ll1_opy_ (u"ࠫࠬॳ"):
    return bstack11ll1_opy_ (u"ࠧ࡮ࡴࡵࡲࡶ࠾࠴࠵ࠢॴ") + bstack1l1ll11ll1_opy_ + bstack11ll1_opy_ (u"ࠨ࠯ࡸࡦ࠲࡬ࡺࡨࠢॵ")
  return bstack11l1l11lll_opy_
def bstack1lll1l1l1l_opy_(options):
  return hasattr(options, bstack11ll1_opy_ (u"ࠧࡴࡧࡷࡣࡨࡧࡰࡢࡤ࡬ࡰ࡮ࡺࡹࠨॶ"))
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
def bstack1l11l1l1l1_opy_(options, bstack111ll1lll1_opy_):
  for bstack1ll1111l1_opy_ in bstack111ll1lll1_opy_:
    if bstack1ll1111l1_opy_ in [bstack11ll1_opy_ (u"ࠨࡣࡵ࡫ࡸ࠭ॷ"), bstack11ll1_opy_ (u"ࠩࡨࡼࡹ࡫࡮ࡴ࡫ࡲࡲࡸ࠭ॸ")]:
      continue
    if bstack1ll1111l1_opy_ in options._experimental_options:
      options._experimental_options[bstack1ll1111l1_opy_] = update(options._experimental_options[bstack1ll1111l1_opy_],
                                                         bstack111ll1lll1_opy_[bstack1ll1111l1_opy_])
    else:
      options.add_experimental_option(bstack1ll1111l1_opy_, bstack111ll1lll1_opy_[bstack1ll1111l1_opy_])
  if bstack11ll1_opy_ (u"ࠪࡥࡷ࡭ࡳࠨॹ") in bstack111ll1lll1_opy_:
    for arg in bstack111ll1lll1_opy_[bstack11ll1_opy_ (u"ࠫࡦࡸࡧࡴࠩॺ")]:
      options.add_argument(arg)
    del (bstack111ll1lll1_opy_[bstack11ll1_opy_ (u"ࠬࡧࡲࡨࡵࠪॻ")])
  if bstack11ll1_opy_ (u"࠭ࡥࡹࡶࡨࡲࡸ࡯࡯࡯ࡵࠪॼ") in bstack111ll1lll1_opy_:
    for ext in bstack111ll1lll1_opy_[bstack11ll1_opy_ (u"ࠧࡦࡺࡷࡩࡳࡹࡩࡰࡰࡶࠫॽ")]:
      try:
        options.add_extension(ext)
      except OSError:
        options.add_encoded_extension(ext)
    del (bstack111ll1lll1_opy_[bstack11ll1_opy_ (u"ࠨࡧࡻࡸࡪࡴࡳࡪࡱࡱࡷࠬॾ")])
def bstack1lllll11l_opy_(options, bstack11l1l1lll1_opy_):
  if bstack11ll1_opy_ (u"ࠩࡳࡶࡪ࡬ࡳࠨॿ") in bstack11l1l1lll1_opy_:
    for bstack1l1l111ll_opy_ in bstack11l1l1lll1_opy_[bstack11ll1_opy_ (u"ࠪࡴࡷ࡫ࡦࡴࠩঀ")]:
      if bstack1l1l111ll_opy_ in options._preferences:
        options._preferences[bstack1l1l111ll_opy_] = update(options._preferences[bstack1l1l111ll_opy_], bstack11l1l1lll1_opy_[bstack11ll1_opy_ (u"ࠫࡵࡸࡥࡧࡵࠪঁ")][bstack1l1l111ll_opy_])
      else:
        options.set_preference(bstack1l1l111ll_opy_, bstack11l1l1lll1_opy_[bstack11ll1_opy_ (u"ࠬࡶࡲࡦࡨࡶࠫং")][bstack1l1l111ll_opy_])
  if bstack11ll1_opy_ (u"࠭ࡡࡳࡩࡶࠫঃ") in bstack11l1l1lll1_opy_:
    for arg in bstack11l1l1lll1_opy_[bstack11ll1_opy_ (u"ࠧࡢࡴࡪࡷࠬ঄")]:
      options.add_argument(arg)
def bstack11ll1l1l1l_opy_(options, bstack11lll11ll1_opy_):
  if bstack11ll1_opy_ (u"ࠨࡹࡨࡦࡻ࡯ࡥࡸࠩঅ") in bstack11lll11ll1_opy_:
    options.use_webview(bool(bstack11lll11ll1_opy_[bstack11ll1_opy_ (u"ࠩࡺࡩࡧࡼࡩࡦࡹࠪআ")]))
  bstack1l11l1l1l1_opy_(options, bstack11lll11ll1_opy_)
def bstack11l1111111_opy_(options, bstack1l111l1l1l_opy_):
  for bstack1l1l1l1l1_opy_ in bstack1l111l1l1l_opy_:
    if bstack1l1l1l1l1_opy_ in [bstack11ll1_opy_ (u"ࠪࡸࡪࡩࡨ࡯ࡱ࡯ࡳ࡬ࡿࡐࡳࡧࡹ࡭ࡪࡽࠧই"), bstack11ll1_opy_ (u"ࠫࡦࡸࡧࡴࠩঈ")]:
      continue
    options.set_capability(bstack1l1l1l1l1_opy_, bstack1l111l1l1l_opy_[bstack1l1l1l1l1_opy_])
  if bstack11ll1_opy_ (u"ࠬࡧࡲࡨࡵࠪউ") in bstack1l111l1l1l_opy_:
    for arg in bstack1l111l1l1l_opy_[bstack11ll1_opy_ (u"࠭ࡡࡳࡩࡶࠫঊ")]:
      options.add_argument(arg)
  if bstack11ll1_opy_ (u"ࠧࡵࡧࡦ࡬ࡳࡵ࡬ࡰࡩࡼࡔࡷ࡫ࡶࡪࡧࡺࠫঋ") in bstack1l111l1l1l_opy_:
    options.bstack11llll11ll_opy_(bool(bstack1l111l1l1l_opy_[bstack11ll1_opy_ (u"ࠨࡶࡨࡧ࡭ࡴ࡯࡭ࡱࡪࡽࡕࡸࡥࡷ࡫ࡨࡻࠬঌ")]))
def bstack111ll11l_opy_(options, bstack1l11llll1_opy_):
  for bstack1ll1llll1_opy_ in bstack1l11llll1_opy_:
    if bstack1ll1llll1_opy_ in [bstack11ll1_opy_ (u"ࠩࡤࡨࡩ࡯ࡴࡪࡱࡱࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭঍"), bstack11ll1_opy_ (u"ࠪࡥࡷ࡭ࡳࠨ঎")]:
      continue
    options._options[bstack1ll1llll1_opy_] = bstack1l11llll1_opy_[bstack1ll1llll1_opy_]
  if bstack11ll1_opy_ (u"ࠫࡦࡪࡤࡪࡶ࡬ࡳࡳࡧ࡬ࡐࡲࡷ࡭ࡴࡴࡳࠨএ") in bstack1l11llll1_opy_:
    for bstack1l11l11111_opy_ in bstack1l11llll1_opy_[bstack11ll1_opy_ (u"ࠬࡧࡤࡥ࡫ࡷ࡭ࡴࡴࡡ࡭ࡑࡳࡸ࡮ࡵ࡮ࡴࠩঐ")]:
      options.bstack11l1l1l111_opy_(
        bstack1l11l11111_opy_, bstack1l11llll1_opy_[bstack11ll1_opy_ (u"࠭ࡡࡥࡦ࡬ࡸ࡮ࡵ࡮ࡢ࡮ࡒࡴࡹ࡯࡯࡯ࡵࠪ঑")][bstack1l11l11111_opy_])
  if bstack11ll1_opy_ (u"ࠧࡢࡴࡪࡷࠬ঒") in bstack1l11llll1_opy_:
    for arg in bstack1l11llll1_opy_[bstack11ll1_opy_ (u"ࠨࡣࡵ࡫ࡸ࠭ও")]:
      options.add_argument(arg)
def bstack11l1l111_opy_(options, caps):
  if not hasattr(options, bstack11ll1_opy_ (u"ࠩࡎࡉ࡞࠭ঔ")):
    return
  if options.KEY == bstack11ll1_opy_ (u"ࠪ࡫ࡴࡵࡧ࠻ࡥ࡫ࡶࡴࡳࡥࡐࡲࡷ࡭ࡴࡴࡳࠨক"):
    options = bstack1l1ll11l1l_opy_.bstack1l1l111l11_opy_(bstack1l1111lll_opy_=options, config=CONFIG)
  if options.KEY == bstack11ll1_opy_ (u"ࠫ࡬ࡵ࡯ࡨ࠼ࡦ࡬ࡷࡵ࡭ࡦࡑࡳࡸ࡮ࡵ࡮ࡴࠩখ") and options.KEY in caps:
    bstack1l11l1l1l1_opy_(options, caps[bstack11ll1_opy_ (u"ࠬ࡭࡯ࡰࡩ࠽ࡧ࡭ࡸ࡯࡮ࡧࡒࡴࡹ࡯࡯࡯ࡵࠪগ")])
  elif options.KEY == bstack11ll1_opy_ (u"࠭࡭ࡰࡼ࠽ࡪ࡮ࡸࡥࡧࡱࡻࡓࡵࡺࡩࡰࡰࡶࠫঘ") and options.KEY in caps:
    bstack1lllll11l_opy_(options, caps[bstack11ll1_opy_ (u"ࠧ࡮ࡱࡽ࠾࡫࡯ࡲࡦࡨࡲࡼࡔࡶࡴࡪࡱࡱࡷࠬঙ")])
  elif options.KEY == bstack11ll1_opy_ (u"ࠨࡵࡤࡪࡦࡸࡩ࠯ࡱࡳࡸ࡮ࡵ࡮ࡴࠩচ") and options.KEY in caps:
    bstack11l1111111_opy_(options, caps[bstack11ll1_opy_ (u"ࠩࡶࡥ࡫ࡧࡲࡪ࠰ࡲࡴࡹ࡯࡯࡯ࡵࠪছ")])
  elif options.KEY == bstack11ll1_opy_ (u"ࠪࡱࡸࡀࡥࡥࡩࡨࡓࡵࡺࡩࡰࡰࡶࠫজ") and options.KEY in caps:
    bstack11ll1l1l1l_opy_(options, caps[bstack11ll1_opy_ (u"ࠫࡲࡹ࠺ࡦࡦࡪࡩࡔࡶࡴࡪࡱࡱࡷࠬঝ")])
  elif options.KEY == bstack11ll1_opy_ (u"ࠬࡹࡥ࠻࡫ࡨࡓࡵࡺࡩࡰࡰࡶࠫঞ") and options.KEY in caps:
    bstack111ll11l_opy_(options, caps[bstack11ll1_opy_ (u"࠭ࡳࡦ࠼࡬ࡩࡔࡶࡴࡪࡱࡱࡷࠬট")])
def bstack111lll1ll_opy_(caps):
  global bstack1l11l1l1ll_opy_
  if isinstance(os.environ.get(bstack11ll1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡉࡔࡡࡄࡔࡕࡥࡁࡖࡖࡒࡑࡆ࡚ࡅࠨঠ")), str):
    bstack1l11l1l1ll_opy_ = eval(os.getenv(bstack11ll1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡊࡕࡢࡅࡕࡖ࡟ࡂࡗࡗࡓࡒࡇࡔࡆࠩড")))
  if bstack1l11l1l1ll_opy_:
    if bstack1l11l11l1l_opy_() < version.parse(bstack11ll1_opy_ (u"ࠩ࠵࠲࠸࠴࠰ࠨঢ")):
      return None
    else:
      from appium.options.common.base import AppiumOptions
      options = AppiumOptions().load_capabilities(caps)
      return options
  else:
    browser = bstack11ll1_opy_ (u"ࠪࡧ࡭ࡸ࡯࡮ࡧࠪণ")
    if bstack11ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡓࡧ࡭ࡦࠩত") in caps:
      browser = caps[bstack11ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡔࡡ࡮ࡧࠪথ")]
    elif bstack11ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࠧদ") in caps:
      browser = caps[bstack11ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࠨধ")]
    browser = str(browser).lower()
    if browser == bstack11ll1_opy_ (u"ࠨ࡫ࡳ࡬ࡴࡴࡥࠨন") or browser == bstack11ll1_opy_ (u"ࠩ࡬ࡴࡦࡪࠧ঩"):
      browser = bstack11ll1_opy_ (u"ࠪࡷࡦ࡬ࡡࡳ࡫ࠪপ")
    if browser == bstack11ll1_opy_ (u"ࠫࡸࡧ࡭ࡴࡷࡱ࡫ࠬফ"):
      browser = bstack11ll1_opy_ (u"ࠬࡩࡨࡳࡱࡰࡩࠬব")
    if browser not in [bstack11ll1_opy_ (u"࠭ࡣࡩࡴࡲࡱࡪ࠭ভ"), bstack11ll1_opy_ (u"ࠧࡦࡦࡪࡩࠬম"), bstack11ll1_opy_ (u"ࠨ࡫ࡨࠫয"), bstack11ll1_opy_ (u"ࠩࡶࡥ࡫ࡧࡲࡪࠩর"), bstack11ll1_opy_ (u"ࠪࡪ࡮ࡸࡥࡧࡱࡻࠫ঱")]:
      return None
    try:
      package = bstack11ll1_opy_ (u"ࠫࡸ࡫࡬ࡦࡰ࡬ࡹࡲ࠴ࡷࡦࡤࡧࡶ࡮ࡼࡥࡳ࠰ࡾࢁ࠳ࡵࡰࡵ࡫ࡲࡲࡸ࠭ল").format(browser)
      name = bstack11ll1_opy_ (u"ࠬࡕࡰࡵ࡫ࡲࡲࡸ࠭঳")
      browser_options = getattr(__import__(package, fromlist=[name]), name)
      options = browser_options()
      if not bstack1lll1l1l1l_opy_(options):
        return None
      for bstack1l11l11l1_opy_ in caps.keys():
        options.set_capability(bstack1l11l11l1_opy_, caps[bstack1l11l11l1_opy_])
      bstack11l1l111_opy_(options, caps)
      return options
    except Exception as e:
      logger.debug(str(e))
      return None
def bstack11lll1l1_opy_(options, bstack1l111ll11_opy_):
  if not bstack1lll1l1l1l_opy_(options):
    return
  for bstack1l11l11l1_opy_ in bstack1l111ll11_opy_.keys():
    if bstack1l11l11l1_opy_ in bstack1l11l1111_opy_:
      continue
    if bstack1l11l11l1_opy_ in options._caps and type(options._caps[bstack1l11l11l1_opy_]) in [dict, list]:
      options._caps[bstack1l11l11l1_opy_] = update(options._caps[bstack1l11l11l1_opy_], bstack1l111ll11_opy_[bstack1l11l11l1_opy_])
    else:
      options.set_capability(bstack1l11l11l1_opy_, bstack1l111ll11_opy_[bstack1l11l11l1_opy_])
  bstack11l1l111_opy_(options, bstack1l111ll11_opy_)
  if bstack11ll1_opy_ (u"࠭࡭ࡰࡼ࠽ࡨࡪࡨࡵࡨࡩࡨࡶࡆࡪࡤࡳࡧࡶࡷࠬ঴") in options._caps:
    if options._caps[bstack11ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡏࡣࡰࡩࠬ঵")] and options._caps[bstack11ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡐࡤࡱࡪ࠭শ")].lower() != bstack11ll1_opy_ (u"ࠩࡩ࡭ࡷ࡫ࡦࡰࡺࠪষ"):
      del options._caps[bstack11ll1_opy_ (u"ࠪࡱࡴࢀ࠺ࡥࡧࡥࡹ࡬࡭ࡥࡳࡃࡧࡨࡷ࡫ࡳࡴࠩস")]
def bstack1l11l1lll_opy_(proxy_config):
  if bstack11ll1_opy_ (u"ࠫ࡭ࡺࡴࡱࡵࡓࡶࡴࡾࡹࠨহ") in proxy_config:
    proxy_config[bstack11ll1_opy_ (u"ࠬࡹࡳ࡭ࡒࡵࡳࡽࡿࠧ঺")] = proxy_config[bstack11ll1_opy_ (u"࠭ࡨࡵࡶࡳࡷࡕࡸ࡯ࡹࡻࠪ঻")]
    del (proxy_config[bstack11ll1_opy_ (u"ࠧࡩࡶࡷࡴࡸࡖࡲࡰࡺࡼ়ࠫ")])
  if bstack11ll1_opy_ (u"ࠨࡲࡵࡳࡽࡿࡔࡺࡲࡨࠫঽ") in proxy_config and proxy_config[bstack11ll1_opy_ (u"ࠩࡳࡶࡴࡾࡹࡕࡻࡳࡩࠬা")].lower() != bstack11ll1_opy_ (u"ࠪࡨ࡮ࡸࡥࡤࡶࠪি"):
    proxy_config[bstack11ll1_opy_ (u"ࠫࡵࡸ࡯ࡹࡻࡗࡽࡵ࡫ࠧী")] = bstack11ll1_opy_ (u"ࠬࡳࡡ࡯ࡷࡤࡰࠬু")
  if bstack11ll1_opy_ (u"࠭ࡰࡳࡱࡻࡽࡆࡻࡴࡰࡥࡲࡲ࡫࡯ࡧࡖࡴ࡯ࠫূ") in proxy_config:
    proxy_config[bstack11ll1_opy_ (u"ࠧࡱࡴࡲࡼࡾ࡚ࡹࡱࡧࠪৃ")] = bstack11ll1_opy_ (u"ࠨࡲࡤࡧࠬৄ")
  return proxy_config
def bstack11l1l11ll1_opy_(config, proxy):
  from selenium.webdriver.common.proxy import Proxy
  if not bstack11ll1_opy_ (u"ࠩࡳࡶࡴࡾࡹࠨ৅") in config:
    return proxy
  config[bstack11ll1_opy_ (u"ࠪࡴࡷࡵࡸࡺࠩ৆")] = bstack1l11l1lll_opy_(config[bstack11ll1_opy_ (u"ࠫࡵࡸ࡯ࡹࡻࠪে")])
  if proxy == None:
    proxy = Proxy(config[bstack11ll1_opy_ (u"ࠬࡶࡲࡰࡺࡼࠫৈ")])
  return proxy
def bstack11l1ll1ll_opy_(self):
  global CONFIG
  global bstack1ll1l11l1_opy_
  try:
    proxy = bstack11l1ll11l_opy_(CONFIG)
    if proxy:
      if proxy.endswith(bstack11ll1_opy_ (u"࠭࠮ࡱࡣࡦࠫ৉")):
        proxies = bstack111lllll1l_opy_(proxy, bstack1l1l11l11_opy_())
        if len(proxies) > 0:
          protocol, bstack11l11lll_opy_ = proxies.popitem()
          if bstack11ll1_opy_ (u"ࠢ࠻࠱࠲ࠦ৊") in bstack11l11lll_opy_:
            return bstack11l11lll_opy_
          else:
            return bstack11ll1_opy_ (u"ࠣࡪࡷࡸࡵࡀ࠯࠰ࠤো") + bstack11l11lll_opy_
      else:
        return proxy
  except Exception as e:
    logger.error(bstack11ll1_opy_ (u"ࠤࡈࡶࡷࡵࡲࠡ࡫ࡱࠤࡸ࡫ࡴࡵ࡫ࡱ࡫ࠥࡶࡲࡰࡺࡼࠤࡺࡸ࡬ࠡ࠼ࠣࡿࢂࠨৌ").format(str(e)))
  return bstack1ll1l11l1_opy_(self)
def bstack1111l111_opy_():
  global CONFIG
  return bstack1l1ll11lll_opy_(CONFIG) and bstack1l11lll111_opy_() and bstack1ll1ll1l11_opy_() >= version.parse(bstack1llll1ll11_opy_)
def bstack1ll111ll1l_opy_():
  global CONFIG
  return (bstack11ll1_opy_ (u"ࠪ࡬ࡹࡺࡰࡑࡴࡲࡼࡾ্࠭") in CONFIG or bstack11ll1_opy_ (u"ࠫ࡭ࡺࡴࡱࡵࡓࡶࡴࡾࡹࠨৎ") in CONFIG) and bstack11l1llll_opy_()
def bstack1l1l1l111_opy_(config):
  bstack1l111ll1ll_opy_ = {}
  if bstack11ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࡑࡳࡸ࡮ࡵ࡮ࡴࠩ৏") in config:
    bstack1l111ll1ll_opy_ = config[bstack11ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࡒࡴࡹ࡯࡯࡯ࡵࠪ৐")]
  if bstack11ll1_opy_ (u"ࠧ࡭ࡱࡦࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭৑") in config:
    bstack1l111ll1ll_opy_ = config[bstack11ll1_opy_ (u"ࠨ࡮ࡲࡧࡦࡲࡏࡱࡶ࡬ࡳࡳࡹࠧ৒")]
  proxy = bstack11l1ll11l_opy_(config)
  if proxy:
    if proxy.endswith(bstack11ll1_opy_ (u"ࠩ࠱ࡴࡦࡩࠧ৓")) and os.path.isfile(proxy):
      bstack1l111ll1ll_opy_[bstack11ll1_opy_ (u"ࠪ࠱ࡵࡧࡣ࠮ࡨ࡬ࡰࡪ࠭৔")] = proxy
    else:
      parsed_url = None
      if proxy.endswith(bstack11ll1_opy_ (u"ࠫ࠳ࡶࡡࡤࠩ৕")):
        proxies = bstack1lllll1111_opy_(config, bstack1l1l11l11_opy_())
        if len(proxies) > 0:
          protocol, bstack11l11lll_opy_ = proxies.popitem()
          if bstack11ll1_opy_ (u"ࠧࡀ࠯࠰ࠤ৖") in bstack11l11lll_opy_:
            parsed_url = urlparse(bstack11l11lll_opy_)
          else:
            parsed_url = urlparse(protocol + bstack11ll1_opy_ (u"ࠨ࠺࠰࠱ࠥৗ") + bstack11l11lll_opy_)
      else:
        parsed_url = urlparse(proxy)
      if parsed_url and parsed_url.hostname: bstack1l111ll1ll_opy_[bstack11ll1_opy_ (u"ࠧࡱࡴࡲࡼࡾࡎ࡯ࡴࡶࠪ৘")] = str(parsed_url.hostname)
      if parsed_url and parsed_url.port: bstack1l111ll1ll_opy_[bstack11ll1_opy_ (u"ࠨࡲࡵࡳࡽࡿࡐࡰࡴࡷࠫ৙")] = str(parsed_url.port)
      if parsed_url and parsed_url.username: bstack1l111ll1ll_opy_[bstack11ll1_opy_ (u"ࠩࡳࡶࡴࡾࡹࡖࡵࡨࡶࠬ৚")] = str(parsed_url.username)
      if parsed_url and parsed_url.password: bstack1l111ll1ll_opy_[bstack11ll1_opy_ (u"ࠪࡴࡷࡵࡸࡺࡒࡤࡷࡸ࠭৛")] = str(parsed_url.password)
  return bstack1l111ll1ll_opy_
def bstack111ll1ll11_opy_(config):
  if bstack11ll1_opy_ (u"ࠫࡹ࡫ࡳࡵࡅࡲࡲࡹ࡫ࡸࡵࡑࡳࡸ࡮ࡵ࡮ࡴࠩড়") in config:
    return config[bstack11ll1_opy_ (u"ࠬࡺࡥࡴࡶࡆࡳࡳࡺࡥࡹࡶࡒࡴࡹ࡯࡯࡯ࡵࠪঢ়")]
  return {}
def bstack1l111ll1l1_opy_(caps):
  global bstack11ll1l11l1_opy_
  if bstack11ll1_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡀ࡯ࡱࡶ࡬ࡳࡳࡹࠧ৞") in caps:
    caps[bstack11ll1_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱ࠺ࡰࡲࡷ࡭ࡴࡴࡳࠨয়")][bstack11ll1_opy_ (u"ࠨ࡮ࡲࡧࡦࡲࠧৠ")] = True
    if bstack11ll1l11l1_opy_:
      caps[bstack11ll1_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬࠼ࡲࡴࡹ࡯࡯࡯ࡵࠪৡ")][bstack11ll1_opy_ (u"ࠪࡰࡴࡩࡡ࡭ࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬৢ")] = bstack11ll1l11l1_opy_
  else:
    caps[bstack11ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡰࡴࡩࡡ࡭ࠩৣ")] = True
    if bstack11ll1l11l1_opy_:
      caps[bstack11ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡱࡵࡣࡢ࡮ࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭৤")] = bstack11ll1l11l1_opy_
@measure(event_name=EVENTS.bstack1ll111ll1_opy_, stage=STAGE.bstack11l1llll1_opy_, bstack1lll1l1l1_opy_=bstack1ll1l11111_opy_)
def bstack1llllllll1_opy_():
  global CONFIG
  if not bstack11lllll11l_opy_(CONFIG) or cli.is_enabled(CONFIG):
    return
  if bstack11ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࠪ৥") in CONFIG and bstack1111lll1_opy_(CONFIG[bstack11ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࠫ০")]):
    if (
      bstack11ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡕࡷࡥࡨࡱࡌࡰࡥࡤࡰࡔࡶࡴࡪࡱࡱࡷࠬ১") in CONFIG
      and bstack1111lll1_opy_(CONFIG[bstack11ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࡍࡱࡦࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭২")].get(bstack11ll1_opy_ (u"ࠪࡷࡰ࡯ࡰࡃ࡫ࡱࡥࡷࡿࡉ࡯࡫ࡷ࡭ࡦࡲࡩࡴࡣࡷ࡭ࡴࡴࠧ৩")))
    ):
      logger.debug(bstack11ll1_opy_ (u"ࠦࡑࡵࡣࡢ࡮ࠣࡦ࡮ࡴࡡࡳࡻࠣࡲࡴࡺࠠࡴࡶࡤࡶࡹ࡫ࡤࠡࡣࡶࠤࡸࡱࡩࡱࡄ࡬ࡲࡦࡸࡹࡊࡰ࡬ࡸ࡮ࡧ࡬ࡪࡵࡤࡸ࡮ࡵ࡮ࠡ࡫ࡶࠤࡪࡴࡡࡣ࡮ࡨࡨࠧ৪"))
      return
    bstack1l111ll1ll_opy_ = bstack1l1l1l111_opy_(CONFIG)
    bstack1l11l111_opy_(CONFIG[bstack11ll1_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷࡐ࡫ࡹࠨ৫")], bstack1l111ll1ll_opy_)
def bstack1l11l111_opy_(key, bstack1l111ll1ll_opy_):
  global bstack1l1ll1111_opy_
  logger.info(bstack1l111lllll_opy_)
  try:
    bstack1l1ll1111_opy_ = Local()
    bstack1ll1l1ll1_opy_ = {bstack11ll1_opy_ (u"࠭࡫ࡦࡻࠪ৬"): key}
    bstack1ll1l1ll1_opy_.update(bstack1l111ll1ll_opy_)
    logger.debug(bstack1l1l1l11_opy_.format(str(bstack1ll1l1ll1_opy_)).replace(key, bstack11ll1_opy_ (u"ࠧ࡜ࡔࡈࡈࡆࡉࡔࡆࡆࡠࠫ৭")))
    bstack1l1ll1111_opy_.start(**bstack1ll1l1ll1_opy_)
    if bstack1l1ll1111_opy_.isRunning():
      logger.info(bstack11l1l11l1l_opy_)
  except Exception as e:
    bstack11ll11l11_opy_(bstack11l1l1ll_opy_.format(str(e)))
def bstack1ll1ll1l1l_opy_():
  global bstack1l1ll1111_opy_
  if bstack1l1ll1111_opy_.isRunning():
    logger.info(bstack1l1l1l1l1l_opy_)
    bstack1l1ll1111_opy_.stop()
  bstack1l1ll1111_opy_ = None
def bstack111ll1ll1l_opy_(bstack11ll11ll1l_opy_=[]):
  global CONFIG
  bstack1l1111l1_opy_ = []
  bstack1l1ll1lll_opy_ = [bstack11ll1_opy_ (u"ࠨࡱࡶࠫ৮"), bstack11ll1_opy_ (u"ࠩࡲࡷ࡛࡫ࡲࡴ࡫ࡲࡲࠬ৯"), bstack11ll1_opy_ (u"ࠪࡨࡪࡼࡩࡤࡧࡑࡥࡲ࡫ࠧৰ"), bstack11ll1_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲ࡜ࡥࡳࡵ࡬ࡳࡳ࠭ৱ"), bstack11ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡔࡡ࡮ࡧࠪ৲"), bstack11ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡖࡦࡴࡶ࡭ࡴࡴࠧ৳")]
  try:
    for err in bstack11ll11ll1l_opy_:
      bstack11l111l11_opy_ = {}
      for k in bstack1l1ll1lll_opy_:
        val = CONFIG[bstack11ll1_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪ৴")][int(err[bstack11ll1_opy_ (u"ࠨ࡫ࡱࡨࡪࡾࠧ৵")])].get(k)
        if val:
          bstack11l111l11_opy_[k] = val
      if(err[bstack11ll1_opy_ (u"ࠩࡨࡶࡷࡵࡲࠨ৶")] != bstack11ll1_opy_ (u"ࠪࠫ৷")):
        bstack11l111l11_opy_[bstack11ll1_opy_ (u"ࠫࡹ࡫ࡳࡵࡵࠪ৸")] = {
          err[bstack11ll1_opy_ (u"ࠬࡴࡡ࡮ࡧࠪ৹")]: err[bstack11ll1_opy_ (u"࠭ࡥࡳࡴࡲࡶࠬ৺")]
        }
        bstack1l1111l1_opy_.append(bstack11l111l11_opy_)
  except Exception as e:
    logger.debug(bstack11ll1_opy_ (u"ࠧࡆࡴࡵࡳࡷࠦࡩ࡯ࠢࡩࡳࡷࡳࡡࡵࡶ࡬ࡲ࡬ࠦࡤࡢࡶࡤࠤ࡫ࡵࡲࠡࡧࡹࡩࡳࡺ࠺ࠡࠩ৻") + str(e))
  finally:
    return bstack1l1111l1_opy_
def bstack1l1l1llll_opy_(file_name):
  bstack1ll1lll11l_opy_ = []
  try:
    bstack1l111llll1_opy_ = os.path.join(tempfile.gettempdir(), file_name)
    if os.path.exists(bstack1l111llll1_opy_):
      with open(bstack1l111llll1_opy_) as f:
        bstack111llll1_opy_ = json.load(f)
        bstack1ll1lll11l_opy_ = bstack111llll1_opy_
      os.remove(bstack1l111llll1_opy_)
    return bstack1ll1lll11l_opy_
  except Exception as e:
    logger.debug(bstack11ll1_opy_ (u"ࠨࡇࡵࡶࡴࡸࠠࡪࡰࠣࡪ࡮ࡴࡤࡪࡰࡪࠤࡪࡸࡲࡰࡴࠣࡰ࡮ࡹࡴ࠻ࠢࠪৼ") + str(e))
    return bstack1ll1lll11l_opy_
def bstack1ll111l11l_opy_():
  try:
      from bstack_utils.constants import bstack111l1l1ll_opy_, EVENTS
      from bstack_utils.helper import bstack11l1l1l11l_opy_, get_host_info, bstack1l1l1ll1l_opy_
      from datetime import datetime
      from filelock import FileLock
      bstack11l1ll1111_opy_ = os.path.join(os.getcwd(), bstack11ll1_opy_ (u"ࠩ࡯ࡳ࡬࠭৽"), bstack11ll1_opy_ (u"ࠪ࡯ࡪࡿ࠭࡮ࡧࡷࡶ࡮ࡩࡳ࠯࡬ࡶࡳࡳ࠭৾"))
      lock = FileLock(bstack11l1ll1111_opy_+bstack11ll1_opy_ (u"ࠦ࠳ࡲ࡯ࡤ࡭ࠥ৿"))
      def bstack1lll1llll_opy_():
          try:
              with lock:
                  with open(bstack11l1ll1111_opy_, bstack11ll1_opy_ (u"ࠧࡸࠢ਀"), encoding=bstack11ll1_opy_ (u"ࠨࡵࡵࡨ࠰࠼ࠧਁ")) as file:
                      data = json.load(file)
                      config = {
                          bstack11ll1_opy_ (u"ࠢࡩࡧࡤࡨࡪࡸࡳࠣਂ"): {
                              bstack11ll1_opy_ (u"ࠣࡅࡲࡲࡹ࡫࡮ࡵ࠯ࡗࡽࡵ࡫ࠢਃ"): bstack11ll1_opy_ (u"ࠤࡤࡴࡵࡲࡩࡤࡣࡷ࡭ࡴࡴ࠯࡫ࡵࡲࡲࠧ਄"),
                          }
                      }
                      bstack11l11ll11_opy_ = datetime.utcnow()
                      bstack111lll1lll_opy_ = bstack11l11ll11_opy_.strftime(bstack11ll1_opy_ (u"ࠥࠩ࡞࠳ࠥ࡮࠯ࠨࡨ࡙ࠫࡈ࠻ࠧࡐ࠾࡙ࠪ࠮ࠦࡨ࡙࡙ࠣࡉࠢਅ"))
                      bstack1l1l11l111_opy_ = os.environ.get(bstack11ll1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡉࡗࡅࡣ࡚࡛ࡉࡅࠩਆ")) if os.environ.get(bstack11ll1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡊࡘࡆࡤ࡛ࡕࡊࡆࠪਇ")) else bstack1l1l1ll1l_opy_.get_property(bstack11ll1_opy_ (u"ࠨࡳࡥ࡭ࡕࡹࡳࡏࡤࠣਈ"))
                      payload = {
                          bstack11ll1_opy_ (u"ࠢࡦࡸࡨࡲࡹࡥࡴࡺࡲࡨࠦਉ"): bstack11ll1_opy_ (u"ࠣࡵࡧ࡯ࡤ࡫ࡶࡦࡰࡷࡷࠧਊ"),
                          bstack11ll1_opy_ (u"ࠤࡧࡥࡹࡧࠢ਋"): {
                              bstack11ll1_opy_ (u"ࠥࡸࡪࡹࡴࡩࡷࡥࡣࡺࡻࡩࡥࠤ਌"): bstack1l1l11l111_opy_,
                              bstack11ll1_opy_ (u"ࠦࡨࡸࡥࡢࡶࡨࡨࡤࡪࡡࡺࠤ਍"): bstack111lll1lll_opy_,
                              bstack11ll1_opy_ (u"ࠧ࡫ࡶࡦࡰࡷࡣࡳࡧ࡭ࡦࠤ਎"): bstack11ll1_opy_ (u"ࠨࡓࡅࡍࡉࡩࡦࡺࡵࡳࡧࡓࡩࡷ࡬࡯ࡳ࡯ࡤࡲࡨ࡫ࠢਏ"),
                              bstack11ll1_opy_ (u"ࠢࡦࡸࡨࡲࡹࡥࡪࡴࡱࡱࠦਐ"): {
                                  bstack11ll1_opy_ (u"ࠣ࡯ࡨࡥࡸࡻࡲࡦࡵࠥ਑"): data,
                                  bstack11ll1_opy_ (u"ࠤࡶࡨࡰࡘࡵ࡯ࡋࡧࠦ਒"): bstack1l1l1ll1l_opy_.get_property(bstack11ll1_opy_ (u"ࠥࡷࡩࡱࡒࡶࡰࡌࡨࠧਓ"))
                              },
                              bstack11ll1_opy_ (u"ࠦࡺࡹࡥࡳࡡࡧࡥࡹࡧࠢਔ"): bstack1l1l1ll1l_opy_.get_property(bstack11ll1_opy_ (u"ࠧࡻࡳࡦࡴࡑࡥࡲ࡫ࠢਕ")),
                              bstack11ll1_opy_ (u"ࠨࡨࡰࡵࡷࡣ࡮ࡴࡦࡰࠤਖ"): get_host_info()
                          }
                      }
                      bstack1lll11l111_opy_ = bstack1ll1l111_opy_(cli.config, [bstack11ll1_opy_ (u"ࠢࡢࡲ࡬ࡷࠧਗ"), bstack11ll1_opy_ (u"ࠣࡧࡧࡷࡎࡴࡳࡵࡴࡸࡱࡪࡴࡴࡢࡶ࡬ࡳࡳࠨਘ"), bstack11ll1_opy_ (u"ࠤࡤࡴ࡮ࠨਙ")], bstack111l1l1ll_opy_)
                      response = bstack11l1l1l11l_opy_(bstack11ll1_opy_ (u"ࠥࡔࡔ࡙ࡔࠣਚ"), bstack1lll11l111_opy_, payload, config)
                      if(response.status_code >= 200 and response.status_code < 300):
                          logger.debug(bstack11ll1_opy_ (u"ࠦࡉࡧࡴࡢࠢࡶࡩࡳࡺࠠࡴࡷࡦࡧࡪࡹࡳࡧࡷ࡯ࡰࡾࠦࡴࡰࠢࡾࢁࠥࡽࡩࡵࡪࠣࡨࡦࡺࡡࠡࡽࢀࠦਛ").format(bstack111l1l1ll_opy_, payload))
                      else:
                          logger.debug(bstack11ll1_opy_ (u"ࠧࡘࡥࡲࡷࡨࡷࡹࠦࡦࡢ࡫࡯ࡩࡩࠦࡦࡰࡴࠣࡿࢂࠦࡷࡪࡶ࡫ࠤࡩࡧࡴࡢࠢࡾࢁࠧਜ").format(bstack111l1l1ll_opy_, payload))
          except Exception as e:
              logger.debug(bstack11ll1_opy_ (u"ࠨࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡶࡩࡳࡪࠠ࡬ࡧࡼࠤࡲ࡫ࡴࡳ࡫ࡦࡷࠥࡪࡡࡵࡣࠣࡻ࡮ࡺࡨࠡࡧࡵࡶࡴࡸࠠࡼࡿࠥਝ").format(e))
      bstack1lll1llll_opy_()
      bstack1lllll11l1_opy_(bstack11l1ll1111_opy_, logger)
  except:
    pass
def bstack1l1l1ll1ll_opy_():
  global bstack1l1ll1l11l_opy_
  global bstack1lll111ll_opy_
  global bstack111l1l111_opy_
  global bstack1l111lll_opy_
  global bstack1l1111l1ll_opy_
  global bstack11l1l1ll1l_opy_
  global CONFIG
  bstack1ll11l1ll_opy_ = os.environ.get(bstack11ll1_opy_ (u"ࠧࡇࡔࡄࡑࡊ࡝ࡏࡓࡍࡢ࡙ࡘࡋࡄࠨਞ"))
  if bstack1ll11l1ll_opy_ in [bstack11ll1_opy_ (u"ࠨࡴࡲࡦࡴࡺࠧਟ"), bstack11ll1_opy_ (u"ࠩࡳࡥࡧࡵࡴࠨਠ")]:
    bstack11ll1l111l_opy_()
  percy.shutdown()
  if bstack1l1ll1l11l_opy_:
    logger.warning(bstack1l1llll111_opy_.format(str(bstack1l1ll1l11l_opy_)))
  else:
    try:
      bstack1lll11111l_opy_ = bstack11llllllll_opy_(bstack11ll1_opy_ (u"ࠪ࠲ࡧࡹࡴࡢࡥ࡮࠱ࡨࡵ࡮ࡧ࡫ࡪ࠲࡯ࡹ࡯࡯ࠩਡ"), logger)
      if bstack1lll11111l_opy_.get(bstack11ll1_opy_ (u"ࠫࡳࡻࡤࡨࡧࡢࡰࡴࡩࡡ࡭ࠩਢ")) and bstack1lll11111l_opy_.get(bstack11ll1_opy_ (u"ࠬࡴࡵࡥࡩࡨࡣࡱࡵࡣࡢ࡮ࠪਣ")).get(bstack11ll1_opy_ (u"࠭ࡨࡰࡵࡷࡲࡦࡳࡥࠨਤ")):
        logger.warning(bstack1l1llll111_opy_.format(str(bstack1lll11111l_opy_[bstack11ll1_opy_ (u"ࠧ࡯ࡷࡧ࡫ࡪࡥ࡬ࡰࡥࡤࡰࠬਥ")][bstack11ll1_opy_ (u"ࠨࡪࡲࡷࡹࡴࡡ࡮ࡧࠪਦ")])))
    except Exception as e:
      logger.error(e)
  if cli.is_running():
    bstack1111l11l_opy_.invoke(bstack1l11111l1_opy_.bstack11lll1ll_opy_)
  logger.info(bstack11l1l1111l_opy_)
  global bstack1l1ll1111_opy_
  if bstack1l1ll1111_opy_:
    bstack1ll1ll1l1l_opy_()
  try:
    with bstack1l1lll11_opy_:
      bstack11l1ll1l_opy_ = bstack1lll111ll_opy_.copy()
    for driver in bstack11l1ll1l_opy_:
      driver.quit()
  except Exception as e:
    pass
  logger.info(bstack1l1ll1ll1l_opy_)
  if bstack11l1l1ll1l_opy_ == bstack11ll1_opy_ (u"ࠩࡵࡳࡧࡵࡴࠨਧ"):
    bstack1l1111l1ll_opy_ = bstack1l1l1llll_opy_(bstack11ll1_opy_ (u"ࠪࡶࡴࡨ࡯ࡵࡡࡨࡶࡷࡵࡲࡠ࡮࡬ࡷࡹ࠴ࡪࡴࡱࡱࠫਨ"))
  if bstack11l1l1ll1l_opy_ == bstack11ll1_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࠫ਩") and len(bstack1l111lll_opy_) == 0:
    bstack1l111lll_opy_ = bstack1l1l1llll_opy_(bstack11ll1_opy_ (u"ࠬࡶࡷࡠࡲࡼࡸࡪࡹࡴࡠࡧࡵࡶࡴࡸ࡟࡭࡫ࡶࡸ࠳ࡰࡳࡰࡰࠪਪ"))
    if len(bstack1l111lll_opy_) == 0:
      bstack1l111lll_opy_ = bstack1l1l1llll_opy_(bstack11ll1_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹࡥࡰࡱࡲࡢࡩࡷࡸ࡯ࡳࡡ࡯࡭ࡸࡺ࠮࡫ࡵࡲࡲࠬਫ"))
  bstack11ll1l1l1_opy_ = bstack11ll1_opy_ (u"ࠧࠨਬ")
  if len(bstack111l1l111_opy_) > 0:
    bstack11ll1l1l1_opy_ = bstack111ll1ll1l_opy_(bstack111l1l111_opy_)
  elif len(bstack1l111lll_opy_) > 0:
    bstack11ll1l1l1_opy_ = bstack111ll1ll1l_opy_(bstack1l111lll_opy_)
  elif len(bstack1l1111l1ll_opy_) > 0:
    bstack11ll1l1l1_opy_ = bstack111ll1ll1l_opy_(bstack1l1111l1ll_opy_)
  elif len(bstack1ll1l1l1l1_opy_) > 0:
    bstack11ll1l1l1_opy_ = bstack111ll1ll1l_opy_(bstack1ll1l1l1l1_opy_)
  if bool(bstack11ll1l1l1_opy_):
    bstack1l1ll1ll_opy_(bstack11ll1l1l1_opy_)
  else:
    bstack1l1ll1ll_opy_()
  bstack1lllll11l1_opy_(bstack1ll11l1l1_opy_, logger)
  if bstack1ll11l1ll_opy_ not in [bstack11ll1_opy_ (u"ࠨࡴࡲࡦࡴࡺ࠭ࡪࡰࡷࡩࡷࡴࡡ࡭ࠩਭ")]:
    bstack1ll111l11l_opy_()
  bstack111lll1l1_opy_.bstack1l1l11l11l_opy_(CONFIG)
  if len(bstack1l1111l1ll_opy_) > 0:
    sys.exit(len(bstack1l1111l1ll_opy_))
def bstack1l1l1ll1l1_opy_(bstack11ll11l1_opy_, frame):
  global bstack1l1l1ll1l_opy_
  logger.error(bstack11l11llll1_opy_)
  bstack1l1l1ll1l_opy_.bstack11l1l11l_opy_(bstack11ll1_opy_ (u"ࠩࡶࡨࡰࡑࡩ࡭࡮ࡑࡳࠬਮ"), bstack11ll11l1_opy_)
  if hasattr(signal, bstack11ll1_opy_ (u"ࠪࡗ࡮࡭࡮ࡢ࡮ࡶࠫਯ")):
    bstack1l1l1ll1l_opy_.bstack11l1l11l_opy_(bstack11ll1_opy_ (u"ࠫࡸࡪ࡫ࡌ࡫࡯ࡰࡘ࡯ࡧ࡯ࡣ࡯ࠫਰ"), signal.Signals(bstack11ll11l1_opy_).name)
  else:
    bstack1l1l1ll1l_opy_.bstack11l1l11l_opy_(bstack11ll1_opy_ (u"ࠬࡹࡤ࡬ࡍ࡬ࡰࡱ࡙ࡩࡨࡰࡤࡰࠬ਱"), bstack11ll1_opy_ (u"࠭ࡓࡊࡉࡘࡒࡐࡔࡏࡘࡐࠪਲ"))
  if cli.is_running():
    bstack1111l11l_opy_.invoke(bstack1l11111l1_opy_.bstack11lll1ll_opy_)
  bstack1ll11l1ll_opy_ = os.environ.get(bstack11ll1_opy_ (u"ࠧࡇࡔࡄࡑࡊ࡝ࡏࡓࡍࡢ࡙ࡘࡋࡄࠨਲ਼"))
  if bstack1ll11l1ll_opy_ == bstack11ll1_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࠨ਴") and not cli.is_enabled(CONFIG):
    bstack11lll11l11_opy_.stop(bstack1l1l1ll1l_opy_.get_property(bstack11ll1_opy_ (u"ࠩࡶࡨࡰࡑࡩ࡭࡮ࡖ࡭࡬ࡴࡡ࡭ࠩਵ")))
  bstack1l1l1ll1ll_opy_()
  sys.exit(1)
def bstack11ll11l11_opy_(err):
  logger.critical(bstack1ll1111ll_opy_.format(str(err)))
  bstack1l1ll1ll_opy_(bstack1ll1111ll_opy_.format(str(err)), True)
  atexit.unregister(bstack1l1l1ll1ll_opy_)
  bstack11ll1l111l_opy_()
  sys.exit(1)
def bstack1ll1l1l111_opy_(error, message):
  logger.critical(str(error))
  logger.critical(message)
  bstack1l1ll1ll_opy_(message, True)
  atexit.unregister(bstack1l1l1ll1ll_opy_)
  bstack11ll1l111l_opy_()
  sys.exit(1)
def bstack1lll11l11_opy_():
  global CONFIG
  global bstack1l11111ll_opy_
  global bstack1llllll11l_opy_
  global bstack1llll1l1_opy_
  CONFIG = bstack11l111l1l1_opy_()
  load_dotenv(CONFIG.get(bstack11ll1_opy_ (u"ࠪࡩࡳࡼࡆࡪ࡮ࡨࠫਸ਼")))
  bstack1l1l1lll_opy_()
  bstack1l11llll_opy_()
  CONFIG = bstack1l1ll111l_opy_(CONFIG)
  update(CONFIG, bstack1llllll11l_opy_)
  update(CONFIG, bstack1l11111ll_opy_)
  if not cli.is_enabled(CONFIG):
    CONFIG = bstack1ll1lll11_opy_(CONFIG)
  bstack1llll1l1_opy_ = bstack11lllll11l_opy_(CONFIG)
  os.environ[bstack11ll1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡅ࡚࡚ࡏࡎࡃࡗࡍࡔࡔࠧ਷")] = bstack1llll1l1_opy_.__str__().lower()
  bstack1l1l1ll1l_opy_.bstack11l1l11l_opy_(bstack11ll1_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯ࡤࡹࡥࡴࡵ࡬ࡳࡳ࠭ਸ"), bstack1llll1l1_opy_)
  if (bstack11ll1_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡓࡧ࡭ࡦࠩਹ") in CONFIG and bstack11ll1_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡔࡡ࡮ࡧࠪ਺") in bstack1l11111ll_opy_) or (
          bstack11ll1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠫ਻") in CONFIG and bstack11ll1_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡏࡣࡰࡩ਼ࠬ") not in bstack1llllll11l_opy_):
    if os.getenv(bstack11ll1_opy_ (u"ࠪࡆࡘ࡚ࡁࡄࡍࡢࡇࡔࡓࡂࡊࡐࡈࡈࡤࡈࡕࡊࡎࡇࡣࡎࡊࠧ਽")):
      CONFIG[bstack11ll1_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭ਾ")] = os.getenv(bstack11ll1_opy_ (u"ࠬࡈࡓࡕࡃࡆࡏࡤࡉࡏࡎࡄࡌࡒࡊࡊ࡟ࡃࡗࡌࡐࡉࡥࡉࡅࠩਿ"))
    else:
      if not CONFIG.get(bstack11ll1_opy_ (u"ࠨࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࠤੀ"), bstack11ll1_opy_ (u"ࠢࠣੁ")) in bstack111ll1l1l1_opy_:
        bstack11ll1ll11_opy_()
  elif (bstack11ll1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠫੂ") not in CONFIG and bstack11ll1_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫ੃") in CONFIG) or (
          bstack11ll1_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡐࡤࡱࡪ࠭੄") in bstack1llllll11l_opy_ and bstack11ll1_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡑࡥࡲ࡫ࠧ੅") not in bstack1l11111ll_opy_):
    del (CONFIG[bstack11ll1_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧ੆")])
  if bstack1lll111111_opy_(CONFIG):
    bstack11ll11l11_opy_(bstack1lll11l1_opy_)
  Config.bstack1l1l1111_opy_().bstack11l1l11l_opy_(bstack11ll1_opy_ (u"ࠨࡵࡴࡧࡵࡒࡦࡳࡥࠣੇ"), CONFIG[bstack11ll1_opy_ (u"ࠧࡶࡵࡨࡶࡓࡧ࡭ࡦࠩੈ")])
  bstack11lll1l11_opy_()
  bstack111l1l1l_opy_()
  if bstack1l11l1l1ll_opy_ and not CONFIG.get(bstack11ll1_opy_ (u"ࠣࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࠦ੉"), bstack11ll1_opy_ (u"ࠤࠥ੊")) in bstack111ll1l1l1_opy_:
    CONFIG[bstack11ll1_opy_ (u"ࠪࡥࡵࡶࠧੋ")] = bstack11llll1l1l_opy_(CONFIG)
    logger.info(bstack11ll111lll_opy_.format(CONFIG[bstack11ll1_opy_ (u"ࠫࡦࡶࡰࠨੌ")]))
  if not bstack1llll1l1_opy_:
    CONFIG[bstack11ll1_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨ੍")] = [{}]
def bstack1l111ll1_opy_(config, bstack1l1lll1l_opy_):
  global CONFIG
  global bstack1l11l1l1ll_opy_
  CONFIG = config
  bstack1l11l1l1ll_opy_ = bstack1l1lll1l_opy_
def bstack111l1l1l_opy_():
  global CONFIG
  global bstack1l11l1l1ll_opy_
  if bstack11ll1_opy_ (u"࠭ࡡࡱࡲࠪ੎") in CONFIG:
    try:
      from appium import version
    except Exception as e:
      bstack1ll1l1l111_opy_(e, bstack1ll11l111_opy_)
    bstack1l11l1l1ll_opy_ = True
    bstack1l1l1ll1l_opy_.bstack11l1l11l_opy_(bstack11ll1_opy_ (u"ࠧࡢࡲࡳࡣࡦࡻࡴࡰ࡯ࡤࡸࡪ࠭੏"), True)
def bstack11llll1l1l_opy_(config):
  bstack1l11l111ll_opy_ = bstack11ll1_opy_ (u"ࠨࠩ੐")
  app = config[bstack11ll1_opy_ (u"ࠩࡤࡴࡵ࠭ੑ")]
  if isinstance(app, str):
    if os.path.splitext(app)[1] in bstack1lll1l11_opy_:
      if os.path.exists(app):
        bstack1l11l111ll_opy_ = bstack1l1l11ll1_opy_(config, app)
      elif bstack11l11ll1l1_opy_(app):
        bstack1l11l111ll_opy_ = app
      else:
        bstack11ll11l11_opy_(bstack1111l1l1_opy_.format(app))
    else:
      if bstack11l11ll1l1_opy_(app):
        bstack1l11l111ll_opy_ = app
      elif os.path.exists(app):
        bstack1l11l111ll_opy_ = bstack1l1l11ll1_opy_(app)
      else:
        bstack11ll11l11_opy_(bstack111llllll1_opy_)
  else:
    if len(app) > 2:
      bstack11ll11l11_opy_(bstack111l1lll_opy_)
    elif len(app) == 2:
      if bstack11ll1_opy_ (u"ࠪࡴࡦࡺࡨࠨ੒") in app and bstack11ll1_opy_ (u"ࠫࡨࡻࡳࡵࡱࡰࡣ࡮ࡪࠧ੓") in app:
        if os.path.exists(app[bstack11ll1_opy_ (u"ࠬࡶࡡࡵࡪࠪ੔")]):
          bstack1l11l111ll_opy_ = bstack1l1l11ll1_opy_(config, app[bstack11ll1_opy_ (u"࠭ࡰࡢࡶ࡫ࠫ੕")], app[bstack11ll1_opy_ (u"ࠧࡤࡷࡶࡸࡴࡳ࡟ࡪࡦࠪ੖")])
        else:
          bstack11ll11l11_opy_(bstack1111l1l1_opy_.format(app))
      else:
        bstack11ll11l11_opy_(bstack111l1lll_opy_)
    else:
      for key in app:
        if key in bstack111l1111_opy_:
          if key == bstack11ll1_opy_ (u"ࠨࡲࡤࡸ࡭࠭੗"):
            if os.path.exists(app[key]):
              bstack1l11l111ll_opy_ = bstack1l1l11ll1_opy_(config, app[key])
            else:
              bstack11ll11l11_opy_(bstack1111l1l1_opy_.format(app))
          else:
            bstack1l11l111ll_opy_ = app[key]
        else:
          bstack11ll11l11_opy_(bstack1l11ll111_opy_)
  return bstack1l11l111ll_opy_
def bstack11l11ll1l1_opy_(bstack1l11l111ll_opy_):
  import re
  bstack11ll11l1l1_opy_ = re.compile(bstack11ll1_opy_ (u"ࡴࠥࡢࡠࡧ࠭ࡻࡃ࠰࡞࠵࠳࠹࡝ࡡ࠱ࡠ࠲ࡣࠪࠥࠤ੘"))
  bstack11l11l1l1_opy_ = re.compile(bstack11ll1_opy_ (u"ࡵࠦࡣࡡࡡ࠮ࡼࡄ࠱࡟࠶࠭࠺࡞ࡢ࠲ࡡ࠳࡝ࠫ࠱࡞ࡥ࠲ࢀࡁ࠮࡜࠳࠱࠾ࡢ࡟࠯࡞࠰ࡡ࠯ࠪࠢਖ਼"))
  if bstack11ll1_opy_ (u"ࠫࡧࡹ࠺࠰࠱ࠪਗ਼") in bstack1l11l111ll_opy_ or re.fullmatch(bstack11ll11l1l1_opy_, bstack1l11l111ll_opy_) or re.fullmatch(bstack11l11l1l1_opy_, bstack1l11l111ll_opy_):
    return True
  else:
    return False
@measure(event_name=EVENTS.bstack1ll1111lll_opy_, stage=STAGE.bstack11l1llll1_opy_, bstack1lll1l1l1_opy_=bstack1ll1l11111_opy_)
def bstack1l1l11ll1_opy_(config, path, bstack1ll1l1ll11_opy_=None):
  import requests
  from requests_toolbelt.multipart.encoder import MultipartEncoder
  import hashlib
  md5_hash = hashlib.md5(open(os.path.abspath(path), bstack11ll1_opy_ (u"ࠬࡸࡢࠨਜ਼")).read()).hexdigest()
  bstack111111l1l_opy_ = bstack11l11l11_opy_(md5_hash)
  bstack1l11l111ll_opy_ = None
  if bstack111111l1l_opy_:
    logger.info(bstack1l11l1ll1_opy_.format(bstack111111l1l_opy_, md5_hash))
    return bstack111111l1l_opy_
  bstack1ll11l1l1l_opy_ = datetime.datetime.now()
  bstack11l11l111l_opy_ = MultipartEncoder(
    fields={
      bstack11ll1_opy_ (u"࠭ࡦࡪ࡮ࡨࠫੜ"): (os.path.basename(path), open(os.path.abspath(path), bstack11ll1_opy_ (u"ࠧࡳࡤࠪ੝")), bstack11ll1_opy_ (u"ࠨࡶࡨࡼࡹ࠵ࡰ࡭ࡣ࡬ࡲࠬਫ਼")),
      bstack11ll1_opy_ (u"ࠩࡦࡹࡸࡺ࡯࡮ࡡ࡬ࡨࠬ੟"): bstack1ll1l1ll11_opy_
    }
  )
  response = requests.post(bstack1l1lll1ll1_opy_, data=bstack11l11l111l_opy_,
                           headers={bstack11ll1_opy_ (u"ࠪࡇࡴࡴࡴࡦࡰࡷ࠱࡙ࡿࡰࡦࠩ੠"): bstack11l11l111l_opy_.content_type},
                           auth=(config[bstack11ll1_opy_ (u"ࠫࡺࡹࡥࡳࡐࡤࡱࡪ࠭੡")], config[bstack11ll1_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷࡐ࡫ࡹࠨ੢")]))
  try:
    res = json.loads(response.text)
    bstack1l11l111ll_opy_ = res[bstack11ll1_opy_ (u"࠭ࡡࡱࡲࡢࡹࡷࡲࠧ੣")]
    logger.info(bstack1ll11l11l1_opy_.format(bstack1l11l111ll_opy_))
    bstack11ll1llll1_opy_(md5_hash, bstack1l11l111ll_opy_)
    cli.bstack1lll1lll1_opy_(bstack11ll1_opy_ (u"ࠢࡩࡶࡷࡴ࠿ࡻࡰ࡭ࡱࡤࡨࡤࡧࡰࡱࠤ੤"), datetime.datetime.now() - bstack1ll11l1l1l_opy_)
  except ValueError as err:
    bstack11ll11l11_opy_(bstack1l1l1l1ll1_opy_.format(str(err)))
  return bstack1l11l111ll_opy_
def bstack11lll1l11_opy_(framework_name=None, args=None):
  global CONFIG
  global bstack11l1l1l11_opy_
  bstack11l11l11l_opy_ = 1
  bstack11ll1l11_opy_ = 1
  if bstack11ll1_opy_ (u"ࠨࡲࡤࡶࡦࡲ࡬ࡦ࡮ࡶࡔࡪࡸࡐ࡭ࡣࡷࡪࡴࡸ࡭ࠨ੥") in CONFIG:
    bstack11ll1l11_opy_ = CONFIG[bstack11ll1_opy_ (u"ࠩࡳࡥࡷࡧ࡬࡭ࡧ࡯ࡷࡕ࡫ࡲࡑ࡮ࡤࡸ࡫ࡵࡲ࡮ࠩ੦")]
  else:
    bstack11ll1l11_opy_ = bstack11l11l1l11_opy_(framework_name, args) or 1
  if bstack11ll1_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭੧") in CONFIG:
    bstack11l11l11l_opy_ = len(CONFIG[bstack11ll1_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧ੨")])
  bstack11l1l1l11_opy_ = int(bstack11ll1l11_opy_) * int(bstack11l11l11l_opy_)
def bstack11l11l1l11_opy_(framework_name, args):
  if framework_name == bstack11l1111lll_opy_ and args and bstack11ll1_opy_ (u"ࠬ࠳࠭ࡱࡴࡲࡧࡪࡹࡳࡦࡵࠪ੩") in args:
      bstack1lll11ll11_opy_ = args.index(bstack11ll1_opy_ (u"࠭࠭࠮ࡲࡵࡳࡨ࡫ࡳࡴࡧࡶࠫ੪"))
      return int(args[bstack1lll11ll11_opy_ + 1]) or 1
  return 1
def bstack11l11l11_opy_(md5_hash):
  try:
    from filelock import FileLock
  except ImportError:
    logger.debug(bstack11ll1_opy_ (u"ࠧࡧ࡫࡯ࡩࡱࡵࡣ࡬ࠢࡱࡳࡹࠦࡡࡷࡣ࡬ࡰࡦࡨ࡬ࡦ࠮ࠣࡹࡸ࡯࡮ࡨࠢࡥࡥࡸ࡯ࡣࠡࡨ࡬ࡰࡪࠦ࡯ࡱࡧࡵࡥࡹ࡯࡯࡯ࡵࠪ੫"))
    bstack11ll1l1l_opy_ = os.path.join(os.path.expanduser(bstack11ll1_opy_ (u"ࠨࢀࠪ੬")), bstack11ll1_opy_ (u"ࠩ࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࠩ੭"), bstack11ll1_opy_ (u"ࠪࡥࡵࡶࡕࡱ࡮ࡲࡥࡩࡓࡄ࠶ࡊࡤࡷ࡭࠴ࡪࡴࡱࡱࠫ੮"))
    if os.path.exists(bstack11ll1l1l_opy_):
      try:
        bstack11111ll11_opy_ = json.load(open(bstack11ll1l1l_opy_, bstack11ll1_opy_ (u"ࠫࡷࡨࠧ੯")))
        if md5_hash in bstack11111ll11_opy_:
          bstack1ll1111l_opy_ = bstack11111ll11_opy_[md5_hash]
          bstack1llll1ll1_opy_ = datetime.datetime.now()
          bstack1l1lll11l_opy_ = datetime.datetime.strptime(bstack1ll1111l_opy_[bstack11ll1_opy_ (u"ࠬࡺࡩ࡮ࡧࡶࡸࡦࡳࡰࠨੰ")], bstack11ll1_opy_ (u"࠭ࠥࡥ࠱ࠨࡱ࠴࡙ࠫࠡࠧࡋ࠾ࠪࡓ࠺ࠦࡕࠪੱ"))
          if (bstack1llll1ll1_opy_ - bstack1l1lll11l_opy_).days > 30:
            return None
          elif version.parse(str(__version__)) > version.parse(bstack1ll1111l_opy_[bstack11ll1_opy_ (u"ࠧࡴࡦ࡮ࡣࡻ࡫ࡲࡴ࡫ࡲࡲࠬੲ")]):
            return None
          return bstack1ll1111l_opy_[bstack11ll1_opy_ (u"ࠨ࡫ࡧࠫੳ")]
      except Exception as e:
        logger.debug(bstack11ll1_opy_ (u"ࠩࡈࡶࡷࡵࡲࠡࡴࡨࡥࡩ࡯࡮ࡨࠢࡐࡈ࠺ࠦࡨࡢࡵ࡫ࠤ࡫࡯࡬ࡦ࠼ࠣࡿࢂ࠭ੴ").format(str(e)))
    return None
  bstack11ll1l1l_opy_ = os.path.join(os.path.expanduser(bstack11ll1_opy_ (u"ࠪࢂࠬੵ")), bstack11ll1_opy_ (u"ࠫ࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࠫ੶"), bstack11ll1_opy_ (u"ࠬࡧࡰࡱࡗࡳࡰࡴࡧࡤࡎࡆ࠸ࡌࡦࡹࡨ࠯࡬ࡶࡳࡳ࠭੷"))
  lock_file = bstack11ll1l1l_opy_ + bstack11ll1_opy_ (u"࠭࠮࡭ࡱࡦ࡯ࠬ੸")
  try:
    with FileLock(lock_file, timeout=10):
      if os.path.exists(bstack11ll1l1l_opy_):
        with open(bstack11ll1l1l_opy_, bstack11ll1_opy_ (u"ࠧࡳࠩ੹")) as f:
          content = f.read().strip()
          if content:
            bstack11111ll11_opy_ = json.loads(content)
            if md5_hash in bstack11111ll11_opy_:
              bstack1ll1111l_opy_ = bstack11111ll11_opy_[md5_hash]
              bstack1llll1ll1_opy_ = datetime.datetime.now()
              bstack1l1lll11l_opy_ = datetime.datetime.strptime(bstack1ll1111l_opy_[bstack11ll1_opy_ (u"ࠨࡶ࡬ࡱࡪࡹࡴࡢ࡯ࡳࠫ੺")], bstack11ll1_opy_ (u"ࠩࠨࡨ࠴ࠫ࡭࠰ࠧ࡜ࠤࠪࡎ࠺ࠦࡏ࠽ࠩࡘ࠭੻"))
              if (bstack1llll1ll1_opy_ - bstack1l1lll11l_opy_).days > 30:
                return None
              elif version.parse(str(__version__)) > version.parse(bstack1ll1111l_opy_[bstack11ll1_opy_ (u"ࠪࡷࡩࡱ࡟ࡷࡧࡵࡷ࡮ࡵ࡮ࠨ੼")]):
                return None
              return bstack1ll1111l_opy_[bstack11ll1_opy_ (u"ࠫ࡮ࡪࠧ੽")]
      return None
  except Exception as e:
    logger.debug(bstack11ll1_opy_ (u"ࠬࡋࡲࡳࡱࡵࠤࡼ࡯ࡴࡩࠢࡩ࡭ࡱ࡫ࠠ࡭ࡱࡦ࡯࡮ࡴࡧࠡࡨࡲࡶࠥࡓࡄ࠶ࠢ࡫ࡥࡸ࡮࠺ࠡࡽࢀࠫ੾").format(str(e)))
    return None
def bstack11ll1llll1_opy_(md5_hash, bstack1l11l111ll_opy_):
  try:
    from filelock import FileLock
  except ImportError:
    logger.debug(bstack11ll1_opy_ (u"࠭ࡦࡪ࡮ࡨࡰࡴࡩ࡫ࠡࡰࡲࡸࠥࡧࡶࡢ࡫࡯ࡥࡧࡲࡥ࠭ࠢࡸࡷ࡮ࡴࡧࠡࡤࡤࡷ࡮ࡩࠠࡧ࡫࡯ࡩࠥࡵࡰࡦࡴࡤࡸ࡮ࡵ࡮ࡴࠩ੿"))
    bstack11lll1lll_opy_ = os.path.join(os.path.expanduser(bstack11ll1_opy_ (u"ࠧࡿࠩ઀")), bstack11ll1_opy_ (u"ࠨ࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࠨઁ"))
    if not os.path.exists(bstack11lll1lll_opy_):
      os.makedirs(bstack11lll1lll_opy_)
    bstack11ll1l1l_opy_ = os.path.join(os.path.expanduser(bstack11ll1_opy_ (u"ࠩࢁࠫં")), bstack11ll1_opy_ (u"ࠪ࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࠪઃ"), bstack11ll1_opy_ (u"ࠫࡦࡶࡰࡖࡲ࡯ࡳࡦࡪࡍࡅ࠷ࡋࡥࡸ࡮࠮࡫ࡵࡲࡲࠬ઄"))
    bstack1ll11l11_opy_ = {
      bstack11ll1_opy_ (u"ࠬ࡯ࡤࠨઅ"): bstack1l11l111ll_opy_,
      bstack11ll1_opy_ (u"࠭ࡴࡪ࡯ࡨࡷࡹࡧ࡭ࡱࠩઆ"): datetime.datetime.strftime(datetime.datetime.now(), bstack11ll1_opy_ (u"ࠧࠦࡦ࠲ࠩࡲ࠵࡚ࠥࠢࠨࡌ࠿ࠫࡍ࠻ࠧࡖࠫઇ")),
      bstack11ll1_opy_ (u"ࠨࡵࡧ࡯ࡤࡼࡥࡳࡵ࡬ࡳࡳ࠭ઈ"): str(__version__)
    }
    try:
      bstack11111ll11_opy_ = {}
      if os.path.exists(bstack11ll1l1l_opy_):
        bstack11111ll11_opy_ = json.load(open(bstack11ll1l1l_opy_, bstack11ll1_opy_ (u"ࠩࡵࡦࠬઉ")))
      bstack11111ll11_opy_[md5_hash] = bstack1ll11l11_opy_
      with open(bstack11ll1l1l_opy_, bstack11ll1_opy_ (u"ࠥࡻ࠰ࠨઊ")) as outfile:
        json.dump(bstack11111ll11_opy_, outfile)
    except Exception as e:
      logger.debug(bstack11ll1_opy_ (u"ࠫࡊࡸࡲࡰࡴࠣࡹࡵࡪࡡࡵ࡫ࡱ࡫ࠥࡓࡄ࠶ࠢ࡫ࡥࡸ࡮ࠠࡧ࡫࡯ࡩ࠿ࠦࡻࡾࠩઋ").format(str(e)))
    return
  bstack11lll1lll_opy_ = os.path.join(os.path.expanduser(bstack11ll1_opy_ (u"ࠬࢄࠧઌ")), bstack11ll1_opy_ (u"࠭࠮ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠭ઍ"))
  if not os.path.exists(bstack11lll1lll_opy_):
    os.makedirs(bstack11lll1lll_opy_)
  bstack11ll1l1l_opy_ = os.path.join(os.path.expanduser(bstack11ll1_opy_ (u"ࠧࡿࠩ઎")), bstack11ll1_opy_ (u"ࠨ࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࠨએ"), bstack11ll1_opy_ (u"ࠩࡤࡴࡵ࡛ࡰ࡭ࡱࡤࡨࡒࡊ࠵ࡉࡣࡶ࡬࠳ࡰࡳࡰࡰࠪઐ"))
  lock_file = bstack11ll1l1l_opy_ + bstack11ll1_opy_ (u"ࠪ࠲ࡱࡵࡣ࡬ࠩઑ")
  bstack1ll11l11_opy_ = {
    bstack11ll1_opy_ (u"ࠫ࡮ࡪࠧ઒"): bstack1l11l111ll_opy_,
    bstack11ll1_opy_ (u"ࠬࡺࡩ࡮ࡧࡶࡸࡦࡳࡰࠨઓ"): datetime.datetime.strftime(datetime.datetime.now(), bstack11ll1_opy_ (u"࠭ࠥࡥ࠱ࠨࡱ࠴࡙ࠫࠡࠧࡋ࠾ࠪࡓ࠺ࠦࡕࠪઔ")),
    bstack11ll1_opy_ (u"ࠧࡴࡦ࡮ࡣࡻ࡫ࡲࡴ࡫ࡲࡲࠬક"): str(__version__)
  }
  try:
    with FileLock(lock_file, timeout=10):
      bstack11111ll11_opy_ = {}
      if os.path.exists(bstack11ll1l1l_opy_):
        with open(bstack11ll1l1l_opy_, bstack11ll1_opy_ (u"ࠨࡴࠪખ")) as f:
          content = f.read().strip()
          if content:
            bstack11111ll11_opy_ = json.loads(content)
      bstack11111ll11_opy_[md5_hash] = bstack1ll11l11_opy_
      with open(bstack11ll1l1l_opy_, bstack11ll1_opy_ (u"ࠤࡺࠦગ")) as outfile:
        json.dump(bstack11111ll11_opy_, outfile)
  except Exception as e:
    logger.debug(bstack11ll1_opy_ (u"ࠪࡉࡷࡸ࡯ࡳࠢࡺ࡭ࡹ࡮ࠠࡧ࡫࡯ࡩࠥࡲ࡯ࡤ࡭࡬ࡲ࡬ࠦࡦࡰࡴࠣࡑࡉ࠻ࠠࡩࡣࡶ࡬ࠥࡻࡰࡥࡣࡷࡩ࠿ࠦࡻࡾࠩઘ").format(str(e)))
def bstack1l1l1ll111_opy_(self):
  return
def bstack1l1lllll1_opy_(self):
  return
def bstack1ll1l111l1_opy_():
  global bstack11l1l1111_opy_
  bstack11l1l1111_opy_ = True
@measure(event_name=EVENTS.bstack1lll111l1_opy_, stage=STAGE.bstack11l1llll1_opy_, bstack1lll1l1l1_opy_=bstack1ll1l11111_opy_)
def bstack1l1l111l1_opy_(self):
  global bstack11l1l11ll_opy_
  global bstack1l111l111l_opy_
  global bstack1llll1lll1_opy_
  try:
    if bstack11ll1_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࠫઙ") in bstack11l1l11ll_opy_ and self.session_id != None and bstack1lll11l1l_opy_(threading.current_thread(), bstack11ll1_opy_ (u"ࠬࡺࡥࡴࡶࡖࡸࡦࡺࡵࡴࠩચ"), bstack11ll1_opy_ (u"࠭ࠧછ")) != bstack11ll1_opy_ (u"ࠧࡴ࡭࡬ࡴࡵ࡫ࡤࠨજ"):
      bstack11ll1ll1_opy_ = bstack11ll1_opy_ (u"ࠨࡲࡤࡷࡸ࡫ࡤࠨઝ") if len(threading.current_thread().bstackTestErrorMessages) == 0 else bstack11ll1_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࠩઞ")
      if bstack11ll1ll1_opy_ == bstack11ll1_opy_ (u"ࠪࡪࡦ࡯࡬ࡦࡦࠪટ"):
        bstack11l111l1ll_opy_(logger)
      if self != None:
        bstack1ll11ll1ll_opy_(self, bstack11ll1ll1_opy_, bstack11ll1_opy_ (u"ࠫ࠱ࠦࠧઠ").join(threading.current_thread().bstackTestErrorMessages))
    threading.current_thread().testStatus = bstack11ll1_opy_ (u"ࠬ࠭ડ")
    if bstack11ll1_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹ࠭ઢ") in bstack11l1l11ll_opy_ and getattr(threading.current_thread(), bstack11ll1_opy_ (u"ࠧࡢ࠳࠴ࡽࡕࡲࡡࡵࡨࡲࡶࡲ࠭ણ"), None):
      bstack1lll1l11ll_opy_.bstack1l1lllll1l_opy_(self, bstack1l11l11ll_opy_, logger, wait=True)
    if bstack11ll1_opy_ (u"ࠨࡤࡨ࡬ࡦࡼࡥࠨત") in bstack11l1l11ll_opy_:
      if not threading.currentThread().behave_test_status:
        bstack1ll11ll1ll_opy_(self, bstack11ll1_opy_ (u"ࠤࡳࡥࡸࡹࡥࡥࠤથ"))
      bstack11l1111l1l_opy_.bstack1l1l1l1lll_opy_(self)
  except Exception as e:
    logger.debug(bstack11ll1_opy_ (u"ࠥࡉࡷࡸ࡯ࡳࠢࡺ࡬࡮ࡲࡥࠡ࡯ࡤࡶࡰ࡯࡮ࡨࠢࡶࡸࡦࡺࡵࡴ࠼ࠣࠦદ") + str(e))
  bstack1llll1lll1_opy_(self)
  self.session_id = None
def bstack1l1ll1l11_opy_(self, *args, **kwargs):
  try:
    from selenium.webdriver.remote.remote_connection import RemoteConnection
    from bstack_utils.helper import bstack1llllll1ll_opy_
    global bstack11l1l11ll_opy_
    command_executor = kwargs.get(bstack11ll1_opy_ (u"ࠫࡨࡵ࡭࡮ࡣࡱࡨࡤ࡫ࡸࡦࡥࡸࡸࡴࡸࠧધ"), bstack11ll1_opy_ (u"ࠬ࠭ન"))
    bstack1lll1l111_opy_ = False
    if type(command_executor) == str and bstack11ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡩ࡯࡮ࠩ઩") in command_executor:
      bstack1lll1l111_opy_ = True
    elif isinstance(command_executor, RemoteConnection) and bstack11ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡣࡰ࡯ࠪપ") in str(getattr(command_executor, bstack11ll1_opy_ (u"ࠨࡡࡸࡶࡱ࠭ફ"), bstack11ll1_opy_ (u"ࠩࠪબ"))):
      bstack1lll1l111_opy_ = True
    else:
      kwargs = bstack1l1ll11l1l_opy_.bstack1l1l111l11_opy_(bstack1l1111lll_opy_=kwargs, config=CONFIG)
      return bstack1lll1l1l_opy_(self, *args, **kwargs)
    if bstack1lll1l111_opy_:
      bstack11l1111l11_opy_ = bstack1l11111ll1_opy_.bstack111lll11l_opy_(CONFIG, bstack11l1l11ll_opy_)
      if kwargs.get(bstack11ll1_opy_ (u"ࠪࡳࡵࡺࡩࡰࡰࡶࠫભ")):
        kwargs[bstack11ll1_opy_ (u"ࠫࡴࡶࡴࡪࡱࡱࡷࠬમ")] = bstack1llllll1ll_opy_(kwargs[bstack11ll1_opy_ (u"ࠬࡵࡰࡵ࡫ࡲࡲࡸ࠭ય")], bstack11l1l11ll_opy_, CONFIG, bstack11l1111l11_opy_)
      elif kwargs.get(bstack11ll1_opy_ (u"࠭ࡤࡦࡵ࡬ࡶࡪࡪ࡟ࡤࡣࡳࡥࡧ࡯࡬ࡪࡶ࡬ࡩࡸ࠭ર")):
        kwargs[bstack11ll1_opy_ (u"ࠧࡥࡧࡶ࡭ࡷ࡫ࡤࡠࡥࡤࡴࡦࡨࡩ࡭࡫ࡷ࡭ࡪࡹࠧ઱")] = bstack1llllll1ll_opy_(kwargs[bstack11ll1_opy_ (u"ࠨࡦࡨࡷ࡮ࡸࡥࡥࡡࡦࡥࡵࡧࡢࡪ࡮࡬ࡸ࡮࡫ࡳࠨલ")], bstack11l1l11ll_opy_, CONFIG, bstack11l1111l11_opy_)
  except Exception as e:
    logger.error(bstack11ll1_opy_ (u"ࠤࡈࡶࡷࡵࡲࠡࡹ࡫ࡩࡳࠦࡰࡳࡱࡦࡩࡸࡹࡩ࡯ࡩࠣࡗࡉࡑࠠࡤࡣࡳࡷ࠿ࠦࡻࡾࠤળ").format(str(e)))
  return bstack1lll1l1l_opy_(self, *args, **kwargs)
@measure(event_name=EVENTS.bstack111lll111l_opy_, stage=STAGE.bstack11l1llll1_opy_, bstack1lll1l1l1_opy_=bstack1ll1l11111_opy_)
def bstack111111ll1_opy_(self, command_executor=bstack11ll1_opy_ (u"ࠥ࡬ࡹࡺࡰ࠻࠱࠲࠵࠷࠽࠮࠱࠰࠳࠲࠶ࡀ࠴࠵࠶࠷ࠦ઴"), *args, **kwargs):
  global bstack1l111l111l_opy_
  global bstack1lll111ll_opy_
  bstack1111ll111_opy_ = bstack1l1ll1l11_opy_(self, command_executor=command_executor, *args, **kwargs)
  if not bstack1l11llll1l_opy_.on():
    return bstack1111ll111_opy_
  try:
    logger.debug(bstack11ll1_opy_ (u"ࠫࡈࡵ࡭࡮ࡣࡱࡨࠥࡋࡸࡦࡥࡸࡸࡴࡸࠠࡸࡪࡨࡲࠥࡈࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࠤࡆࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠡ࡫ࡶࠤ࡫ࡧ࡬ࡴࡧࠣ࠱ࠥࢁࡽࠨવ").format(str(command_executor)))
    logger.debug(bstack11ll1_opy_ (u"ࠬࡎࡵࡣࠢࡘࡖࡑࠦࡩࡴࠢ࠰ࠤࢀࢃࠧશ").format(str(command_executor._url)))
    from selenium.webdriver.remote.remote_connection import RemoteConnection
    if isinstance(command_executor, RemoteConnection) and bstack11ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡩ࡯࡮ࠩષ") in command_executor._url:
      bstack1l1l1ll1l_opy_.bstack11l1l11l_opy_(bstack11ll1_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱ࡟ࡴࡧࡶࡷ࡮ࡵ࡮ࠨસ"), True)
  except:
    pass
  if (isinstance(command_executor, str) and bstack11ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡤࡱࡰࠫહ") in command_executor):
    bstack1l1l1ll1l_opy_.bstack11l1l11l_opy_(bstack11ll1_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬ࡡࡶࡩࡸࡹࡩࡰࡰࠪ઺"), True)
  threading.current_thread().bstackSessionDriver = self
  bstack1ll1111ll1_opy_ = getattr(threading.current_thread(), bstack11ll1_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭ࡗࡩࡸࡺࡍࡦࡶࡤࠫ઻"), None)
  bstack111llll1l1_opy_ = {}
  if self.capabilities is not None:
    bstack111llll1l1_opy_[bstack11ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡤࡴࡡ࡮ࡧ઼ࠪ")] = self.capabilities.get(bstack11ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡔࡡ࡮ࡧࠪઽ"))
    bstack111llll1l1_opy_[bstack11ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸ࡟ࡷࡧࡵࡷ࡮ࡵ࡮ࠨા")] = self.capabilities.get(bstack11ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡗࡧࡵࡷ࡮ࡵ࡮ࠨિ"))
    bstack111llll1l1_opy_[bstack11ll1_opy_ (u"ࠨࡥ࡫ࡶࡴࡳࡥࡠࡱࡳࡸ࡮ࡵ࡮ࡴࠩી")] = self.capabilities.get(bstack11ll1_opy_ (u"ࠩࡪࡳࡴ࡭࠺ࡤࡪࡵࡳࡲ࡫ࡏࡱࡶ࡬ࡳࡳࡹࠧુ"))
  if CONFIG.get(bstack11ll1_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠪૂ"), False) and bstack1l1ll11l1l_opy_.bstack1ll11l1lll_opy_(bstack111llll1l1_opy_):
    threading.current_thread().a11yPlatform = True
  if bstack11ll1_opy_ (u"ࠫࡧ࡫ࡨࡢࡸࡨࠫૃ") in bstack11l1l11ll_opy_ or bstack11ll1_opy_ (u"ࠬࡸ࡯ࡣࡱࡷࠫૄ") in bstack11l1l11ll_opy_:
    bstack11lll11l11_opy_.bstack1ll1lll111_opy_(self)
  if bstack11ll1_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹ࠭ૅ") in bstack11l1l11ll_opy_ and bstack1ll1111ll1_opy_ and bstack1ll1111ll1_opy_.get(bstack11ll1_opy_ (u"ࠧࡴࡶࡤࡸࡺࡹࠧ૆"), bstack11ll1_opy_ (u"ࠨࠩે")) == bstack11ll1_opy_ (u"ࠩࡳࡩࡳࡪࡩ࡯ࡩࠪૈ"):
    bstack11lll11l11_opy_.bstack1ll1lll111_opy_(self)
  bstack1l111l111l_opy_ = self.session_id
  with bstack1l1lll11_opy_:
    bstack1lll111ll_opy_.append(self)
  return bstack1111ll111_opy_
def bstack11l11ll1ll_opy_(args):
  return bstack11ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡨࡼࡪࡩࡵࡵࡱࡵࠫૉ") in str(args)
def bstack11ll111111_opy_(self, driver_command, *args, **kwargs):
  global bstack11ll11l1ll_opy_
  global bstack1lll11lll1_opy_
  bstack11llll1111_opy_ = bstack1lll11l1l_opy_(threading.current_thread(), bstack11ll1_opy_ (u"ࠫ࡮ࡹࡁ࠲࠳ࡼࡘࡪࡹࡴࠨ૊"), None) and bstack1lll11l1l_opy_(
          threading.current_thread(), bstack11ll1_opy_ (u"ࠬࡧ࠱࠲ࡻࡓࡰࡦࡺࡦࡰࡴࡰࠫો"), None)
  bstack111lll1l_opy_ = bstack1lll11l1l_opy_(threading.current_thread(), bstack11ll1_opy_ (u"࠭ࡩࡴࡃࡳࡴࡆ࠷࠱ࡺࡖࡨࡷࡹ࠭ૌ"), None) and bstack1lll11l1l_opy_(
          threading.current_thread(), bstack11ll1_opy_ (u"ࠧࡢࡲࡳࡅ࠶࠷ࡹࡑ࡮ࡤࡸ࡫ࡵࡲ࡮્ࠩ"), None)
  bstack111lll11_opy_ = getattr(self, bstack11ll1_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫ࡂ࠳࠴ࡽࡘ࡮࡯ࡶ࡮ࡧࡗࡨࡧ࡮ࠨ૎"), None) != None and getattr(self, bstack11ll1_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬ࡃ࠴࠵ࡾ࡙ࡨࡰࡷ࡯ࡨࡘࡩࡡ࡯ࠩ૏"), None) == True
  if not bstack1lll11lll1_opy_ and bstack11ll1_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠪૐ") in CONFIG and CONFIG[bstack11ll1_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠫ૑")] == True and bstack1l11l111l1_opy_.bstack1ll1l1111l_opy_(driver_command) and (bstack111lll11_opy_ or bstack11llll1111_opy_ or bstack111lll1l_opy_) and not bstack11l11ll1ll_opy_(args):
    try:
      bstack1lll11lll1_opy_ = True
      logger.debug(bstack11ll1_opy_ (u"ࠬࡖࡥࡳࡨࡲࡶࡲ࡯࡮ࡨࠢࡶࡧࡦࡴࠠࡧࡱࡵࠤࢀࢃࠧ૒").format(driver_command))
      bstack1ll11lll11_opy_ = perform_scan(self, driver_command=driver_command)
      logger.debug(bstack1ll11lll11_opy_)
      try:
        bstack1ll1ll11ll_opy_ = {
          bstack11ll1_opy_ (u"ࠨࡲࡦࡳࡸࡩࡸࡺࠢ૓"): {
            bstack11ll1_opy_ (u"ࠢࡤࡱࡰࡱࡦࡴࡤࠣ૔"): bstack11ll1_opy_ (u"ࠣࡃ࠴࠵࡞ࡥࡓࡄࡃࡑࠦ૕"),
            bstack11ll1_opy_ (u"ࠤࡳࡥࡷࡧ࡭ࡦࡶࡨࡶࡸࠨ૖"): [
              {
                bstack11ll1_opy_ (u"ࠥࡱࡪࡺࡨࡰࡦࠥ૗"): driver_command
              }
            ]
          },
          bstack11ll1_opy_ (u"ࠦࡷ࡫ࡳࡱࡱࡱࡷࡪࠨ૘"): {
            bstack11ll1_opy_ (u"ࠧࡨ࡯ࡥࡻࠥ૙"): {
              bstack11ll1_opy_ (u"ࠨ࡭ࡴࡩࠥ૚"): bstack1ll11lll11_opy_.get(bstack11ll1_opy_ (u"ࠢ࡮ࡵࡪࠦ૛"), bstack11ll1_opy_ (u"ࠣࠤ૜")) if isinstance(bstack1ll11lll11_opy_, dict) else bstack11ll1_opy_ (u"ࠤࠥ૝"),
              bstack11ll1_opy_ (u"ࠥࡷࡺࡩࡣࡦࡵࡶࠦ૞"): bstack1ll11lll11_opy_.get(bstack11ll1_opy_ (u"ࠦࡸࡻࡣࡤࡧࡶࡷࠧ૟"), True) if isinstance(bstack1ll11lll11_opy_, dict) else True
            }
          }
        }
        logger.debug(bstack11ll1_opy_ (u"ࠬࡇࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡹࡣࡢࡰࠣࡥࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࠠ࡭ࡱࡪࠤࡩࡧࡴࡢ࠼ࠣࡿࢂ࠭ૠ").format(bstack1ll1ll11ll_opy_))
        bstack11ll111l1l_opy_.info(json.dumps(bstack1ll1ll11ll_opy_, separators=(bstack11ll1_opy_ (u"࠭ࠬࠨૡ"), bstack11ll1_opy_ (u"ࠧ࠻ࠩૢ"))))
      except Exception as bstack1l11lll1_opy_:
        logger.debug(bstack11ll1_opy_ (u"ࠨࡈࡤ࡭ࡱ࡫ࡤࠡࡶࡲࠤࡱࡵࡧࠡࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠡࡵࡦࡥࡳࠦࡤࡢࡶࡤ࠾ࠥࢁࡽࠨૣ").format(str(bstack1l11lll1_opy_)))
    except Exception as err:
      logger.debug(bstack11ll1_opy_ (u"ࠩࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥࡶࡥࡳࡨࡲࡶࡲࠦࡳࡤࡣࡱࠤࢀࢃࠧ૤").format(str(err)))
    bstack1lll11lll1_opy_ = False
  response = bstack11ll11l1ll_opy_(self, driver_command, *args, **kwargs)
  if (bstack11ll1_opy_ (u"ࠪࡶࡴࡨ࡯ࡵࠩ૥") in str(bstack11l1l11ll_opy_).lower() or bstack11ll1_opy_ (u"ࠫࡧ࡫ࡨࡢࡸࡨࠫ૦") in str(bstack11l1l11ll_opy_).lower()) and bstack1l11llll1l_opy_.on():
    try:
      if driver_command == bstack11ll1_opy_ (u"ࠬࡹࡣࡳࡧࡨࡲࡸ࡮࡯ࡵࠩ૧"):
        bstack11lll11l11_opy_.bstack1l1lll1ll_opy_({
            bstack11ll1_opy_ (u"࠭ࡩ࡮ࡣࡪࡩࠬ૨"): response[bstack11ll1_opy_ (u"ࠧࡷࡣ࡯ࡹࡪ࠭૩")],
            bstack11ll1_opy_ (u"ࠨࡶࡨࡷࡹࡥࡲࡶࡰࡢࡹࡺ࡯ࡤࠨ૪"): bstack11lll11l11_opy_.current_test_uuid() if bstack11lll11l11_opy_.current_test_uuid() else bstack1l11llll1l_opy_.current_hook_uuid()
        })
    except:
      pass
  return response
@measure(event_name=EVENTS.bstack11llllll_opy_, stage=STAGE.bstack11l1llll1_opy_, bstack1lll1l1l1_opy_=bstack1ll1l11111_opy_)
def bstack1l111111l1_opy_(self, command_executor,
             desired_capabilities=None, browser_profile=None, proxy=None,
             keep_alive=True, file_detector=None, options=None, *args, **kwargs):
  global CONFIG
  global bstack1l111l111l_opy_
  global bstack111l11l1l_opy_
  global bstack1ll1l11111_opy_
  global bstack1ll1lll1l1_opy_
  global bstack1ll111111_opy_
  global bstack11l1l11ll_opy_
  global bstack1lll1l1l_opy_
  global bstack1lll111ll_opy_
  global bstack11111ll1l_opy_
  global bstack1l11l11ll_opy_
  if os.getenv(bstack11ll1_opy_ (u"ࠩࡅࡗࡤࡇ࠱࠲࡛ࡢࡎ࡜࡚ࠧ૫")) is not None and bstack1l1ll11l1l_opy_.bstack1llll1l11l_opy_(CONFIG) is None:
    CONFIG[bstack11ll1_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠪ૬")] = True
  CONFIG[bstack11ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡖࡈࡐ࠭૭")] = str(bstack11l1l11ll_opy_) + str(__version__)
  bstack1lllll1l1l_opy_ = os.environ[bstack11ll1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡊࡘࡆࡤ࡛ࡕࡊࡆࠪ૮")]
  bstack11l1111l11_opy_ = bstack1l11111ll1_opy_.bstack111lll11l_opy_(CONFIG, bstack11l1l11ll_opy_)
  CONFIG[bstack11ll1_opy_ (u"࠭ࡴࡦࡵࡷ࡬ࡺࡨࡂࡶ࡫࡯ࡨ࡚ࡻࡩࡥࠩ૯")] = bstack1lllll1l1l_opy_
  CONFIG[bstack11ll1_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡖࡲࡰࡦࡸࡧࡹࡓࡡࡱࠩ૰")] = bstack11l1111l11_opy_
  if CONFIG.get(bstack11ll1_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࡐࡲࡷ࡭ࡴࡴࡳࠨ૱"),bstack11ll1_opy_ (u"ࠩࠪ૲")) and bstack11ll1_opy_ (u"ࠪࡶࡴࡨ࡯ࡵࠩ૳") in bstack11l1l11ll_opy_:
    CONFIG[bstack11ll1_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࡓࡵࡺࡩࡰࡰࡶࠫ૴")].pop(bstack11ll1_opy_ (u"ࠬ࡯࡮ࡤ࡮ࡸࡨࡪ࡚ࡡࡨࡵࡌࡲ࡙࡫ࡳࡵ࡫ࡱ࡫ࡘࡩ࡯ࡱࡧࠪ૵"), None)
    CONFIG[bstack11ll1_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࡕࡰࡵ࡫ࡲࡲࡸ࠭૶")].pop(bstack11ll1_opy_ (u"ࠧࡦࡺࡦࡰࡺࡪࡥࡕࡣࡪࡷࡎࡴࡔࡦࡵࡷ࡭ࡳ࡭ࡓࡤࡱࡳࡩࠬ૷"), None)
  command_executor = bstack1l1l11l11_opy_()
  logger.debug(bstack11lll111ll_opy_.format(command_executor))
  proxy = bstack11l1l11ll1_opy_(CONFIG, proxy)
  bstack1l11ll11ll_opy_ = 0 if bstack111l11l1l_opy_ < 0 else bstack111l11l1l_opy_
  try:
    if bstack1ll1lll1l1_opy_ is True:
      bstack1l11ll11ll_opy_ = int(multiprocessing.current_process().name)
    elif bstack1ll111111_opy_ is True:
      bstack1l11ll11ll_opy_ = int(threading.current_thread().name)
  except:
    bstack1l11ll11ll_opy_ = 0
  bstack1l111ll11_opy_ = bstack11l1llll1l_opy_(CONFIG, bstack1l11ll11ll_opy_)
  logger.debug(bstack11l1l1l1ll_opy_.format(str(bstack1l111ll11_opy_)))
  if bstack11ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡌࡰࡥࡤࡰࠬ૸") in CONFIG and bstack1111lll1_opy_(CONFIG[bstack11ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡍࡱࡦࡥࡱ࠭ૹ")]):
    bstack1l111ll1l1_opy_(bstack1l111ll11_opy_)
  if bstack1l1ll11l1l_opy_.bstack1ll11l1ll1_opy_(CONFIG, bstack1l11ll11ll_opy_) and bstack1l1ll11l1l_opy_.bstack11l1lll1_opy_(bstack1l111ll11_opy_, options, desired_capabilities, CONFIG):
    threading.current_thread().a11yPlatform = True
    if (cli.accessibility is None or not cli.accessibility.is_enabled()):
      bstack1l1ll11l1l_opy_.set_capabilities(bstack1l111ll11_opy_, CONFIG)
  if desired_capabilities:
    bstack1ll1lll1ll_opy_ = bstack1l1ll111l_opy_(desired_capabilities)
    bstack1ll1lll1ll_opy_[bstack11ll1_opy_ (u"ࠪࡹࡸ࡫ࡗ࠴ࡅࠪૺ")] = bstack11lll11lll_opy_(CONFIG)
    bstack11l1lll1ll_opy_ = bstack11l1llll1l_opy_(bstack1ll1lll1ll_opy_)
    if bstack11l1lll1ll_opy_:
      bstack1l111ll11_opy_ = update(bstack11l1lll1ll_opy_, bstack1l111ll11_opy_)
    desired_capabilities = None
  if options:
    bstack11lll1l1_opy_(options, bstack1l111ll11_opy_)
  if not options:
    options = bstack111lll1ll_opy_(bstack1l111ll11_opy_)
  bstack1l11l11ll_opy_ = CONFIG.get(bstack11ll1_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧૻ"))[bstack1l11ll11ll_opy_]
  if proxy and bstack1ll1ll1l11_opy_() >= version.parse(bstack11ll1_opy_ (u"ࠬ࠺࠮࠲࠲࠱࠴ࠬૼ")):
    options.proxy(proxy)
  if options and bstack1ll1ll1l11_opy_() >= version.parse(bstack11ll1_opy_ (u"࠭࠳࠯࠺࠱࠴ࠬ૽")):
    desired_capabilities = None
  if (
          not options and not desired_capabilities
  ) or (
          bstack1ll1ll1l11_opy_() < version.parse(bstack11ll1_opy_ (u"ࠧ࠴࠰࠻࠲࠵࠭૾")) and not desired_capabilities
  ):
    desired_capabilities = {}
    desired_capabilities.update(bstack1l111ll11_opy_)
  logger.info(bstack1llll1111_opy_)
  bstack11l11l11ll_opy_.end(EVENTS.bstack1ll111111l_opy_.value, EVENTS.bstack1ll111111l_opy_.value + bstack11ll1_opy_ (u"ࠣ࠼ࡶࡸࡦࡸࡴࠣ૿"), EVENTS.bstack1ll111111l_opy_.value + bstack11ll1_opy_ (u"ࠤ࠽ࡩࡳࡪࠢ଀"), status=True, failure=None, test_name=bstack1ll1l11111_opy_)
  if bstack11ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡣࡵࡸ࡯ࡧ࡫࡯ࡩࠬଁ") in kwargs:
    del kwargs[bstack11ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡤࡶࡲࡰࡨ࡬ࡰࡪ࠭ଂ")]
  try:
    if bstack1ll1ll1l11_opy_() >= version.parse(bstack11ll1_opy_ (u"ࠬ࠺࠮࠲࠲࠱࠴ࠬଃ")):
      bstack1lll1l1l_opy_(self, command_executor=command_executor,
                options=options, keep_alive=keep_alive, file_detector=file_detector, *args, **kwargs)
    elif bstack1ll1ll1l11_opy_() >= version.parse(bstack11ll1_opy_ (u"࠭࠳࠯࠺࠱࠴ࠬ଄")):
      bstack1lll1l1l_opy_(self, command_executor=command_executor,
                desired_capabilities=desired_capabilities, options=options,
                browser_profile=browser_profile, proxy=proxy,
                keep_alive=keep_alive, file_detector=file_detector)
    elif bstack1ll1ll1l11_opy_() >= version.parse(bstack11ll1_opy_ (u"ࠧ࠳࠰࠸࠷࠳࠶ࠧଅ")):
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
    logger.error(bstack11l111l1l_opy_.format(bstack11ll1_opy_ (u"ࠨࡄࡵࡳࡼࡹࡥࡳࡕࡷࡥࡨࡱࠧଆ"), str(bstack11l111lll1_opy_)))
    raise bstack11l111lll1_opy_
  if bstack1l1ll11l1l_opy_.bstack1ll11l1ll1_opy_(CONFIG, bstack1l11ll11ll_opy_) and bstack1l1ll11l1l_opy_.bstack11l1lll1_opy_(self.caps, options, desired_capabilities):
    if CONFIG[bstack11ll1_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡑࡴࡲࡨࡺࡩࡴࡎࡣࡳࠫଇ")][bstack11ll1_opy_ (u"ࠪࡥࡵࡶ࡟ࡢࡷࡷࡳࡲࡧࡴࡦࠩଈ")] == True:
      threading.current_thread().appA11yPlatform = True
      if cli.accessibility is None or not cli.accessibility.is_enabled():
        bstack1l1ll11l1l_opy_.set_capabilities(bstack1l111ll11_opy_, CONFIG)
  try:
    bstack111lll1111_opy_ = bstack11ll1_opy_ (u"ࠫࠬଉ")
    if bstack1ll1ll1l11_opy_() >= version.parse(bstack11ll1_opy_ (u"ࠬ࠺࠮࠱࠰࠳ࡦ࠶࠭ଊ")):
      if self.caps is not None:
        bstack111lll1111_opy_ = self.caps.get(bstack11ll1_opy_ (u"ࠨ࡯ࡱࡶ࡬ࡱࡦࡲࡈࡶࡤࡘࡶࡱࠨଋ"))
    else:
      if self.capabilities is not None:
        bstack111lll1111_opy_ = self.capabilities.get(bstack11ll1_opy_ (u"ࠢࡰࡲࡷ࡭ࡲࡧ࡬ࡉࡷࡥ࡙ࡷࡲࠢଌ"))
    if bstack111lll1111_opy_:
      bstack1l1ll111l1_opy_(bstack111lll1111_opy_)
      if bstack1ll1ll1l11_opy_() <= version.parse(bstack11ll1_opy_ (u"ࠨ࠵࠱࠵࠸࠴࠰ࠨ଍")):
        self.command_executor._url = bstack11ll1_opy_ (u"ࠤ࡫ࡸࡹࡶ࠺࠰࠱ࠥ଎") + bstack1l1ll11ll1_opy_ + bstack11ll1_opy_ (u"ࠥ࠾࠽࠶࠯ࡸࡦ࠲࡬ࡺࡨࠢଏ")
      else:
        self.command_executor._url = bstack11ll1_opy_ (u"ࠦ࡭ࡺࡴࡱࡵ࠽࠳࠴ࠨଐ") + bstack111lll1111_opy_ + bstack11ll1_opy_ (u"ࠧ࠵ࡷࡥ࠱࡫ࡹࡧࠨ଑")
      logger.debug(bstack1l1111lll1_opy_.format(bstack111lll1111_opy_))
    else:
      logger.debug(bstack1lllll11_opy_.format(bstack11ll1_opy_ (u"ࠨࡏࡱࡶ࡬ࡱࡦࡲࠠࡉࡷࡥࠤࡳࡵࡴࠡࡨࡲࡹࡳࡪࠢ଒")))
  except Exception as e:
    logger.debug(bstack1lllll11_opy_.format(e))
  if bstack11ll1_opy_ (u"ࠧࡳࡱࡥࡳࡹ࠭ଓ") in bstack11l1l11ll_opy_:
    bstack11l1l1l1_opy_(bstack111l11l1l_opy_, bstack11111ll1l_opy_)
  bstack1l111l111l_opy_ = self.session_id
  if bstack11ll1_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࠨଔ") in bstack11l1l11ll_opy_ or bstack11ll1_opy_ (u"ࠩࡥࡩ࡭ࡧࡶࡦࠩକ") in bstack11l1l11ll_opy_ or bstack11ll1_opy_ (u"ࠪࡶࡴࡨ࡯ࡵࠩଖ") in bstack11l1l11ll_opy_:
    threading.current_thread().bstackSessionId = self.session_id
    threading.current_thread().bstackSessionDriver = self
    threading.current_thread().bstackTestErrorMessages = []
  bstack1ll1111ll1_opy_ = getattr(threading.current_thread(), bstack11ll1_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮ࡘࡪࡹࡴࡎࡧࡷࡥࠬଗ"), None)
  if bstack11ll1_opy_ (u"ࠬࡨࡥࡩࡣࡹࡩࠬଘ") in bstack11l1l11ll_opy_ or bstack11ll1_opy_ (u"࠭ࡲࡰࡤࡲࡸࠬଙ") in bstack11l1l11ll_opy_:
    bstack11lll11l11_opy_.bstack1ll1lll111_opy_(self)
  if bstack11ll1_opy_ (u"ࠧࡱࡻࡷࡩࡸࡺࠧଚ") in bstack11l1l11ll_opy_ and bstack1ll1111ll1_opy_ and bstack1ll1111ll1_opy_.get(bstack11ll1_opy_ (u"ࠨࡵࡷࡥࡹࡻࡳࠨଛ"), bstack11ll1_opy_ (u"ࠩࠪଜ")) == bstack11ll1_opy_ (u"ࠪࡴࡪࡴࡤࡪࡰࡪࠫଝ"):
    bstack11lll11l11_opy_.bstack1ll1lll111_opy_(self)
  with bstack1l1lll11_opy_:
    bstack1lll111ll_opy_.append(self)
  if bstack11ll1_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧଞ") in CONFIG and bstack11ll1_opy_ (u"ࠬࡹࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧࠪଟ") in CONFIG[bstack11ll1_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩଠ")][bstack1l11ll11ll_opy_]:
    bstack1ll1l11111_opy_ = CONFIG[bstack11ll1_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪଡ")][bstack1l11ll11ll_opy_][bstack11ll1_opy_ (u"ࠨࡵࡨࡷࡸ࡯࡯࡯ࡐࡤࡱࡪ࠭ଢ")]
  logger.debug(bstack1l111l11l1_opy_.format(bstack1l111l111l_opy_))
try:
  try:
    import Browser
    from subprocess import Popen
    from browserstack_sdk.__init__ import bstack1l11lllll_opy_
    def bstack11lllll1_opy_(self, args, bufsize=-1, executable=None,
              stdin=None, stdout=None, stderr=None,
              preexec_fn=None, close_fds=True,
              shell=False, cwd=None, env=None, universal_newlines=None,
              startupinfo=None, creationflags=0,
              restore_signals=True, start_new_session=False,
              pass_fds=(), *, user=None, group=None, extra_groups=None,
              encoding=None, errors=None, text=None, umask=-1, pipesize=-1):
      global CONFIG
      global bstack1lll1ll1_opy_
      if(bstack11ll1_opy_ (u"ࠤ࡬ࡲࡩ࡫ࡸ࠯࡬ࡶࠦଣ") in args[1]):
        with open(os.path.join(os.path.expanduser(bstack11ll1_opy_ (u"ࠪࢂࠬତ")), bstack11ll1_opy_ (u"ࠫ࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࠫଥ"), bstack11ll1_opy_ (u"ࠬ࠴ࡳࡦࡵࡶ࡭ࡴࡴࡩࡥࡵ࠱ࡸࡽࡺࠧଦ")), bstack11ll1_opy_ (u"࠭ࡷࠨଧ")) as fp:
          fp.write(bstack11ll1_opy_ (u"ࠢࠣନ"))
        if(not os.path.exists(os.path.join(os.path.dirname(args[1]), bstack11ll1_opy_ (u"ࠣ࡫ࡱࡨࡪࡾ࡟ࡣࡵࡷࡥࡨࡱ࠮࡫ࡵࠥ଩")))):
          with open(args[1], bstack11ll1_opy_ (u"ࠩࡵࠫପ")) as f:
            lines = f.readlines()
            index = next((i for i, line in enumerate(lines) if bstack11ll1_opy_ (u"ࠪࡥࡸࡿ࡮ࡤࠢࡩࡹࡳࡩࡴࡪࡱࡱࠤࡤࡴࡥࡸࡒࡤ࡫ࡪ࠮ࡣࡰࡰࡷࡩࡽࡺࠬࠡࡲࡤ࡫ࡪࠦ࠽ࠡࡸࡲ࡭ࡩࠦ࠰ࠪࠩଫ") in line), None)
            if index is not None:
                lines.insert(index+2, bstack1ll111l1_opy_)
            if bstack11ll1_opy_ (u"ࠫࡹࡻࡲࡣࡱࡖࡧࡦࡲࡥࠨବ") in CONFIG and str(CONFIG[bstack11ll1_opy_ (u"ࠬࡺࡵࡳࡤࡲࡗࡨࡧ࡬ࡦࠩଭ")]).lower() != bstack11ll1_opy_ (u"࠭ࡦࡢ࡮ࡶࡩࠬମ"):
                bstack1l1ll1l111_opy_ = bstack1l11lllll_opy_()
                bstack1l1l111ll1_opy_ = bstack11ll1_opy_ (u"ࠧࠨࠩࠍ࠳࠯ࠦ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࠣ࠮࠴ࠐࡣࡰࡰࡶࡸࠥࡨࡳࡵࡣࡦ࡯ࡤࡶࡡࡵࡪࠣࡁࠥࡶࡲࡰࡥࡨࡷࡸ࠴ࡡࡳࡩࡹ࡟ࡵࡸ࡯ࡤࡧࡶࡷ࠳ࡧࡲࡨࡸ࠱ࡰࡪࡴࡧࡵࡪࠣ࠱ࠥ࠹࡝࠼ࠌࡦࡳࡳࡹࡴࠡࡤࡶࡸࡦࡩ࡫ࡠࡥࡤࡴࡸࠦ࠽ࠡࡲࡵࡳࡨ࡫ࡳࡴ࠰ࡤࡶ࡬ࡼ࡛ࡱࡴࡲࡧࡪࡹࡳ࠯ࡣࡵ࡫ࡻ࠴࡬ࡦࡰࡪࡸ࡭ࠦ࠭ࠡ࠳ࡠ࠿ࠏࡩ࡯࡯ࡵࡷࠤࡵࡥࡩ࡯ࡦࡨࡼࠥࡃࠠࡱࡴࡲࡧࡪࡹࡳ࠯ࡣࡵ࡫ࡻࡡࡰࡳࡱࡦࡩࡸࡹ࠮ࡢࡴࡪࡺ࠳ࡲࡥ࡯ࡩࡷ࡬ࠥ࠳ࠠ࠳࡟࠾ࠎࡵࡸ࡯ࡤࡧࡶࡷ࠳ࡧࡲࡨࡸࠣࡁࠥࡶࡲࡰࡥࡨࡷࡸ࠴ࡡࡳࡩࡹ࠲ࡸࡲࡩࡤࡧࠫ࠴࠱ࠦࡰࡳࡱࡦࡩࡸࡹ࠮ࡢࡴࡪࡺ࠳ࡲࡥ࡯ࡩࡷ࡬ࠥ࠳ࠠ࠴ࠫ࠾ࠎࡨࡵ࡮ࡴࡶࠣ࡭ࡲࡶ࡯ࡳࡶࡢࡴࡱࡧࡹࡸࡴ࡬࡫࡭ࡺ࠴ࡠࡤࡶࡸࡦࡩ࡫ࠡ࠿ࠣࡶࡪࡷࡵࡪࡴࡨࠬࠧࡶ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵࠤࠬ࠿ࠏ࡯࡭ࡱࡱࡵࡸࡤࡶ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵ࠶ࡢࡦࡸࡺࡡࡤ࡭࠱ࡧ࡭ࡸ࡯࡮࡫ࡸࡱ࠳ࡲࡡࡶࡰࡦ࡬ࠥࡃࠠࡢࡵࡼࡲࡨࠦࠨ࡭ࡣࡸࡲࡨ࡮ࡏࡱࡶ࡬ࡳࡳࡹࠩࠡ࠿ࡁࠤࢀࢁࠊࠡࠢ࡯ࡩࡹࠦࡣࡢࡲࡶ࠿ࠏࠦࠠࡵࡴࡼࠤࢀࢁࠊࠡࠢࠣࠤࡨࡧࡰࡴࠢࡀࠤࡏ࡙ࡏࡏ࠰ࡳࡥࡷࡹࡥࠩࡤࡶࡸࡦࡩ࡫ࡠࡥࡤࡴࡸ࠯࠻ࠋࠢࠣࢁࢂࠦࡣࡢࡶࡦ࡬ࠥ࠮ࡥࡹࠫࠣࡿࢀࠐࠠࠡࠢࠣࡧࡴࡴࡳࡰ࡮ࡨ࠲ࡪࡸࡲࡰࡴࠫࠦࡋࡧࡩ࡭ࡧࡧࠤࡹࡵࠠࡱࡣࡵࡷࡪࠦࡣࡢࡲࡤࡦ࡮ࡲࡩࡵ࡫ࡨࡷ࠿ࠨࠬࠡࡧࡻ࠭ࡀࠐࠠࠡࡿࢀࠎࠥࠦࡲࡦࡶࡸࡶࡳࠦࡡࡸࡣ࡬ࡸࠥ࡯࡭ࡱࡱࡵࡸࡤࡶ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵ࠶ࡢࡦࡸࡺࡡࡤ࡭࠱ࡧ࡭ࡸ࡯࡮࡫ࡸࡱ࠳ࡩ࡯࡯ࡰࡨࡧࡹ࠮ࡻࡼࠌࠣࠤࠥࠦࡷࡴࡇࡱࡨࡵࡵࡩ࡯ࡶ࠽ࠤࠬࢁࡣࡥࡲࡘࡶࡱࢃࠧࠡ࠭ࠣࡩࡳࡩ࡯ࡥࡧࡘࡖࡎࡉ࡯࡮ࡲࡲࡲࡪࡴࡴࠩࡌࡖࡓࡓ࠴ࡳࡵࡴ࡬ࡲ࡬࡯ࡦࡺࠪࡦࡥࡵࡹࠩࠪ࠮ࠍࠤࠥࠦࠠ࠯࠰࠱ࡰࡦࡻ࡮ࡤࡪࡒࡴࡹ࡯࡯࡯ࡵࠍࠤࠥࢃࡽࠪ࠽ࠍࢁࢂࡁࠊ࠰ࠬࠣࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃࠠࠫ࠱ࠍࠫࠬ࠭ଯ").format(bstack1l1ll1l111_opy_=bstack1l1ll1l111_opy_)
            lines.insert(1, bstack1l1l111ll1_opy_)
            f.seek(0)
            with open(os.path.join(os.path.dirname(args[1]), bstack11ll1_opy_ (u"ࠣ࡫ࡱࡨࡪࡾ࡟ࡣࡵࡷࡥࡨࡱ࠮࡫ࡵࠥର")), bstack11ll1_opy_ (u"ࠩࡺࠫ଱")) as bstack1lll1l1111_opy_:
              bstack1lll1l1111_opy_.writelines(lines)
        CONFIG[bstack11ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡕࡇࡏࠬଲ")] = str(bstack11l1l11ll_opy_) + str(__version__)
        bstack1lllll1l1l_opy_ = os.environ[bstack11ll1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡉࡗࡅࡣ࡚࡛ࡉࡅࠩଳ")]
        bstack11l1111l11_opy_ = bstack1l11111ll1_opy_.bstack111lll11l_opy_(CONFIG, bstack11l1l11ll_opy_)
        CONFIG[bstack11ll1_opy_ (u"ࠬࡺࡥࡴࡶ࡫ࡹࡧࡈࡵࡪ࡮ࡧ࡙ࡺ࡯ࡤࠨ଴")] = bstack1lllll1l1l_opy_
        CONFIG[bstack11ll1_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡕࡸ࡯ࡥࡷࡦࡸࡒࡧࡰࠨଵ")] = bstack11l1111l11_opy_
        bstack1l11ll11ll_opy_ = 0 if bstack111l11l1l_opy_ < 0 else bstack111l11l1l_opy_
        try:
          if bstack1ll1lll1l1_opy_ is True:
            bstack1l11ll11ll_opy_ = int(multiprocessing.current_process().name)
          elif bstack1ll111111_opy_ is True:
            bstack1l11ll11ll_opy_ = int(threading.current_thread().name)
        except:
          bstack1l11ll11ll_opy_ = 0
        CONFIG[bstack11ll1_opy_ (u"ࠢࡶࡵࡨ࡛࠸ࡉࠢଶ")] = False
        CONFIG[bstack11ll1_opy_ (u"ࠣ࡫ࡶࡔࡱࡧࡹࡸࡴ࡬࡫࡭ࡺࠢଷ")] = True
        bstack1l111ll11_opy_ = bstack11l1llll1l_opy_(CONFIG, bstack1l11ll11ll_opy_)
        logger.debug(bstack11l1l1l1ll_opy_.format(str(bstack1l111ll11_opy_)))
        if CONFIG.get(bstack11ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡍࡱࡦࡥࡱ࠭ସ")):
          bstack1l111ll1l1_opy_(bstack1l111ll11_opy_)
        if bstack11ll1_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ହ") in CONFIG and bstack11ll1_opy_ (u"ࠫࡸ࡫ࡳࡴ࡫ࡲࡲࡓࡧ࡭ࡦࠩ଺") in CONFIG[bstack11ll1_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨ଻")][bstack1l11ll11ll_opy_]:
          bstack1ll1l11111_opy_ = CONFIG[bstack11ll1_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴ଼ࠩ")][bstack1l11ll11ll_opy_][bstack11ll1_opy_ (u"ࠧࡴࡧࡶࡷ࡮ࡵ࡮ࡏࡣࡰࡩࠬଽ")]
        args.append(os.path.join(os.path.expanduser(bstack11ll1_opy_ (u"ࠨࢀࠪା")), bstack11ll1_opy_ (u"ࠩ࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࠩି"), bstack11ll1_opy_ (u"ࠪ࠲ࡸ࡫ࡳࡴ࡫ࡲࡲ࡮ࡪࡳ࠯ࡶࡻࡸࠬୀ")))
        args.append(str(threading.get_ident()))
        args.append(json.dumps(bstack1l111ll11_opy_))
        args[1] = os.path.join(os.path.dirname(args[1]), bstack11ll1_opy_ (u"ࠦ࡮ࡴࡤࡦࡺࡢࡦࡸࡺࡡࡤ࡭࠱࡮ࡸࠨୁ"))
      bstack1lll1ll1_opy_ = True
      return bstack1l1ll11l_opy_(self, args, bufsize=bufsize, executable=executable,
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
  def bstack1lll11lll_opy_(self,
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
    global bstack111l11l1l_opy_
    global bstack1ll1l11111_opy_
    global bstack1ll1lll1l1_opy_
    global bstack1ll111111_opy_
    global bstack11l1l11ll_opy_
    CONFIG[bstack11ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡗࡉࡑࠧୂ")] = str(bstack11l1l11ll_opy_) + str(__version__)
    bstack1lllll1l1l_opy_ = os.environ[bstack11ll1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡕࡖࡋࡇࠫୃ")]
    bstack11l1111l11_opy_ = bstack1l11111ll1_opy_.bstack111lll11l_opy_(CONFIG, bstack11l1l11ll_opy_)
    CONFIG[bstack11ll1_opy_ (u"ࠧࡵࡧࡶࡸ࡭ࡻࡢࡃࡷ࡬ࡰࡩ࡛ࡵࡪࡦࠪୄ")] = bstack1lllll1l1l_opy_
    CONFIG[bstack11ll1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡐࡳࡱࡧࡹࡨࡺࡍࡢࡲࠪ୅")] = bstack11l1111l11_opy_
    bstack1l11ll11ll_opy_ = 0 if bstack111l11l1l_opy_ < 0 else bstack111l11l1l_opy_
    try:
      if bstack1ll1lll1l1_opy_ is True:
        bstack1l11ll11ll_opy_ = int(multiprocessing.current_process().name)
      elif bstack1ll111111_opy_ is True:
        bstack1l11ll11ll_opy_ = int(threading.current_thread().name)
    except:
      bstack1l11ll11ll_opy_ = 0
    CONFIG[bstack11ll1_opy_ (u"ࠤ࡬ࡷࡕࡲࡡࡺࡹࡵ࡭࡬࡮ࡴࠣ୆")] = True
    bstack1l111ll11_opy_ = bstack11l1llll1l_opy_(CONFIG, bstack1l11ll11ll_opy_)
    logger.debug(bstack11l1l1l1ll_opy_.format(str(bstack1l111ll11_opy_)))
    if CONFIG.get(bstack11ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡎࡲࡧࡦࡲࠧେ")):
      bstack1l111ll1l1_opy_(bstack1l111ll11_opy_)
    if bstack11ll1_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧୈ") in CONFIG and bstack11ll1_opy_ (u"ࠬࡹࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧࠪ୉") in CONFIG[bstack11ll1_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩ୊")][bstack1l11ll11ll_opy_]:
      bstack1ll1l11111_opy_ = CONFIG[bstack11ll1_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪୋ")][bstack1l11ll11ll_opy_][bstack11ll1_opy_ (u"ࠨࡵࡨࡷࡸ࡯࡯࡯ࡐࡤࡱࡪ࠭ୌ")]
    import urllib
    import json
    if bstack11ll1_opy_ (u"ࠩࡷࡹࡷࡨ࡯ࡔࡥࡤࡰࡪ୍࠭") in CONFIG and str(CONFIG[bstack11ll1_opy_ (u"ࠪࡸࡺࡸࡢࡰࡕࡦࡥࡱ࡫ࠧ୎")]).lower() != bstack11ll1_opy_ (u"ࠫ࡫ࡧ࡬ࡴࡧࠪ୏"):
        bstack1l1l1111ll_opy_ = bstack1l11lllll_opy_()
        bstack1l1ll1l111_opy_ = bstack1l1l1111ll_opy_ + urllib.parse.quote(json.dumps(bstack1l111ll11_opy_))
    else:
        bstack1l1ll1l111_opy_ = bstack11ll1_opy_ (u"ࠬࡽࡳࡴ࠼࠲࠳ࡨࡪࡰ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡤࡱࡰ࠳ࡵࡲࡡࡺࡹࡵ࡭࡬࡮ࡴࡀࡥࡤࡴࡸࡃࠧ୐") + urllib.parse.quote(json.dumps(bstack1l111ll11_opy_))
    browser = self.connect(bstack1l1ll1l111_opy_)
    return browser
except Exception as e:
    pass
def bstack1l11lllll1_opy_():
    global bstack1lll1ll1_opy_
    global bstack11l1l11ll_opy_
    global CONFIG
    try:
        from playwright._impl._browser_type import BrowserType
        from bstack_utils.helper import bstack11ll1l1ll_opy_
        global bstack1l1l1ll1l_opy_
        if not bstack1llll1l1_opy_:
          global bstack11l1llll11_opy_
          if not bstack11l1llll11_opy_:
            from bstack_utils.helper import bstack1l11l1l1_opy_, bstack11ll111ll1_opy_, bstack11111llll_opy_
            bstack11l1llll11_opy_ = bstack1l11l1l1_opy_()
            bstack11ll111ll1_opy_(bstack11l1l11ll_opy_)
            bstack11l1111l11_opy_ = bstack1l11111ll1_opy_.bstack111lll11l_opy_(CONFIG, bstack11l1l11ll_opy_)
            bstack1l1l1ll1l_opy_.bstack11l1l11l_opy_(bstack11ll1_opy_ (u"ࠨࡐࡍࡃ࡜࡛ࡗࡏࡇࡉࡖࡢࡔࡗࡕࡄࡖࡅࡗࡣࡒࡇࡐࠣ୑"), bstack11l1111l11_opy_)
          BrowserType.connect = bstack11ll1l1ll_opy_
          return
        BrowserType.launch = bstack1lll11lll_opy_
        bstack1lll1ll1_opy_ = True
    except Exception as e:
        pass
    try:
      import Browser
      from subprocess import Popen
      Popen.__init__ = bstack11lllll1_opy_
      bstack1lll1ll1_opy_ = True
    except Exception as e:
      pass
def bstack1ll1l111ll_opy_(context, bstack1111l1ll_opy_):
  try:
    context.page.evaluate(bstack11ll1_opy_ (u"ࠢࡠࠢࡀࡂࠥࢁࡽࠣ୒"), bstack11ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࡿࠧࡧࡣࡵ࡫ࡲࡲࠧࡀࠠࠣࡵࡨࡸࡘ࡫ࡳࡴ࡫ࡲࡲࡓࡧ࡭ࡦࠤ࠯ࠤࠧࡧࡲࡨࡷࡰࡩࡳࡺࡳࠣ࠼ࠣࡿࠧࡴࡡ࡮ࡧࠥ࠾ࠬ୓")+ json.dumps(bstack1111l1ll_opy_) + bstack11ll1_opy_ (u"ࠤࢀࢁࠧ୔"))
  except Exception as e:
    logger.debug(bstack11ll1_opy_ (u"ࠥࡩࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡩ࡯ࠢࡳࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹࠦࡳࡦࡵࡶ࡭ࡴࡴࠠ࡯ࡣࡰࡩࠥࢁࡽ࠻ࠢࡾࢁࠧ୕").format(str(e), traceback.format_exc()))
def bstack1l111l111_opy_(context, message, level):
  try:
    context.page.evaluate(bstack11ll1_opy_ (u"ࠦࡤࠦ࠽࠿ࠢࡾࢁࠧୖ"), bstack11ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࡼࠤࡤࡧࡹ࡯࡯࡯ࠤ࠽ࠤࠧࡧ࡮࡯ࡱࡷࡥࡹ࡫ࠢ࠭ࠢࠥࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸࠨ࠺ࠡࡽࠥࡨࡦࡺࡡࠣ࠼ࠪୗ") + json.dumps(message) + bstack11ll1_opy_ (u"࠭ࠬࠣ࡮ࡨࡺࡪࡲࠢ࠻ࠩ୘") + json.dumps(level) + bstack11ll1_opy_ (u"ࠧࡾࡿࠪ୙"))
  except Exception as e:
    logger.debug(bstack11ll1_opy_ (u"ࠣࡧࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡱ࡮ࡤࡽࡼࡸࡩࡨࡪࡷࠤࡦࡴ࡮ࡰࡶࡤࡸ࡮ࡵ࡮ࠡࡽࢀ࠾ࠥࢁࡽࠣ୚").format(str(e), traceback.format_exc()))
@measure(event_name=EVENTS.bstack11llllll11_opy_, stage=STAGE.bstack11l1llll1_opy_, bstack1lll1l1l1_opy_=bstack1ll1l11111_opy_)
def bstack11lll1111_opy_(self, url):
  global bstack1llll1llll_opy_
  try:
    bstack11ll1ll1ll_opy_(url)
  except Exception as err:
    logger.debug(bstack1l1ll11l1_opy_.format(str(err)))
  try:
    bstack1llll1llll_opy_(self, url)
  except Exception as e:
    try:
      bstack1ll111l1ll_opy_ = str(e)
      if any(err_msg in bstack1ll111l1ll_opy_ for err_msg in bstack1ll11l11l_opy_):
        bstack11ll1ll1ll_opy_(url, True)
    except Exception as err:
      logger.debug(bstack1l1ll11l1_opy_.format(str(err)))
    raise e
def bstack1l11l11lll_opy_(self):
  global bstack1l1lll1l11_opy_
  bstack1l1lll1l11_opy_ = self
  return
def bstack11llll11l_opy_(self):
  global bstack1lll1111_opy_
  bstack1lll1111_opy_ = self
  return
def bstack11lll11111_opy_(test_name, bstack1111lllll_opy_):
  global CONFIG
  if percy.bstack1lll1l11l1_opy_() == bstack11ll1_opy_ (u"ࠤࡷࡶࡺ࡫ࠢ୛"):
    bstack1l1l1111l1_opy_ = os.path.relpath(bstack1111lllll_opy_, start=os.getcwd())
    suite_name, _ = os.path.splitext(bstack1l1l1111l1_opy_)
    bstack1lll1l1l1_opy_ = suite_name + bstack11ll1_opy_ (u"ࠥ࠱ࠧଡ଼") + test_name
    threading.current_thread().percySessionName = bstack1lll1l1l1_opy_
def bstack111ll1l1l_opy_(self, test, *args, **kwargs):
  global bstack11ll1111_opy_
  test_name = None
  bstack1111lllll_opy_ = None
  if test:
    test_name = str(test.name)
    bstack1111lllll_opy_ = str(test.source)
  bstack11lll11111_opy_(test_name, bstack1111lllll_opy_)
  bstack11ll1111_opy_(self, test, *args, **kwargs)
@measure(event_name=EVENTS.bstack11llll1l_opy_, stage=STAGE.bstack11l1llll1_opy_, bstack1lll1l1l1_opy_=bstack1ll1l11111_opy_)
def bstack1l11l1ll1l_opy_(driver, bstack1lll1l1l1_opy_):
  if not bstack1111ll1l1_opy_ and bstack1lll1l1l1_opy_:
      bstack111111ll_opy_ = {
          bstack11ll1_opy_ (u"ࠫࡦࡩࡴࡪࡱࡱࠫଢ଼"): bstack11ll1_opy_ (u"ࠬࡹࡥࡵࡕࡨࡷࡸ࡯࡯࡯ࡐࡤࡱࡪ࠭୞"),
          bstack11ll1_opy_ (u"࠭ࡡࡳࡩࡸࡱࡪࡴࡴࡴࠩୟ"): {
              bstack11ll1_opy_ (u"ࠧ࡯ࡣࡰࡩࠬୠ"): bstack1lll1l1l1_opy_
          }
      }
      bstack1l11ll111l_opy_ = bstack11ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࡿࢂ࠭ୡ").format(json.dumps(bstack111111ll_opy_))
      driver.execute_script(bstack1l11ll111l_opy_)
  if bstack1l11l11l11_opy_:
      bstack11l1lll1l_opy_ = {
          bstack11ll1_opy_ (u"ࠩࡤࡧࡹ࡯࡯࡯ࠩୢ"): bstack11ll1_opy_ (u"ࠪࡥࡳࡴ࡯ࡵࡣࡷࡩࠬୣ"),
          bstack11ll1_opy_ (u"ࠫࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠧ୤"): {
              bstack11ll1_opy_ (u"ࠬࡪࡡࡵࡣࠪ୥"): bstack1lll1l1l1_opy_ + bstack11ll1_opy_ (u"࠭ࠠࡱࡣࡶࡷࡪࡪࠡࠨ୦"),
              bstack11ll1_opy_ (u"ࠧ࡭ࡧࡹࡩࡱ࠭୧"): bstack11ll1_opy_ (u"ࠨ࡫ࡱࡪࡴ࠭୨")
          }
      }
      if bstack1l11l11l11_opy_.status == bstack11ll1_opy_ (u"ࠩࡓࡅࡘ࡙ࠧ୩"):
          bstack11l1l111ll_opy_ = bstack11ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡨࡼࡪࡩࡵࡵࡱࡵ࠾ࠥࢁࡽࠨ୪").format(json.dumps(bstack11l1lll1l_opy_))
          driver.execute_script(bstack11l1l111ll_opy_)
          bstack1ll11ll1ll_opy_(driver, bstack11ll1_opy_ (u"ࠫࡵࡧࡳࡴࡧࡧࠫ୫"))
      elif bstack1l11l11l11_opy_.status == bstack11ll1_opy_ (u"ࠬࡌࡁࡊࡎࠪ୬"):
          reason = bstack11ll1_opy_ (u"ࠨࠢ୭")
          bstack11lll1ll11_opy_ = bstack1lll1l1l1_opy_ + bstack11ll1_opy_ (u"ࠧࠡࡨࡤ࡭ࡱ࡫ࡤࠨ୮")
          if bstack1l11l11l11_opy_.message:
              reason = str(bstack1l11l11l11_opy_.message)
              bstack11lll1ll11_opy_ = bstack11lll1ll11_opy_ + bstack11ll1_opy_ (u"ࠨࠢࡺ࡭ࡹ࡮ࠠࡦࡴࡵࡳࡷࡀࠠࠨ୯") + reason
          bstack11l1lll1l_opy_[bstack11ll1_opy_ (u"ࠩࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠬ୰")] = {
              bstack11ll1_opy_ (u"ࠪࡰࡪࡼࡥ࡭ࠩୱ"): bstack11ll1_opy_ (u"ࠫࡪࡸࡲࡰࡴࠪ୲"),
              bstack11ll1_opy_ (u"ࠬࡪࡡࡵࡣࠪ୳"): bstack11lll1ll11_opy_
          }
          bstack11l1l111ll_opy_ = bstack11ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤ࡫ࡸࡦࡥࡸࡸࡴࡸ࠺ࠡࡽࢀࠫ୴").format(json.dumps(bstack11l1lll1l_opy_))
          driver.execute_script(bstack11l1l111ll_opy_)
          bstack1ll11ll1ll_opy_(driver, bstack11ll1_opy_ (u"ࠧࡧࡣ࡬ࡰࡪࡪࠧ୵"), reason)
          bstack11l1l11l11_opy_(reason, str(bstack1l11l11l11_opy_), str(bstack111l11l1l_opy_), logger)
@measure(event_name=EVENTS.bstack1111l11l1_opy_, stage=STAGE.bstack11l1llll1_opy_, bstack1lll1l1l1_opy_=bstack1ll1l11111_opy_)
def bstack1l1ll1lll1_opy_(driver, test):
  if percy.bstack1lll1l11l1_opy_() == bstack11ll1_opy_ (u"ࠣࡶࡵࡹࡪࠨ୶") and percy.bstack11l11lll1_opy_() == bstack11ll1_opy_ (u"ࠤࡷࡩࡸࡺࡣࡢࡵࡨࠦ୷"):
      bstack11lll11ll_opy_ = bstack1lll11l1l_opy_(threading.current_thread(), bstack11ll1_opy_ (u"ࠪࡴࡪࡸࡣࡺࡕࡨࡷࡸ࡯࡯࡯ࡐࡤࡱࡪ࠭୸"), None)
      bstack1l1lllll_opy_(driver, bstack11lll11ll_opy_, test)
  if (bstack1lll11l1l_opy_(threading.current_thread(), bstack11ll1_opy_ (u"ࠫ࡮ࡹࡁ࠲࠳ࡼࡘࡪࡹࡴࠨ୹"), None) and
      bstack1lll11l1l_opy_(threading.current_thread(), bstack11ll1_opy_ (u"ࠬࡧ࠱࠲ࡻࡓࡰࡦࡺࡦࡰࡴࡰࠫ୺"), None)) or (
      bstack1lll11l1l_opy_(threading.current_thread(), bstack11ll1_opy_ (u"࠭ࡩࡴࡃࡳࡴࡆ࠷࠱ࡺࡖࡨࡷࡹ࠭୻"), None) and
      bstack1lll11l1l_opy_(threading.current_thread(), bstack11ll1_opy_ (u"ࠧࡢࡲࡳࡅ࠶࠷ࡹࡑ࡮ࡤࡸ࡫ࡵࡲ࡮ࠩ୼"), None)):
      logger.info(bstack11ll1_opy_ (u"ࠣࡃࡸࡸࡴࡳࡡࡵࡧࠣࡸࡪࡹࡴࠡࡥࡤࡷࡪࠦࡥࡹࡧࡦࡹࡹ࡯࡯࡯ࠢ࡫ࡥࡸࠦࡥ࡯ࡦࡨࡨ࠳ࠦࡐࡳࡱࡦࡩࡸࡹࡩ࡯ࡩࠣࡪࡴࡸࠠࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡵࡧࡶࡸ࡮ࡴࡧࠡ࡫ࡶࠤࡺࡴࡤࡦࡴࡺࡥࡾ࠴ࠠࠣ୽"))
      bstack1l1ll11l1l_opy_.bstack1lll1111ll_opy_(driver, name=test.name, path=test.source)
def bstack11l1ll11l1_opy_(test, bstack1lll1l1l1_opy_):
    try:
      bstack1ll11l1l1l_opy_ = datetime.datetime.now()
      data = {}
      if test:
        data[bstack11ll1_opy_ (u"ࠩࡱࡥࡲ࡫ࠧ୾")] = bstack1lll1l1l1_opy_
      if bstack1l11l11l11_opy_:
        if bstack1l11l11l11_opy_.status == bstack11ll1_opy_ (u"ࠪࡔࡆ࡙ࡓࠨ୿"):
          data[bstack11ll1_opy_ (u"ࠫࡸࡺࡡࡵࡷࡶࠫ஀")] = bstack11ll1_opy_ (u"ࠬࡶࡡࡴࡵࡨࡨࠬ஁")
        elif bstack1l11l11l11_opy_.status == bstack11ll1_opy_ (u"࠭ࡆࡂࡋࡏࠫஂ"):
          data[bstack11ll1_opy_ (u"ࠧࡴࡶࡤࡸࡺࡹࠧஃ")] = bstack11ll1_opy_ (u"ࠨࡨࡤ࡭ࡱ࡫ࡤࠨ஄")
          if bstack1l11l11l11_opy_.message:
            data[bstack11ll1_opy_ (u"ࠩࡵࡩࡦࡹ࡯࡯ࠩஅ")] = str(bstack1l11l11l11_opy_.message)
      user = CONFIG[bstack11ll1_opy_ (u"ࠪࡹࡸ࡫ࡲࡏࡣࡰࡩࠬஆ")]
      key = CONFIG[bstack11ll1_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶࡏࡪࡿࠧஇ")]
      host = bstack1ll1l111_opy_(cli.config, [bstack11ll1_opy_ (u"ࠧࡧࡰࡪࡵࠥஈ"), bstack11ll1_opy_ (u"ࠨࡡࡶࡶࡲࡱࡦࡺࡥࠣஉ"), bstack11ll1_opy_ (u"ࠢࡢࡲ࡬ࠦஊ")], bstack11ll1_opy_ (u"ࠣࡪࡷࡸࡵࡹ࠺࠰࠱ࡤࡴ࡮࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡩ࡯࡮ࠤ஋"))
      url = bstack11ll1_opy_ (u"ࠩࡾࢁ࠴ࡧࡵࡵࡱࡰࡥࡹ࡫࠯ࡴࡧࡶࡷ࡮ࡵ࡮ࡴ࠱ࡾࢁ࠳ࡰࡳࡰࡰࠪ஌").format(host, bstack1l111l111l_opy_)
      headers = {
        bstack11ll1_opy_ (u"ࠪࡇࡴࡴࡴࡦࡰࡷ࠱ࡹࡿࡰࡦࠩ஍"): bstack11ll1_opy_ (u"ࠫࡦࡶࡰ࡭࡫ࡦࡥࡹ࡯࡯࡯࠱࡭ࡷࡴࡴࠧஎ"),
      }
      if bool(data):
        requests.put(url, json=data, headers=headers, auth=(user, key))
        cli.bstack1lll1lll1_opy_(bstack11ll1_opy_ (u"ࠧ࡮ࡴࡵࡲ࠽ࡹࡵࡪࡡࡵࡧࡢࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡶࡸࡦࡺࡵࡴࠤஏ"), datetime.datetime.now() - bstack1ll11l1l1l_opy_)
    except Exception as e:
      logger.error(bstack111l1l11_opy_.format(str(e)))
def bstack1llllll111_opy_(test, bstack1lll1l1l1_opy_):
  global CONFIG
  global bstack1lll1111_opy_
  global bstack1l1lll1l11_opy_
  global bstack1l111l111l_opy_
  global bstack1l11l11l11_opy_
  global bstack1ll1l11111_opy_
  global bstack1ll1ll111l_opy_
  global bstack11l1111l_opy_
  global bstack1l11l1ll_opy_
  global bstack1llllll1l_opy_
  global bstack1lll111ll_opy_
  global bstack1l11l11ll_opy_
  global bstack11l111ll_opy_
  try:
    if not bstack1l111l111l_opy_:
      with bstack11l111ll_opy_:
        bstack11ll111l1_opy_ = os.path.join(os.path.expanduser(bstack11ll1_opy_ (u"࠭ࡾࠨஐ")), bstack11ll1_opy_ (u"ࠧ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠧ஑"), bstack11ll1_opy_ (u"ࠨ࠰ࡶࡩࡸࡹࡩࡰࡰ࡬ࡨࡸ࠴ࡴࡹࡶࠪஒ"))
        if os.path.exists(bstack11ll111l1_opy_):
          with open(bstack11ll111l1_opy_, bstack11ll1_opy_ (u"ࠩࡵࠫஓ")) as f:
            content = f.read().strip()
            if content:
              bstack1l11ll1ll_opy_ = json.loads(bstack11ll1_opy_ (u"ࠥࡿࠧஔ") + content + bstack11ll1_opy_ (u"ࠫࠧࡾࠢ࠻ࠢࠥࡽࠧ࠭க") + bstack11ll1_opy_ (u"ࠧࢃࠢ஖"))
              bstack1l111l111l_opy_ = bstack1l11ll1ll_opy_.get(str(threading.get_ident()))
  except Exception as e:
    logger.debug(bstack11ll1_opy_ (u"࠭ࡅࡳࡴࡲࡶࠥࡸࡥࡢࡦ࡬ࡲ࡬ࠦࡳࡦࡵࡶ࡭ࡴࡴࠠࡊࡆࡶࠤ࡫࡯࡬ࡦ࠼ࠣࠫ஗") + str(e))
  if bstack1lll111ll_opy_:
    with bstack1l1lll11_opy_:
      bstack1111l11ll_opy_ = bstack1lll111ll_opy_.copy()
    for driver in bstack1111l11ll_opy_:
      if bstack1l111l111l_opy_ == driver.session_id:
        if test:
          bstack1l1ll1lll1_opy_(driver, test)
        bstack1l11l1ll1l_opy_(driver, bstack1lll1l1l1_opy_)
  elif bstack1l111l111l_opy_:
    bstack11l1ll11l1_opy_(test, bstack1lll1l1l1_opy_)
  if bstack1lll1111_opy_:
    bstack11l1111l_opy_(bstack1lll1111_opy_)
  if bstack1l1lll1l11_opy_:
    bstack1l11l1ll_opy_(bstack1l1lll1l11_opy_)
  if bstack11l1l1111_opy_:
    bstack1llllll1l_opy_()
def bstack1l1lll111l_opy_(self, test, *args, **kwargs):
  bstack1lll1l1l1_opy_ = None
  if test:
    bstack1lll1l1l1_opy_ = str(test.name)
  bstack1llllll111_opy_(test, bstack1lll1l1l1_opy_)
  bstack1ll1ll111l_opy_(self, test, *args, **kwargs)
def bstack1lll1ll111_opy_(self, parent, test, skip_on_failure=None, rpa=False):
  global bstack1l111l1ll_opy_
  global CONFIG
  global bstack1lll111ll_opy_
  global bstack1l111l111l_opy_
  global bstack11l111ll_opy_
  bstack11l1l1l1l1_opy_ = None
  try:
    if bstack1lll11l1l_opy_(threading.current_thread(), bstack11ll1_opy_ (u"ࠧࡢ࠳࠴ࡽࡕࡲࡡࡵࡨࡲࡶࡲ࠭஘"), None) or bstack1lll11l1l_opy_(threading.current_thread(), bstack11ll1_opy_ (u"ࠨࡣࡳࡴࡆ࠷࠱ࡺࡒ࡯ࡥࡹ࡬࡯ࡳ࡯ࠪங"), None):
      try:
        if not bstack1l111l111l_opy_:
          bstack11ll111l1_opy_ = os.path.join(os.path.expanduser(bstack11ll1_opy_ (u"ࠩࢁࠫச")), bstack11ll1_opy_ (u"ࠪ࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࠪ஛"), bstack11ll1_opy_ (u"ࠫ࠳ࡹࡥࡴࡵ࡬ࡳࡳ࡯ࡤࡴ࠰ࡷࡼࡹ࠭ஜ"))
          with bstack11l111ll_opy_:
            if os.path.exists(bstack11ll111l1_opy_):
              with open(bstack11ll111l1_opy_, bstack11ll1_opy_ (u"ࠬࡸࠧ஝")) as f:
                content = f.read().strip()
                if content:
                  bstack1l11ll1ll_opy_ = json.loads(bstack11ll1_opy_ (u"ࠨࡻࠣஞ") + content + bstack11ll1_opy_ (u"ࠧࠣࡺࠥ࠾ࠥࠨࡹࠣࠩட") + bstack11ll1_opy_ (u"ࠣࡿࠥ஠"))
                  bstack1l111l111l_opy_ = bstack1l11ll1ll_opy_.get(str(threading.get_ident()))
      except Exception as e:
        logger.debug(bstack11ll1_opy_ (u"ࠩࡈࡶࡷࡵࡲࠡࡴࡨࡥࡩ࡯࡮ࡨࠢࡶࡩࡸࡹࡩࡰࡰࠣࡍࡉࡹࠠࡧ࡫࡯ࡩࠥ࡯࡮ࠡࡶࡨࡷࡹࠦࡳࡵࡣࡷࡹࡸࡀࠠࠨ஡") + str(e))
      if bstack1lll111ll_opy_:
        with bstack1l1lll11_opy_:
          bstack1111l11ll_opy_ = bstack1lll111ll_opy_.copy()
        for driver in bstack1111l11ll_opy_:
          if bstack1l111l111l_opy_ == driver.session_id:
            bstack11l1l1l1l1_opy_ = driver
    bstack1ll11l111l_opy_ = bstack1l1ll11l1l_opy_.bstack1llll1111l_opy_(test.tags)
    if bstack11l1l1l1l1_opy_:
      threading.current_thread().isA11yTest = bstack1l1ll11l1l_opy_.bstack11lll1111l_opy_(bstack11l1l1l1l1_opy_, bstack1ll11l111l_opy_)
      threading.current_thread().isAppA11yTest = bstack1l1ll11l1l_opy_.bstack11lll1111l_opy_(bstack11l1l1l1l1_opy_, bstack1ll11l111l_opy_)
    else:
      threading.current_thread().isA11yTest = bstack1ll11l111l_opy_
      threading.current_thread().isAppA11yTest = bstack1ll11l111l_opy_
  except:
    pass
  bstack1l111l1ll_opy_(self, parent, test, skip_on_failure=skip_on_failure, rpa=rpa)
  global bstack1l11l11l11_opy_
  try:
    bstack1l11l11l11_opy_ = self._test
  except:
    bstack1l11l11l11_opy_ = self.test
def bstack11111l11_opy_():
  global bstack1lll1ll1ll_opy_
  try:
    if os.path.exists(bstack1lll1ll1ll_opy_):
      os.remove(bstack1lll1ll1ll_opy_)
  except Exception as e:
    logger.debug(bstack11ll1_opy_ (u"ࠪࡉࡷࡸ࡯ࡳࠢ࡬ࡲࠥࡪࡥ࡭ࡧࡷ࡭ࡳ࡭ࠠࡳࡱࡥࡳࡹࠦࡲࡦࡲࡲࡶࡹࠦࡦࡪ࡮ࡨ࠾ࠥ࠭஢") + str(e))
def bstack1l1ll1l1ll_opy_():
  global bstack1lll1ll1ll_opy_
  bstack1lll11111l_opy_ = {}
  lock_file = bstack1lll1ll1ll_opy_ + bstack11ll1_opy_ (u"ࠫ࠳ࡲ࡯ࡤ࡭ࠪண")
  try:
    from filelock import FileLock
  except ImportError:
    logger.debug(bstack11ll1_opy_ (u"ࠬ࡬ࡩ࡭ࡧ࡯ࡳࡨࡱࠠ࡯ࡱࡷࠤࡦࡼࡡࡪ࡮ࡤࡦࡱ࡫ࠬࠡࡷࡶ࡭ࡳ࡭ࠠࡣࡣࡶ࡭ࡨࠦࡦࡪ࡮ࡨࠤࡴࡶࡥࡳࡣࡷ࡭ࡴࡴࡳࠨத"))
    try:
      if not os.path.isfile(bstack1lll1ll1ll_opy_):
        with open(bstack1lll1ll1ll_opy_, bstack11ll1_opy_ (u"࠭ࡷࠨ஥")) as f:
          json.dump({}, f)
      if os.path.exists(bstack1lll1ll1ll_opy_):
        with open(bstack1lll1ll1ll_opy_, bstack11ll1_opy_ (u"ࠧࡳࠩ஦")) as f:
          content = f.read().strip()
          if content:
            bstack1lll11111l_opy_ = json.loads(content)
    except Exception as e:
      logger.debug(bstack11ll1_opy_ (u"ࠨࡇࡵࡶࡴࡸࠠࡪࡰࠣࡶࡪࡧࡤࡪࡰࡪࠤࡷࡵࡢࡰࡶࠣࡶࡪࡶ࡯ࡳࡶࠣࡪ࡮ࡲࡥ࠻ࠢࠪ஧") + str(e))
    return bstack1lll11111l_opy_
  try:
    os.makedirs(os.path.dirname(bstack1lll1ll1ll_opy_), exist_ok=True)
    with FileLock(lock_file, timeout=10):
      if not os.path.isfile(bstack1lll1ll1ll_opy_):
        with open(bstack1lll1ll1ll_opy_, bstack11ll1_opy_ (u"ࠩࡺࠫந")) as f:
          json.dump({}, f)
      if os.path.exists(bstack1lll1ll1ll_opy_):
        with open(bstack1lll1ll1ll_opy_, bstack11ll1_opy_ (u"ࠪࡶࠬன")) as f:
          content = f.read().strip()
          if content:
            bstack1lll11111l_opy_ = json.loads(content)
  except Exception as e:
    logger.debug(bstack11ll1_opy_ (u"ࠫࡊࡸࡲࡰࡴࠣ࡭ࡳࠦࡲࡦࡣࡧ࡭ࡳ࡭ࠠࡳࡱࡥࡳࡹࠦࡲࡦࡲࡲࡶࡹࠦࡦࡪ࡮ࡨ࠾ࠥ࠭ப") + str(e))
  finally:
    return bstack1lll11111l_opy_
def bstack11l1l1l1_opy_(platform_index, item_index):
  global bstack1lll1ll1ll_opy_
  lock_file = bstack1lll1ll1ll_opy_ + bstack11ll1_opy_ (u"ࠬ࠴࡬ࡰࡥ࡮ࠫ஫")
  try:
    from filelock import FileLock
  except ImportError:
    logger.debug(bstack11ll1_opy_ (u"࠭ࡦࡪ࡮ࡨࡰࡴࡩ࡫ࠡࡰࡲࡸࠥࡧࡶࡢ࡫࡯ࡥࡧࡲࡥ࠭ࠢࡸࡷ࡮ࡴࡧࠡࡤࡤࡷ࡮ࡩࠠࡧ࡫࡯ࡩࠥࡵࡰࡦࡴࡤࡸ࡮ࡵ࡮ࡴࠩ஬"))
    try:
      bstack1lll11111l_opy_ = {}
      if os.path.exists(bstack1lll1ll1ll_opy_):
        with open(bstack1lll1ll1ll_opy_, bstack11ll1_opy_ (u"ࠧࡳࠩ஭")) as f:
          content = f.read().strip()
          if content:
            bstack1lll11111l_opy_ = json.loads(content)
      bstack1lll11111l_opy_[item_index] = platform_index
      with open(bstack1lll1ll1ll_opy_, bstack11ll1_opy_ (u"ࠣࡹࠥம")) as outfile:
        json.dump(bstack1lll11111l_opy_, outfile)
    except Exception as e:
      logger.debug(bstack11ll1_opy_ (u"ࠩࡈࡶࡷࡵࡲࠡ࡫ࡱࠤࡼࡸࡩࡵ࡫ࡱ࡫ࠥࡺ࡯ࠡࡴࡲࡦࡴࡺࠠࡳࡧࡳࡳࡷࡺࠠࡧ࡫࡯ࡩ࠿ࠦࠧய") + str(e))
    return
  try:
    os.makedirs(os.path.dirname(bstack1lll1ll1ll_opy_), exist_ok=True)
    with FileLock(lock_file, timeout=10):
      bstack1lll11111l_opy_ = {}
      if os.path.exists(bstack1lll1ll1ll_opy_):
        with open(bstack1lll1ll1ll_opy_, bstack11ll1_opy_ (u"ࠪࡶࠬர")) as f:
          content = f.read().strip()
          if content:
            bstack1lll11111l_opy_ = json.loads(content)
      bstack1lll11111l_opy_[item_index] = platform_index
      with open(bstack1lll1ll1ll_opy_, bstack11ll1_opy_ (u"ࠦࡼࠨற")) as outfile:
        json.dump(bstack1lll11111l_opy_, outfile)
  except Exception as e:
    logger.debug(bstack11ll1_opy_ (u"ࠬࡋࡲࡳࡱࡵࠤ࡮ࡴࠠࡸࡴ࡬ࡸ࡮ࡴࡧࠡࡶࡲࠤࡷࡵࡢࡰࡶࠣࡶࡪࡶ࡯ࡳࡶࠣࡪ࡮ࡲࡥ࠻ࠢࠪல") + str(e))
def bstack11ll1lllll_opy_(bstack1l111lll1_opy_):
  global CONFIG
  bstack11ll1111l1_opy_ = bstack11ll1_opy_ (u"࠭ࠧள")
  if not bstack11ll1_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪழ") in CONFIG:
    logger.info(bstack11ll1_opy_ (u"ࠨࡐࡲࠤࡵࡲࡡࡵࡨࡲࡶࡲࡹࠠࡱࡣࡶࡷࡪࡪࠠࡶࡰࡤࡦࡱ࡫ࠠࡵࡱࠣ࡫ࡪࡴࡥࡳࡣࡷࡩࠥࡸࡥࡱࡱࡵࡸࠥ࡬࡯ࡳࠢࡕࡳࡧࡵࡴࠡࡴࡸࡲࠬவ"))
  try:
    platform = CONFIG[bstack11ll1_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬஶ")][bstack1l111lll1_opy_]
    if bstack11ll1_opy_ (u"ࠪࡳࡸ࠭ஷ") in platform:
      bstack11ll1111l1_opy_ += str(platform[bstack11ll1_opy_ (u"ࠫࡴࡹࠧஸ")]) + bstack11ll1_opy_ (u"ࠬ࠲ࠠࠨஹ")
    if bstack11ll1_opy_ (u"࠭࡯ࡴࡘࡨࡶࡸ࡯࡯࡯ࠩ஺") in platform:
      bstack11ll1111l1_opy_ += str(platform[bstack11ll1_opy_ (u"ࠧࡰࡵ࡙ࡩࡷࡹࡩࡰࡰࠪ஻")]) + bstack11ll1_opy_ (u"ࠨ࠮ࠣࠫ஼")
    if bstack11ll1_opy_ (u"ࠩࡧࡩࡻ࡯ࡣࡦࡐࡤࡱࡪ࠭஽") in platform:
      bstack11ll1111l1_opy_ += str(platform[bstack11ll1_opy_ (u"ࠪࡨࡪࡼࡩࡤࡧࡑࡥࡲ࡫ࠧா")]) + bstack11ll1_opy_ (u"ࠫ࠱ࠦࠧி")
    if bstack11ll1_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡖࡦࡴࡶ࡭ࡴࡴࠧீ") in platform:
      bstack11ll1111l1_opy_ += str(platform[bstack11ll1_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡗࡧࡵࡷ࡮ࡵ࡮ࠨு")]) + bstack11ll1_opy_ (u"ࠧ࠭ࠢࠪூ")
    if bstack11ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡐࡤࡱࡪ࠭௃") in platform:
      bstack11ll1111l1_opy_ += str(platform[bstack11ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡑࡥࡲ࡫ࠧ௄")]) + bstack11ll1_opy_ (u"ࠪ࠰ࠥ࠭௅")
    if bstack11ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶ࡛࡫ࡲࡴ࡫ࡲࡲࠬெ") in platform:
      bstack11ll1111l1_opy_ += str(platform[bstack11ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡜ࡥࡳࡵ࡬ࡳࡳ࠭ே")]) + bstack11ll1_opy_ (u"࠭ࠬࠡࠩை")
  except Exception as e:
    logger.debug(bstack11ll1_opy_ (u"ࠧࡔࡱࡰࡩࠥ࡫ࡲࡳࡱࡵࠤ࡮ࡴࠠࡨࡧࡱࡩࡷࡧࡴࡪࡰࡪࠤࡵࡲࡡࡵࡨࡲࡶࡲࠦࡳࡵࡴ࡬ࡲ࡬ࠦࡦࡰࡴࠣࡶࡪࡶ࡯ࡳࡶࠣ࡫ࡪࡴࡥࡳࡣࡷ࡭ࡴࡴࠧ௉") + str(e))
  finally:
    if bstack11ll1111l1_opy_[len(bstack11ll1111l1_opy_) - 2:] == bstack11ll1_opy_ (u"ࠨ࠮ࠣࠫொ"):
      bstack11ll1111l1_opy_ = bstack11ll1111l1_opy_[:-2]
    return bstack11ll1111l1_opy_
def bstack111ll11ll_opy_(path, bstack11ll1111l1_opy_):
  try:
    import xml.etree.ElementTree as ET
    bstack11l1ll1ll1_opy_ = ET.parse(path)
    bstack1ll11111ll_opy_ = bstack11l1ll1ll1_opy_.getroot()
    bstack1llllll1l1_opy_ = None
    for suite in bstack1ll11111ll_opy_.iter(bstack11ll1_opy_ (u"ࠩࡶࡹ࡮ࡺࡥࠨோ")):
      if bstack11ll1_opy_ (u"ࠪࡷࡴࡻࡲࡤࡧࠪௌ") in suite.attrib:
        suite.attrib[bstack11ll1_opy_ (u"ࠫࡳࡧ࡭ࡦ்ࠩ")] += bstack11ll1_opy_ (u"ࠬࠦࠧ௎") + bstack11ll1111l1_opy_
        bstack1llllll1l1_opy_ = suite
    bstack1l11lll1l1_opy_ = None
    for robot in bstack1ll11111ll_opy_.iter(bstack11ll1_opy_ (u"࠭ࡲࡰࡤࡲࡸࠬ௏")):
      bstack1l11lll1l1_opy_ = robot
    bstack11l11111_opy_ = len(bstack1l11lll1l1_opy_.findall(bstack11ll1_opy_ (u"ࠧࡴࡷ࡬ࡸࡪ࠭ௐ")))
    if bstack11l11111_opy_ == 1:
      bstack1l11lll1l1_opy_.remove(bstack1l11lll1l1_opy_.findall(bstack11ll1_opy_ (u"ࠨࡵࡸ࡭ࡹ࡫ࠧ௑"))[0])
      bstack111ll1l11_opy_ = ET.Element(bstack11ll1_opy_ (u"ࠩࡶࡹ࡮ࡺࡥࠨ௒"), attrib={bstack11ll1_opy_ (u"ࠪࡲࡦࡳࡥࠨ௓"): bstack11ll1_opy_ (u"ࠫࡘࡻࡩࡵࡧࡶࠫ௔"), bstack11ll1_opy_ (u"ࠬ࡯ࡤࠨ௕"): bstack11ll1_opy_ (u"࠭ࡳ࠱ࠩ௖")})
      bstack1l11lll1l1_opy_.insert(1, bstack111ll1l11_opy_)
      bstack1l11l1llll_opy_ = None
      for suite in bstack1l11lll1l1_opy_.iter(bstack11ll1_opy_ (u"ࠧࡴࡷ࡬ࡸࡪ࠭ௗ")):
        bstack1l11l1llll_opy_ = suite
      bstack1l11l1llll_opy_.append(bstack1llllll1l1_opy_)
      bstack1l1l11l1l1_opy_ = None
      for status in bstack1llllll1l1_opy_.iter(bstack11ll1_opy_ (u"ࠨࡵࡷࡥࡹࡻࡳࠨ௘")):
        bstack1l1l11l1l1_opy_ = status
      bstack1l11l1llll_opy_.append(bstack1l1l11l1l1_opy_)
    bstack11l1ll1ll1_opy_.write(path)
  except Exception as e:
    logger.debug(bstack11ll1_opy_ (u"ࠩࡈࡶࡷࡵࡲࠡ࡫ࡱࠤࡵࡧࡲࡴ࡫ࡱ࡫ࠥࡽࡨࡪ࡮ࡨࠤ࡬࡫࡮ࡦࡴࡤࡸ࡮ࡴࡧࠡࡴࡲࡦࡴࡺࠠࡳࡧࡳࡳࡷࡺࠧ௙") + str(e))
def bstack1lll1ll11_opy_(outs_dir, pabot_args, options, start_time_string, tests_root_name):
  global bstack1lllll11ll_opy_
  global CONFIG
  if bstack11ll1_opy_ (u"ࠥࡴࡾࡺࡨࡰࡰࡳࡥࡹ࡮ࠢ௚") in options:
    del options[bstack11ll1_opy_ (u"ࠦࡵࡿࡴࡩࡱࡱࡴࡦࡺࡨࠣ௛")]
  bstack11ll1111l_opy_ = bstack1l1ll1l1ll_opy_()
  for item_id in bstack11ll1111l_opy_.keys():
    path = os.path.join(outs_dir, str(item_id), bstack11ll1_opy_ (u"ࠬࡵࡵࡵࡲࡸࡸ࠳ࡾ࡭࡭ࠩ௜"))
    bstack111ll11ll_opy_(path, bstack11ll1lllll_opy_(bstack11ll1111l_opy_[item_id]))
  bstack11111l11_opy_()
  return bstack1lllll11ll_opy_(outs_dir, pabot_args, options, start_time_string, tests_root_name)
def bstack1l1lll1l1_opy_(self, ff_profile_dir):
  global bstack11l11lllll_opy_
  if not ff_profile_dir:
    return None
  return bstack11l11lllll_opy_(self, ff_profile_dir)
def bstack1ll1l1l11_opy_(datasources, opts_for_run, outs_dir, pabot_args, suite_group):
  from pabot.pabot import QueueItem
  global CONFIG
  global bstack11ll1l11l1_opy_
  bstack1l1111l111_opy_ = []
  if bstack11ll1_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩ௝") in CONFIG:
    bstack1l1111l111_opy_ = CONFIG[bstack11ll1_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪ௞")]
  return [
    QueueItem(
      datasources,
      outs_dir,
      opts_for_run,
      suite,
      pabot_args[bstack11ll1_opy_ (u"ࠣࡥࡲࡱࡲࡧ࡮ࡥࠤ௟")],
      pabot_args[bstack11ll1_opy_ (u"ࠤࡹࡩࡷࡨ࡯ࡴࡧࠥ௠")],
      argfile,
      pabot_args.get(bstack11ll1_opy_ (u"ࠥ࡬࡮ࡼࡥࠣ௡")),
      pabot_args[bstack11ll1_opy_ (u"ࠦࡵࡸ࡯ࡤࡧࡶࡷࡪࡹࠢ௢")],
      platform[0],
      bstack11ll1l11l1_opy_
    )
    for suite in suite_group
    for argfile in pabot_args[bstack11ll1_opy_ (u"ࠧࡧࡲࡨࡷࡰࡩࡳࡺࡦࡪ࡮ࡨࡷࠧ௣")] or [(bstack11ll1_opy_ (u"ࠨࠢ௤"), None)]
    for platform in enumerate(bstack1l1111l111_opy_)
  ]
def bstack1l1llll1_opy_(self, datasources, outs_dir, options,
                        execution_item, command, verbose, argfile,
                        hive=None, processes=0, platform_index=0, bstack11ll11111l_opy_=bstack11ll1_opy_ (u"ࠧࠨ௥")):
  global bstack11l1lllll_opy_
  self.platform_index = platform_index
  self.bstack11l11lll1l_opy_ = bstack11ll11111l_opy_
  bstack11l1lllll_opy_(self, datasources, outs_dir, options,
                      execution_item, command, verbose, argfile, hive, processes)
def bstack111lll1l1l_opy_(caller_id, datasources, is_last, item, outs_dir):
  global bstack1l1l1l1111_opy_
  global bstack111llll1ll_opy_
  bstack1l1l1ll11l_opy_ = copy.deepcopy(item)
  if not bstack11ll1_opy_ (u"ࠨࡸࡤࡶ࡮ࡧࡢ࡭ࡧࠪ௦") in item.options:
    bstack1l1l1ll11l_opy_.options[bstack11ll1_opy_ (u"ࠩࡹࡥࡷ࡯ࡡࡣ࡮ࡨࠫ௧")] = []
  bstack1l1l1l11l1_opy_ = bstack1l1l1ll11l_opy_.options[bstack11ll1_opy_ (u"ࠪࡺࡦࡸࡩࡢࡤ࡯ࡩࠬ௨")].copy()
  for v in bstack1l1l1ll11l_opy_.options[bstack11ll1_opy_ (u"ࠫࡻࡧࡲࡪࡣࡥࡰࡪ࠭௩")]:
    if bstack11ll1_opy_ (u"ࠬࡈࡓࡕࡃࡆࡏࡕࡒࡁࡕࡈࡒࡖࡒࡏࡎࡅࡇ࡛ࠫ௪") in v:
      bstack1l1l1l11l1_opy_.remove(v)
    if bstack11ll1_opy_ (u"࠭ࡂࡔࡖࡄࡇࡐࡉࡌࡊࡃࡕࡋࡘ࠭௫") in v:
      bstack1l1l1l11l1_opy_.remove(v)
    if bstack11ll1_opy_ (u"ࠧࡃࡕࡗࡅࡈࡑࡄࡆࡈࡏࡓࡈࡇࡌࡊࡆࡈࡒ࡙ࡏࡆࡊࡇࡕࠫ௬") in v:
      bstack1l1l1l11l1_opy_.remove(v)
  bstack1l1l1l11l1_opy_.insert(0, bstack11ll1_opy_ (u"ࠨࡄࡖࡘࡆࡉࡋࡑࡎࡄࡘࡋࡕࡒࡎࡋࡑࡈࡊ࡞࠺ࡼࡿࠪ௭").format(bstack1l1l1ll11l_opy_.platform_index))
  bstack1l1l1l11l1_opy_.insert(0, bstack11ll1_opy_ (u"ࠩࡅࡗ࡙ࡇࡃࡌࡆࡈࡊࡑࡕࡃࡂࡎࡌࡈࡊࡔࡔࡊࡈࡌࡉࡗࡀࡻࡾࠩ௮").format(bstack1l1l1ll11l_opy_.bstack11l11lll1l_opy_))
  bstack1l1l1ll11l_opy_.options[bstack11ll1_opy_ (u"ࠪࡺࡦࡸࡩࡢࡤ࡯ࡩࠬ௯")] = bstack1l1l1l11l1_opy_
  if bstack111llll1ll_opy_:
    bstack1l1l1ll11l_opy_.options[bstack11ll1_opy_ (u"ࠫࡻࡧࡲࡪࡣࡥࡰࡪ࠭௰")].insert(0, bstack11ll1_opy_ (u"ࠬࡈࡓࡕࡃࡆࡏࡈࡒࡉࡂࡔࡊࡗ࠿ࢁࡽࠨ௱").format(bstack111llll1ll_opy_))
  return bstack1l1l1l1111_opy_(caller_id, datasources, is_last, bstack1l1l1ll11l_opy_, outs_dir)
def bstack1lll11l1l1_opy_(command, item_index):
  try:
    if bstack1l1l1ll1l_opy_.get_property(bstack11ll1_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡥࡳࡦࡵࡶ࡭ࡴࡴࠧ௲")):
      os.environ[bstack11ll1_opy_ (u"ࠧࡄࡗࡕࡖࡊࡔࡔࡠࡒࡏࡅ࡙ࡌࡏࡓࡏࡢࡈࡆ࡚ࡁࠨ௳")] = json.dumps(CONFIG[bstack11ll1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫ௴")][item_index % bstack1llll11l1l_opy_])
    global bstack111llll1ll_opy_
    if bstack111llll1ll_opy_:
      command[0] = command[0].replace(bstack11ll1_opy_ (u"ࠩࡵࡳࡧࡵࡴࠨ௵"), bstack11ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠯ࡶࡨࡰࠦࡲࡰࡤࡲࡸ࠲࡯࡮ࡵࡧࡵࡲࡦࡲࠠ࠮࠯ࡥࡷࡹࡧࡣ࡬ࡡࡳࡰࡦࡺࡦࡰࡴࡰࡣ࡮ࡴࡤࡦࡺࠣࠫ௶") + str(item_index % bstack1llll11l1l_opy_) + bstack11ll1_opy_ (u"ࠫࠥ࠳࠭ࡣࡵࡷࡥࡨࡱ࡟ࡪࡶࡨࡱࡤ࡯࡮ࡥࡧࡻࠤࠬ௷") + str(
        item_index) + bstack11ll1_opy_ (u"ࠬࠦࠧ௸") + bstack111llll1ll_opy_, 1)
    else:
      command[0] = command[0].replace(bstack11ll1_opy_ (u"࠭ࡲࡰࡤࡲࡸࠬ௹"),
                                      bstack11ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠳ࡳࡥ࡭ࠣࡶࡴࡨ࡯ࡵ࠯࡬ࡲࡹ࡫ࡲ࡯ࡣ࡯ࠤ࠲࠳ࡢࡴࡶࡤࡧࡰࡥࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡠ࡫ࡱࡨࡪࡾࠠࠨ௺") +  str(item_index % bstack1llll11l1l_opy_) + bstack11ll1_opy_ (u"ࠨࠢ࠰࠱ࡧࡹࡴࡢࡥ࡮ࡣ࡮ࡺࡥ࡮ࡡ࡬ࡲࡩ࡫ࡸࠡࠩ௻") + str(item_index), 1)
  except Exception as e:
    logger.error(bstack11ll1_opy_ (u"ࠩࡈࡶࡷࡵࡲࠡ࡯ࡲࡨ࡮࡬ࡹࡪࡰࡪࠤࡨࡵ࡭࡮ࡣࡱࡨࠥ࡬࡯ࡳࠢࡳࡥࡧࡵࡴࠡࡴࡸࡲ࠿ࠦࡻࡾࠩ௼").format(str(e)))
def bstack1l1111l1l1_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index):
  global bstack1ll1llll11_opy_
  try:
    bstack1lll11l1l1_opy_(command, item_index)
    return bstack1ll1llll11_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index)
  except Exception as e:
    logger.error(bstack11ll1_opy_ (u"ࠪࡉࡷࡸ࡯ࡳࠢ࡬ࡲࠥࡶࡡࡣࡱࡷࠤࡷࡻ࡮࠻ࠢࡾࢁࠬ௽").format(str(e)))
    raise e
def bstack111l111l1_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir):
  global bstack1ll1llll11_opy_
  try:
    bstack1lll11l1l1_opy_(command, item_index)
    return bstack1ll1llll11_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir)
  except Exception as e:
    logger.error(bstack11ll1_opy_ (u"ࠫࡊࡸࡲࡰࡴࠣ࡭ࡳࠦࡰࡢࡤࡲࡸࠥࡸࡵ࡯ࠢ࠵࠲࠶࠹࠺ࠡࡽࢀࠫ௾").format(str(e)))
    try:
      return bstack1ll1llll11_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index)
    except Exception as e2:
      logger.error(bstack11ll1_opy_ (u"ࠬࡋࡲࡳࡱࡵࠤ࡮ࡴࠠࡱࡣࡥࡳࡹࠦ࠲࠯࠳࠶ࠤ࡫ࡧ࡬࡭ࡤࡤࡧࡰࡀࠠࡼࡿࠪ௿").format(str(e2)))
      raise e
def bstack11lllll11_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir, process_timeout):
  global bstack1ll1llll11_opy_
  try:
    bstack1lll11l1l1_opy_(command, item_index)
    if process_timeout is None:
      process_timeout = 3600
    return bstack1ll1llll11_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir, process_timeout)
  except Exception as e:
    logger.error(bstack11ll1_opy_ (u"࠭ࡅࡳࡴࡲࡶࠥ࡯࡮ࠡࡲࡤࡦࡴࡺࠠࡳࡷࡱࠤ࠷࠴࠱࠶࠼ࠣࡿࢂ࠭ఀ").format(str(e)))
    try:
      return bstack1ll1llll11_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir)
    except Exception as e2:
      logger.error(bstack11ll1_opy_ (u"ࠧࡆࡴࡵࡳࡷࠦࡩ࡯ࠢࡳࡥࡧࡵࡴࠡ࠴࠱࠵࠺ࠦࡦࡢ࡮࡯ࡦࡦࡩ࡫࠻ࠢࡾࢁࠬఁ").format(str(e2)))
      raise e
def _1lllll111_opy_(bstack1l1l111l1l_opy_, item_index, process_timeout, sleep_before_start, bstack11lll111_opy_):
  bstack1lll11l1l1_opy_(bstack1l1l111l1l_opy_, item_index)
  if process_timeout is None:
    process_timeout = 3600
  if sleep_before_start and sleep_before_start > 0:
    time.sleep(min(sleep_before_start, 5))
  return process_timeout
def bstack11l11l1ll1_opy_(command, bstack11ll111l11_opy_, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir, process_timeout, sleep_before_start):
  global bstack1ll1llll11_opy_
  global bstack11ll1llll_opy_
  global bstack111llll1ll_opy_
  try:
    for env_name, bstack11111l1l1_opy_ in bstack11ll1llll_opy_.items():
      os.environ[env_name] = bstack11111l1l1_opy_
    bstack111llll1ll_opy_ = bstack11ll1_opy_ (u"ࠣࠤం")
    bstack1lll11l1l1_opy_(command, item_index)
    if process_timeout is None:
      process_timeout = 3600
    if sleep_before_start and sleep_before_start > 0:
      time.sleep(min(sleep_before_start, 5))
    return bstack1ll1llll11_opy_(command, bstack11ll111l11_opy_, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir, process_timeout, sleep_before_start)
  except Exception as e:
    logger.error(bstack11ll1_opy_ (u"ࠩࡈࡶࡷࡵࡲࠡ࡫ࡱࠤࡵࡧࡢࡰࡶࠣࡶࡺࡴࠠ࠶࠰࠳࠾ࠥࢁࡽࠨః").format(str(e)))
    try:
      return bstack1ll1llll11_opy_(command, bstack11ll111l11_opy_, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir, process_timeout)
    except Exception as e2:
      logger.error(bstack11ll1_opy_ (u"ࠪࡉࡷࡸ࡯ࡳࠢ࡬ࡲࠥࡶࡡࡣࡱࡷࠤ࡫ࡧ࡬࡭ࡤࡤࡧࡰࡀࠠࡼࡿࠪఄ").format(str(e2)))
      raise e
def bstack1l1llll1l1_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir, process_timeout, sleep_before_start):
  global bstack1ll1llll11_opy_
  try:
    process_timeout = _1lllll111_opy_(command, item_index, process_timeout, sleep_before_start, bstack11ll1_opy_ (u"ࠫ࠹࠴࠲ࠨఅ"))
    return bstack1ll1llll11_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir, process_timeout, sleep_before_start)
  except Exception as e:
    logger.error(bstack11ll1_opy_ (u"ࠬࡋࡲࡳࡱࡵࠤ࡮ࡴࠠࡱࡣࡥࡳࡹࠦࡲࡶࡰࠣ࠸࠳࠸࠺ࠡࡽࢀࠫఆ").format(str(e)))
    try:
      return bstack1ll1llll11_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir, process_timeout)
    except Exception as e2:
      logger.error(bstack11ll1_opy_ (u"࠭ࡅࡳࡴࡲࡶࠥ࡯࡮ࠡࡲࡤࡦࡴࡺࠠࡧࡣ࡯ࡰࡧࡧࡣ࡬࠼ࠣࡿࢂ࠭ఇ").format(str(e2)))
      raise e
def is_driver_active(driver):
  return True if driver and driver.session_id else False
def bstack11ll11ll_opy_(self, runner, quiet=False, capture=True):
  global bstack1ll1l1lll1_opy_
  bstack11l1ll1l1_opy_ = bstack1ll1l1lll1_opy_(self, runner, quiet=quiet, capture=capture)
  if self.exception:
    if not hasattr(runner, bstack11ll1_opy_ (u"ࠧࡦࡺࡦࡩࡵࡺࡩࡰࡰࡢࡥࡷࡸࠧఈ")):
      runner.exception_arr = []
    if not hasattr(runner, bstack11ll1_opy_ (u"ࠨࡧࡻࡧࡤࡺࡲࡢࡥࡨࡦࡦࡩ࡫ࡠࡣࡵࡶࠬఉ")):
      runner.exc_traceback_arr = []
    runner.exception = self.exception
    runner.exc_traceback = self.exc_traceback
    runner.exception_arr.append(self.exception)
    runner.exc_traceback_arr.append(self.exc_traceback)
  return bstack11l1ll1l1_opy_
def bstack1l111111ll_opy_(runner, hook_name, context, element, bstack111lll1ll1_opy_, *args):
  try:
    if runner.hooks.get(hook_name):
      bstack11l1ll111_opy_.bstack11l1ll1l11_opy_(hook_name, element)
    bstack111lll1ll1_opy_(runner, hook_name, context, *args)
    if runner.hooks.get(hook_name):
      bstack11l1ll111_opy_.bstack1l1llll1ll_opy_(element)
      if hook_name not in [bstack11ll1_opy_ (u"ࠩࡥࡩ࡫ࡵࡲࡦࡡࡤࡰࡱ࠭ఊ"), bstack11ll1_opy_ (u"ࠪࡥ࡫ࡺࡥࡳࡡࡤࡰࡱ࠭ఋ")] and args and hasattr(args[0], bstack11ll1_opy_ (u"ࠫࡪࡸࡲࡰࡴࡢࡱࡪࡹࡳࡢࡩࡨࠫఌ")):
        args[0].error_message = bstack11ll1_opy_ (u"ࠬ࠭఍")
  except Exception as e:
    logger.debug(bstack11ll1_opy_ (u"࠭ࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢ࡫ࡥࡳࡪ࡬ࡦࠢ࡫ࡳࡴࡱࡳࠡ࡫ࡱࠤࡧ࡫ࡨࡢࡸࡨ࠾ࠥࢁࡽࠨఎ").format(str(e)))
@measure(event_name=EVENTS.bstack11l1llllll_opy_, stage=STAGE.bstack11l1llll1_opy_, hook_type=bstack11ll1_opy_ (u"ࠢࡣࡧࡩࡳࡷ࡫ࡁ࡭࡮ࠥఏ"), bstack1lll1l1l1_opy_=bstack1ll1l11111_opy_)
def bstack1ll1ll1l_opy_(runner, name, context, bstack111lll1ll1_opy_, *args):
    if runner.hooks.get(bstack11ll1_opy_ (u"ࠣࡤࡨࡪࡴࡸࡥࡠࡣ࡯ࡰࠧఐ")).__name__ != bstack11ll1_opy_ (u"ࠤࡥࡩ࡫ࡵࡲࡦࡡࡤࡰࡱࡥࡤࡦࡨࡤࡹࡱࡺ࡟ࡩࡱࡲ࡯ࠧ఑"):
      bstack1l111111ll_opy_(runner, name, context, runner, bstack111lll1ll1_opy_, *args)
    try:
      threading.current_thread().bstackSessionDriver if bstack111llll11l_opy_(bstack11ll1_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭ࡖࡩࡸࡹࡩࡰࡰࡇࡶ࡮ࡼࡥࡳࠩఒ")) else context.browser
      runner.driver_initialised = bstack11ll1_opy_ (u"ࠦࡧ࡫ࡦࡰࡴࡨࡣࡦࡲ࡬ࠣఓ")
    except Exception as e:
      logger.debug(bstack11ll1_opy_ (u"ࠬࡌࡡࡪ࡮ࡨࡨࠥࡺ࡯ࠡࡵࡨࡸࠥࡪࡲࡪࡸࡨࡶࠥ࡯࡮ࡪࡶ࡬ࡥࡱ࡯ࡳࡦࠢࡤࡸࡹࡸࡩࡣࡷࡷࡩ࠿ࠦࡻࡾࠩఔ").format(str(e)))
def bstack11lll1lll1_opy_(runner, name, context, bstack111lll1ll1_opy_, *args):
    bstack1l111111ll_opy_(runner, name, context, context.feature, bstack111lll1ll1_opy_, *args)
    try:
      if not bstack1111ll1l1_opy_:
        bstack11l1l1l1l1_opy_ = threading.current_thread().bstackSessionDriver if bstack111llll11l_opy_(bstack11ll1_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰ࡙ࡥࡴࡵ࡬ࡳࡳࡊࡲࡪࡸࡨࡶࠬక")) else context.browser
        if is_driver_active(bstack11l1l1l1l1_opy_):
          if runner.driver_initialised is None: runner.driver_initialised = bstack11ll1_opy_ (u"ࠢࡣࡧࡩࡳࡷ࡫࡟ࡧࡧࡤࡸࡺࡸࡥࠣఖ")
          bstack1111l1ll_opy_ = str(runner.feature.name)
          bstack1ll1l111ll_opy_(context, bstack1111l1ll_opy_)
          bstack11l1l1l1l1_opy_.execute_script(bstack11ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࡿࠧࡧࡣࡵ࡫ࡲࡲࠧࡀࠠࠣࡵࡨࡸࡘ࡫ࡳࡴ࡫ࡲࡲࡓࡧ࡭ࡦࠤ࠯ࠤࠧࡧࡲࡨࡷࡰࡩࡳࡺࡳࠣ࠼ࠣࡿࠧࡴࡡ࡮ࡧࠥ࠾ࠥ࠭గ") + json.dumps(bstack1111l1ll_opy_) + bstack11ll1_opy_ (u"ࠩࢀࢁࠬఘ"))
    except Exception as e:
      logger.debug(bstack11ll1_opy_ (u"ࠪࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦࡳࡦࡶࠣࡷࡪࡹࡳࡪࡱࡱࠤࡳࡧ࡭ࡦࠢ࡬ࡲࠥࡨࡥࡧࡱࡵࡩࠥ࡬ࡥࡢࡶࡸࡶࡪࡀࠠࡼࡿࠪఙ").format(str(e)))
def bstack11lll1l1ll_opy_(runner, name, context, bstack111lll1ll1_opy_, *args):
    if hasattr(context, bstack11ll1_opy_ (u"ࠫࡸࡩࡥ࡯ࡣࡵ࡭ࡴ࠭చ")):
        bstack11l1ll111_opy_.start_test(context)
    target = context.scenario if hasattr(context, bstack11ll1_opy_ (u"ࠬࡹࡣࡦࡰࡤࡶ࡮ࡵࠧఛ")) else context.feature
    bstack1l111111ll_opy_(runner, name, context, target, bstack111lll1ll1_opy_, *args)
@measure(event_name=EVENTS.bstack11l11ll1l_opy_, stage=STAGE.bstack11l1llll1_opy_, bstack1lll1l1l1_opy_=bstack1ll1l11111_opy_)
def bstack11l1lll1l1_opy_(runner, name, context, bstack111lll1ll1_opy_, *args):
    if len(context.scenario.tags) == 0: bstack11l1ll111_opy_.start_test(context)
    bstack1l111111ll_opy_(runner, name, context, context.scenario, bstack111lll1ll1_opy_, *args)
    threading.current_thread().a11y_stop = False
    bstack11l1111l1l_opy_.bstack1l11111lll_opy_(context, *args)
    try:
      bstack11l1l1l1l1_opy_ = bstack1lll11l1l_opy_(threading.current_thread(), bstack11ll1_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰ࡙ࡥࡴࡵ࡬ࡳࡳࡊࡲࡪࡸࡨࡶࠬజ"), context.browser)
      if is_driver_active(bstack11l1l1l1l1_opy_):
        bstack11lll11l11_opy_.bstack1ll1lll111_opy_(bstack1lll11l1l_opy_(threading.current_thread(), bstack11ll1_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱࡓࡦࡵࡶ࡭ࡴࡴࡄࡳ࡫ࡹࡩࡷ࠭ఝ"), {}))
        if runner.driver_initialised is None: runner.driver_initialised = bstack11ll1_opy_ (u"ࠣࡤࡨࡪࡴࡸࡥࡠࡵࡦࡩࡳࡧࡲࡪࡱࠥఞ")
        if (not bstack1111ll1l1_opy_):
          scenario_name = args[0].name
          feature_name = bstack1111l1ll_opy_ = str(runner.feature.name)
          bstack1111l1ll_opy_ = feature_name + bstack11ll1_opy_ (u"ࠩࠣ࠱ࠥ࠭ట") + scenario_name
          if runner.driver_initialised == bstack11ll1_opy_ (u"ࠥࡦࡪ࡬࡯ࡳࡧࡢࡷࡨ࡫࡮ࡢࡴ࡬ࡳࠧఠ"):
            bstack1ll1l111ll_opy_(context, bstack1111l1ll_opy_)
            bstack11l1l1l1l1_opy_.execute_script(bstack11ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡩࡽ࡫ࡣࡶࡶࡲࡶ࠿ࠦࡻࠣࡣࡦࡸ࡮ࡵ࡮ࠣ࠼ࠣࠦࡸ࡫ࡴࡔࡧࡶࡷ࡮ࡵ࡮ࡏࡣࡰࡩࠧ࠲ࠠࠣࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠦ࠿ࠦࡻࠣࡰࡤࡱࡪࠨ࠺ࠡࠩడ") + json.dumps(bstack1111l1ll_opy_) + bstack11ll1_opy_ (u"ࠬࢃࡽࠨఢ"))
    except Exception as e:
      logger.debug(bstack11ll1_opy_ (u"࠭ࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡶࡩࡹࠦࡳࡦࡵࡶ࡭ࡴࡴࠠ࡯ࡣࡰࡩࠥ࡯࡮ࠡࡤࡨࡪࡴࡸࡥࠡࡵࡦࡩࡳࡧࡲࡪࡱ࠽ࠤࢀࢃࠧణ").format(str(e)))
@measure(event_name=EVENTS.bstack11l1llllll_opy_, stage=STAGE.bstack11l1llll1_opy_, hook_type=bstack11ll1_opy_ (u"ࠢࡣࡧࡩࡳࡷ࡫ࡓࡵࡧࡳࠦత"), bstack1lll1l1l1_opy_=bstack1ll1l11111_opy_)
def bstack11lllll111_opy_(runner, name, context, bstack111lll1ll1_opy_, *args):
    bstack1l111111ll_opy_(runner, name, context, args[0], bstack111lll1ll1_opy_, *args)
    try:
      bstack11l1l1l1l1_opy_ = threading.current_thread().bstackSessionDriver if bstack111llll11l_opy_(bstack11ll1_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫ࡔࡧࡶࡷ࡮ࡵ࡮ࡅࡴ࡬ࡺࡪࡸࠧథ")) else context.browser
      if is_driver_active(bstack11l1l1l1l1_opy_):
        if runner.driver_initialised is None: runner.driver_initialised = bstack11ll1_opy_ (u"ࠤࡥࡩ࡫ࡵࡲࡦࡡࡶࡸࡪࡶࠢద")
        bstack11l1ll111_opy_.bstack1lll11ll1l_opy_(args[0])
        if runner.driver_initialised == bstack11ll1_opy_ (u"ࠥࡦࡪ࡬࡯ࡳࡧࡢࡷࡹ࡫ࡰࠣధ"):
          feature_name = bstack1111l1ll_opy_ = str(runner.feature.name)
          bstack1111l1ll_opy_ = feature_name + bstack11ll1_opy_ (u"ࠫࠥ࠳ࠠࠨన") + context.scenario.name
          bstack11l1l1l1l1_opy_.execute_script(bstack11ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࡼࠤࡤࡧࡹ࡯࡯࡯ࠤ࠽ࠤࠧࡹࡥࡵࡕࡨࡷࡸ࡯࡯࡯ࡐࡤࡱࡪࠨࠬࠡࠤࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠧࡀࠠࡼࠤࡱࡥࡲ࡫ࠢ࠻ࠢࠪ఩") + json.dumps(bstack1111l1ll_opy_) + bstack11ll1_opy_ (u"࠭ࡽࡾࠩప"))
    except Exception as e:
      logger.debug(bstack11ll1_opy_ (u"ࠧࡇࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡷࡪࡺࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠡࡰࡤࡱࡪࠦࡩ࡯ࠢࡥࡩ࡫ࡵࡲࡦࠢࡶࡸࡪࡶ࠺ࠡࡽࢀࠫఫ").format(str(e)))
@measure(event_name=EVENTS.bstack11l1llllll_opy_, stage=STAGE.bstack11l1llll1_opy_, hook_type=bstack11ll1_opy_ (u"ࠣࡣࡩࡸࡪࡸࡓࡵࡧࡳࠦబ"), bstack1lll1l1l1_opy_=bstack1ll1l11111_opy_)
def bstack1ll111llll_opy_(runner, name, context, bstack111lll1ll1_opy_, *args):
  bstack11l1ll111_opy_.bstack11ll11lll_opy_(args[0])
  try:
    step_status = args[0].status.name
    bstack11l1l1l1l1_opy_ = threading.current_thread().bstackSessionDriver if bstack11ll1_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬ࡕࡨࡷࡸ࡯࡯࡯ࡆࡵ࡭ࡻ࡫ࡲࠨభ") in threading.current_thread().__dict__.keys() else context.browser
    if is_driver_active(bstack11l1l1l1l1_opy_):
      if runner.driver_initialised is None:
        runner.driver_initialised  = bstack11ll1_opy_ (u"ࠪ࡭ࡳࡹࡴࡦࡲࠪమ")
        feature_name = bstack1111l1ll_opy_ = str(runner.feature.name)
        bstack1111l1ll_opy_ = feature_name + bstack11ll1_opy_ (u"ࠫࠥ࠳ࠠࠨయ") + context.scenario.name
        bstack11l1l1l1l1_opy_.execute_script(bstack11ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࡼࠤࡤࡧࡹ࡯࡯࡯ࠤ࠽ࠤࠧࡹࡥࡵࡕࡨࡷࡸ࡯࡯࡯ࡐࡤࡱࡪࠨࠬࠡࠤࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠧࡀࠠࡼࠤࡱࡥࡲ࡫ࠢ࠻ࠢࠪర") + json.dumps(bstack1111l1ll_opy_) + bstack11ll1_opy_ (u"࠭ࡽࡾࠩఱ"))
    if str(step_status).lower() == bstack11ll1_opy_ (u"ࠧࡧࡣ࡬ࡰࡪࡪࠧల"):
      bstack1ll111l1l_opy_ = bstack11ll1_opy_ (u"ࠨࠩళ")
      bstack1l1111111_opy_ = bstack11ll1_opy_ (u"ࠩࠪఴ")
      bstack11l111llll_opy_ = bstack11ll1_opy_ (u"ࠪࠫవ")
      try:
        import traceback
        bstack1ll111l1l_opy_ = runner.exception.__class__.__name__
        bstack1l11lll11_opy_ = traceback.format_tb(runner.exc_traceback)
        bstack1l1111111_opy_ = bstack11ll1_opy_ (u"ࠫࠥ࠭శ").join(bstack1l11lll11_opy_)
        bstack11l111llll_opy_ = bstack1l11lll11_opy_[-1]
      except Exception as e:
        logger.debug(bstack11llll1lll_opy_.format(str(e)))
      bstack1ll111l1l_opy_ += bstack11l111llll_opy_
      bstack1l111l111_opy_(context, json.dumps(str(args[0].name) + bstack11ll1_opy_ (u"ࠧࠦ࠭ࠡࡈࡤ࡭ࡱ࡫ࡤࠢ࡞ࡱࠦష") + str(bstack1l1111111_opy_)),
                          bstack11ll1_opy_ (u"ࠨࡥࡳࡴࡲࡶࠧస"))
      if runner.driver_initialised == bstack11ll1_opy_ (u"ࠢࡣࡧࡩࡳࡷ࡫࡟ࡴࡶࡨࡴࠧహ"):
        bstack11l11111ll_opy_(getattr(context, bstack11ll1_opy_ (u"ࠨࡲࡤ࡫ࡪ࠭఺"), None), bstack11ll1_opy_ (u"ࠤࡩࡥ࡮ࡲࡥࡥࠤ఻"), bstack1ll111l1l_opy_)
        bstack11l1l1l1l1_opy_.execute_script(bstack11ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡨࡼࡪࡩࡵࡵࡱࡵ࠾ࠥࢁࠢࡢࡥࡷ࡭ࡴࡴࠢ࠻ࠢࠥࡥࡳࡴ࡯ࡵࡣࡷࡩࠧ࠲ࠠࠣࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠦ࠿ࠦࡻࠣࡦࡤࡸࡦࠨ࠺ࠨ఼") + json.dumps(str(args[0].name) + bstack11ll1_opy_ (u"ࠦࠥ࠳ࠠࡇࡣ࡬ࡰࡪࡪࠡ࡝ࡰࠥఽ") + str(bstack1l1111111_opy_)) + bstack11ll1_opy_ (u"ࠬ࠲ࠠࠣ࡮ࡨࡺࡪࡲࠢ࠻ࠢࠥࡩࡷࡸ࡯ࡳࠤࢀࢁࠬా"))
      if runner.driver_initialised == bstack11ll1_opy_ (u"ࠨࡢࡦࡨࡲࡶࡪࡥࡳࡵࡧࡳࠦి"):
        bstack1ll11ll1ll_opy_(bstack11l1l1l1l1_opy_, bstack11ll1_opy_ (u"ࠧࡧࡣ࡬ࡰࡪࡪࠧీ"), bstack11ll1_opy_ (u"ࠣࡕࡦࡩࡳࡧࡲࡪࡱࠣࡪࡦ࡯࡬ࡦࡦࠣࡻ࡮ࡺࡨ࠻ࠢ࡟ࡲࠧు") + str(bstack1ll111l1l_opy_))
    else:
      bstack1l111l111_opy_(context, bstack11ll1_opy_ (u"ࠤࡓࡥࡸࡹࡥࡥࠣࠥూ"), bstack11ll1_opy_ (u"ࠥ࡭ࡳ࡬࡯ࠣృ"))
      if runner.driver_initialised == bstack11ll1_opy_ (u"ࠦࡧ࡫ࡦࡰࡴࡨࡣࡸࡺࡥࡱࠤౄ"):
        bstack11l11111ll_opy_(getattr(context, bstack11ll1_opy_ (u"ࠬࡶࡡࡨࡧࠪ౅"), None), bstack11ll1_opy_ (u"ࠨࡰࡢࡵࡶࡩࡩࠨె"))
      bstack11l1l1l1l1_opy_.execute_script(bstack11ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡥࡹࡧࡦࡹࡹࡵࡲ࠻ࠢࡾࠦࡦࡩࡴࡪࡱࡱࠦ࠿ࠦࠢࡢࡰࡱࡳࡹࡧࡴࡦࠤ࠯ࠤࠧࡧࡲࡨࡷࡰࡩࡳࡺࡳࠣ࠼ࠣࡿࠧࡪࡡࡵࡣࠥ࠾ࠬే") + json.dumps(str(args[0].name) + bstack11ll1_opy_ (u"ࠣࠢ࠰ࠤࡕࡧࡳࡴࡧࡧࠥࠧై")) + bstack11ll1_opy_ (u"ࠩ࠯ࠤࠧࡲࡥࡷࡧ࡯ࠦ࠿ࠦࠢࡪࡰࡩࡳࠧࢃࡽࠨ౉"))
      if runner.driver_initialised == bstack11ll1_opy_ (u"ࠥࡦࡪ࡬࡯ࡳࡧࡢࡷࡹ࡫ࡰࠣొ"):
        bstack1ll11ll1ll_opy_(bstack11l1l1l1l1_opy_, bstack11ll1_opy_ (u"ࠦࡵࡧࡳࡴࡧࡧࠦో"))
  except Exception as e:
    logger.debug(bstack11ll1_opy_ (u"ࠬࡌࡡࡪ࡮ࡨࡨࠥࡺ࡯ࠡ࡯ࡤࡶࡰࠦࡳࡦࡵࡶ࡭ࡴࡴࠠࡴࡶࡤࡸࡺࡹࠠࡪࡰࠣࡥ࡫ࡺࡥࡳࠢࡶࡸࡪࡶ࠺ࠡࡽࢀࠫౌ").format(str(e)))
  bstack1l111111ll_opy_(runner, name, context, args[0], bstack111lll1ll1_opy_, *args)
@measure(event_name=EVENTS.bstack1l11l1l11l_opy_, stage=STAGE.bstack11l1llll1_opy_, bstack1lll1l1l1_opy_=bstack1ll1l11111_opy_)
def bstack1l1ll1l1_opy_(runner, name, context, bstack111lll1ll1_opy_, *args):
  bstack11l1ll111_opy_.end_test(args[0])
  try:
    bstack1111111l1_opy_ = args[0].status.name
    bstack11l1l1l1l1_opy_ = bstack1lll11l1l_opy_(threading.current_thread(), bstack11ll1_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰ࡙ࡥࡴࡵ࡬ࡳࡳࡊࡲࡪࡸࡨࡶ్ࠬ"), context.browser)
    bstack11l1111l1l_opy_.bstack1l1l1l1lll_opy_(bstack11l1l1l1l1_opy_)
    if str(bstack1111111l1_opy_).lower() == bstack11ll1_opy_ (u"ࠧࡧࡣ࡬ࡰࡪࡪࠧ౎"):
      bstack1ll111l1l_opy_ = bstack11ll1_opy_ (u"ࠨࠩ౏")
      bstack1l1111111_opy_ = bstack11ll1_opy_ (u"ࠩࠪ౐")
      bstack11l111llll_opy_ = bstack11ll1_opy_ (u"ࠪࠫ౑")
      try:
        import traceback
        bstack1ll111l1l_opy_ = runner.exception.__class__.__name__
        bstack1l11lll11_opy_ = traceback.format_tb(runner.exc_traceback)
        bstack1l1111111_opy_ = bstack11ll1_opy_ (u"ࠫࠥ࠭౒").join(bstack1l11lll11_opy_)
        bstack11l111llll_opy_ = bstack1l11lll11_opy_[-1]
      except Exception as e:
        logger.debug(bstack11llll1lll_opy_.format(str(e)))
      bstack1ll111l1l_opy_ += bstack11l111llll_opy_
      bstack1l111l111_opy_(context, json.dumps(str(args[0].name) + bstack11ll1_opy_ (u"ࠧࠦ࠭ࠡࡈࡤ࡭ࡱ࡫ࡤࠢ࡞ࡱࠦ౓") + str(bstack1l1111111_opy_)),
                          bstack11ll1_opy_ (u"ࠨࡥࡳࡴࡲࡶࠧ౔"))
      if runner.driver_initialised == bstack11ll1_opy_ (u"ࠢࡣࡧࡩࡳࡷ࡫࡟ࡴࡥࡨࡲࡦࡸࡩࡰࠤౕ") or runner.driver_initialised == bstack11ll1_opy_ (u"ࠨ࡫ࡱࡷࡹ࡫ࡰࠨౖ"):
        bstack11l11111ll_opy_(getattr(context, bstack11ll1_opy_ (u"ࠩࡳࡥ࡬࡫ࠧ౗"), None), bstack11ll1_opy_ (u"ࠥࡪࡦ࡯࡬ࡦࡦࠥౘ"), bstack1ll111l1l_opy_)
        bstack11l1l1l1l1_opy_.execute_script(bstack11ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡩࡽ࡫ࡣࡶࡶࡲࡶ࠿ࠦࡻࠣࡣࡦࡸ࡮ࡵ࡮ࠣ࠼ࠣࠦࡦࡴ࡮ࡰࡶࡤࡸࡪࠨࠬࠡࠤࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠧࡀࠠࡼࠤࡧࡥࡹࡧࠢ࠻ࠩౙ") + json.dumps(str(args[0].name) + bstack11ll1_opy_ (u"ࠧࠦ࠭ࠡࡈࡤ࡭ࡱ࡫ࡤࠢ࡞ࡱࠦౚ") + str(bstack1l1111111_opy_)) + bstack11ll1_opy_ (u"࠭ࠬࠡࠤ࡯ࡩࡻ࡫࡬ࠣ࠼ࠣࠦࡪࡸࡲࡰࡴࠥࢁࢂ࠭౛"))
      if runner.driver_initialised == bstack11ll1_opy_ (u"ࠢࡣࡧࡩࡳࡷ࡫࡟ࡴࡥࡨࡲࡦࡸࡩࡰࠤ౜") or runner.driver_initialised == bstack11ll1_opy_ (u"ࠨ࡫ࡱࡷࡹ࡫ࡰࠨౝ"):
        bstack1ll11ll1ll_opy_(bstack11l1l1l1l1_opy_, bstack11ll1_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࠩ౞"), bstack11ll1_opy_ (u"ࠥࡗࡨ࡫࡮ࡢࡴ࡬ࡳࠥ࡬ࡡࡪ࡮ࡨࡨࠥࡽࡩࡵࡪ࠽ࠤࡡࡴࠢ౟") + str(bstack1ll111l1l_opy_))
    else:
      bstack1l111l111_opy_(context, bstack11ll1_opy_ (u"ࠦࡕࡧࡳࡴࡧࡧࠥࠧౠ"), bstack11ll1_opy_ (u"ࠧ࡯࡮ࡧࡱࠥౡ"))
      if runner.driver_initialised == bstack11ll1_opy_ (u"ࠨࡢࡦࡨࡲࡶࡪࡥࡳࡤࡧࡱࡥࡷ࡯࡯ࠣౢ") or runner.driver_initialised == bstack11ll1_opy_ (u"ࠧࡪࡰࡶࡸࡪࡶࠧౣ"):
        bstack11l11111ll_opy_(getattr(context, bstack11ll1_opy_ (u"ࠨࡲࡤ࡫ࡪ࠭౤"), None), bstack11ll1_opy_ (u"ࠤࡳࡥࡸࡹࡥࡥࠤ౥"))
      bstack11l1l1l1l1_opy_.execute_script(bstack11ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡨࡼࡪࡩࡵࡵࡱࡵ࠾ࠥࢁࠢࡢࡥࡷ࡭ࡴࡴࠢ࠻ࠢࠥࡥࡳࡴ࡯ࡵࡣࡷࡩࠧ࠲ࠠࠣࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠦ࠿ࠦࡻࠣࡦࡤࡸࡦࠨ࠺ࠨ౦") + json.dumps(str(args[0].name) + bstack11ll1_opy_ (u"ࠦࠥ࠳ࠠࡑࡣࡶࡷࡪࡪࠡࠣ౧")) + bstack11ll1_opy_ (u"ࠬ࠲ࠠࠣ࡮ࡨࡺࡪࡲࠢ࠻ࠢࠥ࡭ࡳ࡬࡯ࠣࡿࢀࠫ౨"))
      if runner.driver_initialised == bstack11ll1_opy_ (u"ࠨࡢࡦࡨࡲࡶࡪࡥࡳࡤࡧࡱࡥࡷ࡯࡯ࠣ౩") or runner.driver_initialised == bstack11ll1_opy_ (u"ࠧࡪࡰࡶࡸࡪࡶࠧ౪"):
        bstack1ll11ll1ll_opy_(bstack11l1l1l1l1_opy_, bstack11ll1_opy_ (u"ࠣࡲࡤࡷࡸ࡫ࡤࠣ౫"))
  except Exception as e:
    logger.debug(bstack11ll1_opy_ (u"ࠩࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥࡳࡡࡳ࡭ࠣࡷࡪࡹࡳࡪࡱࡱࠤࡸࡺࡡࡵࡷࡶࠤ࡮ࡴࠠࡢࡨࡷࡩࡷࠦࡦࡦࡣࡷࡹࡷ࡫࠺ࠡࡽࢀࠫ౬").format(str(e)))
  bstack1l111111ll_opy_(runner, name, context, context.scenario, bstack111lll1ll1_opy_, *args)
  if len(context.scenario.tags) == 0: threading.current_thread().current_test_uuid = None
def bstack1l11ll1lll_opy_(runner, name, context, bstack111lll1ll1_opy_, *args):
    target = context.scenario if hasattr(context, bstack11ll1_opy_ (u"ࠪࡷࡨ࡫࡮ࡢࡴ࡬ࡳࠬ౭")) else context.feature
    bstack1l111111ll_opy_(runner, name, context, target, bstack111lll1ll1_opy_, *args)
    threading.current_thread().current_test_uuid = None
def bstack1ll11llll1_opy_(runner, name, context, bstack111lll1ll1_opy_, *args):
    try:
      bstack11l1l1l1l1_opy_ = bstack1lll11l1l_opy_(threading.current_thread(), bstack11ll1_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮ࡗࡪࡹࡳࡪࡱࡱࡈࡷ࡯ࡶࡦࡴࠪ౮"), context.browser)
      bstack11111lll1_opy_ = bstack11ll1_opy_ (u"ࠬ࠭౯")
      if context.failed is True:
        bstack1l1l1lll11_opy_ = []
        bstack1l1l1lll1l_opy_ = []
        bstack1111l111l_opy_ = []
        try:
          import traceback
          for exc in runner.exception_arr:
            bstack1l1l1lll11_opy_.append(exc.__class__.__name__)
          for exc_tb in runner.exc_traceback_arr:
            bstack1l11lll11_opy_ = traceback.format_tb(exc_tb)
            bstack11llll11l1_opy_ = bstack11ll1_opy_ (u"࠭ࠠࠨ౰").join(bstack1l11lll11_opy_)
            bstack1l1l1lll1l_opy_.append(bstack11llll11l1_opy_)
            bstack1111l111l_opy_.append(bstack1l11lll11_opy_[-1])
        except Exception as e:
          logger.debug(bstack11llll1lll_opy_.format(str(e)))
        bstack1ll111l1l_opy_ = bstack11ll1_opy_ (u"ࠧࠨ౱")
        for i in range(len(bstack1l1l1lll11_opy_)):
          bstack1ll111l1l_opy_ += bstack1l1l1lll11_opy_[i] + bstack1111l111l_opy_[i] + bstack11ll1_opy_ (u"ࠨ࡞ࡱࠫ౲")
        bstack11111lll1_opy_ = bstack11ll1_opy_ (u"ࠩࠣࠫ౳").join(bstack1l1l1lll1l_opy_)
        if runner.driver_initialised in [bstack11ll1_opy_ (u"ࠥࡦࡪ࡬࡯ࡳࡧࡢࡪࡪࡧࡴࡶࡴࡨࠦ౴"), bstack11ll1_opy_ (u"ࠦࡧ࡫ࡦࡰࡴࡨࡣࡦࡲ࡬ࠣ౵")]:
          bstack1l111l111_opy_(context, bstack11111lll1_opy_, bstack11ll1_opy_ (u"ࠧ࡫ࡲࡳࡱࡵࠦ౶"))
          bstack11l11111ll_opy_(getattr(context, bstack11ll1_opy_ (u"࠭ࡰࡢࡩࡨࠫ౷"), None), bstack11ll1_opy_ (u"ࠢࡧࡣ࡬ࡰࡪࡪࠢ౸"), bstack1ll111l1l_opy_)
          bstack11l1l1l1l1_opy_.execute_script(bstack11ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࡿࠧࡧࡣࡵ࡫ࡲࡲࠧࡀࠠࠣࡣࡱࡲࡴࡺࡡࡵࡧࠥ࠰ࠥࠨࡡࡳࡩࡸࡱࡪࡴࡴࡴࠤ࠽ࠤࢀࠨࡤࡢࡶࡤࠦ࠿࠭౹") + json.dumps(bstack11111lll1_opy_) + bstack11ll1_opy_ (u"ࠩ࠯ࠤࠧࡲࡥࡷࡧ࡯ࠦ࠿ࠦࠢࡦࡴࡵࡳࡷࠨࡽࡾࠩ౺"))
          bstack1ll11ll1ll_opy_(bstack11l1l1l1l1_opy_, bstack11ll1_opy_ (u"ࠥࡪࡦ࡯࡬ࡦࡦࠥ౻"), bstack11ll1_opy_ (u"ࠦࡘࡵ࡭ࡦࠢࡶࡧࡪࡴࡡࡳ࡫ࡲࡷࠥ࡬ࡡࡪ࡮ࡨࡨ࠿ࠦ࡜࡯ࠤ౼") + str(bstack1ll111l1l_opy_))
          bstack1l11111l11_opy_ = bstack11lllllll_opy_(bstack11111lll1_opy_, runner.feature.name, logger)
          if (bstack1l11111l11_opy_ != None):
            bstack1ll1l1l1l1_opy_.append(bstack1l11111l11_opy_)
      else:
        if runner.driver_initialised in [bstack11ll1_opy_ (u"ࠧࡨࡥࡧࡱࡵࡩࡤ࡬ࡥࡢࡶࡸࡶࡪࠨ౽"), bstack11ll1_opy_ (u"ࠨࡢࡦࡨࡲࡶࡪࡥࡡ࡭࡮ࠥ౾")]:
          bstack1l111l111_opy_(context, bstack11ll1_opy_ (u"ࠢࡇࡧࡤࡸࡺࡸࡥ࠻ࠢࠥ౿") + str(runner.feature.name) + bstack11ll1_opy_ (u"ࠣࠢࡳࡥࡸࡹࡥࡥࠣࠥಀ"), bstack11ll1_opy_ (u"ࠤ࡬ࡲ࡫ࡵࠢಁ"))
          bstack11l11111ll_opy_(getattr(context, bstack11ll1_opy_ (u"ࠪࡴࡦ࡭ࡥࠨಂ"), None), bstack11ll1_opy_ (u"ࠦࡵࡧࡳࡴࡧࡧࠦಃ"))
          bstack11l1l1l1l1_opy_.execute_script(bstack11ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࡼࠤࡤࡧࡹ࡯࡯࡯ࠤ࠽ࠤࠧࡧ࡮࡯ࡱࡷࡥࡹ࡫ࠢ࠭ࠢࠥࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸࠨ࠺ࠡࡽࠥࡨࡦࡺࡡࠣ࠼ࠪ಄") + json.dumps(bstack11ll1_opy_ (u"ࠨࡆࡦࡣࡷࡹࡷ࡫࠺ࠡࠤಅ") + str(runner.feature.name) + bstack11ll1_opy_ (u"ࠢࠡࡲࡤࡷࡸ࡫ࡤࠢࠤಆ")) + bstack11ll1_opy_ (u"ࠨ࠮ࠣࠦࡱ࡫ࡶࡦ࡮ࠥ࠾ࠥࠨࡩ࡯ࡨࡲࠦࢂࢃࠧಇ"))
          bstack1ll11ll1ll_opy_(bstack11l1l1l1l1_opy_, bstack11ll1_opy_ (u"ࠩࡳࡥࡸࡹࡥࡥࠩಈ"))
          bstack1l11111l11_opy_ = bstack11lllllll_opy_(bstack11111lll1_opy_, runner.feature.name, logger)
          if (bstack1l11111l11_opy_ != None):
            bstack1ll1l1l1l1_opy_.append(bstack1l11111l11_opy_)
    except Exception as e:
      logger.debug(bstack11ll1_opy_ (u"ࠪࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦ࡭ࡢࡴ࡮ࠤࡸ࡫ࡳࡴ࡫ࡲࡲࠥࡹࡴࡢࡶࡸࡷࠥ࡯࡮ࠡࡣࡩࡸࡪࡸࠠࡧࡧࡤࡸࡺࡸࡥ࠻ࠢࡾࢁࠬಉ").format(str(e)))
    bstack1l111111ll_opy_(runner, name, context, context.feature, bstack111lll1ll1_opy_, *args)
@measure(event_name=EVENTS.bstack11l1llllll_opy_, stage=STAGE.bstack11l1llll1_opy_, hook_type=bstack11ll1_opy_ (u"ࠦࡦ࡬ࡴࡦࡴࡄࡰࡱࠨಊ"), bstack1lll1l1l1_opy_=bstack1ll1l11111_opy_)
def bstack1llll1ll_opy_(runner, name, context, bstack111lll1ll1_opy_, *args):
    bstack1l111111ll_opy_(runner, name, context, runner, bstack111lll1ll1_opy_, *args)
def bstack1ll1l11l_opy_(self, name, context, *args):
  try:
    if bstack1llll1l1_opy_:
      platform_index = int(threading.current_thread()._name) % bstack1llll11l1l_opy_
      bstack11lll1ll1_opy_ = CONFIG[bstack11ll1_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨಋ")][platform_index]
      os.environ[bstack11ll1_opy_ (u"࠭ࡃࡖࡔࡕࡉࡓ࡚࡟ࡑࡎࡄࡘࡋࡕࡒࡎࡡࡇࡅ࡙ࡇࠧಌ")] = json.dumps(bstack11lll1ll1_opy_)
    global bstack111lll1ll1_opy_
    if not hasattr(self, bstack11ll1_opy_ (u"ࠧࡥࡴ࡬ࡺࡪࡸ࡟ࡪࡰ࡬ࡸ࡮ࡧ࡬ࡪࡵࡨࡨࠬ಍")):
      self.driver_initialised = None
    bstack11l1ll11_opy_ = {
        bstack11ll1_opy_ (u"ࠨࡤࡨࡪࡴࡸࡥࡠࡣ࡯ࡰࠬಎ"): bstack1ll1ll1l_opy_,
        bstack11ll1_opy_ (u"ࠩࡥࡩ࡫ࡵࡲࡦࡡࡩࡩࡦࡺࡵࡳࡧࠪಏ"): bstack11lll1lll1_opy_,
        bstack11ll1_opy_ (u"ࠪࡦࡪ࡬࡯ࡳࡧࡢࡸࡦ࡭ࠧಐ"): bstack11lll1l1ll_opy_,
        bstack11ll1_opy_ (u"ࠫࡧ࡫ࡦࡰࡴࡨࡣࡸࡩࡥ࡯ࡣࡵ࡭ࡴ࠭಑"): bstack11l1lll1l1_opy_,
        bstack11ll1_opy_ (u"ࠬࡨࡥࡧࡱࡵࡩࡤࡹࡴࡦࡲࠪಒ"): bstack11lllll111_opy_,
        bstack11ll1_opy_ (u"࠭ࡡࡧࡶࡨࡶࡤࡹࡴࡦࡲࠪಓ"): bstack1ll111llll_opy_,
        bstack11ll1_opy_ (u"ࠧࡢࡨࡷࡩࡷࡥࡳࡤࡧࡱࡥࡷ࡯࡯ࠨಔ"): bstack1l1ll1l1_opy_,
        bstack11ll1_opy_ (u"ࠨࡣࡩࡸࡪࡸ࡟ࡵࡣࡪࠫಕ"): bstack1l11ll1lll_opy_,
        bstack11ll1_opy_ (u"ࠩࡤࡪࡹ࡫ࡲࡠࡨࡨࡥࡹࡻࡲࡦࠩಖ"): bstack1ll11llll1_opy_,
        bstack11ll1_opy_ (u"ࠪࡥ࡫ࡺࡥࡳࡡࡤࡰࡱ࠭ಗ"): bstack1llll1ll_opy_
    }
    handler = bstack11l1ll11_opy_.get(name, bstack111lll1ll1_opy_)
    try:
      handler(self, name, context, bstack111lll1ll1_opy_, *args)
    except Exception as e:
      logger.debug(bstack11ll1_opy_ (u"ࠫࡊࡸࡲࡰࡴࠣ࡭ࡳࠦࡢࡦࡪࡤࡺࡪࠦࡨࡰࡱ࡮ࠤ࡭ࡧ࡮ࡥ࡮ࡨࡶࠥࢁࡽ࠻ࠢࡾࢁࠬಘ").format(name, str(e)))
    if name in [bstack11ll1_opy_ (u"ࠬࡧࡦࡵࡧࡵࡣ࡫࡫ࡡࡵࡷࡵࡩࠬಙ"), bstack11ll1_opy_ (u"࠭ࡡࡧࡶࡨࡶࡤࡹࡣࡦࡰࡤࡶ࡮ࡵࠧಚ"), bstack11ll1_opy_ (u"ࠧࡢࡨࡷࡩࡷࡥࡡ࡭࡮ࠪಛ")]:
      try:
        bstack11l1l1l1l1_opy_ = threading.current_thread().bstackSessionDriver if bstack111llll11l_opy_(bstack11ll1_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫ࡔࡧࡶࡷ࡮ࡵ࡮ࡅࡴ࡬ࡺࡪࡸࠧಜ")) else context.browser
        bstack11ll1ll1l_opy_ = (
          (name == bstack11ll1_opy_ (u"ࠩࡤࡪࡹ࡫ࡲࡠࡣ࡯ࡰࠬಝ") and self.driver_initialised == bstack11ll1_opy_ (u"ࠥࡦࡪ࡬࡯ࡳࡧࡢࡥࡱࡲࠢಞ")) or
          (name == bstack11ll1_opy_ (u"ࠫࡦ࡬ࡴࡦࡴࡢࡪࡪࡧࡴࡶࡴࡨࠫಟ") and self.driver_initialised == bstack11ll1_opy_ (u"ࠧࡨࡥࡧࡱࡵࡩࡤ࡬ࡥࡢࡶࡸࡶࡪࠨಠ")) or
          (name == bstack11ll1_opy_ (u"࠭ࡡࡧࡶࡨࡶࡤࡹࡣࡦࡰࡤࡶ࡮ࡵࠧಡ") and self.driver_initialised in [bstack11ll1_opy_ (u"ࠢࡣࡧࡩࡳࡷ࡫࡟ࡴࡥࡨࡲࡦࡸࡩࡰࠤಢ"), bstack11ll1_opy_ (u"ࠣ࡫ࡱࡷࡹ࡫ࡰࠣಣ")]) or
          (name == bstack11ll1_opy_ (u"ࠩࡤࡪࡹ࡫ࡲࡠࡵࡷࡩࡵ࠭ತ") and self.driver_initialised == bstack11ll1_opy_ (u"ࠥࡦࡪ࡬࡯ࡳࡧࡢࡷࡹ࡫ࡰࠣಥ"))
        )
        if bstack11ll1ll1l_opy_:
          self.driver_initialised = None
          if bstack11l1l1l1l1_opy_ and hasattr(bstack11l1l1l1l1_opy_, bstack11ll1_opy_ (u"ࠫࡸ࡫ࡳࡴ࡫ࡲࡲࡤ࡯ࡤࠨದ")):
            try:
              bstack11l1l1l1l1_opy_.quit()
            except Exception as e:
              logger.debug(bstack11ll1_opy_ (u"ࠬࡋࡲࡳࡱࡵࠤࡶࡻࡩࡵࡶ࡬ࡲ࡬ࠦࡤࡳ࡫ࡹࡩࡷࠦࡩ࡯ࠢࡥࡩ࡭ࡧࡶࡦࠢ࡫ࡳࡴࡱ࠺ࠡࡽࢀࠫಧ").format(str(e)))
      except Exception as e:
        logger.debug(bstack11ll1_opy_ (u"࠭ࡅࡳࡴࡲࡶࠥ࡯࡮ࠡࡣࡩࡸࡪࡸࠠࡩࡱࡲ࡯ࠥࡩ࡬ࡦࡣࡱࡹࡵࠦࡦࡰࡴࠣࡿࢂࡀࠠࡼࡿࠪನ").format(name, str(e)))
  except Exception as e:
    logger.debug(bstack11ll1_opy_ (u"ࠧࡄࡴ࡬ࡸ࡮ࡩࡡ࡭ࠢࡨࡶࡷࡵࡲࠡ࡫ࡱࠤࡧ࡫ࡨࡢࡸࡨࠤࡷࡻ࡮ࠡࡪࡲࡳࡰࠦࡻࡾ࠼ࠣࡿࢂ࠭಩").format(name, str(e)))
    try:
      bstack111lll1ll1_opy_(self, name, context, *args)
    except Exception as e2:
      logger.debug(bstack11ll1_opy_ (u"ࠨࡇࡵࡶࡴࡸࠠࡪࡰࠣࡪࡦࡲ࡬ࡣࡣࡦ࡯ࠥࡵࡲࡪࡩ࡬ࡲࡦࡲࠠࡣࡧ࡫ࡥࡻ࡫ࠠࡩࡱࡲ࡯ࠥࢁࡽ࠻ࠢࡾࢁࠬಪ").format(name, str(e2)))
def bstack1l111lll11_opy_(config, startdir):
  return bstack11ll1_opy_ (u"ࠤࡧࡶ࡮ࡼࡥࡳ࠼ࠣࡿ࠵ࢃࠢಫ").format(bstack11ll1_opy_ (u"ࠥࡆࡷࡵࡷࡴࡧࡵࡗࡹࡧࡣ࡬ࠤಬ"))
notset = Notset()
def bstack1ll1ll1lll_opy_(self, name: str, default=notset, skip: bool = False):
  global bstack1ll111ll_opy_
  if str(name).lower() == bstack11ll1_opy_ (u"ࠫࡩࡸࡩࡷࡧࡵࠫಭ"):
    return bstack11ll1_opy_ (u"ࠧࡈࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࠦಮ")
  else:
    return bstack1ll111ll_opy_(self, name, default, skip)
def bstack11ll11l1l_opy_(item, when):
  global bstack1l111l11l_opy_
  try:
    bstack1l111l11l_opy_(item, when)
  except Exception as e:
    pass
def bstack1ll1l1ll_opy_():
  return
def bstack1l111l1l_opy_(type, name, status, reason, bstack1ll11ll1_opy_, bstack1ll1l1l11l_opy_):
  bstack111111ll_opy_ = {
    bstack11ll1_opy_ (u"࠭ࡡࡤࡶ࡬ࡳࡳ࠭ಯ"): type,
    bstack11ll1_opy_ (u"ࠧࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠪರ"): {}
  }
  if type == bstack11ll1_opy_ (u"ࠨࡣࡱࡲࡴࡺࡡࡵࡧࠪಱ"):
    bstack111111ll_opy_[bstack11ll1_opy_ (u"ࠩࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠬಲ")][bstack11ll1_opy_ (u"ࠪࡰࡪࡼࡥ࡭ࠩಳ")] = bstack1ll11ll1_opy_
    bstack111111ll_opy_[bstack11ll1_opy_ (u"ࠫࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠧ಴")][bstack11ll1_opy_ (u"ࠬࡪࡡࡵࡣࠪವ")] = json.dumps(str(bstack1ll1l1l11l_opy_))
  if type == bstack11ll1_opy_ (u"࠭ࡳࡦࡶࡖࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠧಶ"):
    bstack111111ll_opy_[bstack11ll1_opy_ (u"ࠧࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠪಷ")][bstack11ll1_opy_ (u"ࠨࡰࡤࡱࡪ࠭ಸ")] = name
  if type == bstack11ll1_opy_ (u"ࠩࡶࡩࡹ࡙ࡥࡴࡵ࡬ࡳࡳ࡙ࡴࡢࡶࡸࡷࠬಹ"):
    bstack111111ll_opy_[bstack11ll1_opy_ (u"ࠪࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸ࠭಺")][bstack11ll1_opy_ (u"ࠫࡸࡺࡡࡵࡷࡶࠫ಻")] = status
    if status == bstack11ll1_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡨࡨ಼ࠬ"):
      bstack111111ll_opy_[bstack11ll1_opy_ (u"࠭ࡡࡳࡩࡸࡱࡪࡴࡴࡴࠩಽ")][bstack11ll1_opy_ (u"ࠧࡳࡧࡤࡷࡴࡴࠧಾ")] = json.dumps(str(reason))
  bstack1l11ll111l_opy_ = bstack11ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࡿࢂ࠭ಿ").format(json.dumps(bstack111111ll_opy_))
  return bstack1l11ll111l_opy_
def bstack1l1ll111_opy_(driver_command, response):
    if driver_command == bstack11ll1_opy_ (u"ࠩࡶࡧࡷ࡫ࡥ࡯ࡵ࡫ࡳࡹ࠭ೀ"):
        bstack11lll11l11_opy_.bstack1l1lll1ll_opy_({
            bstack11ll1_opy_ (u"ࠪ࡭ࡲࡧࡧࡦࠩು"): response[bstack11ll1_opy_ (u"ࠫࡻࡧ࡬ࡶࡧࠪೂ")],
            bstack11ll1_opy_ (u"ࠬࡺࡥࡴࡶࡢࡶࡺࡴ࡟ࡶࡷ࡬ࡨࠬೃ"): bstack11lll11l11_opy_.current_test_uuid()
        })
def bstack111l111l_opy_(item, call, rep):
  global bstack1l11l11ll1_opy_
  global bstack1lll111ll_opy_
  global bstack1111ll1l1_opy_
  name = bstack11ll1_opy_ (u"࠭ࠧೄ")
  try:
    if rep.when == bstack11ll1_opy_ (u"ࠧࡤࡣ࡯ࡰࠬ೅"):
      bstack1l111l111l_opy_ = threading.current_thread().bstackSessionId
      try:
        if not bstack1111ll1l1_opy_:
          name = str(rep.nodeid)
          bstack1l1l1l11ll_opy_ = bstack1l111l1l_opy_(bstack11ll1_opy_ (u"ࠨࡵࡨࡸࡘ࡫ࡳࡴ࡫ࡲࡲࡓࡧ࡭ࡦࠩೆ"), name, bstack11ll1_opy_ (u"ࠩࠪೇ"), bstack11ll1_opy_ (u"ࠪࠫೈ"), bstack11ll1_opy_ (u"ࠫࠬ೉"), bstack11ll1_opy_ (u"ࠬ࠭ೊ"))
          threading.current_thread().bstack1ll1l1lll_opy_ = name
          for driver in bstack1lll111ll_opy_:
            if bstack1l111l111l_opy_ == driver.session_id:
              driver.execute_script(bstack1l1l1l11ll_opy_)
      except Exception as e:
        logger.debug(bstack11ll1_opy_ (u"࠭ࡅࡳࡴࡲࡶࠥ࡯࡮ࠡࡵࡨࡸࡹ࡯࡮ࡨࠢࡶࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠠࡧࡱࡵࠤࡵࡿࡴࡦࡵࡷ࠱ࡧࡪࡤࠡࡵࡨࡷࡸ࡯࡯࡯࠼ࠣࡿࢂ࠭ೋ").format(str(e)))
      try:
        bstack1l11ll1111_opy_(rep.outcome.lower())
        if rep.outcome.lower() != bstack11ll1_opy_ (u"ࠧࡴ࡭࡬ࡴࡵ࡫ࡤࠨೌ"):
          status = bstack11ll1_opy_ (u"ࠨࡨࡤ࡭ࡱ࡫ࡤࠨ್") if rep.outcome.lower() == bstack11ll1_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࠩ೎") else bstack11ll1_opy_ (u"ࠪࡴࡦࡹࡳࡦࡦࠪ೏")
          reason = bstack11ll1_opy_ (u"ࠫࠬ೐")
          if status == bstack11ll1_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡨࡨࠬ೑"):
            reason = rep.longrepr.reprcrash.message
            if (not threading.current_thread().bstackTestErrorMessages):
              threading.current_thread().bstackTestErrorMessages = []
            threading.current_thread().bstackTestErrorMessages.append(reason)
          level = bstack11ll1_opy_ (u"࠭ࡩ࡯ࡨࡲࠫ೒") if status == bstack11ll1_opy_ (u"ࠧࡱࡣࡶࡷࡪࡪࠧ೓") else bstack11ll1_opy_ (u"ࠨࡧࡵࡶࡴࡸࠧ೔")
          data = name + bstack11ll1_opy_ (u"ࠩࠣࡴࡦࡹࡳࡦࡦࠤࠫೕ") if status == bstack11ll1_opy_ (u"ࠪࡴࡦࡹࡳࡦࡦࠪೖ") else name + bstack11ll1_opy_ (u"ࠫࠥ࡬ࡡࡪ࡮ࡨࡨࠦࠦࠧ೗") + reason
          bstack1llllll11_opy_ = bstack1l111l1l_opy_(bstack11ll1_opy_ (u"ࠬࡧ࡮࡯ࡱࡷࡥࡹ࡫ࠧ೘"), bstack11ll1_opy_ (u"࠭ࠧ೙"), bstack11ll1_opy_ (u"ࠧࠨ೚"), bstack11ll1_opy_ (u"ࠨࠩ೛"), level, data)
          for driver in bstack1lll111ll_opy_:
            if bstack1l111l111l_opy_ == driver.session_id:
              driver.execute_script(bstack1llllll11_opy_)
      except Exception as e:
        logger.debug(bstack11ll1_opy_ (u"ࠩࡈࡶࡷࡵࡲࠡ࡫ࡱࠤࡸ࡫ࡴࡵ࡫ࡱ࡫ࠥࡹࡥࡴࡵ࡬ࡳࡳࠦࡣࡰࡰࡷࡩࡽࡺࠠࡧࡱࡵࠤࡵࡿࡴࡦࡵࡷ࠱ࡧࡪࡤࠡࡵࡨࡷࡸ࡯࡯࡯࠼ࠣࡿࢂ࠭೜").format(str(e)))
  except Exception as e:
    logger.debug(bstack11ll1_opy_ (u"ࠪࡉࡷࡸ࡯ࡳࠢ࡬ࡲࠥ࡭ࡥࡵࡶ࡬ࡲ࡬ࠦࡳࡵࡣࡷࡩࠥ࡯࡮ࠡࡲࡼࡸࡪࡹࡴ࠮ࡤࡧࡨࠥࡺࡥࡴࡶࠣࡷࡹࡧࡴࡶࡵ࠽ࠤࢀࢃࠧೝ").format(str(e)))
  bstack1l11l11ll1_opy_(item, call, rep)
def bstack1l1lllll_opy_(driver, bstack1llll11ll1_opy_, test=None):
  global bstack111l11l1l_opy_
  if test != None:
    bstack1llll1l1ll_opy_ = getattr(test, bstack11ll1_opy_ (u"ࠫࡳࡧ࡭ࡦࠩೞ"), None)
    bstack11lll1l11l_opy_ = getattr(test, bstack11ll1_opy_ (u"ࠬࡻࡵࡪࡦࠪ೟"), None)
    PercySDK.screenshot(driver, bstack1llll11ll1_opy_, bstack1llll1l1ll_opy_=bstack1llll1l1ll_opy_, bstack11lll1l11l_opy_=bstack11lll1l11l_opy_, bstack1l1lll111_opy_=bstack111l11l1l_opy_)
  else:
    PercySDK.screenshot(driver, bstack1llll11ll1_opy_)
@measure(event_name=EVENTS.bstack1l1ll1llll_opy_, stage=STAGE.bstack11l1llll1_opy_, bstack1lll1l1l1_opy_=bstack1ll1l11111_opy_)
def bstack1l1ll1ll11_opy_(driver):
  if bstack11111lll_opy_.bstack111l11111_opy_() is True or bstack11111lll_opy_.capturing() is True:
    return
  bstack11111lll_opy_.bstack1ll1l11ll_opy_()
  while not bstack11111lll_opy_.bstack111l11111_opy_():
    bstack1l11l1l111_opy_ = bstack11111lll_opy_.bstack1ll11l1l11_opy_()
    bstack1l1lllll_opy_(driver, bstack1l11l1l111_opy_)
  bstack11111lll_opy_.bstack1ll1ll1111_opy_()
def bstack1ll11l1111_opy_(sequence, driver_command, response = None, bstack1ll1l1llll_opy_ = None, args = None):
    try:
      if sequence != bstack11ll1_opy_ (u"࠭ࡢࡦࡨࡲࡶࡪ࠭ೠ"):
        return
      if percy.bstack1lll1l11l1_opy_() == bstack11ll1_opy_ (u"ࠢࡧࡣ࡯ࡷࡪࠨೡ"):
        return
      bstack1l11l1l111_opy_ = bstack1lll11l1l_opy_(threading.current_thread(), bstack11ll1_opy_ (u"ࠨࡲࡨࡶࡨࡿࡓࡦࡵࡶ࡭ࡴࡴࡎࡢ࡯ࡨࠫೢ"), None)
      for command in bstack111l11ll_opy_:
        if command == driver_command:
          with bstack1l1lll11_opy_:
            bstack1111l11ll_opy_ = bstack1lll111ll_opy_.copy()
          for driver in bstack1111l11ll_opy_:
            bstack1l1ll1ll11_opy_(driver)
      bstack1l1lll1lll_opy_ = percy.bstack11l11lll1_opy_()
      if driver_command in bstack1ll111lll_opy_[bstack1l1lll1lll_opy_]:
        bstack11111lll_opy_.bstack1111l1ll1_opy_(bstack1l11l1l111_opy_, driver_command)
    except Exception as e:
      pass
def bstack1111l1111_opy_(framework_name):
  if bstack1l1l1ll1l_opy_.get_property(bstack11ll1_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬ࡡࡰࡳࡩࡥࡣࡢ࡮࡯ࡩࡩ࠭ೣ")):
      return
  bstack1l1l1ll1l_opy_.bstack11l1l11l_opy_(bstack11ll1_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭ࡢࡱࡴࡪ࡟ࡤࡣ࡯ࡰࡪࡪࠧ೤"), True)
  global bstack11l1l11ll_opy_
  global bstack1lll1ll1_opy_
  global bstack1111l1l1l_opy_
  bstack11l1l11ll_opy_ = framework_name
  logger.info(bstack1ll1111l11_opy_.format(bstack11l1l11ll_opy_.split(bstack11ll1_opy_ (u"ࠫ࠲࠭೥"))[0]))
  bstack1l1l1l111l_opy_()
  try:
    from selenium import webdriver
    from selenium.webdriver.common.service import Service
    from selenium.webdriver.remote.webdriver import WebDriver
    if bstack1llll1l1_opy_:
      Service.start = bstack1l1l1ll111_opy_
      Service.stop = bstack1l1lllll1_opy_
      webdriver.Remote.get = bstack11lll1111_opy_
      WebDriver.quit = bstack1l1l111l1_opy_
      webdriver.Remote.__init__ = bstack1l111111l1_opy_
    if not bstack1llll1l1_opy_:
        webdriver.Remote.__init__ = bstack111111ll1_opy_
    WebDriver.getAccessibilityResults = getAccessibilityResults
    WebDriver.get_accessibility_results = getAccessibilityResults
    WebDriver.getAccessibilityResultsSummary = getAccessibilityResultsSummary
    WebDriver.get_accessibility_results_summary = getAccessibilityResultsSummary
    WebDriver.performScan = perform_scan
    WebDriver.perform_scan = perform_scan
    WebDriver.execute = bstack11ll111111_opy_
    bstack1lll1ll1_opy_ = True
  except Exception as e:
    pass
  try:
    if bstack1llll1l1_opy_:
      from QWeb.keywords import browser
      browser.close_browser = bstack1ll1l111l1_opy_
  except Exception as e:
    pass
  bstack1l11lllll1_opy_()
  if not bstack1lll1ll1_opy_:
    bstack1ll1l1l111_opy_(bstack11ll1_opy_ (u"ࠧࡖࡡࡤ࡭ࡤ࡫ࡪࡹࠠ࡯ࡱࡷࠤ࡮ࡴࡳࡵࡣ࡯ࡰࡪࡪࠢ೦"), bstack1llll11l_opy_)
  if bstack1111l111_opy_():
    try:
      from selenium.webdriver.remote.remote_connection import RemoteConnection
      if hasattr(RemoteConnection, bstack11ll1_opy_ (u"࠭࡟ࡨࡧࡷࡣࡵࡸ࡯ࡹࡻࡢࡹࡷࡲࠧ೧")) and callable(getattr(RemoteConnection, bstack11ll1_opy_ (u"ࠧࡠࡩࡨࡸࡤࡶࡲࡰࡺࡼࡣࡺࡸ࡬ࠨ೨"))):
        RemoteConnection._get_proxy_url = bstack11l1ll1ll_opy_
      else:
        from selenium.webdriver.remote.client_config import ClientConfig
        ClientConfig.get_proxy_url = bstack11l1ll1ll_opy_
    except Exception as e:
      logger.error(bstack1l1llllll1_opy_.format(str(e)))
  if bstack1ll111ll1l_opy_():
    bstack1l11ll11l1_opy_(CONFIG, logger)
  if (bstack11ll1_opy_ (u"ࠨࡴࡲࡦࡴࡺࠧ೩") in str(framework_name).lower()):
    try:
      from robot import run_cli
      from robot.output import Output
      from robot.running.status import TestStatus
      from pabot.pabot import QueueItem
      from pabot import pabot
      try:
        if percy.bstack1lll1l11l1_opy_() == bstack11ll1_opy_ (u"ࠤࡷࡶࡺ࡫ࠢ೪"):
          bstack11ll1111ll_opy_(bstack1ll11l1111_opy_)
        from SeleniumLibrary.keywords.webdrivertools.webdrivertools import WebDriverCreator
        WebDriverCreator._get_ff_profile = bstack1l1lll1l1_opy_
        from SeleniumLibrary.keywords.webdrivertools.webdrivertools import WebDriverCache
        WebDriverCache.close = bstack11llll11l_opy_
      except Exception as e:
        logger.warning(bstack1ll1lll1l_opy_ + str(e))
      try:
        from AppiumLibrary.utils.applicationcache import ApplicationCache
        ApplicationCache.close = bstack1l11l11lll_opy_
      except Exception as e:
        logger.debug(bstack1lllll1lll_opy_ + str(e))
    except Exception as e:
      bstack1ll1l1l111_opy_(e, bstack1ll1lll1l_opy_)
    Output.start_test = bstack111ll1l1l_opy_
    Output.end_test = bstack1l1lll111l_opy_
    TestStatus.__init__ = bstack1lll1ll111_opy_
    QueueItem.__init__ = bstack1l1llll1_opy_
    pabot._create_items = bstack1ll1l1l11_opy_
    try:
      from pabot import __version__ as bstack11lllll1ll_opy_
      if version.parse(bstack11lllll1ll_opy_) >= version.parse(bstack11ll1_opy_ (u"ࠪ࠹࠳࠶࠮࠱ࠩ೫")):
        pabot._run = bstack11l11l1ll1_opy_
      elif version.parse(bstack11lllll1ll_opy_) >= version.parse(bstack11ll1_opy_ (u"ࠫ࠹࠴࠲࠯࠲ࠪ೬")):
        pabot._run = bstack1l1llll1l1_opy_
      elif version.parse(bstack11lllll1ll_opy_) >= version.parse(bstack11ll1_opy_ (u"ࠬ࠸࠮࠲࠷࠱࠴ࠬ೭")):
        pabot._run = bstack11lllll11_opy_
      elif version.parse(bstack11lllll1ll_opy_) >= version.parse(bstack11ll1_opy_ (u"࠭࠲࠯࠳࠶࠲࠵࠭೮")):
        pabot._run = bstack111l111l1_opy_
      else:
        pabot._run = bstack1l1111l1l1_opy_
    except Exception as e:
      pabot._run = bstack1l1111l1l1_opy_
    pabot._create_command_for_execution = bstack111lll1l1l_opy_
    pabot._report_results = bstack1lll1ll11_opy_
  if bstack11ll1_opy_ (u"ࠧࡣࡧ࡫ࡥࡻ࡫ࠧ೯") in str(framework_name).lower():
    try:
      from behave.runner import Runner
      from behave.model import Step
    except Exception as e:
      bstack1ll1l1l111_opy_(e, bstack1ll1llllll_opy_)
    Runner.run_hook = bstack1ll1l11l_opy_
    Step.run = bstack11ll11ll_opy_
  if bstack11ll1_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࠨ೰") in str(framework_name).lower():
    if not bstack1llll1l1_opy_:
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
def bstack1l1lll11ll_opy_():
  global CONFIG
  if bstack11ll1_opy_ (u"ࠩࡳࡥࡷࡧ࡬࡭ࡧ࡯ࡷࡕ࡫ࡲࡑ࡮ࡤࡸ࡫ࡵࡲ࡮ࠩೱ") in CONFIG and int(CONFIG[bstack11ll1_opy_ (u"ࠪࡴࡦࡸࡡ࡭࡮ࡨࡰࡸࡖࡥࡳࡒ࡯ࡥࡹ࡬࡯ࡳ࡯ࠪೲ")]) > 1:
    logger.warning(bstack1l11111l1l_opy_)
def bstack11l11l1l1l_opy_(arg, bstack1l11l1l1l_opy_, bstack1ll1lll11l_opy_=None):
  global CONFIG
  global bstack1l1ll11ll1_opy_
  global bstack1l11l1l1ll_opy_
  global bstack1llll1l1_opy_
  global bstack1l1l1ll1l_opy_
  bstack1ll11l1ll_opy_ = bstack11ll1_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࠫೳ")
  if bstack1l11l1l1l_opy_ and isinstance(bstack1l11l1l1l_opy_, str):
    bstack1l11l1l1l_opy_ = eval(bstack1l11l1l1l_opy_)
  CONFIG = bstack1l11l1l1l_opy_[bstack11ll1_opy_ (u"ࠬࡉࡏࡏࡈࡌࡋࠬ೴")]
  bstack1l1ll11ll1_opy_ = bstack1l11l1l1l_opy_[bstack11ll1_opy_ (u"࠭ࡈࡖࡄࡢ࡙ࡗࡒࠧ೵")]
  bstack1l11l1l1ll_opy_ = bstack1l11l1l1l_opy_[bstack11ll1_opy_ (u"ࠧࡊࡕࡢࡅࡕࡖ࡟ࡂࡗࡗࡓࡒࡇࡔࡆࠩ೶")]
  bstack1llll1l1_opy_ = bstack1l11l1l1l_opy_[bstack11ll1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡂࡗࡗࡓࡒࡇࡔࡊࡑࡑࠫ೷")]
  bstack1l1l1ll1l_opy_.bstack11l1l11l_opy_(bstack11ll1_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬ࡡࡶࡩࡸࡹࡩࡰࡰࠪ೸"), bstack1llll1l1_opy_)
  os.environ[bstack11ll1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡉࡖࡆࡓࡅࡘࡑࡕࡏࠬ೹")] = bstack1ll11l1ll_opy_
  os.environ[bstack11ll1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡇࡔࡔࡆࡊࡉࠪ೺")] = json.dumps(CONFIG)
  os.environ[bstack11ll1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡍ࡛ࡂࡠࡗࡕࡐࠬ೻")] = bstack1l1ll11ll1_opy_
  os.environ[bstack11ll1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡏࡓࡠࡃࡓࡔࡤࡇࡕࡕࡑࡐࡅ࡙ࡋࠧ೼")] = str(bstack1l11l1l1ll_opy_)
  os.environ[bstack11ll1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡐ࡚ࡖࡈࡗ࡙ࡥࡐࡍࡗࡊࡍࡓ࠭೽")] = str(True)
  if bstack1l1llll11l_opy_(arg, [bstack11ll1_opy_ (u"ࠨ࠯ࡱࠫ೾"), bstack11ll1_opy_ (u"ࠩ࠰࠱ࡳࡻ࡭ࡱࡴࡲࡧࡪࡹࡳࡦࡵࠪ೿")]) != -1:
    os.environ[bstack11ll1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡓ࡝࡙ࡋࡓࡕࡡࡓࡅࡗࡇࡌࡍࡇࡏࠫഀ")] = str(True)
  if len(sys.argv) <= 1:
    logger.critical(bstack1llll11l11_opy_)
    return
  bstack1ll1ll1ll_opy_()
  global bstack11l1l1l11_opy_
  global bstack111l11l1l_opy_
  global bstack11ll1l11l1_opy_
  global bstack111llll1ll_opy_
  global bstack1l111lll_opy_
  global bstack1111l1l1l_opy_
  global bstack1ll1lll1l1_opy_
  arg.append(bstack11ll1_opy_ (u"ࠦ࠲࡝ࠢഁ"))
  arg.append(bstack11ll1_opy_ (u"ࠧ࡯ࡧ࡯ࡱࡵࡩ࠿ࡓ࡯ࡥࡷ࡯ࡩࠥࡧ࡬ࡳࡧࡤࡨࡾࠦࡩ࡮ࡲࡲࡶࡹ࡫ࡤ࠻ࡲࡼࡸࡪࡹࡴ࠯ࡒࡼࡸࡪࡹࡴࡘࡣࡵࡲ࡮ࡴࡧࠣം"))
  arg.append(bstack11ll1_opy_ (u"ࠨ࠭ࡘࠤഃ"))
  arg.append(bstack11ll1_opy_ (u"ࠢࡪࡩࡱࡳࡷ࡫࠺ࡕࡪࡨࠤ࡭ࡵ࡯࡬࡫ࡰࡴࡱࠨഄ"))
  global bstack1lll1l1l_opy_
  global bstack1llll1lll1_opy_
  global bstack11ll11l1ll_opy_
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
    bstack11ll11l1ll_opy_ = WebDriver.execute
  except Exception as e:
    pass
  if bstack1l1ll11lll_opy_(CONFIG) and bstack1l11lll111_opy_():
    if bstack1ll1ll1l11_opy_() < version.parse(bstack1llll1ll11_opy_):
      logger.error(bstack1lll1ll11l_opy_.format(bstack1ll1ll1l11_opy_()))
    else:
      try:
        from selenium.webdriver.remote.remote_connection import RemoteConnection
        if hasattr(RemoteConnection, bstack11ll1_opy_ (u"ࠨࡡࡪࡩࡹࡥࡰࡳࡱࡻࡽࡤࡻࡲ࡭ࠩഅ")) and callable(getattr(RemoteConnection, bstack11ll1_opy_ (u"ࠩࡢ࡫ࡪࡺ࡟ࡱࡴࡲࡼࡾࡥࡵࡳ࡮ࠪആ"))):
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
    logger.warning(bstack11ll1_opy_ (u"ࠥࠩࡸࡀࠠࠦࡵࠥഇ"), bstack11lll1l1l1_opy_, str(e))
  try:
    from pytest_bdd import reporting
    bstack1l11l11ll1_opy_ = reporting.runtest_makereport
  except Exception as e:
    logger.debug(bstack11ll1_opy_ (u"ࠫࡕࡲࡥࡢࡵࡨࠤ࡮ࡴࡳࡵࡣ࡯ࡰࠥࡶࡹࡵࡧࡶࡸ࠲ࡨࡤࡥࠢࡷࡳࠥࡸࡵ࡯ࠢࡳࡽࡹ࡫ࡳࡵ࠯ࡥࡨࡩࠦࡴࡦࡵࡷࡷࠬഈ"))
  bstack11ll1l11l1_opy_ = CONFIG.get(bstack11ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࡑࡳࡸ࡮ࡵ࡮ࡴࠩഉ"), {}).get(bstack11ll1_opy_ (u"࠭࡬ࡰࡥࡤࡰࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨഊ"))
  bstack1ll1lll1l1_opy_ = True
  if cli.is_enabled(CONFIG):
    if cli.bstack111l1l1l1_opy_():
      bstack1111l11l_opy_.invoke(bstack1l11111l1_opy_.CONNECT, bstack11llllll1l_opy_())
    platform_index = int(os.environ.get(bstack11ll1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡐࡍࡃࡗࡊࡔࡘࡍࡠࡋࡑࡈࡊ࡞ࠧഋ"), bstack11ll1_opy_ (u"ࠨ࠲ࠪഌ")))
  else:
    bstack1111l1111_opy_(bstack1l11l1lll1_opy_)
  os.environ[bstack11ll1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡗࡖࡉࡗࡔࡁࡎࡇࠪ഍")] = CONFIG[bstack11ll1_opy_ (u"ࠪࡹࡸ࡫ࡲࡏࡣࡰࡩࠬഎ")]
  os.environ[bstack11ll1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡅࡈࡉࡅࡔࡕࡢࡏࡊ࡟ࠧഏ")] = CONFIG[bstack11ll1_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷࡐ࡫ࡹࠨഐ")]
  os.environ[bstack11ll1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡇࡕࡕࡑࡐࡅ࡙ࡏࡏࡏࠩ഑")] = bstack1llll1l1_opy_.__str__()
  from _pytest.config import main as bstack11l11l1l_opy_
  bstack111l1ll1_opy_ = []
  try:
    exit_code = bstack11l11l1l_opy_(arg)
    if cli.is_enabled(CONFIG):
      cli.bstack11l1ll1lll_opy_()
    if bstack11ll1_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱ࡟ࡦࡴࡵࡳࡷࡥ࡬ࡪࡵࡷࠫഒ") in multiprocessing.current_process().__dict__.keys():
      for bstack11l1ll11ll_opy_ in multiprocessing.current_process().bstack_error_list:
        bstack111l1ll1_opy_.append(bstack11l1ll11ll_opy_)
    try:
      bstack11ll111l_opy_ = (bstack111l1ll1_opy_, int(exit_code))
      bstack1ll1lll11l_opy_.append(bstack11ll111l_opy_)
    except:
      bstack1ll1lll11l_opy_.append((bstack111l1ll1_opy_, exit_code))
  except Exception as e:
    logger.error(traceback.format_exc())
    bstack111l1ll1_opy_.append({bstack11ll1_opy_ (u"ࠨࡰࡤࡱࡪ࠭ഓ"): bstack11ll1_opy_ (u"ࠩࡓࡶࡴࡩࡥࡴࡵࠣࠫഔ") + os.environ.get(bstack11ll1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡓࡐࡆ࡚ࡆࡐࡔࡐࡣࡎࡔࡄࡆ࡚ࠪക")), bstack11ll1_opy_ (u"ࠫࡪࡸࡲࡰࡴࠪഖ"): traceback.format_exc(), bstack11ll1_opy_ (u"ࠬ࡯࡮ࡥࡧࡻࠫഗ"): int(os.environ.get(bstack11ll1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡖࡌࡂࡖࡉࡓࡗࡓ࡟ࡊࡐࡇࡉ࡝࠭ഘ")))})
    bstack1ll1lll11l_opy_.append((bstack111l1ll1_opy_, 1))
def mod_behave_main(args, retries):
  try:
    from behave.configuration import Configuration
    from behave.__main__ import run_behave
    from browserstack_sdk.bstack_behave_runner import BehaveRunner
    config = Configuration(args)
    config.update_userdata({bstack11ll1_opy_ (u"ࠢࡳࡧࡷࡶ࡮࡫ࡳࠣങ"): str(retries)})
    return run_behave(config, runner_class=BehaveRunner)
  except Exception as e:
    bstack11111ll1_opy_ = e.__class__.__name__
    print(bstack11ll1_opy_ (u"ࠣࠧࡶ࠾ࠥࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡ࡫ࡱࠤࡷࡻ࡮࡯࡫ࡱ࡫ࠥࡨࡥࡩࡣࡹࡩࠥࡺࡥࡴࡶࠣࠩࡸࠨച") % (bstack11111ll1_opy_, e))
    return 1
def bstack11ll1lll11_opy_(arg):
  global bstack1lll1l1l11_opy_
  bstack1111l1111_opy_(bstack1111lll11_opy_)
  os.environ[bstack11ll1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡋࡖࡣࡆࡖࡐࡠࡃࡘࡘࡔࡓࡁࡕࡇࠪഛ")] = str(bstack1l11l1l1ll_opy_)
  retries = bstack1lll1lll_opy_.bstack1lllllll1l_opy_(CONFIG)
  status_code = 0
  if bstack1lll1lll_opy_.bstack1ll11l11ll_opy_(CONFIG):
    status_code = mod_behave_main(arg, retries)
  else:
    from behave.__main__ import main as bstack1ll111lll1_opy_
    status_code = bstack1ll111lll1_opy_(arg)
  if status_code != 0:
    bstack1lll1l1l11_opy_ = status_code
def bstack1l1111l11_opy_():
  logger.info(bstack1l1ll1l1l1_opy_)
  import argparse
  parser = argparse.ArgumentParser()
  parser.add_argument(bstack11ll1_opy_ (u"ࠪࡷࡪࡺࡵࡱࠩജ"), help=bstack11ll1_opy_ (u"ࠫࡌ࡫࡮ࡦࡴࡤࡸࡪࠦࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࠥࡩ࡯࡯ࡨ࡬࡫ࠬഝ"))
  parser.add_argument(bstack11ll1_opy_ (u"ࠬ࠳ࡵࠨഞ"), bstack11ll1_opy_ (u"࠭࠭࠮ࡷࡶࡩࡷࡴࡡ࡮ࡧࠪട"), help=bstack11ll1_opy_ (u"࡚ࠧࡱࡸࡶࠥࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࠤࡺࡹࡥࡳࡰࡤࡱࡪ࠭ഠ"))
  parser.add_argument(bstack11ll1_opy_ (u"ࠨ࠯࡮ࠫഡ"), bstack11ll1_opy_ (u"ࠩ࠰࠱ࡰ࡫ࡹࠨഢ"), help=bstack11ll1_opy_ (u"ࠪ࡝ࡴࡻࡲࠡࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠠࡢࡥࡦࡩࡸࡹࠠ࡬ࡧࡼࠫണ"))
  parser.add_argument(bstack11ll1_opy_ (u"ࠫ࠲࡬ࠧത"), bstack11ll1_opy_ (u"ࠬ࠳࠭ࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࠪഥ"), help=bstack11ll1_opy_ (u"࡙࠭ࡰࡷࡵࠤࡹ࡫ࡳࡵࠢࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࠬദ"))
  bstack1l111ll111_opy_ = parser.parse_args()
  try:
    bstack11l11l1lll_opy_ = bstack11ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡧࡦࡰࡨࡶ࡮ࡩ࠮ࡺ࡯࡯࠲ࡸࡧ࡭ࡱ࡮ࡨࠫധ")
    if bstack1l111ll111_opy_.framework and bstack1l111ll111_opy_.framework not in (bstack11ll1_opy_ (u"ࠨࡲࡼࡸ࡭ࡵ࡮ࠨന"), bstack11ll1_opy_ (u"ࠩࡳࡽࡹ࡮࡯࡯࠵ࠪഩ")):
      bstack11l11l1lll_opy_ = bstack11ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡩࡶࡦࡳࡥࡸࡱࡵ࡯࠳ࡿ࡭࡭࠰ࡶࡥࡲࡶ࡬ࡦࠩപ")
    bstack11ll1l1lll_opy_ = os.path.join(os.path.dirname(os.path.realpath(__file__)), bstack11l11l1lll_opy_)
    bstack1lll1lllll_opy_ = open(bstack11ll1l1lll_opy_, bstack11ll1_opy_ (u"ࠫࡷ࠭ഫ"))
    bstack1l111llll_opy_ = bstack1lll1lllll_opy_.read()
    bstack1lll1lllll_opy_.close()
    if bstack1l111ll111_opy_.username:
      bstack1l111llll_opy_ = bstack1l111llll_opy_.replace(bstack11ll1_opy_ (u"ࠬ࡟ࡏࡖࡔࡢ࡙ࡘࡋࡒࡏࡃࡐࡉࠬബ"), bstack1l111ll111_opy_.username)
    if bstack1l111ll111_opy_.key:
      bstack1l111llll_opy_ = bstack1l111llll_opy_.replace(bstack11ll1_opy_ (u"࡙࠭ࡐࡗࡕࡣࡆࡉࡃࡆࡕࡖࡣࡐࡋ࡙ࠨഭ"), bstack1l111ll111_opy_.key)
    if bstack1l111ll111_opy_.framework:
      bstack1l111llll_opy_ = bstack1l111llll_opy_.replace(bstack11ll1_opy_ (u"࡚ࠧࡑࡘࡖࡤࡌࡒࡂࡏࡈ࡛ࡔࡘࡋࠨമ"), bstack1l111ll111_opy_.framework)
    file_name = bstack11ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡺ࡯࡯ࠫയ")
    file_path = os.path.abspath(file_name)
    bstack1111llll_opy_ = open(file_path, bstack11ll1_opy_ (u"ࠩࡺࠫര"))
    bstack1111llll_opy_.write(bstack1l111llll_opy_)
    bstack1111llll_opy_.close()
    logger.info(bstack1lll1llll1_opy_)
    try:
      os.environ[bstack11ll1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡉࡖࡆࡓࡅࡘࡑࡕࡏࠬറ")] = bstack1l111ll111_opy_.framework if bstack1l111ll111_opy_.framework != None else bstack11ll1_opy_ (u"ࠦࠧല")
      config = yaml.safe_load(bstack1l111llll_opy_)
      config[bstack11ll1_opy_ (u"ࠬࡹ࡯ࡶࡴࡦࡩࠬള")] = bstack11ll1_opy_ (u"࠭ࡰࡺࡶ࡫ࡳࡳ࠳ࡳࡦࡶࡸࡴࠬഴ")
      bstack11l11l111_opy_(bstack1lll1ll1l_opy_, config)
    except Exception as e:
      logger.debug(bstack1l1l1l1l11_opy_.format(str(e)))
  except Exception as e:
    logger.error(bstack111l1lll1_opy_.format(str(e)))
def bstack11l11l111_opy_(bstack1l1l11lll1_opy_, config, bstack11l11l1111_opy_={}):
  global bstack1llll1l1_opy_
  global bstack11l1l1ll1l_opy_
  global bstack1l1l1ll1l_opy_
  if not config:
    return
  bstack1l111lll1l_opy_ = bstack111111l11_opy_ if not bstack1llll1l1_opy_ else (
    bstack111lll1l11_opy_ if bstack11ll1_opy_ (u"ࠧࡢࡲࡳࠫവ") in config else (
        bstack11lllll1l1_opy_ if config.get(bstack11ll1_opy_ (u"ࠨࡶࡸࡶࡧࡵࡓࡤࡣ࡯ࡩࠬശ")) else bstack1ll11llll_opy_
    )
)
  bstack11lll11l1_opy_ = False
  bstack111lllll11_opy_ = False
  if bstack1llll1l1_opy_ is True:
      if bstack11ll1_opy_ (u"ࠩࡤࡴࡵ࠭ഷ") in config:
          bstack11lll11l1_opy_ = True
      else:
          bstack111lllll11_opy_ = True
  bstack11l1111l11_opy_ = bstack1l11111ll1_opy_.bstack111lll11l_opy_(config, bstack11l1l1ll1l_opy_)
  bstack111ll1lll_opy_ = bstack11l11111l1_opy_()
  data = {
    bstack11ll1_opy_ (u"ࠪࡹࡸ࡫ࡲࡏࡣࡰࡩࠬസ"): config[bstack11ll1_opy_ (u"ࠫࡺࡹࡥࡳࡐࡤࡱࡪ࠭ഹ")],
    bstack11ll1_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷࡐ࡫ࡹࠨഺ"): config[bstack11ll1_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸࡑࡥࡺ഻ࠩ")],
    bstack11ll1_opy_ (u"ࠧࡦࡸࡨࡲࡹࡥࡴࡺࡲࡨ഼ࠫ"): bstack1l1l11lll1_opy_,
    bstack11ll1_opy_ (u"ࠨࡦࡨࡸࡪࡩࡴࡦࡦࡉࡶࡦࡳࡥࡸࡱࡵ࡯ࠬഽ"): os.environ.get(bstack11ll1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡈࡕࡅࡒࡋࡗࡐࡔࡎࠫാ"), bstack11l1l1ll1l_opy_),
    bstack11ll1_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡡ࡫ࡥࡸ࡮ࡥࡥࡡ࡬ࡨࠬി"): bstack1ll11ll111_opy_,
    bstack11ll1_opy_ (u"ࠫࡴࡶࡴࡪ࡯ࡤࡰࡤ࡮ࡵࡣࡡࡸࡶࡱ࠭ീ"): bstack1l1ll11ll_opy_(),
    bstack11ll1_opy_ (u"ࠬ࡫ࡶࡦࡰࡷࡣࡵࡸ࡯ࡱࡧࡵࡸ࡮࡫ࡳࠨു"): {
      bstack11ll1_opy_ (u"࠭࡬ࡢࡰࡪࡹࡦ࡭ࡥࡠࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࠫൂ"): str(config[bstack11ll1_opy_ (u"ࠧࡴࡱࡸࡶࡨ࡫ࠧൃ")]) if bstack11ll1_opy_ (u"ࠨࡵࡲࡹࡷࡩࡥࠨൄ") in config else bstack11ll1_opy_ (u"ࠤࡸࡲࡰࡴ࡯ࡸࡰࠥ൅"),
      bstack11ll1_opy_ (u"ࠪࡰࡦࡴࡧࡶࡣࡪࡩ࡛࡫ࡲࡴ࡫ࡲࡲࠬെ"): sys.version,
      bstack11ll1_opy_ (u"ࠫࡷ࡫ࡦࡦࡴࡵࡩࡷ࠭േ"): bstack1llll111l1_opy_(os.environ.get(bstack11ll1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡋࡘࡁࡎࡇ࡚ࡓࡗࡑࠧൈ"), bstack11l1l1ll1l_opy_)),
      bstack11ll1_opy_ (u"࠭࡬ࡢࡰࡪࡹࡦ࡭ࡥࠨ൉"): bstack11ll1_opy_ (u"ࠧࡱࡻࡷ࡬ࡴࡴࠧൊ"),
      bstack11ll1_opy_ (u"ࠨࡲࡵࡳࡩࡻࡣࡵࠩോ"): bstack1l111lll1l_opy_,
      bstack11ll1_opy_ (u"ࠩࡳࡶࡴࡪࡵࡤࡶࡢࡱࡦࡶࠧൌ"): bstack11l1111l11_opy_,
      bstack11ll1_opy_ (u"ࠪࡸࡪࡹࡴࡩࡷࡥࡣࡺࡻࡩࡥ്ࠩ"): os.environ[bstack11ll1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡉࡗࡅࡣ࡚࡛ࡉࡅࠩൎ")],
      bstack11ll1_opy_ (u"ࠬ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࠨ൏"): os.environ.get(bstack11ll1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡌࡒࡂࡏࡈ࡛ࡔࡘࡋࠨ൐"), bstack11l1l1ll1l_opy_),
      bstack11ll1_opy_ (u"ࠧࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭࡙ࡩࡷࡹࡩࡰࡰࠪ൑"): bstack11ll11l11l_opy_(os.environ.get(bstack11ll1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡇࡔࡄࡑࡊ࡝ࡏࡓࡍࠪ൒"), bstack11l1l1ll1l_opy_)),
      bstack11ll1_opy_ (u"ࠩࡤࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳࡌࡲࡢ࡯ࡨࡻࡴࡸ࡫ࠨ൓"): bstack111ll1lll_opy_.get(bstack11ll1_opy_ (u"ࠪࡲࡦࡳࡥࠨൔ")),
      bstack11ll1_opy_ (u"ࠫࡦࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࡇࡴࡤࡱࡪࡽ࡯ࡳ࡭࡙ࡩࡷࡹࡩࡰࡰࠪൕ"): bstack111ll1lll_opy_.get(bstack11ll1_opy_ (u"ࠬࡼࡥࡳࡵ࡬ࡳࡳ࠭ൖ")),
      bstack11ll1_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡓࡧ࡭ࡦࠩൗ"): config[bstack11ll1_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡔࡡ࡮ࡧࠪ൘")] if config[bstack11ll1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠫ൙")] else bstack11ll1_opy_ (u"ࠤࡸࡲࡰࡴ࡯ࡸࡰࠥ൚"),
      bstack11ll1_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬ൛"): str(config[bstack11ll1_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭൜")]) if bstack11ll1_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧ൝") in config else bstack11ll1_opy_ (u"ࠨࡵ࡯࡭ࡱࡳࡼࡴࠢ൞"),
      bstack11ll1_opy_ (u"ࠧࡰࡵࠪൟ"): sys.platform,
      bstack11ll1_opy_ (u"ࠨࡪࡲࡷࡹࡴࡡ࡮ࡧࠪൠ"): socket.gethostname(),
      bstack11ll1_opy_ (u"ࠩࡶࡨࡰࡘࡵ࡯ࡋࡧࠫൡ"): bstack1l1l1ll1l_opy_.get_property(bstack11ll1_opy_ (u"ࠪࡷࡩࡱࡒࡶࡰࡌࡨࠬൢ"))
    }
  }
  if not bstack1l1l1ll1l_opy_.get_property(bstack11ll1_opy_ (u"ࠫࡸࡪ࡫ࡌ࡫࡯ࡰࡘ࡯ࡧ࡯ࡣ࡯ࠫൣ")) is None:
    data[bstack11ll1_opy_ (u"ࠬ࡫ࡶࡦࡰࡷࡣࡵࡸ࡯ࡱࡧࡵࡸ࡮࡫ࡳࠨ൤")][bstack11ll1_opy_ (u"࠭ࡦࡪࡰ࡬ࡷ࡭࡫ࡤࡎࡧࡷࡥࡩࡧࡴࡢࠩ൥")] = {
      bstack11ll1_opy_ (u"ࠧࡳࡧࡤࡷࡴࡴࠧ൦"): bstack11ll1_opy_ (u"ࠨࡷࡶࡩࡷࡥ࡫ࡪ࡮࡯ࡩࡩ࠭൧"),
      bstack11ll1_opy_ (u"ࠩࡶ࡭࡬ࡴࡡ࡭ࠩ൨"): bstack1l1l1ll1l_opy_.get_property(bstack11ll1_opy_ (u"ࠪࡷࡩࡱࡋࡪ࡮࡯ࡗ࡮࡭࡮ࡢ࡮ࠪ൩")),
      bstack11ll1_opy_ (u"ࠫࡸ࡯ࡧ࡯ࡣ࡯ࡒࡺࡳࡢࡦࡴࠪ൪"): bstack1l1l1ll1l_opy_.get_property(bstack11ll1_opy_ (u"ࠬࡹࡤ࡬ࡍ࡬ࡰࡱࡔ࡯ࠨ൫"))
    }
  if bstack1l1l11lll1_opy_ == bstack1l11ll1l_opy_:
    data[bstack11ll1_opy_ (u"࠭ࡥࡷࡧࡱࡸࡤࡶࡲࡰࡲࡨࡶࡹ࡯ࡥࡴࠩ൬")][bstack11ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡔࡶࡤࡧࡰࡉ࡯࡯ࡨ࡬࡫ࠬ൭")] = bstack11l111lll_opy_(config)
    data[bstack11ll1_opy_ (u"ࠨࡧࡹࡩࡳࡺ࡟ࡱࡴࡲࡴࡪࡸࡴࡪࡧࡶࠫ൮")][bstack11ll1_opy_ (u"ࠩ࡬ࡷࡕ࡫ࡲࡤࡻࡄࡹࡹࡵࡅ࡯ࡣࡥࡰࡪࡪࠧ൯")] = percy.bstack1l1l1lll1_opy_
    data[bstack11ll1_opy_ (u"ࠪࡩࡻ࡫࡮ࡵࡡࡳࡶࡴࡶࡥࡳࡶ࡬ࡩࡸ࠭൰")][bstack11ll1_opy_ (u"ࠫࡵ࡫ࡲࡤࡻࡅࡹ࡮ࡲࡤࡊࡦࠪ൱")] = percy.percy_build_id
  if not bstack1lll1lll_opy_.bstack1l1l1111l_opy_(CONFIG):
    data[bstack11ll1_opy_ (u"ࠬ࡫ࡶࡦࡰࡷࡣࡵࡸ࡯ࡱࡧࡵࡸ࡮࡫ࡳࠨ൲")][bstack11ll1_opy_ (u"࠭ࡴࡦࡵࡷࡓࡷࡩࡨࡦࡵࡷࡶࡦࡺࡩࡰࡰࠪ൳")] = bstack1lll1lll_opy_.bstack1l1l1111l_opy_(CONFIG)
  bstack11ll1ll1l1_opy_ = bstack1l1111111l_opy_.bstack1l1l1111_opy_(CONFIG, logger)
  bstack11l111l1_opy_ = bstack1lll1lll_opy_.bstack1l1l1111_opy_(config=CONFIG)
  if bstack11ll1ll1l1_opy_ is not None and bstack11l111l1_opy_ is not None and bstack11l111l1_opy_.bstack1l1l1ll11_opy_():
    data[bstack11ll1_opy_ (u"ࠧࡦࡸࡨࡲࡹࡥࡰࡳࡱࡳࡩࡷࡺࡩࡦࡵࠪ൴")][bstack11l111l1_opy_.bstack111llll11_opy_()] = bstack11ll1ll1l1_opy_.bstack1l1llll1l_opy_()
  update(data[bstack11ll1_opy_ (u"ࠨࡧࡹࡩࡳࡺ࡟ࡱࡴࡲࡴࡪࡸࡴࡪࡧࡶࠫ൵")], bstack11l11l1111_opy_)
  try:
    response = bstack11l1l1l11l_opy_(bstack11ll1_opy_ (u"ࠩࡓࡓࡘ࡚ࠧ൶"), bstack1111l1lll_opy_(bstack1lllllll1_opy_), data, {
      bstack11ll1_opy_ (u"ࠪࡥࡺࡺࡨࠨ൷"): (config[bstack11ll1_opy_ (u"ࠫࡺࡹࡥࡳࡐࡤࡱࡪ࠭൸")], config[bstack11ll1_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷࡐ࡫ࡹࠨ൹")])
    })
    if response:
      logger.debug(bstack11lll1llll_opy_.format(bstack1l1l11lll1_opy_, str(response.json())))
  except Exception as e:
    logger.debug(bstack1l1l11lll_opy_.format(str(e)))
def bstack1llll111l1_opy_(framework):
  return bstack11ll1_opy_ (u"ࠨࡻࡾ࠯ࡳࡽࡹ࡮࡯࡯ࡣࡪࡩࡳࡺ࠯ࡼࡿࠥൺ").format(str(framework), __version__) if framework else bstack11ll1_opy_ (u"ࠢࡱࡻࡷ࡬ࡴࡴࡡࡨࡧࡱࡸ࠴ࢁࡽࠣൻ").format(
    __version__)
def bstack1ll1ll1ll_opy_():
  global CONFIG
  global bstack1l1l1l11l_opy_
  if bool(CONFIG):
    return
  try:
    bstack1lll11l11_opy_()
    logger.debug(bstack1ll1llll_opy_.format(str(CONFIG)))
    bstack1l1l1l11l_opy_ = bstack111lll1l1_opy_.configure_logger(CONFIG, bstack1l1l1l11l_opy_)
    bstack1l1l1l111l_opy_()
  except Exception as e:
    logger.error(bstack11ll1_opy_ (u"ࠣࡈࡤ࡭ࡱ࡫ࡤࠡࡶࡲࠤࡸ࡫ࡴࡶࡲ࠯ࠤࡪࡸࡲࡰࡴ࠽ࠤࠧർ") + str(e))
    sys.exit(1)
  sys.excepthook = bstack1llll11ll_opy_
  atexit.register(bstack1l1l1ll1ll_opy_)
  signal.signal(signal.SIGINT, bstack1l1l1ll1l1_opy_)
  signal.signal(signal.SIGTERM, bstack1l1l1ll1l1_opy_)
def bstack1llll11ll_opy_(exctype, value, traceback):
  global bstack1lll111ll_opy_
  try:
    for driver in bstack1lll111ll_opy_:
      bstack1ll11ll1ll_opy_(driver, bstack11ll1_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࠩൽ"), bstack11ll1_opy_ (u"ࠥࡗࡪࡹࡳࡪࡱࡱࠤ࡫ࡧࡩ࡭ࡧࡧࠤࡼ࡯ࡴࡩ࠼ࠣࡠࡳࠨൾ") + str(value))
  except Exception:
    pass
  logger.info(bstack11ll1l11ll_opy_)
  bstack1l1ll1ll_opy_(value, True)
  sys.__excepthook__(exctype, value, traceback)
  sys.exit(1)
def bstack1l1ll1ll_opy_(message=bstack11ll1_opy_ (u"ࠫࠬൿ"), bstack111l11ll1_opy_ = False):
  global CONFIG
  bstack11l1111ll_opy_ = bstack11ll1_opy_ (u"ࠬ࡭࡬ࡰࡤࡤࡰࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠧ඀") if bstack111l11ll1_opy_ else bstack11ll1_opy_ (u"࠭ࡥࡳࡴࡲࡶࠬඁ")
  try:
    if message:
      bstack11l11l1111_opy_ = {
        bstack11l1111ll_opy_ : str(message)
      }
      bstack11l11l111_opy_(bstack1l11ll1l_opy_, CONFIG, bstack11l11l1111_opy_)
    else:
      bstack11l11l111_opy_(bstack1l11ll1l_opy_, CONFIG)
  except Exception as e:
    logger.debug(bstack1ll1111l1l_opy_.format(str(e)))
def bstack1l11ll1l1l_opy_(bstack1ll1lllll_opy_, size):
  bstack1l1111llll_opy_ = []
  while len(bstack1ll1lllll_opy_) > size:
    bstack11l1l1ll11_opy_ = bstack1ll1lllll_opy_[:size]
    bstack1l1111llll_opy_.append(bstack11l1l1ll11_opy_)
    bstack1ll1lllll_opy_ = bstack1ll1lllll_opy_[size:]
  bstack1l1111llll_opy_.append(bstack1ll1lllll_opy_)
  return bstack1l1111llll_opy_
def bstack1l1llll11_opy_(args):
  if bstack11ll1_opy_ (u"ࠧ࠮࡯ࠪං") in args and bstack11ll1_opy_ (u"ࠨࡲࡧࡦࠬඃ") in args:
    return True
  return False
@measure(event_name=EVENTS.bstack1ll111111l_opy_, stage=STAGE.bstack11l11ll11l_opy_)
def run_on_browserstack(bstack1l11ll1ll1_opy_=None, bstack1ll1lll11l_opy_=None, bstack1l1111ll1l_opy_=False):
  global CONFIG
  global bstack1l1ll11ll1_opy_
  global bstack1l11l1l1ll_opy_
  global bstack11l1l1ll1l_opy_
  global bstack1l1l1ll1l_opy_
  bstack1ll11l1ll_opy_ = bstack11ll1_opy_ (u"ࠩࠪ඄")
  bstack1lllll11l1_opy_(bstack1ll11l1l1_opy_, logger)
  if bstack1l11ll1ll1_opy_ and isinstance(bstack1l11ll1ll1_opy_, str):
    bstack1l11ll1ll1_opy_ = eval(bstack1l11ll1ll1_opy_)
  if bstack1l11ll1ll1_opy_:
    CONFIG = bstack1l11ll1ll1_opy_[bstack11ll1_opy_ (u"ࠪࡇࡔࡔࡆࡊࡉࠪඅ")]
    bstack1l1ll11ll1_opy_ = bstack1l11ll1ll1_opy_[bstack11ll1_opy_ (u"ࠫࡍ࡛ࡂࡠࡗࡕࡐࠬආ")]
    bstack1l11l1l1ll_opy_ = bstack1l11ll1ll1_opy_[bstack11ll1_opy_ (u"ࠬࡏࡓࡠࡃࡓࡔࡤࡇࡕࡕࡑࡐࡅ࡙ࡋࠧඇ")]
    bstack1l1l1ll1l_opy_.bstack11l1l11l_opy_(bstack11ll1_opy_ (u"࠭ࡉࡔࡡࡄࡔࡕࡥࡁࡖࡖࡒࡑࡆ࡚ࡅࠨඈ"), bstack1l11l1l1ll_opy_)
    bstack1ll11l1ll_opy_ = bstack11ll1_opy_ (u"ࠧࡱࡻࡷ࡬ࡴࡴࠧඉ")
  bstack1l1l1ll1l_opy_.bstack11l1l11l_opy_(bstack11ll1_opy_ (u"ࠨࡵࡧ࡯ࡗࡻ࡮ࡊࡦࠪඊ"), uuid4().__str__())
  logger.info(bstack11ll1_opy_ (u"ࠩࡖࡈࡐࠦࡲࡶࡰࠣࡷࡹࡧࡲࡵࡧࡧࠤࡼ࡯ࡴࡩࠢ࡬ࡨ࠿ࠦࠧඋ") + bstack1l1l1ll1l_opy_.get_property(bstack11ll1_opy_ (u"ࠪࡷࡩࡱࡒࡶࡰࡌࡨࠬඌ")));
  logger.debug(bstack11ll1_opy_ (u"ࠫࡸࡪ࡫ࡓࡷࡱࡍࡩࡃࠧඍ") + bstack1l1l1ll1l_opy_.get_property(bstack11ll1_opy_ (u"ࠬࡹࡤ࡬ࡔࡸࡲࡎࡪࠧඎ")))
  if not bstack1l1111ll1l_opy_:
    if len(sys.argv) <= 1:
      logger.critical(bstack1llll11l11_opy_)
      return
    if sys.argv[1] == bstack11ll1_opy_ (u"࠭࠭࠮ࡸࡨࡶࡸ࡯࡯࡯ࠩඏ") or sys.argv[1] == bstack11ll1_opy_ (u"ࠧ࠮ࡸࠪඐ"):
      logger.info(bstack11ll1_opy_ (u"ࠨࡄࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠠࡑࡻࡷ࡬ࡴࡴࠠࡔࡆࡎࠤࡻࢁࡽࠨඑ").format(__version__))
      return
    if sys.argv[1] == bstack11ll1_opy_ (u"ࠩࡶࡩࡹࡻࡰࠨඒ"):
      bstack1l1111l11_opy_()
      return
  args = sys.argv
  bstack1ll1ll1ll_opy_()
  global bstack11l1l1l11_opy_
  global bstack1llll11l1l_opy_
  global bstack1ll1lll1l1_opy_
  global bstack1ll111111_opy_
  global bstack111l11l1l_opy_
  global bstack11ll1l11l1_opy_
  global bstack111llll1ll_opy_
  global bstack111l1l111_opy_
  global bstack1l111lll_opy_
  global bstack1111l1l1l_opy_
  global bstack11ll1ll11l_opy_
  bstack1llll11l1l_opy_ = len(CONFIG.get(bstack11ll1_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ඓ"), []))
  if not bstack1ll11l1ll_opy_:
    if args[1] == bstack11ll1_opy_ (u"ࠫࡵࡿࡴࡩࡱࡱࠫඔ") or args[1] == bstack11ll1_opy_ (u"ࠬࡶࡹࡵࡪࡲࡲ࠸࠭ඕ"):
      bstack1ll11l1ll_opy_ = bstack11ll1_opy_ (u"࠭ࡰࡺࡶ࡫ࡳࡳ࠭ඖ")
      args = args[2:]
    elif args[1] == bstack11ll1_opy_ (u"ࠧࡳࡱࡥࡳࡹ࠭඗"):
      bstack1ll11l1ll_opy_ = bstack11ll1_opy_ (u"ࠨࡴࡲࡦࡴࡺࠧ඘")
      args = args[2:]
    elif args[1] == bstack11ll1_opy_ (u"ࠩࡳࡥࡧࡵࡴࠨ඙"):
      bstack1ll11l1ll_opy_ = bstack11ll1_opy_ (u"ࠪࡴࡦࡨ࡯ࡵࠩක")
      args = args[2:]
    elif args[1] == bstack11ll1_opy_ (u"ࠫࡷࡵࡢࡰࡶ࠰࡭ࡳࡺࡥࡳࡰࡤࡰࠬඛ"):
      bstack1ll11l1ll_opy_ = bstack11ll1_opy_ (u"ࠬࡸ࡯ࡣࡱࡷ࠱࡮ࡴࡴࡦࡴࡱࡥࡱ࠭ග")
      args = args[2:]
    elif args[1] == bstack11ll1_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹ࠭ඝ"):
      bstack1ll11l1ll_opy_ = bstack11ll1_opy_ (u"ࠧࡱࡻࡷࡩࡸࡺࠧඞ")
      args = args[2:]
    elif args[1] == bstack11ll1_opy_ (u"ࠨࡤࡨ࡬ࡦࡼࡥࠨඟ"):
      bstack1ll11l1ll_opy_ = bstack11ll1_opy_ (u"ࠩࡥࡩ࡭ࡧࡶࡦࠩච")
      args = args[2:]
    else:
      if not bstack11ll1_opy_ (u"ࠪࡪࡷࡧ࡭ࡦࡹࡲࡶࡰ࠭ඡ") in CONFIG or str(CONFIG[bstack11ll1_opy_ (u"ࠫ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱࠧජ")]).lower() in [bstack11ll1_opy_ (u"ࠬࡶࡹࡵࡪࡲࡲࠬඣ"), bstack11ll1_opy_ (u"࠭ࡰࡺࡶ࡫ࡳࡳ࠹ࠧඤ")]:
        bstack1ll11l1ll_opy_ = bstack11ll1_opy_ (u"ࠧࡱࡻࡷ࡬ࡴࡴࠧඥ")
        args = args[1:]
      elif str(CONFIG[bstack11ll1_opy_ (u"ࠨࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࠫඦ")]).lower() == bstack11ll1_opy_ (u"ࠩࡵࡳࡧࡵࡴࠨට"):
        bstack1ll11l1ll_opy_ = bstack11ll1_opy_ (u"ࠪࡶࡴࡨ࡯ࡵࠩඨ")
        args = args[1:]
      elif str(CONFIG[bstack11ll1_opy_ (u"ࠫ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱࠧඩ")]).lower() == bstack11ll1_opy_ (u"ࠬࡶࡡࡣࡱࡷࠫඪ"):
        bstack1ll11l1ll_opy_ = bstack11ll1_opy_ (u"࠭ࡰࡢࡤࡲࡸࠬණ")
        args = args[1:]
      elif str(CONFIG[bstack11ll1_opy_ (u"ࠧࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࠪඬ")]).lower() == bstack11ll1_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࠨත"):
        bstack1ll11l1ll_opy_ = bstack11ll1_opy_ (u"ࠩࡳࡽࡹ࡫ࡳࡵࠩථ")
        args = args[1:]
      elif str(CONFIG[bstack11ll1_opy_ (u"ࠪࡪࡷࡧ࡭ࡦࡹࡲࡶࡰ࠭ද")]).lower() == bstack11ll1_opy_ (u"ࠫࡧ࡫ࡨࡢࡸࡨࠫධ"):
        bstack1ll11l1ll_opy_ = bstack11ll1_opy_ (u"ࠬࡨࡥࡩࡣࡹࡩࠬන")
        args = args[1:]
      else:
        os.environ[bstack11ll1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡌࡒࡂࡏࡈ࡛ࡔࡘࡋࠨ඲")] = bstack1ll11l1ll_opy_
        bstack11ll11l11_opy_(bstack1l11ll11l_opy_)
  os.environ[bstack11ll1_opy_ (u"ࠧࡇࡔࡄࡑࡊ࡝ࡏࡓࡍࡢ࡙ࡘࡋࡄࠨඳ")] = bstack1ll11l1ll_opy_
  bstack11l1l1ll1l_opy_ = bstack1ll11l1ll_opy_
  if cli.is_enabled(CONFIG):
    try:
      bstack11l11111l_opy_ = bstack11l1ll111l_opy_[bstack11ll1_opy_ (u"ࠨࡒ࡜ࡘࡊ࡙ࡔ࠮ࡄࡇࡈࠬප")] if bstack1ll11l1ll_opy_ == bstack11ll1_opy_ (u"ࠩࡳࡽࡹ࡫ࡳࡵࠩඵ") and bstack1l1l1l1l_opy_() else bstack1ll11l1ll_opy_
      bstack1111l11l_opy_.invoke(bstack1l11111l1_opy_.bstack1l11ll1l11_opy_, bstack1ll1ll11_opy_(
        sdk_version=__version__,
        path_config=bstack1lll111ll1_opy_(),
        path_project=os.getcwd(),
        test_framework=bstack11l11111l_opy_,
        frameworks=[bstack11l11111l_opy_],
        framework_versions={
          bstack11l11111l_opy_: bstack11ll11l11l_opy_(bstack11ll1_opy_ (u"ࠪࡖࡴࡨ࡯ࡵࠩබ") if bstack1ll11l1ll_opy_ in [bstack11ll1_opy_ (u"ࠫࡵࡧࡢࡰࡶࠪභ"), bstack11ll1_opy_ (u"ࠬࡸ࡯ࡣࡱࡷࠫම"), bstack11ll1_opy_ (u"࠭ࡲࡰࡤࡲࡸ࠲࡯࡮ࡵࡧࡵࡲࡦࡲࠧඹ")] else bstack1ll11l1ll_opy_)
        },
        bs_config=CONFIG
      ))
      if cli.config.get(bstack11ll1_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠤය"), None):
        CONFIG[bstack11ll1_opy_ (u"ࠣࡤࡸ࡭ࡱࡪࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠥර")] = cli.config.get(bstack11ll1_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠦ඼"), None)
    except Exception as e:
      bstack1111l11l_opy_.invoke(bstack1l11111l1_opy_.bstack11ll111ll_opy_, e.__traceback__, 1)
    if bstack1l11l1l1ll_opy_:
      CONFIG[bstack11ll1_opy_ (u"ࠥࡥࡵࡶࠢල")] = cli.config[bstack11ll1_opy_ (u"ࠦࡦࡶࡰࠣ඾")]
      logger.info(bstack11ll111lll_opy_.format(CONFIG[bstack11ll1_opy_ (u"ࠬࡧࡰࡱࠩ඿")]))
  else:
    bstack1111l11l_opy_.clear()
  global bstack1l1ll11l_opy_
  global bstack11l1llll11_opy_
  if bstack1l11ll1ll1_opy_:
    try:
      bstack1ll11l1l1l_opy_ = datetime.datetime.now()
      os.environ[bstack11ll1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡌࡒࡂࡏࡈ࡛ࡔࡘࡋࠨව")] = bstack1ll11l1ll_opy_
      bstack11l11l111_opy_(bstack11l111ll1_opy_, CONFIG)
      cli.bstack1lll1lll1_opy_(bstack11ll1_opy_ (u"ࠢࡩࡶࡷࡴ࠿ࡹࡤ࡬ࡡࡷࡩࡸࡺ࡟ࡢࡶࡷࡩࡲࡶࡴࡦࡦࠥශ"), datetime.datetime.now() - bstack1ll11l1l1l_opy_)
    except Exception as e:
      logger.debug(bstack1lllll111l_opy_.format(str(e)))
  global bstack1lll1l1l_opy_
  global bstack1llll1lll1_opy_
  global bstack11ll1111_opy_
  global bstack1ll1ll111l_opy_
  global bstack1l11l1ll_opy_
  global bstack11l1111l_opy_
  global bstack1l111l1ll_opy_
  global bstack11l11lllll_opy_
  global bstack1ll1llll11_opy_
  global bstack11l1lllll_opy_
  global bstack1l1l1l1111_opy_
  global bstack1ll1l1111_opy_
  global bstack111lll1ll1_opy_
  global bstack1ll1l1lll1_opy_
  global bstack1llll1llll_opy_
  global bstack1ll1l11l1_opy_
  global bstack1ll111ll_opy_
  global bstack1l111l11l_opy_
  global bstack1lllll11ll_opy_
  global bstack1l11l11ll1_opy_
  global bstack11ll11l1ll_opy_
  try:
    from selenium import webdriver
    from selenium.webdriver.remote.webdriver import WebDriver
    bstack1lll1l1l_opy_ = webdriver.Remote.__init__
    bstack1llll1lll1_opy_ = WebDriver.quit
    bstack1ll1l1111_opy_ = WebDriver.close
    bstack1llll1llll_opy_ = WebDriver.get
    bstack11ll11l1ll_opy_ = WebDriver.execute
  except Exception as e:
    pass
  try:
    import Browser
    from subprocess import Popen
    bstack1l1ll11l_opy_ = Popen.__init__
  except Exception as e:
    pass
  try:
    from bstack_utils.helper import bstack1l11l1l1_opy_
    bstack11l1llll11_opy_ = bstack1l11l1l1_opy_()
  except Exception as e:
    pass
  try:
    global bstack1llllll1l_opy_
    from QWeb.keywords import browser
    bstack1llllll1l_opy_ = browser.close_browser
  except Exception as e:
    pass
  if bstack1l1ll11lll_opy_(CONFIG) and bstack1l11lll111_opy_():
    if bstack1ll1ll1l11_opy_() < version.parse(bstack1llll1ll11_opy_):
      logger.error(bstack1lll1ll11l_opy_.format(bstack1ll1ll1l11_opy_()))
    else:
      try:
        from selenium.webdriver.remote.remote_connection import RemoteConnection
        if hasattr(RemoteConnection, bstack11ll1_opy_ (u"ࠨࡡࡪࡩࡹࡥࡰࡳࡱࡻࡽࡤࡻࡲ࡭ࠩෂ")) and callable(getattr(RemoteConnection, bstack11ll1_opy_ (u"ࠩࡢ࡫ࡪࡺ࡟ࡱࡴࡲࡼࡾࡥࡵࡳ࡮ࠪස"))):
          RemoteConnection._get_proxy_url = bstack11l1ll1ll_opy_
        else:
          from selenium.webdriver.remote.client_config import ClientConfig
          ClientConfig.get_proxy_url = bstack11l1ll1ll_opy_
      except Exception as e:
        logger.error(bstack1l1llllll1_opy_.format(str(e)))
  if not CONFIG.get(bstack11ll1_opy_ (u"ࠪࡨ࡮ࡹࡡࡣ࡮ࡨࡅࡺࡺ࡯ࡄࡣࡳࡸࡺࡸࡥࡍࡱࡪࡷࠬහ"), False) and not bstack1l11ll1ll1_opy_:
    logger.info(bstack111ll111_opy_)
  if not cli.is_enabled(CONFIG):
    if bstack11ll1_opy_ (u"ࠫࡹࡻࡲࡣࡱࡖࡧࡦࡲࡥࠨළ") in CONFIG and str(CONFIG[bstack11ll1_opy_ (u"ࠬࡺࡵࡳࡤࡲࡗࡨࡧ࡬ࡦࠩෆ")]).lower() != bstack11ll1_opy_ (u"࠭ࡦࡢ࡮ࡶࡩࠬ෇"):
      bstack1111lll1l_opy_()
    elif bstack1ll11l1ll_opy_ != bstack11ll1_opy_ (u"ࠧࡱࡻࡷ࡬ࡴࡴࠧ෈") or (bstack1ll11l1ll_opy_ == bstack11ll1_opy_ (u"ࠨࡲࡼࡸ࡭ࡵ࡮ࠨ෉") and not bstack1l11ll1ll1_opy_):
      bstack11l111l111_opy_()
  if (bstack1ll11l1ll_opy_ in [bstack11ll1_opy_ (u"ࠩࡳࡥࡧࡵࡴࠨ්"), bstack11ll1_opy_ (u"ࠪࡶࡴࡨ࡯ࡵࠩ෋"), bstack11ll1_opy_ (u"ࠫࡷࡵࡢࡰࡶ࠰࡭ࡳࡺࡥࡳࡰࡤࡰࠬ෌")]):
    try:
      from robot import run_cli
      from robot.output import Output
      from robot.running.status import TestStatus
      from pabot.pabot import QueueItem
      from pabot import pabot
      try:
        from SeleniumLibrary.keywords.webdrivertools.webdrivertools import WebDriverCreator
        from SeleniumLibrary.keywords.webdrivertools.webdrivertools import WebDriverCache
        WebDriverCreator._get_ff_profile = bstack1l1lll1l1_opy_
        bstack11l1111l_opy_ = WebDriverCache.close
      except Exception as e:
        logger.warning(bstack1ll1lll1l_opy_ + str(e))
      try:
        from AppiumLibrary.utils.applicationcache import ApplicationCache
        bstack1l11l1ll_opy_ = ApplicationCache.close
      except Exception as e:
        logger.debug(bstack1lllll1lll_opy_ + str(e))
    except Exception as e:
      bstack1ll1l1l111_opy_(e, bstack1ll1lll1l_opy_)
    if bstack1ll11l1ll_opy_ != bstack11ll1_opy_ (u"ࠬࡸ࡯ࡣࡱࡷ࠱࡮ࡴࡴࡦࡴࡱࡥࡱ࠭෍"):
      bstack11111l11_opy_()
    bstack11ll1111_opy_ = Output.start_test
    bstack1ll1ll111l_opy_ = Output.end_test
    bstack1l111l1ll_opy_ = TestStatus.__init__
    bstack1ll1llll11_opy_ = pabot._run
    bstack11l1lllll_opy_ = QueueItem.__init__
    bstack1l1l1l1111_opy_ = pabot._create_command_for_execution
    bstack1lllll11ll_opy_ = pabot._report_results
  if bstack1ll11l1ll_opy_ == bstack11ll1_opy_ (u"࠭ࡢࡦࡪࡤࡺࡪ࠭෎"):
    try:
      from behave.runner import Runner
      from behave.model import Step
    except Exception as e:
      bstack1ll1l1l111_opy_(e, bstack1ll1llllll_opy_)
    bstack111lll1ll1_opy_ = Runner.run_hook
    bstack1ll1l1lll1_opy_ = Step.run
  if bstack1ll11l1ll_opy_ == bstack11ll1_opy_ (u"ࠧࡱࡻࡷࡩࡸࡺࠧා"):
    try:
      from _pytest.config import Config
      bstack1ll111ll_opy_ = Config.getoption
      from _pytest import runner
      bstack1l111l11l_opy_ = runner._update_current_test_var
    except Exception as e:
      logger.warning(bstack11ll1_opy_ (u"ࠣࠧࡶ࠾ࠥࠫࡳࠣැ"), bstack11lll1l1l1_opy_, str(e))
    try:
      from pytest_bdd import reporting
      bstack1l11l11ll1_opy_ = reporting.runtest_makereport
    except Exception as e:
      logger.debug(bstack11ll1_opy_ (u"ࠩࡓࡰࡪࡧࡳࡦࠢ࡬ࡲࡸࡺࡡ࡭࡮ࠣࡴࡾࡺࡥࡴࡶ࠰ࡦࡩࡪࠠࡵࡱࠣࡶࡺࡴࠠࡱࡻࡷࡩࡸࡺ࠭ࡣࡦࡧࠤࡹ࡫ࡳࡵࡵࠪෑ"))
    if bstack11l1l111l_opy_():
      logger.warning(bstack111111lll_opy_[bstack11ll1_opy_ (u"ࠪࡗࡉࡑ࠭ࡈࡇࡑ࠱࠵࠶࠵ࠨි")])
  try:
    framework_name = bstack11ll1_opy_ (u"ࠫࡷࡵࡢࡰࡶࠪී") if bstack1ll11l1ll_opy_ in [bstack11ll1_opy_ (u"ࠬࡶࡡࡣࡱࡷࠫු"), bstack11ll1_opy_ (u"࠭ࡲࡰࡤࡲࡸࠬ෕"), bstack11ll1_opy_ (u"ࠧࡳࡱࡥࡳࡹ࠳ࡩ࡯ࡶࡨࡶࡳࡧ࡬ࠨූ")] else bstack1ll1l11l11_opy_(bstack1ll11l1ll_opy_)
    bstack11l111111_opy_ = {
      bstack11ll1_opy_ (u"ࠨࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡳࡧ࡭ࡦࠩ෗"): bstack11ll1_opy_ (u"ࠩࡓࡽࡹ࡫ࡳࡵ࠯ࡦࡹࡨࡻ࡭ࡣࡧࡵࠫෘ") if bstack1ll11l1ll_opy_ == bstack11ll1_opy_ (u"ࠪࡴࡾࡺࡥࡴࡶࠪෙ") and bstack1l1l1l1l_opy_() else framework_name,
      bstack11ll1_opy_ (u"ࠫ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟ࡷࡧࡵࡷ࡮ࡵ࡮ࠨේ"): bstack11ll11l11l_opy_(framework_name),
      bstack11ll1_opy_ (u"ࠬࡹࡤ࡬ࡡࡹࡩࡷࡹࡩࡰࡰࠪෛ"): __version__,
      bstack11ll1_opy_ (u"࠭ࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡸࡷࡪࡪࠧො"): bstack1ll11l1ll_opy_
    }
    if bstack1ll11l1ll_opy_ in bstack11lllllll1_opy_ + bstack11ll1lll1_opy_:
      if bstack1l1ll11l1l_opy_.bstack11l1l1ll1_opy_(CONFIG):
        if bstack11ll1_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࡏࡱࡶ࡬ࡳࡳࡹࠧෝ") in CONFIG:
          os.environ[bstack11ll1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡤࡇࡃࡄࡇࡖࡗࡎࡈࡉࡍࡋࡗ࡝ࡤࡉࡏࡏࡈࡌࡋ࡚ࡘࡁࡕࡋࡒࡒࡤ࡟ࡍࡍࠩෞ")] = os.getenv(bstack11ll1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡥࡁࡄࡅࡈࡗࡘࡏࡂࡊࡎࡌࡘ࡞ࡥࡃࡐࡐࡉࡍࡌ࡛ࡒࡂࡖࡌࡓࡓࡥ࡙ࡎࡎࠪෟ"), json.dumps(CONFIG[bstack11ll1_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࡒࡴࡹ࡯࡯࡯ࡵࠪ෠")]))
          CONFIG[bstack11ll1_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࡓࡵࡺࡩࡰࡰࡶࠫ෡")].pop(bstack11ll1_opy_ (u"ࠬ࡯࡮ࡤ࡮ࡸࡨࡪ࡚ࡡࡨࡵࡌࡲ࡙࡫ࡳࡵ࡫ࡱ࡫ࡘࡩ࡯ࡱࡧࠪ෢"), None)
          CONFIG[bstack11ll1_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࡕࡰࡵ࡫ࡲࡲࡸ࠭෣")].pop(bstack11ll1_opy_ (u"ࠧࡦࡺࡦࡰࡺࡪࡥࡕࡣࡪࡷࡎࡴࡔࡦࡵࡷ࡭ࡳ࡭ࡓࡤࡱࡳࡩࠬ෤"), None)
        bstack11l111111_opy_[bstack11ll1_opy_ (u"ࠨࡶࡨࡷࡹࡌࡲࡢ࡯ࡨࡻࡴࡸ࡫ࠨ෥")] = {
          bstack11ll1_opy_ (u"ࠩࡱࡥࡲ࡫ࠧ෦"): bstack11ll1_opy_ (u"ࠪࡷࡪࡲࡥ࡯࡫ࡸࡱࠬ෧"),
          bstack11ll1_opy_ (u"ࠫࡻ࡫ࡲࡴ࡫ࡲࡲࠬ෨"): str(bstack1ll1ll1l11_opy_())
        }
    if bstack1ll11l1ll_opy_ not in [bstack11ll1_opy_ (u"ࠬࡸ࡯ࡣࡱࡷ࠱࡮ࡴࡴࡦࡴࡱࡥࡱ࠭෩")] and not cli.is_running():
      bstack1111ll11l_opy_, bstack1lllll1l1_opy_ = bstack11lll11l11_opy_.launch(CONFIG, bstack11l111111_opy_)
      if bstack1lllll1l1_opy_.get(bstack11ll1_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾ࠭෪")) is not None and bstack1l1ll11l1l_opy_.bstack1llll1l11l_opy_(CONFIG) is None:
        value = bstack1lllll1l1_opy_[bstack11ll1_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠧ෫")].get(bstack11ll1_opy_ (u"ࠨࡵࡸࡧࡨ࡫ࡳࡴࠩ෬"))
        if value is not None:
            CONFIG[bstack11ll1_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠩ෭")] = value
        else:
          logger.debug(bstack11ll1_opy_ (u"ࠥࡒࡴࠦࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࠦࡤࡢࡶࡤࠤ࡫ࡵࡵ࡯ࡦࠣ࡭ࡳࠦࡲࡦࡵࡳࡳࡳࡹࡥࠣ෮"))
  except Exception as e:
    logger.debug(bstack11l111l1l_opy_.format(bstack11ll1_opy_ (u"࡙ࠫ࡫ࡳࡵࡊࡸࡦࠬ෯"), str(e)))
  if bstack1ll11l1ll_opy_ == bstack11ll1_opy_ (u"ࠬࡶࡹࡵࡪࡲࡲࠬ෰"):
    bstack1ll1lll1l1_opy_ = True
    if bstack1l11ll1ll1_opy_ and bstack1l1111ll1l_opy_:
      bstack11ll1l11l1_opy_ = CONFIG.get(bstack11ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࡒࡴࡹ࡯࡯࡯ࡵࠪ෱"), {}).get(bstack11ll1_opy_ (u"ࠧ࡭ࡱࡦࡥࡱࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩෲ"))
      bstack1111l1111_opy_(bstack111111l1_opy_)
    elif bstack1l11ll1ll1_opy_:
      bstack11ll1l11l1_opy_ = CONFIG.get(bstack11ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡕࡷࡥࡨࡱࡌࡰࡥࡤࡰࡔࡶࡴࡪࡱࡱࡷࠬෳ"), {}).get(bstack11ll1_opy_ (u"ࠩ࡯ࡳࡨࡧ࡬ࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫ෴"))
      global bstack1lll111ll_opy_
      try:
        if bstack1l1llll11_opy_(bstack1l11ll1ll1_opy_[bstack11ll1_opy_ (u"ࠪࡪ࡮ࡲࡥࡠࡰࡤࡱࡪ࠭෵")]) and multiprocessing.current_process().name == bstack11ll1_opy_ (u"ࠫ࠵࠭෶"):
          bstack1l11ll1ll1_opy_[bstack11ll1_opy_ (u"ࠬ࡬ࡩ࡭ࡧࡢࡲࡦࡳࡥࠨ෷")].remove(bstack11ll1_opy_ (u"࠭࠭࡮ࠩ෸"))
          bstack1l11ll1ll1_opy_[bstack11ll1_opy_ (u"ࠧࡧ࡫࡯ࡩࡤࡴࡡ࡮ࡧࠪ෹")].remove(bstack11ll1_opy_ (u"ࠨࡲࡧࡦࠬ෺"))
          bstack1l11ll1ll1_opy_[bstack11ll1_opy_ (u"ࠩࡩ࡭ࡱ࡫࡟࡯ࡣࡰࡩࠬ෻")] = bstack1l11ll1ll1_opy_[bstack11ll1_opy_ (u"ࠪࡪ࡮ࡲࡥࡠࡰࡤࡱࡪ࠭෼")][0]
          with open(bstack1l11ll1ll1_opy_[bstack11ll1_opy_ (u"ࠫ࡫࡯࡬ࡦࡡࡱࡥࡲ࡫ࠧ෽")], bstack11ll1_opy_ (u"ࠬࡸࠧ෾")) as f:
            bstack111111111_opy_ = f.read()
          bstack1l1lllll11_opy_ = bstack11ll1_opy_ (u"ࠨࠢࠣࡨࡵࡳࡲࠦࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤࡹࡤ࡬ࠢ࡬ࡱࡵࡵࡲࡵࠢࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠ࡫ࡱ࡭ࡹ࡯ࡡ࡭࡫ࡽࡩࡀࠦࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤ࡯࡮ࡪࡶ࡬ࡥࡱ࡯ࡺࡦࠪࡾࢁ࠮ࡁࠠࡧࡴࡲࡱࠥࡶࡤࡣࠢ࡬ࡱࡵࡵࡲࡵࠢࡓࡨࡧࡁࠠࡰࡩࡢࡨࡧࠦ࠽ࠡࡒࡧࡦ࠳ࡪ࡯ࡠࡤࡵࡩࡦࡱ࠻ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࡩ࡫ࡦࠡ࡯ࡲࡨࡤࡨࡲࡦࡣ࡮ࠬࡸ࡫࡬ࡧ࠮ࠣࡥࡷ࡭ࠬࠡࡶࡨࡱࡵࡵࡲࡢࡴࡼࠤࡂࠦ࠰ࠪ࠼ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࡶࡵࡽ࠿ࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࡡࡳࡩࠣࡁࠥࡹࡴࡳࠪ࡬ࡲࡹ࠮ࡡࡳࡩࠬ࠯࠶࠶ࠩࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࡥࡹࡥࡨࡴࡹࠦࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢࡤࡷࠥ࡫࠺ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࡲࡤࡷࡸࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࡴ࡭࡟ࡥࡤࠫࡷࡪࡲࡦ࠭ࡣࡵ࡫࠱ࡺࡥ࡮ࡲࡲࡶࡦࡸࡹࠪࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࡖࡤࡣ࠰ࡧࡳࡤࡨࠠ࠾ࠢࡰࡳࡩࡥࡢࡳࡧࡤ࡯ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࡒࡧࡦ࠳ࡪ࡯ࡠࡤࡵࡩࡦࡱࠠ࠾ࠢࡰࡳࡩࡥࡢࡳࡧࡤ࡯ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࡒࡧࡦ࠭࠯࠮ࡴࡧࡷࡣࡹࡸࡡࡤࡧࠫ࠭ࡡࡴࠢࠣࠤ෿").format(str(bstack1l11ll1ll1_opy_))
          bstack1l11ll11_opy_ = bstack1l1lllll11_opy_ + bstack111111111_opy_
          bstack1ll1ll1l1_opy_ = bstack1l11ll1ll1_opy_[bstack11ll1_opy_ (u"ࠧࡧ࡫࡯ࡩࡤࡴࡡ࡮ࡧࠪ฀")] + bstack11ll1_opy_ (u"ࠨࡡࡥࡷࡹࡧࡣ࡬ࡡࡷࡩࡲࡶ࠮ࡱࡻࠪก")
          with open(bstack1ll1ll1l1_opy_, bstack11ll1_opy_ (u"ࠩࡺࠫข")):
            pass
          with open(bstack1ll1ll1l1_opy_, bstack11ll1_opy_ (u"ࠥࡻ࠰ࠨฃ")) as f:
            f.write(bstack1l11ll11_opy_)
          import subprocess
          bstack111ll11l1_opy_ = subprocess.run([bstack11ll1_opy_ (u"ࠦࡵࡿࡴࡩࡱࡱࠦค"), bstack1ll1ll1l1_opy_])
          if os.path.exists(bstack1ll1ll1l1_opy_):
            os.unlink(bstack1ll1ll1l1_opy_)
          os._exit(bstack111ll11l1_opy_.returncode)
        else:
          if bstack1l1llll11_opy_(bstack1l11ll1ll1_opy_[bstack11ll1_opy_ (u"ࠬ࡬ࡩ࡭ࡧࡢࡲࡦࡳࡥࠨฅ")]):
            bstack1l11ll1ll1_opy_[bstack11ll1_opy_ (u"࠭ࡦࡪ࡮ࡨࡣࡳࡧ࡭ࡦࠩฆ")].remove(bstack11ll1_opy_ (u"ࠧ࠮࡯ࠪง"))
            bstack1l11ll1ll1_opy_[bstack11ll1_opy_ (u"ࠨࡨ࡬ࡰࡪࡥ࡮ࡢ࡯ࡨࠫจ")].remove(bstack11ll1_opy_ (u"ࠩࡳࡨࡧ࠭ฉ"))
            bstack1l11ll1ll1_opy_[bstack11ll1_opy_ (u"ࠪࡪ࡮ࡲࡥࡠࡰࡤࡱࡪ࠭ช")] = bstack1l11ll1ll1_opy_[bstack11ll1_opy_ (u"ࠫ࡫࡯࡬ࡦࡡࡱࡥࡲ࡫ࠧซ")][0]
          bstack1111l1111_opy_(bstack111111l1_opy_)
          sys.path.append(os.path.dirname(os.path.abspath(bstack1l11ll1ll1_opy_[bstack11ll1_opy_ (u"ࠬ࡬ࡩ࡭ࡧࡢࡲࡦࡳࡥࠨฌ")])))
          sys.argv = sys.argv[2:]
          mod_globals = globals()
          mod_globals[bstack11ll1_opy_ (u"࠭࡟ࡠࡰࡤࡱࡪࡥ࡟ࠨญ")] = bstack11ll1_opy_ (u"ࠧࡠࡡࡰࡥ࡮ࡴ࡟ࡠࠩฎ")
          mod_globals[bstack11ll1_opy_ (u"ࠨࡡࡢࡪ࡮ࡲࡥࡠࡡࠪฏ")] = os.path.abspath(bstack1l11ll1ll1_opy_[bstack11ll1_opy_ (u"ࠩࡩ࡭ࡱ࡫࡟࡯ࡣࡰࡩࠬฐ")])
          exec(open(bstack1l11ll1ll1_opy_[bstack11ll1_opy_ (u"ࠪࡪ࡮ࡲࡥࡠࡰࡤࡱࡪ࠭ฑ")]).read(), mod_globals)
      except BaseException as e:
        try:
          traceback.print_exc()
          logger.error(bstack11ll1_opy_ (u"ࠫࡈࡧࡵࡨࡪࡷࠤࡊࡾࡣࡦࡲࡷ࡭ࡴࡴ࠺ࠡࡽࢀࠫฒ").format(str(e)))
          for driver in bstack1lll111ll_opy_:
            bstack1ll1lll11l_opy_.append({
              bstack11ll1_opy_ (u"ࠬࡴࡡ࡮ࡧࠪณ"): bstack1l11ll1ll1_opy_[bstack11ll1_opy_ (u"࠭ࡦࡪ࡮ࡨࡣࡳࡧ࡭ࡦࠩด")],
              bstack11ll1_opy_ (u"ࠧࡦࡴࡵࡳࡷ࠭ต"): str(e),
              bstack11ll1_opy_ (u"ࠨ࡫ࡱࡨࡪࡾࠧถ"): multiprocessing.current_process().name
            })
            bstack1ll11ll1ll_opy_(driver, bstack11ll1_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࠩท"), bstack11ll1_opy_ (u"ࠥࡗࡪࡹࡳࡪࡱࡱࠤ࡫ࡧࡩ࡭ࡧࡧࠤࡼ࡯ࡴࡩ࠼ࠣࡠࡳࠨธ") + str(e))
        except Exception:
          pass
      finally:
        try:
          for driver in bstack1lll111ll_opy_:
            driver.quit()
        except Exception as e:
          pass
    else:
      percy.init(bstack1l11l1l1ll_opy_, CONFIG, logger)
      bstack1llllllll1_opy_()
      bstack1l1lll11ll_opy_()
      percy.bstack11111l1l_opy_()
      bstack1l11l1l1l_opy_ = {
        bstack11ll1_opy_ (u"ࠫ࡫࡯࡬ࡦࡡࡱࡥࡲ࡫ࠧน"): args[0],
        bstack11ll1_opy_ (u"ࠬࡉࡏࡏࡈࡌࡋࠬบ"): CONFIG,
        bstack11ll1_opy_ (u"࠭ࡈࡖࡄࡢ࡙ࡗࡒࠧป"): bstack1l1ll11ll1_opy_,
        bstack11ll1_opy_ (u"ࠧࡊࡕࡢࡅࡕࡖ࡟ࡂࡗࡗࡓࡒࡇࡔࡆࠩผ"): bstack1l11l1l1ll_opy_
      }
      if bstack11ll1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫฝ") in CONFIG:
        bstack1l1l1l1ll_opy_ = bstack1lll11ll1_opy_(args, logger, CONFIG, bstack1llll1l1_opy_, bstack1llll11l1l_opy_)
        bstack111l1l111_opy_ = bstack1l1l1l1ll_opy_.bstack1ll1l1l1ll_opy_(run_on_browserstack, bstack1l11l1l1l_opy_, bstack1l1llll11_opy_(args))
      else:
        if bstack1l1llll11_opy_(args):
          bstack1l11l1l1l_opy_[bstack11ll1_opy_ (u"ࠩࡩ࡭ࡱ࡫࡟࡯ࡣࡰࡩࠬพ")] = args
          test = multiprocessing.Process(name=str(0),
                                         target=run_on_browserstack, args=(bstack1l11l1l1l_opy_,))
          test.start()
          test.join()
        else:
          bstack1111l1111_opy_(bstack111111l1_opy_)
          sys.path.append(os.path.dirname(os.path.abspath(args[0])))
          mod_globals = globals()
          mod_globals[bstack11ll1_opy_ (u"ࠪࡣࡤࡴࡡ࡮ࡧࡢࡣࠬฟ")] = bstack11ll1_opy_ (u"ࠫࡤࡥ࡭ࡢ࡫ࡱࡣࡤ࠭ภ")
          mod_globals[bstack11ll1_opy_ (u"ࠬࡥ࡟ࡧ࡫࡯ࡩࡤࡥࠧม")] = os.path.abspath(args[0])
          sys.argv = sys.argv[2:]
          exec(open(args[0]).read(), mod_globals)
  elif bstack1ll11l1ll_opy_ == bstack11ll1_opy_ (u"࠭ࡰࡢࡤࡲࡸࠬย") or bstack1ll11l1ll_opy_ == bstack11ll1_opy_ (u"ࠧࡳࡱࡥࡳࡹ࠭ร"):
    percy.init(bstack1l11l1l1ll_opy_, CONFIG, logger)
    percy.bstack11111l1l_opy_()
    try:
      from pabot import pabot
    except Exception as e:
      bstack1ll1l1l111_opy_(e, bstack1ll1lll1l_opy_)
    bstack1llllllll1_opy_()
    bstack1111l1111_opy_(bstack11l1111lll_opy_)
    if bstack1llll1l1_opy_:
      bstack11lll1l11_opy_(bstack11l1111lll_opy_, args)
      if bstack11ll1_opy_ (u"ࠨ࠯࠰ࡴࡷࡵࡣࡦࡵࡶࡩࡸ࠭ฤ") in args:
        i = args.index(bstack11ll1_opy_ (u"ࠩ࠰࠱ࡵࡸ࡯ࡤࡧࡶࡷࡪࡹࠧล"))
        args.pop(i)
        args.pop(i)
      if bstack11ll1_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ฦ") not in CONFIG:
        CONFIG[bstack11ll1_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧว")] = [{}]
        bstack1llll11l1l_opy_ = 1
      if bstack11l1l1l11_opy_ == 0:
        bstack11l1l1l11_opy_ = 1
      args.insert(0, str(bstack11l1l1l11_opy_))
      args.insert(0, str(bstack11ll1_opy_ (u"ࠬ࠳࠭ࡱࡴࡲࡧࡪࡹࡳࡦࡵࠪศ")))
    if bstack11lll11l11_opy_.on():
      try:
        from robot.run import USAGE
        from robot.utils import ArgumentParser
        from pabot.arguments import _parse_pabot_args
        bstack111lllllll_opy_, pabot_args = _parse_pabot_args(args)
        opts, bstack111l11lll_opy_ = ArgumentParser(
            USAGE,
            auto_pythonpath=False,
            auto_argumentfile=True,
            env_options=bstack11ll1_opy_ (u"ࠨࡒࡐࡄࡒࡘࡤࡕࡐࡕࡋࡒࡒࡘࠨษ"),
        ).parse_args(bstack111lllllll_opy_)
        bstack1lll11l11l_opy_ = args.index(bstack111lllllll_opy_[0]) if len(bstack111lllllll_opy_) > 0 else len(args)
        args.insert(bstack1lll11l11l_opy_, str(bstack11ll1_opy_ (u"ࠧ࠮࠯࡯࡭ࡸࡺࡥ࡯ࡧࡵࠫส")))
        args.insert(bstack1lll11l11l_opy_ + 1, str(os.path.join(os.path.dirname(os.path.realpath(__file__)), bstack11ll1_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫ࡠࡴࡲࡦࡴࡺ࡟࡭࡫ࡶࡸࡪࡴࡥࡳ࠰ࡳࡽࠬห"))))
        if bstack1lll1lll_opy_.bstack1ll11l11ll_opy_(CONFIG):
          args.insert(bstack1lll11l11l_opy_, str(bstack11ll1_opy_ (u"ࠩ࠰࠱ࡱ࡯ࡳࡵࡧࡱࡩࡷ࠭ฬ")))
          args.insert(bstack1lll11l11l_opy_ + 1, str(bstack11ll1_opy_ (u"ࠪࡖࡪࡺࡲࡺࡈࡤ࡭ࡱ࡫ࡤ࠻ࡽࢀࠫอ").format(bstack1lll1lll_opy_.bstack1lllllll1l_opy_(CONFIG))))
        if bstack1111lll1_opy_(os.environ.get(bstack11ll1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡖࡊࡘࡕࡏࠩฮ"))) and str(os.environ.get(bstack11ll1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡗࡋࡒࡖࡐࡢࡘࡊ࡙ࡔࡔࠩฯ"), bstack11ll1_opy_ (u"࠭࡮ࡶ࡮࡯ࠫะ"))) != bstack11ll1_opy_ (u"ࠧ࡯ࡷ࡯ࡰࠬั"):
          for bstack1l111l1l1_opy_ in bstack111l11lll_opy_:
            args.remove(bstack1l111l1l1_opy_)
          test_files = os.environ.get(bstack11ll1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡓࡇࡕ࡙ࡓࡥࡔࡆࡕࡗࡗࠬา")).split(bstack11ll1_opy_ (u"ࠩ࠯ࠫำ"))
          for bstack1ll1l11ll1_opy_ in test_files:
            args.append(bstack1ll1l11ll1_opy_)
      except Exception as e:
        logger.error(bstack11ll1_opy_ (u"ࠥࡉࡷࡸ࡯ࡳࠢࡺ࡬࡮ࡲࡥࠡࡣࡷࡸࡦࡩࡨࡪࡰࡪࠤࡱ࡯ࡳࡵࡧࡱࡩࡷࠦࡦࡰࡴࠣࡿࢂ࠴ࠠࡆࡴࡵࡳࡷࠦ࠭ࠡࡽࢀࠦิ").format(bstack111ll1ll1_opy_, e))
    pabot.main(args)
  elif bstack1ll11l1ll_opy_ == bstack11ll1_opy_ (u"ࠫࡷࡵࡢࡰࡶ࠰࡭ࡳࡺࡥࡳࡰࡤࡰࠬี"):
    try:
      from robot import run_cli
    except Exception as e:
      bstack1ll1l1l111_opy_(e, bstack1ll1lll1l_opy_)
    for a in args:
      if bstack11ll1_opy_ (u"ࠬࡈࡓࡕࡃࡆࡏࡕࡒࡁࡕࡈࡒࡖࡒࡏࡎࡅࡇ࡛ࠫึ") in a:
        bstack111l11l1l_opy_ = int(a.split(bstack11ll1_opy_ (u"࠭࠺ࠨื"))[1])
      if bstack11ll1_opy_ (u"ࠧࡃࡕࡗࡅࡈࡑࡄࡆࡈࡏࡓࡈࡇࡌࡊࡆࡈࡒ࡙ࡏࡆࡊࡇࡕุࠫ") in a:
        bstack11ll1l11l1_opy_ = str(a.split(bstack11ll1_opy_ (u"ࠨ࠼ูࠪ"))[1])
      if bstack11ll1_opy_ (u"ࠩࡅࡗ࡙ࡇࡃࡌࡅࡏࡍࡆࡘࡇࡔฺࠩ") in a:
        bstack111llll1ll_opy_ = str(a.split(bstack11ll1_opy_ (u"ࠪ࠾ࠬ฻"))[1])
    bstack11ll1l111_opy_ = None
    bstack111lllll_opy_ = None
    if bstack11ll1_opy_ (u"ࠫ࠲࠳ࡢࡴࡶࡤࡧࡰࡥࡩࡵࡧࡰࡣ࡮ࡴࡤࡦࡺࠪ฼") in args:
      i = args.index(bstack11ll1_opy_ (u"ࠬ࠳࠭ࡣࡵࡷࡥࡨࡱ࡟ࡪࡶࡨࡱࡤ࡯࡮ࡥࡧࡻࠫ฽"))
      args.pop(i)
      bstack11ll1l111_opy_ = args.pop(i)
    if bstack11ll1_opy_ (u"࠭࠭࠮ࡤࡶࡸࡦࡩ࡫ࡠࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡢ࡭ࡳࡪࡥࡹࠩ฾") in args:
      i = args.index(bstack11ll1_opy_ (u"ࠧ࠮࠯ࡥࡷࡹࡧࡣ࡬ࡡࡳࡰࡦࡺࡦࡰࡴࡰࡣ࡮ࡴࡤࡦࡺࠪ฿"))
      args.pop(i)
      bstack111lllll_opy_ = args.pop(i)
    if bstack11ll1l111_opy_ is not None:
      global bstack11111ll1l_opy_
      bstack11111ll1l_opy_ = bstack11ll1l111_opy_
    if bstack111lllll_opy_ is not None and int(bstack111l11l1l_opy_) < 0:
      bstack111l11l1l_opy_ = int(bstack111lllll_opy_)
    bstack1111l1111_opy_(bstack11l1111lll_opy_)
    run_cli(args)
    if bstack11ll1_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫ࡠࡧࡵࡶࡴࡸ࡟࡭࡫ࡶࡸࠬเ") in multiprocessing.current_process().__dict__.keys():
      for bstack11l1ll11ll_opy_ in multiprocessing.current_process().bstack_error_list:
        bstack1ll1lll11l_opy_.append(bstack11l1ll11ll_opy_)
  elif bstack1ll11l1ll_opy_ == bstack11ll1_opy_ (u"ࠩࡳࡽࡹ࡫ࡳࡵࠩแ"):
    bstack1l1lll1l1l_opy_ = bstack1lll1l11ll_opy_(args, logger, CONFIG, bstack1llll1l1_opy_)
    bstack1l1lll1l1l_opy_.bstack1l111l11_opy_()
    bstack1llllllll1_opy_()
    bstack1ll111111_opy_ = True
    bstack1111l1l1l_opy_ = bstack1l1lll1l1l_opy_.bstack1l1lll1111_opy_()
    bstack1l1lll1l1l_opy_.bstack1l11l1l1l_opy_(bstack1111ll1l1_opy_)
    bstack1l1lll1l1l_opy_.bstack11llll1ll_opy_()
    bstack111l1llll_opy_(bstack1ll11l1ll_opy_, CONFIG, bstack1l1lll1l1l_opy_.bstack1l11111l_opy_())
    bstack1l1111ll_opy_ = bstack1l1lll1l1l_opy_.bstack1ll1l1l1ll_opy_(bstack11l11l1l1l_opy_, {
      bstack11ll1_opy_ (u"ࠪࡌ࡚ࡈ࡟ࡖࡔࡏࠫโ"): bstack1l1ll11ll1_opy_,
      bstack11ll1_opy_ (u"ࠫࡎ࡙࡟ࡂࡒࡓࡣࡆ࡛ࡔࡐࡏࡄࡘࡊ࠭ใ"): bstack1l11l1l1ll_opy_,
      bstack11ll1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡆ࡛ࡔࡐࡏࡄࡘࡎࡕࡎࠨไ"): bstack1llll1l1_opy_
    })
    try:
      bstack111l1ll1_opy_, bstack1l11l11l_opy_ = map(list, zip(*bstack1l1111ll_opy_))
      bstack1l111lll_opy_ = bstack111l1ll1_opy_[0]
      for status_code in bstack1l11l11l_opy_:
        if status_code != 0:
          bstack11ll1ll11l_opy_ = status_code
          break
    except Exception as e:
      logger.debug(bstack11ll1_opy_ (u"ࠨࡕ࡯ࡣࡥࡰࡪࠦࡴࡰࠢࡶࡥࡻ࡫ࠠࡦࡴࡵࡳࡷࡹࠠࡢࡰࡧࠤࡸࡺࡡࡵࡷࡶࠤࡨࡵࡤࡦ࠰ࠣࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦ࠺ࠡࡽࢀࠦๅ").format(str(e)))
  elif bstack1ll11l1ll_opy_ == bstack11ll1_opy_ (u"ࠧࡣࡧ࡫ࡥࡻ࡫ࠧๆ"):
    try:
      from behave.__main__ import main as bstack1ll111lll1_opy_
      from behave.configuration import Configuration
    except Exception as e:
      bstack1ll1l1l111_opy_(e, bstack1ll1llllll_opy_)
    bstack1llllllll1_opy_()
    bstack1ll111111_opy_ = True
    bstack11l1l1l1l_opy_ = 1
    if bstack11ll1_opy_ (u"ࠨࡲࡤࡶࡦࡲ࡬ࡦ࡮ࡶࡔࡪࡸࡐ࡭ࡣࡷࡪࡴࡸ࡭ࠨ็") in CONFIG:
      bstack11l1l1l1l_opy_ = CONFIG[bstack11ll1_opy_ (u"ࠩࡳࡥࡷࡧ࡬࡭ࡧ࡯ࡷࡕ࡫ࡲࡑ࡮ࡤࡸ࡫ࡵࡲ࡮่ࠩ")]
    if bstack11ll1_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ้࠭") in CONFIG:
      bstack1l111l1111_opy_ = int(bstack11l1l1l1l_opy_) * int(len(CONFIG[bstack11ll1_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹ๊ࠧ")]))
    else:
      bstack1l111l1111_opy_ = int(bstack11l1l1l1l_opy_)
    config = Configuration(args)
    bstack111lll11l1_opy_ = config.paths
    if len(bstack111lll11l1_opy_) == 0:
      import glob
      pattern = bstack11ll1_opy_ (u"ࠬ࠰ࠪ࠰ࠬ࠱ࡪࡪࡧࡴࡶࡴࡨ๋ࠫ")
      bstack1l11lll11l_opy_ = glob.glob(pattern, recursive=True)
      args.extend(bstack1l11lll11l_opy_)
      config = Configuration(args)
      bstack111lll11l1_opy_ = config.paths
    bstack111ll111l_opy_ = [os.path.normpath(item) for item in bstack111lll11l1_opy_]
    bstack1ll11lll1l_opy_ = [os.path.normpath(item) for item in args]
    bstack1lllll1l11_opy_ = [item for item in bstack1ll11lll1l_opy_ if item not in bstack111ll111l_opy_]
    import platform as pf
    if pf.system().lower() == bstack11ll1_opy_ (u"࠭ࡷࡪࡰࡧࡳࡼࡹࠧ์"):
      from pathlib import PureWindowsPath, PurePosixPath
      bstack111ll111l_opy_ = [str(PurePosixPath(PureWindowsPath(bstack11l1111ll1_opy_)))
                    for bstack11l1111ll1_opy_ in bstack111ll111l_opy_]
    bstack1l1l11ll11_opy_ = []
    for spec in bstack111ll111l_opy_:
      bstack1ll1l1l1_opy_ = []
      bstack1ll1l1l1_opy_ += bstack1lllll1l11_opy_
      bstack1ll1l1l1_opy_.append(spec)
      bstack1l1l11ll11_opy_.append(bstack1ll1l1l1_opy_)
    execution_items = []
    for bstack1ll1l1l1_opy_ in bstack1l1l11ll11_opy_:
      if bstack11ll1_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪํ") in CONFIG:
        for index, _ in enumerate(CONFIG[bstack11ll1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫ๎")]):
          item = {}
          item[bstack11ll1_opy_ (u"ࠩࡤࡶ࡬࠭๏")] = bstack11ll1_opy_ (u"ࠪࠤࠬ๐").join(bstack1ll1l1l1_opy_)
          item[bstack11ll1_opy_ (u"ࠫ࡮ࡴࡤࡦࡺࠪ๑")] = index
          execution_items.append(item)
      else:
        item = {}
        item[bstack11ll1_opy_ (u"ࠬࡧࡲࡨࠩ๒")] = bstack11ll1_opy_ (u"࠭ࠠࠨ๓").join(bstack1ll1l1l1_opy_)
        item[bstack11ll1_opy_ (u"ࠧࡪࡰࡧࡩࡽ࠭๔")] = 0
        execution_items.append(item)
    bstack1111111l_opy_ = bstack1l11ll1l1l_opy_(execution_items, bstack1l111l1111_opy_)
    for execution_item in bstack1111111l_opy_:
      bstack1ll1ll11l1_opy_ = []
      for item in execution_item:
        bstack1ll1ll11l1_opy_.append(bstack1lll1l1ll_opy_(name=str(item[bstack11ll1_opy_ (u"ࠨ࡫ࡱࡨࡪࡾࠧ๕")]),
                                             target=bstack11ll1lll11_opy_,
                                             args=(item[bstack11ll1_opy_ (u"ࠩࡤࡶ࡬࠭๖")],)))
      for t in bstack1ll1ll11l1_opy_:
        t.start()
      for t in bstack1ll1ll11l1_opy_:
        t.join()
  else:
    bstack11ll11l11_opy_(bstack1l11ll11l_opy_)
  if not bstack1l11ll1ll1_opy_:
    bstack11ll1l111l_opy_()
    if(bstack1ll11l1ll_opy_ in [bstack11ll1_opy_ (u"ࠪࡦࡪ࡮ࡡࡷࡧࠪ๗"), bstack11ll1_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࠫ๘")]):
      bstack1ll111l11l_opy_()
  bstack111lll1l1_opy_.bstack11l111ll11_opy_()
def browserstack_initialize(bstack11llll11_opy_=None):
  logger.info(bstack11ll1_opy_ (u"ࠬࡘࡵ࡯ࡰ࡬ࡲ࡬ࠦࡓࡅࡍࠣࡻ࡮ࡺࡨࠡࡣࡵ࡫ࡸࡀࠠࠨ๙") + str(bstack11llll11_opy_))
  run_on_browserstack(bstack11llll11_opy_, None, True)
@measure(event_name=EVENTS.bstack1l111l1lll_opy_, stage=STAGE.bstack11l1llll1_opy_, bstack1lll1l1l1_opy_=bstack1ll1l11111_opy_)
def bstack11ll1l111l_opy_():
  global CONFIG
  global bstack11l1l1ll1l_opy_
  global bstack11ll1ll11l_opy_
  global bstack1lll1l1l11_opy_
  global bstack1l1l1ll1l_opy_
  bstack11ll1l11l_opy_.bstack11l1lllll1_opy_()
  if cli.is_running():
    bstack1111l11l_opy_.invoke(bstack1l11111l1_opy_.bstack11lll1ll_opy_)
  else:
    bstack11l111l1_opy_ = bstack1lll1lll_opy_.bstack1l1l1111_opy_(config=CONFIG)
    bstack11l111l1_opy_.bstack111llll111_opy_(CONFIG)
  if bstack11l1l1ll1l_opy_ == bstack11ll1_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹ࠭๚"):
    if not cli.is_enabled(CONFIG):
      bstack11lll11l11_opy_.stop()
  else:
    bstack11lll11l11_opy_.stop()
  if not cli.is_enabled(CONFIG):
    bstack1l11llll1l_opy_.bstack1lll1lll1l_opy_()
  if bstack11ll1_opy_ (u"ࠧࡵࡷࡵࡦࡴ࡙ࡣࡢ࡮ࡨࠫ๛") in CONFIG and str(CONFIG[bstack11ll1_opy_ (u"ࠨࡶࡸࡶࡧࡵࡓࡤࡣ࡯ࡩࠬ๜")]).lower() != bstack11ll1_opy_ (u"ࠩࡩࡥࡱࡹࡥࠨ๝"):
    hashed_id, bstack1l111l1l11_opy_ = bstack1llll1l1l1_opy_()
  else:
    hashed_id, bstack1l111l1l11_opy_ = get_build_link()
  bstack1ll11ll1l_opy_(hashed_id)
  logger.info(bstack11ll1_opy_ (u"ࠪࡗࡉࡑࠠࡳࡷࡱࠤࡪࡴࡤࡦࡦࠣࡪࡴࡸࠠࡪࡦ࠽ࠫ๞") + bstack1l1l1ll1l_opy_.get_property(bstack11ll1_opy_ (u"ࠫࡸࡪ࡫ࡓࡷࡱࡍࡩ࠭๟"), bstack11ll1_opy_ (u"ࠬ࠭๠")) + bstack11ll1_opy_ (u"࠭ࠬࠡࡶࡨࡷࡹ࡮ࡵࡣࠢ࡬ࡨ࠿ࠦࠧ๡") + os.getenv(bstack11ll1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡌ࡚ࡈ࡟ࡖࡗࡌࡈࠬ๢"), bstack11ll1_opy_ (u"ࠨࠩ๣")))
  if hashed_id is not None and bstack1ll1ll11l_opy_() != -1:
    sessions = bstack111lllll1_opy_(hashed_id)
    bstack11l1lll11l_opy_(sessions, bstack1l111l1l11_opy_)
  if bstack11l1l1ll1l_opy_ == bstack11ll1_opy_ (u"ࠩࡳࡽࡹ࡫ࡳࡵࠩ๤") and bstack11ll1ll11l_opy_ != 0:
    sys.exit(bstack11ll1ll11l_opy_)
  if bstack11l1l1ll1l_opy_ == bstack11ll1_opy_ (u"ࠪࡦࡪ࡮ࡡࡷࡧࠪ๥") and bstack1lll1l1l11_opy_ != 0:
    sys.exit(bstack1lll1l1l11_opy_)
def bstack1ll11ll1l_opy_(new_id):
    global bstack1ll11ll111_opy_
    bstack1ll11ll111_opy_ = new_id
def bstack1ll1l11l11_opy_(bstack111l11l11_opy_):
  if bstack111l11l11_opy_:
    return bstack111l11l11_opy_.capitalize()
  else:
    return bstack11ll1_opy_ (u"ࠫࠬ๦")
@measure(event_name=EVENTS.bstack1l1lllllll_opy_, stage=STAGE.bstack11l1llll1_opy_, bstack1lll1l1l1_opy_=bstack1ll1l11111_opy_)
def bstack1111111ll_opy_(bstack1l11111111_opy_):
  if bstack11ll1_opy_ (u"ࠬࡴࡡ࡮ࡧࠪ๧") in bstack1l11111111_opy_ and bstack1l11111111_opy_[bstack11ll1_opy_ (u"࠭࡮ࡢ࡯ࡨࠫ๨")] != bstack11ll1_opy_ (u"ࠧࠨ๩"):
    return bstack1l11111111_opy_[bstack11ll1_opy_ (u"ࠨࡰࡤࡱࡪ࠭๪")]
  else:
    bstack1lll1l1l1_opy_ = bstack11ll1_opy_ (u"ࠤࠥ๫")
    if bstack11ll1_opy_ (u"ࠪࡨࡪࡼࡩࡤࡧࠪ๬") in bstack1l11111111_opy_ and bstack1l11111111_opy_[bstack11ll1_opy_ (u"ࠫࡩ࡫ࡶࡪࡥࡨࠫ๭")] != None:
      bstack1lll1l1l1_opy_ += bstack1l11111111_opy_[bstack11ll1_opy_ (u"ࠬࡪࡥࡷ࡫ࡦࡩࠬ๮")] + bstack11ll1_opy_ (u"ࠨࠬࠡࠤ๯")
      if bstack1l11111111_opy_[bstack11ll1_opy_ (u"ࠧࡰࡵࠪ๰")] == bstack11ll1_opy_ (u"ࠣ࡫ࡲࡷࠧ๱"):
        bstack1lll1l1l1_opy_ += bstack11ll1_opy_ (u"ࠤ࡬ࡓࡘࠦࠢ๲")
      bstack1lll1l1l1_opy_ += (bstack1l11111111_opy_[bstack11ll1_opy_ (u"ࠪࡳࡸࡥࡶࡦࡴࡶ࡭ࡴࡴࠧ๳")] or bstack11ll1_opy_ (u"ࠫࠬ๴"))
      return bstack1lll1l1l1_opy_
    else:
      bstack1lll1l1l1_opy_ += bstack1ll1l11l11_opy_(bstack1l11111111_opy_[bstack11ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࠭๵")]) + bstack11ll1_opy_ (u"ࠨࠠࠣ๶") + (
              bstack1l11111111_opy_[bstack11ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡠࡸࡨࡶࡸ࡯࡯࡯ࠩ๷")] or bstack11ll1_opy_ (u"ࠨࠩ๸")) + bstack11ll1_opy_ (u"ࠤ࠯ࠤࠧ๹")
      if bstack1l11111111_opy_[bstack11ll1_opy_ (u"ࠪࡳࡸ࠭๺")] == bstack11ll1_opy_ (u"ࠦ࡜࡯࡮ࡥࡱࡺࡷࠧ๻"):
        bstack1lll1l1l1_opy_ += bstack11ll1_opy_ (u"ࠧ࡝ࡩ࡯ࠢࠥ๼")
      bstack1lll1l1l1_opy_ += bstack1l11111111_opy_[bstack11ll1_opy_ (u"࠭࡯ࡴࡡࡹࡩࡷࡹࡩࡰࡰࠪ๽")] or bstack11ll1_opy_ (u"ࠧࠨ๾")
      return bstack1lll1l1l1_opy_
@measure(event_name=EVENTS.bstack11llll111_opy_, stage=STAGE.bstack11l1llll1_opy_, bstack1lll1l1l1_opy_=bstack1ll1l11111_opy_)
def bstack1lllllllll_opy_(bstack11111l11l_opy_):
  if bstack11111l11l_opy_ == bstack11ll1_opy_ (u"ࠣࡦࡲࡲࡪࠨ๿"):
    return bstack11ll1_opy_ (u"ࠩ࠿ࡸࡩࠦࡣ࡭ࡣࡶࡷࡂࠨࡢࡴࡶࡤࡧࡰ࠳ࡤࡢࡶࡤࠦࠥࡹࡴࡺ࡮ࡨࡁࠧࡩ࡯࡭ࡱࡵ࠾࡬ࡸࡥࡦࡰ࠾ࠦࡃࡂࡦࡰࡰࡷࠤࡨࡵ࡬ࡰࡴࡀࠦ࡬ࡸࡥࡦࡰࠥࡂࡈࡵ࡭ࡱ࡮ࡨࡸࡪࡪ࠼࠰ࡨࡲࡲࡹࡄ࠼࠰ࡶࡧࡂࠬ຀")
  elif bstack11111l11l_opy_ == bstack11ll1_opy_ (u"ࠥࡪࡦ࡯࡬ࡦࡦࠥກ"):
    return bstack11ll1_opy_ (u"ࠫࡁࡺࡤࠡࡥ࡯ࡥࡸࡹ࠽ࠣࡤࡶࡸࡦࡩ࡫࠮ࡦࡤࡸࡦࠨࠠࡴࡶࡼࡰࡪࡃࠢࡤࡱ࡯ࡳࡷࡀࡲࡦࡦ࠾ࠦࡃࡂࡦࡰࡰࡷࠤࡨࡵ࡬ࡰࡴࡀࠦࡷ࡫ࡤࠣࡀࡉࡥ࡮ࡲࡥࡥ࠾࠲ࡪࡴࡴࡴ࠿࠾࠲ࡸࡩࡄࠧຂ")
  elif bstack11111l11l_opy_ == bstack11ll1_opy_ (u"ࠧࡶࡡࡴࡵࡨࡨࠧ຃"):
    return bstack11ll1_opy_ (u"࠭࠼ࡵࡦࠣࡧࡱࡧࡳࡴ࠿ࠥࡦࡸࡺࡡࡤ࡭࠰ࡨࡦࡺࡡࠣࠢࡶࡸࡾࡲࡥ࠾ࠤࡦࡳࡱࡵࡲ࠻ࡩࡵࡩࡪࡴ࠻ࠣࡀ࠿ࡪࡴࡴࡴࠡࡥࡲࡰࡴࡸ࠽ࠣࡩࡵࡩࡪࡴࠢ࠿ࡒࡤࡷࡸ࡫ࡤ࠽࠱ࡩࡳࡳࡺ࠾࠽࠱ࡷࡨࡃ࠭ຄ")
  elif bstack11111l11l_opy_ == bstack11ll1_opy_ (u"ࠢࡦࡴࡵࡳࡷࠨ຅"):
    return bstack11ll1_opy_ (u"ࠨ࠾ࡷࡨࠥࡩ࡬ࡢࡵࡶࡁࠧࡨࡳࡵࡣࡦ࡯࠲ࡪࡡࡵࡣࠥࠤࡸࡺࡹ࡭ࡧࡀࠦࡨࡵ࡬ࡰࡴ࠽ࡶࡪࡪ࠻ࠣࡀ࠿ࡪࡴࡴࡴࠡࡥࡲࡰࡴࡸ࠽ࠣࡴࡨࡨࠧࡄࡅࡳࡴࡲࡶࡁ࠵ࡦࡰࡰࡷࡂࡁ࠵ࡴࡥࡀࠪຆ")
  elif bstack11111l11l_opy_ == bstack11ll1_opy_ (u"ࠤࡷ࡭ࡲ࡫࡯ࡶࡶࠥງ"):
    return bstack11ll1_opy_ (u"ࠪࡀࡹࡪࠠࡤ࡮ࡤࡷࡸࡃࠢࡣࡵࡷࡥࡨࡱ࠭ࡥࡣࡷࡥࠧࠦࡳࡵࡻ࡯ࡩࡂࠨࡣࡰ࡮ࡲࡶ࠿ࠩࡥࡦࡣ࠶࠶࠻ࡁࠢ࠿࠾ࡩࡳࡳࡺࠠࡤࡱ࡯ࡳࡷࡃࠢࠤࡧࡨࡥ࠸࠸࠶ࠣࡀࡗ࡭ࡲ࡫࡯ࡶࡶ࠿࠳࡫ࡵ࡮ࡵࡀ࠿࠳ࡹࡪ࠾ࠨຈ")
  elif bstack11111l11l_opy_ == bstack11ll1_opy_ (u"ࠦࡷࡻ࡮࡯࡫ࡱ࡫ࠧຉ"):
    return bstack11ll1_opy_ (u"ࠬࡂࡴࡥࠢࡦࡰࡦࡹࡳ࠾ࠤࡥࡷࡹࡧࡣ࡬࠯ࡧࡥࡹࡧࠢࠡࡵࡷࡽࡱ࡫࠽ࠣࡥࡲࡰࡴࡸ࠺ࡣ࡮ࡤࡧࡰࡁࠢ࠿࠾ࡩࡳࡳࡺࠠࡤࡱ࡯ࡳࡷࡃࠢࡣ࡮ࡤࡧࡰࠨ࠾ࡓࡷࡱࡲ࡮ࡴࡧ࠽࠱ࡩࡳࡳࡺ࠾࠽࠱ࡷࡨࡃ࠭ຊ")
  else:
    return bstack11ll1_opy_ (u"࠭࠼ࡵࡦࠣࡥࡱ࡯ࡧ࡯࠿ࠥࡧࡪࡴࡴࡦࡴࠥࠤࡨࡲࡡࡴࡵࡀࠦࡧࡹࡴࡢࡥ࡮࠱ࡩࡧࡴࡢࠤࠣࡷࡹࡿ࡬ࡦ࠿ࠥࡧࡴࡲ࡯ࡳ࠼ࡥࡰࡦࡩ࡫࠼ࠤࡁࡀ࡫ࡵ࡮ࡵࠢࡦࡳࡱࡵࡲ࠾ࠤࡥࡰࡦࡩ࡫ࠣࡀࠪ຋") + bstack1ll1l11l11_opy_(
      bstack11111l11l_opy_) + bstack11ll1_opy_ (u"ࠧ࠽࠱ࡩࡳࡳࡺ࠾࠽࠱ࡷࡨࡃ࠭ຌ")
def bstack11ll1lll_opy_(session):
  return bstack11ll1_opy_ (u"ࠨ࠾ࡷࡶࠥࡩ࡬ࡢࡵࡶࡁࠧࡨࡳࡵࡣࡦ࡯࠲ࡸ࡯ࡸࠤࡁࡀࡹࡪࠠࡤ࡮ࡤࡷࡸࡃࠢࡣࡵࡷࡥࡨࡱ࠭ࡥࡣࡷࡥࠥࡹࡥࡴࡵ࡬ࡳࡳ࠳࡮ࡢ࡯ࡨࠦࡃࡂࡡࠡࡪࡵࡩ࡫ࡃࠢࡼࡿࠥࠤࡹࡧࡲࡨࡧࡷࡁࠧࡥࡢ࡭ࡣࡱ࡯ࠧࡄࡻࡾ࠾࠲ࡥࡃࡂ࠯ࡵࡦࡁࡿࢂࢁࡽ࠽ࡶࡧࠤࡦࡲࡩࡨࡰࡀࠦࡨ࡫࡮ࡵࡧࡵࠦࠥࡩ࡬ࡢࡵࡶࡁࠧࡨࡳࡵࡣࡦ࡯࠲ࡪࡡࡵࡣࠥࡂࢀࢃ࠼࠰ࡶࡧࡂࡁࡺࡤࠡࡣ࡯࡭࡬ࡴ࠽ࠣࡥࡨࡲࡹ࡫ࡲࠣࠢࡦࡰࡦࡹࡳ࠾ࠤࡥࡷࡹࡧࡣ࡬࠯ࡧࡥࡹࡧࠢ࠿ࡽࢀࡀ࠴ࡺࡤ࠿࠾ࡷࡨࠥࡧ࡬ࡪࡩࡱࡁࠧࡩࡥ࡯ࡶࡨࡶࠧࠦࡣ࡭ࡣࡶࡷࡂࠨࡢࡴࡶࡤࡧࡰ࠳ࡤࡢࡶࡤࠦࡃࢁࡽ࠽࠱ࡷࡨࡃࡂࡴࡥࠢࡤࡰ࡮࡭࡮࠾ࠤࡦࡩࡳࡺࡥࡳࠤࠣࡧࡱࡧࡳࡴ࠿ࠥࡦࡸࡺࡡࡤ࡭࠰ࡨࡦࡺࡡࠣࡀࡾࢁࡁ࠵ࡴࡥࡀ࠿࠳ࡹࡸ࠾ࠨຍ").format(
    session[bstack11ll1_opy_ (u"ࠩࡳࡹࡧࡲࡩࡤࡡࡸࡶࡱ࠭ຎ")], bstack1111111ll_opy_(session), bstack1lllllllll_opy_(session[bstack11ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡶࡸࡦࡺࡵࡴࠩຏ")]),
    bstack1lllllllll_opy_(session[bstack11ll1_opy_ (u"ࠫࡸࡺࡡࡵࡷࡶࠫຐ")]),
    bstack1ll1l11l11_opy_(session[bstack11ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࠭ຑ")] or session[bstack11ll1_opy_ (u"࠭ࡤࡦࡸ࡬ࡧࡪ࠭ຒ")] or bstack11ll1_opy_ (u"ࠧࠨຓ")) + bstack11ll1_opy_ (u"ࠣࠢࠥດ") + (session[bstack11ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡢࡺࡪࡸࡳࡪࡱࡱࠫຕ")] or bstack11ll1_opy_ (u"ࠪࠫຖ")),
    session[bstack11ll1_opy_ (u"ࠫࡴࡹࠧທ")] + bstack11ll1_opy_ (u"ࠧࠦࠢຘ") + session[bstack11ll1_opy_ (u"࠭࡯ࡴࡡࡹࡩࡷࡹࡩࡰࡰࠪນ")], session[bstack11ll1_opy_ (u"ࠧࡥࡷࡵࡥࡹ࡯࡯࡯ࠩບ")] or bstack11ll1_opy_ (u"ࠨࠩປ"),
    session[bstack11ll1_opy_ (u"ࠩࡦࡶࡪࡧࡴࡦࡦࡢࡥࡹ࠭ຜ")] if session[bstack11ll1_opy_ (u"ࠪࡧࡷ࡫ࡡࡵࡧࡧࡣࡦࡺࠧຝ")] else bstack11ll1_opy_ (u"ࠫࠬພ"))
@measure(event_name=EVENTS.bstack1l11l1ll11_opy_, stage=STAGE.bstack11l1llll1_opy_, bstack1lll1l1l1_opy_=bstack1ll1l11111_opy_)
def bstack11l1lll11l_opy_(sessions, bstack1l111l1l11_opy_):
  try:
    bstack1l111111_opy_ = bstack11ll1_opy_ (u"ࠧࠨຟ")
    if not os.path.exists(bstack1l11l1l11_opy_):
      os.mkdir(bstack1l11l1l11_opy_)
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), bstack11ll1_opy_ (u"࠭ࡡࡴࡵࡨࡸࡸ࠵ࡲࡦࡲࡲࡶࡹ࠴ࡨࡵ࡯࡯ࠫຠ")), bstack11ll1_opy_ (u"ࠧࡳࠩມ")) as f:
      bstack1l111111_opy_ = f.read()
    bstack1l111111_opy_ = bstack1l111111_opy_.replace(bstack11ll1_opy_ (u"ࠨࡽࠨࡖࡊ࡙ࡕࡍࡖࡖࡣࡈࡕࡕࡏࡖࠨࢁࠬຢ"), str(len(sessions)))
    bstack1l111111_opy_ = bstack1l111111_opy_.replace(bstack11ll1_opy_ (u"ࠩࡾࠩࡇ࡛ࡉࡍࡆࡢ࡙ࡗࡒࠥࡾࠩຣ"), bstack1l111l1l11_opy_)
    bstack1l111111_opy_ = bstack1l111111_opy_.replace(bstack11ll1_opy_ (u"ࠪࡿࠪࡈࡕࡊࡎࡇࡣࡓࡇࡍࡆࠧࢀࠫ຤"),
                                              sessions[0].get(bstack11ll1_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡢࡲࡦࡳࡥࠨລ")) if sessions[0] else bstack11ll1_opy_ (u"ࠬ࠭຦"))
    with open(os.path.join(bstack1l11l1l11_opy_, bstack11ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠲ࡸࡥࡱࡱࡵࡸ࠳࡮ࡴ࡮࡮ࠪວ")), bstack11ll1_opy_ (u"ࠧࡸࠩຨ")) as stream:
      stream.write(bstack1l111111_opy_.split(bstack11ll1_opy_ (u"ࠨࡽࠨࡗࡊ࡙ࡓࡊࡑࡑࡗࡤࡊࡁࡕࡃࠨࢁࠬຩ"))[0])
      for session in sessions:
        stream.write(bstack11ll1lll_opy_(session))
      stream.write(bstack1l111111_opy_.split(bstack11ll1_opy_ (u"ࠩࡾࠩࡘࡋࡓࡔࡋࡒࡒࡘࡥࡄࡂࡖࡄࠩࢂ࠭ສ"))[1])
    logger.info(bstack11ll1_opy_ (u"ࠪࡋࡪࡴࡥࡳࡣࡷࡩࡩࠦࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࠥࡨࡵࡪ࡮ࡧࠤࡦࡸࡴࡪࡨࡤࡧࡹࡹࠠࡢࡶࠣࡿࢂ࠭ຫ").format(bstack1l11l1l11_opy_));
  except Exception as e:
    logger.debug(bstack11l11llll_opy_.format(str(e)))
def bstack111lllll1_opy_(hashed_id):
  global CONFIG
  try:
    bstack1ll11l1l1l_opy_ = datetime.datetime.now()
    host = bstack11ll1_opy_ (u"ࠫ࡭ࡺࡴࡱࡵ࠽࠳࠴ࡧࡰࡪ࠯ࡦࡰࡴࡻࡤ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡤࡱࡰࠫຬ") if bstack11ll1_opy_ (u"ࠬࡧࡰࡱࠩອ") in CONFIG else bstack11ll1_opy_ (u"࠭ࡨࡵࡶࡳࡷ࠿࠵࠯ࡢࡲ࡬࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡧࡴࡳࠧຮ")
    user = CONFIG[bstack11ll1_opy_ (u"ࠧࡶࡵࡨࡶࡓࡧ࡭ࡦࠩຯ")]
    key = CONFIG[bstack11ll1_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡌࡧࡼࠫະ")]
    bstack11llll1l11_opy_ = bstack11ll1_opy_ (u"ࠩࡤࡴࡵ࠳ࡡࡶࡶࡲࡱࡦࡺࡥࠨັ") if bstack11ll1_opy_ (u"ࠪࡥࡵࡶࠧາ") in CONFIG else (bstack11ll1_opy_ (u"ࠫࡹࡻࡲࡣࡱࡶࡧࡦࡲࡥࠨຳ") if CONFIG.get(bstack11ll1_opy_ (u"ࠬࡺࡵࡳࡤࡲࡷࡨࡧ࡬ࡦࠩິ")) else bstack11ll1_opy_ (u"࠭ࡡࡶࡶࡲࡱࡦࡺࡥࠨີ"))
    host = bstack1ll1l111_opy_(cli.config, [bstack11ll1_opy_ (u"ࠢࡢࡲ࡬ࡷࠧຶ"), bstack11ll1_opy_ (u"ࠣࡣࡳࡴࡆࡻࡴࡰ࡯ࡤࡸࡪࠨື"), bstack11ll1_opy_ (u"ࠤࡤࡴ࡮ࠨຸ")], host) if bstack11ll1_opy_ (u"ࠪࡥࡵࡶູࠧ") in CONFIG else bstack1ll1l111_opy_(cli.config, [bstack11ll1_opy_ (u"ࠦࡦࡶࡩࡴࠤ຺"), bstack11ll1_opy_ (u"ࠧࡧࡵࡵࡱࡰࡥࡹ࡫ࠢົ"), bstack11ll1_opy_ (u"ࠨࡡࡱ࡫ࠥຼ")], host)
    url = bstack11ll1_opy_ (u"ࠧࡼࡿ࠲ࡿࢂ࠵ࡢࡶ࡫࡯ࡨࡸ࠵ࡻࡾ࠱ࡶࡩࡸࡹࡩࡰࡰࡶ࠲࡯ࡹ࡯࡯ࠩຽ").format(host, bstack11llll1l11_opy_, hashed_id)
    headers = {
      bstack11ll1_opy_ (u"ࠨࡅࡲࡲࡹ࡫࡮ࡵ࠯ࡷࡽࡵ࡫ࠧ຾"): bstack11ll1_opy_ (u"ࠩࡤࡴࡵࡲࡩࡤࡣࡷ࡭ࡴࡴ࠯࡫ࡵࡲࡲࠬ຿"),
    }
    proxies = bstack1lllll1111_opy_(CONFIG, url)
    response = requests.get(url, headers=headers, proxies=proxies, auth=(user, key))
    if response.json():
      cli.bstack1lll1lll1_opy_(bstack11ll1_opy_ (u"ࠥ࡬ࡹࡺࡰ࠻ࡩࡨࡸࡤࡹࡥࡴࡵ࡬ࡳࡳࡹ࡟࡭࡫ࡶࡸࠧເ"), datetime.datetime.now() - bstack1ll11l1l1l_opy_)
      return list(map(lambda session: session[bstack11ll1_opy_ (u"ࠫࡦࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࡠࡵࡨࡷࡸ࡯࡯࡯ࠩແ")], response.json()))
  except Exception as e:
    logger.debug(bstack11ll11lll1_opy_.format(str(e)))
@measure(event_name=EVENTS.bstack1l111ll1l_opy_, stage=STAGE.bstack11l1llll1_opy_, bstack1lll1l1l1_opy_=bstack1ll1l11111_opy_)
def get_build_link():
  global CONFIG
  global bstack1ll11ll111_opy_
  try:
    if bstack11ll1_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡒࡦࡳࡥࠨໂ") in CONFIG:
      bstack1ll11l1l1l_opy_ = datetime.datetime.now()
      host = bstack11ll1_opy_ (u"࠭ࡡࡱ࡫࠰ࡧࡱࡵࡵࡥࠩໃ") if bstack11ll1_opy_ (u"ࠧࡢࡲࡳࠫໄ") in CONFIG else bstack11ll1_opy_ (u"ࠨࡣࡳ࡭ࠬ໅")
      user = CONFIG[bstack11ll1_opy_ (u"ࠩࡸࡷࡪࡸࡎࡢ࡯ࡨࠫໆ")]
      key = CONFIG[bstack11ll1_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵࡎࡩࡾ࠭໇")]
      bstack11llll1l11_opy_ = bstack11ll1_opy_ (u"ࠫࡦࡶࡰ࠮ࡣࡸࡸࡴࡳࡡࡵࡧ່ࠪ") if bstack11ll1_opy_ (u"ࠬࡧࡰࡱ້ࠩ") in CONFIG else bstack11ll1_opy_ (u"࠭ࡡࡶࡶࡲࡱࡦࡺࡥࠨ໊")
      url = bstack11ll1_opy_ (u"ࠧࡩࡶࡷࡴࡸࡀ࠯࠰ࡽࢀ࠾ࢀࢃࡀࡼࡿ࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡦࡳࡲ࠵ࡻࡾ࠱ࡥࡹ࡮ࡲࡤࡴ࠰࡭ࡷࡴࡴ໋ࠧ").format(user, key, host, bstack11llll1l11_opy_)
      if cli.is_enabled(CONFIG):
        bstack1l111l1l11_opy_, hashed_id = cli.bstack1llll111_opy_()
        logger.info(bstack1lll1l1lll_opy_.format(bstack1l111l1l11_opy_))
        return [hashed_id, bstack1l111l1l11_opy_]
      else:
        headers = {
          bstack11ll1_opy_ (u"ࠨࡅࡲࡲࡹ࡫࡮ࡵ࠯ࡷࡽࡵ࡫ࠧ໌"): bstack11ll1_opy_ (u"ࠩࡤࡴࡵࡲࡩࡤࡣࡷ࡭ࡴࡴ࠯࡫ࡵࡲࡲࠬໍ"),
        }
        if bstack11ll1_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬ໎") in CONFIG:
          params = {bstack11ll1_opy_ (u"ࠫࡳࡧ࡭ࡦࠩ໏"): CONFIG[bstack11ll1_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡒࡦࡳࡥࠨ໐")], bstack11ll1_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡤ࡯ࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩ໑"): CONFIG[bstack11ll1_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩ໒")]}
        else:
          params = {bstack11ll1_opy_ (u"ࠨࡰࡤࡱࡪ࠭໓"): CONFIG[bstack11ll1_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡏࡣࡰࡩࠬ໔")]}
        proxies = bstack1lllll1111_opy_(CONFIG, url)
        response = requests.get(url, params=params, headers=headers, proxies=proxies)
        if response.json():
          bstack1ll1l111l_opy_ = response.json()[0][bstack11ll1_opy_ (u"ࠪࡥࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴ࡟ࡣࡷ࡬ࡰࡩ࠭໕")]
          if bstack1ll1l111l_opy_:
            bstack1l111l1l11_opy_ = bstack1ll1l111l_opy_[bstack11ll1_opy_ (u"ࠫࡵࡻࡢ࡭࡫ࡦࡣࡺࡸ࡬ࠨ໖")].split(bstack11ll1_opy_ (u"ࠬࡶࡵࡣ࡮࡬ࡧ࠲ࡨࡵࡪ࡮ࡧࠫ໗"))[0] + bstack11ll1_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡸ࠵ࠧ໘") + bstack1ll1l111l_opy_[
              bstack11ll1_opy_ (u"ࠧࡩࡣࡶ࡬ࡪࡪ࡟ࡪࡦࠪ໙")]
            logger.info(bstack1lll1l1lll_opy_.format(bstack1l111l1l11_opy_))
            bstack1ll11ll111_opy_ = bstack1ll1l111l_opy_[bstack11ll1_opy_ (u"ࠨࡪࡤࡷ࡭࡫ࡤࡠ࡫ࡧࠫ໚")]
            bstack11ll1l1l11_opy_ = CONFIG[bstack11ll1_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡏࡣࡰࡩࠬ໛")]
            if bstack11ll1_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬໜ") in CONFIG:
              bstack11ll1l1l11_opy_ += bstack11ll1_opy_ (u"ࠫࠥ࠭ໝ") + CONFIG[bstack11ll1_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧໞ")]
            if bstack11ll1l1l11_opy_ != bstack1ll1l111l_opy_[bstack11ll1_opy_ (u"࠭࡮ࡢ࡯ࡨࠫໟ")]:
              logger.debug(bstack1llll11lll_opy_.format(bstack1ll1l111l_opy_[bstack11ll1_opy_ (u"ࠧ࡯ࡣࡰࡩࠬ໠")], bstack11ll1l1l11_opy_))
            cli.bstack1lll1lll1_opy_(bstack11ll1_opy_ (u"ࠣࡪࡷࡸࡵࡀࡧࡦࡶࡢࡦࡺ࡯࡬ࡥࡡ࡯࡭ࡳࡱࠢ໡"), datetime.datetime.now() - bstack1ll11l1l1l_opy_)
            return [bstack1ll1l111l_opy_[bstack11ll1_opy_ (u"ࠩ࡫ࡥࡸ࡮ࡥࡥࡡ࡬ࡨࠬ໢")], bstack1l111l1l11_opy_]
    else:
      logger.warning(bstack11l1lll111_opy_)
  except Exception as e:
    logger.debug(bstack11ll11111_opy_.format(str(e)))
  return [None, None]
def bstack11ll1ll1ll_opy_(url, bstack1lll111l1l_opy_=False):
  global CONFIG
  global bstack1l1ll1l11l_opy_
  if not bstack1l1ll1l11l_opy_:
    hostname = bstack1l1111ll1_opy_(url)
    is_private = bstack1111ll1l_opy_(hostname)
    if (bstack11ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡎࡲࡧࡦࡲࠧ໣") in CONFIG and not bstack1111lll1_opy_(CONFIG[bstack11ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡏࡳࡨࡧ࡬ࠨ໤")])) and (is_private or bstack1lll111l1l_opy_):
      bstack1l1ll1l11l_opy_ = hostname
def bstack1l1111ll1_opy_(url):
  return urlparse(url).hostname
def bstack1111ll1l_opy_(hostname):
  for bstack1l1l11llll_opy_ in bstack11llll1ll1_opy_:
    regex = re.compile(bstack1l1l11llll_opy_)
    if regex.match(hostname):
      return True
  return False
def bstack111llll11l_opy_(bstack11ll11l111_opy_):
  return True if bstack11ll11l111_opy_ in threading.current_thread().__dict__.keys() else False
@measure(event_name=EVENTS.bstack1lll1l111l_opy_, stage=STAGE.bstack11l1llll1_opy_, bstack1lll1l1l1_opy_=bstack1ll1l11111_opy_)
def getAccessibilityResults(driver):
  global CONFIG
  global bstack111l11l1l_opy_
  bstack11ll1l1ll1_opy_ = not (bstack1lll11l1l_opy_(threading.current_thread(), bstack11ll1_opy_ (u"ࠬ࡯ࡳࡂ࠳࠴ࡽ࡙࡫ࡳࡵࠩ໥"), None) and bstack1lll11l1l_opy_(
          threading.current_thread(), bstack11ll1_opy_ (u"࠭ࡡ࠲࠳ࡼࡔࡱࡧࡴࡧࡱࡵࡱࠬ໦"), None))
  bstack1l1ll1ll1_opy_ = getattr(driver, bstack11ll1_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱࡁ࠲࠳ࡼࡗ࡭ࡵࡵ࡭ࡦࡖࡧࡦࡴࠧ໧"), None) != True
  bstack111lll1l_opy_ = bstack1lll11l1l_opy_(threading.current_thread(), bstack11ll1_opy_ (u"ࠨ࡫ࡶࡅࡵࡶࡁ࠲࠳ࡼࡘࡪࡹࡴࠨ໨"), None) and bstack1lll11l1l_opy_(
          threading.current_thread(), bstack11ll1_opy_ (u"ࠩࡤࡴࡵࡇ࠱࠲ࡻࡓࡰࡦࡺࡦࡰࡴࡰࠫ໩"), None)
  if bstack111lll1l_opy_:
    if not bstack1l1l11ll1l_opy_():
      logger.warning(bstack11ll1_opy_ (u"ࠥࡒࡴࡺࠠࡢࡰࠣࡅࡵࡶࠠࡂࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡂࡷࡷࡳࡲࡧࡴࡪࡱࡱࠤࡸ࡫ࡳࡴ࡫ࡲࡲ࠱ࠦࡣࡢࡰࡱࡳࡹࠦࡲࡦࡶࡵ࡭ࡪࡼࡥࠡࡃࡳࡴࠥࡇࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡸࡥࡴࡷ࡯ࡸࡸ࠴ࠢ໪"))
      return {}
    logger.debug(bstack11ll1_opy_ (u"ࠫࡕ࡫ࡲࡧࡱࡵࡱ࡮ࡴࡧࠡࡵࡦࡥࡳࠦࡢࡦࡨࡲࡶࡪࠦࡧࡦࡶࡷ࡭ࡳ࡭ࠠࡳࡧࡶࡹࡱࡺࡳࠨ໫"))
    logger.debug(perform_scan(driver, driver_command=bstack11ll1_opy_ (u"ࠬ࡫ࡸࡦࡥࡸࡸࡪ࡙ࡣࡳ࡫ࡳࡸࠬ໬")))
    results = bstack11ll1l1111_opy_(bstack11ll1_opy_ (u"ࠨࡲࡦࡵࡸࡰࡹࡹࠢ໭"))
    if results is not None and results.get(bstack11ll1_opy_ (u"ࠢࡪࡵࡶࡹࡪࡹࠢ໮")) is not None:
        return results[bstack11ll1_opy_ (u"ࠣ࡫ࡶࡷࡺ࡫ࡳࠣ໯")]
    logger.error(bstack11ll1_opy_ (u"ࠤࡑࡳࠥࡇࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡘࡥࡴࡷ࡯ࡸࡸࠦࡷࡦࡴࡨࠤ࡫ࡵࡵ࡯ࡦ࠱ࠦ໰"))
    return []
  if not bstack1l1ll11l1l_opy_.bstack1ll11l1ll1_opy_(CONFIG, bstack111l11l1l_opy_) or (bstack1l1ll1ll1_opy_ and bstack11ll1l1ll1_opy_):
    logger.warning(bstack11ll1_opy_ (u"ࠥࡒࡴࡺࠠࡢࡰࠣࡅࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠣࡅࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࠠࡴࡧࡶࡷ࡮ࡵ࡮࠭ࠢࡦࡥࡳࡴ࡯ࡵࠢࡵࡩࡹࡸࡩࡦࡸࡨࠤࡆࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠤࡷ࡫ࡳࡶ࡮ࡷࡷ࠳ࠨ໱"))
    return {}
  try:
    logger.debug(bstack11ll1_opy_ (u"ࠫࡕ࡫ࡲࡧࡱࡵࡱ࡮ࡴࡧࠡࡵࡦࡥࡳࠦࡢࡦࡨࡲࡶࡪࠦࡧࡦࡶࡷ࡭ࡳ࡭ࠠࡳࡧࡶࡹࡱࡺࡳࠨ໲"))
    logger.debug(perform_scan(driver))
    results = driver.execute_async_script(bstack1l11l111l1_opy_.bstack1l11lll1l_opy_)
    return results
  except Exception:
    logger.error(bstack11ll1_opy_ (u"ࠧࡔ࡯ࠡࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠡࡴࡨࡷࡺࡲࡴࡴࠢࡺࡩࡷ࡫ࠠࡧࡱࡸࡲࡩ࠴ࠢ໳"))
    return {}
@measure(event_name=EVENTS.bstack1ll1ll1ll1_opy_, stage=STAGE.bstack11l1llll1_opy_, bstack1lll1l1l1_opy_=bstack1ll1l11111_opy_)
def getAccessibilityResultsSummary(driver):
  global CONFIG
  global bstack111l11l1l_opy_
  bstack11ll1l1ll1_opy_ = not (bstack1lll11l1l_opy_(threading.current_thread(), bstack11ll1_opy_ (u"࠭ࡩࡴࡃ࠴࠵ࡾ࡚ࡥࡴࡶࠪ໴"), None) and bstack1lll11l1l_opy_(
          threading.current_thread(), bstack11ll1_opy_ (u"ࠧࡢ࠳࠴ࡽࡕࡲࡡࡵࡨࡲࡶࡲ࠭໵"), None))
  bstack1l1ll1ll1_opy_ = getattr(driver, bstack11ll1_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫ࡂ࠳࠴ࡽࡘ࡮࡯ࡶ࡮ࡧࡗࡨࡧ࡮ࠨ໶"), None) != True
  bstack111lll1l_opy_ = bstack1lll11l1l_opy_(threading.current_thread(), bstack11ll1_opy_ (u"ࠩ࡬ࡷࡆࡶࡰࡂ࠳࠴ࡽ࡙࡫ࡳࡵࠩ໷"), None) and bstack1lll11l1l_opy_(
          threading.current_thread(), bstack11ll1_opy_ (u"ࠪࡥࡵࡶࡁ࠲࠳ࡼࡔࡱࡧࡴࡧࡱࡵࡱࠬ໸"), None)
  if bstack111lll1l_opy_:
    if not bstack1l1l11ll1l_opy_():
      logger.warning(bstack11ll1_opy_ (u"ࠦࡓࡵࡴࠡࡣࡱࠤࡆࡶࡰࠡࡃࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠡࡃࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࠥࡹࡥࡴࡵ࡬ࡳࡳ࠲ࠠࡤࡣࡱࡲࡴࡺࠠࡳࡧࡷࡶ࡮࡫ࡶࡦࠢࡄࡴࡵࠦࡁࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࠦࡲࡦࡵࡸࡰࡹࡹࠠࡴࡷࡰࡱࡦࡸࡹ࠯ࠤ໹"))
      return {}
    logger.debug(bstack11ll1_opy_ (u"ࠬࡖࡥࡳࡨࡲࡶࡲ࡯࡮ࡨࠢࡶࡧࡦࡴࠠࡣࡧࡩࡳࡷ࡫ࠠࡨࡧࡷࡸ࡮ࡴࡧࠡࡴࡨࡷࡺࡲࡴࡴࠢࡶࡹࡲࡳࡡࡳࡻࠪ໺"))
    logger.debug(perform_scan(driver, driver_command=bstack11ll1_opy_ (u"࠭ࡥࡹࡧࡦࡹࡹ࡫ࡓࡤࡴ࡬ࡴࡹ࠭໻")))
    results = bstack11ll1l1111_opy_(bstack11ll1_opy_ (u"ࠢࡳࡧࡶࡹࡱࡺࡓࡶ࡯ࡰࡥࡷࡿࠢ໼"))
    if results is not None and results.get(bstack11ll1_opy_ (u"ࠣࡵࡸࡱࡲࡧࡲࡺࠤ໽")) is not None:
        return results[bstack11ll1_opy_ (u"ࠤࡶࡹࡲࡳࡡࡳࡻࠥ໾")]
    logger.error(bstack11ll1_opy_ (u"ࠥࡒࡴࠦࡁࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࠦࡒࡦࡵࡸࡰࡹࡹࠠࡔࡷࡰࡱࡦࡸࡹࠡࡹࡤࡷࠥ࡬࡯ࡶࡰࡧ࠲ࠧ໿"))
    return {}
  if not bstack1l1ll11l1l_opy_.bstack1ll11l1ll1_opy_(CONFIG, bstack111l11l1l_opy_) or (bstack1l1ll1ll1_opy_ and bstack11ll1l1ll1_opy_):
    logger.warning(bstack11ll1_opy_ (u"ࠦࡓࡵࡴࠡࡣࡱࠤࡆࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠤࡆࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠡࡵࡨࡷࡸ࡯࡯࡯࠮ࠣࡧࡦࡴ࡮ࡰࡶࠣࡶࡪࡺࡲࡪࡧࡹࡩࠥࡇࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡸࡥࡴࡷ࡯ࡸࡸࠦࡳࡶ࡯ࡰࡥࡷࡿ࠮ࠣༀ"))
    return {}
  try:
    logger.debug(bstack11ll1_opy_ (u"ࠬࡖࡥࡳࡨࡲࡶࡲ࡯࡮ࡨࠢࡶࡧࡦࡴࠠࡣࡧࡩࡳࡷ࡫ࠠࡨࡧࡷࡸ࡮ࡴࡧࠡࡴࡨࡷࡺࡲࡴࡴࠢࡶࡹࡲࡳࡡࡳࡻࠪ༁"))
    logger.debug(perform_scan(driver))
    bstack1llllllll_opy_ = driver.execute_async_script(bstack1l11l111l1_opy_.bstack1lll11ll_opy_)
    return bstack1llllllll_opy_
  except Exception:
    logger.error(bstack11ll1_opy_ (u"ࠨࡎࡰࠢࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠢࡶࡹࡲࡳࡡࡳࡻࠣࡻࡦࡹࠠࡧࡱࡸࡲࡩ࠴ࠢ༂"))
    return {}
def bstack1l1l11ll1l_opy_():
  global CONFIG
  global bstack111l11l1l_opy_
  bstack1ll1l11l1l_opy_ = bstack1lll11l1l_opy_(threading.current_thread(), bstack11ll1_opy_ (u"ࠧࡪࡵࡄࡴࡵࡇ࠱࠲ࡻࡗࡩࡸࡺࠧ༃"), None) and bstack1lll11l1l_opy_(threading.current_thread(), bstack11ll1_opy_ (u"ࠨࡣࡳࡴࡆ࠷࠱ࡺࡒ࡯ࡥࡹ࡬࡯ࡳ࡯ࠪ༄"), None)
  if not bstack1l1ll11l1l_opy_.bstack1ll11l1ll1_opy_(CONFIG, bstack111l11l1l_opy_) or not bstack1ll1l11l1l_opy_:
        logger.warning(bstack11ll1_opy_ (u"ࠤࡑࡳࡹࠦࡡ࡯ࠢࡄࡴࡵࠦࡁࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࠦࡁࡶࡶࡲࡱࡦࡺࡩࡰࡰࠣࡷࡪࡹࡳࡪࡱࡱ࠰ࠥࡩࡡ࡯ࡰࡲࡸࠥࡸࡥࡵࡴ࡬ࡩࡻ࡫ࠠࡳࡧࡶࡹࡱࡺࡳ࠯ࠤ༅"))
        return False
  return True
def bstack11ll1l1111_opy_(result_type):
    bstack11lllll1l_opy_ = bstack11lll11l11_opy_.current_test_uuid() if bstack11lll11l11_opy_.current_test_uuid() else bstack1l11llll1l_opy_.current_hook_uuid()
    with ThreadPoolExecutor() as executor:
        future = executor.submit(bstack1lll111l11_opy_(bstack11lllll1l_opy_, result_type))
        try:
            return future.result(timeout=bstack1ll1l1ll1l_opy_)
        except TimeoutError:
            logger.error(bstack11ll1_opy_ (u"ࠥࡘ࡮ࡳࡥࡰࡷࡷࠤࡦ࡬ࡴࡦࡴࠣࡿࢂࡹࠠࡸࡪ࡬ࡰࡪࠦࡦࡦࡶࡦ࡬࡮ࡴࡧࠡࡃࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠡࡔࡨࡷࡺࡲࡴࡴࠤ༆").format(bstack1ll1l1ll1l_opy_))
        except Exception as ex:
            logger.debug(bstack11ll1_opy_ (u"ࠦࡊࡸࡲࡰࡴࠣࡶࡪࡺࡲࡪࡧࡹ࡭ࡳ࡭ࠠࡂࡲࡳࠤࡆࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠤࡆࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠡࡽࢀ࠲ࠥࡋࡲࡳࡱࡵࠤ࠲ࠦࡻࡾࠤ༇").format(result_type, str(ex)))
    return {}
@measure(event_name=EVENTS.bstack11lll11l_opy_, stage=STAGE.bstack11l1llll1_opy_, bstack1lll1l1l1_opy_=bstack1ll1l11111_opy_)
def perform_scan(driver, *args, **kwargs):
  global CONFIG
  global bstack111l11l1l_opy_
  bstack11ll1l1ll1_opy_ = not (bstack1lll11l1l_opy_(threading.current_thread(), bstack11ll1_opy_ (u"ࠬ࡯ࡳࡂ࠳࠴ࡽ࡙࡫ࡳࡵࠩ༈"), None) and bstack1lll11l1l_opy_(
          threading.current_thread(), bstack11ll1_opy_ (u"࠭ࡡ࠲࠳ࡼࡔࡱࡧࡴࡧࡱࡵࡱࠬ༉"), None))
  bstack11llllll1_opy_ = not (bstack1lll11l1l_opy_(threading.current_thread(), bstack11ll1_opy_ (u"ࠧࡪࡵࡄࡴࡵࡇ࠱࠲ࡻࡗࡩࡸࡺࠧ༊"), None) and bstack1lll11l1l_opy_(
          threading.current_thread(), bstack11ll1_opy_ (u"ࠨࡣࡳࡴࡆ࠷࠱ࡺࡒ࡯ࡥࡹ࡬࡯ࡳ࡯ࠪ་"), None))
  bstack1l1ll1ll1_opy_ = getattr(driver, bstack11ll1_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬ࡃ࠴࠵ࡾ࡙ࡨࡰࡷ࡯ࡨࡘࡩࡡ࡯ࠩ༌"), None) != True
  if not bstack1l1ll11l1l_opy_.bstack1ll11l1ll1_opy_(CONFIG, bstack111l11l1l_opy_) or (bstack1l1ll1ll1_opy_ and bstack11ll1l1ll1_opy_ and bstack11llllll1_opy_):
    logger.warning(bstack11ll1_opy_ (u"ࠥࡒࡴࡺࠠࡢࡰࠣࡅࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠣࡅࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࠠࡴࡧࡶࡷ࡮ࡵ࡮࠭ࠢࡦࡥࡳࡴ࡯ࡵࠢࡵࡹࡳࠦࡁࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࠦࡳࡤࡣࡱ࠲ࠧ།"))
    return {}
  try:
    bstack11ll11ll11_opy_ = bstack11ll1_opy_ (u"ࠫࡦࡶࡰࠨ༎") in CONFIG and CONFIG.get(bstack11ll1_opy_ (u"ࠬࡧࡰࡱࠩ༏"), bstack11ll1_opy_ (u"࠭ࠧ༐"))
    session_id = getattr(driver, bstack11ll1_opy_ (u"ࠧࡴࡧࡶࡷ࡮ࡵ࡮ࡠ࡫ࡧࠫ༑"), None)
    if not session_id:
      logger.warning(bstack11ll1_opy_ (u"ࠣࡐࡲࠤࡸ࡫ࡳࡴ࡫ࡲࡲࠥࡏࡄࠡࡨࡲࡹࡳࡪࠠࡧࡱࡵࠤࡩࡸࡩࡷࡧࡵࠦ༒"))
      return {bstack11ll1_opy_ (u"ࠤࡨࡶࡷࡵࡲࠣ༓"): bstack11ll1_opy_ (u"ࠥࡒࡴࠦࡳࡦࡵࡶ࡭ࡴࡴࠠࡊࡆࠣࡪࡴࡻ࡮ࡥࠤ༔")}
    if bstack11ll11ll11_opy_:
      try:
        bstack11l11l11l1_opy_ = {
              bstack11ll1_opy_ (u"ࠫࡹ࡮ࡊࡸࡶࡗࡳࡰ࡫࡮ࠨ༕"): os.environ.get(bstack11ll1_opy_ (u"ࠬࡈࡓࡠࡃ࠴࠵࡞ࡥࡊࡘࡖࠪ༖"), os.environ.get(bstack11ll1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡊࡘࡖࠪ༗"), bstack11ll1_opy_ (u"ࠧࠨ༘"))),
              bstack11ll1_opy_ (u"ࠨࡶ࡫ࡘࡪࡹࡴࡓࡷࡱ࡙ࡺ࡯ࡤࠨ༙"): bstack11lll11l11_opy_.current_test_uuid() if bstack11lll11l11_opy_.current_test_uuid() else bstack1l11llll1l_opy_.current_hook_uuid(),
              bstack11ll1_opy_ (u"ࠩࡤࡹࡹ࡮ࡈࡦࡣࡧࡩࡷ࠭༚"): os.environ.get(bstack11ll1_opy_ (u"ࠪࡆࡘࡥࡁ࠲࠳࡜ࡣࡏ࡝ࡔࠨ༛")),
              bstack11ll1_opy_ (u"ࠫࡸࡩࡡ࡯ࡖ࡬ࡱࡪࡹࡴࡢ࡯ࡳࠫ༜"): str(int(datetime.datetime.now().timestamp() * 1000)),
              bstack11ll1_opy_ (u"ࠬࡺࡨࡃࡷ࡬ࡰࡩ࡛ࡵࡪࡦࠪ༝"): os.environ.get(bstack11ll1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡕࡖࡋࡇࠫ༞"), bstack11ll1_opy_ (u"ࠧࠨ༟")),
              bstack11ll1_opy_ (u"ࠨ࡯ࡨࡸ࡭ࡵࡤࠨ༠"): kwargs.get(bstack11ll1_opy_ (u"ࠩࡧࡶ࡮ࡼࡥࡳࡡࡦࡳࡲࡳࡡ࡯ࡦࠪ༡"), None) or bstack11ll1_opy_ (u"ࠪࠫ༢")
          }
        if not hasattr(thread_local, bstack11ll1_opy_ (u"ࠫࡧࡧࡳࡦࡡࡤࡴࡵࡥࡡ࠲࠳ࡼࡣࡸࡩࡲࡪࡲࡷࠫ༣")):
            scripts = {bstack11ll1_opy_ (u"ࠬࡹࡣࡢࡰࠪ༤"): bstack1l11l111l1_opy_.perform_scan}
            thread_local.base_app_a11y_script = scripts
        bstack1lll1ll1l1_opy_ = copy.deepcopy(thread_local.base_app_a11y_script)
        bstack1lll1ll1l1_opy_[bstack11ll1_opy_ (u"࠭ࡳࡤࡣࡱࠫ༥")] = bstack1lll1ll1l1_opy_[bstack11ll1_opy_ (u"ࠧࡴࡥࡤࡲࠬ༦")] % json.dumps(bstack11l11l11l1_opy_)
        bstack1l11l111l1_opy_.bstack111l1ll1l_opy_(bstack1lll1ll1l1_opy_)
        bstack1l11l111l1_opy_.store()
        bstack1lll1111l_opy_ = driver.execute_script(bstack1l11l111l1_opy_.perform_scan)
      except Exception as bstack1lll11l1ll_opy_:
        logger.info(bstack11ll1_opy_ (u"ࠣࡃࡳࡴ࡮ࡻ࡭ࠡࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠡࡵࡦࡥࡳࠦࡦࡢ࡫࡯ࡩࡩࡀࠠࠣ༧") + str(bstack1lll11l1ll_opy_))
        bstack1lll1111l_opy_ = {bstack11ll1_opy_ (u"ࠤࡨࡶࡷࡵࡲࠣ༨"): str(bstack1lll11l1ll_opy_)}
    else:
      bstack1lll1111l_opy_ = driver.execute_async_script(bstack1l11l111l1_opy_.perform_scan, {bstack11ll1_opy_ (u"ࠪࡱࡪࡺࡨࡰࡦࠪ༩"): kwargs.get(bstack11ll1_opy_ (u"ࠫࡩࡸࡩࡷࡧࡵࡣࡨࡵ࡭࡮ࡣࡱࡨࠬ༪"), None) or bstack11ll1_opy_ (u"ࠬ࠭༫")})
    return bstack1lll1111l_opy_
  except Exception as err:
    logger.error(bstack11ll1_opy_ (u"ࠨࡕ࡯ࡣࡥࡰࡪࠦࡴࡰࠢࡵࡹࡳࠦࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࠦࡳࡤࡣࡱ࠲ࠥࢁࡽࠣ༬").format(str(err)))
    return {}