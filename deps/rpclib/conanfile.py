from conans import CMake, ConanFile, tools


class RpcLibConan(ConanFile):
    name = "rpclib"
    channel = "dev"
    version = "v2.2.1_c5"
    license = "MIT"
    author = "carla-simulator"
    url = "https://github.com/carla-simulator/rpclib"
    description = "RPClib patch for carla"
    topics = ("RPC", "CARLA", "Conan")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": True, "fPIC": True}
    generators = "cmake"

    _cmake = None
    _source_folder = "rpclib"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        self.run(f"git clone -b {self.version} https://github.com/carla-simulator/rpclib.git {self._source_folder}")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self, generator="Unix Makefiles")
        self._cmake.configure(source_folder=self._source_folder)
        self._cmake.definitions["CMAKE_CXX_FLAGS"] = "-fPIC -std=c++14"
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
