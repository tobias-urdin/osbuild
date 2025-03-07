"""
Mount Handling for pipeline stages

Allows stages to access file systems provided by devices.
This makes mount handling transparent to the stages, i.e.
the individual stages do not need any code for different
file system types and the underlying devices.
"""

import abc
import hashlib
import json
import os
import subprocess
from typing import Dict, List

from osbuild import host
from osbuild.devices import DeviceManager


class Mount:
    """
    A single mount with its corresponding options
    """

    def __init__(self, name, info, device, target, options: Dict):
        self.name = name
        self.info = info
        self.device = device
        self.target = target
        self.options = options
        self.id = self.calc_id()

    def calc_id(self):
        m = hashlib.sha256()
        m.update(json.dumps(self.info.name, sort_keys=True).encode())
        if self.device:
            m.update(json.dumps(self.device.id, sort_keys=True).encode())
        if self.target:
            m.update(json.dumps(self.target, sort_keys=True).encode())
        m.update(json.dumps(self.options, sort_keys=True).encode())
        return m.hexdigest()


class MountManager:
    """Manager for Mounts

    Uses a `host.ServiceManager` to activate `Mount` instances.
    Takes a `DeviceManager` to access devices and a directory
    called `root`, which is the root of all the specified mount
    points.
    """

    def __init__(self, devices: DeviceManager, root: str) -> None:
        self.devices = devices
        self.root = root
        self.mounts: Dict[str, Dict[str, Mount]] = {}

    def mount(self, mount: Mount) -> Dict:

        source = self.devices.device_abspath(mount.device)

        root = os.fspath(self.root)

        args = {
            "source": source,
            "target": mount.target,

            "root": root,
            "tree": os.fspath(self.devices.tree),

            "options": mount.options,
        }

        mgr = self.devices.service_manager

        client = mgr.start(f"mount/{mount.name}", mount.info.path)
        path = client.call("mount", args)

        if not path:
            res: Dict[str, Mount] = {}
            self.mounts[mount.name] = res
            return res

        if not path.startswith(root):
            raise RuntimeError(f"returned path '{path}' has wrong prefix")

        path = os.path.relpath(path, root)

        self.mounts[mount.name] = path

        return {"path": path}


class MountService(host.Service):
    """Mount host service"""

    @abc.abstractmethod
    def mount(self, args: Dict):
        """Mount a device"""

    @abc.abstractmethod
    def umount(self):
        """Unmount all mounted resources"""

    def stop(self):
        self.umount()

    def dispatch(self, method: str, args, _fds):
        if method == "mount":
            r = self.mount(args)
            return r, None

        raise host.ProtocolError("Unknown method")


class FileSystemMountService(MountService):
    """Specialized mount host service for file system mounts"""

    def __init__(self, args):
        super().__init__(args)

        self.mountpoint = None
        self.check = False

    # pylint: disable=no-self-use
    @abc.abstractmethod
    def translate_options(self, options: Dict) -> List:
        opts = []
        if options.get("readonly"):
            opts.append("ro")
        if options.get("norecovery"):
            opts.append("norecovery")
        if "uid" in options:
            opts.append(f"uid={options['uid']}")
        if "gid" in options:
            opts.append(f"gid={options['gid']}")
        if "umask" in options:
            opts.append(f"umask={options['umask']}")
        if "shortname" in options:
            opts.append(f"shortname={options['shortname']}")
        if "subvol" in options:
            opts.append(f"subvol={options['subvol']}")
        if "compress" in options:
            opts.append(f"compress={options['compress']}")
        if opts:
            return ["-o", ",".join(opts)]
        return []

    def mount(self, args: Dict):

        source = args["source"]
        target = args["target"]
        root = args["root"]
        options = args["options"]

        mountpoint = os.path.join(root, target.lstrip("/"))

        options = self.translate_options(options)

        os.makedirs(mountpoint, exist_ok=True)
        self.mountpoint = mountpoint

        try:
            subprocess.run(
                ["mount"] +
                options + [
                    "--source", source,
                    "--target", mountpoint
                ],
                stderr=subprocess.STDOUT,
                stdout=subprocess.PIPE,
                check=True)
        except subprocess.CalledProcessError as e:
            code = e.returncode
            msg = e.stdout.strip()
            raise RuntimeError(f"{msg} (code: {code})") from e

        self.check = True
        return mountpoint

    def umount(self):
        if not self.mountpoint:
            return

        self.sync()

        print("umounting")

        # We ignore errors here on purpose
        subprocess.run(["umount", self.mountpoint],
                       check=self.check)
        self.mountpoint = None

    def sync(self):
        subprocess.run(["sync", "-f", self.mountpoint],
                       check=self.check)
