import config
import prediction
from nlp_service import NLPService
from flask import Flask
from db import log_request, save_new_ehrtext_training_data
from snomed import Snomed
from text_utils import remove_tildes
from threading import Thread
from flask_restplus import Resource, Api, reqparse, inputs, fields, marshal


app = Flask(__name__)

app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
app.config['RESTPLUS_MASK_SWAGGER'] = False
app.config.SWAGGER_UI_DOC_EXPANSION = 'list'

api = Api(app, title='Codical API')
nlp = NLPService()
ns = api.namespace('Codical')


snomed_term_model = api.model('SnomedTerm', {
    'code': fields.String(example='38341003'),
    'description': fields.String(example='trastorno hipertensivo arterial sistémico'),
    'domain': fields.String(example='trastorno'),
    'synonyms': fields.List(fields.String, example=["hipertensión arterial",
                                                    "enfermedad hipertensiva",
                                                    "enfermedad vascular hipertensiva",
                                                    "degeneración vascular hipertensiva"])
})

search_term_parser = reqparse.RequestParser()
search_term_parser.add_argument('domains', type=str, action='append')
search_term_parser.add_argument('exact', type=inputs.boolean, default=False)
search_term_parser.add_argument('limit', type=int, default=50)


value_model = api.model('Value', {
    'text': fields.String(example='14 mm', attribute='text'),
    'value': fields.Float(example='14', attribute='value'),
    'unit': fields.String(example='mm', attribute='unit')
})

qualifiers_model = api.model('Qualifier', {
                             'text': fields.String(example='severa', attribute='text'),
                             'snomedCTTerm': fields.Nested(snomed_term_model, attribute='snomed_term', example={})})

term_model = api.model('Term', {
    'text': fields.String(example='hipertensión', attribute='text'),
    'snomedCTTerm': fields.Nested(snomed_term_model, attribute='snomed_term'),
    'qualifiers': fields.Nested(qualifiers_model, attribute='qualifiers', default={}),
    'values': fields.Nested(value_model, attribute='values', default={}, example={})
})

phrase_model = api.model('Expression', {
    'expression': fields.String(example='hipertensión severa.', attribute='text'),
    'snomedCTExpression': fields.String(attribute='to_snomed', example="38341003 |trastorno hipertensivo arterial sistémico| : (246112005 |severidad| = 24484000 |severo|)"),
    'terms': fields.Nested(term_model, attribute='terms')
})

coded_text_model = api.model('CodedText', {
    'medicalText': fields.String(example='hipertensión severa.', attribute='text'),
    'expressions': fields.Nested(phrase_model, attribute='phrases')})


@ ns.route('/searchterm/<string:text>')
@ ns.doc(params={'text': 'The text to search.'})
@ ns.response(200, 'Success')
@ api.expect(search_term_parser, validate=True)
class SearchTerm(Resource):
    '''Search a term by its description in the SNOMED-CT standard.'''

    @ api.marshal_with(snomed_term_model, envelope='terms')
    def get(self, text):
        '''Search a term by its description in the SNOMED-CT standard.'''
        args = search_term_parser.parse_args(strict=True)
        text = remove_tildes(text)
        results = Snomed.instance().search_by_description(text, args['exact'], args['limit'], args['domains'])
        return results


@ ns.route('/getterm/<string:code>')
@ ns.doc(params={'code': 'The code of the SNOMED-CT term to search.'})
@ ns.response(200, 'Success')
class GetTerm(Resource):
    '''Fetch a term by its SNOMED-CT code.'''

    @ api.marshal_with(snomed_term_model, envelope='terms')
    def get(self, code):
        '''Fetch a term by its SNOMED-CT code.'''
        results = Snomed.instance().search_by_code(code)
        return results


@ ns.route('/save/', doc=False)
@ ns.response(200, 'Success')
@ ns.response(500, 'Error')
class Save(Resource):
    '''Send a coded clinical text as feedback.'''

    def post(self):
        '''Send a coded clinical text as feedback.'''
        ehrtext = prediction.json_to_ehrtext(api.payload)
        error = save_new_ehrtext_training_data(ehrtext)
        if error is not None:
            return api.abort(500, "Error: '{}'".format(error))
        return '', 200


@ns.route('/codify/<string:text>')
@ns.response(200, 'Success', coded_text_model)
@ns.response(412, 'Validation error')
@ns.doc(params={'text': 'The clinical text to be coded in SNOMED-CT.'})
class Codify(Resource):
    ''' Code a clinical text to SNOMED-CT using Codical IA'''

    def get(self, text):
        ''' Code a clinical text to SNOMED-CT using Codical IA'''
        if not nlp.validate_length(text):
            api.abort(412, 'Text length exceeds the service maximum of {} characters.'.format(config.max_ehrtext_length))
        response_raw = nlp.predict(text)
        response_json = marshal(response_raw, coded_text_model)

        if config.enable_log:
            Thread(target=log_request, args=(text, response_json)).start()

        return response_json


@ns.route('/codifyqualifier/<string:text>', doc=False)
class Codify_Qualifier(Resource):

    @api.marshal_with(qualifiers_model)
    def get(self, text):
        return nlp.predict_qualifier(text)


if __name__ == '__main__':
    app.run()
