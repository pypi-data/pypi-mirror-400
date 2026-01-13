# -*- coding: utf-8 -*-
import os
import pathlib
from collections import namedtuple
from datetime import datetime

Atom = namedtuple('Atom', ['x', 'y', 'z', 'sigma', 'charge', 'epsilon',
                           'name', 'type', 'residue', 'res_no',
                           'seg_id'])


class Molecule:
    def __init__(self, atoms, files=None):
        """
        RISM molecule class

        Parameters
        ----------
        atoms : list of Atom
            List of atoms.
        files : TYPE, optional
            List of original data files. The default is {}.

        Returns
        -------
        None.

        """
        self.atoms = atoms
        self.natom = len(atoms)
        self.natyp = len(set(a.type for a in atoms))
        self.nftyp = len(set((a.sigma, a.epsilon) for a in atoms))
        self.nres = len(set(a.res_no for a in atoms))
        self.nrtyp = len(set(a.residue for a in atoms))
        self.nseg = len(set(a.seg_id for a in atoms if a.seg_id))
        self.nqtyp = len(set(a.charge for a in atoms))
        self.nqtot = sum(a.charge for a in atoms)
        if files is None:
            files = {}
        self._files = files

    def save(self, out=None):
        """
        Save molecule in RISM molecue file (rtxt)

        Parameters
        ----------
        out : file-like, str or pathlib.Path, optional
            File to save molecule. The default is None.

        Returns
        -------
        None.

        """
        if isinstance(out, (str, os.PathLike)):
            with pathlib.Path(out).open('w', encoding="utf-8") as f:
                self._save(f)
        else:
            self._save(out)

    def _save(self, f):
        nter_res = self.atoms[0].residue
        nter_q = sum(a.charge for a in self.atoms
                     if a.res_no == self.atoms[0].res_no)
        nter = f"{nter_res}({nter_q:+.2f})"
        cter_res = self.atoms[-1].residue
        cter_q = sum(a.charge for a in self.atoms
                     if a.res_no == self.atoms[-1].res_no)
        cter = f"{cter_res}({cter_q:+.2f})"

        print("# RISM input file (created by amber2rism program at"
              f" {datetime.now():%d/%m/%Y %H:%M:%S})", file=f)
        for ftype, fpath in self._files.items():
            print(f"# {ftype}: {fpath.resolve()}", file=f)

        print("#     I8X   I5X   I5X   I5X   I5X   I5X   I5X    F8.2"
              "X    A4(F6.2)X    A4(F6.2)", file=f)
        print("#  NATOM NATYP NFTYP  NRES NRTYP  NSEG NQTYP     QTOT"
              "         NTER         CTER", file=f)
        print(f"{self.natom:8d} {self.natyp:5d} {self.nftyp:5d} {self.nres:5d}"
              f" {self.nrtyp:5d} {self.nseg:5d} {self.nqtyp:5d}"
              f" {self.nqtot:8.2f} {nter:>12} {cter:>12}", file=f)

        print("#      F12.7       F12.7       F12.7     F10.6           F16.8"
              "     F10.6X  a4X  a4X  a4X   I5X  a4", file=f)
        print("#          X           Y           Z       SIG               Q"
              "       EPS ATOM ATYP  RES RESNO  SEG", file=f)
        for a in self.atoms:
            print(f"{a.x:12.7f}{a.y:12.7f}{a.z:12.7f}"
                  f"{a.sigma:10.6f}{a.charge:16.8f}{a.epsilon:10.6f}"
                  f" {a.name:4s} {a.type:4s}"
                  f" {a.residue:4s} {a.res_no:5d}"
                  f" {a.seg_id:4s}",
                  file=f)
