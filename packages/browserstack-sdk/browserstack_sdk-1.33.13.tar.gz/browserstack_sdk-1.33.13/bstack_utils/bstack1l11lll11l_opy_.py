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
import threading
import logging
import bstack_utils.accessibility as bstack11llll11l1_opy_
from bstack_utils.helper import bstack11lll11l_opy_
logger = logging.getLogger(__name__)
def bstack111llll111_opy_(bstack1ll11ll1_opy_):
  return True if bstack1ll11ll1_opy_ in threading.current_thread().__dict__.keys() else False
def bstack111l1l11l_opy_(context, *args):
    tags = getattr(args[0], bstack11l1l_opy_ (u"ࠪࡸࡦ࡭ࡳࠨ᠚"), [])
    bstack11l11ll1l_opy_ = bstack11llll11l1_opy_.bstack1l11l11l_opy_(tags)
    threading.current_thread().isA11yTest = bstack11l11ll1l_opy_
    try:
      bstack1l1l1l11l1_opy_ = threading.current_thread().bstackSessionDriver if bstack111llll111_opy_(bstack11l1l_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮ࡗࡪࡹࡳࡪࡱࡱࡈࡷ࡯ࡶࡦࡴࠪ᠛")) else context.browser
      if bstack1l1l1l11l1_opy_ and bstack1l1l1l11l1_opy_.session_id and bstack11l11ll1l_opy_ and bstack11lll11l_opy_(
              threading.current_thread(), bstack11l1l_opy_ (u"ࠬࡧ࠱࠲ࡻࡓࡰࡦࡺࡦࡰࡴࡰࠫ᠜"), None):
          threading.current_thread().isA11yTest = bstack11llll11l1_opy_.bstack1lll111ll1_opy_(bstack1l1l1l11l1_opy_, bstack11l11ll1l_opy_)
    except Exception as e:
       logger.debug(bstack11l1l_opy_ (u"࠭ࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡶࡸࡦࡸࡴࠡࡣ࠴࠵ࡾࠦࡩ࡯ࠢࡥࡩ࡭ࡧࡶࡦ࠼ࠣࡿࢂ࠭᠝").format(str(e)))
def bstack1l11llllll_opy_(bstack1l1l1l11l1_opy_):
    if bstack11lll11l_opy_(threading.current_thread(), bstack11l1l_opy_ (u"ࠧࡪࡵࡄ࠵࠶ࡿࡔࡦࡵࡷࠫ᠞"), None) and bstack11lll11l_opy_(
      threading.current_thread(), bstack11l1l_opy_ (u"ࠨࡣ࠴࠵ࡾࡖ࡬ࡢࡶࡩࡳࡷࡳࠧ᠟"), None) and not bstack11lll11l_opy_(threading.current_thread(), bstack11l1l_opy_ (u"ࠩࡤ࠵࠶ࡿ࡟ࡴࡶࡲࡴࠬᠠ"), False):
      threading.current_thread().a11y_stop = True
      bstack11llll11l1_opy_.bstack111ll1l1_opy_(bstack1l1l1l11l1_opy_, name=bstack11l1l_opy_ (u"ࠥࠦᠡ"), path=bstack11l1l_opy_ (u"ࠦࠧᠢ"))