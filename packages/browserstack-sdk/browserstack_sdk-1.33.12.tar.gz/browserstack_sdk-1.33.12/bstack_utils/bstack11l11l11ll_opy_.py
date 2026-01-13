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
from filelock import FileLock
import json
import os
import time
import uuid
import logging
from typing import Dict, List, Optional
from bstack_utils.bstack111lll1l1_opy_ import get_logger
logger = get_logger(__name__)
bstack1lllll1l1l11_opy_: Dict[str, float] = {}
bstack1lllll1l11l1_opy_: List = []
bstack1lllll11ll1l_opy_ = 5
bstack11l1ll1111_opy_ = os.path.join(os.getcwd(), bstack11ll1_opy_ (u"ࠩ࡯ࡳ࡬࠭‣"), bstack11ll1_opy_ (u"ࠪ࡯ࡪࡿ࠭࡮ࡧࡷࡶ࡮ࡩࡳ࠯࡬ࡶࡳࡳ࠭․"))
logging.getLogger(bstack11ll1_opy_ (u"ࠫ࡫࡯࡬ࡦ࡮ࡲࡧࡰ࠭‥")).setLevel(logging.WARNING)
lock = FileLock(bstack11l1ll1111_opy_+bstack11ll1_opy_ (u"ࠧ࠴࡬ࡰࡥ࡮ࠦ…"))
class bstack1lllll1l1111_opy_:
    duration: float
    name: str
    startTime: float
    worker: int
    status: bool
    failure: str
    details: Optional[str]
    entryType: str
    platform: Optional[int]
    command: Optional[str]
    hookType: Optional[str]
    cli: Optional[bool]
    def __init__(self, duration: float, name: str, start_time: float, bstack1lllll11lll1_opy_: int, status: bool, failure: str, details: Optional[str] = None, platform: Optional[int] = None, command: Optional[str] = None, test_name: Optional[str] = None, hook_type: Optional[str] = None, cli: Optional[bool] = False) -> None:
        self.duration = duration
        self.name = name
        self.startTime = start_time
        self.worker = bstack1lllll11lll1_opy_
        self.status = status
        self.failure = failure
        self.details = details
        self.entryType = bstack11ll1_opy_ (u"ࠨ࡭ࡦࡣࡶࡹࡷ࡫ࠢ‧")
        self.platform = platform
        self.command = command
        self.testName = test_name
        self.hookType = hook_type
        self.cli = cli
class bstack1lll111111l_opy_:
    global bstack1lllll1l1l11_opy_
    @staticmethod
    def bstack1lll1111lll_opy_(key: str):
        bstack1lll1l1ll11_opy_ = bstack1lll111111l_opy_.bstack11ll1111l1l_opy_(key)
        bstack1lll111111l_opy_.mark(bstack1lll1l1ll11_opy_+bstack11ll1_opy_ (u"ࠢ࠻ࡵࡷࡥࡷࡺࠢ "))
        return bstack1lll1l1ll11_opy_
    @staticmethod
    def mark(key: str) -> None:
        try:
            bstack1lllll1l1l11_opy_[key] = time.time_ns() / 1000000
        except Exception as e:
            logger.debug(bstack11ll1_opy_ (u"ࠣࡇࡵࡶࡴࡸ࠺ࠡࡽࢀࠦ ").format(e))
    @staticmethod
    def end(label: str, start: str, end: str, status: bool, failure: Optional[str] = None, hook_type: Optional[str] = None, details: Optional[str] = None, command: Optional[str] = None, test_name: Optional[str] = None) -> None:
        try:
            bstack1lll111111l_opy_.mark(end)
            bstack1lll111111l_opy_.measure(label, start, end, status, failure, hook_type, details, command, test_name)
        except Exception as e:
            logger.debug(bstack11ll1_opy_ (u"ࠤࡈࡶࡷࡵࡲࠡ࡫ࡱࠤࡰ࡫ࡹࠡ࡯ࡨࡸࡷ࡯ࡣࡴ࠼ࠣࡿࢂࠨ‪").format(e))
    @staticmethod
    def measure(label: str, start: str, end: str, status: bool, failure: Optional[str], hook_type: Optional[str] = None, details: Optional[str] = None, command: Optional[str] = None, test_name: Optional[str] = None) -> None:
        try:
            if start not in bstack1lllll1l1l11_opy_ or end not in bstack1lllll1l1l11_opy_:
                logger.debug(bstack11ll1_opy_ (u"ࠥࡉࡷࡸ࡯ࡳࠢ࡬ࡲࠥࡹࡴࡢࡴࡷࠤࡰ࡫ࡹࠡࡹ࡬ࡸ࡭ࠦࡶࡢ࡮ࡸࡩࠥࢁࡽࠡࡱࡵࠤࡪࡴࡤࠡ࡭ࡨࡽࠥࡽࡩࡵࡪࠣࡺࡦࡲࡵࡦࠢࡾࢁࠧ‫").format(start,end))
                return
            duration: float = bstack1lllll1l1l11_opy_[end] - bstack1lllll1l1l11_opy_[start]
            bstack1lllll11llll_opy_ = os.environ.get(bstack11ll1_opy_ (u"ࠦࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡆࡎࡔࡁࡓ࡛ࡢࡍࡘࡥࡒࡖࡐࡑࡍࡓࡍࠢ‬"), bstack11ll1_opy_ (u"ࠧ࡬ࡡ࡭ࡵࡨࠦ‭")).lower() == bstack11ll1_opy_ (u"ࠨࡴࡳࡷࡨࠦ‮")
            bstack1lllll1l1ll1_opy_: bstack1lllll1l1111_opy_ = bstack1lllll1l1111_opy_(duration, label, bstack1lllll1l1l11_opy_[start], os.getpid(), status, failure, details, os.environ.get(bstack11ll1_opy_ (u"ࠢࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡐࡍࡃࡗࡊࡔࡘࡍࡠࡋࡑࡈࡊ࡞ࠢ "), 0), command, test_name, hook_type, bstack1lllll11llll_opy_)
            del bstack1lllll1l1l11_opy_[start]
            del bstack1lllll1l1l11_opy_[end]
            bstack1lll111111l_opy_.bstack1lllll1l11ll_opy_(bstack1lllll1l1ll1_opy_)
        except Exception as e:
            logger.debug(bstack11ll1_opy_ (u"ࠣࡇࡵࡶࡴࡸࠠࡸࡪ࡬ࡰࡪࠦ࡭ࡦࡣࡶࡹࡷ࡯࡮ࡨࠢ࡮ࡩࡾࠦ࡭ࡦࡶࡵ࡭ࡨࡹ࠺ࠡࡽࢀࠦ‰").format(e))
    @staticmethod
    def bstack1lllll1l11ll_opy_(bstack1lllll1l1ll1_opy_):
        os.makedirs(os.path.dirname(bstack11l1ll1111_opy_)) if not os.path.exists(os.path.dirname(bstack11l1ll1111_opy_)) else None
        bstack1lll111111l_opy_.bstack1lllll1l111l_opy_()
        try:
            with lock:
                with open(bstack11l1ll1111_opy_, bstack11ll1_opy_ (u"ࠤࡵ࠯ࠧ‱"), encoding=bstack11ll1_opy_ (u"ࠥࡹࡹ࡬࠭࠹ࠤ′")) as file:
                    try:
                        data = json.load(file)
                    except json.JSONDecodeError:
                        data = []
                    data.append(bstack1lllll1l1ll1_opy_.__dict__)
                    file.seek(0)
                    file.truncate()
                    json.dump(data, file, indent=4)
        except FileNotFoundError as bstack1lllll1l1l1l_opy_:
            logger.debug(bstack11ll1_opy_ (u"ࠦࡋ࡯࡬ࡦࠢࡱࡳࡹࠦࡦࡰࡷࡱࡨࠥࢁࡽࠣ″").format(bstack1lllll1l1l1l_opy_))
            with lock:
                with open(bstack11l1ll1111_opy_, bstack11ll1_opy_ (u"ࠧࡽࠢ‴"), encoding=bstack11ll1_opy_ (u"ࠨࡵࡵࡨ࠰࠼ࠧ‵")) as file:
                    data = [bstack1lllll1l1ll1_opy_.__dict__]
                    json.dump(data, file, indent=4)
        except Exception as e:
            logger.debug(bstack11ll1_opy_ (u"ࠢࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣࡻ࡭࡯࡬ࡦࠢ࡮ࡩࡾࠦ࡭ࡦࡶࡵ࡭ࡨࡹࠠࡢࡲࡳࡩࡳࡪࠠࡼࡿࠥ‶").format(str(e)))
        finally:
            if os.path.exists(bstack11l1ll1111_opy_+bstack11ll1_opy_ (u"ࠣ࠰࡯ࡳࡨࡱࠢ‷")):
                os.remove(bstack11l1ll1111_opy_+bstack11ll1_opy_ (u"ࠤ࠱ࡰࡴࡩ࡫ࠣ‸"))
    @staticmethod
    def bstack1lllll1l111l_opy_():
        attempt = 0
        while (attempt < bstack1lllll11ll1l_opy_):
            attempt += 1
            if os.path.exists(bstack11l1ll1111_opy_+bstack11ll1_opy_ (u"ࠥ࠲ࡱࡵࡣ࡬ࠤ‹")):
                time.sleep(0.5)
            else:
                break
    @staticmethod
    def bstack11ll1111l1l_opy_(label: str) -> str:
        try:
            return bstack11ll1_opy_ (u"ࠦࢀࢃ࠺ࡼࡿࠥ›").format(label,str(uuid.uuid4().hex)[:6])
        except Exception as e:
            logger.debug(bstack11ll1_opy_ (u"ࠧࡋࡲࡳࡱࡵ࠾ࠥࢁࡽࠣ※").format(e))