"""
Class to abstract WW3 executables and some other usefull things.
"""
import os
import shutil
import subprocess

from logging import warning


def cmd_exists(cmd):
    "Check if a system command is available."

    # verify if all executables are working
    if shutil.which(cmd):
        return True
    else:
        raise OSError(f"Command \'{cmd}\' is not available."
                      "Please make sure WW3 was compiled properly "
                      "and that the executables are set in your $PATH.")


def run(runpath, cmd):
    "Run a command in a given path."
    cmd_exists(cmd)
    print(f"Running {cmd}, please wait...")
    path_before = os.getcwd()  # wherever path we where before
    os.chdir(runpath)  # change to the run path because of WW3
    out = subprocess.run(cmd, shell=True, check=False, capture_output=True)
    os.chdir(path_before)  # go back to where we were
    print(f"Done running {cmd}. Return code was {out.returncode}.")
    return out


def mpirun(runpath, cmd, nproc):
    "Run a command in a given path using mpi."
    cmd_exists(cmd)
    print(f"Running {cmd} with MPI, please wait...")
    path_before = os.getcwd()  # wherever path we where before
    os.chdir(runpath)  # change to the run path because of WW3
    mpicmd = f"mpirun -n {nproc} {cmd}"
    out = subprocess.run(mpicmd, shell=True, check=False, capture_output=True)
    os.chdir(path_before)  # go back to where we were
    print(f"Done running {cmd}. Return code was {out.returncode}.")
    return out


def bool_to_str(mybool, long=False):
    """Convert a boolean to \'t\' or \'f\'."""
    if mybool:
        if long:
            return "true"
        else:
            return "t"
    else:
        if long:
            return "false"
        else:
            return "f"


def verify_runpath(runpath):
    """Verify if run_path exists, if not warn and create it"""
    if not os.path.isdir(runpath):
        error = f"Path \'{runpath}\' does not exist, I am creating it for you."
        warning(error)
        os.makedirs(runpath)


def verify_mod_def(runpath, mod_def):
    """Verify for mod_def file exists in the runpath."""
    if not os.path.isfile(mod_def):
        error = f"No such file or directory \'{mod_def}\'"
        raise ValueError(error)
    if not os.path.isfile(os.path.join(runpath, "mod_def.ww3")):
        try:
            shutil.copy(os.path.abspath(mod_def),
                        os.path.join(runpath, "mod_def.ww3"))
        except Exception:
            error = "Could not create \'mod_def.ww3\' in the run path."
            raise ValueError(error)


def verify_ww3_out(runpath, out):
    """Verify if ww3_grd|ww3_pnt exists in the runpath."""
    if os.path.basename(out) not in ["out_grd.ww3", "out_pnt.ww3"]:
        raise ValueError(f"Unknown file type \'{out}\'.")

    if not os.path.isfile(out):
        error = f"No such file or directory \'{out}\'."
        raise ValueError(error)

    # verify if ww3_?.www3 is in the same path as run_path
    runout = os.path.join(runpath, os.path.basename(out))
    if not os.path.isfile(runout):
        warn = (f"File \'{out}\' is not in the run path. "
                "I am creating a link for you.")
        warning(warn)
        os.symlink(os.path.abspath(out), runout)


def verify_ww3_file(runpath, out):
    """Verify if any file exists in the runpath."""
    if not os.path.isfile(out):
        error = f"No such file or directory \'{out}\'."
        raise ValueError(error)

    # verify if the is in the same path as run_path
    runout = os.path.join(runpath, os.path.basename(out))
    if not os.path.isfile(runout):
        warn = (f"File \'{out}\' is not in the run path. "
                "I am creating a link for you.")
        warning(warn)
        os.symlink(os.path.abspath(out), runout)
