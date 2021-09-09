import os
import shutil
from pathlib import Path

from conans import CMake, ConanFile, tools


class RpcLibConan(ConanFile):
    name = "recastlib"
    channel = "dev"
    version = "0b13b0"
    git_commit = "0b13b0d288ac96fdc5347ee38299511c6e9400db"
    license = "Zlib"
    author = "recastnavigation"
    url = "https://github.com/carla-simulator/recastnavigation"
    description = "Recastlib for carla"
    topics = ("Games", "Mesh Constuction", "CARLA", "Conan")
    settings = "os", "compiler", "build_type", "arch"
    options = {"fPIC": [True, False]}
    default_options = {"fPIC": True}
    generators = "cmake"

    _cmake = None
    _source_folder = "recastlib"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        self.run(f"git clone https://github.com/carla-simulator/recastnavigation.git {self._source_folder}")
        self.run(f"cd {self._source_folder} && git reset --hard {self.git_commit}")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self, generator="Ninja")
        self._cmake.configure(source_folder=self._source_folder)
        self._cmake.definitions["CMAKE_CXX_FLAGS"] = "-fPIC -std=c++14"
        self._cmake.definitions["RECASTNAVIGATION_DEMO"] = False
        self._cmake.definitions["RECASTNAVIGATION_TEST"] = False
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        headers_to_move = os.listdir(f"{self.package_folder}/include")
        Path(f"{self.package_folder}/include/recast").mkdir(parents=True, exist_ok=True)
        for header in headers_to_move:
            if header.endswith(".h"):
                shutil.move(f"{self.package_folder}/include/{header}",
                            f"{self.package_folder}/include/recast/{header}")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
