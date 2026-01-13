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
from bstack_utils.constants import bstack11l1ll1ll11_opy_
def bstack1111l1lll_opy_(bstack11l1ll1ll1l_opy_):
    from browserstack_sdk.sdk_cli.cli import cli
    from bstack_utils.helper import bstack1ll1l111_opy_
    host = bstack1ll1l111_opy_(cli.config, [bstack11ll1_opy_ (u"ࠦࡦࡶࡩࡴࠤ᠍"), bstack11ll1_opy_ (u"ࠧࡧࡵࡵࡱࡰࡥࡹ࡫ࠢ᠎"), bstack11ll1_opy_ (u"ࠨࡡࡱ࡫ࠥ᠏")], bstack11l1ll1ll11_opy_)
    return bstack11ll1_opy_ (u"ࠧࡼࡿ࠲ࡿࢂ࠭᠐").format(host, bstack11l1ll1ll1l_opy_)