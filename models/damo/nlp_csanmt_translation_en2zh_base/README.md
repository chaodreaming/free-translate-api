---
tasks:
- translation

widgets:
- task: translation
  inputs:
    - type: text
      name: input
      title: 输入文字
      validator:
        max_words: 128
  examples:
      - name: 1
        title: 示例1
        inputs:
          - name: text
            data: Alibaba Group's mission is to let the world have no difficult business
      - name: 2
        title: 示例2
        inputs:
          - name: text
            data: The weather is really nice today!

model-type:
- csanmt

domain:
- nlp

frameworks:
- tensorflow

backbone:
- transformer

metrics:
- bleu

license: Apache License 2.0

finetune-support: True

language:
- en-zh

tags:
- CSANMT
- Neural Machine Translation
- Continuous Semantic Augmentation
- ACL2022

datasets:
  train:
  - damo/WMT-Chinese-to-English-Machine-Translation-Training-Corpus
  test:
  - damo/WMT-English-to-Chinese-Machine-Translation-newstest
  - damo/IWSLT-English-to-Chinese-Machine-Translation-Spoken
  - damo/WMT-English-to-Chinese-Machine-Translation-Medical
---

# 基于连续语义增强的神经机器翻译模型介绍
本模型基于邻域最小风险优化策略，backbone选用先进的transformer-large模型，编码器和解码器深度分别为24和3，相关论文已发表于ACL 2022，并获得Outstanding Paper Award。

## 模型描述
基于连续语义增强的神经机器翻译模型【[论文链接](https://arxiv.org/abs/2204.06812)】由编码器、解码器以及语义编码器三者构成。其中，语义编码器以大规模多语言预训练模型为基底，结合自适应对比学习，构建跨语言连续语义表征空间。此外，设计混合高斯循环采样策略，融合拒绝采样机制和马尔可夫链，提升采样效率的同时兼顾自然语言句子在离散空间中固有的分布特性。最后，结合邻域风险最小化策略优化翻译模型，能够有效提升数据的利用效率，显著改善模型的泛化能力和鲁棒性。模型结构如下图所示。

<center> <img src="./resources/csanmt-model.png" alt="csanmt_translation_model" width="400"/> <br> <div style="color:orange; border-bottom: 1px solid #d9d9d9; display: inline-block; color: #999; padding: 2px;">CSANMT连续语义增强机器翻译</div> </center>

具体来说，我们将双语句子对两个点作为球心，两点之间的欧氏距离作为半径，构造邻接语义区域（即邻域），邻域内的任意一点均与双语句子对语义等价。为了达到这一点，我们引入切线式对比学习，通过线性插值方法构造困难负样例，其中负样本的游走范围介于随机负样本和切点之间。然后，基于混合高斯循环采样策略，从邻接语义分布中采样增强样本，通过对差值向量进行方向变换和尺度缩放，可以将采样目标退化为选择一系列的尺度向量。

<div> <center> <img src="./resources/ctl.png" alt="tangential_ctl" width="300"/> <br> <div style="color:orange; border-bottom: 1px solid #d9d9d9; display: inline-block; color: #999; padding: 2px;">切线式对比学习</div> </center> </div> <div> <center> <img src="./resources/sampling.png" alt="sampling" width="300"/> <br> <div style="color:orange; border-bottom: 1px solid #d9d9d9; display: inline-block; color: #999; padding: 2px;">混合高斯循环采样</div> </center> </div>


## 期望模型使用方式以及适用范围
本模型适用于具有一定数据规模（百万级以上）的所有翻译语向，同时能够与离散式数据增强方法（如back-translation）结合使用。

### 如何使用
在ModelScope框架上，提供输入源文，即可通过简单的Pipeline调用来使用。

### 代码范例
```python
# English-to-Chinese

from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks

input_sequence = 'Elon Musk, co-founder and chief executive officer of Tesla Motors.'

pipeline_ins = pipeline(task=Tasks.translation, model="damo/nlp_csanmt_translation_en2zh")
outputs = pipeline_ins(input=input_sequence)

print(outputs['translation']) # 'Elon Musk，特斯拉汽车公司联合创始人兼首席执行官。'
```

## 模型局限性以及可能的偏差
1. 模型在通用数据集上训练，部分垂直领域有可能产生一些偏差，请用户自行评测后决定如何使用。
2. 当前版本在tensorflow 2.3和1.14环境测试通过，其他环境下可用性待测试。
3. 当前版本fine-tune在cpu和单机单gpu环境测试通过，单机多gpu等其他环境待测试。

## 训练数据介绍
1. [WMT21](https://arxiv.org/abs/2204.06812)数据集，系WMT官方提供的新闻领域双语数据集。
2. [Opensubtitles2018](https://www.opensubtitles.org)，偏口语化（字幕）的双语数据集。
3. [OPUS](https://www.opensubtitles.org)，众包数据集。

## 模型训练流程

### 数据准备
使用中英双语语料作为训练数据，准备两个文件：train.zh和train.en，其中每一行一一对应，例如：

```
#train.zh
这只是一个例子。
今天天气怎么样？
...
```

```
# train.en
This is just an example.
What's the weather like today?
...
```

### 预处理
训练数据预处理流程如下：

1. Tokenization

英文通过[mosesdecoder](https://github.com/moses-smt/mosesdecoder)进行Tokenization
```
perl tokenizer.perl -l en < train.en > train.en.tok
```

中文通过[jieba](https://github.com/fxsjy/jieba)进行中文分词
```
import jieba

fR = open('train.zh', 'r', encoding='UTF-8')
fW = open('train.zh.tok', 'w', encoding='UTF-8')

for sent in fR: 
    sent = fR.read()
    sent_list = jieba.cut(sent)
    fW.write(' '.join(sent_list))

fR.close()
fW.close()
```

2. [Byte-Pair-Encoding](https://github.com/rsennrich/subword-nmt)

```
subword-nmt apply-bpe -c bpe.en < train.en.tok > train.en.tok.bpe

subword-nmt apply-bpe -c bpe.zh < train.zh.tok > train.zh.tok.bpe
```

### 参数配置

修改Configuration.json相关训练配置，根据用户定制数据进行微调。参数介绍如下：

```
"train": {
        "num_gpus": 0,                                           # 指定GPU数量，0表示CPU运行
        "warmup_steps": 4000,                                    # 冷启动所需要的迭代步数，默认为4000
        "update_cycle": 1,                                       # 累积update_cycle个step的梯度进行一次参数更新，默认为1
        "keep_checkpoint_max": 1,                                # 训练过程中保留的checkpoint数量
        "confidence": 0.9,                                       # label smoothing权重
        "optimizer": "adam",
        "adam_beta1": 0.9,
        "adam_beta2": 0.98,
        "adam_epsilon": 1e-9,
        "gradient_clip_norm": 0.0,
        "learning_rate_decay": "linear_warmup_rsqrt_decay",      # 学习衰减策略，可选模式包括[none, linear_warmup_rsqrt_decay, piecewise_constant]
        "initializer": "uniform_unit_scaling",                   # 参数初始化策略，可选模式包括[uniform, normal, normal_unit_scaling, uniform_unit_scaling]
        "initializer_scale": 0.1,
        "learning_rate": 1.0,                                    # 学习率的缩放系数，即根据step值确定学习率以后，再根据模型的大小对学习率进行缩放
        "train_batch_size_words": 1024,                          # 单训练batch所包含的token数量
        "scale_l1": 0.0,
        "scale_l2": 0.0,
        "train_max_len": 100,                                    # 默认情况下，限制训练数据的长度为100，用户可自行调整
        "max_training_steps": 5,                                 # 最大训练步数
        "save_checkpoints_steps": 1000,                          # 间隔多少steps保存一次模型
        "num_of_samples": 4,                                     # 连续语义采样的样本数量
        "eta": 0.6
    },
"dataset": {
        "train_src": "train.en",                                 # 指定源语言数据文件
        "train_trg": "train.zh",                                 # 指定目标语言数据文件
        "src_vocab": {
            "file": "src_vocab.txt"                              # 指定源语言词典
        },
        "trg_vocab": {
            "file": "trg_vocab.txt"                              # 指定目标语言词典
        }
    }
```

### 模型训练
```python
# English-to-Chinese

from modelscope.trainers.nlp import CsanmtTranslationTrainer

trainer = CsanmtTranslationTrainer(model="damo/nlp_csanmt_translation_en2zh")
trainer.train()

```

## 数据评估及结果
|  Backbone |#Params|  WMT18-20 (NLTK_BLEU)| IWSLT 16-17 (NLTK_BLEU) |    Remark         |
|:---------:|:-----:|:--------------------:|:-----------------------:|:-----------------:|
|     -     |   -   |         31.3         |          19.8           |    Google         |
| 24-6-1024 | 570M  |         29.8         |          19.8           |  ModelScope (big) |
| 24-3-512  | 205M  |         29.1         |          19.3           |  ModelScope (base)|


## 论文引用
如果你觉得这个该模型对有所帮助，请考虑引用下面的相关的论文：
``` bibtex
@inproceedings{wei-etal-2022-learning,
  title = {Learning to Generalize to More: Continuous Semantic Augmentation for Neural Machine Translation},
  author = {Xiangpeng Wei and Heng Yu and Yue Hu and Rongxiang Weng and Weihua Luo and Rong Jin},
  booktitle = {Proceedings of the 60th Annual Meeting of the Association for Computational Linguistics, ACL 2022},
  year = {2022},
}
```
