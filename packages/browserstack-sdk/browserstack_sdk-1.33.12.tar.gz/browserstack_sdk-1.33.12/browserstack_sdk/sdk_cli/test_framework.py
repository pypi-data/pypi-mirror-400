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
import os
import threading
import traceback
from typing import Dict, List, Any, Callable, Tuple, Union
import abc
from datetime import datetime, timezone
from dataclasses import dataclass
from browserstack_sdk.sdk_cli.bstack1lll1l1llll_opy_ import bstack1lll11ll11l_opy_
from browserstack_sdk.sdk_cli.bstack1lll11ll111_opy_ import bstack1lll1lllll1_opy_, bstack1ll1111lll1_opy_
class bstack1lll1111l11_opy_(Enum):
    PRE = 0
    POST = 1
    def __repr__(self) -> str:
        return bstack11ll1_opy_ (u"ࠢࡕࡧࡶࡸࡍࡵ࡯࡬ࡕࡷࡥࡹ࡫࠮ࡼࡿࠥᙉ").format(self.name)
class bstack1llll1ll111_opy_(Enum):
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
        return bstack11ll1_opy_ (u"ࠣࡖࡨࡷࡹࡌࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡔࡶࡤࡸࡪ࠴ࡻࡾࠤᙊ").format(self.name)
class bstack1lll1l11l11_opy_(bstack1lll1lllll1_opy_):
    bstack1ll1ll1llll_opy_: List[str]
    bstack1lll1l11111_opy_: Dict[str, str]
    state: bstack1llll1ll111_opy_
    bstack1l1llll11l1_opy_: datetime
    bstack1l1llll1l11_opy_: datetime
    def __init__(
        self,
        context: bstack1ll1111lll1_opy_,
        bstack1ll1ll1llll_opy_: List[str],
        bstack1lll1l11111_opy_: Dict[str, str],
        state=bstack1llll1ll111_opy_.NONE,
    ):
        super().__init__(context)
        self.bstack1ll1ll1llll_opy_ = bstack1ll1ll1llll_opy_
        self.bstack1lll1l11111_opy_ = bstack1lll1l11111_opy_
        self.state = state
        self.bstack1l1llll11l1_opy_ = datetime.now(tz=timezone.utc)
        self.bstack1l1llll1l11_opy_ = datetime.now(tz=timezone.utc)
    def bstack1lll111ll11_opy_(self, bstack1l1lll11ll1_opy_: bstack1llll1ll111_opy_):
        bstack1l1lll11l1l_opy_ = bstack1llll1ll111_opy_(bstack1l1lll11ll1_opy_).name
        if not bstack1l1lll11l1l_opy_:
            return False
        if bstack1l1lll11ll1_opy_ == self.state:
            return False
        self.state = bstack1l1lll11ll1_opy_
        self.bstack1l1llll1l11_opy_ = datetime.now(tz=timezone.utc)
        return True
@dataclass
class bstack1lll1l1ll1l_opy_:
    test_framework_name: str
    test_framework_version: str
    platform_index: int
@dataclass
class bstack1lll1ll1lll_opy_:
    kind: str
    message: str
    level: Union[None, str] = None
    timestamp: Union[None, datetime] = datetime.now(tz=timezone.utc)
    fileName: str = None
    bstack1llll1lll11_opy_: int = None
    bstack1lll1111l1l_opy_: str = None
    bstack1ll11l_opy_: str = None
    bstack11lllll1l_opy_: str = None
    bstack1lllll111ll_opy_: str = None
    bstack1lll111l111_opy_: str = None
class TestFramework(abc.ABC):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    bstack1llll111ll1_opy_ = bstack11ll1_opy_ (u"ࠤࡷࡩࡸࡺ࡟ࡶࡷ࡬ࡨࠧᙋ")
    bstack1llll1l1111_opy_ = bstack11ll1_opy_ (u"ࠥࡸࡪࡹࡴࡠ࡫ࡧࠦᙌ")
    bstack1llll1l11ll_opy_ = bstack11ll1_opy_ (u"ࠦࡹ࡫ࡳࡵࡡࡱࡥࡲ࡫ࠢᙍ")
    bstack1llll111lll_opy_ = bstack11ll1_opy_ (u"ࠧࡺࡥࡴࡶࡢࡪ࡮ࡲࡥࡠࡲࡤࡸ࡭ࠨᙎ")
    bstack1lll11l1111_opy_ = bstack11ll1_opy_ (u"ࠨࡴࡦࡵࡷࡣࡹࡧࡧࡴࠤᙏ")
    bstack1ll1ll1ll1l_opy_ = bstack11ll1_opy_ (u"ࠢࡵࡧࡶࡸࡤࡸࡥࡴࡷ࡯ࡸࠧᙐ")
    bstack1llll1llll1_opy_ = bstack11ll1_opy_ (u"ࠣࡶࡨࡷࡹࡥࡲࡦࡵࡸࡰࡹࡥࡡࡵࠤᙑ")
    bstack1lllll1111l_opy_ = bstack11ll1_opy_ (u"ࠤࡷࡩࡸࡺ࡟ࡴࡶࡤࡶࡹ࡫ࡤࡠࡣࡷࠦᙒ")
    bstack1lll1ll111l_opy_ = bstack11ll1_opy_ (u"ࠥࡸࡪࡹࡴࡠࡧࡱࡨࡪࡪ࡟ࡢࡶࠥᙓ")
    bstack1lll11lllll_opy_ = bstack11ll1_opy_ (u"ࠦࡹ࡫ࡳࡵࡡ࡯ࡳࡨࡧࡴࡪࡱࡱࠦᙔ")
    bstack1lll1111111_opy_ = bstack11ll1_opy_ (u"ࠧࡺࡥࡴࡶࡢࡪࡷࡧ࡭ࡦࡹࡲࡶࡰࡥ࡮ࡢ࡯ࡨࠦᙕ")
    bstack1lll11111ll_opy_ = bstack11ll1_opy_ (u"ࠨࡴࡦࡵࡷࡣ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟ࡷࡧࡵࡷ࡮ࡵ࡮ࠣᙖ")
    bstack1llll11111l_opy_ = bstack11ll1_opy_ (u"ࠢࡵࡧࡶࡸࡤࡩ࡯ࡥࡧࠥᙗ")
    bstack1lll11111l1_opy_ = bstack11ll1_opy_ (u"ࠣࡶࡨࡷࡹࡥࡲࡦࡴࡸࡲࡤࡴࡡ࡮ࡧࠥᙘ")
    bstack1lll11l1l1l_opy_ = bstack11ll1_opy_ (u"ࠤࡳࡰࡦࡺࡦࡰࡴࡰࡣ࡮ࡴࡤࡦࡺࠥᙙ")
    bstack1lll11ll1l1_opy_ = bstack11ll1_opy_ (u"ࠥࡸࡪࡹࡴࡠࡨࡤ࡭ࡱࡻࡲࡦࠤᙚ")
    bstack1lll1111ll1_opy_ = bstack11ll1_opy_ (u"ࠦࡹ࡫ࡳࡵࡡࡩࡥ࡮ࡲࡵࡳࡧࡢࡸࡾࡶࡥࠣᙛ")
    bstack1llll11l111_opy_ = bstack11ll1_opy_ (u"ࠧࡺࡥࡴࡶࡢࡰࡴ࡭ࡳࠣᙜ")
    bstack1llll1l11l1_opy_ = bstack11ll1_opy_ (u"ࠨࡴࡦࡵࡷࡣࡲ࡫ࡴࡢࠤᙝ")
    bstack1ll1ll111ll_opy_ = bstack11ll1_opy_ (u"ࠧࡵࡧࡶࡸࡤࡹࡣࡰࡲࡨࡷࠬᙞ")
    bstack1llll1l111l_opy_ = bstack11ll1_opy_ (u"ࠣࡣࡸࡸࡴࡳࡡࡵࡧࡢࡷࡪࡹࡳࡪࡱࡱࡣࡳࡧ࡭ࡦࠤᙟ")
    bstack1lll1ll1l1l_opy_ = bstack11ll1_opy_ (u"ࠤࡨࡺࡪࡴࡴࡠࡵࡷࡥࡷࡺࡥࡥࡡࡤࡸࠧᙠ")
    bstack1lll11l1ll1_opy_ = bstack11ll1_opy_ (u"ࠥࡩࡻ࡫࡮ࡵࡡࡨࡲࡩ࡫ࡤࡠࡣࡷࠦᙡ")
    bstack1llll1l1l1l_opy_ = bstack11ll1_opy_ (u"ࠦ࡭ࡵ࡯࡬ࡡ࡬ࡨࠧᙢ")
    bstack1llll1111ll_opy_ = bstack11ll1_opy_ (u"ࠧ࡮࡯ࡰ࡭ࡢࡶࡪࡹࡵ࡭ࡶࠥᙣ")
    bstack1ll1llll111_opy_ = bstack11ll1_opy_ (u"ࠨࡨࡰࡱ࡮ࡣࡱࡵࡧࡴࠤᙤ")
    bstack1ll1lll1l1l_opy_ = bstack11ll1_opy_ (u"ࠢࡩࡱࡲ࡯ࡤࡴࡡ࡮ࡧࠥᙥ")
    bstack1lll11l111l_opy_ = bstack11ll1_opy_ (u"ࠣ࡮ࡲ࡫ࡸࠨᙦ")
    bstack1lll1llll11_opy_ = bstack11ll1_opy_ (u"ࠤࡦࡹࡸࡺ࡯࡮ࡡࡰࡩࡹࡧࡤࡢࡶࡤࠦᙧ")
    bstack1lll1l11l1l_opy_ = bstack11ll1_opy_ (u"ࠥࡴࡪࡴࡤࡪࡰࡪࠦᙨ")
    bstack1ll1ll1l1l1_opy_ = bstack11ll1_opy_ (u"ࠦࡵ࡫࡮ࡥ࡫ࡱ࡫ࠧᙩ")
    bstack1l11111llll_opy_ = bstack11ll1_opy_ (u"࡚ࠧࡅࡔࡖࡢࡗࡈࡘࡅࡆࡐࡖࡌࡔ࡚ࠢᙪ")
    bstack1lll1l111l1_opy_ = bstack11ll1_opy_ (u"ࠨࡔࡆࡕࡗࡣࡑࡕࡇࠣᙫ")
    bstack1l111111111_opy_ = bstack11ll1_opy_ (u"ࠢࡕࡇࡖࡘࡤࡇࡔࡕࡃࡆࡌࡒࡋࡎࡕࠤᙬ")
    bstack1lll1llllll_opy_: Dict[str, bstack1lll1l11l11_opy_] = dict()
    bstack1ll1l1l1l11_opy_: Dict[str, List[Callable]] = dict()
    bstack1ll1ll1llll_opy_: List[str]
    bstack1lll1l11111_opy_: Dict[str, str]
    def __init__(
        self,
        bstack1ll1ll1llll_opy_: List[str],
        bstack1lll1l11111_opy_: Dict[str, str],
        bstack1lll1l1llll_opy_: bstack1lll11ll11l_opy_
    ):
        self.bstack1ll1ll1llll_opy_ = bstack1ll1ll1llll_opy_
        self.bstack1lll1l11111_opy_ = bstack1lll1l11111_opy_
        self.bstack1lll1l1llll_opy_ = bstack1lll1l1llll_opy_
    def track_event(
        self,
        context: bstack1lll1l1ll1l_opy_,
        test_framework_state: bstack1llll1ll111_opy_,
        test_hook_state: bstack1lll1111l11_opy_,
        *args,
        **kwargs,
    ):
        self.logger.debug(bstack11ll1_opy_ (u"ࠣࡶࡵࡥࡨࡱ࡟ࡦࡸࡨࡲࡹࡀࠠࡵࡧࡶࡸࡤ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡵࡷࡥࡹ࡫࠽ࡼࡿࠣࡸࡪࡹࡴࡠࡪࡲࡳࡰࡥࡳࡵࡣࡷࡩࡂࢁࡽࠡࡣࡵ࡫ࡸࡃࡻࡾࠢ࡮ࡻࡦࡸࡧࡴ࠿ࡾࢁࠧ᙭").format(test_framework_state,test_hook_state,args,kwargs))
    def bstack1ll1ll11lll_opy_(
        self,
        instance: bstack1lll1l11l11_opy_,
        bstack1lll1lll111_opy_: Tuple[bstack1llll1ll111_opy_, bstack1lll1111l11_opy_],
        *args,
        **kwargs,
    ):
        bstack1ll1l1l111l_opy_ = TestFramework.bstack1ll1l111lll_opy_(bstack1lll1lll111_opy_)
        if not bstack1ll1l1l111l_opy_ in TestFramework.bstack1ll1l1l1l11_opy_:
            return
        self.logger.debug(bstack11ll1_opy_ (u"ࠤ࡬ࡲࡻࡵ࡫ࡪࡰࡪࠤࢀࢃࠠࡤࡣ࡯ࡰࡧࡧࡣ࡬ࡵࠥ᙮").format(len(TestFramework.bstack1ll1l1l1l11_opy_[bstack1ll1l1l111l_opy_])))
        for callback in TestFramework.bstack1ll1l1l1l11_opy_[bstack1ll1l1l111l_opy_]:
            try:
                callback(self, instance, bstack1lll1lll111_opy_, *args, **kwargs)
            except Exception as e:
                self.logger.error(bstack11ll1_opy_ (u"ࠥࡩࡷࡸ࡯ࡳࠢ࡬ࡲࡻࡵ࡫ࡪࡰࡪࠤࡨࡧ࡬࡭ࡤࡤࡧࡰࡀࠠࡼࡿࠥᙯ").format(e))
                traceback.print_exc()
    @abc.abstractmethod
    def bstack1lllll11111_opy_(self):
        return
    @abc.abstractmethod
    def bstack1lll1lll11l_opy_(self, instance, bstack1lll1lll111_opy_):
        return
    @abc.abstractmethod
    def bstack1lll11l1l11_opy_(self, instance, bstack1lll1lll111_opy_):
        return
    @staticmethod
    def bstack1ll1lllll1l_opy_(target: object, strict=True):
        if target is None:
            return None
        ctx = bstack1lll1lllll1_opy_.create_context(target)
        instance = TestFramework.bstack1lll1llllll_opy_.get(ctx.id, None)
        if instance and instance.bstack1l1lll111l1_opy_(target):
            return instance
        return instance if instance and not strict else None
    @staticmethod
    def bstack1l1111llll1_opy_(reverse=True) -> List[bstack1lll1l11l11_opy_]:
        thread_id = threading.get_ident()
        process_id = os.getpid()
        return sorted(
            filter(
                lambda t: t.context.thread_id == thread_id
                and t.context.process_id == process_id,
                TestFramework.bstack1lll1llllll_opy_.values(),
            ),
            key=lambda t: t.bstack1l1llll11l1_opy_,
            reverse=reverse,
        )
    @staticmethod
    def bstack1l1lll11l11_opy_(ctx: bstack1ll1111lll1_opy_, reverse=True) -> List[bstack1lll1l11l11_opy_]:
        return sorted(
            filter(
                lambda t: t.context.thread_id == ctx.thread_id
                and t.context.process_id == ctx.process_id,
                TestFramework.bstack1lll1llllll_opy_.values(),
            ),
            key=lambda t: t.bstack1l1llll11l1_opy_,
            reverse=reverse,
        )
    @staticmethod
    def bstack1lll1ll1ll1_opy_(instance: bstack1lll1l11l11_opy_, key: str):
        return instance and key in instance.data
    @staticmethod
    def bstack1ll1llll11l_opy_(instance: bstack1lll1l11l11_opy_, key: str, default_value=None):
        return instance.data.get(key, default_value) if instance else default_value
    @staticmethod
    def bstack1lll111ll11_opy_(instance: bstack1lll1l11l11_opy_, key: str, value: Any):
        TestFramework.logger.debug(bstack11ll1_opy_ (u"ࠦࡸ࡫ࡴࡠࡵࡷࡥࡹ࡫࠺ࠡ࡫ࡱࡷࡹࡧ࡮ࡤࡧࡀࡿࢂࠦ࡫ࡦࡻࡀࡿࢂࠦࡶࡢ࡮ࡸࡩࡂࢁࡽࠣᙰ").format(instance.ref(),key,value))
        instance.data[key] = value
        return True
    @staticmethod
    def bstack1lll11llll1_opy_(instance: bstack1lll1l11l11_opy_, entries: Dict[str, Any]):
        TestFramework.logger.debug(bstack11ll1_opy_ (u"ࠧࡹࡥࡵࡡࡶࡸࡦࡺࡥࡠࡧࡱࡸࡷ࡯ࡥࡴ࠼ࠣ࡭ࡳࡹࡴࡢࡰࡦࡩࡂࢁࡽࠡࡧࡱࡸࡷ࡯ࡥࡴ࠿ࡾࢁࠧᙱ").format(instance.ref(),entries,))
        instance.data.update(entries)
        return True
    @staticmethod
    def bstack11ll1lll1ll_opy_(instance: bstack1llll1ll111_opy_, key: str, value: Any):
        TestFramework.logger.debug(bstack11ll1_opy_ (u"ࠨࡵࡱࡦࡤࡸࡪࡥࡳࡵࡣࡷࡩ࠿ࠦࡩ࡯ࡵࡷࡥࡳࡩࡥ࠾ࡽࢀࠤࡰ࡫ࡹ࠾ࡽࢀࠤࡻࡧ࡬ࡶࡧࡀࡿࢂࠨᙲ").format(instance.ref(),key,value))
        instance.data.update(key, value)
        return True
    @staticmethod
    def get_data(key: str, target: object, strict=True, default_value=None):
        instance = TestFramework.bstack1ll1lllll1l_opy_(target, strict)
        return TestFramework.bstack1ll1llll11l_opy_(instance, key, default_value)
    @staticmethod
    def set_data(key: str, value: Any, target: object, strict=True):
        instance = TestFramework.bstack1ll1lllll1l_opy_(target, strict)
        if not instance:
            return False
        instance.data[key] = value
        return True
    @staticmethod
    def bstack1ll1lll1l11_opy_(instance: bstack1lll1l11l11_opy_, key: str, value: object):
        if instance == None:
            return
        instance.data[key] = value
    @staticmethod
    def bstack1ll1ll1l1ll_opy_(instance: bstack1lll1l11l11_opy_, key: str):
        return instance.data[key]
    @staticmethod
    def bstack1ll1l111lll_opy_(bstack1lll1lll111_opy_: Tuple[bstack1llll1ll111_opy_, bstack1lll1111l11_opy_]):
        return bstack11ll1_opy_ (u"ࠢ࠻ࠤᙳ").join((bstack1llll1ll111_opy_(bstack1lll1lll111_opy_[0]).name, bstack1lll1111l11_opy_(bstack1lll1lll111_opy_[1]).name))
    @staticmethod
    def bstack1ll1l11111l_opy_(bstack1lll1lll111_opy_: Tuple[bstack1llll1ll111_opy_, bstack1lll1111l11_opy_], callback: Callable):
        bstack1ll1l1l111l_opy_ = TestFramework.bstack1ll1l111lll_opy_(bstack1lll1lll111_opy_)
        TestFramework.logger.debug(bstack11ll1_opy_ (u"ࠣࡵࡨࡸࡤ࡮࡯ࡰ࡭ࡢࡧࡦࡲ࡬ࡣࡣࡦ࡯࠿ࠦࡨࡰࡱ࡮ࡣࡷ࡫ࡧࡪࡵࡷࡶࡾࡥ࡫ࡦࡻࡀࡿࢂࠨᙴ").format(bstack1ll1l1l111l_opy_))
        if not bstack1ll1l1l111l_opy_ in TestFramework.bstack1ll1l1l1l11_opy_:
            TestFramework.bstack1ll1l1l1l11_opy_[bstack1ll1l1l111l_opy_] = []
        TestFramework.bstack1ll1l1l1l11_opy_[bstack1ll1l1l111l_opy_].append(callback)
    @staticmethod
    def bstack1lll1l1l111_opy_(o):
        klass = o.__class__
        module = klass.__module__
        if module == bstack11ll1_opy_ (u"ࠤࡥࡹ࡮ࡲࡴࡪࡰࡶࠦᙵ"):
            return klass.__qualname__
        return module + bstack11ll1_opy_ (u"ࠥ࠲ࠧᙶ") + klass.__qualname__
    @staticmethod
    def bstack1ll1lllll11_opy_(obj, keys, default_value=None):
        return {k: getattr(obj, k, default_value) for k in keys}