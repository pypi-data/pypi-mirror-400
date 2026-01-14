import os
import urllib.request
import ssl

def download_font(font_name="DejaVuSans.ttf"):
    """
    Downloads a TTF font supporting UTF-8 and Math symbols.
    """
    font_url = "https://raw.githubusercontent.com/senotrusov/dejavu-fonts-ttf/master/ttf/DejaVuSans.ttf"
    
    if not os.path.exists(font_name):
        print(f"[INFO] Downloading font: {font_name}...")
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            
            with urllib.request.urlopen(font_url, context=ctx) as u, open(font_name, 'wb') as f:
                f.write(u.read())
            print("[SUCCESS] Font installed.")
        except Exception as e:
            print(f"[ERROR] Could not download font: {e}")
            return None
    return font_name