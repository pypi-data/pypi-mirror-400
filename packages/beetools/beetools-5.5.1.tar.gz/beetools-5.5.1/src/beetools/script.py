import configparser
import os
import shlex
import subprocess
import sys
from pathlib import Path

from termcolor import colored

from beetools import utils
from beetools import venv
from beetools.msg import info


def exec_batch_in_session(
    p_script_cmds,
    p_switches=None,
    p_script_name=False,
    p_verbose=False,
    p_shell=False,
) -> int:
    """Execute a script in the same session

    Useful when commands has to be executed in one session for instance if
    in a virtual environment is invoked and the commands must be executed
    in the virtual environment.

    Parameters
    ----------
    p_script_cmds
        Commands to execute in a list
    p_switches
        Switches for the bash script.
        Default is None.
    p_script_name
        Name of the script to use
        Default is False and will be set to "do_bashs_cript_temp"
    p_verbose
        Give feedback (or not)
        Default is False
    p_shell
        Run the script in a shell.  See https://docs.python.org/3.9/library/subprocess.html#subprocess.run
        Default is False

    Returns
    -------
    subprocess.CompletedProcess
        See https://docs.python.org/3.9/library/subprocess.html#subprocess.CompletedProcess

    Examples
    --------
    # No proper doctest (<<<) because it is os dependent
    tmp_test = get_tmp_dir() / 'test'
    tmp_t1 = tmp_test / 't1'
    cmd = ['mkdir -p {}'.format(tmp_t1), 'ls -l {}'.format(tmp_test), 'rm -R {}'.format(tmp_test)]
    exec_batch_in_session(cmd)
    """
    if isinstance(p_switches, list):
        switches = p_switches
    elif isinstance(p_switches, str):
        switches = list(shlex.shlex(p_switches))
    else:
        switches = []
    if utils.get_os() in [utils.LINUX, utils.MACOS]:
        script = ["bash"] + switches
        ext = "sh"
        contents = "#!/bin/bash\n"
    elif utils.get_os() == utils.WINDOWS:
        script = []
        ext = "bat"
        contents = ""
    else:
        print(colored(f"Unknown OS ({utils.get_os()})\nSystem terminated!", "red"))
        sys.exit()

    if not p_script_name:
        p_script_name = "exec_batch_in_session_temp"
    batch_pth = utils.get_tmp_dir() / Path(f"{p_script_name}.{ext}")
    script.append(str(batch_pth))
    contents += write_script(batch_pth, p_script_cmds)
    if utils.get_os() == utils.MACOS:
        batch_pth.chmod(0o777)
    if p_verbose:
        print(info("==[Start {0}]====\n{1}==[ End {0} ]====".format(batch_pth, contents)))
    rc = exec_cmd(script, p_verbose=p_verbose, p_shell=p_shell)
    if os.path.isfile(batch_pth):
        os.remove(batch_pth)
    return rc


def exec_batch(p_batch: list, p_verbose: bool = False) -> list:
    """Execute a batch of commands independnatly.

    Each command will be executed independently of the previous one i.e it
    will be in a different session.

    :param p_batch:
        List of the independent commands to execute.

    :param p_verbose:
        Write output to console.

    :return:
        list
        A list with the return code for each batch command.
        See https://docs.python.org/3.9/library/subprocess.html#subprocess.CompletedProcess

    :example:
    >>> from beetools.script import exec_batch
    >>> exec_batch([[ 'echo', 'Hello'],['echo','Goodbye']])
    True
    """

    rc = []
    for cmd in p_batch:
        rc.append(exec_cmd(cmd, p_verbose=p_verbose))
    return rc


def exec_cmd(p_cmd, p_shell=None, p_verbose=True) -> int:
    """Execute a command line instruction on tools.LINUX or tools.WINDOWS

    Parameters
    ----------
    p_cmd
        Command to execute.  See See https://docs.python.org/3.9/library/subprocess.html#subprocess.run
    p_shell
        Run the script in a shell.  See https://docs.python.org/3.9/library/subprocess.html#subprocess.run
        Default is None
    p_verbose
        Give feedback (or not)
        Default is False

    Returns
    -------
    bool
        If successful it returns True (subprocess.CompletedProcess = 0)
        alternatively it returns a subprocess.CompletedProcess
        See https://docs.python.org/3.9/library/subprocess.html#subprocess.CompletedProcess

    Examples
    --------
    >>> from beetools.script import exec_cmd
    >>> exec_cmd([ 'echo', 'Hello'])
    True

    """
    p_cmd = [str(s) for s in p_cmd]
    inst_str = " ".join(p_cmd)
    if p_verbose:
        print(info(f"{inst_str}"))
    if utils.get_os() in [utils.LINUX, utils.MACOS] and not p_shell:
        shell = False
    elif utils.get_os() == utils.WINDOWS and not p_shell:
        shell = True
    elif utils.get_os() not in [utils.WINDOWS, utils.LINUX, utils.MACOS]:
        print(colored(f"Unknown OS ({utils.get_os()})\nSystem terminated!", "red"))
        sys.exit()
    else:
        shell = p_shell
    try:
        comp_proc = subprocess.run(p_cmd, capture_output=False, shell=shell, check=False)
        comp_proc.check_returncode()
    except subprocess.CalledProcessError:
        if p_verbose:
            print(f"\nCmd:\t{inst_str}\nrc:\t{comp_proc.returncode}")
    finally:
        rc = comp_proc.returncode
    return rc


def write_script(p_pth, p_contents):
    """Write a script to disk

    Parameters
    ----------
    p_pth
        Path to the script
    p_contents
        Contents of the script

    Returns
    -------
    subprocess.CompletedProcess
    See https://docs.python.org/3.9/library/subprocess.html#subprocess.CompletedProcess

    Examples
    --------
    >>> from beetools import utils, venv
    >>> venv.set_up(utils.get_tmp_dir(),'new-project',['pip','wheel'],p_verbose=False)
    True

    """
    contents = ""
    for line in p_contents:
        if isinstance(line, list):
            contents += " ".join(line) + "\n"
        else:
            contents += f"{line}\n"
    p_pth.write_text(contents)
    return contents


def example_scripting():
    """Standard example to illustrate standard use.

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
    # Run a few commands in a script.  Useful when executing commands in a
    # venv in the same session.
    tmp_test = utils.get_tmp_dir() / "test"
    tmp_t1 = tmp_test / "T1"
    if utils.get_os() == utils.WINDOWS:
        batch = [
            f"md {tmp_t1}",
            f"dir /B {tmp_test}",
        ]
    else:
        batch = [
            f"mkdir -p {tmp_t1}",
            f"ls -l {tmp_test}",
        ]
    if exec_batch_in_session(batch, p_verbose=False) != 0:
        success = False

    # Execute some commands in a batch
    if utils.get_os() == utils.WINDOWS:
        cmds = [
            ["rd", "/S", "/Q", f"{tmp_t1}"],
            ["md", f"{tmp_t1}"],
        ]
    else:
        cmds = [
            ["mkdir", "-p", f"{tmp_t1}"],
            ["ls", "-l", f"{tmp_test}"],
        ]
    if exec_batch(cmds) != [0, 0]:
        success = False

    # Write a script
    script_pth = utils.get_tmp_dir() / __name__
    cmds = [
        ["echo", "Hello"],
        ["echo", "Goodbye"],
    ]
    contents = write_script(script_pth, cmds)
    print(contents)

    # Create a few files to the previous example and the remove the tree
    t_file = tmp_test / Path("t.tmp")
    t_file.touch(mode=0o666, exist_ok=True)
    t_file = tmp_t1 / Path("t.tmp")
    t_file.touch(mode=0o666, exist_ok=True)
    success = utils.rm_tree(tmp_test, p_crash=True) and success

    # Attempt to remove a temporary locked file.
    venv_name = "new-project"
    success = utils.rm_temp_locked_file(venv.get_dir(utils.get_tmp_dir(), venv_name)) and success

    # Read an option from an ini for a particular os and setup
    cnf = configparser.ConfigParser()
    cnf.read_dict(
        {
            "Folders": {
                "windows1_MyFolderOnSystem": "c:\\Program Files",
                "windows2_MyFolderOnSystem": "c:\\Program Files (x86)",
                "linux1_MyFolderOnSystem": "/usr/local/bin",
                "linux2_MyFolderOnSystem": "/bin",
                "macos1_MyFolderOnSystem": "/System",
                "macos2_MyFolderOnSystem": "/Application",
            }
        }
    )
    os_system_flder = utils.select_os_dir_from_config(cnf, "Folders", "MyFolderOnSystem")
    print(os_system_flder)
    if not os_system_flder:
        success = False

    utils.result_rep(success, p_comment="Done")
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

    return example_scripting()


if __name__ == "__main__":
    do_examples()
# end __main__
