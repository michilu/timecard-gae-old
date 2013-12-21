from random import random
import zipfile
import utils

from google.appengine.api import namespace_manager
from google.appengine.ext import ndb
from google.appengine.runtime import apiproxy_errors
import webapp2

class Model(ndb.Model):
  pass

class FetchPage(utils.RequestHandler):
  def get(self):
    self.fetch_page_async(Model.query())

class Translation(utils.RequestHandler):
  i18n = True
  i18n_domain = "sample"
  i18n_redirect = True

  def get(self):
    i18n_ = _("Python")
    i18n_gettext = gettext("Anaconda")
    self.render_response("sample.html", locals())

class ForMobile(utils.RequestHandler):
  @utils.cache(60)
  def get(self):
    ndb.get_context().memcache_get("sample")
    self.render_response("sample.html", locals(), featurephone=True)

class OverQuotaError(utils.RequestHandler):
  def get(self):
    raise apiproxy_errors.OverQuotaError

class InternalServerError(utils.RequestHandler):
  def get(self):
    assert False

class Head(utils.RequestHandler):
  @utils.head()
  def get(self):
    self.response._app_iter = []

class CORS(utils.RequestHandler):
  @utils.cors()
  def options(self):
    pass

  @utils.cors(origin=lambda:"test")
  def get(self):
    pass

rate_limit = utils.rate_limit(rate=1, size=2, key=lambda self: self.request.remote_addr, tag="RateLimit")
class RateLimit(utils.RequestHandler):
  @rate_limit
  def get(self):
    pass

  @rate_limit
  def post(self):
    pass

  @utils.rate_limit(rate=1, size=1)
  def put(self):
    pass

class CacheTemporary(utils.RequestHandler):
  @utils.cache(temporary=True)
  def get(self):
    self.response.write(random())

class Proxy(utils.RequestHandler):
  def get(self):
    self.proxy()

class Namespace(utils.RequestHandler):
  def get(self):
    self.response.write(namespace_manager.get_namespace())

class ZipFile(utils.RequestHandler):
  use_zipfile = True

  def get(self):
    assert self.response.tell() == 0
    writer = zipfile.ZipFile(self.response, "w")
    writer.writestr("zinfo_or_arcname", b"test")
    writer.close()
    assert self.response.tell() == 134

routes = [
  webapp2.Route("/fetch_page", FetchPage),
  webapp2.Route("/translation", Translation),
  webapp2.Route("/index.html", ForMobile),
  webapp2.Route("/test.html", OverQuotaError),
  webapp2.Route("/error.html", InternalServerError),
  webapp2.Route("/head", Head),
  webapp2.Route("/cors", CORS),
  webapp2.Route("/rate_limit", RateLimit),
  webapp2.Route("/cache_temporary", CacheTemporary),
  webapp2.Route("/proxy", Proxy),
  webapp2.Route("/namespace", Namespace),
  webapp2.Route("/zipfile", ZipFile),
]
