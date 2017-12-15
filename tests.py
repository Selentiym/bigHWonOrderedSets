from bondartsev_nikita.classes import *

param1 = paramClasses.RealParam(0.5, 0.5)
param2 = paramClasses.RealParam(0.6, 0.6)
param3 = paramClasses.RealParam(0.55, 0.55)
inter = param1.intersect(param2)
print(inter.includes(param3))

l1 = ParamList([paramClasses.RealParam.instantiate('0.5'),paramClasses.RealParam.instantiate('0.6')])
l2 = ParamList([param1,param2])

print(l2.includes(l1))

param1 = paramClasses.BinaryDiscreteParam.instantiate('a')
param2 = paramClasses.BinaryDiscreteParam.instantiate('b')
inter = param1.intersect(param2)

print(inter.includes(paramClasses.BinaryDiscreteParam.instantiate('c')))