import pandas as pd


def structure_csv(tag_data_dict):
    """Construct DataFrame matching TrendMiner csv import format from list of tags with timeseries data

    Parameters
    ----------
    tag_data_dict : dict[Tag, pandas.Series]
        Dictionary with Tag instances as the keys, and Series objects with DatetimeIndex as the values

    Returns
    -------
    df : pandas.DataFrame
        DataFrame suitable for Tag Builder csv import
    """

    # TODO: test function before committing
    # Set timezone if absent
    ser_list = []
    for tag, ser in tag_data_dict.items():
        ser = ser.copy()  # copy to not edit original input in place
        if ser.index.tz is None:
            ser.index = ser.index.tz_localize(tag.client.tz, ambiguous='infer')
        ser_list.append(ser)

    # Join data in single DataFrame
    df = pd.concat(ser_list, axis=1)

    # Empty values need to be blank for the import
    df = df.fillna("")

    # Set index to correct string format
    df.index = df.index.map(lambda x: x.isoformat(timespec="milliseconds"))

    # Columns need to contain metadata for the import. Digital tag import not supported, map to digital.
    csv_type = lambda tag_type: "string" if tag_type.casefold() == "digital" else tag_type.casefold()
    tag_metadata_tuples = [
        (tag.name, tag.description, tag.units, csv_type(tag.tag_type))
        for tag in tag_data_dict.keys()
    ]
    df.columns = pd.MultiIndex.from_tuples(tag_metadata_tuples)

    return df
