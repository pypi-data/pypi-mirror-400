from glob import glob
import cclib
import periodictable as pt
from .geometries import xyz_molecule, xyz_atom
import os


class g16_input:
    """ a base level g16 input file
    """

    def __init__(self, input_line:str, geometry:xyz_molecule, file_name:str,charge:int,spin_mult:int, nproc = 36,mem = 5):
        self.checkpoint = file_name[:-3] + "chk"
        self.file_name = file_name
        self.geometry = geometry
        self.mem = mem
        self.nproc = nproc
        self.input_line = input_line.lower()
        self.extra = ""
        self.title_card = "Title Card"
        self.charge = charge
        self.spin_mult = spin_mult


    def write_file(self):
        """writes a file associated with the g16 input instance
        """
        out_string = f"""%chk={self.checkpoint}
%nproc={self.nproc}
%mem={self.mem}GB
#p {self.input_line}

{self.title_card}

{self.charge} {self.spin_mult}
{str(self.geometry)}

{self.extra}


"""
        with open(self.file_name,"w") as file:
            file.write(out_string)

    @classmethod
    def from_file(cls,file_name):
        collect_input = False
        input_line = ""
        nproc = 36
        mem = 5
        charge_collected = False
        charge = 0
        spin_mult = 1
        Title_Card = False
        blank_counter = 0 
        geometry = xyz_molecule([])

        with open(file_name,"r") as file:
            for line in file:
                true_line = line.strip(" \n")

                if "%mem" in true_line:
                    mem = int(true_line.split("=")[1][:-2])

                if "%nproc" in true_line:
                    nproc = int(true_line.split("=")[1])

                if collect_input == True and blank_counter == 0:
                    input_line = input_line + " " + line.strip(" \n")

                if "#p" in true_line:
                    collect_input = True
                    input_line = input_line + line.strip("\n")

                if blank_counter == 2 and charge_collected and true_line != "":
                    geometry.add_atom(xyz_atom.from_string(true_line))

                if blank_counter == 2 and charge_collected == False:
                    true_line = line.strip(" \n\t")
                    charge_mult = true_line.split()
                    charge = charge_mult[0]
                    spin_mult = charge_mult[1]
                    charge_collected = True
                
                if true_line.strip("\t") == "":
                    blank_counter = blank_counter + 1

                                 

        return cls(input_line,geometry,file_name,charge,spin_mult,nproc = nproc,mem = mem)


def stationary_point_count(output_file_pattern:str="*.log"):
    """Evaluates files for number of stationary points
Parameters
----------
output_file_pattern (str): a file pattern to match and evaluate stationary points.

Returns
-------
list[tuple[str,int]]: a list of tuples containing the names of the log files and the number of stationary points"""

    results ={}

    for output_file in glob(output_file_pattern):
        results[output_file] = 0
        with open(output_file) as current_file:
            for line in current_file:
                results[output_file] += "Stationary point" in line

    results = [(key,results[key]) for key in results.keys()]
    if len(results.keys()) == 0:
        raise FileExistsError(f"No files found to match pattern '{output_file_pattern}'.")
    results = sorted(results,key = lambda x: x[1])
    return results


def get_n_geometry(log_file_name:str,n_geometry:int = -1):
    """Grabs the nth geometry (zero indexed) from a log file. Defaults to the last geometry
Parameters
----------
log_file_name (str): the path to a log file

n_geometry (int): the index of the desired geometry

Returns
-------
xyz_molecule"""

    outfile = cclib.io.ccread(log_file_name)
    atom_nums = outfile.atomnos
    correct_geom = outfile.geometries[n_geometry]
    return xyz_molecule.from_cclib_vals(atom_nums,correct_geom)

def rerun_from_last_geom(file_to_rerun):
    """reruns a job from the last geometry found in the log file.
Parameters
----------
file_to_rerun (str): the path to a log file

Returns
-------
None: reformats and resubmits g16 input"""
    new_geometry = get_n_geometry(file_to_rerun)
    old_input = g16_input.from_file(file_to_rerun[:-3]+"gjf")
    old_input.geometry = new_geometry
    old_input.write_file()
    print(f"Rerunning {file_to_rerun[:-4]}")
    os.system(f"sbatch {file_to_rerun[:-3]+"s"}")

def quick_rerun_optimizations(log_file_pattern:str="*.log"):
    """Reruns any files with only one stationary point, and notifies about files with 0 stationary points
Parameters
----------

log_file_pattern (str): a pattern for the path of files to rerun.

Returns
-------
None: reruns files with only 1 stationary point and prints advice for files with 0."""
    statp_eval = stationary_point_count(log_file_pattern)

    for file,statp_count in statp_eval:
        if statp_count == 1:
            rerun_from_last_geom(file)
        elif statp_count == 0:
            print(f"{file} requires manual check, not Stationary point found")





    