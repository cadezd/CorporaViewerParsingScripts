import argparse
import re
import shutil

import fitz


import subprocess
import os

def optimize_pdf(input_file, output_file, quality='ebook', ghostscript_path='gs'):
    quality_settings = {
        'screen': '/screen',     # lowest quality
        'ebook': '/ebook',       # good quality
        'printer': '/printer',   # high quality
        'prepress': '/prepress'  # highest quality
    }

    temp_output = output_file + ".tmp.pdf"

    # Ghostscript for compression and font embedding
    gs_command = [
        ghostscript_path,  # Ghostscript command; ensure it's in your PATH
        '-sDEVICE=pdfwrite',
        '-dCompatibilityLevel=1.4',
        f'-dPDFSETTINGS={quality_settings.get(quality, "/ebook")}',
        '-dEmbedAllFonts=false',
        '-dAutoFilterColorImages=false',
        '-dColorImageFilter=/DCTEncode',
        '-dAutoFilterGrayImages=false',
        '-dGrayImageFilter=/DCTEncode',
        '-dMonoImageFilter=/CCITTFaxEncode',
        '-dSubsetFonts=true',
        '-dCompressFonts=true',
        '-dFastWebView=false',
        '-dDetectDuplicateImages=true',
        '-dColorImageDownsampleType=/Bicubic',
        '-dNOPAUSE',
        '-dQUIET',
        '-dBATCH',
        f'-sOutputFile={temp_output}',
        input_file
    ]

    print("🔧 Compressing and embedding fonts...")
    try:
        subprocess.run(gs_command, check=True)
    except subprocess.CalledProcessError as e:
        print("❌ Ghostscript compression failed:", e)
        return

    # qpdf for linearization (fast web view)
    qpdf_command = [
        'qpdf',
        '--linearize',
        temp_output,
        output_file
    ]

    print("📦 Linearizing PDF for fast web view...")
    try:
        subprocess.run(qpdf_command, check=True)
        print(f"✅ Optimization successful: {output_file}")
    except subprocess.CalledProcessError as e:
        print("❌ Linearization failed:", e)
    finally:
        # Clean up temporary file
        if os.path.exists(temp_output):
            os.remove(temp_output)




def optimize_pdfs(input_file, output_file, quality="ebook", ghostscript_path='gs'):
    print("Optimizing PDF files in directory:", input_file)

    for file in os.listdir(input_file):
        if not file.lower().endswith(".pdf"):
            continue

        path = os.path.join(input_file, file)

        optimized_file_path = os.path.join(output_file, file)
        optimize_pdf(path, optimized_file_path, quality=quality, ghostscript_path=ghostscript_path)



def create_thumbnails(source, destination):
    print(f"Creating thumbnails for files in directory:", source)

    for file in os.listdir(source):
        if not file.lower().endswith(".pdf"):
            continue

        path = os.path.join(source, file)

        # get first page of pdf
        pdf_document = fitz.open(path)
        first_page = pdf_document[0]

        # generate thumbnail
        image = first_page.get_pixmap()
        image.save(os.path.join(destination, f"{file[:-4]}.png"))  # Save as PNG, removing .pdf extension

        print(f"✅ Created thumbnail for '{file}'")


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
                print(f"❌ Error occurred while renaming file '{file}':", e)
                continue

            try:
                new_path = os.path.join(destination, f"{new_file_name}.{file_extension}")
                shutil.copy(path, new_path)
            except Exception as e:
                print(f"❌ Error occurred while copying file '{file}' to '{new_path}':", e)
                continue

        elif corpus == 'yuparl':
            try:
                new_file_name = generate_yuparl_file(file[:-4])  # Remove extension for processing
            except ValueError as e:
                print(f"❌ Error occurred while renaming file '{file}':", e)
                continue

            try:
                new_path = os.path.join(destination, f"{new_file_name}.{file_extension}")
                shutil.copy(path, new_path)
            except Exception as e:
                print(f"❌ Error occurred while copying file '{file}' to '{new_path}':", e)
                continue

        else:
            raise NotImplementedError(f"Renaming for corpus '{corpus}' is not implemented.")

        print(f"✅ Renamed '{file}' to '{new_file_name}.{file_extension}'")

def main():
    parser = argparse.ArgumentParser(
        prog='ParlaVis Data Preparation Tool',
        description='This program is used to prepare PDF and thumbnail data for ParlaVis.'
    )

    subparsers = parser.add_subparsers(dest='command', required=True, help='Subcommand to run')

    # -------------------------------
    # Subcommand: rename
    # -------------------------------
    rename_parser = subparsers.add_parser('rename', help='Rename files according to ParlaVis convention')
    rename_parser.add_argument(
        '-c', '--corpus',
        type=str,
        required=True,
        help='Corpus to prepare (e.g., dzk, yuparl, ...)',
        choices=['dzk', 'yuparl']  # Add other corpora here
    )
    rename_parser.add_argument(
        '-s', '--source',
        type=str,
        required=True,
        help='Source directory containing raw data'
    )
    rename_parser.add_argument(
        '-d', '--destination',
        type=str,
        required=True,
        help='Destination directory for renamed data'
    )

    # -------------------------------
    # Subcommand: thumbnail
    # -------------------------------
    thumb_parser = subparsers.add_parser(
        'thumbnail',
        help='Generate thumbnails for the first page of each PDF and save them under the same name with .png extension'
    )
    thumb_parser.add_argument(
        '-s', '--source',
        type=str,
        required=True,
        help='Source directory containing PDF files'
    )
    thumb_parser.add_argument(
        '-d', '--destination',
        type=str,
        required=True,
        help='Destination directory for thumbnails'
    )

    # -------------------------------
    # Subcommand: optimize
    # -------------------------------
    optimize_parser = subparsers.add_parser('optimize', help='Optimize PDF files for web use')
    optimize_parser.add_argument(
        '-s', '--source',
        type=str,
        required=True,
        help='Source directory containing PDF files'
    )
    optimize_parser.add_argument(
        '-d', '--destination',
        type=str,
        required=True,
        help='Destination directory for optimized PDFs'
    )
    optimize_parser.add_argument(
        '-q', '--quality',
        type=str,
        required=False,
        help='Quality of optimized PDFs (screen, ebook, printer, prepress)',
        default='ebook',
        choices=['screen', 'ebook', 'printer', 'prepress']
    )
    optimize_parser.add_argument(
        "-g", "--ghostscript-path",
        type=str,
        required=False,
        help="Path to the Ghostscript executable (if not in system PATH)",
        default="gs"
    )

    args = parser.parse_args()

    # Execute the appropriate function based on the subcommand
    match args.command:
        case 'rename':
            rename_files(args.source, args.destination, args.corpus)
        case 'thumbnail':
            create_thumbnails(args.source, args.destination)
        case 'optimize':
            optimize_pdfs(args.source, args.destination, quality=args.quality, ghostscript_path=rf"{args.ghostscript_path}")
        case _:
            raise NotImplementedError(f"Command '{args.command}' is not implemented.")



if __name__ == '__main__':
    main()