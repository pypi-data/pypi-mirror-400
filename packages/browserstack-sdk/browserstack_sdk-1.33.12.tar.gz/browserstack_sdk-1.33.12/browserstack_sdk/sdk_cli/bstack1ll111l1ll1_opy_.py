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
from browserstack_sdk.sdk_cli.bstack1l1ll111111_opy_ import bstack1l1l1l111ll_opy_
from browserstack_sdk.sdk_cli.bstack1ll11l1l1l1_opy_ import (
    bstack1ll11lllll1_opy_,
    bstack1ll11lll1ll_opy_,
    bstack1ll1l1111l1_opy_,
    bstack1ll1l1ll1l1_opy_,
)
from browserstack_sdk.sdk_cli.bstack1ll11l1lll1_opy_ import bstack1ll11ll1lll_opy_
from browserstack_sdk.sdk_cli.bstack1ll11l111ll_opy_ import bstack1ll11l11l1l_opy_
from browserstack_sdk.sdk_cli.bstack1lll11ll111_opy_ import bstack1ll1111lll1_opy_
from typing import Tuple, Dict, Any, List, Callable
from browserstack_sdk.sdk_cli.bstack1l1ll111111_opy_ import bstack1l1l1l111ll_opy_
import weakref
class bstack1ll111l1l11_opy_(bstack1l1l1l111ll_opy_):
    bstack1ll111ll111_opy_: str
    frameworks: List[str]
    drivers: Dict[str, Tuple[Callable, bstack1ll1l1ll1l1_opy_]]
    pages: Dict[str, Tuple[Callable, bstack1ll1l1ll1l1_opy_]]
    def __init__(self, bstack1ll111ll111_opy_: str, frameworks: List[str]):
        super().__init__()
        self.drivers = dict()
        self.pages = dict()
        self.bstack1l111l1l111_opy_ = dict()
        self.bstack1ll111ll111_opy_ = bstack1ll111ll111_opy_
        self.frameworks = frameworks
        bstack1ll11l11l1l_opy_.bstack1ll1l11111l_opy_((bstack1ll11lllll1_opy_.bstack1ll11l1ll1l_opy_, bstack1ll11lll1ll_opy_.POST), self.__1l111l11l1l_opy_)
        if any(bstack1ll11ll1lll_opy_.NAME in f.lower().strip() for f in frameworks):
            bstack1ll11ll1lll_opy_.bstack1ll1l11111l_opy_(
                (bstack1ll11lllll1_opy_.bstack1ll11l1l1ll_opy_, bstack1ll11lll1ll_opy_.PRE), self.__1l111l11lll_opy_
            )
            bstack1ll11ll1lll_opy_.bstack1ll1l11111l_opy_(
                (bstack1ll11lllll1_opy_.QUIT, bstack1ll11lll1ll_opy_.POST), self.__1l111l11ll1_opy_
            )
    def __1l111l11l1l_opy_(
        self,
        f: bstack1ll11l11l1l_opy_,
        bstack1l111l1111l_opy_: object,
        exec: Tuple[bstack1ll1l1ll1l1_opy_, str],
        bstack1lll1lll111_opy_: Tuple[bstack1ll11lllll1_opy_, bstack1ll11lll1ll_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        try:
            instance, method_name = exec
            if method_name != bstack11ll1_opy_ (u"ࠦࡳ࡫ࡷࡠࡲࡤ࡫ࡪࠨᓓ"):
                return
            contexts = bstack1l111l1111l_opy_.browser.contexts
            if contexts:
                for context in contexts:
                    if context.pages:
                        for page in context.pages:
                            if bstack11ll1_opy_ (u"ࠧࡧࡢࡰࡷࡷ࠾ࡧࡲࡡ࡯࡭ࠥᓔ") in page.url:
                                self.logger.debug(bstack11ll1_opy_ (u"ࠨࡓࡵࡱࡵ࡭ࡳ࡭ࠠࡵࡪࡨࠤࡳ࡫ࡷࠡࡲࡤ࡫ࡪࠦࡩ࡯ࡵࡷࡥࡳࡩࡥࠣᓕ"))
                                self.pages[instance.ref()] = weakref.ref(page), instance
                                bstack1ll1l1111l1_opy_.bstack1lll111ll11_opy_(instance, self.bstack1ll111ll111_opy_, True)
                                self.logger.debug(bstack11ll1_opy_ (u"ࠢࡠࡡࡲࡲࡤࡶࡡࡨࡧࡢ࡭ࡳ࡯ࡴ࠻ࠢ࡬ࡲࡸࡺࡡ࡯ࡥࡨࡁࠧᓖ") + str(instance.ref()) + bstack11ll1_opy_ (u"ࠣࠤᓗ"))
        except Exception as e:
            self.logger.debug(bstack11ll1_opy_ (u"ࠤࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥ࡯࡮ࠡࡵࡷࡳࡷ࡯࡮ࡨࠢࡱࡩࡼࠦࡰࡢࡩࡨࠤ࠿ࠨᓘ"),e)
    def __1l111l11lll_opy_(
        self,
        f: bstack1ll11ll1lll_opy_,
        driver: object,
        exec: Tuple[bstack1ll1l1ll1l1_opy_, str],
        bstack1lll1lll111_opy_: Tuple[bstack1ll11lllll1_opy_, bstack1ll11lll1ll_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, _ = exec
        if instance.ref() in self.drivers or bstack1ll1l1111l1_opy_.bstack1ll1llll11l_opy_(instance, self.bstack1ll111ll111_opy_, False):
            return
        if not f.bstack1ll11l1l11l_opy_(f.hub_url(driver)):
            self.bstack1l111l1l111_opy_[instance.ref()] = weakref.ref(driver), instance
            bstack1ll1l1111l1_opy_.bstack1lll111ll11_opy_(instance, self.bstack1ll111ll111_opy_, True)
            self.logger.debug(bstack11ll1_opy_ (u"ࠥࡣࡤࡵ࡮ࡠࡵࡨࡰࡪࡴࡩࡶ࡯ࡢ࡭ࡳ࡯ࡴ࠻ࠢࡱࡳࡳࡥࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤࡪࡲࡪࡸࡨࡶࠥ࡯࡮ࡴࡶࡤࡲࡨ࡫࠽ࠣᓙ") + str(instance.ref()) + bstack11ll1_opy_ (u"ࠦࠧᓚ"))
            return
        self.drivers[instance.ref()] = weakref.ref(driver), instance
        bstack1ll1l1111l1_opy_.bstack1lll111ll11_opy_(instance, self.bstack1ll111ll111_opy_, True)
        self.logger.debug(bstack11ll1_opy_ (u"ࠧࡥ࡟ࡰࡰࡢࡷࡪࡲࡥ࡯࡫ࡸࡱࡤ࡯࡮ࡪࡶ࠽ࠤ࡮ࡴࡳࡵࡣࡱࡧࡪࡃࠢᓛ") + str(instance.ref()) + bstack11ll1_opy_ (u"ࠨࠢᓜ"))
    def __1l111l11ll1_opy_(
        self,
        f: bstack1ll11ll1lll_opy_,
        driver: object,
        exec: Tuple[bstack1ll1l1ll1l1_opy_, str],
        bstack1lll1lll111_opy_: Tuple[bstack1ll11lllll1_opy_, bstack1ll11lll1ll_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, _ = exec
        if not instance.ref() in self.drivers:
            return
        self.bstack1l111l11l11_opy_(instance)
        self.logger.debug(bstack11ll1_opy_ (u"ࠢࡠࡡࡲࡲࡤࡹࡥ࡭ࡧࡱ࡭ࡺࡳ࡟ࡲࡷ࡬ࡸ࠿ࠦࡩ࡯ࡵࡷࡥࡳࡩࡥ࠾ࠤᓝ") + str(instance.ref()) + bstack11ll1_opy_ (u"ࠣࠤᓞ"))
    def bstack1l1lllllll1_opy_(self, context: bstack1ll1111lll1_opy_, reverse=True) -> List[Tuple[Callable, bstack1ll1l1ll1l1_opy_]]:
        matches = []
        if self.pages:
            for data in self.pages.values():
                if data[1].bstack1l111l111l1_opy_(context):
                    matches.append(data)
        if self.drivers:
            for data in self.drivers.values():
                if (
                    bstack1ll11ll1lll_opy_.bstack1ll11l11lll_opy_(data[1])
                    and data[1].bstack1l111l111l1_opy_(context)
                    and getattr(data[0](), bstack11ll1_opy_ (u"ࠤࡶࡩࡸࡹࡩࡰࡰࡢ࡭ࡩࠨᓟ"), False)
                ):
                    matches.append(data)
        return sorted(matches, key=lambda d: d[1].bstack1l1llll11l1_opy_, reverse=reverse)
    def bstack1ll1111111l_opy_(self, context: bstack1ll1111lll1_opy_, reverse=True) -> List[Tuple[Callable, bstack1ll1l1ll1l1_opy_]]:
        matches = []
        for data in self.bstack1l111l1l111_opy_.values():
            if (
                data[1].bstack1l111l111l1_opy_(context)
                and getattr(data[0](), bstack11ll1_opy_ (u"ࠥࡷࡪࡹࡳࡪࡱࡱࡣ࡮ࡪࠢᓠ"), False)
            ):
                matches.append(data)
        return sorted(matches, key=lambda d: d[1].bstack1l1llll11l1_opy_, reverse=reverse)
    def bstack1l111l111ll_opy_(self, instance: bstack1ll1l1ll1l1_opy_) -> bool:
        return instance and instance.ref() in self.drivers
    def bstack1l111l11l11_opy_(self, instance: bstack1ll1l1ll1l1_opy_) -> bool:
        if self.bstack1l111l111ll_opy_(instance):
            self.drivers.pop(instance.ref())
            bstack1ll1l1111l1_opy_.bstack1lll111ll11_opy_(instance, self.bstack1ll111ll111_opy_, False)
            return True
        return False