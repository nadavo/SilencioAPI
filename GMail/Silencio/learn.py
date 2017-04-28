from sklearn.model_selection import train_test_split, KFold, cross_val_score, cross_val_predict, GridSearchCV
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_blobs


def createMatrix(dataset,from_encode):
    X_matrix = list()
    Y = list()
    for key in dataset.keys():
        row = list()
        for key2 in dataset[key]:
            if key2 == 'notification_priority':
                continue
            elif key2 == 'from':
                value = dataset[key][key2]
                dataset[key][key2] = from_encode[value]
            row.append(dataset[key][key2])
        Y.append(dataset[key]['notification_priority'])
        X_matrix.append(row)
    return X_matrix, Y


def createModel(dataset, from_encode):
    data, labels = createMatrix(dataset, from_encode)
    print(len(data))
    X_train, X_test, Y_train, Y_test = train_test_split(data, labels, test_size=0.2, random_state=10)
    clf = SVC(kernel='linear')
    #clf = RandomForestClassifier(n_estimators=10, max_depth=None, min_samples_split=2, random_state=2, criterion='entropy')
    print(X_train)
    print(X_test)
    print(Y_train)
    print(Y_test)
    clf = clf.fit(X_train, Y_train)
    predictions = clf.predict(X_test)
    #print(clf.decision_path(X_test))
    print(accuracy_score(Y_test, predictions))
    print(confusion_matrix(Y_test, predictions))
    print(classification_report(Y_test, predictions))
    # results = []
    # kfold = KFold(n_splits=10, random_state=2)
    # predictions = cross_val_results(RandomForestClassifier(), X_train, Y_train, cv=kfold)
    # results.append(cv_results)
    # print(results)
    # msg = "%f (%f)" % (cv_results.mean(), cv_results.std())
    # print(msg)
    return clf
