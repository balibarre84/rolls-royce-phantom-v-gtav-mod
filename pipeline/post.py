# Post-traitement de l'export : brillance de la peinture (vehicle_paint1) + texture de vitre DXT5
import re,sys
D='/home/claude/deliver2/'
p=D+'yft_xml/phantomv.yft.xml'; s=open(p,encoding='utf-8').read()
i=s.find('<Name>vehicle_paint1</Name>'); j=s.find('</Item>\n        <Item>',i)
blk=s[i:j]
def setv(b,name,x):
    return re.sub(r'(<Item name="%s" type="Vector" x=")[^"]*"'%name, r'\g<1>%s"'%x, b)
for k,v in (('specularIntensityMult','0.9'),('specMapIntMask','0.0'),('reflectivePower','1.0'),('specularFalloffMult','250.0')): blk=setv(blk,k,v)
s=s[:i]+blk+s[j:]; open(p,'w',encoding='utf-8').write(s)
p=D+'yft_xml/phantomv.ytd.xml'; t=open(p).read(); a=t.find('phantom_glass_d'); b=t.find('D3DFMT_DXT1',a)
if b>0: t=t[:b]+'D3DFMT_DXT5'+t[b+11:]; open(p,'w').write(t)
