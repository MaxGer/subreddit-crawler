from flask import Flask
from flask_restful import Resource, Api
from analysis import get_analysis
from repeated_timer import RepeatedTimer

app = Flask(__name__)
api = Api(app)
analysis_cache = []

def fetchAnalysis():
    global analysis_cache
    analysis_cache = get_analysis()
    print('updated analysis')

timer = RepeatedTimer(900, fetchAnalysis)
class Analysis(Resource):
    def get(self):
        return analysis_cache, 200

api.add_resource(Analysis, '/analysis')

if __name__ == '__main__':
    fetchAnalysis()
    app.run()
