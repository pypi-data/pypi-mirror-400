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
import json
import logging
import os
import datetime
import threading
from bstack_utils.constants import EVENTS, STAGE
from bstack_utils.helper import bstack11ll111111l_opy_, bstack11ll11ll1ll_opy_, bstack1l111l111l_opy_, error_handler, bstack111llllllll_opy_, bstack111lll111l1_opy_, bstack111llll111l_opy_, bstack1lllll111_opy_, bstack11lll11l_opy_
from bstack_utils.measure import measure
from bstack_utils.bstack1llll1ll1111_opy_ import bstack1llll1ll11ll_opy_
import bstack_utils.bstack1l1llll1l_opy_ as bstack1ll11l1l1_opy_
from bstack_utils.bstack111ll11111_opy_ import bstack11llll111_opy_
import bstack_utils.accessibility as bstack11llll11l1_opy_
from bstack_utils.bstack111lll1l_opy_ import bstack111lll1l_opy_
from bstack_utils.bstack111l1lllll_opy_ import bstack1111l11ll1_opy_
from bstack_utils.constants import bstack1l111ll1ll_opy_
bstack1lll1lll1ll1_opy_ = bstack11l1l_opy_ (u"ࠧࡩࡶࡷࡴࡸࡀ࠯࠰ࡥࡲࡰࡱ࡫ࡣࡵࡱࡵ࠱ࡴࡨࡳࡦࡴࡹࡥࡧ࡯࡬ࡪࡶࡼ࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡧࡴࡳࠧ↢")
logger = logging.getLogger(__name__)
class bstack1ll1llll11_opy_:
    bstack1llll1ll1111_opy_ = None
    bs_config = None
    bstack1llll111_opy_ = None
    @classmethod
    @error_handler(class_method=True)
    @measure(event_name=EVENTS.bstack11l1l111l1l_opy_, stage=STAGE.bstack1lll1l11l_opy_)
    def launch(cls, bs_config, bstack1llll111_opy_):
        cls.bs_config = bs_config
        cls.bstack1llll111_opy_ = bstack1llll111_opy_
        try:
            cls.bstack1lll1lll1lll_opy_()
            bstack11l1lll1l1l_opy_ = bstack11ll111111l_opy_(bs_config)
            bstack11ll111l11l_opy_ = bstack11ll11ll1ll_opy_(bs_config)
            data = bstack1ll11l1l1_opy_.bstack1lll1ll1ll11_opy_(bs_config, bstack1llll111_opy_)
            config = {
                bstack11l1l_opy_ (u"ࠨࡣࡸࡸ࡭࠭↣"): (bstack11l1lll1l1l_opy_, bstack11ll111l11l_opy_),
                bstack11l1l_opy_ (u"ࠩ࡫ࡩࡦࡪࡥࡳࡵࠪ↤"): cls.default_headers()
            }
            response = bstack1l111l111l_opy_(bstack11l1l_opy_ (u"ࠪࡔࡔ࡙ࡔࠨ↥"), cls.request_url(bstack11l1l_opy_ (u"ࠫࡦࡶࡩ࠰ࡸ࠵࠳ࡧࡻࡩ࡭ࡦࡶࠫ↦")), data, config)
            if response.status_code != 200:
                bstack11111ll1_opy_ = response.json()
                if bstack11111ll1_opy_[bstack11l1l_opy_ (u"ࠬࡹࡵࡤࡥࡨࡷࡸ࠭↧")] == False:
                    cls.bstack1lll1ll1lll1_opy_(bstack11111ll1_opy_)
                    return
                cls.bstack1lll1ll11111_opy_(bstack11111ll1_opy_[bstack11l1l_opy_ (u"࠭࡯ࡣࡵࡨࡶࡻࡧࡢࡪ࡮࡬ࡸࡾ࠭↨")])
                cls.bstack1lll1l1lllll_opy_(bstack11111ll1_opy_[bstack11l1l_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠧ↩")])
                return None
            bstack1lll1ll11l1l_opy_ = cls.bstack1lll1ll1l111_opy_(response)
            return bstack1lll1ll11l1l_opy_, response.json()
        except Exception as error:
            logger.error(bstack11l1l_opy_ (u"ࠣࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤࡼ࡮ࡩ࡭ࡧࠣࡧࡷ࡫ࡡࡵ࡫ࡱ࡫ࠥࡨࡵࡪ࡮ࡧࠤ࡫ࡵࡲࠡࡖࡨࡷࡹࡎࡵࡣ࠼ࠣࡿࢂࠨ↪").format(str(error)))
            return None
    @classmethod
    @error_handler(class_method=True)
    def stop(cls, bstack1lll1lll1l1l_opy_=None):
        if not bstack11llll111_opy_.on() and not bstack11llll11l1_opy_.on():
            return
        if os.environ.get(bstack11l1l_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡍ࡛࡙࠭↫")) == bstack11l1l_opy_ (u"ࠥࡲࡺࡲ࡬ࠣ↬") or os.environ.get(bstack11l1l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡉࡗࡅࡣ࡚࡛ࡉࡅࠩ↭")) == bstack11l1l_opy_ (u"ࠧࡴࡵ࡭࡮ࠥ↮"):
            logger.error(bstack11l1l_opy_ (u"࠭ࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢ࡬ࡲࠥࡹࡴࡰࡲࠣࡦࡺ࡯࡬ࡥࠢࡵࡩࡶࡻࡥࡴࡶࠣࡸࡴࠦࡔࡦࡵࡷࡌࡺࡨ࠺ࠡࡏ࡬ࡷࡸ࡯࡮ࡨࠢࡤࡹࡹ࡮ࡥ࡯ࡶ࡬ࡧࡦࡺࡩࡰࡰࠣࡸࡴࡱࡥ࡯ࠩ↯"))
            return {
                bstack11l1l_opy_ (u"ࠧࡴࡶࡤࡸࡺࡹࠧ↰"): bstack11l1l_opy_ (u"ࠨࡧࡵࡶࡴࡸࠧ↱"),
                bstack11l1l_opy_ (u"ࠩࡰࡩࡸࡹࡡࡨࡧࠪ↲"): bstack11l1l_opy_ (u"ࠪࡘࡴࡱࡥ࡯࠱ࡥࡹ࡮ࡲࡤࡊࡆࠣ࡭ࡸࠦࡵ࡯ࡦࡨࡪ࡮ࡴࡥࡥ࠮ࠣࡦࡺ࡯࡬ࡥࠢࡦࡶࡪࡧࡴࡪࡱࡱࠤࡲ࡯ࡧࡩࡶࠣ࡬ࡦࡼࡥࠡࡨࡤ࡭ࡱ࡫ࡤࠨ↳")
            }
        try:
            cls.bstack1llll1ll1111_opy_.shutdown()
            data = {
                bstack11l1l_opy_ (u"ࠫ࡫࡯࡮ࡪࡵ࡫ࡩࡩࡥࡡࡵࠩ↴"): bstack1lllll111_opy_()
            }
            if not bstack1lll1lll1l1l_opy_ is None:
                data[bstack11l1l_opy_ (u"ࠬ࡬ࡩ࡯࡫ࡶ࡬ࡪࡪ࡟࡮ࡧࡷࡥࡩࡧࡴࡢࠩ↵")] = [{
                    bstack11l1l_opy_ (u"࠭ࡲࡦࡣࡶࡳࡳ࠭↶"): bstack11l1l_opy_ (u"ࠧࡶࡵࡨࡶࡤࡱࡩ࡭࡮ࡨࡨࠬ↷"),
                    bstack11l1l_opy_ (u"ࠨࡵ࡬࡫ࡳࡧ࡬ࠨ↸"): bstack1lll1lll1l1l_opy_
                }]
            config = {
                bstack11l1l_opy_ (u"ࠩ࡫ࡩࡦࡪࡥࡳࡵࠪ↹"): cls.default_headers()
            }
            bstack11l1ll1ll11_opy_ = bstack11l1l_opy_ (u"ࠪࡥࡵ࡯࠯ࡷ࠳࠲ࡦࡺ࡯࡬ࡥࡵ࠲ࡿࢂ࠵ࡳࡵࡱࡳࠫ↺").format(os.environ[bstack11l1l_opy_ (u"ࠦࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡉࡗࡅࡣ࡚࡛ࡉࡅࠤ↻")])
            bstack1lll1ll11l11_opy_ = cls.request_url(bstack11l1ll1ll11_opy_)
            response = bstack1l111l111l_opy_(bstack11l1l_opy_ (u"ࠬࡖࡕࡕࠩ↼"), bstack1lll1ll11l11_opy_, data, config)
            if not response.ok:
                raise Exception(bstack11l1l_opy_ (u"ࠨࡓࡵࡱࡳࠤࡷ࡫ࡱࡶࡧࡶࡸࠥࡴ࡯ࡵࠢࡲ࡯ࠧ↽"))
        except Exception as error:
            logger.error(bstack11l1l_opy_ (u"ࠢࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣ࡭ࡳࠦࡳࡵࡱࡳࠤࡧࡻࡩ࡭ࡦࠣࡶࡪࡷࡵࡦࡵࡷࠤࡹࡵࠠࡕࡧࡶࡸࡍࡻࡢ࠻࠼ࠣࠦ↾") + str(error))
            return {
                bstack11l1l_opy_ (u"ࠨࡵࡷࡥࡹࡻࡳࠨ↿"): bstack11l1l_opy_ (u"ࠩࡨࡶࡷࡵࡲࠨ⇀"),
                bstack11l1l_opy_ (u"ࠪࡱࡪࡹࡳࡢࡩࡨࠫ⇁"): str(error)
            }
    @classmethod
    @error_handler(class_method=True)
    def bstack1lll1ll1l111_opy_(cls, response):
        bstack11111ll1_opy_ = response.json() if not isinstance(response, dict) else response
        bstack1lll1ll11l1l_opy_ = {}
        if bstack11111ll1_opy_.get(bstack11l1l_opy_ (u"ࠫ࡯ࡽࡴࠨ⇂")) is None:
            os.environ[bstack11l1l_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡊࡘࡆࡤࡐࡗࡕࠩ⇃")] = bstack11l1l_opy_ (u"࠭࡮ࡶ࡮࡯ࠫ⇄")
        else:
            os.environ[bstack11l1l_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡌ࡚ࡈ࡟ࡋ࡙ࡗࠫ⇅")] = bstack11111ll1_opy_.get(bstack11l1l_opy_ (u"ࠨ࡬ࡺࡸࠬ⇆"), bstack11l1l_opy_ (u"ࠩࡱࡹࡱࡲࠧ⇇"))
        os.environ[bstack11l1l_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡉࡘ࡚ࡈࡖࡄࡢ࡙࡚ࡏࡄࠨ⇈")] = bstack11111ll1_opy_.get(bstack11l1l_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡢ࡬ࡦࡹࡨࡦࡦࡢ࡭ࡩ࠭⇉"), bstack11l1l_opy_ (u"ࠬࡴࡵ࡭࡮ࠪ⇊"))
        logger.info(bstack11l1l_opy_ (u"࠭ࡔࡦࡵࡷ࡬ࡺࡨࠠࡴࡶࡤࡶࡹ࡫ࡤࠡࡹ࡬ࡸ࡭ࠦࡩࡥ࠼ࠣࠫ⇋") + os.getenv(bstack11l1l_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡌ࡚ࡈ࡟ࡖࡗࡌࡈࠬ⇌")));
        if bstack11llll111_opy_.bstack1lll1ll1l1ll_opy_(cls.bs_config, cls.bstack1llll111_opy_.get(bstack11l1l_opy_ (u"ࠨࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡺࡹࡥࡥࠩ⇍"), bstack11l1l_opy_ (u"ࠩࠪ⇎"))) is True:
            bstack1llll1l111ll_opy_, build_hashed_id, bstack1lll1lll111l_opy_ = cls.bstack1lll1ll1111l_opy_(bstack11111ll1_opy_)
            if bstack1llll1l111ll_opy_ != None and build_hashed_id != None:
                bstack1lll1ll11l1l_opy_[bstack11l1l_opy_ (u"ࠪࡳࡧࡹࡥࡳࡸࡤࡦ࡮ࡲࡩࡵࡻࠪ⇏")] = {
                    bstack11l1l_opy_ (u"ࠫ࡯ࡽࡴࡠࡶࡲ࡯ࡪࡴࠧ⇐"): bstack1llll1l111ll_opy_,
                    bstack11l1l_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡣ࡭ࡧࡳࡩࡧࡧࡣ࡮ࡪࠧ⇑"): build_hashed_id,
                    bstack11l1l_opy_ (u"࠭ࡡ࡭࡮ࡲࡻࡤࡹࡣࡳࡧࡨࡲࡸ࡮࡯ࡵࡵࠪ⇒"): bstack1lll1lll111l_opy_
                }
            else:
                bstack1lll1ll11l1l_opy_[bstack11l1l_opy_ (u"ࠧࡰࡤࡶࡩࡷࡼࡡࡣ࡫࡯࡭ࡹࡿࠧ⇓")] = {}
        else:
            bstack1lll1ll11l1l_opy_[bstack11l1l_opy_ (u"ࠨࡱࡥࡷࡪࡸࡶࡢࡤ࡬ࡰ࡮ࡺࡹࠨ⇔")] = {}
        bstack1lll1ll1ll1l_opy_, build_hashed_id = cls.bstack1lll1ll1llll_opy_(bstack11111ll1_opy_)
        if bstack1lll1ll1ll1l_opy_ != None and build_hashed_id != None:
            bstack1lll1ll11l1l_opy_[bstack11l1l_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠩ⇕")] = {
                bstack11l1l_opy_ (u"ࠪࡥࡺࡺࡨࡠࡶࡲ࡯ࡪࡴࠧ⇖"): bstack1lll1ll1ll1l_opy_,
                bstack11l1l_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡢ࡬ࡦࡹࡨࡦࡦࡢ࡭ࡩ࠭⇗"): build_hashed_id,
            }
        else:
            bstack1lll1ll11l1l_opy_[bstack11l1l_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠬ⇘")] = {}
        if bstack1lll1ll11l1l_opy_[bstack11l1l_opy_ (u"࠭࡯ࡣࡵࡨࡶࡻࡧࡢࡪ࡮࡬ࡸࡾ࠭⇙")].get(bstack11l1l_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡥࡨࡢࡵ࡫ࡩࡩࡥࡩࡥࠩ⇚")) != None or bstack1lll1ll11l1l_opy_[bstack11l1l_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠨ⇛")].get(bstack11l1l_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡠࡪࡤࡷ࡭࡫ࡤࡠ࡫ࡧࠫ⇜")) != None:
            cls.bstack1lll1ll111ll_opy_(bstack11111ll1_opy_.get(bstack11l1l_opy_ (u"ࠪ࡮ࡼࡺࠧ⇝")), bstack11111ll1_opy_.get(bstack11l1l_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡢ࡬ࡦࡹࡨࡦࡦࡢ࡭ࡩ࠭⇞")))
        return bstack1lll1ll11l1l_opy_
    @classmethod
    def bstack1lll1ll1111l_opy_(cls, bstack11111ll1_opy_):
        if bstack11111ll1_opy_.get(bstack11l1l_opy_ (u"ࠬࡵࡢࡴࡧࡵࡺࡦࡨࡩ࡭࡫ࡷࡽࠬ⇟")) == None:
            cls.bstack1lll1ll11111_opy_()
            return [None, None, None]
        if bstack11111ll1_opy_[bstack11l1l_opy_ (u"࠭࡯ࡣࡵࡨࡶࡻࡧࡢࡪ࡮࡬ࡸࡾ࠭⇠")][bstack11l1l_opy_ (u"ࠧࡴࡷࡦࡧࡪࡹࡳࠨ⇡")] != True:
            cls.bstack1lll1ll11111_opy_(bstack11111ll1_opy_[bstack11l1l_opy_ (u"ࠨࡱࡥࡷࡪࡸࡶࡢࡤ࡬ࡰ࡮ࡺࡹࠨ⇢")])
            return [None, None, None]
        logger.debug(bstack11l1l_opy_ (u"ࠩࡾࢁࠥࡈࡵࡪ࡮ࡧࠤࡨࡸࡥࡢࡶ࡬ࡳࡳࠦࡓࡶࡥࡦࡩࡸࡹࡦࡶ࡮ࠤࠫ⇣").format(bstack1l111ll1ll_opy_))
        os.environ[bstack11l1l_opy_ (u"ࠪࡆࡘࡥࡔࡆࡕࡗࡓࡕ࡙࡟ࡃࡗࡌࡐࡉࡥࡃࡐࡏࡓࡐࡊ࡚ࡅࡅࠩ⇤")] = bstack11l1l_opy_ (u"ࠫࡹࡸࡵࡦࠩ⇥")
        if bstack11111ll1_opy_.get(bstack11l1l_opy_ (u"ࠬࡰࡷࡵࠩ⇦")):
            os.environ[bstack11l1l_opy_ (u"࠭ࡃࡓࡇࡇࡉࡓ࡚ࡉࡂࡎࡖࡣࡋࡕࡒࡠࡅࡕࡅࡘࡎ࡟ࡓࡇࡓࡓࡗ࡚ࡉࡏࡉࠪ⇧")] = json.dumps({
                bstack11l1l_opy_ (u"ࠧࡶࡵࡨࡶࡳࡧ࡭ࡦࠩ⇨"): bstack11ll111111l_opy_(cls.bs_config),
                bstack11l1l_opy_ (u"ࠨࡲࡤࡷࡸࡽ࡯ࡳࡦࠪ⇩"): bstack11ll11ll1ll_opy_(cls.bs_config)
            })
        if bstack11111ll1_opy_.get(bstack11l1l_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡠࡪࡤࡷ࡭࡫ࡤࡠ࡫ࡧࠫ⇪")):
            os.environ[bstack11l1l_opy_ (u"ࠪࡆࡘࡥࡔࡆࡕࡗࡓࡕ࡙࡟ࡃࡗࡌࡐࡉࡥࡈࡂࡕࡋࡉࡉࡥࡉࡅࠩ⇫")] = bstack11111ll1_opy_[bstack11l1l_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡢ࡬ࡦࡹࡨࡦࡦࡢ࡭ࡩ࠭⇬")]
        if bstack11111ll1_opy_[bstack11l1l_opy_ (u"ࠬࡵࡢࡴࡧࡵࡺࡦࡨࡩ࡭࡫ࡷࡽࠬ⇭")].get(bstack11l1l_opy_ (u"࠭࡯ࡱࡶ࡬ࡳࡳࡹࠧ⇮"), {}).get(bstack11l1l_opy_ (u"ࠧࡢ࡮࡯ࡳࡼࡥࡳࡤࡴࡨࡩࡳࡹࡨࡰࡶࡶࠫ⇯")):
            os.environ[bstack11l1l_opy_ (u"ࠨࡄࡖࡣ࡙ࡋࡓࡕࡑࡓࡗࡤࡇࡌࡍࡑ࡚ࡣࡘࡉࡒࡆࡇࡑࡗࡍࡕࡔࡔࠩ⇰")] = str(bstack11111ll1_opy_[bstack11l1l_opy_ (u"ࠩࡲࡦࡸ࡫ࡲࡷࡣࡥ࡭ࡱ࡯ࡴࡺࠩ⇱")][bstack11l1l_opy_ (u"ࠪࡳࡵࡺࡩࡰࡰࡶࠫ⇲")][bstack11l1l_opy_ (u"ࠫࡦࡲ࡬ࡰࡹࡢࡷࡨࡸࡥࡦࡰࡶ࡬ࡴࡺࡳࠨ⇳")])
        else:
            os.environ[bstack11l1l_opy_ (u"ࠬࡈࡓࡠࡖࡈࡗ࡙ࡕࡐࡔࡡࡄࡐࡑࡕࡗࡠࡕࡆࡖࡊࡋࡎࡔࡊࡒࡘࡘ࠭⇴")] = bstack11l1l_opy_ (u"ࠨ࡮ࡶ࡮࡯ࠦ⇵")
        return [bstack11111ll1_opy_[bstack11l1l_opy_ (u"ࠧ࡫ࡹࡷࠫ⇶")], bstack11111ll1_opy_[bstack11l1l_opy_ (u"ࠨࡤࡸ࡭ࡱࡪ࡟ࡩࡣࡶ࡬ࡪࡪ࡟ࡪࡦࠪ⇷")], os.environ[bstack11l1l_opy_ (u"ࠩࡅࡗࡤ࡚ࡅࡔࡖࡒࡔࡘࡥࡁࡍࡎࡒ࡛ࡤ࡙ࡃࡓࡇࡈࡒࡘࡎࡏࡕࡕࠪ⇸")]]
    @classmethod
    def bstack1lll1ll1llll_opy_(cls, bstack11111ll1_opy_):
        if bstack11111ll1_opy_.get(bstack11l1l_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠪ⇹")) == None:
            cls.bstack1lll1l1lllll_opy_()
            return [None, None]
        if bstack11111ll1_opy_[bstack11l1l_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠫ⇺")][bstack11l1l_opy_ (u"ࠬࡹࡵࡤࡥࡨࡷࡸ࠭⇻")] != True:
            cls.bstack1lll1l1lllll_opy_(bstack11111ll1_opy_[bstack11l1l_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾ࠭⇼")])
            return [None, None]
        if bstack11111ll1_opy_[bstack11l1l_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠧ⇽")].get(bstack11l1l_opy_ (u"ࠨࡱࡳࡸ࡮ࡵ࡮ࡴࠩ⇾")):
            logger.debug(bstack11l1l_opy_ (u"ࠩࡗࡩࡸࡺࠠࡂࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡃࡷ࡬ࡰࡩࠦࡣࡳࡧࡤࡸ࡮ࡵ࡮ࠡࡕࡸࡧࡨ࡫ࡳࡴࡨࡸࡰࠦ࠭⇿"))
            parsed = json.loads(os.getenv(bstack11l1l_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡉࡘ࡚࡟ࡂࡅࡆࡉࡘ࡙ࡉࡃࡋࡏࡍ࡙࡟࡟ࡄࡑࡑࡊࡎࡍࡕࡓࡃࡗࡍࡔࡔ࡟࡚ࡏࡏࠫ∀"), bstack11l1l_opy_ (u"ࠫࢀࢃࠧ∁")))
            capabilities = bstack1ll11l1l1_opy_.bstack1lll1ll11ll1_opy_(bstack11111ll1_opy_[bstack11l1l_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠬ∂")][bstack11l1l_opy_ (u"࠭࡯ࡱࡶ࡬ࡳࡳࡹࠧ∃")][bstack11l1l_opy_ (u"ࠧࡤࡣࡳࡥࡧ࡯࡬ࡪࡶ࡬ࡩࡸ࠭∄")], bstack11l1l_opy_ (u"ࠨࡰࡤࡱࡪ࠭∅"), bstack11l1l_opy_ (u"ࠩࡹࡥࡱࡻࡥࠨ∆"))
            bstack1lll1ll1ll1l_opy_ = capabilities[bstack11l1l_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࡗࡳࡰ࡫࡮ࠨ∇")]
            os.environ[bstack11l1l_opy_ (u"ࠫࡇ࡙࡟ࡂ࠳࠴࡝ࡤࡐࡗࡕࠩ∈")] = bstack1lll1ll1ll1l_opy_
            if bstack11l1l_opy_ (u"ࠧࡧࡵࡵࡱࡰࡥࡹ࡫ࠢ∉") in bstack11111ll1_opy_ and bstack11111ll1_opy_.get(bstack11l1l_opy_ (u"ࠨࡡࡱࡲࡢࡥࡺࡺ࡯࡮ࡣࡷࡩࠧ∊")) is None:
                parsed[bstack11l1l_opy_ (u"ࠧࡴࡥࡤࡲࡳ࡫ࡲࡗࡧࡵࡷ࡮ࡵ࡮ࠨ∋")] = capabilities[bstack11l1l_opy_ (u"ࠨࡵࡦࡥࡳࡴࡥࡳࡘࡨࡶࡸ࡯࡯࡯ࠩ∌")]
            os.environ[bstack11l1l_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡥࡁࡄࡅࡈࡗࡘࡏࡂࡊࡎࡌࡘ࡞ࡥࡃࡐࡐࡉࡍࡌ࡛ࡒࡂࡖࡌࡓࡓࡥ࡙ࡎࡎࠪ∍")] = json.dumps(parsed)
            scripts = bstack1ll11l1l1_opy_.bstack1lll1ll11ll1_opy_(bstack11111ll1_opy_[bstack11l1l_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠪ∎")][bstack11l1l_opy_ (u"ࠫࡴࡶࡴࡪࡱࡱࡷࠬ∏")][bstack11l1l_opy_ (u"ࠬࡹࡣࡳ࡫ࡳࡸࡸ࠭∐")], bstack11l1l_opy_ (u"࠭࡮ࡢ࡯ࡨࠫ∑"), bstack11l1l_opy_ (u"ࠧࡤࡱࡰࡱࡦࡴࡤࠨ−"))
            bstack111lll1l_opy_.bstack1111ll1ll_opy_(scripts)
            commands = bstack11111ll1_opy_[bstack11l1l_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠨ∓")][bstack11l1l_opy_ (u"ࠩࡲࡴࡹ࡯࡯࡯ࡵࠪ∔")][bstack11l1l_opy_ (u"ࠪࡧࡴࡳ࡭ࡢࡰࡧࡷ࡙ࡵࡗࡳࡣࡳࠫ∕")].get(bstack11l1l_opy_ (u"ࠫࡨࡵ࡭࡮ࡣࡱࡨࡸ࠭∖"))
            bstack111lll1l_opy_.bstack11ll11111ll_opy_(commands)
            bstack11l1llll11l_opy_ = capabilities.get(bstack11l1l_opy_ (u"ࠬ࡭࡯ࡰࡩ࠽ࡧ࡭ࡸ࡯࡮ࡧࡒࡴࡹ࡯࡯࡯ࡵࠪ∗"))
            bstack111lll1l_opy_.bstack11l1ll1llll_opy_(bstack11l1llll11l_opy_)
            bstack111lll1l_opy_.store()
        return [bstack1lll1ll1ll1l_opy_, bstack11111ll1_opy_[bstack11l1l_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡤ࡮ࡡࡴࡪࡨࡨࡤ࡯ࡤࠨ∘")]]
    @classmethod
    def bstack1lll1ll11111_opy_(cls, response=None):
        os.environ[bstack11l1l_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡌ࡚ࡈ࡟ࡖࡗࡌࡈࠬ∙")] = bstack11l1l_opy_ (u"ࠨࡰࡸࡰࡱ࠭√")
        os.environ[bstack11l1l_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡍ࡛࡙࠭∛")] = bstack11l1l_opy_ (u"ࠪࡲࡺࡲ࡬ࠨ∜")
        os.environ[bstack11l1l_opy_ (u"ࠫࡇ࡙࡟ࡕࡇࡖࡘࡔࡖࡓࡠࡄࡘࡍࡑࡊ࡟ࡄࡑࡐࡔࡑࡋࡔࡆࡆࠪ∝")] = bstack11l1l_opy_ (u"ࠬ࡬ࡡ࡭ࡵࡨࠫ∞")
        os.environ[bstack11l1l_opy_ (u"࠭ࡂࡔࡡࡗࡉࡘ࡚ࡏࡑࡕࡢࡆ࡚ࡏࡌࡅࡡࡋࡅࡘࡎࡅࡅࡡࡌࡈࠬ∟")] = bstack11l1l_opy_ (u"ࠢ࡯ࡷ࡯ࡰࠧ∠")
        os.environ[bstack11l1l_opy_ (u"ࠨࡄࡖࡣ࡙ࡋࡓࡕࡑࡓࡗࡤࡇࡌࡍࡑ࡚ࡣࡘࡉࡒࡆࡇࡑࡗࡍࡕࡔࡔࠩ∡")] = bstack11l1l_opy_ (u"ࠤࡱࡹࡱࡲࠢ∢")
        cls.bstack1lll1ll1lll1_opy_(response, bstack11l1l_opy_ (u"ࠥࡳࡧࡹࡥࡳࡸࡤࡦ࡮ࡲࡩࡵࡻࠥ∣"))
        return [None, None, None]
    @classmethod
    def bstack1lll1l1lllll_opy_(cls, response=None):
        os.environ[bstack11l1l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡉࡗࡅࡣ࡚࡛ࡉࡅࠩ∤")] = bstack11l1l_opy_ (u"ࠬࡴࡵ࡭࡮ࠪ∥")
        os.environ[bstack11l1l_opy_ (u"࠭ࡂࡔࡡࡄ࠵࠶࡟࡟ࡋ࡙ࡗࠫ∦")] = bstack11l1l_opy_ (u"ࠧ࡯ࡷ࡯ࡰࠬ∧")
        os.environ[bstack11l1l_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡍ࡛ࡂࡠࡌ࡚ࡘࠬ∨")] = bstack11l1l_opy_ (u"ࠩࡱࡹࡱࡲࠧ∩")
        cls.bstack1lll1ll1lll1_opy_(response, bstack11l1l_opy_ (u"ࠥࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠥ∪"))
        return [None, None, None]
    @classmethod
    def bstack1lll1ll111ll_opy_(cls, jwt, build_hashed_id):
        os.environ[bstack11l1l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡉࡗࡅࡣࡏ࡝ࡔࠨ∫")] = jwt
        os.environ[bstack11l1l_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡊࡘࡆࡤ࡛ࡕࡊࡆࠪ∬")] = build_hashed_id
    @classmethod
    def bstack1lll1ll1lll1_opy_(cls, response=None, product=bstack11l1l_opy_ (u"ࠨࠢ∭")):
        if response == None or response.get(bstack11l1l_opy_ (u"ࠧࡦࡴࡵࡳࡷࡹࠧ∮")) == None:
            logger.error(product + bstack11l1l_opy_ (u"ࠣࠢࡅࡹ࡮ࡲࡤࠡࡥࡵࡩࡦࡺࡩࡰࡰࠣࡪࡦ࡯࡬ࡦࡦࠥ∯"))
            return
        for error in response[bstack11l1l_opy_ (u"ࠩࡨࡶࡷࡵࡲࡴࠩ∰")]:
            bstack11l1111ll1l_opy_ = error[bstack11l1l_opy_ (u"ࠪ࡯ࡪࡿࠧ∱")]
            error_message = error[bstack11l1l_opy_ (u"ࠫࡲ࡫ࡳࡴࡣࡪࡩࠬ∲")]
            if error_message:
                if bstack11l1111ll1l_opy_ == bstack11l1l_opy_ (u"ࠧࡋࡒࡓࡑࡕࡣࡆࡉࡃࡆࡕࡖࡣࡉࡋࡎࡊࡇࡇࠦ∳"):
                    logger.info(error_message)
                else:
                    logger.error(error_message)
            else:
                logger.error(bstack11l1l_opy_ (u"ࠨࡄࡢࡶࡤࠤࡺࡶ࡬ࡰࡣࡧࠤࡹࡵࠠࡃࡴࡲࡻࡸ࡫ࡲࡔࡶࡤࡧࡰࠦࠢ∴") + product + bstack11l1l_opy_ (u"ࠢࠡࡨࡤ࡭ࡱ࡫ࡤࠡࡦࡸࡩࠥࡺ࡯ࠡࡵࡲࡱࡪࠦࡥࡳࡴࡲࡶࠧ∵"))
    @classmethod
    def bstack1lll1lll1lll_opy_(cls):
        if cls.bstack1llll1ll1111_opy_ is not None:
            return
        cls.bstack1llll1ll1111_opy_ = bstack1llll1ll11ll_opy_(cls.bstack1lll1lll1111_opy_)
        cls.bstack1llll1ll1111_opy_.start()
    @classmethod
    def bstack1111ll1111_opy_(cls):
        if cls.bstack1llll1ll1111_opy_ is None:
            return
        cls.bstack1llll1ll1111_opy_.shutdown()
    @classmethod
    @error_handler(class_method=True)
    def bstack1lll1lll1111_opy_(cls, bstack111l11l1l1_opy_, event_url=bstack11l1l_opy_ (u"ࠨࡣࡳ࡭࠴ࡼ࠱࠰ࡤࡤࡸࡨ࡮ࠧ∶")):
        config = {
            bstack11l1l_opy_ (u"ࠩ࡫ࡩࡦࡪࡥࡳࡵࠪ∷"): cls.default_headers()
        }
        logger.debug(bstack11l1l_opy_ (u"ࠥࡴࡴࡹࡴࡠࡦࡤࡸࡦࡀࠠࡔࡧࡱࡨ࡮ࡴࡧࠡࡦࡤࡸࡦࠦࡴࡰࠢࡷࡩࡸࡺࡨࡶࡤࠣࡪࡴࡸࠠࡦࡸࡨࡲࡹࡹࠠࡼࡿࠥ∸").format(bstack11l1l_opy_ (u"ࠫ࠱ࠦࠧ∹").join([event[bstack11l1l_opy_ (u"ࠬ࡫ࡶࡦࡰࡷࡣࡹࡿࡰࡦࠩ∺")] for event in bstack111l11l1l1_opy_])))
        response = bstack1l111l111l_opy_(bstack11l1l_opy_ (u"࠭ࡐࡐࡕࡗࠫ∻"), cls.request_url(event_url), bstack111l11l1l1_opy_, config)
        bstack11ll11ll111_opy_ = response.json()
    @classmethod
    def bstack1ll1l1111l_opy_(cls, bstack111l11l1l1_opy_, event_url=bstack11l1l_opy_ (u"ࠧࡢࡲ࡬࠳ࡻ࠷࠯ࡣࡣࡷࡧ࡭࠭∼")):
        logger.debug(bstack11l1l_opy_ (u"ࠣࡵࡨࡲࡩࡥࡤࡢࡶࡤ࠾ࠥࡇࡴࡵࡧࡰࡴࡹ࡯࡮ࡨࠢࡷࡳࠥࡧࡤࡥࠢࡧࡥࡹࡧࠠࡵࡱࠣࡦࡦࡺࡣࡩࠢࡺ࡭ࡹ࡮ࠠࡦࡸࡨࡲࡹࡥࡴࡺࡲࡨ࠾ࠥࢁࡽࠣ∽").format(bstack111l11l1l1_opy_[bstack11l1l_opy_ (u"ࠩࡨࡺࡪࡴࡴࡠࡶࡼࡴࡪ࠭∾")]))
        if not bstack1ll11l1l1_opy_.bstack1lll1lll11ll_opy_(bstack111l11l1l1_opy_[bstack11l1l_opy_ (u"ࠪࡩࡻ࡫࡮ࡵࡡࡷࡽࡵ࡫ࠧ∿")]):
            logger.debug(bstack11l1l_opy_ (u"ࠦࡸ࡫࡮ࡥࡡࡧࡥࡹࡧ࠺ࠡࡐࡲࡸࠥࡧࡤࡥ࡫ࡱ࡫ࠥࡪࡡࡵࡣࠣࡻ࡮ࡺࡨࠡࡧࡹࡩࡳࡺ࡟ࡵࡻࡳࡩ࠿ࠦࡻࡾࠤ≀").format(bstack111l11l1l1_opy_[bstack11l1l_opy_ (u"ࠬ࡫ࡶࡦࡰࡷࡣࡹࡿࡰࡦࠩ≁")]))
            return
        bstack11l1111ll1_opy_ = bstack1ll11l1l1_opy_.bstack1lll1ll11lll_opy_(bstack111l11l1l1_opy_[bstack11l1l_opy_ (u"࠭ࡥࡷࡧࡱࡸࡤࡺࡹࡱࡧࠪ≂")], bstack111l11l1l1_opy_.get(bstack11l1l_opy_ (u"ࠧࡵࡧࡶࡸࡤࡸࡵ࡯ࠩ≃")))
        if bstack11l1111ll1_opy_ != None:
            if bstack111l11l1l1_opy_.get(bstack11l1l_opy_ (u"ࠨࡶࡨࡷࡹࡥࡲࡶࡰࠪ≄")) != None:
                bstack111l11l1l1_opy_[bstack11l1l_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡳࡷࡱࠫ≅")][bstack11l1l_opy_ (u"ࠪࡴࡷࡵࡤࡶࡥࡷࡣࡲࡧࡰࠨ≆")] = bstack11l1111ll1_opy_
            else:
                bstack111l11l1l1_opy_[bstack11l1l_opy_ (u"ࠫࡵࡸ࡯ࡥࡷࡦࡸࡤࡳࡡࡱࠩ≇")] = bstack11l1111ll1_opy_
        if event_url == bstack11l1l_opy_ (u"ࠬࡧࡰࡪ࠱ࡹ࠵࠴ࡨࡡࡵࡥ࡫ࠫ≈"):
            cls.bstack1lll1lll1lll_opy_()
            logger.debug(bstack11l1l_opy_ (u"ࠨࡳࡦࡰࡧࡣࡩࡧࡴࡢ࠼ࠣࡅࡩࡪࡩ࡯ࡩࠣࡨࡦࡺࡡࠡࡶࡲࠤࡧࡧࡴࡤࡪࠣࡻ࡮ࡺࡨࠡࡧࡹࡩࡳࡺ࡟ࡵࡻࡳࡩ࠿ࠦࡻࡾࠤ≉").format(bstack111l11l1l1_opy_[bstack11l1l_opy_ (u"ࠧࡦࡸࡨࡲࡹࡥࡴࡺࡲࡨࠫ≊")]))
            cls.bstack1llll1ll1111_opy_.add(bstack111l11l1l1_opy_)
        elif event_url == bstack11l1l_opy_ (u"ࠨࡣࡳ࡭࠴ࡼ࠱࠰ࡵࡦࡶࡪ࡫࡮ࡴࡪࡲࡸࡸ࠭≋"):
            cls.bstack1lll1lll1111_opy_([bstack111l11l1l1_opy_], event_url)
    @classmethod
    @error_handler(class_method=True)
    def bstack11lllll1l_opy_(cls, logs):
        for log in logs:
            bstack1lll1lll11l1_opy_ = {
                bstack11l1l_opy_ (u"ࠩ࡮࡭ࡳࡪࠧ≌"): bstack11l1l_opy_ (u"ࠪࡘࡊ࡙ࡔࡠࡎࡒࡋࠬ≍"),
                bstack11l1l_opy_ (u"ࠫࡱ࡫ࡶࡦ࡮ࠪ≎"): log[bstack11l1l_opy_ (u"ࠬࡲࡥࡷࡧ࡯ࠫ≏")],
                bstack11l1l_opy_ (u"࠭ࡴࡪ࡯ࡨࡷࡹࡧ࡭ࡱࠩ≐"): log[bstack11l1l_opy_ (u"ࠧࡵ࡫ࡰࡩࡸࡺࡡ࡮ࡲࠪ≑")],
                bstack11l1l_opy_ (u"ࠨࡪࡷࡸࡵࡥࡲࡦࡵࡳࡳࡳࡹࡥࠨ≒"): {},
                bstack11l1l_opy_ (u"ࠩࡰࡩࡸࡹࡡࡨࡧࠪ≓"): log[bstack11l1l_opy_ (u"ࠪࡱࡪࡹࡳࡢࡩࡨࠫ≔")],
            }
            if bstack11l1l_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡵࡹࡳࡥࡵࡶ࡫ࡧࠫ≕") in log:
                bstack1lll1lll11l1_opy_[bstack11l1l_opy_ (u"ࠬࡺࡥࡴࡶࡢࡶࡺࡴ࡟ࡶࡷ࡬ࡨࠬ≖")] = log[bstack11l1l_opy_ (u"࠭ࡴࡦࡵࡷࡣࡷࡻ࡮ࡠࡷࡸ࡭ࡩ࠭≗")]
            elif bstack11l1l_opy_ (u"ࠧࡩࡱࡲ࡯ࡤࡸࡵ࡯ࡡࡸࡹ࡮ࡪࠧ≘") in log:
                bstack1lll1lll11l1_opy_[bstack11l1l_opy_ (u"ࠨࡪࡲࡳࡰࡥࡲࡶࡰࡢࡹࡺ࡯ࡤࠨ≙")] = log[bstack11l1l_opy_ (u"ࠩ࡫ࡳࡴࡱ࡟ࡳࡷࡱࡣࡺࡻࡩࡥࠩ≚")]
            cls.bstack1ll1l1111l_opy_({
                bstack11l1l_opy_ (u"ࠪࡩࡻ࡫࡮ࡵࡡࡷࡽࡵ࡫ࠧ≛"): bstack11l1l_opy_ (u"ࠫࡑࡵࡧࡄࡴࡨࡥࡹ࡫ࡤࠨ≜"),
                bstack11l1l_opy_ (u"ࠬࡲ࡯ࡨࡵࠪ≝"): [bstack1lll1lll11l1_opy_]
            })
    @classmethod
    @error_handler(class_method=True)
    def bstack1lll1lll1l11_opy_(cls, steps):
        bstack1lll1llll111_opy_ = []
        for step in steps:
            bstack1lll1ll1l1l1_opy_ = {
                bstack11l1l_opy_ (u"࠭࡫ࡪࡰࡧࠫ≞"): bstack11l1l_opy_ (u"ࠧࡕࡇࡖࡘࡤ࡙ࡔࡆࡒࠪ≟"),
                bstack11l1l_opy_ (u"ࠨ࡮ࡨࡺࡪࡲࠧ≠"): step[bstack11l1l_opy_ (u"ࠩ࡯ࡩࡻ࡫࡬ࠨ≡")],
                bstack11l1l_opy_ (u"ࠪࡸ࡮ࡳࡥࡴࡶࡤࡱࡵ࠭≢"): step[bstack11l1l_opy_ (u"ࠫࡹ࡯࡭ࡦࡵࡷࡥࡲࡶࠧ≣")],
                bstack11l1l_opy_ (u"ࠬࡳࡥࡴࡵࡤ࡫ࡪ࠭≤"): step[bstack11l1l_opy_ (u"࠭࡭ࡦࡵࡶࡥ࡬࡫ࠧ≥")],
                bstack11l1l_opy_ (u"ࠧࡥࡷࡵࡥࡹ࡯࡯࡯ࠩ≦"): step[bstack11l1l_opy_ (u"ࠨࡦࡸࡶࡦࡺࡩࡰࡰࠪ≧")]
            }
            if bstack11l1l_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡳࡷࡱࡣࡺࡻࡩࡥࠩ≨") in step:
                bstack1lll1ll1l1l1_opy_[bstack11l1l_opy_ (u"ࠪࡸࡪࡹࡴࡠࡴࡸࡲࡤࡻࡵࡪࡦࠪ≩")] = step[bstack11l1l_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡵࡹࡳࡥࡵࡶ࡫ࡧࠫ≪")]
            elif bstack11l1l_opy_ (u"ࠬ࡮࡯ࡰ࡭ࡢࡶࡺࡴ࡟ࡶࡷ࡬ࡨࠬ≫") in step:
                bstack1lll1ll1l1l1_opy_[bstack11l1l_opy_ (u"࠭ࡨࡰࡱ࡮ࡣࡷࡻ࡮ࡠࡷࡸ࡭ࡩ࠭≬")] = step[bstack11l1l_opy_ (u"ࠧࡩࡱࡲ࡯ࡤࡸࡵ࡯ࡡࡸࡹ࡮ࡪࠧ≭")]
            bstack1lll1llll111_opy_.append(bstack1lll1ll1l1l1_opy_)
        cls.bstack1ll1l1111l_opy_({
            bstack11l1l_opy_ (u"ࠨࡧࡹࡩࡳࡺ࡟ࡵࡻࡳࡩࠬ≮"): bstack11l1l_opy_ (u"ࠩࡏࡳ࡬ࡉࡲࡦࡣࡷࡩࡩ࠭≯"),
            bstack11l1l_opy_ (u"ࠪࡰࡴ࡭ࡳࠨ≰"): bstack1lll1llll111_opy_
        })
    @classmethod
    @error_handler(class_method=True)
    @measure(event_name=EVENTS.bstack1llllllll1_opy_, stage=STAGE.bstack1lll1l11l_opy_)
    def bstack1l1lll111l_opy_(cls, screenshot):
        cls.bstack1ll1l1111l_opy_({
            bstack11l1l_opy_ (u"ࠫࡪࡼࡥ࡯ࡶࡢࡸࡾࡶࡥࠨ≱"): bstack11l1l_opy_ (u"ࠬࡒ࡯ࡨࡅࡵࡩࡦࡺࡥࡥࠩ≲"),
            bstack11l1l_opy_ (u"࠭࡬ࡰࡩࡶࠫ≳"): [{
                bstack11l1l_opy_ (u"ࠧ࡬࡫ࡱࡨࠬ≴"): bstack11l1l_opy_ (u"ࠨࡖࡈࡗ࡙ࡥࡓࡄࡔࡈࡉࡓ࡙ࡈࡐࡖࠪ≵"),
                bstack11l1l_opy_ (u"ࠩࡷ࡭ࡲ࡫ࡳࡵࡣࡰࡴࠬ≶"): datetime.datetime.utcnow().isoformat() + bstack11l1l_opy_ (u"ࠪ࡞ࠬ≷"),
                bstack11l1l_opy_ (u"ࠫࡲ࡫ࡳࡴࡣࡪࡩࠬ≸"): screenshot[bstack11l1l_opy_ (u"ࠬ࡯࡭ࡢࡩࡨࠫ≹")],
                bstack11l1l_opy_ (u"࠭ࡴࡦࡵࡷࡣࡷࡻ࡮ࡠࡷࡸ࡭ࡩ࠭≺"): screenshot[bstack11l1l_opy_ (u"ࠧࡵࡧࡶࡸࡤࡸࡵ࡯ࡡࡸࡹ࡮ࡪࠧ≻")]
            }]
        }, event_url=bstack11l1l_opy_ (u"ࠨࡣࡳ࡭࠴ࡼ࠱࠰ࡵࡦࡶࡪ࡫࡮ࡴࡪࡲࡸࡸ࠭≼"))
    @classmethod
    @error_handler(class_method=True)
    def bstack1llll1llll_opy_(cls, driver):
        current_test_uuid = cls.current_test_uuid()
        if not current_test_uuid:
            return
        cls.bstack1ll1l1111l_opy_({
            bstack11l1l_opy_ (u"ࠩࡨࡺࡪࡴࡴࡠࡶࡼࡴࡪ࠭≽"): bstack11l1l_opy_ (u"ࠪࡇࡇ࡚ࡓࡦࡵࡶ࡭ࡴࡴࡃࡳࡧࡤࡸࡪࡪࠧ≾"),
            bstack11l1l_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡵࡹࡳ࠭≿"): {
                bstack11l1l_opy_ (u"ࠧࡻࡵࡪࡦࠥ⊀"): cls.current_test_uuid(),
                bstack11l1l_opy_ (u"ࠨࡩ࡯ࡶࡨ࡫ࡷࡧࡴࡪࡱࡱࡷࠧ⊁"): cls.bstack111ll11l11_opy_(driver)
            }
        })
    @classmethod
    def bstack111ll11ll1_opy_(cls, event: str, bstack111l11l1l1_opy_: bstack1111l11ll1_opy_):
        bstack1111ll111l_opy_ = {
            bstack11l1l_opy_ (u"ࠧࡦࡸࡨࡲࡹࡥࡴࡺࡲࡨࠫ⊂"): event,
            bstack111l11l1l1_opy_.bstack1111l11l11_opy_(): bstack111l11l1l1_opy_.bstack1111l1l111_opy_(event)
        }
        cls.bstack1ll1l1111l_opy_(bstack1111ll111l_opy_)
        result = getattr(bstack111l11l1l1_opy_, bstack11l1l_opy_ (u"ࠨࡴࡨࡷࡺࡲࡴࠨ⊃"), None)
        if event == bstack11l1l_opy_ (u"ࠩࡗࡩࡸࡺࡒࡶࡰࡖࡸࡦࡸࡴࡦࡦࠪ⊄"):
            threading.current_thread().bstackTestMeta = {bstack11l1l_opy_ (u"ࠪࡷࡹࡧࡴࡶࡵࠪ⊅"): bstack11l1l_opy_ (u"ࠫࡵ࡫࡮ࡥ࡫ࡱ࡫ࠬ⊆")}
        elif event == bstack11l1l_opy_ (u"࡚ࠬࡥࡴࡶࡕࡹࡳࡌࡩ࡯࡫ࡶ࡬ࡪࡪࠧ⊇"):
            threading.current_thread().bstackTestMeta = {bstack11l1l_opy_ (u"࠭ࡳࡵࡣࡷࡹࡸ࠭⊈"): getattr(result, bstack11l1l_opy_ (u"ࠧࡳࡧࡶࡹࡱࡺࠧ⊉"), bstack11l1l_opy_ (u"ࠨࠩ⊊"))}
    @classmethod
    def on(cls):
        if (os.environ.get(bstack11l1l_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡍ࡛࡙࠭⊋"), None) is None or os.environ[bstack11l1l_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡉࡘ࡚ࡈࡖࡄࡢࡎ࡜࡚ࠧ⊌")] == bstack11l1l_opy_ (u"ࠦࡳࡻ࡬࡭ࠤ⊍")) and (os.environ.get(bstack11l1l_opy_ (u"ࠬࡈࡓࡠࡃ࠴࠵࡞ࡥࡊࡘࡖࠪ⊎"), None) is None or os.environ[bstack11l1l_opy_ (u"࠭ࡂࡔࡡࡄ࠵࠶࡟࡟ࡋ࡙ࡗࠫ⊏")] == bstack11l1l_opy_ (u"ࠢ࡯ࡷ࡯ࡰࠧ⊐")):
            return False
        return True
    @staticmethod
    def bstack1lll1ll1l11l_opy_(func):
        def wrap(*args, **kwargs):
            if bstack1ll1llll11_opy_.on():
                return func(*args, **kwargs)
            return
        return wrap
    @staticmethod
    def default_headers():
        headers = {
            bstack11l1l_opy_ (u"ࠨࡅࡲࡲࡹ࡫࡮ࡵ࠯ࡗࡽࡵ࡫ࠧ⊑"): bstack11l1l_opy_ (u"ࠩࡤࡴࡵࡲࡩࡤࡣࡷ࡭ࡴࡴ࠯࡫ࡵࡲࡲࠬ⊒"),
            bstack11l1l_opy_ (u"ࠪ࡜࠲ࡈࡓࡕࡃࡆࡏ࠲࡚ࡅࡔࡖࡒࡔࡘ࠭⊓"): bstack11l1l_opy_ (u"ࠫࡹࡸࡵࡦࠩ⊔")
        }
        if os.environ.get(bstack11l1l_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡊࡘࡆࡤࡐࡗࡕࠩ⊕"), None):
            headers[bstack11l1l_opy_ (u"࠭ࡁࡶࡶ࡫ࡳࡷ࡯ࡺࡢࡶ࡬ࡳࡳ࠭⊖")] = bstack11l1l_opy_ (u"ࠧࡃࡧࡤࡶࡪࡸࠠࡼࡿࠪ⊗").format(os.environ[bstack11l1l_opy_ (u"ࠣࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡍ࡛ࡂࡠࡌ࡚ࡘࠧ⊘")])
        return headers
    @staticmethod
    def request_url(url):
        return bstack11l1l_opy_ (u"ࠩࡾࢁ࠴ࢁࡽࠨ⊙").format(bstack1lll1lll1ll1_opy_, url)
    @staticmethod
    def current_test_uuid():
        return getattr(threading.current_thread(), bstack11l1l_opy_ (u"ࠪࡧࡺࡸࡲࡦࡰࡷࡣࡹ࡫ࡳࡵࡡࡸࡹ࡮ࡪࠧ⊚"), None)
    @staticmethod
    def bstack111ll11l11_opy_(driver):
        return {
            bstack111llllllll_opy_(): bstack111lll111l1_opy_(driver)
        }
    @staticmethod
    def bstack1lll1ll111l1_opy_(exception_info, report):
        return [{bstack11l1l_opy_ (u"ࠫࡧࡧࡣ࡬ࡶࡵࡥࡨ࡫ࠧ⊛"): [exception_info.exconly(), report.longreprtext]}]
    @staticmethod
    def bstack1lllll1ll1l_opy_(typename):
        if bstack11l1l_opy_ (u"ࠧࡇࡳࡴࡧࡵࡸ࡮ࡵ࡮ࠣ⊜") in typename:
            return bstack11l1l_opy_ (u"ࠨࡁࡴࡵࡨࡶࡹ࡯࡯࡯ࡇࡵࡶࡴࡸࠢ⊝")
        return bstack11l1l_opy_ (u"ࠢࡖࡰ࡫ࡥࡳࡪ࡬ࡦࡦࡈࡶࡷࡵࡲࠣ⊞")