"""
This script is a the Microsplit project, designed to process paired-end FASTQ files by fragmenting DNA sequences at specified restriction enzyme sites.

Copyright © 2024 Samir Bertache

SPDX-License-Identifier: AGPL-3.0-or-later

===============================================================================

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU Affero General Public License as published by the
Free Software Foundation, either version 3 of the License, or (at your option)
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

import argparse

from microsplit.split import cut

__version__ = "0.1.0"


class _Fmt(
    argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter
):
    pass


def main_cli():
    parser = argparse.ArgumentParser(
        description=(
            "Process Micro-C paired BAM files to paired FASTQ.\n"
            "Short options are provided for convenience."
        ),
        epilog=(
            "Example:\n"
            "  microsplit-cut -1 fwd.bam -2 rev.bam -o1 R1.fastq.gz -o2 R2.fastq.gz -t 12 -s 20 -l 0\n"
        ),
        formatter_class=_Fmt,
    )

    parser.add_argument(
        "-1",
        "--bam_for_file",
        type=str,
        help="Path to forward BAM file.",
        required=True,
    )
    parser.add_argument(
        "-2",
        "--bam_rev_file",
        type=str,
        help="Path to reverse BAM file.",
        required=True,
    )
    parser.add_argument(
        "-o1",
        "--output_forward",
        type=str,
        help="Path to output forward FastQ file.",
        required=True,
    )
    parser.add_argument(
        "-o2",
        "--output_reverse",
        type=str,
        help="Path to output reverse FastQ file.",
        required=True,
    )
    parser.add_argument(
        "-t",
        "--num_threads",
        type=int,
        help="Total number of threads.",
        required=False,
        default=6,
    )
    parser.add_argument(
        "-s",
        "--seed_size",
        type=int,
        help="Minimum size of a segment for extraction.",
        required=False,
    )
    parser.add_argument(
        "-l",
        "--lenght_added",
        type=int,
        help="Number of base pairs added to the neoformed fragment after completion of soft clipping (Default value is 0)",
        required=False,
        default=0,
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )

    args = parser.parse_args()
    cut(args)


if __name__ == "__main__":
    main_cli()
