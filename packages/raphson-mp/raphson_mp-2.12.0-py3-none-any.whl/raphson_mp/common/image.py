from enum import Enum


class ImageFormat(Enum):
    JPEG = "jpeg"
    WEBP = "webp"
    AVIF = "avif"

    @property
    def content_type(self):
        return IMAGE_CONTENT_TYPE[self]


IMAGE_CONTENT_TYPE: dict[ImageFormat, str] = {
    ImageFormat.JPEG: "image/jpeg",
    ImageFormat.WEBP: "image/webp",
    ImageFormat.AVIF: "image/avif",
}


class ImageQuality(Enum):
    HIGH = "high"
    LOW = "low"

    @property
    def resolution(self) -> int:
        if self is ImageQuality.HIGH:
            return 1200  # 1200x1200 matches highest quality MusicBrainz cover
        elif self is ImageQuality.LOW:
            return 512
        else:
            raise ValueError()


def guess_content_type(image_data: bytes) -> str:
    if image_data[:16] == b"\x00\x00\x00 ftypavif\x00\x00\x00\x00":
        return "image/avif"
    elif image_data[:11] == b"\xff\xd8\xff\xe0\x00\x10JFIF\x00":
        return "image/jpeg"
    elif image_data[:4] == b"RIFF" and image_data[8:16] == b"WEBPVP8\x20":
        return "image/webp"
    elif image_data[:4] == b"\x89PNG":
        return "image/png"
    else:
        raise ValueError(image_data[:16])
