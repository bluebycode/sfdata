from flask import Flask
app = Flask(__name__)

import services.models
import services.views