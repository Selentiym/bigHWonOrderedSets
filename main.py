from bondartsev_nikita.classes import *
import csv

config = []
config.append("BinaryDiscreteParam")
config.append("BinaryDiscreteParam")
config.append("BinaryDiscreteParam")
config.append("RealParam")
config.append("RealParam")
config.append("RealParam")
config.append("RealParam")
config.append("BinaryDiscreteParam")
config.append("RealParam")
config.append("RealParam")
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
train = CsvTupleDataHandler("data2/test"+str(normalizeNumber(i-1))+".csv", config)

classifier = EdgedGeneratorClassifier(train, 0.4)

test = CsvTupleDataHandler("data2/test"+str(normalizeNumber(i))+".csv", config)
tp = tn = fn = fp = 0
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
accuracy = (tp + tn) / (fp + fn + tp + tn)
recall = 0.0
print(tp, tn, fp, fn, accuracy, recall)
exit()

results = dict()

for j in range(0,5):
    tp = 0
    tn = 0
    fp = 0
    fn = 0
    edgeParam = float(j) / 50
    print("edge: " + str(edgeParam))
    for i in range(0, 9):
        print (i)
        train = CsvTupleDataHandler("data/test"+str(normalizeNumber(i))+".csv", config)

        # classifier = FullClassifier(train, 3.9)
        classifier = WeightedGeneratorClassifier(train, edgeParam)

        test = CsvTupleDataHandler("data/test"+str(normalizeNumber(i+1))+".csv", config)

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
    recall = tp / ( tp + fp )
    results[edgeParam] = (tp,tn,fp,fn, accuracy, recall)
print(results)
