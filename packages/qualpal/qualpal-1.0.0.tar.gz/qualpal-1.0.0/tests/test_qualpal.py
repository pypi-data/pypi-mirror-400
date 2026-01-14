"""Tests for Qualpal class."""

from __future__ import annotations

import pytest

from qualpal import Qualpal


class TestQualpalInitialization:
    """Test Qualpal initialization."""

    def test_default_initialization(self):
        """Test creating Qualpal with no arguments uses default colorspace."""
        qp = Qualpal()

        # Should have default colorspace
        assert qp._colorspace == {"h": (0, 360), "s": (0, 1), "l": (0, 1)}
        assert qp._space == "hsl"
        assert qp._colors is None
        assert qp._palette is None

    def test_colors_initialization(self):
        """Test creating Qualpal with colors list."""
        colors = ["#ff0000", "#00ff00", "#0000ff"]
        qp = Qualpal(colors=colors)

        assert qp._colors == colors
        assert qp._colorspace is None
        assert qp._palette is None

    def test_colorspace_initialization(self):
        """Test creating Qualpal with colorspace dict."""
        colorspace = {"h": (0, 180), "s": (0.5, 1), "l": (0.3, 0.7)}
        qp = Qualpal(colorspace=colorspace)

        assert qp._colorspace == colorspace
        assert qp._colors is None
        assert qp._palette is None

    def test_palette_initialization(self):
        """Test creating Qualpal with palette name."""
        qp = Qualpal(palette="ColorBrewer:Set1")

        assert qp._palette == "ColorBrewer:Set1"
        assert qp._colors is None
        assert qp._colorspace is None


class TestMutualExclusivity:
    """Test mutual exclusivity of colors, colorspace, and palette."""

    def test_colors_and_colorspace_exclusive(self):
        """Test that colors and colorspace cannot both be provided."""
        with pytest.raises(
            ValueError, match="Provide only one of: colors, colorspace, or palette"
        ):
            Qualpal(
                colors=["#ff0000"], colorspace={"h": (0, 360), "s": (0, 1), "l": (0, 1)}
            )

    def test_colors_and_palette_exclusive(self):
        """Test that colors and palette cannot both be provided."""
        with pytest.raises(
            ValueError, match="Provide only one of: colors, colorspace, or palette"
        ):
            Qualpal(colors=["#ff0000"], palette="ColorBrewer:Set1")

    def test_colorspace_and_palette_exclusive(self):
        """Test that colorspace and palette cannot both be provided."""
        with pytest.raises(
            ValueError, match="Provide only one of: colors, colorspace, or palette"
        ):
            Qualpal(
                colorspace={"h": (0, 360), "s": (0, 1), "l": (0, 1)},
                palette="ColorBrewer:Set1",
            )

    def test_all_three_exclusive(self):
        """Test that all three cannot be provided together."""
        with pytest.raises(
            ValueError, match="Provide only one of: colors, colorspace, or palette"
        ):
            Qualpal(
                colors=["#ff0000"],
                colorspace={"h": (0, 360), "s": (0, 1), "l": (0, 1)},
                palette="ColorBrewer:Set1",
            )


class TestColorspaceValidation:
    """Test colorspace parameter validation."""

    def test_colorspace_hsl_valid(self):
        """Test valid HSL colorspace."""
        colorspace = {"h": (0, 360), "s": (0, 1), "l": (0, 1)}
        qp = Qualpal(colorspace=colorspace, space="hsl")  # type: ignore[arg-type]

        assert qp._colorspace == colorspace
        assert qp._space == "hsl"

    def test_colorspace_lchab_valid(self):
        """Test valid LCHab colorspace."""
        colorspace = {"h": (-180, 180), "c": (0, 100), "l": (0, 100)}
        qp = Qualpal(colorspace=colorspace, space="lchab")  # type: ignore[arg-type]

        assert qp._colorspace == colorspace
        assert qp._space == "lchab"

    def test_colorspace_invalid_space(self):
        """Test invalid space parameter."""
        with pytest.raises(ValueError, match="space must be 'hsl' or 'lchab'"):
            Qualpal(
                colorspace={"h": (0, 360), "s": (0, 1), "l": (0, 1)}, space="invalid"
            )

    def test_colorspace_not_dict(self):
        """Test colorspace must be a dict."""
        with pytest.raises(TypeError, match="colorspace must be a dict"):
            Qualpal(colorspace=[(0, 360), (0, 1), (0, 1)])  # type: ignore[arg-type]

    def test_colorspace_missing_keys_hsl(self):
        """Test HSL colorspace with missing keys."""
        with pytest.raises(ValueError, match="colorspace must have keys"):
            Qualpal(colorspace={"h": (0, 360), "s": (0, 1)}, space="hsl")

    def test_colorspace_extra_keys_hsl(self):
        """Test HSL colorspace with extra keys."""
        with pytest.raises(ValueError, match="colorspace must have keys"):
            Qualpal(
                colorspace={"h": (0, 360), "s": (0, 1), "l": (0, 1), "extra": (0, 1)},
                space="hsl",
            )

    def test_colorspace_wrong_keys_lchab(self):
        """Test LCHab colorspace with wrong keys (using HSL keys)."""
        with pytest.raises(ValueError, match="colorspace must have keys"):
            Qualpal(colorspace={"h": (0, 360), "s": (0, 1), "l": (0, 1)}, space="lchab")

    def test_colorspace_non_numeric_range(self):
        """Test colorspace with non-numeric range values."""
        with pytest.raises(TypeError, match="range must be numeric"):
            Qualpal(colorspace={"h": ("0", "360"), "s": (0, 1), "l": (0, 1)})  # type: ignore[arg-type]

    def test_colorspace_min_greater_than_max(self):
        """Test colorspace with min >= max."""
        with pytest.raises(ValueError, match="min must be < max"):
            Qualpal(colorspace={"h": (360, 0), "s": (0, 1), "l": (0, 1)})

    def test_colorspace_min_equals_max(self):
        """Test colorspace with min == max."""
        with pytest.raises(ValueError, match="min must be < max"):
            Qualpal(colorspace={"h": (0, 360), "s": (0.5, 0.5), "l": (0, 1)})

    def test_colorspace_invalid_tuple_length(self):
        """Test colorspace with wrong tuple length."""
        with pytest.raises(TypeError, match="must be a tuple/list of length 2"):
            Qualpal(colorspace={"h": (0, 180, 360), "s": (0, 1), "l": (0, 1)})  # type: ignore[arg-type]


class TestPaletteValidation:
    """Test palette parameter validation."""

    def test_palette_valid_format(self):
        """Test palette with valid format."""
        qp = Qualpal(palette="ColorBrewer:Set1")

        assert qp._palette == "ColorBrewer:Set1"

    def test_palette_missing_colon(self):
        """Test palette without colon separator."""
        with pytest.raises(ValueError, match="palette must be in format 'source:name'"):
            Qualpal(palette="ColorBrewerSet1")


class TestCVDProperty:
    """Test cvd property and setter."""

    def test_cvd_default_none(self):
        """Test cvd default is None."""
        qp = Qualpal()

        assert qp.cvd is None

    def test_cvd_set_valid(self):
        """Test setting valid cvd."""
        qp = Qualpal()
        qp.cvd = {"protan": 0.5}

        assert qp.cvd == {"protan": 0.5}

    def test_cvd_set_multiple_types(self):
        """Test setting multiple CVD types."""
        qp = Qualpal()
        qp.cvd = {"protan": 0.5, "deutan": 0.2, "tritan": 0.8}

        assert qp.cvd == {"protan": 0.5, "deutan": 0.2, "tritan": 0.8}

    def test_cvd_init_valid(self):
        """Test setting cvd in __init__."""
        qp = Qualpal(cvd={"protan": 1.0})

        assert qp.cvd == {"protan": 1.0}

    def test_cvd_not_dict(self):
        """Test cvd must be a dict."""
        qp = Qualpal()

        with pytest.raises(TypeError, match="cvd must be a dict"):
            qp.cvd = [("protan", 0.5)]  # type: ignore[assignment]

    def test_cvd_invalid_key(self):
        """Test cvd with invalid key."""
        qp = Qualpal()

        with pytest.raises(ValueError, match="cvd keys must be in"):
            qp.cvd = {"invalid": 0.5}

    def test_cvd_non_numeric_value(self):
        """Test cvd with non-numeric value."""
        qp = Qualpal()

        with pytest.raises(TypeError, match="must be a number"):
            qp.cvd = {"protan": "0.5"}  # type: ignore[dict-item]

    def test_cvd_value_below_zero(self):
        """Test cvd with value below 0.0."""
        qp = Qualpal()

        with pytest.raises(ValueError, match=r"must be between 0\.0 and 1\.0"):
            qp.cvd = {"protan": -0.1}

    def test_cvd_value_above_one(self):
        """Test cvd with value above 1.0."""
        qp = Qualpal()

        with pytest.raises(ValueError, match=r"must be between 0\.0 and 1\.0"):
            qp.cvd = {"protan": 1.1}

    def test_cvd_set_to_none(self):
        """Test setting cvd back to None."""
        qp = Qualpal(cvd={"protan": 0.5})
        qp.cvd = None

        assert qp.cvd is None


class TestMetricProperty:
    """Test metric property and setter."""

    def test_metric_default(self):
        """Test metric default is ciede2000."""
        qp = Qualpal()

        assert qp.metric == "ciede2000"

    def test_metric_set_valid(self):
        """Test setting valid metric."""
        qp = Qualpal()
        qp.metric = "din99d"

        assert qp.metric == "din99d"

    def test_metric_init_valid(self):
        """Test setting metric in __init__."""
        qp = Qualpal(metric="cie76")

        assert qp.metric == "cie76"

    def test_metric_invalid(self):
        """Test setting invalid metric."""
        qp = Qualpal()

        with pytest.raises(ValueError, match="metric must be one of"):
            qp.metric = "invalid"


class TestBackgroundProperty:
    """Test background property and setter."""

    def test_background_default_none(self):
        """Test background default is None."""
        qp = Qualpal()

        assert qp.background is None

    def test_background_set_valid(self):
        """Test setting valid background."""
        qp = Qualpal()
        qp.background = "#ffffff"

        assert qp.background == "#ffffff"

    def test_background_init_valid(self):
        """Test setting background in __init__."""
        qp = Qualpal(background="#000000")

        assert qp.background == "#000000"

    def test_background_not_string(self):
        """Test background must be a string."""
        qp = Qualpal()

        with pytest.raises(TypeError, match="background must be a hex string"):
            qp.background = 123  # type: ignore[assignment]

    def test_background_invalid_format_no_hash(self):
        """Test background with invalid format (no #)."""
        qp = Qualpal()

        with pytest.raises(ValueError, match="Invalid hex color"):
            qp.background = "ffffff"

    def test_background_invalid_format_too_short(self):
        """Test background with invalid format (too short)."""
        qp = Qualpal()

        with pytest.raises(ValueError, match="Invalid hex color"):
            qp.background = "#fff"

    def test_background_invalid_format_invalid_chars(self):
        """Test background with invalid characters."""
        qp = Qualpal()

        with pytest.raises(ValueError, match="Invalid hex color"):
            qp.background = "#gggggg"

    def test_background_set_to_none(self):
        """Test setting background back to None."""
        qp = Qualpal(background="#ffffff")
        qp.background = None

        assert qp.background is None


class TestMaxMemoryProperty:
    """Test max_memory property and setter."""

    def test_max_memory_default(self):
        """Test max_memory default is 1.0."""
        qp = Qualpal()

        assert qp.max_memory == 1.0

    def test_max_memory_set_valid(self):
        """Test setting valid max_memory."""
        qp = Qualpal()
        qp.max_memory = 2.5

        assert qp.max_memory == 2.5

    def test_max_memory_init_valid(self):
        """Test setting max_memory in __init__."""
        qp = Qualpal(max_memory=0.5)

        assert qp.max_memory == 0.5

    def test_max_memory_int_converted_to_float(self):
        """Test int max_memory is converted to float."""
        qp = Qualpal(max_memory=2)

        assert qp.max_memory == 2.0
        assert isinstance(qp.max_memory, float)

    def test_max_memory_not_numeric(self):
        """Test max_memory must be numeric."""
        qp = Qualpal()

        with pytest.raises(TypeError, match="max_memory must be a number"):
            qp.max_memory = "1.0"  # type: ignore[assignment]

    def test_max_memory_zero(self):
        """Test max_memory must be positive (not zero)."""
        qp = Qualpal()

        with pytest.raises(ValueError, match="max_memory must be positive"):
            qp.max_memory = 0

    def test_max_memory_negative(self):
        """Test max_memory must be positive (not negative)."""
        qp = Qualpal()

        with pytest.raises(ValueError, match="max_memory must be positive"):
            qp.max_memory = -1.0


class TestColorspaceSizeProperty:
    """Test colorspace_size property and setter."""

    def test_colorspace_size_default(self):
        """Test colorspace_size default is 1000."""
        qp = Qualpal()

        assert qp.colorspace_size == 1000

    def test_colorspace_size_set_valid(self):
        """Test setting valid colorspace_size."""
        qp = Qualpal()
        qp.colorspace_size = 5000

        assert qp.colorspace_size == 5000

    def test_colorspace_size_init_valid(self):
        """Test setting colorspace_size in __init__."""
        qp = Qualpal(colorspace_size=2000)

        assert qp.colorspace_size == 2000

    def test_colorspace_size_not_int(self):
        """Test colorspace_size must be int."""
        qp = Qualpal()

        with pytest.raises(TypeError, match="colorspace_size must be an integer"):
            qp.colorspace_size = 1000.5  # type: ignore[assignment]

    def test_colorspace_size_zero(self):
        """Test colorspace_size must be positive (not zero)."""
        qp = Qualpal()

        with pytest.raises(ValueError, match="colorspace_size must be positive"):
            qp.colorspace_size = 0

    def test_colorspace_size_negative(self):
        """Test colorspace_size must be positive (not negative)."""
        qp = Qualpal()

        with pytest.raises(ValueError, match="colorspace_size must be positive"):
            qp.colorspace_size = -100


class TestComplexScenarios:
    """Test complex initialization scenarios."""

    def test_all_parameters_together(self):
        """Test creating Qualpal with all parameters."""
        qp = Qualpal(
            colorspace={"h": (0, 180), "s": (0.5, 1), "l": (0.3, 0.7)},
            space="hsl",
            cvd={"protan": 0.5},
            metric="din99d",
            background="#ffffff",
            max_memory=2.0,
            colorspace_size=5000,
        )

        assert qp._colorspace == {"h": (0, 180), "s": (0.5, 1), "l": (0.3, 0.7)}
        assert qp._space == "hsl"
        assert qp.cvd == {"protan": 0.5}
        assert qp.metric == "din99d"
        assert qp.background == "#ffffff"
        assert qp.max_memory == 2.0
        assert qp.colorspace_size == 5000

    def test_modify_all_properties_after_init(self):
        """Test modifying all properties after initialization."""
        qp = Qualpal()

        qp.cvd = {"deutan": 0.8}
        qp.metric = "cie76"
        qp.background = "#000000"
        qp.max_memory = 0.5
        qp.colorspace_size = 500

        assert qp.cvd == {"deutan": 0.8}
        assert qp.metric == "cie76"
        assert qp.background == "#000000"
        assert qp.max_memory == 0.5
        assert qp.colorspace_size == 500
