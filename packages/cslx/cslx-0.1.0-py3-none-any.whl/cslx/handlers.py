import json
import traceback
from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join
import os
import sys
import uuid
import tempfile
from pathlib import Path
from jupyter_client.kernelspec import KernelSpecManager
from jupyter_server.base.handlers import APIHandler
from tornado import web

class InstallKernelSpecHandler(APIHandler):
    @web.authenticated
    async def post(self):
        body = self.get_json_body() or {}
        name = body.get("name")
        id = body.get("id")
        url = body.get("url")
        token = body.get("token")
        argv = body.get("argv")
        if not argv:
            argv = [sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"]

        # Create a temporary kernelspec folder and install it for user
        ksm = KernelSpecManager()
        try:
            with tempfile.TemporaryDirectory() as td:
                # create a temporary kernelspec directory and write kernel.json there
                kernel_dir = Path(td) / id
                kernel_dir.mkdir(parents=True, exist_ok=True)
                kernel_json = {
                    "argv": argv,
                    "display_name": name,
                    "language": "python",
                    "interrupt_mode": "message",
                    "metadata": {
                        "kernel_provisioner": {
                            "provisioner_name": "cspyk-provisioner",
                            "config": {"url": url, 
                                       "token": token},
                        }
                    },
                }
                (kernel_dir / "kernel.json").write_text(json.dumps(kernel_json))
                print("Creating directory for kernelspec:", str(kernel_dir))
                print("Kernel JSON:", json.dumps(kernel_json))

                # install into user kernelspecs, replace if exists
                ksm.install_kernel_spec(str(kernel_dir), id, user=True, replace=True)
            self.finish(json.dumps({"status": "ok", "kernelspec": id}))
        except Exception as e:

            traceback.print_exc()
            self.set_status(500)
            self.finish(json.dumps({"status": "error", "message": str(e)}))


class UninstallKernelSpecHandler(APIHandler):
    @web.authenticated
    async def post(self):
        body = self.get_json_body() or {}
        id = body.get("id")
        if not id:
            self.set_status(400)
            self.finish(json.dumps({"status": "error", "message": "missing kernelspec id"}))
            return

        ksm = KernelSpecManager()
        try:
            # Try to remove user-level kernelspec first, fall back to system-level
            try:
                ksm.remove_kernel_spec(id)
                self.finish(json.dumps({"status": "ok"}))
            except Exception as e:
                # attempt system uninstall
                print("Attempting failed to uninstall for kernelspec:", id, "Error:", e)
                self.set_status(500)
                self.finish(json.dumps({"status": "error", "message": str(e)}))

        except Exception as e:
            traceback.print_exc()
            self.set_status(500)
            self.finish(json.dumps({"status": "error", "message": str(e)}))

def setup_handlers(web_app):
    """
    Register tornado handlers on the running Jupyter Server web app.
    """
    host_pattern = ".*$"
    base_url = web_app.settings["base_url"]

    install_route = url_path_join(base_url, "cslx", "api", "install-kernelspec")
    uninstall_route = url_path_join(base_url, "cslx", "api", "uninstall-kernelspec")
    handlers = [
        (install_route, InstallKernelSpecHandler),
        (uninstall_route, UninstallKernelSpecHandler),
    ]
    web_app.add_handlers(host_pattern, handlers)