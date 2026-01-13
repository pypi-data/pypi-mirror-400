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
import threading
import logging
import bstack_utils.accessibility as bstack1l1ll11l1l_opy_
from bstack_utils.helper import bstack1lll11l1l_opy_
logger = logging.getLogger(__name__)
def bstack111llll11l_opy_(bstack11ll11l111_opy_):
  return True if bstack11ll11l111_opy_ in threading.current_thread().__dict__.keys() else False
def bstack1l11111lll_opy_(context, *args):
    tags = getattr(args[0], bstack11ll1_opy_ (u"ࠫࡹࡧࡧࡴࠩ᠛"), [])
    bstack1ll11l111l_opy_ = bstack1l1ll11l1l_opy_.bstack1llll1111l_opy_(tags)
    threading.current_thread().isA11yTest = bstack1ll11l111l_opy_
    try:
      bstack11l1l1l1l1_opy_ = threading.current_thread().bstackSessionDriver if bstack111llll11l_opy_(bstack11ll1_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯ࡘ࡫ࡳࡴ࡫ࡲࡲࡉࡸࡩࡷࡧࡵࠫ᠜")) else context.browser
      if bstack11l1l1l1l1_opy_ and bstack11l1l1l1l1_opy_.session_id and bstack1ll11l111l_opy_ and bstack1lll11l1l_opy_(
              threading.current_thread(), bstack11ll1_opy_ (u"࠭ࡡ࠲࠳ࡼࡔࡱࡧࡴࡧࡱࡵࡱࠬ᠝"), None):
          threading.current_thread().isA11yTest = bstack1l1ll11l1l_opy_.bstack11lll1111l_opy_(bstack11l1l1l1l1_opy_, bstack1ll11l111l_opy_)
    except Exception as e:
       logger.debug(bstack11ll1_opy_ (u"ࠧࡇࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡷࡹࡧࡲࡵࠢࡤ࠵࠶ࡿࠠࡪࡰࠣࡦࡪ࡮ࡡࡷࡧ࠽ࠤࢀࢃࠧ᠞").format(str(e)))
def bstack1l1l1l1lll_opy_(bstack11l1l1l1l1_opy_):
    if bstack1lll11l1l_opy_(threading.current_thread(), bstack11ll1_opy_ (u"ࠨ࡫ࡶࡅ࠶࠷ࡹࡕࡧࡶࡸࠬ᠟"), None) and bstack1lll11l1l_opy_(
      threading.current_thread(), bstack11ll1_opy_ (u"ࠩࡤ࠵࠶ࡿࡐ࡭ࡣࡷࡪࡴࡸ࡭ࠨᠠ"), None) and not bstack1lll11l1l_opy_(threading.current_thread(), bstack11ll1_opy_ (u"ࠪࡥ࠶࠷ࡹࡠࡵࡷࡳࡵ࠭ᠡ"), False):
      threading.current_thread().a11y_stop = True
      bstack1l1ll11l1l_opy_.bstack1lll1111ll_opy_(bstack11l1l1l1l1_opy_, name=bstack11ll1_opy_ (u"ࠦࠧᠢ"), path=bstack11ll1_opy_ (u"ࠧࠨᠣ"))