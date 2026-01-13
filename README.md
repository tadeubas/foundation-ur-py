# [Foundation Devices Python UR Library](https://github.com/Foundation-Devices/foundation-ur-py)

**UR Implementation in Python -- ported from the [C++ Reference Implementation by Blockchain Commons](https://github.com/BlockchainCommons/bc-ur)**

## Introduction

URs ("Uniform Resources") are a method for encoding structured binary data for transport in URIs and QR Codes. They are described in [BCR-2020-005](https://github.com/BlockchainCommons/Research/blob/master/papers/bcr-2020-005-ur.md).

There is also another reference implementation in Swift: [URKit](https://github.com/blockchaincommons/URKit), and a demo app that uses it to display and read multi-part animated QR codes: [URDemo](https://github.com/blockchaincommons/URDemo).

## Installation

The code is not yet available in a package format, so just copy the files into your project.

### Dependencies

Either `hashlib` in a normal Python environment or `uhashlib` in MicroPython must be available.

## Use

1. Include the source folder in your Python project

2. Import the encoder and decoder:
    ```
    from ur.ur_encoder import UREncoder
    from ur.ur_decoder import URDecoder
    ```

3. Write some test code:

    ```
        ur = make_message_ur(32767)
        max_fragment_len = 1000
        first_seq_num = 100
        encoder = UREncoder(ur, max_fragment_len, first_seq_num)
        decoder = URDecoder()
        while True:
            part = encoder.next_part()
            decoder.receive_part(part)
            if decoder.is_complete():
                break

        if decoder.is_success():
            assert(decoder.result == ur)
        else:
            print('{}'.format(decoder.result))
            assert(False)
    ```

## Notes for Maintainers

Before accepting a PR that can affect build or unit tests, make sure the following command succeeds:

Development **install**:
```
poetry install
```

Execute **tests**:
```
poetry run pytest test.py
```

See **coverage**:
```
poetry run pytest --cov=ur --cov-report=term-missing --cov-report=html
```

Ensure that you add new unit tests for new or modified functionality.

**Before commit, check pylint and vulture**:
```
poetry run pylint src
poetry run vulture src
```

Remember to **format new files with black**:
```
poetry run black src/ur/<new_file.py>
```

## Origin, Authors, Copyright & Licenses

Unless otherwise noted (either in this [/README.md](./README.md) or in the file's header comments) the contents of this repository are Copyright © 2020 Foundation Devices, Inc. and Contributors, and are [licensed](./LICENSE) under the [spdx:BSD-2-Clause Plus Patent License](https://spdx.org/licenses/BSD-2-Clause-Patent.html).

This code is a Python port of the original C++ reference implementation by Blockchain Commons.  See
[Blockchain Commons UR Library](https://github.com/BlockchainCommons/bc-ur) for the original version.

## Contributing

We encourage public contributions through issues and pull-requests! Please review [CONTRIBUTING.md](./CONTRIBUTING.md) for details on our development process.

## Version History

### 0.1.0, 08/20/2020 - Initial release

* Initial testing release.
