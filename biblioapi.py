import urllib, urllib2
import json
import lxml.html

from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/biblio/mtl/<int:isbn>')
def mtl_isbn_api(isbn):
    return jsonify(status='ok', data=get_status_by_isbn(isbn))

BASE_URL = 'http://nelligan.ville.montreal.qc.ca/search~S58*frc/?'
BASE_URL_OPTS = {
    'searchtype': 'i',
    'searchscope': 58,
    'SORT': 'DZ',
    'extended': 0,
    'SUBMIT': 'Chercher',
    'searchlimits': ''
}
def get_status_by_isbn(isbn):
    urlopts = dict(BASE_URL_OPTS)
    urlopts['searcharg'] = isbn
    url = BASE_URL + urllib.urlencode(urlopts)
    urlresp = urllib2.urlopen(url)
    tree = lxml.html.parse(urlresp)
    root = tree.getroot()
    result = []
    for itemrow in root.cssselect('tr.bibItemsEntry'):
        cols = [c.text_content().strip() for c in itemrow.cssselect('td')]
        assert len(cols) == 4
        r = {
            'bibliotheque': cols[0],
            'note': cols[1],
            'cote': cols[2],
            'statut': cols[3]
        }
        r['disponible'] = 'DISPO' in r['statut']
        result.append(r)
    return result
    
if __name__ == '__main__':
    app.run()
    
    