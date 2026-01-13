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
import json
import multiprocessing
import os
from bstack_utils.config import Config
class bstack1lll11ll1_opy_():
  def __init__(self, args, logger, bstack1llllllllll_opy_, bstack1llllll1ll1_opy_, bstack1lllll1lll1_opy_):
    self.args = args
    self.logger = logger
    self.bstack1llllllllll_opy_ = bstack1llllllllll_opy_
    self.bstack1llllll1ll1_opy_ = bstack1llllll1ll1_opy_
    self.bstack1lllll1lll1_opy_ = bstack1lllll1lll1_opy_
  def bstack1ll1l1l1ll_opy_(self, bstack1111111lll_opy_, bstack1l11l1l1l_opy_, bstack1lllll1llll_opy_=False):
    bstack1ll1ll11l1_opy_ = []
    manager = multiprocessing.Manager()
    bstack111111111l_opy_ = manager.list()
    bstack1l1l1ll1l_opy_ = Config.bstack1l1l1111_opy_()
    if bstack1lllll1llll_opy_:
      for index, platform in enumerate(self.bstack1llllllllll_opy_[bstack11ll1_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩქ")]):
        if index == 0:
          bstack1l11l1l1l_opy_[bstack11ll1_opy_ (u"ࠧࡧ࡫࡯ࡩࡤࡴࡡ࡮ࡧࠪღ")] = self.args
        bstack1ll1ll11l1_opy_.append(multiprocessing.Process(name=str(index),
                                                    target=bstack1111111lll_opy_,
                                                    args=(bstack1l11l1l1l_opy_, bstack111111111l_opy_)))
    else:
      for index, platform in enumerate(self.bstack1llllllllll_opy_[bstack11ll1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫყ")]):
        bstack1ll1ll11l1_opy_.append(multiprocessing.Process(name=str(index),
                                                    target=bstack1111111lll_opy_,
                                                    args=(bstack1l11l1l1l_opy_, bstack111111111l_opy_)))
    i = 0
    for t in bstack1ll1ll11l1_opy_:
      try:
        if bstack1l1l1ll1l_opy_.get_property(bstack11ll1_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬ࡡࡶࡩࡸࡹࡩࡰࡰࠪშ")):
          os.environ[bstack11ll1_opy_ (u"ࠪࡇ࡚ࡘࡒࡆࡐࡗࡣࡕࡒࡁࡕࡈࡒࡖࡒࡥࡄࡂࡖࡄࠫჩ")] = json.dumps(self.bstack1llllllllll_opy_[bstack11ll1_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧც")][i % self.bstack1lllll1lll1_opy_])
      except Exception as e:
        self.logger.debug(bstack11ll1_opy_ (u"ࠧࡋࡲࡳࡱࡵࠤࡼ࡮ࡩ࡭ࡧࠣࡷࡹࡵࡲࡪࡰࡪࠤࡨࡻࡲࡳࡧࡱࡸࠥࡶ࡬ࡢࡶࡩࡳࡷࡳࠠࡥࡧࡷࡥ࡮ࡲࡳ࠻ࠢࡾࢁࠧძ").format(str(e)))
      i += 1
      t.start()
    for t in bstack1ll1ll11l1_opy_:
      t.join()
    return list(bstack111111111l_opy_)