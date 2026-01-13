# nmrkit

nmrkit is a lightweight Python library for nuclear magnetic resonance (NMR) data processing and analysis. It provides a simple API for common NMR data manipulation tasks, enabling efficient processing and visualization of NMR spectra.

This is an early-stage project under active development. Contributions are welcome to help expand its capabilities!

## Features

- **Data Import/Export**: Support for common NMR formats including TopSpin and Delta
- **Basic Processing**: Fourier transform, apodization (exponential multiplication), zero filling, phase correction
- **Visualization**: Interactive plotting with customizable parameters
- **Simple API**: Intuitive functions for data processing workflows
- **Lightweight**: Minimal dependencies

## Installation

```bash
pip install nmrkit
```

## Quick Start

### Automatic Processing

Use the `auto_process` function for automated application of common processing steps:

```python
import nmrkit as nk

# Load NMR data
data = nk.read('path/to/data')

# Automatically process the spectrum
data = nk.auto_process(data)

# Save the plot to a PDF file
nk.plot(data, output_path="spectrum.pdf")
```

### Manual Processing

For more control, use individual processing functions:

```python
import nmrkit as nk

# Load data with explicit format specification
data = nk.read('path/to/data.jdf', format='delta')

# Apply exponential multiplication (apodization) with 1.0 Hz line broadening
data = nk.em(data, lb=1.0)

# Zero fill to 2048 points for improved resolution
data = nk.zf(data, size=2048)

# Perform Fourier transform
data = nk.ft(data)

# Apply phase correction
data = nk.phase(data, ph0=10.0, ph1=25.0)

# Plot the manually processed spectrum
nk.plot(data)
```

## License

nmrkit is released under the MIT License. See the [LICENSE](LICENSE) file for more information.

## Contributing

The nmrkit project welcomes your expertise and enthusiasm!

### Reporting Issues

If you encounter a bug or have an idea for a new feature, please open an issue on GitHub. When reporting bugs, include as much detail as possible to help us understand and address the issue.

### Contributing Code

To contribute code to nmrkit:

1. Fork the repository
2. Create a new branch for your feature or bug fix
3. Implement your changes
4. Submit a pull request

Please follow the existing code style before submitting a pull request.

Small improvements or fixes are always appreciated. Even minor contributions can make a significant difference!

## Contact

- **GitHub Repository**: https://github.com/jiekangtian/nmrkit

