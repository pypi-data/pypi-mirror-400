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
class bstack11ll1111ll_opy_:
    def __init__(self, handler):
        self._1llll1l1111l_opy_ = None
        self.handler = handler
        self._1llll1l11111_opy_ = self.bstack1llll11lllll_opy_()
        self.patch()
    def patch(self):
        self._1llll1l1111l_opy_ = self._1llll1l11111_opy_.execute
        self._1llll1l11111_opy_.execute = self.bstack1llll1l111l1_opy_()
    def bstack1llll1l111l1_opy_(self):
        def execute(this, driver_command, *args, **kwargs):
            self.handler(bstack11ll1_opy_ (u"ࠤࡥࡩ࡫ࡵࡲࡦࠤ⃧"), driver_command, None, this, args)
            response = self._1llll1l1111l_opy_(this, driver_command, *args, **kwargs)
            self.handler(bstack11ll1_opy_ (u"ࠥࡥ࡫ࡺࡥࡳࠤ⃨"), driver_command, response)
            return response
        return execute
    def reset(self):
        self._1llll1l11111_opy_.execute = self._1llll1l1111l_opy_
    @staticmethod
    def bstack1llll11lllll_opy_():
        from selenium.webdriver.remote.webdriver import WebDriver
        return WebDriver