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
import logging
from enum import Enum
import os
import threading
import traceback
from typing import Dict, List, Any, Callable, Tuple, Union
import abc
from datetime import datetime, timezone
from dataclasses import dataclass
from browserstack_sdk.sdk_cli.bstack1lllll1l11l_opy_ import bstack1lllll11ll1_opy_
from browserstack_sdk.sdk_cli.bstack1lll1lll1ll_opy_ import bstack1llll11111l_opy_, bstack1llll1lll11_opy_
class bstack1lll1l1l11l_opy_(Enum):
    PRE = 0
    POST = 1
    def __repr__(self) -> str:
        return bstack11l1l_opy_ (u"ࠨࡔࡦࡵࡷࡌࡴࡵ࡫ࡔࡶࡤࡸࡪ࠴ࡻࡾࠤᙈ").format(self.name)
class bstack1lll111l111_opy_(Enum):
    NONE = 0
    BEFORE_ALL = 1
    LOG = 2
    SETUP_FIXTURE = 3
    INIT_TEST = 4
    BEFORE_EACH = 5
    AFTER_EACH = 6
    TEST = 7
    STEP = 8
    LOG_REPORT = 9
    AFTER_ALL = 10
    def __eq__(self, other):
        if self.__class__ is other.__class__:
            return self.value == other.value
        return NotImplemented
    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented
    def __repr__(self) -> str:
        return bstack11l1l_opy_ (u"ࠢࡕࡧࡶࡸࡋࡸࡡ࡮ࡧࡺࡳࡷࡱࡓࡵࡣࡷࡩ࠳ࢁࡽࠣᙉ").format(self.name)
class bstack1ll1ll11lll_opy_(bstack1llll11111l_opy_):
    bstack1l1llll1lll_opy_: List[str]
    bstack11lll1l1ll1_opy_: Dict[str, str]
    state: bstack1lll111l111_opy_
    bstack1lll1ll1lll_opy_: datetime
    bstack1llll1111ll_opy_: datetime
    def __init__(
        self,
        context: bstack1llll1lll11_opy_,
        bstack1l1llll1lll_opy_: List[str],
        bstack11lll1l1ll1_opy_: Dict[str, str],
        state=bstack1lll111l111_opy_.NONE,
    ):
        super().__init__(context)
        self.bstack1l1llll1lll_opy_ = bstack1l1llll1lll_opy_
        self.bstack11lll1l1ll1_opy_ = bstack11lll1l1ll1_opy_
        self.state = state
        self.bstack1lll1ll1lll_opy_ = datetime.now(tz=timezone.utc)
        self.bstack1llll1111ll_opy_ = datetime.now(tz=timezone.utc)
    def bstack1lllll1111l_opy_(self, bstack1llll1l111l_opy_: bstack1lll111l111_opy_):
        bstack1llll1l1lll_opy_ = bstack1lll111l111_opy_(bstack1llll1l111l_opy_).name
        if not bstack1llll1l1lll_opy_:
            return False
        if bstack1llll1l111l_opy_ == self.state:
            return False
        self.state = bstack1llll1l111l_opy_
        self.bstack1llll1111ll_opy_ = datetime.now(tz=timezone.utc)
        return True
@dataclass
class bstack11llll11l1l_opy_:
    test_framework_name: str
    test_framework_version: str
    platform_index: int
@dataclass
class bstack1lll111l1l1_opy_:
    kind: str
    message: str
    level: Union[None, str] = None
    timestamp: Union[None, datetime] = datetime.now(tz=timezone.utc)
    fileName: str = None
    bstack1l1ll11111l_opy_: int = None
    bstack1l1l1llll11_opy_: str = None
    bstack1llllll_opy_: str = None
    bstack1lll111lll_opy_: str = None
    bstack1l1l1l1111l_opy_: str = None
    bstack11lll11ll11_opy_: str = None
class TestFramework(abc.ABC):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    bstack1ll11l11l1l_opy_ = bstack11l1l_opy_ (u"ࠣࡶࡨࡷࡹࡥࡵࡶ࡫ࡧࠦᙊ")
    bstack1l11111lll1_opy_ = bstack11l1l_opy_ (u"ࠤࡷࡩࡸࡺ࡟ࡪࡦࠥᙋ")
    bstack1l1llll1ll1_opy_ = bstack11l1l_opy_ (u"ࠥࡸࡪࡹࡴࡠࡰࡤࡱࡪࠨᙌ")
    bstack11llllll1ll_opy_ = bstack11l1l_opy_ (u"ࠦࡹ࡫ࡳࡵࡡࡩ࡭ࡱ࡫࡟ࡱࡣࡷ࡬ࠧᙍ")
    bstack1l11111111l_opy_ = bstack11l1l_opy_ (u"ࠧࡺࡥࡴࡶࡢࡸࡦ࡭ࡳࠣᙎ")
    bstack1l11l1lllll_opy_ = bstack11l1l_opy_ (u"ࠨࡴࡦࡵࡷࡣࡷ࡫ࡳࡶ࡮ࡷࠦᙏ")
    bstack1l1l1l1l1ll_opy_ = bstack11l1l_opy_ (u"ࠢࡵࡧࡶࡸࡤࡸࡥࡴࡷ࡯ࡸࡤࡧࡴࠣᙐ")
    bstack1l1l1l11l11_opy_ = bstack11l1l_opy_ (u"ࠣࡶࡨࡷࡹࡥࡳࡵࡣࡵࡸࡪࡪ࡟ࡢࡶࠥᙑ")
    bstack1l1l11ll111_opy_ = bstack11l1l_opy_ (u"ࠤࡷࡩࡸࡺ࡟ࡦࡰࡧࡩࡩࡥࡡࡵࠤᙒ")
    bstack11llll1llll_opy_ = bstack11l1l_opy_ (u"ࠥࡸࡪࡹࡴࡠ࡮ࡲࡧࡦࡺࡩࡰࡰࠥᙓ")
    bstack1l1llll11l1_opy_ = bstack11l1l_opy_ (u"ࠦࡹ࡫ࡳࡵࡡࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࡤࡴࡡ࡮ࡧࠥᙔ")
    bstack1l1l1lll1ll_opy_ = bstack11l1l_opy_ (u"ࠧࡺࡥࡴࡶࡢࡪࡷࡧ࡭ࡦࡹࡲࡶࡰࡥࡶࡦࡴࡶ࡭ࡴࡴࠢᙕ")
    bstack11lllll1lll_opy_ = bstack11l1l_opy_ (u"ࠨࡴࡦࡵࡷࡣࡨࡵࡤࡦࠤᙖ")
    bstack1l11lllll1l_opy_ = bstack11l1l_opy_ (u"ࠢࡵࡧࡶࡸࡤࡸࡥࡳࡷࡱࡣࡳࡧ࡭ࡦࠤᙗ")
    bstack1ll1111l111_opy_ = bstack11l1l_opy_ (u"ࠣࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡢ࡭ࡳࡪࡥࡹࠤᙘ")
    bstack1l11l1ll1l1_opy_ = bstack11l1l_opy_ (u"ࠤࡷࡩࡸࡺ࡟ࡧࡣ࡬ࡰࡺࡸࡥࠣᙙ")
    bstack1l1111111ll_opy_ = bstack11l1l_opy_ (u"ࠥࡸࡪࡹࡴࡠࡨࡤ࡭ࡱࡻࡲࡦࡡࡷࡽࡵ࡫ࠢᙚ")
    bstack1l1111111l1_opy_ = bstack11l1l_opy_ (u"ࠦࡹ࡫ࡳࡵࡡ࡯ࡳ࡬ࡹࠢᙛ")
    bstack11llll1111l_opy_ = bstack11l1l_opy_ (u"ࠧࡺࡥࡴࡶࡢࡱࡪࡺࡡࠣᙜ")
    bstack11lll11l11l_opy_ = bstack11l1l_opy_ (u"࠭ࡴࡦࡵࡷࡣࡸࡩ࡯ࡱࡧࡶࠫᙝ")
    bstack1l111ll11ll_opy_ = bstack11l1l_opy_ (u"ࠢࡢࡷࡷࡳࡲࡧࡴࡦࡡࡶࡩࡸࡹࡩࡰࡰࡢࡲࡦࡳࡥࠣᙞ")
    bstack11lll1l1lll_opy_ = bstack11l1l_opy_ (u"ࠣࡧࡹࡩࡳࡺ࡟ࡴࡶࡤࡶࡹ࡫ࡤࡠࡣࡷࠦᙟ")
    bstack1l111111ll1_opy_ = bstack11l1l_opy_ (u"ࠤࡨࡺࡪࡴࡴࡠࡧࡱࡨࡪࡪ࡟ࡢࡶࠥᙠ")
    bstack11lll1l1l1l_opy_ = bstack11l1l_opy_ (u"ࠥ࡬ࡴࡵ࡫ࡠ࡫ࡧࠦᙡ")
    bstack1l11111l111_opy_ = bstack11l1l_opy_ (u"ࠦ࡭ࡵ࡯࡬ࡡࡵࡩࡸࡻ࡬ࡵࠤᙢ")
    bstack1l1111ll1l1_opy_ = bstack11l1l_opy_ (u"ࠧ࡮࡯ࡰ࡭ࡢࡰࡴ࡭ࡳࠣᙣ")
    bstack11lll1l111l_opy_ = bstack11l1l_opy_ (u"ࠨࡨࡰࡱ࡮ࡣࡳࡧ࡭ࡦࠤᙤ")
    bstack11lllll111l_opy_ = bstack11l1l_opy_ (u"ࠢ࡭ࡱࡪࡷࠧᙥ")
    bstack11lllllll1l_opy_ = bstack11l1l_opy_ (u"ࠣࡥࡸࡷࡹࡵ࡭ࡠ࡯ࡨࡸࡦࡪࡡࡵࡣࠥᙦ")
    bstack1l11111l1l1_opy_ = bstack11l1l_opy_ (u"ࠤࡳࡩࡳࡪࡩ࡯ࡩࠥᙧ")
    bstack11llll1l111_opy_ = bstack11l1l_opy_ (u"ࠥࡴࡪࡴࡤࡪࡰࡪࠦᙨ")
    bstack1l1l11l1ll1_opy_ = bstack11l1l_opy_ (u"࡙ࠦࡋࡓࡕࡡࡖࡇࡗࡋࡅࡏࡕࡋࡓ࡙ࠨᙩ")
    bstack1l1l1llllll_opy_ = bstack11l1l_opy_ (u"࡚ࠧࡅࡔࡖࡢࡐࡔࡍࠢᙪ")
    bstack1l1l11l1lll_opy_ = bstack11l1l_opy_ (u"ࠨࡔࡆࡕࡗࡣࡆ࡚ࡔࡂࡅࡋࡑࡊࡔࡔࠣᙫ")
    bstack1llll11l1l1_opy_: Dict[str, bstack1ll1ll11lll_opy_] = dict()
    bstack11lll111l1l_opy_: Dict[str, List[Callable]] = dict()
    bstack1l1llll1lll_opy_: List[str]
    bstack11lll1l1ll1_opy_: Dict[str, str]
    def __init__(
        self,
        bstack1l1llll1lll_opy_: List[str],
        bstack11lll1l1ll1_opy_: Dict[str, str],
        bstack1lllll1l11l_opy_: bstack1lllll11ll1_opy_
    ):
        self.bstack1l1llll1lll_opy_ = bstack1l1llll1lll_opy_
        self.bstack11lll1l1ll1_opy_ = bstack11lll1l1ll1_opy_
        self.bstack1lllll1l11l_opy_ = bstack1lllll1l11l_opy_
    def track_event(
        self,
        context: bstack11llll11l1l_opy_,
        test_framework_state: bstack1lll111l111_opy_,
        test_hook_state: bstack1lll1l1l11l_opy_,
        *args,
        **kwargs,
    ):
        self.logger.debug(bstack11l1l_opy_ (u"ࠢࡵࡴࡤࡧࡰࡥࡥࡷࡧࡱࡸ࠿ࠦࡴࡦࡵࡷࡣ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟ࡴࡶࡤࡸࡪࡃࡻࡾࠢࡷࡩࡸࡺ࡟ࡩࡱࡲ࡯ࡤࡹࡴࡢࡶࡨࡁࢀࢃࠠࡢࡴࡪࡷࡂࢁࡽࠡ࡭ࡺࡥࡷ࡭ࡳ࠾ࡽࢀࠦᙬ").format(test_framework_state,test_hook_state,args,kwargs))
    def bstack11llll1l1l1_opy_(
        self,
        instance: bstack1ll1ll11lll_opy_,
        bstack1llll1lll1l_opy_: Tuple[bstack1lll111l111_opy_, bstack1lll1l1l11l_opy_],
        *args,
        **kwargs,
    ):
        bstack1l111l11lll_opy_ = TestFramework.bstack1l111l11l11_opy_(bstack1llll1lll1l_opy_)
        if not bstack1l111l11lll_opy_ in TestFramework.bstack11lll111l1l_opy_:
            return
        self.logger.debug(bstack11l1l_opy_ (u"ࠣ࡫ࡱࡺࡴࡱࡩ࡯ࡩࠣࡿࢂࠦࡣࡢ࡮࡯ࡦࡦࡩ࡫ࡴࠤ᙭").format(len(TestFramework.bstack11lll111l1l_opy_[bstack1l111l11lll_opy_])))
        for callback in TestFramework.bstack11lll111l1l_opy_[bstack1l111l11lll_opy_]:
            try:
                callback(self, instance, bstack1llll1lll1l_opy_, *args, **kwargs)
            except Exception as e:
                self.logger.error(bstack11l1l_opy_ (u"ࠤࡨࡶࡷࡵࡲࠡ࡫ࡱࡺࡴࡱࡩ࡯ࡩࠣࡧࡦࡲ࡬ࡣࡣࡦ࡯࠿ࠦࡻࡾࠤ᙮").format(e))
                traceback.print_exc()
    @abc.abstractmethod
    def bstack1l1l1l11l1l_opy_(self):
        return
    @abc.abstractmethod
    def bstack1l1l1111lll_opy_(self, instance, bstack1llll1lll1l_opy_):
        return
    @abc.abstractmethod
    def bstack1l1l1l11lll_opy_(self, instance, bstack1llll1lll1l_opy_):
        return
    @staticmethod
    def bstack1lllll111ll_opy_(target: object, strict=True):
        if target is None:
            return None
        ctx = bstack1llll11111l_opy_.create_context(target)
        instance = TestFramework.bstack1llll11l1l1_opy_.get(ctx.id, None)
        if instance and instance.bstack1llll1l1l1l_opy_(target):
            return instance
        return instance if instance and not strict else None
    @staticmethod
    def bstack1l1ll111lll_opy_(reverse=True) -> List[bstack1ll1ll11lll_opy_]:
        thread_id = threading.get_ident()
        process_id = os.getpid()
        return sorted(
            filter(
                lambda t: t.context.thread_id == thread_id
                and t.context.process_id == process_id,
                TestFramework.bstack1llll11l1l1_opy_.values(),
            ),
            key=lambda t: t.bstack1lll1ll1lll_opy_,
            reverse=reverse,
        )
    @staticmethod
    def bstack1lll1llll1l_opy_(ctx: bstack1llll1lll11_opy_, reverse=True) -> List[bstack1ll1ll11lll_opy_]:
        return sorted(
            filter(
                lambda t: t.context.thread_id == ctx.thread_id
                and t.context.process_id == ctx.process_id,
                TestFramework.bstack1llll11l1l1_opy_.values(),
            ),
            key=lambda t: t.bstack1lll1ll1lll_opy_,
            reverse=reverse,
        )
    @staticmethod
    def bstack1lll1ll1l1l_opy_(instance: bstack1ll1ll11lll_opy_, key: str):
        return instance and key in instance.data
    @staticmethod
    def bstack1llll1lllll_opy_(instance: bstack1ll1ll11lll_opy_, key: str, default_value=None):
        return instance.data.get(key, default_value) if instance else default_value
    @staticmethod
    def bstack1lllll1111l_opy_(instance: bstack1ll1ll11lll_opy_, key: str, value: Any):
        TestFramework.logger.debug(bstack11l1l_opy_ (u"ࠥࡷࡪࡺ࡟ࡴࡶࡤࡸࡪࡀࠠࡪࡰࡶࡸࡦࡴࡣࡦ࠿ࡾࢁࠥࡱࡥࡺ࠿ࡾࢁࠥࡼࡡ࡭ࡷࡨࡁࢀࢃࠢᙯ").format(instance.ref(),key,value))
        instance.data[key] = value
        return True
    @staticmethod
    def bstack11lllll11l1_opy_(instance: bstack1ll1ll11lll_opy_, entries: Dict[str, Any]):
        TestFramework.logger.debug(bstack11l1l_opy_ (u"ࠦࡸ࡫ࡴࡠࡵࡷࡥࡹ࡫࡟ࡦࡰࡷࡶ࡮࡫ࡳ࠻ࠢ࡬ࡲࡸࡺࡡ࡯ࡥࡨࡁࢀࢃࠠࡦࡰࡷࡶ࡮࡫ࡳ࠾ࡽࢀࠦᙰ").format(instance.ref(),entries,))
        instance.data.update(entries)
        return True
    @staticmethod
    def bstack11ll1lll1ll_opy_(instance: bstack1lll111l111_opy_, key: str, value: Any):
        TestFramework.logger.debug(bstack11l1l_opy_ (u"ࠧࡻࡰࡥࡣࡷࡩࡤࡹࡴࡢࡶࡨ࠾ࠥ࡯࡮ࡴࡶࡤࡲࡨ࡫࠽ࡼࡿࠣ࡯ࡪࡿ࠽ࡼࡿࠣࡺࡦࡲࡵࡦ࠿ࡾࢁࠧᙱ").format(instance.ref(),key,value))
        instance.data.update(key, value)
        return True
    @staticmethod
    def get_data(key: str, target: object, strict=True, default_value=None):
        instance = TestFramework.bstack1lllll111ll_opy_(target, strict)
        return TestFramework.bstack1llll1lllll_opy_(instance, key, default_value)
    @staticmethod
    def set_data(key: str, value: Any, target: object, strict=True):
        instance = TestFramework.bstack1lllll111ll_opy_(target, strict)
        if not instance:
            return False
        instance.data[key] = value
        return True
    @staticmethod
    def bstack11lll1l1l11_opy_(instance: bstack1ll1ll11lll_opy_, key: str, value: object):
        if instance == None:
            return
        instance.data[key] = value
    @staticmethod
    def bstack11lll1llll1_opy_(instance: bstack1ll1ll11lll_opy_, key: str):
        return instance.data[key]
    @staticmethod
    def bstack1l111l11l11_opy_(bstack1llll1lll1l_opy_: Tuple[bstack1lll111l111_opy_, bstack1lll1l1l11l_opy_]):
        return bstack11l1l_opy_ (u"ࠨ࠺ࠣᙲ").join((bstack1lll111l111_opy_(bstack1llll1lll1l_opy_[0]).name, bstack1lll1l1l11l_opy_(bstack1llll1lll1l_opy_[1]).name))
    @staticmethod
    def bstack1ll111ll111_opy_(bstack1llll1lll1l_opy_: Tuple[bstack1lll111l111_opy_, bstack1lll1l1l11l_opy_], callback: Callable):
        bstack1l111l11lll_opy_ = TestFramework.bstack1l111l11l11_opy_(bstack1llll1lll1l_opy_)
        TestFramework.logger.debug(bstack11l1l_opy_ (u"ࠢࡴࡧࡷࡣ࡭ࡵ࡯࡬ࡡࡦࡥࡱࡲࡢࡢࡥ࡮࠾ࠥ࡮࡯ࡰ࡭ࡢࡶࡪ࡭ࡩࡴࡶࡵࡽࡤࡱࡥࡺ࠿ࡾࢁࠧᙳ").format(bstack1l111l11lll_opy_))
        if not bstack1l111l11lll_opy_ in TestFramework.bstack11lll111l1l_opy_:
            TestFramework.bstack11lll111l1l_opy_[bstack1l111l11lll_opy_] = []
        TestFramework.bstack11lll111l1l_opy_[bstack1l111l11lll_opy_].append(callback)
    @staticmethod
    def bstack1l1l1ll1lll_opy_(o):
        klass = o.__class__
        module = klass.__module__
        if module == bstack11l1l_opy_ (u"ࠣࡤࡸ࡭ࡱࡺࡩ࡯ࡵࠥᙴ"):
            return klass.__qualname__
        return module + bstack11l1l_opy_ (u"ࠤ࠱ࠦᙵ") + klass.__qualname__
    @staticmethod
    def bstack1l1ll11l11l_opy_(obj, keys, default_value=None):
        return {k: getattr(obj, k, default_value) for k in keys}