"""
This script downloads PDFs from the arXiv AWS S3 bucket, extracts the text
from the PDFs, and saves the extracted text as individual text files.
WARNING: This script downloads a very large file, 400GB+ as of 05/01/23.
"""

from bs4 import BeautifulSoup
import boto3
from codecarbon import EmissionsTracker
import configparser
import tarfile
import fitz  # PyMuPDF
import glob
import logging
from multiprocessing import cpu_count, Process
import os
import re
from time import time
import shutil
from tqdm.notebook import tqdm

tracker = EmissionsTracker(log_level="critical")
logging.basicConfig(filename='./log.txt', filemode="w", level=logging.INFO)


def download_tar_file(file_key: str) -> None:
    """
    Downloads a tar file containing PDFs from the arXiv AWS S3 bucket.

    :param file_key: The key of the tar file in the S3 bucket.
    """

    config = configparser.ConfigParser()
    config.read('config.ini')

    aws_access_key_id = config['DEFAULT']['ACCESS_KEY']
    aws_secret_access_key = config['DEFAULT']['SECRET_KEY']

    logging.info(f"Preparing to download ArXiv files from file {file_key}..")

    # Create an S3 client with your AWS credentials
    s3 = boto3.client(
        's3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name='us-east-1'  # same region arxiv bucket is in
    )

    # Set the bucket and file key for the desired tar file
    bucket_name = 'arxiv'
    local_path = file_key.replace('pdf/', '')

    # Download the tar file from S3
    s3.download_file(bucket_name, file_key, file_key.replace('pdf/', ''), ExtraArgs={'RequestPayer': 'requester'})

    logging.info(f"Downloaded {file_key} to {local_path}")


def extract_tar_file(file_key: str) -> None:
    """
    Extracts the PDFs from a downloaded tar file and removes the tar file.

    :param file_key: The key of the tar file in the S3 bucket.
    """

    tar_path = file_key.replace('pdf/', '')
    output_path = f'pdf_files/{file_key[-12:-4]}'

    with tarfile.open(tar_path) as tar:
        tar.extractall(output_path)
        logging.info(f"Extracted {tar_path} to {output_path}")

    os.remove(tar_path)


def extract_text_from_pdfs(file_key: str) -> None:
    """
    Extracts text from the PDFs and saves it to individual text files.

    :param file_key: The key of the tar file in the S3 bucket.
    """

    logging.info(f"Beginning to extract text from PDF {file_key}")

    pdf_file_num = f"{file_key[-12:-4]}/{file_key[-12:-8]}"
    pdf_files_path = os.path.join('pdf_files', pdf_file_num)
    pdf_files = glob.glob(os.path.join(pdf_files_path, '*.pdf'))

    text_files_path = 'text_files'
    if not os.path.exists(text_files_path):
        os.makedirs(text_files_path)

    for pdf_file in pdf_files:
        try:
            text = extract_text_from_pdf(pdf_file)
            save_text_to_file(text, pdf_file, text_files_path)
        except Exception as e:
            logging.warning(f"Error processing PDF file {pdf_file}: {e}")
            continue

    logging.info("Texts extracted from PDF files and saved to individual text files.")
    shutil.rmtree(os.path.join('pdf_files', file_key[-12:-4]))


def extract_text_from_pdf(pdf_file: str) -> str:
    """
    Extracts text from a single PDF file.

    :param pdf_file: The path of the PDF file.
    :return: The extracted text.
    """

    with fitz.open(pdf_file) as doc:
        text = ""
        for page in doc:
            text += page.get_text()
    return text


def save_text_to_file(text: str, pdf_file: str, text_files_path: str) -> None:
    """
    Saves the extracted text to a text file.

    :param text: The extracted text.
    :param pdf_file: The path of the PDF file.
    :param text_files_path: The path of the folder to save the text files.
    """

    txt_filename = os.path.splitext(os.path.basename(pdf_file))[0] + '.txt'
    txt_filepath = os.path.join(text_files_path, txt_filename)
    with open(txt_filepath, 'w') as txt_file:
        txt_file.write(text)


def num_tar_from_arxiv() -> tuple[int, list[str]]:
    """
    Retrieves the number of tar files available in the arXiv S3 bucket and
    the keys of the tar files.

    :return: A tuple containing the number of tar files and a list of their keys.
    """

    logging.info("Attempting to retrieve the number of tar buckets available.")

    config = configparser.ConfigParser()
    config.read('config.ini')

    aws_access_key_id = config['DEFAULT']['ACCESS_KEY']
    aws_secret_access_key = config['DEFAULT']['SECRET_KEY']

    s3 = boto3.client(
        's3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name='us-east-1'  # same region arxiv bucket is in
    )

    s3.download_file(
            Bucket='arxiv',
            Key='pdf/arXiv_pdf_manifest.xml',
            Filename='arXiv_pdf_manifest.xml',
            ExtraArgs={'RequestPayer':'requester'}
    )
    manifest = open('arXiv_pdf_manifest.xml', 'r')
    soup = BeautifulSoup(manifest, 'xml')
    num_tar_files = len(soup.find_all('file'))
    filenames = soup.find_all('filename')

    # Pattern to match the text between <filename> and </filename>
    pattern = r'<filename>(.+)</filename>'

    # Use a list comprehension to apply the regex to each string in the list
    file_keys = [re.search(pattern, str(s)).group(1) for s in filenames if re.search(pattern, str(s))]

    return num_tar_files, file_keys


def tar_to_txt(file_key: str) -> None:
    """
    Downloads a tar file, extracts the PDFs, and saves the extracted text as
    individual text files.

    :param file_key: The key of the tar file in the S3 bucket.
    """

    download_tar_file(file_key)
    extract_tar_file(file_key)
    extract_text_from_pdfs(file_key)


def arxiv_to_txt_parallel() -> None:
    """
    Discovers how many arXiv .tar files are available on S3, then performs
    tar_to_txt on each available file to extract pdfs of research papers,
    convert the pdfs to text, and saves the text as .txt files.
    """

    tracker.start()
    start = time()

    num_tar_files, file_keys = num_tar_from_arxiv()
    batch_size = min(16, cpu_count())

    print("Beginning the process of obtaining PDF's from arXiv's S3 bucket, and converting them to text files.", flush=True)
    print(f"Utilizing {batch_size} cores to download {num_tar_files} tar files from arXiv's S3 bucket.\n", flush=True)

    with tqdm(total=num_tar_files, desc="Processing data", unit="tar_files") as progress_bar:
        for i in range(0, num_tar_files, batch_size):
            processes = [
                Process(target=tar_to_txt,
                        args=(file_keys[j], )) for j in range(i, min(i + batch_size, num_tar_files))
            ]

            for process in processes:
                process.start()

            for idx, process in enumerate(processes):
                process.join()
                progress_bar.update(1)

    tracker.stop()
    end = time()

    print("Process complete! All PDF's extracted from S3, converted to text, and stored into './text_files/'.", flush=True)
    print(f"Total time taken: {(end-start)/60} minutes")


if __name__==  "__main__":
    arxiv_to_txt_parallel()
