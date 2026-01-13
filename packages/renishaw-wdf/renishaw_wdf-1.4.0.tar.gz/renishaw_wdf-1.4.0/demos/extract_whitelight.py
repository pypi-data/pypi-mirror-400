# Copyright (c) 2022 Renishaw plc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Extract a whitelight image from a Wdf file into a separate JPEG file.
"""

import sys
import os
import argparse
from io import BytesIO

# allow demos to load the wdf package from the parent folder (not required for normal installation)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from wdf import Wdf, WdfBlockId


def extract_spectrum_whitelight(wdf: Wdf, options: argparse.Namespace):
    """Extract a per-dataset image.

    Images may be collected before and/or after a scan during a measurement. It is possible
    to do this for only some of the scans or for all scans. This gets stored in the per-dataset
    data section. This section begins with a table of 64 bit offsets indexed by the dataset number.
    If the offset is 0 then there is no additional data stored. Otherwise the offset is the location
    of the start of the additional data stream from the start of the table. The first 4 bytes at
    the offset location are the length of the persisted PSET data as a 4 byte unsigned integer
    and this is then followed by that many bytes to be read as a PSET."""

    pset = wdf.get_spectrum_properties(options.dataset)
    name = 'ImageBefore' if options.before else 'ImageAfter'
    if pset and name in pset:
        # Copy the image data to the output file.
        image_stream = BytesIO(pset[name].value)
        with open(options.outpath, 'wb') as output:
            output.write(image_stream.read(-1))


def extract_whitelight(wdf: Wdf, options: argparse.Namespace):
    """Extract the embedded whitelight image.

    The WHITELIGHT section simply contains a JPEG image stream so this can just be copied
    from the section data to the output file."""

    stream = wdf.get_section_stream(WdfBlockId.WHITELIGHT, options.uid)
    with open(options.outpath, 'wb') as output:
        output.write(stream.read(-1))


def main(args=None):
    """Application entry"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-n', '--uid', type=int, default=-1, help='Whitelight image section number')
    group = parser.add_argument_group(
        'per-spectrum image',
        description='Select a per-spectrum image (either before or after the data collection)')
    group.add_argument('--spectrum', type=int, default=None, help='Index of the spectrum')
    xgroup = parser.add_mutually_exclusive_group(required=True)
    xgroup.add_argument(
        '--before', action='store_true',
        help='Retrieve the image obtained before data collection')
    xgroup.add_argument(
        '--after', action='store_true',
        help='Retrieve the image obtained after data collection')
    parser.add_argument('filename', type=str, help="Path to the Wdf file.")
    parser.add_argument('outpath', type=str, help="Path to the output file.")
    options = parser.parse_args(args)

    with Wdf(options.filename) as wdf:
        if options.spectrum:
            extract_spectrum_whitelight(wdf, options)
        else:
            extract_whitelight(wdf, options)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
