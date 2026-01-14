"""
Font scanner service for validating and analyzing font files.
"""

from typing import Dict, Any, Set, List
import struct
from optikka_design_data_layer import logger


class FontPreflight:
    """Service for preflight validation and analysis of font files."""

    @staticmethod
    def detect_file_signature(buf: bytes) -> str:
        """
        Detect file type by magic bytes (file signature).
        Returns: sfnt-ttf, sfnt-otf, ttc, woff, woff2, html, zip, pdf, unknown
        """
        if len(buf) < 4:
            return "unknown"

        # SFNT fonts - use readUInt32BE for TrueType magic
        if len(buf) >= 4:
            magic32 = struct.unpack(">I", buf[0:4])[0]
            if magic32 == 0x00010000:
                return "sfnt-ttf"  # TrueType: 0x00010000

        # OpenType CFF - check first 4 bytes as ASCII
        if len(buf) >= 4 and buf[0:4].decode("ascii", errors="ignore") == "OTTO":
            return "sfnt-otf"

        # Font collections and wrappers
        if len(buf) >= 4:
            magic4 = buf[0:4].decode("ascii", errors="ignore")
            if magic4 == "ttcf":
                return "ttc"  # TrueType Collection
            if magic4 == "wOFF":
                return "woff"  # WOFF
            if magic4 == "wOF2":
                return "woff2"  # WOFF2

        # ZIP - check for PK\x03\x04
        if len(buf) >= 4 and buf[0:4] == b"PK\x03\x04":
            return "zip"

        # PDF - check for %PDF
        if len(buf) >= 4 and buf[0:4].decode("ascii", errors="ignore") == "%PDF":
            return "pdf"

        # HTML - check first 64 bytes for HTML markers
        if len(buf) >= 64:
            head64 = buf[0:64].decode("utf8", errors="ignore").lower()
            if "<!doctype" in head64 or "<html" in head64:
                return "html"
        elif len(buf) >= 4:
            head4 = buf[0 : min(4, len(buf))].decode("utf8", errors="ignore").lower()
            if head4.startswith("<!do") or head4.startswith("<htm"):
                return "html"

        return "unknown"

    @staticmethod
    def detect_mime_type(signature: str) -> str:
        """Map file signature to MIME type."""
        mime_map = {
            "sfnt-ttf": "font/ttf",
            "sfnt-otf": "font/otf",
            "ttc": "font/collection",
            "woff": "font/woff",
            "woff2": "font/woff2",
            "html": "text/html",
            "zip": "application/zip",
            "pdf": "application/pdf",
            "unknown": "application/octet-stream",
        }
        return mime_map.get(signature, "application/octet-stream")

    @staticmethod
    def read_sfnt_table_tags(buf: bytes, signature: str) -> Set[str]:
        """
        Read SFNT table tags from font buffer.
        Returns a set of table tag strings.
        """
        # Only process SFNT fonts
        if signature not in ("sfnt-ttf", "sfnt-otf"):
            return set()

        if len(buf) < 12:
            return set()

        num_tables = struct.unpack(">H", buf[4:6])[0]

        # Sanity check: if numTables is absurdly high, treat as corrupt/non-font
        if num_tables > 200:
            return set()

        tags = set()

        offset = 12
        for i in range(num_tables):
            # Ensure we have enough bytes for the table entry (16 bytes)
            if offset + 16 > len(buf):
                break
            tag = buf[offset : offset + 4].decode("ascii", errors="ignore")
            tags.add(tag)
            offset += 16

        return tags

    @staticmethod
    def classify_tables(tags: Set[str]) -> str:
        """
        Classify font based on table tags.
        Returns: vector, vector+color, bitmap, bitmap+color, svg-color-only, unknown
        """
        has_vector = "glyf" in tags or "CFF " in tags or "CFF2" in tags

        has_bitmap = (
            ("CBDT" in tags and "CBLC" in tags)
            or ("EBDT" in tags and "EBLC" in tags)
            or "sbix" in tags
        )

        has_color = "COLR" in tags and "CPAL" in tags

        has_svg = "SVG " in tags

        if has_vector and has_color:
            return "vector+color"
        if has_bitmap and has_color:
            return "bitmap+color"
        if not has_vector and not has_bitmap and has_svg:
            return "svg-color-only"
        if has_vector:
            return "vector"
        if has_bitmap:
            return "bitmap"
        return "unknown"

    @staticmethod
    def score_font_quality(tags: Set[str], kind: str) -> Dict[str, Any]:
        """
        Score font quality for layout/fit fidelity (0-100).
        Returns dict with score, recommendation, flags, strengths, and reasons.
        """
        score = 0
        flags: List[str] = []
        strengths: List[str] = []
        reasons: List[str] = []

        has = lambda t: t in tags
        has_any = lambda *ts: any(t in tags for t in ts)

        # Core capabilities
        outline = has_any("glyf", "CFF ", "CFF2")
        cmap = has("cmap")
        head = has("head")
        hhea = has("hhea")
        hmtx = has("hmtx")
        has_os2 = has("OS/2")
        has_loca = has("loca")
        has_maxp = has("maxp")

        # Layout/shaping fidelity
        has_gpos = has("GPOS")
        has_gsub = has("GSUB")
        has_kern = has("kern")

        # Color tables
        has_colr = has("COLR")
        has_cpal = has("CPAL")
        has_svg = has("SVG ")

        # Bitmap tables
        has_cbdt = has("CBDT") and has("CBLC")
        has_ebdt = has("EBDT") and has("EBLC")
        has_sbix = has("sbix")
        bitmap = has_cbdt or has_ebdt or has_sbix

        # Hard gates: outline, cmap, head, hhea, hmtx
        if not outline:
            flags.append("no-outline")
            reasons.append("Missing outline tables (glyf/CFF/CFF2)")
        else:
            score += 28
            strengths.append("outline")
            strengths.append("truetype-outlines" if has("glyf") else "cff-outlines")

        if not cmap:
            flags.append("missing-cmap")
            reasons.append("Missing cmap (char→glyph mapping)")
            score -= 25
        else:
            score += 14
            strengths.append("cmap")

        if not head:
            flags.append("missing-head")
            reasons.append("Missing head (unitsPerEm/global header)")
            score -= 20
        else:
            score += 9
            strengths.append("head")

        if not hhea:
            flags.append("missing-hhea")
            reasons.append("Missing hhea (horizontal header metrics)")
            score -= 15
        else:
            score += 11
            strengths.append("hhea")

        if not hmtx:
            flags.append("missing-hmtx")
            reasons.append("Missing hmtx (advance widths)")
            score -= 20
        else:
            score += 14
            strengths.append("hmtx")

        # Supporting tables
        if has_maxp:
            score += 3
            strengths.append("maxp")
        else:
            flags.append("missing-maxp")

        if outline and has("glyf") and not has_loca:
            score -= 10
            flags.append("suspect-glyf-without-loca")
            reasons.append("glyf present but loca missing (suspect TTF)")
        elif has_loca:
            score += 2
            strengths.append("loca")

        # OS/2
        if has_os2:
            score += 4
            strengths.append("os2")
        else:
            flags.append("missing-os2")

        # Shaping fidelity
        if has_gpos:
            score += 10
            strengths.append("gpos")
            strengths.append("kerning-modern")
        elif has_kern:
            score += 7
            strengths.append("kern")
            strengths.append("kerning-legacy")
        else:
            flags.append("no-kerning")
            reasons.append("No kerning tables (widths may differ from design tools)")

        if has_gsub:
            score += 8
            strengths.append("gsub")
            strengths.append("ligatures/substitutions")
        else:
            flags.append("no-gsub")

        # Color support
        if has_colr and has_cpal:
            score += 1
            strengths.append("colr/cpal")
            strengths.append("color-vector")

        # SVG handling
        if has_svg:
            if not outline and not bitmap:
                score = 0
                flags.append("svg-only")
                reasons.append("SVG table without outlines (Skia support unreliable)")
            else:
                flags.append("has-svg")
                reasons.append("Has SVG table (support may vary)")
                score -= 3

        # Bitmap risk
        if bitmap:
            flags.append("bitmap-glyphs")
            reasons.append("Bitmap glyph tables present (scaling may blur)")
            score -= 30

            if not outline:
                score -= 20
                flags.append("bitmap-only")
                reasons.append("Bitmap-only (no outlines)")
            else:
                strengths.append("bitmap-glyphs")

        # Hinting tables
        hinting_tables = ["cvt ", "fpgm", "prep", "gasp", "hdmx", "VDMX", "LTSH"]
        hinting_count = sum(1 for t in hinting_tables if has(t))
        if hinting_count > 0:
            score += min(1, hinting_count)

        # Semantic caps
        if not has_gpos and not has_kern:
            score = min(score, 90)

        if not has_gsub:
            score = min(score, 95)

        if bitmap and not outline:
            score = min(score, 25)

        # Clamp 0..100
        score = max(0, min(100, score))

        # Recommendation aligned to preflight policy
        if kind == "svg-color-only":
            recommendation = "reject"
        elif kind == "unknown":
            recommendation = "reject"
        elif kind in ("bitmap", "bitmap+color"):
            recommendation = "warn"
        else:
            recommendation = "allow"

        # If score is extremely low, override to warn/reject even if kind is vector
        if score < 35 and recommendation == "allow":
            recommendation = "warn"

        # Filter strengths to high-signal items only
        high_signal_strengths = [
            s
            for s in strengths
            if s
            in (
                "outline",
                "truetype-outlines",
                "cff-outlines",
                "os2",
                "gpos",
                "kern",
                "kerning-modern",
                "kerning-legacy",
                "gsub",
                "ligatures/substitutions",
                "colr/cpal",
                "color-vector",
                "bitmap-glyphs",
            )
        ]
        strengths_unique = list(set(high_signal_strengths))

        return {
            "score": score,
            "recommendation": recommendation,
            "flags": flags,
            "strengths": strengths_unique,
            "reasons": reasons,
        }

    def scan_font(self, font_buffer: bytes) -> Dict[str, Any]:
        """
        Scan a font file and return comprehensive validation results.

        Args:
            font_buffer: Font file as bytes

        Returns:
            Dict with signature, mime, kind, score, recommendation, tags, flags, strengths, reasons
        """
        try:
            signature = self.detect_file_signature(font_buffer)
            mime = self.detect_mime_type(signature)

            # Skip non-SFNT files
            if signature not in ("sfnt-ttf", "sfnt-otf"):
                is_font_container = signature in ("ttc", "woff", "woff2")
                return {
                    "signature": signature,
                    "mime": mime,
                    "kind": None,
                    "score": None,
                    "recommendation": ("skip-container" if is_font_container else "skip-nonfont"),
                    "flags": [],
                    "strengths": [],
                    "tags": [],
                    "error": (
                        "Not an SFNT font file"
                        if not is_font_container
                        else "Font container (convert to ttf/otf)"
                    ),
                }

            tags = self.read_sfnt_table_tags(font_buffer, signature)

            # If tags are empty after reading, treat as unknown/corrupt
            if len(tags) == 0:
                return {
                    "signature": signature,
                    "mime": mime,
                    "kind": "unknown",
                    "score": 0,
                    "recommendation": "reject",
                    "flags": ["corrupt-or-invalid"],
                    "strengths": [],
                    "tags": [],
                    "error": "Unable to read SFNT table tags",
                }

            kind = self.classify_tables(tags)
            quality = self.score_font_quality(tags, kind)

            return {
                "signature": signature,
                "mime": mime,
                "kind": kind,
                "score": quality["score"],
                "recommendation": quality["recommendation"],
                "flags": quality["flags"],
                "strengths": quality["strengths"],
                "tags": sorted(list(tags)),
                "reasons": quality["reasons"],
            }

        except Exception as e:
            logger.error(f"Error scanning font: {e}", exc_info=True)
            return {
                "signature": "unknown",
                "mime": "application/octet-stream",
                "kind": None,
                "score": None,
                "recommendation": "error",
                "flags": ["error"],
                "strengths": [],
                "tags": [],
                "error": str(e),
            }
