import argparse
import os
import re
import shutil

import fitz


def create_thumbnails(source, destination, corpus):
    print(f"Creating thumbnails for files in directory:", source)

    for file in os.listdir(source):
        if not file.lower().endswith(".pdf"):
            continue

        path = os.path.join(source, file)

        thumbnails_name = ""
        if corpus == 'dzk':
            try:
                # validate file name format
                thumbnails_name = generate_dzk_file(file[:-4])  # Remove extension for processing
            except ValueError as e:
                print(f"Error occurred while generating thumbnail name for file '{file}':", e)
                continue
        elif corpus == 'yuparl':
            try:
                # validate file name format
                thumbnails_name = generate_yuparl_file(file[:-4])  # Remove extension for processing
            except ValueError as e:
                print(f"Error occurred while generating thumbnail name for file '{file}':", e)
                continue
        else:
            raise NotImplementedError(f"Thumbnail generation for corpus '{corpus}' is not implemented.")

        # get first page of pdf
        pdf_document = fitz.open(path)
        first_page = pdf_document[0]

        # generate thumbnail
        image = first_page.get_pixmap()
        image.save(os.path.join(destination, f"{thumbnails_name}.png"))

        print(f"Created thumbnail for '{file}'")


def generate_dzk_file(old_name):
    old_name_format = r'DezelniZborKranjski-(\d{8})-(\d{1,2})-(\d{1,2})(p(\d+))?'
    match = re.match(old_name_format, old_name)
    if not match:
        raise ValueError(f"File name '{old_name}' does not match expected format for dzk.")

    # date
    date = old_name.split("-")[1]
    year = date[:4]
    month = date[4:6]
    day = date[6:]

    # volume
    volume = old_name.split("-")[2]
    # and number
    number = old_name.split("-")[3]

    # rename file
    new_file_name = f"DZK_{year}-{month}-{day}_{volume}_{number}"
    return new_file_name


def generate_yuparl_file(old_name):
    old_name_format = r'(\d{8})-(\w+)-(\d{1,})?(\w+(\d+))?'
    match = re.match(old_name_format, old_name)
    if not match:
        raise ValueError(f"File name '{old_name}' does not match expected format for yuparl.")

    session_type_dict = {
        "PrivremenoNarodnoPredstavnistvo": "PP",
        "NarodnoPretstavnistvo": "NP",
        "ZakonodajniOdbor": "ZO",
        "Senat": "SE",
        "NarodnaSkupstina": "NS",
    }

    date_part, session_type_part, number_part = old_name.split("-")

    year = date_part[:4]
    month = date_part[4:6]
    day = date_part[6:8]
    date = f"{year}-{month}-{day}"

    session_type = session_type_dict.get(session_type_part)
    if session_type is None:
        raise ValueError(f"Session type '{session_type_part}' is not recognized.")


    number = number_part
    if "prethodna" in number_part:
        number = number_part.replace("prethodna", "prethodna-")
    elif "p" in number_part:
        number = number_part.replace("p", "-")


    return f"yu1Parl_{date}_{session_type}_{number}"


def rename_files(source, destination, corpus):
    print(f"Renaming {corpus} files in directory:", source)

    for file in os.listdir(source):
        # Skip non-PDF and non-PNG files
        if not  file.lower().endswith((".pdf", ".png")):
            continue

        file_extension = file.split('.')[-1]
        path = os.path.join(source, file)

        new_file_name, new_path = "", ""
        if corpus == 'dzk':
            try:
                new_file_name = generate_dzk_file(file[:-4])  # Remove .pdf extension for processing
            except ValueError as e:
                print(f"Error occurred while renaming file '{file}':", e)
                continue

            try:
                new_path = os.path.join(destination, f"{new_file_name}.{file_extension}")
                shutil.copy(path, new_path)
            except Exception as e:
                print(f"Error occurred while copying file '{file}' to '{new_path}':", e)
                continue

        elif corpus == 'yuparl':
            try:
                new_file_name = generate_yuparl_file(file[:-4])  # Remove extension for processing
            except ValueError as e:
                print(f"Error occurred while renaming file '{file}':", e)
                continue

            try:
                new_path = os.path.join(destination, f"{new_file_name}.{file_extension}")
                shutil.copy(path, new_path)
            except Exception as e:
                print(f"Error occurred while copying file '{file}' to '{new_path}':", e)
                continue

        else:
            raise NotImplementedError(f"Renaming for corpus '{corpus}' is not implemented.")

        print(f"Renamed '{file}' to '{new_file_name}.{file_extension}'")

def main():
    parser = argparse.ArgumentParser(
        prog='ParlaVis Data Preparation Tool',
        description='This program is used to prepare PDF and thumbnail data for ParlaVis.'
    )

    # Adding flags
    parser.add_argument(
        '-c', '--corpus',
        type=str,
        required=True,
        help='Corpus to prepare (e.g., dzk, yuparl, ...)',
        default='dzk',
        choices=['dzk', 'yuparl']  # Add other corpora here
    )

    parser.add_argument(
        '-s', '--source',
        type=str,
        required=True,
        help='Source directory containing raw data'
    )

    parser.add_argument(
        '-d', '--destination',
        type=str,
        required=True,
        help='Destination directory for prepared data'
    )

    parser.add_argument(
        '-p', '--process',
        type=str,
        required=True,
        help='Process to perform (e.g., rename, thumbnail)',
        choices=['rename', 'thumbnail']
    )

    args = parser.parse_args()

    # Add other processes as needed
    switcher = {
        'rename': rename_files,
        'thumbnail': create_thumbnails
    }

    # Execute the selected process
    switcher.get(args.process)(args.source, args.destination, args.corpus)


if __name__ == '__main__':
    main()