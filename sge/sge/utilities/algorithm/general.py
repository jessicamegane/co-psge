from sys import version_info


def check_python_version():
    """
    Check the python version to ensure it is correct. PonyGE uses Python 3.

    :return: Nothing
    """

    if version_info.major < 3 or (version_info.minor < 5 and
                                  version_info.major == 3):
        s = "\nError: Python version not supported.\n" \
            "       Must use at least Python 3.5."
        raise Exception(s)
