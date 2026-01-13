import configparser
import inspect
import logging
import os
import shutil
import sys
import tempfile
from pathlib import Path

from beetools.msg import error
from beetools.msg import ok

# Default logging constants
DEF_LOG_LEV = logging.DEBUG
DEF_LOG_LEV_FILE = logging.DEBUG
DEF_LOG_LEV_CON = logging.WARNING
LOG_FILE_NAME = Path(sys.argv[0]).parent / "{}.{}".format(Path(sys.argv[0]).stem, "log")
LOG_FILE_FORMAT = "%(asctime)s%(msecs)d;%(levelname)s;%(name)s;%(funcName)s;%(message)s"
LOG_CONSOLE_FORMAT = "\x1b[0;31;40m\n%(levelname)s - %(name)s - %(funcName)s - %(message)s\x1b[0m"

# Default date format strings
LOG_DATE_FORMAT = "%Y%m%d%H%M%S"
LONG_DATE_FORMAT = "%Y%m%d"
TIME_FORMAT = "%H%M%S"

# Message defaults
BAR_LEN = 50
MSG_LEN = 50
CRASH_RETRY = 2

# Operating system name defaults
WINDOWS = "windows"
LINUX = "linux"
MACOS = "macos"
AIX = "aix"

# Codec List Updated 2021/06/29
CODEC_LIST = [
    ["ascii", "646, us-ascii", "English"],
    ["big5", "big5-tw, csbig5", "Traditional Chinese"],
    ["big5hkscs", "big5-hkscs, hkscs", "Traditional Chinese"],
    ["cp037", "IBM037, IBM039", "English"],
    ["cp273", "273, IBM273, csIBM273", "German New in version 3.4."],
    ["cp424", "EBCDIC-CP-HE, IBM424", "Hebrew"],
    ["cp437", "437, IBM437", "English"],
    ["cp500", "EBCDIC-CP-BE, EBCDIC-CP-CH, IBM500", "Western Europe"],
    ["cp720", "Arabic", "cp737", "Greek"],
    ["cp775", "IBM775", "Baltic languages"],
    ["cp850", "850, IBM850", "Western Europe"],
    ["cp852", "852, IBM852", "Central and Eastern Europe"],
    ["p855", "855, IBM855", "Bulgarian, Byelorussian, Macedonian, Russian, Serbian"],
    ["cp856", "Hebrew"],
    ["cp857", "857, IBM857", "Turkish"],
    ["cp858", "858, IBM858", "Western Europe"],
    ["cp860", "860, IBM860", "Portuguese"],
    ["cp861", "861, CP-IS, IBM861", "Icelandic"],
    ["cp862", "862, IBM862", "Hebrew"],
    ["cp863", "863, IBM863", "Canadian"],
    ["cp864", "IBM864", "Arabic"],
    ["cp865", "865, IBM865", "Danish, Norwegian"],
    ["cp866", "866, IBM866", "Russian"],
    ["cp869", "869, CP-GR, IBM869", "Greek"],
    ["cp874", "Thai"],
    ["cp875", "Greek"],
    ["cp932", "932, ms932, mskanji, ms-kanji", "Japanese"],
    ["cp949", "949, ms949, uhc", "Korean"],
    ["cp950", "950, ms950;Traditional Chinese"],
    ["cp1006", "Urdu"],
    ["cp1026", "ibm1026", "Turkish"],
    ["cp1125", "1125, ibm1125, cp866u, ruscii", "Ukrainian New in version 3.4."],
    ["cp1140", "ibm1140", "Western Europe"],
    ["cp1250", "windows-1250", "Central and Eastern Europe"],
    ["cp1251", "windows-1251", "Bulgarian, Byelorussian, Macedonian, Russian, Serbian"],
    ["cp1252", "windows-1252", "Western Europe"],
    ["cp1253", "windows-1253", "Greek"],
    ["cp1254", "windows-1254", "Turkish"],
    ["cp1255", "windows-1255", "Hebrew"],
    ["cp1256", "windows-1256", "Arabic"],
    ["cp1257", "windows-1257", "Baltic languages"],
    ["cp1258", "windows-1258", "Vietnamese"],
    ["euc_jp", "eucjp, ujis, u-jis", "Japanese"],
    ["euc_jis_2004", "jisx0213, eucjis2004", "Japanese"],
    ["euc_jisx0213", "eucjisx0213", "Japanese"],
    [
        "euc_kr",
        "euckr, korean, ksc5601, ks_c-5601, ks_c-5601-1987, ksx1001, ks_x-1001",
        "Korean",
    ],
    [
        "gb2312",
        "chinese, csiso58gb231280, euc-cn, euccn, eucgb2312-cn, gb2312-1980, gb2312-80, iso-ir-58",
        "Simplified Chinese",
    ],
    ["gbk", "936, cp936, ms936", "Unified Chinese"],
    ["gb18030", "gb18030-2000", "Unified Chinese"],
    ["hz", "hzgb, hz-gb, hz-gb-2312", "Simplified Chinese"],
    ["iso2022_jp", "csiso2022jp, iso2022jp, iso-2022-jp", "Japanese"],
    ["iso2022_jp_1", "iso2022jp-1, iso-2022-jp-1", "Japanese"],
    [
        "iso2022_jp_2",
        "iso2022jp-2, iso-2022-jp-2",
        "Japanese, Korean, Simplified Chinese, Western Europe, Greek",
    ],
    ["iso2022_jp_2004", "iso2022jp-2004, iso-2022-jp-2004", "Japanese"],
    ["iso2022_jp_3", "iso2022jp-3, iso-2022-jp-3", "Japanese"],
    ["iso2022_jp_ext", "iso2022jp-ext, iso-2022-jp-ext", "Japanese"],
    ["iso2022_kr", "csiso2022kr, iso2022kr, iso-2022-kr", "Korean"],
    [
        "latin_1",
        "iso-8859-1, iso8859-1, 8859, cp819, latin, latin1, L1",
        "Western Europe",
    ],
    ["iso8859_2", "iso-8859-2, latin2, L2", "Central and Eastern Europe"],
    ["iso8859_3", "iso-8859-3, latin3, L3", "Esperanto, Maltese"],
    ["iso8859_4", "iso-8859-4, latin4, L4", "Baltic languages"],
    [
        "iso8859_5",
        "iso-8859-5, cyrillic",
        "Bulgarian, Byelorussian, Macedonian, Russian, Serbian",
    ],
    ["iso8859_6", "iso-8859-6, arabic", "Arabic"],
    ["iso8859_7", "iso-8859-7, greek, greek8", "Greek"],
    ["iso8859_8", "iso-8859-8, hebrew", "Hebrew"],
    ["iso8859_9", "iso-8859-9, latin5, L5", "Turkish"],
    ["iso8859_10", "iso-8859-10, latin6, L6", "Nordic languages"],
    ["iso8859_11", "iso-8859-11, thai", "Thai languages"],
    ["iso8859_13", "iso-8859-13, latin7, L7", "Baltic languages"],
    ["iso8859_14", "iso-8859-14, latin8, L8", "Celtic languages"],
    ["iso8859_15", "iso-8859-15, latin9, L9", "Western Europe"],
    ["iso8859_16", "iso-8859-16, latin10, L10", "South-Eastern Europe"],
    ["johab", "cp1361, ms1361", "Korean"],
    ["koi8_r", "Russian"],
    ["koi8_t", "Tajik New in version 3.5."],
    ["koi8_u", "Ukrainian"],
    ["kz1048", "kz_1048, strk1048_2002, rk1048", "Kazakh New in version 3.5."],
    [
        "mac_cyrillic",
        "maccyrillic",
        "Bulgarian, Byelorussian, Macedonian, Russian, Serbian",
    ],
    ["mac_greek", "macgreek", "Greek"],
    ["mac_iceland", "macicelandIcelandic"],
    [
        "mac_latin2",
        "maclatin2, maccentraleurope, mac_centeuro",
        "Central and Eastern Europe",
    ],
    ["mac_roman", "macroman, macintosh", "Western Europe"],
    ["mac_turkish", "macturkish", "Turkish"],
    ["ptcp154", "csptcp154, pt154, cp154, cyrillic-asian", "Kazakh"],
    ["shift_jis", "csshiftjis, shiftjis, sjis, s_jis", "Japanese"],
    ["shift_jis_2004", "shiftjis2004, sjis_2004, sjis2004", "Japanese"],
    ["shift_jisx0213", "shiftjisx0213, sjisx0213, s_jisx0213", "Japanese"],
    ["utf_32", "U32, utf32", "all languages"],
    ["utf_32_be", "UTF-32BE", "all languages"],
    ["utf_32_le", "UTF-32LE", "all languages"],
    ["utf_16", "U16, utf16", "all languages"],
    ["utf_16_be", "UTF-16BE", "all languages"],
    ["utf_16_le", "UTF-16LE", "all languages"],
    ["utf_7", "U7, unicode-1-1-utf-7", "all languages"],
    ["utf_8", "U8, UTF, utf8, cp65001", "all languages"],
    ["utf_8_sig", "", "all languages"],
]


def get_os() -> str:
    """Return a constant for the current operating system

    Parameters
    ----------

    Returns
    -------
    str
        "linux" | "windows"

    Examples
    --------
    # No proper doctest (<<<) because it is os dependent
    get_os()
    'linux'
    """
    if sys.platform.startswith("win32"):
        curr_os = WINDOWS
    elif sys.platform.startswith("linux"):
        curr_os = LINUX
    elif sys.platform.startswith("darwin"):
        curr_os = MACOS
    elif sys.platform.startswith("aix"):
        curr_os = AIX
    else:
        print("OS not listed\nSystem will now terminate")
        sys.exit()
    return curr_os


def get_tmp_dir(p_prefix=None) -> Path:
    """Return os related temporary folder for user.

    Parameters
    ----------

    Returns
    -------
    Path
        Path object with temp folder for user and os

    Examples
    --------
    # No proper doctest (<<<) because it is os dependent
    get_tmp_dir()
    PosixPath('/tmp')

    """
    if p_prefix:
        temp_dir = Path(tempfile.mkdtemp(prefix=p_prefix))
    else:
        temp_dir = Path(tempfile.mkdtemp())
    return temp_dir


def is_struct_the_same(p_x, p_y, p_ref="") -> bool:
    """Compare two structures

    Parameters
    ----------
    p_x
        "Left" structure
    p_y
        "Right" structure
    p_ref
        Reference string
        Default is ''

    Returns
    -------
    bool
        True is structure are the same.  If the contents of dictionaries are the same
        but not necessarily in the same order, they are still regarded as "the same".

    Examples
    --------
    >>> x=[1,2]
    >>> y=[1,2]
    >>> from beetools.utils import is_struct_the_same
    >>> is_struct_the_same(x,y)
    True

    >>> x={1:'One',2:'Two'}
    >>> y={2:'Two',1:'One'}
    >>> from beetools.utils import is_struct_the_same
    >>> is_struct_the_same(x,y)
    True

    >>> z={2:'Two',1:'Three'}
    >>> from beetools.utils import is_struct_the_same
    >>> is_struct_the_same(y,z,'ref str')
    ref str.1.One
    <>
    ref str.1.Three
    False
    """
    success = True
    x_len = 0
    y_len = 0
    if isinstance(p_x, (dict, list, tuple)):
        x_len = len(p_x)
        y_len = len(p_y)
    if x_len == y_len:
        if isinstance(p_x, dict) and isinstance(p_y, dict):
            x_keys_srt = sorted(p_x.keys())
            y_keys_srt = sorted(p_y.keys())
            for key in x_keys_srt:
                if key in y_keys_srt:
                    ref = f"{p_ref}.{key}"
                    success = is_struct_the_same(p_x[key], p_y[key], ref) and success
                else:
                    print(f"Key {p_ref}[ {key} ] not in both structures")
                    success = False
        elif (isinstance(p_x, list) and isinstance(p_y, list)) or (isinstance(p_x, tuple) and isinstance(p_y, tuple)):
            for i, rec in enumerate(p_x):
                ref = f"{p_ref}[ {i} ]"
                success = is_struct_the_same(rec, p_y[i], ref) and success
        elif p_x != p_y:
            print("{0}.{1}\n<>\n{0}.{2}".format(p_ref, p_x, p_y))
            success = False
    else:
        print(f"Length of items in structure differ:\n{p_ref}\nx({x_len}) = {p_x}\ny({y_len}) = {p_y}")
        success = False
    return success


def result_rep(p_success, p_comment="No Comment") -> str:
    """Print a formatted result report

    Parameters
    ----------
    p_success
        True | False
    p_comment
        Comment to print
        Default is "No Comment"

    Returns
    -------
    str
        Formatted result text

    Examples
    --------
    >>> from beetools.utils import result_rep
    >>> result_rep(True)
    <module> - \x1b[32mSuccess\x1b[0m (No Comment)
    '<module> - \\x1b[32mSuccess\\x1b[0m (No Comment)'
    """
    proc_name = inspect.getouterframes(inspect.currentframe(), 1)[1][3]
    if p_success:
        ret_str = "{} - {} ({})".format(proc_name, ok("Success"), p_comment)
    else:
        ret_str = "{} - {} ({})".format(proc_name, error("Failed"), p_comment)
    print(ret_str)
    return ret_str


def rm_temp_locked_file(p_file_path) -> bool:
    """Attempt to remove a temporary locked file

    Parameters
    ----------
    p_file_path
        Patch object

    Returns
    -------
    None

    Examples
    --------
    # No proper doctest (<<<) because it is os dependent

    """
    crash_retry_cntr = 0
    success = False
    while crash_retry_cntr < CRASH_RETRY:
        try:
            if p_file_path.is_file():
                p_file_path.unlink()
            if p_file_path.is_dir():
                shutil.rmtree(p_file_path)
            success = True
        except shutil.Error:
            crash_retry_cntr += 1
        except PermissionError:
            crash_retry_cntr += 1
        else:
            crash_retry_cntr = CRASH_RETRY
    return success


def rm_tree(p_pth, p_crash=True):
    """Remove a tree structure

    Parameters
    ----------
    p_pth
        Root f the tree to remove
    p_crash
        If true, the system will terminate if the structure cannot be removed

    Returns
    -------
    Bool
        Status of the operation

    Examples
    --------
    # No proper doctest (<<<) because it is os dependent

    """
    success = False
    # tree = list(p_pth.glob('**/*'))
    # not_empty = []
    crash_retry_cntr = 0
    # success = False
    while crash_retry_cntr < CRASH_RETRY and not success:
        success = True
        for root, dirs, files in os.walk(p_pth, topdown=False):
            for file in files:
                try:
                    file_pth = os.path.join(root, file)
                    os.remove(file_pth)
                    success = True and success
                except PermissionError:
                    success = False
            for directory in dirs:
                try:
                    dir_pth = os.path.join(root, directory)
                    os.rmdir(dir_pth)
                    success = True and success
                except OSError:
                    success = False
        crash_retry_cntr += 1

    if p_pth.exists():
        try:
            p_pth.rmdir()
            success = True
        except OSError:
            if p_crash:
                print(error("{p_pth} could not be removed.\nSystem terminated."))
                sys.exit()
            else:
                print(error("{p_pth} could not be removed.\nExecution will continue."))
    else:
        success = True
    return success


def select_os_dir_from_config(p_config, p_section, p_option) -> Path:
    """Select the correct folder on a specific os in the Bright Edge eServices
    echo system.

    This is useful when the application runs on different os' and an option
    must be selected dependent on the os and/or the system.  Folders or directories
    are the usual culprits.

    Parameters
    ----------
    p_config
        ConfigParser object.
        See https://docs.python.org/3.9/library/configparser.html#module-configparser
    p_section
        Section to inspect
    p_option
        Option to find for the operating system

    Returns
    -------
    Path
        Path object for the correct folder for the operating system.

    Examples
    --------
    # No proper doctest (<<<) because it is os dependent
    cnf = configparser.ConfigParser()
    cnf.read_dict({ 'Folders' :
                    { 'windows1_MyFolderOnSystem' : 'c:\\Program Files',
                      'windows2_MyFolderOnSystem' : 'c:\\Program Files (x86)',
                      'linux1_MyFolderOnSystem'   : '/usr/local/bin',
                      'linux2_MyFolderOnSystem'   : '/bin'}})
    select_os_dir_from_config( cnf, 'Folders', 'MyFolderOnSystem' )
    beetools.select_os_dir_from_config( cnf, 'Folders', 'MyFolderOnSystem' )
    PosixPath('/usr/local/bin')

    """
    options = p_config.options(p_section)
    directory = None
    for option in options:
        if option.split("_")[0][:-1] == get_os() and option.split("_")[1].lower() == p_option.lower():
            directory = Path(p_config.get(p_section, option))
            if not directory.is_dir():
                directory = None
            else:
                break
    if not directory:
        print(error(f"select_os_dir_from_config not found: {p_section}:{p_option}"))
    return directory


def example_tools():
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

    print()
    # tmp_dir = get_tmp_dir() / 'test'
    # tmp_t1 = tmp_dir / 'T1'

    # Usage of general functions
    print(f"The current os is {get_os()}")
    tmp_dir = get_tmp_dir() / "test"
    print(f"created a temporary folder {tmp_dir}")
    success = rm_tree(tmp_dir, p_crash=True) and success

    # Usage of is_struct_the_same
    x = [1, 2]
    y = [1, 2]
    print(f"x={x}")
    print(f"y={y}")
    print(is_struct_the_same(x, y))

    x = {1: "One", 2: "Two"}
    y = {2: "Two", 1: "One"}
    print(f"x={x}")
    print(f"y={y}")
    print(is_struct_the_same(x, y))

    z = {2: "Two", 1: "Three"}
    print(f"x = {x}")
    print(f"y = {y}")
    print(is_struct_the_same(y, z, "ref str"))

    # Attempt to remove a temporary locked file.
    tmp_dir = get_tmp_dir()
    tmp_pth = tmp_dir / "dropboxfile.txt"
    with open(tmp_pth, "w+") as locked_file:
        for i in range(1000000):
            locked_file.write(str(i))
    success = rm_temp_locked_file(tmp_pth) and success

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
    os_system_dir = select_os_dir_from_config(cnf, "Folders", "MyFolderOnSystem")
    print(os_system_dir)
    success = os_system_dir and success

    result_rep(success, p_comment="Done")
    return success


def do_examples():
    """Example to illustrate usage

    Parameters
    ----------

    Returns
    -------
    bool
        Successful execution [ b_tls.archive_path | False ]

    Examples
    --------

    """

    return example_tools()


if __name__ == "__main__":
    do_examples()
