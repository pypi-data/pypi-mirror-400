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
from time import sleep
from datetime import datetime
from urllib.parse import urlencode
from bstack_utils.bstack11l1ll1l1l1_opy_ import bstack11l1ll1l11l_opy_
from bstack_utils.constants import *
import json
class bstack1lll111l11_opy_:
    def __init__(self, bstack11lllll1l_opy_, bstack11l1ll111ll_opy_):
        self.bstack11lllll1l_opy_ = bstack11lllll1l_opy_
        self.bstack11l1ll111ll_opy_ = bstack11l1ll111ll_opy_
        self.bstack11l1ll11ll1_opy_ = None
    def __call__(self):
        bstack11l1ll11l1l_opy_ = {}
        while True:
            self.bstack11l1ll11ll1_opy_ = bstack11l1ll11l1l_opy_.get(
                bstack11ll1_opy_ (u"ࠨࡰࡨࡼࡹࡥࡰࡰ࡮࡯ࡣࡹ࡯࡭ࡦࠩ᠑"),
                int(datetime.now().timestamp() * 1000)
            )
            bstack11l1ll11l11_opy_ = self.bstack11l1ll11ll1_opy_ - int(datetime.now().timestamp() * 1000)
            if bstack11l1ll11l11_opy_ > 0:
                sleep(bstack11l1ll11l11_opy_ / 1000)
            params = {
                bstack11ll1_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡳࡷࡱࡣࡺࡻࡩࡥࠩ᠒"): self.bstack11lllll1l_opy_,
                bstack11ll1_opy_ (u"ࠪࡸ࡮ࡳࡥࡴࡶࡤࡱࡵ࠭᠓"): int(datetime.now().timestamp() * 1000)
            }
            bstack11l1ll1l111_opy_ = bstack11ll1_opy_ (u"ࠦ࡭ࡺࡴࡱࡵ࠽࠳࠴ࠨ᠔") + bstack11l1ll1l1ll_opy_ + bstack11ll1_opy_ (u"ࠧ࠵ࡡࡶࡶࡲࡱࡦࡺࡥ࠰ࡣࡳ࡭࠴ࡼ࠱࠰ࠤ᠕")
            if self.bstack11l1ll111ll_opy_.lower() == bstack11ll1_opy_ (u"ࠨࡲࡦࡵࡸࡰࡹࡹࠢ᠖"):
                bstack11l1ll11l1l_opy_ = bstack11l1ll1l11l_opy_.results(bstack11l1ll1l111_opy_, params)
            else:
                bstack11l1ll11l1l_opy_ = bstack11l1ll1l11l_opy_.bstack11l1ll11lll_opy_(bstack11l1ll1l111_opy_, params)
            if str(bstack11l1ll11l1l_opy_.get(bstack11ll1_opy_ (u"ࠧࡴࡶࡤࡸࡺࡹࠧ᠗"), bstack11ll1_opy_ (u"ࠨ࠴࠳࠴ࠬ᠘"))) != bstack11ll1_opy_ (u"ࠩ࠷࠴࠹࠭᠙"):
                break
        return bstack11l1ll11l1l_opy_.get(bstack11ll1_opy_ (u"ࠪࡨࡦࡺࡡࠨ᠚"), bstack11l1ll11l1l_opy_)