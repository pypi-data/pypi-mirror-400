import os
from typing import Iterable

from atomflow.components import *
from atomflow.aspects import *
from atomflow.atom import Atom
from atomflow.formats import Format
from atomflow.knowledge import *

class PDBFormat(Format):

    recipe = {
        "and": [
            IndexAspect,
            ElementAspect,
            ResNameAspect,
            ChainAspect,
            ResIndexAspect,
            CoordXAspect,
            CoordYAspect,
            CoordZAspect,
        ]
    }

    extensions = (".pdb",)

    @staticmethod
    def atom_from_line(line: str) -> Atom | None:

        record_type = line[:6].strip()
        if record_type not in ("ATOM", "HETATM"):
            return

        name = line[12:16].strip()
        elem = line[76:78].strip()

        cmps = [
            IndexComponent(line[6:11]),
            NameComponent(name),
            ChainComponent(line[21:22]),
            ResIndexComponent(line[22:26]),
            CoordXComponent(line[30:38]),
            CoordYComponent(line[38:46]),
            CoordZComponent(line[46:54]),
            ElementComponent(elem),
        ]

        # Extract position part from name
        if position := name[len(elem):]:
            cmps.append(PositionComponent(position))

        # Determine polymer type from residue name, and give appropriate residue component
        res_name = line[17:20].strip()

        if res_name in AA_RES_TO_SYM:
            cmps.append(AAResidueComponent(res_name))
        elif res_name in DNA_RES_TO_SYM:
            cmps.append(DNAResidueComponent(res_name))
        elif res_name in RNA_RES_CODES:
            cmps.append(RNAResidueComponent(res_name))
        else:
            cmps.append(ResidueComponent(res_name))

        # Optional fields
        if altloc := line[16:17].strip():
            cmps.append(AltLocComponent(altloc))

        if insertion := line[26:27].strip():
            cmps.append(InsertionComponent(insertion))

        if occupancy := line[54:60].strip():
            cmps.append(OccupancyComponent(occupancy))

        if b_factor := line[60:66].strip():
            cmps.append(TemperatureFactorComponent(b_factor))

        if charge := line[78:80].strip():
            cmps.append(FormalChargeComponent(charge))

        return Atom(*cmps)

    @classmethod
    def line_from_atom(cls, atom: Atom) -> str:

        if not atom.implements(cls.recipe):
            raise ValueError(f"{atom} does not implement aspects required for PDB format")

        record_type = "ATOM" if atom.implements(PolymerAspect) else "HETATM"

        if atom.implements("name") and atom.name == "UNK":
            name_field = " UNK"

        # If the atom has the aspects needed to make a name field (element & position), build it
        elif atom.implements(PositionAspect):
            name_field = f"{atom.element: >2}{atom.position: <2}"

            # Hydrogen positions sometimes spill over on the right - remove leading space to correct
            if len(name_field) > 4:
                name_field = name_field.strip()

        else:
            name_field = f"{atom.element: >2}  "

        altloc = atom.altloc if atom.implements(AltLocAspect) else ''
        ins = atom.insertion if atom.implements(InsertionAspect) else ''
        occ = atom.occupancy if atom.implements(OccupancyAspect) else 1
        b = atom.temp_f if atom.implements(TemperatureFactorAspect) else 0
        charge = atom.fcharge if atom.implements(FormalChargeAspect) else ''
        _ = ' '

        return \
            f"{record_type: <6}{atom.index: >5}{_}{name_field}{altloc: >1}"\
            f"{atom.resname: >3}{_}{atom.chain}{atom.resindex: >4}{ins: >1}{_: >3}"\
            f"{atom.x: >8.3f}{atom.y: >8.3f}{atom.z: >8.3f}{occ: >6.2f}{b: >6.2f}{_: >10}"\
            f"{atom.element :>2}{charge :<2}"

    @classmethod
    def read_file(cls, path: str | os.PathLike) -> list[Atom]:

        with open(path, "r") as file:
            atoms = [PDBFormat.atom_from_line(ln) for ln in file.readlines()
                     if ln.startswith("ATOM") or ln.startswith("HETATM")]

        return atoms

    @classmethod
    def to_file(cls, atoms: Iterable[Atom], path: str | os.PathLike) -> None:

        text = "\n".join(cls.line_from_atom(a) for a in atoms)
        with open(path, "w") as file:
            file.write(text + "\n")
