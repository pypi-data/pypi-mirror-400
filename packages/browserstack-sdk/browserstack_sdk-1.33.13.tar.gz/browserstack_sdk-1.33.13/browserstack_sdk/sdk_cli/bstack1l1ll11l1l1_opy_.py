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
from browserstack_sdk.sdk_cli.bstack1ll1l1ll1ll_opy_ import bstack1ll1ll1l1ll_opy_
from browserstack_sdk.sdk_cli.bstack1llll11l1ll_opy_ import (
    bstack1llll1111l1_opy_,
    bstack1lll1lll1l1_opy_,
    bstack1llll111ll1_opy_,
    bstack1llll1ll1ll_opy_,
)
from browserstack_sdk.sdk_cli.bstack1lll1l11l11_opy_ import bstack1lll11l111l_opy_
from browserstack_sdk.sdk_cli.bstack1ll1l111ll1_opy_ import bstack1ll1l1111l1_opy_
from browserstack_sdk.sdk_cli.bstack1lll1lll1ll_opy_ import bstack1llll1lll11_opy_
from typing import Tuple, Dict, Any, List, Callable
from browserstack_sdk.sdk_cli.bstack1ll1l1ll1ll_opy_ import bstack1ll1ll1l1ll_opy_
import weakref
class bstack1l1ll11ll11_opy_(bstack1ll1ll1l1ll_opy_):
    bstack1l1ll11l1ll_opy_: str
    frameworks: List[str]
    drivers: Dict[str, Tuple[Callable, bstack1llll1ll1ll_opy_]]
    pages: Dict[str, Tuple[Callable, bstack1llll1ll1ll_opy_]]
    def __init__(self, bstack1l1ll11l1ll_opy_: str, frameworks: List[str]):
        super().__init__()
        self.drivers = dict()
        self.pages = dict()
        self.bstack1l1ll1l11l1_opy_ = dict()
        self.bstack1l1ll11l1ll_opy_ = bstack1l1ll11l1ll_opy_
        self.frameworks = frameworks
        bstack1ll1l1111l1_opy_.bstack1ll111ll111_opy_((bstack1llll1111l1_opy_.bstack1llll1ll1l1_opy_, bstack1lll1lll1l1_opy_.POST), self.__1l1ll1l11ll_opy_)
        if any(bstack1lll11l111l_opy_.NAME in f.lower().strip() for f in frameworks):
            bstack1lll11l111l_opy_.bstack1ll111ll111_opy_(
                (bstack1llll1111l1_opy_.bstack1lll1ll1ll1_opy_, bstack1lll1lll1l1_opy_.PRE), self.__1l1ll1l1l11_opy_
            )
            bstack1lll11l111l_opy_.bstack1ll111ll111_opy_(
                (bstack1llll1111l1_opy_.QUIT, bstack1lll1lll1l1_opy_.POST), self.__1l1ll1l1lll_opy_
            )
    def __1l1ll1l11ll_opy_(
        self,
        f: bstack1ll1l1111l1_opy_,
        bstack1l1ll1l1ll1_opy_: object,
        exec: Tuple[bstack1llll1ll1ll_opy_, str],
        bstack1llll1lll1l_opy_: Tuple[bstack1llll1111l1_opy_, bstack1lll1lll1l1_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        try:
            instance, method_name = exec
            if method_name != bstack11l1l_opy_ (u"ࠢ࡯ࡧࡺࡣࡵࡧࡧࡦࠤዞ"):
                return
            contexts = bstack1l1ll1l1ll1_opy_.browser.contexts
            if contexts:
                for context in contexts:
                    if context.pages:
                        for page in context.pages:
                            if bstack11l1l_opy_ (u"ࠣࡣࡥࡳࡺࡺ࠺ࡣ࡮ࡤࡲࡰࠨዟ") in page.url:
                                self.logger.debug(bstack11l1l_opy_ (u"ࠤࡖࡸࡴࡸࡩ࡯ࡩࠣࡸ࡭࡫ࠠ࡯ࡧࡺࠤࡵࡧࡧࡦࠢ࡬ࡲࡸࡺࡡ࡯ࡥࡨࠦዠ"))
                                self.pages[instance.ref()] = weakref.ref(page), instance
                                bstack1llll111ll1_opy_.bstack1lllll1111l_opy_(instance, self.bstack1l1ll11l1ll_opy_, True)
                                self.logger.debug(bstack11l1l_opy_ (u"ࠥࡣࡤࡵ࡮ࡠࡲࡤ࡫ࡪࡥࡩ࡯࡫ࡷ࠾ࠥ࡯࡮ࡴࡶࡤࡲࡨ࡫࠽ࠣዡ") + str(instance.ref()) + bstack11l1l_opy_ (u"ࠦࠧዢ"))
        except Exception as e:
            self.logger.debug(bstack11l1l_opy_ (u"ࠧࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡ࡫ࡱࠤࡸࡺ࡯ࡳ࡫ࡱ࡫ࠥࡴࡥࡸࠢࡳࡥ࡬࡫ࠠ࠻ࠤዣ"),e)
    def __1l1ll1l1l11_opy_(
        self,
        f: bstack1lll11l111l_opy_,
        driver: object,
        exec: Tuple[bstack1llll1ll1ll_opy_, str],
        bstack1llll1lll1l_opy_: Tuple[bstack1llll1111l1_opy_, bstack1lll1lll1l1_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, _ = exec
        if instance.ref() in self.drivers or bstack1llll111ll1_opy_.bstack1llll1lllll_opy_(instance, self.bstack1l1ll11l1ll_opy_, False):
            return
        if not f.bstack1l1ll1ll111_opy_(f.hub_url(driver)):
            self.bstack1l1ll1l11l1_opy_[instance.ref()] = weakref.ref(driver), instance
            bstack1llll111ll1_opy_.bstack1lllll1111l_opy_(instance, self.bstack1l1ll11l1ll_opy_, True)
            self.logger.debug(bstack11l1l_opy_ (u"ࠨ࡟ࡠࡱࡱࡣࡸ࡫࡬ࡦࡰ࡬ࡹࡲࡥࡩ࡯࡫ࡷ࠾ࠥࡴ࡯࡯ࡡࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡦࡵ࡭ࡻ࡫ࡲࠡ࡫ࡱࡷࡹࡧ࡮ࡤࡧࡀࠦዤ") + str(instance.ref()) + bstack11l1l_opy_ (u"ࠢࠣዥ"))
            return
        self.drivers[instance.ref()] = weakref.ref(driver), instance
        bstack1llll111ll1_opy_.bstack1lllll1111l_opy_(instance, self.bstack1l1ll11l1ll_opy_, True)
        self.logger.debug(bstack11l1l_opy_ (u"ࠣࡡࡢࡳࡳࡥࡳࡦ࡮ࡨࡲ࡮ࡻ࡭ࡠ࡫ࡱ࡭ࡹࡀࠠࡪࡰࡶࡸࡦࡴࡣࡦ࠿ࠥዦ") + str(instance.ref()) + bstack11l1l_opy_ (u"ࠤࠥዧ"))
    def __1l1ll1l1lll_opy_(
        self,
        f: bstack1lll11l111l_opy_,
        driver: object,
        exec: Tuple[bstack1llll1ll1ll_opy_, str],
        bstack1llll1lll1l_opy_: Tuple[bstack1llll1111l1_opy_, bstack1lll1lll1l1_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, _ = exec
        if not instance.ref() in self.drivers:
            return
        self.bstack1l1ll1l1111_opy_(instance)
        self.logger.debug(bstack11l1l_opy_ (u"ࠥࡣࡤࡵ࡮ࡠࡵࡨࡰࡪࡴࡩࡶ࡯ࡢࡵࡺ࡯ࡴ࠻ࠢ࡬ࡲࡸࡺࡡ࡯ࡥࡨࡁࠧየ") + str(instance.ref()) + bstack11l1l_opy_ (u"ࠦࠧዩ"))
    def bstack1l1ll11ll1l_opy_(self, context: bstack1llll1lll11_opy_, reverse=True) -> List[Tuple[Callable, bstack1llll1ll1ll_opy_]]:
        matches = []
        if self.pages:
            for data in self.pages.values():
                if data[1].bstack1l1ll11lll1_opy_(context):
                    matches.append(data)
        if self.drivers:
            for data in self.drivers.values():
                if (
                    bstack1lll11l111l_opy_.bstack1l1ll1l1l1l_opy_(data[1])
                    and data[1].bstack1l1ll11lll1_opy_(context)
                    and getattr(data[0](), bstack11l1l_opy_ (u"ࠧࡹࡥࡴࡵ࡬ࡳࡳࡥࡩࡥࠤዪ"), False)
                ):
                    matches.append(data)
        return sorted(matches, key=lambda d: d[1].bstack1lll1ll1lll_opy_, reverse=reverse)
    def bstack1l1ll1l111l_opy_(self, context: bstack1llll1lll11_opy_, reverse=True) -> List[Tuple[Callable, bstack1llll1ll1ll_opy_]]:
        matches = []
        for data in self.bstack1l1ll1l11l1_opy_.values():
            if (
                data[1].bstack1l1ll11lll1_opy_(context)
                and getattr(data[0](), bstack11l1l_opy_ (u"ࠨࡳࡦࡵࡶ࡭ࡴࡴ࡟ࡪࡦࠥያ"), False)
            ):
                matches.append(data)
        return sorted(matches, key=lambda d: d[1].bstack1lll1ll1lll_opy_, reverse=reverse)
    def bstack1l1ll11llll_opy_(self, instance: bstack1llll1ll1ll_opy_) -> bool:
        return instance and instance.ref() in self.drivers
    def bstack1l1ll1l1111_opy_(self, instance: bstack1llll1ll1ll_opy_) -> bool:
        if self.bstack1l1ll11llll_opy_(instance):
            self.drivers.pop(instance.ref())
            bstack1llll111ll1_opy_.bstack1lllll1111l_opy_(instance, self.bstack1l1ll11l1ll_opy_, False)
            return True
        return False