# free-translate-api

Provide free translation model, the effect is nearly comparable to Google, unlimited characters, can build translation api locally, support Chinese, English, French, Russian, Spanish language translation each other.

```bash
# install
pip install -r requirements.txt
# run app
python3 app.py
#gunicorn Comment main function
gunicorn -w 2 --threads 2 -b 0.0.0.0:6006 -t 1800 app:app

```

Default direct run python3 app.py for English to Chinese translation, modify the supertranslate initialization parameter in app.py (model storage folder) to customize the language

The default port is 6006, please refer to test.py for access examples

Support parallel translation, long paragraphs with multiple sentences are recommended to split by themselves, multiple sentences and more than 128 tokens may appear to miss the translation

![img.png](img.png)
Models from modelscope，https://github.com/modelscope/modelscope

Special thanks to Wei Xiangpeng for his help，https://github.com/pemywei/csanmt

This project is suitable for people who have some computing power and have translation needs. The project is based on the modelscope provided by the model to build the translation api.