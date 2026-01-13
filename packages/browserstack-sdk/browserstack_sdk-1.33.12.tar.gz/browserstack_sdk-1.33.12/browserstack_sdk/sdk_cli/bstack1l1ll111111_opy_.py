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
import logging
import abc
from browserstack_sdk.sdk_cli.bstack1lll1l1llll_opy_ import bstack1lll11ll11l_opy_
class bstack1l1l1l111ll_opy_(abc.ABC):
    bin_session_id: str
    bstack1lll1l1llll_opy_: bstack1lll11ll11l_opy_
    def __init__(self):
        self.bstack1lllll11ll1_opy_ = None
        self.config = None
        self.bin_session_id = None
        self.bstack1lll1l1llll_opy_ = None
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
    def bstack1l11lll11l1_opy_(self):
        return (self.bstack1lllll11ll1_opy_ != None and self.bin_session_id != None and self.bstack1lll1l1llll_opy_ != None)
    def configure(self, bstack1lllll11ll1_opy_, config, bin_session_id: str, bstack1lll1l1llll_opy_: bstack1lll11ll11l_opy_):
        self.bstack1lllll11ll1_opy_ = bstack1lllll11ll1_opy_
        self.config = config
        self.bin_session_id = bin_session_id
        self.bstack1lll1l1llll_opy_ = bstack1lll1l1llll_opy_
        if self.bin_session_id:
            self.logger.debug(bstack11ll1_opy_ (u"ࠣ࡝ࡾ࡭ࡩ࠮ࡳࡦ࡮ࡩ࠭ࢂࡣࠠࡤࡱࡱࡪ࡮࡭ࡵࡳࡧࡧࠤࡲࡵࡤࡶ࡮ࡨࠤࢀࡹࡥ࡭ࡨ࠱ࡣࡤࡩ࡬ࡢࡵࡶࡣࡤ࠴࡟ࡠࡰࡤࡱࡪࡥ࡟ࡾ࠼ࠣࡦ࡮ࡴ࡟ࡴࡧࡶࡷ࡮ࡵ࡮ࡠ࡫ࡧࡁࠧᓐ") + str(self.bin_session_id) + bstack11ll1_opy_ (u"ࠤࠥᓑ"))
    def bstack1ll111111l1_opy_(self):
        if not self.bin_session_id:
            raise ValueError(bstack11ll1_opy_ (u"ࠥࡦ࡮ࡴ࡟ࡴࡧࡶࡷ࡮ࡵ࡮ࡠ࡫ࡧࠤࡨࡧ࡮࡯ࡱࡷࠤࡧ࡫ࠠࡏࡱࡱࡩࠧᓒ"))
    @abc.abstractmethod
    def is_enabled(self) -> bool:
        return False