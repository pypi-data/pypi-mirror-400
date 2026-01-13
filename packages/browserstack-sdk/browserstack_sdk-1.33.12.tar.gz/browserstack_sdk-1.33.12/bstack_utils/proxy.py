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
from urllib.parse import urlparse
from bstack_utils.config import Config
from bstack_utils.messages import bstack1111lll11l1_opy_
bstack1l1l1ll1l_opy_ = Config.bstack1l1l1111_opy_()
def bstack1lllll11l111_opy_(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False
def bstack1lllll111lll_opy_(bstack1lllll11ll11_opy_, bstack1lllll111ll1_opy_):
    from pypac import get_pac
    from pypac import PACSession
    from pypac.parser import PACFile
    import socket
    if os.path.isfile(bstack1lllll11ll11_opy_):
        with open(bstack1lllll11ll11_opy_) as f:
            pac = PACFile(f.read())
    elif bstack1lllll11l111_opy_(bstack1lllll11ll11_opy_):
        pac = get_pac(url=bstack1lllll11ll11_opy_)
    else:
        raise Exception(bstack11ll1_opy_ (u"࠭ࡐࡢࡥࠣࡪ࡮ࡲࡥࠡࡦࡲࡩࡸࠦ࡮ࡰࡶࠣࡩࡽ࡯ࡳࡵ࠼ࠣࡿࢂ࠭‼").format(bstack1lllll11ll11_opy_))
    session = PACSession(pac)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((bstack11ll1_opy_ (u"ࠢ࠹࠰࠻࠲࠽࠴࠸ࠣ‽"), 80))
        bstack1lllll11l1l1_opy_ = s.getsockname()[0]
        s.close()
    except:
        bstack1lllll11l1l1_opy_ = bstack11ll1_opy_ (u"ࠨ࠲࠱࠴࠳࠶࠮࠱ࠩ‾")
    proxy_url = session.get_pac().find_proxy_for_url(bstack1lllll111ll1_opy_, bstack1lllll11l1l1_opy_)
    return proxy_url
def bstack1l1ll11lll_opy_(config):
    return bstack11ll1_opy_ (u"ࠩ࡫ࡸࡹࡶࡐࡳࡱࡻࡽࠬ‿") in config or bstack11ll1_opy_ (u"ࠪ࡬ࡹࡺࡰࡴࡒࡵࡳࡽࡿࠧ⁀") in config
def bstack11l1ll11l_opy_(config):
    if not bstack1l1ll11lll_opy_(config):
        return
    if config.get(bstack11ll1_opy_ (u"ࠫ࡭ࡺࡴࡱࡒࡵࡳࡽࡿࠧ⁁")):
        return config.get(bstack11ll1_opy_ (u"ࠬ࡮ࡴࡵࡲࡓࡶࡴࡾࡹࠨ⁂"))
    if config.get(bstack11ll1_opy_ (u"࠭ࡨࡵࡶࡳࡷࡕࡸ࡯ࡹࡻࠪ⁃")):
        return config.get(bstack11ll1_opy_ (u"ࠧࡩࡶࡷࡴࡸࡖࡲࡰࡺࡼࠫ⁄"))
def bstack1lllll1111_opy_(config, bstack1lllll111ll1_opy_):
    proxy = bstack11l1ll11l_opy_(config)
    proxies = {}
    if config.get(bstack11ll1_opy_ (u"ࠨࡪࡷࡸࡵࡖࡲࡰࡺࡼࠫ⁅")) or config.get(bstack11ll1_opy_ (u"ࠩ࡫ࡸࡹࡶࡳࡑࡴࡲࡼࡾ࠭⁆")):
        if proxy.endswith(bstack11ll1_opy_ (u"ࠪ࠲ࡵࡧࡣࠨ⁇")):
            proxies = bstack111lllll1l_opy_(proxy, bstack1lllll111ll1_opy_)
        else:
            proxies = {
                bstack11ll1_opy_ (u"ࠫ࡭ࡺࡴࡱࡵࠪ⁈"): proxy
            }
    bstack1l1l1ll1l_opy_.bstack11l1l11l_opy_(bstack11ll1_opy_ (u"ࠬࡶࡲࡰࡺࡼࡗࡪࡺࡴࡪࡰࡪࡷࠬ⁉"), proxies)
    return proxies
def bstack111lllll1l_opy_(bstack1lllll11ll11_opy_, bstack1lllll111ll1_opy_):
    proxies = {}
    global bstack1lllll11l1ll_opy_
    if bstack11ll1_opy_ (u"࠭ࡐࡂࡅࡢࡔࡗࡕࡘ࡚ࠩ⁊") in globals():
        return bstack1lllll11l1ll_opy_
    try:
        proxy = bstack1lllll111lll_opy_(bstack1lllll11ll11_opy_, bstack1lllll111ll1_opy_)
        if bstack11ll1_opy_ (u"ࠢࡅࡋࡕࡉࡈ࡚ࠢ⁋") in proxy:
            proxies = {}
        elif bstack11ll1_opy_ (u"ࠣࡊࡗࡘࡕࠨ⁌") in proxy or bstack11ll1_opy_ (u"ࠤࡋࡘ࡙ࡖࡓࠣ⁍") in proxy or bstack11ll1_opy_ (u"ࠥࡗࡔࡉࡋࡔࠤ⁎") in proxy:
            bstack1lllll11l11l_opy_ = proxy.split(bstack11ll1_opy_ (u"ࠦࠥࠨ⁏"))
            if bstack11ll1_opy_ (u"ࠧࡀ࠯࠰ࠤ⁐") in bstack11ll1_opy_ (u"ࠨࠢ⁑").join(bstack1lllll11l11l_opy_[1:]):
                proxies = {
                    bstack11ll1_opy_ (u"ࠧࡩࡶࡷࡴࡸ࠭⁒"): bstack11ll1_opy_ (u"ࠣࠤ⁓").join(bstack1lllll11l11l_opy_[1:])
                }
            else:
                proxies = {
                    bstack11ll1_opy_ (u"ࠩ࡫ࡸࡹࡶࡳࠨ⁔"): str(bstack1lllll11l11l_opy_[0]).lower() + bstack11ll1_opy_ (u"ࠥ࠾࠴࠵ࠢ⁕") + bstack11ll1_opy_ (u"ࠦࠧ⁖").join(bstack1lllll11l11l_opy_[1:])
                }
        elif bstack11ll1_opy_ (u"ࠧࡖࡒࡐ࡚࡜ࠦ⁗") in proxy:
            bstack1lllll11l11l_opy_ = proxy.split(bstack11ll1_opy_ (u"ࠨࠠࠣ⁘"))
            if bstack11ll1_opy_ (u"ࠢ࠻࠱࠲ࠦ⁙") in bstack11ll1_opy_ (u"ࠣࠤ⁚").join(bstack1lllll11l11l_opy_[1:]):
                proxies = {
                    bstack11ll1_opy_ (u"ࠩ࡫ࡸࡹࡶࡳࠨ⁛"): bstack11ll1_opy_ (u"ࠥࠦ⁜").join(bstack1lllll11l11l_opy_[1:])
                }
            else:
                proxies = {
                    bstack11ll1_opy_ (u"ࠫ࡭ࡺࡴࡱࡵࠪ⁝"): bstack11ll1_opy_ (u"ࠧ࡮ࡴࡵࡲ࠽࠳࠴ࠨ⁞") + bstack11ll1_opy_ (u"ࠨࠢ ").join(bstack1lllll11l11l_opy_[1:])
                }
        else:
            proxies = {
                bstack11ll1_opy_ (u"ࠧࡩࡶࡷࡴࡸ࠭⁠"): proxy
            }
    except Exception as e:
        print(bstack11ll1_opy_ (u"ࠣࡵࡲࡱࡪࠦࡥࡳࡴࡲࡶࠧ⁡"), bstack1111lll11l1_opy_.format(bstack1lllll11ll11_opy_, str(e)))
    bstack1lllll11l1ll_opy_ = proxies
    return proxies