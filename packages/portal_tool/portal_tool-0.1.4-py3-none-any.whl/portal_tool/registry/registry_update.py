import json
import logging
import pathlib
import shlex
import subprocess

import jinja2

from portal_tool.framework.framework_manager import FrameworkManager
from portal_tool.framework.git_manager import GitManager
from portal_tool.models import GitDetails, PortalModule


def filter_nones(obj):
    """
    Given a JSON-serializable object, return a copy without elements which have
    a value of None.
    """

    if isinstance(obj, list):
        # This version may or may not be easier to read depending on your
        # preferences:
        # return list(filter(None, map(remove_nones, obj)))

        # This version uses a generator expression to avoid computing a full
        # list only to immediately walk it again:
        filtered_values = (filter_nones(j) for j in obj)
        return [i for i in filtered_values if i is not None]
    elif isinstance(obj, dict):
        filtered_items = ((i, filter_nones(j)) for i, j in obj.items())
        return {k: v for k, v in filtered_items if v is not None}
    else:
        return obj


class RegistryManager:
    def __init__(
        self, registry_path: pathlib.Path, framework_manager: FrameworkManager
    ):
        self.registry_path = registry_path
        self.framework_manager = framework_manager

    def update(self) -> None:
        logging.info(f"Updating vcpkg registry at: {self.registry_path.absolute()}")

        git_manager: GitManager = GitManager()
        for module in self.framework_manager.find_modules():
            details = git_manager.to_details(subdirectory=module.short_name)
            self._generate_vcpkg_port(module, details)

    def update_version(self) -> None:
        output = subprocess.check_output(
            shlex.split(
                f'vcpkg --x-builtin-ports-root="{self.registry_path / "ports"}" --x-builtin-registry-versions-dir="{self.registry_path / "versions"}" x-add-version --all --verbose'
            )
        )
        print(output.decode())

    def _generate_vcpkg_port(
        self, module: PortalModule, git_details: GitDetails
    ) -> None:
        env = jinja2.environment.Environment(
            loader=jinja2.PackageLoader("portal_tool", "templates/vcpkg"),
        )

        cmake_template = env.get_template("portfile.cmake.j2")

        cmake = cmake_template.render(module=module, git=git_details)
        usage_template = env.get_template("usage.j2")
        usage = usage_template.render(module=module, git=git_details)

        port_path = self.registry_path / "ports" / module.name
        if not port_path.exists():
            port_path.mkdir(parents=True)

        logging.info(f"Generating vcpkg port at: {port_path}")

        port_file = port_path / "portfile.cmake"
        vcpkg_file = port_path / "vcpkg.json"
        usage_file = port_path / "usage"

        port_file.write_text(cmake)
        self._make_vcpkg_json(module, vcpkg_file)
        usage_file.write_text(usage)

        subprocess.check_output(shlex.split(f'vcpkg format-manifest "{vcpkg_file}"'))

    @staticmethod
    def _make_vcpkg_json(module: PortalModule, json_path: pathlib.Path) -> None:
        old_vcpkg_json = json.loads(
            json_path.read_text() if json_path.exists() else "{}"
        )

        json_details = {
            "name": module.name,
            "version": module.version,
            "description": module.description,
            "license": "MIT",
        }

        json_deps = [
            {"name": "vcpkg-cmake", "host": True},
            {"name": "vcpkg-cmake-config", "host": True},
        ]
        for dependency in module.dependencies:
            json_deps.append(
                {
                    "name": dependency.name,
                    "features": dependency.features,
                    "version>=": dependency.version,
                    "platform": dependency.platform,
                }
            )
        json_details["dependencies"] = json_deps

        # json_features = {}
        # for feature in module.features:
        #     json_feature = {
        #         "description": feature.description,
        #         "dependencies": []
        #     }
        #
        #     for dep in feature.dependencies:
        #         json_feature["dependencies"].append(
        #             {
        #                 "name": dep.name,
        #                 "features": dep.features,
        #                 "version>=": dep.version,
        #                 "platform": dep.platform
        #             }
        #         )
        #     json_features[feature.name] = json_feature

        if json_details["version"] == old_vcpkg_json.get("version"):
            json_details["port-version"] = old_vcpkg_json.get("port-version", 0) + 1

        formatted_json = filter_nones(json_details)
        json_path.write_text(json.dumps(formatted_json, indent=4))
