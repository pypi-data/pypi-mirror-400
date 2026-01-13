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
import re
from bstack_utils.bstack11llll1l1_opy_ import bstack1llll1lllll1_opy_
from bstack_utils.bstack1111111ll1_opy_ import bstack11111l1111_opy_
def bstack1lllll11111l_opy_(fixture_name):
    if fixture_name.startswith(bstack11ll1_opy_ (u"ࠩࡢࡼࡺࡴࡩࡵࡡࡶࡩࡹࡻࡰࡠࡨࡸࡲࡨࡺࡩࡰࡰࡢࡪ࡮ࡾࡴࡶࡴࡨࠫ⁢")):
        return bstack11ll1_opy_ (u"ࠪࡷࡪࡺࡵࡱ࠯ࡩࡹࡳࡩࡴࡪࡱࡱࠫ⁣")
    elif fixture_name.startswith(bstack11ll1_opy_ (u"ࠫࡤࡾࡵ࡯࡫ࡷࡣࡸ࡫ࡴࡶࡲࡢࡱࡴࡪࡵ࡭ࡧࡢࡪ࡮ࡾࡴࡶࡴࡨࠫ⁤")):
        return bstack11ll1_opy_ (u"ࠬࡹࡥࡵࡷࡳ࠱ࡲࡵࡤࡶ࡮ࡨࠫ⁥")
    elif fixture_name.startswith(bstack11ll1_opy_ (u"࠭࡟ࡹࡷࡱ࡭ࡹࡥࡴࡦࡣࡵࡨࡴࡽ࡮ࡠࡨࡸࡲࡨࡺࡩࡰࡰࡢࡪ࡮ࡾࡴࡶࡴࡨࠫ⁦")):
        return bstack11ll1_opy_ (u"ࠧࡵࡧࡤࡶࡩࡵࡷ࡯࠯ࡩࡹࡳࡩࡴࡪࡱࡱࠫ⁧")
    elif fixture_name.startswith(bstack11ll1_opy_ (u"ࠨࡡࡻࡹࡳ࡯ࡴࡠࡶࡨࡥࡷࡪ࡯ࡸࡰࡢࡪࡺࡴࡣࡵ࡫ࡲࡲࡤ࡬ࡩࡹࡶࡸࡶࡪ࠭⁨")):
        return bstack11ll1_opy_ (u"ࠩࡷࡩࡦࡸࡤࡰࡹࡱ࠱ࡲࡵࡤࡶ࡮ࡨࠫ⁩")
def bstack1llll1lll1l1_opy_(fixture_name):
    return bool(re.match(bstack11ll1_opy_ (u"ࠪࡢࡤࡾࡵ࡯࡫ࡷࡣ࠭ࡹࡥࡵࡷࡳࢀࡹ࡫ࡡࡳࡦࡲࡻࡳ࠯࡟ࠩࡨࡸࡲࡨࡺࡩࡰࡰࡿࡱࡴࡪࡵ࡭ࡧࠬࡣ࡫࡯ࡸࡵࡷࡵࡩࡤ࠴ࠪࠨ⁪"), fixture_name))
def bstack1llll1lll111_opy_(fixture_name):
    return bool(re.match(bstack11ll1_opy_ (u"ࠫࡣࡥࡸࡶࡰ࡬ࡸࡤ࠮ࡳࡦࡶࡸࡴࢁࡺࡥࡢࡴࡧࡳࡼࡴࠩࡠ࡯ࡲࡨࡺࡲࡥࡠࡨ࡬ࡼࡹࡻࡲࡦࡡ࠱࠮ࠬ⁫"), fixture_name))
def bstack1lllll1111l1_opy_(fixture_name):
    return bool(re.match(bstack11ll1_opy_ (u"ࠬࡤ࡟ࡹࡷࡱ࡭ࡹࡥࠨࡴࡧࡷࡹࡵࢂࡴࡦࡣࡵࡨࡴࡽ࡮ࠪࡡࡦࡰࡦࡹࡳࡠࡨ࡬ࡼࡹࡻࡲࡦࡡ࠱࠮ࠬ⁬"), fixture_name))
def bstack1lllll111l11_opy_(fixture_name):
    if fixture_name.startswith(bstack11ll1_opy_ (u"࠭࡟ࡹࡷࡱ࡭ࡹࡥࡳࡦࡶࡸࡴࡤ࡬ࡵ࡯ࡥࡷ࡭ࡴࡴ࡟ࡧ࡫ࡻࡸࡺࡸࡥࠨ⁭")):
        return bstack11ll1_opy_ (u"ࠧࡴࡧࡷࡹࡵ࠳ࡦࡶࡰࡦࡸ࡮ࡵ࡮ࠨ⁮"), bstack11ll1_opy_ (u"ࠨࡄࡈࡊࡔࡘࡅࡠࡇࡄࡇࡍ࠭⁯")
    elif fixture_name.startswith(bstack11ll1_opy_ (u"ࠩࡢࡼࡺࡴࡩࡵࡡࡶࡩࡹࡻࡰࡠ࡯ࡲࡨࡺࡲࡥࡠࡨ࡬ࡼࡹࡻࡲࡦࠩ⁰")):
        return bstack11ll1_opy_ (u"ࠪࡷࡪࡺࡵࡱ࠯ࡰࡳࡩࡻ࡬ࡦࠩⁱ"), bstack11ll1_opy_ (u"ࠫࡇࡋࡆࡐࡔࡈࡣࡆࡒࡌࠨ⁲")
    elif fixture_name.startswith(bstack11ll1_opy_ (u"ࠬࡥࡸࡶࡰ࡬ࡸࡤࡺࡥࡢࡴࡧࡳࡼࡴ࡟ࡧࡷࡱࡧࡹ࡯࡯࡯ࡡࡩ࡭ࡽࡺࡵࡳࡧࠪ⁳")):
        return bstack11ll1_opy_ (u"࠭ࡴࡦࡣࡵࡨࡴࡽ࡮࠮ࡨࡸࡲࡨࡺࡩࡰࡰࠪ⁴"), bstack11ll1_opy_ (u"ࠧࡂࡈࡗࡉࡗࡥࡅࡂࡅࡋࠫ⁵")
    elif fixture_name.startswith(bstack11ll1_opy_ (u"ࠨࡡࡻࡹࡳ࡯ࡴࡠࡶࡨࡥࡷࡪ࡯ࡸࡰࡢࡱࡴࡪࡵ࡭ࡧࡢࡪ࡮ࡾࡴࡶࡴࡨࠫ⁶")):
        return bstack11ll1_opy_ (u"ࠩࡷࡩࡦࡸࡤࡰࡹࡱ࠱ࡲࡵࡤࡶ࡮ࡨࠫ⁷"), bstack11ll1_opy_ (u"ࠪࡅࡋ࡚ࡅࡓࡡࡄࡐࡑ࠭⁸")
    return None, None
def bstack1lllll111l1l_opy_(hook_name):
    if hook_name in [bstack11ll1_opy_ (u"ࠫࡸ࡫ࡴࡶࡲࠪ⁹"), bstack11ll1_opy_ (u"ࠬࡺࡥࡢࡴࡧࡳࡼࡴࠧ⁺")]:
        return hook_name.capitalize()
    return hook_name
def bstack1llll1llll11_opy_(hook_name):
    if hook_name in [bstack11ll1_opy_ (u"࠭ࡳࡦࡶࡸࡴࡤ࡬ࡵ࡯ࡥࡷ࡭ࡴࡴࠧ⁻"), bstack11ll1_opy_ (u"ࠧࡴࡧࡷࡹࡵࡥ࡭ࡦࡶ࡫ࡳࡩ࠭⁼")]:
        return bstack11ll1_opy_ (u"ࠨࡄࡈࡊࡔࡘࡅࡠࡇࡄࡇࡍ࠭⁽")
    elif hook_name in [bstack11ll1_opy_ (u"ࠩࡶࡩࡹࡻࡰࡠ࡯ࡲࡨࡺࡲࡥࠨ⁾"), bstack11ll1_opy_ (u"ࠪࡷࡪࡺࡵࡱࡡࡦࡰࡦࡹࡳࠨⁿ")]:
        return bstack11ll1_opy_ (u"ࠫࡇࡋࡆࡐࡔࡈࡣࡆࡒࡌࠨ₀")
    elif hook_name in [bstack11ll1_opy_ (u"ࠬࡺࡥࡢࡴࡧࡳࡼࡴ࡟ࡧࡷࡱࡧࡹ࡯࡯࡯ࠩ₁"), bstack11ll1_opy_ (u"࠭ࡴࡦࡣࡵࡨࡴࡽ࡮ࡠ࡯ࡨࡸ࡭ࡵࡤࠨ₂")]:
        return bstack11ll1_opy_ (u"ࠧࡂࡈࡗࡉࡗࡥࡅࡂࡅࡋࠫ₃")
    elif hook_name in [bstack11ll1_opy_ (u"ࠨࡶࡨࡥࡷࡪ࡯ࡸࡰࡢࡱࡴࡪࡵ࡭ࡧࠪ₄"), bstack11ll1_opy_ (u"ࠩࡷࡩࡦࡸࡤࡰࡹࡱࡣࡨࡲࡡࡴࡵࠪ₅")]:
        return bstack11ll1_opy_ (u"ࠪࡅࡋ࡚ࡅࡓࡡࡄࡐࡑ࠭₆")
    return hook_name
def bstack1llll1llllll_opy_(node, scenario):
    if hasattr(node, bstack11ll1_opy_ (u"ࠫࡨࡧ࡬࡭ࡵࡳࡩࡨ࠭₇")):
        parts = node.nodeid.rsplit(bstack11ll1_opy_ (u"ࠧࡡࠢ₈"))
        params = parts[-1]
        return bstack11ll1_opy_ (u"ࠨࡻࡾࠢ࡞ࡿࢂࠨ₉").format(scenario.name, params)
    return scenario.name
def bstack1lllll1111ll_opy_(node):
    try:
        examples = []
        if hasattr(node, bstack11ll1_opy_ (u"ࠧࡤࡣ࡯ࡰࡸࡶࡥࡤࠩ₊")):
            examples = list(node.callspec.params[bstack11ll1_opy_ (u"ࠨࡡࡳࡽࡹ࡫ࡳࡵࡡࡥࡨࡩࡥࡥࡹࡣࡰࡴࡱ࡫ࠧ₋")].values())
        return examples
    except:
        return []
def bstack1lllll111111_opy_(feature, scenario):
    return list(feature.tags) + list(scenario.tags)
def bstack1llll1lll1ll_opy_(report):
    try:
        status = bstack11ll1_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࠩ₌")
        if report.passed or (report.failed and hasattr(report, bstack11ll1_opy_ (u"ࠥࡻࡦࡹࡸࡧࡣ࡬ࡰࠧ₍"))):
            status = bstack11ll1_opy_ (u"ࠫࡵࡧࡳࡴࡧࡧࠫ₎")
        elif report.skipped:
            status = bstack11ll1_opy_ (u"ࠬࡹ࡫ࡪࡲࡳࡩࡩ࠭₏")
        bstack1llll1lllll1_opy_(status)
    except:
        pass
def bstack1l11ll1111_opy_(status):
    try:
        bstack1llll1lll11l_opy_ = bstack11ll1_opy_ (u"࠭ࡦࡢ࡫࡯ࡩࡩ࠭ₐ")
        if status == bstack11ll1_opy_ (u"ࠧࡱࡣࡶࡷࡪࡪࠧₑ"):
            bstack1llll1lll11l_opy_ = bstack11ll1_opy_ (u"ࠨࡲࡤࡷࡸ࡫ࡤࠨₒ")
        elif status == bstack11ll1_opy_ (u"ࠩࡶ࡯࡮ࡶࡰࡦࡦࠪₓ"):
            bstack1llll1lll11l_opy_ = bstack11ll1_opy_ (u"ࠪࡷࡰ࡯ࡰࡱࡧࡧࠫₔ")
        bstack1llll1lllll1_opy_(bstack1llll1lll11l_opy_)
    except:
        pass
def bstack1llll1llll1l_opy_(item=None, report=None, summary=None, extra=None):
    return
def bstack11l1l111l_opy_():
    bstack11ll1_opy_ (u"ࠦࠧࠨࡃࡩࡧࡦ࡯ࠥ࡯ࡦࠡࡲࡼࡸࡪࡹࡴ࠮ࡲࡤࡶࡦࡲ࡬ࡦ࡮ࠣ࡭ࡸࠦࡩ࡯ࡵࡷࡥࡱࡲࡥࡥࠢࡤࡲࡩࠦࡲࡦࡶࡸࡶࡳࠦࡔࡳࡷࡨࠤ࡮࡬ࠠࡧࡱࡸࡲࡩ࠲ࠠࡇࡣ࡯ࡷࡪࠦ࡯ࡵࡪࡨࡶࡼ࡯ࡳࡦࠤࠥࠦₕ")
    return bstack11111l1111_opy_(bstack11ll1_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸࡤࡶࡡࡳࡣ࡯ࡰࡪࡲࠧₖ"))