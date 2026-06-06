import re, base64, sys
src = sys.argv[1]
out = sys.argv[2] if len(sys.argv) > 2 else 'decomp/_cap.jpg'
s = open(src, encoding='utf-8', errors='ignore').read()
m = re.search(r'base64,([A-Za-z0-9+/=]+)', s)
if not m:
    print('NO base64 found'); sys.exit(1)
open(out, 'wb').write(base64.b64decode(m.group(1)))
print('wrote', out)
