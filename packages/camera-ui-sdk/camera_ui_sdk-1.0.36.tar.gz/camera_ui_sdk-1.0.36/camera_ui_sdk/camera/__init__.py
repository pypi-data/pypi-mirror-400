from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Literal, NotRequired, Protocol, TypedDict, runtime_checkable

if TYPE_CHECKING:
    from PIL.Image import Image as PILImageType

    from ..observable import HybridObservable
    from ..sensor.base import Sensor, SensorLike, SensorType
    from ..service.base import Service, ServiceType
    from ..types import LoggerService

from ..sensor import BaseDetectionLabel, DetectionLabel

CameraType = Literal["camera", "doorbell"]
"""
Camera device type.
- `camera`: Standard surveillance camera
- `doorbell`: Doorbell camera
"""

ZoneType = Literal["intersect", "contain"]
"""
Detection zone intersection type.
- `intersect`: Trigger when object touches the zone boundary
- `contain`: Trigger only when object is fully inside the zone
"""

ZoneFilter = Literal["include", "exclude"]
"""
Detection zone filter mode.
- `include`: Only consider detections inside this zone
- `exclude`: Only consider detections outside this zone
"""

CameraRole = Literal["high-resolution", "mid-resolution", "low-resolution", "snapshot"]
"""
Camera stream resolution role.
Used to identify different quality streams from the same camera.
"""

StreamingRole = Literal["high-resolution", "mid-resolution", "low-resolution"]
"""Streaming roles (excludes snapshot)."""

DecoderFormat = Literal["nv12"]
"""Internal decoder output format."""

ImageInputFormat = Literal["nv12", "rgb", "rgba", "gray"]
"""Supported image input formats for processing."""

ImageOutputFormat = Literal["rgb", "rgba", "gray"]
"""Supported image output formats after processing."""

CameraFrameWorkerDecoder = Literal["wasm", "rust"]
"""Frame worker decoder implementation."""

MotionResolution = Literal["low", "medium", "high"]
"""
Motion detection resolution setting.
Higher resolution = more accurate but slower.
"""

AudioCodec = Literal[
    "PCMU", "PCMA", "MPEG4-GENERIC", "opus", "G722", "MPA", "PCM", "FLAC", "ELD", "PCML", "L16"
]
"""Supported audio codecs (RTP/SDP format names)."""

AudioFFmpegCodec = Literal[
    "pcm_mulaw", "pcm_alaw", "aac", "libopus", "g722", "mp3", "pcm_s16be", "pcm_s16le", "flac"
]
"""FFmpeg audio codec names for transcoding."""

VideoCodec = Literal["H264", "H265", "VP8", "VP9", "AV1", "JPEG", "RAW"]
"""Supported video codecs (RTP/SDP format names)."""

VideoFFmpegCodec = Literal["h264", "hevc", "vp8", "vp9", "av1", "mjpeg", "rawvideo"]
"""FFmpeg video codec names for transcoding."""

RTSPAudioCodec = Literal["aac", "opus", "pcma"]
"""Audio codecs supported for RTSP streaming."""

ProbeAudioCodec = Literal["aac", "opus", "pcma"]
"""Audio codecs supported for stream probing."""

VideoStreamingMode = Literal["auto", "webrtc", "mse", "webrtc/tcp"]
"""
Video streaming mode for UI playback.
- `auto`: Automatically select best method
- `webrtc`: WebRTC with UDP (lowest latency)
- `webrtc/tcp`: WebRTC with TCP fallback
- `mse`: Media Source Extensions (browser native)
"""

CameraAspectRatio = Literal["16:9", "8:3", "4:3", "auto"]
"""Camera aspect ratio for UI display."""

FrameType = Literal["stream", "motion"]
"""Frame type identifier for frame workers."""

Point = tuple[float, float]
"""Zone polygon coordinate as (x, y) tuple (0-100 percentage)."""


class FrameMetadata(TypedDict):
    """Decoded frame metadata from the video decoder."""

    format: DecoderFormat
    """Decoder format."""
    frameSize: int
    """Total frame data size in bytes."""
    width: int
    """Current frame width (may be scaled)."""
    height: int
    """Current frame height (may be scaled)."""
    origWidth: int
    """Original video width before scaling."""
    origHeight: int
    """Original video height before scaling."""


class ImageInformation(TypedDict):
    """Image dimension and format information."""

    width: int
    """Image width in pixels."""
    height: int
    """Image height in pixels."""
    channels: int
    """Number of color channels (1=gray, 3=RGB, 4=RGBA)."""
    format: ImageInputFormat
    """Pixel format."""


class ImageCrop(TypedDict):
    """Crop region for image processing."""

    top: int
    """Top offset in pixels."""
    left: int
    """Left offset in pixels."""
    width: int
    """Crop width in pixels."""
    height: int
    """Crop height in pixels."""


class ImageResize(TypedDict):
    """Resize dimensions for image processing."""

    width: int
    """Target width in pixels."""
    height: int
    """Target height in pixels."""


class ImageFormat(TypedDict):
    """Output format conversion option."""

    to: ImageOutputFormat
    """Target pixel format."""


class ImageOptions(TypedDict, total=False):
    """Combined image processing options."""

    format: ImageFormat
    """Output format conversion."""
    crop: ImageCrop
    """Crop region."""
    resize: ImageResize
    """Resize dimensions."""


class FrameImage(TypedDict):
    """Processed image with PIL Image instance."""

    image: PILImageType
    """PIL Image instance for further processing."""
    info: ImageInformation
    """Image information."""


class FrameBuffer(TypedDict):
    """Processed image as raw buffer."""

    image: bytes
    """Raw pixel data."""
    info: ImageInformation
    """Image information."""


class FrameData(TypedDict):
    """Raw frame data from decoder."""

    id: str
    """Unique frame identifier."""
    data: bytes
    """Raw frame pixel data."""
    timestamp: int
    """Frame capture timestamp."""
    metadata: FrameMetadata
    """Decoder metadata."""
    info: ImageInformation
    """Image information."""


class VideoFrame(Protocol):
    """
    Video frame with processing capabilities.
    Provides methods to convert raw decoder output to usable image formats.
    """

    @property
    def id(self) -> str:
        """Unique frame identifier."""
        ...

    @property
    def data(self) -> bytes:
        """Raw frame pixel data."""
        ...

    @property
    def metadata(self) -> FrameMetadata:
        """Decoder metadata."""
        ...

    @property
    def info(self) -> ImageInformation:
        """Image information."""
        ...

    @property
    def timestamp(self) -> int:
        """Frame capture timestamp."""
        ...

    @property
    def inputWidth(self) -> int:
        """Original video width."""
        ...

    @property
    def inputHeight(self) -> int:
        """Original video height."""
        ...

    @property
    def inputFormat(self) -> DecoderFormat:
        """Decoder output format."""
        ...

    async def toBuffer(self) -> FrameBuffer:
        """
        Convert frame to raw pixel buffer.

        Returns:
            Processed image buffer with metadata.
        """
        ...

    async def toImage(self) -> FrameImage:
        """
        Convert frame to PIL image instance.

        Returns:
            PIL image for further processing.
        """
        ...


class Go2RtcWSSource(TypedDict):
    """WebSocket streaming URLs from go2rtc."""

    webrtc: str
    """WebRTC signaling endpoint."""
    mse: str
    """MSE streaming endpoint."""


class Go2RtcRTSPSource(TypedDict):
    """RTSP streaming URLs from go2rtc."""

    base: str
    """Base RTSP URL."""
    default: str
    """Default stream (video + audio)."""
    muted: str
    """Video only (muted)."""
    aac: str
    """Stream with AAC audio URL."""
    opus: str
    """Stream with Opus audio URL."""
    pcma: str
    """Stream with PCMA audio URL."""
    onvif: str
    """ONVIF URL."""
    prebuffered: str
    """Prebuffered stream URL."""


class Go2RtcSnapshotSource(TypedDict):
    """Snapshot/image URLs from go2rtc."""

    mp4: str
    """MP4 single-frame video URL."""
    jpeg: str
    """JPEG snapshot URL."""
    mjpeg: str
    """MJPEG stream URL."""


class StreamUrls(TypedDict):
    """Collection of all streaming URLs for a camera source."""

    ws: Go2RtcWSSource
    """WebSocket URLs."""
    rtsp: Go2RtcRTSPSource
    """RTSP URLs."""
    snapshot: Go2RtcSnapshotSource
    """Snapshot URLs."""


class ProbeConfig(TypedDict, total=False):
    """Configuration for stream probing."""

    video: bool
    """Include video track info."""
    audio: bool | Literal["all"] | list[ProbeAudioCodec]
    """Include audio track info (true, 'all', or specific codecs)."""
    microphone: bool
    """Include microphone/backchannel info."""


class FMTPInfo(TypedDict):
    """Format parameters (fmtp) from SDP."""

    payload: int
    """RTP payload type number."""
    config: str
    """Codec-specific configuration string."""


class AudioCodecProperties(TypedDict):
    """Audio codec properties from stream probe."""

    sampleRate: int
    """Audio sample rate in Hz."""
    channels: int
    """Number of audio channels."""
    payloadType: int
    """RTP payload type."""
    fmtpInfo: NotRequired[FMTPInfo]
    """Optional format parameters."""


class VideoCodecProperties(TypedDict):
    """Video codec properties from stream probe."""

    clockRate: int
    """Video clock rate."""
    payloadType: int
    """RTP payload type."""
    fmtpInfo: NotRequired[FMTPInfo]
    """Optional format parameters."""


class AudioStreamInfo(TypedDict):
    """Audio stream information from probe."""

    codec: AudioCodec
    """Audio codec."""
    ffmpegCodec: AudioFFmpegCodec
    """FFmpeg codec name."""
    properties: AudioCodecProperties
    """Codec properties."""
    direction: Literal["sendonly", "recvonly", "sendrecv", "inactive"]
    """Stream direction."""


class VideoStreamInfo(TypedDict):
    """Video stream information from probe."""

    codec: VideoCodec
    """Video codec."""
    ffmpegCodec: VideoFFmpegCodec
    """FFmpeg codec name."""
    properties: VideoCodecProperties
    """Codec properties."""
    direction: Literal["sendonly", "recvonly", "sendrecv", "inactive"]
    """Stream direction."""


class ProbeStream(TypedDict):
    """Stream probe result containing SDP and track information."""

    sdp: str
    """Raw SDP string."""
    audio: list[AudioStreamInfo]
    """Available audio tracks."""
    video: list[VideoStreamInfo]
    """Available video tracks."""


class RTSPUrlOptions(TypedDict, total=False):
    """Options for generating RTSP URLs."""

    video: bool
    """Include video track."""
    audio: bool | RTSPAudioCodec | list[RTSPAudioCodec]
    """Include audio track(s)."""
    gop: bool
    """Request keyframe at start (GOP)."""
    prebuffer: bool
    """Use prebuffered stream."""
    audioSingleTrack: bool
    """Combine audio tracks into single track."""
    backchannel: bool
    """Enable backchannel (two-way audio)."""
    timeout: int
    """Connection timeout in ms."""


class IceServer(TypedDict):
    """WebRTC ICE server configuration."""

    urls: list[str]
    """STUN/TURN server URLs."""
    username: NotRequired[str]
    """Authentication username."""
    credential: NotRequired[str]
    """Authentication credential."""


class PluginLabels(TypedDict):
    """Plugin-provided detection labels."""

    sensorId: str
    """Sensor ID providing the labels."""
    sensorName: str
    """Sensor display name."""
    pluginId: str
    """Plugin ID."""
    labels: list[str]
    """Available labels from this sensor."""


class AvailableLabels(TypedDict):
    """All available detection labels for a camera."""

    base: tuple[BaseDetectionLabel, ...]
    """Built-in base labels."""
    plugins: list[PluginLabels]
    """Plugin-provided labels by sensor."""
    all: list[str]
    """Combined list of all available labels."""


class DetectionZone(TypedDict):
    """
    Detection zone configuration.
    Defines areas for detection filtering or privacy masking.
    """

    name: str
    """Zone display name."""
    points: list[Point]
    """Polygon points (0-100 percentage coordinates)."""
    type: ZoneType
    """Intersection detection type."""
    filter: ZoneFilter
    """Include/exclude filter mode."""
    labels: list[DetectionLabel]
    """Labels to filter (empty = all labels)."""
    isPrivacyMask: bool
    """Whether this is a privacy mask (blur/block area)."""
    color: str
    """Zone display color (hex)."""


class MotionDetectionSettings(TypedDict):
    """Motion detection settings."""

    timeout: int
    """Cooldown timeout after motion ends (seconds)."""
    resolution: MotionResolution
    """Detection resolution quality."""


class ObjectDetectionSettings(TypedDict):
    """Object detection settings."""

    confidence: float
    """Minimum confidence threshold (0-1)."""
    timeout: int
    """Cooldown timeout after detection ends (seconds)."""


class CameraDetectionSettings(TypedDict):
    """Combined detection settings for a camera."""

    motion: MotionDetectionSettings
    """Motion detection settings."""
    object: ObjectDetectionSettings
    """Object detection settings."""


class CameraInformation(TypedDict, total=False):
    """Camera hardware/firmware information."""

    model: str
    """Camera model name."""
    manufacturer: str
    """Manufacturer name."""
    hardware: str
    """Hardware version/revision."""
    serialNumber: str
    """Device serial number."""
    firmwareVersion: str
    """Current firmware version."""
    supportUrl: str
    """Manufacturer support URL."""


class CameraFrameWorkerSettings(TypedDict):
    """Frame worker (decoder) settings."""

    fps: int
    """Target frames per second for detection."""


class CameraInput(TypedDict):
    """Camera video input/source with resolved URLs."""

    _id: str
    """Unique source ID."""
    name: str
    """Source display name."""
    role: CameraRole
    """Resolution role."""
    useForSnapshot: bool
    """Use this source for snapshots."""
    hotMode: bool
    """Keep connection always active."""
    preload: bool
    """Preload stream on startup."""
    prebuffer: bool
    """Enable stream prebuffering."""
    urls: StreamUrls
    """Generated streaming URLs."""
    childSourceId: str | None
    """Child source ID (for snapshot fallback)."""


class CameraInputSettings(TypedDict):
    """Camera input settings (user configuration)."""

    _id: str
    """Unique source ID."""
    name: str
    """Source display name."""
    role: CameraRole
    """Resolution role."""
    useForSnapshot: bool
    """Use this source for snapshots."""
    hotMode: bool
    """Keep connection always active."""
    preload: bool
    """Preload stream on startup."""
    prebuffer: bool
    """Enable stream prebuffering."""
    urls: list[str]
    """User-provided stream URLs."""
    childSourceId: str | None
    """Child source ID (for snapshot fallback)."""


class CameraConfigInputSettings(TypedDict):
    """Camera input settings for config (without auto-generated fields)."""

    name: str
    """Source display name."""
    role: CameraRole
    """Resolution role."""
    useForSnapshot: bool
    """Use this source for snapshots."""
    hotMode: bool
    """Keep connection always active."""
    preload: bool
    """Preload stream on startup."""
    prebuffer: bool
    """Enable stream prebuffering."""
    childSourceId: str | None
    """Child source ID (for snapshot fallback)."""


class BaseCameraConfig(TypedDict):
    """Base camera configuration (shared fields)."""

    name: str
    """Camera display name."""
    nativeId: NotRequired[str]
    """Native device ID from plugin."""
    isCloud: NotRequired[bool]
    """Whether camera streams from cloud."""
    disabled: NotRequired[bool]
    """Disable this camera."""
    info: NotRequired[CameraInformation]
    """Camera hardware information."""


class CameraConfig(BaseCameraConfig):
    """Full camera configuration with sources."""

    sources: list[CameraConfigInputSettings]
    """Video input sources."""


class CameraConfigPartial(TypedDict, total=False):
    """Camera configuration subset for partial updates."""

    name: str
    """Camera display name."""
    nativeId: str
    """Native device ID from plugin."""
    isCloud: bool
    """Whether camera streams from cloud."""
    disabled: bool
    """Disable this camera."""
    info: CameraInformation
    """Camera hardware information."""
    sources: list[CameraConfigInputSettings]
    """Video input sources."""


class CameraUiSettings(TypedDict):
    """UI display settings for a camera."""

    streamingMode: VideoStreamingMode
    """Preferred streaming method."""
    streamingSource: StreamingRole | Literal["auto"]
    """Preferred stream quality."""
    aspectRatio: CameraAspectRatio
    """Display aspect ratio."""


class CameraRecordingSettings(TypedDict):
    """Recording settings for a camera."""

    enabled: bool
    """Enable recording."""


class CameraSourceData(CameraConfigInputSettings):
    """Camera source with resolved URLs."""

    _id: str
    """Unique source ID."""
    urls: StreamUrls
    """Generated streaming URLs."""


class AssignedPlugin(TypedDict):
    """Plugin assignment info."""

    id: str
    """Plugin ID."""
    name: str
    """Plugin display name."""


class PluginAssignments(TypedDict, total=False):
    """
    Plugin assignments for camera sensors/features.
    Maps sensor types to their assigned plugin(s).
    """

    motion: AssignedPlugin
    """Motion detection plugin."""
    object: AssignedPlugin
    """Object detection plugin."""
    audio: AssignedPlugin
    """Audio detection plugin."""
    face: AssignedPlugin
    """Face detection plugin."""
    licensePlate: AssignedPlugin
    """License plate detection plugin."""
    ptz: AssignedPlugin
    """PTZ control plugin."""
    battery: AssignedPlugin
    """Battery info plugin."""
    cameraController: AssignedPlugin
    """Camera controller plugin."""
    light: list[AssignedPlugin]
    """Light control plugins."""
    siren: list[AssignedPlugin]
    """Siren control plugins."""
    contact: list[AssignedPlugin]
    """Contact sensor plugins."""
    doorbell: list[AssignedPlugin]
    """Doorbell trigger plugins."""
    hub: list[AssignedPlugin]
    """Hub/bridge plugins."""


class CameraPluginInfo(TypedDict):
    """Camera source plugin information."""

    id: str
    """Plugin ID."""
    name: str
    """Plugin display name."""


class BaseCamera(TypedDict):
    """Base camera data structure (stored in database)."""

    _id: str
    """Unique camera ID."""
    nativeId: str | None
    """Native device ID from plugin."""
    pluginInfo: CameraPluginInfo | None
    """Source plugin information."""
    name: str
    """Camera display name."""
    disabled: bool
    """Whether camera is disabled."""
    isCloud: bool
    """Whether camera streams from cloud."""
    info: CameraInformation
    """Camera hardware information."""
    type: CameraType
    """Camera type (camera/doorbell)."""
    snapshotTTL: int
    """Snapshot cache TTL in seconds."""
    detectionZones: list[DetectionZone]
    """Detection zone configurations."""
    detectionSettings: CameraDetectionSettings
    """Detection settings."""
    frameWorkerSettings: CameraFrameWorkerSettings
    """Frame worker settings."""
    interface: CameraUiSettings
    """UI display settings."""
    recording: CameraRecordingSettings
    """Recording settings."""
    plugins: list[AssignedPlugin]
    """Installed plugins."""
    assignments: PluginAssignments
    """Sensor-to-plugin assignments."""


class Camera(BaseCamera):
    """Camera with resolved video sources."""

    sources: list[CameraSourceData]
    """Video input sources."""


CameraPublicProperties = Literal[
    "_id",
    "nativeId",
    "pluginInfo",
    "name",
    "disabled",
    "isCloud",
    "info",
    "type",
    "snapshotTTL",
    "detectionZones",
    "detectionSettings",
    "frameWorkerSettings",
    "interface",
    "recording",
    "plugins",
    "assignments",
    "sources",
]
"""Camera public property names for observation."""


class CameraPropertyObservableObject(TypedDict):
    """Camera property change event."""

    property: str
    """Property name that changed."""
    old_state: Any
    """Previous value."""
    new_state: Any
    """New value."""


@runtime_checkable
class CameraSource(Protocol):
    """Camera source with snapshot and probe capabilities."""

    _id: str
    """Unique source ID."""
    name: str
    """Source display name."""
    role: CameraRole
    """Resolution role."""
    useForSnapshot: bool
    """Use this source for snapshots."""
    hotMode: bool
    """Keep connection always active."""
    preload: bool
    """Preload stream on startup."""
    prebuffer: bool
    """Enable stream prebuffering."""
    urls: StreamUrls
    """Generated streaming URLs."""
    childSourceId: str | None
    """Child source ID (for snapshot fallback)."""

    async def snapshot(self, forceNew: bool = False) -> bytes | None:
        """
        Get camera snapshot image.

        Args:
            forceNew: Force fresh snapshot (ignore cache).

        Returns:
            JPEG image data or None if unavailable.
        """
        ...

    async def probeStream(
        self, probeConfig: ProbeConfig | None = None, refresh: bool = False
    ) -> ProbeStream | None:
        """
        Probe stream for codec and track information.

        Args:
            probeConfig: What to probe for.
            refresh: Force fresh probe (ignore cache).

        Returns:
            Stream information or None if unavailable.
        """
        ...


@runtime_checkable
class CameraDeviceSource(CameraSource, Protocol):
    """Camera source with full streaming capabilities."""

    def generateRTSPUrl(self, options: RTSPUrlOptions | None = None) -> str:
        """
        Generate RTSP URL with specified options.

        Args:
            options: URL generation options.

        Returns:
            RTSP URL string.
        """
        ...


@runtime_checkable
class CameraDevice(Protocol):
    """
    Main camera device interface.
    Provides access to camera streams, sensors, and services.
    """

    @property
    def id(self) -> str:
        """Unique camera ID."""
        ...

    @property
    def nativeId(self) -> str | None:
        """Native device ID from plugin."""
        ...

    @property
    def pluginInfo(self) -> CameraPluginInfo | None:
        """Source plugin information."""
        ...

    @property
    def disabled(self) -> bool:
        """Whether camera is disabled."""
        ...

    @property
    def name(self) -> str:
        """Camera display name."""
        ...

    @property
    def type(self) -> CameraType:
        """Camera type (camera/doorbell)."""
        ...

    @property
    def snapshotTTL(self) -> int:
        """Snapshot cache TTL."""
        ...

    @property
    def info(self) -> CameraInformation:
        """Camera hardware information."""
        ...

    @property
    def isCloud(self) -> bool:
        """Whether camera streams from cloud."""
        ...

    @property
    def detectionZones(self) -> list[DetectionZone]:
        """Detection zone configurations."""
        ...

    @property
    def detectionSettings(self) -> CameraDetectionSettings:
        """Detection settings."""
        ...

    @property
    def frameWorkerSettings(self) -> CameraFrameWorkerSettings:
        """Frame worker settings."""
        ...

    @property
    def sources(self) -> list[CameraDeviceSource]:
        """All video sources."""
        ...

    @property
    def streamSource(self) -> CameraDeviceSource:
        """Primary streaming source."""
        ...

    @property
    def highResolutionSource(self) -> CameraDeviceSource | None:
        """High resolution source (if available)."""
        ...

    @property
    def midResolutionSource(self) -> CameraDeviceSource | None:
        """Mid resolution source (if available)."""
        ...

    @property
    def lowResolutionSource(self) -> CameraDeviceSource | None:
        """Low resolution source (if available)."""
        ...

    @property
    def snapshotSource(self) -> CameraSource | None:
        """Snapshot source (if available)."""
        ...

    @property
    def connected(self) -> bool:
        """Whether camera is connected."""
        ...

    @property
    def frameWorkerConnected(self) -> bool:
        """Whether frame worker is connected."""
        ...

    @property
    def onConnected(self) -> HybridObservable[bool]:
        """Observable for connection state changes."""
        ...

    @property
    def onFrameWorkerConnected(self) -> HybridObservable[bool]:
        """Observable for frame worker state changes."""
        ...

    @property
    def logger(self) -> LoggerService:
        """Logger service for this camera."""
        ...

    async def connect(self) -> None:
        """Connect to the camera."""
        ...

    async def disconnect(self) -> None:
        """Disconnect from the camera."""
        ...

    def onPropertyChange(
        self, property: CameraPublicProperties | list[CameraPublicProperties]
    ) -> HybridObservable[CameraPropertyObservableObject]:
        """
        Observe camera property changes.

        Args:
            property: Property name(s) to observe.

        Returns:
            Observable emitting old and new values.
        """
        ...

    def getSensors(self) -> list[SensorLike]:
        """Get all sensors attached to this camera."""
        ...

    def getSensor(self, sensorId: str) -> SensorLike | None:
        """Get sensor by ID."""
        ...

    def getSensorsByType(self, sensorType: SensorType) -> list[SensorLike]:
        """Get all sensors of a specific type."""
        ...

    def getMotionSensor(self) -> SensorLike | None:
        """Get motion detection sensor."""
        ...

    def getObjectSensor(self) -> SensorLike | None:
        """Get object detection sensor."""
        ...

    def getFaceSensor(self) -> SensorLike | None:
        """Get face detection sensor."""
        ...

    def getLicensePlateSensor(self) -> SensorLike | None:
        """Get license plate detection sensor."""
        ...

    def getAudioSensor(self) -> SensorLike | None:
        """Get audio detection sensor."""
        ...

    def getPTZControl(self) -> SensorLike | None:
        """Get PTZ control sensor."""
        ...

    async def addSensor(self, sensor: Sensor[Any, Any, Any]) -> None:
        """
        Add a sensor to this camera.

        Args:
            sensor: Sensor instance to add.
        """
        ...

    async def removeSensor(self, sensorId: str) -> None:
        """
        Remove a sensor from this camera.

        Args:
            sensorId: ID of sensor to remove.
        """
        ...

    def onSensorAdded(self, callback: Callable[[str, SensorType], None]) -> Callable[[], None]:
        """
        Register callback for sensor additions.

        Args:
            callback: Called when sensor is added.

        Returns:
            Unsubscribe function.
        """
        ...

    def onSensorRemoved(self, callback: Callable[[str, SensorType], None]) -> Callable[[], None]:
        """
        Register callback for sensor removals.

        Args:
            callback: Called when sensor is removed.

        Returns:
            Unsubscribe function.
        """
        ...

    async def registerService(self, service: Service) -> None:
        """
        Register a service for this camera.

        Args:
            service: Service instance to register.
        """
        ...

    async def unregisterService(self, serviceType: ServiceType) -> None:
        """
        Unregister a service from this camera.

        Args:
            serviceType: Service type to unregister.
        """
        ...


__all__ = [
    # Types
    "CameraType",
    "ZoneType",
    "ZoneFilter",
    "CameraRole",
    "StreamingRole",
    "DecoderFormat",
    "ImageInputFormat",
    "ImageOutputFormat",
    "CameraFrameWorkerDecoder",
    "MotionResolution",
    "AudioCodec",
    "AudioFFmpegCodec",
    "VideoCodec",
    "VideoFFmpegCodec",
    "RTSPAudioCodec",
    "ProbeAudioCodec",
    "VideoStreamingMode",
    "CameraAspectRatio",
    "FrameType",
    "Point",
    # Frame/Image
    "FrameMetadata",
    "ImageInformation",
    "ImageCrop",
    "ImageResize",
    "ImageFormat",
    "ImageOptions",
    "FrameImage",
    "FrameBuffer",
    "FrameData",
    "VideoFrame",
    # Streaming URLs
    "Go2RtcWSSource",
    "Go2RtcRTSPSource",
    "Go2RtcSnapshotSource",
    "StreamUrls",
    # Probe
    "ProbeConfig",
    "FMTPInfo",
    "AudioCodecProperties",
    "VideoCodecProperties",
    "AudioStreamInfo",
    "VideoStreamInfo",
    "ProbeStream",
    "RTSPUrlOptions",
    "IceServer",
    # Detection
    "PluginLabels",
    "AvailableLabels",
    "DetectionZone",
    "MotionDetectionSettings",
    "ObjectDetectionSettings",
    "CameraDetectionSettings",
    # Config
    "CameraInformation",
    "CameraFrameWorkerSettings",
    "CameraInput",
    "CameraInputSettings",
    "CameraConfigInputSettings",
    "BaseCameraConfig",
    "CameraConfig",
    "CameraConfigPartial",
    "CameraUiSettings",
    "CameraRecordingSettings",
    "CameraSourceData",
    # Plugin assignments
    "AssignedPlugin",
    "PluginAssignments",
    "CameraPluginInfo",
    # Camera
    "BaseCamera",
    "Camera",
    "CameraPublicProperties",
    "CameraPropertyObservableObject",
    # Protocols
    "CameraSource",
    "CameraDeviceSource",
    "CameraDevice",
]
