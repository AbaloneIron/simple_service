from flask import Flask, url_for, request, jsonify, make_response
import logging, os, subprocess, re, json
app = Flask(__name__)

version = "v0.4 20180510"

logging.basicConfig(filename="app_log.log",level=logging.DEBUG)

def ser_x10_status(x10_response):
    """Takes an x10 response and returns serialized json"""
    dev_dict = {}
    items = x10_response.split("\n")
    for item in items:
        m = re.search(' House (\w): (.*)', item)
        if m:
            if len(m.group(2)) > 1:
                devices = m.group(2).split(",")
                for d in devices:
                    (l,r) = d.split("=")
                    temp_dev_id = m.group(1) + l
                    status = 'off'
                    if r == 1:
		        status = 'on'
		    dev_dict[temp_dev_id] = status
    return dev_dict

@app.route("/")
def reroute():
    """Duplicate of default"""
    return "Simple Service: %s" % version

@app.route("/service")
def hello():
    """Default route. Change this to a service definition"""
    return "Hello Service: %s" % version
    
@app.route("/service/one", methods=['GET'])
def one():
    return "Hello One"
    
@app.route("/service/gpio", methods=['GET'])
def get_gpio():
    """gets the current status of all the active gpios"""
    gpio = 6
    status = 1
    return make_response(jsonify({'gpio': gpio, 'value': status}), 200)
    
@app.route("/service/x10/<device>/<switch>", methods=['GET'])
def set_x10(device, switch):
    """sets an x10 device"""
    command = "/usr/local/bin/x10cmd rf %s %s" % (device, switch)
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    outs, errs = p.communicate()
    if errs:
        message = errs
    else:
        message = outs
    message = "some message"
    stdout = "some made up message"    
    return make_response(jsonify({'command': command, 'status': p.stdout, 'message': message}), 200)

@app.route("/service/x10", methods=['GET'])
def get_x10():
    """gets the current status of all the registered x10 devices"""
    command = "/usr/local/bin/x10cmd st"
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    outs, errs = p.communicate()
    if p.stderr:
        status = "fail"
        error = "There was a problem getting status of x10 devices (%s)" % errs
        devices = {}
    else:
        status = "success"
        error = ''
        devices = ser_x10_status(outs)
        logging.info("Device status: %s" % devices)
    return make_response(jsonify(status=status, message=error, devices=devices), 200)

    
#tempC = int(open('/sys/class/thermal/thermal_zone0/temp').read()) / 1e3
    
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)
    
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
    logging.info('Application simple_service starting...')
