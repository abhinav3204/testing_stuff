from google.cloud import storage
from zipfile import ZipFile
from zipfile import is_zipfile
import io
from multiprocessing import Pool
import time

def zipextract(bucketname, zipfilename_with_path, destination_blob_pathname):

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucketname)

    destination_blob_pathname = destination_blob_pathname
    
    blob = bucket.blob(zipfilename_with_path)
    zipbytes = io.BytesIO(blob.download_as_string())

    if is_zipfile(zipbytes):
        with ZipFile(zipbytes, 'r') as myzip:
            for contentfilename in myzip.namelist():
                print(contentfilename)
                contentfile = myzip.read(contentfilename)
                blob = bucket.blob(destination_blob_pathname + "/" + contentfilename)
                blob.upload_from_string(contentfile)
                print("Completed")

#gs://nsefno-historical-data/unzipped/2022/MAR_2022/GFDLNFO_TICK_02032022.zip
# gs://nsefno-historical-data/unzipped/2022/MAR_2022/GFDLNFO_TICK_02032022.zip

def main():
    tic = time.perf_counter
    zipextract("nsefno-historical-data", "2022/MAR_2022/GFDLNFO_TICK_02032022.zip", 
                "unzipped/2022/MAR_2022") # if the file is gs://mybucket/path/file.zip
    toc = time.perf_counter
    print("Total time: " + str(toc-tic))

if __name__ == "__main__":
    main()
