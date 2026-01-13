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
import threading
import os
import logging
from uuid import uuid4
from bstack_utils.bstack111l1ll11l_opy_ import bstack111l1ll1l1_opy_, bstack111ll111ll_opy_
from bstack_utils.bstack111ll11lll_opy_ import bstack1l11llll1l_opy_
from bstack_utils.helper import bstack1lll11l1l_opy_, bstack111lll1lll_opy_, Result
from bstack_utils.bstack111l1l1l1l_opy_ import bstack11lll11l11_opy_
from bstack_utils.capture import bstack111l1l1lll_opy_
from bstack_utils.constants import *
logger = logging.getLogger(__name__)
class bstack111ll1111_opy_:
    def __init__(self):
        self.bstack111ll11ll1_opy_ = bstack111l1l1lll_opy_(self.bstack111l1l1111_opy_)
        self.tests = {}
    @staticmethod
    def bstack111l1l1111_opy_(log):
        if not (log[bstack11ll1_opy_ (u"ࠫࡲ࡫ࡳࡴࡣࡪࡩࠬཔ")] and log[bstack11ll1_opy_ (u"ࠬࡳࡥࡴࡵࡤ࡫ࡪ࠭ཕ")].strip()):
            return
        active = bstack1l11llll1l_opy_.bstack111ll111l1_opy_()
        log = {
            bstack11ll1_opy_ (u"࠭࡬ࡦࡸࡨࡰࠬབ"): log[bstack11ll1_opy_ (u"ࠧ࡭ࡧࡹࡩࡱ࠭བྷ")],
            bstack11ll1_opy_ (u"ࠨࡶ࡬ࡱࡪࡹࡴࡢ࡯ࡳࠫམ"): bstack111lll1lll_opy_(),
            bstack11ll1_opy_ (u"ࠩࡰࡩࡸࡹࡡࡨࡧࠪཙ"): log[bstack11ll1_opy_ (u"ࠪࡱࡪࡹࡳࡢࡩࡨࠫཚ")],
        }
        if active:
            if active[bstack11ll1_opy_ (u"ࠫࡹࡿࡰࡦࠩཛ")] == bstack11ll1_opy_ (u"ࠬ࡮࡯ࡰ࡭ࠪཛྷ"):
                log[bstack11ll1_opy_ (u"࠭ࡨࡰࡱ࡮ࡣࡷࡻ࡮ࡠࡷࡸ࡭ࡩ࠭ཝ")] = active[bstack11ll1_opy_ (u"ࠧࡩࡱࡲ࡯ࡤࡸࡵ࡯ࡡࡸࡹ࡮ࡪࠧཞ")]
            elif active[bstack11ll1_opy_ (u"ࠨࡶࡼࡴࡪ࠭ཟ")] == bstack11ll1_opy_ (u"ࠩࡷࡩࡸࡺࠧའ"):
                log[bstack11ll1_opy_ (u"ࠪࡸࡪࡹࡴࡠࡴࡸࡲࡤࡻࡵࡪࡦࠪཡ")] = active[bstack11ll1_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡵࡹࡳࡥࡵࡶ࡫ࡧࠫར")]
        bstack11lll11l11_opy_.bstack1l1l11l11l_opy_([log])
    def start_test(self, attrs):
        test_uuid = uuid4().__str__()
        self.tests[test_uuid] = {}
        self.bstack111ll11ll1_opy_.start()
        driver = bstack1lll11l1l_opy_(threading.current_thread(), bstack11ll1_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯ࡘ࡫ࡳࡴ࡫ࡲࡲࡉࡸࡩࡷࡧࡵࠫལ"), None)
        bstack111l1ll11l_opy_ = bstack111ll111ll_opy_(
            name=attrs.scenario.name,
            uuid=test_uuid,
            started_at=bstack111lll1lll_opy_(),
            file_path=attrs.feature.filename,
            result=bstack11ll1_opy_ (u"ࠨࡰࡦࡰࡧ࡭ࡳ࡭ࠢཤ"),
            framework=bstack11ll1_opy_ (u"ࠧࡃࡧ࡫ࡥࡻ࡫ࠧཥ"),
            scope=[attrs.feature.name],
            bstack111l1l11ll_opy_=bstack11lll11l11_opy_.bstack111l1ll111_opy_(driver) if driver and driver.session_id else {},
            meta={},
            tags=attrs.scenario.tags
        )
        self.tests[test_uuid][bstack11ll1_opy_ (u"ࠨࡶࡨࡷࡹࡥࡤࡢࡶࡤࠫས")] = bstack111l1ll11l_opy_
        threading.current_thread().current_test_uuid = test_uuid
        bstack11lll11l11_opy_.bstack111ll11l11_opy_(bstack11ll1_opy_ (u"ࠩࡗࡩࡸࡺࡒࡶࡰࡖࡸࡦࡸࡴࡦࡦࠪཧ"), bstack111l1ll11l_opy_)
    def end_test(self, attrs):
        bstack111l1l1l11_opy_ = {
            bstack11ll1_opy_ (u"ࠥࡲࡦࡳࡥࠣཨ"): attrs.feature.name,
            bstack11ll1_opy_ (u"ࠦࡩ࡫ࡳࡤࡴ࡬ࡴࡹ࡯࡯࡯ࠤཀྵ"): attrs.feature.description
        }
        current_test_uuid = threading.current_thread().current_test_uuid
        bstack111l1ll11l_opy_ = self.tests[current_test_uuid][bstack11ll1_opy_ (u"ࠬࡺࡥࡴࡶࡢࡨࡦࡺࡡࠨཪ")]
        meta = {
            bstack11ll1_opy_ (u"ࠨࡦࡦࡣࡷࡹࡷ࡫ࠢཫ"): bstack111l1l1l11_opy_,
            bstack11ll1_opy_ (u"ࠢࡴࡶࡨࡴࡸࠨཬ"): bstack111l1ll11l_opy_.meta.get(bstack11ll1_opy_ (u"ࠨࡵࡷࡩࡵࡹࠧ཭"), []),
            bstack11ll1_opy_ (u"ࠤࡶࡧࡪࡴࡡࡳ࡫ࡲࠦ཮"): {
                bstack11ll1_opy_ (u"ࠥࡲࡦࡳࡥࠣ཯"): attrs.feature.scenarios[0].name if len(attrs.feature.scenarios) else None
            }
        }
        bstack111l1ll11l_opy_.bstack111l1lllll_opy_(meta)
        bstack111l1ll11l_opy_.bstack111ll11111_opy_(bstack1lll11l1l_opy_(threading.current_thread(), bstack11ll1_opy_ (u"ࠫࡨࡻࡲࡳࡧࡱࡸࡤࡺࡥࡴࡶࡢ࡬ࡴࡵ࡫ࡴࠩ཰"), []))
        bstack111l1llll1_opy_, exception = self._111l1l11l1_opy_(attrs)
        bstack111l1lll1l_opy_ = Result(result=attrs.status.name, exception=exception, bstack111l1l1ll1_opy_=[bstack111l1llll1_opy_])
        self.tests[threading.current_thread().current_test_uuid][bstack11ll1_opy_ (u"ࠬࡺࡥࡴࡶࡢࡨࡦࡺࡡࠨཱ")].stop(time=bstack111lll1lll_opy_(), duration=int(attrs.duration)*1000, result=bstack111l1lll1l_opy_)
        bstack11lll11l11_opy_.bstack111ll11l11_opy_(bstack11ll1_opy_ (u"࠭ࡔࡦࡵࡷࡖࡺࡴࡆࡪࡰ࡬ࡷ࡭࡫ࡤࠨི"), self.tests[threading.current_thread().current_test_uuid][bstack11ll1_opy_ (u"ࠧࡵࡧࡶࡸࡤࡪࡡࡵࡣཱིࠪ")])
    def bstack1lll11ll1l_opy_(self, attrs):
        bstack111ll1111l_opy_ = {
            bstack11ll1_opy_ (u"ࠨ࡫ࡧུࠫ"): uuid4().__str__(),
            bstack11ll1_opy_ (u"ࠩ࡮ࡩࡾࡽ࡯ࡳࡦཱུࠪ"): attrs.keyword,
            bstack11ll1_opy_ (u"ࠪࡷࡹ࡫ࡰࡠࡣࡵ࡫ࡺࡳࡥ࡯ࡶࠪྲྀ"): [],
            bstack11ll1_opy_ (u"ࠫࡹ࡫ࡸࡵࠩཷ"): attrs.name,
            bstack11ll1_opy_ (u"ࠬࡹࡴࡢࡴࡷࡩࡩࡥࡡࡵࠩླྀ"): bstack111lll1lll_opy_(),
            bstack11ll1_opy_ (u"࠭ࡲࡦࡵࡸࡰࡹ࠭ཹ"): bstack11ll1_opy_ (u"ࠧࡱࡧࡱࡨ࡮ࡴࡧࠨེ"),
            bstack11ll1_opy_ (u"ࠨࡦࡨࡷࡨࡸࡩࡱࡶ࡬ࡳࡳཻ࠭"): bstack11ll1_opy_ (u"ོࠩࠪ")
        }
        self.tests[threading.current_thread().current_test_uuid][bstack11ll1_opy_ (u"ࠪࡸࡪࡹࡴࡠࡦࡤࡸࡦཽ࠭")].add_step(bstack111ll1111l_opy_)
        threading.current_thread().current_step_uuid = bstack111ll1111l_opy_[bstack11ll1_opy_ (u"ࠫ࡮ࡪࠧཾ")]
    def bstack11ll11lll_opy_(self, attrs):
        current_test_id = bstack1lll11l1l_opy_(threading.current_thread(), bstack11ll1_opy_ (u"ࠬࡩࡵࡳࡴࡨࡲࡹࡥࡴࡦࡵࡷࡣࡺࡻࡩࡥࠩཿ"), None)
        current_step_uuid = bstack1lll11l1l_opy_(threading.current_thread(), bstack11ll1_opy_ (u"࠭ࡣࡶࡴࡵࡩࡳࡺ࡟ࡴࡶࡨࡴࡤࡻࡵࡪࡦྀࠪ"), None)
        bstack111l1llll1_opy_, exception = self._111l1l11l1_opy_(attrs)
        bstack111l1lll1l_opy_ = Result(result=attrs.status.name, exception=exception, bstack111l1l1ll1_opy_=[bstack111l1llll1_opy_])
        self.tests[current_test_id][bstack11ll1_opy_ (u"ࠧࡵࡧࡶࡸࡤࡪࡡࡵࡣཱྀࠪ")].bstack111l1ll1ll_opy_(current_step_uuid, duration=int(attrs.duration)*1000, result=bstack111l1lll1l_opy_)
        threading.current_thread().current_step_uuid = None
    def bstack11l1ll1l11_opy_(self, name, attrs):
        try:
            bstack111l11llll_opy_ = uuid4().__str__()
            self.tests[bstack111l11llll_opy_] = {}
            self.bstack111ll11ll1_opy_.start()
            scopes = []
            driver = bstack1lll11l1l_opy_(threading.current_thread(), bstack11ll1_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫ࡔࡧࡶࡷ࡮ࡵ࡮ࡅࡴ࡬ࡺࡪࡸࠧྂ"), None)
            current_thread = threading.current_thread()
            if not hasattr(current_thread, bstack11ll1_opy_ (u"ࠩࡦࡹࡷࡸࡥ࡯ࡶࡢࡸࡪࡹࡴࡠࡪࡲࡳࡰࡹࠧྃ")):
                current_thread.current_test_hooks = []
            current_thread.current_test_hooks.append(bstack111l11llll_opy_)
            if name in [bstack11ll1_opy_ (u"ࠥࡦࡪ࡬࡯ࡳࡧࡢࡥࡱࡲ྄ࠢ"), bstack11ll1_opy_ (u"ࠦࡦ࡬ࡴࡦࡴࡢࡥࡱࡲࠢ྅")]:
                file_path = os.path.join(attrs.config.base_dir, attrs.config.environment_file)
                scopes = [attrs.config.environment_file]
            elif name in [bstack11ll1_opy_ (u"ࠧࡨࡥࡧࡱࡵࡩࡤ࡬ࡥࡢࡶࡸࡶࡪࠨ྆"), bstack11ll1_opy_ (u"ࠨࡡࡧࡶࡨࡶࡤ࡬ࡥࡢࡶࡸࡶࡪࠨ྇")]:
                file_path = attrs.filename
                scopes = [attrs.name]
            else:
                file_path = attrs.filename
                if hasattr(attrs, bstack11ll1_opy_ (u"ࠧࡧࡧࡤࡸࡺࡸࡥࠨྈ")):
                    scopes =  [attrs.feature.name]
            hook_data = bstack111l1ll1l1_opy_(
                name=name,
                uuid=bstack111l11llll_opy_,
                started_at=bstack111lll1lll_opy_(),
                file_path=file_path,
                framework=bstack11ll1_opy_ (u"ࠣࡄࡨ࡬ࡦࡼࡥࠣྉ"),
                bstack111l1l11ll_opy_=bstack11lll11l11_opy_.bstack111l1ll111_opy_(driver) if driver and driver.session_id else {},
                scope=scopes,
                result=bstack11ll1_opy_ (u"ࠤࡳࡩࡳࡪࡩ࡯ࡩࠥྊ"),
                hook_type=name
            )
            self.tests[bstack111l11llll_opy_][bstack11ll1_opy_ (u"ࠥࡸࡪࡹࡴࡠࡦࡤࡸࡦࠨྋ")] = hook_data
            current_test_id = bstack1lll11l1l_opy_(threading.current_thread(), bstack11ll1_opy_ (u"ࠦࡨࡻࡲࡳࡧࡱࡸࡤࡺࡥࡴࡶࡢࡹࡺ࡯ࡤࠣྌ"), None)
            if current_test_id:
                hook_data.bstack111ll11l1l_opy_(current_test_id)
            if name == bstack11ll1_opy_ (u"ࠧࡨࡥࡧࡱࡵࡩࡤࡧ࡬࡭ࠤྍ"):
                threading.current_thread().before_all_hook_uuid = bstack111l11llll_opy_
            threading.current_thread().current_hook_uuid = bstack111l11llll_opy_
            bstack11lll11l11_opy_.bstack111ll11l11_opy_(bstack11ll1_opy_ (u"ࠨࡈࡰࡱ࡮ࡖࡺࡴࡓࡵࡣࡵࡸࡪࡪࠢྎ"), hook_data)
        except Exception as e:
            logger.debug(bstack11ll1_opy_ (u"ࠢࡆࡴࡵࡳࡷࠦ࡯ࡤࡥࡸࡶࡷ࡫ࡤࠡ࡫ࡱࠤࡸࡺࡡࡳࡶࠣ࡬ࡴࡵ࡫ࠡࡧࡹࡩࡳࡺࡳ࠭ࠢ࡫ࡳࡴࡱࠠ࡯ࡣࡰࡩ࠿ࠦࠥࡴ࠮ࠣࡩࡷࡸ࡯ࡳ࠼ࠣࠩࡸࠨྏ"), name, e)
    def bstack1l1llll1ll_opy_(self, attrs):
        bstack111l1lll11_opy_ = bstack1lll11l1l_opy_(threading.current_thread(), bstack11ll1_opy_ (u"ࠨࡥࡸࡶࡷ࡫࡮ࡵࡡ࡫ࡳࡴࡱ࡟ࡶࡷ࡬ࡨࠬྐ"), None)
        hook_data = self.tests[bstack111l1lll11_opy_][bstack11ll1_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡥࡣࡷࡥࠬྑ")]
        status = bstack11ll1_opy_ (u"ࠥࡴࡦࡹࡳࡦࡦࠥྒ")
        exception = None
        bstack111l1llll1_opy_ = None
        if hook_data.name == bstack11ll1_opy_ (u"ࠦࡦ࡬ࡴࡦࡴࡢࡥࡱࡲࠢྒྷ"):
            self.bstack111ll11ll1_opy_.reset()
            bstack111l1l111l_opy_ = self.tests[bstack1lll11l1l_opy_(threading.current_thread(), bstack11ll1_opy_ (u"ࠬࡨࡥࡧࡱࡵࡩࡤࡧ࡬࡭ࡡ࡫ࡳࡴࡱ࡟ࡶࡷ࡬ࡨࠬྔ"), None)][bstack11ll1_opy_ (u"࠭ࡴࡦࡵࡷࡣࡩࡧࡴࡢࠩྕ")].result.result
            if bstack111l1l111l_opy_ == bstack11ll1_opy_ (u"ࠢࡧࡣ࡬ࡰࡪࡪࠢྖ"):
                if attrs.hook_failures == 1:
                    status = bstack11ll1_opy_ (u"ࠣࡲࡤࡷࡸ࡫ࡤࠣྗ")
                elif attrs.hook_failures == 2:
                    status = bstack11ll1_opy_ (u"ࠤࡩࡥ࡮ࡲࡥࡥࠤ྘")
            elif attrs.aborted:
                status = bstack11ll1_opy_ (u"ࠥࡪࡦ࡯࡬ࡦࡦࠥྙ")
            threading.current_thread().before_all_hook_uuid = None
        else:
            if hook_data.name == bstack11ll1_opy_ (u"ࠫࡧ࡫ࡦࡰࡴࡨࡣࡦࡲ࡬ࠨྚ") and attrs.hook_failures == 1:
                status = bstack11ll1_opy_ (u"ࠧ࡬ࡡࡪ࡮ࡨࡨࠧྛ")
            elif hasattr(attrs, bstack11ll1_opy_ (u"࠭ࡥࡳࡴࡲࡶࡤࡳࡥࡴࡵࡤ࡫ࡪ࠭ྜ")) and attrs.error_message:
                status = bstack11ll1_opy_ (u"ࠢࡧࡣ࡬ࡰࡪࡪࠢྜྷ")
            bstack111l1llll1_opy_, exception = self._111l1l11l1_opy_(attrs)
        bstack111l1lll1l_opy_ = Result(result=status, exception=exception, bstack111l1l1ll1_opy_=[bstack111l1llll1_opy_])
        hook_data.stop(time=bstack111lll1lll_opy_(), duration=0, result=bstack111l1lll1l_opy_)
        bstack11lll11l11_opy_.bstack111ll11l11_opy_(bstack11ll1_opy_ (u"ࠨࡊࡲࡳࡰࡘࡵ࡯ࡈ࡬ࡲ࡮ࡹࡨࡦࡦࠪྞ"), self.tests[bstack111l1lll11_opy_][bstack11ll1_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡥࡣࡷࡥࠬྟ")])
        threading.current_thread().current_hook_uuid = None
    def _111l1l11l1_opy_(self, attrs):
        try:
            import traceback
            bstack1l11lll11_opy_ = traceback.format_tb(attrs.exc_traceback)
            bstack111l1llll1_opy_ = bstack1l11lll11_opy_[-1] if bstack1l11lll11_opy_ else None
            exception = attrs.exception
        except Exception:
            logger.debug(bstack11ll1_opy_ (u"ࠥࡉࡷࡸ࡯ࡳࠢࡲࡧࡨࡻࡲࡳࡧࡧࠤࡼ࡮ࡩ࡭ࡧࠣ࡫ࡪࡺࡴࡪࡰࡪࠤࡨࡻࡳࡵࡱࡰࠤࡹࡸࡡࡤࡧࡥࡥࡨࡱࠢྠ"))
            bstack111l1llll1_opy_ = None
            exception = None
        return bstack111l1llll1_opy_, exception