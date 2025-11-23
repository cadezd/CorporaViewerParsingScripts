import argparse

import optimizer
import parser_dzk
import parser_yuparl
import renamer
import thumbnailer


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

    parse_parser = subparsers.add_parser('parse', help='Generates JSON file from XML files')
    rename_parser.add_argument(
        '-c', '--corpus',
        type=str,
        required=True,
        help='Corpus to prepare (e.g., dzk, yuparl, ...)',
        choices=['dzk', 'yuparl']  # Add other corpora here
    )
    parse_parser.add_argument(
        '-s', '--source',
        type=str,
        required=True,
        help='Source directory containing XML files'
    )
    parse_parser.add_argument(
        '-d', '--destination',
        type=str,
        required=True,
        help='Destination directory for JSON files'
    )
    parse_parser.add_argument(
        '-f', '--from-index',
        type=int,
        required=False,
        help='Starting index for parsing files',
        default=0
    )
    parse_parser.add_argument(
        '-t', '--to-index',
        type=int,
        required=False,
        help='Ending index for parsing files',
        default=-1
    )


    args = parser.parse_args()

    # Execute the appropriate function based on the subcommand
    match args.command:
        case 'rename':
            renamer.rename_files(args.source, args.destination, args.corpus)
        case 'thumbnail':
            thumbnailer.create_thumbnails(args.source, args.destination)
        case 'optimize':
            optimizer.optimize_pdfs(args.source, args.destination, quality=args.quality, ghostscript_path=rf"{args.ghostscript_path}")
        case 'parse':
            if args.corpus == 'dzk':
                parser_dzk.parse(args.source, args.destination, args.from_index, args.to_index)
            elif args.corpus == 'yuparl':
                parser_yuparl.parse(args.source, args.destination, args.from_index, args.to_index)
            else:
                raise NotImplementedError(f"Parsing for corpus '{args.corpus}' is not implemented.")
        case _:
            raise NotImplementedError(f"Command '{args.command}' is not implemented.")



if __name__ == '__main__':
    main()