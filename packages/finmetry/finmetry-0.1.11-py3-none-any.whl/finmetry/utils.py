import os as _os
import pandas as _pd


def make_dir(path1: str) -> None:
    """Makes the directory at given path1, if directory is not present.

    Path1 should have the name of the directory which is to be created at the end of the path.

    Parameters
    ----------
    path1 : str
        Path of the directory to be created, including the name of the directory.
    """
    try:
        _os.mkdir(path1)
    except FileExistsError as e:
        pass

    return


def get_dir_path(fname: str) -> list[str]:
    """gives the path of all the sub-directories inside fname folder.

    Parameters
    ----------
    fname : str
        path of the folder

    Returns
    -------
    list[str]
        folerpaths of all the sub-directories inside fname folder.
    """
    return [
        _os.path.join(fname, x)
        for x in _os.listdir(fname)
        if _os.path.isdir(_os.path.join(fname, x))
    ]


def get_file_path(fname: str) -> list[str]:
    """gives the path of all the files inside fname folder, does not give path to any sub-folder.

    Parameters
    ----------
    fname : str
        path of the folder

    Returns
    -------
    list[str]
        file paths of all the files inside fname folder.
    """
    return [
        _os.path.join(fname, x)
        for x in _os.listdir(fname)
        if _os.path.isfile(_os.path.join(fname, x))
    ]


def get_dir_name(fname: str) -> list[str]:
    """gives the name of all the sub-directories inside fname folder.

    Parameters
    ----------
    fname : str
        path of the folder

    Returns
    -------
    list[str]
        names of all the sub-directories inside fname folder.
    """
    return [x for x in _os.listdir(fname) if _os.path.isdir(_os.path.join(fname, x))]


def get_file_name(fname: str) -> list[str]:
    """gives the name of all the files inside fname folder, does not give name of any sub-folder.

    Parameters
    ----------
    fname : str
        path of the folder

    Returns
    -------
    list[str]
        file names of all the files inside fname folder.
    """
    return [x for x in _os.listdir(fname) if _os.path.isfile(_os.path.join(fname, x))]


def append_it(data: _pd.DataFrame, filepath: str) -> None:
    """Appends the data on the given filepath after comparing Indexes of both the data.

    This compares the data already at the given filepath, and then appends only the data not already present.

    Parameters
    ----------
    data : _pd.DataFrame
        data frame with Datetime like index
    filepath : str
        filepath, where the dataframe will be appended.
    """
    try:
        df1 = _pd.read_pickle(filepath)
        ### checking the data after the last date
        d1 = df1.index[-1]
        f1 = data.index > d1
        df1 = _pd.concat([df1, data[f1]])
        ### checking the data before the first date
        d1 = df1.index[0]
        f1 = data.index < d1
        df1 = _pd.concat([data[f1], df1])

        df1.to_pickle(filepath)
        return
    except FileNotFoundError as e:
        print(f"Creating the file - {filepath}")
        data.to_pickle(filepath)
        return


def append_it_blind(data: _pd.DataFrame, filepath: str) -> None:
    """Appends the data at the given filepath

    This blindly appends the data on the given filepath even if the data is repitition of available data.

    Parameters
    ----------
    data : _pd.DataFrame
        data frame with Datetime like index
    filepath : str
        filepath, where the dataframe will be appended.
    """
    try:
        df1 = _pd.read_pickle(filepath)
        df1 = _pd.concat([data, df1])
        df1.to_pickle(filepath)
        return
    except FileNotFoundError as e:
        print(f"Creating the file - {filepath}")
        data.to_pickle(filepath)
        return


