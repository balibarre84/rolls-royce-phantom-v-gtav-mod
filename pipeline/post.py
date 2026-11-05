# Post-traitement de l'export Sollumz (CodeWalker XML) : brillance de TOUTES les peintures (vehicle_paint1),
# distances/drapeaux de LOD du drawable (comme le pack de référence : 9998 / 3) et texture de vitre DXT5.
# Usage : python post.py <dossier contenant phantomv.yft.xml et phantomv.ytd.xml>
import re, sys
D = sys.argv[-1].rstrip('/') + '/'
p = D + 'phantomv.yft.xml'; s = open(p, encoding='utf-8').read()
def setv(b, name, x): return re.sub(r'(<Item name="%s" type="Vector" x=")[^"]*"' % name, r'\g<1>%s"' % x, b)
def paint(m):
    b = m.group(0)
    for k, v in (('specularIntensityMult', '0.9'), ('specMapIntMask', '0.0'), ('reflectivePower', '1.0'), ('specularFalloffMult', '250.0')): b = setv(b, k, v)
    return b
s, n = re.subn(r'<Name>vehicle_paint1</Name>.*?</Parameters>', paint, s, flags=re.S); print('shaders de peinture :', n)
for k, v in (('LodDistHigh', 9998), ('LodDistMed', 9998), ('LodDistLow', 9998), ('LodDistVlow', 9998), ('FlagsHigh', 3), ('FlagsMed', 3), ('FlagsLow', 3), ('FlagsVlow', 3)):
    s, c = re.subn(r'(<%s value=")[^"]*(")' % k, r'\g<1>%s\2' % v, s, count=1); assert c == 1, k
open(p, 'w', encoding='utf-8').write(s)
p = D + 'phantomv.ytd.xml'; t = open(p).read(); a = t.find('phantom_glass_d'); b = t.find('D3DFMT_DXT1', a)
if b > 0: t = t[:b] + 'D3DFMT_DXT5' + t[b + 11:]; open(p, 'w').write(t)
# textures de chrome du pack citroends23 (stageV) : entrées ajoutées au dictionnaire de textures si absentes
KROM = {'krom2': (256, 256, 7, 'X32, X64, X128, UNK24'), 'krom2_s': (256, 256, 7, 'X32, X64, X128, UNK24')}
t = open(p).read()
for n, (w, h, m, uf) in KROM.items():
    if '<Name>%s</Name>' % n not in t:
        e = (' <Item>\n  <Name>%s</Name>\n  <Unk32 value="128" />\n  <Usage>DEFAULT</Usage>\n  <UsageFlags>%s</UsageFlags>\n  <ExtraFlags value="0" />\n'
             '  <Width value="%d" />\n  <Height value="%d" />\n  <MipLevels value="%d" />\n  <Format>D3DFMT_DXT1</Format>\n  <FileName>%s.dds</FileName>\n </Item>\n') % (n, uf, w, h, m, n)
        t = t.replace('</TextureDictionary>', e + '</TextureDictionary>')
open(p, 'w').write(t)
