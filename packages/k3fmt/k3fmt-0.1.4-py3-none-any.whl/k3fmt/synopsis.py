import k3fmt

lines = [
    "hello",
    "world",
]

# add left padding to each line in a string
k3fmt.line_pad("\n".join(lines), " " * 4)
# "    hello"
# "    world"


# format a multi-row line
items = [
    "name:",
    ["John", "j is my nick"],
    "age:",
    26,
    "experience:",
    ["2000 THU", "2006 sina", "2010 other"],
]

k3fmt.format_line(items, sep=" | ", aligns="llllll")
# outputs:
#    name: | John         | age: | 26 | experience: | 2000 THU
#          | j is my nick |      |    |             | 2006 sina
#          |              |      |    |             | 2010 other


# ['ab']
print(k3fmt.tokenize("ab"))
# ['a', 'b']
print(k3fmt.tokenize("a b"))
# ['a', 'b']
print(k3fmt.tokenize(" a  b "))
# ['a', 'b']
print(k3fmt.tokenize(" a\t b\n c\r "))
# ['a b', 'c d']
print(k3fmt.tokenize("a bxyc d", sep="xy"))
# ['a', 'x x', 'b']
print(k3fmt.tokenize('a "x x" b'))
# ['a', 'x x', 'b']
print(k3fmt.tokenize("a 'x x' b 'x"))  # the last `'x` has no pair, discard
# ['a', 'a b', 'c d']
print(k3fmt.tokenize(" a  xa bx yc dy ", quote="xy"))
# ['a', 'xa bx', 'yc dy']
print(k3fmt.tokenize("a xa bx yc dy", quote="xy", preserve=True))
# ['', 'a', 'xa bx', 'yc dy', '']
print(k3fmt.tokenize(" a xa bx yc dy ", sep=" ", quote="xy", preserve=True))
