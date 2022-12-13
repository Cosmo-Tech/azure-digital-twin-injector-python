import os


def ls_files(client, path, recursive=False):
    """
    Lists files (blobs) under a path, optionally recursively inside the client's container
    """
    if not path == "" and not path.endswith("/"):
        path += "/"

    blob_iter = client.list_blobs(name_starts_with=path)
    files = []
    for blob in blob_iter:
        relative_path = os.path.relpath(blob.name, path)
        if (recursive or "/" not in relative_path) and relative_path.endswith(".csv"):
            files.append(relative_path)
    return files
