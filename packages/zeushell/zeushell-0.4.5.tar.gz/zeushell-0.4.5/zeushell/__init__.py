def start():
    qqqqqqq=open("w.txt","w")
    qqqqqqq.write("[]")
    qqqqqqq.close()
def name(a):
    global shellname
    shellname=a
def function():
    import ast
    def dd(func):
        try:
            qqqqqqq=open("w.txt","r")
            funclist=ast.literal_eval(qqqqqqq.read())
            qqqqqqq.close()
        except:
            funclist=[]
        funclist.append(func.__name__)
        qqqqqqq=open("w.txt","w")
        qqqqqqq.write(str(funclist))
        qqqqqqq.close()
        return func
    return dd
def run():
    import ast
    try:
        shellname+=": "
    except:
        shellname="Zeushell: "
    while True:
        ino=input(shellname)
        s=ino.split()
        njdo=[]
        for i in s:
          try:
            siu=int(i)
            njdo.append(siu)
          except:
              njdo.append(i)
        s=njdo      
        if s==[]:
            continue
        aaaaa=s[0]
        qqqqqqq=open("w.txt","r")
        wigeiu=qqqqqqq.read()
        qqqqqqq.close()
        if aaaaa not in ast.literal_eval(wigeiu):
            print('You didn\'t have '+aaaaa+' function') 
            continue
        try:
          s=s[1:]
        except:
          s=[]
        s=ast.literal_eval(str(s).replace("[","(").replace("]",")"))
        kwargs = {}
        globals()[func_name](*s,**kwargs)
    return 1