from pathlib import Path
from subprocess import CompletedProcess

from beetools import script
from beetools import utils


def activate(p_venv_root_dir, p_venv_name) -> str:
    """Compile command to activate a virtual environment

    This method is useful in the exec_batch_in_session() method to invoke a virtual
    environment in a session to execute other commands in the virtual
    environment.

    Parameters
    ----------
    p_venv_root_dir
        This is the "root" folder of the virtual environment will be
        created in
    p_venv_name
        The name of the virtual environment.

    Returns
    -------
    str
        The command to activate the virtual environment depending on the
        operating system.

    Examples
    --------
    # No proper doctest (<<<) because it is os dependent
    activate(get_tmp_dir(),'new-project')
    'source /tmp/new-project_env/bin/activate'

    """
    if utils.get_os() in [utils.LINUX, utils.MACOS]:
        cmd = "source {}".format(get_dir(p_venv_root_dir, p_venv_name) / Path("bin", "activate"))
    else:
        cmd = "CALL {}".format(get_dir(p_venv_root_dir, p_venv_name) / Path("Scripts", "activate"))
    return cmd


def get_dir(p_venv_root_dir, p_name_pref) -> Path:
    """Compile the virtual environment root folder in Bright Edge eServices format

    Parameters
    ----------
    p_name_pref
    p_venv_root_dir
        This is the "root" folder of the virtual environment will be
        created in

    Returns
    -------
    Path
        Path object with virtual environment name

    Examples
    --------
    # No proper doctest (<<<) because it is os dependent
    beetools.get_dir(beetools.get_tmp_dir(), 'new-project')
    PosixPath('/tmp/new-project_env')

    """
    return p_venv_root_dir / Path(f"{p_name_pref}_env")


def install_in(p_venv_root_dir, p_venv_name, p_instructions, p_verbose=True):
    """Execute (install) commands in a virtual environment

    Parameters
    ----------
    p_venv_root_dir
        This is the "root" folder of the virtual environment will be created in
    p_venv_name
        The name of the virtual environment.
    p_instructions
        Instructions to execute in virtual environment
    p_verbose
        Give feedback (or not)
        Default is True

    Returns
    -------
    subprocess.CompletedProcess
    See https://docs.python.org/3.9/library/subprocess.html#subprocess.CompletedProcess

    Examples
    --------
    # No proper doctest (<<<) because it is os dependent
    beetools.install_in( beetools.get_tmp_dir(),
                              'new-project',
                              ['echo Installing in VEnv','pip install wheel','echo Done!'])
    + sudo -i
    Installing in VEnv
    Done!
    + exit
    True

    """
    switches = []
    script_name = "install_in"
    if utils.get_os() == utils.LINUX:
        switches = ["-x"]
        script_cmds = ["sudo -i << _EOF_"]
    elif utils.get_os() == utils.WINDOWS:
        script_cmds = []
        if p_verbose:
            script_cmds.append("@ECHO OFF")
    else:
        script_cmds = []
        if p_verbose:
            script_cmds.append("@ECHO OFF")
    script_cmds.append(f"{activate(p_venv_root_dir, p_venv_name)}")
    for instr in p_instructions:
        script_cmds.append(instr)
    if utils.get_os() == utils.LINUX:
        script_cmds.append("_EOF_")
        script_cmds.append("exit")
    ret_code = script.exec_batch_in_session(
        script_cmds,
        p_script_name=script_name,
        p_verbose=p_verbose,
        p_switches=switches,
    )
    return ret_code


def set_up(p_venv_root_dir, p_venv_name, p_package_list=None, p_verbose=True) -> CompletedProcess:
    """Create a virtual environment with some defaults

    Parameters
    ----------
    p_verbose
    p_venv_root_dir
        This is the "root" folder of the virtual environment will be created in
    p_venv_name
        The name of the virtual environment.
    p_package_list
        List of packages to install

    Returns
    -------
    subprocess.CompletedProcess
    See https://docs.python.org/3.9/library/subprocess.html#subprocess.CompletedProcess

    Examples
    --------
    >>> from beetools.venv import set_up
    >>> from beetools.utils import get_tmp_dir
    >>> set_up( get_tmp_dir(),'new-project',['pip','wheel'],p_verbose=False)
    True

    """
    switches = []
    script_cmds = []
    if utils.get_os() == utils.WINDOWS:
        pip_cmd = "pip"
    else:
        pip_cmd = "pip3"
        switches = ["-x"]
        script_cmds = ["sudo -i << _EOF_"]
    script.exec_cmd(
        [
            "python",
            "-m",
            "venv",
            get_dir(p_venv_root_dir, p_venv_name),
        ],
        p_verbose=p_verbose,
    )
    script_name = "set_up"
    script_cmds.append(f"{activate(p_venv_root_dir, p_venv_name)}")
    if not p_package_list:
        p_package_list = []
    for package in p_package_list:
        if package[0] == "pypi":
            script_cmds.append(f"{pip_cmd} install {package[1]}")
        elif package[0] == "Local":
            script_cmds.append(f"{pip_cmd} install --find-links {package[2]} {package[1]}")
    if utils.get_os() == utils.LINUX:
        script_cmds.append("_EOF_")
        script_cmds.append("exit")
    ret_code = script.exec_batch_in_session(
        script_cmds, p_script_name=script_name, p_verbose=p_verbose, p_switches=switches
    )
    return ret_code


def example_virtual_environment():
    """Standard example to illustrate virtual environment tools.

    Parameters
    ----------

    Returns
    -------
    bool
        Successful execution [ b_tls.archive_path | False ]

    Examples
    --------

    """
    success = True
    # Remove remains of any previous skeletons still hanging around.
    venv_name = "new-project"
    if utils.get_os() == utils.WINDOWS:
        p_cmd = ["rd", "/S", "/Q", get_dir(utils.get_tmp_dir(), venv_name)]
    else:
        p_cmd = ["rm", "-f", "-r", get_dir(utils.get_tmp_dir(), venv_name)]
    script.exec_cmd(p_cmd, p_verbose=True)

    # Install a new venv including termcolor in a tmp directory
    package_list = [["Web", "termcolor"], ["Web", "wheel"]]
    success = set_up(utils.get_tmp_dir(), venv_name, package_list, p_verbose=True) and success
    # Install/upgrade in an existing venv
    instructions = [
        f"echo Setting up the {venv_name} VEnv...",
        "pip install --upgrade wheel",
        "echo Done!",
    ]
    success = install_in(utils.get_tmp_dir(), venv_name, instructions, p_verbose=True) and success
    utils.result_rep(success, p_comment="Done")

    # Get the venv activation command
    t_venv = activate(utils.get_tmp_dir(), venv_name)
    print(f"Cmd example:\t{t_venv}")
    success = t_venv and success
    return success


def do_examples(p_cls=True):
    """Example to illustrate usage

    Parameters
    ----------
    p_cls
        Clear the screen before start
        Default is True

    Returns
    -------
    bool
        Successful execution [ b_tls.archive_path | False ]

    Examples
    --------

    """

    return example_virtual_environment()


if __name__ == "__main__":
    do_examples()
# end __main__
