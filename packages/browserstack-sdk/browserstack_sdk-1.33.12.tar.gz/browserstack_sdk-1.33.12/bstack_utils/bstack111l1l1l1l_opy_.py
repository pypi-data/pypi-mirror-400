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
import json
import logging
import os
import datetime
import threading
from bstack_utils.constants import EVENTS, STAGE
from bstack_utils.helper import bstack11ll11l11l1_opy_, bstack11l1llll111_opy_, bstack11l1l1l11l_opy_, error_handler, bstack11l111111l1_opy_, bstack111lll111ll_opy_, bstack11l111l1lll_opy_, bstack111lll1lll_opy_, bstack1lll11l1l_opy_
from bstack_utils.measure import measure
from bstack_utils.bstack1llll1ll111l_opy_ import bstack1llll1ll1l11_opy_
import bstack_utils.bstack1l111l11ll_opy_ as bstack1l11111ll1_opy_
from bstack_utils.bstack111ll11lll_opy_ import bstack1l11llll1l_opy_
import bstack_utils.accessibility as bstack1l1ll11l1l_opy_
from bstack_utils.bstack1l11l111l1_opy_ import bstack1l11l111l1_opy_
from bstack_utils.bstack111l1ll11l_opy_ import bstack111l111lll_opy_
from bstack_utils.constants import bstack111ll1ll1_opy_
bstack1lll1lll11l1_opy_ = bstack11ll1_opy_ (u"ࠨࡪࡷࡸࡵࡹ࠺࠰࠱ࡦࡳࡱࡲࡥࡤࡶࡲࡶ࠲ࡵࡢࡴࡧࡵࡺࡦࡨࡩ࡭࡫ࡷࡽ࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡨࡵ࡭ࠨ↣")
logger = logging.getLogger(__name__)
class bstack11lll11l11_opy_:
    bstack1llll1ll111l_opy_ = None
    bs_config = None
    bstack11l111111_opy_ = None
    @classmethod
    @error_handler(class_method=True)
    @measure(event_name=EVENTS.bstack11l1l111ll1_opy_, stage=STAGE.bstack11l1llll1_opy_)
    def launch(cls, bs_config, bstack11l111111_opy_):
        cls.bs_config = bs_config
        cls.bstack11l111111_opy_ = bstack11l111111_opy_
        try:
            cls.bstack1lll1ll1lll1_opy_()
            bstack11ll1111ll1_opy_ = bstack11ll11l11l1_opy_(bs_config)
            bstack11ll1111111_opy_ = bstack11l1llll111_opy_(bs_config)
            data = bstack1l11111ll1_opy_.bstack1lll1lll1l1l_opy_(bs_config, bstack11l111111_opy_)
            config = {
                bstack11ll1_opy_ (u"ࠩࡤࡹࡹ࡮ࠧ↤"): (bstack11ll1111ll1_opy_, bstack11ll1111111_opy_),
                bstack11ll1_opy_ (u"ࠪ࡬ࡪࡧࡤࡦࡴࡶࠫ↥"): cls.default_headers()
            }
            response = bstack11l1l1l11l_opy_(bstack11ll1_opy_ (u"ࠫࡕࡕࡓࡕࠩ↦"), cls.request_url(bstack11ll1_opy_ (u"ࠬࡧࡰࡪ࠱ࡹ࠶࠴ࡨࡵࡪ࡮ࡧࡷࠬ↧")), data, config)
            if response.status_code != 200:
                bstack1lllll1l1_opy_ = response.json()
                if bstack1lllll1l1_opy_[bstack11ll1_opy_ (u"࠭ࡳࡶࡥࡦࡩࡸࡹࠧ↨")] == False:
                    cls.bstack1lll1ll1ll1l_opy_(bstack1lllll1l1_opy_)
                    return
                cls.bstack1lll1ll11l1l_opy_(bstack1lllll1l1_opy_[bstack11ll1_opy_ (u"ࠧࡰࡤࡶࡩࡷࡼࡡࡣ࡫࡯࡭ࡹࡿࠧ↩")])
                cls.bstack1lll1ll1111l_opy_(bstack1lllll1l1_opy_[bstack11ll1_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠨ↪")])
                return None
            bstack1lll1lll111l_opy_ = cls.bstack1lll1llll111_opy_(response)
            return bstack1lll1lll111l_opy_, response.json()
        except Exception as error:
            logger.error(bstack11ll1_opy_ (u"ࠤࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥࡽࡨࡪ࡮ࡨࠤࡨࡸࡥࡢࡶ࡬ࡲ࡬ࠦࡢࡶ࡫࡯ࡨࠥ࡬࡯ࡳࠢࡗࡩࡸࡺࡈࡶࡤ࠽ࠤࢀࢃࠢ↫").format(str(error)))
            return None
    @classmethod
    @error_handler(class_method=True)
    def stop(cls, bstack1lll1ll11ll1_opy_=None):
        if not bstack1l11llll1l_opy_.on() and not bstack1l1ll11l1l_opy_.on():
            return
        if os.environ.get(bstack11ll1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡉࡘ࡚ࡈࡖࡄࡢࡎ࡜࡚ࠧ↬")) == bstack11ll1_opy_ (u"ࠦࡳࡻ࡬࡭ࠤ↭") or os.environ.get(bstack11ll1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡊࡘࡆࡤ࡛ࡕࡊࡆࠪ↮")) == bstack11ll1_opy_ (u"ࠨ࡮ࡶ࡮࡯ࠦ↯"):
            logger.error(bstack11ll1_opy_ (u"ࠧࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣ࡭ࡳࠦࡳࡵࡱࡳࠤࡧࡻࡩ࡭ࡦࠣࡶࡪࡷࡵࡦࡵࡷࠤࡹࡵࠠࡕࡧࡶࡸࡍࡻࡢ࠻ࠢࡐ࡭ࡸࡹࡩ࡯ࡩࠣࡥࡺࡺࡨࡦࡰࡷ࡭ࡨࡧࡴࡪࡱࡱࠤࡹࡵ࡫ࡦࡰࠪ↰"))
            return {
                bstack11ll1_opy_ (u"ࠨࡵࡷࡥࡹࡻࡳࠨ↱"): bstack11ll1_opy_ (u"ࠩࡨࡶࡷࡵࡲࠨ↲"),
                bstack11ll1_opy_ (u"ࠪࡱࡪࡹࡳࡢࡩࡨࠫ↳"): bstack11ll1_opy_ (u"࡙ࠫࡵ࡫ࡦࡰ࠲ࡦࡺ࡯࡬ࡥࡋࡇࠤ࡮ࡹࠠࡶࡰࡧࡩ࡫࡯࡮ࡦࡦ࠯ࠤࡧࡻࡩ࡭ࡦࠣࡧࡷ࡫ࡡࡵ࡫ࡲࡲࠥࡳࡩࡨࡪࡷࠤ࡭ࡧࡶࡦࠢࡩࡥ࡮ࡲࡥࡥࠩ↴")
            }
        try:
            cls.bstack1llll1ll111l_opy_.shutdown()
            data = {
                bstack11ll1_opy_ (u"ࠬ࡬ࡩ࡯࡫ࡶ࡬ࡪࡪ࡟ࡢࡶࠪ↵"): bstack111lll1lll_opy_()
            }
            if not bstack1lll1ll11ll1_opy_ is None:
                data[bstack11ll1_opy_ (u"࠭ࡦࡪࡰ࡬ࡷ࡭࡫ࡤࡠ࡯ࡨࡸࡦࡪࡡࡵࡣࠪ↶")] = [{
                    bstack11ll1_opy_ (u"ࠧࡳࡧࡤࡷࡴࡴࠧ↷"): bstack11ll1_opy_ (u"ࠨࡷࡶࡩࡷࡥ࡫ࡪ࡮࡯ࡩࡩ࠭↸"),
                    bstack11ll1_opy_ (u"ࠩࡶ࡭࡬ࡴࡡ࡭ࠩ↹"): bstack1lll1ll11ll1_opy_
                }]
            config = {
                bstack11ll1_opy_ (u"ࠪ࡬ࡪࡧࡤࡦࡴࡶࠫ↺"): cls.default_headers()
            }
            bstack11l1ll1ll1l_opy_ = bstack11ll1_opy_ (u"ࠫࡦࡶࡩ࠰ࡸ࠴࠳ࡧࡻࡩ࡭ࡦࡶ࠳ࢀࢃ࠯ࡴࡶࡲࡴࠬ↻").format(os.environ[bstack11ll1_opy_ (u"ࠧࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡊࡘࡆࡤ࡛ࡕࡊࡆࠥ↼")])
            bstack1lll1ll111ll_opy_ = cls.request_url(bstack11l1ll1ll1l_opy_)
            response = bstack11l1l1l11l_opy_(bstack11ll1_opy_ (u"࠭ࡐࡖࡖࠪ↽"), bstack1lll1ll111ll_opy_, data, config)
            if not response.ok:
                raise Exception(bstack11ll1_opy_ (u"ࠢࡔࡶࡲࡴࠥࡸࡥࡲࡷࡨࡷࡹࠦ࡮ࡰࡶࠣࡳࡰࠨ↾"))
        except Exception as error:
            logger.error(bstack11ll1_opy_ (u"ࠣࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡴࡶࡲࡴࠥࡨࡵࡪ࡮ࡧࠤࡷ࡫ࡱࡶࡧࡶࡸࠥࡺ࡯ࠡࡖࡨࡷࡹࡎࡵࡣ࠼࠽ࠤࠧ↿") + str(error))
            return {
                bstack11ll1_opy_ (u"ࠩࡶࡸࡦࡺࡵࡴࠩ⇀"): bstack11ll1_opy_ (u"ࠪࡩࡷࡸ࡯ࡳࠩ⇁"),
                bstack11ll1_opy_ (u"ࠫࡲ࡫ࡳࡴࡣࡪࡩࠬ⇂"): str(error)
            }
    @classmethod
    @error_handler(class_method=True)
    def bstack1lll1llll111_opy_(cls, response):
        bstack1lllll1l1_opy_ = response.json() if not isinstance(response, dict) else response
        bstack1lll1lll111l_opy_ = {}
        if bstack1lllll1l1_opy_.get(bstack11ll1_opy_ (u"ࠬࡰࡷࡵࠩ⇃")) is None:
            os.environ[bstack11ll1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡊࡘࡖࠪ⇄")] = bstack11ll1_opy_ (u"ࠧ࡯ࡷ࡯ࡰࠬ⇅")
        else:
            os.environ[bstack11ll1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡍ࡛ࡂࡠࡌ࡚ࡘࠬ⇆")] = bstack1lllll1l1_opy_.get(bstack11ll1_opy_ (u"ࠩ࡭ࡻࡹ࠭⇇"), bstack11ll1_opy_ (u"ࠪࡲࡺࡲ࡬ࠨ⇈"))
        os.environ[bstack11ll1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡉࡗࡅࡣ࡚࡛ࡉࡅࠩ⇉")] = bstack1lllll1l1_opy_.get(bstack11ll1_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡣ࡭ࡧࡳࡩࡧࡧࡣ࡮ࡪࠧ⇊"), bstack11ll1_opy_ (u"࠭࡮ࡶ࡮࡯ࠫ⇋"))
        logger.info(bstack11ll1_opy_ (u"ࠧࡕࡧࡶࡸ࡭ࡻࡢࠡࡵࡷࡥࡷࡺࡥࡥࠢࡺ࡭ࡹ࡮ࠠࡪࡦ࠽ࠤࠬ⇌") + os.getenv(bstack11ll1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡍ࡛ࡂࡠࡗࡘࡍࡉ࠭⇍")));
        if bstack1l11llll1l_opy_.bstack1lll1ll111l1_opy_(cls.bs_config, cls.bstack11l111111_opy_.get(bstack11ll1_opy_ (u"ࠩࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࡤࡻࡳࡦࡦࠪ⇎"), bstack11ll1_opy_ (u"ࠪࠫ⇏"))) is True:
            bstack1llll1l1l1ll_opy_, build_hashed_id, bstack1lll1l1lllll_opy_ = cls.bstack1lll1ll11l11_opy_(bstack1lllll1l1_opy_)
            if bstack1llll1l1l1ll_opy_ != None and build_hashed_id != None:
                bstack1lll1lll111l_opy_[bstack11ll1_opy_ (u"ࠫࡴࡨࡳࡦࡴࡹࡥࡧ࡯࡬ࡪࡶࡼࠫ⇐")] = {
                    bstack11ll1_opy_ (u"ࠬࡰࡷࡵࡡࡷࡳࡰ࡫࡮ࠨ⇑"): bstack1llll1l1l1ll_opy_,
                    bstack11ll1_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡤ࡮ࡡࡴࡪࡨࡨࡤ࡯ࡤࠨ⇒"): build_hashed_id,
                    bstack11ll1_opy_ (u"ࠧࡢ࡮࡯ࡳࡼࡥࡳࡤࡴࡨࡩࡳࡹࡨࡰࡶࡶࠫ⇓"): bstack1lll1l1lllll_opy_
                }
            else:
                bstack1lll1lll111l_opy_[bstack11ll1_opy_ (u"ࠨࡱࡥࡷࡪࡸࡶࡢࡤ࡬ࡰ࡮ࡺࡹࠨ⇔")] = {}
        else:
            bstack1lll1lll111l_opy_[bstack11ll1_opy_ (u"ࠩࡲࡦࡸ࡫ࡲࡷࡣࡥ࡭ࡱ࡯ࡴࡺࠩ⇕")] = {}
        bstack1lll1ll1l1l1_opy_, build_hashed_id = cls.bstack1lll1ll1ll11_opy_(bstack1lllll1l1_opy_)
        if bstack1lll1ll1l1l1_opy_ != None and build_hashed_id != None:
            bstack1lll1lll111l_opy_[bstack11ll1_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠪ⇖")] = {
                bstack11ll1_opy_ (u"ࠫࡦࡻࡴࡩࡡࡷࡳࡰ࡫࡮ࠨ⇗"): bstack1lll1ll1l1l1_opy_,
                bstack11ll1_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡣ࡭ࡧࡳࡩࡧࡧࡣ࡮ࡪࠧ⇘"): build_hashed_id,
            }
        else:
            bstack1lll1lll111l_opy_[bstack11ll1_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾ࠭⇙")] = {}
        if bstack1lll1lll111l_opy_[bstack11ll1_opy_ (u"ࠧࡰࡤࡶࡩࡷࡼࡡࡣ࡫࡯࡭ࡹࡿࠧ⇚")].get(bstack11ll1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪ࡟ࡩࡣࡶ࡬ࡪࡪ࡟ࡪࡦࠪ⇛")) != None or bstack1lll1lll111l_opy_[bstack11ll1_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠩ⇜")].get(bstack11ll1_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡡ࡫ࡥࡸ࡮ࡥࡥࡡ࡬ࡨࠬ⇝")) != None:
            cls.bstack1lll1ll1l111_opy_(bstack1lllll1l1_opy_.get(bstack11ll1_opy_ (u"ࠫ࡯ࡽࡴࠨ⇞")), bstack1lllll1l1_opy_.get(bstack11ll1_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡣ࡭ࡧࡳࡩࡧࡧࡣ࡮ࡪࠧ⇟")))
        return bstack1lll1lll111l_opy_
    @classmethod
    def bstack1lll1ll11l11_opy_(cls, bstack1lllll1l1_opy_):
        if bstack1lllll1l1_opy_.get(bstack11ll1_opy_ (u"࠭࡯ࡣࡵࡨࡶࡻࡧࡢࡪ࡮࡬ࡸࡾ࠭⇠")) == None:
            cls.bstack1lll1ll11l1l_opy_()
            return [None, None, None]
        if bstack1lllll1l1_opy_[bstack11ll1_opy_ (u"ࠧࡰࡤࡶࡩࡷࡼࡡࡣ࡫࡯࡭ࡹࡿࠧ⇡")][bstack11ll1_opy_ (u"ࠨࡵࡸࡧࡨ࡫ࡳࡴࠩ⇢")] != True:
            cls.bstack1lll1ll11l1l_opy_(bstack1lllll1l1_opy_[bstack11ll1_opy_ (u"ࠩࡲࡦࡸ࡫ࡲࡷࡣࡥ࡭ࡱ࡯ࡴࡺࠩ⇣")])
            return [None, None, None]
        logger.debug(bstack11ll1_opy_ (u"ࠪࡿࢂࠦࡂࡶ࡫࡯ࡨࠥࡩࡲࡦࡣࡷ࡭ࡴࡴࠠࡔࡷࡦࡧࡪࡹࡳࡧࡷ࡯ࠥࠬ⇤").format(bstack111ll1ll1_opy_))
        os.environ[bstack11ll1_opy_ (u"ࠫࡇ࡙࡟ࡕࡇࡖࡘࡔࡖࡓࡠࡄࡘࡍࡑࡊ࡟ࡄࡑࡐࡔࡑࡋࡔࡆࡆࠪ⇥")] = bstack11ll1_opy_ (u"ࠬࡺࡲࡶࡧࠪ⇦")
        if bstack1lllll1l1_opy_.get(bstack11ll1_opy_ (u"࠭ࡪࡸࡶࠪ⇧")):
            os.environ[bstack11ll1_opy_ (u"ࠧࡄࡔࡈࡈࡊࡔࡔࡊࡃࡏࡗࡤࡌࡏࡓࡡࡆࡖࡆ࡙ࡈࡠࡔࡈࡔࡔࡘࡔࡊࡐࡊࠫ⇨")] = json.dumps({
                bstack11ll1_opy_ (u"ࠨࡷࡶࡩࡷࡴࡡ࡮ࡧࠪ⇩"): bstack11ll11l11l1_opy_(cls.bs_config),
                bstack11ll1_opy_ (u"ࠩࡳࡥࡸࡹࡷࡰࡴࡧࠫ⇪"): bstack11l1llll111_opy_(cls.bs_config)
            })
        if bstack1lllll1l1_opy_.get(bstack11ll1_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡡ࡫ࡥࡸ࡮ࡥࡥࡡ࡬ࡨࠬ⇫")):
            os.environ[bstack11ll1_opy_ (u"ࠫࡇ࡙࡟ࡕࡇࡖࡘࡔࡖࡓࡠࡄࡘࡍࡑࡊ࡟ࡉࡃࡖࡌࡊࡊ࡟ࡊࡆࠪ⇬")] = bstack1lllll1l1_opy_[bstack11ll1_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡣ࡭ࡧࡳࡩࡧࡧࡣ࡮ࡪࠧ⇭")]
        if bstack1lllll1l1_opy_[bstack11ll1_opy_ (u"࠭࡯ࡣࡵࡨࡶࡻࡧࡢࡪ࡮࡬ࡸࡾ࠭⇮")].get(bstack11ll1_opy_ (u"ࠧࡰࡲࡷ࡭ࡴࡴࡳࠨ⇯"), {}).get(bstack11ll1_opy_ (u"ࠨࡣ࡯ࡰࡴࡽ࡟ࡴࡥࡵࡩࡪࡴࡳࡩࡱࡷࡷࠬ⇰")):
            os.environ[bstack11ll1_opy_ (u"ࠩࡅࡗࡤ࡚ࡅࡔࡖࡒࡔࡘࡥࡁࡍࡎࡒ࡛ࡤ࡙ࡃࡓࡇࡈࡒࡘࡎࡏࡕࡕࠪ⇱")] = str(bstack1lllll1l1_opy_[bstack11ll1_opy_ (u"ࠪࡳࡧࡹࡥࡳࡸࡤࡦ࡮ࡲࡩࡵࡻࠪ⇲")][bstack11ll1_opy_ (u"ࠫࡴࡶࡴࡪࡱࡱࡷࠬ⇳")][bstack11ll1_opy_ (u"ࠬࡧ࡬࡭ࡱࡺࡣࡸࡩࡲࡦࡧࡱࡷ࡭ࡵࡴࡴࠩ⇴")])
        else:
            os.environ[bstack11ll1_opy_ (u"࠭ࡂࡔࡡࡗࡉࡘ࡚ࡏࡑࡕࡢࡅࡑࡒࡏࡘࡡࡖࡇࡗࡋࡅࡏࡕࡋࡓ࡙࡙ࠧ⇵")] = bstack11ll1_opy_ (u"ࠢ࡯ࡷ࡯ࡰࠧ⇶")
        return [bstack1lllll1l1_opy_[bstack11ll1_opy_ (u"ࠨ࡬ࡺࡸࠬ⇷")], bstack1lllll1l1_opy_[bstack11ll1_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡠࡪࡤࡷ࡭࡫ࡤࡠ࡫ࡧࠫ⇸")], os.environ[bstack11ll1_opy_ (u"ࠪࡆࡘࡥࡔࡆࡕࡗࡓࡕ࡙࡟ࡂࡎࡏࡓ࡜ࡥࡓࡄࡔࡈࡉࡓ࡙ࡈࡐࡖࡖࠫ⇹")]]
    @classmethod
    def bstack1lll1ll1ll11_opy_(cls, bstack1lllll1l1_opy_):
        if bstack1lllll1l1_opy_.get(bstack11ll1_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠫ⇺")) == None:
            cls.bstack1lll1ll1111l_opy_()
            return [None, None]
        if bstack1lllll1l1_opy_[bstack11ll1_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠬ⇻")][bstack11ll1_opy_ (u"࠭ࡳࡶࡥࡦࡩࡸࡹࠧ⇼")] != True:
            cls.bstack1lll1ll1111l_opy_(bstack1lllll1l1_opy_[bstack11ll1_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠧ⇽")])
            return [None, None]
        if bstack1lllll1l1_opy_[bstack11ll1_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠨ⇾")].get(bstack11ll1_opy_ (u"ࠩࡲࡴࡹ࡯࡯࡯ࡵࠪ⇿")):
            logger.debug(bstack11ll1_opy_ (u"ࠪࡘࡪࡹࡴࠡࡃࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠡࡄࡸ࡭ࡱࡪࠠࡤࡴࡨࡥࡹ࡯࡯࡯ࠢࡖࡹࡨࡩࡥࡴࡵࡩࡹࡱࠧࠧ∀"))
            parsed = json.loads(os.getenv(bstack11ll1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡠࡃࡆࡇࡊ࡙ࡓࡊࡄࡌࡐࡎ࡚࡙ࡠࡅࡒࡒࡋࡏࡇࡖࡔࡄࡘࡎࡕࡎࡠ࡛ࡐࡐࠬ∁"), bstack11ll1_opy_ (u"ࠬࢁࡽࠨ∂")))
            capabilities = bstack1l11111ll1_opy_.bstack1lll1ll1l11l_opy_(bstack1lllll1l1_opy_[bstack11ll1_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾ࠭∃")][bstack11ll1_opy_ (u"ࠧࡰࡲࡷ࡭ࡴࡴࡳࠨ∄")][bstack11ll1_opy_ (u"ࠨࡥࡤࡴࡦࡨࡩ࡭࡫ࡷ࡭ࡪࡹࠧ∅")], bstack11ll1_opy_ (u"ࠩࡱࡥࡲ࡫ࠧ∆"), bstack11ll1_opy_ (u"ࠪࡺࡦࡲࡵࡦࠩ∇"))
            bstack1lll1ll1l1l1_opy_ = capabilities[bstack11ll1_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࡘࡴࡱࡥ࡯ࠩ∈")]
            os.environ[bstack11ll1_opy_ (u"ࠬࡈࡓࡠࡃ࠴࠵࡞ࡥࡊࡘࡖࠪ∉")] = bstack1lll1ll1l1l1_opy_
            if bstack11ll1_opy_ (u"ࠨࡡࡶࡶࡲࡱࡦࡺࡥࠣ∊") in bstack1lllll1l1_opy_ and bstack1lllll1l1_opy_.get(bstack11ll1_opy_ (u"ࠢࡢࡲࡳࡣࡦࡻࡴࡰ࡯ࡤࡸࡪࠨ∋")) is None:
                parsed[bstack11ll1_opy_ (u"ࠨࡵࡦࡥࡳࡴࡥࡳࡘࡨࡶࡸ࡯࡯࡯ࠩ∌")] = capabilities[bstack11ll1_opy_ (u"ࠩࡶࡧࡦࡴ࡮ࡦࡴ࡙ࡩࡷࡹࡩࡰࡰࠪ∍")]
            os.environ[bstack11ll1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡉࡘ࡚࡟ࡂࡅࡆࡉࡘ࡙ࡉࡃࡋࡏࡍ࡙࡟࡟ࡄࡑࡑࡊࡎࡍࡕࡓࡃࡗࡍࡔࡔ࡟࡚ࡏࡏࠫ∎")] = json.dumps(parsed)
            scripts = bstack1l11111ll1_opy_.bstack1lll1ll1l11l_opy_(bstack1lllll1l1_opy_[bstack11ll1_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠫ∏")][bstack11ll1_opy_ (u"ࠬࡵࡰࡵ࡫ࡲࡲࡸ࠭∐")][bstack11ll1_opy_ (u"࠭ࡳࡤࡴ࡬ࡴࡹࡹࠧ∑")], bstack11ll1_opy_ (u"ࠧ࡯ࡣࡰࡩࠬ−"), bstack11ll1_opy_ (u"ࠨࡥࡲࡱࡲࡧ࡮ࡥࠩ∓"))
            bstack1l11l111l1_opy_.bstack111l1ll1l_opy_(scripts)
            commands = bstack1lllll1l1_opy_[bstack11ll1_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠩ∔")][bstack11ll1_opy_ (u"ࠪࡳࡵࡺࡩࡰࡰࡶࠫ∕")][bstack11ll1_opy_ (u"ࠫࡨࡵ࡭࡮ࡣࡱࡨࡸ࡚࡯ࡘࡴࡤࡴࠬ∖")].get(bstack11ll1_opy_ (u"ࠬࡩ࡯࡮࡯ࡤࡲࡩࡹࠧ∗"))
            bstack1l11l111l1_opy_.bstack11ll11l111l_opy_(commands)
            bstack11ll11111ll_opy_ = capabilities.get(bstack11ll1_opy_ (u"࠭ࡧࡰࡱࡪ࠾ࡨ࡮ࡲࡰ࡯ࡨࡓࡵࡺࡩࡰࡰࡶࠫ∘"))
            bstack1l11l111l1_opy_.bstack11l1lll11l1_opy_(bstack11ll11111ll_opy_)
            bstack1l11l111l1_opy_.store()
        return [bstack1lll1ll1l1l1_opy_, bstack1lllll1l1_opy_[bstack11ll1_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡥࡨࡢࡵ࡫ࡩࡩࡥࡩࡥࠩ∙")]]
    @classmethod
    def bstack1lll1ll11l1l_opy_(cls, response=None):
        os.environ[bstack11ll1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡍ࡛ࡂࡠࡗࡘࡍࡉ࠭√")] = bstack11ll1_opy_ (u"ࠩࡱࡹࡱࡲࠧ∛")
        os.environ[bstack11ll1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡉࡘ࡚ࡈࡖࡄࡢࡎ࡜࡚ࠧ∜")] = bstack11ll1_opy_ (u"ࠫࡳࡻ࡬࡭ࠩ∝")
        os.environ[bstack11ll1_opy_ (u"ࠬࡈࡓࡠࡖࡈࡗ࡙ࡕࡐࡔࡡࡅ࡙ࡎࡒࡄࡠࡅࡒࡑࡕࡒࡅࡕࡇࡇࠫ∞")] = bstack11ll1_opy_ (u"࠭ࡦࡢ࡮ࡶࡩࠬ∟")
        os.environ[bstack11ll1_opy_ (u"ࠧࡃࡕࡢࡘࡊ࡙ࡔࡐࡒࡖࡣࡇ࡛ࡉࡍࡆࡢࡌࡆ࡙ࡈࡆࡆࡢࡍࡉ࠭∠")] = bstack11ll1_opy_ (u"ࠣࡰࡸࡰࡱࠨ∡")
        os.environ[bstack11ll1_opy_ (u"ࠩࡅࡗࡤ࡚ࡅࡔࡖࡒࡔࡘࡥࡁࡍࡎࡒ࡛ࡤ࡙ࡃࡓࡇࡈࡒࡘࡎࡏࡕࡕࠪ∢")] = bstack11ll1_opy_ (u"ࠥࡲࡺࡲ࡬ࠣ∣")
        cls.bstack1lll1ll1ll1l_opy_(response, bstack11ll1_opy_ (u"ࠦࡴࡨࡳࡦࡴࡹࡥࡧ࡯࡬ࡪࡶࡼࠦ∤"))
        return [None, None, None]
    @classmethod
    def bstack1lll1ll1111l_opy_(cls, response=None):
        os.environ[bstack11ll1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡊࡘࡆࡤ࡛ࡕࡊࡆࠪ∥")] = bstack11ll1_opy_ (u"࠭࡮ࡶ࡮࡯ࠫ∦")
        os.environ[bstack11ll1_opy_ (u"ࠧࡃࡕࡢࡅ࠶࠷࡙ࡠࡌ࡚ࡘࠬ∧")] = bstack11ll1_opy_ (u"ࠨࡰࡸࡰࡱ࠭∨")
        os.environ[bstack11ll1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡍ࡛࡙࠭∩")] = bstack11ll1_opy_ (u"ࠪࡲࡺࡲ࡬ࠨ∪")
        cls.bstack1lll1ll1ll1l_opy_(response, bstack11ll1_opy_ (u"ࠦࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠦ∫"))
        return [None, None, None]
    @classmethod
    def bstack1lll1ll1l111_opy_(cls, jwt, build_hashed_id):
        os.environ[bstack11ll1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡊࡘࡆࡤࡐࡗࡕࠩ∬")] = jwt
        os.environ[bstack11ll1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡕࡖࡋࡇࠫ∭")] = build_hashed_id
    @classmethod
    def bstack1lll1ll1ll1l_opy_(cls, response=None, product=bstack11ll1_opy_ (u"ࠢࠣ∮")):
        if response == None or response.get(bstack11ll1_opy_ (u"ࠨࡧࡵࡶࡴࡸࡳࠨ∯")) == None:
            logger.error(product + bstack11ll1_opy_ (u"ࠤࠣࡆࡺ࡯࡬ࡥࠢࡦࡶࡪࡧࡴࡪࡱࡱࠤ࡫ࡧࡩ࡭ࡧࡧࠦ∰"))
            return
        for error in response[bstack11ll1_opy_ (u"ࠪࡩࡷࡸ࡯ࡳࡵࠪ∱")]:
            bstack111llll11l1_opy_ = error[bstack11ll1_opy_ (u"ࠫࡰ࡫ࡹࠨ∲")]
            error_message = error[bstack11ll1_opy_ (u"ࠬࡳࡥࡴࡵࡤ࡫ࡪ࠭∳")]
            if error_message:
                if bstack111llll11l1_opy_ == bstack11ll1_opy_ (u"ࠨࡅࡓࡔࡒࡖࡤࡇࡃࡄࡇࡖࡗࡤࡊࡅࡏࡋࡈࡈࠧ∴"):
                    logger.info(error_message)
                else:
                    logger.error(error_message)
            else:
                logger.error(bstack11ll1_opy_ (u"ࠢࡅࡣࡷࡥࠥࡻࡰ࡭ࡱࡤࡨࠥࡺ࡯ࠡࡄࡵࡳࡼࡹࡥࡳࡕࡷࡥࡨࡱࠠࠣ∵") + product + bstack11ll1_opy_ (u"ࠣࠢࡩࡥ࡮ࡲࡥࡥࠢࡧࡹࡪࠦࡴࡰࠢࡶࡳࡲ࡫ࠠࡦࡴࡵࡳࡷࠨ∶"))
    @classmethod
    def bstack1lll1ll1lll1_opy_(cls):
        if cls.bstack1llll1ll111l_opy_ is not None:
            return
        cls.bstack1llll1ll111l_opy_ = bstack1llll1ll1l11_opy_(cls.bstack1lll1ll1l1ll_opy_)
        cls.bstack1llll1ll111l_opy_.start()
    @classmethod
    def bstack1111l1l1l1_opy_(cls):
        if cls.bstack1llll1ll111l_opy_ is None:
            return
        cls.bstack1llll1ll111l_opy_.shutdown()
    @classmethod
    @error_handler(class_method=True)
    def bstack1lll1ll1l1ll_opy_(cls, bstack1111l1l11l_opy_, event_url=bstack11ll1_opy_ (u"ࠩࡤࡴ࡮࠵ࡶ࠲࠱ࡥࡥࡹࡩࡨࠨ∷")):
        config = {
            bstack11ll1_opy_ (u"ࠪ࡬ࡪࡧࡤࡦࡴࡶࠫ∸"): cls.default_headers()
        }
        logger.debug(bstack11ll1_opy_ (u"ࠦࡵࡵࡳࡵࡡࡧࡥࡹࡧ࠺ࠡࡕࡨࡲࡩ࡯࡮ࡨࠢࡧࡥࡹࡧࠠࡵࡱࠣࡸࡪࡹࡴࡩࡷࡥࠤ࡫ࡵࡲࠡࡧࡹࡩࡳࡺࡳࠡࡽࢀࠦ∹").format(bstack11ll1_opy_ (u"ࠬ࠲ࠠࠨ∺").join([event[bstack11ll1_opy_ (u"࠭ࡥࡷࡧࡱࡸࡤࡺࡹࡱࡧࠪ∻")] for event in bstack1111l1l11l_opy_])))
        response = bstack11l1l1l11l_opy_(bstack11ll1_opy_ (u"ࠧࡑࡑࡖࡘࠬ∼"), cls.request_url(event_url), bstack1111l1l11l_opy_, config)
        bstack11l1llll1ll_opy_ = response.json()
    @classmethod
    def bstack1lll1llll_opy_(cls, bstack1111l1l11l_opy_, event_url=bstack11ll1_opy_ (u"ࠨࡣࡳ࡭࠴ࡼ࠱࠰ࡤࡤࡸࡨ࡮ࠧ∽")):
        logger.debug(bstack11ll1_opy_ (u"ࠤࡶࡩࡳࡪ࡟ࡥࡣࡷࡥ࠿ࠦࡁࡵࡶࡨࡱࡵࡺࡩ࡯ࡩࠣࡸࡴࠦࡡࡥࡦࠣࡨࡦࡺࡡࠡࡶࡲࠤࡧࡧࡴࡤࡪࠣࡻ࡮ࡺࡨࠡࡧࡹࡩࡳࡺ࡟ࡵࡻࡳࡩ࠿ࠦࡻࡾࠤ∾").format(bstack1111l1l11l_opy_[bstack11ll1_opy_ (u"ࠪࡩࡻ࡫࡮ࡵࡡࡷࡽࡵ࡫ࠧ∿")]))
        if not bstack1l11111ll1_opy_.bstack1lll1lll1l11_opy_(bstack1111l1l11l_opy_[bstack11ll1_opy_ (u"ࠫࡪࡼࡥ࡯ࡶࡢࡸࡾࡶࡥࠨ≀")]):
            logger.debug(bstack11ll1_opy_ (u"ࠧࡹࡥ࡯ࡦࡢࡨࡦࡺࡡ࠻ࠢࡑࡳࡹࠦࡡࡥࡦ࡬ࡲ࡬ࠦࡤࡢࡶࡤࠤࡼ࡯ࡴࡩࠢࡨࡺࡪࡴࡴࡠࡶࡼࡴࡪࡀࠠࡼࡿࠥ≁").format(bstack1111l1l11l_opy_[bstack11ll1_opy_ (u"࠭ࡥࡷࡧࡱࡸࡤࡺࡹࡱࡧࠪ≂")]))
            return
        bstack11l1111l11_opy_ = bstack1l11111ll1_opy_.bstack1lll1ll11111_opy_(bstack1111l1l11l_opy_[bstack11ll1_opy_ (u"ࠧࡦࡸࡨࡲࡹࡥࡴࡺࡲࡨࠫ≃")], bstack1111l1l11l_opy_.get(bstack11ll1_opy_ (u"ࠨࡶࡨࡷࡹࡥࡲࡶࡰࠪ≄")))
        if bstack11l1111l11_opy_ != None:
            if bstack1111l1l11l_opy_.get(bstack11ll1_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡳࡷࡱࠫ≅")) != None:
                bstack1111l1l11l_opy_[bstack11ll1_opy_ (u"ࠪࡸࡪࡹࡴࡠࡴࡸࡲࠬ≆")][bstack11ll1_opy_ (u"ࠫࡵࡸ࡯ࡥࡷࡦࡸࡤࡳࡡࡱࠩ≇")] = bstack11l1111l11_opy_
            else:
                bstack1111l1l11l_opy_[bstack11ll1_opy_ (u"ࠬࡶࡲࡰࡦࡸࡧࡹࡥ࡭ࡢࡲࠪ≈")] = bstack11l1111l11_opy_
        if event_url == bstack11ll1_opy_ (u"࠭ࡡࡱ࡫࠲ࡺ࠶࠵ࡢࡢࡶࡦ࡬ࠬ≉"):
            cls.bstack1lll1ll1lll1_opy_()
            logger.debug(bstack11ll1_opy_ (u"ࠢࡴࡧࡱࡨࡤࡪࡡࡵࡣ࠽ࠤࡆࡪࡤࡪࡰࡪࠤࡩࡧࡴࡢࠢࡷࡳࠥࡨࡡࡵࡥ࡫ࠤࡼ࡯ࡴࡩࠢࡨࡺࡪࡴࡴࡠࡶࡼࡴࡪࡀࠠࡼࡿࠥ≊").format(bstack1111l1l11l_opy_[bstack11ll1_opy_ (u"ࠨࡧࡹࡩࡳࡺ࡟ࡵࡻࡳࡩࠬ≋")]))
            cls.bstack1llll1ll111l_opy_.add(bstack1111l1l11l_opy_)
        elif event_url == bstack11ll1_opy_ (u"ࠩࡤࡴ࡮࠵ࡶ࠲࠱ࡶࡧࡷ࡫ࡥ࡯ࡵ࡫ࡳࡹࡹࠧ≌"):
            cls.bstack1lll1ll1l1ll_opy_([bstack1111l1l11l_opy_], event_url)
    @classmethod
    @error_handler(class_method=True)
    def bstack1l1l11l11l_opy_(cls, logs):
        for log in logs:
            bstack1lll1lll1111_opy_ = {
                bstack11ll1_opy_ (u"ࠪ࡯࡮ࡴࡤࠨ≍"): bstack11ll1_opy_ (u"࡙ࠫࡋࡓࡕࡡࡏࡓࡌ࠭≎"),
                bstack11ll1_opy_ (u"ࠬࡲࡥࡷࡧ࡯ࠫ≏"): log[bstack11ll1_opy_ (u"࠭࡬ࡦࡸࡨࡰࠬ≐")],
                bstack11ll1_opy_ (u"ࠧࡵ࡫ࡰࡩࡸࡺࡡ࡮ࡲࠪ≑"): log[bstack11ll1_opy_ (u"ࠨࡶ࡬ࡱࡪࡹࡴࡢ࡯ࡳࠫ≒")],
                bstack11ll1_opy_ (u"ࠩ࡫ࡸࡹࡶ࡟ࡳࡧࡶࡴࡴࡴࡳࡦࠩ≓"): {},
                bstack11ll1_opy_ (u"ࠪࡱࡪࡹࡳࡢࡩࡨࠫ≔"): log[bstack11ll1_opy_ (u"ࠫࡲ࡫ࡳࡴࡣࡪࡩࠬ≕")],
            }
            if bstack11ll1_opy_ (u"ࠬࡺࡥࡴࡶࡢࡶࡺࡴ࡟ࡶࡷ࡬ࡨࠬ≖") in log:
                bstack1lll1lll1111_opy_[bstack11ll1_opy_ (u"࠭ࡴࡦࡵࡷࡣࡷࡻ࡮ࡠࡷࡸ࡭ࡩ࠭≗")] = log[bstack11ll1_opy_ (u"ࠧࡵࡧࡶࡸࡤࡸࡵ࡯ࡡࡸࡹ࡮ࡪࠧ≘")]
            elif bstack11ll1_opy_ (u"ࠨࡪࡲࡳࡰࡥࡲࡶࡰࡢࡹࡺ࡯ࡤࠨ≙") in log:
                bstack1lll1lll1111_opy_[bstack11ll1_opy_ (u"ࠩ࡫ࡳࡴࡱ࡟ࡳࡷࡱࡣࡺࡻࡩࡥࠩ≚")] = log[bstack11ll1_opy_ (u"ࠪ࡬ࡴࡵ࡫ࡠࡴࡸࡲࡤࡻࡵࡪࡦࠪ≛")]
            cls.bstack1lll1llll_opy_({
                bstack11ll1_opy_ (u"ࠫࡪࡼࡥ࡯ࡶࡢࡸࡾࡶࡥࠨ≜"): bstack11ll1_opy_ (u"ࠬࡒ࡯ࡨࡅࡵࡩࡦࡺࡥࡥࠩ≝"),
                bstack11ll1_opy_ (u"࠭࡬ࡰࡩࡶࠫ≞"): [bstack1lll1lll1111_opy_]
            })
    @classmethod
    @error_handler(class_method=True)
    def bstack1lll1lll1lll_opy_(cls, steps):
        bstack1lll1ll1llll_opy_ = []
        for step in steps:
            bstack1lll1ll11lll_opy_ = {
                bstack11ll1_opy_ (u"ࠧ࡬࡫ࡱࡨࠬ≟"): bstack11ll1_opy_ (u"ࠨࡖࡈࡗ࡙ࡥࡓࡕࡇࡓࠫ≠"),
                bstack11ll1_opy_ (u"ࠩ࡯ࡩࡻ࡫࡬ࠨ≡"): step[bstack11ll1_opy_ (u"ࠪࡰࡪࡼࡥ࡭ࠩ≢")],
                bstack11ll1_opy_ (u"ࠫࡹ࡯࡭ࡦࡵࡷࡥࡲࡶࠧ≣"): step[bstack11ll1_opy_ (u"ࠬࡺࡩ࡮ࡧࡶࡸࡦࡳࡰࠨ≤")],
                bstack11ll1_opy_ (u"࠭࡭ࡦࡵࡶࡥ࡬࡫ࠧ≥"): step[bstack11ll1_opy_ (u"ࠧ࡮ࡧࡶࡷࡦ࡭ࡥࠨ≦")],
                bstack11ll1_opy_ (u"ࠨࡦࡸࡶࡦࡺࡩࡰࡰࠪ≧"): step[bstack11ll1_opy_ (u"ࠩࡧࡹࡷࡧࡴࡪࡱࡱࠫ≨")]
            }
            if bstack11ll1_opy_ (u"ࠪࡸࡪࡹࡴࡠࡴࡸࡲࡤࡻࡵࡪࡦࠪ≩") in step:
                bstack1lll1ll11lll_opy_[bstack11ll1_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡵࡹࡳࡥࡵࡶ࡫ࡧࠫ≪")] = step[bstack11ll1_opy_ (u"ࠬࡺࡥࡴࡶࡢࡶࡺࡴ࡟ࡶࡷ࡬ࡨࠬ≫")]
            elif bstack11ll1_opy_ (u"࠭ࡨࡰࡱ࡮ࡣࡷࡻ࡮ࡠࡷࡸ࡭ࡩ࠭≬") in step:
                bstack1lll1ll11lll_opy_[bstack11ll1_opy_ (u"ࠧࡩࡱࡲ࡯ࡤࡸࡵ࡯ࡡࡸࡹ࡮ࡪࠧ≭")] = step[bstack11ll1_opy_ (u"ࠨࡪࡲࡳࡰࡥࡲࡶࡰࡢࡹࡺ࡯ࡤࠨ≮")]
            bstack1lll1ll1llll_opy_.append(bstack1lll1ll11lll_opy_)
        cls.bstack1lll1llll_opy_({
            bstack11ll1_opy_ (u"ࠩࡨࡺࡪࡴࡴࡠࡶࡼࡴࡪ࠭≯"): bstack11ll1_opy_ (u"ࠪࡐࡴ࡭ࡃࡳࡧࡤࡸࡪࡪࠧ≰"),
            bstack11ll1_opy_ (u"ࠫࡱࡵࡧࡴࠩ≱"): bstack1lll1ll1llll_opy_
        })
    @classmethod
    @error_handler(class_method=True)
    @measure(event_name=EVENTS.bstack1111l11l1_opy_, stage=STAGE.bstack11l1llll1_opy_)
    def bstack1l1lll1ll_opy_(cls, screenshot):
        cls.bstack1lll1llll_opy_({
            bstack11ll1_opy_ (u"ࠬ࡫ࡶࡦࡰࡷࡣࡹࡿࡰࡦࠩ≲"): bstack11ll1_opy_ (u"࠭ࡌࡰࡩࡆࡶࡪࡧࡴࡦࡦࠪ≳"),
            bstack11ll1_opy_ (u"ࠧ࡭ࡱࡪࡷࠬ≴"): [{
                bstack11ll1_opy_ (u"ࠨ࡭࡬ࡲࡩ࠭≵"): bstack11ll1_opy_ (u"ࠩࡗࡉࡘ࡚࡟ࡔࡅࡕࡉࡊࡔࡓࡉࡑࡗࠫ≶"),
                bstack11ll1_opy_ (u"ࠪࡸ࡮ࡳࡥࡴࡶࡤࡱࡵ࠭≷"): datetime.datetime.utcnow().isoformat() + bstack11ll1_opy_ (u"ࠫ࡟࠭≸"),
                bstack11ll1_opy_ (u"ࠬࡳࡥࡴࡵࡤ࡫ࡪ࠭≹"): screenshot[bstack11ll1_opy_ (u"࠭ࡩ࡮ࡣࡪࡩࠬ≺")],
                bstack11ll1_opy_ (u"ࠧࡵࡧࡶࡸࡤࡸࡵ࡯ࡡࡸࡹ࡮ࡪࠧ≻"): screenshot[bstack11ll1_opy_ (u"ࠨࡶࡨࡷࡹࡥࡲࡶࡰࡢࡹࡺ࡯ࡤࠨ≼")]
            }]
        }, event_url=bstack11ll1_opy_ (u"ࠩࡤࡴ࡮࠵ࡶ࠲࠱ࡶࡧࡷ࡫ࡥ࡯ࡵ࡫ࡳࡹࡹࠧ≽"))
    @classmethod
    @error_handler(class_method=True)
    def bstack1ll1lll111_opy_(cls, driver):
        current_test_uuid = cls.current_test_uuid()
        if not current_test_uuid:
            return
        cls.bstack1lll1llll_opy_({
            bstack11ll1_opy_ (u"ࠪࡩࡻ࡫࡮ࡵࡡࡷࡽࡵ࡫ࠧ≾"): bstack11ll1_opy_ (u"ࠫࡈࡈࡔࡔࡧࡶࡷ࡮ࡵ࡮ࡄࡴࡨࡥࡹ࡫ࡤࠨ≿"),
            bstack11ll1_opy_ (u"ࠬࡺࡥࡴࡶࡢࡶࡺࡴࠧ⊀"): {
                bstack11ll1_opy_ (u"ࠨࡵࡶ࡫ࡧࠦ⊁"): cls.current_test_uuid(),
                bstack11ll1_opy_ (u"ࠢࡪࡰࡷࡩ࡬ࡸࡡࡵ࡫ࡲࡲࡸࠨ⊂"): cls.bstack111l1ll111_opy_(driver)
            }
        })
    @classmethod
    def bstack111ll11l11_opy_(cls, event: str, bstack1111l1l11l_opy_: bstack111l111lll_opy_):
        bstack1111l1llll_opy_ = {
            bstack11ll1_opy_ (u"ࠨࡧࡹࡩࡳࡺ࡟ࡵࡻࡳࡩࠬ⊃"): event,
            bstack1111l1l11l_opy_.bstack1111ll1111_opy_(): bstack1111l1l11l_opy_.bstack111l111ll1_opy_(event)
        }
        cls.bstack1lll1llll_opy_(bstack1111l1llll_opy_)
        result = getattr(bstack1111l1l11l_opy_, bstack11ll1_opy_ (u"ࠩࡵࡩࡸࡻ࡬ࡵࠩ⊄"), None)
        if event == bstack11ll1_opy_ (u"ࠪࡘࡪࡹࡴࡓࡷࡱࡗࡹࡧࡲࡵࡧࡧࠫ⊅"):
            threading.current_thread().bstackTestMeta = {bstack11ll1_opy_ (u"ࠫࡸࡺࡡࡵࡷࡶࠫ⊆"): bstack11ll1_opy_ (u"ࠬࡶࡥ࡯ࡦ࡬ࡲ࡬࠭⊇")}
        elif event == bstack11ll1_opy_ (u"࠭ࡔࡦࡵࡷࡖࡺࡴࡆࡪࡰ࡬ࡷ࡭࡫ࡤࠨ⊈"):
            threading.current_thread().bstackTestMeta = {bstack11ll1_opy_ (u"ࠧࡴࡶࡤࡸࡺࡹࠧ⊉"): getattr(result, bstack11ll1_opy_ (u"ࠨࡴࡨࡷࡺࡲࡴࠨ⊊"), bstack11ll1_opy_ (u"ࠩࠪ⊋"))}
    @classmethod
    def on(cls):
        if (os.environ.get(bstack11ll1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡉࡘ࡚ࡈࡖࡄࡢࡎ࡜࡚ࠧ⊌"), None) is None or os.environ[bstack11ll1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡉࡗࡅࡣࡏ࡝ࡔࠨ⊍")] == bstack11ll1_opy_ (u"ࠧࡴࡵ࡭࡮ࠥ⊎")) and (os.environ.get(bstack11ll1_opy_ (u"࠭ࡂࡔࡡࡄ࠵࠶࡟࡟ࡋ࡙ࡗࠫ⊏"), None) is None or os.environ[bstack11ll1_opy_ (u"ࠧࡃࡕࡢࡅ࠶࠷࡙ࡠࡌ࡚ࡘࠬ⊐")] == bstack11ll1_opy_ (u"ࠣࡰࡸࡰࡱࠨ⊑")):
            return False
        return True
    @staticmethod
    def bstack1lll1lll11ll_opy_(func):
        def wrap(*args, **kwargs):
            if bstack11lll11l11_opy_.on():
                return func(*args, **kwargs)
            return
        return wrap
    @staticmethod
    def default_headers():
        headers = {
            bstack11ll1_opy_ (u"ࠩࡆࡳࡳࡺࡥ࡯ࡶ࠰ࡘࡾࡶࡥࠨ⊒"): bstack11ll1_opy_ (u"ࠪࡥࡵࡶ࡬ࡪࡥࡤࡸ࡮ࡵ࡮࠰࡬ࡶࡳࡳ࠭⊓"),
            bstack11ll1_opy_ (u"ࠫ࡝࠳ࡂࡔࡖࡄࡇࡐ࠳ࡔࡆࡕࡗࡓࡕ࡙ࠧ⊔"): bstack11ll1_opy_ (u"ࠬࡺࡲࡶࡧࠪ⊕")
        }
        if os.environ.get(bstack11ll1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡊࡘࡖࠪ⊖"), None):
            headers[bstack11ll1_opy_ (u"ࠧࡂࡷࡷ࡬ࡴࡸࡩࡻࡣࡷ࡭ࡴࡴࠧ⊗")] = bstack11ll1_opy_ (u"ࠨࡄࡨࡥࡷ࡫ࡲࠡࡽࢀࠫ⊘").format(os.environ[bstack11ll1_opy_ (u"ࠤࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡍ࡛࡙ࠨ⊙")])
        return headers
    @staticmethod
    def request_url(url):
        return bstack11ll1_opy_ (u"ࠪࡿࢂ࠵ࡻࡾࠩ⊚").format(bstack1lll1lll11l1_opy_, url)
    @staticmethod
    def current_test_uuid():
        return getattr(threading.current_thread(), bstack11ll1_opy_ (u"ࠫࡨࡻࡲࡳࡧࡱࡸࡤࡺࡥࡴࡶࡢࡹࡺ࡯ࡤࠨ⊛"), None)
    @staticmethod
    def bstack111l1ll111_opy_(driver):
        return {
            bstack11l111111l1_opy_(): bstack111lll111ll_opy_(driver)
        }
    @staticmethod
    def bstack1lll1lll1ll1_opy_(exception_info, report):
        return [{bstack11ll1_opy_ (u"ࠬࡨࡡࡤ࡭ࡷࡶࡦࡩࡥࠨ⊜"): [exception_info.exconly(), report.longreprtext]}]
    @staticmethod
    def bstack1lllll1ll11_opy_(typename):
        if bstack11ll1_opy_ (u"ࠨࡁࡴࡵࡨࡶࡹ࡯࡯࡯ࠤ⊝") in typename:
            return bstack11ll1_opy_ (u"ࠢࡂࡵࡶࡩࡷࡺࡩࡰࡰࡈࡶࡷࡵࡲࠣ⊞")
        return bstack11ll1_opy_ (u"ࠣࡗࡱ࡬ࡦࡴࡤ࡭ࡧࡧࡉࡷࡸ࡯ࡳࠤ⊟")