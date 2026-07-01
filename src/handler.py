import os, boto3, urllib.parse, struct, zlib

s3 = boto3.client('s3')
DEST_BUCKET_NAME = os.environ.get('DEST_BUCKET_NAME')

def lambda_handler(event, context):
    for record in event['Records']:
        source_bucket = record['s3']['bucket']['name']
        source_key = urllib.parse.unquote_plus(record['s3']['object']['key'])
        download_path = f'/tmp/{os.path.basename(source_key)}'
        s3.download_file(source_bucket, source_key, download_path)
        file_name, _ = os.path.splitext(source_key)
        dest_key = f"{file_name}.pdf"
        pdf_path = f'/tmp/{os.path.basename(dest_key)}'
        with open(download_path, 'rb') as f:
            img_data = f.read()
        pdf_bytes = image_to_pdf(img_data, source_key)
        with open(pdf_path, 'wb') as f:
            f.write(pdf_bytes)
        s3.upload_file(pdf_path, DEST_BUCKET_NAME, dest_key)
        print(f"PDF cree: {dest_key}")
    return {'statusCode': 200, 'body': 'Success'}

def image_to_pdf(img_data, filename):
    ext = os.path.splitext(filename)[1].lower()
    if ext in ('.jpg', '.jpeg'):
        return jpeg_to_pdf(img_data)
    elif ext == '.png':
        return png_to_pdf(img_data)
    else:
        return jpeg_to_pdf(img_data)

def jpeg_to_pdf(data):
    w, h = get_jpeg_size(data)
    img_len = len(data)
    objs = []
    objs.append(b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")
    objs.append(b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n")
    objs.append(f"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {w} {h}] /Contents 4 0 R /Resources << /XObject << /Im0 5 0 R >> >> >>\nendobj\n".encode())
    stream = f"q {w} 0 0 {h} 0 0 cm /Im0 Do Q".encode()
    objs.append(f"4 0 obj\n<< /Length {len(stream)} >>\nstream\n".encode() + stream + b"\nendstream\nendobj\n")
    objs.append(f"5 0 obj\n<< /Type /XObject /Subtype /Image /Width {w} /Height {h} /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode /Length {img_len} >>\nstream\n".encode() + data + b"\nendstream\nendobj\n")
    return build_pdf(objs)

def png_to_pdf(data):
    w, h = get_png_size(data)
    raw = extract_png_raw(data, w, h)
    compressed = zlib.compress(raw)
    c_len = len(compressed)
    objs = []
    objs.append(b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")
    objs.append(b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n")
    objs.append(f"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {w} {h}] /Contents 4 0 R /Resources << /XObject << /Im0 5 0 R >> >> >>\nendobj\n".encode())
    stream = f"q {w} 0 0 {h} 0 0 cm /Im0 Do Q".encode()
    objs.append(f"4 0 obj\n<< /Length {len(stream)} >>\nstream\n".encode() + stream + b"\nendstream\nendobj\n")
    objs.append(f"5 0 obj\n<< /Type /XObject /Subtype /Image /Width {w} /Height {h} /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /FlateDecode /Length {c_len} >>\nstream\n".encode() + compressed + b"\nendstream\nendobj\n")
    return build_pdf(objs)

def build_pdf(objs):
    pdf = b"%PDF-1.4\n"
    offsets = []
    for obj in objs:
        offsets.append(len(pdf))
        pdf += obj
    xref_pos = len(pdf)
    pdf += f"xref\n0 {len(objs)+1}\n0000000000 65535 f \n".encode()
    for off in offsets:
        pdf += f"{off:010d} 00000 n \n".encode()
    pdf += f"trailer\n<< /Size {len(objs)+1} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n".encode()
    return pdf

def get_jpeg_size(data):
    i = 2
    while i < len(data):
        if data[i] != 0xFF:
            break
        marker = data[i+1]
        if marker == 0xC0 or marker == 0xC2:
            h = struct.unpack('>H', data[i+5:i+7])[0]
            w = struct.unpack('>H', data[i+7:i+9])[0]
            return w, h
        length = struct.unpack('>H', data[i+2:i+4])[0]
        i += 2 + length
    return 200, 200

def get_png_size(data):
    w = struct.unpack('>I', data[16:20])[0]
    h = struct.unpack('>I', data[20:24])[0]
    return w, h

def extract_png_raw(data, w, h):
    idat = b""
    i = 8
    while i < len(data):
        length = struct.unpack('>I', data[i:i+4])[0]
        chunk_type = data[i+4:i+8]
        if chunk_type == b"IDAT":
            idat += data[i+8:i+8+length]
        i += 12 + length
    raw_with_filter = zlib.decompress(idat)
    stride = w * 3 + 1
    pixels = b""
    for row in range(h):
        start = row * stride
        pixels += raw_with_filter[start+1:start+stride]
    return pixels
