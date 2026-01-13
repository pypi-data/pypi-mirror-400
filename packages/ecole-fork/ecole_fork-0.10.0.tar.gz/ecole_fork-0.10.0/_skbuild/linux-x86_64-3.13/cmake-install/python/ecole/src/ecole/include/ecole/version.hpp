#pragma once

#include <string_view>
#include <filesystem>

#include <scip/config.h>

#include "ecole/export.hpp"

namespace ecole::version {

struct ECOLE_EXPORT VersionInfo {
	unsigned int major;
	unsigned int minor;
	unsigned int patch;
	std::string_view revision = "unknown";
	std::string_view build_type = "unknown";
	std::string_view build_os = "unknown";
	std::string_view build_time = "unknown";
	std::string_view build_compiler = "unknown";
};

/**
 * Ecole version, as per header files.
 */
inline constexpr auto get_ecole_header_version() noexcept -> VersionInfo {
	return {
		0,  // NOLINT(readability-magic-numbers)
		9,  // NOLINT(readability-magic-numbers)
		6,  // NOLINT(readability-magic-numbers)
		"3e09e55cf7dd660414952c4299e3a490b8fcf850",
		"Release",
		"Linux-6.14.0-32-generic",
		"2025-10-10T18:15:27",
		"GNU-14.2.0",
	};
}

/**
 * Ecole version of the library.
 *
 * This is the version of Ecole when compiling it as a library.
 * This is useful for detecting incompatibilities when loading as a dynamic library.
 */
ECOLE_EXPORT auto get_ecole_lib_version() noexcept -> VersionInfo;

/**
 * Path of the libecole shared library when it exists.
 *
 * This is used for Ecole extensions to locate the library.
 */
ECOLE_EXPORT auto get_ecole_lib_path() -> std::filesystem::path;

/**
 * SCIP version, as per current header files.
 */
inline constexpr auto get_scip_header_version() noexcept -> VersionInfo {
	return {SCIP_VERSION_MAJOR, SCIP_VERSION_MINOR, SCIP_VERSION_PATCH};
}

/**
 * SCIP version, as per the (dynamically) loaded library.
 */
ECOLE_EXPORT auto get_scip_lib_version() noexcept -> VersionInfo;

/**
 * Path of the libscip shared library when it exists.
 *
 * This is used for Ecole extensions to locate the library.
 */
ECOLE_EXPORT auto get_scip_lib_path() -> std::filesystem::path;

/**
 * SCIP version used to compile Ecole library.
 */
ECOLE_EXPORT auto get_scip_buildtime_version() noexcept -> VersionInfo;

}  // namespace ecole
