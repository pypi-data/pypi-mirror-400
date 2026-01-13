"""Tests for builder module - Formula functionality."""

from __future__ import annotations

import pytest

from spreadsheet_dl.builder import (
    FormulaBuilder,
    FormulaDependencyGraph,
    RangeRef,
)

pytestmark = [pytest.mark.unit, pytest.mark.builder]


class TestFormulaBuilder:
    """Tests for FormulaBuilder class."""

    def test_sum_formula(self) -> None:
        """Test SUM formula generation."""
        f = FormulaBuilder()
        formula_str = f.sum(f.range("A2", "A100"))
        assert formula_str == "of:=SUM([.A2:A100])"

    def test_sumif_formula(self) -> None:
        """Test SUMIF formula generation."""
        f = FormulaBuilder()
        formula_str = f.sumif(
            f.sheet("Expenses").col("B"),
            f.cell("A2"),
            f.sheet("Expenses").col("D"),
        )
        assert "SUMIF" in formula_str
        assert "Expenses" in formula_str

    def test_sumifs_formula(self) -> None:
        """Test SUMIFS formula generation."""
        f = FormulaBuilder()
        formula_str = f.sumifs(
            f.range("D2", "D100"),
            (f.range("A2", "A100"), f.cell("E1")),
            (f.range("B2", "B100"), f.cell("F1")),
        )
        assert "SUMIFS" in formula_str

    def test_vlookup_formula(self) -> None:
        """Test VLOOKUP formula generation."""
        f = FormulaBuilder()
        formula_str = f.vlookup(
            f.cell("A2"),
            f.range("A1", "B10"),
            2,
            exact=True,
        )
        assert "VLOOKUP" in formula_str
        assert "2" in formula_str
        assert "0" in formula_str  # exact match

    def test_vlookup_approximate(self) -> None:
        """Test VLOOKUP with approximate match."""
        f = FormulaBuilder()
        formula_str = f.vlookup(
            f.cell("A2"),
            f.range("A1", "B10"),
            2,
            exact=False,
        )
        assert "1" in formula_str  # approximate match

    def test_hlookup_formula(self) -> None:
        """Test HLOOKUP formula generation."""
        f = FormulaBuilder()
        formula_str = f.hlookup(
            f.cell("A1"),
            f.range("A1", "Z10"),
            5,
            exact=True,
        )
        assert "HLOOKUP" in formula_str

    def test_index_formula(self) -> None:
        """Test INDEX formula generation."""
        f = FormulaBuilder()
        formula_str = f.index(f.range("A1", "D10"), 2, 3)
        assert "INDEX" in formula_str

    def test_match_formula(self) -> None:
        """Test MATCH formula generation."""
        f = FormulaBuilder()
        formula_str = f.match(f.cell("A1"), f.range("B1", "B100"))
        assert "MATCH" in formula_str

    def test_index_match_formula(self) -> None:
        """Test INDEX/MATCH combination."""
        f = FormulaBuilder()
        formula_str = f.index_match(
            f.range("B1", "B100"),
            f.match(f.cell("A1"), f.range("A1", "A100")),
        )
        assert "INDEX" in formula_str
        assert "MATCH" in formula_str

    def test_if_formula(self) -> None:
        """Test IF formula generation."""
        f = FormulaBuilder()
        formula_str = f.if_expr("[.B2]>0", '"Yes"', '"No"')
        assert formula_str == 'of:=IF([.B2]>0;"Yes";"No")'

    def test_subtract_formula(self) -> None:
        """Test subtraction formula."""
        f = FormulaBuilder()
        formula_str = f.subtract("B2", "C2")
        assert formula_str == "of:=[.B2]-[.C2]"

    def test_multiply_formula(self) -> None:
        """Test multiplication formula."""
        f = FormulaBuilder()
        formula_str = f.multiply("B2", "C2")
        assert "*" in formula_str

    def test_divide_formula(self) -> None:
        """Test division formula with zero check."""
        f = FormulaBuilder()
        formula_str = f.divide("B2", "C2")
        assert "IF" in formula_str
        assert ">0" in formula_str or "<>0" in formula_str

    def test_average_formula(self) -> None:
        """Test AVERAGE formula."""
        f = FormulaBuilder()
        formula_str = f.average(f.range("A1", "A10"))
        assert formula_str == "of:=AVERAGE([.A1:A10])"

    def test_averageif_formula(self) -> None:
        """Test AVERAGEIF formula."""
        f = FormulaBuilder()
        formula_str = f.averageif(
            f.range("A1", "A100"),
            ">0",
            f.range("B1", "B100"),
        )
        assert "AVERAGEIF" in formula_str

    def test_averageif_no_average_range(self) -> None:
        """Test AVERAGEIF without separate average range."""
        f = FormulaBuilder()
        formula_str = f.averageif(
            f.range("A1", "A100"),
            ">0",
        )
        assert "AVERAGEIF" in formula_str

    def test_count_formula(self) -> None:
        """Test COUNT formula."""
        f = FormulaBuilder()
        formula_str = f.count(f.range("A1", "A10"))
        assert formula_str == "of:=COUNT([.A1:A10])"

    def test_counta_formula(self) -> None:
        """Test COUNTA formula."""
        f = FormulaBuilder()
        formula_str = f.counta(f.range("A1", "A10"))
        assert formula_str == "of:=COUNTA([.A1:A10])"

    def test_countblank_formula(self) -> None:
        """Test COUNTBLANK formula."""
        f = FormulaBuilder()
        formula_str = f.countblank(f.range("A1", "A10"))
        assert "COUNTBLANK" in formula_str

    def test_countif_formula(self) -> None:
        """Test COUNTIF formula."""
        f = FormulaBuilder()
        formula_str = f.countif(f.range("A1", "A100"), ">50")
        assert "COUNTIF" in formula_str

    def test_countifs_formula(self) -> None:
        """Test COUNTIFS formula."""
        f = FormulaBuilder()
        formula_str = f.countifs(
            (f.range("A1", "A100"), ">0"),
            (f.range("B1", "B100"), "<100"),
        )
        assert "COUNTIFS" in formula_str

    def test_max_formula(self) -> None:
        """Test MAX formula."""
        f = FormulaBuilder()
        formula_str = f.max(f.range("A1", "A10"))
        assert formula_str == "of:=MAX([.A1:A10])"

    def test_min_formula(self) -> None:
        """Test MIN formula."""
        f = FormulaBuilder()
        formula_str = f.min(f.range("A1", "A10"))
        assert formula_str == "of:=MIN([.A1:A10])"

    def test_median_formula(self) -> None:
        """Test MEDIAN formula."""
        f = FormulaBuilder()
        formula_str = f.median(f.range("A1", "A100"))
        assert "MEDIAN" in formula_str

    def test_stdev_formula(self) -> None:
        """Test STDEV formula."""
        f = FormulaBuilder()
        formula_str = f.stdev(f.range("A1", "A100"))
        assert "STDEV" in formula_str

    def test_stdevp_formula(self) -> None:
        """Test STDEVP formula."""
        f = FormulaBuilder()
        formula_str = f.stdevp(f.range("A1", "A100"))
        assert "STDEVP" in formula_str

    def test_var_formula(self) -> None:
        """Test VAR formula."""
        f = FormulaBuilder()
        formula_str = f.var(f.range("A1", "A100"))
        assert "VAR" in formula_str

    def test_percentile_formula(self) -> None:
        """Test PERCENTILE formula."""
        f = FormulaBuilder()
        formula_str = f.percentile(f.range("A1", "A100"), 0.9)
        assert "PERCENTILE" in formula_str

    def test_abs_formula(self) -> None:
        """Test ABS formula."""
        f = FormulaBuilder()
        formula_str = f.abs(f.cell("A1"))
        assert "ABS" in formula_str

    def test_round_formula(self) -> None:
        """Test ROUND formula."""
        f = FormulaBuilder()
        formula_str = f.round(f.cell("A1"), 2)
        assert "ROUND" in formula_str

    def test_roundup_formula(self) -> None:
        """Test ROUNDUP formula."""
        f = FormulaBuilder()
        formula_str = f.roundup(f.cell("A1"), 0)
        assert "ROUNDUP" in formula_str

    def test_rounddown_formula(self) -> None:
        """Test ROUNDDOWN formula."""
        f = FormulaBuilder()
        formula_str = f.rounddown(f.cell("A1"), 0)
        assert "ROUNDDOWN" in formula_str

    def test_mod_formula(self) -> None:
        """Test MOD formula."""
        f = FormulaBuilder()
        formula_str = f.mod(f.cell("A1"), 3)
        assert "MOD" in formula_str

    def test_power_formula(self) -> None:
        """Test POWER formula."""
        f = FormulaBuilder()
        formula_str = f.power(f.cell("A1"), 2)
        assert "POWER" in formula_str

    def test_sqrt_formula(self) -> None:
        """Test SQRT formula."""
        f = FormulaBuilder()
        formula_str = f.sqrt(f.cell("A1"))
        assert "SQRT" in formula_str

    def test_named_range_formula(self) -> None:
        """Test named range in formula."""
        f = FormulaBuilder()
        ref = f.named_range("MyRange")
        assert ref == "[MyRange]"


class TestFormulaBuilderFinancial:
    """Tests for FormulaBuilder financial functions."""

    def test_pmt_formula(self) -> None:
        """Test PMT formula."""
        f = FormulaBuilder()
        formula_str = f.pmt(0.05 / 12, 360, -200000)
        assert "PMT" in formula_str

    def test_pmt_formula_with_cells(self) -> None:
        """Test PMT formula with cell references."""
        f = FormulaBuilder()
        formula_str = f.pmt(f.cell("B1"), f.cell("B2"), f.cell("B3"))
        assert "PMT" in formula_str

    def test_pv_formula(self) -> None:
        """Test PV formula."""
        f = FormulaBuilder()
        formula_str = f.pv(0.05, 10, -1000)
        assert "PV" in formula_str

    def test_fv_formula(self) -> None:
        """Test FV formula."""
        f = FormulaBuilder()
        formula_str = f.fv(0.05 / 12, 120, -100, -1000)
        assert "FV" in formula_str

    def test_npv_formula(self) -> None:
        """Test NPV formula."""
        f = FormulaBuilder()
        formula_str = f.npv(0.1, f.range("A1", "A10"))
        assert "NPV" in formula_str

    def test_irr_formula(self) -> None:
        """Test IRR formula."""
        f = FormulaBuilder()
        formula_str = f.irr(f.range("A1", "A10"))
        assert "IRR" in formula_str

    def test_nper_formula(self) -> None:
        """Test NPER formula."""
        f = FormulaBuilder()
        formula_str = f.nper(0.05 / 12, -500, 10000)
        assert "NPER" in formula_str

    def test_rate_formula(self) -> None:
        """Test RATE formula."""
        f = FormulaBuilder()
        formula_str = f.rate(120, -500, 50000)
        assert "RATE" in formula_str


class TestFormulaBuilderDateTimeFunctions:
    """Tests for FormulaBuilder date/time functions."""

    def test_today_formula(self) -> None:
        """Test TODAY formula."""
        f = FormulaBuilder()
        formula_str = f.today()
        assert formula_str == "of:=TODAY()"

    def test_now_formula(self) -> None:
        """Test NOW formula."""
        f = FormulaBuilder()
        formula_str = f.now()
        assert formula_str == "of:=NOW()"

    def test_date_formula(self) -> None:
        """Test DATE formula."""
        f = FormulaBuilder()
        formula_str = f.date(2025, 1, 15)
        assert "DATE" in formula_str

    def test_year_formula(self) -> None:
        """Test YEAR formula."""
        f = FormulaBuilder()
        formula_str = f.year(f.cell("A1"))
        assert "YEAR" in formula_str

    def test_month_formula(self) -> None:
        """Test MONTH formula."""
        f = FormulaBuilder()
        formula_str = f.month(f.cell("A1"))
        assert "MONTH" in formula_str

    def test_day_formula(self) -> None:
        """Test DAY formula."""
        f = FormulaBuilder()
        formula_str = f.day(f.cell("A1"))
        assert "DAY" in formula_str

    def test_edate_formula(self) -> None:
        """Test EDATE formula."""
        f = FormulaBuilder()
        formula_str = f.edate(f.cell("A1"), 3)
        assert "EDATE" in formula_str
        assert "[.A1]" in formula_str
        assert ";3" in formula_str

    def test_eomonth_formula(self) -> None:
        """Test EOMONTH formula."""
        f = FormulaBuilder()
        formula_str = f.eomonth(f.cell("A1"), 0)
        assert "EOMONTH" in formula_str

    def test_datedif_formula(self) -> None:
        """Test DATEDIF formula."""
        f = FormulaBuilder()
        formula_str = f.datedif(f.cell("A1"), f.cell("B1"), "M")
        assert "DATEDIF" in formula_str


class TestFormulaBuilderTextFunctions:
    """Tests for FormulaBuilder text functions."""

    def test_concatenate_formula(self) -> None:
        """Test CONCATENATE formula."""
        f = FormulaBuilder()
        formula_str = f.concatenate(f.cell("A1"), '" "', f.cell("B1"))
        assert "CONCATENATE" in formula_str

    def test_left_formula(self) -> None:
        """Test LEFT formula."""
        f = FormulaBuilder()
        formula_str = f.left(f.cell("A1"), 5)
        assert "LEFT" in formula_str

    def test_right_formula(self) -> None:
        """Test RIGHT formula."""
        f = FormulaBuilder()
        formula_str = f.right(f.cell("A1"), 5)
        assert "RIGHT" in formula_str

    def test_mid_formula(self) -> None:
        """Test MID formula."""
        f = FormulaBuilder()
        formula_str = f.mid(f.cell("A1"), 2, 5)
        assert "MID" in formula_str

    def test_len_formula(self) -> None:
        """Test LEN formula."""
        f = FormulaBuilder()
        formula_str = f.len(f.cell("A1"))
        assert "LEN" in formula_str

    def test_trim_formula(self) -> None:
        """Test TRIM formula."""
        f = FormulaBuilder()
        formula_str = f.trim(f.cell("A1"))
        assert "TRIM" in formula_str

    def test_upper_formula(self) -> None:
        """Test UPPER formula."""
        f = FormulaBuilder()
        formula_str = f.upper(f.cell("A1"))
        assert "UPPER" in formula_str

    def test_lower_formula(self) -> None:
        """Test LOWER formula."""
        f = FormulaBuilder()
        formula_str = f.lower(f.cell("A1"))
        assert "LOWER" in formula_str

    def test_proper_formula(self) -> None:
        """Test PROPER formula."""
        f = FormulaBuilder()
        formula_str = f.proper(f.cell("A1"))
        assert "PROPER" in formula_str

    def test_text_formula(self) -> None:
        """Test TEXT formula."""
        f = FormulaBuilder()
        formula_str = f.text(f.cell("A1"), '"$#,##0.00"')
        assert "TEXT" in formula_str


class TestFormulaBuilderLogicalFunctions:
    """Tests for FormulaBuilder logical functions."""

    def test_and_formula(self) -> None:
        """Test AND formula."""
        f = FormulaBuilder()
        formula_str = f.and_expr("[.A1]>0", "[.B1]<100")
        assert "AND" in formula_str

    def test_or_formula(self) -> None:
        """Test OR formula."""
        f = FormulaBuilder()
        formula_str = f.or_expr("[.A1]>0", "[.B1]>0")
        assert "OR" in formula_str

    def test_not_formula(self) -> None:
        """Test NOT formula."""
        f = FormulaBuilder()
        formula_str = f.not_expr("[.A1]=0")
        assert "NOT" in formula_str

    def test_iferror_formula(self) -> None:
        """Test IFERROR formula."""
        f = FormulaBuilder()
        formula_str = f.iferror(f.divide("A1", "B1"), "0")
        assert "IFERROR" in formula_str

    def test_isblank_formula(self) -> None:
        """Test ISBLANK formula."""
        f = FormulaBuilder()
        formula_str = f.isblank(f.cell("A1"))
        assert "ISBLANK" in formula_str


class TestFormulaDependencyGraph:
    """Tests for FormulaDependencyGraph - circular reference detection."""

    def test_no_circular_reference(self) -> None:
        """Test detecting no circular reference."""
        graph = FormulaDependencyGraph()
        graph.add_cell("B1", "of:=[.A1]")
        graph.add_cell("C1", "of:=[.B1]")
        graph.add_cell("D1", "of:=[.C1]")
        refs = graph.detect_circular_references()
        assert len(refs) == 0

    def test_circular_reference_detected(self) -> None:
        """Test detecting circular reference."""
        graph = FormulaDependencyGraph()
        graph.add_cell("A1", "of:=[.B1]")
        graph.add_cell("B1", "of:=[.C1]")
        graph.add_cell("C1", "of:=[.A1]")
        refs = graph.detect_circular_references()
        assert len(refs) > 0

    def test_self_reference(self) -> None:
        """Test detecting self-reference."""
        graph = FormulaDependencyGraph()
        graph.add_cell("A1", "of:=[.A1]")
        refs = graph.detect_circular_references()
        assert len(refs) > 0

    def test_complex_circular(self) -> None:
        """Test detecting complex circular reference."""
        graph = FormulaDependencyGraph()
        graph.add_cell("A1", "of:=[.B1]+[.C1]")
        graph.add_cell("B1", "of:=[.D1]")
        graph.add_cell("C1", "of:=[.E1]")
        graph.add_cell("E1", "of:=[.A1]")  # Creates cycle
        refs = graph.detect_circular_references()
        assert len(refs) > 0

    def test_multiple_dependencies(self) -> None:
        """Test cell with multiple dependencies."""
        graph = FormulaDependencyGraph()
        graph.add_cell("A1", "of:=[.B1]+[.C1]+[.D1]")
        refs = graph.detect_circular_references()
        assert len(refs) == 0

    def test_find_cycle(self) -> None:
        """Test finding the cycle path."""
        graph = FormulaDependencyGraph()
        graph.add_cell("A1", "of:=[.B1]")
        graph.add_cell("B1", "of:=[.C1]")
        graph.add_cell("C1", "of:=[.A1]")
        refs = graph.detect_circular_references()
        assert len(refs) > 0
        _cell, cycle = refs[0]
        assert any("A1" in c for c in cycle)

    def test_clear_graph(self) -> None:
        """Test clearing the dependency graph."""
        graph = FormulaDependencyGraph()
        graph.add_cell("A1", "of:=[.B1]")
        # Clear by creating new graph
        graph = FormulaDependencyGraph()
        refs = graph.detect_circular_references()
        assert len(refs) == 0

    def test_add_cell_no_formula(self) -> None:
        """Test adding cell without formula (line 1734)."""
        graph = FormulaDependencyGraph()
        graph.add_cell("A1", None)
        assert "Sheet1.A1" in graph._dependencies
        assert len(graph._dependencies["Sheet1.A1"]) == 0

    def test_add_cell_with_custom_sheet(self) -> None:
        """Test adding cell with custom sheet name (line 1737)."""
        graph = FormulaDependencyGraph()
        graph.add_cell("A1", "of:=[.B1]", sheet="MySheet")
        deps = graph.get_dependencies("A1", sheet="MySheet")
        assert "MySheet.B1" in deps

    def test_extract_cross_sheet_references(self) -> None:
        """Test extracting cross-sheet references (lines 1762-1765)."""
        graph = FormulaDependencyGraph()
        graph.add_cell("A1", "of:=[Sheet2.B5]+[OtherSheet.C10]", sheet="Sheet1")
        deps = graph.get_dependencies("A1", sheet="Sheet1")
        assert "Sheet2.B5" in deps
        assert "OtherSheet.C10" in deps

    def test_extract_cross_sheet_with_quotes(self) -> None:
        """Test cross-sheet references with quoted sheet names (line 1763)."""
        graph = FormulaDependencyGraph()
        graph.add_cell("A1", "of:=['My Sheet'.B5]", sheet="Sheet1")
        deps = graph.get_dependencies("A1", sheet="Sheet1")
        assert "My Sheet.B5" in deps

    def test_validate_raises_on_circular(self) -> None:
        """Test validate() raises CircularReferenceError (lines 1826-1829)."""
        from spreadsheet_dl.builder import CircularReferenceError

        graph = FormulaDependencyGraph()
        graph.add_cell("A1", "of:=[.B1]")
        graph.add_cell("B1", "of:=[.A1]")
        with pytest.raises(CircularReferenceError):
            graph.validate()

    def test_validate_succeeds_without_circular(self) -> None:
        """Test validate() succeeds without circular references."""
        graph = FormulaDependencyGraph()
        graph.add_cell("A1", "of:=[.B1]")
        graph.add_cell("B1", "of:=[.C1]")
        graph.validate()  # Should not raise

    def test_get_dependencies(self) -> None:
        """Test get_dependencies method (lines 1842-1843)."""
        graph = FormulaDependencyGraph()
        graph.add_cell("A1", "of:=[.B1]+[.C1]")
        deps = graph.get_dependencies("A1")
        assert "Sheet1.B1" in deps
        assert "Sheet1.C1" in deps

    def test_get_dependents(self) -> None:
        """Test get_dependents method (lines 1856-1863)."""
        graph = FormulaDependencyGraph()
        graph.add_cell("A1", "of:=[.B1]")
        graph.add_cell("C1", "of:=[.B1]")
        graph.add_cell("D1", "of:=[.B1]+[.E1]")
        # B1 is depended on by A1, C1, and D1
        dependents = graph.get_dependents("B1")
        assert "Sheet1.A1" in dependents
        assert "Sheet1.C1" in dependents
        assert "Sheet1.D1" in dependents

    def test_circular_reference_error_formatting(self) -> None:
        """Test CircularReferenceError message formatting (lines 1692-1698)."""
        from spreadsheet_dl.builder import CircularReferenceError

        cycle = ["Sheet1.A1", "Sheet1.B1", "Sheet1.C1", "Sheet1.A1"]
        error = CircularReferenceError("Sheet1.A1", cycle)
        assert "Sheet1.A1" in str(error)
        assert "Sheet1.B1" in str(error)
        assert "->" in str(error)
        assert error.cell == "Sheet1.A1"
        assert error.cycle == cycle


class TestFormulaCoverageGaps:
    """Tests for untested formula methods to achieve 95% coverage."""

    def test_weekday_formula(self) -> None:
        """Test WEEKDAY formula (line 743)."""
        fb = FormulaBuilder()
        # Default type
        result = fb.weekday("A1")
        assert result == "of:=WEEKDAY([.A1];1)"
        # Custom type
        result = fb.weekday("B2", type=2)
        assert result == "of:=WEEKDAY([.B2];2)"

    def test_weeknum_formula(self) -> None:
        """Test WEEKNUM formula (line 747)."""
        fb = FormulaBuilder()
        result = fb.weeknum("A1")
        assert result == "of:=WEEKNUM([.A1];1)"
        result = fb.weeknum("B2", type=2)
        assert result == "of:=WEEKNUM([.B2];2)"

    def test_index_formula_without_col(self) -> None:
        """Test INDEX formula without col_num (line 816)."""
        fb = FormulaBuilder()
        result = fb.index(
            array=RangeRef(start="A1", end="A10"), row_num=5, col_num=None
        )
        assert result == "of:=INDEX([.A1:A10];5)"

    def test_index_match_with_prefix_strip(self) -> None:
        """Test INDEX/MATCH with prefix stripping (lines 855-857)."""
        fb = FormulaBuilder()
        # Test with prefix already in match formula
        match_with_prefix = fb.match("value", RangeRef(start="A1", end="A10"))
        result = fb.index_match(RangeRef(start="B1", end="B10"), match_with_prefix)
        assert "INDEX" in result
        assert "MATCH" in result

    def test_offset_with_height_width(self) -> None:
        """Test OFFSET formula with height and width (lines 868-876)."""
        fb = FormulaBuilder()
        # With height only
        result = fb.offset("A1", rows=2, cols=3, height=5)
        assert result == "of:=OFFSET([.A1];2;3;5)"
        # With height and width
        result = fb.offset("A1", rows=2, cols=3, height=5, width=10)
        assert result == "of:=OFFSET([.A1];2;3;5;10)"

    def test_indirect_formula(self) -> None:
        """Test INDIRECT formula (line 880)."""
        fb = FormulaBuilder()
        result = fb.indirect("A1")
        assert result == "of:=INDIRECT([.A1])"

    def test_left_formula(self) -> None:
        """Test LEFT formula (line 893)."""
        fb = FormulaBuilder()
        result = fb.left("A1", num_chars=5)
        assert result == "of:=LEFT([.A1];5)"

    def test_right_formula(self) -> None:
        """Test RIGHT formula (line 935)."""
        fb = FormulaBuilder()
        result = fb.right("A1", num_chars=3)
        assert result == "of:=RIGHT([.A1];3)"

    def test_mid_formula(self) -> None:
        """Test MID formula (line 941)."""
        fb = FormulaBuilder()
        result = fb.mid("A1", start_num=2, num_chars=5)
        assert result == "of:=MID([.A1];2;5)"

    def test_find_formula(self) -> None:
        """Test FIND formula (lines 935 with start_num)."""
        fb = FormulaBuilder()
        # With explicit start_num
        result = fb.find("text", "A1", start_num=5)
        assert result == 'of:=FIND("text";[.A1];5)'

    def test_search_formula(self) -> None:
        """Test SEARCH formula (line 941 with start_num)."""
        fb = FormulaBuilder()
        # With explicit start_num
        result = fb.search("pattern", "A1", start_num=2)
        assert result == 'of:=SEARCH("pattern";[.A1];2)'

    def test_substitute_with_instance(self) -> None:
        """Test SUBSTITUTE formula with instance_num (lines 951-954)."""
        fb = FormulaBuilder()
        result = fb.substitute("A1", old_text="old", new_text="new", instance_num=2)
        assert '"old"' in result
        assert '"new"' in result
        assert ";2)" in result

    def test_text_formula(self) -> None:
        """Test TEXT formula (line 895-897)."""
        fb = FormulaBuilder()
        result = fb.text("A1", format_text="0.00")
        assert result == 'of:=TEXT([.A1];"0.00")'

    def test_iferror_formula(self) -> None:
        """Test IFERROR formula (line 971-977)."""
        fb = FormulaBuilder()
        result = fb.iferror(value="A1", value_if_error="0")
        assert result == "of:=IFERROR([.A1];0)"

    def test_ifna_formula(self) -> None:
        """Test IFNA formula (line 985)."""
        fb = FormulaBuilder()
        result = fb.ifna(value="A1", value_if_na="NA")
        assert result == "of:=IFNA([.A1];[.NA])"

    def test_isblank_formula(self) -> None:
        """Test ISBLANK formula (line 999-1001)."""
        fb = FormulaBuilder()
        result = fb.isblank("A1")
        assert result == "of:=ISBLANK([.A1])"

    def test_iserror_formula(self) -> None:
        """Test ISERROR formula (line 1003-1005)."""
        fb = FormulaBuilder()
        result = fb.iserror("A1")
        assert result == "of:=ISERROR([.A1])"

    def test_isnumber_formula(self) -> None:
        """Test ISNUMBER formula (line 1007-1009)."""
        fb = FormulaBuilder()
        result = fb.isnumber("A1")
        assert result == "of:=ISNUMBER([.A1])"

    def test_istext_formula(self) -> None:
        """Test ISTEXT formula (line 1011-1013)."""
        fb = FormulaBuilder()
        result = fb.istext("A1")
        assert result == "of:=ISTEXT([.A1])"

    def test_concat_formula(self) -> None:
        """Test CONCAT formula (alias for CONCATENATE, line 893)."""
        fb = FormulaBuilder()
        result = fb.concat("A1", "B1", "C1")
        assert "CONCATENATE" in result
        assert result == "of:=CONCATENATE([.A1];[.B1];[.C1])"

    def test_array_formula(self) -> None:
        """Test array formula wrapping (lines 1032-1034)."""
        fb = FormulaBuilder()
        # Without prefix
        result = fb.array("SUM(A1:A10)")
        assert result == "of:={SUM(A1:A10)}"
        # With prefix - should strip it
        result = fb.array("of:=SUM(B1:B10)")
