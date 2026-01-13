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
import logging
from enum import Enum
from typing import Dict, Tuple, Callable, Type, List, Any
import abc
from datetime import datetime, timezone, timedelta
from browserstack_sdk.sdk_cli.bstack1lll11ll111_opy_ import bstack1lll1lllll1_opy_, bstack1ll1111lll1_opy_
import os
import threading
class bstack1ll11lll1ll_opy_(Enum):
    PRE = 0
    POST = 1
    def __repr__(self) -> str:
        return bstack11ll1_opy_ (u"ࠣࡊࡲࡳࡰ࡙ࡴࡢࡶࡨ࠲ࢀࢃࠢዦ").format(self.name)
class bstack1ll11lllll1_opy_(Enum):
    NONE = 0
    bstack1ll11l1ll1l_opy_ = 1
    bstack1ll11l11l11_opy_ = 3
    bstack1ll11l1l1ll_opy_ = 4
    bstack1l1lll1l11l_opy_ = 5
    QUIT = 6
    def __eq__(self, other):
        if self.__class__ is other.__class__:
            return self.value == other.value
        return NotImplemented
    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented
    def __repr__(self) -> str:
        return bstack11ll1_opy_ (u"ࠤࡄࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳࡌࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡔࡶࡤࡸࡪ࠴ࡻࡾࠤዧ").format(self.name)
class bstack1ll1l1ll1l1_opy_(bstack1lll1lllll1_opy_):
    framework_name: str
    framework_version: str
    state: bstack1ll11lllll1_opy_
    previous_state: bstack1ll11lllll1_opy_
    bstack1l1llll11l1_opy_: datetime
    bstack1l1llll1l11_opy_: datetime
    def __init__(
        self,
        context: bstack1ll1111lll1_opy_,
        framework_name: str,
        framework_version: str,
        state=bstack1ll11lllll1_opy_.NONE,
    ):
        super().__init__(context)
        self.framework_name = framework_name
        self.framework_version = framework_version
        self.state = state
        self.previous_state = bstack1ll11lllll1_opy_.NONE
        self.bstack1l1llll11l1_opy_ = datetime.now(tz=timezone.utc)
        self.bstack1l1llll1l11_opy_ = datetime.now(tz=timezone.utc)
    def bstack1lll111ll11_opy_(self, bstack1l1lll11ll1_opy_: bstack1ll11lllll1_opy_):
        bstack1l1lll11l1l_opy_ = bstack1ll11lllll1_opy_(bstack1l1lll11ll1_opy_).name
        if not bstack1l1lll11l1l_opy_:
            return False
        if bstack1l1lll11ll1_opy_ == self.state:
            return False
        if self.state == bstack1ll11lllll1_opy_.bstack1ll11l11l11_opy_: # bstack1l1lll1llll_opy_ bstack1l1lll1l1l1_opy_ for bstack1l1lll1ll11_opy_ in bstack1l1llll1111_opy_, it bstack1l1lll1l1ll_opy_ bstack1l1lll1111l_opy_ bstack1l1lll1lll1_opy_ times bstack1l1llll111l_opy_ a new state
            return True
        if (
            bstack1l1lll11ll1_opy_ == bstack1ll11lllll1_opy_.NONE
            or (self.state != bstack1ll11lllll1_opy_.NONE and bstack1l1lll11ll1_opy_ == bstack1ll11lllll1_opy_.bstack1ll11l1ll1l_opy_)
            or (self.state < bstack1ll11lllll1_opy_.bstack1ll11l1ll1l_opy_ and bstack1l1lll11ll1_opy_ == bstack1ll11lllll1_opy_.bstack1ll11l1l1ll_opy_)
            or (self.state < bstack1ll11lllll1_opy_.bstack1ll11l1ll1l_opy_ and bstack1l1lll11ll1_opy_ == bstack1ll11lllll1_opy_.QUIT)
        ):
            raise ValueError(bstack11ll1_opy_ (u"ࠥ࡭ࡳࡼࡡ࡭࡫ࡧࠤࡸࡺࡡࡵࡧࠣࡸࡷࡧ࡮ࡴ࡫ࡷ࡭ࡴࡴ࠺ࠡࠤየ") + str(self.state) + bstack11ll1_opy_ (u"ࠦࠥࡃ࠾ࠡࠤዩ") + str(bstack1l1lll11ll1_opy_))
        self.previous_state = self.state
        self.state = bstack1l1lll11ll1_opy_
        self.bstack1l1llll1l11_opy_ = datetime.now(tz=timezone.utc)
        return True
class bstack1ll1l1111l1_opy_(abc.ABC):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    bstack1lll1llllll_opy_: Dict[str, bstack1ll1l1ll1l1_opy_] = dict()
    framework_name: str
    framework_version: str
    classes: List[Type]
    def __init__(
        self,
        framework_name: str,
        framework_version: str,
        classes: List[Type],
    ):
        self.framework_name = framework_name
        self.framework_version = framework_version
        self.classes = classes
    @abc.abstractmethod
    def bstack1ll1l11l1ll_opy_(self, instance: bstack1ll1l1ll1l1_opy_, method_name: str, bstack1ll1l11l1l1_opy_: timedelta, *args, **kwargs):
        return
    @abc.abstractmethod
    def bstack1ll11l11ll1_opy_(
        self, method_name, previous_state: bstack1ll11lllll1_opy_, *args, **kwargs
    ) -> bstack1ll11lllll1_opy_:
        return
    @abc.abstractmethod
    def bstack1ll1l11llll_opy_(
        self,
        target: object,
        exec: Tuple[bstack1ll1l1ll1l1_opy_, str],
        bstack1lll1lll111_opy_: Tuple[bstack1ll11lllll1_opy_, bstack1ll11lll1ll_opy_],
        result: Any,
        *args,
        **kwargs,
    ) -> Callable:
        return
    def bstack1ll11ll1l1l_opy_(self, bstack1l1llll1l1l_opy_: List[str]):
        for clazz in self.classes:
            for method_name in bstack1l1llll1l1l_opy_:
                bstack1l1lll11lll_opy_ = getattr(clazz, method_name, None)
                if not callable(bstack1l1lll11lll_opy_):
                    self.logger.warning(bstack11ll1_opy_ (u"ࠧࡻ࡮ࡱࡣࡷࡧ࡭࡫ࡤࠡ࡯ࡨࡸ࡭ࡵࡤ࠻ࠢࠥዪ") + str(method_name) + bstack11ll1_opy_ (u"ࠨࠢያ"))
                    continue
                bstack1ll1l1111ll_opy_ = self.bstack1ll11l11ll1_opy_(
                    method_name, previous_state=bstack1ll11lllll1_opy_.NONE
                )
                bstack1l1ll1llll1_opy_ = self.bstack1l1lll1ll1l_opy_(
                    method_name,
                    (bstack1ll1l1111ll_opy_ if bstack1ll1l1111ll_opy_ else bstack1ll11lllll1_opy_.NONE),
                    bstack1l1lll11lll_opy_,
                )
                if not callable(bstack1l1ll1llll1_opy_):
                    self.logger.warning(bstack11ll1_opy_ (u"ࠢ࡮ࡧࡷ࡬ࡴࡪࠠ࡯ࡱࡷࠤࡵࡧࡴࡤࡪࡨࡨ࠿ࠦࡻ࡮ࡧࡷ࡬ࡴࡪ࡟࡯ࡣࡰࡩࢂࠦࠨࡼࡵࡨࡰ࡫࠴ࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡱࡥࡲ࡫ࡽ࠻ࠢࠥዬ") + str(self.framework_version) + bstack11ll1_opy_ (u"ࠣࠫࠥይ"))
                    continue
                setattr(clazz, method_name, bstack1l1ll1llll1_opy_)
    def bstack1l1lll1ll1l_opy_(
        self,
        method_name: str,
        bstack1ll1l1111ll_opy_: bstack1ll11lllll1_opy_,
        bstack1l1lll11lll_opy_: Callable,
    ):
        def wrapped(target, *args, **kwargs):
            bstack1ll11l1l1l_opy_ = datetime.now()
            (bstack1ll1l1111ll_opy_,) = wrapped.__vars__
            bstack1ll1l1111ll_opy_ = (
                bstack1ll1l1111ll_opy_
                if bstack1ll1l1111ll_opy_ and bstack1ll1l1111ll_opy_ != bstack1ll11lllll1_opy_.NONE
                else self.bstack1ll11l11ll1_opy_(method_name, previous_state=bstack1ll1l1111ll_opy_, *args, **kwargs)
            )
            if bstack1ll1l1111ll_opy_ == bstack1ll11lllll1_opy_.bstack1ll11l1ll1l_opy_:
                ctx = bstack1lll1lllll1_opy_.create_context(self.bstack1l1lll11111_opy_(target))
                if not self.bstack1l1lll1l111_opy_() or ctx.id not in bstack1ll1l1111l1_opy_.bstack1lll1llllll_opy_:
                    bstack1ll1l1111l1_opy_.bstack1lll1llllll_opy_[ctx.id] = bstack1ll1l1ll1l1_opy_(
                        ctx, self.framework_name, self.framework_version, bstack1ll1l1111ll_opy_
                    )
                self.logger.debug(bstack11ll1_opy_ (u"ࠤࡺࡶࡦࡶࡰࡦࡦࠣࡱࡪࡺࡨࡰࡦࠣࡧࡷ࡫ࡡࡵࡧࡧ࠾ࠥࢁࡴࡢࡴࡪࡩࡹ࠴࡟ࡠࡥ࡯ࡥࡸࡹ࡟ࡠࡿࠣࡱࡪࡺࡨࡰࡦࡢࡲࡦࡳࡥ࠾ࡽࡰࡩࡹ࡮࡯ࡥࡡࡱࡥࡲ࡫ࡽࠡࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡸࡺࡡࡵࡧࡀࡿ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟ࡴࡶࡤࡸࡪࢃࠠࡤࡶࡻࡁࢀࡩࡴࡹ࠰࡬ࡨࢂࠦࡩ࡯ࡵࡷࡥࡳࡩࡥࡴ࠿ࠥዮ") + str(bstack1ll1l1111l1_opy_.bstack1lll1llllll_opy_.keys()) + bstack11ll1_opy_ (u"ࠥࠦዯ"))
            else:
                self.logger.debug(bstack11ll1_opy_ (u"ࠦࡼࡸࡡࡱࡲࡨࡨࠥࡳࡥࡵࡪࡲࡨࠥ࡯࡮ࡷࡱ࡮ࡩࡩࡀࠠࡼࡶࡤࡶ࡬࡫ࡴ࠯ࡡࡢࡧࡱࡧࡳࡴࡡࡢࢁࠥࡳࡥࡵࡪࡲࡨࡤࡴࡡ࡮ࡧࡀࡿࡲ࡫ࡴࡩࡱࡧࡣࡳࡧ࡭ࡦࡿࠣࡪࡷࡧ࡭ࡦࡹࡲࡶࡰࡥࡳࡵࡣࡷࡩࡂࢁࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡶࡸࡦࡺࡥࡾࠢ࡬ࡲࡸࡺࡡ࡯ࡥࡨࡷࡂࠨደ") + str(bstack1ll1l1111l1_opy_.bstack1lll1llllll_opy_.keys()) + bstack11ll1_opy_ (u"ࠧࠨዱ"))
            instance = bstack1ll1l1111l1_opy_.bstack1ll1lllll1l_opy_(self.bstack1l1lll11111_opy_(target))
            if bstack1ll1l1111ll_opy_ == bstack1ll11lllll1_opy_.NONE or not instance:
                ctx = bstack1lll1lllll1_opy_.create_context(self.bstack1l1lll11111_opy_(target))
                self.logger.warning(bstack11ll1_opy_ (u"ࠨࡷࡳࡣࡳࡴࡪࡪࠠ࡮ࡧࡷ࡬ࡴࡪࠠࡶࡰࡷࡶࡦࡩ࡫ࡦࡦ࠽ࠤࢀࡳࡥࡵࡪࡲࡨࡤࡴࡡ࡮ࡧࢀࠤ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟ࡴࡶࡤࡸࡪࡃࡻࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡢࡷࡹࡧࡴࡦࡿࠣࡧࡹࡾ࠽ࡼࡥࡷࡼࢂࠦࡩ࡯ࡵࡷࡥࡳࡩࡥࡴ࠿ࠥዲ") + str(bstack1ll1l1111l1_opy_.bstack1lll1llllll_opy_.keys()) + bstack11ll1_opy_ (u"ࠢࠣዳ"))
                return bstack1l1lll11lll_opy_(target, *args, **kwargs)
            bstack1l1ll1lllll_opy_ = self.bstack1ll1l11llll_opy_(
                target,
                (instance, method_name),
                (bstack1ll1l1111ll_opy_, bstack1ll11lll1ll_opy_.PRE),
                None,
                *args,
                **kwargs,
            )
            if instance.bstack1lll111ll11_opy_(bstack1ll1l1111ll_opy_):
                self.logger.debug(bstack11ll1_opy_ (u"ࠣࡣࡳࡴࡱ࡯ࡥࡥࠢࡶࡸࡦࡺࡥ࠮ࡶࡵࡥࡳࡹࡩࡵ࡫ࡲࡲ࠿ࠦࡻࡪࡰࡶࡸࡦࡴࡣࡦ࠰ࡳࡶࡪࡼࡩࡰࡷࡶࡣࡸࡺࡡࡵࡧࢀࠤࡂࡄࠠࡼ࡫ࡱࡷࡹࡧ࡮ࡤࡧ࠱ࡷࡹࡧࡴࡦࡿࠣࠬࢀࡺࡹࡱࡧࠫࡸࡦࡸࡧࡦࡶࠬࢁ࠳ࢁ࡭ࡦࡶ࡫ࡳࡩࡥ࡮ࡢ࡯ࡨࢁࠥࢁࡡࡳࡩࡶࢁ࠮࡛ࠦࠣዴ") + str(instance.ref()) + bstack11ll1_opy_ (u"ࠤࡠࠦድ"))
            result = (
                bstack1l1ll1lllll_opy_(target, bstack1l1lll11lll_opy_, *args, **kwargs)
                if callable(bstack1l1ll1lllll_opy_)
                else bstack1l1lll11lll_opy_(target, *args, **kwargs)
            )
            bstack1l1lll111ll_opy_ = self.bstack1ll1l11llll_opy_(
                target,
                (instance, method_name),
                (bstack1ll1l1111ll_opy_, bstack1ll11lll1ll_opy_.POST),
                result,
                *args,
                **kwargs,
            )
            self.bstack1ll1l11l1ll_opy_(instance, method_name, datetime.now() - bstack1ll11l1l1l_opy_, *args, **kwargs)
            return bstack1l1lll111ll_opy_ if bstack1l1lll111ll_opy_ else result
        wrapped.__name__ = method_name
        wrapped.__vars__ = (bstack1ll1l1111ll_opy_,)
        return wrapped
    @staticmethod
    def bstack1ll1lllll1l_opy_(target: object, strict=True):
        ctx = bstack1lll1lllll1_opy_.create_context(target)
        instance = bstack1ll1l1111l1_opy_.bstack1lll1llllll_opy_.get(ctx.id, None)
        if instance and instance.bstack1l1lll111l1_opy_(target):
            return instance
        return instance if instance and not strict else None
    @staticmethod
    def bstack1l1lll11l11_opy_(
        ctx: bstack1ll1111lll1_opy_, state: bstack1ll11lllll1_opy_, reverse=True
    ) -> List[bstack1ll1l1ll1l1_opy_]:
        return sorted(
            filter(
                lambda t: t.state == state
                and t.context.thread_id == ctx.thread_id
                and t.context.process_id == ctx.process_id,
                bstack1ll1l1111l1_opy_.bstack1lll1llllll_opy_.values(),
            ),
            key=lambda t: t.bstack1l1llll11l1_opy_,
            reverse=reverse,
        )
    @staticmethod
    def bstack1lll1ll1ll1_opy_(instance: bstack1ll1l1ll1l1_opy_, key: str):
        return instance and key in instance.data
    @staticmethod
    def bstack1ll1llll11l_opy_(instance: bstack1ll1l1ll1l1_opy_, key: str, default_value=None):
        return instance.data.get(key, default_value) if instance else default_value
    @staticmethod
    def bstack1lll111ll11_opy_(instance: bstack1ll1l1ll1l1_opy_, key: str, value: Any) -> bool:
        instance.data[key] = value
        bstack1ll1l1111l1_opy_.logger.debug(bstack11ll1_opy_ (u"ࠥࡷࡪࡺ࡟ࡴࡶࡤࡸࡪࡀࠠࡪࡰࡶࡸࡦࡴࡣࡦ࠿ࡾ࡭ࡳࡹࡴࡢࡰࡦࡩ࠳ࡸࡥࡧࠪࠬࢁࠥࡱࡥࡺ࠿ࡾ࡯ࡪࡿࡽࠡࡸࡤࡰࡺ࡫࠽ࠣዶ") + str(value) + bstack11ll1_opy_ (u"ࠦࠧዷ"))
        return True
    @staticmethod
    def get_data(key: str, target: object, strict=True, default_value=None):
        instance = bstack1ll1l1111l1_opy_.bstack1ll1lllll1l_opy_(target, strict)
        return bstack1ll1l1111l1_opy_.bstack1ll1llll11l_opy_(instance, key, default_value)
    @staticmethod
    def set_data(key: str, value: Any, target: object, strict=True):
        instance = bstack1ll1l1111l1_opy_.bstack1ll1lllll1l_opy_(target, strict)
        if not instance:
            return False
        instance.data[key] = value
        return True
    def bstack1l1lll1l111_opy_(self):
        return self.framework_name == bstack11ll1_opy_ (u"ࠬࡶ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵࠩዸ")
    def bstack1l1lll11111_opy_(self, target):
        return target if not self.bstack1l1lll1l111_opy_() else self.bstack1l1llll11ll_opy_()
    @staticmethod
    def bstack1l1llll11ll_opy_():
        return str(os.getpid()) + str(threading.get_ident())