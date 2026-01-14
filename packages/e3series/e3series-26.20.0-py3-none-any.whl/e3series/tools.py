from __future__ import annotations
import re
import os
import os.path
import sys
import uuid
import psutil
import shutil
import operator
import subprocess

import winreg
import win32com.client
import win32com.client.gencache
import win32event
import win32api
import win32job
import win32com
import win32con
import win32process
import pythoncom
import warnings
import threading

from typing import Union, Optional, TextIO, Any, TYPE_CHECKING
from typing_extensions import TypeAlias
from enum import Enum

if TYPE_CHECKING:
    from .com import Application, DbeApplication

Version: TypeAlias = tuple[int, int]

_global_process_job: Optional[Any] = None
_global_process_job_lock = threading.Lock()


class E3Warning(UserWarning):
    pass


def get_version_from_executable(executable_path: str) -> Version:
    file_info = win32api.GetFileVersionInfo(executable_path, "\\")
    ms = file_info["FileVersionMS"]
    return (win32api.HIWORD(ms), win32api.LOWORD(ms))


def get_executable_from_pid(pid: int) -> str:
    process_handle = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, False, pid)
    executable_path = win32process.GetModuleFileNameEx(process_handle, 0)
    win32api.CloseHandle(process_handle)
    return str(executable_path)


def get_commandline_args_from_pid(pid: int) -> Optional[str]:
    strComputer = "."
    obj_wmi_service = win32com.client.Dispatch("WbemScripting.SWbemLocator")
    obj_swbem_services = obj_wmi_service.ConnectServer(strComputer, "root/cimv2")

    proc_items = list(obj_swbem_services.ExecQuery(f"Select * from Win32_Process where ProcessId='{int(pid)}'"))
    if len(proc_items) == 0:
        raise RuntimeError(f"Invalid process ID '{pid}'")

    obj_item = proc_items[0]
    assert obj_item.ProcessId == pid
    return str(obj_item.CommandLine)


def get_installed() -> list[tuple[Version, str]]:
    """
    Returns a list of all installed E3.series. The installed versions are read from the registry. Only existing Installations are returned.

    :return: a list of tuples. Every tuple corresponds to the schema (<version>, <executable path>), e.g. ((25, 0), 'C:\\Program Files\\Zuken\\E3.series_2025\\E3.series.exe'). The list is always sorted by version with the latest version at the end.
    """
    with winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE) as registry:
        versions: list[str] = []
        try:
            with winreg.OpenKey(registry, "SOFTWARE\\Zuken\\E3.series") as root_key:
                i = 0
                while True:
                    try:
                        child_key = winreg.EnumKey(root_key, i)
                        versions.append(child_key)
                        i += 1
                    except OSError:
                        break
        except FileNotFoundError:
            pass

        version_and_path: list[tuple[Version, str]] = []
        for version in versions:
            with winreg.OpenKey(registry, f"SOFTWARE\\Zuken\\E3.series\\{version}") as key:
                try:
                    value, type = winreg.QueryValueEx(key, "InstallationPath")
                    if type != winreg.REG_SZ:
                        continue

                    executable_path = os.path.join(value, "E3.series.exe")
                    if not os.path.isfile(executable_path):
                        continue

                    # We read the product version, because it includes the minor version.
                    # The registry folder does not include the service pack and patch version
                    file_version = get_version_from_executable(executable_path)
                    if version != f"{file_version[0]}.0":
                        warnings.warn(
                            f"Registry key 'HKEY_LOCAL_MACHINE\\Software\\Zuken\\E3.series\\{version}\\InstallationPath' contains a path to the wrong executable (Version {file_version[0]}.{file_version[1]}). ",
                            E3Warning,
                        )
                        continue
                    version_and_path.append((file_version, executable_path))
                except FileNotFoundError:
                    pass

    version_and_path.sort(key=operator.itemgetter(0))
    return version_and_path


def get_registered_typelibs() -> list[tuple[Version, str]]:
    """
    Returns registered E3.series COM typelibs. Only existing typelibs are returned. The typelibs are sorted with the latest version at the end.
    """
    with winreg.ConnectRegistry(None, winreg.HKEY_CLASSES_ROOT) as registry:
        hex_versions: list[str] = []
        try:
            with winreg.OpenKey(registry, "TypeLib\\{59B53E00-679B-41ED-9D11-766E27B6A7A4}") as root_key:
                i = 0
                while True:
                    try:
                        child_key = winreg.EnumKey(root_key, i)
                        hex_versions.append(child_key)
                        i += 1
                    except OSError:
                        break

        except FileNotFoundError:
            pass

        version_and_path: list[tuple[Version, str]] = []
        for hex_version in hex_versions:
            for bitness in ["win32", "win64"]:
                try:
                    with winreg.OpenKey(registry, f"TypeLib\\{{59B53E00-679B-41ED-9D11-766E27B6A7A4}}\\{hex_version}\\0\\{bitness}") as key:
                        tlb_path, type = winreg.QueryValueEx(key, "")
                        if type != winreg.REG_SZ:
                            continue

                        hex_pieces = hex_version.split(".")
                        assert len(hex_pieces) == 2
                        version = (int(hex_pieces[0], 16), int(hex_pieces[1], 16))

                        if not os.path.isfile(tlb_path):
                            warnings.warn(
                                f'E3.series version {version[0]}.{version[1]} was not uninstalled correctly. The typelib is still registered, but the file "{tlb_path}" does not exist anymore.',
                                E3Warning,
                            )
                            continue

                        version_and_path.append((version, tlb_path))
                except FileNotFoundError:
                    pass

    version_and_path.sort(key=operator.itemgetter(0))
    return version_and_path


class Language(Enum):
    ENGLISH_US = 1
    FRENCH_CANADIAN = 2
    RUSSIAN = 7
    DUTCH = 31
    FRENCH = 33
    SPANISH = 34
    ITALIAN = 39
    ENGLISH_GB = 44
    POLISH = 48
    GERMAN = 49
    BRAZILIAN_PORTUGUESE = 55
    JAPANESE = 81
    CHINESE = 86
    TURKISH = 90
    PORTUGUESE = 351


class StartArguments:
    def __init__(self) -> None:
        self.filename: Optional[str] = None
        self.cable: bool = False
        self.compare_config_file: Optional[str] = None
        self.compare_new_file: Optional[str] = None
        self.compare_old_file: Optional[str] = None
        self.dbe: bool = False
        self.demo: bool = False
        self.dist_design: bool = False
        self.economy: bool = False
        self.fluid: bool = False
        self.formboard: bool = False
        self.functional_design: bool = False
        self.inprocreg_only: bool = False
        self.level: bool = False
        self.logic: bool = False
        self.mu_create: bool = False
        self.multiuser: bool = False
        self.mu_open: Union[bool, str, None] = False
        self.new: bool = False
        self.no_cgm: bool = False
        self.no_dbe: bool = False
        self.no_export_exf: bool = False
        self.no_import_ruplan: bool = False
        self.no_import_step: bool = False
        self.no_mil_standard: bool = False
        self.no_panel: bool = False
        self.no_pdf: bool = False
        self.no_plugin: bool = False
        self.no_splash: bool = False
        self.no_wire: bool = False
        self.no_xvl: bool = False
        self.plus: bool = False
        self.redliner: bool = False
        self.register: bool = False
        self.schema: bool = False
        self.student: bool = False
        self.topology: bool = False
        self.unregister: bool = False
        self.view: bool = False
        self.workspace: Optional[str] = None
        self.automation: bool = False
        self.language: Union[Language, int, None] = None

    def to_list(self) -> list[str]:
        result: list[str] = []
        if self.mu_create and not self.multiuser:
            raise ValueError("StartArguments.mu_create requires StartArguments.multiuser to be set to True.")

        if self.mu_open and not self.multiuser:
            raise ValueError("StartArguments.mu_open requires StartArguments.multiuser to be set to True.")

        if self.plus and not self.view:
            raise ValueError("StartArgemtns.plus requires StartArguments.view to be set to True.")

        if self.filename is not None:
            result.append(self.filename)
        if self.cable:
            result.append("/cable")
        if self.compare_config_file is not None:
            result.append("/compareconfigfile")
            result.append(self.compare_config_file)
        if self.compare_new_file is not None:
            result.append("/comparenewfile")
            result.append(self.compare_new_file)
        if self.compare_old_file is not None:
            result.append("/compareoldfile")
            result.append(self.compare_old_file)
        if self.dbe:
            result.append("/dbe")
        if self.demo:
            result.append("/demo")
        if self.dist_design:
            result.append("/distdesign")
        if self.economy:
            result.append("/economy")
        if self.fluid:
            result.append("/fluid")
        if self.formboard:
            result.append("/formboard")
        if self.functional_design:
            result.append("/functionaldesign")
        if self.inprocreg_only:
            result.append("/inprocregonly")
        if self.level:
            result.append("/level")
        if self.logic:
            result.append("/logic")
        if self.mu_create:
            result.append("/mucreate")
        if self.multiuser:
            result.append("/multiuser")
        if self.mu_open:
            result.append("/muopen")
            if isinstance(self.mu_open, str):
                result.append(self.mu_open)

        if self.new:
            result.append("/new")
        if self.no_cgm:
            result.append("/nocgm")
        if self.no_dbe:
            result.append("/nodbe")
        if self.no_export_exf:
            result.append("/noexportexf")
        if self.no_import_ruplan:
            result.append("/noimportruplan")
        if self.no_import_step:
            result.append("/noimportstep")
        if self.no_mil_standard:
            result.append("/nomilstandard")
        if self.no_panel:
            result.append("/nopanel")
        if self.no_pdf:
            result.append("/nopdf")
        if self.no_plugin:
            result.append("/noplugin")
        if self.no_splash:
            result.append("/nosplash")
        if self.no_wire:
            result.append("/nowire")
        if self.no_xvl:
            result.append("/noxvl")
        if self.plus:
            result.append("/plus")
        if self.redliner:
            result.append("/redliner")
        if self.register:
            result.append("/register")
        if self.schema:
            result.append("/schema")
        if self.student:
            result.append("/student")
        if self.topology:
            result.append("/topology")
        if self.unregister:
            result.append("/unregister")
        if self.view:
            result.append("/view")
        if self.workspace is not None:
            result.append("/Workspace=" + self.workspace)
        if self.automation:
            result.append("/automation")
        if self.language is not None:
            if type(self.language) is Language:
                result.append("/language=" + str(self.language.value))
            elif type(self.language) is int:
                result.append("/language=" + str(self.language))
            else:
                raise TypeError("language must be either an int or a member of e3series.tools.Language.")

        return result


def _assign_current_process_to_global_job() -> None:
    with _global_process_job_lock:
        global _global_process_job
        if _global_process_job is None:
            _global_process_job = win32job.CreateJobObject(None, f"E3.Python.Library:{os.getpid()}")  # type:ignore

            job_object_info = win32job.QueryInformationJobObject(_global_process_job, win32job.JobObjectExtendedLimitInformation)
            job_object_info["BasicLimitInformation"]["LimitFlags"] |= win32job.JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE

            win32job.SetInformationJobObject(_global_process_job.handle, win32job.JobObjectExtendedLimitInformation, job_object_info)
            current_process_handle = win32process.GetCurrentProcess()
            win32job.AssignProcessToJobObject(_global_process_job, current_process_handle)


def start(
    args: Union[StartArguments, list[str], None] = None,
    *,
    executable: Optional[str] = None,
    wait_for_com: bool = True,
    timeout_seconds: Optional[float] = None,
    keep_alive: bool = True,
) -> subprocess.Popen[bytes]:
    """
    Starts an E3.series process. This function returns not before the CT.Application or CT.DBEApplication COM object is ready.
    This example starts an instance of E3.formboard in Japanese:
    ```
    from e3series.tools import Language, StartArguments, start
    args = StartArguments()
    args.formboard = True
    args.language = Language.JAPANESE
    start(args)
    ```

    :param args: The commandline arguments for E3.series.
    :param executable: Path to the E3.series.exe. If this argument is None the latest registered E3.series.exe is executed.
    :param timeout_seconds: Timout in seconds to wait for the initialization event.
    :param keep_alive: If set to False, the E3 Process will be terminated with the script process.
    """
    if timeout_seconds is not None and timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be None or positive.")

    if executable is None:
        installed_tlbs = get_registered_typelibs()
        if len(installed_tlbs) == 0:
            raise Exception("E3.series was not installed properly. If you want to start a specific E3.series, provide a executable path.")

        _, tlb_path = installed_tlbs[-1]
        tlb_directory = os.path.dirname(tlb_path)
        executable = os.path.join(tlb_directory, "E3.series.exe")

    if not os.path.isfile(executable):
        raise FileNotFoundError(f'The file "{executable}" does not exist.')

    if os.path.basename(executable).lower() != "e3.series.exe":
        raise Exception("The executable name must be 'E3.series.exe'.")

    if isinstance(args, StartArguments):
        arg_list = args.to_list()
    elif isinstance(args, list):
        arg_list = list(args)  # The list needs to be copied, because we don't want to modify the input arguments.
    elif args is None:
        arg_list = []
    elif isinstance(args, str):
        raise ValueError("Invalid value for parameter args. Plase provide a list of strings instead of a single string.")
    else:
        raise ValueError("Invalid value for parameter args.")

    if wait_for_com:
        if any((arg.startswith("/startup_event=") for arg in arg_list)):
            raise ValueError("The /startup_event argument may not be provided, when starting with wait_for_com=True.")
        event_name = str(uuid.uuid4())
        arg_list.append(f"/startup_event={event_name}")

    popen_args = [executable] + arg_list

    try:
        if wait_for_com:
            event_handle = win32event.CreateEvent(None, True, False, event_name)
            win_timeout = int(1e3 * timeout_seconds) if timeout_seconds is not None else win32event.INFINITE

        creationflags = 0
        if keep_alive:
            creationflags |= subprocess.CREATE_BREAKAWAY_FROM_JOB
        else:
            _assign_current_process_to_global_job()

        process = subprocess.Popen(popen_args, creationflags=creationflags)

        if wait_for_com:
            process_handle = int(getattr(process, "_handle"))
            event_result = win32event.WaitForMultipleObjects([event_handle, process_handle], False, win_timeout)
            if event_result == win32event.WAIT_TIMEOUT:
                raise TimeoutError("The start E3.series was aborted due to the given timeout.")

    finally:
        if wait_for_com:
            win32api.CloseHandle(event_handle)

    return process


def _get_monikers_from_rot(moniker_pattern: str, pids: Optional[list[int]] = None) -> list[tuple[Any, int]]:
    result: list[tuple[object, int]] = []

    context = pythoncom.CreateBindCtx()
    rot = pythoncom.GetRunningObjectTable()
    for moniker in rot.EnumRunning():  # type: ignore
        moniker_name = moniker.GetDisplayName(context, None)

        match = re.match(moniker_pattern, moniker_name)
        if match:
            pid = int(match.group(1))
            if pids is None or pid in pids:  # type: ignore
                result.append((rot.GetObject(moniker), pid))

    return result


def _get_app_monikers_from_rot(pids: Optional[list[int]] = None) -> list[tuple[Any, int]]:
    return _get_monikers_from_rot(r"!E3Application:(\d+)", pids)


def _get_dbe_monikers_from_rot(pids: Optional[list[int]] = None) -> list[tuple[Any, int]]:
    return _get_monikers_from_rot(r"!E3DbeApplicationFactory:(\d+)", pids)


def get_running_e3s() -> list[int]:
    """
    Returns the process ids of all running processes with an application object.
    """
    monikers = _get_app_monikers_from_rot()
    return [pid for _, pid in monikers]


def get_running_dbes() -> list[int]:
    """
    Returns the ids of all running processes with an dbe application object.
    """
    monikers = _get_dbe_monikers_from_rot()
    return [pid for _, pid in monikers]


def _check_dispatch_cast(pid: int, raw_obj: Any) -> None:
    if not hasattr(raw_obj, "PutInfo"):
        process_description = f"pid: {pid}"
        try:
            executable_path = get_executable_from_pid(pid)
            process_description += f', path: "{executable_path}"'

            version = get_version_from_executable(executable_path)
            process_description += f", version: {version}"
        except Exception:
            pass  # This only improves the error message, so if we can't get the path or version we just show the pid.

        raise RuntimeError(
            f'The COM type library for running E3.series ({process_description}) is not registered. Register the library by executing E3.series as administrator with the command line argument "/register" or reinstalling.'
        )


def _dispatch_with_errorhandling(query: Any, resultCLSID: str) -> Any:
    try:
        return win32com.client.Dispatch(query, resultCLSID=resultCLSID)
    except AttributeError as e:
        if e.name == "CLSIDToClassMap":  # type: ignore
            mod_name: str = getattr(e, "_obj").__name__
            mod_name_parts = mod_name.split(".")
            if len(mod_name_parts) == 3:
                folder_name = mod_name_parts[2]
                gen_path: str = win32com.client.gencache.GetGeneratePath()  # type: ignore
                folder_path = os.path.join(gen_path, folder_name)
                shutil.rmtree(folder_path)
                del sys.modules[mod_name]
                try:
                    return win32com.client.Dispatch(query, resultCLSID=resultCLSID)
                except AttributeError:
                    pass

    raise RuntimeError(f'Connection to "{resultCLSID}" failed.')


def _raw_connect_app(pid: int) -> Any:
    """
    Returns a raw CT.APPLICATION object from the given process.
    """
    if pid <= 0:
        raise ValueError(f"Invalid process id {pid}.")

    if not psutil.pid_exists(pid):
        raise ValueError(f"Process with pid {pid} does not exist or has already terminated.")

    objects = _get_app_monikers_from_rot([pid])
    if len(objects) == 0:
        raise Exception(f"Could not find an IApplicationInterface for pid {pid} in the RunningObjectTable.")

    iunknown, _ = objects[0]
    query = iunknown.QueryInterface(pythoncom.IID_IDispatch)
    raw_app = _dispatch_with_errorhandling(query, resultCLSID="CT.Application")
    _check_dispatch_cast(pid, raw_app)
    return raw_app


def _raw_connect_dbe(pid: int) -> Any:
    if pid <= 0:
        raise ValueError(f"Invalid process id {pid}.")

    if not psutil.pid_exists(pid):
        raise ValueError(f"Process with pid {pid} does not exist or has already terminated.")

    objects = _get_dbe_monikers_from_rot([pid])
    if len(objects) == 0:
        raise Exception(f"Could not find an IDbeApplicationInterface for pid {pid} in the RunningObjectTable.")

    iunknown, _ = objects[0]
    factory = iunknown.QueryInterface(pythoncom.IID_IClassFactory)
    instance = factory.CreateInstance(None, pythoncom.IID_IDispatch)
    del factory

    raw_dbe = _dispatch_with_errorhandling(instance, resultCLSID="CT.DbeApplication")
    _check_dispatch_cast(pid, raw_dbe)
    return raw_dbe


def _get_default_app() -> Optional[int]:
    running_e3_pids = get_running_e3s()
    if len(running_e3_pids) == 0:
        return None

    current_process = psutil.Process()
    parent_process_pids: list[int] = [process.pid for process in current_process.parents()]

    for parent_process_pid in parent_process_pids:
        if parent_process_pid in running_e3_pids:
            return parent_process_pid

    return running_e3_pids[0] if len(running_e3_pids) > 0 else None


def _get_default_dbe() -> Optional[int]:
    running_e3_pids = get_running_dbes()
    if len(running_e3_pids) == 0:
        return None

    current_process = psutil.Process()
    parent_process_pids: list[int] = [process.pid for process in current_process.parents()]

    for parent_process_pid in parent_process_pids:
        if parent_process_pid in running_e3_pids:
            return parent_process_pid

    return running_e3_pids[0] if len(running_e3_pids) > 0 else None


def _variant_to_dict(variant: Any, zeroBasedEntries: bool = True) -> dict[Any, tuple[Any, ...]]:
    result = {}
    try:  # Check if the dict contained in the variant is empty (might be a wrong variant as well)
        variant.keys()
        variant.items()
    except:
        return result
    keys = variant.keys()
    items = variant.Items()
    if len(keys) != len(items):
        raise AttributeError("Failed converting into dict!")
    if zeroBasedEntries:
        for key, item in zip(keys, items):
            result[key] = item
    else:
        for key, item in zip(keys, items):
            result[key] = item[1:] if type(item) is tuple and len(item) > 0 else tuple()
    return result

def _dict_to_variant(d:dict) -> None:
    com_dict = win32com.client.Dispatch("Scripting.Dictionary")
    if not type(d) is dict:
        return com_dict
    for k, v in d.items():
        com_dict.Add(k, v)
    return com_dict

class E3seriesOutput:
    """
    This class helps to redirect the output of the print function to an instance of E3.series. Usage:
    ```
    import e3series as e3
    import sys

    app = e3.Application()
    sys.stdout = e3.tools.E3seriesOutput(app, sys.stdout)
    print("hello") # the output is written to console and to the E3.series Message window.
    ```
    If you also set `sys.stderr` the output of stacktraces and the warnings module is also redirected to E3.series:
    ```
    sys.stderr = tools.E3seriesOutput(app, sys.stderr, (255, 0, 0))
    raise Exception("test") # Uncaught exceptions are now written to E3.series
    ```

    If you want to reset the output after a certain task, you have to save the old `sys.stdout` in a temporary variable and set it back to its original value after your task:
    ```
    app = e3.Application()
    temp = sys.stdout
    sys.stdout = E3seriesOutput(app, temp)
    print("hello1") # the output is written to console and to the E3.series Message window.
    sys.stdout = temp
    print("hello2") # the output is written only to console.
    ```
    Due to restrictions in the E3 COM-API this class adds a line break every time the stream gets flushed.
    """

    def __init__(self, app: Union[Application, DbeApplication], stream: Optional[TextIO], color: Optional[tuple[int, int, int]] = None) -> None:
        """
        Creates a new instance of `E3seriesOutput`.

        :param app: The application or dbeapplication object to write to.
        :param stream: This argument must be a file like object. If it is provided, the messages are additionally written to this stream.
        :param color: The color that is used to display the text in E3.series. If no color is provided the default color is used (black).
        """
        self._stream = stream
        self._app = app
        self._color = color
        self._buffer: list[str] = []

    def _flush_buffer(self) -> None:
        if len(self._buffer) > 0:
            text = "".join(self._buffer)
            self._buffer.clear()
            if self._color is None:
                self._app.PutMessage(text)
            else:
                self._app.PutMessageEx(0, text, 0, self._color[0], self._color[1], self._color[2])

    def write(self, s: str) -> int:
        length = len(s)
        if self._stream is not None:
            self._stream.write(s)

        # PutMessage always adds a linebreak at the end. Because of this
        # we can't call PutMessage if the message does not end with a linebreak.
        # Instead we collect these messages in the self._buffer - list.
        # The content of the list is printed when the next linebreak is given to write.

        s = s.replace("\r\n", "\n")
        line_break_index = s.rfind("\n")
        if line_break_index == -1:
            self._buffer.append(s)
        else:
            start = s[0:line_break_index]
            if start != "":
                self._buffer.append(start)
            self._flush_buffer()

            rest = s[line_break_index + 1 :]
            if rest != "":
                self._buffer.append(rest)
        return length

    def flush(self) -> None:
        if self._stream is not None:
            self._stream.flush()
        self._flush_buffer()
