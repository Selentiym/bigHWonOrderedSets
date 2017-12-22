from bondartsev_nikita.classes import *
import csv

config = []
config.append("RealParam")
config.append("RealParam")
config.append("RealParam")
config.append("RealParam")
config.append("RealParam")
config.append("RealParam")
config.append("RealParam")
config.append("RealParam")
# for j in range(0, 9):
#     config.append("DiscreteParam")
config = tuple(config)

def normalizeNumber(num):
    return num % 8 + 1

i=1
# train = CsvTupleDataHandler("diabetes/test"+str(normalizeNumber(i-1))+".csv", config,ExtendedParamListObject)
#
# classifier = EdgedGeneratorClassifier(train, 0.05)
#
# test = CsvTupleDataHandler("diabetes/test"+str(normalizeNumber(i))+".csv", config,ExtendedParamListObject)
# tp = tn = fn = fp = 0
# print(test.getNegativeContext().getObjects().__len__())
# for obj in test.getNegativeContext().getObjects():
#     if classifier.classify(obj):
#         tp += 1
#     else:
#         fn += 1
#     # results[0][int(classifier.classify(obj))] += 1
# for obj in test.getPositiveContext().getObjects():
#     if classifier.classify(obj):
#         fp += 1
#     else:
#         tn += 1
# accuracy = (tp + tn) / (fp + fn + tp + tn)
# recall = 0.0
# print(tp, tn, fp, fn, accuracy, recall)
# exit()
dataHandlers = dict()
for j in range(0,8):
    i = normalizeNumber(j)
    dataHandlers[i] = CsvTupleDataHandler("diabetes/test"+str(i)+".csv", config, ExtendedParamListObject)

results = dict()

for j in range(3,20):
    tp = 0
    tn = 0
    fp = 0
    fn = 0
    edgeParam = float(j) / 150
    print("edge: " + str(edgeParam))
    for i in range(0, 8):
        print (i)
        train = dataHandlers[normalizeNumber(i)]

        # classifier = FullClassifier(train, 3.9)
        classifier = EdgedGeneratorClassifier(train, edgeParam)

        test = dataHandlers[normalizeNumber(i+1)]

        for obj in test.getNegativeContext().getObjects():
            if classifier.classify(obj):
                tp += 1
            else:
                fn += 1
            # results[0][int(classifier.classify(obj))] += 1
        for obj in test.getPositiveContext().getObjects():
            if classifier.classify(obj):
                fp += 1
            else:
                tn += 1
            # results[1][int(classifier.classify(obj))] += 1
    accuracy = (tp + tn) / ( fp + fn + tp + tn)
    # recall = tp / ( tp + fp )
    recall = 0.0
    results[edgeParam] = (tp,tn,fp,fn, accuracy, recall)
print(results)
