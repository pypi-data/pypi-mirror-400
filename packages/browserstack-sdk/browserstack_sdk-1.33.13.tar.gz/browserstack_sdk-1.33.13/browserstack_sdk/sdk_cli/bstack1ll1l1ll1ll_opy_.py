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
import logging
import abc
from browserstack_sdk.sdk_cli.bstack1lllll1l11l_opy_ import bstack1lllll11ll1_opy_
class bstack1ll1ll1l1ll_opy_(abc.ABC):
    bin_session_id: str
    bstack1lllll1l11l_opy_: bstack1lllll11ll1_opy_
    def __init__(self):
        self.bstack1ll1ll11l11_opy_ = None
        self.config = None
        self.bin_session_id = None
        self.bstack1lllll1l11l_opy_ = None
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
    def bstack1lll1l11lll_opy_(self):
        return (self.bstack1ll1ll11l11_opy_ != None and self.bin_session_id != None and self.bstack1lllll1l11l_opy_ != None)
    def configure(self, bstack1ll1ll11l11_opy_, config, bin_session_id: str, bstack1lllll1l11l_opy_: bstack1lllll11ll1_opy_):
        self.bstack1ll1ll11l11_opy_ = bstack1ll1ll11l11_opy_
        self.config = config
        self.bin_session_id = bin_session_id
        self.bstack1lllll1l11l_opy_ = bstack1lllll1l11l_opy_
        if self.bin_session_id:
            self.logger.debug(bstack11l1l_opy_ (u"ࠦࡠࢁࡩࡥࠪࡶࡩࡱ࡬ࠩࡾ࡟ࠣࡧࡴࡴࡦࡪࡩࡸࡶࡪࡪࠠ࡮ࡱࡧࡹࡱ࡫ࠠࡼࡵࡨࡰ࡫࠴࡟ࡠࡥ࡯ࡥࡸࡹ࡟ࡠ࠰ࡢࡣࡳࡧ࡭ࡦࡡࡢࢁ࠿ࠦࡢࡪࡰࡢࡷࡪࡹࡳࡪࡱࡱࡣ࡮ࡪ࠽ࠣዛ") + str(self.bin_session_id) + bstack11l1l_opy_ (u"ࠧࠨዜ"))
    def bstack1ll11111lll_opy_(self):
        if not self.bin_session_id:
            raise ValueError(bstack11l1l_opy_ (u"ࠨࡢࡪࡰࡢࡷࡪࡹࡳࡪࡱࡱࡣ࡮ࡪࠠࡤࡣࡱࡲࡴࡺࠠࡣࡧࠣࡒࡴࡴࡥࠣዝ"))
    @abc.abstractmethod
    def is_enabled(self) -> bool:
        return False