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
import re
from bstack_utils.bstack111l11ll1_opy_ import bstack1lllll1111l1_opy_
from bstack_utils.bstack1111111l11_opy_ import bstack11111l1111_opy_
def bstack1lllll111l1l_opy_(fixture_name):
    if fixture_name.startswith(bstack11l1l_opy_ (u"ࠨࡡࡻࡹࡳ࡯ࡴࡠࡵࡨࡸࡺࡶ࡟ࡧࡷࡱࡧࡹ࡯࡯࡯ࡡࡩ࡭ࡽࡺࡵࡳࡧࠪ⁡")):
        return bstack11l1l_opy_ (u"ࠩࡶࡩࡹࡻࡰ࠮ࡨࡸࡲࡨࡺࡩࡰࡰࠪ⁢")
    elif fixture_name.startswith(bstack11l1l_opy_ (u"ࠪࡣࡽࡻ࡮ࡪࡶࡢࡷࡪࡺࡵࡱࡡࡰࡳࡩࡻ࡬ࡦࡡࡩ࡭ࡽࡺࡵࡳࡧࠪ⁣")):
        return bstack11l1l_opy_ (u"ࠫࡸ࡫ࡴࡶࡲ࠰ࡱࡴࡪࡵ࡭ࡧࠪ⁤")
    elif fixture_name.startswith(bstack11l1l_opy_ (u"ࠬࡥࡸࡶࡰ࡬ࡸࡤࡺࡥࡢࡴࡧࡳࡼࡴ࡟ࡧࡷࡱࡧࡹ࡯࡯࡯ࡡࡩ࡭ࡽࡺࡵࡳࡧࠪ⁥")):
        return bstack11l1l_opy_ (u"࠭ࡴࡦࡣࡵࡨࡴࡽ࡮࠮ࡨࡸࡲࡨࡺࡩࡰࡰࠪ⁦")
    elif fixture_name.startswith(bstack11l1l_opy_ (u"ࠧࡠࡺࡸࡲ࡮ࡺ࡟ࡵࡧࡤࡶࡩࡵࡷ࡯ࡡࡩࡹࡳࡩࡴࡪࡱࡱࡣ࡫࡯ࡸࡵࡷࡵࡩࠬ⁧")):
        return bstack11l1l_opy_ (u"ࠨࡶࡨࡥࡷࡪ࡯ࡸࡰ࠰ࡱࡴࡪࡵ࡭ࡧࠪ⁨")
def bstack1lllll1111ll_opy_(fixture_name):
    return bool(re.match(bstack11l1l_opy_ (u"ࠩࡡࡣࡽࡻ࡮ࡪࡶࡢࠬࡸ࡫ࡴࡶࡲࡿࡸࡪࡧࡲࡥࡱࡺࡲ࠮ࡥࠨࡧࡷࡱࡧࡹ࡯࡯࡯ࡾࡰࡳࡩࡻ࡬ࡦࠫࡢࡪ࡮ࡾࡴࡶࡴࡨࡣ࠳࠰ࠧ⁩"), fixture_name))
def bstack1llll1llllll_opy_(fixture_name):
    return bool(re.match(bstack11l1l_opy_ (u"ࠪࡢࡤࡾࡵ࡯࡫ࡷࡣ࠭ࡹࡥࡵࡷࡳࢀࡹ࡫ࡡࡳࡦࡲࡻࡳ࠯࡟࡮ࡱࡧࡹࡱ࡫࡟ࡧ࡫ࡻࡸࡺࡸࡥࡠ࠰࠭ࠫ⁪"), fixture_name))
def bstack1llll1lll111_opy_(fixture_name):
    return bool(re.match(bstack11l1l_opy_ (u"ࠫࡣࡥࡸࡶࡰ࡬ࡸࡤ࠮ࡳࡦࡶࡸࡴࢁࡺࡥࡢࡴࡧࡳࡼࡴࠩࡠࡥ࡯ࡥࡸࡹ࡟ࡧ࡫ࡻࡸࡺࡸࡥࡠ࠰࠭ࠫ⁫"), fixture_name))
def bstack1llll1lll11l_opy_(fixture_name):
    if fixture_name.startswith(bstack11l1l_opy_ (u"ࠬࡥࡸࡶࡰ࡬ࡸࡤࡹࡥࡵࡷࡳࡣ࡫ࡻ࡮ࡤࡶ࡬ࡳࡳࡥࡦࡪࡺࡷࡹࡷ࡫ࠧ⁬")):
        return bstack11l1l_opy_ (u"࠭ࡳࡦࡶࡸࡴ࠲࡬ࡵ࡯ࡥࡷ࡭ࡴࡴࠧ⁭"), bstack11l1l_opy_ (u"ࠧࡃࡇࡉࡓࡗࡋ࡟ࡆࡃࡆࡌࠬ⁮")
    elif fixture_name.startswith(bstack11l1l_opy_ (u"ࠨࡡࡻࡹࡳ࡯ࡴࡠࡵࡨࡸࡺࡶ࡟࡮ࡱࡧࡹࡱ࡫࡟ࡧ࡫ࡻࡸࡺࡸࡥࠨ⁯")):
        return bstack11l1l_opy_ (u"ࠩࡶࡩࡹࡻࡰ࠮࡯ࡲࡨࡺࡲࡥࠨ⁰"), bstack11l1l_opy_ (u"ࠪࡆࡊࡌࡏࡓࡇࡢࡅࡑࡒࠧⁱ")
    elif fixture_name.startswith(bstack11l1l_opy_ (u"ࠫࡤࡾࡵ࡯࡫ࡷࡣࡹ࡫ࡡࡳࡦࡲࡻࡳࡥࡦࡶࡰࡦࡸ࡮ࡵ࡮ࡠࡨ࡬ࡼࡹࡻࡲࡦࠩ⁲")):
        return bstack11l1l_opy_ (u"ࠬࡺࡥࡢࡴࡧࡳࡼࡴ࠭ࡧࡷࡱࡧࡹ࡯࡯࡯ࠩ⁳"), bstack11l1l_opy_ (u"࠭ࡁࡇࡖࡈࡖࡤࡋࡁࡄࡊࠪ⁴")
    elif fixture_name.startswith(bstack11l1l_opy_ (u"ࠧࡠࡺࡸࡲ࡮ࡺ࡟ࡵࡧࡤࡶࡩࡵࡷ࡯ࡡࡰࡳࡩࡻ࡬ࡦࡡࡩ࡭ࡽࡺࡵࡳࡧࠪ⁵")):
        return bstack11l1l_opy_ (u"ࠨࡶࡨࡥࡷࡪ࡯ࡸࡰ࠰ࡱࡴࡪࡵ࡭ࡧࠪ⁶"), bstack11l1l_opy_ (u"ࠩࡄࡊ࡙ࡋࡒࡠࡃࡏࡐࠬ⁷")
    return None, None
def bstack1lllll111l11_opy_(hook_name):
    if hook_name in [bstack11l1l_opy_ (u"ࠪࡷࡪࡺࡵࡱࠩ⁸"), bstack11l1l_opy_ (u"ࠫࡹ࡫ࡡࡳࡦࡲࡻࡳ࠭⁹")]:
        return hook_name.capitalize()
    return hook_name
def bstack1llll1llll11_opy_(hook_name):
    if hook_name in [bstack11l1l_opy_ (u"ࠬࡹࡥࡵࡷࡳࡣ࡫ࡻ࡮ࡤࡶ࡬ࡳࡳ࠭⁺"), bstack11l1l_opy_ (u"࠭ࡳࡦࡶࡸࡴࡤࡳࡥࡵࡪࡲࡨࠬ⁻")]:
        return bstack11l1l_opy_ (u"ࠧࡃࡇࡉࡓࡗࡋ࡟ࡆࡃࡆࡌࠬ⁼")
    elif hook_name in [bstack11l1l_opy_ (u"ࠨࡵࡨࡸࡺࡶ࡟࡮ࡱࡧࡹࡱ࡫ࠧ⁽"), bstack11l1l_opy_ (u"ࠩࡶࡩࡹࡻࡰࡠࡥ࡯ࡥࡸࡹࠧ⁾")]:
        return bstack11l1l_opy_ (u"ࠪࡆࡊࡌࡏࡓࡇࡢࡅࡑࡒࠧⁿ")
    elif hook_name in [bstack11l1l_opy_ (u"ࠫࡹ࡫ࡡࡳࡦࡲࡻࡳࡥࡦࡶࡰࡦࡸ࡮ࡵ࡮ࠨ₀"), bstack11l1l_opy_ (u"ࠬࡺࡥࡢࡴࡧࡳࡼࡴ࡟࡮ࡧࡷ࡬ࡴࡪࠧ₁")]:
        return bstack11l1l_opy_ (u"࠭ࡁࡇࡖࡈࡖࡤࡋࡁࡄࡊࠪ₂")
    elif hook_name in [bstack11l1l_opy_ (u"ࠧࡵࡧࡤࡶࡩࡵࡷ࡯ࡡࡰࡳࡩࡻ࡬ࡦࠩ₃"), bstack11l1l_opy_ (u"ࠨࡶࡨࡥࡷࡪ࡯ࡸࡰࡢࡧࡱࡧࡳࡴࠩ₄")]:
        return bstack11l1l_opy_ (u"ࠩࡄࡊ࡙ࡋࡒࡠࡃࡏࡐࠬ₅")
    return hook_name
def bstack1llll1lll1l1_opy_(node, scenario):
    if hasattr(node, bstack11l1l_opy_ (u"ࠪࡧࡦࡲ࡬ࡴࡲࡨࡧࠬ₆")):
        parts = node.nodeid.rsplit(bstack11l1l_opy_ (u"ࠦࡠࠨ₇"))
        params = parts[-1]
        return bstack11l1l_opy_ (u"ࠧࢁࡽࠡ࡝ࡾࢁࠧ₈").format(scenario.name, params)
    return scenario.name
def bstack1lllll11111l_opy_(node):
    try:
        examples = []
        if hasattr(node, bstack11l1l_opy_ (u"࠭ࡣࡢ࡮࡯ࡷࡵ࡫ࡣࠨ₉")):
            examples = list(node.callspec.params[bstack11l1l_opy_ (u"ࠧࡠࡲࡼࡸࡪࡹࡴࡠࡤࡧࡨࡤ࡫ࡸࡢ࡯ࡳࡰࡪ࠭₊")].values())
        return examples
    except:
        return []
def bstack1lllll111111_opy_(feature, scenario):
    return list(feature.tags) + list(scenario.tags)
def bstack1llll1lll1ll_opy_(report):
    try:
        status = bstack11l1l_opy_ (u"ࠨࡨࡤ࡭ࡱ࡫ࡤࠨ₋")
        if report.passed or (report.failed and hasattr(report, bstack11l1l_opy_ (u"ࠤࡺࡥࡸࡾࡦࡢ࡫࡯ࠦ₌"))):
            status = bstack11l1l_opy_ (u"ࠪࡴࡦࡹࡳࡦࡦࠪ₍")
        elif report.skipped:
            status = bstack11l1l_opy_ (u"ࠫࡸࡱࡩࡱࡲࡨࡨࠬ₎")
        bstack1lllll1111l1_opy_(status)
    except:
        pass
def bstack11ll1ll1_opy_(status):
    try:
        bstack1llll1llll1l_opy_ = bstack11l1l_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡨࡨࠬ₏")
        if status == bstack11l1l_opy_ (u"࠭ࡰࡢࡵࡶࡩࡩ࠭ₐ"):
            bstack1llll1llll1l_opy_ = bstack11l1l_opy_ (u"ࠧࡱࡣࡶࡷࡪࡪࠧₑ")
        elif status == bstack11l1l_opy_ (u"ࠨࡵ࡮࡭ࡵࡶࡥࡥࠩₒ"):
            bstack1llll1llll1l_opy_ = bstack11l1l_opy_ (u"ࠩࡶ࡯࡮ࡶࡰࡦࡦࠪₓ")
        bstack1lllll1111l1_opy_(bstack1llll1llll1l_opy_)
    except:
        pass
def bstack1llll1lllll1_opy_(item=None, report=None, summary=None, extra=None):
    return
def bstack1l1ll1l11_opy_():
    bstack11l1l_opy_ (u"ࠥࠦࠧࡉࡨࡦࡥ࡮ࠤ࡮࡬ࠠࡱࡻࡷࡩࡸࡺ࠭ࡱࡣࡵࡥࡱࡲࡥ࡭ࠢ࡬ࡷࠥ࡯࡮ࡴࡶࡤࡰࡱ࡫ࡤࠡࡣࡱࡨࠥࡸࡥࡵࡷࡵࡲ࡚ࠥࡲࡶࡧࠣ࡭࡫ࠦࡦࡰࡷࡱࡨ࠱ࠦࡆࡢ࡮ࡶࡩࠥࡵࡴࡩࡧࡵࡻ࡮ࡹࡥࠣࠤࠥₔ")
    return bstack11111l1111_opy_(bstack11l1l_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࡣࡵࡧࡲࡢ࡮࡯ࡩࡱ࠭ₕ"))