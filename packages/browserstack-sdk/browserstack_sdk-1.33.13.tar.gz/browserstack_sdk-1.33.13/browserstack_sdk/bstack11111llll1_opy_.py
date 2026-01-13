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
bstack11l1l_opy_ (u"ࠢࠣࠤࠍࡔࡾࡺࡥࡴࡶࠣࡸࡪࡹࡴࠡࡥࡲࡰࡱ࡫ࡣࡵ࡫ࡲࡲࠥ࡮ࡥ࡭ࡲࡨࡶࠥࡻࡳࡪࡰࡪࠤࡩ࡯ࡲࡦࡥࡷࠤࡵࡿࡴࡦࡵࡷࠤ࡭ࡵ࡯࡬ࡵ࠱ࠎࠧࠨࠢၯ")
import pytest
import io
import os
from contextlib import redirect_stdout, redirect_stderr
import subprocess
import sys
def bstack11111lllll_opy_(bstack11111ll1l1_opy_=None, bstack11111lll11_opy_=None):
    bstack11l1l_opy_ (u"ࠣࠤࠥࠎࠥࠦࠠࠡࡅࡲࡰࡱ࡫ࡣࡵࠢࡳࡽࡹ࡫ࡳࡵࠢࡷࡩࡸࡺࡳࠡࡷࡶ࡭ࡳ࡭ࠠࡱࡻࡷࡩࡸࡺࠧࡴࠢ࡬ࡲࡹ࡫ࡲ࡯ࡣ࡯ࠤࡆࡖࡉࡴ࠰ࠍࠤࠥࠦࠠࡂࡴࡪࡷ࠿ࠐࠠࠡࠢࠣࠤࠥࠦࠠࡵࡧࡶࡸࡤࡧࡲࡨࡵࠣࠬࡱ࡯ࡳࡵ࠮ࠣࡳࡵࡺࡩࡰࡰࡤࡰ࠮ࡀࠠࡄࡱࡰࡴࡱ࡫ࡴࡦࠢ࡯࡭ࡸࡺࠠࡰࡨࠣࡴࡾࡺࡥࡴࡶࠣࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸࠦࡩ࡯ࡥ࡯ࡹࡩ࡯࡮ࡨࠢࡳࡥࡹ࡮ࡳࠡࡣࡱࡨࠥ࡬࡬ࡢࡩࡶ࠲ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤ࡚ࠥࡡ࡬ࡧࡶࠤࡵࡸࡥࡤࡧࡧࡩࡳࡩࡥࠡࡱࡹࡩࡷࠦࡴࡦࡵࡷࡣࡵࡧࡴࡩࡵࠣ࡭࡫ࠦࡢࡰࡶ࡫ࠤࡦࡸࡥࠡࡲࡵࡳࡻ࡯ࡤࡦࡦ࠱ࠎࠥࠦࠠࠡࠢࠣࠤࠥࡺࡥࡴࡶࡢࡴࡦࡺࡨࡴࠢࠫࡰ࡮ࡹࡴࠡࡱࡵࠤࡸࡺࡲ࠭ࠢࡲࡴࡹ࡯࡯࡯ࡣ࡯࠭࠿ࠦࡔࡦࡵࡷࠤ࡫࡯࡬ࡦࠪࡶ࠭࠴ࡪࡩࡳࡧࡦࡸࡴࡸࡹࠩ࡫ࡨࡷ࠮ࠦࡴࡰࠢࡦࡳࡱࡲࡥࡤࡶࠣࡪࡷࡵ࡭࠯ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࡇࡦࡴࠠࡣࡧࠣࡥࠥࡹࡩ࡯ࡩ࡯ࡩࠥࡶࡡࡵࡪࠣࡷࡹࡸࡩ࡯ࡩࠣࡳࡷࠦ࡬ࡪࡵࡷࠤࡴ࡬ࠠࡱࡣࡷ࡬ࡸ࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࡋࡪࡲࡴࡸࡥࡥࠢ࡬ࡪࠥࡺࡥࡴࡶࡢࡥࡷ࡭ࡳࠡ࡫ࡶࠤࡵࡸ࡯ࡷ࡫ࡧࡩࡩ࠴ࠊࠡࠢࠣࠤࡗ࡫ࡴࡶࡴࡱࡷ࠿ࠐࠠࠡࠢࠣࠤࠥࠦࠠࡥ࡫ࡦࡸ࠿ࠦࡃࡰ࡮࡯ࡩࡨࡺࡩࡰࡰࠣࡶࡪࡹࡵ࡭ࡶࡶࠤࡼ࡯ࡴࡩࠢ࡮ࡩࡾࡹ࠺ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦ࠭ࠡࡵࡸࡧࡨ࡫ࡳࡴࠢࠫࡦࡴࡵ࡬ࠪࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠ࠮ࠢࡦࡳࡺࡴࡴࠡࠪ࡬ࡲࡹ࠯ࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥ࠳ࠠ࡯ࡱࡧࡩ࡮ࡪࡳࠡࠪ࡯࡭ࡸࡺࠩࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦ࠭ࠡࡶࡨࡷࡹࡥࡦࡪ࡮ࡨࡷࠥ࠮࡬ࡪࡵࡷ࠭ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣ࠱ࠥ࡫ࡲࡳࡱࡵࠤ࠭ࡹࡴࡳࠫࠍࠤࠥࠦࠠࠣࠤࠥၰ")
    try:
        bstack11111lll1l_opy_ = os.getenv(bstack11l1l_opy_ (u"ࠤࡓ࡝࡙ࡋࡓࡕࡡࡆ࡙ࡗࡘࡅࡏࡖࡢࡘࡊ࡙ࡔࠣၱ")) is not None
        if bstack11111ll1l1_opy_ is not None:
            args = list(bstack11111ll1l1_opy_)
        elif bstack11111lll11_opy_ is not None:
            if isinstance(bstack11111lll11_opy_, str):
                args = [bstack11111lll11_opy_]
            elif isinstance(bstack11111lll11_opy_, list):
                args = list(bstack11111lll11_opy_)
            else:
                args = [bstack11l1l_opy_ (u"ࠥ࠲ࠧၲ")]
        else:
            args = [bstack11l1l_opy_ (u"ࠦ࠳ࠨၳ")]
        if bstack11111lll1l_opy_:
            return _11111l1lll_opy_(args)
        bstack11111ll1ll_opy_ = args + [
            bstack11l1l_opy_ (u"ࠧ࠳࠭ࡤࡱ࡯ࡰࡪࡩࡴ࠮ࡱࡱࡰࡾࠨၴ"),
            bstack11l1l_opy_ (u"ࠨ࠭࠮ࡳࡸ࡭ࡪࡺࠢၵ")
        ]
        class bstack11111ll111_opy_:
            bstack11l1l_opy_ (u"ࠢࠣࠤࡓࡽࡹ࡫ࡳࡵࠢࡳࡰࡺ࡭ࡩ࡯ࠢࡷ࡬ࡦࡺࠠࡤࡣࡳࡸࡺࡸࡥࡴࠢࡦࡳࡱࡲࡥࡤࡶࡨࡨࠥࡺࡥࡴࡶࠣ࡭ࡹ࡫࡭ࡴ࠰ࠥࠦࠧၶ")
            def __init__(self):
                self.bstack11111l1l11_opy_ = []
                self.test_files = set()
                self.bstack11111ll11l_opy_ = None
            def pytest_collection_finish(self, session):
                bstack11l1l_opy_ (u"ࠣࠤࠥࡌࡴࡵ࡫ࠡࡥࡤࡰࡱ࡫ࡤࠡࡣࡩࡸࡪࡸࠠࡤࡱ࡯ࡰࡪࡩࡴࡪࡱࡱࠤ࡮ࡹࠠࡧ࡫ࡱ࡭ࡸ࡮ࡥࡥ࠰ࠥࠦࠧၷ")
                try:
                    for item in session.items:
                        nodeid = item.nodeid
                        self.bstack11111l1l11_opy_.append(nodeid)
                        if bstack11l1l_opy_ (u"ࠤ࠽࠾ࠧၸ") in nodeid:
                            file_path = nodeid.split(bstack11l1l_opy_ (u"ࠥ࠾࠿ࠨၹ"), 1)[0]
                            if file_path.endswith(bstack11l1l_opy_ (u"ࠫ࠳ࡶࡹࠨၺ")):
                                self.test_files.add(file_path)
                except Exception as e:
                    self.bstack11111ll11l_opy_ = str(e)
        collector = bstack11111ll111_opy_()
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            exit_code = pytest.main(bstack11111ll1ll_opy_, plugins=[collector])
        if collector.bstack11111ll11l_opy_:
            return {bstack11l1l_opy_ (u"ࠧࡹࡵࡤࡥࡨࡷࡸࠨၻ"): False, bstack11l1l_opy_ (u"ࠨࡣࡰࡷࡱࡸࠧၼ"): 0, bstack11l1l_opy_ (u"ࠢ࡯ࡱࡧࡩ࡮ࡪࡳࠣၽ"): [], bstack11l1l_opy_ (u"ࠣࡶࡨࡷࡹࡥࡦࡪ࡮ࡨࡷࠧၾ"): [], bstack11l1l_opy_ (u"ࠤࡨࡶࡷࡵࡲࠣၿ"): bstack11l1l_opy_ (u"ࠥࡇࡴࡲ࡬ࡦࡥࡷ࡭ࡴࡴࠠࡦࡴࡵࡳࡷࡀࠠࡼࡿࠥႀ").format(collector.bstack11111ll11l_opy_)}
        return {
            bstack11l1l_opy_ (u"ࠦࡸࡻࡣࡤࡧࡶࡷࠧႁ"): True,
            bstack11l1l_opy_ (u"ࠧࡩ࡯ࡶࡰࡷࠦႂ"): len(collector.bstack11111l1l11_opy_),
            bstack11l1l_opy_ (u"ࠨ࡮ࡰࡦࡨ࡭ࡩࡹࠢႃ"): collector.bstack11111l1l11_opy_,
            bstack11l1l_opy_ (u"ࠢࡵࡧࡶࡸࡤ࡬ࡩ࡭ࡧࡶࠦႄ"): sorted(collector.test_files),
            bstack11l1l_opy_ (u"ࠣࡧࡻ࡭ࡹࡥࡣࡰࡦࡨࠦႅ"): exit_code
        }
    except Exception as e:
        return {bstack11l1l_opy_ (u"ࠤࡶࡹࡨࡩࡥࡴࡵࠥႆ"): False, bstack11l1l_opy_ (u"ࠥࡧࡴࡻ࡮ࡵࠤႇ"): 0, bstack11l1l_opy_ (u"ࠦࡳࡵࡤࡦ࡫ࡧࡷࠧႈ"): [], bstack11l1l_opy_ (u"ࠧࡺࡥࡴࡶࡢࡪ࡮ࡲࡥࡴࠤႉ"): [], bstack11l1l_opy_ (u"ࠨࡥࡳࡴࡲࡶࠧႊ"): bstack11l1l_opy_ (u"ࠢࡖࡰࡨࡼࡵ࡫ࡣࡵࡧࡧࠤࡪࡸࡲࡰࡴࠣ࡭ࡳࠦࡴࡦࡵࡷࠤࡨࡵ࡬࡭ࡧࡦࡸ࡮ࡵ࡮࠻ࠢࡾࢁࠧႋ").format(e)}
def _11111l1lll_opy_(args):
    bstack11l1l_opy_ (u"ࠣࠤࠥࡍࡸࡵ࡬ࡢࡶࡨࡨࠥࡩ࡯࡭࡮ࡨࡧࡹ࡯࡯࡯ࠢࡨࡼࡪࡩࡵࡵࡧࡧࠤ࡮ࡴࠠࡢࠢࡶࡩࡵࡧࡲࡢࡶࡨࠤࡕࡿࡴࡩࡱࡱࠤࡵࡸ࡯ࡤࡧࡶࡷࠥࡺ࡯ࠡࡣࡹࡳ࡮ࡪࠠ࡯ࡧࡶࡸࡪࡪࠠࡱࡻࡷࡩࡸࡺࠠࡪࡵࡶࡹࡪࡹ࠮ࠣࠤࠥႌ")
    bstack11111l1l1l_opy_ = [sys.executable, bstack11l1l_opy_ (u"ࠤ࠰ࡱႍࠧ"), bstack11l1l_opy_ (u"ࠥࡴࡾࡺࡥࡴࡶࠥႎ"), bstack11l1l_opy_ (u"ࠦ࠲࠳ࡣࡰ࡮࡯ࡩࡨࡺ࠭ࡰࡰ࡯ࡽࠧႏ"), bstack11l1l_opy_ (u"ࠧ࠳࠭ࡲࡷ࡬ࡩࡹࠨ႐")]
    bstack11111l1ll1_opy_ = [a for a in args if a not in (bstack11l1l_opy_ (u"ࠨ࠭࠮ࡥࡲࡰࡱ࡫ࡣࡵ࠯ࡲࡲࡱࡿࠢ႑"), bstack11l1l_opy_ (u"ࠢ࠮࠯ࡴࡹ࡮࡫ࡴࠣ႒"), bstack11l1l_opy_ (u"ࠣ࠯ࡴࠦ႓"))]
    cmd = bstack11111l1l1l_opy_ + bstack11111l1ll1_opy_
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, env=os.environ.copy())
        stdout = proc.stdout.splitlines()
        bstack11111l1l11_opy_ = []
        test_files = set()
        for line in stdout:
            line = line.strip()
            if not line or bstack11l1l_opy_ (u"ࠤࠣࡧࡴࡲ࡬ࡦࡥࡷࡩࡩࠨ႔") in line.lower():
                continue
            if bstack11l1l_opy_ (u"ࠥ࠾࠿ࠨ႕") in line:
                bstack11111l1l11_opy_.append(line)
                file_path = line.split(bstack11l1l_opy_ (u"ࠦ࠿ࡀࠢ႖"), 1)[0]
                if file_path.endswith(bstack11l1l_opy_ (u"ࠬ࠴ࡰࡺࠩ႗")):
                    test_files.add(file_path)
        success = proc.returncode in (0, 5)
        return {
            bstack11l1l_opy_ (u"ࠨࡳࡶࡥࡦࡩࡸࡹࠢ႘"): success,
            bstack11l1l_opy_ (u"ࠢࡤࡱࡸࡲࡹࠨ႙"): len(bstack11111l1l11_opy_),
            bstack11l1l_opy_ (u"ࠣࡰࡲࡨࡪ࡯ࡤࡴࠤႚ"): bstack11111l1l11_opy_,
            bstack11l1l_opy_ (u"ࠤࡷࡩࡸࡺ࡟ࡧ࡫࡯ࡩࡸࠨႛ"): sorted(test_files),
            bstack11l1l_opy_ (u"ࠥࡩࡽ࡯ࡴࡠࡥࡲࡨࡪࠨႜ"): proc.returncode,
            bstack11l1l_opy_ (u"ࠦࡪࡸࡲࡰࡴࠥႝ"): None if success else bstack11l1l_opy_ (u"࡙ࠧࡵࡣࡲࡵࡳࡨ࡫ࡳࡴࠢࡦࡳࡱࡲࡥࡤࡶ࡬ࡳࡳࠦࡦࡢ࡫࡯ࡩࡩࠦࠨࡦࡺ࡬ࡸࠥࢁࡽࠪࠤ႞").format(proc.returncode)
        }
    except Exception as e:
        return {bstack11l1l_opy_ (u"ࠨࡳࡶࡥࡦࡩࡸࡹࠢ႟"): False, bstack11l1l_opy_ (u"ࠢࡤࡱࡸࡲࡹࠨႠ"): 0, bstack11l1l_opy_ (u"ࠣࡰࡲࡨࡪ࡯ࡤࡴࠤႡ"): [], bstack11l1l_opy_ (u"ࠤࡷࡩࡸࡺ࡟ࡧ࡫࡯ࡩࡸࠨႢ"): [], bstack11l1l_opy_ (u"ࠥࡩࡷࡸ࡯ࡳࠤႣ"): bstack11l1l_opy_ (u"ࠦࡘࡻࡢࡱࡴࡲࡧࡪࡹࡳࠡࡥࡲࡰࡱ࡫ࡣࡵ࡫ࡲࡲࠥ࡫ࡲࡳࡱࡵ࠾ࠥࢁࡽࠣႤ").format(e)}