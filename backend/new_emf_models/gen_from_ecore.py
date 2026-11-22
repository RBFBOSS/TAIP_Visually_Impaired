import sys
import xml.etree.ElementTree as ET
from pathlib import Path

XSI_NS = "http://www.w3.org/2001/XMLSchema-instance"

TYPE_MAP = {
    "EString": "str",
    "EInt": "int",
    "EIntegerObject": "int",
    "EFloat": "float",
    "EDouble": "float",
    "EBoolean": "bool",
    "EDate": "datetime",
}


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def find_by_local_name(parent: ET.Element, target: str) -> list[ET.Element]:
    return [child for child in parent if local_name(child.tag) == target]


def resolve_type(etype: str, enum_names: set[str], class_names: set[str]) -> str:
    if not etype:
        return "Any"
    short_name = etype.rsplit("/", 1)[-1]
    if short_name in enum_names:
        return short_name
    if short_name in class_names:
        return f'"{short_name}"'
    ecore_primitive = etype.rsplit("#//", 1)[-1]
    return TYPE_MAP.get(ecore_primitive, "Any")


def generate(ecore_file: Path, out_file: Path) -> None:
    root = ET.parse(ecore_file).getroot()
    packages = [root] + [
        elem for elem in root.iter() if local_name(elem.tag) == "eSubpackages"
    ]

    enums: list[tuple[str, list[str]]] = []
    classes: list[dict] = []

    for pkg in packages:
        for clf in find_by_local_name(pkg, "eClassifiers"):
            xsi_type = clf.attrib.get(f"{{{XSI_NS}}}type", "")
            name = clf.attrib["name"]

            if xsi_type.endswith("EEnum"):
                literals = [
                    lit.attrib["name"]
                    for lit in find_by_local_name(clf, "eLiterals")
                ]
                enums.append((name, literals))

            elif xsi_type.endswith("EClass"):
                supers = [
                    s.rsplit("/", 1)[-1]
                    for s in clf.attrib.get("eSuperTypes", "").split()
                    if s
                ]
                features = []
                for feat in find_by_local_name(clf, "eStructuralFeatures"):
                    features.append(
                        {
                            "name": feat.attrib["name"],
                            "etype": feat.attrib.get("eType", ""),
                            "upper": int(feat.attrib.get("upperBound", "1")),
                            "lower": int(feat.attrib.get("lowerBound", "0")),
                        }
                    )
                ops = []
                for op in find_by_local_name(clf, "eOperations"):
                    params = [
                        (p.attrib["name"], p.attrib.get("eType", ""))
                        for p in find_by_local_name(op, "eParameters")
                    ]
                    ops.append(
                        {
                            "name": op.attrib["name"],
                            "etype": op.attrib.get("eType", ""),
                            "upper": int(op.attrib.get("upperBound", "1")),
                            "params": params,
                        }
                    )
                classes.append(
                    {
                        "name": name,
                        "supers": supers,
                        "features": features,
                        "ops": ops,
                    }
                )

    enum_names = {e[0] for e in enums}
    class_names = {c["name"] for c in classes}

    ordered: list[dict] = []
    remaining = classes[:]
    placed: set[str] = set()
    while remaining:
        progressed = False
        for c in remaining[:]:
            if all(s in placed or s not in class_names for s in c["supers"]):
                ordered.append(c)
                placed.add(c["name"])
                remaining.remove(c)
                progressed = True
        if not progressed:
            ordered.extend(remaining)
            break

    lines = [
        '"""Python code generated from an Ecore metamodel."""',
        "from __future__ import annotations",
        "from dataclasses import dataclass, field",
        "from datetime import datetime",
        "from enum import Enum",
        "from typing import Any",
        "",
    ]

    for enum_name, literals in enums:
        lines.append(f"class {enum_name}(str, Enum):")
        for lit in literals:
            lines.append(f'    {lit} = "{lit}"')
        lines.append("")

    for cls in ordered:
        bases = f"({', '.join(cls['supers'])})" if cls["supers"] else ""
        lines.append("@dataclass")
        lines.append(f"class {cls['name']}{bases}:")

        has_body = False
        for feat in cls["features"]:
            py_type = resolve_type(feat["etype"], enum_names, class_names)
            is_many = feat["upper"] == -1 or feat["upper"] > 1
            if is_many:
                lines.append(f"    {feat['name']}: list[{py_type}] = field(default_factory=list)")
            elif feat["lower"] == 0:
                lines.append(f"    {feat['name']}: {py_type} | None = None")
            else:
                lines.append(f"    {feat['name']}: {py_type} = field(default=None)  # type: ignore[assignment]")
            has_body = True

        for op in cls["ops"]:
            params_str = ", ".join(
                f"{p_name}: {resolve_type(p_type, enum_names, class_names)}"
                for p_name, p_type in op["params"]
            )
            sig = f"self, {params_str}" if params_str else "self"
            ret = resolve_type(op["etype"], enum_names, class_names) if op["etype"] else "None"
            if op["upper"] == -1 and op["etype"]:
                ret = f"list[{ret}]"
            lines.append(f"    def {op['name']}({sig}) -> {ret}:")
            lines.append("        raise NotImplementedError")
            lines.append("")
            has_body = True

        if not has_body:
            lines.append("    pass")
        lines.append("")

    out_file.write_text("\n".join(lines), encoding="utf-8")
    print(f"Successfully generated: {out_file} ({len(enums)} enums, {len(ordered)} classes)")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python gen_from_ecore.py <model.ecore> <output.py>")
        sys.exit(1)
    generate(Path(sys.argv[1]), Path(sys.argv[2]))