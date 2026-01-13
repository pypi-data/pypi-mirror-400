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
import requests
from urllib.parse import urljoin, urlencode
from datetime import datetime
import os
import logging
import json
from bstack_utils.constants import bstack11l11lll1l1_opy_
logger = logging.getLogger(__name__)
class bstack11l1ll1l11l_opy_:
    @staticmethod
    def results(builder,params=None):
        bstack1llll1l1l11l_opy_ = urljoin(builder, bstack11ll1_opy_ (u"ࠫ࡮ࡹࡳࡶࡧࡶࠫₜ"))
        if params:
            bstack1llll1l1l11l_opy_ += bstack11ll1_opy_ (u"ࠧࡅࡻࡾࠤ₝").format(urlencode({bstack11ll1_opy_ (u"࠭ࡴࡦࡵࡷࡣࡷࡻ࡮ࡠࡷࡸ࡭ࡩ࠭₞"): params.get(bstack11ll1_opy_ (u"ࠧࡵࡧࡶࡸࡤࡸࡵ࡯ࡡࡸࡹ࡮ࡪࠧ₟"))}))
        return bstack11l1ll1l11l_opy_.bstack1llll1l1l111_opy_(bstack1llll1l1l11l_opy_)
    @staticmethod
    def bstack11l1ll11lll_opy_(builder,params=None):
        bstack1llll1l1l11l_opy_ = urljoin(builder, bstack11ll1_opy_ (u"ࠨ࡫ࡶࡷࡺ࡫ࡳ࠮ࡵࡸࡱࡲࡧࡲࡺࠩ₠"))
        if params:
            bstack1llll1l1l11l_opy_ += bstack11ll1_opy_ (u"ࠤࡂࡿࢂࠨ₡").format(urlencode({bstack11ll1_opy_ (u"ࠪࡸࡪࡹࡴࡠࡴࡸࡲࡤࡻࡵࡪࡦࠪ₢"): params.get(bstack11ll1_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡵࡹࡳࡥࡵࡶ࡫ࡧࠫ₣"))}))
        return bstack11l1ll1l11l_opy_.bstack1llll1l1l111_opy_(bstack1llll1l1l11l_opy_)
    @staticmethod
    def bstack1llll1l1l111_opy_(bstack1llll1l1l1l1_opy_):
        bstack1llll1l1l1ll_opy_ = os.environ.get(bstack11ll1_opy_ (u"ࠬࡈࡓࡠࡃ࠴࠵࡞ࡥࡊࡘࡖࠪ₤"), os.environ.get(bstack11ll1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡊࡘࡖࠪ₥"), bstack11ll1_opy_ (u"ࠧࠨ₦")))
        headers = {bstack11ll1_opy_ (u"ࠨࡃࡸࡸ࡭ࡵࡲࡪࡼࡤࡸ࡮ࡵ࡮ࠨ₧"): bstack11ll1_opy_ (u"ࠩࡅࡩࡦࡸࡥࡳࠢࡾࢁࠬ₨").format(bstack1llll1l1l1ll_opy_)}
        response = requests.get(bstack1llll1l1l1l1_opy_, headers=headers)
        bstack1llll1l11lll_opy_ = {}
        try:
            bstack1llll1l11lll_opy_ = response.json()
        except Exception as e:
            logger.debug(bstack11ll1_opy_ (u"ࠥࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦࡰࡢࡴࡶࡩࠥࡐࡓࡐࡐࠣࡶࡪࡹࡰࡰࡰࡶࡩ࠿ࠦࡻࡾࠤ₩").format(e))
            pass
        if bstack1llll1l11lll_opy_ is not None:
            bstack1llll1l11lll_opy_[bstack11ll1_opy_ (u"ࠫࡳ࡫ࡸࡵࡡࡳࡳࡱࡲ࡟ࡵ࡫ࡰࡩࠬ₪")] = response.headers.get(bstack11ll1_opy_ (u"ࠬࡴࡥࡹࡶࡢࡴࡴࡲ࡬ࡠࡶ࡬ࡱࡪ࠭₫"), str(int(datetime.now().timestamp() * 1000)))
            bstack1llll1l11lll_opy_[bstack11ll1_opy_ (u"࠭ࡳࡵࡣࡷࡹࡸ࠭€")] = response.status_code
        return bstack1llll1l11lll_opy_
    @staticmethod
    def bstack1llll1l1ll11_opy_(bstack1llll1l11l11_opy_, data):
        logger.debug(bstack11ll1_opy_ (u"ࠢࡑࡴࡲࡧࡪࡹࡳࡪࡰࡪࠤࡗ࡫ࡱࡶࡧࡶࡸࠥ࡬࡯ࡳࠢࡷࡩࡸࡺࡏࡳࡥ࡫ࡩࡸࡺࡲࡢࡶ࡬ࡳࡳ࡙ࡰ࡭࡫ࡷࡘࡪࡹࡴࡴࠤ₭"))
        return bstack11l1ll1l11l_opy_.bstack1llll1l11ll1_opy_(bstack11ll1_opy_ (u"ࠨࡒࡒࡗ࡙࠭₮"), bstack1llll1l11l11_opy_, data=data)
    @staticmethod
    def bstack1llll1l11l1l_opy_(bstack1llll1l11l11_opy_, data):
        logger.debug(bstack11ll1_opy_ (u"ࠤࡓࡶࡴࡩࡥࡴࡵ࡬ࡲ࡬ࠦࡒࡦࡳࡸࡩࡸࡺࠠࡧࡱࡵࠤ࡬࡫ࡴࡕࡧࡶࡸࡔࡸࡣࡩࡧࡶࡸࡷࡧࡴࡪࡱࡱࡓࡷࡪࡥࡳࡧࡧࡘࡪࡹࡴࡴࠤ₯"))
        res = bstack11l1ll1l11l_opy_.bstack1llll1l11ll1_opy_(bstack11ll1_opy_ (u"ࠪࡋࡊ࡚ࠧ₰"), bstack1llll1l11l11_opy_, data=data)
        return res
    @staticmethod
    def bstack1llll1l11ll1_opy_(method, bstack1llll1l11l11_opy_, data=None, params=None, extra_headers=None):
        bstack1llll1l1l1ll_opy_ = os.environ.get(bstack11ll1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡉࡗࡅࡣࡏ࡝ࡔࠨ₱"), bstack11ll1_opy_ (u"ࠬ࠭₲"))
        headers = {
            bstack11ll1_opy_ (u"࠭ࡡࡶࡶ࡫ࡳࡷ࡯ࡺࡢࡶ࡬ࡳࡳ࠭₳"): bstack11ll1_opy_ (u"ࠧࡃࡧࡤࡶࡪࡸࠠࡼࡿࠪ₴").format(bstack1llll1l1l1ll_opy_),
            bstack11ll1_opy_ (u"ࠨࡅࡲࡲࡹ࡫࡮ࡵ࠯ࡗࡽࡵ࡫ࠧ₵"): bstack11ll1_opy_ (u"ࠩࡤࡴࡵࡲࡩࡤࡣࡷ࡭ࡴࡴ࠯࡫ࡵࡲࡲࠬ₶"),
            bstack11ll1_opy_ (u"ࠪࡅࡨࡩࡥࡱࡶࠪ₷"): bstack11ll1_opy_ (u"ࠫࡦࡶࡰ࡭࡫ࡦࡥࡹ࡯࡯࡯࠱࡭ࡷࡴࡴࠧ₸")
        }
        if extra_headers:
            headers.update(extra_headers)
        url = bstack11l11lll1l1_opy_ + bstack11ll1_opy_ (u"ࠧ࠵ࠢ₹") + bstack1llll1l11l11_opy_.lstrip(bstack11ll1_opy_ (u"࠭࠯ࠨ₺"))
        try:
            if method == bstack11ll1_opy_ (u"ࠧࡈࡇࡗࠫ₻"):
                response = requests.get(url, headers=headers, params=params, json=data)
            elif method == bstack11ll1_opy_ (u"ࠨࡒࡒࡗ࡙࠭₼"):
                response = requests.post(url, headers=headers, json=data)
            elif method == bstack11ll1_opy_ (u"ࠩࡓ࡙࡙࠭₽"):
                response = requests.put(url, headers=headers, json=data)
            else:
                raise ValueError(bstack11ll1_opy_ (u"࡙ࠥࡳࡹࡵࡱࡲࡲࡶࡹ࡫ࡤࠡࡊࡗࡘࡕࠦ࡭ࡦࡶ࡫ࡳࡩࡀࠠࡼࡿࠥ₾").format(method))
            logger.debug(bstack11ll1_opy_ (u"ࠦࡔࡸࡣࡩࡧࡶࡸࡷࡧࡴࡪࡱࡱࠤࡷ࡫ࡱࡶࡧࡶࡸࠥࡳࡡࡥࡧࠣࡸࡴࠦࡕࡓࡎ࠽ࠤࢀࢃࠠࡸ࡫ࡷ࡬ࠥࡳࡥࡵࡪࡲࡨ࠿ࠦࡻࡾࠤ₿").format(url, method))
            bstack1llll1l11lll_opy_ = {}
            try:
                bstack1llll1l11lll_opy_ = response.json()
            except Exception as e:
                logger.debug(bstack11ll1_opy_ (u"ࠧࡌࡡࡪ࡮ࡨࡨࠥࡺ࡯ࠡࡲࡤࡶࡸ࡫ࠠࡋࡕࡒࡒࠥࡸࡥࡴࡲࡲࡲࡸ࡫࠺ࠡࡽࢀࠤ࠲ࠦࡻࡾࠤ⃀").format(e, response.text))
            if bstack1llll1l11lll_opy_ is not None:
                bstack1llll1l11lll_opy_[bstack11ll1_opy_ (u"࠭࡮ࡦࡺࡷࡣࡵࡵ࡬࡭ࡡࡷ࡭ࡲ࡫ࠧ⃁")] = response.headers.get(
                    bstack11ll1_opy_ (u"ࠧ࡯ࡧࡻࡸࡤࡶ࡯࡭࡮ࡢࡸ࡮ࡳࡥࠨ⃂"), str(int(datetime.now().timestamp() * 1000))
                )
                bstack1llll1l11lll_opy_[bstack11ll1_opy_ (u"ࠨࡵࡷࡥࡹࡻࡳࠨ⃃")] = response.status_code
            return bstack1llll1l11lll_opy_
        except Exception as e:
            logger.error(bstack11ll1_opy_ (u"ࠤࡒࡶࡨ࡮ࡥࡴࡶࡵࡥࡹ࡯࡯࡯ࠢࡵࡩࡶࡻࡥࡴࡶࠣࡪࡦ࡯࡬ࡦࡦ࠽ࠤࢀࢃࠠ࠮ࠢࡾࢁࠧ⃄").format(e, url))
            return None
    @staticmethod
    def bstack11l11l11lll_opy_(bstack1llll1l1l1l1_opy_, data):
        bstack11ll1_opy_ (u"ࠥࠦࠧࠐࠠࠡࠢࠣࠤࠥࠦࠠࡔࡧࡱࡨࡸࠦࡡࠡࡒࡘࡘࠥࡸࡥࡲࡷࡨࡷࡹࠦࡴࡰࠢࡶࡸࡴࡸࡥࠡࡶ࡫ࡩࠥ࡬ࡡࡪ࡮ࡨࡨࠥࡺࡥࡴࡶࡶࠎࠥࠦࠠࠡࠢࠣࠤࠥࠨࠢࠣ⃅")
        bstack1llll1l1l1ll_opy_ = os.environ.get(bstack11ll1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡉࡗࡅࡣࡏ࡝ࡔࠨ⃆"), bstack11ll1_opy_ (u"ࠬ࠭⃇"))
        headers = {
            bstack11ll1_opy_ (u"࠭ࡡࡶࡶ࡫ࡳࡷ࡯ࡺࡢࡶ࡬ࡳࡳ࠭⃈"): bstack11ll1_opy_ (u"ࠧࡃࡧࡤࡶࡪࡸࠠࡼࡿࠪ⃉").format(bstack1llll1l1l1ll_opy_),
            bstack11ll1_opy_ (u"ࠨࡅࡲࡲࡹ࡫࡮ࡵ࠯ࡗࡽࡵ࡫ࠧ⃊"): bstack11ll1_opy_ (u"ࠩࡤࡴࡵࡲࡩࡤࡣࡷ࡭ࡴࡴ࠯࡫ࡵࡲࡲࠬ⃋")
        }
        response = requests.put(bstack1llll1l1l1l1_opy_, headers=headers, json=data)
        bstack1llll1l11lll_opy_ = {}
        try:
            bstack1llll1l11lll_opy_ = response.json()
        except Exception as e:
            logger.debug(bstack11ll1_opy_ (u"ࠥࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦࡰࡢࡴࡶࡩࠥࡐࡓࡐࡐࠣࡶࡪࡹࡰࡰࡰࡶࡩ࠿ࠦࡻࡾࠤ⃌").format(e))
            pass
        logger.debug(bstack11ll1_opy_ (u"ࠦࡗ࡫ࡱࡶࡧࡶࡸ࡚ࡺࡩ࡭ࡵ࠽ࠤࡵࡻࡴࡠࡨࡤ࡭ࡱ࡫ࡤࡠࡶࡨࡷࡹࡹࠠࡳࡧࡶࡴࡴࡴࡳࡦ࠼ࠣࡿࢂࠨ⃍").format(bstack1llll1l11lll_opy_))
        if bstack1llll1l11lll_opy_ is not None:
            bstack1llll1l11lll_opy_[bstack11ll1_opy_ (u"ࠬࡴࡥࡹࡶࡢࡴࡴࡲ࡬ࡠࡶ࡬ࡱࡪ࠭⃎")] = response.headers.get(
                bstack11ll1_opy_ (u"࠭࡮ࡦࡺࡷࡣࡵࡵ࡬࡭ࡡࡷ࡭ࡲ࡫ࠧ⃏"), str(int(datetime.now().timestamp() * 1000))
            )
            bstack1llll1l11lll_opy_[bstack11ll1_opy_ (u"ࠧࡴࡶࡤࡸࡺࡹࠧ⃐")] = response.status_code
        return bstack1llll1l11lll_opy_
    @staticmethod
    def bstack11l11l1l11l_opy_(bstack1llll1l1l1l1_opy_):
        bstack11ll1_opy_ (u"ࠣࠤࠥࠎࠥࠦࠠࠡࠢࠣࠤ࡙ࠥࡥ࡯ࡦࡶࠤࡦࠦࡇࡆࡖࠣࡶࡪࡷࡵࡦࡵࡷࠤࡹࡵࠠࡨࡧࡷࠤࡹ࡮ࡥࠡࡥࡲࡹࡳࡺࠠࡰࡨࠣࡪࡦ࡯࡬ࡦࡦࠣࡸࡪࡹࡴࡴࠌࠣࠤࠥࠦࠠࠡࠢࠣࠦࠧࠨ⃑")
        bstack1llll1l1l1ll_opy_ = os.environ.get(bstack11ll1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡍ⃒࡛࡙࠭"), bstack11ll1_opy_ (u"⃓ࠪࠫ"))
        headers = {
            bstack11ll1_opy_ (u"ࠫࡦࡻࡴࡩࡱࡵ࡭ࡿࡧࡴࡪࡱࡱࠫ⃔"): bstack11ll1_opy_ (u"ࠬࡈࡥࡢࡴࡨࡶࠥࢁࡽࠨ⃕").format(bstack1llll1l1l1ll_opy_),
            bstack11ll1_opy_ (u"࠭ࡃࡰࡰࡷࡩࡳࡺ࠭ࡕࡻࡳࡩࠬ⃖"): bstack11ll1_opy_ (u"ࠧࡢࡲࡳࡰ࡮ࡩࡡࡵ࡫ࡲࡲ࠴ࡰࡳࡰࡰࠪ⃗")
        }
        response = requests.get(bstack1llll1l1l1l1_opy_, headers=headers)
        bstack1llll1l11lll_opy_ = {}
        try:
            bstack1llll1l11lll_opy_ = response.json()
            logger.debug(bstack11ll1_opy_ (u"ࠣࡔࡨࡵࡺ࡫ࡳࡵࡗࡷ࡭ࡱࡹ࠺ࠡࡩࡨࡸࡤ࡬ࡡࡪ࡮ࡨࡨࡤࡺࡥࡴࡶࡶࠤࡷ࡫ࡳࡱࡱࡱࡷࡪࡀࠠࡼࡿ⃘ࠥ").format(bstack1llll1l11lll_opy_))
        except Exception as e:
            logger.debug(bstack11ll1_opy_ (u"ࠤࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥࡶࡡࡳࡵࡨࠤࡏ࡙ࡏࡏࠢࡵࡩࡸࡶ࡯࡯ࡵࡨ࠾ࠥࢁࡽࠡ࠯ࠣࡿࢂࠨ⃙").format(e, response.text))
            pass
        if bstack1llll1l11lll_opy_ is not None:
            bstack1llll1l11lll_opy_[bstack11ll1_opy_ (u"ࠪࡲࡪࡾࡴࡠࡲࡲࡰࡱࡥࡴࡪ࡯ࡨ⃚ࠫ")] = response.headers.get(
                bstack11ll1_opy_ (u"ࠫࡳ࡫ࡸࡵࡡࡳࡳࡱࡲ࡟ࡵ࡫ࡰࡩࠬ⃛"), str(int(datetime.now().timestamp() * 1000))
            )
            bstack1llll1l11lll_opy_[bstack11ll1_opy_ (u"ࠬࡹࡴࡢࡶࡸࡷࠬ⃜")] = response.status_code
        return bstack1llll1l11lll_opy_
    @staticmethod
    def bstack11111l1l1l1_opy_(bstack11l1ll1ll1l_opy_, payload):
        bstack11ll1_opy_ (u"ࠨࠢࠣࠌࠣࠤࠥࠦࠠࠡࠢࠣࡑࡦࡱࡥࡴࠢࡤࠤࡕࡕࡓࡕࠢࡵࡩࡶࡻࡥࡴࡶࠣࡸࡴࠦࡴࡩࡧࠣࡧࡴࡲ࡬ࡦࡥࡷ࠱ࡧࡻࡩ࡭ࡦ࠰ࡨࡦࡺࡡࠡࡧࡱࡨࡵࡵࡩ࡯ࡶ࠱ࠎࠥࠦࠠࠡࠢࠣࠤࠥࡇࡲࡨࡵ࠽ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࡨࡲࡩࡶ࡯ࡪࡰࡷࠤ࠭ࡹࡴࡳࠫ࠽ࠤ࡙࡮ࡥࠡࡃࡓࡍࠥ࡫࡮ࡥࡲࡲ࡭ࡳࡺࠠࡱࡣࡷ࡬࠳ࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࡵࡧࡹ࡭ࡱࡤࡨࠥ࠮ࡤࡪࡥࡷ࠭࠿ࠦࡔࡩࡧࠣࡶࡪࡷࡵࡦࡵࡷࠤࡵࡧࡹ࡭ࡱࡤࡨ࠳ࠐࠠࠡࠢࠣࠤࠥࠦࠠࡓࡧࡷࡹࡷࡴࡳ࠻ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࡥ࡫ࡦࡸ࠿ࠦࡒࡦࡵࡳࡳࡳࡹࡥࠡࡨࡵࡳࡲࠦࡴࡩࡧࠣࡅࡕࡏࠬࠡࡱࡵࠤࡓࡵ࡮ࡦࠢ࡬ࡪࠥ࡬ࡡࡪ࡮ࡨࡨ࠳ࠐࠠࠡࠢࠣࠤࠥࠦࠠࠣࠤࠥ⃝")
        try:
            url = bstack11ll1_opy_ (u"ࠢࡼࡿ࠲ࡿࢂࠨ⃞").format(bstack11l11lll1l1_opy_, bstack11l1ll1ll1l_opy_)
            bstack1llll1l1l1ll_opy_ = os.environ.get(bstack11ll1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡍ࡛ࡂࡠࡌ࡚ࡘࠬ⃟"), bstack11ll1_opy_ (u"ࠩࠪ⃠"))
            headers = {
                bstack11ll1_opy_ (u"ࠪࡥࡺࡺࡨࡰࡴ࡬ࡾࡦࡺࡩࡰࡰࠪ⃡"): bstack11ll1_opy_ (u"ࠫࡇ࡫ࡡࡳࡧࡵࠤࢀࢃࠧ⃢").format(bstack1llll1l1l1ll_opy_),
                bstack11ll1_opy_ (u"ࠬࡉ࡯࡯ࡶࡨࡲࡹ࠳ࡔࡺࡲࡨࠫ⃣"): bstack11ll1_opy_ (u"࠭ࡡࡱࡲ࡯࡭ࡨࡧࡴࡪࡱࡱ࠳࡯ࡹ࡯࡯ࠩ⃤")
            }
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            bstack1llll1l111ll_opy_ = [200, 202]
            if response.status_code in bstack1llll1l111ll_opy_:
                return response.json()
            else:
                logger.error(bstack11ll1_opy_ (u"ࠢࡇࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡧࡴࡲ࡬ࡦࡥࡷࠤࡧࡻࡩ࡭ࡦࠣࡨࡦࡺࡡ࠯ࠢࡖࡸࡦࡺࡵࡴ࠼ࠣࡿࢂ࠲ࠠࡓࡧࡶࡴࡴࡴࡳࡦ࠼ࠣࡿࢂࠨ⃥").format(
                    response.status_code, response.text))
                return None
        except Exception as e:
            logger.error(bstack11ll1_opy_ (u"ࠣࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡱࡱࡶࡸࡤࡩ࡯࡭࡮ࡨࡧࡹࡥࡢࡶ࡫࡯ࡨࡤࡪࡡࡵࡣ࠽ࠤࢀࢃ⃦ࠢ").format(e))
            return None