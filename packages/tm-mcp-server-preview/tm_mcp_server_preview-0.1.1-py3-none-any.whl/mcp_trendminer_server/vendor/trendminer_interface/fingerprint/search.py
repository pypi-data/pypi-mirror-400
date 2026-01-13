import pandas as pd
from trendminer_interface.base import AuthenticatableBase
from .hull import FingerprintHull


class FingerprintSearch(AuthenticatableBase):
    """Fingerprint search

    A fingerprint search is not a work organizer object and cannot be saved. It can only be instantiated and executed.
    """

    def __init__(
            self,
            client,
            hulls,
            threshold,
    ):
        super().__init__(client=client)
        self.hulls = hulls
        self.threshold = threshold

    def get_results(self, intervals, name="match", drop=True):
        """Executes fingerprints search and extracts results from the server

        Parameters
        ----------
        intervals : pandas.DataFrame or pandas.Interval
            Interval(s) to search in
        name : str, default 'match'
            Name of the IntervalIndex of the returned DataFrame
        drop : bool, default True
            Whether to drop the original index if `intervals` is a DataFrame

        Returns
        -------
        DataFrame
            Search results, including calculations and similarity score (`score`). Sorted from old to new.
        """

        if isinstance(intervals, pd.Interval):
            intervals = pd.IntervalIndex(data=[intervals])

        if isinstance(intervals, pd.IntervalIndex):
            intervals = pd.DataFrame(index=intervals)
            drop = True # overwrite drop

        if intervals.interval.has_overlaps():
            raise ValueError("Search input must be none-overlapping intervals")

        interval = pd.Interval(
            left=intervals.index.left.min() + pd.Timedelta(milliseconds=int(intervals.index.closed in ["right", "neither"])),
            right=intervals.index.right.max() - pd.Timedelta(milliseconds=int(intervals.index.closed in ["left", "neither"])),
            closed=intervals.index.closed,
        )

        excluded_intervals = intervals.interval.invert(name="excluded")
        if excluded_intervals.index.closed in ["left", "both"]:
            excluded_intervals = excluded_intervals.interval.grow(left=pd.Timedelta(milliseconds=1))
        elif excluded_intervals.index.closed in ["right", "both"]:
            excluded_intervals = excluded_intervals.interval.grow(right=pd.Timedelta(milliseconds=1))

        excluded_interval_data = excluded_intervals.index.map(
            lambda x: {
                "startDate": x.left.isoformat(timespec="milliseconds"),
                "endDate": x.right.isoformat(timespec="milliseconds"),
            }
        ).to_list()

        queries = [hull._json() for hull in self.hulls]
        min_duration = min([query["hulls"][-1]["offset"] for query in queries])

        data = {
            "contextTimePeriod": {
                "startDate": interval.left.isoformat(timespec="milliseconds"),
                "endDate": interval.right.isoformat(timespec="milliseconds"),
            },
            "filters": excluded_interval_data,
            "params": {
                "detectionThreshold": self.threshold,
                "duration": min_duration,
            },
            "queries": queries,
        }

        r = self.client.session.post("/compute/fingerprintsearch/newSearch", json=data)

        if r.json():
            results = (
                pd.DataFrame(r.json())
                .drop("openEnded", axis=1)  # Remove openEnded information that comes from properties
                .assign(
                    startDate=lambda df: pd.to_datetime(df["startDate"]).dt.tz_convert(self.client.tz),
                    endDate=lambda df: pd.to_datetime(df["endDate"]).dt.tz_convert(self.client.tz)
                )
                .pipe(lambda df: df.set_index(
                    pd.IntervalIndex.from_arrays(
                        left=df.pop("startDate"),
                        right=df.pop("endDate"),
                        closed="both",
                        name=name,
                    )
                ))
                .sort_index()
            )
        else:
            results = pd.DataFrame(
                index=pd.IntervalIndex(
                    data=[], closed="both", dtype=f"interval[datetime64[ns, {self.client.tz}], both]"
                ),
                columns=["score"],
                dtype="float64",
            )

        # Merge original and results DataFrames
        reset_df = intervals.reset_index(drop=drop)
        if results.empty:
            mapped_df = reset_df[0:0]  # required since from_records cannot handle empty index in pandas 2 (fixed in 3)
        else:
            mapped_df = pd.DataFrame.from_records(
                index=results.index,
                data=results.index.map(
                    lambda x: reset_df[intervals.index.overlaps(x)].iloc[0, :]
                )
            )

        return pd.concat([results, mapped_df], axis=1)


class FingerprintSearchFactory(AuthenticatableBase):
    tm_class = FingerprintSearch

    def __call__(self, hulls, threshold):
        """Instantiate new fingerprint search

        Parameters
        ----------
        hulls : list of FingerprintHull
            Tag hulls coming from a fingerprint
        threshold : float
            Detection threshold for matches. Value between 0 and 100.
        """
        return self.tm_class(
            client=self.client,
            hulls=hulls,
            threshold=threshold,
        )
