from abc import ABC, abstractmethod, abstractproperty
from typing import Set, List, Type
import csv
import math


class Context:

    def __init__(self, paramList: 'ParamList'):
        self._objs = set()
        self._paramList = paramList

    def addObject(self, obj: 'AObject'):
        if self._paramList.compatible(obj.dash()):
            self._objs.add(obj)
        else:
            raise NonCompatibleParamsException("Trying to add an object to a context with incompatible parameter set.")

    def dash(self, params: 'ParamList') -> List['AObject']:
        rez = []
        for obj in self._objs:
            if params.includes(obj.dash()):
                rez.append(obj)
        return rez

    def getObjects(self) -> Set['AObject']:
        return self._objs


class AObject(ABC):

    @abstractmethod
    def dash(self) -> 'ParamList':
        pass


class Object(AObject):

    def dash(self) -> 'ParamList':
        return self.params

    def __init__(self, params: List['AParam'], label='noLabel'):
        self.params = ParamList(params)
        self.label = label

    def __str__(self):
        return self.label


class ExtendedParamListObject(Object):
    def __init__(self, params: List['AParam'], label='noLabel'):
        self.params = ExtendedParamList(params)
        self.label = label


class AParam(ABC):

    @classmethod
    @abstractmethod
    def instantiate(cls,value) -> 'AParam':
        pass

    # @abstractmethod
    # def compatible(self, second: 'AParam') -> bool:
    #     pass
    def compatible(self, second: 'AParam') -> bool:
        return type(second) == type(self)

    def intersect(self, second: 'AParam') -> 'AParam':
        if not second.compatible(self):
            raise NonCompatibleParamsException("Params not compatible",self, second)
        return self._doIntersect(second)

    @abstractmethod
    def _doIntersect(self, second: 'AParam') -> 'AParam':
        pass
        # raise NotImplemented("_doIntersect implemented but called. " +
        #     "Look at intersect method. Either intersect should be overridden or _doIntesect defined")

    @abstractmethod
    def weight(self) -> float:
        """Насколько признак интересен. Так, очень широкие признаки реально не так важны"""
        pass

    @abstractmethod
    def includes(self, param: 'AParam') -> bool:
        """Реально понадобится для проверки"""
        pass


class ParamList(AParam):
    """"Composite for AParam"""

    @staticmethod
    def instantiate(value) -> 'AParam':
        pass

    def __init__(self, params: List['AParam']):
        super(ParamList, self).__init__()
        self.params = params

    # def add(self, param: 'AParam'):
    #     self.params.__add__(param)

    def compatible(self, second: 'ParamList'):
        if self.params.__len__() != second.params.__len__():
            return False
        for ind, val in enumerate(self.params):
            if not second.params[ind].compatible(val):
                return False
        return True

    def intersect(self, second: 'ParamList') -> 'ParamList':
        rez = []
        for ind, val in enumerate(self.params):
            rez.append(second.params[ind].intersect(val))
        return self.newInstance(rez)

    def newInstance(self,params):
        k = self.__class__
        return k(params)

    def weight(self) -> float:
        rez = 0
        for ind, val in enumerate(self.params):
            rez += val.weight()
        return rez

    def includes(self, toTestParam: AParam):
        if not isinstance(toTestParam, ParamList):
            raise TypeError("A scalar param given to be compared with a vector one")
        for ind, param in enumerate(self.params):
            if not param.includes(toTestParam.params[ind]):
                return False
        return True

    def _doIntersect(self, second: 'AParam'):
        pass


class ExtendedParamList(ParamList):
    def includes(self, toTestParam: AParam):
        # print()
        if not isinstance(toTestParam, ParamList):
            raise TypeError("A scalar param given to be compared with a vector one")
        missedCount = 0
        for ind, param in enumerate(self.params):
            if not param.includes(toTestParam.params[ind]):
                missedCount += 1
                # print(ind,end=',')
            if missedCount > 1:
                return False
        return True


class ADataHandler(ABC):

    @abstractmethod
    def __init__(self, dataFilename, config):
        pass

    @abstractmethod
    def getNegativeContext(self) -> Context:
        pass

    @abstractmethod
    def getPositiveContext(self) -> Context:
        pass

    @abstractmethod
    def createObject(self, dataLine) -> AObject:
        pass


class CsvTupleDataHandler(ADataHandler):

    def __init__(self, dataFilename, config: tuple, ObjectClass = Object):
        self.config = config
        self._objClass = ObjectClass
        with open(dataFilename, 'r') as f:
            reader = csv.reader(f)
            self._rawDataList = list(reader)
        mainParamSet = self.createObject(['__head' for x in range(0, config.__len__())]).dash()
        self._posCont = Context(mainParamSet)
        self._negCont = Context(mainParamSet)
        for dataLine in self._rawDataList:
            target = dataLine.pop()
            obj = self.createObject(dataLine)
            if target == '1':
                self._posCont.addObject(obj)
            elif target == '0':
                self._negCont.addObject(obj)

    def createObject(self, dataLine) -> 'AObject':
        params = []
        for ind, value in enumerate(dataLine):
            className = getattr(paramClasses, self.config[ind])
            params.append(className.instantiate(value))
        return self._objClass(params)

    def getPositiveContext(self) -> Context:
        return self._posCont

    def getNegativeContext(self) -> Context:
        return self._negCont

class LazyFCAException (Exception):
    pass


class NonCompatibleParamsException(LazyFCAException):
    pass


class AClassifier(ABC):

    def __init__(self, data: ADataHandler):
        self._data = data

    @abstractmethod
    def classify(self, obj: AObject) -> bool:
        pass


class ALinearClassifier(AClassifier):

    @abstractmethod
    def calculate(self, obj: AObject) -> float:
        pass

    def __init__(self, data: ADataHandler, edgeParameter: float):
        AClassifier.__init__(self, data)
        self._edge = edgeParameter

    def classify(self, obj: AObject):
        return self.calculate(obj) >= self._edge


class WeightedGeneratorClassifier(ALinearClassifier):

    def __init__(self, data: ADataHandler, edgeParameter: float):
        AClassifier.__init__(self, data)
        self._edge = edgeParameter

    def calculate(self, testObj: AObject) -> float:
        pos = self._data.getPositiveContext()
        neg = self._data.getNegativeContext()
        val = 0.0
        sp = pos.getObjects().__len__()
        sn = neg.getObjects().__len__()
        for obj in pos.getObjects():
            paramToTest = obj.dash().intersect(testObj.dash())
            if neg.dash(paramToTest).__len__() == 0:
                val += pos.dash(paramToTest).__len__() * self.getWeight(paramToTest) / sp
        for obj in neg.getObjects():
            paramToTest = obj.dash().intersect(testObj.dash())
            if pos.dash(paramToTest).__len__() == 0:
                val -= neg.dash(paramToTest).__len__() * self.getWeight(paramToTest) / sn
        return val

    def getWeight(self, params: 'AParamList'):
        return params.weight()


class EdgedGeneratorClassifier(ALinearClassifier):

    def __init__(self, data: ADataHandler, edgeParameter: float):
        AClassifier.__init__(self, data)
        self._edge = edgeParameter

    def calculate(self, testObj: AObject) -> float:
        pos = self._data.getPositiveContext()
        neg = self._data.getNegativeContext()
        val = 0.0
        sp = pos.getObjects().__len__()
        sn = neg.getObjects().__len__()
        for obj in pos.getObjects():
            paramToTest = obj.dash().intersect(testObj.dash())
            support = pos.dash(paramToTest).__len__()
            # if support > 2:
            #     print(support)
            support = support / sp
            if support > self._edge:
                val += 1 / sp
        for obj in neg.getObjects():
            paramToTest = obj.dash().intersect(testObj.dash())
            support = neg.dash(paramToTest).__len__() / sn
            if support > self._edge:
                val -= 1 / sn
        return val

    def getWeight(self, param: AParam) -> float:
        return param.weight()

    def classify(self, obj: AObject):
        return self.calculate(obj) >= 0


class GeneratorClassifier(WeightedGeneratorClassifier):

    def getWeight(self, param: AParam):
        return 1


class FullClassifier(ALinearClassifier):

    def calculate(self, testObj: AObject) -> float:
        pos = self._data.getPositiveContext()
        neg = self._data.getNegativeContext()
        val = 0.0
        sp = pos.getObjects().__len__()
        sn = neg.getObjects().__len__()
        for obj in pos.getObjects().union(neg.getObjects()):
            paramToTest = obj.dash().intersect(testObj.dash())
            pd = pos.dash(paramToTest)
            val += (pos.dash(paramToTest).__len__()/sp - neg.dash(paramToTest).__len__()/sn)
        return val


# class DetailedObjectsClassifier(ALinearClassifier):
#
#     def calculate(self, obj: AObject):
#         pos = self._data.getPositiveContext()
#         neg = self._data.getNegativeContext()
#         val = 0.0
#         sp = pos.getObjects().__len__()
#         sn = neg.getObjects().__len__()
#         for obj in pos.getObjects().union(neg.getObjects()):
#             paramToTest = obj.dash().intersect(testObj.dash())
#             val += (pos.dash(paramToTest).__len__() / sp - neg.dash(paramToTest).__len__() / sn) * paramToTest.weight()
#         return val


class QuantileClassifier(AClassifier):

    def __init__(self, data: ADataHandler, limitLower, limitUpper):
        super().__init__(data)
        self._limitUpper = limitUpper
        self._limitLower = limitLower

    def classify(self, obj: AObject) -> bool:
        pos = self._data.getPositiveContext()
        neg = self._data.getNegativeContext()
        objParams = obj.dash()
        saveSim = []
        posLen = pos.getObjects().__len__()
        negLen = neg.getObjects().__len__()
        for posObj in pos.getObjects():
              # degree of similarity
            saveSim.append((objParams.intersect(posObj.dash()).weight(), posObj, 1/posLen))
        for negObj in neg.getObjects():
            saveSim.append((objParams.intersect(negObj.dash()).weight(), negObj, -1/negLen))
        saveSim.sort(key = lambda tup: tup[0])
        len = saveSim.__len__()
        votes = 0.0
        for tup in saveSim[math.floor(len*self._limitLower):math.ceil(len*self._limitUpper)]:
            votes += tup[2]
        return votes > 0.0



class paramClasses:

    class DiscreteParam(AParam):

        @classmethod
        def instantiate(cls,value) -> 'AParam':
            if value == '__head':
                return cls([])
            return cls([value])

        def __init__(self, vals):
            self._vals = set(vals)

        def includes(self, param: AParam) -> bool:
            return self._vals.intersection(param._vals) == param._vals

        def weight(self) -> float:
            if self._vals.__len__() > 1:
                return 0
            return 1

        def _doIntersect(self, second: 'paramClasses.DiscreteParam'):
            return paramClasses.DiscreteParam(self._vals.union(second._vals))

    class BinaryDiscreteParam(AParam):

        def weight(self) -> float:
            return float(self._empty)

        def _doIntersect(self, second: 'AParam') -> 'AParam':
            if self._val == second._val:
                return paramClasses.BinaryDiscreteParam(self._val)
            else:
                return paramClasses.BinaryDiscreteParam()

        @classmethod
        def instantiate(cls, value) -> 'AParam':
            if value == "__head":
                value = False
            return cls(value)

        def __init__(self, val = False):
            self._val = val
            self._empty = not bool(val)

        def includes(self, param: 'AParam'):
            return param._val != self._val or self._empty

    class RealParam(AParam):

        def weight(self) -> float:
            return 1.0/(self._upper - self._lower + 1)

        def _doIntersect(self, second: 'AParam') -> 'AParam':
            return paramClasses.RealParam(min(self._lower, second._lower),max(self._upper, second._upper))

        @classmethod
        def instantiate(cls, value) -> 'AParam':
            if value == "__head":
                value = 0.0
            else:
                value = float(value)
            return cls(value,value)

        def __init__(self, lower, upper):
            self._lower = lower
            self._upper = upper

        def includes(self, param: 'AParam'):
            return (self._lower <= param._lower) and (self._upper >= param._upper)


