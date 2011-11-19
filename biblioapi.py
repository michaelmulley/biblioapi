import urllib, urllib2
import json
import re

from flask import Flask, jsonify
import lxml.html
import mechanize

app = Flask(__name__)

@app.route('/biblio/mtl/<isbn>')
def mtl_isbn_api(isbn):
    return jsonify(status='ok', data=mtl_get_status_by_isbn(isbn))
    
@app.route('/biblio/banq/<isbn>')
def banq_isbn_api(isbn):
    return jsonify(status='ok', data=banq_get_status_by_isbn(isbn))

MTL_BASE_URL = 'http://nelligan.ville.montreal.qc.ca/search~S58*frc/?'
MTL_BASE_URL_OPTS = {
    'searchtype': 'i',
    'searchscope': 58,
    'SORT': 'DZ',
    'extended': 0,
    'SUBMIT': 'Chercher',
    'searchlimits': ''
}
def mtl_get_status_by_isbn(isbn):
    urlopts = dict(MTL_BASE_URL_OPTS)
    urlopts['searcharg'] = isbn
    url = MTL_BASE_URL + urllib.urlencode(urlopts)
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
    
BANQ_BASE_URL = 'http://iris.banq.qc.ca/alswww2.dll/APS_ZONES?fn=AdvancedSearch&Style=Portal3&SubStyle=&Lang=FRE&ResponseEncoding=utf-8'
def banq_get_status_by_isbn(isbn):
    br = mechanize.Browser()
    br.open(BANQ_BASE_URL)
    br.select_form(name="ExpertSearch")
    br["q.form.t1.term"] = ["NUMERO="]
    br["q.form.t1.expr"] = str(isbn)
    
    resp2 = br.submit()
    
    resp3 = br.follow_link(url_regex=re.compile(r'^APS_PRESENT_BIB'))
    root = lxml.html.fromstring(resp3.get_data())
    
    result = []
    for item in root.cssselect('.DetailDataCell ol li'):
        itemtext = item.text_content()
        result.append({
            'cote': item.cssselect('a')[0].text_content().strip(),
            'disponible': ('Disponible' in itemtext and 'Disponible le' not in itemtext)
        })
    return result
    
if __name__ == '__main__':
    app.run()
    
    