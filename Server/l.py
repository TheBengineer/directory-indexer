__author__ = 'boh01'


def wf(variable):
    f = open("/tmp/data","w")
    lines = 0
    while len(variable):
        folder, fname = variable.pop()
        f.write("\""+folder +"\",\""+fname+"\"")
        lines += 1
        if lines%100000 == 0:
            print lines


def ignore():
    c = compile("""def test():
    print "hi" """, '<String>', 'exec')
    savefile = open("/tmp/data.csv", "w")
    savefile.write(d.files_to_add)
    #$len(d.files_to_add)
    #len(s.directories_to_refresh)
    #def test():; print "hi"