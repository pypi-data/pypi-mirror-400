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
import threading
import tempfile
import os
import time
from datetime import datetime
from bstack_utils.bstack11l1ll1l1l1_opy_ import bstack11l1ll1l11l_opy_
from bstack_utils.constants import bstack11l11lll1l1_opy_, bstack11l1111l1_opy_
from bstack_utils.bstack11l111l1_opy_ import bstack1lll1lll_opy_
from bstack_utils import bstack111lll1l1_opy_
bstack11l11l11l1l_opy_ = 10
class bstack111l1llll_opy_:
    def __init__(self, bstack1ll11l1ll_opy_, config, bstack11l11l1ll1l_opy_=0):
        self.bstack11l111lll11_opy_ = set()
        self.lock = threading.Lock()
        self.bstack11l11l11l11_opy_ = bstack11ll1_opy_ (u"ࠨࡻࡾ࠱ࡷࡩࡸࡺ࡯ࡳࡥ࡫ࡩࡸࡺࡲࡢࡶ࡬ࡳࡳ࠵ࡡࡱ࡫࠲ࡺ࠶࠵ࡦࡢ࡫࡯ࡩࡩ࠳ࡴࡦࡵࡷࡷࠧᮁ").format(bstack11l11lll1l1_opy_)
        self.bstack11l111ll1ll_opy_ = os.path.join(tempfile.gettempdir(), bstack11ll1_opy_ (u"ࠢࡢࡤࡲࡶࡹࡥࡢࡶ࡫࡯ࡨࡤࢁࡽࠣᮂ").format(os.environ.get(bstack11ll1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡍ࡛ࡂࡠࡗࡘࡍࡉ࠭ᮃ"))))
        self.bstack11l11l111ll_opy_ = os.path.join(tempfile.gettempdir(), bstack11ll1_opy_ (u"ࠤࡩࡥ࡮ࡲࡥࡥࡡࡷࡩࡸࡺࡳࡠࡽࢀ࠲ࡹࡾࡴࠣᮄ").format(os.environ.get(bstack11ll1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡉࡘ࡚ࡈࡖࡄࡢ࡙࡚ࡏࡄࠨᮅ"))))
        self.bstack11l11l11ll1_opy_ = 2
        self.bstack1ll11l1ll_opy_ = bstack1ll11l1ll_opy_
        self.config = config
        self.logger = bstack111lll1l1_opy_.get_logger(__name__, bstack11l1111l1_opy_)
        self.bstack11l11l1ll1l_opy_ = bstack11l11l1ll1l_opy_
        self.bstack11l11l1111l_opy_ = False
        self.bstack11l11ll1111_opy_ = not (
                            os.environ.get(bstack11ll1_opy_ (u"ࠦࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡆ࡚ࡏࡌࡅࡡࡕ࡙ࡓࡥࡉࡅࡇࡑࡘࡎࡌࡉࡆࡔࠥᮆ")) and
                            os.environ.get(bstack11ll1_opy_ (u"ࠧࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡓࡕࡄࡆࡡࡌࡒࡉࡋࡘࠣᮇ")) and
                            os.environ.get(bstack11ll1_opy_ (u"ࠨࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡏࡕࡃࡏࡣࡓࡕࡄࡆࡡࡆࡓ࡚ࡔࡔࠣᮈ"))
                        )
        if bstack1lll1lll_opy_.bstack11l11l11111_opy_(config):
            self.bstack11l11l11ll1_opy_ = bstack1lll1lll_opy_.bstack11l11l1l1l1_opy_(config, self.bstack11l11l1ll1l_opy_)
            self.bstack11l11l1llll_opy_()
    def bstack11l111lll1l_opy_(self):
        return bstack11ll1_opy_ (u"ࠢࡼࡿࡢࡿࢂࠨᮉ").format(self.config.get(bstack11ll1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠫᮊ")), os.environ.get(bstack11ll1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡄࡘࡍࡑࡊ࡟ࡓࡗࡑࡣࡎࡊࡅࡏࡖࡌࡊࡎࡋࡒࠨᮋ")))
    def bstack11l111llll1_opy_(self):
        try:
            if self.bstack11l11ll1111_opy_:
                return
            with self.lock:
                try:
                    with open(self.bstack11l11l111ll_opy_, bstack11ll1_opy_ (u"ࠥࡶࠧᮌ")) as f:
                        bstack11l11l1ll11_opy_ = set(line.strip() for line in f if line.strip())
                except FileNotFoundError:
                    bstack11l11l1ll11_opy_ = set()
                bstack11l11l1l1ll_opy_ = bstack11l11l1ll11_opy_ - self.bstack11l111lll11_opy_
                if not bstack11l11l1l1ll_opy_:
                    return
                self.bstack11l111lll11_opy_.update(bstack11l11l1l1ll_opy_)
                data = {bstack11ll1_opy_ (u"ࠦ࡫ࡧࡩ࡭ࡧࡧࡘࡪࡹࡴࡴࠤᮍ"): list(self.bstack11l111lll11_opy_), bstack11ll1_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡒࡦࡳࡥࠣᮎ"): self.config.get(bstack11ll1_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡓࡧ࡭ࡦࠩᮏ")), bstack11ll1_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡘࡵ࡯ࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠧᮐ"): os.environ.get(bstack11ll1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡃࡗࡌࡐࡉࡥࡒࡖࡐࡢࡍࡉࡋࡎࡕࡋࡉࡍࡊࡘࠧᮑ")), bstack11ll1_opy_ (u"ࠤࡳࡶࡴࡰࡥࡤࡶࡑࡥࡲ࡫ࠢᮒ"): self.config.get(bstack11ll1_opy_ (u"ࠪࡴࡷࡵࡪࡦࡥࡷࡒࡦࡳࡥࠨᮓ"))}
            response = bstack11l1ll1l11l_opy_.bstack11l11l11lll_opy_(self.bstack11l11l11l11_opy_, data)
            if response.get(bstack11ll1_opy_ (u"ࠦࡸࡺࡡࡵࡷࡶࠦᮔ")) == 200:
                self.logger.debug(bstack11ll1_opy_ (u"࡙ࠧࡵࡤࡥࡨࡷࡸ࡬ࡵ࡭࡮ࡼࠤࡸ࡫࡮ࡵࠢࡩࡥ࡮ࡲࡥࡥࠢࡷࡩࡸࡺࡳ࠻ࠢࡾࢁࠧᮕ").format(data))
            else:
                self.logger.debug(bstack11ll1_opy_ (u"ࠨࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡶࡩࡳࡪࠠࡧࡣ࡬ࡰࡪࡪࠠࡵࡧࡶࡸࡸࡀࠠࡼࡿࠥᮖ").format(response))
        except Exception as e:
            self.logger.debug(bstack11ll1_opy_ (u"ࠢࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣࡨࡺࡸࡩ࡯ࡩࠣࡷࡪࡴࡤࡪࡰࡪࠤ࡫ࡧࡩ࡭ࡧࡧࠤࡹ࡫ࡳࡵࡵ࠽ࠤࢀࢃࠢᮗ").format(e))
    def bstack11l11l1l11l_opy_(self):
        if self.bstack11l11ll1111_opy_:
            with self.lock:
                try:
                    with open(self.bstack11l11l111ll_opy_, bstack11ll1_opy_ (u"ࠣࡴࠥᮘ")) as f:
                        bstack11l11l111l1_opy_ = set(line.strip() for line in f if line.strip())
                    failed_count = len(bstack11l11l111l1_opy_)
                except FileNotFoundError:
                    failed_count = 0
                self.logger.debug(bstack11ll1_opy_ (u"ࠤࡓࡳࡱࡲࡥࡥࠢࡩࡥ࡮ࡲࡥࡥࠢࡷࡩࡸࡺࡳࠡࡥࡲࡹࡳࡺࠠࠩ࡮ࡲࡧࡦࡲࠩ࠻ࠢࡾࢁࠧᮙ").format(failed_count))
                if failed_count >= self.bstack11l11l11ll1_opy_:
                    self.logger.info(bstack11ll1_opy_ (u"ࠥࡘ࡭ࡸࡥࡴࡪࡲࡰࡩࠦࡣࡳࡱࡶࡷࡪࡪࠠࠩ࡮ࡲࡧࡦࡲࠩ࠻ࠢࡾࢁࠥࡄ࠽ࠡࡽࢀࠦᮚ").format(failed_count, self.bstack11l11l11ll1_opy_))
                    self.bstack11l111lllll_opy_(failed_count)
                    self.bstack11l11l1111l_opy_ = True
            return
        try:
            response = bstack11l1ll1l11l_opy_.bstack11l11l1l11l_opy_(bstack11ll1_opy_ (u"ࠦࢀࢃ࠿ࡣࡷ࡬ࡰࡩࡔࡡ࡮ࡧࡀࡿࢂࠬࡢࡶ࡫࡯ࡨࡗࡻ࡮ࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࡁࢀࢃࠦࡱࡴࡲ࡮ࡪࡩࡴࡏࡣࡰࡩࡂࢁࡽࠣᮛ").format(self.bstack11l11l11l11_opy_, self.config.get(bstack11ll1_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡒࡦࡳࡥࠨᮜ")), os.environ.get(bstack11ll1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡈࡕࡊࡎࡇࡣࡗ࡛ࡎࡠࡋࡇࡉࡓ࡚ࡉࡇࡋࡈࡖࠬᮝ")), self.config.get(bstack11ll1_opy_ (u"ࠧࡱࡴࡲ࡮ࡪࡩࡴࡏࡣࡰࡩࠬᮞ"))))
            if response.get(bstack11ll1_opy_ (u"ࠣࡵࡷࡥࡹࡻࡳࠣᮟ")) == 200:
                failed_count = response.get(bstack11ll1_opy_ (u"ࠤࡩࡥ࡮ࡲࡥࡥࡖࡨࡷࡹࡹࡃࡰࡷࡱࡸࠧᮠ"), 0)
                self.logger.debug(bstack11ll1_opy_ (u"ࠥࡔࡴࡲ࡬ࡦࡦࠣࡪࡦ࡯࡬ࡦࡦࠣࡸࡪࡹࡴࡴࠢࡦࡳࡺࡴࡴ࠻ࠢࡾࢁࠧᮡ").format(failed_count))
                if failed_count >= self.bstack11l11l11ll1_opy_:
                    self.logger.info(bstack11ll1_opy_ (u"࡙ࠦ࡮ࡲࡦࡵ࡫ࡳࡱࡪࠠࡤࡴࡲࡷࡸ࡫ࡤ࠻ࠢࡾࢁࠥࡄ࠽ࠡࡽࢀࠦᮢ").format(failed_count, self.bstack11l11l11ll1_opy_))
                    self.bstack11l111lllll_opy_(failed_count)
                    self.bstack11l11l1111l_opy_ = True
            else:
                self.logger.error(bstack11ll1_opy_ (u"ࠧࡌࡡࡪ࡮ࡨࡨࠥࡺ࡯ࠡࡲࡲࡰࡱࠦࡦࡢ࡫࡯ࡩࡩࠦࡴࡦࡵࡷࡷ࠿ࠦࡻࡾࠤᮣ").format(response))
        except Exception as e:
            self.logger.error(bstack11ll1_opy_ (u"ࠨࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢࡧࡹࡷ࡯࡮ࡨࠢࡳࡳࡱࡲࡩ࡯ࡩ࠽ࠤࢀࢃࠢᮤ").format(e))
    def bstack11l111lllll_opy_(self, failed_count):
        with open(self.bstack11l111ll1ll_opy_, bstack11ll1_opy_ (u"ࠢࡸࠤᮥ")) as f:
            f.write(bstack11ll1_opy_ (u"ࠣࡖ࡫ࡶࡪࡹࡨࡰ࡮ࡧࠤࡨࡸ࡯ࡴࡵࡨࡨࠥࡧࡴࠡࡽࢀࡠࡳࠨᮦ").format(datetime.now()))
            f.write(bstack11ll1_opy_ (u"ࠤࡉࡥ࡮ࡲࡥࡥࠢࡷࡩࡸࡺࡳࠡࡥࡲࡹࡳࡺ࠺ࠡࡽࢀࡠࡳࠨᮧ").format(failed_count))
        self.logger.debug(bstack11ll1_opy_ (u"ࠥࡅࡧࡵࡲࡵࠢࡅࡹ࡮ࡲࡤࠡࡨ࡬ࡰࡪࠦࡣࡳࡧࡤࡸࡪࡪ࠺ࠡࡽࢀࠦᮨ").format(self.bstack11l111ll1ll_opy_))
    def bstack11l11l1llll_opy_(self):
        def bstack11l11l1lll1_opy_():
            while not self.bstack11l11l1111l_opy_:
                time.sleep(bstack11l11l11l1l_opy_)
                self.bstack11l111llll1_opy_()
                self.bstack11l11l1l11l_opy_()
        bstack11l11l1l111_opy_ = threading.Thread(target=bstack11l11l1lll1_opy_, daemon=True)
        bstack11l11l1l111_opy_.start()