import logging

import ciocore.exceptions
from ciocore import loggeria


logger = logging.getLogger(
    "{}.uploader".format(loggeria.CONDUCTOR_LOGGER_NAME))


class ThreadQueueJob():
    """
    This class is a data structure that holds all the necessary information for
    file upload jobs that are progressing through all the workers in the uploader 
    module.
    """

    def __init__(self, path, md5, project=None):

        self.path = path
        self.file_md5 = md5 # MD5 of the file as it currently exists on disk

        self.file_size = None # In bytes
        self.upload_type = None # Single part vs multi part
        self.already_uploaded = False # Has this file already been uploaded to Conductor?
        self.project = project # The Conductor Project that this job belongs to

        self.file_upload_id = None  # This is different than the ID for the Upload entity
        self._parts = [] # If it's a multi-part upload, this holds the parts info
        self.total_parts = None # The total number of parts for a multi-part upload

        self.presigned_url = None # The presigned URL to upload to
        self.part_index = None # If multi-part, this is the part number/index
        self.kms_key_name = None # KMS Key name, if applicable    
        self.etag = None # ETag returned from upload, only for multi-part uploads

    def set_parts(self, parts):
        """
        Sets the parts information for a multi-part upload.

        Args:
            parts (list): A list of parts information, each part is a dict with
                            'partNumber' and 'url' keys.
        """
        self._parts = parts
        self.total_parts = len(parts)

    def get_parts(self):
        """
        Returns a list of all the parts.

        Return: A list of parts information, each part is a dict with
                'partNumber' and 'url' keys.
    
        """
        return self._parts

    def create_multipart_jobs(self):
        """
        Create a new ThreadQueueJob for each part of the multipart upload. All
        the details that are common to all parts are copied into each new
        ThreadQueueJob

        Yields: 
            A new ThreadQueueJob
        """

        for part in self.get_parts():

            part_job = ThreadQueueJob(path=self.path,
                                      md5=self.file_md5)

            part_job.file_size = self.file_size
            part_job.upload_type = self.upload_type
            part_job.file_upload_id = self.file_upload_id
            part_job.alredy_uploaded = self.already_uploaded

            part_job.part_size = self.part_size
            part_job.total_parts = self.total_parts
            part_job.kms_key_name = self.kms_key_name

            part_job.presigned_url = part['url']
            part_job.part_index = part['partNumber']
            logger.debug("Created part for ({}) part number {} (etag: {})".format(self.path, part['partNumber'], part.get('etag', 'N/A')))
            yield part_job

    def is_multipart(self):
        return self.upload_type == "multiPartURLs"

    def is_vendor_aws(self):

        if self.presigned_url is None:
            raise ciocore.exceptions.UploadError(
                "Presigned URL is None, cannot determine vendor."
            )
        
        return "amazonaws" in self.presigned_url

    def is_vendor_cw(self):

        if self.presigned_url is None:
            raise ciocore.exceptions.UploadError(
                "Presigned URL is None, cannot determine vendor."
            )        
        
        return "coreweave" in self.presigned_url
    
    def is_vendor_gcp(self):

        if self.presigned_url is None:
            raise ciocore.exceptions.UploadError(
                "Presigned URL is None, cannot determine vendor."
            )        
        
        return "gcp" in self.presigned_url    

    def __str__(self):
        return "<STR: {} ({})>".format(self.path, self.file_md5)

    def __repr__(self):
        return "<REPR: {} ({})>".format(self.path, self.file_md5)

    @staticmethod
    def format_for_upload_request(jobs):
        """
        Given a list of ThreadQueueJobs, create the expected json-compatible
        structure expected by the AE endpoint to generate pre-signed URLs

        Args:
            jobs (list): A list of ThreadQueueJobs objects

        Returns:
            A list of dicts (keys: path, hash, size) for each ThreadQueueJob
        """

        request_data_struct = []

        for job in jobs:
            request_data_struct.append(
                {
                    "path": job.path,
                    "hash": job.file_md5,
                    "size": job.file_size,
                }
            )

        return request_data_struct

    @staticmethod
    def aggregate_parts(parts):
        """
        Given a list of ThreadQueueJobs's (that represent the parts of a single
        file) create the expected json-compatible structure expected by the AE 
        endpoint to generate pre-signed URLs

        Args:
            jobs (list): A list of ThreadQueueJobs objects

        Returns:
            A list of dicts (keys: path, hash, size) for each ThreadQueueJob

        Helper function to take all the parts of a multipart upload and put 
        them into a format that's expected for the HTTP call.
        """

        completed_parts_payload = []

        for part in parts:
            completed_parts_payload.append({'partNumber': part.part_index,
                                            'etag': part.etag}
                                           )

        # AWS requires part numbers to be in ascending order
        completed_parts_payload.sort(key=lambda x: x['partNumber'])

        return completed_parts_payload