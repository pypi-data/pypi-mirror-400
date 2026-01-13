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
class RobotHandler():
    def __init__(self, args, logger, bstack1llllllllll_opy_, bstack1llllll1ll1_opy_):
        self.args = args
        self.logger = logger
        self.bstack1llllllllll_opy_ = bstack1llllllllll_opy_
        self.bstack1llllll1ll1_opy_ = bstack1llllll1ll1_opy_
    @staticmethod
    def version():
        import robot
        return robot.__version__
    @staticmethod
    def bstack111l11l1l1_opy_(bstack1lllll1l1l1_opy_):
        bstack1lllll1l1ll_opy_ = []
        if bstack1lllll1l1l1_opy_:
            tokens = str(os.path.basename(bstack1lllll1l1l1_opy_)).split(bstack11ll1_opy_ (u"ࠨ࡟ࠣწ"))
            camelcase_name = bstack11ll1_opy_ (u"ࠢࠡࠤჭ").join(t.title() for t in tokens)
            suite_name, bstack1lllll1ll1l_opy_ = os.path.splitext(camelcase_name)
            bstack1lllll1l1ll_opy_.append(suite_name)
        return bstack1lllll1l1ll_opy_
    @staticmethod
    def bstack1lllll1ll11_opy_(typename):
        if bstack11ll1_opy_ (u"ࠣࡃࡶࡷࡪࡸࡴࡪࡱࡱࠦხ") in typename:
            return bstack11ll1_opy_ (u"ࠤࡄࡷࡸ࡫ࡲࡵ࡫ࡲࡲࡊࡸࡲࡰࡴࠥჯ")
        return bstack11ll1_opy_ (u"࡙ࠥࡳ࡮ࡡ࡯ࡦ࡯ࡩࡩࡋࡲࡳࡱࡵࠦჰ")