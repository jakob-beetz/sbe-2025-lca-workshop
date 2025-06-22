import json, ifcopenshell
from ifcopenshell.util import selector
from ifccsv import IfcCsv

# # ---- 0. load IFC & profile --------------------
# IFC_PATH   = "./sbe-2025-lca-workshop/data/IFC_models/Duplex_QTO.ifc"
# IFC_PATH   = "./sbe-2025-lca-workshop/data/IFC_models/Duplex_QTO.ifc"
# PROFILE_JS = "./sbe-2025-lca-workshop/data/all_materials_query_duplex.json"

# f = ifcopenshell.open(IFC_PATH)
# profile = json.load(open(PROFILE_JS))
def get_ifc_csv(ifc_path, profile_js):
    f = ifcopenshell.open(ifc_path)
    profile = json.load(open(profile_js))
    query      = profile["query"]
    elements   = selector.filter_elements(f, query)

    # ---- 2. attributes, headers, formatting -------
    attrs      = [a["name"] for a in profile["attributes"]]
    headers    = [a["header"] for a in profile["attributes"]]
    formatting = [a["formatting"] for a in profile["attributes"]]

    # optional features
    sort       = [a["sort"]     for a in profile["attributes"]]
    # Modified: Extract the full dictionary for each group, not just the 'group' value
    groups     = [a["group"] for a in profile["attributes"] if "group" in a]
    summaries  = [a["summary"]  for a in profile["attributes"]]

    # ---- 3. settings / defaults -------------------
    s = profile["settings"]
    csv_opts = dict(
        include_global_id = s.get("include_global_id", True),
        delimiter         = s.get("csv_custom_delimiter") or s.get("csv_delimiter", ","),
        null              = s.get("null_value", "N/A"),
        empty             = s.get("empty_value", "-"),
        bool_true         = s.get("true_value", "YES"),
        bool_false        = s.get("false_value", "NO"),
        concat            = s.get("concat_value", ", "),
        should_preserve_existing = s.get("should_preserve_existing", False),
    )

    fmt = s.get("format", "csv").lower()          # csv / ods / xlsx / pd
    out = f"export.{fmt if fmt!='pd' else 'csv'}" # pd returns DataFrame

    # ---- 4. export --------------------------------
    ic = IfcCsv()
    ic.export(
        f,                 # ifcopenshell.file
        elements,
        attributes = attrs,
        headers    = headers,
        output     = out if fmt != "pd" else None,
        format     = fmt,  # IfcCsv.FILE_FORMAT enum resolves str
        **csv_opts
    )

    if fmt == "pd":
        df = ic.export_pd()          # you get a pandas.DataFrame to post-process
        df.to_csv(out, index=False)

    print(f"✓ Exported {len(elements)} rows to {out}")

    return ic.export_pd()