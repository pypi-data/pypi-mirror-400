import pandas as pd

from trendminer_interface.base import SerializableBase
from trendminer_interface.tag import Tag
from trendminer_interface.asset import Attribute
from .entry import FingerprintEntryMultiFactory



class FingerprintHull(SerializableBase):
    """Fingerprint hull data for a single Tag or Attribute

    Attributes
    ----------
    reference : Tag or Attribute
        Underlying tag or attribute
    values : pd.DataFrame
        Min and max values (columns names: minValue, maxValue) with TimedeltaIndex
    latent : bool
        Whether the hull was implicitly added to the fingerprint from a tag hidden at fingerprint creation
    """

    def __init__(
            self,
            client,
            reference,
            values,
            latent,
    ):
        super().__init__(client=client)
        self.reference = reference
        self.values = values
        self.latent = latent

    @classmethod
    def _from_json(cls, client, data):
        return cls(
            client=client,
            reference=FingerprintEntryMultiFactory(client=client)._from_json_fingerprint(data["dataReference"]),
            latent=data["latent"],
            values=cls._hull_json_to_df(data["hullValues"]),
        )

    @staticmethod
    def _hull_json_to_df(values):
        df = pd.DataFrame(values)
        df = df.set_index("offset", drop=True)
        df.index = pd.to_timedelta(df.index, unit="ms")
        return df

    @staticmethod
    def _hull_df_to_json(values):
        values = values.copy()
        values.index = (values.index.total_seconds()*1000).astype(int)
        return values.reset_index().to_dict(orient="records")

    @property
    def tag(self):
        """Underlying tag of the reference"""
        if isinstance(self.reference, Attribute):
            return self.reference.tag
        else:
            return self.reference

    def __repr__(self):
        return f"<< {self.__class__.__name__} | {self.reference.name} >>"

    def _json(self):
        """json representation used in fingerprint search"""
        return {
            "tag": {
                "id": self.tag.name,
                "shift": int(self.tag.shift.total_seconds()),
                "interpolationType": self.tag._interpolation_payload_str,
            },
            "hulls": self._hull_df_to_json(self.values)
        }
