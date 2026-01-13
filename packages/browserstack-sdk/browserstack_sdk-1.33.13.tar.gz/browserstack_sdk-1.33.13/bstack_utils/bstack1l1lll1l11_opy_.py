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
from bstack_utils.constants import bstack11l1l11ll1l_opy_, bstack11l1l1l11l1_opy_, bstack11l1l1111l1_opy_
import tempfile
import json
bstack1111llll111_opy_ = os.getenv(bstack11l1l_opy_ (u"ࠧࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡑࡕࡇࡠࡈࡌࡐࡊࠨṦ"), None) or os.path.join(tempfile.gettempdir(), bstack11l1l_opy_ (u"ࠨࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡪࡥࡣࡷࡪ࠲ࡱࡵࡧࠣṧ"))
bstack1111llll1l1_opy_ = os.path.join(bstack11l1l_opy_ (u"ࠢ࡭ࡱࡪࠦṨ"), bstack11l1l_opy_ (u"ࠨࡵࡧ࡯࠲ࡩ࡬ࡪ࠯ࡧࡩࡧࡻࡧ࠯࡮ࡲ࡫ࠬṩ"))
_1111lllll11_opy_ = threading.Lock()
logging.Formatter.converter = time.gmtime
def get_logger(name=__name__, level=None):
  logger = logging.getLogger(name)
  if level:
    logging.basicConfig(
      level=level,
      format=bstack11l1l_opy_ (u"ࠩࠨࠬࡦࡹࡣࡵ࡫ࡰࡩ࠮ࡹࠠ࡜ࠧࠫࡲࡦࡳࡥࠪࡵࡠ࡟ࠪ࠮࡬ࡦࡸࡨࡰࡳࡧ࡭ࡦࠫࡶࡡࠥ࠳ࠠࠦࠪࡰࡩࡸࡹࡡࡨࡧࠬࡷࠬṪ"),
      datefmt=bstack11l1l_opy_ (u"ࠪࠩ࡞࠳ࠥ࡮࠯ࠨࡨ࡙ࠫࡈ࠻ࠧࡐ࠾࡙࡚ࠪࠨṫ"),
      stream=sys.stdout
    )
  return logger
def bstack1l111111_opy_(name=__name__, level=logging.DEBUG):
  bstack11l1l_opy_ (u"ࠦࠧࠨࠊࠡࠢࡕࡩࡹࡻࡲ࡯ࡵࠣࡥࠥࡲ࡯ࡨࡩࡨࡶࠥࡺࡨࡢࡶࠣࡻࡷ࡯ࡴࡦࡵࠣࡳࡳࡲࡹࠡࡶࡲࠤࡦࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮࠯࡮ࡲ࡫ࠥ࡬ࡩ࡭ࡧࠍࠤࠥࡉࡲࡦࡣࡷࡩࡸࠦࡡ࡯ࡦࠣࡱࡦࡴࡡࡨࡧࡶࠤ࡮ࡺࡳࠡࡱࡺࡲࠥࡧࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࠢࡩ࡭ࡱ࡫ࠠࡩࡣࡱࡨࡱ࡫ࡲࠋࠢࠣࡓࡳࡲࡹࠡࡧࡱࡥࡧࡲࡥࡴࠢ࡯ࡳ࡬࡭ࡩ࡯ࡩࠣ࡭࡫ࠦࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡇࡕࡕࡑࡐࡅ࡙ࡏࡏࡏࡡࡏࡓࡌ࡙ࠠࡦࡰࡹ࡭ࡷࡵ࡮࡮ࡧࡱࡸࠥࡼࡡࡳ࡫ࡤࡦࡱ࡫ࠠࡪࡵࠣࡷࡪࡺࠠࡵࡱࠣࡥࠥࡺࡲࡶࡶ࡫ࡽࠥࡼࡡ࡭ࡷࡨࠎࠥࠦࡁࡳࡩࡶ࠾ࠏࠦࠠࠡࠢࡱࡥࡲ࡫࠺ࠡࡎࡲ࡫࡬࡫ࡲࠡࡰࡤࡱࡪࠦࠨࡥࡧࡩࡥࡺࡲࡴࡴࠢࡷࡳࠥࡥ࡟࡯ࡣࡰࡩࡤࡥࠩࠋࠢࠣࠤࠥࡲࡥࡷࡧ࡯࠾ࠥࡒ࡯ࡨࡩ࡬ࡲ࡬ࠦ࡬ࡦࡸࡨࡰࠥ࠮ࡤࡦࡨࡤࡹࡱࡺࡳࠡࡶࡲࠤࡉࡋࡂࡖࡉࠬࠎࠥࠦࡒࡦࡶࡸࡶࡳࡹ࠺ࠋࠢࠣࠤࠥࡲ࡯ࡨࡩ࡬ࡲ࡬࠴ࡌࡰࡩࡪࡩࡷࡀࠠࡄࡱࡱࡪ࡮࡭ࡵࡳࡧࡧࠤࡱࡵࡧࡨࡧࡵࠤࡹ࡮ࡡࡵࠢࡺࡶ࡮ࡺࡥࡴࠢࡲࡲࡱࡿࠠࡵࡱࠣࡥࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴ࠮࡭ࡱࡪࠤ࠭࡯ࡦࠡࡧࡱࡥࡧࡲࡥࡥࠫࠍࠤࠥࠨࠢࠣṬ")
  logger_name = bstack11l1l_opy_ (u"ࠧࡧࡵࡵࡱࡰࡥࡹ࡯࡯࡯࠰ࡾ࠴ࢂࠨṭ").format(name)
  logger = logging.getLogger(logger_name)
  is_enabled = os.getenv(bstack11l1l_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡇࡕࡕࡑࡐࡅ࡙ࡏࡏࡏࡡࡏࡓࡌ࡙ࠧṮ"), bstack11l1l_opy_ (u"ࠧࠨṯ")).lower() == bstack11l1l_opy_ (u"ࠨࡶࡵࡹࡪ࠭Ṱ")
  if not is_enabled:
    logger.setLevel(logging.CRITICAL)
    logger.propagate = False
    return logger
  with _1111lllll11_opy_:
    if logger.handlers:
      return logger
    bstack111l111l1ll_opy_ = os.path.join(os.getcwd(), bstack11l1l_opy_ (u"ࠩ࡯ࡳ࡬࠭ṱ"), bstack11l1l_opy_ (u"ࠪࡥࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴ࠮࡭ࡱࡪࠫṲ"))
    log_dir = os.path.dirname(bstack111l111l1ll_opy_)
    if not os.path.exists(log_dir):
      os.makedirs(log_dir)
    bstack111l111llll_opy_ = logging.FileHandler(bstack111l111l1ll_opy_)
    bstack1111llllll1_opy_ = logging.Formatter(
      fmt=bstack11l1l_opy_ (u"ࠫࠪ࠮ࡡࡴࡥࡷ࡭ࡲ࡫ࠩࡴࠢ࡞ࠩ࠭ࡴࡡ࡮ࡧࠬࡷࡢࡡࠥࠩ࡮ࡨࡺࡪࡲ࡮ࡢ࡯ࡨ࠭ࡸࡣࠠ࠮ࠢ࡞ࠤࡘࡊࡋ࠮ࡃࡘࡘࡔࡓࡁࡕࡋࡒࡒࠥࡣࠠࠦࠪࡰࡩࡸࡹࡡࡨࡧࠬࡷࠬṳ"),
      datefmt=bstack11l1l_opy_ (u"࡙ࠬࠫ࠮ࠧࡰ࠱ࠪࡪࡔࠦࡊ࠽ࠩࡒࡀࠥࡔ࡜ࠪṴ"),
    )
    bstack111l111llll_opy_.setFormatter(bstack1111llllll1_opy_)
    bstack111l111llll_opy_.setLevel(level)
    bstack111l111llll_opy_.addFilter(lambda r: r.name != bstack11l1l_opy_ (u"࠭ࡳࡦ࡮ࡨࡲ࡮ࡻ࡭࠯ࡹࡨࡦࡩࡸࡩࡷࡧࡵ࠲ࡷ࡫࡭ࡰࡶࡨ࠲ࡷ࡫࡭ࡰࡶࡨࡣࡨࡵ࡮࡯ࡧࡦࡸ࡮ࡵ࡮ࠨṵ"))
    logger.addHandler(bstack111l111llll_opy_)
    logger.setLevel(level)
    logger.propagate = False
  return logger
def bstack1ll1lll1lll_opy_():
  bstack111l111lll1_opy_ = os.environ.get(bstack11l1l_opy_ (u"ࠢࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡂࡊࡐࡄࡖ࡞ࡥࡄࡆࡄࡘࡋࠧṶ"), bstack11l1l_opy_ (u"ࠣࡨࡤࡰࡸ࡫ࠢṷ"))
  return logging.DEBUG if bstack111l111lll1_opy_.lower() == bstack11l1l_opy_ (u"ࠤࡷࡶࡺ࡫ࠢṸ") else logging.INFO
def bstack1l1l1l11lll_opy_():
  global bstack1111llll111_opy_
  if os.path.exists(bstack1111llll111_opy_):
    os.remove(bstack1111llll111_opy_)
  if os.path.exists(bstack1111llll1l1_opy_):
    os.remove(bstack1111llll1l1_opy_)
def bstack1l11l11ll1_opy_():
  for handler in logging.getLogger().handlers:
    logging.getLogger().removeHandler(handler)
def configure_logger(config, log_level):
  bstack111l111ll11_opy_ = log_level
  if bstack11l1l_opy_ (u"ࠪࡰࡴ࡭ࡌࡦࡸࡨࡰࠬṹ") in config and config[bstack11l1l_opy_ (u"ࠫࡱࡵࡧࡍࡧࡹࡩࡱ࠭Ṻ")] in bstack11l1l1l11l1_opy_:
    bstack111l111ll11_opy_ = bstack11l1l1l11l1_opy_[config[bstack11l1l_opy_ (u"ࠬࡲ࡯ࡨࡎࡨࡺࡪࡲࠧṻ")]]
  if config.get(bstack11l1l_opy_ (u"࠭ࡤࡪࡵࡤࡦࡱ࡫ࡁࡶࡶࡲࡇࡦࡶࡴࡶࡴࡨࡐࡴ࡭ࡳࠨṼ"), False):
    logging.getLogger().setLevel(bstack111l111ll11_opy_)
    return bstack111l111ll11_opy_
  global bstack1111llll111_opy_
  bstack1l11l11ll1_opy_()
  bstack111l111l11l_opy_ = logging.Formatter(
    fmt=bstack11l1l_opy_ (u"ࠧࠦࠪࡤࡷࡨࡺࡩ࡮ࡧࠬࡷࠥࡡࠥࠩࡰࡤࡱࡪ࠯ࡳ࡞࡝ࠨࠬࡱ࡫ࡶࡦ࡮ࡱࡥࡲ࡫ࠩࡴ࡟ࠣ࠱ࠥࠫࠨ࡮ࡧࡶࡷࡦ࡭ࡥࠪࡵࠪṽ"),
    datefmt=bstack11l1l_opy_ (u"ࠨࠧ࡜࠱ࠪࡳ࠭ࠦࡦࡗࠩࡍࡀࠥࡎ࠼ࠨࡗ࡟࠭Ṿ"),
  )
  bstack1111llll1ll_opy_ = logging.StreamHandler(sys.stdout)
  file_handler = logging.FileHandler(bstack1111llll111_opy_)
  file_handler.setFormatter(bstack111l111l11l_opy_)
  bstack1111llll1ll_opy_.setFormatter(bstack111l111l11l_opy_)
  file_handler.setLevel(logging.DEBUG)
  bstack1111llll1ll_opy_.setLevel(log_level)
  file_handler.addFilter(lambda r: r.name != bstack11l1l_opy_ (u"ࠩࡶࡩࡱ࡫࡮ࡪࡷࡰ࠲ࡼ࡫ࡢࡥࡴ࡬ࡺࡪࡸ࠮ࡳࡧࡰࡳࡹ࡫࠮ࡳࡧࡰࡳࡹ࡫࡟ࡤࡱࡱࡲࡪࡩࡴࡪࡱࡱࠫṿ"))
  logging.getLogger().setLevel(logging.DEBUG)
  bstack1111llll1ll_opy_.setLevel(bstack111l111ll11_opy_)
  logging.getLogger().addHandler(bstack1111llll1ll_opy_)
  logging.getLogger().addHandler(file_handler)
  return bstack111l111ll11_opy_
def bstack111l11l111l_opy_(config):
  try:
    bstack111l11l11l1_opy_ = set(bstack11l1l1111l1_opy_)
    bstack111l1111l1l_opy_ = bstack11l1l_opy_ (u"ࠪࠫẀ")
    with open(bstack11l1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡽࡲࡲࠧẁ")) as bstack1111lll1lll_opy_:
      bstack111l11111ll_opy_ = bstack1111lll1lll_opy_.read()
      bstack111l1111l1l_opy_ = re.sub(bstack11l1l_opy_ (u"ࡷ࠭࡞ࠩ࡞ࡶ࠯࠮ࡅࠣ࠯ࠬࠧࡠࡳ࠭Ẃ"), bstack11l1l_opy_ (u"࠭ࠧẃ"), bstack111l11111ll_opy_, flags=re.M)
      bstack111l1111l1l_opy_ = re.sub(
        bstack11l1l_opy_ (u"ࡲࠨࡠࠫࡠࡸ࠱ࠩࡀࠪࠪẄ") + bstack11l1l_opy_ (u"ࠨࡾࠪẅ").join(bstack111l11l11l1_opy_) + bstack11l1l_opy_ (u"ࠩࠬ࠲࠯ࠪࠧẆ"),
        bstack11l1l_opy_ (u"ࡵࠫࡡ࠸࠺ࠡ࡝ࡕࡉࡉࡇࡃࡕࡇࡇࡡࠬẇ"),
        bstack111l1111l1l_opy_, flags=re.M | re.I
      )
    def bstack111l1111l11_opy_(dic):
      bstack111l111111l_opy_ = {}
      for key, value in dic.items():
        if key in bstack111l11l11l1_opy_:
          bstack111l111111l_opy_[key] = bstack11l1l_opy_ (u"ࠫࡠࡘࡅࡅࡃࡆࡘࡊࡊ࡝ࠨẈ")
        else:
          if isinstance(value, dict):
            bstack111l111111l_opy_[key] = bstack111l1111l11_opy_(value)
          else:
            bstack111l111111l_opy_[key] = value
      return bstack111l111111l_opy_
    bstack111l111111l_opy_ = bstack111l1111l11_opy_(config)
    return {
      bstack11l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡾࡳ࡬ࠨẉ"): bstack111l1111l1l_opy_,
      bstack11l1l_opy_ (u"࠭ࡦࡪࡰࡤࡰࡨࡵ࡮ࡧ࡫ࡪ࠲࡯ࡹ࡯࡯ࠩẊ"): json.dumps(bstack111l111111l_opy_)
    }
  except Exception as e:
    return {}
def bstack1111llll11l_opy_(inipath, rootpath):
  log_dir = os.path.join(os.getcwd(), bstack11l1l_opy_ (u"ࠧ࡭ࡱࡪࠫẋ"))
  if not os.path.exists(log_dir):
    os.makedirs(log_dir)
  bstack111l111ll1l_opy_ = os.path.join(log_dir, bstack11l1l_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࡠࡥࡲࡲ࡫࡯ࡧࡴࠩẌ"))
  if not os.path.exists(bstack111l111ll1l_opy_):
    bstack111l11111l1_opy_ = {
      bstack11l1l_opy_ (u"ࠤ࡬ࡲ࡮ࡶࡡࡵࡪࠥẍ"): str(inipath),
      bstack11l1l_opy_ (u"ࠥࡶࡴࡵࡴࡱࡣࡷ࡬ࠧẎ"): str(rootpath)
    }
    with open(os.path.join(log_dir, bstack11l1l_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࡣࡨࡵ࡮ࡧ࡫ࡪࡷ࠳ࡰࡳࡰࡰࠪẏ")), bstack11l1l_opy_ (u"ࠬࡽࠧẐ")) as bstack111l1111111_opy_:
      bstack111l1111111_opy_.write(json.dumps(bstack111l11111l1_opy_))
def bstack111l11l1111_opy_():
  try:
    bstack111l111ll1l_opy_ = os.path.join(os.getcwd(), bstack11l1l_opy_ (u"࠭࡬ࡰࡩࠪẑ"), bstack11l1l_opy_ (u"ࠧࡱࡻࡷࡩࡸࡺ࡟ࡤࡱࡱࡪ࡮࡭ࡳ࠯࡬ࡶࡳࡳ࠭Ẓ"))
    if os.path.exists(bstack111l111ll1l_opy_):
      with open(bstack111l111ll1l_opy_, bstack11l1l_opy_ (u"ࠨࡴࠪẓ")) as bstack111l1111111_opy_:
        bstack111l111l111_opy_ = json.load(bstack111l1111111_opy_)
      return bstack111l111l111_opy_.get(bstack11l1l_opy_ (u"ࠩ࡬ࡲ࡮ࡶࡡࡵࡪࠪẔ"), bstack11l1l_opy_ (u"ࠪࠫẕ")), bstack111l111l111_opy_.get(bstack11l1l_opy_ (u"ࠫࡷࡵ࡯ࡵࡲࡤࡸ࡭࠭ẖ"), bstack11l1l_opy_ (u"ࠬ࠭ẗ"))
  except:
    pass
  return None, None
def bstack1111lllllll_opy_():
  try:
    bstack111l111ll1l_opy_ = os.path.join(os.getcwd(), bstack11l1l_opy_ (u"࠭࡬ࡰࡩࠪẘ"), bstack11l1l_opy_ (u"ࠧࡱࡻࡷࡩࡸࡺ࡟ࡤࡱࡱࡪ࡮࡭ࡳ࠯࡬ࡶࡳࡳ࠭ẙ"))
    if os.path.exists(bstack111l111ll1l_opy_):
      os.remove(bstack111l111ll1l_opy_)
  except:
    pass
def bstack11lllll1l_opy_(config):
  try:
    from bstack_utils.helper import bstack1l1ll11111_opy_, bstack1l1l1ll1l_opy_
    from browserstack_sdk.sdk_cli.cli import cli
    global bstack1111llll111_opy_
    if config.get(bstack11l1l_opy_ (u"ࠨࡦ࡬ࡷࡦࡨ࡬ࡦࡃࡸࡸࡴࡉࡡࡱࡶࡸࡶࡪࡒ࡯ࡨࡵࠪẚ"), False):
      return
    uuid = os.getenv(bstack11l1l_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡘ࡙ࡎࡊࠧẛ")) if os.getenv(bstack11l1l_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡉࡘ࡚ࡈࡖࡄࡢ࡙࡚ࡏࡄࠨẜ")) else bstack1l1ll11111_opy_.get_property(bstack11l1l_opy_ (u"ࠦࡸࡪ࡫ࡓࡷࡱࡍࡩࠨẝ"))
    if not uuid or uuid == bstack11l1l_opy_ (u"ࠬࡴࡵ࡭࡮ࠪẞ"):
      return
    bstack111l1111lll_opy_ = [bstack11l1l_opy_ (u"࠭ࡲࡦࡳࡸ࡭ࡷ࡫࡭ࡦࡰࡷࡷ࠳ࡺࡸࡵࠩẟ"), bstack11l1l_opy_ (u"ࠧࡑ࡫ࡳࡪ࡮ࡲࡥࠨẠ"), bstack11l1l_opy_ (u"ࠨࡲࡼࡴࡷࡵࡪࡦࡥࡷ࠲ࡹࡵ࡭࡭ࠩạ"), bstack1111llll111_opy_, bstack1111llll1l1_opy_]
    bstack1111lllll1l_opy_, root_path = bstack111l11l1111_opy_()
    if bstack1111lllll1l_opy_ != None:
      bstack111l1111lll_opy_.append(bstack1111lllll1l_opy_)
    if root_path != None:
      bstack111l1111lll_opy_.append(os.path.join(root_path, bstack11l1l_opy_ (u"ࠩࡦࡳࡳ࡬ࡴࡦࡵࡷ࠲ࡵࡿࠧẢ")))
    bstack1l11l11ll1_opy_()
    logging.shutdown()
    output_file = os.path.join(tempfile.gettempdir(), bstack11l1l_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭࠰ࡰࡴ࡭ࡳ࠮ࠩả") + uuid + bstack11l1l_opy_ (u"ࠫ࠳ࡺࡡࡳ࠰ࡪࡾࠬẤ"))
    with tarfile.open(output_file, bstack11l1l_opy_ (u"ࠧࡽ࠺ࡨࡼࠥấ")) as archive:
      for file in filter(lambda f: os.path.exists(f), bstack111l1111lll_opy_):
        try:
          archive.add(file,  arcname=os.path.basename(file))
        except:
          pass
      for name, data in bstack111l11l111l_opy_(config).items():
        tarinfo = tarfile.TarInfo(name)
        bstack111l1111ll1_opy_ = data.encode()
        tarinfo.size = len(bstack111l1111ll1_opy_)
        archive.addfile(tarinfo, io.BytesIO(bstack111l1111ll1_opy_))
    bstack11l111l111_opy_ = MultipartEncoder(
      fields= {
        bstack11l1l_opy_ (u"࠭ࡤࡢࡶࡤࠫẦ"): (os.path.basename(output_file), open(os.path.abspath(output_file), bstack11l1l_opy_ (u"ࠧࡳࡤࠪầ")), bstack11l1l_opy_ (u"ࠨࡣࡳࡴࡱ࡯ࡣࡢࡶ࡬ࡳࡳ࠵ࡸ࠮ࡩࡽ࡭ࡵ࠭Ẩ")),
        bstack11l1l_opy_ (u"ࠩࡦࡰ࡮࡫࡮ࡵࡄࡸ࡭ࡱࡪࡕࡶ࡫ࡧࠫẩ"): uuid
      }
    )
    bstack111l111l1l1_opy_ = bstack1l1l1ll1l_opy_(cli.config, [bstack11l1l_opy_ (u"ࠥࡥࡵ࡯ࡳࠣẪ"), bstack11l1l_opy_ (u"ࠦࡴࡨࡳࡦࡴࡹࡥࡧ࡯࡬ࡪࡶࡼࠦẫ"), bstack11l1l_opy_ (u"ࠧࡻࡰ࡭ࡱࡤࡨࠧẬ")], bstack11l1l11ll1l_opy_)
    response = requests.post(
      bstack11l1l_opy_ (u"ࠨࡻࡾ࠱ࡦࡰ࡮࡫࡮ࡵ࠯࡯ࡳ࡬ࡹ࠯ࡶࡲ࡯ࡳࡦࡪࠢậ").format(bstack111l111l1l1_opy_),
      data=bstack11l111l111_opy_,
      headers={bstack11l1l_opy_ (u"ࠧࡄࡱࡱࡸࡪࡴࡴ࠮ࡖࡼࡴࡪ࠭Ắ"): bstack11l111l111_opy_.content_type},
      auth=(config[bstack11l1l_opy_ (u"ࠨࡷࡶࡩࡷࡔࡡ࡮ࡧࠪắ")], config[bstack11l1l_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴࡍࡨࡽࠬẰ")])
    )
    os.remove(output_file)
    if response.status_code != 200:
      get_logger().debug(bstack11l1l_opy_ (u"ࠪࡉࡷࡸ࡯ࡳࠢࡸࡴࡱࡵࡡࡥࠢ࡯ࡳ࡬ࡹ࠺ࠡࠩằ") + response.status_code)
  except Exception as e:
    get_logger().debug(bstack11l1l_opy_ (u"ࠫࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡪࡰࠣࡷࡪࡴࡤࡪࡰࡪࠤࡱࡵࡧࡴ࠼ࠪẲ") + str(e))
  finally:
    try:
      bstack1l1l1l11lll_opy_()
      bstack1111lllllll_opy_()
    except:
      pass