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
import json
import shutil
import tempfile
import threading
import urllib.request
import uuid
from pathlib import Path
import logging
import re
from bstack_utils.helper import bstack1llll111l1l_opy_
bstack11ll11llll1_opy_ = 100 * 1024 * 1024 # 100 bstack11ll1l1ll11_opy_
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
bstack1lll11lll1l_opy_ = bstack1llll111l1l_opy_()
bstack1ll1ll1l11l_opy_ = bstack11ll1_opy_ (u"࡛ࠧࡰ࡭ࡱࡤࡨࡪࡪࡁࡵࡶࡤࡧ࡭ࡳࡥ࡯ࡶࡶ࠱ࠧᚆ")
bstack1ll1ll11111_opy_ = bstack11ll1_opy_ (u"ࠨࡔࡦࡵࡷࡐࡪࡼࡥ࡭ࠤᚇ")
bstack1ll1ll111l1_opy_ = bstack11ll1_opy_ (u"ࠢࡃࡷ࡬ࡰࡩࡒࡥࡷࡧ࡯ࠦᚈ")
bstack1ll1l1llll1_opy_ = bstack11ll1_opy_ (u"ࠣࡊࡲࡳࡰࡒࡥࡷࡧ࡯ࠦᚉ")
bstack11ll1l1l1l1_opy_ = bstack11ll1_opy_ (u"ࠤࡅࡹ࡮ࡲࡤࡍࡧࡹࡩࡱࡎ࡯ࡰ࡭ࡈࡺࡪࡴࡴࠣᚊ")
_11ll11lllll_opy_ = threading.local()
def bstack1ll1lllllll_opy_(test_framework_state, test_hook_state):
    bstack11ll1_opy_ (u"ࠥࠦࠧࠐࠠࠡࠢࠣࡗࡪࡺࠠࡵࡪࡨࠤࡨࡻࡲࡳࡧࡱࡸࠥࡺࡥࡴࡶࠣࡩࡻ࡫࡮ࡵࠢࡶࡸࡦࡺࡥࠡ࡫ࡱࠤࡹ࡮ࡲࡦࡣࡧ࠱ࡱࡵࡣࡢ࡮ࠣࡷࡹࡵࡲࡢࡩࡨ࠲ࠏࠦࠠࠡࠢࡗ࡬࡮ࡹࠠࡧࡷࡱࡧࡹ࡯࡯࡯ࠢࡶ࡬ࡴࡻ࡬ࡥࠢࡥࡩࠥࡩࡡ࡭࡮ࡨࡨࠥࡨࡹࠡࡶ࡫ࡩࠥ࡫ࡶࡦࡰࡷࠤ࡭ࡧ࡮ࡥ࡮ࡨࡶࠥ࠮ࡳࡶࡥ࡫ࠤࡦࡹࠠࡵࡴࡤࡧࡰࡥࡥࡷࡧࡱࡸ࠮ࠐࠠࠡࠢࠣࡦࡪ࡬࡯ࡳࡧࠣࡥࡳࡿࠠࡧ࡫࡯ࡩࠥࡻࡰ࡭ࡱࡤࡨࡸࠦ࡯ࡤࡥࡸࡶ࠳ࠐࠠࠡࠢࠣࠦࠧࠨᚋ")
    _11ll11lllll_opy_.test_framework_state = test_framework_state
    _11ll11lllll_opy_.test_hook_state = test_hook_state
def bstack11ll1l1llll_opy_():
    bstack11ll1_opy_ (u"ࠦࠧࠨࠊࠡࠢࠣࠤࡗ࡫ࡴࡳ࡫ࡨࡺࡪࠦࡴࡩࡧࠣࡧࡺࡸࡲࡦࡰࡷࠤࡹ࡫ࡳࡵࠢࡨࡺࡪࡴࡴࠡࡵࡷࡥࡹ࡫ࠠࡧࡴࡲࡱࠥࡺࡨࡳࡧࡤࡨ࠲ࡲ࡯ࡤࡣ࡯ࠤࡸࡺ࡯ࡳࡣࡪࡩ࠳ࠐࠠࠡࠢࠣࡖࡪࡺࡵࡳࡰࡶࠤࡦࠦࡴࡶࡲ࡯ࡩࠥ࠮ࡴࡦࡵࡷࡣ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟ࡴࡶࡤࡸࡪ࠲ࠠࡵࡧࡶࡸࡤ࡮࡯ࡰ࡭ࡢࡷࡹࡧࡴࡦࠫࠣࡳࡷࠦࠨࡏࡱࡱࡩ࠱ࠦࡎࡰࡰࡨ࠭ࠥ࡯ࡦࠡࡰࡲࡸࠥࡹࡥࡵ࠰ࠍࠤࠥࠦࠠࠣࠤࠥᚌ")
    return (
        getattr(_11ll11lllll_opy_, bstack11ll1_opy_ (u"ࠬࡺࡥࡴࡶࡢࡪࡷࡧ࡭ࡦࡹࡲࡶࡰࡥࡳࡵࡣࡷࡩࠬᚍ"), None),
        getattr(_11ll11lllll_opy_, bstack11ll1_opy_ (u"࠭ࡴࡦࡵࡷࡣ࡭ࡵ࡯࡬ࡡࡶࡸࡦࡺࡥࠨᚎ"), None)
    )
class bstack11ll1l11l_opy_:
    bstack11ll1_opy_ (u"ࠢࠣࠤࠍࠤࠥࠦࠠࡇ࡫࡯ࡩ࡚ࡶ࡬ࡰࡣࡧࡩࡷࠦࡰࡳࡱࡹ࡭ࡩ࡫ࡳࠡࡨࡸࡲࡨࡺࡩࡰࡰࡤࡰ࡮ࡺࡹࠡࡶࡲࠤࡺࡶ࡬ࡰࡣࡧࠤࡦࡴࠠࡢࡶࡷࡥࡨ࡮࡭ࡦࡰࡷࠤࡧࡧࡳࡦࡦࠣࡳࡳࠦࡴࡩࡧࠣ࡫࡮ࡼࡥ࡯ࠢࡩ࡭ࡱ࡫ࠠࡱࡣࡷ࡬࠳ࠐࠠࠡࠢࠣࡍࡹࠦࡳࡶࡲࡳࡳࡷࡺࡳࠡࡤࡲࡸ࡭ࠦ࡬ࡰࡥࡤࡰࠥ࡬ࡩ࡭ࡧࠣࡴࡦࡺࡨࡴࠢࡤࡲࡩࠦࡈࡕࡖࡓ࠳ࡍ࡚ࡔࡑࡕ࡙ࠣࡗࡒࡳ࠭ࠢࡤࡲࡩࠦࡣࡰࡲ࡬ࡩࡸࠦࡴࡩࡧࠣࡪ࡮ࡲࡥࠡ࡫ࡱࡸࡴࠦࡡࠡࡦࡨࡷ࡮࡭࡮ࡢࡶࡨࡨࠏࠦࠠࠡࠢࡧ࡭ࡷ࡫ࡣࡵࡱࡵࡽࠥࡽࡩࡵࡪ࡬ࡲࠥࡺࡨࡦࠢࡸࡷࡪࡸࠧࡴࠢ࡫ࡳࡲ࡫ࠠࡧࡱ࡯ࡨࡪࡸࠠࡶࡰࡧࡩࡷࠦࡾ࠰࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠰ࡗࡳࡰࡴࡧࡤࡦࡦࡄࡸࡹࡧࡣࡩ࡯ࡨࡲࡹࡹ࠮ࠋࠢࠣࠤࠥࡏࡦࠡࡣࡱࠤࡴࡶࡴࡪࡱࡱࡥࡱࠦࡡࡵࡶࡤࡧ࡭ࡳࡥ࡯ࡶࠣࡴࡦࡸࡡ࡮ࡧࡷࡩࡷࠦࠨࡪࡰࠣࡎࡘࡕࡎࠡࡨࡲࡶࡲࡧࡴࠪࠢ࡬ࡷࠥࡶࡲࡰࡸ࡬ࡨࡪࡪࠠࡢࡰࡧࠤࡨࡵ࡮ࡵࡣ࡬ࡲࡸࠦࡡࠡࡶࡵࡹࡹ࡮ࡹࠡࡸࡤࡰࡺ࡫ࠊࠡࠢࠣࠤ࡫ࡵࡲࠡࡶ࡫ࡩࠥࡱࡥࡺࠢࠥࡦࡺ࡯࡬ࡥࡃࡷࡸࡦࡩࡨ࡮ࡧࡱࡸࠧ࠲ࠠࡵࡪࡨࠤ࡫࡯࡬ࡦࠢࡺ࡭ࡱࡲࠠࡣࡧࠣࡴࡱࡧࡣࡦࡦࠣ࡭ࡳࠦࡴࡩࡧࠣࠦࡇࡻࡩ࡭ࡦࡏࡩࡻ࡫࡬ࠣࠢࡩࡳࡱࡪࡥࡳ࠽ࠣࡳࡹ࡮ࡥࡳࡹ࡬ࡷࡪ࠲ࠊࠡࠢࠣࠤ࡮ࡺࠠࡥࡧࡩࡥࡺࡲࡴࡴࠢࡷࡳࠥࠨࡔࡦࡵࡷࡐࡪࡼࡥ࡭ࠤ࠱ࠎࠥࠦࠠࠡࡖ࡫࡭ࡸࠦࡶࡦࡴࡶ࡭ࡴࡴࠠࡰࡨࠣࡥࡩࡪ࡟ࡢࡶࡷࡥࡨ࡮࡭ࡦࡰࡷࠤ࡮ࡹࠠࡢࠢࡹࡳ࡮ࡪࠠ࡮ࡧࡷ࡬ࡴࡪ⠔ࡪࡶࠣ࡬ࡦࡴࡤ࡭ࡧࡶࠤࡦࡲ࡬ࠡࡧࡵࡶࡴࡸࡳࠡࡩࡵࡥࡨ࡫ࡦࡶ࡮࡯ࡽࠥࡨࡹࠡ࡮ࡲ࡫࡬࡯࡮ࡨࠌࠣࠤࠥࠦࡴࡩࡧࡰࠤࡦࡴࡤࠡࡵ࡬ࡱࡵࡲࡹࠡࡴࡨࡸࡺࡸ࡮ࡪࡰࡪࠤࡼ࡯ࡴࡩࡱࡸࡸࠥࡺࡨࡳࡱࡺ࡭ࡳ࡭ࠠࡦࡺࡦࡩࡵࡺࡩࡰࡰࡶ࠲ࠏࠦࠠࠡࠢࠥࠦࠧᚏ")
    @staticmethod
    def upload_attachment(bstack11ll1l1l111_opy_: str, *bstack11ll1l11l1l_opy_) -> None:
        if not bstack11ll1l1l111_opy_ or not bstack11ll1l1l111_opy_.strip():
            logger.error(bstack11ll1_opy_ (u"ࠣࡣࡧࡨࡤࡧࡴࡵࡣࡦ࡬ࡲ࡫࡮ࡵࠢࡩࡥ࡮ࡲࡥࡥ࠼ࠣࡔࡷࡵࡶࡪࡦࡨࡨࠥ࡬ࡩ࡭ࡧࠣࡴࡦࡺࡨࠡ࡫ࡶࠤࡪࡳࡰࡵࡻࠣࡳࡷࠦࡎࡰࡰࡨ࠲ࠧᚐ"))
            return
        bstack11ll1l1ll1l_opy_ = bstack11ll1l11l1l_opy_[0] if bstack11ll1l11l1l_opy_ and len(bstack11ll1l11l1l_opy_) > 0 else None
        bstack11ll1l11111_opy_ = None
        test_framework_state, test_hook_state = bstack11ll1l1llll_opy_()
        try:
            if bstack11ll1l1l111_opy_.startswith(bstack11ll1_opy_ (u"ࠤ࡫ࡸࡹࡶ࠺࠰࠱ࠥᚑ")) or bstack11ll1l1l111_opy_.startswith(bstack11ll1_opy_ (u"ࠥ࡬ࡹࡺࡰࡴ࠼࠲࠳ࠧᚒ")):
                logger.debug(bstack11ll1_opy_ (u"ࠦࡕࡧࡴࡩࠢ࡬ࡷࠥ࡯ࡤࡦࡰࡷ࡭࡫࡯ࡥࡥࠢࡤࡷ࡛ࠥࡒࡍ࠽ࠣࡨࡴࡽ࡮࡭ࡱࡤࡨ࡮ࡴࡧࠡࡶ࡫ࡩࠥ࡬ࡩ࡭ࡧ࠱ࠦᚓ"))
                url = bstack11ll1l1l111_opy_
                bstack11ll1l1111l_opy_ = str(uuid.uuid4())
                bstack11ll1l1lll1_opy_ = os.path.basename(urllib.request.urlparse(url).path)
                if not bstack11ll1l1lll1_opy_ or not bstack11ll1l1lll1_opy_.strip():
                    bstack11ll1l1lll1_opy_ = bstack11ll1l1111l_opy_
                temp_file = tempfile.NamedTemporaryFile(delete=False,
                                                        prefix=bstack11ll1_opy_ (u"ࠧࡻࡰ࡭ࡱࡤࡨࡤࠨᚔ") + bstack11ll1l1111l_opy_ + bstack11ll1_opy_ (u"ࠨ࡟ࠣᚕ"),
                                                        suffix=bstack11ll1_opy_ (u"ࠢࡠࠤᚖ") + bstack11ll1l1lll1_opy_)
                with urllib.request.urlopen(url) as response, open(temp_file.name, bstack11ll1_opy_ (u"ࠨࡹࡥࠫᚗ")) as out_file:
                    shutil.copyfileobj(response, out_file)
                bstack11ll1l11111_opy_ = Path(temp_file.name)
                logger.debug(bstack11ll1_opy_ (u"ࠤࡇࡳࡼࡴ࡬ࡰࡣࡧࡩࡩࠦࡦࡪ࡮ࡨࠤࡹࡵࠠࡵࡧࡰࡴࡴࡸࡡࡳࡻࠣࡰࡴࡩࡡࡵ࡫ࡲࡲ࠿ࠦࡻࡾࠤᚘ").format(bstack11ll1l11111_opy_))
            else:
                bstack11ll1l11111_opy_ = Path(bstack11ll1l1l111_opy_)
                logger.debug(bstack11ll1_opy_ (u"ࠥࡔࡦࡺࡨࠡ࡫ࡶࠤ࡮ࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡤࠡࡣࡶࠤࡱࡵࡣࡢ࡮ࠣࡪ࡮ࡲࡥ࠻ࠢࡾࢁࠧᚙ").format(bstack11ll1l11111_opy_))
        except Exception as e:
            logger.error(bstack11ll1_opy_ (u"ࠦࡋࡧࡩ࡭ࡧࡧࠤࡹࡵࠠࡰࡤࡷࡥ࡮ࡴࠠࡧ࡫࡯ࡩࠥ࡬ࡲࡰ࡯ࠣࡴࡦࡺࡨ࠰ࡗࡕࡐ࠿ࠦࡻࡾࠤᚚ").format(e))
            return
        if bstack11ll1l11111_opy_ is None or not bstack11ll1l11111_opy_.exists():
            logger.error(bstack11ll1_opy_ (u"࡙ࠧ࡯ࡶࡴࡦࡩࠥ࡬ࡩ࡭ࡧࠣࡨࡴ࡫ࡳࠡࡰࡲࡸࠥ࡫ࡸࡪࡵࡷ࠾ࠥࢁࡽࠣ᚛").format(bstack11ll1l11111_opy_))
            return
        if bstack11ll1l11111_opy_.stat().st_size > bstack11ll11llll1_opy_:
            logger.error(bstack11ll1_opy_ (u"ࠨࡆࡪ࡮ࡨࠤࡸ࡯ࡺࡦࠢࡨࡼࡨ࡫ࡥࡥࡵࠣࡱࡦࡾࡩ࡮ࡷࡰࠤࡦࡲ࡬ࡰࡹࡨࡨࠥࡹࡩࡻࡧࠣࡳ࡫ࠦࡻࡾࠤ᚜").format(bstack11ll11llll1_opy_))
            return
        bstack11ll1l11lll_opy_ = bstack11ll1_opy_ (u"ࠢࡕࡧࡶࡸࡑ࡫ࡶࡦ࡮ࠥ᚝")
        if bstack11ll1l1ll1l_opy_:
            try:
                params = json.loads(bstack11ll1l1ll1l_opy_)
                if bstack11ll1_opy_ (u"ࠣࡤࡸ࡭ࡱࡪࡁࡵࡶࡤࡧ࡭ࡳࡥ࡯ࡶࠥ᚞") in params and params.get(bstack11ll1_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡂࡶࡷࡥࡨ࡮࡭ࡦࡰࡷࠦ᚟")) is True:
                    bstack11ll1l11lll_opy_ = bstack11ll1_opy_ (u"ࠥࡆࡺ࡯࡬ࡥࡎࡨࡺࡪࡲࠢᚠ")
            except Exception as bstack11ll1l111l1_opy_:
                logger.error(bstack11ll1_opy_ (u"ࠦࡏ࡙ࡏࡏࠢࡳࡥࡷࡹࡩ࡯ࡩࠣࡩࡷࡸ࡯ࡳࠢ࡬ࡲࠥࡧࡴࡵࡣࡦ࡬ࡲ࡫࡮ࡵࡒࡤࡶࡦࡳࡳ࠻ࠢࡾࢁࠧᚡ").format(bstack11ll1l111l1_opy_))
        bstack11ll1l11l11_opy_ = False
        from browserstack_sdk.sdk_cli.bstack1ll1ll1111l_opy_ import bstack1ll1l1lllll_opy_
        if test_framework_state in bstack1ll1l1lllll_opy_.bstack1ll1ll11ll1_opy_:
            if bstack11ll1l11lll_opy_ == bstack1ll1ll111l1_opy_:
                bstack11ll1l11l11_opy_ = True
            bstack11ll1l11lll_opy_ = bstack1ll1l1llll1_opy_
        try:
            platform_index = os.environ[bstack11ll1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡕࡒࡁࡕࡈࡒࡖࡒࡥࡉࡏࡆࡈ࡜ࠬᚢ")]
            target_dir = os.path.join(bstack1lll11lll1l_opy_, bstack1ll1ll1l11l_opy_ + str(platform_index),
                                      bstack11ll1l11lll_opy_)
            if bstack11ll1l11l11_opy_:
                target_dir = os.path.join(target_dir, bstack11ll1l1l1l1_opy_)
            os.makedirs(target_dir, exist_ok=True)
            logger.debug(bstack11ll1_opy_ (u"ࠨࡃࡳࡧࡤࡸࡪࡪ࠯ࡷࡧࡵ࡭࡫࡯ࡥࡥࠢࡷࡥࡷ࡭ࡥࡵࠢࡧ࡭ࡷ࡫ࡣࡵࡱࡵࡽ࠿ࠦࡻࡾࠤᚣ").format(target_dir))
            file_name = os.path.basename(bstack11ll1l11111_opy_)
            bstack11ll1l111ll_opy_ = os.path.join(target_dir, file_name)
            if os.path.exists(bstack11ll1l111ll_opy_):
                base_name, extension = os.path.splitext(file_name)
                bstack11ll1l1l1ll_opy_ = 1
                while os.path.exists(os.path.join(target_dir, base_name + str(bstack11ll1l1l1ll_opy_) + extension)):
                    bstack11ll1l1l1ll_opy_ += 1
                bstack11ll1l111ll_opy_ = os.path.join(target_dir, base_name + str(bstack11ll1l1l1ll_opy_) + extension)
            shutil.copy(bstack11ll1l11111_opy_, bstack11ll1l111ll_opy_)
            logger.info(bstack11ll1_opy_ (u"ࠢࡇ࡫࡯ࡩࠥࡹࡵࡤࡥࡨࡷࡸ࡬ࡵ࡭࡮ࡼࠤࡨࡵࡰࡪࡧࡧࠤࡹࡵ࠺ࠡࡽࢀࠦᚤ").format(bstack11ll1l111ll_opy_))
        except Exception as e:
            logger.error(bstack11ll1_opy_ (u"ࠣࡇࡵࡶࡴࡸࠠ࡮ࡱࡹ࡭ࡳ࡭ࠠࡧ࡫࡯ࡩࠥࡺ࡯ࠡࡶࡤࡶ࡬࡫ࡴࠡࡦ࡬ࡶࡪࡩࡴࡰࡴࡼ࠾ࠥࢁࡽࠣᚥ").format(e))
            return
        finally:
            if bstack11ll1l1l111_opy_.startswith(bstack11ll1_opy_ (u"ࠤ࡫ࡸࡹࡶ࠺࠰࠱ࠥᚦ")) or bstack11ll1l1l111_opy_.startswith(bstack11ll1_opy_ (u"ࠥ࡬ࡹࡺࡰࡴ࠼࠲࠳ࠧᚧ")):
                try:
                    if bstack11ll1l11111_opy_ is not None and bstack11ll1l11111_opy_.exists():
                        bstack11ll1l11111_opy_.unlink()
                        logger.debug(bstack11ll1_opy_ (u"࡙ࠦ࡫࡭ࡱࡱࡵࡥࡷࡿࠠࡧ࡫࡯ࡩࠥࡪࡥ࡭ࡧࡷࡩࡩࡀࠠࡼࡿࠥᚨ").format(bstack11ll1l11111_opy_))
                except Exception as ex:
                    logger.error(bstack11ll1_opy_ (u"ࠧࡋࡲࡳࡱࡵࠤࡩ࡫࡬ࡦࡶ࡬ࡲ࡬ࠦࡴࡦ࡯ࡳࡳࡷࡧࡲࡺࠢࡩ࡭ࡱ࡫࠺ࠡࡽࢀࠦᚩ").format(ex))
    @staticmethod
    def bstack11l1lllll1_opy_() -> None:
        bstack11ll1_opy_ (u"ࠨࠢࠣࠌࠣࠤࠥࠦࠠࠡࠢࠣࡈࡪࡲࡥࡵࡧࡶࠤࡦࡲ࡬ࠡࡨࡲࡰࡩ࡫ࡲࡴࠢࡺ࡬ࡴࡹࡥࠡࡰࡤࡱࡪࡹࠠࡴࡶࡤࡶࡹࠦࡷࡪࡶ࡫ࠤ࡛ࠧࡰ࡭ࡱࡤࡨࡪࡪࡁࡵࡶࡤࡧ࡭ࡳࡥ࡯ࡶࡶ࠱ࠧࠦࡦࡰ࡮࡯ࡳࡼ࡫ࡤࠡࡤࡼࠤࡦࠦ࡮ࡶ࡯ࡥࡩࡷࠦࡩ࡯ࠌࠣࠤࠥࠦࠠࠡࠢࠣࡸ࡭࡫ࠠࡶࡵࡨࡶࠬࡹࠠࡿ࠱࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࠢࡧ࡭ࡷ࡫ࡣࡵࡱࡵࡽ࠳ࠐࠠࠡࠢࠣࠤࠥࠦࠠࠣࠤࠥᚪ")
        bstack11ll1l1l11l_opy_ = bstack1llll111l1l_opy_()
        pattern = re.compile(bstack11ll1_opy_ (u"ࡲࠣࡗࡳࡰࡴࡧࡤࡦࡦࡄࡸࡹࡧࡣࡩ࡯ࡨࡲࡹࡹ࠭࡝ࡦ࠮ࠦᚫ"))
        if os.path.exists(bstack11ll1l1l11l_opy_):
            for item in os.listdir(bstack11ll1l1l11l_opy_):
                bstack11ll1l11ll1_opy_ = os.path.join(bstack11ll1l1l11l_opy_, item)
                if os.path.isdir(bstack11ll1l11ll1_opy_) and pattern.fullmatch(item):
                    try:
                        shutil.rmtree(bstack11ll1l11ll1_opy_)
                    except Exception as e:
                        logger.error(bstack11ll1_opy_ (u"ࠣࡇࡵࡶࡴࡸࠠࡥࡧ࡯ࡩࡹ࡯࡮ࡨࠢࡧ࡭ࡷ࡫ࡣࡵࡱࡵࡽ࠿ࠦࡻࡾࠤᚬ").format(e))
        else:
            logger.info(bstack11ll1_opy_ (u"ࠤࡗ࡬ࡪࠦࡤࡪࡴࡨࡧࡹࡵࡲࡺࠢࡧࡳࡪࡹࠠ࡯ࡱࡷࠤࡪࡾࡩࡴࡶ࠽ࠤࢀࢃࠢᚭ").format(bstack11ll1l1l11l_opy_))