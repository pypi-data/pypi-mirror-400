# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.8] - 2026-01-07

### Added
- **Parallel device flashing** - Multiple devices can now be flashed simultaneously
  - `--ip` parameter now accepts multiple IP addresses for parallel network flashing
  - `--serial` parameter now accepts multiple serial numbers for sequential USB flashing
  - Uses `ProcessPoolExecutor` for true parallel execution (separate processes per device)
  - Each device gets isolated pylink state, preventing conflicts
  - Real-time progress reporting with ✓/✗ indicators per device
  - Summary report showing success/failure counts
  - Example: `bmlab-flash firmware.bin --ip 192.168.1.100 192.168.1.101 192.168.1.102`
  - Example: `bmlab-flash firmware.bin --serial 123456 789012 345678`

### Changed
- **Smart execution strategy based on connection type**:
  - Network devices (--ip): Parallel flashing using ProcessPoolExecutor
  - USB devices (--serial): Sequential flashing to avoid USB driver conflicts
  - Auto-detection still works for single device scenarios
- **Unified device output format** - Same format for single or multiple devices
- Added 500ms delay after each flash operation for proper device release

### Added (Testing)
- New CI workflow `test-flash.yml` for testing parallel flashing functionality
- Tests for single device flashing (USB serial and network IP)
- Tests for multiple device flashing (2 and 3 devices in parallel)
- Tests for auto-detection and MCU parameter handling

## [0.1.7] - 2026-01-06

### Fixed
- **Network scanning now correctly detects target MCU for all devices**:
  - Added thread lock (`threading.Lock`) to serialize JLink connections during parallel scanning
  - Prevents state conflicts in pylink library when multiple threads connect simultaneously
  - Previously parallel scans could incorrectly detect STM32F765ZG instead of actual STM32F103RE
  - Added 500ms delay after disconnect to ensure device is fully released
- **CI workflow improvements**:
  - Removed excessive debug output from test steps
  - Simplified Docker container setup and cleanup
  - Fixed validation logic: removed redundant device counting, only validate target MCU and IPs
  - Added network cleanup before creation to prevent "pool overlaps" errors
  - Strict validation restored: exactly 3 STM32F103RE devices required at specified IPs

### Changed
- Network scanning: target detection is now serialized with lock protection
  - Port checks remain parallel for speed
  - Target MCU detection runs sequentially to prevent pylink state conflicts

## [0.1.6] - 2026-01-04

### Changed
- **Renamed `bmlab-jlink-rtt` to `bmlab-rtt`** - Command renamed to support multiple programmers
  - Added `--programmer` (`-p`) parameter to select programmer type (default: jlink)
  - Follows the same pattern as `bmlab-flash` command
  - Updated all documentation, examples, and launch configurations
  - Old command name `bmlab-jlink-rtt` is no longer available

## [0.1.4] - 2025-12-14

### Changed
- **Improved resilience of network scanning for JLink Remote Server**:
  - Added parallel scanning with limited concurrency (using `concurrent.futures.ThreadPoolExecutor`).
  - Added socket timeout to avoid hanging on unresponsive IPs.
- **launch.json** can now run the CLI via `"module": "bmlab_toolkit.scan_cli"` for correct relative import functionality.

### Fixed
  - Properly close J-Link connection after each IP scan (using `finally` + `_disconnect_target()`).
  - Explicit error and exception handling when connecting to the target device.

## [0.1.3] - 2025-12-14

### Added
- **Network Scanning for JLink Remote Servers** - `bmlab-scan` now supports scanning IP networks
  - New `--network` parameter accepts CIDR notation (e.g., `192.168.1.0/24`)
  - New `--start-ip` and `--end-ip` parameters for specifying IP range by last octet
  - Sequential scanning to avoid segmentation faults
  - Socket-based pre-check (port 19020) before attempting JLink connection
  - Automatic target detection for remote servers
  - Example: `bmlab-scan --network 192.168.1.0/24 --start-ip 100 --end-ip 150`

### Fixed
- **Communication timeout errors during network scan** - Added proper exception handling for timeout errors during JLink disconnect in network scanning
- **Serial key error in network scan** - Fixed output logic to properly separate network scan results from USB scan results

## [0.1.2] - 2025-12-13

### Added
- **Unified Logging Control** - Added `--log-level` (`-l`) parameter to all CLI tools
  - Supports DEBUG, INFO, WARNING (default), ERROR levels
  - Available in `bmlab-flash`, `bmlab-jlink-rtt`, and `bmlab-erase`
  - Programmatic API: `log_level` parameter in `JLinkProgrammer.__init__()`

### Changed
- **Removed `do_verify` parameter** - Flash verification is always enabled (built into pylink flash_file)
- **Removed `-v/--verbose` flags** - Replaced with `--log-level` for consistent logging control
- **Improved RTT workflow** - `start_rtt()` now handles connection and reset automatically
  - No need to manually call `_connect_target()` before RTT operations
  - Simplified RTT CLI code

### Fixed
- **Communication timeout errors suppressed** - Changed pylink logger to CRITICAL level to hide harmless timeout errors during disconnect
- **RTT connection loss detection** - RTT read errors now properly disconnect instead of infinite error loop
  - Graceful exit when JLinkRemoteServer is closed
  - Clear error message: "RTT connection lost"
- **Better error handling** - RTT read exceptions are propagated to allow proper cleanup

## [0.1.1] - 2025-12-11

### Fixed
- **Linux Segmentation Fault with IP Connections** - Fixed critical bug causing segfault on Linux when using `bmlab-jlink-rtt --ip`
  - Skip USB device enumeration for IP connections (not applicable for network JLink)
  - Skip `set_tif()` and `connect()` calls for IP connections (handled by JLink Remote Server)
  - Skip `reset()` operation for IP connections to avoid crashes
  - IP connections now use remote server's existing target connection instead of attempting reconnection

### Changed
- Improved IP connection handling for better stability on Linux systems
- IP connections now display "Remote Target" as MCU name when not explicitly specified

## [0.1.0] - 2025-11-22

### Added
- Command-line interface with `bmlab-flash` command
- `bmlab-erase` command for erasing device flash memory
- `erase()` method in Programmer base class and JLinkProgrammer implementation
- Device erase CLI with support for auto-detection and manual configuration
- Support for erasing via IP address connection

- **RTT Message Sending** - Added retry logic for RTT write operations
  - `bmlab-jlink-rtt` CLI command for real-time device communication
  - `start_rtt()` method to initiate RTT communication
  - `stop_rtt()` method to stop RTT communication
  - `rtt_read()` method to read data from RTT buffers
  - `rtt_write()` method to write data to RTT buffers
  - Support for custom RTT control block addresses
  - Configurable timeouts and delays
  - `--msg-retries` parameter (default: 10) for configurable retry attempts
  - Automatic retry with 1-second delay between attempts
  - Warning message if all retry attempts fail
  - Verbose mode shows retry attempts and success status

- **RTT CLI Features**:
  - Auto-detection of JLink serial and MCU (or specify explicitly)
  - Configurable read timeout (default 10s, 0 for indefinite)
  - Send messages to device via `--msg` parameter
  - Configurable message send delay with `--msg-timeout`
  - Optional target reset control (`--reset` / `--no-reset`)
  - Verbose mode for debugging with `-v` flag
  - Escape sequence support in messages (e.g., `\n`, `\t`)

- **Network JLink Support** - Added ability to connect to JLink via IP address
  - `--ip` parameter in both `bmlab-flash` and `bmlab-jlink-rtt` CLI commands
  - `ip_addr` parameter in `JLinkProgrammer` constructor
  - Connection format: `jlink.open(ip_addr="192.168.1.100:19020")`
  - When using IP connection, MCU parameter is not required
  - `--serial` and `--ip` are mutually exclusive parameters
  - Full support for flashing and RTT communication over network
