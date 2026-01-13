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
class RobotHandler():
    def __init__(self, args, logger, bstack1llllll1ll1_opy_, bstack1111111lll_opy_):
        self.args = args
        self.logger = logger
        self.bstack1llllll1ll1_opy_ = bstack1llllll1ll1_opy_
        self.bstack1111111lll_opy_ = bstack1111111lll_opy_
    @staticmethod
    def version():
        import robot
        return robot.__version__
    @staticmethod
    def bstack1111l1ll11_opy_(bstack1lllll1ll11_opy_):
        bstack1lllll1l1ll_opy_ = []
        if bstack1lllll1ll11_opy_:
            tokens = str(os.path.basename(bstack1lllll1ll11_opy_)).split(bstack11l1l_opy_ (u"ࠧࡥࠢძ"))
            camelcase_name = bstack11l1l_opy_ (u"ࠨࠠࠣწ").join(t.title() for t in tokens)
            suite_name, bstack1lllll1l1l1_opy_ = os.path.splitext(camelcase_name)
            bstack1lllll1l1ll_opy_.append(suite_name)
        return bstack1lllll1l1ll_opy_
    @staticmethod
    def bstack1lllll1ll1l_opy_(typename):
        if bstack11l1l_opy_ (u"ࠢࡂࡵࡶࡩࡷࡺࡩࡰࡰࠥჭ") in typename:
            return bstack11l1l_opy_ (u"ࠣࡃࡶࡷࡪࡸࡴࡪࡱࡱࡉࡷࡸ࡯ࡳࠤხ")
        return bstack11l1l_opy_ (u"ࠤࡘࡲ࡭ࡧ࡮ࡥ࡮ࡨࡨࡊࡸࡲࡰࡴࠥჯ")