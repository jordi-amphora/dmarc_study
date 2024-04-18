import mailbox
import os
import email
import gzip
import os
from pathlib import Path
import xml.etree.ElementTree as ET
import os
import csv
import os
import pdb

def write_to_csv(aggregated_data, output_file):
    """Writes aggregated data to a CSV file."""
    with open(output_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write the header
        headers = ['version', 'org_name', 'email', 'report_id', 'date_begin', 'date_end', 'domain', 'policy',
                   'source_ip', 'count', 'disposition', 'dkim_pass', 'spf_result']
        writer.writerow(headers)
        
        # Write data rows
        for data in aggregated_data:
            for record in data['records']:
                row = [
                    data['version'],
                    data['org_name'],
                    data['email'],
                    data['report_id'],
                    data['date_range']['begin'],
                    data['date_range']['end'],
                    data['domain'],
                    data['policy'],
                    record['source_ip'],
                    record['count'],
                    record['disposition'],
                    record['dkim_pass'],
                    record['spf_result']
                ]
                writer.writerow(row)


def parse_dmarc_xml(file_path):
    """Parse a DMARC XML file and extract comprehensive data using XPath."""
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Extracting fields from the XML structure
    version = root.find('version').text if root.find('version') is not None else 'Unknown'
    org_name = root.find('.//org_name').text if root.find('.//org_name') is not None else 'Unknown'
    email = root.find('.//email').text if root.find('.//email') is not None else 'Unknown'
    report_id = root.find('.//report_id').text if root.find('.//report_id') is not None else 'Unknown'
    date_begin = root.find('.//date_range/begin').text if root.find('.//date_range/begin') is not None else 'Unknown'
    date_end = root.find('.//date_range/end').text if root.find('.//date_range/end') is not None else 'Unknown'
    domain = root.find('.//policy_published/domain').text if root.find('.//policy_published/domain') is not None else 'Unknown'
    policy = root.find('.//policy_published/p').text if root.find('.//policy_published/p') is not None else 'Unknown'

    # Extracting records
    records = []
    for row in root.findall('.//record/row'):
        source_ip = row.find('source_ip').text if row.find('source_ip') is not None else 'Unknown'
        count = row.find('count').text if row.find('count') is not None else 'Unknown'
        disposition = row.find('.//disposition').text if row.find('.//disposition') is not None else 'Unknown'
        dkim_pass = row.find('.//dkim').text if row.find('.//dkim') is not None else 'Unknown'
        spf_result = row.find('.//spf').text if row.find('.//spf') is not None else 'Unknown'

        record = {
            'source_ip': source_ip,
            'count': count,
            'disposition': disposition,
            'dkim_pass': dkim_pass,
            'spf_result': spf_result
        }
        records.append(record)
    # pdb.set_trace()

    return {
        'version': version,
        'org_name': org_name,
        'email': email,
        'report_id': report_id,
        'date_range': {'begin': date_begin, 'end': date_end},
        'domain': domain,
        'policy': policy,
        'records': records
    }

def aggregate_data(directory):
    """Aggregate data from multiple DMARC reports in a specified directory."""
    aggregated_data = []
    
    # Iterate over all XML files in the directory
    for filename in os.listdir(directory):
        if filename.endswith('.xml'):
            file_path = os.path.join(directory, filename)
            report_data = parse_dmarc_xml(file_path)
            aggregated_data.append(report_data)
    
    return aggregated_data


def decompress_gz_files(input_dir):
    # Path object for the input directory
    input_path = Path(input_dir)
    
    # Iterate over all gzip files in the directory
    for gz_path in input_path.glob('*.gz'):
        # Define the output file path (same name without .gz)
        output_file_path = gz_path.with_suffix('')

        # Open the gzip file and create the output file
        with gzip.open(gz_path, 'rb') as f_in, open(output_file_path, 'wb') as f_out:
            # Copy contents from gzip file to output file
            f_out.write(f_in.read())
            print(f"Decompressed: {output_file_path}")


def extract_attachments(mbox_path, output_dir):
    # Ensure output directory exists
    print(f"start extract_attachments")
    if not os.path.isdir(output_dir):
        print("creating output_dir")
        os.makedirs(output_dir)

    # Open the MBOX file
    mbox = mailbox.mbox(mbox_path)

    for message in mbox:
        if message.is_multipart():
            for part in message.walk():
                # Check if the part is an attachment
                content_disposition = part.get('Content-Disposition', None)
                if content_disposition and 'attachment' in content_disposition:
                    file_name = part.get_filename()
                    # Ensure filename is provided and does not contain path traversal
                    if file_name:
                        file_name = os.path.basename(file_name)
                        file_path = os.path.join(output_dir, file_name)
                        # Write the file out to disk
                        with open(file_path, 'wb') as file:
                            file.write(part.get_payload(decode=True))
                        print(f"Extracted: {file_path}")

if __name__ == "__main__":
    input_dir = "../input_files"
    input_path = Path(input_dir)
    
    # Iterate over all gzip files in the directory
    for mbox_path in input_path.glob('*.mbox'):
        print(f"processing mbox: {mbox_path}")

        # Path to your MBOX file
        # mbox_path = 'reports.mbox'
        # Directory where you want to save attachments
        output_dir = '../output_files'
        extract_attachments(mbox_path, output_dir)
        decompress_gz_files(output_dir)
        # data = aggregate_data(output_dir)
        # print("Aggregated Data:")
        # for report in data:
        #     print(report)

        data = aggregate_data(output_dir)
        output_file = '../output.csv'
        write_to_csv(data, output_file)
        print(f"Data has been written to {output_file}")



