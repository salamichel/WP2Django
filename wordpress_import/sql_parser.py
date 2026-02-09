"""
WordPress SQL Dump Parser.

Parses MySQL dump files and extracts table structures and data rows.
Handles WordPress-specific SQL patterns including:
- CREATE TABLE statements
- INSERT INTO statements (single and multi-row)
- Various MySQL data types and escaping
"""

import re
import logging

logger = logging.getLogger("wordpress_import")


class SQLParser:
    """Parse a WordPress MySQL dump file into structured data."""

    # Regex patterns
    RE_CREATE_TABLE = re.compile(
        r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?`?(\w+)`?\s*\((.*?)\)\s*(?:ENGINE|TYPE)\s*=",
        re.DOTALL | re.IGNORECASE,
    )
    RE_COLUMN_DEF = re.compile(
        r"`(\w+)`\s+([\w()]+(?:\s+unsigned)?)",
        re.IGNORECASE,
    )
    RE_INSERT = re.compile(
        r"INSERT\s+(?:INTO\s+)?`?(\w+)`?\s*(?:\(([^)]*)\))?\s*VALUES\s*",
        re.IGNORECASE,
    )

    def __init__(self, file_path):
        self.file_path = file_path
        self.tables = {}  # table_name -> {"columns": [...], "rows": [...]}
        self.table_prefix = "wp_"

    def parse(self):
        """Parse the entire SQL dump file."""
        logger.info("Parsing SQL dump: %s", self.file_path)

        with open(self.file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        self._detect_prefix(content)
        logger.info("Detected table prefix: %s", self.table_prefix)

        self._parse_create_tables(content)
        logger.info("Found %d table definitions", len(self.tables))

        self._parse_inserts(content)

        total_rows = sum(len(t["rows"]) for t in self.tables.values())
        logger.info("Parsed %d total data rows", total_rows)

        return self.tables

    def _detect_prefix(self, content):
        """Auto-detect the WordPress table prefix."""
        match = re.search(r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?`?(\w+?)options`", content, re.IGNORECASE)
        if match:
            self.table_prefix = match.group(1)
        else:
            match = re.search(r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?`?(\w+?)posts`", content, re.IGNORECASE)
            if match:
                self.table_prefix = match.group(1)

    def _parse_create_tables(self, content):
        """Extract all CREATE TABLE definitions."""
        for match in self.RE_CREATE_TABLE.finditer(content):
            table_name = match.group(1)
            body = match.group(2)
            columns = []
            for col_match in self.RE_COLUMN_DEF.finditer(body):
                columns.append(col_match.group(1))
            if columns:
                self.tables[table_name] = {"columns": columns, "rows": []}

    def _parse_inserts(self, content):
        """Extract all INSERT statements and populate table rows."""
        for match in self.RE_INSERT.finditer(content):
            table_name = match.group(1)
            explicit_cols = match.group(2)

            if table_name not in self.tables:
                # Table might not have CREATE TABLE (e.g., inserts only)
                self.tables[table_name] = {"columns": [], "rows": []}

            # Determine columns for this insert
            if explicit_cols:
                cols = [c.strip().strip("`") for c in explicit_cols.split(",")]
            else:
                cols = self.tables[table_name]["columns"]

            # Parse the VALUES section
            start = match.end()
            rows = self._extract_value_tuples(content, start)

            for values in rows:
                if cols and len(values) == len(cols):
                    row = dict(zip(cols, values))
                    self.tables[table_name]["rows"].append(row)
                elif values:
                    # Fallback: use index-based access
                    self.tables[table_name]["rows"].append(
                        {str(i): v for i, v in enumerate(values)}
                    )

    def _extract_value_tuples(self, content, start):
        """Extract value tuples from VALUES (...), (...), ...;"""
        tuples = []
        pos = start
        length = len(content)

        while pos < length:
            # Skip whitespace
            while pos < length and content[pos] in " \t\r\n,":
                pos += 1

            if pos >= length or content[pos] == ";":
                break

            if content[pos] != "(":
                break

            # Parse one tuple
            values, pos = self._parse_tuple(content, pos)
            if values is not None:
                tuples.append(values)

        return tuples

    def _parse_tuple(self, content, pos):
        """Parse a single (val1, val2, ...) tuple, return (values_list, new_pos)."""
        if content[pos] != "(":
            return None, pos

        pos += 1  # skip '('
        values = []
        length = len(content)

        while pos < length:
            # Skip whitespace
            while pos < length and content[pos] in " \t\r\n":
                pos += 1

            if pos >= length:
                break

            if content[pos] == ")":
                pos += 1
                return values, pos

            if content[pos] == ",":
                pos += 1
                continue

            # Parse a value
            val, pos = self._parse_value(content, pos)
            values.append(val)

        return values, pos

    def _parse_value(self, content, pos):
        """Parse a single SQL value (string, number, NULL, etc.)."""
        length = len(content)

        # Skip whitespace
        while pos < length and content[pos] in " \t\r\n":
            pos += 1

        if pos >= length:
            return None, pos

        ch = content[pos]

        # NULL
        if content[pos:pos + 4].upper() == "NULL":
            return None, pos + 4

        # Quoted string
        if ch in ("'", '"'):
            return self._parse_quoted_string(content, pos)

        # Number or other literal
        start = pos
        while pos < length and content[pos] not in (",", ")", ";", " ", "\t", "\r", "\n"):
            pos += 1
        val = content[start:pos]
        # Try to convert to number
        try:
            if "." in val:
                return float(val), pos
            return int(val), pos
        except ValueError:
            return val, pos

    def _parse_quoted_string(self, content, pos):
        """Parse a single-quoted or double-quoted SQL string with escape handling."""
        quote = content[pos]
        pos += 1
        result = []
        length = len(content)

        while pos < length:
            ch = content[pos]
            if ch == "\\":
                # Escaped character
                pos += 1
                if pos < length:
                    esc = content[pos]
                    if esc == "n":
                        result.append("\n")
                    elif esc == "r":
                        result.append("\r")
                    elif esc == "t":
                        result.append("\t")
                    elif esc == "0":
                        result.append("\0")
                    else:
                        result.append(esc)
                pos += 1
            elif ch == quote:
                # Check for doubled quote (escape by doubling)
                if pos + 1 < length and content[pos + 1] == quote:
                    result.append(quote)
                    pos += 2
                else:
                    pos += 1
                    return "".join(result), pos
            else:
                result.append(ch)
                pos += 1

        return "".join(result), pos

    def get_table(self, suffix):
        """Get table data by suffix (e.g., 'posts' -> 'wp_posts')."""
        full_name = self.table_prefix + suffix
        return self.tables.get(full_name, {"columns": [], "rows": []})

    def get_core_tables(self):
        """Return list of WordPress core table suffixes found."""
        core_suffixes = [
            "posts", "postmeta", "comments", "commentmeta",
            "terms", "termmeta", "term_taxonomy", "term_relationships",
            "users", "usermeta", "options", "links",
        ]
        found = []
        for suffix in core_suffixes:
            full = self.table_prefix + suffix
            if full in self.tables and self.tables[full]["rows"]:
                found.append(suffix)
        return found

    def get_plugin_tables(self):
        """Detect non-core WordPress tables (likely from plugins)."""
        core_suffixes = {
            "posts", "postmeta", "comments", "commentmeta",
            "terms", "termmeta", "term_taxonomy", "term_relationships",
            "users", "usermeta", "options", "links",
        }
        core_full = {self.table_prefix + s for s in core_suffixes}
        plugin_tables = {}

        for table_name in self.tables:
            if table_name not in core_full and table_name.startswith(self.table_prefix):
                # Try to identify the plugin
                suffix = table_name[len(self.table_prefix):]
                plugin_name = self._identify_plugin(suffix)
                if plugin_name not in plugin_tables:
                    plugin_tables[plugin_name] = []
                plugin_tables[plugin_name].append(table_name)

        return plugin_tables

    def _identify_plugin(self, table_suffix):
        """Try to identify which plugin a table belongs to."""
        known_plugins = {
            "woocommerce": ["woocommerce_", "wc_"],
            "yoast_seo": ["yoast_", "yoast_seo_"],
            "acf": ["acf_"],  # Advanced Custom Fields stores in postmeta mostly
            "contact_form_7": ["cf7_", "contact_form_"],
            "wpforms": ["wpforms_"],
            "gravity_forms": ["gf_", "rg_"],
            "elementor": ["elementor_"],
            "wpseo": ["wpseo_"],
            "redirection": ["redirection_"],
            "wordfence": ["wfls_", "wfblockediplog", "wfconfig", "wfcrawlers",
                          "wffilechanges", "wfhits", "wfhoover", "wfissues",
                          "wfknownfilelist", "wflivetraffichuman", "wflocs",
                          "wflogins", "wfnotifications", "wfpendingissues",
                          "wfreversecache", "wfsnipcache", "wfstatus",
                          "wftrafficrates"],
            "wpml": ["icl_"],
            "polylang": ["term_language", "term_translations"],
        }

        for plugin_name, prefixes in known_plugins.items():
            for prefix in prefixes:
                if table_suffix.startswith(prefix):
                    return plugin_name

        return "unknown"
