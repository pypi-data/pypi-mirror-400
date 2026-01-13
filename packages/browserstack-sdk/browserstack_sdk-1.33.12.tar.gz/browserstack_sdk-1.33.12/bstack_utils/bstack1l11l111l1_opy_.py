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
import json
from bstack_utils.bstack111lll1l1_opy_ import get_logger
logger = get_logger(__name__)
class bstack11l1lll1111_opy_(object):
  bstack11lll1lll_opy_ = os.path.join(os.path.expanduser(bstack11ll1_opy_ (u"ࠪࢂࠬ៰")), bstack11ll1_opy_ (u"ࠫ࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࠫ៱"))
  bstack11l1ll1lll1_opy_ = os.path.join(bstack11lll1lll_opy_, bstack11ll1_opy_ (u"ࠬࡩ࡯࡮࡯ࡤࡲࡩࡹ࠮࡫ࡵࡲࡲࠬ៲"))
  commands_to_wrap = None
  perform_scan = None
  bstack1l11lll1l_opy_ = None
  bstack1lll11ll_opy_ = None
  bstack11ll111llll_opy_ = None
  bstack11ll11111ll_opy_ = None
  def __new__(cls):
    if not hasattr(cls, bstack11ll1_opy_ (u"࠭ࡩ࡯ࡵࡷࡥࡳࡩࡥࠨ៳")):
      cls.instance = super(bstack11l1lll1111_opy_, cls).__new__(cls)
      cls.instance.bstack11l1lll111l_opy_()
    return cls.instance
  def bstack11l1lll111l_opy_(self):
    try:
      with open(self.bstack11l1ll1lll1_opy_, bstack11ll1_opy_ (u"ࠧࡳࠩ៴")) as bstack1l1l11l1_opy_:
        bstack11l1ll1llll_opy_ = bstack1l1l11l1_opy_.read()
        data = json.loads(bstack11l1ll1llll_opy_)
        if bstack11ll1_opy_ (u"ࠨࡥࡲࡱࡲࡧ࡮ࡥࡵࠪ៵") in data:
          self.bstack11ll11l111l_opy_(data[bstack11ll1_opy_ (u"ࠩࡦࡳࡲࡳࡡ࡯ࡦࡶࠫ៶")])
        if bstack11ll1_opy_ (u"ࠪࡷࡨࡸࡩࡱࡶࡶࠫ៷") in data:
          self.bstack111l1ll1l_opy_(data[bstack11ll1_opy_ (u"ࠫࡸࡩࡲࡪࡲࡷࡷࠬ៸")])
        if bstack11ll1_opy_ (u"ࠬࡴ࡯࡯ࡄࡖࡸࡦࡩ࡫ࡊࡰࡩࡶࡦࡇ࠱࠲ࡻࡆ࡬ࡷࡵ࡭ࡦࡑࡳࡸ࡮ࡵ࡮ࡴࠩ៹") in data:
          self.bstack11l1lll11l1_opy_(data[bstack11ll1_opy_ (u"࠭࡮ࡰࡰࡅࡗࡹࡧࡣ࡬ࡋࡱࡪࡷࡧࡁ࠲࠳ࡼࡇ࡭ࡸ࡯࡮ࡧࡒࡴࡹ࡯࡯࡯ࡵࠪ៺")])
    except:
      pass
  def bstack11l1lll11l1_opy_(self, bstack11ll11111ll_opy_):
    if bstack11ll11111ll_opy_ != None:
      self.bstack11ll11111ll_opy_ = bstack11ll11111ll_opy_
  def bstack111l1ll1l_opy_(self, scripts):
    if scripts != None:
      self.perform_scan = scripts.get(bstack11ll1_opy_ (u"ࠧࡴࡥࡤࡲࠬ៻"),bstack11ll1_opy_ (u"ࠨࠩ៼"))
      self.bstack1l11lll1l_opy_ = scripts.get(bstack11ll1_opy_ (u"ࠩࡪࡩࡹࡘࡥࡴࡷ࡯ࡸࡸ࠭៽"),bstack11ll1_opy_ (u"ࠪࠫ៾"))
      self.bstack1lll11ll_opy_ = scripts.get(bstack11ll1_opy_ (u"ࠫ࡬࡫ࡴࡓࡧࡶࡹࡱࡺࡳࡔࡷࡰࡱࡦࡸࡹࠨ៿"),bstack11ll1_opy_ (u"ࠬ࠭᠀"))
      self.bstack11ll111llll_opy_ = scripts.get(bstack11ll1_opy_ (u"࠭ࡳࡢࡸࡨࡖࡪࡹࡵ࡭ࡶࡶࠫ᠁"),bstack11ll1_opy_ (u"ࠧࠨ᠂"))
  def bstack11ll11l111l_opy_(self, commands_to_wrap):
    if commands_to_wrap != None and len(commands_to_wrap) != 0:
      self.commands_to_wrap = commands_to_wrap
  def store(self):
    try:
      with open(self.bstack11l1ll1lll1_opy_, bstack11ll1_opy_ (u"ࠨࡹࠪ᠃")) as file:
        json.dump({
          bstack11ll1_opy_ (u"ࠤࡦࡳࡲࡳࡡ࡯ࡦࡶࠦ᠄"): self.commands_to_wrap,
          bstack11ll1_opy_ (u"ࠥࡷࡨࡸࡩࡱࡶࡶࠦ᠅"): {
            bstack11ll1_opy_ (u"ࠦࡸࡩࡡ࡯ࠤ᠆"): self.perform_scan,
            bstack11ll1_opy_ (u"ࠧ࡭ࡥࡵࡔࡨࡷࡺࡲࡴࡴࠤ᠇"): self.bstack1l11lll1l_opy_,
            bstack11ll1_opy_ (u"ࠨࡧࡦࡶࡕࡩࡸࡻ࡬ࡵࡵࡖࡹࡲࡳࡡࡳࡻࠥ᠈"): self.bstack1lll11ll_opy_,
            bstack11ll1_opy_ (u"ࠢࡴࡣࡹࡩࡗ࡫ࡳࡶ࡮ࡷࡷࠧ᠉"): self.bstack11ll111llll_opy_
          },
          bstack11ll1_opy_ (u"ࠣࡰࡲࡲࡇ࡙ࡴࡢࡥ࡮ࡍࡳ࡬ࡲࡢࡃ࠴࠵ࡾࡉࡨࡳࡱࡰࡩࡔࡶࡴࡪࡱࡱࡷࠧ᠊"): self.bstack11ll11111ll_opy_
        }, file)
    except Exception as e:
      logger.error(bstack11ll1_opy_ (u"ࠤࡈࡶࡷࡵࡲࠡࡹ࡫࡭ࡱ࡫ࠠࡴࡶࡲࡶ࡮ࡴࡧࠡࡥࡲࡱࡲࡧ࡮ࡥࡵ࠽ࠤࢀࢃࠢ᠋").format(e))
      pass
  def bstack1ll1l1111l_opy_(self, command_name):
    try:
      return any(command.get(bstack11ll1_opy_ (u"ࠪࡲࡦࡳࡥࠨ᠌")) == command_name for command in self.commands_to_wrap)
    except:
      return False
bstack1l11l111l1_opy_ = bstack11l1lll1111_opy_()