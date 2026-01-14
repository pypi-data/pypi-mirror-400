import datetime
import json
import logging
import os
import pathlib
import requests.exceptions
import sys
import time
import threading
import traceback

import ciocore
from ciocore import (
    api_client,
    client_db,
    common,
    config,
    file_utils,
    loggeria,
    worker,
    exceptions,
)

from . import thread_queue_job

from .upload_stats import UploadStats

logger = logging.getLogger(
    "{}.uploader".format(loggeria.CONDUCTOR_LOGGER_NAME))


class MD5Worker(worker.ThreadWorker):
    """
    This worker will pull filenames from in_queue and compute it's base64 encoded
    md5, which will be added to out_queue
    """

    def __init__(self, *args, **kwargs):
        # The location of the sqlite database. If None, it will degault to a value
        self.md5_caching = kwargs.get("md5_caching")
        self.database_filepath = kwargs.get("database_filepath")
        super(MD5Worker, self).__init__(*args, **kwargs)

    def do_work(self, job, thread_int):
        logger.debug("job is %s", job)

        current_md5, cache_hit = self.get_md5(job.path)

        # if a submission time md5 was provided then check against it
        if job.file_md5:
            logger.info(
                "Enforcing md5 match: %s for: %s", job.file_md5, job.path
            )
            if current_md5 != job.file_md5:
                message = "MD5 of %s has changed since submission\n" % job.path
                message += "submitted md5: %s\n" % job.file_md5
                message += "current md5:   %s\n" % current_md5
                message += (
                    "This is likely due to the file being written to after the user"
                )
                message += " submitted the job but before it got uploaded to conductor"
                logger.error(message)
                raise exceptions.UploadError(message)

        else:
            job.file_md5 = current_md5

        self.metric_store.set_dict("file_md5s", job.path, current_md5)
        self.metric_store.set_dict("file_md5s_cache_hit", job.path, cache_hit)
        job.file_size = os.path.getsize(job.path)

        return job

    def get_md5(self, filepath):
        """
        For the given filepath, return a tuple of its md5 and whether the cache was used.

        Use the sqlite db cache to retrive this (if the cache is valid), otherwise generate the md5
        from scratch
        """

        cache_hit = True

        # If md5 caching is disable, then just generate the md5 from scratch
        if not self.md5_caching:
            cache_hit = False
            return common.generate_md5(filepath, poll_seconds=5), cache_hit

        # Otherwise attempt to use the md5 cache
        file_info = get_file_info(filepath)
        file_cache = client_db.FilesDB.get_cached_file(
            file_info, db_filepath=self.database_filepath, thread_safe=True
        )
        if not file_cache:
            cache_hit = False
            logger.debug("No md5 cache available for file: %s", filepath)
            md5 = common.generate_md5(filepath, poll_seconds=5)
            file_info["md5"] = md5
            self.cache_file_info(file_info)
            return md5, cache_hit

        logger.debug("Using md5 cache for file: %s", filepath)
        return file_cache["md5"], cache_hit

    def cache_file_info(self, file_info):
        """
        Store the given file_info into the database
        """
        client_db.FilesDB.add_file(
            file_info, db_filepath=self.database_filepath, thread_safe=True
        )


class MD5OutputWorker(worker.ThreadWorker):
    """
    This worker will batch the computed md5's into self.batch_size chunks. It will send a partial
    batch after waiting self.wait_time seconds
    """

    def __init__(self, *args, **kwargs):
        super(MD5OutputWorker, self).__init__(*args, **kwargs)
        self.batch_size = 20  # the controls the batch size for http get_signed_urls
        self.wait_time = 2
        self.batch = {}

    def check_for_poison_pill(self, job):
        """we need to make sure we ship the last batch before we terminate"""
        if job == self.PoisonPill():
            logger.debug("md5outputworker got poison pill")
            self.ship_batch()
            super(MD5OutputWorker, self).check_for_poison_pill(job)

    # helper function to ship batch
    def ship_batch(self):
        if self.batch:
            logger.debug("sending batch: %s", self.batch)
            self.put_job(self.batch)
            self.batch = {}

    @common.dec_catch_exception(raise_=True)
    def target(self, thread_int):
        while not common.SIGINT_EXIT:
            job = None

            try:
                logger.debug("Worker querying for job")
                job = self.in_queue.get(block=True, timeout=self.wait_time)
                logger.debug("Got job")
                queue_size = self.in_queue.qsize()

            except:
                logger.debug("No jobs available")

                if self._job_counter.value >= self.task_count:
                    if self.batch:
                        self.ship_batch()

                    logger.debug(
                        "Worker has completed all of its tasks (%s)", job)
                    self.thread_complete_counter.decrement()
                    break

                elif self._job_counter.value == 0:
                    logger.debug("Worker waiting for first job")

                time.sleep(1)
                continue

            logger.debug("Worker got job %s", job)
            self._job_counter.increment()
            logger.debug(
                "Processing Job '%s' #%s on %s. %s tasks remaining in queue",
                job,
                self._job_counter.value,
                self,
                queue_size,
            )

            try:
                self.check_for_poison_pill(job)

                # add file info to the batch list
                self.batch[job.path] = job

                # if the batch is self.batch_size, ship it
                if len(self.batch) == self.batch_size:
                    self.ship_batch()

                # mark this task as done
                self.mark_done()

            except Exception as exception:
                logger.exception(
                    'CAUGHT EXCEPTION on job "%s" [%s]:\n', job, self)

                # if there is no error queue to dump data into, then simply raise the exception
                if self.error_queue is None:
                    raise

                self.error_queue.put(sys.exc_info())
                # exit the while loop to stop the thread
                break


class HttpBatchWorker(worker.ThreadWorker):
    """
    This worker recieves a list of ThreadQueue Jobs with path, hash, size attributes. It generates
    the request to the back-end to get signed upload urls for each file in the batch. The result
    can be a mix of multi-part and single-part upload urls - each one has a unique set of data.

    If a requested file isn't part of the result, it indicates that it already exists on the bucket
    and hence has been previously uploaded.

    This will will add values for upload_type, presigned_url, part_size, parts, kms_key_name and 
    upload_id (of the file - NOT the Upload entity) to each job.
    """

    def __init__(self, *args, **kwargs):
        super(HttpBatchWorker, self).__init__(*args, **kwargs)
        self.api_client = api_client.ApiClient()

    def make_request(self, jobs):
        uri_path = "/api/v2/files/get_upload_urls"
        headers = {"Content-Type": "application/json"}
        data = {"upload_files": thread_queue_job.ThreadQueueJob.format_for_upload_request(jobs.values()),
                "project": list(jobs.values())[0].project}

        response_str, response_code = self.api_client.make_request(
            uri_path=uri_path,
            verb="POST",
            headers=headers,
            data=json.dumps(data),
            raise_on_error=True,
            use_api_key=True,
        )

        if response_code == 200:
            url_list = json.loads(response_str)
            return url_list

        if response_code == 204:
            return None

        raise exceptions.UploadError(
            "%s Failed request to: %s\n%s" % (
                response_code, uri_path, response_str)
        )

    def do_work(self, jobs, thread_int):
        logger.debug("Getting upload urls for %s", jobs)
        result = self.make_request(jobs)
        logger.debug("Got result: %s", result)

        # Determine which files have already been uploaded by looking at the difference between
        # the file paths in job and the file paths returned by the request. Only files that need
        # to be uploaded are returned by the request.
        # Ideally, the MD5 would be used as the key but because the MD5 isn't returned for single-
        # part files, we have to use the file path instead.
        if result:
            for upload_type, items in result.items():
                for item in items:

                    job_key = item["filePath"]

                    logger.debug("Matching %s in request", job_key)

                    jobs[job_key].upload_type = upload_type
                    jobs[job_key].kms_key_name = result.get('kmsKeyName')

                    self.metric_store.increment(
                        "bytes_to_upload", jobs[job_key].file_size, item["filePath"])
                    self.metric_store.increment("num_files_to_upload")

                    if upload_type == "multiPartURLs":
                        jobs[job_key].part_size = item["partSize"]
                        jobs[job_key].set_parts(item["parts"])
                        jobs[job_key].file_upload_id = item.get("uploadID")

                    elif upload_type == "singlePartURLs":
                        jobs[job_key].presigned_url = item["preSignedURL"]

                    else:
                        raise exceptions.UploadError("Unknown upload_type '{}' for {}".format(upload_type,
                                                                                              item))

        # If a job has no upload_type, it indicates it wasn't part of the result
        # above and has already been uploaded.
        # If it's a multipart job we need to split it into a job per part (to allow
        # for parallelization of the uploads).
        for job_count, job in enumerate(jobs.values()):

            if job.upload_type is None:
                job.already_uploaded = True
                self.metric_store.increment("already_uploaded", True, job.path)

            if job.is_multipart():
                logger.debug(
                    "Job is multipart: %s, splitting parts into separate jobs", job)
                for part_job in job.create_multipart_jobs():
                    self.put_job(part_job)

            else:
                logger.debug("Job is singlepart: %s, adding to out_queue", job)
                self.put_job(job)

            # The job counter is already incremented in target() once, so skip the first
            # iteration
            if job_count > 0:
                self._job_counter.increment()

        return None


class UploadWorker(worker.ThreadWorker):
    """
    This worker receives a thread_queue_job.ThreadQueueJob and performs the upload.
    """

    def __init__(self, *args, **kwargs):
        super(UploadWorker, self).__init__(*args, **kwargs)
        self.chunk_size = 1048576  # 1M
        self.report_size = 10485760  # 10M
        self.api_client = api_client.ApiClient()

    def chunked_reader(self, filename):
        with open(filename, "rb") as fp:
            while worker.WORKING and not common.SIGINT_EXIT:
                data = fp.read(self.chunk_size)
                if not data:
                    # we are done reading the file
                    break
                # TODO: can we wrap this in a retry?
                yield data

                # report upload progress
                self.metric_store.increment(
                    "bytes_uploaded", len(data), filename)

    def do_work(self, job, thread_int):

        if not job:
            return worker.EMPTY_JOB            

        if job.already_uploaded:
            logger.debug("Job is already uploaded: %s", job.path)
            return job

        try:
            if job.is_multipart():
                return self.do_multipart_upload(job)

            else:
                return self.do_singlepart_upload(job)

        except Exception as err_msg:
            real_md5 = common.get_base64_md5(job.path)

            # Gather helpful details from the exception
            exc_tb = sys.exc_info()[2]
            exception_line_num = exc_tb.tb_lineno
            exception_file = pathlib.Path(
                exc_tb.tb_frame.f_code.co_filename).name

            if isinstance(err_msg, requests.exceptions.HTTPError):
                error_message = f"Upload of {job.path} failed with a response code {err_msg.response.status_code} ({err_msg.response.reason}) (expected '{job.file_md5}', got '{real_md5}')"
            else:
                error_message = (
                    f"Upload of {job.path} failed. (expected '{job.file_md5}', got '{real_md5}') {str(err_msg)} [{exception_file}-{exception_line_num}]"
                )

            raise exceptions.UploadError(error_message)

    @common.DecRetry(retry_exceptions=api_client.CONNECTION_EXCEPTIONS, tries=5)
    def do_singlepart_upload(self, job):
        """
        Note that for GCS we don't rely on the make_request's own retry mechanism because we need to
        recreate the chunked_reader generator before retrying the request. Instead, we wrap this
        method in a retry decorator.

        We cannot reuse make_request method for S3 because it adds auth and Transfer-Encoding
        headers that S3 does not accept.
        """

        if job.is_vendor_aws() or job.is_vendor_cw():
            # must declare content-length ourselves due to zero byte bug in requests library.
            # api_client.make_prepared_request docstring.
            headers = {
                "Content-Type": "application/octet-stream",
                "Content-Length": str(job.file_size),
            }

            with open(job.path, "rb") as fh:
                # TODO: support chunked
                response = self.api_client.make_prepared_request(
                    verb="PUT",
                    url=job.presigned_url,
                    headers=headers,
                    params=None,
                    data=fh,
                    tries=1,
                    # s3 will return a 501 if the Transfer-Encoding header exists
                    remove_headers_list=["Transfer-Encoding"],
                )

                # close response object to add back to pool, since no body is being read
                # https://requests.readthedocs.io/en/master/user/advanced/#body-content-workflow
                response.close()

                # report upload progress
                self.metric_store.increment(
                    "bytes_uploaded", job.file_size, job.path)

        else:
            headers = {"Content-MD5": job.file_md5,
                       "Content-Type": "application/octet-stream"}

            if job.kms_key_name is not None:
                headers["x-goog-encryption-kms-key-name"] = job.kms_key_name

            response = self.api_client.make_request(
                conductor_url=job.presigned_url,
                headers=headers,
                data=self.chunked_reader(job.path),
                verb="PUT",
                tries=1,
                use_api_key=True,
            )

        logger.debug("Response from upload: %s", response)

        return job

    def do_multipart_upload(self, job):
        """
        Files will be split into partSize returned by the FileAPI and hydrated once all parts are
        uploaded. On successful part upload, response headers will contain an ETag. This value must
        be tracked along with the part number in order to complete and hydrate the file.
        """

        resp_headers = self._do_multipart_upload(job)

        if resp_headers:
            job.etag = resp_headers["ETag"].strip('"')

        return job

    @common.DecRetry(retry_exceptions=api_client.CONNECTION_EXCEPTIONS, tries=5)
    def _do_multipart_upload(self, job):

        with open(job.path, "rb") as fh:
            # seek to the correct part position
            start = (job.part_index - 1) * job.part_size
            fh.seek(start)

            # read up to part size determined by file-api
            data = fh.read(job.part_size)
            content_length = len(data)

            # upload part
            response = self.api_client.make_prepared_request(
                verb="PUT",
                url=job.presigned_url,
                headers={"Content-Type": "application/octet-stream"},
                params=None,
                data=data,
                tries=1,
                remove_headers_list=[
                    "Transfer-Encoding"
                ],  # s3 will return a 501 if the Transfer-Encoding header exists
            )

            # report upload progress
            self.metric_store.increment(
                "bytes_uploaded", content_length, job.path)

            # close response object to add back to pool
            # https://requests.readthedocs.io/en/master/user/advanced/#body-content-workflow
            response.close()

            logger.debug("Response from multipart upload: %s", response)

            return response.headers


class MultiPartSiphonWorker(worker.ThreadWorker):
    """
    This class is responsible for gathering all the jobs (aka files) and ensuring
    the necessary steps are taken to have them available to be used by a Conductor Job.

    For single-part files, this simply means passing the job to the out_queue so 
    that the Uploader is aware that the file has been sucesfully uploaded.

    For multi-part files, this means collecting all the parts together and then
    sending a request to the backend indicating that the file is complete.
    """

    def __init__(self, *args, **kwargs):
        super(MultiPartSiphonWorker, self).__init__(*args, **kwargs)

        self.api_client = api_client.ApiClient()
        self.multipart_siphon = {}

    def do_work(self, job, thread_int):
        """
        Process files that have already been uploaded.

        If it's a single-part file, add the job to the out queue, so that it can
        be used to determine if the Upload entity is complete.

        If it's a multi-part upload, collect all the parts together. Once all the
        parts have been accumulated, mark it as complete and add the file to the
        out queue.
        """

        if not job:
            return None

        if not job.is_multipart():
            logger.debug("Job is not multipart (%s, %s)",
                         job.total_parts, job.part_index)
            
            return job

        if job.file_md5 not in self.multipart_siphon:
            self.multipart_siphon[job.file_md5] = []

            # Add to the task count for this worker.
            # -1 because a task has already been added for a single file
            # but not all its parts.
            old_task_count = self.task_count
            self.task_count += job.total_parts - 1
            logger.debug("Incrementing task count to %s from %s",
                            self.task_count, old_task_count)

        self.multipart_siphon[job.file_md5].append(job)

        if len(self.multipart_siphon[job.file_md5]) == job.total_parts:

            complete_payload = {
                "uploadID": job.file_upload_id,
                "hash": job.file_md5,
                "completedParts": thread_queue_job.ThreadQueueJob.aggregate_parts(self.multipart_siphon[job.file_md5]),
                "project": job.project,
            }

            # Complete multipart upload in order to hydrate file for availability
            logger.debug("Complete payload: %s", complete_payload)
            uri_path = "/api/v2/files/multipart/complete"
            headers = {"Content-Type": "application/json"}
            self.api_client.make_request(
                uri_path=uri_path,
                verb="POST",
                headers=headers,
                data=json.dumps(complete_payload),
                raise_on_error=True,
                use_api_key=True,
            )

            logger.debug("JSON payload: '%s'",
                            json.dumps(complete_payload))
            
            for job_part in self.multipart_siphon[job.file_md5]:
                self.put_job(job_part)

            return None

    def is_complete(self):
        # Get the number of files already uploaded as they are not passed to the Upload
        # worker
        file_store = self.metric_store.get("files")

        if isinstance(file_store, dict):
            already_completed_uploads = len(
                [x for x in file_store.values() if x["already_uploaded"]]
            )
            queue_size = self.out_queue.qsize()
            logger.debug(
                "Is complete? out_queue_size=%s, completed_uploads=%s, task_count=%s",
                queue_size,
                already_completed_uploads,
                self.task_count,
            )

            return (queue_size) >= self.task_count

        else:
            logger.debug("Is complete?: Files not initialized yet")
            return False


class Uploader(object):
    sleep_time = 10

    CLIENT_NAME = "Uploader"

    def __init__(self, args=None):
        logger.debug("Uploader.__init__")
        self.api_client = api_client.ApiClient()
        self.args = args or {}
        logger.debug("args: %s", self.args)

        self.location = self.args.get("location")
        self.project = self.args.get("project")
        self.progress_callback = None
        self.cancel = False
        self.error_messages = []
        self.num_files_to_process = 0

        self.report_status_thread = None
        self.monitor_status_thread = None

    def emit_progress(self, upload_stats):
        if self.progress_callback:
            self.progress_callback(upload_stats)

    def prepare_workers(self):
        logger.debug("preparing workers...")

        if isinstance(threading.current_thread(), threading._MainThread):
            common.register_sigint_signal_handler()
        
        self.manager = None

    def create_manager(self):
        job_description = [
            (
                MD5Worker,
                [],
                {
                    "thread_count": self.args["thread_count"],
                    "database_filepath": self.args["database_filepath"],
                    "md5_caching": self.args["md5_caching"],
                },
            ),
            (MD5OutputWorker, [], {"thread_count": 1}),
            (HttpBatchWorker, [], {"thread_count": 1}),
            (UploadWorker, [], {"thread_count": self.args["thread_count"]}),
            (MultiPartSiphonWorker, [], {"thread_count": 1})
        ]

        manager = worker.JobManager(job_description)
        return manager

    @common.dec_catch_exception(raise_=True)
    def report_status(self):
        logger.debug("started report_status thread")
        update_interval = 15
        while True:
            # don't report status if we are doing a local_upload
            if not self.upload_id:
                logger.debug(
                    "not updating status as we were not provided an upload_id")
                return

            if self.working:
                bytes_to_upload = self.manager.metric_store.get(
                    "bytes_to_upload")
                bytes_uploaded = self.manager.metric_store.get(
                    "bytes_uploaded")
                try:
                    status_dict = {
                        "upload_id": self.upload_id,
                        "transfer_size": bytes_to_upload,
                        "bytes_transfered": bytes_uploaded,
                    }
                    logger.debug("reporting status as: %s", status_dict)
                    self.api_client.make_request(
                        "/uploads/%s/update" % self.upload_id,
                        data=json.dumps(status_dict),
                        verb="POST",
                        use_api_key=True,
                    )

                except Exception:
                    logger.error("could not report status:")
                    logger.error(traceback.print_exc())
                    logger.error(traceback.format_exc())

            else:
                break

            time.sleep(update_interval)

    def create_report_status_thread(self):
        logger.debug("creating reporter thread")
        self.report_status_thread = threading.Thread(
            name="ReporterThread", target=self.report_status
        )
        self.report_status_thread.daemon = True
        self.report_status_thread.start()

    @common.dec_catch_exception(raise_=True)
    def monitor_status(self, progress_handler):
        logger.debug("starting monitor_status thread")
        update_interval = 5

        def sleep():
            time.sleep(update_interval)

        while True:
            if self.working:
                try:
                    upload_stats = UploadStats.create(
                        self.manager.metric_store,
                        self.num_files_to_process,
                        self.job_start_time,
                    )
                    progress_handler(upload_stats)
                except Exception as e:
                    print(e)
                    print(traceback.format_exc())

            else:
                break
            sleep()

    def create_monitor_status_thread(self):
        logger.debug("creating console status thread")
        self.monitor_status_thread = threading.Thread(
            name="PrintStatusThread",
            target=self.monitor_status,
            args=(self.emit_progress,),
        )

        # make sure threads don't stop the program from exiting
        self.monitor_status_thread.daemon = True

        # start thread
        self.monitor_status_thread.start()

    def mark_upload_finished(self, upload_id, upload_files):
        data = {
            "upload_id": upload_id,
            "status": "server_pending",
            "upload_files": upload_files,
        }

        self.api_client.make_request(
            "/uploads/%s/finish" % upload_id,
            data=json.dumps(data),
            verb="POST",
            use_api_key=True,
        )
        return True

    def mark_upload_failed(self, error_message, upload_id):
        logger.error("Upload failed: %s", error_message)

        # report error_message to the app
        self.api_client.make_request(
            "/uploads/%s/fail" % upload_id,
            data=error_message,
            verb="POST",
            use_api_key=True,
        )

        return True

    def assets_only(self, *paths):
        processed_filepaths = file_utils.process_upload_filepaths(paths)
        file_map = {path: None for path in processed_filepaths}
        self.handle_upload_response(project=None, upload_files=file_map)

        if common.SIGINT_EXIT or self.cancel:
            print("\nUpload cancelled\n")

        elif self.error_messages:
            print("\nUpload of {} file completed with errors\n".format(len(file_map)))

        else:
            print("\nUpload of {} file completed\n".format(len(file_map)))

        error_messages = []

        for exception in self.error_messages:
            error_messages.append(str(exception[1]))
            traceback_message = "".join(
                traceback.format_exception(None, exception[1], exception[2]))
            print(traceback_message)
            logger.error(traceback_message)

        if error_messages:

            log_file = loggeria.LOG_PATH
            sys.stderr.write("\nError uploading files:\n")

            for err_msg in error_messages:
                sys.stderr.write("\t{}\n".format(err_msg))

            sys.stderr.write(
                "\nSee log {} for more details\n\n".format(log_file))

        self.error_messages = []

    def handle_upload_response(self, project, upload_files, upload_id=None):
        """
        This is a really confusing method and should probably be split into to clear logic
        branches: one that is called when in daemon mode, and one that is not. If not called in
        daemon mode (local_upload=True), then md5_only is True and project is not None.Otherwise
        we're in daemon mode, where the project information is not required because the daemon will
        only be fed uploads by the app which have valid projects attached to them.
        """
        try:
            logger.info("%s", "  NEXT UPLOAD  ".center(30, "#"))
            logger.info("project: %s", project)
            logger.info("upload_id is %s", upload_id)
            logger.info(
                "upload_files %s:(truncated)\n\t%s",
                len(upload_files),
                "\n\t".join(list(upload_files)[:5]),
            )

            # reset counters
            self.num_files_to_process = len(upload_files)
            logger.debug("Processing %s files", self.num_files_to_process)
            self.job_start_time = datetime.datetime.now()
            self.upload_id = upload_id
            self.job_failed = False

            # signal the reporter to start working
            self.working = True

            self.prepare_workers()

            # Adjust the number of threads
            if self.num_files_to_process < self.args["thread_count"]:
                self.args["thread_count"] = min(self.args["thread_count"], self.num_files_to_process)
                logger.info(
                    "Adjusting thread count to %s", self.args["thread_count"]
                )

            # create worker pools
            self.manager = self.create_manager()
            self.manager.start()

            # create reporters
            logger.debug("creating report status thread...")
            self.create_report_status_thread()

            # load tasks into worker pools
            for path in upload_files:
                md5 = upload_files[path]
                self.manager.add_task((path, md5, project))

            logger.info("creating console status thread...")
            self.create_monitor_status_thread()

            # wait for work to finish
            while not self.manager.is_complete():
                logger.debug(
                    "Manager is running, cancel requested?: %s", self.cancel)

                if self.cancel or self.manager.error or common.SIGINT_EXIT:
                    self.error_messages = self.manager.stop_work()
                    logger.debug("Manager sucesfully stopped")
                    break

                time.sleep(5)

            # Shutdown the manager once all jobs are done
            if not (self.cancel or self.manager.error or common.SIGINT_EXIT):
                self.manager.join()

            upload_stats = UploadStats.create(
                self.manager.metric_store,
                self.num_files_to_process,
                self.job_start_time,
            )
            logger.info(upload_stats.get_formatted_text())
            self.emit_progress(upload_stats)

            logger.debug("Error_message: %s", self.error_messages)

            # signal to the reporter to stop working
            self.working = False

            logger.debug("Waiting for reporter status thread to join")
            self.report_status_thread.join()

            logger.debug("Waiting for print status thread to join")
            self.monitor_status_thread.join()

            #  Despite storing lots of data about new uploads, we will only send back the things
            #  that have changed, to keep payloads small.
            finished_upload_files = {}
            if self.upload_id and not self.error_messages:
                md5s = self.return_md5s()
                for path in md5s:
                    finished_upload_files[path] = {
                        "source": path, "md5": md5s[path]}

                self.mark_upload_finished(
                    self.upload_id, finished_upload_files)

        except:
            self.error_messages.append(sys.exc_info())

    def main(self, run_one_loop=False):
        def show_ouput(upload_stats):
            print(upload_stats.get_formatted_text())
            logger.info("File Progress: %s", upload_stats.file_progress)

        self.progress_callback = show_ouput

        logger.info("Uploader Started. Checking for uploads...")

        waiting_for_uploads_flag = False

        while not common.SIGINT_EXIT:
            try:
                # TODO: we should pass args as url params, not http data
                data = {}
                data["location"] = self.location
                logger.debug("Data: %s", data)
                resp_str, resp_code = self.api_client.make_request(
                    "/uploads/client/next",
                    data=json.dumps(data),
                    verb="PUT",
                    use_api_key=True,
                )
                if resp_code == 204:
                    if not waiting_for_uploads_flag:
                        sys.stdout.write("\nWaiting for jobs to upload ")
                        sys.stdout.flush()

                    logger.debug("no files to upload")
                    sys.stdout.write(".")
                    sys.stdout.flush()
                    time.sleep(self.sleep_time)
                    waiting_for_uploads_flag = True
                    continue

                elif resp_code != 201:
                    logger.error(
                        "received invalid response code from app %s", resp_code
                    )
                    logger.error("response is %s", resp_str)
                    time.sleep(self.sleep_time)
                    continue

                print("")  # to make a newline after the 204 loop

                try:
                    json_data = json.loads(resp_str)
                    upload = json_data.get("data", {})

                except ValueError:
                    logger.error("response was not valid json: %s", resp_str)
                    time.sleep(self.sleep_time)
                    continue

                upload_files = upload["upload_files"]
                upload_id = upload["id"]
                project = upload["project"]

                self.handle_upload_response(project, upload_files, upload_id)

                if self.error_messages:
                    logger.info("Upload of entity %s failed with errors.", upload_id)

                else:
                    logger.info("Upload of entity %s completed.", upload_id)
                
                upload_stats = UploadStats.create(
                    self.manager.metric_store,
                    self.num_files_to_process,
                    self.job_start_time,
                )
                show_ouput(upload_stats)
                logger.debug(self.manager.worker_queue_status_text())

                error_messages = []

                for exception in self.error_messages:
                    error_messages.append(str(exception[1]))

                if error_messages:
                    self.mark_upload_failed(
                        error_message="Uploader ERROR: {}".format(
                            "\n".join(error_messages)),
                        upload_id=upload_id
                    )

                    log_file = loggeria.LOG_PATH
                    sys.stderr.write("\nError uploading files:\n")

                    for err_msg in error_messages:
                        sys.stderr.write("\t{}\n".format(err_msg))

                    sys.stderr.write(
                        "\nSee log {} for more details\n\n".format(log_file))

                self.error_messages = []

                waiting_for_uploads_flag = False

            except KeyboardInterrupt:
                logger.info("ctrl-c exit")
                break
            except Exception as err_msg:
                logger.exception("Caught exception:\n%s", err_msg)
                time.sleep(self.sleep_time)
                continue

        logger.info("exiting uploader")

    def return_md5s(self):
        """
        Return a dictionary of the filepaths and their md5s that were generated
        upon uploading
        """
        return self.manager.metric_store.get_dict("file_md5s")


def run_uploader(args):
    """
    Start the uploader process. This process will run indefinitely, polling
    the Conductor cloud app for files that need to be uploaded.
    """
    # convert the Namespace object to a dictionary
    args_dict = vars(args)
    cfg = config.config().config

    api_client.ApiClient.register_client(
        client_name=Uploader.CLIENT_NAME, client_version=ciocore.version
    )

    # Set up logging
    log_level_name = args_dict.get("log_level") or cfg["log_level"]

    loggeria.setup_conductor_logging(
        logger_level=loggeria.LEVEL_MAP.get(log_level_name),
        log_dirpath=args_dict.get("log_dir"),
        log_filename="conductor_uploader.log",
        disable_console_logging=not args_dict["log_to_console"],
        use_system_log=False,
    )

    print("Logging to %s", loggeria.LOG_PATH)

    logger.debug("Uploader parsed_args is %s", args_dict)

    resolved_args = resolve_args(args_dict)
    uploader = Uploader(resolved_args)

    if args.paths:
        processed_filepaths = file_utils.process_upload_filepaths(
            args.paths[0])
        file_map = {path: None for path in processed_filepaths}
        uploader.handle_upload_response(project=None, upload_files=file_map)

    else:
        uploader.main()


def get_file_info(filepath):
    """
    For the given filepath return the following information in a dictionary:

        "filepath": filepath (str)
        "modtime": modification time (datetime.datetime)
        "size": filesize in bytes (int)

    """
    assert os.path.isfile(filepath), "Filepath does not exist: %s" % filepath
    stat = os.stat(filepath)
    modtime = datetime.datetime.fromtimestamp(stat.st_mtime)

    return {"filepath": filepath, "modtime": modtime, "size": stat.st_size}


def resolve_args(args):
    """
    Resolve all arguments, reconciling differences between command line args and config.yml args.
    See resolve_arg function.
    """

    args["md5_caching"] = resolve_arg("md5_caching", args)
    args["database_filepath"] = resolve_arg("database_filepath", args)
    args["location"] = resolve_arg("location", args)
    args["thread_count"] = resolve_arg("thread_count", args)

    return args


def resolve_arg(key, args):
    """
    If the key doesn't exist (or is None), grab it from the config.
    """

    cfg = config.config().config
    config_value = cfg.get(key)

    value = args.get(key, config_value)

    if value is None:
        value = config_value

    return value
