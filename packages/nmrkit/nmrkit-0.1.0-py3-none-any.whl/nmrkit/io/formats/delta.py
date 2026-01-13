import struct
from typing import Dict, Optional, List

import numpy as np

from nmrkit.core import NMRData, DimensionInfo, LinearGenerator
from nmrkit.io.base import FormatReader
from nmrkit.utils import complexify


class DeltaReader(FormatReader):
    # Maximum number of dimensions supported
    MAX_DIMENSIONS = 8

    # Header offsets (in bytes)
    OFFSET_ENDIAN_FLAG = 8  # Endianness flag
    OFFSET_DIM_COUNT = 12  # Number of dimensions
    OFFSET_DATA_TYPE = 14  # Data type byte
    OFFSET_DIM_TYPES = 24  # Dimension type flags
    OFFSET_DIM_SIZES = 176  # Dimension sizes
    OFFSET_AXIS_START = 272  # Axis start values
    OFFSET_AXIS_STOP = 336  # Axis stop values
    OFFSET_BASE_FREQ = 1064  # Base frequencies
    OFFSET_ZERO_POINT = 1128  # Zero points (offsets)
    OFFSET_PARAM_START = 1240  # Parameter start position
    OFFSET_PARAM_LENGTH = 1244  # Parameter length in bytes
    OFFSET_DATA_START = 1284  # Data start position
    OFFSET_DATA_LENGTH = 1288  # Data length in bytes

    # Dimension types
    DIM_TYPE_NONE = 0  # No type
    DIM_TYPE_REAL = 1  # Real data
    DIM_TYPE_TPPI = 2  # TPPI (Time-Proportional Phase Incrementation)
    DIM_TYPE_COMPLEX = 3  # Complex data
    DIM_TYPE_REAL_COMPLEX = 4  # Real-complex data (Magnitude)
    DIM_TYPE_ENVELOPE = 5  # Envelope

    # Bitmask for data type byte
    PRECISION_BIT = 0x40  # 7th bit for float32 precision

    # Block size for data reshaping
    BLOCK_SIZE = 32

    # Endian modes
    BIG_ENDIAN = 0  # Big-endian byte order
    LITTLE_ENDIAN = 1  # Little-endian byte order

    # Data formats
    FORMAT_1D = 1  # 1D NMR data
    FORMAT_2D = 2  # 2D NMR data
    FORMAT_3D = 3  # 3D NMR data
    FORMAT_4D = 4  # 4D NMR data
    FORMAT_5D = 5  # 5D NMR data
    FORMAT_6D = 6  # 6D NMR data
    FORMAT_7D = 7  # 7D NMR data
    FORMAT_8D = 8  # 8D NMR data
    FORMAT_SMALL2D = 12  # Small 2D data
    FORMAT_SMALL3D = 13  # Small 3D data
    FORMAT_SMALL4D = 14  # Small 4D data

    # Unit types (SI units)
    SIUNIT_NONE = 0  # No unit
    SIUNIT_ABUNDANCE = 1  # Abundance
    SIUNIT_HZ = 13  # Hertz
    SIUNIT_PPM = 26  # Parts per million
    SIUNIT_SECONDS = 28  # Seconds
    SIUNIT_DECIBEL = 35  # Decibel

    # Parameter value types
    PARMVAL_NONE = -1  # Not JEOL's definition
    PARMVAL_STR = 0  # String value
    PARMVAL_INT = 1  # Integer value
    PARMVAL_FLT = 2  # Float value
    PARMVAL_Z = 3  # Complex value
    PARMVAL_INF = 4  # Infinity value

    # Infinity types
    INF_NEG = 1  # Negative infinity
    INF_MINUS1 = 2  # Minus 1
    INF_ZERO = 3  # Zero
    INF_PLUS1 = 4  # Plus 1
    INF_POS = 5  # Positive infinity

    # String length constants
    JVAL_STRLEN = 16  # Length of string values
    NAMELEN = 128  # Length of names (assumed value)

    def __init__(self, filename: str, options: Optional[Dict] = None):
        super().__init__(filename, options)
        self._file = None
        self._dim_sizes = [0] * 8

        self._dim_types = [0] * 8
        self._axis_start = [0.0] * 8
        self._axis_stop = [0.0] * 8

        # Unit information for each dimension
        self._unit_types = [self.SIUNIT_NONE] * 8  # Unit type codes
        self._unit_exps = [0] * 8  # Unit exponents

    def read(self) -> NMRData:
        with open(self.filename, "rb") as self._file:
            self._parse_header()
            params = self._parse_params()
            data = self._read_data()
            dimensions = self._create_dimensions()
            metadata = self._create_metadata()

            return NMRData(
                data=data,
                dimensions=dimensions,
                metadata=metadata,
                source_format="delta",
                source_filename=self.filename,
            )

    def _parse_header(self) -> None:
        try:
            # Read the standard header buffer
            self._file.seek(0)
            hdr_buff = self._file.read(4096)

            # Verify we read the expected header size
            if len(hdr_buff) < 4096:
                raise IOError(
                    f"Expected to read 4096 bytes for header, but got {
                        len(hdr_buff)} bytes")

            # Read endian flag
            endian_flag = struct.unpack_from(
                "B", hdr_buff, self.OFFSET_ENDIAN_FLAG)[0]
            if endian_flag == 0:
                self._byte_order = "big"
            elif endian_flag == 1:
                self._byte_order = "little"
            else:
                raise ValueError(
                    f"Invalid endian flag: {endian_flag}. Expected 0 (big-endian) or 1 (little-endian)")

            # Read dimension count
            self._dim_count = struct.unpack_from(
                "B", hdr_buff, self.OFFSET_DIM_COUNT)[0]
            if self._dim_count < 1 or self._dim_count > self.MAX_DIMENSIONS:
                raise ValueError(
                    f"Invalid dimension count: {self._dim_count}. Expected 1-{self.MAX_DIMENSIONS}"
                )

            # Read data type (2 bits for type code, 7th bit for precision)
            data_type_byte = struct.unpack_from(
                "B", hdr_buff, self.OFFSET_DATA_TYPE)[0]
            # Check 7th bit for float32 precision
            self._data_type = (
                np.float32 if (
                    data_type_byte & self.PRECISION_BIT) else np.float64)

            # Read dimension types
            for i in range(self._dim_count):
                offset = self.OFFSET_DIM_TYPES + i
                self._dim_types[i] = struct.unpack_from(
                    "B", hdr_buff, offset)[0]

            # Read unit information (JEOL_JUNIT structure)
            # Each jUnit structure contains: unitType (1 byte), unitExp (1
            # byte), scaleType (1 byte)
            OFFSET_DATA_UNITS = 32
            for i in range(self._dim_count):
                offset = OFFSET_DATA_UNITS + i * 3
                self._unit_types[i] = struct.unpack_from(
                    "B", hdr_buff, offset)[0]
                self._unit_exps[i] = struct.unpack_from(
                    "B", hdr_buff, offset + 1)[0]
                # scaleType is unused for now

            # Read dimension sizes (always big-endian)
            for i in range(self._dim_count):
                offset = self.OFFSET_DIM_SIZES + i * 4
                self._dim_sizes[i] = struct.unpack_from(
                    ">I", hdr_buff, offset)[0]

            # Read axis start values (always big-endian)
            for i in range(self._dim_count):
                offset = self.OFFSET_AXIS_START + i * 8
                self._axis_start[i] = struct.unpack_from(
                    ">d", hdr_buff, offset)[0]

            # Read axis stop values (always big-endian)
            for i in range(self._dim_count):
                offset = self.OFFSET_AXIS_STOP + i * 8
                self._axis_stop[i] = struct.unpack_from(
                    ">d", hdr_buff, offset)[0]

            # Read base frequency (always big-endian)
            self._base_freq = [0.0] * self.MAX_DIMENSIONS
            fmt_float64 = ">d"  # Always use big-endian
            for i in range(self._dim_count):
                offset = self.OFFSET_BASE_FREQ + i * 8
                self._base_freq[i] = struct.unpack_from(
                    fmt_float64, hdr_buff, offset)[0]

            # Read zero point (offset) (always big-endian)
            self._zero_point = [0.0] * self.MAX_DIMENSIONS
            for i in range(self._dim_count):
                offset = self.OFFSET_ZERO_POINT + i * 8
                self._zero_point[i] = struct.unpack_from(
                    fmt_float64, hdr_buff, offset)[0]

            # Read parameter start position (always big-endian)
            self._param_start = struct.unpack_from(
                ">I", hdr_buff, self.OFFSET_PARAM_START
            )[0]

            # Read parameter length (always big-endian)
            self._param_length = struct.unpack_from(
                ">I", hdr_buff, self.OFFSET_PARAM_LENGTH
            )[0]

            # Read data start position (always big-endian)
            self._data_start = struct.unpack_from(
                ">I", hdr_buff, self.OFFSET_DATA_START
            )[0]

            # Read data length (always big-endian)
            self._data_length = struct.unpack_from(
                ">Q", hdr_buff, self.OFFSET_DATA_LENGTH
            )[0]

        except Exception as e:
            raise IOError(f"Failed to parse header: {str(e)}") from e

    def _parse_params(self) -> Dict:
        """Parse parameters from the JEOL Delta format file.

        Returns:
            Dict: A dictionary containing parsed parameters.
        """
        params = {}

        try:
            # Check if we have valid parameter section information
            if not hasattr(
                    self,
                    "_param_start") or not hasattr(
                    self,
                    "_param_length"):
                self._parse_header()

            # Skip if no parameters
            if self._param_length <= 0:
                return params

            # Read parameter header and values
            self._file.seek(self._param_start)
            param_data = self._file.read(self._param_length)

            # Verify we read the expected amount of data
            if len(param_data) != self._param_length:
                raise IOError(
                    f"Expected to read {
                        self._param_length} bytes for parameters, but got {
                        len(param_data)} bytes")

            # Parse parameter header
            parm_hdr_offset = 0
            parm_size = struct.unpack_from(
                ">I", param_data, parm_hdr_offset)[0]
            lo_id = struct.unpack_from(
                ">I", param_data, parm_hdr_offset + 4)[0]
            hi_id = struct.unpack_from(
                ">I", param_data, parm_hdr_offset + 8)[0]
            total_size = struct.unpack_from(
                ">I", param_data, parm_hdr_offset + 12)[0]

            # Calculate the number of parameters
            num_params = hi_id - lo_id + 1

            # Skip the parameter header
            param_val_offset = parm_hdr_offset + 16  # 4 ints * 4 bytes each

            # Parse each parameter value (DeltaParmVal)
            for i in range(num_params):
                # Check if we have enough data left
                if param_val_offset + \
                        (2 * (self.NAMELEN + 1)) + 4 + 16 + 16 + 4 > len(param_data):
                    break

                # Read parameter class name
                param_class = struct.unpack_from(
                    f">{self.NAMELEN + 1}s", param_data, param_val_offset
                )[0]
                param_class = param_class.decode(
                    "utf-8", errors="ignore").strip("\x00")
                param_val_offset += self.NAMELEN + 1

                # Read unit scale
                unit_scale = struct.unpack_from(
                    ">I", param_data, param_val_offset)[0]
                param_val_offset += 4

                # Skip units[2] (2 jUnit structs, total 24 bytes)
                # 2 * (int unitType, int unitExp, int scaleType) = 2 * 3 * 4
                # bytes
                param_val_offset += 24

                # Read value
                # Read string value
                str_val = struct.unpack_from(
                    f">{self.JVAL_STRLEN}s", param_data, param_val_offset
                )[0]
                str_val = str_val.decode(
                    "utf-8", errors="ignore").strip("\x00")
                param_val_offset += self.JVAL_STRLEN

                # Read double value
                double_val = struct.unpack_from(
                    ">d", param_data, param_val_offset)[0]
                param_val_offset += 8

                # Read integer value
                int_val = struct.unpack_from(
                    ">I", param_data, param_val_offset)[0]
                param_val_offset += 4

                # Read infinity type
                inf_type = struct.unpack_from(
                    ">I", param_data, param_val_offset)[0]
                param_val_offset += 4

                # Read complex value (jComplex)
                complex_re = struct.unpack_from(
                    ">d", param_data, param_val_offset)[0]
                complex_im = struct.unpack_from(
                    ">d", param_data, param_val_offset + 8)[0]
                param_val_offset += 16

                # Read value type
                val_type = struct.unpack_from(
                    ">I", param_data, param_val_offset)[0]
                param_val_offset += 4

                # Read parameter name
                param_name = struct.unpack_from(
                    f">{self.NAMELEN + 1}s", param_data, param_val_offset
                )[0]
                param_name = param_name.decode(
                    "utf-8", errors="ignore").strip("\x00")
                param_val_offset += self.NAMELEN + 1

                # Determine the actual value based on val_type
                actual_val = None
                if val_type == self.PARMVAL_STR:
                    actual_val = str_val
                elif val_type == self.PARMVAL_INT:
                    actual_val = int_val
                elif val_type == self.PARMVAL_FLT:
                    actual_val = double_val
                elif val_type == self.PARMVAL_Z:
                    actual_val = complex(complex_re, complex_im)
                elif val_type == self.PARMVAL_INF:
                    if inf_type == self.INF_NEG:
                        actual_val = float("-inf")
                    elif inf_type == self.INF_POS:
                        actual_val = float("inf")
                    elif inf_type == self.INF_ZERO:
                        actual_val = 0.0
                    elif inf_type == self.INF_PLUS1:
                        actual_val = 1.0
                    elif inf_type == self.INF_MINUS1:
                        actual_val = -1.0

                # Store parameter in dictionary
                if param_name:
                    if param_class:
                        if param_class not in params:
                            params[param_class] = {}
                        params[param_class][param_name] = actual_val
                    else:
                        params[param_name] = actual_val

        except Exception as e:
            # Log the error but don't fail the entire read operation
            import logging

            logging.warning(f"Failed to parse parameters: {str(e)}")

        return params

    def _read_raw_data(self) -> np.ndarray:
        """Read raw data from file and convert to numpy array"""
        try:
            self._file.seek(self._data_start)
            raw_data = self._file.read(self._data_length)

            # Verify that we read the expected amount of data
            if len(raw_data) != self._data_length:
                raise IOError(
                    f"Expected to read {
                        self._data_length} bytes, but got {
                        len(raw_data)} bytes")

            return np.frombuffer(raw_data, dtype=self._data_type)
        except Exception as e:
            raise IOError(
                f"Failed to read raw data from file: {
                    str(e)}") from e

    def _read_data(self) -> np.ndarray:
        data = self._read_raw_data()

        if self._dim_count == 1:
            if self._dim_types[0] == self.DIM_TYPE_REAL:
                return data
            elif self._dim_types[0] == self.DIM_TYPE_COMPLEX:
                # For complex 1D data: [real0, real1, ..., realN, imag0, imag1, ..., imagN]
                # Reshape into complex128 format: [complex0, complex1, ...,
                # complexN]
                return complexify(
                    data, mode="separated", first_component="real")
        elif self._dim_count == 2:
            target_shape = self._dim_sizes[0], self._dim_sizes[1]

            if (
                self._dim_types[0] == self.DIM_TYPE_COMPLEX
                and self._dim_types[1] == self.DIM_TYPE_REAL
            ) or (
                self._dim_types[0] == self.DIM_TYPE_REAL_COMPLEX
                and self._dim_types[1] == self.DIM_TYPE_REAL_COMPLEX
            ):
                # real first then imag, in block
                complex_data = complexify(
                    data, mode="separated", first_component="real"
                )
                return self._delta_reshape(complex_data, target_shape)

            elif (
                self._dim_types[0] == self.DIM_TYPE_COMPLEX
                and self._dim_types[1] == self.DIM_TYPE_COMPLEX
            ):
                # real first then imag, in block
                hypercomplex_size = data.size // 4
                real_real_part = self._delta_reshape(
                    data[:hypercomplex_size], target_shape
                )
                real_imag_part = self._delta_reshape(
                    data[hypercomplex_size: hypercomplex_size * 2], target_shape
                )
                imag_real_part = self._delta_reshape(
                    data[hypercomplex_size * 2: hypercomplex_size * 3], target_shape
                )
                imag_imag_part = self._delta_reshape(
                    data[hypercomplex_size * 3:], target_shape
                )
                dim2_real = real_real_part + 1j * real_imag_part
                dim2_imag = imag_real_part + 1j * imag_imag_part
                return np.concatenate((dim2_real, dim2_imag), axis=1)

        # Fallback for unsupported dimension counts or types
        return data

    def _create_dimensions(self) -> List[DimensionInfo]:
        dimensions = []

        # Create dimension objects for each dimension
        for i in range(self._dim_count):
            size = self._dim_sizes[i]
            start = self._axis_start[i]
            stop = self._axis_stop[i]
            dim_type = self._dim_types[i]

            # Determine if this is complex data
            is_complex = dim_type in [
                self.DIM_TYPE_COMPLEX,
                self.DIM_TYPE_TPPI,
                self.DIM_TYPE_REAL_COMPLEX,
            ]

            is_time_domain = False
            if self._unit_types[i] == self.SIUNIT_SECONDS:
                # Time domain if unit type is seconds with exponent 0 or 1
                if self._unit_exps[i] == 0 or self._unit_exps[i] == 1:
                    is_time_domain = True
            elif self._unit_types[i] == self.SIUNIT_HZ:
                # Hz can be both time and frequency domain, use additional
                # checks
                if i == 0:  # First dimension is more likely to be time domain
                    is_time_domain = True
                if start == 0.0:  # Time typically starts at 0
                    is_time_domain = True
            elif self._unit_types[i] == self.SIUNIT_PPM:
                # PPM is always frequency domain
                is_time_domain = False
            else:
                # Fallback for unknown unit types
                if i == 0:  # First dimension is usually time domain (F2)
                    is_time_domain = True
                if start == 0.0:  # Time typically starts at 0
                    is_time_domain = True
                if (
                    self._base_freq[i] != 0 and self._zero_point[i] != 0
                ):  # Has valid NMR parameters
                    is_time_domain = True

            # Determine unit based on domain type
            # Time domain data axis uses seconds, frequency domain uses ppm
            # Note: transmitter_offset is in Hz regardless of domain type
            unit = "s" if is_time_domain else "ppm"

            # Determine dimension name (F2, F1, F3, etc.) - F2 is first
            # dimension
            dim_name = f"F{self._dim_count - i}"

            # Calculate spectral width correctly based on domain type
            # For time domain: sw = n/t (where n is number of points, t is total time)
            # For frequency domain: sw = abs(stop - start)
            if is_time_domain:
                # Time domain: spectral width is inverse of time increment
                # This is the standard way to calculate spectral width in NMR
                total_time = stop - start
                spectral_width = size / total_time if total_time != 0 else 0.0
            else:
                # Frequency domain: use the axis difference directly
                spectral_width = abs(stop - start)

            # Calculate offset correctly based on domain type
            if is_time_domain:
                # For time domain data, use zero_point to calculate offset
                # (carrier frequency in Hz)
                offset = spectral_width * self._zero_point[i]

            else:
                # For frequency domain data, use axis_start directly
                offset = start

            # Calculate step size for linear axis
            step = (stop - start) / size if size > 0 else 0.0

            dim_info = DimensionInfo(
                size=size,
                is_complex=is_complex,
                spectral_width=spectral_width,
                observation_frequency=self._base_freq[
                    i
                ],  # Store base_freq as observation frequency in MHz
                unit=unit,
                transmitter_offset=offset,
                axis_generator=LinearGenerator(start=start, step=step),
                domain_type="time" if is_time_domain else "frequency",
                can_ft=is_time_domain,  # Can perform FT on time domain data
                domain_metadata={"name": dim_name, "dimension_type": dim_type},
            )

            dimensions.append(dim_info)

        return dimensions

    def _create_metadata(self) -> Dict[str, any]:
        metadata = {
            # Basic file information
            "source_format": "delta",
            "source_filename": self.filename,
            "endianness": self._byte_order,
            # Data structure information
            "dimension_count": self._dim_count,
            "data_type": self._data_type.__name__,  # Get numpy dtype name
            "data_start_offset": self._data_start,
            "data_length_bytes": self._data_length,
            # Dimension-specific information
            "dimension_types": self._dim_types[: self._dim_count],
            "dimension_sizes": self._dim_sizes[: self._dim_count],
            "axis_start_values": self._axis_start[: self._dim_count],
            "axis_stop_values": self._axis_stop[: self._dim_count],
            # NMR-specific parameters
            "base_frequencies": self._base_freq[: self._dim_count],
            "zero_points": self._zero_point[: self._dim_count],
        }

        return metadata

    def _delta_reshape(
            self,
            arr_1d: np.ndarray,
            target_shape: tuple) -> np.ndarray:
        dim_0_size, dim_1_size = target_shape

        return (
            arr_1d.reshape(
                dim_1_size // self.BLOCK_SIZE,
                dim_0_size // self.BLOCK_SIZE,
                self.BLOCK_SIZE,
                self.BLOCK_SIZE,
            )
            .transpose(1, 3, 0, 2)
            .reshape(dim_0_size, dim_1_size)
        )
