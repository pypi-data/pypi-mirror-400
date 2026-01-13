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


from enum import IntEnum, IntFlag


class WdfFlags(IntFlag):
    NoFlag = 0

    XYXY = (1 << 0)
    """Multiple X list and data blocks exist"""

    Checksum = (1 << 1)
    """checksum is enabled"""

    CosmicRayRemoval = (1 << 2)
    """hardware cosmic ray removal was enabled"""

    Multitrack = (1 << 3)
    """separate x-list for each spectrum"""

    Saturation = (1 << 4)
    """saturated datasets exist"""

    FileBackup = (1 << 5)
    """a complete backup file has been created"""

    Temporary = (1 << 6)
    """this is a temporary file set for Display Title else filename"""

    Slice = (1 << 7)
    """Indicates that file has been extracted from WdfVol file slice like X / Y / Z."""

    PQ = (1 << 8)
    """Indicates that the measurement was performed with a PQ."""


class WdfType(IntEnum):
    Unspecified = 0
    Single = 1
    """file contains a single spectrum"""
    Series = 2
    """file contains multiple spectra with one common data origin (time, depth, temperature etc)"""
    Map = 3
    """file contains multiple spectra with more that one common data origin. Typically area maps
    use X and Y spatial origins. Volume maps use X, Y and Z. The WMAP block normally defines the
    physical region.obeys the maparea object. check scan type for streamline, linefocus, etc."""


class WdfSpectrumFlags(IntFlag):

    NoFlag = 0

    Saturated = (1 << 0)
    """Saturation flag. Some part of the spectrum data was saturated"""

    Error = (1 << 1)
    """Error flag. An error occurred while collecting this spectrum"""

    CosmicRay = (1 << 2)
    """Cosmic ray flag. A cosmic ray was detected and accepted in software"""

    # Error codes for PAF autofocus
    LTSuccess = (1 << 3)
    """LiveTrack signal was successul"""

    PAFSignalError = (1 << 4)
    """PAF signal was insufficient to track focus for this spectrum"""

    PAFTooMuchSpread = (1 << 5)
    """Quality of PAF signal was too poor to track focus for this spectrum"""

    PAFDirectionsDisagree = (1 << 6)
    """PAF prospective moves differed in direction for this spectrum"""

    PAFSafeLimitsExceeded = (1 << 7)
    """PAF prospective move would have exceeded safe limits"""

    SaturationThresholdExceeded = (1 << 8)
    """Too large a number of saturated pixels were present"""

    SoftLimitReached = (1 << 9)
    """LiveTrack is at one of its soft-limits (in 'edge' mode)"""

    PointWasInterpolated = (1 << 10)
    """The z-value information for this point was interpolated from neighbouring points"""

    Masked = (1 << 48)
    """The spectrum is excluded by the current mask.

    Bits from the Masked bit up to 63 are all reserved for use with custom
    masking. These bits may be used by end-user software to indicate special
    masking of spectra.
    """


class WdfScanType(IntEnum):
    Unspecified = 0
    """for data that does not represent a spectrum collected from a Renishaw system"""

    Static = 1
    """for single readout off the detector. Can be spectrum or image"""

    Continuous = 2
    """for readouts using continuous extended scanning. Can be spectrum or image
    (unlikely; impossible for x axis readout)"""

    StepRepeat = 3
    """for multiple statics taken at slightly overlapping ranges, then 'stitched'
    together to a single extended spectrum. Can be spectrum or image (unlikely)"""

    FilterScan = 4
    """filter image and filter scan both supported purely for historical reasons"""

    FilterImage = 5

    StreamLine = 6
    """must be a WdfType_Map measurement"""

    StreamLineHR = 7
    """must be a WdfType_Map measurement"""

    Point = 8
    """for scans performed with a point detector"""

    # The values below for multitrack and linefocus are flags that can be ORed with the above integer values
    #   - multitrack discrete on fixed grating systems will only be static
    #   - multitrack discrete could, on a fibre-probe system, be continuous, stitched, or static
    #   - linefocusmapping couild be continuous, stitched, or static, but at time of writing is static

    WdfScanType_MultitrackStitched = 0x0100
    """result is not a multitrack file"""
    WdfScanType_MultitrackDiscrete = 0x0200
    """result is multitrack file (wdf header has multitrack flag set)"""
    WdfScanType_LineFocusMapping = 0x0400
    """Could be Static, Continuous (not yet implemented, impossible for x axis
    readout), or StepAndRepeat (not yet implemented)"""


class WdfBlockId(IntEnum):
    """
    Block identity values

    Renishaw will only use uppercase letter values. Third-parties may
    define their own block ids but should use lower-case letter values.
    """

    FILE = 0x31464457  # 'W' 'D' 'F' '1'
    """File header block id."""
    DATA = 0x41544144  # 'D' 'A' 'T' 'A'
    """Spectral data block id."""
    YLIST = 0x54534c59  # 'Y' 'L' 'S' 'T'
    XLIST = 0x54534c58  # 'X' 'L' 'S' 'T'
    ORIGIN = 0x4e47524f  # 'O' 'R' 'G' 'N'
    """Data origin block id (additional values per spectrum,
    ie: spatial coordinates, timestamp and so on)"""
    COMMENT = 0x54584554  # 'T' 'E' 'X' 'T'
    """Free-form file comment block id."""
    WIREDATA = 0x41445857  # 'W' 'X' 'D' 'A'
    """Global file properties block id."""
    DATASETDATA = 0x42445857  # 'W' 'X' 'D' 'B'
    """Per-spectrum extended property information block id."""
    MEASUREMENT = 0x4d445857  # 'W' 'X' 'D' 'M'
    """WiRE measurement definition block id."""
    CALIBRATION = 0x53435857  # 'W' 'X' 'C' 'S'
    INSTRUMENT = 0x53495857  # 'W' 'X' 'I' 'S'
    MAPAREA = 0x50414d57  # 'W' 'M' 'A' 'P'
    WHITELIGHT = 0x4c544857  # 'W' 'H' 'T' 'L'
    THUMBNAIL = 0x4c49414e  # 'N' 'A' 'I' 'L'
    MAP = 0x2050414d  # 'M' 'A' 'P' ' '
    CURVEFIT = 0x52414643  # 'C' 'F' 'A' 'R'
    COMPONENT = 0x534c4344  # 'D' 'C' 'L' 'S'
    PCA = 0x52414350  # 'P' 'C' 'A' 'R'
    EM = 0x4552434d  # 'M' 'C' 'R' 'E'
    ZELDAC = 0x43444c5a  # 'Z' 'L' 'D' 'C'
    RESPONSECAL = 0x4c414352  # 'R' 'C' 'A' 'L'
    CAP = 0x20504143  # 'C' 'A' 'P' ' '
    PROCESSING = 0x50524157  # 'W' 'A' 'R' 'P'
    ANALYSIS = 0x41524157  # 'W' 'A' 'R' 'A'
    SPECTRUMLABELS = 0x4C424C57  # 'W' 'L' 'B' 'L'
    CHECKSUM = 0x4b484357  # 'W' 'C' 'H' 'K'
    RXCALDATA = 0x44435852  # 'R' 'X' 'C' 'D'
    RXCALFIT = 0x46435852  # 'R' 'X' 'C' 'F'
    XCAL = 0x4C414358  # 'X' 'C' 'A' 'L'
    SPECSEARCH = 0x48435253  # 'S' 'R' 'C' 'H'
    TEMPPROFILE = 0x504d4554  # 'T' 'E' 'M' 'P'
    UNITCONVERT = 0x56434e55  # 'U' 'N' 'C' 'V'
    ARPLATE = 0x52505241  # 'A' 'R' 'P' 'R'
    ELECSIGN = 0x43454c45  # 'E' 'L' 'E' 'C'
    BKXLIST = 0x4c584b42  # 'B' 'K' 'X' 'L'
    AUXILARYDATA = 0x20585541  # 'A' 'U' 'X' ' '
    CHANGELOG = 0x474c4843  # 'C' 'H' 'L' 'G'
    SURFACE = 0x46525553  # 'S' 'U' 'R' 'F'
    ARCALPLATE = 0x50435241  # 'A' 'R' 'C' 'P'
    PMC = 0x20434d50  # 'P' 'M' 'C' ' '
    CAMERAFIXEDFREQDATA = 0x44464643  # 'C' 'F' 'F' 'D'
    CLUSTER = 0x53554c43  # 'C' 'L' 'U' 'S'
    HIERARCHICALCLUSTER = 0x20414348  # 'H' 'C' 'A' ' '
    TEMPPTR = 0x52545054  # 'T' 'P' 'T' 'R'
    UNKNOWN = 0x3f4b4e55  # 'U' 'N' 'K' '?'
    WMSK = 0x4b534d57  # 'W' 'M' 'S' 'K'
    STDV = 0x56445453  # 'S' 'T' 'D' 'V'
    EDIT = 0x54494445  # 'E' 'D' 'I' 'T'
    WSLS = 0x534c5357  # 'W' 'S' 'L' 'S'
    WPAC = 0x43415057  # 'W' 'P' 'A' 'C'
    TRRD = 0x44525254  # 'T' 'R' 'R' 'D'
    AUTOANALYSIS = 0x4f545541  # 'A' 'U' 'T' 'O'
    CCDALIGN = 0x41444343  # 'C' 'C' 'D' 'A'
    ANY = 0xffffffff  # reserved value for @ref Wdf_FindSection
