from __future__ import annotations

import html
import math
import zipfile
from io import BytesIO
from typing import Any

import pandas as pd

from gradpath.matching import REFERENCE_EXPORT_COLUMNS, build_matching_rows


def build_results(
    programs: list[dict[str, Any]],
    profile: dict[str, Any],
    custom_weights: dict[str, float] | None = None,
) -> list[dict[str, Any]]:
    """Build ranked matching rows with reference export columns and legacy UI columns."""
    return build_matching_rows(programs, profile, custom_weights=custom_weights)


def results_dataframe(
    programs: list[dict[str, Any]],
    profile: dict[str, Any],
    custom_weights: dict[str, float] | None = None,
) -> pd.DataFrame:
    rows = build_results(programs, profile, custom_weights=custom_weights)
    if not rows:
        return pd.DataFrame()
    leading = [column for column in REFERENCE_EXPORT_COLUMNS if column in rows[0]]
    rest = [column for column in rows[0] if column not in leading]
    return pd.DataFrame(rows)[[*leading, *rest]]


def reference_export_dataframe(
    programs: list[dict[str, Any]],
    profile: dict[str, Any],
    custom_weights: dict[str, float] | None = None,
) -> pd.DataFrame:
    df = results_dataframe(programs, profile, custom_weights=custom_weights)
    if df.empty:
        return df
    return df[[column for column in REFERENCE_EXPORT_COLUMNS if column in df.columns]]


def comparison_dataframe(rows: list[dict[str, Any]]) -> pd.DataFrame:
    fields = [
        "University",
        "Program",
        "Degree",
        "Category",
        "Overall Score",
        "Research Fit Score",
        "POI Fit",
        "Professors",
        "Risk Note",
        "Next Action",
        "Letter Strategy",
        "TOEFL/GRE",
        "Application Website",
    ]
    return pd.DataFrame([{field: row.get(field, "") for field in fields} for row in rows])


def results_workbook_bytes(programs: list[dict[str, Any]], profile: dict[str, Any]) -> bytes:
    rows = build_results(programs, profile)
    sheets = {
        "Shortlist": _rows_for_sheet(rows, REFERENCE_EXPORT_COLUMNS),
        "Score Breakdown": _rows_for_sheet(
            rows,
            [
                "University",
                "Program",
                "Degree",
                "Category",
                "Overall Score",
                "Research Fit Score",
                "Evidence Fit Score",
                "Letter Fit Score",
                "Route Fit Score",
                "Feasibility Score",
                "Balance Note",
            ],
        ),
        "Actions": _rows_for_sheet(
            rows,
            [
                "University",
                "Program",
                "Category",
                "Status",
                "Next Action",
                "Risk Note",
                "Research Signal",
                "Letter Strategy",
                "GRE Strategy",
                "English / TOEFL Strategy",
                "TA / Funding Note",
            ],
        ),
        "Sources": _rows_for_sheet(
            rows,
            [
                "University",
                "Program",
                "Source",
                "System Confidence",
                "Application Website",
                "Search Strategy",
                "Research Set",
                "Last Reviewed",
            ],
        ),
        "Profile": _profile_rows(profile),
    }
    return _build_xlsx(sheets)


def _rows_for_sheet(rows: list[dict[str, Any]], columns: list[str]) -> list[list[Any]]:
    available = [column for column in columns if rows and column in rows[0]]
    if not available:
        available = columns
    return [available, *[[row.get(column, "") for column in available] for row in rows]]


def _profile_rows(profile: dict[str, Any]) -> list[list[Any]]:
    rows = [["Field", "Value"]]
    for key, value in profile.items():
        rows.append([key, _display_value(value)])
    return rows


def _display_value(value: Any) -> str:
    if isinstance(value, dict):
        return " | ".join(f"{key}: {_display_value(item)}" for key, item in value.items())
    if isinstance(value, list):
        return "; ".join(str(item) for item in value)
    return str(value)


def _build_xlsx(sheets: dict[str, list[list[Any]]]) -> bytes:
    output = BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", _content_types_xml(len(sheets)))
        archive.writestr("_rels/.rels", _root_rels_xml())
        archive.writestr("xl/workbook.xml", _workbook_xml(list(sheets)))
        archive.writestr("xl/_rels/workbook.xml.rels", _workbook_rels_xml(len(sheets)))
        archive.writestr("xl/styles.xml", _styles_xml())
        for index, (name, rows) in enumerate(sheets.items(), start=1):
            archive.writestr(f"xl/worksheets/sheet{index}.xml", _sheet_xml(name, rows))
    return output.getvalue()


def _content_types_xml(sheet_count: int) -> str:
    sheet_overrides = "".join(
        f'<Override PartName="/xl/worksheets/sheet{index}.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        for index in range(1, sheet_count + 1)
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" '
        'ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/xl/workbook.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        '<Override PartName="/xl/styles.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
        f"{sheet_overrides}</Types>"
    )


def _root_rels_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
        'Target="xl/workbook.xml"/></Relationships>'
    )


def _workbook_xml(sheet_names: list[str]) -> str:
    sheets_xml = "".join(
        f'<sheet name="{_xml(sheet_name[:31])}" sheetId="{index}" r:id="rId{index}"/>'
        for index, sheet_name in enumerate(sheet_names, start=1)
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        f"<sheets>{sheets_xml}</sheets></workbook>"
    )


def _workbook_rels_xml(sheet_count: int) -> str:
    rels = "".join(
        f'<Relationship Id="rId{index}" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
        f'Target="worksheets/sheet{index}.xml"/>'
        for index in range(1, sheet_count + 1)
    )
    rels += (
        f'<Relationship Id="rId{sheet_count + 1}" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" '
        'Target="styles.xml"/>'
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        f"{rels}</Relationships>"
    )


def _styles_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        '<fonts count="2"><font><sz val="11"/><name val="Aptos"/></font>'
        '<font><b/><color rgb="FFFFFFFF"/><sz val="11"/><name val="Aptos"/></font></fonts>'
        '<fills count="7"><fill><patternFill patternType="none"/></fill>'
        '<fill><patternFill patternType="gray125"/></fill>'
        '<fill><patternFill patternType="solid"><fgColor rgb="FF2F6F73"/></patternFill></fill>'
        '<fill><patternFill patternType="solid"><fgColor rgb="FFF8D7DA"/></patternFill></fill>'
        '<fill><patternFill patternType="solid"><fgColor rgb="FFDDEFE4"/></patternFill></fill>'
        '<fill><patternFill patternType="solid"><fgColor rgb="FFEAF2FF"/></patternFill></fill>'
        '<fill><patternFill patternType="solid"><fgColor rgb="FFE7E5DF"/>'
        "</patternFill></fill></fills>"
        '<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>'
        '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" '
        'borderId="0"/></cellStyleXfs>'
        '<cellXfs count="7">'
        '<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>'
        '<xf numFmtId="0" fontId="1" fillId="2" borderId="0" xfId="0" applyFont="1" applyFill="1"/>'
        '<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>'
        '<xf numFmtId="0" fontId="0" fillId="3" borderId="0" xfId="0" applyFill="1"/>'
        '<xf numFmtId="0" fontId="0" fillId="4" borderId="0" xfId="0" applyFill="1"/>'
        '<xf numFmtId="0" fontId="0" fillId="5" borderId="0" xfId="0" applyFill="1"/>'
        '<xf numFmtId="0" fontId="0" fillId="6" borderId="0" xfId="0" applyFill="1"/>'
        '</cellXfs><cellStyles count="1"><cellStyle name="Normal" xfId="0" '
        'builtinId="0"/></cellStyles>'
        "</styleSheet>"
    )


def _sheet_xml(sheet_name: str, rows: list[list[Any]]) -> str:
    max_cols = max((len(row) for row in rows), default=1)
    max_rows = max(len(rows), 1)
    dimension = f"A1:{_column_letter(max_cols)}{max_rows}"
    cols = "".join(
        f'<col min="{index}" max="{index}" '
        f'width="{_column_width(rows, index - 1)}" customWidth="1"/>'
        for index in range(1, max_cols + 1)
    )
    row_xml = "".join(
        _row_xml(row, row_index, rows[0] if rows else [])
        for row_index, row in enumerate(rows, 1)
    )
    auto_filter = f'<autoFilter ref="{dimension}"/>' if len(rows) > 1 and max_cols > 1 else ""
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f'<dimension ref="{dimension}"/>'
        '<sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" '
        'activePane="bottomLeft" state="frozen"/></sheetView></sheetViews>'
        f"<cols>{cols}</cols><sheetData>{row_xml}</sheetData>{auto_filter}"
        "</worksheet>"
    )


def _row_xml(row: list[Any], row_index: int, headers: list[Any]) -> str:
    cells = []
    for col_index, value in enumerate(row, start=1):
        header = str(headers[col_index - 1]) if col_index <= len(headers) else ""
        style = _cell_style(value, row_index, header)
        cells.append(_cell_xml(row_index, col_index, value, style))
    return f'<row r="{row_index}">{"".join(cells)}</row>'


def _cell_style(value: Any, row_index: int, header: str) -> int:
    if row_index == 1:
        return 1
    text = str(value)
    if header in {"Category", "Status", "Track"}:
        if "衝刺" in text:
            return 3
        if "Moderate" in text or text == "Active":
            return 4
        if "MS" in text:
            return 5
        if "Demoted" in text or "Archive" in text:
            return 6
    return 2


def _cell_xml(row_index: int, col_index: int, value: Any, style: int) -> str:
    ref = f"{_column_letter(col_index)}{row_index}"
    if value is None:
        return f'<c r="{ref}" s="{style}"/>'
    if isinstance(value, bool):
        return f'<c r="{ref}" s="{style}" t="b"><v>{1 if value else 0}</v></c>'
    if isinstance(value, int | float) and not isinstance(value, bool) and math.isfinite(value):
        return f'<c r="{ref}" s="{style}"><v>{value}</v></c>'
    return f'<c r="{ref}" s="{style}" t="inlineStr"><is><t>{_xml(str(value))}</t></is></c>'


def _column_width(rows: list[list[Any]], index: int) -> int:
    values = [str(row[index]) for row in rows[:50] if index < len(row)]
    max_len = max([len(value) for value in values] or [10])
    return max(10, min(55, max_len + 2))


def _column_letter(index: int) -> str:
    letters = ""
    while index:
        index, remainder = divmod(index - 1, 26)
        letters = chr(65 + remainder) + letters
    return letters


def _xml(value: str) -> str:
    return html.escape(value, quote=True)
