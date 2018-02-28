import qrcode, os, uuid
import PIL
import textwrap
import cups
import threading
import time
import logging
import os
import subprocess

from flask import Flask, Blueprint, request, jsonify
from flask_restful import Resource, Api
from PIL import Image as pimg
from flask import current_app
from PIL import ImageFont, Image, ImageDraw
from multiprocessing import Queue

api = Blueprint('api', 'app', url_prefix='/api')
apiFramework = Api(api)

printHistory = []
tagHistory = []

logging.basicConfig(
    level=logging.DEBUG,
    format='(%(threadName)-10s) %(message)s',
)

# Helper functions

def getLabel(text, fontsize, width, height):
    font = PIL.ImageFont.truetype(os.path.abspath(os.path.dirname(__file__))+"/OCRA.ttf", fontsize)
    textImg = PIL.Image.new(mode="L", size=(width, width), color=255)
    draw = PIL.ImageDraw.Draw(textImg)

    margin = 0
    offset = 0

    for line in textwrap.wrap(text, width=14):
        w, h = draw.textsize(line, font)
        posW = (width - w) / 2
        draw.text((posW, offset), line, font=font)
        offset += font.getsize(line)[1]

    return textImg

def getQCcode(data, width, height):
    qr = qrcode.QRCode()
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image()
    img = img.resize((width, width), PIL.Image.ANTIALIAS)
    return img

def getPrintFile(url, description):

    fontsize = int(float(current_app.config['PRINT_FONT_SIZE']))
    height = int((float(current_app.config['PRINT_HEIGHT']) / 25.400) * 300)
    width = int((float(current_app.config['PRINT_WIDTH']) / 25.400) * 300)

    printFile = PIL.Image.new(mode="L", size=(width, height), color=255)

    qrImg = getQCcode(url, width, height)
    printFile.paste(qrImg, (0, 0))

    if description != None:
        textImg = getLabel(description, fontsize, width, height)
        printFile.paste(textImg, (0, qrImg.size[1]))
    
    return printFile

# Threading

def nfcDaemon(q, script, id, url, description):
    returned_value = subprocess.call(""+script+" -i '"+ id+"' -u '"+ url+"' -t '"+ description+"'", shell=True)
    q.put(returned_value)
    return returned_value

q = Queue()

# Flask api classes

class Print(Resource):

    def get(self, id):
        for item in printHistory:
            if (item['uuid'] == id):
                return item
        return {"state": "not found"}, 404

    def post(self):
        try:
            data = request.get_json(force=True)

            if not 'url' in data:
                return {"state": "missing params"}, 400
            else:
                url = data["url"]
            if 'uuid' in data:
                id = data['uuid']
            else:
                id = str(uuid.uuid4())
            if 'description' in data:
                description = data['description']
            else: 
                description = None
            
            img = getPrintFile(url+"?uuid="+id, description)
            img.save(os.path.abspath(os.path.dirname(__file__)) + "/qrcodes/" + id + ".png")

            # Try to print 
            conn = cups.Connection()
            printers = conn.getPrinters()
            for printer in printers:
               conn.printFile(printer, os.path.abspath(os.path.dirname(__file__)) + "/qrcodes/" + id + ".png", " ", {})
            
            printHistory.append({'uuid': id,'url': url, 'description': description })

            return  {"state": "success", 'uuid': id}, 200
        except:
            return {"state": "something went wrong"}, 500

class Tag(Resource):

    def post(self):
        try:
            for i in threading.enumerate():
                if i.name == "nfcDaemon":
                    if i.isAlive():
                        return {"state": "waiting"}, 503

            data = request.get_json(force=True)
            if not 'url' in data:
                return 'missing params', 400
            else:
                url = data["url"]
            if 'uuid' in data:
                id = data['uuid']
            else:
                id = str(uuid.uuid4())
            if 'description' in data:
                description = data['description']
            else: 
                description = None

            tagHistory.append({'uuid': id,'url': url })

            # Start tagging
            d = threading.Thread(name='nfcDaemon', target=nfcDaemon, args=(q, current_app.config['TAGGING_SCRIPT'], id, url, description))
            d.setDaemon(True)
            d.start()

            return {"state": "success", 'uuid': id}, 200
        except:
            return {"state": "something went wrong"}, 500

    def get(self, id):

        for item in tagHistory:
            if item['uuid'] == id:
                try:
                    for i in threading.enumerate():
                        if i.name == "nfcDaemon":
                            if i.isAlive():
                                return {"state": "waiting"}, 503
                    
                    if not "state" in item:
                        item['state'] = q.get()
                    
                    if "state" in item:
                        if item['state'] == 0:
                            return {"state": "success"}, 200
                        else:
                            return {"state": "something went wrong"}, 500
        
                except:
                    return {"state": "something went wrong"}, 500          
        return {"state": "not found"}, 404

apiFramework.add_resource(Print, '/label', '/label/<string:id>')
apiFramework.add_resource(Tag, '/nfc', '/nfc/<string:id>')