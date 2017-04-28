import read_call_log
from sklearn.externals import joblib

test = read_call_log.calls_log_parser("mayCallLog.csv")
# for c in test.get_calls():
#     print(c.get_vec())

batch_s = int(0.9*len(test.get_calls()))
test.batch_learn(test.get_calls()[0:batch_s])
print(test.clf.coef_)

joblib.dump(test.clf.coef_, 'model_coef.dat')

# for c in test.get_calls()[batch_s:]:
#     print(c)
#     print "expected: " + c.get_type() + ", predict: " + str(test.predict(c.get_vec()))


