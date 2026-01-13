# src/cdd/analyze/pdf.py
"""PDF analysis: extract structure for evidence-based contracts."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional


def analyze_pdf(pdf_path: Path, output_dir: Path) -> Dict[str, Any]:
    """
    Analyze a PDF and extract structural elements.
    
    Produces:
    - Page images (PNG)
    - structure.json with all detected elements
    - elements.md summary for easy reference
    - layout.json with semantic groupings
    
    Args:
        pdf_path: Path to PDF file
        output_dir: Directory to write analysis output
        
    Returns:
        Analysis summary dict
    """
    try:
        import fitz  # PyMuPDF
    except ImportError:
        raise ImportError("PDF analysis requires PyMuPDF: pip install pymupdf")
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    doc = fitz.open(str(pdf_path))
    
    result = {
        "source": str(pdf_path),
        "source_name": pdf_path.name,
        "type": "pdf",
        "page_count": len(doc),
        "pages": [],
        "summary": {
            "total_elements": 0,
            "rectangles": 0,
            "lines": 0,
            "text_blocks": 0,
        },
        "layout": {
            "form_fields": [],
            "tables": [],
            "sections": [],
        }
    }
    
    for page_num, page in enumerate(doc):
        page_data = _analyze_page(page, page_num, output_dir)
        result["pages"].append(page_data)
        
        # Update summary counts
        for el in page_data.get("elements", []):
            result["summary"]["total_elements"] += 1
            el_type = el.get("type")
            if el_type == "rectangle":
                result["summary"]["rectangles"] += 1
            elif el_type == "line":
                result["summary"]["lines"] += 1
            elif el_type == "text":
                result["summary"]["text_blocks"] += 1
    
    # Detect semantic layout
    _detect_layout(result)
    
    doc.close()
    
    # Write structure.json
    structure_path = output_dir / "structure.json"
    with open(structure_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    
    # Write human-readable summary
    summary_path = output_dir / "elements.md"
    _write_summary(result, summary_path)
    
    # Write layout analysis
    layout_path = output_dir / "layout.md"
    _write_layout(result, layout_path)
    
    result["output_dir"] = str(output_dir)
    result["structure_file"] = str(structure_path)
    
    return result


def _analyze_page(page, page_num: int, output_dir: Path) -> Dict[str, Any]:
    """Analyze a single PDF page."""
    # Render page as image
    pix = page.get_pixmap(dpi=150)
    img_path = output_dir / f"page_{page_num + 1}.png"
    pix.save(str(img_path))
    
    page_data = {
        "page": page_num + 1,
        "image": str(img_path.name),  # Relative path
        "width": round(page.rect.width, 1),
        "height": round(page.rect.height, 1),
        "elements": []
    }
    
    element_counter = 0
    
    # Extract drawings (rectangles, lines)
    for path in page.get_drawings():
        for item in path.get("items", []):
            item_type = item[0]
            
            if item_type == "re":  # Rectangle
                rect = item[1]
                width = round(rect.width, 1)
                height = round(rect.height, 1)
                
                # Enhanced classification
                classification = _classify_rectangle(width, height)
                
                page_data["elements"].append({
                    "id": f"R{page_num + 1}_{element_counter}",
                    "type": "rectangle",
                    "classification": classification,
                    "bounds": {
                        "x": round(rect.x0, 1),
                        "y": round(rect.y0, 1),
                        "width": width,
                        "height": height,
                        "x2": round(rect.x1, 1),
                        "y2": round(rect.y1, 1),
                    }
                })
                element_counter += 1
                
            elif item_type == "l":  # Line
                p1, p2 = item[1], item[2]
                is_horizontal = abs(p1.y - p2.y) < 2
                is_vertical = abs(p1.x - p2.x) < 2
                length = ((p2.x - p1.x)**2 + (p2.y - p1.y)**2)**0.5
                
                page_data["elements"].append({
                    "id": f"L{page_num + 1}_{element_counter}",
                    "type": "line",
                    "orientation": "horizontal" if is_horizontal else ("vertical" if is_vertical else "diagonal"),
                    "length": round(length, 1),
                    "bounds": {
                        "x1": round(p1.x, 1),
                        "y1": round(p1.y, 1),
                        "x2": round(p2.x, 1),
                        "y2": round(p2.y, 1),
                    }
                })
                element_counter += 1
    
    # Extract text with positions
    text_counter = 0
    for block in page.get_text("dict")["blocks"]:
        if block.get("type") == 0:  # Text block
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span.get("text", "").strip()
                    if text:
                        bbox = span.get("bbox", [0, 0, 0, 0])
                        flags = span.get("flags", 0)
                        
                        # Detect if this is a label (ends with colon, short, etc.)
                        is_label = text.endswith(':') or (len(text) < 40 and not any(c.isdigit() for c in text))
                        
                        page_data["elements"].append({
                            "id": f"T{page_num + 1}_{text_counter}",
                            "type": "text",
                            "content": text,
                            "is_label": is_label,
                            "bounds": {
                                "x": round(bbox[0], 1),
                                "y": round(bbox[1], 1),
                                "width": round(bbox[2] - bbox[0], 1),
                                "height": round(bbox[3] - bbox[1], 1),
                                "x2": round(bbox[2], 1),
                                "y2": round(bbox[3], 1),
                            },
                            "style": {
                                "font": span.get("font", ""),
                                "size": round(span.get("size", 0), 1),
                                "bold": bool(flags & 16),
                                "italic": bool(flags & 2),
                            }
                        })
                        text_counter += 1
    
    # Sort elements by position (top to bottom, left to right)
    page_data["elements"].sort(key=lambda e: (
        e["bounds"].get("y", e["bounds"].get("y1", 0)),
        e["bounds"].get("x", e["bounds"].get("x1", 0))
    ))
    
    # Find label-field associations
    _associate_labels(page_data)
    
    return page_data


def _classify_rectangle(width: float, height: float) -> str:
    """Enhanced rectangle classification."""
    area = width * height
    aspect = width / height if height > 0 else 0
    
    # Checkbox: small square
    if 8 < width < 16 and 8 < height < 16 and 0.7 < aspect < 1.3:
        return "checkbox"
    
    # Thin horizontal line (underline)
    if height < 3 and width > 50:
        return "underline"
    
    # Thin vertical line
    if width < 3 and height > 20:
        return "vertical_line"
    
    # Large text area
    if width > 200 and height > 50:
        return "text_area"
    
    # Input field (typical form field)
    if 15 < height < 30 and width > 50:
        return "input_field"
    
    # Signature box (wider, medium height)
    if height > 15 and width > 80 and aspect > 3:
        return "signature_field"
    
    # Small box
    if width < 80 and height < 30:
        return "box"
    
    return "rectangle"


def _associate_labels(page_data: Dict[str, Any]) -> None:
    """Associate text labels with nearby form fields."""
    elements = page_data["elements"]
    
    text_elements = [e for e in elements if e["type"] == "text"]
    field_elements = [e for e in elements if e["type"] == "rectangle" and 
                      e.get("classification") in ("input_field", "checkbox", "text_area", "signature_field")]
    
    for field in field_elements:
        fb = field["bounds"]
        field_y = fb.get("y", 0)
        field_x = fb.get("x", 0)
        
        best_label = None
        best_distance = float("inf")
        
        for text in text_elements:
            if not text.get("is_label"):
                continue
                
            tb = text["bounds"]
            text_y = tb.get("y", 0)
            text_x = tb.get("x", 0)
            text_x2 = tb.get("x2", text_x + tb.get("width", 0))
            
            # Label should be to the left or above the field
            # and relatively close
            
            # Left of field (same row)
            if abs(text_y - field_y) < 15 and text_x2 < field_x and text_x2 > field_x - 200:
                distance = field_x - text_x2
                if distance < best_distance:
                    best_distance = distance
                    best_label = text
            
            # Above field
            elif text_y < field_y and text_y > field_y - 25 and abs(text_x - field_x) < 50:
                distance = field_y - text_y
                if distance < best_distance:
                    best_distance = distance
                    best_label = text
        
        if best_label:
            field["associated_label"] = best_label["id"]
            field["label_text"] = best_label["content"]


def _detect_layout(result: Dict[str, Any]) -> None:
    """Detect semantic layout sections and issues."""
    layout = result["layout"]
    layout["overlaps"] = []
    
    for page in result["pages"]:
        elements = page["elements"]
        page_num = page["page"]
        
        # Find form field rows (label + input on same y)
        for el in elements:
            if el["type"] == "rectangle" and el.get("associated_label"):
                layout["form_fields"].append({
                    "page": page_num,
                    "label": el.get("label_text", ""),
                    "label_id": el.get("associated_label"),
                    "field_id": el["id"],
                    "field_type": el.get("classification"),
                    "bounds": el["bounds"],
                })
        
        # Detect tables (grid of aligned rectangles)
        rects = [e for e in elements if e["type"] == "rectangle"]
        _detect_tables(rects, page_num, layout)
        
        # Detect overlaps
        _detect_overlaps(elements, page_num, layout)


def _detect_tables(rects: List[Dict], page_num: int, layout: Dict) -> None:
    """Detect table structures from aligned rectangles."""
    if len(rects) < 4:
        return
    
    # Group by y position (rows)
    y_groups: Dict[int, List[Dict]] = {}
    for r in rects:
        y_key = int(r["bounds"]["y"] / 5) * 5  # Round to 5pt
        if y_key not in y_groups:
            y_groups[y_key] = []
        y_groups[y_key].append(r)
    
    # Find rows with multiple aligned elements
    for y_key, row_rects in y_groups.items():
        if len(row_rects) >= 3:  # At least 3 columns
            # Check if they're roughly same height
            heights = [r["bounds"]["height"] for r in row_rects]
            if max(heights) - min(heights) < 5:
                layout["tables"].append({
                    "page": page_num,
                    "y": y_key,
                    "columns": len(row_rects),
                    "cell_ids": [r["id"] for r in sorted(row_rects, key=lambda x: x["bounds"]["x"])],
                })


def _detect_overlaps(elements: List[Dict], page_num: int, layout: Dict) -> None:
    """Detect overlapping elements that may indicate layout issues.
    
    Only flags actual text-text overlaps where adjacent texts merge together.
    """
    
    def get_bounds(el: Dict) -> Tuple[float, float, float, float]:
        """Get (x1, y1, x2, y2) for an element."""
        b = el["bounds"]
        x1 = b.get("x", b.get("x1", 0))
        y1 = b.get("y", b.get("y1", 0))
        x2 = b.get("x2", x1 + b.get("width", 0))
        y2 = b.get("y2", y1 + b.get("height", 0))
        return (x1, y1, x2, y2)
    
    def same_row(b1: Tuple, b2: Tuple, tolerance: float = 8) -> bool:
        """Check if two elements are on the same row (similar y)."""
        _, y1_1, _, y2_1 = b1
        _, y1_2, _, y2_2 = b2
        mid1 = (y1_1 + y2_1) / 2
        mid2 = (y1_2 + y2_2) / 2
        return abs(mid1 - mid2) < tolerance
    
    # Check text-to-text merging (adjacent texts that overlap)
    texts = [e for e in elements if e["type"] == "text"]
    
    for i, t1 in enumerate(texts):
        b1 = get_bounds(t1)
        for t2 in texts[i+1:]:
            b2 = get_bounds(t2)
            
            # Only check if on same row
            if not same_row(b1, b2):
                continue
            
            # Determine which is left and which is right
            if b1[0] < b2[0]:
                left_bounds, left_el = b1, t1
                right_bounds, right_el = b2, t2
            else:
                left_bounds, left_el = b2, t2
                right_bounds, right_el = b1, t1
            
            # Gap = right.x1 - left.x2 (positive = space between, negative = overlap)
            gap = right_bounds[0] - left_bounds[2]
            
            # Only flag if texts actually overlap (negative gap > 2pt)
            if gap < -2:
                layout["overlaps"].append({
                    "page": page_num,
                    "type": "text_text_overlap",
                    "severity": "error",
                    "element1": left_el["id"],
                    "element2": right_el["id"],
                    "text1": left_el.get("content", "")[:25],
                    "text2": right_el.get("content", "")[:25],
                    "overlap": round(-gap, 1),
                    "description": f"Texts merge: \"{left_el.get('content', '')[:20]}\" + \"{right_el.get('content', '')[:20]}\""
                })


def _write_summary(result: Dict[str, Any], output_path: Path) -> None:
    """Write human-readable element summary."""
    lines = [
        f"# Analysis: {result['source_name']}",
        "",
        f"Pages: {result['page_count']}",
        f"Total elements: {result['summary']['total_elements']}",
        f"  - Rectangles: {result['summary']['rectangles']}",
        f"  - Lines: {result['summary']['lines']}",
        f"  - Text blocks: {result['summary']['text_blocks']}",
        "",
    ]
    
    for page in result["pages"]:
        lines.append(f"## Page {page['page']}")
        lines.append(f"Image: {page['image']}")
        lines.append(f"Size: {page['width']} x {page['height']}")
        lines.append("")
        
        # Group elements by type
        rectangles = [e for e in page["elements"] if e["type"] == "rectangle"]
        texts = [e for e in page["elements"] if e["type"] == "text"]
        
        if rectangles:
            lines.append("### Rectangles")
            for r in rectangles:
                b = r["bounds"]
                label = f" <- \"{r['label_text']}\"" if r.get("label_text") else ""
                lines.append(f"- `{r['id']}`: {r['classification']} at ({b['x']}, {b['y']}) {b['width']}x{b['height']}{label}")
            lines.append("")
        
        if texts:
            lines.append("### Key Text")
            for t in texts[:30]:  # First 30 text elements
                content = t["content"][:50]
                style = "**bold**" if t["style"]["bold"] else ""
                label_marker = " [LABEL]" if t.get("is_label") else ""
                lines.append(f"- `{t['id']}`: \"{content}\" {style}{label_marker}")
            if len(texts) > 30:
                lines.append(f"  ... and {len(texts) - 30} more text elements")
            lines.append("")
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def _write_layout(result: Dict[str, Any], output_path: Path) -> None:
    """Write semantic layout analysis."""
    layout = result["layout"]
    
    lines = [
        f"# Layout Analysis: {result['source_name']}",
        "",
    ]
    
    # Show overlaps/issues first (most important)
    overlaps = layout.get("overlaps", [])
    if overlaps:
        lines.append("## ⚠️  Layout Issues Detected")
        lines.append("")
        for o in overlaps:
            severity = "🔴" if o["severity"] == "error" else "🟡"
            lines.append(f"- {severity} Page {o['page']}: {o['description']}")
            if o["type"] == "text_text_merge":
                lines.append(f"  - `{o['element1']}` \"{o['text1']}...\"")
                lines.append(f"  - `{o['element2']}` \"{o['text2']}...\"")
            elif o["type"] == "text_rect_overlap":
                lines.append(f"  - Text `{o['element1']}`: \"{o['text']}...\"")
                lines.append(f"  - Overlaps `{o['element2']}` ({o['rect_type']}) by {o['overlap']}pt")
            else:
                lines.append(f"  - `{o['element1']}` and `{o['element2']}`")
        lines.append("")
    else:
        lines.append("## ✅ No Layout Issues Detected")
        lines.append("")
    
    lines.append("## Form Fields (Label -> Input associations)")
    lines.append("")
    
    for ff in layout["form_fields"]:
        lines.append(f"- Page {ff['page']}: \"{ff['label']}\" -> `{ff['field_id']}` ({ff['field_type']})")
    
    if layout["tables"]:
        lines.append("")
        lines.append("## Detected Tables")
        lines.append("")
        for t in layout["tables"]:
            lines.append(f"- Page {t['page']} at y={t['y']}: {t['columns']} columns")
            lines.append(f"  Cells: {', '.join(t['cell_ids'])}")
    
    lines.append("")
    lines.append("## Usage in Contracts")
    lines.append("")
    lines.append("Reference form fields with source_ref:")
    lines.append("```yaml")
    lines.append("requirements:")
    lines.append("  - id: R001")
    lines.append("    source_ref: SRC001#R1_0  # NAME input field")
    lines.append("```")
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def compare_analyses(original: Dict[str, Any], generated: Dict[str, Any]) -> Dict[str, Any]:
    """Compare two PDF analyses and return differences."""
    differences = {
        "page_size_match": True,
        "element_counts": {},
        "missing_in_generated": [],
        "extra_in_generated": [],
        "dimension_mismatches": [],
    }
    
    # Compare page sizes
    for i, (op, gp) in enumerate(zip(original["pages"], generated["pages"])):
        if abs(op["width"] - gp["width"]) > 5 or abs(op["height"] - gp["height"]) > 5:
            differences["page_size_match"] = False
            differences["page_size_diff"] = {
                "page": i + 1,
                "original": f"{op['width']}x{op['height']}",
                "generated": f"{gp['width']}x{gp['height']}",
            }
    
    # Compare element counts by type
    for el_type in ["checkbox", "input_field", "text_area", "signature_field"]:
        orig_count = sum(
            1 for p in original["pages"] 
            for e in p["elements"] 
            if e.get("classification") == el_type
        )
        gen_count = sum(
            1 for p in generated["pages"] 
            for e in p["elements"] 
            if e.get("classification") == el_type
        )
        differences["element_counts"][el_type] = {
            "original": orig_count,
            "generated": gen_count,
            "match": orig_count == gen_count,
        }
    
    return differences

