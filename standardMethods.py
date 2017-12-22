from sklearn import tree
import numpy as np

def normalizeNumber(num):
    return (num % 8) + 1

dataHandlers = dict()
for j in range(0,8):
    i = normalizeNumber(j)
    dataHandlers[i] = np.loadtxt('diabetes/test'+str(i)+'.csv',delimiter=',')

for j in range(1,50):
    minLeaf = j / 100
    tp = tn = fp = fn = 0
    for i in range(0,8):

        data = dataHandlers[normalizeNumber(i)]

        target = data[:, -1]

        predictors = data[:,0:-1]
        data = dataHandlers[normalizeNumber(i+1)]

        classifier = tree.DecisionTreeClassifier(min_weight_fraction_leaf=minLeaf)
        classifier.fit(predictors, target)

        for dataPoint in list(data):
            trg = dataPoint[-1]
            toTest = [dataPoint[0:-1]]
            predicted = classifier.predict(toTest)
            if trg ==1:
                if predicted == 1:
                    tp += 1
                else:
                    fn += 1
            else:
                if predicted == 1:
                    fp += 1
                else:
                    tn += 1
    accuracy = (tp + tn) / (tp + tn + fp + fn)
    print(minLeaf,tp,tn,fp,fn,accuracy)
