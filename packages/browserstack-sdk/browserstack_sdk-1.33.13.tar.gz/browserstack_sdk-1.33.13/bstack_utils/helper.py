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
import collections
import datetime
import json
import os
import platform
import re
import subprocess
import traceback
import tempfile
import multiprocessing
import threading
import sys
from math import ceil
from unittest import result
import urllib
from urllib.parse import urlparse
import zipfile
import git
import requests
from packaging import version
from bstack_utils.config import Config
from bstack_utils.constants import (bstack11lll111ll_opy_, bstack1lll11lll_opy_, bstack1ll111ll1l_opy_,
                                    bstack11l11ll1lll_opy_, bstack11l1l11ll11_opy_, bstack11l1l1111l1_opy_, bstack11l1l1111ll_opy_)
from bstack_utils.measure import measure
from bstack_utils.messages import bstack11l111ll1l_opy_, bstack1l1l11ll11_opy_
from bstack_utils.proxy import bstack1lllll111l_opy_, bstack1l1ll1l1ll_opy_
from bstack_utils.constants import *
from bstack_utils import bstack1l1lll1l11_opy_
from bstack_utils.bstack11llll11ll_opy_ import bstack1ll1l1l11_opy_
from browserstack_sdk._version import __version__
bstack1l1ll11111_opy_ = Config.bstack11l1l11ll1_opy_()
logger = bstack1l1lll1l11_opy_.get_logger(__name__, bstack1l1lll1l11_opy_.bstack1ll1lll1lll_opy_())
bstack1ll11l1ll_opy_ = bstack1l1lll1l11_opy_.bstack1l111111_opy_(__name__)
def bstack11ll111111l_opy_(config):
    return config[bstack11l1l_opy_ (u"ࠨࡷࡶࡩࡷࡔࡡ࡮ࡧࠪ᮴")]
def bstack11ll11ll1ll_opy_(config):
    return config[bstack11l1l_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴࡍࡨࡽࠬ᮵")]
def bstack1l11ll111_opy_():
    try:
        import playwright
        return True
    except ImportError:
        return False
def bstack111ll1lllll_opy_(obj):
    values = []
    bstack111l1llllll_opy_ = re.compile(bstack11l1l_opy_ (u"ࡵࠦࡣࡉࡕࡔࡖࡒࡑࡤ࡚ࡁࡈࡡ࡟ࡨ࠰ࠪࠢ᮶"), re.I)
    for key in obj.keys():
        if bstack111l1llllll_opy_.match(key):
            values.append(obj[key])
    return values
def bstack111ll11l11l_opy_(config):
    tags = []
    tags.extend(bstack111ll1lllll_opy_(os.environ))
    tags.extend(bstack111ll1lllll_opy_(config))
    return tags
def bstack111lll111ll_opy_(markers):
    tags = []
    for marker in markers:
        tags.append(marker.name)
    return tags
def bstack111ll1ll11l_opy_(bstack111l1l1l111_opy_):
    if not bstack111l1l1l111_opy_:
        return bstack11l1l_opy_ (u"ࠫࠬ᮷")
    return bstack11l1l_opy_ (u"ࠧࢁࡽࠡࠪࡾࢁ࠮ࠨ᮸").format(bstack111l1l1l111_opy_.name, bstack111l1l1l111_opy_.email)
def bstack11ll11l11l1_opy_():
    try:
        repo = git.Repo(search_parent_directories=True)
        bstack111l1l1llll_opy_ = repo.common_dir
        info = {
            bstack11l1l_opy_ (u"ࠨࡳࡩࡣࠥ᮹"): repo.head.commit.hexsha,
            bstack11l1l_opy_ (u"ࠢࡴࡪࡲࡶࡹࡥࡳࡩࡣࠥᮺ"): repo.git.rev_parse(repo.head.commit, short=True),
            bstack11l1l_opy_ (u"ࠣࡤࡵࡥࡳࡩࡨࠣᮻ"): repo.active_branch.name,
            bstack11l1l_opy_ (u"ࠤࡷࡥ࡬ࠨᮼ"): repo.git.describe(all=True, tags=True, exact_match=True),
            bstack11l1l_opy_ (u"ࠥࡧࡴࡳ࡭ࡪࡶࡷࡩࡷࠨᮽ"): bstack111ll1ll11l_opy_(repo.head.commit.committer),
            bstack11l1l_opy_ (u"ࠦࡨࡵ࡭࡮࡫ࡷࡸࡪࡸ࡟ࡥࡣࡷࡩࠧᮾ"): repo.head.commit.committed_datetime.isoformat(),
            bstack11l1l_opy_ (u"ࠧࡧࡵࡵࡪࡲࡶࠧᮿ"): bstack111ll1ll11l_opy_(repo.head.commit.author),
            bstack11l1l_opy_ (u"ࠨࡡࡶࡶ࡫ࡳࡷࡥࡤࡢࡶࡨࠦᯀ"): repo.head.commit.authored_datetime.isoformat(),
            bstack11l1l_opy_ (u"ࠢࡤࡱࡰࡱ࡮ࡺ࡟࡮ࡧࡶࡷࡦ࡭ࡥࠣᯁ"): repo.head.commit.message,
            bstack11l1l_opy_ (u"ࠣࡴࡲࡳࡹࠨᯂ"): repo.git.rev_parse(bstack11l1l_opy_ (u"ࠤ࠰࠱ࡸ࡮࡯ࡸ࠯ࡷࡳࡵࡲࡥࡷࡧ࡯ࠦᯃ")),
            bstack11l1l_opy_ (u"ࠥࡧࡴࡳ࡭ࡰࡰࡢ࡫࡮ࡺ࡟ࡥ࡫ࡵࠦᯄ"): bstack111l1l1llll_opy_,
            bstack11l1l_opy_ (u"ࠦࡼࡵࡲ࡬ࡶࡵࡩࡪࡥࡧࡪࡶࡢࡨ࡮ࡸࠢᯅ"): subprocess.check_output([bstack11l1l_opy_ (u"ࠧ࡭ࡩࡵࠤᯆ"), bstack11l1l_opy_ (u"ࠨࡲࡦࡸ࠰ࡴࡦࡸࡳࡦࠤᯇ"), bstack11l1l_opy_ (u"ࠢ࠮࠯ࡪ࡭ࡹ࠳ࡣࡰ࡯ࡰࡳࡳ࠳ࡤࡪࡴࠥᯈ")]).strip().decode(
                bstack11l1l_opy_ (u"ࠨࡷࡷࡪ࠲࠾ࠧᯉ")),
            bstack11l1l_opy_ (u"ࠤ࡯ࡥࡸࡺ࡟ࡵࡣࡪࠦᯊ"): repo.git.describe(tags=True, abbrev=0, always=True),
            bstack11l1l_opy_ (u"ࠥࡧࡴࡳ࡭ࡪࡶࡶࡣࡸ࡯࡮ࡤࡧࡢࡰࡦࡹࡴࡠࡶࡤ࡫ࠧᯋ"): repo.git.rev_list(
                bstack11l1l_opy_ (u"ࠦࢀࢃ࠮࠯ࡽࢀࠦᯌ").format(repo.head.commit, repo.git.describe(tags=True, abbrev=0, always=True)), count=True)
        }
        remotes = repo.remotes
        bstack111l1lll111_opy_ = []
        for remote in remotes:
            bstack11l111l1111_opy_ = {
                bstack11l1l_opy_ (u"ࠧࡴࡡ࡮ࡧࠥᯍ"): remote.name,
                bstack11l1l_opy_ (u"ࠨࡵࡳ࡮ࠥᯎ"): remote.url,
            }
            bstack111l1lll111_opy_.append(bstack11l111l1111_opy_)
        bstack11l1111ll11_opy_ = {
            bstack11l1l_opy_ (u"ࠢ࡯ࡣࡰࡩࠧᯏ"): bstack11l1l_opy_ (u"ࠣࡩ࡬ࡸࠧᯐ"),
            **info,
            bstack11l1l_opy_ (u"ࠤࡵࡩࡲࡵࡴࡦࡵࠥᯑ"): bstack111l1lll111_opy_
        }
        bstack11l1111ll11_opy_ = bstack11l1111l111_opy_(bstack11l1111ll11_opy_)
        return bstack11l1111ll11_opy_
    except git.InvalidGitRepositoryError:
        return {}
    except Exception as err:
        print(bstack11l1l_opy_ (u"ࠥࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡩ࡯ࠢࡳࡳࡵࡻ࡬ࡢࡶ࡬ࡲ࡬ࠦࡇࡪࡶࠣࡱࡪࡺࡡࡥࡣࡷࡥࠥࡽࡩࡵࡪࠣࡩࡷࡸ࡯ࡳ࠼ࠣࡿࢂࠨᯒ").format(err))
        return {}
def bstack111ll11l111_opy_(bstack11l111l1l11_opy_=None):
    bstack11l1l_opy_ (u"ࠦࠧࠨࠊࠡࠢࠣࠤࡌ࡫ࡴࠡࡩ࡬ࡸࠥࡳࡥࡵࡣࡧࡥࡹࡧࠠࡴࡲࡨࡧ࡮࡬ࡩࡤࡣ࡯ࡰࡾࠦࡦࡰࡴࡰࡥࡹࡺࡥࡥࠢࡩࡳࡷࠦࡁࡊࠢࡶࡩࡱ࡫ࡣࡵ࡫ࡲࡲࠥࡻࡳࡦࠢࡦࡥࡸ࡫ࡳࠡࡨࡲࡶࠥ࡫ࡡࡤࡪࠣࡪࡴࡲࡤࡦࡴࠣ࡭ࡳࠦࡴࡩࡧࠣࡰ࡮ࡹࡴ࠯ࠌࠣࠤࠥࠦࡁࡳࡩࡶ࠾ࠏࠦࠠࠡࠢࠣࠤࠥࠦࡦࡰ࡮ࡧࡩࡷࡹࠠࠩ࡮࡬ࡷࡹ࠲ࠠࡰࡲࡷ࡭ࡴࡴࡡ࡭ࠫ࠽ࠤࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣ࠱ࠥࡔ࡯࡯ࡧ࠽ࠤࡒࡵ࡮ࡰ࠯ࡵࡩࡵࡵࠠࡢࡲࡳࡶࡴࡧࡣࡩ࠮ࠣࡹࡸ࡫ࡳࠡࡥࡸࡶࡷ࡫࡮ࡵࠢࡧ࡭ࡷ࡫ࡣࡵࡱࡵࡽࠥࡡ࡯ࡴ࠰ࡪࡩࡹࡩࡷࡥࠪࠬࡡࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣ࠱ࠥࡋ࡭ࡱࡶࡼࠤࡱ࡯ࡳࡵࠢ࡞ࡡ࠿ࠦࡍࡶ࡮ࡷ࡭࠲ࡸࡥࡱࡱࠣࡥࡵࡶࡲࡰࡣࡦ࡬ࠥࡽࡩࡵࡪࠣࡲࡴࠦࡳࡰࡷࡵࡧࡪࡹࠠࡤࡱࡱࡪ࡮࡭ࡵࡳࡧࡧ࠰ࠥࡸࡥࡵࡷࡵࡲࡸ࡛ࠦ࡞ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠ࠮ࠢࡏ࡭ࡸࡺࠠࡰࡨࠣࡴࡦࡺࡨࡴ࠼ࠣࡑࡺࡲࡴࡪ࠯ࡵࡩࡵࡵࠠࡢࡲࡳࡶࡴࡧࡣࡩࠢࡺ࡭ࡹ࡮ࠠࡴࡲࡨࡧ࡮࡬ࡩࡤࠢࡩࡳࡱࡪࡥࡳࡵࠣࡸࡴࠦࡡ࡯ࡣ࡯ࡽࡿ࡫ࠊࠡࠢࠣࠤࡗ࡫ࡴࡶࡴࡱࡷ࠿ࠐࠠࠡࠢࠣࠤࠥࠦࠠ࡭࡫ࡶࡸ࠿ࠦࡌࡪࡵࡷࠤࡴ࡬ࠠࡥ࡫ࡦࡸࡸ࠲ࠠࡦࡣࡦ࡬ࠥࡩ࡯࡯ࡶࡤ࡭ࡳ࡯࡮ࡨࠢࡪ࡭ࡹࠦ࡭ࡦࡶࡤࡨࡦࡺࡡࠡࡨࡲࡶࠥࡧࠠࡧࡱ࡯ࡨࡪࡸ࠮ࠋࠢࠣࠤࠥࠨࠢࠣᯓ")
    if bstack11l111l1l11_opy_ is None:
        bstack11l111l1l11_opy_ = [os.getcwd()]
    elif isinstance(bstack11l111l1l11_opy_, list) and len(bstack11l111l1l11_opy_) == 0:
        return []
    results = []
    for folder in bstack11l111l1l11_opy_:
        try:
            if not os.path.exists(folder):
                raise Exception(bstack11l1l_opy_ (u"ࠧࡌ࡯࡭ࡦࡨࡶࠥࡪ࡯ࡦࡵࠣࡲࡴࡺࠠࡦࡺ࡬ࡷࡹࡀࠠࡼࡿࠥᯔ").format(folder))
            repo = git.Repo(folder, search_parent_directories=True)
            result = {
                bstack11l1l_opy_ (u"ࠨࡰࡳࡋࡧࠦᯕ"): bstack11l1l_opy_ (u"ࠢࠣᯖ"),
                bstack11l1l_opy_ (u"ࠣࡨ࡬ࡰࡪࡹࡃࡩࡣࡱ࡫ࡪࡪࠢᯗ"): [],
                bstack11l1l_opy_ (u"ࠤࡤࡹࡹ࡮࡯ࡳࡵࠥᯘ"): [],
                bstack11l1l_opy_ (u"ࠥࡴࡷࡊࡡࡵࡧࠥᯙ"): bstack11l1l_opy_ (u"ࠦࠧᯚ"),
                bstack11l1l_opy_ (u"ࠧࡩ࡯࡮࡯࡬ࡸࡒ࡫ࡳࡴࡣࡪࡩࡸࠨᯛ"): [],
                bstack11l1l_opy_ (u"ࠨࡰࡳࡖ࡬ࡸࡱ࡫ࠢᯜ"): bstack11l1l_opy_ (u"ࠢࠣᯝ"),
                bstack11l1l_opy_ (u"ࠣࡲࡵࡈࡪࡹࡣࡳ࡫ࡳࡸ࡮ࡵ࡮ࠣᯞ"): bstack11l1l_opy_ (u"ࠤࠥᯟ"),
                bstack11l1l_opy_ (u"ࠥࡴࡷࡘࡡࡸࡆ࡬ࡪ࡫ࠨᯠ"): bstack11l1l_opy_ (u"ࠦࠧᯡ")
            }
            bstack111lll11l11_opy_ = repo.active_branch.name
            bstack111ll1ll1l1_opy_ = repo.head.commit
            result[bstack11l1l_opy_ (u"ࠧࡶࡲࡊࡦࠥᯢ")] = bstack111ll1ll1l1_opy_.hexsha
            bstack111l1l11lll_opy_ = _11l11111ll1_opy_(repo)
            logger.debug(bstack11l1l_opy_ (u"ࠨࡂࡢࡵࡨࠤࡧࡸࡡ࡯ࡥ࡫ࠤ࡫ࡵࡲࠡࡥࡲࡱࡵࡧࡲࡪࡵࡲࡲ࠿ࠦࠢᯣ") + str(bstack111l1l11lll_opy_) + bstack11l1l_opy_ (u"ࠢࠣᯤ"))
            if bstack111l1l11lll_opy_:
                try:
                    bstack11l111l1lll_opy_ = repo.git.diff(bstack11l1l_opy_ (u"ࠣ࠯࠰ࡲࡦࡳࡥ࠮ࡱࡱࡰࡾࠨᯥ"), bstack1ll1l11l1ll_opy_ (u"ࠤࡾࡦࡦࡹࡥࡠࡤࡵࡥࡳࡩࡨࡾ࠰࠱࠲ࢀࡩࡵࡳࡴࡨࡲࡹࡥࡢࡳࡣࡱࡧ࡭ࢃ᯦ࠢ")).split(bstack11l1l_opy_ (u"ࠪࡠࡳ࠭ᯧ"))
                    logger.debug(bstack11l1l_opy_ (u"ࠦࡈ࡮ࡡ࡯ࡩࡨࡨࠥ࡬ࡩ࡭ࡧࡶࠤࡧ࡫ࡴࡸࡧࡨࡲࠥࢁࡢࡢࡵࡨࡣࡧࡸࡡ࡯ࡥ࡫ࢁࠥࡧ࡮ࡥࠢࡾࡧࡺࡸࡲࡦࡰࡷࡣࡧࡸࡡ࡯ࡥ࡫ࢁ࠿ࠦࠢᯨ") + str(bstack11l111l1lll_opy_) + bstack11l1l_opy_ (u"ࠧࠨᯩ"))
                    result[bstack11l1l_opy_ (u"ࠨࡦࡪ࡮ࡨࡷࡈ࡮ࡡ࡯ࡩࡨࡨࠧᯪ")] = [f.strip() for f in bstack11l111l1lll_opy_ if f.strip()]
                    commits = list(repo.iter_commits(bstack1ll1l11l1ll_opy_ (u"ࠢࡼࡤࡤࡷࡪࡥࡢࡳࡣࡱࡧ࡭ࢃ࠮࠯ࡽࡦࡹࡷࡸࡥ࡯ࡶࡢࡦࡷࡧ࡮ࡤࡪࢀࠦᯫ")))
                except Exception:
                    logger.debug(bstack11l1l_opy_ (u"ࠣࡈࡤ࡭ࡱ࡫ࡤࠡࡶࡲࠤ࡬࡫ࡴࠡࡥ࡫ࡥࡳ࡭ࡥࡥࠢࡩ࡭ࡱ࡫ࡳࠡࡨࡵࡳࡲࠦࡢࡳࡣࡱࡧ࡭ࠦࡣࡰ࡯ࡳࡥࡷ࡯ࡳࡰࡰ࠱ࠤࡋࡧ࡬࡭࡫ࡱ࡫ࠥࡨࡡࡤ࡭ࠣࡸࡴࠦࡲࡦࡥࡨࡲࡹࠦࡣࡰ࡯ࡰ࡭ࡹࡹ࠮ࠣᯬ"))
                    commits = list(repo.iter_commits(max_count=10))
                    if commits:
                        result[bstack11l1l_opy_ (u"ࠤࡩ࡭ࡱ࡫ࡳࡄࡪࡤࡲ࡬࡫ࡤࠣᯭ")] = _111llllll11_opy_(commits[:5])
            else:
                commits = list(repo.iter_commits(max_count=10))
                if commits:
                    result[bstack11l1l_opy_ (u"ࠥࡪ࡮ࡲࡥࡴࡅ࡫ࡥࡳ࡭ࡥࡥࠤᯮ")] = _111llllll11_opy_(commits[:5])
            bstack11l111l111l_opy_ = set()
            bstack111lll1l111_opy_ = []
            for commit in commits:
                logger.debug(bstack11l1l_opy_ (u"ࠦࡕࡸ࡯ࡤࡧࡶࡷ࡮ࡴࡧࠡࡥࡲࡱࡲ࡯ࡴ࠻ࠢࠥᯯ") + str(commit.message) + bstack11l1l_opy_ (u"ࠧࠨᯰ"))
                bstack11l111111l1_opy_ = commit.author.name if commit.author else bstack11l1l_opy_ (u"ࠨࡕ࡯࡭ࡱࡳࡼࡴࠢᯱ")
                bstack11l111l111l_opy_.add(bstack11l111111l1_opy_)
                bstack111lll1l111_opy_.append({
                    bstack11l1l_opy_ (u"ࠢ࡮ࡧࡶࡷࡦ࡭ࡥ᯲ࠣ"): commit.message.strip(),
                    bstack11l1l_opy_ (u"ࠣࡷࡶࡩࡷࠨ᯳"): bstack11l111111l1_opy_
                })
            result[bstack11l1l_opy_ (u"ࠤࡤࡹࡹ࡮࡯ࡳࡵࠥ᯴")] = list(bstack11l111l111l_opy_)
            result[bstack11l1l_opy_ (u"ࠥࡧࡴࡳ࡭ࡪࡶࡐࡩࡸࡹࡡࡨࡧࡶࠦ᯵")] = bstack111lll1l111_opy_
            result[bstack11l1l_opy_ (u"ࠦࡵࡸࡄࡢࡶࡨࠦ᯶")] = bstack111ll1ll1l1_opy_.committed_datetime.strftime(bstack11l1l_opy_ (u"࡙ࠧࠫ࠮ࠧࡰ࠱ࠪࡪࠢ᯷"))
            if (not result[bstack11l1l_opy_ (u"ࠨࡰࡳࡖ࡬ࡸࡱ࡫ࠢ᯸")] or result[bstack11l1l_opy_ (u"ࠢࡱࡴࡗ࡭ࡹࡲࡥࠣ᯹")].strip() == bstack11l1l_opy_ (u"ࠣࠤ᯺")) and bstack111ll1ll1l1_opy_.message:
                bstack111l1ll1l1l_opy_ = bstack111ll1ll1l1_opy_.message.strip().splitlines()
                result[bstack11l1l_opy_ (u"ࠤࡳࡶ࡙࡯ࡴ࡭ࡧࠥ᯻")] = bstack111l1ll1l1l_opy_[0] if bstack111l1ll1l1l_opy_ else bstack11l1l_opy_ (u"ࠥࠦ᯼")
                if len(bstack111l1ll1l1l_opy_) > 2:
                    result[bstack11l1l_opy_ (u"ࠦࡵࡸࡄࡦࡵࡦࡶ࡮ࡶࡴࡪࡱࡱࠦ᯽")] = bstack11l1l_opy_ (u"ࠬࡢ࡮ࠨ᯾").join(bstack111l1ll1l1l_opy_[2:]).strip()
            results.append(result)
        except Exception as err:
            logger.error(bstack11l1l_opy_ (u"ࠨࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢ࡬ࡲࠥࡶ࡯ࡱࡷ࡯ࡥࡹ࡯࡮ࡨࠢࡊ࡭ࡹࠦ࡭ࡦࡶࡤࡨࡦࡺࡡࠡࡨࡲࡶࠥࡇࡉࠡࡵࡨࡰࡪࡩࡴࡪࡱࡱࠤ࠭࡬࡯࡭ࡦࡨࡶ࠿ࠦࡻࡾࠫ࠽ࠤࢀࢃࠠ࠮ࠢࡾࢁࠧ᯿").format(
                folder,
                type(err).__name__,
                str(err)
            ))
    filtered_results = [
        result
        for result in results
        if _11l111l1ll1_opy_(result)
    ]
    return filtered_results
def _11l111l1ll1_opy_(result):
    bstack11l1l_opy_ (u"ࠢࠣࠤࠍࠤࠥࠦࠠࡉࡧ࡯ࡴࡪࡸࠠࡵࡱࠣࡧ࡭࡫ࡣ࡬ࠢ࡬ࡪࠥࡧࠠࡨ࡫ࡷࠤࡲ࡫ࡴࡢࡦࡤࡸࡦࠦࡲࡦࡵࡸࡰࡹࠦࡩࡴࠢࡹࡥࡱ࡯ࡤࠡࠪࡱࡳࡳ࠳ࡥ࡮ࡲࡷࡽࠥ࡬ࡩ࡭ࡧࡶࡇ࡭ࡧ࡮ࡨࡧࡧࠤࡦࡴࡤࠡࡣࡸࡸ࡭ࡵࡲࡴࠫ࠱ࠎࠥࠦࠠࠡࠤࠥࠦᰀ")
    return (
        isinstance(result.get(bstack11l1l_opy_ (u"ࠣࡨ࡬ࡰࡪࡹࡃࡩࡣࡱ࡫ࡪࡪࠢᰁ"), None), list)
        and len(result[bstack11l1l_opy_ (u"ࠤࡩ࡭ࡱ࡫ࡳࡄࡪࡤࡲ࡬࡫ࡤࠣᰂ")]) > 0
        and isinstance(result.get(bstack11l1l_opy_ (u"ࠥࡥࡺࡺࡨࡰࡴࡶࠦᰃ"), None), list)
        and len(result[bstack11l1l_opy_ (u"ࠦࡦࡻࡴࡩࡱࡵࡷࠧᰄ")]) > 0
    )
def _11l11111ll1_opy_(repo):
    bstack11l1l_opy_ (u"ࠧࠨࠢࠋࠢࠣࠤ࡚ࠥࡲࡺࠢࡷࡳࠥࡪࡥࡵࡧࡵࡱ࡮ࡴࡥࠡࡶ࡫ࡩࠥࡨࡡࡴࡧࠣࡦࡷࡧ࡮ࡤࡪࠣࡪࡴࡸࠠࡵࡪࡨࠤ࡬࡯ࡶࡦࡰࠣࡶࡪࡶ࡯ࠡࡹ࡬ࡸ࡭ࡵࡵࡵࠢ࡫ࡥࡷࡪࡣࡰࡦࡨࡨࠥࡴࡡ࡮ࡧࡶࠤࡦࡴࡤࠡࡹࡲࡶࡰࠦࡷࡪࡶ࡫ࠤࡦࡲ࡬ࠡࡘࡆࡗࠥࡶࡲࡰࡸ࡬ࡨࡪࡸࡳ࠯ࠌࠣࠤࠥࠦࡒࡦࡶࡸࡶࡳࡹࠠࡵࡪࡨࠤࡩ࡫ࡦࡢࡷ࡯ࡸࠥࡨࡲࡢࡰࡦ࡬ࠥ࡯ࡦࠡࡲࡲࡷࡸ࡯ࡢ࡭ࡧ࠯ࠤࡪࡲࡳࡦࠢࡑࡳࡳ࡫࠮ࠋࠢࠣࠤࠥࠨࠢࠣᰅ")
    try:
        try:
            origin = repo.remotes.origin
            bstack111l1ll1lll_opy_ = origin.refs[bstack11l1l_opy_ (u"࠭ࡈࡆࡃࡇࠫᰆ")]
            target = bstack111l1ll1lll_opy_.reference.name
            if target.startswith(bstack11l1l_opy_ (u"ࠧࡰࡴ࡬࡫࡮ࡴ࠯ࠨᰇ")):
                return target
        except Exception:
            pass
        if repo.remotes and repo.remotes.origin.refs:
            for ref in repo.remotes.origin.refs:
                if ref.name.startswith(bstack11l1l_opy_ (u"ࠨࡱࡵ࡭࡬࡯࡮࠰ࠩᰈ")):
                    return ref.name
        if repo.heads:
            return repo.heads[0].name
    except Exception:
        pass
    return None
def _111llllll11_opy_(commits):
    bstack11l1l_opy_ (u"ࠤࠥࠦࠏࠦࠠࠡࠢࡊࡩࡹࠦ࡬ࡪࡵࡷࠤࡴ࡬ࠠࡤࡪࡤࡲ࡬࡫ࡤࠡࡨ࡬ࡰࡪࡹࠠࡧࡴࡲࡱࠥࡧࠠ࡭࡫ࡶࡸࠥࡵࡦࠡࡥࡲࡱࡲ࡯ࡴࡴ࠰ࠍࠤࠥࠦࠠࠣࠤࠥᰉ")
    bstack11l111l1lll_opy_ = set()
    try:
        for commit in commits:
            if commit.parents:
                for parent in commit.parents:
                    diff = commit.diff(parent)
                    for bstack111ll11ll1l_opy_ in diff:
                        if bstack111ll11ll1l_opy_.a_path:
                            bstack11l111l1lll_opy_.add(bstack111ll11ll1l_opy_.a_path)
                        if bstack111ll11ll1l_opy_.b_path:
                            bstack11l111l1lll_opy_.add(bstack111ll11ll1l_opy_.b_path)
    except Exception:
        pass
    return list(bstack11l111l1lll_opy_)
def bstack11l1111l111_opy_(bstack11l1111ll11_opy_):
    bstack111ll11lll1_opy_ = bstack11l111ll11l_opy_(bstack11l1111ll11_opy_)
    if bstack111ll11lll1_opy_ and bstack111ll11lll1_opy_ > bstack11l11ll1lll_opy_:
        bstack111lll1111l_opy_ = bstack111ll11lll1_opy_ - bstack11l11ll1lll_opy_
        bstack111l1llll11_opy_ = bstack111lll11lll_opy_(bstack11l1111ll11_opy_[bstack11l1l_opy_ (u"ࠥࡧࡴࡳ࡭ࡪࡶࡢࡱࡪࡹࡳࡢࡩࡨࠦᰊ")], bstack111lll1111l_opy_)
        bstack11l1111ll11_opy_[bstack11l1l_opy_ (u"ࠦࡨࡵ࡭࡮࡫ࡷࡣࡲ࡫ࡳࡴࡣࡪࡩࠧᰋ")] = bstack111l1llll11_opy_
        logger.info(bstack11l1l_opy_ (u"࡚ࠧࡨࡦࠢࡦࡳࡲࡳࡩࡵࠢ࡫ࡥࡸࠦࡢࡦࡧࡱࠤࡹࡸࡵ࡯ࡥࡤࡸࡪࡪ࠮ࠡࡕ࡬ࡾࡪࠦ࡯ࡧࠢࡦࡳࡲࡳࡩࡵࠢࡤࡪࡹ࡫ࡲࠡࡶࡵࡹࡳࡩࡡࡵ࡫ࡲࡲࠥ࡯ࡳࠡࡽࢀࠤࡐࡈࠢᰌ")
                    .format(bstack11l111ll11l_opy_(bstack11l1111ll11_opy_) / 1024))
    return bstack11l1111ll11_opy_
def bstack11l111ll11l_opy_(bstack1llllll1ll_opy_):
    try:
        if bstack1llllll1ll_opy_:
            bstack111lllll111_opy_ = json.dumps(bstack1llllll1ll_opy_)
            bstack111lll1l1ll_opy_ = sys.getsizeof(bstack111lllll111_opy_)
            return bstack111lll1l1ll_opy_
    except Exception as e:
        logger.debug(bstack11l1l_opy_ (u"ࠨࡓࡰ࡯ࡨࡸ࡭࡯࡮ࡨࠢࡺࡩࡳࡺࠠࡸࡴࡲࡲ࡬ࠦࡷࡩ࡫࡯ࡩࠥࡩࡡ࡭ࡥࡸࡰࡦࡺࡩ࡯ࡩࠣࡷ࡮ࢀࡥࠡࡱࡩࠤࡏ࡙ࡏࡏࠢࡲࡦ࡯࡫ࡣࡵ࠼ࠣࡿࢂࠨᰍ").format(e))
    return -1
def bstack111lll11lll_opy_(field, bstack111ll1111l1_opy_):
    try:
        bstack111ll1111ll_opy_ = len(bytes(bstack11l1l11ll11_opy_, bstack11l1l_opy_ (u"ࠧࡶࡶࡩ࠱࠽࠭ᰎ")))
        bstack111llll1l11_opy_ = bytes(field, bstack11l1l_opy_ (u"ࠨࡷࡷࡪ࠲࠾ࠧᰏ"))
        bstack111ll111ll1_opy_ = len(bstack111llll1l11_opy_)
        bstack111l1l11ll1_opy_ = ceil(bstack111ll111ll1_opy_ - bstack111ll1111l1_opy_ - bstack111ll1111ll_opy_)
        if bstack111l1l11ll1_opy_ > 0:
            bstack111l1l111ll_opy_ = bstack111llll1l11_opy_[:bstack111l1l11ll1_opy_].decode(bstack11l1l_opy_ (u"ࠩࡸࡸ࡫࠳࠸ࠨᰐ"), errors=bstack11l1l_opy_ (u"ࠪ࡭࡬ࡴ࡯ࡳࡧࠪᰑ")) + bstack11l1l11ll11_opy_
            return bstack111l1l111ll_opy_
    except Exception as e:
        logger.debug(bstack11l1l_opy_ (u"ࠦࡊࡸࡲࡰࡴࠣࡻ࡭࡯࡬ࡦࠢࡷࡶࡺࡴࡣࡢࡶ࡬ࡲ࡬ࠦࡦࡪࡧ࡯ࡨ࠱ࠦ࡮ࡰࡶ࡫࡭ࡳ࡭ࠠࡸࡣࡶࠤࡹࡸࡵ࡯ࡥࡤࡸࡪࡪࠠࡩࡧࡵࡩ࠿ࠦࡻࡾࠤᰒ").format(e))
    return field
def bstack1l111l11l1_opy_():
    env = os.environ
    if (bstack11l1l_opy_ (u"ࠧࡐࡅࡏࡍࡌࡒࡘࡥࡕࡓࡎࠥᰓ") in env and len(env[bstack11l1l_opy_ (u"ࠨࡊࡆࡐࡎࡍࡓ࡙࡟ࡖࡔࡏࠦᰔ")]) > 0) or (
            bstack11l1l_opy_ (u"ࠢࡋࡇࡑࡏࡎࡔࡓࡠࡊࡒࡑࡊࠨᰕ") in env and len(env[bstack11l1l_opy_ (u"ࠣࡌࡈࡒࡐࡏࡎࡔࡡࡋࡓࡒࡋࠢᰖ")]) > 0):
        return {
            bstack11l1l_opy_ (u"ࠤࡱࡥࡲ࡫ࠢᰗ"): bstack11l1l_opy_ (u"ࠥࡎࡪࡴ࡫ࡪࡰࡶࠦᰘ"),
            bstack11l1l_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡹࡷࡲࠢᰙ"): env.get(bstack11l1l_opy_ (u"ࠧࡈࡕࡊࡎࡇࡣ࡚ࡘࡌࠣᰚ")),
            bstack11l1l_opy_ (u"ࠨࡪࡰࡤࡢࡲࡦࡳࡥࠣᰛ"): env.get(bstack11l1l_opy_ (u"ࠢࡋࡑࡅࡣࡓࡇࡍࡆࠤᰜ")),
            bstack11l1l_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟࡯ࡷࡰࡦࡪࡸࠢᰝ"): env.get(bstack11l1l_opy_ (u"ࠤࡅ࡙ࡎࡒࡄࡠࡐࡘࡑࡇࡋࡒࠣᰞ"))
        }
    if env.get(bstack11l1l_opy_ (u"ࠥࡇࡎࠨᰟ")) == bstack11l1l_opy_ (u"ࠦࡹࡸࡵࡦࠤᰠ") and bstack1llll1ll1_opy_(env.get(bstack11l1l_opy_ (u"ࠧࡉࡉࡓࡅࡏࡉࡈࡏࠢᰡ"))):
        return {
            bstack11l1l_opy_ (u"ࠨ࡮ࡢ࡯ࡨࠦᰢ"): bstack11l1l_opy_ (u"ࠢࡄ࡫ࡵࡧࡱ࡫ࡃࡊࠤᰣ"),
            bstack11l1l_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟ࡶࡴ࡯ࠦᰤ"): env.get(bstack11l1l_opy_ (u"ࠤࡆࡍࡗࡉࡌࡆࡡࡅ࡙ࡎࡒࡄࡠࡗࡕࡐࠧᰥ")),
            bstack11l1l_opy_ (u"ࠥ࡮ࡴࡨ࡟࡯ࡣࡰࡩࠧᰦ"): env.get(bstack11l1l_opy_ (u"ࠦࡈࡏࡒࡄࡎࡈࡣࡏࡕࡂࠣᰧ")),
            bstack11l1l_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡳࡻ࡭ࡣࡧࡵࠦᰨ"): env.get(bstack11l1l_opy_ (u"ࠨࡃࡊࡔࡆࡐࡊࡥࡂࡖࡋࡏࡈࡤࡔࡕࡎࠤᰩ"))
        }
    if env.get(bstack11l1l_opy_ (u"ࠢࡄࡋࠥᰪ")) == bstack11l1l_opy_ (u"ࠣࡶࡵࡹࡪࠨᰫ") and bstack1llll1ll1_opy_(env.get(bstack11l1l_opy_ (u"ࠤࡗࡖࡆ࡜ࡉࡔࠤᰬ"))):
        return {
            bstack11l1l_opy_ (u"ࠥࡲࡦࡳࡥࠣᰭ"): bstack11l1l_opy_ (u"࡙ࠦࡸࡡࡷ࡫ࡶࠤࡈࡏࠢᰮ"),
            bstack11l1l_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡺࡸ࡬ࠣᰯ"): env.get(bstack11l1l_opy_ (u"ࠨࡔࡓࡃ࡙ࡍࡘࡥࡂࡖࡋࡏࡈࡤ࡝ࡅࡃࡡࡘࡖࡑࠨᰰ")),
            bstack11l1l_opy_ (u"ࠢ࡫ࡱࡥࡣࡳࡧ࡭ࡦࠤᰱ"): env.get(bstack11l1l_opy_ (u"ࠣࡖࡕࡅ࡛ࡏࡓࡠࡌࡒࡆࡤࡔࡁࡎࡇࠥᰲ")),
            bstack11l1l_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡰࡸࡱࡧ࡫ࡲࠣᰳ"): env.get(bstack11l1l_opy_ (u"ࠥࡘࡗࡇࡖࡊࡕࡢࡆ࡚ࡏࡌࡅࡡࡑ࡙ࡒࡈࡅࡓࠤᰴ"))
        }
    if env.get(bstack11l1l_opy_ (u"ࠦࡈࡏࠢᰵ")) == bstack11l1l_opy_ (u"ࠧࡺࡲࡶࡧࠥᰶ") and env.get(bstack11l1l_opy_ (u"ࠨࡃࡊࡡࡑࡅࡒࡋ᰷ࠢ")) == bstack11l1l_opy_ (u"ࠢࡤࡱࡧࡩࡸ࡮ࡩࡱࠤ᰸"):
        return {
            bstack11l1l_opy_ (u"ࠣࡰࡤࡱࡪࠨ᰹"): bstack11l1l_opy_ (u"ࠤࡆࡳࡩ࡫ࡳࡩ࡫ࡳࠦ᰺"),
            bstack11l1l_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡸࡶࡱࠨ᰻"): None,
            bstack11l1l_opy_ (u"ࠦ࡯ࡵࡢࡠࡰࡤࡱࡪࠨ᰼"): None,
            bstack11l1l_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡳࡻ࡭ࡣࡧࡵࠦ᰽"): None
        }
    if env.get(bstack11l1l_opy_ (u"ࠨࡂࡊࡖࡅ࡙ࡈࡑࡅࡕࡡࡅࡖࡆࡔࡃࡉࠤ᰾")) and env.get(bstack11l1l_opy_ (u"ࠢࡃࡋࡗࡆ࡚ࡉࡋࡆࡖࡢࡇࡔࡓࡍࡊࡖࠥ᰿")):
        return {
            bstack11l1l_opy_ (u"ࠣࡰࡤࡱࡪࠨ᱀"): bstack11l1l_opy_ (u"ࠤࡅ࡭ࡹࡨࡵࡤ࡭ࡨࡸࠧ᱁"),
            bstack11l1l_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡸࡶࡱࠨ᱂"): env.get(bstack11l1l_opy_ (u"ࠦࡇࡏࡔࡃࡗࡆࡏࡊ࡚࡟ࡈࡋࡗࡣࡍ࡚ࡔࡑࡡࡒࡖࡎࡍࡉࡏࠤ᱃")),
            bstack11l1l_opy_ (u"ࠧࡰ࡯ࡣࡡࡱࡥࡲ࡫ࠢ᱄"): None,
            bstack11l1l_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡴࡵ࡮ࡤࡨࡶࠧ᱅"): env.get(bstack11l1l_opy_ (u"ࠢࡃࡋࡗࡆ࡚ࡉࡋࡆࡖࡢࡆ࡚ࡏࡌࡅࡡࡑ࡙ࡒࡈࡅࡓࠤ᱆"))
        }
    if env.get(bstack11l1l_opy_ (u"ࠣࡅࡌࠦ᱇")) == bstack11l1l_opy_ (u"ࠤࡷࡶࡺ࡫ࠢ᱈") and bstack1llll1ll1_opy_(env.get(bstack11l1l_opy_ (u"ࠥࡈࡗࡕࡎࡆࠤ᱉"))):
        return {
            bstack11l1l_opy_ (u"ࠦࡳࡧ࡭ࡦࠤ᱊"): bstack11l1l_opy_ (u"ࠧࡊࡲࡰࡰࡨࠦ᱋"),
            bstack11l1l_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡻࡲ࡭ࠤ᱌"): env.get(bstack11l1l_opy_ (u"ࠢࡅࡔࡒࡒࡊࡥࡂࡖࡋࡏࡈࡤࡒࡉࡏࡍࠥᱍ")),
            bstack11l1l_opy_ (u"ࠣ࡬ࡲࡦࡤࡴࡡ࡮ࡧࠥᱎ"): None,
            bstack11l1l_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡰࡸࡱࡧ࡫ࡲࠣᱏ"): env.get(bstack11l1l_opy_ (u"ࠥࡈࡗࡕࡎࡆࡡࡅ࡙ࡎࡒࡄࡠࡐࡘࡑࡇࡋࡒࠣ᱐"))
        }
    if env.get(bstack11l1l_opy_ (u"ࠦࡈࡏࠢ᱑")) == bstack11l1l_opy_ (u"ࠧࡺࡲࡶࡧࠥ᱒") and bstack1llll1ll1_opy_(env.get(bstack11l1l_opy_ (u"ࠨࡓࡆࡏࡄࡔࡍࡕࡒࡆࠤ᱓"))):
        return {
            bstack11l1l_opy_ (u"ࠢ࡯ࡣࡰࡩࠧ᱔"): bstack11l1l_opy_ (u"ࠣࡕࡨࡱࡦࡶࡨࡰࡴࡨࠦ᱕"),
            bstack11l1l_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡷࡵࡰࠧ᱖"): env.get(bstack11l1l_opy_ (u"ࠥࡗࡊࡓࡁࡑࡊࡒࡖࡊࡥࡏࡓࡉࡄࡒࡎࡠࡁࡕࡋࡒࡒࡤ࡛ࡒࡍࠤ᱗")),
            bstack11l1l_opy_ (u"ࠦ࡯ࡵࡢࡠࡰࡤࡱࡪࠨ᱘"): env.get(bstack11l1l_opy_ (u"࡙ࠧࡅࡎࡃࡓࡌࡔࡘࡅࡠࡌࡒࡆࡤࡔࡁࡎࡇࠥ᱙")),
            bstack11l1l_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡴࡵ࡮ࡤࡨࡶࠧᱚ"): env.get(bstack11l1l_opy_ (u"ࠢࡔࡇࡐࡅࡕࡎࡏࡓࡇࡢࡎࡔࡈ࡟ࡊࡆࠥᱛ"))
        }
    if env.get(bstack11l1l_opy_ (u"ࠣࡅࡌࠦᱜ")) == bstack11l1l_opy_ (u"ࠤࡷࡶࡺ࡫ࠢᱝ") and bstack1llll1ll1_opy_(env.get(bstack11l1l_opy_ (u"ࠥࡋࡎ࡚ࡌࡂࡄࡢࡇࡎࠨᱞ"))):
        return {
            bstack11l1l_opy_ (u"ࠦࡳࡧ࡭ࡦࠤᱟ"): bstack11l1l_opy_ (u"ࠧࡍࡩࡵࡎࡤࡦࠧᱠ"),
            bstack11l1l_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡻࡲ࡭ࠤᱡ"): env.get(bstack11l1l_opy_ (u"ࠢࡄࡋࡢࡎࡔࡈ࡟ࡖࡔࡏࠦᱢ")),
            bstack11l1l_opy_ (u"ࠣ࡬ࡲࡦࡤࡴࡡ࡮ࡧࠥᱣ"): env.get(bstack11l1l_opy_ (u"ࠤࡆࡍࡤࡐࡏࡃࡡࡑࡅࡒࡋࠢᱤ")),
            bstack11l1l_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡱࡹࡲࡨࡥࡳࠤᱥ"): env.get(bstack11l1l_opy_ (u"ࠦࡈࡏ࡟ࡋࡑࡅࡣࡎࡊࠢᱦ"))
        }
    if env.get(bstack11l1l_opy_ (u"ࠧࡉࡉࠣᱧ")) == bstack11l1l_opy_ (u"ࠨࡴࡳࡷࡨࠦᱨ") and bstack1llll1ll1_opy_(env.get(bstack11l1l_opy_ (u"ࠢࡃࡗࡌࡐࡉࡑࡉࡕࡇࠥᱩ"))):
        return {
            bstack11l1l_opy_ (u"ࠣࡰࡤࡱࡪࠨᱪ"): bstack11l1l_opy_ (u"ࠤࡅࡹ࡮ࡲࡤ࡬࡫ࡷࡩࠧᱫ"),
            bstack11l1l_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡸࡶࡱࠨᱬ"): env.get(bstack11l1l_opy_ (u"ࠦࡇ࡛ࡉࡍࡆࡎࡍ࡙ࡋ࡟ࡃࡗࡌࡐࡉࡥࡕࡓࡎࠥᱭ")),
            bstack11l1l_opy_ (u"ࠧࡰ࡯ࡣࡡࡱࡥࡲ࡫ࠢᱮ"): env.get(bstack11l1l_opy_ (u"ࠨࡂࡖࡋࡏࡈࡐࡏࡔࡆࡡࡏࡅࡇࡋࡌࠣᱯ")) or env.get(bstack11l1l_opy_ (u"ࠢࡃࡗࡌࡐࡉࡑࡉࡕࡇࡢࡔࡎࡖࡅࡍࡋࡑࡉࡤࡔࡁࡎࡇࠥᱰ")),
            bstack11l1l_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟࡯ࡷࡰࡦࡪࡸࠢᱱ"): env.get(bstack11l1l_opy_ (u"ࠤࡅ࡙ࡎࡒࡄࡌࡋࡗࡉࡤࡈࡕࡊࡎࡇࡣࡓ࡛ࡍࡃࡇࡕࠦᱲ"))
        }
    if bstack1llll1ll1_opy_(env.get(bstack11l1l_opy_ (u"ࠥࡘࡋࡥࡂࡖࡋࡏࡈࠧᱳ"))):
        return {
            bstack11l1l_opy_ (u"ࠦࡳࡧ࡭ࡦࠤᱴ"): bstack11l1l_opy_ (u"ࠧ࡜ࡩࡴࡷࡤࡰ࡙ࠥࡴࡶࡦ࡬ࡳ࡚ࠥࡥࡢ࡯ࠣࡗࡪࡸࡶࡪࡥࡨࡷࠧᱵ"),
            bstack11l1l_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡻࡲ࡭ࠤᱶ"): bstack11l1l_opy_ (u"ࠢࡼࡿࡾࢁࠧᱷ").format(env.get(bstack11l1l_opy_ (u"ࠨࡕ࡜ࡗ࡙ࡋࡍࡠࡖࡈࡅࡒࡌࡏࡖࡐࡇࡅ࡙ࡏࡏࡏࡕࡈࡖ࡛ࡋࡒࡖࡔࡌࠫᱸ")), env.get(bstack11l1l_opy_ (u"ࠩࡖ࡝ࡘ࡚ࡅࡎࡡࡗࡉࡆࡓࡐࡓࡑࡍࡉࡈ࡚ࡉࡅࠩᱹ"))),
            bstack11l1l_opy_ (u"ࠥ࡮ࡴࡨ࡟࡯ࡣࡰࡩࠧᱺ"): env.get(bstack11l1l_opy_ (u"ࠦࡘ࡟ࡓࡕࡇࡐࡣࡉࡋࡆࡊࡐࡌࡘࡎࡕࡎࡊࡆࠥᱻ")),
            bstack11l1l_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡳࡻ࡭ࡣࡧࡵࠦᱼ"): env.get(bstack11l1l_opy_ (u"ࠨࡂࡖࡋࡏࡈࡤࡈࡕࡊࡎࡇࡍࡉࠨᱽ"))
        }
    if bstack1llll1ll1_opy_(env.get(bstack11l1l_opy_ (u"ࠢࡂࡒࡓ࡚ࡊ࡟ࡏࡓࠤ᱾"))):
        return {
            bstack11l1l_opy_ (u"ࠣࡰࡤࡱࡪࠨ᱿"): bstack11l1l_opy_ (u"ࠤࡄࡴࡵࡼࡥࡺࡱࡵࠦᲀ"),
            bstack11l1l_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡸࡶࡱࠨᲁ"): bstack11l1l_opy_ (u"ࠦࢀࢃ࠯ࡱࡴࡲ࡮ࡪࡩࡴ࠰ࡽࢀ࠳ࢀࢃ࠯ࡣࡷ࡬ࡰࡩࡹ࠯ࡼࡿࠥᲂ").format(env.get(bstack11l1l_opy_ (u"ࠬࡇࡐࡑࡘࡈ࡝ࡔࡘ࡟ࡖࡔࡏࠫᲃ")), env.get(bstack11l1l_opy_ (u"࠭ࡁࡑࡒ࡙ࡉ࡞ࡕࡒࡠࡃࡆࡇࡔ࡛ࡎࡕࡡࡑࡅࡒࡋࠧᲄ")), env.get(bstack11l1l_opy_ (u"ࠧࡂࡒࡓ࡚ࡊ࡟ࡏࡓࡡࡓࡖࡔࡐࡅࡄࡖࡢࡗࡑ࡛ࡇࠨᲅ")), env.get(bstack11l1l_opy_ (u"ࠨࡃࡓࡔ࡛ࡋ࡙ࡐࡔࡢࡆ࡚ࡏࡌࡅࡡࡌࡈࠬᲆ"))),
            bstack11l1l_opy_ (u"ࠤ࡭ࡳࡧࡥ࡮ࡢ࡯ࡨࠦᲇ"): env.get(bstack11l1l_opy_ (u"ࠥࡅࡕࡖࡖࡆ࡛ࡒࡖࡤࡐࡏࡃࡡࡑࡅࡒࡋࠢᲈ")),
            bstack11l1l_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡲࡺࡳࡢࡦࡴࠥᲉ"): env.get(bstack11l1l_opy_ (u"ࠧࡇࡐࡑࡘࡈ࡝ࡔࡘ࡟ࡃࡗࡌࡐࡉࡥࡎࡖࡏࡅࡉࡗࠨᲊ"))
        }
    if env.get(bstack11l1l_opy_ (u"ࠨࡁ࡛ࡗࡕࡉࡤࡎࡔࡕࡒࡢ࡙ࡘࡋࡒࡠࡃࡊࡉࡓ࡚ࠢ᲋")) and env.get(bstack11l1l_opy_ (u"ࠢࡕࡈࡢࡆ࡚ࡏࡌࡅࠤ᲌")):
        return {
            bstack11l1l_opy_ (u"ࠣࡰࡤࡱࡪࠨ᲍"): bstack11l1l_opy_ (u"ࠤࡄࡾࡺࡸࡥࠡࡅࡌࠦ᲎"),
            bstack11l1l_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡸࡶࡱࠨ᲏"): bstack11l1l_opy_ (u"ࠦࢀࢃࡻࡾ࠱ࡢࡦࡺ࡯࡬ࡥ࠱ࡵࡩࡸࡻ࡬ࡵࡵࡂࡦࡺ࡯࡬ࡥࡋࡧࡁࢀࢃࠢᲐ").format(env.get(bstack11l1l_opy_ (u"࡙࡙ࠬࡔࡖࡈࡑࡤ࡚ࡅࡂࡏࡉࡓ࡚ࡔࡄࡂࡖࡌࡓࡓ࡙ࡅࡓࡘࡈࡖ࡚ࡘࡉࠨᲑ")), env.get(bstack11l1l_opy_ (u"࠭ࡓ࡚ࡕࡗࡉࡒࡥࡔࡆࡃࡐࡔࡗࡕࡊࡆࡅࡗࠫᲒ")), env.get(bstack11l1l_opy_ (u"ࠧࡃࡗࡌࡐࡉࡥࡂࡖࡋࡏࡈࡎࡊࠧᲓ"))),
            bstack11l1l_opy_ (u"ࠣ࡬ࡲࡦࡤࡴࡡ࡮ࡧࠥᲔ"): env.get(bstack11l1l_opy_ (u"ࠤࡅ࡙ࡎࡒࡄࡠࡄࡘࡍࡑࡊࡉࡅࠤᲕ")),
            bstack11l1l_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡱࡹࡲࡨࡥࡳࠤᲖ"): env.get(bstack11l1l_opy_ (u"ࠦࡇ࡛ࡉࡍࡆࡢࡆ࡚ࡏࡌࡅࡋࡇࠦᲗ"))
        }
    if any([env.get(bstack11l1l_opy_ (u"ࠧࡉࡏࡅࡇࡅ࡙ࡎࡒࡄࡠࡄࡘࡍࡑࡊ࡟ࡊࡆࠥᲘ")), env.get(bstack11l1l_opy_ (u"ࠨࡃࡐࡆࡈࡆ࡚ࡏࡌࡅࡡࡕࡉࡘࡕࡌࡗࡇࡇࡣࡘࡕࡕࡓࡅࡈࡣ࡛ࡋࡒࡔࡋࡒࡒࠧᲙ")), env.get(bstack11l1l_opy_ (u"ࠢࡄࡑࡇࡉࡇ࡛ࡉࡍࡆࡢࡗࡔ࡛ࡒࡄࡇࡢ࡚ࡊࡘࡓࡊࡑࡑࠦᲚ"))]):
        return {
            bstack11l1l_opy_ (u"ࠣࡰࡤࡱࡪࠨᲛ"): bstack11l1l_opy_ (u"ࠤࡄ࡛ࡘࠦࡃࡰࡦࡨࡆࡺ࡯࡬ࡥࠤᲜ"),
            bstack11l1l_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡸࡶࡱࠨᲝ"): env.get(bstack11l1l_opy_ (u"ࠦࡈࡕࡄࡆࡄࡘࡍࡑࡊ࡟ࡑࡗࡅࡐࡎࡉ࡟ࡃࡗࡌࡐࡉࡥࡕࡓࡎࠥᲞ")),
            bstack11l1l_opy_ (u"ࠧࡰ࡯ࡣࡡࡱࡥࡲ࡫ࠢᲟ"): env.get(bstack11l1l_opy_ (u"ࠨࡃࡐࡆࡈࡆ࡚ࡏࡌࡅࡡࡅ࡙ࡎࡒࡄࡠࡋࡇࠦᲠ")),
            bstack11l1l_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥ࡮ࡶ࡯ࡥࡩࡷࠨᲡ"): env.get(bstack11l1l_opy_ (u"ࠣࡅࡒࡈࡊࡈࡕࡊࡎࡇࡣࡇ࡛ࡉࡍࡆࡢࡍࡉࠨᲢ"))
        }
    if env.get(bstack11l1l_opy_ (u"ࠤࡥࡥࡲࡨ࡯ࡰࡡࡥࡹ࡮ࡲࡤࡏࡷࡰࡦࡪࡸࠢᲣ")):
        return {
            bstack11l1l_opy_ (u"ࠥࡲࡦࡳࡥࠣᲤ"): bstack11l1l_opy_ (u"ࠦࡇࡧ࡭ࡣࡱࡲࠦᲥ"),
            bstack11l1l_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡺࡸ࡬ࠣᲦ"): env.get(bstack11l1l_opy_ (u"ࠨࡢࡢ࡯ࡥࡳࡴࡥࡢࡶ࡫࡯ࡨࡗ࡫ࡳࡶ࡮ࡷࡷ࡚ࡸ࡬ࠣᲧ")),
            bstack11l1l_opy_ (u"ࠢ࡫ࡱࡥࡣࡳࡧ࡭ࡦࠤᲨ"): env.get(bstack11l1l_opy_ (u"ࠣࡤࡤࡱࡧࡵ࡯ࡠࡵ࡫ࡳࡷࡺࡊࡰࡤࡑࡥࡲ࡫ࠢᲩ")),
            bstack11l1l_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡰࡸࡱࡧ࡫ࡲࠣᲪ"): env.get(bstack11l1l_opy_ (u"ࠥࡦࡦࡳࡢࡰࡱࡢࡦࡺ࡯࡬ࡥࡐࡸࡱࡧ࡫ࡲࠣᲫ"))
        }
    if env.get(bstack11l1l_opy_ (u"ࠦ࡜ࡋࡒࡄࡍࡈࡖࠧᲬ")) or env.get(bstack11l1l_opy_ (u"ࠧ࡝ࡅࡓࡅࡎࡉࡗࡥࡍࡂࡋࡑࡣࡕࡏࡐࡆࡎࡌࡒࡊࡥࡓࡕࡃࡕࡘࡊࡊࠢᲭ")):
        return {
            bstack11l1l_opy_ (u"ࠨ࡮ࡢ࡯ࡨࠦᲮ"): bstack11l1l_opy_ (u"ࠢࡘࡧࡵࡧࡰ࡫ࡲࠣᲯ"),
            bstack11l1l_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟ࡶࡴ࡯ࠦᲰ"): env.get(bstack11l1l_opy_ (u"ࠤ࡚ࡉࡗࡉࡋࡆࡔࡢࡆ࡚ࡏࡌࡅࡡࡘࡖࡑࠨᲱ")),
            bstack11l1l_opy_ (u"ࠥ࡮ࡴࡨ࡟࡯ࡣࡰࡩࠧᲲ"): bstack11l1l_opy_ (u"ࠦࡒࡧࡩ࡯ࠢࡓ࡭ࡵ࡫࡬ࡪࡰࡨࠦᲳ") if env.get(bstack11l1l_opy_ (u"ࠧ࡝ࡅࡓࡅࡎࡉࡗࡥࡍࡂࡋࡑࡣࡕࡏࡐࡆࡎࡌࡒࡊࡥࡓࡕࡃࡕࡘࡊࡊࠢᲴ")) else None,
            bstack11l1l_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡴࡵ࡮ࡤࡨࡶࠧᲵ"): env.get(bstack11l1l_opy_ (u"ࠢࡘࡇࡕࡇࡐࡋࡒࡠࡉࡌࡘࡤࡉࡏࡎࡏࡌࡘࠧᲶ"))
        }
    if any([env.get(bstack11l1l_opy_ (u"ࠣࡉࡆࡔࡤࡖࡒࡐࡌࡈࡇ࡙ࠨᲷ")), env.get(bstack11l1l_opy_ (u"ࠤࡊࡇࡑࡕࡕࡅࡡࡓࡖࡔࡐࡅࡄࡖࠥᲸ")), env.get(bstack11l1l_opy_ (u"ࠥࡋࡔࡕࡇࡍࡇࡢࡇࡑࡕࡕࡅࡡࡓࡖࡔࡐࡅࡄࡖࠥᲹ"))]):
        return {
            bstack11l1l_opy_ (u"ࠦࡳࡧ࡭ࡦࠤᲺ"): bstack11l1l_opy_ (u"ࠧࡍ࡯ࡰࡩ࡯ࡩࠥࡉ࡬ࡰࡷࡧࠦ᲻"),
            bstack11l1l_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡻࡲ࡭ࠤ᲼"): None,
            bstack11l1l_opy_ (u"ࠢ࡫ࡱࡥࡣࡳࡧ࡭ࡦࠤᲽ"): env.get(bstack11l1l_opy_ (u"ࠣࡒࡕࡓࡏࡋࡃࡕࡡࡌࡈࠧᲾ")),
            bstack11l1l_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡰࡸࡱࡧ࡫ࡲࠣᲿ"): env.get(bstack11l1l_opy_ (u"ࠥࡆ࡚ࡏࡌࡅࡡࡌࡈࠧ᳀"))
        }
    if env.get(bstack11l1l_opy_ (u"ࠦࡘࡎࡉࡑࡒࡄࡆࡑࡋࠢ᳁")):
        return {
            bstack11l1l_opy_ (u"ࠧࡴࡡ࡮ࡧࠥ᳂"): bstack11l1l_opy_ (u"ࠨࡓࡩ࡫ࡳࡴࡦࡨ࡬ࡦࠤ᳃"),
            bstack11l1l_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥࡵࡳ࡮ࠥ᳄"): env.get(bstack11l1l_opy_ (u"ࠣࡕࡋࡍࡕࡖࡁࡃࡎࡈࡣࡇ࡛ࡉࡍࡆࡢ࡙ࡗࡒࠢ᳅")),
            bstack11l1l_opy_ (u"ࠤ࡭ࡳࡧࡥ࡮ࡢ࡯ࡨࠦ᳆"): bstack11l1l_opy_ (u"ࠥࡎࡴࡨࠠࠤࡽࢀࠦ᳇").format(env.get(bstack11l1l_opy_ (u"ࠫࡘࡎࡉࡑࡒࡄࡆࡑࡋ࡟ࡋࡑࡅࡣࡎࡊࠧ᳈"))) if env.get(bstack11l1l_opy_ (u"࡙ࠧࡈࡊࡒࡓࡅࡇࡒࡅࡠࡌࡒࡆࡤࡏࡄࠣ᳉")) else None,
            bstack11l1l_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡴࡵ࡮ࡤࡨࡶࠧ᳊"): env.get(bstack11l1l_opy_ (u"ࠢࡔࡊࡌࡔࡕࡇࡂࡍࡇࡢࡆ࡚ࡏࡌࡅࡡࡑ࡙ࡒࡈࡅࡓࠤ᳋"))
        }
    if bstack1llll1ll1_opy_(env.get(bstack11l1l_opy_ (u"ࠣࡐࡈࡘࡑࡏࡆ࡚ࠤ᳌"))):
        return {
            bstack11l1l_opy_ (u"ࠤࡱࡥࡲ࡫ࠢ᳍"): bstack11l1l_opy_ (u"ࠥࡒࡪࡺ࡬ࡪࡨࡼࠦ᳎"),
            bstack11l1l_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡹࡷࡲࠢ᳏"): env.get(bstack11l1l_opy_ (u"ࠧࡊࡅࡑࡎࡒ࡝ࡤ࡛ࡒࡍࠤ᳐")),
            bstack11l1l_opy_ (u"ࠨࡪࡰࡤࡢࡲࡦࡳࡥࠣ᳑"): env.get(bstack11l1l_opy_ (u"ࠢࡔࡋࡗࡉࡤࡔࡁࡎࡇࠥ᳒")),
            bstack11l1l_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟࡯ࡷࡰࡦࡪࡸࠢ᳓"): env.get(bstack11l1l_opy_ (u"ࠤࡅ࡙ࡎࡒࡄࡠࡋࡇ᳔ࠦ"))
        }
    if bstack1llll1ll1_opy_(env.get(bstack11l1l_opy_ (u"ࠥࡋࡎ࡚ࡈࡖࡄࡢࡅࡈ࡚ࡉࡐࡐࡖ᳕ࠦ"))):
        return {
            bstack11l1l_opy_ (u"ࠦࡳࡧ࡭ࡦࠤ᳖"): bstack11l1l_opy_ (u"ࠧࡍࡩࡵࡊࡸࡦࠥࡇࡣࡵ࡫ࡲࡲࡸࠨ᳗"),
            bstack11l1l_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡻࡲ࡭ࠤ᳘"): bstack11l1l_opy_ (u"ࠢࡼࡿ࠲ࡿࢂ࠵ࡡࡤࡶ࡬ࡳࡳࡹ࠯ࡳࡷࡱࡷ࠴ࢁࡽ᳙ࠣ").format(env.get(bstack11l1l_opy_ (u"ࠨࡉࡌࡘࡍ࡛ࡂࡠࡕࡈࡖ࡛ࡋࡒࡠࡗࡕࡐࠬ᳚")), env.get(bstack11l1l_opy_ (u"ࠩࡊࡍ࡙ࡎࡕࡃࡡࡕࡉࡕࡕࡓࡊࡖࡒࡖ࡞࠭᳛")), env.get(bstack11l1l_opy_ (u"ࠪࡋࡎ࡚ࡈࡖࡄࡢࡖ࡚ࡔ࡟ࡊࡆ᳜ࠪ"))),
            bstack11l1l_opy_ (u"ࠦ࡯ࡵࡢࡠࡰࡤࡱࡪࠨ᳝"): env.get(bstack11l1l_opy_ (u"ࠧࡍࡉࡕࡊࡘࡆࡤ࡝ࡏࡓࡍࡉࡐࡔ࡝᳞ࠢ")),
            bstack11l1l_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡴࡵ࡮ࡤࡨࡶ᳟ࠧ"): env.get(bstack11l1l_opy_ (u"ࠢࡈࡋࡗࡌ࡚ࡈ࡟ࡓࡗࡑࡣࡎࡊࠢ᳠"))
        }
    if env.get(bstack11l1l_opy_ (u"ࠣࡅࡌࠦ᳡")) == bstack11l1l_opy_ (u"ࠤࡷࡶࡺ࡫᳢ࠢ") and env.get(bstack11l1l_opy_ (u"࡚ࠥࡊࡘࡃࡆࡎ᳣ࠥ")) == bstack11l1l_opy_ (u"ࠦ࠶ࠨ᳤"):
        return {
            bstack11l1l_opy_ (u"ࠧࡴࡡ࡮ࡧ᳥ࠥ"): bstack11l1l_opy_ (u"ࠨࡖࡦࡴࡦࡩࡱࠨ᳦"),
            bstack11l1l_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥࡵࡳ࡮᳧ࠥ"): bstack11l1l_opy_ (u"ࠣࡪࡷࡸࡵࡀ࠯࠰ࡽࢀ᳨ࠦ").format(env.get(bstack11l1l_opy_ (u"࡙ࠩࡉࡗࡉࡅࡍࡡࡘࡖࡑ࠭ᳩ"))),
            bstack11l1l_opy_ (u"ࠥ࡮ࡴࡨ࡟࡯ࡣࡰࡩࠧᳪ"): None,
            bstack11l1l_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡲࡺࡳࡢࡦࡴࠥᳫ"): None,
        }
    if env.get(bstack11l1l_opy_ (u"࡚ࠧࡅࡂࡏࡆࡍ࡙࡟࡟ࡗࡇࡕࡗࡎࡕࡎࠣᳬ")):
        return {
            bstack11l1l_opy_ (u"ࠨ࡮ࡢ࡯ࡨ᳭ࠦ"): bstack11l1l_opy_ (u"ࠢࡕࡧࡤࡱࡨ࡯ࡴࡺࠤᳮ"),
            bstack11l1l_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟ࡶࡴ࡯ࠦᳯ"): None,
            bstack11l1l_opy_ (u"ࠤ࡭ࡳࡧࡥ࡮ࡢ࡯ࡨࠦᳰ"): env.get(bstack11l1l_opy_ (u"ࠥࡘࡊࡇࡍࡄࡋࡗ࡝ࡤࡖࡒࡐࡌࡈࡇ࡙ࡥࡎࡂࡏࡈࠦᳱ")),
            bstack11l1l_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡲࡺࡳࡢࡦࡴࠥᳲ"): env.get(bstack11l1l_opy_ (u"ࠧࡈࡕࡊࡎࡇࡣࡓ࡛ࡍࡃࡇࡕࠦᳳ"))
        }
    if any([env.get(bstack11l1l_opy_ (u"ࠨࡃࡐࡐࡆࡓ࡚ࡘࡓࡆࠤ᳴")), env.get(bstack11l1l_opy_ (u"ࠢࡄࡑࡑࡇࡔ࡛ࡒࡔࡇࡢ࡙ࡗࡒࠢᳵ")), env.get(bstack11l1l_opy_ (u"ࠣࡅࡒࡒࡈࡕࡕࡓࡕࡈࡣ࡚࡙ࡅࡓࡐࡄࡑࡊࠨᳶ")), env.get(bstack11l1l_opy_ (u"ࠤࡆࡓࡓࡉࡏࡖࡔࡖࡉࡤ࡚ࡅࡂࡏࠥ᳷"))]):
        return {
            bstack11l1l_opy_ (u"ࠥࡲࡦࡳࡥࠣ᳸"): bstack11l1l_opy_ (u"ࠦࡈࡵ࡮ࡤࡱࡸࡶࡸ࡫ࠢ᳹"),
            bstack11l1l_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡺࡸ࡬ࠣᳺ"): None,
            bstack11l1l_opy_ (u"ࠨࡪࡰࡤࡢࡲࡦࡳࡥࠣ᳻"): env.get(bstack11l1l_opy_ (u"ࠢࡃࡗࡌࡐࡉࡥࡊࡐࡄࡢࡒࡆࡓࡅࠣ᳼")) or None,
            bstack11l1l_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟࡯ࡷࡰࡦࡪࡸࠢ᳽"): env.get(bstack11l1l_opy_ (u"ࠤࡅ࡙ࡎࡒࡄࡠࡋࡇࠦ᳾"), 0)
        }
    if env.get(bstack11l1l_opy_ (u"ࠥࡋࡔࡥࡊࡐࡄࡢࡒࡆࡓࡅࠣ᳿")):
        return {
            bstack11l1l_opy_ (u"ࠦࡳࡧ࡭ࡦࠤᴀ"): bstack11l1l_opy_ (u"ࠧࡍ࡯ࡄࡆࠥᴁ"),
            bstack11l1l_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡻࡲ࡭ࠤᴂ"): None,
            bstack11l1l_opy_ (u"ࠢ࡫ࡱࡥࡣࡳࡧ࡭ࡦࠤᴃ"): env.get(bstack11l1l_opy_ (u"ࠣࡉࡒࡣࡏࡕࡂࡠࡐࡄࡑࡊࠨᴄ")),
            bstack11l1l_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡰࡸࡱࡧ࡫ࡲࠣᴅ"): env.get(bstack11l1l_opy_ (u"ࠥࡋࡔࡥࡐࡊࡒࡈࡐࡎࡔࡅࡠࡅࡒ࡙ࡓ࡚ࡅࡓࠤᴆ"))
        }
    if env.get(bstack11l1l_opy_ (u"ࠦࡈࡌ࡟ࡃࡗࡌࡐࡉࡥࡉࡅࠤᴇ")):
        return {
            bstack11l1l_opy_ (u"ࠧࡴࡡ࡮ࡧࠥᴈ"): bstack11l1l_opy_ (u"ࠨࡃࡰࡦࡨࡊࡷ࡫ࡳࡩࠤᴉ"),
            bstack11l1l_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥࡵࡳ࡮ࠥᴊ"): env.get(bstack11l1l_opy_ (u"ࠣࡅࡉࡣࡇ࡛ࡉࡍࡆࡢ࡙ࡗࡒࠢᴋ")),
            bstack11l1l_opy_ (u"ࠤ࡭ࡳࡧࡥ࡮ࡢ࡯ࡨࠦᴌ"): env.get(bstack11l1l_opy_ (u"ࠥࡇࡋࡥࡐࡊࡒࡈࡐࡎࡔࡅࡠࡐࡄࡑࡊࠨᴍ")),
            bstack11l1l_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡲࡺࡳࡢࡦࡴࠥᴎ"): env.get(bstack11l1l_opy_ (u"ࠧࡉࡆࡠࡄࡘࡍࡑࡊ࡟ࡊࡆࠥᴏ"))
        }
    return {bstack11l1l_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡴࡵ࡮ࡤࡨࡶࠧᴐ"): None}
def get_host_info():
    return {
        bstack11l1l_opy_ (u"ࠢࡩࡱࡶࡸࡳࡧ࡭ࡦࠤᴑ"): platform.node(),
        bstack11l1l_opy_ (u"ࠣࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࠥᴒ"): platform.system(),
        bstack11l1l_opy_ (u"ࠤࡷࡽࡵ࡫ࠢᴓ"): platform.machine(),
        bstack11l1l_opy_ (u"ࠥࡺࡪࡸࡳࡪࡱࡱࠦᴔ"): platform.version(),
        bstack11l1l_opy_ (u"ࠦࡦࡸࡣࡩࠤᴕ"): platform.architecture()[0]
    }
def bstack1l11ll11l_opy_():
    try:
        import selenium
        return True
    except ImportError:
        return False
def bstack111llllllll_opy_():
    if bstack1l1ll11111_opy_.get_property(bstack11l1l_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯ࡤࡹࡥࡴࡵ࡬ࡳࡳ࠭ᴖ")):
        return bstack11l1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࠬᴗ")
    return bstack11l1l_opy_ (u"ࠧࡶࡰ࡮ࡲࡴࡽ࡮ࡠࡩࡵ࡭ࡩ࠭ᴘ")
def bstack111lll111l1_opy_(driver):
    info = {
        bstack11l1l_opy_ (u"ࠨࡥࡤࡴࡦࡨࡩ࡭࡫ࡷ࡭ࡪࡹࠧᴙ"): driver.capabilities,
        bstack11l1l_opy_ (u"ࠩࡶࡩࡸࡹࡩࡰࡰࡢ࡭ࡩ࠭ᴚ"): driver.session_id,
        bstack11l1l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࠫᴛ"): driver.capabilities.get(bstack11l1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡓࡧ࡭ࡦࠩᴜ"), None),
        bstack11l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡥࡶࡦࡴࡶ࡭ࡴࡴࠧᴝ"): driver.capabilities.get(bstack11l1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡖࡦࡴࡶ࡭ࡴࡴࠧᴞ"), None),
        bstack11l1l_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࠩᴟ"): driver.capabilities.get(bstack11l1l_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡑࡥࡲ࡫ࠧᴠ"), None),
        bstack11l1l_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡣࡻ࡫ࡲࡴ࡫ࡲࡲࠬᴡ"):driver.capabilities.get(bstack11l1l_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱ࡛࡫ࡲࡴ࡫ࡲࡲࠬᴢ"), None),
    }
    if bstack111llllllll_opy_() == bstack11l1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࠪᴣ"):
        if bstack1111ll1l_opy_():
            info[bstack11l1l_opy_ (u"ࠬࡶࡲࡰࡦࡸࡧࡹ࠭ᴤ")] = bstack11l1l_opy_ (u"࠭ࡡࡱࡲ࠰ࡥࡺࡺ࡯࡮ࡣࡷࡩࠬᴥ")
        elif driver.capabilities.get(bstack11l1l_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱ࠺ࡰࡲࡷ࡭ࡴࡴࡳࠨᴦ"), {}).get(bstack11l1l_opy_ (u"ࠨࡶࡸࡶࡧࡵࡳࡤࡣ࡯ࡩࠬᴧ"), False):
            info[bstack11l1l_opy_ (u"ࠩࡳࡶࡴࡪࡵࡤࡶࠪᴨ")] = bstack11l1l_opy_ (u"ࠪࡸࡺࡸࡢࡰࡵࡦࡥࡱ࡫ࠧᴩ")
        else:
            info[bstack11l1l_opy_ (u"ࠫࡵࡸ࡯ࡥࡷࡦࡸࠬᴪ")] = bstack11l1l_opy_ (u"ࠬࡧࡵࡵࡱࡰࡥࡹ࡫ࠧᴫ")
    return info
def bstack1111ll1l_opy_():
    if bstack1l1ll11111_opy_.get_property(bstack11l1l_opy_ (u"࠭ࡡࡱࡲࡢࡥࡺࡺ࡯࡮ࡣࡷࡩࠬᴬ")):
        return True
    if bstack1llll1ll1_opy_(os.environ.get(bstack11l1l_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡉࡔࡡࡄࡔࡕࡥࡁࡖࡖࡒࡑࡆ࡚ࡅࠨᴭ"), None)):
        return True
    return False
def bstack111lll1llll_opy_(bstack111llll11l1_opy_, url, response, headers=None, data=None):
    bstack11l1l_opy_ (u"ࠣࠤࠥࠎࠥࠦࠠࠡࡄࡸ࡭ࡱࡪࠠࡢࡷࡷࡳࡲࡧࡴࡪࡱࡱࠤࡱࡵࡧࠡࡲࡤࡶࡦࡳࡥࡵࡧࡵࡷࠥ࡬࡯ࡳࠢࡵࡩࡶࡻࡥࡴࡶ࠲ࡶࡪࡹࡰࡰࡰࡶࡩࠥࡲ࡯ࡨࡩ࡬ࡲ࡬ࠐࠠࠡࠢࠣࡅࡷ࡭ࡳ࠻ࠌࠣࠤࠥࠦࠠࠡࠢࠣࡶࡪࡷࡵࡦࡵࡷࡣࡹࡿࡰࡦ࠼ࠣࡌ࡙࡚ࡐࠡ࡯ࡨࡸ࡭ࡵࡤࠡࠪࡊࡉ࡙࠲ࠠࡑࡑࡖࡘ࠱ࠦࡥࡵࡥ࠱࠭ࠏࠦࠠࠡࠢࠣࠤࠥࠦࡵࡳ࡮࠽ࠤࡗ࡫ࡱࡶࡧࡶࡸ࡛ࠥࡒࡍ࠱ࡨࡲࡩࡶ࡯ࡪࡰࡷࠎࠥࠦࠠࠡࠢࠣࠤࠥࡸࡥࡴࡲࡲࡲࡸ࡫࠺ࠡࡔࡨࡷࡵࡵ࡮ࡴࡧࠣࡳࡧࡰࡥࡤࡶࠣࡪࡷࡵ࡭ࠡࡴࡨࡵࡺ࡫ࡳࡵࡵࠍࠤࠥࠦࠠࠡࠢࠣࠤ࡭࡫ࡡࡥࡧࡵࡷ࠿ࠦࡒࡦࡳࡸࡩࡸࡺࠠࡩࡧࡤࡨࡪࡸࡳࠡࡱࡵࠤࡓࡵ࡮ࡦࠌࠣࠤࠥࠦࠠࠡࠢࠣࡨࡦࡺࡡ࠻ࠢࡕࡩࡶࡻࡥࡴࡶࠣࡎࡘࡕࡎࠡࡦࡤࡸࡦࠦ࡯ࡳࠢࡑࡳࡳ࡫ࠊࠡࠢࠣࠤࡗ࡫ࡴࡶࡴࡱࡷ࠿ࠐࠠࠡࠢࠣࠤࠥࠦࠠࡥ࡫ࡦࡸ࠿ࠦࡆࡰࡴࡰࡥࡹࡺࡥࡥࠢ࡯ࡳ࡬ࠦ࡭ࡦࡵࡶࡥ࡬࡫ࠠࡸ࡫ࡷ࡬ࠥࡸࡥࡲࡷࡨࡷࡹࠦࡡ࡯ࡦࠣࡶࡪࡹࡰࡰࡰࡶࡩࠥࡪࡡࡵࡣࠍࠤࠥࠦࠠࠣࠤࠥᴮ")
    bstack111lll1lll1_opy_ = {
        bstack11l1l_opy_ (u"ࠤ࡫ࡩࡦࡪࡥࡳࡵࠥᴯ"): headers,
        bstack11l1l_opy_ (u"ࠥࡱࡪࡺࡨࡰࡦࠥᴰ"): bstack111llll11l1_opy_.upper(),
        bstack11l1l_opy_ (u"ࠦࡦ࡭ࡥ࡯ࡶࠥᴱ"): None,
        bstack11l1l_opy_ (u"ࠧ࡫࡮ࡥࡲࡲ࡭ࡳࡺࠢᴲ"): url,
        bstack11l1l_opy_ (u"ࠨࡪࡴࡱࡱࠦᴳ"): data
    }
    try:
        bstack111l1lllll1_opy_ = response.json()
    except Exception:
        bstack111l1lllll1_opy_ = response.text
    bstack111ll111lll_opy_ = {
        bstack11l1l_opy_ (u"ࠢࡣࡱࡧࡽࠧᴴ"): bstack111l1lllll1_opy_,
        bstack11l1l_opy_ (u"ࠣࡵࡷࡥࡹࡻࡳࡄࡱࡧࡩࠧᴵ"): response.status_code
    }
    return {
        bstack11l1l_opy_ (u"ࠤࡵࡩࡶࡻࡥࡴࡶࠥᴶ"): bstack111lll1lll1_opy_,
        bstack11l1l_opy_ (u"ࠥࡶࡪࡹࡰࡰࡰࡶࡩࠧᴷ"): bstack111ll111lll_opy_
    }
def bstack1l111l111l_opy_(bstack111llll11l1_opy_, url, data, config):
    headers = config.get(bstack11l1l_opy_ (u"ࠫ࡭࡫ࡡࡥࡧࡵࡷࠬᴸ"), None)
    proxies = bstack1lllll111l_opy_(config, url)
    auth = config.get(bstack11l1l_opy_ (u"ࠬࡧࡵࡵࡪࠪᴹ"), None)
    response = requests.request(
            bstack111llll11l1_opy_,
            url=url,
            headers=headers,
            auth=auth,
            json=data,
            proxies=proxies
        )
    try:
        log_message = bstack111lll1llll_opy_(bstack111llll11l1_opy_, url, response, headers, data)
        bstack1ll11l1ll_opy_.debug(json.dumps(log_message, separators=(bstack11l1l_opy_ (u"࠭ࠬࠨᴺ"), bstack11l1l_opy_ (u"ࠧ࠻ࠩᴻ"))))
    except Exception as e:
        logger.debug(bstack11l1l_opy_ (u"ࠣࡇࡵࡶࡴࡸࠠࡸࡪ࡬ࡰࡪࠦ࡬ࡰࡩࡪ࡭ࡳ࡭ࠠࡢࡷࡷࡳࡲࡧࡴࡪࡱࡱࠤࡷ࡫ࡱࡶࡧࡶࡸ࠿ࠦࡻࡾࠤᴼ").format(e))
    return response
def bstack11ll111l_opy_(bstack1l11ll1lll_opy_, size):
    bstack1lllll1ll_opy_ = []
    while len(bstack1l11ll1lll_opy_) > size:
        bstack1l111ll11l_opy_ = bstack1l11ll1lll_opy_[:size]
        bstack1lllll1ll_opy_.append(bstack1l111ll11l_opy_)
        bstack1l11ll1lll_opy_ = bstack1l11ll1lll_opy_[size:]
    bstack1lllll1ll_opy_.append(bstack1l11ll1lll_opy_)
    return bstack1lllll1ll_opy_
def bstack111llll111l_opy_(message, bstack111ll11111l_opy_=False):
    os.write(1, bytes(message, bstack11l1l_opy_ (u"ࠩࡸࡸ࡫࠳࠸ࠨᴽ")))
    os.write(1, bytes(bstack11l1l_opy_ (u"ࠪࡠࡳ࠭ᴾ"), bstack11l1l_opy_ (u"ࠫࡺࡺࡦ࠮࠺ࠪᴿ")))
    if bstack111ll11111l_opy_:
        with open(bstack11l1l_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯࠲ࡵ࠱࠲ࡻ࠰ࠫᵀ") + os.environ[bstack11l1l_opy_ (u"࠭ࡂࡔࡡࡗࡉࡘ࡚ࡏࡑࡕࡢࡆ࡚ࡏࡌࡅࡡࡋࡅࡘࡎࡅࡅࡡࡌࡈࠬᵁ")] + bstack11l1l_opy_ (u"ࠧ࠯࡮ࡲ࡫ࠬᵂ"), bstack11l1l_opy_ (u"ࠨࡣࠪᵃ")) as f:
            f.write(message + bstack11l1l_opy_ (u"ࠩ࡟ࡲࠬᵄ"))
def bstack1l1l1111l1l_opy_():
    return os.environ[bstack11l1l_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡄ࡙࡙ࡕࡍࡂࡖࡌࡓࡓ࠭ᵅ")].lower() == bstack11l1l_opy_ (u"ࠫࡹࡸࡵࡦࠩᵆ")
def bstack1lllll111_opy_():
    return bstack1111ll1l1l_opy_().replace(tzinfo=None).isoformat() + bstack11l1l_opy_ (u"ࠬࡠࠧᵇ")
def bstack11l11111l1l_opy_(start, finish):
    return (datetime.datetime.fromisoformat(finish.rstrip(bstack11l1l_opy_ (u"࡚࠭ࠨᵈ"))) - datetime.datetime.fromisoformat(start.rstrip(bstack11l1l_opy_ (u"࡛ࠧࠩᵉ")))).total_seconds() * 1000
def bstack111l1llll1l_opy_(timestamp):
    return bstack111lll11111_opy_(timestamp).isoformat() + bstack11l1l_opy_ (u"ࠨ࡜ࠪᵊ")
def bstack111llllll1l_opy_(bstack111ll111l1l_opy_):
    date_format = bstack11l1l_opy_ (u"ࠩࠨ࡝ࠪࡳࠥࡥࠢࠨࡌ࠿ࠫࡍ࠻ࠧࡖ࠲ࠪ࡬ࠧᵋ")
    bstack111lll1l11l_opy_ = datetime.datetime.strptime(bstack111ll111l1l_opy_, date_format)
    return bstack111lll1l11l_opy_.isoformat() + bstack11l1l_opy_ (u"ࠪ࡞ࠬᵌ")
def bstack11l111ll111_opy_(outcome):
    _, exception, _ = outcome.excinfo or (None, None, None)
    if exception:
        return bstack11l1l_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡧࡧࠫᵍ")
    else:
        return bstack11l1l_opy_ (u"ࠬࡶࡡࡴࡵࡨࡨࠬᵎ")
def bstack1llll1ll1_opy_(val):
    if val is None:
        return False
    return val.__str__().lower() == bstack11l1l_opy_ (u"࠭ࡴࡳࡷࡨࠫᵏ")
def bstack111ll1l1l11_opy_(val):
    return val.__str__().lower() == bstack11l1l_opy_ (u"ࠧࡧࡣ࡯ࡷࡪ࠭ᵐ")
def error_handler(bstack11l1111ll1l_opy_=Exception, class_method=False, default_value=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except bstack11l1111ll1l_opy_ as e:
                print(bstack11l1l_opy_ (u"ࠣࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡧࡷࡱࡧࡹ࡯࡯࡯ࠢࡾࢁࠥ࠳࠾ࠡࡽࢀ࠾ࠥࢁࡽࠣᵑ").format(func.__name__, bstack11l1111ll1l_opy_.__name__, str(e)))
                return default_value
        return wrapper
    def bstack111l1l1ll11_opy_(bstack111ll1l111l_opy_):
        def wrapped(cls, *args, **kwargs):
            try:
                return bstack111ll1l111l_opy_(cls, *args, **kwargs)
            except bstack11l1111ll1l_opy_ as e:
                print(bstack11l1l_opy_ (u"ࠤࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥ࡯࡮ࠡࡨࡸࡲࡨࡺࡩࡰࡰࠣࡿࢂࠦ࠭࠿ࠢࡾࢁ࠿ࠦࡻࡾࠤᵒ").format(bstack111ll1l111l_opy_.__name__, bstack11l1111ll1l_opy_.__name__, str(e)))
                return default_value
        return wrapped
    if class_method:
        return bstack111l1l1ll11_opy_
    else:
        return decorator
def bstack11lll11ll1_opy_(bstack1llllll1ll1_opy_):
    if os.getenv(bstack11l1l_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡄ࡙࡙ࡕࡍࡂࡖࡌࡓࡓ࠭ᵓ")) is not None:
        return bstack1llll1ll1_opy_(os.getenv(bstack11l1l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡅ࡚࡚ࡏࡎࡃࡗࡍࡔࡔࠧᵔ")))
    if bstack11l1l_opy_ (u"ࠬࡧࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࠩᵕ") in bstack1llllll1ll1_opy_ and bstack111ll1l1l11_opy_(bstack1llllll1ll1_opy_[bstack11l1l_opy_ (u"࠭ࡡࡶࡶࡲࡱࡦࡺࡩࡰࡰࠪᵖ")]):
        return False
    if bstack11l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡇࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࠩᵗ") in bstack1llllll1ll1_opy_ and bstack111ll1l1l11_opy_(bstack1llllll1ll1_opy_[bstack11l1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡁࡶࡶࡲࡱࡦࡺࡩࡰࡰࠪᵘ")]):
        return False
    return True
def bstack11ll1l1l_opy_():
    try:
        from pytest_bdd import reporting
        bstack111llll1l1l_opy_ = os.environ.get(bstack11l1l_opy_ (u"ࠤࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡗࡖࡉࡗࡥࡆࡓࡃࡐࡉ࡜ࡕࡒࡌࠤᵙ"), None)
        return bstack111llll1l1l_opy_ is None or bstack111llll1l1l_opy_ == bstack11l1l_opy_ (u"ࠥࡴࡾࡺࡥࡴࡶ࠰ࡦࡩࡪࠢᵚ")
    except Exception as e:
        return False
def bstack11l111l11_opy_(hub_url, CONFIG):
    if bstack1l1l1l1ll1_opy_() <= version.parse(bstack11l1l_opy_ (u"ࠫ࠸࠴࠱࠴࠰࠳ࠫᵛ")):
        if hub_url:
            return bstack11l1l_opy_ (u"ࠧ࡮ࡴࡵࡲ࠽࠳࠴ࠨᵜ") + hub_url + bstack11l1l_opy_ (u"ࠨ࠺࠹࠲࠲ࡻࡩ࠵ࡨࡶࡤࠥᵝ")
        return bstack1lll11lll_opy_
    if hub_url:
        return bstack11l1l_opy_ (u"ࠢࡩࡶࡷࡴࡸࡀ࠯࠰ࠤᵞ") + hub_url + bstack11l1l_opy_ (u"ࠣ࠱ࡺࡨ࠴࡮ࡵࡣࠤᵟ")
    return bstack1ll111ll1l_opy_
def bstack111l1lll1l1_opy_():
    return isinstance(os.getenv(bstack11l1l_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡒ࡜ࡘࡊ࡙ࡔࡠࡒࡏ࡙ࡌࡏࡎࠨᵠ")), str)
def bstack1111lll11_opy_(url):
    return urlparse(url).hostname
def bstack11l11l1ll_opy_(hostname):
    for bstack1l1l11l111_opy_ in bstack11lll111ll_opy_:
        regex = re.compile(bstack1l1l11l111_opy_)
        if regex.match(hostname):
            return True
    return False
def bstack111ll1l1ll1_opy_(bstack111lll11l1l_opy_, file_name, logger):
    bstack1lll11111_opy_ = os.path.join(os.path.expanduser(bstack11l1l_opy_ (u"ࠪࢂࠬᵡ")), bstack111lll11l1l_opy_)
    try:
        if not os.path.exists(bstack1lll11111_opy_):
            os.makedirs(bstack1lll11111_opy_)
        file_path = os.path.join(os.path.expanduser(bstack11l1l_opy_ (u"ࠫࢃ࠭ᵢ")), bstack111lll11l1l_opy_, file_name)
        if not os.path.isfile(file_path):
            with open(file_path, bstack11l1l_opy_ (u"ࠬࡽࠧᵣ")):
                pass
            with open(file_path, bstack11l1l_opy_ (u"ࠨࡷࠬࠤᵤ")) as outfile:
                json.dump({}, outfile)
        return file_path
    except Exception as e:
        logger.debug(bstack11l111ll1l_opy_.format(str(e)))
def bstack111ll1l1l1l_opy_(file_name, key, value, logger):
    file_path = bstack111ll1l1ll1_opy_(bstack11l1l_opy_ (u"ࠧ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠧᵥ"), file_name, logger)
    if file_path != None:
        if os.path.exists(file_path):
            bstack1l1l111ll1_opy_ = json.load(open(file_path, bstack11l1l_opy_ (u"ࠨࡴࡥࠫᵦ")))
        else:
            bstack1l1l111ll1_opy_ = {}
        bstack1l1l111ll1_opy_[key] = value
        with open(file_path, bstack11l1l_opy_ (u"ࠤࡺ࠯ࠧᵧ")) as outfile:
            json.dump(bstack1l1l111ll1_opy_, outfile)
def bstack11l11ll11l_opy_(file_name, logger):
    file_path = bstack111ll1l1ll1_opy_(bstack11l1l_opy_ (u"ࠪ࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࠪᵨ"), file_name, logger)
    bstack1l1l111ll1_opy_ = {}
    if file_path != None and os.path.exists(file_path):
        with open(file_path, bstack11l1l_opy_ (u"ࠫࡷ࠭ᵩ")) as bstack11l1llll11_opy_:
            bstack1l1l111ll1_opy_ = json.load(bstack11l1llll11_opy_)
    return bstack1l1l111ll1_opy_
def bstack111l11l1_opy_(file_path, logger):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        logger.debug(bstack11l1l_opy_ (u"ࠬࡋࡲࡳࡱࡵࠤ࡮ࡴࠠࡥࡧ࡯ࡩࡹ࡯࡮ࡨࠢࡩ࡭ࡱ࡫࠺ࠡࠩᵪ") + file_path + bstack11l1l_opy_ (u"࠭ࠠࠨᵫ") + str(e))
def bstack1l1l1l1ll1_opy_():
    from selenium import webdriver
    return version.parse(webdriver.__version__)
class Notset:
    def __repr__(self):
        return bstack11l1l_opy_ (u"ࠢ࠽ࡐࡒࡘࡘࡋࡔ࠿ࠤᵬ")
def bstack1l11llll_opy_(config):
    if bstack11l1l_opy_ (u"ࠨ࡫ࡶࡔࡱࡧࡹࡸࡴ࡬࡫࡭ࡺࠧᵭ") in config:
        del (config[bstack11l1l_opy_ (u"ࠩ࡬ࡷࡕࡲࡡࡺࡹࡵ࡭࡬࡮ࡴࠨᵮ")])
        return False
    if bstack1l1l1l1ll1_opy_() < version.parse(bstack11l1l_opy_ (u"ࠪ࠷࠳࠺࠮࠱ࠩᵯ")):
        return False
    if bstack1l1l1l1ll1_opy_() >= version.parse(bstack11l1l_opy_ (u"ࠫ࠹࠴࠱࠯࠷ࠪᵰ")):
        return True
    if bstack11l1l_opy_ (u"ࠬࡻࡳࡦ࡙࠶ࡇࠬᵱ") in config and config[bstack11l1l_opy_ (u"࠭ࡵࡴࡧ࡚࠷ࡈ࠭ᵲ")] is False:
        return False
    else:
        return True
def bstack11l1lll111_opy_(args_list, bstack111ll111111_opy_):
    index = -1
    for value in bstack111ll111111_opy_:
        try:
            index = args_list.index(value)
            return index
        except Exception as e:
            return index
    return index
def bstack11l1lllll1l_opy_(a, b):
  for k, v in b.items():
    if isinstance(v, dict) and k in a and isinstance(a[k], dict):
        bstack11l1lllll1l_opy_(a[k], v)
    else:
        a[k] = v
class Result:
    def __init__(self, result=None, duration=None, exception=None, bstack111l1l11l1_opy_=None):
        self.result = result
        self.duration = duration
        self.exception = exception
        self.exception_type = type(self.exception).__name__ if exception else None
        self.bstack111l1l11l1_opy_ = bstack111l1l11l1_opy_
    @classmethod
    def passed(cls):
        return Result(result=bstack11l1l_opy_ (u"ࠧࡱࡣࡶࡷࡪࡪࠧᵳ"))
    @classmethod
    def failed(cls, exception=None):
        return Result(result=bstack11l1l_opy_ (u"ࠨࡨࡤ࡭ࡱ࡫ࡤࠨᵴ"), exception=exception)
    def bstack1lllll1ll1l_opy_(self):
        if self.result != bstack11l1l_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࠩᵵ"):
            return None
        if isinstance(self.exception_type, str) and bstack11l1l_opy_ (u"ࠥࡅࡸࡹࡥࡳࡶ࡬ࡳࡳࠨᵶ") in self.exception_type:
            return bstack11l1l_opy_ (u"ࠦࡆࡹࡳࡦࡴࡷ࡭ࡴࡴࡅࡳࡴࡲࡶࠧᵷ")
        return bstack11l1l_opy_ (u"࡛ࠧ࡮ࡩࡣࡱࡨࡱ࡫ࡤࡆࡴࡵࡳࡷࠨᵸ")
    def bstack111ll1ll1ll_opy_(self):
        if self.result != bstack11l1l_opy_ (u"࠭ࡦࡢ࡫࡯ࡩࡩ࠭ᵹ"):
            return None
        if self.bstack111l1l11l1_opy_:
            return self.bstack111l1l11l1_opy_
        return bstack111lllll11l_opy_(self.exception)
def bstack111lllll11l_opy_(exc):
    return [traceback.format_exception(exc)]
def bstack11l1111llll_opy_(message):
    if isinstance(message, str):
        return not bool(message and message.strip())
    return True
def bstack11lll11l_opy_(object, key, default_value):
    if not object or not object.__dict__:
        return default_value
    if key in object.__dict__.keys():
        return object.__dict__.get(key)
    return default_value
def bstack111llllll1_opy_(config, logger):
    try:
        import playwright
        bstack111lll11ll1_opy_ = playwright.__file__
        bstack111ll1l11l1_opy_ = os.path.split(bstack111lll11ll1_opy_)
        bstack111ll1l1111_opy_ = bstack111ll1l11l1_opy_[0] + bstack11l1l_opy_ (u"ࠧ࠰ࡦࡵ࡭ࡻ࡫ࡲ࠰ࡲࡤࡧࡰࡧࡧࡦ࠱࡯࡭ࡧ࠵ࡣ࡭࡫࠲ࡧࡱ࡯࠮࡫ࡵࠪᵺ")
        os.environ[bstack11l1l_opy_ (u"ࠨࡉࡏࡓࡇࡇࡌࡠࡃࡊࡉࡓ࡚࡟ࡉࡖࡗࡔࡤࡖࡒࡐ࡚࡜ࠫᵻ")] = bstack1l1ll1l1ll_opy_(config)
        with open(bstack111ll1l1111_opy_, bstack11l1l_opy_ (u"ࠩࡵࠫᵼ")) as f:
            bstack111l1ll1_opy_ = f.read()
            bstack111l1l1l1l1_opy_ = bstack11l1l_opy_ (u"ࠪ࡫ࡱࡵࡢࡢ࡮࠰ࡥ࡬࡫࡮ࡵࠩᵽ")
            bstack11l1111l1ll_opy_ = bstack111l1ll1_opy_.find(bstack111l1l1l1l1_opy_)
            if bstack11l1111l1ll_opy_ == -1:
              process = subprocess.Popen(bstack11l1l_opy_ (u"ࠦࡳࡶ࡭ࠡ࡫ࡱࡷࡹࡧ࡬࡭ࠢࡪࡰࡴࡨࡡ࡭࠯ࡤ࡫ࡪࡴࡴࠣᵾ"), shell=True, cwd=bstack111ll1l11l1_opy_[0])
              process.wait()
              bstack111ll11l1l1_opy_ = bstack11l1l_opy_ (u"ࠬࠨࡵࡴࡧࠣࡷࡹࡸࡩࡤࡶࠥ࠿ࠬᵿ")
              bstack111lll1ll11_opy_ = bstack11l1l_opy_ (u"ࠨࠢࠣࠢ࡟ࠦࡺࡹࡥࠡࡵࡷࡶ࡮ࡩࡴ࡝ࠤ࠾ࠤࡨࡵ࡮ࡴࡶࠣࡿࠥࡨ࡯ࡰࡶࡶࡸࡷࡧࡰࠡࡿࠣࡁࠥࡸࡥࡲࡷ࡬ࡶࡪ࠮ࠧࡨ࡮ࡲࡦࡦࡲ࠭ࡢࡩࡨࡲࡹ࠭ࠩ࠼ࠢ࡬ࡪࠥ࠮ࡰࡳࡱࡦࡩࡸࡹ࠮ࡦࡰࡹ࠲ࡌࡒࡏࡃࡃࡏࡣࡆࡍࡅࡏࡖࡢࡌ࡙࡚ࡐࡠࡒࡕࡓ࡝࡟ࠩࠡࡤࡲࡳࡹࡹࡴࡳࡣࡳࠬ࠮ࡁࠠࠣࠤࠥᶀ")
              bstack111l1lll1ll_opy_ = bstack111l1ll1_opy_.replace(bstack111ll11l1l1_opy_, bstack111lll1ll11_opy_)
              with open(bstack111ll1l1111_opy_, bstack11l1l_opy_ (u"ࠧࡸࠩᶁ")) as f:
                f.write(bstack111l1lll1ll_opy_)
    except Exception as e:
        logger.error(bstack1l1l11ll11_opy_.format(str(e)))
def bstack1lll11llll_opy_():
  try:
    bstack111lllll1l1_opy_ = os.path.join(tempfile.gettempdir(), bstack11l1l_opy_ (u"ࠨࡱࡳࡸ࡮ࡳࡡ࡭ࡡ࡫ࡹࡧࡥࡵࡳ࡮࠱࡮ࡸࡵ࡮ࠨᶂ"))
    bstack111lll1l1l1_opy_ = []
    if os.path.exists(bstack111lllll1l1_opy_):
      with open(bstack111lllll1l1_opy_) as f:
        bstack111lll1l1l1_opy_ = json.load(f)
      os.remove(bstack111lllll1l1_opy_)
    return bstack111lll1l1l1_opy_
  except:
    pass
  return []
def bstack11l1l1ll11_opy_(bstack11ll111l11_opy_):
  try:
    bstack111lll1l1l1_opy_ = []
    bstack111lllll1l1_opy_ = os.path.join(tempfile.gettempdir(), bstack11l1l_opy_ (u"ࠩࡲࡴࡹ࡯࡭ࡢ࡮ࡢ࡬ࡺࡨ࡟ࡶࡴ࡯࠲࡯ࡹ࡯࡯ࠩᶃ"))
    if os.path.exists(bstack111lllll1l1_opy_):
      with open(bstack111lllll1l1_opy_) as f:
        bstack111lll1l1l1_opy_ = json.load(f)
    bstack111lll1l1l1_opy_.append(bstack11ll111l11_opy_)
    with open(bstack111lllll1l1_opy_, bstack11l1l_opy_ (u"ࠪࡻࠬᶄ")) as f:
        json.dump(bstack111lll1l1l1_opy_, f)
  except:
    pass
def bstack11111111_opy_(logger, bstack111ll1ll111_opy_ = False):
  try:
    test_name = os.environ.get(bstack11l1l_opy_ (u"ࠫࡕ࡟ࡔࡆࡕࡗࡣ࡙ࡋࡓࡕࡡࡑࡅࡒࡋࠧᶅ"), bstack11l1l_opy_ (u"ࠬ࠭ᶆ"))
    if test_name == bstack11l1l_opy_ (u"࠭ࠧᶇ"):
        test_name = threading.current_thread().__dict__.get(bstack11l1l_opy_ (u"ࠧࡱࡻࡷࡩࡸࡺࡂࡥࡦࡢࡸࡪࡹࡴࡠࡰࡤࡱࡪ࠭ᶈ"), bstack11l1l_opy_ (u"ࠨࠩᶉ"))
    bstack11l111l1l1l_opy_ = bstack11l1l_opy_ (u"ࠩ࠯ࠤࠬᶊ").join(threading.current_thread().bstackTestErrorMessages)
    if bstack111ll1ll111_opy_:
        bstack1ll11111l1_opy_ = os.environ.get(bstack11l1l_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡓࡐࡆ࡚ࡆࡐࡔࡐࡣࡎࡔࡄࡆ࡚ࠪᶋ"), bstack11l1l_opy_ (u"ࠫ࠵࠭ᶌ"))
        bstack11ll1ll1l1_opy_ = {bstack11l1l_opy_ (u"ࠬࡴࡡ࡮ࡧࠪᶍ"): test_name, bstack11l1l_opy_ (u"࠭ࡥࡳࡴࡲࡶࠬᶎ"): bstack11l111l1l1l_opy_, bstack11l1l_opy_ (u"ࠧࡪࡰࡧࡩࡽ࠭ᶏ"): bstack1ll11111l1_opy_}
        bstack111l1ll11ll_opy_ = []
        bstack111ll1lll11_opy_ = os.path.join(tempfile.gettempdir(), bstack11l1l_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࡠࡲࡳࡴࡤ࡫ࡲࡳࡱࡵࡣࡱ࡯ࡳࡵ࠰࡭ࡷࡴࡴࠧᶐ"))
        if os.path.exists(bstack111ll1lll11_opy_):
            with open(bstack111ll1lll11_opy_) as f:
                bstack111l1ll11ll_opy_ = json.load(f)
        bstack111l1ll11ll_opy_.append(bstack11ll1ll1l1_opy_)
        with open(bstack111ll1lll11_opy_, bstack11l1l_opy_ (u"ࠩࡺࠫᶑ")) as f:
            json.dump(bstack111l1ll11ll_opy_, f)
    else:
        bstack11ll1ll1l1_opy_ = {bstack11l1l_opy_ (u"ࠪࡲࡦࡳࡥࠨᶒ"): test_name, bstack11l1l_opy_ (u"ࠫࡪࡸࡲࡰࡴࠪᶓ"): bstack11l111l1l1l_opy_, bstack11l1l_opy_ (u"ࠬ࡯࡮ࡥࡧࡻࠫᶔ"): str(multiprocessing.current_process().name)}
        if bstack11l1l_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡥࡥࡳࡴࡲࡶࡤࡲࡩࡴࡶࠪᶕ") not in multiprocessing.current_process().__dict__.keys():
            multiprocessing.current_process().bstack_error_list = []
        multiprocessing.current_process().bstack_error_list.append(bstack11ll1ll1l1_opy_)
  except Exception as e:
      logger.warn(bstack11l1l_opy_ (u"ࠢࡖࡰࡤࡦࡱ࡫ࠠࡵࡱࠣࡷࡹࡵࡲࡦࠢࡳࡽࡹ࡫ࡳࡵࠢࡩࡹࡳࡴࡥ࡭ࠢࡧࡥࡹࡧ࠺ࠡࡽࢀࠦᶖ").format(e))
def bstack1l1ll1ll_opy_(error_message, test_name, index, logger):
  try:
    from filelock import FileLock
  except ImportError:
    logger.debug(bstack11l1l_opy_ (u"ࠨࡨ࡬ࡰࡪࡲ࡯ࡤ࡭ࠣࡲࡴࡺࠠࡢࡸࡤ࡭ࡱࡧࡢ࡭ࡧ࠯ࠤࡺࡹࡩ࡯ࡩࠣࡦࡦࡹࡩࡤࠢࡩ࡭ࡱ࡫ࠠࡰࡲࡨࡶࡦࡺࡩࡰࡰࡶࠫᶗ"))
    try:
      bstack11l111l11l1_opy_ = []
      bstack11ll1ll1l1_opy_ = {bstack11l1l_opy_ (u"ࠩࡱࡥࡲ࡫ࠧᶘ"): test_name, bstack11l1l_opy_ (u"ࠪࡩࡷࡸ࡯ࡳࠩᶙ"): error_message, bstack11l1l_opy_ (u"ࠫ࡮ࡴࡤࡦࡺࠪᶚ"): index}
      bstack111l1l11l11_opy_ = os.path.join(tempfile.gettempdir(), bstack11l1l_opy_ (u"ࠬࡸ࡯ࡣࡱࡷࡣࡪࡸࡲࡰࡴࡢࡰ࡮ࡹࡴ࠯࡬ࡶࡳࡳ࠭ᶛ"))
      if os.path.exists(bstack111l1l11l11_opy_):
          with open(bstack111l1l11l11_opy_) as f:
              bstack11l111l11l1_opy_ = json.load(f)
      bstack11l111l11l1_opy_.append(bstack11ll1ll1l1_opy_)
      with open(bstack111l1l11l11_opy_, bstack11l1l_opy_ (u"࠭ࡷࠨᶜ")) as f:
          json.dump(bstack11l111l11l1_opy_, f)
    except Exception as e:
      logger.warn(bstack11l1l_opy_ (u"ࠢࡖࡰࡤࡦࡱ࡫ࠠࡵࡱࠣࡷࡹࡵࡲࡦࠢࡵࡳࡧࡵࡴࠡࡨࡸࡲࡳ࡫࡬ࠡࡦࡤࡸࡦࡀࠠࡼࡿࠥᶝ").format(e))
    return
  bstack11l111l11l1_opy_ = []
  bstack11ll1ll1l1_opy_ = {bstack11l1l_opy_ (u"ࠨࡰࡤࡱࡪ࠭ᶞ"): test_name, bstack11l1l_opy_ (u"ࠩࡨࡶࡷࡵࡲࠨᶟ"): error_message, bstack11l1l_opy_ (u"ࠪ࡭ࡳࡪࡥࡹࠩᶠ"): index}
  bstack111l1l11l11_opy_ = os.path.join(tempfile.gettempdir(), bstack11l1l_opy_ (u"ࠫࡷࡵࡢࡰࡶࡢࡩࡷࡸ࡯ࡳࡡ࡯࡭ࡸࡺ࠮࡫ࡵࡲࡲࠬᶡ"))
  lock_file = bstack111l1l11l11_opy_ + bstack11l1l_opy_ (u"ࠬ࠴࡬ࡰࡥ࡮ࠫᶢ")
  try:
    with FileLock(lock_file, timeout=10):
      if os.path.exists(bstack111l1l11l11_opy_):
          with open(bstack111l1l11l11_opy_, bstack11l1l_opy_ (u"࠭ࡲࠨᶣ")) as f:
              content = f.read().strip()
              if content:
                  bstack11l111l11l1_opy_ = json.load(open(bstack111l1l11l11_opy_))
      bstack11l111l11l1_opy_.append(bstack11ll1ll1l1_opy_)
      with open(bstack111l1l11l11_opy_, bstack11l1l_opy_ (u"ࠧࡸࠩᶤ")) as f:
          json.dump(bstack11l111l11l1_opy_, f)
  except Exception as e:
    logger.warn(bstack11l1l_opy_ (u"ࠣࡗࡱࡥࡧࡲࡥࠡࡶࡲࠤࡸࡺ࡯ࡳࡧࠣࡶࡴࡨ࡯ࡵࠢࡩࡹࡳࡴࡥ࡭ࠢࡧࡥࡹࡧࠠࡸ࡫ࡷ࡬ࠥ࡬ࡩ࡭ࡧࠣࡰࡴࡩ࡫ࡪࡰࡪ࠾ࠥࢁࡽࠣᶥ").format(e))
def bstack1l1111l1ll_opy_(bstack1l1ll11l11_opy_, name, logger):
  try:
    bstack11ll1ll1l1_opy_ = {bstack11l1l_opy_ (u"ࠩࡱࡥࡲ࡫ࠧᶦ"): name, bstack11l1l_opy_ (u"ࠪࡩࡷࡸ࡯ࡳࠩᶧ"): bstack1l1ll11l11_opy_, bstack11l1l_opy_ (u"ࠫ࡮ࡴࡤࡦࡺࠪᶨ"): str(threading.current_thread()._name)}
    return bstack11ll1ll1l1_opy_
  except Exception as e:
    logger.warn(bstack11l1l_opy_ (u"࡛ࠧ࡮ࡢࡤ࡯ࡩࠥࡺ࡯ࠡࡵࡷࡳࡷ࡫ࠠࡣࡧ࡫ࡥࡻ࡫ࠠࡧࡷࡱࡲࡪࡲࠠࡥࡣࡷࡥ࠿ࠦࡻࡾࠤᶩ").format(e))
  return
def bstack11l11111lll_opy_():
    return platform.system() == bstack11l1l_opy_ (u"࠭ࡗࡪࡰࡧࡳࡼࡹࠧᶪ")
def bstack1ll1l1ll1_opy_(bstack11l1111l1l1_opy_, config, logger):
    bstack111l1l1l11l_opy_ = {}
    try:
        return {key: config[key] for key in config if bstack11l1111l1l1_opy_.match(key)}
    except Exception as e:
        logger.debug(bstack11l1l_opy_ (u"ࠢࡖࡰࡤࡦࡱ࡫ࠠࡵࡱࠣࡪ࡮ࡲࡴࡦࡴࠣࡧࡴࡴࡦࡪࡩࠣ࡯ࡪࡿࡳࠡࡤࡼࠤࡷ࡫ࡧࡦࡺࠣࡱࡦࡺࡣࡩ࠼ࠣࡿࢂࠨᶫ").format(e))
    return bstack111l1l1l11l_opy_
def bstack111llll1111_opy_(bstack111ll11llll_opy_, bstack111l1ll1ll1_opy_):
    bstack111l1l1ll1l_opy_ = version.parse(bstack111ll11llll_opy_)
    bstack111llll1ll1_opy_ = version.parse(bstack111l1ll1ll1_opy_)
    if bstack111l1l1ll1l_opy_ > bstack111llll1ll1_opy_:
        return 1
    elif bstack111l1l1ll1l_opy_ < bstack111llll1ll1_opy_:
        return -1
    else:
        return 0
def bstack1111ll1l1l_opy_():
    return datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
def bstack111lll11111_opy_(timestamp):
    return datetime.datetime.fromtimestamp(timestamp, datetime.timezone.utc).replace(tzinfo=None)
def bstack111l1l1lll1_opy_(framework):
    from browserstack_sdk._version import __version__
    return str(framework) + str(__version__)
def bstack1l111llll_opy_(options, framework, config, bstack11l1111ll1_opy_={}):
    if options is None:
        return
    if getattr(options, bstack11l1l_opy_ (u"ࠨࡩࡨࡸࠬᶬ"), None):
        caps = options
    else:
        caps = options.to_capabilities()
    bstack1l11111l1_opy_ = caps.get(bstack11l1l_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬࠼ࡲࡴࡹ࡯࡯࡯ࡵࠪᶭ"))
    bstack111l1lll11l_opy_ = True
    bstack1ll1lll11l_opy_ = os.environ[bstack11l1l_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡉࡘ࡚ࡈࡖࡄࡢ࡙࡚ࡏࡄࠨᶮ")]
    bstack1l1lll11l11_opy_ = config.get(bstack11l1l_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠫᶯ"), False)
    if bstack1l1lll11l11_opy_:
        bstack1ll1ll1lll1_opy_ = config.get(bstack11l1l_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࡔࡶࡴࡪࡱࡱࡷࠬᶰ"), {})
        bstack1ll1ll1lll1_opy_[bstack11l1l_opy_ (u"࠭ࡡࡶࡶ࡫ࡘࡴࡱࡥ࡯ࠩᶱ")] = os.getenv(bstack11l1l_opy_ (u"ࠧࡃࡕࡢࡅ࠶࠷࡙ࡠࡌ࡚ࡘࠬᶲ"))
        bstack11ll11111l1_opy_ = json.loads(os.getenv(bstack11l1l_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡤࡇࡃࡄࡇࡖࡗࡎࡈࡉࡍࡋࡗ࡝ࡤࡉࡏࡏࡈࡌࡋ࡚ࡘࡁࡕࡋࡒࡒࡤ࡟ࡍࡍࠩᶳ"), bstack11l1l_opy_ (u"ࠩࡾࢁࠬᶴ"))).get(bstack11l1l_opy_ (u"ࠪࡷࡨࡧ࡮࡯ࡧࡵ࡚ࡪࡸࡳࡪࡱࡱࠫᶵ"))
    if bstack111ll1l1l11_opy_(caps.get(bstack11l1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡹࡸ࡫ࡗ࠴ࡅࠪᶶ"))) or bstack111ll1l1l11_opy_(caps.get(bstack11l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡺࡹࡥࡠࡹ࠶ࡧࠬᶷ"))):
        bstack111l1lll11l_opy_ = False
    if bstack1l11llll_opy_({bstack11l1l_opy_ (u"ࠨࡵࡴࡧ࡚࠷ࡈࠨᶸ"): bstack111l1lll11l_opy_}):
        bstack1l11111l1_opy_ = bstack1l11111l1_opy_ or {}
        bstack1l11111l1_opy_[bstack11l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࡙ࡄࡌࠩᶹ")] = bstack111l1l1lll1_opy_(framework)
        bstack1l11111l1_opy_[bstack11l1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡁࡶࡶࡲࡱࡦࡺࡩࡰࡰࠪᶺ")] = bstack1l1l1111l1l_opy_()
        bstack1l11111l1_opy_[bstack11l1l_opy_ (u"ࠩࡷࡩࡸࡺࡨࡶࡤࡅࡹ࡮ࡲࡤࡖࡷ࡬ࡨࠬᶻ")] = bstack1ll1lll11l_opy_
        bstack1l11111l1_opy_[bstack11l1l_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡒࡵࡳࡩࡻࡣࡵࡏࡤࡴࠬᶼ")] = bstack11l1111ll1_opy_
        if bstack1l1lll11l11_opy_:
            bstack1l11111l1_opy_[bstack11l1l_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠫᶽ")] = bstack1l1lll11l11_opy_
            bstack1l11111l1_opy_[bstack11l1l_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࡔࡶࡴࡪࡱࡱࡷࠬᶾ")] = bstack1ll1ll1lll1_opy_
            bstack1l11111l1_opy_[bstack11l1l_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࡕࡰࡵ࡫ࡲࡲࡸ࠭ᶿ")][bstack11l1l_opy_ (u"ࠧࡴࡥࡤࡲࡳ࡫ࡲࡗࡧࡵࡷ࡮ࡵ࡮ࠨ᷀")] = bstack11ll11111l1_opy_
        if getattr(options, bstack11l1l_opy_ (u"ࠨࡵࡨࡸࡤࡩࡡࡱࡣࡥ࡭ࡱ࡯ࡴࡺࠩ᷁"), None):
            options.set_capability(bstack11l1l_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬࠼ࡲࡴࡹ࡯࡯࡯ࡵ᷂ࠪ"), bstack1l11111l1_opy_)
        else:
            options[bstack11l1l_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭࠽ࡳࡵࡺࡩࡰࡰࡶࠫ᷃")] = bstack1l11111l1_opy_
    else:
        if getattr(options, bstack11l1l_opy_ (u"ࠫࡸ࡫ࡴࡠࡥࡤࡴࡦࡨࡩ࡭࡫ࡷࡽࠬ᷄"), None):
            options.set_capability(bstack11l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡖࡈࡐ࠭᷅"), bstack111l1l1lll1_opy_(framework))
            options.set_capability(bstack11l1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡅࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࠧ᷆"), bstack1l1l1111l1l_opy_())
            options.set_capability(bstack11l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡴࡦࡵࡷ࡬ࡺࡨࡂࡶ࡫࡯ࡨ࡚ࡻࡩࡥࠩ᷇"), bstack1ll1lll11l_opy_)
            options.set_capability(bstack11l1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡣࡷ࡬ࡰࡩࡖࡲࡰࡦࡸࡧࡹࡓࡡࡱࠩ᷈"), bstack11l1111ll1_opy_)
            if bstack1l1lll11l11_opy_:
                options.set_capability(bstack11l1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠨ᷉"), bstack1l1lll11l11_opy_)
                options.set_capability(bstack11l1l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࡑࡳࡸ࡮ࡵ࡮ࡴ᷊ࠩ"), bstack1ll1ll1lll1_opy_)
                options.set_capability(bstack11l1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࡒࡴࡹ࡯࡯࡯ࡵ࠱ࡷࡨࡧ࡮࡯ࡧࡵ࡚ࡪࡸࡳࡪࡱࡱࠫ᷋"), bstack11ll11111l1_opy_)
        else:
            options[bstack11l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡖࡈࡐ࠭᷌")] = bstack111l1l1lll1_opy_(framework)
            options[bstack11l1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡅࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࠧ᷍")] = bstack1l1l1111l1l_opy_()
            options[bstack11l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡴࡦࡵࡷ࡬ࡺࡨࡂࡶ࡫࡯ࡨ࡚ࡻࡩࡥ᷎ࠩ")] = bstack1ll1lll11l_opy_
            options[bstack11l1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡣࡷ࡬ࡰࡩࡖࡲࡰࡦࡸࡧࡹࡓࡡࡱ᷏ࠩ")] = bstack11l1111ll1_opy_
            if bstack1l1lll11l11_opy_:
                options[bstack11l1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠨ᷐")] = bstack1l1lll11l11_opy_
                options[bstack11l1l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࡑࡳࡸ࡮ࡵ࡮ࡴࠩ᷑")] = bstack1ll1ll1lll1_opy_
                options[bstack11l1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࡒࡴࡹ࡯࡯࡯ࡵࠪ᷒")][bstack11l1l_opy_ (u"ࠬࡹࡣࡢࡰࡱࡩࡷ࡜ࡥࡳࡵ࡬ࡳࡳ࠭ᷓ")] = bstack11ll11111l1_opy_
    return options
def bstack11l1111lll1_opy_(bstack11l1111111l_opy_, framework):
    bstack11l1111ll1_opy_ = bstack1l1ll11111_opy_.get_property(bstack11l1l_opy_ (u"ࠨࡐࡍࡃ࡜࡛ࡗࡏࡇࡉࡖࡢࡔࡗࡕࡄࡖࡅࡗࡣࡒࡇࡐࠣᷔ"))
    if bstack11l1111111l_opy_ and len(bstack11l1111111l_opy_.split(bstack11l1l_opy_ (u"ࠧࡤࡣࡳࡷࡂ࠭ᷕ"))) > 1:
        ws_url = bstack11l1111111l_opy_.split(bstack11l1l_opy_ (u"ࠨࡥࡤࡴࡸࡃࠧᷖ"))[0]
        if bstack11l1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡥࡲࡱࠬᷗ") in ws_url:
            from browserstack_sdk._version import __version__
            bstack11l11111111_opy_ = json.loads(urllib.parse.unquote(bstack11l1111111l_opy_.split(bstack11l1l_opy_ (u"ࠪࡧࡦࡶࡳ࠾ࠩᷘ"))[1]))
            bstack11l11111111_opy_ = bstack11l11111111_opy_ or {}
            bstack1ll1lll11l_opy_ = os.environ[bstack11l1l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡉࡗࡅࡣ࡚࡛ࡉࡅࠩᷙ")]
            bstack11l11111111_opy_[bstack11l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡖࡈࡐ࠭ᷚ")] = str(framework) + str(__version__)
            bstack11l11111111_opy_[bstack11l1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡅࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࠧᷛ")] = bstack1l1l1111l1l_opy_()
            bstack11l11111111_opy_[bstack11l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡴࡦࡵࡷ࡬ࡺࡨࡂࡶ࡫࡯ࡨ࡚ࡻࡩࡥࠩᷜ")] = bstack1ll1lll11l_opy_
            bstack11l11111111_opy_[bstack11l1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡣࡷ࡬ࡰࡩࡖࡲࡰࡦࡸࡧࡹࡓࡡࡱࠩᷝ")] = bstack11l1111ll1_opy_
            bstack11l1111111l_opy_ = bstack11l1111111l_opy_.split(bstack11l1l_opy_ (u"ࠩࡦࡥࡵࡹ࠽ࠨᷞ"))[0] + bstack11l1l_opy_ (u"ࠪࡧࡦࡶࡳ࠾ࠩᷟ") + urllib.parse.quote(json.dumps(bstack11l11111111_opy_))
    return bstack11l1111111l_opy_
def bstack1lll1111_opy_():
    global bstack11l111ll1_opy_
    from playwright._impl._browser_type import BrowserType
    bstack11l111ll1_opy_ = BrowserType.connect
    return bstack11l111ll1_opy_
def bstack1l111ll1l_opy_(framework_name):
    global bstack11l1ll111l_opy_
    bstack11l1ll111l_opy_ = framework_name
    return framework_name
def bstack1l1l1l1l_opy_(self, *args, **kwargs):
    global bstack11l111ll1_opy_
    try:
        global bstack11l1ll111l_opy_
        if bstack11l1l_opy_ (u"ࠫࡼࡹࡅ࡯ࡦࡳࡳ࡮ࡴࡴࠨᷠ") in kwargs:
            kwargs[bstack11l1l_opy_ (u"ࠬࡽࡳࡆࡰࡧࡴࡴ࡯࡮ࡵࠩᷡ")] = bstack11l1111lll1_opy_(
                kwargs.get(bstack11l1l_opy_ (u"࠭ࡷࡴࡇࡱࡨࡵࡵࡩ࡯ࡶࠪᷢ"), None),
                bstack11l1ll111l_opy_
            )
    except Exception as e:
        logger.error(bstack11l1l_opy_ (u"ࠢࡆࡴࡵࡳࡷࠦࡷࡩࡧࡱࠤࡵࡸ࡯ࡤࡧࡶࡷ࡮ࡴࡧࠡࡕࡇࡏࠥࡩࡡࡱࡵ࠽ࠤࢀࢃࠢᷣ").format(str(e)))
    return bstack11l111ll1_opy_(self, *args, **kwargs)
def bstack111ll1l1lll_opy_(bstack111l1ll1111_opy_, proxies):
    proxy_settings = {}
    try:
        if not proxies:
            proxies = bstack1lllll111l_opy_(bstack111l1ll1111_opy_, bstack11l1l_opy_ (u"ࠣࠤᷤ"))
        if proxies and proxies.get(bstack11l1l_opy_ (u"ࠤ࡫ࡸࡹࡶࡳࠣᷥ")):
            parsed_url = urlparse(proxies.get(bstack11l1l_opy_ (u"ࠥ࡬ࡹࡺࡰࡴࠤᷦ")))
            if parsed_url and parsed_url.hostname: proxy_settings[bstack11l1l_opy_ (u"ࠫࡵࡸ࡯ࡹࡻࡋࡳࡸࡺࠧᷧ")] = str(parsed_url.hostname)
            if parsed_url and parsed_url.port: proxy_settings[bstack11l1l_opy_ (u"ࠬࡶࡲࡰࡺࡼࡔࡴࡸࡴࠨᷨ")] = str(parsed_url.port)
            if parsed_url and parsed_url.username: proxy_settings[bstack11l1l_opy_ (u"࠭ࡰࡳࡱࡻࡽ࡚ࡹࡥࡳࠩᷩ")] = str(parsed_url.username)
            if parsed_url and parsed_url.password: proxy_settings[bstack11l1l_opy_ (u"ࠧࡱࡴࡲࡼࡾࡖࡡࡴࡵࠪᷪ")] = str(parsed_url.password)
        return proxy_settings
    except:
        return proxy_settings
def bstack111l1ll11_opy_(bstack111l1ll1111_opy_):
    bstack111ll11l1ll_opy_ = {
        bstack11l1l1111ll_opy_[bstack111l1ll1l11_opy_]: bstack111l1ll1111_opy_[bstack111l1ll1l11_opy_]
        for bstack111l1ll1l11_opy_ in bstack111l1ll1111_opy_
        if bstack111l1ll1l11_opy_ in bstack11l1l1111ll_opy_
    }
    bstack111ll11l1ll_opy_[bstack11l1l_opy_ (u"ࠣࡲࡵࡳࡽࡿࡓࡦࡶࡷ࡭ࡳ࡭ࡳࠣᷫ")] = bstack111ll1l1lll_opy_(bstack111l1ll1111_opy_, bstack1l1ll11111_opy_.get_property(bstack11l1l_opy_ (u"ࠤࡳࡶࡴࡾࡹࡔࡧࡷࡸ࡮ࡴࡧࡴࠤᷬ")))
    bstack111ll1lll1l_opy_ = [element.lower() for element in bstack11l1l1111l1_opy_]
    bstack111ll111l11_opy_(bstack111ll11l1ll_opy_, bstack111ll1lll1l_opy_)
    return bstack111ll11l1ll_opy_
def bstack111ll111l11_opy_(d, keys):
    for key in list(d.keys()):
        if key.lower() in keys:
            d[key] = bstack11l1l_opy_ (u"ࠥ࠮࠯࠰ࠪࠣᷭ")
    for value in d.values():
        if isinstance(value, dict):
            bstack111ll111l11_opy_(value, keys)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    bstack111ll111l11_opy_(item, keys)
def bstack1l1l1ll11l1_opy_():
    bstack111ll1l11ll_opy_ = [os.environ.get(bstack11l1l_opy_ (u"ࠦࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡊࡎࡒࡅࡔࡡࡇࡍࡗࠨᷮ")), os.path.join(os.path.expanduser(bstack11l1l_opy_ (u"ࠧࢄࠢᷯ")), bstack11l1l_opy_ (u"࠭࠮ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠭ᷰ")), os.path.join(bstack11l1l_opy_ (u"ࠧ࠰ࡶࡰࡴࠬᷱ"), bstack11l1l_opy_ (u"ࠨ࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࠨᷲ"))]
    for path in bstack111ll1l11ll_opy_:
        if path is None:
            continue
        try:
            if os.path.exists(path):
                logger.debug(bstack11l1l_opy_ (u"ࠤࡉ࡭ࡱ࡫ࠠࠨࠤᷳ") + str(path) + bstack11l1l_opy_ (u"ࠥࠫࠥ࡫ࡸࡪࡵࡷࡷ࠳ࠨᷴ"))
                if not os.access(path, os.W_OK):
                    logger.debug(bstack11l1l_opy_ (u"ࠦࡌ࡯ࡶࡪࡰࡪࠤࡵ࡫ࡲ࡮࡫ࡶࡷ࡮ࡵ࡮ࡴࠢࡩࡳࡷࠦࠧࠣ᷵") + str(path) + bstack11l1l_opy_ (u"ࠧ࠭ࠢ᷶"))
                    os.chmod(path, 0o777)
                else:
                    logger.debug(bstack11l1l_opy_ (u"ࠨࡆࡪ࡮ࡨࠤࠬࠨ᷷") + str(path) + bstack11l1l_opy_ (u"ࠢࠨࠢࡤࡰࡷ࡫ࡡࡥࡻࠣ࡬ࡦࡹࠠࡵࡪࡨࠤࡷ࡫ࡱࡶ࡫ࡵࡩࡩࠦࡰࡦࡴࡰ࡭ࡸࡹࡩࡰࡰࡶ࠲᷸ࠧ"))
            else:
                logger.debug(bstack11l1l_opy_ (u"ࠣࡅࡵࡩࡦࡺࡩ࡯ࡩࠣࡪ࡮ࡲࡥ᷹ࠡࠩࠥ") + str(path) + bstack11l1l_opy_ (u"ࠤࠪࠤࡼ࡯ࡴࡩࠢࡺࡶ࡮ࡺࡥࠡࡲࡨࡶࡲ࡯ࡳࡴ࡫ࡲࡲ࠳ࠨ᷺"))
                os.makedirs(path, exist_ok=True)
                os.chmod(path, 0o777)
            logger.debug(bstack11l1l_opy_ (u"ࠥࡓࡵ࡫ࡲࡢࡶ࡬ࡳࡳࠦࡳࡶࡥࡦࡩࡪࡪࡥࡥࠢࡩࡳࡷࠦࠧࠣ᷻") + str(path) + bstack11l1l_opy_ (u"ࠦࠬ࠴ࠢ᷼"))
            return path
        except Exception as e:
            logger.debug(bstack11l1l_opy_ (u"ࠧࡌࡡࡪ࡮ࡨࡨࠥࡺ࡯ࠡࡵࡨࡸࠥࡻࡰࠡࡨ࡬ࡰࡪࠦࠧࡼࡲࡤࡸ࡭ࢃࠧ࠻᷽ࠢࠥ") + str(e) + bstack11l1l_opy_ (u"ࠨࠢ᷾"))
    logger.debug(bstack11l1l_opy_ (u"ࠢࡂ࡮࡯ࠤࡵࡧࡴࡩࡵࠣࡪࡦ࡯࡬ࡦࡦ࠱᷿ࠦ"))
    return None
@measure(event_name=EVENTS.bstack11l11llll1l_opy_, stage=STAGE.bstack1lll1l11l_opy_)
def bstack1ll1l1ll111_opy_(binary_path, bstack1ll11llll1l_opy_, bs_config):
    logger.debug(bstack11l1l_opy_ (u"ࠣࡅࡸࡶࡷ࡫࡮ࡵࠢࡆࡐࡎࠦࡐࡢࡶ࡫ࠤ࡫ࡵࡵ࡯ࡦ࠽ࠤࢀࢃࠢḀ").format(binary_path))
    bstack111l1l1l1ll_opy_ = bstack11l1l_opy_ (u"ࠩࠪḁ")
    bstack111ll11ll11_opy_ = {
        bstack11l1l_opy_ (u"ࠪࡷࡩࡱ࡟ࡷࡧࡵࡷ࡮ࡵ࡮ࠨḂ"): __version__,
        bstack11l1l_opy_ (u"ࠦࡴࡹࠢḃ"): platform.system(),
        bstack11l1l_opy_ (u"ࠧࡵࡳࡠࡣࡵࡧ࡭ࠨḄ"): platform.machine(),
        bstack11l1l_opy_ (u"ࠨࡣ࡭࡫ࡢࡺࡪࡸࡳࡪࡱࡱࠦḅ"): bstack11l1l_opy_ (u"ࠧ࠱ࠩḆ"),
        bstack11l1l_opy_ (u"ࠣࡵࡧ࡯ࡤࡲࡡ࡯ࡩࡸࡥ࡬࡫ࠢḇ"): bstack11l1l_opy_ (u"ࠩࡳࡽࡹ࡮࡯࡯ࠩḈ")
    }
    bstack11l111l11ll_opy_(bstack111ll11ll11_opy_)
    try:
        if binary_path:
            if bstack11l11111lll_opy_():
                bstack111ll11ll11_opy_[bstack11l1l_opy_ (u"ࠪࡧࡱ࡯࡟ࡷࡧࡵࡷ࡮ࡵ࡮ࠨḉ")] = subprocess.check_output([binary_path, bstack11l1l_opy_ (u"ࠦࡻ࡫ࡲࡴ࡫ࡲࡲࠧḊ")]).strip().decode(bstack11l1l_opy_ (u"ࠬࡻࡴࡧ࠯࠻ࠫḋ"))
            else:
                bstack111ll11ll11_opy_[bstack11l1l_opy_ (u"࠭ࡣ࡭࡫ࡢࡺࡪࡸࡳࡪࡱࡱࠫḌ")] = subprocess.check_output([binary_path, bstack11l1l_opy_ (u"ࠢࡷࡧࡵࡷ࡮ࡵ࡮ࠣḍ")], stderr=subprocess.DEVNULL).strip().decode(bstack11l1l_opy_ (u"ࠨࡷࡷࡪ࠲࠾ࠧḎ"))
        response = requests.request(
            bstack11l1l_opy_ (u"ࠩࡊࡉ࡙࠭ḏ"),
            url=bstack1ll1l1l11_opy_(bstack11l1l1l1lll_opy_),
            headers=None,
            auth=(bs_config[bstack11l1l_opy_ (u"ࠪࡹࡸ࡫ࡲࡏࡣࡰࡩࠬḐ")], bs_config[bstack11l1l_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶࡏࡪࡿࠧḑ")]),
            json=None,
            params=bstack111ll11ll11_opy_
        )
        data = response.json()
        if response.status_code == 200 and bstack11l1l_opy_ (u"ࠬࡻࡲ࡭ࠩḒ") in data.keys() and bstack11l1l_opy_ (u"࠭ࡵࡱࡦࡤࡸࡪࡪ࡟ࡤ࡮࡬ࡣࡻ࡫ࡲࡴ࡫ࡲࡲࠬḓ") in data.keys():
            logger.debug(bstack11l1l_opy_ (u"ࠢࡏࡧࡨࡨࠥࡺ࡯ࠡࡷࡳࡨࡦࡺࡥࠡࡤ࡬ࡲࡦࡸࡹ࠭ࠢࡦࡹࡷࡸࡥ࡯ࡶࠣࡦ࡮ࡴࡡࡳࡻࠣࡺࡪࡸࡳࡪࡱࡱ࠾ࠥࢁࡽࠣḔ").format(bstack111ll11ll11_opy_[bstack11l1l_opy_ (u"ࠨࡥ࡯࡭ࡤࡼࡥࡳࡵ࡬ࡳࡳ࠭ḕ")]))
            if bstack11l1l_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡄࡌࡒࡆࡘ࡙ࡠࡗࡕࡐࠬḖ") in os.environ:
                logger.debug(bstack11l1l_opy_ (u"ࠥࡗࡰ࡯ࡰࡱ࡫ࡱ࡫ࠥࡨࡩ࡯ࡣࡵࡽࠥࡪ࡯ࡸࡰ࡯ࡳࡦࡪࠠࡢࡵࠣࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡅࡍࡓࡇࡒ࡚ࡡࡘࡖࡑࠦࡩࡴࠢࡶࡩࡹࠨḗ"))
                data[bstack11l1l_opy_ (u"ࠫࡺࡸ࡬ࠨḘ")] = os.environ[bstack11l1l_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡇࡏࡎࡂࡔ࡜ࡣ࡚ࡘࡌࠨḙ")]
            bstack111llll11ll_opy_ = bstack111lllllll1_opy_(data[bstack11l1l_opy_ (u"࠭ࡵࡳ࡮ࠪḚ")], bstack1ll11llll1l_opy_)
            bstack111l1l1l1ll_opy_ = os.path.join(bstack1ll11llll1l_opy_, bstack111llll11ll_opy_)
            os.chmod(bstack111l1l1l1ll_opy_, 0o777) # bstack11l111ll1l1_opy_ permission
            return bstack111l1l1l1ll_opy_
    except Exception as e:
        logger.debug(bstack11l1l_opy_ (u"ࠢࡆࡴࡵࡳࡷࠦࡷࡩ࡫࡯ࡩࠥࡪ࡯ࡸࡰ࡯ࡳࡦࡪࡩ࡯ࡩࠣࡲࡪࡽࠠࡔࡆࡎࠤࢀࢃࠢḛ").format(e))
    return binary_path
def bstack11l111l11ll_opy_(bstack111ll11ll11_opy_):
    try:
        if bstack11l1l_opy_ (u"ࠨ࡮࡬ࡲࡺࡾࠧḜ") not in bstack111ll11ll11_opy_[bstack11l1l_opy_ (u"ࠩࡲࡷࠬḝ")].lower():
            return
        if os.path.exists(bstack11l1l_opy_ (u"ࠥ࠳ࡪࡺࡣ࠰ࡱࡶ࠱ࡷ࡫࡬ࡦࡣࡶࡩࠧḞ")):
            with open(bstack11l1l_opy_ (u"ࠦ࠴࡫ࡴࡤ࠱ࡲࡷ࠲ࡸࡥ࡭ࡧࡤࡷࡪࠨḟ"), bstack11l1l_opy_ (u"ࠧࡸࠢḠ")) as f:
                bstack111l1ll11l1_opy_ = {}
                for line in f:
                    if bstack11l1l_opy_ (u"ࠨ࠽ࠣḡ") in line:
                        key, value = line.rstrip().split(bstack11l1l_opy_ (u"ࠢ࠾ࠤḢ"), 1)
                        bstack111l1ll11l1_opy_[key] = value.strip(bstack11l1l_opy_ (u"ࠨࠤ࡟ࠫࠬḣ"))
                bstack111ll11ll11_opy_[bstack11l1l_opy_ (u"ࠩࡧ࡭ࡸࡺࡲࡰࠩḤ")] = bstack111l1ll11l1_opy_.get(bstack11l1l_opy_ (u"ࠥࡍࡉࠨḥ"), bstack11l1l_opy_ (u"ࠦࠧḦ"))
        elif os.path.exists(bstack11l1l_opy_ (u"ࠧ࠵ࡥࡵࡥ࠲ࡥࡱࡶࡩ࡯ࡧ࠰ࡶࡪࡲࡥࡢࡵࡨࠦḧ")):
            bstack111ll11ll11_opy_[bstack11l1l_opy_ (u"࠭ࡤࡪࡵࡷࡶࡴ࠭Ḩ")] = bstack11l1l_opy_ (u"ࠧࡢ࡮ࡳ࡭ࡳ࡫ࠧḩ")
    except Exception as e:
        logger.debug(bstack11l1l_opy_ (u"ࠣࡗࡱࡥࡧࡲࡥࠡࡶࡲࠤ࡬࡫ࡴࠡࡦ࡬ࡷࡹࡸ࡯ࠡࡱࡩࠤࡱ࡯࡮ࡶࡺࠥḪ") + e)
@measure(event_name=EVENTS.bstack11l1l11lll1_opy_, stage=STAGE.bstack1lll1l11l_opy_)
def bstack111lllllll1_opy_(bstack11l1111l11l_opy_, bstack111lll1ll1l_opy_):
    logger.debug(bstack11l1l_opy_ (u"ࠤࡇࡳࡼࡴ࡬ࡰࡣࡧ࡭ࡳ࡭ࠠࡔࡆࡎࠤࡧ࡯࡮ࡢࡴࡼࠤ࡫ࡸ࡯࡮࠼ࠣࠦḫ") + str(bstack11l1111l11l_opy_) + bstack11l1l_opy_ (u"ࠥࠦḬ"))
    zip_path = os.path.join(bstack111lll1ll1l_opy_, bstack11l1l_opy_ (u"ࠦࡩࡵࡷ࡯࡮ࡲࡥࡩ࡫ࡤࡠࡨ࡬ࡰࡪ࠴ࡺࡪࡲࠥḭ"))
    bstack111llll11ll_opy_ = bstack11l1l_opy_ (u"ࠬ࠭Ḯ")
    with requests.get(bstack11l1111l11l_opy_, stream=True) as response:
        response.raise_for_status()
        with open(zip_path, bstack11l1l_opy_ (u"ࠨࡷࡣࠤḯ")) as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
        logger.debug(bstack11l1l_opy_ (u"ࠢࡇ࡫࡯ࡩࠥࡪ࡯ࡸࡰ࡯ࡳࡦࡪࡥࡥࠢࡶࡹࡨࡩࡥࡴࡵࡩࡹࡱࡲࡹ࠯ࠤḰ"))
    with zipfile.ZipFile(zip_path, bstack11l1l_opy_ (u"ࠨࡴࠪḱ")) as zip_ref:
        bstack111ll1llll1_opy_ = zip_ref.namelist()
        if len(bstack111ll1llll1_opy_) > 0:
            bstack111llll11ll_opy_ = bstack111ll1llll1_opy_[0] # bstack111llll1lll_opy_ bstack11l11ll11ll_opy_ will be bstack11l11111l11_opy_ 1 file i.e. the binary in the zip
        zip_ref.extractall(bstack111lll1ll1l_opy_)
        logger.debug(bstack11l1l_opy_ (u"ࠤࡉ࡭ࡱ࡫ࡳࠡࡵࡸࡧࡨ࡫ࡳࡴࡨࡸࡰࡱࡿࠠࡦࡺࡷࡶࡦࡩࡴࡦࡦࠣࡸࡴࠦࠧࠣḲ") + str(bstack111lll1ll1l_opy_) + bstack11l1l_opy_ (u"ࠥࠫࠧḳ"))
    os.remove(zip_path)
    return bstack111llll11ll_opy_
def get_cli_dir():
    bstack111lllll1ll_opy_ = bstack1l1l1ll11l1_opy_()
    if bstack111lllll1ll_opy_:
        bstack1ll11llll1l_opy_ = os.path.join(bstack111lllll1ll_opy_, bstack11l1l_opy_ (u"ࠦࡨࡲࡩࠣḴ"))
        if not os.path.exists(bstack1ll11llll1l_opy_):
            os.makedirs(bstack1ll11llll1l_opy_, mode=0o777, exist_ok=True)
        return bstack1ll11llll1l_opy_
    else:
        raise FileNotFoundError(bstack11l1l_opy_ (u"ࠧࡔ࡯ࠡࡹࡵ࡭ࡹࡧࡢ࡭ࡧࠣࡨ࡮ࡸࡥࡤࡶࡲࡶࡾࠦࡡࡷࡣ࡬ࡰࡦࡨ࡬ࡦࠢࡩࡳࡷࠦࡴࡩࡧࠣࡗࡉࡑࠠࡣ࡫ࡱࡥࡷࡿ࠮ࠣḵ"))
def bstack1lll1l1lll1_opy_(bstack1ll11llll1l_opy_):
    bstack11l1l_opy_ (u"ࠨࠢࠣࡉࡨࡸࠥࡺࡨࡦࠢࡳࡥࡹ࡮ࠠࡧࡱࡵࠤࡹ࡮ࡥࠡࡄࡵࡳࡼࡹࡥࡳࡕࡷࡥࡨࡱࠠࡔࡆࡎࠤࡧ࡯࡮ࡢࡴࡼࠤ࡮ࡴࠠࡢࠢࡺࡶ࡮ࡺࡡࡣ࡮ࡨࠤࡩ࡯ࡲࡦࡥࡷࡳࡷࡿ࠮ࠣࠤࠥḶ")
    bstack111l1l11l1l_opy_ = [
        os.path.join(bstack1ll11llll1l_opy_, f)
        for f in os.listdir(bstack1ll11llll1l_opy_)
        if os.path.isfile(os.path.join(bstack1ll11llll1l_opy_, f)) and f.startswith(bstack11l1l_opy_ (u"ࠢࡣ࡫ࡱࡥࡷࡿ࠭ࠣḷ"))
    ]
    if len(bstack111l1l11l1l_opy_) > 0:
        return max(bstack111l1l11l1l_opy_, key=os.path.getmtime) # get bstack111l1ll111l_opy_ binary
    return bstack11l1l_opy_ (u"ࠣࠤḸ")
def bstack11ll11l1111_opy_():
  from selenium import webdriver
  return version.parse(webdriver.__version__)
def bstack1l1llll111l_opy_(d, u):
  for k, v in u.items():
    if isinstance(v, collections.abc.Mapping):
      d[k] = bstack1l1llll111l_opy_(d.get(k, {}), v)
    else:
      if isinstance(v, list):
        d[k] = d.get(k, []) + v
      else:
        d[k] = v
  return d
def bstack1l1l1ll1l_opy_(data, keys, default=None):
    bstack11l1l_opy_ (u"ࠤࠥࠦࠏࠦࠠࠡࠢࡖࡥ࡫࡫࡬ࡺࠢࡪࡩࡹࠦࡡࠡࡰࡨࡷࡹ࡫ࡤࠡࡸࡤࡰࡺ࡫ࠠࡧࡴࡲࡱࠥࡧࠠࡥ࡫ࡦࡸ࡮ࡵ࡮ࡢࡴࡼࠤࡴࡸࠠ࡭࡫ࡶࡸ࠳ࠐࠠࠡࠢࠣ࠾ࡵࡧࡲࡢ࡯ࠣࡨࡦࡺࡡ࠻ࠢࡗ࡬ࡪࠦࡤࡪࡥࡷ࡭ࡴࡴࡡࡳࡻࠣࡳࡷࠦ࡬ࡪࡵࡷࠤࡹࡵࠠࡵࡴࡤࡺࡪࡸࡳࡦ࠰ࠍࠤࠥࠦࠠ࠻ࡲࡤࡶࡦࡳࠠ࡬ࡧࡼࡷ࠿ࠦࡁࠡ࡮࡬ࡷࡹࠦ࡯ࡧࠢ࡮ࡩࡾࡹ࠯ࡪࡰࡧ࡭ࡨ࡫ࡳࠡࡴࡨࡴࡷ࡫ࡳࡦࡰࡷ࡭ࡳ࡭ࠠࡵࡪࡨࠤࡵࡧࡴࡩ࠰ࠍࠤࠥࠦࠠ࠻ࡲࡤࡶࡦࡳࠠࡥࡧࡩࡥࡺࡲࡴ࠻࡙ࠢࡥࡱࡻࡥࠡࡶࡲࠤࡷ࡫ࡴࡶࡴࡱࠤ࡮࡬ࠠࡵࡪࡨࠤࡵࡧࡴࡩࠢࡧࡳࡪࡹࠠ࡯ࡱࡷࠤࡪࡾࡩࡴࡶ࠱ࠎࠥࠦࠠࠡ࠼ࡵࡩࡹࡻࡲ࡯࠼ࠣࡘ࡭࡫ࠠࡷࡣ࡯ࡹࡪࠦࡡࡵࠢࡷ࡬ࡪࠦ࡮ࡦࡵࡷࡩࡩࠦࡰࡢࡶ࡫࠰ࠥࡵࡲࠡࡦࡨࡪࡦࡻ࡬ࡵࠢ࡬ࡪࠥࡴ࡯ࡵࠢࡩࡳࡺࡴࡤ࠯ࠌࠣࠤࠥࠦࠢࠣࠤḹ")
    if not data:
        return default
    current = data
    try:
        for key in keys:
            if isinstance(current, dict):
                current = current[key]
            elif isinstance(current, list) and isinstance(key, int):
                current = current[key]
            else:
                return default
        return current
    except (KeyError, IndexError, TypeError):
        return default
def bstack1lllll11ll_opy_(bstack11l111111ll_opy_, key, value):
    bstack11l1l_opy_ (u"ࠥࠦࠧࠐࠠࠡࠢࠣࡗࡹࡵࡲࡦࠢࡆࡐࡎࠦࡥ࡯ࡸ࡬ࡶࡴࡴ࡭ࡦࡰࡷࠤࡻࡧࡲࡪࡣࡥࡰࡪࡹࠠ࡮ࡣࡳࡴ࡮ࡴࡧࠡ࡫ࡱࠤࡹ࡮ࡥࠡࡲࡵࡳࡻ࡯ࡤࡦࡦࠣࡨ࡮ࡩࡴࡪࡱࡱࡥࡷࡿ࠮ࠋࠢࠣࠤࠥࡇࡲࡨࡵ࠽ࠎࠥࠦࠠࠡࠢࠣࠤࠥࡩ࡬ࡪࡡࡨࡲࡻࡥࡶࡢࡴࡶࡣࡲࡧࡰ࠻ࠢࡇ࡭ࡨࡺࡩࡰࡰࡤࡶࡾࠦࡴࡰࠢࡶࡸࡴࡸࡥࠡࡧࡱࡺ࡮ࡸ࡯࡯࡯ࡨࡲࡹࠦࡶࡢࡴ࡬ࡥࡧࡲࡥࠡ࡯ࡤࡴࡵ࡯࡮ࡨࡵࠍࠤࠥࠦࠠࠡࠢࠣࠤࡰ࡫ࡹ࠻ࠢࡎࡩࡾࠦࡦࡳࡱࡰࠤࡈࡒࡉࡠࡅࡄࡔࡘࡥࡔࡐࡡࡆࡓࡓࡌࡉࡈࠌࠣࠤࠥࠦࠠࠡࠢࠣࡺࡦࡲࡵࡦ࠼࡚ࠣࡦࡲࡵࡦࠢࡩࡶࡴࡳࠠࡤࡱࡰࡱࡦࡴࡤࠡ࡮࡬ࡲࡪࠦࡡࡳࡩࡸࡱࡪࡴࡴࡴࠌࠣࠤࠥࠦࠢࠣࠤḺ")
    if key in bstack11llll1l1_opy_:
        bstack1ll1ll1111_opy_ = bstack11llll1l1_opy_[key]
        if isinstance(bstack1ll1ll1111_opy_, list):
            for env_name in bstack1ll1ll1111_opy_:
                bstack11l111111ll_opy_[env_name] = value
        else:
            bstack11l111111ll_opy_[bstack1ll1ll1111_opy_] = value