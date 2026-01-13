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
import os
import threading
from uuid import uuid4
from itertools import zip_longest
from collections import OrderedDict
from robot.libraries.BuiltIn import BuiltIn
from browserstack_sdk.bstack111l111111_opy_ import RobotHandler
from bstack_utils.capture import bstack111l1l11ll_opy_
from bstack_utils.bstack111l1lllll_opy_ import bstack1111l11ll1_opy_, bstack111l1lll11_opy_, bstack111l1l1111_opy_
from bstack_utils.bstack111ll11111_opy_ import bstack11llll111_opy_
from bstack_utils.bstack111l1lll1l_opy_ import bstack1ll1llll11_opy_
from bstack_utils.constants import *
from bstack_utils.helper import bstack11lll11l_opy_, bstack1lllll111_opy_, Result, \
    error_handler, bstack1111ll1l1l_opy_
class bstack_robot_listener:
    ROBOT_LISTENER_API_VERSION = 2
    _lock = threading.Lock()
    store = {
        bstack11l1l_opy_ (u"ࠪࡧࡺࡸࡲࡦࡰࡷࡣ࡭ࡵ࡯࡬ࡡࡸࡹ࡮ࡪࠧྠ"): [],
        bstack11l1l_opy_ (u"ࠫ࡬ࡲ࡯ࡣࡣ࡯ࡣ࡭ࡵ࡯࡬ࡵࠪྡ"): [],
        bstack11l1l_opy_ (u"ࠬࡺࡥࡴࡶࡢ࡬ࡴࡵ࡫ࡴࠩྡྷ"): []
    }
    bstack111l11111l_opy_ = []
    bstack111l1111l1_opy_ = []
    @staticmethod
    def bstack111l1l1ll1_opy_(log):
        if not ((isinstance(log[bstack11l1l_opy_ (u"࠭࡭ࡦࡵࡶࡥ࡬࡫ࠧྣ")], list) or (isinstance(log[bstack11l1l_opy_ (u"ࠧ࡮ࡧࡶࡷࡦ࡭ࡥࠨྤ")], dict)) and len(log[bstack11l1l_opy_ (u"ࠨ࡯ࡨࡷࡸࡧࡧࡦࠩྥ")])>0) or (isinstance(log[bstack11l1l_opy_ (u"ࠩࡰࡩࡸࡹࡡࡨࡧࠪྦ")], str) and log[bstack11l1l_opy_ (u"ࠪࡱࡪࡹࡳࡢࡩࡨࠫྦྷ")].strip())):
            return
        active = bstack11llll111_opy_.bstack111ll111ll_opy_()
        log = {
            bstack11l1l_opy_ (u"ࠫࡱ࡫ࡶࡦ࡮ࠪྨ"): log[bstack11l1l_opy_ (u"ࠬࡲࡥࡷࡧ࡯ࠫྩ")],
            bstack11l1l_opy_ (u"࠭ࡴࡪ࡯ࡨࡷࡹࡧ࡭ࡱࠩྪ"): bstack1111ll1l1l_opy_().isoformat() + bstack11l1l_opy_ (u"࡛ࠧࠩྫ"),
            bstack11l1l_opy_ (u"ࠨ࡯ࡨࡷࡸࡧࡧࡦࠩྫྷ"): log[bstack11l1l_opy_ (u"ࠩࡰࡩࡸࡹࡡࡨࡧࠪྭ")],
        }
        if active:
            if active[bstack11l1l_opy_ (u"ࠪࡸࡾࡶࡥࠨྮ")] == bstack11l1l_opy_ (u"ࠫ࡭ࡵ࡯࡬ࠩྯ"):
                log[bstack11l1l_opy_ (u"ࠬ࡮࡯ࡰ࡭ࡢࡶࡺࡴ࡟ࡶࡷ࡬ࡨࠬྰ")] = active[bstack11l1l_opy_ (u"࠭ࡨࡰࡱ࡮ࡣࡷࡻ࡮ࡠࡷࡸ࡭ࡩ࠭ྱ")]
            elif active[bstack11l1l_opy_ (u"ࠧࡵࡻࡳࡩࠬྲ")] == bstack11l1l_opy_ (u"ࠨࡶࡨࡷࡹ࠭ླ"):
                log[bstack11l1l_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡳࡷࡱࡣࡺࡻࡩࡥࠩྴ")] = active[bstack11l1l_opy_ (u"ࠪࡸࡪࡹࡴࡠࡴࡸࡲࡤࡻࡵࡪࡦࠪྵ")]
        bstack1ll1llll11_opy_.bstack11lllll1l_opy_([log])
    def __init__(self):
        self.messages = bstack1111lll11l_opy_()
        self._111l111lll_opy_ = None
        self._1111ll1lll_opy_ = None
        self._1111lll1ll_opy_ = OrderedDict()
        self.bstack111ll1111l_opy_ = bstack111l1l11ll_opy_(self.bstack111l1l1ll1_opy_)
    @error_handler(class_method=True)
    def start_suite(self, name, attrs):
        self.messages.bstack1111llll1l_opy_()
        if not self._1111lll1ll_opy_.get(attrs.get(bstack11l1l_opy_ (u"ࠫ࡮ࡪࠧྶ")), None):
            self._1111lll1ll_opy_[attrs.get(bstack11l1l_opy_ (u"ࠬ࡯ࡤࠨྷ"))] = {}
        bstack1111l111l1_opy_ = bstack111l1l1111_opy_(
                bstack1111l1llll_opy_=attrs.get(bstack11l1l_opy_ (u"࠭ࡩࡥࠩྸ")),
                name=name,
                started_at=bstack1lllll111_opy_(),
                file_path=os.path.relpath(attrs[bstack11l1l_opy_ (u"ࠧࡴࡱࡸࡶࡨ࡫ࠧྐྵ")], start=os.getcwd()) if attrs.get(bstack11l1l_opy_ (u"ࠨࡵࡲࡹࡷࡩࡥࠨྺ")) != bstack11l1l_opy_ (u"ࠩࠪྻ") else bstack11l1l_opy_ (u"ࠪࠫྼ"),
                framework=bstack11l1l_opy_ (u"ࠫࡗࡵࡢࡰࡶࠪ྽")
            )
        threading.current_thread().current_suite_id = attrs.get(bstack11l1l_opy_ (u"ࠬ࡯ࡤࠨ྾"), None)
        self._1111lll1ll_opy_[attrs.get(bstack11l1l_opy_ (u"࠭ࡩࡥࠩ྿"))][bstack11l1l_opy_ (u"ࠧࡵࡧࡶࡸࡤࡪࡡࡵࡣࠪ࿀")] = bstack1111l111l1_opy_
    @error_handler(class_method=True)
    def end_suite(self, name, attrs):
        messages = self.messages.bstack111l111l1l_opy_()
        self._1111l11lll_opy_(messages)
        with self._lock:
            for bstack111l11l11l_opy_ in self.bstack111l11111l_opy_:
                bstack111l11l11l_opy_[bstack11l1l_opy_ (u"ࠨࡶࡨࡷࡹࡥࡲࡶࡰࠪ࿁")][bstack11l1l_opy_ (u"ࠩ࡫ࡳࡴࡱࡳࠨ࿂")].extend(self.store[bstack11l1l_opy_ (u"ࠪ࡫ࡱࡵࡢࡢ࡮ࡢ࡬ࡴࡵ࡫ࡴࠩ࿃")])
                bstack1ll1llll11_opy_.bstack1ll1l1111l_opy_(bstack111l11l11l_opy_)
            self.bstack111l11111l_opy_ = []
            self.store[bstack11l1l_opy_ (u"ࠫ࡬ࡲ࡯ࡣࡣ࡯ࡣ࡭ࡵ࡯࡬ࡵࠪ࿄")] = []
    @error_handler(class_method=True)
    def start_test(self, name, attrs):
        self.bstack111ll1111l_opy_.start()
        if not self._1111lll1ll_opy_.get(attrs.get(bstack11l1l_opy_ (u"ࠬ࡯ࡤࠨ࿅")), None):
            self._1111lll1ll_opy_[attrs.get(bstack11l1l_opy_ (u"࠭ࡩࡥ࿆ࠩ"))] = {}
        driver = bstack11lll11l_opy_(threading.current_thread(), bstack11l1l_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱࡓࡦࡵࡶ࡭ࡴࡴࡄࡳ࡫ࡹࡩࡷ࠭࿇"), None)
        bstack111l1lllll_opy_ = bstack111l1l1111_opy_(
            bstack1111l1llll_opy_=attrs.get(bstack11l1l_opy_ (u"ࠨ࡫ࡧࠫ࿈")),
            name=name,
            started_at=bstack1lllll111_opy_(),
            file_path=os.path.relpath(attrs[bstack11l1l_opy_ (u"ࠩࡶࡳࡺࡸࡣࡦࠩ࿉")], start=os.getcwd()),
            scope=RobotHandler.bstack1111l1ll11_opy_(attrs.get(bstack11l1l_opy_ (u"ࠪࡷࡴࡻࡲࡤࡧࠪ࿊"), None)),
            framework=bstack11l1l_opy_ (u"ࠫࡗࡵࡢࡰࡶࠪ࿋"),
            tags=attrs[bstack11l1l_opy_ (u"ࠬࡺࡡࡨࡵࠪ࿌")],
            hooks=self.store[bstack11l1l_opy_ (u"࠭ࡧ࡭ࡱࡥࡥࡱࡥࡨࡰࡱ࡮ࡷࠬ࿍")],
            bstack111l1l1lll_opy_=bstack1ll1llll11_opy_.bstack111ll11l11_opy_(driver) if driver and driver.session_id else {},
            meta={},
            code=bstack11l1l_opy_ (u"ࠢࡼࡿࠣࡠࡳࠦࡻࡾࠤ࿎").format(bstack11l1l_opy_ (u"ࠣࠢࠥ࿏").join(attrs[bstack11l1l_opy_ (u"ࠩࡷࡥ࡬ࡹࠧ࿐")]), name) if attrs[bstack11l1l_opy_ (u"ࠪࡸࡦ࡭ࡳࠨ࿑")] else name
        )
        self._1111lll1ll_opy_[attrs.get(bstack11l1l_opy_ (u"ࠫ࡮ࡪࠧ࿒"))][bstack11l1l_opy_ (u"ࠬࡺࡥࡴࡶࡢࡨࡦࡺࡡࠨ࿓")] = bstack111l1lllll_opy_
        threading.current_thread().current_test_uuid = bstack111l1lllll_opy_.bstack1111ll11l1_opy_()
        threading.current_thread().current_test_id = attrs.get(bstack11l1l_opy_ (u"࠭ࡩࡥࠩ࿔"), None)
        self.bstack111ll11ll1_opy_(bstack11l1l_opy_ (u"ࠧࡕࡧࡶࡸࡗࡻ࡮ࡔࡶࡤࡶࡹ࡫ࡤࠨ࿕"), bstack111l1lllll_opy_)
    @error_handler(class_method=True)
    def end_test(self, name, attrs):
        self.bstack111ll1111l_opy_.reset()
        bstack1111l1lll1_opy_ = bstack111l111l11_opy_.get(attrs.get(bstack11l1l_opy_ (u"ࠨࡵࡷࡥࡹࡻࡳࠨ࿖")), bstack11l1l_opy_ (u"ࠩࡶ࡯࡮ࡶࡰࡦࡦࠪ࿗"))
        self._1111lll1ll_opy_[attrs.get(bstack11l1l_opy_ (u"ࠪ࡭ࡩ࠭࿘"))][bstack11l1l_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡧࡥࡹࡧࠧ࿙")].stop(time=bstack1lllll111_opy_(), duration=int(attrs.get(bstack11l1l_opy_ (u"ࠬ࡫࡬ࡢࡲࡶࡩࡩࡺࡩ࡮ࡧࠪ࿚"), bstack11l1l_opy_ (u"࠭࠰ࠨ࿛"))), result=Result(result=bstack1111l1lll1_opy_, exception=attrs.get(bstack11l1l_opy_ (u"ࠧ࡮ࡧࡶࡷࡦ࡭ࡥࠨ࿜")), bstack111l1l11l1_opy_=[attrs.get(bstack11l1l_opy_ (u"ࠨ࡯ࡨࡷࡸࡧࡧࡦࠩ࿝"))]))
        self.bstack111ll11ll1_opy_(bstack11l1l_opy_ (u"ࠩࡗࡩࡸࡺࡒࡶࡰࡉ࡭ࡳ࡯ࡳࡩࡧࡧࠫ࿞"), self._1111lll1ll_opy_[attrs.get(bstack11l1l_opy_ (u"ࠪ࡭ࡩ࠭࿟"))][bstack11l1l_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡧࡥࡹࡧࠧ࿠")], True)
        with self._lock:
            self.store[bstack11l1l_opy_ (u"ࠬࡺࡥࡴࡶࡢ࡬ࡴࡵ࡫ࡴࠩ࿡")] = []
        threading.current_thread().current_test_uuid = None
        threading.current_thread().current_test_id = None
    @error_handler(class_method=True)
    def start_keyword(self, name, attrs):
        self.messages.bstack1111llll1l_opy_()
        current_test_id = bstack11lll11l_opy_(threading.current_thread(), bstack11l1l_opy_ (u"࠭ࡣࡶࡴࡵࡩࡳࡺ࡟ࡵࡧࡶࡸࡤ࡯ࡤࠨ࿢"), None)
        bstack111l11lll1_opy_ = current_test_id if bstack11lll11l_opy_(threading.current_thread(), bstack11l1l_opy_ (u"ࠧࡤࡷࡵࡶࡪࡴࡴࡠࡶࡨࡷࡹࡥࡩࡥࠩ࿣"), None) else bstack11lll11l_opy_(threading.current_thread(), bstack11l1l_opy_ (u"ࠨࡥࡸࡶࡷ࡫࡮ࡵࡡࡶࡹ࡮ࡺࡥࡠ࡫ࡧࠫ࿤"), None)
        if attrs.get(bstack11l1l_opy_ (u"ࠩࡷࡽࡵ࡫ࠧ࿥"), bstack11l1l_opy_ (u"ࠪࠫ࿦")).lower() in [bstack11l1l_opy_ (u"ࠫࡸ࡫ࡴࡶࡲࠪ࿧"), bstack11l1l_opy_ (u"ࠬࡺࡥࡢࡴࡧࡳࡼࡴࠧ࿨")]:
            hook_type = bstack111l11l1ll_opy_(attrs.get(bstack11l1l_opy_ (u"࠭ࡴࡺࡲࡨࠫ࿩")), bstack11lll11l_opy_(threading.current_thread(), bstack11l1l_opy_ (u"ࠧࡤࡷࡵࡶࡪࡴࡴࡠࡶࡨࡷࡹࡥࡵࡶ࡫ࡧࠫ࿪"), None))
            hook_name = bstack11l1l_opy_ (u"ࠨࡽࢀࠫ࿫").format(attrs.get(bstack11l1l_opy_ (u"ࠩ࡮ࡻࡳࡧ࡭ࡦࠩ࿬"), bstack11l1l_opy_ (u"ࠪࠫ࿭")))
            if hook_type in [bstack11l1l_opy_ (u"ࠫࡇࡋࡆࡐࡔࡈࡣࡆࡒࡌࠨ࿮"), bstack11l1l_opy_ (u"ࠬࡇࡆࡕࡇࡕࡣࡆࡒࡌࠨ࿯")]:
                hook_name = bstack11l1l_opy_ (u"࡛࠭ࡼࡿࡠࠤࢀࢃࠧ࿰").format(bstack1111l1l1l1_opy_.get(hook_type), attrs.get(bstack11l1l_opy_ (u"ࠧ࡬ࡹࡱࡥࡲ࡫ࠧ࿱"), bstack11l1l_opy_ (u"ࠨࠩ࿲")))
            bstack1111l1l11l_opy_ = bstack111l1lll11_opy_(
                bstack1111l1llll_opy_=bstack111l11lll1_opy_ + bstack11l1l_opy_ (u"ࠩ࠰ࠫ࿳") + attrs.get(bstack11l1l_opy_ (u"ࠪࡸࡾࡶࡥࠨ࿴"), bstack11l1l_opy_ (u"ࠫࠬ࿵")).lower(),
                name=hook_name,
                started_at=bstack1lllll111_opy_(),
                file_path=os.path.relpath(attrs.get(bstack11l1l_opy_ (u"ࠬࡹ࡯ࡶࡴࡦࡩࠬ࿶")), start=os.getcwd()),
                framework=bstack11l1l_opy_ (u"࠭ࡒࡰࡤࡲࡸࠬ࿷"),
                tags=attrs[bstack11l1l_opy_ (u"ࠧࡵࡣࡪࡷࠬ࿸")],
                scope=RobotHandler.bstack1111l1ll11_opy_(attrs.get(bstack11l1l_opy_ (u"ࠨࡵࡲࡹࡷࡩࡥࠨ࿹"), None)),
                hook_type=hook_type,
                meta={}
            )
            threading.current_thread().current_hook_uuid = bstack1111l1l11l_opy_.bstack1111ll11l1_opy_()
            threading.current_thread().current_hook_id = bstack111l11lll1_opy_ + bstack11l1l_opy_ (u"ࠩ࠰ࠫ࿺") + attrs.get(bstack11l1l_opy_ (u"ࠪࡸࡾࡶࡥࠨ࿻"), bstack11l1l_opy_ (u"ࠫࠬ࿼")).lower()
            with self._lock:
                self.store[bstack11l1l_opy_ (u"ࠬࡩࡵࡳࡴࡨࡲࡹࡥࡨࡰࡱ࡮ࡣࡺࡻࡩࡥࠩ࿽")] = [bstack1111l1l11l_opy_.bstack1111ll11l1_opy_()]
                if bstack11lll11l_opy_(threading.current_thread(), bstack11l1l_opy_ (u"࠭ࡣࡶࡴࡵࡩࡳࡺ࡟ࡵࡧࡶࡸࡤࡻࡵࡪࡦࠪ࿾"), None):
                    self.store[bstack11l1l_opy_ (u"ࠧࡵࡧࡶࡸࡤ࡮࡯ࡰ࡭ࡶࠫ࿿")].append(bstack1111l1l11l_opy_.bstack1111ll11l1_opy_())
                else:
                    self.store[bstack11l1l_opy_ (u"ࠨࡩ࡯ࡳࡧࡧ࡬ࡠࡪࡲࡳࡰࡹࠧက")].append(bstack1111l1l11l_opy_.bstack1111ll11l1_opy_())
            if bstack111l11lll1_opy_:
                self._1111lll1ll_opy_[bstack111l11lll1_opy_ + bstack11l1l_opy_ (u"ࠩ࠰ࠫခ") + attrs.get(bstack11l1l_opy_ (u"ࠪࡸࡾࡶࡥࠨဂ"), bstack11l1l_opy_ (u"ࠫࠬဃ")).lower()] = { bstack11l1l_opy_ (u"ࠬࡺࡥࡴࡶࡢࡨࡦࡺࡡࠨင"): bstack1111l1l11l_opy_ }
            bstack1ll1llll11_opy_.bstack111ll11ll1_opy_(bstack11l1l_opy_ (u"࠭ࡈࡰࡱ࡮ࡖࡺࡴࡓࡵࡣࡵࡸࡪࡪࠧစ"), bstack1111l1l11l_opy_)
        else:
            bstack111l1l1l11_opy_ = {
                bstack11l1l_opy_ (u"ࠧࡪࡦࠪဆ"): uuid4().__str__(),
                bstack11l1l_opy_ (u"ࠨࡶࡨࡼࡹ࠭ဇ"): bstack11l1l_opy_ (u"ࠩࡾࢁࠥࢁࡽࠨဈ").format(attrs.get(bstack11l1l_opy_ (u"ࠪ࡯ࡼࡴࡡ࡮ࡧࠪဉ")), attrs.get(bstack11l1l_opy_ (u"ࠫࡦࡸࡧࡴࠩည"), bstack11l1l_opy_ (u"ࠬ࠭ဋ"))) if attrs.get(bstack11l1l_opy_ (u"࠭ࡡࡳࡩࡶࠫဌ"), []) else attrs.get(bstack11l1l_opy_ (u"ࠧ࡬ࡹࡱࡥࡲ࡫ࠧဍ")),
                bstack11l1l_opy_ (u"ࠨࡵࡷࡩࡵࡥࡡࡳࡩࡸࡱࡪࡴࡴࠨဎ"): attrs.get(bstack11l1l_opy_ (u"ࠩࡤࡶ࡬ࡹࠧဏ"), []),
                bstack11l1l_opy_ (u"ࠪࡷࡹࡧࡲࡵࡧࡧࡣࡦࡺࠧတ"): bstack1lllll111_opy_(),
                bstack11l1l_opy_ (u"ࠫࡷ࡫ࡳࡶ࡮ࡷࠫထ"): bstack11l1l_opy_ (u"ࠬࡶࡥ࡯ࡦ࡬ࡲ࡬࠭ဒ"),
                bstack11l1l_opy_ (u"࠭ࡤࡦࡵࡦࡶ࡮ࡶࡴࡪࡱࡱࠫဓ"): attrs.get(bstack11l1l_opy_ (u"ࠧࡥࡱࡦࠫန"), bstack11l1l_opy_ (u"ࠨࠩပ"))
            }
            if attrs.get(bstack11l1l_opy_ (u"ࠩ࡯࡭ࡧࡴࡡ࡮ࡧࠪဖ"), bstack11l1l_opy_ (u"ࠪࠫဗ")) != bstack11l1l_opy_ (u"ࠫࠬဘ"):
                bstack111l1l1l11_opy_[bstack11l1l_opy_ (u"ࠬࡱࡥࡺࡹࡲࡶࡩ࠭မ")] = attrs.get(bstack11l1l_opy_ (u"࠭࡬ࡪࡤࡱࡥࡲ࡫ࠧယ"))
            if not self.bstack111l1111l1_opy_:
                self._1111lll1ll_opy_[self._1111l1111l_opy_()][bstack11l1l_opy_ (u"ࠧࡵࡧࡶࡸࡤࡪࡡࡵࡣࠪရ")].add_step(bstack111l1l1l11_opy_)
                threading.current_thread().current_step_uuid = bstack111l1l1l11_opy_[bstack11l1l_opy_ (u"ࠨ࡫ࡧࠫလ")]
            self.bstack111l1111l1_opy_.append(bstack111l1l1l11_opy_)
    @error_handler(class_method=True)
    def end_keyword(self, name, attrs):
        messages = self.messages.bstack111l111l1l_opy_()
        self._1111l11lll_opy_(messages)
        current_test_id = bstack11lll11l_opy_(threading.current_thread(), bstack11l1l_opy_ (u"ࠩࡦࡹࡷࡸࡥ࡯ࡶࡢࡸࡪࡹࡴࡠ࡫ࡧࠫဝ"), None)
        bstack111l11lll1_opy_ = current_test_id if current_test_id else bstack11lll11l_opy_(threading.current_thread(), bstack11l1l_opy_ (u"ࠪࡧࡺࡸࡲࡦࡰࡷࡣࡸࡻࡩࡵࡧࡢ࡭ࡩ࠭သ"), None)
        bstack1111llllll_opy_ = bstack111l111l11_opy_.get(attrs.get(bstack11l1l_opy_ (u"ࠫࡸࡺࡡࡵࡷࡶࠫဟ")), bstack11l1l_opy_ (u"ࠬࡹ࡫ࡪࡲࡳࡩࡩ࠭ဠ"))
        bstack1111lll1l1_opy_ = attrs.get(bstack11l1l_opy_ (u"࠭࡭ࡦࡵࡶࡥ࡬࡫ࠧအ"))
        if bstack1111llllll_opy_ != bstack11l1l_opy_ (u"ࠧࡴ࡭࡬ࡴࡵ࡫ࡤࠨဢ") and not attrs.get(bstack11l1l_opy_ (u"ࠨ࡯ࡨࡷࡸࡧࡧࡦࠩဣ")) and self._111l111lll_opy_:
            bstack1111lll1l1_opy_ = self._111l111lll_opy_
        bstack111l1ll1ll_opy_ = Result(result=bstack1111llllll_opy_, exception=bstack1111lll1l1_opy_, bstack111l1l11l1_opy_=[bstack1111lll1l1_opy_])
        if attrs.get(bstack11l1l_opy_ (u"ࠩࡷࡽࡵ࡫ࠧဤ"), bstack11l1l_opy_ (u"ࠪࠫဥ")).lower() in [bstack11l1l_opy_ (u"ࠫࡸ࡫ࡴࡶࡲࠪဦ"), bstack11l1l_opy_ (u"ࠬࡺࡥࡢࡴࡧࡳࡼࡴࠧဧ")]:
            bstack111l11lll1_opy_ = current_test_id if current_test_id else bstack11lll11l_opy_(threading.current_thread(), bstack11l1l_opy_ (u"࠭ࡣࡶࡴࡵࡩࡳࡺ࡟ࡴࡷ࡬ࡸࡪࡥࡩࡥࠩဨ"), None)
            if bstack111l11lll1_opy_:
                bstack111l11llll_opy_ = bstack111l11lll1_opy_ + bstack11l1l_opy_ (u"ࠢ࠮ࠤဩ") + attrs.get(bstack11l1l_opy_ (u"ࠨࡶࡼࡴࡪ࠭ဪ"), bstack11l1l_opy_ (u"ࠩࠪါ")).lower()
                self._1111lll1ll_opy_[bstack111l11llll_opy_][bstack11l1l_opy_ (u"ࠪࡸࡪࡹࡴࡠࡦࡤࡸࡦ࠭ာ")].stop(time=bstack1lllll111_opy_(), duration=int(attrs.get(bstack11l1l_opy_ (u"ࠫࡪࡲࡡࡱࡵࡨࡨࡹ࡯࡭ࡦࠩိ"), bstack11l1l_opy_ (u"ࠬ࠶ࠧီ"))), result=bstack111l1ll1ll_opy_)
                bstack1ll1llll11_opy_.bstack111ll11ll1_opy_(bstack11l1l_opy_ (u"࠭ࡈࡰࡱ࡮ࡖࡺࡴࡆࡪࡰ࡬ࡷ࡭࡫ࡤࠨု"), self._1111lll1ll_opy_[bstack111l11llll_opy_][bstack11l1l_opy_ (u"ࠧࡵࡧࡶࡸࡤࡪࡡࡵࡣࠪူ")])
        else:
            bstack111l11lll1_opy_ = current_test_id if current_test_id else bstack11lll11l_opy_(threading.current_thread(), bstack11l1l_opy_ (u"ࠨࡥࡸࡶࡷ࡫࡮ࡵࡡ࡫ࡳࡴࡱ࡟ࡪࡦࠪေ"), None)
            if bstack111l11lll1_opy_ and len(self.bstack111l1111l1_opy_) == 1:
                current_step_uuid = bstack11lll11l_opy_(threading.current_thread(), bstack11l1l_opy_ (u"ࠩࡦࡹࡷࡸࡥ࡯ࡶࡢࡷࡹ࡫ࡰࡠࡷࡸ࡭ࡩ࠭ဲ"), None)
                self._1111lll1ll_opy_[bstack111l11lll1_opy_][bstack11l1l_opy_ (u"ࠪࡸࡪࡹࡴࡠࡦࡤࡸࡦ࠭ဳ")].bstack111ll111l1_opy_(current_step_uuid, duration=int(attrs.get(bstack11l1l_opy_ (u"ࠫࡪࡲࡡࡱࡵࡨࡨࡹ࡯࡭ࡦࠩဴ"), bstack11l1l_opy_ (u"ࠬ࠶ࠧဵ"))), result=bstack111l1ll1ll_opy_)
            else:
                self.bstack1111l1l1ll_opy_(attrs)
            self.bstack111l1111l1_opy_.pop()
    def log_message(self, message):
        try:
            if message.get(bstack11l1l_opy_ (u"࠭ࡨࡵ࡯࡯ࠫံ"), bstack11l1l_opy_ (u"ࠧ࡯ࡱ့ࠪ")) == bstack11l1l_opy_ (u"ࠨࡻࡨࡷࠬး"):
                return
            self.messages.push(message)
            logs = []
            if bstack11llll111_opy_.bstack111ll111ll_opy_():
                logs.append({
                    bstack11l1l_opy_ (u"ࠩࡷ࡭ࡲ࡫ࡳࡵࡣࡰࡴ္ࠬ"): bstack1lllll111_opy_(),
                    bstack11l1l_opy_ (u"ࠪࡱࡪࡹࡳࡢࡩࡨ်ࠫ"): message.get(bstack11l1l_opy_ (u"ࠫࡲ࡫ࡳࡴࡣࡪࡩࠬျ")),
                    bstack11l1l_opy_ (u"ࠬࡲࡥࡷࡧ࡯ࠫြ"): message.get(bstack11l1l_opy_ (u"࠭࡬ࡦࡸࡨࡰࠬွ")),
                    **bstack11llll111_opy_.bstack111ll111ll_opy_()
                })
                if len(logs) > 0:
                    bstack1ll1llll11_opy_.bstack11lllll1l_opy_(logs)
        except Exception as err:
            pass
    def close(self):
        bstack1ll1llll11_opy_.bstack1111ll1111_opy_()
    def bstack1111l1l1ll_opy_(self, bstack111l111ll1_opy_):
        if not bstack11llll111_opy_.bstack111ll111ll_opy_():
            return
        kwname = bstack11l1l_opy_ (u"ࠧࡼࡿࠣࡿࢂ࠭ှ").format(bstack111l111ll1_opy_.get(bstack11l1l_opy_ (u"ࠨ࡭ࡺࡲࡦࡳࡥࠨဿ")), bstack111l111ll1_opy_.get(bstack11l1l_opy_ (u"ࠩࡤࡶ࡬ࡹࠧ၀"), bstack11l1l_opy_ (u"ࠪࠫ၁"))) if bstack111l111ll1_opy_.get(bstack11l1l_opy_ (u"ࠫࡦࡸࡧࡴࠩ၂"), []) else bstack111l111ll1_opy_.get(bstack11l1l_opy_ (u"ࠬࡱࡷ࡯ࡣࡰࡩࠬ၃"))
        error_message = bstack11l1l_opy_ (u"ࠨ࡫ࡸࡰࡤࡱࡪࡀࠠ࡝ࠤࡾ࠴ࢂࡢࠢࠡࡾࠣࡷࡹࡧࡴࡶࡵ࠽ࠤࡡࠨࡻ࠲ࡿ࡟ࠦࠥࢂࠠࡦࡺࡦࡩࡵࡺࡩࡰࡰ࠽ࠤࡡࠨࡻ࠳ࡿ࡟ࠦࠧ၄").format(kwname, bstack111l111ll1_opy_.get(bstack11l1l_opy_ (u"ࠧࡴࡶࡤࡸࡺࡹࠧ၅")), str(bstack111l111ll1_opy_.get(bstack11l1l_opy_ (u"ࠨ࡯ࡨࡷࡸࡧࡧࡦࠩ၆"))))
        bstack1111lllll1_opy_ = bstack11l1l_opy_ (u"ࠤ࡮ࡻࡳࡧ࡭ࡦ࠼ࠣࡠࠧࢁ࠰ࡾ࡞ࠥࠤࢁࠦࡳࡵࡣࡷࡹࡸࡀࠠ࡝ࠤࡾ࠵ࢂࡢࠢࠣ၇").format(kwname, bstack111l111ll1_opy_.get(bstack11l1l_opy_ (u"ࠪࡷࡹࡧࡴࡶࡵࠪ၈")))
        bstack111l11ll1l_opy_ = error_message if bstack111l111ll1_opy_.get(bstack11l1l_opy_ (u"ࠫࡲ࡫ࡳࡴࡣࡪࡩࠬ၉")) else bstack1111lllll1_opy_
        bstack1111lll111_opy_ = {
            bstack11l1l_opy_ (u"ࠬࡺࡩ࡮ࡧࡶࡸࡦࡳࡰࠨ၊"): self.bstack111l1111l1_opy_[-1].get(bstack11l1l_opy_ (u"࠭ࡳࡵࡣࡵࡸࡪࡪ࡟ࡢࡶࠪ။"), bstack1lllll111_opy_()),
            bstack11l1l_opy_ (u"ࠧ࡮ࡧࡶࡷࡦ࡭ࡥࠨ၌"): bstack111l11ll1l_opy_,
            bstack11l1l_opy_ (u"ࠨ࡮ࡨࡺࡪࡲࠧ၍"): bstack11l1l_opy_ (u"ࠩࡈࡖࡗࡕࡒࠨ၎") if bstack111l111ll1_opy_.get(bstack11l1l_opy_ (u"ࠪࡷࡹࡧࡴࡶࡵࠪ၏")) == bstack11l1l_opy_ (u"ࠫࡋࡇࡉࡍࠩၐ") else bstack11l1l_opy_ (u"ࠬࡏࡎࡇࡑࠪၑ"),
            **bstack11llll111_opy_.bstack111ll111ll_opy_()
        }
        bstack1ll1llll11_opy_.bstack11lllll1l_opy_([bstack1111lll111_opy_])
    def _1111l1111l_opy_(self):
        for bstack1111l1llll_opy_ in reversed(self._1111lll1ll_opy_):
            bstack1111l111ll_opy_ = bstack1111l1llll_opy_
            data = self._1111lll1ll_opy_[bstack1111l1llll_opy_][bstack11l1l_opy_ (u"࠭ࡴࡦࡵࡷࡣࡩࡧࡴࡢࠩၒ")]
            if isinstance(data, bstack111l1lll11_opy_):
                if not bstack11l1l_opy_ (u"ࠧࡆࡃࡆࡌࠬၓ") in data.bstack111l11ll11_opy_():
                    return bstack1111l111ll_opy_
            else:
                return bstack1111l111ll_opy_
    def _1111l11lll_opy_(self, messages):
        try:
            bstack111l1111ll_opy_ = BuiltIn().get_variable_value(bstack11l1l_opy_ (u"ࠣࠦࡾࡐࡔࡍࠠࡍࡇ࡙ࡉࡑࢃࠢၔ")) in (bstack1111ll1ll1_opy_.DEBUG, bstack1111ll1ll1_opy_.TRACE)
            for message, bstack1111l1ll1l_opy_ in zip_longest(messages, messages[1:]):
                name = message.get(bstack11l1l_opy_ (u"ࠩࡰࡩࡸࡹࡡࡨࡧࠪၕ"))
                level = message.get(bstack11l1l_opy_ (u"ࠪࡰࡪࡼࡥ࡭ࠩၖ"))
                if level == bstack1111ll1ll1_opy_.FAIL:
                    self._111l111lll_opy_ = name or self._111l111lll_opy_
                    self._1111ll1lll_opy_ = bstack1111l1ll1l_opy_.get(bstack11l1l_opy_ (u"ࠦࡲ࡫ࡳࡴࡣࡪࡩࠧၗ")) if bstack111l1111ll_opy_ and bstack1111l1ll1l_opy_ else self._1111ll1lll_opy_
        except:
            pass
    @classmethod
    def bstack111ll11ll1_opy_(self, event: str, bstack111l11l1l1_opy_: bstack1111l11ll1_opy_, bstack1111l11l1l_opy_=False):
        if event == bstack11l1l_opy_ (u"࡚ࠬࡥࡴࡶࡕࡹࡳࡌࡩ࡯࡫ࡶ࡬ࡪࡪࠧၘ"):
            bstack111l11l1l1_opy_.set(hooks=self.store[bstack11l1l_opy_ (u"࠭ࡴࡦࡵࡷࡣ࡭ࡵ࡯࡬ࡵࠪၙ")])
        if event == bstack11l1l_opy_ (u"ࠧࡕࡧࡶࡸࡗࡻ࡮ࡔ࡭࡬ࡴࡵ࡫ࡤࠨၚ"):
            event = bstack11l1l_opy_ (u"ࠨࡖࡨࡷࡹࡘࡵ࡯ࡈ࡬ࡲ࡮ࡹࡨࡦࡦࠪၛ")
        if bstack1111l11l1l_opy_:
            bstack1111ll111l_opy_ = {
                bstack11l1l_opy_ (u"ࠩࡨࡺࡪࡴࡴࡠࡶࡼࡴࡪ࠭ၜ"): event,
                bstack111l11l1l1_opy_.bstack1111l11l11_opy_(): bstack111l11l1l1_opy_.bstack1111l1l111_opy_(event)
            }
            with self._lock:
                self.bstack111l11111l_opy_.append(bstack1111ll111l_opy_)
        else:
            bstack1ll1llll11_opy_.bstack111ll11ll1_opy_(event, bstack111l11l1l1_opy_)
class bstack1111lll11l_opy_:
    def __init__(self):
        self._1111llll11_opy_ = []
    def bstack1111llll1l_opy_(self):
        self._1111llll11_opy_.append([])
    def bstack111l111l1l_opy_(self):
        return self._1111llll11_opy_.pop() if self._1111llll11_opy_ else list()
    def push(self, message):
        self._1111llll11_opy_[-1].append(message) if self._1111llll11_opy_ else self._1111llll11_opy_.append([message])
class bstack1111ll1ll1_opy_:
    FAIL = bstack11l1l_opy_ (u"ࠪࡊࡆࡏࡌࠨၝ")
    ERROR = bstack11l1l_opy_ (u"ࠫࡊࡘࡒࡐࡔࠪၞ")
    WARNING = bstack11l1l_opy_ (u"ࠬ࡝ࡁࡓࡐࠪၟ")
    bstack111l11l111_opy_ = bstack11l1l_opy_ (u"࠭ࡉࡏࡈࡒࠫၠ")
    DEBUG = bstack11l1l_opy_ (u"ࠧࡅࡇࡅ࡙ࡌ࠭ၡ")
    TRACE = bstack11l1l_opy_ (u"ࠨࡖࡕࡅࡈࡋࠧၢ")
    bstack1111l11111_opy_ = [FAIL, ERROR]
def bstack1111ll1l11_opy_(bstack1111ll11ll_opy_):
    if not bstack1111ll11ll_opy_:
        return None
    if bstack1111ll11ll_opy_.get(bstack11l1l_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡥࡣࡷࡥࠬၣ"), None):
        return getattr(bstack1111ll11ll_opy_[bstack11l1l_opy_ (u"ࠪࡸࡪࡹࡴࡠࡦࡤࡸࡦ࠭ၤ")], bstack11l1l_opy_ (u"ࠫࡺࡻࡩࡥࠩၥ"), None)
    return bstack1111ll11ll_opy_.get(bstack11l1l_opy_ (u"ࠬࡻࡵࡪࡦࠪၦ"), None)
def bstack111l11l1ll_opy_(hook_type, current_test_uuid):
    if hook_type.lower() not in [bstack11l1l_opy_ (u"࠭ࡳࡦࡶࡸࡴࠬၧ"), bstack11l1l_opy_ (u"ࠧࡵࡧࡤࡶࡩࡵࡷ࡯ࠩၨ")]:
        return
    if hook_type.lower() == bstack11l1l_opy_ (u"ࠨࡵࡨࡸࡺࡶࠧၩ"):
        if current_test_uuid is None:
            return bstack11l1l_opy_ (u"ࠩࡅࡉࡋࡕࡒࡆࡡࡄࡐࡑ࠭ၪ")
        else:
            return bstack11l1l_opy_ (u"ࠪࡆࡊࡌࡏࡓࡇࡢࡉࡆࡉࡈࠨၫ")
    elif hook_type.lower() == bstack11l1l_opy_ (u"ࠫࡹ࡫ࡡࡳࡦࡲࡻࡳ࠭ၬ"):
        if current_test_uuid is None:
            return bstack11l1l_opy_ (u"ࠬࡇࡆࡕࡇࡕࡣࡆࡒࡌࠨၭ")
        else:
            return bstack11l1l_opy_ (u"࠭ࡁࡇࡖࡈࡖࡤࡋࡁࡄࡊࠪၮ")