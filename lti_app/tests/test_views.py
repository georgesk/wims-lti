import os

import oauth2
import oauthlib.oauth1.rfc5849.signature as oauth_signature
from django.conf import settings
from django.http import Http404
from django.shortcuts import reverse
from django.test import Client, RequestFactory, TestCase
from wimsapi import Class, Sheet, User

from api.models import LMS, WIMS, WimsClass
from lti_app import views
# URL to the WIMS server used for tests, the server must recogned ident 'myself' and passwd 'toto'
from lti_app.enums import Role


WIMS_URL = os.getenv("WIMS_URL") or "http://localhost:7777/wims/wims.cgi"

KEY = 'provider1'
SECRET = 'secret1'



class WimsClassTestCase(TestCase):
    
    def test_wims_class_ok(self):
        params = {
            'lti_message_type':                   'basic-lti-launch-request',
            'lti_version':                        'LTI-1p0',
            'launch_presentation_locale':         'fr-FR',
            'resource_link_id':                   'X',
            'context_id':                         '77777',
            'context_title':                      "A title",
            'user_id':                            '77',
            'lis_person_contact_email_primary':   'test@email.com',
            'lis_person_name_family':             'Doe',
            'lis_person_name_given':              'Jhon',
            'tool_consumer_instance_description': 'UPEM',
            'tool_consumer_instance_guid':        "elearning.upem.fr",
            'oauth_consumer_key':                 KEY,
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              settings.ROLES_ALLOWED_CREATE_WIMS_CLASS[0].value,
        }
        
        norm_params = oauth_signature.normalize_parameters([(k, v) for k, v in params.items()])
        
        uri = oauth_signature.normalize_base_string_uri(
            "https://testserver" + reverse("lti:wims_class", args=[1]))
        base_string = oauth_signature.construct_base_string("POST", uri, norm_params)
        
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, SECRET, None)
        request = RequestFactory().post(reverse("lti:wims_class", args=[1]), secure=True)
        request.POST = params
        
        WIMS.objects.create(url=WIMS_URL, name="WIMS UPEM", ident="myself", passwd="toto",
                            rclass="myclass")
        LMS.objects.create(uuid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                           name="Moodle UPEM", key=KEY, secret=SECRET)
        r = views.wims_class(request, 1)
        self.assertIn(WIMS_URL, r.url)
    
    
    def test_wims_class_invalid_method(self):
        r = Client().patch(reverse("lti:wims_class", args=[1]))
        self.assertContains(r, "405 Method Not Allowed: 'PATCH'", status_code=405)
    
    
    def test_wims_class_invalid_method_get(self):
        r = Client().get(reverse("lti:wims_class", args=[1]))
        self.assertContains(r, "405 Method Not Allowed: 'GET'. Did you forget trailing '/' ?",
                            status_code=405)
    
    
    def test_wims_class_invalid_lti(self):
        params = {
            'lti_message_type':                   'wrong',
            'lti_version':                        'LTI-1p0',
            'launch_presentation_locale':         'fr-FR',
            'resource_link_id':                   'X',
            'context_id':                         'X',
            'context_title':                      "A title",
            'user_id':                            'X',
            'lis_person_contact_email_primary':   'X',
            'lis_person_name_family':             'X',
            'lis_person_name_given':              'X',
            'tool_consumer_instance_description': 'X',
            'tool_consumer_instance_guid':        'elearning.u-pem.fr',
            'oauth_consumer_key':                 KEY,
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              "Learner"
        }
        request = RequestFactory().post(reverse("lti:wims_class", args=[1]), secure=True)
        request.POST = params
        
        WIMS.objects.create(url=WIMS_URL, name="WIMS UPEM", ident="myself", passwd="toto",
                            rclass="myclass")
        LMS.objects.create(uuid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                           name="Moodle UPEM", key=KEY, secret=SECRET)
        r = views.wims_class(request, 1)
        self.assertContains(r, "LTI request is invalid, missing parameter(s): ['oauth_signature']",
                            status_code=400)
    
    
    def test_wims_class_unknown_wims(self):
        params = {
            'lti_message_type':                   'basic-lti-launch-request',
            'lti_version':                        'LTI-1p0',
            'launch_presentation_locale':         'fr-FR',
            'resource_link_id':                   'X',
            'context_id':                         '77777',
            'context_title':                      "A title",
            'user_id':                            '77',
            'lis_person_contact_email_primary':   'test@email.com',
            'lis_person_name_family':             'Doe',
            'lis_person_name_given':              'Jhon',
            'tool_consumer_instance_description': 'UPEM',
            'tool_consumer_instance_guid':        "elearning.upem.fr",
            'oauth_consumer_key':                 KEY,
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              settings.ROLES_ALLOWED_CREATE_WIMS_CLASS[0].value,
        }
        
        norm_params = oauth_signature.normalize_parameters([(k, v) for k, v in params.items()])
        
        uri = oauth_signature.normalize_base_string_uri(
            "https://testserver" + reverse("lti:wims_class", args=[1]))
        base_string = oauth_signature.construct_base_string("POST", uri, norm_params)
        
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, SECRET, None)
        request = RequestFactory().post(reverse("lti:wims_class", args=[1]), secure=True)
        request.POST = params
        LMS.objects.create(uuid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                           name="Moodle UPEM", key=KEY, secret=SECRET)
        with self.assertRaisesMessage(Http404, "Unknown WIMS server of id '999999'"):
            views.wims_class(request, 999999)
    
    
    def test_wims_class_unknown_lms(self):
        params = {
            'lti_message_type':                   'basic-lti-launch-request',
            'lti_version':                        'LTI-1p0',
            'launch_presentation_locale':         'fr-FR',
            'resource_link_id':                   'X',
            'context_id':                         '77777',
            'context_title':                      "A title",
            'user_id':                            '77',
            'lis_person_contact_email_primary':   'test@email.com',
            'lis_person_name_family':             'Doe',
            'lis_person_name_given':              'Jhon',
            'tool_consumer_instance_description': 'UPEM',
            'tool_consumer_instance_guid':        "unknown.fr",
            'oauth_consumer_key':                 KEY,
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              settings.ROLES_ALLOWED_CREATE_WIMS_CLASS[
                                                      0].value,
        }
        
        norm_params = oauth_signature.normalize_parameters([(k, v) for k, v in params.items()])
        
        uri = oauth_signature.normalize_base_string_uri(
            "https://testserver" + reverse("lti:wims_class", args=[1]))
        base_string = oauth_signature.construct_base_string("POST", uri, norm_params)
        
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, SECRET, None)
        request = RequestFactory().post(reverse("lti:wims_class", args=[1]), secure=True)
        request.POST = params
        
        wims = WIMS.objects.create(url=WIMS_URL, name="WIMS UPEM", ident="X", passwd="X",
                                   rclass="myclass")
        LMS.objects.create(uuid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                           name="Moodle UPEM", key=KEY, secret=SECRET)
        
        with self.assertRaisesMessage(Http404, "No LMS found with uuid '%s'"
                                               % params["tool_consumer_instance_guid"]):
            views.wims_class(request, wims.pk)
    
    
    def test_wims_class_wrong_ident_passwd(self):
        params = {
            'lti_message_type':                   'basic-lti-launch-request',
            'lti_version':                        'LTI-1p0',
            'launch_presentation_locale':         'fr-FR',
            'resource_link_id':                   'X',
            'context_id':                         '77777',
            'context_title':                      "A title",
            'user_id':                            '77',
            'lis_person_contact_email_primary':   'test@email.com',
            'lis_person_name_family':             'Doe',
            'lis_person_name_given':              'Jhon',
            'tool_consumer_instance_description': 'UPEM',
            'tool_consumer_instance_guid':        "elearning.upem.fr",
            'oauth_consumer_key':                 KEY,
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              settings.ROLES_ALLOWED_CREATE_WIMS_CLASS[
                                                      0].value,
        }
        
        norm_params = oauth_signature.normalize_parameters([(k, v) for k, v in params.items()])
        uri = oauth_signature.normalize_base_string_uri(
            "https://testserver" + reverse("lti:wims_class", args=[1]))
        base_string = oauth_signature.construct_base_string("POST", uri, norm_params)
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, SECRET, None)
        
        request = RequestFactory().post(reverse("lti:wims_class", args=[1]), secure=True)
        request.POST = params
        
        wims = WIMS.objects.create(url=WIMS_URL, name="WIMS UPEM",
                                   ident="wrong", passwd="wrong", rclass="myclass")
        LMS.objects.create(uuid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                           name="Moodle UPEM", key=KEY, secret=SECRET)
        
        r = views.wims_class(request, wims.pk)
        self.assertContains(r, "Identification Failure : bad login/pwd", status_code=502)
    
    
    def test_wims_class_could_not_join_server(self):
        params = {
            'lti_message_type':                   'basic-lti-launch-request',
            'lti_version':                        'LTI-1p0',
            'launch_presentation_locale':         'fr-FR',
            'resource_link_id':                   'X',
            'context_id':                         '77777',
            'context_title':                      "A title",
            'user_id':                            '77',
            'lis_person_contact_email_primary':   'test@email.com',
            'lis_person_name_family':             'Doe',
            'lis_person_name_given':              'Jhon',
            'tool_consumer_instance_description': 'UPEM',
            'tool_consumer_instance_guid':        "elearning.upem.fr",
            'oauth_consumer_key':                 KEY,
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              settings.ROLES_ALLOWED_CREATE_WIMS_CLASS[
                                                      0].value,
        }
        
        norm_params = oauth_signature.normalize_parameters([(k, v) for k, v in params.items()])
        uri = oauth_signature.normalize_base_string_uri(
            "https://testserver" + reverse("lti:wims_class", args=[1]))
        base_string = oauth_signature.construct_base_string("POST", uri, norm_params)
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, SECRET, None)
        
        request = RequestFactory().post(reverse("lti:wims_class", args=[1]), secure=True)
        request.POST = params
        
        wims = WIMS.objects.create(url="https://can.not.join.fr/", name="WIMS UPEM",
                                   ident="wrong", passwd="wrong", rclass="myclass")
        LMS.objects.create(uuid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                           name="Moodle UPEM", key=KEY, secret=SECRET)
        
        r = views.wims_class(request, wims.pk)
        self.assertContains(r, "https://can.not.join.fr/", status_code=504)



class WimsActivityTestCase(TestCase):
    
    def test_wims_activity_ok(self):
        params = {
            'lti_message_type':                   'basic-lti-launch-request',
            'lti_version':                        'LTI-1p0',
            'launch_presentation_locale':         'fr-FR',
            'resource_link_id':                   'X',
            'context_id':                         '77777',
            'context_title':                      "A title",
            'user_id':                            '77',
            'lis_person_contact_email_primary':   'test@email.com',
            'lis_person_name_family':             'Doe',
            'lis_person_name_given':              'Jhon',
            'lis_result_sourcedid':               "14821455",
            'lis_outcome_service_url':            "www.outcom.com",
            'tool_consumer_instance_description': 'UPEM',
            'tool_consumer_instance_guid':        "elearning.upem.fr",
            'oauth_consumer_key':                 KEY,
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              settings.ROLES_ALLOWED_CREATE_WIMS_CLASS[0].value,
        }
        
        norm_params = oauth_signature.normalize_parameters([(k, v) for k, v in params.items()])
        
        uri = oauth_signature.normalize_base_string_uri(
            "https://testserver" + reverse("lti:wims_activity", args=[1, 1]))
        base_string = oauth_signature.construct_base_string("POST", uri, norm_params)
        
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, SECRET, None)
        request = RequestFactory().post(reverse("lti:wims_activity", args=[1, 1]), secure=True)
        request.POST = params
        
        wims = WIMS.objects.create(url=WIMS_URL, name="WIMS UPEM", ident="myself", passwd="toto",
                                   rclass="myclass")
        lms = LMS.objects.create(uuid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                                 name="Moodle UPEM", key="provider1", secret="secret1")
        supervisor = User("supervisor", "Supervisor", "", "password", "test@email.com")
        wclass = Class(wims.rclass, "A title", "UPEM", "test@email.com", "password", supervisor,
                       lang="fr")
        wclass.save(WIMS_URL, "myself", "toto")
        WimsClass.objects.create(lms=lms, lms_uuid="77777", wims=wims, qclass=wclass.qclass,
                                 name="test1")
        wclass.additem(Sheet("Titre", "Description", sheetmode=1))
        
        r = views.wims_activity(request, 1, 1)
        
        self.assertIn(WIMS_URL, r.url)
        self.assertIn("sh=1", r.url)
    
    
    def test_wims_class_invalid_method(self):
        r = Client().patch(reverse("lti:wims_activity", args=[1, 1]))
        self.assertContains(r, "405 Method Not Allowed: 'PATCH'", status_code=405)
    
    
    def test_wims_class_invalid_method_get(self):
        r = Client().get(reverse("lti:wims_activity", args=[1, 1]))
        self.assertContains(r, "405 Method Not Allowed: 'GET'. Did you forget trailing '/' ?",
                            status_code=405)
    
    
    def test_wims_class_invalid_lti(self):
        params = {
            'lti_message_type':                   'wrong',
            'lti_version':                        'LTI-1p0',
            'launch_presentation_locale':         'fr-FR',
            'resource_link_id':                   'X',
            'context_id':                         'X',
            'context_title':                      "A title",
            'user_id':                            'X',
            'lis_person_contact_email_primary':   'X',
            'lis_person_name_family':             'X',
            'lis_person_name_given':              'X',
            'tool_consumer_instance_description': 'X',
            'tool_consumer_instance_guid':        'elearning.u-pem.fr',
            'oauth_consumer_key':                 KEY,
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              "Learner"
        }
        request = RequestFactory().post(reverse("lti:wims_activity", args=[1, 1]), secure=True)
        request.POST = params
        
        WIMS.objects.create(url=WIMS_URL, name="WIMS UPEM", ident="myself", passwd="toto",
                            rclass="myclass")
        LMS.objects.create(uuid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                           name="Moodle UPEM", key=KEY, secret=SECRET)
        r = views.wims_activity(request, 1, 1)
        self.assertContains(r, "LTI request is invalid, missing parameter(s): ['oauth_signature']",
                            status_code=400)
    
    
    def test_wims_class_unknown_wims(self):
        params = {
            'lti_message_type':                   'basic-lti-launch-request',
            'lti_version':                        'LTI-1p0',
            'launch_presentation_locale':         'fr-FR',
            'resource_link_id':                   'X',
            'context_id':                         '77777',
            'context_title':                      "A title",
            'user_id':                            '77',
            'lis_person_contact_email_primary':   'test@email.com',
            'lis_person_name_family':             'Doe',
            'lis_person_name_given':              'Jhon',
            'tool_consumer_instance_description': 'UPEM',
            'tool_consumer_instance_guid':        "elearning.upem.fr",
            'oauth_consumer_key':                 KEY,
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              settings.ROLES_ALLOWED_CREATE_WIMS_CLASS[0].value,
        }
        
        norm_params = oauth_signature.normalize_parameters([(k, v) for k, v in params.items()])
        
        uri = oauth_signature.normalize_base_string_uri(
            "https://testserver" + reverse("lti:wims_activity", args=[1, 1]))
        base_string = oauth_signature.construct_base_string("POST", uri, norm_params)
        
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, SECRET, None)
        request = RequestFactory().post(reverse("lti:wims_activity", args=[1, 1]), secure=True)
        request.POST = params
        LMS.objects.create(uuid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                           name="Moodle UPEM", key=KEY, secret=SECRET)
        with self.assertRaisesMessage(Http404, "Unknown WIMS server of id '999999'"):
            views.wims_activity(request, 999999, 1)
    
    
    def test_wims_class_unknown_lms(self):
        params = {
            'lti_message_type':                   'basic-lti-launch-request',
            'lti_version':                        'LTI-1p0',
            'launch_presentation_locale':         'fr-FR',
            'resource_link_id':                   'X',
            'context_id':                         '77777',
            'context_title':                      "A title",
            'user_id':                            '77',
            'lis_person_contact_email_primary':   'test@email.com',
            'lis_person_name_family':             'Doe',
            'lis_person_name_given':              'Jhon',
            'tool_consumer_instance_description': 'UPEM',
            'tool_consumer_instance_guid':        "unknown.fr",
            'oauth_consumer_key':                 KEY,
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              settings.ROLES_ALLOWED_CREATE_WIMS_CLASS[
                                                      0].value,
        }
        
        norm_params = oauth_signature.normalize_parameters([(k, v) for k, v in params.items()])
        
        uri = oauth_signature.normalize_base_string_uri(
            "https://testserver" + reverse("lti:wims_activity", args=[1, 1]))
        base_string = oauth_signature.construct_base_string("POST", uri, norm_params)
        
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, SECRET, None)
        request = RequestFactory().post(reverse("lti:wims_activity", args=[1, 1]), secure=True)
        request.POST = params
        
        wims = WIMS.objects.create(url=WIMS_URL, name="WIMS UPEM", ident="X", passwd="X",
                                   rclass="myclass")
        LMS.objects.create(uuid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                           name="Moodle UPEM", key=KEY, secret=SECRET)
        
        with self.assertRaisesMessage(Http404, "No LMS found with uuid '%s'"
                                               % params["tool_consumer_instance_guid"]):
            views.wims_activity(request, wims.pk, 1)
    
    
    def test_wims_class_wrong_ident_passwd(self):
        params = {
            'lti_message_type':                   'basic-lti-launch-request',
            'lti_version':                        'LTI-1p0',
            'launch_presentation_locale':         'fr-FR',
            'resource_link_id':                   'X',
            'context_id':                         '77777',
            'context_title':                      "A title",
            'user_id':                            '77',
            'lis_person_contact_email_primary':   'test@email.com',
            'lis_person_name_family':             'Doe',
            'lis_person_name_given':              'Jhon',
            'tool_consumer_instance_description': 'UPEM',
            'tool_consumer_instance_guid':        "elearning.upem.fr",
            'oauth_consumer_key':                 KEY,
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              settings.ROLES_ALLOWED_CREATE_WIMS_CLASS[
                                                      0].value,
        }
        
        norm_params = oauth_signature.normalize_parameters([(k, v) for k, v in params.items()])
        uri = oauth_signature.normalize_base_string_uri(
            "https://testserver" + reverse("lti:wims_activity", args=[1, 1]))
        base_string = oauth_signature.construct_base_string("POST", uri, norm_params)
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, SECRET, None)
        
        request = RequestFactory().post(reverse("lti:wims_activity", args=[1, 1]), secure=True)
        request.POST = params
        
        wims = WIMS.objects.create(url=WIMS_URL, name="WIMS UPEM",
                                   ident="wrong", passwd="wrong", rclass="myclass")
        LMS.objects.create(uuid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                           name="Moodle UPEM", key=KEY, secret=SECRET)
        
        r = views.wims_activity(request, wims.pk, 1)
        self.assertContains(r, "Identification Failure : bad login/pwd", status_code=502)
    
    
    def test_wims_class_could_not_join_server(self):
        params = {
            'lti_message_type':                   'basic-lti-launch-request',
            'lti_version':                        'LTI-1p0',
            'launch_presentation_locale':         'fr-FR',
            'resource_link_id':                   'X',
            'context_id':                         '77777',
            'context_title':                      "A title",
            'user_id':                            '77',
            'lis_person_contact_email_primary':   'test@email.com',
            'lis_person_name_family':             'Doe',
            'lis_person_name_given':              'Jhon',
            'tool_consumer_instance_description': 'UPEM',
            'tool_consumer_instance_guid':        "elearning.upem.fr",
            'oauth_consumer_key':                 KEY,
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              settings.ROLES_ALLOWED_CREATE_WIMS_CLASS[
                                                      0].value,
        }
        
        norm_params = oauth_signature.normalize_parameters([(k, v) for k, v in params.items()])
        uri = oauth_signature.normalize_base_string_uri(
            "https://testserver" + reverse("lti:wims_activity", args=[1, 1]))
        base_string = oauth_signature.construct_base_string("POST", uri, norm_params)
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, SECRET, None)
        
        request = RequestFactory().post(reverse("lti:wims_activity", args=[1, 1]), secure=True)
        request.POST = params
        
        wims = WIMS.objects.create(url="https://can.not.join.fr/", name="WIMS UPEM",
                                   ident="wrong", passwd="wrong", rclass="myclass")
        LMS.objects.create(uuid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                           name="Moodle UPEM", key=KEY, secret=SECRET)
        
        r = views.wims_activity(request, wims.pk, 1)
        self.assertContains(r, "https://can.not.join.fr/", status_code=504)
    
    
    def test_wims_activity_unknown_wimsclass(self):
        params = {
            'lti_message_type':                   'basic-lti-launch-request',
            'lti_version':                        'LTI-1p0',
            'launch_presentation_locale':         'fr-FR',
            'resource_link_id':                   'X',
            'context_id':                         '77778',
            'context_title':                      "A title",
            'user_id':                            '77',
            'lis_person_contact_email_primary':   'test@email.com',
            'lis_person_name_family':             'Doe',
            'lis_person_name_given':              'Jhon',
            'lis_result_sourcedid':               "14821455",
            'lis_outcome_service_url':            "www.outcom.com",
            'tool_consumer_instance_description': 'UPEM',
            'tool_consumer_instance_guid':        "elearning.upem.fr",
            'oauth_consumer_key':                 KEY,
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              settings.ROLES_ALLOWED_CREATE_WIMS_CLASS[0].value,
        }
        
        norm_params = oauth_signature.normalize_parameters([(k, v) for k, v in params.items()])
        
        uri = oauth_signature.normalize_base_string_uri(
            "https://testserver" + reverse("lti:wims_activity", args=[1, 1]))
        base_string = oauth_signature.construct_base_string("POST", uri, norm_params)
        
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, SECRET, None)
        request = RequestFactory().post(reverse("lti:wims_activity", args=[1, 1]), secure=True)
        request.POST = params
        
        WIMS.objects.create(url=WIMS_URL, name="WIMS UPEM", ident="myself", passwd="toto",
                            rclass="myclass")
        LMS.objects.create(uuid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                           name="Moodle UPEM", key="provider1", secret="secret1")
        
        r = views.wims_activity(request, 1, 1)
        self.assertContains(r, "Could not find class of id '77778'", status_code=404)
    
    
    def test_wims_activity_ok_student(self):
        params = {
            'lti_message_type':                   'basic-lti-launch-request',
            'lti_version':                        'LTI-1p0',
            'launch_presentation_locale':         'fr-FR',
            'resource_link_id':                   'X',
            'context_id':                         '77777',
            'context_title':                      "A title",
            'user_id':                            '77',
            'lis_person_contact_email_primary':   'test@email.com',
            'lis_person_name_family':             'Doe',
            'lis_person_name_given':              'Jhon',
            'lis_result_sourcedid':               "14821455",
            'lis_outcome_service_url':            "www.outcom.com",
            'tool_consumer_instance_description': 'UPEM',
            'tool_consumer_instance_guid':        "elearning.upem.fr",
            'oauth_consumer_key':                 KEY,
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              Role.LEARNER.value,
        }
        
        norm_params = oauth_signature.normalize_parameters([(k, v) for k, v in params.items()])
        
        uri = oauth_signature.normalize_base_string_uri(
            "https://testserver" + reverse("lti:wims_activity", args=[1, 1]))
        base_string = oauth_signature.construct_base_string("POST", uri, norm_params)
        
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, SECRET, None)
        request = RequestFactory().post(reverse("lti:wims_activity", args=[1, 1]), secure=True)
        request.POST = params
        
        wims = WIMS.objects.create(url=WIMS_URL, name="WIMS UPEM", ident="myself", passwd="toto",
                                   rclass="myclass")
        lms = LMS.objects.create(uuid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                                 name="Moodle UPEM", key="provider1", secret="secret1")
        supervisor = User("supervisor", "Supervisor", "", "password", "test@email.com")
        wclass = Class(wims.rclass, "A title", "UPEM", "test@email.com", "password", supervisor,
                       lang="fr")
        wclass.save(WIMS_URL, "myself", "toto")
        WimsClass.objects.create(lms=lms, lms_uuid="77777", wims=wims, qclass=wclass.qclass,
                                 name="test1")
        wclass.additem(Sheet("Titre", "Description", sheetmode=1))
        
        r = views.wims_activity(request, 1, 1)
        
        self.assertIn(WIMS_URL, r.url)
        self.assertIn("sh=1", r.url)


    def test_wims_activity_ok_overwrite_sourcedid(self):
        params = {
            'lti_message_type':                   'basic-lti-launch-request',
            'lti_version':                        'LTI-1p0',
            'launch_presentation_locale':         'fr-FR',
            'resource_link_id':                   '7777',
            'context_id':                         '77777',
            'context_title':                      "A title",
            'user_id':                            '77',
            'lis_person_contact_email_primary':   'test@email.com',
            'lis_person_name_family':             'Doe',
            'lis_person_name_given':              'Jhon',
            'lis_result_sourcedid':               "14821455",
            'lis_outcome_service_url':            "www.outcom.com",
            'tool_consumer_instance_description': 'UPEM',
            'tool_consumer_instance_guid':        "elearning.upem.fr",
            'oauth_consumer_key':                 KEY,
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              Role.LEARNER.value,
        }

        norm_params = oauth_signature.normalize_parameters([(k, v) for k, v in params.items()])

        uri = oauth_signature.normalize_base_string_uri(
            "https://testserver" + reverse("lti:wims_activity", args=[1, 1]))
        base_string = oauth_signature.construct_base_string("POST", uri, norm_params)

        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, SECRET, None)
        request = RequestFactory().post(reverse("lti:wims_activity", args=[1, 1]), secure=True)
        request.POST = params

        wims = WIMS.objects.create(url=WIMS_URL, name="WIMS UPEM", ident="myself",
                                   passwd="toto",
                                   rclass="myclass")
        lms = LMS.objects.create(uuid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                                 name="Moodle UPEM", key="provider1", secret="secret1")
        supervisor = User("supervisor", "Supervisor", "", "password", "test@email.com")
        wclass = Class(wims.rclass, "A title", "UPEM", "test@email.com", "password", supervisor,
                       lang="fr")
        wclass.save(WIMS_URL, "myself", "toto")
        WimsClass.objects.create(lms=lms, lms_uuid="77777", wims=wims, qclass=wclass.qclass,
                                 name="test1")
        wclass.additem(Sheet("Titre", "Description", sheetmode=1))

        views.wims_activity(request, 1, 1)
        r = views.wims_activity(request, 1, 1)

        self.assertIn(WIMS_URL, r.url)
        self.assertIn("sh=1", r.url)
