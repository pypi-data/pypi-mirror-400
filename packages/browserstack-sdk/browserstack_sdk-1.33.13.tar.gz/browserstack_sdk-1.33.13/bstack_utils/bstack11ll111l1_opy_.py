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
import threading
import tempfile
import os
import time
from datetime import datetime
from bstack_utils.bstack11l1ll11lll_opy_ import bstack11l1ll1l1ll_opy_
from bstack_utils.constants import bstack11l1l11111l_opy_, bstack1lllll1l1l_opy_
from bstack_utils.bstack1111l1ll_opy_ import bstack11llllll1l_opy_
from bstack_utils import bstack1l1lll1l11_opy_
bstack11l11l1ll11_opy_ = 10
class bstack1lll1l1l1_opy_:
    def __init__(self, bstack1l1lllll1l_opy_, config, bstack11l11l111ll_opy_=0):
        self.bstack11l11l11lll_opy_ = set()
        self.lock = threading.Lock()
        self.bstack11l111ll1ll_opy_ = bstack11l1l_opy_ (u"ࠧࢁࡽ࠰ࡶࡨࡷࡹࡵࡲࡤࡪࡨࡷࡹࡸࡡࡵ࡫ࡲࡲ࠴ࡧࡰࡪ࠱ࡹ࠵࠴࡬ࡡࡪ࡮ࡨࡨ࠲ࡺࡥࡴࡶࡶࠦᮀ").format(bstack11l1l11111l_opy_)
        self.bstack11l11l1l111_opy_ = os.path.join(tempfile.gettempdir(), bstack11l1l_opy_ (u"ࠨࡡࡣࡱࡵࡸࡤࡨࡵࡪ࡮ࡧࡣࢀࢃࠢᮁ").format(os.environ.get(bstack11l1l_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡌ࡚ࡈ࡟ࡖࡗࡌࡈࠬᮂ"))))
        self.bstack11l11l11l11_opy_ = os.path.join(tempfile.gettempdir(), bstack11l1l_opy_ (u"ࠣࡨࡤ࡭ࡱ࡫ࡤࡠࡶࡨࡷࡹࡹ࡟ࡼࡿ࠱ࡸࡽࡺࠢᮃ").format(os.environ.get(bstack11l1l_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡘ࡙ࡎࡊࠧᮄ"))))
        self.bstack11l111llll1_opy_ = 2
        self.bstack1l1lllll1l_opy_ = bstack1l1lllll1l_opy_
        self.config = config
        self.logger = bstack1l1lll1l11_opy_.get_logger(__name__, bstack1lllll1l1l_opy_)
        self.bstack11l11l111ll_opy_ = bstack11l11l111ll_opy_
        self.bstack11l111lllll_opy_ = False
        self.bstack11l111lll11_opy_ = not (
                            os.environ.get(bstack11l1l_opy_ (u"ࠥࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡅ࡙ࡎࡒࡄࡠࡔࡘࡒࡤࡏࡄࡆࡐࡗࡍࡋࡏࡅࡓࠤᮅ")) and
                            os.environ.get(bstack11l1l_opy_ (u"ࠦࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡒࡔࡊࡅࡠࡋࡑࡈࡊ࡞ࠢᮆ")) and
                            os.environ.get(bstack11l1l_opy_ (u"ࠧࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡕࡔࡂࡎࡢࡒࡔࡊࡅࡠࡅࡒ࡙ࡓ࡚ࠢᮇ"))
                        )
        if bstack11llllll1l_opy_.bstack11l11l1l11l_opy_(config):
            self.bstack11l111llll1_opy_ = bstack11llllll1l_opy_.bstack11l11l11111_opy_(config, self.bstack11l11l111ll_opy_)
            self.bstack11l11ll1111_opy_()
    def bstack11l11l111l1_opy_(self):
        return bstack11l1l_opy_ (u"ࠨࡻࡾࡡࡾࢁࠧᮈ").format(self.config.get(bstack11l1l_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡔࡡ࡮ࡧࠪᮉ")), os.environ.get(bstack11l1l_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡃࡗࡌࡐࡉࡥࡒࡖࡐࡢࡍࡉࡋࡎࡕࡋࡉࡍࡊࡘࠧᮊ")))
    def bstack11l11l1ll1l_opy_(self):
        try:
            if self.bstack11l111lll11_opy_:
                return
            with self.lock:
                try:
                    with open(self.bstack11l11l11l11_opy_, bstack11l1l_opy_ (u"ࠤࡵࠦᮋ")) as f:
                        bstack11l11l1l1l1_opy_ = set(line.strip() for line in f if line.strip())
                except FileNotFoundError:
                    bstack11l11l1l1l1_opy_ = set()
                bstack11l11l1llll_opy_ = bstack11l11l1l1l1_opy_ - self.bstack11l11l11lll_opy_
                if not bstack11l11l1llll_opy_:
                    return
                self.bstack11l11l11lll_opy_.update(bstack11l11l1llll_opy_)
                data = {bstack11l1l_opy_ (u"ࠥࡪࡦ࡯࡬ࡦࡦࡗࡩࡸࡺࡳࠣᮌ"): list(self.bstack11l11l11lll_opy_), bstack11l1l_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡑࡥࡲ࡫ࠢᮍ"): self.config.get(bstack11l1l_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡒࡦࡳࡥࠨᮎ")), bstack11l1l_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡗࡻ࡮ࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠦᮏ"): os.environ.get(bstack11l1l_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡂࡖࡋࡏࡈࡤࡘࡕࡏࡡࡌࡈࡊࡔࡔࡊࡈࡌࡉࡗ࠭ᮐ")), bstack11l1l_opy_ (u"ࠣࡲࡵࡳ࡯࡫ࡣࡵࡐࡤࡱࡪࠨᮑ"): self.config.get(bstack11l1l_opy_ (u"ࠩࡳࡶࡴࡰࡥࡤࡶࡑࡥࡲ࡫ࠧᮒ"))}
            response = bstack11l1ll1l1ll_opy_.bstack11l11l11ll1_opy_(self.bstack11l111ll1ll_opy_, data)
            if response.get(bstack11l1l_opy_ (u"ࠥࡷࡹࡧࡴࡶࡵࠥᮓ")) == 200:
                self.logger.debug(bstack11l1l_opy_ (u"ࠦࡘࡻࡣࡤࡧࡶࡷ࡫ࡻ࡬࡭ࡻࠣࡷࡪࡴࡴࠡࡨࡤ࡭ࡱ࡫ࡤࠡࡶࡨࡷࡹࡹ࠺ࠡࡽࢀࠦᮔ").format(data))
            else:
                self.logger.debug(bstack11l1l_opy_ (u"ࠧࡌࡡࡪ࡮ࡨࡨࠥࡺ࡯ࠡࡵࡨࡲࡩࠦࡦࡢ࡫࡯ࡩࡩࠦࡴࡦࡵࡷࡷ࠿ࠦࡻࡾࠤᮕ").format(response))
        except Exception as e:
            self.logger.debug(bstack11l1l_opy_ (u"ࠨࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢࡧࡹࡷ࡯࡮ࡨࠢࡶࡩࡳࡪࡩ࡯ࡩࠣࡪࡦ࡯࡬ࡦࡦࠣࡸࡪࡹࡴࡴ࠼ࠣࡿࢂࠨᮖ").format(e))
    def bstack11l11l1lll1_opy_(self):
        if self.bstack11l111lll11_opy_:
            with self.lock:
                try:
                    with open(self.bstack11l11l11l11_opy_, bstack11l1l_opy_ (u"ࠢࡳࠤᮗ")) as f:
                        bstack11l111lll1l_opy_ = set(line.strip() for line in f if line.strip())
                    failed_count = len(bstack11l111lll1l_opy_)
                except FileNotFoundError:
                    failed_count = 0
                self.logger.debug(bstack11l1l_opy_ (u"ࠣࡒࡲࡰࡱ࡫ࡤࠡࡨࡤ࡭ࡱ࡫ࡤࠡࡶࡨࡷࡹࡹࠠࡤࡱࡸࡲࡹࠦࠨ࡭ࡱࡦࡥࡱ࠯࠺ࠡࡽࢀࠦᮘ").format(failed_count))
                if failed_count >= self.bstack11l111llll1_opy_:
                    self.logger.info(bstack11l1l_opy_ (u"ࠤࡗ࡬ࡷ࡫ࡳࡩࡱ࡯ࡨࠥࡩࡲࡰࡵࡶࡩࡩࠦࠨ࡭ࡱࡦࡥࡱ࠯࠺ࠡࡽࢀࠤࡃࡃࠠࡼࡿࠥᮙ").format(failed_count, self.bstack11l111llll1_opy_))
                    self.bstack11l11l11l1l_opy_(failed_count)
                    self.bstack11l111lllll_opy_ = True
            return
        try:
            response = bstack11l1ll1l1ll_opy_.bstack11l11l1lll1_opy_(bstack11l1l_opy_ (u"ࠥࡿࢂࡅࡢࡶ࡫࡯ࡨࡓࡧ࡭ࡦ࠿ࡾࢁࠫࡨࡵࡪ࡮ࡧࡖࡺࡴࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࡀࡿࢂࠬࡰࡳࡱ࡭ࡩࡨࡺࡎࡢ࡯ࡨࡁࢀࢃࠢᮚ").format(self.bstack11l111ll1ll_opy_, self.config.get(bstack11l1l_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡑࡥࡲ࡫ࠧᮛ")), os.environ.get(bstack11l1l_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡇ࡛ࡉࡍࡆࡢࡖ࡚ࡔ࡟ࡊࡆࡈࡒ࡙ࡏࡆࡊࡇࡕࠫᮜ")), self.config.get(bstack11l1l_opy_ (u"࠭ࡰࡳࡱ࡭ࡩࡨࡺࡎࡢ࡯ࡨࠫᮝ"))))
            if response.get(bstack11l1l_opy_ (u"ࠢࡴࡶࡤࡸࡺࡹࠢᮞ")) == 200:
                failed_count = response.get(bstack11l1l_opy_ (u"ࠣࡨࡤ࡭ࡱ࡫ࡤࡕࡧࡶࡸࡸࡉ࡯ࡶࡰࡷࠦᮟ"), 0)
                self.logger.debug(bstack11l1l_opy_ (u"ࠤࡓࡳࡱࡲࡥࡥࠢࡩࡥ࡮ࡲࡥࡥࠢࡷࡩࡸࡺࡳࠡࡥࡲࡹࡳࡺ࠺ࠡࡽࢀࠦᮠ").format(failed_count))
                if failed_count >= self.bstack11l111llll1_opy_:
                    self.logger.info(bstack11l1l_opy_ (u"ࠥࡘ࡭ࡸࡥࡴࡪࡲࡰࡩࠦࡣࡳࡱࡶࡷࡪࡪ࠺ࠡࡽࢀࠤࡃࡃࠠࡼࡿࠥᮡ").format(failed_count, self.bstack11l111llll1_opy_))
                    self.bstack11l11l11l1l_opy_(failed_count)
                    self.bstack11l111lllll_opy_ = True
            else:
                self.logger.error(bstack11l1l_opy_ (u"ࠦࡋࡧࡩ࡭ࡧࡧࠤࡹࡵࠠࡱࡱ࡯ࡰࠥ࡬ࡡࡪ࡮ࡨࡨࠥࡺࡥࡴࡶࡶ࠾ࠥࢁࡽࠣᮢ").format(response))
        except Exception as e:
            self.logger.error(bstack11l1l_opy_ (u"ࠧࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡࡦࡸࡶ࡮ࡴࡧࠡࡲࡲࡰࡱ࡯࡮ࡨ࠼ࠣࡿࢂࠨᮣ").format(e))
    def bstack11l11l11l1l_opy_(self, failed_count):
        with open(self.bstack11l11l1l111_opy_, bstack11l1l_opy_ (u"ࠨࡷࠣᮤ")) as f:
            f.write(bstack11l1l_opy_ (u"ࠢࡕࡪࡵࡩࡸ࡮࡯࡭ࡦࠣࡧࡷࡵࡳࡴࡧࡧࠤࡦࡺࠠࡼࡿ࡟ࡲࠧᮥ").format(datetime.now()))
            f.write(bstack11l1l_opy_ (u"ࠣࡈࡤ࡭ࡱ࡫ࡤࠡࡶࡨࡷࡹࡹࠠࡤࡱࡸࡲࡹࡀࠠࡼࡿ࡟ࡲࠧᮦ").format(failed_count))
        self.logger.debug(bstack11l1l_opy_ (u"ࠤࡄࡦࡴࡸࡴࠡࡄࡸ࡭ࡱࡪࠠࡧ࡫࡯ࡩࠥࡩࡲࡦࡣࡷࡩࡩࡀࠠࡼࡿࠥᮧ").format(self.bstack11l11l1l111_opy_))
    def bstack11l11ll1111_opy_(self):
        def bstack11l11l1l1ll_opy_():
            while not self.bstack11l111lllll_opy_:
                time.sleep(bstack11l11l1ll11_opy_)
                self.bstack11l11l1ll1l_opy_()
                self.bstack11l11l1lll1_opy_()
        bstack11l11l1111l_opy_ = threading.Thread(target=bstack11l11l1l1ll_opy_, daemon=True)
        bstack11l11l1111l_opy_.start()