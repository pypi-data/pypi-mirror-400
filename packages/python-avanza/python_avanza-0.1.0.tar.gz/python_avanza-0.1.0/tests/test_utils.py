"""
Unit tests for utility functions
"""

import pytest
from avanza.utils import (
    convert_instrument_type,
    convert_time_period,
    InfoDict,
)
from avanza.constants import InstrumentType, TimePeriod


class TestConverters:
    """Test converter functions"""

    def test_convert_instrument_type_string(self):
        """Test converting string to InstrumentType"""
        result = convert_instrument_type("stock")
        assert result == InstrumentType.STOCK

    def test_convert_instrument_type_enum(self):
        """Test passing InstrumentType enum"""
        result = convert_instrument_type(InstrumentType.ETF)
        assert result == InstrumentType.ETF

    def test_convert_instrument_type_invalid(self):
        """Test invalid instrument type raises ValueError"""
        with pytest.raises(ValueError, match="Invalid instrument type"):
            convert_instrument_type("invalid")

    def test_convert_time_period_string(self):
        """Test converting string to TimePeriod"""
        result = convert_time_period("one_month")
        assert result == TimePeriod.ONE_MONTH

    def test_convert_time_period_enum(self):
        """Test passing TimePeriod enum"""
        result = convert_time_period(TimePeriod.ONE_YEAR)
        assert result == TimePeriod.ONE_YEAR

    def test_convert_time_period_invalid(self):
        """Test invalid time period raises ValueError"""
        with pytest.raises(ValueError, match="Invalid time period"):
            convert_time_period("invalid")


class TestInfoDict:
    """Test InfoDict wrapper class"""

    def test_attribute_access(self):
        """Test accessing dict values as attributes"""
        info = InfoDict({"name": "Test", "value": 123})
        assert info.name == "Test"
        assert info.value == 123

    def test_dict_access(self):
        """Test normal dict access"""
        info = InfoDict({"name": "Test"})
        assert info["name"] == "Test"
        assert info.get("name") == "Test"

    def test_attribute_error(self):
        """Test accessing non-existent attribute"""
        info = InfoDict({"name": "Test"})
        with pytest.raises(AttributeError):
            _ = info.nonexistent

    def test_setattr(self):
        """Test setting attributes"""
        info = InfoDict()
        info.name = "Test"
        assert info["name"] == "Test"

    def test_delattr(self):
        """Test deleting attributes"""
        info = InfoDict({"name": "Test"})
        del info.name
        assert "name" not in info
