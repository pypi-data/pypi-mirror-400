from collections.abc import Sequence
from typing import overload


def library_version() -> str:
    """Get the mp4-rust library version"""

def estimate_maximum_moov_box_size(audio_sample_count: int, video_sample_count: int) -> int:
    """Estimate maximum moov box size"""

class Mp4SampleEntryAvc1:
    """
    H.264/AVC video sample entry.

    Contains codec configuration for AVC (Advanced Video Coding).
    """

    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, width: int, height: int, avc_profile_indication: int, avc_level_indication: int, profile_compatibility: int, sps_data: object | None = None, pps_data: object | None = None, length_size_minus_one: int = 3, chroma_format: int | None = None, bit_depth_luma_minus8: int | None = None, bit_depth_chroma_minus8: int | None = None) -> None: ...

    @property
    def width(self) -> int:
        """Video width in pixels"""

    @width.setter
    def width(self, arg: int, /) -> None: ...

    @property
    def height(self) -> int:
        """Video height in pixels"""

    @height.setter
    def height(self, arg: int, /) -> None: ...

    @property
    def avc_profile_indication(self) -> int:
        """AVC profile"""

    @avc_profile_indication.setter
    def avc_profile_indication(self, arg: int, /) -> None: ...

    @property
    def profile_compatibility(self) -> int:
        """Profile compatibility flags"""

    @profile_compatibility.setter
    def profile_compatibility(self, arg: int, /) -> None: ...

    @property
    def avc_level_indication(self) -> int:
        """AVC level"""

    @avc_level_indication.setter
    def avc_level_indication(self, arg: int, /) -> None: ...

    @property
    def length_size_minus_one(self) -> int:
        """NAL unit length field size minus 1"""

    @length_size_minus_one.setter
    def length_size_minus_one(self, arg: int, /) -> None: ...

    @property
    def sps_data(self) -> list[bytes]:
        """List of SPS (Sequence Parameter Set) data"""

    @sps_data.setter
    def sps_data(self, arg: Sequence[bytes], /) -> None: ...

    @property
    def pps_data(self) -> list[bytes]:
        """List of PPS (Picture Parameter Set) data"""

    @pps_data.setter
    def pps_data(self, arg: Sequence[bytes], /) -> None: ...

    @property
    def chroma_format(self) -> int | None:
        """Chroma format (optional)"""

    @chroma_format.setter
    def chroma_format(self, arg: int, /) -> None: ...

    @property
    def bit_depth_luma_minus8(self) -> int | None:
        """Luma bit depth minus 8 (optional)"""

    @bit_depth_luma_minus8.setter
    def bit_depth_luma_minus8(self, arg: int, /) -> None: ...

    @property
    def bit_depth_chroma_minus8(self) -> int | None:
        """Chroma bit depth minus 8 (optional)"""

    @bit_depth_chroma_minus8.setter
    def bit_depth_chroma_minus8(self, arg: int, /) -> None: ...

class Mp4SampleEntryHev1:
    """
    H.265/HEVC video sample entry (out-of-band parameters).

    Contains codec configuration for HEVC (High Efficiency Video Coding).
    VPS/SPS/PPS are stored in the sample entry.
    """

    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, width: int, height: int, general_profile_idc: int, general_level_idc: int, nalu_types: object | None = None, nalu_data: object | None = None, general_profile_space: int = 0, general_tier_flag: int = 0, general_profile_compatibility_flags: int = 0, general_constraint_indicator_flags: int = 0, chroma_format_idc: int = 1, bit_depth_luma_minus8: int = 0, bit_depth_chroma_minus8: int = 0, min_spatial_segmentation_idc: int = 0, parallelism_type: int = 0, avg_frame_rate: int = 0, constant_frame_rate: int = 0, num_temporal_layers: int = 0, temporal_id_nested: int = 0, length_size_minus_one: int = 3) -> None: ...

    @property
    def width(self) -> int:
        """Video width in pixels"""

    @width.setter
    def width(self, arg: int, /) -> None: ...

    @property
    def height(self) -> int:
        """Video height in pixels"""

    @height.setter
    def height(self, arg: int, /) -> None: ...

    @property
    def general_profile_space(self) -> int:
        """Profile space (0-3)"""

    @general_profile_space.setter
    def general_profile_space(self, arg: int, /) -> None: ...

    @property
    def general_tier_flag(self) -> int:
        """Tier flag (0=Main, 1=High)"""

    @general_tier_flag.setter
    def general_tier_flag(self, arg: int, /) -> None: ...

    @property
    def general_profile_idc(self) -> int:
        """Profile IDC"""

    @general_profile_idc.setter
    def general_profile_idc(self, arg: int, /) -> None: ...

    @property
    def general_profile_compatibility_flags(self) -> int:
        """Profile compatibility flags"""

    @general_profile_compatibility_flags.setter
    def general_profile_compatibility_flags(self, arg: int, /) -> None: ...

    @property
    def general_constraint_indicator_flags(self) -> int:
        """Constraint indicator flags"""

    @general_constraint_indicator_flags.setter
    def general_constraint_indicator_flags(self, arg: int, /) -> None: ...

    @property
    def general_level_idc(self) -> int:
        """Level IDC"""

    @general_level_idc.setter
    def general_level_idc(self, arg: int, /) -> None: ...

    @property
    def chroma_format_idc(self) -> int:
        """Chroma format IDC"""

    @chroma_format_idc.setter
    def chroma_format_idc(self, arg: int, /) -> None: ...

    @property
    def bit_depth_luma_minus8(self) -> int:
        """Luma bit depth minus 8"""

    @bit_depth_luma_minus8.setter
    def bit_depth_luma_minus8(self, arg: int, /) -> None: ...

    @property
    def bit_depth_chroma_minus8(self) -> int:
        """Chroma bit depth minus 8"""

    @bit_depth_chroma_minus8.setter
    def bit_depth_chroma_minus8(self, arg: int, /) -> None: ...

    @property
    def min_spatial_segmentation_idc(self) -> int:
        """Minimum spatial segmentation IDC"""

    @min_spatial_segmentation_idc.setter
    def min_spatial_segmentation_idc(self, arg: int, /) -> None: ...

    @property
    def parallelism_type(self) -> int:
        """Parallelism type"""

    @parallelism_type.setter
    def parallelism_type(self, arg: int, /) -> None: ...

    @property
    def avg_frame_rate(self) -> int:
        """Average frame rate"""

    @avg_frame_rate.setter
    def avg_frame_rate(self, arg: int, /) -> None: ...

    @property
    def constant_frame_rate(self) -> int:
        """Constant frame rate flag"""

    @constant_frame_rate.setter
    def constant_frame_rate(self, arg: int, /) -> None: ...

    @property
    def num_temporal_layers(self) -> int:
        """Number of temporal layers"""

    @num_temporal_layers.setter
    def num_temporal_layers(self, arg: int, /) -> None: ...

    @property
    def temporal_id_nested(self) -> int:
        """Temporal ID nested flag"""

    @temporal_id_nested.setter
    def temporal_id_nested(self, arg: int, /) -> None: ...

    @property
    def length_size_minus_one(self) -> int:
        """NAL unit length field size minus 1"""

    @length_size_minus_one.setter
    def length_size_minus_one(self, arg: int, /) -> None: ...

    @property
    def nalu_types(self) -> list[int]:
        """List of NAL unit types"""

    @nalu_types.setter
    def nalu_types(self, arg: Sequence[int], /) -> None: ...

    @property
    def nalu_data(self) -> list[bytes]:
        """List of NAL unit data"""

    @nalu_data.setter
    def nalu_data(self, arg: Sequence[bytes], /) -> None: ...

class Mp4SampleEntryHvc1:
    """
    H.265/HEVC video sample entry (in-band parameters).

    Contains codec configuration for HEVC (High Efficiency Video Coding).
    VPS/SPS/PPS are stored in the sample stream.
    """

    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, width: int, height: int, general_profile_idc: int, general_level_idc: int, nalu_types: object | None = None, nalu_data: object | None = None, general_profile_space: int = 0, general_tier_flag: int = 0, general_profile_compatibility_flags: int = 0, general_constraint_indicator_flags: int = 0, chroma_format_idc: int = 1, bit_depth_luma_minus8: int = 0, bit_depth_chroma_minus8: int = 0, min_spatial_segmentation_idc: int = 0, parallelism_type: int = 0, avg_frame_rate: int = 0, constant_frame_rate: int = 0, num_temporal_layers: int = 0, temporal_id_nested: int = 0, length_size_minus_one: int = 3) -> None: ...

    @property
    def width(self) -> int:
        """Video width in pixels"""

    @width.setter
    def width(self, arg: int, /) -> None: ...

    @property
    def height(self) -> int:
        """Video height in pixels"""

    @height.setter
    def height(self, arg: int, /) -> None: ...

    @property
    def general_profile_space(self) -> int:
        """Profile space (0-3)"""

    @general_profile_space.setter
    def general_profile_space(self, arg: int, /) -> None: ...

    @property
    def general_tier_flag(self) -> int:
        """Tier flag (0=Main, 1=High)"""

    @general_tier_flag.setter
    def general_tier_flag(self, arg: int, /) -> None: ...

    @property
    def general_profile_idc(self) -> int:
        """Profile IDC (1=Main, 2=Main10, 3=Main Still Picture)"""

    @general_profile_idc.setter
    def general_profile_idc(self, arg: int, /) -> None: ...

    @property
    def general_profile_compatibility_flags(self) -> int:
        """Profile compatibility flags (32-bit)"""

    @general_profile_compatibility_flags.setter
    def general_profile_compatibility_flags(self, arg: int, /) -> None: ...

    @property
    def general_constraint_indicator_flags(self) -> int:
        """Constraint indicator flags (48-bit)"""

    @general_constraint_indicator_flags.setter
    def general_constraint_indicator_flags(self, arg: int, /) -> None: ...

    @property
    def general_level_idc(self) -> int:
        """Level IDC (30x value, e.g., 93 = Level 3.1)"""

    @general_level_idc.setter
    def general_level_idc(self, arg: int, /) -> None: ...

    @property
    def chroma_format_idc(self) -> int:
        """Chroma format (0=monochrome, 1=4:2:0, 2=4:2:2, 3=4:4:4)"""

    @chroma_format_idc.setter
    def chroma_format_idc(self, arg: int, /) -> None: ...

    @property
    def bit_depth_luma_minus8(self) -> int:
        """Luma bit depth minus 8"""

    @bit_depth_luma_minus8.setter
    def bit_depth_luma_minus8(self, arg: int, /) -> None: ...

    @property
    def bit_depth_chroma_minus8(self) -> int:
        """Chroma bit depth minus 8"""

    @bit_depth_chroma_minus8.setter
    def bit_depth_chroma_minus8(self, arg: int, /) -> None: ...

    @property
    def min_spatial_segmentation_idc(self) -> int:
        """Minimum spatial segmentation IDC"""

    @min_spatial_segmentation_idc.setter
    def min_spatial_segmentation_idc(self, arg: int, /) -> None: ...

    @property
    def parallelism_type(self) -> int:
        """Parallelism type"""

    @parallelism_type.setter
    def parallelism_type(self, arg: int, /) -> None: ...

    @property
    def avg_frame_rate(self) -> int:
        """Average frame rate"""

    @avg_frame_rate.setter
    def avg_frame_rate(self, arg: int, /) -> None: ...

    @property
    def constant_frame_rate(self) -> int:
        """Constant frame rate flag"""

    @constant_frame_rate.setter
    def constant_frame_rate(self, arg: int, /) -> None: ...

    @property
    def num_temporal_layers(self) -> int:
        """Number of temporal layers"""

    @num_temporal_layers.setter
    def num_temporal_layers(self, arg: int, /) -> None: ...

    @property
    def temporal_id_nested(self) -> int:
        """Temporal ID nested flag"""

    @temporal_id_nested.setter
    def temporal_id_nested(self, arg: int, /) -> None: ...

    @property
    def length_size_minus_one(self) -> int:
        """NAL unit length field size minus 1 (usually 3 = 4 bytes)"""

    @length_size_minus_one.setter
    def length_size_minus_one(self, arg: int, /) -> None: ...

    @property
    def nalu_types(self) -> list[int]:
        """List of VPS/SPS/PPS NAL unit types"""

    @nalu_types.setter
    def nalu_types(self, arg: Sequence[int], /) -> None: ...

    @property
    def nalu_data(self) -> list[bytes]:
        """List of VPS/SPS/PPS NAL unit data"""

    @nalu_data.setter
    def nalu_data(self, arg: Sequence[bytes], /) -> None: ...

class Mp4SampleEntryVp08:
    """
    VP8 video sample entry.

    Contains codec configuration for VP8.
    """

    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, width: int, height: int, bit_depth: int = 8, chroma_subsampling: int = 0, video_full_range_flag: bool = False, colour_primaries: int = 1, transfer_characteristics: int = 1, matrix_coefficients: int = 1) -> None: ...

    @property
    def width(self) -> int:
        """Video width in pixels"""

    @width.setter
    def width(self, arg: int, /) -> None: ...

    @property
    def height(self) -> int:
        """Video height in pixels"""

    @height.setter
    def height(self, arg: int, /) -> None: ...

    @property
    def bit_depth(self) -> int:
        """Bit depth (usually 8)"""

    @bit_depth.setter
    def bit_depth(self, arg: int, /) -> None: ...

    @property
    def chroma_subsampling(self) -> int:
        """Chroma subsampling (0=4:2:0 vertical, 1=4:2:0 colocated)"""

    @chroma_subsampling.setter
    def chroma_subsampling(self, arg: int, /) -> None: ...

    @property
    def video_full_range_flag(self) -> bool:
        """Full range flag (True=0-255, False=16-235)"""

    @video_full_range_flag.setter
    def video_full_range_flag(self, arg: bool, /) -> None: ...

    @property
    def colour_primaries(self) -> int:
        """Color primaries (ITU-T H.273, 1=BT.709)"""

    @colour_primaries.setter
    def colour_primaries(self, arg: int, /) -> None: ...

    @property
    def transfer_characteristics(self) -> int:
        """Transfer characteristics (ITU-T H.273, 1=BT.709)"""

    @transfer_characteristics.setter
    def transfer_characteristics(self, arg: int, /) -> None: ...

    @property
    def matrix_coefficients(self) -> int:
        """Matrix coefficients (ITU-T H.273, 1=BT.709)"""

    @matrix_coefficients.setter
    def matrix_coefficients(self, arg: int, /) -> None: ...

class Mp4SampleEntryVp09:
    """
    VP9 video sample entry.

    Contains codec configuration for VP9.
    """

    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, width: int, height: int, profile: int, level: int, bit_depth: int = 8, chroma_subsampling: int = 0, video_full_range_flag: bool = False, colour_primaries: int = 1, transfer_characteristics: int = 1, matrix_coefficients: int = 1) -> None: ...

    @property
    def width(self) -> int:
        """Video width in pixels"""

    @width.setter
    def width(self, arg: int, /) -> None: ...

    @property
    def height(self) -> int:
        """Video height in pixels"""

    @height.setter
    def height(self, arg: int, /) -> None: ...

    @property
    def profile(self) -> int:
        """Profile (0=Profile 0, 1=Profile 1, 2=Profile 2, 3=Profile 3)"""

    @profile.setter
    def profile(self, arg: int, /) -> None: ...

    @property
    def level(self) -> int:
        """Level (10=Level 1.0, 51=Level 5.1, etc.)"""

    @level.setter
    def level(self, arg: int, /) -> None: ...

    @property
    def bit_depth(self) -> int:
        """Bit depth (8, 10, 12)"""

    @bit_depth.setter
    def bit_depth(self, arg: int, /) -> None: ...

    @property
    def chroma_subsampling(self) -> int:
        """
        Chroma subsampling (0=4:2:0 vertical, 1=4:2:0 colocated, 2=4:2:2, 3=4:4:4)
        """

    @chroma_subsampling.setter
    def chroma_subsampling(self, arg: int, /) -> None: ...

    @property
    def video_full_range_flag(self) -> bool:
        """Full range flag (True=0-255, False=16-235)"""

    @video_full_range_flag.setter
    def video_full_range_flag(self, arg: bool, /) -> None: ...

    @property
    def colour_primaries(self) -> int:
        """Color primaries (ITU-T H.273, 1=BT.709)"""

    @colour_primaries.setter
    def colour_primaries(self, arg: int, /) -> None: ...

    @property
    def transfer_characteristics(self) -> int:
        """Transfer characteristics (ITU-T H.273, 1=BT.709)"""

    @transfer_characteristics.setter
    def transfer_characteristics(self, arg: int, /) -> None: ...

    @property
    def matrix_coefficients(self) -> int:
        """Matrix coefficients (ITU-T H.273, 1=BT.709)"""

    @matrix_coefficients.setter
    def matrix_coefficients(self, arg: int, /) -> None: ...

class Mp4SampleEntryAv01:
    """
    AV1 video sample entry.

    Contains codec configuration for AV1 (AOMedia Video 1).
    """

    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, width: int, height: int, seq_profile: int, seq_level_idx_0: int, config_obus: bytes, seq_tier_0: int = 0, high_bitdepth: int = 0, twelve_bit: int = 0, monochrome: int = 0, chroma_subsampling_x: int = 1, chroma_subsampling_y: int = 1, chroma_sample_position: int = 0, initial_presentation_delay_present: bool = False, initial_presentation_delay_minus_one: int = 0) -> None: ...

    @property
    def width(self) -> int:
        """Video width in pixels"""

    @width.setter
    def width(self, arg: int, /) -> None: ...

    @property
    def height(self) -> int:
        """Video height in pixels"""

    @height.setter
    def height(self, arg: int, /) -> None: ...

    @property
    def seq_profile(self) -> int:
        """Sequence profile (0=Main, 1=High, 2=Professional)"""

    @seq_profile.setter
    def seq_profile(self, arg: int, /) -> None: ...

    @property
    def seq_level_idx_0(self) -> int:
        """Sequence level index"""

    @seq_level_idx_0.setter
    def seq_level_idx_0(self, arg: int, /) -> None: ...

    @property
    def seq_tier_0(self) -> int:
        """Sequence tier (0=Main, 1=High)"""

    @seq_tier_0.setter
    def seq_tier_0(self, arg: int, /) -> None: ...

    @property
    def high_bitdepth(self) -> int:
        """High bit depth flag (1=10-bit or higher)"""

    @high_bitdepth.setter
    def high_bitdepth(self, arg: int, /) -> None: ...

    @property
    def twelve_bit(self) -> int:
        """12-bit flag"""

    @twelve_bit.setter
    def twelve_bit(self, arg: int, /) -> None: ...

    @property
    def monochrome(self) -> int:
        """Monochrome flag"""

    @monochrome.setter
    def monochrome(self, arg: int, /) -> None: ...

    @property
    def chroma_subsampling_x(self) -> int:
        """Horizontal chroma subsampling"""

    @chroma_subsampling_x.setter
    def chroma_subsampling_x(self, arg: int, /) -> None: ...

    @property
    def chroma_subsampling_y(self) -> int:
        """Vertical chroma subsampling"""

    @chroma_subsampling_y.setter
    def chroma_subsampling_y(self, arg: int, /) -> None: ...

    @property
    def chroma_sample_position(self) -> int:
        """Chroma sample position (0=unknown, 1=vertical, 2=colocated)"""

    @chroma_sample_position.setter
    def chroma_sample_position(self, arg: int, /) -> None: ...

    @property
    def initial_presentation_delay_present(self) -> bool:
        """Whether initial presentation delay is present"""

    @initial_presentation_delay_present.setter
    def initial_presentation_delay_present(self, arg: bool, /) -> None: ...

    @property
    def initial_presentation_delay_minus_one(self) -> int:
        """Initial presentation delay minus 1"""

    @initial_presentation_delay_minus_one.setter
    def initial_presentation_delay_minus_one(self, arg: int, /) -> None: ...

    @property
    def config_obus(self) -> bytes:
        """Configuration OBUs (e.g., Sequence Header)"""

    @config_obus.setter
    def config_obus(self, arg: bytes, /) -> None: ...

class Mp4SampleEntryOpus:
    """
    Opus audio sample entry.

    Contains codec configuration for Opus.
    """

    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, channel_count: int, sample_rate: int, sample_size: int = 16, pre_skip: int = 0, input_sample_rate: int | None = None, output_gain: int = 0) -> None: ...

    @property
    def channel_count(self) -> int:
        """Number of channels"""

    @channel_count.setter
    def channel_count(self, arg: int, /) -> None: ...

    @property
    def sample_rate(self) -> int:
        """Sample rate (Hz)"""

    @sample_rate.setter
    def sample_rate(self, arg: int, /) -> None: ...

    @property
    def sample_size(self) -> int:
        """Sample size (bits)"""

    @sample_size.setter
    def sample_size(self, arg: int, /) -> None: ...

    @property
    def pre_skip(self) -> int:
        """Pre-skip sample count"""

    @pre_skip.setter
    def pre_skip(self, arg: int, /) -> None: ...

    @property
    def input_sample_rate(self) -> int | None:
        """Input sample rate (Hz, None if same as sample_rate)"""

    @input_sample_rate.setter
    def input_sample_rate(self, arg: int, /) -> None: ...

    @property
    def output_gain(self) -> int:
        """Output gain (dB * 256)"""

    @output_gain.setter
    def output_gain(self, arg: int, /) -> None: ...

class Mp4SampleEntryMp4a:
    """
    AAC audio sample entry.

    Contains codec configuration for AAC (MPEG-4 Audio).
    """

    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, channel_count: int, sample_rate: int, dec_specific_info: bytes, sample_size: int = 16, buffer_size_db: int = 0, max_bitrate: int = 0, avg_bitrate: int = 0) -> None: ...

    @property
    def channel_count(self) -> int:
        """Number of channels"""

    @channel_count.setter
    def channel_count(self, arg: int, /) -> None: ...

    @property
    def sample_rate(self) -> int:
        """Sample rate (Hz)"""

    @sample_rate.setter
    def sample_rate(self, arg: int, /) -> None: ...

    @property
    def sample_size(self) -> int:
        """Sample size (bits)"""

    @sample_size.setter
    def sample_size(self, arg: int, /) -> None: ...

    @property
    def buffer_size_db(self) -> int:
        """Buffer size DB"""

    @buffer_size_db.setter
    def buffer_size_db(self, arg: int, /) -> None: ...

    @property
    def max_bitrate(self) -> int:
        """Maximum bitrate (bps)"""

    @max_bitrate.setter
    def max_bitrate(self, arg: int, /) -> None: ...

    @property
    def avg_bitrate(self) -> int:
        """Average bitrate (bps)"""

    @avg_bitrate.setter
    def avg_bitrate(self, arg: int, /) -> None: ...

    @property
    def dec_specific_info(self) -> bytes:
        """Decoder specific info (AudioSpecificConfig)"""

    @dec_specific_info.setter
    def dec_specific_info(self, arg: bytes, /) -> None: ...

class Mp4SampleEntryFlac:
    """
    FLAC audio sample entry.

    Contains codec configuration for FLAC.
    """

    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, channel_count: int, sample_rate: int, streaminfo_data: bytes, sample_size: int = 16) -> None: ...

    @property
    def channel_count(self) -> int:
        """Number of channels"""

    @channel_count.setter
    def channel_count(self, arg: int, /) -> None: ...

    @property
    def sample_rate(self) -> int:
        """Sample rate (Hz)"""

    @sample_rate.setter
    def sample_rate(self, arg: int, /) -> None: ...

    @property
    def sample_size(self) -> int:
        """Sample size (bits)"""

    @sample_size.setter
    def sample_size(self, arg: int, /) -> None: ...

    @property
    def streaminfo_data(self) -> bytes:
        """FLAC STREAMINFO metadata block"""

    @streaminfo_data.setter
    def streaminfo_data(self, arg: bytes, /) -> None: ...

class Mp4TrackInfo:
    """
    MP4 track information.

    Contains track ID, kind (audio/video), duration, and timescale.
    """

    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, track_id: int, kind: str, duration: int, timescale: int) -> None: ...

    @property
    def track_id(self) -> int:
        """Track ID"""

    @track_id.setter
    def track_id(self, arg: int, /) -> None: ...

    @property
    def kind(self) -> str:
        """Track kind ('audio' or 'video')"""

    @kind.setter
    def kind(self, arg: str, /) -> None: ...

    @property
    def duration(self) -> int:
        """Duration in timescale units"""

    @duration.setter
    def duration(self, arg: int, /) -> None: ...

    @property
    def timescale(self) -> int:
        """Timescale (units per second)"""

    @timescale.setter
    def timescale(self, arg: int, /) -> None: ...

    @property
    def duration_seconds(self) -> float:
        """Duration in seconds"""

    def __repr__(self) -> str: ...

class Mp4DemuxSample:
    """
    Sample retrieved from a demultiplexer.

    Contains track information, timestamp, and data.
    The data property is lazily loaded from the file on access.
    """

    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, track: Mp4TrackInfo, sample_entry: object, keyframe: bool, timestamp: int, duration: int, data_offset: int, data_size: int, input_stream: object) -> None: ...

    @property
    def track(self) -> Mp4TrackInfo:
        """Track information for this sample"""

    @property
    def sample_entry(self) -> object:
        """Sample entry (codec configuration)"""

    @property
    def keyframe(self) -> bool:
        """Whether this is a keyframe"""

    @property
    def timestamp(self) -> int:
        """Timestamp in timescale units"""

    @property
    def duration(self) -> int:
        """Duration in timescale units"""

    @property
    def data(self) -> bytes:
        """Sample data (bytes)"""

    @property
    def timestamp_seconds(self) -> float:
        """Timestamp in seconds"""

    @property
    def duration_seconds(self) -> float:
        """Duration in seconds"""

    def __repr__(self) -> str: ...

class Mp4FileDemuxer:
    """
    Demultiplexer for reading MP4 files.

    Reads MP4 data from a file path or file-like object and allows
    iteration over samples. Supports the context manager protocol.

    Example:
        with Mp4FileDemuxer('input.mp4') as demuxer:
            for sample in demuxer:
                print(sample.track.kind, sample.timestamp)
    """

    def __init__(self, source: object) -> None:
        """
        Create a demultiplexer.

        Args:
            source: File path (str/Path) or file-like object
        """

    def close(self) -> None:
        """Close the demultiplexer and release resources"""

    @property
    def tracks(self) -> list[Mp4TrackInfo]:
        """List of track information in the MP4 file"""

    def __enter__(self) -> Mp4FileDemuxer: ...

    def __exit__(self, exc_type: object | None, exc_val: object | None, exc_tb: object | None) -> None: ...

    def __iter__(self) -> Mp4FileDemuxer: ...

    def __next__(self) -> Mp4DemuxSample: ...

class Mp4FileMuxerOptions:
    """
    Multiplexer options.

    Allows reserving moov box size for streaming output.
    """

    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, reserved_moov_box_size: int = 0) -> None: ...

    @property
    def reserved_moov_box_size(self) -> int:
        """Reserved moov box size in bytes"""

    @reserved_moov_box_size.setter
    def reserved_moov_box_size(self, arg: int, /) -> None: ...

    @staticmethod
    def estimate_maximum_moov_box_size(audio_sample_count: int, video_sample_count: int) -> int:
        """
        Estimate maximum moov box size.

        Args:
            audio_sample_count: Number of audio samples
            video_sample_count: Number of video samples

        Returns:
            Estimated size in bytes
        """

class Mp4MuxSample:
    """
    Sample to add to the multiplexer.

    Specifies track kind, codec configuration, timestamp, and data.
    """

    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, track_kind: str, sample_entry: object, keyframe: bool, timescale: int, duration: int, data: bytes) -> None: ...

    @property
    def track_kind(self) -> str:
        """Track kind ('audio' or 'video')"""

    @track_kind.setter
    def track_kind(self, arg: str, /) -> None: ...

    @property
    def sample_entry(self) -> object:
        """Sample entry (codec configuration)"""

    @sample_entry.setter
    def sample_entry(self, arg: object, /) -> None: ...

    @property
    def keyframe(self) -> bool:
        """Whether this is a keyframe"""

    @keyframe.setter
    def keyframe(self, arg: bool, /) -> None: ...

    @property
    def timescale(self) -> int:
        """Timescale (units per second)"""

    @timescale.setter
    def timescale(self, arg: int, /) -> None: ...

    @property
    def duration(self) -> int:
        """Duration in timescale units"""

    @duration.setter
    def duration(self, arg: int, /) -> None: ...

    @property
    def data(self) -> bytes:
        """Sample data (bytes)"""

    @data.setter
    def data(self, arg: bytes, /) -> None: ...

    def __repr__(self) -> str: ...

class Mp4FileMuxer:
    """
    Multiplexer for writing MP4 files.

    Appends samples to create an MP4 file. Supports the context manager
    protocol. finalize() is called automatically when exiting a with block.

    Example:
        with Mp4FileMuxer('output.mp4') as muxer:
            muxer.append_sample(sample)
    """

    def __init__(self, destination: object, options: Mp4FileMuxerOptions | None = None) -> None:
        """
        Create a multiplexer.

        Args:
            destination: Output file path (str/Path) or file-like object
            options: Multiplexer options (optional)
        """

    def close(self) -> None:
        """Close the multiplexer and release resources"""

    def append_sample(self, sample: Mp4MuxSample) -> None:
        """
        Append a sample.

        Args:
            sample: Sample to append (Mp4MuxSample)
        """

    def finalize(self) -> None:
        """
        Finalize the MP4 file.

        Writes the moov box to complete the MP4 file.
        Called automatically when using a with statement.
        """

    def __enter__(self) -> Mp4FileMuxer: ...

    def __exit__(self, exc_type: object | None, exc_val: object | None, exc_tb: object | None) -> None: ...
