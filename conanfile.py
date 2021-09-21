from conans import CMake, ConanFile, tools


class LibCarlaConan(ConanFile):
    name = "LibCarla"
    version = "0.9.12"
    license = "MIT"
    author = "carla-simulator"
    url = "https://github.com/carla-simulator/carla"
    settings = "os", "compiler", "build_type", "arch"
    requires = [
        "boost/1.69.0",
        "libpng/1.6.37",
        "gtest/1.10.0",
        "recastlib/0b13b0@libcarla/dev",
        "rpclib/v2.2.1_c5@libcarla/dev"
    ]
    description = "Carla CPP API"
    topics = ("CARLA", "Conan")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "fPIC": [True, False],
        "test" : [True, False]
    }
    default_options = {
        "fPIC": True,
        "test" : False
    }
    generators = "cmake"

    exports_sources = [
        "libcarla/ToolChain.cmake",
        "libcarla/CMakeLists.txt.in"
        "deps/*"
    ]

    _cmake = None
    _source_folder = "libcarla"
    _deps_folder = "deps"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        # Clean libcarla source
        self.run(f"rm -rf {self._source_folder}/cmake {self._source_folder}/source {self._source_folder}/carla")

        # Clone carla repository with no-tree config
        self.run(f"git clone -b {self.version} --no-checkout --filter=tree:0 https://github.com/carla-simulator/carla/ {self._source_folder}/carla")

        # Checkout for only LibCarla : sparse checkout
        self.run(f"cd {self._source_folder}/carla && git sparse-checkout set LibCarla && mv LibCarla/cmake .. && mv LibCarla/source .. && cd .. && rm -rf carla")

        # Make conan installed packages available to libcarla
        tools.replace_in_file(f"{self._source_folder}/cmake/CMakeLists.txt", "project(libcarla)",
                             '''project(libcarla)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()
include(${CMAKE_CURRENT_SOURCE_DIR}/../CMakeLists.txt.in)''')

        # Generate Versoion.h file in carla source
        self.run(f"cp {self._source_folder}/source/carla/Version.h.in {self._source_folder}/source/carla/Version.h")
        tools.replace_in_file(f"{self._source_folder}/source/carla/Version.h", "${CARLA_VERSION}",
                              self.version)

        # Modification in code intrinsics for compatibility with gcc\g++ 9
        tools.replace_in_file(f"{self._source_folder}/source/test/common/test_streaming.cpp", "Server<tcp::Server>",
                              "carla::streaming::low_level::Server<tcp::Server>")
        tools.replace_in_file(f"{self._source_folder}/source/test/common/test_streaming.cpp", "Client<tcp::Client>",
                              "carla::streaming::low_level::Client<tcp::Client>")
        tools.replace_in_file(f"{self._source_folder}/source/carla/trafficmanager/TrafficManagerServer.h", "catch(std::exception)",
                        "catch(std::exception &)")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self, generator="Ninja", build_type="Client")
        self._cmake.definitions["CMAKE_TOOLCHAIN_FILE"] = f"{self._source_folder}/ToolChain.cmake"
        self._cmake.definitions["CMAKE_EXPORT_COMPILE_COMMANDS"] = True
        self._cmake.configure(source_folder=f"{self._source_folder}/cmake")
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.system_libs.append("pthread")
