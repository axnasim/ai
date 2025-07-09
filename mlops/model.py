import pickle 
import sklearn

class Model(object):

    def __init__(self):
        print("Initialising")
        with open('model.pkl', "rb") as f:
            self.model = pickle.load(f)

    def predict(self,X,features_names):
        print("Predict called")
        return self.model.predict(X)