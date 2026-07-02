#!/usr/bin/env python3
import argparse
import os
import sys
import base64
import subprocess
from pathlib import Path

html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Crop Icons</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.5.13/cropper.min.css" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.5.13/cropper.min.js"></script>
    <style>
        body { background: #222; color: white; font-family: sans-serif; text-align: center; }
        .container { max-width: 90%; margin: 20px auto; height: 60vh; }
        img { max-width: 100%; max-height: 100%; }
        button { padding: 10px 20px; font-size: 16px; margin: 10px; cursor: pointer; background: #4caf50; color: white; border: none; border-radius: 4px; }
        button:hover { background: #45a049; }
        select { padding: 10px; font-size: 16px; margin: 10px; }
    </style>
</head>
<body>
    <h2>Crop your icons precisely</h2>
    <p>Select the icon you are cropping from the dropdown, then click Download Precise Crop.</p>
    <select id="iconSelect">
        {options}
    </select>
    <div class="container">
        <img id="image" src="data:image/{ext};base64,{b64_image}" crossorigin="anonymous">
    </div>
    <button onclick="downloadCrop()">Download Precise Crop</button>
    
    <script>
        const image = document.getElementById('image');
        const select = document.getElementById('iconSelect');
        let cropper;

        function initCropper() {
            if (cropper) { cropper.destroy(); }
            cropper = new Cropper(image, {
                viewMode: 1,
                dragMode: 'crop',
                autoCropArea: 0.1,
                restore: false,
                guides: true,
                center: true,
                highlight: false,
                cropBoxMovable: true,
                cropBoxResizable: true,
                toggleDragModeOnDblclick: false,
            });
        }

        function downloadCrop() {
            const canvas = cropper.getCroppedCanvas();
            const dataURL = canvas.toDataURL('image/png');
            const name = select.value;
            
            const a = document.createElement('a');
            a.href = dataURL;
            a.download = name + '_precise.png';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        }

        image.onload = initCropper;
    </script>
</body>
</html>
"""

def generate_cropper(image_path, icons):
    if not os.path.exists(image_path):
        print(f"Error: Image {image_path} not found.")
        sys.exit(1)
        
    ext = image_path.split('.')[-1].lower()
    if ext == 'jpg': ext = 'jpeg'
    
    try:
        with open(image_path, "rb") as f:
            b64_image = base64.b64encode(f.read()).decode('utf-8')
    except Exception as e:
        print(f"Error reading image: {e}")
        sys.exit(1)
        
    options = "\\n".join([f'<option value="{icon}">{icon}</option>' for icon in icons])
    
    html = html_template.replace('{options}', options).replace('{ext}', ext).replace('{b64_image}', b64_image)
    
    out_path = "crop.html"
    with open(out_path, "w") as f:
        f.write(html)
        
    print(f"✅ Generated {out_path} successfully!")
    print(f"Please open {os.path.abspath(out_path)} in your browser, crop each icon, and download them.")

def trace_icons(png_files):
    try:
        from PIL import Image, ImageFilter, ImageOps
    except ImportError:
        print("Error: Pillow is required. Please 'pip install Pillow'")
        sys.exit(1)
        
    for png in png_files:
        if not os.path.exists(png):
            print(f"Warning: {png} not found, skipping.")
            continue
            
        try:
            name = os.path.basename(png).replace('_precise.png', '').replace('.png', '')
            img = Image.open(png).convert("L")
            
            # INITIAL THRESHOLD:
            # We use 150 because typical screenshot backgrounds are white (255)
            # and dark UI elements are near black (<100). 150 safely separates them
            # while resisting mild anti-aliasing artifacts.
            img_bw = img.point(lambda x: 0 if x < 150 else 255, '1')
            
            # UPSCALE:
            # Upscale 5x to give the blur step sub-pixel precision.
            # This drastically smooths out jagged pixel edges.
            cw, ch = img_bw.size
            img_bw = img_bw.resize((cw * 5, ch * 5), Image.Resampling.BICUBIC)
            
            # BLUR:
            # A radius of 5 pixels (at the 5x scale) perfectly smooths the vector curves.
            img_bw = img_bw.convert("L").filter(ImageFilter.GaussianBlur(radius=5))
            
            # FINAL THRESHOLD:
            # We use 128 (the exact midpoint of 0-255 grayscale) to re-harden 
            # the edges after blurring, effectively rounding the geometry.
            img_bw = img_bw.point(lambda x: 0 if x < 128 else 255, '1')
            
            bmp_path = f"{name}_tmp.bmp"
            svg_path = f"{name}.svg"
            
            img_bw.save(bmp_path)
            
            # Run potrace
            subprocess.run(["potrace", "-s", "-a", "1.5", "-O", "1.0", bmp_path, "-o", svg_path], check=True)
            
            # Clean up
            if os.path.exists(bmp_path):
                os.remove(bmp_path)
                
            print(f"✅ Successfully traced {png} -> {svg_path}")
            
        except Exception as e:
            print(f"Error processing {png}: {e}")

def main():
    parser = argparse.ArgumentParser(description="SVG Icon Generator Skill Tools")
    subparsers = parser.add_subparsers(dest="command", help="Subcommand to run")
    
    # generate-cropper
    parser_crop = subparsers.add_parser("generate-cropper", help="Generate HTML cropper for an image")
    parser_crop.add_argument("image_path", help="Path to the reference image")
    parser_crop.add_argument("icons", nargs="+", help="List of icon names to extract")
    
    # trace
    parser_trace = subparsers.add_parser("trace", help="Trace cropped PNGs into SVGs")
    parser_trace.add_argument("png_files", nargs="+", help="List of downloaded PNG files to trace")
    
    args = parser.parse_args()
    
    if args.command == "generate-cropper":
        generate_cropper(args.image_path, args.icons)
    elif args.command == "trace":
        trace_icons(args.png_files)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
