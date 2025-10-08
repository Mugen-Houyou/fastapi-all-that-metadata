"""Utilities for extracting and editing image metadata."""

from __future__ import annotations

import base64
import io
import mimetypes
from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Dict, Iterable, Mapping, MutableMapping, Tuple

import piexif
from PIL import Image, ImageFile

try:  # pragma: no cover - optional dependency registration
    from pillow_heif import register_avif_opener, register_heif_opener

    register_heif_opener()
    register_avif_opener()
except ModuleNotFoundError:  # pragma: no cover - pillow-heif is an optional dependency
    pass

# Allow processing of large images without Pillow warnings and permit truncated files.
Image.MAX_IMAGE_PIXELS = None
ImageFile.LOAD_TRUNCATED_IMAGES = True


ExifDict = MutableMapping[str, Any]


def _guess_mime(filename: str | None, content_type: str | None) -> str | None:
    if content_type and content_type != "application/octet-stream":
        return content_type
    if filename:
        guessed, _ = mimetypes.guess_type(filename)
        return guessed
    return None


def _is_exif_supported_for_editing(mime: str | None) -> bool:
    if not mime:
        return False
    return any(
        mime.lower().startswith(prefix)
        for prefix in ("image/jpeg", "image/jpg", "image/tiff", "image/webp")
    )


def _clean_bytes(value: bytes) -> str:
    try:
        return value.decode("utf-8").rstrip("\x00")
    except UnicodeDecodeError:
        return base64.b64encode(value).decode("ascii")


def _rational_to_float(value: Any) -> float | None:
    if hasattr(value, "numerator") and hasattr(value, "denominator"):
        denominator = getattr(value, "denominator") or 0
        if denominator == 0:
            return None
        return float(getattr(value, "numerator")) / float(denominator)
    if isinstance(value, (tuple, list)) and len(value) == 2:
        numerator, denominator = value
        if not denominator:
            return None
        return float(numerator) / float(denominator)
    return None


def _normalise_value(value: Any) -> Any:
    if isinstance(value, bytes):
        return _clean_bytes(value)
    if isinstance(value, (list, tuple)):
        return [
            _normalise_value(item) if not hasattr(item, "numerator") else _rational_to_float(item)
            for item in value
        ]
    if hasattr(value, "numerator") and hasattr(value, "denominator"):
        return _rational_to_float(value)
    return value


def _make_tag_lookup() -> Dict[str, Tuple[str, int, str]]:
    lookup: Dict[str, Tuple[str, int, str]] = {}
    for ifd_name, tags in piexif.TAGS.items():
        for tag_id, info in tags.items():
            name = info.get("name")
            type_name = info.get("type")
            if not name or not type_name:
                continue
            lookup.setdefault(name, (ifd_name, tag_id, type_name))
    return lookup


TAG_LOOKUP = _make_tag_lookup()


def _convert_to_exif_type(value: Any, type_name: str) -> Any:
    if type_name == "Ascii":
        if isinstance(value, bytes):
            return value
        return str(value).encode("utf-8")
    if type_name in {"Byte", "Short", "Long", "SShort", "SLong"}:
        return int(value)
    if type_name in {"Rational", "SRational"}:
        if isinstance(value, (tuple, list)) and len(value) == 2:
            num, den = value
            return int(num), int(den)
        if isinstance(value, str) and "/" in value:
            num_str, den_str = value.split("/", 1)
            return int(num_str.strip()), int(den_str.strip())
        frac = Fraction(str(value)).limit_denominator(1000000)
        return frac.numerator, frac.denominator
    if type_name == "Undefined":
        if isinstance(value, bytes):
            return value
        return str(value).encode("utf-8")
    if type_name in {"Float", "Double"}:
        return float(value)
    return value


def _extract_gps(exif_dict: Mapping[str, Mapping[int, Any]]) -> Dict[str, Any]:
    gps_ifd = exif_dict.get("GPS")
    if not gps_ifd:
        return {}

    gps_tags: Dict[str, Any] = {}
    for key, value in gps_ifd.items():
        info = piexif.TAGS.get("GPS", {}).get(key)
        name = info.get("name") if info else str(key)
        gps_tags[name] = value

    def _to_degrees(coords: Iterable[Any], ref: str | bytes | None) -> float | None:
        if not coords or len(coords) != 3:
            return None
        degrees, minutes, seconds = coords
        deg = _rational_to_float(degrees) or 0.0
        minute = _rational_to_float(minutes) or 0.0
        second = _rational_to_float(seconds) or 0.0
        result = deg + minute / 60.0 + second / 3600.0
        if isinstance(ref, bytes):
            ref = _clean_bytes(ref)
        if ref in {"S", "W"}:
            result *= -1
        return result

    lat = _to_degrees(gps_tags.get("GPSLatitude"), gps_tags.get("GPSLatitudeRef"))
    lon = _to_degrees(gps_tags.get("GPSLongitude"), gps_tags.get("GPSLongitudeRef"))
    alt = gps_tags.get("GPSAltitude")
    if alt is not None:
        alt = _rational_to_float(alt) or alt

    gps_result: Dict[str, Any] = {}
    if lat is not None:
        gps_result["lat"] = lat
    if lon is not None:
        gps_result["lon"] = lon
    if alt is not None:
        gps_result["alt"] = alt
    return gps_result


def _normalise_exif(
    exif_dict: Mapping[str, Mapping[int, Any]]
) -> Tuple[ExifDict, Dict[str, Dict[str, Any]]]:
    readable: ExifDict = {}
    raw: Dict[str, Dict[str, Any]] = {}

    for ifd_name, tags in exif_dict.items():
        if not isinstance(tags, Mapping):
            continue
        raw_section: Dict[str, Any] = {}
        for tag_id, value in tags.items():
            info = piexif.TAGS.get(ifd_name, {}).get(tag_id)
            tag_name = info.get("name") if info else str(tag_id)
            cleaned_value = _normalise_value(value)
            raw_section[tag_name] = cleaned_value
            if ifd_name in {"0th", "Exif", "Interop"}:
                readable[tag_name] = cleaned_value
        if raw_section:
            raw[ifd_name] = raw_section
    return readable, raw


@dataclass
class MetadataResult:
    image: Dict[str, Any]
    exif: Dict[str, Any]
    gps: Dict[str, Any]
    raw: Dict[str, Dict[str, Any]]
    exif_bytes: bytes | None
    mime: str | None


class MetadataError(Exception):
    """Raised when metadata extraction or editing fails."""


def extract_metadata(
    file_bytes: bytes, filename: str | None, content_type: str | None
) -> MetadataResult:
    mime = _guess_mime(filename, content_type)

    try:
        with Image.open(io.BytesIO(file_bytes)) as image:
            width, height = image.size
            exif_bytes = image.info.get("exif")
            exif_dict: Dict[str, Mapping[int, Any]] = {}
            if exif_bytes:
                try:
                    exif_dict = piexif.load(exif_bytes)
                except Exception as exc:  # pragma: no cover - defensive
                    raise MetadataError("EXIF 정보를 불러오지 못했습니다.") from exc
            else:
                exif_data = image.getexif()
                if exif_data:
                    exif_dict = {"0th": dict(exif_data.items())}

    except MetadataError:
        raise
    except Exception as exc:  # pragma: no cover - defensive
        raise MetadataError("이미지 파일을 처리할 수 없습니다.") from exc

    readable, raw = _normalise_exif(exif_dict)
    gps = _extract_gps(exif_dict)

    image_info = {
        "width": width,
        "height": height,
        "mime": mime,
        "size": len(file_bytes),
    }

    return MetadataResult(
        image=image_info,
        exif=readable,
        gps=gps,
        raw=raw,
        exif_bytes=exif_bytes,
        mime=mime,
    )


def apply_exif_edits(
    file_bytes: bytes,
    result: MetadataResult,
    updates: Mapping[str, Any] | None = None,
    removals: Iterable[str] | None = None,
) -> Tuple[bytes, MetadataResult]:
    if not _is_exif_supported_for_editing(result.mime):
        raise MetadataError("해당 이미지 형식은 EXIF 편집을 지원하지 않습니다.")

    if result.exif_bytes is None:
        exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "Interop": {}, "1st": {}, "thumbnail": None}
    else:
        try:
            exif_dict = piexif.load(result.exif_bytes)
        except Exception as exc:  # pragma: no cover - defensive
            raise MetadataError("EXIF 데이터를 불러오지 못했습니다.") from exc

    updates = updates or {}
    removals = set(removals or [])

    for tag_name in removals:
        tag_info = TAG_LOOKUP.get(tag_name)
        if not tag_info:
            continue
        ifd_name, tag_id, _ = tag_info
        if ifd_name in exif_dict and tag_id in exif_dict[ifd_name]:
            del exif_dict[ifd_name][tag_id]

    for tag_name, new_value in updates.items():
        tag_info = TAG_LOOKUP.get(tag_name)
        if not tag_info:
            raise MetadataError(f"지원하지 않는 EXIF 태그입니다: {tag_name}")
        ifd_name, tag_id, type_name = tag_info
        converted = _convert_to_exif_type(new_value, type_name)
        exif_dict.setdefault(ifd_name, {})[tag_id] = converted

    exif_bytes = piexif.dump(exif_dict)

    try:
        modified_bytes = piexif.insert(exif_bytes, file_bytes)
    except Exception as exc:  # pragma: no cover - defensive
        raise MetadataError("EXIF 데이터를 적용하지 못했습니다.") from exc

    updated = extract_metadata(modified_bytes, None, result.mime)
    return modified_bytes, updated


def build_json_response(result: MetadataResult) -> Dict[str, Any]:
    return {
        "image": result.image,
        "exif": result.exif,
        "gps": result.gps,
        "raw": result.raw,
    }


def build_edit_response(
    modified_bytes: bytes, filename: str | None, result: MetadataResult
) -> Dict[str, Any]:
    b64 = base64.b64encode(modified_bytes).decode("ascii")
    return {
        **build_json_response(result),
        "file": {
            "filename": filename or "edited-image.jpg",
            "mime": result.mime,
            "base64": b64,
            "size": len(modified_bytes),
        },
    }

