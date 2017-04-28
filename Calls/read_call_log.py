'''
read call log calls
'''
import datetime
import re
import csv
from sklearn import svm
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.model_selection import train_test_split

MISSED = 'Missed'
MISSED_O = 'Missed-O'
INCOMING = 'Incoming'

MISSED_CL = 3
MISSED_O_CL = 2
INCOMING_CL = 1

class calls_log_parser:
    class Call:
        def __init__(self, number, duration, c_type, time, contact_id=None):
            self._number = number
            self._duration = duration #should be int
            self._type = c_type
            self._time = time
            self._contact_id = contact_id
            self.vec = []
            # self.parse_time_str(time)


        def get_type(self):
            return self._type

        def get_number(self):
            return self._number

        def get_name(self):
            return self._contact_id

        def get_time(self):
            return self._time

        def set_type(self,c_type):
            self._type = c_type

        def __str__(self):
            return "number: " + str(self._number) + ", contact: " + str(self._contact_id) + ", duration: " + str(self._duration)\
                   + ", type: " + str(self._type) + ", time: " + str(self._time)

        def get_vec(self):
            self.vec = [self._number]
            if self._contact_id == 'UNKNOWN':
                self.vec.append(0)
            else:
                self.vec.append(1)
            self.vec.append(self._time.weekday())
            h = (self._time - self._time.replace(hour=0, minute=0, second=0)).seconds / 3600
            self.vec.append(h)



    #####################################################################################################################

    def __init__(self, file_name):
        self.calls_file = open(file_name, 'r')
        self.file_reader = csv.reader(self.calls_file)
        self.calls = []
        self.parse_calls()

    def add_call(self, call):
        self.calls.append(call)

    def get_calls(self):
        return self.calls

    def parse_calls(self):
        for row in self.file_reader:
            if re.match(r'\s*Call History Manager\s*',row[0]):
                continue
            if re.match(r'\s*SI No\s*',row[0]):
                continue

            call_type = row[4]
            call_time = datetime.datetime.strptime(row[5],'%m/%d/%Y %H:%M')
            last_call = None
            if len(self.calls) == 0:
                last_call = None
            else:
                last_call = self.calls[-1]

            if call_type == 'Outgoing':
                if last_call and last_call.get_type() == MISSED:
                    if (call_time - last_call.get_time()).seconds/60 > 10:
                        last_call.set_type(MISSED_O)
                continue

            call_number = row[3]
            call_duration = row[6]
            call_contact_id = row[1]
            call = self.Call(call_number,call_duration,call_type,call_time,call_contact_id)

            self.add_call(call)
        return

    def create_phone_dict(self):
        phone_dict = dict()
        i = 0
        for c in self.calls:
            if c.get_number() in phone_dict.keys():
                continue
            else:
                i += 1
                phone_dict[c.get_number()] = i
        return phone_dict

    def create_name_dict(self):
        name_dict = dict()
        i = 0
        for c in self.calls:
            if c.get_name in name_dict.keys():
                continue
            else:
                name_dict[c.get_name()] = i+1
        return name_dict

    def __str__(self):
        calls_str = ""
        for call in self.calls:
            calls_str = calls_str + str(call) + '\n'
        return calls_str

    def batch_learn(self,batch):
        p_dict = self.create_phone_dict()
        Y = []
        X = []
        # x_m = []
        for i in range(len(batch)):
            batch[i].get_vec()
            batch[i].vec[0] = p_dict[batch[i].get_number()]
            X.append(batch[i].vec)
            # x_m.append(batch[i].get_type())
            if batch[i].get_type() == MISSED: Y.append(MISSED_CL)
            elif batch[i].get_type() == MISSED_O:Y.append(MISSED_O_CL)
            else: Y.append(INCOMING_CL)
        X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=10)
        self.clf = svm.SVC(kernel='linear')
        self.clf.fit(X_train, Y_train)
        self.predictions = self.clf.predict(X_test)
        print(accuracy_score(Y_test, self.predictions))
        print(confusion_matrix(Y_test, self.predictions))
        print(classification_report(Y_test, self.predictions))
        return

    def predict(self,vec):
        return self.clf.predict([vec])



