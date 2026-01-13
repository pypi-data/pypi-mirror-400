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
import os
import re
from enum import Enum
bstack11l111ll1l_opy_ = {
  bstack11ll1_opy_ (u"࠭ࡵࡴࡧࡵࡒࡦࡳࡥࠨᠲ"): bstack11ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡵࡴࡧࡵࠫᠳ"),
  bstack11ll1_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡌࡧࡼࠫᠴ"): bstack11ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯࡭ࡨࡽࠬᠵ"),
  bstack11ll1_opy_ (u"ࠪࡳࡸ࡜ࡥࡳࡵ࡬ࡳࡳ࠭ᠶ"): bstack11ll1_opy_ (u"ࠫࡴࡹ࡟ࡷࡧࡵࡷ࡮ࡵ࡮ࠨᠷ"),
  bstack11ll1_opy_ (u"ࠬࡻࡳࡦ࡙࠶ࡇࠬᠸ"): bstack11ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡻࡳࡦࡡࡺ࠷ࡨ࠭ᠹ"),
  bstack11ll1_opy_ (u"ࠧࡱࡴࡲ࡮ࡪࡩࡴࡏࡣࡰࡩࠬᠺ"): bstack11ll1_opy_ (u"ࠨࡲࡵࡳ࡯࡫ࡣࡵࠩᠻ"),
  bstack11ll1_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡏࡣࡰࡩࠬᠼ"): bstack11ll1_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࠩᠽ"),
  bstack11ll1_opy_ (u"ࠫࡸ࡫ࡳࡴ࡫ࡲࡲࡓࡧ࡭ࡦࠩᠾ"): bstack11ll1_opy_ (u"ࠬࡴࡡ࡮ࡧࠪᠿ"),
  bstack11ll1_opy_ (u"࠭ࡤࡦࡤࡸ࡫ࠬᡀ"): bstack11ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡤࡦࡤࡸ࡫ࠬᡁ"),
  bstack11ll1_opy_ (u"ࠨࡥࡲࡲࡸࡵ࡬ࡦࡎࡲ࡫ࡸ࠭ᡂ"): bstack11ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡥࡲࡲࡸࡵ࡬ࡦࠩᡃ"),
  bstack11ll1_opy_ (u"ࠪࡲࡪࡺࡷࡰࡴ࡮ࡐࡴ࡭ࡳࠨᡄ"): bstack11ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡲࡪࡺࡷࡰࡴ࡮ࡐࡴ࡭ࡳࠨᡅ"),
  bstack11ll1_opy_ (u"ࠬࡧࡰࡱ࡫ࡸࡱࡑࡵࡧࡴࠩᡆ"): bstack11ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡧࡰࡱ࡫ࡸࡱࡑࡵࡧࡴࠩᡇ"),
  bstack11ll1_opy_ (u"ࠧࡷ࡫ࡧࡩࡴ࠭ᡈ"): bstack11ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡷ࡫ࡧࡩࡴ࠭ᡉ"),
  bstack11ll1_opy_ (u"ࠩࡶࡩࡱ࡫࡮ࡪࡷࡰࡐࡴ࡭ࡳࠨᡊ"): bstack11ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡶࡩࡱ࡫࡮ࡪࡷࡰࡐࡴ࡭ࡳࠨᡋ"),
  bstack11ll1_opy_ (u"ࠫࡹ࡫࡬ࡦ࡯ࡨࡸࡷࡿࡌࡰࡩࡶࠫᡌ"): bstack11ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡹ࡫࡬ࡦ࡯ࡨࡸࡷࡿࡌࡰࡩࡶࠫᡍ"),
  bstack11ll1_opy_ (u"࠭ࡧࡦࡱࡏࡳࡨࡧࡴࡪࡱࡱࠫᡎ"): bstack11ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡧࡦࡱࡏࡳࡨࡧࡴࡪࡱࡱࠫᡏ"),
  bstack11ll1_opy_ (u"ࠨࡶ࡬ࡱࡪࢀ࡯࡯ࡧࠪᡐ"): bstack11ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡶ࡬ࡱࡪࢀ࡯࡯ࡧࠪᡑ"),
  bstack11ll1_opy_ (u"ࠪࡷࡪࡲࡥ࡯࡫ࡸࡱ࡛࡫ࡲࡴ࡫ࡲࡲࠬᡒ"): bstack11ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡷࡪࡲࡥ࡯࡫ࡸࡱࡤࡼࡥࡳࡵ࡬ࡳࡳ࠭ᡓ"),
  bstack11ll1_opy_ (u"ࠬࡳࡡࡴ࡭ࡆࡳࡲࡳࡡ࡯ࡦࡶࠫᡔ"): bstack11ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡳࡡࡴ࡭ࡆࡳࡲࡳࡡ࡯ࡦࡶࠫᡕ"),
  bstack11ll1_opy_ (u"ࠧࡪࡦ࡯ࡩ࡙࡯࡭ࡦࡱࡸࡸࠬᡖ"): bstack11ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡪࡦ࡯ࡩ࡙࡯࡭ࡦࡱࡸࡸࠬᡗ"),
  bstack11ll1_opy_ (u"ࠩࡰࡥࡸࡱࡂࡢࡵ࡬ࡧࡆࡻࡴࡩࠩᡘ"): bstack11ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡰࡥࡸࡱࡂࡢࡵ࡬ࡧࡆࡻࡴࡩࠩᡙ"),
  bstack11ll1_opy_ (u"ࠫࡸ࡫࡮ࡥࡍࡨࡽࡸ࠭ᡚ"): bstack11ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡸ࡫࡮ࡥࡍࡨࡽࡸ࠭ᡛ"),
  bstack11ll1_opy_ (u"࠭ࡡࡶࡶࡲ࡛ࡦ࡯ࡴࠨᡜ"): bstack11ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡡࡶࡶࡲ࡛ࡦ࡯ࡴࠨᡝ"),
  bstack11ll1_opy_ (u"ࠨࡪࡲࡷࡹࡹࠧᡞ"): bstack11ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡪࡲࡷࡹࡹࠧᡟ"),
  bstack11ll1_opy_ (u"ࠪࡦ࡫ࡩࡡࡤࡪࡨࠫᡠ"): bstack11ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡦ࡫ࡩࡡࡤࡪࡨࠫᡡ"),
  bstack11ll1_opy_ (u"ࠬࡽࡳࡍࡱࡦࡥࡱ࡙ࡵࡱࡲࡲࡶࡹ࠭ᡢ"): bstack11ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡽࡳࡍࡱࡦࡥࡱ࡙ࡵࡱࡲࡲࡶࡹ࠭ᡣ"),
  bstack11ll1_opy_ (u"ࠧࡥ࡫ࡶࡥࡧࡲࡥࡄࡱࡵࡷࡗ࡫ࡳࡵࡴ࡬ࡧࡹ࡯࡯࡯ࡵࠪᡤ"): bstack11ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡥ࡫ࡶࡥࡧࡲࡥࡄࡱࡵࡷࡗ࡫ࡳࡵࡴ࡬ࡧࡹ࡯࡯࡯ࡵࠪᡥ"),
  bstack11ll1_opy_ (u"ࠩࡧࡩࡻ࡯ࡣࡦࡐࡤࡱࡪ࠭ᡦ"): bstack11ll1_opy_ (u"ࠪࡨࡪࡼࡩࡤࡧࠪᡧ"),
  bstack11ll1_opy_ (u"ࠫࡷ࡫ࡡ࡭ࡏࡲࡦ࡮ࡲࡥࠨᡨ"): bstack11ll1_opy_ (u"ࠬࡸࡥࡢ࡮ࡢࡱࡴࡨࡩ࡭ࡧࠪᡩ"),
  bstack11ll1_opy_ (u"࠭ࡡࡱࡲ࡬ࡹࡲ࡜ࡥࡳࡵ࡬ࡳࡳ࠭ᡪ"): bstack11ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡡࡱࡲ࡬ࡹࡲࡥࡶࡦࡴࡶ࡭ࡴࡴࠧᡫ"),
  bstack11ll1_opy_ (u"ࠨࡥࡸࡷࡹࡵ࡭ࡏࡧࡷࡻࡴࡸ࡫ࠨᡬ"): bstack11ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡥࡸࡷࡹࡵ࡭ࡏࡧࡷࡻࡴࡸ࡫ࠨᡭ"),
  bstack11ll1_opy_ (u"ࠪࡲࡪࡺࡷࡰࡴ࡮ࡔࡷࡵࡦࡪ࡮ࡨࠫᡮ"): bstack11ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡲࡪࡺࡷࡰࡴ࡮ࡔࡷࡵࡦࡪ࡮ࡨࠫᡯ"),
  bstack11ll1_opy_ (u"ࠬࡧࡣࡤࡧࡳࡸࡎࡴࡳࡦࡥࡸࡶࡪࡉࡥࡳࡶࡶࠫᡰ"): bstack11ll1_opy_ (u"࠭ࡡࡤࡥࡨࡴࡹ࡙ࡳ࡭ࡅࡨࡶࡹࡹࠧᡱ"),
  bstack11ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࡙ࡄࡌࠩᡲ"): bstack11ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࡙ࡄࡌࠩᡳ"),
  bstack11ll1_opy_ (u"ࠩࡶࡳࡺࡸࡣࡦࠩᡴ"): bstack11ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡶࡳࡺࡸࡣࡦࠩᡵ"),
  bstack11ll1_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭ᡶ"): bstack11ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡧࡻࡩ࡭ࡦࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭ᡷ"),
  bstack11ll1_opy_ (u"࠭ࡨࡰࡵࡷࡒࡦࡳࡥࠨᡸ"): bstack11ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡨࡰࡵࡷࡒࡦࡳࡥࠨ᡹"),
  bstack11ll1_opy_ (u"ࠨࡧࡱࡥࡧࡲࡥࡔ࡫ࡰࠫ᡺"): bstack11ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡧࡱࡥࡧࡲࡥࡔ࡫ࡰࠫ᡻"),
  bstack11ll1_opy_ (u"ࠪࡷ࡮ࡳࡏࡱࡶ࡬ࡳࡳࡹࠧ᡼"): bstack11ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡷ࡮ࡳࡏࡱࡶ࡬ࡳࡳࡹࠧ᡽"),
  bstack11ll1_opy_ (u"ࠬࡻࡰ࡭ࡱࡤࡨࡒ࡫ࡤࡪࡣࠪ᡾"): bstack11ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡻࡰ࡭ࡱࡤࡨࡒ࡫ࡤࡪࡣࠪ᡿"),
  bstack11ll1_opy_ (u"ࠧࡵࡧࡶࡸ࡭ࡻࡢࡃࡷ࡬ࡰࡩ࡛ࡵࡪࡦࠪᢀ"): bstack11ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡵࡧࡶࡸ࡭ࡻࡢࡃࡷ࡬ࡰࡩ࡛ࡵࡪࡦࠪᢁ"),
  bstack11ll1_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡑࡴࡲࡨࡺࡩࡴࡎࡣࡳࠫᢂ"): bstack11ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡥࡹ࡮ࡲࡤࡑࡴࡲࡨࡺࡩࡴࡎࡣࡳࠫᢃ")
}
bstack11l11ll11l1_opy_ = [
  bstack11ll1_opy_ (u"ࠫࡴࡹࠧᢄ"),
  bstack11ll1_opy_ (u"ࠬࡵࡳࡗࡧࡵࡷ࡮ࡵ࡮ࠨᢅ"),
  bstack11ll1_opy_ (u"࠭ࡳࡦ࡮ࡨࡲ࡮ࡻ࡭ࡗࡧࡵࡷ࡮ࡵ࡮ࠨᢆ"),
  bstack11ll1_opy_ (u"ࠧࡴࡧࡶࡷ࡮ࡵ࡮ࡏࡣࡰࡩࠬᢇ"),
  bstack11ll1_opy_ (u"ࠨࡦࡨࡺ࡮ࡩࡥࡏࡣࡰࡩࠬᢈ"),
  bstack11ll1_opy_ (u"ࠩࡵࡩࡦࡲࡍࡰࡤ࡬ࡰࡪ࠭ᢉ"),
  bstack11ll1_opy_ (u"ࠪࡥࡵࡶࡩࡶ࡯࡙ࡩࡷࡹࡩࡰࡰࠪᢊ"),
]
bstack1l1ll11l11_opy_ = {
  bstack11ll1_opy_ (u"ࠫࡺࡹࡥࡳࡐࡤࡱࡪ࠭ᢋ"): [bstack11ll1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡚࡙ࡅࡓࡐࡄࡑࡊ࠭ᢌ"), bstack11ll1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡛ࡓࡆࡔࡢࡒࡆࡓࡅࠨᢍ")],
  bstack11ll1_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡋࡦࡻࠪᢎ"): bstack11ll1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡂࡅࡆࡉࡘ࡙࡟ࡌࡇ࡜ࠫᢏ"),
  bstack11ll1_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡏࡣࡰࡩࠬᢐ"): bstack11ll1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡅ࡙ࡎࡒࡄࡠࡐࡄࡑࡊ࠭ᢑ"),
  bstack11ll1_opy_ (u"ࠫࡵࡸ࡯࡫ࡧࡦࡸࡓࡧ࡭ࡦࠩᢒ"): bstack11ll1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡕࡘࡏࡋࡇࡆࡘࡤࡔࡁࡎࡇࠪᢓ"),
  bstack11ll1_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨᢔ"): bstack11ll1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡂࡖࡋࡏࡈࡤࡏࡄࡆࡐࡗࡍࡋࡏࡅࡓࠩᢕ"),
  bstack11ll1_opy_ (u"ࠨࡲࡤࡶࡦࡲ࡬ࡦ࡮ࡶࡔࡪࡸࡐ࡭ࡣࡷࡪࡴࡸ࡭ࠨᢖ"): bstack11ll1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡒࡄࡖࡆࡒࡌࡆࡎࡖࡣࡕࡋࡒࡠࡒࡏࡅ࡙ࡌࡏࡓࡏࠪᢗ"),
  bstack11ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡎࡲࡧࡦࡲࠧᢘ"): bstack11ll1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡐࡔࡉࡁࡍࠩᢙ"),
  bstack11ll1_opy_ (u"ࠬࡸࡥࡳࡷࡱࡘࡪࡹࡴࡴࠩᢚ"): bstack11ll1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡘࡅࡓࡗࡑࡣ࡙ࡋࡓࡕࡕࠪᢛ"),
  bstack11ll1_opy_ (u"ࠧࡢࡲࡳࠫᢜ"): [bstack11ll1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡂࡒࡓࡣࡎࡊࠧᢝ"), bstack11ll1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡃࡓࡔࠬᢞ")],
  bstack11ll1_opy_ (u"ࠪࡰࡴ࡭ࡌࡦࡸࡨࡰࠬᢟ"): bstack11ll1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡗࡉࡑ࡟ࡍࡑࡊࡐࡊ࡜ࡅࡍࠩᢠ"),
  bstack11ll1_opy_ (u"ࠬࡧࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࠩᢡ"): bstack11ll1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡇࡕࡕࡑࡐࡅ࡙ࡏࡏࡏࠩᢢ"),
  bstack11ll1_opy_ (u"ࠧࡵࡧࡶࡸࡔࡨࡳࡦࡴࡹࡥࡧ࡯࡬ࡪࡶࡼࠫᢣ"): [bstack11ll1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡤࡕࡂࡔࡇࡕ࡚ࡆࡈࡉࡍࡋࡗ࡝ࠬᢤ"), bstack11ll1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡥࡒࡆࡒࡒࡖ࡙ࡏࡎࡈࠩᢥ")],
  bstack11ll1_opy_ (u"ࠪࡸࡺࡸࡢࡰࡕࡦࡥࡱ࡫ࠧᢦ"): bstack11ll1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘ࡚ࡘࡂࡐࡕࡆࡅࡑࡋࠧᢧ"),
  bstack11ll1_opy_ (u"ࠬࡹ࡭ࡢࡴࡷࡗࡪࡲࡥࡤࡶ࡬ࡳࡳࡌࡥࡢࡶࡸࡶࡪࡈࡲࡢࡰࡦ࡬ࡪࡹࡅࡏࡘࠪᢨ"): bstack11ll1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡕࡒࡄࡊࡈࡗ࡙ࡘࡁࡕࡋࡒࡒࡤ࡙ࡍࡂࡔࡗࡣࡘࡋࡌࡆࡅࡗࡍࡔࡔ࡟ࡇࡇࡄࡘ࡚ࡘࡅࡠࡄࡕࡅࡓࡉࡈࡆࡕᢩࠪ")
}
bstack11l1l111l1_opy_ = {
  bstack11ll1_opy_ (u"ࠧࡶࡵࡨࡶࡓࡧ࡭ࡦࠩᢪ"): [bstack11ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡶࡵࡨࡶࡤࡴࡡ࡮ࡧࠪ᢫"), bstack11ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡷࡶࡩࡷࡔࡡ࡮ࡧࠪ᢬")],
  bstack11ll1_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵࡎࡩࡾ࠭᢭"): [bstack11ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡥࡨࡩࡥࡴࡵࡢ࡯ࡪࡿࠧ᢮"), bstack11ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡦࡩࡣࡦࡵࡶࡏࡪࡿࠧ᢯")],
  bstack11ll1_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡓࡧ࡭ࡦࠩᢰ"): bstack11ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡢࡶ࡫࡯ࡨࡓࡧ࡭ࡦࠩᢱ"),
  bstack11ll1_opy_ (u"ࠨࡲࡵࡳ࡯࡫ࡣࡵࡐࡤࡱࡪ࠭ᢲ"): bstack11ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡲࡵࡳ࡯࡫ࡣࡵࡐࡤࡱࡪ࠭ᢳ"),
  bstack11ll1_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬᢴ"): bstack11ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡦࡺ࡯࡬ࡥࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬᢵ"),
  bstack11ll1_opy_ (u"ࠬࡶࡡࡳࡣ࡯ࡰࡪࡲࡳࡑࡧࡵࡔࡱࡧࡴࡧࡱࡵࡱࠬᢶ"): [bstack11ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡶࡰࡱࠩᢷ"), bstack11ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡰࡢࡴࡤࡰࡱ࡫࡬ࡴࡒࡨࡶࡕࡲࡡࡵࡨࡲࡶࡲ࠭ᢸ")],
  bstack11ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡌࡰࡥࡤࡰࠬᢹ"): bstack11ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯࡮ࡲࡧࡦࡲࠧᢺ"),
  bstack11ll1_opy_ (u"ࠪࡶࡪࡸࡵ࡯ࡖࡨࡷࡹࡹࠧᢻ"): bstack11ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡶࡪࡸࡵ࡯ࡖࡨࡷࡹࡹࠧᢼ"),
  bstack11ll1_opy_ (u"ࠬࡧࡰࡱࠩᢽ"): bstack11ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡧࡰࡱࠩᢾ"),
  bstack11ll1_opy_ (u"ࠧ࡭ࡱࡪࡐࡪࡼࡥ࡭ࠩᢿ"): bstack11ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮࡭ࡱࡪࡐࡪࡼࡥ࡭ࠩᣀ"),
  bstack11ll1_opy_ (u"ࠩࡤࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳ࠭ᣁ"): bstack11ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡤࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳ࠭ᣂ"),
  bstack11ll1_opy_ (u"ࠦࡸࡳࡡࡳࡶࡖࡩࡱ࡫ࡣࡵ࡫ࡲࡲࡋ࡫ࡡࡵࡷࡵࡩࡇࡸࡡ࡯ࡥ࡫ࡩࡸࡉࡌࡊࠤᣃ"): bstack11ll1_opy_ (u"ࠧࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡹ࡫ࡳࡵࡑࡵࡧ࡭࡫ࡳࡵࡴࡤࡸ࡮ࡵ࡮࠯ࡵࡰࡥࡷࡺࡓࡦ࡮ࡨࡧࡹ࡯࡯࡯ࡈࡨࡥࡹࡻࡲࡦࡄࡵࡥࡳࡩࡨࡦࡵࠥᣄ"),
}
bstack11ll1lll1l_opy_ = {
  bstack11ll1_opy_ (u"࠭࡯ࡴࡘࡨࡶࡸ࡯࡯࡯ࠩᣅ"): bstack11ll1_opy_ (u"ࠧࡰࡵࡢࡺࡪࡸࡳࡪࡱࡱࠫᣆ"),
  bstack11ll1_opy_ (u"ࠨࡵࡨࡰࡪࡴࡩࡶ࡯࡙ࡩࡷࡹࡩࡰࡰࠪᣇ"): [bstack11ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡵࡨࡰࡪࡴࡩࡶ࡯ࡢࡺࡪࡸࡳࡪࡱࡱࠫᣈ"), bstack11ll1_opy_ (u"ࠪࡷࡪࡲࡥ࡯࡫ࡸࡱࡤࡼࡥࡳࡵ࡬ࡳࡳ࠭ᣉ")],
  bstack11ll1_opy_ (u"ࠫࡸ࡫ࡳࡴ࡫ࡲࡲࡓࡧ࡭ࡦࠩᣊ"): bstack11ll1_opy_ (u"ࠬࡴࡡ࡮ࡧࠪᣋ"),
  bstack11ll1_opy_ (u"࠭ࡤࡦࡸ࡬ࡧࡪࡔࡡ࡮ࡧࠪᣌ"): bstack11ll1_opy_ (u"ࠧࡥࡧࡹ࡭ࡨ࡫ࠧᣍ"),
  bstack11ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡐࡤࡱࡪ࠭ᣎ"): [bstack11ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࠪᣏ"), bstack11ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡣࡳࡧ࡭ࡦࠩᣐ")],
  bstack11ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶ࡛࡫ࡲࡴ࡫ࡲࡲࠬᣑ"): bstack11ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡥࡶࡦࡴࡶ࡭ࡴࡴࠧᣒ"),
  bstack11ll1_opy_ (u"࠭ࡲࡦࡣ࡯ࡑࡴࡨࡩ࡭ࡧࠪᣓ"): bstack11ll1_opy_ (u"ࠧࡳࡧࡤࡰࡤࡳ࡯ࡣ࡫࡯ࡩࠬᣔ"),
  bstack11ll1_opy_ (u"ࠨࡣࡳࡴ࡮ࡻ࡭ࡗࡧࡵࡷ࡮ࡵ࡮ࠨᣕ"): [bstack11ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡣࡳࡴ࡮ࡻ࡭ࡠࡸࡨࡶࡸ࡯࡯࡯ࠩᣖ"), bstack11ll1_opy_ (u"ࠪࡥࡵࡶࡩࡶ࡯ࡢࡺࡪࡸࡳࡪࡱࡱࠫᣗ")],
  bstack11ll1_opy_ (u"ࠫࡦࡩࡣࡦࡲࡷࡍࡳࡹࡥࡤࡷࡵࡩࡈ࡫ࡲࡵࡵࠪᣘ"): [bstack11ll1_opy_ (u"ࠬࡧࡣࡤࡧࡳࡸࡘࡹ࡬ࡄࡧࡵࡸࡸ࠭ᣙ"), bstack11ll1_opy_ (u"࠭ࡡࡤࡥࡨࡴࡹ࡙ࡳ࡭ࡅࡨࡶࡹ࠭ᣚ")]
}
bstack1l1111l1l_opy_ = [
  bstack11ll1_opy_ (u"ࠧࡢࡥࡦࡩࡵࡺࡉ࡯ࡵࡨࡧࡺࡸࡥࡄࡧࡵࡸࡸ࠭ᣛ"),
  bstack11ll1_opy_ (u"ࠨࡲࡤ࡫ࡪࡒ࡯ࡢࡦࡖࡸࡷࡧࡴࡦࡩࡼࠫᣜ"),
  bstack11ll1_opy_ (u"ࠩࡳࡶࡴࡾࡹࠨᣝ"),
  bstack11ll1_opy_ (u"ࠪࡷࡪࡺࡗࡪࡰࡧࡳࡼࡘࡥࡤࡶࠪᣞ"),
  bstack11ll1_opy_ (u"ࠫࡹ࡯࡭ࡦࡱࡸࡸࡸ࠭ᣟ"),
  bstack11ll1_opy_ (u"ࠬࡹࡴࡳ࡫ࡦࡸࡋ࡯࡬ࡦࡋࡱࡸࡪࡸࡡࡤࡶࡤࡦ࡮ࡲࡩࡵࡻࠪᣠ"),
  bstack11ll1_opy_ (u"࠭ࡵ࡯ࡪࡤࡲࡩࡲࡥࡥࡒࡵࡳࡲࡶࡴࡃࡧ࡫ࡥࡻ࡯࡯ࡳࠩᣡ"),
  bstack11ll1_opy_ (u"ࠧࡨࡱࡲ࡫࠿ࡩࡨࡳࡱࡰࡩࡔࡶࡴࡪࡱࡱࡷࠬᣢ"),
  bstack11ll1_opy_ (u"ࠨ࡯ࡲࡾ࠿࡬ࡩࡳࡧࡩࡳࡽࡕࡰࡵ࡫ࡲࡲࡸ࠭ᣣ"),
  bstack11ll1_opy_ (u"ࠩࡰࡷ࠿࡫ࡤࡨࡧࡒࡴࡹ࡯࡯࡯ࡵࠪᣤ"),
  bstack11ll1_opy_ (u"ࠪࡷࡪࡀࡩࡦࡑࡳࡸ࡮ࡵ࡮ࡴࠩᣥ"),
  bstack11ll1_opy_ (u"ࠫࡸࡧࡦࡢࡴ࡬࠲ࡴࡶࡴࡪࡱࡱࡷࠬᣦ"),
]
bstack1llll11111_opy_ = [
  bstack11ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࠩᣧ"),
  bstack11ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࡒࡴࡹ࡯࡯࡯ࡵࠪᣨ"),
  bstack11ll1_opy_ (u"ࠧ࡭ࡱࡦࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭ᣩ"),
  bstack11ll1_opy_ (u"ࠨࡲࡤࡶࡦࡲ࡬ࡦ࡮ࡶࡔࡪࡸࡐ࡭ࡣࡷࡪࡴࡸ࡭ࠨᣪ"),
  bstack11ll1_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬᣫ"),
  bstack11ll1_opy_ (u"ࠪࡰࡴ࡭ࡌࡦࡸࡨࡰࠬᣬ"),
  bstack11ll1_opy_ (u"ࠫ࡭ࡺࡴࡱࡒࡵࡳࡽࡿࠧᣭ"),
  bstack11ll1_opy_ (u"ࠬ࡮ࡴࡵࡲࡶࡔࡷࡵࡸࡺࠩᣮ"),
  bstack11ll1_opy_ (u"࠭ࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࠩᣯ"),
  bstack11ll1_opy_ (u"ࠧࡵࡧࡶࡸࡈࡵ࡮ࡵࡧࡻࡸࡔࡶࡴࡪࡱࡱࡷࠬᣰ"),
  bstack11ll1_opy_ (u"ࠨࡶࡨࡷࡹࡕࡢࡴࡧࡵࡺࡦࡨࡩ࡭࡫ࡷࡽࠬᣱ"),
  bstack11ll1_opy_ (u"ࠩࡷࡩࡸࡺࡒࡦࡲࡲࡶࡹ࡯࡮ࡨࠩᣲ"),
  bstack11ll1_opy_ (u"ࠪࡧࡺࡹࡴࡰ࡯࡙ࡥࡷ࡯ࡡࡣ࡮ࡨࡷࠬᣳ"),
  bstack11ll1_opy_ (u"ࠫࡨࡻࡳࡵࡱࡰࡘࡦ࡭ࠧᣴ"),
  bstack11ll1_opy_ (u"ࠬࡧࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࠩᣵ"),
  bstack11ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡆࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠨ᣶"),
  bstack11ll1_opy_ (u"ࠧࡳࡧࡵࡹࡳ࡚ࡥࡴࡶࡶࠫ᣷"),
  bstack11ll1_opy_ (u"ࠨࡅࡘࡗ࡙ࡕࡍࡠࡖࡄࡋࡤ࠷ࠧ᣸"),
  bstack11ll1_opy_ (u"ࠩࡆ࡙ࡘ࡚ࡏࡎࡡࡗࡅࡌࡥ࠲ࠨ᣹"),
  bstack11ll1_opy_ (u"ࠪࡇ࡚࡙ࡔࡐࡏࡢࡘࡆࡍ࡟࠴ࠩ᣺"),
  bstack11ll1_opy_ (u"ࠫࡈ࡛ࡓࡕࡑࡐࡣ࡙ࡇࡇࡠ࠶ࠪ᣻"),
  bstack11ll1_opy_ (u"ࠬࡉࡕࡔࡖࡒࡑࡤ࡚ࡁࡈࡡ࠸ࠫ᣼"),
  bstack11ll1_opy_ (u"࠭ࡃࡖࡕࡗࡓࡒࡥࡔࡂࡉࡢ࠺ࠬ᣽"),
  bstack11ll1_opy_ (u"ࠧࡄࡗࡖࡘࡔࡓ࡟ࡕࡃࡊࡣ࠼࠭᣾"),
  bstack11ll1_opy_ (u"ࠨࡅࡘࡗ࡙ࡕࡍࡠࡖࡄࡋࡤ࠾ࠧ᣿"),
  bstack11ll1_opy_ (u"ࠩࡆ࡙ࡘ࡚ࡏࡎࡡࡗࡅࡌࡥ࠹ࠨᤀ"),
  bstack11ll1_opy_ (u"ࠪࡴࡪࡸࡣࡺࠩᤁ"),
  bstack11ll1_opy_ (u"ࠫࡵ࡫ࡲࡤࡻࡒࡴࡹ࡯࡯࡯ࡵࠪᤂ"),
  bstack11ll1_opy_ (u"ࠬࡶࡥࡳࡥࡼࡇࡦࡶࡴࡶࡴࡨࡑࡴࡪࡥࠨᤃ"),
  bstack11ll1_opy_ (u"࠭ࡤࡪࡵࡤࡦࡱ࡫ࡁࡶࡶࡲࡇࡦࡶࡴࡶࡴࡨࡐࡴ࡭ࡳࠨᤄ"),
  bstack11ll1_opy_ (u"ࠧࡵࡷࡵࡦࡴ࡙ࡣࡢ࡮ࡨࠫᤅ"),
  bstack11ll1_opy_ (u"ࠨࡶࡸࡶࡧࡵࡓࡤࡣ࡯ࡩࡔࡶࡴࡪࡱࡱࡷࠬᤆ"),
  bstack11ll1_opy_ (u"ࠩࡷࡩࡸࡺࡏࡳࡥ࡫ࡩࡸࡺࡲࡢࡶ࡬ࡳࡳࡕࡰࡵ࡫ࡲࡲࡸ࠭ᤇ"),
  bstack11ll1_opy_ (u"ࠪ࡬ࡺࡨࡒࡦࡩ࡬ࡳࡳ࠭ᤈ")
]
bstack11l1l11llll_opy_ = [
  bstack11ll1_opy_ (u"ࠫࡺࡶ࡬ࡰࡣࡧࡑࡪࡪࡩࡢࠩᤉ"),
  bstack11ll1_opy_ (u"ࠬࡻࡳࡦࡴࡑࡥࡲ࡫ࠧᤊ"),
  bstack11ll1_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸࡑࡥࡺࠩᤋ"),
  bstack11ll1_opy_ (u"ࠧࡴࡧࡶࡷ࡮ࡵ࡮ࡏࡣࡰࡩࠬᤌ"),
  bstack11ll1_opy_ (u"ࠨࡶࡨࡷࡹࡖࡲࡪࡱࡵ࡭ࡹࡿࠧᤍ"),
  bstack11ll1_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡏࡣࡰࡩࠬᤎ"),
  bstack11ll1_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡖࡤ࡫ࠬᤏ"),
  bstack11ll1_opy_ (u"ࠫࡵࡸ࡯࡫ࡧࡦࡸࡓࡧ࡭ࡦࠩᤐ"),
  bstack11ll1_opy_ (u"ࠬࡹࡥ࡭ࡧࡱ࡭ࡺࡳࡖࡦࡴࡶ࡭ࡴࡴࠧᤑ"),
  bstack11ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡎࡢ࡯ࡨࠫᤒ"),
  bstack11ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡗࡧࡵࡷ࡮ࡵ࡮ࠨᤓ"),
  bstack11ll1_opy_ (u"ࠨ࡮ࡲࡧࡦࡲࠧᤔ"),
  bstack11ll1_opy_ (u"ࠩࡲࡷࠬᤕ"),
  bstack11ll1_opy_ (u"ࠪࡳࡸ࡜ࡥࡳࡵ࡬ࡳࡳ࠭ᤖ"),
  bstack11ll1_opy_ (u"ࠫ࡭ࡵࡳࡵࡵࠪᤗ"),
  bstack11ll1_opy_ (u"ࠬࡧࡵࡵࡱ࡚ࡥ࡮ࡺࠧᤘ"),
  bstack11ll1_opy_ (u"࠭ࡲࡦࡩ࡬ࡳࡳ࠭ᤙ"),
  bstack11ll1_opy_ (u"ࠧࡵ࡫ࡰࡩࡿࡵ࡮ࡦࠩᤚ"),
  bstack11ll1_opy_ (u"ࠨ࡯ࡤࡧ࡭࡯࡮ࡦࠩᤛ"),
  bstack11ll1_opy_ (u"ࠩࡵࡩࡸࡵ࡬ࡶࡶ࡬ࡳࡳ࠭ᤜ"),
  bstack11ll1_opy_ (u"ࠪ࡭ࡩࡲࡥࡕ࡫ࡰࡩࡴࡻࡴࠨᤝ"),
  bstack11ll1_opy_ (u"ࠫࡩ࡫ࡶࡪࡥࡨࡓࡷ࡯ࡥ࡯ࡶࡤࡸ࡮ࡵ࡮ࠨᤞ"),
  bstack11ll1_opy_ (u"ࠬࡼࡩࡥࡧࡲࠫ᤟"),
  bstack11ll1_opy_ (u"࠭࡮ࡰࡒࡤ࡫ࡪࡒ࡯ࡢࡦࡗ࡭ࡲ࡫࡯ࡶࡶࠪᤠ"),
  bstack11ll1_opy_ (u"ࠧࡣࡨࡦࡥࡨ࡮ࡥࠨᤡ"),
  bstack11ll1_opy_ (u"ࠨࡦࡨࡦࡺ࡭ࠧᤢ"),
  bstack11ll1_opy_ (u"ࠩࡦࡹࡸࡺ࡯࡮ࡕࡦࡶࡪ࡫࡮ࡴࡪࡲࡸࡸ࠭ᤣ"),
  bstack11ll1_opy_ (u"ࠪࡧࡺࡹࡴࡰ࡯ࡖࡩࡳࡪࡋࡦࡻࡶࠫᤤ"),
  bstack11ll1_opy_ (u"ࠫࡷ࡫ࡡ࡭ࡏࡲࡦ࡮ࡲࡥࠨᤥ"),
  bstack11ll1_opy_ (u"ࠬࡴ࡯ࡑ࡫ࡳࡩࡱ࡯࡮ࡦࠩᤦ"),
  bstack11ll1_opy_ (u"࠭ࡣࡩࡧࡦ࡯࡚ࡘࡌࠨᤧ"),
  bstack11ll1_opy_ (u"ࠧ࡭ࡱࡦࡥࡱࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩᤨ"),
  bstack11ll1_opy_ (u"ࠨࡣࡦࡧࡪࡶࡴࡄࡱࡲ࡯࡮࡫ࡳࠨᤩ"),
  bstack11ll1_opy_ (u"ࠩࡦࡥࡵࡺࡵࡳࡧࡆࡶࡦࡹࡨࠨᤪ"),
  bstack11ll1_opy_ (u"ࠪࡨࡪࡼࡩࡤࡧࡑࡥࡲ࡫ࠧᤫ"),
  bstack11ll1_opy_ (u"ࠫࡦࡶࡰࡪࡷࡰ࡚ࡪࡸࡳࡪࡱࡱࠫ᤬"),
  bstack11ll1_opy_ (u"ࠬࡧࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࡘࡨࡶࡸ࡯࡯࡯ࠩ᤭"),
  bstack11ll1_opy_ (u"࠭࡮ࡰࡄ࡯ࡥࡳࡱࡐࡰ࡮࡯࡭ࡳ࡭ࠧ᤮"),
  bstack11ll1_opy_ (u"ࠧ࡮ࡣࡶ࡯ࡘ࡫࡮ࡥࡍࡨࡽࡸ࠭᤯"),
  bstack11ll1_opy_ (u"ࠨࡦࡨࡺ࡮ࡩࡥࡍࡱࡪࡷࠬᤰ"),
  bstack11ll1_opy_ (u"ࠩࡧࡩࡻ࡯ࡣࡦࡋࡧࠫᤱ"),
  bstack11ll1_opy_ (u"ࠪࡨࡪࡪࡩࡤࡣࡷࡩࡩࡊࡥࡷ࡫ࡦࡩࠬᤲ"),
  bstack11ll1_opy_ (u"ࠫ࡭࡫ࡡࡥࡧࡵࡔࡦࡸࡡ࡮ࡵࠪᤳ"),
  bstack11ll1_opy_ (u"ࠬࡶࡨࡰࡰࡨࡒࡺࡳࡢࡦࡴࠪᤴ"),
  bstack11ll1_opy_ (u"࠭࡮ࡦࡶࡺࡳࡷࡱࡌࡰࡩࡶࠫᤵ"),
  bstack11ll1_opy_ (u"ࠧ࡯ࡧࡷࡻࡴࡸ࡫ࡍࡱࡪࡷࡔࡶࡴࡪࡱࡱࡷࠬᤶ"),
  bstack11ll1_opy_ (u"ࠨࡥࡲࡲࡸࡵ࡬ࡦࡎࡲ࡫ࡸ࠭ᤷ"),
  bstack11ll1_opy_ (u"ࠩࡸࡷࡪ࡝࠳ࡄࠩᤸ"),
  bstack11ll1_opy_ (u"ࠪࡥࡵࡶࡩࡶ࡯ࡏࡳ࡬ࡹ᤹ࠧ"),
  bstack11ll1_opy_ (u"ࠫࡪࡴࡡࡣ࡮ࡨࡆ࡮ࡵ࡭ࡦࡶࡵ࡭ࡨ࠭᤺"),
  bstack11ll1_opy_ (u"ࠬࡼࡩࡥࡧࡲ࡚࠷᤻࠭"),
  bstack11ll1_opy_ (u"࠭࡭ࡪࡦࡖࡩࡸࡹࡩࡰࡰࡌࡲࡸࡺࡡ࡭࡮ࡄࡴࡵࡹࠧ᤼"),
  bstack11ll1_opy_ (u"ࠧࡦࡵࡳࡶࡪࡹࡳࡰࡕࡨࡶࡻ࡫ࡲࠨ᤽"),
  bstack11ll1_opy_ (u"ࠨࡵࡨࡰࡪࡴࡩࡶ࡯ࡏࡳ࡬ࡹࠧ᤾"),
  bstack11ll1_opy_ (u"ࠩࡶࡩࡱ࡫࡮ࡪࡷࡰࡇࡩࡶࠧ᤿"),
  bstack11ll1_opy_ (u"ࠪࡸࡪࡲࡥ࡮ࡧࡷࡶࡾࡒ࡯ࡨࡵࠪ᥀"),
  bstack11ll1_opy_ (u"ࠫࡸࡿ࡮ࡤࡖ࡬ࡱࡪ࡝ࡩࡵࡪࡑࡘࡕ࠭᥁"),
  bstack11ll1_opy_ (u"ࠬ࡭ࡥࡰࡎࡲࡧࡦࡺࡩࡰࡰࠪ᥂"),
  bstack11ll1_opy_ (u"࠭ࡧࡱࡵࡏࡳࡨࡧࡴࡪࡱࡱࠫ᥃"),
  bstack11ll1_opy_ (u"ࠧ࡯ࡧࡷࡻࡴࡸ࡫ࡑࡴࡲࡪ࡮ࡲࡥࠨ᥄"),
  bstack11ll1_opy_ (u"ࠨࡥࡸࡷࡹࡵ࡭ࡏࡧࡷࡻࡴࡸ࡫ࠨ᥅"),
  bstack11ll1_opy_ (u"ࠩࡩࡳࡷࡩࡥࡄࡪࡤࡲ࡬࡫ࡊࡢࡴࠪ᥆"),
  bstack11ll1_opy_ (u"ࠪࡼࡲࡹࡊࡢࡴࠪ᥇"),
  bstack11ll1_opy_ (u"ࠫࡽࡳࡸࡋࡣࡵࠫ᥈"),
  bstack11ll1_opy_ (u"ࠬࡳࡡࡴ࡭ࡆࡳࡲࡳࡡ࡯ࡦࡶࠫ᥉"),
  bstack11ll1_opy_ (u"࠭࡭ࡢࡵ࡮ࡆࡦࡹࡩࡤࡃࡸࡸ࡭࠭᥊"),
  bstack11ll1_opy_ (u"ࠧࡸࡵࡏࡳࡨࡧ࡬ࡔࡷࡳࡴࡴࡸࡴࠨ᥋"),
  bstack11ll1_opy_ (u"ࠨࡦ࡬ࡷࡦࡨ࡬ࡦࡅࡲࡶࡸࡘࡥࡴࡶࡵ࡭ࡨࡺࡩࡰࡰࡶࠫ᥌"),
  bstack11ll1_opy_ (u"ࠩࡤࡴࡵ࡜ࡥࡳࡵ࡬ࡳࡳ࠭᥍"),
  bstack11ll1_opy_ (u"ࠪࡥࡨࡩࡥࡱࡶࡌࡲࡸ࡫ࡣࡶࡴࡨࡇࡪࡸࡴࡴࠩ᥎"),
  bstack11ll1_opy_ (u"ࠫࡷ࡫ࡳࡪࡩࡱࡅࡵࡶࠧ᥏"),
  bstack11ll1_opy_ (u"ࠬࡪࡩࡴࡣࡥࡰࡪࡇ࡮ࡪ࡯ࡤࡸ࡮ࡵ࡮ࡴࠩᥐ"),
  bstack11ll1_opy_ (u"࠭ࡣࡢࡰࡤࡶࡾ࠭ᥑ"),
  bstack11ll1_opy_ (u"ࠧࡧ࡫ࡵࡩ࡫ࡵࡸࠨᥒ"),
  bstack11ll1_opy_ (u"ࠨࡥ࡫ࡶࡴࡳࡥࠨᥓ"),
  bstack11ll1_opy_ (u"ࠩ࡬ࡩࠬᥔ"),
  bstack11ll1_opy_ (u"ࠪࡩࡩ࡭ࡥࠨᥕ"),
  bstack11ll1_opy_ (u"ࠫࡸࡧࡦࡢࡴ࡬ࠫᥖ"),
  bstack11ll1_opy_ (u"ࠬࡷࡵࡦࡷࡨࠫᥗ"),
  bstack11ll1_opy_ (u"࠭ࡩ࡯ࡶࡨࡶࡳࡧ࡬ࠨᥘ"),
  bstack11ll1_opy_ (u"ࠧࡢࡲࡳࡗࡹࡵࡲࡦࡅࡲࡲ࡫࡯ࡧࡶࡴࡤࡸ࡮ࡵ࡮ࠨᥙ"),
  bstack11ll1_opy_ (u"ࠨࡧࡱࡥࡧࡲࡥࡄࡣࡰࡩࡷࡧࡉ࡮ࡣࡪࡩࡎࡴࡪࡦࡥࡷ࡭ࡴࡴࠧᥚ"),
  bstack11ll1_opy_ (u"ࠩࡱࡩࡹࡽ࡯ࡳ࡭ࡏࡳ࡬ࡹࡅࡹࡥ࡯ࡹࡩ࡫ࡈࡰࡵࡷࡷࠬᥛ"),
  bstack11ll1_opy_ (u"ࠪࡲࡪࡺࡷࡰࡴ࡮ࡐࡴ࡭ࡳࡊࡰࡦࡰࡺࡪࡥࡉࡱࡶࡸࡸ࠭ᥜ"),
  bstack11ll1_opy_ (u"ࠫࡺࡶࡤࡢࡶࡨࡅࡵࡶࡓࡦࡶࡷ࡭ࡳ࡭ࡳࠨᥝ"),
  bstack11ll1_opy_ (u"ࠬࡸࡥࡴࡧࡵࡺࡪࡊࡥࡷ࡫ࡦࡩࠬᥞ"),
  bstack11ll1_opy_ (u"࠭ࡳࡰࡷࡵࡧࡪ࠭ᥟ"),
  bstack11ll1_opy_ (u"ࠧࡴࡧࡱࡨࡐ࡫ࡹࡴࠩᥠ"),
  bstack11ll1_opy_ (u"ࠨࡧࡱࡥࡧࡲࡥࡑࡣࡶࡷࡨࡵࡤࡦࠩᥡ"),
  bstack11ll1_opy_ (u"ࠩࡸࡴࡩࡧࡴࡦࡋࡲࡷࡉ࡫ࡶࡪࡥࡨࡗࡪࡺࡴࡪࡰࡪࡷࠬᥢ"),
  bstack11ll1_opy_ (u"ࠪࡩࡳࡧࡢ࡭ࡧࡄࡹࡩ࡯࡯ࡊࡰ࡭ࡩࡨࡺࡩࡰࡰࠪᥣ"),
  bstack11ll1_opy_ (u"ࠫࡪࡴࡡࡣ࡮ࡨࡅࡵࡶ࡬ࡦࡒࡤࡽࠬᥤ"),
  bstack11ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࠭ᥥ"),
  bstack11ll1_opy_ (u"࠭ࡷࡥ࡫ࡲࡗࡪࡸࡶࡪࡥࡨࠫᥦ"),
  bstack11ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࡙ࡄࡌࠩᥧ"),
  bstack11ll1_opy_ (u"ࠨࡲࡵࡩࡻ࡫࡮ࡵࡅࡵࡳࡸࡹࡓࡪࡶࡨࡘࡷࡧࡣ࡬࡫ࡱ࡫ࠬᥨ"),
  bstack11ll1_opy_ (u"ࠩ࡫࡭࡬࡮ࡃࡰࡰࡷࡶࡦࡹࡴࠨᥩ"),
  bstack11ll1_opy_ (u"ࠪࡨࡪࡼࡩࡤࡧࡓࡶࡪ࡬ࡥࡳࡧࡱࡧࡪࡹࠧᥪ"),
  bstack11ll1_opy_ (u"ࠫࡪࡴࡡࡣ࡮ࡨࡗ࡮ࡳࠧᥫ"),
  bstack11ll1_opy_ (u"ࠬࡹࡩ࡮ࡑࡳࡸ࡮ࡵ࡮ࡴࠩᥬ"),
  bstack11ll1_opy_ (u"࠭ࡲࡦ࡯ࡲࡺࡪࡏࡏࡔࡃࡳࡴࡘ࡫ࡴࡵ࡫ࡱ࡫ࡸࡒ࡯ࡤࡣ࡯࡭ࡿࡧࡴࡪࡱࡱࠫᥭ"),
  bstack11ll1_opy_ (u"ࠧࡩࡱࡶࡸࡓࡧ࡭ࡦࠩ᥮"),
  bstack11ll1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪ᥯"),
  bstack11ll1_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࠫᥰ"),
  bstack11ll1_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡓࡧ࡭ࡦࠩᥱ"),
  bstack11ll1_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲ࡜ࡥࡳࡵ࡬ࡳࡳ࠭ᥲ"),
  bstack11ll1_opy_ (u"ࠬࡶࡡࡨࡧࡏࡳࡦࡪࡓࡵࡴࡤࡸࡪ࡭ࡹࠨᥳ"),
  bstack11ll1_opy_ (u"࠭ࡰࡳࡱࡻࡽࠬᥴ"),
  bstack11ll1_opy_ (u"ࠧࡵ࡫ࡰࡩࡴࡻࡴࡴࠩ᥵"),
  bstack11ll1_opy_ (u"ࠨࡷࡱ࡬ࡦࡴࡤ࡭ࡧࡧࡔࡷࡵ࡭ࡱࡶࡅࡩ࡭ࡧࡶࡪࡱࡵࠫ᥶")
]
bstack1lll111lll_opy_ = {
  bstack11ll1_opy_ (u"ࠩࡹࠫ᥷"): bstack11ll1_opy_ (u"ࠪࡺࠬ᥸"),
  bstack11ll1_opy_ (u"ࠫ࡫࠭᥹"): bstack11ll1_opy_ (u"ࠬ࡬ࠧ᥺"),
  bstack11ll1_opy_ (u"࠭ࡦࡰࡴࡦࡩࠬ᥻"): bstack11ll1_opy_ (u"ࠧࡧࡱࡵࡧࡪ࠭᥼"),
  bstack11ll1_opy_ (u"ࠨࡱࡱࡰࡾࡧࡵࡵࡱࡰࡥࡹ࡫ࠧ᥽"): bstack11ll1_opy_ (u"ࠩࡲࡲࡱࡿࡁࡶࡶࡲࡱࡦࡺࡥࠨ᥾"),
  bstack11ll1_opy_ (u"ࠪࡪࡴࡸࡣࡦ࡮ࡲࡧࡦࡲࠧ᥿"): bstack11ll1_opy_ (u"ࠫ࡫ࡵࡲࡤࡧ࡯ࡳࡨࡧ࡬ࠨᦀ"),
  bstack11ll1_opy_ (u"ࠬࡶࡲࡰࡺࡼ࡬ࡴࡹࡴࠨᦁ"): bstack11ll1_opy_ (u"࠭ࡰࡳࡱࡻࡽࡍࡵࡳࡵࠩᦂ"),
  bstack11ll1_opy_ (u"ࠧࡱࡴࡲࡼࡾࡶ࡯ࡳࡶࠪᦃ"): bstack11ll1_opy_ (u"ࠨࡲࡵࡳࡽࡿࡐࡰࡴࡷࠫᦄ"),
  bstack11ll1_opy_ (u"ࠩࡳࡶࡴࡾࡹࡶࡵࡨࡶࠬᦅ"): bstack11ll1_opy_ (u"ࠪࡴࡷࡵࡸࡺࡗࡶࡩࡷ࠭ᦆ"),
  bstack11ll1_opy_ (u"ࠫࡵࡸ࡯ࡹࡻࡳࡥࡸࡹࠧᦇ"): bstack11ll1_opy_ (u"ࠬࡶࡲࡰࡺࡼࡔࡦࡹࡳࠨᦈ"),
  bstack11ll1_opy_ (u"࠭࡬ࡰࡥࡤࡰࡵࡸ࡯ࡹࡻ࡫ࡳࡸࡺࠧᦉ"): bstack11ll1_opy_ (u"ࠧ࡭ࡱࡦࡥࡱࡖࡲࡰࡺࡼࡌࡴࡹࡴࠨᦊ"),
  bstack11ll1_opy_ (u"ࠨ࡮ࡲࡧࡦࡲࡰࡳࡱࡻࡽࡵࡵࡲࡵࠩᦋ"): bstack11ll1_opy_ (u"ࠩ࡯ࡳࡨࡧ࡬ࡑࡴࡲࡼࡾࡖ࡯ࡳࡶࠪᦌ"),
  bstack11ll1_opy_ (u"ࠪࡰࡴࡩࡡ࡭ࡲࡵࡳࡽࡿࡵࡴࡧࡵࠫᦍ"): bstack11ll1_opy_ (u"ࠫ࠲ࡲ࡯ࡤࡣ࡯ࡔࡷࡵࡸࡺࡗࡶࡩࡷ࠭ᦎ"),
  bstack11ll1_opy_ (u"ࠬ࠳࡬ࡰࡥࡤࡰࡵࡸ࡯ࡹࡻࡸࡷࡪࡸࠧᦏ"): bstack11ll1_opy_ (u"࠭࠭࡭ࡱࡦࡥࡱࡖࡲࡰࡺࡼ࡙ࡸ࡫ࡲࠨᦐ"),
  bstack11ll1_opy_ (u"ࠧ࡭ࡱࡦࡥࡱࡶࡲࡰࡺࡼࡴࡦࡹࡳࠨᦑ"): bstack11ll1_opy_ (u"ࠨ࠯࡯ࡳࡨࡧ࡬ࡑࡴࡲࡼࡾࡖࡡࡴࡵࠪᦒ"),
  bstack11ll1_opy_ (u"ࠩ࠰ࡰࡴࡩࡡ࡭ࡲࡵࡳࡽࡿࡰࡢࡵࡶࠫᦓ"): bstack11ll1_opy_ (u"ࠪ࠱ࡱࡵࡣࡢ࡮ࡓࡶࡴࡾࡹࡑࡣࡶࡷࠬᦔ"),
  bstack11ll1_opy_ (u"ࠫࡧ࡯࡮ࡢࡴࡼࡴࡦࡺࡨࠨᦕ"): bstack11ll1_opy_ (u"ࠬࡨࡩ࡯ࡣࡵࡽࡵࡧࡴࡩࠩᦖ"),
  bstack11ll1_opy_ (u"࠭ࡰࡢࡥࡩ࡭ࡱ࡫ࠧᦗ"): bstack11ll1_opy_ (u"ࠧ࠮ࡲࡤࡧ࠲࡬ࡩ࡭ࡧࠪᦘ"),
  bstack11ll1_opy_ (u"ࠨࡲࡤࡧ࠲࡬ࡩ࡭ࡧࠪᦙ"): bstack11ll1_opy_ (u"ࠩ࠰ࡴࡦࡩ࠭ࡧ࡫࡯ࡩࠬᦚ"),
  bstack11ll1_opy_ (u"ࠪ࠱ࡵࡧࡣ࠮ࡨ࡬ࡰࡪ࠭ᦛ"): bstack11ll1_opy_ (u"ࠫ࠲ࡶࡡࡤ࠯ࡩ࡭ࡱ࡫ࠧᦜ"),
  bstack11ll1_opy_ (u"ࠬࡲ࡯ࡨࡨ࡬ࡰࡪ࠭ᦝ"): bstack11ll1_opy_ (u"࠭࡬ࡰࡩࡩ࡭ࡱ࡫ࠧᦞ"),
  bstack11ll1_opy_ (u"ࠧ࡭ࡱࡦࡥࡱ࡯ࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩᦟ"): bstack11ll1_opy_ (u"ࠨ࡮ࡲࡧࡦࡲࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪᦠ"),
  bstack11ll1_opy_ (u"ࠩࡦࡹࡸࡺ࡯࡮࠯ࡵࡩࡵ࡫ࡡࡵࡧࡵࠫᦡ"): bstack11ll1_opy_ (u"ࠪࡧࡺࡹࡴࡰ࡯ࡕࡩࡵ࡫ࡡࡵࡧࡵࠫᦢ")
}
bstack11l1l111l11_opy_ = bstack11ll1_opy_ (u"ࠦ࡭ࡺࡴࡱࡵ࠽࠳࠴࡭ࡩࡵࡪࡸࡦ࠳ࡩ࡯࡮࠱ࡳࡩࡷࡩࡹ࠰ࡥ࡯࡭࠴ࡸࡥ࡭ࡧࡤࡷࡪࡹ࠯࡭ࡣࡷࡩࡸࡺ࠯ࡥࡱࡺࡲࡱࡵࡡࡥࠤᦣ")
bstack11l1l11l1l1_opy_ = bstack11ll1_opy_ (u"ࠧ࠵ࡰࡦࡴࡦࡽ࠴࡮ࡥࡢ࡮ࡷ࡬ࡨ࡮ࡥࡤ࡭ࠥᦤ")
bstack111l1l1ll_opy_ = bstack11ll1_opy_ (u"ࠨࡨࡵࡶࡳࡷ࠿࠵࠯ࡦࡦࡶ࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡧࡴࡳ࠯ࡴࡧࡱࡨࡤࡹࡤ࡬ࡡࡨࡺࡪࡴࡴࡴࠤᦥ")
bstack11l1l11lll_opy_ = bstack11ll1_opy_ (u"ࠧࡩࡶࡷࡴࡸࡀ࠯࠰ࡪࡸࡦ࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡨࡵ࡭࠰ࡹࡧ࠳࡭ࡻࡢࠨᦦ")
bstack111l1ll11_opy_ = bstack11ll1_opy_ (u"ࠨࡪࡷࡸࡵࡀ࠯࠰ࡪࡸࡦ࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡨࡵ࡭࠻࠺࠳࠳ࡼࡪ࠯ࡩࡷࡥࠫᦧ")
bstack1lll1l11l_opy_ = bstack11ll1_opy_ (u"ࠩ࡫ࡸࡹࡶࡳ࠻࠱࠲࡬ࡺࡨ࠮ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡣࡰ࡯࠲ࡲࡪࡾࡴࡠࡪࡸࡦࡸ࠭ᦨ")
bstack11111l1ll_opy_ = {
  bstack11ll1_opy_ (u"ࠪࡨࡪ࡬ࡡࡶ࡮ࡷࠫᦩ"): bstack11ll1_opy_ (u"ࠫ࡭ࡻࡢ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡤࡱࡰࠫᦪ"),
  bstack11ll1_opy_ (u"ࠬࡻࡳ࠮ࡧࡤࡷࡹ࠭ᦫ"): bstack11ll1_opy_ (u"࠭ࡨࡶࡤ࠰ࡹࡸ࡫࠭ࡰࡰ࡯ࡽ࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡨࡵ࡭ࠨ᦬"),
  bstack11ll1_opy_ (u"ࠧࡶࡵࠪ᦭"): bstack11ll1_opy_ (u"ࠨࡪࡸࡦ࠲ࡻࡳ࠮ࡱࡱࡰࡾ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡩ࡯࡮ࠩ᦮"),
  bstack11ll1_opy_ (u"ࠩࡨࡹࠬ᦯"): bstack11ll1_opy_ (u"ࠪ࡬ࡺࡨ࠭ࡦࡷ࠰ࡳࡳࡲࡹ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡤࡱࡰࠫᦰ"),
  bstack11ll1_opy_ (u"ࠫ࡮ࡴࠧᦱ"): bstack11ll1_opy_ (u"ࠬ࡮ࡵࡣ࠯ࡤࡴࡸ࠳࡯࡯࡮ࡼ࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡧࡴࡳࠧᦲ"),
  bstack11ll1_opy_ (u"࠭ࡡࡶࠩᦳ"): bstack11ll1_opy_ (u"ࠧࡩࡷࡥ࠱ࡦࡶࡳࡦ࠯ࡲࡲࡱࡿ࠮ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡣࡰ࡯ࠪᦴ")
}
bstack11l1l11l11l_opy_ = {
  bstack11ll1_opy_ (u"ࠨࡥࡵ࡭ࡹ࡯ࡣࡢ࡮ࠪᦵ"): 50,
  bstack11ll1_opy_ (u"ࠩࡨࡶࡷࡵࡲࠨᦶ"): 40,
  bstack11ll1_opy_ (u"ࠪࡻࡦࡸ࡮ࡪࡰࡪࠫᦷ"): 30,
  bstack11ll1_opy_ (u"ࠫ࡮ࡴࡦࡰࠩᦸ"): 20,
  bstack11ll1_opy_ (u"ࠬࡪࡥࡣࡷࡪࠫᦹ"): 10
}
bstack11l1111l1_opy_ = bstack11l1l11l11l_opy_[bstack11ll1_opy_ (u"࠭ࡩ࡯ࡨࡲࠫᦺ")]
bstack111111l1_opy_ = bstack11ll1_opy_ (u"ࠧࡱࡻࡷ࡬ࡴࡴ࠭ࡱࡻࡷ࡬ࡴࡴࡡࡨࡧࡱࡸ࠴࠭ᦻ")
bstack11l1111lll_opy_ = bstack11ll1_opy_ (u"ࠨࡴࡲࡦࡴࡺ࠭ࡱࡻࡷ࡬ࡴࡴࡡࡨࡧࡱࡸ࠴࠭ᦼ")
bstack1111lll11_opy_ = bstack11ll1_opy_ (u"ࠩࡥࡩ࡭ࡧࡶࡦ࠯ࡳࡽࡹ࡮࡯࡯ࡣࡪࡩࡳࡺ࠯ࠨᦽ")
bstack1l11l1lll1_opy_ = bstack11ll1_opy_ (u"ࠪࡴࡾࡺࡥࡴࡶ࠰ࡴࡾࡺࡨࡰࡰࡤ࡫ࡪࡴࡴ࠰ࠩᦾ")
bstack11lll1l1l1_opy_ = bstack11ll1_opy_ (u"ࠫࡕࡲࡥࡢࡵࡨࠤ࡮ࡴࡳࡵࡣ࡯ࡰࠥࡶࡹࡵࡧࡶࡸࠥࡧ࡮ࡥࠢࡳࡽࡹ࡫ࡳࡵ࠯ࡶࡩࡱ࡫࡮ࡪࡷࡰࠤࡵࡧࡣ࡬ࡣࡪࡩࡸ࠴ࠠࡡࡲ࡬ࡴࠥ࡯࡮ࡴࡶࡤࡰࡱࠦࡰࡺࡶࡨࡷࡹࠦࡰࡺࡶࡨࡷࡹ࠳ࡳࡦ࡮ࡨࡲ࡮ࡻ࡭ࡡࠩᦿ")
bstack111111lll_opy_ = {
  bstack11ll1_opy_ (u"࡙ࠬࡄࡌ࠯ࡊࡉࡓ࠳࠰࠱࠷ࠪᧀ"): bstack11ll1_opy_ (u"࠭ࠪࠫࠬࠣ࡟ࡘࡊࡋ࠮ࡉࡈࡒ࠲࠶࠰࠶࡟ࠣࡤࡵࡿࡴࡦࡵࡷ࠱ࡵࡧࡲࡢ࡮࡯ࡩࡱࡦࠠࡪࡵࠣ࡭ࡳࡹࡴࡢ࡮࡯ࡩࡩࠦࡩ࡯ࠢࡼࡳࡺࡸࠠࡦࡰࡹ࡭ࡷࡵ࡮࡮ࡧࡱࡸ࠳ࠦࡔࡩ࡫ࡶࠤࡲࡧࡹࠡࡥࡤࡹࡸ࡫ࠠࡤࡱࡱࡪࡱ࡯ࡣࡵࡵࠣࡻ࡮ࡺࡨࠡࡄࡵࡳࡼࡹࡥࡳࡕࡷࡥࡨࡱࠠࡔࡆࡎ࠲ࠥࡖ࡬ࡦࡣࡶࡩࠥࡻ࡮ࡪࡰࡶࡸࡦࡲ࡬ࠡ࡫ࡷࠤࡺࡹࡩ࡯ࡩ࠽ࠤࡵ࡯ࡰࠡࡷࡱ࡭ࡳࡹࡴࡢ࡮࡯ࠤࡵࡿࡴࡦࡵࡷ࠱ࡵࡧࡲࡢ࡮࡯ࡩࡱࠦࠪࠫࠬࠪᧁ")
}
bstack11l11lllll1_opy_ = [bstack11ll1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡕࡔࡇࡕࡒࡆࡓࡅࠨᧂ"), bstack11ll1_opy_ (u"ࠨ࡛ࡒ࡙ࡗࡥࡕࡔࡇࡕࡒࡆࡓࡅࠨᧃ")]
bstack11l1l11l1ll_opy_ = [bstack11ll1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡃࡆࡇࡊ࡙ࡓࡠࡍࡈ࡝ࠬᧄ"), bstack11ll1_opy_ (u"ࠪ࡝ࡔ࡛ࡒࡠࡃࡆࡇࡊ࡙ࡓࡠࡍࡈ࡝ࠬᧅ")]
bstack11111111_opy_ = re.compile(bstack11ll1_opy_ (u"ࠫࡣࡡ࡜࡝ࡹ࠰ࡡ࠰ࡀ࠮ࠫࠦࠪᧆ"))
bstack1lllllll11_opy_ = [
  bstack11ll1_opy_ (u"ࠬࡧࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࡐࡤࡱࡪ࠭ᧇ"),
  bstack11ll1_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡗࡧࡵࡷ࡮ࡵ࡮ࠨᧈ"),
  bstack11ll1_opy_ (u"ࠧࡥࡧࡹ࡭ࡨ࡫ࡎࡢ࡯ࡨࠫᧉ"),
  bstack11ll1_opy_ (u"ࠨࡰࡨࡻࡈࡵ࡭࡮ࡣࡱࡨ࡙࡯࡭ࡦࡱࡸࡸࠬ᧊"),
  bstack11ll1_opy_ (u"ࠩࡤࡴࡵ࠭᧋"),
  bstack11ll1_opy_ (u"ࠪࡹࡩ࡯ࡤࠨ᧌"),
  bstack11ll1_opy_ (u"ࠫࡱࡧ࡮ࡨࡷࡤ࡫ࡪ࠭᧍"),
  bstack11ll1_opy_ (u"ࠬࡲ࡯ࡤࡣ࡯ࡩࠬ᧎"),
  bstack11ll1_opy_ (u"࠭࡯ࡳ࡫ࡨࡲࡹࡧࡴࡪࡱࡱࠫ᧏"),
  bstack11ll1_opy_ (u"ࠧࡢࡷࡷࡳ࡜࡫ࡢࡷ࡫ࡨࡻࠬ᧐"),
  bstack11ll1_opy_ (u"ࠨࡰࡲࡖࡪࡹࡥࡵࠩ᧑"), bstack11ll1_opy_ (u"ࠩࡩࡹࡱࡲࡒࡦࡵࡨࡸࠬ᧒"),
  bstack11ll1_opy_ (u"ࠪࡧࡱ࡫ࡡࡳࡕࡼࡷࡹ࡫࡭ࡇ࡫࡯ࡩࡸ࠭᧓"),
  bstack11ll1_opy_ (u"ࠫࡪࡼࡥ࡯ࡶࡗ࡭ࡲ࡯࡮ࡨࡵࠪ᧔"),
  bstack11ll1_opy_ (u"ࠬ࡫࡮ࡢࡤ࡯ࡩࡕ࡫ࡲࡧࡱࡵࡱࡦࡴࡣࡦࡎࡲ࡫࡬࡯࡮ࡨࠩ᧕"),
  bstack11ll1_opy_ (u"࠭࡯ࡵࡪࡨࡶࡆࡶࡰࡴࠩ᧖"),
  bstack11ll1_opy_ (u"ࠧࡱࡴ࡬ࡲࡹࡖࡡࡨࡧࡖࡳࡺࡸࡣࡦࡑࡱࡊ࡮ࡴࡤࡇࡣ࡬ࡰࡺࡸࡥࠨ᧗"),
  bstack11ll1_opy_ (u"ࠨࡣࡳࡴࡆࡩࡴࡪࡸ࡬ࡸࡾ࠭᧘"), bstack11ll1_opy_ (u"ࠩࡤࡴࡵࡖࡡࡤ࡭ࡤ࡫ࡪ࠭᧙"), bstack11ll1_opy_ (u"ࠪࡥࡵࡶࡗࡢ࡫ࡷࡅࡨࡺࡩࡷ࡫ࡷࡽࠬ᧚"), bstack11ll1_opy_ (u"ࠫࡦࡶࡰࡘࡣ࡬ࡸࡕࡧࡣ࡬ࡣࡪࡩࠬ᧛"), bstack11ll1_opy_ (u"ࠬࡧࡰࡱ࡙ࡤ࡭ࡹࡊࡵࡳࡣࡷ࡭ࡴࡴࠧ᧜"),
  bstack11ll1_opy_ (u"࠭ࡤࡦࡸ࡬ࡧࡪࡘࡥࡢࡦࡼࡘ࡮ࡳࡥࡰࡷࡷࠫ᧝"),
  bstack11ll1_opy_ (u"ࠧࡢ࡮࡯ࡳࡼ࡚ࡥࡴࡶࡓࡥࡨࡱࡡࡨࡧࡶࠫ᧞"),
  bstack11ll1_opy_ (u"ࠨࡣࡱࡨࡷࡵࡩࡥࡅࡲࡺࡪࡸࡡࡨࡧࠪ᧟"), bstack11ll1_opy_ (u"ࠩࡤࡲࡩࡸ࡯ࡪࡦࡆࡳࡻ࡫ࡲࡢࡩࡨࡉࡳࡪࡉ࡯ࡶࡨࡲࡹ࠭᧠"),
  bstack11ll1_opy_ (u"ࠪࡥࡳࡪࡲࡰ࡫ࡧࡈࡪࡼࡩࡤࡧࡕࡩࡦࡪࡹࡕ࡫ࡰࡩࡴࡻࡴࠨ᧡"),
  bstack11ll1_opy_ (u"ࠫࡦࡪࡢࡑࡱࡵࡸࠬ᧢"),
  bstack11ll1_opy_ (u"ࠬࡧ࡮ࡥࡴࡲ࡭ࡩࡊࡥࡷ࡫ࡦࡩࡘࡵࡣ࡬ࡧࡷࠫ᧣"),
  bstack11ll1_opy_ (u"࠭ࡡ࡯ࡦࡵࡳ࡮ࡪࡉ࡯ࡵࡷࡥࡱࡲࡔࡪ࡯ࡨࡳࡺࡺࠧ᧤"),
  bstack11ll1_opy_ (u"ࠧࡢࡰࡧࡶࡴ࡯ࡤࡊࡰࡶࡸࡦࡲ࡬ࡑࡣࡷ࡬ࠬ᧥"),
  bstack11ll1_opy_ (u"ࠨࡣࡹࡨࠬ᧦"), bstack11ll1_opy_ (u"ࠩࡤࡺࡩࡒࡡࡶࡰࡦ࡬࡙࡯࡭ࡦࡱࡸࡸࠬ᧧"), bstack11ll1_opy_ (u"ࠪࡥࡻࡪࡒࡦࡣࡧࡽ࡙࡯࡭ࡦࡱࡸࡸࠬ᧨"), bstack11ll1_opy_ (u"ࠫࡦࡼࡤࡂࡴࡪࡷࠬ᧩"),
  bstack11ll1_opy_ (u"ࠬࡻࡳࡦࡍࡨࡽࡸࡺ࡯ࡳࡧࠪ᧪"), bstack11ll1_opy_ (u"࠭࡫ࡦࡻࡶࡸࡴࡸࡥࡑࡣࡷ࡬ࠬ᧫"), bstack11ll1_opy_ (u"ࠧ࡬ࡧࡼࡷࡹࡵࡲࡦࡒࡤࡷࡸࡽ࡯ࡳࡦࠪ᧬"),
  bstack11ll1_opy_ (u"ࠨ࡭ࡨࡽࡆࡲࡩࡢࡵࠪ᧭"), bstack11ll1_opy_ (u"ࠩ࡮ࡩࡾࡖࡡࡴࡵࡺࡳࡷࡪࠧ᧮"),
  bstack11ll1_opy_ (u"ࠪࡧ࡭ࡸ࡯࡮ࡧࡧࡶ࡮ࡼࡥࡳࡇࡻࡩࡨࡻࡴࡢࡤ࡯ࡩࠬ᧯"), bstack11ll1_opy_ (u"ࠫࡨ࡮ࡲࡰ࡯ࡨࡨࡷ࡯ࡶࡦࡴࡄࡶ࡬ࡹࠧ᧰"), bstack11ll1_opy_ (u"ࠬࡩࡨࡳࡱࡰࡩࡩࡸࡩࡷࡧࡵࡉࡽ࡫ࡣࡶࡶࡤࡦࡱ࡫ࡄࡪࡴࠪ᧱"), bstack11ll1_opy_ (u"࠭ࡣࡩࡴࡲࡱࡪࡪࡲࡪࡸࡨࡶࡈ࡮ࡲࡰ࡯ࡨࡑࡦࡶࡰࡪࡰࡪࡊ࡮ࡲࡥࠨ᧲"), bstack11ll1_opy_ (u"ࠧࡤࡪࡵࡳࡲ࡫ࡤࡳ࡫ࡹࡩࡷ࡛ࡳࡦࡕࡼࡷࡹ࡫࡭ࡆࡺࡨࡧࡺࡺࡡࡣ࡮ࡨࠫ᧳"),
  bstack11ll1_opy_ (u"ࠨࡥ࡫ࡶࡴࡳࡥࡥࡴ࡬ࡺࡪࡸࡐࡰࡴࡷࠫ᧴"), bstack11ll1_opy_ (u"ࠩࡦ࡬ࡷࡵ࡭ࡦࡦࡵ࡭ࡻ࡫ࡲࡑࡱࡵࡸࡸ࠭᧵"),
  bstack11ll1_opy_ (u"ࠪࡧ࡭ࡸ࡯࡮ࡧࡧࡶ࡮ࡼࡥࡳࡆ࡬ࡷࡦࡨ࡬ࡦࡄࡸ࡭ࡱࡪࡃࡩࡧࡦ࡯ࠬ᧶"),
  bstack11ll1_opy_ (u"ࠫࡦࡻࡴࡰ࡙ࡨࡦࡻ࡯ࡥࡸࡖ࡬ࡱࡪࡵࡵࡵࠩ᧷"),
  bstack11ll1_opy_ (u"ࠬ࡯࡮ࡵࡧࡱࡸࡆࡩࡴࡪࡱࡱࠫ᧸"), bstack11ll1_opy_ (u"࠭ࡩ࡯ࡶࡨࡲࡹࡉࡡࡵࡧࡪࡳࡷࡿࠧ᧹"), bstack11ll1_opy_ (u"ࠧࡪࡰࡷࡩࡳࡺࡆ࡭ࡣࡪࡷࠬ᧺"), bstack11ll1_opy_ (u"ࠨࡱࡳࡸ࡮ࡵ࡮ࡢ࡮ࡌࡲࡹ࡫࡮ࡵࡃࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠫ᧻"),
  bstack11ll1_opy_ (u"ࠩࡧࡳࡳࡺࡓࡵࡱࡳࡅࡵࡶࡏ࡯ࡔࡨࡷࡪࡺࠧ᧼"),
  bstack11ll1_opy_ (u"ࠪࡹࡳ࡯ࡣࡰࡦࡨࡏࡪࡿࡢࡰࡣࡵࡨࠬ᧽"), bstack11ll1_opy_ (u"ࠫࡷ࡫ࡳࡦࡶࡎࡩࡾࡨ࡯ࡢࡴࡧࠫ᧾"),
  bstack11ll1_opy_ (u"ࠬࡴ࡯ࡔ࡫ࡪࡲࠬ᧿"),
  bstack11ll1_opy_ (u"࠭ࡩࡨࡰࡲࡶࡪ࡛࡮ࡪ࡯ࡳࡳࡷࡺࡡ࡯ࡶ࡙࡭ࡪࡽࡳࠨᨀ"),
  bstack11ll1_opy_ (u"ࠧࡥ࡫ࡶࡥࡧࡲࡥࡂࡰࡧࡶࡴ࡯ࡤࡘࡣࡷࡧ࡭࡫ࡲࡴࠩᨁ"),
  bstack11ll1_opy_ (u"ࠨࡥ࡫ࡶࡴࡳࡥࡐࡲࡷ࡭ࡴࡴࡳࠨᨂ"),
  bstack11ll1_opy_ (u"ࠩࡵࡩࡨࡸࡥࡢࡶࡨࡇ࡭ࡸ࡯࡮ࡧࡇࡶ࡮ࡼࡥࡳࡕࡨࡷࡸ࡯࡯࡯ࡵࠪᨃ"),
  bstack11ll1_opy_ (u"ࠪࡲࡦࡺࡩࡷࡧ࡚ࡩࡧ࡙ࡣࡳࡧࡨࡲࡸ࡮࡯ࡵࠩᨄ"),
  bstack11ll1_opy_ (u"ࠫࡦࡴࡤࡳࡱ࡬ࡨࡘࡩࡲࡦࡧࡱࡷ࡭ࡵࡴࡑࡣࡷ࡬ࠬᨅ"),
  bstack11ll1_opy_ (u"ࠬࡴࡥࡵࡹࡲࡶࡰ࡙ࡰࡦࡧࡧࠫᨆ"),
  bstack11ll1_opy_ (u"࠭ࡧࡱࡵࡈࡲࡦࡨ࡬ࡦࡦࠪᨇ"),
  bstack11ll1_opy_ (u"ࠧࡪࡵࡋࡩࡦࡪ࡬ࡦࡵࡶࠫᨈ"),
  bstack11ll1_opy_ (u"ࠨࡣࡧࡦࡊࡾࡥࡤࡖ࡬ࡱࡪࡵࡵࡵࠩᨉ"),
  bstack11ll1_opy_ (u"ࠩ࡯ࡳࡨࡧ࡬ࡦࡕࡦࡶ࡮ࡶࡴࠨᨊ"),
  bstack11ll1_opy_ (u"ࠪࡷࡰ࡯ࡰࡅࡧࡹ࡭ࡨ࡫ࡉ࡯࡫ࡷ࡭ࡦࡲࡩࡻࡣࡷ࡭ࡴࡴࠧᨋ"),
  bstack11ll1_opy_ (u"ࠫࡦࡻࡴࡰࡉࡵࡥࡳࡺࡐࡦࡴࡰ࡭ࡸࡹࡩࡰࡰࡶࠫᨌ"),
  bstack11ll1_opy_ (u"ࠬࡧ࡮ࡥࡴࡲ࡭ࡩࡔࡡࡵࡷࡵࡥࡱࡕࡲࡪࡧࡱࡸࡦࡺࡩࡰࡰࠪᨍ"),
  bstack11ll1_opy_ (u"࠭ࡳࡺࡵࡷࡩࡲࡖ࡯ࡳࡶࠪᨎ"),
  bstack11ll1_opy_ (u"ࠧࡳࡧࡰࡳࡹ࡫ࡁࡥࡤࡋࡳࡸࡺࠧᨏ"),
  bstack11ll1_opy_ (u"ࠨࡵ࡮࡭ࡵ࡛࡮࡭ࡱࡦ࡯ࠬᨐ"), bstack11ll1_opy_ (u"ࠩࡸࡲࡱࡵࡣ࡬ࡖࡼࡴࡪ࠭ᨑ"), bstack11ll1_opy_ (u"ࠪࡹࡳࡲ࡯ࡤ࡭ࡎࡩࡾ࠭ᨒ"),
  bstack11ll1_opy_ (u"ࠫࡦࡻࡴࡰࡎࡤࡹࡳࡩࡨࠨᨓ"),
  bstack11ll1_opy_ (u"ࠬࡹ࡫ࡪࡲࡏࡳ࡬ࡩࡡࡵࡅࡤࡴࡹࡻࡲࡦࠩᨔ"),
  bstack11ll1_opy_ (u"࠭ࡵ࡯࡫ࡱࡷࡹࡧ࡬࡭ࡑࡷ࡬ࡪࡸࡐࡢࡥ࡮ࡥ࡬࡫ࡳࠨᨕ"),
  bstack11ll1_opy_ (u"ࠧࡥ࡫ࡶࡥࡧࡲࡥࡘ࡫ࡱࡨࡴࡽࡁ࡯࡫ࡰࡥࡹ࡯࡯࡯ࠩᨖ"),
  bstack11ll1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡔࡰࡱ࡯ࡷ࡛࡫ࡲࡴ࡫ࡲࡲࠬᨗ"),
  bstack11ll1_opy_ (u"ࠩࡨࡲ࡫ࡵࡲࡤࡧࡄࡴࡵࡏ࡮ࡴࡶࡤࡰࡱᨘ࠭"),
  bstack11ll1_opy_ (u"ࠪࡩࡳࡹࡵࡳࡧ࡚ࡩࡧࡼࡩࡦࡹࡶࡌࡦࡼࡥࡑࡣࡪࡩࡸ࠭ᨙ"), bstack11ll1_opy_ (u"ࠫࡼ࡫ࡢࡷ࡫ࡨࡻࡉ࡫ࡶࡵࡱࡲࡰࡸࡖ࡯ࡳࡶࠪᨚ"), bstack11ll1_opy_ (u"ࠬ࡫࡮ࡢࡤ࡯ࡩ࡜࡫ࡢࡷ࡫ࡨࡻࡉ࡫ࡴࡢ࡫࡯ࡷࡈࡵ࡬࡭ࡧࡦࡸ࡮ࡵ࡮ࠨᨛ"),
  bstack11ll1_opy_ (u"࠭ࡲࡦ࡯ࡲࡸࡪࡇࡰࡱࡵࡆࡥࡨ࡮ࡥࡍ࡫ࡰ࡭ࡹ࠭᨜"),
  bstack11ll1_opy_ (u"ࠧࡤࡣ࡯ࡩࡳࡪࡡࡳࡈࡲࡶࡲࡧࡴࠨ᨝"),
  bstack11ll1_opy_ (u"ࠨࡤࡸࡲࡩࡲࡥࡊࡦࠪ᨞"),
  bstack11ll1_opy_ (u"ࠩ࡯ࡥࡺࡴࡣࡩࡖ࡬ࡱࡪࡵࡵࡵࠩ᨟"),
  bstack11ll1_opy_ (u"ࠪࡰࡴࡩࡡࡵ࡫ࡲࡲࡘ࡫ࡲࡷ࡫ࡦࡩࡸࡋ࡮ࡢࡤ࡯ࡩࡩ࠭ᨠ"), bstack11ll1_opy_ (u"ࠫࡱࡵࡣࡢࡶ࡬ࡳࡳ࡙ࡥࡳࡸ࡬ࡧࡪࡹࡁࡶࡶ࡫ࡳࡷ࡯ࡺࡦࡦࠪᨡ"),
  bstack11ll1_opy_ (u"ࠬࡧࡵࡵࡱࡄࡧࡨ࡫ࡰࡵࡃ࡯ࡩࡷࡺࡳࠨᨢ"), bstack11ll1_opy_ (u"࠭ࡡࡶࡶࡲࡈ࡮ࡹ࡭ࡪࡵࡶࡅࡱ࡫ࡲࡵࡵࠪᨣ"),
  bstack11ll1_opy_ (u"ࠧ࡯ࡣࡷ࡭ࡻ࡫ࡉ࡯ࡵࡷࡶࡺࡳࡥ࡯ࡶࡶࡐ࡮ࡨࠧᨤ"),
  bstack11ll1_opy_ (u"ࠨࡰࡤࡸ࡮ࡼࡥࡘࡧࡥࡘࡦࡶࠧᨥ"),
  bstack11ll1_opy_ (u"ࠩࡶࡥ࡫ࡧࡲࡪࡋࡱ࡭ࡹ࡯ࡡ࡭ࡗࡵࡰࠬᨦ"), bstack11ll1_opy_ (u"ࠪࡷࡦ࡬ࡡࡳ࡫ࡄࡰࡱࡵࡷࡑࡱࡳࡹࡵࡹࠧᨧ"), bstack11ll1_opy_ (u"ࠫࡸࡧࡦࡢࡴ࡬ࡍ࡬ࡴ࡯ࡳࡧࡉࡶࡦࡻࡤࡘࡣࡵࡲ࡮ࡴࡧࠨᨨ"), bstack11ll1_opy_ (u"ࠬࡹࡡࡧࡣࡵ࡭ࡔࡶࡥ࡯ࡎ࡬ࡲࡰࡹࡉ࡯ࡄࡤࡧࡰ࡭ࡲࡰࡷࡱࡨࠬᨩ"),
  bstack11ll1_opy_ (u"࠭࡫ࡦࡧࡳࡏࡪࡿࡃࡩࡣ࡬ࡲࡸ࠭ᨪ"),
  bstack11ll1_opy_ (u"ࠧ࡭ࡱࡦࡥࡱ࡯ࡺࡢࡤ࡯ࡩࡘࡺࡲࡪࡰࡪࡷࡉ࡯ࡲࠨᨫ"),
  bstack11ll1_opy_ (u"ࠨࡲࡵࡳࡨ࡫ࡳࡴࡃࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠫᨬ"),
  bstack11ll1_opy_ (u"ࠩ࡬ࡲࡹ࡫ࡲࡌࡧࡼࡈࡪࡲࡡࡺࠩᨭ"),
  bstack11ll1_opy_ (u"ࠪࡷ࡭ࡵࡷࡊࡑࡖࡐࡴ࡭ࠧᨮ"),
  bstack11ll1_opy_ (u"ࠫࡸ࡫࡮ࡥࡍࡨࡽࡘࡺࡲࡢࡶࡨ࡫ࡾ࠭ᨯ"),
  bstack11ll1_opy_ (u"ࠬࡽࡥࡣ࡭࡬ࡸࡗ࡫ࡳࡱࡱࡱࡷࡪ࡚ࡩ࡮ࡧࡲࡹࡹ࠭ᨰ"), bstack11ll1_opy_ (u"࠭ࡳࡤࡴࡨࡩࡳࡹࡨࡰࡶ࡚ࡥ࡮ࡺࡔࡪ࡯ࡨࡳࡺࡺࠧᨱ"),
  bstack11ll1_opy_ (u"ࠧࡳࡧࡰࡳࡹ࡫ࡄࡦࡤࡸ࡫ࡕࡸ࡯ࡹࡻࠪᨲ"),
  bstack11ll1_opy_ (u"ࠨࡧࡱࡥࡧࡲࡥࡂࡵࡼࡲࡨࡋࡸࡦࡥࡸࡸࡪࡌࡲࡰ࡯ࡋࡸࡹࡶࡳࠨᨳ"),
  bstack11ll1_opy_ (u"ࠩࡶ࡯࡮ࡶࡌࡰࡩࡆࡥࡵࡺࡵࡳࡧࠪᨴ"),
  bstack11ll1_opy_ (u"ࠪࡻࡪࡨ࡫ࡪࡶࡇࡩࡧࡻࡧࡑࡴࡲࡼࡾࡖ࡯ࡳࡶࠪᨵ"),
  bstack11ll1_opy_ (u"ࠫ࡫ࡻ࡬࡭ࡅࡲࡲࡹ࡫ࡸࡵࡎ࡬ࡷࡹ࠭ᨶ"),
  bstack11ll1_opy_ (u"ࠬࡽࡡࡪࡶࡉࡳࡷࡇࡰࡱࡕࡦࡶ࡮ࡶࡴࠨᨷ"),
  bstack11ll1_opy_ (u"࠭ࡷࡦࡤࡹ࡭ࡪࡽࡃࡰࡰࡱࡩࡨࡺࡒࡦࡶࡵ࡭ࡪࡹࠧᨸ"),
  bstack11ll1_opy_ (u"ࠧࡢࡲࡳࡒࡦࡳࡥࠨᨹ"),
  bstack11ll1_opy_ (u"ࠨࡥࡸࡷࡹࡵ࡭ࡔࡕࡏࡇࡪࡸࡴࠨᨺ"),
  bstack11ll1_opy_ (u"ࠩࡷࡥࡵ࡝ࡩࡵࡪࡖ࡬ࡴࡸࡴࡑࡴࡨࡷࡸࡊࡵࡳࡣࡷ࡭ࡴࡴࠧᨻ"),
  bstack11ll1_opy_ (u"ࠪࡷࡨࡧ࡬ࡦࡈࡤࡧࡹࡵࡲࠨᨼ"),
  bstack11ll1_opy_ (u"ࠫࡼࡪࡡࡍࡱࡦࡥࡱࡖ࡯ࡳࡶࠪᨽ"),
  bstack11ll1_opy_ (u"ࠬࡹࡨࡰࡹ࡛ࡧࡴࡪࡥࡍࡱࡪࠫᨾ"),
  bstack11ll1_opy_ (u"࠭ࡩࡰࡵࡌࡲࡸࡺࡡ࡭࡮ࡓࡥࡺࡹࡥࠨᨿ"),
  bstack11ll1_opy_ (u"ࠧࡹࡥࡲࡨࡪࡉ࡯࡯ࡨ࡬࡫ࡋ࡯࡬ࡦࠩᩀ"),
  bstack11ll1_opy_ (u"ࠨ࡭ࡨࡽࡨ࡮ࡡࡪࡰࡓࡥࡸࡹࡷࡰࡴࡧࠫᩁ"),
  bstack11ll1_opy_ (u"ࠩࡸࡷࡪࡖࡲࡦࡤࡸ࡭ࡱࡺࡗࡅࡃࠪᩂ"),
  bstack11ll1_opy_ (u"ࠪࡴࡷ࡫ࡶࡦࡰࡷ࡛ࡉࡇࡁࡵࡶࡤࡧ࡭ࡳࡥ࡯ࡶࡶࠫᩃ"),
  bstack11ll1_opy_ (u"ࠫࡼ࡫ࡢࡅࡴ࡬ࡺࡪࡸࡁࡨࡧࡱࡸ࡚ࡸ࡬ࠨᩄ"),
  bstack11ll1_opy_ (u"ࠬࡱࡥࡺࡥ࡫ࡥ࡮ࡴࡐࡢࡶ࡫ࠫᩅ"),
  bstack11ll1_opy_ (u"࠭ࡵࡴࡧࡑࡩࡼ࡝ࡄࡂࠩᩆ"),
  bstack11ll1_opy_ (u"ࠧࡸࡦࡤࡐࡦࡻ࡮ࡤࡪࡗ࡭ࡲ࡫࡯ࡶࡶࠪᩇ"), bstack11ll1_opy_ (u"ࠨࡹࡧࡥࡈࡵ࡮࡯ࡧࡦࡸ࡮ࡵ࡮ࡕ࡫ࡰࡩࡴࡻࡴࠨᩈ"),
  bstack11ll1_opy_ (u"ࠩࡻࡧࡴࡪࡥࡐࡴࡪࡍࡩ࠭ᩉ"), bstack11ll1_opy_ (u"ࠪࡼࡨࡵࡤࡦࡕ࡬࡫ࡳ࡯࡮ࡨࡋࡧࠫᩊ"),
  bstack11ll1_opy_ (u"ࠫࡺࡶࡤࡢࡶࡨࡨ࡜ࡊࡁࡃࡷࡱࡨࡱ࡫ࡉࡥࠩᩋ"),
  bstack11ll1_opy_ (u"ࠬࡸࡥࡴࡧࡷࡓࡳ࡙ࡥࡴࡵ࡬ࡳࡳ࡙ࡴࡢࡴࡷࡓࡳࡲࡹࠨᩌ"),
  bstack11ll1_opy_ (u"࠭ࡣࡰ࡯ࡰࡥࡳࡪࡔࡪ࡯ࡨࡳࡺࡺࡳࠨᩍ"),
  bstack11ll1_opy_ (u"ࠧࡸࡦࡤࡗࡹࡧࡲࡵࡷࡳࡖࡪࡺࡲࡪࡧࡶࠫᩎ"), bstack11ll1_opy_ (u"ࠨࡹࡧࡥࡘࡺࡡࡳࡶࡸࡴࡗ࡫ࡴࡳࡻࡌࡲࡹ࡫ࡲࡷࡣ࡯ࠫᩏ"),
  bstack11ll1_opy_ (u"ࠩࡦࡳࡳࡴࡥࡤࡶࡋࡥࡷࡪࡷࡢࡴࡨࡏࡪࡿࡢࡰࡣࡵࡨࠬᩐ"),
  bstack11ll1_opy_ (u"ࠪࡱࡦࡾࡔࡺࡲ࡬ࡲ࡬ࡌࡲࡦࡳࡸࡩࡳࡩࡹࠨᩑ"),
  bstack11ll1_opy_ (u"ࠫࡸ࡯࡭ࡱ࡮ࡨࡍࡸ࡜ࡩࡴ࡫ࡥࡰࡪࡉࡨࡦࡥ࡮ࠫᩒ"),
  bstack11ll1_opy_ (u"ࠬࡻࡳࡦࡅࡤࡶࡹ࡮ࡡࡨࡧࡖࡷࡱ࠭ᩓ"),
  bstack11ll1_opy_ (u"࠭ࡳࡩࡱࡸࡰࡩ࡛ࡳࡦࡕ࡬ࡲ࡬ࡲࡥࡵࡱࡱࡘࡪࡹࡴࡎࡣࡱࡥ࡬࡫ࡲࠨᩔ"),
  bstack11ll1_opy_ (u"ࠧࡴࡶࡤࡶࡹࡏࡗࡅࡒࠪᩕ"),
  bstack11ll1_opy_ (u"ࠨࡣ࡯ࡰࡴࡽࡔࡰࡷࡦ࡬ࡎࡪࡅ࡯ࡴࡲࡰࡱ࠭ᩖ"),
  bstack11ll1_opy_ (u"ࠩ࡬࡫ࡳࡵࡲࡦࡊ࡬ࡨࡩ࡫࡮ࡂࡲ࡬ࡔࡴࡲࡩࡤࡻࡈࡶࡷࡵࡲࠨᩗ"),
  bstack11ll1_opy_ (u"ࠪࡱࡴࡩ࡫ࡍࡱࡦࡥࡹ࡯࡯࡯ࡃࡳࡴࠬᩘ"),
  bstack11ll1_opy_ (u"ࠫࡱࡵࡧࡤࡣࡷࡊࡴࡸ࡭ࡢࡶࠪᩙ"), bstack11ll1_opy_ (u"ࠬࡲ࡯ࡨࡥࡤࡸࡋ࡯࡬ࡵࡧࡵࡗࡵ࡫ࡣࡴࠩᩚ"),
  bstack11ll1_opy_ (u"࠭ࡡ࡭࡮ࡲࡻࡉ࡫࡬ࡢࡻࡄࡨࡧ࠭ᩛ"),
  bstack11ll1_opy_ (u"ࠧࡥ࡫ࡶࡥࡧࡲࡥࡊࡦࡏࡳࡨࡧࡴࡰࡴࡄࡹࡹࡵࡣࡰ࡯ࡳࡰࡪࡺࡩࡰࡰࠪᩜ")
]
bstack1l1lll1ll1_opy_ = bstack11ll1_opy_ (u"ࠨࡪࡷࡸࡵࡹ࠺࠰࠱ࡤࡴ࡮࠳ࡣ࡭ࡱࡸࡨ࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡨࡵ࡭࠰ࡣࡳࡴ࠲ࡧࡵࡵࡱࡰࡥࡹ࡫࠯ࡶࡲ࡯ࡳࡦࡪࠧᩝ")
bstack1lll1l11_opy_ = [bstack11ll1_opy_ (u"ࠩ࠱ࡥࡵࡱࠧᩞ"), bstack11ll1_opy_ (u"ࠪ࠲ࡦࡧࡢࠨ᩟"), bstack11ll1_opy_ (u"ࠫ࠳࡯ࡰࡢ᩠ࠩ")]
bstack111l1111_opy_ = [bstack11ll1_opy_ (u"ࠬ࡯ࡤࠨᩡ"), bstack11ll1_opy_ (u"࠭ࡰࡢࡶ࡫ࠫᩢ"), bstack11ll1_opy_ (u"ࠧࡤࡷࡶࡸࡴࡳ࡟ࡪࡦࠪᩣ"), bstack11ll1_opy_ (u"ࠨࡵ࡫ࡥࡷ࡫ࡡࡣ࡮ࡨࡣ࡮ࡪࠧᩤ")]
bstack1l1lll11l1_opy_ = {
  bstack11ll1_opy_ (u"ࠩࡦ࡬ࡷࡵ࡭ࡦࡑࡳࡸ࡮ࡵ࡮ࡴࠩᩥ"): bstack11ll1_opy_ (u"ࠪ࡫ࡴࡵࡧ࠻ࡥ࡫ࡶࡴࡳࡥࡐࡲࡷ࡭ࡴࡴࡳࠨᩦ"),
  bstack11ll1_opy_ (u"ࠫ࡫࡯ࡲࡦࡨࡲࡼࡔࡶࡴࡪࡱࡱࡷࠬᩧ"): bstack11ll1_opy_ (u"ࠬࡳ࡯ࡻ࠼ࡩ࡭ࡷ࡫ࡦࡰࡺࡒࡴࡹ࡯࡯࡯ࡵࠪᩨ"),
  bstack11ll1_opy_ (u"࠭ࡥࡥࡩࡨࡓࡵࡺࡩࡰࡰࡶࠫᩩ"): bstack11ll1_opy_ (u"ࠧ࡮ࡵ࠽ࡩࡩ࡭ࡥࡐࡲࡷ࡭ࡴࡴࡳࠨᩪ"),
  bstack11ll1_opy_ (u"ࠨ࡫ࡨࡓࡵࡺࡩࡰࡰࡶࠫᩫ"): bstack11ll1_opy_ (u"ࠩࡶࡩ࠿࡯ࡥࡐࡲࡷ࡭ࡴࡴࡳࠨᩬ"),
  bstack11ll1_opy_ (u"ࠪࡷࡦ࡬ࡡࡳ࡫ࡒࡴࡹ࡯࡯࡯ࡵࠪᩭ"): bstack11ll1_opy_ (u"ࠫࡸࡧࡦࡢࡴ࡬࠲ࡴࡶࡴࡪࡱࡱࡷࠬᩮ")
}
bstack1l11l1111_opy_ = [
  bstack11ll1_opy_ (u"ࠬ࡭࡯ࡰࡩ࠽ࡧ࡭ࡸ࡯࡮ࡧࡒࡴࡹ࡯࡯࡯ࡵࠪᩯ"),
  bstack11ll1_opy_ (u"࠭࡭ࡰࡼ࠽ࡪ࡮ࡸࡥࡧࡱࡻࡓࡵࡺࡩࡰࡰࡶࠫᩰ"),
  bstack11ll1_opy_ (u"ࠧ࡮ࡵ࠽ࡩࡩ࡭ࡥࡐࡲࡷ࡭ࡴࡴࡳࠨᩱ"),
  bstack11ll1_opy_ (u"ࠨࡵࡨ࠾࡮࡫ࡏࡱࡶ࡬ࡳࡳࡹࠧᩲ"),
  bstack11ll1_opy_ (u"ࠩࡶࡥ࡫ࡧࡲࡪ࠰ࡲࡴࡹ࡯࡯࡯ࡵࠪᩳ"),
]
bstack1l111111l_opy_ = bstack1llll11111_opy_ + bstack11l1l11llll_opy_ + bstack1lllllll11_opy_
bstack11llll1ll1_opy_ = [
  bstack11ll1_opy_ (u"ࠪࡢࡱࡵࡣࡢ࡮࡫ࡳࡸࡺࠤࠨᩴ"),
  bstack11ll1_opy_ (u"ࠫࡣࡨࡳ࠮࡮ࡲࡧࡦࡲ࠮ࡤࡱࡰࠨࠬ᩵"),
  bstack11ll1_opy_ (u"ࠬࡤ࠱࠳࠹࠱ࠫ᩶"),
  bstack11ll1_opy_ (u"࠭࡞࠲࠲࠱ࠫ᩷"),
  bstack11ll1_opy_ (u"ࠧ࡟࠳࠺࠶࠳࠷࡛࠷࠯࠼ࡡ࠳࠭᩸"),
  bstack11ll1_opy_ (u"ࠨࡠ࠴࠻࠷࠴࠲࡜࠲࠰࠽ࡢ࠴ࠧ᩹"),
  bstack11ll1_opy_ (u"ࠩࡡ࠵࠼࠸࠮࠴࡝࠳࠱࠶ࡣ࠮ࠨ᩺"),
  bstack11ll1_opy_ (u"ࠪࡢ࠶࠿࠲࠯࠳࠹࠼࠳࠭᩻")
]
bstack11l1ll1ll11_opy_ = bstack11ll1_opy_ (u"ࠫ࡭ࡺࡴࡱࡵ࠽࠳࠴ࡧࡰࡪ࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡥࡲࡱࠬ᩼")
bstack1lllllll1_opy_ = bstack11ll1_opy_ (u"ࠬࡹࡤ࡬࠱ࡹ࠵࠴࡫ࡶࡦࡰࡷࠫ᩽")
bstack1ll11llll_opy_ = [ bstack11ll1_opy_ (u"࠭ࡡࡶࡶࡲࡱࡦࡺࡥࠨ᩾") ]
bstack111lll1l11_opy_ = [ bstack11ll1_opy_ (u"ࠧࡢࡲࡳ࠱ࡦࡻࡴࡰ࡯ࡤࡸࡪ᩿࠭") ]
bstack11lllll1l1_opy_ = [bstack11ll1_opy_ (u"ࠨࡶࡸࡶࡧࡵࡓࡤࡣ࡯ࡩࠬ᪀")]
bstack111111l11_opy_ = [ bstack11ll1_opy_ (u"ࠩࡲࡦࡸ࡫ࡲࡷࡣࡥ࡭ࡱ࡯ࡴࡺࠩ᪁") ]
bstack1lll1ll1l_opy_ = bstack11ll1_opy_ (u"ࠪࡗࡉࡑࡓࡦࡶࡸࡴࠬ᪂")
bstack11l111ll1_opy_ = bstack11ll1_opy_ (u"ࠫࡘࡊࡋࡕࡧࡶࡸࡆࡺࡴࡦ࡯ࡳࡸࡪࡪࠧ᪃")
bstack1l11ll1l_opy_ = bstack11ll1_opy_ (u"࡙ࠬࡄࡌࡖࡨࡷࡹ࡙ࡵࡤࡥࡨࡷࡸ࡬ࡵ࡭ࠩ᪄")
bstack1llll1ll11_opy_ = bstack11ll1_opy_ (u"࠭࠴࠯࠲࠱࠴ࠬ᪅")
bstack1ll11l11l_opy_ = [
  bstack11ll1_opy_ (u"ࠧࡆࡔࡕࡣࡋࡇࡉࡍࡇࡇࠫ᪆"),
  bstack11ll1_opy_ (u"ࠨࡇࡕࡖࡤ࡚ࡉࡎࡇࡇࡣࡔ࡛ࡔࠨ᪇"),
  bstack11ll1_opy_ (u"ࠩࡈࡖࡗࡥࡂࡍࡑࡆࡏࡊࡊ࡟ࡃ࡛ࡢࡇࡑࡏࡅࡏࡖࠪ᪈"),
  bstack11ll1_opy_ (u"ࠪࡉࡗࡘ࡟ࡏࡇࡗ࡛ࡔࡘࡋࡠࡅࡋࡅࡓࡍࡅࡅࠩ᪉"),
  bstack11ll1_opy_ (u"ࠫࡊࡘࡒࡠࡕࡒࡇࡐࡋࡔࡠࡐࡒࡘࡤࡉࡏࡏࡐࡈࡇ࡙ࡋࡄࠨ᪊"),
  bstack11ll1_opy_ (u"ࠬࡋࡒࡓࡡࡆࡓࡓࡔࡅࡄࡖࡌࡓࡓࡥࡃࡍࡑࡖࡉࡉ࠭᪋"),
  bstack11ll1_opy_ (u"࠭ࡅࡓࡔࡢࡇࡔࡔࡎࡆࡅࡗࡍࡔࡔ࡟ࡓࡇࡖࡉ࡙࠭᪌"),
  bstack11ll1_opy_ (u"ࠧࡆࡔࡕࡣࡈࡕࡎࡏࡇࡆࡘࡎࡕࡎࡠࡔࡈࡊ࡚࡙ࡅࡅࠩ᪍"),
  bstack11ll1_opy_ (u"ࠨࡇࡕࡖࡤࡉࡏࡏࡐࡈࡇ࡙ࡏࡏࡏࡡࡄࡆࡔࡘࡔࡆࡆࠪ᪎"),
  bstack11ll1_opy_ (u"ࠩࡈࡖࡗࡥࡃࡐࡐࡑࡉࡈ࡚ࡉࡐࡐࡢࡊࡆࡏࡌࡆࡆࠪ᪏"),
  bstack11ll1_opy_ (u"ࠪࡉࡗࡘ࡟ࡏࡃࡐࡉࡤࡔࡏࡕࡡࡕࡉࡘࡕࡌࡗࡇࡇࠫ᪐"),
  bstack11ll1_opy_ (u"ࠫࡊࡘࡒࡠࡃࡇࡈࡗࡋࡓࡔࡡࡌࡒ࡛ࡇࡌࡊࡆࠪ᪑"),
  bstack11ll1_opy_ (u"ࠬࡋࡒࡓࡡࡄࡈࡉࡘࡅࡔࡕࡢ࡙ࡓࡘࡅࡂࡅࡋࡅࡇࡒࡅࠨ᪒"),
  bstack11ll1_opy_ (u"࠭ࡅࡓࡔࡢࡘ࡚ࡔࡎࡆࡎࡢࡇࡔࡔࡎࡆࡅࡗࡍࡔࡔ࡟ࡇࡃࡌࡐࡊࡊࠧ᪓"),
  bstack11ll1_opy_ (u"ࠧࡆࡔࡕࡣࡈࡕࡎࡏࡇࡆࡘࡎࡕࡎࡠࡖࡌࡑࡊࡊ࡟ࡐࡗࡗࠫ᪔"),
  bstack11ll1_opy_ (u"ࠨࡇࡕࡖࡤ࡙ࡏࡄࡍࡖࡣࡈࡕࡎࡏࡇࡆࡘࡎࡕࡎࡠࡈࡄࡍࡑࡋࡄࠨ᪕"),
  bstack11ll1_opy_ (u"ࠩࡈࡖࡗࡥࡓࡐࡅࡎࡗࡤࡉࡏࡏࡐࡈࡇ࡙ࡏࡏࡏࡡࡋࡓࡘ࡚࡟ࡖࡐࡕࡉࡆࡉࡈࡂࡄࡏࡉࠬ᪖"),
  bstack11ll1_opy_ (u"ࠪࡉࡗࡘ࡟ࡑࡔࡒ࡜࡞ࡥࡃࡐࡐࡑࡉࡈ࡚ࡉࡐࡐࡢࡊࡆࡏࡌࡆࡆࠪ᪗"),
  bstack11ll1_opy_ (u"ࠫࡊࡘࡒࡠࡐࡄࡑࡊࡥࡎࡐࡖࡢࡖࡊ࡙ࡏࡍࡘࡈࡈࠬ᪘"),
  bstack11ll1_opy_ (u"ࠬࡋࡒࡓࡡࡑࡅࡒࡋ࡟ࡓࡇࡖࡓࡑ࡛ࡔࡊࡑࡑࡣࡋࡇࡉࡍࡇࡇࠫ᪙"),
  bstack11ll1_opy_ (u"࠭ࡅࡓࡔࡢࡑࡆࡔࡄࡂࡖࡒࡖ࡞ࡥࡐࡓࡑ࡛࡝ࡤࡉࡏࡏࡈࡌࡋ࡚ࡘࡁࡕࡋࡒࡒࡤࡌࡁࡊࡎࡈࡈࠬ᪚"),
]
bstack1l11l1l11_opy_ = bstack11ll1_opy_ (u"ࠧ࠯࠱ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠮ࡣࡵࡸ࡮࡬ࡡࡤࡶࡶ࠳ࠬ᪛")
bstack1ll11l1l1_opy_ = os.path.join(os.path.expanduser(bstack11ll1_opy_ (u"ࠨࢀࠪ᪜")), bstack11ll1_opy_ (u"ࠩ࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࠩ᪝"), bstack11ll1_opy_ (u"ࠪ࠲ࡧࡹࡴࡢࡥ࡮࠱ࡨࡵ࡮ࡧ࡫ࡪ࠲࡯ࡹ࡯࡯ࠩ᪞"))
bstack11ll11lll1l_opy_ = bstack11ll1_opy_ (u"ࠫ࡭ࡺࡴࡱࡵ࠽࠳࠴ࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽ࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡨࡵ࡭࠰ࡣࡳ࡭ࠬ᪟")
bstack11l1l111lll_opy_ = [ bstack11ll1_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸࠬ᪠"), bstack11ll1_opy_ (u"࠭ࡲࡰࡤࡲࡸࠬ᪡"), bstack11ll1_opy_ (u"ࠧࡱࡣࡥࡳࡹ࠭᪢"), bstack11ll1_opy_ (u"ࠨࡤࡨ࡬ࡦࡼࡥࠨ᪣")]
bstack11lllllll1_opy_ = [ bstack11ll1_opy_ (u"ࠩࡳࡽࡹ࡫ࡳࡵࠩ᪤"), bstack11ll1_opy_ (u"ࠪࡶࡴࡨ࡯ࡵࠩ᪥"), bstack11ll1_opy_ (u"ࠫࡵࡧࡢࡰࡶࠪ᪦"), bstack11ll1_opy_ (u"ࠬࡨࡥࡩࡣࡹࡩࠬᪧ") ]
bstack11ll1lll1_opy_ = [ bstack11ll1_opy_ (u"࠭ࡲࡰࡤࡲࡸࠬ᪨") ]
bstack11l1l1111l1_opy_ = [ bstack11ll1_opy_ (u"ࠧࡱࡻࡷࡩࡸࡺࠧ᪩") ]
bstack1ll1l1ll1l_opy_ = 360
bstack11l1ll1l1ll_opy_ = bstack11ll1_opy_ (u"ࠣࡣࡳࡴ࠲ࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽ࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡨࡵ࡭ࠣ᪪")
bstack11l1l1111ll_opy_ = bstack11ll1_opy_ (u"ࠤࡤࡹࡹࡵ࡭ࡢࡶࡨ࠳ࡦࡶࡩ࠰ࡸ࠴࠳࡮ࡹࡳࡶࡧࡶࠦ᪫")
bstack11l1l11ll1l_opy_ = bstack11ll1_opy_ (u"ࠥࡥࡺࡺ࡯࡮ࡣࡷࡩ࠴ࡧࡰࡪ࠱ࡹ࠵࠴࡯ࡳࡴࡷࡨࡷ࠲ࡹࡵ࡮࡯ࡤࡶࡾࠨ᪬")
bstack11ll111l11l_opy_ = bstack11ll1_opy_ (u"ࠦࡆࡶࡰࠡࡃࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠡࡃࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࠥࡺࡥࡴࡶࡶࠤࡦࡸࡥࠡࡵࡸࡴࡵࡵࡲࡵࡧࡧࠤࡴࡴࠠࡐࡕࠣࡺࡪࡸࡳࡪࡱࡱࠤࠪࡹࠠࡢࡰࡧࠤࡦࡨ࡯ࡷࡧࠣࡪࡴࡸࠠࡂࡰࡧࡶࡴ࡯ࡤࠡࡦࡨࡺ࡮ࡩࡥࡴ࠰ࠥ᪭")
bstack11l1lllll1l_opy_ = bstack11ll1_opy_ (u"ࠧ࠷࠱࠯࠲ࠥ᪮")
bstack111l11ll11_opy_ = {
  bstack11ll1_opy_ (u"࠭ࡐࡂࡕࡖࠫ᪯"): bstack11ll1_opy_ (u"ࠧࡱࡣࡶࡷࡪࡪࠧ᪰"),
  bstack11ll1_opy_ (u"ࠨࡈࡄࡍࡑ࠭᪱"): bstack11ll1_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࠩ᪲"),
  bstack11ll1_opy_ (u"ࠪࡗࡐࡏࡐࠨ᪳"): bstack11ll1_opy_ (u"ࠫࡸࡱࡩࡱࡲࡨࡨࠬ᪴")
}
bstack111l11ll_opy_ = [
  bstack11ll1_opy_ (u"ࠧ࡭ࡥࡵࠤ᪵"),
  bstack11ll1_opy_ (u"ࠨࡧࡰࡄࡤࡧࡰࠨ᪶"),
  bstack11ll1_opy_ (u"ࠢࡨࡱࡉࡳࡷࡽࡡࡳࡦ᪷ࠥ"),
  bstack11ll1_opy_ (u"ࠣࡴࡨࡪࡷ࡫ࡳࡩࠤ᪸"),
  bstack11ll1_opy_ (u"ࠤࡦࡰ࡮ࡩ࡫ࡆ࡮ࡨࡱࡪࡴࡴ᪹ࠣ"),
  bstack11ll1_opy_ (u"ࠥࡷࡨࡸࡥࡦࡰࡶ࡬ࡴࡺ᪺ࠢ"),
  bstack11ll1_opy_ (u"ࠦࡸࡻࡢ࡮࡫ࡷࡉࡱ࡫࡭ࡦࡰࡷࠦ᪻"),
  bstack11ll1_opy_ (u"ࠧࡹࡥ࡯ࡦࡎࡩࡾࡹࡔࡰࡇ࡯ࡩࡲ࡫࡮ࡵࠤ᪼"),
  bstack11ll1_opy_ (u"ࠨࡳࡦࡰࡧࡏࡪࡿࡳࡕࡱࡄࡧࡹ࡯ࡶࡦࡇ࡯ࡩࡲ࡫࡮ࡵࠤ᪽"),
  bstack11ll1_opy_ (u"ࠢࡤ࡮ࡨࡥࡷࡋ࡬ࡦ࡯ࡨࡲࡹࠨ᪾"),
  bstack11ll1_opy_ (u"ࠣࡣࡦࡸ࡮ࡵ࡮ࡴࠤᪿ"),
  bstack11ll1_opy_ (u"ࠤࡨࡼࡪࡩࡵࡵࡧࡖࡧࡷ࡯ࡰࡵࠤᫀ"),
  bstack11ll1_opy_ (u"ࠥࡩࡽ࡫ࡣࡶࡶࡨࡅࡸࡿ࡮ࡤࡕࡦࡶ࡮ࡶࡴࠣ᫁"),
  bstack11ll1_opy_ (u"ࠦࡨࡲ࡯ࡴࡧࠥ᫂"),
  bstack11ll1_opy_ (u"ࠧࡷࡵࡪࡶ᫃ࠥ"),
  bstack11ll1_opy_ (u"ࠨࡰࡦࡴࡩࡳࡷࡳࡔࡰࡷࡦ࡬ࡆࡩࡴࡪࡱࡱ᫄ࠦ"),
  bstack11ll1_opy_ (u"ࠢࡱࡧࡵࡪࡴࡸ࡭ࡎࡷ࡯ࡸ࡮࡚࡯ࡶࡥ࡫ࠦ᫅"),
  bstack11ll1_opy_ (u"ࠣࡵ࡫ࡥࡰ࡫ࠢ᫆"),
  bstack11ll1_opy_ (u"ࠤࡦࡰࡴࡹࡥࡂࡲࡳࠦ᫇")
]
bstack11l1l1l1l11_opy_ = [
  bstack11ll1_opy_ (u"ࠥࡧࡱ࡯ࡣ࡬ࠤ᫈"),
  bstack11ll1_opy_ (u"ࠦࡸࡩࡲࡦࡧࡱࡷ࡭ࡵࡴࠣ᫉"),
  bstack11ll1_opy_ (u"ࠧࡧࡵࡵࡱ᫊ࠥ"),
  bstack11ll1_opy_ (u"ࠨ࡭ࡢࡰࡸࡥࡱࠨ᫋"),
  bstack11ll1_opy_ (u"ࠢࡵࡧࡶࡸࡨࡧࡳࡦࠤᫌ")
]
bstack1ll111lll_opy_ = {
  bstack11ll1_opy_ (u"ࠣࡥ࡯࡭ࡨࡱࠢᫍ"): [bstack11ll1_opy_ (u"ࠤࡦࡰ࡮ࡩ࡫ࡆ࡮ࡨࡱࡪࡴࡴࠣᫎ")],
  bstack11ll1_opy_ (u"ࠥࡷࡨࡸࡥࡦࡰࡶ࡬ࡴࡺࠢ᫏"): [bstack11ll1_opy_ (u"ࠦࡸࡩࡲࡦࡧࡱࡷ࡭ࡵࡴࠣ᫐")],
  bstack11ll1_opy_ (u"ࠧࡧࡵࡵࡱࠥ᫑"): [bstack11ll1_opy_ (u"ࠨࡳࡦࡰࡧࡏࡪࡿࡳࡕࡱࡈࡰࡪࡳࡥ࡯ࡶࠥ᫒"), bstack11ll1_opy_ (u"ࠢࡴࡧࡱࡨࡐ࡫ࡹࡴࡖࡲࡅࡨࡺࡩࡷࡧࡈࡰࡪࡳࡥ࡯ࡶࠥ᫓"), bstack11ll1_opy_ (u"ࠣࡵࡦࡶࡪ࡫࡮ࡴࡪࡲࡸࠧ᫔"), bstack11ll1_opy_ (u"ࠤࡦࡰ࡮ࡩ࡫ࡆ࡮ࡨࡱࡪࡴࡴࠣ᫕")],
  bstack11ll1_opy_ (u"ࠥࡱࡦࡴࡵࡢ࡮ࠥ᫖"): [bstack11ll1_opy_ (u"ࠦࡲࡧ࡮ࡶࡣ࡯ࠦ᫗")],
  bstack11ll1_opy_ (u"ࠧࡺࡥࡴࡶࡦࡥࡸ࡫ࠢ᫘"): [bstack11ll1_opy_ (u"ࠨࡴࡦࡵࡷࡧࡦࡹࡥࠣ᫙")],
}
bstack11l1l1l1111_opy_ = {
  bstack11ll1_opy_ (u"ࠢࡤ࡮࡬ࡧࡰࡋ࡬ࡦ࡯ࡨࡲࡹࠨ᫚"): bstack11ll1_opy_ (u"ࠣࡥ࡯࡭ࡨࡱࠢ᫛"),
  bstack11ll1_opy_ (u"ࠤࡶࡧࡷ࡫ࡥ࡯ࡵ࡫ࡳࡹࠨ᫜"): bstack11ll1_opy_ (u"ࠥࡷࡨࡸࡥࡦࡰࡶ࡬ࡴࡺࠢ᫝"),
  bstack11ll1_opy_ (u"ࠦࡸ࡫࡮ࡥࡍࡨࡽࡸ࡚࡯ࡆ࡮ࡨࡱࡪࡴࡴࠣ᫞"): bstack11ll1_opy_ (u"ࠧࡹࡥ࡯ࡦࡎࡩࡾࡹࠢ᫟"),
  bstack11ll1_opy_ (u"ࠨࡳࡦࡰࡧࡏࡪࡿࡳࡕࡱࡄࡧࡹ࡯ࡶࡦࡇ࡯ࡩࡲ࡫࡮ࡵࠤ᫠"): bstack11ll1_opy_ (u"ࠢࡴࡧࡱࡨࡐ࡫ࡹࡴࠤ᫡"),
  bstack11ll1_opy_ (u"ࠣࡶࡨࡷࡹࡩࡡࡴࡧࠥ᫢"): bstack11ll1_opy_ (u"ࠤࡷࡩࡸࡺࡣࡢࡵࡨࠦ᫣")
}
bstack1111l111ll_opy_ = {
  bstack11ll1_opy_ (u"ࠪࡆࡊࡌࡏࡓࡇࡢࡅࡑࡒࠧ᫤"): bstack11ll1_opy_ (u"ࠫࡘࡻࡩࡵࡧࠣࡗࡪࡺࡵࡱࠩ᫥"),
  bstack11ll1_opy_ (u"ࠬࡇࡆࡕࡇࡕࡣࡆࡒࡌࠨ᫦"): bstack11ll1_opy_ (u"࠭ࡓࡶ࡫ࡷࡩ࡚ࠥࡥࡢࡴࡧࡳࡼࡴࠧ᫧"),
  bstack11ll1_opy_ (u"ࠧࡃࡇࡉࡓࡗࡋ࡟ࡆࡃࡆࡌࠬ᫨"): bstack11ll1_opy_ (u"ࠨࡖࡨࡷࡹࠦࡓࡦࡶࡸࡴࠬ᫩"),
  bstack11ll1_opy_ (u"ࠩࡄࡊ࡙ࡋࡒࡠࡇࡄࡇࡍ࠭᫪"): bstack11ll1_opy_ (u"ࠪࡘࡪࡹࡴࠡࡖࡨࡥࡷࡪ࡯ࡸࡰࠪ᫫")
}
bstack11l11lll1ll_opy_ = 65536
bstack11l11ll1l1l_opy_ = bstack11ll1_opy_ (u"ࠫ࠳࠴࠮࡜ࡖࡕ࡙ࡓࡉࡁࡕࡇࡇࡡࠬ᫬")
bstack11l11ll11ll_opy_ = [
      bstack11ll1_opy_ (u"ࠬࡻࡳࡦࡴࡑࡥࡲ࡫ࠧ᫭"), bstack11ll1_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸࡑࡥࡺࠩ᫮"), bstack11ll1_opy_ (u"ࠧࡩࡶࡷࡴࡕࡸ࡯ࡹࡻࠪ᫯"), bstack11ll1_opy_ (u"ࠨࡪࡷࡸࡵࡹࡐࡳࡱࡻࡽࠬ᫰"), bstack11ll1_opy_ (u"ࠩࡦࡹࡸࡺ࡯࡮ࡘࡤࡶ࡮ࡧࡢ࡭ࡧࡶࠫ᫱"),
      bstack11ll1_opy_ (u"ࠪࡴࡷࡵࡸࡺࡗࡶࡩࡷ࠭᫲"), bstack11ll1_opy_ (u"ࠫࡵࡸ࡯ࡹࡻࡓࡥࡸࡹࠧ᫳"), bstack11ll1_opy_ (u"ࠬࡲ࡯ࡤࡣ࡯ࡔࡷࡵࡸࡺࡗࡶࡩࡷ࠭᫴"), bstack11ll1_opy_ (u"࠭࡬ࡰࡥࡤࡰࡕࡸ࡯ࡹࡻࡓࡥࡸࡹࠧ᫵"),
      bstack11ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡵࡴࡧࡵࡒࡦࡳࡥࠨ᫶"), bstack11ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡢࡥࡦࡩࡸࡹࡋࡦࡻࠪ᫷"), bstack11ll1_opy_ (u"ࠩࡤࡹࡹ࡮ࡔࡰ࡭ࡨࡲࠬ᫸")
    ]
bstack11l1l1l1lll_opy_= {
  bstack11ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡎࡲࡧࡦࡲࠧ᫹"): bstack11ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡏࡳࡨࡧ࡬ࠨ᫺"),
  bstack11ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࡑࡳࡸ࡮ࡵ࡮ࡴࠩ᫻"): bstack11ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࡒࡴࡹ࡯࡯࡯ࡵࠪ᫼"),
  bstack11ll1_opy_ (u"ࠧ࡭ࡱࡦࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭᫽"): bstack11ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡕࡷࡥࡨࡱࡌࡰࡥࡤࡰࡔࡶࡴࡪࡱࡱࡷࠬ᫾"),
  bstack11ll1_opy_ (u"ࠩࡳࡥࡷࡧ࡬࡭ࡧ࡯ࡷࡕ࡫ࡲࡑ࡮ࡤࡸ࡫ࡵࡲ࡮ࠩ᫿"): bstack11ll1_opy_ (u"ࠪࡴࡦࡸࡡ࡭࡮ࡨࡰࡸࡖࡥࡳࡒ࡯ࡥࡹ࡬࡯ࡳ࡯ࠪᬀ"),
  bstack11ll1_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧᬁ"): bstack11ll1_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨᬂ"),
  bstack11ll1_opy_ (u"࠭࡬ࡰࡩࡏࡩࡻ࡫࡬ࠨᬃ"): bstack11ll1_opy_ (u"ࠧ࡭ࡱࡪࡐࡪࡼࡥ࡭ࠩᬄ"),
  bstack11ll1_opy_ (u"ࠨࡪࡷࡸࡵࡖࡲࡰࡺࡼࠫᬅ"): bstack11ll1_opy_ (u"ࠩ࡫ࡸࡹࡶࡐࡳࡱࡻࡽࠬᬆ"),
  bstack11ll1_opy_ (u"ࠪ࡬ࡹࡺࡰࡴࡒࡵࡳࡽࡿࠧᬇ"): bstack11ll1_opy_ (u"ࠫ࡭ࡺࡴࡱࡵࡓࡶࡴࡾࡹࠨᬈ"),
  bstack11ll1_opy_ (u"ࠬ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࠨᬉ"): bstack11ll1_opy_ (u"࠭ࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࠩᬊ"),
  bstack11ll1_opy_ (u"ࠧࡵࡧࡶࡸࡈࡵ࡮ࡵࡧࡻࡸࡔࡶࡴࡪࡱࡱࡷࠬᬋ"): bstack11ll1_opy_ (u"ࠨࡶࡨࡷࡹࡉ࡯࡯ࡶࡨࡼࡹࡕࡰࡵ࡫ࡲࡲࡸ࠭ᬌ"),
  bstack11ll1_opy_ (u"ࠩࡷࡩࡸࡺࡏࡣࡵࡨࡶࡻࡧࡢࡪ࡮࡬ࡸࡾ࠭ᬍ"): bstack11ll1_opy_ (u"ࠪࡸࡪࡹࡴࡐࡤࡶࡩࡷࡼࡡࡣ࡫࡯࡭ࡹࡿࠧᬎ"),
  bstack11ll1_opy_ (u"ࠫࡹ࡫ࡳࡵࡔࡨࡴࡴࡸࡴࡪࡰࡪࠫᬏ"): bstack11ll1_opy_ (u"ࠬࡺࡥࡴࡶࡕࡩࡵࡵࡲࡵ࡫ࡱ࡫ࠬᬐ"),
  bstack11ll1_opy_ (u"࠭ࡴࡦࡵࡷࡓࡧࡹࡥࡳࡸࡤࡦ࡮ࡲࡩࡵࡻࡒࡴࡹ࡯࡯࡯ࡵࠪᬑ"): bstack11ll1_opy_ (u"ࠧࡵࡧࡶࡸࡔࡨࡳࡦࡴࡹࡥࡧ࡯࡬ࡪࡶࡼࡓࡵࡺࡩࡰࡰࡶࠫᬒ"),
  bstack11ll1_opy_ (u"ࠨࡶࡨࡷࡹࡘࡥࡱࡱࡵࡸ࡮ࡴࡧࡐࡲࡷ࡭ࡴࡴࡳࠨᬓ"): bstack11ll1_opy_ (u"ࠩࡷࡩࡸࡺࡒࡦࡲࡲࡶࡹ࡯࡮ࡨࡑࡳࡸ࡮ࡵ࡮ࡴࠩᬔ"),
  bstack11ll1_opy_ (u"ࠪࡧࡺࡹࡴࡰ࡯࡙ࡥࡷ࡯ࡡࡣ࡮ࡨࡷࠬᬕ"): bstack11ll1_opy_ (u"ࠫࡨࡻࡳࡵࡱࡰ࡚ࡦࡸࡩࡢࡤ࡯ࡩࡸ࠭ᬖ"),
  bstack11ll1_opy_ (u"ࠬࡧࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࠩᬗ"): bstack11ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡆࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠨᬘ"),
  bstack11ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡇࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࠩᬙ"): bstack11ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡁࡶࡶࡲࡱࡦࡺࡩࡰࡰࠪᬚ"),
  bstack11ll1_opy_ (u"ࠩࡵࡩࡷࡻ࡮ࡕࡧࡶࡸࡸ࠭ᬛ"): bstack11ll1_opy_ (u"ࠪࡶࡪࡸࡵ࡯ࡖࡨࡷࡹࡹࠧᬜ"),
  bstack11ll1_opy_ (u"ࠫࡵ࡫ࡲࡤࡻࠪᬝ"): bstack11ll1_opy_ (u"ࠬࡶࡥࡳࡥࡼࠫᬞ"),
  bstack11ll1_opy_ (u"࠭ࡰࡦࡴࡦࡽࡔࡶࡴࡪࡱࡱࡷࠬᬟ"): bstack11ll1_opy_ (u"ࠧࡱࡧࡵࡧࡾࡕࡰࡵ࡫ࡲࡲࡸ࠭ᬠ"),
  bstack11ll1_opy_ (u"ࠨࡲࡨࡶࡨࡿࡃࡢࡲࡷࡹࡷ࡫ࡍࡰࡦࡨࠫᬡ"): bstack11ll1_opy_ (u"ࠩࡳࡩࡷࡩࡹࡄࡣࡳࡸࡺࡸࡥࡎࡱࡧࡩࠬᬢ"),
  bstack11ll1_opy_ (u"ࠪࡨ࡮ࡹࡡࡣ࡮ࡨࡅࡺࡺ࡯ࡄࡣࡳࡸࡺࡸࡥࡍࡱࡪࡷࠬᬣ"): bstack11ll1_opy_ (u"ࠫࡩ࡯ࡳࡢࡤ࡯ࡩࡆࡻࡴࡰࡅࡤࡴࡹࡻࡲࡦࡎࡲ࡫ࡸ࠭ᬤ"),
  bstack11ll1_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠬᬥ"): bstack11ll1_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾ࠭ᬦ"),
  bstack11ll1_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࡏࡱࡶ࡬ࡳࡳࡹࠧᬧ"): bstack11ll1_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࡐࡲࡷ࡭ࡴࡴࡳࠨᬨ"),
  bstack11ll1_opy_ (u"ࠩࡷࡹࡷࡨ࡯ࡔࡥࡤࡰࡪ࠭ᬩ"): bstack11ll1_opy_ (u"ࠪࡸࡺࡸࡢࡰࡕࡦࡥࡱ࡫ࠧᬪ"),
  bstack11ll1_opy_ (u"ࠫࡹࡻࡲࡣࡱࡖࡧࡦࡲࡥࡐࡲࡷ࡭ࡴࡴࡳࠨᬫ"): bstack11ll1_opy_ (u"ࠬࡺࡵࡳࡤࡲࡗࡨࡧ࡬ࡦࡑࡳࡸ࡮ࡵ࡮ࡴࠩᬬ"),
  bstack11ll1_opy_ (u"࠭ࡴࡦࡵࡷࡓࡷࡩࡨࡦࡵࡷࡶࡦࡺࡩࡰࡰࡒࡴࡹ࡯࡯࡯ࡵࠪᬭ"): bstack11ll1_opy_ (u"ࠧࡵࡧࡶࡸࡔࡸࡣࡩࡧࡶࡸࡷࡧࡴࡪࡱࡱࡓࡵࡺࡩࡰࡰࡶࠫᬮ"),
  bstack11ll1_opy_ (u"ࠨࡲࡵࡳࡽࡿࡓࡦࡶࡷ࡭ࡳ࡭ࡳࠨᬯ"): bstack11ll1_opy_ (u"ࠩࡳࡶࡴࡾࡹࡔࡧࡷࡸ࡮ࡴࡧࡴࠩᬰ")
}
bstack11l1l11111l_opy_ = [bstack11ll1_opy_ (u"ࠪࡴࡾࡺࡥࡴࡶࠪᬱ"), bstack11ll1_opy_ (u"ࠫࡷࡵࡢࡰࡶࠪᬲ")]
bstack111ll1l1l1_opy_ = (bstack11ll1_opy_ (u"ࠧࡶࡹࡵࡧࡶࡸࠧᬳ"),)
bstack11l11lll11l_opy_ = bstack11ll1_opy_ (u"࠭ࡳࡥ࡭࠲ࡺ࠶࠵ࡵࡱࡦࡤࡸࡪࡥࡣ࡭࡫᬴ࠪ")
bstack1l1l11l1l_opy_ = bstack11ll1_opy_ (u"ࠢࡩࡶࡷࡴࡸࡀ࠯࠰ࡣࡳ࡭࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡨࡵ࡭࠰ࡣࡸࡸࡴࡳࡡࡵࡧ࠰ࡸࡺࡸࡢࡰࡵࡦࡥࡱ࡫࠯ࡷ࠳࠲࡫ࡷ࡯ࡤࡴ࠱ࠥᬵ")
bstack1ll1111111_opy_ = bstack11ll1_opy_ (u"ࠣࡪࡷࡸࡵࡹ࠺࠰࠱ࡪࡶ࡮ࡪ࠮ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡣࡰ࡯࠲ࡨࡦࡹࡨࡣࡱࡤࡶࡩ࠵ࡢࡶ࡫࡯ࡨࡸ࠵ࠢᬶ")
bstack1l1l1lllll_opy_ = bstack11ll1_opy_ (u"ࠤ࡫ࡸࡹࡶࡳ࠻࠱࠲ࡥࡵ࡯࠮ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡣࡰ࡯࠲ࡥࡺࡺ࡯࡮ࡣࡷࡩ࠲ࡺࡵࡳࡤࡲࡷࡨࡧ࡬ࡦ࠱ࡹ࠵࠴ࡨࡵࡪ࡮ࡧࡷ࠳ࡰࡳࡰࡰࠥᬷ")
class EVENTS(Enum):
  bstack11l1l11l111_opy_ = bstack11ll1_opy_ (u"ࠪࡷࡩࡱ࠺ࡰ࠳࠴ࡽ࠿ࡶࡲࡪࡰࡷ࠱ࡧࡻࡩ࡭ࡦ࡯࡭ࡳࡱࠧᬸ")
  bstack1l111l1lll_opy_ = bstack11ll1_opy_ (u"ࠫࡸࡪ࡫࠻ࡥ࡯ࡩࡦࡴࡵࡱࠩᬹ") # final bstack11l1l1l1l1l_opy_
  bstack11l11llll11_opy_ = bstack11ll1_opy_ (u"ࠬࡹࡤ࡬࠼ࡶࡩࡳࡪ࡬ࡰࡩࡶࠫᬺ")
  bstack1ll11ll11_opy_ = bstack11ll1_opy_ (u"࠭ࡳࡥ࡭࠽ࡸࡺࡸࡢࡰࡵࡦࡥࡱ࡫࠺ࡱࡴ࡬ࡲࡹ࠳ࡢࡶ࡫࡯ࡨࡱ࡯࡮࡬ࠩᬻ") #shift post bstack11l11ll1ll1_opy_
  bstack1l111ll1l_opy_ = bstack11ll1_opy_ (u"ࠧࡴࡦ࡮࠾ࡦࡻࡴࡰ࡯ࡤࡸࡪࡀࡰࡳ࡫ࡱࡸ࠲ࡨࡵࡪ࡮ࡧࡰ࡮ࡴ࡫ࠨᬼ") #shift post bstack11l11ll1ll1_opy_
  bstack11l1l111ll1_opy_ = bstack11ll1_opy_ (u"ࠨࡵࡧ࡯࠿ࡺࡥࡴࡶ࡫ࡹࡧ࠭ᬽ") #shift
  bstack11l11lll111_opy_ = bstack11ll1_opy_ (u"ࠩࡶࡨࡰࡀࡰࡦࡴࡦࡽ࠿ࡪ࡯ࡸࡰ࡯ࡳࡦࡪࠧᬾ") #shift
  bstack1111ll11_opy_ = bstack11ll1_opy_ (u"ࠪࡷࡩࡱ࠺ࡵࡷࡵࡦࡴࡹࡣࡢ࡮ࡨ࠾࡭ࡻࡢ࠮࡯ࡤࡲࡦ࡭ࡥ࡮ࡧࡱࡸࠬᬿ")
  bstack1l11l111111_opy_ = bstack11ll1_opy_ (u"ࠫࡸࡪ࡫࠻ࡣ࠴࠵ࡾࡀࡳࡢࡸࡨ࠱ࡷ࡫ࡳࡶ࡮ࡷࡷࠬᭀ")
  bstack11lll11l_opy_ = bstack11ll1_opy_ (u"ࠬࡹࡤ࡬࠼ࡤ࠵࠶ࡿ࠺ࡥࡴ࡬ࡺࡪࡸ࠭ࡱࡧࡵࡪࡴࡸ࡭ࡴࡥࡤࡲࠬᭁ")
  bstack1ll111ll1_opy_ = bstack11ll1_opy_ (u"࠭ࡳࡥ࡭࠽ࡥࡺࡺ࡯࡮ࡣࡷࡩ࠿ࡲ࡯ࡤࡣ࡯ࠫᭂ") #shift
  bstack1ll1111lll_opy_ = bstack11ll1_opy_ (u"ࠧࡴࡦ࡮࠾ࡦࡶࡰ࠮ࡣࡸࡸࡴࡳࡡࡵࡧ࠽ࡥࡵࡶ࠭ࡶࡲ࡯ࡳࡦࡪࠧᭃ") #shift
  bstack1l11l1ll11_opy_ = bstack11ll1_opy_ (u"ࠨࡵࡧ࡯࠿ࡧࡵࡵࡱࡰࡥࡹ࡫࠺ࡤ࡫࠰ࡥࡷࡺࡩࡧࡣࡦࡸࡸ᭄࠭")
  bstack1ll1ll1ll1_opy_ = bstack11ll1_opy_ (u"ࠩࡶࡨࡰࡀࡡ࠲࠳ࡼ࠾࡬࡫ࡴ࠮ࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹ࠮ࡴࡨࡷࡺࡲࡴࡴ࠯ࡶࡹࡲࡳࡡࡳࡻࠪᭅ") #shift
  bstack1lll1l111l_opy_ = bstack11ll1_opy_ (u"ࠪࡷࡩࡱ࠺ࡢ࠳࠴ࡽ࠿࡭ࡥࡵ࠯ࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺ࠯ࡵࡩࡸࡻ࡬ࡵࡵࠪᭆ") #shift
  bstack11l11ll1lll_opy_ = bstack11ll1_opy_ (u"ࠫࡸࡪ࡫࠻ࡲࡨࡶࡨࡿࠧᭇ") #shift
  bstack11lllll1111_opy_ = bstack11ll1_opy_ (u"ࠬࡹࡤ࡬࠼ࡳࡩࡷࡩࡹ࠻ࡵࡦࡶࡪ࡫࡮ࡴࡪࡲࡸࠬᭈ")
  bstack11llll111_opy_ = bstack11ll1_opy_ (u"࠭ࡳࡥ࡭࠽ࡥࡺࡺ࡯࡮ࡣࡷࡩ࠿ࡹࡥࡴࡵ࡬ࡳࡳ࠳ࡳࡵࡣࡷࡹࡸ࠭ᭉ") #shift
  bstack1ll11111_opy_ = bstack11ll1_opy_ (u"ࠧࡴࡦ࡮࠾ࡦࡻࡴࡰ࡯ࡤࡸࡪࡀࡨࡶࡤ࠰ࡱࡦࡴࡡࡨࡧࡰࡩࡳࡺࠧᭊ")
  bstack11l1l1l1ll1_opy_ = bstack11ll1_opy_ (u"ࠨࡵࡧ࡯࠿ࡶࡲࡰࡺࡼ࠱ࡸ࡫ࡴࡶࡲࠪᭋ") #shift
  bstack1ll111111l_opy_ = bstack11ll1_opy_ (u"ࠩࡶࡨࡰࡀࡳࡦࡶࡸࡴࠬᭌ")
  bstack11l1l1l11ll_opy_ = bstack11ll1_opy_ (u"ࠪࡷࡩࡱ࠺ࡱࡧࡵࡧࡾࡀࡳ࡯ࡣࡳࡷ࡭ࡵࡴࠨ᭍") # not bstack11l1l11ll11_opy_ in python
  bstack1lll111l1_opy_ = bstack11ll1_opy_ (u"ࠫࡸࡪ࡫࠻ࡦࡵ࡭ࡻ࡫ࡲ࠻ࡳࡸ࡭ࡹ࠭᭎") # used in bstack11l1l1l111l_opy_
  bstack11llllll11_opy_ = bstack11ll1_opy_ (u"ࠬࡹࡤ࡬࠼ࡧࡶ࡮ࡼࡥࡳ࠼ࡪࡩࡹ࠭᭏") # used in bstack11l1l1l111l_opy_
  bstack11l1llllll_opy_ = bstack11ll1_opy_ (u"࠭ࡳࡥ࡭࠽࡬ࡴࡵ࡫ࠨ᭐")
  bstack1l1lllllll_opy_ = bstack11ll1_opy_ (u"ࠧࡴࡦ࡮࠾ࡦࡻࡴࡰ࡯ࡤࡸࡪࡀࡳࡦࡵࡶ࡭ࡴࡴ࠭࡯ࡣࡰࡩࠬ᭑")
  bstack11llll1l_opy_ = bstack11ll1_opy_ (u"ࠨࡵࡧ࡯࠿ࡧࡵࡵࡱࡰࡥࡹ࡫࠺ࡴࡧࡶࡷ࡮ࡵ࡮࠮ࡣࡱࡲࡴࡺࡡࡵ࡫ࡲࡲࠬ᭒") #
  bstack1111l11l1_opy_ = bstack11ll1_opy_ (u"ࠩࡶࡨࡰࡀ࡯࠲࠳ࡼ࠾ࡩࡸࡩࡷࡧࡵ࠱ࡹࡧ࡫ࡦࡕࡦࡶࡪ࡫࡮ࡔࡪࡲࡸࠬ᭓")
  bstack1l1ll1llll_opy_ = bstack11ll1_opy_ (u"ࠪࡷࡩࡱ࠺ࡱࡧࡵࡧࡾࡀࡡࡶࡶࡲ࠱ࡨࡧࡰࡵࡷࡵࡩࠬ᭔")
  bstack11l11ll1l_opy_ = bstack11ll1_opy_ (u"ࠫࡸࡪ࡫࠻ࡲࡵࡩ࠲ࡺࡥࡴࡶࠪ᭕")
  bstack1l11l1l11l_opy_ = bstack11ll1_opy_ (u"ࠬࡹࡤ࡬࠼ࡳࡳࡸࡺ࠭ࡵࡧࡶࡸࠬ᭖")
  bstack11llllll_opy_ = bstack11ll1_opy_ (u"࠭ࡳࡥ࡭࠽ࡨࡷ࡯ࡶࡦࡴ࠽ࡴࡷ࡫࠭ࡪࡰ࡬ࡸ࡮ࡧ࡬ࡪࡼࡤࡸ࡮ࡵ࡮ࠨ᭗") #shift
  bstack111lll111l_opy_ = bstack11ll1_opy_ (u"ࠧࡴࡦ࡮࠾ࡩࡸࡩࡷࡧࡵ࠾ࡵࡵࡳࡵ࠯࡬ࡲ࡮ࡺࡩࡢ࡮࡬ࡾࡦࡺࡩࡰࡰࠪ᭘") #shift
  bstack11l11llllll_opy_ = bstack11ll1_opy_ (u"ࠨࡵࡧ࡯࠿ࡧࡵࡵࡱ࠰ࡧࡦࡶࡴࡶࡴࡨࠫ᭙")
  bstack11l11llll1l_opy_ = bstack11ll1_opy_ (u"ࠩࡶࡨࡰࡀࡡࡶࡶࡲࡱࡦࡺࡥ࠻࡫ࡧࡰࡪ࠳ࡴࡪ࡯ࡨࡳࡺࡺࠧ᭚")
  bstack1l1l1ll1l1l_opy_ = bstack11ll1_opy_ (u"ࠪࡷࡩࡱ࠺ࡤ࡮࡬࠾ࡸࡺࡡࡳࡶࠪ᭛")
  bstack11l1l111l1l_opy_ = bstack11ll1_opy_ (u"ࠫࡸࡪ࡫࠻ࡥ࡯࡭࠿ࡪ࡯ࡸࡰ࡯ࡳࡦࡪࠧ᭜")
  bstack11l11ll1l11_opy_ = bstack11ll1_opy_ (u"ࠬࡹࡤ࡬࠼ࡦࡰ࡮ࡀࡣࡩࡧࡦ࡯࠲ࡻࡰࡥࡣࡷࡩࠬ᭝")
  bstack1l1l1l1ll1l_opy_ = bstack11ll1_opy_ (u"࠭ࡳࡥ࡭࠽ࡧࡱ࡯࠺ࡰࡰ࠰ࡦࡴࡵࡴࡴࡶࡵࡥࡵ࠭᭞")
  bstack1l1l11llll1_opy_ = bstack11ll1_opy_ (u"ࠧࡴࡦ࡮࠾ࡨࡲࡩ࠻ࡱࡱ࠱ࡨࡵ࡮࡯ࡧࡦࡸࠬ᭟")
  bstack1l1l11l1111_opy_ = bstack11ll1_opy_ (u"ࠨࡵࡧ࡯࠿ࡩ࡬ࡪ࠼ࡲࡲ࠲ࡹࡴࡰࡲࠪ᭠")
  bstack1l1ll1l111l_opy_ = bstack11ll1_opy_ (u"ࠩࡶࡨࡰࡀࡳࡵࡣࡵࡸࡇ࡯࡮ࡔࡧࡶࡷ࡮ࡵ࡮ࠨ᭡")
  bstack1l1l1l1l1ll_opy_ = bstack11ll1_opy_ (u"ࠪࡷࡩࡱ࠺ࡤࡱࡱࡲࡪࡩࡴࡃ࡫ࡱࡗࡪࡹࡳࡪࡱࡱࠫ᭢")
  bstack11l1l11lll1_opy_ = bstack11ll1_opy_ (u"ࠫࡸࡪ࡫࠻ࡦࡵ࡭ࡻ࡫ࡲࡊࡰ࡬ࡸࠬ᭣")
  bstack11l1l111111_opy_ = bstack11ll1_opy_ (u"ࠬࡹࡤ࡬࠼ࡩ࡭ࡳࡪࡎࡦࡣࡵࡩࡸࡺࡈࡶࡤࠪ᭤")
  bstack11lll1111l1_opy_ = bstack11ll1_opy_ (u"࠭ࡳࡥ࡭࠽ࡥࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࡆࡳࡣࡰࡩࡼࡵࡲ࡬ࡋࡱ࡭ࡹ࠭᭥")
  bstack11ll1lllll1_opy_ = bstack11ll1_opy_ (u"ࠧࡴࡦ࡮࠾ࡦࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࡇࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡖࡸࡦࡸࡴࠨ᭦")
  bstack1l111ll11l1_opy_ = bstack11ll1_opy_ (u"ࠨࡵࡧ࡯࠿ࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࡈࡵ࡮ࡧ࡫ࡪࠫ᭧")
  bstack11l11ll111l_opy_ = bstack11ll1_opy_ (u"ࠩࡶࡨࡰࡀ࡯ࡣࡵࡨࡶࡻࡧࡢࡪ࡮࡬ࡸࡾࡉ࡯࡯ࡨ࡬࡫ࠬ᭨")
  bstack1l111ll1111_opy_ = bstack11ll1_opy_ (u"ࠪࡷࡩࡱ࠺ࡢ࡫ࡖࡩࡱ࡬ࡈࡦࡣ࡯ࡗࡹ࡫ࡰࠨ᭩")
  bstack1l111l1lll1_opy_ = bstack11ll1_opy_ (u"ࠫࡸࡪ࡫࠻ࡣ࡬ࡗࡪࡲࡦࡉࡧࡤࡰࡌ࡫ࡴࡓࡧࡶࡹࡱࡺࠧ᭪")
  bstack1l1111ll1ll_opy_ = bstack11ll1_opy_ (u"ࠬࡹࡤ࡬࠼ࡷࡩࡸࡺࡆࡳࡣࡰࡩࡼࡵࡲ࡬ࡇࡹࡩࡳࡺࠧ᭫")
  bstack1l11111l111_opy_ = bstack11ll1_opy_ (u"࠭ࡳࡥ࡭࠽ࡸࡪࡹࡴࡔࡧࡶࡷ࡮ࡵ࡮ࡆࡸࡨࡲࡹ᭬࠭")
  bstack1l1111l1l11_opy_ = bstack11ll1_opy_ (u"ࠧࡴࡦ࡮࠾ࡨࡲࡩ࠻࡮ࡲ࡫ࡈࡸࡥࡢࡶࡨࡨࡊࡼࡥ࡯ࡶࠪ᭭")
  bstack11l1l1l11l1_opy_ = bstack11ll1_opy_ (u"ࠨࡵࡧ࡯࠿ࡩ࡬ࡪ࠼ࡨࡲࡶࡻࡥࡶࡧࡗࡩࡸࡺࡅࡷࡧࡱࡸࠬ᭮")
  bstack11lll111lll_opy_ = bstack11ll1_opy_ (u"ࠩࡶࡨࡰࡀࡡࡶࡶࡲࡱࡦࡺࡩࡰࡰࡉࡶࡦࡳࡥࡸࡱࡵ࡯ࡘࡺ࡯ࡱࠩ᭯")
  bstack1l1l11ll1l1_opy_ = bstack11ll1_opy_ (u"ࠪࡷࡩࡱ࠺ࡰࡰࡖࡸࡴࡶࠧ᭰")
class STAGE(Enum):
  bstack11l11ll11l_opy_ = bstack11ll1_opy_ (u"ࠫࡸࡺࡡࡳࡶࠪ᭱")
  END = bstack11ll1_opy_ (u"ࠬ࡫࡮ࡥࠩ᭲")
  bstack11l1llll1_opy_ = bstack11ll1_opy_ (u"࠭ࡳࡪࡰࡪࡰࡪ࠭᭳")
bstack11l1ll111l_opy_ = {
  bstack11ll1_opy_ (u"ࠧࡑ࡛ࡗࡉࡘ࡚ࠧ᭴"): bstack11ll1_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࠨ᭵"),
  bstack11ll1_opy_ (u"ࠩࡓ࡝࡙ࡋࡓࡕ࠯ࡅࡈࡉ࠭᭶"): bstack11ll1_opy_ (u"ࠪࡔࡾࡺࡥࡴࡶ࠰ࡧࡺࡩࡵ࡮ࡤࡨࡶࠬ᭷")
}
PLAYWRIGHT_HUB_URL = bstack11ll1_opy_ (u"ࠦࡼࡹࡳ࠻࠱࠲ࡧࡩࡶ࠮ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡣࡰ࡯࠲ࡴࡱࡧࡹࡸࡴ࡬࡫࡭ࡺ࠿ࡤࡣࡳࡷࡂࠨ᭸")
bstack1l111ll1lll_opy_ = 98
bstack1l11l11l1ll_opy_ = 100
bstack111111ll1l_opy_ = {
  bstack11ll1_opy_ (u"ࠬࡸࡥࡳࡷࡱࠫ᭹"): bstack11ll1_opy_ (u"࠭࠭࠮ࡴࡨࡶࡺࡴࡳࠨ᭺"),
  bstack11ll1_opy_ (u"ࠧࡥࡧ࡯ࡥࡾ࠭᭻"): bstack11ll1_opy_ (u"ࠨ࠯࠰ࡶࡪࡸࡵ࡯ࡵ࠰ࡨࡪࡲࡡࡺࠩ᭼"),
  bstack11ll1_opy_ (u"ࠩࡵࡩࡷࡻ࡮࠮ࡦࡨࡰࡦࡿࠧ᭽"): 0
}
bstack11l11lll1l1_opy_ = bstack11ll1_opy_ (u"ࠥ࡬ࡹࡺࡰࡴ࠼࠲࠳ࡨࡵ࡬࡭ࡧࡦࡸࡴࡸ࠭ࡰࡤࡶࡩࡷࡼࡡࡣ࡫࡯࡭ࡹࡿ࠮ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡣࡰ࡯ࠥ᭾")
bstack11l1l1ll111_opy_ = bstack11ll1_opy_ (u"ࠦ࡭ࡺࡴࡱࡵ࠽࠳࠴ࡻࡰ࡭ࡱࡤࡨ࠲ࡵࡢࡴࡧࡵࡺࡦࡨࡩ࡭࡫ࡷࡽ࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡨࡵ࡭ࠣ᭿")
bstack111ll1ll1_opy_ = bstack11ll1_opy_ (u"࡚ࠧࡅࡔࡖࠣࡖࡊࡖࡏࡓࡖࡌࡒࡌࠦࡁࡏࡆࠣࡅࡓࡇࡌ࡚ࡖࡌࡇࡘࠨᮀ")