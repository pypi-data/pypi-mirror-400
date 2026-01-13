#!/usr/bin/env python3

import argparse

import pandas as pd
import tabulate

# HTML + DataTables JavaScript with column filters and fixed header
html_code = """
<html>
<head>
    <link rel="stylesheet"
          href="https://cdn.datatables.net/1.13.4/css/jquery.dataTables.min.css">
    <link rel="stylesheet"
          href="https://cdn.datatables.net/fixedheader/3.2.0/css/fixedHeader.dataTables.min.css">
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://cdn.datatables.net/1.13.4/js/jquery.dataTables.min.js"></script>
    <script src="https://cdn.datatables.net/fixedheader/3.2.0/js/dataTables.fixedHeader.min.js"></script>
    <script>
        $(document).ready(function() {{
            // Add input fields to each column header
            $('#myTable thead tr').clone(true).appendTo('#myTable thead');
            $('#myTable thead tr:eq(1) th').each(function (i) {{
                var title = $(this).text();
                $(this).html('<input type="text" placeholder="Filter ' + title + '" />');

                // Enable per-column filtering
                $('input', this).on('keyup change', function () {{
                    if (table.column(i).search() !== this.value) {{
                        table.column(i).search(this.value).draw();
                    }}
                }});
            }});

            // Initialize DataTable with ordering, fixed header, and per-column search
            var table = $('table').DataTable({{
                orderCellsTop: true,  // Allow column headers to remain fixed
                fixedHeader: true      // Enable the fixed header functionality
            }});
        }});
    </script>
</head>
<body>
    <h2>{query}</h2>
    {html_table}
</body>
</html>
"""

def main():
    parser = argparse.ArgumentParser(description="Analyze and visualize AVL trace data")
    parser.add_argument("--tracefile", nargs="+", required=True, type=str, help="Trace file(s) to analyze.")
    parser.add_argument("--query", type=str, help="Query to filter trace data.", default=None)
    parser.add_argument("--sort", type=str, help="Column to sort by.", default=None)
    parser.add_argument("--output", type=str, help="Output HTML file name.", default=None)
    parser.add_argument("--debug", action="store_true", help="Enable debug mode for detailed output.")

    args = parser.parse_args()

    # Read in trace files
    df = pd.concat([pd.read_csv(f) for f in args.tracefile], ignore_index=True)

    # Run Query if provided
    if args.query:
        if args.debug:
            print(f"Applying query: {args.query}")
        df = df.query(args.query)

    # Sort by column if specified
    if args.sort:
        if args.debug:
            print(f"Sorting by column: {args.sort}")
        df = df.sort_values(by=args.sort)

    # Output to HTML if specified
    if args.output:
        if args.debug:
            print(f"Writing output to: {args.output}")
        html_table = df.to_html(index=False, table_id="myTable")
        html_content = html_code.format(query=args.query or "AVL Trace Analysis", html_table=html_table)

        with open(args.output, "w") as f:
            f.write(html_content)
    else:
        print(tabulate.tabulate(df.values.tolist(), headers=df.columns, tablefmt="grid"))

if __name__ == "__main__":
    main()
    exit(0)
