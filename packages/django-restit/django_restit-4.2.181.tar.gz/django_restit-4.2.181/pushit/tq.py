from pushit import utils


def run_update(task):
    proj_info = utils.getProjectInfo(task.data.project, task.data.branch)
    if proj_info is None:
        task.failed(f"{utils.settings.HOSTNAME} - no project for {task.data.project}:{task.data.branch}")
    else:
        utils.updateCode(proj_info.get("updater", None), task.data.branch)
        task.log(f"{utils.settings.HOSTNAME} - completed")
        task.completed()
