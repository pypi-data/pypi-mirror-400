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
from uuid import uuid4
from bstack_utils.helper import bstack111lll1lll_opy_, bstack111ll1ll111_opy_
from bstack_utils.bstack1l1l111111_opy_ import bstack1lllll1111ll_opy_
class bstack111l111lll_opy_:
    def __init__(self, name=None, code=None, uuid=None, file_path=None, started_at=None, framework=None, tags=[], scope=[], bstack1llll111l1l1_opy_=None, bstack1llll111ll11_opy_=True, bstack1llll1111l1_opy_=None, bstack1l1l11lll1_opy_=None, result=None, duration=None, bstack1111ll11l1_opy_=None, meta={}):
        self.bstack1111ll11l1_opy_ = bstack1111ll11l1_opy_
        self.name = name
        self.code = code
        self.file_path = file_path
        self.uuid = uuid
        if not self.uuid and bstack1llll111ll11_opy_:
            self.uuid = uuid4().__str__()
        self.started_at = started_at
        self.framework = framework
        self.tags = tags
        self.scope = scope
        self.bstack1llll111l1l1_opy_ = bstack1llll111l1l1_opy_
        self.bstack1llll1111l1_opy_ = bstack1llll1111l1_opy_
        self.bstack1l1l11lll1_opy_ = bstack1l1l11lll1_opy_
        self.result = result
        self.duration = duration
        self.meta = meta
        self.hooks = []
    def bstack111l111l1l_opy_(self):
        if self.uuid:
            return self.uuid
        self.uuid = uuid4().__str__()
        return self.uuid
    def bstack111l1lllll_opy_(self, meta):
        self.meta = meta
    def bstack111ll11111_opy_(self, hooks):
        self.hooks = hooks
    def bstack1llll111lll1_opy_(self):
        bstack1llll11l1l11_opy_ = os.path.relpath(self.file_path, start=os.getcwd())
        return {
            bstack11ll1_opy_ (u"ࠧࡧ࡫࡯ࡩࡤࡴࡡ࡮ࡧࠪℝ"): bstack1llll11l1l11_opy_,
            bstack11ll1_opy_ (u"ࠨ࡮ࡲࡧࡦࡺࡩࡰࡰࠪ℞"): bstack1llll11l1l11_opy_,
            bstack11ll1_opy_ (u"ࠩࡹࡧࡤ࡬ࡩ࡭ࡧࡳࡥࡹ࡮ࠧ℟"): bstack1llll11l1l11_opy_
        }
    def set(self, **kwargs):
        for key, val in kwargs.items():
            if not hasattr(self, key):
                raise TypeError(bstack11ll1_opy_ (u"࡙ࠥࡳ࡫ࡸࡱࡧࡦࡸࡪࡪࠠࡢࡴࡪࡹࡲ࡫࡮ࡵ࠼ࠣࠦ℠") + key)
            setattr(self, key, val)
    def bstack1llll111ll1l_opy_(self):
        return {
            bstack11ll1_opy_ (u"ࠫࡳࡧ࡭ࡦࠩ℡"): self.name,
            bstack11ll1_opy_ (u"ࠬࡨ࡯ࡥࡻࠪ™"): {
                bstack11ll1_opy_ (u"࠭࡬ࡢࡰࡪࠫ℣"): bstack11ll1_opy_ (u"ࠧࡱࡻࡷ࡬ࡴࡴࠧℤ"),
                bstack11ll1_opy_ (u"ࠨࡥࡲࡨࡪ࠭℥"): self.code
            },
            bstack11ll1_opy_ (u"ࠩࡶࡧࡴࡶࡥࡴࠩΩ"): self.scope,
            bstack11ll1_opy_ (u"ࠪࡸࡦ࡭ࡳࠨ℧"): self.tags,
            bstack11ll1_opy_ (u"ࠫ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱࠧℨ"): self.framework,
            bstack11ll1_opy_ (u"ࠬࡹࡴࡢࡴࡷࡩࡩࡥࡡࡵࠩ℩"): self.started_at
        }
    def bstack1llll111llll_opy_(self):
        return {
         bstack11ll1_opy_ (u"࠭࡭ࡦࡶࡤࠫK"): self.meta
        }
    def bstack1llll11l11l1_opy_(self):
        return {
            bstack11ll1_opy_ (u"ࠧࡤࡷࡶࡸࡴࡳࡒࡦࡴࡸࡲࡕࡧࡲࡢ࡯ࠪÅ"): {
                bstack11ll1_opy_ (u"ࠨࡴࡨࡶࡺࡴ࡟࡯ࡣࡰࡩࠬℬ"): self.bstack1llll111l1l1_opy_
            }
        }
    def bstack1llll11l1111_opy_(self, bstack1llll11l1lll_opy_, details):
        step = next(filter(lambda st: st[bstack11ll1_opy_ (u"ࠩ࡬ࡨࠬℭ")] == bstack1llll11l1lll_opy_, self.meta[bstack11ll1_opy_ (u"ࠪࡷࡹ࡫ࡰࡴࠩ℮")]), None)
        step.update(details)
    def bstack1lll11ll1l_opy_(self, bstack1llll11l1lll_opy_):
        step = next(filter(lambda st: st[bstack11ll1_opy_ (u"ࠫ࡮ࡪࠧℯ")] == bstack1llll11l1lll_opy_, self.meta[bstack11ll1_opy_ (u"ࠬࡹࡴࡦࡲࡶࠫℰ")]), None)
        step.update({
            bstack11ll1_opy_ (u"࠭ࡳࡵࡣࡵࡸࡪࡪ࡟ࡢࡶࠪℱ"): bstack111lll1lll_opy_()
        })
    def bstack111l1ll1ll_opy_(self, bstack1llll11l1lll_opy_, result, duration=None):
        bstack1llll1111l1_opy_ = bstack111lll1lll_opy_()
        if bstack1llll11l1lll_opy_ is not None and self.meta.get(bstack11ll1_opy_ (u"ࠧࡴࡶࡨࡴࡸ࠭Ⅎ")):
            step = next(filter(lambda st: st[bstack11ll1_opy_ (u"ࠨ࡫ࡧࠫℳ")] == bstack1llll11l1lll_opy_, self.meta[bstack11ll1_opy_ (u"ࠩࡶࡸࡪࡶࡳࠨℴ")]), None)
            step.update({
                bstack11ll1_opy_ (u"ࠪࡪ࡮ࡴࡩࡴࡪࡨࡨࡤࡧࡴࠨℵ"): bstack1llll1111l1_opy_,
                bstack11ll1_opy_ (u"ࠫࡩࡻࡲࡢࡶ࡬ࡳࡳ࠭ℶ"): duration if duration else bstack111ll1ll111_opy_(step[bstack11ll1_opy_ (u"ࠬࡹࡴࡢࡴࡷࡩࡩࡥࡡࡵࠩℷ")], bstack1llll1111l1_opy_),
                bstack11ll1_opy_ (u"࠭ࡲࡦࡵࡸࡰࡹ࠭ℸ"): result.result,
                bstack11ll1_opy_ (u"ࠧࡧࡣ࡬ࡰࡺࡸࡥࠨℹ"): str(result.exception) if result.exception else None
            })
    def add_step(self, bstack1llll111l1ll_opy_):
        if self.meta.get(bstack11ll1_opy_ (u"ࠨࡵࡷࡩࡵࡹࠧ℺")):
            self.meta[bstack11ll1_opy_ (u"ࠩࡶࡸࡪࡶࡳࠨ℻")].append(bstack1llll111l1ll_opy_)
        else:
            self.meta[bstack11ll1_opy_ (u"ࠪࡷࡹ࡫ࡰࡴࠩℼ")] = [ bstack1llll111l1ll_opy_ ]
    def bstack1llll11l111l_opy_(self):
        return {
            bstack11ll1_opy_ (u"ࠫࡺࡻࡩࡥࠩℽ"): self.bstack111l111l1l_opy_(),
            bstack11ll1_opy_ (u"ࠬࡸࡥࡴࡷ࡯ࡸࠬℾ"): bstack11ll1_opy_ (u"࠭ࡰࡦࡰࡧ࡭ࡳ࡭ࠧℿ"),
            **self.bstack1llll111ll1l_opy_(),
            **self.bstack1llll111lll1_opy_(),
            **self.bstack1llll111llll_opy_()
        }
    def bstack1llll11l1ll1_opy_(self):
        if not self.result:
            return {}
        data = {
            bstack11ll1_opy_ (u"ࠧࡧ࡫ࡱ࡭ࡸ࡮ࡥࡥࡡࡤࡸࠬ⅀"): self.bstack1llll1111l1_opy_,
            bstack11ll1_opy_ (u"ࠨࡦࡸࡶࡦࡺࡩࡰࡰࡢ࡭ࡳࡥ࡭ࡴࠩ⅁"): self.duration,
            bstack11ll1_opy_ (u"ࠩࡵࡩࡸࡻ࡬ࡵࠩ⅂"): self.result.result
        }
        if data[bstack11ll1_opy_ (u"ࠪࡶࡪࡹࡵ࡭ࡶࠪ⅃")] == bstack11ll1_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡧࡧࠫ⅄"):
            data[bstack11ll1_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡸࡶࡪࡥࡴࡺࡲࡨࠫⅅ")] = self.result.bstack1lllll1ll11_opy_()
            data[bstack11ll1_opy_ (u"࠭ࡦࡢ࡫࡯ࡹࡷ࡫ࠧⅆ")] = [{bstack11ll1_opy_ (u"ࠧࡣࡣࡦ࡯ࡹࡸࡡࡤࡧࠪⅇ"): self.result.bstack111ll11ll11_opy_()}]
        return data
    def bstack1llll11ll1l1_opy_(self):
        return {
            bstack11ll1_opy_ (u"ࠨࡷࡸ࡭ࡩ࠭ⅈ"): self.bstack111l111l1l_opy_(),
            **self.bstack1llll111ll1l_opy_(),
            **self.bstack1llll111lll1_opy_(),
            **self.bstack1llll11l1ll1_opy_(),
            **self.bstack1llll111llll_opy_()
        }
    def bstack111l111ll1_opy_(self, event, result=None):
        if result:
            self.result = result
        if bstack11ll1_opy_ (u"ࠩࡖࡸࡦࡸࡴࡦࡦࠪⅉ") in event:
            return self.bstack1llll11l111l_opy_()
        elif bstack11ll1_opy_ (u"ࠪࡊ࡮ࡴࡩࡴࡪࡨࡨࠬ⅊") in event:
            return self.bstack1llll11ll1l1_opy_()
    def bstack1111ll1111_opy_(self):
        pass
    def stop(self, time=None, duration=None, result=None):
        self.bstack1llll1111l1_opy_ = time if time else bstack111lll1lll_opy_()
        self.duration = duration if duration else bstack111ll1ll111_opy_(self.started_at, self.bstack1llll1111l1_opy_)
        if result:
            self.result = result
class bstack111ll111ll_opy_(bstack111l111lll_opy_):
    def __init__(self, hooks=[], bstack111l1l11ll_opy_={}, *args, **kwargs):
        self.hooks = hooks
        self.bstack111l1l11ll_opy_ = bstack111l1l11ll_opy_
        super().__init__(*args, **kwargs, bstack1l1l11lll1_opy_=bstack11ll1_opy_ (u"ࠫࡹ࡫ࡳࡵࠩ⅋"))
    @classmethod
    def bstack1llll11ll111_opy_(cls, scenario, feature, test, **kwargs):
        steps = []
        for step in scenario.steps:
            steps.append({
                bstack11ll1_opy_ (u"ࠬ࡯ࡤࠨ⅌"): id(step),
                bstack11ll1_opy_ (u"࠭ࡴࡦࡺࡷࠫ⅍"): step.name,
                bstack11ll1_opy_ (u"ࠧ࡬ࡧࡼࡻࡴࡸࡤࠨⅎ"): step.keyword,
            })
        return bstack111ll111ll_opy_(
            **kwargs,
            meta={
                bstack11ll1_opy_ (u"ࠨࡨࡨࡥࡹࡻࡲࡦࠩ⅏"): {
                    bstack11ll1_opy_ (u"ࠩࡱࡥࡲ࡫ࠧ⅐"): feature.name,
                    bstack11ll1_opy_ (u"ࠪࡴࡦࡺࡨࠨ⅑"): feature.filename,
                    bstack11ll1_opy_ (u"ࠫࡩ࡫ࡳࡤࡴ࡬ࡴࡹ࡯࡯࡯ࠩ⅒"): feature.description
                },
                bstack11ll1_opy_ (u"ࠬࡹࡣࡦࡰࡤࡶ࡮ࡵࠧ⅓"): {
                    bstack11ll1_opy_ (u"࠭࡮ࡢ࡯ࡨࠫ⅔"): scenario.name
                },
                bstack11ll1_opy_ (u"ࠧࡴࡶࡨࡴࡸ࠭⅕"): steps,
                bstack11ll1_opy_ (u"ࠨࡧࡻࡥࡲࡶ࡬ࡦࡵࠪ⅖"): bstack1lllll1111ll_opy_(test)
            }
        )
    def bstack1llll11ll11l_opy_(self):
        return {
            bstack11ll1_opy_ (u"ࠩ࡫ࡳࡴࡱࡳࠨ⅗"): self.hooks
        }
    def bstack1llll11l1l1l_opy_(self):
        if self.bstack111l1l11ll_opy_:
            return {
                bstack11ll1_opy_ (u"ࠪ࡭ࡳࡺࡥࡨࡴࡤࡸ࡮ࡵ࡮ࡴࠩ⅘"): self.bstack111l1l11ll_opy_
            }
        return {}
    def bstack1llll11ll1l1_opy_(self):
        return {
            **super().bstack1llll11ll1l1_opy_(),
            **self.bstack1llll11ll11l_opy_()
        }
    def bstack1llll11l111l_opy_(self):
        return {
            **super().bstack1llll11l111l_opy_(),
            **self.bstack1llll11l1l1l_opy_()
        }
    def bstack1111ll1111_opy_(self):
        return bstack11ll1_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡵࡹࡳ࠭⅙")
class bstack111l1ll1l1_opy_(bstack111l111lll_opy_):
    def __init__(self, hook_type, *args,bstack111l1l11ll_opy_={}, **kwargs):
        self.hook_type = hook_type
        self.bstack1l111lll1l1_opy_ = None
        self.bstack111l1l11ll_opy_ = bstack111l1l11ll_opy_
        super().__init__(*args, **kwargs, bstack1l1l11lll1_opy_=bstack11ll1_opy_ (u"ࠬ࡮࡯ࡰ࡭ࠪ⅚"))
    def bstack1111ll1l1l_opy_(self):
        return self.hook_type
    def bstack1llll11l11ll_opy_(self):
        return {
            bstack11ll1_opy_ (u"࠭ࡨࡰࡱ࡮ࡣࡹࡿࡰࡦࠩ⅛"): self.hook_type
        }
    def bstack1llll11ll1l1_opy_(self):
        return {
            **super().bstack1llll11ll1l1_opy_(),
            **self.bstack1llll11l11ll_opy_()
        }
    def bstack1llll11l111l_opy_(self):
        return {
            **super().bstack1llll11l111l_opy_(),
            bstack11ll1_opy_ (u"ࠧࡵࡧࡶࡸࡤࡸࡵ࡯ࡡ࡬ࡨࠬ⅜"): self.bstack1l111lll1l1_opy_,
            **self.bstack1llll11l11ll_opy_()
        }
    def bstack1111ll1111_opy_(self):
        return bstack11ll1_opy_ (u"ࠨࡪࡲࡳࡰࡥࡲࡶࡰࠪ⅝")
    def bstack111ll11l1l_opy_(self, bstack1l111lll1l1_opy_):
        self.bstack1l111lll1l1_opy_ = bstack1l111lll1l1_opy_