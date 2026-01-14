Excel_Mcp
=========\n+
Small utility package exposing a CLI `excel-mcp` for basic Excel tasks.\n+\n+Usage examples:\n+\n+```bash\n+# list sheets\n+excel-mcp describe myworkbook.xlsx\n+\n+# read first 10 rows\n+excel-mcp read myworkbook.xlsx --sheet Sheet1 --limit 10\n+\n+# write rows from a JSON file (array of arrays)\n+excel-mcp write myworkbook.xlsx --sheet Sheet1 --rows-file rows.json\n+```\n+\n+This package depends on `openpyxl` and optionally `pandas` for JSON export convenience.\n+\n*** End Patch

