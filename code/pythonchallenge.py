#puzzle 0
print(2**38)

encrypted= """g fmnc wms bgblr rpylqjyrc gr zw fylb.
rfyrq ufyr amknsrcpq ypc dmp. bmgle gr gl zw fylb gq glcddgagclr ylb rfyrq ufw rfgq rcvr gq qm jmle.
sqgle qrpgle.kyicrpylq() gq pcamkkclbcb. lmu ynnjw ml rfc spj."""

for c in encrypted:
    if 'a' <= c <= 'z':
        print(chr((ord(c) - ord('a') + 2) % 26 + ord('a')), end='')
    else:
        print(c, end='')
