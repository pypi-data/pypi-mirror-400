import os
from collections import defaultdict
from operator import itemgetter
from typing import Iterable

from atomflow.atom import Atom
from atomflow.formats import Format
from atomflow.aspects import (ResOLCAspect,
                              ResIndexAspect,
                              ChainAspect,
                              EntityAspect,
                              PolymerAspect)
from atomflow.components import (AAResidueComponent,
                                 DNAResidueComponent,
                                 RNAResidueComponent,
                                 EntityComponent,
                                 ResIndexComponent)
from atomflow.knowledge import *


class FastaFormat(Format):

    recipe = {
        "and": [
            ResOLCAspect,
            ResIndexAspect,
            {"or": [
                {"and": [
                    PolymerAspect,
                    ChainAspect
                ]},
                EntityAspect,
            ]},
        ],
    }

    extensions = (".fasta", ".faa", ".fna")

    @classmethod
    def read_file(cls, path: str | os.PathLike) -> list[Atom]:

        with open(path, "r") as file:
            lines = reversed([line.strip() for line in file.readlines()])

        atoms = []
        seq_lines = []

        for ln in lines:
            if ln.startswith(">"):

                # Extract identifier from header
                header = ln.lstrip(">")
                if header[:3] in ("sp|", "tr|"):
                    header = header[3:]
                identifier = header.split("|")[0]
                ent = EntityComponent(identifier)

                # Compose sequence from gathered lines
                seq = "".join(seq_lines)

                # Determine polymer type from the sequence
                symbol_set = set(seq)
                if not symbol_set - DNA_ONE_LETTER_CODES:
                    cmp_type = DNAResidueComponent
                elif not symbol_set - RNA_RES_CODES:
                    cmp_type = RNAResidueComponent
                elif not symbol_set - AA_ONE_LETTER_CODES:
                    cmp_type = AAResidueComponent
                else:
                    raise ValueError(f"Could not determine polymer type of sequence:\n{seq[:20]}...")

                # Convert sequence into a list of atoms
                new_atms = []
                for i, res in enumerate(seq):
                    resn = cmp_type(res)
                    resi = ResIndexComponent(i+1)
                    new_atms.append(Atom(resn, resi, ent))
                atoms = new_atms + atoms

                seq_lines = []

            else:
                seq_lines.insert(0, ln)

        return atoms

    @classmethod
    def to_file(cls, atoms: Iterable[Atom], path: str | os.PathLike) -> None:

        residue_sets = defaultdict(set)

        # Collect unique (index, res_code) pairs by entity
        for atom in atoms:

            # Skip atoms without needed information
            if not atom.implements(cls.recipe):
                continue

            # Get or compose entity name
            if atom.implements(EntityAspect):
                ent = atom.entity
            else:
                ent = atom.polymer + "_" + atom.chain

            residue_sets[ent].add((atom.resindex, atom.res_olc))

        # Assemble residue codes into sequences, and collect unique sequences by entity
        seqs = {}
        for ent, residues in residue_sets.items():
            seq = "".join([r for _, r in sorted(residues, key=itemgetter(0))])
            if seq in seqs:
                continue
            seqs[seq] = ent

        # Write out all sequences to one file
        with open(path, "w") as file:
            file.writelines([f">{ent}\n{seq}\n" for seq, ent in seqs.items()])


if __name__ == '__main__':
    pass