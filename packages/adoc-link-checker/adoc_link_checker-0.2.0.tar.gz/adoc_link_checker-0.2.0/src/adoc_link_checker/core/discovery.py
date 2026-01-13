import os


def find_adoc_files(path: str) -> list[str]:
    """
    Return a list of .adoc files from a file or directory path.
    """
    if os.path.isfile(path):
        if not path.endswith(".adoc"):
            raise ValueError("Provided file is not a .adoc file")
        return [path]

    adoc_files: list[str] = []

    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(".adoc"):
                adoc_files.append(os.path.join(root, file))

    return adoc_files
