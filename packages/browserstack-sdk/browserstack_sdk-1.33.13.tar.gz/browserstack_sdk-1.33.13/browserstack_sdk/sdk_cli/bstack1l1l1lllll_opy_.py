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
from collections import defaultdict
from threading import Lock
from dataclasses import dataclass
import logging
import traceback
from typing import List, Dict, Any
import os
@dataclass
class bstack1l1lll1l1l_opy_:
    sdk_version: str
    path_config: str
    path_project: str
    test_framework: str
    frameworks: List[str]
    framework_versions: Dict[str, str]
    bs_config: Dict[str, Any]
@dataclass
class bstack1llll1111l_opy_:
    pass
class bstack111111lll_opy_:
    bstack1l11ll1l1l_opy_ = bstack11l1l_opy_ (u"ࠧࡨ࡯ࡰࡶࡶࡸࡷࡧࡰࠣᇋ")
    CONNECT = bstack11l1l_opy_ (u"ࠨࡣࡰࡰࡱࡩࡨࡺࠢᇌ")
    bstack1l1111lll1_opy_ = bstack11l1l_opy_ (u"ࠢࡴࡪࡸࡸࡩࡵࡷ࡯ࠤᇍ")
    CONFIG = bstack11l1l_opy_ (u"ࠣࡥࡲࡲ࡫࡯ࡧࠣᇎ")
    bstack1ll11l1ll11_opy_ = bstack11l1l_opy_ (u"ࠤࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࡸࠨᇏ")
    bstack1lll1111l1_opy_ = bstack11l1l_opy_ (u"ࠥࡩࡽ࡯ࡴࠣᇐ")
class bstack1ll11l1l1ll_opy_:
    bstack1ll11ll11l1_opy_ = bstack11l1l_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡷࡹࡧࡲࡵࡧࡧࠦᇑ")
    FINISHED = bstack11l1l_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣ࡫࡯࡮ࡪࡵ࡫ࡩࡩࠨᇒ")
class bstack1ll11l1ll1l_opy_:
    bstack1ll11ll11l1_opy_ = bstack11l1l_opy_ (u"ࠨࡴࡦࡵࡷࡣࡷࡻ࡮ࡠࡵࡷࡥࡷࡺࡥࡥࠤᇓ")
    FINISHED = bstack11l1l_opy_ (u"ࠢࡵࡧࡶࡸࡤࡸࡵ࡯ࡡࡩ࡭ࡳ࡯ࡳࡩࡧࡧࠦᇔ")
class bstack1ll11l1lll1_opy_:
    bstack1ll11ll11l1_opy_ = bstack11l1l_opy_ (u"ࠣࡪࡲࡳࡰࡥࡲࡶࡰࡢࡷࡹࡧࡲࡵࡧࡧࠦᇕ")
    FINISHED = bstack11l1l_opy_ (u"ࠤ࡫ࡳࡴࡱ࡟ࡳࡷࡱࡣ࡫࡯࡮ࡪࡵ࡫ࡩࡩࠨᇖ")
class bstack1ll11ll111l_opy_:
    bstack1ll11ll1111_opy_ = bstack11l1l_opy_ (u"ࠥࡧࡧࡺ࡟ࡴࡧࡶࡷ࡮ࡵ࡮ࡠࡥࡵࡩࡦࡺࡥࡥࠤᇗ")
class bstack1ll11l1llll_opy_:
    _1ll11ll1lll_opy_ = None
    def __new__(cls):
        if not cls._1ll11ll1lll_opy_:
            cls._1ll11ll1lll_opy_ = super(bstack1ll11l1llll_opy_, cls).__new__(cls)
        return cls._1ll11ll1lll_opy_
    def __init__(self):
        self._hooks = defaultdict(lambda: defaultdict(list))
        self._lock = Lock()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
    def clear(self):
        with self._lock:
            self._hooks = defaultdict(list)
    def register(self, event_name, callback):
        with self._lock:
            if not callable(callback):
                raise ValueError(bstack11l1l_opy_ (u"ࠦࡈࡧ࡬࡭ࡤࡤࡧࡰࠦ࡭ࡶࡵࡷࠤࡧ࡫ࠠࡤࡣ࡯ࡰࡦࡨ࡬ࡦࠢࡩࡳࡷࠦࠢᇘ") + event_name)
            pid = os.getpid()
            self.logger.debug(bstack11l1l_opy_ (u"ࠧࡘࡥࡨ࡫ࡶࡸࡪࡸࡩ࡯ࡩࠣࡧࡦࡲ࡬ࡣࡣࡦ࡯ࠥ࡬࡯ࡳࠢࡨࡺࡪࡴࡴࠡࠩࡾࡩࡻ࡫࡮ࡵࡡࡱࡥࡲ࡫ࡽࠨࠢࡺ࡭ࡹ࡮ࠠࡱ࡫ࡧࠤࠧᇙ") + str(pid) + bstack11l1l_opy_ (u"ࠨࠢᇚ"))
            self._hooks[event_name][pid].append(callback)
    def invoke(self, event_name, *args, **kwargs):
        with self._lock:
            pid = os.getpid()
            callbacks = self._hooks.get(event_name, {}).get(pid, [])
            if not callbacks:
                self.logger.warning(bstack11l1l_opy_ (u"ࠢࡏࡱࠣࡧࡦࡲ࡬ࡣࡣࡦ࡯ࡸࠦࡦࡰࡴࠣࡩࡻ࡫࡮ࡵࠢࠪࡿࡪࡼࡥ࡯ࡶࡢࡲࡦࡳࡥࡾࠩࠣࡻ࡮ࡺࡨࠡࡲ࡬ࡨࠥࠨᇛ") + str(pid) + bstack11l1l_opy_ (u"ࠣࠤᇜ"))
                return
            self.logger.debug(bstack11l1l_opy_ (u"ࠤࡌࡲࡻࡵ࡫ࡪࡰࡪࠤࢀࡲࡥ࡯ࠪࡦࡥࡱࡲࡢࡢࡥ࡮ࡷ࠮ࢃࠠࡤࡣ࡯ࡰࡧࡧࡣ࡬ࡵࠣࡪࡴࡸࠠࡦࡸࡨࡲࡹࠦࠧࡼࡧࡹࡩࡳࡺ࡟࡯ࡣࡰࡩࢂ࠭ࠠࡸ࡫ࡷ࡬ࠥࡶࡩࡥࠢࠥᇝ") + str(pid) + bstack11l1l_opy_ (u"ࠥࠦᇞ"))
            for callback in callbacks:
                try:
                    self.logger.debug(bstack11l1l_opy_ (u"ࠦࡎࡴࡶࡰ࡭ࡨࡨࠥࡩࡡ࡭࡮ࡥࡥࡨࡱࠠࡧࡱࡵࠤࡪࡼࡥ࡯ࡶࠣࠫࢀ࡫ࡶࡦࡰࡷࡣࡳࡧ࡭ࡦࡿࠪࠤࡼ࡯ࡴࡩࠢࡳ࡭ࡩࠦࠢᇟ") + str(pid) + bstack11l1l_opy_ (u"ࠧࠨᇠ"))
                    callback(event_name, *args, **kwargs)
                except Exception as e:
                    self.logger.error(bstack11l1l_opy_ (u"ࠨࡅࡳࡴࡲࡶࠥ࡯࡮ࡷࡱ࡮࡭ࡳ࡭ࠠࡤࡣ࡯ࡰࡧࡧࡣ࡬ࠢࡩࡳࡷࠦࡥࡷࡧࡱࡸࠥ࠭ࡻࡦࡸࡨࡲࡹࡥ࡮ࡢ࡯ࡨࢁࠬࠦࡷࡪࡶ࡫ࠤࡵ࡯ࡤࠡࡽࡳ࡭ࡩࢃ࠺ࠡࠤᇡ") + str(e) + bstack11l1l_opy_ (u"ࠢࠣᇢ"))
                    traceback.print_exc()
bstack1l1l1lllll_opy_ = bstack1ll11l1llll_opy_()