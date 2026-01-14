# Shuttle

`shuttle` is a Typer-based command-line interface & python library for interacting with the SPI-to-USB devboard over its NDJSON serial protocol. The tool is packaged as `lr-shuttle` for PyPI distribution and exposes high-level helpers for common workflows such as probing firmware info, querying protocol metadata, and issuing TiMo SPI sequences.


## Installation

```bash
python3 -m pip install lr-shuttle
```

The package supports Python 3.11 and later. When working from this repository you can install it in editable mode:

```bash
make -C host dev
```

## Connecting to the Devboard

- The CLI talks to the board over a serial device supplied via `--port` or the `SHUTTLE_PORT` environment variable (e.g., `/dev/ttyUSB0`).
- Default baud rate is `921600` with a `2s` read timeout. Both can be overridden using `--baud` and `--timeout`.
- Use `--log SERIAL.log` to capture raw RX/TX NDJSON lines with UTC timestamps for later inspection.

## Core Commands

| Command | Description |
| --- | --- |
| `shuttle ping` | Sends a `ping` command to fetch firmware/protocol metadata. |
| `shuttle get-info` | Calls `get.info` and pretty-prints the returned capability snapshot. |
| `shuttle spi-cfg [options]` | Queries or updates the devboard SPI defaults (wraps the `spi.cfg` protocol command). |
| `shuttle uart-cfg [options]` | Queries or updates the devboard UART defaults (wraps the `uart.cfg` protocol command). |
| `shuttle uart-tx [payload]` | Transmits bytes over the devboard UART (wraps the `uart.tx` protocol command). |


### SPI Configuration Workflow

- Run `shuttle spi-cfg --port /dev/ttyUSB0` with no extra flags to fetch the current board-level SPI defaults (the response mirrors the firmware’s `spi` object).
- Provide overrides such as `--hz 1500000 --clock-phase trailing` to persist new defaults in the device’s NVS store. String arguments are case-insensitive; the CLI normalizes them to the lowercase values expected by the firmware.
- If you need to push a raw JSON document (e.g., the sample in [`src/spi.cfg`](../src/spi.cfg)), pipe it through a future send-file helper or `screen`/`cat` directly; `spi-cfg` itself focuses on structured flag input.


### UART Configuration Workflow

- Use `shuttle uart-cfg --port /dev/ttyUSB0` with no overrides to dump the persisted UART defaults (`baudrate`, `stopbits`, `parity`).
- Supply `--baudrate`, `--stopbits`, or `--parity` (accepts `n/none`, `e/even`, `o/odd`) to persist new values. Arguments are validated client-side to match the firmware’s accepted ranges (baudrate 1.2 k–4 M, stopbits 1–2).
- Like the SPI helper, UART updates are persisted to the device’s NVS region, so you only need to run the command when changing settings.

### UART Transmission

- `shuttle uart-tx [HEX] --port /dev/ttyUSB0` forwards a hex-encoded payload to the devboard using the `uart.tx` protocol command. The CLI trims whitespace/underscores and validates the string before sending.
- To avoid manual hex encoding, pass `--text "Hello"` (optionally with `--newline`) to send UTF-8 text, `--file payload.bin` to transmit the raw bytes of a file, or provide `-` as the argument to read from stdin. Exactly one payload source can be used per invocation.
- Use `--uart-port` if a future firmware exposes multiple UART instances; otherwise the option can be omitted and the default device UART is used.
- Responses echo the number of bytes accepted by the firmware, matching the `n` field returned by `uart.tx`.


### Sequence Integrity Checks

Every device message carries a monotonically increasing `seq` counter. Shuttle enforces sequential integrity both within multi-transfer operations and across invocations when requested:

- During a command, any gap in response/event sequence numbers raises a `ShuttleSerialError`, helping you catch dropped frames immediately.
- Pass `--seq-meta /path/to/seq.meta` to persist the last observed sequence number. Subsequent Shuttle runs expect the very next `seq` value; if a gap is detected (for example because the device dropped messages while Shuttle was offline), the CLI exits with an error detailing the missing value.
- The metadata file stores a single integer. Delete it (or point `--seq-meta` to another location) if the device was power-cycled and its counter reset.


### Logging and Diagnostics

- `--log FILE` appends every raw NDJSON line (RX and TX) along with an ISO-8601 timestamp. This is useful for post-run audits or attaching transcripts to bug reports.
- Combine `--log` with `--seq-meta` to maintain both a byte-perfect trace and an audit trail of sequence continuity.
- Rich panels highlight non-`ok` responses and include firmware error codes returned by the device, making it straightforward to spot invalid arguments or transport failures.

### Environment Tips

- Export `SHUTTLE_PORT` in your shell profile to avoid typing `--port` for each command.
- For scripted flows, prefer `shuttle timo read-reg` and `shuttle timo nop` helpers instead of manually streaming raw JSON—they take care of command IDs, transfer framing, and error presentation.
- Use `make -C host test` to run the CLI unit tests and verify local changes before publishing to PyPI.



## TiMo SPI Commands

Commands implementing the SPI protocol as described at [docs.lumenradio.io/timotwo/spi-interface](https://docs.lumenrad.io/timotwo/spi-interface/).

| Command | Description |
| --- | --- |
| `shuttle timo nop` | Issues a single-frame TiMo NOP SPI transfer through the devboard. |
| `shuttle timo read-reg --addr 0x05 --length 2` | Performs the two-phase TiMo register read sequence and decodes the resulting payload/IRQ flags. |
| `shuttle timo write-reg --addr 0x05 --data cafebabe` | Performs the two-phase TiMo register write sequence to write bytes to a register. |
| `shuttle timo read-dmx --length 12` | Reads the latest received DMX values from the TiMo device using a two-phase SPI sequence. |

All commands respect the global options declared on the root CLI (`--log`, `--seq-meta`, `--port`, etc.). Rich tables are used to render human-friendly summaries of responses and decoded payloads.


### TiMo Register Read Example

To read bytes from a TiMo register, use the `read-reg` command. I.e. to read the device name:

```bash
$ shuttle timo read-reg --addr 0x36 --length 12
                    TiMo read-reg
 Status     OK
 Command    spi.xfer (payload phase)
 RX         00 48 65 6c 6c 6f 20 57 6f 72 6c 64 00
 IRQ level  {'level': 'low'}
                      TiMo read-reg
 Address        0x36
 Length         12
 Data           48 65 6c 6c 6f 20 57 6f 72 6c 64 00
 IRQ (command)  0x00
 IRQ (payload)  0x00
 Command RX     00
 Payload RX     00 48 65 6c 6c 6f 20 57 6f 72 6c 64 00
```


### TiMo Register Write Example

To write bytes to a TiMo register, use the `write-reg` command. I.e. to set the device name to `Hello World`:

```bash
shuttle timo write-reg --addr 0x36 --data 48656c6c6f20576f726c6400 --port /dev/ttyUSB0
```

- `--addr` specifies the register address (decimal or 0x-prefixed, 0-63)
- `--data` is a hex string of bytes to write (1-32 bytes)
- `--port` is your serial device

The command will print a summary table with the address, data written, and IRQ flags for each phase. If bit 7 of the IRQ flags is set, the sequence should be retried per the TiMo protocol.


### TiMo DMX Read Example

Read the latest received DMX values from the window set up by the DMX_WINDOW register:

```bash
shuttle timo read-dmx --length 12 --port /dev/ttyUSB0
```

This will print a summary table with the length, data bytes (hex), and IRQ flags for each phase. If bit 7 of the IRQ flags is set, the sequence should be retried per the TiMo protocol.

- `--length` specifies the number of DMX bytes to read (1 - max_transfer_bytes)
- `--port` is your serial device


### Using the Library from Python

Use the transport helpers for HIL tests with explicit request→response pairing:

```python
from shuttle.serial_client import NDJSONSerialClient
from shuttle import timo

with NDJSONSerialClient("/dev/ttyUSB0") as client:
    # Fire a TiMo read-reg using the async API
    commands = timo.read_reg_sequence(address=0x05, length=2)
    responses = [client.send_command("spi.xfer", cmd).result(timeout=1.0) for cmd in commands]
    print("Command RX:", responses[0]["rx"])
    print("Payload RX:", responses[1]["rx"])
```

Legacy helpers (`spi_xfer`, `ping`, etc.) remain for simple sequential calls; prefer `send_command` when you need explicit request→response control.

#### Parsing registers with `REGISTER_MAP`

`REGISTER_MAP` in `shuttle.timo` documents the bit layout of TiMo registers. Example: read the `VERSION` register (0x10) and decode firmware/hardware versions.

```python
from shuttle.serial_client import NDJSONSerialClient
from shuttle import timo

def read_register(client, reg_meta):
    addr = reg_meta["address"]
    length = reg_meta.get("length", 1)
    seq = timo.read_reg_sequence(addr, length)
    responses = [client.send_command("spi.xfer", cmd).result(timeout=1.0) for cmd in seq]
    # The payload frame is in the second response's RX field
    rx_payload = bytes.fromhex(responses[1]["rx"])
    return rx_payload[1:]  # skip IRQ flags byte

with NDJSONSerialClient("/dev/ttyUSB0") as client:
    reg_meta = timo.REGISTER_MAP["VERSION"]
    version_bytes = read_register(client, reg_meta)
    fw_version = timo.slice_bits(version_bytes, *reg_meta["fields"]["FW_VERSION"]["bits"])
    hw_version = timo.slice_bits(version_bytes, *reg_meta["fields"]["HW_VERSION"]["bits"])
    print(f"VERSION: FW={fw_version:#x} HW={hw_version:#x}")
```

Use the field metadata in `timo.REGISTER_MAP` to interpret other registers (e.g., check `REGISTER_MAP[0x01]["fields"]` for status flags).

More examples can be found in the [examples directory](examples/).

### Async-style Command and Event Handling

`NDJSONSerialClient` now dispatches in a background reader thread and exposes futures so you can fan out work without changing the client for new ops:

- `send_command(op, params)` returns a `Future` that resolves to the matching response or raises on timeout/sequence gap. You can issue multiple commands back-to-back and wait later.
- `register_event_listener("ev.name")` returns a subscription whose `.next(timeout=…)` yields each event payload; multiple listeners can subscribe to the same event (e.g., IRQ and DMX streams).

Example HIL sketch:

```python
client = NDJSONSerialClient(port, baudrate=DEFAULT_BAUD, timeout=DEFAULT_TIMEOUT)
irq_sub = client.register_event_listener("spi.irq")
cmd_future = client.send_command("timo.read-reg", {"address": 0x05, "length": 1})

# Wait for either side as your test requires
reg_resp = cmd_future.result(timeout=1)
irq_event = irq_sub.next(timeout=1)
```

Events continue to emit until you close the subscription or client, so you can assert on multiple DMX frames or IRQ edges without recreating listeners.


## Production Test SPI Commands

| Command | Description |
| --- | --- |
| `shuttle prodtest reset` |  |
| `shuttle prodtest ping` |  |
| `shuttle prodtest io-self-test` |  |
