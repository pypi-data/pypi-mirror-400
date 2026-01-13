# -*- coding: utf-8 -*-
import argparse
from pathlib import Path

import parmed as pmd

from .base import BaseConverter
from .rism import Atom, Molecule


class AmberConverter(BaseConverter):
    """Converter of AMBER files into the RISM molecule file."""

    format = "amber"
    help = "from AMBER prmtop7 and inpcrd files"

    def __init__(self, args):
        self.prmtop = args.prmtop
        self.inpcrd = args.inpcrd
        self.amber = pmd.load_file(str(self.prmtop.resolve()),
                                   str(self.inpcrd.resolve()))

    def to_rtxt(self, rtxt):
        atoms = [
            Atom(
                x=a.xx, y=a.xy, z=a.xz, sigma=a.sigma, charge=a.charge,
                epsilon=a.epsilon, name=a.name, type=a.type,
                residue=a.residue.name, res_no=a.residue.idx + 1,
                seg_id=a.residue.segid
            ) for a in self.amber.atoms
        ]
        mol = Molecule(atoms, files={"TPF": self.prmtop, "CRF": self.inpcrd})
        mol.save(rtxt)

    @staticmethod
    def arguments(ap):
        ap.add_argument("prmtop", type=Path,
                        help="AMBER prmtop7 file")
        ap.add_argument("inpcrd", type=Path,
                        help="AMBER inpcrd file")


def main(argv=None):
    """
    Commanline interface for AMBER to RISM converter

    Parameters
    ----------
    argv : list, optional
        Arguments. If None uses `sys.argv`. The default is None.

    Returns
    -------
    None.

    """
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--rtxt", type=Path,
                    help="RISM molecule file")
    AmberConverter.arguments(ap)

    args = ap.parse_args(argv)

    conv = AmberConverter(args)
    conv.to_rtxt(args.rtxt)


if __name__ == "__main__":
    main()
