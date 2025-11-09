import subprocess
from datetime import datetime

from src.supported_file_types.exceptions import ExifWriterError
from src.supported_file_types.exif_writer import ExifWriter


class MP4Writer(ExifWriter):
    _VERTICAL_DIRECTIONS = ["S", "N"]
    _HORIZONTAL_DIRECTIONS = ["W", "E"]

    @staticmethod
    def write(source_filepath: str, output_filepath: str, metadata: dict) -> None:
        exif_args = MP4Writer._get_exif_args(source_filepath, output_filepath, metadata)
        try:
            subprocess.run(
                exif_args, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
        except subprocess.CalledProcessError as e:
            # Catch all exiftool errors and raise ExifWriterError
            # This allows the caller to handle it gracefully
            raise ExifWriterError() from e

    @staticmethod
    def _get_exif_args(
        source_filepath: str, output_filepath: str, metadata: dict
    ) -> list[str]:
        timestamp = int(metadata["photoTakenTime"]["timestamp"])
        latitude = metadata["geoData"]["latitude"]
        longitude = metadata["geoData"]["longitude"]
        altitude = metadata["geoData"]["altitude"]
        description = metadata["description"]
        title = metadata["title"]

        exif_args = ["exiftool", "-q", "-P"]
        exif_args.extend(MP4Writer._get_date_args(timestamp))
        exif_args.extend(MP4Writer._get_gps_args(latitude, longitude, altitude))
        exif_args.extend(MP4Writer._get_description_args(description))
        exif_args.extend(MP4Writer._get_title_args(title))
        exif_args.append(source_filepath)
        exif_args.append("-o")
        exif_args.append(output_filepath)
        return exif_args

    @staticmethod
    def _get_date_args(timestamp: int) -> list[str]:
        formatted_datetime = datetime.fromtimestamp(timestamp).strftime(
            ExifWriter.DATETIME_STR_FORMAT
        )
        return [
            f"-CreateDate={formatted_datetime}",
            f"-ModifyDate={formatted_datetime}",
            f"-MediaCreateDate={formatted_datetime}",
            f"-MediaModifyDate={formatted_datetime}",
        ]

    @staticmethod
    def _get_direction(value: float, direction: list[str]) -> str:
        if value < 0:
            return direction[0]
        if value > 0:
            return direction[1]
        return ""

    @staticmethod
    def _get_gps_args(latitude: float, longitude: float, altitude: float) -> list[str]:
        latitude_ref = MP4Writer._get_direction(
            latitude, MP4Writer._VERTICAL_DIRECTIONS
        )
        longitude_ref = MP4Writer._get_direction(
            longitude, MP4Writer._HORIZONTAL_DIRECTIONS
        )
        altitude = round(abs(altitude), 4)
        return [
            "-GPSVersionID=2 0 0 0",
            f"-GPSLatitudeRef={latitude_ref}",
            f"-GPSLatitude={latitude}",
            f"-GPSLongitudeRef={longitude_ref}",
            f"-GPSLongitude={longitude}",
            f"-GPSAltitudeRef={altitude}",
            f"-GPSAltitude={altitude}",
        ]

    @staticmethod
    def _get_description_args(description: str) -> list[str]:
        return [
            f"-Description={description}",
            f"-Comment={description}",
        ]

    @staticmethod
    def _get_title_args(title: str) -> list[str]:
        return [
            f"-Title={title}",
        ]
