use crate::{DtmfKey as RustDtmfKey, DtmfTable as RustDtmfTable, DtmfTone as RustDtmfTone};
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
extern crate std;
use std::collections::hash_map::DefaultHasher;
use std::format;
use std::hash::{Hash, Hasher};

/// A DTMF (Dual-Tone Multi-Frequency) key representing telephony keypad buttons.
///
/// DtmfKey represents one of the 16 standard DTMF keys used in telephony systems:
/// - Digits 0-9
/// - Special characters * and #
/// - Letters A-D (extended keypad)
///
/// Each key corresponds to a unique pair of low and high frequency tones.
///
/// Examples:
///     >>> from dtmf_table import DtmfKey
///     >>> key = DtmfKey.from_char('5')
///     >>> key.to_char()
///     '5'
///     >>> low, high = key.freqs()
///     >>> (low, high)
///     (770, 1336)
#[pyclass(name = "DtmfKey", module = "dtmf_table")]
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct PyDtmfKey {
    inner: RustDtmfKey,
}

#[pymethods]
impl PyDtmfKey {
    /// Create a DtmfKey from a character.
    ///
    /// Args:
    ///     c (str): Single character representing the DTMF key ('0'-'9', '*', '#', 'A'-'D')
    ///
    /// Returns:
    ///     DtmfKey: The corresponding DTMF key
    ///
    /// Raises:
    ///     ValueError: If the character is not a valid DTMF key
    #[staticmethod]
    #[pyo3(signature = (c), text_signature = "(c: str) -> DtmfKey")]
    fn from_char(c: char) -> PyResult<Self> {
        match RustDtmfKey::from_char(c) {
            Some(key) => Ok(PyDtmfKey { inner: key }),
            None => Err(PyValueError::new_err(format!(
                "Invalid DTMF character: '{}'",
                c
            ))),
        }
    }

    /// Convert the DtmfKey to its character representation.
    ///
    /// Returns:
    ///     str: Single character representing the key
    #[pyo3(signature = (), text_signature = "($self) -> str")]
    fn to_char(&self) -> char {
        self.inner.to_char()
    }

    /// Get the canonical frequencies for this DTMF key.
    ///
    /// Returns:
    ///     tuple[int, int]: (low_frequency_hz, high_frequency_hz)
    #[pyo3(signature = (), text_signature = "($self) -> tuple[int, int]")]
    fn freqs(&self) -> (u16, u16) {
        self.inner.freqs()
    }

    fn __str__(&self) -> String {
        self.inner.to_char().to_string()
    }

    fn __repr__(&self) -> String {
        format!("DtmfKey('{}')", self.inner.to_char())
    }

    fn __eq__(&self, other: &PyDtmfKey) -> bool {
        self.inner == other.inner
    }

    fn __hash__(&self) -> u64 {
        let mut hasher = DefaultHasher::new();
        self.inner.hash(&mut hasher);
        hasher.finish()
    }
}

/// A DTMF tone containing a key and its associated frequency pair.
///
/// DtmfTone represents the complete information for a DTMF signal:
/// the key character and its corresponding low and high frequencies.
/// This is useful for iterating over all possible tones or when you need
/// both the key and frequency information together.
///
/// Examples:
///     >>> from dtmf_table import DtmfTable
///     >>> tones = DtmfTable.all_tones()
///     >>> tone = tones[0]  # First tone
///     >>> print(tone)
///     1: (697 Hz, 1209 Hz)
///     >>> tone.key.to_char()
///     '1'
///     >>> (tone.low_hz, tone.high_hz)
///     (697, 1209)
#[pyclass(name = "DtmfTone", module = "dtmf_table")]
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct PyDtmfTone {
    inner: RustDtmfTone,
}

#[pymethods]
impl PyDtmfTone {
    /// Create a new DtmfTone.
    ///
    /// Args:
    ///     key (DtmfKey): The DTMF key
    ///     low_hz (int): Low frequency in Hz
    ///     high_hz (int): High frequency in Hz
    #[new]
    #[pyo3(signature = (key, low_hz, high_hz), text_signature = "(key: DtmfKey, low_hz: int, high_hz: int)")]
    fn new(key: PyDtmfKey, low_hz: u16, high_hz: u16) -> Self {
        PyDtmfTone {
            inner: RustDtmfTone {
                key: key.inner,
                low_hz,
                high_hz,
            },
        }
    }

    /// The DTMF key for this tone.
    #[getter]
    fn key(&self) -> PyDtmfKey {
        PyDtmfKey {
            inner: self.inner.key,
        }
    }

    /// Low frequency in Hz.
    #[getter]
    fn low_hz(&self) -> u16 {
        self.inner.low_hz
    }

    /// High frequency in Hz.
    #[getter]
    fn high_hz(&self) -> u16 {
        self.inner.high_hz
    }

    fn __str__(&self) -> String {
        format!(
            "{}: ({} Hz, {} Hz)",
            self.inner.key.to_char(),
            self.inner.low_hz,
            self.inner.high_hz
        )
    }

    fn __repr__(&self) -> String {
        format!(
            "DtmfTone(key=DtmfKey('{}'), low_hz={}, high_hz={})",
            self.inner.key.to_char(),
            self.inner.low_hz,
            self.inner.high_hz
        )
    }

    fn __eq__(&self, other: &PyDtmfTone) -> bool {
        self.inner == other.inner
    }
}

/// DTMF frequency lookup table for audio processing applications.
///
/// DtmfTable provides efficient bidirectional mapping between DTMF keys and their
/// canonical frequency pairs. It supports exact lookups, tolerance-based matching
/// for real-world audio analysis, and frequency snapping for noisy estimates.
///
/// The table contains all 16 standard DTMF frequencies used in telephony:
///
/// =======  =======  =======  =======  =======
///          1209 Hz  1336 Hz  1477 Hz  1633 Hz
/// =======  =======  =======  =======  =======
/// 697 Hz      1        2        3        A
/// 770 Hz      4        5        6        B
/// 852 Hz      7        8        9        C
/// 941 Hz      *        0        #        D
/// =======  =======  =======  =======  =======
///
/// Examples:
///     Basic usage:
///
///     >>> from dtmf_table import DtmfTable, DtmfKey
///     >>> table = DtmfTable()
///     >>>
///     >>> # Forward lookup: key to frequencies
///     >>> key = DtmfKey.from_char('5')
///     >>> low, high = table.lookup_key(key)
///     >>> (low, high)
///     (770, 1336)
///
///     Real-world audio analysis:
///
///     >>> # Reverse lookup with tolerance (from FFT peaks)
///     >>> key = table.from_pair_tol_f64(770.2, 1335.8, 5.0)
///     >>> key.to_char() if key else None
///     '5'
///     >>>
///     >>> # Snap noisy frequencies to nearest canonical values
///     >>> key, low, high = table.nearest_u32(768, 1340)
///     >>> (key.to_char(), low, high)
///     ('5', 770, 1336)
#[pyclass(name = "DtmfTable", module = "dtmf_table")]
#[derive(Debug)]
pub struct PyDtmfTable {
    inner: RustDtmfTable,
}

#[pymethods]
impl PyDtmfTable {
    /// Create a new DTMF table instance.
    #[new]
    #[pyo3(signature = (), text_signature = "()")]
    fn new() -> Self {
        PyDtmfTable {
            inner: RustDtmfTable::new(),
        }
    }

    /// Get all DTMF keys in keypad order.
    ///
    /// Returns:
    ///     list[DtmfKey]: All 16 DTMF keys
    #[staticmethod]
    #[pyo3(signature = (), text_signature = "() -> list[DtmfKey]")]
    fn all_keys() -> Vec<PyDtmfKey> {
        RustDtmfTable::ALL_KEYS
            .iter()
            .map(|&key| PyDtmfKey { inner: key })
            .collect()
    }

    /// Get all DTMF tones in keypad order.
    ///
    /// Returns:
    ///     list[DtmfTone]: All 16 DTMF tones
    #[staticmethod]
    #[pyo3(signature = (), text_signature = "() -> list[DtmfTone]")]
    fn all_tones() -> Vec<PyDtmfTone> {
        RustDtmfTable::ALL_TONES
            .iter()
            .map(|&tone| PyDtmfTone { inner: tone })
            .collect()
    }

    /// Look up frequencies for a given key.
    ///
    /// Args:
    ///     key (DtmfKey): The DTMF key to look up
    ///
    /// Returns:
    ///     tuple[int, int]: (low_frequency_hz, high_frequency_hz)
    #[staticmethod]
    #[pyo3(signature = (key), text_signature = "(key: DtmfKey) -> tuple[int, int]")]
    fn lookup_key(key: PyDtmfKey) -> (u16, u16) {
        RustDtmfTable::lookup_key(key.inner)
    }

    /// Find DTMF key from exact frequency pair.
    ///
    /// Args:
    ///     low (int): Low frequency in Hz
    ///     high (int): High frequency in Hz
    ///
    /// Returns:
    ///     DtmfKey or None: The matching key, or None if no exact match
    #[staticmethod]
    #[pyo3(signature = (low, high), text_signature = "(low: int, high: int) -> DtmfKey | None")]
    fn from_pair_exact(low: u16, high: u16) -> Option<PyDtmfKey> {
        RustDtmfTable::from_pair_exact(low, high).map(|key| PyDtmfKey { inner: key })
    }

    /// Find DTMF key from frequency pair with automatic order normalization.
    ///
    /// Args:
    ///     a (int): First frequency in Hz
    ///     b (int): Second frequency in Hz
    ///
    /// Returns:
    ///     DtmfKey or None: The matching key, or None if no exact match
    #[staticmethod]
    #[pyo3(signature = (a, b), text_signature = "(a: int, b: int) -> DtmfKey | None")]
    fn from_pair_normalised(a: u16, b: u16) -> Option<PyDtmfKey> {
        RustDtmfTable::from_pair_normalised(a, b).map(|key| PyDtmfKey { inner: key })
    }

    /// Find DTMF key from frequency pair with tolerance (integer version).
    ///
    /// Args:
    ///     low (int): Low frequency in Hz
    ///     high (int): High frequency in Hz
    ///     tol_hz (int): Tolerance in Hz
    ///
    /// Returns:
    ///     DtmfKey or None: The matching key within tolerance, or None
    #[pyo3(signature = (low, high, tol_hz), text_signature = "(low: int, high: int, tol_hz: int) -> DtmfKey | None")]
    fn from_pair_tol_u32(&self, low: u32, high: u32, tol_hz: u32) -> Option<PyDtmfKey> {
        self.inner
            .from_pair_tol_u32(low, high, tol_hz)
            .map(|key| PyDtmfKey { inner: key })
    }

    /// Find DTMF key from frequency pair with tolerance (float version).
    ///
    /// Args:
    ///     low (float): Low frequency in Hz
    ///     high (float): High frequency in Hz
    ///     tol_hz (float): Tolerance in Hz
    ///
    /// Returns:
    ///     DtmfKey or None: The matching key within tolerance, or None
    #[pyo3(signature = (low, high, tol_hz), text_signature = "($self, low: float, high: float, tol_hz: float) -> DtmfKey | None")]
    fn from_pair_tol_f64(&self, low: f64, high: f64, tol_hz: f64) -> Option<PyDtmfKey> {
        self.inner
            .from_pair_tol_f64(low, high, tol_hz)
            .map(|key| PyDtmfKey { inner: key })
    }

    /// Find the nearest DTMF key and snap frequencies to canonical values (integer version).
    ///
    /// Args:
    ///     low (int): Low frequency estimate in Hz
    ///     high (int): High frequency estimate in Hz
    ///
    /// Returns:
    ///     tuple[DtmfKey, int, int]: (key, snapped_low_hz, snapped_high_hz)
    #[pyo3(signature = (low, high), text_signature = "($self, low: int, high: int) -> tuple[DtmfKey, int, int]")]
    fn nearest_u32(&self, low: u32, high: u32) -> (PyDtmfKey, u16, u16) {
        let (key, snapped_low, snapped_high) = self.inner.nearest_u32(low, high);
        (PyDtmfKey { inner: key }, snapped_low, snapped_high)
    }

    /// Find the nearest DTMF key and snap frequencies to canonical values (float version).
    ///
    /// Args:
    ///     low (float): Low frequency estimate in Hz
    ///     high (float): High frequency estimate in Hz
    ///
    /// Returns:
    ///     tuple[DtmfKey, int, int]: (key, snapped_low_hz, snapped_high_hz)
    #[pyo3(signature = (low, high), text_signature = "($self, low: float, high: float) -> tuple[DtmfKey, int, int]")]
    fn nearest_f64(&self, low: f64, high: f64) -> (PyDtmfKey, u16, u16) {
        let (key, snapped_low, snapped_high) = self.inner.nearest_f64(low, high);
        (PyDtmfKey { inner: key }, snapped_low, snapped_high)
    }

    fn __str__(&self) -> String {
        format!("{:#}", self.inner)
    }

    fn __repr__(&self) -> String {
        "DtmfTable()".to_string()
    }
}

/// Initialize the Python module
#[pymodule]
fn dtmf_table(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyDtmfKey>()?;
    m.add_class::<PyDtmfTone>()?;
    m.add_class::<PyDtmfTable>()?;

    // Add module-level constants
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
    m.add(
        "__doc__",
        r#"DTMF (Dual-Tone Multi-Frequency) frequency table for telephony applications.

This library provides efficient, const-first mappings between DTMF keys and their
canonical frequency pairs. Built with Rust for performance, it offers both exact
lookups and tolerance-based matching for real-world audio analysis.

Key Features:
- Zero-allocation const-evaluated mappings
- Bidirectional key ⟷ frequency conversion
- Tolerance-based reverse lookup for FFT analysis
- Frequency snapping for noisy estimates
- Support for all 16 standard DTMF tones

Classes:
    DtmfKey: Represents a single DTMF key (0-9, *, #, A-D)
    DtmfTone: Combines a key with its frequency pair
    DtmfTable: Main lookup table for conversions and analysis

Example:
    >>> from dtmf_table import DtmfTable, DtmfKey
    >>> table = DtmfTable()
    >>> key = DtmfKey.from_char('5')
    >>> low, high = key.freqs()
    >>> print(f"Key {key} = {low}Hz + {high}Hz")
    Key 5 = 770Hz + 1336Hz
"#,
    )?;

    Ok(())
}
