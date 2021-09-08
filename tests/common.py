from google_drive_downloader import GoogleDriveDownloader as gdd

def get_data(data, out):
    """Download pre-processed wind or ice data."""
    if data == "wind":
        fid = "1hUoZvwuwL1wQNvF5UL-Z_GlgWfh44vnk"
        gdd.download_file_from_google_drive(file_id=fid,
                                            dest_path=out,
                                            showsize=True,
                                            overwrite=False)
    elif data == "ice":
        fid = "1uu_qeiE4obalq_hUxIT4esEHYiIsngEb"
        gdd.download_file_from_google_drive(file_id=fid,
                                            dest_path=out,
                                            showsize=True,
                                            overwrite=False)
    else:
        raise ValueError("data type not valid. Use wind or ice.")

def get_grid(out):
    fid = "18vdv-2Ku6r_7gNphzlYBl-Fs8aeWp4L1"
    gdd.download_file_from_google_drive(file_id=fid,
                                    dest_path=out,
                                    showsize=True,
                                    overwrite=False)