import os
import subprocess


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


def optimize_pdfs(input_dir, output_dir, quality="ebook", ghostscript_path='gs'):
    print("Optimizing PDF files in directory:", input_dir)

    for file in os.listdir(input_dir):
        if not file.lower().endswith(".pdf"):
            continue

        path = os.path.join(input_dir, file)

        optimized_file_path = os.path.join(output_dir, file)
        optimize_pdf(path, optimized_file_path, quality=quality, ghostscript_path=ghostscript_path)