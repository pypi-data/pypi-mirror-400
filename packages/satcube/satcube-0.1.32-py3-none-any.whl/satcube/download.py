from __future__ import annotations

from datetime import date, timedelta

import cubexpress

from satcube.objects import SatCubeMetadata


def metadata(
    lon: float,
    lat: float,
    edge_size: int,
    *,
    start: str = "2015-01-01",
    end: str | None = None,
    max_cscore: float = 1.0,
    min_cscore: float = 0.0,
) -> SatCubeMetadata:
    """
    Build a SatCubeMetadata object for a Sentinel-2 patch.

    Args:
        lon: Longitude of the patch centre (WGS-84 decimal degrees).
        lat: Latitude of the patch centre (WGS-84 decimal degrees).
        edge_size: Length of the square patch edge in metres.
        start: Start date (inclusive) for the query, formatted YYYY-MM-DD. Default "2015-01-01".
        end: End date (inclusive). If None, defaults to yesterday. Default None.
        max_cscore: Upper threshold for the cloud-score CDF filter. Default 1.0.
        min_cscore: Lower threshold for the cloud-score CDF filter. Default 0.0.

    Returns:
        SatCubeMetadata wrapper ready for chained processing (e.g. .download().align().gapfill()).

    Examples:
        >>> import satcube
        >>> meta = satcube.metadata(
        ...     lon=-77.06,
        ...     lat=-9.54,
        ...     edge_size=2048,
        ...     start="2019-01-01",
        ...     end="2019-12-31"
        ... )
        >>> print(len(meta))
    """
    if end is None:
        end = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")

    df = cubexpress.s2_table(
        lon=lon,
        lat=lat,
        edge_size=edge_size,
        start=start,
        end=end,
        max_cscore=max_cscore,
        min_cscore=min_cscore,
    )

    return SatCubeMetadata(df=df)
