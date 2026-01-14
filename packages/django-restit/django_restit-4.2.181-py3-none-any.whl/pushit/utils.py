from rest import settings
from rest import log
from objict import objict
import os
import subprocess

GIT_PROJECTS = settings.get("GIT_PROJECTS", None)
logger = log.getLogger("pushit", filename="pushit.log")


def updateCode(update_cmd, branch, update_user="ec2-user"):
    if settings.PUSHIT_TEST_SUDO:
        cmd = ["sudo", "-lU", update_user, update_cmd, branch]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        if err.strip():
            logger.warning("WARNING: cannot run {}, we don't have sudo rights".format(update_cmd))
            logger.warning("WARNING: add {} to your sudo user".format(update_cmd))
            return
    # - lock it so we kill any updates in progress and start a new one
    cmd = ["sudo", "-u", update_user, update_cmd, branch]
    logger.info("updating...", cmd)
    subprocess.Popen(cmd, close_fds=True)


def parseGitLab(request):
    info = objict(vendor="gitlab")
    info.name = request.DATA.get("project.name")
    info.kind = request.DATA.get("object_kind")
    if "ref" in request.DATA:
        info.branch = request.DATA.get("ref").split('/')[-1]
    if info.kind == "merge_request":
        info.state = request.DATA.get("object_attributes.state", None)
        if info.state == "merged":
            info.kind = "merged"
    return info


def parseGithub(request):
    info = objict(vendor="github")
    info.name = request.DATA.get("repository.name")
    info.kind = request.DATA.getHeader("HTTP_X_GITHUB_EVENT")
    if "ref" in request.DATA:
        info.branch = request.DATA.get("ref").split('/')[-1]
    logger.info("github request", info)
    return info


def getProjectInfo(name, branch):
    return getProjectForBranch(GIT_PROJECTS.get(name, None), branch)


def getProjectForBranch(proj_info, branch):
    if proj_info is None:
        return None
    if isinstance(proj_info, list):
        for pi in proj_info:
            if pi["branch"] == branch:
                return pi
        return None
    if proj_info["branch"] == branch:
        return proj_info
    return None
