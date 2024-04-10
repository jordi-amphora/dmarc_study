# DMARC Report Parser

This script parses DMARC reports from MBOX files, aggregates the data, and writes it to a CSV file.

## Prerequisites

You need to have Python installed on your machine to run this script.

## Usage

1. Download your MBOX files from Google Takeout. You can follow the instructions [here](https://support.google.com/accounts/answer/3024190) to download your data.

2. Place the downloaded MBOX files in the `../input_files` directory.

3. Run the script using the command `python scripts/extract.py`.

The script will process each MBOX file, extract the DMARC reports, decompress them, aggregate the data, and write it to a CSV file.

## Output

The output will be a CSV file named `output.csv` located in the root directory. The CSV file will contain the following columns:

- version
- org_name
- email
- report_id
- date_begin
- date_end
- domain
- policy
- source_ip
- count
- disposition
- dkim_pass
- spf_result

Each row in the CSV file represents a record from a DMARC report.

## Note

The script assumes that the MBOX files are located in the `../input_files` directory and the output directory is `../output_files`. If you want to change these directories, you need to modify the `input_dir` and `output_dir` variables in the script.