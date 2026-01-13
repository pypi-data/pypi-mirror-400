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
from bstack_utils.helper import bstack1l1l1ll11l1_opy_
bstack11ll1l1111l_opy_ = 100 * 1024 * 1024 # 100 bstack11ll1l1lll1_opy_
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
bstack1l1l11llll1_opy_ = bstack1l1l1ll11l1_opy_()
bstack1l1l111ll11_opy_ = bstack11l1l_opy_ (u"࡚ࠦࡶ࡬ࡰࡣࡧࡩࡩࡇࡴࡵࡣࡦ࡬ࡲ࡫࡮ࡵࡵ࠰ࠦᚅ")
bstack11lll111ll1_opy_ = bstack11l1l_opy_ (u"࡚ࠧࡥࡴࡶࡏࡩࡻ࡫࡬ࠣᚆ")
bstack11lll111lll_opy_ = bstack11l1l_opy_ (u"ࠨࡂࡶ࡫࡯ࡨࡑ࡫ࡶࡦ࡮ࠥᚇ")
bstack11lll11l1ll_opy_ = bstack11l1l_opy_ (u"ࠢࡉࡱࡲ࡯ࡑ࡫ࡶࡦ࡮ࠥᚈ")
bstack11ll1l11lll_opy_ = bstack11l1l_opy_ (u"ࠣࡄࡸ࡭ࡱࡪࡌࡦࡸࡨࡰࡍࡵ࡯࡬ࡇࡹࡩࡳࡺࠢᚉ")
_11ll1l11l1l_opy_ = threading.local()
def bstack11llll1l11l_opy_(test_framework_state, test_hook_state):
    bstack11l1l_opy_ (u"ࠤࠥࠦࠏࠦࠠࠡࠢࡖࡩࡹࠦࡴࡩࡧࠣࡧࡺࡸࡲࡦࡰࡷࠤࡹ࡫ࡳࡵࠢࡨࡺࡪࡴࡴࠡࡵࡷࡥࡹ࡫ࠠࡪࡰࠣࡸ࡭ࡸࡥࡢࡦ࠰ࡰࡴࡩࡡ࡭ࠢࡶࡸࡴࡸࡡࡨࡧ࠱ࠎࠥࠦࠠࠡࡖ࡫࡭ࡸࠦࡦࡶࡰࡦࡸ࡮ࡵ࡮ࠡࡵ࡫ࡳࡺࡲࡤࠡࡤࡨࠤࡨࡧ࡬࡭ࡧࡧࠤࡧࡿࠠࡵࡪࡨࠤࡪࡼࡥ࡯ࡶࠣ࡬ࡦࡴࡤ࡭ࡧࡵࠤ࠭ࡹࡵࡤࡪࠣࡥࡸࠦࡴࡳࡣࡦ࡯ࡤ࡫ࡶࡦࡰࡷ࠭ࠏࠦࠠࠡࠢࡥࡩ࡫ࡵࡲࡦࠢࡤࡲࡾࠦࡦࡪ࡮ࡨࠤࡺࡶ࡬ࡰࡣࡧࡷࠥࡵࡣࡤࡷࡵ࠲ࠏࠦࠠࠡࠢࠥࠦࠧᚊ")
    _11ll1l11l1l_opy_.test_framework_state = test_framework_state
    _11ll1l11l1l_opy_.test_hook_state = test_hook_state
def bstack11ll1l1l1ll_opy_():
    bstack11l1l_opy_ (u"ࠥࠦࠧࠐࠠࠡࠢࠣࡖࡪࡺࡲࡪࡧࡹࡩࠥࡺࡨࡦࠢࡦࡹࡷࡸࡥ࡯ࡶࠣࡸࡪࡹࡴࠡࡧࡹࡩࡳࡺࠠࡴࡶࡤࡸࡪࠦࡦࡳࡱࡰࠤࡹ࡮ࡲࡦࡣࡧ࠱ࡱࡵࡣࡢ࡮ࠣࡷࡹࡵࡲࡢࡩࡨ࠲ࠏࠦࠠࠡࠢࡕࡩࡹࡻࡲ࡯ࡵࠣࡥࠥࡺࡵࡱ࡮ࡨࠤ࠭ࡺࡥࡴࡶࡢࡪࡷࡧ࡭ࡦࡹࡲࡶࡰࡥࡳࡵࡣࡷࡩ࠱ࠦࡴࡦࡵࡷࡣ࡭ࡵ࡯࡬ࡡࡶࡸࡦࡺࡥࠪࠢࡲࡶࠥ࠮ࡎࡰࡰࡨ࠰ࠥࡔ࡯࡯ࡧࠬࠤ࡮࡬ࠠ࡯ࡱࡷࠤࡸ࡫ࡴ࠯ࠌࠣࠤࠥࠦࠢࠣࠤᚋ")
    return (
        getattr(_11ll1l11l1l_opy_, bstack11l1l_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࡤࡹࡴࡢࡶࡨࠫᚌ"), None),
        getattr(_11ll1l11l1l_opy_, bstack11l1l_opy_ (u"ࠬࡺࡥࡴࡶࡢ࡬ࡴࡵ࡫ࡠࡵࡷࡥࡹ࡫ࠧᚍ"), None)
    )
class bstack1ll111ll1_opy_:
    bstack11l1l_opy_ (u"ࠨࠢࠣࠌࠣࠤࠥࠦࡆࡪ࡮ࡨ࡙ࡵࡲ࡯ࡢࡦࡨࡶࠥࡶࡲࡰࡸ࡬ࡨࡪࡹࠠࡧࡷࡱࡧࡹ࡯࡯࡯ࡣ࡯࡭ࡹࡿࠠࡵࡱࠣࡹࡵࡲ࡯ࡢࡦࠣࡥࡳࠦࡡࡵࡶࡤࡧ࡭ࡳࡥ࡯ࡶࠣࡦࡦࡹࡥࡥࠢࡲࡲࠥࡺࡨࡦࠢࡪ࡭ࡻ࡫࡮ࠡࡨ࡬ࡰࡪࠦࡰࡢࡶ࡫࠲ࠏࠦࠠࠡࠢࡌࡸࠥࡹࡵࡱࡲࡲࡶࡹࡹࠠࡣࡱࡷ࡬ࠥࡲ࡯ࡤࡣ࡯ࠤ࡫࡯࡬ࡦࠢࡳࡥࡹ࡮ࡳࠡࡣࡱࡨࠥࡎࡔࡕࡒ࠲ࡌ࡙࡚ࡐࡔࠢࡘࡖࡑࡹࠬࠡࡣࡱࡨࠥࡩ࡯ࡱ࡫ࡨࡷࠥࡺࡨࡦࠢࡩ࡭ࡱ࡫ࠠࡪࡰࡷࡳࠥࡧࠠࡥࡧࡶ࡭࡬ࡴࡡࡵࡧࡧࠎࠥࠦࠠࠡࡦ࡬ࡶࡪࡩࡴࡰࡴࡼࠤࡼ࡯ࡴࡩ࡫ࡱࠤࡹ࡮ࡥࠡࡷࡶࡩࡷ࠭ࡳࠡࡪࡲࡱࡪࠦࡦࡰ࡮ࡧࡩࡷࠦࡵ࡯ࡦࡨࡶࠥࢄ࠯࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠯ࡖࡲ࡯ࡳࡦࡪࡥࡥࡃࡷࡸࡦࡩࡨ࡮ࡧࡱࡸࡸ࠴ࠊࠡࠢࠣࠤࡎ࡬ࠠࡢࡰࠣࡳࡵࡺࡩࡰࡰࡤࡰࠥࡧࡴࡵࡣࡦ࡬ࡲ࡫࡮ࡵࠢࡳࡥࡷࡧ࡭ࡦࡶࡨࡶࠥ࠮ࡩ࡯ࠢࡍࡗࡔࡔࠠࡧࡱࡵࡱࡦࡺࠩࠡ࡫ࡶࠤࡵࡸ࡯ࡷ࡫ࡧࡩࡩࠦࡡ࡯ࡦࠣࡧࡴࡴࡴࡢ࡫ࡱࡷࠥࡧࠠࡵࡴࡸࡸ࡭ࡿࠠࡷࡣ࡯ࡹࡪࠐࠠࠡࠢࠣࡪࡴࡸࠠࡵࡪࡨࠤࡰ࡫ࡹࠡࠤࡥࡹ࡮ࡲࡤࡂࡶࡷࡥࡨ࡮࡭ࡦࡰࡷࠦ࠱ࠦࡴࡩࡧࠣࡪ࡮ࡲࡥࠡࡹ࡬ࡰࡱࠦࡢࡦࠢࡳࡰࡦࡩࡥࡥࠢ࡬ࡲࠥࡺࡨࡦࠢࠥࡆࡺ࡯࡬ࡥࡎࡨࡺࡪࡲࠢࠡࡨࡲࡰࡩ࡫ࡲ࠼ࠢࡲࡸ࡭࡫ࡲࡸ࡫ࡶࡩ࠱ࠐࠠࠡࠢࠣ࡭ࡹࠦࡤࡦࡨࡤࡹࡱࡺࡳࠡࡶࡲࠤ࡚ࠧࡥࡴࡶࡏࡩࡻ࡫࡬ࠣ࠰ࠍࠤࠥࠦࠠࡕࡪ࡬ࡷࠥࡼࡥࡳࡵ࡬ࡳࡳࠦ࡯ࡧࠢࡤࡨࡩࡥࡡࡵࡶࡤࡧ࡭ࡳࡥ࡯ࡶࠣ࡭ࡸࠦࡡࠡࡸࡲ࡭ࡩࠦ࡭ࡦࡶ࡫ࡳࡩ⠚ࡩࡵࠢ࡫ࡥࡳࡪ࡬ࡦࡵࠣࡥࡱࡲࠠࡦࡴࡵࡳࡷࡹࠠࡨࡴࡤࡧࡪ࡬ࡵ࡭࡮ࡼࠤࡧࡿࠠ࡭ࡱࡪ࡫࡮ࡴࡧࠋࠢࠣࠤࠥࡺࡨࡦ࡯ࠣࡥࡳࡪࠠࡴ࡫ࡰࡴࡱࡿࠠࡳࡧࡷࡹࡷࡴࡩ࡯ࡩࠣࡻ࡮ࡺࡨࡰࡷࡷࠤࡹ࡮ࡲࡰࡹ࡬ࡲ࡬ࠦࡥࡹࡥࡨࡴࡹ࡯࡯࡯ࡵ࠱ࠎࠥࠦࠠࠡࠤࠥࠦᚎ")
    @staticmethod
    def upload_attachment(bstack11ll1l1l111_opy_: str, *bstack11ll1l1l11l_opy_) -> None:
        if not bstack11ll1l1l111_opy_ or not bstack11ll1l1l111_opy_.strip():
            logger.error(bstack11l1l_opy_ (u"ࠢࡢࡦࡧࡣࡦࡺࡴࡢࡥ࡫ࡱࡪࡴࡴࠡࡨࡤ࡭ࡱ࡫ࡤ࠻ࠢࡓࡶࡴࡼࡩࡥࡧࡧࠤ࡫࡯࡬ࡦࠢࡳࡥࡹ࡮ࠠࡪࡵࠣࡩࡲࡶࡴࡺࠢࡲࡶࠥࡔ࡯࡯ࡧ࠱ࠦᚏ"))
            return
        bstack11ll11llll1_opy_ = bstack11ll1l1l11l_opy_[0] if bstack11ll1l1l11l_opy_ and len(bstack11ll1l1l11l_opy_) > 0 else None
        bstack11ll1l11ll1_opy_ = None
        test_framework_state, test_hook_state = bstack11ll1l1l1ll_opy_()
        try:
            if bstack11ll1l1l111_opy_.startswith(bstack11l1l_opy_ (u"ࠣࡪࡷࡸࡵࡀ࠯࠰ࠤᚐ")) or bstack11ll1l1l111_opy_.startswith(bstack11l1l_opy_ (u"ࠤ࡫ࡸࡹࡶࡳ࠻࠱࠲ࠦᚑ")):
                logger.debug(bstack11l1l_opy_ (u"ࠥࡔࡦࡺࡨࠡ࡫ࡶࠤ࡮ࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡤࠡࡣࡶࠤ࡚ࡘࡌ࠼ࠢࡧࡳࡼࡴ࡬ࡰࡣࡧ࡭ࡳ࡭ࠠࡵࡪࡨࠤ࡫࡯࡬ࡦ࠰ࠥᚒ"))
                url = bstack11ll1l1l111_opy_
                bstack11ll1l111l1_opy_ = str(uuid.uuid4())
                bstack11ll1l1ll1l_opy_ = os.path.basename(urllib.request.urlparse(url).path)
                if not bstack11ll1l1ll1l_opy_ or not bstack11ll1l1ll1l_opy_.strip():
                    bstack11ll1l1ll1l_opy_ = bstack11ll1l111l1_opy_
                temp_file = tempfile.NamedTemporaryFile(delete=False,
                                                        prefix=bstack11l1l_opy_ (u"ࠦࡺࡶ࡬ࡰࡣࡧࡣࠧᚓ") + bstack11ll1l111l1_opy_ + bstack11l1l_opy_ (u"ࠧࡥࠢᚔ"),
                                                        suffix=bstack11l1l_opy_ (u"ࠨ࡟ࠣᚕ") + bstack11ll1l1ll1l_opy_)
                with urllib.request.urlopen(url) as response, open(temp_file.name, bstack11l1l_opy_ (u"ࠧࡸࡤࠪᚖ")) as out_file:
                    shutil.copyfileobj(response, out_file)
                bstack11ll1l11ll1_opy_ = Path(temp_file.name)
                logger.debug(bstack11l1l_opy_ (u"ࠣࡆࡲࡻࡳࡲ࡯ࡢࡦࡨࡨࠥ࡬ࡩ࡭ࡧࠣࡸࡴࠦࡴࡦ࡯ࡳࡳࡷࡧࡲࡺࠢ࡯ࡳࡨࡧࡴࡪࡱࡱ࠾ࠥࢁࡽࠣᚗ").format(bstack11ll1l11ll1_opy_))
            else:
                bstack11ll1l11ll1_opy_ = Path(bstack11ll1l1l111_opy_)
                logger.debug(bstack11l1l_opy_ (u"ࠤࡓࡥࡹ࡮ࠠࡪࡵࠣ࡭ࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡪࠠࡢࡵࠣࡰࡴࡩࡡ࡭ࠢࡩ࡭ࡱ࡫࠺ࠡࡽࢀࠦᚘ").format(bstack11ll1l11ll1_opy_))
        except Exception as e:
            logger.error(bstack11l1l_opy_ (u"ࠥࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦ࡯ࡣࡶࡤ࡭ࡳࠦࡦࡪ࡮ࡨࠤ࡫ࡸ࡯࡮ࠢࡳࡥࡹ࡮࠯ࡖࡔࡏ࠾ࠥࢁࡽࠣᚙ").format(e))
            return
        if bstack11ll1l11ll1_opy_ is None or not bstack11ll1l11ll1_opy_.exists():
            logger.error(bstack11l1l_opy_ (u"ࠦࡘࡵࡵࡳࡥࡨࠤ࡫࡯࡬ࡦࠢࡧࡳࡪࡹࠠ࡯ࡱࡷࠤࡪࡾࡩࡴࡶ࠽ࠤࢀࢃࠢᚚ").format(bstack11ll1l11ll1_opy_))
            return
        if bstack11ll1l11ll1_opy_.stat().st_size > bstack11ll1l1111l_opy_:
            logger.error(bstack11l1l_opy_ (u"ࠧࡌࡩ࡭ࡧࠣࡷ࡮ࢀࡥࠡࡧࡻࡧࡪ࡫ࡤࡴࠢࡰࡥࡽ࡯࡭ࡶ࡯ࠣࡥࡱࡲ࡯ࡸࡧࡧࠤࡸ࡯ࡺࡦࠢࡲࡪࠥࢁࡽࠣ᚛").format(bstack11ll1l1111l_opy_))
            return
        bstack11ll1l11111_opy_ = bstack11l1l_opy_ (u"ࠨࡔࡦࡵࡷࡐࡪࡼࡥ࡭ࠤ᚜")
        if bstack11ll11llll1_opy_:
            try:
                params = json.loads(bstack11ll11llll1_opy_)
                if bstack11l1l_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡇࡴࡵࡣࡦ࡬ࡲ࡫࡮ࡵࠤ᚝") in params and params.get(bstack11l1l_opy_ (u"ࠣࡤࡸ࡭ࡱࡪࡁࡵࡶࡤࡧ࡭ࡳࡥ࡯ࡶࠥ᚞")) is True:
                    bstack11ll1l11111_opy_ = bstack11l1l_opy_ (u"ࠤࡅࡹ࡮ࡲࡤࡍࡧࡹࡩࡱࠨ᚟")
            except Exception as bstack11ll1l1l1l1_opy_:
                logger.error(bstack11l1l_opy_ (u"ࠥࡎࡘࡕࡎࠡࡲࡤࡶࡸ࡯࡮ࡨࠢࡨࡶࡷࡵࡲࠡ࡫ࡱࠤࡦࡺࡴࡢࡥ࡫ࡱࡪࡴࡴࡑࡣࡵࡥࡲࡹ࠺ࠡࡽࢀࠦᚠ").format(bstack11ll1l1l1l1_opy_))
        bstack11ll1l1ll11_opy_ = False
        from browserstack_sdk.sdk_cli.bstack1ll1lll1ll1_opy_ import bstack1ll1l11llll_opy_
        if test_framework_state in bstack1ll1l11llll_opy_.bstack11lllllllll_opy_:
            if bstack11ll1l11111_opy_ == bstack11lll111lll_opy_:
                bstack11ll1l1ll11_opy_ = True
            bstack11ll1l11111_opy_ = bstack11lll11l1ll_opy_
        try:
            platform_index = os.environ[bstack11l1l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡔࡑࡇࡔࡇࡑࡕࡑࡤࡏࡎࡅࡇ࡛ࠫᚡ")]
            target_dir = os.path.join(bstack1l1l11llll1_opy_, bstack1l1l111ll11_opy_ + str(platform_index),
                                      bstack11ll1l11111_opy_)
            if bstack11ll1l1ll11_opy_:
                target_dir = os.path.join(target_dir, bstack11ll1l11lll_opy_)
            os.makedirs(target_dir, exist_ok=True)
            logger.debug(bstack11l1l_opy_ (u"ࠧࡉࡲࡦࡣࡷࡩࡩ࠵ࡶࡦࡴ࡬ࡪ࡮࡫ࡤࠡࡶࡤࡶ࡬࡫ࡴࠡࡦ࡬ࡶࡪࡩࡴࡰࡴࡼ࠾ࠥࢁࡽࠣᚢ").format(target_dir))
            file_name = os.path.basename(bstack11ll1l11ll1_opy_)
            bstack11ll1l11l11_opy_ = os.path.join(target_dir, file_name)
            if os.path.exists(bstack11ll1l11l11_opy_):
                base_name, extension = os.path.splitext(file_name)
                bstack11ll1l111ll_opy_ = 1
                while os.path.exists(os.path.join(target_dir, base_name + str(bstack11ll1l111ll_opy_) + extension)):
                    bstack11ll1l111ll_opy_ += 1
                bstack11ll1l11l11_opy_ = os.path.join(target_dir, base_name + str(bstack11ll1l111ll_opy_) + extension)
            shutil.copy(bstack11ll1l11ll1_opy_, bstack11ll1l11l11_opy_)
            logger.info(bstack11l1l_opy_ (u"ࠨࡆࡪ࡮ࡨࠤࡸࡻࡣࡤࡧࡶࡷ࡫ࡻ࡬࡭ࡻࠣࡧࡴࡶࡩࡦࡦࠣࡸࡴࡀࠠࡼࡿࠥᚣ").format(bstack11ll1l11l11_opy_))
        except Exception as e:
            logger.error(bstack11l1l_opy_ (u"ࠢࡆࡴࡵࡳࡷࠦ࡭ࡰࡸ࡬ࡲ࡬ࠦࡦࡪ࡮ࡨࠤࡹࡵࠠࡵࡣࡵ࡫ࡪࡺࠠࡥ࡫ࡵࡩࡨࡺ࡯ࡳࡻ࠽ࠤࢀࢃࠢᚤ").format(e))
            return
        finally:
            if bstack11ll1l1l111_opy_.startswith(bstack11l1l_opy_ (u"ࠣࡪࡷࡸࡵࡀ࠯࠰ࠤᚥ")) or bstack11ll1l1l111_opy_.startswith(bstack11l1l_opy_ (u"ࠤ࡫ࡸࡹࡶࡳ࠻࠱࠲ࠦᚦ")):
                try:
                    if bstack11ll1l11ll1_opy_ is not None and bstack11ll1l11ll1_opy_.exists():
                        bstack11ll1l11ll1_opy_.unlink()
                        logger.debug(bstack11l1l_opy_ (u"ࠥࡘࡪࡳࡰࡰࡴࡤࡶࡾࠦࡦࡪ࡮ࡨࠤࡩ࡫࡬ࡦࡶࡨࡨ࠿ࠦࡻࡾࠤᚧ").format(bstack11ll1l11ll1_opy_))
                except Exception as ex:
                    logger.error(bstack11l1l_opy_ (u"ࠦࡊࡸࡲࡰࡴࠣࡨࡪࡲࡥࡵ࡫ࡱ࡫ࠥࡺࡥ࡮ࡲࡲࡶࡦࡸࡹࠡࡨ࡬ࡰࡪࡀࠠࡼࡿࠥᚨ").format(ex))
    @staticmethod
    def bstack1ll1ll1l1_opy_() -> None:
        bstack11l1l_opy_ (u"ࠧࠨࠢࠋࠢࠣࠤࠥࠦࠠࠡࠢࡇࡩࡱ࡫ࡴࡦࡵࠣࡥࡱࡲࠠࡧࡱ࡯ࡨࡪࡸࡳࠡࡹ࡫ࡳࡸ࡫ࠠ࡯ࡣࡰࡩࡸࠦࡳࡵࡣࡵࡸࠥࡽࡩࡵࡪ࡚ࠣࠦࡶ࡬ࡰࡣࡧࡩࡩࡇࡴࡵࡣࡦ࡬ࡲ࡫࡮ࡵࡵ࠰ࠦࠥ࡬࡯࡭࡮ࡲࡻࡪࡪࠠࡣࡻࠣࡥࠥࡴࡵ࡮ࡤࡨࡶࠥ࡯࡮ࠋࠢࠣࠤࠥࠦࠠࠡࠢࡷ࡬ࡪࠦࡵࡴࡧࡵࠫࡸࠦࡾ࠰࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࠡࡦ࡬ࡶࡪࡩࡴࡰࡴࡼ࠲ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠢࠣࠤᚩ")
        bstack11ll11lllll_opy_ = bstack1l1l1ll11l1_opy_()
        pattern = re.compile(bstack11l1l_opy_ (u"ࡸࠢࡖࡲ࡯ࡳࡦࡪࡥࡥࡃࡷࡸࡦࡩࡨ࡮ࡧࡱࡸࡸ࠳࡜ࡥ࠭ࠥᚪ"))
        if os.path.exists(bstack11ll11lllll_opy_):
            for item in os.listdir(bstack11ll11lllll_opy_):
                bstack11ll1l1llll_opy_ = os.path.join(bstack11ll11lllll_opy_, item)
                if os.path.isdir(bstack11ll1l1llll_opy_) and pattern.fullmatch(item):
                    try:
                        shutil.rmtree(bstack11ll1l1llll_opy_)
                    except Exception as e:
                        logger.error(bstack11l1l_opy_ (u"ࠢࡆࡴࡵࡳࡷࠦࡤࡦ࡮ࡨࡸ࡮ࡴࡧࠡࡦ࡬ࡶࡪࡩࡴࡰࡴࡼ࠾ࠥࢁࡽࠣᚫ").format(e))
        else:
            logger.info(bstack11l1l_opy_ (u"ࠣࡖ࡫ࡩࠥࡪࡩࡳࡧࡦࡸࡴࡸࡹࠡࡦࡲࡩࡸࠦ࡮ࡰࡶࠣࡩࡽ࡯ࡳࡵ࠼ࠣࡿࢂࠨᚬ").format(bstack11ll11lllll_opy_))