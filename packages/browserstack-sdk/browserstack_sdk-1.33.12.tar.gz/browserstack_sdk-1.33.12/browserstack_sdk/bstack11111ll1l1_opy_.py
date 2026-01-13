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
bstack11ll1_opy_ (u"ࠣࠤࠥࠎࡕࡿࡴࡦࡵࡷࠤࡹ࡫ࡳࡵࠢࡦࡳࡱࡲࡥࡤࡶ࡬ࡳࡳࠦࡨࡦ࡮ࡳࡩࡷࠦࡵࡴ࡫ࡱ࡫ࠥࡪࡩࡳࡧࡦࡸࠥࡶࡹࡵࡧࡶࡸࠥ࡮࡯ࡰ࡭ࡶ࠲ࠏࠨࠢࠣၰ")
import pytest
import io
import os
from contextlib import redirect_stdout, redirect_stderr
import subprocess
import sys
def bstack11111lllll_opy_(bstack11111lll1l_opy_=None, bstack11111l1l11_opy_=None):
    bstack11ll1_opy_ (u"ࠤࠥࠦࠏࠦࠠࠡࠢࡆࡳࡱࡲࡥࡤࡶࠣࡴࡾࡺࡥࡴࡶࠣࡸࡪࡹࡴࡴࠢࡸࡷ࡮ࡴࡧࠡࡲࡼࡸࡪࡹࡴࠨࡵࠣ࡭ࡳࡺࡥࡳࡰࡤࡰࠥࡇࡐࡊࡵ࠱ࠎࠥࠦࠠࠡࡃࡵ࡫ࡸࡀࠊࠡࠢࠣࠤࠥࠦࠠࠡࡶࡨࡷࡹࡥࡡࡳࡩࡶࠤ࠭ࡲࡩࡴࡶ࠯ࠤࡴࡶࡴࡪࡱࡱࡥࡱ࠯࠺ࠡࡅࡲࡱࡵࡲࡥࡵࡧࠣࡰ࡮ࡹࡴࠡࡱࡩࠤࡵࡿࡴࡦࡵࡷࠤࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠠࡪࡰࡦࡰࡺࡪࡩ࡯ࡩࠣࡴࡦࡺࡨࡴࠢࡤࡲࡩࠦࡦ࡭ࡣࡪࡷ࠳ࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࡔࡢ࡭ࡨࡷࠥࡶࡲࡦࡥࡨࡨࡪࡴࡣࡦࠢࡲࡺࡪࡸࠠࡵࡧࡶࡸࡤࡶࡡࡵࡪࡶࠤ࡮࡬ࠠࡣࡱࡷ࡬ࠥࡧࡲࡦࠢࡳࡶࡴࡼࡩࡥࡧࡧ࠲ࠏࠦࠠࠡࠢࠣࠤࠥࠦࡴࡦࡵࡷࡣࡵࡧࡴࡩࡵࠣࠬࡱ࡯ࡳࡵࠢࡲࡶࠥࡹࡴࡳ࠮ࠣࡳࡵࡺࡩࡰࡰࡤࡰ࠮ࡀࠠࡕࡧࡶࡸࠥ࡬ࡩ࡭ࡧࠫࡷ࠮࠵ࡤࡪࡴࡨࡧࡹࡵࡲࡺࠪ࡬ࡩࡸ࠯ࠠࡵࡱࠣࡧࡴࡲ࡬ࡦࡥࡷࠤ࡫ࡸ࡯࡮࠰ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࡈࡧ࡮ࠡࡤࡨࠤࡦࠦࡳࡪࡰࡪࡰࡪࠦࡰࡢࡶ࡫ࠤࡸࡺࡲࡪࡰࡪࠤࡴࡸࠠ࡭࡫ࡶࡸࠥࡵࡦࠡࡲࡤࡸ࡭ࡹ࠮ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࡌ࡫ࡳࡵࡲࡦࡦࠣ࡭࡫ࠦࡴࡦࡵࡷࡣࡦࡸࡧࡴࠢ࡬ࡷࠥࡶࡲࡰࡸ࡬ࡨࡪࡪ࠮ࠋࠢࠣࠤࠥࡘࡥࡵࡷࡵࡲࡸࡀࠊࠡࠢࠣࠤࠥࠦࠠࠡࡦ࡬ࡧࡹࡀࠠࡄࡱ࡯ࡰࡪࡩࡴࡪࡱࡱࠤࡷ࡫ࡳࡶ࡮ࡷࡷࠥࡽࡩࡵࡪࠣ࡯ࡪࡿࡳ࠻ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠ࠮ࠢࡶࡹࡨࡩࡥࡴࡵࠣࠬࡧࡵ࡯࡭ࠫࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡ࠯ࠣࡧࡴࡻ࡮ࡵࠢࠫ࡭ࡳࡺࠩࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦ࠭ࠡࡰࡲࡨࡪ࡯ࡤࡴࠢࠫࡰ࡮ࡹࡴࠪࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠ࠮ࠢࡷࡩࡸࡺ࡟ࡧ࡫࡯ࡩࡸࠦࠨ࡭࡫ࡶࡸ࠮ࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤ࠲ࠦࡥࡳࡴࡲࡶࠥ࠮ࡳࡵࡴࠬࠎࠥࠦࠠࠡࠤࠥࠦၱ")
    try:
        bstack11111lll11_opy_ = os.getenv(bstack11ll1_opy_ (u"ࠥࡔ࡞࡚ࡅࡔࡖࡢࡇ࡚ࡘࡒࡆࡐࡗࡣ࡙ࡋࡓࡕࠤၲ")) is not None
        if bstack11111lll1l_opy_ is not None:
            args = list(bstack11111lll1l_opy_)
        elif bstack11111l1l11_opy_ is not None:
            if isinstance(bstack11111l1l11_opy_, str):
                args = [bstack11111l1l11_opy_]
            elif isinstance(bstack11111l1l11_opy_, list):
                args = list(bstack11111l1l11_opy_)
            else:
                args = [bstack11ll1_opy_ (u"ࠦ࠳ࠨၳ")]
        else:
            args = [bstack11ll1_opy_ (u"ࠧ࠴ࠢၴ")]
        if bstack11111lll11_opy_:
            return _11111l1ll1_opy_(args)
        bstack11111l1lll_opy_ = args + [
            bstack11ll1_opy_ (u"ࠨ࠭࠮ࡥࡲࡰࡱ࡫ࡣࡵ࠯ࡲࡲࡱࡿࠢၵ"),
            bstack11ll1_opy_ (u"ࠢ࠮࠯ࡴࡹ࡮࡫ࡴࠣၶ")
        ]
        class bstack11111ll11l_opy_:
            bstack11ll1_opy_ (u"ࠣࠤࠥࡔࡾࡺࡥࡴࡶࠣࡴࡱࡻࡧࡪࡰࠣࡸ࡭ࡧࡴࠡࡥࡤࡴࡹࡻࡲࡦࡵࠣࡧࡴࡲ࡬ࡦࡥࡷࡩࡩࠦࡴࡦࡵࡷࠤ࡮ࡺࡥ࡮ࡵ࠱ࠦࠧࠨၷ")
            def __init__(self):
                self.bstack11111l1l1l_opy_ = []
                self.test_files = set()
                self.bstack11111ll111_opy_ = None
            def pytest_collection_finish(self, session):
                bstack11ll1_opy_ (u"ࠤࠥࠦࡍࡵ࡯࡬ࠢࡦࡥࡱࡲࡥࡥࠢࡤࡪࡹ࡫ࡲࠡࡥࡲࡰࡱ࡫ࡣࡵ࡫ࡲࡲࠥ࡯ࡳࠡࡨ࡬ࡲ࡮ࡹࡨࡦࡦ࠱ࠦࠧࠨၸ")
                try:
                    for item in session.items:
                        nodeid = item.nodeid
                        self.bstack11111l1l1l_opy_.append(nodeid)
                        if bstack11ll1_opy_ (u"ࠥ࠾࠿ࠨၹ") in nodeid:
                            file_path = nodeid.split(bstack11ll1_opy_ (u"ࠦ࠿ࡀࠢၺ"), 1)[0]
                            if file_path.endswith(bstack11ll1_opy_ (u"ࠬ࠴ࡰࡺࠩၻ")):
                                self.test_files.add(file_path)
                except Exception as e:
                    self.bstack11111ll111_opy_ = str(e)
        collector = bstack11111ll11l_opy_()
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            exit_code = pytest.main(bstack11111l1lll_opy_, plugins=[collector])
        if collector.bstack11111ll111_opy_:
            return {bstack11ll1_opy_ (u"ࠨࡳࡶࡥࡦࡩࡸࡹࠢၼ"): False, bstack11ll1_opy_ (u"ࠢࡤࡱࡸࡲࡹࠨၽ"): 0, bstack11ll1_opy_ (u"ࠣࡰࡲࡨࡪ࡯ࡤࡴࠤၾ"): [], bstack11ll1_opy_ (u"ࠤࡷࡩࡸࡺ࡟ࡧ࡫࡯ࡩࡸࠨၿ"): [], bstack11ll1_opy_ (u"ࠥࡩࡷࡸ࡯ࡳࠤႀ"): bstack11ll1_opy_ (u"ࠦࡈࡵ࡬࡭ࡧࡦࡸ࡮ࡵ࡮ࠡࡧࡵࡶࡴࡸ࠺ࠡࡽࢀࠦႁ").format(collector.bstack11111ll111_opy_)}
        return {
            bstack11ll1_opy_ (u"ࠧࡹࡵࡤࡥࡨࡷࡸࠨႂ"): True,
            bstack11ll1_opy_ (u"ࠨࡣࡰࡷࡱࡸࠧႃ"): len(collector.bstack11111l1l1l_opy_),
            bstack11ll1_opy_ (u"ࠢ࡯ࡱࡧࡩ࡮ࡪࡳࠣႄ"): collector.bstack11111l1l1l_opy_,
            bstack11ll1_opy_ (u"ࠣࡶࡨࡷࡹࡥࡦࡪ࡮ࡨࡷࠧႅ"): sorted(collector.test_files),
            bstack11ll1_opy_ (u"ࠤࡨࡼ࡮ࡺ࡟ࡤࡱࡧࡩࠧႆ"): exit_code
        }
    except Exception as e:
        return {bstack11ll1_opy_ (u"ࠥࡷࡺࡩࡣࡦࡵࡶࠦႇ"): False, bstack11ll1_opy_ (u"ࠦࡨࡵࡵ࡯ࡶࠥႈ"): 0, bstack11ll1_opy_ (u"ࠧࡴ࡯ࡥࡧ࡬ࡨࡸࠨႉ"): [], bstack11ll1_opy_ (u"ࠨࡴࡦࡵࡷࡣ࡫࡯࡬ࡦࡵࠥႊ"): [], bstack11ll1_opy_ (u"ࠢࡦࡴࡵࡳࡷࠨႋ"): bstack11ll1_opy_ (u"ࠣࡗࡱࡩࡽࡶࡥࡤࡶࡨࡨࠥ࡫ࡲࡳࡱࡵࠤ࡮ࡴࠠࡵࡧࡶࡸࠥࡩ࡯࡭࡮ࡨࡧࡹ࡯࡯࡯࠼ࠣࡿࢂࠨႌ").format(e)}
def _11111l1ll1_opy_(args):
    bstack11ll1_opy_ (u"ࠤࠥࠦࡎࡹ࡯࡭ࡣࡷࡩࡩࠦࡣࡰ࡮࡯ࡩࡨࡺࡩࡰࡰࠣࡩࡽ࡫ࡣࡶࡶࡨࡨࠥ࡯࡮ࠡࡣࠣࡷࡪࡶࡡࡳࡣࡷࡩࠥࡖࡹࡵࡪࡲࡲࠥࡶࡲࡰࡥࡨࡷࡸࠦࡴࡰࠢࡤࡺࡴ࡯ࡤࠡࡰࡨࡷࡹ࡫ࡤࠡࡲࡼࡸࡪࡹࡴࠡ࡫ࡶࡷࡺ࡫ࡳ࠯ࠤႍࠥࠦ")
    bstack11111llll1_opy_ = [sys.executable, bstack11ll1_opy_ (u"ࠥ࠱ࡲࠨႎ"), bstack11ll1_opy_ (u"ࠦࡵࡿࡴࡦࡵࡷࠦႏ"), bstack11ll1_opy_ (u"ࠧ࠳࠭ࡤࡱ࡯ࡰࡪࡩࡴ࠮ࡱࡱࡰࡾࠨ႐"), bstack11ll1_opy_ (u"ࠨ࠭࠮ࡳࡸ࡭ࡪࡺࠢ႑")]
    bstack11111ll1ll_opy_ = [a for a in args if a not in (bstack11ll1_opy_ (u"ࠢ࠮࠯ࡦࡳࡱࡲࡥࡤࡶ࠰ࡳࡳࡲࡹࠣ႒"), bstack11ll1_opy_ (u"ࠣ࠯࠰ࡵࡺ࡯ࡥࡵࠤ႓"), bstack11ll1_opy_ (u"ࠤ࠰ࡵࠧ႔"))]
    cmd = bstack11111llll1_opy_ + bstack11111ll1ll_opy_
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, env=os.environ.copy())
        stdout = proc.stdout.splitlines()
        bstack11111l1l1l_opy_ = []
        test_files = set()
        for line in stdout:
            line = line.strip()
            if not line or bstack11ll1_opy_ (u"ࠥࠤࡨࡵ࡬࡭ࡧࡦࡸࡪࡪࠢ႕") in line.lower():
                continue
            if bstack11ll1_opy_ (u"ࠦ࠿ࡀࠢ႖") in line:
                bstack11111l1l1l_opy_.append(line)
                file_path = line.split(bstack11ll1_opy_ (u"ࠧࡀ࠺ࠣ႗"), 1)[0]
                if file_path.endswith(bstack11ll1_opy_ (u"࠭࠮ࡱࡻࠪ႘")):
                    test_files.add(file_path)
        success = proc.returncode in (0, 5)
        return {
            bstack11ll1_opy_ (u"ࠢࡴࡷࡦࡧࡪࡹࡳࠣ႙"): success,
            bstack11ll1_opy_ (u"ࠣࡥࡲࡹࡳࡺࠢႚ"): len(bstack11111l1l1l_opy_),
            bstack11ll1_opy_ (u"ࠤࡱࡳࡩ࡫ࡩࡥࡵࠥႛ"): bstack11111l1l1l_opy_,
            bstack11ll1_opy_ (u"ࠥࡸࡪࡹࡴࡠࡨ࡬ࡰࡪࡹࠢႜ"): sorted(test_files),
            bstack11ll1_opy_ (u"ࠦࡪࡾࡩࡵࡡࡦࡳࡩ࡫ࠢႝ"): proc.returncode,
            bstack11ll1_opy_ (u"ࠧ࡫ࡲࡳࡱࡵࠦ႞"): None if success else bstack11ll1_opy_ (u"ࠨࡓࡶࡤࡳࡶࡴࡩࡥࡴࡵࠣࡧࡴࡲ࡬ࡦࡥࡷ࡭ࡴࡴࠠࡧࡣ࡬ࡰࡪࡪࠠࠩࡧࡻ࡭ࡹࠦࡻࡾࠫࠥ႟").format(proc.returncode)
        }
    except Exception as e:
        return {bstack11ll1_opy_ (u"ࠢࡴࡷࡦࡧࡪࡹࡳࠣႠ"): False, bstack11ll1_opy_ (u"ࠣࡥࡲࡹࡳࡺࠢႡ"): 0, bstack11ll1_opy_ (u"ࠤࡱࡳࡩ࡫ࡩࡥࡵࠥႢ"): [], bstack11ll1_opy_ (u"ࠥࡸࡪࡹࡴࡠࡨ࡬ࡰࡪࡹࠢႣ"): [], bstack11ll1_opy_ (u"ࠦࡪࡸࡲࡰࡴࠥႤ"): bstack11ll1_opy_ (u"࡙ࠧࡵࡣࡲࡵࡳࡨ࡫ࡳࡴࠢࡦࡳࡱࡲࡥࡤࡶ࡬ࡳࡳࠦࡥࡳࡴࡲࡶ࠿ࠦࡻࡾࠤႥ").format(e)}