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
import re
import sys
import json
import time
import shutil
import tempfile
import requests
import subprocess
from threading import Thread
from os.path import expanduser
from bstack_utils.constants import *
from requests.auth import HTTPBasicAuth
from bstack_utils.helper import bstack11l1l1l11l_opy_
from bstack_utils.measure import measure
from bstack_utils.bstack111ll1l1ll_opy_ import bstack1111l1lll_opy_
class bstack11l1l11l1_opy_:
  working_dir = os.getcwd()
  bstack1l1lll1l_opy_ = False
  config = {}
  bstack111ll1111ll_opy_ = bstack11ll1_opy_ (u"ࠪࠫᾟ")
  binary_path = bstack11ll1_opy_ (u"ࠫࠬᾠ")
  bstack1111111ll1l_opy_ = bstack11ll1_opy_ (u"ࠬ࠭ᾡ")
  bstack11111lll_opy_ = False
  bstack1llllll11l1l_opy_ = None
  bstack111111ll1l1_opy_ = {}
  bstack1lllllll1ll1_opy_ = 300
  bstack1llllllll1ll_opy_ = False
  logger = None
  bstack111111l1111_opy_ = False
  bstack1l1l1lll1_opy_ = False
  percy_build_id = None
  bstack1111111l11l_opy_ = bstack11ll1_opy_ (u"࠭ࠧᾢ")
  bstack1lllllll11l1_opy_ = {
    bstack11ll1_opy_ (u"ࠧࡤࡪࡵࡳࡲ࡫ࠧᾣ") : 1,
    bstack11ll1_opy_ (u"ࠨࡨ࡬ࡶࡪ࡬࡯ࡹࠩᾤ") : 2,
    bstack11ll1_opy_ (u"ࠩࡨࡨ࡬࡫ࠧᾥ") : 3,
    bstack11ll1_opy_ (u"ࠪࡷࡦ࡬ࡡࡳ࡫ࠪᾦ") : 4
  }
  def __init__(self) -> None: pass
  def bstack1111111llll_opy_(self):
    bstack11111111l1l_opy_ = bstack11ll1_opy_ (u"ࠫࠬᾧ")
    bstack111111111ll_opy_ = sys.platform
    bstack1111111l1ll_opy_ = bstack11ll1_opy_ (u"ࠬࡶࡥࡳࡥࡼࠫᾨ")
    if re.match(bstack11ll1_opy_ (u"ࠨࡤࡢࡴࡺ࡭ࡳࢂ࡭ࡢࡥࠣࡳࡸࠨᾩ"), bstack111111111ll_opy_) != None:
      bstack11111111l1l_opy_ = bstack11l1l111l11_opy_ + bstack11ll1_opy_ (u"ࠢ࠰ࡲࡨࡶࡨࡿ࠭ࡰࡵࡻ࠲ࡿ࡯ࡰࠣᾪ")
      self.bstack1111111l11l_opy_ = bstack11ll1_opy_ (u"ࠨ࡯ࡤࡧࠬᾫ")
    elif re.match(bstack11ll1_opy_ (u"ࠤࡰࡷࡼ࡯࡮ࡽ࡯ࡶࡽࡸࢂ࡭ࡪࡰࡪࡻࢁࡩࡹࡨࡹ࡬ࡲࢁࡨࡣࡤࡹ࡬ࡲࢁࡽࡩ࡯ࡥࡨࢀࡪࡳࡣࡽࡹ࡬ࡲ࠸࠸ࠢᾬ"), bstack111111111ll_opy_) != None:
      bstack11111111l1l_opy_ = bstack11l1l111l11_opy_ + bstack11ll1_opy_ (u"ࠥ࠳ࡵ࡫ࡲࡤࡻ࠰ࡻ࡮ࡴ࠮ࡻ࡫ࡳࠦᾭ")
      bstack1111111l1ll_opy_ = bstack11ll1_opy_ (u"ࠦࡵ࡫ࡲࡤࡻ࠱ࡩࡽ࡫ࠢᾮ")
      self.bstack1111111l11l_opy_ = bstack11ll1_opy_ (u"ࠬࡽࡩ࡯ࠩᾯ")
    else:
      bstack11111111l1l_opy_ = bstack11l1l111l11_opy_ + bstack11ll1_opy_ (u"ࠨ࠯ࡱࡧࡵࡧࡾ࠳࡬ࡪࡰࡸࡼ࠳ࢀࡩࡱࠤᾰ")
      self.bstack1111111l11l_opy_ = bstack11ll1_opy_ (u"ࠧ࡭࡫ࡱࡹࡽ࠭ᾱ")
    return bstack11111111l1l_opy_, bstack1111111l1ll_opy_
  def bstack1111111111l_opy_(self):
    try:
      bstack111111l1l1l_opy_ = [os.path.join(expanduser(bstack11ll1_opy_ (u"ࠣࢀࠥᾲ")), bstack11ll1_opy_ (u"ࠩ࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࠩᾳ")), self.working_dir, tempfile.gettempdir()]
      for path in bstack111111l1l1l_opy_:
        if(self.bstack111111l11ll_opy_(path)):
          return path
      raise bstack11ll1_opy_ (u"࡙ࠥࡳࡧࡢ࡭ࡧࠣࡸࡴࠦࡤࡰࡹࡱࡰࡴࡧࡤࠡࡲࡨࡶࡨࡿࠠࡣ࡫ࡱࡥࡷࡿࠢᾴ")
    except Exception as e:
      self.logger.error(bstack11ll1_opy_ (u"ࠦࡋࡧࡩ࡭ࡧࡧࠤࡹࡵࠠࡧ࡫ࡱࡨࠥࡧࡶࡢ࡫࡯ࡥࡧࡲࡥࠡࡲࡤࡸ࡭ࠦࡦࡰࡴࠣࡴࡪࡸࡣࡺࠢࡧࡳࡼࡴ࡬ࡰࡣࡧ࠰ࠥࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡ࠯ࠣࡿࢂࠨ᾵").format(e))
  def bstack111111l11ll_opy_(self, path):
    try:
      if not os.path.exists(path):
        os.makedirs(path)
      return True
    except:
      return False
  def bstack1llllll1lll1_opy_(self, bstack111111lll11_opy_):
    return os.path.join(bstack111111lll11_opy_, self.bstack111ll1111ll_opy_ + bstack11ll1_opy_ (u"ࠧ࠴ࡥࡵࡣࡪࠦᾶ"))
  def bstack1lllllllllll_opy_(self, bstack111111lll11_opy_, bstack111111llll1_opy_):
    if not bstack111111llll1_opy_: return
    try:
      bstack11111l11l11_opy_ = self.bstack1llllll1lll1_opy_(bstack111111lll11_opy_)
      with open(bstack11111l11l11_opy_, bstack11ll1_opy_ (u"ࠨࡷࠣᾷ")) as f:
        f.write(bstack111111llll1_opy_)
        self.logger.debug(bstack11ll1_opy_ (u"ࠢࡔࡣࡹࡩࡩࠦ࡮ࡦࡹࠣࡉ࡙ࡧࡧࠡࡨࡲࡶࠥࡶࡥࡳࡥࡼࠦᾸ"))
    except Exception as e:
      self.logger.error(bstack11ll1_opy_ (u"ࠣࡗࡱࡥࡧࡲࡥࠡࡶࡲࠤࡸࡧࡶࡦࠢࡷ࡬ࡪࠦࡥࡵࡣࡪ࠰ࠥ࡫ࡲࡳࡱࡵ࠾ࠥࢁࡽࠣᾹ").format(e))
  def bstack1111111l1l1_opy_(self, bstack111111lll11_opy_):
    try:
      bstack11111l11l11_opy_ = self.bstack1llllll1lll1_opy_(bstack111111lll11_opy_)
      if os.path.exists(bstack11111l11l11_opy_):
        with open(bstack11111l11l11_opy_, bstack11ll1_opy_ (u"ࠤࡵࠦᾺ")) as f:
          bstack111111llll1_opy_ = f.read().strip()
          return bstack111111llll1_opy_ if bstack111111llll1_opy_ else None
    except Exception as e:
      self.logger.error(bstack11ll1_opy_ (u"ࠥࡊࡦ࡯࡬ࡦࡦࠣࡰࡴࡧࡤࡪࡰࡪࠤࡊ࡚ࡡࡨ࠮ࠣࡩࡷࡸ࡯ࡳ࠼ࠣࡿࢂࠨΆ").format(e))
  def bstack11111l111ll_opy_(self, bstack111111lll11_opy_, bstack11111111l1l_opy_):
    bstack111111l1l11_opy_ = self.bstack1111111l1l1_opy_(bstack111111lll11_opy_)
    if bstack111111l1l11_opy_:
      try:
        bstack1llllllllll1_opy_ = self.bstack11111111l11_opy_(bstack111111l1l11_opy_, bstack11111111l1l_opy_)
        if not bstack1llllllllll1_opy_:
          self.logger.debug(bstack11ll1_opy_ (u"ࠦࡕ࡫ࡲࡤࡻࠣࡦ࡮ࡴࡡࡳࡻࠣ࡭ࡸࠦࡵࡱࠢࡷࡳࠥࡪࡡࡵࡧࠣࠬࡊ࡚ࡡࡨࠢࡸࡲࡨ࡮ࡡ࡯ࡩࡨࡨ࠮ࠨᾼ"))
          return True
        self.logger.debug(bstack11ll1_opy_ (u"ࠧࡔࡥࡸࠢࡓࡩࡷࡩࡹࠡࡤ࡬ࡲࡦࡸࡹࠡࡸࡨࡶࡸ࡯࡯࡯ࠢࡤࡺࡦ࡯࡬ࡢࡤ࡯ࡩ࠱ࠦࡤࡰࡹࡱࡰࡴࡧࡤࡪࡰࡪࠤࡺࡶࡤࡢࡶࡨࠦ᾽"))
        return False
      except Exception as e:
        self.logger.warn(bstack11ll1_opy_ (u"ࠨࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡦ࡬ࡪࡩ࡫ࠡࡨࡲࡶࠥࡨࡩ࡯ࡣࡵࡽࠥࡻࡰࡥࡣࡷࡩࡸ࠲ࠠࡶࡵ࡬ࡲ࡬ࠦࡥࡹ࡫ࡶࡸ࡮ࡴࡧࠡࡤ࡬ࡲࡦࡸࡹ࠻ࠢࡾࢁࠧι").format(e))
    return False
  def bstack11111111l11_opy_(self, bstack111111l1l11_opy_, bstack11111111l1l_opy_):
    try:
      headers = {
        bstack11ll1_opy_ (u"ࠢࡊࡨ࠰ࡒࡴࡴࡥ࠮ࡏࡤࡸࡨ࡮ࠢ᾿"): bstack111111l1l11_opy_
      }
      response = bstack11l1l1l11l_opy_(bstack11ll1_opy_ (u"ࠨࡉࡈࡘࠬ῀"), bstack11111111l1l_opy_, {}, {bstack11ll1_opy_ (u"ࠤ࡫ࡩࡦࡪࡥࡳࡵࠥ῁"): headers})
      if response.status_code == 304:
        return False
      return True
    except Exception as e:
      raise(bstack11ll1_opy_ (u"ࠥࡉࡷࡸ࡯ࡳࠢࡦ࡬ࡪࡩ࡫ࡪࡰࡪࠤ࡫ࡵࡲࠡࡒࡨࡶࡨࡿࠠࡣ࡫ࡱࡥࡷࡿࠠࡶࡲࡧࡥࡹ࡫ࡳ࠻ࠢࡾࢁࠧῂ").format(e))
  @measure(event_name=EVENTS.bstack11l11lll111_opy_, stage=STAGE.bstack11l1llll1_opy_)
  def bstack111111l111l_opy_(self, bstack11111111l1l_opy_, bstack1111111l1ll_opy_):
    try:
      bstack1llllll1l111_opy_ = self.bstack1111111111l_opy_()
      bstack1llllllll1l1_opy_ = os.path.join(bstack1llllll1l111_opy_, bstack11ll1_opy_ (u"ࠫࡵ࡫ࡲࡤࡻ࠱ࡾ࡮ࡶࠧῃ"))
      bstack11111111111_opy_ = os.path.join(bstack1llllll1l111_opy_, bstack1111111l1ll_opy_)
      if self.bstack11111l111ll_opy_(bstack1llllll1l111_opy_, bstack11111111l1l_opy_): # if bstack111111ll11l_opy_, bstack11llll11ll1_opy_ bstack111111llll1_opy_ is bstack111111lllll_opy_ to bstack111ll1l1l11_opy_ version available (response 304)
        if os.path.exists(bstack11111111111_opy_):
          self.logger.info(bstack11ll1_opy_ (u"ࠧࡖࡥࡳࡥࡼࠤࡧ࡯࡮ࡢࡴࡼࠤ࡫ࡵࡵ࡯ࡦࠣ࡭ࡳࠦࡻࡾ࠮ࠣࡷࡰ࡯ࡰࡱ࡫ࡱ࡫ࠥࡪ࡯ࡸࡰ࡯ࡳࡦࡪࠢῄ").format(bstack11111111111_opy_))
          return bstack11111111111_opy_
        if os.path.exists(bstack1llllllll1l1_opy_):
          self.logger.info(bstack11ll1_opy_ (u"ࠨࡐࡦࡴࡦࡽࠥࢀࡩࡱࠢࡩࡳࡺࡴࡤࠡ࡫ࡱࠤࢀࢃࠬࠡࡷࡱࡾ࡮ࡶࡰࡪࡰࡪࠦ῅").format(bstack1llllllll1l1_opy_))
          return self.bstack1llllll11l11_opy_(bstack1llllllll1l1_opy_, bstack1111111l1ll_opy_)
      self.logger.info(bstack11ll1_opy_ (u"ࠢࡅࡱࡺࡲࡱࡵࡡࡥ࡫ࡱ࡫ࠥࡶࡥࡳࡥࡼࠤࡧ࡯࡮ࡢࡴࡼࠤ࡫ࡸ࡯࡮ࠢࡾࢁࠧῆ").format(bstack11111111l1l_opy_))
      response = bstack11l1l1l11l_opy_(bstack11ll1_opy_ (u"ࠨࡉࡈࡘࠬῇ"), bstack11111111l1l_opy_, {}, {})
      if response.status_code == 200:
        bstack111111ll111_opy_ = response.headers.get(bstack11ll1_opy_ (u"ࠤࡈࡘࡦ࡭ࠢῈ"), bstack11ll1_opy_ (u"ࠥࠦΈ"))
        if bstack111111ll111_opy_:
          self.bstack1lllllllllll_opy_(bstack1llllll1l111_opy_, bstack111111ll111_opy_)
        with open(bstack1llllllll1l1_opy_, bstack11ll1_opy_ (u"ࠫࡼࡨࠧῊ")) as file:
          file.write(response.content)
        self.logger.info(bstack11ll1_opy_ (u"ࠧࡊ࡯ࡸࡰ࡯ࡳࡦࡪࡥࡥࠢࡳࡩࡷࡩࡹࠡࡤ࡬ࡲࡦࡸࡹࠡࡣࡱࡨࠥࡹࡡࡷࡧࡧࠤࡦࡺࠠࡼࡿࠥΉ").format(bstack1llllllll1l1_opy_))
        return self.bstack1llllll11l11_opy_(bstack1llllllll1l1_opy_, bstack1111111l1ll_opy_)
      else:
        raise(bstack11ll1_opy_ (u"ࠨࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡧࡳࡼࡴ࡬ࡰࡣࡧࠤࡹ࡮ࡥࠡࡨ࡬ࡰࡪ࠴ࠠࡔࡶࡤࡸࡺࡹࠠࡤࡱࡧࡩ࠿ࠦࡻࡾࠤῌ").format(response.status_code))
    except Exception as e:
      self.logger.error(bstack11ll1_opy_ (u"ࠢࡖࡰࡤࡦࡱ࡫ࠠࡵࡱࠣࡨࡴࡽ࡮࡭ࡱࡤࡨࠥࡶࡥࡳࡥࡼࠤࡧ࡯࡮ࡢࡴࡼ࠾ࠥࢁࡽࠣ῍").format(e))
  def bstack1llllll11lll_opy_(self, bstack11111111l1l_opy_, bstack1111111l1ll_opy_):
    try:
      retry = 2
      bstack11111111111_opy_ = None
      bstack1lllllllll1l_opy_ = False
      while retry > 0:
        bstack11111111111_opy_ = self.bstack111111l111l_opy_(bstack11111111l1l_opy_, bstack1111111l1ll_opy_)
        bstack1lllllllll1l_opy_ = self.bstack1llllll1ll11_opy_(bstack11111111l1l_opy_, bstack1111111l1ll_opy_, bstack11111111111_opy_)
        if bstack1lllllllll1l_opy_:
          break
        retry -= 1
      return bstack11111111111_opy_, bstack1lllllllll1l_opy_
    except Exception as e:
      self.logger.error(bstack11ll1_opy_ (u"ࠣࡗࡱࡥࡧࡲࡥࠡࡶࡲࠤ࡬࡫ࡴࠡࡲࡨࡶࡨࡿࠠࡣ࡫ࡱࡥࡷࡿࠠࡱࡣࡷ࡬ࠧ῎").format(e))
    return bstack11111111111_opy_, False
  def bstack1llllll1ll11_opy_(self, bstack11111111l1l_opy_, bstack1111111l1ll_opy_, bstack11111111111_opy_, bstack1llllll1l1ll_opy_ = 0):
    if bstack1llllll1l1ll_opy_ > 1:
      return False
    if bstack11111111111_opy_ == None or os.path.exists(bstack11111111111_opy_) == False:
      self.logger.warn(bstack11ll1_opy_ (u"ࠤࡓࡩࡷࡩࡹࠡࡲࡤࡸ࡭ࠦ࡮ࡰࡶࠣࡪࡴࡻ࡮ࡥ࠮ࠣࡶࡪࡺࡲࡺ࡫ࡱ࡫ࠥࡪ࡯ࡸࡰ࡯ࡳࡦࡪࠢ῏"))
      return False
    bstack1llllll1l11l_opy_ = bstack11ll1_opy_ (u"ࡵࠦࡣ࠴ࠪࡁࡲࡨࡶࡨࡿ࠯ࡤ࡮࡬ࠤࡡࡪࠫ࡝࠰࡟ࡨ࠰ࡢ࠮࡝ࡦ࠮ࠦῐ")
    command = bstack11ll1_opy_ (u"ࠫࢀࢃࠠ࠮࠯ࡹࡩࡷࡹࡩࡰࡰࠪῑ").format(bstack11111111111_opy_)
    bstack111111l1ll1_opy_ = subprocess.check_output(command, shell=True, text=True)
    if re.match(bstack1llllll1l11l_opy_, bstack111111l1ll1_opy_) != None:
      return True
    else:
      self.logger.error(bstack11ll1_opy_ (u"ࠧࡖࡥࡳࡥࡼࠤࡻ࡫ࡲࡴ࡫ࡲࡲࠥࡩࡨࡦࡥ࡮ࠤ࡫ࡧࡩ࡭ࡧࡧࠦῒ"))
      return False
  def bstack1llllll11l11_opy_(self, bstack1llllllll1l1_opy_, bstack1111111l1ll_opy_):
    try:
      working_dir = os.path.dirname(bstack1llllllll1l1_opy_)
      shutil.unpack_archive(bstack1llllllll1l1_opy_, working_dir)
      bstack11111111111_opy_ = os.path.join(working_dir, bstack1111111l1ll_opy_)
      os.chmod(bstack11111111111_opy_, 0o755)
      return bstack11111111111_opy_
    except Exception as e:
      self.logger.error(bstack11ll1_opy_ (u"ࠨࡕ࡯ࡣࡥࡰࡪࠦࡴࡰࠢࡸࡲࡿ࡯ࡰࠡࡲࡨࡶࡨࡿࠠࡣ࡫ࡱࡥࡷࡿࠢΐ"))
  def bstack1llllll11ll1_opy_(self):
    try:
      bstack1lllllll1l1l_opy_ = self.config.get(bstack11ll1_opy_ (u"ࠧࡱࡧࡵࡧࡾ࠭῔"))
      bstack1llllll11ll1_opy_ = bstack1lllllll1l1l_opy_ or (bstack1lllllll1l1l_opy_ is None and self.bstack1l1lll1l_opy_)
      if not bstack1llllll11ll1_opy_ or self.config.get(bstack11ll1_opy_ (u"ࠨࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࠫ῕"), None) not in bstack11l1l11111l_opy_:
        return False
      self.bstack11111lll_opy_ = True
      return True
    except Exception as e:
      self.logger.error(bstack11ll1_opy_ (u"ࠤࡘࡲࡦࡨ࡬ࡦࠢࡷࡳࠥࡪࡥࡵࡧࡦࡸࠥࡶࡥࡳࡥࡼ࠰ࠥࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡࡽࢀࠦῖ").format(e))
  def bstack1lllllll111l_opy_(self):
    try:
      bstack1lllllll111l_opy_ = self.percy_capture_mode
      return bstack1lllllll111l_opy_
    except Exception as e:
      self.logger.error(bstack11ll1_opy_ (u"࡙ࠥࡳࡧࡢ࡭ࡧࠣࡸࡴࠦࡤࡦࡶࡨࡧࡹࠦࡰࡦࡴࡦࡽࠥࡩࡡࡱࡶࡸࡶࡪࠦ࡭ࡰࡦࡨ࠰ࠥࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡࡽࢀࠦῗ").format(e))
  def init(self, bstack1l1lll1l_opy_, config, logger):
    self.bstack1l1lll1l_opy_ = bstack1l1lll1l_opy_
    self.config = config
    self.logger = logger
    if not self.bstack1llllll11ll1_opy_():
      return
    self.bstack111111ll1l1_opy_ = config.get(bstack11ll1_opy_ (u"ࠫࡵ࡫ࡲࡤࡻࡒࡴࡹ࡯࡯࡯ࡵࠪῘ"), {})
    self.percy_capture_mode = config.get(bstack11ll1_opy_ (u"ࠬࡶࡥࡳࡥࡼࡇࡦࡶࡴࡶࡴࡨࡑࡴࡪࡥࠨῙ"))
    try:
      bstack11111111l1l_opy_, bstack1111111l1ll_opy_ = self.bstack1111111llll_opy_()
      self.bstack111ll1111ll_opy_ = bstack1111111l1ll_opy_
      bstack11111111111_opy_, bstack1lllllllll1l_opy_ = self.bstack1llllll11lll_opy_(bstack11111111l1l_opy_, bstack1111111l1ll_opy_)
      if bstack1lllllllll1l_opy_:
        self.binary_path = bstack11111111111_opy_
        thread = Thread(target=self.bstack1llllll1l1l1_opy_)
        thread.start()
      else:
        self.bstack111111l1111_opy_ = True
        self.logger.error(bstack11ll1_opy_ (u"ࠨࡉ࡯ࡸࡤࡰ࡮ࡪࠠࡱࡧࡵࡧࡾࠦࡰࡢࡶ࡫ࠤ࡫ࡵࡵ࡯ࡦࠣ࠱ࠥࢁࡽ࠭ࠢࡘࡲࡦࡨ࡬ࡦࠢࡷࡳࠥࡹࡴࡢࡴࡷࠤࡕ࡫ࡲࡤࡻࠥῚ").format(bstack11111111111_opy_))
    except Exception as e:
      self.logger.error(bstack11ll1_opy_ (u"ࠢࡖࡰࡤࡦࡱ࡫ࠠࡵࡱࠣࡷࡹࡧࡲࡵࠢࡳࡩࡷࡩࡹ࠭ࠢࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥࢁࡽࠣΊ").format(e))
  def bstack11111l11ll1_opy_(self):
    try:
      logfile = os.path.join(self.working_dir, bstack11ll1_opy_ (u"ࠨ࡮ࡲ࡫ࠬ῜"), bstack11ll1_opy_ (u"ࠩࡳࡩࡷࡩࡹ࠯࡮ࡲ࡫ࠬ῝"))
      os.makedirs(os.path.dirname(logfile)) if not os.path.exists(os.path.dirname(logfile)) else None
      self.logger.debug(bstack11ll1_opy_ (u"ࠥࡔࡺࡹࡨࡪࡰࡪࠤࡵ࡫ࡲࡤࡻࠣࡰࡴ࡭ࡳࠡࡣࡷࠤࢀࢃࠢ῞").format(logfile))
      self.bstack1111111ll1l_opy_ = logfile
    except Exception as e:
      self.logger.error(bstack11ll1_opy_ (u"࡚ࠦࡴࡡࡣ࡮ࡨࠤࡹࡵࠠࡴࡧࡷࠤࡵ࡫ࡲࡤࡻࠣࡰࡴ࡭ࠠࡱࡣࡷ࡬࠱ࠦࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢࡾࢁࠧ῟").format(e))
  @measure(event_name=EVENTS.bstack11l11ll1lll_opy_, stage=STAGE.bstack11l1llll1_opy_)
  def bstack1llllll1l1l1_opy_(self):
    bstack11111l1111l_opy_ = self.bstack1llllllll11l_opy_()
    if bstack11111l1111l_opy_ == None:
      self.bstack111111l1111_opy_ = True
      self.logger.error(bstack11ll1_opy_ (u"ࠧࡖࡥࡳࡥࡼࠤࡹࡵ࡫ࡦࡰࠣࡲࡴࡺࠠࡧࡱࡸࡲࡩ࠲ࠠࡇࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡷࡹࡧࡲࡵࠢࡳࡩࡷࡩࡹࠣῠ"))
      return False
    bstack1llllll1llll_opy_ = [bstack11ll1_opy_ (u"ࠨࡡࡱࡲ࠽ࡩࡽ࡫ࡣ࠻ࡵࡷࡥࡷࡺࠢῡ") if self.bstack1l1lll1l_opy_ else bstack11ll1_opy_ (u"ࠧࡦࡺࡨࡧ࠿ࡹࡴࡢࡴࡷࠫῢ")]
    bstack111l111l1l1_opy_ = self.bstack1lllllll1111_opy_()
    if bstack111l111l1l1_opy_ != None:
      bstack1llllll1llll_opy_.append(bstack11ll1_opy_ (u"ࠣ࠯ࡦࠤࢀࢃࠢΰ").format(bstack111l111l1l1_opy_))
    env = os.environ.copy()
    env[bstack11ll1_opy_ (u"ࠤࡓࡉࡗࡉ࡙ࡠࡖࡒࡏࡊࡔࠢῤ")] = bstack11111l1111l_opy_
    env[bstack11ll1_opy_ (u"ࠥࡘࡍࡥࡂࡖࡋࡏࡈࡤ࡛ࡕࡊࡆࠥῥ")] = os.environ.get(bstack11ll1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡉࡗࡅࡣ࡚࡛ࡉࡅࠩῦ"), bstack11ll1_opy_ (u"ࠬ࠭ῧ"))
    bstack1lllllllll11_opy_ = [self.binary_path]
    self.bstack11111l11ll1_opy_()
    self.bstack1llllll11l1l_opy_ = self.bstack11111l11111_opy_(bstack1lllllllll11_opy_ + bstack1llllll1llll_opy_, env)
    self.logger.debug(bstack11ll1_opy_ (u"ࠨࡓࡵࡣࡵࡸ࡮ࡴࡧࠡࡊࡨࡥࡱࡺࡨࠡࡅ࡫ࡩࡨࡱࠢῨ"))
    bstack1llllll1l1ll_opy_ = 0
    while self.bstack1llllll11l1l_opy_.poll() == None:
      bstack111111111l1_opy_ = self.bstack11111l111l1_opy_()
      if bstack111111111l1_opy_:
        self.logger.debug(bstack11ll1_opy_ (u"ࠢࡉࡧࡤࡰࡹ࡮ࠠࡄࡪࡨࡧࡰࠦࡳࡶࡥࡦࡩࡸࡹࡦࡶ࡮ࠥῩ"))
        self.bstack1llllllll1ll_opy_ = True
        return True
      bstack1llllll1l1ll_opy_ += 1
      self.logger.debug(bstack11ll1_opy_ (u"ࠣࡊࡨࡥࡱࡺࡨࠡࡅ࡫ࡩࡨࡱࠠࡓࡧࡷࡶࡾࠦ࠭ࠡࡽࢀࠦῪ").format(bstack1llllll1l1ll_opy_))
      time.sleep(2)
    self.logger.error(bstack11ll1_opy_ (u"ࠤࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥࡹࡴࡢࡴࡷࠤࡵ࡫ࡲࡤࡻ࠯ࠤࡍ࡫ࡡ࡭ࡶ࡫ࠤࡈ࡮ࡥࡤ࡭ࠣࡊࡦ࡯࡬ࡦࡦࠣࡥ࡫ࡺࡥࡳࠢࡾࢁࠥࡧࡴࡵࡧࡰࡴࡹࡹࠢΎ").format(bstack1llllll1l1ll_opy_))
    self.bstack111111l1111_opy_ = True
    return False
  def bstack11111l111l1_opy_(self, bstack1llllll1l1ll_opy_ = 0):
    if bstack1llllll1l1ll_opy_ > 10:
      return False
    try:
      bstack1111111l111_opy_ = os.environ.get(bstack11ll1_opy_ (u"ࠪࡔࡊࡘࡃ࡚ࡡࡖࡉࡗ࡜ࡅࡓࡡࡄࡈࡉࡘࡅࡔࡕࠪῬ"), bstack11ll1_opy_ (u"ࠫ࡭ࡺࡴࡱ࠼࠲࠳ࡱࡵࡣࡢ࡮࡫ࡳࡸࡺ࠺࠶࠵࠶࠼ࠬ῭"))
      bstack1llllllll111_opy_ = bstack1111111l111_opy_ + bstack11l1l11l1l1_opy_
      response = requests.get(bstack1llllllll111_opy_)
      data = response.json()
      self.percy_build_id = data.get(bstack11ll1_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࠫ΅"), {}).get(bstack11ll1_opy_ (u"࠭ࡩࡥࠩ`"), None)
      return True
    except:
      self.logger.debug(bstack11ll1_opy_ (u"ࠢࡆࡴࡵࡳࡷࠦ࡯ࡤࡥࡸࡶࡷ࡫ࡤࠡࡹ࡫࡭ࡱ࡫ࠠࡱࡴࡲࡧࡪࡹࡳࡪࡰࡪࠤ࡭࡫ࡡ࡭ࡶ࡫ࠤࡨ࡮ࡥࡤ࡭ࠣࡶࡪࡹࡰࡰࡰࡶࡩࠧ῰"))
      return False
  def bstack1llllllll11l_opy_(self):
    bstack1lllllll1lll_opy_ = bstack11ll1_opy_ (u"ࠨࡣࡳࡴࠬ῱") if self.bstack1l1lll1l_opy_ else bstack11ll1_opy_ (u"ࠩࡤࡹࡹࡵ࡭ࡢࡶࡨࠫῲ")
    bstack1lllllll1l11_opy_ = bstack11ll1_opy_ (u"ࠥࡹࡳࡪࡥࡧ࡫ࡱࡩࡩࠨῳ") if self.config.get(bstack11ll1_opy_ (u"ࠫࡵ࡫ࡲࡤࡻࠪῴ")) is None else True
    bstack11l1ll1ll1l_opy_ = bstack11ll1_opy_ (u"ࠧࡧࡰࡪ࠱ࡤࡴࡵࡥࡰࡦࡴࡦࡽ࠴࡭ࡥࡵࡡࡳࡶࡴࡰࡥࡤࡶࡢࡸࡴࡱࡥ࡯ࡁࡱࡥࡲ࡫࠽ࡼࡿࠩࡸࡾࡶࡥ࠾ࡽࢀࠪࡵ࡫ࡲࡤࡻࡀࡿࢂࠨ῵").format(self.config[bstack11ll1_opy_ (u"࠭ࡰࡳࡱ࡭ࡩࡨࡺࡎࡢ࡯ࡨࠫῶ")], bstack1lllllll1lll_opy_, bstack1lllllll1l11_opy_)
    if self.percy_capture_mode:
      bstack11l1ll1ll1l_opy_ += bstack11ll1_opy_ (u"ࠢࠧࡲࡨࡶࡨࡿ࡟ࡤࡣࡳࡸࡺࡸࡥࡠ࡯ࡲࡨࡪࡃࡻࡾࠤῷ").format(self.percy_capture_mode)
    uri = bstack1111l1lll_opy_(bstack11l1ll1ll1l_opy_)
    try:
      response = bstack11l1l1l11l_opy_(bstack11ll1_opy_ (u"ࠨࡉࡈࡘࠬῸ"), uri, {}, {bstack11ll1_opy_ (u"ࠩࡤࡹࡹ࡮ࠧΌ"): (self.config[bstack11ll1_opy_ (u"ࠪࡹࡸ࡫ࡲࡏࡣࡰࡩࠬῺ")], self.config[bstack11ll1_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶࡏࡪࡿࠧΏ")])})
      if response.status_code == 200:
        data = response.json()
        self.bstack11111lll_opy_ = data.get(bstack11ll1_opy_ (u"ࠬࡹࡵࡤࡥࡨࡷࡸ࠭ῼ"))
        self.percy_capture_mode = data.get(bstack11ll1_opy_ (u"࠭ࡰࡦࡴࡦࡽࡤࡩࡡࡱࡶࡸࡶࡪࡥ࡭ࡰࡦࡨࠫ´"))
        os.environ[bstack11ll1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡐࡆࡔࡆ࡝ࠬ῾")] = str(self.bstack11111lll_opy_)
        os.environ[bstack11ll1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡑࡇࡕࡇ࡞ࡥࡃࡂࡒࡗ࡙ࡗࡋ࡟ࡎࡑࡇࡉࠬ῿")] = str(self.percy_capture_mode)
        if bstack1lllllll1l11_opy_ == bstack11ll1_opy_ (u"ࠤࡸࡲࡩ࡫ࡦࡪࡰࡨࡨࠧ ") and str(self.bstack11111lll_opy_).lower() == bstack11ll1_opy_ (u"ࠥࡸࡷࡻࡥࠣ "):
          self.bstack1l1l1lll1_opy_ = True
        if bstack11ll1_opy_ (u"ࠦࡹࡵ࡫ࡦࡰࠥ ") in data:
          return data[bstack11ll1_opy_ (u"ࠧࡺ࡯࡬ࡧࡱࠦ ")]
        else:
          raise bstack11ll1_opy_ (u"࠭ࡔࡰ࡭ࡨࡲࠥࡔ࡯ࡵࠢࡉࡳࡺࡴࡤࠡ࠯ࠣࡿࢂ࠭ ").format(data)
      else:
        raise bstack11ll1_opy_ (u"ࠢࡇࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡪࡪࡺࡣࡩࠢࡳࡩࡷࡩࡹࠡࡶࡲ࡯ࡪࡴࠬࠡࡔࡨࡷࡵࡵ࡮ࡴࡧࠣࡷࡹࡧࡴࡶࡵࠣ࠱ࠥࢁࡽ࠭ࠢࡕࡩࡸࡶ࡯࡯ࡵࡨࠤࡇࡵࡤࡺࠢ࠰ࠤࢀࢃࠢ ").format(response.status_code, response.json())
    except Exception as e:
      self.logger.error(bstack11ll1_opy_ (u"ࠣࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡤࡴࡨࡥࡹ࡯࡮ࡨࠢࡳࡩࡷࡩࡹࠡࡲࡵࡳ࡯࡫ࡣࡵࠤ ").format(e))
  def bstack1lllllll1111_opy_(self):
    bstack1111111lll1_opy_ = os.path.join(tempfile.gettempdir(), bstack11ll1_opy_ (u"ࠤࡳࡩࡷࡩࡹࡄࡱࡱࡪ࡮࡭࠮࡫ࡵࡲࡲࠧ "))
    try:
      if bstack11ll1_opy_ (u"ࠪࡺࡪࡸࡳࡪࡱࡱࠫ ") not in self.bstack111111ll1l1_opy_:
        self.bstack111111ll1l1_opy_[bstack11ll1_opy_ (u"ࠫࡻ࡫ࡲࡴ࡫ࡲࡲࠬ ")] = 2
      with open(bstack1111111lll1_opy_, bstack11ll1_opy_ (u"ࠬࡽࠧ ")) as fp:
        json.dump(self.bstack111111ll1l1_opy_, fp)
      return bstack1111111lll1_opy_
    except Exception as e:
      self.logger.error(bstack11ll1_opy_ (u"ࠨࡕ࡯ࡣࡥࡰࡪࠦࡴࡰࠢࡦࡶࡪࡧࡴࡦࠢࡳࡩࡷࡩࡹࠡࡥࡲࡲ࡫࠲ࠠࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣࡿࢂࠨ​").format(e))
  def bstack11111l11111_opy_(self, cmd, env = os.environ.copy()):
    try:
      if self.bstack1111111l11l_opy_ == bstack11ll1_opy_ (u"ࠧࡸ࡫ࡱࠫ‌"):
        bstack1llllll1ll1l_opy_ = [bstack11ll1_opy_ (u"ࠨࡥࡰࡨ࠳࡫ࡸࡦࠩ‍"), bstack11ll1_opy_ (u"ࠩ࠲ࡧࠬ‎")]
        cmd = bstack1llllll1ll1l_opy_ + cmd
      cmd = bstack11ll1_opy_ (u"ࠪࠤࠬ‏").join(cmd)
      self.logger.debug(bstack11ll1_opy_ (u"ࠦࡗࡻ࡮࡯࡫ࡱ࡫ࠥࢁࡽࠣ‐").format(cmd))
      with open(self.bstack1111111ll1l_opy_, bstack11ll1_opy_ (u"ࠧࡧࠢ‑")) as bstack11111111ll1_opy_:
        process = subprocess.Popen(cmd, shell=True, stdout=bstack11111111ll1_opy_, text=True, stderr=bstack11111111ll1_opy_, env=env, universal_newlines=True)
      return process
    except Exception as e:
      self.bstack111111l1111_opy_ = True
      self.logger.error(bstack11ll1_opy_ (u"ࠨࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡶࡸࡦࡸࡴࠡࡲࡨࡶࡨࡿࠠࡸ࡫ࡷ࡬ࠥࡩ࡭ࡥࠢ࠰ࠤࢀࢃࠬࠡࡇࡻࡧࡪࡶࡴࡪࡱࡱ࠾ࠥࢁࡽࠣ‒").format(cmd, e))
  def shutdown(self):
    try:
      if self.bstack1llllllll1ll_opy_:
        self.logger.info(bstack11ll1_opy_ (u"ࠢࡔࡶࡲࡴࡵ࡯࡮ࡨࠢࡓࡩࡷࡩࡹࠣ–"))
        cmd = [self.binary_path, bstack11ll1_opy_ (u"ࠣࡧࡻࡩࡨࡀࡳࡵࡱࡳࠦ—")]
        self.bstack11111l11111_opy_(cmd)
        self.bstack1llllllll1ll_opy_ = False
    except Exception as e:
      self.logger.error(bstack11ll1_opy_ (u"ࠤࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥࡹࡴࡰࡲࠣࡷࡪࡹࡳࡪࡱࡱࠤࡼ࡯ࡴࡩࠢࡦࡳࡲࡳࡡ࡯ࡦࠣ࠱ࠥࢁࡽ࠭ࠢࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲ࠿ࠦࡻࡾࠤ―").format(cmd, e))
  def bstack11111l1l_opy_(self):
    if not self.bstack11111lll_opy_:
      return
    try:
      bstack111111lll1l_opy_ = 0
      while not self.bstack1llllllll1ll_opy_ and bstack111111lll1l_opy_ < self.bstack1lllllll1ll1_opy_:
        if self.bstack111111l1111_opy_:
          self.logger.info(bstack11ll1_opy_ (u"ࠥࡔࡪࡸࡣࡺࠢࡶࡩࡹࡻࡰࠡࡨࡤ࡭ࡱ࡫ࡤࠣ‖"))
          return
        time.sleep(1)
        bstack111111lll1l_opy_ += 1
      os.environ[bstack11ll1_opy_ (u"ࠫࡕࡋࡒࡄ࡛ࡢࡆࡊ࡙ࡔࡠࡒࡏࡅ࡙ࡌࡏࡓࡏࠪ‗")] = str(self.bstack111111l11l1_opy_())
      self.logger.info(bstack11ll1_opy_ (u"ࠧࡖࡥࡳࡥࡼࠤࡸ࡫ࡴࡶࡲࠣࡧࡴࡳࡰ࡭ࡧࡷࡩࡩࠨ‘"))
    except Exception as e:
      self.logger.error(bstack11ll1_opy_ (u"ࠨࡕ࡯ࡣࡥࡰࡪࠦࡴࡰࠢࡶࡩࡹࡻࡰࠡࡲࡨࡶࡨࡿࠬࠡࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤࢀࢃࠢ’").format(e))
  def bstack111111l11l1_opy_(self):
    if self.bstack1l1lll1l_opy_:
      return
    try:
      bstack1111111ll11_opy_ = [platform[bstack11ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡏࡣࡰࡩࠬ‚")].lower() for platform in self.config.get(bstack11ll1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫ‛"), [])]
      bstack11111l11l1l_opy_ = sys.maxsize
      bstack1lllllll11ll_opy_ = bstack11ll1_opy_ (u"ࠩࠪ“")
      for browser in bstack1111111ll11_opy_:
        if browser in self.bstack1lllllll11l1_opy_:
          bstack111111ll1ll_opy_ = self.bstack1lllllll11l1_opy_[browser]
        if bstack111111ll1ll_opy_ < bstack11111l11l1l_opy_:
          bstack11111l11l1l_opy_ = bstack111111ll1ll_opy_
          bstack1lllllll11ll_opy_ = browser
      return bstack1lllllll11ll_opy_
    except Exception as e:
      self.logger.error(bstack11ll1_opy_ (u"࡙ࠥࡳࡧࡢ࡭ࡧࠣࡸࡴࠦࡦࡪࡰࡧࠤࡧ࡫ࡳࡵࠢࡳࡰࡦࡺࡦࡰࡴࡰ࠰ࠥࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡࡽࢀࠦ”").format(e))
  @classmethod
  def bstack1lll1l11l1_opy_(self):
    return os.getenv(bstack11ll1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡔࡊࡘࡃ࡚ࠩ„"), bstack11ll1_opy_ (u"ࠬࡌࡡ࡭ࡵࡨࠫ‟")).lower()
  @classmethod
  def bstack11l11lll1_opy_(self):
    return os.getenv(bstack11ll1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡖࡅࡓࡅ࡜ࡣࡈࡇࡐࡕࡗࡕࡉࡤࡓࡏࡅࡇࠪ†"), bstack11ll1_opy_ (u"ࠧࠨ‡"))
  @classmethod
  def bstack11llll1ll1l_opy_(cls, value):
    cls.bstack1l1l1lll1_opy_ = value
  @classmethod
  def bstack111111l1lll_opy_(cls):
    return cls.bstack1l1l1lll1_opy_
  @classmethod
  def bstack11llll1lll1_opy_(cls, value):
    cls.percy_build_id = value
  @classmethod
  def bstack11111111lll_opy_(cls):
    return cls.percy_build_id