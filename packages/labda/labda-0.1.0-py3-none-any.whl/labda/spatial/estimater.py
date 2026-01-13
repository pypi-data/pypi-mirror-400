from dataclasses import dataclass

import geopandas as gpd
from timezonefinder import TimezoneFinder


@dataclass
class SpatialEstimater:
    samples: int = 10
    limit: float = 0.75

    @staticmethod
    def estimate_crs(gdf: gpd.GeoDataFrame) -> tuple[str, str]:
        estimated_crs = gdf.estimate_utm_crs()
        unit = estimated_crs.axis_info[0].unit_name

        return estimated_crs.to_string(), unit

    def estimate_timezone(self, gdf: gpd.GeoDataFrame) -> str:
        samples = gdf.sample(n=self.samples)

        if samples.crs != "EPSG:4326":
            samples.to_crs("EPSG:4326", inplace=True)

        tz_finder = TimezoneFinder()
        samples["timezone"] = samples.apply(
            lambda row: tz_finder.timezone_at(lat=row.geometry.y, lng=row.geometry.x),  # type: ignore
            axis=1,
        )

        timezones = samples["timezone"].value_counts()
        timezone = str(timezones.idxmax())

        n = len(timezones)
        count = timezones.loc[timezone]
        percentage = (count / n) * 100

        if percentage < self.limit:
            raise ValueError(
                f"Timezone could not be determined with sufficient confidence. Most common timezone is less than {self.limit * 100:.2f}% ({percentage * 100:.2f}%)."
            )

        return timezone
