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
import sys
import logging
import tarfile
import io
import os
import time
import requests
import re
import threading
from requests_toolbelt.multipart.encoder import MultipartEncoder
from bstack_utils.constants import bstack11l1l1ll111_opy_, bstack11l1l11l11l_opy_, bstack11l11ll11ll_opy_
import tempfile
import json
bstack111l11l11l1_opy_ = os.getenv(bstack11ll1_opy_ (u"ࠨࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡒࡏࡈࡡࡉࡍࡑࡋࠢṧ"), None) or os.path.join(tempfile.gettempdir(), bstack11ll1_opy_ (u"ࠢࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡤࡦࡤࡸ࡫࠳ࡲ࡯ࡨࠤṨ"))
bstack111l1111lll_opy_ = os.path.join(bstack11ll1_opy_ (u"ࠣ࡮ࡲ࡫ࠧṩ"), bstack11ll1_opy_ (u"ࠩࡶࡨࡰ࠳ࡣ࡭࡫࠰ࡨࡪࡨࡵࡨ࠰࡯ࡳ࡬࠭Ṫ"))
_1111llll1ll_opy_ = threading.Lock()
logging.Formatter.converter = time.gmtime
def get_logger(name=__name__, level=None):
  logger = logging.getLogger(name)
  if level:
    logging.basicConfig(
      level=level,
      format=bstack11ll1_opy_ (u"ࠪࠩ࠭ࡧࡳࡤࡶ࡬ࡱࡪ࠯ࡳࠡ࡝ࠨࠬࡳࡧ࡭ࡦࠫࡶࡡࡠࠫࠨ࡭ࡧࡹࡩࡱࡴࡡ࡮ࡧࠬࡷࡢࠦ࠭ࠡࠧࠫࡱࡪࡹࡳࡢࡩࡨ࠭ࡸ࠭ṫ"),
      datefmt=bstack11ll1_opy_ (u"ࠫࠪ࡟࠭ࠦ࡯࠰ࠩࡩ࡚ࠥࡉ࠼ࠨࡑ࠿ࠫࡓ࡛ࠩṬ"),
      stream=sys.stdout
    )
  return logger
def bstack1l1l111l_opy_(name=__name__, level=logging.DEBUG):
  bstack11ll1_opy_ (u"ࠧࠨࠢࠋࠢࠣࡖࡪࡺࡵࡳࡰࡶࠤࡦࠦ࡬ࡰࡩࡪࡩࡷࠦࡴࡩࡣࡷࠤࡼࡸࡩࡵࡧࡶࠤࡴࡴ࡬ࡺࠢࡷࡳࠥࡧࡵࡵࡱࡰࡥࡹ࡯࡯࡯࠰࡯ࡳ࡬ࠦࡦࡪ࡮ࡨࠎࠥࠦࡃࡳࡧࡤࡸࡪࡹࠠࡢࡰࡧࠤࡲࡧ࡮ࡢࡩࡨࡷࠥ࡯ࡴࡴࠢࡲࡻࡳࠦࡡࡶࡶࡲࡱࡦࡺࡩࡰࡰࠣࡪ࡮ࡲࡥࠡࡪࡤࡲࡩࡲࡥࡳࠌࠣࠤࡔࡴ࡬ࡺࠢࡨࡲࡦࡨ࡬ࡦࡵࠣࡰࡴ࡭ࡧࡪࡰࡪࠤ࡮࡬ࠠࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡁࡖࡖࡒࡑࡆ࡚ࡉࡐࡐࡢࡐࡔࡍࡓࠡࡧࡱࡺ࡮ࡸ࡯࡯࡯ࡨࡲࡹࠦࡶࡢࡴ࡬ࡥࡧࡲࡥࠡ࡫ࡶࠤࡸ࡫ࡴࠡࡶࡲࠤࡦࠦࡴࡳࡷࡷ࡬ࡾࠦࡶࡢ࡮ࡸࡩࠏࠦࠠࡂࡴࡪࡷ࠿ࠐࠠࠡࠢࠣࡲࡦࡳࡥ࠻ࠢࡏࡳ࡬࡭ࡥࡳࠢࡱࡥࡲ࡫ࠠࠩࡦࡨࡪࡦࡻ࡬ࡵࡵࠣࡸࡴࠦ࡟ࡠࡰࡤࡱࡪࡥ࡟ࠪࠌࠣࠤࠥࠦ࡬ࡦࡸࡨࡰ࠿ࠦࡌࡰࡩࡪ࡭ࡳ࡭ࠠ࡭ࡧࡹࡩࡱࠦࠨࡥࡧࡩࡥࡺࡲࡴࡴࠢࡷࡳࠥࡊࡅࡃࡗࡊ࠭ࠏࠦࠠࡓࡧࡷࡹࡷࡴࡳ࠻ࠌࠣࠤࠥࠦ࡬ࡰࡩࡪ࡭ࡳ࡭࠮ࡍࡱࡪ࡫ࡪࡸ࠺ࠡࡅࡲࡲ࡫࡯ࡧࡶࡴࡨࡨࠥࡲ࡯ࡨࡩࡨࡶࠥࡺࡨࡢࡶࠣࡻࡷ࡯ࡴࡦࡵࠣࡳࡳࡲࡹࠡࡶࡲࠤࡦࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮࠯࡮ࡲ࡫ࠥ࠮ࡩࡧࠢࡨࡲࡦࡨ࡬ࡦࡦࠬࠎࠥࠦࠢࠣࠤṭ")
  logger_name = bstack11ll1_opy_ (u"ࠨࡡࡶࡶࡲࡱࡦࡺࡩࡰࡰ࠱ࡿ࠵ࢃࠢṮ").format(name)
  logger = logging.getLogger(logger_name)
  is_enabled = os.getenv(bstack11ll1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡁࡖࡖࡒࡑࡆ࡚ࡉࡐࡐࡢࡐࡔࡍࡓࠨṯ"), bstack11ll1_opy_ (u"ࠨࠩṰ")).lower() == bstack11ll1_opy_ (u"ࠩࡷࡶࡺ࡫ࠧṱ")
  if not is_enabled:
    logger.setLevel(logging.CRITICAL)
    logger.propagate = False
    return logger
  with _1111llll1ll_opy_:
    if logger.handlers:
      return logger
    bstack111l111l111_opy_ = os.path.join(os.getcwd(), bstack11ll1_opy_ (u"ࠪࡰࡴ࡭ࠧṲ"), bstack11ll1_opy_ (u"ࠫࡦࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮࠯࡮ࡲ࡫ࠬṳ"))
    log_dir = os.path.dirname(bstack111l111l111_opy_)
    if not os.path.exists(log_dir):
      os.makedirs(log_dir)
    bstack1111llll111_opy_ = logging.FileHandler(bstack111l111l111_opy_)
    bstack111l11l1111_opy_ = logging.Formatter(
      fmt=bstack11ll1_opy_ (u"ࠬࠫࠨࡢࡵࡦࡸ࡮ࡳࡥࠪࡵࠣ࡟ࠪ࠮࡮ࡢ࡯ࡨ࠭ࡸࡣ࡛ࠦࠪ࡯ࡩࡻ࡫࡬࡯ࡣࡰࡩ࠮ࡹ࡝ࠡ࠯ࠣ࡟࡙ࠥࡄࡌ࠯ࡄ࡙࡙ࡕࡍࡂࡖࡌࡓࡓࠦ࡝ࠡࠧࠫࡱࡪࡹࡳࡢࡩࡨ࠭ࡸ࠭Ṵ"),
      datefmt=bstack11ll1_opy_ (u"࡚࠭ࠥ࠯ࠨࡱ࠲ࠫࡤࡕࠧࡋ࠾ࠪࡓ࠺ࠦࡕ࡝ࠫṵ"),
    )
    bstack1111llll111_opy_.setFormatter(bstack111l11l1111_opy_)
    bstack1111llll111_opy_.setLevel(level)
    bstack1111llll111_opy_.addFilter(lambda r: r.name != bstack11ll1_opy_ (u"ࠧࡴࡧ࡯ࡩࡳ࡯ࡵ࡮࠰ࡺࡩࡧࡪࡲࡪࡸࡨࡶ࠳ࡸࡥ࡮ࡱࡷࡩ࠳ࡸࡥ࡮ࡱࡷࡩࡤࡩ࡯࡯ࡰࡨࡧࡹ࡯࡯࡯ࠩṶ"))
    logger.addHandler(bstack1111llll111_opy_)
    logger.setLevel(level)
    logger.propagate = False
  return logger
def bstack1l1ll1l1111_opy_():
  bstack111l1111l11_opy_ = os.environ.get(bstack11ll1_opy_ (u"ࠣࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡃࡋࡑࡅࡗ࡟࡟ࡅࡇࡅ࡙ࡌࠨṷ"), bstack11ll1_opy_ (u"ࠤࡩࡥࡱࡹࡥࠣṸ"))
  return logging.DEBUG if bstack111l1111l11_opy_.lower() == bstack11ll1_opy_ (u"ࠥࡸࡷࡻࡥࠣṹ") else logging.INFO
def bstack1lll11l1l11_opy_():
  global bstack111l11l11l1_opy_
  if os.path.exists(bstack111l11l11l1_opy_):
    os.remove(bstack111l11l11l1_opy_)
  if os.path.exists(bstack111l1111lll_opy_):
    os.remove(bstack111l1111lll_opy_)
def bstack11l111ll11_opy_():
  for handler in logging.getLogger().handlers:
    logging.getLogger().removeHandler(handler)
def configure_logger(config, log_level):
  bstack1111lllllll_opy_ = log_level
  if bstack11ll1_opy_ (u"ࠫࡱࡵࡧࡍࡧࡹࡩࡱ࠭Ṻ") in config and config[bstack11ll1_opy_ (u"ࠬࡲ࡯ࡨࡎࡨࡺࡪࡲࠧṻ")] in bstack11l1l11l11l_opy_:
    bstack1111lllllll_opy_ = bstack11l1l11l11l_opy_[config[bstack11ll1_opy_ (u"࠭࡬ࡰࡩࡏࡩࡻ࡫࡬ࠨṼ")]]
  if config.get(bstack11ll1_opy_ (u"ࠧࡥ࡫ࡶࡥࡧࡲࡥࡂࡷࡷࡳࡈࡧࡰࡵࡷࡵࡩࡑࡵࡧࡴࠩṽ"), False):
    logging.getLogger().setLevel(bstack1111lllllll_opy_)
    return bstack1111lllllll_opy_
  global bstack111l11l11l1_opy_
  bstack11l111ll11_opy_()
  bstack1111lllll11_opy_ = logging.Formatter(
    fmt=bstack11ll1_opy_ (u"ࠨࠧࠫࡥࡸࡩࡴࡪ࡯ࡨ࠭ࡸ࡛ࠦࠦࠪࡱࡥࡲ࡫ࠩࡴ࡟࡞ࠩ࠭ࡲࡥࡷࡧ࡯ࡲࡦࡳࡥࠪࡵࡠࠤ࠲ࠦࠥࠩ࡯ࡨࡷࡸࡧࡧࡦࠫࡶࠫṾ"),
    datefmt=bstack11ll1_opy_ (u"ࠩࠨ࡝࠲ࠫ࡭࠮ࠧࡧࡘࠪࡎ࠺ࠦࡏ࠽ࠩࡘࡠࠧṿ"),
  )
  bstack111l11111ll_opy_ = logging.StreamHandler(sys.stdout)
  file_handler = logging.FileHandler(bstack111l11l11l1_opy_)
  file_handler.setFormatter(bstack1111lllll11_opy_)
  bstack111l11111ll_opy_.setFormatter(bstack1111lllll11_opy_)
  file_handler.setLevel(logging.DEBUG)
  bstack111l11111ll_opy_.setLevel(log_level)
  file_handler.addFilter(lambda r: r.name != bstack11ll1_opy_ (u"ࠪࡷࡪࡲࡥ࡯࡫ࡸࡱ࠳ࡽࡥࡣࡦࡵ࡭ࡻ࡫ࡲ࠯ࡴࡨࡱࡴࡺࡥ࠯ࡴࡨࡱࡴࡺࡥࡠࡥࡲࡲࡳ࡫ࡣࡵ࡫ࡲࡲࠬẀ"))
  logging.getLogger().setLevel(logging.DEBUG)
  bstack111l11111ll_opy_.setLevel(bstack1111lllllll_opy_)
  logging.getLogger().addHandler(bstack111l11111ll_opy_)
  logging.getLogger().addHandler(file_handler)
  return bstack1111lllllll_opy_
def bstack111l11l111l_opy_(config):
  try:
    bstack111l11111l1_opy_ = set(bstack11l11ll11ll_opy_)
    bstack111l111l11l_opy_ = bstack11ll1_opy_ (u"ࠫࠬẁ")
    with open(bstack11ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡾࡳ࡬ࠨẂ")) as bstack1111lll1lll_opy_:
      bstack111l111ll1l_opy_ = bstack1111lll1lll_opy_.read()
      bstack111l111l11l_opy_ = re.sub(bstack11ll1_opy_ (u"ࡸࠧ࡟ࠪ࡟ࡷ࠰࠯࠿ࠤ࠰࠭ࠨࡡࡴࠧẃ"), bstack11ll1_opy_ (u"ࠧࠨẄ"), bstack111l111ll1l_opy_, flags=re.M)
      bstack111l111l11l_opy_ = re.sub(
        bstack11ll1_opy_ (u"ࡳࠩࡡࠬࡡࡹࠫࠪࡁࠫࠫẅ") + bstack11ll1_opy_ (u"ࠩࡿࠫẆ").join(bstack111l11111l1_opy_) + bstack11ll1_opy_ (u"ࠪ࠭࠳࠰ࠤࠨẇ"),
        bstack11ll1_opy_ (u"ࡶࠬࡢ࠲࠻ࠢ࡞ࡖࡊࡊࡁࡄࡖࡈࡈࡢ࠭Ẉ"),
        bstack111l111l11l_opy_, flags=re.M | re.I
      )
    def bstack111l111lll1_opy_(dic):
      bstack111l1111111_opy_ = {}
      for key, value in dic.items():
        if key in bstack111l11111l1_opy_:
          bstack111l1111111_opy_[key] = bstack11ll1_opy_ (u"ࠬࡡࡒࡆࡆࡄࡇ࡙ࡋࡄ࡞ࠩẉ")
        else:
          if isinstance(value, dict):
            bstack111l1111111_opy_[key] = bstack111l111lll1_opy_(value)
          else:
            bstack111l1111111_opy_[key] = value
      return bstack111l1111111_opy_
    bstack111l1111111_opy_ = bstack111l111lll1_opy_(config)
    return {
      bstack11ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡿ࡭࡭ࠩẊ"): bstack111l111l11l_opy_,
      bstack11ll1_opy_ (u"ࠧࡧ࡫ࡱࡥࡱࡩ࡯࡯ࡨ࡬࡫࠳ࡰࡳࡰࡰࠪẋ"): json.dumps(bstack111l1111111_opy_)
    }
  except Exception as e:
    return {}
def bstack111l111111l_opy_(inipath, rootpath):
  log_dir = os.path.join(os.getcwd(), bstack11ll1_opy_ (u"ࠨ࡮ࡲ࡫ࠬẌ"))
  if not os.path.exists(log_dir):
    os.makedirs(log_dir)
  bstack111l111l1l1_opy_ = os.path.join(log_dir, bstack11ll1_opy_ (u"ࠩࡳࡽࡹ࡫ࡳࡵࡡࡦࡳࡳ࡬ࡩࡨࡵࠪẍ"))
  if not os.path.exists(bstack111l111l1l1_opy_):
    bstack1111llll1l1_opy_ = {
      bstack11ll1_opy_ (u"ࠥ࡭ࡳ࡯ࡰࡢࡶ࡫ࠦẎ"): str(inipath),
      bstack11ll1_opy_ (u"ࠦࡷࡵ࡯ࡵࡲࡤࡸ࡭ࠨẏ"): str(rootpath)
    }
    with open(os.path.join(log_dir, bstack11ll1_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸࡤࡩ࡯࡯ࡨ࡬࡫ࡸ࠴ࡪࡴࡱࡱࠫẐ")), bstack11ll1_opy_ (u"࠭ࡷࠨẑ")) as bstack111l1111ll1_opy_:
      bstack111l1111ll1_opy_.write(json.dumps(bstack1111llll1l1_opy_))
def bstack111l111l1ll_opy_():
  try:
    bstack111l111l1l1_opy_ = os.path.join(os.getcwd(), bstack11ll1_opy_ (u"ࠧ࡭ࡱࡪࠫẒ"), bstack11ll1_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࡠࡥࡲࡲ࡫࡯ࡧࡴ࠰࡭ࡷࡴࡴࠧẓ"))
    if os.path.exists(bstack111l111l1l1_opy_):
      with open(bstack111l111l1l1_opy_, bstack11ll1_opy_ (u"ࠩࡵࠫẔ")) as bstack111l1111ll1_opy_:
        bstack111l111ll11_opy_ = json.load(bstack111l1111ll1_opy_)
      return bstack111l111ll11_opy_.get(bstack11ll1_opy_ (u"ࠪ࡭ࡳ࡯ࡰࡢࡶ࡫ࠫẕ"), bstack11ll1_opy_ (u"ࠫࠬẖ")), bstack111l111ll11_opy_.get(bstack11ll1_opy_ (u"ࠬࡸ࡯ࡰࡶࡳࡥࡹ࡮ࠧẗ"), bstack11ll1_opy_ (u"࠭ࠧẘ"))
  except:
    pass
  return None, None
def bstack111l111llll_opy_():
  try:
    bstack111l111l1l1_opy_ = os.path.join(os.getcwd(), bstack11ll1_opy_ (u"ࠧ࡭ࡱࡪࠫẙ"), bstack11ll1_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࡠࡥࡲࡲ࡫࡯ࡧࡴ࠰࡭ࡷࡴࡴࠧẚ"))
    if os.path.exists(bstack111l111l1l1_opy_):
      os.remove(bstack111l111l1l1_opy_)
  except:
    pass
def bstack1l1l11l11l_opy_(config):
  try:
    from bstack_utils.helper import bstack1l1l1ll1l_opy_, bstack1ll1l111_opy_
    from browserstack_sdk.sdk_cli.cli import cli
    global bstack111l11l11l1_opy_
    if config.get(bstack11ll1_opy_ (u"ࠩࡧ࡭ࡸࡧࡢ࡭ࡧࡄࡹࡹࡵࡃࡢࡲࡷࡹࡷ࡫ࡌࡰࡩࡶࠫẛ"), False):
      return
    uuid = os.getenv(bstack11ll1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡉࡘ࡚ࡈࡖࡄࡢ࡙࡚ࡏࡄࠨẜ")) if os.getenv(bstack11ll1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡉࡗࡅࡣ࡚࡛ࡉࡅࠩẝ")) else bstack1l1l1ll1l_opy_.get_property(bstack11ll1_opy_ (u"ࠧࡹࡤ࡬ࡔࡸࡲࡎࡪࠢẞ"))
    if not uuid or uuid == bstack11ll1_opy_ (u"࠭࡮ࡶ࡮࡯ࠫẟ"):
      return
    bstack1111lllll1l_opy_ = [bstack11ll1_opy_ (u"ࠧࡳࡧࡴࡹ࡮ࡸࡥ࡮ࡧࡱࡸࡸ࠴ࡴࡹࡶࠪẠ"), bstack11ll1_opy_ (u"ࠨࡒ࡬ࡴ࡫࡯࡬ࡦࠩạ"), bstack11ll1_opy_ (u"ࠩࡳࡽࡵࡸ࡯࡫ࡧࡦࡸ࠳ࡺ࡯࡮࡮ࠪẢ"), bstack111l11l11l1_opy_, bstack111l1111lll_opy_]
    bstack1111llll11l_opy_, root_path = bstack111l111l1ll_opy_()
    if bstack1111llll11l_opy_ != None:
      bstack1111lllll1l_opy_.append(bstack1111llll11l_opy_)
    if root_path != None:
      bstack1111lllll1l_opy_.append(os.path.join(root_path, bstack11ll1_opy_ (u"ࠪࡧࡴࡴࡦࡵࡧࡶࡸ࠳ࡶࡹࠨả")))
    bstack11l111ll11_opy_()
    logging.shutdown()
    output_file = os.path.join(tempfile.gettempdir(), bstack11ll1_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮࠱ࡱࡵࡧࡴ࠯ࠪẤ") + uuid + bstack11ll1_opy_ (u"ࠬ࠴ࡴࡢࡴ࠱࡫ࡿ࠭ấ"))
    with tarfile.open(output_file, bstack11ll1_opy_ (u"ࠨࡷ࠻ࡩࡽࠦẦ")) as archive:
      for file in filter(lambda f: os.path.exists(f), bstack1111lllll1l_opy_):
        try:
          archive.add(file,  arcname=os.path.basename(file))
        except:
          pass
      for name, data in bstack111l11l111l_opy_(config).items():
        tarinfo = tarfile.TarInfo(name)
        bstack1111llllll1_opy_ = data.encode()
        tarinfo.size = len(bstack1111llllll1_opy_)
        archive.addfile(tarinfo, io.BytesIO(bstack1111llllll1_opy_))
    bstack11l11l111l_opy_ = MultipartEncoder(
      fields= {
        bstack11ll1_opy_ (u"ࠧࡥࡣࡷࡥࠬầ"): (os.path.basename(output_file), open(os.path.abspath(output_file), bstack11ll1_opy_ (u"ࠨࡴࡥࠫẨ")), bstack11ll1_opy_ (u"ࠩࡤࡴࡵࡲࡩࡤࡣࡷ࡭ࡴࡴ࠯ࡹ࠯ࡪࡾ࡮ࡶࠧẩ")),
        bstack11ll1_opy_ (u"ࠪࡧࡱ࡯ࡥ࡯ࡶࡅࡹ࡮ࡲࡤࡖࡷ࡬ࡨࠬẪ"): uuid
      }
    )
    bstack111l1111l1l_opy_ = bstack1ll1l111_opy_(cli.config, [bstack11ll1_opy_ (u"ࠦࡦࡶࡩࡴࠤẫ"), bstack11ll1_opy_ (u"ࠧࡵࡢࡴࡧࡵࡺࡦࡨࡩ࡭࡫ࡷࡽࠧẬ"), bstack11ll1_opy_ (u"ࠨࡵࡱ࡮ࡲࡥࡩࠨậ")], bstack11l1l1ll111_opy_)
    response = requests.post(
      bstack11ll1_opy_ (u"ࠢࡼࡿ࠲ࡧࡱ࡯ࡥ࡯ࡶ࠰ࡰࡴ࡭ࡳ࠰ࡷࡳࡰࡴࡧࡤࠣẮ").format(bstack111l1111l1l_opy_),
      data=bstack11l11l111l_opy_,
      headers={bstack11ll1_opy_ (u"ࠨࡅࡲࡲࡹ࡫࡮ࡵ࠯ࡗࡽࡵ࡫ࠧắ"): bstack11l11l111l_opy_.content_type},
      auth=(config[bstack11ll1_opy_ (u"ࠩࡸࡷࡪࡸࡎࡢ࡯ࡨࠫẰ")], config[bstack11ll1_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵࡎࡩࡾ࠭ằ")])
    )
    os.remove(output_file)
    if response.status_code != 200:
      get_logger().debug(bstack11ll1_opy_ (u"ࠫࡊࡸࡲࡰࡴࠣࡹࡵࡲ࡯ࡢࡦࠣࡰࡴ࡭ࡳ࠻ࠢࠪẲ") + response.status_code)
  except Exception as e:
    get_logger().debug(bstack11ll1_opy_ (u"ࠬࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡ࡫ࡱࠤࡸ࡫࡮ࡥ࡫ࡱ࡫ࠥࡲ࡯ࡨࡵ࠽ࠫẳ") + str(e))
  finally:
    try:
      bstack1lll11l1l11_opy_()
      bstack111l111llll_opy_()
    except:
      pass