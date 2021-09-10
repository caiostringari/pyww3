import os
from .utils import (run, mpirun)
from .namelists import add_namelist_block, remove_namelist_block


class WW3Base():
    """
    Define the base class WW3(). Everything else enhirits from this class.
    """

    def to_file(self):
        """Write namelist text to file ww3_?.nml."""
        if os.path.isfile(os.path.join(self.runpath, self.output)):
            os.remove(os.path.join(self.runpath, self.output))
        with open(os.path.join(self.runpath, self.output), 'w') as f:
            f.write(self.text)

    def run(self, mpi=False, nproc=2):
        """Run a program using mpi or not."""
        if mpi:
            res = mpirun(self.runpath, self.EXE, nproc)
        else:
            res = run(self.runpath, self.EXE)
        self.__setattr__("returncode", res.returncode)
        self.__setattr__("stdout", res.stdout)
        self.__setattr__("stderr", res.stderr)

    def update_text(self, block: str, action: str = "add", index: int = -1):
        """Update namelist block in the text with an action."""

        # add case
        if action.lower().startswith("a"):
            newtext = add_namelist_block(self.text, block, index)

        # remove case
        else:
            newtext = remove_namelist_block(self.text, block)

        # update class attribute
        self.__setattr__("text", newtext)