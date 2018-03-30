import requests

class Response():
  def __init__(self, response):
    self.response = response

  @property
  def json(self):
    return self.response.json()

class SummaryResponse(Response):
  @property
  def topology_id(self):
    return self.json["topologies"][0]["id"]

class TopologyResponse(Response):
  @property
  def spouts(self):
    return self.json["spouts"]

  @property
  def bolts(self):
    return self.json["bolts"]

  def get_spout(self, name):
    return [spout for spout in self.spouts if spout["spoutId"] == name][0]

  def get_bolt(self, name):
    return [bolt for bolt in self.bolts if bolt["boltId"] == name][0]

class ApiClient():
  REST_API_BASE = "http://localhost:8080/api/v1"

  def get_summary(self):
    result = requests.get(self.REST_API_BASE + "/topology/summary")
    return SummaryResponse(result)

  def get_topology(self, topology_id):
    result = requests.get(self.REST_API_BASE + "/topology/%s" % topology_id)
    return TopologyResponse(result)
