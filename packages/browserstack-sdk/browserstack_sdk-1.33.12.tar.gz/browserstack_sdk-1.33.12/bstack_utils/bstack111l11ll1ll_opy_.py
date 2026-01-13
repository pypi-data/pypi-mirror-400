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
from _pytest import fixtures
from _pytest.python import _call_with_optional_argument
from pytest import Module, Class
from bstack_utils.helper import Result, bstack111ll1111l1_opy_
from browserstack_sdk.bstack1l1l1ll1_opy_ import bstack1lll1l11ll_opy_
def _111l11l1lll_opy_(method, this, arg):
    arg_count = method.__code__.co_argcount
    if arg_count > 1:
        method(this, arg)
    else:
        method(this)
class bstack111l11lllll_opy_:
    def __init__(self, handler):
        self._111l1l1111l_opy_ = {}
        self._111l11l1ll1_opy_ = {}
        self.handler = handler
        self.patch()
        pass
    def patch(self):
        pytest_version = bstack1lll1l11ll_opy_.version()
        if bstack111ll1111l1_opy_(pytest_version, bstack11ll1_opy_ (u"ࠧ࠾࠮࠲࠰࠴ࠦḼ")) >= 0:
            self._111l1l1111l_opy_[bstack11ll1_opy_ (u"࠭ࡦࡶࡰࡦࡸ࡮ࡵ࡮ࡠࡨ࡬ࡼࡹࡻࡲࡦࠩḽ")] = Module._register_setup_function_fixture
            self._111l1l1111l_opy_[bstack11ll1_opy_ (u"ࠧ࡮ࡱࡧࡹࡱ࡫࡟ࡧ࡫ࡻࡸࡺࡸࡥࠨḾ")] = Module._register_setup_module_fixture
            self._111l1l1111l_opy_[bstack11ll1_opy_ (u"ࠨࡥ࡯ࡥࡸࡹ࡟ࡧ࡫ࡻࡸࡺࡸࡥࠨḿ")] = Class._register_setup_class_fixture
            self._111l1l1111l_opy_[bstack11ll1_opy_ (u"ࠩࡰࡩࡹ࡮࡯ࡥࡡࡩ࡭ࡽࡺࡵࡳࡧࠪṀ")] = Class._register_setup_method_fixture
            Module._register_setup_function_fixture = self.bstack111l11ll1l1_opy_(bstack11ll1_opy_ (u"ࠪࡪࡺࡴࡣࡵ࡫ࡲࡲࡤ࡬ࡩࡹࡶࡸࡶࡪ࠭ṁ"))
            Module._register_setup_module_fixture = self.bstack111l11ll1l1_opy_(bstack11ll1_opy_ (u"ࠫࡲࡵࡤࡶ࡮ࡨࡣ࡫࡯ࡸࡵࡷࡵࡩࠬṂ"))
            Class._register_setup_class_fixture = self.bstack111l11ll1l1_opy_(bstack11ll1_opy_ (u"ࠬࡩ࡬ࡢࡵࡶࡣ࡫࡯ࡸࡵࡷࡵࡩࠬṃ"))
            Class._register_setup_method_fixture = self.bstack111l11ll1l1_opy_(bstack11ll1_opy_ (u"࠭࡭ࡦࡶ࡫ࡳࡩࡥࡦࡪࡺࡷࡹࡷ࡫ࠧṄ"))
        else:
            self._111l1l1111l_opy_[bstack11ll1_opy_ (u"ࠧࡧࡷࡱࡧࡹ࡯࡯࡯ࡡࡩ࡭ࡽࡺࡵࡳࡧࠪṅ")] = Module._inject_setup_function_fixture
            self._111l1l1111l_opy_[bstack11ll1_opy_ (u"ࠨ࡯ࡲࡨࡺࡲࡥࡠࡨ࡬ࡼࡹࡻࡲࡦࠩṆ")] = Module._inject_setup_module_fixture
            self._111l1l1111l_opy_[bstack11ll1_opy_ (u"ࠩࡦࡰࡦࡹࡳࡠࡨ࡬ࡼࡹࡻࡲࡦࠩṇ")] = Class._inject_setup_class_fixture
            self._111l1l1111l_opy_[bstack11ll1_opy_ (u"ࠪࡱࡪࡺࡨࡰࡦࡢࡪ࡮ࡾࡴࡶࡴࡨࠫṈ")] = Class._inject_setup_method_fixture
            Module._inject_setup_function_fixture = self.bstack111l11ll1l1_opy_(bstack11ll1_opy_ (u"ࠫ࡫ࡻ࡮ࡤࡶ࡬ࡳࡳࡥࡦࡪࡺࡷࡹࡷ࡫ࠧṉ"))
            Module._inject_setup_module_fixture = self.bstack111l11ll1l1_opy_(bstack11ll1_opy_ (u"ࠬࡳ࡯ࡥࡷ࡯ࡩࡤ࡬ࡩࡹࡶࡸࡶࡪ࠭Ṋ"))
            Class._inject_setup_class_fixture = self.bstack111l11ll1l1_opy_(bstack11ll1_opy_ (u"࠭ࡣ࡭ࡣࡶࡷࡤ࡬ࡩࡹࡶࡸࡶࡪ࠭ṋ"))
            Class._inject_setup_method_fixture = self.bstack111l11ll1l1_opy_(bstack11ll1_opy_ (u"ࠧ࡮ࡧࡷ࡬ࡴࡪ࡟ࡧ࡫ࡻࡸࡺࡸࡥࠨṌ"))
    def bstack111l11llll1_opy_(self, bstack111l11l1l1l_opy_, hook_type):
        bstack111l1l11111_opy_ = id(bstack111l11l1l1l_opy_.__class__)
        if (bstack111l1l11111_opy_, hook_type) in self._111l11l1ll1_opy_:
            return
        meth = getattr(bstack111l11l1l1l_opy_, hook_type, None)
        if meth is not None and fixtures.getfixturemarker(meth) is None:
            self._111l11l1ll1_opy_[(bstack111l1l11111_opy_, hook_type)] = meth
            setattr(bstack111l11l1l1l_opy_, hook_type, self.bstack111l11l1l11_opy_(hook_type, bstack111l1l11111_opy_))
    def bstack111l11lll11_opy_(self, instance, bstack111l11ll11l_opy_):
        if bstack111l11ll11l_opy_ == bstack11ll1_opy_ (u"ࠣࡨࡸࡲࡨࡺࡩࡰࡰࡢࡪ࡮ࡾࡴࡶࡴࡨࠦṍ"):
            self.bstack111l11llll1_opy_(instance.obj, bstack11ll1_opy_ (u"ࠤࡶࡩࡹࡻࡰࡠࡨࡸࡲࡨࡺࡩࡰࡰࠥṎ"))
            self.bstack111l11llll1_opy_(instance.obj, bstack11ll1_opy_ (u"ࠥࡸࡪࡧࡲࡥࡱࡺࡲࡤ࡬ࡵ࡯ࡥࡷ࡭ࡴࡴࠢṏ"))
        if bstack111l11ll11l_opy_ == bstack11ll1_opy_ (u"ࠦࡲࡵࡤࡶ࡮ࡨࡣ࡫࡯ࡸࡵࡷࡵࡩࠧṐ"):
            self.bstack111l11llll1_opy_(instance.obj, bstack11ll1_opy_ (u"ࠧࡹࡥࡵࡷࡳࡣࡲࡵࡤࡶ࡮ࡨࠦṑ"))
            self.bstack111l11llll1_opy_(instance.obj, bstack11ll1_opy_ (u"ࠨࡴࡦࡣࡵࡨࡴࡽ࡮ࡠ࡯ࡲࡨࡺࡲࡥࠣṒ"))
        if bstack111l11ll11l_opy_ == bstack11ll1_opy_ (u"ࠢࡤ࡮ࡤࡷࡸࡥࡦࡪࡺࡷࡹࡷ࡫ࠢṓ"):
            self.bstack111l11llll1_opy_(instance.obj, bstack11ll1_opy_ (u"ࠣࡵࡨࡸࡺࡶ࡟ࡤ࡮ࡤࡷࡸࠨṔ"))
            self.bstack111l11llll1_opy_(instance.obj, bstack11ll1_opy_ (u"ࠤࡷࡩࡦࡸࡤࡰࡹࡱࡣࡨࡲࡡࡴࡵࠥṕ"))
        if bstack111l11ll11l_opy_ == bstack11ll1_opy_ (u"ࠥࡱࡪࡺࡨࡰࡦࡢࡪ࡮ࡾࡴࡶࡴࡨࠦṖ"):
            self.bstack111l11llll1_opy_(instance.obj, bstack11ll1_opy_ (u"ࠦࡸ࡫ࡴࡶࡲࡢࡱࡪࡺࡨࡰࡦࠥṗ"))
            self.bstack111l11llll1_opy_(instance.obj, bstack11ll1_opy_ (u"ࠧࡺࡥࡢࡴࡧࡳࡼࡴ࡟࡮ࡧࡷ࡬ࡴࡪࠢṘ"))
    @staticmethod
    def bstack111l11l11ll_opy_(hook_type, func, args):
        if hook_type in [bstack11ll1_opy_ (u"࠭ࡳࡦࡶࡸࡴࡤࡳࡥࡵࡪࡲࡨࠬṙ"), bstack11ll1_opy_ (u"ࠧࡵࡧࡤࡶࡩࡵࡷ࡯ࡡࡰࡩࡹ࡮࡯ࡥࠩṚ")]:
            _111l11l1lll_opy_(func, args[0], args[1])
            return
        _call_with_optional_argument(func, args[0])
    def bstack111l11l1l11_opy_(self, hook_type, bstack111l1l11111_opy_):
        def bstack111l11lll1l_opy_(arg=None):
            self.handler(hook_type, bstack11ll1_opy_ (u"ࠨࡤࡨࡪࡴࡸࡥࠨṛ"))
            result = None
            try:
                bstack1l1lll11lll_opy_ = self._111l11l1ll1_opy_[(bstack111l1l11111_opy_, hook_type)]
                self.bstack111l11l11ll_opy_(hook_type, bstack1l1lll11lll_opy_, (arg,))
                result = Result(result=bstack11ll1_opy_ (u"ࠩࡳࡥࡸࡹࡥࡥࠩṜ"))
            except Exception as e:
                result = Result(result=bstack11ll1_opy_ (u"ࠪࡪࡦ࡯࡬ࡦࡦࠪṝ"), exception=e)
                self.handler(hook_type, bstack11ll1_opy_ (u"ࠫࡦ࡬ࡴࡦࡴࠪṞ"), result)
                raise e.with_traceback(e.__traceback__)
            self.handler(hook_type, bstack11ll1_opy_ (u"ࠬࡧࡦࡵࡧࡵࠫṟ"), result)
        def bstack111l11ll111_opy_(this, arg=None):
            self.handler(hook_type, bstack11ll1_opy_ (u"࠭ࡢࡦࡨࡲࡶࡪ࠭Ṡ"))
            result = None
            exception = None
            try:
                self.bstack111l11l11ll_opy_(hook_type, self._111l11l1ll1_opy_[hook_type], (this, arg))
                result = Result(result=bstack11ll1_opy_ (u"ࠧࡱࡣࡶࡷࡪࡪࠧṡ"))
            except Exception as e:
                result = Result(result=bstack11ll1_opy_ (u"ࠨࡨࡤ࡭ࡱ࡫ࡤࠨṢ"), exception=e)
                self.handler(hook_type, bstack11ll1_opy_ (u"ࠩࡤࡪࡹ࡫ࡲࠨṣ"), result)
                raise e.with_traceback(e.__traceback__)
            self.handler(hook_type, bstack11ll1_opy_ (u"ࠪࡥ࡫ࡺࡥࡳࠩṤ"), result)
        if hook_type in [bstack11ll1_opy_ (u"ࠫࡸ࡫ࡴࡶࡲࡢࡱࡪࡺࡨࡰࡦࠪṥ"), bstack11ll1_opy_ (u"ࠬࡺࡥࡢࡴࡧࡳࡼࡴ࡟࡮ࡧࡷ࡬ࡴࡪࠧṦ")]:
            return bstack111l11ll111_opy_
        return bstack111l11lll1l_opy_
    def bstack111l11ll1l1_opy_(self, bstack111l11ll11l_opy_):
        def bstack111l1l111l1_opy_(this, *args, **kwargs):
            self.bstack111l11lll11_opy_(this, bstack111l11ll11l_opy_)
            self._111l1l1111l_opy_[bstack111l11ll11l_opy_](this, *args, **kwargs)
        return bstack111l1l111l1_opy_