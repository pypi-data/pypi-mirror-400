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
class bstack1lll111l11_opy_:
    def __init__(self, handler):
        self._1llll1l111l1_opy_ = None
        self.handler = handler
        self._1llll1l11111_opy_ = self.bstack1llll1l1111l_opy_()
        self.patch()
    def patch(self):
        self._1llll1l111l1_opy_ = self._1llll1l11111_opy_.execute
        self._1llll1l11111_opy_.execute = self.bstack1llll11lllll_opy_()
    def bstack1llll11lllll_opy_(self):
        def execute(this, driver_command, *args, **kwargs):
            self.handler(bstack11l1l_opy_ (u"ࠣࡤࡨࡪࡴࡸࡥ⃦ࠣ"), driver_command, None, this, args)
            response = self._1llll1l111l1_opy_(this, driver_command, *args, **kwargs)
            self.handler(bstack11l1l_opy_ (u"ࠤࡤࡪࡹ࡫ࡲࠣ⃧"), driver_command, response)
            return response
        return execute
    def reset(self):
        self._1llll1l11111_opy_.execute = self._1llll1l111l1_opy_
    @staticmethod
    def bstack1llll1l1111l_opy_():
        from selenium.webdriver.remote.webdriver import WebDriver
        return WebDriver