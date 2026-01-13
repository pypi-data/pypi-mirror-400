# -*- coding: utf-8 -*-

class ConvRegistry:
    converters = {}


def get_converters():
    return ConvRegistry.converters


class BaseConverter:
    def __init_subclass__(cls):
        ConvRegistry.converters[cls.format] = cls

    @staticmethod
    def arguments(ap):
        """
        Adds format-specific parameters in the parser

        Parameters
        ----------
        ap : argparse.ArgumentParser
            Argument parser.

        Returns
        -------
        None.

        """

    def to_rtxt(self, rtxt):
        """
        Save molecule data in the RISM molecule file (rtxt)

        Parameters
        ----------
        rtxt : file-like, str, pathlib.Path, optional
            path to write RISM molecule file. If None write to stdout.
            The default is None.

        Returns
        -------
        None.

        """
