def handleMissingMetric(f):
  def new_f(*args, **kwargs):
    try:
      return f(*args, **kwargs)
    except (KeyError, IndexError):
      return -1
  return new_f

def handleAndLogException(f):
  def new_f(*args, **kwargs):
    try:
      return f(*args, **kwargs)
    except Exception as e:
      print e.message

      import traceback
      traceback.print_exc()

  return new_f

  
