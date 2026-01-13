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
import threading
from uuid import uuid4
from itertools import zip_longest
from collections import OrderedDict
from robot.libraries.BuiltIn import BuiltIn
from browserstack_sdk.bstack1111ll1ll1_opy_ import RobotHandler
from bstack_utils.capture import bstack111l1l1lll_opy_
from bstack_utils.bstack111l1ll11l_opy_ import bstack111l111lll_opy_, bstack111l1ll1l1_opy_, bstack111ll111ll_opy_
from bstack_utils.bstack111ll11lll_opy_ import bstack1l11llll1l_opy_
from bstack_utils.bstack111l1l1l1l_opy_ import bstack11lll11l11_opy_
from bstack_utils.constants import *
from bstack_utils.helper import bstack1lll11l1l_opy_, bstack111lll1lll_opy_, Result, \
    error_handler, bstack111l11l1ll_opy_
class bstack_robot_listener:
    ROBOT_LISTENER_API_VERSION = 2
    _lock = threading.Lock()
    store = {
        bstack11ll1_opy_ (u"ࠫࡨࡻࡲࡳࡧࡱࡸࡤ࡮࡯ࡰ࡭ࡢࡹࡺ࡯ࡤࠨྡ"): [],
        bstack11ll1_opy_ (u"ࠬ࡭࡬ࡰࡤࡤࡰࡤ࡮࡯ࡰ࡭ࡶࠫྡྷ"): [],
        bstack11ll1_opy_ (u"࠭ࡴࡦࡵࡷࡣ࡭ࡵ࡯࡬ࡵࠪྣ"): []
    }
    bstack111l1111ll_opy_ = []
    bstack111l1111l1_opy_ = []
    @staticmethod
    def bstack111l1l1111_opy_(log):
        if not ((isinstance(log[bstack11ll1_opy_ (u"ࠧ࡮ࡧࡶࡷࡦ࡭ࡥࠨྤ")], list) or (isinstance(log[bstack11ll1_opy_ (u"ࠨ࡯ࡨࡷࡸࡧࡧࡦࠩྥ")], dict)) and len(log[bstack11ll1_opy_ (u"ࠩࡰࡩࡸࡹࡡࡨࡧࠪྦ")])>0) or (isinstance(log[bstack11ll1_opy_ (u"ࠪࡱࡪࡹࡳࡢࡩࡨࠫྦྷ")], str) and log[bstack11ll1_opy_ (u"ࠫࡲ࡫ࡳࡴࡣࡪࡩࠬྨ")].strip())):
            return
        active = bstack1l11llll1l_opy_.bstack111ll111l1_opy_()
        log = {
            bstack11ll1_opy_ (u"ࠬࡲࡥࡷࡧ࡯ࠫྩ"): log[bstack11ll1_opy_ (u"࠭࡬ࡦࡸࡨࡰࠬྪ")],
            bstack11ll1_opy_ (u"ࠧࡵ࡫ࡰࡩࡸࡺࡡ࡮ࡲࠪྫ"): bstack111l11l1ll_opy_().isoformat() + bstack11ll1_opy_ (u"ࠨ࡜ࠪྫྷ"),
            bstack11ll1_opy_ (u"ࠩࡰࡩࡸࡹࡡࡨࡧࠪྭ"): log[bstack11ll1_opy_ (u"ࠪࡱࡪࡹࡳࡢࡩࡨࠫྮ")],
        }
        if active:
            if active[bstack11ll1_opy_ (u"ࠫࡹࡿࡰࡦࠩྯ")] == bstack11ll1_opy_ (u"ࠬ࡮࡯ࡰ࡭ࠪྰ"):
                log[bstack11ll1_opy_ (u"࠭ࡨࡰࡱ࡮ࡣࡷࡻ࡮ࡠࡷࡸ࡭ࡩ࠭ྱ")] = active[bstack11ll1_opy_ (u"ࠧࡩࡱࡲ࡯ࡤࡸࡵ࡯ࡡࡸࡹ࡮ࡪࠧྲ")]
            elif active[bstack11ll1_opy_ (u"ࠨࡶࡼࡴࡪ࠭ླ")] == bstack11ll1_opy_ (u"ࠩࡷࡩࡸࡺࠧྴ"):
                log[bstack11ll1_opy_ (u"ࠪࡸࡪࡹࡴࡠࡴࡸࡲࡤࡻࡵࡪࡦࠪྵ")] = active[bstack11ll1_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡵࡹࡳࡥࡵࡶ࡫ࡧࠫྶ")]
        bstack11lll11l11_opy_.bstack1l1l11l11l_opy_([log])
    def __init__(self):
        self.messages = bstack111l11111l_opy_()
        self._1111ll1lll_opy_ = None
        self._111l111111_opy_ = None
        self._1111l1ll1l_opy_ = OrderedDict()
        self.bstack111ll11ll1_opy_ = bstack111l1l1lll_opy_(self.bstack111l1l1111_opy_)
    @error_handler(class_method=True)
    def start_suite(self, name, attrs):
        self.messages.bstack1111lll111_opy_()
        if not self._1111l1ll1l_opy_.get(attrs.get(bstack11ll1_opy_ (u"ࠬ࡯ࡤࠨྷ")), None):
            self._1111l1ll1l_opy_[attrs.get(bstack11ll1_opy_ (u"࠭ࡩࡥࠩྸ"))] = {}
        bstack111l11l11l_opy_ = bstack111ll111ll_opy_(
                bstack1111ll11l1_opy_=attrs.get(bstack11ll1_opy_ (u"ࠧࡪࡦࠪྐྵ")),
                name=name,
                started_at=bstack111lll1lll_opy_(),
                file_path=os.path.relpath(attrs[bstack11ll1_opy_ (u"ࠨࡵࡲࡹࡷࡩࡥࠨྺ")], start=os.getcwd()) if attrs.get(bstack11ll1_opy_ (u"ࠩࡶࡳࡺࡸࡣࡦࠩྻ")) != bstack11ll1_opy_ (u"ࠪࠫྼ") else bstack11ll1_opy_ (u"ࠫࠬ྽"),
                framework=bstack11ll1_opy_ (u"ࠬࡘ࡯ࡣࡱࡷࠫ྾")
            )
        threading.current_thread().current_suite_id = attrs.get(bstack11ll1_opy_ (u"࠭ࡩࡥࠩ྿"), None)
        self._1111l1ll1l_opy_[attrs.get(bstack11ll1_opy_ (u"ࠧࡪࡦࠪ࿀"))][bstack11ll1_opy_ (u"ࠨࡶࡨࡷࡹࡥࡤࡢࡶࡤࠫ࿁")] = bstack111l11l11l_opy_
    @error_handler(class_method=True)
    def end_suite(self, name, attrs):
        messages = self.messages.bstack1111ll111l_opy_()
        self._1111lll11l_opy_(messages)
        with self._lock:
            for bstack1111l11lll_opy_ in self.bstack111l1111ll_opy_:
                bstack1111l11lll_opy_[bstack11ll1_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡳࡷࡱࠫ࿂")][bstack11ll1_opy_ (u"ࠪ࡬ࡴࡵ࡫ࡴࠩ࿃")].extend(self.store[bstack11ll1_opy_ (u"ࠫ࡬ࡲ࡯ࡣࡣ࡯ࡣ࡭ࡵ࡯࡬ࡵࠪ࿄")])
                bstack11lll11l11_opy_.bstack1lll1llll_opy_(bstack1111l11lll_opy_)
            self.bstack111l1111ll_opy_ = []
            self.store[bstack11ll1_opy_ (u"ࠬ࡭࡬ࡰࡤࡤࡰࡤ࡮࡯ࡰ࡭ࡶࠫ࿅")] = []
    @error_handler(class_method=True)
    def start_test(self, name, attrs):
        self.bstack111ll11ll1_opy_.start()
        if not self._1111l1ll1l_opy_.get(attrs.get(bstack11ll1_opy_ (u"࠭ࡩࡥ࿆ࠩ")), None):
            self._1111l1ll1l_opy_[attrs.get(bstack11ll1_opy_ (u"ࠧࡪࡦࠪ࿇"))] = {}
        driver = bstack1lll11l1l_opy_(threading.current_thread(), bstack11ll1_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫ࡔࡧࡶࡷ࡮ࡵ࡮ࡅࡴ࡬ࡺࡪࡸࠧ࿈"), None)
        bstack111l1ll11l_opy_ = bstack111ll111ll_opy_(
            bstack1111ll11l1_opy_=attrs.get(bstack11ll1_opy_ (u"ࠩ࡬ࡨࠬ࿉")),
            name=name,
            started_at=bstack111lll1lll_opy_(),
            file_path=os.path.relpath(attrs[bstack11ll1_opy_ (u"ࠪࡷࡴࡻࡲࡤࡧࠪ࿊")], start=os.getcwd()),
            scope=RobotHandler.bstack111l11l1l1_opy_(attrs.get(bstack11ll1_opy_ (u"ࠫࡸࡵࡵࡳࡥࡨࠫ࿋"), None)),
            framework=bstack11ll1_opy_ (u"ࠬࡘ࡯ࡣࡱࡷࠫ࿌"),
            tags=attrs[bstack11ll1_opy_ (u"࠭ࡴࡢࡩࡶࠫ࿍")],
            hooks=self.store[bstack11ll1_opy_ (u"ࠧࡨ࡮ࡲࡦࡦࡲ࡟ࡩࡱࡲ࡯ࡸ࠭࿎")],
            bstack111l1l11ll_opy_=bstack11lll11l11_opy_.bstack111l1ll111_opy_(driver) if driver and driver.session_id else {},
            meta={},
            code=bstack11ll1_opy_ (u"ࠣࡽࢀࠤࡡࡴࠠࡼࡿࠥ࿏").format(bstack11ll1_opy_ (u"ࠤࠣࠦ࿐").join(attrs[bstack11ll1_opy_ (u"ࠪࡸࡦ࡭ࡳࠨ࿑")]), name) if attrs[bstack11ll1_opy_ (u"ࠫࡹࡧࡧࡴࠩ࿒")] else name
        )
        self._1111l1ll1l_opy_[attrs.get(bstack11ll1_opy_ (u"ࠬ࡯ࡤࠨ࿓"))][bstack11ll1_opy_ (u"࠭ࡴࡦࡵࡷࡣࡩࡧࡴࡢࠩ࿔")] = bstack111l1ll11l_opy_
        threading.current_thread().current_test_uuid = bstack111l1ll11l_opy_.bstack111l111l1l_opy_()
        threading.current_thread().current_test_id = attrs.get(bstack11ll1_opy_ (u"ࠧࡪࡦࠪ࿕"), None)
        self.bstack111ll11l11_opy_(bstack11ll1_opy_ (u"ࠨࡖࡨࡷࡹࡘࡵ࡯ࡕࡷࡥࡷࡺࡥࡥࠩ࿖"), bstack111l1ll11l_opy_)
    @error_handler(class_method=True)
    def end_test(self, name, attrs):
        self.bstack111ll11ll1_opy_.reset()
        bstack1111l1l1ll_opy_ = bstack111l11ll11_opy_.get(attrs.get(bstack11ll1_opy_ (u"ࠩࡶࡸࡦࡺࡵࡴࠩ࿗")), bstack11ll1_opy_ (u"ࠪࡷࡰ࡯ࡰࡱࡧࡧࠫ࿘"))
        self._1111l1ll1l_opy_[attrs.get(bstack11ll1_opy_ (u"ࠫ࡮ࡪࠧ࿙"))][bstack11ll1_opy_ (u"ࠬࡺࡥࡴࡶࡢࡨࡦࡺࡡࠨ࿚")].stop(time=bstack111lll1lll_opy_(), duration=int(attrs.get(bstack11ll1_opy_ (u"࠭ࡥ࡭ࡣࡳࡷࡪࡪࡴࡪ࡯ࡨࠫ࿛"), bstack11ll1_opy_ (u"ࠧ࠱ࠩ࿜"))), result=Result(result=bstack1111l1l1ll_opy_, exception=attrs.get(bstack11ll1_opy_ (u"ࠨ࡯ࡨࡷࡸࡧࡧࡦࠩ࿝")), bstack111l1l1ll1_opy_=[attrs.get(bstack11ll1_opy_ (u"ࠩࡰࡩࡸࡹࡡࡨࡧࠪ࿞"))]))
        self.bstack111ll11l11_opy_(bstack11ll1_opy_ (u"ࠪࡘࡪࡹࡴࡓࡷࡱࡊ࡮ࡴࡩࡴࡪࡨࡨࠬ࿟"), self._1111l1ll1l_opy_[attrs.get(bstack11ll1_opy_ (u"ࠫ࡮ࡪࠧ࿠"))][bstack11ll1_opy_ (u"ࠬࡺࡥࡴࡶࡢࡨࡦࡺࡡࠨ࿡")], True)
        with self._lock:
            self.store[bstack11ll1_opy_ (u"࠭ࡴࡦࡵࡷࡣ࡭ࡵ࡯࡬ࡵࠪ࿢")] = []
        threading.current_thread().current_test_uuid = None
        threading.current_thread().current_test_id = None
    @error_handler(class_method=True)
    def start_keyword(self, name, attrs):
        self.messages.bstack1111lll111_opy_()
        current_test_id = bstack1lll11l1l_opy_(threading.current_thread(), bstack11ll1_opy_ (u"ࠧࡤࡷࡵࡶࡪࡴࡴࡠࡶࡨࡷࡹࡥࡩࡥࠩ࿣"), None)
        bstack1111l111l1_opy_ = current_test_id if bstack1lll11l1l_opy_(threading.current_thread(), bstack11ll1_opy_ (u"ࠨࡥࡸࡶࡷ࡫࡮ࡵࡡࡷࡩࡸࡺ࡟ࡪࡦࠪ࿤"), None) else bstack1lll11l1l_opy_(threading.current_thread(), bstack11ll1_opy_ (u"ࠩࡦࡹࡷࡸࡥ࡯ࡶࡢࡷࡺ࡯ࡴࡦࡡ࡬ࡨࠬ࿥"), None)
        if attrs.get(bstack11ll1_opy_ (u"ࠪࡸࡾࡶࡥࠨ࿦"), bstack11ll1_opy_ (u"ࠫࠬ࿧")).lower() in [bstack11ll1_opy_ (u"ࠬࡹࡥࡵࡷࡳࠫ࿨"), bstack11ll1_opy_ (u"࠭ࡴࡦࡣࡵࡨࡴࡽ࡮ࠨ࿩")]:
            hook_type = bstack1111lll1l1_opy_(attrs.get(bstack11ll1_opy_ (u"ࠧࡵࡻࡳࡩࠬ࿪")), bstack1lll11l1l_opy_(threading.current_thread(), bstack11ll1_opy_ (u"ࠨࡥࡸࡶࡷ࡫࡮ࡵࡡࡷࡩࡸࡺ࡟ࡶࡷ࡬ࡨࠬ࿫"), None))
            hook_name = bstack11ll1_opy_ (u"ࠩࡾࢁࠬ࿬").format(attrs.get(bstack11ll1_opy_ (u"ࠪ࡯ࡼࡴࡡ࡮ࡧࠪ࿭"), bstack11ll1_opy_ (u"ࠫࠬ࿮")))
            if hook_type in [bstack11ll1_opy_ (u"ࠬࡈࡅࡇࡑࡕࡉࡤࡇࡌࡍࠩ࿯"), bstack11ll1_opy_ (u"࠭ࡁࡇࡖࡈࡖࡤࡇࡌࡍࠩ࿰")]:
                hook_name = bstack11ll1_opy_ (u"ࠧ࡜ࡽࢀࡡࠥࢁࡽࠨ࿱").format(bstack1111l111ll_opy_.get(hook_type), attrs.get(bstack11ll1_opy_ (u"ࠨ࡭ࡺࡲࡦࡳࡥࠨ࿲"), bstack11ll1_opy_ (u"ࠩࠪ࿳")))
            bstack1111llll11_opy_ = bstack111l1ll1l1_opy_(
                bstack1111ll11l1_opy_=bstack1111l111l1_opy_ + bstack11ll1_opy_ (u"ࠪ࠱ࠬ࿴") + attrs.get(bstack11ll1_opy_ (u"ࠫࡹࡿࡰࡦࠩ࿵"), bstack11ll1_opy_ (u"ࠬ࠭࿶")).lower(),
                name=hook_name,
                started_at=bstack111lll1lll_opy_(),
                file_path=os.path.relpath(attrs.get(bstack11ll1_opy_ (u"࠭ࡳࡰࡷࡵࡧࡪ࠭࿷")), start=os.getcwd()),
                framework=bstack11ll1_opy_ (u"ࠧࡓࡱࡥࡳࡹ࠭࿸"),
                tags=attrs[bstack11ll1_opy_ (u"ࠨࡶࡤ࡫ࡸ࠭࿹")],
                scope=RobotHandler.bstack111l11l1l1_opy_(attrs.get(bstack11ll1_opy_ (u"ࠩࡶࡳࡺࡸࡣࡦࠩ࿺"), None)),
                hook_type=hook_type,
                meta={}
            )
            threading.current_thread().current_hook_uuid = bstack1111llll11_opy_.bstack111l111l1l_opy_()
            threading.current_thread().current_hook_id = bstack1111l111l1_opy_ + bstack11ll1_opy_ (u"ࠪ࠱ࠬ࿻") + attrs.get(bstack11ll1_opy_ (u"ࠫࡹࡿࡰࡦࠩ࿼"), bstack11ll1_opy_ (u"ࠬ࠭࿽")).lower()
            with self._lock:
                self.store[bstack11ll1_opy_ (u"࠭ࡣࡶࡴࡵࡩࡳࡺ࡟ࡩࡱࡲ࡯ࡤࡻࡵࡪࡦࠪ࿾")] = [bstack1111llll11_opy_.bstack111l111l1l_opy_()]
                if bstack1lll11l1l_opy_(threading.current_thread(), bstack11ll1_opy_ (u"ࠧࡤࡷࡵࡶࡪࡴࡴࡠࡶࡨࡷࡹࡥࡵࡶ࡫ࡧࠫ࿿"), None):
                    self.store[bstack11ll1_opy_ (u"ࠨࡶࡨࡷࡹࡥࡨࡰࡱ࡮ࡷࠬက")].append(bstack1111llll11_opy_.bstack111l111l1l_opy_())
                else:
                    self.store[bstack11ll1_opy_ (u"ࠩࡪࡰࡴࡨࡡ࡭ࡡ࡫ࡳࡴࡱࡳࠨခ")].append(bstack1111llll11_opy_.bstack111l111l1l_opy_())
            if bstack1111l111l1_opy_:
                self._1111l1ll1l_opy_[bstack1111l111l1_opy_ + bstack11ll1_opy_ (u"ࠪ࠱ࠬဂ") + attrs.get(bstack11ll1_opy_ (u"ࠫࡹࡿࡰࡦࠩဃ"), bstack11ll1_opy_ (u"ࠬ࠭င")).lower()] = { bstack11ll1_opy_ (u"࠭ࡴࡦࡵࡷࡣࡩࡧࡴࡢࠩစ"): bstack1111llll11_opy_ }
            bstack11lll11l11_opy_.bstack111ll11l11_opy_(bstack11ll1_opy_ (u"ࠧࡉࡱࡲ࡯ࡗࡻ࡮ࡔࡶࡤࡶࡹ࡫ࡤࠨဆ"), bstack1111llll11_opy_)
        else:
            bstack111ll1111l_opy_ = {
                bstack11ll1_opy_ (u"ࠨ࡫ࡧࠫဇ"): uuid4().__str__(),
                bstack11ll1_opy_ (u"ࠩࡷࡩࡽࡺࠧဈ"): bstack11ll1_opy_ (u"ࠪࡿࢂࠦࡻࡾࠩဉ").format(attrs.get(bstack11ll1_opy_ (u"ࠫࡰࡽ࡮ࡢ࡯ࡨࠫည")), attrs.get(bstack11ll1_opy_ (u"ࠬࡧࡲࡨࡵࠪဋ"), bstack11ll1_opy_ (u"࠭ࠧဌ"))) if attrs.get(bstack11ll1_opy_ (u"ࠧࡢࡴࡪࡷࠬဍ"), []) else attrs.get(bstack11ll1_opy_ (u"ࠨ࡭ࡺࡲࡦࡳࡥࠨဎ")),
                bstack11ll1_opy_ (u"ࠩࡶࡸࡪࡶ࡟ࡢࡴࡪࡹࡲ࡫࡮ࡵࠩဏ"): attrs.get(bstack11ll1_opy_ (u"ࠪࡥࡷ࡭ࡳࠨတ"), []),
                bstack11ll1_opy_ (u"ࠫࡸࡺࡡࡳࡶࡨࡨࡤࡧࡴࠨထ"): bstack111lll1lll_opy_(),
                bstack11ll1_opy_ (u"ࠬࡸࡥࡴࡷ࡯ࡸࠬဒ"): bstack11ll1_opy_ (u"࠭ࡰࡦࡰࡧ࡭ࡳ࡭ࠧဓ"),
                bstack11ll1_opy_ (u"ࠧࡥࡧࡶࡧࡷ࡯ࡰࡵ࡫ࡲࡲࠬန"): attrs.get(bstack11ll1_opy_ (u"ࠨࡦࡲࡧࠬပ"), bstack11ll1_opy_ (u"ࠩࠪဖ"))
            }
            if attrs.get(bstack11ll1_opy_ (u"ࠪࡰ࡮ࡨ࡮ࡢ࡯ࡨࠫဗ"), bstack11ll1_opy_ (u"ࠫࠬဘ")) != bstack11ll1_opy_ (u"ࠬ࠭မ"):
                bstack111ll1111l_opy_[bstack11ll1_opy_ (u"࠭࡫ࡦࡻࡺࡳࡷࡪࠧယ")] = attrs.get(bstack11ll1_opy_ (u"ࠧ࡭࡫ࡥࡲࡦࡳࡥࠨရ"))
            if not self.bstack111l1111l1_opy_:
                self._1111l1ll1l_opy_[self._1111llll1l_opy_()][bstack11ll1_opy_ (u"ࠨࡶࡨࡷࡹࡥࡤࡢࡶࡤࠫလ")].add_step(bstack111ll1111l_opy_)
                threading.current_thread().current_step_uuid = bstack111ll1111l_opy_[bstack11ll1_opy_ (u"ࠩ࡬ࡨࠬဝ")]
            self.bstack111l1111l1_opy_.append(bstack111ll1111l_opy_)
    @error_handler(class_method=True)
    def end_keyword(self, name, attrs):
        messages = self.messages.bstack1111ll111l_opy_()
        self._1111lll11l_opy_(messages)
        current_test_id = bstack1lll11l1l_opy_(threading.current_thread(), bstack11ll1_opy_ (u"ࠪࡧࡺࡸࡲࡦࡰࡷࡣࡹ࡫ࡳࡵࡡ࡬ࡨࠬသ"), None)
        bstack1111l111l1_opy_ = current_test_id if current_test_id else bstack1lll11l1l_opy_(threading.current_thread(), bstack11ll1_opy_ (u"ࠫࡨࡻࡲࡳࡧࡱࡸࡤࡹࡵࡪࡶࡨࡣ࡮ࡪࠧဟ"), None)
        bstack1111l11l11_opy_ = bstack111l11ll11_opy_.get(attrs.get(bstack11ll1_opy_ (u"ࠬࡹࡴࡢࡶࡸࡷࠬဠ")), bstack11ll1_opy_ (u"࠭ࡳ࡬࡫ࡳࡴࡪࡪࠧအ"))
        bstack1111lllll1_opy_ = attrs.get(bstack11ll1_opy_ (u"ࠧ࡮ࡧࡶࡷࡦ࡭ࡥࠨဢ"))
        if bstack1111l11l11_opy_ != bstack11ll1_opy_ (u"ࠨࡵ࡮࡭ࡵࡶࡥࡥࠩဣ") and not attrs.get(bstack11ll1_opy_ (u"ࠩࡰࡩࡸࡹࡡࡨࡧࠪဤ")) and self._1111ll1lll_opy_:
            bstack1111lllll1_opy_ = self._1111ll1lll_opy_
        bstack111l1lll1l_opy_ = Result(result=bstack1111l11l11_opy_, exception=bstack1111lllll1_opy_, bstack111l1l1ll1_opy_=[bstack1111lllll1_opy_])
        if attrs.get(bstack11ll1_opy_ (u"ࠪࡸࡾࡶࡥࠨဥ"), bstack11ll1_opy_ (u"ࠫࠬဦ")).lower() in [bstack11ll1_opy_ (u"ࠬࡹࡥࡵࡷࡳࠫဧ"), bstack11ll1_opy_ (u"࠭ࡴࡦࡣࡵࡨࡴࡽ࡮ࠨဨ")]:
            bstack1111l111l1_opy_ = current_test_id if current_test_id else bstack1lll11l1l_opy_(threading.current_thread(), bstack11ll1_opy_ (u"ࠧࡤࡷࡵࡶࡪࡴࡴࡠࡵࡸ࡭ࡹ࡫࡟ࡪࡦࠪဩ"), None)
            if bstack1111l111l1_opy_:
                bstack111l1lll11_opy_ = bstack1111l111l1_opy_ + bstack11ll1_opy_ (u"ࠣ࠯ࠥဪ") + attrs.get(bstack11ll1_opy_ (u"ࠩࡷࡽࡵ࡫ࠧါ"), bstack11ll1_opy_ (u"ࠪࠫာ")).lower()
                self._1111l1ll1l_opy_[bstack111l1lll11_opy_][bstack11ll1_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡧࡥࡹࡧࠧိ")].stop(time=bstack111lll1lll_opy_(), duration=int(attrs.get(bstack11ll1_opy_ (u"ࠬ࡫࡬ࡢࡲࡶࡩࡩࡺࡩ࡮ࡧࠪီ"), bstack11ll1_opy_ (u"࠭࠰ࠨု"))), result=bstack111l1lll1l_opy_)
                bstack11lll11l11_opy_.bstack111ll11l11_opy_(bstack11ll1_opy_ (u"ࠧࡉࡱࡲ࡯ࡗࡻ࡮ࡇ࡫ࡱ࡭ࡸ࡮ࡥࡥࠩူ"), self._1111l1ll1l_opy_[bstack111l1lll11_opy_][bstack11ll1_opy_ (u"ࠨࡶࡨࡷࡹࡥࡤࡢࡶࡤࠫေ")])
        else:
            bstack1111l111l1_opy_ = current_test_id if current_test_id else bstack1lll11l1l_opy_(threading.current_thread(), bstack11ll1_opy_ (u"ࠩࡦࡹࡷࡸࡥ࡯ࡶࡢ࡬ࡴࡵ࡫ࡠ࡫ࡧࠫဲ"), None)
            if bstack1111l111l1_opy_ and len(self.bstack111l1111l1_opy_) == 1:
                current_step_uuid = bstack1lll11l1l_opy_(threading.current_thread(), bstack11ll1_opy_ (u"ࠪࡧࡺࡸࡲࡦࡰࡷࡣࡸࡺࡥࡱࡡࡸࡹ࡮ࡪࠧဳ"), None)
                self._1111l1ll1l_opy_[bstack1111l111l1_opy_][bstack11ll1_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡧࡥࡹࡧࠧဴ")].bstack111l1ll1ll_opy_(current_step_uuid, duration=int(attrs.get(bstack11ll1_opy_ (u"ࠬ࡫࡬ࡢࡲࡶࡩࡩࡺࡩ࡮ࡧࠪဵ"), bstack11ll1_opy_ (u"࠭࠰ࠨံ"))), result=bstack111l1lll1l_opy_)
            else:
                self.bstack1111l11111_opy_(attrs)
            self.bstack111l1111l1_opy_.pop()
    def log_message(self, message):
        try:
            if message.get(bstack11ll1_opy_ (u"ࠧࡩࡶࡰࡰ့ࠬ"), bstack11ll1_opy_ (u"ࠨࡰࡲࠫး")) == bstack11ll1_opy_ (u"ࠩࡼࡩࡸ္࠭"):
                return
            self.messages.push(message)
            logs = []
            if bstack1l11llll1l_opy_.bstack111ll111l1_opy_():
                logs.append({
                    bstack11ll1_opy_ (u"ࠪࡸ࡮ࡳࡥࡴࡶࡤࡱࡵ်࠭"): bstack111lll1lll_opy_(),
                    bstack11ll1_opy_ (u"ࠫࡲ࡫ࡳࡴࡣࡪࡩࠬျ"): message.get(bstack11ll1_opy_ (u"ࠬࡳࡥࡴࡵࡤ࡫ࡪ࠭ြ")),
                    bstack11ll1_opy_ (u"࠭࡬ࡦࡸࡨࡰࠬွ"): message.get(bstack11ll1_opy_ (u"ࠧ࡭ࡧࡹࡩࡱ࠭ှ")),
                    **bstack1l11llll1l_opy_.bstack111ll111l1_opy_()
                })
                if len(logs) > 0:
                    bstack11lll11l11_opy_.bstack1l1l11l11l_opy_(logs)
        except Exception as err:
            pass
    def close(self):
        bstack11lll11l11_opy_.bstack1111l1l1l1_opy_()
    def bstack1111l11111_opy_(self, bstack1111l11ll1_opy_):
        if not bstack1l11llll1l_opy_.bstack111ll111l1_opy_():
            return
        kwname = bstack11ll1_opy_ (u"ࠨࡽࢀࠤࢀࢃࠧဿ").format(bstack1111l11ll1_opy_.get(bstack11ll1_opy_ (u"ࠩ࡮ࡻࡳࡧ࡭ࡦࠩ၀")), bstack1111l11ll1_opy_.get(bstack11ll1_opy_ (u"ࠪࡥࡷ࡭ࡳࠨ၁"), bstack11ll1_opy_ (u"ࠫࠬ၂"))) if bstack1111l11ll1_opy_.get(bstack11ll1_opy_ (u"ࠬࡧࡲࡨࡵࠪ၃"), []) else bstack1111l11ll1_opy_.get(bstack11ll1_opy_ (u"࠭࡫ࡸࡰࡤࡱࡪ࠭၄"))
        error_message = bstack11ll1_opy_ (u"ࠢ࡬ࡹࡱࡥࡲ࡫࠺ࠡ࡞ࠥࡿ࠵ࢃ࡜ࠣࠢࡿࠤࡸࡺࡡࡵࡷࡶ࠾ࠥࡢࠢࡼ࠳ࢀࡠࠧࠦࡼࠡࡧࡻࡧࡪࡶࡴࡪࡱࡱ࠾ࠥࡢࠢࡼ࠴ࢀࡠࠧࠨ၅").format(kwname, bstack1111l11ll1_opy_.get(bstack11ll1_opy_ (u"ࠨࡵࡷࡥࡹࡻࡳࠨ၆")), str(bstack1111l11ll1_opy_.get(bstack11ll1_opy_ (u"ࠩࡰࡩࡸࡹࡡࡨࡧࠪ၇"))))
        bstack1111l1lll1_opy_ = bstack11ll1_opy_ (u"ࠥ࡯ࡼࡴࡡ࡮ࡧ࠽ࠤࡡࠨࡻ࠱ࡿ࡟ࠦࠥࢂࠠࡴࡶࡤࡸࡺࡹ࠺ࠡ࡞ࠥࡿ࠶ࢃ࡜ࠣࠤ၈").format(kwname, bstack1111l11ll1_opy_.get(bstack11ll1_opy_ (u"ࠫࡸࡺࡡࡵࡷࡶࠫ၉")))
        bstack111l11lll1_opy_ = error_message if bstack1111l11ll1_opy_.get(bstack11ll1_opy_ (u"ࠬࡳࡥࡴࡵࡤ࡫ࡪ࠭၊")) else bstack1111l1lll1_opy_
        bstack111l111l11_opy_ = {
            bstack11ll1_opy_ (u"࠭ࡴࡪ࡯ࡨࡷࡹࡧ࡭ࡱࠩ။"): self.bstack111l1111l1_opy_[-1].get(bstack11ll1_opy_ (u"ࠧࡴࡶࡤࡶࡹ࡫ࡤࡠࡣࡷࠫ၌"), bstack111lll1lll_opy_()),
            bstack11ll1_opy_ (u"ࠨ࡯ࡨࡷࡸࡧࡧࡦࠩ၍"): bstack111l11lll1_opy_,
            bstack11ll1_opy_ (u"ࠩ࡯ࡩࡻ࡫࡬ࠨ၎"): bstack11ll1_opy_ (u"ࠪࡉࡗࡘࡏࡓࠩ၏") if bstack1111l11ll1_opy_.get(bstack11ll1_opy_ (u"ࠫࡸࡺࡡࡵࡷࡶࠫၐ")) == bstack11ll1_opy_ (u"ࠬࡌࡁࡊࡎࠪၑ") else bstack11ll1_opy_ (u"࠭ࡉࡏࡈࡒࠫၒ"),
            **bstack1l11llll1l_opy_.bstack111ll111l1_opy_()
        }
        bstack11lll11l11_opy_.bstack1l1l11l11l_opy_([bstack111l111l11_opy_])
    def _1111llll1l_opy_(self):
        for bstack1111ll11l1_opy_ in reversed(self._1111l1ll1l_opy_):
            bstack111l11l111_opy_ = bstack1111ll11l1_opy_
            data = self._1111l1ll1l_opy_[bstack1111ll11l1_opy_][bstack11ll1_opy_ (u"ࠧࡵࡧࡶࡸࡤࡪࡡࡵࡣࠪၓ")]
            if isinstance(data, bstack111l1ll1l1_opy_):
                if not bstack11ll1_opy_ (u"ࠨࡇࡄࡇࡍ࠭ၔ") in data.bstack1111ll1l1l_opy_():
                    return bstack111l11l111_opy_
            else:
                return bstack111l11l111_opy_
    def _1111lll11l_opy_(self, messages):
        try:
            bstack1111l1l111_opy_ = BuiltIn().get_variable_value(bstack11ll1_opy_ (u"ࠤࠧࡿࡑࡕࡇࠡࡎࡈ࡚ࡊࡒࡽࠣၕ")) in (bstack1111l1111l_opy_.DEBUG, bstack1111l1111l_opy_.TRACE)
            for message, bstack1111lll1ll_opy_ in zip_longest(messages, messages[1:]):
                name = message.get(bstack11ll1_opy_ (u"ࠪࡱࡪࡹࡳࡢࡩࡨࠫၖ"))
                level = message.get(bstack11ll1_opy_ (u"ࠫࡱ࡫ࡶࡦ࡮ࠪၗ"))
                if level == bstack1111l1111l_opy_.FAIL:
                    self._1111ll1lll_opy_ = name or self._1111ll1lll_opy_
                    self._111l111111_opy_ = bstack1111lll1ll_opy_.get(bstack11ll1_opy_ (u"ࠧࡳࡥࡴࡵࡤ࡫ࡪࠨၘ")) if bstack1111l1l111_opy_ and bstack1111lll1ll_opy_ else self._111l111111_opy_
        except:
            pass
    @classmethod
    def bstack111ll11l11_opy_(self, event: str, bstack1111l1l11l_opy_: bstack111l111lll_opy_, bstack111l11ll1l_opy_=False):
        if event == bstack11ll1_opy_ (u"࠭ࡔࡦࡵࡷࡖࡺࡴࡆࡪࡰ࡬ࡷ࡭࡫ࡤࠨၙ"):
            bstack1111l1l11l_opy_.set(hooks=self.store[bstack11ll1_opy_ (u"ࠧࡵࡧࡶࡸࡤ࡮࡯ࡰ࡭ࡶࠫၚ")])
        if event == bstack11ll1_opy_ (u"ࠨࡖࡨࡷࡹࡘࡵ࡯ࡕ࡮࡭ࡵࡶࡥࡥࠩၛ"):
            event = bstack11ll1_opy_ (u"ࠩࡗࡩࡸࡺࡒࡶࡰࡉ࡭ࡳ࡯ࡳࡩࡧࡧࠫၜ")
        if bstack111l11ll1l_opy_:
            bstack1111l1llll_opy_ = {
                bstack11ll1_opy_ (u"ࠪࡩࡻ࡫࡮ࡵࡡࡷࡽࡵ࡫ࠧၝ"): event,
                bstack1111l1l11l_opy_.bstack1111ll1111_opy_(): bstack1111l1l11l_opy_.bstack111l111ll1_opy_(event)
            }
            with self._lock:
                self.bstack111l1111ll_opy_.append(bstack1111l1llll_opy_)
        else:
            bstack11lll11l11_opy_.bstack111ll11l11_opy_(event, bstack1111l1l11l_opy_)
class bstack111l11111l_opy_:
    def __init__(self):
        self._1111l11l1l_opy_ = []
    def bstack1111lll111_opy_(self):
        self._1111l11l1l_opy_.append([])
    def bstack1111ll111l_opy_(self):
        return self._1111l11l1l_opy_.pop() if self._1111l11l1l_opy_ else list()
    def push(self, message):
        self._1111l11l1l_opy_[-1].append(message) if self._1111l11l1l_opy_ else self._1111l11l1l_opy_.append([message])
class bstack1111l1111l_opy_:
    FAIL = bstack11ll1_opy_ (u"ࠫࡋࡇࡉࡍࠩၞ")
    ERROR = bstack11ll1_opy_ (u"ࠬࡋࡒࡓࡑࡕࠫၟ")
    WARNING = bstack11ll1_opy_ (u"࠭ࡗࡂࡔࡑࠫၠ")
    bstack1111l1ll11_opy_ = bstack11ll1_opy_ (u"ࠧࡊࡐࡉࡓࠬၡ")
    DEBUG = bstack11ll1_opy_ (u"ࠨࡆࡈࡆ࡚ࡍࠧၢ")
    TRACE = bstack11ll1_opy_ (u"ࠩࡗࡖࡆࡉࡅࠨၣ")
    bstack1111ll11ll_opy_ = [FAIL, ERROR]
def bstack1111llllll_opy_(bstack1111ll1l11_opy_):
    if not bstack1111ll1l11_opy_:
        return None
    if bstack1111ll1l11_opy_.get(bstack11ll1_opy_ (u"ࠪࡸࡪࡹࡴࡠࡦࡤࡸࡦ࠭ၤ"), None):
        return getattr(bstack1111ll1l11_opy_[bstack11ll1_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡧࡥࡹࡧࠧၥ")], bstack11ll1_opy_ (u"ࠬࡻࡵࡪࡦࠪၦ"), None)
    return bstack1111ll1l11_opy_.get(bstack11ll1_opy_ (u"࠭ࡵࡶ࡫ࡧࠫၧ"), None)
def bstack1111lll1l1_opy_(hook_type, current_test_uuid):
    if hook_type.lower() not in [bstack11ll1_opy_ (u"ࠧࡴࡧࡷࡹࡵ࠭ၨ"), bstack11ll1_opy_ (u"ࠨࡶࡨࡥࡷࡪ࡯ࡸࡰࠪၩ")]:
        return
    if hook_type.lower() == bstack11ll1_opy_ (u"ࠩࡶࡩࡹࡻࡰࠨၪ"):
        if current_test_uuid is None:
            return bstack11ll1_opy_ (u"ࠪࡆࡊࡌࡏࡓࡇࡢࡅࡑࡒࠧၫ")
        else:
            return bstack11ll1_opy_ (u"ࠫࡇࡋࡆࡐࡔࡈࡣࡊࡇࡃࡉࠩၬ")
    elif hook_type.lower() == bstack11ll1_opy_ (u"ࠬࡺࡥࡢࡴࡧࡳࡼࡴࠧၭ"):
        if current_test_uuid is None:
            return bstack11ll1_opy_ (u"࠭ࡁࡇࡖࡈࡖࡤࡇࡌࡍࠩၮ")
        else:
            return bstack11ll1_opy_ (u"ࠧࡂࡈࡗࡉࡗࡥࡅࡂࡅࡋࠫၯ")