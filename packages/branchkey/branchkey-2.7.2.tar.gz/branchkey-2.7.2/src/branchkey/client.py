import json
import logging
import os
import warnings
from http import HTTPStatus
from queue import LifoQueue
from time import sleep

import numpy as np
import requests

from .__consumer import Consumer
from .utils import AGGREGATED_OUTPUT_DIR, FILE_METADATA


class Client:
    def __init__(
        self,
        credentials: dict,
        host: str = "https://app.branchkey.com",
        rbmq_host: str = None,
        rbmq_port: int = 5671,
        rbmq_ssl: bool = True,
        ssl: bool = True,
        wait_for_run: bool = False,
        run_check_interval_s: int = 30,
        proxies: dict = None,
    ):
        if credentials is None:
            credentials = dict(
                name="guest",
                id="guest",
                session_token="guest",
                tree_id="guest",
                branch_id="guest",
                owner_id="guest",
            )
        self.__leaf_name = credentials["name"]
        self.__leaf_id = credentials["id"]
        self.__leaf_session_token = credentials["session_token"]
        self.__tree_id = credentials["tree_id"]
        self.__branch_id = credentials["branch_id"]
        self.__user_id = credentials["owner_id"]
        self.__status = "authenticated"

        self.__api_host = host
        self.__proxies = proxies
        # Verify SSL certs
        self.__verify = ssl

        # Extract hostname from API host for RabbitMQ connection, or use override
        if rbmq_host is not None:
            rabbitmq_host = rbmq_host
        else:
            rabbitmq_host = (
                host.replace("https://", "").replace("http://", "").split("/")[0]
            )

        self.queue = LifoQueue(maxsize=1)
        self.__run_status = None
        self.__run_number = None
        self.__wait_for_run = wait_for_run
        self.__run_check_interval_s = run_check_interval_s

        self.rabbit_credentials = dict(
            leaf_name=self.__leaf_name,
            leaf_id=self.__leaf_id,
            queue_password=self.__leaf_session_token,
            host=rabbitmq_host,
            port=rbmq_port,
            ssl=rbmq_ssl,
            tree_id=self.__tree_id,
            branch_id=self.__branch_id,
        )
        self.consumer = None

        # Start consumer for RabbitMQ messages
        try:
            consumer = Consumer(
                self.rabbit_credentials, self.queue, self.__update_run_status
            )
            self.consumer = consumer.spawn_consumer_thread()
        except Exception as e:
            print(f"Warning: Failed to start RabbitMQ consumer: {e}")

        self.get_run_details()

    def _get_auth_headers(self) -> dict[str, str]:
        """
        Generate Bearer authentication headers for API requests

        Returns:
            dict: Headers with Authorization and accept fields
        """
        return {
            "Authorization": f"Bearer {self.__leaf_id}:{self.__leaf_session_token}",
            "accept": "application/json",
        }

    def get_run_details(self) -> None:
        """
        Fetch current run status and run number from the API

        Updates internal state with run_status and run_number

        Raises:
            Exception: If API request fails or response cannot be parsed
        """
        try:
            url = self.__api_host + "/api/v1/run/" + self.__branch_id
            headers = self._get_auth_headers()
            headers["LEAF"] = "true"

            resp = requests.get(
                url, headers=headers, verify=self.__verify, proxies=self.__proxies
            )

            print(
                f"received resp code from api-gateway for get_run_details: {resp.status_code}"
            )
            if resp.status_code != HTTPStatus.OK:
                raise Exception(resp.json())

            run_details = resp.json()["data"]
            try:
                self.__run_status = run_details["run_status"]
                self.__run_number = run_details["run_number"]
            except Exception as e:
                raise Exception(
                    f"Failed to parse response from get_run_details API: {e}"
                )

        except Exception as e:
            msg = "Getting Run details failed: {}".format(e)
            raise Exception(msg)

    def __update_run_status(self, status):
        self.__run_status = status
        if status == "start":
            self.get_run_details()

    def disable_ssl_verification(self, enabled: bool = False) -> bool:
        """
        Enable or disable SSL certificate verification

        Args:
            enabled: Whether to enable SSL verification

        Returns:
            bool: Current SSL verification state

        Warning:
            Disabling SSL verification is a security risk and not recommended
        """
        warnings.warn(
            "[BranchKey] We highly recommend enabling ssl verification. Use this at your own risk."
        )
        self.__verify = enabled
        return self.__verify

    def convert_pytorch_numpy(
        self, model, weighting: float = 1
    ) -> tuple[float, list[np.ndarray]]:
        """
        Convert PyTorch model parameters to numpy arrays

        Args:
            model: PyTorch model named_parameters() iterator
            weighting: Weight for aggregation (default: 1)
                - Number of training samples (most common)
                - Fixed value for equal weighting
                - Quality score (e.g., validation accuracy)

        Returns:
            tuple: (weighting, list of numpy arrays)

        Example:
            >>> weighting, params = client.convert_pytorch_numpy(
            ...     model.named_parameters(),
            ...     weighting=len(train_dataset)
            ... )
        """
        params = []
        for param in model:
            params.append(param[1].data.cpu().detach().numpy())
        return (weighting, params)

    def save_weights(
        self, file_path: str, weighting: float, parameters: list[np.ndarray]
    ) -> str:
        """
        Save model weights in compressed NPZ format

        Args:
            file_path: Output path (.npz extension added automatically)
            weighting: Weight for aggregation
                - Number of training samples (most common)
                - Fixed value for equal weighting (e.g., 1)
                - Quality-based weight (e.g., validation_accuracy * num_samples)
            parameters: List of numpy arrays containing model parameters

        Returns:
            str: Full file path with .npz extension

        Example:
            >>> file_path = client.save_weights(
            ...     "model_weights",
            ...     weighting=1000,
            ...     parameters=[layer1, layer2, ...]
            ... )
            >>> print(file_path)  # "model_weights.npz"
        """
        if not file_path.endswith(".npz"):
            file_path += ".npz"

        # Create dict for savez_compressed
        arrays_dict = {"weighting": np.array([weighting], dtype=np.float64)}
        for i, arr in enumerate(parameters):
            arrays_dict[f"layer_{i}"] = arr

        np.savez_compressed(file_path, **arrays_dict)
        return file_path

    def validate_weight_shape(self, file) -> bool:
        """
        Validate NPZ file format before uploading to API

        Args:
            file: Binary file object (opened NPZ file)

        Returns:
            bool: True if validation passes

        Raises:
            Exception: If file format is invalid:
                - Missing 'weighting' field
                - Invalid weighting format (must be single value)
                - No layer arrays found
                - Layer arrays are not numpy arrays

        Note:
            File position is reset to beginning after validation
        """
        # Load NPZ without pickle
        data = np.load(file, allow_pickle=False)

        # Check for required 'weighting' field
        if "weighting" not in data.files:
            raise Exception(
                "[validate_weight_shape] Missing 'weighting' field in NPZ file"
            )

        weighting = data["weighting"]
        if weighting.size != 1:
            raise Exception(
                "[validate_weight_shape] 'weighting' must be a single value"
            )

        # Check that there are layer arrays
        layer_keys = [k for k in data.files if k.startswith("layer_")]
        if len(layer_keys) == 0:
            raise Exception("[validate_weight_shape] No layer arrays found in NPZ file")

        # Validate each layer is a numpy array
        for key in layer_keys:
            if not isinstance(data[key], np.ndarray):
                raise Exception(f"[validate_weight_shape] {key} is not a numpy array")

        file.seek(0)
        return True

    def file_upload(self, file_path: str) -> str:
        """
        Upload model weights file to BranchKey server

        Args:
            file_path: Path to NPZ file containing model weights

        Returns:
            str: Unique file ID assigned by server

        Raises:
            Exception: If upload fails or run is blocked

        Note:
            - File is validated before upload
            - Waits for run to start if wait_for_run=True
            - Requires run_status to be "start"

        Example:
            >>> file_path = client.save_weights("model", 1000, parameters)
            >>> file_id = client.file_upload(file_path)
            >>> print(f"Uploaded: {file_id}")
        """
        try:
            if self.__run_status != "start":
                if self.__wait_for_run:
                    while self.__run_status != "start":
                        print(
                            f"run is blocked, going into sleep for {self.__run_check_interval_s} seconds before checking again"
                        )
                        sleep(self.__run_check_interval_s)
                else:
                    raise Exception("run is blocked")

            with open(file_path, mode="rb") as f:
                self.validate_weight_shape(f)

                url = self.__api_host + "/api/v1/file/upload"
                headers = self._get_auth_headers()
                data = {
                    "data": json.dumps(
                        {"leaf_name": self.__leaf_name, "metadata": FILE_METADATA}
                    )
                }
                file = {"file": f}

                resp = requests.post(
                    url,
                    files=file,
                    data=data,
                    headers=headers,
                    verify=self.__verify,
                    proxies=self.__proxies,
                )

                if resp.status_code != HTTPStatus.CREATED:
                    raise Exception(resp.json()["error"])
                else:
                    return resp.json()["data"]["file_id"]

        except Exception as e:
            msg = "File Upload failed for leaf {} for file {}: {}".format(
                self.__leaf_name, file_path, e
            )
            raise Exception(msg)

    def file_download(self, file_id: str) -> bool:
        """
        Download aggregated model weights from server

        Args:
            file_id: Unique file ID (typically from aggregation notification)

        Returns:
            bool: True if download successful

        Raises:
            Exception: If download fails or file is empty

        Note:
            - File saved to ./aggregated_files/{file_id}.npz
            - Directory created automatically if it doesn't exist
            - File contains only layer arrays (no weighting field)

        Example:
            >>> if not client.queue.empty():
            ...     aggregation_id = client.queue.get(block=False)
            ...     client.file_download(aggregation_id)
            ...     # File saved to ./aggregated_files/{aggregation_id}.npz
        """
        try:
            if not os.path.exists(AGGREGATED_OUTPUT_DIR):
                os.makedirs(AGGREGATED_OUTPUT_DIR)

            url = self.__api_host + "/api/v1/file/download/" + file_id
            headers = self._get_auth_headers()
            headers["accept"] = "*/*"

            resp = requests.get(
                url, headers=headers, verify=self.__verify, proxies=self.__proxies
            )

            if resp.status_code != HTTPStatus.OK:
                raise Exception(resp.json()["error"])

            try:
                download_url = resp.json()["data"]["download_url"]
            except Exception:
                raise Exception(
                    f"Failed to parse response from download API: {resp.json()}"
                )

            resp = requests.get(
                download_url, verify=self.__verify, proxies=self.__proxies
            )
            if len(resp.content) == 0:
                raise Exception("file not received")

            f = open(AGGREGATED_OUTPUT_DIR + "/" + file_id + ".npz", "wb")
            f.write(resp.content)
            f.close()
            print(f"downloaded file {file_id}")
            return True

        except Exception as e:
            msg = "File Download failed for leaf {} for file {}: {}".format(
                self.__leaf_name, file_id, e
            )
            raise Exception(msg)

    def send_performance_metrics(
        self, aggregation_id: str, data: str, mode: str
    ) -> bool:
        """
        Submit training or testing performance metrics to server

        Args:
            aggregation_id: ID of the aggregation these metrics relate to
            data: JSON string containing metrics (e.g., '{"accuracy": 0.95, "loss": 0.12}')
            mode: Metric type - "test", "train", or "non-federated"

        Returns:
            bool: True if submission successful, False otherwise

        Example:
            >>> import json
            >>> metrics = {"accuracy": 0.95, "loss": 0.12}
            >>> client.send_performance_metrics(
            ...     aggregation_id="agg-uuid",
            ...     data=json.dumps(metrics),
            ...     mode="test"
            ... )
        """
        try:
            url = self.__api_host + "/api/v1/performance/analysis"
            headers = self._get_auth_headers()
            payload = json.dumps(
                {
                    "mode": mode,
                    "aggregation_id": aggregation_id,
                    "leaf_id": self.__leaf_id,
                    "branch_id": self.__branch_id,
                    "tree_id": self.__tree_id,
                    "data": data,
                }
            )

            resp = requests.post(
                url,
                headers=headers,
                data=payload,
                verify=self.__verify,
                proxies=self.__proxies,
            )

            print(f"received resp code from performance_analyser: {resp.status_code}")
            if resp.status_code != HTTPStatus.CREATED:
                raise Exception(resp.json())
            else:
                return True

        except Exception as e:
            msg = "Sending Performance Metrics failed for aggregation {}: {}".format(
                aggregation_id, e
            )
            logging.error(msg)
            return False

    @property
    def leaf_id(self):
        return self.__leaf_id

    @property
    def branch_id(self):
        return self.__branch_id

    @property
    def tree_id(self):
        return self.__tree_id

    @property
    def user_id(self):
        return self.__user_id

    @property
    def session_token(self):
        return self.__leaf_session_token

    @property
    def is_authenticated(self):
        return self.__status == "authenticated"

    @property
    def run_status(self):
        return self.__run_status

    @property
    def run_number(self):
        return self.__run_number

    def close(self) -> None:
        """
        Gracefully shutdown the client and RabbitMQ consumer

        Stops the background RabbitMQ consumer thread and cleans up resources.
        Should be called when done using the client, or use context manager.

        Example:
            >>> client = Client(credentials)
            >>> # ... do work ...
            >>> client.close()

            Or with context manager:
            >>> with Client(credentials) as client:
            ...     # ... do work ...
            ...     pass  # Automatically closed
        """
        if self.consumer is not None and self.consumer.is_alive():
            try:
                # Request consumer to stop using pika's thread-safe callback mechanism
                if hasattr(self.consumer, "consumer"):
                    self.consumer.consumer.request_stop()
                    # Wait for thread to exit gracefully
                    self.consumer.join(timeout=5.0)
                    if self.consumer.is_alive():
                        logging.warning(
                            "[Client] Consumer thread did not stop gracefully, forcing shutdown"
                        )
                        self.consumer.kill()
            except Exception as e:
                logging.warning(f"[Client] Error stopping consumer: {e}")

        # Clean up the queue to release socketpair resources
        try:
            while not self.queue.empty():
                self.queue.get_nowait()
        except Exception:
            pass

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensure cleanup"""
        self.close()
        return False
