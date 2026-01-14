import asyncio
import pathlib
import signal
from typing import Any
from jupyter_client.connect import KernelConnectionInfo
from jupyter_client.provisioning.provisioner_base import KernelProvisionerBase
import requests
import typing as t

class CSKernelProvisioner(KernelProvisionerBase):
    """Provisioner for CSPython kernels."""

    KERNEL_NAME = "cspython"
    process = None
    pid = None
    pgid = None
    ip = None
    cwd = None
    remote_kernel_id = None
    conduit_base_url = "http://127.0.0.1:8080"
    conduit_token = ""

    def __init__(self, **kwargs: t.Any):
        super().__init__(**kwargs)
        self.remote_kernel_id = None
        self.tunnel_proc = None
        self.tunneled_ports = []

        metadata = self.kernel_spec.metadata
        if not metadata:
            raise RuntimeError("CSPYK: Kernel spec metadata is missing")
        
        config = metadata.get('kernel_provisioner', {}).get('config', {}) or {}
        url = config.get('url', self.conduit_base_url)
        token = config.get('token', None)

        if not url:
            raise RuntimeError("CSPYK: provisioner config missing 'url' in kernelspec metadata or provisioner config")
        self.conduit_base_url = url
        self.conduit_token = token

    def _get_conduit_headers(self) -> dict[str, str]:
        """Helper to get headers with auth token for Conduit API requests."""
        headers = {}
        if self.conduit_token:
            headers["X-Tunnel-Authorization"] = f"tunnel {self.conduit_token}"
        return headers
    
    @property
    def has_process(self) -> bool:
        """Returns True if the kernel process is running."""
        # Implementation specific to CSPython kernel
        # print("CSPYK: Checking if CSPython kernel process is running...")
        return self.remote_kernel_id is not None

    async def poll(self) -> int | None:
        """Checks if the kernel process is still running."""
        # Implementation specific to CSPython kernel
        #print("CSPYK: Polling CSPython kernel process status...")

        pollUrl = f"{self.conduit_base_url}/api/v1/jupyter/kernels/{self.remote_kernel_id}/status"
        
        try:
            response = requests.get(pollUrl, headers=self._get_conduit_headers())
            if response.status_code != 200:
                #print("CSPYK: Error polling kernel status:", response.text)
                return 1
        except Exception as e:
            #print("CSPYK: Exception while polling kernel status:", e)
            return 1

        status = response.json().get("Status")
        if status == "running":
            #print("CSPYK: Kernel is running.")
            return None
        elif status == "stopped":
            #print("CSPYK: Kernel has stopped.")
            return 0
        
        #print("CSPYK: Unknown kernel status:", status)
        return None
    
    async def wait(self) -> int | None:
        """Waits for the kernel process to terminate."""
        # Implementation specific to CSPython kernel
        print("CSPYK: Waiting for CSPython kernel process to terminate...")
        ret = 0
        if self.remote_kernel_id:
             while await self.poll() is None:  # type:ignore[unreachable]
                await asyncio.sleep(2)
            
        self.remote_kernel_id = None  # allow has_process to now return False
        return ret 
    
    async def send_signal(self, signum: int) -> None:
        """Sends a signal to the kernel process."""
        # Implementation specific to CSPython kernel
        print(f"CSPYK: Sending signal {signum} to CSPython kernel process...")
        shutdownUrl = f"{self.conduit_base_url}/api/v1/jupyter/kernels/shutdown"
        if self.remote_kernel_id:
            try:
                response = requests.post(
                    shutdownUrl,
                    json={"kernelId": self.remote_kernel_id, "signal": signum},
                    headers=self._get_conduit_headers(),
                )
                if response.status_code != 200:
                    print("CSPYK: Error sending signal to kernel:", response.text)
            except Exception as e:
                print("CSPYK: Exception while sending signal to kernel:", e)


    async def kill(self, restart: bool = False) -> None:
        """Kills the kernel process."""
        # Implementation specific to CSPython kernel
        print("CSPYK: Killing CSPython kernel process...")
        await self.send_signal(signal.SIGKILL)

    async def terminate(self, restart: bool = False) -> None:
        """Terminates the kernel process."""
        # Implementation specific to CSPython kernel
        print("CSPYK: Terminating CSPython kernel process...")
        await self.send_signal(signal.SIGTERM)
            
    async def launch_kernel(self, cmd: list[str], **kwargs: Any) -> KernelConnectionInfo:
        """Launches the kernel process."""
    
        # This provisions a remote kernel on the Conduit server
        provisionUrl = f"{self.conduit_base_url}/api/v1/jupyter/kernels"
        provisionJson = {
            "kernelName": "python3",
            "venvPath": "tmp",
            "condaEnv": ""
        }

        response = requests.post(provisionUrl, json=provisionJson, headers=self._get_conduit_headers())
        print("CSPYK: Headers :", self._get_conduit_headers())
        if response.status_code != 201:
            raise RuntimeError("CSPYK: Error provisioning kernel: " + response.text + " Error code: " + str(response.status_code))

        self.remote_kernel_id = response.json().get("kernelId")

        # Once the kernel is provisioned, get its connection JSON to dertmine the ZMQ ports opened on the server 
        connectionInfoUrl = f"{self.conduit_base_url}/api/v1/jupyter/kernels/{self.remote_kernel_id}/connection"
        conn_response = requests.get(connectionInfoUrl, headers=self._get_conduit_headers())
        if conn_response.status_code != 200:
            raise RuntimeError(f"CSPYK: Error getting connection info: {conn_response.text}")
        
        kci = conn_response.json().get("connectionInfo")
        kci["key"] = kci["key"].encode("ascii")

        km = self.parent
        km.transport = kci["transport"]
        km.session.signature_scheme = kci["signature_scheme"]
        key_l, key_r = km.session.key, kci["key"]
        if key_l and key_l != key_r:
            print(f"Overriding local Session key with remote ({key_l=} vs {key_r=}")
            km.session.key = key_r

        # Now that we have the remote kernel's ZMQ ports, set up a devtunnel to forward them locally. 
        # First create the devtunnel tunnel via the Conduit API
        tunnelJson  = {
            "tunnelName": self.remote_kernel_id + "-tunnel",
            "expiration": "1d",
            "ports": [int(kci["shell_port"]), int(kci["iopub_port"]), 
                      int(kci["stdin_port"]), int(kci["hb_port"]), int(kci["control_port"])],
            "createToken": True
        }

        tunnelUrl = f"{self.conduit_base_url}/api/v1/tunnels/devtunnels"
        tunnel_response = requests.post(tunnelUrl, json=tunnelJson, headers=self._get_conduit_headers())

        if tunnel_response.status_code != 201:
            raise RuntimeError(f"CSPYK: Error creating dev tunnel: {tunnel_response.text}")

        tunnel_response_json = tunnel_response.json()
        tunnlName = tunnel_response_json.get("tunnelName")
        tunnelID = tunnel_response_json.get("tunnelID")
        token = tunnel_response_json.get("token")

        # devtunnel connect <tunnelID> --access-token <token>
        #print(f"To connect to the kernel, run: devtunnel connect {tunnelID} --access-token {token}")

        from cspyk.devtunnel import start_devtunnel

        # Start the devtunnel process locally to forward the remote kernel ports onto the local machine.
        # We determine the port forwarding state by monitoring devtunnel connect output. 
        # This is an asynchronous operation. 
        self.tunneled_ports = []
        try:
            proc, tunneled_ports = await start_devtunnel(tunnelID, token, kci, km)
        except FileNotFoundError:
            print("devtunnel binary not found on PATH; please install or provide full path.")
            proc = None
            tunneled_ports = []

        self.tunnel_proc = proc
        self.tunneled_ports = tunneled_ports


        # Wait until all ports are forwarded from the async devtunnel process
        while len(self.tunneled_ports) < 5 and self.tunnel_proc.returncode is None:
            print("CSPYK: Waiting for all port forwardings to be established...")
            await asyncio.sleep(1)

        # Use this in poll logic as well
        # If the devtunnel process has exited, raise an error
        if self.tunnel_proc.returncode is not None:
            print("CSPYK: devtunnel process exited unexpectedly with code", self.tunnel_proc.returncode)
            raise RuntimeError("devtunnel process exited before all ports were forwarded")
        
        km.ip = kci["ip"]
        km.write_connection_file()  
        
        return kci
    
    async def cleanup(self, restart: bool = False) -> None:
        """Cleans up resources after kernel termination."""
        print("CSPYK: Cleaning up CSPython kernel resources...")

        # Cleanup the devtunnel process if it exists
        proc = getattr(self, "tunnel_proc", None)
        if proc:
            try:
                # Use helper to stop cleanly
                from cspyk.devtunnel import stop_devtunnel

                await stop_devtunnel(proc)
            except Exception as e:
                print("Error stopping devtunnel:", e)
        
    
    async def shutdown_requested(self, restart: bool = False) -> None:
        """Handles shutdown requests for the kernel."""
        # Implementation specific to CSPython kernel
        print("CSPYK: Shutdown requested for CSPython kernel...")
        ## TODO: implement a graceful shutdown
        await self.send_signal(signal.SIGTERM)
        return None  # Placeholder implementation
    
    async def pre_launch(self, **kwargs: Any) -> dict[str, Any]:
        """Prepares for kernel launch."""
        # Implementation specific to CSPython kernel
        print("CSPYK: Preparing to launch CSPython kernel... args:", kwargs)
        
        km = self.parent    
        km.write_connection_file()
        prov_info = await self.get_provisioner_info()
        print("CSPYK: Provisioner info:", prov_info)
        # self.config.setdefault("KernelManager", {}).setdefault("connection_file", fp)
        # print("CSPYK: Preparing to launch CSPython kernel... connection_file:", fp)
        
        extra_arguments = kwargs.pop("extra_arguments", [])
        kernel_cmd = self.kernel_spec.argv + extra_arguments

        return await super().pre_launch(cmd=kernel_cmd, **kwargs)
    
    def resolve_path(self, path_str: str) -> str | None:
        """Resolve path to given file."""
        path = pathlib.Path(path_str).expanduser()
        if not path.is_absolute() and self.cwd:
            path = (pathlib.Path(self.cwd) / path).resolve()
        if path.exists():
            return path.as_posix()
        return None

    @staticmethod
    def _scrub_kwargs(kwargs: dict[str, Any]) -> dict[str, Any]:
        """Remove any keyword arguments that Popen does not tolerate."""
        keywords_to_scrub: list[str] = ["extra_arguments", "kernel_id"]
        scrubbed_kwargs = kwargs.copy()
        for kw in keywords_to_scrub:
            scrubbed_kwargs.pop(kw, None)
        return scrubbed_kwargs

    async def post_launch(self, **kwargs: Any) -> None:
        """Finalizes after kernel launch."""
        # Implementation specific to CSPython kernel
        print("CSPYK: Finalizing CSPython kernel launch...")
        return None  # Placeholder implementation
    
    async def get_provisioner_info(self) -> dict[str, Any]:
        """Returns information about the provisioner."""
        print("CSPYK: Getting provisioner information...")
        provisioner_info = await super().get_provisioner_info()
        provisioner_info.update({"pid": self.pid, "pgid": self.pgid, "ip": self.ip})
        return provisioner_info 

    async def load_provisioner_info(self, provisioner_info: dict) -> None:
        """Loads provisioner information."""
        # Implementation specific to CSPython kernel
        print("CSPYK: Loading provisioner information...")
        await super().load_provisioner_info(provisioner_info)
        self.pid = provisioner_info["pid"]
        self.pgid = provisioner_info["pgid"]
        self.ip = provisioner_info["ip"] 
    
    def get_shutdown_wait_time(self, recommended: float = 5.0) -> float:
        """Returns the wait time for shutdown."""
        print("CSPYK: Getting shutdown wait time...")
        return recommended  # Placeholder implementation
    
    def get_stable_start_time(self, recommended: float = 10.0) -> float:
        """Returns the stable start time for the kernel."""
        print("CSPYK: Getting stable start time...")
        return recommended  # Placeholder implementation    
    

