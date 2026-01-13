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
import json
import multiprocessing
import os
from bstack_utils.config import Config
class bstack1l1ll11l1l_opy_():
  def __init__(self, args, logger, bstack1llllll1ll1_opy_, bstack1111111lll_opy_, bstack1lllll1lll1_opy_):
    self.args = args
    self.logger = logger
    self.bstack1llllll1ll1_opy_ = bstack1llllll1ll1_opy_
    self.bstack1111111lll_opy_ = bstack1111111lll_opy_
    self.bstack1lllll1lll1_opy_ = bstack1lllll1lll1_opy_
  def bstack1llll1l1l_opy_(self, bstack111111l111_opy_, bstack1lll1l1ll1_opy_, bstack1lllll1llll_opy_=False):
    bstack1l111111l_opy_ = []
    manager = multiprocessing.Manager()
    bstack1llllllllll_opy_ = manager.list()
    bstack1l1ll11111_opy_ = Config.bstack11l1l11ll1_opy_()
    if bstack1lllll1llll_opy_:
      for index, platform in enumerate(self.bstack1llllll1ll1_opy_[bstack11l1l_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨფ")]):
        if index == 0:
          bstack1lll1l1ll1_opy_[bstack11l1l_opy_ (u"࠭ࡦࡪ࡮ࡨࡣࡳࡧ࡭ࡦࠩქ")] = self.args
        bstack1l111111l_opy_.append(multiprocessing.Process(name=str(index),
                                                    target=bstack111111l111_opy_,
                                                    args=(bstack1lll1l1ll1_opy_, bstack1llllllllll_opy_)))
    else:
      for index, platform in enumerate(self.bstack1llllll1ll1_opy_[bstack11l1l_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪღ")]):
        bstack1l111111l_opy_.append(multiprocessing.Process(name=str(index),
                                                    target=bstack111111l111_opy_,
                                                    args=(bstack1lll1l1ll1_opy_, bstack1llllllllll_opy_)))
    i = 0
    for t in bstack1l111111l_opy_:
      try:
        if bstack1l1ll11111_opy_.get_property(bstack11l1l_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫ࡠࡵࡨࡷࡸ࡯࡯࡯ࠩყ")):
          os.environ[bstack11l1l_opy_ (u"ࠩࡆ࡙ࡗࡘࡅࡏࡖࡢࡔࡑࡇࡔࡇࡑࡕࡑࡤࡊࡁࡕࡃࠪშ")] = json.dumps(self.bstack1llllll1ll1_opy_[bstack11l1l_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ჩ")][i % self.bstack1lllll1lll1_opy_])
      except Exception as e:
        self.logger.debug(bstack11l1l_opy_ (u"ࠦࡊࡸࡲࡰࡴࠣࡻ࡭࡯࡬ࡦࠢࡶࡸࡴࡸࡩ࡯ࡩࠣࡧࡺࡸࡲࡦࡰࡷࠤࡵࡲࡡࡵࡨࡲࡶࡲࠦࡤࡦࡶࡤ࡭ࡱࡹ࠺ࠡࡽࢀࠦც").format(str(e)))
      i += 1
      t.start()
    for t in bstack1l111111l_opy_:
      t.join()
    return list(bstack1llllllllll_opy_)