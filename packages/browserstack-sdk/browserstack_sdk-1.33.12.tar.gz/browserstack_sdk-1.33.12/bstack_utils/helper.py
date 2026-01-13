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
from bstack_utils.constants import (bstack11llll1ll1_opy_, bstack111l1ll11_opy_, bstack11l1l11lll_opy_,
                                    bstack11l11lll1ll_opy_, bstack11l11ll1l1l_opy_, bstack11l11ll11ll_opy_, bstack11l1l1l1lll_opy_)
from bstack_utils.measure import measure
from bstack_utils.messages import bstack1ll111l11_opy_, bstack1l1llllll1_opy_
from bstack_utils.proxy import bstack1lllll1111_opy_, bstack11l1ll11l_opy_
from bstack_utils.constants import *
from bstack_utils import bstack111lll1l1_opy_
from bstack_utils.bstack111ll1l1ll_opy_ import bstack1111l1lll_opy_
from browserstack_sdk._version import __version__
bstack1l1l1ll1l_opy_ = Config.bstack1l1l1111_opy_()
logger = bstack111lll1l1_opy_.get_logger(__name__, bstack111lll1l1_opy_.bstack1l1ll1l1111_opy_())
bstack11ll111l1l_opy_ = bstack111lll1l1_opy_.bstack1l1l111l_opy_(__name__)
def bstack11ll11l11l1_opy_(config):
    return config[bstack11ll1_opy_ (u"ࠩࡸࡷࡪࡸࡎࡢ࡯ࡨࠫ᮵")]
def bstack11l1llll111_opy_(config):
    return config[bstack11ll1_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵࡎࡩࡾ࠭᮶")]
def bstack11l1llll_opy_():
    try:
        import playwright
        return True
    except ImportError:
        return False
def bstack111lll1l1l1_opy_(obj):
    values = []
    bstack111lll1111l_opy_ = re.compile(bstack11ll1_opy_ (u"ࡶࠧࡤࡃࡖࡕࡗࡓࡒࡥࡔࡂࡉࡢࡠࡩ࠱ࠤࠣ᮷"), re.I)
    for key in obj.keys():
        if bstack111lll1111l_opy_.match(key):
            values.append(obj[key])
    return values
def bstack111l1l1lll1_opy_(config):
    tags = []
    tags.extend(bstack111lll1l1l1_opy_(os.environ))
    tags.extend(bstack111lll1l1l1_opy_(config))
    return tags
def bstack111lllll111_opy_(markers):
    tags = []
    for marker in markers:
        tags.append(marker.name)
    return tags
def bstack111ll1lll1l_opy_(bstack111l1ll1l1l_opy_):
    if not bstack111l1ll1l1l_opy_:
        return bstack11ll1_opy_ (u"ࠬ࠭᮸")
    return bstack11ll1_opy_ (u"ࠨࡻࡾࠢࠫࡿࢂ࠯ࠢ᮹").format(bstack111l1ll1l1l_opy_.name, bstack111l1ll1l1l_opy_.email)
def bstack11ll111l1ll_opy_():
    try:
        repo = git.Repo(search_parent_directories=True)
        bstack111l1ll1ll1_opy_ = repo.common_dir
        info = {
            bstack11ll1_opy_ (u"ࠢࡴࡪࡤࠦᮺ"): repo.head.commit.hexsha,
            bstack11ll1_opy_ (u"ࠣࡵ࡫ࡳࡷࡺ࡟ࡴࡪࡤࠦᮻ"): repo.git.rev_parse(repo.head.commit, short=True),
            bstack11ll1_opy_ (u"ࠤࡥࡶࡦࡴࡣࡩࠤᮼ"): repo.active_branch.name,
            bstack11ll1_opy_ (u"ࠥࡸࡦ࡭ࠢᮽ"): repo.git.describe(all=True, tags=True, exact_match=True),
            bstack11ll1_opy_ (u"ࠦࡨࡵ࡭࡮࡫ࡷࡸࡪࡸࠢᮾ"): bstack111ll1lll1l_opy_(repo.head.commit.committer),
            bstack11ll1_opy_ (u"ࠧࡩ࡯࡮࡯࡬ࡸࡹ࡫ࡲࡠࡦࡤࡸࡪࠨᮿ"): repo.head.commit.committed_datetime.isoformat(),
            bstack11ll1_opy_ (u"ࠨࡡࡶࡶ࡫ࡳࡷࠨᯀ"): bstack111ll1lll1l_opy_(repo.head.commit.author),
            bstack11ll1_opy_ (u"ࠢࡢࡷࡷ࡬ࡴࡸ࡟ࡥࡣࡷࡩࠧᯁ"): repo.head.commit.authored_datetime.isoformat(),
            bstack11ll1_opy_ (u"ࠣࡥࡲࡱࡲ࡯ࡴࡠ࡯ࡨࡷࡸࡧࡧࡦࠤᯂ"): repo.head.commit.message,
            bstack11ll1_opy_ (u"ࠤࡵࡳࡴࡺࠢᯃ"): repo.git.rev_parse(bstack11ll1_opy_ (u"ࠥ࠱࠲ࡹࡨࡰࡹ࠰ࡸࡴࡶ࡬ࡦࡸࡨࡰࠧᯄ")),
            bstack11ll1_opy_ (u"ࠦࡨࡵ࡭࡮ࡱࡱࡣ࡬࡯ࡴࡠࡦ࡬ࡶࠧᯅ"): bstack111l1ll1ll1_opy_,
            bstack11ll1_opy_ (u"ࠧࡽ࡯ࡳ࡭ࡷࡶࡪ࡫࡟ࡨ࡫ࡷࡣࡩ࡯ࡲࠣᯆ"): subprocess.check_output([bstack11ll1_opy_ (u"ࠨࡧࡪࡶࠥᯇ"), bstack11ll1_opy_ (u"ࠢࡳࡧࡹ࠱ࡵࡧࡲࡴࡧࠥᯈ"), bstack11ll1_opy_ (u"ࠣ࠯࠰࡫࡮ࡺ࠭ࡤࡱࡰࡱࡴࡴ࠭ࡥ࡫ࡵࠦᯉ")]).strip().decode(
                bstack11ll1_opy_ (u"ࠩࡸࡸ࡫࠳࠸ࠨᯊ")),
            bstack11ll1_opy_ (u"ࠥࡰࡦࡹࡴࡠࡶࡤ࡫ࠧᯋ"): repo.git.describe(tags=True, abbrev=0, always=True),
            bstack11ll1_opy_ (u"ࠦࡨࡵ࡭࡮࡫ࡷࡷࡤࡹࡩ࡯ࡥࡨࡣࡱࡧࡳࡵࡡࡷࡥ࡬ࠨᯌ"): repo.git.rev_list(
                bstack11ll1_opy_ (u"ࠧࢁࡽ࠯࠰ࡾࢁࠧᯍ").format(repo.head.commit, repo.git.describe(tags=True, abbrev=0, always=True)), count=True)
        }
        remotes = repo.remotes
        bstack111lll111l1_opy_ = []
        for remote in remotes:
            bstack11l1111l1l1_opy_ = {
                bstack11ll1_opy_ (u"ࠨ࡮ࡢ࡯ࡨࠦᯎ"): remote.name,
                bstack11ll1_opy_ (u"ࠢࡶࡴ࡯ࠦᯏ"): remote.url,
            }
            bstack111lll111l1_opy_.append(bstack11l1111l1l1_opy_)
        bstack111ll1lll11_opy_ = {
            bstack11ll1_opy_ (u"ࠣࡰࡤࡱࡪࠨᯐ"): bstack11ll1_opy_ (u"ࠤࡪ࡭ࡹࠨᯑ"),
            **info,
            bstack11ll1_opy_ (u"ࠥࡶࡪࡳ࡯ࡵࡧࡶࠦᯒ"): bstack111lll111l1_opy_
        }
        bstack111ll1lll11_opy_ = bstack111l1ll1lll_opy_(bstack111ll1lll11_opy_)
        return bstack111ll1lll11_opy_
    except git.InvalidGitRepositoryError:
        return {}
    except Exception as err:
        print(bstack11ll1_opy_ (u"ࠦࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡪࡰࠣࡴࡴࡶࡵ࡭ࡣࡷ࡭ࡳ࡭ࠠࡈ࡫ࡷࠤࡲ࡫ࡴࡢࡦࡤࡸࡦࠦࡷࡪࡶ࡫ࠤࡪࡸࡲࡰࡴ࠽ࠤࢀࢃࠢᯓ").format(err))
        return {}
def bstack111lll11111_opy_(bstack111l1l111ll_opy_=None):
    bstack11ll1_opy_ (u"ࠧࠨࠢࠋࠢࠣࠤࠥࡍࡥࡵࠢࡪ࡭ࡹࠦ࡭ࡦࡶࡤࡨࡦࡺࡡࠡࡵࡳࡩࡨ࡯ࡦࡪࡥࡤࡰࡱࡿࠠࡧࡱࡵࡱࡦࡺࡴࡦࡦࠣࡪࡴࡸࠠࡂࡋࠣࡷࡪࡲࡥࡤࡶ࡬ࡳࡳࠦࡵࡴࡧࠣࡧࡦࡹࡥࡴࠢࡩࡳࡷࠦࡥࡢࡥ࡫ࠤ࡫ࡵ࡬ࡥࡧࡵࠤ࡮ࡴࠠࡵࡪࡨࠤࡱ࡯ࡳࡵ࠰ࠍࠤࠥࠦࠠࡂࡴࡪࡷ࠿ࠐࠠࠡࠢࠣࠤࠥࠦࠠࡧࡱ࡯ࡨࡪࡸࡳࠡࠪ࡯࡭ࡸࡺࠬࠡࡱࡳࡸ࡮ࡵ࡮ࡢ࡮ࠬ࠾ࠥࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤ࠲ࠦࡎࡰࡰࡨ࠾ࠥࡓ࡯࡯ࡱ࠰ࡶࡪࡶ࡯ࠡࡣࡳࡴࡷࡵࡡࡤࡪ࠯ࠤࡺࡹࡥࡴࠢࡦࡹࡷࡸࡥ࡯ࡶࠣࡨ࡮ࡸࡥࡤࡶࡲࡶࡾ࡛ࠦࡰࡵ࠱࡫ࡪࡺࡣࡸࡦࠫ࠭ࡢࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤ࠲ࠦࡅ࡮ࡲࡷࡽࠥࡲࡩࡴࡶࠣ࡟ࡢࡀࠠࡎࡷ࡯ࡸ࡮࠳ࡲࡦࡲࡲࠤࡦࡶࡰࡳࡱࡤࡧ࡭ࠦࡷࡪࡶ࡫ࠤࡳࡵࠠࡴࡱࡸࡶࡨ࡫ࡳࠡࡥࡲࡲ࡫࡯ࡧࡶࡴࡨࡨ࠱ࠦࡲࡦࡶࡸࡶࡳࡹࠠ࡜࡟ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡ࠯ࠣࡐ࡮ࡹࡴࠡࡱࡩࠤࡵࡧࡴࡩࡵ࠽ࠤࡒࡻ࡬ࡵ࡫࠰ࡶࡪࡶ࡯ࠡࡣࡳࡴࡷࡵࡡࡤࡪࠣࡻ࡮ࡺࡨࠡࡵࡳࡩࡨ࡯ࡦࡪࡥࠣࡪࡴࡲࡤࡦࡴࡶࠤࡹࡵࠠࡢࡰࡤࡰࡾࢀࡥࠋࠢࠣࠤࠥࡘࡥࡵࡷࡵࡲࡸࡀࠊࠡࠢࠣࠤࠥࠦࠠࠡ࡮࡬ࡷࡹࡀࠠࡍ࡫ࡶࡸࠥࡵࡦࠡࡦ࡬ࡧࡹࡹࠬࠡࡧࡤࡧ࡭ࠦࡣࡰࡰࡷࡥ࡮ࡴࡩ࡯ࡩࠣ࡫࡮ࡺࠠ࡮ࡧࡷࡥࡩࡧࡴࡢࠢࡩࡳࡷࠦࡡࠡࡨࡲࡰࡩ࡫ࡲ࠯ࠌࠣࠤࠥࠦࠢࠣࠤᯔ")
    if bstack111l1l111ll_opy_ is None:
        bstack111l1l111ll_opy_ = [os.getcwd()]
    elif isinstance(bstack111l1l111ll_opy_, list) and len(bstack111l1l111ll_opy_) == 0:
        return []
    results = []
    for folder in bstack111l1l111ll_opy_:
        try:
            if not os.path.exists(folder):
                raise Exception(bstack11ll1_opy_ (u"ࠨࡆࡰ࡮ࡧࡩࡷࠦࡤࡰࡧࡶࠤࡳࡵࡴࠡࡧࡻ࡭ࡸࡺ࠺ࠡࡽࢀࠦᯕ").format(folder))
            repo = git.Repo(folder, search_parent_directories=True)
            result = {
                bstack11ll1_opy_ (u"ࠢࡱࡴࡌࡨࠧᯖ"): bstack11ll1_opy_ (u"ࠣࠤᯗ"),
                bstack11ll1_opy_ (u"ࠤࡩ࡭ࡱ࡫ࡳࡄࡪࡤࡲ࡬࡫ࡤࠣᯘ"): [],
                bstack11ll1_opy_ (u"ࠥࡥࡺࡺࡨࡰࡴࡶࠦᯙ"): [],
                bstack11ll1_opy_ (u"ࠦࡵࡸࡄࡢࡶࡨࠦᯚ"): bstack11ll1_opy_ (u"ࠧࠨᯛ"),
                bstack11ll1_opy_ (u"ࠨࡣࡰ࡯ࡰ࡭ࡹࡓࡥࡴࡵࡤ࡫ࡪࡹࠢᯜ"): [],
                bstack11ll1_opy_ (u"ࠢࡱࡴࡗ࡭ࡹࡲࡥࠣᯝ"): bstack11ll1_opy_ (u"ࠣࠤᯞ"),
                bstack11ll1_opy_ (u"ࠤࡳࡶࡉ࡫ࡳࡤࡴ࡬ࡴࡹ࡯࡯࡯ࠤᯟ"): bstack11ll1_opy_ (u"ࠥࠦᯠ"),
                bstack11ll1_opy_ (u"ࠦࡵࡸࡒࡢࡹࡇ࡭࡫࡬ࠢᯡ"): bstack11ll1_opy_ (u"ࠧࠨᯢ")
            }
            bstack11l1111ll11_opy_ = repo.active_branch.name
            bstack111l1ll1111_opy_ = repo.head.commit
            result[bstack11ll1_opy_ (u"ࠨࡰࡳࡋࡧࠦᯣ")] = bstack111l1ll1111_opy_.hexsha
            bstack111ll11ll1l_opy_ = _111llll1l11_opy_(repo)
            logger.debug(bstack11ll1_opy_ (u"ࠢࡃࡣࡶࡩࠥࡨࡲࡢࡰࡦ࡬ࠥ࡬࡯ࡳࠢࡦࡳࡲࡶࡡࡳ࡫ࡶࡳࡳࡀࠠࠣᯤ") + str(bstack111ll11ll1l_opy_) + bstack11ll1_opy_ (u"ࠣࠤᯥ"))
            if bstack111ll11ll1l_opy_:
                try:
                    bstack111lll1lll1_opy_ = repo.git.diff(bstack11ll1_opy_ (u"ࠤ࠰࠱ࡳࡧ࡭ࡦ࠯ࡲࡲࡱࡿ᯦ࠢ"), bstack1l1ll111l1l_opy_ (u"ࠥࡿࡧࡧࡳࡦࡡࡥࡶࡦࡴࡣࡩࡿ࠱࠲࠳ࢁࡣࡶࡴࡵࡩࡳࡺ࡟ࡣࡴࡤࡲࡨ࡮ࡽࠣᯧ")).split(bstack11ll1_opy_ (u"ࠫࡡࡴࠧᯨ"))
                    logger.debug(bstack11ll1_opy_ (u"ࠧࡉࡨࡢࡰࡪࡩࡩࠦࡦࡪ࡮ࡨࡷࠥࡨࡥࡵࡹࡨࡩࡳࠦࡻࡣࡣࡶࡩࡤࡨࡲࡢࡰࡦ࡬ࢂࠦࡡ࡯ࡦࠣࡿࡨࡻࡲࡳࡧࡱࡸࡤࡨࡲࡢࡰࡦ࡬ࢂࡀࠠࠣᯩ") + str(bstack111lll1lll1_opy_) + bstack11ll1_opy_ (u"ࠨࠢᯪ"))
                    result[bstack11ll1_opy_ (u"ࠢࡧ࡫࡯ࡩࡸࡉࡨࡢࡰࡪࡩࡩࠨᯫ")] = [f.strip() for f in bstack111lll1lll1_opy_ if f.strip()]
                    commits = list(repo.iter_commits(bstack1l1ll111l1l_opy_ (u"ࠣࡽࡥࡥࡸ࡫࡟ࡣࡴࡤࡲࡨ࡮ࡽ࠯࠰ࡾࡧࡺࡸࡲࡦࡰࡷࡣࡧࡸࡡ࡯ࡥ࡫ࢁࠧᯬ")))
                except Exception:
                    logger.debug(bstack11ll1_opy_ (u"ࠤࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥ࡭ࡥࡵࠢࡦ࡬ࡦࡴࡧࡦࡦࠣࡪ࡮ࡲࡥࡴࠢࡩࡶࡴࡳࠠࡣࡴࡤࡲࡨ࡮ࠠࡤࡱࡰࡴࡦࡸࡩࡴࡱࡱ࠲ࠥࡌࡡ࡭࡮࡬ࡲ࡬ࠦࡢࡢࡥ࡮ࠤࡹࡵࠠࡳࡧࡦࡩࡳࡺࠠࡤࡱࡰࡱ࡮ࡺࡳ࠯ࠤᯭ"))
                    commits = list(repo.iter_commits(max_count=10))
                    if commits:
                        result[bstack11ll1_opy_ (u"ࠥࡪ࡮ࡲࡥࡴࡅ࡫ࡥࡳ࡭ࡥࡥࠤᯮ")] = _111l1l1l111_opy_(commits[:5])
            else:
                commits = list(repo.iter_commits(max_count=10))
                if commits:
                    result[bstack11ll1_opy_ (u"ࠦ࡫࡯࡬ࡦࡵࡆ࡬ࡦࡴࡧࡦࡦࠥᯯ")] = _111l1l1l111_opy_(commits[:5])
            bstack111ll111l11_opy_ = set()
            bstack111ll1lllll_opy_ = []
            for commit in commits:
                logger.debug(bstack11ll1_opy_ (u"ࠧࡖࡲࡰࡥࡨࡷࡸ࡯࡮ࡨࠢࡦࡳࡲࡳࡩࡵ࠼ࠣࠦᯰ") + str(commit.message) + bstack11ll1_opy_ (u"ࠨࠢᯱ"))
                bstack111ll1l11l1_opy_ = commit.author.name if commit.author else bstack11ll1_opy_ (u"ࠢࡖࡰ࡮ࡲࡴࡽ࡮᯲ࠣ")
                bstack111ll111l11_opy_.add(bstack111ll1l11l1_opy_)
                bstack111ll1lllll_opy_.append({
                    bstack11ll1_opy_ (u"ࠣ࡯ࡨࡷࡸࡧࡧࡦࠤ᯳"): commit.message.strip(),
                    bstack11ll1_opy_ (u"ࠤࡸࡷࡪࡸࠢ᯴"): bstack111ll1l11l1_opy_
                })
            result[bstack11ll1_opy_ (u"ࠥࡥࡺࡺࡨࡰࡴࡶࠦ᯵")] = list(bstack111ll111l11_opy_)
            result[bstack11ll1_opy_ (u"ࠦࡨࡵ࡭࡮࡫ࡷࡑࡪࡹࡳࡢࡩࡨࡷࠧ᯶")] = bstack111ll1lllll_opy_
            result[bstack11ll1_opy_ (u"ࠧࡶࡲࡅࡣࡷࡩࠧ᯷")] = bstack111l1ll1111_opy_.committed_datetime.strftime(bstack11ll1_opy_ (u"ࠨ࡚ࠥ࠯ࠨࡱ࠲ࠫࡤࠣ᯸"))
            if (not result[bstack11ll1_opy_ (u"ࠢࡱࡴࡗ࡭ࡹࡲࡥࠣ᯹")] or result[bstack11ll1_opy_ (u"ࠣࡲࡵࡘ࡮ࡺ࡬ࡦࠤ᯺")].strip() == bstack11ll1_opy_ (u"ࠤࠥ᯻")) and bstack111l1ll1111_opy_.message:
                bstack11l111l1111_opy_ = bstack111l1ll1111_opy_.message.strip().splitlines()
                result[bstack11ll1_opy_ (u"ࠥࡴࡷ࡚ࡩࡵ࡮ࡨࠦ᯼")] = bstack11l111l1111_opy_[0] if bstack11l111l1111_opy_ else bstack11ll1_opy_ (u"ࠦࠧ᯽")
                if len(bstack11l111l1111_opy_) > 2:
                    result[bstack11ll1_opy_ (u"ࠧࡶࡲࡅࡧࡶࡧࡷ࡯ࡰࡵ࡫ࡲࡲࠧ᯾")] = bstack11ll1_opy_ (u"࠭࡜࡯ࠩ᯿").join(bstack11l111l1111_opy_[2:]).strip()
            results.append(result)
        except Exception as err:
            logger.error(bstack11ll1_opy_ (u"ࠢࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣ࡭ࡳࠦࡰࡰࡲࡸࡰࡦࡺࡩ࡯ࡩࠣࡋ࡮ࡺࠠ࡮ࡧࡷࡥࡩࡧࡴࡢࠢࡩࡳࡷࠦࡁࡊࠢࡶࡩࡱ࡫ࡣࡵ࡫ࡲࡲࠥ࠮ࡦࡰ࡮ࡧࡩࡷࡀࠠࡼࡿࠬ࠾ࠥࢁࡽࠡ࠯ࠣࡿࢂࠨᰀ").format(
                folder,
                type(err).__name__,
                str(err)
            ))
    filtered_results = [
        result
        for result in results
        if _111l1lll1l1_opy_(result)
    ]
    return filtered_results
def _111l1lll1l1_opy_(result):
    bstack11ll1_opy_ (u"ࠣࠤࠥࠎࠥࠦࠠࠡࡊࡨࡰࡵ࡫ࡲࠡࡶࡲࠤࡨ࡮ࡥࡤ࡭ࠣ࡭࡫ࠦࡡࠡࡩ࡬ࡸࠥࡳࡥࡵࡣࡧࡥࡹࡧࠠࡳࡧࡶࡹࡱࡺࠠࡪࡵࠣࡺࡦࡲࡩࡥࠢࠫࡲࡴࡴ࠭ࡦ࡯ࡳࡸࡾࠦࡦࡪ࡮ࡨࡷࡈ࡮ࡡ࡯ࡩࡨࡨࠥࡧ࡮ࡥࠢࡤࡹࡹ࡮࡯ࡳࡵࠬ࠲ࠏࠦࠠࠡࠢࠥࠦࠧᰁ")
    return (
        isinstance(result.get(bstack11ll1_opy_ (u"ࠤࡩ࡭ࡱ࡫ࡳࡄࡪࡤࡲ࡬࡫ࡤࠣᰂ"), None), list)
        and len(result[bstack11ll1_opy_ (u"ࠥࡪ࡮ࡲࡥࡴࡅ࡫ࡥࡳ࡭ࡥࡥࠤᰃ")]) > 0
        and isinstance(result.get(bstack11ll1_opy_ (u"ࠦࡦࡻࡴࡩࡱࡵࡷࠧᰄ"), None), list)
        and len(result[bstack11ll1_opy_ (u"ࠧࡧࡵࡵࡪࡲࡶࡸࠨᰅ")]) > 0
    )
def _111llll1l11_opy_(repo):
    bstack11ll1_opy_ (u"ࠨࠢࠣࠌࠣࠤࠥࠦࡔࡳࡻࠣࡸࡴࠦࡤࡦࡶࡨࡶࡲ࡯࡮ࡦࠢࡷ࡬ࡪࠦࡢࡢࡵࡨࠤࡧࡸࡡ࡯ࡥ࡫ࠤ࡫ࡵࡲࠡࡶ࡫ࡩࠥ࡭ࡩࡷࡧࡱࠤࡷ࡫ࡰࡰࠢࡺ࡭ࡹ࡮࡯ࡶࡶࠣ࡬ࡦࡸࡤࡤࡱࡧࡩࡩࠦ࡮ࡢ࡯ࡨࡷࠥࡧ࡮ࡥࠢࡺࡳࡷࡱࠠࡸ࡫ࡷ࡬ࠥࡧ࡬࡭࡙ࠢࡇࡘࠦࡰࡳࡱࡹ࡭ࡩ࡫ࡲࡴ࠰ࠍࠤࠥࠦࠠࡓࡧࡷࡹࡷࡴࡳࠡࡶ࡫ࡩࠥࡪࡥࡧࡣࡸࡰࡹࠦࡢࡳࡣࡱࡧ࡭ࠦࡩࡧࠢࡳࡳࡸࡹࡩࡣ࡮ࡨ࠰ࠥ࡫࡬ࡴࡧࠣࡒࡴࡴࡥ࠯ࠌࠣࠤࠥࠦࠢࠣࠤᰆ")
    try:
        try:
            origin = repo.remotes.origin
            bstack111ll111l1l_opy_ = origin.refs[bstack11ll1_opy_ (u"ࠧࡉࡇࡄࡈࠬᰇ")]
            target = bstack111ll111l1l_opy_.reference.name
            if target.startswith(bstack11ll1_opy_ (u"ࠨࡱࡵ࡭࡬࡯࡮࠰ࠩᰈ")):
                return target
        except Exception:
            pass
        if repo.remotes and repo.remotes.origin.refs:
            for ref in repo.remotes.origin.refs:
                if ref.name.startswith(bstack11ll1_opy_ (u"ࠩࡲࡶ࡮࡭ࡩ࡯࠱ࠪᰉ")):
                    return ref.name
        if repo.heads:
            return repo.heads[0].name
    except Exception:
        pass
    return None
def _111l1l1l111_opy_(commits):
    bstack11ll1_opy_ (u"ࠥࠦࠧࠐࠠࠡࠢࠣࡋࡪࡺࠠ࡭࡫ࡶࡸࠥࡵࡦࠡࡥ࡫ࡥࡳ࡭ࡥࡥࠢࡩ࡭ࡱ࡫ࡳࠡࡨࡵࡳࡲࠦࡡࠡ࡮࡬ࡷࡹࠦ࡯ࡧࠢࡦࡳࡲࡳࡩࡵࡵ࠱ࠎࠥࠦࠠࠡࠤࠥࠦᰊ")
    bstack111lll1lll1_opy_ = set()
    try:
        for commit in commits:
            if commit.parents:
                for parent in commit.parents:
                    diff = commit.diff(parent)
                    for bstack11l11111lll_opy_ in diff:
                        if bstack11l11111lll_opy_.a_path:
                            bstack111lll1lll1_opy_.add(bstack11l11111lll_opy_.a_path)
                        if bstack11l11111lll_opy_.b_path:
                            bstack111lll1lll1_opy_.add(bstack11l11111lll_opy_.b_path)
    except Exception:
        pass
    return list(bstack111lll1lll1_opy_)
def bstack111l1ll1lll_opy_(bstack111ll1lll11_opy_):
    bstack11l111l11ll_opy_ = bstack111lll11lll_opy_(bstack111ll1lll11_opy_)
    if bstack11l111l11ll_opy_ and bstack11l111l11ll_opy_ > bstack11l11lll1ll_opy_:
        bstack111l1l1l11l_opy_ = bstack11l111l11ll_opy_ - bstack11l11lll1ll_opy_
        bstack11l11111ll1_opy_ = bstack111ll11lll1_opy_(bstack111ll1lll11_opy_[bstack11ll1_opy_ (u"ࠦࡨࡵ࡭࡮࡫ࡷࡣࡲ࡫ࡳࡴࡣࡪࡩࠧᰋ")], bstack111l1l1l11l_opy_)
        bstack111ll1lll11_opy_[bstack11ll1_opy_ (u"ࠧࡩ࡯࡮࡯࡬ࡸࡤࡳࡥࡴࡵࡤ࡫ࡪࠨᰌ")] = bstack11l11111ll1_opy_
        logger.info(bstack11ll1_opy_ (u"ࠨࡔࡩࡧࠣࡧࡴࡳ࡭ࡪࡶࠣ࡬ࡦࡹࠠࡣࡧࡨࡲࠥࡺࡲࡶࡰࡦࡥࡹ࡫ࡤ࠯ࠢࡖ࡭ࡿ࡫ࠠࡰࡨࠣࡧࡴࡳ࡭ࡪࡶࠣࡥ࡫ࡺࡥࡳࠢࡷࡶࡺࡴࡣࡢࡶ࡬ࡳࡳࠦࡩࡴࠢࡾࢁࠥࡑࡂࠣᰍ")
                    .format(bstack111lll11lll_opy_(bstack111ll1lll11_opy_) / 1024))
    return bstack111ll1lll11_opy_
def bstack111lll11lll_opy_(bstack11ll1111l_opy_):
    try:
        if bstack11ll1111l_opy_:
            bstack111llll11ll_opy_ = json.dumps(bstack11ll1111l_opy_)
            bstack111l1llll11_opy_ = sys.getsizeof(bstack111llll11ll_opy_)
            return bstack111l1llll11_opy_
    except Exception as e:
        logger.debug(bstack11ll1_opy_ (u"ࠢࡔࡱࡰࡩࡹ࡮ࡩ࡯ࡩࠣࡻࡪࡴࡴࠡࡹࡵࡳࡳ࡭ࠠࡸࡪ࡬ࡰࡪࠦࡣࡢ࡮ࡦࡹࡱࡧࡴࡪࡰࡪࠤࡸ࡯ࡺࡦࠢࡲࡪࠥࡐࡓࡐࡐࠣࡳࡧࡰࡥࡤࡶ࠽ࠤࢀࢃࠢᰎ").format(e))
    return -1
def bstack111ll11lll1_opy_(field, bstack111ll11l11l_opy_):
    try:
        bstack111llll111l_opy_ = len(bytes(bstack11l11ll1l1l_opy_, bstack11ll1_opy_ (u"ࠨࡷࡷࡪ࠲࠾ࠧᰏ")))
        bstack11l111l1l1l_opy_ = bytes(field, bstack11ll1_opy_ (u"ࠩࡸࡸ࡫࠳࠸ࠨᰐ"))
        bstack111lll11ll1_opy_ = len(bstack11l111l1l1l_opy_)
        bstack111ll111111_opy_ = ceil(bstack111lll11ll1_opy_ - bstack111ll11l11l_opy_ - bstack111llll111l_opy_)
        if bstack111ll111111_opy_ > 0:
            bstack111lll1l11l_opy_ = bstack11l111l1l1l_opy_[:bstack111ll111111_opy_].decode(bstack11ll1_opy_ (u"ࠪࡹࡹ࡬࠭࠹ࠩᰑ"), errors=bstack11ll1_opy_ (u"ࠫ࡮࡭࡮ࡰࡴࡨࠫᰒ")) + bstack11l11ll1l1l_opy_
            return bstack111lll1l11l_opy_
    except Exception as e:
        logger.debug(bstack11ll1_opy_ (u"ࠧࡋࡲࡳࡱࡵࠤࡼ࡮ࡩ࡭ࡧࠣࡸࡷࡻ࡮ࡤࡣࡷ࡭ࡳ࡭ࠠࡧ࡫ࡨࡰࡩ࠲ࠠ࡯ࡱࡷ࡬࡮ࡴࡧࠡࡹࡤࡷࠥࡺࡲࡶࡰࡦࡥࡹ࡫ࡤࠡࡪࡨࡶࡪࡀࠠࡼࡿࠥᰓ").format(e))
    return field
def bstack1lll11llll_opy_():
    env = os.environ
    if (bstack11ll1_opy_ (u"ࠨࡊࡆࡐࡎࡍࡓ࡙࡟ࡖࡔࡏࠦᰔ") in env and len(env[bstack11ll1_opy_ (u"ࠢࡋࡇࡑࡏࡎࡔࡓࡠࡗࡕࡐࠧᰕ")]) > 0) or (
            bstack11ll1_opy_ (u"ࠣࡌࡈࡒࡐࡏࡎࡔࡡࡋࡓࡒࡋࠢᰖ") in env and len(env[bstack11ll1_opy_ (u"ࠤࡍࡉࡓࡑࡉࡏࡕࡢࡌࡔࡓࡅࠣᰗ")]) > 0):
        return {
            bstack11ll1_opy_ (u"ࠥࡲࡦࡳࡥࠣᰘ"): bstack11ll1_opy_ (u"ࠦࡏ࡫࡮࡬࡫ࡱࡷࠧᰙ"),
            bstack11ll1_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡺࡸ࡬ࠣᰚ"): env.get(bstack11ll1_opy_ (u"ࠨࡂࡖࡋࡏࡈࡤ࡛ࡒࡍࠤᰛ")),
            bstack11ll1_opy_ (u"ࠢ࡫ࡱࡥࡣࡳࡧ࡭ࡦࠤᰜ"): env.get(bstack11ll1_opy_ (u"ࠣࡌࡒࡆࡤࡔࡁࡎࡇࠥᰝ")),
            bstack11ll1_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡰࡸࡱࡧ࡫ࡲࠣᰞ"): env.get(bstack11ll1_opy_ (u"ࠥࡆ࡚ࡏࡌࡅࡡࡑ࡙ࡒࡈࡅࡓࠤᰟ"))
        }
    if env.get(bstack11ll1_opy_ (u"ࠦࡈࡏࠢᰠ")) == bstack11ll1_opy_ (u"ࠧࡺࡲࡶࡧࠥᰡ") and bstack1111lll1_opy_(env.get(bstack11ll1_opy_ (u"ࠨࡃࡊࡔࡆࡐࡊࡉࡉࠣᰢ"))):
        return {
            bstack11ll1_opy_ (u"ࠢ࡯ࡣࡰࡩࠧᰣ"): bstack11ll1_opy_ (u"ࠣࡅ࡬ࡶࡨࡲࡥࡄࡋࠥᰤ"),
            bstack11ll1_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡷࡵࡰࠧᰥ"): env.get(bstack11ll1_opy_ (u"ࠥࡇࡎࡘࡃࡍࡇࡢࡆ࡚ࡏࡌࡅࡡࡘࡖࡑࠨᰦ")),
            bstack11ll1_opy_ (u"ࠦ࡯ࡵࡢࡠࡰࡤࡱࡪࠨᰧ"): env.get(bstack11ll1_opy_ (u"ࠧࡉࡉࡓࡅࡏࡉࡤࡐࡏࡃࠤᰨ")),
            bstack11ll1_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡴࡵ࡮ࡤࡨࡶࠧᰩ"): env.get(bstack11ll1_opy_ (u"ࠢࡄࡋࡕࡇࡑࡋ࡟ࡃࡗࡌࡐࡉࡥࡎࡖࡏࠥᰪ"))
        }
    if env.get(bstack11ll1_opy_ (u"ࠣࡅࡌࠦᰫ")) == bstack11ll1_opy_ (u"ࠤࡷࡶࡺ࡫ࠢᰬ") and bstack1111lll1_opy_(env.get(bstack11ll1_opy_ (u"ࠥࡘࡗࡇࡖࡊࡕࠥᰭ"))):
        return {
            bstack11ll1_opy_ (u"ࠦࡳࡧ࡭ࡦࠤᰮ"): bstack11ll1_opy_ (u"࡚ࠧࡲࡢࡸ࡬ࡷࠥࡉࡉࠣᰯ"),
            bstack11ll1_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡻࡲ࡭ࠤᰰ"): env.get(bstack11ll1_opy_ (u"ࠢࡕࡔࡄ࡚ࡎ࡙࡟ࡃࡗࡌࡐࡉࡥࡗࡆࡄࡢ࡙ࡗࡒࠢᰱ")),
            bstack11ll1_opy_ (u"ࠣ࡬ࡲࡦࡤࡴࡡ࡮ࡧࠥᰲ"): env.get(bstack11ll1_opy_ (u"ࠤࡗࡖࡆ࡜ࡉࡔࡡࡍࡓࡇࡥࡎࡂࡏࡈࠦᰳ")),
            bstack11ll1_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡱࡹࡲࡨࡥࡳࠤᰴ"): env.get(bstack11ll1_opy_ (u"࡙ࠦࡘࡁࡗࡋࡖࡣࡇ࡛ࡉࡍࡆࡢࡒ࡚ࡓࡂࡆࡔࠥᰵ"))
        }
    if env.get(bstack11ll1_opy_ (u"ࠧࡉࡉࠣᰶ")) == bstack11ll1_opy_ (u"ࠨࡴࡳࡷࡨ᰷ࠦ") and env.get(bstack11ll1_opy_ (u"ࠢࡄࡋࡢࡒࡆࡓࡅࠣ᰸")) == bstack11ll1_opy_ (u"ࠣࡥࡲࡨࡪࡹࡨࡪࡲࠥ᰹"):
        return {
            bstack11ll1_opy_ (u"ࠤࡱࡥࡲ࡫ࠢ᰺"): bstack11ll1_opy_ (u"ࠥࡇࡴࡪࡥࡴࡪ࡬ࡴࠧ᰻"),
            bstack11ll1_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡹࡷࡲࠢ᰼"): None,
            bstack11ll1_opy_ (u"ࠧࡰ࡯ࡣࡡࡱࡥࡲ࡫ࠢ᰽"): None,
            bstack11ll1_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡴࡵ࡮ࡤࡨࡶࠧ᰾"): None
        }
    if env.get(bstack11ll1_opy_ (u"ࠢࡃࡋࡗࡆ࡚ࡉࡋࡆࡖࡢࡆࡗࡇࡎࡄࡊࠥ᰿")) and env.get(bstack11ll1_opy_ (u"ࠣࡄࡌࡘࡇ࡛ࡃࡌࡇࡗࡣࡈࡕࡍࡎࡋࡗࠦ᱀")):
        return {
            bstack11ll1_opy_ (u"ࠤࡱࡥࡲ࡫ࠢ᱁"): bstack11ll1_opy_ (u"ࠥࡆ࡮ࡺࡢࡶࡥ࡮ࡩࡹࠨ᱂"),
            bstack11ll1_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡹࡷࡲࠢ᱃"): env.get(bstack11ll1_opy_ (u"ࠧࡈࡉࡕࡄࡘࡇࡐࡋࡔࡠࡉࡌࡘࡤࡎࡔࡕࡒࡢࡓࡗࡏࡇࡊࡐࠥ᱄")),
            bstack11ll1_opy_ (u"ࠨࡪࡰࡤࡢࡲࡦࡳࡥࠣ᱅"): None,
            bstack11ll1_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥ࡮ࡶ࡯ࡥࡩࡷࠨ᱆"): env.get(bstack11ll1_opy_ (u"ࠣࡄࡌࡘࡇ࡛ࡃࡌࡇࡗࡣࡇ࡛ࡉࡍࡆࡢࡒ࡚ࡓࡂࡆࡔࠥ᱇"))
        }
    if env.get(bstack11ll1_opy_ (u"ࠤࡆࡍࠧ᱈")) == bstack11ll1_opy_ (u"ࠥࡸࡷࡻࡥࠣ᱉") and bstack1111lll1_opy_(env.get(bstack11ll1_opy_ (u"ࠦࡉࡘࡏࡏࡇࠥ᱊"))):
        return {
            bstack11ll1_opy_ (u"ࠧࡴࡡ࡮ࡧࠥ᱋"): bstack11ll1_opy_ (u"ࠨࡄࡳࡱࡱࡩࠧ᱌"),
            bstack11ll1_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥࡵࡳ࡮ࠥᱍ"): env.get(bstack11ll1_opy_ (u"ࠣࡆࡕࡓࡓࡋ࡟ࡃࡗࡌࡐࡉࡥࡌࡊࡐࡎࠦᱎ")),
            bstack11ll1_opy_ (u"ࠤ࡭ࡳࡧࡥ࡮ࡢ࡯ࡨࠦᱏ"): None,
            bstack11ll1_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡱࡹࡲࡨࡥࡳࠤ᱐"): env.get(bstack11ll1_opy_ (u"ࠦࡉࡘࡏࡏࡇࡢࡆ࡚ࡏࡌࡅࡡࡑ࡙ࡒࡈࡅࡓࠤ᱑"))
        }
    if env.get(bstack11ll1_opy_ (u"ࠧࡉࡉࠣ᱒")) == bstack11ll1_opy_ (u"ࠨࡴࡳࡷࡨࠦ᱓") and bstack1111lll1_opy_(env.get(bstack11ll1_opy_ (u"ࠢࡔࡇࡐࡅࡕࡎࡏࡓࡇࠥ᱔"))):
        return {
            bstack11ll1_opy_ (u"ࠣࡰࡤࡱࡪࠨ᱕"): bstack11ll1_opy_ (u"ࠤࡖࡩࡲࡧࡰࡩࡱࡵࡩࠧ᱖"),
            bstack11ll1_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡸࡶࡱࠨ᱗"): env.get(bstack11ll1_opy_ (u"ࠦࡘࡋࡍࡂࡒࡋࡓࡗࡋ࡟ࡐࡔࡊࡅࡓࡏ࡚ࡂࡖࡌࡓࡓࡥࡕࡓࡎࠥ᱘")),
            bstack11ll1_opy_ (u"ࠧࡰ࡯ࡣࡡࡱࡥࡲ࡫ࠢ᱙"): env.get(bstack11ll1_opy_ (u"ࠨࡓࡆࡏࡄࡔࡍࡕࡒࡆࡡࡍࡓࡇࡥࡎࡂࡏࡈࠦᱚ")),
            bstack11ll1_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥ࡮ࡶ࡯ࡥࡩࡷࠨᱛ"): env.get(bstack11ll1_opy_ (u"ࠣࡕࡈࡑࡆࡖࡈࡐࡔࡈࡣࡏࡕࡂࡠࡋࡇࠦᱜ"))
        }
    if env.get(bstack11ll1_opy_ (u"ࠤࡆࡍࠧᱝ")) == bstack11ll1_opy_ (u"ࠥࡸࡷࡻࡥࠣᱞ") and bstack1111lll1_opy_(env.get(bstack11ll1_opy_ (u"ࠦࡌࡏࡔࡍࡃࡅࡣࡈࡏࠢᱟ"))):
        return {
            bstack11ll1_opy_ (u"ࠧࡴࡡ࡮ࡧࠥᱠ"): bstack11ll1_opy_ (u"ࠨࡇࡪࡶࡏࡥࡧࠨᱡ"),
            bstack11ll1_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥࡵࡳ࡮ࠥᱢ"): env.get(bstack11ll1_opy_ (u"ࠣࡅࡌࡣࡏࡕࡂࡠࡗࡕࡐࠧᱣ")),
            bstack11ll1_opy_ (u"ࠤ࡭ࡳࡧࡥ࡮ࡢ࡯ࡨࠦᱤ"): env.get(bstack11ll1_opy_ (u"ࠥࡇࡎࡥࡊࡐࡄࡢࡒࡆࡓࡅࠣᱥ")),
            bstack11ll1_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡲࡺࡳࡢࡦࡴࠥᱦ"): env.get(bstack11ll1_opy_ (u"ࠧࡉࡉࡠࡌࡒࡆࡤࡏࡄࠣᱧ"))
        }
    if env.get(bstack11ll1_opy_ (u"ࠨࡃࡊࠤᱨ")) == bstack11ll1_opy_ (u"ࠢࡵࡴࡸࡩࠧᱩ") and bstack1111lll1_opy_(env.get(bstack11ll1_opy_ (u"ࠣࡄࡘࡍࡑࡊࡋࡊࡖࡈࠦᱪ"))):
        return {
            bstack11ll1_opy_ (u"ࠤࡱࡥࡲ࡫ࠢᱫ"): bstack11ll1_opy_ (u"ࠥࡆࡺ࡯࡬ࡥ࡭࡬ࡸࡪࠨᱬ"),
            bstack11ll1_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡹࡷࡲࠢᱭ"): env.get(bstack11ll1_opy_ (u"ࠧࡈࡕࡊࡎࡇࡏࡎ࡚ࡅࡠࡄࡘࡍࡑࡊ࡟ࡖࡔࡏࠦᱮ")),
            bstack11ll1_opy_ (u"ࠨࡪࡰࡤࡢࡲࡦࡳࡥࠣᱯ"): env.get(bstack11ll1_opy_ (u"ࠢࡃࡗࡌࡐࡉࡑࡉࡕࡇࡢࡐࡆࡈࡅࡍࠤᱰ")) or env.get(bstack11ll1_opy_ (u"ࠣࡄࡘࡍࡑࡊࡋࡊࡖࡈࡣࡕࡏࡐࡆࡎࡌࡒࡊࡥࡎࡂࡏࡈࠦᱱ")),
            bstack11ll1_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡰࡸࡱࡧ࡫ࡲࠣᱲ"): env.get(bstack11ll1_opy_ (u"ࠥࡆ࡚ࡏࡌࡅࡍࡌࡘࡊࡥࡂࡖࡋࡏࡈࡤࡔࡕࡎࡄࡈࡖࠧᱳ"))
        }
    if bstack1111lll1_opy_(env.get(bstack11ll1_opy_ (u"࡙ࠦࡌ࡟ࡃࡗࡌࡐࡉࠨᱴ"))):
        return {
            bstack11ll1_opy_ (u"ࠧࡴࡡ࡮ࡧࠥᱵ"): bstack11ll1_opy_ (u"ࠨࡖࡪࡵࡸࡥࡱࠦࡓࡵࡷࡧ࡭ࡴࠦࡔࡦࡣࡰࠤࡘ࡫ࡲࡷ࡫ࡦࡩࡸࠨᱶ"),
            bstack11ll1_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥࡵࡳ࡮ࠥᱷ"): bstack11ll1_opy_ (u"ࠣࡽࢀࡿࢂࠨᱸ").format(env.get(bstack11ll1_opy_ (u"ࠩࡖ࡝ࡘ࡚ࡅࡎࡡࡗࡉࡆࡓࡆࡐࡗࡑࡈࡆ࡚ࡉࡐࡐࡖࡉࡗ࡜ࡅࡓࡗࡕࡍࠬᱹ")), env.get(bstack11ll1_opy_ (u"ࠪࡗ࡞࡙ࡔࡆࡏࡢࡘࡊࡇࡍࡑࡔࡒࡎࡊࡉࡔࡊࡆࠪᱺ"))),
            bstack11ll1_opy_ (u"ࠦ࡯ࡵࡢࡠࡰࡤࡱࡪࠨᱻ"): env.get(bstack11ll1_opy_ (u"࡙࡙ࠧࡔࡖࡈࡑࡤࡊࡅࡇࡋࡑࡍ࡙ࡏࡏࡏࡋࡇࠦᱼ")),
            bstack11ll1_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡴࡵ࡮ࡤࡨࡶࠧᱽ"): env.get(bstack11ll1_opy_ (u"ࠢࡃࡗࡌࡐࡉࡥࡂࡖࡋࡏࡈࡎࡊࠢ᱾"))
        }
    if bstack1111lll1_opy_(env.get(bstack11ll1_opy_ (u"ࠣࡃࡓࡔ࡛ࡋ࡙ࡐࡔࠥ᱿"))):
        return {
            bstack11ll1_opy_ (u"ࠤࡱࡥࡲ࡫ࠢᲀ"): bstack11ll1_opy_ (u"ࠥࡅࡵࡶࡶࡦࡻࡲࡶࠧᲁ"),
            bstack11ll1_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡹࡷࡲࠢᲂ"): bstack11ll1_opy_ (u"ࠧࢁࡽ࠰ࡲࡵࡳ࡯࡫ࡣࡵ࠱ࡾࢁ࠴ࢁࡽ࠰ࡤࡸ࡭ࡱࡪࡳ࠰ࡽࢀࠦᲃ").format(env.get(bstack11ll1_opy_ (u"࠭ࡁࡑࡒ࡙ࡉ࡞ࡕࡒࡠࡗࡕࡐࠬᲄ")), env.get(bstack11ll1_opy_ (u"ࠧࡂࡒࡓ࡚ࡊ࡟ࡏࡓࡡࡄࡇࡈࡕࡕࡏࡖࡢࡒࡆࡓࡅࠨᲅ")), env.get(bstack11ll1_opy_ (u"ࠨࡃࡓࡔ࡛ࡋ࡙ࡐࡔࡢࡔࡗࡕࡊࡆࡅࡗࡣࡘࡒࡕࡈࠩᲆ")), env.get(bstack11ll1_opy_ (u"ࠩࡄࡔࡕ࡜ࡅ࡚ࡑࡕࡣࡇ࡛ࡉࡍࡆࡢࡍࡉ࠭ᲇ"))),
            bstack11ll1_opy_ (u"ࠥ࡮ࡴࡨ࡟࡯ࡣࡰࡩࠧᲈ"): env.get(bstack11ll1_opy_ (u"ࠦࡆࡖࡐࡗࡇ࡜ࡓࡗࡥࡊࡐࡄࡢࡒࡆࡓࡅࠣᲉ")),
            bstack11ll1_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡳࡻ࡭ࡣࡧࡵࠦᲊ"): env.get(bstack11ll1_opy_ (u"ࠨࡁࡑࡒ࡙ࡉ࡞ࡕࡒࡠࡄࡘࡍࡑࡊ࡟ࡏࡗࡐࡆࡊࡘࠢ᲋"))
        }
    if env.get(bstack11ll1_opy_ (u"ࠢࡂ࡜ࡘࡖࡊࡥࡈࡕࡖࡓࡣ࡚࡙ࡅࡓࡡࡄࡋࡊࡔࡔࠣ᲌")) and env.get(bstack11ll1_opy_ (u"ࠣࡖࡉࡣࡇ࡛ࡉࡍࡆࠥ᲍")):
        return {
            bstack11ll1_opy_ (u"ࠤࡱࡥࡲ࡫ࠢ᲎"): bstack11ll1_opy_ (u"ࠥࡅࡿࡻࡲࡦࠢࡆࡍࠧ᲏"),
            bstack11ll1_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡹࡷࡲࠢᲐ"): bstack11ll1_opy_ (u"ࠧࢁࡽࡼࡿ࠲ࡣࡧࡻࡩ࡭ࡦ࠲ࡶࡪࡹࡵ࡭ࡶࡶࡃࡧࡻࡩ࡭ࡦࡌࡨࡂࢁࡽࠣᲑ").format(env.get(bstack11ll1_opy_ (u"࠭ࡓ࡚ࡕࡗࡉࡒࡥࡔࡆࡃࡐࡊࡔ࡛ࡎࡅࡃࡗࡍࡔࡔࡓࡆࡔ࡙ࡉࡗ࡛ࡒࡊࠩᲒ")), env.get(bstack11ll1_opy_ (u"ࠧࡔ࡛ࡖࡘࡊࡓ࡟ࡕࡇࡄࡑࡕࡘࡏࡋࡇࡆࡘࠬᲓ")), env.get(bstack11ll1_opy_ (u"ࠨࡄࡘࡍࡑࡊ࡟ࡃࡗࡌࡐࡉࡏࡄࠨᲔ"))),
            bstack11ll1_opy_ (u"ࠤ࡭ࡳࡧࡥ࡮ࡢ࡯ࡨࠦᲕ"): env.get(bstack11ll1_opy_ (u"ࠥࡆ࡚ࡏࡌࡅࡡࡅ࡙ࡎࡒࡄࡊࡆࠥᲖ")),
            bstack11ll1_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡲࡺࡳࡢࡦࡴࠥᲗ"): env.get(bstack11ll1_opy_ (u"ࠧࡈࡕࡊࡎࡇࡣࡇ࡛ࡉࡍࡆࡌࡈࠧᲘ"))
        }
    if any([env.get(bstack11ll1_opy_ (u"ࠨࡃࡐࡆࡈࡆ࡚ࡏࡌࡅࡡࡅ࡙ࡎࡒࡄࡠࡋࡇࠦᲙ")), env.get(bstack11ll1_opy_ (u"ࠢࡄࡑࡇࡉࡇ࡛ࡉࡍࡆࡢࡖࡊ࡙ࡏࡍࡘࡈࡈࡤ࡙ࡏࡖࡔࡆࡉࡤ࡜ࡅࡓࡕࡌࡓࡓࠨᲚ")), env.get(bstack11ll1_opy_ (u"ࠣࡅࡒࡈࡊࡈࡕࡊࡎࡇࡣࡘࡕࡕࡓࡅࡈࡣ࡛ࡋࡒࡔࡋࡒࡒࠧᲛ"))]):
        return {
            bstack11ll1_opy_ (u"ࠤࡱࡥࡲ࡫ࠢᲜ"): bstack11ll1_opy_ (u"ࠥࡅ࡜࡙ࠠࡄࡱࡧࡩࡇࡻࡩ࡭ࡦࠥᲝ"),
            bstack11ll1_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡹࡷࡲࠢᲞ"): env.get(bstack11ll1_opy_ (u"ࠧࡉࡏࡅࡇࡅ࡙ࡎࡒࡄࡠࡒࡘࡆࡑࡏࡃࡠࡄࡘࡍࡑࡊ࡟ࡖࡔࡏࠦᲟ")),
            bstack11ll1_opy_ (u"ࠨࡪࡰࡤࡢࡲࡦࡳࡥࠣᲠ"): env.get(bstack11ll1_opy_ (u"ࠢࡄࡑࡇࡉࡇ࡛ࡉࡍࡆࡢࡆ࡚ࡏࡌࡅࡡࡌࡈࠧᲡ")),
            bstack11ll1_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟࡯ࡷࡰࡦࡪࡸࠢᲢ"): env.get(bstack11ll1_opy_ (u"ࠤࡆࡓࡉࡋࡂࡖࡋࡏࡈࡤࡈࡕࡊࡎࡇࡣࡎࡊࠢᲣ"))
        }
    if env.get(bstack11ll1_opy_ (u"ࠥࡦࡦࡳࡢࡰࡱࡢࡦࡺ࡯࡬ࡥࡐࡸࡱࡧ࡫ࡲࠣᲤ")):
        return {
            bstack11ll1_opy_ (u"ࠦࡳࡧ࡭ࡦࠤᲥ"): bstack11ll1_opy_ (u"ࠧࡈࡡ࡮ࡤࡲࡳࠧᲦ"),
            bstack11ll1_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡻࡲ࡭ࠤᲧ"): env.get(bstack11ll1_opy_ (u"ࠢࡣࡣࡰࡦࡴࡵ࡟ࡣࡷ࡬ࡰࡩࡘࡥࡴࡷ࡯ࡸࡸ࡛ࡲ࡭ࠤᲨ")),
            bstack11ll1_opy_ (u"ࠣ࡬ࡲࡦࡤࡴࡡ࡮ࡧࠥᲩ"): env.get(bstack11ll1_opy_ (u"ࠤࡥࡥࡲࡨ࡯ࡰࡡࡶ࡬ࡴࡸࡴࡋࡱࡥࡒࡦࡳࡥࠣᲪ")),
            bstack11ll1_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡱࡹࡲࡨࡥࡳࠤᲫ"): env.get(bstack11ll1_opy_ (u"ࠦࡧࡧ࡭ࡣࡱࡲࡣࡧࡻࡩ࡭ࡦࡑࡹࡲࡨࡥࡳࠤᲬ"))
        }
    if env.get(bstack11ll1_opy_ (u"ࠧ࡝ࡅࡓࡅࡎࡉࡗࠨᲭ")) or env.get(bstack11ll1_opy_ (u"ࠨࡗࡆࡔࡆࡏࡊࡘ࡟ࡎࡃࡌࡒࡤࡖࡉࡑࡇࡏࡍࡓࡋ࡟ࡔࡖࡄࡖ࡙ࡋࡄࠣᲮ")):
        return {
            bstack11ll1_opy_ (u"ࠢ࡯ࡣࡰࡩࠧᲯ"): bstack11ll1_opy_ (u"࡙ࠣࡨࡶࡨࡱࡥࡳࠤᲰ"),
            bstack11ll1_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡷࡵࡰࠧᲱ"): env.get(bstack11ll1_opy_ (u"࡛ࠥࡊࡘࡃࡌࡇࡕࡣࡇ࡛ࡉࡍࡆࡢ࡙ࡗࡒࠢᲲ")),
            bstack11ll1_opy_ (u"ࠦ࡯ࡵࡢࡠࡰࡤࡱࡪࠨᲳ"): bstack11ll1_opy_ (u"ࠧࡓࡡࡪࡰࠣࡔ࡮ࡶࡥ࡭࡫ࡱࡩࠧᲴ") if env.get(bstack11ll1_opy_ (u"ࠨࡗࡆࡔࡆࡏࡊࡘ࡟ࡎࡃࡌࡒࡤࡖࡉࡑࡇࡏࡍࡓࡋ࡟ࡔࡖࡄࡖ࡙ࡋࡄࠣᲵ")) else None,
            bstack11ll1_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥ࡮ࡶ࡯ࡥࡩࡷࠨᲶ"): env.get(bstack11ll1_opy_ (u"࡙ࠣࡈࡖࡈࡑࡅࡓࡡࡊࡍ࡙ࡥࡃࡐࡏࡐࡍ࡙ࠨᲷ"))
        }
    if any([env.get(bstack11ll1_opy_ (u"ࠤࡊࡇࡕࡥࡐࡓࡑࡍࡉࡈ࡚ࠢᲸ")), env.get(bstack11ll1_opy_ (u"ࠥࡋࡈࡒࡏࡖࡆࡢࡔࡗࡕࡊࡆࡅࡗࠦᲹ")), env.get(bstack11ll1_opy_ (u"ࠦࡌࡕࡏࡈࡎࡈࡣࡈࡒࡏࡖࡆࡢࡔࡗࡕࡊࡆࡅࡗࠦᲺ"))]):
        return {
            bstack11ll1_opy_ (u"ࠧࡴࡡ࡮ࡧࠥ᲻"): bstack11ll1_opy_ (u"ࠨࡇࡰࡱࡪࡰࡪࠦࡃ࡭ࡱࡸࡨࠧ᲼"),
            bstack11ll1_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥࡵࡳ࡮ࠥᲽ"): None,
            bstack11ll1_opy_ (u"ࠣ࡬ࡲࡦࡤࡴࡡ࡮ࡧࠥᲾ"): env.get(bstack11ll1_opy_ (u"ࠤࡓࡖࡔࡐࡅࡄࡖࡢࡍࡉࠨᲿ")),
            bstack11ll1_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡱࡹࡲࡨࡥࡳࠤ᳀"): env.get(bstack11ll1_opy_ (u"ࠦࡇ࡛ࡉࡍࡆࡢࡍࡉࠨ᳁"))
        }
    if env.get(bstack11ll1_opy_ (u"࡙ࠧࡈࡊࡒࡓࡅࡇࡒࡅࠣ᳂")):
        return {
            bstack11ll1_opy_ (u"ࠨ࡮ࡢ࡯ࡨࠦ᳃"): bstack11ll1_opy_ (u"ࠢࡔࡪ࡬ࡴࡵࡧࡢ࡭ࡧࠥ᳄"),
            bstack11ll1_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟ࡶࡴ࡯ࠦ᳅"): env.get(bstack11ll1_opy_ (u"ࠤࡖࡌࡎࡖࡐࡂࡄࡏࡉࡤࡈࡕࡊࡎࡇࡣ࡚ࡘࡌࠣ᳆")),
            bstack11ll1_opy_ (u"ࠥ࡮ࡴࡨ࡟࡯ࡣࡰࡩࠧ᳇"): bstack11ll1_opy_ (u"ࠦࡏࡵࡢࠡࠥࡾࢁࠧ᳈").format(env.get(bstack11ll1_opy_ (u"࡙ࠬࡈࡊࡒࡓࡅࡇࡒࡅࡠࡌࡒࡆࡤࡏࡄࠨ᳉"))) if env.get(bstack11ll1_opy_ (u"ࠨࡓࡉࡋࡓࡔࡆࡈࡌࡆࡡࡍࡓࡇࡥࡉࡅࠤ᳊")) else None,
            bstack11ll1_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥ࡮ࡶ࡯ࡥࡩࡷࠨ᳋"): env.get(bstack11ll1_opy_ (u"ࠣࡕࡋࡍࡕࡖࡁࡃࡎࡈࡣࡇ࡛ࡉࡍࡆࡢࡒ࡚ࡓࡂࡆࡔࠥ᳌"))
        }
    if bstack1111lll1_opy_(env.get(bstack11ll1_opy_ (u"ࠤࡑࡉ࡙ࡒࡉࡇ࡛ࠥ᳍"))):
        return {
            bstack11ll1_opy_ (u"ࠥࡲࡦࡳࡥࠣ᳎"): bstack11ll1_opy_ (u"ࠦࡓ࡫ࡴ࡭࡫ࡩࡽࠧ᳏"),
            bstack11ll1_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡺࡸ࡬ࠣ᳐"): env.get(bstack11ll1_opy_ (u"ࠨࡄࡆࡒࡏࡓ࡞ࡥࡕࡓࡎࠥ᳑")),
            bstack11ll1_opy_ (u"ࠢ࡫ࡱࡥࡣࡳࡧ࡭ࡦࠤ᳒"): env.get(bstack11ll1_opy_ (u"ࠣࡕࡌࡘࡊࡥࡎࡂࡏࡈࠦ᳓")),
            bstack11ll1_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡰࡸࡱࡧ࡫ࡲ᳔ࠣ"): env.get(bstack11ll1_opy_ (u"ࠥࡆ࡚ࡏࡌࡅࡡࡌࡈ᳕ࠧ"))
        }
    if bstack1111lll1_opy_(env.get(bstack11ll1_opy_ (u"ࠦࡌࡏࡔࡉࡗࡅࡣࡆࡉࡔࡊࡑࡑࡗ᳖ࠧ"))):
        return {
            bstack11ll1_opy_ (u"ࠧࡴࡡ࡮ࡧ᳗ࠥ"): bstack11ll1_opy_ (u"ࠨࡇࡪࡶࡋࡹࡧࠦࡁࡤࡶ࡬ࡳࡳࡹ᳘ࠢ"),
            bstack11ll1_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥࡵࡳ࡮᳙ࠥ"): bstack11ll1_opy_ (u"ࠣࡽࢀ࠳ࢀࢃ࠯ࡢࡥࡷ࡭ࡴࡴࡳ࠰ࡴࡸࡲࡸ࠵ࡻࡾࠤ᳚").format(env.get(bstack11ll1_opy_ (u"ࠩࡊࡍ࡙ࡎࡕࡃࡡࡖࡉࡗ࡜ࡅࡓࡡࡘࡖࡑ࠭᳛")), env.get(bstack11ll1_opy_ (u"ࠪࡋࡎ࡚ࡈࡖࡄࡢࡖࡊࡖࡏࡔࡋࡗࡓࡗ࡟᳜ࠧ")), env.get(bstack11ll1_opy_ (u"ࠫࡌࡏࡔࡉࡗࡅࡣࡗ࡛ࡎࡠࡋࡇ᳝ࠫ"))),
            bstack11ll1_opy_ (u"ࠧࡰ࡯ࡣࡡࡱࡥࡲ࡫᳞ࠢ"): env.get(bstack11ll1_opy_ (u"ࠨࡇࡊࡖࡋ࡙ࡇࡥࡗࡐࡔࡎࡊࡑࡕࡗ᳟ࠣ")),
            bstack11ll1_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥ࡮ࡶ࡯ࡥࡩࡷࠨ᳠"): env.get(bstack11ll1_opy_ (u"ࠣࡉࡌࡘࡍ࡛ࡂࡠࡔࡘࡒࡤࡏࡄࠣ᳡"))
        }
    if env.get(bstack11ll1_opy_ (u"ࠤࡆࡍ᳢ࠧ")) == bstack11ll1_opy_ (u"ࠥࡸࡷࡻࡥ᳣ࠣ") and env.get(bstack11ll1_opy_ (u"࡛ࠦࡋࡒࡄࡇࡏ᳤ࠦ")) == bstack11ll1_opy_ (u"ࠧ࠷᳥ࠢ"):
        return {
            bstack11ll1_opy_ (u"ࠨ࡮ࡢ࡯ࡨ᳦ࠦ"): bstack11ll1_opy_ (u"ࠢࡗࡧࡵࡧࡪࡲ᳧ࠢ"),
            bstack11ll1_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟ࡶࡴ࡯᳨ࠦ"): bstack11ll1_opy_ (u"ࠤ࡫ࡸࡹࡶ࠺࠰࠱ࡾࢁࠧᳩ").format(env.get(bstack11ll1_opy_ (u"࡚ࠪࡊࡘࡃࡆࡎࡢ࡙ࡗࡒࠧᳪ"))),
            bstack11ll1_opy_ (u"ࠦ࡯ࡵࡢࡠࡰࡤࡱࡪࠨᳫ"): None,
            bstack11ll1_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡳࡻ࡭ࡣࡧࡵࠦᳬ"): None,
        }
    if env.get(bstack11ll1_opy_ (u"ࠨࡔࡆࡃࡐࡇࡎ࡚࡙ࡠࡘࡈࡖࡘࡏࡏࡏࠤ᳭")):
        return {
            bstack11ll1_opy_ (u"ࠢ࡯ࡣࡰࡩࠧᳮ"): bstack11ll1_opy_ (u"ࠣࡖࡨࡥࡲࡩࡩࡵࡻࠥᳯ"),
            bstack11ll1_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡷࡵࡰࠧᳰ"): None,
            bstack11ll1_opy_ (u"ࠥ࡮ࡴࡨ࡟࡯ࡣࡰࡩࠧᳱ"): env.get(bstack11ll1_opy_ (u"࡙ࠦࡋࡁࡎࡅࡌࡘ࡞ࡥࡐࡓࡑࡍࡉࡈ࡚࡟ࡏࡃࡐࡉࠧᳲ")),
            bstack11ll1_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡳࡻ࡭ࡣࡧࡵࠦᳳ"): env.get(bstack11ll1_opy_ (u"ࠨࡂࡖࡋࡏࡈࡤࡔࡕࡎࡄࡈࡖࠧ᳴"))
        }
    if any([env.get(bstack11ll1_opy_ (u"ࠢࡄࡑࡑࡇࡔ࡛ࡒࡔࡇࠥᳵ")), env.get(bstack11ll1_opy_ (u"ࠣࡅࡒࡒࡈࡕࡕࡓࡕࡈࡣ࡚ࡘࡌࠣᳶ")), env.get(bstack11ll1_opy_ (u"ࠤࡆࡓࡓࡉࡏࡖࡔࡖࡉࡤ࡛ࡓࡆࡔࡑࡅࡒࡋࠢ᳷")), env.get(bstack11ll1_opy_ (u"ࠥࡇࡔࡔࡃࡐࡗࡕࡗࡊࡥࡔࡆࡃࡐࠦ᳸"))]):
        return {
            bstack11ll1_opy_ (u"ࠦࡳࡧ࡭ࡦࠤ᳹"): bstack11ll1_opy_ (u"ࠧࡉ࡯࡯ࡥࡲࡹࡷࡹࡥࠣᳺ"),
            bstack11ll1_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡻࡲ࡭ࠤ᳻"): None,
            bstack11ll1_opy_ (u"ࠢ࡫ࡱࡥࡣࡳࡧ࡭ࡦࠤ᳼"): env.get(bstack11ll1_opy_ (u"ࠣࡄࡘࡍࡑࡊ࡟ࡋࡑࡅࡣࡓࡇࡍࡆࠤ᳽")) or None,
            bstack11ll1_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡰࡸࡱࡧ࡫ࡲࠣ᳾"): env.get(bstack11ll1_opy_ (u"ࠥࡆ࡚ࡏࡌࡅࡡࡌࡈࠧ᳿"), 0)
        }
    if env.get(bstack11ll1_opy_ (u"ࠦࡌࡕ࡟ࡋࡑࡅࡣࡓࡇࡍࡆࠤᴀ")):
        return {
            bstack11ll1_opy_ (u"ࠧࡴࡡ࡮ࡧࠥᴁ"): bstack11ll1_opy_ (u"ࠨࡇࡰࡅࡇࠦᴂ"),
            bstack11ll1_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥࡵࡳ࡮ࠥᴃ"): None,
            bstack11ll1_opy_ (u"ࠣ࡬ࡲࡦࡤࡴࡡ࡮ࡧࠥᴄ"): env.get(bstack11ll1_opy_ (u"ࠤࡊࡓࡤࡐࡏࡃࡡࡑࡅࡒࡋࠢᴅ")),
            bstack11ll1_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡱࡹࡲࡨࡥࡳࠤᴆ"): env.get(bstack11ll1_opy_ (u"ࠦࡌࡕ࡟ࡑࡋࡓࡉࡑࡏࡎࡆࡡࡆࡓ࡚ࡔࡔࡆࡔࠥᴇ"))
        }
    if env.get(bstack11ll1_opy_ (u"ࠧࡉࡆࡠࡄࡘࡍࡑࡊ࡟ࡊࡆࠥᴈ")):
        return {
            bstack11ll1_opy_ (u"ࠨ࡮ࡢ࡯ࡨࠦᴉ"): bstack11ll1_opy_ (u"ࠢࡄࡱࡧࡩࡋࡸࡥࡴࡪࠥᴊ"),
            bstack11ll1_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟ࡶࡴ࡯ࠦᴋ"): env.get(bstack11ll1_opy_ (u"ࠤࡆࡊࡤࡈࡕࡊࡎࡇࡣ࡚ࡘࡌࠣᴌ")),
            bstack11ll1_opy_ (u"ࠥ࡮ࡴࡨ࡟࡯ࡣࡰࡩࠧᴍ"): env.get(bstack11ll1_opy_ (u"ࠦࡈࡌ࡟ࡑࡋࡓࡉࡑࡏࡎࡆࡡࡑࡅࡒࡋࠢᴎ")),
            bstack11ll1_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡳࡻ࡭ࡣࡧࡵࠦᴏ"): env.get(bstack11ll1_opy_ (u"ࠨࡃࡇࡡࡅ࡙ࡎࡒࡄࡠࡋࡇࠦᴐ"))
        }
    return {bstack11ll1_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥ࡮ࡶ࡯ࡥࡩࡷࠨᴑ"): None}
def get_host_info():
    return {
        bstack11ll1_opy_ (u"ࠣࡪࡲࡷࡹࡴࡡ࡮ࡧࠥᴒ"): platform.node(),
        bstack11ll1_opy_ (u"ࠤࡳࡰࡦࡺࡦࡰࡴࡰࠦᴓ"): platform.system(),
        bstack11ll1_opy_ (u"ࠥࡸࡾࡶࡥࠣᴔ"): platform.machine(),
        bstack11ll1_opy_ (u"ࠦࡻ࡫ࡲࡴ࡫ࡲࡲࠧᴕ"): platform.version(),
        bstack11ll1_opy_ (u"ࠧࡧࡲࡤࡪࠥᴖ"): platform.architecture()[0]
    }
def bstack1l11lll111_opy_():
    try:
        import selenium
        return True
    except ImportError:
        return False
def bstack11l111111l1_opy_():
    if bstack1l1l1ll1l_opy_.get_property(bstack11ll1_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡥࡳࡦࡵࡶ࡭ࡴࡴࠧᴗ")):
        return bstack11ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠭ᴘ")
    return bstack11ll1_opy_ (u"ࠨࡷࡱ࡯ࡳࡵࡷ࡯ࡡࡪࡶ࡮ࡪࠧᴙ")
def bstack111lll111ll_opy_(driver):
    info = {
        bstack11ll1_opy_ (u"ࠩࡦࡥࡵࡧࡢࡪ࡮࡬ࡸ࡮࡫ࡳࠨᴚ"): driver.capabilities,
        bstack11ll1_opy_ (u"ࠪࡷࡪࡹࡳࡪࡱࡱࡣ࡮ࡪࠧᴛ"): driver.session_id,
        bstack11ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࠬᴜ"): driver.capabilities.get(bstack11ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡔࡡ࡮ࡧࠪᴝ"), None),
        bstack11ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸ࡟ࡷࡧࡵࡷ࡮ࡵ࡮ࠨᴞ"): driver.capabilities.get(bstack11ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡗࡧࡵࡷ࡮ࡵ࡮ࠨᴟ"), None),
        bstack11ll1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࠪᴠ"): driver.capabilities.get(bstack11ll1_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡒࡦࡳࡥࠨᴡ"), None),
        bstack11ll1_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡤࡼࡥࡳࡵ࡬ࡳࡳ࠭ᴢ"):driver.capabilities.get(bstack11ll1_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲ࡜ࡥࡳࡵ࡬ࡳࡳ࠭ᴣ"), None),
    }
    if bstack11l111111l1_opy_() == bstack11ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࠫᴤ"):
        if bstack1l1lll1l_opy_():
            info[bstack11ll1_opy_ (u"࠭ࡰࡳࡱࡧࡹࡨࡺࠧᴥ")] = bstack11ll1_opy_ (u"ࠧࡢࡲࡳ࠱ࡦࡻࡴࡰ࡯ࡤࡸࡪ࠭ᴦ")
        elif driver.capabilities.get(bstack11ll1_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫࠻ࡱࡳࡸ࡮ࡵ࡮ࡴࠩᴧ"), {}).get(bstack11ll1_opy_ (u"ࠩࡷࡹࡷࡨ࡯ࡴࡥࡤࡰࡪ࠭ᴨ"), False):
            info[bstack11ll1_opy_ (u"ࠪࡴࡷࡵࡤࡶࡥࡷࠫᴩ")] = bstack11ll1_opy_ (u"ࠫࡹࡻࡲࡣࡱࡶࡧࡦࡲࡥࠨᴪ")
        else:
            info[bstack11ll1_opy_ (u"ࠬࡶࡲࡰࡦࡸࡧࡹ࠭ᴫ")] = bstack11ll1_opy_ (u"࠭ࡡࡶࡶࡲࡱࡦࡺࡥࠨᴬ")
    return info
def bstack1l1lll1l_opy_():
    if bstack1l1l1ll1l_opy_.get_property(bstack11ll1_opy_ (u"ࠧࡢࡲࡳࡣࡦࡻࡴࡰ࡯ࡤࡸࡪ࠭ᴭ")):
        return True
    if bstack1111lll1_opy_(os.environ.get(bstack11ll1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡊࡕࡢࡅࡕࡖ࡟ࡂࡗࡗࡓࡒࡇࡔࡆࠩᴮ"), None)):
        return True
    return False
def bstack111l1l11lll_opy_(bstack111l1ll11l1_opy_, url, response, headers=None, data=None):
    bstack11ll1_opy_ (u"ࠤࠥࠦࠏࠦࠠࠡࠢࡅࡹ࡮ࡲࡤࠡࡣࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࠥࡲ࡯ࡨࠢࡳࡥࡷࡧ࡭ࡦࡶࡨࡶࡸࠦࡦࡰࡴࠣࡶࡪࡷࡵࡦࡵࡷ࠳ࡷ࡫ࡳࡱࡱࡱࡷࡪࠦ࡬ࡰࡩࡪ࡭ࡳ࡭ࠊࠡࠢࠣࠤࡆࡸࡧࡴ࠼ࠍࠤࠥࠦࠠࠡࠢࠣࠤࡷ࡫ࡱࡶࡧࡶࡸࡤࡺࡹࡱࡧ࠽ࠤࡍ࡚ࡔࡑࠢࡰࡩࡹ࡮࡯ࡥࠢࠫࡋࡊ࡚ࠬࠡࡒࡒࡗ࡙࠲ࠠࡦࡶࡦ࠲࠮ࠐࠠࠡࠢࠣࠤࠥࠦࠠࡶࡴ࡯࠾ࠥࡘࡥࡲࡷࡨࡷࡹࠦࡕࡓࡎ࠲ࡩࡳࡪࡰࡰ࡫ࡱࡸࠏࠦࠠࠡࠢࠣࠤࠥࠦࡲࡦࡵࡳࡳࡳࡹࡥ࠻ࠢࡕࡩࡸࡶ࡯࡯ࡵࡨࠤࡴࡨࡪࡦࡥࡷࠤ࡫ࡸ࡯࡮ࠢࡵࡩࡶࡻࡥࡴࡶࡶࠎࠥࠦࠠࠡࠢࠣࠤࠥ࡮ࡥࡢࡦࡨࡶࡸࡀࠠࡓࡧࡴࡹࡪࡹࡴࠡࡪࡨࡥࡩ࡫ࡲࡴࠢࡲࡶࠥࡔ࡯࡯ࡧࠍࠤࠥࠦࠠࠡࠢࠣࠤࡩࡧࡴࡢ࠼ࠣࡖࡪࡷࡵࡦࡵࡷࠤࡏ࡙ࡏࡏࠢࡧࡥࡹࡧࠠࡰࡴࠣࡒࡴࡴࡥࠋࠢࠣࠤࠥࡘࡥࡵࡷࡵࡲࡸࡀࠊࠡࠢࠣࠤࠥࠦࠠࠡࡦ࡬ࡧࡹࡀࠠࡇࡱࡵࡱࡦࡺࡴࡦࡦࠣࡰࡴ࡭ࠠ࡮ࡧࡶࡷࡦ࡭ࡥࠡࡹ࡬ࡸ࡭ࠦࡲࡦࡳࡸࡩࡸࡺࠠࡢࡰࡧࠤࡷ࡫ࡳࡱࡱࡱࡷࡪࠦࡤࡢࡶࡤࠎࠥࠦࠠࠡࠤࠥࠦᴯ")
    bstack111lllll11l_opy_ = {
        bstack11ll1_opy_ (u"ࠥ࡬ࡪࡧࡤࡦࡴࡶࠦᴰ"): headers,
        bstack11ll1_opy_ (u"ࠦࡲ࡫ࡴࡩࡱࡧࠦᴱ"): bstack111l1ll11l1_opy_.upper(),
        bstack11ll1_opy_ (u"ࠧࡧࡧࡦࡰࡷࠦᴲ"): None,
        bstack11ll1_opy_ (u"ࠨࡥ࡯ࡦࡳࡳ࡮ࡴࡴࠣᴳ"): url,
        bstack11ll1_opy_ (u"ࠢ࡫ࡵࡲࡲࠧᴴ"): data
    }
    try:
        bstack11l1111111l_opy_ = response.json()
    except Exception:
        bstack11l1111111l_opy_ = response.text
    bstack111l1ll1l11_opy_ = {
        bstack11ll1_opy_ (u"ࠣࡤࡲࡨࡾࠨᴵ"): bstack11l1111111l_opy_,
        bstack11ll1_opy_ (u"ࠤࡶࡸࡦࡺࡵࡴࡅࡲࡨࡪࠨᴶ"): response.status_code
    }
    return {
        bstack11ll1_opy_ (u"ࠥࡶࡪࡷࡵࡦࡵࡷࠦᴷ"): bstack111lllll11l_opy_,
        bstack11ll1_opy_ (u"ࠦࡷ࡫ࡳࡱࡱࡱࡷࡪࠨᴸ"): bstack111l1ll1l11_opy_
    }
def bstack11l1l1l11l_opy_(bstack111l1ll11l1_opy_, url, data, config):
    headers = config.get(bstack11ll1_opy_ (u"ࠬ࡮ࡥࡢࡦࡨࡶࡸ࠭ᴹ"), None)
    proxies = bstack1lllll1111_opy_(config, url)
    auth = config.get(bstack11ll1_opy_ (u"࠭ࡡࡶࡶ࡫ࠫᴺ"), None)
    response = requests.request(
            bstack111l1ll11l1_opy_,
            url=url,
            headers=headers,
            auth=auth,
            json=data,
            proxies=proxies
        )
    try:
        log_message = bstack111l1l11lll_opy_(bstack111l1ll11l1_opy_, url, response, headers, data)
        bstack11ll111l1l_opy_.debug(json.dumps(log_message, separators=(bstack11ll1_opy_ (u"ࠧ࠭ࠩᴻ"), bstack11ll1_opy_ (u"ࠨ࠼ࠪᴼ"))))
    except Exception as e:
        logger.debug(bstack11ll1_opy_ (u"ࠤࡈࡶࡷࡵࡲࠡࡹ࡫࡭ࡱ࡫ࠠ࡭ࡱࡪ࡫࡮ࡴࡧࠡࡣࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࠥࡸࡥࡲࡷࡨࡷࡹࡀࠠࡼࡿࠥᴽ").format(e))
    return response
def bstack1l11ll1l1l_opy_(bstack1ll1lllll_opy_, size):
    bstack1l1111llll_opy_ = []
    while len(bstack1ll1lllll_opy_) > size:
        bstack11l1l1ll11_opy_ = bstack1ll1lllll_opy_[:size]
        bstack1l1111llll_opy_.append(bstack11l1l1ll11_opy_)
        bstack1ll1lllll_opy_ = bstack1ll1lllll_opy_[size:]
    bstack1l1111llll_opy_.append(bstack1ll1lllll_opy_)
    return bstack1l1111llll_opy_
def bstack11l111l1lll_opy_(message, bstack11l111l1l11_opy_=False):
    os.write(1, bytes(message, bstack11ll1_opy_ (u"ࠪࡹࡹ࡬࠭࠹ࠩᴾ")))
    os.write(1, bytes(bstack11ll1_opy_ (u"ࠫࡡࡴࠧᴿ"), bstack11ll1_opy_ (u"ࠬࡻࡴࡧ࠯࠻ࠫᵀ")))
    if bstack11l111l1l11_opy_:
        with open(bstack11ll1_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰ࠳࡯࠲࠳ࡼ࠱ࠬᵁ") + os.environ[bstack11ll1_opy_ (u"ࠧࡃࡕࡢࡘࡊ࡙ࡔࡐࡒࡖࡣࡇ࡛ࡉࡍࡆࡢࡌࡆ࡙ࡈࡆࡆࡢࡍࡉ࠭ᵂ")] + bstack11ll1_opy_ (u"ࠨ࠰࡯ࡳ࡬࠭ᵃ"), bstack11ll1_opy_ (u"ࠩࡤࠫᵄ")) as f:
            f.write(message + bstack11ll1_opy_ (u"ࠪࡠࡳ࠭ᵅ"))
def bstack1ll111l11l1_opy_():
    return os.environ[bstack11ll1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡅ࡚࡚ࡏࡎࡃࡗࡍࡔࡔࠧᵆ")].lower() == bstack11ll1_opy_ (u"ࠬࡺࡲࡶࡧࠪᵇ")
def bstack111lll1lll_opy_():
    return bstack111l11l1ll_opy_().replace(tzinfo=None).isoformat() + bstack11ll1_opy_ (u"࡚࠭ࠨᵈ")
def bstack111ll1ll111_opy_(start, finish):
    return (datetime.datetime.fromisoformat(finish.rstrip(bstack11ll1_opy_ (u"࡛ࠧࠩᵉ"))) - datetime.datetime.fromisoformat(start.rstrip(bstack11ll1_opy_ (u"ࠨ࡜ࠪᵊ")))).total_seconds() * 1000
def bstack111llll1l1l_opy_(timestamp):
    return bstack111l1ll111l_opy_(timestamp).isoformat() + bstack11ll1_opy_ (u"ࠩ࡝ࠫᵋ")
def bstack111llllllll_opy_(bstack111lll11l11_opy_):
    date_format = bstack11ll1_opy_ (u"ࠪࠩ࡞ࠫ࡭ࠦࡦࠣࠩࡍࡀࠥࡎ࠼ࠨࡗ࠳ࠫࡦࠨᵌ")
    bstack111l1lllll1_opy_ = datetime.datetime.strptime(bstack111lll11l11_opy_, date_format)
    return bstack111l1lllll1_opy_.isoformat() + bstack11ll1_opy_ (u"ࠫ࡟࠭ᵍ")
def bstack111lllll1ll_opy_(outcome):
    _, exception, _ = outcome.excinfo or (None, None, None)
    if exception:
        return bstack11ll1_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡨࡨࠬᵎ")
    else:
        return bstack11ll1_opy_ (u"࠭ࡰࡢࡵࡶࡩࡩ࠭ᵏ")
def bstack1111lll1_opy_(val):
    if val is None:
        return False
    return val.__str__().lower() == bstack11ll1_opy_ (u"ࠧࡵࡴࡸࡩࠬᵐ")
def bstack11l1111llll_opy_(val):
    return val.__str__().lower() == bstack11ll1_opy_ (u"ࠨࡨࡤࡰࡸ࡫ࠧᵑ")
def error_handler(bstack111llll11l1_opy_=Exception, class_method=False, default_value=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except bstack111llll11l1_opy_ as e:
                print(bstack11ll1_opy_ (u"ࠤࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥ࡯࡮ࠡࡨࡸࡲࡨࡺࡩࡰࡰࠣࡿࢂࠦ࠭࠿ࠢࡾࢁ࠿ࠦࡻࡾࠤᵒ").format(func.__name__, bstack111llll11l1_opy_.__name__, str(e)))
                return default_value
        return wrapper
    def bstack11l111111ll_opy_(bstack111l1llll1l_opy_):
        def wrapped(cls, *args, **kwargs):
            try:
                return bstack111l1llll1l_opy_(cls, *args, **kwargs)
            except bstack111llll11l1_opy_ as e:
                print(bstack11ll1_opy_ (u"ࠥࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡩ࡯ࠢࡩࡹࡳࡩࡴࡪࡱࡱࠤࢀࢃࠠ࠮ࡀࠣࡿࢂࡀࠠࡼࡿࠥᵓ").format(bstack111l1llll1l_opy_.__name__, bstack111llll11l1_opy_.__name__, str(e)))
                return default_value
        return wrapped
    if class_method:
        return bstack11l111111ll_opy_
    else:
        return decorator
def bstack11lllll11l_opy_(bstack1llllllllll_opy_):
    if os.getenv(bstack11ll1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡅ࡚࡚ࡏࡎࡃࡗࡍࡔࡔࠧᵔ")) is not None:
        return bstack1111lll1_opy_(os.getenv(bstack11ll1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡆ࡛ࡔࡐࡏࡄࡘࡎࡕࡎࠨᵕ")))
    if bstack11ll1_opy_ (u"࠭ࡡࡶࡶࡲࡱࡦࡺࡩࡰࡰࠪᵖ") in bstack1llllllllll_opy_ and bstack11l1111llll_opy_(bstack1llllllllll_opy_[bstack11ll1_opy_ (u"ࠧࡢࡷࡷࡳࡲࡧࡴࡪࡱࡱࠫᵗ")]):
        return False
    if bstack11ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡁࡶࡶࡲࡱࡦࡺࡩࡰࡰࠪᵘ") in bstack1llllllllll_opy_ and bstack11l1111llll_opy_(bstack1llllllllll_opy_[bstack11ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡂࡷࡷࡳࡲࡧࡴࡪࡱࡱࠫᵙ")]):
        return False
    return True
def bstack1l1l1l1l_opy_():
    try:
        from pytest_bdd import reporting
        bstack11l1111l111_opy_ = os.environ.get(bstack11ll1_opy_ (u"ࠥࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡘࡗࡊࡘ࡟ࡇࡔࡄࡑࡊ࡝ࡏࡓࡍࠥᵚ"), None)
        return bstack11l1111l111_opy_ is None or bstack11l1111l111_opy_ == bstack11ll1_opy_ (u"ࠦࡵࡿࡴࡦࡵࡷ࠱ࡧࡪࡤࠣᵛ")
    except Exception as e:
        return False
def bstack1l1l11l11_opy_(hub_url, CONFIG):
    if bstack1ll1ll1l11_opy_() <= version.parse(bstack11ll1_opy_ (u"ࠬ࠹࠮࠲࠵࠱࠴ࠬᵜ")):
        if hub_url:
            return bstack11ll1_opy_ (u"ࠨࡨࡵࡶࡳ࠾࠴࠵ࠢᵝ") + hub_url + bstack11ll1_opy_ (u"ࠢ࠻࠺࠳࠳ࡼࡪ࠯ࡩࡷࡥࠦᵞ")
        return bstack111l1ll11_opy_
    if hub_url:
        return bstack11ll1_opy_ (u"ࠣࡪࡷࡸࡵࡹ࠺࠰࠱ࠥᵟ") + hub_url + bstack11ll1_opy_ (u"ࠤ࠲ࡻࡩ࠵ࡨࡶࡤࠥᵠ")
    return bstack11l1l11lll_opy_
def bstack111ll1ll11l_opy_():
    return isinstance(os.getenv(bstack11ll1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡓ࡝࡙ࡋࡓࡕࡡࡓࡐ࡚ࡍࡉࡏࠩᵡ")), str)
def bstack1l1111ll1_opy_(url):
    return urlparse(url).hostname
def bstack1111ll1l_opy_(hostname):
    for bstack1l1l11llll_opy_ in bstack11llll1ll1_opy_:
        regex = re.compile(bstack1l1l11llll_opy_)
        if regex.match(hostname):
            return True
    return False
def bstack11l111l1ll1_opy_(bstack111ll1l1111_opy_, file_name, logger):
    bstack11lll1lll_opy_ = os.path.join(os.path.expanduser(bstack11ll1_opy_ (u"ࠫࢃ࠭ᵢ")), bstack111ll1l1111_opy_)
    try:
        if not os.path.exists(bstack11lll1lll_opy_):
            os.makedirs(bstack11lll1lll_opy_)
        file_path = os.path.join(os.path.expanduser(bstack11ll1_opy_ (u"ࠬࢄࠧᵣ")), bstack111ll1l1111_opy_, file_name)
        if not os.path.isfile(file_path):
            with open(file_path, bstack11ll1_opy_ (u"࠭ࡷࠨᵤ")):
                pass
            with open(file_path, bstack11ll1_opy_ (u"ࠢࡸ࠭ࠥᵥ")) as outfile:
                json.dump({}, outfile)
        return file_path
    except Exception as e:
        logger.debug(bstack1ll111l11_opy_.format(str(e)))
def bstack11l111l111l_opy_(file_name, key, value, logger):
    file_path = bstack11l111l1ll1_opy_(bstack11ll1_opy_ (u"ࠨ࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࠨᵦ"), file_name, logger)
    if file_path != None:
        if os.path.exists(file_path):
            bstack1lll11111l_opy_ = json.load(open(file_path, bstack11ll1_opy_ (u"ࠩࡵࡦࠬᵧ")))
        else:
            bstack1lll11111l_opy_ = {}
        bstack1lll11111l_opy_[key] = value
        with open(file_path, bstack11ll1_opy_ (u"ࠥࡻ࠰ࠨᵨ")) as outfile:
            json.dump(bstack1lll11111l_opy_, outfile)
def bstack11llllllll_opy_(file_name, logger):
    file_path = bstack11l111l1ll1_opy_(bstack11ll1_opy_ (u"ࠫ࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࠫᵩ"), file_name, logger)
    bstack1lll11111l_opy_ = {}
    if file_path != None and os.path.exists(file_path):
        with open(file_path, bstack11ll1_opy_ (u"ࠬࡸࠧᵪ")) as bstack1l1l11l1_opy_:
            bstack1lll11111l_opy_ = json.load(bstack1l1l11l1_opy_)
    return bstack1lll11111l_opy_
def bstack1lllll11l1_opy_(file_path, logger):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        logger.debug(bstack11ll1_opy_ (u"࠭ࡅࡳࡴࡲࡶࠥ࡯࡮ࠡࡦࡨࡰࡪࡺࡩ࡯ࡩࠣࡪ࡮ࡲࡥ࠻ࠢࠪᵫ") + file_path + bstack11ll1_opy_ (u"ࠧࠡࠩᵬ") + str(e))
def bstack1ll1ll1l11_opy_():
    from selenium import webdriver
    return version.parse(webdriver.__version__)
class Notset:
    def __repr__(self):
        return bstack11ll1_opy_ (u"ࠣ࠾ࡑࡓ࡙࡙ࡅࡕࡀࠥᵭ")
def bstack11lll11lll_opy_(config):
    if bstack11ll1_opy_ (u"ࠩ࡬ࡷࡕࡲࡡࡺࡹࡵ࡭࡬࡮ࡴࠨᵮ") in config:
        del (config[bstack11ll1_opy_ (u"ࠪ࡭ࡸࡖ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵࠩᵯ")])
        return False
    if bstack1ll1ll1l11_opy_() < version.parse(bstack11ll1_opy_ (u"ࠫ࠸࠴࠴࠯࠲ࠪᵰ")):
        return False
    if bstack1ll1ll1l11_opy_() >= version.parse(bstack11ll1_opy_ (u"ࠬ࠺࠮࠲࠰࠸ࠫᵱ")):
        return True
    if bstack11ll1_opy_ (u"࠭ࡵࡴࡧ࡚࠷ࡈ࠭ᵲ") in config and config[bstack11ll1_opy_ (u"ࠧࡶࡵࡨ࡛࠸ࡉࠧᵳ")] is False:
        return False
    else:
        return True
def bstack1l1llll11l_opy_(args_list, bstack111l1l1ll11_opy_):
    index = -1
    for value in bstack111l1l1ll11_opy_:
        try:
            index = args_list.index(value)
            return index
        except Exception as e:
            return index
    return index
def bstack11ll1111lll_opy_(a, b):
  for k, v in b.items():
    if isinstance(v, dict) and k in a and isinstance(a[k], dict):
        bstack11ll1111lll_opy_(a[k], v)
    else:
        a[k] = v
class Result:
    def __init__(self, result=None, duration=None, exception=None, bstack111l1l1ll1_opy_=None):
        self.result = result
        self.duration = duration
        self.exception = exception
        self.exception_type = type(self.exception).__name__ if exception else None
        self.bstack111l1l1ll1_opy_ = bstack111l1l1ll1_opy_
    @classmethod
    def passed(cls):
        return Result(result=bstack11ll1_opy_ (u"ࠨࡲࡤࡷࡸ࡫ࡤࠨᵴ"))
    @classmethod
    def failed(cls, exception=None):
        return Result(result=bstack11ll1_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࠩᵵ"), exception=exception)
    def bstack1lllll1ll11_opy_(self):
        if self.result != bstack11ll1_opy_ (u"ࠪࡪࡦ࡯࡬ࡦࡦࠪᵶ"):
            return None
        if isinstance(self.exception_type, str) and bstack11ll1_opy_ (u"ࠦࡆࡹࡳࡦࡴࡷ࡭ࡴࡴࠢᵷ") in self.exception_type:
            return bstack11ll1_opy_ (u"ࠧࡇࡳࡴࡧࡵࡸ࡮ࡵ࡮ࡆࡴࡵࡳࡷࠨᵸ")
        return bstack11ll1_opy_ (u"ࠨࡕ࡯ࡪࡤࡲࡩࡲࡥࡥࡇࡵࡶࡴࡸࠢᵹ")
    def bstack111ll11ll11_opy_(self):
        if self.result != bstack11ll1_opy_ (u"ࠧࡧࡣ࡬ࡰࡪࡪࠧᵺ"):
            return None
        if self.bstack111l1l1ll1_opy_:
            return self.bstack111l1l1ll1_opy_
        return bstack111ll1ll1ll_opy_(self.exception)
def bstack111ll1ll1ll_opy_(exc):
    return [traceback.format_exception(exc)]
def bstack11l11111l11_opy_(message):
    if isinstance(message, str):
        return not bool(message and message.strip())
    return True
def bstack1lll11l1l_opy_(object, key, default_value):
    if not object or not object.__dict__:
        return default_value
    if key in object.__dict__.keys():
        return object.__dict__.get(key)
    return default_value
def bstack1l11ll11l1_opy_(config, logger):
    try:
        import playwright
        bstack111ll111lll_opy_ = playwright.__file__
        bstack11l1111lll1_opy_ = os.path.split(bstack111ll111lll_opy_)
        bstack111llllll11_opy_ = bstack11l1111lll1_opy_[0] + bstack11ll1_opy_ (u"ࠨ࠱ࡧࡶ࡮ࡼࡥࡳ࠱ࡳࡥࡨࡱࡡࡨࡧ࠲ࡰ࡮ࡨ࠯ࡤ࡮࡬࠳ࡨࡲࡩ࠯࡬ࡶࠫᵻ")
        os.environ[bstack11ll1_opy_ (u"ࠩࡊࡐࡔࡈࡁࡍࡡࡄࡋࡊࡔࡔࡠࡊࡗࡘࡕࡥࡐࡓࡑ࡛࡝ࠬᵼ")] = bstack11l1ll11l_opy_(config)
        with open(bstack111llllll11_opy_, bstack11ll1_opy_ (u"ࠪࡶࠬᵽ")) as f:
            bstack111111111_opy_ = f.read()
            bstack111llllll1l_opy_ = bstack11ll1_opy_ (u"ࠫ࡬ࡲ࡯ࡣࡣ࡯࠱ࡦ࡭ࡥ࡯ࡶࠪᵾ")
            bstack111ll11l111_opy_ = bstack111111111_opy_.find(bstack111llllll1l_opy_)
            if bstack111ll11l111_opy_ == -1:
              process = subprocess.Popen(bstack11ll1_opy_ (u"ࠧࡴࡰ࡮ࠢ࡬ࡲࡸࡺࡡ࡭࡮ࠣ࡫ࡱࡵࡢࡢ࡮࠰ࡥ࡬࡫࡮ࡵࠤᵿ"), shell=True, cwd=bstack11l1111lll1_opy_[0])
              process.wait()
              bstack111l1l1llll_opy_ = bstack11ll1_opy_ (u"࠭ࠢࡶࡵࡨࠤࡸࡺࡲࡪࡥࡷࠦࡀ࠭ᶀ")
              bstack111lllllll1_opy_ = bstack11ll1_opy_ (u"ࠢࠣࠤࠣࡠࠧࡻࡳࡦࠢࡶࡸࡷ࡯ࡣࡵ࡞ࠥ࠿ࠥࡩ࡯࡯ࡵࡷࠤࢀࠦࡢࡰࡱࡷࡷࡹࡸࡡࡱࠢࢀࠤࡂࠦࡲࡦࡳࡸ࡭ࡷ࡫ࠨࠨࡩ࡯ࡳࡧࡧ࡬࠮ࡣࡪࡩࡳࡺࠧࠪ࠽ࠣ࡭࡫ࠦࠨࡱࡴࡲࡧࡪࡹࡳ࠯ࡧࡱࡺ࠳ࡍࡌࡐࡄࡄࡐࡤࡇࡇࡆࡐࡗࡣࡍ࡚ࡔࡑࡡࡓࡖࡔ࡞࡙ࠪࠢࡥࡳࡴࡺࡳࡵࡴࡤࡴ࠭࠯࠻ࠡࠤࠥࠦᶁ")
              bstack11l111ll1l1_opy_ = bstack111111111_opy_.replace(bstack111l1l1llll_opy_, bstack111lllllll1_opy_)
              with open(bstack111llllll11_opy_, bstack11ll1_opy_ (u"ࠨࡹࠪᶂ")) as f:
                f.write(bstack11l111ll1l1_opy_)
    except Exception as e:
        logger.error(bstack1l1llllll1_opy_.format(str(e)))
def bstack1l1ll11ll_opy_():
  try:
    bstack111l1lll111_opy_ = os.path.join(tempfile.gettempdir(), bstack11ll1_opy_ (u"ࠩࡲࡴࡹ࡯࡭ࡢ࡮ࡢ࡬ࡺࡨ࡟ࡶࡴ࡯࠲࡯ࡹ࡯࡯ࠩᶃ"))
    bstack111lll1ll11_opy_ = []
    if os.path.exists(bstack111l1lll111_opy_):
      with open(bstack111l1lll111_opy_) as f:
        bstack111lll1ll11_opy_ = json.load(f)
      os.remove(bstack111l1lll111_opy_)
    return bstack111lll1ll11_opy_
  except:
    pass
  return []
def bstack1l1ll111l1_opy_(bstack111lll1111_opy_):
  try:
    bstack111lll1ll11_opy_ = []
    bstack111l1lll111_opy_ = os.path.join(tempfile.gettempdir(), bstack11ll1_opy_ (u"ࠪࡳࡵࡺࡩ࡮ࡣ࡯ࡣ࡭ࡻࡢࡠࡷࡵࡰ࠳ࡰࡳࡰࡰࠪᶄ"))
    if os.path.exists(bstack111l1lll111_opy_):
      with open(bstack111l1lll111_opy_) as f:
        bstack111lll1ll11_opy_ = json.load(f)
    bstack111lll1ll11_opy_.append(bstack111lll1111_opy_)
    with open(bstack111l1lll111_opy_, bstack11ll1_opy_ (u"ࠫࡼ࠭ᶅ")) as f:
        json.dump(bstack111lll1ll11_opy_, f)
  except:
    pass
def bstack11l111l1ll_opy_(logger, bstack111llll1lll_opy_ = False):
  try:
    test_name = os.environ.get(bstack11ll1_opy_ (u"ࠬࡖ࡙ࡕࡇࡖࡘࡤ࡚ࡅࡔࡖࡢࡒࡆࡓࡅࠨᶆ"), bstack11ll1_opy_ (u"࠭ࠧᶇ"))
    if test_name == bstack11ll1_opy_ (u"ࠧࠨᶈ"):
        test_name = threading.current_thread().__dict__.get(bstack11ll1_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࡃࡦࡧࡣࡹ࡫ࡳࡵࡡࡱࡥࡲ࡫ࠧᶉ"), bstack11ll1_opy_ (u"ࠩࠪᶊ"))
    bstack111ll1l1l1l_opy_ = bstack11ll1_opy_ (u"ࠪ࠰ࠥ࠭ᶋ").join(threading.current_thread().bstackTestErrorMessages)
    if bstack111llll1lll_opy_:
        bstack1l11ll11ll_opy_ = os.environ.get(bstack11ll1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡔࡑࡇࡔࡇࡑࡕࡑࡤࡏࡎࡅࡇ࡛ࠫᶌ"), bstack11ll1_opy_ (u"ࠬ࠶ࠧᶍ"))
        bstack1l11111l11_opy_ = {bstack11ll1_opy_ (u"࠭࡮ࡢ࡯ࡨࠫᶎ"): test_name, bstack11ll1_opy_ (u"ࠧࡦࡴࡵࡳࡷ࠭ᶏ"): bstack111ll1l1l1l_opy_, bstack11ll1_opy_ (u"ࠨ࡫ࡱࡨࡪࡾࠧᶐ"): bstack1l11ll11ll_opy_}
        bstack111llll1111_opy_ = []
        bstack11l1111l11l_opy_ = os.path.join(tempfile.gettempdir(), bstack11ll1_opy_ (u"ࠩࡳࡽࡹ࡫ࡳࡵࡡࡳࡴࡵࡥࡥࡳࡴࡲࡶࡤࡲࡩࡴࡶ࠱࡮ࡸࡵ࡮ࠨᶑ"))
        if os.path.exists(bstack11l1111l11l_opy_):
            with open(bstack11l1111l11l_opy_) as f:
                bstack111llll1111_opy_ = json.load(f)
        bstack111llll1111_opy_.append(bstack1l11111l11_opy_)
        with open(bstack11l1111l11l_opy_, bstack11ll1_opy_ (u"ࠪࡻࠬᶒ")) as f:
            json.dump(bstack111llll1111_opy_, f)
    else:
        bstack1l11111l11_opy_ = {bstack11ll1_opy_ (u"ࠫࡳࡧ࡭ࡦࠩᶓ"): test_name, bstack11ll1_opy_ (u"ࠬ࡫ࡲࡳࡱࡵࠫᶔ"): bstack111ll1l1l1l_opy_, bstack11ll1_opy_ (u"࠭ࡩ࡯ࡦࡨࡼࠬᶕ"): str(multiprocessing.current_process().name)}
        if bstack11ll1_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱ࡟ࡦࡴࡵࡳࡷࡥ࡬ࡪࡵࡷࠫᶖ") not in multiprocessing.current_process().__dict__.keys():
            multiprocessing.current_process().bstack_error_list = []
        multiprocessing.current_process().bstack_error_list.append(bstack1l11111l11_opy_)
  except Exception as e:
      logger.warn(bstack11ll1_opy_ (u"ࠣࡗࡱࡥࡧࡲࡥࠡࡶࡲࠤࡸࡺ࡯ࡳࡧࠣࡴࡾࡺࡥࡴࡶࠣࡪࡺࡴ࡮ࡦ࡮ࠣࡨࡦࡺࡡ࠻ࠢࡾࢁࠧᶗ").format(e))
def bstack11l1l11l11_opy_(error_message, test_name, index, logger):
  try:
    from filelock import FileLock
  except ImportError:
    logger.debug(bstack11ll1_opy_ (u"ࠩࡩ࡭ࡱ࡫࡬ࡰࡥ࡮ࠤࡳࡵࡴࠡࡣࡹࡥ࡮ࡲࡡࡣ࡮ࡨ࠰ࠥࡻࡳࡪࡰࡪࠤࡧࡧࡳࡪࡥࠣࡪ࡮ࡲࡥࠡࡱࡳࡩࡷࡧࡴࡪࡱࡱࡷࠬᶘ"))
    try:
      bstack111ll1ll1l1_opy_ = []
      bstack1l11111l11_opy_ = {bstack11ll1_opy_ (u"ࠪࡲࡦࡳࡥࠨᶙ"): test_name, bstack11ll1_opy_ (u"ࠫࡪࡸࡲࡰࡴࠪᶚ"): error_message, bstack11ll1_opy_ (u"ࠬ࡯࡮ࡥࡧࡻࠫᶛ"): index}
      bstack111l1l11l1l_opy_ = os.path.join(tempfile.gettempdir(), bstack11ll1_opy_ (u"࠭ࡲࡰࡤࡲࡸࡤ࡫ࡲࡳࡱࡵࡣࡱ࡯ࡳࡵ࠰࡭ࡷࡴࡴࠧᶜ"))
      if os.path.exists(bstack111l1l11l1l_opy_):
          with open(bstack111l1l11l1l_opy_) as f:
              bstack111ll1ll1l1_opy_ = json.load(f)
      bstack111ll1ll1l1_opy_.append(bstack1l11111l11_opy_)
      with open(bstack111l1l11l1l_opy_, bstack11ll1_opy_ (u"ࠧࡸࠩᶝ")) as f:
          json.dump(bstack111ll1ll1l1_opy_, f)
    except Exception as e:
      logger.warn(bstack11ll1_opy_ (u"ࠣࡗࡱࡥࡧࡲࡥࠡࡶࡲࠤࡸࡺ࡯ࡳࡧࠣࡶࡴࡨ࡯ࡵࠢࡩࡹࡳࡴࡥ࡭ࠢࡧࡥࡹࡧ࠺ࠡࡽࢀࠦᶞ").format(e))
    return
  bstack111ll1ll1l1_opy_ = []
  bstack1l11111l11_opy_ = {bstack11ll1_opy_ (u"ࠩࡱࡥࡲ࡫ࠧᶟ"): test_name, bstack11ll1_opy_ (u"ࠪࡩࡷࡸ࡯ࡳࠩᶠ"): error_message, bstack11ll1_opy_ (u"ࠫ࡮ࡴࡤࡦࡺࠪᶡ"): index}
  bstack111l1l11l1l_opy_ = os.path.join(tempfile.gettempdir(), bstack11ll1_opy_ (u"ࠬࡸ࡯ࡣࡱࡷࡣࡪࡸࡲࡰࡴࡢࡰ࡮ࡹࡴ࠯࡬ࡶࡳࡳ࠭ᶢ"))
  lock_file = bstack111l1l11l1l_opy_ + bstack11ll1_opy_ (u"࠭࠮࡭ࡱࡦ࡯ࠬᶣ")
  try:
    with FileLock(lock_file, timeout=10):
      if os.path.exists(bstack111l1l11l1l_opy_):
          with open(bstack111l1l11l1l_opy_, bstack11ll1_opy_ (u"ࠧࡳࠩᶤ")) as f:
              content = f.read().strip()
              if content:
                  bstack111ll1ll1l1_opy_ = json.load(open(bstack111l1l11l1l_opy_))
      bstack111ll1ll1l1_opy_.append(bstack1l11111l11_opy_)
      with open(bstack111l1l11l1l_opy_, bstack11ll1_opy_ (u"ࠨࡹࠪᶥ")) as f:
          json.dump(bstack111ll1ll1l1_opy_, f)
  except Exception as e:
    logger.warn(bstack11ll1_opy_ (u"ࠤࡘࡲࡦࡨ࡬ࡦࠢࡷࡳࠥࡹࡴࡰࡴࡨࠤࡷࡵࡢࡰࡶࠣࡪࡺࡴ࡮ࡦ࡮ࠣࡨࡦࡺࡡࠡࡹ࡬ࡸ࡭ࠦࡦࡪ࡮ࡨࠤࡱࡵࡣ࡬࡫ࡱ࡫࠿ࠦࡻࡾࠤᶦ").format(e))
def bstack11lllllll_opy_(bstack11111lll1_opy_, name, logger):
  try:
    bstack1l11111l11_opy_ = {bstack11ll1_opy_ (u"ࠪࡲࡦࡳࡥࠨᶧ"): name, bstack11ll1_opy_ (u"ࠫࡪࡸࡲࡰࡴࠪᶨ"): bstack11111lll1_opy_, bstack11ll1_opy_ (u"ࠬ࡯࡮ࡥࡧࡻࠫᶩ"): str(threading.current_thread()._name)}
    return bstack1l11111l11_opy_
  except Exception as e:
    logger.warn(bstack11ll1_opy_ (u"ࠨࡕ࡯ࡣࡥࡰࡪࠦࡴࡰࠢࡶࡸࡴࡸࡥࠡࡤࡨ࡬ࡦࡼࡥࠡࡨࡸࡲࡳ࡫࡬ࠡࡦࡤࡸࡦࡀࠠࡼࡿࠥᶪ").format(e))
  return
def bstack11l111ll11l_opy_():
    return platform.system() == bstack11ll1_opy_ (u"ࠧࡘ࡫ࡱࡨࡴࡽࡳࠨᶫ")
def bstack1ll1lllll1_opy_(bstack111l1l1ll1l_opy_, config, logger):
    bstack111ll111ll1_opy_ = {}
    try:
        return {key: config[key] for key in config if bstack111l1l1ll1l_opy_.match(key)}
    except Exception as e:
        logger.debug(bstack11ll1_opy_ (u"ࠣࡗࡱࡥࡧࡲࡥࠡࡶࡲࠤ࡫࡯࡬ࡵࡧࡵࠤࡨࡵ࡮ࡧ࡫ࡪࠤࡰ࡫ࡹࡴࠢࡥࡽࠥࡸࡥࡨࡧࡻࠤࡲࡧࡴࡤࡪ࠽ࠤࢀࢃࠢᶬ").format(e))
    return bstack111ll111ll1_opy_
def bstack111ll1111l1_opy_(bstack111l1lll1ll_opy_, bstack111lllll1l1_opy_):
    bstack111ll1llll1_opy_ = version.parse(bstack111l1lll1ll_opy_)
    bstack111lll1llll_opy_ = version.parse(bstack111lllll1l1_opy_)
    if bstack111ll1llll1_opy_ > bstack111lll1llll_opy_:
        return 1
    elif bstack111ll1llll1_opy_ < bstack111lll1llll_opy_:
        return -1
    else:
        return 0
def bstack111l11l1ll_opy_():
    return datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
def bstack111l1ll111l_opy_(timestamp):
    return datetime.datetime.fromtimestamp(timestamp, datetime.timezone.utc).replace(tzinfo=None)
def bstack111ll1l111l_opy_(framework):
    from browserstack_sdk._version import __version__
    return str(framework) + str(__version__)
def bstack1llllll1ll_opy_(options, framework, config, bstack11l1111l11_opy_={}):
    if options is None:
        return
    if getattr(options, bstack11ll1_opy_ (u"ࠩࡪࡩࡹ࠭ᶭ"), None):
        caps = options
    else:
        caps = options.to_capabilities()
    bstack1ll11lllll_opy_ = caps.get(bstack11ll1_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭࠽ࡳࡵࡺࡩࡰࡰࡶࠫᶮ"))
    bstack111lll1ll1l_opy_ = True
    bstack1lllll1l1l_opy_ = os.environ[bstack11ll1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡉࡗࡅࡣ࡚࡛ࡉࡅࠩᶯ")]
    bstack1l11l1l111l_opy_ = config.get(bstack11ll1_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠬᶰ"), False)
    if bstack1l11l1l111l_opy_:
        bstack1l1l1111ll1_opy_ = config.get(bstack11ll1_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࡕࡰࡵ࡫ࡲࡲࡸ࠭ᶱ"), {})
        bstack1l1l1111ll1_opy_[bstack11ll1_opy_ (u"ࠧࡢࡷࡷ࡬࡙ࡵ࡫ࡦࡰࠪᶲ")] = os.getenv(bstack11ll1_opy_ (u"ࠨࡄࡖࡣࡆ࠷࠱࡚ࡡࡍ࡛࡙࠭ᶳ"))
        bstack11l1lll1l11_opy_ = json.loads(os.getenv(bstack11ll1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡥࡁࡄࡅࡈࡗࡘࡏࡂࡊࡎࡌࡘ࡞ࡥࡃࡐࡐࡉࡍࡌ࡛ࡒࡂࡖࡌࡓࡓࡥ࡙ࡎࡎࠪᶴ"), bstack11ll1_opy_ (u"ࠪࡿࢂ࠭ᶵ"))).get(bstack11ll1_opy_ (u"ࠫࡸࡩࡡ࡯ࡰࡨࡶ࡛࡫ࡲࡴ࡫ࡲࡲࠬᶶ"))
    if bstack11l1111llll_opy_(caps.get(bstack11ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡺࡹࡥࡘ࠵ࡆࠫᶷ"))) or bstack11l1111llll_opy_(caps.get(bstack11ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡻࡳࡦࡡࡺ࠷ࡨ࠭ᶸ"))):
        bstack111lll1ll1l_opy_ = False
    if bstack11lll11lll_opy_({bstack11ll1_opy_ (u"ࠢࡶࡵࡨ࡛࠸ࡉࠢᶹ"): bstack111lll1ll1l_opy_}):
        bstack1ll11lllll_opy_ = bstack1ll11lllll_opy_ or {}
        bstack1ll11lllll_opy_[bstack11ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡓࡅࡍࠪᶺ")] = bstack111ll1l111l_opy_(framework)
        bstack1ll11lllll_opy_[bstack11ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡂࡷࡷࡳࡲࡧࡴࡪࡱࡱࠫᶻ")] = bstack1ll111l11l1_opy_()
        bstack1ll11lllll_opy_[bstack11ll1_opy_ (u"ࠪࡸࡪࡹࡴࡩࡷࡥࡆࡺ࡯࡬ࡥࡗࡸ࡭ࡩ࠭ᶼ")] = bstack1lllll1l1l_opy_
        bstack1ll11lllll_opy_[bstack11ll1_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡓࡶࡴࡪࡵࡤࡶࡐࡥࡵ࠭ᶽ")] = bstack11l1111l11_opy_
        if bstack1l11l1l111l_opy_:
            bstack1ll11lllll_opy_[bstack11ll1_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠬᶾ")] = bstack1l11l1l111l_opy_
            bstack1ll11lllll_opy_[bstack11ll1_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࡕࡰࡵ࡫ࡲࡲࡸ࠭ᶿ")] = bstack1l1l1111ll1_opy_
            bstack1ll11lllll_opy_[bstack11ll1_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࡏࡱࡶ࡬ࡳࡳࡹࠧ᷀")][bstack11ll1_opy_ (u"ࠨࡵࡦࡥࡳࡴࡥࡳࡘࡨࡶࡸ࡯࡯࡯ࠩ᷁")] = bstack11l1lll1l11_opy_
        if getattr(options, bstack11ll1_opy_ (u"ࠩࡶࡩࡹࡥࡣࡢࡲࡤࡦ࡮ࡲࡩࡵࡻ᷂ࠪ"), None):
            options.set_capability(bstack11ll1_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭࠽ࡳࡵࡺࡩࡰࡰࡶࠫ᷃"), bstack1ll11lllll_opy_)
        else:
            options[bstack11ll1_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮࠾ࡴࡶࡴࡪࡱࡱࡷࠬ᷄")] = bstack1ll11lllll_opy_
    else:
        if getattr(options, bstack11ll1_opy_ (u"ࠬࡹࡥࡵࡡࡦࡥࡵࡧࡢࡪ࡮࡬ࡸࡾ࠭᷅"), None):
            options.set_capability(bstack11ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡗࡉࡑࠧ᷆"), bstack111ll1l111l_opy_(framework))
            options.set_capability(bstack11ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡆࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠨ᷇"), bstack1ll111l11l1_opy_())
            options.set_capability(bstack11ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡵࡧࡶࡸ࡭ࡻࡢࡃࡷ࡬ࡰࡩ࡛ࡵࡪࡦࠪ᷈"), bstack1lllll1l1l_opy_)
            options.set_capability(bstack11ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡤࡸ࡭ࡱࡪࡐࡳࡱࡧࡹࡨࡺࡍࡢࡲࠪ᷉"), bstack11l1111l11_opy_)
            if bstack1l11l1l111l_opy_:
                options.set_capability(bstack11ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺ᷊ࠩ"), bstack1l11l1l111l_opy_)
                options.set_capability(bstack11ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࡒࡴࡹ࡯࡯࡯ࡵࠪ᷋"), bstack1l1l1111ll1_opy_)
                options.set_capability(bstack11ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࡓࡵࡺࡩࡰࡰࡶ࠲ࡸࡩࡡ࡯ࡰࡨࡶ࡛࡫ࡲࡴ࡫ࡲࡲࠬ᷌"), bstack11l1lll1l11_opy_)
        else:
            options[bstack11ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡗࡉࡑࠧ᷍")] = bstack111ll1l111l_opy_(framework)
            options[bstack11ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡆࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠨ᷎")] = bstack1ll111l11l1_opy_()
            options[bstack11ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡵࡧࡶࡸ࡭ࡻࡢࡃࡷ࡬ࡰࡩ࡛ࡵࡪࡦ᷏ࠪ")] = bstack1lllll1l1l_opy_
            options[bstack11ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡤࡸ࡭ࡱࡪࡐࡳࡱࡧࡹࡨࡺࡍࡢࡲ᷐ࠪ")] = bstack11l1111l11_opy_
            if bstack1l11l1l111l_opy_:
                options[bstack11ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠩ᷑")] = bstack1l11l1l111l_opy_
                options[bstack11ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࡒࡴࡹ࡯࡯࡯ࡵࠪ᷒")] = bstack1l1l1111ll1_opy_
                options[bstack11ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࡓࡵࡺࡩࡰࡰࡶࠫᷓ")][bstack11ll1_opy_ (u"࠭ࡳࡤࡣࡱࡲࡪࡸࡖࡦࡴࡶ࡭ࡴࡴࠧᷔ")] = bstack11l1lll1l11_opy_
    return options
def bstack111ll11llll_opy_(bstack11l111l11l1_opy_, framework):
    bstack11l1111l11_opy_ = bstack1l1l1ll1l_opy_.get_property(bstack11ll1_opy_ (u"ࠢࡑࡎࡄ࡝࡜ࡘࡉࡈࡊࡗࡣࡕࡘࡏࡅࡗࡆࡘࡤࡓࡁࡑࠤᷕ"))
    if bstack11l111l11l1_opy_ and len(bstack11l111l11l1_opy_.split(bstack11ll1_opy_ (u"ࠨࡥࡤࡴࡸࡃࠧᷖ"))) > 1:
        ws_url = bstack11l111l11l1_opy_.split(bstack11ll1_opy_ (u"ࠩࡦࡥࡵࡹ࠽ࠨᷗ"))[0]
        if bstack11ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡦࡳࡲ࠭ᷘ") in ws_url:
            from browserstack_sdk._version import __version__
            bstack111ll11111l_opy_ = json.loads(urllib.parse.unquote(bstack11l111l11l1_opy_.split(bstack11ll1_opy_ (u"ࠫࡨࡧࡰࡴ࠿ࠪᷙ"))[1]))
            bstack111ll11111l_opy_ = bstack111ll11111l_opy_ or {}
            bstack1lllll1l1l_opy_ = os.environ[bstack11ll1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡊࡘࡆࡤ࡛ࡕࡊࡆࠪᷚ")]
            bstack111ll11111l_opy_[bstack11ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡗࡉࡑࠧᷛ")] = str(framework) + str(__version__)
            bstack111ll11111l_opy_[bstack11ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡆࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠨᷜ")] = bstack1ll111l11l1_opy_()
            bstack111ll11111l_opy_[bstack11ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡵࡧࡶࡸ࡭ࡻࡢࡃࡷ࡬ࡰࡩ࡛ࡵࡪࡦࠪᷝ")] = bstack1lllll1l1l_opy_
            bstack111ll11111l_opy_[bstack11ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡤࡸ࡭ࡱࡪࡐࡳࡱࡧࡹࡨࡺࡍࡢࡲࠪᷞ")] = bstack11l1111l11_opy_
            bstack11l111l11l1_opy_ = bstack11l111l11l1_opy_.split(bstack11ll1_opy_ (u"ࠪࡧࡦࡶࡳ࠾ࠩᷟ"))[0] + bstack11ll1_opy_ (u"ࠫࡨࡧࡰࡴ࠿ࠪᷠ") + urllib.parse.quote(json.dumps(bstack111ll11111l_opy_))
    return bstack11l111l11l1_opy_
def bstack1l11l1l1_opy_():
    global bstack11l1llll11_opy_
    from playwright._impl._browser_type import BrowserType
    bstack11l1llll11_opy_ = BrowserType.connect
    return bstack11l1llll11_opy_
def bstack11ll111ll1_opy_(framework_name):
    global bstack11l1l11ll_opy_
    bstack11l1l11ll_opy_ = framework_name
    return framework_name
def bstack11ll1l1ll_opy_(self, *args, **kwargs):
    global bstack11l1llll11_opy_
    try:
        global bstack11l1l11ll_opy_
        if bstack11ll1_opy_ (u"ࠬࡽࡳࡆࡰࡧࡴࡴ࡯࡮ࡵࠩᷡ") in kwargs:
            kwargs[bstack11ll1_opy_ (u"࠭ࡷࡴࡇࡱࡨࡵࡵࡩ࡯ࡶࠪᷢ")] = bstack111ll11llll_opy_(
                kwargs.get(bstack11ll1_opy_ (u"ࠧࡸࡵࡈࡲࡩࡶ࡯ࡪࡰࡷࠫᷣ"), None),
                bstack11l1l11ll_opy_
            )
    except Exception as e:
        logger.error(bstack11ll1_opy_ (u"ࠣࡇࡵࡶࡴࡸࠠࡸࡪࡨࡲࠥࡶࡲࡰࡥࡨࡷࡸ࡯࡮ࡨࠢࡖࡈࡐࠦࡣࡢࡲࡶ࠾ࠥࢁࡽࠣᷤ").format(str(e)))
    return bstack11l1llll11_opy_(self, *args, **kwargs)
def bstack111ll1l1ll1_opy_(bstack111l1l11l11_opy_, proxies):
    proxy_settings = {}
    try:
        if not proxies:
            proxies = bstack1lllll1111_opy_(bstack111l1l11l11_opy_, bstack11ll1_opy_ (u"ࠤࠥᷥ"))
        if proxies and proxies.get(bstack11ll1_opy_ (u"ࠥ࡬ࡹࡺࡰࡴࠤᷦ")):
            parsed_url = urlparse(proxies.get(bstack11ll1_opy_ (u"ࠦ࡭ࡺࡴࡱࡵࠥᷧ")))
            if parsed_url and parsed_url.hostname: proxy_settings[bstack11ll1_opy_ (u"ࠬࡶࡲࡰࡺࡼࡌࡴࡹࡴࠨᷨ")] = str(parsed_url.hostname)
            if parsed_url and parsed_url.port: proxy_settings[bstack11ll1_opy_ (u"࠭ࡰࡳࡱࡻࡽࡕࡵࡲࡵࠩᷩ")] = str(parsed_url.port)
            if parsed_url and parsed_url.username: proxy_settings[bstack11ll1_opy_ (u"ࠧࡱࡴࡲࡼࡾ࡛ࡳࡦࡴࠪᷪ")] = str(parsed_url.username)
            if parsed_url and parsed_url.password: proxy_settings[bstack11ll1_opy_ (u"ࠨࡲࡵࡳࡽࡿࡐࡢࡵࡶࠫᷫ")] = str(parsed_url.password)
        return proxy_settings
    except:
        return proxy_settings
def bstack11l111lll_opy_(bstack111l1l11l11_opy_):
    bstack111ll1l11ll_opy_ = {
        bstack11l1l1l1lll_opy_[bstack111l1ll11ll_opy_]: bstack111l1l11l11_opy_[bstack111l1ll11ll_opy_]
        for bstack111l1ll11ll_opy_ in bstack111l1l11l11_opy_
        if bstack111l1ll11ll_opy_ in bstack11l1l1l1lll_opy_
    }
    bstack111ll1l11ll_opy_[bstack11ll1_opy_ (u"ࠤࡳࡶࡴࡾࡹࡔࡧࡷࡸ࡮ࡴࡧࡴࠤᷬ")] = bstack111ll1l1ll1_opy_(bstack111l1l11l11_opy_, bstack1l1l1ll1l_opy_.get_property(bstack11ll1_opy_ (u"ࠥࡴࡷࡵࡸࡺࡕࡨࡸࡹ࡯࡮ࡨࡵࠥᷭ")))
    bstack111lll1l111_opy_ = [element.lower() for element in bstack11l11ll11ll_opy_]
    bstack111ll11l1ll_opy_(bstack111ll1l11ll_opy_, bstack111lll1l111_opy_)
    return bstack111ll1l11ll_opy_
def bstack111ll11l1ll_opy_(d, keys):
    for key in list(d.keys()):
        if key.lower() in keys:
            d[key] = bstack11ll1_opy_ (u"ࠦ࠯࠰ࠪࠫࠤᷮ")
    for value in d.values():
        if isinstance(value, dict):
            bstack111ll11l1ll_opy_(value, keys)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    bstack111ll11l1ll_opy_(item, keys)
def bstack1llll111l1l_opy_():
    bstack111l1l11ll1_opy_ = [os.environ.get(bstack11ll1_opy_ (u"ࠧࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡋࡏࡌࡆࡕࡢࡈࡎࡘࠢᷯ")), os.path.join(os.path.expanduser(bstack11ll1_opy_ (u"ࠨࡾࠣᷰ")), bstack11ll1_opy_ (u"ࠧ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠧᷱ")), os.path.join(bstack11ll1_opy_ (u"ࠨ࠱ࡷࡱࡵ࠭ᷲ"), bstack11ll1_opy_ (u"ࠩ࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࠩᷳ"))]
    for path in bstack111l1l11ll1_opy_:
        if path is None:
            continue
        try:
            if os.path.exists(path):
                logger.debug(bstack11ll1_opy_ (u"ࠥࡊ࡮ࡲࡥࠡࠩࠥᷴ") + str(path) + bstack11ll1_opy_ (u"ࠦࠬࠦࡥࡹ࡫ࡶࡸࡸ࠴ࠢ᷵"))
                if not os.access(path, os.W_OK):
                    logger.debug(bstack11ll1_opy_ (u"ࠧࡍࡩࡷ࡫ࡱ࡫ࠥࡶࡥࡳ࡯࡬ࡷࡸ࡯࡯࡯ࡵࠣࡪࡴࡸࠠࠨࠤ᷶") + str(path) + bstack11ll1_opy_ (u"ࠨ᷷ࠧࠣ"))
                    os.chmod(path, 0o777)
                else:
                    logger.debug(bstack11ll1_opy_ (u"ࠢࡇ࡫࡯ࡩ᷸ࠥ࠭ࠢ") + str(path) + bstack11ll1_opy_ (u"ࠣࠩࠣࡥࡱࡸࡥࡢࡦࡼࠤ࡭ࡧࡳࠡࡶ࡫ࡩࠥࡸࡥࡲࡷ࡬ࡶࡪࡪࠠࡱࡧࡵࡱ࡮ࡹࡳࡪࡱࡱࡷ࠳ࠨ᷹"))
            else:
                logger.debug(bstack11ll1_opy_ (u"ࠤࡆࡶࡪࡧࡴࡪࡰࡪࠤ࡫࡯࡬ࡦ᷺ࠢࠪࠦ") + str(path) + bstack11ll1_opy_ (u"ࠥࠫࠥࡽࡩࡵࡪࠣࡻࡷ࡯ࡴࡦࠢࡳࡩࡷࡳࡩࡴࡵ࡬ࡳࡳ࠴ࠢ᷻"))
                os.makedirs(path, exist_ok=True)
                os.chmod(path, 0o777)
            logger.debug(bstack11ll1_opy_ (u"ࠦࡔࡶࡥࡳࡣࡷ࡭ࡴࡴࠠࡴࡷࡦࡧࡪ࡫ࡤࡦࡦࠣࡪࡴࡸࠠࠨࠤ᷼") + str(path) + bstack11ll1_opy_ (u"ࠧ࠭࠮᷽ࠣ"))
            return path
        except Exception as e:
            logger.debug(bstack11ll1_opy_ (u"ࠨࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡶࡩࡹࠦࡵࡱࠢࡩ࡭ࡱ࡫ࠠࠨࡽࡳࡥࡹ࡮ࡽࠨ࠼ࠣࠦ᷾") + str(e) + bstack11ll1_opy_ (u"᷿ࠢࠣ"))
    logger.debug(bstack11ll1_opy_ (u"ࠣࡃ࡯ࡰࠥࡶࡡࡵࡪࡶࠤ࡫ࡧࡩ࡭ࡧࡧ࠲ࠧḀ"))
    return None
@measure(event_name=EVENTS.bstack11l11ll1l11_opy_, stage=STAGE.bstack11l1llll1_opy_)
def bstack1l11lll11ll_opy_(binary_path, bstack1l1ll1l1ll1_opy_, bs_config):
    logger.debug(bstack11ll1_opy_ (u"ࠤࡆࡹࡷࡸࡥ࡯ࡶࠣࡇࡑࡏࠠࡑࡣࡷ࡬ࠥ࡬࡯ࡶࡰࡧ࠾ࠥࢁࡽࠣḁ").format(binary_path))
    bstack111lll11l1l_opy_ = bstack11ll1_opy_ (u"ࠪࠫḂ")
    bstack111l1llllll_opy_ = {
        bstack11ll1_opy_ (u"ࠫࡸࡪ࡫ࡠࡸࡨࡶࡸ࡯࡯࡯ࠩḃ"): __version__,
        bstack11ll1_opy_ (u"ࠧࡵࡳࠣḄ"): platform.system(),
        bstack11ll1_opy_ (u"ࠨ࡯ࡴࡡࡤࡶࡨ࡮ࠢḅ"): platform.machine(),
        bstack11ll1_opy_ (u"ࠢࡤ࡮࡬ࡣࡻ࡫ࡲࡴ࡫ࡲࡲࠧḆ"): bstack11ll1_opy_ (u"ࠨ࠲ࠪḇ"),
        bstack11ll1_opy_ (u"ࠤࡶࡨࡰࡥ࡬ࡢࡰࡪࡹࡦ࡭ࡥࠣḈ"): bstack11ll1_opy_ (u"ࠪࡴࡾࡺࡨࡰࡰࠪḉ")
    }
    bstack111ll11l1l1_opy_(bstack111l1llllll_opy_)
    try:
        if binary_path:
            if bstack11l111ll11l_opy_():
                bstack111l1llllll_opy_[bstack11ll1_opy_ (u"ࠫࡨࡲࡩࡠࡸࡨࡶࡸ࡯࡯࡯ࠩḊ")] = subprocess.check_output([binary_path, bstack11ll1_opy_ (u"ࠧࡼࡥࡳࡵ࡬ࡳࡳࠨḋ")]).strip().decode(bstack11ll1_opy_ (u"࠭ࡵࡵࡨ࠰࠼ࠬḌ"))
            else:
                bstack111l1llllll_opy_[bstack11ll1_opy_ (u"ࠧࡤ࡮࡬ࡣࡻ࡫ࡲࡴ࡫ࡲࡲࠬḍ")] = subprocess.check_output([binary_path, bstack11ll1_opy_ (u"ࠣࡸࡨࡶࡸ࡯࡯࡯ࠤḎ")], stderr=subprocess.DEVNULL).strip().decode(bstack11ll1_opy_ (u"ࠩࡸࡸ࡫࠳࠸ࠨḏ"))
        response = requests.request(
            bstack11ll1_opy_ (u"ࠪࡋࡊ࡚ࠧḐ"),
            url=bstack1111l1lll_opy_(bstack11l11lll11l_opy_),
            headers=None,
            auth=(bs_config[bstack11ll1_opy_ (u"ࠫࡺࡹࡥࡳࡐࡤࡱࡪ࠭ḑ")], bs_config[bstack11ll1_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷࡐ࡫ࡹࠨḒ")]),
            json=None,
            params=bstack111l1llllll_opy_
        )
        data = response.json()
        if response.status_code == 200 and bstack11ll1_opy_ (u"࠭ࡵࡳ࡮ࠪḓ") in data.keys() and bstack11ll1_opy_ (u"ࠧࡶࡲࡧࡥࡹ࡫ࡤࡠࡥ࡯࡭ࡤࡼࡥࡳࡵ࡬ࡳࡳ࠭Ḕ") in data.keys():
            logger.debug(bstack11ll1_opy_ (u"ࠣࡐࡨࡩࡩࠦࡴࡰࠢࡸࡴࡩࡧࡴࡦࠢࡥ࡭ࡳࡧࡲࡺ࠮ࠣࡧࡺࡸࡲࡦࡰࡷࠤࡧ࡯࡮ࡢࡴࡼࠤࡻ࡫ࡲࡴ࡫ࡲࡲ࠿ࠦࡻࡾࠤḕ").format(bstack111l1llllll_opy_[bstack11ll1_opy_ (u"ࠩࡦࡰ࡮ࡥࡶࡦࡴࡶ࡭ࡴࡴࠧḖ")]))
            if bstack11ll1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡅࡍࡓࡇࡒ࡚ࡡࡘࡖࡑ࠭ḗ") in os.environ:
                logger.debug(bstack11ll1_opy_ (u"ࠦࡘࡱࡩࡱࡲ࡬ࡲ࡬ࠦࡢࡪࡰࡤࡶࡾࠦࡤࡰࡹࡱࡰࡴࡧࡤࠡࡣࡶࠤࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡆࡎࡔࡁࡓ࡛ࡢ࡙ࡗࡒࠠࡪࡵࠣࡷࡪࡺࠢḘ"))
                data[bstack11ll1_opy_ (u"ࠬࡻࡲ࡭ࠩḙ")] = os.environ[bstack11ll1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡈࡉࡏࡃࡕ࡝ࡤ࡛ࡒࡍࠩḚ")]
            bstack111ll1111ll_opy_ = bstack11l111ll111_opy_(data[bstack11ll1_opy_ (u"ࠧࡶࡴ࡯ࠫḛ")], bstack1l1ll1l1ll1_opy_)
            bstack111lll11l1l_opy_ = os.path.join(bstack1l1ll1l1ll1_opy_, bstack111ll1111ll_opy_)
            os.chmod(bstack111lll11l1l_opy_, 0o777) # bstack111l1lll11l_opy_ permission
            return bstack111lll11l1l_opy_
    except Exception as e:
        logger.debug(bstack11ll1_opy_ (u"ࠣࡇࡵࡶࡴࡸࠠࡸࡪ࡬ࡰࡪࠦࡤࡰࡹࡱࡰࡴࡧࡤࡪࡰࡪࠤࡳ࡫ࡷࠡࡕࡇࡏࠥࢁࡽࠣḜ").format(e))
    return binary_path
def bstack111ll11l1l1_opy_(bstack111l1llllll_opy_):
    try:
        if bstack11ll1_opy_ (u"ࠩ࡯࡭ࡳࡻࡸࠨḝ") not in bstack111l1llllll_opy_[bstack11ll1_opy_ (u"ࠪࡳࡸ࠭Ḟ")].lower():
            return
        if os.path.exists(bstack11ll1_opy_ (u"ࠦ࠴࡫ࡴࡤ࠱ࡲࡷ࠲ࡸࡥ࡭ࡧࡤࡷࡪࠨḟ")):
            with open(bstack11ll1_opy_ (u"ࠧ࠵ࡥࡵࡥ࠲ࡳࡸ࠳ࡲࡦ࡮ࡨࡥࡸ࡫ࠢḠ"), bstack11ll1_opy_ (u"ࠨࡲࠣḡ")) as f:
                bstack11l1111l1ll_opy_ = {}
                for line in f:
                    if bstack11ll1_opy_ (u"ࠢ࠾ࠤḢ") in line:
                        key, value = line.rstrip().split(bstack11ll1_opy_ (u"ࠣ࠿ࠥḣ"), 1)
                        bstack11l1111l1ll_opy_[key] = value.strip(bstack11ll1_opy_ (u"ࠩࠥࡠࠬ࠭Ḥ"))
                bstack111l1llllll_opy_[bstack11ll1_opy_ (u"ࠪࡨ࡮ࡹࡴࡳࡱࠪḥ")] = bstack11l1111l1ll_opy_.get(bstack11ll1_opy_ (u"ࠦࡎࡊࠢḦ"), bstack11ll1_opy_ (u"ࠧࠨḧ"))
        elif os.path.exists(bstack11ll1_opy_ (u"ࠨ࠯ࡦࡶࡦ࠳ࡦࡲࡰࡪࡰࡨ࠱ࡷ࡫࡬ࡦࡣࡶࡩࠧḨ")):
            bstack111l1llllll_opy_[bstack11ll1_opy_ (u"ࠧࡥ࡫ࡶࡸࡷࡵࠧḩ")] = bstack11ll1_opy_ (u"ࠨࡣ࡯ࡴ࡮ࡴࡥࠨḪ")
    except Exception as e:
        logger.debug(bstack11ll1_opy_ (u"ࠤࡘࡲࡦࡨ࡬ࡦࠢࡷࡳࠥ࡭ࡥࡵࠢࡧ࡭ࡸࡺࡲࡰࠢࡲࡪࠥࡲࡩ࡯ࡷࡻࠦḫ") + e)
@measure(event_name=EVENTS.bstack11l1l111l1l_opy_, stage=STAGE.bstack11l1llll1_opy_)
def bstack11l111ll111_opy_(bstack11l11111111_opy_, bstack111l1l1l1ll_opy_):
    logger.debug(bstack11ll1_opy_ (u"ࠥࡈࡴࡽ࡮࡭ࡱࡤࡨ࡮ࡴࡧࠡࡕࡇࡏࠥࡨࡩ࡯ࡣࡵࡽࠥ࡬ࡲࡰ࡯࠽ࠤࠧḬ") + str(bstack11l11111111_opy_) + bstack11ll1_opy_ (u"ࠦࠧḭ"))
    zip_path = os.path.join(bstack111l1l1l1ll_opy_, bstack11ll1_opy_ (u"ࠧࡪ࡯ࡸࡰ࡯ࡳࡦࡪࡥࡥࡡࡩ࡭ࡱ࡫࠮ࡻ࡫ࡳࠦḮ"))
    bstack111ll1111ll_opy_ = bstack11ll1_opy_ (u"࠭ࠧḯ")
    with requests.get(bstack11l11111111_opy_, stream=True) as response:
        response.raise_for_status()
        with open(zip_path, bstack11ll1_opy_ (u"ࠢࡸࡤࠥḰ")) as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
        logger.debug(bstack11ll1_opy_ (u"ࠣࡈ࡬ࡰࡪࠦࡤࡰࡹࡱࡰࡴࡧࡤࡦࡦࠣࡷࡺࡩࡣࡦࡵࡶࡪࡺࡲ࡬ࡺ࠰ࠥḱ"))
    with zipfile.ZipFile(zip_path, bstack11ll1_opy_ (u"ࠩࡵࠫḲ")) as zip_ref:
        bstack11l11111l1l_opy_ = zip_ref.namelist()
        if len(bstack11l11111l1l_opy_) > 0:
            bstack111ll1111ll_opy_ = bstack11l11111l1l_opy_[0] # bstack111l1l1l1l1_opy_ bstack11l1l11ll11_opy_ will be bstack111ll1l1lll_opy_ 1 file i.e. the binary in the zip
        zip_ref.extractall(bstack111l1l1l1ll_opy_)
        logger.debug(bstack11ll1_opy_ (u"ࠥࡊ࡮ࡲࡥࡴࠢࡶࡹࡨࡩࡥࡴࡵࡩࡹࡱࡲࡹࠡࡧࡻࡸࡷࡧࡣࡵࡧࡧࠤࡹࡵࠠࠨࠤḳ") + str(bstack111l1l1l1ll_opy_) + bstack11ll1_opy_ (u"ࠦࠬࠨḴ"))
    os.remove(zip_path)
    return bstack111ll1111ll_opy_
def get_cli_dir():
    bstack111llll1ll1_opy_ = bstack1llll111l1l_opy_()
    if bstack111llll1ll1_opy_:
        bstack1l1ll1l1ll1_opy_ = os.path.join(bstack111llll1ll1_opy_, bstack11ll1_opy_ (u"ࠧࡩ࡬ࡪࠤḵ"))
        if not os.path.exists(bstack1l1ll1l1ll1_opy_):
            os.makedirs(bstack1l1ll1l1ll1_opy_, mode=0o777, exist_ok=True)
        return bstack1l1ll1l1ll1_opy_
    else:
        raise FileNotFoundError(bstack11ll1_opy_ (u"ࠨࡎࡰࠢࡺࡶ࡮ࡺࡡࡣ࡮ࡨࠤࡩ࡯ࡲࡦࡥࡷࡳࡷࡿࠠࡢࡸࡤ࡭ࡱࡧࡢ࡭ࡧࠣࡪࡴࡸࠠࡵࡪࡨࠤࡘࡊࡋࠡࡤ࡬ࡲࡦࡸࡹ࠯ࠤḶ"))
def bstack1l1ll1ll11l_opy_(bstack1l1ll1l1ll1_opy_):
    bstack11ll1_opy_ (u"ࠢࠣࠤࡊࡩࡹࠦࡴࡩࡧࠣࡴࡦࡺࡨࠡࡨࡲࡶࠥࡺࡨࡦࠢࡅࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࠡࡕࡇࡏࠥࡨࡩ࡯ࡣࡵࡽࠥ࡯࡮ࠡࡣࠣࡻࡷ࡯ࡴࡢࡤ࡯ࡩࠥࡪࡩࡳࡧࡦࡸࡴࡸࡹ࠯ࠤࠥࠦḷ")
    bstack111lll1l1ll_opy_ = [
        os.path.join(bstack1l1ll1l1ll1_opy_, f)
        for f in os.listdir(bstack1l1ll1l1ll1_opy_)
        if os.path.isfile(os.path.join(bstack1l1ll1l1ll1_opy_, f)) and f.startswith(bstack11ll1_opy_ (u"ࠣࡤ࡬ࡲࡦࡸࡹ࠮ࠤḸ"))
    ]
    if len(bstack111lll1l1ll_opy_) > 0:
        return max(bstack111lll1l1ll_opy_, key=os.path.getmtime) # get bstack111ll1l1l11_opy_ binary
    return bstack11ll1_opy_ (u"ࠤࠥḹ")
def bstack11l1lll11ll_opy_():
  from selenium import webdriver
  return version.parse(webdriver.__version__)
def bstack1l11l11l1l1_opy_(d, u):
  for k, v in u.items():
    if isinstance(v, collections.abc.Mapping):
      d[k] = bstack1l11l11l1l1_opy_(d.get(k, {}), v)
    else:
      if isinstance(v, list):
        d[k] = d.get(k, []) + v
      else:
        d[k] = v
  return d
def bstack1ll1l111_opy_(data, keys, default=None):
    bstack11ll1_opy_ (u"ࠥࠦࠧࠐࠠࠡࠢࠣࡗࡦ࡬ࡥ࡭ࡻࠣ࡫ࡪࡺࠠࡢࠢࡱࡩࡸࡺࡥࡥࠢࡹࡥࡱࡻࡥࠡࡨࡵࡳࡲࠦࡡࠡࡦ࡬ࡧࡹ࡯࡯࡯ࡣࡵࡽࠥࡵࡲࠡ࡮࡬ࡷࡹ࠴ࠊࠡࠢࠣࠤ࠿ࡶࡡࡳࡣࡰࠤࡩࡧࡴࡢ࠼ࠣࡘ࡭࡫ࠠࡥ࡫ࡦࡸ࡮ࡵ࡮ࡢࡴࡼࠤࡴࡸࠠ࡭࡫ࡶࡸࠥࡺ࡯ࠡࡶࡵࡥࡻ࡫ࡲࡴࡧ࠱ࠎࠥࠦࠠࠡ࠼ࡳࡥࡷࡧ࡭ࠡ࡭ࡨࡽࡸࡀࠠࡂࠢ࡯࡭ࡸࡺࠠࡰࡨࠣ࡯ࡪࡿࡳ࠰࡫ࡱࡨ࡮ࡩࡥࡴࠢࡵࡩࡵࡸࡥࡴࡧࡱࡸ࡮ࡴࡧࠡࡶ࡫ࡩࠥࡶࡡࡵࡪ࠱ࠎࠥࠦࠠࠡ࠼ࡳࡥࡷࡧ࡭ࠡࡦࡨࡪࡦࡻ࡬ࡵ࠼࡚ࠣࡦࡲࡵࡦࠢࡷࡳࠥࡸࡥࡵࡷࡵࡲࠥ࡯ࡦࠡࡶ࡫ࡩࠥࡶࡡࡵࡪࠣࡨࡴ࡫ࡳࠡࡰࡲࡸࠥ࡫ࡸࡪࡵࡷ࠲ࠏࠦࠠࠡࠢ࠽ࡶࡪࡺࡵࡳࡰ࠽ࠤ࡙࡮ࡥࠡࡸࡤࡰࡺ࡫ࠠࡢࡶࠣࡸ࡭࡫ࠠ࡯ࡧࡶࡸࡪࡪࠠࡱࡣࡷ࡬࠱ࠦ࡯ࡳࠢࡧࡩ࡫ࡧࡵ࡭ࡶࠣ࡭࡫ࠦ࡮ࡰࡶࠣࡪࡴࡻ࡮ࡥ࠰ࠍࠤࠥࠦࠠࠣࠤࠥḺ")
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
def bstack1l11llllll_opy_(bstack11l1111ll1l_opy_, key, value):
    bstack11ll1_opy_ (u"ࠦࠧࠨࠊࠡࠢࠣࠤࡘࡺ࡯ࡳࡧࠣࡇࡑࡏࠠࡦࡰࡹ࡭ࡷࡵ࡮࡮ࡧࡱࡸࠥࡼࡡࡳ࡫ࡤࡦࡱ࡫ࡳࠡ࡯ࡤࡴࡵ࡯࡮ࡨࠢ࡬ࡲࠥࡺࡨࡦࠢࡳࡶࡴࡼࡩࡥࡧࡧࠤࡩ࡯ࡣࡵ࡫ࡲࡲࡦࡸࡹ࠯ࠌࠣࠤࠥࠦࡁࡳࡩࡶ࠾ࠏࠦࠠࠡࠢࠣࠤࠥࠦࡣ࡭࡫ࡢࡩࡳࡼ࡟ࡷࡣࡵࡷࡤࡳࡡࡱ࠼ࠣࡈ࡮ࡩࡴࡪࡱࡱࡥࡷࡿࠠࡵࡱࠣࡷࡹࡵࡲࡦࠢࡨࡲࡻ࡯ࡲࡰࡰࡰࡩࡳࡺࠠࡷࡣࡵ࡭ࡦࡨ࡬ࡦࠢࡰࡥࡵࡶࡩ࡯ࡩࡶࠎࠥࠦࠠࠡࠢࠣࠤࠥࡱࡥࡺ࠼ࠣࡏࡪࡿࠠࡧࡴࡲࡱࠥࡉࡌࡊࡡࡆࡅࡕ࡙࡟ࡕࡑࡢࡇࡔࡔࡆࡊࡉࠍࠤࠥࠦࠠࠡࠢࠣࠤࡻࡧ࡬ࡶࡧ࠽ࠤ࡛ࡧ࡬ࡶࡧࠣࡪࡷࡵ࡭ࠡࡥࡲࡱࡲࡧ࡮ࡥࠢ࡯࡭ࡳ࡫ࠠࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠍࠤࠥࠦࠠࠣࠤࠥḻ")
    if key in bstack1l1ll11l11_opy_:
        bstack1llll1l1l_opy_ = bstack1l1ll11l11_opy_[key]
        if isinstance(bstack1llll1l1l_opy_, list):
            for env_name in bstack1llll1l1l_opy_:
                bstack11l1111ll1l_opy_[env_name] = value
        else:
            bstack11l1111ll1l_opy_[bstack1llll1l1l_opy_] = value