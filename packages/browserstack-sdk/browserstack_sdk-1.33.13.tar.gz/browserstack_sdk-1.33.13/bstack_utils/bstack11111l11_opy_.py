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
from time import sleep
from datetime import datetime
from urllib.parse import urlencode
from bstack_utils.bstack11l1ll11lll_opy_ import bstack11l1ll1l1ll_opy_
from bstack_utils.constants import *
import json
class bstack11lllll1_opy_:
    def __init__(self, bstack1lll111lll_opy_, bstack11l1ll1l111_opy_):
        self.bstack1lll111lll_opy_ = bstack1lll111lll_opy_
        self.bstack11l1ll1l111_opy_ = bstack11l1ll1l111_opy_
        self.bstack11l1ll11ll1_opy_ = None
    def __call__(self):
        bstack11l1ll11l11_opy_ = {}
        while True:
            self.bstack11l1ll11ll1_opy_ = bstack11l1ll11l11_opy_.get(
                bstack11l1l_opy_ (u"ࠧ࡯ࡧࡻࡸࡤࡶ࡯࡭࡮ࡢࡸ࡮ࡳࡥࠨ᠐"),
                int(datetime.now().timestamp() * 1000)
            )
            bstack11l1ll111ll_opy_ = self.bstack11l1ll11ll1_opy_ - int(datetime.now().timestamp() * 1000)
            if bstack11l1ll111ll_opy_ > 0:
                sleep(bstack11l1ll111ll_opy_ / 1000)
            params = {
                bstack11l1l_opy_ (u"ࠨࡶࡨࡷࡹࡥࡲࡶࡰࡢࡹࡺ࡯ࡤࠨ᠑"): self.bstack1lll111lll_opy_,
                bstack11l1l_opy_ (u"ࠩࡷ࡭ࡲ࡫ࡳࡵࡣࡰࡴࠬ᠒"): int(datetime.now().timestamp() * 1000)
            }
            bstack11l1ll11l1l_opy_ = bstack11l1l_opy_ (u"ࠥ࡬ࡹࡺࡰࡴ࠼࠲࠳ࠧ᠓") + bstack11l1ll1l11l_opy_ + bstack11l1l_opy_ (u"ࠦ࠴ࡧࡵࡵࡱࡰࡥࡹ࡫࠯ࡢࡲ࡬࠳ࡻ࠷࠯ࠣ᠔")
            if self.bstack11l1ll1l111_opy_.lower() == bstack11l1l_opy_ (u"ࠧࡸࡥࡴࡷ࡯ࡸࡸࠨ᠕"):
                bstack11l1ll11l11_opy_ = bstack11l1ll1l1ll_opy_.results(bstack11l1ll11l1l_opy_, params)
            else:
                bstack11l1ll11l11_opy_ = bstack11l1ll1l1ll_opy_.bstack11l1ll1l1l1_opy_(bstack11l1ll11l1l_opy_, params)
            if str(bstack11l1ll11l11_opy_.get(bstack11l1l_opy_ (u"࠭ࡳࡵࡣࡷࡹࡸ࠭᠖"), bstack11l1l_opy_ (u"ࠧ࠳࠲࠳ࠫ᠗"))) != bstack11l1l_opy_ (u"ࠨ࠶࠳࠸ࠬ᠘"):
                break
        return bstack11l1ll11l11_opy_.get(bstack11l1l_opy_ (u"ࠩࡧࡥࡹࡧࠧ᠙"), bstack11l1ll11l11_opy_)