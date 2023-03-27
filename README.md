# free-translate-api

Provide free translation model, the effect is nearly comparable to Google, unlimited characters, can build translation api locally, support Chinese, English, French, Russian, Spanish language translation each other.

Not an official implementation of modelscope, avoiding excessive dependencies, only a few dependencies need to be installed and can be easily deployed

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


Models from modelscope，https://github.com/modelscope/modelscope

Special thanks to Wei Xiangpeng for his help，https://github.com/pemywei/csanmt

This project is suitable for people who have some computing power and have translation needs. The project is based on the modelscope provided by the model to build the translation api.

## Data Evaluation and Results
|  Backbone |#Params|  WMT18-20 (NLTK_BLEU)| IWSLT 16-17 (NLTK_BLEU) |    Remark   |
|:---------:|:-----:|:--------------------:|:-----------------------:|:-----------:|
|     -     |   -   |         31.3         |          19.8           |    Google   |
| 24-6-1024 | 570M  |         29.8         |          19.8           |  ModelScope |


## Paper Citation
If you think this model would be helpful, please consider citing the following related paper：
``` bibtex
@inproceedings{wei-etal-2022-learning,
  title = {Learning to Generalize to More: Continuous Semantic Augmentation for Neural Machine Translation},
  author = {Xiangpeng Wei and Heng Yu and Yue Hu and Rongxiang Weng and Weihua Luo and Rong Jin},
  booktitle = {Proceedings of the 60th Annual Meeting of the Association for Computational Linguistics, ACL 2022},
  year = {2022},
}
```