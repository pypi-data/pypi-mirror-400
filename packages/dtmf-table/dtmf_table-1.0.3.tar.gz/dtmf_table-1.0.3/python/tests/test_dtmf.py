"""
Test suite for the dtmf_table Python module.
"""
import pytest
from dtmf_table import DtmfKey, DtmfTable, DtmfTone


class TestDtmfKey:
    """Tests for DtmfKey class."""

    def test_from_char_valid(self):
        """Test creating DtmfKey from valid characters."""
        # Test digits
        for digit in "0123456789":
            key = DtmfKey.from_char(digit)
            assert key.to_char() == digit

        # Test special characters
        star_key = DtmfKey.from_char('*')
        assert star_key.to_char() == '*'

        hash_key = DtmfKey.from_char('#')
        assert hash_key.to_char() == '#'

        # Test letters
        for letter in "ABCD":
            key = DtmfKey.from_char(letter)
            assert key.to_char() == letter

    def test_from_char_invalid(self):
        """Test creating DtmfKey from invalid characters."""
        invalid_chars = ['E', 'F', 'x', '@', '!', ' ']
        for char in invalid_chars:
            with pytest.raises(ValueError, match="Invalid DTMF character"):
                DtmfKey.from_char(char)

        # Test empty string separately (different error message)
        with pytest.raises(ValueError, match="expected a string of length 1"):
            DtmfKey.from_char('')

    def test_to_char(self):
        """Test converting DtmfKey to character."""
        test_chars = "0123456789*#ABCD"
        for char in test_chars:
            key = DtmfKey.from_char(char)
            assert key.to_char() == char

    def test_freqs(self):
        """Test getting frequencies for DTMF keys."""
        # Test some known frequency mappings
        key_5 = DtmfKey.from_char('5')
        low, high = key_5.freqs()
        assert low == 770
        assert high == 1336

        key_1 = DtmfKey.from_char('1')
        low, high = key_1.freqs()
        assert low == 697
        assert high == 1209

        key_hash = DtmfKey.from_char('#')
        low, high = key_hash.freqs()
        assert low == 941
        assert high == 1477

    def test_string_representation(self):
        """Test string representation of DtmfKey."""
        key = DtmfKey.from_char('5')
        assert str(key) == '5'
        assert repr(key) == "DtmfKey('5')"

    def test_equality(self):
        """Test DtmfKey equality."""
        key1 = DtmfKey.from_char('5')
        key2 = DtmfKey.from_char('5')
        key3 = DtmfKey.from_char('6')

        assert key1 == key2
        assert key1 != key3
        assert not (key1 == key3)

    def test_hash(self):
        """Test DtmfKey hashing for use in sets/dicts."""
        key1 = DtmfKey.from_char('5')
        key2 = DtmfKey.from_char('5')
        key3 = DtmfKey.from_char('6')

        # Same keys should have same hash
        assert hash(key1) == hash(key2)

        # Can be used in sets
        key_set = {key1, key2, key3}
        assert len(key_set) == 2  # key1 and key2 are the same


class TestDtmfTone:
    """Tests for DtmfTone class."""

    def test_creation(self):
        """Test creating DtmfTone."""
        key = DtmfKey.from_char('5')
        tone = DtmfTone(key, 770, 1336)

        assert tone.key == key
        assert tone.low_hz == 770
        assert tone.high_hz == 1336

    def test_properties(self):
        """Test DtmfTone properties."""
        key = DtmfKey.from_char('A')
        tone = DtmfTone(key, 697, 1633)

        assert tone.key.to_char() == 'A'
        assert tone.low_hz == 697
        assert tone.high_hz == 1633

    def test_string_representation(self):
        """Test string representation of DtmfTone."""
        key = DtmfKey.from_char('5')
        tone = DtmfTone(key, 770, 1336)

        assert str(tone) == "5: (770 Hz, 1336 Hz)"
        assert repr(tone) == "DtmfTone(key=DtmfKey('5'), low_hz=770, high_hz=1336)"

    def test_equality(self):
        """Test DtmfTone equality."""
        key1 = DtmfKey.from_char('5')
        key2 = DtmfKey.from_char('5')
        key3 = DtmfKey.from_char('6')

        tone1 = DtmfTone(key1, 770, 1336)
        tone2 = DtmfTone(key2, 770, 1336)
        tone3 = DtmfTone(key3, 770, 1477)

        assert tone1 == tone2
        assert tone1 != tone3


class TestDtmfTable:
    """Tests for DtmfTable class."""

    def test_creation(self):
        """Test creating DtmfTable."""
        table = DtmfTable()
        assert table is not None

    def test_all_keys(self):
        """Test getting all DTMF keys."""
        all_keys = DtmfTable.all_keys()
        assert len(all_keys) == 16

        # Check that all expected characters are present
        chars = [key.to_char() for key in all_keys]
        expected_chars = set("0123456789*#ABCD")
        actual_chars = set(chars)
        assert actual_chars == expected_chars

    def test_all_tones(self):
        """Test getting all DTMF tones."""
        all_tones = DtmfTable.all_tones()
        assert len(all_tones) == 16

        # Check that tones match keys
        chars_from_tones = [tone.key.to_char() for tone in all_tones]
        expected_chars = set("0123456789*#ABCD")
        actual_chars = set(chars_from_tones)
        assert actual_chars == expected_chars

    def test_lookup_key(self):
        """Test looking up frequencies for a key."""
        key = DtmfKey.from_char('5')
        low, high = DtmfTable.lookup_key(key)
        assert low == 770
        assert high == 1336

    def test_from_pair_exact(self):
        """Test exact frequency pair lookup."""
        # Valid pair
        key = DtmfTable.from_pair_exact(770, 1336)
        assert key is not None
        assert key.to_char() == '5'

        # Invalid pair
        key = DtmfTable.from_pair_exact(800, 1300)
        assert key is None

    def test_from_pair_normalised(self):
        """Test normalized frequency pair lookup (order independent)."""
        # Normal order
        key1 = DtmfTable.from_pair_normalised(770, 1336)
        assert key1 is not None
        assert key1.to_char() == '5'

        # Reversed order
        key2 = DtmfTable.from_pair_normalised(1336, 770)
        assert key2 is not None
        assert key2.to_char() == '5'

        # Should be the same key
        assert key1 == key2

    def test_from_pair_tol_u32(self):
        """Test tolerance-based lookup with integers."""
        table = DtmfTable()

        # Within tolerance
        key = table.from_pair_tol_u32(772, 1340, 5)
        assert key is not None
        assert key.to_char() == '5'

        # Outside tolerance
        key = table.from_pair_tol_u32(800, 1400, 5)
        assert key is None

        # Edge case: exactly at tolerance
        key = table.from_pair_tol_u32(775, 1341, 5)
        assert key is not None
        assert key.to_char() == '5'

    def test_from_pair_tol_f64(self):
        """Test tolerance-based lookup with floats."""
        table = DtmfTable()

        # Within tolerance (example from FFT bin centers)
        key = table.from_pair_tol_f64(770.2, 1335.6, 6.0)
        assert key is not None
        assert key.to_char() == '5'

        # Outside tolerance
        key = table.from_pair_tol_f64(800.0, 1400.0, 5.0)
        assert key is None

    def test_nearest_u32(self):
        """Test nearest key snapping with integers."""
        table = DtmfTable()

        # Test snapping to nearest frequencies
        key, snapped_low, snapped_high = table.nearest_u32(768, 1342)
        assert key.to_char() == '5'
        assert snapped_low == 770
        assert snapped_high == 1336

    def test_nearest_f64(self):
        """Test nearest key snapping with floats."""
        table = DtmfTable()

        # Test snapping with floating point values
        key, snapped_low, snapped_high = table.nearest_f64(768.5, 1342.3)
        assert key.to_char() == '5'
        assert snapped_low == 770
        assert snapped_high == 1336

    def test_string_representation(self):
        """Test string representation of DtmfTable."""
        table = DtmfTable()
        table_str = str(table)

        # Should contain DTMF information
        assert "DTMF" in table_str
        assert "Hz" in table_str

        # Should contain some key information
        assert "5:" in table_str or "5 " in table_str

    def test_comprehensive_frequency_mapping(self):
        """Test that all standard DTMF frequencies are correctly mapped."""
        # Standard DTMF frequency matrix
        expected_mapping = {
            ('1', 697, 1209), ('2', 697, 1336), ('3', 697, 1477), ('A', 697, 1633),
            ('4', 770, 1209), ('5', 770, 1336), ('6', 770, 1477), ('B', 770, 1633),
            ('7', 852, 1209), ('8', 852, 1336), ('9', 852, 1477), ('C', 852, 1633),
            ('*', 941, 1209), ('0', 941, 1336), ('#', 941, 1477), ('D', 941, 1633),
        }

        for char, expected_low, expected_high in expected_mapping:
            # Test forward lookup
            key = DtmfKey.from_char(char)
            low, high = key.freqs()
            assert low == expected_low, f"Key {char}: expected low {expected_low}, got {low}"
            assert high == expected_high, f"Key {char}: expected high {expected_high}, got {high}"

            # Test reverse lookup
            found_key = DtmfTable.from_pair_exact(expected_low, expected_high)
            assert found_key is not None, f"Could not find key for frequencies {expected_low}, {expected_high}"
            assert found_key.to_char() == char, f"Expected {char}, got {found_key.to_char()}"


if __name__ == "__main__":
    pytest.main([__file__])