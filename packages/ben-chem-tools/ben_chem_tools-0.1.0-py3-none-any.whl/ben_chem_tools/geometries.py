import numpy as np
import periodictable as pt

##################################################
# This file holds objects for geometries like 
# atoms and molecules.
##################################################


class xyz_atom:

    def __init__(self,atom_label:str,x_coord:float,y_coord:float,z_coord:float):

        self.atom_label = str(atom_label).split()[0]

        try: 
            self.x_coord = float(x_coord)
        except ValueError:
            raise ValueError("x_coord must be a numeric value.")
        try: 
            self.y_coord = float(x_coord)
        except ValueError:
            raise ValueError("y_coord must be a numeric value.")
        try: 
            self.z_coord = float(x_coord)
        except ValueError:
            raise ValueError("z_coord must be a numeric value.")
        
    @classmethod
    def from_string(cls,atom_string:str):
        atom_string = str(atom_string).strip().split()
        if len(atom_string) !=4:
            raise ValueError(f"Supplied string splits in to {len(atom_string)} items. Method requires 4.")
        return cls(*atom_string)

    @classmethod
    def from_cclib_vals(cls,atom_num:int,coords:list[float]):
        try: 
            atom_label = pt.elements[int(atom_num)]
        except ValueError:
            atom_label = atom_num
        except KeyError:
            KeyError(f"atom number {atom_num} not found")
        if len(coords) != 3:
            raise ValueError(f"coords is {len(coords)} long. It must have a length of 3.")
        return cls(atom_label,coords[0],coords[1],coords[2])
    
    def as_list(self):
        return [self.atom_label,[self.x_coord,self.y_coord,self.z_coord]]
    
    def apply_transormation(self,transformation_matrix,inplace=False):

        transformation_matrix = np.array(transformation_matrix)
        transformation_matrix = transformation_matrix.reshape((3,3))
        position_vector = np.array([self.x_coord,self.y_coord,self.z_coord])
        position_vector = position_vector @ transformation_matrix

        if inplace:
            self.x_coord = float(position_vector[0])
            self.y_coord = float(position_vector[1])
            self.z_coord = float(position_vector[2])
        return position_vector
        
    def __str__(self):
        return f"{self.atom_label}    {self.x_coord:.6f}     {self.y_coord:.6f}     {self.z_coord:.6f}"
    
    def __repr__(self):
        return f"{self.atom_label}    {self.x_coord:.6f}     {self.y_coord:.6f}     {self.z_coord:.6f}"




class xyz_molecule:

    def __init__(self,atom_list:list[xyz_atom]):
        self.atom_list:list[xyz_atom] = atom_list

    @classmethod
    def from_cclib_vals(cls,atom_nums,atom_coords):
        acc = []
        for atom_num,atom_coord in zip(atom_nums,atom_coords):
            acc.append(xyz_atom.from_cclib_vals(atom_num,atom_coords))
        return cls(acc)
    
    @classmethod
    def from_string(cls,molecule_string:str):
        molecule_string = molecule_string.strip()
        acc = []
        for atom_string in molecule_string.split("\n"):
            acc.append(xyz_atom.from_string(atom_string))
        return cls(acc)
    
    @classmethod
    def from_xyz_file(cls,file_path:str):
        with open(file_path,"r") as file:
            file_lines = file.readlines()
            num_atoms = int(file_lines[0].strip())
        acc = []
        for line in file_lines[2:2+num_atoms]:
            acc.append(xyz_atom.from_string(line))  
        return cls(acc)  

    def add_atom(self,new_atom):
        self.atom_list.append(new_atom)



    def as_list(self):
        return [atom.as_list() for atom in self.atom_list]
    
    def write_xyz_file(self,file_name,comment_line=""):
        with open(file_name,"w") as outfile:
            outfile.write(f"{len(self.atom_list)}\n")
            outfile.write(f"{comment_line}\n")
            for atom in self.atom_list:
                outfile.write(f"{str(atom)}\n")
    
    def apply_transformation(self,transformation_matrix,inplace=False):
        transformed_coords = []
        for atom in self.atom_list:
            transformed_coords.append(atom.apply_transormation(transformation_matrix,inplace))
        return transformed_coords
    
    def __str__(self):
        acc = ""
        for atom in self.atom_list:
            acc += f"{str(atom)}\n"
        acc = acc.strip()
        return acc
    
    def __repr__(self):
        acc = ""
        for atom in self.atom_list:
            acc += f"{str(atom)}\n"
        acc = acc.strip()
        return acc

