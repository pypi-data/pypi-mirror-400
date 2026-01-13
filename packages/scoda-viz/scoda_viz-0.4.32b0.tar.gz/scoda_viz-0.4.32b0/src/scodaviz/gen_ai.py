from IPython.display import Markdown, display

try:
    import google.generativeai as genai  
except:
    print('ERROR: google not available.')

class scoda_ai:

  model = None
  api_key = None

  def __init__(self, api_key = None, model_to_use = 'gemini-2.5-flash'):
    self.set_api_key(api_key, model_to_use)

  def set_api_key(self, api_key, model_to_use = 'gemini-2.5-flash'):
      self.api_key = api_key
      genai.configure(api_key=api_key)
      self.model = genai.GenerativeModel(model_to_use)
      return 

  def ask(self, data_str: str, 
          q: str = '요거 생물학적으로 설명 좀 부탁해~',
          prompt: str = '요거 나의 scRNA-seq 분석 결과 데이터야: '):
      question = f"{prompt}\n{data_str}\n\n질문: {q}"
      response = self.model.generate_content(question)
      return Markdown(response.text)
