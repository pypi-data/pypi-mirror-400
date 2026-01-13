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
import multiprocessing
import os
import json
from time import sleep
import time
import bstack_utils.accessibility as bstack1l1ll11l1l_opy_
from browserstack_sdk.bstack1ll1lll1_opy_ import *
from bstack_utils.config import Config
from bstack_utils.messages import bstack11lll1l1l1_opy_, bstack111111l111_opy_
from bstack_utils.bstack11l111l1_opy_ import bstack1lll1lll_opy_
from bstack_utils.constants import bstack111111ll1l_opy_
from bstack_utils.bstack11ll1ll1l1_opy_ import bstack1l1111111l_opy_
from bstack_utils.bstack1111111ll1_opy_ import bstack11111l1111_opy_
class bstack1lll1l11ll_opy_:
    def __init__(self, args, logger, bstack1llllllllll_opy_, bstack1llllll1ll1_opy_):
        self.args = args
        self.logger = logger
        self.bstack1llllllllll_opy_ = bstack1llllllllll_opy_
        self.bstack1llllll1ll1_opy_ = bstack1llllll1ll1_opy_
        self._prepareconfig = None
        self.Config = None
        self.runner = None
        self.bstack111ll111l_opy_ = []
        self.bstack11111l111l_opy_ = []
        self.bstack1l1l11ll11_opy_ = []
        self.bstack111111llll_opy_ = self.bstack1l1lll1111_opy_()
        self.bstack11l1l1l1l_opy_ = -1
    def bstack1l11l1l1l_opy_(self, bstack1lllllllll1_opy_):
        self.parse_args()
        self.bstack1111111l1l_opy_()
        self.bstack111111l1ll_opy_(bstack1lllllllll1_opy_)
        self.bstack1llllll11ll_opy_()
    def bstack11llll1ll_opy_(self):
        bstack11ll1ll1l1_opy_ = bstack1l1111111l_opy_.bstack1l1l1111_opy_(self.bstack1llllllllll_opy_, self.logger)
        if bstack11ll1ll1l1_opy_ is None:
            self.logger.warn(bstack11ll1_opy_ (u"ࠨࡏࡳࡥ࡫ࡩࡸࡺࡲࡢࡶ࡬ࡳࡳࠦࡨࡢࡰࡧࡰࡪࡸࠠࡪࡵࠣࡲࡴࡺࠠࡪࡰ࡬ࡸ࡮ࡧ࡬ࡪࡼࡨࡨ࠳ࠦࡓ࡬࡫ࡳࡴ࡮ࡴࡧࠡࡱࡵࡧ࡭࡫ࡳࡵࡴࡤࡸ࡮ࡵ࡮࠯ࠤႦ"))
            return
        bstack1llllll1l11_opy_ = False
        bstack11ll1ll1l1_opy_.bstack1lllllll111_opy_(bstack11ll1_opy_ (u"ࠢࡦࡰࡤࡦࡱ࡫ࡤࠣႧ"), bstack11ll1ll1l1_opy_.bstack1l1l1ll11_opy_())
        start_time = time.time()
        if bstack11ll1ll1l1_opy_.bstack1l1l1ll11_opy_():
            test_files = self.bstack1111111l11_opy_()
            bstack1llllll1l11_opy_ = True
            bstack1llllll1l1l_opy_ = bstack11ll1ll1l1_opy_.bstack111111l1l1_opy_(test_files)
            if bstack1llllll1l1l_opy_:
                self.bstack111ll111l_opy_ = [os.path.normpath(item) for item in bstack1llllll1l1l_opy_]
                self.__111111lll1_opy_()
                bstack11ll1ll1l1_opy_.bstack1lllllll1l1_opy_(bstack1llllll1l11_opy_)
                self.logger.info(bstack11ll1_opy_ (u"ࠣࡖࡨࡷࡹࡹࠠࡳࡧࡲࡶࡩ࡫ࡲࡦࡦࠣࡹࡸ࡯࡮ࡨࠢࡲࡶࡨ࡮ࡥࡴࡶࡵࡥࡹ࡯࡯࡯࠼ࠣࡿࢂࠨႨ").format(self.bstack111ll111l_opy_))
            else:
                self.logger.info(bstack11ll1_opy_ (u"ࠤࡑࡳࠥࡺࡥࡴࡶࠣࡪ࡮ࡲࡥࡴࠢࡺࡩࡷ࡫ࠠࡳࡧࡲࡶࡩ࡫ࡲࡦࡦࠣࡦࡾࠦ࡯ࡳࡥ࡫ࡩࡸࡺࡲࡢࡶ࡬ࡳࡳ࠴ࠢႩ"))
        bstack11ll1ll1l1_opy_.bstack1lllllll111_opy_(bstack11ll1_opy_ (u"ࠥࡸ࡮ࡳࡥࡕࡣ࡮ࡩࡳ࡚࡯ࡂࡲࡳࡰࡾࠨႪ"), int((time.time() - start_time) * 1000)) # bstack1111111111_opy_ to bstack11111l11l1_opy_
    def __111111lll1_opy_(self):
        bstack11ll1_opy_ (u"ࠦࠧࠨࠊࠡࠢࠣࠤࠥࠦࠠࠡࡔࡨࡴࡱࡧࡣࡦࠢࡷࡩࡸࡺࠠࡧ࡫࡯ࡩࠥࡶࡡࡵࡪࡶࠤ࡮ࡴࠠࡄࡎࡌࠤ࡫ࡲࡡࡨࡵࠣࡻ࡮ࡺࡨࠡࡱࡵࡧ࡭࡫ࡳࡵࡴࡤࡸࡪࡪࠠࡧ࡫࡯ࡩࠥࡶࡡࡵࡪࡶ࠲ࠏࠦࠠࠡࠢࠣࠤࠥࠦࡏࡳࡥ࡫ࡩࡸࡺࡲࡢࡶ࡬ࡳࡳࠦࡳࡦࡴࡹࡩࡷࠦࡲࡦࡶࡸࡶࡳࡹࠠࡳࡧࡲࡶࡩ࡫ࡲࡦࡦࠣࡪ࡮ࡲࡥࠡࡰࡤࡱࡪࡹࠬࠡࡣࡱࡨࠥࡽࡥࠡࡵ࡬ࡱࡵࡲࡹࠡࡷࡳࡨࡦࡺࡥࠋࠢࠣࠤࠥࠦࠠࠡࠢࡷ࡬ࡪࠦࡃࡍࡋࠣࡥࡷ࡭ࡳࠡࡶࡲࠤࡺࡹࡥࠡࡶ࡫ࡳࡸ࡫ࠠࡧ࡫࡯ࡩࡸ࠴ࠠࡖࡵࡨࡶࠬࡹࠠࡧ࡫࡯ࡸࡪࡸࡩ࡯ࡩࠣࡪࡱࡧࡧࡴࠢࠫ࠱ࡲ࠲ࠠ࠮࡭ࠬࠤࡷ࡫࡭ࡢ࡫ࡱࠎࠥࠦࠠࠡࠢࠣࠤࠥ࡯࡮ࡵࡣࡦࡸࠥࡧ࡮ࡥࠢࡺ࡭ࡱࡲࠠࡣࡧࠣࡥࡵࡶ࡬ࡪࡧࡧࠤࡳࡧࡴࡶࡴࡤࡰࡱࡿࠠࡥࡷࡵ࡭ࡳ࡭ࠠࡱࡻࡷࡩࡸࡺࠠࡤࡱ࡯ࡰࡪࡩࡴࡪࡱࡱ࠲ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠢࠣࠤႫ")
        try:
            if not self.bstack111ll111l_opy_:
                self.logger.debug(bstack11ll1_opy_ (u"ࠧࡔ࡯ࠡࡱࡵࡧ࡭࡫ࡳࡵࡴࡤࡸࡪࡪࠠࡧ࡫࡯ࡩࡸࠦࡰࡢࡶ࡫ࠤࡹࡵࠠࡴࡧࡷࠦႬ"))
                return
            bstack11111111l1_opy_ = []
            for flag in self.bstack11111l111l_opy_:
                if flag.startswith(bstack11ll1_opy_ (u"࠭࠭ࠨႭ")):
                    bstack11111111l1_opy_.append(flag)
                    continue
                bstack1llllll111l_opy_ = False
                if bstack11ll1_opy_ (u"ࠧ࠻࠼ࠪႮ") in flag:
                    bstack11111111ll_opy_ = flag.split(bstack11ll1_opy_ (u"ࠨ࠼࠽ࠫႯ"), 1)[0]
                    if os.path.exists(bstack11111111ll_opy_):
                        bstack1llllll111l_opy_ = True
                elif os.path.exists(flag):
                    if os.path.isdir(flag) or (os.path.isfile(flag) and flag.endswith(bstack11ll1_opy_ (u"ࠩ࠱ࡴࡾ࠭Ⴐ"))):
                        bstack1llllll111l_opy_ = True
                if not bstack1llllll111l_opy_:
                    bstack11111111l1_opy_.append(flag)
            bstack11111111l1_opy_.extend(self.bstack111ll111l_opy_)
            self.bstack11111l111l_opy_ = bstack11111111l1_opy_
        except Exception as e:
            self.logger.error(bstack11ll1_opy_ (u"ࠥࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡷࡩ࡫࡯ࡩࠥࡹࡥࡵࡶ࡬ࡲ࡬ࠦ࡯ࡳࡥ࡫ࡩࡸࡺࡲࡢࡶࡨࡨࠥࡹࡥ࡭ࡧࡦࡸࡴࡸࡳ࠻ࠢࡾࢁࠧႱ").format(str(e)))
    @staticmethod
    def version():
        import pytest
        return pytest.__version__
    @staticmethod
    def bstack1llllll1lll_opy_():
        return bstack11111l1111_opy_(bstack11ll1_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࡣࡸ࡫࡬ࡦࡰ࡬ࡹࡲ࠭Ⴒ"))
    def bstack1llllllll11_opy_(self, arg):
        if arg in self.args:
            i = self.args.index(arg)
            self.args.pop(i + 1)
            self.args.pop(i)
    def parse_args(self):
        self.bstack11l1l1l1l_opy_ = -1
        if self.bstack1llllll1ll1_opy_ and bstack11ll1_opy_ (u"ࠬࡶࡡࡳࡣ࡯ࡰࡪࡲࡳࡑࡧࡵࡔࡱࡧࡴࡧࡱࡵࡱࠬႳ") in self.bstack1llllllllll_opy_:
            self.bstack11l1l1l1l_opy_ = int(self.bstack1llllllllll_opy_[bstack11ll1_opy_ (u"࠭ࡰࡢࡴࡤࡰࡱ࡫࡬ࡴࡒࡨࡶࡕࡲࡡࡵࡨࡲࡶࡲ࠭Ⴔ")])
        try:
            bstack1lllllll11l_opy_ = [bstack11ll1_opy_ (u"ࠧ࠮࠯ࡧࡶ࡮ࡼࡥࡳࠩႵ"), bstack11ll1_opy_ (u"ࠨ࠯࠰ࡴࡱࡻࡧࡪࡰࡶࠫႶ"), bstack11ll1_opy_ (u"ࠩ࠰ࡴࠬႷ")]
            if self.bstack11l1l1l1l_opy_ >= 0:
                bstack1lllllll11l_opy_.extend([bstack11ll1_opy_ (u"ࠪ࠱࠲ࡴࡵ࡮ࡲࡵࡳࡨ࡫ࡳࡴࡧࡶࠫႸ"), bstack11ll1_opy_ (u"ࠫ࠲ࡴࠧႹ")])
            for arg in bstack1lllllll11l_opy_:
                self.bstack1llllllll11_opy_(arg)
        except Exception as exc:
            self.logger.error(str(exc))
    def get_args(self):
        return self.args
    def bstack1111111l1l_opy_(self):
        bstack11111l111l_opy_ = [os.path.normpath(item) for item in self.args]
        self.bstack11111l111l_opy_ = bstack11111l111l_opy_
        return self.bstack11111l111l_opy_
    def bstack1l111l11_opy_(self):
        try:
            from _pytest.config import _prepareconfig
            from _pytest.config import Config
            from _pytest import runner
            if not self.bstack1llllll1lll_opy_():
                self.logger.warning(bstack111111l111_opy_)
            self._prepareconfig = _prepareconfig
            self.Config = Config
            self.runner = runner
        except Exception as e:
            self.logger.warning(bstack11ll1_opy_ (u"ࠧࠫࡳ࠻ࠢࠨࡷࠧႺ"), bstack11lll1l1l1_opy_, str(e))
    def bstack111111l1ll_opy_(self, bstack1lllllllll1_opy_):
        bstack1l1l1ll1l_opy_ = Config.bstack1l1l1111_opy_()
        if bstack1lllllllll1_opy_:
            self.bstack11111l111l_opy_.append(bstack11ll1_opy_ (u"࠭࠭࠮ࡵ࡮࡭ࡵ࡙ࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧࠪႻ"))
            self.bstack11111l111l_opy_.append(bstack11ll1_opy_ (u"ࠧࡕࡴࡸࡩࠬႼ"))
        if bstack1l1l1ll1l_opy_.bstack1llllllll1l_opy_():
            self.bstack11111l111l_opy_.append(bstack11ll1_opy_ (u"ࠨ࠯࠰ࡷࡰ࡯ࡰࡔࡧࡶࡷ࡮ࡵ࡮ࡔࡶࡤࡸࡺࡹࠧႽ"))
            self.bstack11111l111l_opy_.append(bstack11ll1_opy_ (u"ࠩࡗࡶࡺ࡫ࠧႾ"))
        self.bstack11111l111l_opy_.append(bstack11ll1_opy_ (u"ࠪ࠱ࡵ࠭Ⴟ"))
        self.bstack11111l111l_opy_.append(bstack11ll1_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࡣࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡳࡰࡺ࡭ࡩ࡯ࠩჀ"))
        self.bstack11111l111l_opy_.append(bstack11ll1_opy_ (u"ࠬ࠳࠭ࡥࡴ࡬ࡺࡪࡸࠧჁ"))
        self.bstack11111l111l_opy_.append(bstack11ll1_opy_ (u"࠭ࡣࡩࡴࡲࡱࡪ࠭Ⴢ"))
        if self.bstack11l1l1l1l_opy_ > 1:
            self.bstack11111l111l_opy_.append(bstack11ll1_opy_ (u"ࠧ࠮ࡰࠪჃ"))
            self.bstack11111l111l_opy_.append(str(self.bstack11l1l1l1l_opy_))
    def bstack1llllll11ll_opy_(self):
        if bstack1lll1lll_opy_.bstack1ll11l11ll_opy_(self.bstack1llllllllll_opy_):
             self.bstack11111l111l_opy_ += [
                bstack111111ll1l_opy_.get(bstack11ll1_opy_ (u"ࠨࡴࡨࡶࡺࡴࠧჄ")), str(bstack1lll1lll_opy_.bstack1lllllll1l_opy_(self.bstack1llllllllll_opy_)),
                bstack111111ll1l_opy_.get(bstack11ll1_opy_ (u"ࠩࡧࡩࡱࡧࡹࠨჅ")), str(bstack111111ll1l_opy_.get(bstack11ll1_opy_ (u"ࠪࡶࡪࡸࡵ࡯࠯ࡧࡩࡱࡧࡹࠨ჆")))
            ]
    def bstack1llllll1111_opy_(self):
        bstack1l1l11ll11_opy_ = []
        for spec in self.bstack111ll111l_opy_:
            bstack1ll1l1l1_opy_ = [spec]
            bstack1ll1l1l1_opy_ += self.bstack11111l111l_opy_
            bstack1l1l11ll11_opy_.append(bstack1ll1l1l1_opy_)
        self.bstack1l1l11ll11_opy_ = bstack1l1l11ll11_opy_
        return bstack1l1l11ll11_opy_
    def bstack1l1lll1111_opy_(self):
        try:
            from pytest_bdd import reporting
            self.bstack111111llll_opy_ = True
            return True
        except Exception as e:
            self.bstack111111llll_opy_ = False
        return self.bstack111111llll_opy_
    def bstack1l11111l_opy_(self):
        bstack11ll1_opy_ (u"ࠦࠧࠨࠊࠡࠢࠣࠤࠥࠦࠠࠡࡉࡨࡸࠥࡺࡨࡦࠢࡦࡳࡺࡴࡴࠡࡱࡩࠤࡹ࡫ࡳࡵࡵࠣࡻ࡮ࡺࡨࡰࡷࡷࠤࡷࡻ࡮࡯࡫ࡱ࡫ࠥࡺࡨࡦ࡯ࠣࡹࡸ࡯࡮ࡨࠢࡳࡽࡹ࡫ࡳࡵࠢࡦࡳࡱࡲࡥࡤࡶ࡬ࡳࡳ࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࡔࡨࡸࡺࡸ࡮ࡴ࠼ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡ࡫ࡱࡸ࠿ࠦࡔࡩࡧࠣࡸࡴࡺࡡ࡭ࠢࡱࡹࡲࡨࡥࡳࠢࡲࡪࠥࡺࡥࡴࡶࡶࠤࡨࡵ࡬࡭ࡧࡦࡸࡪࡪ࠮ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠥࠦࠧჇ")
        try:
            from browserstack_sdk.bstack11111ll1l1_opy_ import bstack11111lllll_opy_
            bstack1llllll11l1_opy_ = bstack11111lllll_opy_(bstack11111lll1l_opy_=self.bstack11111l111l_opy_)
            if not bstack1llllll11l1_opy_.get(bstack11ll1_opy_ (u"ࠬࡹࡵࡤࡥࡨࡷࡸ࠭჈"), False):
                self.logger.error(bstack11ll1_opy_ (u"ࠨࡔࡦࡵࡷࠤࡨࡵࡵ࡯ࡶࠣࡧࡴࡲ࡬ࡦࡥࡷ࡭ࡴࡴࠠࡧࡣ࡬ࡰࡪࡪ࠺ࠡࡽࢀࠦ჉").format(bstack1llllll11l1_opy_.get(bstack11ll1_opy_ (u"ࠧࡦࡴࡵࡳࡷ࠭჊"), bstack11ll1_opy_ (u"ࠨࡗࡱ࡯ࡳࡵࡷ࡯ࠢࡨࡶࡷࡵࡲࠨ჋"))))
                return 0
            count = bstack1llllll11l1_opy_.get(bstack11ll1_opy_ (u"ࠩࡦࡳࡺࡴࡴࠨ჌"), 0)
            self.logger.info(bstack11ll1_opy_ (u"ࠥࡘࡴࡺࡡ࡭ࠢࡷࡩࡸࡺࡳࠡࡥࡲࡰࡱ࡫ࡣࡵࡧࡧ࠾ࠥࢁࡽࠣჍ").format(count))
            return count
        except Exception as e:
            self.logger.error(bstack11ll1_opy_ (u"ࠦࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡸࡪ࡬ࡰࡪࠦࡧࡦࡶࡷ࡭ࡳ࡭ࠠࡵࡧࡶࡸࠥࡩ࡯ࡶࡰࡷ࠾ࠥࢁࡽࠣ჎").format(e))
            return 0
    def bstack1ll1l1l1ll_opy_(self, bstack1111111lll_opy_, bstack1l11l1l1l_opy_):
        bstack1l11l1l1l_opy_[bstack11ll1_opy_ (u"ࠬࡉࡏࡏࡈࡌࡋࠬ჏")] = self.bstack1llllllllll_opy_
        multiprocessing.set_start_method(bstack11ll1_opy_ (u"࠭ࡳࡱࡣࡺࡲࠬა"))
        bstack1ll1ll11l1_opy_ = []
        manager = multiprocessing.Manager()
        bstack111111111l_opy_ = manager.list()
        if bstack11ll1_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪბ") in self.bstack1llllllllll_opy_:
            for index, platform in enumerate(self.bstack1llllllllll_opy_[bstack11ll1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫგ")]):
                bstack1ll1ll11l1_opy_.append(multiprocessing.Process(name=str(index),
                                                            target=bstack1111111lll_opy_,
                                                            args=(self.bstack11111l111l_opy_, bstack1l11l1l1l_opy_, bstack111111111l_opy_)))
            bstack11111l11ll_opy_ = len(self.bstack1llllllllll_opy_[bstack11ll1_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬდ")])
        else:
            bstack1ll1ll11l1_opy_.append(multiprocessing.Process(name=str(0),
                                                        target=bstack1111111lll_opy_,
                                                        args=(self.bstack11111l111l_opy_, bstack1l11l1l1l_opy_, bstack111111111l_opy_)))
            bstack11111l11ll_opy_ = 1
        i = 0
        for t in bstack1ll1ll11l1_opy_:
            os.environ[bstack11ll1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡓࡐࡆ࡚ࡆࡐࡔࡐࡣࡎࡔࡄࡆ࡚ࠪე")] = str(i)
            if bstack11ll1_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧვ") in self.bstack1llllllllll_opy_:
                os.environ[bstack11ll1_opy_ (u"ࠬࡉࡕࡓࡔࡈࡒ࡙ࡥࡐࡍࡃࡗࡊࡔࡘࡍࡠࡆࡄࡘࡆ࠭ზ")] = json.dumps(self.bstack1llllllllll_opy_[bstack11ll1_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩთ")][i % bstack11111l11ll_opy_])
            i += 1
            t.start()
        for t in bstack1ll1ll11l1_opy_:
            t.join()
        return list(bstack111111111l_opy_)
    @staticmethod
    def bstack1l1lllll1l_opy_(driver, bstack1lllllll1ll_opy_, logger, item=None, wait=False):
        item = item or getattr(threading.current_thread(), bstack11ll1_opy_ (u"ࠧࡤࡷࡵࡶࡪࡴࡴࡠࡶࡨࡷࡹࡥࡩࡵࡧࡰࠫი"), None)
        if item and getattr(item, bstack11ll1_opy_ (u"ࠨࡡࡤ࠵࠶ࡿ࡟ࡵࡧࡶࡸࡤࡩࡡࡴࡧࠪკ"), None) and not getattr(item, bstack11ll1_opy_ (u"ࠩࡢࡥ࠶࠷ࡹࡠࡵࡷࡳࡵࡥࡤࡰࡰࡨࠫლ"), False):
            logger.info(
                bstack11ll1_opy_ (u"ࠥࡅࡺࡺ࡯࡮ࡣࡷࡩࠥࡺࡥࡴࡶࠣࡧࡦࡹࡥࠡࡧࡻࡩࡨࡻࡴࡪࡱࡱࠤ࡭ࡧࡳࠡࡧࡱࡨࡪࡪ࠮ࠡࡒࡵࡳࡨ࡫ࡳࡴ࡫ࡱ࡫ࠥ࡬࡯ࡳࠢࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠢࡷࡩࡸࡺࡩ࡯ࡩࠣ࡭ࡸࠦࡵ࡯ࡦࡨࡶࡼࡧࡹ࠯ࠤმ"))
            bstack111111l11l_opy_ = item.cls.__name__ if not item.cls is None else None
            bstack1l1ll11l1l_opy_.bstack1lll1111ll_opy_(driver, item.name, item.path)
            item._a11y_stop_done = True
            if wait:
                sleep(2)
    def bstack1111111l11_opy_(self):
        bstack11ll1_opy_ (u"ࠦࠧࠨࠊࠡࠢࠣࠤࠥࠦࠠࠡࡔࡨࡸࡺࡸ࡮ࡴࠢࡷ࡬ࡪࠦ࡬ࡪࡵࡷࠤࡴ࡬ࠠࡵࡧࡶࡸࠥ࡬ࡩ࡭ࡧࡶࠤࡹࡵࠠࡣࡧࠣࡩࡽ࡫ࡣࡶࡶࡨࡨ࠳ࠐࠠࠡࠢࠣࠤࠥࠦࠠࠣࠤࠥნ")
        try:
            from browserstack_sdk.bstack11111ll1l1_opy_ import bstack11111lllll_opy_
            bstack111111ll11_opy_ = bstack11111lllll_opy_(bstack11111lll1l_opy_=self.bstack11111l111l_opy_)
            if not bstack111111ll11_opy_.get(bstack11ll1_opy_ (u"ࠬࡹࡵࡤࡥࡨࡷࡸ࠭ო"), False):
                self.logger.error(bstack11ll1_opy_ (u"ࠨࡔࡦࡵࡷࠤ࡫࡯࡬ࡦࠢࡦࡳࡱࡲࡥࡤࡶ࡬ࡳࡳࠦࡦࡢ࡫࡯ࡩࡩࡀࠠࡼࡿࠥპ").format(bstack111111ll11_opy_.get(bstack11ll1_opy_ (u"ࠧࡦࡴࡵࡳࡷ࠭ჟ"), bstack11ll1_opy_ (u"ࠨࡗࡱ࡯ࡳࡵࡷ࡯ࠢࡨࡶࡷࡵࡲࠨრ"))))
                return []
            test_files = bstack111111ll11_opy_.get(bstack11ll1_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡧ࡫࡯ࡩࡸ࠭ს"), [])
            count = bstack111111ll11_opy_.get(bstack11ll1_opy_ (u"ࠪࡧࡴࡻ࡮ࡵࠩტ"), 0)
            self.logger.debug(bstack11ll1_opy_ (u"ࠦࡈࡵ࡬࡭ࡧࡦࡸࡪࡪࠠࡼࡿࠣࡸࡪࡹࡴࡴࠢ࡬ࡲࠥࢁࡽࠡࡨ࡬ࡰࡪࡹࠢუ").format(count, len(test_files)))
            return test_files
        except Exception as e:
            self.logger.error(bstack11ll1_opy_ (u"ࠧࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡࡦࡸࡶ࡮ࡴࡧࠡࡶࡨࡷࡹࠦࡦࡪ࡮ࡨࡷࠥࡩ࡯࡭࡮ࡨࡧࡹ࡯࡯࡯࠼ࠣࡿࢂࠨფ").format(e))
            return []