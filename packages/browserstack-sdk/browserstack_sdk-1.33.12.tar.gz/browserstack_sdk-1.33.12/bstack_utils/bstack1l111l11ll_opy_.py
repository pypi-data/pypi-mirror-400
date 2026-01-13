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
import logging
import datetime
import threading
from bstack_utils.helper import bstack11ll111l1ll_opy_, bstack1lll11llll_opy_, get_host_info, bstack111l1l1lll1_opy_, \
 bstack11lllll11l_opy_, bstack1lll11l1l_opy_, error_handler, bstack11l111l1lll_opy_, bstack111lll1lll_opy_
import bstack_utils.accessibility as bstack1l1ll11l1l_opy_
from bstack_utils.bstack11l111l1_opy_ import bstack1lll1lll_opy_
from bstack_utils.bstack111ll11lll_opy_ import bstack1l11llll1l_opy_
from bstack_utils.percy import bstack11l1l11l1_opy_
from bstack_utils.config import Config
bstack1l1l1ll1l_opy_ = Config.bstack1l1l1111_opy_()
logger = logging.getLogger(__name__)
percy = bstack11l1l11l1_opy_()
@error_handler(class_method=False)
def bstack1lll1lll1l1l_opy_(bs_config, bstack11l111111_opy_):
  try:
    data = {
        bstack11ll1_opy_ (u"ࠩࡩࡳࡷࡳࡡࡵࠩ⊠"): bstack11ll1_opy_ (u"ࠪ࡮ࡸࡵ࡮ࠨ⊡"),
        bstack11ll1_opy_ (u"ࠫࡵࡸ࡯࡫ࡧࡦࡸࡤࡴࡡ࡮ࡧࠪ⊢"): bs_config.get(bstack11ll1_opy_ (u"ࠬࡶࡲࡰ࡬ࡨࡧࡹࡔࡡ࡮ࡧࠪ⊣"), bstack11ll1_opy_ (u"࠭ࠧ⊤")),
        bstack11ll1_opy_ (u"ࠧ࡯ࡣࡰࡩࠬ⊥"): bs_config.get(bstack11ll1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠫ⊦"), os.path.basename(os.path.abspath(os.getcwd()))),
        bstack11ll1_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡠ࡫ࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬ⊧"): bs_config.get(bstack11ll1_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬ⊨")),
        bstack11ll1_opy_ (u"ࠫࡩ࡫ࡳࡤࡴ࡬ࡴࡹ࡯࡯࡯ࠩ⊩"): bs_config.get(bstack11ll1_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡈࡪࡹࡣࡳ࡫ࡳࡸ࡮ࡵ࡮ࠨ⊪"), bstack11ll1_opy_ (u"࠭ࠧ⊫")),
        bstack11ll1_opy_ (u"ࠧࡴࡶࡤࡶࡹ࡫ࡤࡠࡣࡷࠫ⊬"): bstack111lll1lll_opy_(),
        bstack11ll1_opy_ (u"ࠨࡶࡤ࡫ࡸ࠭⊭"): bstack111l1l1lll1_opy_(bs_config),
        bstack11ll1_opy_ (u"ࠩ࡫ࡳࡸࡺ࡟ࡪࡰࡩࡳࠬ⊮"): get_host_info(),
        bstack11ll1_opy_ (u"ࠪࡧ࡮ࡥࡩ࡯ࡨࡲࠫ⊯"): bstack1lll11llll_opy_(),
        bstack11ll1_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡢࡶࡺࡴ࡟ࡪࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫ⊰"): os.environ.get(bstack11ll1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡇ࡛ࡉࡍࡆࡢࡖ࡚ࡔ࡟ࡊࡆࡈࡒ࡙ࡏࡆࡊࡇࡕࠫ⊱")),
        bstack11ll1_opy_ (u"࠭ࡦࡢ࡫࡯ࡩࡩࡥࡴࡦࡵࡷࡷࡤࡸࡥࡳࡷࡱࠫ⊲"): os.environ.get(bstack11ll1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡒࡆࡔࡘࡒࠬ⊳"), False),
        bstack11ll1_opy_ (u"ࠨࡸࡨࡶࡸ࡯࡯࡯ࡡࡦࡳࡳࡺࡲࡰ࡮ࠪ⊴"): bstack11ll111l1ll_opy_(),
        bstack11ll1_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠩ⊵"): bstack1lll1l1llll1_opy_(bs_config),
        bstack11ll1_opy_ (u"ࠪࡪࡷࡧ࡭ࡦࡹࡲࡶࡰࡥࡤࡦࡶࡤ࡭ࡱࡹࠧ⊶"): bstack1lll1l1l11l1_opy_(bstack11l111111_opy_),
        bstack11ll1_opy_ (u"ࠫࡵࡸ࡯ࡥࡷࡦࡸࡤࡳࡡࡱࠩ⊷"): bstack1lll1l1l1lll_opy_(bs_config, bstack11l111111_opy_.get(bstack11ll1_opy_ (u"ࠬ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡷࡶࡩࡩ࠭⊸"), bstack11ll1_opy_ (u"࠭ࠧ⊹"))),
        bstack11ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡇࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࠩ⊺"): bstack11lllll11l_opy_(bs_config),
        bstack11ll1_opy_ (u"ࠨࡶࡨࡷࡹࡥ࡯ࡳࡥ࡫ࡩࡸࡺࡲࡢࡶ࡬ࡳࡳ࠭⊻"): bstack1lll1l1l111l_opy_(bs_config)
    }
    return data
  except Exception as error:
    logger.error(bstack11ll1_opy_ (u"ࠤࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥࡽࡨࡪ࡮ࡨࠤࡨࡸࡥࡢࡶ࡬ࡲ࡬ࠦࡰࡢࡻ࡯ࡳࡦࡪࠠࡧࡱࡵࠤ࡙࡫ࡳࡵࡊࡸࡦ࠿ࠦࠠࡼࡿࠥ⊼").format(str(error)))
    return None
def bstack1lll1l1l11l1_opy_(framework):
  return {
    bstack11ll1_opy_ (u"ࠪࡪࡷࡧ࡭ࡦࡹࡲࡶࡰࡔࡡ࡮ࡧࠪ⊽"): framework.get(bstack11ll1_opy_ (u"ࠫ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟࡯ࡣࡰࡩࠬ⊾"), bstack11ll1_opy_ (u"ࠬࡖࡹࡵࡧࡶࡸࠬ⊿")),
    bstack11ll1_opy_ (u"࠭ࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡘࡨࡶࡸ࡯࡯࡯ࠩ⋀"): framework.get(bstack11ll1_opy_ (u"ࠧࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡢࡺࡪࡸࡳࡪࡱࡱࠫ⋁")),
    bstack11ll1_opy_ (u"ࠨࡵࡧ࡯࡛࡫ࡲࡴ࡫ࡲࡲࠬ⋂"): framework.get(bstack11ll1_opy_ (u"ࠩࡶࡨࡰࡥࡶࡦࡴࡶ࡭ࡴࡴࠧ⋃")),
    bstack11ll1_opy_ (u"ࠪࡰࡦࡴࡧࡶࡣࡪࡩࠬ⋄"): bstack11ll1_opy_ (u"ࠫࡵࡿࡴࡩࡱࡱࠫ⋅"),
    bstack11ll1_opy_ (u"ࠬࡺࡥࡴࡶࡉࡶࡦࡳࡥࡸࡱࡵ࡯ࠬ⋆"): framework.get(bstack11ll1_opy_ (u"࠭ࡴࡦࡵࡷࡊࡷࡧ࡭ࡦࡹࡲࡶࡰ࠭⋇"))
  }
def bstack1lll1l1l111l_opy_(bs_config):
  bstack11ll1_opy_ (u"ࠢࠣࠤࠍࠤࠥࡘࡥࡵࡷࡵࡲࡸࠦࡴࡩࡧࠣࡸࡪࡹࡴࠡࡱࡵࡧ࡭࡫ࡳࡵࡴࡤࡸ࡮ࡵ࡮ࠡࡦࡤࡸࡦࠦࡦࡰࡴࠣࡦࡺ࡯࡬ࡥࠢࡶࡸࡦࡸࡴ࠯ࠌࠣࠤࠧࠨࠢ⋈")
  if not bs_config:
    return {}
  bstack1111l11lll1_opy_ = bstack1lll1lll_opy_(bs_config).bstack11111l1lll1_opy_(bs_config)
  return bstack1111l11lll1_opy_
def bstack111lll11l_opy_(bs_config, framework):
  bstack11lll11l1_opy_ = False
  bstack111lllll11_opy_ = False
  bstack1lll1l1lll11_opy_ = False
  if bstack11ll1_opy_ (u"ࠨࡶࡸࡶࡧࡵࡓࡤࡣ࡯ࡩࠬ⋉") in bs_config:
    bstack1lll1l1lll11_opy_ = True
  elif bstack11ll1_opy_ (u"ࠩࡤࡴࡵ࠭⋊") in bs_config:
    bstack11lll11l1_opy_ = True
  else:
    bstack111lllll11_opy_ = True
  bstack11l1111l11_opy_ = {
    bstack11ll1_opy_ (u"ࠪࡳࡧࡹࡥࡳࡸࡤࡦ࡮ࡲࡩࡵࡻࠪ⋋"): bstack1l11llll1l_opy_.bstack1lll1l1l1ll1_opy_(bs_config, framework),
    bstack11ll1_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠫ⋌"): bstack1l1ll11l1l_opy_.bstack11l1l1ll1_opy_(bs_config),
    bstack11ll1_opy_ (u"ࠬࡶࡥࡳࡥࡼࠫ⋍"): bs_config.get(bstack11ll1_opy_ (u"࠭ࡰࡦࡴࡦࡽࠬ⋎"), False),
    bstack11ll1_opy_ (u"ࠧࡢࡷࡷࡳࡲࡧࡴࡦࠩ⋏"): bstack111lllll11_opy_,
    bstack11ll1_opy_ (u"ࠨࡣࡳࡴࡤࡧࡵࡵࡱࡰࡥࡹ࡫ࠧ⋐"): bstack11lll11l1_opy_,
    bstack11ll1_opy_ (u"ࠩࡷࡹࡷࡨ࡯ࡴࡥࡤࡰࡪ࠭⋑"): bstack1lll1l1lll11_opy_
  }
  return bstack11l1111l11_opy_
@error_handler(class_method=False)
def bstack1lll1l1llll1_opy_(bs_config):
  try:
    bstack1lll1l1ll111_opy_ = json.loads(os.getenv(bstack11ll1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡉࡘ࡚࡟ࡂࡅࡆࡉࡘ࡙ࡉࡃࡋࡏࡍ࡙࡟࡟ࡄࡑࡑࡊࡎࡍࡕࡓࡃࡗࡍࡔࡔ࡟࡚ࡏࡏࠫ⋒"), bstack11ll1_opy_ (u"ࠫࢀࢃࠧ⋓")))
    bstack1lll1l1ll111_opy_ = bstack1lll1l1lll1l_opy_(bs_config, bstack1lll1l1ll111_opy_)
    return {
        bstack11ll1_opy_ (u"ࠬࡹࡥࡵࡶ࡬ࡲ࡬ࡹࠧ⋔"): bstack1lll1l1ll111_opy_
    }
  except Exception as error:
    logger.error(bstack11ll1_opy_ (u"ࠨࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢࡺ࡬࡮ࡲࡥࠡࡥࡵࡩࡦࡺࡩ࡯ࡩࠣ࡫ࡪࡺ࡟ࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿ࡟ࡴࡧࡷࡸ࡮ࡴࡧࡴࠢࡩࡳࡷࠦࡔࡦࡵࡷࡌࡺࡨ࠺ࠡࠢࡾࢁࠧ⋕").format(str(error)))
    return {}
def bstack1lll1l1lll1l_opy_(bs_config, bstack1lll1l1ll111_opy_):
  if ((bstack11ll1_opy_ (u"ࠧࡵࡷࡵࡦࡴ࡙ࡣࡢ࡮ࡨࠫ⋖") in bs_config or not bstack11lllll11l_opy_(bs_config)) and bstack1l1ll11l1l_opy_.bstack11l1l1ll1_opy_(bs_config)):
    bstack1lll1l1ll111_opy_[bstack11ll1_opy_ (u"ࠣ࡫ࡱࡧࡱࡻࡤࡦࡇࡱࡧࡴࡪࡥࡥࡇࡻࡸࡪࡴࡳࡪࡱࡱࠦ⋗")] = True
  return bstack1lll1l1ll111_opy_
def bstack1lll1ll1l11l_opy_(array, bstack1lll1l1ll1l1_opy_, bstack1lll1l1l1l1l_opy_):
  result = {}
  for o in array:
    key = o[bstack1lll1l1ll1l1_opy_]
    result[key] = o[bstack1lll1l1l1l1l_opy_]
  return result
def bstack1lll1lll1l11_opy_(bstack1l1l11lll1_opy_=bstack11ll1_opy_ (u"ࠩࠪ⋘")):
  bstack1lll1l1l1l11_opy_ = bstack1l1ll11l1l_opy_.on()
  bstack1lll1l1l11ll_opy_ = bstack1l11llll1l_opy_.on()
  bstack1lll1l1ll1ll_opy_ = percy.bstack1lll1l11l1_opy_()
  if bstack1lll1l1ll1ll_opy_ and not bstack1lll1l1l11ll_opy_ and not bstack1lll1l1l1l11_opy_:
    return bstack1l1l11lll1_opy_ not in [bstack11ll1_opy_ (u"ࠪࡇࡇ࡚ࡓࡦࡵࡶ࡭ࡴࡴࡃࡳࡧࡤࡸࡪࡪࠧ⋙"), bstack11ll1_opy_ (u"ࠫࡑࡵࡧࡄࡴࡨࡥࡹ࡫ࡤࠨ⋚")]
  elif bstack1lll1l1l1l11_opy_ and not bstack1lll1l1l11ll_opy_:
    return bstack1l1l11lll1_opy_ not in [bstack11ll1_opy_ (u"ࠬࡎ࡯ࡰ࡭ࡕࡹࡳ࡙ࡴࡢࡴࡷࡩࡩ࠭⋛"), bstack11ll1_opy_ (u"࠭ࡈࡰࡱ࡮ࡖࡺࡴࡆࡪࡰ࡬ࡷ࡭࡫ࡤࠨ⋜"), bstack11ll1_opy_ (u"ࠧࡍࡱࡪࡇࡷ࡫ࡡࡵࡧࡧࠫ⋝")]
  return bstack1lll1l1l1l11_opy_ or bstack1lll1l1l11ll_opy_ or bstack1lll1l1ll1ll_opy_
@error_handler(class_method=False)
def bstack1lll1ll11111_opy_(bstack1l1l11lll1_opy_, test=None):
  bstack1lll1l1ll11l_opy_ = bstack1l1ll11l1l_opy_.on()
  if not bstack1lll1l1ll11l_opy_ or bstack1l1l11lll1_opy_ not in [bstack11ll1_opy_ (u"ࠨࡖࡨࡷࡹࡘࡵ࡯ࡈ࡬ࡲ࡮ࡹࡨࡦࡦࠪ⋞")] or test == None:
    return None
  return {
    bstack11ll1_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠩ⋟"): bstack1lll1l1ll11l_opy_ and bstack1lll11l1l_opy_(threading.current_thread(), bstack11ll1_opy_ (u"ࠪࡥ࠶࠷ࡹࡑ࡮ࡤࡸ࡫ࡵࡲ࡮ࠩ⋠"), None) == True and bstack1l1ll11l1l_opy_.bstack1llll1111l_opy_(test[bstack11ll1_opy_ (u"ࠫࡹࡧࡧࡴࠩ⋡")])
  }
def bstack1lll1l1l1lll_opy_(bs_config, framework):
  bstack11lll11l1_opy_ = False
  bstack111lllll11_opy_ = False
  bstack1lll1l1lll11_opy_ = False
  if bstack11ll1_opy_ (u"ࠬࡺࡵࡳࡤࡲࡗࡨࡧ࡬ࡦࠩ⋢") in bs_config:
    bstack1lll1l1lll11_opy_ = True
  elif bstack11ll1_opy_ (u"࠭ࡡࡱࡲࠪ⋣") in bs_config:
    bstack11lll11l1_opy_ = True
  else:
    bstack111lllll11_opy_ = True
  bstack11l1111l11_opy_ = {
    bstack11ll1_opy_ (u"ࠧࡰࡤࡶࡩࡷࡼࡡࡣ࡫࡯࡭ࡹࡿࠧ⋤"): bstack1l11llll1l_opy_.bstack1lll1l1l1ll1_opy_(bs_config, framework),
    bstack11ll1_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠨ⋥"): bstack1l1ll11l1l_opy_.bstack1llll1l11l_opy_(bs_config),
    bstack11ll1_opy_ (u"ࠩࡳࡩࡷࡩࡹࠨ⋦"): bs_config.get(bstack11ll1_opy_ (u"ࠪࡴࡪࡸࡣࡺࠩ⋧"), False),
    bstack11ll1_opy_ (u"ࠫࡦࡻࡴࡰ࡯ࡤࡸࡪ࠭⋨"): bstack111lllll11_opy_,
    bstack11ll1_opy_ (u"ࠬࡧࡰࡱࡡࡤࡹࡹࡵ࡭ࡢࡶࡨࠫ⋩"): bstack11lll11l1_opy_,
    bstack11ll1_opy_ (u"࠭ࡴࡶࡴࡥࡳࡸࡩࡡ࡭ࡧࠪ⋪"): bstack1lll1l1lll11_opy_
  }
  return bstack11l1111l11_opy_