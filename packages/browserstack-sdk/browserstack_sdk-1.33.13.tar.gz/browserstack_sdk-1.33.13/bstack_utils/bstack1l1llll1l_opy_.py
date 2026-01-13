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
import logging
import datetime
import threading
from bstack_utils.helper import bstack11ll11l11l1_opy_, bstack1l111l11l1_opy_, get_host_info, bstack111ll11l11l_opy_, \
 bstack11lll11ll1_opy_, bstack11lll11l_opy_, error_handler, bstack111llll111l_opy_, bstack1lllll111_opy_
import bstack_utils.accessibility as bstack11llll11l1_opy_
from bstack_utils.bstack1111l1ll_opy_ import bstack11llllll1l_opy_
from bstack_utils.bstack111ll11111_opy_ import bstack11llll111_opy_
from bstack_utils.percy import bstack1l111lll1l_opy_
from bstack_utils.config import Config
bstack1l1ll11111_opy_ = Config.bstack11l1l11ll1_opy_()
logger = logging.getLogger(__name__)
percy = bstack1l111lll1l_opy_()
@error_handler(class_method=False)
def bstack1lll1ll1ll11_opy_(bs_config, bstack1llll111_opy_):
  try:
    data = {
        bstack11l1l_opy_ (u"ࠨࡨࡲࡶࡲࡧࡴࠨ⊟"): bstack11l1l_opy_ (u"ࠩ࡭ࡷࡴࡴࠧ⊠"),
        bstack11l1l_opy_ (u"ࠪࡴࡷࡵࡪࡦࡥࡷࡣࡳࡧ࡭ࡦࠩ⊡"): bs_config.get(bstack11l1l_opy_ (u"ࠫࡵࡸ࡯࡫ࡧࡦࡸࡓࡧ࡭ࡦࠩ⊢"), bstack11l1l_opy_ (u"ࠬ࠭⊣")),
        bstack11l1l_opy_ (u"࠭࡮ࡢ࡯ࡨࠫ⊤"): bs_config.get(bstack11l1l_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡔࡡ࡮ࡧࠪ⊥"), os.path.basename(os.path.abspath(os.getcwd()))),
        bstack11l1l_opy_ (u"ࠨࡤࡸ࡭ࡱࡪ࡟ࡪࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫ⊦"): bs_config.get(bstack11l1l_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫ⊧")),
        bstack11l1l_opy_ (u"ࠪࡨࡪࡹࡣࡳ࡫ࡳࡸ࡮ࡵ࡮ࠨ⊨"): bs_config.get(bstack11l1l_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡇࡩࡸࡩࡲࡪࡲࡷ࡭ࡴࡴࠧ⊩"), bstack11l1l_opy_ (u"ࠬ࠭⊪")),
        bstack11l1l_opy_ (u"࠭ࡳࡵࡣࡵࡸࡪࡪ࡟ࡢࡶࠪ⊫"): bstack1lllll111_opy_(),
        bstack11l1l_opy_ (u"ࠧࡵࡣࡪࡷࠬ⊬"): bstack111ll11l11l_opy_(bs_config),
        bstack11l1l_opy_ (u"ࠨࡪࡲࡷࡹࡥࡩ࡯ࡨࡲࠫ⊭"): get_host_info(),
        bstack11l1l_opy_ (u"ࠩࡦ࡭ࡤ࡯࡮ࡧࡱࠪ⊮"): bstack1l111l11l1_opy_(),
        bstack11l1l_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡡࡵࡹࡳࡥࡩࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪ⊯"): os.environ.get(bstack11l1l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡆ࡚ࡏࡌࡅࡡࡕ࡙ࡓࡥࡉࡅࡇࡑࡘࡎࡌࡉࡆࡔࠪ⊰")),
        bstack11l1l_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡨࡨࡤࡺࡥࡴࡶࡶࡣࡷ࡫ࡲࡶࡰࠪ⊱"): os.environ.get(bstack11l1l_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡘࡅࡓࡗࡑࠫ⊲"), False),
        bstack11l1l_opy_ (u"ࠧࡷࡧࡵࡷ࡮ࡵ࡮ࡠࡥࡲࡲࡹࡸ࡯࡭ࠩ⊳"): bstack11ll11l11l1_opy_(),
        bstack11l1l_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠨ⊴"): bstack1lll1l1l111l_opy_(bs_config),
        bstack11l1l_opy_ (u"ࠩࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࡤࡪࡥࡵࡣ࡬ࡰࡸ࠭⊵"): bstack1lll1l1lll1l_opy_(bstack1llll111_opy_),
        bstack11l1l_opy_ (u"ࠪࡴࡷࡵࡤࡶࡥࡷࡣࡲࡧࡰࠨ⊶"): bstack1lll1l1l1l11_opy_(bs_config, bstack1llll111_opy_.get(bstack11l1l_opy_ (u"ࠫ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟ࡶࡵࡨࡨࠬ⊷"), bstack11l1l_opy_ (u"ࠬ࠭⊸"))),
        bstack11l1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡆࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠨ⊹"): bstack11lll11ll1_opy_(bs_config),
        bstack11l1l_opy_ (u"ࠧࡵࡧࡶࡸࡤࡵࡲࡤࡪࡨࡷࡹࡸࡡࡵ࡫ࡲࡲࠬ⊺"): bstack1lll1l1l1ll1_opy_(bs_config)
    }
    return data
  except Exception as error:
    logger.error(bstack11l1l_opy_ (u"ࠣࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤࡼ࡮ࡩ࡭ࡧࠣࡧࡷ࡫ࡡࡵ࡫ࡱ࡫ࠥࡶࡡࡺ࡮ࡲࡥࡩࠦࡦࡰࡴࠣࡘࡪࡹࡴࡉࡷࡥ࠾ࠥࠦࡻࡾࠤ⊻").format(str(error)))
    return None
def bstack1lll1l1lll1l_opy_(framework):
  return {
    bstack11l1l_opy_ (u"ࠩࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࡓࡧ࡭ࡦࠩ⊼"): framework.get(bstack11l1l_opy_ (u"ࠪࡪࡷࡧ࡭ࡦࡹࡲࡶࡰࡥ࡮ࡢ࡯ࡨࠫ⊽"), bstack11l1l_opy_ (u"ࠫࡕࡿࡴࡦࡵࡷࠫ⊾")),
    bstack11l1l_opy_ (u"ࠬ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡗࡧࡵࡷ࡮ࡵ࡮ࠨ⊿"): framework.get(bstack11l1l_opy_ (u"࠭ࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡹࡩࡷࡹࡩࡰࡰࠪ⋀")),
    bstack11l1l_opy_ (u"ࠧࡴࡦ࡮࡚ࡪࡸࡳࡪࡱࡱࠫ⋁"): framework.get(bstack11l1l_opy_ (u"ࠨࡵࡧ࡯ࡤࡼࡥࡳࡵ࡬ࡳࡳ࠭⋂")),
    bstack11l1l_opy_ (u"ࠩ࡯ࡥࡳ࡭ࡵࡢࡩࡨࠫ⋃"): bstack11l1l_opy_ (u"ࠪࡴࡾࡺࡨࡰࡰࠪ⋄"),
    bstack11l1l_opy_ (u"ࠫࡹ࡫ࡳࡵࡈࡵࡥࡲ࡫ࡷࡰࡴ࡮ࠫ⋅"): framework.get(bstack11l1l_opy_ (u"ࠬࡺࡥࡴࡶࡉࡶࡦࡳࡥࡸࡱࡵ࡯ࠬ⋆"))
  }
def bstack1lll1l1l1ll1_opy_(bs_config):
  bstack11l1l_opy_ (u"ࠨࠢࠣࠌࠣࠤࡗ࡫ࡴࡶࡴࡱࡷࠥࡺࡨࡦࠢࡷࡩࡸࡺࠠࡰࡴࡦ࡬ࡪࡹࡴࡳࡣࡷ࡭ࡴࡴࠠࡥࡣࡷࡥࠥ࡬࡯ࡳࠢࡥࡹ࡮ࡲࡤࠡࡵࡷࡥࡷࡺ࠮ࠋࠢࠣࠦࠧࠨ⋇")
  if not bs_config:
    return {}
  bstack11111l1l11l_opy_ = bstack11llllll1l_opy_(bs_config).bstack1111l1111ll_opy_(bs_config)
  return bstack11111l1l11l_opy_
def bstack1llll1l1_opy_(bs_config, framework):
  bstack111lll11l_opy_ = False
  bstack1ll11l1l11_opy_ = False
  bstack1lll1l1l11ll_opy_ = False
  if bstack11l1l_opy_ (u"ࠧࡵࡷࡵࡦࡴ࡙ࡣࡢ࡮ࡨࠫ⋈") in bs_config:
    bstack1lll1l1l11ll_opy_ = True
  elif bstack11l1l_opy_ (u"ࠨࡣࡳࡴࠬ⋉") in bs_config:
    bstack111lll11l_opy_ = True
  else:
    bstack1ll11l1l11_opy_ = True
  bstack11l1111ll1_opy_ = {
    bstack11l1l_opy_ (u"ࠩࡲࡦࡸ࡫ࡲࡷࡣࡥ࡭ࡱ࡯ࡴࡺࠩ⋊"): bstack11llll111_opy_.bstack1lll1l1l1l1l_opy_(bs_config, framework),
    bstack11l1l_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠪ⋋"): bstack11llll11l1_opy_.bstack1111111l1_opy_(bs_config),
    bstack11l1l_opy_ (u"ࠫࡵ࡫ࡲࡤࡻࠪ⋌"): bs_config.get(bstack11l1l_opy_ (u"ࠬࡶࡥࡳࡥࡼࠫ⋍"), False),
    bstack11l1l_opy_ (u"࠭ࡡࡶࡶࡲࡱࡦࡺࡥࠨ⋎"): bstack1ll11l1l11_opy_,
    bstack11l1l_opy_ (u"ࠧࡢࡲࡳࡣࡦࡻࡴࡰ࡯ࡤࡸࡪ࠭⋏"): bstack111lll11l_opy_,
    bstack11l1l_opy_ (u"ࠨࡶࡸࡶࡧࡵࡳࡤࡣ࡯ࡩࠬ⋐"): bstack1lll1l1l11ll_opy_
  }
  return bstack11l1111ll1_opy_
@error_handler(class_method=False)
def bstack1lll1l1l111l_opy_(bs_config):
  try:
    bstack1lll1l1llll1_opy_ = json.loads(os.getenv(bstack11l1l_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡥࡁࡄࡅࡈࡗࡘࡏࡂࡊࡎࡌࡘ࡞ࡥࡃࡐࡐࡉࡍࡌ࡛ࡒࡂࡖࡌࡓࡓࡥ࡙ࡎࡎࠪ⋑"), bstack11l1l_opy_ (u"ࠪࡿࢂ࠭⋒")))
    bstack1lll1l1llll1_opy_ = bstack1lll1l1ll111_opy_(bs_config, bstack1lll1l1llll1_opy_)
    return {
        bstack11l1l_opy_ (u"ࠫࡸ࡫ࡴࡵ࡫ࡱ࡫ࡸ࠭⋓"): bstack1lll1l1llll1_opy_
    }
  except Exception as error:
    logger.error(bstack11l1l_opy_ (u"ࠧࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡࡹ࡫࡭ࡱ࡫ࠠࡤࡴࡨࡥࡹ࡯࡮ࡨࠢࡪࡩࡹࡥࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࡥࡳࡦࡶࡷ࡭ࡳ࡭ࡳࠡࡨࡲࡶ࡚ࠥࡥࡴࡶࡋࡹࡧࡀࠠࠡࡽࢀࠦ⋔").format(str(error)))
    return {}
def bstack1lll1l1ll111_opy_(bs_config, bstack1lll1l1llll1_opy_):
  if ((bstack11l1l_opy_ (u"࠭ࡴࡶࡴࡥࡳࡘࡩࡡ࡭ࡧࠪ⋕") in bs_config or not bstack11lll11ll1_opy_(bs_config)) and bstack11llll11l1_opy_.bstack1111111l1_opy_(bs_config)):
    bstack1lll1l1llll1_opy_[bstack11l1l_opy_ (u"ࠢࡪࡰࡦࡰࡺࡪࡥࡆࡰࡦࡳࡩ࡫ࡤࡆࡺࡷࡩࡳࡹࡩࡰࡰࠥ⋖")] = True
  return bstack1lll1l1llll1_opy_
def bstack1lll1ll11ll1_opy_(array, bstack1lll1l1ll1l1_opy_, bstack1lll1l1ll11l_opy_):
  result = {}
  for o in array:
    key = o[bstack1lll1l1ll1l1_opy_]
    result[key] = o[bstack1lll1l1ll11l_opy_]
  return result
def bstack1lll1lll11ll_opy_(bstack1lll1lll_opy_=bstack11l1l_opy_ (u"ࠨࠩ⋗")):
  bstack1lll1l1l1lll_opy_ = bstack11llll11l1_opy_.on()
  bstack1lll1l1ll1ll_opy_ = bstack11llll111_opy_.on()
  bstack1lll1l1l11l1_opy_ = percy.bstack1llll111l_opy_()
  if bstack1lll1l1l11l1_opy_ and not bstack1lll1l1ll1ll_opy_ and not bstack1lll1l1l1lll_opy_:
    return bstack1lll1lll_opy_ not in [bstack11l1l_opy_ (u"ࠩࡆࡆ࡙࡙ࡥࡴࡵ࡬ࡳࡳࡉࡲࡦࡣࡷࡩࡩ࠭⋘"), bstack11l1l_opy_ (u"ࠪࡐࡴ࡭ࡃࡳࡧࡤࡸࡪࡪࠧ⋙")]
  elif bstack1lll1l1l1lll_opy_ and not bstack1lll1l1ll1ll_opy_:
    return bstack1lll1lll_opy_ not in [bstack11l1l_opy_ (u"ࠫࡍࡵ࡯࡬ࡔࡸࡲࡘࡺࡡࡳࡶࡨࡨࠬ⋚"), bstack11l1l_opy_ (u"ࠬࡎ࡯ࡰ࡭ࡕࡹࡳࡌࡩ࡯࡫ࡶ࡬ࡪࡪࠧ⋛"), bstack11l1l_opy_ (u"࠭ࡌࡰࡩࡆࡶࡪࡧࡴࡦࡦࠪ⋜")]
  return bstack1lll1l1l1lll_opy_ or bstack1lll1l1ll1ll_opy_ or bstack1lll1l1l11l1_opy_
@error_handler(class_method=False)
def bstack1lll1ll11lll_opy_(bstack1lll1lll_opy_, test=None):
  bstack1lll1l1lll11_opy_ = bstack11llll11l1_opy_.on()
  if not bstack1lll1l1lll11_opy_ or bstack1lll1lll_opy_ not in [bstack11l1l_opy_ (u"ࠧࡕࡧࡶࡸࡗࡻ࡮ࡇ࡫ࡱ࡭ࡸ࡮ࡥࡥࠩ⋝")] or test == None:
    return None
  return {
    bstack11l1l_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠨ⋞"): bstack1lll1l1lll11_opy_ and bstack11lll11l_opy_(threading.current_thread(), bstack11l1l_opy_ (u"ࠩࡤ࠵࠶ࡿࡐ࡭ࡣࡷࡪࡴࡸ࡭ࠨ⋟"), None) == True and bstack11llll11l1_opy_.bstack1l11l11l_opy_(test[bstack11l1l_opy_ (u"ࠪࡸࡦ࡭ࡳࠨ⋠")])
  }
def bstack1lll1l1l1l11_opy_(bs_config, framework):
  bstack111lll11l_opy_ = False
  bstack1ll11l1l11_opy_ = False
  bstack1lll1l1l11ll_opy_ = False
  if bstack11l1l_opy_ (u"ࠫࡹࡻࡲࡣࡱࡖࡧࡦࡲࡥࠨ⋡") in bs_config:
    bstack1lll1l1l11ll_opy_ = True
  elif bstack11l1l_opy_ (u"ࠬࡧࡰࡱࠩ⋢") in bs_config:
    bstack111lll11l_opy_ = True
  else:
    bstack1ll11l1l11_opy_ = True
  bstack11l1111ll1_opy_ = {
    bstack11l1l_opy_ (u"࠭࡯ࡣࡵࡨࡶࡻࡧࡢࡪ࡮࡬ࡸࡾ࠭⋣"): bstack11llll111_opy_.bstack1lll1l1l1l1l_opy_(bs_config, framework),
    bstack11l1l_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠧ⋤"): bstack11llll11l1_opy_.bstack1lllll1lll_opy_(bs_config),
    bstack11l1l_opy_ (u"ࠨࡲࡨࡶࡨࡿࠧ⋥"): bs_config.get(bstack11l1l_opy_ (u"ࠩࡳࡩࡷࡩࡹࠨ⋦"), False),
    bstack11l1l_opy_ (u"ࠪࡥࡺࡺ࡯࡮ࡣࡷࡩࠬ⋧"): bstack1ll11l1l11_opy_,
    bstack11l1l_opy_ (u"ࠫࡦࡶࡰࡠࡣࡸࡸࡴࡳࡡࡵࡧࠪ⋨"): bstack111lll11l_opy_,
    bstack11l1l_opy_ (u"ࠬࡺࡵࡳࡤࡲࡷࡨࡧ࡬ࡦࠩ⋩"): bstack1lll1l1l11ll_opy_
  }
  return bstack11l1111ll1_opy_