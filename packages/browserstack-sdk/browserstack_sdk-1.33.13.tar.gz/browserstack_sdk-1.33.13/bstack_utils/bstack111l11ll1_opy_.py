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
import os
import threading
from bstack_utils.config import Config
from bstack_utils.constants import EVENTS, STAGE
from bstack_utils.helper import bstack111ll1l1ll1_opy_, bstack1111lll11_opy_, bstack11lll11l_opy_, bstack11l11l1ll_opy_, \
    bstack111ll1l1l1l_opy_
from bstack_utils.measure import measure
def bstack11l11l11l_opy_(bstack1llll11lll1l_opy_):
    for driver in bstack1llll11lll1l_opy_:
        try:
            driver.quit()
        except Exception as e:
            pass
@measure(event_name=EVENTS.bstack11111l111_opy_, stage=STAGE.bstack1lll1l11l_opy_)
def bstack111lllll1l_opy_(driver, status, reason=bstack11l1l_opy_ (u"⃨ࠪࠫ")):
    bstack1l1ll11111_opy_ = Config.bstack11l1l11ll1_opy_()
    if bstack1l1ll11111_opy_.bstack111111llll_opy_():
        return
    bstack1lll1l111_opy_ = bstack1lll11ll1_opy_(bstack11l1l_opy_ (u"ࠫࡸ࡫ࡴࡔࡧࡶࡷ࡮ࡵ࡮ࡔࡶࡤࡸࡺࡹࠧ⃩"), bstack11l1l_opy_ (u"⃪ࠬ࠭"), status, reason, bstack11l1l_opy_ (u"⃫࠭ࠧ"), bstack11l1l_opy_ (u"ࠧࠨ⃬"))
    driver.execute_script(bstack1lll1l111_opy_)
@measure(event_name=EVENTS.bstack11111l111_opy_, stage=STAGE.bstack1lll1l11l_opy_)
def bstack11lll1lll1_opy_(page, status, reason=bstack11l1l_opy_ (u"ࠨ⃭ࠩ")):
    try:
        if page is None:
            return
        bstack1l1ll11111_opy_ = Config.bstack11l1l11ll1_opy_()
        if bstack1l1ll11111_opy_.bstack111111llll_opy_():
            return
        bstack1lll1l111_opy_ = bstack1lll11ll1_opy_(bstack11l1l_opy_ (u"ࠩࡶࡩࡹ࡙ࡥࡴࡵ࡬ࡳࡳ࡙ࡴࡢࡶࡸࡷ⃮ࠬ"), bstack11l1l_opy_ (u"⃯ࠪࠫ"), status, reason, bstack11l1l_opy_ (u"ࠫࠬ⃰"), bstack11l1l_opy_ (u"ࠬ࠭⃱"))
        page.evaluate(bstack11l1l_opy_ (u"ࠨ࡟ࠡ࠿ࡁࠤࢀࢃࠢ⃲"), bstack1lll1l111_opy_)
    except Exception as e:
        print(bstack11l1l_opy_ (u"ࠢࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣ࡭ࡳࠦࡳࡦࡶࡷ࡭ࡳ࡭ࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠡࡵࡷࡥࡹࡻࡳࠡࡨࡲࡶࠥࡶ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵࠢࡾࢁࠧ⃳"), e)
def bstack1lll11ll1_opy_(type, name, status, reason, bstack11ll1ll11l_opy_, bstack1l1l1ll111_opy_):
    bstack1ll111lll1_opy_ = {
        bstack11l1l_opy_ (u"ࠨࡣࡦࡸ࡮ࡵ࡮ࠨ⃴"): type,
        bstack11l1l_opy_ (u"ࠩࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠬ⃵"): {}
    }
    if type == bstack11l1l_opy_ (u"ࠪࡥࡳࡴ࡯ࡵࡣࡷࡩࠬ⃶"):
        bstack1ll111lll1_opy_[bstack11l1l_opy_ (u"ࠫࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠧ⃷")][bstack11l1l_opy_ (u"ࠬࡲࡥࡷࡧ࡯ࠫ⃸")] = bstack11ll1ll11l_opy_
        bstack1ll111lll1_opy_[bstack11l1l_opy_ (u"࠭ࡡࡳࡩࡸࡱࡪࡴࡴࡴࠩ⃹")][bstack11l1l_opy_ (u"ࠧࡥࡣࡷࡥࠬ⃺")] = json.dumps(str(bstack1l1l1ll111_opy_))
    if type == bstack11l1l_opy_ (u"ࠨࡵࡨࡸࡘ࡫ࡳࡴ࡫ࡲࡲࡓࡧ࡭ࡦࠩ⃻"):
        bstack1ll111lll1_opy_[bstack11l1l_opy_ (u"ࠩࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠬ⃼")][bstack11l1l_opy_ (u"ࠪࡲࡦࡳࡥࠨ⃽")] = name
    if type == bstack11l1l_opy_ (u"ࠫࡸ࡫ࡴࡔࡧࡶࡷ࡮ࡵ࡮ࡔࡶࡤࡸࡺࡹࠧ⃾"):
        bstack1ll111lll1_opy_[bstack11l1l_opy_ (u"ࠬࡧࡲࡨࡷࡰࡩࡳࡺࡳࠨ⃿")][bstack11l1l_opy_ (u"࠭ࡳࡵࡣࡷࡹࡸ࠭℀")] = status
        if status == bstack11l1l_opy_ (u"ࠧࡧࡣ࡬ࡰࡪࡪࠧ℁") and str(reason) != bstack11l1l_opy_ (u"ࠣࠤℂ"):
            bstack1ll111lll1_opy_[bstack11l1l_opy_ (u"ࠩࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠬ℃")][bstack11l1l_opy_ (u"ࠪࡶࡪࡧࡳࡰࡰࠪ℄")] = json.dumps(str(reason))
    bstack11lllll1ll_opy_ = bstack11l1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡩࡽ࡫ࡣࡶࡶࡲࡶ࠿ࠦࡻࡾࠩ℅").format(json.dumps(bstack1ll111lll1_opy_))
    return bstack11lllll1ll_opy_
def bstack11ll1lll_opy_(url, config, logger, bstack11lll1l11l_opy_=False):
    hostname = bstack1111lll11_opy_(url)
    is_private = bstack11l11l1ll_opy_(hostname)
    try:
        if is_private or bstack11lll1l11l_opy_:
            file_path = bstack111ll1l1ll1_opy_(bstack11l1l_opy_ (u"ࠬ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࠬ℆"), bstack11l1l_opy_ (u"࠭࠮ࡣࡵࡷࡥࡨࡱ࠭ࡤࡱࡱࡪ࡮࡭࠮࡫ࡵࡲࡲࠬℇ"), logger)
            if os.environ.get(bstack11l1l_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡌࡐࡅࡄࡐࡤࡔࡏࡕࡡࡖࡉ࡙ࡥࡅࡓࡔࡒࡖࠬ℈")) and eval(
                    os.environ.get(bstack11l1l_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡍࡑࡆࡅࡑࡥࡎࡐࡖࡢࡗࡊ࡚࡟ࡆࡔࡕࡓࡗ࠭℉"))):
                return
            if (bstack11l1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡍࡱࡦࡥࡱ࠭ℊ") in config and not config[bstack11l1l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡎࡲࡧࡦࡲࠧℋ")]):
                os.environ[bstack11l1l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡐࡔࡉࡁࡍࡡࡑࡓ࡙ࡥࡓࡆࡖࡢࡉࡗࡘࡏࡓࠩℌ")] = str(True)
                bstack1llll11llll1_opy_ = {bstack11l1l_opy_ (u"ࠬ࡮࡯ࡴࡶࡱࡥࡲ࡫ࠧℍ"): hostname}
                bstack111ll1l1l1l_opy_(bstack11l1l_opy_ (u"࠭࠮ࡣࡵࡷࡥࡨࡱ࠭ࡤࡱࡱࡪ࡮࡭࠮࡫ࡵࡲࡲࠬℎ"), bstack11l1l_opy_ (u"ࠧ࡯ࡷࡧ࡫ࡪࡥ࡬ࡰࡥࡤࡰࠬℏ"), bstack1llll11llll1_opy_, logger)
    except Exception as e:
        pass
def bstack1ll1l11l1l_opy_(caps, bstack1llll11lll11_opy_):
    if bstack11l1l_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫࠻ࡱࡳࡸ࡮ࡵ࡮ࡴࠩℐ") in caps:
        caps[bstack11l1l_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬࠼ࡲࡴࡹ࡯࡯࡯ࡵࠪℑ")][bstack11l1l_opy_ (u"ࠪࡰࡴࡩࡡ࡭ࠩℒ")] = True
        if bstack1llll11lll11_opy_:
            caps[bstack11l1l_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮࠾ࡴࡶࡴࡪࡱࡱࡷࠬℓ")][bstack11l1l_opy_ (u"ࠬࡲ࡯ࡤࡣ࡯ࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧ℔")] = bstack1llll11lll11_opy_
    else:
        caps[bstack11l1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡲ࡯ࡤࡣ࡯ࠫℕ")] = True
        if bstack1llll11lll11_opy_:
            caps[bstack11l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴࡬ࡰࡥࡤࡰࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨ№")] = bstack1llll11lll11_opy_
def bstack1lllll1111l1_opy_(bstack1111l1lll1_opy_):
    bstack1llll11ll1ll_opy_ = bstack11lll11l_opy_(threading.current_thread(), bstack11l1l_opy_ (u"ࠨࡶࡨࡷࡹ࡙ࡴࡢࡶࡸࡷࠬ℗"), bstack11l1l_opy_ (u"ࠩࠪ℘"))
    if bstack1llll11ll1ll_opy_ == bstack11l1l_opy_ (u"ࠪࠫℙ") or bstack1llll11ll1ll_opy_ == bstack11l1l_opy_ (u"ࠫࡸࡱࡩࡱࡲࡨࡨࠬℚ"):
        threading.current_thread().testStatus = bstack1111l1lll1_opy_
    else:
        if bstack1111l1lll1_opy_ == bstack11l1l_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡨࡨࠬℛ"):
            threading.current_thread().testStatus = bstack1111l1lll1_opy_