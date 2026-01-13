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
import os
import threading
from bstack_utils.config import Config
from bstack_utils.constants import EVENTS, STAGE
from bstack_utils.helper import bstack11l111l1ll1_opy_, bstack1l1111ll1_opy_, bstack1lll11l1l_opy_, bstack1111ll1l_opy_, \
    bstack11l111l111l_opy_
from bstack_utils.measure import measure
def bstack1l1l1ll1ll_opy_(bstack1llll11lll11_opy_):
    for driver in bstack1llll11lll11_opy_:
        try:
            driver.quit()
        except Exception as e:
            pass
@measure(event_name=EVENTS.bstack11llll111_opy_, stage=STAGE.bstack11l1llll1_opy_)
def bstack1ll11ll1ll_opy_(driver, status, reason=bstack11ll1_opy_ (u"ࠫࠬ⃩")):
    bstack1l1l1ll1l_opy_ = Config.bstack1l1l1111_opy_()
    if bstack1l1l1ll1l_opy_.bstack1llllllll1l_opy_():
        return
    bstack1l1l1l11ll_opy_ = bstack1l111l1l_opy_(bstack11ll1_opy_ (u"ࠬࡹࡥࡵࡕࡨࡷࡸ࡯࡯࡯ࡕࡷࡥࡹࡻࡳࠨ⃪"), bstack11ll1_opy_ (u"⃫࠭ࠧ"), status, reason, bstack11ll1_opy_ (u"ࠧࠨ⃬"), bstack11ll1_opy_ (u"ࠨ⃭ࠩ"))
    driver.execute_script(bstack1l1l1l11ll_opy_)
@measure(event_name=EVENTS.bstack11llll111_opy_, stage=STAGE.bstack11l1llll1_opy_)
def bstack11l11111ll_opy_(page, status, reason=bstack11ll1_opy_ (u"⃮ࠩࠪ")):
    try:
        if page is None:
            return
        bstack1l1l1ll1l_opy_ = Config.bstack1l1l1111_opy_()
        if bstack1l1l1ll1l_opy_.bstack1llllllll1l_opy_():
            return
        bstack1l1l1l11ll_opy_ = bstack1l111l1l_opy_(bstack11ll1_opy_ (u"ࠪࡷࡪࡺࡓࡦࡵࡶ࡭ࡴࡴࡓࡵࡣࡷࡹࡸ⃯࠭"), bstack11ll1_opy_ (u"ࠫࠬ⃰"), status, reason, bstack11ll1_opy_ (u"ࠬ࠭⃱"), bstack11ll1_opy_ (u"࠭ࠧ⃲"))
        page.evaluate(bstack11ll1_opy_ (u"ࠢࡠࠢࡀࡂࠥࢁࡽࠣ⃳"), bstack1l1l1l11ll_opy_)
    except Exception as e:
        print(bstack11ll1_opy_ (u"ࠣࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡴࡧࡷࡸ࡮ࡴࡧࠡࡵࡨࡷࡸ࡯࡯࡯ࠢࡶࡸࡦࡺࡵࡴࠢࡩࡳࡷࠦࡰ࡭ࡣࡼࡻࡷ࡯ࡧࡩࡶࠣࡿࢂࠨ⃴"), e)
def bstack1l111l1l_opy_(type, name, status, reason, bstack1ll11ll1_opy_, bstack1ll1l1l11l_opy_):
    bstack111111ll_opy_ = {
        bstack11ll1_opy_ (u"ࠩࡤࡧࡹ࡯࡯࡯ࠩ⃵"): type,
        bstack11ll1_opy_ (u"ࠪࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸ࠭⃶"): {}
    }
    if type == bstack11ll1_opy_ (u"ࠫࡦࡴ࡮ࡰࡶࡤࡸࡪ࠭⃷"):
        bstack111111ll_opy_[bstack11ll1_opy_ (u"ࠬࡧࡲࡨࡷࡰࡩࡳࡺࡳࠨ⃸")][bstack11ll1_opy_ (u"࠭࡬ࡦࡸࡨࡰࠬ⃹")] = bstack1ll11ll1_opy_
        bstack111111ll_opy_[bstack11ll1_opy_ (u"ࠧࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠪ⃺")][bstack11ll1_opy_ (u"ࠨࡦࡤࡸࡦ࠭⃻")] = json.dumps(str(bstack1ll1l1l11l_opy_))
    if type == bstack11ll1_opy_ (u"ࠩࡶࡩࡹ࡙ࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧࠪ⃼"):
        bstack111111ll_opy_[bstack11ll1_opy_ (u"ࠪࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸ࠭⃽")][bstack11ll1_opy_ (u"ࠫࡳࡧ࡭ࡦࠩ⃾")] = name
    if type == bstack11ll1_opy_ (u"ࠬࡹࡥࡵࡕࡨࡷࡸ࡯࡯࡯ࡕࡷࡥࡹࡻࡳࠨ⃿"):
        bstack111111ll_opy_[bstack11ll1_opy_ (u"࠭ࡡࡳࡩࡸࡱࡪࡴࡴࡴࠩ℀")][bstack11ll1_opy_ (u"ࠧࡴࡶࡤࡸࡺࡹࠧ℁")] = status
        if status == bstack11ll1_opy_ (u"ࠨࡨࡤ࡭ࡱ࡫ࡤࠨℂ") and str(reason) != bstack11ll1_opy_ (u"ࠤࠥ℃"):
            bstack111111ll_opy_[bstack11ll1_opy_ (u"ࠪࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸ࠭℄")][bstack11ll1_opy_ (u"ࠫࡷ࡫ࡡࡴࡱࡱࠫ℅")] = json.dumps(str(reason))
    bstack1l11ll111l_opy_ = bstack11ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࡼࡿࠪ℆").format(json.dumps(bstack111111ll_opy_))
    return bstack1l11ll111l_opy_
def bstack11ll1ll1ll_opy_(url, config, logger, bstack1lll111l1l_opy_=False):
    hostname = bstack1l1111ll1_opy_(url)
    is_private = bstack1111ll1l_opy_(hostname)
    try:
        if is_private or bstack1lll111l1l_opy_:
            file_path = bstack11l111l1ll1_opy_(bstack11ll1_opy_ (u"࠭࠮ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠭ℇ"), bstack11ll1_opy_ (u"ࠧ࠯ࡤࡶࡸࡦࡩ࡫࠮ࡥࡲࡲ࡫࡯ࡧ࠯࡬ࡶࡳࡳ࠭℈"), logger)
            if os.environ.get(bstack11ll1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡍࡑࡆࡅࡑࡥࡎࡐࡖࡢࡗࡊ࡚࡟ࡆࡔࡕࡓࡗ࠭℉")) and eval(
                    os.environ.get(bstack11ll1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡎࡒࡇࡆࡒ࡟ࡏࡑࡗࡣࡘࡋࡔࡠࡇࡕࡖࡔࡘࠧℊ"))):
                return
            if (bstack11ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡎࡲࡧࡦࡲࠧℋ") in config and not config[bstack11ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡏࡳࡨࡧ࡬ࠨℌ")]):
                os.environ[bstack11ll1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡑࡕࡃࡂࡎࡢࡒࡔ࡚࡟ࡔࡇࡗࡣࡊࡘࡒࡐࡔࠪℍ")] = str(True)
                bstack1llll11lll1l_opy_ = {bstack11ll1_opy_ (u"࠭ࡨࡰࡵࡷࡲࡦࡳࡥࠨℎ"): hostname}
                bstack11l111l111l_opy_(bstack11ll1_opy_ (u"ࠧ࠯ࡤࡶࡸࡦࡩ࡫࠮ࡥࡲࡲ࡫࡯ࡧ࠯࡬ࡶࡳࡳ࠭ℏ"), bstack11ll1_opy_ (u"ࠨࡰࡸࡨ࡬࡫࡟࡭ࡱࡦࡥࡱ࠭ℐ"), bstack1llll11lll1l_opy_, logger)
    except Exception as e:
        pass
def bstack1l111ll1l1_opy_(caps, bstack1llll11llll1_opy_):
    if bstack11ll1_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬࠼ࡲࡴࡹ࡯࡯࡯ࡵࠪℑ") in caps:
        caps[bstack11ll1_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭࠽ࡳࡵࡺࡩࡰࡰࡶࠫℒ")][bstack11ll1_opy_ (u"ࠫࡱࡵࡣࡢ࡮ࠪℓ")] = True
        if bstack1llll11llll1_opy_:
            caps[bstack11ll1_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯࠿ࡵࡰࡵ࡫ࡲࡲࡸ࠭℔")][bstack11ll1_opy_ (u"࠭࡬ࡰࡥࡤࡰࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨℕ")] = bstack1llll11llll1_opy_
    else:
        caps[bstack11ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴࡬ࡰࡥࡤࡰࠬ№")] = True
        if bstack1llll11llll1_opy_:
            caps[bstack11ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮࡭ࡱࡦࡥࡱࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩ℗")] = bstack1llll11llll1_opy_
def bstack1llll1lllll1_opy_(bstack1111l1l1ll_opy_):
    bstack1llll11ll1ll_opy_ = bstack1lll11l1l_opy_(threading.current_thread(), bstack11ll1_opy_ (u"ࠩࡷࡩࡸࡺࡓࡵࡣࡷࡹࡸ࠭℘"), bstack11ll1_opy_ (u"ࠪࠫℙ"))
    if bstack1llll11ll1ll_opy_ == bstack11ll1_opy_ (u"ࠫࠬℚ") or bstack1llll11ll1ll_opy_ == bstack11ll1_opy_ (u"ࠬࡹ࡫ࡪࡲࡳࡩࡩ࠭ℛ"):
        threading.current_thread().testStatus = bstack1111l1l1ll_opy_
    else:
        if bstack1111l1l1ll_opy_ == bstack11ll1_opy_ (u"࠭ࡦࡢ࡫࡯ࡩࡩ࠭ℜ"):
            threading.current_thread().testStatus = bstack1111l1l1ll_opy_