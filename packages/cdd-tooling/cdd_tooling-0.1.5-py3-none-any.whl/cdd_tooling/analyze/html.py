# src/cdd/analyze/html.py
"""HTML analyzer for web project contracts."""
from __future__ import annotations

import json
import re
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from collections import defaultdict


class HTMLStructureParser(HTMLParser):
    """Parse HTML and extract structural information."""
    
    def __init__(self):
        super().__init__()
        self.elements: List[Dict[str, Any]] = []
        self.element_counts: Dict[str, int] = defaultdict(int)
        self.classes_found: Set[str] = set()
        self.ids_found: Set[str] = set()
        self.images: List[Dict[str, Any]] = []
        self.links: List[Dict[str, Any]] = []
        self.buttons: List[Dict[str, Any]] = []
        self.text_content: List[str] = []
        self.in_style = False
        self.in_script = False
        self.css_classes_defined: Set[str] = set()
        self.current_text = ""
        
    def handle_starttag(self, tag: str, attrs: List[tuple]) -> None:
        attrs_dict = dict(attrs)
        self.element_counts[tag] += 1
        
        if tag == 'style':
            self.in_style = True
        if tag == 'script':
            self.in_script = True
            
        # Track classes
        if 'class' in attrs_dict:
            for cls in attrs_dict['class'].split():
                self.classes_found.add(cls)
                
        # Track IDs
        if 'id' in attrs_dict:
            self.ids_found.add(attrs_dict['id'])
            
        # Track images
        if tag == 'img':
            src = attrs_dict.get('src', '')
            img_info = {
                'src_type': 'base64' if src.startswith('data:') else 'url',
                'alt': attrs_dict.get('alt', ''),
                'src_preview': src[:80] + '...' if len(src) > 80 else src
            }
            if img_info['src_type'] == 'base64':
                match = re.match(r'data:image/(\w+);base64,(.+)', src)
                if match:
                    img_info['format'] = match.group(1)
                    img_info['base64_length'] = len(match.group(2))
            self.images.append(img_info)
            
        # Track links
        if tag == 'a':
            self.links.append({
                'href': attrs_dict.get('href', ''),
                'class': attrs_dict.get('class', '')
            })
            
        # Track buttons
        if tag == 'button':
            self.buttons.append({
                'class': attrs_dict.get('class', ''),
                'type': attrs_dict.get('type', 'button')
            })
            
    def handle_endtag(self, tag: str) -> None:
        if tag == 'style':
            self.in_style = False
        if tag == 'script':
            self.in_script = False
            
    def handle_data(self, data: str) -> None:
        data = data.strip()
        if data and not self.in_style and not self.in_script:
            self.text_content.append(data)
            
        # Extract CSS class definitions from style blocks
        if self.in_style:
            classes = re.findall(r'\.([a-zA-Z_-][a-zA-Z0-9_-]*)\s*\{', data)
            self.css_classes_defined.update(classes)


def analyze_html(source_path: Path, output_dir: Path) -> Dict[str, Any]:
    """
    Analyze HTML file structure for evidence-based contracts.
    
    Args:
        source_path: Path to HTML file
        output_dir: Directory for output artifacts
        
    Returns:
        Analysis result with structure and summary
    """
    source_path = Path(source_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    content = source_path.read_text(encoding='utf-8')
    
    # Parse HTML
    parser = HTMLStructureParser()
    parser.feed(content)
    
    # Extract additional patterns
    screen_labels = re.findall(r'<div class="screen-label">([^<]+)</div>', content)
    step_titles = re.findall(r'<div class="step-title">([^<]+)</div>', content)
    
    # Check for common required elements (configurable patterns)
    required_elements = {
        'app_icon': 'app-icon' in parser.classes_found,
        'app_title': 'app-title' in parser.classes_found,
        'ios_button': any('btn-ios' in b.get('class', '') for b in parser.buttons),
        'android_button': any('btn-android' in b.get('class', '') for b in parser.buttons),
        'qr_code': any('qrserver.com' in img.get('src_preview', '') or 'qr' in img.get('alt', '').lower() for img in parser.images),
        'icon_base64_embedded': any(img['src_type'] == 'base64' and img.get('format') == 'png' for img in parser.images),
    }
    
    # Build result
    result = {
        'file': str(source_path),
        'source_name': source_path.name,
        'type': 'html',
        'summary': {
            'total_elements': sum(parser.element_counts.values()),
            'num_screens': len(screen_labels),
            'num_images': len(parser.images),
            'num_buttons': len(parser.buttons),
            'num_steps': len(step_titles),
        },
        'screens': screen_labels,
        'steps': step_titles,
        'images': parser.images,
        'required_elements': required_elements,
        'css_classes_used': sorted(parser.classes_found),
        'css_classes_defined': sorted(parser.css_classes_defined),
        'ids': sorted(parser.ids_found),
        'element_counts': dict(parser.element_counts),
        'output_dir': str(output_dir),
    }
    
    # Write structure.json
    structure_path = output_dir / 'structure.json'
    structure_path.write_text(json.dumps(result, indent=2))
    
    # Write elements.md (human-readable)
    elements_md = _generate_elements_md(result)
    (output_dir / 'elements.md').write_text(elements_md)
    
    return result


def _generate_elements_md(result: Dict[str, Any]) -> str:
    """Generate human-readable element catalog."""
    lines = [
        f"# HTML Analysis: {result['source_name']}",
        "",
        "## Summary",
        "",
        f"- Total elements: {result['summary']['total_elements']}",
        f"- Images: {result['summary']['num_images']}",
        f"- Buttons: {result['summary']['num_buttons']}",
        f"- Screens: {result['summary']['num_screens']}",
        f"- Steps: {result['summary']['num_steps']}",
        "",
        "## Required Elements Check",
        "",
    ]
    
    for key, present in result['required_elements'].items():
        status = "✓" if present else "✗"
        lines.append(f"- [{status}] {key}")
    
    lines.extend([
        "",
        "## CSS Classes Used",
        "",
    ])
    for cls in result['css_classes_used'][:50]:  # Limit to first 50
        lines.append(f"- `{cls}`")
    if len(result['css_classes_used']) > 50:
        lines.append(f"- ... and {len(result['css_classes_used']) - 50} more")
    
    lines.extend([
        "",
        "## Images",
        "",
    ])
    for img in result['images']:
        lines.append(f"- [{img['src_type']}] alt=\"{img['alt']}\"")
    
    lines.extend([
        "",
        "## Element Counts",
        "",
        "| Tag | Count |",
        "|-----|-------|",
    ])
    for tag, count in sorted(result['element_counts'].items()):
        lines.append(f"| {tag} | {count} |")
    
    return "\n".join(lines)


def compare_html_analyses(original: Dict[str, Any], generated: Dict[str, Any]) -> Dict[str, Any]:
    """Compare two HTML analyses."""
    diff = {
        'required_elements_match': True,
        'required_elements_diff': {},
        'element_counts': {},
        'classes_added': [],
        'classes_removed': [],
    }
    
    # Compare required elements
    for key in set(original.get('required_elements', {}).keys()) | set(generated.get('required_elements', {}).keys()):
        orig_val = original.get('required_elements', {}).get(key)
        gen_val = generated.get('required_elements', {}).get(key)
        if orig_val != gen_val:
            diff['required_elements_match'] = False
            diff['required_elements_diff'][key] = {'original': orig_val, 'generated': gen_val}
    
    # Compare element counts
    orig_counts = original.get('element_counts', {})
    gen_counts = generated.get('element_counts', {})
    for tag in set(orig_counts.keys()) | set(gen_counts.keys()):
        orig = orig_counts.get(tag, 0)
        gen = gen_counts.get(tag, 0)
        diff['element_counts'][tag] = {
            'original': orig,
            'generated': gen,
            'match': orig == gen,
        }
    
    # Compare CSS classes
    orig_classes = set(original.get('css_classes_used', []))
    gen_classes = set(generated.get('css_classes_used', []))
    diff['classes_added'] = sorted(gen_classes - orig_classes)
    diff['classes_removed'] = sorted(orig_classes - gen_classes)
    
    return diff
