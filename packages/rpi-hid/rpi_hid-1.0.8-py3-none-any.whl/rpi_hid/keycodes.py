# USB HID Keyboard Scan Codes (US layout)

MOD = {
    "CTRL": 0x01,
    "SHIFT": 0x02,
    "ALT": 0x04,
    "GUI": 0x08
}

SHIFT = 0x02

KEY = {
    # Letters
    'a':4,'b':5,'c':6,'d':7,'e':8,'f':9,'g':10,'h':11,'i':12,'j':13,
    'k':14,'l':15,'m':16,'n':17,'o':18,'p':19,'q':20,'r':21,'s':22,
    't':23,'u':24,'v':25,'w':26,'x':27,'y':28,'z':29,

    # Numbers
    '1':30,'2':31,'3':32,'4':33,'5':34,'6':35,'7':36,'8':37,'9':38,'0':39,

    # Control keys
    'ENTER':40,'ESC':41,'BACKSPACE':42,'TAB':43,' ':44,

    # Punctuation (base)
    '-':45,'=':46,'[':47,']':48,'\\':49,';':51,"'":52,'`':53,
    ',':54,'.':55,'/':56,

    # SHIFT + number row
    '!':(SHIFT,30),
    '@':(SHIFT,31),
    '#':(SHIFT,32),
    '$':(SHIFT,33),
    '%':(SHIFT,34),
    '^':(SHIFT,35),
    '&':(SHIFT,36),
    '*':(SHIFT,37),
    '(':(SHIFT,38),
    ')':(SHIFT,39),

    # SHIFT + punctuation
    '_':(SHIFT,45),
    '+':(SHIFT,46),
    '{':(SHIFT,47),
    '}':(SHIFT,48),
    '|':(SHIFT,49),
    ':':(SHIFT,51),
    '"':(SHIFT,52),
    '~':(SHIFT,53),
    '<':(SHIFT,54),
    '>':(SHIFT,55),
    '?':(SHIFT,56),
}


SHIFTED = {
    '!':('SHIFT','1'),
    '@':('SHIFT','2'),
    '#':('SHIFT','3'),
    '$':('SHIFT','4'),
    '%':('SHIFT','5'),
    '^':('SHIFT','6'),
    '&':('SHIFT','7'),
    '*':('SHIFT','8'),
    '(':('SHIFT','9'),
    ')':('SHIFT','0'),
    ':':('SHIFT',';'),
    '"':('SHIFT',"'"),
    '<':('SHIFT',','),
    '>':('SHIFT','.'),
    '?':('SHIFT','/')
}
